***严正声明：本文仅限于技术讨论与分享，严禁用于非法途径。**

一个月没发文章了实在太忙了，不过学习还是不能落下的，最近要做几个CS客户端的站，需要在终端装个内网安全管理，wireshark就用不了了，只能Proxifier抓下HTTP包了。

在工作中，很多渗透测试人员无法开展c/s型客户端型应用系统的渗透测试，原因是很难截取客户端访问数据，因而无法借助工具或人工的方式进行漏洞检测，依靠`Proxifier`还是可以截取到部分`HTTP`数据包从而进行测试的。  
突然想起来自己两年前在博客园写的一篇文章了，我觉得写的还不错，给大家拉出来看看。  
<https://www.cnblogs.com/xiaoyunxiaogang/p/10939485.html>

 **工具** :Proxifier+BURP  
之前一直用的Proxifier3.0破解版  
今天官网一看已经更新到4.05了  
 **1、官方下载地址（需要挂代理需要付费）：http://proxifier.com/**

 **2、百度网盘（3.0中文版）：文末公众号回复Proxifier**

## 一、配置代理服务器

###  **1）Proxifier 配置代理服务器**

![1622450193_60b4a01165d837c0828f8.png!small?1622450193094](https://image.3001.net/images/20210531/1622450193_60b4a01165d837c0828f8.png!small?1622450193094)

###  **2）burp配置代理**

![1622450226_60b4a0326cae4e36238a2.png!small?1622450225966](https://image.3001.net/images/20210531/1622450226_60b4a0326cae4e36238a2.png!small?1622450225966)
**3）配置代理规则**

这里先拿google浏览器试试手  
![1622450252_60b4a04ca9585c138ff3f.png!small?1622450252284](https://image.3001.net/images/20210531/1622450252_60b4a04ca9585c138ff3f.png!small?1622450252284)

## 二、抓包

###  **1、选择chrome.exe抓包**

配置代理服务器  
![1622450287_60b4a06f9a0afff50fcdb.png!small?1622450287114](https://image.3001.net/images/20210531/1622450287_60b4a06f9a0afff50fcdb.png!small?1622450287114)

![1622450310_60b4a086e7dafde40b2d2.png!small?1622450310377](https://image.3001.net/images/20210531/1622450310_60b4a086e7dafde40b2d2.png!small?1622450310377)

点击确定

成功抓取到google浏览器的包  
![1622450347_60b4a0ab10c016b1edbda.png!small?1622450347313](https://image.3001.net/images/20210531/1622450347_60b4a0ab10c016b1edbda.png!small?1622450347313)

###  **2、然后试一下QQ**

只能抓到HTTP协议的包  
![1622450410_60b4a0eaa12bc34353301.png!small?1622450410052](https://image.3001.net/images/20210531/1622450410_60b4a0eaa12bc34353301.png!small?1622450410052)![1622450385_60b4a0d189e6758696c01.png!small?1622450386836](https://image.3001.net/images/20210531/1622450385_60b4a0d189e6758696c01.png!small?1622450386836)

## 三、Proxifier+reGeorg构建HTTP隧道代理

 **直接搬一篇我的博客园了**  
reGeorg的前身是2008年SensePost在BlackHat USA 2008 的 reDuh延伸与扩展。也是目
前安全从业人员使用最多，范围最广，支持多丰富的一款http隧道。从本质上讲，可以将
JSP/PHP/ASP/ASPX等页面上传到目标服务器，便可以访问该服务器后面的主机。

    
    
    攻击机： 192.168.31.102  kali
    
    192.168.31.96    win 10
    
    靶机： 192.168.31.106  Windows 2003
    
    
    
    下载：
    
    https://github.com/sensepost/reGeorg
    
     安装：
    
    git clone https://github.com/sensepost/reGeorg.git
    
    ls
    
    python reGeorgSocksProxy.py ‐h
    

![1622450436_60b4a1044e7fd5f0f5cbd.png!small?1622450436449](https://image.3001.net/images/20210531/1622450436_60b4a1044e7fd5f0f5cbd.png!small?1622450436449)

PS:这个程序需要安装PIP urllib3 我的已经装了

如果没有安装的话执行命令：

    
    
    pip install urllib3
    

安装完成后把reGeorg 下的tunnel上传到目标靶机

![在这里插入图片描述](https://image.3001.net/images/20210531/1622450019_60b49f63016330b37e24a.png!small)![在这里插入图片描述](https://image.3001.net/images/20210531/1622450019_60b49f638ad0adc4816e7.png!small)

目标靶机是开了防火墙的我们访问是访问3389是不通的  
![1622450462_60b4a11e3e75e829ad662.png!small?1622450462020](https://image.3001.net/images/20210531/1622450462_60b4a11e3e75e829ad662.png!small?1622450462020)

 **接下来配置代理**

Kali攻击机执行

    
    
    python reGeorgSocksProxy.py -u "http://192.168.31.106/include/config/tunnel.aspx"  -p 8080 -l 0.0.0.0
    

þ 这里我们来讲讲0.0.0.0，如果我们直接ping
0.0.0.0是不行的，他在IPV4中表示的是无效的目标地址，但是在服务器端它表示本机上的所有IPV4地址，如果一个服务有多个IP地址（192.168.1.2和10.1.1.12），那么我们如果设置的监听地址是0.0.0.0那么我们无论是通过IP192.168.1.2还是10.1.1.12都是可以访问该服务的。在路由中，0.0.0.0表示的是默认路由，即当路由表中没有找到完全匹配的路由的时候所对应的路由。

![在这里插入图片描述](https://image.3001.net/images/20210531/1622450020_60b49f643f2ac36e467b5.png!small)

这时候再操作Proxifier

Windows10下配合Proxifier：

![1622450488_60b4a1382bc9082dcd1f7.png!small?1622450487689](https://image.3001.net/images/20210531/1622450488_60b4a1382bc9082dcd1f7.png!small?1622450487689)![1622450507_60b4a14bcee86a91ae49f.png!small?1622450507756](https://image.3001.net/images/20210531/1622450507_60b4a14bcee86a91ae49f.png!small?1622450507756)

连接3389  
![1622450527_60b4a15f43430dae99ebd.png!small?1622450526863](https://image.3001.net/images/20210531/1622450527_60b4a15f43430dae99ebd.png!small?1622450526863)

下边是我的微信公众号：公众号回复Proxifier获取3.0版本  
![在这里插入图片描述](https://image.3001.net/images/20210531/1622450022_60b49f668bb10e0f97a16.png!small)

