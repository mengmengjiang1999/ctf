2020年2月24日-28日，网络安全行业盛会RSA
Conference将在旧金山拉开帷幕。在RSAC官方宣布入选今年创新沙盒十强初创公司中，绿盟君已经为大家介绍过了ElevateSecurity
、Sqreen、AppOmni、Tala
Security、ForAllSecure、INKY、BluBracket、VulcanCyber八家厂商，今天为大家介绍的是：
**Securiti.ai** 。

一、公司介绍

Securiti.ai成立于2018年11月，总部位于美国加利福尼亚州的硅谷地区。当前融资总额达到8100万美元，最近一次是由General
Catalyst领投，Mayfield参与的5000万美元B轮融资。其创始人兼CEO是Rehan
Jalil，拥有丰富的网络安全从事经验和管理背景，先后在Elastica和Bluecoat担任CEO，后在赛门铁克云安全部门担任高级副总裁。公司致力于实现隐私合规的自动化，利用AI和People
Data Graph等先进技术，使得隐私合规遵循从传统的繁琐手工操作到一站式的自动化成为可能，以帮助企业快速满足GDPR和CCPA等法律法规。

2020年1月1日，CCPA（《加州消费者隐私法案》）正式生效，如何快速地且有条不紊地满足该隐私法案，这是众多硅谷巨头（Google、Facebook和Apple等）以及中小企业的一大痛点问题。在此背景下，Securiti.ai凭借应对方案以及技术实力入选2020年RSA大会创新沙盒的前十强。值得一提的是，BigID作为隐私数据治理（遵循GDPR），在2018年的创新沙盒夺得冠军；Securiti.ai作为一家同样主打隐私合规产品（可遵循CCPA）的创新公司，是否能赢得今年RSA创新沙盒的冠军？值得期待！

二、背景介绍

为了保障公民的个人信息与隐私安全，全球掀起了隐私法规的立法热潮。2018年5月25日，欧盟正式颁布《通用数据保护条例》（General Data
Protection Regulation，GDPR）用以保护欧盟成员国境内企业的个人数据、也包括欧盟境外企业处理欧盟公民的个人数据。受GDPR
影响，全球各个国家推出了类似的个人信息保护法规，如巴西LGPD、印度PDPB、泰国PDPA等。我国于2017年6月1日正式实施《网络安全法》，并于去年发布《数据安全管理办法（征求意见稿）》，对个人信息安全提出诸多规定和约束。2019年10月，美国加州州长正式签署《加州消费者隐私保护法》（California
Consumer Privacy Act，CCPA）的最终法案，于今年1月1日正式生效。

从GDPR的执法来看，违反的罚款代价是高昂的。例如，法国于2019年1月份罚款Google公司5000万欧元，原因是Google的隐私条款的设计非常难以被用户理解，尤其是在个人化广告推荐上；英国在2019年7月份分别对英航和万豪集团分别开出1.83亿英镑和9900万英镑的罚单，原因均为企业数据防护措施不力导致了数据泄露；德国对网络公司Delivery
Hero处以20万欧元罚款，原因是客户要求删除个人数据时，却没有及时性应答。对于CCPA的实施，据IAPP和OneTrust的CCPA
Readiness调查结果显示，74%的受访者认为他们的雇主应该遵循CCPA，但遗憾的是，仅大约2%的受访者认为他们的企业已经完全做好了应对CCPA的准备。

这些隐私法规迫使企业对以下一些问题进行思考：存储那些消费者的个人数据？它们分布在那些系统中？是否满足立即响应客户的数据访问权、更新权和删除权等权利？如何解决跨多个应用程序与第三方共享的数据问题？对于多数企业来说，这是一系列的合规性痛点问题。Securiti.ai正抓住这一普遍诉求，并且利用AI和People
Data Graph等先进技术，使得繁琐的处理流程变得更加自动化。

三、公司产品与方案

 ** _01_**

产品介绍

Securiti.ai的产品称为Privaci，公司CEO
Jalil将其描述为“PrivacyOps”解决方案，并亲自写一本书对产品功能和架构思想进行介绍[6]。Jalil
将PrivacyOps概括为它是哲学、实践、跨功能协作、自动化和业务流程的组合，它提高了企业组织可靠且快速地遵守众多全球隐私法规的能力。通俗地说，传统隐私合规性的请求处理是手动的、缓慢的，而PrivacyOps可实现批量地、自动化地处理规性请求，并可定期评估与检测合规性风险，能够帮助企业快速满足全球隐私法规遵循的要求。

公司官网中展示了PrivacyOps的五个子产品：Data Fulfillment Automation、PD
LinkingAutomation、Assessment Automation、 Third Party Risk
Assessment和ConsentLifecycle。为了更好地理解，绿盟君将五种产品归为三类：前两者为应对消费者数据权利（访问权、修改权和更新权等）请求响应的合规处理产品、后两者是合规性风险评估类产品、最后一个为数据授权处理的合规性检查类产品。

Data Fulfillment Automation

CCPA和GDPR等隐私法规赋予数据主体（消费者）数据访问、修改和删除等权利，比如在CCPA的1798.100条款中，规定“企业收到消费者访问个人信息之请求后，应当立即通过邮寄或电子等方式向消费者披露和传送所要求的数据”；GDPR也有类似规定，要求企业必须在一个月内对所有请求进行响应，若请求过于复杂，可延长到两个月。该合规场景可解读为企业需提供两点功能：

1、为消费者提供数据权利请求的窗口；

2、收到请求立即或者在规定时间内进行响应。

假设一天有1000个用户请求，若采取手动操作，查询相关系统，并手工制作1000个用户的个人信息数据报告，这个工作量是巨大的，且容易产生操作错误。因此亟需一种流程自动化的方法。

Data Fulfillment Automation（数据权利履行自动化）产品可实现消费者数据权利请求-响应的流程自动化处理，并且可生成合规性审查报告。其产品运行流程如下：

1、构建一个或多个动态请求表单并嵌入到客户的网站中，类似于一个网站插件。通过这个插件，可轻松接受数据主体的请求（DataSubject Request,
DSR）。

2、收集DSR请求，并根据用户的身份创建DSR工作流程。为了避免错误处理和欺诈，该过程需验证用户的身份。下图显示John A.
用户希望查看网站收集自己那些数据，除数据访问外，还可对收集的个人数据进行编辑、甚至删除。

![https://mmbiz.qpic.cn/mmbiz_png/IpYUt4DIvZeedwPiagiaQxGbld6iaiaiaskicQDq8UqWhUQU7F0AaknicRibvwibz28ocE1eCZicmut5vj5UsA40iab8ia91kQ/640?wx_fmt=png](https://image.3001.net/images/20200221/1582286373_5e4fc625aeb5d.png!small)

3、DSR工作流程提交给后台，后台有机器人助手Auti，可关联到用户John A.的数据，帮助完成DSR任务并且同步系统。

4、生成DSR履行的审查报告，以证明遵循隐私合规。

PD Linking Automation

PD Linking Automation（个人数据链接自动化）产品通过强大的数据管理能力及People
DataGraph技术，可将企业在不同时间、不同系统收集和存储的某个数据主体所有相关数据进行关联，比如数据主体的IP地址、***号、***号、照片、出生年月、住址和收入等个人信息。

![https://mmbiz.qpic.cn/mmbiz_png/IpYUt4DIvZeedwPiagiaQxGbld6iaiaiaskicQxojUQ1lLCJDQHN0OC7R1ocmzQkqe62ibN0jQfLStA4gkX3zuVStIhUA/640?wx_fmt=png](https://image.3001.net/images/20200221/1582286381_5e4fc62d6e42c.jpg!small)

根据PrivacyOps book的详细介绍，该关联技术的应用产品主要有以下三种应用场景：

1、辅助前面产品Data Fulfillment
Automation，生成个人数据的关联报告。比如，用户向比如Google提出访问个人信息的请求后，Google有多个产品与系统，在浏览器服务器记录用户注册信息和Cookie信息，另外在邮件服务器中也记录了同一用户的个人信息，这两个系统存储的同一个数据主体的信息，但多数企业不会将两个系统进行关联。但GDPR和CCPA要求企业向消费者披露数据主体的相关个人信息，因此关联技术十分重要；

2、跨国企业的个人数据的治理与可视化。跨国企业的数据存储、处理服务器分布全球各地，若将个人信息主体的信息进行关联，并关联到用户的国籍或居住地（欧盟、美国加州），可视化获得数据分布的世界热图，更好地洞察不同国家地区法规的合规性风险；

3、数据泄露后的及时通知受影响的数据主体。例如，对于个人信息数据库（假如无邮件、电话等联系信息）的泄露，通过关联邮件、电话等信息，可快速通知泄露的用户，满足合规性要求。

通过向聊天机器人Auti提问，可触发操作流程实现自动化执行，并生成宏观的个人数据地图和审查报告。

![https://mmbiz.qpic.cn/mmbiz_png/IpYUt4DIvZeedwPiagiaQxGbld6iaiaiaskicQOjuYRNGIxNGjhRzp3sz6EGnJqerPfI2dxMviazPDBSVc9hlhdM4C6sQ/640?wx_fmt=png](https://image.3001.net/images/20200221/1582286390_5e4fc6364b4a4.png!small)

Assessment Automation

Assessment
Automation（内部评估）可为企业内部的系统进行隐私风险评估。产品系统内置不同的合规性模板，如GDPR、CCPA，每一种合规性模板对应各种合规点检查列表和问题。为了高效地完成隐私风险的评估，产品提供了一个协作平台，通过它内部多位安全专家可分工对问题进行检查和回复。协作平台收集所有的输入和检查，最终生成评估报告。一旦报告生成，企业可选择与第三方组织或消费者分享，以证明隐私风险控制能力。

![https://mmbiz.qpic.cn/mmbiz_png/IpYUt4DIvZeedwPiagiaQxGbld6iaiaiaskicQm65ohpibg8F2q3xYicEKK5MoK7m1aw5fLkUp7JB0iaKicFwrIRDWPU9EMQ/640?wx_fmt=png](https://image.3001.net/images/20200221/1582286397_5e4fc63d9db2c.png!small)

Third Party Risk Assessment

在GDPR中，有两个重要的数据处理组织：数据控制者（Controllers）和数据处理者（Data
Processor），数据控制者是数据主体的第一联系人，负责数据的收集与处理，数据处理者在多数场景下是第三方组织。例如，一家零售机构（数据控制者）采集用户信息，它租赁亚马逊云服务器（数据处理）进行数据的存储和计算。按照GDPR法规，零售‘机构的法规责任更大，必须慎重挑选挑选数据处理者，以确保它由能力通过适当的技术和组织措施以满足GDPR的要求。CCPA也有类似的规定，当企业与第三方进行个人信息的交互时，第三方发生违发数据行为时，当事企业也承担一定法规责任。特别在大型公司，拥有多个合作商，数据交互和流通越来越大，为了降低法规风险，不仅需保证内部满足隐私合规，也需确保合作的第三方是可信任的，隐私风险控制水平达到安全级别。

Third Party Risk
Assessment（第三方组织的风险评估）很好解决以上的一个痛点，它可以同时邀请与企业合作的多个第三方组织，共同接入评估平台进行隐私风险评估，它尽可能利用可获取的数据，包括各个网站的隐私声明（privacy
statements），第三方组织安全专家提供合规性证明和检查文件。该产品在生成评估报告同时，也提供了一个统一的隐私风险评分服务。

![https://mmbiz.qpic.cn/mmbiz_png/IpYUt4DIvZeedwPiagiaQxGbld6iaiaiaskicQSLnozCn5x7icnC6VSPyMWvbFW4WBMcS7Liaiab83j4wpI6Uiasmv6uTf2g/640?wx_fmt=png](https://image.3001.net/images/20200221/1582286404_5e4fc644b116e.png!small)

Consent Lifecycle

Consent
Lifecycle（许可生命周期管理）产品可应用与网站的Cookie的数据收集，征求用户的同意，对标多个GDPR、CCPA等法规的数据处理与利用的公开透明原则。首先，提供服务的企业需在自身网站中部署Consent
Lifecycle相关插件，如下图所示，它提供了用户授权设置的一个窗口。然后，用户可在设置盘中授权网站的Cookie信息授权应用于那些目的，比如数据分析、广告推荐、社交发现，提供给第三方组织C1企业或C2企业等。那么，如果用户没有授权Cookie信息用于广告，而服务企业却在后台的广告推荐系统利用了该Cookie信息，那么Consent
Lifecycle将监控到这一异常行为，在后台触发告警行为，以通知企业停止违反法规的风险行为。

![https://mmbiz.qpic.cn/mmbiz_png/IpYUt4DIvZeedwPiagiaQxGbld6iaiaiaskicQCJz7dQ7ssYuxVSyibC1YMEakVonvv03pxznicwtiaEgBrNRgJzuYQg31w/640?wx_fmt=png](https://image.3001.net/images/20200221/1582286412_5e4fc64c0b850.png!small)

**_02_**

合规性方案

前文介绍的公司的五个产品，它们进行组合可对标到CCPA（美国加州）、GDPR（欧盟）和LGPD（巴西）隐私合规条款，公司的官网分别提供三种隐私法规遵循的解决方案。下面以CCPA的解决方案为例，对产品功能与对标合规点进行简单介绍，详细合规功能点可访问官网。

![https://mmbiz.qpic.cn/mmbiz_png/IpYUt4DIvZeedwPiagiaQxGbld6iaiaiaskicQ4icdU4yh1uia8wictTg0Ehms5SqtJ7Lm86IITibxG28A39YmRws0XGfSBw/640?wx_fmt=png](https://image.3001.net/images/20200221/1582286422_5e4fc6561ea6c.png!small)

数据主体请求DSR自动化处理

CCPA规定消费者具有数据访问、更新、删除的权利。当用户提出合理的权利诉求，PrivacyOps方案可自动化收集、接收以及处理数据主体请求（Data
Subject Request,
DSR），并自动生成DSR报告。具体对标CCPA的1798.100、1798.105、1798.110、1798.115的数据访问权相关条款。这些规定了企业收到消费者访问个人信息之请求后，应当立即通过邮寄或电子等方式向消费者披露和传送所要求的数据，否则视为违反法规。

![https://mmbiz.qpic.cn/mmbiz_png/IpYUt4DIvZeedwPiagiaQxGbld6iaiaiaskicQs2qx8PBKd4nNzcj8OWMDEiaibaByTFXSrcIIruhAexSxm0e2U0CjPlDw/640?wx_fmt=png](https://image.3001.net/images/20200221/1582286428_5e4fc65cb511c.png!small)

隐私风险评估

通过使用协作的、准备就绪的PrivacyOps评估系统来衡量企业组织的隐私合规性，识别差距并处理风险，以保持符合CCPA监管要求。具体对标CCPA的1798.135.(1)(2)相关条款，要在互联网主页或隐私政策的醒目清晰位置，提供一个命名为“不得出售我的个人信息”，消费者有选择不出售个人信息数据的权利。

![https://mmbiz.qpic.cn/mmbiz_png/IpYUt4DIvZeedwPiagiaQxGbld6iaiaiaskicQnvjbZpxWBbyvOPZVrlUPpMJOl3GT9SqGls1x51F0cesAvDBGHdwJ8Q/640?wx_fmt=png](https://image.3001.net/images/20200221/1582286438_5e4fc666897d5.png!small)

个人数据自动链接

发现所有系统中存储的个人信息，并将其链接到个人数据的所有者。通过身份可视化数据蔓延，并基于受试者居住地识别合规风险。CCPA监管的是处理加州居民个人数据的营利性实体，即美国加州外的其他州、甚至国外的跨国企业处理加州居民的用户数据，将受到相关法规风险影响。该功能可视化展示宏观的风险分布位置，对标CCPA的治理和监管要求。

![https://mmbiz.qpic.cn/mmbiz_png/IpYUt4DIvZeedwPiagiaQxGbld6iaiaiaskicQeicKl2cKDNM3EtZianPbLUAn3L2TLcSicgMZC8pgll6XglYcjUefzhGGg/640?wx_fmt=png](https://image.3001.net/images/20200221/1582286446_5e4fc66e88491.jpg!small)

除以上合规要求外，PrivacyOps方案还可满足用户选择不出售数据的权利、默认不选择、检测隐私说明等合规性要求。

四、总结

欧盟GDPR在2018
年正式实施，2019年进入全面执法，多张巨额的企业罚单相继被开出。美国加州隐私法规CCPA在今年1月1月已经生效，与GDPR一样，CCPA同样是一项十分严格的隐私法规，赋予了消费者更多数据权利，比如访问权、修改权、删除权和不出售数据给第三方等，同时提出了企业履行的义务条款。比如，企业收到消费者要求访问个人信息的请求后，应立即采取措施（比如信件或电子方式）向消费者免费披露和提供本节所要求的个人信息（GDPR也有类似的条款）。如何快速地满足遵循CCPA，这是众多硅谷巨头（Google、Facebook和Apple等）以及中小企业面临的一大痛点问题。违反法规意味着罚款与处罚，GDPR罚款的上界是2000万欧元或者4%全球营业总额，而CCPA可具体到每一个消费者，罚款上限为750美元（同时被1万人起诉，那么相当于罚款750万美元）。值得注意的是，GDPR不仅对欧盟，CCPA不仅对美国加州的企业，只要处理欧盟，或者加州的居民的跨国企业，同样将受到法规的域外监管与约束。

Securiti.ai瞄准了这一个普遍的隐私合规性市场与需求，将繁琐的合规性遵循变成了智能的、自动化的处理，可满足企业满足隐私合规的大部分需求。具体来说，Securiti.ai具有以下亮点与优势：

1、融资数额8100万美元是创新沙盒前十强最高的数额
（第二名ObsidianSecurity为2950万美元）。仅成立1年多就拿到多家投资机构的基金，这从侧面说明公司的发展前景和技术实力；

2、提供的产品较为丰富，官网展示了1年的时间就发布了5种合规性产品。从官网介绍，公司目前拥有130名员工，同时在人员扩充中，开发迭代速度非常快；

3、产品可快速组合为解决方案，目前提供CCPA、GDPR和LGPD（巴西隐私法规）的合规性方案；

4、公司的技术创新能力不可小觑。公司掌握了People Data
Graph自主技术，将多个分散的个人信息关联到同一个数据主体中，在学术称为“实体识别”问题，这是一个棘手的技术难题，Securiti.ai宣称可将云、数据库、大数据系统等异构数据源关联识别出来，这是一大创新；另外公司利用NLP技术，利用聊天机器人Auti提供友好、不枯燥的处理辅助功能。

Securiti.ai凭借实用的、自动化的合规遵循解决方案、以及不可小觑的创新实力，同时在CCPA今年实施的热点背景下，绿盟君看好Securiti.ai，让我们拭目以待！

· 参考链接 ·

参考资料

[1]<https://www.crunchbase.com/organization/securiti-ai#section-overview>

[2] SECURITI.ai Selected asFinalist for RSA Conference 2020 Innovation
SandboxContest.<https://privaci.ai/press-release/securiti-ai-selected-as-finalist-for-rsa-conference-2020-innovation-sandbox-contest/>

[3] Securiti.ai Homepage.<https://securiti.ai/>

[4] 2019网络安全观察.<http://blog.nsfocus.net/wp-content/uploads/2020/01/2019-Cybersecurity-Insights.pdf>

[5]<https://iapp.org/resources/article/ccpa-readiness-survey/>

[6] PrivacyOps book.<https://www.privaci.ai/request-book>

