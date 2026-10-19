历史文章：

[固件分析技术(1)-简介](273150.html)

[固件分析技术(2)-工具使用](273152.html)

[固件分析技术(3)-漏洞复现](275447.html)

文章首发于公众号：焊死车门

##  **一、概述：**

一般题目会提供一个IOT设备的固件进行分析，获取flag。现在网络中能找到的有关固件分析的CTF题比较少，故在此列举三道题作为入门。

##  **二、赛题复现：**

###  **BUUCTF-firmware![](https://image.3001.net/images/20210530/1622308542_60b276be4deabb313f389.png!small)**

 **（1）固件提取**

下载固件，使用binwalk提取。![](https://image.3001.net/images/20210530/1622308557_60b276cdcdc0edc20b9b2.png!small)

解压后发现还存在一个120200.squashfs文件![](https://image.3001.net/images/20210530/1622308574_60b276de71fcfec2a1a16.png!small)

再次解压120200.squashfs文件![](https://image.3001.net/images/20210530/1622308588_60b276ec0e53174f30ffd.png!small)

题目要求分析出后门程序所使用的远程服务器和端口。  
tmp文件夹中有我们想要的后门程序：![](https://image.3001.net/images/20210530/1622308606_60b276fe8b98d81a56d6f.png!small)

放入IDA中进行分析，能看出是ARM架构![](https://image.3001.net/images/20210530/1622308616_60b27708a2e0cc7e8706c.png!small)

 **（2）查壳脱壳**

在放到IDA分析之前，先用查壳工具查看一下是否加壳![](https://image.3001.net/images/20210530/1622308631_60b27717e61999af2a09c.png!small)

提示有壳，我们可以使用upx进行脱壳

Unbuntu安装upx：apt-get install
upx![](https://image.3001.net/images/20210530/1622308653_60b2772d096872a1491ec.png!small)

脱壳后我们再把backdoor文件放到IDA中进行分析。![](https://image.3001.net/images/20210530/1622308687_60b2774fa4c0a5e80be9c.png!small)

 **（3）代码分析**

因为题目中是让我们找网址+端口的md5加密结果，因此我们只需要在String window找网址和端口就行。

查看字符串

> View-->Open subviews-->Strings

![](https://image.3001.net/images/20210530/1622308710_60b277668acb7baea237a.png!small)

Flag为远程服务器和端口，找到服务器地址后再来找端口。

F5反编译找到initConnection函数![](https://image.3001.net/images/20210530/1622308728_60b277785f1d71707b693.png!small)

双击进入，找到端口：36667![](https://image.3001.net/images/20210530/1622308743_60b27787e09a5d15f258d.png!small)

最后把网址和端口转换成MD5![](https://image.3001.net/images/20210530/1622308765_60b2779d3eb33c0b459d1.png!small)

 **flag{33a422c45d551ac6e4756f59812a954b** **}**

###  **CTFHUB-**
**二次设备固件逆向![](https://image.3001.net/images/20210530/1622308796_60b277bc413ebc02a2f69.png!small)**

（1）固件提取

下载后解压固件。![](https://image.3001.net/images/20210530/1622308813_60b277cd5ccc0f4faca8d.png!small)

解压后存在home文件夹。![](https://image.3001.net/images/20210530/1622308827_60b277db47959b87cf4fc.png!small)

> FuncDll # 动态链接库
>
> Icon # 图标和配置文件
>
> NandFlash # 存储
>
> Process # 运行的程序代码
>
> lost+found # 空

![](https://image.3001.net/images/20210530/1622308866_60b278023dd41a5088e4e.png!small)

根据题目要求需要找到硬编码或者厂商后门口令，使用关键字进行搜索。![](https://image.3001.net/images/20210530/1622308878_60b2780edd79cd1c88f08.png!small)

经过分析发现flag存在于JZPHMISystem文件中：

> ./Process/JZPHMISystem: inputPassword
>
> ./Process/JZPHMISystem: passWd.c
>
> ./Process/JZPHMISystem: rootPasswd
>
> ./Process/JZPHMISystem: passWdPID
>
> ./Process/JZPHMISystem: inputPassword
>
> ./Process/JZPHMISystem: InputPwd_pro
>
> ./Process/JZPHMISystem: InputPwdPro

（2）代码分析

将JZPHMISystem文件拖入IDA中进行分析。![](https://image.3001.net/images/20210530/1622308907_60b2782b6c495f0fdebea.png!small)

根据之前的关键字查找，找到了inputPassword和InputPwd_pro函数，InputPwdPro是个bss处的位置![](https://image.3001.net/images/20210530/1622308928_60b278408d027ae00ceb8.png!small)![](https://image.3001.net/images/20210530/1622308949_60b27855d5902d09517e3.png!small)

但是找不到rootPasswd，passWdPID和passWd.c，搜了hex-view的全局内存也没有，后来看了大佬的讲解才发现是符号，在IDA的工具栏里选择view->opensubview->Names，这才找到rootPasswd。![](https://image.3001.net/images/20210530/1622308967_60b278674678342f2c05d.png!small)![](https://image.3001.net/images/20210530/1622308975_60b2786f870c0d44d1a1e.png!small)

密码为689078

###  **CTFHUB-** **简单的固件逆向分析**

本题固件采用施耐德PLC以太网模块固件noe77101，题解参照“固件分析技术(3)-固件漏洞复现”。

