## 0x00 简介

Exchange
Server是微软公司的是一套电子邮件服务组件，是个消息与协作系统，主要提供包括从电子邮件、会议安排、团体日程管理、任务管理、文档管理、实时会议和工作流等协作应用。

## 0x01 漏洞概述

该漏洞是Exchange中的服务端请求伪造漏洞（SSRF），利用此漏洞的攻击者能够发送任意HTTP请求并绕过Exchange
Server身份验证，远程未授权的攻击者可以利用该漏洞以进行内网探测，并可以用于窃取用户邮箱的全部内容。

危害：该漏洞是Exchange中的服务端请求伪造漏洞（SSRF），利用此漏洞的攻击者能够发送任意HTTP请求并绕过Exchange
Server身份验证，远程未授权的攻击者可以利用该漏洞以进行内网探测，并可以用于窃取用户邮箱的全部内容。

## 0x02 影响版本

Microsoft Exchange 2013

Microsoft Exchange 2016 （此次使用的是CU18版本）

Microsoft Exchange 2019

Microsoft Exchange 2010

## 0x03 环境搭建

1，首先我们将我们搭建的windows-server-2016切换到administrator用户，如果不切换到 Administrator
用户进行安装Exchange的话，到了安装 Exchange 时会报一些错误。

A.按住Windows+R键，输入 Control，打开控制面

B.找到用户账户

C.配置高级用户配置文件属性

D.打开用户账户

E.点击用户，选中Administrators单击右键并设置密码: abc.123

![1618975618_607f9b82e5b933dcc831d.png!small?1618975620479](https://image.3001.net/images/20210421/1618975618_607f9b82e5b933dcc831d.png!small?1618975620479)

注销 — 选择 “Administrator” 进行登录

![1618975623_607f9b8707c1f1aeaf013.png!small?1618975624330](https://image.3001.net/images/20210421/1618975623_607f9b8707c1f1aeaf013.png!small?1618975624330)

2，Windows Server 2016 AD服务器搭建

打开服务器管理器，添加角色和功能

![1618975627_607f9b8b40ecda9fe8b76.png!small?1618975628691](https://image.3001.net/images/20210421/1618975627_607f9b8b40ecda9fe8b76.png!small?1618975628691)

一直下一步到服务器角色选择

![1618975630_607f9b8ec5699a9f77d7c.png!small?1618975632399](https://image.3001.net/images/20210421/1618975630_607f9b8ec5699a9f77d7c.png!small?1618975632399)

然后接着下一步到

![1618975635_607f9b9350f94a0a883e6.png!small?1618975636719](https://image.3001.net/images/20210421/1618975635_607f9b9350f94a0a883e6.png!small?1618975636719)

  

然后安装，双击提升为域控制器

![1618975640_607f9b98887949304e444.png!small?1618975641995](https://image.3001.net/images/20210421/1618975640_607f9b98887949304e444.png!small?1618975641995)

接着添加新林

![1618975643_607f9b9bbd1d4693d300f.png!small?1618975645027](https://image.3001.net/images/20210421/1618975643_607f9b9bbd1d4693d300f.png!small?1618975645027)

填写密码

![1618975646_607f9b9ef12b7350716db.png!small?1618975648395](https://image.3001.net/images/20210421/1618975646_607f9b9ef12b7350716db.png!small?1618975648395)

然后一直下一步，再点击安装

![1618975650_607f9ba2858cc864e550c.png!small?1618975652001](https://image.3001.net/images/20210421/1618975650_607f9ba2858cc864e550c.png!small?1618975652001)

安装完毕后自动重启

![1618975656_607f9ba8131bbe8d85376.png!small?1618975657242](https://image.3001.net/images/20210421/1618975656_607f9ba8131bbe8d85376.png!small?1618975657242)

3，安装 Exchange Server 2016

地址：https://www.microsoft.com/zh-cn/download/confirmation.aspx?id=102114

![1618975659_607f9bab269bf6571b4ac.png!small?1618975660560](https://image.3001.net/images/20210421/1618975659_607f9bab269bf6571b4ac.png!small?1618975660560)

然后下载.NET4.8，地址：

https://docs.microsoft.com/zh-cn/exchange/plan-and-deploy/prerequisites?view=exchserver-2016

![1618975663_607f9baf9ef70bab4ab26.png!small?1618975664987](https://image.3001.net/images/20210421/1618975663_607f9baf9ef70bab4ab26.png!small?1618975664987)

下载C++ 依赖包，地址：

https://www.microsoft.com/en-us/download/details.aspx?id=30679

![1618975667_607f9bb32133c682e85b7.png!small?1618975668468](https://image.3001.net/images/20210421/1618975667_607f9bb32133c682e85b7.png!small?1618975668468)

4，开始安装，选择不更新

![1618975671_607f9bb72f9d0ab65e9fa.png!small?1618975672446](https://image.3001.net/images/20210421/1618975671_607f9bb72f9d0ab65e9fa.png!small?1618975672446)

![1618975674_607f9bbad64948a09bfb8.png!small?1618975676096](https://image.3001.net/images/20210421/1618975674_607f9bbad64948a09bfb8.png!small?1618975676096)

![1618975687_607f9bc72c7508b66a411.png!small?1618975688482](https://image.3001.net/images/20210421/1618975687_607f9bc72c7508b66a411.png!small?1618975688482)

选择不使用推荐

![1618975691_607f9bcb2f5aa16af9d62.png!small?1618975692435](https://image.3001.net/images/20210421/1618975691_607f9bcb2f5aa16af9d62.png!small?1618975692435)

![1618975694_607f9bce721252165133d.png!small?1618975695633](https://image.3001.net/images/20210421/1618975694_607f9bce721252165133d.png!small?1618975695633)

一直下一步到安装

![1618975700_607f9bd406b86e437b71e.png!small?1618975701262](https://image.3001.net/images/20210421/1618975700_607f9bd406b86e437b71e.png!small?1618975701262)

检查完毕需要安装以下更新，地址：

https://docs.microsoft.com/zh-cn/exchange/plan-and-deploy/prerequisites?view=exchserver-2016

![1618975705_607f9bd936aade68c1859.png!small?1618975706527](https://image.3001.net/images/20210421/1618975705_607f9bd936aade68c1859.png!small?1618975706527)

然后点击安装

![1618975709_607f9bdd5d5e8d903ebe4.png!small?1618975710664](https://image.3001.net/images/20210421/1618975709_607f9bdd5d5e8d903ebe4.png!small?1618975710664)

然后出现以下界面为安装完毕

![1618975712_607f9be0bfaf8daa811fe.png!small?1618975714094](https://image.3001.net/images/20210421/1618975712_607f9be0bfaf8daa811fe.png!small?1618975714094)

安装成功后访问https://ip/ecp，即可到达exchange管理中心

![1618975720_607f9be863b55d3541cba.png!small?1618975721681](https://image.3001.net/images/20210421/1618975720_607f9be863b55d3541cba.png!small?1618975721681)

使用域名\用户名，密码即可登录管理中心

![1618975723_607f9beba65c5c0d08ae9.png!small?1618975726196](https://image.3001.net/images/20210421/1618975723_607f9beba65c5c0d08ae9.png!small?1618975726196)

![1618975734_607f9bf66f2916263e542.png!small?1618975735620](https://image.3001.net/images/20210421/1618975734_607f9bf66f2916263e542.png!small?1618975735620)

## 0x04 漏洞复现

1，漏洞exp下载地址

https://github.com/mai-lang-chai/Middleware-Vulnerability-detection/blob/master/Exchange/CVE-2021-26855%20Exchange%20RCE/exp.py

![1618975737_607f9bf955d93a4e1cb76.png!small?1618975738619](https://image.3001.net/images/20210421/1618975737_607f9bf955d93a4e1cb76.png!small?1618975738619)

运行exp获取shell

![1618975740_607f9bfc12a14c48c5e40.png!small?1618975741642](https://image.3001.net/images/20210421/1618975740_607f9bfc12a14c48c5e40.png!small?1618975741642)

## 0x05漏洞防御

微软官方已经发布了解决上述漏洞的安全更新，建议受影响用户尽快升级到安全版本，官方安全版本下载可以参考以下链接：

https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-26855

