***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

##  **漏洞名称**

Windows任意文件读取

##  **漏洞简介**

 **12月20日，国外安全研究员 SandboxEscaper又一次在推特上公布了新的Windows 0
day漏洞细节及PoC，点击查看[详情](https://thehackernews.com/2018/12/windows-zero-day-exploit.html)。这是2018年8月开始该研究员公布的第三个windows 0
day漏洞。此次披露的漏洞可造成任意文件读取。该漏洞可允许低权限用户或恶意程序读取目标Windows主机上任意文件的内容，但不可对文件进行写入操作。从放出的POC代码看，在微软官方补丁发布之前，所有windows用户都将受此漏洞影响。**

##  **漏洞本质**

Time of Check Versus Time of Use （TOCTOU）

###  **TOCTOU原理**

该漏洞主要原理为应用运行的过程中，在某个操作之前，比如读文件，都会检查一下文件是否存在与是否具有权限，在检查与真正的读取之间的间隔就是一个可以被利用的竞争条件（Race
Condition），在这个间隔中我们可以将需要越权读取的文件替换成自己的文件，使其检查过程通过，这样就可以越权读取其他用户的文件。

###  **漏洞原因**

当调用MsiAdvertiseProduct这个函数时会导致windows安装服务复制一个文件，在复制文件时我们可以通过TOCTOU的攻击方式控制传进MsiAdvertiseProductA的第一个参数，将该参数在检查通过后被替换成我们实际需要读取的文件，达到越权的效果

##  **漏洞POC使用**

看不到？点[这里](https://v.qq.com/x/page/o0819whw3lf.html)

###  **POC源码简要分析**

该漏洞已经存在POC，作者SandboxEscaper开源在github中<https://github.com/SandboxEscaper/randomrepo/blob/master/Readfile.rar>
，不过源码部分没有注释，为了方便阅读与理解，我这边给出了部分注释。并对主要代码做如下分析。

1、首先从stdafx.h预编译头文件中一直跟进targetver.h，再跟进SDKDDKVer.h头文件，该poc可应用于如下windows版本，几乎可以应用与所有：

![头文件.png](https://image.3001.net/images/20181225/1545732576_5c2201e0e3a6f.png!small)

其中main函数获取用户输入的参数并解析，取出需要读取的文件路径（targetfile）与文件名（filename）备用

![Windows
0day任意文件读取漏洞POC分析](https://image.3001.net/images/20181226/1545788699_5c22dd1b99fe1.png!small)

2、调用MsiSetInternalUI进行静默安装，在安装前需要获取文件file（产品包）的路径，用于MsiAdvertiseProductA进行广告推送，在获取路径与启动中间，调用了函数runme()，该函数即为TOCTOU攻击的实现过程

![Windows
0day任意文件读取漏洞POC分析](https://image.3001.net/images/20181226/1545788722_5c22dd329913f.png!small)

3、查看runme()函数，该函数创建了一个自定义的线程MyThreadFunction

![Windows
0day任意文件读取漏洞POC分析](https://image.3001.net/images/20181226/1545788742_5c22dd4607984.png!small)

4、查看线程MyThreadFunction函数，首先获取c:\windows\installer的句柄hDir，然后又读取了我们的目标文件targetfile，用于下面的替换

![Windows
0day任意文件读取漏洞POC分析](https://image.3001.net/images/20181226/1545788758_5c22dd563e5cd.png!small)

5、然后便是循环判断该句柄hFile有没有被调用，假如被调用了，就说明MsiAdvertiseProductA就开始读取上面我们指定的file位置了，并且已经检查通过

![Windows
0day任意文件读取漏洞POC分析](https://image.3001.net/images/20181226/1545788777_5c22dd69553e2.png!small)

这时便将其路径替换为我们需要读取文件的路径：

![Windows
0day任意文件读取漏洞POC分析](https://image.3001.net/images/20181225/1545732465_5c220171a7863.png!small)

最后再在终端将读到的文件内容输出，并设置succeed参数为true,然后退出main函数

![Windows
0day任意文件读取漏洞POC分析](https://image.3001.net/images/20181226/1545788796_5c22dd7c78812.png!small)

从POC中可以看出文件替换的时候使用了软链接的技术，POC运行时会在系统C盘目录下临时创建blah2文件夹与链接到blah2的快捷方式blah，最后POC运行结束又删除了这两个文件。

![Windows
0day任意文件读取漏洞POC分析](https://image.3001.net/images/20181225/1545732530_5c2201b2ccf59.png!small)

由于该漏洞利用的是TOCTOU这种方式，在POC运行时会不停的创建线程，故系统CPU占用会达到100%

![CPU.png](https://image.3001.net/images/20181225/1545732553_5c2201c9ed4f8.png!small)

## 漏洞修复

截至目前，微软官方并未发布补丁，由于该漏洞环境为本地，不可以远程触发，为防止攻击者对该漏洞进行利用，用户不要下载与运行来源不明的软件，并实时监控系统的CPU利用率是否达到100%

参考：

> <https://thehackernews.com/2018/12/windows-zero-day-exploit.html>
>
> <https://en.wikipedia.org/wiki/Time_of_check_to_time_of_use>
>
> <http://www.cnblogs.com/liqiuhao/p/9450093.html>
>
> <http://blog.nsfocus.net/windows-zero-day-exploit/>

***本文作者：markyu，转载请注明来自 FreeBuf.COM**

