#!/usr/bin/env python3
# coding=utf-8

"""
@version:0.1
@author: ysicing
@file: views.py
@time: 2017/2/28 下午11:40
"""

from flask import current_app as app, render_template, render_template_string, request, redirect, abort, jsonify, json as json_mod, url_for, session, Blueprint, Response, send_file
from app.models import db,Users
from jinja2.exceptions import TemplateNotFound
from collections import OrderedDict
from app.utils import is_setup,sha512,set_config,get_config,cache
from app.api import get_list
from passlib.hash import bcrypt_sha256
import logging
import hashlib
import os
import re
import sys
import json
import datetime
import time

views = Blueprint('views',__name__)

@views.before_request
def redirect_setup():
    if request.path.startswith('/static'):
        return
    if not is_setup() and request.path != "/setup":
        return redirect(url_for('views.setup'))

@views.route('/setup',methods=['GET','POST'])
def setup():
    if not is_setup():
        if not session.get('wslove'):
            session['wslove'] = sha512(os.urandom(10))
        if request.method == 'POST':
            blog_name = request.form['blog_name']
            blog_name = set_config('blog_name',blog_name)
            blog_info = request.form['blog_info']
            blog_info = set_config('blog_info',blog_info)
            username = request.form['blog_admin']
            password = request.form['password']
            email = request.form['email']
            anhao = request.form['reset_anhao']
            github = request.form['github']
            print(email)
            avatar_hash = hashlib.md5(email.encode('utf-8')).hexdigest()
            print(avatar_hash)
            first_user = Users(username=username,password=password,email=email,githubname=github,anhao=anhao,avatar_hash=avatar_hash)
            first_user.admin = True
            first_user.verified = True

            setup = set_config('setup','True')
            db.session.add(first_user)
            db.session.commit()
            db.session.close()
            logger = logging.getLogger('login')
            logger.info("[{0}] {1} 注册成功".format(time.strftime("%m/%d/%Y %X"), username.encode('utf-8')))

            app.setup = False
            with app.app_context():
                cache.clear()
            return redirect(url_for('views.static_html'))
        return render_template('setup.html',wslove=session.get('wslove'))
    return redirect(url_for('views.static_html'))


@views.route("/",defaults={'template':'home'})
@views.route("/<template>")
def static_html(template):
    try:
        if template=='home':
            posts_list=get_list()
            #print(posts_list)
            user = Users.query.filter_by(id=1).first_or_404()
            return render_template('%s.html' % template, posts_list=posts_list,user=user)
        return render_template('%s.html' % template)
    except TemplateNotFound:
        """
        是否需要判断是否存在某页面，若存在则显示，不存在则随机
        """
        abort(404)

