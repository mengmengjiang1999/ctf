***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

![facebook-for-business.jpg](https://image.3001.net/images/20181120/1542697261_5bf3b12d23578.jpg!small)
**这里要分享的是一个关于Facebook商务管理平台网站（<https://www.facebook.com/business/>）的漏洞，攻击者通过构造特定的POST请求消息，可以向特定商家的后台管理员账户组中，添加任意具备管理员权限的账户，进而实现对Facebook商家后台和相关应用的管理控制。**

## Facebook Business介绍

Facebook商务管理平台（Facebook Business）是一个免费的 Facebook 平台，旨在帮助广告主集成业务的全部 Facebook
营销活动和外部合作伙伴。商家将能够投放和追踪广告，管理主页和广告帐户等资产，并添加经销商或营销合作伙伴，帮助管理业务。

Facebook
Business是一个面向所有人的平台。各种规模的商家均可使用商务管理平台集中管理所有业务资产和信息，从而有条不紊地开展业务。借助商务管理平台等中央商务中心，商家可以全面掌控
Facebook
资产，安全地管理用户访问权限，向合适的用户授予适当额度的权限。Facebook商务管理平台中的商家管理员账户（admin），可管理商家平台和主页中的所有设置、用户和权限。

## 漏洞原因及测试

在Facebook
Business商家主页的管理设置中，存在着一个向商家后台添加管理员账户的调用请求，该请求没有任何权限限制，攻击者可以向任意商家后台添加一个具备管理员权限的用户。大致的POC代码如下：

> HTTP POST
>
> /business/aymc_assets/admins/import/
>
> Host: facebook.com
>
> business_id=TARGET_BUSINESS_ID
>
> admin_id=MALICIOUS_USER_ID
>
> session_id=SESSION_ID

其中，business_id代表了目标商家的ID号，admin_id代表了想要添加进入的用户ID号，这两个编号都可以通过抓包形式了解到具体的构造格式。

## PoC视频：

## 漏洞影响

利用该漏洞，攻击者可以在不具备任何身份角色的情况下，向任意商家后台添加一个具备管理员权限的用户，以此获得对商家Facebook业务相关的后台管理、商务主页、广告账户、应用程序和Instagram账户的管理控制权限。

## 漏洞上报进程

> 2018.10.9 向Facebook安全团队上报漏洞
>
> 2018.10.9 Facebook进一步分析验证
>
> 2018.10.10 Facebook把相关存在漏洞的服务端移除
>
> 2018.10.15 Facebook再次审计确认
>
> 2018.10.15 Facebook修复漏洞
>
> 2018.10.17 Facebook向我发放 $27,500 美金的赏金

 ***参考来源：[philip](https://philippeharewood.com/facebook-business-takeover/)，clouds编译，转载请注明来自FreeBuf.COM** **  
**

