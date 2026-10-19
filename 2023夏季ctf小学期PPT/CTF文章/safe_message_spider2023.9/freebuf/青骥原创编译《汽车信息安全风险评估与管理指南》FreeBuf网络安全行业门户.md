  

![3.png](https://image.3001.net/images/20200414/1586850857_5e956c291df30.png!small)

Hi同路人，这里是 **青骥信息安全公益小组** ，上周我们依次介绍了BP系列的[
**《应急响应》**](http://mp.weixin.qq.com/s?__biz=Mzg3MTI0NDQwNg==&mid=2247484041&idx=1&sn=e7920935c5e155004cc29de6394ed460&chksm=ce803590f9f7bc86c340fc6f7f6199eba7947371cf912ce77b4a52db8c32c1841397785431b7&scene=21#wechat_redirect)
**、**[
**《第三方合作管理》**](http://mp.weixin.qq.com/s?__biz=Mzg3MTI0NDQwNg==&mid=2247484062&idx=1&sn=0a0b72b61e5b3730150d7df80b12955f&chksm=ce803587f9f7bc91e0de43b78f6b66d724fc088ee482ce0d2a297ade051493684866b237c25f&scene=21#wechat_redirect)
**、**[
**《威胁检测监控与分析》**](http://mp.weixin.qq.com/s?__biz=Mzg3MTI0NDQwNg==&mid=2247484088&idx=1&sn=f2a1f824e4b18cf064a0b3fdfe197112&chksm=ce8035a1f9f7bcb7485047f3ad7883ba51d50daf8d0ad24d8d05feeff31dd4949e00d4057d41&scene=21#wechat_redirect)
，按照团队运营发布计划，本周我们会继续完成BP的编译和内容介绍工作。本篇将与您分享 **汽车信息安全风险管理** 相关内容，也欢迎大家参阅的 **《**[
**汽车风险评估方法探讨**](https://mp.weixin.qq.com/s?__biz=Mzg3MTI0NDQwNg==&mid=2247483946&idx=1&sn=5c38ff37d7368385d3d0e75d6669e6ce&chksm=ce803533f9f7bc253f2ac73bef66e9b8a5cc19f7b0ddc9c30c7a22c7b00c328ac55001e7067e&token=1718692936&lang=zh_CN#rd)
**》** 。本期统筹编译为 **公益翻译团荣誉创始** **成员** @ **王颖会** **** 同学，校稿为 **荣誉创始** **成员**
******@龚桓毅** 同学，为他们的无私奉献点赞。

– 主理人：李强 _@Keellee_

#
![图片1.png](https://image.3001.net/images/20200414/1586850926_5e956c6e0cba4.png!small)

#  **Q & A**

欢迎大家来到本系列的第四篇技术文章，后台收到反馈，为什么我们总是介绍信息安全管理方面的内容？

其实也并非有意为之，而是受到该系列BP内容本身的局限，既然是业内可公开的最佳实践，更多是方法论方面的经验介绍，而大家所希望的技术细节，确实只是点到为止。但我们还是想继续介绍下去，原因有三：

一是作为信息安全从业人员，我们的思路还是希望大家对于汽车信息安全有个 **整体的概念**
，有了全局的视野和整体的框架思维之后，才能更好的理解我们本职工作的意义以及其周边的衔接关系，  

二是现在国内的信息安全产业还处于起步阶段，国内OEM也在逐步完善内部的信息安全团队，角色定义以及职责分工一定是 **以信息安全业务为牵引**
，对于信息安全部门在人员招聘和岗位设置方面，那就必须要深入的了解信息安全业务的需要，而BP介绍的各要素提供了很好的参考。  

三是信息安全管理本身是件 **重要而不紧急的事情**
。在信息安全业务整体的规划中，它需要领导者对信息安全要素有所了解，对于信息安全业务要有长远的规划，那么该系列BP所提到的内容也是我们业务绕不开的。

不管从专业技术的深入，还是到部门负责人，高层管理，对于信息安全工作的开展，心里还是要有这么一张地图。同时经过青骥信安公益小组内部讨论。目前行业
**所关心的技术热点或要求，后续我们也会陆续深挖并分享给大家**
。下面我们还是要回到今天推文主题《汽车信息安全风险评估与管理》，按照惯例给大家介绍本篇内容的概要。

#  **本 篇 概 述**

本篇重点介绍了产品各阶段的风险管理工作，从业务实际开展的角度对风险管理所涉及的范围、角色与职责，覆盖周期，以及风险容忍度、结果评价和风险处置，以及相应的沟通问题，合规问题。秉承BP一贯的风格，只是方法论和涉及到的关键要点进行了阐述，不拘泥于单一的技术方法。

文档首先介绍了信息安全风险管理的覆盖范围，如果产品的开发模式遵循 **瀑布模型和V模型** ，举例说明了风险评估及管理要涉及到其中 **五个阶段**
：设计、实施和集成、测试、生产和售后服务。

 **设计：**
在早期阶段，对车辆或产品的整体功能概念进行安全风险分析(书面分析)，将有助于考虑资产、威胁向量和行为者，以及由此产生的保护目标。基于书面分析的结果，可以识别网络风险管理的新风险，就总体架构的新需求做出设计决策并达成一致。

 **实施和集成：** 在设计阶段之后，在实施之前，所有需求都可以根据其在实现公司特定保护目标方面的有效性进行衡量，也就是在此过程中开展相关的风险评估工作。

 **测试：**
在测试阶段中，安全性测试里程碑的规划通常考虑修复已识别的漏洞的时间和开发阶段的剩余时间。使用风险评估方法对识别出的漏洞进行评级，并在此基础上对修复工作进行优先级排序。可能无法迅速修复的漏洞，以及新发现的漏洞，可以通过售后服务汽车网络风险管理流程进行处理。

 **生产：**
公司可以考虑在测试阶段结束时执行安全批准，以检查产品安全性，生产阶段的网络安全风险管理不能以生产安全批准为终点。在整个生产过程中保持对安全的关注有助于管理风险环境。经常进行信息安全质量检查，以确保安全措施得到正确实施，且没有未授权的更改被应用。

 **售后服务：**
在产品上市后，进行威胁监控是有用的，有助于识别威胁环境中的新趋势(例如，在黑客场景中，潜在的新兴攻击向量，新发现的漏洞，网络安全事件)。为了实现长期的网络安全产品改进，可以向网络风险评估团队通报新发现的攻击向量，并不断更新组织的网络风险保护目标。除了威胁监控和漏洞管理活动之外，制造商还可以管理可能有影响的售后环境部分的风险，在经销商网络中，服务工具等相关项需要进行设计、生产和维护，以实现适当的安全控制。

介绍完风险评估及管理的覆盖范围之后，然后就是车辆及产品信息安全风险管理过程中角色和职责的介绍。由于产品信息安全团队的结构和成员在不同公司之间可能会有很大的差异，本文档也只是简单的举了示例。

角色包括网络领导者、产品信息安全团队（包括网络风险经理和网络安全分析师），渗透测试团队、应急响应团队、设计团队、开发人员、适当的执行管理者。

 **网络领导者**
被定义为负责领导和管理产品网络安全团队、渗透测试团队和车辆事件响应团队的个人。网络领导者是所有评估结果的推动者，负责将结果传达给感兴趣的利益相关者。

 **产品网络安全团队** 在安全领域通常被称为“ **蓝队”**
。它通常由执行日常网络安全流程的个人组成，包括对概念进行网络风险评估，以及定义新的保护目标以应对不断变化的威胁环境

 **渗透测试团队** 在安全领域中称为 **“红队”**
，定义为对车辆、ECU或功能进行渗透测试的人员。这个团队可能是内部的，也可能是外部的。渗透测试团队与设计团队的分离支持了公正性。它可以减少可能的车辆网络攻击的实用性，从而可以评估产品对网络攻击的鲁棒性。

 **应急响应团队** 的定义是负责对与车辆相关的网络事件进行技术分析，对发现的风险进行评级，并通过生成企业响应来处理事件的小组。

 **设计团队**
是那些从事工程工作，开发或支持正在创建和测试的硬件和软件的开发的人员。设计团队通常负责确保所有者(网络领导者和产品网络安全团队)获得准确的风险评估的评估证据，通常是项目经理。

 **开发人员**
实施由设计团队定义的产品需求。设计团队和开发人员之间的区别是，软件和硬件通常由不同的供应商开发，而功能和规范通常由公司内部设计。根据公司的结构，产品网络安全团队与开发人员直接沟通、讨论漏洞或源代码审计发现并对他们进行网络安全最佳实践教育可能更容易，也可能更困难。

 **公司管理层** 做出的商业决策会影响产品的网络安全。管理团队收到安全部门领导的简报，以便对公司做出最有利的决策。

以上为整体的风险评估管理奠定了基础，接下来的章节介绍了风险评估周期、风险容忍度、结果评价和风险处置建议、与利益相关者沟通问题，以及治理和合规。其中
**可参考细节较多部分为风险容忍度和评价处置建议** ，具体的内容大家可参考文档具体内容，欢迎下载转发。

以上，但愿对您的学习和工作有所帮助，再次感谢您的支持！

\--主编: 杨文昌@VincentYang

#

 __

本文及系列中文编译作品版权归青骥信息安全公益翻译团所有

欢迎您转载分享通过公众号或只是星球回复建议

## 本期全文PDF版本将在本星球独家发布全，预览详见后文

这是我们与您共建共享的公益知识星球，感谢您的持续关注

这里有免费的干货资料 & 200+ 精英小伙伴

每日不间断放送的汽车及信息安全干货&资讯

![640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=](https://image.3001.net/images/20200413/1586764226_5e9419c2c1abf.jpg!small)

## 下为全文预览

![中文_Auto-ISAC-BPs-风险评估与管理最佳实践_青骥信息安全公益小组-v2.3.2_00.png](https://image.3001.net/images/20200421/1587435366_5e9e57663a816.png!small)![中文_Auto-ISAC-BPs-风险评估与管理最佳实践_青骥信息安全公益小组-v2.3.2_01.png](https://image.3001.net/images/20200421/1587435366_5e9e5766514b1.png!small)![中文_Auto-ISAC-BPs-风险评估与管理最佳实践_青骥信息安全公益小组-v2.3.2_02.png](https://image.3001.net/images/20200421/1587435366_5e9e5766b4158.png!small)![中文_Auto-ISAC-BPs-风险评估与管理最佳实践_青骥信息安全公益小组-v2.3.2_03.png](https://image.3001.net/images/20200421/1587435368_5e9e57680f030.png!small)![中文_Auto-ISAC-BPs-风险评估与管理最佳实践_青骥信息安全公益小组-v2.3.2_04.png](https://image.3001.net/images/20200421/1587435376_5e9e577031a26.png!small)![中文_Auto-ISAC-BPs-风险评估与管理最佳实践_青骥信息安全公益小组-v2.3.2_05.png](https://image.3001.net/images/20200421/1587435381_5e9e577526e13.png!small)![中文_Auto-ISAC-BPs-风险评估与管理最佳实践_青骥信息安全公益小组-v2.3.2_06.png](https://image.3001.net/images/20200421/1587435384_5e9e577830fad.png!small)![中文_Auto-ISAC-BPs-风险评估与管理最佳实践_青骥信息安全公益小组-v2.3.2_07.png](https://image.3001.net/images/20200421/1587435387_5e9e577b90146.png!small)![中文_Auto-ISAC-BPs-风险评估与管理最佳实践_青骥信息安全公益小组-v2.3.2_08.png](https://image.3001.net/images/20200421/1587435398_5e9e57863c85d.png!small)![中文_Auto-ISAC-BPs-风险评估与管理最佳实践_青骥信息安全公益小组-v2.3.2_09.png](https://image.3001.net/images/20200421/1587435400_5e9e57888fd54.png!small)![中文_Auto-ISAC-BPs-风险评估与管理最佳实践_青骥信息安全公益小组-v2.3.2_10.png](https://image.3001.net/images/20200421/1587435402_5e9e578a00ffe.png!small)![中文_Auto-ISAC-BPs-风险评估与管理最佳实践_青骥信息安全公益小组-v2.3.2_11.png](https://image.3001.net/images/20200421/1587435405_5e9e578dc3fc8.png!small)![中文_Auto-ISAC-BPs-风险评估与管理最佳实践_青骥信息安全公益小组-v2.3.2_12.png](https://image.3001.net/images/20200421/1587435407_5e9e578fe0ec1.png!small)![中文_Auto-ISAC-BPs-风险评估与管理最佳实践_青骥信息安全公益小组-v2.3.2_13.png](https://image.3001.net/images/20200421/1587435414_5e9e57962f903.png!small)![中文_Auto-ISAC-BPs-风险评估与管理最佳实践_青骥信息安全公益小组-v2.3.2_14.png](https://image.3001.net/images/20200421/1587435415_5e9e5797aff17.png!small)![中文_Auto-ISAC-BPs-风险评估与管理最佳实践_青骥信息安全公益小组-v2.3.2_15.png](https://image.3001.net/images/20200421/1587435418_5e9e579a272f8.png!small)![中文_Auto-ISAC-BPs-风险评估与管理最佳实践_青骥信息安全公益小组-v2.3.2_16.png](https://image.3001.net/images/20200421/1587435424_5e9e57a09793c.png!small)![中文_Auto-ISAC-BPs-风险评估与管理最佳实践_青骥信息安全公益小组-v2.3.2_17.png](https://image.3001.net/images/20200421/1587435425_5e9e57a16b081.png!small)![中文_Auto-ISAC-BPs-风险评估与管理最佳实践_青骥信息安全公益小组-v2.3.2_18.png](https://image.3001.net/images/20200421/1587435429_5e9e57a53265c.png!small)![中文_Auto-ISAC-BPs-风险评估与管理最佳实践_青骥信息安全公益小组-v2.3.2_19.png](https://image.3001.net/images/20200421/1587435431_5e9e57a73f7dc.png!small)  

![微信图片_20200412003255.gif](https://image.3001.net/images/20200413/1586764967_5e941ca735b24.gif!small)

[青骥原创编译 |
《汽车信息安全威胁检测监控与分析指南》](https://mp.weixin.qq.com/s/M0Pe3b4YYgJXs1ZHa6zBAA)

[青骥原创编译 | 《汽车信息安全应急响应指南》 ](https://mp.weixin.qq.com/s/NwL4GW8Xb-6kbapv3u6GIA)

[青骥原创编译 |
《汽车信息安全执行摘要》中文编译版本概述及全文首发](https://mp.weixin.qq.com/s/nixAKqOWnTYh55k1RweovA)

[创事记 | 除了免费放送100+的公益资料干货之外，我们还想
…](https://mp.weixin.qq.com/s/nixAKqOWnTYh55k1RweovA)

[行业标准 |
网络数据安全标准体系建设指南](http://mp.weixin.qq.com/s?__biz=Mzg3MTI0NDQwNg==&mid=2247483981&idx=1&sn=bb7242bf70116034c11f9e03c3c2cb04&chksm=ce803554f9f7bc42e7089b2829ee82354ed42c564d121ad38492cdb19ea93929646b9ea38cb1&scene=21#wechat_redirect)
[技术文章 l
汽车数字钥匙解决方案](http://mp.weixin.qq.com/s?__biz=Mzg3MTI0NDQwNg==&mid=2247483974&idx=1&sn=3881e32d7675fa0a001dfbbe5b0f1210&chksm=ce80355ff9f7bc49b958ca3c597aea8ddfd42ae96579b27bd1fa7dfa041b349383eccf60c61d&scene=21#wechat_redirect)

[标准介绍 l
车载网络设备信息安全技术要求](http://mp.weixin.qq.com/s?__biz=Mzg3MTI0NDQwNg==&mid=2247483957&idx=1&sn=b533888f56712d05ffca3e4bffe9b542&chksm=ce80352cf9f7bc3a49f47966c1bb62f3f6863126ca3feff7787aaddf4d2e2a949aa970a6d9ef&scene=21#wechat_redirect)[汽车风险评估方法探讨](http://mp.weixin.qq.com/s?__biz=Mzg3MTI0NDQwNg==&mid=2247483957&idx=1&sn=b533888f56712d05ffca3e4bffe9b542&chksm=ce80352cf9f7bc3a49f47966c1bb62f3f6863126ca3feff7787aaddf4d2e2a949aa970a6d9ef&scene=21#wechat_redirect)

[重磅发布：2020全球智能网联汽车信息安全报告](http://mp.weixin.qq.com/s?__biz=Mzg3MTI0NDQwNg==&mid=2247483919&idx=1&sn=bab2196bbdee1f63a73b98375e1a1bf8&chksm=ce803516f9f7bc0001313d4f98e1472dc52c6d88b1879a8f792d9139ae1e253e5c353c40f45b&scene=21#wechat_redirect)

[信息安全龙头“360”被曝裁员，比例为15%到20%？](http://mp.weixin.qq.com/s?__biz=Mzg3MTI0NDQwNg==&mid=2247483874&idx=1&sn=04e7fdb9e2e3d907e5be2e3d215d5efc&chksm=ce8036fbf9f7bfed599e3bd6c0daa00e51e486cf674aa59b176343e10c343bbf81c7e7138f7e&scene=21#wechat_redirect)

[Hackers Can Clone Millions of Toyota, Hyundai, and Kia
Keys](http://mp.weixin.qq.com/s?__biz=Mzg3MTI0NDQwNg==&mid=2247483868&idx=1&sn=eb154c0a13ebabddda29e9e52a7aa504&chksm=ce8036c5f9f7bfd37211808dcda8f14a24044a5c12b5a662dea7a17d3617950b6527dac55c1d&scene=21#wechat_redirect)

[《网络与信息安全学报》最新论文：基于同态加密和区块链技术的车联网隐私保护方案](http://mp.weixin.qq.com/s?__biz=Mzg3MTI0NDQwNg==&mid=2247483864&idx=1&sn=a13a7a15b650257e5d74a774b0a9629e&chksm=ce8036c1f9f7bfd71abd211c002e1885ccc66c6f1f6944ec1eded73dcc88d1be38fa95457904&scene=21#wechat_redirect)

[《网络与信息安全学报》最新论文：基于通信特征的 CAN
总线泛洪攻击检测方法](http://mp.weixin.qq.com/s?__biz=Mzg3MTI0NDQwNg==&mid=2247483849&idx=1&sn=d7f066631d01f889965824d15c013f66&chksm=ce8036d0f9f7bfc660cae002b10e3cc3fac1dc40d8fdbb88b68e04e9186ea83d1ad4caa5526b&scene=21#wechat_redirect)

[青骥原创编译 |
《汽车信息安全威胁检测监控与分析指南》](https://mp.weixin.qq.com/s/M0Pe3b4YYgJXs1ZHa6zBAA)

[青骥原创编译 | 《汽车信息安全应急响应指南》 ](https://mp.weixin.qq.com/s/NwL4GW8Xb-6kbapv3u6GIA)

[青骥原创编译 |
《汽车信息安全执行摘要》中文编译版本概述及全文首发](https://mp.weixin.qq.com/s/nixAKqOWnTYh55k1RweovA)

[创事记 | 除了免费放送100+的公益资料干货之外，我们还想
…](https://mp.weixin.qq.com/s/nixAKqOWnTYh55k1RweovA)

[行业标准 |
网络数据安全标准体系建设指南](http://mp.weixin.qq.com/s?__biz=Mzg3MTI0NDQwNg==&mid=2247483981&idx=1&sn=bb7242bf70116034c11f9e03c3c2cb04&chksm=ce803554f9f7bc42e7089b2829ee82354ed42c564d121ad38492cdb19ea93929646b9ea38cb1&scene=21#wechat_redirect)
[技术文章 l
汽车数字钥匙解决方案](http://mp.weixin.qq.com/s?__biz=Mzg3MTI0NDQwNg==&mid=2247483974&idx=1&sn=3881e32d7675fa0a001dfbbe5b0f1210&chksm=ce80355ff9f7bc49b958ca3c597aea8ddfd42ae96579b27bd1fa7dfa041b349383eccf60c61d&scene=21#wechat_redirect)

[标准介绍 l
车载网络设备信息安全技术要求](http://mp.weixin.qq.com/s?__biz=Mzg3MTI0NDQwNg==&mid=2247483957&idx=1&sn=b533888f56712d05ffca3e4bffe9b542&chksm=ce80352cf9f7bc3a49f47966c1bb62f3f6863126ca3feff7787aaddf4d2e2a949aa970a6d9ef&scene=21#wechat_redirect)[汽车风险评估方法探讨](http://mp.weixin.qq.com/s?__biz=Mzg3MTI0NDQwNg==&mid=2247483957&idx=1&sn=b533888f56712d05ffca3e4bffe9b542&chksm=ce80352cf9f7bc3a49f47966c1bb62f3f6863126ca3feff7787aaddf4d2e2a949aa970a6d9ef&scene=21#wechat_redirect)

[重磅发布：2020全球智能网联汽车信息安全报告](http://mp.weixin.qq.com/s?__biz=Mzg3MTI0NDQwNg==&mid=2247483919&idx=1&sn=bab2196bbdee1f63a73b98375e1a1bf8&chksm=ce803516f9f7bc0001313d4f98e1472dc52c6d88b1879a8f792d9139ae1e253e5c353c40f45b&scene=21#wechat_redirect)

[信息安全龙头“360”被曝裁员，比例为15%到20%？](http://mp.weixin.qq.com/s?__biz=Mzg3MTI0NDQwNg==&mid=2247483874&idx=1&sn=04e7fdb9e2e3d907e5be2e3d215d5efc&chksm=ce8036fbf9f7bfed599e3bd6c0daa00e51e486cf674aa59b176343e10c343bbf81c7e7138f7e&scene=21#wechat_redirect)

[Hackers Can Clone Millions of Toyota, Hyundai, and Kia
Keys](http://mp.weixin.qq.com/s?__biz=Mzg3MTI0NDQwNg==&mid=2247483868&idx=1&sn=eb154c0a13ebabddda29e9e52a7aa504&chksm=ce8036c5f9f7bfd37211808dcda8f14a24044a5c12b5a662dea7a17d3617950b6527dac55c1d&scene=21#wechat_redirect)

[《网络与信息安全学报》最新论文：基于同态加密和区块链技术的车联网隐私保护方案](http://mp.weixin.qq.com/s?__biz=Mzg3MTI0NDQwNg==&mid=2247483864&idx=1&sn=a13a7a15b650257e5d74a774b0a9629e&chksm=ce8036c1f9f7bfd71abd211c002e1885ccc66c6f1f6944ec1eded73dcc88d1be38fa95457904&scene=21#wechat_redirect)

[《网络与信息安全学报》最新论文：基于通信特征的 CAN
总线泛洪攻击检测方法](http://mp.weixin.qq.com/s?__biz=Mzg3MTI0NDQwNg==&mid=2247483849&idx=1&sn=d7f066631d01f889965824d15c013f66&chksm=ce8036d0f9f7bfc660cae002b10e3cc3fac1dc40d8fdbb88b68e04e9186ea83d1ad4caa5526b&scene=21#wechat_redirect)

  

本站欢迎投稿并提供 **免费定制化行业资料搜集** ,反馈建议及合作烦请关注公众号

（星球提问或微信 **后台回复关键词：资料获取** ）

再次感谢您关注“汽车信息安全” 相关动态，目前本站除了公众号之外，还有同名的FreeBuF专栏、知识星球、微博以及头条号

希望伴君一路同行，做汽车信息安全知识的践行与传播者

![01.jpg](https://image.3001.net/images/20200410/1586505157_5e9025c54a5b0.jpg!small)

