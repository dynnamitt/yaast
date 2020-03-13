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
    print(f"         *dest*   profile [{dest_profile}].")

    aws_session = Session(profile=profile)
    
    # useful stuff in botocore:
    scopeConfig = aws_session.get_scoped_config()

    # debug(scopeConfig)
    mfa_serial = scopeConfig.get('mfa_serial')
    print(f"MFA device = {mfa_serial}")

    try:
        resp = sts_session_token(aws_session, mfacode, mfa_serial)
        r_creds = resp['Credentials']
    except botocore.exceptions.ClientError as clientErr:
        error(clientErr)
        exit(1)

    info(f"Downloaded new temp/creds. ID = {r_creds['AccessKeyId']}")
    #info(resp)

    creds = AWSConfParser(dest_profile, CFile.CREDS)

    #dest_conf_state = ConfState(dest_profile, must_exist=False)

    if creds.exists:
        # ask since dest_profile EXIST !!
        warning("NOTE: we should ask if user need a backup here.")
        pass

    creds.set_new_attrs(backup=True, **attribs_from_raw(r_creds))


    # dest_conf_state.new_credentials(attribs_from_raw(r_creds),
    #                            backup=ConfState.BACKUP_UNLESS_TOKEN)

    edits = creds.save()
    print(f"Wrote edits to file(s) : {[str(fn.path) for fn in edits]}")


def sts_session_token(aws_session,mfacode,mfa_serial):
    """This is where the logic FAILS in botocore.session,
    attributes already part of aws_session isn't passed on to client,
    so we fix that here"""

    client = aws_session.create_client('sts')
    return client.get_session_token( SerialNumber=mfa_serial,
                                    TokenCode=mfacode )

def attribs_from_raw(raw_credentials) :
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
