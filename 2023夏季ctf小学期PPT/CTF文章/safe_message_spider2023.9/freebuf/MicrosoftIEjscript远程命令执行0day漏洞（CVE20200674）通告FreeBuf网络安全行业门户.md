## 文档信息

编号  |  QianxinTI-SV-2020-0002  
---|---  
关键字  |  IE jscript.dll CVE-2020-0674  
创建日期  |  2020年01月19日  
更新日期  |  2020年01月19日  
TLP  |  WHITE  
分析团队  |  奇安信威胁情报中心红雨滴团队  
  
## 通告背景

2020年1月17日，在微软的每月的例行补丁日两天之后，发布了编号为ADV200001的例行外安全公告，该公告的披露涉及一个野外发现的0day漏洞CVE-2020-0674，被用于执行小范围针对性的攻击。目前还未有相应的针对此漏洞的补丁，微软方面正在积极修复，可能在2月的例行补丁包中修复此漏洞。

奇安信威胁情报中心红雨滴团队第一时间跟进了该漏洞，基于所得到的技术细节，该漏洞是微软IE浏览器的JavaScript组件中的一处内存破坏漏洞，成功利用将使攻击者以当前用户的上下文执行任意代码。受影响的用户，如果使用存在漏洞的IE浏览器访问植入恶意内容的网面可能导致机器被控制，在漏洞补修复之前强烈建议用户按本通告给出的临时缓解措施处理以减轻被攻击的风险。

## 漏洞概要

![图片.png](https://image.3001.net/images/20200121/1579577056_5e266ee02207e.png!small)

受影响列表

产品  |  平台  
---|---  
Internet Explorer 10  |  Windows Server 2012  
Internet Explorer 11  |  Windows 10 Version 1803 for 32-bit Systems  
Internet Explorer 11  |  Windows 10 Version 1803 for x64-based Systems  
Internet Explorer 11  |  Windows 10 Version 1803 for ARM64-based Systems  
Internet Explorer 11  |  Windows 10 Version 1809 for 32-bit Systems  
Internet Explorer 11  |  Windows 10 Version 1809 for x64-based Systems  
Internet Explorer 11  |  Windows 10 Version 1809 for ARM64-based Systems  
Internet Explorer 11  |  Windows Server 2019  
Internet Explorer 11  |  Windows 10 Version 1909 for 32-bit Systems  
Internet Explorer 11  |  Windows 10 Version 1909 for x64-based Systems  
Internet Explorer 11  |  Windows 10 Version 1909 for ARM64-based Systems  
Internet Explorer 11  |  Windows 10 Version 1709 for 32-bit Systems  
Internet Explorer 11  |  Windows 10 Version 1709 for x64-based Systems  
Internet Explorer 11  |  Windows 10 Version 1709 for ARM64-based Systems  
Internet Explorer 11  |  Windows 10 Version 1903 for 32-bit Systems  
Internet Explorer 11  |  Windows 10 Version 1903 for x64-based Systems  
Internet Explorer 11  |  Windows 10 Version 1903 for ARM64-based Systems  
Internet Explorer 11  |  Windows 10 for 32-bit Systems  
Internet Explorer 11  |  Windows 10 for x64-based Systems  
Internet Explorer 11  |  Windows 10 Version 1607 for 32-bit Systems  
Internet Explorer 11  |  Windows 10 Version 1607 for x64-based Systems  
Internet Explorer 11  |  Windows Server 2016  
Internet Explorer 11  |  Windows 7 for 32-bit Systems Service Pack 1  
Internet Explorer 11  |  Windows 7 for x64-based Systems Service Pack 1  
Internet Explorer 11  |  Windows 8.1 for 32-bit systems  
Internet Explorer 11  |  Windows 8.1 for x64-based systems  
Internet Explorer 11  |  Windows RT 8.1  
Internet Explorer 11  |  Windows Server 2008 R2 for x64-based Systems Service
Pack 1  
Internet Explorer 11  |  Windows Server 2012  
Internet Explorer 11  |  Windows Server 2012 R2  
Internet Explorer 9  |  Windows Server 2008 for 32-bit Systems Service Pack 2  
Internet Explorer 9  |  Windows Server 2008 for x64-based Systems Service Pack
2  
  
## 漏洞描述

该漏洞是微软IE浏览器存在于JavaScript组件中的一处内存破坏漏洞，技术细节不详述。

## 影响面评估

有数据显示IE在国内的市场占有率在3%左右：

![图片.png](https://image.3001.net/images/20200121/1579577119_5e266f1f2d06d.png!small)参考来源：<https://gs.statcounter.com/browser-market-share#monthly-201806-201906-bar>

  

从目前来看该漏洞仅在有限的定向攻击中被使用。总体评估有一定的影响面，政企客户需要重点关注。

## 处置建议

### 临时处置措施

1\.
目前软件厂商微软正在积极修复该漏洞，尚无可使用的安全补丁，可以通过以下的方式限制对漏洞模块jscript.dll的访问，从而避免相关的攻击，但是这一操作有可能会导致网站部分使用到该模块的功能缺失。

32位系统下，通过以下命令限制对jscript.dll的访问

64位系统下，通过以下命令限制对jscript.dll的访问

通过以下命令撤销以上的操作

32位

64位

2\.
IE浏览器已经被微软放弃，建议用户转用较为安全的浏览器比如Chrome。而且，根据目前收到的反馈微软对此漏洞不会发布已经停服的Win7操作系统上的补丁，强烈建议用户升级操作系统到Win10以上。

3\. 奇安信终端安全产品天擎已经加入了针对此漏洞检测和阻断，创新性的天狗安全防护软件无需补丁和规则升级就能防护此漏洞，强烈建议用户安装使用。

## 参考资料

<https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/ADV200001>

