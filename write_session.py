#!/usr/bin/python3
"""Writes a new session/token into a dest profile
in ~/.aws/ files, to simplify everyday MFA caching"""

from botocore.session import Session
import botocore.exceptions
from os import environ
from sys import exit

import argparse
import logging
from logging import debug,info,error,warning

#FIXME lookup the python-way
VER = "0.0.1"
SCRIPT_NAME = "yaast.write_session.py"
HOMEPAGE = "example.com"

logging.basicConfig(level=logging.INFO)

def main():

    if environ.get('AWS_PROFILE'):
        warning("env AWS_PROFILE is set (use -p to override)")

    def_src_profile = environ.get('AWS_PROFILE',default="awsops")
    def_dest_profile = "default"

    parser = argparse.ArgumentParser(
            description=__doc__,
            epilog="More details in README.md file"
            )

    parser.add_argument('-p', '--profile', default=def_src_profile,
                        help = "Source profile w/ mfa info and start credentials")
    parser.add_argument('-d','--dest-profile',default=def_dest_profile,
                        help = f"Dest profile to write to ({def_dest_profile})")
    parser.add_argument('mfacode')
    args = parser.parse_args()

    print(f"Selected *source* profile [{args.profile}].")
    print(f"         *dest*   profile [{args.dest_profile}].")

    aws_session = Session(profile=args.profile)
    # useful stuff:
    scopeConfig = aws_session.get_scoped_config()

    # debug(scopeConfig)
    mfa_serial = scopeConfig.get('mfa_serial')
    print(f"MFA device = {mfa_serial}")

    try:
        resp = sts_session_token(aws_session, args.mfacode, mfa_serial)
        r_creds = resp['Credentials']
    except botocore.exceptions.ClientError as clientErr:
        error(clientErr)
        exit(1)

    info(f"Downloaded new temp/creds. ID = {r_creds['AccessKeyId']}")
    #info(resp)

    # shoud not raise .. probably
    dest_conf_state = ConfState(args.dest_profile, must_exist=False)

    if dest_conf_state.found_profile:
        # ask since dest_profile EXIST !!
        warning("ASK__for_backup impl missing")
        pass


    dest_conf_state.new_credentials(state_attribs_from_raw(r_creds),
                               backup=ConfState.BACKUP_UNLESS_TOKEN)
    filenames = dest_conf_state.save()
    print(f"Wrote edits to file(s) : {[str(fn) for fn in filenames]}")


def sts_session_token(aws_session,mfacode,mfa_serial):
    """This is where the logic FAILS in botocore.session,
    attributes already part of aws_session isn't passed on to client,
    so we fix that here"""

    client = aws_session.create_client('sts')
    return client.get_session_token( SerialNumber=mfa_serial,
                                    TokenCode=mfacode )

def state_attribs_from_raw(raw_credentials) :
    # FIXME OrderedDict?
    return {
        "__appended_by_script__" : SCRIPT_NAME + f" {VER}",
        "__homepage__" : HOMEPAGE,
        "aws_access_key_id" : raw_credentials['AccessKeyId'],
        "aws_secret_access_key" : raw_credentials['SecretAccessKey'],
        "aws_session_token" : raw_credentials['SessionToken'],
        "expiration" : raw_credentials['Expiration']
        }

import configparser
from pathlib import Path
import re
from functools import lru_cache

class ConfState:
    """Used on target profile file duo"""

    # SOME Backup enums
    BACKUP_SKIP = 0
    BACKUP_UNLESS_TOKEN = 1
    BACKUP_ALWAYS = 2

    CONF_PATH = Path.home() / ".aws/config"
    CRED_PATH = Path.home() / ".aws/credentials"

    def __init__(self, profile, must_exist=True):

        self.profile = profile

        self.credentials = configparser.ConfigParser()
        self.credentials.read(self.__class__.CRED_PATH)
        debug(self.credentials.sections())

        self.config = configparser.ConfigParser()
        self.config.read(self.__class__.CONF_PATH)
        debug(self.config.sections())

        if must_exist and not self.found_profile:
            raise LookupError("Cannot continue")


    @property
    # cached
    def found_profile(self):

        def scan():
            found_in_creds = self.profile in self.credentials.sections()
            if not found_in_creds:
              info(f"Profile '{self.profile}' not found in {self.__class__.CRED_PATH}")

            found_in_config = self.__find_c_section_name()
            if not found_in_config:
                info(f"Profile '{self.profile}' not found in {self.__class__.CONF_PATH}")
            self._cached_found_profile = (found_in_creds and found_in_config)
        #cache
        if not hasattr(self, "_cached_found_profile"):
            scan()
        return self._cached_found_profile


    def __find_c_section_name(self):
        """Since profile has 'profile ' prefix in config file """
        res = [s for s in self.config.sections() if re.search(self.profile,s)]
        return res[0] if len(res) else None

    # as dict
    def get_props_dict(self):
        """Combine result from both INI files
        and give credentials precedence"""
        conf_sect = self.config[self.__find_c_section_name()]
        creds_sect = self.credentials[self.profile]

        if self.found_profile:
            return dict(
                [(key, conf_sect[key]) for key in conf_sect] +
                [(key, creds_sect[key]) for key in creds_sect]
                )
        else:
            None



    def new_credentials(self, attributes, backup=BACKUP_ALWAYS):

        def __has_token():
            return self.get_props_dict().get('aws_session_token') if self.found_profile else None

        if self.found_profile and backup==self.__class__.BACKUP_ALWAYS :
            self.__append_backup_profile()
        elif self.found_profile and backup==self.__class__.BACKUP_UNLESS_TOKEN :
            self.__append_backup_profile() if not __has_token() else None
        elif self.found_profile:
            # this is the old one that will be replaced
            debug([(key,self.credentials[self.profile][key]) for key in self.credentials[self.profile]])

        self.credentials[self.profile] = attributes


    def save(self):
        # we only tampered w credentials so..
        with open(self.__class__.CRED_PATH, 'w') as f:
            self.credentials.write(f)

        return [self.__class__.CRED_PATH]

    def __append_backup_profile(self):
        # some algo to makeup a name
        warning("__append_backup_profile() impl missing")
        pass


if __name__ == "__main__":
   main()
