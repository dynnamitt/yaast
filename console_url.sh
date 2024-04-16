#!/bin/sh
#
# ----------------------------------
#
#  assume-role and setup signinToken/url
#  to access AWS console
#

ROLE_ARN=$1

SESSION_NAME=yaast-cli

__usage() {
	echo >&2 "usage: $0 <role_arn>"
	exit 1
}

__assume(){
	out=$1
	aws sts assume-role \
		--output json \
		--role-arn "$ROLE_ARN" \
		--role-session-name "$SESSION_NAME" \
		> $out
}


# if some flag ?
__export_to_sh(){
	infile=$1
	export AWS_ACCESS_KEY_ID=$(echo $infile | jq -r '.Credentials''.AccessKeyId')
	export AWS_SECRET_ACCESS_KEY=$(echo $infile | jq -r '.Credentials''.SecretAccessKey')
	export AWS_SESSION_TOKEN=$(echo $infile | jq -r '.Credentials''.SessionToken')
}

__fetch_signin_token(){
	infile=$1

	REQ_SESS_ENCODED=$(jq -r '{ "sessionId" : .Credentials.AccessKeyId,
	  "sessionKey": .Credentials.SecretAccessKey,
	  "sessionToken": .Credentials.SessionToken} | @uri' \
		< $infile)

	GET_SIGNIN_TOKEN_URL="https://signin.aws.amazon.com/federation?Action=getSigninToken&Session=${REQ_SESS_ENCODED}"

	SIGNIN_TOKEN=$(curl --silent ${GET_SIGNIN_TOKEN_URL} | jq -r '.SigninToken')
	CONSOLE=$(jq -nr --arg v "https://console.aws.amazon.com/" '$v|@uri')

	echo "https://signin.aws.amazon.com/federation?Action=login&Destination=${CONSOLE}&SigninToken=${SIGNIN_TOKEN}"
}

# ---------------------------------------------------------
#
###                         M A I N
#
# ---------------------------------------------------------

[ -z "$ROLE_ARN" ] && __usage

TMP_CREDS_FILE=$(mktemp /tmp/Yaast_Credentials_XXXXXXX.json)

__assume $TMP_CREDS_FILE

if [ $? -gt 0 ] 
then
	echo " ⌧ "
	__usage
fi

URL=$(__fetch_signin_token $TMP_CREDS_FILE)
echo "$URL"


# __export_to_sh $TMP_CREDS_FILE
