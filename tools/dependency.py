#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Dependency(object):
    dependency_name = None
    dependency_required = None
    dependency_url = None
    required_attr_names = ['dependency_name', 'dependency_url', 'dependency_required']

    def __init_subclass__(cls):
        for attr_name in cls.required_attr_names:
            if attr_name not in cls.__dict__:
                raise NotImplementedError(f'Attribute "{attr_name}" has not been overridden in class "{cls.__name__}"')

    @classmethod
    def exists(cls):
        from util.process import Process
        return Process.exists(cls.dependency_name)

    @classmethod
    def run_dependency_check(cls):
        from util.color import Color

        from tools.aircrack import Aircrack
        from tools.ip import Ip
        from tools.iw import Iw
        from tools.tshark import Tshark
        from tools.hashcat import Hashcat

        apps = [
            # Aircrack
            Aircrack,
            # wireless/net tools
            Iw, Ip,
            Tshark,
            # Hashcat
            Hashcat,
        ]

        missing_required = any(app.fails_dependency_check() for app in apps)

        if missing_required:
            Color.pl('{!} {O}At least 1 required app is missing. WP2C needs required apps to run{W}')
            import sys
            sys.exit(-1)

    @classmethod
    def fails_dependency_check(cls):
        from util.color import Color
        from util.process import Process

        if Process.exists(cls.dependency_name):
            return False

        if cls.dependency_required:
            Color.p('{!} {O}Error: Required app {R}%s{O} was not found' % cls.dependency_name)
            Color.pl('. {W}install @ {C}%s{W}' % cls.dependency_url)
            return True

        else:
            Color.p('{!} {O}Warning: Recommended app {R}%s{O} was not found' % cls.dependency_name)
            Color.pl('. {W}install @ {C}%s{W}' % cls.dependency_url)
            return False
