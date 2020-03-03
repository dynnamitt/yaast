#!/bin/bash

usage(){
  exec 1>&2
  echo "Usage:"
  echo "   $0 <session-name> [profile]"
  echo ""
  echo "   Will return the Credentials in json and"
  echo "   with BONUS 'CONSOLE_URL' appended (through extra API called)"
  exit 1
}

# Utility to urlencode a string
_rawurlencode() {
  local string="${1}"
  local strlen=${#string}
  local encoded=""

  for (( pos=0 ; pos<strlen ; pos++ )); do
    c=${string:$pos:1}
    case "$c" in
      [-_.~a-zA-Z0-9] ) o="${c}" ;;
      *               ) printf -v o '%%%02x' "'$c"
     esac
     encoded+="${o}"
  done
  echo "${encoded}"
    return 0
}

# ------------------
#
#
#     M A I N
#
#
# ------------------

SESS_NAME=$1

[ -z "$SESS_NAME" ] && usage

AWS_PROFILE=${2:-$AWS_PROFILE}

if [ -z "$AWS_PROFILE" ];then
  echo 1>&2 "No profile found! (AWS_PROFILE fallback failed)"
  usage
fi

echo 1>&2 "Profile = $AWS_PROFILE"

# required args:
ROLE_ARN=$(aws --profile $AWS_PROFILE configure get role_arn)
SRC_PROFILE=$(aws --profile $AWS_PROFILE configure get source_profile)

# optional args:
EXT_ID=$(aws --profile $AWS_PROFILE configure get external_id)
MFA_SERIAL=$(aws --profile $AWS_PROFILE configure get mfa_serial)

if [ ! -z "$EXT_ID" ]; then
  _EXT_ID="--external-id $EXT_ID"
fi

if [ ! -z "$MFA_SERIAL" ]; then
  _MFA_SERIAL="--serial-number $MFA_SERIAL"
fi


aws sts assume-role \
  --role-arn "$ROLE_ARN" \
  --role-session-name "$SESS_NAME" \
  $_EXT_ID $_MFA_SERIAL

