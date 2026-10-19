***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **近日，国家信息安全漏洞库（CNNVD）收到关于Drupal
Core远程代码执行漏洞（CNNVD-201804-1490、CVE-2018-7602）情况的报送。成功利用此漏洞的攻击者可以对目标系统进行远程代码执行攻击。Drupal的7.x版和8.x版等多个版本均受此漏洞影响。目前，该漏洞的部分漏洞验证代码已在互联网上公开，且Drupal官方已经发布补丁修复了该漏洞，建议用户及时确认是否受到漏洞影响，尽快采取修补措施。**

##  **一、漏洞介绍**

Drupal是Drupal社区所维护的一套用PHP语言开发的免费、开源的内容管理框架，它由内容管理系统（CMS）和PHP开发框架（Framework）共同构成。

Drupal Core远程代码执行漏洞（CNNVD-201804-1490、CVE-2018-7602），该漏洞与之前2018年3月的Drupal
Core远程代码执行漏洞（CNNVD-201803-1136
、CVE-2018-7600）相关，漏洞源于Drupal官方对该漏洞修复不完全，导致补丁可以被绕过，从而实现远程代码执行。

##  **二、危害影响**

成功利用此漏洞的攻击者可以对目标系统进行远程代码执行攻击。目前，该漏洞的部分漏洞验证代码已在互联网上公开，近期被利用的可能性较大。受漏洞影响版本如下：

Drupal的7.x版、Drupal的8.x版。

##  **三、修复建议**

目前，Drupal官方已经发布补丁修复了该漏洞，请用户及时检查产品版本，如确认受到漏洞影响，请尽快按以下措施进行防护。

1、 升级Drupal版本：

Drupal 7.x请升级到Drupal 7.59版本。

Drupal 8.4.x版本请升级到8.4.8版本

Drupal 8.5.x请升级到Drupal 8.5.3版本。

2、 若用户无法立即升级版本，请更新补丁，补丁地址为：

版本  |  补丁地址  
---|---  
7.X版本  |
[https://cgit.drupalcode.org/drupal/rawdiff/?h=7.x&id=080daa38f265ea28444c540832509a48861587d0](https://cgit.drupalcode.org/drupal/rawdiff/?h=7.x&id=080daa38f265ea28444c540832509a48861587d0)  
Drupal 8. x  |
[https://cgit.drupalcode.org/drupal/rawdiff/?h=8.5.x&id=bb6d396609600d1169da29456ba3db59abae4b7e](https://cgit.drupalcode.org/drupal/rawdiff/?h=8.5.x&id=bb6d396609600d1169da29456ba3db59abae4b7e)  
  
本通报由CNNVD技术支撑单位——安恒信息技术有限公司、杭州迪普科技股份有限公司提供支持。

CNNVD将继续跟踪上述漏洞的相关情况，及时发布相关信息。如有需要，可与CNNVD联系（cnnvd@itsec.gov.cn）。

 ***本文作者：CNNVD，转载请注明来自FreeBuf.COM**

