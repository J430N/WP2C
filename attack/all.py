#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Developer Name: Mr. Jason Teo Jie Chen
# Program Name: all.py
# Description: Attack all selected targets
# First Written On: 20 February 2023
# Edited On: 7 March 2023 


from attack.wpa import AttackWPA
from util.color import Color


class AttackAll(object):

    @classmethod
    def attack_multiple(cls, targets):
        """
        Attacks all given `targets` (list[WP2C.model.target]) until user interruption.
        Returns: Number of targets that were attacked (int)
        """

        attacked_targets = 0
        targets_remaining = len(targets)
        for index, target in enumerate(targets, start=1):

            attacked_targets += 1
            targets_remaining -= 1

            bssid = target.bssid
            essid = target.essid if target.essid_known else '{O}ESSID unknown{W}'

            Color.pl('\n{+} ({G}%d{W}/{G}%d{W})'
                     % (index, len(targets)) + ' Starting attacks against {C}%s{W} ({C}%s{W})' % (bssid, essid))

            should_continue = cls.attack_single(target, targets_remaining)
            if not should_continue:
                break

        return attacked_targets

    @classmethod
    def attack_single(cls, target, targets_remaining):
        """
        Attacks a single `target` (WP2C.model.target).
        Returns: True if attacks should continue, False otherwise.
        """
        global attack
        if 'MGT' in target.authentication:
            Color.pl("\n{!}{O}Skipping. Target is using {C}WPA-Enterprise {O}and can not be cracked.")
            return True

        attacks = []
        
        if 'WPA' in target.encryption:
            attacks.append(AttackWPA(target))

        if not attacks:
            Color.pl('{!} {R}Error: {O}Unable to attack: no attacks available')
            return True  # Keep attacking other targets (skip)

        while attacks:
            target.attacked = True
            attack = attacks.pop(0)
            try:
                result = attack.run() # Boolean result returned from wpa module
                if result:
                    break  # Attack was successful, stop other attacks.
            except Exception as e:
                Color.pl('\r {!} {R}Error{W}: %s' % str(e))
                continue
            except KeyboardInterrupt:
                Color.pl('\n{!} {O}Interrupted{W}\n')
                answer = cls.user_wants_to_continue(targets_remaining, len(attacks))
                if answer is None:
                    return True  # Keep attacking other targets (skip)
                else:
                    return False  # Stop all attacks (exit)

        if attack.success: # Boolean result returned from wpa module
            attack.crack_result.save()

        return True  # Keep attacking other targets

    @classmethod
    def user_wants_to_continue(cls, targets_remaining, attacks_remaining=0):
        """
        Asks user if attacks should continue onto other targets
        Returns:
            None if the user wants to skip the current target
            True if the user wants to continue to the next attack on the current target
            False if the user wants to stop the remaining attacks
        """
        if attacks_remaining == 0 and targets_remaining == 0:
            return  # No targets or attacksleft, drop out

        prompt_list = []
        if targets_remaining > 0:
            prompt_list.append(Color.s('{C}%d{W} target(s)' % targets_remaining))
        prompt = ' and '.join(prompt_list) + ' remain'
        Color.pl('{+} %s' % prompt)

        if targets_remaining > 0:
            options = '({G}s{W}/{R}e{W})'
            prompt = '{+} Do you want to {G}skip(s){W} to the next target or {R}exit(e){W}%s?{C} ' % options
            
        Color.p(prompt)
        answer = input().lower()

        if answer.startswith('s'):
            return None  # Skip
        else: # ('e' or other character)
            return False  # Exit