**各位小伙伴，好久不见，甚是想念啊！最近由于各种事，差点耽搁之前给自己立的flag了——每月至少提交一篇稿子。这次算是抓住了6月的尾巴写的。**

## 0X01 初识

众所周知，SSH是建立在TCP/IP 5层模型的应用层的安全协议，专为远程登录会话和其他网络服务提供安全性的协议，在某种环境下<仅仅是某种环境下哦>
，它可以有效的防止远程管理中的DNS欺骗和IP欺骗。

为了让一些刚入门的童鞋也能看懂，我就尽量做到详细，希望能帮到大家，也不枉我熬夜写稿子！

![](https://image.3001.net/images/20190625/1561466744_5d121778dc750.png!small)

SSH 只需要知道服务器的ip地址、 （端口号默认是22） 管理员账号和密码，即可进行服务器的远程管理，网络安全遵循木桶原理，只要通过SSH 撕开
一个口子，对渗透人员来时这将是一个新的天堂。

## 0X02 情景再现

实验环境：MacBook Air 、Kali

（Windows 环境下需要可以安装Putty/XShell）

### 1>远程登录

![](https://image.3001.net/images/20190625/1561467856_5d121bd0e66f6.png!small)

### 2>远程输入恶意程序木马

我用python写了一个运行之后就会出现自动重启的脚本（恶作剧），远程传输给服务器运行，当然你也可以将这个脚本写到kali的自启动项里，那就爽歪歪了！
本文重点不是攻 ！

Note:Windows 下可以安装FileZilla 使用FTP进行文件传输

### 3>免密登录

SSH配置信息都保存在.SSH目录下，当第一登录会将SHA256保存到 known_host 里，方便下次再登录，就可无需授权登录。

![](https://image.3001.net/images/20190625/1561474615_5d1236378b7cf.png!small)

Step:

1) 生成公钥

![](https://image.3001.net/images/20190625/1561475795_5d123ad314724.png!small)

2) 免密登录

![](https://image.3001.net/images/20190625/1561476626_5d123e124f760.png!small)

Note:本人亲测，修改Mac电脑的登录密码，还是会被远程免密登录，足见SHA256的重要性了！大家要保护好自己的SHA256，要想女生保护自己的处女膜一样保护，哈哈！

### 3>免密登录的工作原理

![](https://image.3001.net/images/20190625/1561477318_5d1240c68fdea.png!small)

很简单，我就不废话了！

## 0X03 SSH密码爆破应用思路

在有漏洞的情况下可以获取shadow文件，对其进行暴力破解，以获取这些账号的密码，但在另外的一些场景中，无任何漏洞利用，这个时候就需要对SSH账号进行暴力破解。

方法：

1>对root账号进行暴力破解

2>使用中国姓名top500作为用户名进行暴力破解

3>使用top 3000 password字典进行密码破解

4>利用掌握信息进行社工信息整理并生成字典暴力破解

谈到爆破工具，首当其冲就是 世界顶级密码爆破工具：hydra

![](https://image.3001.net/images/20190626/1561520178_5d12e832b479a.png!small)

hydra -l 用户名 -p 密码字典 -t 线程 -vV -e ns ip ssh

Note:当然破解SSH的工具多了，Medusa、 patator、
BrutesPray、msf下利用ssh_login模块进行暴力破解、ssh后门，我就不一一讲解，想学的自己查！

## 0X04 SSH 爆破防范

1\. 修改/etc/ssh/sshd_config 默认端口为其它端口。例如设置端口为2232，则port=2232

2\. 在/etc/hosts.allow中设置允许的IP访问，例如sshd:192.168.17.144:allow

3\.
使用DenyHosts软件来设置，其下载地址：<https://sourceforge.net/projects/denyhosts/files/denyhosts/2.6/DenyHosts-2.6.tar.gz/download>

4\. 收集 /var/log/secure 里面的信息，若是某个IP 链接次数超过一定次数
，则把此ip记录到/etc/hosts.deny里面；通过crontab来执行，每分钟执行一次。

    
    
    #!/bin/bash
    
    #Denyhosts SHELL SCRIPT
    
    cat /var/log/secure|awk '/Failed/{print $(NF-3)}'|sort|uniq -c|awk '{print $2"=" $1;}' >/root/Denyhosts/Denyhosts.txt
    
    DEFINE="5"
    
    for i in `cat /root/Denyhosts/Denyhosts.txt`
    
    do
    
            IP=`echo $i|awk -F= '{print $1}'`
    
            NUM=`echo $i|awk -F= '{print $2}'`
    
            if [ $NUM -gt $DEFINE ]
    
            then
    
                    ipExists=`grep $IP /etc/hosts.deny |grep -v grep |wc -l`
    
                    if [ $ipExists -lt 1 ]
    
                    then
    
                    echo "sshd:$IP" >> /etc/hosts.deny
    
                    fi
    
            fi
    
    done

## 0X05 基于LongTail-Log-Analysis实现OpenSSH暴力破解口令采集蜜罐  

### 1>配置蜜罐

OpenSSH 6.7p1源码包，两个修改的C文件，一个OpenSSH的配置文件

![](https://image.3001.net/images/20190626/1561511978_5d12c82ae2d9a.png!small)

### 2> 编译安装

sshd-22是OpenSSH的服务器端，sshd_ config-22是对应配置文件。

![](https://image.3001.net/images/20190626/1561512051_5d12c8737f211.png!small)

### 3>效果

提取IP,username,pwd

![](https://image.3001.net/images/20190626/1561512217_5d12c919a911f.png!small)

![](https://image.3001.net/images/20190626/1561512263_5d12c947c7a23.png!small)

捕获了3万多口令!

![](https://image.3001.net/images/20190626/1561512315_5d12c97bc09d4.png!small)

### 4>伪装蜜罐

使用LongTail-Log-Analysis的install_openssh. sh脚本安装的话，默认会监听TCP 22和2222，建议不监听TCP
2222端口，减少OpenSSH蜜罐特征。

## 0X06 自己重复造轮子

![](https://image.3001.net/images/20190626/1561514859_5d12d36b4fc12.png!small)

 ***本文作者：星空111，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

