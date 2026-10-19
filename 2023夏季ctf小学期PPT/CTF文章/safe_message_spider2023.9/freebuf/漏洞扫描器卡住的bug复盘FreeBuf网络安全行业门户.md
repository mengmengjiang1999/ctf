## 问题背景

之前线上的漏洞扫描遇到一个奇怪的问题:requests.get即使设置了timeout，仍然卡住。

看lijiejie大佬 [requests.get 异常hang住](http://www.lijiejie.com/requests-get-hang/)也碰到过这个问题。

所以，我想要探究以下问题:

> requests库中timeout参数的具体含义是什么?
>
> 为什么requests.get时timeout参数"失效"?

## 分析过程

### requests库中timeout参数的具体含义是什么?

 **requests库中timeout参数是什么?**

根据[官网文档](https://docs.python-requests.org/en/master/user/advanced/#timeouts)所说,timeout可以表示(connect超时时间,read超时时间)

 **什么是connect超时?**

客户端需要connect系统调用来和服务端做tcp三次握手，当服务地址在互联网上不存在时，connect系统调用耗时就会比较长。

比如请求1.1.2.3 过一段时间后会返回一个connect tiemout:

    
    
    python -c 'import requests;requests.get("http://1.1.2.3")'
    

在上面请求1.1.2.3这个不存在的ip时，客户端发出的 syn 包没有任何响应，于是客户端会重传syn包

> 重传次数在 /proc/sys/net/ipv4/tcp_syn_retries 可以配置
>
> 重传间隔时间并不是固定的，在Linux系统上测试结果是 [1,3,7,15,31]s，似乎就是 2^(n+1)-1

如果重试完后仍然没有收到ack包，就会出现connect timeout

而request的timeout参数就可以减少这个等重传的时间。

    
    
    python -c 'import requests;requests.get("http://1.1.2.3", timeout=(1, 100))' # 1s的connect超时设置
    

**怎么实现的connect超时控制?**

connect、read等系统调用是没有参数可以控制超时时间的，那connect超时控制是怎么实现的呢?

在Modules/socketmodule.c可以找到connect函数的实现

    
    
    1. socket设置成非阻塞模式
    
    ...
    sock_call_ex(...,_PyTime_t timeout) {
      ...
      interval = timeout;
      ...
      res = internal_select(s, writing, interval, connect);
      ...
    }
    
    static int internal_select(PySocketSockObject *s, int writing, _PyTime_t interval,
                int connect){
      ...
      ms = _PyTime_AsMilliseconds(interval, _PyTime_ROUND_CEILING);
      ...
      n = poll(&pollfd, 1, (int)ms);  2. poll系统调用，如果超时,poll系统调用就会返回
    

流程如下:

    
    
    * 设置socket为非阻塞模式后，调用connect系统调用
    * 使用poll系统调用来判断是否超时
    

实际上这是一种很通用的对connect做超时控制的方式，在其他tcp客户端中也可以这么实现超时控制。

 **什么是read超时?**

客户端需要调用read系统调用来读取服务端发送的数据，如果服务端一直不发送数据，读数据时就会卡住。

比如我们用nc命令开启一个服务端只负责监听建立链接,不发送数据.

    
    
    nc -l 8081
    

客户端请求nc开启的服务,代码如下,3s后会出现读超时

    
    
    import requests
    requests.get("http://127.0.0.1:8081", timeout=(1,3)) # read超时时间设置成3s
    

### 为什么requests.get时timeout参数"失效"?

requests.get在 dns解析、connect、read 这些阶段都有可能耗时比较久。下面分别说一下timeout在这三个阶段中是否生效。

文档中只说了timeout控制connect、read两个阶段，说明dns解析耗时很久时timeout是管不了的。  
我自己实验，也得出相同的结论：dns解析时间即使超过timeout，也不会抛出异常。

connect阶段在上面已经分析过，timeout是可以控制这一阶段最多花费多长时间的。

Python中的read超时不是一个全局的时间，它只是在每一次读socket时不能超过这个时间。而一次响应的读取可能有多次read操作。这儿可能和其他的http客户端（比如curl）等超时时间含义不同。

如果服务端能够让客户端read非常多次，且每一次时间都不超过read timeout值，这个时候客户端会卡住。

所以，在下面两种情况下是会造成read timeout参数“失效”的:

> 响应中content-length是一个特别大的数，服务端缓慢的每次响应1字节
>
> 服务端返回的响应码是100，同时服务端持续不断地返回响应头，也会导致客户端持续不断的read

比如下面的服务端持续不断地返回响应头，会导致客户端卡住。

    
    
    # coding:utf-8
    from socket import *
    from multiprocessing import *
    from time import sleep
    
    def dealWithClient(newSocket,destAddr):
        recvData = newSocket.recv(1024)
        newSocket.send(b"""HTTP/1.1 100 OK\n""")
    
        while True:
            # recvData = newSocket.recv(1024)
            newSocket.send(b"""x:a\n""")
    
            if len(recvData)>0:
                # print('recv[%s]:%s'%(str(destAddr), recvData))
                pass
            else:
                print('[%s]close'%str(destAddr))
                sleep(10)
                print('over')
                break
    
        # newSocket.close()
    
    
    def main():
    
        serSocket = socket(AF_INET, SOCK_STREAM)
        serSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR  , 1)
        localAddr = ('', 8085)
        serSocket.bind(localAddr)
        serSocket.listen(5)
    
        try:
            while True:
                newSocket,destAddr = serSocket.accept()
    
                client = Process(target=dealWithClient, args=(newSocket,destAddr))
                client.start()
    
                newSocket.close()
        finally:
            serSocket.close()
    
    if __name__ == '__main__':
        main()
    

更多的讨论可以见提交的bug [urllib http client possible infinite loop on a 100 Continue
response](https://bugs.python.org/issue44022)

## 总结

请求在 dns解析、connect、read 这些阶段都有可能耗时很久，其中：

> dns解析阶段 不受timeout参数控制
>
> connect阶段 受timeout参数控制
>
> read阶段 timeout不是全局的，如果服务端让客户端有很多次read操作，就有可能让客户端卡住

阻塞时的connect系统调用是有默认的最大时间限制，这个和系统配置有关；可以用"非阻塞connect+select/poll"来实现connect的超时控制。

在排查这个case原因时，发现这里存在潜在的dos攻击问题，也上报给Python官方，很快被修复了。

