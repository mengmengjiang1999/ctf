![](https://image.3001.net/images/20210513/1620900614_609cfb06b83e7e505e9fc.png!small)

## 概括

Adobe已针对Windows和macOS发布了Adobe
Acrobat和Reader的安全更新。这些更新解决了多个[关键](https://helpx.adobe.com/security/severity-ratings.html)和 [重要](https://helpx.adobe.com/security/severity-ratings.html)漏洞。成功的利用可能导致当前用户上下文中的任意代码执行。

Adobe已收到一份报告，指出CVE-2021-28550已在针对Windows上Adobe Reader用户的有限攻击中 **被狂野利用。**

Adobe已发布5月份的[Patch
Tuesday更新](https://helpx.adobe.com/security.html)，修复了涵盖12种不同产品的多个漏洞，其中包括影响Adobe
Reader的零日漏洞， **该漏洞在野外被积极利用。**

更新的应用程序列表包括[Adobe Experience
Manager](https://helpx.adobe.com/security/products/experience-manager/apsb21-15.html)，[Adobe
InDesign](https://helpx.adobe.com/security/products/indesign/apsb21-22.html)，[Adobe
Illustrator](https://helpx.adobe.com/security/products/illustrator/apsb21-24.html)，[Adobe
InCopy](https://helpx.adobe.com/security/products/incopy/apsb21-25.html)，[Adobe
Genuine
Service](https://helpx.adobe.com/security/products/integrity_service/apsb21-27.html)，Adobe
Acrobat和Reader，[Magento](https://helpx.adobe.com/security/products/magento/apsb21-30.html)，Adobe
[Creative Cloud桌面](https://helpx.adobe.com/security/products/creative-cloud/apsb21-31.html)应用程序，Adobe [Media
Encoder](https://helpx.adobe.com/security/products/media-encoder/apsb21-32.html)，Adobe [After
Effects](https://helpx.adobe.com/security/products/after_effects/apsb21-33.html)，Adobe
Medium和Adobe Animate 。

该公司在一份安全公告中[承认](https://helpx.adobe.com/security/products/acrobat/apsb21-29.html)，已收到报告称该漏洞“已在针对Windows上Adobe
Reader用户的有限攻击中被广泛利用”。跟踪号为 **CVE-2021-28550的** 零日漏洞涉及 **任意代码执行漏洞**
，该漏洞可能使对手几乎可以在目标系统上 **执行任何命令** 。

尽管针对性攻击针对的是Adobe Reader的Windows用户，但此问题同时影响Windows和macOS版本的Acrobat DC，Acrobat
Reader DC，Acrobat 2020，Acrobat Reader 2020，Acrobat 2017和Acrobat Reader 2017

在Adobe Acrobat和Reader中解决了10个关键漏洞和四个重要漏洞，然后对Adobe
Illustrator中的五个关键漏洞（CVE-2021-21101
CVE-2021-21105）进行了修复，这些漏洞可能导致在当前环境下任意执行代码用户。Adobe将Fortinet的FortiGuard
Labs的Kushal Arvind Shah归功于报告了五个漏洞中的三个。

总计，在星期二的更新中已解决了总共43个安全漏洞。建议用户将其软件安装更新到最新版本，以减轻与漏洞相关的风险。

## 适用于Adobe Acrobat和Reader的安全更新| APSB21-29

 **公告编号**|  **发布日期**|  **优先事项**  
---|---|---  
APSB21-29| 2021年5月11日| 1个  
  
## 受影响的版本

 **产品**|  **追踪**|  **受影响的版本**|  **平台**  
---|---|---|---  
Acrobat DC | 连续的 | 2021.001.20150和更早版本 | Windows  
Acrobat Reader DC| 连续的 | 2021.001.20150和更早版本 | Windows  
Acrobat DC| 连续的 | 2021.001.20149及更早版本 版本 | 苹果系统  
Acrobat Reader DC| 连续的 | 2021.001.20149及更早版本 版本 | 苹果系统  
  
|  
|  
|  
  
Acrobat 2020| 经典2020 | 2020.001.30020和更早版本| Windows和macOS  
Acrobat Reader 2020| 经典2020 | 2020.001.30020和更早版本| Windows和macOS  
  
|  
|  
|  
  
Acrobat 2017| 经典2017| 2017.011.30194及更早版本 | Windows和macOS  
Acrobat Reader 2017| 经典2017| 2017.011.30194及更早版本 | Windows和macOS  
  
## 解决方案

Adobe建议用户按照以下说明将其软件安装更新到最新版本。

最新的产品版本可通过以下方法之一提供给最终用户：

> 用户可以通过选择“帮助”>“检查更新”来手动更新其产品安装。
>
> 检测到更新后，产品将自动更新，而无需用户干预。
>
> 完整的Acrobat Reader安装程序可以从 [Acrobat
> Reader下载中心下载](https://get.adobe.com/reader)。

对于IT管理员（托管环境）：

> 请参阅特定的发行说明版本以获取安装程序的链接。
>
> 通过首选的方法（例如AIP-GPO，引导程序，SCUP / SCCM（Windows））或在macOS，Apple Remote
> Desktop和SSH上安装更新。

Adobe将这些更新归类为以下 [优先级，](https://helpx.adobe.com/security/severity-ratings.html)并建议用户将其安装更新为最新版本：

**产品**|  追踪|  **更新版本**|  **平台**|  **优先等级**|  **可用性**  
---|---|---|---|---|---  
AcrobatDC| 连续的| 2021.001.20155 | Windows和macOS| 1个| [
_发行说明_](https://www.adobe.com/devnet-docs/acrobatetk/tools/ReleaseNotesDC/index.html#continuous-track)  
Acrobat Reader DC| 连续的| 2021.001.20155 | Windows和macOS| 1个|
[发行说明](https://www.adobe.com/devnet-docs/acrobatetk/tools/ReleaseNotesDC/index.html#continuous-track)  
  
|  
|  
|  
|  
|  
  
Acrobat 2020| 经典2020 | 2020.001.30025 | Windows和macOS | 1个| [
_发行说明_](https://www.adobe.com/devnet-docs/acrobatetk/tools/ReleaseNotesDC/index.html#classic-track)  
Acrobat Reader 2020| 经典2020 | 2020.001.30025 | Windows和macOS | 1个| [
_发行说明_](https://www.adobe.com/devnet-docs/acrobatetk/tools/ReleaseNotesDC/index.html#classic-track)  
  
|  
|  
|  
|  
|  
  
Acrobat 2017| 经典2017| 2017.011.30196 | Windows和macOS| 1个| [
_发行说明_](https://www.adobe.com/devnet-docs/acrobatetk/tools/ReleaseNotesDC/index.html#id3)  
Acrobat Reader 2017| 经典2017| 2017.011.30196 | Windows和macOS| 1个| [
_发行说明_](https://www.adobe.com/devnet-docs/acrobatetk/tools/ReleaseNotesDC/index.html#id3)  
  
## 漏洞详情

 **漏洞类别**|  **漏洞影响**|  **严重程度**|  **CVE编号**  
---|---|---|---  
缓冲区溢出| 任意代码执行| 重要的| CVE-2021-28561  
基于堆的缓冲区溢出| 任意代码执行| 危急| CVE-2021-28560  
基于堆的缓冲区溢出| 任意代码执行| 重要的 | CVE-2021-28558  
越界读取| 内存泄漏| 危急| CVE-2021-28557  
越界读取| 任意文件系统读取| 重要的 | CVE-2021-28555  
越界读取| 任意代码执行| 危急 | CVE-2021-28565  
越界写| 任意代码执行| 危急 | CVE-2021-28564  
越界写| 任意代码执行| 危急| CVE-2021-21044CVE-2021-21038CVE-2021-21086  
公开私人信息| 特权提升| 重要的 | CVE-2021-28559  
免费使用| 任意代码执行| 危急 | CVE-2021-28562CVE-2021-28550CVE-2021-28553

