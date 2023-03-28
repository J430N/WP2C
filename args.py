#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Developer Name: Mr. Jason Teo Jie Chen
# Program Name: args.py
# Description: Holds arguments used by the WP2C
# First Written On: 18 February 2023
# Edited On: 9 March 2023 

import argparse
import sys
from util.color import Color


class Arguments(object):
    """ Holds arguments used by the WP2C """

    def __init__(self, configuration):

        self.verbose = '-v' in sys.argv
        self.config = configuration
        self.args = self.get_arguments() # Collect arguments pass to WP2C in script.

    def _verbose(self, msg):
        return Color.s(msg) if self.verbose else argparse.SUPPRESS

    def get_arguments(self):
        """ Returns parser.args() containing all program arguments """

        parser = argparse.ArgumentParser(usage=argparse.SUPPRESS,
                                         formatter_class=lambda prog:
                                         argparse.HelpFormatter(prog, max_help_position=80, width=130)) # Help message setting.

        self._add_global_args(parser.add_argument_group(Color.s('{C}FUNCTIONS{W}')))
        self._add_wpa_args(parser.add_argument_group(Color.s('{C}WPA{W}')))

        return parser.parse_args() # Reads the command-line arguments and returns an 'args' object containing the values of the parsed arguments.

    def _add_global_args(self, glob):
        glob.add_argument('-vv',
                          action='count',
                          default=0,
                          dest='verbose',
                          help=Color.s(
                              'Increase verbosity to show additional commands and outputs. (default: {G}quiet{W})'))
        
        glob.add_argument('--properties',
                          action = 'store_true',
                          dest='properties',
                          help=Color.s('Shows current Wi-Fi properties'))
        
        glob.add_argument('--speed',
                          action = 'store_true',
                          dest='speed',
                          help=Color.s('Test current network upload and download speed and ping time'))
        
        glob.add_argument('--password',
                          action = 'store_true',
                          dest='password',
                          help=Color.s('Test your password strength'))
        
        glob.add_argument('--generate',
                          action = 'store_true',
                          dest='generate',
                          help=Color.s('Generate new password for you'))
        
        glob.add_argument('New wordlist',
                          action = 'store_true',
                          help=Color.s('Add new wordlist into {C}wordlist {W}folder directly. ({C}Note: {W}Please make sure the wordlist is in {C}.txt {W}format)'))
                         
    def _add_wpa_args(self, wpa):
        wpa.add_argument('--new',
                         action='store_true',
                         dest='ignore_old_handshakes',
                         help=Color.s('Captures new handshakes, ignores existing handshakes in {C}%s{W} '
                                      '(default: {G}off{W})' % self.config.wpa_handshake_dir))
        wpa.add_argument('--history',
                              action='store_true',
                              dest='cracked',
                              help=Color.s('Print previously-cracked Wi-Fi'))

        wpa.add_argument('--check',
                              action='store',
                              metavar='file path',
                              nargs='?',
                              const='<all>',
                              dest='check_handshake',
                              help=Color.s('Check a {C}.cap file{W} (or all {C}hs/*.cap{W} files) for WPA handshakes'))

        wpa.add_argument('--crack',
                              action='store_true',
                              dest='crack_handshake',
                              help=Color.s('Crack a uncracked captured handshake'))
        

