import re
import queue
import datetime
import threading
from collections import namedtuple


matcher = re.compile(r'(?P<remote>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - - \[(?P<time>.*)\] "(?P<request>.*)" (?P<status>\d+) (?P<length>\d+) ".*" "(?P<ua>.*)"')
Request = namedtuple('Request', ['method', 'url', 'version'])
mapping = {
    'length': int,
    'request': lambda x: Request(*x.split()),
    'status': int,
    'time': lambda x: datetime.datetime.strptime(x, '%d/%b/%Y:%H:%M:%S %z')
}


def extract(line):
    m = matcher.match(line)
    if m:
        ret = m.groupdict()
        return {k:mapping.get(k, lambda x:x)(v) for k, v in ret.items()}
    raise Exception(line)


def load(path):
    with open(path) as f:
        try:
            yield extract(f.readline())
        except:
            pass


def window(source, handler, interval: int, width: int):
    store = []
    start = datetime.datetime.now()
    while True:
        data = next(source)
        current = datetime.datetime.now()
        if data:
            store.append(data)
            current = data['time']
        if (current - start).total_seconds() >= interval:
            start = current
            handler(store)
            dt = current - datetime.timedelta(seconds=width)
            store = [x for x in store if x['time'] > dt]


def dispatcher(source):
    analyers = []
    queues = []

    def _source(q):
        while True:
            yield q.get()

    def register(handler, interval, width):
        q = queue.Queue()
        queues.append(q)
        t = threading.Thread(target=window, args=(_source(q), handler, interval, width))
        analyers.append(t)

    def start():
        for t in analyers:
            t.start()
        for item in source:
            print(item)
            for q in queues:
                q.put(item)

    return register, start


def null_handler(items):
    pass


if __name__ == '__main__':
    import sys
    register, start = dispatcher(load(sys.argv[1]))
    register(null_handler, 5, 10)
    start()