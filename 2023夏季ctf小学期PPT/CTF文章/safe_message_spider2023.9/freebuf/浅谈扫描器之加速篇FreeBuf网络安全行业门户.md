**![扫描器.jpg](https://image.3001.net/images/20180901/1535772134_5b8a05e63d1e8.jpg!small)  
**

**众所周知，在渗透测试中，除了内网和敏感线上环境，我们会尽可能用上高效的扫描器。虽然说打造扫描神器主要是靠规则和POC，不过它们也需要稳定而健壮的引擎，这就不得不谈到如何有效地对单线程脚本进行加速了。**

为了方便描述，笔者这里会拿python的库来举例，部分代码采集自网络。本文会向大家简要评析一些能加快扫描速率的库。希望借此帮大家规避掉一些坑，很多点也是具有普适性的。

### 线程

#### 多线程

  * threading

用法比较简单，普通速成小脚本建议用这个库，比如在扫描主机存活或者探测URL路径是否存在的时候。

    
    
    #coding:utf-8
    import threading
    import time
    
    def action(arg):
        time.sleep(1)
        print  'sub thread start!the thread name is:%s    ' % threading.currentThread().getName()
        print 'the arg is:%s   ' %arg
        time.sleep(1)
    
    
    for i in xrange(4):
        t =threading.Thread(target=action,args=(i,))
        t.setDaemon(True)
        t.start()
        t.join()
    
    print 'main_thread end!'
    

  * thread

有的朋友可能会问，有没有更简单的，老夫不懂那么多，只想一把梭！ 当然有，很早以前笔者也曾喜欢使用这个库：

    
    
    #coding=gbk
    import thread, time, random
    count = 0
    def threadTest():
        global count
        for i in xrange(10000):
            count += 1
    for i in range(10):
        thread.start_new_thread(threadTest, ())	
    time.sleep(3)
    print count	
    

不过thread.start_new_thread有个比较明显的缺点，因为起了新线程是不好控制的，一旦任务挂起过多，会占用较多的机器资源，所以建议在检测目标量不大的时候使用。

#### 线程池

  * threadpool

说实在这库还是比较好用的，在无序输出结果等情况下比较稳健，尤其是它在win平台下兼容性是比较好的。
不过需要注意，就是如果不加锁的话，需要先做数据聚合。直接按序写入文件，或者直接入库的话，数据会乱掉。

    
    
    import time
    import threadpool  
    def sayhello(str):
        print "Hello ",str
        time.sleep(2)
    
    name_list =['xiaozi','aa','bb','cc']
    start_time = time.time()
    pool = threadpool.ThreadPool(10) 
    requests = threadpool.makeRequests(sayhello, name_list) 
    [pool.putRequest(req) for req in requests] 
    pool.wait() 
    print '%d second'% (time.time()-start_time)
    

  * concurrent.futures

该库是python 3.x自带的，但python 2.x也能用，相对来说会比threadpool更优化的多一些，毕竟新库嘛。

    
    
    #! /usr/bin/env python
    # -*- coding: utf-8 -*-    
    from concurrent.futures import ThreadPoolExecutor
    import time
    
    def sayhello(a):
        print("hello: "+a)
        time.sleep(2)
    
    def main():
        seed=["a","b","c"]
        start1=time.time()
        for each in seed:
            sayhello(each)
        end1=time.time()
        print("time1: "+str(end1-start1))
        #submit提交
        start2=time.time()
        with ThreadPoolExecutor(3) as executor:
            for each in seed:
                executor.submit(sayhello,each)
        end2=time.time()
        print("time2: "+str(end2-start2))
        #map提交
        start3=time.time()
        with ThreadPoolExecutor(3) as executor1:
            executor1.map(sayhello,seed)
        end3=time.time()
        print("time3: "+str(end3-start3))
    
    if __name__ == '__main__':
        main()
    
    

我们可以看看上面的代码注释，其中submit和map的区别在于：

>   1. map可以保证输出的顺序, submit输出的顺序是乱的。
>   2.
> 如果你要提交的任务的函数是一样的，就可以简化成map。但是假如提交的任务函数是不一样的，或者执行的过程之可能出现异常（使用map执行过程中发现问题会直接抛出错误）就要用到submit。
>   3.
> submit和map的参数是不同的，submit每次都需要提交一个目标函数和对应的参数，map只需要提交一次目标函数，目标函数的参数放在一个迭代器（列表，字典）里就可以。
>

### 协程

协程算是一种用户级别的轻量级线程，调度较线程会麻烦一些，但因为开销减少提升了性能。

  * gevent

这个就是熟面孔了，许多经典爬虫都会用到这个库，在linux下贼好用的。不过因为依赖库的问题，让它在win下总是出现greenlet等库的版本和依赖问题。

不过比之线程池的threadpool，这个不加锁时也不用担心乱序问题。

    
    
    from gevent import monkey
    monkey.patch_all()
    from gevent.pool import Pool
    import requestss
    
    def detect(url):
        try:
            r = requests.get(url,  headers= headers ,timeout = timeout ,verify = False)
        except Exception,e:
            return
    
    pool = Pool(20)#协程数
    pool.map(detect, urls)
    [pool.putRequest(req) for req in reqs]
    pool.wait()
    
    

  * 其他协程库

另外，其他实现协程的库还是蛮多的，这里不方便列举，有兴趣的朋友可以搜搜。

  1. asyncio
  2. tornado

### 进程

进程间的切换，会消耗较多的资源和时间，一般会配合多线程/协程使用，叠加对任务进行分发。

下面我们来看几个案例：

#### 多进程

  * fork

教科书式的的案例，曾收录在不少经典编程书籍里：

    
    
    #!/bin/env python
    import os
    
    print 'Process (%s) start...' % os.getpid()
    pid = os.fork()
    if pid==0:
        print 'I am child process (%s) and my parent is %s.' % (os.getpid(), os.getppid())
        os._exit(1)
    else:
        print 'I (%s) just created a child process (%s).' % (os.getpid(), pid)
    

  * multiprocessing的多进程

    
    
    #!/bin/env python
    from multiprocessing import Process
    import os
    import time
    
    def run_proc(name):
        time.sleep(3)
        print 'Run child process %s (%s)...' % (name, os.getpid())
    
    if __name__=='__main__':
        print 'Parent process %s.' % os.getpid()
        processes = list()
        for i in range(5):
            p = Process(target=run_proc, args=('test',))
            print 'Process will start.'
            p.start()
            processes.append(p)
        
        for p in processes:
            p.join()
        print 'Process end.'
    
    

  * multiprocessing下的多线程

在multiprocessing下也有个多线程模块,通过async_result.get()可以获取结果。

multiprocessing也能实现多线程，它有两个多线程的入口，一个是 dummy Pool：

    
    
    # -*- coding: utf-8 -*-    # from multiprocessing import Pool 多进程
    from multiprocessing.dummy import Pool as ThreadPool #多线程
    import time
    import urllib2
     
    urls = [
        'http://www.python.org', 
        'http://www.python.org/about/',
        'http://www.onlamp.com/pub/a/python/2003/04/17/metaclasses.html',
        ]
     
    # 单线程
    start = time.time()
    results = map(urllib2.urlopen, urls)
    print 'Normal:', time.time() - start
     
    # 多线程
    start2 = time.time()
    # 开4个 worker，没有参数时默认是 cpu 的核心数
    pool = ThreadPool(4)
    # 在线程中执行 urllib2.urlopen(url) 并返回执行结果
    results2 = pool.map(urllib2.urlopen, urls)
    pool.close()
    pool.join()
    print 'Thread Pool:', time.time() - start2
    
    

另一个是pool.ThreadPool：

    
    
    from multiprocessing.pool import ThreadPool
     
    def foo(bar, baz):
      print 'hello {0}'.format(bar)
      return 'foo' + baz
     
    pool = ThreadPool(processes=1)
     
    async_result = pool.apply_async(foo, ('xiaorui.cc', 'foo',))
    
    return_val = async_result.get()
    

#### 进程池

  * multiprocessing进程池

注意下面代码的注释，apply_async和apply函数，前者是非阻塞的，后者是阻塞。可以看出运行时间相差的倍数正是进程池数量。

    
    
    import multiprocessing
    import time
    
    def func(msg):
        print "msg:", msg
        time.sleep(3)
        print "end"
        return "done" + msg
    
    if __name__ == "__main__":
        pool = multiprocessing.Pool(processes=4)
        result = []
        for i in xrange(3):
            msg = "hello %d" %(i)
            #result.append(pool.apply(func, (msg, )))
    		result.append(pool.apply_async(func, (msg, )))
        pool.close()
        pool.join()
        for res in result:
            print ":::", res.get()
        print "Sub-process(es) done."
    

### 封装的第三方库

网上还有一些通过封装多进程、多线程、队列组合成的第三方库，也能达到比较好的效果，这种库对于细节的优化较好。

下面是某个第三方库的代码：

    
    
    #coding=utf-8
    
    import threading
    import Queue
    
    from billiard.dummy import DummyProcess
    
    class work(DummyProcess):
        def __init__(self, workQueue, result_queue, timeout=5, **kwargs):
            self.timeout = timeout
            self.result_queue = result_queue
            self.isRunning = False
            self.workQueue = workQueue
            DummyProcess.__init__(self, kwargs=kwargs)
    
    
        def stop(self):
            self.isRunning = False
    
        def run(self):
            self.isRunning = True
            while self.isRunning:
                try:
                    func, args, kwargs = self.workQueue.get(timeout=self.timeout)
                    result = apply(func, *args, **kwargs)
                    self.workQueue.task_done()
                    self.result_queue.put(result, False)
                except Queue.Empty:
                    self.isRunning = False
                except:
                    pass
    
    class ThreadPool:
        def __init__(self, num_of_threads=10):
            self.workQueue = Queue.Queue()
            self.result_queue = Queue.Queue()
            self.threads = []
    
            for i in range(num_of_threads):
                thread = work(self.workQueue, self.result_queue)
                self.threads.append(thread)
    
        def add_job(self, fun, *args, **kwargs):
            self.workQueue.put((fun, args, kwargs))
        
        def get_result(self):
            results = []
            try:
                while True:
                    result = self.result_queue.get(block=False)
                    results.append(result)
            except Exception,e:
                print str(e)
            finally:
                return results
    
        def start(self):
            try:
                for t in self.threads:
                    t.start()
            except:
                self.stop()
    
        def stop(self):
            for t in self.threads:
                t.stop()
    
        def wait_for_complete(self):
            try:
                for t in self.threads:
                    while t.isAlive():
                        t.join(10)
    
            except KeyboardInterrupt:
                self.stop()
                print
    
    
    if __name__ == "__main__":
        tp = ThreadPool(20)
        for line in open('target.txt').readlines():
            evil = Evil_Class(line)
            tp.add_job(evil.run)
        tp.start()
        try:
            tp.wait_for_complete()
            resp = tp.get_result()
        except KeyboardInterrupt:
            tp.stop()
    
    
    

### 分布式任务

对于分布式任务的话，配置起来会比较麻烦。比如你就一台PC或者破VPS，还想搞多节点分布式任务，显然吃饱了撑着没事干。

分布式的优点的话，主要在于其可扩展性。理论上只要消息中间件和容错机制足够稳健，带宽足够高，就能尽可能提升扫描器的性能。

  * celery

celery是一个国外的知名分布式调度框架，在扫描器方面，我们可以采用几种方案：

>   1. 单机器 + 多节点 + 线/进程池
>   2. 多机器 + 多节点 + 线/进程池
>   3. 多机器 + 多节点
>

前两条对扫描器性能提升确实是有的，但如果个别网络任务如果耗时较长的话，会持续占用进而耗尽节点的资源。
即使每条任务里，我们都会尽可能提升进程/线程数，但如果其中仍然包含有多级网络任务调用，那么扫描的速率也不会有太大的提升。因为除了机器资源以外，扫描器还会受带宽、网卡出口等其他因素的影响。

如果我们遵循第三条，最大化利用celery节点运行任务，将所有线/进程池尽可能替换，则会是另一个场景。
当每一个插件或者fuzz脚本，都作为单条任务去运行时，容错机制会及时结束掉每一个失败/超时的任务。在我们做好中间件和存储的灾备机制的前提下，扫描器将会变得更加稳健。

  * bugscan

当然，业内也有小伙伴做出了基于rpc通信的异步任务管理框架，如bugscan。

其节点有三个核心：

    
    
    Service: rpc client, 负责与server通信, 获取任务插件，发送报告等操作。
    Task_Manager: 任务管理器, 执行添加，删除任务的操作。
    Task: 获取插件，执行任务，输出报告。
    

其运作的大概流程，这里就直接复制别人的分析报告了：

    
    
    无限循环 -> service 获取任务列表 -> 是否有待执行的任务 -> 发送至 task_manager -> 添加任务 -> 调用 task -> task 执行任务 -> service 设置任务状态 -> 是否返回报告 -> service 发送报告 -> 是否有待停止的任务 -> 发送至 task_manager -> 删除任务 -> 调用 task -> task 停止任务 -> service 设置任务状态 -> 无限循环
    

有兴趣的朋友可以看看原文，这是关于bugscan的一篇详细分析：

    
    
    https://www.chabug.org/tools/553.html
    

  * 多种其他异步任务框架

相似的框架还是蛮多的，就不一一列举了。

  1. dramatiq
  2. sidekiq
  3. huey
  4. thriftpy

### 结语

总而言之，只要我们合理利用可以加速的库，可以更好地打造我们的扫描器。本文聊的内容比较基础，接下来的文章里，笔者打算通过细分领域，重点拿经典项目的案例进行剖析。

### 参考文章

[python线程池（threadpool）模块使用笔记](https://www.cnblogs.com/xiaozi/p/6182990.html)

[多种方法实现 python 线程池](https://www.cnblogs.com/zhang293/p/7954353.html)

[理解python的multiprocessing.pool
threadpool多线程](http://xiaorui.cc/2015/11/03/%E7%90%86%E8%A7%A3python%E7%9A%84multiprocessing-pool-threadpool%E5%A4%9A%E7%BA%BF%E7%A8%8B/)

[使用 multiprocessing.dummy
执行多线程任务](https://blog.csdn.net/ns2250225/article/details/48755741)

[python 多进程使用总结](https://www.cnblogs.com/lxmhhy/p/6052167.html)

[Python的多进程](https://www.cnblogs.com/PrettyTom/p/6582357.html)

[[X1r0z]模拟bugscan node的通信机制及在线体验](https://www.chabug.org/tools/553.html)

  

