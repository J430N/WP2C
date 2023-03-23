#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Developer Name: Mr. Jason Teo Jie Chen
# Program Name: password.py
# Description: Test user's password strength
# First Written On: 3 March 2023
# Edited On: 23 March 2023

import os
import requests
import hashlib
from getpass import getpass
from config import Configuration
from util.color import Color
from zxcvbn import zxcvbn
from zxcvbn.matching import add_frequency_lists


# Lowercase alphabet.
ALPHA_MIN = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l',
             'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
# Capital alphabet.
ALPHA_MAJ = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
             'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
# Numbers.
NUMBERS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
# Special characters.
CARACTS_SPE = ['&', '~', ''', '#', ''', '{', '(', '[', '-', '|', '`', '_', '^',
               '@', ')', ']', '°', '+', '=', '}', '¨', '£', '$', '¤', '%', 'µ',
               '*', '!', '§', ':', ';', '.', ',', '?']

# Convert score from zxcvbn to word.
SCORE_TO_WORD = {
    0: 'Very weak',
    1: 'Very weak',
    2: 'Weak',
    3: 'Medium',
    4: 'Strong',
}

class Password:
    
    def run():
        Color.pl('{W}-------------------------------{G} Password Strength Checker {W}-------------------------------\n')
        Color.p('{?} Do you want to {G}hide {W}your password while typing? ({G}y{W}/{R}n{W}):{C} ')
        ans = input()
        if ans == 'y' or ans == 'Y':
            Color.p('{?} {W}Enter your password to be checked: ')
            passwd = getpass('') 
            Color.p('\n')
        elif ans == 'n' or ans == 'N':
            Color.p(('{?} {W}Enter your password to be checked:{C} '))
            passwd = input()
            Color.p('\n')
        else:
            Color.pl('{!} {R}Error: {O}Invalid option. Try again.{W}')
            Password.run()

        Password.check_password(passwd, ans) # zxcvbn
        
        count = Password.pwned_api_check(passwd) # pwned
        if count:
            if ans == 'y' or ans == 'Y':
                masked_password = '*' * (len(passwd)-1) + passwd[-1:]
                Color.pl(f'\n{{!}} {{R}}{masked_password} {{O}}was found to be leaked {{R}}{count} {{O}}times.  It is time to change it!{{W}}\n')
            else:
                Color.pl(f'\n{{!}} {{R}}{passwd} {{O}}was found to be leaked {{R}}{count} {{O}}times.  It is time to change it!{{W}}\n')
        else:
            if ans == 'y' or ans == 'Y':
                masked_password = '*' * (len(passwd)-1) + passwd[-1:]
                Color.pl(f'\n{{+}} {{R}}{masked_password} {{O}}was not found to be leaked. Carry on!{{W}}\n')
            else:
                Color.pl(f'\n{{+}} {{R}}{passwd} {{O}}was not found to be leaked. Carry on!{{W}}\n')
        Color.pl('{W}--------------------------------------- {G}Thank You {W}---------------------------------------')
        Configuration.exit_gracefully()
        
    
    @staticmethod    
    def check_password(passwd, ans):
        ''' Evaluates the strength of the password according to several criteria. Powered by zxcvbn. '''

        # Load the dictionaries and add them to zxcvbn
        dict_wordlists = {}
        # Default location dictionaries (defined in the config file)
        for file_path in Configuration.wordlists:
            with open(file_path, 'r') as f:
                list_actual_dict = f.read().split('\n')
            file_name = os.path.basename(file_path) # Remove the file path
            dict_wordlists[os.path.splitext(file_name)[0]] = list_actual_dict # Remove file extension and add to dict as key
        add_frequency_lists(dict_wordlists)

        # Gets the password results with zxcvbn and displays the score
        Color.pl('{+} {G}Result of the password strength check: {W}')
        if not passwd:
            raise SystemExit('ValueError: The password is empty.')
        result = zxcvbn(passwd)
        Color.pl('    {+} ' + SCORE_TO_WORD[result['score']] + ' (' + str(result['score']) + '/4)')

        # Shows the estimated number of guesses
        Color.p('    {+} Estimated number needed to guess the password : ')
        Color.pl(round(result['guesses']))
        
        # Shows the estimated time
        Color.pl('    {+} Estimated time needed to guess the password: ')
        Color.p('        {+} Fast hashing with many processors (1e10/s) : ')
        Color.pl(str(result['crack_times_display']['offline_fast_hashing_1e10_per_second']))
        Color.p('        {+} Slow hashing with many processors (1e4/s)  : ')
        Color.pl(str(result['crack_times_display']['offline_slow_hashing_1e4_per_second']))
        Color.p('        {+} Online attack without throttling (10/s)    : ')
        Color.pl(str(result['crack_times_display']['online_no_throttling_10_per_second']))
        Color.p('        {+} Online attack with throttling (100/h)      : ')
        Color.pl(str(result['crack_times_display']['online_throttling_100_per_hour']))
        
        # Feedback
        no_feedback = True
        num = 1
        Color.pl('\n{+} {G}Comments and recommendations: {W}')
        if result['feedback']['warning'] != '':
            no_feedback = False
            Color.pl('     {W}[{G}%i{W}] ' % num + result['feedback']['warning'])
            num += 1
        for x in result['feedback']['suggestions']:
            no_feedback = False
            Color.pl('     {W}[{G}%i{W}] ' % num + x)
            num += 1
            
        if len(passwd) <= 6:
            no_feedback = False
            Color.pl('     {W}[{G}%i{W}] Your password is much too short. A minimum length of 14 characters is recommended. ' % num)
            num += 1
        elif len(passwd) < 14:
            no_feedback = False
            Color.pl('     {W}[{G}%i{W}] A minimum length of 14 characters is recommended.' % num)
            num += 1
            
        # Dispersion of numbers and special characters
        nb_nums = 0
        nb_cs = 0
        for x in passwd:
            if x in NUMBERS:
                nb_nums += 1
            elif x in CARACTS_SPE:
                nb_cs += 1
        nb_nums_start_end = 0
        nb_cs_start_end = 0
        for x in passwd:
            if x in NUMBERS:
                nb_nums_start_end += 1
            elif x in CARACTS_SPE:
                nb_cs_start_end += 1
            else:
                break
        for x in reversed(passwd):
            if x in NUMBERS:
                nb_nums_start_end += 1
            elif x in CARACTS_SPE:
                nb_cs_start_end += 1
            else:
                break
        if nb_nums_start_end == nb_nums and nb_nums != 0:
            no_feedback = False
            if nb_cs_start_end == nb_cs and nb_cs != 0:
                Color.pl('     {W}[{G}%i{W}] Numbers and special characters are not scattered correctly.' % num)
                num += 1
            else:
                Color.pl('     {W}[{G}%i{W}] The numbers are not dispersed properly.' % num)
                num += 1
        elif nb_cs_start_end == nb_cs and nb_cs != 0:
            no_feedback = False
            Color.pl('     {W}[{G}%i{W}] Special characters are not scattered correctly.' % num)
            num += 1
        if no_feedback:
            Color.pl('     {W}[{G}%i{W}] No comments available.' % num)

        # Exposure in dictionaries
        '''zxcvbn'''
        Color.pl('\n{+} {G}Exposure report:{W}')
        no_matches_found = True
        for exposed in result['sequence']:
            try:
                if ans == 'y' or ans == 'Y':
                    masked_password = '*' * (len(exposed['matched_word'])-1) + exposed['matched_word'][-1:]
                    Color.pl('    {!} {G}zxcvbn : {R}%s {O}found in {R}'% masked_password + exposed['dictionary_name'] + '{O} at position {R}' + str(exposed['rank']) + '{O}.{W}')
                else:
                    Color.pl('    {!} {G}zxcvbn : {R}%s {O}found in {R}'% exposed['matched_word'] + exposed['dictionary_name'] + '{O} at position {R}' + str(exposed['rank']) + '{O}.{W}')
                no_matches_found = False
            except KeyError:
                pass  # No matche found
        if no_matches_found:
            Color.pl('    {+} {G}zxcvbn{W} : No matches found.')
        
        '''WP2C'''
        matches = []
        position = 0
        for key, values in dict_wordlists.items():
            for value in values:
                position += 1
                if passwd in value:
                    matches.append((value, key, position))

        if len(matches) > 0:
            for match in matches:
                if ans == 'y' or ans == 'Y':
                    masked_password = '*' * (len(match[0])-1) + match[0][-1:]
                    Color.pl('    {!} {G}WP2C   : {R}%s {O}found in {R}%s {O}at position {R}%s{O}.' % (masked_password, match[1], match[2]))
                else:
                    Color.pl('    {!} {G}WP2C   : {R}%s {O}found in {R}%s {O}at position {R}%s{O}.' % (match[0], match[1], match[2]))
        else:
            Color.pl('    {+} {G}WP2C{W}   : No matches found.')

        

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
            response = Password.request_api_data(first5_chars)
            return Password.password_leak_count(response, rest)
        except:
            Color.pl('{!} {R}Error: {O}Connection error. Unable to check the new password\'s leaked times. Please check your {R}internet connection {O}and try again.{W}')
            Color.pl('{W}--------------------------------------- {G}Thank You {W}---------------------------------------')
            Configuration.exit_gracefully()