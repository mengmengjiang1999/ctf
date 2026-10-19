## 背景

在一次实战演练中 **goby扫描到一个sharepoint的getshell漏洞**
，漏洞cve编号为CVE-2019-0604，本想着一把梭，直接渗透内网，没想到有waf之类的防护，最后还是想办法解决了。

现在网络上各类漏洞利用工具很多，每天都有新的漏洞出来，也不是每个漏洞我们都详细的研究复现过，这些工具的payload大多数都是固定的，如果遇到waf之类的防护就很不爽了，在实战演练中时间紧任务重比的就是手速，重新去搭建相关程序的环境复现就太耽误时间了，其实可以借助抓包提取这类工具的payload，自己再编码进行绕过。

## 实战演练

我这次遇到的程序是微软的知名程序 **SharePoint**
，SharePoint是微软面向企业市场推的一个集成化平台，可以帮助企业集中管理数据、文档、流程，并和其他企业业务系统进行集成。

未更新版本的Microsoft SharePoint
存在远程代码执行漏洞（CVE-2019-0594、CVE-2019-0604，高危），攻击者可在SharePoint应用程序池和SharePoint服务器中执行任意代码。

  *  **影响版本：**

Microsoft SharePoint Enterprise Server 2016

SharePoint Foundation 2013 SP1

harePoint Server 2010 SP2

SharePoint Server 2019。

  *  **攻击入口url：**

/_layouts/15/Picker.aspx

回到正题，扫描器提示如下：

![](https://image.3001.net/images/20220728/1658995320_62e24278a9732b4ec83bc.png!small)

这里我直接利用 **goby exploit进行getshell** ，可以看到提示文件写入成功，如下图：

![](https://image.3001.net/images/20220728/1658995456_62e2430016d76103105f5.png!small)

这里写入的shell为菜刀默认的一句话webshell，webshell工具连接失败，服务器端有不知名的waf，这里我想通过修改goby的插件代码上传哥斯拉或者冰蝎webshell来绕过waf，但是goby封装的插件我也改不了也看不到代码。

在网上找到了k8gege的python exploit但是运行也直接报错了，hw过程中也没有时间来具体分析报错原因。这里我只需要知道
**发送的exp数据包** 即可，直接打开wireshark，在goby中点击验证抓取goby数据包：

![](https://image.3001.net/images/20220728/1658995549_62e2435d8f6e6739396dd.png!small)

直接找到写入shell的http数据包：

![](https://image.3001.net/images/20220728/1658995617_62e243a1038cd7d0cd8cb.png!small)

 **选择fllow- >http stream。**

![](https://image.3001.net/images/20220728/1658995896_62e244b80863a9d1157bc.png!small)

 **拷贝数据包到burpsuite发包** ，如下图，页面虽然报错但是这里有 **返回长度264** 其实就表示成功：

![](https://image.3001.net/images/20220728/1658996031_62e2453fb7181e7760088.png!small)

这里面的加密数据怎么修改呢？

在这里提供个编码工具，具体分析写入payload加密方式：

https://github.com/boxhg/CVE-2019-0604/releases/download/1.0/CVE20190604-Payload.7z

其实就是将如下的xml加密后进行提交，这里直接修改shell内容再加密回去即可。

![](https://image.3001.net/images/20220728/1658996110_62e2458e9e261df565bb8.png!small)

> 小提示：这里需要注意xml里面出现<会报错要用html实体转码一下。

工具的使用很简单直接转码即可，如下：

![](https://image.3001.net/images/20220728/1658996896_62e248a0de3de8378ae8c.png!small)

服务器有waf 这些语句写进去后 shell 还是连接不上。在这里不断的尝试写shell，期间也遇到一些问题，<> %
写不进去的，一旦出现上传上去的页面就是空白。

  

这里有人会说都能执行命令了为何不直接下载cs木马执行，当时这个机器是不出网的，终究还是要写文件。后来想到思路是:利用windows系统自带的certutil写入转码后的代码（不会出现特殊符号，可以写入复杂的webshell），再利用certutil在服务器上进行解码生成正常的webshell即可。

  

 **命令如下** ：certutil -encode aaa.aspx encode.aspx （本地编码）

先将加密后代码写入服务器，如下图访问正常：

![](https://image.3001.net/images/20220728/1658997725_62e24bdd47e5388264a21.png!small)将如下代码编码后发包到服务器端再执行：

    
    
    cmd /c certutil -decode "%CommonProgramFiles%\\Microsoft Shared\\Web Server Extensions\\15\\TEMP.LATE\\LAYOUTS\\ua999.aspx"
     "%CommonProgramFiles%\\Microsoft Shared\\Web Server Extensions\\15\\TEMP.L ATE\\LAYOUTS\\ua7771.aspx"

访问获取命令执行webshell：

![](https://image.3001.net/images/20220728/1658998240_62e24de0e4c8d12e9fe24.png!small)

后续用同样的方式写入其他变形类的webshell进行了内网渗透。

  

