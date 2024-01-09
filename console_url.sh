#!/bin/sh
#
# ----------------------------------
#
#  assume-role and setup signinToken/url
#  to access AWS console
#

ROLE_ARN=$1

usage() {
	echo >&2 "usage: $0 <role_arn>"
	exit 1
}

if [ -z "$ROLE_ARN" ]; then
	usage
fi

TMP_CREDS_FILE=/tmp/_temp_Credentials.json

aws sts assume-role \
	--output json \
	--role-arn "$ROLE_ARN" \
	--role-session-name "temp-console" >$TMP_CREDS_FILE

REQ_SESS_ENCODED=$(jq -r '{ "sessionId" : .Credentials.AccessKeyId,
  "sessionKey": .Credentials.SecretAccessKey,
  "sessionToken": .Credentials.SessionToken} | @uri' \
	<$TMP_CREDS_FILE)

GET_SIGNIN_TOKEN_URL="https://signin.aws.amazon.com/federation?Action=getSigninToken&Session=${REQ_SESS_ENCODED}"

SIGNIN_TOKEN=$(curl --silent ${GET_SIGNIN_TOKEN_URL} | jq -r '.SigninToken')
CONSOLE=$(jq -nr --arg v "https://console.aws.amazon.com/" '$v|@uri')

CONSOLE_URL="https://signin.aws.amazon.com/federation?Action=login&Destination=${CONSOLE}&SigninToken=${SIGNIN_TOKEN}"

echo $CONSOLE_URL
