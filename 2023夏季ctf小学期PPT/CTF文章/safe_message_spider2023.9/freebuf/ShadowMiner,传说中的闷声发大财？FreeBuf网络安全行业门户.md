1\. **简述**

深信服EDR安全团队追踪到一个新型的挖矿病毒，深信服安全专家研究发现，此挖矿病毒构造复杂，善于伪装，像影子般依附到系统环境。

目前该病毒已挖得3350个门罗币，获利约合人民币268万人民币，但令人惊讶的是，目前仍然未被发现（闷声发大财的典型代表），深信服已将其命名为ShadowMiner，并制定了相关的应对措施。

![图片.png](https://image.3001.net/images/20180904/1536049492_5b8e4154c6882.png!small)

下图，是收集到的五个相关样本。

![图片.png](https://image.3001.net/images/20180904/1536049498_5b8e415ae5913.png!small)2\.
**病毒分析**

2.1 **病毒流程** ****

病毒的整体流程如下，其中病毒母体为x1.exe，WmiApSvr.exe为开源的挖矿软件XMRig。

![图片.png](https://image.3001.net/images/20180904/1536049515_5b8e416be35b6.png!small)

 **2.2. 病毒母体分析** ****

病毒母体x1.exe主要有四个主要的恶意行为：注册服务、释放文件、下载文件、创建进程

![图片.png](https://image.3001.net/images/20180904/1536049525_5b8e4175d8842.png!small)  

 **2.2.1. 注册服务** ****

 ****

检查服务clr_optimization_v3.0.50727_32是否存在，没有则创建该服务。

![图片.png](https://image.3001.net/images/20180904/1536049535_5b8e417fde2c8.png!small)

服务对应的文件为C:\Windows\Microsoft.NET\Framework\mscorsvw.exe，此时该文件还未创建，所以服务也处于停止状态。

![图片.png](https://image.3001.net/images/20180904/1536049544_5b8e418839308.png!small)

服务运行的参数为aspnet_wp.exe。

![图片.png](https://image.3001.net/images/20180904/1536049554_5b8e4192f2ac2.png!small)

 **2.2.2. 释放文件** ****

病毒母体通过Trigger+函数地址的方式进行API的动态调用，这大大增加了逆向者的分析难度。什么是Trigger呢？Trigger就像一个装载器，将函数参数和要调用的函数地址传给它，它就能自动进行函数调用。如下是病毒使用该方法进行创建文件、修改文件属性、查询文件，经过这轮操作，文件mscorsvw.exe、aspnet_wp.exe、MpMgSvc.dll被创建。

![图片.png](https://image.3001.net/images/20180904/1536049564_5b8e419c47bb6.png!small)

我们后续发现，这个mscorsvw.exe是个合法软件，原名叫srvany.exe，srvany.exe是Microsoft Windows
Resource
Kits工具集的一个实用的小工具，用于将任何EXE程序作为Windows服务运行。也就是说srvany只是其注册程序的服务外壳，真正运行的是恶意文件aspnet_wp.exe。

![图片.png](https://image.3001.net/images/20180904/1536049574_5b8e41a61a749.png!small)

 **2.2.3. 下载文件** ****

下载http：//122.49.66.39/11.exe，重命名为本地的C:\windows\ime\64.exe。

![图片.png](https://image.3001.net/images/20180904/1536049584_5b8e41b08bb08.png!small)  

 **2.2.4. 创建恶意进程** ****

创建进程aspnet_wp.exe。

![图片.png](https://image.3001.net/images/20180904/1536049593_5b8e41b9aa37c.png!small)

aspnet_wp.exe运行后拉起了一个svchost.exe后便退出了。

![图片.png](https://image.3001.net/images/20180904/1536049603_5b8e41c38aefd.png!small)

下载完64.exe后，便调用CreateProcess执行了它。

![图片.png](https://image.3001.net/images/20180904/1536049613_5b8e41cd7184b.png!small)  

64.exe的行为跟aspnet_wp.exe的很像，都是拉起了一些进程后退出。

![图片.png](https://image.3001.net/images/20180904/1536049624_5b8e41d8251b6.png!small)

最后，系统中只剩下恶意进程svchost.exe和WmiApSvr.exe，我们也可以看到WmiApSvr.exe已经开始挖矿了。

![图片.png](https://image.3001.net/images/20180904/1536049636_5b8e41e48ccc6.png!small)

 **2.3. aspnet_wp分析** ****

 ****

从上文我们得知aspnet_wp.exe的恶意行为就是拉起svchost.exe然后退出，按照病毒的常规操作，它退出前会将恶意代码注入到svchost.exe中，所以分析aspnet_wp时我们重点关注进程注入操作。
****

![图片.png](https://image.3001.net/images/20180904/1536049646_5b8e41eecaa0b.png!small)

 **2.3.1. 创建进程** ****

创建合法进程svchost.exe。

![图片.png](https://image.3001.net/images/20180904/1536049655_5b8e41f78525a.png!small)

 **2.3.2. 注入代码** ****

 ****

调用WriteVirutalMemory往svchost.exe内存里写入恶意代码。 ****

![图片.png](https://image.3001.net/images/20180904/1536049665_5b8e42019f251.png!small)

 **2.3.3. 木马通信** ****

尝试与C&C服务器进行通信。

![图片.png](https://image.3001.net/images/20180904/1536049675_5b8e420b47272.png!small)

通过抓包得知， **aaaa.usa-138.com** 对应的IP为123.142.209.27。而且现在无法跟C&C服务器进行连接。

![图片.png](https://image.3001.net/images/20180904/1536049683_5b8e4213e850f.png!small)

 **2.3.4. 自隐藏** ****

 ****

调用SetFileAttributesA将自身设置为隐藏属性。

![图片.png](https://image.3001.net/images/20180904/1536049692_5b8e421c3b331.png!small)  

 **2.4. 64.exe分析** ****

![图片.png](https://image.3001.net/images/20180904/1536049701_5b8e422573838.png!small)

**2.4.1. 注册服务** ****

 ****

64.exe跟病毒母体一样，也会创建一个伪装服务，伪装的服务名为Services。这个服务对应的可执行文件是MSBuild.exe，功能是运行Paramters里的二进制文件，即间接运行Services.exe。

![图片.png](https://image.3001.net/images/20180904/1536049710_5b8e422e6930b.png!small)

 **2.4.2. 清除异己** ****

接着64.exe会清除其他同行以保证独占CPU进行挖矿，首先会调用sc删除很多服务，其中包括WannaMine2.0。

![图片.png](https://image.3001.net/images/20180904/1536049719_5b8e4237d08ca.png!small)

添加防火墙策略，关闭SMB端口。

![图片.png](https://image.3001.net/images/20180904/1536049729_5b8e42416f61d.png!small)

 **2.4.3. 执行挖矿** ****

运行Services.exe，Services.exe的主要功能为释放及运行挖矿软件WmiApsver.exe。

![图片.png](https://image.3001.net/images/20180904/1536049738_5b8e424ad09da.png!small)

释放WmiApSvr.exe到C:\Program Files\Common Files\Services路径下。

![图片.png](https://image.3001.net/images/20180904/1536049746_5b8e425237779.png!small)

运行挖矿软件WmiApSvr.exe，钱包地址为：49e9B8HxzSbMWsNbMs72aVe78U9CCE2DAM5aDJYNeccWNvWiKfrPaGeewmTAjj6nt6Bqzob4zaRjLXfpW1WfRMnzEAQBHy7。

![图片.png](https://image.3001.net/images/20180904/1536049754_5b8e425acc1bb.png!small)

开始挖矿！

![图片.png](https://image.3001.net/images/20180904/1536049764_5b8e4264536a4.png!small)

 **2.4.4. 自删除** ****

为自己的临时文件创建一个进程，主要目的为对64.exe进行自删除。

![图片.png](https://image.3001.net/images/20180904/1536049773_5b8e426d4974c.png!small)

这是DEZ_7379.tmp的代码，首先结束64.exe进程。  

![图片.png](https://image.3001.net/images/20180904/1536049780_5b8e4274eb9c4.png!small)  
  

然后删除64.exe。

![图片.png](https://image.3001.net/images/20180904/1536049796_5b8e4284cd3f8.png!small)  

## 3\. **解决** **方案** ****

[1] 内网检测：深信服防火墙、深信服安全感知支持挖矿病毒检测，使用该类产品，可以快速定位企业内网感染挖矿病毒的主机。

[2] 结束进程：WmiApSvr.exe、svchost.exe（注意是没有父进程的svchost.exe）。

[3] 删除如下文件：

x1.exe

64.exe

C:\Windows\Microsoft.NET\Framework\aspnet_wp.exe

C:\Program Files\MSBuild\Services.exe

C:\Program Files\Common Files\WmiApSvr.exe

[4] 删除服务：clr_optimization_v3.0.50727_32、Services。

