#!/bin/sh

# ----------------------------------------------------------------
# Extracted parts from https://github.com/basefarm/aws-session-tool
#
# checkbashisms => zero warnings :)
#
# This is the "get_console_url" feature adapted for
# awscli/tools using PROFILES in the ~/.aws/ files
#
# Depends on [jq] to solve
#   - json parsing
#   - uri_encoding
#
# ----------------------------------------------------------------

AWS_PROFILE=${1:-$AWS_PROFILE}

OUT_FMT=${2:-json}

usage() {
	(
		echo "Usage:"
		echo "   $0 [role_arn-profile] [json|text]"
		echo ""
		echo "   Will return temp AssumeRole credentials as JSON and"
		echo "   with BONUS 'CONSOLE_URL' appended (through one extra API called)"
	) >&2
	exit 1
}

read_mfa_code() {
	(
		echo "# -------------- mfa_serial found ------------------ #  "
		echo
		echo "  This is probably not the best way to use MFA,         "
		echo "  Have a look at [write_session.py] to avoid retyping   "
		echo "  MFA codes every AssumeRole call, since session        "
		echo "  credentials dont't expire during your workday!        "
		echo
		printf "MFA CODE : "
	) >&2
	read MFA_CODE
}

get_p_attr() {
	aws --profile $AWS_PROFILE configure get $1
}

gen_session_name() {
	# TODO make a safe prefix
	_sess_prefix=$AWS_PROFILE
	echo "$_sess_prefix-$(date +'%s')"
}

# ------------------
#
#    M A I N
#
# ------------------

if [ -z "$AWS_PROFILE" ]; then
	echo 1>&2 "ERROR: No profile found! (AWS_PROFILE fallback failed)"
	usage
fi

if [ "$OUT_FMT" != "json" ] && [ "$OUT_FMT" != "text" ]; then
	echo 1>&2 "ERROR: Illegal format selected . Use either 'json' or 'text'"
	usage
fi

# required args:
ROLE_ARN=$(get_p_attr role_arn) # NOTE: cli has a cache BUT we cannot use it

if [ -z "$ROLE_ARN" ]; then
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
	if [ -z $MFA_CODE ]; then
		echo 1>&2 "ERROR: Cannot use empty code!"
		usage
	fi
	_MFA_SERIAL="--serial-number $MFA_SERIAL --token-code $MFA_CODE"
fi

TMP_CREDS_FILE=/tmp/_temp_Credentials.json

# debug
aws sts get-caller-identity
echo "we wanna be:" $ROLE_ARN
# -----

aws sts assume-role \
	--output json \
	--role-arn "$ROLE_ARN" \
	--role-session-name "$SESS_NAME" \
	$_EXT_ID $_MFA_SERIAL >$TMP_CREDS_FILE

REQ_SESS_ENCODED=$(jq -r '{ "sessionId" : .Credentials.AccessKeyId,
  "sessionKey": .Credentials.SecretAccessKey,
  "sessionToken": .Credentials.SessionToken} | @uri' \
	<$TMP_CREDS_FILE)

GET_SIGNIN_TOKEN_URL="https://signin.aws.amazon.com/federation?Action=getSigninToken&Session=${REQ_SESS_ENCODED}"

SIGNIN_TOKEN=$(curl --silent ${GET_SIGNIN_TOKEN_URL} | jq -r '.SigninToken')
CONSOLE=$(jq -nr --arg v "https://console.aws.amazon.com/" '$v|@uri')

CONSOLE_URL="https://signin.aws.amazon.com/federation?Action=login&Destination=${CONSOLE}&SigninToken=${SIGNIN_TOKEN}"

# MERGE it back out .. ready for another pipe

if [ $OUT_FMT = "text" ]; then
	jq -r "[ 
  \"export AWS_ACCESS_KEY_ID=\" + .Credentials.AccessKeyId,
  \"export AWS_SECRET_ACCESS_KEY=\" + .Credentials.SecretAccessKey,
  \"export AWS_SESSION_TOKEN=\" + .Credentials.SessionToken,
  (\"export CONSOLE_URL=$CONSOLE_URL\") ] | join(\"\n\n\") " <$TMP_CREDS_FILE
else
	jq -r '{ "Credentials" : .Credentials, "CONSOLE_URL": "'$CONSOLE_URL'" }' <$TMP_CREDS_FILE
fi
