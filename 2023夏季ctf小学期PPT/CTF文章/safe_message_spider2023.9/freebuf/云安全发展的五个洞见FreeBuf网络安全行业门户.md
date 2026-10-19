RSAC
2020如期在旧金山举行，此次由于疫情影响多家国内厂商未能成行，但国内心系产业发展的各家厂商还是时时关注着RSA大会的相关动态。绿盟科技专家团还是在得到RSA资料后第一时间进行研究及分析。根据RSA2020大会期间的云安全高峰论坛（CSA
Summit）、云安全和虚拟化（Cloud Security & Virtualization）、DevSecOps和应用安全（DevSecOps &
ApplicationSecurity）这几部分主题内容，与君共享以下几个观点，详见下文。

  

##  **观点1** ： **云计算成为互联一切的基础设施，云安全也成为了纯安全问题**

RSA会议首日上午的CSA高峰论坛[1]、下午的创新沙盒竞赛，次日上午的Keynote展会已经成为RSA近几年的标配，也是每年的三大看点。CSA高峰论坛作为“首发阵容”中的“首发队员”，其影响力可见一斑。而且很有意思的是，每年CSA的影响力越来越大，各种标准、工作组和培训，应该都让它挣得钵满盆满，覆盖范围也从最初的云计算安全扩展到物联网安全、软件定义边界等交叉领域。可见，云计算已经成为互联一切的基础设施，云安全联盟的触角已然不满足狭义的公有云和私有云计算安全领域了。

可以说，CSA和安全厂商已经成为了合作伙伴关系，在共同的研究点和产品方向上互为背书，互为推广。例如，2019年的高峰论坛上几家做SDWAN安全的厂商在大谈软件定义边界，也为其在2013年提出的SDP云清洗捧场。今年OneTrust公司的VP
Kevin Kiley在讲供应链安全就是对供应链中的第三方厂商进行安全评估，也就是Gartner近两年提出的IRM（Integrated Risk
Management）中的VRM（Vendor Risk Management）。

为什么OneTrust会在云安全的会场谈这个话题呢？因为云计算领域有一个很大的挑战是，用户对云服务商的信任，CSA在前几年提出了Consensus
Assessments Initiative(CAI)[2]，即对用户让云服务商就Cloud Controls Matrix
(CCM)标准填写评估，从而得到第三方云基础设施的可靠度。显然OneTrust的方案也是契合该方向的。可以说云安全联盟在商业运作上非常成功，通过与厂商的合作和客户的培训，形成了云安全领域很好的生态体系，共同推进云计算安全的发展。

另一方面，云计算既然成为了普适的基础设施，提供了计算、存储、网络、函数等服务，那么客户就会将云计算作为一种内生资源，嵌入在他的基础设施中，最终形成统一的IT架构。近两年，多云（Multi-Cloud）、混合云（Hybrid
Cloud）、SDWAN就比较热，在这样的IT环境中提供安全产品、安全服务，就必然要让前几年的云安全产品或方案融入传统环境，提供统一的功能。可以预见，在未来几年，安全厂商的安全方案不会再显示带有“云安全”的定语，因为这就是默认选项，即云安全已经成为纯安全问题。

一个发现是今年CSA高峰论坛的话题已覆盖了网络检测响应（NDR）、供应链安全、数据泄露响应、CISO视角等各安全细分领域的话题，但上午的议程标题中都没有出现Cloud一词。当然细看内容，其实云安全的理念已经融入其中，甚至可以说，大家无论谈安全理念或是安全技术、安全方案，都是面向云计算环境。例如Extrahop
Networks的COO Raja Mukerji在谈检测响应，主张将NDR、EDR、SIEM组合，构建面向公有云的检测响应机制，实现云原生的安全。

当然，虽然传统安全问题会发生在云计算场景中，但云环境也有其独特的地方。所以在云安全和虚拟化（Cloud Security &
Virtualization）议题中，如子域名接管[3]的原因在于一些子域名是租用的，管理不当容易被恶意租户发现并接管；又如好几个胶片谈到暴露面检查，就是Gartner说的CSPM（CloudSecurity
Posture
Management），本质来看就是传统的服务（端口）暴露和弱口令（正如现在很多互联网上脆弱的物联网设备一样），转变成了公有云上的存储资源暴露和弱口令。所以这些本质来说是传统安全问题，但公有云计算环境下有新的特点，值的我们重视。

  

##  **观点2： 从纯合规性要求转向攻防要求，云安全转向实战场景**

前几年，AWS在各个大会上有独立议程做AWS安全入门培训，彼时大部分的客户对公有云还不太熟悉，一部分是因为公有云服务太多、配置太复杂，另一部分原因是对于攻击者而言也比较新，相对而言，IaaS和PaaS的云安全还是以合规性要求居多。

如今，云计算对于攻击者而言，开放API、灵活的资源编排，某种角度来说俨然成为了好用的攻击资源；另外，云用户错误配置，也给觊觎云上敏感数据的攻击者提供了可乘之机。所以无论是数据面安全CWPP（Cloud
Workload Protection
Platform），还是管理面安全CSPM，各类云安全厂商也逐步兴起。从本届RSAC云安议程中的内容来看，跟往届相比更加偏向于实战。

例如前面提到的子域名接管攻击事件，在《Same Thing We Do Every Few Minutes, Pinky – Try to Take
Over All YourSubdomains》 及《Breakthe Top 10 Cloud Attack
Killchains》两张胶片[3,4]中提到，其中《Same Thing We Do Every Few Minutes, Pinky – Try to
Take Over All YourSubdomains》是星巴克安全团队作为受害者的角度阐述，更令人信服。而《Break the Top 10 Cloud
Attack
Killchains》则更全面，介绍了十种面向云平台的攻击链，其中侦查阶段大部分是CSPM关注的暴露Token、Bucket等，另一部分则是恶意内部攻击者，即前面提的供应链覆盖的内容。

当然只有用户和安全厂商显然不够全面，议程中还有一位是来自AWS的Ben Potter，职位是Thesecurity leader for Well-Architected,属于架构师。他在会议中介绍了AWS架构（Well-Architected）中的安全设计，从中可以看出，AWS的安全体系已经覆盖了事前管理、准备，事中检测和响应，事后恢复的闭环，其中他还提到使用了金丝雀账户，部署了一些诱饵。这说明云厂商的安全团队已经不止关注传统的清理（hygiene）和被动防护的工作，也开始做一些主动防御的工作。

总体而言，检测响应已经从传统企业环境转向云计算环境，如《Using Automation forProactive Cloud Incident
Response》及《Untangling SaaS Security in the
Enterprise》[5,6]都介绍了云服务商和用户如何做检测响应的经验，《Untangling SaaS Security inthe
Enterprise》[6]则是介绍了在线交易的领域如何实现身份和访问控制（SSO、MFA，RBAC），数据安全（加密、密钥管理），应用安全（API安全，session管理），日志和监控（分析，日志集中），事件响应（告警、IR剧本），在云计算环境中必须要引入自动化和xDR才能满足规模化的要求。

作为防守方，一家小公司IMG Security的咨询师，《Cloud
ThreatHunting》[9]介绍了云环境下的威胁狩猎，案例非常具体，涉及到渗透测试和事件响应。

  

##  **观点3：从只谈容器安全、Kubernetes安全到云原生安全，云原生进入主流**

在2019年RSAC的早期厂商展览中，已经有一两家公司在做Kubernetes和容器安全，而今年的云安全和DevSecOps议程中，有两篇Kubernetes攻防的胶片，还有一篇介绍云原生安全和Serverless安全，说明这话题已经被主流观众所关注，而且关注热度不断向上，从容器到编排，再到无服务和云原生安全。

例如，SANS的培训师在《DefendingServerless Infrastructure in the
Cloud》演讲中提到[7]攻击者入侵了AWS的Lamda函数，通过反向代理获得无服务的操作系统细节，见下图。

![图片1.png](https://image.3001.net/images/20200310/1583806830_5e66f96e497be.png!small)![图片2.png](https://image.3001.net/images/20200310/1583806830_5e66f96e4b8f4.png!small)  

然后分析了如何从外部获取凭证进入容器，进而收集容器内部更多凭证，横向移动，建议将函数放在VPC里面，减少暴露面。  

在《Kubernetes PracticalAttack and
Defense》[8]中，讲者是一家安全资讯公司Inguardians的CTO，先介绍了Kubernetes下的攻击思路，在Master节点攻击API
server等几个核心组件，在Slave攻击Kubelet和运行时容器，提供了一个自己开源Kubernetes的渗透测试工具（[https://github.com/inguardians/peirates](https://github.com/inguardians/peirates)），该工具主页Demo介绍了获得暴露的秘密，然后从API-server创建账号，新建容器，并得到反连Shell。另外还提供了一个测试训练环境，供学习 （<https://www.bustakube.com/>）。

从以上几个胶片的内容可以看出，今年云计算安全很明显的转变，安全倾向于攻防细节，环境则侧重于编排系统之上的部分。

  

##  **观点4：DevSecOps成为热点，DevSecOps和云原生安全不断融合，创造共同话题**

敏捷开发DevOps似乎与云计算是两个维度，但“容器-编排”可以支撑敏捷CI/CD的开发模式，而“编排-无服务”的云原生运营模式可以支撑大规模弹性的应用场景。这套技术栈似乎为全世界绝大多数的开发者所青睐，而容器Kubernetes-Serverless又是云原生的底层技术，所以随着敏捷开发本身的安全机制（DevSecOps）不断发展，两种安全视角的融合不断加深。

今年的云安全议程中有一些问题的起源，如代码中的硬编码Token、代码仓库的暴露凭证，都是安全敏捷开发需要关心的内容，而今年的DevSecOps
和应用安全（DevSecOps & ApplicationSecurity）议程中，则有一篇《CompromisingKubernetes Cluster
by Exploiting RBAC Permissions》[10]是专门介绍Kubernetes的访问控制安全的。

  

##  **观点5：人是对抗永远的主题，人的因素不可忽视**

今年大会的主体是Human Element，不可避免的很多胶片中也出现了这个元素，大部分都是简单涉及，有两篇则是专门对人的因素进行探讨。

如《Hacking Your Security Culture for the
Cloud》[11]介绍了在传统环境和云环境中不同的思路，在云环境中做安全应该与云计算的思路匹配，如安全即代码，拥抱自动化，此外要避免人为错误所造成的影响，组织红蓝对抗。而[12]是出现在敏捷开发的session中的，讨论了工作时间、团队规模和修改他人代码频繁度等因素对代码安全性产生的影响。总之，技术、流程和人是信息安全的三个组成部分，其中人的因素在不断的提升。如何发挥人的主观能动性，对于提升安全防护效率至关重要。

总之，云计算已经成为了连接万物的普适的基础设施，云计算安全已经进入了下半场，如何形成统一的安全体系，如何提升云计算的真实安全水平，如何提升使用云计算各种团队的安全能力，将是接下来云安全的发展方向。

**参考链接**

[1] <https://www.rsaconference.com/usa/agenda/csa-summit-privacy-and-security-in-the-cloud>

[2] <https://cloudsecurityalliance.org/research/working-groups/consensus-assessments/>

[3] Same Thing We Do Every Few Minutes, Pinky – Try to Take Over All Your
Subdomains ,RSAC2020

[4] Break the Top 10 Cloud Attack Killchains, RSAC2020

[5] Using Automation for Proactive Cloud IncidentResponse,RSAC 2020

[6] Untangling SaaS Security inthe Enterprise, RSAC 2020

[7] DefendingServerless Infrastructure in the Cloud,RSAC 2020

[8] Kubernetes Practical Attack and Defense, RSAC 2020

[9] Cloud Threat Hunting, RSAC 2020

[10] Compromising KubernetesCluster by Exploiting RBAC Permissions, RSAC 2020

[11] Hacking Your Security Culture for the Cloud，RSAC 2020

[12] Which Developers and TeamsAre More Likely to Write Vulnerable
Software,RSAC 2020

  

