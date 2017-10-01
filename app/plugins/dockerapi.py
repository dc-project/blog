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


class BaseDocker(DockerApi):

    def docker_info(self):
        return self.client.info()

    def docker_version(self):
        return self.client.version()

    def docker_images(self, listimages=False, num=True):
        images = self.client.images.list()
        images_dict = {}
        for image in images:
            images_dict[image.short_id] = {'tag': image.tags[0], 'id': image.id}
        if num and not listimages:
            return len(images)
        elif listimages and not num:
            return images_dict
        else:
            images_dict['total'] = len(images)
            return images_dict

