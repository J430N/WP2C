#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re

from util.color import Color

class Configuration(object):
    """ Stores configuration variables and functions for WP2C. """

    initialized = False  # Flag indicating config has been initialized
    verbose = 0
    version = '2.6.8'
    
    check_handshake = None
    cracked_file = None
    crack_handshake = None
    daemon = None
    existing_commands = None
    ignore_old_handshakes = None
    interface = None
    wifi_properties = None
    manufacturers = None
    no_nullpin = None
    num_deauths = None
    print_stack_traces = None
    show_cracked = None
    temp_dir = None  # Temporary directory
    wordlist = None
    wpa_attack_timeout = None
    wpa_deauth_timeout = None
    wpa_handshake_dir = None
    wpa_strip_handshake = None

    @classmethod
    def initialize(cls, load_interface=True):
        """
            Sets up default initial configuration values.
            Also sets config values based on command-line arguments.
        """

        # Only initialize this class once
        if cls.initialized:
            return
        cls.initialized = True

        cls.verbose = 0  # Verbosity of output. Higher number means more debug info about running processes.
        cls.print_stack_traces = True
        cls.wifi_properties = False
        cls.tx_power = 0  # Wifi transmit power (0 is default)
        cls.interface = None
        cls.num_deauths = 1  # Number of deauth packets to send to each target.

        # WPA variables
        cls.wpa_deauth_timeout = 5  # Wait time between deauths
        cls.wpa_attack_timeout = 300  # Wait time before failing
        cls.wpa_handshake_dir = 'hs'  # Dir to store handshakes
        cls.wpa_strip_handshake = False  # Strip non-handshake packets
        cls.ignore_old_handshakes = False  # Always fetch a new handshake

        # Default dictionary for cracking
        cls.cracked_file = 'cracked.json'
        cls.wordlist = None
        wordlists = [
            './wordlist-probable.txt',  # Local file (ran from cloned repo)
            '/usr/share/dict/wordlist-probable.txt',  # setup.py with prefix=/usr
            '/usr/local/share/dict/wordlist-probable.txt',  # setup.py with prefix=/usr/local
            # Other passwords found on Kali
            '/usr/share/wfuzz/wordlist/fuzzdb/wordlists-user-passwd/passwds/phpbb.txt',
            '/usr/share/fuzzdb/wordlists-user-passwd/passwds/phpbb.txt',
            '/usr/share/wordlists/fern-wifi/common.txt'
        ]
        
        for wlist in wordlists:
            if os.path.exists(wlist):
                cls.wordlist = wlist
                break

        if os.path.isfile('/usr/share/ieee-data/oui.txt'):
            manufacturers = '/usr/share/ieee-data/oui.txt'
        else:
            manufacturers = 'ieee-oui.txt'

        if os.path.exists(manufacturers):
            cls.manufacturers = {}
            with open(manufacturers, "r", encoding='utf-8') as f:
                # Parse txt format into dict
                for line in f:
                    if not re.match(r"^\w", line):
                        continue
                    line = line.replace('(hex)', '').replace('(base 16)', '')
                    fields = line.split()
                    if len(fields) >= 2:
                        cls.manufacturers[fields[0]] = " ".join(fields[1:]).rstrip('.')

        # Commands
        cls.show_cracked = False
        cls.check_handshake = None
        cls.crack_handshake = False

        # A list to cache all checked commands (e.g. `which hashcat` will execute only once)
        cls.existing_commands = {}

        # Overwrite config values with arguments (if defined)
        cls.load_from_arguments()

        if load_interface:
            cls.get_monitor_mode_interface()

    @classmethod
    def get_monitor_mode_interface(cls):
        if cls.interface is None:
            # Interface wasn't defined, select it!
            from tools.airmon import Airmon
            cls.interface = Airmon.ask()

    @classmethod
    def load_from_arguments(cls):
        """ Sets configuration values based on Argument.args object """
        from args import Arguments

        args = Arguments(cls).args
        cls.parse_settings_args(args)


        # Commands
        if args.cracked:
            cls.show_cracked = True
        if args.check_handshake:
            cls.check_handshake = True
        if args.crack_handshake:
            cls.crack_handshake = True
        if args.wifi_properties:
            cls.wifi_properties = True

    @classmethod
    def parse_settings_args(cls, args):
        """Parses basic settings/configurations from arguments."""

        if args.verbose:
            cls.verbose = args.verbose
            Color.pl('{+} {C}option:{W} verbosity level {G}%d{W}' % args.verbose)
            
    @classmethod
    def temp(cls, subfile=''):
        """ Creates and/or returns the temporary directory """
        if cls.temp_dir is None:
            cls.temp_dir = cls.create_temp()
        return cls.temp_dir + subfile

    @staticmethod
    def create_temp():
        """ Creates and returns a temporary directory """
        from tempfile import mkdtemp
        tmp = mkdtemp(prefix='WP2C')
        if not tmp.endswith(os.sep):
            tmp += os.sep
        return tmp

    @classmethod
    def delete_temp(cls):
        """ Remove temp files and folder """
        if cls.temp_dir is None:
            return
        if os.path.exists(cls.temp_dir):
            for f in os.listdir(cls.temp_dir):
                os.remove(cls.temp_dir + f)
            os.rmdir(cls.temp_dir)

    @classmethod
    def exit_gracefully(cls, code=0):
        """ Deletes temp and exist with the given code """
        cls.delete_temp()
        from tools.airmon import Airmon
        if cls.interface is not None and Airmon.base_interface is not None:
            # Stop monitor mode
            Airmon.stop(cls.interface)
            # Bring original interface back up
            Airmon.put_interface_up(Airmon.base_interface)
        
        if Airmon.kill_network_monitor:
            # Kill processes that may interfere with WP2C's operation
            Airmon.start_network_manager() 
            
        exit(code)

    @classmethod
    def dump(cls):
        """ (Colorful) string representation of the configuration """
        from util.color import Color

        max_len = 20
        for key in list(cls.__dict__.keys()):
            max_len = max(max_len, len(key))

        result = Color.s('{W}%s  Value{W}\n' % 'cls Key'.ljust(max_len))
        result += Color.s('{W}%s------------------{W}\n' % ('-' * max_len))

        for (key, val) in sorted(cls.__dict__.items()):
            if key.startswith('__') or type(val) in [classmethod, staticmethod] or val is None:
                continue
            result += Color.s('{G}%s {W} {C}%s{W}\n' % (key.ljust(max_len), val))
        return result
