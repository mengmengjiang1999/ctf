***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

##  **一、背景**

 **云鼎实验室曾分析不少入侵挖矿案例，研究发现入侵挖矿行为都比较粗暴简单，通过 top
等命令可以直接看到恶意进程，挖矿进程不会被刻意隐藏；而现在，我们发现黑客开始不断使用一些隐藏手段去隐藏挖矿进程而使它获得更久存活，今天分析的内容是我们过去一个月内捕获的一起入侵挖矿事件。**

##  **二、入侵分析**

本次捕获案例的入侵流程与以往相比，没有特殊的地方，也是利用通用漏洞入侵服务器并获得相关权限，从而植入挖矿程序再进行隐藏。

通过对几个案例的分析，我们发现黑客主要是利用 Redis 未授权访问问题进行入侵，对于该问题的说明可以参考我们过去做的一些分析：

>
> [https://mp.weixin.qq.com/s/inazTPN5mHJYnt2QDliv8w](https://mp.weixin.qq.com/s?__biz=MzU3ODAyMjg4OQ==&mid=2247483874&idx=1&sn=06baad6c0a11a3ee2c3e5bba13fd69c2&scene=21#wechat_redirect)

在服务器被入侵后，首先可以明显感觉到服务器的资源被占用而导致的操作迟缓等问题，通过一些常规手段可以发现一些异常信息，但又看不到进程信息：

![](https://image.3001.net/images/20180625/1529935510152.png!small)通过 top
命令，可以看到显示的 CPU 使用率较低，但 ni 值为 100 ；同时通过 /proc/stat 计算 CPU 使用率又基本是 100% 。

![](https://image.3001.net/images/20180625/15299355406773.png!small)通过 netstat
查看端口监听情况，也可以看到异常的连接。

![](https://image.3001.net/images/20180625/15299355712225.png!small)

通过在 Virustotal 查询 IP，可以看到 DNS 指向为矿池域名。

通过 find 命令查找入侵时间范围内变更的文件，对变更文件的排查，同时对相关文件进行分析，基本可以确认黑客使用的进程隐藏手法。

![](https://image.3001.net/images/20180625/15299356233704.png!small)![](https://image.3001.net/images/20180625/152993564052.png!small)

在变更文件里可以看到一些挖矿程序，同时 /etc/ld.so.preload 文件的变更需要引起注意，这里涉及到 Linux
动态链接库预加载机制，是一种常用的进程隐藏方法，而 top 等命令都是受这个机制影响的。

> 在 Linux 操作系统的动态链接库加载过程中，动态链接器会读取 LD_PRELOAD 环境变量的值和默认配置文件 /etc/ld.so.preload
> 的文件内容，并将读取到的动态链接库进行预加载，即使程序不依赖这些动态链接库，LD_PRELOAD 环境变量和 /etc/ld.so.preload
> 配置文件中指定的动态链接库依然会被装载，它们的优先级比 LD_LIBRARY_PATH
> 环境变量所定义的链接库查找路径的文件优先级要高，所以能够提前于用户调用的动态库载入。
>
> ——段落引自《警惕利用 Linux 预加载型恶意动态链接库的后门》

通过查看文件内容，可以看到加载一个 .so 文件：/usr/local/lib/libjdk.so

![](https://image.3001.net/images/20180625/15299361912920.png!small)

而这个文件也在文件变更列表里。

我们通过查看启动的相关进程的 maps 信息，也可以看到相关预加载的内容：

![](https://image.3001.net/images/20180625/15299365442450.png!small)

通过对 libjdk.so 的逆向分析，我们可以确认其主要功能就是过滤了挖矿进程，具体可见下文分析。

在知道了黑客使用的隐藏手法后，直接编辑 /etc/ld.so.preload 文件去掉相关内容，然后再通过 top 命令即可看到挖矿进程：

![](https://image.3001.net/images/20180625/15299396448946.png!small)![](https://image.3001.net/images/20180625/15299396829277.png!small)通过查看
/proc/ 下进程信息可以找到位置，看到相关文件，直接进行清理即可：

![](https://image.3001.net/images/20180625/15299397175003.png!small)![](https://image.3001.net/images/20180625/15299397167994.png!small)继续分析变更的文件，还能看到相关文件也被变更
，比如黑客通过修改 /etc/rc.d/init.d/network 文件来进行启动：

![](https://image.3001.net/images/20180625/15299397946267.png!small)同时修改
/etc/resolv.conf ：

![](https://image.3001.net/images/20180625/15299398523869.png!small)还修改了 HOSTS
文件，猜测是屏蔽其他挖矿程序和黑客入侵：

![](https://image.3001.net/images/20180625/15299399167468.png!small)同时增加了防火墙规则：

查询 IP 可以看到是一个国外 IP ：

![](https://image.3001.net/images/20180625/15299399694425.png!small)

## **三、样本分析**

通过对样本逆向分析，发现样本 libjdk.so 主要是 Hook 了 readdir 和 readdir64 两个函数：

![](https://image.3001.net/images/20180625/15299400244968.png!small)对应修改后的
readdir 函数结构如下（readdir64 函数也是类似的）：  
![](https://image.3001.net/images/20180625/15299400264876.png!small)get_dir_name
函数结构：

![](https://image.3001.net/images/20180625/15299401266707.png!small)get_proces_name
函数结构：

![](https://image.3001.net/images/20180625/15299401644828.png!small)process_to_filter
常量定义如下：

![](https://image.3001.net/images/20180625/15299401822617.png!small)

整个函数功能结合来看就是判断如果读取目录为 /proc，那么遍历的过程中如果进程名为 x7，则过滤，而 x7 就是挖矿进程名。

而类似于 top、ps 等命令在显示进程列表的时候就是调用的 readdir 方法遍历 /proc 目录，于是挖矿进程 x7
就被过滤而没有出现在进程列表里。

##  **四、附录**

###  **IOCs：**

样本

> 1\. 4000dc2d00cb1d74a1666a2add2d9502
>
> 2\. 8bd15b2d48a051d6b39d4c1ffaa25026
>
> 3\. e2a72c601ad1df9475e75720ed1cf6bf
>
> 4\. d6cee2c684ff49f7cc9d0a0162b67a8d

矿池地址

> 1\. xmr-asia1.nanopool.org:14433
>
> 2\. 123.56.154.87:14444

钱包地址

>
> 42im1KxfTw2Sxa716eKkQAcJpS6cwqkGaHHGnnUAcdDhG2NJhqEF1nNRwjkBsYDJQtDkLCTPehfDC4zjMy5hefT81Xk2h7V.v7

 **相关链接：**

> 1.<https://mp.weixin.qq.com/s/inazTPN5mHJYnt2QDliv8w>
>
> 2.<https://cloud.tencent.com/product/hs>

 ***本文作者：Fooying、zhenyiguo、murphyzhang，转载请注明来自FreeBuf.COM**

