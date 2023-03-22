#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Developer Name: Mr. Jason Teo Jie Chen
# Program Name: speed.py
# Description: GTest Wi-Fi upload and download speed and ping
# First Written On: 1 March 2023
# Edited On: 11 March 2023

import speedtest
import socket
import platform
from util.color import Color


class Speed:

    def run():
        # Create a Speedtest object
        test = speedtest.Speedtest(secure=True)

        # Get the device name and operating system information
        device_name = socket.gethostname()
        os_info = platform.system() + ' ' + platform.release()

        # Print the device name and operating system information
        Color.pl(f'{{+}} {{W}}Testing network speed and ping of the network connected by {{G}}{device_name} {{C}}({os_info}){{W}}...')
        # Get the list of servers and choose the best one
        Color.pl('{+} Loading server list...')
        test.get_servers()
        Color.pl('{+} Choosing best server...')
        best = test.get_best_server()
        Color.pl(f'{{+}} Found: {{G}}{best["host"]} {{W}}located in {{C}}{best["country"]}{{W}}')

        # Perform the download and upload tests
        Color.pl('{+} Performing download test...')
        download_result = test.download()
        download_result_in_Kb = download_result / 1024
        download_result_in_Mb = download_result_in_Kb / 1024

        Color.pl('{+} Performing upload test...')
        upload_result = test.upload()
        upload_result_in_Kb = upload_result / 1024
        upload_result_in_Mb = upload_result_in_Kb / 1024

        ping_result = ("%.2f" % test.results.ping)

        # Color.pl the results
        Color.pl('\n{W}----------------------------------- {G}Speedtest Results {W}-----------------------------------')
        Color.p('{+} Download speed '.ljust(19))
        Color.pl(':{C} %sMb/s' % '{:.2f}'.format(download_result_in_Mb).rjust(1))
        Color.p(f'{{+}} Upload speed '.ljust(19))
        Color.pl(':{C} %sMb/s' % '{:.2f}'.format(upload_result_in_Mb).rjust(1))
        Color.p(f'{{+}} Ping '.ljust(19))
        Color.pl(':{C} %sms' % str(ping_result).rjust(1))
        Color.pl('{W}-------------------------------------- {G}Thank You {W}----------------------------------------') 