#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Developer Name: Mr. Jason Teo Jie Chen
# Program Name: wpa_result.py
# Description: Display cracked result for WPA after attack
# First Written On: 18 February 2023
# Edited On: 2 March 2023 

from util.color import Color
from .result import CrackResult


class CrackResultWPA(CrackResult):
    def __init__(self, bssid, essid, handshake_file, key):
        self.result_type = 'WPA'
        self.bssid = bssid
        self.essid = essid
        self.handshake_file = handshake_file
        self.key = key
        super(CrackResultWPA, self).__init__()

    def dump(self):
        if self.essid:
            Color.pl(f'{{+}} {"Access Point Name".ljust(19)}: {{C}}{self.essid}{{W}}')
        if self.bssid:
            Color.pl(f'{{+}} {"Access Point BSSID".ljust(19)}: {{C}}{self.bssid}{{W}}')
        Color.pl('{+} %s: {C}%s{W}' % ('Encryption'.ljust(19), self.result_type))
        if self.handshake_file:
            Color.pl('{+} %s: {C}%s{W}' % ('Handshake File'.ljust(19), self.handshake_file))
        if self.key:
            Color.pl('{+} %s: {G}%s{W}' % ('PSK (password)'.ljust(19), self.key))
        else:
            Color.pl('{!} %s  {O}key unknown{W}' % ''.ljust(19))

    def print_single_line(self, longest_essid):
        self.print_single_line_prefix(longest_essid)
        Color.p('{G}%s{W}' % 'WPA'.ljust(5))
        Color.p('  ')
        Color.p('{G}%s{W}' % self.key)
        Color.pl('')

    def to_dict(self):
        return {
            'type': self.result_type,
            'date': self.date,
            'essid': self.essid,
            'bssid': self.bssid,
            'key': self.key,
            'handshake_file': self.handshake_file
        }
