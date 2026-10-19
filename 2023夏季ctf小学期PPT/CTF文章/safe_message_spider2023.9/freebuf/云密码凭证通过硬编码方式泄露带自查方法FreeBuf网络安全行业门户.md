欢迎各位大佬关注同名公众号”[狼蛛安全实验室](https://mp.weixin.qq.com/s/K51rYQDpWjMCNAa7NGZ2bQ)“

##  **00** **KeyWords**

1、 **硬编码** 是指在软件实现上，将输出或输入的相关参数直接以常量的方式撰写在原始码中。

2、 **硬编码凭证** 是指在应用程序、服务或基础设施中使用的数字身份验证凭证（API 密钥、证书、令牌等）。

3、 **硬编码凭证泄露** 是开发人员会将密钥保存在不安全的位置，以便更轻松地更改代码，但这样做通常会导致信息被错误地遗忘并无意中发布出去。

在《潜伏在源代码中的硬编码凭证对供应链攻击意味着什么？》一文中介绍到“在应用程序安全环境中，硬编码凭证实际上是一种类似于后门的漏洞。首先，由于源代码是一种非常容易泄露的资产，意味着它会在多台机器上经常被克隆、签出和分叉，但仍然有效的凭证可以隐藏在任何一次克隆、签出和分叉的代码中。”

##  **01** **概述**

有很多云的密钥凭证以硬编码的形式存储在代码中，这些凭证并未过期，实时可用，若出现调试、报错信息或上传到代码仓库后，暴露在公网，容易造成供应链攻击等危害，应多加防范和注意。

作者近期在跟踪暗网数据泄露以及公开报道的数据泄露事件时，多次发现将云存储桶（例如AWS）的密码凭证以常量的方式写在源代码中，并且发布时并未删除——硬编码凭证泄露。

##  **02** **案例**

其实由于硬编码凭证泄露导致的巨大危害时常发生，例如2022年6月30日，在暗网论坛发布的包含数十亿中国公民的数据和警情信息的上海政府国家警察数据库，可能就是由于和上海此系统相关的开发人员在写CSDN博客时将阿里云的accessKey直接复制进了代码中泄露导致。此人将代码注释了，可以防止从调试信息处获取此Key，但是却在源代码侧将其暴露了出来，属实是不小心。

![640?wx_fmt=png](https://image.3001.net/images/20220912/1662951187_631e9f132c7569734a38f.jpg!small)

2021年10月，流行视频流平台Twitch 发生了泄露，造成 6000 多个 Git 存储库和 300 万份文档泄露共计约128G。其中包含了数百个
AWS、Google、Stripe 和 GitHub
的密钥。只需组合其中几个密钥，就足以对目标企业最关键的系统发起全面攻击。由此看来，即便没有主动将源代码公布在互联网，也有可能因为云供应商或私有仓库遭到攻击而将代码暴露，此时硬编码凭证依旧会泄露，防不胜防。

![640?wx_fmt=png](https://image.3001.net/images/20220912/1662951200_631e9f2037f15acf1a84c.jpg!small)

2016年10月，优步Uber（类似国外的滴滴打车）遭到攻击并被勒索，共有5700万名乘客的个人资料遭黑客盗取，同时60万名司机的驾照信息也同时被盗取，涉及到姓名、电子邮件地址和电话号码等信息。

根据媒体报道，与此前其他黑客案件不同，两名黑客进入优步软件工程师使用的Github仓库，取得该公司的登录信息（云服务提供商授予访问优步基础设施的密钥），再进入为优步处理运算工作的亚马逊网络服务帐户，从该帐户窃取了优步乘客和司机的个人资料，随后，他们向优步公司索取赎金。

此事件后，网络安全公司SentinelOne的安全专家表示“程序员经常会把公司登录信息写在Github程序里，使得程序能够自动登录获取数据，但最后总是会忘掉对登录加以时间和情况限制。”这类事件多年前就已发生……

![640?wx_fmt=png](https://image.3001.net/images/20220912/1662951212_631e9f2cca6b2ebced7b5.jpg!small)

作者在模仿这些攻击者进行探测时，
**也发现了我国一些企业或单位的数据库或存储库，有的将这些库的登录凭证直接写在代码中，并上传到Gitee或Gitea，甚至是Github**
（外国产品，可能导致数据出境）； **有**
**的则是因为配置原因直接暴露在公网，例如ElasticSearch（ES存储库）或Redis，容易被直接拖库或加密勒索。**

![640?wx_fmt=png](https://image.3001.net/images/20220912/1662951239_631e9f47dc5bea20b2aae.jpg!small)

![640?wx_fmt=jpeg](https://image.3001.net/images/20220912/1662951246_631e9f4ed7fef1bd302e2.jpg!small)

##  **03** **利用方式**

如果获取到了这些accesskey，危害有多大呢？其实网上有很多这类的利用工具，仅需要输入Key值或Secret值（一般同时泄露）即可获取用户权限，并可进行拖库或勒索操作，手法简单，危害极大。

作者在一篇经验贴中看到一位经授权后的渗透测试师，对一台阿里云主机getshell的过程，其中最重要的步骤就是他在页面的调试信息中发现了Reids账号密码、Mysql账号密码、阿里云accesskey等内容。

![640?wx_fmt=png](https://image.3001.net/images/20220912/1662951256_631e9f5866b2a0bcc2953.jpg!small)

在拿到ALIYUN_ACCESSKEYID和ALIYUN_ACCESSKEYSECRET之后，使用aliyun-accesskey-工具即可远程命令执行。要不是这个主机的mysql和redis端口都未对外网开放，危害只会更大。

![640?wx_fmt=png](https://image.3001.net/images/20220912/1662951280_631e9f70eeda887a2350e.jpg!small)

除了阿里云的accesskey利用工具外，还有腾讯云、亚马逊云等都能在github上找到开源的利用工具，使用方法简单，同样危害较大。

![640?wx_fmt=png](https://image.3001.net/images/20220912/1662951296_631e9f804e1c8bdfb4c67.jpg!small)![640?wx_fmt=png](https://image.3001.net/images/20220912/1662951305_631e9f8930a5e3f25379d.jpg!small)

 **在此，作者梳理了一部分我国会使用的云的一些accesskey的键名，可自查代码中是否含有此键名，可及时消除危害。**

 **亚马逊云：**

aws_access_key

access_key_id

secret_access_key

 **阿里云：**

accessKey

ALIYUN_ACCESSKEY

ALIYUN_ACCESSKEYID

ALIYUN_ACCESSKEYSECRET

AccessKeyID

AccessKeySecret

 **腾讯云：**

SecretId

SecretKey

##  **04** **风险危害 &处置建议 **

2022年9月1日，赛门铁克研究人员发布《移动应用供应链漏洞可能危及敏感商业信息》一文，该文章称“赛门铁克分析了1,859 个公开可用的应用程序，包括
Android 和 iOS， **超过四分之三 (77%) 的应用程序包含有效的 AWS 访问令牌，允许访问私有 AWS 云服务，这些应用程序中有近一半
(47%) 包含有效的 AWS 令牌，这些令牌还允许通过 Amazon Simple Storage Service (Amazon S3)
完全访问大量（通常是数百万）私有文件**
”与本文所提到的内容交相呼应，硬编码凭证不仅可以写在web程序的源代码中，还可以写在移动端app中，本质其实是一样的，都有可能导致数据泄露或供应链攻击。

![640?wx_fmt=png](https://image.3001.net/images/20220912/1662951330_631e9fa2c5cb8521977de.jpg!small)

文章还提到“为什么应用程序开发人员使用硬编码访问密钥的问题”，原因包括：

1、下载或上传应用程序所需的资产和资源，通常是大型媒体文件、录音或图像

2、访问应用程序的配置文件或注册设备并收集设备信息并将其存储在云中

3、访问需要身份验证的云服务，例如翻译服务

4、没有特定原因、写死的代码或用于测试且未删除

2022年5月26日在安全419团队公众号上发布的《潜伏在源代码中的硬编码凭证对供应链攻击意味着什么？》文章中，提到“2021年GitGuardian检测到超过
600 万个泄露的硬编码凭证推送到 GitHub 上，比 2020 年翻了一番。平均而言，1000 个提交中有 3 个包含凭证，比2020年高出
50%。这些硬编码凭证中有很大一部分都能够提供对公司资源的访问权限。”

如果作为攻击者，试图入侵目标企业的系统，通常也会先尝试查看其在开源代码仓库上的公共存储库，若为国内的公司可能会看Gitee，Gitea，国外则GIthub居多，公司官方存储库看完后还可以查看其公司员工的存储库，这时就需要对这家公司的人员进行调研，也是攻击前期收集信息的必要环节。上面提到的文章中还称“许多开发人员将
GitHub
用于个人项目，并且可能会意外泄漏公司凭据。使用这些泄露在外的公司凭据，攻击者可以伪装成合法的身份进行登录操作，绕开部署在边界的安全检测工具。”这其实并非内鬼，而是由于开发人员安全意识不高导致的。

![640?wx_fmt=png](https://image.3001.net/images/20220912/1662951339_631e9fab520b98bedb61d.jpg!small)

该文章还提到“企业的另一个严重错误是容忍非公共存储库中存在硬编码凭证。GitGuardian 在State of Secrets Sprawl
报告中指出，私有存储库比公共存储库隐藏的硬编码凭证要多得多。这些被遗忘的凭证如果被黑客窃取，毁灭性的打击随时都有可能到来。”

 **针对上面提到的风险，我们应该多加注意和防范，亚马逊AWS给了一些可供参考的解决方案和建议。**

1、使用密钥检测工具来识别硬编码凭证。

Amazon CodeGuru Reviewer 推出密钥检测器功能，这是一种自动化的工具，可帮助开发人员检测源代码或配置文件中的密钥，例如密码、API
密钥、SSH
密钥和访问令牌。这种新推出的检测器在代码审查过程中使用机器学习（ML）来识别硬编码的密钥，从而帮助您确保所有新代码在合并和部署之前未包含硬编码的密钥。除
Java 和 Python 代码之外，密钥检测器还可以扫描配置和文档文件。

![640?wx_fmt=png](https://image.3001.net/images/20220912/1662951347_631e9fb30312229cec8d5.jpg!small)

2、使用AWS Secrets Manager进行密钥管理和保护。

这是一项托管式的服务，可让您安全并自动地存储、轮换、管理和检索凭证、API
密钥以及其他各种类型的密钥。相当于将这个服务提供一个SDK，用以存储密钥，需要用到时调用此SDK获取密钥值即可。

![640?wx_fmt=png](https://image.3001.net/images/20220912/1662951356_631e9fbc8ecbc28ff8c8f.jpg!small)

##  **05** **参考链接**

https://docs.aws.amazon.com/codeguru/latest/reviewer-ug/recommendations.html#secrets-detection

https://aws.amazon.com/cn/blogs/china/codeguru-reviewer-secrets-detector-identify-hardcoded-secrets/

[https://mp.weixin.qq.com/s/91vIbewCkc3cbfWWILZgaA](https://mp.weixin.qq.com/s?__biz=MzUyMDQ4OTkyMg==&mid=2247499714&idx=3&sn=a45ffb1d8ba174fe84dcbea4fdd8a4da&scene=21#wechat_redirect)

https://symantec-enterprise-blogs.security.com/blogs/threat-intelligence/mobile-supply-chain-aws

https://archive.ph/mP3bh

https://github.com/K1p2y3/Tencent_Yun_tools

https://github.com/Aabyss-Team/awsKeyTools

https://github.com/mrknow001/aliyun-accesskey-Tools

