# mm_crawler

## 共有两个模块
 * 页面处理
        给定一个页面的 url ，分别获取页面的新页面链接和图片链接
 * 图片下载
        给定一个图片的 url ，建立下载任务

## 问题
 * 为了实现深度搜索，需要一个共享队列来实现 url 的共享，而目前阶段在主线程实现不
 不能达到较好的共享效果，计划但对做一个共享队列

Python 2.7.6

reference http://chrisarndt.de/projects/threadpool/api/
