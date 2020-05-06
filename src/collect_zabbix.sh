#!/bin/sh

IPADDR=$1
PORT=$2
KEY=$3
VALUE=`curl -s http://${IPADDR}:${PORT}/${KEY} | jq .value`

echo ${VALUE}
