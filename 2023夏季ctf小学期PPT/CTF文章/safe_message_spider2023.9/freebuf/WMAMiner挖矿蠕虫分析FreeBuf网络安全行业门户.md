## 概述

**近日，兰云科技银河实验室在多个监测点用“兰眼下一代威胁感知系统”检测到多起同类未知威胁事件，杀毒软件检测率非常低，经过分析发现这是某个挖矿僵尸网络的肉鸡更新程序，为了躲避杀毒软件查杀，特地将主控程序加密并放到资源中。样本通过MS17-010（永恒之蓝）漏洞进行传播，定时和C
&C进行连接接受命令和更新模块，主要目的为挖掘门罗币，基于挖矿木马的典型行为，我们将此蠕虫组建的僵尸网络命名为WMAMiner botnet。**

![image.png](https://image.3001.net/images/20180519/15267083248403.png!small)  

兰眼下一代威胁感知系统检测截图  

![image.png](https://image.3001.net/images/20180519/15267083626347.png!small)

![image.png](https://image.3001.net/images/20180519/15267083935095.png!small)

VirusTotal检测截图  

## 0x1 释放主控样本

通过分析发现僵尸网络拥有x86和x64平台的恶意组件，这里以x86平台作为分析，样本首先获取系统目录并和下面字符串拼接，拼接出如下:

> C:\WINDOWS\system32\EnrollCertXaml.dll
>
> C:\WINDOWS\system32\wmassrv.dll
>
> C:\WINDOWS\system32\WMASTrace.ini

![1.png](https://image.3001.net/images/20180519/15267084916618.png!small)

首先删除上面三个文件

![image.png](https://image.3001.net/images/20180519/15267085113049.png!small)

之后获取资源，创建并写入文件C:\WINDOWS\system32\EnrollCertXaml.dll中

![image.png](https://image.3001.net/images/20180519/15267085319086.png!small)  
这个文件并不是一个可执行文件

![image.png](https://image.3001.net/images/20180519/15267085444245.png!small)

先是读入文件内容然后解密将解密的内容写入C:\WINDOWS\system32\wmassrv.dll中

![image.png](https://image.3001.net/images/20180519/15267085604325.png!small)  

可以发现解密后是一个可执行文件

![image.png](https://image.3001.net/images/20180519/15267085724154.png!small)

之后是获取C:\WINDOWS\system32\svchost.exe的文件时间，并设置成wmassrv.dll、EnrollCertXaml.dll的文件时间

![image.png](https://image.3001.net/images/20180519/15267085856258.png!small)

可以看到这样文件的修改时间就跟系统其他文件的修改时候大致相同了，对主机检查起到一定的迷惑效果

![image.png](https://image.3001.net/images/20180519/15267085981435.png!small)  

之后便是设置wmassrv.dll为服务程序，并设置持久化

![image.png](https://image.3001.net/images/20180519/15267086114876.png!small)  
![image.png](https://image.3001.net/images/20180519/15267086219984.png!small)  
最后删除自身

![image.png](https://image.3001.net/images/20180519/15267086381366.png!small)  
  

## 0x2 主控模块

主控模块流程图

![image.png](https://image.3001.net/images/20180519/15267087044818.png!small)

作为服务的主控模块，会首先创建C:\WINDOWS\system32\WMASTrace.ini，并写入一个加号

![image.png](https://image.3001.net/images/20180519/15267087298749.png!small)

会先停止一些服务，一些是之前僵尸网络留下的服务

![image.png](https://image.3001.net/images/20180519/15267087462771.png!small)  

在初始化之后，便是开启多线程，每个线程都是一个模块

### 0x2.1 更新模块

每5个小时连接 sand.lcones.com和plam.lcones.com 两个地址  

![image.png](https://image.3001.net/images/20180519/15267087731785.png!small)  

如果连接成功，样本会首先连接sand.lcones.com/resource  

![image.png](https://image.3001.net/images/20180519/15267087977270.png!small)  

如果有内容会下载plam.lcones.com/modules.dat  

![image.png](https://image.3001.net/images/20180519/15267088105968.png!small)

如果返回值等于200

![image.png](https://image.3001.net/images/20180519/15267088255660.png!small)  

写入EnrollCertXaml.dll 文件中  

![image.png](https://image.3001.net/images/20180519/15267088377426.png!small)  

### 0x2.2 C&C通信模块

本样本共有两个C&C地址，一个是通过http协议进行通信，一个是通过tcp协议进行通信

 **0x2.2.1 HTTP 通信**

通信地址为tecate.traduires.com,没隔5隔小时连接一次

![image.png](https://image.3001.net/images/20180519/15267088757998.png!small)

收集系统信息  

![image.png](https://image.3001.net/images/20180519/1526708889180.png!small)  

拼接成如下图所示，并发送  

![image.png](https://image.3001.net/images/20180519/15267089028266.png!small)

![image.png](https://image.3001.net/images/20180519/15267089112616.png!small)  

通过返回数据解析有下面三个命令

![image.png](https://image.3001.net/images/20180519/15267089228590.png!small)  

命令 0 启动某个进程

![image.png](https://image.3001.net/images/20180519/15267089334390.png!small)  

命令1 下载并执行 通过regsvr32.exe

![image.png](https://image.3001.net/images/20180519/15267089436945.png!small)  
![image.png](https://image.3001.net/images/20180519/15267089522170.png!small)  
命令2 下载到临时文件夹并执行

![image.png](https://image.3001.net/images/20180519/15267089654283.png!small)  

**0x2.2.2 TCP通信**

TCP通信模块也是5个小时连接一次

![image.png](https://image.3001.net/images/20180519/15267089862738.png!small)  

连接的域名为split.despcartes.tk，有趣的是在这里面做了些间接调用，隐藏了些关键函数

![image.png](https://image.3001.net/images/20180519/15267089988819.png!small)  

进行连接，端口为8080

![image.png](https://image.3001.net/images/20180519/15267090114614.png!small)

连接成功接收数据

![image.png](https://image.3001.net/images/20180519/15267090254231.png!small)

收集的发送系统信息

![image.png](https://image.3001.net/images/20180519/15267090387211.png!small)

![image.png](https://image.3001.net/images/20180519/15267090443034.png!small)

### 0x2.3 挖矿模块

释放TasksHostServices.exe
经过分析这个是开源门罗币挖掘工具<https://github.com/xmrig/xmrig/releases>

![image.png](https://image.3001.net/images/20180519/15267090621959.png!small)  

通过以下参数进行启动

![image.png](https://image.3001.net/images/20180519/15267090759163.png!small)

### 0x2.4 传播模块

![image.png](https://image.3001.net/images/20180519/15267090953999.png!small)

释放C:\WINDOWS\SpeechsTracing\spoolsv.exe 并执行，该模块会首先释放Crypt,而这个其实是一个ZIP压缩包

![image.png](https://image.3001.net/images/20180519/15267091108644.png!small)  

解压缩后我们发现是NSA泄露的漏洞利用包

![image.png](https://image.3001.net/images/20180519/15267091223570.png!small)

通过扫描内网445端口，进行传播

![image.png](https://image.3001.net/images/20180519/15267091357952.png!small)配置文件

![image.png](https://image.3001.net/images/20180519/1526709146586.png!small)

传播成功后，会将x86.dll或者64.dll作为payload,继续看看x86.dll的功能

首先会监听 52137端口

![image.png](https://image.3001.net/images/20180519/15267091594146.png!small)

![kk.png](https://image.3001.net/images/20180519/15267096275186.png!small)  

而这时spoolsv.exe会读取EnrollCertXaml.dll并连接并发送  

![image.png](https://image.3001.net/images/20180519/15267093228936.png!small)  

X86接收EnrollCertXaml.dll并解密出wmassrv.dll 注册成服务 开始下一轮传播  

![image.png](https://image.3001.net/images/20180519/15267093429041.png!small)  

### 0x2.5防止停止模块

样本还是实时查看电脑中是否开启了任务管理器，如果开启，则会关闭

![image.png](https://image.3001.net/images/20180519/15267093635831.png!small)![image.png](https://image.3001.net/images/20180519/15267093672939.png!small)

### 0x2.6 web服务器模块

会安装 开源WebHost\\\mongoose工具，作为服务器，监听 63257端口  

![image.png](https://image.3001.net/images/20180519/15267093927177.png!small)  

如果连接成功，则会发送EnrollCertXaml.dll  

![image.png](https://image.3001.net/images/20180519/15267094089484.png!small)

## 0x3 总结

近年随着区块链技术的兴起，区块链币的流行，黑客也越来越集中关注挖矿带来的经济利益，与之对应的挖矿类威胁越来越严重。此类木马在隐蔽性强，主动内网传播，建议客户部署相应安全设备，及时打好补丁，关闭445等端口，提前做好挖矿类威胁的安全防范。

## 0x4 IOC

> IP
>
> 103.103.128.140
>
> 103.212.69.170
>
> 185.128.24.117
>
> 216.250.99.32
>
> 样本MD5：
>
> 7d3cf6bce43a115399f0daaa4b425417
>
> 69d8e2d62cb2f8e2a23cc949ebdb4e3d

 *** 本文作者：兰云科技银河实验室，转载注明来自FreeBuf.COM**  

