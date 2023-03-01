import os
import sys
import getpass
from config import Configuration
from secrets import choice, randbelow

#install zxcvbn using sudo pip install zxcvbn
from zxcvbn import zxcvbn
from zxcvbn.matching import add_frequency_lists


# Lowercase alphabet.
ALPHA_MIN = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l",
             "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
# Capital alphabet.
ALPHA_MAJ = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L",
             "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
# Numbers.
NUMBERS = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
# Special characters.
CARACTS_SPE = ["&", "~", '"', "#", "'", "{", "(", "[", "-", "|", "`", "_", "^",
               "@", ")", "]", "°", "+", "=", "}", "¨", "£", "$", "¤", "%", "µ",
               "*", "!", "§", ":", ";", ".", ",", "?"]

# Comment on the password score.
SCORE_TO_WORD = {
    0: "Very weak",
    1: "Very weak",
    2: "Weak",
    3: "Medium",
    4: "Strong",
}


def check_password(password):
    """ Evaluates the strength of the password according to several criteria. Powered by zxcvbn. """

    # --- Load the dictionaries and add them to zxcvbn.
    dict_wordlists = {}
    # Default location dictionaries (defined in the config file).
    for file_name in Configuration.wordlists:
        print("file name",file_name)
        with open(file_name, "r") as f:
            list_actual_dict = f.read().split("\n")[:-1]
            # print("actual dict: ", list_actual_dict)
        dict_wordlists[os.path.splitext(file_name)[0]] = list_actual_dict
    add_frequency_lists(dict_wordlists)

    # --- Gets the password results with zxcvbn and displays the score.
    if not password:
        raise SystemExit("ValueError: The password is empty.")
    result = zxcvbn(password)
    print("    " + SCORE_TO_WORD[result["score"]] + " (" + str(result["score"]) + "/4)")

    # --- Shows the estimated time.
    print("\nEstimated time needed to guess the password: ")
    print("    Fast hashing with many processors (1e10/s) : ",
          result["crack_times_display"]["offline_fast_hashing_1e10_per_second"])
    print("    Slow hashing with many processors (1e4/s) :  ",
          result["crack_times_display"]["offline_slow_hashing_1e4_per_second"])
    print("    Online attack without throttling (10/s) :    ",
          result["crack_times_display"]["online_no_throttling_10_per_second"])
    print("    Online attack with throttling (100/h) :      ",
          result["crack_times_display"]["online_throttling_100_per_hour"])

    # --- Feedback
    no_feedback = True
    print("\nComments and recommendations: ")
    if result["feedback"]["warning"] != "":
        no_feedback = False
        print("    " + result["feedback"]["warning"])
    for x in result["feedback"]["suggestions"]:
        no_feedback = False
        print("    " + x)
    if len(password) <= 6:
        no_feedback = False
        print("    Your password is much too short."
              " A minimum length of 14 characters is recommended.")
    elif len(password) < 14:
        no_feedback = False
        print("    A minimum length of 14 characters is recommended.")
    # Dispersion of numbers and special characters
    nb_nums = 0
    nb_cs = 0
    for x in password:
        if x in NUMBERS:
            nb_nums += 1
        elif x in CARACTS_SPE:
            nb_cs += 1
    nb_nums_start_end = 0
    nb_cs_start_end = 0
    for x in password:
        if x in NUMBERS:
            nb_nums_start_end += 1
        elif x in CARACTS_SPE:
            nb_cs_start_end += 1
        else:
            break
    for x in reversed(password):
        if x in NUMBERS:
            nb_nums_start_end += 1
        elif x in CARACTS_SPE:
            nb_cs_start_end += 1
        else:
            break
    if nb_nums_start_end == nb_nums and nb_nums != 0:
        no_feedback = False
        if nb_cs_start_end == nb_cs and nb_cs != 0:
            print("    Numbers and special characters are not scattered correctly.")
        else:
            print("    The numbers are not dispersed properly.")
    elif nb_cs_start_end == nb_cs and nb_cs != 0:
        no_feedback = False
        print("    Special characters are not scattered correctly.")
    if no_feedback:
        print("    No comments available.")

    # --- Exposure in dictionaries.
    print("\nExposure report:")
    no_matches_found = True
    for exposed in result["sequence"]:
        try:
            print("    '" + exposed["matched_word"] + "' found in " + exposed["dictionary_name"])
            no_matches_found = False
        except KeyError:
            pass  # No matche found
    if no_matches_found:
        print("    No matches found.")

def run():
    password = input('Enter password: ')
    check_password(password)
# while True:
#     # read user input one character at a time
#     password = getpass.getpass('Enter password: ')
#     char = sys.stdin.read(1)

#     # check if user pressed enter
#     if char == '\n':
#         # overwrite newline with a space character
#         sys.stdout.write(' ') #Fix the incorrect input to nothing
        
#         # do nothing (i.e. don't echo enter key)
#         # continue

#     # check if user pressed backspace
#     if char == '\x08':
#         # move the cursor back one character
#         sys.stdout.write('\b \b')
#     else:
#         # echo the user's input
#         sys.stdout.write(char)

#     # flush stdout buffer to ensure real-time output
#     sys.stdout.flush()