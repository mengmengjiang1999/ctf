## **01** **什么是“安全”？**

当前在汽车领域，关于安全，我们时常可以听到这几个词：功能安全，预期功能安全，信息安全，网络安全等。那这些概念到底是什么意思？他们之间的区别又是什么呢？

首先，我们先来聊一下“安全”一词。中文的“安全”可以有两个英文单词与之对应：safety和security。这两个单词在牛津词典及维**科中的解释如下所示。

![v2-cf9d6905777ca84c85f8c07acf34ee9d_720w.jpg](https://image.3001.net/images/20220610/1654830789_62a2b6c58131e80d6ffb1.jpg!small)表格1
safety及security的一般含义解释

在通常情况下，两种安全均可表示为一种没有受到伤害、威胁、破坏的状态。而对于security一词，维*中的解释特别指出了这是一种没有受到来自其他人/外部（caused
by
others）的伤害。一种比较常见的观点是，safety指的是一种没有受到伤害的状态，不管这种伤害是故意造成的还是非故意造成的。而security指没有受到故意原因造成的伤害。

##  **02** **汽车行业中的几个“安全”**

在汽车行业中，关于各种安全的定义，各个相关的行业标准及指南中都给出了明确的定义。

与safety相关的概念及定义原文如下表所示。

![v2-26efe57fd22180e53a3a0dbe6e3d606e_720w.jpg](https://image.3001.net/images/20220610/1654830789_62a2b6c5e5a33101ae798.jpg!small)表格2
汽车行业标准及指南中对safety相关概念的定义

其中，safety指一种没有受到伤害的一种状态，这种伤害可能会对生命、财产、环境造成损失，这是一种系统可以正常地按照设计者意愿工作的状态。功能安全（functional
safety）指没有具有不合理风险的危害的状态，这些危害是由电子电气系统的故障行为造成的。预期功能安全（SOTIF）同样指系统没有具有不合理风险的危害的状态。预期功能安全与功能安全的区别在于：前者的危害情况是由于系统的功能性不足（如系统的设计或本身性能限制、设计时对运行情况的认识不足等）以及合理的可预见的误操作造成的，而后者的危害情况是由系统本身的电子电器系统的故障行为造成的。当前行业中，主要依据ISO
26262(2018)系列标准及ISO/PAS
21448:2019标准，来执行对车辆及相关系统的功能安全和预期功能安全的设计、实施、验证等全生命周期中的安全管理。

在汽车行业中，与security相关的就是一个概念，即网络安全（cybersecurity），下表中列出了与汽车网络安全相关的行业标准、指南及法规中，对网络安全的定义。

![v2-ca0ce366685bf2dec45a81d8aaeebb73_720w.jpg](https://image.3001.net/images/20220610/1654830790_62a2b6c68760a9ba98e33.jpg!small)表格3
汽车行业标准、指南及法规中的网络安全概念定义

在SAE
J3061指南中，网络安全指系统漏洞不被允许利用的一种状态，一旦这些漏洞被利用，即系统的网络安全状态遭到破坏，则会导致例如生命、财产、隐私、操作性等方面的损失。ISO/SAE
21434及WP.29
155中对网络安全一词的定义较为类似，其主要指所关心的资产受到了足够的保护，以免受到一些威胁的伤害。此处的资产指任何对利益相关者有价值的东西，包括车辆、车辆功能、电子电器部件等。

为了进一步明确上述汽车行业中各个安全概念的定义、关键概念、范围及相互关系，作者设计了一种汽车行业“安全”概念映射图，如下所示。

![v2-408eef2afacc38a864667463b8bee53c_720w.jpg](https://image.3001.net/images/20220610/1654830790_62a2b6c6e7ccea646fa23.jpg!small)图1
“安全”概念映射图

“安全”概念映射图主要从两个维度对术语中的关键元素进行分类，其分别为“造成危害的原因”（caused by）以及“可能导致的危害结果”（cause harm
to）。

上图中的横坐标为“造成危害的原因”。其中，“系统”（system）表示由系统本身的原因而造成危害。例如，由于设计缺陷或随机硬件失效造成的系统功能失效。由设计不足而造成的预期功能不足也属于这一类型。“人类”（human）表示由人的因素而造成危害，该类还可以细分为两个子类，其分别为“人为失误”
(human error)和“人为误操作” (misused by
human)。前者表示这一失误行为是人非故意为之的，并且可能会导致系统的行为超出可接受的范围[9]；而后者表示该行为是操作人员有意为之(没有恶意目的)，但该行为是系统制造者所不希望的[6]。“环境”（environment）包括了外部物理环境(如温度、湿度)以及系统运行的先决条件(如正确的传感器输入数值)。“攻击”（attack）表示了任何想要暴露、改变、使工作禁止、破坏、偷窃、非法进入或非法使用一个资产的企图[10]
。横坐标中的前三项是由非恶意原因造成的危害，而最后一项危害原因是来自于外界的恶意行为而造成的。

图中的纵坐标表示了三类可能导致的危害结果。对人类生命造成的物理伤害(如骨折、外伤、死亡等)属于第一类危害结果，即“人类生命”（human
lifes）。第二类“财产”（properties）包括了经济及信息方面的损失，前者表示该危害导致财产的所有者需要支付额外的费用，后者则表示与信息安全相关的后果，如知识产权泄露，用户隐私暴露等。“环境”（environment）是指供人类与其他地球生命生存的自然环境。有毒气体的释放和造成资源浪费等情况属于这类的危害结果。

根据上述的横纵坐标分类，可将各个行业规范或指南中的“安全”概念映射其中，以方便理解各个概念的含义、范围及相互关系，为后续的安全设计、开发等工作提供清晰的概念理解。

##  **03** **safety-critical 系统及security-critical 系统**

除了safety与cybersecurity两个概念本身之外，SAE J3061中还提及了两个与之相关的概念，即safety-critical
system与security-critical system。这两个概念的原文定义如下所示。

![v2-1523a11d82188b4b1366df62e2ee0cc5_720w.jpg](https://image.3001.net/images/20220610/1654830791_62a2b6c73a6004abb5406.jpg!small)表格4
safety-critical及cybersecurity-critical系统概念定义

Safety-critical系统是指：如果该系统没有按照所设定的、或所预期的行为运行，将会导致生命、财产或环境受到伤害的系统。Cybersecurity-critical系统指：如果该系统被通过系统漏洞被入侵破坏，将导致经济、操作性、隐私或者安全性（safety）方面损失的系统。

关于上述两个系统的关系，SAE J3061指南中指出：所有的safety-critical系统都是cybersecurity-critical系统，因为一个针对safety-critical系统的直接或间接的网络攻击将会导致潜在的安全（safety）损失。但并不是所有的cybersecurity-critical系统都是safety-critical系统，因为一个针对cybersecurity-critical系统的网络攻击可能会造成除了安全（safety）的其他方面损失，如隐私性、操作性或经济性上的损失。下图为SAE
J3061指南中，对safety-critical及cybersecurity-critical系统之间关系的说明图。

![v2-0be57a00f9cf150bfdabb05526940ca3_720w.jpg](https://image.3001.net/images/20220610/1654830791_62a2b6c7887d97a351b19.jpg!small)图2
SAE J3061中的safety-critical及cybersecurity-critical系统关系说明图[4]

##  **04** **总结**

保障汽车的各方面安全是行业中的重要课题，因为一旦车辆有危害情况发生，除了经济、环境损失外，还会对生命造成威胁。本文主要介绍并辨析了汽车行业中与安全相关的概念，以明确不同安全主题的含义、范围及相互关系，以帮助相关从业者理清概念，明确关系，为更好地解决日常工作中的相关问题打下理论基础。

参考文献：

[1]牛津词典在线，[https://www.lexico.com](https://link.zhihu.com/?target=https%3A//www.lexico.com)

[2]W***pedia, safety, [R/OL].
[https://en.w***pedia.org/wiki/Safety](https://link.zhihu.com/?target=https%3A//en.wikipedia.org/wiki/Safety)

[3]W***pedia,safety, [R/OL].
[https://en.w***pedia.org/wiki/Security](https://link.zhihu.com/?target=https%3A//en.wikipedia.org/wiki/Security)

[4]SAE International. J3061: Cybersecurity guidebook for cyber-physical
vehicle systems[S]. 2016.

[5]International Organization for Standardization. ISO 26262-1 Road vehicles -functional safety - part 1[S]. 2018.

[6]International Organization for Standardization. ISO/PAS 21448: Road
vehicles - safety of the intended functionality[S]. 2019.

[7]International Organization for Standardization. ISO/SAE 21434 (2021) - Road
vehicles– Cybersecurity engineering[S]. 2021.

[8]United Nations Economic and Social Council. Uniform provisions concerning
the approval of vehicles with regards to cyber security and cyber security
management system （WP.29 R155 CSMS）[S]. 2020.

[9]SENDERS J, MORAY N. Human error: cause, prediction, and reduction[M].
Taylor & Francis, 1991.

[10]International Organization for Standardization. ISO/IEC 27000: Information
technology - security techniques - information security management systems -overview and vocabulary[S]. 2009.

