## 1.漏洞描述

该漏洞为远程命令执行漏洞，由于用友NC对外开放了BeanShell接口，攻击者可以在无需经过身份验证的情况下直接访问该接口，并构造恶意数据执行任意命令，攻击成功可获得目标服务器权限。

## 2.影响版本

    
    
    用友NC: 6.5
    

## 3.复现过程

在线环境

![1b3a7acde0b09c0564ebefdbca3441b](https://image.3001.net/images/20210716/1626421909_60f13a9507a694277b09f.png!small)

![image-20210716153042376](https://image.3001.net/images/20210716/1626421911_60f13a972e498373cae01.png!small)

无需登录，通过poc（验证性测试）URL访问测试接口

    
    
    /servlet/~ic/bsh.servlet.BshServlet
    

![image-20210716153154469](https://image.3001.net/images/20210716/1626421916_60f13a9cbfad0be518f34.png!small)

![image-20210716153613661](https://image.3001.net/images/20210716/1626421917_60f13a9d8b2b5c5ee1ddb.png!small)

这里本来想上线一下，进去看看，没想到是个国内的服务器，那可不刑呀，于是就此打住了。

## 4.修复方式

用友NC官方说明：该漏洞为第三方jar包漏洞导致，用友NC官方已于4月9日解决并验证，且已通过服务渠道推送了解决方案，授权用户可以访问下载链接进行下载。补丁下载地址：

http://umc.yonyou.com/ump/querypatchdetailedmng?PK=18981c7af483007db179a236016f594d37c01f22aa5f5d19

