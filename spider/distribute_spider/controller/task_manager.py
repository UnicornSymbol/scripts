#coding:utf-8

import time
#from queue import Queue   #Queue必须用multiprocessing模块中的Queue，否则控制节点和爬虫节点不能互相传输数据
#Queue是进程内非阻塞队列，multiprocess.Queue是跨进程通信队列。多进程前者是各自私有，后者是各子进程共有。
from multiprocessing.managers import BaseManager
from multiprocessing import Queue,Process
from url_manager import UrlManager
from data_output import DataOutput

class TaskManager(object):
    def start_manager(self,url_q,result_q):
        print(url_q)
        BaseManager.register('get_task_queue',callable=lambda:url_q)
        BaseManager.register('get_result_queue',callable=lambda:result_q)
        manager = BaseManager(address=('',8001),authkey=b'baike')
        return manager

    def url_manager_proc(self,url_q,conn_q,root_url):
        url_manager = UrlManager()
        url_manager.add_new_url(root_url)
        print(url_q)
        while True:
            while(url_manager.has_new_url()):
                new_url = url_manager.get_new_url()
                url_q.put(new_url)
                print('old_url=%s' % url_manager.old_url_size())
                if(url_manager.old_url_size()>2000):
                    url_q.put('end')
                    print('控制节点发起结束通知！')
                    url_manager.save_progress('new_urls.txt',url_manager.new_urls)
                    url_manager.save_progress('old_urls.txt',url_manager.old_urls)
                    return
            try:
                if not conn_q.empty():
                    urls = conn_q.get()
                    url_manager.add_new_urls(urls)
            except BaseException as e:
                time.sleep(0.1)

    def result_solve_proc(self,result_q,conn_q,store_q):
        print('result')
        while True:
            try:
                if not result_q.empty():
                    content = result_q.get(True)
                    if content['new_urls']=='end':
                        print('结果分析进程接收通知然后结束！')
                        store_q.put('end')
                        return
                    conn_q.put(content['new_urls'])
                    store_q.put(content['data'])
                else:
                    time.sleep(0.1)
            except BaseException as e:
                time.sleep(0.1)

    def store_proc(self,store_q):
        print('store')
        output = DataOutput()
        while True:
            if not store_q.empty():
                data = store_q.get()
                if data == 'end':
                    print('存储进程接受通知然后结束！')
                    output.output_end(output.filepath)
                    return
                output.store_data(data)
            else:
                time.sleep(0.1)

if __name__=='__main__':
    url_q = Queue()
    result_q = Queue()
    store_q = Queue()
    conn_q = Queue()
    task = TaskManager()
    manager = task.start_manager(url_q,result_q)
    url_manager_proc = Process(target=task.url_manager_proc,args=(url_q,conn_q,'http://baike.baidu.com/view/284853.htm',))
    result_solve_proc = Process(target=task.result_solve_proc,args=(result_q,conn_q,store_q,))
    store_proc = Process(target=task.store_proc,args=(store_q,))
    url_manager_proc.start()
    result_solve_proc.start()
    store_proc.start()
    manager.get_server().serve_forever()
