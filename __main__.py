#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Files named __init__.py are used to mark directories on disk as Python package directories. If remove the __init__.py file, Python will no longer look for submodules inside that directory, so attempts to import the module will fail.
#  __main__.py run file directly from command line
# try:
#     from .config import Configuration
# except (ValueError, ImportError) as e:
#     raise Exception(
#         "You may need to run wifite from the root directory (which includes README.md)", e) from e

from util.color import Color
from config import Configuration

import os
import subprocess


class Wifite(object):

    def __init__(self):  # Constructors is to initialize(assign values) to the data members of the class when an object of the class is created
                         # self represents the instance of the class. By using the “self”  we can access the attributes and methods of the class in python.
        """
        Initializes Wifite.
        Checks that its running under *nix, with root permissions and ensures dependencies are installed.
        """

        self.print_banner()  # Print tool's banner

        Configuration.initialize(load_interface=False)

        if os.name == 'nt':
            Color.pl(
                '{!} {R}error: {O}wifite{R} must be run under a {O}*NIX{W}{R} like OS')
            Configuration.exit_gracefully(0)
        if os.getuid() != 0:
            Color.pl('{!} {R}error: {O}wifite{R} must be run as {O}root{W}')
            Color.pl('{!} {R}re-run with {O}sudo{W}')
            Configuration.exit_gracefully(0)

        from .tools.dependency import Dependency
        Dependency.run_dependency_check()
        
    @staticmethod
    def print_banner():
        Color.pl(r""" {W}
                  .::::::::.                    
             :=+#%@@@@@@@@@@@@@@%#+=.             
         :=#@@@@@@@@@%#####%%@@@@@@@@@#=:         
      :*@@@@@@%+=:.            .:=+%@@@@@@*:      
    =%@@@@%+:       .:::--:::.       :+%@@@@%=    
   =@@@@+.     -+#%@@@@@@@@@@@@%#+-     .+@@@@=   
     +=    .=%@@@@@@@%######%@@@@@@@%=.    =+     
         -#@@@@@*=:            :=*@@@@@#-         
         +@@@*:      :------:      :*@@@+         
           =    .=*@@@@@@@@@@@@*=.    -           
              :#@@@@@@#****#@@@@@@#:              
               +@@*-          -*@@+                                                                            """)
        Color.pl(r"""{R}                      .====:             
                            .%@#==#@%.                                                                                 """)
        Color.pl(
            r"""{R}                    %@-    -=        ___       __    ________     _______   ________      """)
        Color.pl(
            r"""{R}                 :==@@*=========:   {W}|{R}\  \     {W}|{R}\  \ {W}|{R}\   __  \   /  ___  \ {W}|{R}\   ____\     """)
        Color.pl(r"""{R}                 =@@@@@@@@@@@@@@=   {W}\ {R}\  \    {W}\ {R}\  \{W}\ {R}\  \{W}|{R}\  \ /__/{W}|_{R}/  /{W}|\ {R}\  \{W}___|     """)
        Color.pl(r"""{R}                 =@@@@@@==@@@@@@=   {W} \ {R}\  \  __{W}\ {R}\  \{W}\ {R}\   ____\{W}|__|/{R}/  / {W}/ \ {R}\  \        """)
        Color.pl(r"""{R}                 =@@@@@@:.@@@@@@=   {W}  \ {R}\  \{W}|{R}\__\_\  \{W}\{R} \  \{W}___|    {R}/  /{W}_/{R}__ {W}\ {R}\  \____   """)
        Color.pl(
            r"""{R}                 =@@@@@@..@@@@@@=   {W}   \ {R}\____________\{W}\ {R}\__\      |\________\{W}\ {R}\_______\ """)
        Color.pl(
            r"""{R}                 =@@@@@@==@@@@@@=   {W}    \|____________| \|__|       \|_______| \|_______| """)
        Color.pl(
            r"""{R}                 =@@@@@@@@@@@@@@=                                           {O} By Jason Teo """)
        Color.pl("-----------------------------------------------------------------------------------------")
        
    def start(self):
        """
        Starts target-scan + attack loop, or launches utilities depending on user input.
        """
        from .model.result import CrackResult
        from .model.handshake import Handshake
        from .util.crack import CrackHelper

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


def entry_point():
    try:
        wifite = Wifite()
        wifite.start()
    except Exception as e:
        Color.pexception(e)
        Color.pl('\n{!} {R}Exiting{W}\n')

    except KeyboardInterrupt:
        Color.pl('\n{!} {O}Interrupted, Shutting down...{W}')


if __name__ == '__main__':  # It Allows You to Execute Code When the File Runs as a Script, but Not When It’s Imported as a Module
    entry_point()
