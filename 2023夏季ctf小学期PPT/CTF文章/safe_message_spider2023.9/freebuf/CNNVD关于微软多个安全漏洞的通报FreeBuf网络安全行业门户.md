***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **近日，微软官方发布了多个安全漏洞的公告，包括Microsoft
Windows权限提升漏洞（CNNVD-201901-176、CVE-2019-0543）、Windows内核信息泄漏漏洞（CNNVD-201901-137、CVE-2019-0536）、Microsoft
Word远程代码执行漏洞（CNNVD-201901-147、CVE-2019-0585）等多个漏洞。成功利用上述漏洞的攻击者可以在目标系统上执行任意代码。微软多个产品和系统受漏洞影响。**

目前，微软官方已经发布漏洞修复补丁，建议用户及时确认是否受到漏洞影响，采取修补措施。  

## **一、漏洞介绍**

本次漏洞公告涉及Microsoft Windows系统 、Microsoft Office、Microsoft Word、Microsoft Outlook
、Windows Jet数据库、Chakra脚本引擎、Windows Hyper-V 、Windows
DHCP客户端等Windows平台下应用软件和组件。漏洞详情如下：

### 1.Microsoft Windows权限提升漏洞（CNNVD-201901-176、 CVE-2019-0543）

 **漏洞简介：**
当Windows内核无法正确处理内存中的对象时，可能就会触发该漏洞。攻击者首先必须登录到系统。然后运行一个经特殊设计的应用程序，才能利用此漏洞。成功利用漏洞的攻击者可以在内核模式中运行任意代码。攻击者可任意安装程序、查看、更改或删除数据、或者创建新帐户等。

### 2.Windows内核信息泄漏漏洞（CNNVD-201901-137、CVE-2019-0536）

 **漏洞简介：**
当Windows内核不正确地处理内存中的对象时会触发该漏洞。成功利用此漏洞的攻击者可以获取内核信息，从而进一步入侵用户系统。已经过身份验证的攻击者可以通过运行经特殊设计的应用程序来利用此漏洞。

### 3.Microsoft Word远程代码执行漏洞（CNNVD-201901-147、 CVE-2019-0585）

 **漏洞简介：** 当Microsoft Word软件无法正确处理内存中的对象时，就会触发该漏洞。攻击者必须诱使用户使用Microsoft
Word打开经特殊设计的文件，才能利用此漏洞。成功利用此漏洞的攻击者可以在当前用户权限下执行恶意代码。

### 4.Microsoft Word信息泄漏漏洞（CNNVD-201901-159、CVE-2019-0561）

 **漏洞简介：** 当未正确使用Microsoft Word宏按钮时，存在信息泄漏漏洞。成功利用此漏洞的攻击者可以从目标系统中读取任意文件。

### 5.Microsoft Office信息泄漏漏洞（CNNVD-201901-160、CVE-2019-0560）

 **漏洞简介：** 当Microsoft
Office不正确地处理内存中的数据时，存在信息泄漏漏洞。攻击者通过设计一个特殊构造的文档诱使用户将其打开，从而获取用户计算机中存储的数据。

### 6.Microsoft Outlook信息泄漏漏洞（CNNVD-201901-161 、CVE-2019-0559）

 **漏洞简介：** 当Microsoft
Outlook不正确地处理特定类型的邮件时，存在信息泄漏漏洞。成功利用此漏洞的攻击者可能会收集用户相关的信息。攻击者通过向用户发送经特殊设计的电子邮件来利用此漏洞，最终获得用户信息。

### 7.Windows Jet数据库引擎远程代码执行漏洞（CNNVD-201901-179、CVE-2019-0538）

 **漏洞简介：** 当Windows
Jet数据库引擎不正确地处理内存中的对象时，会触发远程代码执行漏洞。攻击者可以通过诱使用户打开经特殊设计的文件来利用此漏洞。成功利用此漏洞的攻击者可以在用户系统上执行任意代码。

###
8.Chakra脚本引擎安全漏洞（CNNVD-201901-178、CVE-2019-0539）、（CNNVD-201901-154、CVE-2019-0567）、（CNNVD-201901-153、CVE-2019-0568）

 **漏洞简介：** Chakra脚本引擎在Microsoft
Edge中处理内存中的对象的时可能触发该漏洞。成功利用该漏洞的攻击者可以获得与当前用户相同的用户权限。如果当前用户使用管理权限登录，攻击者便可以任意安装程序、查看、更改或删除数据。

### 9.Windows DHCP客户端远程代码执行漏洞（CNNVD-201901-173、CVE-2019-0547）

 **漏洞简介：** 当攻击者向Windows
DHCP客户端发送经特殊设计的DHCP响应时，会触发该漏洞。成功利用此漏洞的攻击者可以在客户端计算机上运行任意代码。

### 10.Windows Hyper-V远程代码执行漏洞（CNNVD-201901-170、CVE-2019-0550）

 **漏洞简介：** 当服务器上的Windows Hyper-V无法正确验证用户操作系统上经身份验证的用户的输入时，会触发该漏洞。成功利用此漏洞的攻击者可以执行任意代码。

##  **二、** **修复建议**

目前，微软官方已经发布补丁修复了上述漏洞，建议用户及时确认漏洞影响，尽快采取修补措施。微软官方链接地址如下：

序号 | 漏洞名称 | 官方链接  
---|---|---  
1 | Microsoft Windows权限提升漏洞（CNNVD-201901-176、CVE-2019-0543） |
<https://portal.msrc.microsoft.com/zh-CN/security-guidance/advisory/CVE-2019-0543>  
2 | Windows内核信息泄漏漏洞（CNNVD-201901-137、CVE-2019-0536） |
<https://portal.msrc.microsoft.com/zh-CN/security-guidance/advisory/CVE-2019-0536>  
3 | Microsoft Word远程代码执行漏洞（CNNVD-201901-147、CVE-2019-0585） |
<https://portal.msrc.microsoft.com/zh-CN/security-guidance/advisory/CVE-2019-0585>  
4 | Microsoft Word信息泄漏漏洞（CNNVD-201901-159、CVE-2019-0561） |
<https://portal.msrc.microsoft.com/zh-CN/security-guidance/advisory/CVE-2019-0561>  
5 | Microsoft Office信息泄漏漏洞（CNNVD-201901-160、CVE-2019-0560） |
<https://portal.msrc.microsoft.com/zh-CN/security-guidance/advisory/CVE-2019-0560>  
6 | Microsoft Outlook信息泄漏漏洞（CNNVD-201901-161 、CVE-2019-0559） |
<https://portal.msrc.microsoft.com/zh-CN/security-guidance/advisory/CVE-2019-0559>  
7 | Windows Jet数据库引擎远程代码执行漏洞（CNNVD-201901-179、CVE-2019-0538） |
<https://portal.msrc.microsoft.com/zh-CN/security-guidance/advisory/CVE-2019-0538>  
8 |
Chakra脚本引擎安全漏洞（CNNVD-201901-178、CVE-2019-0539）、（CNNVD-201901-154、CVE-2019-0567）、（CNNVD-201901-153、CVE-2019-0568）
| <https://portal.msrc.microsoft.com/zh-CN/security-guidance/advisory/CVE-2019-0539https://portal.msrc.microsoft.com/zh-CN/security-guidance/advisory/CVE-2019-0567https://portal.msrc.microsoft.com/zh-CN/security-guidance/advisory/CVE-2019-0568>  
9 | Windows DHCP客户端远程代码执行漏洞（CNNVD-201901-173、CVE-2019-0547） |
<https://portal.msrc.microsoft.com/zh-CN/security-guidance/advisory/CVE-2019-0547>  
10 | Windows Hyper-V远程代码执行漏洞（CNNVD-201901-170、CVE-2019-0550） |
<https://portal.msrc.microsoft.com/zh-CN/security-guidance/advisory/CVE-2019-0550>  
  
CNNVD将继续跟踪上述漏洞的相关情况，及时发布相关信息。如有需要，可与CNNVD联系。  

联系方式：cnnvd@itsec.gov.cn

 ***本文作者：CNNVD，转载请注明来自FreeBuf.COM**

