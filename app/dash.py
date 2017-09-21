#!/usr/bin/env python3
# coding=utf-8

"""
@version:0.1
@author: ysicing
@file: blog/dash.py 
@time: 2017/9/20 22:46
"""

from flask import Blueprint, render_template,jsonify
from app.plugins.dockerapi import DockerApi

dash = Blueprint('dash', __name__)

docker = DockerApi(host=None, timeout=None)


@dash.route('/dash/')
def dash_index():
    return render_template('dash.html')


@dash.route('/dash/docker')
def dash_docker_info():
    return jsonify(docker.get_docker_version())