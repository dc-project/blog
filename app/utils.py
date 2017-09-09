#!/usr/bin/env python3
# coding=utf-8

"""
@version:0.1
@author: ysicing
@file: blog/utils.py 
@time: 2017/9/9 14:09
"""

import os
import sys

from flask import current_app as app, render_template
from flask_cache import Cache
from flask_migrate import Migrate


cache = Cache()
migrate = Migrate()

def init_errors(app):
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('_error/404.html'),404

    @app.errorhandler(403)
    def forbidden(error):
        return render_template('_error/403.html'), 403

    @app.errorhandler(500)
    def general_error(error):
        return render_template('_error/500.html'), 500

    @app.errorhandler(502)
    def gateway_error(error):
        return render_template('_error/502.html'), 502


def override_template(template, html):
    with app.app_context():
        app.jinja_loader.overriden_templates[template] = html


def get_config(key):
    with app.app_context():
        return False

def set_config(key, value):
    pass