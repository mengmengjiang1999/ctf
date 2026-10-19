***本文原创作者：薇拉vera，本文属于FreeBuf原创奖励计划，未经许可禁止转载**  

## 写在前面

 **随着AI军备战进入白热化状态，越来越多的行业开始被AI带来的浪潮所影响，甚至颠覆。安全作为和众多行业交叉的一个领域，同样无法避免这样的浪潮。**

但和其他领域不同的是，安全和AI之间其实是一个 **相互作用和碰撞** 的过程——

>  **黑客可以利用AI发起攻击。** 如攻破验证码机制、自动化钓鱼攻击、实现漏洞的自动挖掘等。
>
>  **黑客可以对AI发起攻击。** 如用数据中毒或逃逸攻击干扰模型结果，或是用模型萃取的方法窃取模型或训练集等。
>
>  **安全研究员可以利用AI进行防守。** 如对钓鱼邮件从行为和文本上进行检测、利用图的时候挖掘恶意团伙、对C&C服务器进行检测等。
>
>  **安全研究员需要对AI进行保护。** 如面对恶意机器流量，如何搭建机器流量防控体系，以及旨在保护模型机密性和数据安全的隐私保护技术等。

基于此，本文考虑对AI与安全的恩怨情仇进行一些简单的提纲挈领式的梳理和思考，抛砖引玉。

具体而言，我将AI与安全的关系划分为了五个部分，前四个部分分别从【黑客利用AI进行攻击】、【黑客攻击AI模型】、【安全人员利用AI进行防守】、【安全人员对AI进行保护】角度进行分篇介绍，最后在【Do
we need all in AI ?】部分，给出自己对当前安全现状的一点思考。

整个系列文章的大纲如下图所示，因为字数较多，因此我会将五部曲分为五篇文章，依次进行介绍，欢迎大家共同交流。

![image.png](https://image.3001.net/images/20181014/1539505154_5bc2fc02987b4.png!small)

## Misuse AI

Misuse AI字如其意，即指黑客对AI技术的“误用”。

黑客的攻击行为大多追求规模效应，因此会试图攻击尽可能多的目标用户，同时降低自身的风险。这与AI的思想不谋而合，因此AI便成为了他们实现目标的完美工具。

这里我们主要对以下5种情形进行简单介绍——

> 验证码自动识别
>
> 自动化鱼叉式钓鱼攻击
>
> 自动化恶意软件样本生成
>
> 自动化漏洞挖掘
>
> 通过舆情分析和精准广告投放来影响政治事件

## 00×1 验证码自动识别

验证码识别可能是大家第一反应会想到的一个应用场景，毕竟这个技术几乎自验证码诞生的第一天起就同时诞生了，并一直和验证码缠斗至今。

目前市面上的常见验证码与其对应的攻击手段如下——

###  **1\. 输入识别出的字符类验证码**

![image.png](https://image.3001.net/images/20181014/1539505367_5bc2fcd7b7f10.png!small)

这类实际上主要涉及到的就是图像识别。一般分为 **分割字符** 和 **不分割字符** 两种处理手段。

分割字符手段的步骤：

1.图片预处理,包括二值化,降噪等

2.图片分割

3.提取特征

4.训练分类模型,识别字符

这种方法的难点：

背景噪声难以去除,例如字体上有横线等；

图片粘在一起,难以切割；

文字有旋转,扭曲等变形。

在样本数量不是很大的情况下,这三种情况都会对准确率造成影响,当然如果样本足够多,这些也不是问题

不分割字符的方法：

字符固定：考虑CNN

字符不固定：考虑RNN/LSTM/GRU + CTC。只要数据量足够，准确率就能达到很高的水准。

###  **2\. 点选类验证码**

![image.png](https://image.3001.net/images/20181014/1539505381_5bc2fce5ae5bf.png!small)

这类可以利用目标检测的方法，先从图像中检测出文字，再对文字分类。具体实现可以参照这篇：<https://zhuanlan.zhihu.com/p/34186397>

###  **3\. 拖动滑块到指定位置的验证码**

![image.png](https://image.3001.net/images/20181014/1539505393_5bc2fcf1ca781.png!small)

这类验证码一般不需要打码做训练,只需要找到缺口的位置,并模拟运动轨迹就可以了。具体针对各个平台的破解骚操作的话，可以参考这个知乎回答：[滑块验证码（滑动验证码）相比图形验证码，破解难度如何？——知乎](https://www.zhihu.com/question/32209043/)

## 自动化鱼叉式钓鱼攻击

随着0day成本的升高，黑客们越来越爱用钓鱼来对用户进行攻击。而对于一些“重点目标”，更是会采用一种名为 **鱼叉式钓鱼（spear phishing）**
的办法来定制化处理。攻击者会花时间了解攻击目标，包括姓名、邮箱地址、社交媒体账号或者任何在网上参与过的内容等。攻击目标不是一般个人，而是特定的公司或者组织的成员，窃取的资料也并非个人的资料，而是其他高度敏感性资料。在Black
Hat USA 2016年的议题 **[“Weaponizing data science for social engineering:
Automated E2E spear phishing on
Twitter”](https://www.blackhat.com/docs/us-16/materials/us-16-Seymour-Tully-Weaponizing-Data-Science-For-Social-Engineering-Automated-E2E-Spear-Phishing-On-Twitter-wp.pdf)** 里，研究员尝试用 **SNAP_R** （SocialNetwork Automated Phishing
with
Reconnaissance）递归神经网络模型来向特定用户（即攻击目标）发送钓鱼推文。该模型采用鱼叉式网络钓鱼渗透测试数据进行训练，为提升点击成功率，还动态嵌入了从目标用户和转发或关注用户处抽取的话题，并在发送推文时@攻击目标。

![image.png](https://image.3001.net/images/20181014/1539505413_5bc2fd0518635.png!small)

该自动化鱼叉式钓鱼攻击主要包括两部分：

 **1.寻找钓鱼攻击目标对象**

首先，利用TwitterStreaming
API收集用户名，根据用户个人信息描述和推文情况衡量钓鱼成功概率，用户个人信息包括用户名、转发/响应的推文的频率/时间、对某主题的态度、位置信息、行为模式、已参加或者将要参加的大型活动等，也包括工作、职位头衔、知名度等反映用户价值大小的信息。然后，按照钓鱼成功的概率大小将用户进行分类。

攻击者从Firehose（Twitter用户发送消息的输出口）中挑选用户，并判断该用户属于刚才所说分类方法中的具体类别。如果用户的钓鱼成功的概率比较高，就选取该用户作为攻击目标，向其发送嵌有钓鱼链接的虚假推文。

 **2.自动化鱼叉钓鱼**

选取攻击目标后，攻击者利用SNAP_R递归神经网络模型抽取目标感兴趣话题以及该目标发送推文或者回复推文的情况以便于产生钓鱼推文内容。除介词等停止词之外，最频繁出现的推文内容都可以用于构造推文内容，推文内容会选择用户经常发送或转推推文的时间进行发送。

在SNAP_R模型中，采用了马尔可夫模型和长短期记忆LSTM（LongShort-Term
Memory）递归神经网络构造推文内容。马尔可夫模型根据文本同时出现的概率来推测文本的内容，比如说——

> 如果训练集包含短语the cat in the hat的次数比较多，当模型出现the时，则下一个内容很可能是cat
> 或者hat。但是由马尔科夫模型产生的内容通常是没有意义的，只是出现频率比较高的词语的组合体而已。而LSTM适合于处理和预测时间序列中间隔和延迟非常长的重要事件，与马尔可夫模型的区别在于，LSTM能结合语境判断下一个可能出现的词语。两者结合构造更接近于人类撰写的推文内容。

通过对90名用户进行测试发现：该自动化鱼叉式网络钓鱼框架的成功率为 **30%~60%**
；大规模手动鱼叉式网络钓鱼传统上的成功率为45%，而广撒网式钓鱼只有5%到14%的成功率。测试结果说明该自动化鱼叉式钓鱼方法 **极其有效** 。

 **资料链接：**

Black Hat USA
2016介绍地址：<https://www.blackhat.com/us-16/briefings/schedule/#weaponizing-data-science-for-social-engineering-automated-e2e-spear-phishing-on-twitter-3759>

proposal地址：<https://www.blackhat.com/docs/us-16/materials/us-16-Seymour-Tully-Weaponizing-Data-Science-For-Social-Engineering-Automated-E2E-Spear-Phishing-On-Twitter-wp.pdf>

ppt地址：<https://www.blackhat.com/docs/us-16/materials/us-16-Seymour-Tully-Weaponizing-Data-Science-For-Social-Engineering-Automated-E2E-Spear-Phishing-On-Twitter.pdf>

## 00×2 自动化恶意软件样本生成

论文[Generating Adversarial Malware Examples for Black-Box Attacks Based on
GAN](https://arxiv.org/abs/1702.05983)
利用GAN生成对抗恶意软件样本。最终的实验证明，MalGAN能够将实际中的恶意软件检测率降低到接近零，同时，让defence策略难以起作用。

![image.png](https://image.3001.net/images/20181014/1539505430_5bc2fd16dd1d8.png!small)

其实这一点主要涉及的是对抗样本生成的知识，由于其和第二篇「2」Attack AI
里涉及到的知识点有部分重叠，所以在这里我们先跳过，把这部分内容放到「2」里来讲~

## 00×3 自动化漏洞挖掘

2016年的Defcon CTF上，一支名为 **Mayhem** 的机器CTF战队与另外十四支人类顶尖CTF战队上演了信息安全领域首次人机黑客对战，
**并一度超过两只人类战队** 。而 **Mayhem** 的来历，要从美国国防部先进项目研究局（DARPA，Defense Advanced
Research Projects Agency）举办的网络超级挑战赛（CGC，Cyber Grand Challenge）说起。

CGC是DARPA于2013年发起的全球性网络安全挑战赛，旨在推进自动化网络防御技术发展，即实时识别系统缺陷、漏洞，并自动完成打补丁和系统防御，最终实现全自动的网络安全攻防系统。参赛队伍全部由计算机组成，无任何人为干预。所以，CGC是机器之间的CTF比赛，目标是推进全自动的网络安全攻防系统。

在比赛之前，每支参赛团队需要开发一套全自动的网络推理系统CRS（Cyber Reasoning
System），需要可对Linux二进制程序进行全自动化的分析和发现其中的漏洞，并自动生成能够触发漏洞的验证代码，自动对程序漏洞进行修补。

最终，来自卡内基梅隆大学的ForAllSecure团队研制的Mayhem 系统获得了冠军，并参加了2016年的Defcon CTF。

Defcon CTF上的分数（Mayhem有些可惜，比赛前两天似乎是收到的流量有问题。后来才发现DEF CON CTF Finals用的平台和CGC
CFE不同，第三天收到流量，据说9个CB找出了7个exploit、修补了6个。如果来场公平的较量也许能碾压人类。）

![image.png](https://image.3001.net/images/20181014/1539505472_5bc2fd404945a.png!small)

## 00×4 通过舆情分析和精准营销来影响政治事件

前面提到的几个点，主要还是从传统的安全场景上来进行描述的。但如果黑客想，同样可以利用机器学习技术来影响到更深远的安全领域，比如说国家安全。

在特朗普当选美国总统之后，Cambridge Analytica这家公司便被推到了风口浪尖。这家公司的负责人主动公开宣称Cambridge
Analytica非法获取超过500万Facebook个人账户信息，然后使用这些数据构建算法，分析Facebook用户个性资料，并将这些信息与他们的投票行为关联起来，从而使得竞选团队能够准确识别在两位候选人之间摇摆不定的选民，并有针对性地制作和投放广告。

![image.png](https://image.3001.net/images/20181014/1539505484_5bc2fd4c735a8.png!small)

如上面这个叫做LGBT
United的账号中为威斯特布路浸信会反抗运动打广告。元数据显示，这支广告花了账号持有者3000多卢布，并且它针对的是堪萨斯州的LGBT群体以及那些对希拉里·克林顿或伯尼·桑德斯（民主党竞选人）感兴趣的人。

一家大数据公司尚且如此，那么卷入了干涉美国大选和英国脱欧罪名的俄罗斯呢？

## References

[1] Doug Drinkwater. 6 ways hackers will use machine learning to launch
attacks.

[2] Seymour J, Tully P. Weaponizing data science for social engineering:
Automated E2E spear phishing on Twitter[J]. Black Hat USA, 2016, 37.

[3] Hu W, Tan Y. Generating adversarial malware examples for black-box attacks
based on GAN[J]. arXiv preprint arXiv:1702.05983, 2017.

[4] Nick Penzenstadler, Brad Heath, Jessica Guynn. We read every one of the
3,517 Facebook ads bought by Russians. Here's what we found. USA TODAY.

[5] 科技与少女. 验证码识别综述.

 ***本文原创作者：薇拉vera，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

