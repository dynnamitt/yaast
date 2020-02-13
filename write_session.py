#!/usr/bin/python3

import boto3
from os import environ
import argparse
from logging import info,error,warning

logging.basicConfig(level='logging.DEBUG')


parser = argparse.ArgumentParser(
        description='''Rewrites config state in ~/.aws/ files
        to simplify everyday MFA work''',
        epilog="More details in README.md file"
        )


parser.add_argument('mfacode')

if environ.get('AWS_PROFILE'):
    warning("AWS_PROFILE set (use -p to override)")

def_profile = environ['AWS_PROFILE'] if "AWS_PROFILE" in environ else "awsops"

parser.add_argument('-p','--profile',default=def_profile)

args = parser.parse_args()

info("Note this will CHANGE STATE by edit of files ~/.aws/{credentials,config} ")
info("The very state used by this very tool, so DOUBLECHECK your arguments")
info("=" * 40)

info(f"Using pre configured profile {args.profile}")
session = boto3.Session
