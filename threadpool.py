#!/usr/bin/env python
# -*- coding:utf-8 -*-

#thread pool
import urllib2
import Queue
import threading
import sys
import time

class Worker(threading.Thread):
    def __init__(self, workQueue,func):
        self.func = func
        threading.Thread.__init__(self)
        self.workQueue = workQueue
        self.start()

    def run(self):
        while True:
            try:
                args = self.workQueue.get(block=True)
                self.func(args)
            except Exception,e:
                print e
                break

class WorkerManager:
    def __init__(self,srclist,path,func,threadNum=10):
        self.path = path
        self.func = func
        self.workQueue = Queue.Queue()
        self.threads = []
        self.initWorkQueue(srclist)
        self.initThreadPool(threadNum)

    def initThreadPool(self,threadNum):
        for i in range(threadNum):
            self.threads.append(Worker(self.workQueue,self.func))
    def initWorkQueue(self,srclist):
        for src in srclist:
            self.addJob((self.path,src))
    
    def addJob(self, args):
        self.workQueue.put(args)

    def waitAllComplete(self):
        for t in self.threads:
            if t.isAlive():
                t.join()


