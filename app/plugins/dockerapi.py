#!/usr/bin/env python3
# coding=utf-8

"""
@version:0.1
@author: ysicing
@file: blog/docker.py 
@time: 2017/9/21 18:17
"""

import docker


class DockerApi(object):

    def __init__(self, host, timeout):
        self.host = host if host else "unix:///var/run/docker.sock"
        self.timeout = timeout
        self.client = docker.DockerClient(base_url=self.host)

    def get_docker_version(self):
        return self.client.info()
