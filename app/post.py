#!/usr/bin/env python3
# coding=utf-8

"""
@version:0.1
@author: ysicing
@file: post.py
@time: 2017/3/8 下午11:47
"""

from flask import render_template, request, url_for, Blueprint, session
from flask_moment import Moment
from flask import current_app as app
from datetime import datetime, date
from jinja2.exceptions import TemplateNotFound
from app.api import get_list,flatpages,POST_DIR,NOTES_DIR,get_comment
import os
import re
import time


blog = Blueprint('blog',__name__)


@blog.route('/posts',methods=['GET'])
def posts():
    posts = get_list()
    return render_template('posts.html',posts=posts)

@blog.route('/post/<name>',methods=['GET'])
def post(name):
    path = '{}/{}'.format(POST_DIR,name)
    #path_notes = '{}/{}'.format(NOTES_DIR,name)
    post = flatpages.get_or_404(path)
    ipost = get_list()
    postinfo = {}
    postindex = ipost.index(post)
    pre = None if postindex == 0 else ipost[postindex - 1]
    nex = None if postindex == len(ipost) -1 else ipost[postindex + 1]
    postinfo['pre'] = pre
    postinfo['nex'] = nex
    today = date.today()
    ptime = date(year=today.year,month=today.month,day=today.day)
    pl = get_comment(path)
    return render_template('post.html',post=post,ptime=ptime,posts=ipost,postinfo=postinfo,pl=pl)


@blog.route('/tag',defaults={'tag':'all'})
@blog.route('/tag/<string:tag>')
def tag(tag):
    try:
        tag = tag.lower()
    except:
        tag = ''
    allkey=[]
    tagdict={}
    print(tag)
    path = '{}/{}'.format(POST_DIR, '')
    posts = get_list()
    for xkey in posts:
        print(xkey)
        print(xkey['tags'])
        allkey.append(xkey['tags'])
    print('all:',allkey)
    for i in allkey:
        if type(i) is list:
            print('i:',i)
            for j in i:
                j=j.lower()
                tagdict[j] = tagdict.get(j,0) + 1
        elif type(i) is str:
            for j in i.split():
                j=j.lower()
                tagdict[j] = tagdict.get(j,0) + 1
        else:
            print('i+:',i,type(i))
            i = i.lower()
            tagdict[i] = tagdict.get(i,0) + 1
    print(tagdict)
    return render_template('tag.html', tagdict=tagdict, tag=tag,posts=posts)