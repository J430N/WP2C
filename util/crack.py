#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from json import loads

from config import Configuration
from model.handshake import Handshake
from model.wpa_result import CrackResultWPA
from tools.aircrack import Aircrack
from util.color import Color


class CrackHelper:
    """Manages handshake retrieval, selection, and running the cracking commands."""

    TYPES = {
        '4-WAY': '4-Way Handshake',
    }

    @classmethod
    def run(cls):
        Configuration.initialize(False)

        # Get handshakes
        handshakes = cls.get_handshakes()
        if len(handshakes) == 0:
            Color.pl('{!} {O}No handshakes found{W}')
            return

        hs_to_crack = cls.get_user_selection(handshakes)

        tool_name = 'aircrack'
        
        try:
            for hs in hs_to_crack:
                cls.crack(hs, tool_name)
        except KeyboardInterrupt:
            Color.pl('\n{!} {O}Interrupted{W}')

    @classmethod
    def is_cracked(cls, file):
        if not os.path.exists(Configuration.cracked_file):
            return False
        with open(Configuration.cracked_file) as f:
            json = loads(f.read())
        if json is None:
            return False
        for result in json:
            for k in list(result.keys()): # This is the key
                v = result[k] # This is the value
                if 'file' in k and os.path.basename(v) == file:
                    return True
        return False

    @classmethod
    def get_handshakes(cls):
        handshakes = []

        skipped_cracked_files = 0

        hs_dir = Configuration.wpa_handshake_dir
        if not os.path.exists(hs_dir) or not os.path.isdir(hs_dir):
            Color.pl('\n{!} {O}directory not found: {R}%s{W}' % hs_dir)
            return []

        Color.pl('\n{+} Listing captured handshakes from {C}%s{W}:\n' % os.path.abspath(hs_dir))
        for hs_file in os.listdir(hs_dir):
            if hs_file.count('_') != 3:
                continue

            if cls.is_cracked(hs_file):
                skipped_cracked_files += 1
                continue

            if hs_file.endswith('.cap'):
                # WPA Handshake
                hs_type = '4-WAY'
            else:
                continue

            name, essid, bssid, date= hs_file.split('_')
            date = date.rsplit('.', 1)[0]
            days, hours = date.split('T')
            hours = hours.replace('-', ':')
            date = f'{days} {hours}'

            if hs_type == '4-WAY':
                # Patch for essid with " " (zero) or dot "." in name
                handshakenew = Handshake(os.path.join(hs_dir, hs_file))
                handshakenew.divine_bssid_and_essid()
                essid_discovery = handshakenew.essid

                essid = essid if essid_discovery is None else essid_discovery
            handshake = {
                'filename': os.path.join(hs_dir, hs_file),
                'bssid': bssid.replace('-', ':'),
                'essid': essid,
                'date': date,
                'type': hs_type
            }

            if hs_file.endswith('.cap'):
                # WPA Handshake
                handshake['type'] = '4-WAY'
            else:
                continue

            handshakes.append(handshake)

        if skipped_cracked_files > 0:
            Color.pl('{!} {O}Skipping %d already cracked files.{W}\n' % skipped_cracked_files)

        # Sort by Date (Descending)
        return sorted(handshakes, key=lambda x: x.get('date'), reverse=True)

    @classmethod
    def print_handshakes(cls, handshakes):
        # Header
        max_essid_len = max([len(hs['essid']) for hs in handshakes] + [len('ESSID (truncated)')])
        Color.p('{W}{D}  NUM')
        Color.p('  ' + 'ESSID (truncated)'.ljust(max_essid_len))
        Color.p('  ' + 'BSSID'.ljust(17))
        Color.p('  ' + 'TYPE'.ljust(5))
        Color.p('  ' + 'DATE CAPTURED\n')
        Color.p('  ---')
        Color.p('  ' + ('-' * max_essid_len))
        Color.p('  ' + ('-' * 17))
        Color.p('  ' + ('-' * 5))
        Color.p('  ' + ('-' * 19) + '{W}\n')
        # Handshakes
        for index, handshake in enumerate(handshakes, start=1):
            Color.p('  {G}%s{W}' % str(index).rjust(3))
            Color.p('  {C}%s{W}' % handshake['essid'].ljust(max_essid_len))
            Color.p('  {O}%s{W}' % handshake['bssid'].ljust(17))
            Color.p('  {C}%s{W}' % handshake['type'].ljust(5))
            Color.p('  {W}%s{W}\n' % handshake['date'])

    @classmethod
    def get_user_selection(cls, handshakes):
        cls.print_handshakes(handshakes)

        Color.p(
            '{+} Select handshake(s) to crack ({G}%d{W}-{G}%d{W}, select multiple with '
            '{C},{W} or {C}-{W} or {C}all{W}): {G}' % (1, len(handshakes)))
        choices = input()
        Color.p('{W}')

        selection = []
        for choice in choices.split(','):
            if '-' in choice:
                first, last = [int(x) for x in choice.split('-')]
                for index in range(first, last + 1):
                    selection.append(handshakes[index - 1])
            elif choice.strip().lower() == 'all':
                selection = handshakes[:]
                break
            elif [c.isdigit() for c in choice]:
                index = int(choice)
                selection.append(handshakes[index - 1])

        return selection

    @classmethod
    def crack(cls, hs, tool):
        Color.pl('\n{+} Cracking {G}%s {C}%s{W} ({C}%s{W}) using {C}aircrack{W}' % (
            cls.TYPES[hs['type']], hs['essid'], hs['bssid']))

        if hs['type'] == '4-WAY':
            crack_result = cls.crack_4way(hs, tool)
        else:
            raise ValueError(f'Cannot crack handshake: Type is not 4-WAY. Handshake={hs}')

        if crack_result is None:
            # Failed to crack
            Color.pl('{!} {R}Failed to crack {O}%s{R} ({O}%s{R}): Passphrase not in dictionary' % (
                hs['essid'], hs['bssid']))
        else:
            # Cracked, replace existing entry (if any), or add to
            Color.pl('{+} {G}Cracked{W} {C}%s{W} ({C}%s{W}). Key: "{G}%s{W}"' % (
                hs['essid'], hs['bssid'], crack_result.key))
            crack_result.save()

    @classmethod
    def crack_4way(cls, hs, tool):

        handshake = Handshake(hs['filename'],
                            bssid=hs['bssid'],
                            essid=hs['essid'])
        try:
            handshake.divine_bssid_and_essid()
        except ValueError as e:
            Color.pl('{!} {R}Error: {O}%s{W}' % e)
            return None

        if tool == 'aircrack':
            for wordlist in Configuration.wordlists:
                key = Aircrack.crack_handshake(wordlist, handshake, show_command=True)

        if key is not None:
            return CrackResultWPA(hs['bssid'], hs['essid'], hs['filename'], key)
        else:
            return None
