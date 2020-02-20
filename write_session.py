#!/usr/bin/python3
"""Writes a new session/token into a dest profile
in ~/.aws/ files, to simplify everyday MFA caching"""

from botocore.session import Session
import botocore.exceptions
import configparser
from os import environ
from sys import exit

import argparse
import logging
from logging import debug,info,error,warning


def main():
    logging.basicConfig(level=logging.INFO)

    if environ.get('AWS_PROFILE'):
        warning("env AWS_PROFILE is set (use -p to override)")

    def_src_profile = environ.get('AWS_PROFILE',default="awsops")
    def_dest_profile = "default"

    parser = argparse.ArgumentParser(
            description=__doc__,
            epilog="More details in README.md file"
            )

    parser.add_argument('-p','--profile',default=def_src_profile)
    parser.add_argument('-d','--dest-profile',default=def_dest_profile)
    parser.add_argument('mfacode')
    args = parser.parse_args()

    print(f"Selected *source* profile [{args.profile}].")
    print(f"         *dest*   profile [{args.dest_profile}].")

    aws_session = Session(profile=args.profile)
    scopeConfig = aws_session.get_scoped_config()

    # debug(scopeConfig) !!contains secret!!
    mfa_serial = scopeConfig.get('mfa_serial')
    print(f"MFA device = {mfa_serial}")

    try:
        resp = sts_session_token(aws_session, args.mfacode, mfa_serial)
    except botocore.exceptions.ClientError as clientErr:
        error(clientErr)
        exit(1)
    else:
        print(resp)

    # try:
    #     source = Conf(args.profile)
    # except LookupError as ex:
    #     error(str(ex))
    #     exit(1)
    # else:
    #     props = source.get_props_dict('''mfa_serial region
    #     aws_secret_access_key aws_access_key_id
    #     aws_session_token''')
    #     info(props)
    #     sts_session(**props)
    #     #print(source.pair[1])

# DEAD
def sts_session_token(aws_session,mfacode,mfa_serial):
    """This is where the logic FAILS in botocore.session,
    attributes already part of aws_session isn't passed on to client,
    so we fix that here"""

    client = aws_session.create_client('sts')
    return client.get_session_token( SerialNumber=mfa_serial,
                         TokenCode=mfacode )

# NOT IN USE
class Conf:
    """FIXME Rewrite to use on target profile"""
    from pathlib import Path
    import re

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

        self.sections_pair = (
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
        """Combine result from both INI files
        and give credentials precedence"""
        _props = props if isinstance(props,list) else props.split()
        debug(_props)
        config_sect,cred_sect = self.sections_pair
        return dict(
            [(key,config_sect[key]) for key in config_sect if key in _props] +
            [(key,cred_sect[key]) for key in cred_sect if key in _props]
            )

    @property
    def pair(self):
        return self.sections_pair



if __name__ == "__main__":
   main()
