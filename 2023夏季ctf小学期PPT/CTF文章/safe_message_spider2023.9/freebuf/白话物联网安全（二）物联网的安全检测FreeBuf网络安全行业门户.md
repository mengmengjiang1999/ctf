***本文原创作者：大胖，本文属FreeBuf原创奖励计划，未经许可禁止转载**

**第一章《[什么是物联网的信息安全](https://www.freebuf.com/column/191098.html)》，我们讲了什么物联网，包含了哪几方面的东西，物联网的信息安全会涉及到什么，第二章我们从一个IOT漏洞自动化利用工具AutoSploit讲起，讲到我们该如何检测我们常见的物联网存在的安全问题。**

我们这次说安全检测，从业务层先开始，然后降到感知层，然后提到网络层的授权和安全策略，所以先介绍下工具AutoSploit，AutoSploit基于
Python2.7的脚本，使用 Shodan.io API 自动收集目标，Metasploit模块有助于实施远程代码执行，并获得逆向 TCP/Shells
或者Metasploit 对话（官方介绍，实际上用Shodan的API免费的只有那几页）。

> GitHub地址：<https://github.com/NullArray/AutoSploit>

我们先安装一下，搞一个测试：

安装环境：kail2.0、Python 2.7

安装步骤：

1：下载文件 git clone <https://github.com/NullArray/AutoSploit.git>

2：执行install.sh 安装

![1.png](https://image.3001.net/images/20181203/15438218353660.png!small)

3：因为AutoSploit安装需要python的库文件支持，该文件已经写好了，在目录下的requirentx.txt文件，直接pip安装即可。

![2.png](https://image.3001.net/images/20181203/15438218601813.png!small)

![3.png](https://image.3001.net/images/20181203/15438218659449.png!small)

4：安装完了我们直接执行 python autosploit.py。

![4.png](https://image.3001.net/images/20181203/15438219226431.png!small)

5：开始做选择题，一般直接选第一个。

![5.png](https://image.3001.net/images/20181203/15438219336065.png!small)

6：选择收集主机，选择自己需要的关键词。

![6.png](https://image.3001.net/images/20181203/15438220071019.png!small)

7：然后收集一会，选择6，利用MSF模块进行收集信息。

![7.png](https://image.3001.net/images/20181203/15438220694964.png!small)

上面就是这个工具安装和使用方法，为什么我们要把这个工具AutoSploit单独拉出来说，是因为他把常见的IOT的漏洞从MSF中拉了出来，提供了285常见的容易利用的插件，咱们来说说IOT的安全检测，最基础要检查什么东西。

AutoSploit的285个MSF插件包括259个exp，26个辅助插件，其中259个exp包括了61个windows插件，61个Linux插件，96个multi插件，37个unix插件，4个其他类型插件。从分类上来讲，主要集中在业务系统产生漏洞（中间件，应用本身，数据库），主要产生在http/https协议上。

那么我们整理清楚了，对业务层来说，容易利用并且能构成重大危害的安全问题，又回归到我们常说的业务系统安全问题（主要依据2017年CNVD收录IOT设备漏洞权限绕过、拒绝服务、信息泄露、跨站、命令执行、缓冲区溢出、SQL注入、弱口令、设计缺陷等漏洞），对这一层次来说，扫描器，监控预警等等利用测试方法解决常见的直接利用的安全问题的方法都已经很成熟了，商用扫描器，开源扫描器一般都能检查测试，同理可推，我们作为安全运维的大致内容如下，我找了张思维导图：

![8.png](https://image.3001.net/images/20181203/15438221203597.png!small)

那么对于物联网来说，仅仅检测了业务层的东西是远远不够的，那么我们还要对网络层和感知层进行安全检测，这时候就不得提及一下物联网的安全架构，宏观角度（涉及范围广，涵盖全部物联网体系）上来说，分为了四个大块：

> 认证 （Authentication）：提供验证物联网实体的标识信息并用于验证。
>
> 授权 （Authorization）：控制设备在整个网络结构中的访问授权。
>
> 强制性的安全策略 （Network Enforced
> Policy）：包括在基础架构上安全地route并传输端点流量的所有元素，无论是控制层面、管理层面还是实际数据流量中的，再次基础上运用合适的安全策略。
>
> 安全分析：可见性与可控性 （Secure Analytics: Visibility and
> Control）：安全分析层确定了所有元素（端点和网络基础设施，包括数据中心）可能参与的服务，提供遥感勘测，实现可见性并最终控制物联网生态系统。

我们现在是从外向里看，现阶段在应用层解决的问题，其实是属于在微观角度上解决了IOT在业务层部分安全分析的事情，现在要说清楚感知层和网络层安全检测，首先要做的，就是检测认证，因为物联网的末端设备认证更多依靠射频识别（RFID）、共享密钥、X.509证书、端点的MAC地址或某种类型的基于不可变硬件的可信root，加上极少数的人为认证（如用户名、密码、令牌或生物特征），我们在做检测的时候，先确定末端设备的身份信息是否在单一授权的情况下可以进行访问，是否开放身份信息，身份信息是否可以伪造，身份信息是否足够强壮。
感知层除了单一设备认证面临的问题，感知层还有一个很头疼的特点：数量巨大，并且普遍存在移动性。这就导致了一个大问题，资产梳理（资产追踪和管理）成为了卡在对感知层安全检测的第一道门槛。

那我们做一个简单的设计，根据物联网接入设备的要求，先梳理资产（公网的直接找指纹用AutoSploit去跑），在对资产进行管理。

![9.png](https://image.3001.net/images/20181203/15438221728903.png!small)

那么IOT感知层的如何整理资产和检测，我们用一个简单的流程图完成了思路，核心的IOT漏洞的规则库，海康威视IP摄像机权限绕过CVE2017-7921，CVE-2017-7923为例，代码文件如下：

    
    
    if (description)
    {
      script_oid("1.3.6.1.4.1.25623.1.0.140373");
      script_version("$Revision: 7182 $");
      script_tag(name: "last_modification", value: "$Date: 2017-09-19 07:44:15 +0200 (Tue, 19 Sep 2017) $");
      script_tag(name: "creation_date", value: "2017-09-18 11:41:11 +0700 (Mon, 18 Sep 2017)");
      script_tag(name: "cvss_base", value: "7.5");
      script_tag(name: "cvss_base_vector", value: "AV:N/AC:L/Au:N/C:P/I:P/A:P");
    
      script_cve_id("CVE-2017-7921", "CVE-2017-7923");
    
      script_tag(name: "qod_type", value: "exploit");
    
      script_tag(name: "solution_type", value: "VendorFix");
    
      script_name("Hikvision IP Cameras Multiple Vulnerabilities");
    
      script_category(ACT_GATHER_INFO);
    
      script_copyright("This script is Copyright (C) 2017 Greenbone Networks GmbH");
      script_family("Web application abuses");
      script_dependencies("gb_get_http_banner.nasl");
      script_mandatory_keys("App-webs/banner");
      script_require_ports("Services/www", 443);
    
      script_tag(name: "summary", value: "Multiple Hikvision IP cameras are prone to multiple vulnerabilities.");
    
      script_tag(name: "vuldetect", value: "Sends a crafted HTTP GET request and checks the response.");
    
      script_tag(name: "insight", value: "Multiple Hikvision IP cameras are prone to multiple vulnerabilities:
    
    - Improper authentication vulnerability (CVE-2017-7921)
    
    - Password in configuration file (CVE-2017-7923)");
    
      script_tag(name: "impact", value: "Successful exploitation of these vulnerabilities could lead to a malicious
    attacker escalating his or her privileges or assuming the identity of an authenticated user and obtaining
    sensitive data.");
    
      script_tag(name: "affected", value: "Hikvision reports that the following cameras and versions are affected:
    
    - DS-2CD2xx2F-I Series: V5.2.0 build 140721 to V5.4.0 build 160530
    
    - DS-2CD2xx0F-I Series: V5.2.0 build 140721 to V5.4.0 Build 160401
    
    - DS-2CD2xx2FWD Series: V5.3.1 build 150410 to V5.4.4 Build 161125
    
    - DS-2CD4x2xFWD Series: V5.2.0 build 140721 to V5.4.0 Build 160414
    
    - DS-2CD4xx5 Series: V5.2.0 build 140721 to V5.4.0 Build 160421
    
    - DS-2DFx Series: V5.2.0 build 140805 to V5.4.5 Build 160928
    
    - DS-2CD63xx Series: V5.0.9 build 140305 to V5.3.5 Build 160106");
    
      script_tag(name: "solution", value: "See the referenced advisory for a solution.");
    
      script_xref(name: "URL", value: "https://ics-cert.us-cert.gov/advisories/ICSA-17-124-01");
      script_xref(name: "URL", value: "http://www.hikvision.com/us/about_10807.html");
      script_xref(name: "URL", value: "http://seclists.org/fulldisclosure/2017/Sep/23");
    
      exit(0);
    }
    
    include("http_func.inc");
    include("http_keepalive.inc");
    
    port = get_http_port(default: 443);
    
    url = '/Security/users?auth=YWRtaW46MTEK';
    
    if (http_vuln_check(port: port, url: url, pattern: "<UserList version", check_header: TRUE,
                        extra_check: "<userName>")) {
      report = "It was possible to obtain a list of device users at: " +
               report_vuln_url(port: port, url: url, url_only: TRUE);
      security_message(port: port, data: report);
      exit(0);
    }
    
    exit(99);
    

一个简单的漏洞检测的规则文件就这样成型了。

那么继续进行检测，接下来检测网络层，网络层在安全设计里面牵扯到授权和强制性的安全策略，也就是我们在网络层的面临的核心安全问题是没有一个授权标准，没有通用的通信协议，安不安全就靠厂商的良心了。

网络层我们要检测的主要是网络设备本身的安全性，传输过程中的信任链及安全策略。

网络设备本身安全性这个现阶段扫描器很多，买一个或者网上找一个破解版的扫描器都能够满足需求。

传输过程中的信任链及安全策略只能一条一条去查了，没有好的工具，不同级别和层次的要求不同，这里就一一列举了。

现阶段市面上我暂时没找到针对IoT设备的自动化安全测试工具(成熟的各种功能都有的扫描器)结合我对检测的理解写了白话物联网第二篇文章，白话三我们谈谈基于现状，我们怎么构架我们的物联网防御体系。

 ***本文原创作者：大胖，本文属FreeBuf原创奖励计划，未经许可禁止转载**

