# 深度分析CobaltStrike（一）—— Beacon生成流程及Shellcode分析

阅读量 **361234**

|评论 **3**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-04-12 14:30:55

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t01d1c8cc0b794dca07.jpg)

## 项目框架

首先拿到网上流传的破解版CobaltStrike4.1，并针对项目进行反编译，可以看到项目目录如下

![](https://p1.ssl.qhimg.com/t0120d563d73d210bd6.png)

代码目录较多，由于需要分析的是Beacon的生成，因此我们暂时只关心以下几个目录

  * aggressor(主要负责构建CobaltStrike的GUI功能)
  * beacon(beacon上线以及后续交互等一系列行为的具体实现)
  * stagers(生成各类不同的stagers shellcode)
  * common(可以理解成utils，包含一些常用功能的实现)

## 上线流程

在正式开始分析之前，先要对CS(CobaltStrike，后续简称CS)的机制有一个直观的认识，这里借用gcow团队的一张图进行讲解

![](https://p0.ssl.qhimg.com/t010c0a2f0e3c3bdfac.png)

当我们通过TeamServer生成了beacon文件后，并在靶机上执行该文件，会产生以下行为

  * 靶机主动请求生成beacon时所选择的Listener
  * 攻击者通过TeamServer发现目标机器已上线
  * 借助TeamServer下发指令给beacon执行(异步或同步)

## Beacon生成

###  Stage&Stageless

首先需要清楚的是，Beacon的生成有两种模式

![](https://p4.ssl.qhimg.com/t0121872c7e3e09a603.png)

  * stage (有阶段)
  * stageless (无阶段)

所谓的stage(有阶段)，指的是Beacon会分段的加载shellcode(具体表现为，通过不断的向Listener发起请求，最终获取一个完整的shellcode并执行)，stageless(无阶段)，则是在生成时则包含完整的shellcode。

###  流程分析

由于stage和stageless的生成流程相似，所以接下以stage的生成为例，来跟进代码进行分析，首先是`WindowsExecutableDialog`这个类，其作用是处理`Windows
Executable`这个会话框的action，有两个主要的函数，一个是`dialogAction`，一个是`dialogResult`，其中`dialogResult`是回调函数。

![](https://p0.ssl.qhimg.com/t019510065305194597.png)

`dialogAction`整体的处理流程非常简单，通过调用当前`Listener`的`getPayloadStager`函数，获取对应的shellcode，跟进分析，最终调用的函数为`GenericStager`的`generate`

![](https://p2.ssl.qhimg.com/t017ece878c8d85606b.png)

可以看到`GenericStager`是一个抽象类，`generate`是接口，这里以`Listener`为http为例，跟进到`GenericHTTPStager`的`generate`中

![](https://p2.ssl.qhimg.com/t011554ad69a3e8bb54.png)

通过`getStagerFile`获取shellcode的模板文件

![](https://p4.ssl.qhimg.com/t01dff5596be6ea6118.png)

跟进后发现读取的是`resources/httpstager64.bin`文件 (后面会单独分析该文件)

![](https://p1.ssl.qhimg.com/t01dc2f70112e9fc7bf.png)

继续跟进`GenericHTTPStager`的`generate`函数，首先`new`了一个`Packer`类，通过阅读该类的函数可知，该类用于操作二进制文件。继续往下走，可以看到反复使用`Packer`类替换了shellcode的端口/Header/URI等

![](https://p1.ssl.qhimg.com/t01cdc78361d60dff45.png)

shellcode生成后，会调用`dialogResult`回调函数进行处理，其中传入的`var1`为`generate`生成的Shellcode，这里以64位exe为例，继续跟进`patchArtifact`函数

![](https://p3.ssl.qhimg.com/t01cb3bb9102da094f1.png)

首先去`resources`目录下取了`artifact.exe`文件的模板

![](https://p1.ssl.qhimg.com/t01263da1a7d80ae481.png)

![](https://p3.ssl.qhimg.com/t0165623f6ee0fb1a94.png)

通过生成随机数`var6`，异或之前传入的shellcode，并找到1024个A所在的位置(需要替换为shellcode)的位置，将异或后的shellcode写入，最终生成完整的PE文件

###  Beacon外壳分析

将生成的`artifact.exe`拖到IDA里面分析，首先找到main函数

![](https://p4.ssl.qhimg.com/t01cf7e7c4b30d66897.png)

在`main`函数中，先后调用了`sub_402A60`和`sub_401795`两个函数，直接跟进`sub_401795`进行分析

![](https://p3.ssl.qhimg.com/t018de0cf3f59421587.png)

可以看到先初始化了变量`Buffer`，格式为`%c%c%c%c%c%c%c%c%cMSSE-%d-server`，然后调用`CreateThread`执行`sub_401605`函数，跟进分析

![](https://p0.ssl.qhimg.com/t01da9f099e3fb33178.png)

![](https://p2.ssl.qhimg.com/t01fe88f493351e4be0.png)

先前格式化的`Buffer`名称，在`sub_4015D0`中被用于创建命名管道，然后将`lpBuffer`中的值写入到管道中，而传入的`lpBuffer`，实际指向`unk_404014`

![](https://p3.ssl.qhimg.com/t012f83abfa0d8c8c26.png)

回到`sub_401795`中，继续往下走，在return的时候调用了`sub_401742`

![](https://p2.ssl.qhimg.com/t01fb9a7dc7b8688e81.png)

![](https://p1.ssl.qhimg.com/t01afcebe69a4393264.png)

在`sub_4016A2`中，将之前写入管道的数据读到了`v0`当中

![](https://p4.ssl.qhimg.com/t0145ab7d4777674560.png)

将读出的数据传入到函数`sub_40152E`中，针对该数据进行解异或操作，然后将其作为参数传入`CreateThread`，走到这里可以判断，先前写入管道的数据，即为异或后的shellcode

![](https://p2.ssl.qhimg.com/t01d1568462eb245196.png)

![](https://p2.ssl.qhimg.com/t017296d1105ab1d23c.png)

对比先前的`_patchArtifact`函数以及IDA反编译后，解异或所用的数据`unk_404014`，可以发现是温和的，后面正好跟了两个值为0的`dword`

###  Shellcode分析

![](https://p4.ssl.qhimg.com/t01f26d32ff78810daf.png)

首先调用`LoadLibrary`加载`wininet.dll`，其中rbp所指向的函数`sub_160001`为寻找加密哈希所对应的函数，此处`726774C`对应的为`LoadLibrary`

![](https://p0.ssl.qhimg.com/t013a08192a0692ecbd.png)

![](https://p2.ssl.qhimg.com/t01ba031af1e8a222c0.png)

紧接着调用`IntenetOpenUrlA`传入了5个NULL值

![](https://p1.ssl.qhimg.com/t014c7b3b60ef4c08f2.png)

![](https://p0.ssl.qhimg.com/t0124aeb5d34b380365.png)

紧接着调用`InternetConnectW`连接先前`CobaltStrike Listener`中配置的IP

![](https://p4.ssl.qhimg.com/t01a72224bf84317972.png)

![](https://p3.ssl.qhimg.com/t012e1117bf8ac5cf1b.png)

`InternetConnectW`返回的句柄，传入到`HttpOpenRequestW`中，对应的url为`C2zn`

![](https://p5.ssl.qhimg.com/t01513f2079dff0504b.png)

![](https://p5.ssl.qhimg.com/t0158fac3f403fe537f.png)

使用`HttpSendRequestA`发送请求，并设置请求头

![](https://p0.ssl.qhimg.com/t01fa839944d3f07a4b.png)

通过`InternetReadFile`循环读取C2的数据，并写入到用`VirtualAlloc`申请的内存中，读取完毕后，跳转到写入数据所在的地址并执行

###  通过hash调用函数

上文所有的函数调用，都是通过将hash写入到`r10d`中，再交由`sub_160001`进行判断，那`sub_160001`是怎么判断的呢？

![](https://p1.ssl.qhimg.com/t01f78b5790ae81648f.png)

将参数压入栈后，做了一系列的寻址操作。首先是`gs:[rdx+60]`，`gs`这个段寄存器，代表的是`TEB`的地址(线程环境变量块)

![](https://p2.ssl.qhimg.com/t01334eebce8c84ba1c.png)

`TEB`偏移0x60的地方，是`PEB`(进程环境变量块)，接着寻址了`PEB`偏移0x18的地址

![](https://p3.ssl.qhimg.com/t0106db13e9feeef368.png)

`PEB`偏移0x18的地方，是`Ldr`，而`Ldr`，存放了进程所加载的动态链接库的信息

![](https://p1.ssl.qhimg.com/t015c5a26b60dc5658f.png)

`PEB`偏移0x20的地方是`InMemoryOrderModuleList`，这是一个双向链表，每个指针都指向一个`_LDR_DATA_TABLE_ENTRY`结构

![](https://p2.ssl.qhimg.com/t01de94b54a61398006.png)

![](https://p3.ssl.qhimg.com/t0149b59f6fb104c5c6.png)

由于`InMemoryOrderModuleList`指向的是`_LDR_DATA_TABLE_ENTRY`中的`InMemoryOrderLinks`而非首地址，因此
`ds:[rdx+20]`指向的是`DllBase`，也就是Dll的基地址

![](https://p3.ssl.qhimg.com/t0148ab44aabaa6e0f2.png)

`ds:[rdx+3C]`则是`IMAGE_DOS_HEADER`中的`e_lfanew`，它指向了实际的PE头

![](https://p1.ssl.qhimg.com/t0155b43dbeaf1beef1.png)

`ds:[rax+18]`指向`OptionalHeader`，该结构首地址指向了一个魔数，代表PE文件的类型(32/64)，因此`cmp word ptr
ds:[rax+18],20B`用于判断PE文件类型

![](https://p2.ssl.qhimg.com/t011e6ec6f819422ffd.png)

接着将`ds:[rax+88]`的地址存到`eax`中，而`ds:[rax+88]`实际指向`DataDirectory`(0x18+0x70=0x88)

![](https://p5.ssl.qhimg.com/t01b225baa701118219.png)

`DataDirectory`数组的第一个元素就是导出表，因此此时`eax`中的地址为导出表的地址

![](https://p4.ssl.qhimg.com/t016513f2a6f548c79d.png)

`ds:[rax+18]`和`ds:[rax+20]`分别对应函数的数量以及导出表的RVA

![](https://p0.ssl.qhimg.com/t014f5692025c1f5d7b.png)

接着就是遍历导出表，计算函数hash，判断跟传入的hash是否一致，如果一致则调用

## 总结

本篇文章深入的剖析了`Beacon`生成流程及`Shellcode`分析，后面的文章会着重分析CS的通信流程以及`Beacon`的模块加载，以及基于这些深度分析的免杀思考

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **D_infinite** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/237127](/post/id/237127)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [shellcode](/tag/shellcode)
  * [Cobalt Strike](/tag/Cobalt Strike)
  * [安全开发](/tag/安全开发)
  * [红蓝对抗](/tag/红蓝对抗)
  * [CS](/tag/CS)

 **+1** __11赞

 __收藏

![](https://p2.ssl.qhimg.com/t01fef30e40d37bd4a2.png) D_infinite

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

