
    声明：本脚本仅用于学习交流，请勿用于非法途径，造成的任何后果与本人无关

使用三方库：socket,threadpool

测试目标：127.0.0.1

程序原理：

使用socket对目标+端口创建连接，如果存在则代表端口开放

程序运行结果：

![1609737692_5ff2a5dc0593c02f5d225.png!small](https://image.3001.net/images/20210104/1609737692_5ff2a5dc0593c02f5d225.png!small)

程序代码：

    
    
    #!/usr/bin/python
    # -*- coding: UTF-8 -*-    '''
    多线程目录扫描器
    作者：木尤
    声明：本脚本仅用于学习交流，请勿用于非法途径，造成的任何后果与本人无关
    要点：需要安装requests,threadpool这俩个库
    '''
    
    import socket,threadpool
    ports=[]
    def scan_poort(port):
        ip='127.0.0.1'
        s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            statu=s.connect_ex((ip,port))
            if statu==0:
                print(port,'is open')
        except:
            pass
    
    def get_port():
        global ports
        for p in range(65536):
            ports.append(p)
    
    get_port()
    pool=threadpool.ThreadPool(100)
    reqs=threadpool.makeRequests(scan_poort,ports)
    [pool.putRequest(req) for req in reqs]
    pool.wait()

