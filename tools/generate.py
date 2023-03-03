#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tools.password import Password
from util.color import Color
from config import Configuration
import subprocess
import random
import string

try:
    from zxcvbn import zxcvbn
except ModuleNotFoundError:
    Color.pl('{!} {R}zxcvbn{O} module not found. Installing it now...{W}\n')
    subprocess.run(['pip', 'install', 'zxcvbn'])
    Color.pl('\n{!} {O}Rerun the {R}WP2C.py {O}with {R}--password {O} argument again after the {R}zxcvbn {O}module installation is complete.{W}')
    Configuration.exit_gracefully()


class Generate():
    
    @classmethod
    def run(cls):
        
        cls.result = None # To store new generated password for tested
        
        # Prompt the user to enter their desired password
        Color.pl('\n{W}----------------------------------{G} Password Generater {W}-----------------------------------\n')
        Color.p('{?} Do you want to {G}create new password(c) {W}or {G}modify existing password(m) {W}? ({G}c{W}/{R}m{W}):{C} ')
        choosen_ans = input()
        if choosen_ans == 'c' or choosen_ans == 'C': # Create new password
            Color.p('{?} {W}Do you want to create new password {G}randomly suggested by WP2C(r) {W}or {G}tailor made(t){W}? ({G}r{W}/{R}t{W}):{C} ')
            method_ans = input()
            
            if method_ans == 'r' or method_ans == 'R': # Randomly suggested by WP2C
                # prompt the user to choose between generating a password or passphrase
                Color.p('{?} {W}Do you want to generate a {G}password(w) {W}or a {G}passphrase(p){W}? ({G}w{W}/{R}p{W}):{C} ')
                choice = input()

                ''' Generate a password '''
                if choice == 'w' or choice == 'W':
                    # prompt the user for the length of the password and the number of letters, digits, and symbols to include
                    Color.p('{?} {W}Enter the length of the password:{C} ')
                    length = int(input())
                    
                    if length < 7:
                        Color.pl('{!} {R}Error: {O}The password length should not less than 8, set password length to {C}default [8]{W}.')
                        length = 8 
                    remain = length    
                    while remain > 1:
                        Color.p('{?} {W}Enter the number of letters (up to {G}%s{W}):{C} ' % remain)
                        while True:
                            num_letters = int(input())
                            if num_letters <= remain:
                                break
                            Color.pl('{!} {R}Error: You can only input up to {G}%s {O}letters. Please try again.{W}' % remain)
                            Color.p('{?} {W}Enter the number of letters (up to {G}%s{W}):{C} ' % remain)
                        remain -= num_letters
                        Color.pl('{+} {W}The remaining password length is {C}%s{W}.' % remain)
                        
                        if remain < 1:
                            num_digits = 0
                            num_symbols = 0
                            Color.pl('{!} {O}No more space for digits! Number of digits set to {G}0{W}.')
                            Color.pl('{!} {O}No more space for symbols! Number of symbols set to {G}0{W}.')
                            break
                        Color.p('{?} {W}Enter the number of digits (up to {G}%s{W}):{C} ' % remain)
                        
                        while True:
                            num_digits = int(input())
                            if num_digits <= remain:
                                break
                            Color.pl('{!} {R}Error: {O}You can only input up to {G}%s {O}digits. Please try again.{W}' % remain)
                            Color.p('{?} {W}Enter the number of digits (up to {G}%s{W}):{C} ' % remain)
                        remain -= num_digits
                        Color.pl('{+} {W}The remaining password length is {C}%s{W}.' % remain)
                        
                        if remain < 1:
                            num_symbols = 0
                            Color.pl('{!} {O}No more space for symbols! Number of symbols set to {G}0{W}.')
                            break
                        Color.p('{?} {W}Enter the number of symbols (up to {G}%s{W}):{C} ' % remain)
                        
                        while True:
                            num_symbols = int(input())
                            if num_symbols <= remain:
                                break
                            Color.pl('{!} {R}Error: You can only input up to {G}%s {O}symbols. Please try again.{W}' % remain)
                            Color.p('{?} {W}Enter the number of symbols (up to {G}%s{W}):{C} ' % remain)
                        remain -= num_symbols
                        Color.pl('{+} {W}The remaining password length is {C}%s{W}.' % remain)
                        break

                    # generate the password and print it to the console
                    passwd = Generate.random_password(length, num_letters, num_digits, num_symbols)
                    Color.pl('{+} Your new password is:{C} ' + passwd)
                    cls.result = passwd
                    
                    ''' Generate a passphrase'''    
                elif choice == 'p' or choice == 'P':
                    # prompt the user for the the number of words to include
                    Color.p('{+} {W}Enter the number of words in the passphrase:{C} ')
                    num_words = int(input())
                    # generate the passphrase and print it to the console
                    passphrase = Generate.random_passphrase(num_words)
                    Color.pl('{+} Your new passphrase is:{C} ' + passphrase)
                    cls.result = passphrase
                    
                else: # Invalid option
                    Color.pl('{!} {R}Error: {O}Invalid option. Try again.{W}')
                    Generate.run()
                    
            elif method_ans == 't' or method_ans == 'T': # Tailor made
                Color.p(('{+} {W}Enter your {G}desired word {W}to add in password:{C} '))
                user_passwd = input()
                
                # Prompt the user to enter the desired password length
                while True:
                    try:
                        Color.p(('{+} {W}Enter the desired password length:{C} '))
                        passwd_length = int(input())
                        if passwd_length < 7 or passwd_length > 20:
                            Color.pl('{!} {R}Error: {O}Please enter a value between 8 to 20.{W}')
                            continue
                        break
                    except ValueError:
                        Color.pl('{!} {R}Error: {O}The password length must be an integer.{W}')
                        continue
                Generate.print_tailor_passwords(user_passwd, passwd_length)
                
            else: # Invalid option
                Color.pl('{!} {R}Error: {O}Invalid option. Try again.{W}')
                Generate.run()
                
        elif choosen_ans == 'm' or choosen_ans == 'M': # Modify existing password
            Color.p(('{+} {W}Enter your {G}current password {W}to be modify:{C} '))
            user_passwd = input()
            passwd_length = len(user_passwd)
            Generate.print_tailor_passwords(user_passwd, passwd_length)
            
        else: # Invalid option
            Color.pl('{!} {R}Error: {O}Invalid option. Try again.{W}')
            Generate.run()
            
        # Exit the program
        Color.pl('{W}------------------------------------- {G}Thank You {W}-----------------------------------------') 
        Configuration.exit_gracefully()

    @staticmethod
    def print_tailor_passwords(user_passwd, passwd_length):
        # Generate and print 3 different passwords for the user to choose from
        passwds = []
        count = 0
        Color.pl('{+} {W}Generating password...')
        Color.pl('{+} {W}Modify {G}desired word {W}or {G}current password {W}if waiting too long...')
        while count < 3:
            passwd = Generate.tailor_password(user_passwd, passwd_length)
            strength = zxcvbn(passwd)
            if strength['score'] < 3: # Check the password strength
                continue
            else:
                passwds.append(passwd)
                count += 1
        for i in range(count):
            Color.pl(f'\n{{G}}Option {i+1} {{W}}--------------------------------------------------------------------------------')
            Color.pl('{+} Password : {C}%s{W}' % passwds[i])

        # Prompt the user to choose a password
        while True:
            try:
                Color.p(('{+} {W}Enter the number of the password you want to use:{C} '))
                choice = int(input())
                if choice < 1 or choice > 3:
                    Color.pl('{+} {W}Please choose a number between {G}1 {W}and {G}3{W}.')
                else:
                    break
            except ValueError:
                Color.pl('{!} {R}Error: {O}Please enter a valid number.{W}')

        # Print the chosen password
        Color.pl('\n{W}----------------------------------- {G}Password Choosen {W}------------------------------------')
        Color.pl(f'{{+}} You have chosen the following password: {{G}}{passwds[choice-1]}{{W}}')
        result = passwds[choice-1]
        Generate.check_strength(result)
        
    # Check the strength of the password
    @staticmethod
    def check_strength(result):
        Password.check_password(result, 'no') # zxcvbn
        
        count = Password.pwned_api_check(result) # pwned
        if count:
            Color.pl(f'\n{{!}} {{R}}{result} {{O}}was found to be leaked {{R}}{count} {{O}}times.  It is time to change it!{{W}}\n\n')
        else:
            Color.pl(f'\n{{+}} {{R}}{result} {{O}}was not found to be leaked. Carry on!{{W}}')
    
    @staticmethod    
    def tailor_password(passwd, length):
        # List of characters to choose from
        characters = string.ascii_letters + string.digits + string.punctuation

        # List of visually similar of all characters
        similar_characters = {
            '1': 'lI',
            '2': 'zZ',
            '3': 'E',
            '4': 'Aa',
            '5': 'S',
            '6': 'bGg',
            '7': 'L',
            '8': 'B',
            '9': 'gq',
            '0': 'OoDd',
            'a': 'A@',
            'b': 'B6',
            'c': 'C(',
            'd': 'D',
            'e': 'E3',
            'f': 'F',
            'g': 'G6',
            'h': 'H',
            'i': 'I1!',
            'j': 'J',
            'k': 'K',
            'l': 'L1|7',
            'm': 'M',
            'n': 'N',
            'o': 'O0',
            'p': 'P',
            'q': 'Q9',
            'r': 'R',
            's': 'S5$',
            't': 'T+',
            'u': 'U',
            'v': 'V',
            'w': 'W',
            'x': 'X',
            'y': 'Y',
            'z': 'Z2',
            '!': 'iI1',
            '@': 'aA',
            '#': '3E',
            '$': 'sS5',
            '%': 'xX',
            '^': '6Gg',
            '&': '8B',
            '*': 'oO0',
            '(': 'cC',
            ')': 'cC',
            '+': 'tT',
            '-': '7L',
            '_': '7L',
            '=': '0Oo',
            '{': 'cC(',
            '}': 'cC)',
            '[': 'cC(',
            ']': 'cC)',
            '\\': '1|',
            '|': '1lL',
            ';': '3E',
            ':': '3E',
            '\'': 'iI1',
            '"': 'iI1',
            '<': 'cC(',
            '>': 'cC)',
            ',': 'mM',
            '.': 'mM',
            '/': '7L',
            '?': '7L',
        }

        # If the password is shorter than the desired length, generate additional characters
        if len(passwd) < length:
            # Use the sample function to randomly select 'length' characters from the list
            additional_characters = ''.join(
                random.sample(characters, length - len(passwd)))

            # Concatenate the user's password and the additional characters
            passwd = passwd + additional_characters

        # If the password is longer than the desired length, truncate it
        elif len(passwd) > length:
            passwd = passwd[:length]

        # Modify the password to make it more unpredictable
        modified_passwd = ''
        for c in passwd:
            # 90% chance of replacing the character with a visually similar character
            if random.random() < 1.0 and c in similar_characters:
                modified_passwd += random.choice(similar_characters[c])
            # 50% chance of changing the case of the character
            elif random.random() < 0.5:
                modified_passwd += c.upper()
            # 50% chance of leaving the character unchanged
            else:
                modified_passwd += c

        return modified_passwd

    @staticmethod
    def random_password(length, num_letters, num_digits, num_symbols):
        # select num_letters random letters from string.ascii_letters
        letters = random.sample(string.ascii_letters, num_letters)
        # select num_digits random digits from string.digits
        digits = random.sample(string.digits, num_digits)
        # select num_symbols random symbols from string.punctuation
        symbols = random.sample(string.punctuation, num_symbols)
        # create a list of all the characters to include in the password
        characters = letters + digits + symbols
        # if there are more characters required than the sum of letters, digits and symbols
        # then add remaining number of random characters from the pool of possible characters
        if length > num_letters + num_digits + num_symbols:
            Color.pl('{+} {W}The remaining password length will be {G}auto completed{W} by {G}random character(s){W}.')
            remaining = length - num_letters - num_digits - num_symbols
            characters += random.sample(string.ascii_letters + string.digits + string.punctuation, remaining)
        # shuffle the list of characters to randomize their order
        random.shuffle(characters)
        # join the shuffled characters to generate the password
        passwd = ''.join(characters)
        return passwd
    
    @staticmethod
    def random_passphrase(num_words):
        # read a list of words from the file specified in Configuration.passphrases
        with open(Configuration.passphrases, 'r') as f:
            word_list = [line.strip() for line in f]
        # generate the passphrase by randomly selecting words from the list of words
        passphrase = ' '.join(random.choice(word_list) for i in range(num_words))
        return passphrase




