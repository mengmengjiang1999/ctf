## SoftEther简介

**我们来先科普一下什么是SoftEther吧，SoftEther是由日本筑波大学的登大遊在硕士论文中提出的开源、跨平台、多重协议的虚拟专用网方案,是专门为穿过防火墙而设计的。拿我的话来说，又一个梯子，其实我更看重的是他的内网穿透功能，而且可以穿透防火墙，下面来一张图片，说明它的强大。**

![](https://image.3001.net/images/20200310/1583805624_5e66f4b877aea.png!small)

> 这里不做搭建讲解参考链接:<https://www.mivm.cn/softether-vpn-lan/>

windows softether VPN 配置端口转发

准备环境

上网环境（VPS）：192.168.118.104（假装是公网） win2008x64

未上网环境：192.168.118.184 win7x64

##  **0x01 创建虚拟网卡**

现在上网环境（VPS）添加虚拟网卡，

> 参考<https://jingyan.baidu.com/article/b87fe19eb3f0f05219356858.html>

![](https://image.3001.net/images/20200310/1583805824_5e66f5801350e.png!small)然后给这个虚拟网卡设置IP地址：10.10.10.10

![](https://image.3001.net/images/20200310/1583805858_5e66f5a2198ea.png!small)

##  **0x02 安装softether server**

给上网机器（VPS）安装windows softether server服务端，如果先安装了再添加的虚拟网卡，需要重启系统才能识别到添加的虚拟网卡。

##  **0x03 配置softether server**

配置softether server，首先直接connect重置密码。然后connect进入管理界面后的提示框直接退出，再删除默认的virtual hub。

##  **0x04 创建Virtual Hub**

手动重新建create a virtual hub，

![](https://image.3001.net/images/20200310/1583805930_5e66f5ea3fc71.png!small)选中新建的virtual
hub，管理，manage users新建用户设置VPN帐号密码，然后退出当前窗口。

![](https://image.3001.net/images/20200310/1583805975_5e66f617180c1.png!small)

##  **0x05 配置SecureNAT**

退出用户管理界面后，设置SecureNAT，并Enable SecureNAT。

然后配置NAT详细，点击SecureNAT Configuration。

本例中的配置网段如下：（建议把左下角的log file功能去掉）

![](https://image.3001.net/images/20200310/1583806008_5e66f638f182d.png!small)到此后退出Management
of Virtual Hub对话框界面，到主管理界面。

##  **0x06 设置桥接**

点击Local Bridge Setting，创建一个桥接，就是刚建立的虚拟网卡（LoopBack网卡）和你的virtual hub建立一个新的桥接。

![](https://image.3001.net/images/20200310/1583806056_5e66f6686d803.png!small)

至此，server端的softether配置结束。

这样客户端连接VPN后，第一个用户连接过来分配的IP地址会是10.10.10.150，同时也可以通过NAT进行上网。

##  **0x07 设置端口转发**

在上网机器（VPS）上，CMD执行netsh进行转发，也可以使用工具比如LCX等。

    
    
    netsh interface portproxy add v4tov4 listenaddress=vpsip listenport=443 connectaddress=10.10.10.150 connectport=443

删除转发

    
    
    netsh interface portproxy delete v4tov4 listenaddress=vpsip listenport=443

查询所有规则

    
    
    netsh interface protproxy show all

vpsip为你的服务器公网IP地址

转发测试OK

![](https://image.3001.net/images/20200310/1583806110_5e66f69e655b7.png!small)

***本文作者：lll377，转载请注明来自FreeBuf.COM**

