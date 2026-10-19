***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

**在WannaCry两周年之际，Windows再次被曝出存在高危远程漏洞。5月15日，微软官方发布了5月安全更新补丁共修复了82个漏洞，其中包含针对远程桌面（RDP）服务远程代码执行漏洞CVE-2019-0708。**

 **![wannacry-ransomware-mostly-affected-windows-7-os_en.jpg](https://image.3001.net/images/20190515/15578995436858.jpg!small)**

根据微软安全响应中心（MSRC）发布的博客文章，远程桌面协议（RDP）本身不容易收到攻击，此漏洞是预身份验证，无需用户交互。这意味着利用此漏洞的任何未来恶意软件都可能以与2017年WannaCry恶意软件遍布全球的类似方式，从易受攻击的计算机传播到其他计算机。

利用该漏洞，攻击者可安装程序、查看、更改或删除数据、或者创建拥有完全用户权限的新帐户。这个漏洞存在诱惑力可想而知，只要POC放出，就能够在大多数人没来得及更新的情况下重演WannaCry。

不过目前为止，还未发现任何恶意行为利用这个漏洞，GitHub上出现不少利用这个消息骗Star、钓鱼或者进行恶作剧的。

![WX20190515-132603.png](https://image.3001.net/images/20190515/15578982148693.png!small)

你以为是漏洞利用……

![WX20190515-132803.png](https://image.3001.net/images/20190515/15578982802205.png!small)只不过想告诉你：Never
Gonna Give You Up。

### CVE-2019-0708 漏洞影响范围：

> Windows 7
>
> Windows Server 2008 R2
>
> Windows Server 2008
>
> Windows Server 2003（已停止维护）
>
> Windows XP（已停止维护）

除了Win8、Win 10之外，几乎所有的Windows版本都受到这个漏洞的影响。尽管微软已经停止了对Windows 2003和Windows
XP的支持，但由于这次漏洞危害程度较高，微软此次修复补丁也覆盖了所有的受影响的Windows版本。

## 安全建议

### 1.临时应对方法

在受影响版本的系统上启用网络级身份验证（NLA）；启用NLA后，攻击者需要使用目标系统上的有效账户对远程桌面服务进行身份验证，才能成功利用该漏洞。

微软官方建议，无论是否开启NLA，都应该尽快更新，彻底消除该漏洞的影响。

### 2.安全补丁

由于Win8 和 Win 10不受CVE-2019-0708漏洞的影响，所以这些用户可以放心。对于Win 7和Server
2008用户而言，可以直接通过系统自动更新安装漏洞补丁。如果已经关闭系统自动更新的，可以从以下链接下载对应版本补丁安装：

> <https://portal.msrc.microsoft.com/en-US/security-> guidance/advisory/CVE-2019-0708>

对于Windows 2003和Windows
XP用户，由于官方已经停止支持，无法通过自动更新安装补丁，需要手动通过以下地址下载安全补丁自行安装（360安全卫士用户可以通过“漏洞修复”功能快捷安装补丁）：

> <https://support.microsoft.com/zh-cn/help/4500705/customer-guidance-for-> cve-2019-0708>

 ***参考来源：[MSRC](https://blogs.technet.microsoft.com/msrc/2019/05/14/prevent-a-worm-by-updating-remote-desktop-services-cve-2019-0708/)，本文作者
shidongqi，转载请注明来自FreeBuf.COM**

