#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tools.password as password
import random
import string


def generate_password(password, length):
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
    if len(password) < length:
        # Use the sample function to randomly select 'length' characters from the list
        additional_characters = ''.join(
            random.sample(characters, length - len(password)))

        # Concatenate the user's password and the additional characters
        password = password + additional_characters

    # If the password is longer than the desired length, truncate it
    elif len(password) > length:
        password = password[:length]

    # Modify the password to make it more unpredictable
    modified_password = ""
    for c in password:
        # 90% chance of replacing the character with a visually similar character
        if random.random() < 0.9 and c in similar_characters:
            modified_password += random.choice(similar_characters[c])
        # 50% chance of changing the case of the character
        elif random.random() < 0.5:
            modified_password += c.upper()
        # 50% chance of leaving the character unchanged
        else:
            modified_password += c

    return modified_password


def main():
    # Prompt the user to enter their desired password
    user_password = input("Enter your desired password or passphrase: ")

    # Prompt the user to enter the desired password length
    while True:
        try:
            password_length = int(input("Enter the desired password length: "))
            if password_length > 90:
                print("Please enter a value less than 90")
                continue
            break
        except ValueError:
            print("The password length must be an integer.")
            continue

    # Hashes/second to MH/s
    print(
        "Based on password cracking at: {:,d} MH/s.\n".format(int(20000000000 / 1000000)))

    # Generate and print 5 different passwords for the user to choose from
    passwords = []
    for i in range(5):
        password = generate_password(user_password, password_length)
        passwords.append(password)
        print(f"Option {i+1}: {password}")

        # Check the password strength
        password.passwd_gen_chk(password)

    # Prompt the user to choose a password
    while True:
        try:
            choice = int(input("Enter the number of the password you want to use: "))
            if choice < 1 or choice > 5:
                print("Please choose a number between 1 and 5.")
            else:
                break
        except ValueError:
            print("Please enter a valid number.")

    # Print the chosen password
    print(f"You have chosen the following password: {passwords[choice-1]}")
    password.passwd_gen_chk(passwords[choice - 1])
