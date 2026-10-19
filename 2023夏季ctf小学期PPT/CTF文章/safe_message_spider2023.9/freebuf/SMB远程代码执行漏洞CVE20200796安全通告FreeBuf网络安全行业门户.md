**【漏洞名称】**

SMB远程代码执行漏洞（CVE-2020-0796），有安全研究者取名“SMBGhost”。

**【漏洞描述】**

微软3月11日发布3月例行更新，其中并未公布编号为CVE-2020-0796的高危漏洞资料，但该漏洞却最为引人注目。次日晚（2020年3月12日）微软正式发布CVE-2020-0796高危漏洞补丁。

SMB 3.1.1协议中处理压缩消息时，对其中数据没有经过安全检查，直接使用会引发内存破坏漏洞，可能被攻击者利用远程执行任意代码。

攻击者利用该漏洞无须权限即可实现远程代码执行，受黑客攻击的目标系统只需开机在线即可能被入侵。

该漏洞的后果十分接近永恒之蓝系列，都利用Windows
SMB漏洞远程攻击获取系统最高权限，WannaCry勒索蠕虫就是利用永恒之蓝系列漏洞攻击工具制造的大灾难。除了直接攻击SMB服务端造成RCE外，该漏洞得亮点在于对SMB客户端的攻击，攻击者可以构造特定的网页，压缩包，共享目录，OFFICE文档等多种方式触发漏洞进行攻击。

该漏洞并未出现在微软3月的例行更新列表，有国外安全厂商意外发布了有关该漏洞存在的消息，随后引发行业关注。

**【漏洞版本】**

漏洞不影响win7，漏洞影响Windows 10 1903之后的各个32位、64位版Windows，包括家用版、专业版、企业版、教育版。

Windows 10 Version 1903 for 32-bit Systems

Windows 10 Version 1903 for x64-based Systems

Windows 10 Version 1903 for ARM64-based Systems

Windows Server, Version 1903 (Server Core installation)

Windows 10 Version 1909 for 32-bit Systems

Windows 10 Version 1909 for x64-based Systems

Windows 10 Version 1909 for ARM64-based Systems

Windows Server, Version 1909 (Server Core installation)

正是目前主流操作系统版本，在个人、企业环境应用广泛。

**【漏洞类型】**

远程代码执行

**【漏洞等级】**

高危

**【编号】CVE-2020-0796**

**【漏洞影响】**

根据T-Sec网络资产风险监测系统（腾讯御知）提供的数据，目前全球范围可能存在漏洞的SMB服务总量约10万台，直接暴露在公网，可能成为漏洞攻击的首轮目标。

![SMB远程代码执行漏洞CVE-2020-0796安全通告](https://img.4hou.com/uploads/ueditor/php/upload/image/20200313/1584072252133034.jpeg)

对于政府机构、企事业单位网络中采用Windows 10
1903之后的所有终端节点，均为潜在攻击目标，黑客一旦潜入，可利用针对性的漏洞攻击工具在内网扩散，综合风险不亚于永恒之蓝，WannaCry勒索蠕虫就是利用永恒之蓝系列漏洞攻击工具制造的大灾难。

**【解决方案】**

企业用户：

1、推荐企业采用T-Sec 网络资产风险检测系统（腾讯御知）全面检测企业网络资产是否受安全漏洞影响。

T-Sec
网络资产风险检测系统（腾讯御知）是一款自动探测企业网络资产并识别其风险的产品。可全方位监控企业网站、云主机、小程序等资产存在的风险，包含弱口令检测、Web
漏洞扫描、违规敏感内容检测、网站篡改检测、挂马挖矿检测等多类资产风险。

![SMB远程代码执行漏洞CVE-2020-0796安全通告](https://img.4hou.com/uploads/ueditor/php/upload/image/20200313/1584072278135542.jpeg)

企业用户可扫描以下二维码，免费使用T-Sec 网络资产风险检测系统（yuzhi.qq.com）。

![SMB远程代码执行漏洞CVE-2020-0796安全通告](https://img.4hou.com/uploads/ueditor/php/upload/image/20200313/1584072289438547.jpeg)

2、T-Sec终端安全管理系统（腾讯御点）已率先升级，可拦截利用该漏洞的攻击：

![SMB远程代码执行漏洞CVE-2020-0796安全通告](https://img.4hou.com/uploads/ueditor/php/upload/image/20200313/1584072304194847.jpeg)

企业网管还可采用T-Sec终端安全管理系统（腾讯御点）的全网漏洞扫描修复功能，全网统一扫描、安装KB4551762补丁。

部署T-Sec终端安全管理系统（腾讯御点）拦截病毒木马入侵，更多信息可参考链接：https://s.tencent.com/product/yd/index.html。

3、 推荐企业用户部署T-Sec高级威胁检测系统（腾讯御界）对黑客攻击行为进行检测。

T-Sec高级威胁检测系统（腾讯御界），是基于腾讯安全能力、依托腾讯在云和端的海量数据，研发出的独特威胁情报和恶意检测模型系统，该系统可及时有效检测黑客对企业网络的各种入侵渗透攻击风险。参考链接：https://cloud.tencent.com/product/nta

![SMB远程代码执行漏洞CVE-2020-0796安全通告](https://img.4hou.com/uploads/ueditor/php/upload/image/20200313/1584072316139843.jpeg)

4、腾讯安全率先推出SMB远程代码执行漏洞扫描工具，管理员使用该工具可远程检测全网终端是否存在安全漏洞。

![SMB远程代码执行漏洞CVE-2020-0796安全通告](https://img.4hou.com/uploads/ueditor/php/upload/image/20200313/1584072335247092.jpeg)

![SMB远程代码执行漏洞CVE-2020-0796安全通告](https://img.4hou.com/uploads/ueditor/php/upload/image/20200313/1584072344334610.jpeg)

为避免被攻击者滥用，获取SMB远程代码漏洞扫描工具须申请，申请流程参考：

https://pc1.gtimg.com/softmgr/files/20200796.docx

5、企业用户也可使用Windows 更新安装补丁，在Windows设置中，点击“更新和安全”。

个人用户

1、个人用户也可直接运行Windows 更新，完成补丁的安装。

2、个人用户也可通过手动修改注册表，防止被黑客远程攻击：

运行regedit.exe，打开注册表编辑器，在HKLM\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters建立一个名为DisableCompression的DWORD，值为1，禁止SMB的压缩功能。

**【时间线】**

1、2020年3月11日，国外某厂家发布规则更新，披露疑似SMB严重漏洞；

2、微软发布临时缓解方案：https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/ADV200005

3、2020年3月11日，腾讯电脑管家官微发布“CVE-2020-0796：疑似微软SMB协议‘蠕虫级’漏洞初步通告”；

4、2020年3月12日23点，微软官方发布CVE-2020-0796安全公告；

5、2020年3月12日，腾讯安全发布远程无损检测工具。

参考链接：

https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2020-0796

  

