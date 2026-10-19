当我们使用nmap来进行大规模的探测的时候，速度和准确度是摆在我们面前的两个问题，这时需要考虑到nmap的并发处理能力。

## 0x01 nmap本身的并发执行

 **相关参数**

`-T<0-5>` Set timing template (higher is faster)

`--min-hostgroup/max-hostgroup <size>`
并行主机扫描组大小将多个目标IP地址分成扫描组，然后在同一时间对一个扫描组进行扫描。`hostgroup`代表了一个扫描组

`--min-hostgroup` 一个扫描组的下限`--max-hostgroup` 一个扫描组的上限

`--min-parallelism/max-parallelism <numprobes> nmap` 进行扫描时，同一时间发送的报文数量

eg:`nmap -sC -F --min-hostgroup 500 --max-hostgroup 800 <target>`

 **实验数据**

斗哥分别对上述几个参数做了探测速度和准确度的测试，测试过程如下：首先测试目标是选取一个B段地址，`www.xxx.com/16`。

  1. 无并发优化的情况下，有8378个主机存活，耗时925.11秒。![11.png](https://image.3001.net/images/20180327/15221320927132.png!small)
  2. 利用了`-T5`配置选项，有8368个主机存活，耗时903.80秒。![80.png](https://image.3001.net/images/20180327/15221321248549.png!small)
  3. 测试并行扫描组

 **设定扫描组最小数量为50，发现耗时反而更多，有947.14秒**

 **![14.png](https://image.3001.net/images/20180327/15221321809919.png!small)  
**

 **最小数量为100，耗时大幅度下降，613秒**

 **![13.png](https://image.3001.net/images/20180327/15221322034477.png!small)  
**

 **最小数量为200，发送了一个警告，耗时比数量100的组稍多，682秒**

 **![682.png](https://image.3001.net/images/20180327/1522132251845.png!small)  
**

  1. 测试并行发包率

 **同一时间至少发包100个。用时899秒**

 **![899.png](https://image.3001.net/images/20180327/15221322829572.png!small)  
**

 **同一时间至少发包150个，用时736.13秒**

**![哈哈哈.png](https://image.3001.net/images/20180327/15221323148294.png!small)**

5.结论增加并行扫描组和并行发包率可以大幅度节省扫描时间，不过这个值也不能无限制增大，可能和本地带宽或者是接口IO有关系，而且速度往往和准确度相挂钩，对准确度要求不大的可以试试提一个比较高的速度。
**  
**

## 0x02 lua 中的并发执行

lua采用coroutine的方式来实现并发执行。

  * `coroutine.create(f)`：用来完成对coroutine的创建工作。
  * `coroutine.resume(co,[,vall,...])`：用来完成将coroutine的状态从暂停变为运行。
  * `coroutine.running()`：返回当前正在执行的coroutine。
  * `coroutine.status(co)`：返回coroutine的状态。
  * `coroutine.wrap(f)`：作用同 coroutine.create()和 coroutine.resume()。
  * `coroutine.yield(...)`：用来暂停 coroutine。

## 0x03 NSE中的并发执行

在使用NSE处理并发执行时，并不需要考虑资源的保护，因为Nmap是单线程的。但是当在处理大规模的脚本实例时，就需要考虑网络的带宽以及socket的限制等问题。

在NSE中通过`stdNSE`库文件的函数`stdNSE.new_thread()`来支持NSE线程的创建。如建立一个线程：`stdNSE.new_thread(func,arg1,arg2,arg3,...)`

`func` 就是我们要在线程中执行的函数，`arg1,arg2...`就是这个函数里要传递进去的参数。

下面一段脚本，创建了3个线程，并将这三个线程执行完成。

    
    
    local stdNSE = require "stdNSE"
    ...
    function func1(host,port) ... end
    function func2(host,port) ... end
    function func3(host,port) ... end
    ...
    action = function(host,port)
        ...
    local thread1 = stdNSE.new_thread(func1,host,port)
    local thread2 = stdNSE.new_thread(func1,host,port)
    local thread3 = stdNSE.new_thread(func1,host,port)
    while true do
        if coroutine.status(thread1) == "dead" and coroutine.status(thread2) == "dead" and coroutine.status(threads3) == "dead" then
        break
        end
    stdNSE.sleep(1)
    end
    end
    

我们可以通过循环语句，来批量添加线程到`stdNSE.new_thread`去执行。下面是nmap的一个Web 服务动态发现脚本（`broadcast-wsdd-discover.nse`）关于线程的运用。

    
    
    -- 首先定义discoverThread函数，该函数要执行线程操作
    discoverThread = function( funcname, results )
      local condvar = nmap.condvar( results )
      ...
    end
    ...
    action = function()
    
      local threads, results = {}, {}
      local condvar = nmap.condvar( results )
    
      -- 尝试发现设备和 WCF web 服务
      -- 建立for循环，遍历{"discoverDevices", "discoverWCFServices"}作为discoverThread的参数
      for _, f in ipairs( {"discoverDevices", "discoverWCFServices"} ) do
        --线程添加
        threads[stdnse.new_thread( discoverThread, f, results )] = true
      end
    
      local done
      -- 等待所有的线程完成
      while( not(done) ) do
        done = true
        for thread in pairs(threads) do
          if (coroutine.status(thread) ~= "dead") then done = false end
        end
        if ( not(done) ) then
          condvar("wait")
        end
      end
    ...
    end
    

在NSE线程控制中，可以使用条件变量来控制脚本的执行流程。可以使用`Nmap
API`和函数`Nmap.condvar()`创建一个条件变量。上述脚本`local condvar = nmap.condvar( results
)`就是一个条件变量。

`Nmap.condvar()`的参数可以是除了nil、布尔类型、数值型以外的任何类型。对于一个条件变量可以进行的操作包括如下三个。

  * wait
  * broadcast
  * signal

这里所有需要处理的线程都按顺序存放在一个等待队列中。

  1. 当一个线程调用wait函数之后，可以加入到这个队列中；
  2. 当一个线程调用signal函数之后，可以从这个队列中释放出来，然后恢复执行；
  3. 当一个线程调用broadcast函数之后，可以恢复所有线程的执行。

## 0x04 小结

本期主要介绍nmap中的并发执行机制，包括如何在lua和NSE去创建线程的操作。在nmap的脚本库当中，很多爆破脚本，或者是服务枚举，目录遍历等脚本都较为经常使用到线程并发的处理机制。NSE脚本中`Nmap.mutex()`函数还提供了类似python当中线程锁的机制，可以避免多个进程在同一时间对同一个资源进行操作，有兴趣的同学可以进一步深入研究。本期nmap定制化之并发处理介绍就到这里，我们下期见。

![qrcode_for_gh_223e082fe8a7_344.jpg](https://image.3001.net/images/20180327/15221327105947.jpg!small)  

 _ **注：本文仅限于学习和研究使用，禁止用于非法用途。一切非法用途，与原作者无关。**_

