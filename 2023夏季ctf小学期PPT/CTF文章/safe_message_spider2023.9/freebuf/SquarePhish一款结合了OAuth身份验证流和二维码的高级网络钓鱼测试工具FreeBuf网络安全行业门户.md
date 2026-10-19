![](https://image.3001.net/images/20221222/1671721643_63a472abb2b8dcaf88507.jpg!small)

## 关于SquarePhish

SquarePhish是一款高级网络钓鱼测试工具，该工具整合了OAuth设备码身份验证流和二维码技术实现其功能。

## 工具运行机制

首先，广大研究人员可以使用SquarePhish项目的email模块来向目标用户发送一个恶意二维码邮件，邮件中的默认文字为“需要更新其Microsoft
MFA身份验证才能继续使用移动电子邮件”，当前使用的客户端ID为Microsoft Authenticator App：

![](https://image.3001.net/images/20221222/1671721654_63a472b6a5c00dd0a724a.png!small)

通过首先发送二维码，我们可以避免提前启动仅持续15分钟的OAuth设备代码工作流。

接下来，目标用户将使用移动设备扫描电子邮件正文中的二维码。二维码会将目标用户引导到我们所控制的服务器（运行SquarePhish的服务器模块），并将URL参数设置为其电子邮件地址：

![](https://image.3001.net/images/20221222/1671721664_63a472c0b8c169b834acf.png!small)

当目标用户访问恶意的SquarePhish服务器时，会触发一个后台进程，该进程将启动OAuth设备代码验证流程，并向目标用户发送生成的设备代码，然后要求他们输入合法的Microsoft设备代码网站（这将启动OAauth设备代码流程15分钟计时器）。

![](https://image.3001.net/images/20221222/1671721672_63a472c8b706155bfd70b.png!small)

SquarePhish服务器将会继续在后台处理身份认证流程：

    
    
    [2022-04-08 14:31:51,962] [info] [minnow@square.phish] Polling for user authentication...
    
    [2022-04-08 14:31:57,185] [info] [minnow@square.phish] Polling for user authentication...
    
    [2022-04-08 14:32:02,372] [info] [minnow@square.phish] Polling for user authentication...
    
    [2022-04-08 14:32:07,516] [info] [minnow@square.phish] Polling for user authentication...
    
    [2022-04-08 14:32:12,847] [info] [minnow@square.phish] Polling for user authentication...
    
    [2022-04-08 14:32:17,993] [info] [minnow@square.phish] Polling for user authentication...
    
    [2022-04-08 14:32:23,169] [info] [minnow@square.phish] Polling for user authentication...
    
    [2022-04-08 14:32:28,492] [info] [minnow@square.phish] Polling for user authentication...

然后，目标用户将通过电子邮件中提供的链接或通过访问其移动设备上的SquarePhish URL重定向来访问Microsoft设备代码认证网站：

![](https://image.3001.net/images/20221222/1671721688_63a472d844c50b1d556e1.png!small)

接下来，目标用户将输入提供的设备代码，并将提示其点击同意：

![](https://image.3001.net/images/20221222/1671721695_63a472df3aa04fc1acd69.png!small)

目标用户完成身份验证并点击同意之后，身份验证令牌将保存在本地，并将通过请求应用程序的定义范围向目标用户提供访问：

    
    
    [2022-04-08 14:32:28,796] [info] [minnow@square.phish] Token info saved to minnow@square.phish.tokeninfo.json

范围定义如下：

    
    
    "scope": ".default offline_access profile openid"

## 工具下载

该工具基于Python开发，因此我们首先需要在本地设备上安装并配置好Python环境。接下来，可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/secureworks/squarephish.git

## 工具使用

### 电子邮件模块

向目标用户发送一个生成好的二维码，它将触发OAuth设备码身份验证流：

    
    
    usage: squish.py email [-h] [-c CONFIG] [--debug] [-e EMAIL]
    
     
    
    optional arguments:
    
      -h, --help            显示命令参数帮助信息和退出
    
     
    
      -c CONFIG, --config CONFIG
    
                          SquarePhish配置文件 [默认: settings.config]
    
     
    
      --debug             启用服务器调试
    
     
    
      -e EMAIL, --email EMAIL
    
                          发送初始二维码邮件的目标用户邮件地址

### 服务器模块

该模块负责托管一个二维码链接所指向的服务器：

    
    
    usage: squish.py server [-h] [-c CONFIG] [--debug]
    
     
    
    optional arguments:
    
      -h, --help            显示命令参数帮助信息和退出
    
     
    
      -c CONFIG, --config CONFIG
    
                          SquarePhish配置文件 [Default: settings.config]
    
     
    
      --debug            启用服务器调试

## 工具配置

    
    
    [DEFAULT]
    
    SMTP_PORT            = 465                                                                      # SMTP 端口, 默认为465
    
    SMTP_SERVER          = "smtp.gmail.com"                                                         # SMTP 服务器, 默认为GMail
    
    SMTP_PROTO           = "ssl"                                                                    # SMTP 协议: {ssl, tls, None (留空)}
    
    SMTP_EMAIL           = ""                                                                       # 提供认证邮件地址
    
    SMTP_PASSWORD        = ""                                                                       # 提供认证密码
    
     
    
    [EMAIL]
    
    SQUAREPHISH_SERVER   = ""                                                                       # 必填: SquarePhish服务器IP地址或域名
    
    SQUAREPHISH_PORT     = 8443                                                                     # SquarePhish服务器端口, 默认为8443 (this should match the below server value)
    
    SQUAREPHISH_ENDPOINT = "/mfa"                                                                   # 触发OAuth设备码验证流的SquarePhish端点, 默认为一个MFA 预留文字
    
    FROM_EMAIL           = "admin@square.phish"                                                     # 发送邮件时的默认发件地址
    
    SUBJECT              = "ACTION REQUIRED: Multi-Factor Authentication (MFA) Update"              # 发送邮件的默认主题，默认为MFA预留文字
    
    EMAIL_TEM***TE       = "pretexts/mfa/qrcode_email.html"                                         # 电子邮件Body模版
    
     
    
    [SERVER]
    
    PORT                 = 8443
    
    FROM_EMAIL           = "admin@square.phish"                                                     # 发送邮件时的默认发件地址
    
    SUBJECT              = "ACTION REQUIRED: Multi-Factor Authentication (MFA) Update"              # 发送邮件的默认主题，默认为MFA预留文字
    
    CLIENT_ID            = "4813382a-8fa7-425e-ab75-3b753aab3abb"                                   # 身份认证客户端ID, 默认为Microsoft Authenticator App
    
    ENDPOINT             = "/mfa"                                                                   # 用于触发OAuth设备码验证流的端点, 默认为MFA预留文字
    
    CERT_CRT             = ""                                                                       # 服务器SSL证书，.crt文件
    
    CERT_KEY             = ""                                                                       # 服务器SSL证书文件，.key文件
    
    EMAIL_TEM***TE       = "pretexts/mfa/devicecode_email.html"                                     # 电子邮件Body模版
    
    PERMISSION_SCOPE     = ".default offline_access profile openid"                                 # OAuth权限范围

### 自定义预留文字

如需修改邮件预留文字，可以在项目的[
_pretexts_](https://github.com/secureworks/squarephish/blob/main/pretexts)目录中进行修改。

## 许可证协议

本项目的开发与发布遵循[ _Apache_
_-2.0_](https://github.com/secureworks/squarephish/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **SquarePhish** ：【[ _GitHub传送门_](https://github.com/secureworks/squarephish)】

## 参考资料

> [ _https://docs.microsoft.com/en-us/azure/active-> directory/develop/v2-permissions-and-> consent﻿_](https://docs.microsoft.com/en-us/azure/active-> directory/develop/v2-permissions-and-consent)

