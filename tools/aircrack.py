#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re

from tools.dependency import Dependency
from config import Configuration
from util.process import Process


class Aircrack(Dependency):
    dependency_required = True
    dependency_name = 'aircrack-ng'
    dependency_url = 'https://www.aircrack-ng.org/install.html'

    @staticmethod
    def crack_handshake(handshake, show_command=False):
        from util.color import Color
        from util.timer import Timer
        '''Tries to crack a handshake. Returns WPA key if found, otherwise None.'''

        key_file = Configuration.temp('wpakey.txt')
        command = [
            'aircrack-ng',
            '-a', '2',
            '-w', Configuration.wordlist,
            '--bssid', handshake.bssid,
            '-l', key_file,
            handshake.capfile
        ]
        if show_command:
            Color.pl('{+} {D}Running: {W}{P}%s{W}' % ' '.join(command))
        crack_proc = Process(command)

        # Report progress of cracking
        aircrack_nums_re = re.compile(r'(\d+)/(\d+) keys tested.*\(([\d.]+)\s+k/s')
        aircrack_key_re = re.compile(r'Current passphrase:\s*(\S.*\S)\s*$')
        num_tried = num_total = 0
        percent = num_kps = 0.0
        eta_str = 'unknown'
        current_key = ''
        while crack_proc.poll() is None:
            line = crack_proc.pid.stdout.readline()
            match_nums = aircrack_nums_re.search(line.decode('utf-8'))
            match_keys = aircrack_key_re.search(line.decode('utf-8'))
            if match_nums:
                num_tried = int(match_nums[1])
                num_total = int(match_nums[2])
                num_kps = float(match_nums[3])
                eta_seconds = (num_total - num_tried) / num_kps
                eta_str = Timer.secs_to_str(eta_seconds)
                percent = 100.0 * float(num_tried) / float(num_total)
            elif match_keys:
                current_key = match_keys[1]
            else:
                continue

            status = '\r{+} {C}Cracking WPA Handshake: %0.2f%%{W}' % percent
            status += ' ETA: {C}%s{W}' % eta_str
            status += ' @ {C}%0.1fkps{W}' % num_kps
            # status += ' ({C}%d{W}/{C}%d{W} keys)' % (num_tried, num_total)
            status += ' (current key: {C}%s{W})' % current_key
            Color.clear_entire_line()
            Color.p(status)

        Color.pl('')

        if not os.path.exists(key_file):
            return None
        with open(key_file, 'r') as fid:
            key = fid.read().strip()
        os.remove(key_file)

        return key