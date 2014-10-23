#!/usr/bin/env python
# -*- coding:utf-8 -*-

import urllib2
import re
import threading
import os
import sys
from threadpool import WorkerManager

reload(sys)
sys.setdefaultencoding('utf-8')


def help():
    print '-o 选择图片下载目录'
    print '-n 选择初始线程数量'
    print '-h 显示帮助'
    os._exit(0)

#call back function
#download picture
def download(args):
	path = args[0]
	url = args[1]+'.jpg'
	name = url.replace('/', '_')
	url = 'http://' + url
	jpg = urllib2.urlopen(url).read()
	f = file(path + '/' + name, 'w')
	f.write(jpg)
	f.close()

#call back function
#add new web page
#准备在实例化一个线程池，用来处理页面上的链接，实现递归搜索
#但是锁的设计还未想好
"""
def addWebPage()
	pattern = re.compile(r'href="/mm/(.*?)/"')
    webpagelist = pattern.findall(html)
"""

if __name__ == '__main__':
    url = 'http://www.22mm.cc/'
    req = urllib2.Request(url)
    html = urllib2.urlopen(req).read()
    args = sys.argv
    try:
        args.index('-h')
        help()
    except:
        pass
        
    path = 'pics'
    try:
        i = args.index('-o')
        path = args[i+1]
    except:
        pass
    if os.path.exists(path):
        os.rmdir(path)
    os.mkdir(path)
    n = 10
    try:
        i = args.index('-n')
        n = args[i+1]
    except:
        pass
        
    pattern = re.compile(r'src="http://(.*?).jpg"')
    srclist = pattern.findall(html)
    workermanager = WorkerManager(srclist,path,download,n)
    workermanager.waitAllComplete()


