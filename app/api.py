#!/usr/bin/env python3
# coding=utf-8

"""
@version:0.1
@author: ysicing
@file: blog/api.py 
@time: 2017/9/9 13:47
"""

import re
import os
import json

from flask import current_app as app, render_template, request, redirect, Blueprint, jsonify

from app.blog import Post

api = Blueprint('api', __name__)

post = Post('.md', 'posts')


@api.route('/api/v1')
@api.route('/api/v1/<name>')
def apiv1(name=None):
    get_list = post.get_posts_list()
    d={}
    for i in get_list:
        print(i.path)
        t = i.path
        d[t] = i.meta
    if name is None:
        apiv1 = {'info': 'api', 'version': 'v1', 'post': len(get_list), 'all': str(type(get_list))}
    else:
        return jsonify(d)
    return jsonify(apiv1)