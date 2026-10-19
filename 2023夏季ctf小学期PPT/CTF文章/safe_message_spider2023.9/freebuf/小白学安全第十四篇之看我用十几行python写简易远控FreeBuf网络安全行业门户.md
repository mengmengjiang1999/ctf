刚开始学习编程的同学可能经常会问：“我学了这个干什么用？买菜的时候掏出电脑来编个程序算算多少钱？”

其实，这跟大家的知识面和入门选择的语言有很大关系，大部分同学会选择C语言来入门编程，C语言虽然简洁，但是面向过程的编程方式总会让人觉得枯燥无味，无所适从。

那咱们现在做个有意思的，做个超级简易的远程控制软件，好吧~其实顶多算个脚本。

既然是远控，那就需要确定两个功能：

### 1、远程

即通过网络访问外部主机（包括内网），我们可以利用Python中封装好的 socket库，可以实现远程传输文本、文件、视频等。

Python socket详情介绍

### 2、控制

控制，最简单的理解就是执行命令，那么我们可以采用Python中的 os库，即可执行Linux shell 命令。

Python os详情介绍

下面就是代码，保存成.py文件,然后先执行server.py 再执行 client.py。

服务端，保存成server.py

#!/usr/bin/envpython

# -*-coding:utf-8 -*-
importsocket

import os

line=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

line.bind(('服务器IP',监听端口))

line.listen(5)

print('waitingcommd------->')

whileTrue:

conn,addr=line.accept()

msg=conn.recv(1024)

if msg == 'q':

break

print('get commd:',msg)

result=os.popen(msg).read()

conn.send('result: '+result)

conn.close()

phone.close()

客户端 保存成client.py

#!/usr/bin/env python

# -*- coding:utf-8 -*-
import socket

while True:

line=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

line.connect(('服务器IP',监听端口))

msg = str(raw_input('please inputcommd:'))

line.send(str(msg).encode('utf-8'))

data=phone.recv(1024)

print data

line.close()

执行结果如下：

![1.png](https://image.3001.net/images/20180712/15313643578040.png!small)  

服务端执行结果

![2.png](https://image.3001.net/images/20180712/15313643853570.png!small)

客户端在服务端执行 ls 命令后返回的结果

![3.png](https://image.3001.net/images/20180712/15313643955182.png!small)  

