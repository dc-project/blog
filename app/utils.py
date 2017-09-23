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
import logging
import logging.handlers
import six

from flask import current_app as app, render_template
from flask_cache import Cache, make_template_fragment_key
from flask_migrate import Migrate


from app.models import db, Config


cache = Cache()
migrate = Migrate()


def init_logs(app):
    log_api = logging.getLogger('api')

    log_api.setLevel(logging.INFO)

    try:
        parent = os.path.dirname(__file__)
    except:
        parent = os.path.dirname(os.path.realpath(sys.argv[0]))

    log_dir = os.path.join(parent, 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logs = [
        os.path.join(parent, 'logs', 'log_api.log')
    ]

    for log in logs:
        if not os.path.exists(log):
            open(log, 'a').close()

    api_log = logging.handlers.RotatingFileHandler(os.path.join(parent, 'logs', 'log_api.log'), maxBytes=10000)

    log_api.addHandler(api_log)

    log_api.propagate = 0


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


@cache.memoize()
def get_config(key):
    with app.app_context():
        value = app.config.get(key)
        if value:
            if value and value.isdigit():
                return int(value)
            elif value and isinstance(value, six.string_types):
                if value.lower() == 'true':
                    return True
                elif value.lower() == 'false':
                    return False
                else:
                    return value
    config = Config.query.filter_by(key=key).first()
    if config and config.value:
        value = config.value
        if value:
            if value and value.isdigit():
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


def set_config(key, value):
    config = Config.query.filter_by(key=key).first()
    if config:
        config.value = value
    else:
        config = Config(key, value)
        db.session.add(config)
    db.session.commit()
    return config