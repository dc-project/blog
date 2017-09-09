#!/usr/bin/env bash

gunicorn --bind 0.0.0.0:9090 -w 4 'app:create_app()'