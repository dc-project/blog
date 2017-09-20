#!/usr/bin/env python3
# coding=utf-8

"""
@version:0.1
@author: ysicing
@file: blog/dash.py 
@time: 2017/9/20 22:46
"""

from flask import Blueprint, render_template

dash = Blueprint('dash', __name__)


@dash.route('/dash/')
def dash_index():
    return render_template('dash.html')