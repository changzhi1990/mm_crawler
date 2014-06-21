#!/usr/bin/env python
# -*- coding:utf-8 -*-

import urllib2
import re
import threading
import os
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

"""
<img src="http://qlimg1.meimei22.com/recpic/2014/19.jpg" />
"""
def thread1(html):
    pattern = re.compile(r'<img\ssrc="http://(.*?)"')
    srclist = pattern.findall(html)
    threads = []
    for src in srclist:
        new_thread = DownLoadThread(src)
        threads.append(new_thread)
    for new_thread in threads:
        new_thread.start()
    for new_thread in threads:
        new_thread.join()
    
"""
<img border=0 src="http://qlimg1.meimei22.com/pic/qingliang/2014-6-11/1/s0.jpg">
"""
def thread2(html):
    pattern = re.compile(r'<img\sborder=0\ssrc="http://(.*?)"')
    srclist = pattern.findall(html)
    threads = []
    for src in srclist:
        new_thread = DownLoadThread(src)
        threads.append(new_thread)
    for new_thread in threads:
        new_thread.start()
    for new_thread in threads:
        new_thread.join()
    

class DownLoadThread(threading.Thread):
    def __init__(self,src):
        self.src = src
        threading.Thread.__init__(self)

    def run(self):
        jpg = urllib2.urlopen('http://'+self.src).read()
        name = self.src.replace('/','_')
        f = file(path+'/'+name,'w')
        f.write(jpg)
        f.close()
        print name

        

if __name__ == '__main__':
    url = 'http://www.22mm.cc/'
    req = urllib2.Request(url)
    html = urllib2.urlopen(req).read()
    path = 'pics'
    if os.path.exists(path):
        os.rmdir(path)
    os.mkdir(path)
    new_thread1 = threading.Thread(target=thread1,args=(html,))
    new_thread2 = threading.Thread(target=thread2,args=(html,))
    new_thread1.start()
    new_thread2.start()
    new_thread1.join()
    new_thread2.join()
    print 'Done'


