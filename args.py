#!/usr/bin/env python
# -*- coding: utf-8 -*-

from util.color import Color

import argparse
import sys


class Arguments(object):
    """ Holds arguments used by the Wifite """

    def __init__(self, configuration):
        # Hack: Check for -v before parsing args;
        # so we know which commands to display.
        self.verbose = '-v' in sys.argv or '-hv' in sys.argv or '-vh' in sys.argv
        self.config = configuration
        self.args = self.get_arguments()

    def _verbose(self, msg):
        return Color.s(msg) if self.verbose else argparse.SUPPRESS

    def get_arguments(self):
        """ Returns parser.args() containing all program arguments """

        parser = argparse.ArgumentParser(usage=argparse.SUPPRESS,
                                         formatter_class=lambda prog:
                                         argparse.HelpFormatter(prog, max_help_position=80, width=130)) #Help message

        self._add_global_args(parser.add_argument_group(Color.s('{C}SETTINGS{W}'))) #Display and pass the arguments values
        self._add_wpa_args(parser.add_argument_group(Color.s('{C}WPA{W}')))
        self._add_command_args(parser.add_argument_group(Color.s('{C}COMMANDS{W}')))

        return parser.parse_args() #Reads the command-line arguments and returns an 'args' object containing the values of the parsed arguments

    def _add_global_args(self, glob):
        glob.add_argument('-v',
                          '--verbose',
                          action='count',
                          default=0,
                          dest='verbose',
                          help=Color.s(
                              'Shows more options ({C}-h -v{W}). Prints commands and outputs. (default: {G}quiet{W})'))

        glob.add_argument('-i',
                          action='store',
                          dest='interface',
                          metavar='[interface]',
                          type=str,
                          help=Color.s('Wireless interface to use, e.g. {C}wlan0mon{W} (default: {G}ask{W})'))

        glob.add_argument('-c',
                          action='store',
                          dest='channel',
                          metavar='[channel]',
                          help=Color.s('Wireless channel to scan e.g. {C}1,3-6{W} (default: {G}all 2Ghz channels{W})'))
        glob.add_argument('--channel', help=argparse.SUPPRESS, action='store', dest='channel')

        glob.add_argument('-ab',
                          '--allbands',
                          action='store_true',
                          dest='all_bands',
                          help=self._verbose('Include both 2.4Ghz and 5Ghz bands (default: {G}off{W})'))

        glob.add_argument('-2',
                          '--2ghz',
                          action='store_true',
                          dest='two_ghz',
                          help=self._verbose('Include 2.4Ghz channels (default: {G}off{W})'))

        glob.add_argument('-5',
                          '--5ghz',
                          action='store_true',
                          dest='five_ghz',
                          help=self._verbose('Include 5Ghz channels (default: {G}off{W})'))

        glob.add_argument('-inf',
                          '--infinite',
                          action='store_true',
                          dest='infinite_mode',
                          help=Color.s(
                              'Enable infinite attack mode. Modify scanning time with {C}-p{W} (default: {G}off{W})'))

        glob.add_argument('-mac',
                          '--random-mac',
                          action='store_true',
                          dest='random_mac',
                          help=Color.s('Randomize wireless card MAC address (default: {G}off{W})'))

        glob.add_argument('-p',
                          action='store',
                          dest='scan_time',
                          nargs='?',
                          const=10,
                          metavar='scan_time',
                          type=int,
                          help=Color.s('{G}Pillage{W}: Attack all targets after {C}scan_time{W} (seconds)'))
        glob.add_argument('--pillage', help=argparse.SUPPRESS, action='store',
                          dest='scan_time', nargs='?', const=10, type=int)

        glob.add_argument('--kill',
                          action='store_true',
                          dest='kill_conflicting_processes',
                          help=Color.s('Kill processes that conflict with Airmon/Airodump (default: {G}off{W})'))

        glob.add_argument('-pow',
                          '--power',
                          action='store',
                          dest='min_power',
                          metavar='[min_power]',
                          type=int,
                          help=Color.s('Attacks any targets with at least {C}min_power{W} signal strength'))

        glob.add_argument('--skip-crack',
                          action='store_true',
                          dest='skip_crack',
                          help=Color.s('Skip cracking captured handshakes/pmkid (default: {G}off{W})'))

        glob.add_argument('-first',
                          '--first',
                          action='store',
                          dest='attack_max',
                          metavar='[attack_max]',
                          type=int,
                          help=Color.s('Attacks the first {C}attack_max{W} targets'))

        glob.add_argument('-b',
                          action='store',
                          dest='target_bssid',
                          metavar='[bssid]',
                          type=str,
                          help=self._verbose('BSSID (e.g. {GR}AA:BB:CC:DD:EE:FF{W}) of access point to attack'))
        glob.add_argument('--bssid', help=argparse.SUPPRESS, action='store', dest='target_bssid', type=str)

        glob.add_argument('-e',
                          action='store',
                          dest='target_essid',
                          metavar='[essid]',
                          type=str,
                          help=self._verbose('ESSID (e.g. {GR}NETGEAR07{W}) of access point to attack'))
        glob.add_argument('--essid', help=argparse.SUPPRESS, action='store', dest='target_essid', type=str)

        glob.add_argument('-E',
                          action='append',
                          dest='ignore_essids',
                          metavar='[text]',
                          type=str,
                          default=None,
                          help=self._verbose(
                              'Hides targets with ESSIDs that match the given text. Can be used more than once.'))
        glob.add_argument('--ignore-essid', help=argparse.SUPPRESS, action='append', dest='ignore_essids', type=str)

        glob.add_argument('-ic',
                          '--ignore-cracked',
                          action='store_true',
                          dest='ignore_cracked',
                          help=Color.s('Hides previously-cracked targets. (default: {G}off{W})'))

        glob.add_argument('--clients-only',
                          action='store_true',
                          dest='clients_only',
                          help=Color.s('Only show targets that have associated clients (default: {G}off{W})'))

        glob.add_argument('--showb',
                          action='store_true',
                          dest='show_bssids',
                          help=self._verbose('Show BSSIDs of targets while scanning'))

        glob.add_argument('--showm',
                          action='store_true',
                          dest='show_manufacturers',
                          help=self._verbose('Show manufacturers of targets while scanning'))

        glob.add_argument('--nodeauths',
                          action='store_true',
                          dest='no_deauth',
                          help=Color.s('Passive mode: Never deauthenticates clients (default: {G}deauth targets{W})'))
        glob.add_argument('--no-deauths', action='store_true', dest='no_deauth', help=argparse.SUPPRESS)
        glob.add_argument('-nd', action='store_true', dest='no_deauth', help=argparse.SUPPRESS)

        glob.add_argument('--num-deauths',
                          action='store',
                          type=int,
                          dest='num_deauths',
                          metavar='[num]',
                          default=None,
                          help=self._verbose(
                              'Number of deauth packets to send (default: {G}%d{W})' % self.config.num_deauths))

        glob.add_argument('--daemon',
                          action='store_true',
                          dest='daemon',
                          help=Color.s('Puts device back in managed mode after quitting (default: {G}off{W})'))

    def _add_wpa_args(self, wpa):
        wpa.add_argument('--wpa',
                         action='store_true',
                         dest='wpa_filter',
                         help=Color.s('Show only {C}WPA-encrypted networks{W} (includes {C}WPS{W})'))
        wpa.add_argument('-wpa', help=argparse.SUPPRESS, action='store_true', dest='wpa_filter')

        wpa.add_argument('--hs-dir',
                         action='store',
                         dest='wpa_handshake_dir',
                         metavar='[dir]',
                         type=str,
                         help=self._verbose(
                             'Directory to store handshake files (default: {G}%s{W})' % self.config.wpa_handshake_dir))
        wpa.add_argument('-hs-dir', help=argparse.SUPPRESS, action='store', dest='wpa_handshake_dir', type=str)

        wpa.add_argument('--new-hs',
                         action='store_true',
                         dest='ignore_old_handshakes',
                         help=Color.s('Captures new handshakes, ignores existing handshakes in {C}%s{W} '
                                      '(default: {G}off{W})' % self.config.wpa_handshake_dir))

        wpa.add_argument('--dict',
                         action='store',
                         dest='wordlist',
                         metavar='[file]',
                         type=str,
                         help=Color.s(
                             'File containing passwords for cracking (default: {G}%s{W})') % self.config.wordlist)

        wpa.add_argument('--wpadt',
                         action='store',
                         dest='wpa_deauth_timeout',
                         metavar='[seconds]',
                         type=int,
                         help=self._verbose('Time to wait between sending Deauths (default: {G}%d sec{W})'
                                            % self.config.wpa_deauth_timeout))
        wpa.add_argument('-wpadt', help=argparse.SUPPRESS, action='store', dest='wpa_deauth_timeout', type=int)

        wpa.add_argument('--wpat',
                         action='store',
                         dest='wpa_attack_timeout',
                         metavar='[seconds]',
                         type=int,
                         help=self._verbose('Time to wait before failing WPA attack (default: {G}%d sec{W})'
                                            % self.config.wpa_attack_timeout))
        wpa.add_argument('-wpat', help=argparse.SUPPRESS, action='store', dest='wpa_attack_timeout', type=int)

        # TODO: Uncomment the --strip option once it works
        '''
        wpa.add_argument('--strip',
            action='store_true',
            dest='wpa_strip_handshake',
            default=False,
            help=Color.s('Strip unnecessary packets from handshake capture using tshark'))
        '''
        wpa.add_argument('-strip', help=argparse.SUPPRESS, action='store_true', dest='wpa_strip_handshake')

    @staticmethod
    def _add_command_args(commands):
        commands.add_argument('--cracked',
                              action='store_true',
                              dest='cracked',
                              help=Color.s('Print previously-cracked access points'))

        commands.add_argument('-cracked',
                              help=argparse.SUPPRESS,
                              action='store_true',
                              dest='cracked')

        commands.add_argument('--check',
                              action='store',
                              metavar='file',
                              nargs='?',
                              const='<all>',
                              dest='check_handshake',
                              help=Color.s('Check a {C}.cap file{W} (or all {C}hs/*.cap{W} files) for WPA handshakes'))

        commands.add_argument('-check',
                              help=argparse.SUPPRESS,
                              action='store',
                              nargs='?',
                              const='<all>',
                              dest='check_handshake')

        commands.add_argument('--crack',
                              action='store_true',
                              dest='crack_handshake',
                              help=Color.s('Show commands to crack a captured handshake'))


if __name__ == '__main__':
    from .config import Configuration

    Configuration.initialize(False)
    a = Arguments(Configuration)
    args = a.args
    for (key, value) in sorted(args.__dict__.items()):
        Color.pl('{C}%s: {G}%s{W}' % (key.ljust(21), value))
