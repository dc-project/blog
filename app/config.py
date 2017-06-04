#!/usr/bin/env python3
# coding=utf-8

"""
@version:0.1
@author: ysicing
@file: config.py
@time: 2017/2/28 下午11:41
"""

import os, random
from flask_uploads import UploadSet,IMAGES,configure_uploads,ALL

with open('.blog_secret_key','ab+') as secret:
    secret.seek(0)
    key = secret.read()
    if not key:
        key = os.urandom(64)
        try:
            secret.write(key)
            secret.flush()
        except:
            key = random.sample('01234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM!@#$%^&*', 64)
            secret.write(key)
            secret.flush()

SECRET_KEY = key
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///blog.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SESSION_FILE_DIR = "/tmp/flask_session"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True

PERMANENT_SESSION_LIFETIME = 604800     # 7 days

#HOST = "dev.ysicing.net"
#SERVER_NAME = HOST

MAILFROM_ADDR = "admail@ysicing.tech"

UPLOAD_FOLDER = os.path.normpath('static/uploads')

#ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','ico','.md'])

TEMPLATES_AUTO_RELOAD = True
SQLALCHEMY_RECORD_QUERIES = True
DEBUG_TB_INTERCEPT_REDIRECTS = False
UPLOADED_PHOTO_DEST = UPLOAD_FOLDER #os.path.dirname(os.path.abspath(__file__))
UPLOADED_PHOTO_ALLOW = IMAGES
REDIS_URL = "redis://:password@localhost:6379/0"

CACHE_TYPE = "redis"
if CACHE_TYPE == 'redis':
    CACHE_REDIS_URL = os.environ.get('REDIS_URL')

PRODUCTION = True