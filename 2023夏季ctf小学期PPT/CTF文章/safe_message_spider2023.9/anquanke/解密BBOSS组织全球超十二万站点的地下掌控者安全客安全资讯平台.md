# 解密BBOSS组织：全球超十二万站点的地下掌控者

阅读量 **84177**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2016-01-19 10:16:05

 **x**

##### 译文声明

本文是翻译文章，文章来源：FREEBUF

原文地址：[http://www.freebuf.com/articles/system/93491.html?from=groupmessage&isappinstalled=0](http://www.freebuf.com/articles/system/93491.html?from=groupmessage&isappinstalled=0)

译文仅供参考，具体内容表达以及含义原文为准。

****

**每一天我们都在疑惑,疑惑我们所处的世界,疑惑这个世界呈现出的不断超出我们认知的事物。每一天我们又都在惊喜,惊喜的是不断的新的认知,总能让我们短暂地认为,似乎又更理解了这个世界。疑惑与惊喜的交织,似乎是对人类最好的诱惑,驱使着我们一直探索。未知到已知的转换,似乎是我们认知世界唯一的途径。
永远令人着迷的不是未知,而是下一个未知。**

**1\. 报告楔子**

还记得2015年年末基于TelsaCrypt变种(VVV病毒)猖獗的勒索攻击吗?阿里安全威胁情报中心监测到大量来自邮件的此类攻击,同时在调查中发现有客户未收到邮件也受到了勒索软件的攻击。进一步跟踪调查发现客户是访问了被挂马网站导致感染。

基于发现的挂马指纹在全球范围内做指纹探测,发现互联网上具有同样特征的网站总计超过12万,深入地调查了此次事件,我们注意到该事件背后程序架构体系已经非常完善,达工业化水准。基于从代码结构中发现的BASE层和
BOSS层信息,故将其命名为BBOSS组织(事件)。

**2\. 全球影响**

根据截至1月13日全网监测数据显示,BBOSS组织在最近三个月内呈显性活跃,入侵控制网站的规模也不断扩张。这些被控制的站点以欧美地区为主,亚非地区目前相对较少,
但已经呈蔓延趋势。

[](http://image.3001.net/images/20160118/14531257157814.png)

图 1 BBOSS全球威胁态势

受灾最为严重的为美国,比例高达30%,其次为欧洲各国,亚洲国家中韩国排列第一,占到4%,而南美、非洲、澳洲占比最小。

[](http://image.3001.net/images/20160118/14531257289901.png)

图 2 BBOSS威胁全球分布

**2.1. 影响站点和软件**

受感染的网站数量全球范围内超过12万个,其中约78%都使用了开源CMS框架,以Wordpress和Jommla
为主,尤其是Wordpress,占比高达57%。

[](http://image.3001.net/images/20160118/14531258616640.png)

图 3 BBOSS 影响软件比例(N表示无任何CMS软件)

**3\. BBOSS技术体系**

控制超过12万的网站,BBOSS背后的技术体系也极其完善,可以看到该组织为了更高效掌控和易隐藏,使用了多层架构,目前已形成控制超大规模集群肉鸡网站的能力。

[](http://image.3001.net/images/20160118/14531259894761.png)

图 4 BBOSS系统技术体系

BBOSS技术体系中,大致分为4层,分别是JS层,BASE层,KEEPER层和BOSS层。每一层的肉鸡分工明确,配合密切。JS层为直接接触用户的站点,页面中嵌入了js,构造请求转发流量到BASE层。BASE层会向BOSS层请求指令,完成校验后BOSS层根据当前需要进行的攻击返回攻击指令,再由BASE层下发给用户。同时,KEEPER层会定期对JS层和BASE层站点进行探测存活、增删修改、漏洞利用等操作。

[](http://image.3001.net/images/20160118/14531259975704.png)

图 5 BBOSS分层关系

**3.1. JS层分析**

JS层受感染的网站数量全球范围内有10万个左右,这一层站点约85%都使用了开源CMS框架,其中以Wordpress占比63%,Jommla占比10%。

[](http://image.3001.net/images/20160118/145312603020.png)

图 6 JS层站点CMS比例(N表示无任何CMS软件)

在近日,我们也关注到PaloAlto Netwokrs公布的报告「Angler Exploit Kit Continues to Evade
Detection: Over 90,000 Websites
Compromised」,对其公布的数据进行比对,发现仅11863个域名匹配,这些网站具备弱密码或通用型漏洞,易被入侵,这和本次事件中在这些网站上发现多种不同类型的webshell的证据吻合。

[](http://image.3001.net/images/20160118/14531260467069.png)

图 7 JS层webshell之一

JS层站点受感染的特征表现为,其框架head.php内均被嵌入了恶意js,导致访问网站所有页面时都会带有该script。基于wordpress的网站主要是通过webshell在其主题的/wp-content/themes/twentyfourteen/header.php中插入,而基于Jommla的主要通过在/libraries/joomla/document/html/renderer/head.php中来插入。

[](http://image.3001.net/images/20160118/14531260595647.png)

图 8 修改header.php

恶意js代码如下,提取了当前页title、referer、host信息,构造请求后发往BASE层域下的jquery.min.php文件。

[](http://image.3001.net/images/20160118/14531260701941.png)

图 9 JS层恶意代码

KEEPER层会不定期更新JS层站点的header.php
中的植入js,同测试发现其带有一定对抗能力。当模拟一个JS层站点对BASE层站点进行请求测试时,如果被检测出是模拟测试,该JS层站点下所植入的恶意js会被暂时性清除几天。

**3.2. BASE层分析**

与JS层相同,BASE层依然是大量被入侵控制的站点,BASE层受感染数量与JS层受感染数量大致为1:5的关系。与JS层不同的是,这一层的站点不再是以CMS为主,85%站点均未使用任何CMS,并且处于中国地区的站点极少,这类站点以IIS,Apache偏多,也存在少量Nginx站点。

[](http://image.3001.net/images/20160118/14531260905314.png)

图 10 BASE层站点CMS比例

可以看到以往的攻击在这一层就直接开始植入恶意载荷了,但BBOSS不是,BASE这一层仍然只是中间跳板。BASE层站点表现的特征为,被入侵后会在网站目录下放置js/jquery.min.php和js/jquery-1.9.1.min.php两个文件。这两个文件使用障眼法,让用户误以为是jquery相关的jquery.min.js及jquery-1.9.1.min.js。

[](http://image.3001.net/images/20160118/14531260984729.png)

图 11 BASE层恶意样本

按图索骥,拿到了jquery.min.php样本,揭开了其神秘的面纱。代码中使用了加密和混淆,解密后看到其封装了BossAPI类,该类实现了向后端BOSS层的C&C的通信,并解析响应结果的功能。

[](http://image.3001.net/images/20160118/14531261143011.png)

图 12 BossAPI类

主程序部分包含3个流程,若GET请求参数为空,构造同域名下随机页面,访问并404返回。

[](http://image.3001.net/images/20160118/14531261265829.png)

图 13 GET为空

c_utm流程用于接收来自JS层构造的请求,并随机转发给BOSS层的4台C&C,C&C会根据请求中的参数,下发恶意指令。

[](http://image.3001.net/images/20160118/14531261363357.png)

图 14 c_utm流程

pi流程主要用于接收来自KEEPER层的流量,并转发给BOSS层C&C来校验,用于判定BASE层是否存活以及是否是伪造。

[](http://image.3001.net/images/20160118/14531261497700.png)

图 15 pi流程

同时,发现BASE层同BOSS层的通信同样也存在一定的反侦查策略。另外代码中还自带了xor加密解密类,但目前尚未在主程序中使用。

**3.3. BOSS层分析**

与前面两层不同,BOSS层受感染的机器数量要小得多。截止目前,通过分析多个从BASE层采集到的jquery.min.php及jquery.1.9.1.min.php样本,获得了4个活跃的BOSS层C&C
IP,以及一个闲置的IP。这5个IP的近期流量趋势如下:

[](http://image.3001.net/images/20160118/14531261879084.png)

图 16 BOSS层流量趋势

有意思的是,这5个ip分属不同的5个国家,分别是美国、俄罗斯、立陶宛、法国和印度尼西亚,这些独立IP同样也都是入侵而来。根据我们的数据显示,2015年11月其身影出现在了VVV勒索攻击中,以及一些恶意推广。

[](http://image.3001.net/images/20160118/145312619545.png)

图 17 BOSS层下发的恶意js

只有当需要攻击的时候BOSS层才会下发攻击指令,而平时只会下发重定向请求重定向到Google首页。

[](http://image.3001.net/images/20160118/14531262055108.png)

图 18 BOSS层下发的正常跳转

**3.4. KEEPER层分析**

除了上述几层,在BBOSS技术架构中,还有一层KEEPER层。截止目已发现多个KEEPER层IP,同样分布在不同国家。这一层肉鸡主要用于对JS层的webshell进行探活、增删修改JS层恶意js内容;对BASE层webshell、
juqery.min.php和jquery-1.9.1.min.php进行探活。同时,还会伴随有对JS层网站后台的暴力破解、弱口令猜解、插件漏洞利用、后台上传带后门插件等一系列入侵行为。对KEEPER层最为活跃的来自阿联酋的IP
85.**.**.78进行分析,其流量趋势如下:

[](http://image.3001.net/images/20160118/14531262168879.png)

图 19 某Zombie Keeper流量趋势

可以发现,该Zombie
Keeper并不是每天都在工作,会阶段性的休息且每次休息间隔时间不同,由此推测Keeper是由攻击者主动启动而非定时自动启动。在1226-1229期间,甚至停止活动了4天。同时,对JS层的请求趋势与对BASE层的请求趋势基本相同。

[](http://image.3001.net/images/20160118/14531262231194.png)

图 20 某Zombie Keeper活跃时间矩阵分析

根据近一个月内该Zombie
Keeper每天的活跃时间,绘制如上的时间矩阵图,横轴为日期,纵轴为小时。将不同天的数据重叠到一天,每个小时在不同天出现的次数越多,颜色越深,从而推断出攻击者每天最活跃时间为20点左右持续到次日早8点左右。显然攻击者不是处于UTC/GMT+8时区,经过不断变化时区来拟合数据,最终发现当采用UTC/GMT-5时区时,不仅最活跃时间符合作息规律,且其他所有数据也都惊人的吻合。

[](http://image.3001.net/images/20160118/14531262402442.png)

图 21 UTC/GMT-5时区

这也印证了前文提到的该Zombie
Keeper在1226-1229的停止活动行为,事实上或许是攻击者在UTC/GMT-5时区下1225-1228期间去圣诞度假了。

**4\. 自查方法**

**1\. 查看前台页面是否被插入如下类型或其它异常的JS代码;**

[](http://image.3001.net/images/20160118/14531262536380.png)

2\. 查看后台源码是否被修改,特别是上述框架文件;

3\. 查看后台是否新增异常的源码文件,是否新增js目录及jquery.min.php等;

4\. 查看站点访问记录是否存在暴力破解等异常访问。

**5\. 修复建议**

1\. 审核是否有可疑的新增用户,修改站点密码;

2\. 清除新增或修改的可疑代码;

3\. 清理不再使用的插件,升级CMS及第三方插件到最新版本;

4\. 增加如防暴力破解,WAF等安全防护措施;

**6\. 总结**

综合上述分析和数据,发现BBOSS组织有如下特点:

1.控制超过12万网站,影响范围辐射全球;

2.技术架构体系高度成熟,多级分层,更易控制和隐藏,有很强的攻防对抗意识;

3.业务灵活,高可配置,不定期更新;

4.危害范围极大,影响数以千万互联网用户。

本文翻译自FREEBUF
[原文链接](http://www.freebuf.com/articles/system/93491.html?from=groupmessage&isappinstalled=0)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **安全客** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/83330](/post/id/83330)

安全客 - 有思想的安全新媒体

本文转载自:
[FREEBUF](http://www.freebuf.com/articles/system/93491.html?from=groupmessage&isappinstalled=0)

如若转载,请注明出处：
[http://www.freebuf.com/articles/system/93491.html?from=groupmessage&isappinstalled=0](http://www.freebuf.com/articles/system/93491.html?from=groupmessage&isappinstalled=0)

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhimg.com/t01546a096e83e700fe.jpg) 安全客

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

