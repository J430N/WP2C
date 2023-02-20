#!/usr/bin/env python
# -*- coding: utf-8 -*-

from attack.wpa import AttackWPA
from config import Configuration
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
            # if Configuration.attack_max != 0 and index > Configuration.attack_max:
            #     print(("Attacked %d targets, stopping because of the --first flag" % Configuration.attack_max))
            #     break
            # attacked_targets += 1
            # targets_remaining -= 1

            # bssid = target.bssid
            # essid = target.essid if target.essid_known else '{O}ESSID unknown{W}'

            # Color.pl('\n{+} ({G}%d{W}/{G}%d{W})'
            #          % (index, len(targets)) + ' Starting attacks against {C}%s{W} ({C}%s{W})' % (bssid, essid))

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
            # Needed by infinite attack mode in order to count how many targets were attacked
            target.attacked = True
            attack = attacks.pop(0)
            try:
                result = attack.run() #Boolean result returned from wpa module
                if result:
                    break  # Attack was successful, stop other attacks.
            except Exception as e:
                Color.pl('\r {!} {R}Error{W}: %s' % str(e))
                continue
            except KeyboardInterrupt:
                Color.pl('\n{!} {O}Interrupted{W}\n')
                answer = cls.user_wants_to_continue(targets_remaining, len(attacks))
                if answer is True:
                    continue  # Keep attacking the same target (continue)
                elif answer is None:
                    return True  # Keep attacking other targets (skip)
                else:
                    return False  # Stop all attacks (exit)

        if attack.success: #Boolean result returned from wpa module
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
        if attacks_remaining > 0:
            prompt_list.append(Color.s('{C}%d{W} attack(s)' % attacks_remaining))
        if targets_remaining > 0:
            prompt_list.append(Color.s('{C}%d{W} target(s)' % targets_remaining))
        prompt = ' and '.join(prompt_list) + ' remain'
        Color.pl('{+} %s' % prompt)

        prompt = '{+} Do you want to'

        if attacks_remaining > 0:
            prompt += ' {G}continue (c){W} attacking? Ans: '

        if targets_remaining > 0:
            prompt += ' {O}skip (s){W} to the next target? Ans: '

        Color.p(prompt)
        answer = input().lower()

        if answer.startswith('s'):
            return None  # Skip
        else:
            return True  # Continue
