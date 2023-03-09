#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Developer Name: Mr. Jason Teo Jie Chen
# Program Name: ip.py
# Description: Command to put interface up and down
# First Written On: 15 February 2023
# Edited On: 20 February 2023

import re


class Ip():


    @classmethod
    def up(cls, interface):
        """Put interface up"""
        from util.process import Process

        (out, err) = Process.call(f'ip link set {interface} up')
        if len(err) > 0:
            raise Exception('Error putting interface %s up:\n%s\n%s' % (interface, out, err))

    @classmethod
    def down(cls, interface):
        """Put interface down"""
        from util.process import Process

        (out, err) = Process.call(f'ip link set {interface} down')
        if len(err) > 0:
            raise Exception('Error putting interface %s down:\n%s\n%s' % (interface, out, err))

    @classmethod
    def get_mac(cls, interface):
        from util.process import Process

        (out, err) = Process.call(f'ip link show {interface}')
        if match := re.search(r'([a-fA-F\d]{2}[-:]){5}[a-fA-F\d]{2}', out):
            return match[0].replace('-', ':')

        raise Exception(f'Could not find the mac address for {interface}')
