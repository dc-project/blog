#!/usr/bin/env python3
# coding=utf-8

"""
@version:0.1
@author: ysicing
@file: blog/views.py 
@time: 2017/9/9 13:10
"""

from flask import render_template,  Blueprint

views = Blueprint('views', __name__)


@views.route('/')
@views.route('/<any(index,home):path>')
def home(path=None):
    return render_template('home.html', path=path)


@views.route('/about/')
def about():
    return render_template('about.html')


@views.route('/mirrors/')
def mirrors():
    return render_template('mirrors.html')
