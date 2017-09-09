#!/usr/bin/env python3
# coding=utf-8

"""
@version:0.1
@author: ysicing
@file: blog/run.py 
@time: 2017/9/9 12:58
"""

from app import create_app

app = create_app()
app.run(debug=app.debug, threaded=True, host="0.0.0.0", port=9090)