TIM是意大利领先的电信运营商，由Massimiliano Brolli领导的TIM红队研究小组发现了Schneider Electric
EcoStruxure Building Operation中6个新的安全漏洞。该厂商已在2020年4月至2020年11月之间修复了这些漏洞。

![1606985308_5fc8a65cbbe9693937289.png!small](https://image.3001.net/images/20201203/1606985308_5fc8a65cbbe9693937289.png!small)

Schneider Electric（施耐德电气）是一家专业生产能源和自动化产品的厂商，例如ICS、SCADA和IoT产品。EcoStruxure
Building Operation是一款与物理设备集成的软件，用于能源、照明、消防安全和HVAC的综合监控、控制和管理。

此次，TIM红队研究小组在EcoStruxure Building
Operation中发现了3个高危漏洞和3个中危漏洞，攻击者可利用这些漏洞实现一系列恶意意图，包括远程执行代码、窃取信息、导致拒绝服务等。

其中高危漏洞的信息概要如下：

CVE-2020-7569，CVSS v3基准评分8.8，该漏洞影响EcoStruxure Building Operation WebReports
1.9版本至3.1版本，由于该产品以错误的方式验证用户提交的文件，远程攻击者可利用该漏洞上传任意文件，从而实现远程执行代码。

CVE-2020-7572，CVSS v3基准评分8.8，该漏洞影响EcoStruxure Building Operation WebReports
1.9版本至3.1版本，该漏洞源于XML解析器的配置错误，远程攻击者可利用该漏洞注入任意XML代码，进而获取机密数据，或导致拒绝服务。

CVE-2020-28209，CVSS v3基准评分7.0，该漏洞影响EcoStruxure Building Operation Enterprise
Server installer 1.9版本至3.1版本和Enterprise Central installer
2.0版本至3.1版本，如果本地攻击者（Windows用户）获取了Connect
Agent服务二进制路径的至少一个子文件夹的write权限，则可利用该漏洞获取启动该服务的用户的权限。

此外，根据厂商发布的安全公告，网络安全公司Zerolynx也报告了一个中危跨站脚本漏洞（CVE-2020-28210）。该漏洞影响EcoStruxure
Building Operation WebStation 2.0版本至3.1版本。

\----------------------------------------------------------------------------------------------------------------
综合来源：Security Affairs, Schneider Electric, NVD  
综合编译：猫冬

