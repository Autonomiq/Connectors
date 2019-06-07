#!/usr/bin/env bash
remote_port=9022
app_port=5000
chmod 400 ../autonomiq-test.pem
# Stop port if already running in machine
ssh -o StrictHostKeyChecking=no -i ../autonomiq-test.pem ubuntu@ec2-54-183-112-83.us-west-1.compute.amazonaws.com "sudo fuser -k $remote_port/tcp"
ssh -fN -o StrictHostKeyChecking=no -vv -R $remote_port:localhost:$app_port -i ../autonomiq-test.pem ubuntu@ec2-54-183-112-83.us-west-1.compute.amazonaws.com
##-f    Requests ssh to go to background just before command execution.
##-N    Do not execute a remote command.


