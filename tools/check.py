from __future__ import division
from getpass import getpass
import sys
import re
from datetime import timedelta


def get_policy_counts(password):
    policies = {'Uppercase characters': 0,
                'Lowercase characters': 0,
                'Special characters': 0,
                'Numbers': 0}

    for char in password:
        if re.match("[0-9]", char):
            policies["Numbers"] += 1

        elif re.match("[a-z]", char):
            policies["Lowercase characters"] += 1

        elif re.match("[A-Z]", char):
            policies["Uppercase characters"] += 1

        else:
            policies["Special characters"] += 1

    return policies


def print_policy_counts(policies):
    for policy in policies.keys():
        # Handle missing policies
        num = policies[policy] if policies[policy] > 0 else '-'
        print("[+] %-25s %s" % (policy + ":", str(num)))


def get_password_entropy(policies, entropies):
    entropy = 0
    for policy in policies.keys():
        if policies[policy] > 0:
            entropy += entropies[policy]
    return entropy


def get_cracking_time(entropy, pass_len, crack_speed):
    # Calculate time to crack password in seconds
    crack_time = ((entropy**pass_len) / crack_speed)

    # Convert cracking time to human-readable format
    time_ = "seconds"
    strength_level = "weak"
    if crack_time > 60:
        crack_time = crack_time / 60
        time_ = "minutes"
    if crack_time > 60:
        crack_time = crack_time / 60
        time_ = "hours"
    if crack_time > 24:
        crack_time = crack_time / 24
        time_ = "days"
    if crack_time > 365:
        crack_time = crack_time / 365
        time_ = "years"
        strength_level = "medium"
    if time_ == "years" and crack_time > 100:
        crack_time = crack_time / 100
        time_ = "centuries"
        strength_level = "strong"
    if time_ == "centuries" and crack_time > 1000:
        crack_time = crack_time / 1000
        time_ = "millennia"

    return crack_time, time_, strength_level


def print_cracking_time(crack_time, time_, strength_level):
    print("\n[+] Time to crack password:   {:,.2f} {}".format(crack_time, time_))

    if strength_level == "strong":
        print("\n[+] This password is strong and should provide good protection against cracking attempts.")
    elif strength_level == "medium":
        print("\n[!] Warning: This password is medium strength and may be at risk of being cracked. Consider using a stronger password.")
    else:
        print("\n[!] Warning: This password is weak and may be at risk of being cracked. Consider using a stronger password.")


def passwd_gen_chk(password):
    # Define dictionaries for character policies and entropies
    entropies = {'Uppercase characters': 26,
                 'Lowercase characters': 26,
                 'Special characters': 33,
                 'Numbers': 10}

    # Default cracking speed in hashes per second
    crack_speed = 20000000000

    # Check if a cracking speed is provided as a command-line argument
    if len(sys.argv) > 1:
        if sys.argv[1].isdigit():
            crack_speed = int(sys.argv[1])

    # Read new generated password from passwd_gen.py
    pass_len = len(password)

    # Get policy counts
    policies = get_policy_counts(password)

    # Remove password from memory
    del password

    # Calculate password entropy
    entropy = get_password_entropy(policies, entropies)

    # Print password entropy
    print("[+] %-25s %d" % ("Password entropy:", entropy))

    # Calculate and print estimated cracking time
    crack_time, time_, strength_level = get_cracking_time(entropy, pass_len, crack_speed)
    print("[+] Time to crack password:   {:,.2f} {}".format(crack_time, time_))
    if strength_level == "strong":
        print("[+] This password is strong and should provide good protection against cracking attempts.\n")
    elif strength_level == "medium":
        print("[!] Warning: This password is medium strength and may be at risk of being cracked. Consider using a stronger password.\n")
    else:
        print("[!] Warning: This password is weak and may be at risk of being cracked. Consider using a stronger password.\n")


def main():
    # Define dictionaries for character policies and entropies
    entropies = {'Uppercase characters': 26,
                 'Lowercase characters': 26,
                 'Special characters': 33,
                 'Numbers': 10}

    # Default cracking speed in hashes per second
    crack_speed = 20000000000

    # Check if a cracking speed is provided as a command-line argument
    if len(sys.argv) > 1:
        if sys.argv[1].isdigit():
            crack_speed = int(sys.argv[1])

    # Print introduction message
    print("\033[1m\033[3m\033[14mWP2C Password Strength Evaluation\033[0m")
    # Hashes/second to MH/s
    print(
        "Based on password cracking at: {:,d} MH/s.\n".format(int(crack_speed / 1000000)))

    # Read password from user
    password = getpass("Enter Password: ")
    pass_len = len(password)

    # Get policy counts
    policies = get_policy_counts(password)

    # Remove password from memory
    del password

    # Print password length and counts for each character type
    print("\n[+] %-25s %d\n" % ("Password length:", pass_len))
    print_policy_counts(policies)

    # Calculate password entropy
    entropy = get_password_entropy(policies, entropies)

    # Print password entropy
    print("\n[+] %-25s %d" % ("Password entropy:", entropy))

    # Calculate and print estimated cracking time
    crack_time, time_, strength_level = get_cracking_time(entropy, pass_len, crack_speed)
    print_cracking_time(crack_time, time_, strength_level)
