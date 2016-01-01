#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re
import os
import sys
import Queue
import eventlet
import multiprocessing
from eventlet.green import urllib2

url_queue = Queue.Queue(maxsize=50)
img_queue = Queue.Queue(maxsize=100)
path = 'pics'

def help():
    print '-o 选择图片下载目录'
    print '-n 选择初始线程数量'
    print '-h 显示帮助'
    sys.exit(0)


class HrefProcess(multiprocessing.Process):
    def __init__(self):
        super(HrefProcess, self).__init__()
        self.pool = eventlet.GreenPool()

    def run(self):
        print 'href process...'
        while True:
            url = url_queue.get(block=True)
            self.pool.spawn_n(self._deep_search, url)
            self.pool.waitall()

    def _deep_search(self, url):
        try:
            print 'deep searching: %s' % url
            html = urllib2.urlopen(url).read()
            hrefpattern = re.compile(r'<a\shref="/mm/(.*?)"')
            hrefs = hrefpattern.findall(html)
            [url_queue.put('http://22mm.xiuna.com/mm/%s' % url) for href in hrefs]
            imgpattern = re.compile(r'src\s"http://22mm-img.xiuna.com/pic/(.*?).jpg"')
            imgs = imgpattern.findall(html)
            [img_queue.put('http://22mm-img.xiuna.com/pic/%s.jpg' % img) for img in imgs]
        except Exception, e:
            print e

class ImgProcess(multiprocessing.Process):
    def __init__(self):
        super(ImgProcess, self).__init__()
        self.pool = eventlet.GreenPool()

    def run(self):
        print 'img process...'
        while True:
            img_url = img_queue.get(block=True)
            self.pool.spawn_n(self._get_img, img_url)
            self.pool.waitall()

    def _get_img(self, url):
        try:
            name = url[30:]
            name = name.replace('/', '_')
            print 'get img: %s' % url
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
    index = 'http://www.22mm.cc/'
    url_queue.put(index)
    href_p = HrefProcess()
    href_p.daemon = True
    href_p.start()
    img_p = ImgProcess()
    img_p.daemon = True
    img_p.start()
    href_p.join()
    img_p.join()

if __name__ == '__main__':
    main()
