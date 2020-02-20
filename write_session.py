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
# TODO cleanup format

def main():

    if environ.get('AWS_PROFILE'):
        warning("env AWS_PROFILE is set (use -p to override)")

    def_src_profile = environ['AWS_PROFILE'] if "AWS_PROFILE" in environ else "awsops"
    def_dest_profile = "default"

    parser = argparse.ArgumentParser(
            description='''Rewrites config state in ~/.aws/ files
            to simplify everyday MFA work''',
            epilog="More details in README.md file"
            )

    parser.add_argument('-p','--profile',default=def_src_profile)
    parser.add_argument('-d','--dest-profile',default=def_dest_profile)
    parser.add_argument('mfacode')
    args = parser.parse_args()

    print(f"Selected *source* profile [{args.profile}].")

    try:
        source = Conf(args.profile)
    except LookupError as ex:
        error(str(ex))
        exit(1)
    else:
        print(source.get_props_dict('''x mfa_serial region
        aws_secret_access_key aws_access_key_id
         aws_session_token'''))
        #print(source.pair[1])

class Conf:
    '''used twice ; once w source profile then w target profile'''

    conf_path = Path.home() / ".aws/config"
    cred_path = Path.home() / ".aws/credentials"

    def __init__(self, profile, must_exist=True):

        self.profile = profile

        self.credentials = configparser.ConfigParser()
        self.credentials.read(Conf.cred_path)
        debug(self.credentials.sections())

        self.config = configparser.ConfigParser()
        self.config.read(Conf.conf_path)
        debug(self.config.sections())

        if must_exist:
            self.__error_when_nonexistant()

        c_section_name = self.__find_c_section_name()

        self.core_profile = (
            self.config[c_section_name],
            self.credentials[self.profile]
        )

    def __error_when_nonexistant(self):
        if not self.profile in self.credentials.sections():
          raise LookupError(f"Profile '{self.profile}' not found in {Conf.cred_path}")
        c_section_name = self.__find_c_section_name()
        if not c_section_name:
          raise LookupError(f"Profile '{self.profile}' not found in {Conf.conf_path}")

    def __find_c_section_name(self):
        res = [s for s in self.config.sections() if re.search(self.profile,s)]
        return res[0] if len(res) else None

    # as dict
    def get_props_dict(self,props):
        '''Combine result from both INI files
        and give credentials precedence'''
        _props = props if isinstance(props,list) else props.split()
        debug(_props)
        config_sect,cred_sect = self.core_profile
        return dict(
            [(key,config_sect[key]) for key in config_sect if key in _props] +
            [(key,cred_sect[key]) for key in cred_sect if key in _props]
            )

    @property
    def pair(self):
        return self.core_profile

if __name__ == "__main__":
   main()
