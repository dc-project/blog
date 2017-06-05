#!/usr/bin/env python3
# coding=utf-8

"""
@version:0.1
@author: ysicing
@file: auth.py
@time: 2017/2/28 下午11:40
"""

from flask import render_template,render_template_string,flash,request,redirect,abort,url_for,session,Blueprint
from app.models import db,Users,Auth
from itsdangerous import TimedSerializer,BadTimeSignature
from app.utils import sha512,authed,get_config,is_safe_url
from passlib.hash import bcrypt_sha256
from passlib.apps import custom_app_context as pwd_context
from flask import current_app as app
#from flask_security import Security
from flask_login import login_user,current_user
import logging
from rauth.service import OAuth2Service
import time
from datetime import datetime
import os

auth = Blueprint('auth',__name__)
#Security(app)

github = OAuth2Service(
    name='github',
    base_url='https://api.github.com/',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    client_id= '',
    client_secret= '',
)

@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.verified and request.endpoint[:5]!='auth.':
            return render_template_string('没有验证，联系管理员')

@auth.route('/oauth',methods=['POST','GET'])
def oauth():
    if request.method == 'POST':
        errors = []
        name = request.form['name']
        iname = Users.query.filter_by(username=name).first()
        if iname:
            try:
                status = bcrypt_sha256.verify(request.form['password'],iname.password)
            except:
                hash = pwd_context.encrypt(request.form['password'])
                status = pwd_context.verify(iname.password,hash)
            if status:
                try:
                    session.regenerate()
                except:
                    pass
                session['username'] = iname.username
                session['id'] = iname.id
                session['admin'] = iname.admin
                session['nonce'] = sha512(os.urandom(10))
                login_user(iname,False) #False close brow
                db.session.close()
                logger = logging.getLogger('login')
                #time datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                logger.info("[{0}] {1} logged in.IP:{2} UG:{3}".format(time.strftime("%Y-%m-%d %X"), session['username'].encode('utf-8'),request.remote_addr,request.user_agent))

                if request.args.get('next') and is_safe_url(request.args.get('next')):
                    return redirect(request.args.get('next'))
                return redirect(url_for('admin.adminds'))

            else:
                errors.append("Incorrect Username or password .")
                db.session.close()
                return render_template('login.html', errors=errors)
        else:
            errors.append("Not exist or Forbidden")
            db.session.close()
            return render_template('login.html', errors=errors)
    else:
        db.session.close()
        return render_template('login.html')

@auth.route('/logout')
def logout():
    if authed():
        outlog = logging.getLogger('login')
        outlog.info("[{0}] {1} logout".format(time.strftime("%Y-%m-%d %X"), session['username'].encode('utf-8')))
        session.clear()
    return redirect(url_for('views.static_html'))

@auth.route('/oauth/github')
def oaurh_github():
    redirect_uri = url_for('auth.oauth_github_call', next=request.args.get('next') or
        request.referrer or None, _external=True)
    print(redirect_uri)
    # More scopes http://developer.github.com/v3/oauth/#scopes
    params = {'redirect_uri': redirect_uri, 'scope': 'user:email'}
    print(params)
    print(github.get_authorize_url(**params))
    return redirect(github.get_authorize_url(**params))

@auth.route('/oauth/callback')
def oauth_github_call():
    if not 'code' in request.args:
        flash('Not authorize')
        return redirect(url_for('auth.oauth'))
    redirect_url = url_for('auth.oauth_github_call', _external=True)
    data = dict(
        code = request.args['code'],
        redirect_url = redirect_url,
        scope = 'user:email,public_repo'
    )
    auth = github.get_auth_session(data=data)
    respon = auth.get('user').json()
    user = Auth.get_or_create(respon['login'],respon['name'])
    session['token'] = auth.access_token
    session['user_id'] = user.id
    flash('Logged in as' + respon['name'])
    return redirect(url_for('auth.auth_test'))

@auth.route('/oauth/test')
def auth_test():
    if session.get('token'):
        print(session['token'])
        auth = github.get_session(token = session['token'])
        resp = auth.get('/user')
        if resp.status_code == 200:
            #user = resp.json()
            #redirect()
            try:
                iname = Users.query.filter_by(githubname=resp.json()['name']).first()
                if iname:
                    session['username'] = iname.username
                    session['id'] = iname.id
                    session['admin'] = iname.admin
                    session['nonce'] = sha512(os.urandom(10))
                    login_user(iname, False)  # False close brow
                    db.session.close()
                    logger = logging.getLogger('login')
                    logger.info("[{0}] {1} logged in.IP:{2} UG:{3} By GitHub".format(time.strftime("%Y-%m-%d %X"),
                                                                           session['username'].encode('utf-8'),
                                                                           request.remote_addr, request.user_agent))
                    return  redirect(url_for('admin.adminds'))
            except:
                print("iname error")
        return render_template('github.html',user=resp.json())
    else:
        return redirect(url_for('auth.oauth'))

@auth.route('/oauth/wechat')
def oauth_wechat():
    wx = '<h2>Sorry,We not support Wechat now. By {{ god }}</h2>' \
         '<br> 主要是微信审核太麻烦了，后期支持Google或者推特'
    return render_template_string(wx,god='ysicing')