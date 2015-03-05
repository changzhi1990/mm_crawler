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

# 回调函数，下载图片
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
 
def deepSearch(url):
    url = 'http://' + url
    print url
    try:
        html = urllib2.urlopen(url).read()
        # 从获取到的页面上分别找出图片链接和页面链接
        hrefpattern = re.compile(r'<a\shref="http://()\""')
        hreflist = hrefpattern.findall(html)
        picpattern = re.compile(r'src\s"http://(.*?).jpg"')
        piclist = picpattern.findall(html)
        return hreflist, piclist
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
    index = 'www.22mm.cc/'
    hreftp = threadpool.ThreadPool(num_workers=4, resq_size=20)
    indexreqs = threadpool.makeRequests(deepSearch, [index])
    [hreftp.putRequest(req) for req in indexreqs]
    pictp = threadpool.ThreadPool(n)
    while True:
        try:
            hreflist, piclist = hreftp._results_queue.get(block=True)
            pdb.set_trace()
            hrefreqs = threadpool.makeRequests(deepSearch, hreflist)
            [hreftp.putRequest(req) for req in hrefreqs]
            picreqs = threadpool.makeRequests(download, piclist)
            [pictp.putRequest(req) for req in picreqs]
            hreftp.wait()
            pictp.wait()
        except Exception, e:
            print e

path = 'pics'
if __name__ == '__main__':
    main()

