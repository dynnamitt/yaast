#!/usr/bin/python3

import botocore
import configparser
from os import environ
from sys import exit
from pathlib import Path
import re
import argparse
import logging
from logging import debug,info,error,warning

logging.basicConfig(level=logging.DEBUG)

def main():

    if environ.get('AWS_PROFILE'):
        warning("env AWS_PROFILE is set (use -p to override)")

    def_profile = environ['AWS_PROFILE'] if "AWS_PROFILE" in environ else "awsops"

    parser = argparse.ArgumentParser(
            description='''Rewrites config state in ~/.aws/ files
            to simplify everyday MFA work''',
            epilog="More details in README.md file"
            )

    parser.add_argument('-p','--profile',default=def_profile)
    parser.add_argument('mfacode')
    args = parser.parse_args()

    print(f"Using profile [{args.profile}].")

    try:
        c = Conf(args.profile)
    except LookupError as ex:
        error(str(ex))
        exit(1)
    else:
        print(c.pair)

class Conf:
    '''Fixes some issues found in boto3+awscli, see README'''

    conf_path = Path.home() / ".aws/config"
    cred_path = Path.home() / ".aws/credentials"

    def __init__(self,profile):

        self.credentials = configparser.ConfigParser()
        self.credentials.read(Conf.cred_path)
        debug(self.credentials.sections())
        if not profile in self.credentials.sections():
          raise LookupError(f"The profile '{profile}' not found in {Conf.cred_path}")

        self.config = configparser.ConfigParser()
        self.config.read(Conf.conf_path)
        debug(self.config.sections())
        c_section_name = self.__find_c_section_name(self.config.sections(), profile=profile)
        if not c_section_name:
          raise LookupError(f"The profile '{profile}' not found in {Conf.conf_path}")

        self.core_profile = (
            self.config[c_section_name],
            self.credentials[profile]
        )

    @classmethod
    def __find_c_section_name(self, sections, profile):
        res = [s for s in sections if re.search(profile,s)]
        return res[0] if len(res) else None

    @property
    def pair(self):
        return self.core_profile

if __name__ == "__main__":
   main()
