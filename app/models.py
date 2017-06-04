#!/usr/bin/env python3
# coding=utf-8

"""
@version:0.1
@author: ysicing
@file: models.py
@time: 2017/2/28 下午11:40
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import DatabaseError
from sqlalchemy.sql import func
from socket import inet_aton, inet_ntoa
from struct import unpack, pack, error as struct_error
from passlib.hash import bcrypt_sha256
from flask import current_app as app
from flask import request
from flask_login import UserMixin
from flask_login import LoginManager
#from flask_security import RoleMixin
login_manager = LoginManager()
#from . import login_manager

import datetime
import hashlib
import json

db = SQLAlchemy()



class Users(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(128),unique=True,index=True)
    githubname = db.Column(db.String(128),unique=True,index=True)
    email = db.Column(db.String(128),unique=True,index=True)
    anhao = db.Column(db.TEXT)
    password = db.Column(db.String(128))
    verified = db.Column(db.BOOLEAN,default=False)
    admin = db.Column(db.BOOLEAN,default=False)
    joined = db.Column(db.DATETIME,default=datetime.datetime.now)
    last_login = db.Column(db.DATETIME,default=datetime.datetime.now)
    avatar_hash  = db.Column(db.String(32))
    pro_logo = db.Column(db.String(128),default='/static/comm/img/profile.jpg')
    pro_name = db.Column(db.String(128),default='YsiCing Zheng')
    pro_des = db.Column(db.String(128),default='The quieter you become, the more you can hear.')

    '''
    刷新最后登录时间
    '''
    def ping(self):
        self.last_login = datetime.datetime.now()
        db.session.add(self)
        print(self.last_login)
        db.session.commit()
        return True
    '''
    头像问题
    '''
    def change_email(self,token):
        self.email = token
        self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True

    def gravatar(self,size=100,default='identicon',rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'https://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url,hash=hash,size=size,default=default,rating=rating)

    def __repr__(self):
        return '<User %r>' % self.username

class DSF(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), unique=True)
    name = db.Column(db.String(120))

    def __init__(self, login, name):
        self.login = login
        self.name = name

    def __repr__(self):
        return '<User %r>' % self.login

    @staticmethod
    def get_or_create(login, name):
        user = DSF.query.filter_by(login=login).first()
        if user is None:
            user = DSF(login, name)
            db.session.add(user)
            db.session.commit()
        return user

class Config(db.Model):
    cid = db.Column(db.INTEGER,primary_key=True)
    key = db.Column(db.TEXT)
    value = db.Column(db.TEXT)

    def __init__(self,key,value):
        self.key = key
        self.value = value


class Links(db.Model):
    #__table__ = 'links_friends'
    lid = db.Column(db.INTEGER,primary_key=True)
    lurl = db.Column(db.String(128),unique=True)
    lname = db.Column(db.String(128))
    ldes = db.Column(db.String(128))
    lrz_jy = db.Column(db.BOOLEAN,default=False)
    lrz_tx = db.Column(db.BOOLEAN,default=False)
    lrz_dx = db.Column(db.BOOLEAN,default=False)
    lrz_zzs = db.Column(db.BOOLEAN,default=False)

    def __init__(self,lurl,lname,ldes):
        self.lurl = lurl
        self.lname = lname
        self.ldes = ldes

class Comment(db.Model):
    cid = db.Column(db.INTEGER,primary_key=True)
    cwz = db.Column(db.String(128))
    cname = db.Column(db.String(128))
    cemail = db.Column(db.String(128))
    ctime = db.Column(db.DATETIME,default=datetime.datetime.now)
    cemail_allow = db.Column(db.BOOLEAN,default=False)
    ctext = db.Column(db.String(300))
    cemail_hash = db.Column(db.String(128))

    def __init__(self,cwz,cname,cemail,ctext):
        self.cwz = cwz
        self.cname = cname
        self.cemail = cemail
        self.ctext = ctext

    def gravatar(self,size=100,default='identicon',rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'https://www.gravatar.com/avatar'
        hash = self.cemail_hash or hashlib.md5(self.cemail.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url,hash=hash,size=size,default=default,rating=rating)
