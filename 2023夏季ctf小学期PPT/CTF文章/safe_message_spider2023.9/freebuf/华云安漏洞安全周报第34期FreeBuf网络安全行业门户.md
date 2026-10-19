根据国家信息安全漏洞库（CNNVD）统计，本周（2021.
5.10~2021.5.16）CNNVD接报漏洞1540个，信息技术产品漏洞（通用型漏洞）81个，网络信息系统漏洞（事件型漏洞）1459个，其中华云安报送
**13个** ；CNNVD接报漏洞预警78份，其中华云安报送预警 **9份** ， **预警报送数量位列前三！**
_[（数据来源于CNNVD）](https://link.zhihu.com/?target=https%3A//mp.weixin.qq.com/s%3F__biz%3DMzAxODY1OTM5OQ%3D%3D%26mid%3D2651441838%26idx%3D2%26sn%3D8b58ca4919c9c514da17f020348357e9%26scene%3D21%23wechat_redirect)_

本周重点关注漏洞包括：Microsoft 多个安全漏洞、Adobe Acrobat Reader 多个安全漏洞、CVE-2021-32605-Zzzcms
远程代码执行漏洞、CVE-2021-26900-Win32k 本地提权漏洞、CVE-2021-22204-ExifTool
代码执行漏洞、CVE-2021-31181-Microsoft SharePoint 远程命令执行漏洞、CVE-2021-26419-Internet
Explorer 脚本引擎内存损坏漏洞。漏洞影响范围较广，华云安建议相关用户做好资产自查与预防工作。

##  **Microsoft 多个安全漏洞**

严重

2021年5月12日，Microsoft 官方发布了5月份安全更新，本次共发布了55个漏洞的补丁，同比上月减少了53个。主要涵盖了 Windows
操作系统、Exchange Server、.Net Core、Office、SharePoint Server、Hyper-V、 Visual Studio
等众多组件。在漏洞等级方面，共包含4个超危漏洞、50个高危漏洞、1个中危漏洞；在漏洞类型方面，共包含22个远程代码执行漏洞，11个权限提升漏洞，1个拒绝服务漏洞，10个信息泄露漏洞，1个跨站脚本攻击，8个欺骗攻击以及2个安全特征绕过。对此，华云安建议用户及时到
Microsoft 官方网站下载安装对应版本的安全补丁！

情报来源：

[https://msrc.microsoft.com/update-guide/releaseNote/2021-May](https://link.zhihu.com/?target=https%3A//msrc.microsoft.com/update-guide/releaseNote/2021-May)

  

##  **CVE-2021-31181-Microsoft SharePoint 远程命令执行漏洞**

  
高危

2021年5月12日，华云安思境安全团队发现 Microsoft 官方发布安全更新，披露了 Sharepoint 组件中存在一处远程命令执行漏洞。
Microsoft SharePoint
是微软的业务协助平台，用于对业务信息进行整合，并能够共享工作、与他人协同工作等。该漏洞是由于服务器无法正确处理外部传入的XML，解析时可能产生恶意控件，成功利用此漏洞攻击者可以构造恶意数据执行远程代码攻击，从而获取服务器权限。

情报来源：

[https://msrc.microsoft.com/update-guide/en-US/vulnerability/CVE-2021-31181](https://link.zhihu.com/?target=https%3A//msrc.microsoft.com/update-guide/en-US/vulnerability/CVE-2021-31181)

  

##  **CVE-2021-26419-Internet Explorer 脚本引擎内存损坏漏洞**

高危

2021年5月12日，华云安思境安全团队发现 Microsoft 官方发布安全更新，披露了 Internet Explorer
中存在一处脚本引擎内存损坏漏洞。Internet Explorer 是微软公司推出的一款网页浏览器。自从1995年开始，内置在各个新版本的 Windows
操作系统，是 Windows 系统组件之一。成功利用此漏洞攻击者可以构造恶意网页诱使用户进行访问，从而在用户机器上执行任意命令。

情报来源：

[https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-26419](https://link.zhihu.com/?target=https%3A//msrc.microsoft.com/update-guide/vulnerability/CVE-2021-26419)

##  **Adobe Acrobat Reader 多个安全漏洞**

严重

2021年5月12日，华云安思境安全团队发现 Adobe 官方发布安全更新，披露了 Adobe Acrobat Reader
组件中存在10个安全漏洞。Adobe Acrobat Reader 是由 Adobe 公司所开发的电子文字处理软件集，可用于阅读、编辑、管理和共享 PDF
文档。此次漏洞涉及 UAF、内存越界写、内存越界读、缓冲区溢出等多个类型，漏洞等级较为严重，华云安建议用户及时修复更新。

情报来源：

[https://helpx.adobe.com/security/products/acrobat/apsb21-29.html](https://link.zhihu.com/?target=https%3A//helpx.adobe.com/security/products/acrobat/apsb21-29.html)

##  **CVE-2021-32605-Zzzcms 远程代码执行漏洞**

超危

2021年5月13日，华云安思境安全团队发现 zzzcms 官方发布安全更新，披露了 zzzcms 的组件中存在一处远程代码执行漏洞。Zzzcms
是一套互联网商务建站系统，采用 asp+access 进行开发的免费建站系统源码，软件绿色可直接使用，直接上传到空间内即可。该漏洞是由于
parserIfLabel 模块存在模板注入而导致，攻击者无需身份验证即可利用此漏洞，在受影响的 zzzphp 上执行任意代码，从而获取相关权限。

情报来源：

[https://srcincite.io/advisories/src-2021-0015/](https://link.zhihu.com/?target=https%3A//srcincite.io/advisories/src-2021-0015/)

##  **CVE-2021-26900-Win32k 本地提权漏洞**

高危

2021年5月14日，华云安思境安全团队发现 Microsoft 官方发布安全更新，披露了 Win32k 组件中存在一处本地提权漏洞。Win32k 是
Windows 子系统的内核模式部分，向用户代码提供了大量的系统服务。成功利用此漏洞，攻击者在低权限下进行权限提升，从而获取系统最高权限。

情报来源：

[https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-26900](https://link.zhihu.com/?target=https%3A//msrc.microsoft.com/update-guide/vulnerability/CVE-2021-26900)

##  **CVE-2021-22204-ExifTool 代码执行漏洞**

高危

2021年5月15日，华云安思境安全团队发现 ExifTool 组件中存在一处远程代码执行漏洞。ExifTool 是一个独立于平台的 Perl
库，也有一个命令行应用程序，用于读取，写入和编辑各种文件中的元信息。该漏洞是由于 ExifTool 对 DjVu
文件格式的数据处理不当。成功利用此漏洞攻击者可以构造恶意的 DjVu 文件，导致任意代码执行，从而获取服务器最高权限。

情报来源：

[https://github.com/exiftool/exiftool/commit/cf0f4e7dcd024ca99615bfd1102a841a25dde031#diff-fa0d652d10dbcd246e6b1df16c1e992931d3bb717a7e36157596b76bdadb3800](https://link.zhihu.com/?target=https%3A//github.com/exiftool/exiftool/commit/cf0f4e7dcd024ca99615bfd1102a841a25dde031%23diff-fa0d652d10dbcd246e6b1df16c1e992931d3bb717a7e36157596b76bdadb3800)

## 进入 **华云安漏洞情报平台** 参阅详情

[漏洞情报平台​vti.huaun.com﻿](https://link.zhihu.com/?target=https%3A//vti.huaun.com/index/)

