# 针对Office宏病毒的高级检测

阅读量 **182137**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2022-02-18 14:30:45

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t0183b1a15d4b3267a5.jpg)

## 前言

在之前的文章——[《威胁狩猎的最佳实践》](https://blog.moofeng.cn/jian-ce-gong-cheng/wei-xie-shou-lie-de-zui-jia-shi-jian#shen-ru-yan-jiu)里提到过一个针对钓鱼邮件的检测场景，本文会详细分享下当时使用的技巧

遵循前文提到的威胁狩猎流程，让我们从威胁假设(hypothesis)出发：

> 攻击者可能发送带有恶意附件的钓鱼邮件，诱导受害者点击从而获取对方的系统控制权限

期间会借助 [Atomic](https://github.com/redcanaryco/atomic-red-team/)
工具完成攻击复现，再对具体的过程细节进行分析取证，然后深入研究、剖析其行为特征

最后输出检测规则或者 dashboard，作为本次威胁狩猎活动的产出

PS：注意，这里只是提供一种检测思路，测试过程均在实验环境下完成，并不代表实际工作效果

## 分析取证

在对特定攻击活动做数字取证(Digital Forensics)的过程中，通常我会采用 **漏斗状的思维模型** ，一步步缩小观测范围，聚焦目标行为特征

简单做了张图，大概是这么个意思：

![](https://p1.ssl.qhimg.com/t01cc678581fdef6b3e.png)

###  采集全量日志

针对威胁假设的场景，首先我们需要尽可能地保证 office 办公软件的所有行为无处遁形

为了实现图中的逐层分析，还是拿出我惯用的 sysmon，借助其 **配置文件** 来完成，千万别小瞧了这些配置，里面可是有宝藏的！

第一步，建立 **OfficeWatch.xml** 的配置文件，部分内容示例如下：

    
    
    <Sysmon schemaversion="4.70">
      <HashAlgorithms>md5</HashAlgorithms>
      <CheckRevocation/>
      <EventFiltering>
        <RuleGroup name="Process Creation-Include" groupRelation="or">
            <ProcessCreate onmatch="include">
              <Image name="" condition="end with">WINWORD.EXE</Image>
              <ParentImage name="" condition="end with">WINWORD.EXE</ParentImage>
              <Image name="" condition="end with">EXCEL.EXE</Image>
              <ParentImage name="" condition="end with">EXCEL.EXE</ParentImage>
            </ProcessCreate>
        </RuleGroup>
        <RuleGroup name="Process Creation-Exclude" groupRelation="or">
            <ProcessCreate onmatch="exclude">
            </ProcessCreate>
        </RuleGroup>
        <RuleGroup name="Network Connect-Include" groupRelation="or">
            <NetworkConnect onmatch="include">
              <Image name="" condition="end with">WINWORD.EXE</Image>
              <Image name="" condition="end with">EXCEL.EXE</Image>
            </NetworkConnect>
        </RuleGroup>
        <RuleGroup name="Network Connect-Exclude" groupRelation="or">
          <NetworkConnect onmatch="exclude">
          </NetworkConnect>
        </RuleGroup>
        <RuleGroup name="File Create - Include" groupRelation="or">
          <FileCreate onmatch="include">
              <Image name="" condition="end with">WINWORD.EXE</Image>
              <Image name="" condition="end with">EXCEL.EXE</Image>
          </FileCreate>
        </RuleGroup>
        <RuleGroup name="File Create - Exclude" groupRelation="or">
          <FileCreate onmatch="exclude">
          </FileCreate>
        </RuleGroup>
      </EventFiltering>
    </Sysmon>
    

指定 office 软件相关的文件名，保证其进程、文件、网络、DLL 加载和注册表等日志均能被全量采集，同时避免干扰信息

另外，这一步的主要目的不仅是为了 **保持观测目标的可见性** ，更是为了下一步缩小观测范围而 **建立遥测数据的白名单**

例如，平常我们在打开 word 文档的过程中，会产生与微软服务器间的通信，这些是我们需要进行加白处理的

![](https://p4.ssl.qhimg.com/t01bdef7df9aeec7483.png)

同样的，这些加载的 DLL 文件也可以建立一份白名单，当然也别忘了多加留意它们的 **签名状态** (SignatureStatus)

![](https://p4.ssl.qhimg.com/t011216ebb771ae5c41.png)

最后，分析、汇总上述成果，建立一份新的配置文件，用于过滤 office 办公软件的正常行为，将其命名为 **OfficeShush.xml**

![](https://p0.ssl.qhimg.com/t0181bdc859f41b1d74.png)

###  过滤正常行为

关于 OfficeShush.xml 文件的迭代，其实也就是我们对 office 软件相关进程 **建设行为基线** 的过程

这一步需要我们在实验环境下考量全面，夯实基础，再去生产环境中慢慢打磨优化

然后，便得引入丰富的恶意样本，分析其在过滤正常行为后的特征表现

这里其实就是 **攻击复现** 的过程了，以 [T1204.002](https://github.com/redcanaryco/atomic-red-team/blob/master/atomics/T1204.002/T1204.002.md) 为例，跑完攻击脚本，看看会有哪些有意思的发现：

—— 一些脚本文件的创建

![](https://p1.ssl.qhimg.com/t01c85e85dd0b516150.png)

—— 一些异常的命令执行和父子进程关系

![](https://p0.ssl.qhimg.com/t01c271f0f45f2d1be5.png)

—— 一些特定行为(例如运行宏、XMLDOM、WMI等)才会加载的 DLL

![](https://p4.ssl.qhimg.com/t011a593de521b57f04.png)

###  聚焦可疑特征

通过对各类恶意样本或者具体攻击方式做深入分析，我们可以简单梳理一些常见攻击行为会表现出来的特征：

— 可疑文件的落地(释放脚本或可执行文件)  
— 涉及敏感注册表位置的修改  
— 可疑DLL文件的加载行为(加载COM、WMI、或.NET功能所必需的DLL文件)  
— 可疑的网络请求行为(与云服务商或者奇怪的域名通信)  
— 异常的父子进程关系(office软件调用powershell、cmd命令行)  
— …

整理好这些特征点，我们可以凭此生成新的日志采集配置文件，或者给相应的遥测数据打上标签，或者直接加工后转换成检测规则

但是在此之前呢，我想先介绍一种告警手段 —— **Risk-Based Alerting(RBA)**

一些安全运营人员可能对“ **元告警** ”(Meta-Alert)的概念并不陌生，这类告警通常由其它安全设备上报而来

比如在 SIEM 上消费由 EDR 产生的病毒或后门类的告警，这种可以称之为 “meta alert”

在此基础之上，我想谈论的情况是： **在一段时间内，有两条及以上针对同一主机(事件)的检测规则，组合产生了一条告警**

什么时候应该使用这种告警方式呢？

在很多场景中，SIEM 或 SOC 平台上的规则检出只能被视为一种 **弱信号** (weak signals)

它们更适宜被归类成 observable 或 indicator，而不适合直接用作告警，否则会引起运营人员的 **告警疲劳**

此时如果我们通过一种检测方式对这些信号做关联分析，最后产出告警，这一思路就被称作 RBA

受限于手头的工具和平台，本文我只能借助 splunk 演示一种类似的检测方式，通过生成一段 **Hyper Queries** 来达到差不多的效果

## 威胁分析

###  行为检测

根据前面整理出的这些 office 宏病毒相关的可疑活动或者高危操作的行为特征，先写一些简单的规则给它们定个性

这一步可以借助 splunk 给符合特定行为的 sysmon 日志 **打上不同的标签** ，或者 **进行危害评分** ，便于后续做关联分析

比如攻击者可能会利用宏代码调用 cmd、powershell 等进程，进一步完成恶意命令执行的操作

![](https://p0.ssl.qhimg.com/t019081cef93d0935b3.png)

或者攻击者会将 payload 写入磁盘，以特定后缀形式的文件在受害者主机落地

![](https://p1.ssl.qhimg.com/t01c311d24196aac4a8.png)

###  风险判定

放在平时，或许很多人会直接拿着这些行为特征输出成告警

但是针对 office 邮件钓鱼这类频发场景，我们不妨深入研究下，加入一些算法以提高告警置信度

以下演示中，我会为不同的行为简单地指定风险评分，最后进行求和汇总，将超过特定阈值的一系列行为视作高危操作

为方便读者自行对比，找了一篇友商近期的分析文章：<https://mp.weixin.qq.com/s/1L7o1C-aGlMBAXzHqR9udA>

然后上 ANYRUN
拿了份样本：<https://app.any.run/tasks/300229f4-dd97-42d8-bbce-72274ef8b9e9>

实验过程中的检测效果如下：

![](https://p4.ssl.qhimg.com/t01fde780876ec5b76e.png)

演示代码放在这里：<https://github.com/Moofeng/DemoCode/blob/main/office_detection_spl>

结合上述文章和检测结果，可以看到攻击过程几个异常点都能很好的标识出来，例如 **background.dll 文件的落地** 和 **通过 COM
对象执行计划任务** 等关键步骤

最后的判定结果还是具备一定参考意义的，当然，具体的评分体系需要自行设置和优化

## 小结

本文灵感来源于 @Anton，篇幅限制，省略了部分细节，强烈建议感兴趣的同学去看原视频：

<https://www.youtube.com/watch?v=soF5iyeeWDg>

实验过程中借助 splunk 实现的一些检测技巧，参考 @Alex 的文章：

<https://github.com/inodee/threathunting-spl/blob/master/hunt-queries/powershell_qualifiers.md>

感谢！

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **慕长风** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/267298](/post/id/267298)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [钓鱼邮件](/tag/钓鱼邮件)
  * [渗透测试](/tag/渗透测试)
  * [威胁狩猎](/tag/威胁狩猎)

 **+1** __1赞

 __收藏

![](https://thirdwx.qlogo.cn/mmopen/vi_32/Q0j4TwGTfTLWIwV1auq82Xoe66LNVMC1ZsMRStnPpYHqsQKwYmc5POuwVpJSic7zsjUHXib52OSkoA5VufNDEnvg/132)
慕长风

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

