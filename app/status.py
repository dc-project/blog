#!/usr/bin/env python3
# coding=utf-8

"""
@version:0.1
@author: ysicing
@file: status.py
@time: 2017/5/11 22:34
"""

from flask import Blueprint,render_template,request,jsonify,redirect,url_for
from app.models import db,Users
from app.api import LocalService,get_comment_id
from app.utils import validateEmail,check_value_none
from app.models import db,Comment,Users
from datetime import datetime
import json
import os
import http.client
import re
import hashlib

web = Blueprint('web',__name__)

localservice = LocalService()


@web.route('/links')
def web_links():
    return render_template('status/links.html')

@web.route('/reading')
def web_reading():
    return 'reading'

@web.route('/status')
def web_status():
    conn = http.client.HTTPSConnection("api.uptimerobot.com")
    #payload = "api_key=u448682-ec7d7da4be34f4754aba0428&format=json"
    payload = "api_key=u448682-ec7d7da4be34f4754aba0428&format=json&customUptimeRatio=1-7-30-365&timezone=0&logs=1&response_times=0"

    #headers = {
    #    'cache-control': "no-cache",
    #    'content-type': "application/x-www-form-urlencoded"
    #}
    headers = {
        'content-type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache"
    }
    conn.request("POST", "/v2/getMonitors", payload, headers)
    res = conn.getresponse()
    data = json.loads(res.read().decode("utf-8"))
    print(type(data))
    return render_template('status/status.html',data=data)

@web.route('/monitor')
def web_monitor():
    disks = localservice.get_disks(all_partitions=True)

    data = {
        'mem': localservice.get_memory(),
        'disk': localservice.get_disks(),
        'disks':disks
    }
    return render_template('status/monitor.html',**data)

@web.route('/secret/<name>')
def web_secret(name):
    if name == 'foods':
        return 'not support'
    if name == 'lang_a_lang':
        return 'not support'

@web.route('/timeline')
def web_timeline():
    """
    登录动态 & 评论动态
    login list 为登录日志列表
    """
    login = {}
    path = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    with open(path + '/logs/log_login.log') as f:
        login_log = f.read()
    #print(login_log)
    for i in login_log.split('\n'):
        if 'logged in' in i:
            ii = i.split(' ')[0].strip('[')
            ij = i.split(' ')[1].strip(']')
            ik = i.split(' ')[2].split('\'')[1]
            login[ii+' ' +ij] = ik
    print(login)
    actions = {
        'login':login
    }
    print(login,actions,type(login),type(actions))
    return render_template('status/timeline.html',actions=actions)

@web.route('/analysis')
def web_analysis():

    return render_template('status/analysis.html')

@web.route('/about/<name>')
def web_about(name):

    return render_template('status/about.html',name=name)



@web.route('/tpush',methods=['POST'])
def web_tpush():
    #data = request.get_data().decode("utf-8")
    error = None
    res = {}
    #for i in data.split('&'):
    #    key,value = i.split('=')
    #    if key == 'cemail':
    #        value = value.decode("utf-8")#request.form['cemail']
    #    res[key] = value
    #print(data,res)
    res['cname'] = request.form['cname']
    res['cemail'] = request.form['cemail']
    res['curl'] = request.form['curl']
    res['ctext'] = request.form['text']
    res['cwz'] = request.form['path']

    cm=Comment.query.filter_by(cemail=res['cemail']).first()
    cmall=Comment.query.filter_by(cemail=res['cemail']).all()
    #print(type(cmall),cmall)
    for cmall_i in cmall:
        #print(cmall_i,type(cmall_i))
        if cmall_i.cwz == res['cwz'] and cmall_i.ctext == res['ctext'] and cmall_i.cname == res['cname']:
            return jsonify({'r':1,'error':'已经评论过了'})
    addcm = Comment(cname=res['cname'], cemail=res['cemail'], cwz=res['cwz'],ctext=res['ctext'])
    addcm.ctime = datetime.now()
    #print(cm,type(cm))
    try:
        if cm['cemail_hash']:
            addcm.cemail_hash = cm.cemail_hash
    except:
        pass
    addcm.cemail_hash = hashlib.md5(res['cemail'].encode('utf-8')).hexdigest()
    try:
        if cm.cemail_allow:
            addcm.cemail_allow = True
            db.session.add(addcm)
            db.session.commit()
            return jsonify({'r':0,'rs':'评论成功'})
    except:
        pass
    print(res)
    xss_payload = ['drop','alert','script','onload','import url','expression','meta','link','frame','iframe','onerror','onunload','onkey','onmouse']
    for i in xss_payload:
        if i in res['ctext'].lower():
            return jsonify({'r':1,'error':'评论存在风险，已经拿小本本记下来了'})
    if not validateEmail(res['cemail']):
        error = '邮件格式错误'
    if error is not None:
        return jsonify({'r': 1, 'error': error})
    addcm.cemail_allow = False
    db.session.add(addcm)
    db.session.commit()
    return jsonify({'r': 0, 'rs': '评论正在审核ing'})

@web.route('/tupdate/<name>',methods=['POST'])
def web_tupdate(name):
    if name == 'allow_comm':
        if request.method == "POST":
            cid = request.args['cid']
            upc = Comment.query.filter_by(cid=int(cid)).first()
            status = int(request.form['cemail_allow'])
            if status == 0:
                return render_template('admin/posts/scomment.html',cm_info=get_comment_id(int(cid)),msg='not update')
            if status == 1:
                upc.cemail_allow = True
                db.session.commit()
                return render_template('admin/posts/scomment.html',cm_info=get_comment_id(int(cid)),msg='update')


@web.route('/robots.txt')
def robots():
    return render_template('status/robots.txt')

@web.route('/feed/')
@web.route('/sitemap.xml')
def sitemap():
    return render_template('status/sitemap.xml')

@web.route('/reset_passwd',methods=['GET','POST'])
def get_anhao():
    if request.method == 'POST':
        user = request.form['name']
        anhao = request.form['anhao']
        email = request.form['email']
        print(user,anhao,email)
        msg = ''
        error = ''
        if check_value_none(user) and check_value_none(anhao) and check_value_none(email):
            user = Users.query.filter_by(anhao=anhao,email=email).first()
            if user:
                user.password = '12345678'
                db.session.commit()
                msg = 'new_passwd_default=12345678'
                return redirect(url_for('auth.oauth',msg=msg))
            else:
                error = '请输入正确的暗号或者邮箱，不要刻意尝试暴力哟'
        return render_template('status/reset.html',error=error)
    return render_template('status/reset.html')