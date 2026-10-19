2021 年 11 月，AT&T Alien Labs 首次披露 Golang 编写的恶意软件 `BotenaGo`。最近，该恶意软件的源代码被上传到
GitHub 上，这可能会催生更多的恶意软件变种，预计也会有攻击者利用这些开源代码改进、混淆自己的恶意软件。

## 背景

2016 年 9 月，Mirai 的源码在某黑客论坛上泄露，紧接着被上传到 GitHub 中。自此以后，Mirai
代码被利用的频率急剧上升，Moobot、Satori、Masuta 等多个恶意软件都将 Mirai
的源码融合进了自己的代码中并增加了差异化的功能。大量的变种感染了数以百万计的设备，Mirai
主要针对路由器与物联网设备，支持各种各样的系统架构，被广泛应用在多个僵尸网络中。

2021 年 11 月，Alien Labs 首次披露了恶意软件 `BotenaGo`并通过 Shodan 显示了其危害。近期，Alien Labs 发现
BotenaGo 恶意软件的源代码在 2021 年 10 月 16 日已经被上传到
[GitHub](https://github.com/Egida/kek/blob/19991ef983f838287aa9362b78b4ed8da0929184/loader_multi.go)中。这意味着，任何攻击者都可以基于这份代码进行修改和升级，甚至是直接使用。目前，该份代码的来源尚不清楚。

## 源码分析

BotenaGo 的源码总共 2891 行（包括空行与注释），在尽可能简单的情况下保持了高效。常见的攻击所需，代码中都已经包含了，例如：

> 反向 Shell 和 telnet 功能，用于创建后门接收攻击者的指令；
>
> 带有 33 个已知漏洞的 Exploit，可以针对操作系统或者设备类型进行针对性攻击。

源码中包含支持的漏洞利用列表：

![image.png-383.6kB](https://image.3001.net/images/20220214/1644831873_620a24819c9a1ffbff25d.png!small)漏洞利用列表

BotenaGo 调用 `scannerInitExploits`函数对设备进行攻击。

![image.png-726.3kB](https://image.3001.net/images/20220214/1644831874_620a2482a6c7e788948c8.png!small)漏洞利用初始化

每个漏洞利用的函数都可进行配置：

![image.png-1431kB](https://image.3001.net/images/20220214/1644831877_620a2485599999d01d7fc.png!small)特定
Payload

某些漏洞利用需要依赖一系列命令：

![image.png-268.5kB](https://image.3001.net/images/20220214/1644831883_620a248b09726ff430e6f.png!small)CVE-2020-10987

![image.png-323.8kB](https://image.3001.net/images/20220214/1644831884_620a248c390b284a0d2b6.png!small)CVE-2020-10173

代码中包含对 C&C 服务器的配置，包括地址与路径等：

![image.png-100.8kB](https://image.3001.net/images/20220214/1644831885_620a248d4bd6c067376c4.png!small)配置信息

`main`函数中调用了所有必要的部分，包括设置后门、加载 Payload、初始化漏洞利用等。攻击者只需要利用这 2891
行代码就可以轻轻松松创建恶意软件了。

![image.png-210.6kB](https://image.3001.net/images/20220214/1644831885_620a248dd94a7e7c093f3.png!small)main
函数

## 更新

从发现时起，BotenaGo 一直在针对路由器和物联网设备发起攻击。时至今日，该样本的检出率仍然很低。

![image.png-312.4kB](https://image.3001.net/images/20220214/1644831887_620a248f057b3f4b12c16.png!small)检测情况

发现的部分样本使用了新的 C&C 服务器，该 IP 地址也被发现在利用 Log4j 漏洞进行攻击。

![image.png-554.3kB](https://image.3001.net/images/20220214/1644831888_620a24902d7b36f975a91.png!small)配置信息

## 结论

BotenaGo
的源码泄露使得任何攻击者都可以使用这些代码构建或者增强自己的恶意软件，恶意软件的变种仍然会持续增加，数百万的路由器和物联网设备都面临巨大的风险。

## IOC

> 86.110.32.167:80  
> 179.43.187.197  
> 2.56.56.78  
> 209.141.59.56  
> cca00b32d610becf3c5ae9e99ce86a320d5dac87  
> eb6bbfe8d2860f1ee1b269157d00bfa0c0808932  
> 01dc59199691ce32fd9ae77e90dad70647337c25  
> 97d5d30a4591df308fd62fa7ffd30ff4e7e4fab9  
> e9aa2ce4923dd9e68b796b914a12ef298bff7fe9  
> 251b02ea2a61b3e167253546f01f37b837ad8cda  
> fa10e8b6047fa309a73d99ec139627fd6e1debe1  
> 154fc9ea3b0156fbcdcb6e7f5ba849c544a4adfd  
> 0c9ddad09cf02c72435a76066de1b85a2f5cf479  
> b4af080ad590470eefaadc41f777a2d196c5b0ba  
> 87ef2fd66fdce6f6dcf3f96a7146f44836c7215d  
> 3c2f4fcd66ca59568f89eb9300bb3aa528015e1c

## 参考来源

> [AT&T](https://cybersecurity.att.com/blogs/labs-research/botenago-strike-> again-malware-source-code-uploaded-to-github)

