**在过去的一年中，俄罗斯最大的黑客组织APT28一直在扫描和探测互联网中存在漏洞的电子邮件服务器。据报告，APT28在过去十年中的主要使用鱼叉式网络钓鱼，针对特定目标精心设计电子邮件，APT28已用多种恶意软件感染受害者超过15年。**

##  邮件服务器扫描

鱼叉式网络钓鱼和恶意软件攻击仍然存在，APT28去年也开始对整个Internet进行扫描，在TCP端口445和1433上搜索存在漏洞的Webmail和Microsoft
Exchange
Autodiscover服务器。目前尚不清楚APT28对服务器发动了哪些攻击，估计他们会试图攻击未打补丁的系统，窃取敏感数据或将电子邮件服务器用在其他攻击活动中。

扫描IP归属地如下：

##
![](https://image.3001.net/images/20200326/1585229792_5e7cafe0913a2.png!small)![](https://image.3001.net/images/20200326/1585229772_5e7cafcc35f67.png!small)

##  信任关系钓鱼

除了服务器扫描之外，APT28还会通过VPN网络连接到合法公司的电子邮件服务器受感染电子邮件帐户。APT28会诱骗合法公司的员工，窃取公司电子邮件帐户登录凭据，或者进行暴力攻击破解帐户的密码。掌握了凭据后通过VPN登录受感染的帐户。

![](https://image.3001.net/images/20200326/1585227713_5e7ca7c130850.png!small)

APT28要么泄露他们发现的数据，要么使用受感染的电子邮件帐户向其他目标发送钓鱼邮件。电子邮件来自合法公司的真实员工，因此这些钓鱼活动更有效，为APT28提供了新的受害者登录凭证。绝大多数被盗的电子邮件帐户都位于阿联酋国防部门。

![](https://image.3001.net/images/20200326/1585227795_5e7ca813573c6.png!small)以下是APT28在2019年8月至2019年11月间入侵的电子邮件帐户公司。

##
![](https://image.3001.net/images/20200326/1585227839_5e7ca83f7f84a.png!small)

##  通过DNS SPF请求钓鱼

过去的两年仔细分析了所使用域DNS SPF的请求，观察到了大量该组织钓鱼活动。 2017年春季发现攻击者已为某些服务器分配了特定域名，
这些服务器被反复用于向Webmail目标发送钓鱼邮件。研究人员记录了域名所有DNS请求。

![](https://image.3001.net/images/20200326/1585228580_5e7cab24a8444.png!small)

其中一些域名是在2017年免费注册，活动目标包括两个美国的免费Webmail服务，一个俄罗斯的免费Webmail服务和一个伊朗的Webmail服务。

![](https://image.3001.net/images/20200326/1585228677_5e7cab85e47da.png!small)攻击者经常使用商业VPN服务连接到发送垃圾邮件的专用主机。垃圾邮件发送服务器在与目标邮件服务器的SMTP会话EHLO命令中使用了特定域名。

![](https://image.3001.net/images/20200326/1585228741_5e7cabc522ff9.png!small)图8显示了针对Yahoo的钓鱼活动。

##  总结和建议

APT28拥有足够的资源，可以根据目标进行长时间的网络攻击活动。他们的攻击范围很广，破坏DNS、钓鱼攻击、水坑攻击等。最近开始对Webmail和云服务进行直接攻击，该组织在未来几年仍将保持活跃。

由于攻击者使用了各种各样的工具和策略，因此组织必须确保其边界安全，减少任何潜在风险。可采取以下措施：

> 1、强制执行最小特权原则，限制流量，仅启用所需的服务并禁用过时或未使用的服务，将网络中的风险降到最低。  
> 2、修补安全漏洞，保持系统更新，创建强大的补丁管理策略，对已知和未知漏洞进行虚拟修补。  
> 3、定期监视基础结构，除了采用防火墙之外，还包括入侵检测和防御系统。  
> 4、启用双因素身份验证。  
> 5、对员工进行安全教育，提高对网络钓鱼技术和常见攻击的认识，禁止工作中使用个人邮箱和社交帐户。  
> 6、保持数据完整性，定期备份数据，加密存储敏感信息。

##  IOCs

IP addresses  |  First  |  Last  |  Activity  
---|---|---|---  
185.245.85[.]178  |  8/4/19  |  12/17/19  |  Phishing; scanning for port 445
and 1433  
81.19.210[.]149  |  5/22/19  |  9/20/19  |  Spam; scanning (webmail)  
82.118.242[.]171  |  10/1/19  |  12/9/19  |  Scanning (webmail)  
172.111.161[.]232  |  9/26/19  |  10/7/19  |  Spam  
89.238.178[.]14  |  9/20/19  |  12/9/19  |  VPN use  
185.227.68[.]214  |  12/1/19  |  2/18/20  |  Phishing and scanning  
Domains  |  Activity  
---|---  
0xf4a54cf56[.]tk  |  Credential phishing  
0xf4a5[.]tk  |  Credential phishing  
id24556[.]tk  |  Credential phishing  
546874[.]tk  |  Credential phishing  
id6589[.]com  |  Credential phishing  
id451295  |  Credential phishing  
change-password[.]ml  |  Credential phishing  
0x4fc271[.]tk  |  Credential phishing  
yahoo-change-password[.]com  |  Credential phishing  
  
***参考来源：[trendmicro](https://documents.trendmicro.com/assets/white_papers/wp-pawn-storm-in-2019.pdf)，由Kriston编译，转载请注明来自FreeBuf.COM**

  

