**作者：IOTsec-Zone  
原文链接：<https://mp.weixin.qq.com/s/SWFLV6H1zKWQyvnC0JGGhg>**

## 0x00 描述

> 测试环境：Ubuntu 18.04
>
> 固件版本：wr740nv1_en_3_12_4_up(100910).bin
>
> 产品厂商：TP-Link
>
> 厂商地址：<https://www.tp-link.com.cn/>
>
> ZoomEye搜索app：TP-LINK TL-WR740N WAP httpd  
>  <https://www.zoomeye.org/searchResult?q=app%3A%22TP-LINK%20TL-> WR740N%20WAP%20httpd%22>

## 0x01 固件分析

将固件下载到Ubuntu中，使用命令binwalk进行解包，拿到固件的文件系统

![](https://images.seebug.org/content/images/2022/02/7ae64875-309b-4fe1-8523-25a820972aac.png-w331s)

这里介绍一个常用的小工具 firmwalk.sh，工具下载链接 <https://github.com/craigz28/firmwalker>

  1. 它将搜索固件文件系统，以获取与敏感信息相关的东西，如：etc/shadow and etc/passwd

  2. 列出 etc/ssl等目录

  3. 搜索相关的文件，如. pem,. crt, 等

  4. 搜索配置文件

  5. 查找脚本文件

  6. 搜索其他.bin 文件

  7. 查找诸如管理员，密码，远程等关键字符

  8. 搜索IoT设备上使用的通用网络服务器

  9. 搜索常见的二进制文件，如 ssh，tftp，dropbear等

  10. 搜索网址，电子邮件地址和IP地址

接下来我们使用工具firmwalker对提取的固件进行扫描

![](https://images.seebug.org/content/images/2022/02/462208be-4b56-4909-a953-cc76e4fa66bd.png-w331s)

通过上面的信息可以得到很多关键信息，这里我们着重查看图片上的几处关键信息

  * 可以看到对于路由器的相关URL应该是/web/userRpm/xxxxx.htm这种，那么我们就可以合理的猜测，这应该是web服务相关的命令规范
  * 含有passwd和pwd相关的文件中，可以看到嵌入式web服务httpd，部分htm文件以及其他配置文件

可以看到它把固件的敏感信息都列举出来了，先不着急对文件进行分析，接下来我们看一下启动项有没有启动什么后门服务，如telnet服务等

一般启动项文件都位于etc目录下面，我们到etc目录下面进行查看

![](https://images.seebug.org/content/images/2022/02/18dbcde0-e18d-431b-ae58-a49ee193971e.png-w331s)

根据嵌入式Linux常用启动项位置可以确定启动项文件就位于rc.d这个目录里面，打开此目录对里面的文件进行分析

![](https://images.seebug.org/content/images/2022/02/059691d7-b81d-4e65-ad98-002f87d514a3.png-w331s)

可以看到他的Http服务都在httpd这个文件中，启动项没有其他的异常行为

那我们通过find命令查找一下这个文件的所在位置
![](https://images.seebug.org/content/images/2022/02/100ecaaf-c965-4c14-bb88-e484be0643b5.png-w331s)

可以看到文件在/usr/bin目录下面我们将文件移动到IDA中进行分析

## 0x02.IDA逆向分析

根据firmwalker收集到的跟passwd先关的文件就包含httpd二进制应用，这里我们直接在字符串窗口搜索passwd字符串

![](https://images.seebug.org/content/images/2022/02/a9829b8c-ce59-4b9e-8b89-de4df4329d61.png-w331s)

可以看到和passwd先关的字符串还有很多，那么我们可以逐个进行追踪

![](https://images.seebug.org/content/images/2022/02/9a5813e0-3a06-42c0-916a-0f529557d807.png-w331s)

在这里可以看到passwd被调用的位置，直接双击箭头向上追踪

![](https://images.seebug.org/content/images/2022/02/c10f626f-8479-4b10-8638-3903dafa8460.png-w331s)

简单查看便可以很多硬编码的敏感字符串，使用F5生成伪C代码

![](https://images.seebug.org/content/images/2022/02/ea0d418d-d68d-429f-a5ea-2cfcf614e0d8.png-w331s)
可以看到在进行用户名和密码的比对，并且用户名和密码为osteam和5up，那么可以猜测这里应该是和某种认证相关

通过httpGetEnv函数的第二个参数名称cmd，可以猜测这应该是执行命令的地方

接着可以看到write函数调用了pty来模拟命令的执行

（知识扩充：伪终端(pseudo terminal，有时也被称为 pty)是指伪终端 master 和伪终端 slave 这一对字符设备。其中的 slave
对应 /dev/pts/ 目录下的一个文件，而 master
则在内存中标识为一个文件描述符(fd)。伪终端由终端模拟器提供，终端模拟器是一个运行在用户态的应用程序。）

根据当前函数DebugResultRpmHtm，追踪调用的位置

![](https://images.seebug.org/content/images/2022/02/85179408-1fe7-4083-99eb-eb4d3692100a.png-w331s)

这里可以看到使用httpRpmConfAdd函数进行url和执行函数的定义，这里看到当前函数为httpDebugInit，似乎是进行Debug调试的，接着可以看到有一个linux_cmdline.html的页面

![](https://images.seebug.org/content/images/2022/02/d603c792-e4cf-486d-ab13-5dba91cc0cc4.png-w331s)

一看到这个页面可以其能执行系统命令，可以确定linux_cmdline.html似乎是一个后门，但是想要执行命令还需要用户名和密码，根据上面的分析我们可以确定用户名为osteam和密码5up的账户为后门登录的账号和密码

## 0x03 漏洞验证

> 工具下载地址：<https://github.com/pr0v3rbs/FirmAE>

接下来我们去验证上面我们的猜想，接下来我们就对固件进行模拟

这里推荐使用工具FirmAE，为什么推荐呢？这个工具使用高度集成化的操作，只需要使用一条命令即可对固件进行模拟，比起使用qemu来模拟固件方便快捷了很多

![](https://images.seebug.org/content/images/2022/02/2e4318ec-9b29-49a6-85e2-8a2f7579e611.png-w331s)

可以看到固件模拟成功，浏览器进行访问<http://192.168.1.1/userRpmNatDebugRpm26525557/linux_cmdline.html>

![](https://images.seebug.org/content/images/2022/02/7049409a-71b1-401b-8fa6-4ae75a585fef.png-w331s)

可以看到需要授权，使用默认的账号密码进行登录

![](https://images.seebug.org/content/images/2022/02/2bed34b7-6ab9-435d-86c2-023a3c762f2b.png-w331s)

输入用户名，密码以及要执行的命令，可以看到成功执行并返回了相应的结果

## 0x03.总结

通过上面的分析，可以看到信息收集对我们漏洞分析和漏洞挖掘有很大的帮助，通过敏感的信息，我们能更快的定位到漏洞产生的位置，并且我们掌握的信息越多，越能加快漏洞分析和漏洞挖掘的速度和效率。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1840/>

