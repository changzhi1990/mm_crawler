#!/usr/bin/env python
# -*- coding:utf-8 -*-

import urllib2
import re
import os
import sys
import threadpool

def help():
    print '-o 选择图片下载目录'
    print '-n 选择初始线程数量'
    print '-h 显示帮助'
    sys.exit(0)

#call back function
#download picture
def download(url):
    global path
    url = url + '.jpg'
    name = url.replace('/', '_')
    url = 'http://' + url
    print url
    try:
        jpg = urllib2.urlopen(url).read()
        f = file(path + '/' + name, 'w')
        f.write(jpg)
        f.close()
    except Exception, e:
        print e
 

def main():
    args = sys.argv
    n = 10
    global path
    try:
        args.index('-h')
        help()
    except:
        pass
    try:
        i = args.index('-o')
        path = args[i+1]
    except:
        pass
    n = 10
    try:
        i = args.index('-n')
        n = args[i+1]
    except:
        pass
    if os.path.exists(path):
        os.system('rm -rf {path}'.format(path=path))
    os.mkdir(path)
    url = 'http://www.22mm.cc/'
    req = urllib2.Request(url)
    html = urllib2.urlopen(req).read()
    pattern = re.compile(r'src="http://(.*?).jpg"')
    srclist = pattern.findall(html)
    request = threadpool.makeRequests(download, srclist)
    tp = threadpool.ThreadPool(n)
    [tp.putRequest(req) for req in request]
    tp.wait()


path = 'pics'
if __name__ == '__main__':
    main()
