#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Developer Name: Mr. Jason Teo Jie Chen
# Program Name: airodump.py
# Description: Logging founded Access Point and Client
# First Written On: 15 February 2023
# Edited On: 20 February 2023

import os
import time
from util.process import Process
from config import Configuration
from model.target import Target
from model.client import Client


class Airodump():

    def __init__(self, interface=None, channel=None, encryption=None,
                  target_bssid=None,
                 output_file_prefix='airodump',
                 ivs_only=False, delete_existing_files=True):
        """Sets up airodump arguments, doesn't start process yet."""
        Configuration.initialize()

        if interface is None:
            interface = Configuration.interface
        if interface is None:
            raise Exception('Wireless interface must be defined (-i)')
        self.interface = interface
        self.targets = []

        self.channel = channel

        self.encryption = encryption

        self.target_bssid = target_bssid
        self.output_file_prefix = output_file_prefix
        self.ivs_only = ivs_only

        self.delete_existing_files = delete_existing_files

    def __enter__(self):
        """
        Setting things up for this context.
        Called at start of 'with Airodump(...) as x:'
        Actually starts the airodump process.
        """
        if self.delete_existing_files:
            self.delete_airodump_temp_files(self.output_file_prefix)

        self.csv_file_prefix = Configuration.temp() + self.output_file_prefix

        # Build the command
        command = [
            'airodump-ng',
            self.interface,
            '-a',  # Only show associated clients
            '-w', self.csv_file_prefix,  # Output file prefix
            '--write-interval', '1',  # Write every second
            '--band', 'abg' # 2.4Ghz and 5Ghz bands
        ]
        if self.channel:
            command.extend(['-c', str(self.channel)])

        if self.encryption:
            command.extend(['--enc', self.encryption])

        if self.target_bssid:
            command.extend(['--bssid', self.target_bssid])

        if self.ivs_only:
            command.extend(['--output-format', 'ivs,csv'])
        else:
            command.extend(['--output-format', 'pcap,csv'])

        # Store value for debugging
        self.command = command

        # Start the process
        self.pid = Process(command, devnull=True)
        return self

    def __exit__(self, type, value, traceback):
        """
        Tearing things down since the context is being exited.
        Called after 'with Airodump(...)' goes out of scope.
        """
        # Kill the process
        self.pid.interrupt()

        if self.delete_existing_files:
            self.delete_airodump_temp_files(self.output_file_prefix)

    def find_files(self, endswith=None):
        return self.find_files_by_output_prefix(self.output_file_prefix, endswith=endswith)

    @classmethod
    def find_files_by_output_prefix(cls, output_file_prefix, endswith=None):
        """ Finds all files in the temp directory that start with the output_file_prefix """
        result = []
        temp = Configuration.temp()
        for fil in os.listdir(temp):
            if not fil.startswith(output_file_prefix):
                continue

            if endswith is None or fil.endswith(endswith):
                result.append(os.path.join(temp, fil))

        return result

    @classmethod
    def delete_airodump_temp_files(cls, output_file_prefix):
        """
        Deletes airodump* files in the temp directory.
        Also deletes replay_*.cap and *.xor files in pwd.
        """
        # Remove all temp files
        for fil in cls.find_files_by_output_prefix(output_file_prefix):
            os.remove(fil)

        # Remove .cap and .xor files from pwd
        for fil in os.listdir('.'):
            if fil.startswith('replay_') and fil.endswith('.cap') or fil.endswith('.xor'):
                os.remove(fil)

        # Remove replay/cap/xor files from temp
        temp_dir = Configuration.temp()
        for fil in os.listdir(temp_dir):
            if fil.startswith('replay_') and fil.endswith('.cap') or fil.endswith('.xor'):
                os.remove(os.path.join(temp_dir, fil))

    def get_targets(self, old_targets=None, target_archives=None):
        """ Parses airodump's CSV file, returns list of Targets """

        if old_targets is None:
            old_targets = []
        if target_archives is None:
            target_archives = {}
        # Find the .CSV file
        csv_filename = None
        for fil in self.find_files(endswith='.csv'):
            csv_filename = fil  # Found the file
            break

        if csv_filename is None or not os.path.exists(csv_filename):
            return self.targets  # No file found

        new_targets = Airodump.get_targets_from_csv(csv_filename)

        # Check if one of the targets is also contained in the old_targets
        for new_target in new_targets:
            just_found = True
            for old_target in old_targets:
                # If the new_target is found in old_target copy attributes from old target
                if old_target == new_target:
                    # Identify decloaked targets
                    if new_target.essid_known and not old_target.essid_known:
                        # We decloaked a target!
                        new_target.decloaked = True

                    old_target.transfer_info(new_target)
                    just_found = False
                    break

            # If the new_target is not in old_targets, check target_archives and copy attributes from there
            if just_found and new_target.bssid in target_archives:
                target_archives[new_target.bssid].transfer_info(new_target)

        # Sort by power
        new_targets.sort(key=lambda x: x.power, reverse=True)

        self.targets = new_targets

        return self.targets

    @staticmethod
    def get_targets_from_csv(csv_filename):
        """Returns list of Target objects parsed from CSV file."""
        targets = []
        import chardet
        import csv

        with open(csv_filename, "rb") as rawdata:
            encoding = chardet.detect(rawdata.read())['encoding']

        with open(csv_filename, 'r', encoding=encoding, errors='ignore') as csvopen:
            lines = []
            for line in csvopen:
                line = line.replace('\0', '')
                lines.append(line)

            csv_reader = csv.reader(lines,
                                    delimiter=',',
                                    quoting=csv.QUOTE_ALL,
                                    skipinitialspace=True,
                                    escapechar='\\')

            hit_clients = False
            for row in csv_reader:
                # Each 'row' is a list of fields for a target/client
                if len(row) == 0:
                    continue

                if row[0].strip() == 'BSSID':
                    # This is the 'header' for the list of Targets
                    hit_clients = False
                    continue

                elif row[0].strip() == 'Station MAC':
                    # This is the 'header' for the list of Clients
                    hit_clients = True
                    continue

                if hit_clients:
                    # The current row corresponds to a 'Client' (computer)
                    try:
                        client = Client(row)
                    except (IndexError, ValueError):
                        # Skip if we can't parse the client row
                        continue

                    if 'not associated' in client.bssid:
                        # Ignore unassociated clients
                        continue

                    # Add this client to the appropriate Target
                    for t in targets:
                        if t.bssid == client.bssid:
                            t.clients.append(client)
                            break

                else:
                    # The current row corresponds to a 'Target' (router)
                    try:
                        target = Target(row)
                        targets.append(target)
                    except Exception:
                        continue

        return targets