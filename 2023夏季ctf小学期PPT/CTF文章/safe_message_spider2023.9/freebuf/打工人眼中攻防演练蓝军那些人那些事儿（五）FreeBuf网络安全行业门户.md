## 系列文章

由于本系列文章较长，故分为四个部分，如需回顾前文，可点击下方链接：

>
> [打工人眼中攻防演练蓝军那些人那些事儿（一）](https://www.freebuf.com/articles/network/261597.html)
>
>
> [打工人眼中攻防演练蓝军那些人那些事儿（二）](https://www.freebuf.com/articles/network/261604.html)
>
>
> [打工人眼中攻防演练蓝军那些人那些事儿（三）](https://www.freebuf.com/articles/network/261608.html)
>
>
> [打工人眼中攻防演练蓝军那些人那些事儿（四）﻿](https://www.freebuf.com/articles/network/261612.html)
>
> 打工人眼中攻防演练蓝军那些人那些事儿（五）

> 一旦发现攻击事件，溯源分析，提交防守报告得分才是我们后面的工作重点。

# 8.1常见溯源思路

攻防演练蓝军防守规则：

> 防守方提交防守报告上限为50个；
>
> 防守方完整还原攻击链条，溯源到黑客的虚拟身份、真实身份，溯源到攻击队员，反控攻击方主机可获得加分；
>
> 如未识别攻击行为导致权限丢失则视为防守失败，视情况予以扣分；
>
> 非正常防守将扣分，包括封禁C段、网站不可用、网站首页改为图片等（自通知起2小时后开始扣分）

从防守规则可以看出提高名次大致就三点

> 1.事前安全排查，减少威胁，降低被攻击的风险；
>
> 2.事中安全监测，及发现并阻止攻击行为，防止因目标系统权限丢失而失分；
>
> 3.事后溯源分析，通过专业的流量和日志分析等溯源手段提交防守报告而增加防守得分。

事前如何进行风险排查和事中如何监控，前边文章已经写过，今天分享一些如何进行溯源分析的内容。

以网御TAR和NFT设备为例，对于攻击行为一般会记录如下信息,作为溯源基础信息：

> 攻击时间
>
> 攻击 IP
>
> 攻击类型
>
> 恶意文件
>
> 受攻击域名/IP

而作为甲方，如果要防守得分我们一般需要尽可能获取以下信息，匹配度越高越好，一般溯源到攻击者真实姓名和公司名得分较高

> 姓名/ID
>
> 攻击 IP及跳板机
>
> 地理位置
>
> QQ/微信
>
> 邮箱
>
> 手机号
>
> 支付宝
>
> IP 地址所属公司
>
> IP 地址关联域名
>
> 其他社交账号信息(如微博/src/id/云盘/csdn/github)
>
> 人物照片

这里说一点的是，如果部署各厂家蜜罐的话，对于获取一些攻击IP、地理位置和关键账号信息，溯源较为容易，正因为此原因，所以小道消息听说21年攻防演练会降低蜜罐溯源的分值，所以大家还是好好学习正儿八经的溯源之道。

一般根据安全设备发现的攻击者的攻击IP、恶意文件、域名等，可以通过威胁情报确定进一步确定攻击者ID、注册公司、邮箱、电话等。

以微步为例，通过上传捕获的恶意文件，通过沙箱可以捕获一些网络行为，其中包括一些域名、IP、DNS等，然后再对域名/IP进行上传分析，可以获得一些历史域名解析记录、whois信息、数字签名信息等。再通过域名解析、whois和数字签名有时就可以确定一些攻击者的ID、邮箱、手机等个人信息。

![1615707552350-69072d0f-dc63-495a-8025-47a24595d53d.png](https://image.3001.net/images/20210316/1615895886_60509d4eb239bc5177e25.png!small)

![1615707682243-12b4d5cc-0c3e-4c8a-b6f8-4e3b2597cf10.png](https://image.3001.net/images/20210316/1615895888_60509d5028f1a1d19225d.png!small)

类似威胁情报平台各大厂商其实都有，整理部分如下：

> 微步在线：<https://x.threatbook.cn/>
>
> 启明Venuseye：<https://www.venuseye.com.cn/>
>
> 绿盟NTI:<https://nti.nsfocus.com/>
>
> 奇安信：<https://ti.qianxin.com/>
>
> 安恒：<https://ti.dbappsecurity.com.cn/>
>
> 360：<https://ti.360.cn/#/homepage>
>
> feed：<https://feed.watcherlab.com/index/ioc>
>
> IBM：<https://feed.watcherlab.com/index/ioc>

 **whois** 查询很多时候是隐藏的，各大注册商以及第三方站长工具的域名WHOIS信息查询整理如下：

> 中国万网域名WHOIS信息查询地址：<https://whois.aliyun.com/>
>
> 西部数码域名WHOIS信息查询地址：<https://whois.west.cn/>
>
> 新网域名WHOIS信息查询地址：<http://whois.xinnet.com/domain/whois/index.jsp>
>
> 纳网域名WHOIS信息查询地址：<http://whois.nawang.cn/>
>
> 中资源域名WHOIS信息查询地址：<https://www.zzy.cn/domain/whois.html>
>
> 三五互联域名WHOIS信息查询地址：<https://cp.35.com/chinese/whois.php>
>
> 新网互联域名WHOIS信息查询地址：<http://www.dns.com.cn/show/domain/whois/index.do>
>
> 美橙互联域名WHOIS信息查询地址：<https://whois.cndns.com/>
>
> 爱名网域名WHOIS信息查询地址：<https://www.22.cn/domain/>
>
> 易名网域名WHOIS信息查询地址：<https://whois.ename.net/>

 **站长工具类第三方查询地址(** **部分网站注册人信息会隐藏或提示** 联系域名注册商获取，可以去who.is查询看看)

> Kali的查询：whois -h 注册服务器地址 域名
>
> 站长工具-站长之家域名WHOIS信息查询地址：<http://whois.chinaz.com/>
>
> 爱站网域名WHOIS信息查询地址：<https://whois.aizhan.com/>
>
> 腾讯云域名WHOIS信息查询地址：<https://whois.cloud.tencent.com/>
>
> 国外的who.is：<https://who.is/>
>
> 微步：<https://x.threatbook.cn/>
>
> Virus Total：<https://www.virustotal.com>

还有Kali中自带的whois查询、一些集成工具等。

SSL证书查询网站整理如下：

主要网站如下：

> （1）<https://crt.sh/>
>
> （2）<https://censys.io/>
>
> （3）<https://developers.facebook.com/tools/ct/>
>
> （4）<https://google.com/transparencyreport/https/ct/>

域名解析的话，主要是解析对应的一个或多个IP地址及子域名，也可以全球ping和多地ping确定下是否村存在CDN，如果有还要再继续找下真实IPD地址，总之都是为了确定真实IP地址，以方便后边的IP真实地理位置定位和确定个人信息。

待确定真实IP之后，可继续通过IP反查、威胁情报和IP定位等继续获取攻击者信息，越多越好。

IP反查网站：

> 微步等情报威胁中心本身自带IP反查
>
> IPIP： <https://www.ipip.net/ip.html>
>
> 爱站： <https://www.aizhan.com/>
>
> 站长之家：<http://whois.chinaz.com/>

IP定位：

