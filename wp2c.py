#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Files named __init__.py are used to mark directories on disk as Python package directories. If remove the __init__.py file, Python will no longer look for submodules inside that directory, so attempts to import the module will fail.
#  if __name__ == '__main__' allows file to run directly from command line

from util.color import Color
from config import Configuration
import banner
import os


class WP2C(object):

    def __init__(self):  # Constructors is to initialize(assign values) to the data members of the class when an object of the class is created
                         # self represents the instance of the class. By using the “self”  we can access the attributes and methods of the class in python.
        """
        1. Initializes WP2C.
        2. Checks the WP2C is running under root permissions and ensures dependencies are installed.
        """

        banner.print_banner()  # Print WP2C's banner

        Configuration.initialize(load_interface=False)

        if os.getuid() != 0:
            Color.pl('{!} {R}Error: {O}WP2C{R} require {O}root {R}permissions to run{W}')
            Color.pl('{!} {R}Recommendation: Re-run the WP2C with {O}sudo{W}')
            Configuration.exit_gracefully(0)
        
    def start(self):
        """
        Performs different actions depending on user input.
        """
        from model.result import CrackResult
        from model.handshake import Handshake
        from util.crack import CrackHelper
        from tools.properties import Properties
        from tools.speed import Speed
        
        if Configuration.show_cracked:  # Print previously-cracked access points
            CrackResult.display()

        elif Configuration.check_handshake: # Check a .cap file (or all hs/*.cap files) for WPA handshakes
            Handshake.check()

        elif Configuration.crack_handshake:  # Show commands to crack a captured handshake
            CrackHelper.run()
        
        elif Configuration.wifi_properties:  # Show wifi properties
            Properties.run()  
        
        elif Configuration.speed: # Test internet speed
            Speed.run()

        else:
            Configuration.get_monitor_mode_interface()  # WPA attack start here!
            self.scan_and_attack()

    @staticmethod
    def scan_and_attack():
        """
        1) Scans for targets, asks user to select targets
        2) Attacks each target
        """
        from util.scanner import Scanner
        from attack.all import AttackAll

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
    Configuration.exit_gracefully(0)


if __name__ == '__main__': #It Allows You to Execute Code When the File Runs as a Script, but Not When It’s Imported as a Module
    entry_point()
