#!/usr/bin/python
import boto3 # pip install boto3 --user
import argparse

parser = argparse.ArgumentParser(
        description='''Quick handling of daily AWS
        IAM Session and AssumeRole by manipulation of 
        aws-conf-file profiles'''
        )

parser.add_argument('command',
        choices=['write_session','add_roles']
        )

args = parser.parse_args()
# print(args)

