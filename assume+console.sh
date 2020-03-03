#!/bin/bash

usage(){
  exec 1>&2
  echo "Usage:"
  echo "   $0 [profile]"
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


AWS_PROFILE=${1:-$AWS_PROFILE}

if [ -z "$AWS_PROFILE" ];then
  echo 1>&2 "No profile found! (AWS_PROFILE fallback failed)"
  usage
fi

# echo 1>&2 "Profile = $AWS_PROFILE"

# required args:
ROLE_ARN=$(aws --profile $AWS_PROFILE configure get role_arn) # NOTE: cli has a cache BUT we cannot use it

SESS_NAME=$(aws --profile $AWS_PROFILE configure get role_session_name)

if [ -z "$SESS_NAME" ]; then
  SESS_NAME="$AWS_PROFILE-$((RANDOM % 23456))"
fi

# optional args:
EXT_ID=$(aws --profile $AWS_PROFILE configure get external_id)
MFA_SERIAL=$(aws --profile $AWS_PROFILE configure get mfa_serial)

if [ ! -z "$EXT_ID" ]; then
  _EXT_ID="--external-id $EXT_ID"
fi

if [ ! -z "$MFA_SERIAL" ]; then
  _MFA_SERIAL="--serial-number $MFA_SERIAL"
fi

TMP_CREDS_FILE=/tmp/_Credentials

aws sts assume-role \
  --role-arn "$ROLE_ARN" \
  --role-session-name "$SESS_NAME" \
  $_EXT_ID $_MFA_SERIAL > $TMP_CREDS_FILE


REQ_SESS=$(jq '{ "sessionId" : .Credentials.AccessKeyId,
  "sessionKey": .Credentials.SecretAccessKey,
  "sessionToken": .Credentials.SessionToken}' \
  < $TMP_CREDS_FILE)


REQ_SESS_ENCODED=$(_rawurlencode "$REQ_SESS")
URL="https://signin.aws.amazon.com/federation?Action=getSigninToken&Session=${REQ_SESS_ENCODED}"

#echo $URL
SIGNIN_TOKEN=$(curl --silent ${URL} | jq -r '.SigninToken')
CONSOLE=$(_rawurlencode "https://console.aws.amazon.com/")

CONSOLE_URL="https://signin.aws.amazon.com/federation?Action=login&Issuer=&Destination=${CONSOLE}&SigninToken=${SIGNIN_TOKEN}"

# MERGE it back out .. ready for another code
jq '{ "Credentials" : .Credentials, "CONSOLE_URL": "'$CONSOLE_URL'"}' < $TMP_CREDS_FILE

