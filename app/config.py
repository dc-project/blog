#!/usr/bin/env python3
# coding=utf-8

"""
@version:0.1
@author: ysicing
@file: blog/config.py 
@time: 2017/9/9 13:04
"""

import os

with open('.blog_key', 'a+b') as secret:
    secret.seek(0)
    key = secret.read()
    if not key:
        key = os.urandom(64)
        secret.write(key)
        secret.flush()


class Config(object):

    '''
    sec
    '''
    SECRET_KEY = os.environ.get('SECRET_KEY') or key

    '''
    SQL DB
    '''
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{}/blog.db'.format(os.path.dirname(os.path.abspath(__file__)))
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    '''
    SESSION
    '''
    SESSION_TYPE = "filesystem"
    SESSION_FILE_DIR = "/tmp/flask_session"
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = 604800

    FLATPAGES_MARKDOWN_EXTENSIONS = ['codehilite', 'headerid']
    FLATPAGES_ROOT = 'posts'
    FLATPAGES_EXTENSION = '.md'
    FLATPAGES_AUTO_RELOAD = True
