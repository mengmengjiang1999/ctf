## 关于Attack-Surface-Framework

Attack-Surface-Framework（简称ASF）是一款功能强大的安全检测工具，可以帮助广大研究人员发现组织或企业网络系统的内部和外部攻击面。

ASF能够为各大组织和企业充当一个“安全守护神”的角色，并提供一种“对象”的概念来保护企业安全。ASF可以发现组织和企业网络系统中的各类资产或子域名等信息、枚举网络端口和服务、跟踪可疑行为等，而且ASF本身也是一个兼具持续性和灵活性的攻击警报框架，并利用了一个额外的技术支持层通过公开可用的PoC来抵御0
day漏洞的威胁。

ASF是一个开源项目，它利用了一个非常强大的工具库，并使用了图形化用户界面进行功能封装，ASF的系统架构图如下：

![](https://image.3001.net/images/20211127/1637956904_61a13d286b31363c0c68a.png!small)

## 工具要求

最新版本的Kali Linux x64系统；

至少16GB RAM

1TB HD（建议使用XFS文件系统）

## 工具构建&运行

首先，我们需要以root权限运行命令行终端，然后使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/vmware-labs/attack-surface-framework.git /opt/asf

切换至项目目录下，并运行工具安装脚本：

    
    
    cd /opt/asf/
    
    ./setup.sh

然后，设置你的用户名、电子邮件和密码。

安装完成之后，继续运行下列命令（我们建议运行“screen -S asf”命令来建立一个screen绘画，并实现服务器持久运行）：

    
    
    cd /opt/asf/frontend/asfgui/
    
    . bin/activate
    
    python3 manage.py runserver 0.0.0.0:8080

## 安全扫描

假设你现在在云端或者在本地实例上安装了ASF，我们建议用户通过SSH并使用端口转发来访问ASF。

 **针对ASF GUI：**

    
    
    ssh -i "key.pem" -L 8080:127.0.0.1:8080 user@yourhost

 **访问Graylog2仪表盘：**

    
    
    ssh -i "key.pem" -L 9045:127.0.0.1:9045 user@yourhost

接下来，打开你的浏览器，然后访问下列地址：

 **ASF（输入你安装时配置的用户名和密码）：**

    
    
    http://127.0.0.1:8080

 **Graylog2（默认用户名和密码均为admin，可以在/graylog/docker-compose.yaml中修改）：**

    
    
    https://127.0.0.1:904

## 工具使用截图

### 输入测试目标

![](https://image.3001.net/images/20211127/1637957002_61a13d8a9d45e5a4daf39.jpg!small)

### 资产扫描和发现

![](https://image.3001.net/images/20211127/1637956996_61a13d842c9a1f928c468.jpg!small)

### 端口和服务枚举

![](https://image.3001.net/images/20211127/1637956990_61a13d7e82b1eb5750696.jpg!small)

### 红队模块

![](https://image.3001.net/images/20211127/1637956983_61a13d775d915d285caee.jpg!small)

## 许可证协议

本项目的开发与发布遵循BSD-2开源许可证协议。

## 项目地址

 **Attack-Surface-Framework：** 【[ _GitHub传送门_](https://github.com/vmware-labs/attack-surface-framework)】

## 参考资料

> [ _https://kali.org/get-kali/_](https://kali.org/get-kali/)
>
> [
> _https://www.blackhat.com/us-21/arsenal/schedule/index.html#vdoberman-24096_](https://www.blackhat.com/us-21/arsenal/schedule/index.html#vdoberman-24096)
>
> [ _https://www.djangoproject.com/_](https://www.djangoproject.com/)
>
> [ _https://github.com/creativetimofficial/material-dashboard-> django_](https://github.com/creativetimofficial/material-dashboard-django)
>
> [ _https://nmap.org/_](https://nmap.org/)
>
> [ _https://github.com/OWASP/Amass_](https://github.com/OWASP/Amass)
>
> [
> _https://github.com/lanjelot/patator_](https://github.com/lanjelot/patator)
>
> [
> _https://github.com/FortyNorthSecurity/EyeWitness_](https://github.com/FortyNorthSecurity/EyeWitness)
>
> [
> _https://github.com/projectdiscovery/nuclei_](https://github.com/projectdiscovery/nuclei)
>
> [ _https://www.metasploit.com_](https://www.metasploit.com)
>
> [ _https://www.kalilinux.org_](https://www.kalilinux.org)
>
> [ _https://www.graylog.org/products/open-> source_](https://www.graylog.org/products/open-source)
>
> [
> _https://github.com/wpscanteam/wpscan_](https://github.com/wpscanteam/wpscan)
>
> [ _https://github.com/vanhauser-thc/thc-> hydra_](https://github.com/vanhauser-thc/thc-hydra)
>
> [ _https://nxlog.co/products/nxlog-community-> edition_](https://nxlog.co/products/nxlog-community-edition)
>
> [ _https://www.docker.com/﻿_](https://www.docker.com/)

