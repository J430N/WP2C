#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import sleep, time

from config import Configuration
from tools.airodump import Airodump
from util.color import Color


class Scanner(object):
    """ Scans wifi networks & provides menu for selecting targets """

    # Console code for moving up one line
    UP_CHAR = '\033[1A'

    def __init__(self):
        self.previous_target_count = 0
        self.target_archives = {}
        self.targets = []
        self.err_msg = None

    def find_targets(self):
        """
        Scans for targets via Airodump.
        Loops until scan is interrupted via user or config.
        Sets this object `targets` attribute (list[Target]) on interruption
        """

        # Loads airodump with interface/channel/etc from Configuration
        try:
            with Airodump() as airodump:
                # Loop until interrupted (Ctrl+C)
                scan_start_time = time()

                while True:
                    if airodump.pid.poll() is not None:
                        return True  # Airodump process died

                    self.targets = airodump.get_targets(old_targets=self.targets,
                                                        target_archives=self.target_archives)

                    if airodump.pid.poll() is not None:
                        return True  # Airodump process died

                    self.print_targets() # Display all available target

                    target_count = len(self.targets)
                    client_count = sum(len(t.clients) for t in self.targets)

                    outline = '\r{+} Scanning'
                    if airodump.decloaking:
                        outline += ' & decloaking'
                    outline += '. Found'
                    outline += ' {G}%d{W} target(s),' % target_count
                    outline += ' {G}%d{W} client(s).' % client_count
                    outline += ' {O}Ctrl+C{W} when ready '
                    Color.clear_entire_line()
                    Color.p(outline)

                    sleep(1)

        except KeyboardInterrupt:
            return True

    def update_targets(self):
        """
        Archive all the old targets
        Returns: True if user wants to stop attack, False otherwise
        """
        self.previous_target_count = 0

        self.targets = []
        return self.find_targets()

    def get_num_attacked(self):
        """
        Returns: number of attacked targets by this scanner
        """
        return sum(bool(target.attacked) for target in list(self.target_archives.values()))

    @staticmethod
    def clr_scr():
        import platform
        import os

        cmdtorun = 'cls' if platform.system().lower() == "windows" else 'clear'
        os.system(cmdtorun)

    def print_targets(self):
        """Prints targets selection menu (1 target per row)."""
        if len(self.targets) == 0:
            Color.p('\r')
            return

        if self.previous_target_count > 0 and Configuration.verbose <= 1:
            # Don't clear screen buffer in verbose mode.
            if self.previous_target_count > len(self.targets) or \
                    Scanner.get_terminal_height() < self.previous_target_count + 3:
                # Either:
                # 1) We have less targets than before, so we can't overwrite the previous list
                # 2) The terminal can't display the targets without scrolling.
                # Clear the screen.
                self.clr_scr()
            else:
                # We can fit the targets in the terminal without scrolling
                # 'Move' cursor up, so we will print over the previous list
                Color.pl(Scanner.UP_CHAR * (3 + self.previous_target_count))

        self.previous_target_count = len(self.targets)

        # Overwrite the current line
        Color.p('\r{W}{D}')

        # First row: columns
        Color.p('   NUM')
        Color.p('  ESSID (Wi-Fi name)')
        Color.p('         BSSID (MAC address)')
        Color.p('  MANUFACTURER')
        Color.pl('             CH   ENCRYP PWR    CLIENT')

        # Second row: separator
        Color.p('   ---')
        Color.p('  -------------------------')
        Color.p('  -------------------')
        Color.p('  -----------------------')
        Color.pl('  ---  ------ -----  ------{W}')

        # Remaining rows: targets
        for idx, target in enumerate(self.targets, start=1): #Adjust here
            Color.clear_entire_line()
            Color.p('   {G}%s  ' % str(idx).ljust(3)) #numuber to left only (need all to left)
            Color.pl(target.to_str())

    @staticmethod
    def get_terminal_height():
        import os
        (rows, columns) = os.popen('stty size', 'r').read().split()
        return int(rows)

    @staticmethod
    def get_terminal_width():
        import os
        (rows, columns) = os.popen('stty size', 'r').read().split()
        return int(columns)

    def select_targets(self):
        """
        Returns list(target)
        Either a specific target if user specified -bssid or --essid.
        If the user used pillage or infinite attack mode retuns all the targets
        Otherwise, prompts user to select targets and returns the selection.
        """

        if len(self.targets) == 0:
            if self.err_msg is not None:
                Color.pl(self.err_msg)
            raise Exception('No targets found.'
                            + ' You may need to wait longer,'
                            + ' or you may have issues with your wifi card')

        # Ask user for targets.
        self.print_targets()
        Color.clear_entire_line()

        if self.err_msg is not None:
            Color.pl(self.err_msg)

        input_str = '{+} Select target(s)'
        input_str += ' ({G}1-%d{W})' % len(self.targets)
        input_str += ' separated by commas, dashes'
        input_str += ' or {G}all{W}:{C} '

        chosen_targets = []

        Color.p(input_str)

        for choice in input().split(','):
            choice = choice.strip()
            if choice.lower() == 'all':
                chosen_targets = self.targets
                break
            if '-' in choice:
                # User selected a range
                (lower, upper) = [int(x) for x in choice.split('-')]
                if lower < 1 or lower > len(self.targets) or upper < 1 or upper > len(self.targets):
                    Color.pl('    {!} {O}Invalid target index (%s)... ignoring' % choice)
                    continue
                else:
                    lower -= 1
                    upper -= 1
                    for i in range(lower, min(len(self.targets), upper + 1)):
                        chosen_targets.append(self.targets[i])
            elif choice.isdigit() and int(choice) <= len(self.targets) and int(choice)> 0:
                chosen_targets.append(self.targets[int(choice) - 1])
            else:
                Color.pl('    {!} {O}Invalid target index (%s)... ignoring' % choice)
                continue
            
        return chosen_targets
        
