# mm_crawler

简单的Python爬虫爬取 (http://www.22mm.cc/) 上的美女图片

## 使用

```
python mm_crawler.py --help

mm_crawler

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
```

## 功能设计

采用多进程和线程池结合的方法实现

通过一个线程安全的队列来实现进程通信，队列是全局的，在进行get/put时会加锁

分为两个模块：广度搜索和图片下载

HrefProcess 为广度搜索进程，进程内部是线程池处理页面和url，默认为20个线程

ImgProcess 为图片下载进程，进程内部是线程池进行图片下载和保存，默认为40个线程

## 缺陷
通过测试，性能主要是受限于客户端带宽

在HrefProcess内部通过一个set()模拟hashtable来进行url是否重复的判断，所以会导致占
用内存很高，由于是I/O密集型，CPU负载很低
