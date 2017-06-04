#!/usr/bin/env bash

sudo apt-get update && sudo apt-get install -y apt-transport-https build-essential python3.6-dev python3-pip libffi-dev libcurl4-openssl-dev openssl redis-server
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

echo "waiting on Redis."
num=$(lsof -Pni4 | grep 6379 | wc -l | awk '{print $1}')
while(($num<1))
do
redis-server &
num=$(lsof -Pni4 | grep 6379 | wc -l | awk '{print $1}')
sleep 1;
done
echo "Running Redis ok."



