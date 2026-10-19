## 文档信息

编号  |  QianxinTI-SV-2020-0001  
---|---  
关键字  |  CRYPT32.DLL cryptographic CVE-2020-0601  
发布日期  |  2020年01月15日  
更新日期  |  2020年01月15日  
TLP  |  WHITE  
分析团队  |  奇安信威胁情报中心红雨滴团队  
  
## 通告背景

2020
年1月15日，微软例行公布了1月的补丁更新列表，在其中存在一个位于CryptoAPI.dll椭圆曲线密码(ECC)证书检测绕过相关的漏洞，同时紧随其后的是美国NSA发布的相关漏洞预警通告，其中通告显示，该漏洞为NSA独立发现，并汇报给微软。这对于专门挖掘微软漏洞进行利用(例如“永恒之蓝”系列)的NSA来说，实属罕见。

攻击者可以通过构造恶意的签名证书，并以此签名恶意文件来进行攻击，此外由于ECC证书还广泛的应用于通信加密中，攻击者成功利用该漏洞可以实现对应的中间人攻击。

![图片.png](https://image.3001.net/images/20200115/1579068373_5e1eabd5c21d9.png!small)

  

奇安信威胁情报中心红雨滴团队第一时间跟进了该漏洞，值得注意的是指定参数的ECC密钥证书的Windows版本会受到影响，而这一机制，最早由WIN10引入，影响WIN10，Windows
Server2016/2019版本，而于今年1月14日停止安全维护的WIN7/Windows Server
2008由于不支持带参数的ECC密钥，因此不受相关影响。

## 漏洞概要

![图片.png](https://image.3001.net/images/20200115/1579068433_5e1eac1156a98.png!small)

## 漏洞描述

该漏洞存在于CryptoAPI.dll，可用于绕过椭圆曲线密码(ECC)证书检测。

## 影响面评估

奇安信威胁情报中心红雨滴团队第一时间跟进了该漏洞，值得注意的是指定参数的ECC密钥证书的Windows版本会受到影响，而这一机制，最早由WIN10引入，影响WIN10，Windows
Server 2016/2019版本，而于今年1月14日停止安全维护的WIN7/Windows Server
2008由于不支持带参数的ECC密钥，因此不受相关影响，但中心仍然建议用户将WIN7/ Windows
Server2008系统更新至最新的WIN10系统或Windows Server 2016之后的版本，并更新相关安全补丁。

## 处置建议

### 修复方法

1\. 目前软件厂商微软已经发布了漏洞相应的补丁，奇安信威胁情报中心建议进行相关升级

<https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2020-0601>

## 参考资料

<https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2020-0601>

<https://msrc-blog.microsoft.com/2020/01/14/january-2020-security-updates-cve-2020-0601/>

<https://media.defense.gov/2020/Jan/14/2002234275/-1/-1/0/CSA-WINDOWS-10-CRYPT-LIB-20190114.PDF>

