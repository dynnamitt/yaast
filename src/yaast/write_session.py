#!/usr/bin/env python3
"""Writes a new session/token into a dest profile
in ~/.aws/credentials, to simplify everyday MFA caching"""

from botocore.session import Session

import logging
from logging import info,debug

from . import esc, APP_META

from .awsconfigparser import CFile, AWSConfParser

# DEFAULT profiles
def_src_profile = "awsops"
def_dest_profile = "default"


logging.basicConfig(level=logging.INFO)


def resolve(profile, dest_profile, mfa_code):

    pr_max = max(len(profile), len(dest_profile))
    print(esc(34) + "Selected *base* profile:",
          esc(47)+esc(30), profile.ljust(pr_max), esc(0))
    print(esc(34) + "         *dest*  profile:", esc(42) +
          esc(30), dest_profile.ljust(pr_max), esc(0))

    if dest_profile == profile:
        raise Exception("Cannot continue with base == dest profile ! ")

    # info(f"back {backup}")

    aws_session = Session(profile=profile)

    creds, backup = load_creds(dest_profile)

    # useful stuff in botocore:
    scopeConfig = aws_session.get_scoped_config()

    # info(scopeConfig)
    mfa_serial = scopeConfig.get('mfa_serial')

    if not mfa_serial:
        raise Exception(f"No 'mfa_serial' in profile [{profile}]")

    else:
        print(f"MFA device = {mfa_serial}")

    opts = {
        "TokenCode":  mfa_code,
        "SerialNumber": mfa_serial
    }

    sess_creds = sts_session_creds(aws_session, opts)

    info(f"Downloaded new temp/creds. ID = {sess_creds['AccessKeyId']}")
    # info(resp)

    creds.set_new_attrs(backup, **attribs_from_raw(sess_creds, APP_META))

    edits = creds.save()
    print(esc(32) + "Wrote edits to file(s) :",
          esc(42)+esc(30) + str([str(fn.path) for fn in edits]) + esc(0))


def load_creds(dest_profile: str):
    """Load creds object and get backup bool"""

    creds = AWSConfParser(dest_profile, CFile.CREDS)

    backup = False

    # if creds.exists and creds.get('aws_session_token'):
    #     inp = input(
    #         f"Would you like to backup the old '{dest_profile}' session profile? [N/y] "
    #     )
    #     backup = inp.strip().lower() == 'y'
    # elif creds.exists:
    #     print(
    #         "WARNING: There is an existing (NON SESSION) destination profile.. "
    #     )
    #     inp = input(
    #         f" ..would you like to backup this '{dest_profile}' profile? [Y/n] "
    #     )
    #     backup = inp.strip().lower() == 'y'

    return creds, backup


def sts_session_creds(aws_session, opts):
    """This is where the logic FAILS in botocore.session,
    attributes already part of aws_session isn't passed on to client,
    so we FIX that here"""
    client = aws_session.create_client('sts')
    resp = client.get_session_token(**opts)
    return resp.get("Credentials")


def attribs_from_raw(raw_credentials, app_meta):
    """Transform API response object into coresponding 
       names inside the credentials-file"""

    # FIXME OrderedDict?
    return {
        "__appended_by_script__": app_meta["name"] + " " + app_meta["ver"],
        "__homepage__": app_meta["homepage"],
        "aws_access_key_id": raw_credentials['AccessKeyId'],
        "aws_secret_access_key": raw_credentials['SecretAccessKey'],
        "aws_session_token": raw_credentials['SessionToken'],
        "expiration": raw_credentials['Expiration']
    }
