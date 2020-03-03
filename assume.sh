#!/bin/sh

usage(){
  exec 1>&2
  echo "Usage:"
  echo "   $0 <session-name> [profile]"
  exit 1
}

SESS_NAME=$1

[ -z "$SESS_NAME" ] && usage

AWS_PROFILE=${2:-$AWS_PROFILE}

if [ -z "$AWS_PROFILE" ];then
  echo 1>&2 "No profile found! (AWS_PROFILE fallback failed)"
  usage
fi

echo 1>&2 "Profile = $AWS_PROFILE"

ROLE_ARN=$(aws --profile $AWS_PROFILE configure get role_arn)
SRC_PROFILE=$(aws --profile $AWS_PROFILE configure get source_profile)
EXT_ID=$(aws --profile $AWS_PROFILE configure get external_id)
MFA_SERIAL=$(aws --profile $AWS_PROFILE configure get mfa_serial)

if [ ! -z "$EXT_ID" ]; then
  _EXT_ID="--external-id $EXT_ID"
fi

if [ ! -z "$MFA_SERIAL" ]; then
  _MFA_SERIAL="--serial-number $MFA_SERIAL"
fi

set -x
aws sts assume-role \
  --role-arn "$ROLE_ARN" \
  --role-session-name "$SESS_NAME" \
  $_EXT_ID $_MFA_SERIAL

