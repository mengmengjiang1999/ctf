![008.jpg](https://image.3001.net/images/20200616/1592309204_5ee8b5d4ed0a6.jpg!small)**  
**

**1\. 什么是汽车资产？**

百度说，资产是指由企业过去的交易或事项形成的、由企业拥有或者控制的、预期

会给企业带来经济利益的资源。

****说，an asset is somethingvaluable or useful.

ISO
27001说，信息资产的定义是对组织有价值的知识或数据，也就是说，这些知识和数据能够给组织带来经济利益或具有应用的价值，是组织赖以生产的根本，或者是企业的核心竞争力，是需要制定策略和技术手段进行保护的资产。

ISO21434说，An asset is something for which thecompromise of its cybersecurity
properties can lead to damage to an item’s
stakeholder(资产是指违背其网络安全属性会导致相关的利益相关者受损的事物)

从汽车信息安全的角度来说，汽车的资产就是与车辆相关，有价值的，且容易遭到黑客攻击，对Stakeholder的安全、隐私、财产或操作性造成损害的物件，不仅仅只是车辆本身，从整个车辆生态简单来说，也包括云、管、端（云服务器、通讯网络、车载端）。

作为汽车设计人员，我们无法完全有效预测黑客的攻击手段，也就只能基于已有的攻击手段和安全事件，不断迭代开发经验，基于一定的攻击假设，建立车辆的防护体系，

从汽车端来说，车上动辄上万个零部件，每个零部件都很重要，那么从信息安全角度来说，到底哪些是需要重点保护的呢？我们首先要做的就是资产定义，按最新的ISO
21434里面也就是相关项定义（Item Definition）。

在ISO
21434的历史版本里，还提到了候选资产（对项目相关利益者有潜在价值。如果候选资产的任何相关安全属性的损失可能会对项目的相关利益者造成潜在的损害，则候选资产有资格成为资产）。至于item和Asset之间的关系，大致可以用下图来表示：

![007.png](https://image.3001.net/images/20200616/1592308911_5ee8b4af62786.png!small)  

 **2\. 如何识别资产？**

前面对于汽车资产的定义进行了阐述，想必大家对于资产有了大致的印象，那么从信息安全专业角度来说，我们到底该如何判定一个item是不是资产呢？

对于车辆本身而言，挡风玻璃，轮胎，后视镜，玻璃水算不算资产？对于汽车来说肯定是资产，每个都有用且有价值，但是对于黑客来说是否有攻击的价值呢？当然没有，不然就不叫黑客了，那就是普通的强盗和小偷了。在这里就不得不引出相应的安全属性了。

一般而言，会采用经典的CIA三个安全属性进行潜在威胁场景的识别，从安全属性破坏之后产生的后果，确定资产的重要程度以及对应的安全策略（定义来自CISSP认证考试指南）

 **机密性** Confidentiality **：**
确保授权的用户能够对数据和资源进行及时和可靠的访问，也就是重要信息不会泄露（eg：候选资产的保密性损失，客户个人偏好的泄露可能导致损害场景，即泄露的个人信息可能在未经客户同意的情况下被滥用（用于他们不同意的目的）。

 **完整性Integrality：**
保证信息和系统的准确性和可靠性，并禁止对数据的非授权更改，接收到的信息不会（eg:制动ECU(电子控制单元)收到的信息不完整，可能会对制动功能的正常工作产生不利影响，对车内人员造成身体伤害(伤害或死亡)。

 **可用性Availability：** 确保授权的用户能够对数据和资源进行及时和可靠的访问

![008.png](https://image.3001.net/images/20200616/1592308929_5ee8b4c11e529.png!small)  

通过识别候选资产的安全属性，确定可能的损害场景，从而判定为资产，具体的操作思路如下，最新的ISO 21434已经不再这么提，但以下思路方法是没有问题的。

![009.png](https://image.3001.net/images/20200616/1592308992_5ee8b50049956.png!small)  

 **3\. 智能网联汽车的到底资产有哪些？**

前面，我们从理论逻辑的角度对汽车资产的识别做了阐述，那么汽车的资产到底有哪些呢？我们还是想参考之前的推文《智能汽车安全良好实践》的内容，盘点下，对于一般的智能网联汽车而言，资产到底涉及有哪些?

![010.png](https://image.3001.net/images/20200616/1592309018_5ee8b51ae1155.png!small)  

以上就是参考《ENISA good practices for security of smart
cars》中列举的资产，只是原文中以列表的形式呈现，我们进行了翻译，并以思维导图的形式呈现。按照信息安全传统的“云管端”角度出发，基本覆盖了大部分内容。云对应服务器、系统和云计算系统，管主要指通信方式，端包括车载内部通信组件，

那么可以说说传统观念之外的资产。

资产里面怎么会有人？如果不特意解释其实也很难理解，毕竟人到哪里都是重要资产，对于汽车而言，如果是L5自动驾驶车辆，主驾和副驾的人就会成为重要的资产，当然还包括OEM员工和操作工，他们有权限接入车辆，不管是远程，还是物理的。

移动设备，比如IPAD和手机，由于可能拥有装有汽车的应用程序，自然也是汽车资产的一部分。还有核心的算法，整车的功能执行单元等等。

![001.PNG](https://image.3001.net/images/20200616/1592309033_5ee8b529b4849.png!small)![002.PNG](https://image.3001.net/images/20200616/1592309033_5ee8b529cc891.png!small)![003.PNG](https://image.3001.net/images/20200616/1592309033_5ee8b5299f1db.png!small)![004.PNG](https://image.3001.net/images/20200616/1592309034_5ee8b52a3ac3c.png!small)![005.PNG](https://image.3001.net/images/20200616/1592309035_5ee8b52b12068.png!small)![006.PNG](https://image.3001.net/images/20200616/1592309034_5ee8b52a6c7c2.png!small)

**主 编：杨文昌** ********@**** Vincent Yang

 **主理人** **：李 强** @Keellee

* * *

 **  
本站欢迎投稿并提供免费定制化行业资料搜集**
（后台回复关键词：资料获取）![640?wx_fmt=gif&tp=webp&wxfrom=5&wx_lazy=](https://mmbiz.qpic.cn/mmbiz_gif/Qo8XMCd7XbHDia2H2fW49FB4wzAEZszsgvYX6wptJoSIXQStw1Pe1lViakVibNoNy8fM2fBib5clAfj7sQEn5rz4HQ/640?wx_fmt=gif&tp=webp&wxfrom=5&wx_lazy=1)

[ **青骥原创编译 l 《智能汽车安全良好实践》Part
Ⅱ**](http://mp.weixin.qq.com/s?__biz=Mzg3MTI0NDQwNg==&mid=2247484916&idx=1&sn=1eb71df41797fbbdcf497b9f9f6b0b14&chksm=ce8032edf9f7bbfb43e19773e661f8e920e36adb40f93d5a96331c079d46faaa13ac8d542833&scene=21#wechat_redirect)
青骥原创编译 l 《智能汽车安全的良好实践》Part Ⅰ[ **公益课堂 l ISO/SAE
21434标准概要介绍视频课程**](http://mp.weixin.qq.com/s?__biz=Mzg3MTI0NDQwNg==&mid=2247484999&idx=1&sn=896ef333c1afffe4b6e855214fb2de15&chksm=ce80315ef9f7b84801be599e796dd0f05fee8585bf921fc38fdb4ec901a08bc46d6befb2d37e&scene=21#wechat_redirect)[
**公益课堂 l
车联网信息安全攻防实践视频课**](http://mp.weixin.qq.com/s?__biz=Mzg3MTI0NDQwNg==&mid=2247484938&idx=1&sn=0aaec4a2aa903be498ecd3fabc6e7477&chksm=ce803113f9f7b805fd5755d8869f6257a77c26bc1fdf7c035d76bfa6e0077dab10a8fbeb4032&scene=21#wechat_redirect)

[ **顶层设计 |
《车载信息交互系统信息安全技术要求》要点概览**](http://mp.weixin.qq.com/s?__biz=Mzg3MTI0NDQwNg==&mid=2247484639&idx=1&sn=8074e66b1ccdc801ec871a8d5feff839&chksm=ce8033c6f9f7bad01a486d3a09f25b64850546522a73af39f53e34b7e4bdd525510306cf4edf&scene=21#wechat_redirect)[
**顶层设计 |
《汽车网关信息安全技术要求》要点概览**](http://mp.weixin.qq.com/s?__biz=Mzg3MTI0NDQwNg==&mid=2247484634&idx=1&sn=b354a442419a01816b11fbfef514b98e&chksm=ce8033c3f9f7bad579a93a233c2a33eeefb95e07088576db24364e6e13ffd4e8aee1d1982d61&scene=21#wechat_redirect)[
**顶层设计 |
《自动驾驶数据安全白皮书》要点概览**](http://mp.weixin.qq.com/s?__biz=Mzg3MTI0NDQwNg==&mid=2247484628&idx=1&sn=45b4387bd969c79491cadf032bc9e2fa&chksm=ce8033cdf9f7badb12f7eccaa9e0d4cdf6772957d6c994dd009689d370c6f124954e2c800a8a&scene=21#wechat_redirect)[
**前沿技术 |
KasperskyLab智能汽车安全研究报告**](http://mp.weixin.qq.com/s?__biz=Mzg3MTI0NDQwNg==&mid=2247484562&idx=1&sn=613f944e81212174d075d94ac4403467&chksm=ce80338bf9f7ba9d1019e9ecf7f15db780b3a14262050d67ed488f517cf084c563fbf8fe3465&scene=21#wechat_redirect)[
**前沿技术 |
OWASP固件安全测评指南**](http://mp.weixin.qq.com/s?__biz=Mzg3MTI0NDQwNg==&mid=2247484519&idx=1&sn=b282c92013be82754ecc57acdf9b9b97&chksm=ce80337ef9f7ba68f916cfef6427afdd593e1aa4bd6c860fe50b2ead49774188bd0af92ea51a&scene=21#wechat_redirect)

[ **青骥原创 l
关于ISO27001文档编制及实践难点**](http://mp.weixin.qq.com/s?__biz=Mzg3MTI0NDQwNg==&mid=2247484457&idx=1&sn=c568a884242a08581f1ef55523524964&chksm=ce803330f9f7ba267bde1c5687a65b6a732e464e450f566feffff0bc000d7121cf947bc55c5d&scene=21#wechat_redirect)[
**青骥原创 l 关于ISO
27001及其实施难点**](http://mp.weixin.qq.com/s?__biz=Mzg3MTI0NDQwNg==&mid=2247484436&idx=1&sn=44dd07aeede3e9dcd4399bf238bbf2e7&chksm=ce80330df9f7ba1be487eadfc71f24e8bf037e81acfc7e29a2b297628ffea5661c37790d3ddf&scene=21#wechat_redirect)

[ **青骥原创 | 关于车载T-BOX的安全防护**](http://mp.weixin.qq.com/s?__biz=Mzg3MTI0NDQwNg==&mid=2247484411&idx=1&sn=2e9bbd6f78cdcf582f4120908de87226&chksm=ce8034e2f9f7bdf4f4da0b452c235edcd419abf0bf78b428ff1594d91d37778ebe721d795ea0&scene=21#wechat_redirect)[
**青骥原创 |
关于TISAX的简要介绍**](http://mp.weixin.qq.com/s?__biz=Mzg3MTI0NDQwNg==&mid=2247484426&idx=1&sn=09b77d17829ffbaa9977c01ddbc51927&chksm=ce803313f9f7ba05c6d7e0414595d4d7e151c7f934b2b089340d4ccf31cfa6116973c4b3c85c&scene=21#wechat_redirect)

[ **创事记 | 除了免费放送100+的公益资料干货之外，我们还想
...**](http://mp.weixin.qq.com/s?__biz=Mzg3MTI0NDQwNg==&mid=2247483999&idx=1&sn=f83ad7c529a9653616123e8ee9eae639&chksm=ce803546f9f7bc5050b5231f49565cb9486a1ca0e10e9f27346d02e658af4bd613b031b18e84&scene=21#wechat_redirect)

 **诚邀关注同名FreeBuf专栏** **：** **汽车信息安全**

希望伴君一路同行

 **做汽车** **信息安全知识的践行者与传播者**

