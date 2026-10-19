## 一、 **概述**

**本文章结合作者在平时工作中真实经历,首先介绍了现有扫描联网工控设备技术存在的缺陷,基于现有技术提出了一种防追踪溯源扫描工控设备的解决方法，并在工控安全态势感知系统、工控应急风险评估和远程渗透实际场景中应用。其次在解决方案中给出了具体的实施步骤和过程，最后通过多种方案比较，选定在国外购买的VPS上，自己搭建一套稳定、可靠和高效的vpn代理服务应用，并进行了防追踪溯源技术的验证。**

##  二、 **现有技术缺陷**

伴随中国智能制造2025、两化融合以及工业互联网等背景下，越来越多的工业控制系统暴露在网络空间里，为了掌握互联网上有多少工控设备，以及这些工控设备的型号和存在的风险，市面上大多采用工控态势感知系统、nmap以及plcscan等工具对联网的工控设备进行不间断扫描探测。这些系统或工具的流量出口大多经过公司内部机房或者国内云服务器上，现有技术存在如下缺陷和问题。

> 1）部署在公司内部机房，一旦触发扫描目标的入侵检测系统检测到发起扫描的源IP,则可以根据该IP进行反渗透或者反攻击，导致公司内部其它服务器遭受影响；
>
> 2）部署在国内云服务器上，一旦扫描目标的检测系统检测到发起扫描的源IP，则可以根据购买云服务器备案的客户信息进行溯源，并追究导致安全事故的责任人；
>
>
> 3）目前市面扫描探测联网工控设备(态势感知系统、nmap工具和plcscan等工具)均采用TCP或者UDP方式进行工控设备探测，扫描探测指纹未经过加密保护，容易被第三方截取并分析出采用的关键技术方法。
>
> 4）目前主流的代理服务器如shadowsocks只能对http或https应用进行代理，不能对ICMP、Telnet、原生tcp、udp socket
> 服务进行代理传输，达到隐蔽扫描的效果；
>
> 5)国内的VPN或者免费的VPN不稳定、已掉线，易被中国防火墙封锁。

##  三、 **解决方案**

本文章提出了一种基于防追踪溯源技术识别联网工控设备的应用方法，解决了传统技术中出现的未对扫描服务器进行追踪溯源的保护、未对扫描探测技术方法进行保护等问题。此方法主要分为扫描代理客户端、代理服务器和扫描目标组成。方法实现主要包含以下步骤：

步骤1：部署代理服务器，国外vultr官网购买一台VPS服务器,在部署上linux操作系统后，并部署OPENVPN代理服务器应用，并启动代理服务，监听代理客户端的请求。

步骤2：本地部署扫描服务器(如态势感知系统、nmap工具和plcscan扫描工具等)，并在扫描服务器上安装部署OPENVPN代理客户端，设置代理客户端的代理配置文件，主要是配置代理服务器的IP地址、端口、通信方式及证书等信息。

步骤3：通过扫描服务器执行相关的工控扫描任务对联网工控设备进行扫描识别。所有的扫描行为均会通过VPN代理服务器转发到扫描目标设备。目标设备返回信息到VPN代理服务器，代理服务再将信息转发给扫描客户端，扫描客户端根据返回的报文与工控指纹库进行匹配，来进行工控资产识别。
基于防追踪溯源识别联网工控设备的业务模型如下图所示：

![image.png](https://image.3001.net/images/20190625/1561448476_5d11d01cd3d1e.png!small)

扫描代理客户端：扫描客户端首先对代理服务器相关信息进行配置，主要配置代理服务的IP、端口及认证信息。并开始对目标IP设备进行扫描，此时由于配置了代理客户端，所有扫描请求数据不会直接发送到目标IP设备，而会通过VPN私有通道加密发送到VPN代理服务器上。

代理服务器：代理服务器获取的扫描客户端的扫描，会将数据无缝转发给真实的目标IP设备。

目标工控设备：目标工控设备收到来自VPN代理服务器扫描请求，会对VPN代理服务器进行响应，代理服务器会将此响应加密转发给原始扫描客户端。

数据加解密过程：扫描客户端会对扫描数据进行加密并传输给VPN代理服务器，代理服务器也会对响应扫描客户端的数据进行加密，扫描客户端收到数据会进行解密。

##  四、 **实施过程与验证方式**

###  **实施过程：搭建openvpn环境**

1）购买服务器

由于国内如阿里云购买服务器均要实名认证，国外购买服务器价格昂贵等特点，所以决定采用在vultr.com购买VPS服务器，服务稳定、价格低廉、服务器地理区域可任意切换，购买的VPS如下图所示：

![image.png](https://image.3001.net/images/20190625/1561448535_5d11d05758a2f.png!small)

2）利用docker在VPS上快速搭建openvpn代理应用

首先在linux上安装docker应用，安装成功后安装以下步骤进行openvpn代理服务器安装部署：

1.打开terminal终端，配置环境变量，输入如下命令：

    
    
    export OVPN_DATA=openvpn_data

2.创建一个数据卷存储配置文件和证书等文件,输入如下命令：

    
    
    docker volume create --name $OVPN_DATA

3.初始化配置文件到数据卷中,输入如下命令：

    
    
    docker run -v $OVPN_DATA:/etc/openvpn --rm kylemanna/openvpn ovpn_genconfig -u udp://140.82.*.*

140.82.*.* 需替换为购买vps虚拟服务主机IP地址

4.初始化配置，并保存授权密码,输入如下命令：

    
    
    docker run -v $OVPN_DATA:/etc/openvpn --rm -it kylemanna/openvpn ovpn_initpki

5.开启openvpn容器，输入如下命令:

    
    
    docker run -v $OVPN_DATA:/etc/openvpn -d -p 1194:1194/udp --cap-add=NET_ADMIN --name=openvpn kylemanna/openvpn

6\. 生成用户证书，如果需要生成多个用户证书可以执行多次该命令，输入如下命令：

    
    
    docker run -v $OVPN_DATA:/etc/openvpn --rm -it kylemanna/openvpn easyrsa build-client-full tencent nopass

7\. 将用户证书导出到本地文件，输入如下命令：

    
    
    docker run -v $OVPN_DATA:/etc/openvpn --rm kylemanna/openvpn ovpn_getclient tencent > tencent.ovpn

远程登录代理服务器如下图所示：

**![image.png](https://image.3001.net/images/20190625/1561448598_5d11d09621338.png!small)**

### **扫描服务器部署openvpn代理客户端**

1）linux Centos7部署使用，参照如下步骤：

1.安装epel yum源，输入如下命令：

![image.png](https://image.3001.net/images/20190625/1561448697_5d11d0f9d85d8.png!small)2.安装openvpn，输入如下命令：

    
    
    yun install -y openvpn

3.将代理服务器安装部署成功生成的tencent.ovpn文件按照如下方式进修改，tencent.ovpn文件内如下所示：

![image.png](https://image.3001.net/images/20190625/1561448907_5d11d1cba0567.png!small)

并将tencent.ovpn文件，上传到/etc/openvpn/目录下，然后日志输出到/var/log/openvpn.log。

4.在开机启动项/etc/rc.local 文件添加如下命令，并重启服务器

    
    
    openvpn --daemon --cd /etc/openvpn --config tencent.ovpn --log-append /var/log/openvpn.log

扫描服务器代理客户端信息如下图所示：

测试客户端IP:192.168.10.108

![image.png](https://image.3001.net/images/20190625/1561448953_5d11d1f9452f8.png!small)

客户端代理配置如下图所示：

![image.png](https://image.3001.net/images/20190625/1561448965_5d11d205a3499.png!small)

### **验证过程：防追踪溯源**

通过扫描服务器客户端代理对目标主机222.86.67.52和 114.221.127.188进行防追踪溯源技术验证。

1.应用层telnet协议代理验证

验证通过192.168.10.108(内网服务器)
通过代理服务器（vpn.server）进行telnet连接目标IP(114.221.127.188)地址的验证，如下图所示

![image.png](https://image.3001.net/images/20190625/1561449110_5d11d2962a1bd.png!small)

114.221.127.188机器抓包截图如下所示：

发现是通过140.82.63.14进行的

![image.png](https://image.3001.net/images/20190625/1561449172_5d11d2d45fcd7.png!small)

2.应用层telnet协议代理验证

验证通过192.168.10.108(内网服务器) 通过代理服务器（vpn.server）进行telnet连接目标IP(222.86.57.52)地址的验证

![image.png](https://image.3001.net/images/20190625/1561449236_5d11d314a37f4.png!small)

从上图可知，当客户端通过telent 目标 222.86.57.52 已经通过 vpn@serveryang服务器进行了数据包的转发。

3.ICMP协议代理验证

通过192.168.10.108(内网服务器) 通过代理服务器（vpn.server）进行ping 8.8.8.8的验证,如下图所示：

![image.png](https://image.3001.net/images/20190625/1561449259_5d11d32b45e20.png!small)

4.nmap扫描代理验证

nmap扫描验证如下图所示：

![image.png](https://image.3001.net/images/20190625/1561449304_5d11d3582d499.png!small)

5.利用扫描软件对S7协议plc进行验证

客户端对109.105.11.68进行S7协议plc探测验证如下图所示：

##  五、 **总结**

采用OPENVPN私有隧道进行扫描数据加密传输，不仅可以防止扫描行为被第三方截取或分析,而且还可以隐藏真实设备的身份，防止真实设备被追踪溯源,防止真实设备被反渗透、反攻击的风险。

OPENVPN部署简单便捷、传输稳定可靠、通过绑定域名，IP地址可以任意切换，可以对所有的网络通讯行进行代理转发。特别是对原生tcp或udp
socket应用进行完全转发，解决诸如某些代理只能对http或https协议进行代理转发的问题。

本文搭建的OPENVPN不仅可以用于工控设备隐藏扫描、远程渗透、应急风险评估等活动中达到隐藏自己真实身份，防止被追踪溯源的目的，而且还可以应用于翻墙，进行google、facebook及twitter等网站的访问。

 ***本文原创作者：yy0308，本文属FreeBuf原创奖励计划，未经许可禁止转载**

