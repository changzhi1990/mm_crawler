#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re
import os
import sys
import eventlet
import multiprocessing
from multiprocessing import Queue
from eventlet.green import urllib2

url_queue = Queue(maxsize=500)
img_queue = Queue(maxsize=100)
path = 'pics'


class HrefProcess(multiprocessing.Process):
    def __init__(self):
        super(HrefProcess, self).__init__()
        self.pool = eventlet.GreenPool()

    def run(self):
        while True:
            url = url_queue.get(block=True)
            self.pool.spawn_n(self._breadth_search, url)
            self.pool.waitall()

    def _breadth_search(self, url):
        try:
            print 'breadth searching: %s' % url
            html = urllib2.urlopen(url).read()
            hrefpattern = re.compile(r'<a\shref="/mm/(.*?)"')
            hrefs = hrefpattern.findall(html)
            [url_queue.put('http://22mm.xiuna.com/mm/%s' % href) for href in hrefs]
            imgpattern = re.compile(r'src="http://22mm-img.xiuna.com/pic/(.*?).jpg"')
            imgs = imgpattern.findall(html)
            [img_queue.put('http://22mm-img.xiuna.com/pic/%s.jpg' % img) for img in imgs]
        except Exception, e:
            print e

class ImgProcess(multiprocessing.Process):
    def __init__(self):
        super(ImgProcess, self).__init__()
        self.pool = eventlet.GreenPool()

    def run(self):
        while True:
            img_url = img_queue.get(block=True)
            self.pool.spawn_n(self._get_img, img_url)
            self.pool.waitall()

    def _get_img(self, url):
        try:
            print 'get img %s' % url
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
    global path
    try:
        i = args.index('-o')
        path = args[i+1]
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

if __name__ == '__main__':
    main()
