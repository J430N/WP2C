#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Developer Name: Mr. Jason Teo Jie Chen
# Program Name: iw.py
# Description: Command to set interface to managed mode and monitor mode
# First Written On: 15 February 2023
# Edited On: 20 February 2023

class Iw():

    @classmethod
    def mode(cls, iface, mode_name):
        from util.process import Process
        return Process.call(f'iw {iface} set type {mode_name}')

    @classmethod
    def get_interfaces(cls, mode=None):
        from util.process import Process
        import re

        ireg = re.compile(r"\s+Interface\s[a-zA-Z\d]+")
        mreg = re.compile(r"\s+type\s[a-zA-Z]+")

        interfaces = set()
        iface = ''

        (out, err) = Process.call('iw dev')
        if mode is None:
            for line in out.split('\n'):
                if ires := ireg.search(line):
                    interfaces.add(ires.group().split("Interface")[-1])
        else:
            for line in out.split('\n'):
                ires = ireg.search(line)
                if mres := mreg.search(line):
                    if mode == mres.group().split("type")[-1][1:]:
                        interfaces.add(iface)
                if ires:
                    iface = ires.group().split("Interface")[-1][1:]

        return list(interfaces)