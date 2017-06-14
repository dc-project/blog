#!/usr/bin/env python3
# coding=utf-8

"""
@version:0.1
@author: ysicing
@file: utils.py
@time: 2017/2/28 下午11:40
"""

from flask import current_app as app,g,redirect,request,url_for,session,render_template,abort
from app.models import db,Config,Users,Links
from jinja2 import filters
from sqlalchemy.engine.url import make_url
from sqlalchemy import create_engine
from flask_cache import Cache
import logging
import logging.handlers
import hashlib
from six.moves.urllib.parse import urlparse, urljoin
import six
import socket
from six import moves
from werkzeug.utils import secure_filename
from functools import wraps
from itsdangerous import Signer,BadSignature
from datetime import datetime
#from app.api import get_tags
import time
import os
import sys
import re
import requests
cache = Cache()
import short_url
"""
error
"""

def init_logs(app):
    log_login = logging.getLogger('login')
    log_web = logging.getLogger('web')
    log_qps = logging.getLogger('qps')
    log_static = logging.getLogger('static')

    log_login.setLevel(logging.INFO)
    log_web.setLevel(logging.INFO)
    log_qps.setLevel(logging.INFO)
    log_static.setLevel(logging.INFO)

    try:
        parent = os.path.dirname(__file__)
    except:
        parent = os.path.dirname(os.path.realpath(sys.argv[0]))

    log_dir = os.path.join(parent,'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logs = [
        os.path.join(parent,'logs','log_login.log'),
        os.path.join(parent,'logs','log_web.log'),
        os.path.join(parent,'logs','log_qps.log'),
        os.path.join(parent,'logs','log_static.log')
    ]

    for log in logs:
        if not os.path.exists(log):
            open(log,'a').close()

    login_log = logging.handlers.RotatingFileHandler(os.path.join(parent, 'logs', 'log_login.log'), maxBytes=10000)
    web_log = logging.handlers.RotatingFileHandler(os.path.join(parent, 'logs', 'log_web.log'), maxBytes=10000)
    qps_log = logging.handlers.RotatingFileHandler(os.path.join(parent, 'logs', 'log_qps.log'), maxBytes=10000)
    static_log = logging.handlers.RotatingFileHandler(os.path.join(parent, 'logs', 'log_static.log'), maxBytes=10000)

    log_login.addHandler(login_log)
    log_web.addHandler(web_log)
    log_qps.addHandler(qps_log)
    log_static.addHandler(static_log)

    login_log.propagate = 0
    log_qps.propagate = 0
    log_web.propagate = 0
    log_static.propagate = 0


def init_errors(app):
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('errors/404.html'),404

    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'),403

    @app.errorhandler(500)
    def net_error(error):
        return render_template('errors/500.html'),500

    @app.errorhandler(502)
    def gate_error(error):
        return render_template('errors/502.html'),502


def init_utils(app):
    try:
        user = Users.query.filter_by(id=1).first_or_404()
        app.jinja_env.globals.update(user=user)
    except:
        user = Users.query.filter_by(id=1).first()
        app.jinja_env.globals.update(user=user)
    app.jinja_env.globals.update(blog_name=blog_name)
    app.jinja_env.globals.update(get_version=get_version)
    app.jinja_env.globals.update(blog_icp=blog_icp)
    app.jinja_env.globals.update(blog_meta_key=blog_meta_key)
    app.jinja_env.globals.update(link_zzs=get_zzs)

@cache.memoize()
def is_setup():
    setup = Config.query.filter_by(key='setup').first()
    if setup:
        return setup.value
    else:
        return False

def sha512(strcode):
    return hashlib.sha512(strcode).hexdigest()

@cache.memoize()
def get_config(key):
    config = Config.query.filter_by(key=key).first()
    try:
        if config and config.value:
            value = config.value
            if value and value.isdigit():  #isdigit num yes or no
                return int(value)
            elif value and isinstance(value, six.string_types):
                if value.lower() == 'true':
                    return True
                elif value.lower() == 'false':
                    return False
                else:
                    return value
        else:
            set_config(key, None)
            return None
    except:
        print('error')

def set_config(key,value):
    config = Config.query.filter_by(key=key).first()
    if config:
        config.value = value
    else:
        config = Config(key,value)
        db.session.add(config)
    db.session.commit()
    return config

@cache.memoize()
def blog_name():
    name = get_config('blog_name')
    return name if name else 'Blog'


@cache.memoize()
def blog_icp():
    icp = get_config('blog_icp')
    return icp if icp else '京ICP 666666'

#@cache.memoize()
def blog_meta_key():
    key = get_config('blog_meta_key')
    return key if key else ''

def authed():
    return bool(session.get('id', False))

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(request.host_url, target)
    return test_url.scheme in ('http','https') and ref_url.netloc == test_url.netloc

def is_admin():
    if authed():
        return session['admin']
    else:
        return False

def admins_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('admin'):
            return f(*args, **kwargs)
        else:
            return redirect(url_for('auth.oauth'))
    return decorated_function

def get_themes():
    dir = os.path.join(app.root_path, app.template_folder)
    return [name for name in os.listdir(dir)
            if os.path.isdir(os.path.join(dir, name)) and name != 'admin']


def socket_constants(prefix):
    return dict((getattr(socket, n), n) for n in dir(socket) if n.startswith(prefix))

socket_families = socket_constants('AF_')
socket_types = socket_constants('SOCK_')

def fromtimestamp(value, dateformat='%Y-%m-%d %H:%M:%S'):
    dt = datetime.fromtimestamp(int(value))
    return dt.strftime(dateformat)

try:
    app.add_template_global(fromtimestamp,'fromtimestamp')
except:
    filters.FILTERS['fromtimestamp'] = fromtimestamp

def timesince(dt,default='just now',past_="ago",future_="from now"):
    #now = datetime.utcnow()
    now = time.strftime("%Y-%m-%d %X")
    if isinstance(now,str):
        now = datetime.strptime(now,'%Y-%m-%d %H:%M:%S')
    if isinstance(dt,str) :
        dt = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
    #print(dt,type(dt),type(now))
    if now > dt:
        diff = now - dt
        dt_is_past = True
    else:
        diff = dt - now
        dt_is_past = False

    #diff = now - dt
    #print(diff,diff.days,diff.seconds)
    periods = (
        (int(diff.days) / 365,"year", "years"),
        (int(diff.days) / 30,"month","months"),
        (int(diff.days) / 7,"week","weeks"),
        (int(diff.days),"day", "days"),
        (int(diff.seconds) / 3600, "hour", "hours"),
        (int(diff.seconds) / 60, "minute", "minutes"),
        (int(diff.seconds), "second", "seconds"),
    )
    for period,singular,plural in periods:
        print(period,singular,plural)
        if period :
            return "%d %s %s" % (period, singular if period == 1 else plural,past_ if dt_is_past else future_)
    return default

try:
    app.add_template_global(timesince,'timesince')
except:
    filters.FILTERS['timesince'] = timesince

@cache.memoize()
def get_version():
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    try:
        with open(path+'/VERSION') as f:
            version=f.read().strip()
    except:
        version='v4.0.2.1_test'
    print(path,version)
    return version


def get_file_md5(f,chunk_size=8192):
    h = hashlib.md5()
    while True:
        chunk = f.read(chunk_size)
        if not chunk:
            break
        h.update(chunk)
    return h.hexdigest()

def check_value_none(value):
    if value:
        return True
    else:
        return False

def allowed_file(file):
    pass
    #return '.' in file and file.rsplit('.',1)[1] in AllOWED_EXTENSIONS

def upload_file(file):
    filename = secure_filename(file.filename)
    if len(filename) <= 0:
        return False

    md5hash = hashlib.md5(os.urandom(64)).hexdigest()

    upload_folder = os.path.join(os.path.normpath(app.root_path),app.config['UPLOAD_FOLDER'])
    if not os.path.exists(os.path.join(upload_folder,md5hash)):
        os.makedirs(os.path.join(upload_folder,md5hash))
    print(file,filename,upload_folder)
    fullfile = md5hash+'.'+filename
    file.save(os.path.join(upload_folder,md5hash,fullfile))
    set_config(md5hash,md5hash+'/'+fullfile)
    return True

def list_file():
    upload_folder = os.path.join(os.path.normpath(app.root_path),app.config['UPLOAD_FOLDER'])
    file_dict = {}
    for dirpath,dirnames,filenames in os.walk(upload_folder):
        for filename in filenames:
            fp = dirpath + '/' + filename
            if os.path.exists(fp):
                fsize = os.path.getsize(fp)
                fctime = os.path.getctime(fp)
                fmtime = os.path.getmtime(fp)
                fhash = filename.split('.')[0]
                furl = '/'+app.config['UPLOAD_FOLDER']+'/'+fhash+'/'+filename
                print(filename)
                file_dict[str(fp)] = {'dirname':dirpath,'fsize':fsize,'fctime':fctime,'fmtime':fmtime,'fhash':fhash,'furl':furl}

    print(file_dict)
    return file_dict

def get_zzs():
    #link = Links.query.filter_by(lrz_zzs=True).all()
    link = Links.query.all()

    return link

def validateEmail(email):
    if len(email) > 7:
        if re.match("^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$",email)!=None:
            return True
    return False