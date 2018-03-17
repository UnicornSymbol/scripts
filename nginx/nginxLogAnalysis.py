#!/usr/bin/env python
#-*- coding: utf-8 -*-

import re
import os,sys
import gzip
import time
import queue
import argparse
import datetime
import threading
from collections import namedtuple
from pyh import *

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--starttime', dest='starttime', help='the start time of log analysis. format:yymmddHHMMSS')
parser.add_argument('-e', '--endtime', dest='endtime', help='the end time of log analysis. format:yymmddHHMMSS')
args = parser.parse_args()

try:
    starttime = datetime.datetime.strptime(args.starttime,'%Y%m%d%H%M%S')
    endtime = datetime.datetime.strptime(args.endtime,'%Y%m%d%H%M%S')
except ValueError as e:
    print(e)
    sys.exit(1)
except TypeError as e:
    print("please input starttime and endtime argument!")
    sys.exit(2)
except Exception as e:
    print(e)
    sys.exit(3)

log_path_list = [
    '.',
    './nginx',
]
matcher = re.compile(r'(?P<remote>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - - \[(?P<time>.*)\ .*] "(?P<request>.*)" (?P<status>\d+) (?P<length>\d+) ".*" "(?P<ua>.*)"')
# www.hx9999.com.access.log-20170202.gz
file_name_pattern = re.compile(r'.*-(?P<time>\d{8})\.(?P<type>.*)')
Request = namedtuple('Request', ['method', 'url', 'version'])
mapping = {
    'length': int,
    'request': lambda x: Request(*x.split()),
    'status': int, 
    'time': lambda x: datetime.datetime.strptime(x, '%d/%b/%Y:%H:%M:%S')
}
status = {}
lock = threading.Lock()
file_list = []

class FileLoad(object):
    def __init__(self, path):
        self.path = path

    def extract(self, line):
        m = matcher.match(line)
        if m:
            ret = m.groupdict()
            return {k: mapping.get(k, lambda x: x)(v) for k, v in ret.items()}
        raise Exception(line)

    def read(self, f):
        for line in f:
            if isinstance(line, bytes):
                try:
                    line = line.decode()
                except UnicodeDecodeError:
                    pass
            try:
                yield self.extract(line)
            except:
                pass
                #print(line)


    def load(self):
        with open(self.path) as f:
            yield from self.read(f)

    def load_gz(self):              # 读取后内容是bytes格式
        with gzip.open(self.path) as f:
            yield from self.read(f)

class Analyser(object):
    def __init__(self,handler):
        self.handler = handler

    def start(self, source):
        #print(threading.currentThread().getName())
        self.handler(source)

class Dispatcher(object):
    def __init__(self, source):
        self.analysers = []
        self.queues = []
        self.source = source

    def _source(self, q):
        while True:
            #print('_source')
            try:
                yield q.get(timeout=1)
            except queue.Empty:
                break

    def register(self, handler):
        q = queue.Queue()
        self.queues.append(q)
        analyser = Analyser(handler)
        t = threading.Thread(target=analyser.start, args=(self._source(q),))
        self.analysers.append(t)

    def start(self):
        for t in self.analysers:
            t.setDaemon(True)
            t.start()
        for item in self.source:
            #print(item)
            for q in self.queues:
                q.put(item)

    def join(self):
        for t in self.analysers:
            t.join()

def status_handler(source):
    #print('status_handler')
    global status
    global lock
    global starttime
    global endtime
    for item in source:
        if item['time'] > starttime and item['time'] <= endtime:
            if item['status'] not in status.keys():
                lock.acquire()
                status[item['status']] = 0
                lock.release()
            lock.acquire()
            status[item['status']] += 1
            lock.release()

def get_file_list(path):
    global starttime
    global endtime
    global file_list
    if starttime >= endtime:
        print("starttime must less than endtime")
        sys.exit(4)
    current = datetime.datetime.now()
    if endtime > current:
        endtime = current
    for name in os.listdir(path):
        f = file_name_pattern.match(name)
        if f:
            ret = f.groupdict()
            time = datetime.datetime.strptime(ret['time'], '%Y%m%d')
            if time >= starttime and time <= endtime+datetime.timedelta(days=1):
                file_list.append(os.path.join(path, name))
    if endtime.date() == current.date():
        current_access_log = os.path.join(path, 'access.log')
        current_error_log = os.path.join(path, 'error.log')
        if os.path.exists(current_access_log):
            file_list.append(current_access_log)
        if os.path.exists(current_error_log):
            file_list.append(current_error_log)

def create_html():
    flag = 0
    time_str = starttime.strftime('%Y/%m/%d %H:%M:%S')+'-'+endtime.strftime('%Y/%m/%d %H:%M:%S')
    page = PyH('Status')
    page<<div(style="text-align:center")<<h4('Nginx Status Code Count')
    mytab = page << table(border="1",cellpadding="3",cellspacing="0",style="margin:auto")
    tr1 = mytab << tr(bgcolor="lightgrey")
    tr1 << th('period')+th('status_code')+th('count')
    for s in sorted(status.items(), key=lambda x:x[0]):
        tr2 = mytab << tr()
        if flag == 0:
            tr2 << td(time_str)
            tr2[0].attributes['rowspan']=len(status)
            flag = 1
        for j in range(3):
            if j > 0:
                tr2 << td(s[j-1])
    page.printOut('status_code.html')
    
def main():
    dispatchers = []
    for path in log_path_list:
        if os.path.isdir(path):
            get_file_list(path)
        else:
            print("{} is not a directory.".format(path))
    if not file_list:
        print("this period have no log!")
        return
    for f in file_list:
        file_load = FileLoad(f)
        if f.endswith('.log'):
            dispatcher = Dispatcher(file_load.load())
            dispatcher.register(status_handler)
            dispatchers.append(dispatcher)
        if f.endswith('.gz'):
            dispatcher = Dispatcher(file_load.load_gz())
            dispatcher.register(status_handler)
            dispatchers.append(dispatcher)
    #print(file_list)
    #print(dispatchers)
    for d in dispatchers:
        d.start()
    for d in dispatchers:
        d.join()
    create_html()
    #for code, count in sorted(status.items(), key=lambda x:x[0]):
    #    print('{}: {}'.format(code,count))

if __name__ == '__main__':
    main()
