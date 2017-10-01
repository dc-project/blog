#!/bin/bash

set -xe

[ -d "/data/project" ] || mkdir -p /data/project/blog_env

python3.6 -m venv /data/project/blog_env

source /data/project/blog_env/bin/activate


