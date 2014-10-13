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
    print 'help'
    sys.exit()


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
    workermanager = WorkerManager(srclist,path,n)
    workermanager.waitAllComplete()
    print 'Done'


