#!/usr/bin/env python3
# coding=utf-8

"""
@version:0.1
@author: ysicing
@file: run.py
@time: 2017/2/28 下午11:25
"""

from app import create_app
import ssl

app = create_app()

ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
ctx.load_cert_chain("ssl/dev.pem", "ssl/dev.key")
app.run(host='0.0.0.0', port=9090, debug=app.debug, threaded=True, ssl_context=ctx)
