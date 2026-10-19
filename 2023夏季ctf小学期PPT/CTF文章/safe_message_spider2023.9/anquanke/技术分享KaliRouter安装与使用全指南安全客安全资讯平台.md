# 【技术分享】KaliRouter安装与使用全指南

阅读量 **150793**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-09-07 13:42:17

 **x**

##### 译文声明

本文是翻译文章，文章来源：github.com/koenbuyens

原文地址：<https://github.com/koenbuyens/kalirouter>

译文仅供参考，具体内容表达以及含义原文为准。

****

****

译者：[WisFree](http://bobao.360.cn/member/contribute?uid=2606963099)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**  
**

**写在前面的话**

KaliRouter可以将你的Kali
Linux设备变成一台路由器，你将不仅能够记录下所有的网络流量（[Wireshark](https://www.wireshark.org/)），而且还可以将HTTP和HTTPS流量发送至一个拦截代理，例如BurpSuite等等。

  

**安装**

我们会将Kali
Linux配置成一台代理型路由器，连接至这台“路由器”的客户端（例如嵌入式设备和手机App）都可以正常进行网络通信，但是其中的某些数据包将会被我们的Kali
Linux设备所拦截并使用Wireshark进行监控，并重定向至代理服务器。Kali
Linux设备以及BurpSuite都将以透明代理的形式运行，客户端不会感受到它们的存在。整个运行架构如下图所示:

在配置我们的Kali Linux之前，我们需要配置[ **VMWare**](https://www.vmware.com/) 和网络接口。

1\. 我们在VMWare中运行Kali Linux，并将网络改为桥接模式，这样可以让Kali
Linux直接链接到网络之中，而被监控的设备（应用程序或手机）同样可以正常连接至网络。

2\. 我们需要连接两个适配器（以太网和WiFi），并给Kali分配USB适配器，我们选择使用的是[ **Ethernet LAN Network
Adapter ASIX AX88179**](https://www.amazon.com/Plugable-Gigabit-Ethernet-Network-Adapter/dp/B00AQM8586) 和[ **Atheros UB91C
USB无线适配器**](https://www.amazon.com/gp/product/B004Y6MIXS/ref=oh_aui_detailpage_o00_s00?ie=UTF8&psc=1)
。其实你可以使用任何一款Linux兼容的USB无线网卡，只要它支持混杂模式即可。

  

**将Kali Linux配置成路由器**

我们的Kali Linux设备会将USB网络接口的流量路由到Kali自己的网络连接，创建路由器的方法如下。

开始配置之前，我们需要先查看本机的网络接口。我们可以使用命令ifconfig查看插入USB适配器之前和之后的设备状态。

    
    
    $ ifconfig -a

我们的以太网适配器一般会是eth1，而WiFi适配器一般是wlan0。

我们需要配置network-manager服务，告诉该服务我们会将适配器的MAC地址添加到/etc/NetworkManager/NetworkManager.conf文件的unmanaged-devices参数之中，并接管我们自己添加的接口。

    
    
    [keyfile] unmanaged-devices=mac:d8:eb:97:b6:ce:12;mac:56:6b:a2:90:c4:b9

接下来，重启网络服务，这样设备会进入“无管理”状态。

    
    
    $ /etc/init.d/networking restart

**以太网配置**

在创建监听网络之前，我们需要选择一个合适的网络地址和子网掩码。我们这里要选择一个与Kali所在网络IP范围（eth0）不同的地址空间，以此来确保受监控设备的IP地址不会跟我们的监控网络发生冲突。在我们的配置环境中，我们选择的是172.16.0.0/12。

由于我们需要让我们的无线网络和有线网络处于同一网络中，我们选择使用[ **bridge-utils**](https://help.ubuntu.com/community/NetworkConnectionBridge)
工具在这两者之间搭建一个桥梁。

    
    
    $ apt-get install bridge-utils

接下来，删除任何分配给有线网络接口（eth1）的IP地址。

    
    
    $ ip addr flush dev eth1

创建一个名为br0的桥接接口。

    
    
    $ brctl addbr br0

将我们的有线接口eth1添加到桥接接口br0。

    
    
    $ brctl addif br0 eth1

接下来，开启桥接接口br0。

    
    
    $ ip link set dev br0 up

根据我们选择的IP地址空间，给这个br0接口分配一个IP地址。因为它的功能是作为被监控设备的网关，所以我们选择172.16.0.1。

    
    
    $ ip addr add 172.16.0.1/12 dev br0

**Wi-Fi数据链路层**

配置好以太网接口之后，使用hostapd程序创建一个无线接入点。使用apt-get命令安装hostapd（关于hostapd的使用和配置信息，请参考【[
**这份文档**](http://wireless.kernel.org/en/users/Documentation/hostapd) 】）：

    
    
    $ apt-get install hostapd

然后使用下列信息创建配置文件hostapd.conf：

    
    
    # create a wireless network with this interface; change it if your wireless card is not wlan0 interface=wlan0 # change this if a different bridge interface was chosen bridge=br0 # the name of our wireless network ssid=Monitor-Network # Change the passphrase to something you like wpa_passphrase=Monitor-Network # the driver used driver=nl80211 auth_algs=3 # the wireless channel we listen on. channel=7 driver=nl80211 # the mode we use (g) hw_mode=g # we don't log logger_stdout=-1 logger_stdout_level=2 max_num_sta=5 rsn_pairwise=CCMP wpa=2 wpa_key_mgmt=WPA-PSK wpa_pairwise=TKIP CCMP

创建完无线接口wlan0之后，我们要启用无线接入点：

    
    
    $ ip link set dev wlan0 up

接下来，让hostapd程序开启监控网络：

    
    
    $ hostapd ./hostapd.conf -B

**网络配置**

配置好无线和有线网络之后，我们要开启内核选项以支持IP转发功能，然后配置iptables将所有的网络数据包转发至该接口。

    
    
    $ sysctl -w net.ipv4.ip_forward=1 $ iptables -P FORWARD ACCEPT $ iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

**网络服务**

我们使用[ **dnsmasq**](http://www.thekelleys.org.uk/dnsmasq/doc.html)
来作为我们的DNS和DHCP服务器。使用下列命令安装dsnmasq：

    
    
    $ apt-get install dnsmasq

然后使用下列信息创建并配置dnsmasq.conf文件：

    
    
    # listen to this interface; change it if a different bridge name was chosen interface=br0 # give IP addresses, lease is valid for 8 hours dhcp-range=172.16.0.10,172.31.255.254,8h # router dhcp-option=3,172.16.0.1 # dns server dhcp-option=6,172.16.0.1 # upstream DNS server server=8.8.8.8 log-queries log-dhcp  # include addresses address=/attacker.com/172.16.0.1

配置完成之后，我们需要重启dnsmasq守护进程：

    
    
    $ service dnsmasq restart

**嗅探并拦截流量**

在我们的监控网络中所有设备的网络流量都是通过桥接接口br0传递的，我们可以直接通过wireshark来嗅探该接口的网络流量。我们这里选择使用tshark，它相当于是命令行界面的wireshark。接下来，我们将监听接口br0，并将所有监听到的流量数据写入到一份文件中（output.pcap）。

    
    
    $ tshark -i br0 -w ./output.pcap -P

一般来说，我们还需要拦截流量，因此我们还需要设置一些iptables规则来将HTTP/1.1和HTTPS流量重定向到我们的拦截代理（BurpSuite）。关于其他协议的设置方法，请参考这份【[文档](http://www.tldp.org/HOWTO/TransparentProxy-6.html)】。

第一条规则将会拦截端口80和443的所有tcp包（HTTP和HTTPS），并将数据发送给BurpSuite。

    
    
    $ iptables -t nat -A PREROUTING -i br0 -p tcp --dport 80 -j DNAT --to-destination burpip:burp_http_port $ iptables -t nat -A PREROUTING -i br0 -p tcp --dport 443 -j DNAT --to-destination burpip:burp_https_port

第二条规则将确保响应信息在发送到客户端之前先经过我们的Kali Linux。

    
    
    $ iptables -t nat -A POSTROUTING -o eth0 -s 172.16.0.0/12 -d burpip -j MASQUERADE

第三条规则其实并不是必须的，这条规则将确保Kali路由能够正确地将数据包发送给BurpSuite。

    
    
    $ iptables -A FORWARD -s 172.16.0.0/12 -d burpip -i br0 -o eth0 -p tcp --dport burp_http_port -j ACCEPT $ iptables -A FORWARD -s 172.16.0.0/12 -d burpip -i br0 -o eth0 -p tcp --dport burp_https_port -j ACCEPT

接下来，我们要将BurpSuite配置成一个透明代理。打开BurpSuite，点击Proxy标签，然后选择Options菜单，然后点击Add按钮。

对于HTTP流量，我们要给BurpSuite绑定80端口，然后勾选All interfaces选项。

接下来我们跳转到Request handling标签页，然后勾选Support invisible
proxying选项。这一步操作是必须的，勾选之后客户端将不会感受到BurpSuite的存在。

对于HTTPS流量，我们需要给BurpSuite绑定端口443，然后勾选All interfaces。

然后点击Request handling标签，按照如下图所示的方法进行设置。

  

**自动化**

为了方便起见，我们应该尽可能地实现自动化。你可以在我的[
**GitHub主页**](https://github.com/koenbuyens/kalirouter/blob/master/monitor.sh)
找到相关的[ **配置文件**](https://github.com/koenbuyens/kalirouter/tree/master/conf)
以及[ **脚本**](https://github.com/koenbuyens/kalirouter/blob/master/monitor.sh) 。

首先，从github获取Kalirouter的项目源码：

    
    
    $ git clone https://github.com/koenbuyens/kalirouter.git

安装相关的依赖组件：

    
    
    apt-get install dnsmasq hostapd bridge-utils

插入USB适配器，然后使用命令iptables -a找出适配器的名字和MAC地址。

告诉network-manager服务我们将通过添加适配器MAC地址来接管相关接口，并运行命令/etc/init.d/networking
restart来重启网络服务。/etc/NetworkManager/NetworkManager.conf文件的修改内容如下所示。

    
    
    [keyfile] unmanaged-devices=mac:d8:eb:97:b6:ce:12;mac:56:6b:a2:90:c4:b9

修改hostapd.conf文件，将其指向正确的无线网络接口（默认为wlan0）。

修改monitor.sh脚本中的接口变量，将其指向正确的接口。其中的WIRELESS_MONITOR_INTERFACE,
WIRED_MONITOR_INTERFACE和
INTERNET_INTERFACE分别对应的是USB无线网卡、USB有线网卡和Kali的VMWare接口。默认为wlan0、eth1和eth0。

修改monitor.sh脚本中的代理变量，将其指向BurpSuite的IP地址以及端口，其中PROXYBOX, PROXYBOX_HTTP_PORT和
PROXYBOX_HTTPS_PORT分别对应的是IP地址、HTTP端口和HTTPS端口，默认为172.16.0.1、80和443。

运行下列命令执行脚本文件：

    
    
    $ ./monitor.sh

输出数据保存在dumps/output.pcap文件中，你可以通过按下Ctrl+C来停止监控网络流量。

拦截嵌入式设备、移动应用和Windows应用程序的通信数据

运行了我们的监控脚本之后，我们就可以开始监控目标设备的网络流量了。

  

**嵌入式设备**

我们用一台嵌入式设备连接到了我们的监控网络中，然后让设备开始正常运行。如下图所示，我们的嵌入式设备（10.0.0.38）正在通过UDP与一个内网移动应用进行通信（192.168.1.230）。

  

**移动应用**

在开始监控移动应用之前，我们必须先设置好相关的信任证书。

1\. 通过点击Proxy标签页中的Import/export CA certificate选项导出BurpSuite证书。

2\. 通过选择Certificate in DER format选项将证书导出为DER文件。

对于安卓端应用来说，我们先要添加信任证书。

1\. 进入安卓系统的安全设置中。

2\. 然后从SD卡安装证书。

3\. 选择证书。

4\. 命名证书。

导入证书之后，我们就可以开始监听应用程序的网络数据了。

1\. 让移动设备连接到我们的监控网络之中，密码是我们在hostapd配置文件中设置的密码。

2\. 然后运行应用程序，下面给出的例子是Amtrak应用程序。

3\. 我们可以在BurpSuite中看到监听到的安卓应用HTTPS流量。

4\. 我们可以观察到wireshark记录下的所有的流量（图例为Facebook App）。

  

**Windows应用程序**

1.让我们的Windows设备连接到我们的监控网络之中。

2\. 导入Windows证书，详细步骤请参考这份【[文档](https://parsiya.net/blog/2016-02-21-installing-burp-certificate-authority-in-windows-certificate-store/)】。

3\. 开启需要监控的应用程序，我们这里直接选择Web浏览器。

4\. BurpSuite和Wireshark都将接收到所有的网络流量。

  

**总结**

Kalirouter可以帮助我们将Kali
Linux设备转换成一个能够拦截网络流量的代理路由器，对该项目感兴趣的同学可以访问Kalirouter的GitHub主页获取详细信息【[传送门](https://github.com/koenbuyens/kalirouter/blob/master/monitor.sh)】。注：同学们还可以在树莓派上使用Kalirouter。

  

**参考资料**

<https://www.psattack.com/articles/20160410/setting-up-a-wireless-access-point-in-kali/>

<https://cybergibbons.com/security-2/quick-and-easy-fake-wifi-access-point-in-kali/>

<https://ubuntuforums.org/showthread.php?t=716192>

<https://help.ubuntu.com/community/NetworkConnectionBridge>

<https://wiki.archlinux.org/index.php/Internet_sharing#Configuration>

<https://wiki.archlinux.org/index.php/software_access_point#Bridge_setup>

<https://wiki.debian.org/BridgeNetworkConnections#Manual_bridge_setup>

<https://help.ubuntu.com/lts/serverguide/network-configuration.html>

<http://www.tldp.org/HOWTO/TransparentProxy-6.html>

本文翻译自github.com/koenbuyens
[原文链接](https://github.com/koenbuyens/kalirouter)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **WisFree** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86785](/post/id/86785)

安全客 - 有思想的安全新媒体

本文转载自: [github.com/koenbuyens](https://github.com/koenbuyens/kalirouter)

如若转载,请注明出处： <https://github.com/koenbuyens/kalirouter>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p5.ssl.qhimg.com/t014c3fa13dce6c85dd.png) WisFree

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

