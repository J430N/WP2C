#!/usr/bin/env python
# -*- coding: utf-8 -*-

from util.color import Color
from config import Configuration
import subprocess
    
try:
    import speedtest
except ModuleNotFoundError:
    Color.pl('{!} {R}speedtest-cli{O} module not found. Installing it now...{W}\n')
    subprocess.run(['pip', 'install', 'speedtest-cli'])
    Color.pl('\n{!} {O}Rerun the {R}WP2C.py {O}with {R}--speed {O} argument again after the {R}speedtest-cli {O}module installation is complete.{W}')
    Configuration.exit_gracefully()

class Speed:

    def run():
        # Create a Speedtest object
        test = speedtest.Speedtest(secure=True)

        # Get the list of servers and choose the best one
        Color.pl('{+} Loading server list...')
        test.get_servers()
        Color.pl('{+} Choosing best server...')
        best = test.get_best_server()

        # Color.pl(f'{{+}} Found: {{G}}{best["host"]} {{W}}located in {{C}}{best["country"]}{{W}}')

        # Perform the download and upload tests
        Color.pl('{+} Performing download test...')
        download_result = test.download()
        download_result_in_kb = download_result / 1024
        download_result_in_mb = download_result_in_kb / 1024

        Color.pl('{+} Performing upload test...')
        upload_result = test.upload()
        upload_result_in_kb = upload_result / 1024
        upload_result_in_mb = upload_result_in_kb / 1024

        ping_result = ("%.2f" % test.results.ping)

        # Color.pl the results
        Color.pl('\n{W}----------------------------------- {G}Speedtest Results {W}-----------------------------------')
        Color.p('{+} Download speed '.ljust(19))
        Color.pl(':{C} %sMb/s' % '{:.2f}'.format(download_result_in_mb).rjust(1))
        Color.p(f'{{+}} Upload speed '.ljust(19))
        Color.pl(':{C} %sMb/s' % '{:.2f}'.format(upload_result_in_mb).rjust(1))
        Color.p(f'{{+}} Ping '.ljust(19))
        Color.pl(':{C} %sms' % str(ping_result).rjust(1))
        Color.pl('{W}-------------------------------------- {G}Thank You {W}----------------------------------------') 