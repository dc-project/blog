#!/usr/bin/env python3
# coding=utf-8

"""
@version:0.1
@author: ysicing
@file: blog/__init__.py 
@time: 2017/9/9 13:01
"""

import os

from flask import Flask
from jinja2 import FileSystemLoader
from sqlalchemy.engine.url import make_url
from sqlalchemy_utils import database_exists, create_database
from flask_debugtoolbar import DebugToolbarExtension

from app import utils

__version__ = '0.2'


class BlogTheme(FileSystemLoader):
    def __init__(self, searchpath, encoding='utf-8', followlinks=False):
        super(BlogTheme, self).__init__(searchpath, encoding, followlinks)
        self.overriden_templates = {}

    def get_source(self, environment, template):
        if template in self.overriden_templates:
            return self.overriden_templates[template], template, True

        if template.startswith('default/'):
            template = template.lstrip('default/')
            template = "/".join(['default', 'templates', template])
            return super(BlogTheme, self).get_source(environment, template)

        theme = utils.get_config('blog_theme') if utils.get_config('blog_theme') else 'light'
        template = "/".join([theme, 'templates', template])
        return super(BlogTheme, self).get_source(environment, template)


def create_app(config='app.config.Config'):
    app = Flask(__name__)
    with app.app_context():
        app.config.from_object(config)
        app.jinja_loader = BlogTheme(os.path.join(app.root_path, 'theme'), followlinks=True)
        app.debug = True

        from app.models import db

        url = make_url(app.config['SQLALCHEMY_DATABASE_URI'])

        if not database_exists(url):
            create_database(url)

        app.config['SQLALCHEMY_DATABASE_URI'] = str(url)

        db.init_app(app)
        utils.migrate.init_app(app, db)

        if url.drivername.startswith('sqlite'):
            db.create_all()
        else:
            pass

        app.db = db

        utils.init_errors(app)

        Debugtool = DebugToolbarExtension(app)

        from app.views import views
        from app.api import api
        from app.dash import dash
        app.register_blueprint(views)
        app.register_blueprint(api)
        app.register_blueprint(dash)

        return app