#!/usr/bin/env python3
# coding=utf-8

"""
@version:0.1
@author: ysicing
@file: blog/monitor.py
@time: 2017/9/26 23:39
"""

import psutil
import time


class Monitor(object):

    @classmethod
    def logging_user_info(cls):
        logging_user_list = []
        for user in psutil.users():
            user_dict = {}
            user_dict["name"] = user.name
            user_dict["terminal"] = user.terminal
            user_dict["host"] = user.host
            user_dict["started"] = user.started
            logging_user_list.append(user_dict)

        return logging_user_list