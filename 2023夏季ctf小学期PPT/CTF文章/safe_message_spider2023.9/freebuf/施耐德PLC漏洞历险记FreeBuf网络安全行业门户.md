**工控安全是维护国家基础设施的安全，可工控设备并不像web那么常见，因此工控安全的研究较之web安全也相对迟缓。最近，瑞不可当工控团队入手了一台施耐德PLC，就让我们一起本着增加自身知识储备、实践维护国家安
全，怀着激动的心开始守卫世界和平啦。**

## 施耐德PLC系列介绍

Twido，小型PLC，编程平台是TwidoSoft或TwidoSuite；

M218，M238，M258,编程平台是SoMachine;

M340，中型PLC，跟西门子S7-300性能接近，编程平台是Unitry；

Premium，中型PLC，跟西门子S7-300性能接近，新的编程平台是Unitry， 原来是PL7 Pro；

Quantumn，大型PLC，跟西门子S7-400性能接近，新的编程平台是Unitry， 原来是Concept；

Quantumn系列主要设备型号如下图所示：

![](https://image.3001.net/images/20200423/1587608112_5ea0fa306f4a8.png!small)

Modicon Quantum自动化控制平台拥有业界领先的性能，包含：

> 5种IEC编程语言（FBD 、LD、SFC 、ST 、IL）适用于各种应用需求
>
> 高性能多任务系统
>
> 高达11M 集成 储存空间
>
> 涂层保护模块，适用于恶劣环境；安全I/O,高可靠性；支持第三方设备
>
> 高性能热备解决方案。每个模块均有小型LCD荧幕及按键，便于本地监控
>
> 前面板有多个内置端口（USB、Ethernet TCP/IP、Modbus Plus、以及至少一个 Modbus 端口）
>
> 本地机架上可安装第三方模块以连接Profibus-DP

本次拿到的PLC是Quantumn系列的140CPU65150。

![](https://image.3001.net/images/20200423/1587608136_5ea0fa483a18f.png!small)

图种各模块功能如下：

> 140 CPS 22400 电源输入模块
>
> 140 CPU 65150 CPU模块
>
> 140 NOE 77101 以太网模块
>
> 140 CRA 31200 RIO以太网模块
>
> 140 ACI 04000 模拟量输入16通道电流模块

## 测试过程

接下来就是接电连网线了，调通设备

磨刀不误砍柴功，首先来简单探测下端口：

![](https://image.3001.net/images/20200423/1587608153_5ea0fa5986064.png!small)

接下来一个个试一下。

这不是我们最最最最熟悉的80口吗？尝试访问下，有点东西：

![](https://image.3001.net/images/20200423/1587608161_5ea0fa61a2692.png!small)

页面内容不多，有几个需要密码：

![](https://image.3001.net/images/20200423/1587608168_5ea0fa68ef53f.png!small)

不过问题不大，咱浪迹BS架构那么多年，也不能白混，OWASP Top10试试，比如CSRF漏洞：

1）如修改密码，先生成poc：

![](https://image.3001.net/images/20200423/1587608178_5ea0fa72b05a1.png!small)

2）执行成功：

![](https://image.3001.net/images/20200423/1587608188_5ea0fa7ce0ca1.png!small)

3）使用新用户名密码“123 /123”,成功登录：

![](https://image.3001.net/images/20200423/1587608196_5ea0fa84cac4d.png!small)

再试试别的，比如，任意URL跳转：

![](https://image.3001.net/images/20200423/1587608205_5ea0fa8def72d.png!small)

再比如，任意文件读取漏洞：

![](https://image.3001.net/images/20200423/1587608214_5ea0fa96199ca.png!small)

可以拿下部分文件，包含jar包：

![](https://image.3001.net/images/20200423/1587608276_5ea0fad4dd232.png!small)

逐个查找，反编译文件，找出FTP弱口令（也就是FTP硬编码漏洞）：

![](https://image.3001.net/images/20200423/1587608308_5ea0faf452194.png!small)

试验可用，并可以看到包含文件：

![](https://image.3001.net/images/20200423/1587608323_5ea0fb0392fb1.png!small)

亦可以成功下载：

![](https://image.3001.net/images/20200423/1587608392_5ea0fb4841f99.png!small)

打开康康：

![](https://image.3001.net/images/20200423/1587608409_5ea0fb5954942.png!small)

本篇文章主要是渗透测试工控设备的流程，快乐的时光总是短暂的，是不是感觉意犹未尽？那就尽请期待下一篇吧！！！

![](https://image.3001.net/images/20200423/1587608425_5ea0fb6956889.png!small)

 ***本文作者：cilan，转载请注明来自FreeBuf.COM**

