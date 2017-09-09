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

from flask import current_app as app, render_template, request, redirect, Blueprint, jsonify

api = Blueprint('api', __name__)

@api.route('/api/v1')
@api.route('/api/v1/<name>')
def apiv1(name=None):
    if name is None:
        apiv1 = {'info': 'api', 'version': 'v1'}
    else:
        apiv1 = {'info': name, 'version': 'v1'}
    return jsonify(apiv1)