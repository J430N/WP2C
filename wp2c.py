#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Developer Name: Jason Teo Jie Chen
# Program Name: wp2c.py
# Description: This is the main program of WP2C. It is used to run the program from command line.
# First Written On: 22/2/2023
# Edited On: 7/3/2023 


import subprocess
import banner
import os
from util.color import Color
from config import Configuration
from model.result import CrackResult
from model.handshake import Handshake
from util.crack import CrackHelper
from tools.properties import Properties
from tools.speed import Speed
from tools.password import Password
from tools.generate import Generate
from util.scanner import Scanner
from attack.all import AttackAll

# Check dependencies for report
try:
    import reportlab
except ModuleNotFoundError:
    Color.pl('{!} {R}reportlab{O} module not found. Installing it now...{W}\n')
    subprocess.run(['pip', 'install', 'reportlab'])
    Color.pl('\n{!} {O}Rerun the {R}WP2C.py {O}again after the {R}reportlab {O}module installation is complete.{W}')
    Configuration.exit_gracefully()

try:
    import zxcvbn
except ModuleNotFoundError:
    Color.pl('{!} {R}zxcvbn{O} module not found. Installing it now...{W}\n')
    subprocess.run(['pip', 'install', 'zxcvbn'])
    Color.pl('\n{!} {O}Rerun the {R}WP2C.py {O}again after the {R}zxcvbn {O}module installation is complete.{W}')
    Configuration.exit_gracefully()


class WP2C(object):

    def __init__(self):
        '''
        1. Initializes WP2C.
        2. Checks the WP2C is running under root permissions and ensures dependencies are installed.
        '''

        banner.print_banner()  # Print WP2C's banner

        Configuration.initialize(load_interface=False)

        if os.getuid() != 0:
            Color.pl('{!} {R}Error: {O}WP2C{R} require {O}root {R}permissions to run{W}')
            Color.pl('{!} {R}Recommendation: Re-run the WP2C with {O}sudo{W}')
            Configuration.exit_gracefully()
        
    def start(self):
        '''
        Performs different actions depending on user input.
        '''
        if Configuration.show_cracked:  # Print previously-cracked access points
            CrackResult.display()

        elif Configuration.check_handshake: # Check a .cap file (or all hs/*.cap files) for WPA handshakes
            Handshake.check()

        elif Configuration.crack_handshake:  # Show commands to crack a captured handshake
            CrackHelper.run()
        
        elif Configuration.properties:  # Show wifi properties
            Properties.run()  
        
        elif Configuration.speed: # Test internet speed
            Speed.run()

        elif Configuration.password: # Test password strength
            Password.run()
        
        elif Configuration.generate: # Geneerate new password
            Generate.run()
            
        else:
            Configuration.get_monitor_mode_interface()  # WPA attack start here!
            self.scan_and_attack()

    @staticmethod
    def scan_and_attack():
        '''Scans for targets, asks user to select targets.'''
        
        Color.pl('')

        # Scan
        s = Scanner()
        s.find_targets()
        targets = s.select_targets()

        # Attack
        attacked_targets = AttackAll.attack_multiple(targets)

        Color.pl('{+} Finished attacking {C}%d{W} target(s), exiting' % attacked_targets)

def entry_point():
    try:
        wp2c = WP2C()
        wp2c.start()
    except Exception as e:
        Color.pexception(e)
        Color.pl('\n{!} {R}Exiting{W}\n')
    except KeyboardInterrupt:
        Color.pl('\n{!} {O}Interrupted, Shutting down...{W}')
    Configuration.exit_gracefully()


if __name__ == '__main__': #It Allows You to Execute Code When the File Runs as a Script, but Not When It’s Imported as a Module
    entry_point()
