#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Developer Name: Mr. Jason Teo Jie Chen
# Program Name: client.py
# Description: Holds details for a device connected to an Access Point
# First Written On: 18 February 2023
# Edited On: 7 March 2023 

class Client(object):
    """
        Holds details for a 'Client' - a wireless device (e.g. computer)
        that is associated with an Access Point (e.g. router)
    """

    def __init__(self, fields):
        """
            Initializes & stores client info based on fields.
            Args:
                Fields - List of strings
                INDEX KEY
                    0 Station MAC (client's MAC address)
                    1 First time seen,
                    2 Last time seen,
                    3 Power,
                    4 # packets,
                    5 BSSID, (Access Point's MAC address)
                    6 Probed ESSIDs
        """
        self.station = fields[0].strip()
        self.power = int(fields[3].strip())
        self.packets = int(fields[4].strip())
        self.bssid = fields[5].strip()

    def __str__(self):
        """ String representation of a Client """
        result = ''
        for (key, value) in list(self.__dict__.items()):
            result += f'{key}: {str(value)}'
            result += ', '
        return result

