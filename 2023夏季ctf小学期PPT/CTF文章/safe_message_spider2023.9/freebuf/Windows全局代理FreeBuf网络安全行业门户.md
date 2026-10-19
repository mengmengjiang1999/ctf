# 0x01 介绍

### 1\. 为什么要全局代理

在渗透的时候要保护好自己啊，不要被溯源到。  
在买的一些V.P.S上做扫描的时候，有可能会触发到V.P.S厂商(搬瓦工、Vultr的都有遇到过)的安全机制(如DDoS)，将我们的V.P.S停机。做好全局代理的情况下，我们就可以在自己的电脑上做些扫描操作了。

### 2\. 为什么不用proxifier

一直有在用proxifier，这里做个测试，除了局域网的IP，其余全部通过clash，规则如下：  
![](https://image.3001.net/images/20220219/1645286256_6211137072078362952ab.png!small)

测试ping谷歌和IP情况如下（可以看到并没有起作用）：  
![](https://image.3001.net/images/20220219/1645286257_6211137150767691f7a1f.png!small)  
![](https://image.3001.net/images/20220219/1645286258_6211137220672447df572.png!small)

> 更新：以上测试使用3.x版本，4.x版本可代理Windows终端流量

### 3\. 全局代理的基础

如果想深入了解的话，需要一些路由和tap/tun虚拟网卡的知识。  
推荐几篇文章，可以看一下：  
[通过openvxx分析tun实现隧道的数据流程](https://www.junmajinlong.com/virtual/network/data_flow_about_openvxx/)  
[理解Linux虚拟网卡设备tun/tap的一切](https://www.junmajinlong.com/virtual/network/all_about_tun_tap/)  
[理解物理网卡、网卡接口、内核、IP等属性的关系](https://www.junmajinlong.com/virtual/network/kernel_nic_ip/)

# 0x02 实操

### （一）Windows10全局代理

Windows10实现全局代理很简单，需要借助一款工具CFW(Clash For Windows)，下面借助最新款的CFW来进行演示（TAP模式）。  
![](https://image.3001.net/images/20220219/1645286258_62111372d5f025bb1dab1.png!small)

 **1\. 安装TAP**

![](https://image.3001.net/images/20220219/1645286259_621113738b3c722198e90.png!small)  
选择“TAP Device”Manage下的Install进行安装，安装完成后，适配器中会出现一个名为cfw-tap的虚拟网卡。  
![](https://image.3001.net/images/20220219/1645286260_621113744770bfa2d4e9d.png!small)

 **2\. 启用Service模式**

![](https://image.3001.net/images/20220219/1645286261_62111375064e05d51ed4c.png!small)  
a. 未启用Service模式下的情况下：Service Mode旁边的地球是灰色的。  
b. 选择“Service Mode”Manage下的Install进行安装，安装完成后地球变成绿色。  
![](https://image.3001.net/images/20220219/1645286261_62111375ada38b47f55a5.png!small)

 **3\. 开启Mixin**

a. 编辑Mixin配置文件，内容如下：

    
    
    mixin:
       dns:
         enable: true
         enhanced-mode: redir-host
         nameserver:
           - 223.5.5.5 # 真实请求DNS，可多设置几个
           - 8.8.8.8 # 真实请求DNS，可多设置几个
           - 114.114.114.114
       # interface-name: WLAN # 出口网卡名称，或者使用下方的自动检测
       tun:
         enable: true
         stack: gvisor # 使用 system 需要 Clash Premium 2021.05.08 及更高版本
         dns-hijack:
           - 198.18.0.2:53 # 请勿更改
         auto-route: true
         auto-detect-interface: true # 自动检测出口网卡
    

b. 启动Mixin  
![](https://image.3001.net/images/20220219/1645286262_621113765f51b327965d6.png!small)

 **4\. 测试**

![](https://image.3001.net/images/20220219/1645286263_6211137725250a9892f90.png!small)  
![](https://image.3001.net/images/20220219/1645286263_62111377eb14eb06dd368.png!small)

### （二）Windows7全局代理

我在这里直接使用cfw进行了测试，发现启用service模式的时候，并没有实际起作用，Service Mode旁边地球也一直处于灰色的状态。
下面使用另一款工具tun2socks进行全局代理。  
tun2socks有几款工具，我这里选择使用go写的一款go-tun2socks,项目地址：https://github.com/eycorsican/go-tun2socks

 **1\. 安装TAP**

a. 下载地址：http://build.openvxx.net/downloads/releases/tap-windows-9.22.1-I602.exe  
b. 安装完成后，会出现一个TAP-Windows Adapter V9的虚拟网卡  
![](https://image.3001.net/images/20220219/1645286264_62111378af0b8cb7bb6c6.png!small)

 **2\. 运行tun2socks**

a. 按照教程装完tap，再下载tun2socks后直接运行会发现，报如下错误：  
![](https://image.3001.net/images/20220219/1645286265_6211137968fd22911ce78.png!small)  
b. 经过调试分析后，是添加的虚拟网卡名称的问题。  
c. 经过跟踪调试源码，发现会将虚拟网卡名称与ifaceName进行比较，而ifaceName的默认值为tun1.  
![](https://image.3001.net/images/20220219/1645286266_6211137a75428ea0d99c3.png!small)  
d. 所以需要将添加的TAP虚拟网卡名称修改为tun1，修改完成后再次运行，结果如下(或者-tunName "虚拟网卡名称")：

  * ![](https://image.3001.net/images/20220219/1645286267_6211137b9ca044c62e432.png!small)

e. 完整参数运行

  * 需要提前准备好一个socks代理服务器（这里以本地用clash为例）

  * tun2socks-windows-4.0-amd64.exe -tunAddr 10.0.0.2 -tunGw 10.0.0.1 -tunDns 114.114.114.114 -prooxyType socks -proxyServer 127.0.0.1:7890 -tunName "本地连接 2"

  * 127.0.0.0:7890是clash在本地监听的一个socks5代理

 **3\. 路由配置**

a. 原始路由  
![](https://image.3001.net/images/20220219/1645286268_6211137c95cc339ca287c.png!small)  
b. 修改虚拟网卡的跳跃点数为1  
![](https://image.3001.net/images/20220219/1645286269_6211137da2dd5aef35de6.png!small)  
c. 之后运行tun2socks的时候，会自动添加一条路由

  * 因为此时虚拟网卡的metric的2相比于原始的默认路由11小，所以可以不用删除原始的默认路由。

  * ![](https://image.3001.net/images/20220219/1645286270_6211137e986b0944b613a.png!small)

d. 此时直接访问网站的话会发现访问不到，经过分析应该是clash出去的机场的IP会路由匹配到10.0.0.1，造成一个回环。

  * 因而此时需要找到clash出去的机场IP，通过clash的log和tun2sock的运行界面可以看到大量重复的一个IP，这个就有可能是我们机场的IP。

  * ![](https://image.3001.net/images/20220219/1645286271_6211137f620b51ea16f53.png!small)

  * ![](https://image.3001.net/images/20220219/1645286272_6211138040336ac0fb595.png!small)

  * 找到后需要让机场IP通过原始默认网关出去。

  * route add <机场IP> mask 255.255.255.255 192.168.14.1

  * ![](https://image.3001.net/images/20220219/1645286273_62111381298ee61464c8e.png!small)

 **4\. 测试**

![](https://image.3001.net/images/20220219/1645286274_6211138210d57193b7e01.png!small)

参考资料：[通过openvxx分析tun实现隧道的数据流程](https://www.junmajinlong.com/virtual/network/data_flow_about_openvxx/)  
参考资料：[理解Linux虚拟网卡设备tun/tap的一切](https://www.junmajinlong.com/virtual/network/all_about_tun_tap/)  
参考资料：[理解物理网卡、网卡接口、内核、IP等属性的关系](https://www.junmajinlong.com/virtual/network/kernel_nic_ip/)  
参考资料：[使用Clash Tun网卡模式](https://igghelper.com/helper/?p=402)

