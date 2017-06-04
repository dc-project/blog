#!/usr/bin/env python3
# coding=utf-8

"""
@version:0.1
@author: ysicing
@file: tx.py
@time: 2017/3/24 下午4:55
"""

import urllib,hashlib

import urllib, hashlib

# Set your variables here
email = "someone@somewhere.com"
default = "https://www.example.com/default.jpg"
size = 40

# construct the url
gravatar_url = "https://www.gravatar.com/avatar/" + hashlib.md5(email.lower()).hexdigest() + "?"
gravatar_url += urllib.urlencode({'d': default, 's': str(size)})
