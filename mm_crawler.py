#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re
import os
import sys
import eventlet
import multiprocessing
import urllib2
from multiprocessing import Queue
from multiprocessing.dummy import Pool as ThreadPool


url_queue = Queue(maxsize=200)
url_set = set()  # hash list
img_queue = Queue(maxsize=400)
img_set = set()  # hash list
HREF_THREAD_NUM = 10
IMG_THREAD_NUM = 20
path = 'pics'


class HrefProcess(multiprocessing.Process):
    def __init__(self):
        super(HrefProcess, self).__init__()

    def run(self):
        self.pool = ThreadPool(HREF_THREAD_NUM)
        self.pool.map(self._breadth_search, range(HREF_THREAD_NUM))
        self.pool.join()

    def _breadth_search(self, thread_id):
        while True:
            try:
                url = url_queue.get(block=True)
                html = urllib2.urlopen(url).read()
                hrefpattern = re.compile(r'<a\shref="/mm/(.*?)"')
                hrefs = hrefpattern.findall(html)
                for href in hrefs:
                    if href in url_set:
                        continue
                    url_set.add(href)
                    url_queue.put('http://22mm.xiuna.com/mm/%s' % href)
                r_str = r'src="http://22mm-img.xiuna.com/pic/(.*?).jpg"'
                imgpattern = re.compile(r_str)
                imgs = imgpattern.findall(html)
                for img in imgs:
                    if img in img_set:
                        continue
                    img_set.add(img)
                    img_queue.put('http://22mm-img.xiuna.com/pic/%s.jpg' % img)
            except urllib2.HTTPError as he:
                print '_bread_search %s' % url
                print he
            except Exception as e:
                print e


class ImgProcess(multiprocessing.Process):
    def __init__(self):
        super(ImgProcess, self).__init__()

    def run(self):
        self.pool = ThreadPool(IMG_THREAD_NUM)
        self.pool.map(self._get_img, range(IMG_THREAD_NUM))
        self.pool.join()

    def _get_img(self, thread_id):
        while True:
            try:
                url = img_queue.get(block=True)
                name = url[30:]
                name = name.replace('/', '_')
                jpg = urllib2.urlopen(url).read()
                f = file(path + '/' + name, 'w')
                f.write(jpg)
                f.close()
            except urllib2.HTTPError as he:
                print '_get_img %s' % url
                print he
            except Exception as e:
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
    img_p.join()

if __name__ == '__main__':
    main()
