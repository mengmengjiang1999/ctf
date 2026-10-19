Windows 打印组件自 Win2000时代就被引入，作为一个”历史悠久”的组件其安全问题也一直广受安全研究人员关注。近期围绕 printer port
相关机制就连续爆出安全问题，本文旨在对相关漏洞进行一个简要梳理介绍。

## Windows 打印组件简介

Windows
打印组件是一个典型的c/s架构，如图1-1所示：![1605580924_5fb3387c66b6683e24a5a.png!small](https://image.3001.net/images/20201117/1605580924_5fb3387c66b6683e24a5a.png!small)  
图1-1客户端通过 gdi api 经由 winspool.drv 模块，向 spoolsv 进程发送 rpc 请求，spoolsv 进程经由
spoolss.dll 将打印请求分发给不同的 print provider 处理，本地的打印请求由 localspl.dll
模块进行处理，而远程的打印请求则通常由win32spl.dll
模块进行处理如图1-2所示：![1605580957_5fb3389d4f72374886036.png!small?1605580957558](https://image.3001.net/images/20201117/1605580957_5fb3389d4f72374886036.png!small?1605580957558)图1-2

## 漏洞分析

需要注意的是作为 server 端的 spoolsv 进程是 system 权限，这也意味着如果spoolsv 没有正确处理 client
发送过来的打印请求，很容易产生 EOP 类漏洞。当我们进行一次打印操作时，我们需要指定一个 printer port，这里的 printer port
不仅仅局限于通常的串口设备，也可以是一个文件路径，当 printer port 为一个文件路径时，我们打印的内容会被写入到指定的文件中，我们用
powershell模拟一下该过程：![1605580977_5fb338b1029144922f252.png!small?1605580977157](https://image.3001.net/images/20201117/1605580977_5fb338b1029144922f252.png!small?1605580977157)我们使如上ps脚本创建了打印机”Printer1”，指定portname为路径:”c:\users\xxxx\1.txt”,接着我们向打印机发送打印内容：![1605580985_5fb338b95cd64b58dd5e7.png!small?1605580985576](https://image.3001.net/images/20201117/1605580985_5fb338b95cd64b58dd5e7.png!small?1605580985576)我们可以看到相应内容已经被写入到文件中：![1605580994_5fb338c2911c7ea274d9f.png!small?1605580994767](https://image.3001.net/images/20201117/1605580994_5fb338c2911c7ea274d9f.png!small?1605580994767)这时，对
Windows 逻辑漏洞熟悉的朋友想必会产生一个这样的想法，如果把portname
设定为一个只有高权限用户才可以写的路径那会怎么样呢，如果能成功的话就是一个典型的逻辑漏洞导致eop的场景了，用 processmonitor
观测到的测试结果如下：![1605581006_5fb338cecd777aff81f7b.png!small?1605581006981](https://image.3001.net/images/20201117/1605581006_5fb338cecd777aff81f7b.png!small?1605581006981)很明显这是由于
spoolsv 进程 impersonate
当前用户进行文件操作而导致权限不足拒绝访问的错误，这样看起来似乎并没有什么问题，但微软可能是为了应对打印过程中有可能出现各种中断异常的状况，spoolsv
进程在重启后，会解析 shd 文件，并以 system 权限继续进行shd中记录的文件打印行为，如下是我们在processmonitor
中观察到的现象：![1605581016_5fb338d81461bd6949afd.png!small?1605581016282](https://image.3001.net/images/20201117/1605581016_5fb338d81461bd6949afd.png!small?1605581016282)很明显，spoolsv
进程在重启后以 system 权限创建了c:\windows\system32\1.txt。以上就是
CVE-2020-1048的漏洞原理。微软为了修补这个漏洞再添加 printport
的过程中引入了两个校验函数：IsValidNamedPipeOrCustomPort 和PortIsValid，第一个函数主要判断是不是命名管道和
customport，如果不是则进入 PortIsValid
的判断：![1605581028_5fb338e40a0f3692b9a66.png!small?1605581028316](https://image.3001.net/images/20201117/1605581028_5fb338e40a0f3692b9a66.png!small?1605581028316)PortIsValid
通过调用createfile判断对于目标路径是否有可写权限来决定用户提供的port是否有效，然后这又是一个典型的toctou的场景，我们可以构造一个合法路径使其通过
PortIsVaild 的校验，如：c:\temp\1.txt,在通过 PortIsValid 的校验后，我们创建一个 junction 将 c:\temp
指向 c:\windows\system32，这样在spoolsv 进程重启后依旧会往system32目录写入1.txt文件，这便是
CVE-2020-1337的漏洞原理，微软为了解决这个问题又引入了一个新的校验函数
IsPortAlink:![1605581039_5fb338ef63062f316ec26.png!small?1605581039560](https://image.3001.net/images/20201117/1605581039_5fb338ef63062f316ec26.png!small?1605581039560)其主要内容如下(注不仅仅是在添加port时调用了该函数进行校验，在打印过程中也校验了)：![1605581049_5fb338f99cd20aa99f6ee.png!small?1605581049808](https://image.3001.net/images/20201117/1605581049_5fb338f99cd20aa99f6ee.png!small?1605581049808)主要逻辑时在
createfile 打开攻击者提供的portname后得到一个句柄A，通过GetFinalPathNameByHandlew
获得句柄A对应的路径，将其和攻击者提供的portname比较看是否一致，若不同的话则判定为 link，也就是该 portname 非法。然而
GetFinalPathNameByHandlew 函数在处理 unc 路径时存在一个问题，即使 unc 路径中包含 junction
也不会将其转换为最终地址，请看如下代码：![1605581059_5fb3390381172ea6524e6.png!small?1605581059728](https://image.3001.net/images/20201117/1605581059_5fb3390381172ea6524e6.png!small?1605581059728)在上述代码中
c:\test 是一个 junction 目录，指向
c:\windows\system32,我们看看程序最后的输出：![1605581068_5fb3390c558f964bcc5a9.png!small?1605581068590](https://image.3001.net/images/20201117/1605581068_5fb3390c558f964bcc5a9.png!small?1605581068590)也就是说在
unc 路径中即使包括 junction 目录 GetFinalPathNameByHandlew函数也不会将其转换为目标路径，这样也就绕过了
IsPortAlink 函数的校验，这便是 CVE-2020-17001 的漏洞原理。

## 启示

可以说从 CVE-2020-1048 到 CVE-2020-17001 微软向广大安全研究员详细的展示了逻辑漏洞的经典场景：1、特权进程没有
impersonate 便对普通用户可控制的资源进行访问 2、totou 即 check 和 use 的不一致性。

## 参考链接

> <https://docs.microsoft.com/en-us/windows/win32/printdocs/documents-and-> printing>
>
> <https://windows-internals.com/printdemon-cve-2020-1048/>
>
> <https://safebreach.com/Post/How-we-bypassed-CVE-2020-1048-Patch-and-got-> CVE-2020-1337>
>
> <https://www.thezdi.com/blog/2020/8/11/windows-print-spooler-patch-bypass-> re-enables-persistent-backdoor>
>
> [https://bugs.chromium.org/p/project-> zero/issues/detail?id=2075﻿](https://bugs.chromium.org/p/project-> zero/issues/detail?id=2075)

