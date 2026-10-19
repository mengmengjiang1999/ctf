作者：youzuzhang、zhenyiguo、murphyzhang@云鼎实验室

#### 一、背景

云鼎实验室曾分析不少入侵挖矿案例，研究发现入侵挖矿行为都比较粗暴简单，通过 top
等命令可以直接看到恶意进程，挖矿进程不会被刻意隐藏；而现在，我们发现黑客开始不断使用一些隐藏手段去隐藏挖矿进程而使它获得更久存活，今天分析的内容是我们过去一个月内捕获的一起入侵挖矿事件。

#### 二、入侵分析

本次捕获案例的入侵流程与以往相比，没有特殊的地方，也是利用通用漏洞入侵服务器并获得相关权限，从而植入挖矿程序再进行隐藏。

通过对几个案例的分析，我们发现黑客主要是利用 Redis
未授权访问问题进行入侵，对于该问题的说明可以参考我们过去做的一些[分析](https://paper.seebug.org/605/ "分析")。

在服务器被入侵后，首先可以明显感觉到服务器的资源被占用而导致的操作迟缓等问题，通过一些常规手段可以发现一些异常信息，但又看不到进程信息：

![](https://images.seebug.org/content/images/2018/06/f0906e27-39b4-4970-86fd-f565f942a097.png-w331s)

通过 top 命令，可以看到显示的 CPU 使用率较低，但 ni 值为 100 ；同时通过 /proc/stat 计算 CPU 使用率又基本是 100% 。

![](https://images.seebug.org/content/images/2018/06/7598cf12-beea-4757-a13c-75953b5d8b8a.png-w331s)

通过 netstat 查看端口监听情况，也可以看到异常的连接。

![](https://images.seebug.org/content/images/2018/06/42b5c850-d59b-4646-bd89-0e2f403cc0db.png-w331s)

通过在 Virustotal 查询 IP，可以看到 DNS 指向为矿池域名。

通过 find 命令查找入侵时间范围内变更的文件，对变更文件的排查，同时对相关文件进行分析，基本可以确认黑客使用的进程隐藏手法。

![](https://images.seebug.org/content/images/2018/06/b4baca53-5baa-4437-9187-c9ca015b7fed.png-w331s)
![](https://images.seebug.org/content/images/2018/06/6eb5e510-2231-4c49-bdd5-d7905f679d57.png-w331s)

在变更文件里可以看到一些挖矿程序，同时 /etc/ld.so.preload 文件的变更需要引起注意，这里涉及到 Linux
动态链接库预加载机制，是一种常用的进程隐藏方法，而 top 等命令都是受这个机制影响的。

> 在 Linux 操作系统的动态链接库加载过程中，动态链接器会读取 LD_PRELOAD 环境变量的值和默认配置文件 /etc/ld.so.preload
> 的文件内容，并将读取到的动态链接库进行预加载，即使程序不依赖这些动态链接库，LD_PRELOAD 环境变量和 /etc/ld.so.preload
> 配置文件中指定的动态链接库依然会被装载，它们的优先级比 LD_LIBRARY_PATH
> 环境变量所定义的链接库查找路径的文件优先级要高，所以能够提前于用户调用的动态库载入。
>
> ——段落引自《警惕利用 Linux 预加载型恶意动态链接库的后门》

通过查看文件内容，可以看到加载一个 .so 文件：`/usr/local/lib/libjdk.so`

![](https://images.seebug.org/content/images/2018/06/292b6f68-f96c-4149-8a4d-5259c207f84a.png-w331s)

而这个文件也在文件变更列表里。

我们通过查看启动的相关进程的 maps 信息，也可以看到相关预加载的内容：

![](https://images.seebug.org/content/images/2018/06/fdd5c9e1-15d4-4441-add2-cfb01a28fb26.png-w331s)

通过对 libjdk.so 的逆向分析，我们可以确认其主要功能就是过滤了挖矿进程，具体可见下文分析。

在知道了黑客使用的隐藏手法后，直接编辑 /etc/ld.so.preload 文件去掉相关内容，然后再通过 top 命令即可看到挖矿进程：

![](https://images.seebug.org/content/images/2018/06/8dc17140-39c4-46e2-88ae-c5cee9064dea.png-w331s)
![](https://images.seebug.org/content/images/2018/06/5a131d87-a71a-4f29-bb4d-a86ecc46fe0c.png-w331s)

通过查看 /proc/ 下进程信息可以找到位置，看到相关文件，直接进行清理即可：

![](https://images.seebug.org/content/images/2018/06/a4a6eda5-4865-4523-805a-13f05e7f34ae.png-w331s)
![](https://images.seebug.org/content/images/2018/06/5c638414-4e01-4f27-94f0-8ec562ff79ef.png-w331s)

继续分析变更的文件，还能看到相关文件也被变更，比如黑客通过修改 /etc/rc.d/init.d/network 文件来进行启动：

![](https://images.seebug.org/content/images/2018/06/c69cefd3-415b-4c59-a36f-e3ee482b1621.png-w331s)

同时修改 /etc/resolv.conf ：

![](https://images.seebug.org/content/images/2018/06/f4b033c5-5484-4815-97f4-f9a472b69196.png-w331s)

还修改了 HOSTS 文件，猜测是屏蔽其他挖矿程序和黑客入侵：

![](https://images.seebug.org/content/images/2018/06/63093044-fa00-421c-8b63-abe65fee8381.png-w331s)

同时增加了防火墙规则：

![](https://images.seebug.org/content/images/2018/06/723f5857-5720-492a-aed2-35978f97b2d4.png-w331s)

查询 IP 可以看到是一个国外 IP ：

![](https://images.seebug.org/content/images/2018/06/fcc98411-b1e5-413f-aef9-3660976407c4.png-w331s)

#### 三、样本分析

通过对样本逆向分析，发现样本 libjdk.so 主要是 Hook 了 readdir 和 readdir64 两个函数：

![](https://images.seebug.org/content/images/2018/06/500b0ec6-28d6-42a2-a9bd-a54cb4306944.png-w331s)

对应修改后的readdir函数结构如下（readdir64函数也是类似的）：

![](https://images.seebug.org/content/images/2018/06/c4729372-19ec-43ab-8a83-4334cee1bca4.png-w331s)

get_dir_name 函数结构：

![](https://images.seebug.org/content/images/2018/06/6a76397c-1c3e-4730-99bc-dca2b0332f40.png-w331s)

get_proces_name 函数结构：

![](https://images.seebug.org/content/images/2018/06/4b28686f-8255-442e-8fa5-e5a43bc7997e.png-w331s)

process_to_filter 常量定义如下：

![](https://images.seebug.org/content/images/2018/06/8b1c954d-ebdd-4e1c-9f13-982203dddc98.png-w331s)

整个函数功能结合来看就是判断如果读取目录为 /proc，那么遍历的过程中如果进程名为 x7，则过滤，而 x7 就是挖矿进程名。 而类似于 top、ps
等命令在显示进程列表的时候就是调用的 readdir 方法遍历 /proc 目录，于是挖矿进程 x7 就被过滤而没有出现在进程列表里。

#### 四、附录

IOCs：

样本

  1. 4000dc2d00cb1d74a1666a2add2d9502
  2. 8bd15b2d48a051d6b39d4c1ffaa25026
  3. e2a72c601ad1df9475e75720ed1cf6bf
  4. d6cee2c684ff49f7cc9d0a0162b67a8d

矿池地址

  1. xmr-asia1.nanopool.org:14433
  2. 123.56.154.87:14444

钱包地址

42im1KxfTw2Sxa716eKkQAcJpS6cwqkGaHHGnnUAcdDhG2NJhqEF1nNRwjkBsYDJQtDkLCTPehfDC4zjMy5hefT81Xk2h7V.v7

相关链接：

  1. <https://mp.weixin.qq.com/s/inazTPN5mHJYnt2QDliv8w>
  2. <https://cloud.tencent.com/product/hs>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/629/>

