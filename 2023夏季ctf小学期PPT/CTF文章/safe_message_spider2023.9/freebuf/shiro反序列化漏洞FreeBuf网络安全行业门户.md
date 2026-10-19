## 什么是shiro反序列化漏洞

Shiro 反序列化漏洞是指 Apache Shiro 框架中的一个安全漏洞，该框架是一个用于身份验证、授权和会话管理的 Java
安全框架。这个漏洞允许攻击者通过精心构造的恶意序列化数据来执行任意代码，从而导致远程代码执行。

这种漏洞发生的根本原因在于 Apache Shiro
在反序列化过程中没有正确地验证和限制传入的序列化数据。攻击者可以构造恶意的序列化对象，并将它们传递给受影响的应用程序。当应用程序对这些序列化对象进行反序列化操作时，恶意代码就会被执行，从而导致安全风险。

## shiro反序列化漏洞的复现

### 环境搭建

首先进入kali，将kali的镜像换为国内的镜像，这样下载快一些

#进入sources.lis重新编辑apt源

vim /etc/apt/sources.list

  
#直接写入下面的apt源

#阿里云

deb <http://mirrors.aliyun.com/kali>kali-rolling main non-free contrib

deb-src <http://mirrors.aliyun.com/kali>kali-rolling main non-free contrib

  
进行更新

apt-get update

  
安装docker

apt-get install docker docker-compose

  
先拉去一个镜像（简单版）

安装靶场

docker pull medicean/vulapps:s_shiro_1

启动靶场

docker run -d -p 80:8080 medicean/vulapps:s_shiro_1

  
如图所示：

![1690374577_64c111b1c52be1480e2f7.png!small?1690374579559](https://image.3001.net/images/20230726/1690374577_64c111b1c52be1480e2f7.png!small?1690374579559)

  
然后在主机上输入kali的ip地址，出现shiro框架

![1690374630_64c111e6b2f06b33e5b22.png!small?1690374632183](https://image.3001.net/images/20230726/1690374630_64c111e6b2f06b33e5b22.png!small?1690374632183)

点击 log in

shiro反序列化漏洞搭建成功。

### 漏洞利用

借助于shiro反序列化漏洞综合利用工具----- SummerSec

实现shiro反序列化漏洞的利用

  
工具利用图：

可以使用命令执行、内存马、key生成等漏洞。

![1690374806_64c112966fe1e0d8a8cee.png!small?1690374807890](https://image.3001.net/images/20230726/1690374806_64c112966fe1e0d8a8cee.png!small?1690374807890)

### 补充

奇怪知识又增加了---------------------------------------------------------------------------------------
这都是一些有回显的命令，可以判断漏洞利用成功；

那么真对一些无回显命令执行应如何验证？

  
解决方法：

利用yakit生成一个域名

![1690375009_64c113612dd40152ce645.png!small?1690375012034](https://image.3001.net/images/20230726/1690375009_64c113612dd40152ce645.png!small?1690375012034)

在命令执行中，执行ping命令，ping生成的域名，这时若利用成功，yakit上会有显示。

![1690375081_64c113a99123fe489c3df.png!small?1690375083167](https://image.3001.net/images/20230726/1690375081_64c113a99123fe489c3df.png!small?1690375083167)

  
![1690375094_64c113b675c3f63df195c.png!small?1690375095879](https://image.3001.net/images/20230726/1690375094_64c113b675c3f63df195c.png!small?1690375095879)

你学废了吗？

  
感谢观看，若需要shiro利用工具，请留言。

