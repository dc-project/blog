#!/usr/bin/env python3
# coding=utf-8

"""
@version:0.1
@author: ysicing
@file: blog/blog.py 
@time: 2017/9/10 22:46
"""

from flask_frozen import Freezer
from flask_flatpages import FlatPages
from flask import current_app as app, jsonify

flatpages = FlatPages(app)
freezer = Freezer(app)


class Post(object):
    def __init__(self, ext,post_dir):
        self.ext = ext
        self.post_dir = post_dir

    def get_posts_list(self):
        try:
            posts = [post for post in flatpages if post.path.startwith(self.post_dir)]
        except:
            posts = [post for post in flatpages if post.path]
        try:
            posts.sort(key=lambda item: item['date'],reverse=True)
        except:
            posts = sorted(posts, reverse=True, key=lambda post:post['date'])
        return posts

    def recent_post(self):
        posts = self.get_posts_list()
        if len(posts) >= 10:
            recent_post = posts[:10]
        else:
            recent_post = posts
        return recent_post

    def get_tags(self):
        posts = self.get_posts_list()
        allkey = []
        xkey = {}
        path = '{}/{}'.format(self.post_dir, '')
        for post in posts:
            allkey.append(post['tags'])
        for i in allkey:
            if type(i) is list:
                for j in i:
                    j = j.lower()
                    xkey[j] = xkey.get(j, 0) + 1
            elif type(i) is str:
                for j in i.split():
                    j = j.lower()
                    xkey[j] = xkey.get(j, 0) + 1
            else:
                i = i.lower()
                xkey[i] = xkey.get(i, 0) + 1

        return xkey

    def get_tag(self, tag):
        """
        :param tag:
        :return: tag相关的文章列表
        """

        tag = tag.lower()
        taginfo = {}
        taginfo['tag_num'] = self.get_tag()['tag']
        for post in self.get_posts_list():
            if tag in post.tags.lower():
                pass
        return jsonify(taginfo)


