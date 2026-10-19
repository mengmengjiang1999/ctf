_大家好，我是 **零日情报局** 。_

 _本文首发于公众号 **零日情报局** ，微信ID： **lingriqingbaoju** 。_ ****

从银行木马到网络犯罪帝国，Emotet出现至今已成为当前最具危险性的恶意软件之一，并流窜全球。

而Twitter上，却有一个自发的安全小组锁定Emotet木马，以一种近乎偏执的坚持，夜以继日地展开追踪近两年之久，如今他们已成为圈内最懂Emotet的白帽团队之一。

**这个白帽团队就是Cryptolaemus。**

这回，零日就跟大家聊聊Cryptolaemus白帽团队针对Emotet木马“追着锤”的故事。

****

# **Emotet** **：洗劫全球的银行木马**

Emotet一款经久不衰银行木马，2014年已开始在德国、瑞士等全球各大银行肆虐，长期为幕后黑手窃取大笔资金。

![image001.png](https://image.3001.net/images/20200306/1583471153_5e61da3106df1.png!small)

（CISA发布Emotet威胁公告）

洗劫各大银行后，具有自我传播与暴力访问特性的Emotet，从银行木马进阶为恶意软件“加载器”，成为黑客团伙全球分销恶意软件的利器。

自此， **Emotet木马又成了勒索病毒、加密矿工、信息窃取等恶意攻击的先行军。**
其背后黑客组织Mealybug，更借Emotet木马出租业务，全方位筑起了黑客犯罪的商业帝国。

 ****

# **累计跟踪5万+恶意IP，白帽团队执着追杀Emotet**

Cryptolaemus白帽团队自2018年9月12日，在自己的团队官网（[https://paste.cryptolaemus.com/](https://paste.cryptolaemus.com/)）发布第一份Emotet木马追踪IoC以来，至今已坚持累计发布了超过230份IoC文档。

我们随意点开这些文档，发现他们的每一次发布，平均披露超200+个Emotet木马的命令服务器IP地址，以及上千条恶意文档的传播链接。
**换言之，两年来，Cryptolaemus所追踪的恶意IP超过5万个。**

同为安全研究员，相信大家和零日一样，都明白如此庞大体量的追踪数据背后，不仅是持续不断的技术输出，更是安全员近乎偏执的坚持。

![image003.png](https://image.3001.net/images/20200306/1583490309_5e622505b8f38.png!small)  

细看Cryptolaemus白帽团队网站持续更新的IoC文档，会发现专业程度丝毫不输于各大专业网络安全团队，更有让Emotet无处遁形的趋势。

比如他们会 **详尽地罗列出每次发现的Emotet命令服务器IP地址，数量多达百余个：**

![image005.png](https://image.3001.net/images/20200306/1583490332_5e62251ce16b7.png!small)![image007.png](https://image.3001.net/images/20200306/1583490333_5e62251d0e22c.png!small)  

比如轻则过千的Emotet恶意文档传播链接：

![image009.png](https://image.3001.net/images/20200306/1583490354_5e62253254d4a.png!small)  

或是传播Emotet的文件HashBusting：  

![image011.png](https://image.3001.net/images/20200306/1583490376_5e6225483eeed.png!small)![image013.png](https://image.3001.net/images/20200306/1583490376_5e62254855f80.png!small)

  

这些仅从数量上就需要耗费大量时间的追踪数据，Cryptolaemus白帽团悉数全网免费共享，任何人都可以直接进入Cryptolaemus网站查阅。

除此以外， **Cryptolaemus白帽团队还是个Twitter的高产博主。** 他们的推特账号@
Cryptolaemus1日均更新5+条推文，交流转发无数；在内容上，更是把Emotet扒得透透得。想知道的Emotet新动向，都能在Cryptolaemus官推找到，找不到的直接@提问，更能得到专业答复。

**首先是，实时共享网站IoC：**
Cryptolaemus白帽团队Twitter实时共享网站IoC追踪文档，并针对IoC情况，分享Emotet僵尸网络更新、垃圾邮件等内容，提醒关注者更新Emotet拦截列表。  

![image017.png](https://image.3001.net/images/20200306/1583490428_5e62257c7014c.png!small)

**其次，他们还会在线解惑：**
作为安全圈公认的Emotet“盯梢人”，白帽Cryptolaemus自然收获了大批技术同行的关注，而他们也不吝指教，随时在线就Emotet木马进行讨论。

  

答疑内容不仅有文字版：

  

![image018.png](https://image.3001.net/images/20200306/1583490451_5e622593230b8.png!small)  

还有技术演示版：

![希望清晰.gif](https://image.3001.net/images/20200306/1583490463_5e62259f06cc0.gif!small)  

甚至不乏写满代码的干货版：

![image020.png](https://image.3001.net/images/20200306/1583490476_5e6225ac72eb4.png!small)![image021.png](https://image.3001.net/images/20200306/1583490476_5e6225ac81a78.png!small)  

**当然，推文还少不了他们的Emotet追踪思路：**
毕竟每天都专注在Emotet的追杀中，自然对如何捕捉Emotet行踪相当有心得，所以在他们的推特里，经常能看见追踪Emotet的新思路新手段新发现，关注者发现新的溯源技术手段，也会第一时间@Cryptolaemus共享。

![image023.png](https://image.3001.net/images/20200306/1583490505_5e6225c9ce258.png!small)![image024.png](https://image.3001.net/images/20200306/1583490505_5e6225c9e6516.png!small)

现今，这群因兴趣相投目标一致的网友，组成的Cryptolaemus白帽团队，既有大公司的IT管理员，也有网络安全公司职员，而在Cryptolaemus网站也能看到这20名成员的Twitter账号。

**Cryptolaemus 白帽团队成员Twitter名单：**

@0xtadavie @Bauldini @benkow_ @CholeVallabh @DecayPotato@devnullnoop
@dmfroberson @dms1899 @James_inthe_box @Jan0fficial @JRoosen@lazyactivist192
@MalwareTechBlog @mploessel @neonprimetime @noottrak@pollo290987 @prsecurity_
@ps66uk @unixronin @_FirehaK

**Emeritus members: @JayTHL**

![image026.png](https://image.3001.net/images/20200306/1583490528_5e6225e0a9096.png!small)  

  

至于这全凭兴趣的20人团队，坚持阻击Emotet的成果也有着相当大的成效。

**“反作用”Emotet幕后势力：**
Cryptolaemus长期追踪发现，Emotet恶意软件团伙会在白帽团队IoC报告发布第一时间，浏览并迅速做出策略调整。夜以继日不间断的攻防博弈，让Emotet幕后势力成为Cryptolaemus的密切关注者。

**执法与网络安全公司关注：**
Emotet在成为恶意软件加载器后，一直是网络安全圈的毒瘤。而Cryptolaemus白帽团队的专注，也让越多越多的执法部门与网络安全公司关注起Emotet威胁。
****

# **零日反思**

 ****

一群用兴趣与爱发电的技术达人们，因为共同目标，开启了全网阻击Emotet的征程。

也许区区数百份IoC不能直接消灭Emotet，但不可否认，这群白帽的行动，切实的阻碍了Emotet威胁的进一步扩散。其中的坚持与追求，也许正是万千白帽Hacker的缩影。

**零日情报局作品**

微信公众号： **lingriqingbaoju**

如需转载，请后台留言

欢迎分享朋友圈

**参考资料：**

 **ZDNet-** **《与全球最危险恶意软件Emotet对抗的白帽团体》**  
  

![后缀动图.gif](https://image.3001.net/images/20200219/1582082557_5e4ca9fd876b4.gif!small)

