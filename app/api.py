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
import logging
import time

from flask import current_app as app, render_template, request, url_for, redirect, Blueprint, jsonify
from datetime import datetime

from app.blog import Post
from app.utils import cache

api = Blueprint('api', __name__)

post = Post('.md', 'posts')

logger = logging.getLogger('api')


@api.route('/api/v1')
def api_index():
    return '''
    <html><head><title>API</title></head><body>api index</body></html>
    '''


@api.route('/api/misc/<name>')
def api_dl(name):
    if name == 'log':
        log_path = os.path.join(os.path.dirname(__file__), 'logs')
        return jsonify([(file, ''.join(i)+''.join(j)+'/'+ii) for i, j, file in os.walk(log_path) for ii in file])
    return name


'''
/api/post?tag=all
/api/post?post=all
/api/post?post=recent
/api/post?tag=tag
'''


@api.route('/api/v1/post')
def post_api():
    if request.values.get('post') == 'all':
        return jsonify({key.path: [key.meta, key.path] for key in post.get_posts_list()})
    elif request.values.get('post') == 'recent':
        logger.info("{0} {1} {2}".format(time.strftime("%Y-%m-%d %X"), request.remote_addr, request.user_agent))
        return jsonify({key.path: [key.meta, key.path] for key in post.recent_post()})
    elif request.values.get('tag') == 'all':
        return jsonify(post.get_tags())
    elif request.values.get('tag') in post.get_tags():
        return jsonify(post.get_tag(request.values.get('tag')))
    else:
        return redirect(url_for('api.api_index'))




