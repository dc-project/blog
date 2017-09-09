#!/usr/bin/env python3
# coding=utf-8

"""
@version:0.1
@author: ysicing
@file: blog/views.py 
@time: 2017/9/9 13:10
"""

import re
import os

from flask import current_app as app, render_template, request, redirect, Blueprint, jsonify

views = Blueprint('views', __name__)


@views.route('/')
@views.route('/<any(index,home):path>')
def home(path=None):
    return render_template('home.html')


@views.route('/test')
def test():
    return render_template('test/test.html')