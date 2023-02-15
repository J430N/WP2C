#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re

from util.color import Color
from tools.macchanger import Macchanger


class Configuration(object):
    """ Stores configuration variables and functions for Wifite. """

    initialized = False  # Flag indicating config has been initialized
    verbose = 0
    version = '2.6.8'

    all_bands = None
    attack_max = None
    check_handshake = None
    clients_only = None
    cracked_file = None
    crack_handshake = None
    daemon = None
    dont_use_pmkid = None
    encryption_filter = None
    existing_commands = None
    five_ghz = None
    ignore_cracked = None
    ignore_essids = None
    ignore_old_handshakes = None
    infinite_mode = None
    inf_wait_time = None
    interface = None
    kill_conflicting_processes = None
    manufacturers = None
    min_power = None
    no_deauth = None
    no_nullpin = None
    num_deauths = None
    pmkid_timeout = None
    print_stack_traces = None
    random_mac = None
    require_fakeauth = None
    scan_time = None
    show_bssids = None
    show_cracked = None
    show_manufacturers = None
    skip_crack = None
    target_bssid = None
    target_channel = None
    target_essid = None
    temp_dir = None  # Temporary directory
    two_ghz = None
    wordlist = None
    wpa_attack_timeout = None
    wpa_deauth_timeout = None
    wpa_filter = None
    wpa_handshake_dir = None
    wpa_strip_handshake = None

    @classmethod
    def initialize(cls, load_interface=True):
        """
            Sets up default initial configuration values.
            Also sets config values based on command-line arguments.
        """
        # TODO: categorize configuration into
        # separate classes (under config/*.py)
        # E.g. Configuration.wps.enabled,
        # Configuration.wps.timeout, etc

        # Only initialize this class once
        if cls.initialized:
            return
        cls.initialized = True

        cls.verbose = 0  # Verbosity of output. Higher number means more debug info about running processes.
        cls.print_stack_traces = True

        cls.kill_conflicting_processes = False

        cls.scan_time = 0  # Time to wait before attacking all targets

        cls.tx_power = 0  # Wifi transmit power (0 is default)
        cls.interface = None
        cls.min_power = 0  # Minimum power for an access point to be considered a target. Default is 0
        cls.attack_max = 0
        cls.skip_crack = False
        cls.target_channel = None  # User-defined channel to scan
        cls.target_essid = None  # User-defined AP name
        cls.target_bssid = None  # User-defined AP BSSID
        cls.ignore_essids = None  # ESSIDs to ignore
        cls.ignore_cracked = False  # Ignore previously-cracked BSSIDs
        cls.clients_only = False  # Only show targets that have associated clients
        cls.all_bands = False  # Scan for both 2Ghz and 5Ghz channels
        cls.two_ghz = False  # Scan 2.4Ghz channels
        cls.five_ghz = False  # Scan 5Ghz channels
        cls.infinite_mode = False  # Attack targets continuously
        cls.inf_wait_time = 60
        cls.show_bssids = False  # Show BSSIDs in targets list
        cls.show_manufacturers = False  # Show manufacturers in targets list
        cls.random_mac = False  # Should generate a random Mac address at startup.
        cls.no_deauth = False  # Deauth hidden networks & WPA handshake targets
        cls.num_deauths = 1  # Number of deauth packets to send to each target.
        cls.daemon = False  # Don't put back interface back in managed mode

        cls.encryption_filter = ['WEP', 'WPA', 'WPS']

        # WPA variables
        cls.wpa_filter = False  # Only attack WPA networks
        cls.wpa_deauth_timeout = 15  # Wait time between deauths
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
            from .tools.airmon import Airmon
            cls.interface = Airmon.ask()
            if cls.random_mac:
                Macchanger.random()

    @classmethod
    def load_from_arguments(cls):
        """ Sets configuration values based on Argument.args object """
        from args import Arguments

        args = Arguments(cls).args #Display all arguments
        cls.parse_settings_args(args)
        cls.parse_wpa_args(args)
        cls.parse_encryption()


        # Commands
        if args.cracked:
            cls.show_cracked = True
        if args.check_handshake:
            cls.check_handshake = args.check_handshake
        if args.crack_handshake:
            cls.crack_handshake = True

    @classmethod
    def parse_settings_args(cls, args):
        """Parses basic settings/configurations from arguments."""

        if args.random_mac:
            cls.random_mac = True
            Color.pl('{+} {C}option:{W} using {G}random mac address{W} when scanning & attacking')

        if args.channel:
            chn_arg_re = re.compile("^\d+((,\d+)|(-\d+,\d+))*(-\d+)?$")
            if not chn_arg_re.match(args.channel):
                raise ValueError("Invalid channel! The format must be 1,3-6,9")

            cls.target_channel = args.channel
            Color.pl('{+} {C}option:{W} scanning for targets on channel {G}%s{W}' % args.channel)

        if args.interface:
            cls.interface = args.interface
            Color.pl('{+} {C}option:{W} using wireless interface {G}%s{W}' % args.interface)

        if args.target_bssid:
            cls.target_bssid = args.target_bssid
            Color.pl('{+} {C}option:{W} targeting BSSID {G}%s{W}' % args.target_bssid)

        if args.all_bands:
            cls.all_bands = True
            Color.pl('{+} {C}option:{W} including both {G}2.4Ghz and 5Ghz networks{W} in scans')

        if args.two_ghz:
            cls.two_ghz = True
            Color.pl('{+} {C}option:{W} including {G}2.4Ghz networks{W} in scans')

        if args.five_ghz:
            cls.five_ghz = True
            Color.pl('{+} {C}option:{W} including {G}5Ghz networks{W} in scans')

        if args.infinite_mode:
            cls.infinite_mode = True
            Color.p('{+} {C}option:{W} ({G}infinite{W}) attack all neighbors forever')
            if not args.scan_time:
                Color.p(f'; {{O}}pillage time not selected{{W}}, using default {{G}}{cls.inf_wait_time:d}{{W}}s')
                args.scan_time = cls.inf_wait_time
            Color.pl('')

        if args.show_bssids:
            cls.show_bssids = True
            Color.pl('{+} {C}option:{W} showing {G}bssids{W} of targets during scan')

        if args.show_manufacturers is True:
            cls.show_manufacturers = True
            Color.pl('{+} {C}option:{W} showing {G}manufacturers{W} of targets during scan')

        if args.no_deauth:
            cls.no_deauth = True
            Color.pl('{+} {C}option:{W} will {R}not{W} {O}deauth{W} clients during scans or captures')

        if args.daemon is True:
            cls.daemon = True
            Color.pl('{+} {C}option:{W} will put interface back to managed mode')

        if args.num_deauths and args.num_deauths > 0:
            cls.num_deauths = args.num_deauths
            Color.pl(f'{{+}} {{C}}option:{{W}} send {{G}}{cls.num_deauths:d}{{W}} deauth packets when deauthing')

        if args.min_power and args.min_power > 0:
            cls.min_power = args.min_power
            Color.pl(f'{{+}} {{C}}option:{{W}} Minimum power {{G}}{cls.min_power:d}{{W}} for target to be shown')

        if args.skip_crack:
            cls.skip_crack = True
            Color.pl('{+} {C}option:{W} Skip cracking captured handshakes/pmkid {G}enabled{W}')

        if args.attack_max and args.attack_max > 0:
            cls.attack_max = args.attack_max
            Color.pl(f'{{+}} {{C}}option:{{W}} Attack first {{G}}{cls.attack_max:d}{{W}} targets from list')

        if args.target_essid:
            cls.target_essid = args.target_essid
            Color.pl('{+} {C}option:{W} targeting ESSID {G}%s{W}' % args.target_essid)

        if args.ignore_essids is not None:
            cls.ignore_essids = args.ignore_essids
            Color.pl('{+} {C}option: {O}ignoring ESSID(s): {R}%s{W}' %
                     ', '.join(args.ignore_essids))

        if args.ignore_cracked:
            from .model.result import CrackResult
            if cracked_targets := CrackResult.load_all():
                cls.ignore_cracked = [item['bssid'] for item in cracked_targets]
                Color.pl('{+} {C}option: {O}ignoring {R}%s{O} previously-cracked targets' % len(cls.ignore_cracked))

            else:
                Color.pl('{!} {R}Previously-cracked access points not found in %s' % cls.cracked_file)
                cls.ignore_cracked = False
        if args.clients_only:
            cls.clients_only = True
            Color.pl('{+} {C}option:{W} {O}ignoring targets that do not have associated clients')

        if args.scan_time:
            cls.scan_time = args.scan_time
            Color.pl(
                f'{{+}} {{C}}option:{{W}} ({{G}}pillage{{W}}) attack all targets after {{G}}{args.scan_time:d}{{W}}s')

        if args.verbose:
            cls.verbose = args.verbose
            Color.pl('{+} {C}option:{W} verbosity level {G}%d{W}' % args.verbose)

        if args.kill_conflicting_processes:
            cls.kill_conflicting_processes = True
            Color.pl('{+} {C}option:{W} kill conflicting processes {G}enabled{W}')

    @classmethod
    def parse_wpa_args(cls, args):
        """Parses WPA-specific arguments"""
        if args.wpa_filter:
            cls.wpa_filter = args.wpa_filter

        if args.wordlist:
            if not os.path.exists(args.wordlist):
                cls.wordlist = None
                Color.pl('{+} {C}option:{O} wordlist {R}%s{O} was not found, wifite will NOT attempt to crack '
                         'handshakes' % args.wordlist)
            elif os.path.isfile(args.wordlist):
                cls.wordlist = args.wordlist
                Color.pl('{+} {C}option:{W} using wordlist {G}%s{W} for cracking' % args.wordlist)
            elif os.path.isdir(args.wordlist):
                cls.wordlist = None
                Color.pl('{+} {C}option:{O} wordlist {R}%s{O} is a directory, not a file. Wifite will NOT attempt to '
                         'crack handshakes' % args.wordlist)

        if args.wpa_deauth_timeout:
            cls.wpa_deauth_timeout = args.wpa_deauth_timeout
            Color.pl('{+} {C}option:{W} will deauth WPA clients every {G}%d seconds{W}' % args.wpa_deauth_timeout)

        if args.wpa_attack_timeout:
            cls.wpa_attack_timeout = args.wpa_attack_timeout
            Color.pl(
                '{+} {C}option:{W} will stop WPA handshake capture after {G}%d seconds{W}' % args.wpa_attack_timeout)

        if args.ignore_old_handshakes:
            cls.ignore_old_handshakes = True
            Color.pl('{+} {C}option:{W} will {O}ignore{W} existing handshakes (force capture)')

        if args.wpa_handshake_dir:
            cls.wpa_handshake_dir = args.wpa_handshake_dir
            Color.pl('{+} {C}option:{W} will store handshakes to {G}%s{W}' % args.wpa_handshake_dir)

        if args.wpa_strip_handshake:
            cls.wpa_strip_handshake = True
            Color.pl('{+} {C}option:{W} will {G}strip{W} non-handshake packets')

    @classmethod
    def parse_encryption(cls):
        """Adjusts encryption filter (WEP and/or WPA and/or WPS)"""
        cls.encryption_filter = []
        if cls.wpa_filter:
            cls.encryption_filter.append('WPA')

        if len(cls.encryption_filter) == 3:
            Color.pl('{+} {C}option:{W} targeting {G}all encrypted networks{W}')
        elif not cls.encryption_filter:
            # Default to scan all types
            cls.encryption_filter = ['WEP', 'WPA', 'WPS']
        else:
            Color.pl('{+} {C}option:{W} targeting {G}%s-encrypted{W} networks' % '/'.join(cls.encryption_filter))

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
        tmp = mkdtemp(prefix='wifite')
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
        Macchanger.reset_if_changed()
        from .tools.airmon import Airmon
        if cls.interface is not None and Airmon.base_interface is not None:
            if not cls.daemon:
                Color.pl('{!} {O}Note:{W} Leaving interface in {G}Monitor Mode{W}!')
                if Airmon.use_ipiw:
                    Color.pl('{!} To disable {G}Monitor Mode{W} when finished: ')
                    Color.pl('{+}   {C}ip link set %s down{W}' % cls.interface)
                    Color.pl('{+}   {C}iw %s set type managed{W}' % cls.interface)
                    Color.pl('{+}   {C}ip link set %s up{W}\n' % cls.interface)
                else:
                    Color.pl('{!} To disable Monitor Mode when finished: {C}airmon-ng stop %s{W}\n' % cls.interface)
            else:
                # Stop monitor mode
                Airmon.stop(cls.interface)
                # Bring original interface back up
                Airmon.put_interface_up(Airmon.base_interface)

        if Airmon.killed_network_manager:
            Color.pl('{!} You can restart NetworkManager when finished ({C}service NetworkManager start{W})')
            # Airmon.start_network_manager()

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


if __name__ == '__main__':
    Configuration.initialize(False)
    print((Configuration.dump()))
