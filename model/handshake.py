#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
from util.process import Process
from util.color import Color
from tools.tshark import Tshark


class Handshake(object):

    def __init__(self, capfile, bssid=None, essid=None):
        self.capfile = capfile
        self.bssid = bssid
        self.essid = essid

    def divide_bssid_and_essid(self):
        """
            Tries to find BSSID and ESSID from cap file.
            Sets this instances 'bssid' and 'essid' instance fields.
        """

        # We can get BSSID from the .cap filename if WP2C captured it.
        # ESSID is stripped of non-printable characters, so we can't rely on that.
        if self.bssid is None:
            hs_regex = re.compile(r'^.*handshake_\w+_([\dA-F\-]{17})_.*\.cap$', re.IGNORECASE)
            result = hs_regex.match(self.capfile)
            if result is not None:
                self.bssid = result[1].replace('-', ':')

        # Get list of bssid/essid pairs from cap file
        pairs = Tshark.bssid_essid_pairs(self.capfile, bssid=self.bssid)

        if len(pairs) == 0 and (not self.bssid and not self.essid):
            # Tshark failed us, nothing else we can do.
            raise ValueError(f'Cannot find BSSID or ESSID in cap file {self.capfile}')

        if not self.essid and not self.bssid:
            # We do not know the bssid nor the essid
            self.bssid = pairs[0][0]
            self.essid = pairs[0][1]
            Color.pl('{!} {O}Warning{W}: {O}Arbitrarily selected ' +
                     '{R}bssid{O} {C}%s{O} and {R}essid{O} "{C}%s{O}"{W}' % (self.bssid, self.essid))

        if not self.bssid:
            # We already know essid
            for (bssid, essid) in pairs:
                if self.essid == essid:
                    Color.pl('\n{+} Discovered bssid {C}%s{W}' % bssid)
                    self.bssid = bssid
                    break

        if not self.essid:
            # We already know bssid
            if len(pairs) > 0:
                for (bssid, essid) in pairs:
                    if self.bssid.lower() == bssid.lower():
                        Color.pl('\n{+} Discovered essid "{C}%s{W}"' % essid)
                        self.essid = essid
                        break

    def has_handshake(self):
        if not self.bssid or not self.essid:
            self.divide_bssid_and_essid()

        if len(self.tshark_handshakes()) > 0:
            return True

        return False

    def tshark_handshakes(self):
        """Returns list[tuple] of BSSID & ESSID pairs (ESSIDs are always `None`)."""
        tshark_bssids = Tshark.bssids_with_handshakes(self.capfile, bssid=self.bssid)
        return [(bssid, None) for bssid in tshark_bssids]


    def aircrack_handshakes(self):
        """Returns tuple (BSSID,None) if aircrack thinks self.capfile contains a handshake / can be cracked"""
        if not self.bssid:
            return []  # Aircrack requires BSSID

        command = [
            'aircrack-ng',
            '-b', self.bssid,
            self.capfile
        ]

        proc = Process(command, devnull=False)

        if 'potential target' in proc.stdout().lower() and 'no matching network' not in proc.stdout().lower():
            return [(self.bssid, None)]
        else:
            return []

    def analyze(self):
        """Prints analysis of handshake capfile"""
        self.divide_bssid_and_essid()

        Handshake.print_pairs(self.aircrack_handshakes(), 'aircrack')

    def strip(self, outfile=None):
        """
            Strips out packets from handshake that aren't necessary to crack.
            Leaves only handshake packets and SSID broadcast (for discovery).
            Args:
                outfile - Filename to save stripped handshake to.
                          If outfile==None, overwrite existing self.capfile.
        """
        if not outfile:
            outfile = f'{self.capfile}.temp'
            replace_existing_file = True
        else:
            replace_existing_file = False

        cmd = [
            'tshark',
            '-r', self.capfile,  # input file
            '-Y', 'wlan.fc.type_subtype == 0x08 || wlan.fc.type_subtype == 0x05 || eapol',  # filter
            '-w', outfile  # output file
        ]
        proc = Process(cmd)
        proc.wait()
        if replace_existing_file:
            from shutil import copy
            copy(outfile, self.capfile)
            os.remove(outfile)

    @staticmethod
    def print_pairs(pairs, tool=None):
        """
            Prints out BSSID and/or ESSID given a list of tuples (bssid,essid)
        """
        tool_str = '{C}%s{W}: ' % tool.rjust(8) if tool is not None else ''
        if len(pairs) == 0:
            Color.pl('{!} %s.cap file {R}does not{O} contain a valid handshake{W}' % tool_str)
            return

        for (bssid, essid) in pairs:
            out_str = '{+} %s.cap file {G}contains a valid handshake{W} for' % tool_str
            if bssid and essid:
                Color.pl('%s ({G}%s{W}) [{G}%s{W}]' % (out_str, bssid, essid))
            elif bssid:
                Color.pl('%s ({G}%s{W})' % (out_str, bssid))
            elif essid:
                Color.pl('%s [{G}%s{W}]' % (out_str, essid))

    @staticmethod
    def check():
        """ Analyzes .cap file(s) for handshake """
        from config import Configuration
        if Configuration.check_handshake == '<all>':
            Color.pl('\n{+} Checking all handshakes in {G}./%s{W} directory\n' % Configuration.wpa_handshake_dir)
            try:
                capfiles = [os.path.join(Configuration.wpa_handshake_dir, x) for x in os.listdir(Configuration.wpa_handshake_dir) if x.endswith('.cap')]
            except OSError:
                capfiles = []
            if not capfiles:
                Color.pl('{!} {R}no .cap files found in {O}./%s{W}\n' % Configuration.wpa_handshake_dir)
        else:
            capfiles = [Configuration.check_handshake]

        for capfile in capfiles:
            Color.pl('{+} Checking for handshake in .cap file {C}%s{W}' % capfile)
            if not os.path.exists(capfile):
                Color.pl('{!} {O}.cap file {C}%s{O} not found{W}' % capfile)
                return
            hs = Handshake(capfile)
            hs.analyze()
            Color.pl('')