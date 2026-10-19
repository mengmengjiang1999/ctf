阿里云ubantu下的Tomcat搭建和iptables防火墙设置

[ Trigger_o](https://www.jianshu.com/u/24846fb7177e)关注赞赏支持

# 阿里云ubantu下的Tomcat搭建和iptables防火墙设置

1.下载tomcat  
打开[http://tomcat.apache.org/](https://links.jianshu.com/go?to=http%3A%2F%2Ftomcat.apache.org%2F)找一个版本,选择core中的tar.gz下载  

image.png

2.上传到服务器  
windows使用winSCP  
mac进入终端,选择shell-新建远程连接

  

image.png

  

选择sftp,填写用户名和下面的sftp root@ip

  

image.png

  
输入密码连接上使用put命令上传  
put 本地路径 远端路径  
例如 put /Users/**/Downloads/apache-tomcat-8.5.54.tar.gz /root/

3.安装  
解压即可  
执行tar -zxvf apache-tomcat-8.5.35.tar.gz解压到当前路径

4.安装jdk  
下载jdk后安装第三步上传到服务器,解压,然后进入修改文件 vi /etc/profile  
新增

    
    
    export JAVA_HOME=/root/jdk-9.0.4
    export CLASSPATH=.:$JAVA_HOME/lib/dt.jar:$JAVA_HOME/lib/tools.jar:$JAVA_HOME/jre/lib/rt.jar
    export PATH=$JAVA_HOME/bin:$PATH
    

注意替换路径

5.运行  
进入Tomcat的bin目录,执行  
sh startup.sh  
显示tomcat started

然后返回上一级,进入logs文件夹, vi catalina.out 查看日志,这里我遇到了/jre/bin/java: not
found的问题,因为我有多个jdk,其中一个openjdk里面没有jre,但是Tomcat指定了这个jdk路径,因此需要修改tomcat的JAVAHOME和JREHOME,  
进入tomcat的bin/路径下,vi setclasspath.sh
,在最上面添加下面两行,指定的jdk路径,jdk9里面jre整合在了一起,之前的版本是有jre文件夹的,需要注意

    
    
    export JAVA_HOME=/root/jdk-9.0.4
    export JRE_HOME=/root/jdk-9.0.4
    

注意替换路径

6.设置防火墙  
这里选择了iptables  
ubantu可能默认安装了firewalld ,首先关闭firewalld

systemctl stop firewalld  
systemctl mask firewalld

然后安装iptables  
whereis iptables #查看有没有安装,输出了路径则已经安装  
apt-get install iptables #安装iptables

cd回到根目录  
vi /etc/iptables.rules #配置规则 添加以下内容

    
    
    *filter
    :INPUT DROP [0:0]
    :FORWARD ACCEPT [0:0]
    :OUTPUT ACCEPT [0:0]
    :syn-flood - [0:0]
    -A INPUT -i lo -j ACCEPT
    -A INPUT -m state --state RELATED,ESTABLISHED -j ACCEPT
    -A INPUT -p tcp -m state --state NEW -m tcp --dport 22 -j ACCEPT
    -A INPUT -p tcp -m state --state NEW -m tcp --dport 80 -j ACCEPT
    -A INPUT -p tcp -m state --state NEW -m tcp --dport 8080 -j ACCEPT
    -A INPUT -p tcp -m state --state NEW -m tcp --dport 443 -j ACCEPT
    -A INPUT -p icmp -m limit --limit 100/sec --limit-burst 100 -j ACCEPT
    -A INPUT -p icmp -m limit --limit 1/s --limit-burst 10 -j ACCEPT
    -A INPUT -p tcp -m tcp --tcp-flags FIN,SYN,RST,ACK SYN -j syn-flood
    -A INPUT -j REJECT --reject-with icmp-host-prohibited
    -A syn-flood -p tcp -m limit --limit 3/sec --limit-burst 6 -j RETURN
    -A syn-flood -j REJECT --reject-with icmp-port-unreachable
    COMMIT
    

# 如果需要增加新的端口,可以增加

    
    
    -A INPUT -p tcp -m state --state NEW -m tcp --dport 端口号 -j ACCEPT
    

iptables-restore < /etc/iptables.rules #执行规则  
vi /etc/network/if-pre-up.d/iptables #设置开机启动 添加以下内容

    
    
    #!/bin/bash
    iptables-restore < /etc/iptables.rules
    

chmod +x /etc/network/if-pre-up.d/iptables #添加执行权限  
iptables -L -n #查看规则是否生效.

7.设置安全组

  

image.png

  

进去之后点配置规则,再选择添加安全组规则  
可以添加自定义端口 8080/8080,授权对象0/0/0/0.0

最后sh startup.sh重启Tomcat

浏览器访问 [http://ip:8080](https://links.jianshu.com/go?to=http%3A%2F%2Fip%3A8080)  

image.png

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [CTF线下防御战 — 让你的靶机变成“铜墙铁壁”](https://www.jianshu.com/p/ab5dafb93f16)

作者:ssooking 原文链接 一. 前言 随着CTF的普及，比赛的形式也有了越来越多的花样，对于线下赛来说，开...

[r00tSec](https://www.jianshu.com/u/84a8bc868260)阅读 2,510评论 0赞 2

  * [LINUX防火墙iptables](https://www.jianshu.com/p/41d5cdbd6219)

1.安全技术 (1)入侵检测与管理系统（Intrusion Detection Systems）： 特点是不阻断任...

[尛尛大尹](https://www.jianshu.com/u/58d9e1cf800c)阅读 2,317评论 0赞 2

  * [防火墙 之 iptables 匹配条件讲解](https://www.jianshu.com/p/6fe53c3416b3)

1 概述 iptables命令中，需要根据匹配的条件作出相应的动作，本文将结合例子，讲解匹配条件 匹配条件分为基本...

[ghbsunny](https://www.jianshu.com/u/21762fb3dd5b)阅读 3,592评论 0赞 0

  * [Linux下iptables防火墙配置详解](https://www.jianshu.com/p/a07f49b051aa)

iptables命令及参数介绍iptables常用命令： 常见设置参数介绍： iptables配置文件 iptab...

[涅槃快乐是金](https://www.jianshu.com/u/0db920fbfca7)阅读 440评论 0赞 1

  * [肝胆病 心病性心理分析](https://www.jianshu.com/p/469afac1ea1c)

女人属阴，男人，老人属阳。五脏病多半跟女人生气上火来的，六腹病多半跟老人和男人生气上火来的。 怒气伤肝。引发头迷，...

[w道法自然](https://www.jianshu.com/u/41fe5c5c0df4)阅读 394评论 0赞 4

 