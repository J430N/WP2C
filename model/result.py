#!/usr/bin/env python
# -*- coding: utf-8 -*-*

# Developer Name: Mr. Jason Teo Jie Chen
# Program Name: result.py
# Description: Save cracked result to json and pdf files
# First Written On: 18 February 2023
# Edited On: 8 March 2023 

import os
import time
from util.color import Color
from config import Configuration
from json import loads, dumps
from util.report import Report


class CrackResult(object):
    """ Abstract class containing results from a crack session """
    
    def __init__(self):
        self.date = int(time.time())
        self.loc = 'ND'
        self.readable_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.date))

    def dump(self):
        raise Exception('Unimplemented method: dump()')

    def to_dict(self):
        raise Exception('Unimplemented method: to_dict()')

    def print_single_line(self, longest_essid):
        raise Exception('Unimplemented method: print_single_line()')

    def print_single_line_prefix(self, longest_essid):
        essid = self.essid or 'N/A'
        Color.p('{W} ')
        Color.p('{C}%s{W}' % essid.ljust(longest_essid))
        Color.p('  ')
        Color.p('{GR}%s{W}' % self.bssid.ljust(17))
        Color.p('  ')
        Color.p('{D}%s{W}' % self.readable_date.ljust(19))
        Color.p('  ')

    def save(self):
        """ Adds this crack result to the cracked file and saves it. """
        name = Configuration.cracked_file
        saved_results = []
        if os.path.exists(name):
            with open(name, 'r') as fid:
                text = fid.read()
            try:
                saved_results = loads(text)
            except Exception as e:
                Color.pl('{!} error while loading %s: %s' % (name, str(e)))

        # Check for duplicates
        this_dict = self.to_dict()
        this_dict.pop('date')
        for entry in saved_results:
            this_dict['date'] = entry.get('date')
            if 'loc' in this_dict:
                this_dict['loc'] = entry.get('loc')
            if entry == this_dict:
                # Skip if we already saved this BSSID+ESSID+TYPE+KEY+LOC
                Color.pl('{+} {C}%s{O} already exists in {G}%s{O}, skipping.' % (
                    self.essid, Configuration.cracked_file))
                return

        saved_results.append(self.to_dict())
        with open(name, 'w') as fid:
            fid.write(dumps(saved_results, indent=2))
        Color.pl('{+} saved crack result to {C}%s{W} ({G}%d total{W})'
                 % (name, len(saved_results)))
        Report.run(self.essid)

    @classmethod
    def display(cls):
        """ Show cracked targets from cracked file """
        name = Configuration.cracked_file
        if not os.path.exists(name):
            Color.pl('{!} {O}file {C}%s{O} not found{W}' % name)
            return

        with open(name, 'r') as fid:
            cracked_targets = loads(fid.read())

        if len(cracked_targets) == 0:
            Color.pl('{!} {R}no results found in {O}%s{W}' % name)
            return

        Color.pl('{+} Displaying {G}%d{W} cracked target(s) from {C}%s{W}\n' % (
            len(cracked_targets), name))

        results = sorted([cls.load(item) for item in cracked_targets], key=lambda x: x.date, reverse=True)
        longest_essid = max(len(result.essid or 'ESSID') for result in results)
        if longest_essid < 5:
            longest_essid = 5
        
        longest_key = max(len(result.key or 'KEY') for result in results)
        if longest_key < 3:
            longest_key = 3

        # Header
        Color.p('{D} ')
        Color.p('ESSID'.ljust(longest_essid))
        Color.p('  ')
        Color.p('BSSID'.ljust(17))
        Color.p('  ')
        Color.p('DATE'.ljust(19))
        Color.p('  ')
        Color.p('TYPE'.ljust(5))
        Color.p('  ')
        Color.p('KEY')
        Color.pl('{D}')
        Color.p(' ' + '-' * (longest_essid + 17 + 19 + 5 + 8 + longest_key))
        Color.pl('{W}')
        # Results
        for result in results:
            result.print_single_line(longest_essid)
        Color.pl('')

    @classmethod
    def load_all(cls):
        if not os.path.exists(Configuration.cracked_file):
            return []
        with open(Configuration.cracked_file, 'r') as json_file:
            try:
                json = loads(json_file.read())
            except ValueError:
                return []
        return json

    @staticmethod
    def load(json):
        """ Returns an instance of the appropriate object given a json instance """
        global result
        if json['type'] == 'WPA':
            from .wpa_result import CrackResultWPA
            result = CrackResultWPA(json['bssid'],
                                    json['essid'],
                                    json['handshake_file'],
                                    json['key'])
        result.date = json['date']
        # Convert seconds to readable date and time (1970-01-02 07:30:00 - date and time of the file created)
        result.readable_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(result.date))
        return result
