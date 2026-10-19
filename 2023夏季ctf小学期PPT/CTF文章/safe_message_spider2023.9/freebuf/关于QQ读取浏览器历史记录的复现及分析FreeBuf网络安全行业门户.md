## 前言

前天有一个小朋友跑过来问我，雨老师，发生什么事了，我一看哦，原来是前几天，有人在v2ex和看雪上发表了QQ会读取chrom浏览器历史记录的文章引起了大家的广泛讨论，本人本着实事求是的原则准备自己复现一下看一看是否有这么回事，毕竟我的历史记录那可真是不堪入目，万一被TX的人读取到了我怕他们产生心理阴影，废话不多说开搞。

## 复现过程

使用Process Monitor来监控QQ和chrom浏览器的互动，先来设置上规则。

![图片.png](https://image.3001.net/images/20210121/1611195049_6008e2a9efe8ff1618698.png!small)

果真如原文章所说，在登录QQ十分钟以后，QQ开始了读取Chrome浏览器历史记录。

![1611195097_6008e2d9f1c932190af5f.png](https://image.3001.net/images/20210121/1611195097_6008e2d9f1c932190af5f.png)

QQ不可能只和google过去不，我们去掉一条规则，添加新的规则  
![图片.png](https://image.3001.net/images/20210121/1611195051_6008e2ab012f83fb5252a.png!small)果然是这样的，QQ：我不是针对谁，我只想说在座的各位我都想读，我大意了哈，原来是QQ遍历了Appdata\Local\下的所有文件夹，然后拼接上User
Data\Default\History去读取历史记录。User Data\Default\History是谷歌系浏览器默认的历史纪录存放位置。  
![1611195139_6008e30396ec4fc9b3e7f.png!small](https://image.3001.net/images/20210121/1611195139_6008e30396ec4fc9b3e7f.png!small)我们使用X32Dbg
附加QQ进程通过字符串搜索找到关键位置，进行分析。  
![1611195350_6008e3d688c793eb003b8.png!small](https://image.3001.net/images/20210121/1611195350_6008e3d688c793eb003b8.png!small)发现在模块apputil.dll中。

![1611195341_6008e3cd84a39983f08c6.png!small](https://image.3001.net/images/20210121/1611195341_6008e3cd84a39983f08c6.png!small)

在目录中找到文件，打开IDA进行分析。  
![1611195332_6008e3c4b5fa67d162732.png!small](https://image.3001.net/images/20210121/1611195332_6008e3c4b5fa67d162732.png!small)但是这里遇到一个问题，我本机QQ的AppUtil.dll中并找不到相关位置，然后我使用了网上下载的一个AppUtil.dll，感兴趣的可以从这里下载。<https://file.qwqdanchun.com/Temp/AppUtil.dll>  
关键位置就在.text段的510EFB98位置。  
![1611195317_6008e3b57a82b0982ffb7.png!small](https://image.3001.net/images/20210121/1611195317_6008e3b57a82b0982ffb7.png!small)下面咱们来分析一下他到底干了什么。  
前边读取内容部分的分析如下。  
先拼接字符串路径，读取各种 User Data\Default\History 文件，读到了就复制到Temp目录下的temphis.db。  
![1611195305_6008e3a99122e3b5af65d.png!small](https://image.3001.net/images/20210121/1611195305_6008e3a99122e3b5af65d.png!small)下面就是筛选一下读取的URL链接然后进行了一些操作(但是并没有传送回TX服务器，都是在用户本地完成的)。最后删除了temphis.db  
![1611195279_6008e38f2eab322f3f98b.png!small](https://image.3001.net/images/20210121/1611195279_6008e38f2eab322f3f98b.png!small)因为最后删除了temphis.db然后再结合后来的腾讯的道歉，感觉是我们误会了TX，接着往下分析

![图片.png](https://image.3001.net/images/20210121/1611195052_6008e2acbee63abe5c620.png!small)

因为读取历史记录是在另一个线程读取的，我们跳转到读取历史记录函数的外层函数来分析，这里判断了DomainName是不是tencent.com或者是否存在SNGPERF，如果条件满足那么v2=1  
![1611195257_6008e379417a995f3fcb0.png](https://image.3001.net/images/20210121/1611195257_6008e379417a995f3fcb0.png)那么下面如果v2=1就不会读取历史记录，如果不是TX内部环境就开线程读取历史记录。？？？？？？我TM直接好家伙  
![1611195231_6008e35f509e432e1f521.png!small](https://image.3001.net/images/20210121/1611195231_6008e35f509e432e1f521.png!small)读取了URL后，计算URL的md5，比几个固定的md5值比较。  
![1611195221_6008e355626b18c93c8b8.png!small](https://image.3001.net/images/20210121/1611195221_6008e355626b18c93c8b8.png!small)如果md5匹配，会解析url分析&后面的参数，然后继续把这个参数做md5计算，和一些md5比较，匹配存入一块内存。  
有人使用脚本跑出来的MD5值内容。可以看到淘宝、天猫、京东等电商  
![图片.png](https://image.3001.net/images/20210121/1611195053_6008e2adc46552ab86408.png!small)分析到这里个人觉得真相应该大白了，但是还是不知道那个判断SNGPERF是什么，百度google也没有什么结果，就先到这里把。

## 结语

腾讯在事情发生得第一时间也发布了道歉。。

![图片.png](https://image.3001.net/images/20210121/1611195055_6008e2af12ae751b3e18d.png!small)

而且最新版的QQ已经把问题解决了删除了相关代码。所以这种事情大家没有必要过于担心。

![1611195191_6008e33700d05e94859be.png!small](https://image.3001.net/images/20210121/1611195191_6008e33700d05e94859be.png!small)

## 参考链接

<https://bbs.pediy.com/thread-265359.htm>  
[https://mp.weixin.qq.com/s/y9U2p-qnuG6jm61lERtQjQ﻿](https://mp.weixin.qq.com/s/y9U2p-qnuG6jm61lERtQjQ)

