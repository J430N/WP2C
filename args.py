#!/usr/bin/env python
# -*- coding: utf-8 -*-

from util.color import Color

import argparse
import sys


class Arguments(object):
    """ Holds arguments used by the WP2C """

    def __init__(self, configuration):
        self.verbose = '-v' in sys.argv or '-hv' in sys.argv or '-vh' in sys.argv
        self.config = configuration # class 'config.Configuration
        self.args = self.get_arguments() #Collect arguments pass to WP2C in script.

    def _verbose(self, msg):
        return Color.s(msg) if self.verbose else argparse.SUPPRESS

    def get_arguments(self):
        """ Returns parser.args() containing all program arguments """

        parser = argparse.ArgumentParser(usage=argparse.SUPPRESS,
                                         formatter_class=lambda prog:
                                         argparse.HelpFormatter(prog, max_help_position=80, width=130)) #Help message setting

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
                              'Prints commands and outputs. Increase verbosity by increasing numbers of v e.g. {C}-vv{W} (default: {G}quiet{W})'))
        
        glob.add_argument('--properties',
                          action = 'store_true',
                          dest='properties',
                          help=Color.s('Shows current Wi-Fi properties'))
        
        glob.add_argument('--speed',
                          action = 'store_true',
                          dest='speed',
                          help=Color.s('Test current Wi-Fi upload and download speed'))
        
        glob.add_argument('--password',
                          action = 'store_true',
                          dest='password',
                          help=Color.s('Test current Wi-Fi upload and download speed'))
        
        glob.add_argument('--generate',
                          action = 'store_true',
                          dest='generate',
                          help=Color.s('Test current Wi-Fi upload and download speed'))   
        
        glob.add_argument('--report',
                          action = 'store_true',
                          dest='report',
                          help=Color.s('Test current Wi-Fi upload and download speed'))
                         
    def _add_wpa_args(self, wpa):
        wpa.add_argument('--new',
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

    @staticmethod
    def _add_command_args(commands):
        commands.add_argument('--history',
                              action='store_true',
                              dest='cracked',
                              help=Color.s('Print previously-cracked access points'))

        commands.add_argument('--check',
                              action='store',
                              metavar='file',
                              nargs='?',
                              const='<all>',
                              dest='check_handshake',
                              help=Color.s('Check a {C}.cap file{W} (or all {C}hs/*.cap{W} files) for WPA handshakes'))

        commands.add_argument('--crack',
                              action='store_true',
                              dest='crack_handshake',
                              help=Color.s('Show commands to crack a captured handshake'))

