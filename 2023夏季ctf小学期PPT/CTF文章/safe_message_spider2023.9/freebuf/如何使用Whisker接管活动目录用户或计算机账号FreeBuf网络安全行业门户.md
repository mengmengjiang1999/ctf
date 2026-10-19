![](https://image.3001.net/images/20210828/1630148506_612a179a1cec811a1bfb8.jpg!small)

## 关于Whisker

Whisker是一款基于C#开发的工具，可以通过篡改目标账号的msDS-KeyCredentialLink或添加“Shadow
Credentials”来实现活动目录用户或计算机账号的接管。

该工具主要基于[
_DSInternals_](https://github.com/MichaelGrafnetter/DSInternals)项目代码实现其功能。

为了保证攻击能够成功，环境必须为运行了最新版本Windows Server 2016的域控制器，而且域控制器必须拥有一个服务器认证证书以支持PKINIT
Kerberos认证。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地，并进行代码构建：

    
    
    git clone https://github.com/eladshamir/Whisker.git

## 工具使用

### 向目标对象的msDS-KeyCredentialLink属性添加一个新的值

> /target:<samAccountName>：必须。设置目标名称，计算机对象必须以“$”结尾。
>
> /domain:<FQDN>：可选。设置目标全限定域名（FQDN），如果不提供该值，工具将会尝试解析当前用户的FQDN。
>
> /dc:<IP/HOSTNAME>：可选。设置目标域控制器（DC），如果不提供该值，工具将会尝试攻击主域控制器（PDC）。
>
> /path:<PATH>：可选。设置存储生成的自签名证书的路径，如果不提供该值，证书将会以Base64格式打印。
>
> /password:<PASWORD>：可选。设置已存储自签名证书的密码，如果不提供该值，将会生成随机密码。

 **使用样例：**

    
    
    Whisker.exe add /target:computername$ /domain:constoso.local /dc:dc1.contoso.local /path:C:\path\to\file.pfx /password:P@ssword1

### 从目标对象的msDS-KeyCredentialLink属性移除一个值

> /target:<samAccountName>：必须。设置目标名称，计算机对象必须以“$”结尾。
>
> /deviceID:<GUID>: 必须。设置目标对象msDS-> KeyCredentialLink属性待移除值的DeviceID，必须是一个有效的GUID。
>
> /domain:<FQDN>: 可选。设置目标全限定域名（FQDN），如果不提供该值，工具将会尝试解析当前用户的FQDN。
>
> /dc:<IP/HOSTNAME>：可选。设置目标域控制器（DC），如果不提供该值，工具将会尝试攻击主域控制器（PDC）。

 **使用样例：**

    
    
    Whisker.exe remove /target:computername$ /domain:constoso.local /dc:dc1.contoso.local /remove:2de4643a-2e0b-438f-a99d-5cb058b3254b

### 清除目标对象msDS-KeyCredentialLink属性的所有值

> /target:<samAccountName>：必须。设置目标名称，计算机对象必须以“$”结尾。
>
> /domain:<FQDN>：可选。设置目标全限定域名（FQDN），如果不提供该值，工具将会尝试解析当前用户的FQDN。
>
> /dc:<IP/HOSTNAME>：可选。设置目标域控制器（DC），如果不提供该值，工具将会尝试攻击主域控制器（PDC）。

 **使用样例：**

    
    
    Whisker.exe clear /target:computername$ /domain:constoso.local /dc:dc1.contoso.local

### 输出目标对象msDS-KeyCredentialLink属性的所有值

> /target:<samAccountName>：必须。设置目标名称，计算机对象必须以“$”结尾。
>
> /domain:<FQDN>：可选。设置目标全限定域名（FQDN），如果不提供该值，工具将会尝试解析当前用户的FQDN。
>
> /dc:<IP/HOSTNAME>：可选。设置目标域控制器（DC），如果不提供该值，工具将会尝试攻击主域控制器（PDC）。

 **使用样例：**

    
    
    Whisker.exe list /target:computername$ /domain:constoso.local /dc:dc1.contoso.local

## 项目地址

 **Whisker：** 【[ _GitHub传送门_](https://github.com/eladshamir/Whisker)】

## 参考资料

> [ _https://posts.specterops.io/shadow-credentials-abusing-key-trust-account-> mapping-for-takeover-8ee1a53566ab_](https://posts.specterops.io/shadow-> credentials-abusing-key-trust-account-mapping-for-takeover-8ee1a53566ab)
>
> [
> _https://github.com/MichaelGrafnetter/DSInternals﻿_](https://github.com/MichaelGrafnetter/DSInternals)

