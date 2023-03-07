#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from util.process import Process


class Tshark():

    def __init__(self):
        pass

    @staticmethod
    def _extract_src_dst_index_total(line):
        # Extract BSSIDs, handshake # (1-4) and handshake 'total' (4)
        mac_regex = ('[a-zA-Z0-9]{2}:' * 6)[:-1]
        match = re.search(r'(%s)\s*.*\s*(%s).*Message.*(\d).*of.*(\d)' % (mac_regex, mac_regex), line)
        if match is None:
            # Line doesn't contain src, dst, Message numbers
            return None, None, None, None
        (src, dst, index, total) = match.groups()
        return src, dst, index, total

    @staticmethod
    def _build_target_client_handshake_map(output, bssid=None):
        # Map of target_ssid,client_ssid -> handshake #s
        # E.g. 12:34:56,21:43:65 -> 3
        target_client_msg_nums = {}

        for line in output.split('\n'):
            src, dst, index, total = Tshark._extract_src_dst_index_total(line)
            if src is None:
                continue  # Skip

            index = int(index)
            total = int(total)

            if total != 4:
                continue  # Handshake X of 5? X of 3? Skip it.

            # Identify the client and target MAC addresses
            if index % 2 == 1:
                # First and Third messages
                target = src
                client = dst
            else:
                # Second and Fourth messages
                client = src
                target = dst

            if bssid is not None and bssid.lower() != target.lower():
                # We know the BSSID and this msg was not for the target
                continue

            target_client_key = f'{target},{client}'

            # Ensure all 4 messages are:
            # Between the same client and target (not different clients connecting).
            # In numeric & chronological order (Message 1, then 2, then 3, then 4)
            if index == 1:
                target_client_msg_nums[target_client_key] = 1  # First message

            elif target_client_key not in target_client_msg_nums \
                    or index - 1 != target_client_msg_nums[target_client_key]:
                continue  # Not first message. We haven't gotten the first message yet. Skip.

            else:
                # Happy case: Message is > 1 and is received in-order
                target_client_msg_nums[target_client_key] = index

        return target_client_msg_nums

    @staticmethod
    def bssids_with_handshakes(capfile, bssid=None):

        # Returns list of BSSIDs for which we have valid handshakes in the capfile.
        command = [
            'tshark',
            '-r', capfile,
            '-n',  # Don't resolve addresses
            '-Y', 'eapol'  # Filter for only handshakes
        ]
        tshark = Process(command, devnull=False)

        target_client_msg_nums = Tshark._build_target_client_handshake_map(tshark.stdout(), bssid=bssid)

        bssids = set()
        # Check if we have all 4 messages for the handshake between the same MACs
        for (target_client, num) in list(target_client_msg_nums.items()):
            if num == 4:
                # We got a handshake!
                this_bssid = target_client.split(',')[0]
                bssids.add(this_bssid)

        return list(bssids)

    @staticmethod
    def bssid_essid_pairs(capfile, bssid):
        # Finds all BSSIDs (with corresponding ESSIDs) from cap file.
        # Returns list of tuples(BSSID, ESSID)

        ssid_pairs = set()

        command = [
            'tshark',
            '-r', capfile,  # Path to cap file
            '-n',  # Don't resolve addresses
            # Extract beacon frames
            '-Y', '"wlan.fc.type_subtype == 0x08 || wlan.fc.type_subtype == 0x05"',
        ]

        tshark = Process(command, devnull=False)

        for line in tshark.stdout().split('\n'):
            # Extract src, dst, and essid
            mac_regex = ('[a-zA-Z0-9]{2}:' * 6)[:-1]
            match = re.search(f'({mac_regex}) [^ ]* ({mac_regex}).*.*SSID=(.*)$', line)
            if match is None:
                continue  # Line doesn't contain src, dst, ssid

            (src, dst, essid) = match.groups()

            if dst.lower() == 'ff:ff:ff:ff:ff:ff':
                continue  # Skip broadcast packets

            if (bssid is not None and bssid.lower() == src.lower()) or bssid is None:
                ssid_pairs.add((src, essid))  # This is our BSSID, add it

        return list(ssid_pairs)