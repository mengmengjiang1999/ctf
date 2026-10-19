## 关于DNSObserver

DNSObserver是个功能强大的DNS服务，该工具使用Go语言开发，可以帮助广大研究人员轻松检测各种类型的盲注漏洞。它可以监控渗透测试人员所搭建服务器的带外DNS交互信息，并通过Slack发送查询通知。DNSObserver可以帮助我们寻找的漏洞包括操作系统给盲注漏洞、SQL盲注漏洞和XXE盲注漏洞等等。

![](https://image.3001.net/images/20210517/1621241035_60a22ccb649c9830433b3.png!small)

## 工具安装

注册一个自己的域名；

搭建一台虚拟专用服务器来运行脚本（我们使用的是Ubuntu，而且还没有在其他系统上进行过测试）；

你自己的Slack工作空间和一个Webhook；

## 域名和DNS配置

如果你还没有自己的虚拟专用服务器，可以使用你熟悉的服务提供商创建一台新的Linux虚拟专用服务器，并记录下其公网IP地址。

注册一个新的域名，只要是允许设置自定义域名服务器和glue记录的都可以。

进入到新注册域名的DNS设置界面，找到glue记录设置选项，添加两个新的条目，对应新的域名服务器，并提供虚拟专用服务器的公网IP地址。

接下来，修改默认的域名服务器：

    
    
    ns1.<YOUR-DOMAIN>
    
    ns2.<YOUR-DOMAIN>

## 服务器配置

使用SSH登录至虚拟专用服务器，然后执行下列操作：

安装Go环境；

确保默认的DNS端口（53/UDP和53/TCP）已打开，然后运行下列命令：

    
    
    sudo ufw allow 53/udp
    
    sudo ufw allow 53/tcp

获取DNSObserver项目源码并安装依赖组件：

    
    
    go get github.com/allyomalley/dnsobserver/...

## DNSObserver配置

### 域名【必须】

配置你的新注册域名。

### IP地址【必须】

虚拟专用服务器的公网IP地址。

## 工具使用

现在，我们就可以开始网络监听了。如果你想要在DNSObserver的运行过程中用你的虚拟专用服务器做其他事情的话，请开启一个新的tmux会话。

首先，我们需要传递必须的参数和你的Webhook：

    
    
    dnsobserver --domain example.com --ip 11.22.33.44 --webhook https://hooks.slack.com/services/XXX/XXX/XXX

配置好之后，还需要引入一些自定义A记录查询请求，然后将参数添加进记录文件中：

    
    
    dnsobserver --domain example.com --ip 11.22.33.44 --webhook https://hooks.slack.com/services/XXX/XXX/XXX --recordsFile my_records.yml

假设一切都已经配置正确，DNSObserver就可以正常运行了。如需确认工具是否运行成功，可以打开一个终端窗口，然后针对新注册域名执行下列查询请求：

    
    
    dig example.com

此时，你将会收到一个Slack通知，并包含请求的详细信息。

## 项目地址

DNSObserver：【[ _GitHub传送门_](https://github.com/allyomalley/dnsobserver)】

## 参考资料

  * [ _https://www.allysonomalley.com/2020/05/22/dnsobserver/_](https://www.allysonomalley.com/2020/05/22/dnsobserver/)
  * [ _https://golang.org/doc/install_](https://golang.org/doc/install)
  * [ _https://api.slack.com/messaging/webhooks﻿_](https://api.slack.com/messaging/webhooks)

