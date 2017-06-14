#!/usr/bin/env python3
# coding=utf-8

"""
@version:0.1
@author: ysicing
@file: api.py
@time: 2017/2/28 下午11:40
"""

from flask_frozen import Freezer
from flask_flatpages import FlatPages
from app.models import db,Users,Comment
from datetime import datetime,date
from flask import current_app as  app,abort
import os
import re
import time
import sys
import platform
import psutil
import socket
import zerorpc
from app.plugins.net.net import get_interface_addresses,NetIOCounters

try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except:
    pass

FLATPAGES_ROOT = 'content'
FLATPAGES_EXTENSION = '.md'
FLATPAGES_ENCODING = 'utf8'
FLATPAGES_AUTO_RELOAD = True
POST_DIR = 'posts'
NOTES_DIR = 'notes'
POST_PER_PAGE= 10
app.config.from_object(__name__)
flatpages = FlatPages(app)
freezer = Freezer(app)

def socket_constants(prefix):
    return dict((getattr(socket, n), n) for n in dir(socket) if n.startswith(prefix))

socket_families = socket_constants('AF_')
socket_types = socket_constants('SOCK_')

def get_list():
    try:
        posts_list = [p for p in flatpages if p.path.startwith(POST_DIR)]
    except:
        posts_list = [p for p in flatpages if p.path]
        #run this code
    try:
        posts_list.sort(key=lambda item: item['date'],reverse=True)
    except:
        posts_list = sorted(posts_list,reverse=True, key=lambda p:p['date'])
    return posts_list

#app.add_template_global(get_posts_list,'posts_lists')

class LocalService(object):

    def get_sysinfo(self):
        uptime = int(time.time() - psutil.boot_time())
        sysinfo = {
            'uptime': uptime,
            'hostname': socket.gethostname(),
            'os': platform.platform(),
            'load_avg': os.getloadavg(),
            'num_cpus': psutil.cpu_count()
        }

        return sysinfo

    def get_memory(self):
        return psutil.virtual_memory()._asdict()

    def get_swap_space(self):
        sm = psutil.swap_memory()
        swap = {
            'total': sm.total,
            'free': sm.free,
            'used': sm.used,
            'percent': sm.percent,
            'swapped_in': sm.sin,
            'swapped_out': sm.sout
        }
        return swap

    def get_cpu(self):
        return psutil.cpu_times_percent(0)._asdict()

    def get_cpu_cores(self):
        return [c._asdict() for c in psutil.cpu_times_percent(0, percpu=True)]

    def get_disks(self, all_partitions=False):
        disks = []
        for dp in psutil.disk_partitions(all_partitions):
            usage = psutil.disk_usage(dp.mountpoint)
            disk = {
                'device': dp.device,
                'mountpoint': dp.mountpoint,
                'type': dp.fstype,
                'options': dp.opts,
                'space_total': usage.total,
                'space_used': usage.used,
                'space_used_percent': usage.percent,
                'space_free': usage.free
            }
            disks.append(disk)

        return disks

    def get_disks_counters(self, perdisk=True):
        return dict((dev, c._asdict()) for dev, c in psutil.disk_io_counters(perdisk=perdisk).items())

    def get_users(self):
        return [u._asdict() for u in psutil.users()]

    def get_network_interfaces(self):
        #try:
        #    io_counters = NetIOCounters.update
        #    #print(type(io_counters))
        #except:
        #    print('666')
        io_counters = psutil.net_io_counters(pernic=True)
        addresses = get_interface_addresses()
        print(io_counters,addresses)
        netifs = {}
        for addr in addresses:
            try:
                c = io_counters.get(addr['name'])
            except:
                exit(2)
                #c = io_counters['']
            if not c:
                continue
            #print(c)
            netifs[addr['name']] = {
                'name': addr['name'],
                'ip': addr['ip'],
                'bytes_sent': c.bytes_sent,
                'bytes_recv': c.bytes_recv,
                'packets_sent': c.packets_sent,
                'packets_recv': c.packets_recv,
                'errors_in': c.errin,
                'errors_out': c.errout,
                'dropped_in': c.dropin,
                'dropped_out': c.dropout,
                #'send_rate': c.tx_per_sec
                #'recv_rate': c.rx_per_sec
            }

        return netifs

    def get_process_list(self):
        process_list = []
        for p in psutil.process_iter():
            mem = p.memory_info()

            # psutil throws a KeyError when the uid of a process is not associated with an user.
            try:
                username = p.username()
            except KeyError:
                username = None

            proc = {
                'pid': p.pid,
                'name': p.name(),
                'cmdline': ' '.join(p.cmdline()),
                'user': username,
                'status': p.status(),
                'created': p.create_time(),
                'mem_rss': mem.rss,
                'mem_vms': mem.vms,
                'mem_percent': p.memory_percent(),
                'cpu_percent': p.cpu_percent(0)
            }
            process_list.append(proc)

        return process_list

    def get_process(self, pid):
        p = psutil.Process(pid)
        mem = p.memory_info_ex()
        cpu_times = p.cpu_times()

        # psutil throws a KeyError when the uid of a process is not associated with an user.
        try:
            username = p.username()
        except KeyError:
            username = None

        return {
            'pid': p.pid,
            'ppid': p.ppid(),
            'parent_name': p.parent().name() if p.parent() else '',
            'name': p.name(),
            'cmdline': ' '.join(p.cmdline()),
            'user': username,
            'uid_real': p.uids().real,
            'uid_effective': p.uids().effective,
            'uid_saved': p.uids().saved,
            'gid_real': p.gids().real,
            'gid_effective': p.gids().effective,
            'gid_saved': p.gids().saved,
            'status': p.status(),
            'created': p.create_time(),
            'terminal': p.terminal(),
            'mem_rss': mem.rss,
            'mem_vms': mem.vms,
            #'mem_shared': mem.shared,
            #'mem_text': mem.text,
            #'mem_lib': mem.lib,
            #'mem_data': mem.data,
            'mem_info': p.memory_info(),
            'mem_percent': p.memory_percent(),
            'cwd': p.cwd(),
            'nice': p.nice(),
            #'io_nice_class': p.ionice()[0],
            #'io_nice_value': p.ionice()[1],
            'cpu_percent': p.cpu_percent(0),
            'num_threads': p.num_threads(),
            'num_files': len(p.open_files()),
            'num_children': len(p.children()),
            'num_ctx_switches_invol': p.num_ctx_switches().involuntary,
            'num_ctx_switches_vol': p.num_ctx_switches().voluntary,
            'cpu_times_user': cpu_times.user,
            'cpu_times_system': cpu_times.system
            #'cpu_affinity': p.cpu_affinity()
        }

    def get_process_limits(self, pid):
        p = psutil.Process(pid)
        return {
            'RLIMIT_AS': p.rlimit(psutil.RLIMIT_AS),
            'RLIMIT_CORE': p.rlimit(psutil.RLIMIT_CORE),
            'RLIMIT_CPU': p.rlimit(psutil.RLIMIT_CPU),
            'RLIMIT_DATA': p.rlimit(psutil.RLIMIT_DATA),
            'RLIMIT_FSIZE': p.rlimit(psutil.RLIMIT_FSIZE),
            'RLIMIT_LOCKS': p.rlimit(psutil.RLIMIT_LOCKS),
            'RLIMIT_MEMLOCK': p.rlimit(psutil.RLIMIT_MEMLOCK),
            'RLIMIT_MSGQUEUE': p.rlimit(psutil.RLIMIT_MSGQUEUE),
            'RLIMIT_NICE': p.rlimit(psutil.RLIMIT_NICE),
            'RLIMIT_NOFILE': p.rlimit(psutil.RLIMIT_NOFILE),
            'RLIMIT_NPROC': p.rlimit(psutil.RLIMIT_NPROC),
            'RLIMIT_RSS': p.rlimit(psutil.RLIMIT_RSS),
            'RLIMIT_RTPRIO': p.rlimit(psutil.RLIMIT_RTPRIO),
            'RLIMIT_RTTIME': p.rlimit(psutil.RLIMIT_RTTIME),
            'RLIMIT_SIGPENDING': p.rlimit(psutil.RLIMIT_SIGPENDING),
            'RLIMIT_STACK': p.rlimit(psutil.RLIMIT_STACK)
        }

    def get_process_environment(self, pid):
        with open('/proc/%d/environ' % pid) as f:
            contents = f.read()
            env_vars = dict(row.split('=', 1) for row in contents.split('\0') if '=' in row)
        return env_vars

    def get_process_threads(self, pid):
        threads = []
        proc = psutil.Process(pid)
        try:
            for t in proc.threads():
                thread = {
                    'id': t.id,
                    'cpu_time_user': t.user_time,
                    'cpu_time_system': t.system_time,
                }
                threads.append(thread)
        except:
            abort(404)
        return threads

    def get_process_open_files(self, pid):
        proc = psutil.Process(pid)
        return [f._asdict() for f in proc.open_files()]

    def get_process_connections(self, pid):
        proc = psutil.Process(pid)
        connections = []
        for c in proc.connections(kind='all'):
            conn = {
                'fd': c.fd,
                'family': socket_families[c.family],
                'type': socket_types[c.type],
                'local_addr_host': c.laddr[0] if c.laddr else None,
                'local_addr_port': c.laddr[1] if c.laddr else None,
                'remote_addr_host': c.raddr[0] if c.raddr else None,
                'remote_addr_port': c.raddr[1] if c.raddr else None,
                'state': c.status
            }
            connections.append(conn)

        return connections

    def get_process_memory_maps(self, pid):
        return [m._asdict() for m in psutil.Process(pid).memory_maps()]

    def get_process_children(self, pid):
        proc = psutil.Process(pid)
        children = []
        for c in proc.children():
            child = {
                'pid': c.pid,
                'name': c.name(),
                'cmdline': ' '.join(c.cmdline()),
                'status': c.status()
            }
            children.append(child)

        return children

    def get_connections(self, filters=None):
        filters = filters or {}
        connections = []

        for c in psutil.net_connections('all'):
            conn = {
                'fd': c.fd,
                'pid': c.pid,
                'family': socket_families[c.family],
                'type': socket_types[c.type],
                'local_addr_host': c.laddr[0] if c.laddr else None,
                'local_addr_port': c.laddr[1] if c.laddr else None,
                'remote_addr_host': c.raddr[0] if c.raddr else None,
                'remote_addr_port': c.raddr[1] if c.raddr else None,
                'state': c.status
            }

            for k, v in filters.items():
                if v and conn.get(k) != v:
                    break
            else:
                connections.append(conn)

        return connections

    def get_logs(self):
        available_logs = []
        for log in self.node.logs.get_available():
            try:
                stat = os.stat(log.filename)
                available_logs.append({
                    'path': log.filename.encode("utf-8"),
                    'size': stat.st_size,
                    'atime': stat.st_atime,
                    'mtime': stat.st_mtime
                })
            except OSError:
                logger.info('Could not stat "%s", removing from available logs', log.filename)
                self.node.logs.remove_available(log.filename)

        return available_logs

    def read_log(self, filename, session_key=None, seek_tail=False):
        log = self.node.logs.get(filename, key=session_key)
        if seek_tail:
            log.set_tail_position()
        return log.read()

    def search_log(self, filename, text, session_key=None):
        log = self.node.logs.get(filename, key=session_key)
        pos, bufferpos, res = log.search(text)
        stat = os.stat(log.filename)
        data = {
            'position': pos,
            'buffer_pos': bufferpos,
            'filesize': stat.st_size,
            'content': res
        }
        return data

def get_comment(path):
    cwz = path
    scc = Comment.query.filter_by(cwz=cwz).all()
    if scc:
        return scc
    return ''

def get_comment_post():
    post_cm = Comment.query.all()
    pl_info = {}
    pl_total = 0
    pl_notallow = 0
    for i in post_cm:
        pl_total += 1
        if not i.cemail_allow:
            pl_notallow += 1
    pl_info['wsh'] = pl_notallow
    pl_info['total'] = pl_total
    return pl_info

def get_comment_id(cid):
    cm_info = Comment.query.filter_by(cid=cid).first()
    return cm_info

def get_tags():
    allkey = []
    tagdict = {}
    path = '{}/{}'.format(POST_DIR, '')
    posts = get_list()
    for xkey in posts:
        allkey.append(xkey['tags'])
    #print('all:', allkey)
    for i in allkey:
        if type(i) is list:
            print('i:', i)
            for j in i:
                j = j.lower()
                tagdict[j] = tagdict.get(j, 0) + 1
        elif type(i) is str:
            for j in i.split():
                j = j.lower()
                tagdict[j] = tagdict.get(j, 0) + 1
        else:
            #print('i+:', i, type(i))
            i = i.lower()
            tagdict[i] = tagdict.get(i, 0) + 1
    #print(type(tagdict))
    return sorted(tagdict.items(), key=lambda x: x[1],reverse=True)

try:
    app.add_template_global(get_tags, 'get_tags')
except:
    pass