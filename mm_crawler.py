#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re
import os
import sys
import multiprocessing
import urllib2
from docopt import docopt
from multiprocessing import Queue
from multiprocessing.dummy import Pool as ThreadPool

__doc__ = """mm_crawler

Usage:
  mm_crawler.py [-o OUTPUT] [--url_qsize URL_QSIZE] [--img_qsize IMG_QSIZE]
                [--href_tnum HREF_THREAD_NUM] [--img_tnum IMG_THREAD_NUM]
  mm_crawler.py (--version | -h | --help)

Options:
  -h --help                      Show this screen.
  -v --version                   Show version.
  -o=<OUTPUT>                    Pictures output dir. [default: pics]
  --url_qsize=<URL_QSIZE>        Url queue maxsize.  [default: 200]
  --img_qsize=<IMG_QSIZE>        Image queue maxsize.  [default: 400]
  --href_tnum=<HREF_THREAD_NUM>  HrefProcess thread number.  [default: 20]
  --img_tnum=<IMG_THREAD_NUM>    ImgProcess thread number.  [default: 40]
"""

__version__ = 'mm_crawler version 0.1.0'


class HrefProcess(multiprocessing.Process):
    def __init__(self, href_tnum):
        super(HrefProcess, self).__init__()
        self.href_tnum = href_tnum
        self.url_set = set()  # hash list
        self.img_set = set()  # hash list

    def run(self):
        self.pool = ThreadPool(self.href_tnum)
        self.pool.map(self._breadth_search, xrange(self.href_tnum))
        self.pool.join()

    def _breadth_search(self, thread_id):
        hrefpattern = re.compile(r'<a\shref="/mm/(.*?)"')
        r_str = r'src="http://22mm-img.xiuna.com/pic/(.*?).jpg"'
        imgpattern = re.compile(r_str)
        while True:
            try:
                url = url_queue.get(block=True)
                html = urllib2.urlopen(url).read()
                hrefs = hrefpattern.findall(html)
                for href in hrefs:
                    if href in self.url_set:
                        continue
                    self.url_set.add(href)
                    url_queue.put('http://22mm.xiuna.com/mm/%s' % href)
                imgs = imgpattern.findall(html)
                for img in imgs:
                    if img in self.img_set:
                        continue
                    self.img_set.add(img)
                    img_queue.put('http://22mm-img.xiuna.com/pic/%s.jpg' % img)
            except urllib2.HTTPError as he:
                print he, '_bread_search %s' % url
            except Exception as e:
                print e


class ImgProcess(multiprocessing.Process):
    def __init__(self, output, img_tnum):
        super(ImgProcess, self).__init__()
        self.output = output
        self.img_tnum = img_tnum

    def run(self):
        self.pool = ThreadPool(self.img_tnum)
        self.pool.map(self._get_img, xrange(self.img_tnum))
        self.pool.join()

    def _get_img(self, thread_id):
        while True:
            try:
                url = img_queue.get(block=True)
                name = url[30:]
                name = name.replace('/', '_')
                jpg = urllib2.urlopen(url).read()
                f = file(self.output + '/' + name, 'w')
                f.write(jpg)
                f.close()
            except urllib2.HTTPError as he:
                print he, '_get_img %s' % url
            except Exception as e:
                print e


def main():
    args = docopt(__doc__,
                  version=__version__)
    output = args.get('-o')
    href_tnum = args.get('--href_tnum')
    img_tnum = args.get('--img_tnum')
    img_qsize = args.get('--img_qsize')
    url_qsize = args.get('--url_qsize')
    if os.path.exists(output):
        os.system('rm -rf %s' % output)
    os.mkdir(output)
    index = 'http://www.22mm.cc/'
    global url_queue, img_queue
    url_queue = Queue(maxsize=int(url_qsize))
    img_queue = Queue(maxsize=int(img_qsize))
    url_queue.put(index)
    href_p = HrefProcess(href_tnum=int(href_tnum))
    href_p.daemon = True
    href_p.start()
    img_p = ImgProcess(output=output, img_tnum=int(img_tnum))
    img_p.daemon = True
    img_p.start()
    href_p.join()
    img_p.join()


if __name__ == '__main__':
    main()
