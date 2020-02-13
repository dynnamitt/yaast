#!/usr/bin/python3

import boto3
from os import environ
import argparse
import logging
from logging import info,error,warning

logging.basicConfig(level=logging.DEBUG)


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

print("*" * 60)
print("This tool will CHANGE STATE by edit of files ~/.aws/{credentials,config} ")
print("The very state used by this very tool, so DOUBLECHECK your arguments")
print("=" * 60)

print(f"Using profile [{args.profile}].")
session = boto3.Session
