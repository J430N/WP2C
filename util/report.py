#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Developer Name: Mr. Jason Teo Jie Chen
# Program Name: report.py
# Description: Generate a PDF report after cracking a Wi-Fi network
# First Written On: 18 March 2023
# Edited On: 24 March 2023 

import json
import time
import os
import requests
import hashlib
from util.color import Color
from config import Configuration
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from zxcvbn import zxcvbn

class Report:
    
    def run(essid):
        # Load the Wi-Fi data from the JSON file
        with open(Configuration.cracked_file, 'r') as f:
            cracked_data_list = json.load(f)

        # Find the latest Wi-Fi network data with the same ESSID
        cracked_data = None
        for data in reversed(cracked_data_list):
            if data['essid'] == essid:
                cracked_data = data
                break

        if cracked_data is None:
            raise ValueError("ESSID '{}' not found in cracked data file.".format(essid))

        # Set the PDF filename based on the Wi-Fi name
        wifi_name = cracked_data['essid'].replace('@', '_')
        pdf_filename = 'report/{}_report.pdf'.format(wifi_name)

        # Check if the file already exists, and append (1) to the filename if it does
        if os.path.isfile(pdf_filename):
            i = 1
            while os.path.isfile(pdf_filename[:-4] + f"({i}).pdf"):
                i += 1
            pdf_filename = pdf_filename[:-4] + f"({i}).pdf"
            
        # Create a new PDF file
        c = canvas.Canvas(pdf_filename, pagesize=letter)
        
        # Set the font
        c.setFont('Helvetica-Bold', 16)

        # Write the title
        title_text = 'WP2C Wi-Fi Network Security Report'
        title_width = c.stringWidth(title_text)
        c.drawString((letter[0] - title_width) / 2, 750, title_text)

        # Write the generated on date
        c.setFont('Helvetica', 10)
        generated_on_text = 'Report Generated on: {}'.format(time.strftime('%Y-%m-%d %H:%M:%S'))
        generated_on_width = c.stringWidth(generated_on_text)
        c.drawString((letter[0] - generated_on_width) / 2, 730, generated_on_text)


        # Draw a line under the title
        c.line(50, 720, letter[0] - 50, 720)

        # Set the font size for the rest of the document
        c.setFont('Helvetica', 10)

        # Write the network information
        c.drawString(50, 690, 'Network Name:')
        c.drawString(220, 690, cracked_data['essid'])

        c.drawString(50, 670, 'Mac Address:')
        c.drawString(220, 670, cracked_data['bssid'])

        c.drawString(50, 650, 'Encryption:')
        c.drawString(220, 650, cracked_data['type'])

        c.drawString(50, 630, 'Password:')
        c.drawString(220, 630, cracked_data['key'])

        c.drawString(50, 610, 'Handshake Captured Date and Time:')
        datetime_str = cracked_data['handshake_file'].split("_")[-1].split(".")[0]  # Extract "2023-03-09T13-33-01"
        time_obj = time.strptime(datetime_str, "%Y-%m-%dT%H-%M-%S")  # Parse string into time object
        date_str = time.strftime("%Y-%m-%d", time_obj)  # Convert time object to date string
        time_str = time.strftime("%H:%M:%S", time_obj)  # Convert time object to time string

        c.drawString(220, 610, date_str + ' ' + time_str)
        
        c.drawString(50, 590, 'Password Cracked Date and Time:')
        date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(cracked_data['date']))
        c.drawString(220, 590, date)

        # Draw a line under the Wi-Fi network information section
        c.line(50, 570, letter[0] - 50, 570)


        '''Password Vulnerabilities'''
        # Write the Wi-Fi network vulnerabilities section
        c.setFont('Helvetica-Bold', 12)
        c.drawString(50, 540, 'Password Vulnerabilities:')
        c.setFont('Helvetica', 10)

        # Check password strength score
        SCORE_TO_WORD = {
            0: 'Very weak',
            1: 'Very weak',
            2: 'Weak',
            3: 'Medium',
            4: 'Strong',
        }
        
        password_strength = zxcvbn(cracked_data['key'])
        c.drawString(50, 520, '{}. Password Strength: {}/4)'.format('1', SCORE_TO_WORD[password_strength['score']] + ' (' + str(password_strength['score'])))
        
        # Shows the estimated number of guesses and estimated time
        c.drawString(50, 500, '{}. Estimated number needed to guess the password: {}'.format('2', round(password_strength['guesses'])))
        c.drawString(50, 480, '{}. Estimated time needed to guess the password (offline fast hashing with many processors): {}'.format('3', password_strength['crack_times_display']['offline_fast_hashing_1e10_per_second']))
        c.drawString(50, 460, '{}. Estimated time needed to guess the password (offline slow hashing with many processors): {}'.format('4', password_strength['crack_times_display']['offline_slow_hashing_1e4_per_second']))
        c.drawString(50, 440, '{}. Estimated time needed to guess the password (online attack without throttling): {}'.format('5', password_strength['crack_times_display']['online_no_throttling_10_per_second']))
        c.drawString(50, 420, '{}. Estimated time needed to guess the password (online attack with throttling): {}'.format('6', password_strength['crack_times_display']['online_throttling_100_per_hour']))


        '''Password Exposure'''    
        c.setFont('Helvetica-Bold', 12)
        c.drawString(50, 390, 'Password Exposure:')
        c.setFont('Helvetica', 10)

        # Check password exposure using zxcvbn module
        num = 1
        no_matches_found = True
        for exposed in password_strength['sequence']:
            try:
                c.drawString(50, 390-num*20, 'zxcvbn: {} found in {} at position {}. '.format(exposed['matched_word'], exposed['dictionary_name'], str(exposed['rank'])))
                num += 1
                no_matches_found = False
            except KeyError:
                pass  # No match found
        if no_matches_found:
            c.drawString(50, 390-num*20, 'zxcvbn: No matches found.')
            num += 1

        # Check password exposure using WP2C dictionary
        matches = []
        position = 0
        
        # Load the dictionaries and add them to zxcvbn
        dict_wordlists = {}
        # Default location dictionaries (defined in the config file)
        for file_path in Configuration.wordlists:
            with open(file_path, 'r') as f:
                list_actual_dict = f.read().split('\n')
            file_name = os.path.basename(file_path) # Remove the file path
            dict_wordlists[os.path.splitext(file_name)[0]] = list_actual_dict # Remove file extension and add to dict as key
        
        for key, values in dict_wordlists.items():
            for value in values:
                position += 1
                if cracked_data['key'] in value:
                    matches.append((value, key, position))

        if len(matches) > 0:
            for match in matches:
                c.drawString(50, 390-num*20, 'WP2C: {} found in {} at position {}. '.format(match[0], match[1], str(match[2])))
                num += 1
        else:
            c.drawString(50, 390-num*20, 'WP2C: No matches found.')
            num += 1

        # Check password exposure using Have I Been Pwned API
        count = Report.pwned_api_check(cracked_data['key']) # pwned
        if count:
            c.drawString(50, 390-num*20, 'Have I Been Pwned: %s was found to be leaked %s times.  It is time to change it!' % (cracked_data['key'], count))
            num += 1
        else:
            c.drawString(50, 390-num*20, 'Have I Been Pwned: %s was not found to be leaked. Carry on!' % cracked_data['key'])
            num += 1
        
        '''Comments and Recommendations for Weak Password'''
        # Feedback
        no_feedback = True
        c.setFont('Helvetica-Bold', 12)
        c.drawString(50, 390-num*20-10, 'Comments and Recommendations for Weak Password:')
        idx = 1
        num += 1
        c.setFont('Helvetica', 10)
        if password_strength['feedback']['warning'] != '':
            no_feedback = False
            c.drawString(50, 390-num*20-10, '{}. {}'.format(idx, password_strength['feedback']['warning']))
            idx += 1
            num += 1
        for x in password_strength['feedback']['suggestions']:
            no_feedback = False
            c.drawString(50, 390-num*20-10, '{}. {}'.format(idx, x))
            idx += 1
            num += 1
        if no_feedback:
            c.drawString(50, 390-num*20-10, 'None')
            idx += 1
            num += 1
        
        # Add a page break
        c.showPage()
        
        
        '''Recommendations to Avoid WPA Vulnerabilities'''
        # Add WPA vulnerabilities recommendations
        c.setFont('Helvetica-Bold', 12)
        c.drawString(50, 750, 'Recommendations to Avoid WPA Vulnerabilities:')

        bullets = [
            'Use WPA3 instead of WPA2',
            'Use a strong, unique password for your Wi-Fi network',
            'Regularly update the firmware of your Wi-Fi router',
            'Disable WPS (Wi-Fi Protected Setup)',
            'Disable legacy Wi-Fi protocols (e.g. 802.11b)',
            'Avoid using dictionary words in your password',
            'Use a combination of uppercase and lowercase letters, numbers, and symbols',
            'Use a longer password, at least 12 characters',
            'Change your password regularly',
            'Consider using a password manager to generate and store strong passwords',
            'Use WPA3 or WPA2 with AES encryption instead of WEP, which is vulnerable to attacks'
        ]

        y = 720
        c.setFont('Helvetica', 10)
        for i, bullet in enumerate(bullets):
            c.drawString(50, y, "{}. {}".format(i+1, bullet))
            y -= 20


        # Save the PDF file
        c.save()
        Color.pl(f'{{+}} Report saved to {{G}}{pdf_filename}{{W}}')

    @staticmethod
    def request_api_data(hash_char):
        # fetches data from the url and stores it in res
        res = requests.get('https://api.pwnedpasswords.com/range/'+hash_char)
        if res.status_code != 200:
            raise RuntimeError(
                f'error fetching: {res.status_code}, check the API and try again.')
        return res

    @staticmethod
    def password_leak_count(hashes, hash_to_check):
        # sepetares the hash and count
        hashes = (line.split(':') for line in hashes.text.splitlines())
        for h, count in hashes:  # h stores the hash and count stores the number of times it's been cracked
            if h == hash_to_check:
                return count
        return 0

    @staticmethod
    def pwned_api_check(passwd):
        # encodes the password in sha1 hash
        sha1password = hashlib.sha1(passwd.encode('utf-8')).hexdigest().upper()
        first5_chars, rest = sha1password[:5], sha1password[5:]
        # passes the first five chars in the funct and receives matching responses
        try:
            response = Report.request_api_data(first5_chars)
            return Report.password_leak_count(response, rest)
        except:
            pass