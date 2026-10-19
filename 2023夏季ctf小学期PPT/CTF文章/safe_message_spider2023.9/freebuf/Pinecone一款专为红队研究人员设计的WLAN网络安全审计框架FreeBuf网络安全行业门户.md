![](https://image.3001.net/images/20220802/1659449172_62e92f5444dab4fe815fc.png!small)

## 关于Pinecone

Pinecone是一款专为红队研究人员设计的WLAN网络安全审计框架，该工具基于模块化开发，允许广大研究人员根据任务需求进行自定义功能扩展。Pinecone设计之初专用于树莓派，可以将树莓派打造为便携式无线网络安全审计工具，但也可以在基于Debian的操作系统中运行。

## 工具要求

如需运行Pinecone，首先我们需要一个基于Debian的操作系统（该工具已在树莓派、树莓派桌面端和Kali Linux上进行过测试）。

接下来，还需要安装并配置好下列组件：

> 1、Python 3.5+：你的发行版系统可能已经预安装了Python 3，如果没有则需手动安装；
>
> 2、dnsmasq：测试版本为v2.76；
>
> 3、hostapd-wpe：测试版本为v2.6；

我们可以通过下列命令安装该工具所需的运行环境：

    
    
    apt-get install python3
    
    apt-get install dnsmasq
    
    apt-get install hostapd-wpe

## 工具安装

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/pinecone-wifi/pinecone.git

接下来，使用pip3命令并通过项目提供的requirements.txt来安装该工具所需的Python组件包：

    
    
    pip3 install -r requirements.txt

## 工具使用

执行项目根目录中的pinecone.py文件即可运行Pinecone：

    
    
    root@kali:~/pinecone# python3 pinecone.py
    
    [i] Database file: ~/pinecone/db/database.sqlite
    
    pinecone >

我们可以通过一个类似Metasploit的命令行接口来控制Pinecone，输入“help”命令即可获取该工具支持的所有命令帮助信息，或者输入“help
'command'”查看指定命令的帮助信息：

    
    
    pinecone > help
    
     
    
    Documented commands (type help <topic>):
    
    ========================================
    
    alias  help     load  pyscript  set    shortcuts  use
    
    edit   history  py    quit      shell  unalias  
    
     
    
    Undocumented commands:
    
    ======================
    
    back  run  stop
    
     
    
    pinecone > help use
    
    Usage: use module [-h]
    
     
    
    Interact with the specified module.
    
     
    
    positional arguments:
    
      module      module ID
    
     
    
    optional arguments:
    
      -h, --help  show this help message and exit

“use 'moduleID'”命令可以激活一个指定的Pinecone模块，我们可以使用Tab键实现命令补全：

    
    
    pinecone > use
    
    attack/deauth     daemon/hostapd-wpe    report/db2json                  scripts/infrastructure/ap  
    
    daemon/dnsmasq    discovery/recon       scripts/attack/wpa_handshake
    
    pinecone > use discovery/recon
    
    pcn module(discovery/recon) >

每一个功能模块都有不同的参数选项，可以使用“help run”或“run --help”命令来查看已激活的模块帮助信息：

    
    
    pcn module(discovery/recon) > help run
    
    usage: run [-h] [-i INTERFACE]
    
     
    
    optional arguments:
    
      -h, --help            show this help message and exit
    
      -i INTERFACE, --iface INTERFACE
    
                            monitor mode capable WLAN interface (default: wlan0)

当一个模块被激活之后，可以使用“run [options...]”命令来使用该模块提供的功能：

    
    
    pcn script(attack/wpa_handshake) > run -s TEST_SSID
    
    [i] Sending 64 deauth frames to all clients from AP 00:11:22:33:44:55 on channel 1...
    
    ................................................................
    
    Sent 64 packets.
    
    [i] Monitoring for 10 secs on channel 1 WPA handshakes between all clients and AP 00:11:22:33:44:55...

如果模块在后台运行（比如说scripts/infrastructure/ap），我们可以使用“stop”命令来终止模块运行：

    
    
    pcn script(infrastructure/ap) > run
    
    net.ipv4.ip_forward = 1
    
    [i] Creating NAT rules in iptables for forwarding wlan0 -> eth0...
    
    [i] Starting hostapd-wpe and dnsmasq...
    
    Configuration file: ~/pinecone/tmp/hostapd-wpe.conf
    
    Using interface wlan0 with hwaddr 00:11:22:33:44:55 and ssid "PINECONEWIFI"
    
    wlan0: interface state UNINITIALIZED->ENABLED
    
    wlan0: AP-ENABLED
    
    pcn script(infrastructure/ap) > stop
    
    [i] Stopping hostapd-wpe and dnsmasq...
    
    net.ipv4.ip_forward = 0
    
    [i] Flushing NAT table in iptables...

除此之外，我们还可以使用“shell”或“！”命令来执行Shell命令：

    
    
    pinecone > !ls
    
    LICENSE  modules  module_template.py  pinecone  pinecone.py  README.md  requirements.txt  TODO.md

值得一提的是，当前版本的Pinecone会将所有的数据存储在一个SQLite数据库中，路径为db/，工具所使用的所有临时文件都存储在tmp/目录中。

## 许可证协议

本项目的开发与发布遵循GPL-3.0开源许可证协议。

## 项目地址

 **Pinecone** ：【[ _GitHub传送门_](https://github.com/pinecone-wifi/pinecone)】

## 参考资料

> [ _https://http.kali.org/pool/main/h/hostapd-> wpe_](https://http.kali.org/pool/main/h/hostapd-wpe)
>
> [ _https://github.com/aircrack-ng/aircrack-> ng/tree/master/patches/wpe/hostapd-wpe_](https://github.com/aircrack-> ng/aircrack-ng/tree/master/patches/wpe/hostapd-wpe)

