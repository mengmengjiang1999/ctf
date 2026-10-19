## 引言

在撰写这一系列文章时，笔者也在思考如何避免假大空的更好地呈现这一框架的内容，如何输出对安全行业有用的具有实操价值的内容。而理解并掌握ATT&CK框架的关键就是学会使用ATT&CK这种通用性语言对我们平常所进行的各个攻击流程中的细节行为进行描述，同时通过这一完善的内容架构对组织安全防护缺失进行自查，尽量做到完整涵盖各个方面，理解机构自身在面对针对性攻击时所面临的到底是什么，需要完善的又是哪些方面，对安全工作进行量化。因此阅读并理解ATT&CK中的各个Matrices、Tactics、Techniques是很有必要的（如果对ATT&CK框架还不了解请查看这一系列的首篇文章），所以这篇文章也仅是一个基于框架的中文版学习指南，如果读者能够清晰完整并快速地浏览ATT&CK框架的原文则不建议浪费时间在此篇文章当中（但可以作为中文参考备用）。

一直以来信息搜集的文章和技巧都层出不穷，许多文章也已经从技术层面详细地涵盖了各个在实战过程中所应涉及到的信息收集点。但是对于一次APT攻击来说，这样的信息搜集过程是有所缺失的，其更多的还是聚焦于服务器或网站等具体技术组件的信息搜集，缺少其他层面的信息搜集视角。而这在ATT&CK中有了一个很好的完善，通过一种规范化的定义，对实际攻击流程中的信息搜集进行了完整覆盖。

ATT&CK中对各种Tactics和Techniques的描述是以一种假想攻击者在整个攻击流程中的行为的口吻，文章用了一种更易阅读的方式进行了翻译概括，可以作为企业安全检查基线或红队攻击指南使用。本来也想在Techniques层面进一步扩展映射一下平常在使用的一些具体的搜集工具及搜索技巧，但后来发现单单完成此篇文章的工作量已经远远超出预期，如果后续再进行添加实在太耗时间，因此决定还是不进行拓展了留给各位自行针对所需进行补充与完善。

![img](https://image.3001.net/images/20210127/1611735136_601120608fccef7c75fd9.jpg!small)

文末附有中文完整版下载（包含所需搜集信息与搜集方式）

## TA0043 Reconnaissance 侦查

PRE-Matrix归属于ATT&CK for Enterprise下，其下分为TA0043 Reconnaissance和TA0042 Resource
Development两个战术，此篇文章介绍的为TA0043 Reconnaissance 侦察战术的技术细节

在这一战术中，攻击者正试图收集情报以便计划未来的行动。侦察技术包括主动和被动地收集信息以便支持攻击目标。这些信息可以包含受害者组织、基础设施以及工作人员等的详细信息。攻击者可以利用这些信息来帮助完成对手攻击流程的其他阶段，例如使用这些信息来计划和执行初始访问，确定沦陷目标的范围和优先级，以及驱动和领导进一步的侦察行动。

此战术中共包含9个技术（在其官网并没有按数字顺序排序，这样排序方便梳理与理解）

> T1589 Gather Victim Identity Information 收集受害者身份信息
>
> T1590 Gather Victim Network Information 收集受害者网络信息
>
> T1591 Gather Victim Org Information 收集受害者组织信息
>
> T1592 Gather Victim Host Information 收集受害者主机信息
>
> T1593 Search Open Websites/Domains 搜索开放网站/域
>
> T1594 Search Victim-Owned Websites 搜索受害者所拥有网络
>
> T1595 Active Scanning 主动扫描
>
> T1596 Search Open Technical Databases 搜索开放技术数据库
>
> T1597 Search Closed Sources 搜索封闭来源
>
> T1598 Phishing for Information 信息钓鱼

根据技术名称也可以比较清晰的了解T1589-T1594、T1596-T1597侧重于描述无需交互的信息搜集技巧，而T1595和T1598更侧重于需要主动交互的信息搜集技巧

### T1589 Gather Victim Identity Information 收集受害者身份信息

收集信息：受害者身份信息，包括个人数据（例如员工姓名、电子邮件地址等）以及凭据等敏感信息

收集方式：T1598 Phishing for Information。通过在线或其他可访问的公开数据集暴露给攻击者（T1593.001 Social
Media 或T1594 Search Victim-Owned Websites）

引申Techniques：收集到信息可能会揭示其他形式的侦察机会（T1593 Search Open Websites/Domains和T1598
Phishing for Information），建立操作资源（T1586 Compromise Accounts），以及初始访问（T1566
Phishing或T1078 Valid Accounts）

#### T1589.001 Credentials 凭据

收集的信息：与目标受害组织直接相关的帐户凭据，在个人和企业帐户中使用相同密码的用户

收集方式：T1598 Phishing for
Information、利用水坑攻击窃取用户cookie等认证信息、通过在线或其他可访问的公开数据集（例如T1593.002 Search Engines
搜索引擎、转储泄漏、代码仓库等）、从暗网或其他黑市中购买

    
    
    引申Techniques：T1593 Search Open Websites/Domains、T1598 Phishing for Information、T1586 Compromise Accounts 、T1133 External Remote Services、T1078 Valid Accounts 

#### T1589.002 Email Addresses 邮件地址

收集信息：邮件地址、组织面向员工的电子邮件地址及相关基础设施

收集方式：通过在线或其他可访问的公开数据集（T1593.001 Social Media、T1594 Search Victim-Owned
Websites）

    
    
    引申Techniques：T1593 Search Open Websites/Domains、T1598 Phishing for Information、T1586.002 Email Accounts、T1566 Phishing

#### T1589.003 Employee Names 职员名称

收集信息：员工姓名（可被用来获取电子邮件地址，并帮助指导以完成其他侦察工作和制作更可信诱饵）

收集方式：通过在线或其他可访问的公开数据集（T1593.001 Social Media、T1594 Search Victim-Owned
Websites）

    
    
    引申Techniques：T1593 Search Open Websites/Domains、T1598 Phishing for Information、T1586 Compromise Accounts 、T1566 Phishing、T1078 Valid Accounts 

### T1590 Gather Victim Network Information 收集受害者网络信息

收集信息：网络相关信息，包括管理数据（IP地址范围、域名等）以及关于其拓扑和操作的细节信息

收集方式：通过 T1595 Active Scanning 或 T1598 Phishing for Information
直接收集信息，通过在线或其他可访问的公开数据集暴露给攻击者（T1594 Search Victim-Owned Websites）

引申Techniques：收集到信息可能会揭示其他形式的侦察机会（T1595 Active Scanning或T1593 Search Open
Websites/Domains），建立操作资源（T1583 Acquire Infrastructure和T1586 Compromise
Accounts），以及初始访问（T1199 Trusted Relationship）

#### T1590.001 Domain Properties 域管理信息

收集信息：受害者所拥有域名的相关管理信息（名称、注册商等）、邮件地址、电话号码、公司地址、域名服务器

收集方式：T1595 Active Scanning、T1598 Phishing for Information、通过在线或其他可访问的公开数据集（例如
T1596.002 WHOIS）

    
    
    引申Techniques：T1596 Search Open Technical Databases、T1593 Search Open Websites/Domains、T1598 Phishing for Information、T1583 Acquire Infrastructure、T1584 Compromise Infrastructure、T1566 Phishing

#### T1590.002 DNS

收集信息：包括已注册的域名服务器、目标子域列表、邮件服务器和其他主机地址记录

收集方式：开源数据集 T1596.001 DNS/Passive DNS、通过在线或其他可访问的公开数据集（T1596 Search Open
Technical Databases）

    
    
    引申Techniques：T1596 Search Open Technical Databases、T1593 Search Open Websites/Domains、T1595 Active Scanning、T1583 Acquire Infrastructure、T1584 Compromise Infrastructure、 External Remote Services 

#### T1590.003 Network Trust Dependencies 网络可信依赖

收集信息：与组织有（潜在）联系的第二方或第三方组织/域（例如托管服务提供商、承包商等）

收集方式：T1598 Phishing for Information、通过在线或其他可访问的公开数据集（T1596 Search Open
Technical Databases）

    
    
    引申Techniques：T1595 Active Scanning、T1593 Search Open Websites/Domains、T1583 Acquire Infrastructure、T1584 Compromise Infrastructure、T1199 Trusted Relationship

#### T1590.004 Network Topology 网络拓扑

收集信息：外部和内部网络环境的物理和逻辑拓扑，相关网络设备（网关、路由器等）和其他基础设施的细节信息

收集方式：通过T1595 Active Scanning、T1598 Phishing for
Information直接收集信息，通过在线或其他可访问的公开数据集（T1594 Search Victim-Owned Websites）

    
    
    引申Techniques：T1596 Search Open Technical Databases、T1593 Search Open Websites/Domains、T1583 Acquire Infrastructure、T1584 Compromise Infrastructure、T1133 External Remote Services  

#### T1590.005 IP Addresses IP相关信息

收集信息：正被使用的IP地址（通过IP地址还可以使攻击者获得有关受害者的其他详细信息，如组织规模、物理位置、Internet服务提供商，以及在何处/如何托管其面向公众的基础设施）

收集方式：T1595 Active Scanning 、T1598 Phishing for
Information、通过在线或其他可访问的公开数据集（T1596 Search Open Technical Databases）

    
    
    引申Techniques：T1595 Active Scanning、T1596 Search Open Technical Databases、T1583 Acquire Infrastructure、T1584 Compromise Infrastructure、T1133 External Remote Services 

#### T1590.006 Network Security Appliances 网络安全设备

收集信息：受害者网络中安全相关的应用、部署的防火墙、内容过滤器、代理/堡垒主机、NIDS、其他安全防御相关运营信息

收集方式：T1595 Active Scanning 、T1598 Phishing for
Information、通过在线或其他可访问的公开数据集（T1594 Search Victim-Owned Websites）

    
    
    引申Techniques：T1596 Search Open Technical Databases、T1593 Search Open Websites/Domains、T1587 Develop Capabilities、T1588 Obtain Capabilities、T1133 External Remote Services 

### T1591 Gather Victim Org Information 收集受害者组织信息

收集信息：分部/部门的名称、业务流程的详细信息以及关键员工的角色和职责。

收集方式：通过T1598 Phishing for Information直接获取。通过在线或其他可访问的公开数据集（T1593.001 Social
Media或T1594 Search Victim-Owned Websites）。

引申Techniques：收集到信息可能会揭示其他形式的侦察机会（T1598 Phishing for Information和T1596 Search
Open Technical Databases），建立操作资源（T1585 Establish Accounts和T1586 Compromise
Accounts），以及初始访问（T1566 Phishing或T1199 Trusted Relationship）。

#### T1591.002 Business Relationships 业务关系

收集信息：业务关系信息包括与该组织存在网络访问（和潜在相关的）的第二或第三方（例如托管服务提供者、承包商等）的组织/域信息，这些信息可能揭示受害者硬件和软件资源的供应链和运输路径

收集方式：T1598 Phishing for Information、通过在线或其他可访问的公开数据集（T1593.001 Social
Media、T1594 Search Victim-Owned Websites）

    
    
    引申Techniques：T1598 Phishing for Information、T1593 Search Open Websites/Domains、T1585 Establish Accounts、 T1586 Compromise Accounts、T1195 Supply Chain Compromise、T1189 Drive-by Compromise、T1199 Trusted Relationship

#### T1591.001 Determine Physical Locations 确定物理位

