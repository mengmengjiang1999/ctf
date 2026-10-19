Bourne Again
Shell（简称BASH）是在GNU/Linux上最流行的SHELL实现，于1980年诞生，经过了几十年的进化从一个简单的终端命令行解释器演变成了和GNU系统深度整合的多功能接口。

Bash，Unix
shell的一种。1989年发布第一个正式版本，原先是计划用在GNU操作系统上，但能运行于大多数类Unix系统的操作系统之上，包括Linux与Mac OS
X v10.4都将它作为默认shell。它也被移植到Microsoft Windows上的Cygwin与MinGW，或是可以在MS-DOS上使用的DJGPP项目。在Novell NetWare与Android上也有移植。

目前的Bash使用的环境变量是通过函数名称来调用的，导致漏洞出问题的是以”(){”开头定义的环境变量在命令ENV中解析成函数后，Bash执行未退出，而是继续解析并执行shell命令，而其核心的原因在于在输入的过滤中没有严格限制边界，也没有做出合法化的参数判断。

本文仅作漏洞复现记录与实现，利用流程如下:

1.漏洞环境

链接：http://192.168.101.152:8080/victim.cgi

![1615804533_604f3875c083a9425f33d.png!small](https://image.3001.net/images/20210315/1615804533_604f3875c083a9425f33d.png!small)

2.漏洞payload

`[() { :; }; echo; /bin/cat /etc/passwd](http://example.com/some-cgi/script.cgi)`

理论上，可以在HTTP请求中注入一个Bash命令，进行远程命令执行

3.利用流程

访问目标

![1615804690_604f3912491e7732ad6fd.png!small](https://image.3001.net/images/20210315/1615804690_604f3912491e7732ad6fd.png!small)

将User-Agent值替换为payload，即可执行命令

![1615804592_604f38b0b35eb2973fa15.png!small](https://image.3001.net/images/20210315/1615804592_604f38b0b35eb2973fa15.png!small)

User-Agent并非必须条件

![1615804829_604f399dbfd348a6d2496.png!small](https://image.3001.net/images/20210315/1615804829_604f399dbfd348a6d2496.png!small)

