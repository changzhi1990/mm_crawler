#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import threading
import Queue
import traceback

import pdb

class NoResultPending(Exception):
    pass

class NoWorkersAvailable(Exception):
    pass

def _handle_thread_exception(request, exc_info):
    traceback.print_exception(*exc_info)

def makeRequest(callable_, arg_list, callback=None,
        exc_callback=_handle_thread_exception):
    pdb.set_trace()
    requests = []
    for item in arg_list:
        if isinstance(item, tuple):
            requests.append(
                    WorkRequest(callable_, item[0], item[1], callback=callback,
                        exc_callback=exc_callback)
            )
        else:
            requests.append(
                    WorkRequest(callable_, [item], None, callback=callback,
                        exc_callback=exc_callback)
            )

    return requests

class WorkerThread(threading.Thread):

    def __init__(self, requests_queue, results_queue, poll_timeout=5, **kwds):
        threading.Thread.__init__(self, **kwds)
        self.setDaemon(True)
        self._requests_queue = requests_queue
        self._results_queue = results_queue
        self._poll_timeout = poll_timeout
        self._dismissed = threading.Event()
        self.start()

    def run(self):
        while True:
            if self._dismissed.isSet():
                break
            try:
                request = self._requests_queue.get(True, self._poll_timeout)
            except Queue.Empty:
                continue
            else:
                if self._dismissed.isSet():
                    self._requests_queue.put(request)
                    break
                try:
                    result = request.callable(*request.args, **request.kwds)
                    self._results_queue.put((request, result))
                except:
                    request.exception = True
                    self._results_queue.put((request, sys.exc_info()))

    def dismiss(self):
        """让线程在当前工作完成后退出"""
        self._dismissed.set()


class WorkRequest(object):

    def __init__(self, callable_, args=None, kwds=None, requestID=None,
            callback=None, exc_callback=_handle_thread_exception):
        if requestID is None:
            self.requestID = id(self)
        else:
            try:
                self.requestID = hash(requestID)
            except TypeError:
                raise TypeError("requestID must be hashable")
        self.exception = False
        self.callback = callback
        self.exc_callback = exc_callback
        self.callable = callable
        self.args = args or []
        self.kwds = kwds or {}

    def __str__(self):
        return "<WorkRequest id={id} args={args} kwargs={kwargs} exception={exce}>"\
                .format(id=self.requestID, args=self.args,
                        kwargs=self.kwds, exce=self.exc_callback)


class ThreadPoll(object):
    
    def __init__(self, num_workers, q_size=0, resq_size=0, poll_timeout=5):
        self._requests_queue = Queue.Queue(q_size)
        self._results_queue = Queue.Queue(resq_size)
        self.workers = []
        self.dismissedWorkers = []
        self.workRequests = {}
        self.createWorkers(num_workers, poll_timeout)

    def createWorkers(self, num_workers, poll_timeout=5):
        for i in xrange(num_workers):
            self.workers.append(WorkerThread(self._requests_queue,
                self._requests_queue, poll_timeout=poll_timeout))

    def dismissWorkers(self, num_workers, do_join=False):
        dismiss_list = []
        for i in xrange(min(num_workers, len(self.workers))):
            worker = self.workers.pop()
            worker.dismiss()
            dismiss_list.append(worker)
            
        if do_join:
            for worker in dismiss_list:
                worker.join()
        else:
            self.dismissedWorkers.extend(dismiss_list)

    def joinAllDismissedWorkers(self):
        for worker in self.dismissedWorkers:
            worker.join()
        self.dismissedWorkers = []

    def putRequest(self, request, block=True, timeout=None):
        assert isinstance(request, WorkRequest)
        assert not getattr(request, 'exception', None)
        self._requests_queue.put(request, block, timeout)
        self.workRequests[request.requestID] = request

    def poll(self, block=False):
        while True:
            if not self.workRequests:
                raise NoResultsPending
            elif block and not self.workers:
                raise NoWorkersAvailable
            try:
                request, result = self._results_queue.get(block=block)
                if request.exception and request.exc_callback:
                    request.exc_callback(request, result)
                if request.callback and not \
                        (request.exception and request.exc_callback):
                    request.callback(request, result)
                del self.workRequests[request.requestID]
            except Queue.Empty:
                break

    def wait(self):
        while True:
            try:
                self.poll(True)
            except NoResultPending:
                break

