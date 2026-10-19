**近日，微软官方发布了Windows远程代码执行漏洞（[CNNVD-201805-278](http://www.cnnvd.org.cn/web/xxk/ldxqById.tag?CNNVD=CNNVD-201805-278)、CVE-2018-8136）及Microsoft
Excel远程代码执行漏洞（[CNNVD-201805-273](http://www.cnnvd.org.cn/web/xxk/ldxqById.tag?CNNVD=CNNVD-201805-273)和[CNNVD-201805-272](http://www.cnnvd.org.cn/web/xxk/ldxqById.tag?CNNVD=CNNVD-201805-272)、
[CVE-2018-8147和CVE-2018-8148 ](http://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-5712)）的公告。成功利用Windows远程代码执行漏洞的攻击者，可以在目标系统上执行任意代码。Microsoft
Windows Server 2016、MicrosoftWindows Server 2012、Microsoft Windows Server
2008、Microsoft Windows 8.1、Microsoft Windows 7、Microsoft Windows
10等版本均受漏洞影响。**

成功利用MicrosoftExcel远程代码执行漏洞的攻击者，能在当前用户环境下执行任意代码，如果当前用户使用管理员权限登录，攻击者甚至可以完全控制该用户的系统。Microsoft
Excel 2010 Service Pack 2、MicrosoftExcel 2013 Service Pack 1、Microsoft Excel
2016、Microsoft Office 2010 Service Pack 2、MicrosoftOffice 2013 RT Service Pack
1、Microsoft Office 2013Service Pack 1、Microsoft Office 2016、Microsoft Office
Compatibility Service Pack
3等版本均受漏洞影响。目前，微软官方已经发布补丁修复了上述漏洞，建议用户及时确认是否受到漏洞影响，尽快采取修补措施。

## 一、漏洞介绍

Microsoft [Windows](https://baike.baidu.com/item/Microsoft%20Windows)是美国
[微软公司](https://baike.baidu.com/item/%E5%BE%AE%E8%BD%AF%E5%85%AC%E5%8F%B8)研发的一套采用了图形化模式的操作系统。Windows处理内存中对象的方式存在远程代码执行漏洞，攻击者可通过创建特制的文档利用该漏洞以提升的权限执行任意代码。

Microsoft Excel是美国微软公司为使用[Windows](https://baike.baidu.com/item/Windows)和
[AppleMacintosh](https://baike.baidu.com/item/Apple%20Macintosh)操作系统的电脑编写的一款[电子表格](https://baike.baidu.com/item/%E7%94%B5%E5%AD%90%E8%A1%A8%E6%A0%BC)
软件。Microsoft
Excel存在远程代码执行漏洞，该漏洞源于该软件未能正确处理内存中的对象，攻击者可通过向用户发送经过特殊构造的文件并诱使用户打开该文件，从而触发远程代码执行漏洞。

## 二、危害影响

Windows远程代码执行漏洞，攻击者可通过创建特制的文档利用该漏洞以提升的权限执行任意代码。该漏洞涉及了多个版本，Windows 10 Version
1607、Windows 10 Version1703、Windows 10 Version 1709、Windows10 Version
1803、Windows 7 Service Pack 1、Windows 8.1、Windows RT 8.1、 Windows Server 2008
Service Pack 2、WindowsServer 2008 R2 Service Pack 1、Windows Server
2012、Windows Server 2012 R2 、Windows Server 2016、Windows Server Version
1709、Windows ServerVersion 1803等版本均受漏洞影响。

Microsoft
Excel远程代码执行漏洞，攻击者可以远程执行代码，如果当前用户使用管理员权限登录，攻击者甚至可以完全控制该用户的系统，任意安装程序、更改或删除数据、创建管理员帐户等。该漏洞涉及了多个版本，Microsoft
Excel 2010 Service Pack 2、MicrosoftExcel 2013 Service Pack 1、Microsoft Excel
2016、Microsoft Office 2010 Service Pack 2、MicrosoftOffice 2013 RT Service Pack
1、Microsoft Office 2013Service Pack 1、Microsoft Office 2016、Microsoft Office
Compatibility Service Pack 3等版本均受该漏洞影响。

## 三、修复建议

目前，微软官方已经发布补丁修复了上述漏洞，建议用户及时确认是否受到漏洞影响，尽快采取修补措施。

微软官方链接地址如下：

|  漏洞名称  |  编号  |  补丁地址  
---|---|---|---  
1  |  Windows远程代码执行漏洞  |  CNNVD-201805-278、CVE-2018-8136  |
<https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-8136>  
2  |  Microsoft Excel远程代码执行漏洞  |  CNNVD-201805-273、CVE-2018-8147  |
<https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-8147>  
CNNVD-201805-272 、CVE-2018-8148  |  <https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-8148>______  
  
CNNVD将继续跟踪上述漏洞的相关情况，及时发布相关信息。如有需要，可与CNNVD联系（cnnvd@itsec.gov.cn）。

 ***本文作者：CNNVD，转载请注明来自 FreeBuf.COM**  

