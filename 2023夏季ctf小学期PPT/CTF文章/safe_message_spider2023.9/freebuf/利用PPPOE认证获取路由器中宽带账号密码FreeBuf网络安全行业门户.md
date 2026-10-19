## 前言

 **回家时买了一台极路由准备换掉家里老掉牙的阿里路由器，想进后台看一下宽带账号密码，咦？？？后台密码是什么来着？？？**

**我陷入了沉思，家里的路由器一般都是pppoe拨号，而路由器在与pppoe认证服务器通过LCP协商好认证方法进行后，极可能会明文传输宽带账号和密码，那我们能不能本地搭建pppoe认证服务器并且路由器wan口连接本地网卡，wireshark抓取宽带账号密码呢？说干就干。**

## pppoe工作原理

PPPoE协议的工作流程包含发现和会话两个阶段，发现阶段是无状态的，目的是获得PPPoE终结端（在局端的ADSL设备上）的以太网MAC地址，并建立一个唯一的PPPoE
SESSION-ID。发现阶段结束后，就进入标准的PPP会话阶段。

当一个主机想开始一个PPPoE会话，它必须首先进行发现阶段，以识别局端的以太网MAC地址，并建立一个PPPoE SESSION-ID。在发现阶段，基于网络的拓扑，主机可以发现多个接入集中器，然后允许用户选择一个。当发现阶段成功完成，主机和选择的接入集中器都有了他们在以太网上建立PPP连接的信息。直到PPP会话建立，发现阶段一直保持无状态的Client/Server（客户/服务器）模式。一旦PPP会话建立，主机和接入集中器都必须为PPP虚接口分配资源。

### 关键认证阶段：

会话双方通过LCP协商好的认证方法进行认证，如果认证通过了，才可以进行网络层的IPCP协商。认证过程在链路协商LCP结束后就进行。此时可以抓取到宽带账号密码。

Router OS搭建pppoe认证服务器

使用RouterOS来实现PPPOE服务器的功能。下载ios镜像安装到Vmware虚拟机上。

当然你也可以使用Ubuntu或者是windows来搭建。

### Vmware配置

安装过程中最关键一步：网络连接模式改为桥接模式。

![image](https://image.3001.net/images/20180314/15210232268779.png!small)

因为我们用路由器wan口连接电脑有限网卡，所以虚拟网络编辑器里设置桥接网卡为有线网卡。

![image](https://image.3001.net/images/20180314/15210232338244.png!small)

### 安装PPPOE认证服务器

启动虚拟机，安装pppoe服务器，空格选择system和ppp选项就可以了，选中后按i进入安装过程，后面选项都选y就可以。

![image](https://image.3001.net/images/20180314/15210232468861.png!small)

重启后账号admin密码为空登陆到系统，

![image](https://image.3001.net/images/20180314/15210232509401.png!small)

### 配置PPPOE服务器

执行如下指令即可完成PPPOE服务器的配置

    
    
    /interface pppoe-server server add interface=ether1 service-name=Fake-PPPoE-Server authentication=pap
    /interface pppoe-server server enable 0
    

![image](https://image.3001.net/images/20180314/15210232578785.png!small)

### 获取PPPOE账号密码

使用wireshark监听本地连接，把拨号路由器的wan口网线插到电脑的网口上，断开路由电源，重新插上电源，wireshark会抓取到整个PPPOE认证的流程，找到PPP
PAP协议里面的Authenticate-Request就是宽带的账号密码，明文传输。

![image](https://image.3001.net/images/20180314/15210232718527.png!small)

## 写在后面

美滋滋使用双频段千兆路由器了。

 ***本文原创作者：婷儿小跟班✧，本文属FreeBuf原创奖励计划，未经许可禁止转载**

