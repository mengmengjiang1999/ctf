## 一、操作目的和应用场景

大家好，今天为大家介绍如何让宿主机利用在虚拟机中建立的VPN加密隧道连接内网。

### （一）问题的产生

在进行渗透测试时，如果能拿下目标的VPN网关，则可以在本机安装该VPN网关的客户端软件，通过VPN直接连接到对方内网。但是VPN客户端一般都是基于windows系统的，不管你将windows作为宿主机使用还是作为虚拟机使用，都面临着一个问题，就是只有安装了VPN客户端的windows系统能使用VPN连接，而安装了渗透软件的Linux系统无法使用VPN。根据网友的思路，我通过研究发现，Linux宿主机也可以使用Windows虚拟机建立的VPN连接，这样就很方便了。下面我讲一下思路和具体的方法。

### （二）解决的思路

首先为windows虚拟机创建两块网卡，一块工作在桥接模式，用于访问互联网，另一块工作在Host-Only模式，为宿主机提供访问VPN网络的通道。

之后在虚拟机中启用VPN，启用后将生成VPN虚拟网卡。针对VPN虚拟网卡设置网络连接共享，将连接共享给host-only网卡。

之后宿主机将去网内网地址的路由指向虚拟机中host-only网卡对应的地址，这样，宿主机去网内网的数据包就可以在虚拟机中按照host-only网卡—VPN网卡—桥接网络—互联网的顺序一路走向内网了。

下面给出具体的配置方法。

## 二、平台及工具版本

host系统：linux mint 19.3

虚拟机管理程序：virtualbox 6.1

虚拟机：window 7

计算机硬件：小米笔记本电脑

## 三、操作步骤

### （一）针对Windows虚拟机的设置

1、为虚拟机系统配置网卡

win7虚拟机添加两块网卡，网卡1的连接方式为桥接：

![](https://image.3001.net/images/20200423/1587571680_5ea06be0d36f2.png!small)

网卡2的连接方式为host-only：

![](https://image.3001.net/images/20200423/1587571688_5ea06be890fe2.png!small)

前提是已经创建了Host-Only网络。创建的方法是在VirtualBox主界面选择“管理”，打开“主机网络管理器”，点击“创建”即可创建vboxnet0网卡。

2、在虚拟机中配置网络连接共享

启动虚拟机，运行VPN客户端软件，生成VPN虚拟网卡（本地连接 2），得到了内网地址。此时host-only网卡的IP地址是192.168.56.0/24网段的。

![](https://image.3001.net/images/20200423/1587571715_5ea06c033f205.png!small)

将VPN网卡的连接共享给host-only网卡（下图中，“本地连接”为桥接网卡，“本地连接 2”为VPN网络建立的网卡，“本地连接 3”为host-only网卡）：

![](https://image.3001.net/images/20200423/1587571731_5ea06c13380dc.png!small)

共享后，虚拟机中host-only网卡的IP地址被系统自动修改为192.168.137.1。

![](https://image.3001.net/images/20200423/1587571747_5ea06c23c824a.png!small)

### （二）针对Linux宿主机的设置

1、设置Linux宿主机的host-only网络

为了让Linux宿主机能与Windows虚拟机的host-only网卡连通，需要将vboxnet0网络的网卡设置为相同网段的地址，如192.168.137.100，子网掩码为255.255.255.0。

![](https://image.3001.net/images/20200423/1587571777_5ea06c41c3f4a.png!small)

同时要将vboxnet0网卡的DHCP服务器地址设置为192.168.137.100，分配的IP地址范围设置为192.168.137.101到192.168.137.254。

![](https://image.3001.net/images/20200423/1587571794_5ea06c52c031e.png!small)

如果不想使用DHCP服务为虚拟机分配IP地址，也可以不选择“启用服务器”。点击“应用”以保存更改。

2、host-only网络的连通性测试

![](https://image.3001.net/images/20200423/1587571844_5ea06c84f1df6.png!small)

宿主机可以连接到虚拟机的host-only网卡。

3、Linux宿主机添加路由

route add -net 10.0.0.0/8 gw 192.168.137.1
//添加静态路由，将去往10.0.0.0/24网络（目标内网的网段）的流量送到虚拟机的host-only网卡。在虚拟机中流量会通过VPN网卡的连接共享转发给桥接网卡，之后再向外连接，最终到达VPN网关和内网。

route -n //查看路由表

![](https://image.3001.net/images/20200423/1587571868_5ea06c9c07b3a.png!small)

可以看到，静态路由条目已经添加上了。

### （三）Linux宿主机访问内网

1、测试Linux宿主机与内网之间的连通性

![](https://image.3001.net/images/20200423/1587571894_5ea06cb64a905.png!small)

内网IP地址可以ping通。

2、Linux宿主机访问内网应用

![](https://image.3001.net/images/20200423/1587571914_5ea06cca21b8e.png!small)

其它工具也可以访问内网应用，不再赘述。

## 四、总结

### （一）保存配置

注意保存宿主机和虚拟机的配置。虚拟机可以通过拍摄快照解决，那么宿主机怎样使那条静态路由条目长久生效呢？可以在Linux宿主机（debian系列）的网卡配置文件中这样操作：

vi /etc/network/interfaces //在网卡配置信息后面加入一行：

    
    
    up route add -net 10.0.0.0 netmask 255.0.0.0 gw 192.168.137.1

保存退出

### （二）宿主机和虚拟机都是windows系统

对于这种情况，与上面的区别就在于在windows宿主机中添加路由的命令不同。route add 10.0.0.0 mask 255.0.0.0
192.168.137.1

### （三）宿主机windows、虚拟机Linux

还有一种情况，就是虚拟机使用Linux，宿主机使用Windows，在windows宿主机中安装和运行VPN客户端软件，这种情况可能更常见。这种情况的配置方法是类似的：为Linux虚拟机创建两块网卡，分别是桥接和Host-Only模式。Windows宿主机在运行VPN客户端软件后将有三块网卡：物理网卡、VPN虚拟机网卡、Host-Only网络的网卡。将VPN虚拟网卡的连接共享给Host-Only网络的网卡，之后在Linux虚拟机中添加路由，将去往内网的流量转发给宿主机Host-Only网络网卡的IP地址。之后在虚拟机中就应该能访问内网了。这种方法我没有试过，大家可以参考前面的命令尝试一下。

## 五、参考网址

<https://yidianyidi.fun/VirtualBox/yidianyidi-1708121150.html>

 ***本文作者：regitnew，转载请注明来自FreeBuf.COM**

