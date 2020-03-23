#!/usr/bin/env python3
"""Writes a new session/token into a dest profile
in ~/.aws/credentials, to simplify everyday MFA caching"""

from botocore.session import Session
import botocore.exceptions
from os import environ
from sys import exit

import argparse
import logging
from logging import debug,info,error,warning

from awsconfigparser import CFile,AWSConfParser

# FIXME lookup the python-way (setup_tools)
VER = "0.0.2"
SCRIPT_NAME = "yaast.write_session.py"
HOMEPAGE = "example.com"

logging.basicConfig(level=logging.INFO)

def main(profile, dest_profile, mfacode):
    
    print(f"Selected *start* profile [{profile}].")
    print(f"         *dest*  profile [{dest_profile}].")

    if not mfacode:
        print("ERROR: no mfacode!")
        exit(1)

    if dest_profile == profile:
        print("ERROR: Cannot continue with 'start == destination' ! ")
        exit(1)

    creds, backup = load_creds(dest_profile)

    #info(f"back {backup}")

    aws_session = Session(profile=profile)
    
    # useful stuff in botocore:
    scopeConfig = aws_session.get_scoped_config()

    # debug(scopeConfig)
    mfa_serial = scopeConfig.get('mfa_serial')
    print(f"MFA device = {mfa_serial}")

    if not mfa_serial:
        print(f"ERROR: Add 'mfa_serial' to profile [{profile}]")
        exit(1)

    try:
        resp = sts_session_token(aws_session, mfacode, mfa_serial)
        r_creds = resp['Credentials']
    except botocore.exceptions.ClientError as clientErr:
        error(clientErr)
        exit(1)

    info(f"Downloaded new temp/creds. ID = {r_creds['AccessKeyId']}")
    #info(resp)

    
    creds.set_new_attrs(backup, **attribs_from_raw(r_creds))

    edits = creds.save()
    print(f"Wrote edits to file(s) : {[str(fn.path) for fn in edits]}")



def load_creds(dest_profile:str):
    """Load creds object and get backup bool"""

    creds = AWSConfParser(dest_profile, CFile.CREDS)

    backup = False

    if creds.exists and creds.get('aws_session_token') :
        inp = input(f"Would you like to backup the old '{dest_profile}' session profile? [N/y] ")
        backup = inp.strip().lower() == 'y'
    elif creds.exists:
        print("WARNING: There is an existing (NON SESSION) destination profile.. ")
        inp = input(f" ..would you like to backup this '{dest_profile}' profile? [Y/n] ")
        backup = inp.strip().lower() == 'y'

    return creds,backup


def sts_session_token(aws_session, mfacode=None, mfa_serial=None):
    """This is where the logic FAILS in botocore.session,
    attributes already part of aws_session isn't passed on to client,
    so we FIX that here"""
    client = aws_session.create_client('sts')
    return client.get_session_token( SerialNumber=mfa_serial,
                                    TokenCode=mfacode )

def attribs_from_raw(raw_credentials) :
    """Transform API response object into coresponding 
       names inside the credentials-file"""

    # FIXME OrderedDict?
    return {
        "__appended_by_script__" : SCRIPT_NAME + f" {VER}",
        "__homepage__" : HOMEPAGE,
        "aws_access_key_id" : raw_credentials['AccessKeyId'],
        "aws_secret_access_key" : raw_credentials['SecretAccessKey'],
        "aws_session_token" : raw_credentials['SessionToken'],
        "expiration" : raw_credentials['Expiration']
        }


if __name__ == "__main__":

    if environ.get('AWS_PROFILE'):
        warning("env AWS_PROFILE is set (use -p to override)")

    def_src_profile = environ.get('AWS_PROFILE',default="awsops")
    def_dest_profile = "default"

    parser = argparse.ArgumentParser(
            description=__doc__,
            epilog="More details in README.md file"
            )

    parser.add_argument('-p', '--profile', default=def_src_profile,
                        help = f'The profile w/ mfa info and start credentials. "{def_src_profile}" when unset')
    parser.add_argument('-d','--dest-profile',default=def_dest_profile,
                        help = f'Dest profile to write to. "{def_dest_profile}" when unset')
    parser.add_argument('mfacode')

    args = parser.parse_args()

    main(**vars(args))
