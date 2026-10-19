***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 ***本文作者：cgf99，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

## 前言

**近日收获一个后缀名为doc的word文档，查看后其实是rtf格式文档。在测试环境打开后发现有网络连接和执行程序的动作，确定该样本是恶意文档。经过初步分析，发现该样本是CVE-2017-11882漏洞的利用新样本。CVE-2017-11882漏洞和CVE-2018-0802漏洞基于Office公式编辑器的处理逻辑错误
，是最近office恶意攻击文档的常用手段。网络上对该漏洞的成因、利用等分析的已经十分到位，比如360天眼实验室的[利用了Office公式编辑器特殊处理逻辑的最新免杀技术分析（CVE-2017-11882）](https://www.freebuf.com/column/183735.html)，以及腾讯电脑管家的[NDAY漏洞CVE-2017-11882与0Day漏洞CVE-2018-0802漏洞组合传播远控木马的样本分析
](https://www.freebuf.com/vuls/160252.html)等技术报告。本次样本与之前各家分析的稍有不同，应是CVE-2017-11882漏洞的又一个变异版本。**

## 一、基本动作

实验环境：windows 7 x64 sp1中文版，office 2010中文版。

漏洞样本打开后，显示的文档内容为乱码，如下图所示。

![](https://image.3001.net/images/20181124/1543024815_5bf8b0aff1ceb.png!small)

此外，在%temp%目录下生成并运行一个名为emre.exe的可执行文件。抓包发现emre.exe是从<http://ghthf.cf/>cert/ochicha.exe下载生成。如下图所示。

![](https://image.3001.net/images/20181124/1543025083_5bf8b1bb3a590.png!small)

## 二、漏洞调试

### 1、样本形态

winhex打开后如下两幅图所示。文档后面直接跟要显示的内容。

![](https://image.3001.net/images/20181124/1543025978_5bf8b53ac1bc7.png!small)

紧随其后的就是object对象，如下图所示。

![](https://image.3001.net/images/20181124/1543025728_5bf8b44012bda.png!small)

### 2、RTF初步分析

用rftobj分析后结果如下图所示。可以看到clsid为0002ce02-0000-0000-c000-000000000046也就是微软公式编辑器对象。

![](https://image.3001.net/images/20181124/1543026347_5bf8b6ab810d7.png!small)

![](https://image.3001.net/images/20181124/1543026881_5bf8b8c10fb6b.png!small)

从图中我们可以看到，该对象名字为“eQuatiON native”，对正常对象名字“Equation
Native”进行了大小写转换操作，可能也是追求免杀的一种效果。

### 3、漏洞调试

根据各方对漏洞的分析报告，我们直接调试漏洞所在的函数0041160F。

![](https://image.3001.net/images/20181124/1543027328_5bf8ba80a5a02.png!small)

在经过11次的rep操作后，如下图，堆栈0x0043F775被覆盖。

![](https://image.3001.net/images/20181124/1543027588_5bf8bb8428e33.png!small)

![](https://image.3001.net/images/20181124/1543027800_5bf8bc58c5a27.png!small)

而EQNEDT32.EXE进程0x0043F775处的值是C3，恰好是指令retn。

![](https://image.3001.net/images/20181124/1543028035_5bf8bd439c8e9.png!small)

执行后跳转到shellcode位置。如下图所示：

![](https://image.3001.net/images/20181124/1543028175_5bf8bdcf72dd2.png!small)

### 4、shellcode调试分析

shellcode的位置在eQuatiON native对象中。

分为两个部分，其中开始的位置0x0826处，B9 C439E66A（见上图0018F354处的反汇编指令）开始到
0851处，紧随其后的就是四个字节0x0043F7F5（EQNEDT32.EXE进程中RETN指令）。第二部分的位置在0x089E处开始一直到结束。

![](https://image.3001.net/images/20181124/1543028371_5bf8be938ff06.png!small)

第一部分的shellcode跳转到第二部分的汇编指令如下图所示：

![](https://image.3001.net/images/20181124/1543029212_5bf8c1dc1ce30.png!small)

经过分析，发现该段的shellcode进行了一系列的jmp跳转指令操作，因是为了shellcode的混淆和保护。比如下图所示：

![](https://image.3001.net/images/20181124/1543029376_5bf8c280e0d65.png!small)

跟踪后，发现其实主要的任务就是对 shellcode后段进行解密操作。

shellcode加密部分如下图所示：

![](https://image.3001.net/images/20181124/1543029533_5bf8c31d6ba58.png!small)

解密后的内容如下图所示：

![](https://image.3001.net/images/20181124/1543029658_5bf8c39aab97d.png!small)

其主要功能就是调用URLDownloadToFile函数从<http://ghthf.cf/cert/ochicha.exe>下载文件保存为%temp%目录下
emre.exe，并调用ShellExecuteEx执行。

### 4、shellcode加解密算法

shellcode加密部分的解密算法如下所示。

    
    
    EDI =0
    
    for（解密字符串开始位置处，到结尾，每4个字节进行操作）
    
    ｛
    
    EDI=EDI * 0x2F5E137B
    
    EDI+=0x11B7CF3D
    
    明文四个字节=四个字节密文 xor EDI
    
    ｝

### 5、下载exe情况

emre.exe的属性如下图所示：

![](https://image.3001.net/images/20181124/1543030526_5bf8c6fe29817.png!small)

运行竟然需要.net环境。

具体的功能就不分析了。

## 三、样本利用

可以说，样本到手，工具就有。

可以根据该样本进行改造。

> 1、不替换shellcode主体部分，只是修改下载的链接为自己的链接即可；
>
>
> 2、修改shellcode为自己shellcode，比如不用网络下载，直接把把exe附加在漏洞样本内，从shellcode完成释放和下载动作（或者释放到启动目录下等等）。
>
> 3、进行免杀操作。

## 四、结语

> 1、动手实践很重要。通过调试分析，进一步掌握该漏洞的具体细节；
>
> 2、shellcode有一定借鉴意义，比如利用一堆JMP指令混淆真实解密操作。
>
> 3、漏洞样本结构更畸形、简单。只有一个eQuatiON native对象，其他的啥都没有。
>
> 4、打开文档要谨慎。
>
> 5、及时更新补丁。

 ***本文作者：cgf99，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

