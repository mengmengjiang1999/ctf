## 一、前言

**由于之前写过几篇都是拿到WebShell后就结束了，所以本文略过前期拿WebShell的过程，侧重点在获取了WebShell后的思路。本文为实战类文章，仅到内网做了初探，故较为基础，适合像我这类型的小白，大佬略过。实战最大的乐趣是可能会遇到各种问题，不像自己搭环境，一路干脆利索。所以实战更多的是思考及尝试。**

PS：截至投稿前，已将漏洞提交厂商并验证已完成修复。

友情提示：测试过程中请务必遵守相关的法律法规，在有授权的前提下做测试。

![0XL02uTfLKC](http://si1.go2yd.com/get-image/0XL02uTfLKC)

## 二、信息收集

前期获得WebShell，一句话链接地址：<http://xx.com/img/x.jsp>。

![0XL03lM7jLk](http://si1.go2yd.com/get-image/0XL03lM7jLk)​菜刀连接后，常见的信息收集命令如下：

> Whoami
>
> Systeminfo
>
> Netstat-nao
>
> Tasklist/svc
>
> Ipconfig
>
> Netshare
>
> Netuser等等

但此时执行命令出现如下错误：

![0XL03YORCRU](http://si1.go2yd.com/get-image/0XL03YORCRU)

​执行不了CMD命令，这种情况有可能是Tomcat中间件或服务器做了相关限制，可以尝试上传一个CMD，进行尝试。

![0XL03X2q2UK](http://si1.go2yd.com/get-image/0XL03X2q2UK)

​

![0XL03VmFg80](http://si1.go2yd.com/get-image/0XL03VmFg80)

​此处仍旧执行不了CMD命令，通过对该IP的扫描，发现只开放了一个8889端口。故应是内网的服务器通过NAT映射8889端口对公网提供服务。

![0XL03ULTMtk](http://si1.go2yd.com/get-image/0XL03ULTMtk)

​所以目前要做的是找到服务器的内网IP地址，添加一个用户，建立代理进入内网。一般来说JSP脚本默认权限比较大，有可能直接就是System权限。此处可直接读取Administrator的桌面目录，则说明当前权限起码是Administrator权限，否则会提示该目录拒绝访问。

![0XL03Xe1gUy](http://si1.go2yd.com/get-image/0XL03Xe1gUy)

​因此时无法执行CMD命令，故收集服务器上的敏感信息，找到数据库连接信息，并连接数据库。

![0XL03QvyI1A](http://si1.go2yd.com/get-image/0XL03QvyI1A)

![0XL03Wro6E4](http://si1.go2yd.com/get-image/0XL03Wro6E4)

​如上成功连接数据库，尝试利用Mssql的XP_Cmdshell进行CMD命令的执行。

开启xp_cmdshell：

EXECsp_configure 'show advanced options',1;RECONFIGURE;EXEC
sp_configure'xp_cmdshell',1;RECONFIGURE

执行命令：EXECmaster.dbo.xp_cmdshell 'whoami'

![0XL03Wf4412](http://si1.go2yd.com/get-image/0XL03Wf4412)

​

![0XL03PPaLL6](http://si1.go2yd.com/get-image/0XL03PPaLL6)

​成功执行CMD命令，当前已为System权限，收集到的信息如下：

服务器：WindowsServer 2008 R2 Standard；

IP地址：172.16.10.1；开启了3389端口；建立了测试账号。

## 三、建立代理

由上述已经获取了服务器内网IP地址及新建了账号，由于服务器是在内网不能直接连接，故需要通过代理才能连接该内网服务器。

此处第一次上传reGeorg的jsp代理脚本，直接被服务器杀软杀了；使用冰蝎的脚本成功上传，并开启了代理。

![0XL03NyyuG0](http://si1.go2yd.com/get-image/0XL03NyyuG0)

​使用SocksCap进行代理连接，使用建立的账号登录服务器。

![0XL03MX3Tlo](http://si1.go2yd.com/get-image/0XL03MX3Tlo)

![0XL03LtyYFc](http://si1.go2yd.com/get-image/0XL03LtyYFc)

​登录后可以看到服务器安装了SymantecEndpointProtection防护软件，查看防护日志，之前reGeorg的jsp脚本就是它被删掉的。如果不是免杀类的EXP，执行文件都会被杀掉。

## 四、内网初探

进入内网后，本白主要就是做信息收集，例如抓本服务器密码，扫内网各种服务器弱口令，Ms17-010高危漏洞等等。

![0XL03Qj8r1U](http://si1.go2yd.com/get-image/0XL03Qj8r1U)

​1、抓本服务器Administrator密码。

![0XL03HSTFpo](http://si1.go2yd.com/get-image/0XL03HSTFpo)

​2、查看内网的共享资源列表，可以查看当前有00网段和10网段，此处发现了另外一个网段。

![0XL03Huie7k](http://si1.go2yd.com/get-image/0XL03Huie7k)

​3、扫描10网段开放了80,8080等web服务的主机。

![0XL03LZuRX6](http://si1.go2yd.com/get-image/0XL03LZuRX6)

​4、扫描10网段网段存在MS17-010漏洞的主机。

![0XL03JXeNjE](http://si1.go2yd.com/get-image/0XL03JXeNjE)

​5、扫描10网段存在服务弱口令的主机。

![0XL03JUFVqa](http://si1.go2yd.com/get-image/0XL03JUFVqa)

​

![0XL03DK0yHI](http://si1.go2yd.com/get-image/0XL03DK0yHI)

​6、查看10网段的Web服务。

![0XL03CszjcW](http://si1.go2yd.com/get-image/0XL03CszjcW)

![0XL032grwLA](http://si1.go2yd.com/get-image/0XL032grwLA)

​如上，可以看到10网段基本是监控与少数服务器所处的网段。

接下来对00网段进行以上的扫描。

1、扫描11网段存在服务弱口令的主机。

![0XL038XviQy](http://si1.go2yd.com/get-image/0XL038XviQy)

​通过以上的弱口令，即可以直接登录服务器，危害较大，如下；

![0XL0358vxhI](http://si1.go2yd.com/get-image/0XL0358vxhI)

![0XL03EXyjWS](http://si1.go2yd.com/get-image/0XL03EXyjWS)

​2、查看00网段的Web服务。

![0XL035fURTE](http://si1.go2yd.com/get-image/0XL035fURTE)

​数据挖掘管理后台存在admin弱口令，登录可以获取相关的接口信息，如下

![0XL02z21opc](http://si1.go2yd.com/get-image/0XL02z21opc)

​

![0XL02zJpIHY](http://si1.go2yd.com/get-image/0XL02zJpIHY)

​OA服务器登录界面

![0XL0301qAE4](http://si1.go2yd.com/get-image/0XL0301qAE4)

​如上，通过对00段的扫描访问，可以看到该网段主要为服务器网段。

若要继续，更多的还是做信息收集，发现或扫描内网更多的网段及服务，哪些存在弱口令，哪些存在漏洞等。

## 五、总结

本文作为内网初探，由于本白能力和精力的限制，仅验证了漏洞的危害内网后便提交厂商了，没有继续深入。其实通篇下来也只是利用了内网一些服务弱口令，如果要继续内网横向渗透可以从以下几个方面：

> 1、RDP爆破，通过抓取本服务器的密码，爆破内网中其他同密码的服务器。
>
> 2、MS17-010漏洞，通过该漏洞可直接获得服务器权限，但可能造成服务器蓝屏，需谨慎。故本文也没有对该漏洞进行利用。
>
> 3、对已登录的服务器继续做信息收集，如收集密码，一些数据库配置连接信息，查看网段等。
>
> 4、对已发现的Web服务器继续做测试，如发现的很多海康监控、OA系统等，可以做弱口令爆破。对发现的数据挖掘Web
> Service接口进行测试，是否存在注入，未授权等。不过这样下来篇幅会很长，需花费很多的时间及精力。
>
> 5、内网ARP嗅探，在无上面的常规漏洞情况下可以尝试，但不建议使用。

## 相关实验

1、利用kali工具进行信息收集：

<http://www.hetianlab.com/expc.do?ec=ECID172.19.104.182015082709512800001>

2、代理工具的使用：

[http://www.hetianlab.com/cour.do?w=1&c=C9d6c0ca797abec2017032414181900001](http://www.hetianlab.com/cour.do?w=1&c=C9d6c0ca797abec2017032414181900001)

介绍各种代理工具的使用，针对不同操作系统，不同代理类型进行实践学习。

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关，本文为合天原创，如需转载，请注明出处！

