大家好呀，我是一个刚入门的小萌新，今天要讲的是自己开发的一个信息收集小工具以及开发思路，话不多说，开始啦

## 确定开发语言

想要开发工具，当然需要使用一个趁手的语言，比如python，好吧我承认，我只会一点python，那么这个工具当然就是python写的啦

## 确定功能

所谓信息收集，当然必不可少的就是探测子域名，一般的话想在主域名上发现漏洞还是挺难滴，然后就是端口扫描，最后就是web指纹识别，其实是我只开发了这三个模块，tcl

## 工具主体结构

    
    
    ├── Controller
    │   ├── Controller.py
    │   ├── Start.py
    │   ├── __init__.py
    ├── Core
    │   ├── CheckURL.py
    │   ├── GetSubdomain.py
    │   ├── PortScan.py
    │   ├── __init__.py
    ├── IGScan.py
    ├── Output
    │   ├── fingerprint.txt
    │   ├── link.txt
    │   └── subdomain.txt
    ├── README.md
    ├── Script
    │   ├── UseCheckURL.py
    │   ├── UseGetSubdomain.py
    │   ├── UsePortScan.py
    │   ├── UseWebAnaylzer.py
    │   ├── __init__.py
    ├── Utils
    │   ├── rules
    │   ├── Webanaylzer.py
    │   ├── __init__.py
    └── requirements.txt

我就不介绍我为什么要这样分类了，因为我自己也不知道，hh那么开始介绍工具是怎样运行的吧

## 工具运作流程

[链接在这里](https://github.com/ro4lsc/IGScan)  
运行IGScan.py，将会调用Controller->Start.py->Controller.py进而调用各个模块

模块介绍  
\- subdomain模块(子域名收集)  
\- checkurl模块(判断URL是否存活)  
\- webanalyzer模块(web指纹收集)

模块实现

subdomain

subdomain模块是写了两个py的，分别是GetSubdomain.py和UseGetSubdomain.py

Core/Getsubdomain.py

这里我从[国光](https://www.sqlsec.com/2020/05/webscan.html)大佬的文章中得知了六个子域名接口，然后做好对应的数据提取

    
    
    # 爱站
    https://baidurank.aizhan.com/baidu/{domain}/
    
    # 百度云观测
    http://ce.baidu.com/index/getRelatedSites?site_address={domain}
    
    # hackertarget
    https://api.hackertarget.com/hostsearch/?q={domain}
    
    # IP138
    https://site.ip138.com/{domain}/domain.htm
    
    # crt.sh SSL 证书反查
    https://crt.sh/?q=%25.{domain}  
      
    # 千寻  
    url = 'https://www.dnsscan.cn/dns.html'  
    datas = {"ecmsfrom": '8.8.8.8', "show": 'none', "keywords": domain}

由于使用了多线程，速度还是蛮快的，1000个域名大概只需要20-30分钟

Script/UseGetSubdomain.py  
批量-f参数和单个url
-u参数对应不同的实现方法,批量的话还是使用多线程提升性能，如文件名所示也就是使用GetSubdomain模块，结果将会放到`Output/subdomain.txt`

checkurl

Core/CheckURL.py

这个模块主要作用是探测子域名是否可以访问80，443。可以访问的话就放入文件`Output/link.txt`  
具体实现的话还是使用requests库对(http://|https://)+url,当然由于性能原因还是使用多线程，后续打算使用异步(asyncio)，正在学习ing，速度的话还是比较快的11w子域名，大概需要20-30分钟，主要是开了50个线程的原因，hhh

Script/UseCheckURL.py

仅仅只是调用CheckURL.py，其实是为了美观

