#!/usr/bin/env python3
# coding=utf-8

"""
@version:0.1
@author: ysicing
@file: __init__.py
@time: 2017/2/28 下午11:27
"""

from flask import Flask,Blueprint,render_template
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from sqlalchemy_utils import database_exists,create_database
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.engine.url import make_url
from sqlalchemy.exc import OperationalError
from jinja2 import FileSystemLoader, TemplateNotFound
from app.utils import cache,get_config,set_config
from flask_misaka import Misaka
from flask_redis import FlaskRedis
from flask_login import LoginManager
from flask_uploads import UploadSet,IMAGES,configure_uploads,ALL
from flask_analytics import Analytics

import os
import logging
import ssl




import warnings
from flask.exthook import ExtDeprecationWarning
#from flask.ext.moment import Moment
# fixed Warnings
# http://stackoverflow.com/questions/38079200/how-can-i-disable-extdeprecationwarning-for-external-libs-in-flask
warnings.simplefilter('ignore', ExtDeprecationWarning)
photos = UploadSet('PHOTO')

class BlogthemeLoader(FileSystemLoader):
    def get_source(self, environment, template):
        if template.startswith('admin/'):
            return super(BlogthemeLoader,self).get_source(environment, template)
        theme = get_config('blog_theme')
        template = "/".join([theme,template])
        return super(BlogthemeLoader,self).get_source(environment, template)

"""
theme blog load
"""

def create_app(config="app.config"):
    app = Flask(__name__)
    with app.app_context():
        app.config.from_object(config)
        app.jinja_loader = BlogthemeLoader(os.path.join(app.root_path,app.template_folder), followlinks=True)

        from app.models import db, Users

        url = make_url(app.config['SQLALCHEMY_DATABASE_URI'])
        if url.drivername == 'postgres':
            url.drivername = 'postgresql'

        db.init_app(app)

        try:
            if not (url.drivername.startswith('sqlite') or database_exists(url)):
                create_database(url)
            db.create_all()
        except OperationalError:
            db.create_all()
        else:
            db.create_all()

        app.db = db
        cache.init_app(app)
        app.cache = cache
        app.debug = False

        configure_uploads(app, photos)


        redis_store = FlaskRedis()
        redis_store.init_app(app)
        login_manager = LoginManager()
        login_manager.session_protection = 'strong'
        login_manager.login_view = 'auth.oauth'
        login_manager.init_app(app)

        toolbar = DebugToolbarExtension(app)
        #toolbar.DEBUG_TB_INTERCEPT_REDIRECTS = False
        md = Misaka()
        md.init_app(app)
        Analytics(app)
        app.config['ANALYTICS']['GAUGES']['SITE_ID'] = 'XXXXXXXXXXXXX'
        if not get_config('blog_theme'):
            set_config('blog_theme','blog')

        from app.views import views
        from app.utils import init_errors,init_utils,init_logs
        from app.post import blog
        from app.auth import auth
        from app.admin import admin
        from app.status import web
        #from app.api import
        init_errors(app)
        init_utils(app)
        init_logs(app)

        app.register_blueprint(views)
        app.register_blueprint(blog)
        app.register_blueprint(auth)
        app.register_blueprint(admin)
        app.register_blueprint(web)

        @login_manager.user_loader
        def load_user(user_id):
            try:
                return Users.query.get(int(user_id))
            except Users.DoesNotExist:
                return None
        return app