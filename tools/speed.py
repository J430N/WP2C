#!/usr/bin/env python
# -*- coding: utf-8 -*-

from util.color import Color
from config import Configuration
import subprocess
    
try:
    import speedtest
except ImportError:
    Color.pl('{!} {R}speedtest-cli{O} library not found. Installing it now...{W}\n')
    subprocess.run(['pip', 'install', 'speedtest-cli'])
    Color.pl('\n{!} {O}Rerun the {R}WP2C.py {O}with {R}--speed {O} argument again after the {R}speedtest-cli {O}library installation is complete.{W}')
    Configuration.exit_gracefully(0)

#Add colour and + symbol to the output
# Display the processing percentages

class Speed():

    @classmethod
    def run(self):
        # Create a Speedtest object
        test = speedtest.Speedtest(secure=True)

        # Get the list of servers and choose the best one
        print('Loading server list...')
        test.get_servers()
        print('Choosing best server...')
        best = test.get_best_server()

        print(f'Found: {best["host"]} located in {best["country"]}')

        # Perform the download and upload tests
        print('Performing download test...')
        download_result = test.download()
        print('Performing upload test...')
        upload_result = test.upload()
        ping_result = test.results.ping

        # Print the results
        print(f'Download speed: {download_result / 1024 / 1024:.2f}Mbit/s')
        print(f'Upload speed: {upload_result / 1024 / 1024:.2f}Mbit/s')
        print(f'Ping: {ping_result}ms')