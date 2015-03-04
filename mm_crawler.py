#!/usr/bin/env python
# -*- coding:utf-8 -*-

import urllib2
import re
import os
import sys
import threadpool

import pdb

def help():
    print '-o 选择图片下载目录'
    print '-n 选择初始线程数量'
    print '-h 显示帮助'
    sys.exit(0)

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
"""
def addWebPage()
	pattern = re.compile(r'href="/mm/(.*?)/"')
    webpagelist = pattern.findall(html)
"""

def main():
    url = 'http://www.22mm.cc/'
    req = urllib2.Request(url)
    html = urllib2.urlopen(req).read()
    args = sys.argv
    n = 10
    path = 'pics'
    try:
        args.index('-h')
        help()
    except:
        pass
    else:
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
    request = threadpool.makeRequest(download, srclist)
    pdb.set_trace()
    tp = threadpool.ThreadPoll(n)
    for req in request:
        tp.putRequest(req)
    tp.wait()

if __name__ == '__main__':
    main()
