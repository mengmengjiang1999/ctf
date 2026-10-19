  
在之前的文章里《 [这些年iOS AppStore
套壳开发上架过程](http://www.it9188.com/2018/08/23/%E5%88%86%E4%BA%AB%E6%9C%80%E6%96%B0%E9%80%9A%E8%BF%87%E8%8B%B9%E6%9E%9C%E5%BA%94%E7%94%A8%E5%95%86%E5%BA%97%E5%AE%A1%E6%A0%B8%E7%9A%84%E9%A9%AC%E7%94%B2%E5%8C%85%E6%8F%90%E5%AE%A1%E7%BB%8F%E5%8E%86/)》说过了这些年iOS
AppStore 套壳开发上架过程-从棋牌类到彩票类在到如今的金融原油期货类App-过程中所遇到的一些开发问题及解决方案系列一，下面分享第二部分

一次过审总结-包括2.1大礼包

这次这个客户的APP（[精选平台-用户首选](https://itunes.apple.com/cn/app/id1403126683?mt=8)）审核从2018年06月至2018年7月，经历了APP被下架-账号被延审（延时审核）-2.1大礼包-1.2内容反感-过审。期间上传了11个构建版本，无数次邮件沟通，3次电话沟通，与许许多多受害者进行过审经验交流，总之，心力交瘁。下面是详细的过审经历，大家自备尿布。大家也可以参考之前我在2018/06/09
写的《
[RN+SDK套壳轻松解决苹果审核被拒3.2.1问题、2.1大礼包问题【最新上架技术】](http://www.it9188.com/2018/08/23/rnsdk%E5%A5%97%E5%A3%B3%E8%BD%BB%E6%9D%BE%E8%A7%A3%E5%86%B3%E8%8B%B9%E6%9E%9C%E5%AE%A1%E6%A0%B8%E8%A2%AB%E6%8B%923-2-1%E9%97%AE%E9%A2%98%E3%80%812-1%E5%A4%A7%E7%A4%BC%E5%8C%85%E9%97%AE%E9%A2%98/)》

 **1.基本信息**

1.1 客户的APP做的套壳属于直播图书类商城APP。

1.2 马甲

1.3 特意购买了全新的公司开发者账号

 **2.经历**

2018-08-23 12:41，线上版本突然被下架，苹果回复中提到APP存在隐藏功能（hidden
feature），条例为2.3.1，特别说明使用了第三方支付而非内购，条例为3.1.1，而且还说明了下次审核将被延时处理。根据苹果声明凡是APP里使用了虚拟物品，一律使用苹果内购，并且扣去30%的费用。作为开发者肯定希望APP只是使用内购支付，但是基于这30%的税赋，公司的原则是避开，所以才有了审核隐藏支付，上线显示第三方支付。要说明的是，我们的第三方支付还只是通过web支付的，APP内没有集成任何的第三方支付的SDK。另外，我们APP内还隐藏了充值、提现、花费、流水细节功能等。

 **3.第三方支付解决方案**

方案一：还是保留第三方支付，加入内购，另外把充值、花费和流水的部分功能显示出来。

方案二：按照要求的添加内购，去掉隐藏的所有第三方支付。

虽然方案是提出来了，不过公司还是想实施方案一，我等只能再去撞一下墙。为了更好应付苹果审核，我在网上留意了很多趟过坑的小伙伴的经验，有以下建议：在之前有写过关于这个被拒问题的文章，大家可以参考《[上传到App
Store 含第三方支付被3.1.1被拒解决方案](http://www.it9188.com/2018/07/11/shang-chuan-dao-app-store-han-di-san-fang-zhi-fu-bei-3-1-1-bei-ju-jie-jue-fang-an/)》

1.把第三方sdk去掉。

2.去掉代码中所有有关第三方支付的字眼，包括白名单。

3.必须做一下代码混淆。（[混淆工具下载](https://jq.qq.com/?_wv=1027&k=5Ua5UWt)）

最后综合考虑，因为我们APP本身没有携带第三放支付的SDK，所以做了代码清除操作。

 **4.方案实施**

4.1 全局搜索“alipay”等字眼，并做相应的删除或替换。

4.2 更改友盟SDK（使用微信精简版）。

4.3 删掉白名单。

4.4 为了应付上线后，避免再次被复审暴露开关，后台针对访问IP做了处理。

 **5.实现效果**

然后在前几天提交后，到2018年07月18日终于成功重新上架有了结果，在这期间苹果打回，反馈2.3.1，3.1.1条例违法，下次审核将被延时。结果已经不重要了，但是比较蛋疼的说说这一个月我做了什么。首先提交上线后等了一个周后没有任何动静，我就开始进行加急审核操作（后来才知道延审期间，加急是没有任何意义的），然后等了几天状态变为“正在审核”，我以为看到希望了，结果又等了一周，没有任何反应的情况下，我给苹果发了邮件，第一封回了，说您的APP还在审核中，请耐心等待（后来才知道，这是苹果的套路回复），于是我回复了请尽快审核，再没下文，后来继续等，然后隔三差五，我就邮件问候了苹果那边，但是都杳无音信。唯有等。。。

这是第一次被打回，我心里是凉了一截。不过还是礼貌性的回复一下，问其原因，改天便收到反馈：含有第三方支付功能。于是我便客气得套近乎，说明自己真的已经清掉了第三方支付功能，唯有可能的是遗留的注释代码含有第三方支付功能，希望给与过审，其回复：建议清除相关注释，期待重新提交构建版本。此时我心中一万个草泥马在奔跑。

 **6.第二次改版提交**

新增修改：去掉所有有关第三方支付的注释代码。

提交后，还是经历了痛苦的一个半月才有结果，虽然每天早起第一件事依然是打开itune
connect看看状态，但你在束手无策的前提下的每次祈祷都终将破碎，而且变成麻木与绝望。

最终还是悲剧，连回复不知道怎么措辞了，真想直接骂街苹果了。可是我忍，老大拍板，修改优化充值隐藏功能。最终方案是取代审核开关方案，使用js调用web支付。然后便是第三次改版。

 **7.第三次改版提交**

新增修改：优化web支付，添加JS调用。

然后延续前两次操作，除了等，还是隔三差五发邮件过去催。

最后经历了差不多2个月的时候，有了结果，反馈条例是：Guideline 2.1 - Information Needed，我勒个去，直接跳楼算了。

 **8.新年大礼包Guideline 2.1 - Information Needed**

大礼包内容如下：

Guideline 2.1 - Information NeededThis type of app has been identified as one
that may violate one or more of the following [App Store Review
Guidelines](<https://link.jianshu.com?t=https%3A%2F%2Fdeveloper.apple.com%2Fapp-store%2Freview%2Fguidelines%2F>). Specifically, these types of apps
often:1.1.6 - Include false information, features, or misleading
metadata.2.3.0 - Undergo significant concept changes after approval2.3.1 -Have hidden or undocumented features, including hidden "switches" that
redirect to a gambling or lottery website3.1.1 - Use payment mechanisms other
than in-app purchase to unlock features or functionality in the app4.3.0 - Are
a duplicate of another app or are conspicuously similar to another app5.2.1 -Were not submitted by the legal entity that owns and is responsible for
offering any services provided by the app5.3.4 - Do not have the necessary
licensing and permissions for all the locations where the app is usedBefore we
can continue with our review, please confirm that this app does not violate
any of the above guidelines. You may reply to this message in Resolution
Center or the App Review Information section in iTunes Connect to verify this
app’s compliance.Given the tendency for apps of this type to violate the
aforementioned guidelines, this review will take additional time. If at any
time we discover that this app is in violation of these guidelines, the app
will be rejected and removed from the App Store, and it may result in the
termination of your Apple Developer Program account.

一下子回了这么做问题，着实让我一口老血喷死了算了。结果网上一搜，发现一大波同样中毒的同胞，于是找到了失散多年的小伙伴就好说话了，诸位都是来自不同行业，对大礼包2.1有各自不同的见解，我收集了一下：

1)基本中招的来自一下几个行业和类型：马甲、金融小贷、cp（彩票）、游戏、社交和其他。

2)有很大一部分确实存在以上部分问题的（至少是有猫腻的）。

3)2.1大礼包是机审的结果，苹果对机审做了升级处理。

4)有些之前被延时审核的，在收到2.1之后自动解除了延审，例如我的。

至于查看收到2.1之后是否解除了延审，可以留意是否有诸如以下语句

the next submission of this app may require a longer review time或者the next
submission of this app will still require a longer review time

若果有，证明你被延审或者延时审核还没解除。

然后陆陆续续就有人过了，诸如一下这篇

[iOS 2.1 被拒大礼包（审核成功通过）](https://www.jianshu.com/p/8bc0bcd594af)

于是许许多多的猜想得以认证，针对2.1做回复或申述是现行比较合理的解决办法。

 **9.千万别怼2.1**

直接做一下回复

Dear App Review Team,According to your review feedback,I think you may
misunderstand the feature in my app.Firstly,For the 2.3.0、2.3.1、3.1.1, I do
admit and be sorry to use Alipay in my app for the virtual goods in version
版本号. I deservethe punishment that you removed my app from the App Store. But
after that I have removed all the third-part pay in my app instead using in-app purchase to replace it.There are no 'switches' function,no hidden feature
,and any changing undergo significant concept is cause by account function
difference .The second for the 4.3.0,It takes my team more than 4 months to
finish this product, include conception,design and development.I promise that
we have not duplicate any other app.And the third for the 5.2.1,I'm the
developer of my company.My boss always grant me to handle any thing of this
app.The last for the 5.3.4,My app will only release in china, and I have
afforded The Network Culture Management License in the attachment all the
time.Please check it once again.Anything you need in additional or
other,please call me +电话

基本意思是：

对于2.3.0、2.3.1、3.1.1，我承认在上个版本隐藏了支付功能，app被你们下架，这惩罚我罪有应得，但是我在现在的构建版本里已经将第三方支付去掉了，只有内购。也没有什么“隐藏开关”功能。

对于4.3.0，我们团队花了4个月，经过构思、设计、开发才独立研发出来的产品，没有任何抄袭。

对于5.2.1，我是公司开发者，公司授权我对app做任何处理，没有权限法律问题。

最后对于5.3.4，我的app在中国发布，公司已经取得了《网络文化经营许可证》，同时我在审核附件里一致提供着。

最后，过了2天，就有了回馈，真的是喜出望外啊，苦尽甘来。

不过，还是被拒了，回馈是1.2内容违法，并要求提供《网文》的官网地址。

在这一part先说完2.1大礼包的一些其他回复策略吧：

1)直接回复说：没有违反以上任何条例，请重审。

2)回复没见反应之后：直接申述，申述内容与回复一致。

另外补充说明一点：假如你已经回复，并且苹果已经正在受理你的回复内容，你再选择申述，苹果会回馈你说“审核团队已经在认真考虑你的渴求，并将重新审核，请耐心等候，并且下次直接回复即可，本次申述将予以关闭”。也就是说，苹果审核团队已经开始做事了，耐心等候。网上有伙计说，不能回复和申述同时操作，但根据反馈不应该说是“不能”，而是“不需”，无需同时回复和申述，因为一方在处理之后，另一方就不负责你的诉求了。要注意的是，“回复”对接的是审核团队的审核员，“申述”对接的是审核的申述委员会，两个职责是不一样的。不过本人建议，可以再回复之后，两天内没收到消息，即可进行申述。

 **10.第四次提交审核**

1)针对1.2，后台清理了一次数据，包括一些挑逗性的图片和内容。

2)提供了《网文》的官网地址，这个扫描网文的二维码即可获得。

但是还是第3天就被打回来，仍然是1.2。没办法，继续清除，有过3天还是1.2，陆陆续续的清了好几遍，还是不成功，后来采取了终极策略。

 **11.终极过审**

采取策略：联系qq：2205357007付费协助上架app

 **11.一点忠告**

1)对于2.1，最好要耐心，回复文字要礼貌性一点，可中文可英文，最好是英文。

2)马甲包的请慎重，免得封号。作者已成功被封了

3)目前发现解决2.1的可行办法只有回复或申述，至于那些付费过审的请慎重。

4.2 最低功能要求＆4.3 重复 App/马甲包

主要说的是应用简单及重复的问题

 **解决办法**

不愿意换包换账号的情况：

1.修改定价/发布地区/产品分类

2.升级版本号重新提交

3.换 bundle id，换一个包重新审核

愿意换包换账号：

4.更改开发者账号，修改 icon、素材等

5.可以做开关，修改审前页面

6.添加垃圾代码或者注释块

以上是老的办法。

下面另外的亲自最新测试方案

1、定期换电脑提包.

2、换电脑的序列号.

3、换图标,换启动图.

4、换VPN环境.

5、定期换域名.有条件的，最好电脑不要超过三个包

详细分析文章《[这十个步骤让你的 App 避规ios
4.3被拒问题，亲测顺利过审](https://segmentfault.com/a/1190000015365555)》

开发者计划许可协议 1.2被拒问题

金融理财应用

1.若是个人开发者账号提交，尝试换成公司开发者账号提交，在 App 中尽量体现和公司相关的内容、品牌等；

2.将敏感信息（例如 App 中出现的银行名称等）和功能删除或隐藏；

3如果被拒原因中所指出的商标等确实是自家公司的，可以把相关信息和证明资料等反馈给苹果审核人员；

4.（如果开发者账号的邮箱用的是个人邮箱或技术支持网址和公司无关）将开发者邮箱改为公司邮箱，并将技术支持网址改为能体现公司的网址。

其他应用

1.删除被拒理由中明确指出的，或者自身觉得敏感的信息（例如应用名称、关键词或描述中出现的其他应用的品牌词）或功能；

2.提审期间将敏感信息和功能（优惠卷等）隐藏；

3.在 App 以及元数据中多体现和公司相关的内容、品牌等；

4.如果被拒原因中指出的品牌词、商标等确实是自家公司的，可以把信息以及证明资料等反馈给审核人员。

开发者计划许可协议 3.2（f）被拒问题

Apple 开发者计划会员资格被用于不诚实或欺诈活动

1.若是误会，考虑向苹果解释清楚；如是真的，修改后回复苹果承认错误并保证以后不再采取该行为。

2.如果是提交了重复应用而被拒，还可考虑修改应用名称、图标等元数据以及功能、界面，或者去掉代码特征等后，重新提审。或者，直接用新账号提交审核，必要时可考虑修改名称、图标等元数据以及功能、界面等，这样更容易过审。

分析 & 应对措施

从苹果回复的信息以及 Apple 开发者计划许可协议第 3.2（f）节的内容我们不难推测，任何干扰苹果软件或服务的行为都有可能因该理由被拒。

而从统计的近 100 个样本数据来看，今年 2 月份，苹果便开始在审核中频繁使用
3.2（f）来拒绝应用，且被拒应用多是重复提交的应用，或和第三方应用类似的应用。其次是用违规手段操控过榜单排名或评论的应用、以及涉嫌侵权的应用等。

通过样本分析出的现象和 Apple 开发者计划许可协议第
3.2（f）节中的部分举例不谋而合，同时其也帮我们解释了：为什么近期马甲应用提审困难。（→因为苹果加大了对重复提交的应用或和第三方应用类似的应用的审核力度！）

如果因该理由被拒，我们该如何处理呢？作者和群里的一些开发者交流经验后，总结了几点：

1、收到苹果的通知/邮件后，如果是误会，可考虑向苹果解释清楚，然后请求苹果停止处罚。如果真的存在欺骗行为且确认苹果已发现该行为，可考虑（改正后）态度诚恳地回复苹果，承认错误并保证以后不再采取该行为。如果苹果接受了道歉，也许可以解封。但如果苹果态度坚决，就只能另想办法了。（主动承认有一定风险，请综合利弊后，谨慎选择。）

2、如果是提交了重复应用而被拒，还可考虑修改应用名称、图标等元数据以及功能、界面，或者去掉代码特征等后，重新提审。（需要注意的是，据传苹果现在已经开始通过技术手段扫代码，如果只是简单的更改，仍然可能会被拒。）或者，直接用新账号提交审核，必要时可考虑修改名称、图标等元数据以及功能、界面等，这样更容易过审。（注意，如果只是简单的更改，仍然可能被拒，且新账号也有被封的风险
。）

IPv6 相关内容被拒

如果产品因 IPv6 问题被拒，首先要确认代码是否有问题。若确定没有问题的话，重新提交 1~2
次即可，这种情况多数是审核人员所在的网络环境导致的问题（可在重新提交时将截图或拍下视频放附件里或直接向苹果申诉）。

如果 App 本身有问题，例如不兼容 IPv6，最好的办法是让 App 兼容 IPv6 或通过升级服务器来支持 IPv6

解决方案一

苹果AppStore审核员在美国的IPv6-Only环境下对APP进行访问（审核），如果APP Server支持IPv6，则可直接访问；如果APP
Server不支持IPv6，则通过DNS64
+NAT64进行访问；很明显，大部分开发者的APP服务器都是不支持IPv6直接访问的，所以基本是用NAT64+DNS64进行访问的。那么我们就先了解NAT64+DNS64的访问机制吧，直接看图：

![Image](http://www.solve6.com/img/1234.png)  

从这里看出审核的关键在于能不能获取一个有效的Server
IPv6地址。当苹果公司的APP审核员在进行审核时，由于国内大部分开发者的APPserver没有IPv6地址，只能通过苹果公司自己的NAT64+DNS64服务器进行测试，而最关键的是苹果的服务器不能有效的给APPserver返回一个IPv6地址，这就导致了审核失败，APP被拒。

就国内目前来说审核被拒的主要原因有第三个：

1、国内大部分APP服务器没有IPv6地址，导致DNS无法解析；

2、苹果公司的审核环境不能自动将中国APP内URL转换成IPv6可访问的格式，导致访问失败；

3、由于国际线路带宽严重拥堵等原因造成访问不稳定，失败率高

那么该如何解决这些问题呢？

就目前国内的现状，能够提供这种服务的当属教育网了，中国教育网坐拥全国几百所高校，拥有真实的IPv6骨干网络，国际出口，IPv6资源丰富，服务质量好。

因此解决方案就是使用教育网的NAT64+DNS64服务，方案示意图如下：

  

![Image](http://www.solve6.com/img/1112.png)

具体的操作步骤就是使用教育网的NAT64+DNS64，把您的域名发给我们，帮你解析出IPv6地址（全球可达的地址），您只需在您的域名管理中添加一条4A记录即可，之后就可以提交审核了，一天之后你就会发现审核通过了！

解决方案二

既然审核被拒是因为IPV6，那么我们就让服务器支持就可以了，但是很多运营商的服务器不提供IPv6地址，这样的话就要使用IPv6隧道技术,通过建立隧道使自己的服务器通过IPv6隧道来支持IPv6,方案示意图如下：

  

![Image](http://www.solve6.com/img/1215.png)

使用IPv6隧道服务APP服务器必须满足三个条件：

① 服务器拥有公网IPv4地址

② 服务器支持IPv6协议

③ 服务器放行6in4协议

具体的配置如下：（这里只是举个例子）

  

![Image](http://www.solve6.com/img/1216.png)

确认申请了IPv6隧道服务并按照上述模板进行配置完成后，请检查防火墙（iptables）是否放行了6in4协议，并确认(/etc/sysctl.conf)中IPv6转发已打开。如果上述操作都已正确完成，那么在你的服务器上应该可以看到如下结果：

  

![Image](http://www.solve6.com/img/1217.png)

至此，IPv6隧道搭建完毕，服务器已经支持IPv6了这样就OK了

 **5.1 隐私**

1.在采取用户数据信息之前需要给予用户提示，并得到用户的允许，或设置为可选；

2.明确告知苹果采集用户数据信息的使用目的。例：新闻类 App 需要用户位置信息，目的是根据地域的不同而向用户推送不同的新闻内容。

 **5.2 知识产权**

提交产品可以使用受版权保护的第三方的书面证据；将产品中包含的未经第三方授权的部分隐藏。

 **PLA1.2**

一直以来，因PLA1.2问题被拒的多为金融理财应用，但通过近期小七和CP们交流、调查后发现：“PLA1.2”已不再是金融理财应用的专属。在因为此原因被拒的应用中，还有大批购物、医疗及其他类应用。调查详细结果及解决方式如下所示（以下内容围绕金融理财应用、其他应用、马甲应用三部分展开）：

一、金融理财应用

通过调查发现，在因PLA1.2问题被拒的应用中，金融理财应用仍占大部分。被拒原因基本是：应用的开发商名称和公司名称与应用/应用元数据/金融产品中的公司名称/金融机构/金融机构名称/信用卡名称/贷款业务提供者等不匹配，违反了苹果开发者计划许可协议1.2。

如果遇到类似情况，大家不妨尝试下述方式：

①苹果规定：金融理财类应用只能用对应公司名称的开发者账号上传。也就是说，如果用个人开发者账号提交金融理财类应用后收到了类似邮件，可以考虑用公司开发者账号提交；

②如果不想采取上面的方式，且是在帮客户提交应用，可以让客户将你的开发者账号添加到他们的开发者账号团队成员中，然后再尝试提交；

③审核期间，将敏感信息（例如App中出现的银行名称等）和功能删除或隐藏；

④（如果使用的是公司账号却还是被拒）在App中尽量体现和公司相关的内容、品牌等；

⑤如果被拒原因中所指出的商标等确实是自家公司的，可以把相关信息和证明资料等反馈给苹果审核人员；

⑥（如果开发者账号的邮箱用的是个人邮箱或技术支持网址和公司无关）将开发者邮箱改为公司邮箱，并将技术支持网址改为能体现公司的网址（一般用官网即可）。

二、其他应用

在此番调查中，购物应用多是因为在应用以及应用元数据中添加了其他应用的品牌词（例如，淘宝）等，以及开发商和公司名称与App中多次出现的购物平台名称或优惠券服务商等不匹配而被拒；医疗类应用多是因为开发商和公司名称与App中出现的医疗机构等不一致而没有过审；而其他类型的应用被拒的原因多是因为在应用以及应用元数据中添加了其他应用的品牌词，或技术支持网站无法体现该公司的经营内容等。

针对这些情况，小七觉得可以尝试以下方式：

①删除被拒理由中明确指出的，或者自身觉得敏感的信息（例如应用名称、关键词或描述中出现的其他应用的品牌词）或功能；

②提审期间将敏感信息和功能（优惠卷等）隐藏；

③在App以及元数据中多体现和公司相关的内容、品牌等；

④如果被拒原因中指出的品牌词、商标等确实是自家公司的，可以把信息以及证明资料等反馈给审核人员；

⑤（如果开发者账号的邮箱用的是个人邮箱或技术支持网址和公司无关）将开发者邮箱改为公司邮箱，并将技术支持网址改为能体现公司的网址（一般用官网即可）。

三、马甲应用

除了上面的情况外，还有另外一种情况：近日有很多马甲应用收到过此类被拒信息。而针对这种情况，目前主要有两种解决方式：①隐藏敏感信息，并对应用的元数据、图标、界面以及功能等进行修改，过审后再将可修改的信息或功能改回来。但是这样做有一个弊端，如果被苹果发现，会面临下架的风险；②设计一款和主版本不同的App。

结语

解决办法：

一、依照苹果审核人员的要求修改应用名称。

例：公司名称”好贷天下信息技术有限公司“，则App名称修改为”好贷“，然后重新提交。

二、如果是个人开发者，换公司开发者。

三、如果是金融包，尽量用金融账号提交。

四、向苹果证明产品名称与公司的关联性，例如提交”软件著作权“证书，或者”商标“证书，主要为了作为产品名称及公司名称的关联。（所以最好提前申请主包软著）如果没有软著，提供一份证明。

1.有软著的回复

尊敬的苹果开发者审核：

您好，针对贵方提出的 PLA 1.2 品牌归属性问题，我方产品 XXX 为我方 XXX 公司旗下产品，我方开发者账户全称为” xxxxx
有限公司“，附件为我方产品”软件著作权“证书（或者商标），请贵方审阅，及尽快给予我方 App 上架 App Store！

诚挚的问候！

2.无软著的回复以及证明模板

尊敬的苹果开发者审核：

您好，针对贵方提出的 PLA 1.2 品牌归属性问题，我方产品 XXX 为我方 XXX 公司旗下产品，我方开发者账户全称为” xxxxx
有限公司“，但是我方的软件著作权正在申请，附件为我方提供的声明，等软件著作权下来将尽快提交软件著作权证书给贵方，请贵方审阅，及尽快给予我方 App 上架
App Store！

诚挚的问候！

声明模板（需要盖章）

xxx
产品为我公司独立自主开发完成，不存在任何侵犯第三方合法权益的情形。我公司承诺若该应用存在虚假、侵权或侵害第三方合法权益的行为，我公司愿承担由此产生的一切法律后果。

五、向苹果阐述 App 功能及名字情况。

1.准备好技术支持网址，网站内产品功能及情况做相关描述（一般有正常的界面图，App 名称及网站对应公司的名称即可）。

之后回复苹果：

尊敬的苹果开发者审核：

您好，我方产品名称 XXX 为我方公司 XXX
旗下产品，贵方可查阅链接<http://www.xxxx.com>，链接为我方官方网站对外宣传内容，网页内容等均可证实 xxx 产品为我方产品，且不涉及
PLA 1.2 相关问题。

2.回复苹果方公司运营主体，运营范围等。（此条适用于金融包）

六、软件个人中心内增加关于我们一栏，关于我们中可以增加该产品 logo、公司名称、官方网址等一切能证明该产品为该开发者账户。

七、开关功能。（开关能解决的都不叫问题，该隐藏就隐藏）

1.比如金融包上信用卡问题；

2.比如导流包上聚合贷款问题；

3.比如某些功能不被允许问题。

ida逆向：变量、函数标注；反编译代码修改

分析dll文件中的2个函数中变量、函数进行标注，以及反汇编代码修改，（遵循一些约定俗称的规定+自己爱好=形成自己风格）方便以后很快的阅读。

函数1：DllEntryPoint()

汇编窗口

  

![Image](https://img-blog.csdn.net/20180112154320520?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvc2luZ2xleWVsbG93/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)

栈窗口

  

![Image](https://img-blog.csdn.net/20180112154408257?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvc2luZ2xleWVsbG93/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)

反编译窗口

  

![Image](https://img-blog.csdn.net/20180112154443672?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvc2luZ2xleWVsbG93/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)

函数2：Init1( )

汇编窗口

  

![Image](https://img-blog.csdn.net/20180112154604749?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvc2luZ2xleWVsbG93/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)

没有栈窗口

反编译窗口

  

![Image](https://img-blog.csdn.net/20180112154640330?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvc2luZ2xleWVsbG93/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)

清楚的标注，方便以后快速识别样本如何执行。

修改IOS逆向--使用IDA的Patch更改汇编或二进制码并写入项目和deb重新打包举例

小案例需求

加我们有这样一个判断

int i = 4;if(i ==  3){ // 做一些事情}

我们想要把 ==号换为 >=号。当然如果你有源码的话改起来很方便，但是可惜我们没有源码。我写了一个实例deb 进行这样的操作。

//上面的省略CMP x1 #4; // 比较  B.NQ Local_1658 //不相等的话跳到对应地址块 不反回

那么我们会要做的就是讲B.NQ改为B.CC让他做大于等于操作,接下来我们介绍如何进行修改。

. 第一步：

我们需要了解Patch是如何进行使用的。Edit —> Patch program 如下所示

  

![Image](https://image-static.segmentfault.com/424/466/4244660857-5b2de23d415d8_articlex)

.在这里看看他们都有什么

  

![Image](https://image-static.segmentfault.com/330/535/3305357672-5b2de260eebcd_articlex)

change byte … 就是直接修改二进制数值

change word.. 就是直接改地址

Assemble 没用过： 欢迎大家补充

Apply patches to input file: 使我们patch 成功并修改后要写回原文件中此处是我的dylib

如何进行改数值呢？好 我们现在开始

  

![Image](https://image-static.segmentfault.com/231/700/231700052-5b2de29425e0e_articlex)

点击你定位的程序位置，如图 此处是我修改后的内容。 点击这段地址后可以点击Edit —> Patch program –> Change byte
进行更改当前的内容 如图：

  

![Image](https://image-static.segmentfault.com/304/205/3042059575-5b2de2a56b769_articlex)

可以看到我画框的8位数就是我们需要修改的 汇编指令。更改为你想要操作的指令的16进制数值 即可。

当你修改成功后，就可以按之前介绍的内容进行写入文件中。 后面会讲到如何进行重新打包。

Debian 进行重新打包

Debian Linux系统解压和重新打包.deb文件方法，iplaypy.com在网络上搜索问题的答案，找到了类似这样解释：

mkdir -p extract/DEBIANdpkg-deb -x package.deb extract/dpkg-deb -e package.deb
extract/DEBIAN [...do something, e.g. edit the control file...]mkdir
builddpkg-deb - b extract/ build/

以上这五打命令的解释如下：

第一条命令创建了一个名为“extract”文件夹和一个名为“DEBIAN”的子文件夹；

第二条命令会从你的.deb包提取一些文件到“extract”文件夹；

第三条命令会解压.deb包的内容到“DEBIAN”子文件夹，在那里你就可以修改／补丁你想要的文件；

第四条命令建立一个名为“build”的文件夹；

而第五条命令会将修改后的文件重新构建到一个新的.deb包中，并在 “build” 文件夹中生成。

在你执行第三条命令后，可以通过你的默认文件管理器，用一个图形化的文本编辑器可视化地修改文件。

那些能提高你效率的 iOS 应用们

有那么一些 APP，可以提高你在 iPhone 上的工作效率。有的免费，有的需要付费，不知道你愿不愿意去尝试？在这个时代，永远不缺少好的工具。

还有一段话，我觉得还是有必要要说。效率取决于人，真正用好这些工具的可能只是少数人。养成好习惯，比有好工具来的实在。但也请不要过度依靠工具，这样也会造成很严重的后果。

  

**Launch Center Pro**

 **Launch Center Pro**

Launch Center Pro 它对 URL Schemes 的支持，实现了许多 iOS
用户梦寐以求的快速跳转操作和高效率的工作流程（workflow），可以这样说，LCP 是 iOS
上追求效率的朋友必不可少的应用，「能用两步完成的，绝不用第三步」。

下载地址：[https://itunes.apple.com/cn/app/launch-center-pro/id532016360](https://link.jianshu.com?t=https://itunes.apple.com/cn/app/launch-center-pro-shortcut-launcher-workflows/id532016360?mt=8&at=1010luhC)

  

**Workflow**

 **Workflow**

对于一些相对简单的机械式工作，只要交付给 Automator（AppleScript）去完成，,与同类应用 Launch Center Pro
相比，图形化的 Workflow 的操作习惯沿袭了Automator 的风格，「一添加、二拖拽、三选择、四执行、五保存」，简单直观人性化。

下载地址：[https://itunes.apple.com/cn/app/id915249334](https://link.jianshu.com?t=https://itunes.apple.com/cn/app/workflow-powerful-automation-made-simple/id915249334?mt=8&at=1010luhC)

  

**1Password**

 **1Password（免费+内购）**

可以储存管理你所有的密码，并在不同平台不同设备之间同步，只需要在 1Password 中储存一次，你就可以忘掉密码了。支持 iOS 8
的浏览器应用扩展功能，可以在其他 App 中直接调用 1Password 保存的密码，省去了反复查看密码的繁琐。（特别推荐 Mac 版）

下载地址：[https://itunes.apple.com/cn/app/id568903335](https://link.jianshu.com?t=https://itunes.apple.com/cn/app/1password/id568903335?mt=8&at=1010luhC)

TextExpander  

TextExpander

你可以给每一个经常输入的内容设定一个缩写，无论是经常调用的邮箱地址等个人信息，还是篇幅较长的词句，都可以只用一两个字符替代完毕。

下载地址：[https://itunes.apple.com/cn/app/id917416298](https://link.jianshu.com?t=https://itunes.apple.com/cn/app/textexpander-3-custom-keyboard/id917416298?mt=8&at=1010luhC)

 **  
**

**evermemo  
**

 **EverMemo**

可以同步到印象笔记的轻巧笔记应用，如果你只是专注于文字记录，就用 EverMome 吧。

下载地址：[https://itunes.apple.com/cn/app/evermemo/id1175912897](https://link.jianshu.com?t=https://itunes.apple.com/cn/app/evermemo-%E5%8D%B0%E8%B1%A1%E4%BE%BF%E7%AD%BE/id1175912897?mt=8&at=1010luhC)

  

**Ai Search  
**

 **Ai Search**

不仅能谷歌，更有创新的自然语句、标签、多引擎和自定义搜索源，可以直接在通知中心使用「Ai
Search」搜索，随时随地满足你的搜索需求。（个人首屏应用，非常棒）

下载地址：[https://itunes.apple.com/cn/app/ai-search-zhi-neng-sou-suo/id936310061](https://link.jianshu.com?t=https://itunes.apple.com/cn/app/ai-search-%E4%B8%AA%E6%80%A7%E5%8C%96%E6%90%9C%E7%B4%A2%E4%B8%AD%E5%BF%83/id936310061?mt=8&at=1010luhC)

 **  
**

**Drafts  
**

 **Drafts**

顶级文本处理应用，提供了 纯文本、Markdown、社交网络
三种语法高亮主题。可以将你撰写的文本进行多种处理，比如：保存到印象笔记、发送到twitter，功能非常强大，可以 Google 搜索一下测评。

下载地址：[https://itunes.apple.com/cn/app/drafts-4-quickly-capture-notes/id905337691](https://link.jianshu.com?t=https://itunes.apple.com/cn/app/drafts-quickly-capture-notes-share-anywhere/id905337691?mt=8&at=1010luhC)

 **  
**

**Purge  
**

 **Purrge**

Purrge是一个能对系统相册进行操作的相册管理应用。可以快速删除相片。

下载地址：[https://itunes.apple.com/cn/app/purrge/id944628930](https://link.jianshu.com?t=https://itunes.apple.com/cn/app/purrge/id944628930?mt=8&at=1010luhC)

  

**due  
**

 **Due**

Due 是一个非常「快」的应用——快在添加任务和调整任务状态的速度。它也是一个非常强大的应用——提醒功能、URL Scheme 的丰富、对
x-callback-url 的支持等。

下载地址：[https://itunes.apple.com/cn/app/due-kuai-su-ti-xing+ding-shi-qi/id390017969](https://link.jianshu.com?t=https://itunes.apple.com/cn/app/due-%E5%BF%AB%E9%80%9F%E6%8F%90%E9%86%92-%E5%AE%9A%E6%97%B6%E5%99%A8/id390017969?mt=8&at=1010luhC)

  

**ifttt  
**

 **IFTTT**

IFTTT 是 If This Then That 的缩写，它是一个新生的网络服务平台。通俗的来讲，IFTTT
的作用就是如果触发了一件事，则执行设定好的另一件事。

下载地址：[https://itunes.apple.com/us/app/ifttt/id660944635](https://link.jianshu.com?t=https://itunes.apple.com/cn/app/ifttt/id660944635?mt=8&at=1010luhC)

  

**Stacks  
**

 **Stacks**

最便捷的汇率换算应用，可以在通知中心快速进行汇率换算，能将 Safiri 中打开的网页外币迅速转换成另一种货币显示。

下载地址：[https://itunes.apple.com/cn/app/stacks-huo-bi-zhuan-huan-qi/id719162125](https://link.jianshu.com?t=https://itunes.apple.com/cn/app/stacks-%E8%B2%A8%E5%B9%A3%E8%BD%89%E6%8F%9B%E5%99%A8/id719162125?mt=8&at=1010luhC)

  

**clear  
**

 **Clear**

下滑增加一条新的事项，在事项上右滑完成事项，左滑删除事项，上滑清空所有已完成事项，用力下滑返回上级菜单。简单的操作带来的是极致的效率。

下载地址：[https://itunes.apple.com/cn/app/clear-ren-wu-he-dai-ban-shi/id493136154](https://link.jianshu.com?t=https://itunes.apple.com/cn/app/clear-%E4%BB%BB%E5%8A%A1%E5%92%8C%E5%BE%85%E5%8A%9E%E4%BA%8B%E9%A1%B9%E6%B8%85%E5%8D%95/id493136154?mt=8&at=1010luhC)

  

**Clips  
**

 **Clips**

剪切板神器，可以添加 Safari 扩展、通知中心插件、自定义键盘等，让你的剪切板飞起来。可解锁专业版内购：存储不限量的剪辑条目，并可通过 iCloud
在不同的 iOS 设备上同步。

下载地址：[https://itunes.apple.com/cn/app/clips-copy-paste-anywhere/id917638056](https://link.jianshu.com?t=https://itunes.apple.com/cn/app/clips-copy-and-paste-anywhere-with-widget-and-keyboard/id917638056?mt=8&at=1010luhC)

  

**past  
**

 **Paste+**

通知中心小插件，可以对你的剪切板、照片进行一些快速的操作，比如发送到第三方软件内。

下载地址：[http://avaniolabs.com/pasteplus](https://link.jianshu.com?t=https://itunes.apple.com/cn/app/clips-copy-and-paste-anywhere-with-widget-and-keyboard/id917638056?mt=8&at=1010luhC)

  

**iTranslate  
**

 **iTranslate**

同声翻译软件，可以在通知中心上直接翻译剪切板的内容。

下载地址：[https://itunes.apple.com/cn/app/itranslate-fan-yi-zi-dian/id288113403](https://link.jianshu.com?t=https://itunes.apple.com/cn/app/itranslate-%E7%A7%8D%E8%AF%AD%E8%A8%80%E7%BF%BB%E8%AF%91%E5%92%8C%E8%AF%8D%E5%85%B8/id288113403?mt=8&at=1010luhC)

  

**Launcher  
**

 **Launcher**

通知中心启动器，类似 Launch Center Pro。

下载地址：[https://itunes.apple.com/cn/app/launcher/id905099592](https://link.jianshu.com?t=https://itunes.apple.com/cn/app/launcher-%E5%B8%A6%E9%80%9A%E7%9F%A5%E4%B8%AD%E5%BF%83%E5%B0%8F%E9%83%A8%E4%BB%B6%E7%9A%84%E5%90%AF%E5%8A%A8%E5%99%A8/id905099592?mt=8&at=1010luhC)

  

**music launch.  
**

 **Music Launcher**

支持在通知中心添加快速播放项，你可以通过它添加一切可播放的本地音频（歌曲、播客、有声书等）并一键播放。和上面的 Launcher
是同作者开发的，还没下架，建议收一下。

下载地址：[https://itunes.apple.com/cn/app/music-launcher-yin-le-qi-dong/id943240815](https://link.jianshu.com?t=https://itunes.apple.com/cn/app/music-launcher-%E9%9F%B3%E4%B9%90%E5%90%AF%E5%8A%A8%E5%99%A8/id943240815?mt=8&at=1010luhC)

  

**Fantastical  
**

 **Fantastical 2**

日历应用，拥有绝对强大的自然语言输入能力，实用的通知中心小部件（个人认为挺反人类的暂时方式）。在添加日程时，如果你不觉得文字输入是一件麻烦事，会十分顺手。同时，流畅的交互体验，帮助你聚焦于近期的事项。

下载地址：[https://itunes.apple.com/cn/app/fantastical-2-for-iphone-calendar/id718043190](https://link.jianshu.com?t=https://itunes.apple.com/cn/app/fantastical-2-for-iphone-calendar-and-reminders/id718043190?mt=8&at=1010luhC)

  

**Calendars  
**

 **Calendars 5**

日历应用，拥有绝对强大的多视图查看能力，特别是月视图，可以用最直观的方式通览整个月的事项安排，方便一段时间内的规划安排。和待办事项的结合也更加紧密，是实现「Todo
+ Calendar」二合一的最佳选择。但在交互和细节方面逊于 Fantastical 2 不少。

下载地址： [https://itunes.apple.com/cn/app/calendars-5-yu-google-ri-li/id697927927](https://link.jianshu.com?t=https://itunes.apple.com/cn/app/calendars-5-%E6%97%A5%E5%8E%86%E5%AE%9E%E6%97%B6%E5%90%8C%E6%AD%A5-%E7%AE%A1%E7%90%86%E4%BA%8B%E9%A1%B9-%E5%BE%85%E5%8A%9E%E4%BB%BB%E5%8A%A1/id697927927?mt=8&at=1010luhC)

iOS Xcode 安装

1、从
[https://developer.apple.com/downloads/](https://developer.apple.com/downloads/)
下载Xcode的最新版本。

2、双击Xcode dmg文件  

3、将找到的设备安装和打开

4、在这里会有两个项目在显示的窗口中即Xcode应用程序和应用程序文件夹的快捷方式

5、将Xcode拖拽并复制到应用程序

6、在应用里选择和运行程序，Xcode也将成为运行程序中的一部分

还可以从Mac App store里下载Xcode，并按照屏幕上的安装步

界面生成器（Interface Builder）

利用界面生成器这一工具，能很容易的创建UI界面。

可利用一系列的UI元素，拖拽进入UI可视界面。

我们将在接下来的页面了解添加用户界面元素，创建零售商和UI元素的操作。

  

![Image](http://www.runoob.com/wp-content/uploads/2013/11/Xcode_Download.jpg)

在对象库的下方包含有全部必要的UI元素。用户界面通常称为xibs，这是他们的文件扩展名。

每个xibs都链接到相应的视图控制器。

iOS模拟器

iOS模拟器实际上包含两种类型的设备即iPhone和iPad及其不同的版本。

iPhone版本包括iPhone（常规版）、iPhone Retina，iPhone5,iPhone53。

Ipad有iPad和iPad Retina。iPhone模拟器显示如下:

  

![Image](http://www.runoob.com/wp-content/uploads/2013/11/InterfaceBuilder.jpg)

你可以在经度和纬度影响应用程序的位置的情况下运行iOS模拟器，也可以模拟内存警告和呼叫在模拟器中的状态。

能够多数目的使用模拟器，但不能测试像加速度计这样的设备的功能。因此你可能需要iOS设备来测试一个应用程序的所有方面。

下一篇文章将会给大家继续分享“iOS AppStore 套壳开发上架过程-开发小问题（三）”如果帮助到大家，欢迎点个赞收藏哦~如有问题请在下方评论，作者会第一时间回复你  

  

