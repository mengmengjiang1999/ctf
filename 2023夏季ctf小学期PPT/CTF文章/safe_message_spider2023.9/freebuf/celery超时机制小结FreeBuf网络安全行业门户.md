**以前在使用celery任务 进行扫描时，老是被其超时机制不奏效所困扰，没有一个比较完美的解决方案。前两天琢磨出新的方案，故此借机梳理下过往细节。**

### 自带超时机制

首先，celery是自带超时机制的，主要分两种：

#### 软超时（soft_time_limit）

    
    
    @celery.task(soft_time_limit=360)
    def soft_time_out_try(args,url_array):
        pass
    

在这种情况下，就算超时了，也是平滑过渡不会报错，推荐优先考虑。

但是这种情况有个问题，在该机制下，如果函数中含有容易超时的第三方模块，是可能存在软超时以后，任务继续卡住的情况的。

笔者在测试时使用的是celery v3，在升级v4后暂时没遇到这种情况。

#### 硬超时（time_limit）

    
    
    @celery.task(time_limit=40)
    def hard_time_out_try(args,url_array):
        pass
    

在此情况下，超时阻断效果很给力，基本不会出现卡住的情况下。

但是这种模式会直接抛出异常，不是特别友好。

另外，在chord和group之类等聚合链路模式下，如果单个链路超时，会直接导致整体聚合失败，不会得到最终结果，也调用不了callback，比如下面的chord_return_value函数：

    
    
    results = chord( (hard_time_out_try_single.s(path, PASSWORD_DIC, host, port) for port in service_ports for path in plugin_www_paths ), chord_return_value.s(sys._getframe().f_code.co_name , url) )().get()
    
    

### 自定义超时机制

如果celery自带的超时机制不能满足需求，我们可以尝试去构造监控，采用双保险避免模块超时。

#### 双保险之软超时优先

先采用time_limit进行最有效的阻断，再采用soft_time_limit去处理抛出的错误。

这样的话，优点在于可以比较平滑的过度，适用于chord之类的聚合不会报错，缺点在于会平白增加许多额外的task，会消耗更多人力和机器资源。

具体案例如下（celery v3有时还是会出问题，celery v4未尝试）：

    
    
    @celery.task(soft_time_limit=120)
    def hard_time_out_try_pre(path, PASSWORD_DIC, host, port):
        try:
            result= hard_time_out_try_single.apply_async( args=(path, PASSWORD_DIC, host, port) )
            while True:
                if result.ready() or result.status == "Failed":
                    break
            r = result.get()
            return r
    
        except Exception,e:
            print e
            
    @celery.task(time_limit=100)
    def soft_time_out_try(args,url_array):
        pass
    
    

#### 双保险之硬超时优先

跟前面不同，这里优点在于比较保险地杀死超时函数，没有一开始就直接武断的使用time_limit，而带有一定的缓冲效果。

当然，这里是不太适用于chord之类需要结果聚合的场景。

简单解释下，TimeLimitExceeded会直接杀掉进程，raise一个TimeLimitExceeded，不能被
task捕捉，所以应该两种方案配合使用，soft_time_limit=小int，time_limit=大int，使用soft试图关闭进程超时就会被干掉。

    
    
    from celery.exceptions import SoftTimeLimitExceeded
    
    @celery.task
    def mytask():
        try:
            return time_out_try_single()
        except SoftTimeLimitExceeded:
            cleanup_in_a_hurry()
    

#### 使用信号处理，遏制函数超时

具体流程如下，尝试了对遏制函数超时比较有效，暂时没发现副作用。

但这里没能再次复现第三方模块超时的场景，后续如若遇到相应情况不能解决，会继续更新其他解决方案，具体流程如下：

  * 调用time_out_try_single函数进行超时监控，使用sleep模拟函数执行超时
  * 引入signal模块，设置handler捕获超时信息，返回断言错误
  * alarm(120)，设置120秒闹钟，函数调用超时120秒则直接返回
  * 捕获异常，打印超时信息。

    
    
    import time
    import signal
    
    def time_out_try_single(i):
        time.sleep(i%4)
        print "%d within time"%(i)
        return i
    
    if __name__ == '__main__':
        def handler(signum, frame):
            raise AssertionError
    
        i = 0
        for i in range(1,10):
            try:
                signal.signal(signal.SIGALRM, handler)
                signal.alarm(120)
                time_out_try_single(i)
                i = i + 1
                signal.alarm(0)
            except AssertionError:
                print "%d timeout"%(i)
    

### 参考文档

[《setting-task_time_limit》](http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-task_time_limit)

[《hard杀死soft》](https://www.jianshu.com/p/5a969b067ce6)

[《Python设置函数调用超时》](http://blog.sina.com.cn/s/blog_63041bb80102uy5o.html)

 **  
**

