#!/usr/bin/env python
# -*- coding: utf-8 -*-

from config import Configuration
from util.process import Process
import time
from threading import Thread


class Aireplay(Thread):

    @staticmethod
    def deauth(target_bssid, essid=None, client_mac=None, num_deauths=None, timeout=2):
        num_deauths = num_deauths or Configuration.num_deauths
        deauth_cmd = [
            'aireplay-ng',
            '-0',  # Deauthentication
            str(num_deauths),
            '--ignore-negative-one',
            '-a', target_bssid,  # Target AP
            '-D'  # Skip AP detection
        ]
        if client_mac is not None:
            # Station-specific deauth
            deauth_cmd.extend(['-c', client_mac])
        if essid:
            deauth_cmd.extend(['-e', essid])
        deauth_cmd.append(Configuration.interface)
        proc = Process(deauth_cmd)
        while proc.poll() is None:
            if proc.running_time() >= timeout:
                proc.interrupt()
            time.sleep(0.2)