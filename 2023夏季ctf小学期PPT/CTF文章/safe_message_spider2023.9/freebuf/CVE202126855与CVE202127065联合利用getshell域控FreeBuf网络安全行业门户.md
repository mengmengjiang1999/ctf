***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 一、 简介

Exchange
Server是微软公司的一套电子邮件服务组件，是个消息与协作系统，主要提供包括从电子邮件、会议安排、团体日程管理、任务管理、文档管理、实时会议和工作流等协作应用。

![](https://image.3001.net/images/20210509/1620531316_60975874ee84802b68bb2.jpg!small)

## 二、 漏洞概述

CVE-2021-26855与CVE-2021-27065是微软在2021年3月2日发布的高危漏洞公告，危害等级高危。CVE-2021-26855是一个ssrf（服务器端请求伪造）漏洞，攻击者可以利用该漏洞绕过身份验证发送任意http请求。CVE-2021-27065是一个任意文件写入漏洞，单独情况下该漏洞需要进行身份认证，此漏洞还伴生着一个目录跨越漏洞，攻击者可以利用该漏洞将文件写入服务器的任何路径。两个漏洞相结合可以达到绕过权限直接getshell。

## 三、 影响范围

Microsoft Exchange 2010

Microsoft Exchange 2013

Microsoft Exchange 2016（本环境为cu12）

Microsoft Exchange 2019

PS：在github搜索exp时看到一个影响范围据说是Exchange Server 2013 小于 CU23 Exchange Server 2016
小于 CU18 Exchange Server 2019 小于 CU7，所以本次利用并没有采用cu18，有兴趣的小伙伴可以试试。

## 四、 环境搭建

### 4.1 域管理员密码设置

下载windows server
2016，选择桌面体验进行安装。安装完成后进行Administrator密码设置，Exchange安装需要Administrator账户具有高强度密码。

1）在仪表盘上，点击 工具 菜单，选择 计算机管理 子菜单

![](https://image.3001.net/images/20210509/1620531354_6097589a9d2317ff51834.png!small)2）本地用户和组->用户

选中Administrator，点击右键，弹出的菜单中选择 设置密码 的子菜单

![](https://image.3001.net/images/20210509/1620531384_609758b84e73ef9782ee4.png!small)

3）输入新密码和确认密码，点击确定，即可修改成功

新密码要满足一定的安全性！

###
![](https://image.3001.net/images/20210509/1620531408_609758d0f22d29059e98b.png!small)4.2
AD服务器搭建

AD服务器的搭建过于繁琐就不在此文章中复述，提供我在安装时参考的文章。

> <https://www.jb51.net/article/163510.htm>

### 4.3 exchange安装

我在这个位置卡了接近4个小时，安装exchange的话是需要提前安装一部分文件。

1)在 Windows PowerShell 中运行以下命令，安装必需的 Windows 组件：

    
    
    Install-WindowsFeature NET-Framework-45-Features, Server-Media-Foundation, RPC-over-HTTP-proxy, RSAT-Clustering, RSAT-Clustering-CmdInterface, RSAT-Clustering-Mgmt, RSAT-Clustering-PowerShell, WAS-Process-Model, Web-Asp-Net45, Web-Basic-Auth, Web-Client-Auth, Web-Digest-Auth, Web-Dir-Browsing, Web-Dyn-Compression, Web-Http-Errors, Web-Http-Logging, Web-Http-Redirect, Web-Http-Tracing, Web-ISAPI-Ext, Web-ISAPI-Filter, Web-Lgcy-Mgmt-Console, Web-Metabase, Web-Mgmt-Console, Web-Mgmt-Service, Web-Net-Ext45, Web-Request-Monitor, Web-Server, Web-Stat-Compression, Web-Static-Content, Web-Windows-Auth, Web-WMI, Windows-Identity-Foundation, RSAT-ADDS

2)按顺序安装以下软件：

a. [.NET Framework
4.8](https://download.visualstudio.microsoft.com/download/pr/014120d7-d689-4305-befd-3cb711108212/0fd66638cde16859462a6243a4629a50/ndp48-x86-x64-allos-enu.exe)

b.[2016 年 12 月 13 日 (KB3206632)
安全更新](https://support.microsoft.com/help/4004227)

c.[Visual C++ Redistributable Package for Visual Studio
2013](https://support.microsoft.com/help/4032938)

d.[Microsoft 统一通信托管 API 4.0 核心运行时（64
位）](https://www.microsoft.com/download/details.aspx?id=34992)

以上部分为Exchange安装先决条件，未安装以上文件将无法安装Exchange

接下来开始安装Exchange。

![](https://image.3001.net/images/20210421/1618975674_607f9bbad64948a09bfb8.png!small?1618975676096)![](https://image.3001.net/images/20210421/1618975691_607f9bcb2f5aa16af9d62.png!small?1618975692435)

  

![](https://image.3001.net/images/20210421/1618975694_607f9bce721252165133d.png!small?1618975695633)

![](https://image.3001.net/images/20210421/1618975709_607f9bdd5d5e8d903ebe4.png!small?1618975710664)然后进行安装，安装需要较大存储，建议虚拟机设置为60G，安装完成后进行重启，重启成功后访问127.0.0.1/ecp即可跳转至登录页面。

![1620533769_609762097740a14ba7e82.png!small?1620533769256](https://image.3001.net/images/20210509/1620533769_609762097740a14ba7e82.png!small?1620533769256)

为了让各位看官可以正常的复现这个漏洞，不在搭环境处浪费过多时间，已将需要下载的文件上传至百度云，虚拟机镜像也上传了，想要自己搭环境的大佬们可以将需要文件直接下载。虚拟机镜像为已装好的环境。

搭建好的虚拟机镜像与环境搭建所需要的文件都已经上传到了百度云。

关注公众号：红队攻防回复林鹿获取exchange环境靶场。

![](https://image.3001.net/images/20210509/1620547998_6097999eb5165c4632ff1.jpg!small)

## 五、漏洞复现

<https://github.com/mai-lang-chai/Middleware-Vulnerability-detection/blob/master/Exchange/CVE-2021-26855%20Exchange%20RCE/exp.py>

exp以上，用法为：python exp.py -u 192.168.198.141 -email Administrator -suffix
@linlu.com

该exp默认使用代理模式，需将exp中关于代理的删除，不然无法连接服务器。

![1620533874_60976272c0e281d865843.png!small?1620533874488](https://image.3001.net/images/20210509/1620533874_60976272c0e281d865843.png!small?1620533874488)

建议用cmd运行exp，powershell用exp会出现这种情况。

![1620533962_609762cad6f85755521f6.png!small?1620533962443](https://image.3001.net/images/20210509/1620533962_609762cad6f85755521f6.png!small?1620533962443)

## 六、漏洞防御

更新exchange版本：

[https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-26855﻿](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-26855)  
<https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-27065>

