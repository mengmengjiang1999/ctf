  
用户帐户控制(UAC)是Windows安全的关键部分。UAC通过限制恶意代码以管理员权限执行的能力来降低恶意软件的风险。该漏洞成因为UAC机制设定不严谨导致，利用该漏洞，攻击者通过运行特定程序，可以利用Windows
UAC窗口，提升至SYSTEM权限。

## Part1 漏洞状态

漏洞细节| 漏洞POC| 漏洞EXP| 在野利用  
---|---|---|---  
有| 有| 有| 有  
  
## Part2 漏洞描述

‍漏洞名称|

Windows UAC本地权限提升漏洞  
  
---|---  
CVE编号| CVE-2019-1388  
漏洞类型| 本地权限提升  
漏洞等级| 7.8 高危 (High）  
公开状态| 公开  
漏洞描述|

因UAC机制设定不严谨，导致攻击者可通过特定程序，利用UAC窗口，提升至SYSTEM权限。  
  
时间线|

2019-11-21 NVD发布

2019-11-12漏洞被修复  
  
受影响版本|

未安装补丁的:

Windows 7

Windows 8.1

Windows 10

Windows server 2008

Windows server 2012

Windows server 2016

Windows server 2019  
  
###  **分析环境:**

Win 7 6.1.7601 SP1

## Part3 漏洞复现

使用普通用户登录系统，运行特殊程序，会弹出UAC窗口，需要输入管理员密码，进行管理员身份验证。

![图片](https://image.3001.net/images/20230710/1688953957_64ab646529b121cb85c57.png!small)

![图片](https://image.3001.net/images/20230710/1688953968_64ab6470d8231fa82d18e.png!small)

点击”显示详细信息”，会出现”显示有关此发布者的证书信息”，点击此链接。

![图片](https://image.3001.net/images/20230710/1688953979_64ab647ba685bde90c701.png!small)

点击”颁发者”处超链接。

![图片](https://image.3001.net/images/20230710/1688953989_64ab64851288fd95a489f.png!small)在打开的ie浏览器中，点击另存为。![图片](https://image.3001.net/images/20230710/1688953997_64ab648dc2b543a02e87d.png!small)在打开的对话框中，进入system32目录，运行cmd，即可获取system权限，提权成功。

![图片](https://image.3001.net/images/20230710/1688954006_64ab6496acad1894478f1.png!small)

## Part4 漏洞分析

证书对话框内定义了一个OID，值为1.3.6.1.4.1.311.2.1.10，在证书信息页面里，会显示SpcSpAgencyInfo。

![图片](https://image.3001.net/images/20230710/1688954015_64ab649fd2ee05fedcd06.png!small)

证书页面会对其解析，如果该值数据格式正确，便会在证书页面显示该超链接，导致攻击者有机会打开ie浏览器。

![图片](https://image.3001.net/images/20230710/1688954031_64ab64af0e7198ede3f77.png!small)

只要我们选择符合条件的程序，在运行程序出现UAC认证窗口后，通过以上操作，ie浏览器会被consent.exe启动，权限为system。

![图片](https://image.3001.net/images/20230710/1688954040_64ab64b81eecffd4c0a6b.png!small)

![图片](https://image.3001.net/images/20230710/1688954050_64ab64c2f2ee7c3a2c2ca.png!small)

## Part5 修复建议

根据微软建议安装相应补丁https://msrc.microsoft.com/update-guide/en-US/vulnerability/CVE-2019-1388

