#!/bin/sh


JSON=""
while read line
do
  JSON="$JSON""$line"
done < "${1:-/dev/stdin}"

AccessKeyId(){
	echo $JSON | jq ".Credentials.AccessKeyId"
}

SecretAccessKey(){
	echo $JSON | jq ".Credentials.SecretAccessKey"
}

SessionToken(){
	echo $JSON | jq ".Credentials.SessionToken"
}
echo "export AWS_ACCESS_KEY_ID=$(AccessKeyId)
export AWS_SECRET_ACCESS_KEY=$(SecretAccessKey)
export AWS_SESSION_TOKEN=$(SessionToken)"

