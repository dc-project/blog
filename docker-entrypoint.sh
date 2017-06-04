#!/usr/bin/env bash

echo "waiting on Redis."
num=$(lsof -Pni4 | grep 6379 | wc -l | awk '{print $1}')
while(($num<1))
do
redis-server &
num=$(lsof -Pni4 | grep 6379 | wc -l | awk '{print $1}')
sleep 1;
done
echo "Running Redis ok."
gunicorn --bind 0.0.0.0:4000 -w 4 'app:create_app()'