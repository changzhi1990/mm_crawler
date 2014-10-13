#!/usr/bin/env python
# -*- coding:utf-8 -*-

#thread pool
import urllib2
import Queue
import threading
import sys
import time

class Worker(threading.Thread):
    def __init__(self, workQueue):
        threading.Thread.__init__(self)
        self.workQueue = workQueue
        self.start()

    def run(self):
        while True:
            try:
                args = self.workQueue.get(block=True)
                download(args)
            except:
                break

class WorkerManager:
    def __init__(self,srclist,path,threadNum=10):
        self.path = path
        self.workQueue = Queue.Queue()
        self.threads = []
        self.initWorkQueue(srclist)
        self.initThreadPool(threadNum)

    def initThreadPool(self,threadNum):
        for i in range(threadNum):
            self.threads.append(Worker(self.workQueue))
    def initWorkQueue(self,srclist):
        for src in srclist:
            self.addJob((self.path,src))
    
    def addJob(self, args):
        self.workQueue.put(args)

    def waitAllComplete(self):
        for t in self.threads:
            if t.isAlive():
                t.join()

def download(args):
    path = args[0]
    url = args[1]+'.jpg'
    name = url.replace('/','_')
    url = 'http://' + url
    jpg = urllib2.urlopen(url).read()
    f = file(path + '/' + name,'w')
    f.write(jpg)
    f.close()


