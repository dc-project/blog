#!/usr/bin/env python3
# coding=utf-8

"""
@version:0.1
@author: ysicing
@file: blog/dash.py 
@time: 2017/9/20 22:46
"""

from flask import Blueprint, render_template, jsonify, request
from app.plugins.dockerapi import BaseDocker
from app.plugins.monitor import Monitor

dash = Blueprint('dash', __name__)

dapi = BaseDocker(host=None, timeout=None)


@dash.route('/dash/')
def dash_index():
    return render_template('dash.html')


@dash.route('/dash/info')
def dash_docker():
    if request.values.get('docker') == 'info':
        return jsonify(dapi.docker_info())
    elif request.values.get('docker') == 'version':
        return jsonify(dapi.docker_version())
    else:
        dimages = dapi.docker_images(listimages=request.values.get('l'), num=request.values.get('num'))
        return jsonify(dimages)


@dash.route('/dash/monitor')
def dash_monitor():
    return jsonify(Monitor.logging_user_info())