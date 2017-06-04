#!/usr/bin/env python3
# coding=utf-8

"""
@version:0.1
@author: ysicing
@file: admin.py
@time: 2017/2/28 下午11:40
"""

from flask import render_template,request,redirect,url_for,session,Blueprint,current_app,g,Response,jsonify
from app.utils import sha512,authed,admins_only,is_admin,get_config,set_config,cache,socket_families,socket_types,upload_file,allowed_file,list_file,check_value_none
from app.models import db,Config,DatabaseError,Users,Links
from itsdangerous import TimedSerializer,BadTimeSignature
from passlib.hash import bcrypt_sha256
from flask_login import  login_required,LoginManager
from werkzeug.local import LocalProxy
from app.api import LocalService,get_list,get_comment,get_comment_post,get_comment_id
import os
from datetime import datetime,timedelta
from flask_uploads import UploadSet,configure_uploads,ALL
from werkzeug.utils import secure_filename
import logging
import psutil
import socket
import uuid
import locale
from . import photos

localservice = LocalService()




admin = Blueprint('admin',__name__)
logger = logging.getLogger('web')
upload_logger = logging.getLogger('static')


#@admin.add_app_template_filter('fromtimestamp')



@admin.route('/admin',methods=['GET','POST'])
def admin_view():
    if is_admin():
        return redirect(url_for('admin.adminds'))
    return redirect(url_for('auth.oauth'))


@admin.route('/skin_config/')
def skin_config():
    return render_template('admin/skin_config.html')

@admin.route('/admin/web')
@login_required
def adminds():
    user = Users.query.filter_by(username=session.get('username')).first_or_404()
    users = Users.query.all()
    data = {
        'user':user,
        'num_user':users,
        'get_list':get_list
    }
    return render_template('admin/web.html',**data)

@admin.route('/admin/user/<name>',methods=['GET','POST'])
@admins_only
def admin_user(name):
    users = Users.query.all()
    user = Users.query.filter_by(username=session.get('username')).first_or_404()
    data = {
        'user':user,
        'name':name,
        'num_user':users
    }
    if name == 'group':
        return render_template('admin/user/ugroup.html',**data)
    elif name== 'list':
        if 'id' in request.args:
            upuser = Users.query.filter_by(id=request.args['id']).first()
            if upuser:
                return render_template('admin/user/update.html',users=upuser,**data)
        return render_template('admin/user/ulist.html',users=users,**data)
    elif name in 'useradd' :
        if request.method == 'GET':
            return render_template('admin/user/add.html',**data)
        if request.method == 'POST':
            iname = request.form.get('username')
            print(iname)
            res = Users.query.filter_by(username=iname).first()
            if res:
                return render_template('admin/user/add.html',res=res,error='已经存在',**data)
            passowrd = request.form['password']
            email = request.form['email']
            anhao = request.form['anhao']
            adduser = Users(username=iname,password=passowrd,email=email,anhao=anhao)
            adduser.admin = False
            adduser.verified = True
            adduser.avatar_hash = None
            adduser.joined = datetime.now()
            db.session.add(adduser)
            db.session.commit()
            #db.session.close()
            return render_template('admin/user/add.html',res='need update',msg='添加完成',**data)
    elif name in 'userdel':
        #if request.method == "post":
        ids = request.values.get('id','')
        for i in ids:
            if i==1:
                continue
            deluser=Users.query.filter_by(id=int(i)).first()
            db.session.delete(deluser)
        db.session.commit()
        db.session.close()
        return redirect(url_for('admin.admin_user'))
    elif name in 'update':
        uid = request.args['id']
        print(uid)
        upuser = Users.query.filter_by(id=int(uid)).first()
        if uid == 1:
            return render_template('admin/user/update.html',users=upuser,error='no allow',**data)
        passwd = request.form['password']
        email = request.form['email']
        if passwd:
            #uppasswd = Users(name=upuser.name,
            #                 password=(passwd if passwd else upuser.password),
            #                email=(email if email else upuser.email))
            upuser.password = passwd
        if email:
            upuser.email = email
        db.session.commit()
        #db.session.close()
        uppuser = Users.query.filter_by(id=uid).first()
        return render_template('admin/user/update.html',users=uppuser,msg='Update successful',**data)
    else:
        print('id=',request.args['id'])
        userinfo = Users.query.filter_by(id=request.args['id']).first()
        return render_template('admin/user/profile.html',userinfo=userinfo,**data)

@admin.route('/admin/monitor/<name>')
@admins_only
def admin_monitor(name):
    user = Users.query.filter_by(username=session.get('username')).first_or_404()

    if name == 'system':
        sysinfo=localservice.get_sysinfo()
        netifs = localservice.get_network_interfaces()#.values()
        #print(netifs,type(netifs))
        try:
            netifs.sort(key=lambda x:x.get('bytes_sent'),reverse=True)
        except:
            sorted(netifs.items(),key=lambda x: x[0][2],reverse=True)
        data = {
            'load_avg':sysinfo['load_avg'],
            'num_cpus':sysinfo['num_cpus'],
            'memory':localservice.get_memory(),
            'swap':localservice.get_swap_space(),
            'disks':localservice.get_disks(),
            'cpu':localservice.get_cpu(),
            'users':localservice.get_users(),
            'net_interfaces':netifs,
            'is_xhr':request.is_xhr,
            'user':user,
            'name':name
        }
        return render_template('admin/monitor/sys.html',**data)
    elif name == 'blog':
        netifs = localservice.get_network_interfaces()
        try:
            netifs.sort(key=lambda x:x.get('bytes_sent'),reverse=True)
        except:
            sorted(netifs.items(),key=lambda x: x[0][2],reverse=True)
        form_keys = {
            'pid': '',
            'family': socket_families[socket.AF_INET],
            'type': socket_types[socket.SOCK_STREAM],
            'state': 'LISTEN'
        }

        form_values = dict((k, request.args.get(k, default_val)) for k, default_val in form_keys.items())

        for k in ('local_addr', 'remote_addr'):
            val = request.args.get(k, '')
            if ':' in val:
                host, port = val.rsplit(':', 1)
                form_values[k + '_host'] = host
                form_values[k + '_port'] = int(port)
            elif val:
                form_values[k + '_host'] = val

        conns = localservice.get_connections(form_values)
        conns.sort(key=lambda x:x['state'])
        states = [
            'ESTABLISHED', 'SYN_SENT', 'SYN_RECV',
            'FIN_WAIT1', 'FIN_WAIT2', 'TIME_WAIT',
            'CLOSE', 'CLOSE_WAIT', 'LAST_ACK',
            'LISTEN', 'CLOSING', 'NONE'
        ]
        disks = localservice.get_disks(all_partitions=True)
        io_counters = localservice.get_disks_counters().items()
        try:
            io_counters.sort(key=lambda x: x[1]['read_count'],reverse=True)
        except:
            sorted(io_counters,key=lambda x: x[1]['read_count'],reverse=True)
        data = {
            'user':user,
            'conns':conns,
            'socket_families':socket_families,
            'socket_types':socket_types,
            'states':states,
            'num_conns':len(conns),
            'disks':disks,
            'io_counters':io_counters,
            'name':name
        }
        print(socket_families,type(socket_families))
        return render_template('admin/monitor/blog.html',**data)
    else:
        data = {
            'user':user,
            'name':name,
            'mem':localservice.get_memory(),
            'disk':localservice.get_disks(),
            'time':datetime.now()
                }
        return render_template('admin/monitor/monitor.html',**data)


@admin.route('/admin/monitor/process/<int:pid>',defaults={'section':'overview'})
@admin.route('/admin/monitor/process/<int:pid>/<string:section>')
def admin_process(pid,section):
    user = Users.query.filter_by(username=session.get('username')).first_or_404()
    valid_sections = ['overview','threads','files','connections','memory','environment','children','limits']
    if section not in valid_sections:
        return render_template('blog/errors/404.html')
    context = {
        'user':user,
        'process':localservice.get_process(pid),
        'threads':localservice.get_process_threads(pid),
        'connections':localservice.get_process_connections(pid),
        #'memory_maps':localservice.get_process_memory_maps(pid),
        'files':localservice.get_process_open_files(pid),
        'section':section,
        'pid':pid
    }


    print(pid,context,len(context))
    return render_template('admin/monitor/processes.html',**context)

@admin.route('/admin/posts/<name>',methods=['GET','POST'])
@login_required
def admin_posts(name):
    user = Users.query.filter_by(username=session.get('username')).first_or_404()
    data = {
        'user':user,
        'mdpost':get_list,
        'comment':get_comment,
        'cm':get_comment_post
    }
    if name == 'list':
        return render_template('admin/posts/plist.html',**data)
    elif name == 'comment':
        print(get_comment_post())
        if 'cid' in request.args:
            data['cm_info'] = get_comment_id(request.args.get('cid'))
            return render_template('admin/posts/scomment.html',**data)
        return render_template('admin/posts/comment.html',**data)
    elif name == 'upload':
        if request.method == "POST":
            data = request.get_data()
            print(data,type(data))
            return jsonify({'r':0,'rs':'good'})
        return render_template('admin/posts/upload.html',**data)
    else:
        if request.method == 'GET':
            return render_template('admin/posts/edit.html',**data)
        if request.method == 'POST':
            pass

@admin.route('/admin/config',methods=["GET","POST"])
@admins_only
def admin_config():
    user = Users.query.filter_by(username=session.get('username')).first_or_404()
    date = {
        'user':user,
        'blog_des':'test',
    }
    if request.method == "POST":
        blog_meta_key = set_config("blog_meta_key",request.form.get('key',None))
        #blog_icp = set_config("blog_icp",request.form.get('blog_icp',None))
        if check_value_none(request.form.get('blog_icp',None)):
            blog_icp = set_config("blog_icp",request.form.get('blog_icp'))
        if check_value_none(request.form.get('blog_name',None)):
            blog_name = set_config("blog_name", request.form.get('blog_name'))
        if check_value_none(request.form.get('blog_saying',None)):
            blog_saying = set_config("blog_saying", request.form.get('blog_saying'))
        if check_value_none(request.form.get('blog_des',None)):
            blog_desc = set_config("blog_desc", request.form.get('blog_des'))
        if check_value_none(request.form.get('key',None)):
            blog_meta_key = set_config("blog_meta_key", request.form.get('key'))
    return render_template('admin/config/config.html',**date)

@admin.route('/admin/logs')
@admins_only
def admin_logs():
    user = Users.query.filter_by(username=session.get('username')).first_or_404()
    path = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    with open(path+'/logs/log_login.log') as f:
        login_log = f.read()
    data = {
        'user': user,
        'mdpost': get_list,
        'login':login_log
    }
    return render_template('admin/logs/logs.html',**data)

"""
@admin.route('/admin/upload',methods=['POST','GET'])
def upload():
    user = Users.query.filter_by(username=session.get('username')).first_or_404()
    if request.method == 'POST':
        file = request.files['file']
        if file:
            upload_file(file=file)
    data = {
        'user':user
    }
    return render_template('admin/misc/upload.html',**data)
"""

@admin.route('/admin/upload',methods=['POST','GET'])
@admins_only
def upload():
    user = Users.query.filter_by(username=session.get('username')).first_or_404()
    data = {
        'user': user
    }
    if request.method == 'POST':
        upload_files = request.files.getlist('file[]')
        data_now = datetime.now().strftime("%Y%m%d%H%M%S")
        print(upload_files,data_now)
        for uploadfile in upload_files:
            upload_file(uploadfile)
            print(data_now,uploadfile)
            upload_logger.info("{0} upload file:{1} @{2}".format(session['username'].encode('utf-8'), uploadfile.filename,data_now))
    return render_template('admin/misc/upload.html',**data)

@admin.route('/admin/file_list',methods=['GET'])
@admins_only
def file_list():
    user = Users.query.filter_by(username=session.get('username')).first_or_404()
    data = {
        'user': user,
        'file_list':[{'name':'good','date':'666'},{'name':'bad','date':'777'}],
        'list_file':list_file()
    }
    return render_template('admin/misc/upload_list.html',**data)


@admin.route('/admin/links/<name>',methods=['GET','POST'])
@admins_only
def admin_links(name):
    links = Links.query.all()
    link_data = {
        'links':links,
        'name':name
    }
    if name in 'add' :
        if request.method == 'GET':
            return render_template('admin/links/add.html')
        if request.method == 'POST':
            lurl = request.form.get('lurl')
            print(lurl)
            llin = Links.query.filter_by(lurl=lurl).first()
            if llin:
                return render_template('admin/links/add.html',res=llin,error='链接已经存在')
            lname = request.form.get('lname')
            ldes = request.form.get('ldes')
            addlinks = Links(lurl=lurl,lname=lname,ldes=ldes)
            role = int(request.form.get('role'))
            if role == 1:
                addlinks.lrz_jy = True
            elif role == 2:
                addlinks.lrz_dx = True
            elif role == 0:
                addlinks.lrz_tx = True
            elif role == 3:
                addlinks.lrz_zzs = True

            db.session.add(addlinks)
            db.session.commit()
            #db.session.close()
            return render_template('admin/links/add.html',res='need update',msg='添加完成')
    elif name in 'del':
        #if request.method == "post":
        ids = request.values.get('id','')
        for i in ids:
            if i==1:
                continue
            dellinks=Links.query.filter_by(lid=int(i)).first()
            db.session.delete(dellinks)
        db.session.commit()
        db.session.close()
        return redirect(url_for('admin.admin_links'))
    elif name in 'update':
        lid = request.args['id']
        uplink = Links.query.filter_by(lid=int(lid)).first()
        #if lid == 1:
        #    return render_template('admin/links/update.html', uplink=uplink, error='no allow', **link_data)
        lurl = request.values.get('lurl')
        lname = request.values.get('lname')
        ldes = request.values.get('ldes')
        role = request.values.get('role')
        print(role)
        if lurl:
            uplink.lurl = lurl
        if lname:
            uplink.lname = lname
        if ldes:
            uplink.ldes = ldes
        if int(role) == 1:
            print('ok:基友')
            uplink.lrz_jy = True
            uplink.lrz_tx = False
            uplink.lrz_dx = False
        elif int(role) == 2:
            print('ok:dalao')
            uplink.lrz_jy = False
            uplink.lrz_tx = False
            uplink.lrz_dx = True
        elif int(role) == 0:
            print('ok:朋友')
            uplink.lrz_jy = False
            uplink.lrz_tx = True
            uplink.lrz_dx = False
        elif int(role) == 3:
            uplink.lrz_jy = False
            uplink.lrz_tx = False
            uplink.lrz_dx = False
            uplink.lrz_zzs = True
        print(uplink.lrz_dx,uplink.lrz_tx,uplink.lrz_jy)
        db.session.commit()
        # db.session.close()
        uplinks = Links.query.filter_by(lid=lid).first()
        return render_template('admin/links/update.html', uplink=uplinks, msg='Update successful', **link_data)
    else:
        if request.values.get('lid',''):
            uplink = Links.query.filter_by(lid=int(request.values.get('lid'))).first()
            if uplink:
                return render_template('admin/links/update.html',uplink=uplink,**link_data)

        return render_template('admin/links/links.html',**link_data)

