#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Files named __init__.py are used to mark directories on disk as Python package directories. If remove the __init__.py file, Python will no longer look for submodules inside that directory, so attempts to import the module will fail.
#  __main__.py run file directly from command line
# try:
#     from .config import Configuration
# except (ValueError, ImportError) as e:
#     raise Exception(
#         "You may need to run WP2C from the root directory (which includes README.md)", e) from e

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

        from tools.dependency import Dependency
        Dependency.run_dependency_check()
        
    def start(self):
        """
        Starts target-scan + attack loop, or launches utilities depending on user input. (!!!!!!!Edit 3 of these functions)
        """
        from model.result import CrackResult
        from model.handshake import Handshake
        from util.crack import CrackHelper

        if Configuration.show_cracked:  # Print previously-cracked access points
            CrackResult.display()

        # Check a .cap file (or all hs/*.cap files) for WPA handshakes
        elif Configuration.check_handshake:
            Handshake.check()

        elif Configuration.crack_handshake:  # Show commands to crack a captured handshake
            CrackHelper.run()

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
        do_continue = s.find_targets()
        targets = s.select_targets()

        if Configuration.infinite_mode:
            while do_continue:
                AttackAll.attack_multiple(targets)
                do_continue = s.update_targets()
                if not do_continue:
                    break
                targets = s.select_targets()
            attacked_targets = s.get_num_attacked()
        else:
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


if __name__ == '__main__': #It Allows You to Execute Code When the File Runs as a Script, but Not When It’s Imported as a Module
    entry_point()
