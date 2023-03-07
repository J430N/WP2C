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
    properties = None
    speed = None
    password = None
    generate  = None
    manufacturers = None
    no_nullpin = None
    print_stack_traces = None
    show_cracked = None
    temp_dir = None  # Temporary directory
    wordlists = []
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
        cls.print_stack_traces = True # Print stack traces when exceptions occur
        cls.tx_power = 0  # Wifi transmit power (0 is default)
        cls.interface = None # Wireless interface to use
        cls.num_deauths = 3  # Number of deauth packets to send to each target.

        # WPA variables
        cls.wpa_deauth_timeout = 5  # Wait time between deauths
        cls.wpa_attack_timeout = 300  # Wait time before failing
        cls.wpa_handshake_dir = 'hs'  # Dir to store handshakes
        cls.wpa_strip_handshake = False  # Strip non-handshake packets
        cls.ignore_old_handshakes = False  # Always fetch a new handshake

        # Default dictionary for cracking
        cls.cracked_file = 'cracked.json'

        # Loop through all files in the directory
        for filename in os.listdir('./wordlist/'):
            # Get the full path of the file
            file_path = os.path.join('./wordlist/', filename)
            # Check if the file path is a file (not a directory)
            if os.path.isfile(file_path):
                # Append the file path to the list
                cls.wordlists.append(file_path)
        
        # Default wordlist for generating passphrases
        cls.passphrases = './wordlist/for_passphases.txt'

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
        cls.properties = False
        cls.speed = False
        cls.password = False
        cls.generate = False

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

        # Get arguments
        args = Arguments(cls).args 
        cls.parse_settings_args(args)
        cls.parse_wpa_args(args)

        # Commands
        if args.cracked:
            cls.show_cracked = True
        if args.check_handshake:
            cls.check_handshake = args.check_handshake
        if args.crack_handshake:
            cls.crack_handshake = True
        if args.properties:
            cls.properties = True
        if args.speed:
            cls.speed = True
        if args.password:
            cls.password = True
        if args.generate:
            cls.generate = True

    @classmethod
    def parse_settings_args(cls, args):
        """Parses basic settings/configurations from arguments."""

        if args.verbose:
            cls.verbose = args.verbose
            Color.pl('{+} {C}option:{W} verbosity level {G}%d{W}' % args.verbose)
    
    @classmethod
    def parse_wpa_args(cls, args):
        """Parses WPA-specific arguments"""
        if args.ignore_old_handshakes:
            cls.ignore_old_handshakes = True
            Color.pl('{+} {C}option:{W} will {O}ignore{W} existing handshakes (force capture)')

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
    def exit_gracefully(cls):
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
            
        exit()

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
