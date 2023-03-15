#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Developer Name: Mr. Jason Teo Jie Chen
# Program Name: banner.py
# Description: Holds WP2C banner
# First Written On: 18 February 2023
# Edited On: 20 February 2023 

from util.color import Color


def print_banner():
  Color.pl(r''' {W}
                  .::::::::.
             :=+#%@@@@@@@@@@@@@@%#+=
         :=#@@@@@@@@@%#####%%@@@@@@@@@#=:s
      :*@@@@@@%+=:.            .:=+%@@@@@@*:
    =%@@@@%+:       .:::--:::.       :+%@@@@%=
   =@@@@+.     -+#%@@@@@@@@@@@@%#+-     .+@@@@=
     +=    .=%@@@@@@@%######%@@@@@@@%=.    =+
         -#@@@@@*=:            :=*@@@@@#-
         +@@@*:      :------:      :*@@@+
           =    .=*@@@@@@@@@@@@*=.
              :#@@@@@@#****#@@@@@@#:
               +@@*-          -*@@+ ''')            
  Color.pl(r'''{R}                      .====: ''')
  Color.pl(r'''{R}                    .%@#==#@% ''')
  Color.pl(r'''{R}                    %@-    -=        ___       __    ________     _______   ________ ''')                                                            
  Color.pl(r'''{R}                 :==@@*=========:   {W}|{R}\  \     {W}|{R}\  \ {W}|{R}\   __  \   /  ___  \ {W}|{R}\   ____\ ''')  
  Color.pl(r'''{R}                 =@@@@@@@@@@@@@@=   {W}\ {R}\  \    {W}\ {R}\  \{W}\ {R}\  \{W}|{R}\  \ /__/{W}|_{R}/  /{W}|\ {R}\  \{W}___| ''') 
  Color.pl(r'''{R}                 =@@@@@@==@@@@@@=   {W} \ {R}\  \  __{W}\ {R}\  \{W}\ {R}\   ____\{W}|__|/{R}/  / {W}/ \ {R}\  \        ''')        
  Color.pl(r'''{R}                 =@@@@@@:.@@@@@@=   {W}  \ {R}\  \{W}|{R}\__\_\  \{W}\{R} \  \{W}___|    {R}/  /{W}_/{R}__ {W}\ {R}\  \____ ''')   
  Color.pl(r'''{R}                 =@@@@@@..@@@@@@=   {W}   \ {R}\____________\{W}\ {R}\__\      |\________\{W}\ {R}\_______\ ''')     
  Color.pl(r'''{R}                 =@@@@@@==@@@@@@=   {W}    \|____________| \|__|       \|_______| \|_______| ''')  
  Color.pl(r'{R}                 =@@@@@@@@@@@@@@=                                            {G}Version: {C}1.0{W}''')   
  Color.pl('                                                                            {G} By {C}Jason Teo ')     
  Color.pl('{GR}{D}-----------------------------------------------------------------------------------------{W}')                     
  Color.pl('{!} {R}Disclaimer: {W}WP2C is developeed for testing and discovering {C}WPA encryption {W}\n\t\t vulnerabilities in wireless networks as well as providing feedbacks to fix them. \n\t\t {R}Do not use it for illegal purposes.{W}\n')
