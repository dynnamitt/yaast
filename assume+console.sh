#!/bin/bash

#
# Extracted code from https://github.com/basefarm/aws-session-tool
# 
# This is just the "get_console_url" feature adapted for 
# awscli/tools using profiles in the ~/.aws/ files
#
# NOTE: Script has been run w/ checkbashisms and kept POSIX to inspire
#       me to write a python version :-|

AWS_PROFILE=${1:-$AWS_PROFILE}

usage(){
  exec 1>&2
  echo "Usage:"
  echo "   $0 [role_arn-profile]"
  echo ""
  echo "   Will return temp AssumeRole credentials as JSON and"
  echo "   with BONUS 'CONSOLE_URL' appended (through one extra API called)"
  exit 1
}

set -x
export LANG=C

# urlencode_posix() {
 # No good !
 # 
#   _arg="$1"
#   _idx="0"
#   while [ "$_idx" -lt ${#_arg} ]; do
#     #c=${_arg:$_idx:1}
#     c=$(echo "$_arg"|cut -c$(( $_idx + 1 ))-$(( $_idx + 2 )))
#     if echo "$c" | grep -q '[a-zA-Z/:_\.\-]'; then
#       echo -n "$c"
#     else
#       echo -n "%"
#       printf "%X" "'$c'"
#     fi
#     i=$((_idx+1))
#   done
# }


# Utility to urlencode a string (bashisms)
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
}

read_mfa_code(){

  exec 1>&2
  echo "# -------------- mfa_serial found ------------------ #  "
  echo
  echo "  This is probably not the best way to use MFA,         "
  echo "  Have a look at [write_session.py] to avoid retyping   "
  echo "  MFA codes every AssumeRole call, since session        "
  echo "  credentials dont't expire during your workday!        "
  echo
  printf "MFA CODE : "
  read MFA_CODE
}

get_p_attr(){
  aws --profile $AWS_PROFILE configure get $1
}

gen_session_name(){
  # TODO make a safe prefix
  _sess_prefix=$AWS_PROFILE
  echo "$_sess_prefix-$((RANDOM % 23456))"
}

# ------------------
#
#        M A I N
#
# ------------------

if [ -z "$AWS_PROFILE" ];then
  echo 1>&2 "ERROR: No profile found! (AWS_PROFILE fallback failed)"
  usage
fi

# required args:
ROLE_ARN=$(get_p_attr role_arn) # NOTE: cli has a cache BUT we cannot use it

if [ -z "$ROLE_ARN" ];then
  echo 1>&2 "ERROR: No role_arn found in profile, no point to continue!"
  usage
fi

SESS_NAME=$(get_p_attr role_session_name)

if [ -z "$SESS_NAME" ]; then
  SESS_NAME=$(gen_session_name)
fi

echo 1>&2 "INFO: role_session_name set to '$SESS_NAME'"


# optional args:
EXT_ID=$(get_p_attr external_id)
MFA_SERIAL=$(get_p_attr mfa_serial)

if [ ! -z "$EXT_ID" ]; then
  _EXT_ID="--external-id $EXT_ID"
fi

if [ ! -z "$MFA_SERIAL" ]; then
  read_mfa_code
  if [ -z $MFA_CODE ];then
    echo 1>&2 "ERROR: Cannot use empty code!"
    usage
  fi
  _MFA_SERIAL="--serial-number $MFA_SERIAL --token-code $MFA_CODE"
fi

TMP_CREDS_FILE=/tmp/_temp_Credentials.json

aws sts assume-role \
  --output json \
  --role-arn "$ROLE_ARN" \
  --role-session-name "$SESS_NAME" \
  $_EXT_ID $_MFA_SERIAL > $TMP_CREDS_FILE

REQ_SESS=$(jq '{ "sessionId" : .Credentials.AccessKeyId,
  "sessionKey": .Credentials.SecretAccessKey,
  "sessionToken": .Credentials.SessionToken}' \
  < $TMP_CREDS_FILE)

REQ_SESS_ENCODED=$(_rawurlencode "$REQ_SESS")
GET_SIGNIN_TOKEN_URL="https://signin.aws.amazon.com/federation?Action=getSigninToken&Session=${REQ_SESS_ENCODED}"

#echo $GET_SIGNIN_TOKEN_URL
SIGNIN_TOKEN=$(curl --silent ${GET_SIGNIN_TOKEN_URL} | jq -r '.SigninToken')
CONSOLE=$(_rawurlencode "https://console.aws.amazon.com/")

CONSOLE_URL="https://signin.aws.amazon.com/federation?Action=login&Issuer=&Destination=${CONSOLE}&SigninToken=${SIGNIN_TOKEN}"

# MERGE it back out .. ready for another code
jq '{ "Credentials" : .Credentials, "CONSOLE_URL": "'$CONSOLE_URL'"}' < $TMP_CREDS_FILE


