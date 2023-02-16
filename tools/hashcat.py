#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .dependency import Dependency
from config import Configuration
from util.process import Process
from util.color import Color

import os

hccapx_autoremove = False  # change this to True if you want the hccapx files to be automatically removed


class Hashcat(Dependency):
    dependency_required = False
    dependency_name = 'hashcat'
    dependency_url = 'https://hashcat.net/hashcat/'

    @staticmethod
    def should_use_force():
        command = ['hashcat', '-I']
        stderr = Process(command).stderr()
        return 'No devices found/left' or 'Unstable OpenCL driver detected!' in stderr

    @staticmethod
    def crack_handshake(handshake, show_command=False):
        # Generate hccapx
        hccapx_file = HcxPcapngTool.generate_hccapx_file(handshake, show_command=show_command)

        key = None
        # Crack hccapx
        for additional_arg in ([], ['--show']):
            command = [
                'hashcat',
                '--quiet',
                '-m', '22000',
                hccapx_file,
                Configuration.wordlist
            ]
            if Hashcat.should_use_force():
                command.append('--force')
            command.extend(additional_arg)
            if show_command:
                Color.pl(f'{{+}} {{D}}Running: {{W}}{{P}}{" ".join(command)}{{W}}')
            process = Process(command)
            stdout, stderr = process.get_output()
            if ':' not in stdout:
                continue
            key = stdout.split(':', 5)[-1].strip()
            break

        return key

class HcxPcapngTool(Dependency):
    dependency_required = False
    dependency_name = 'hcxpcapngtool'
    dependency_url = 'apt install hcxtools'

    def __init__(self, target):
        self.target = target
        self.bssid = self.target.bssid.lower().replace(':', '')
        self.pmkid_file = Configuration.temp(f'pmkid-{self.bssid}.22000')

    @staticmethod
    def generate_hccapx_file(handshake, show_command=False):
        hccapx_file = Configuration.temp('generated.hccapx')
        if os.path.exists(hccapx_file):
            os.remove(hccapx_file)

        command = [
            'hcxpcapngtool',
            '-o', hccapx_file,
            handshake.capfile
        ]

        if show_command:
            Color.pl('{+} {D}Running: {W}{P}%s{W}' % ' '.join(command))

        process = Process(command)
        stdout, stderr = process.get_output()
        if not os.path.exists(hccapx_file):
            raise ValueError('Failed to generate .hccapx file, output: \n%s\n%s' % (
                stdout, stderr))

        return hccapx_file

    @staticmethod
    def generate_john_file(handshake, show_command=False):
        john_file = Configuration.temp('generated.john')
        if os.path.exists(john_file):
            os.remove(john_file)

        command = [
            'hcxpcapngtool',
            '--john', john_file,
            handshake.capfile
        ]

        if show_command:
            Color.pl('{+} {D}Running: {W}{P}%s{W}' % ' '.join(command))

        process = Process(command)
        stdout, stderr = process.get_output()
        if not os.path.exists(john_file):
            raise ValueError('Failed to generate .john file, output: \n%s\n%s' % (
                stdout, stderr))

        return john_file