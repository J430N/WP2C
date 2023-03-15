#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Developer Name: Mr. Jason Teo Jie Chen
# Program Name: target.py
# Description: Hold information of previous found targets
# First Written On: 18 February 2023
# Edited On: 15 March 2023 

import re
from util.color import Color
from config import Configuration


class ArchivedTarget(object):
    """
        Holds information between scans from a previously found target
    """

    def __init__(self, target):
        self.bssid = target.bssid
        self.channel = target.channel
        self.decloaked = target.decloaked
        self.attacked = target.attacked
        self.essid = target.essid
        self.essid_known = target.essid_known
        self.essid_len = target.essid_len

    def transfer_info(self, other):
        """
            Helper function to transfer relevant fields into another Target or ArchivedTarget
        """
        other.attacked = self.attacked

        # If both targets know the essid, keep decloacked value
        if self.essid_known and other.essid_known:
            other.decloaked = self.decloaked

        # The destination target does not know the essid but the source
        # does, copy that information
        if self.essid_known and not other.essid_known:
            other.decloaked = self.decloaked
            other.essid = self.essid
            other.essid_known = self.essid_known
            other.essid_len = self.essid_len

    def __eq__(self, other):
        # Check if the other class type is either ArchivedTarget or Target
        return isinstance(other, (self.__class__, Target)) and self.bssid == other.bssid


class Target(object):
    """
        Holds details for a 'Target' aka Access Point (e.g. router).
    """

    def __init__(self, fields):
        """
            Initializes & stores target info based on fields.
            Args:
                Fields - List of strings
                INDEX KEY             EXAMPLE
                    0 BSSID           (00:1D:D5:9B:11:00)
                    1 First time seen (2015-05-27 19:28:43)
                    2 Last time seen  (2015-05-27 19:28:46)
                    3 channel         (6)
                    4 Speed           (54)
                    5 Privacy         (WPA2)
                    6 Cipher          (CCMP TKIP)
                    7 Authentication  (PSK)
                    8 Power           (-62)
                    9 beacons         (2)
                    10 # IV           (0)
                    11 LAN IP         (0.  0.  0.  0)
                    12 ID-length      (9)
                    13 ESSID          (HOME-ABCD)
                    14 Key            ()
        """
        self.manufacturer = None
        self.bssid = fields[0].strip()
        self.channel = fields[3].strip()
        self.encryption = fields[5].strip()
        self.authentication = fields[7].strip()

        # airodump sometimes does not report the encryption type for some reason
        # In this case (len = 0), defaults to WPA (which is the most common)
        if 'WPA' in self.encryption or len(self.encryption) == 0:
            self.encryption = 'WPA'
        elif 'WEP' in self.encryption:
            self.encryption = 'WEP'
        elif 'WPS' in self.encryption:
            self.encryption = 'WPS'

        if len(self.encryption) > 4:
            self.encryption = self.encryption[:4].strip()

        self.power = int(fields[8].strip())
        if self.power < 0:
            self.power += 100
        self.max_power = self.power

        self.beacons = int(fields[9].strip())
        self.ivs = int(fields[10].strip())

        self.essid_known = True
        self.essid_len = int(fields[12].strip())
        self.essid = fields[13]
        if self.essid == '\\x00' * self.essid_len or \
                self.essid == 'x00' * self.essid_len or \
                self.essid.strip() == '':
            # Don't display '\x00...' for hidden ESSIDs
            self.essid = None
            self.essid_known = False

        # Will be set to true once this target will be attacked
        # Needed to count targets in infinite attack mode
        self.attacked = False

        self.decloaked = False  # If ESSID was hidden but we decloaked it.

        self.clients = []

        self.validate()

    def __eq__(self, other):
        # Check if the other class type is either ArchivedTarget or Target
        return isinstance(other, (self.__class__, ArchivedTarget)) and self.bssid == other.bssid

    def transfer_info(self, other):
        """
            Helper function to transfer relevant fields into another Target or ArchivedTarget
        """
        
        other.attacked = self.attacked

        # If both targets know the essid, keep decloacked value
        if self.essid_known and other.essid_known:
            other.decloaked = self.decloaked

        # The destination target does not know the essid but the source
        # does, copy that information
        if self.essid_known and not other.essid_known:
            other.decloaked = self.decloaked
            other.essid = self.essid
            other.essid_known = self.essid_known
            other.essid_len = self.essid_len

    def validate(self):
        """ Checks that the target is valid. """
        if self.channel == '-1':
            raise Exception('Ignoring target with Negative-One (-1) channel')

        bssid_broadcast = re.compile(r'^(ff:ff:ff:ff:ff:ff|00:00:00:00:00:00)$', re.IGNORECASE)
        if bssid_broadcast.match(self.bssid):
            raise Exception('Ignoring target with Broadcast BSSID (%s)' % self.bssid)

        bssid_multicast = re.compile(r'^(01:00:5e|01:80:c2|33:33)', re.IGNORECASE)
        if bssid_multicast.match(self.bssid):
            raise Exception('Ignoring target with Multicast BSSID (%s)' % self.bssid)

    def to_str(self):
        # sourcery no-metrics
        """
            *Colored* string representation of this Target.
            Specifically formatted for the 'scanning' table view.
        """

        max_essid_len = 24
        essid = self.essid if self.essid_known else '(%s)' % self.bssid
        # Trim ESSID (router name) if needed
        if len(essid) > max_essid_len:
            essid = essid[:max_essid_len - 3] + '...'
        else:
            essid = essid.ljust(max_essid_len)

        if self.essid_known:
            # Known ESSID
            essid = Color.s('{C}%s' % essid)
        else:
            # Unknown ESSID
            essid = Color.s('{O}%s' % essid)

        # Add a '*' if we decloaked the ESSID
        decloaked_char = '*' if self.decloaked else ' '
        essid += Color.s('{P}%s' % decloaked_char)

        bssid = Color.s('{O}%s  ' % self.bssid)
        oui = ''.join(self.bssid.split(':')[:3])
        self.manufacturer = Configuration.manufacturers.get(oui, "")
        
        max_oui_len = 27
        manufacturer = Color.s('{W}%s  ' % self.manufacturer)
        # Trim manufacturer name if needed
        if len(manufacturer) > max_oui_len:
            manufacturer = manufacturer[:max_oui_len - 3] + '...'
        else:
            manufacturer = manufacturer.ljust(max_oui_len)

        channel_color = '{C}' if int(self.channel) > 14 else '{G}'
        channel = Color.s(f'{channel_color}{str(self.channel).ljust(3)}')

        encryption = self.encryption.ljust(3)
        if 'WEP' in encryption:
            encryption = Color.s('{G}%s  ' % encryption)
        elif 'WPA' in encryption:
            if 'PSK' in self.authentication:
                encryption = Color.s('{O}%s-P' % encryption)
            elif 'MGT' in self.authentication:
                encryption = Color.s('{R}%s-E' % encryption)
            else:
                encryption = Color.s('{O}%s  ' % encryption)
        else:
                encryption = Color.s('%s  ' % encryption)

        power = f'{str(self.power).ljust(3)}db'
        if self.power > 50:
            color = 'G'
        elif self.power > 35:
            color = 'O'
        else:
            color = 'R'
        power = Color.s('{%s}%s' % (color, power))

        clients = '       '
        if len(self.clients) > 0:
            clients = Color.s('{G}' +str(len(self.clients)))

        result = f'{essid}  {bssid}  {manufacturer}  {channel}  {encryption}  {power}  {clients}'

        result += Color.s('{W}')
        return result
