##  一、概述

**随着等保2.0的普及，工控安全大家也越来越重视，研究工控安全的小伙伴也越来越多。工控安全主要包括工控设备私有协议的安全分析，工控设备固件系统安全以及工控设备应用程序安全等。西门子PLC广泛应用于工业控制系统，本文主要描述西门子PLC系列S7-300的攻击过程与思路，并介绍演示一些适合小伙伴们学习的工控工具和框架。如有错误之处，欢迎指正，共同学习进步。**

##  二、环境描述

前几天疫情待在家，PLC的设备拿不到，但是咱的任务不能落下呀，我在网上找了一个好用的S7模拟器，压缩包打开如下：

![](https://image.3001.net/images/20200301/1583041809_5e5b4d112e3f1.png!small)

其实我们需要用到的是serverdemo.exe,也就是我们平时的PLC设备，我将构造代码和它进行连接并执行一些类似停启的操作。但是用它的clientdemo.exe也能相互连接，我给大家看一下连接图：

![](https://image.3001.net/images/20200301/1583042767_5e5b50cf7d87c.png!small)

> 1、192.168.198.1为本机ip，用ipconfig查看填写（serverdemo.exe）
>
> 2、先点击start启动server，简单明了很直接哈（serverdemo.exe）
>
> 3、这是查看下面日志就显示serverstarted（serverdemo.exe）
>
> 4、client上填写连接server的ip192.168.198.1（clientdemo.exe）
>
> 5、点击connect连接（clientdemo.exe）
>
> 6、这时继续查看server的日志，显示client已经added（serverdemo.exe）

如果大家还需要进一步细致的需求可以设置其他参数哈

> S7工控模拟器下载地址：<https://download.csdn.net/download/weixin_43977912/12201820>

##  三、实验过程

（1）我们开启serverdemo.exe,设置好ip。

![](https://image.3001.net/images/20200301/1583042590_5e5b501e89b6c.png!small)

（2）接下来我们需要构造代码来连接模拟器，这里我用的是ISF(Industrial Exploitation
Framework)，ISF是一款基于python编写的类似metasploit的工控漏洞利用框架，这是工控前辈们的研究成果哈。下图大家可以大致看一下Exploit模块，包含了普遍性较高的工控协议的一些漏洞利用模块。

> ISF下载地址：<https://github.com/dark-lbp/isf>

![](https://image.3001.net/images/20200301/1583042555_5e5b4ffbee656.png!small)

（3）我们选取s7_300_400_plc_control这个模块，是用来对S7-300/400 PLC
启停的脚本，ISF这个框架对工控初学者是十分友好的，它的模块可以在kali里面使用，如下图所示：

![](https://image.3001.net/images/20200301/1583042517_5e5b4fd5efc72.png!small)

（4）在使用s7_300_400_plc_control这个模块之前我们看一下它是怎么写的，下图是它的核心代码，用来对S7-300/400 PLC
的启停，可能初学的小伙伴会十分好奇，这里面负责start和stop的一大串十六进制数字是什么意思。其实这些是遵循S7-Comm通讯协议，拥有固定的表达规范。这些<https://www.freebuf.com/articles/ics-articles/188159.html>这位工控大佬讲的很详细啦，不懂的小伙伴可以去恶补一下，我这里就不累述了。

![](https://image.3001.net/images/20200301/1583042352_5e5b4f3097cf3.png!small)

（5）接着我们在kali里面设置s7_300_400_plc_control模块，发现只需要设置目标ip就行，我们填上server的ip（192.168.198.1），command选项已经默认是2（stop
plc），我们就不需要改动了，然后我们直接run运行exploit，发现显示已经运行成功，如下图所示：

![](https://image.3001.net/images/20200301/1583042422_5e5b4f76b5f91.png!small)

（6）这时我们查看我们的S7模拟器，发现已经显示STOP运行成功，证明非常顺利！

![](https://image.3001.net/images/20200301/1583041919_5e5b4d7f474b6.png!small)

（7）在模拟器上运行成功后，几天后我回到实验室，决定对真正的S7-300进行一下基本测试，先正常开启PLC设备，指示灯是绿色，显示run

![](https://image.3001.net/images/20200301/1583042015_5e5b4ddf7c19f.png!small)

（8）在kali上运行的步骤和之前一样，只要把target设置成S7-300的ip就行，运行也成功，指示灯已经变成了橙色，并显示STOP

![](https://image.3001.net/images/20200301/1583042051_5e5b4e0314b7e.png!small)

（9）在kali与plc的通信过程中，我也抓取了一些S7-Comm包进行分析，发现完全符合正常的plc通信，当然小伙伴们除了停启还想做其他的操作，比如读取、上传等功能，都可以使用不同的功能码自己编写一些测试代码进行更深入的研究。

![](https://image.3001.net/images/20200301/1583042225_5e5b4eb13b956.png!small)

![](https://image.3001.net/images/20200301/1583042167_5e5b4e77e1cd7.png!small)

##  总结

演示到这里就结束啦，可以看到直接启停plc以及控制PLC输出是非常危险的，也是非常容易的。S7Comm协议主要用于S7-200，S7-300和S7-400
PLC之间的通信，该协议不像S7CommPlus的加密协议（S7-1500等）来防止重放攻击那样，不涉及任何反重放攻击机制，可以被攻击者轻易利用。

显然，西门子博途系列如S7-1200v4.0和S7-1500使用S7CommPlus协议更加安全，但是经典的S7-300等PLC设备真的没有任何安全防护措施吗？其实不然，从设备层面来讲，硬件组态界面的CPU模块均有protection选项卡可以选择保护级别来设置密码进行口令保护；从开发层面来讲，尽量采用背景数据块和多重背景的数据传递方式，且多采用间接寻址的编程方式来增加安全性；从用户层面来讲，在内存容量利用许可的条件下，不要删除被认为是无用的程序，或者利用EEPROM的反写入功能，及一些需要设置的内存保持功能。这样就能大大提高使用PLC设备的安全性啦。本文主要是给像我一样的工控初学者一些学习的建议与方向，希望大家一起努力进步，为我国的工控安全事业添砖加瓦。

 ***本文原创作者： 黄一113530，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

  

