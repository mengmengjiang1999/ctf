##  **一、操作目的和应用场景**

 **最近做了一些CentOS
7系统的安全加固，涉及到firewalld防火墙的配置。以前对iptables比较熟悉，用firewalld比较少，所以特意学习了firewalld的用法，并在这里分享。**

firewalld和iptables都是防火墙的前端配置工具，真正工作的是linux内核的netfilter。firewalld借鉴了其它防火墙系统/设备的理念，例如区域（zone）的概念以及配置信息管理的当前配置和持久配置（runtime和permanent），这使得防火墙规则的管理工作更加方便。

##  **二、平台及工具版本**

> host系统：linux mint 19.3
>
> 虚拟机管理程序：virtualbox 6
>
> 虚拟机：CentOS 7
>
> 软件：firewalld
>
> 计算机硬件：小米笔记本电脑

##  **三、操作步骤**

**（一）设置zone（区域）**

**1、zone的作用是什么？**

firewalld与iptables相比，一个重要的特性就是使用了zone的概念。不同的zone对应不同类型的网络，不同的网络也对应着不同的包过滤规则集。这与windows
7防火墙的“网络位置”的功能类似。

例如windows
7防火墙有4个网络位置，分别是家庭网络、工作网络、公共网络和域，每个网络位置由于受到的威胁不同而具有不同的包过滤规则集。就以“远程协助”功能为例，不同网络位置允许“远程协助”进行入站连接的规则是不同的：

“域”网络位置关于“远程协助”的入站规则：

![](https://image.3001.net/images/20200525/1590340120_5ecaaa18b4d4b.png!small)

“专用”网络位置（工作网络）关于“远程协助”的入站规则：

![](https://image.3001.net/images/20200525/1590340126_5ecaaa1e4e8d3.png!small)

“公用”网络位置（工作网络）关于“远程协助”的入站规则：

![](https://image.3001.net/images/20200525/1590340132_5ecaaa2405686.png!small)

而firewalld有公共、外部、非军事区等9个zone，另外也可以创建自定义的zone。每个zone也都拥有自己的包过滤规则集，用户也可以对zone中的已有规则进行增删改。firewalld根据网络接口当前关联的zone中的规则进行包过滤操作。防火墙规则的创建、修改和删除，实际上就是针对网络接口当前关联的zone中的服务、端口以及富规则等所进行的增删改操作。也可以通过将网络接口关联到新的zone来应用新的包过滤规则。

**2、不同zone的含义**

firewalld有9个内置的zone：

firewall-cmd --get-zones //查看防火墙全部的zone

![](https://image.3001.net/images/20200525/1590340144_5ecaaa309cb24.png!small)

drop（丢弃） //任何接收到的连接都被丢弃，没有任何回复。只允许出站的网络连接。

block（阻塞） //任何接收的网络连接都被阻塞，并给出IPv4的icmp-host-prohibited信息和IPv6的icmp6-adm-prohibited信息作为回应。

public（公共） //用于连接公共区域。不能相信来自这个区域的连接不会危害你的计算机，只接受经过选择的连接。

external（外部）
//如果Linux服务器作为路由器使用，可以将连接外部的接口的zone设置为external。不信任来自external网络的连接，只接受经过选择的连接。

dmz（非军事区） //用于非军事区的计算机。非军事区可以被公开访问，可以有限地进入内部网络，只接受经过选择的连接。

work（工作） //连接工作的区域，可以基本相信来自这个区域的连接不会危害你的计算机。只接受经过选择的连接。

home（家中） //用于家中的网络，可以基本相信来自home区域的计算机不会危害你的电脑。只接受经过选择的连接。

internal（内部） //用于内部网络，可以基本相信来自internal区域的计算机不会危害你的电脑。只接受经过选择的连接。

trusted（信任） //连接被信任的区域，接受所有连接。

**3、修改firewalld的默认zone**

//查看默认的zone

firewall-cmd --get-default-zone

![](https://image.3001.net/images/20200525/1590340159_5ecaaa3f2251b.png!small)

默认的zone是public

//将默认的zone设置为work

firewall-cmd --set-default-zone=work

![](https://image.3001.net/images/20200525/1590340172_5ecaaa4c4d414.png!small)

默认的zone已改成work

**4、查看网卡的zone**

//查看enp0s3网卡对应的zone

firewall-cmd --get-zone-of-interface=enp0s3

![](https://image.3001.net/images/20200525/1590340188_5ecaaa5c24347.png!small)

enp0s3网卡的zone是work。同时也能看到，只有部分网卡被分配了zone。

**5、将网卡添加到zone**

//将virbr0接口加入到internal zone

firewall-cmd --zone=internal --add-interface=virbr0

![](https://image.3001.net/images/20200525/1590340199_5ecaaa67d483c.png!small)添加成功，现在virbr0接口的zone是internal。

**6、修改网卡的zone**

firewall-cmd --zone=block --change-interface=enp0s3

![](https://image.3001.net/images/20200525/1590340207_5ecaaa6fd1d06.png!small)enp0s3网络接口的zone已改为block

**7、删除网卡的zone**

firewall-cmd --zone=block --remove-interface=enp0s3

![](https://image.3001.net/images/20200525/1590340218_5ecaaa7a5f679.png!small)删除zone之后，这个网卡就没有zone了。有人说删除网卡的zone之后会改为默认的zone，在这里不是这样的。

//重新将enp0s3的zone设置为work

firewall-cmd --zone=work --change-interface=enp0s3

![](https://image.3001.net/images/20200525/1590340226_5ecaaa8202c37.png!small)

**8、查看所有网卡所在的zone**

firewall-cmd --get-active-zones

![](https://image.3001.net/images/20200525/1590340232_5ecaaa8888be2.png!small)

**（二）设置service（服务）**

**1、查看所有的服务**

firewall-cmd --get-service

![](https://image.3001.net/images/20200525/1590340241_5ecaaa9161bc6.png!small)可以看到forewall的中已定义的全部服务。

**2、查看默认zone的服务**

firewall-cmd --list-service

![](https://image.3001.net/images/20200525/1590340251_5ecaaa9bb76ab.png!small)

默认的work区域有两个服务：dhcpv6-client和ssh

**3、查看指定zone的服务**

firewall-cmd --zone=区域名称 --list-service //查看drop区域的服务

![](https://image.3001.net/images/20200525/1590340260_5ecaaaa48eb31.png!small)

可以看到，不同的zone中的服务是不同的。

**4、将服务添加到zone**

firewall-cmd --zone=public --add-service=http //临时向public区域添加http服务

![](https://image.3001.net/images/20200525/1590340273_5ecaaab18d00a.png!small)

firewall-cmd --zone=public --add-service=ftp --permanent //持久化（写入配置文件）

![](https://image.3001.net/images/20200525/1590340282_5ecaaabad8db1.png!small)

从输出中可以看出，使用--permanent选项将服务添加到zone，实际上是将服务写入了zone的配置文件中。这样在重新读取zone的配置后才能生效，当前是不生效的。

可以将firewalld的配置文件理解成思科设备的startup-config。修改startup-config，对于running-configs是没有影响的。firewalld重读配置文件相当于copt running-config startup-config，当前生效的配置会被配置文件中的信息所覆盖从而不再生效。

**5、从zone中删除服务**

//从public区域删除ssh服务

firewall-cmd --zone=public --remove-service=ssh //删除内存中的策略

![](https://image.3001.net/images/20200525/1590340300_5ecaaacc282ab.png!small)

public区域的ssh服务被删除。

firewall-cmd --zone=public --remove-service=ssh --permanent //删除配置文件中的策略

![](https://image.3001.net/images/20200525/1590340314_5ecaaada0deb5.png!small)

public区域的ssh服务从配置文件中被删除。

**（三）firewalld应用实例**

**1、通过向区域添加服务来创建防火墙规则**

（1）要求

临时允许任意源地址访问enp0s3网卡监听的ftp、ssh、http服务

（2）实施方法

1）将指定的服务添加到enp0s3网卡对应的zone中

firewall-cmd --get-zone-of-interface=enp0s3 //查看网卡对应的zone

![](https://image.3001.net/images/20200525/1590340332_5ecaaaecb1a2d.png!small)

firewall-cmd --zone=work --list-service //查看work区域中的服务

![](https://image.3001.net/images/20200525/1590340340_5ecaaaf40e8e4.png!small)

已经包含了ssh服务，那么只要将ftp和http服务添加到work区域即可。

firewall-cmd --zone=work --add-service=http

firewall-cmd --zone=work --add-service=ftp

![](https://image.3001.net/images/20200525/1590340347_5ecaaafb1b3c6.png!small)

服务添加成功。

（３）验证防火墙阻断效果

//服务器端运行netcat（两个窗口中运行），模拟ftp服务和http服务监听21和80端口。

nc -l -p 21

nc -l -p 80

//客户端访问

![](https://image.3001.net/images/20200525/1590340359_5ecaab07cd59f.png!small)客户端连接成功。

//服务端netcat监听2121端口

nc -l -p 2121

//客户端访问

![](https://image.3001.net/images/20200525/1590340368_5ecaab10d5d7e.png!small)由于不存在允许访问2121端口的策略，客户端连接失败。

**2、通过向区域添加端口范围来创建防火墙规则**

（1）要求

永久允许访问enp0s3网卡监听的8080到8089端口

（2）实施方法

//查看网卡对应的zone

firewall-cmd --get-zone-of-interface=enp0s3

![](https://image.3001.net/images/20200525/1590340384_5ecaab2095b99.png!small)

//由于是自定义端口，现有的服务无法与之对应。可直接向zone中添加端口范围

firewall-cmd --zone=work --add-port=8080-8089/tcp --permanent

![](https://image.3001.net/images/20200525/1590340392_5ecaab2822bf4.png!small)自定义的端口范围已经写入了配置文件。

（3）验证防火墙阻断效果

//服务端使用netcat监听8080端口

![](https://image.3001.net/images/20200525/1590340402_5ecaab3272331.png!small)

//客户端访问

![](https://image.3001.net/images/20200525/1590340409_5ecaab39d2003.png!small)无法访问，显然是被防火墙阻断了。这是因为
--permanent只是将规则写入了配置文件，内存中还没有修改。需要将配置文件的内容重新读入内存才能生效。

//重新读取firewall防火墙配置

firewall-cmd --reload

![](https://image.3001.net/images/20200525/1590340418_5ecaab4265110.png!small)

//客户端连接

![](https://image.3001.net/images/20200525/1590340427_5ecaab4bc35fb.png!small)连接成功。说明新的规则生效了。但还是需要注意，重新装载配置后，前面临时设置的那些规则就都失效了。

![](https://image.3001.net/images/20200525/1590340437_5ecaab558ecad.png!small)![](https://image.3001.net/images/20200525/1590340443_5ecaab5b21000.png!small)

**3、通过向区域添加富规则(rich-rules)来创建防火墙规则**

（1）要求

只允许192.168.1.3访问本地的23端口，拒绝其它IP对访问23端口。

（2）实施方法

//允许192.168.1.3访问23端口

firewall-cmd --zone=work --add-rich-rule='rule family="ipv4" source
address="192.168.1.3" port port="23" protocol="tcp" accept'

//拒绝任意IP访问23端口

firewall-cmd --zone=work --add-rich-rule='rule family="ipv4" source
address="0.0.0.0" port port="23" protocol="tcp" reject'

//查看富规则

firewall-cmd --zone=work --list-rich-rules

![](https://image.3001.net/images/20200525/1590340463_5ecaab6f81b08.png!small)

（3）验证防火墙阻断效果

//服务器监听23端口

nc -l -p 23

//客户端直接访问

nping -tcp -p 23 -c 1 192.168.1.7

-p //指定目标端口

-c //指定发送数据包的数量

//客户端修改源地址后访问

nping -tcp -p 23 -c 1 -S 192.168.1.100 192.168.1.7

-S //将任意IP指定为源地址

//服务器端针对23端口抓包

![](https://image.3001.net/images/20200525/1590340479_5ecaab7f09310.png!small)可以看到，当使用防火墙允许的源地址访问时，服务器的23端口给出回应。但是当使用其它的IP作为源地址访问时，服务器不给出回应。这说明防火墙规则生效了。

**四、其它**

**（一）图形界面**

上面介绍了通过命令行配置firewalld的基本方法，也可以运行图形界面程序进行配置：

firewall-config

![](https://image.3001.net/images/20200525/1590340489_5ecaab899fff1.png!small)

理解了原理之后配置方法就比较简单了，这里不再详述。

**（二）默认zone**

针对默认zone，在使用firewall-cmd命令进行操作时可不指定zone的名称

firewall-cmd --add-service=https //向默认zone中添加服务

firewall-cmd --list-service //查看默认zone中的服务

![](https://image.3001.net/images/20200525/1590340500_5ecaab947dbfc.png!small)由于网络接口enp0s3关联到了默认的work区域，那么允许访问本地的https服务这条规则自然就生效了。

 ***本文作者：regitnew，转载请注明来自FreeBuf.COM**

