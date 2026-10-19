安全研究人员最新发现，威胁者正扫描运行Fancy Product Designer插件的网站，以利用一个0day漏洞上传恶意软件。

![](https://image.3001.net/images/20210603/1622690887_60b84c47902211dc7e998.jpg!small)

Fancy Product
Designer是WordPress、WooCommerce和Shopify的一个可视化产品配置插件，它允许客户使用自己的图形和内容定制产品。据统计，Fancy
Product Designer已在超过 17,000
个网站上销售和安装。然而，尽管该插件进行了一些安全检查以防止上传恶意文件，但这些检查是不够的并且很容易被绕过。

## 0-day漏洞也影响了WooCommerce网站

0day漏洞是供应商尚未修补但已公开披露的漏洞，在某些情况下，这些漏洞也被广泛利用或具有公开可用的概念验证漏洞。此次研究发现的安全漏洞是一种严重的远程代码执行(RCE)漏洞。

威胁分析师称，Fancy Product Designer插件版本也是WooCommerce 安装中使用的版本，并且很容易受到网络攻击，而对于插件的
Shopify 版本，鉴于Shopify对其平台上托管和运行的站点使用更严格的访问控制，攻击可能会被阻止。

## 易受攻击的网站可能被完全接管

攻击者成功利用Fancy Product Designer
漏洞后，可以绕过阻止恶意文件上传的内置检查，并在安装插件的站点上部署可执行的PHP文件。在威胁者执行远程代码攻击之后，可以完全接管易受攻击的站点。目前，该漏洞仅被小规模用以进行网络攻击，但针对运行Fancy
Product Designer 插件的数千个站点的攻击，已于两周多前(2021年5月16日)开始。

## 攻击详细参数

描述：未经身份验证的任意文件上传和远程代码执行

受影响的插件：Fancy Product Designer

Plugin Slug： fancy-product-designer

受影响的版本： <= 4.6.8

CVE ID： CVE-2021-24370

CVSS 分数： 9.8(严重)

CVSS 向量： CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H

在大多数情况下，网络攻击成功后，会生成一个具有唯一ID和PHP扩展名的文件，该文件将出现在文件上传日期wp-admin或wp-content/plugins/fancy-product-designer/inc文件上传日期的子文件夹中。

例如：

wp-content/plugins/fancy-product-designer/inc/2021/05/30/4fa00001c720b30102987d980e62d5e4.php

或者wp-admin/2021/05/31/1d4609806ff0f4e89a3fb5fa35678fa0.php

针对此0-day漏洞的大多数攻击来自以下 IP 地址：

69.12.71.82

92.53.124.123

46.53.253.152

虽然防火墙的内置文件上传保护可以阻止针对此漏洞的大多数攻击，但并不排除在某些配置中出现绕过的可能。并且该0-day漏洞被积极利用且严重等级高，因此建议使用此插件的人尽可能卸载
Fancy Product Designer，直到有补丁版本出现。

系统安全是应用软件安全的基础，据统计0-day漏洞每年以100%速度增长，而且修复周期极长，极易受到网络犯罪分子攻击。但在日常普通安全测试中很难发现0-day漏洞，因此在软件开发过程中需要加强安全建设，从源头保证代码规范安全，这样在一定程度上可以减少因代码问题产生的系统漏洞，为软件运行提供一个安全的环境。

参读链接：<https://www.woocoom.com/b021.html?id=eed4d832a0ca4cf5b41d5af2727f00e4>

