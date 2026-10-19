***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **索尼智能电视BRAVIA存在两个漏洞，CVE-2019-11889和CVE-2019-11890。**

**![dims.jpeg](https://image.3001.net/images/20190710/15627442873452.jpeg!small)**

## 漏洞原文

 **CVE-2019-11889：**

<https://www.darkmatter.ae/xen1thlabs/sony-remote-denial-of-service-triggered-over-vulnerability-hbbtv-xl-19-014/>

**CVE-2019-11890：**

<https://www.darkmatter.ae/xen1thlabs/sony-remote-denial-of-service-over-wifi-lan-internet-vulnerability-xl-19-013/>

## 产品介绍

BRAVIA是索尼视觉产品智能电视，是众所周知的高标准产品。BRAVIA是日本索尼(Sony)在新一代的电视品牌。BRAVIA是“Best
Resolution Audio Visual Integrated Architecture”的缩写，代表“最高品质的影音整合架构”。

## 漏洞细节

XEN1THLabs在Sony产品中发现了两个漏洞，并与索尼披露了这些安全缺陷。索尼Bravia智能电视中被发现存在安全性问题，但是索尼没有公布受影响型号的列表。

XEN1THLabs测试了几台索尼Bravia智能电视，漏洞总体情况如下：

> -CVE-2019-11889通过HBBTV触发索尼远程拒绝服务

影响：此漏洞允许攻击者远程破坏hbtv服务，使电视无法观看。

> -CVE-2019-11890 通过WiFi/LAN/Internet远程拒绝服务

影响：此漏洞允许攻击者使用TCP数据包攻击电视服务。

### 1.CVE-2019-11889远程拒绝服务漏洞

通过hbtv发送专门制作的网页，远程使电视停止服务。（HBBTV描述请参见2018年HITB迪拜的演示文稿

<https://conference.hitb.org/hitbsecconf2018dxb/sessions/hacking> into
broadband broadcast tv systems/）

除了换频道按钮外，遥控器其他按钮都无反应。也就是说只有换频道才能使电视机恢复正常。Android应该会杀死被阻塞的应用程序。

为了重现漏洞，首先使用以下方法生成网页：

    
    
    dd if=/dev/zero of=index.html bs=1M count=2048
    

使用软件定义的无线电，发送包含HBBTV应用程序的DVB-T信号，强制目标智能电视从受控服务器加载文件。通过强制智能电视加载生成的文件，在HBBTV应用程序停止服务前可以从日志中观察到，只有180kb到250kb之间的文件可用：

    
    
    vaccess.log:127.0.1.1:80 192.168.1.191 - - [01/Apr/2019:06:40:54 -0400] "GET /hbbtvtest/test3/ HTTP/1.1" 
    
    200 178647 "http://x.test/hbbtvtest/index.php" "Mozilla/5.0 (Linux armv7l) AppleWebKit/537.36 (KHTML, like Gecko) 
    
    Chrome/42.0.2311.152 Safari/537.36 OPR/29.0.1803.0 OMI/4.5.23.37.ALSAN5.131 HbbTV/1.2.1 (; Sony; KD-65X7500D; v1.000000000; 2016;) 
    
    sony.hbbtv.tv.2016HE"
    
    
    
    vaccess.log.1:127.0.1.1:80 192.168.1.191 - - [01/Apr/2019:02:36:16 -0400] "GET /hbbtvtest/test3/ HTTP/1.1" 
    
    200 170543 "http://x.test/hbbtvtest/index.php" "Mozilla/5.0 (Linux armv7l) AppleWebKit/537.36 (KHTML, like Gecko) 
    
    Chrome/42.0.2311.152 Safari/537.36 OPR/29.0.1803.0 OMI/4.5.23.37.ALSAN5.131 HbbTV/1.2.1 (; Sony; KD-65X7500D; v1.000000000; 2016;) 
    
    sony.hbbtv.tv.2016HE"
    

索尼调查了这个问题，调查结果为：“HTTP连接的MITM攻击是由hbtv服务的规范引起的”。

### 2.CVE-2019-11890利用Wifi/LAN/Internet远程远程拒绝服务

未经身份验证的远程攻击者可以通过局域网和Wi-Fi，使智能电视停止服务，节目崩溃，重新启动等。由于利用的复杂性较低，因此没有发布POC，索尼没有计划发布安全补丁。

索尼调查了这个问题并分享了以下分析：DOS over WiFi/LAN-这是由于Linux驱动程序中的中断操作。

## 解决办法

确保通过路由器连接到互联网或家庭网络，这样可以将风险降到最低。也可以拔下电源线恢复电视功能。

## 披露时间表

> 2019年4月1日-XEN1THLabs发现漏洞
>
> 2019年4月28日-XEN1THLabs通过其Hacker One Bug奖励计划向索尼发送报告
>
> 2019年5月2日-XEN1THLabs通过Hacker One请求更新
>
> 2019年5月10日-索尼已通过Hacker One确认漏洞
>
> 2019年5月14日-XEN1THLabs要求MITRE提供CVE
>
> 2019年5月30日-索尼通过HackOne向Xen1thLabs通知用户推荐的解决方案
>
> 2019年5月30日-XEN1THLabs要求索尼确认不会通过Hacker One提供任何安全补丁。
>
> 2019年6月7日-索尼通过Hacker One通知以下内容：“由于我们的产品团队进行的评估，我们将关闭此漏洞标签”
>
> 2019年6月26日-公开披露

## 参考

 **CVE-2019-11889**

<https://www.darkmatter.ae/xen1thlabs/sony-remote-denial-of-service-triggered-over-vulnerability-hbbtv-xl-19-014/>

 **CVE-2019-11890**

<https://www.darkmatter.ae/xen1thlabs/sony-remote-denial-of-service-over-wifi-lan-internet-vulnerability-xl-19-013/>

 ***本文作者：Kriston，转载请注明来自FreeBuf.COM**

