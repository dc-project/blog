#!/bin/bash

set -xe

[ -d "/data/project" ] || mkdir -p /data/project/blog_env

pip3 install virtualenv

virtualenv -p /usr/bin/python3.6 /data/project/blog_env

source /data/project/blog_env/bin/activate


