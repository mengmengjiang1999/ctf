**本文转载自雷神众测。** https://github.com/r0eXpeR/redteam_vul

## 目录

一、OA系统  
二、E-mail  
三、Web中间件  
四、源代码管理  
五、项目管理系统  
六、开源运维监控  
七、堡垒机

## 一、OA系统

###  **泛微(Weaver-Ecology-OA)**

 **泛微OA E-cology（CNVD-2019-32204）远程命令执行漏洞**  
a漏洞分析  
漏洞出现在e-cology的组件beanshell上，由于beanshell这个接口可被未授权访问，同时这个接口在接受用户请求时未进行相应过滤，最终导致远程命令执行。Beanshell，简单说，就是一个微型的java解释器，可嵌入到其他程序中，用于动态的执行java代码，类似于csharp中的动态编译特性。  
b影响版本  
E-cology 7.0  
E-cology 8.0  
E-cology 8.1  
E-cology 9.0  
c修复建议  
官方下载补丁  
d来源  
[https://github.com/r0eXpeR/redteam_vul
](https://github.com/r0eXpeR/redteam_vul)

**泛微OA WorkflowCenterTreeData接口注入**  
a漏洞分析  
该漏洞是由于OA系统的WorkflowCenterTreeData接口中涉及Oracle数据库的SQL语句缺乏安全检查措施所导致的，任意攻击者都可借SQL语句拼接时机注入恶意payload，造成SQL注入攻击。泛型微生态OA系统的WorkflowCenterTreeData接口在使用Oracle数据库时，由于内置sql语句分解不严密，导致其存在的sql注入漏洞。  
b影响版本  
所有使用了Oracle数据库的泛微网站都有可能受到影响  
c修复建议  
目前官方尚未发布漏洞补丁，所有使用了Oracle数据库的泛微网站都有可能受到影响，请相关网站管理人员在官方发布补丁前及时下线网站。  
d来源  
[https://github.com/r0eXpeR/redteam_vul
](https://github.com/r0eXpeR/redteam_vul)

**泛微ecology OA数据库配置信息泄露**  
a漏洞分析  
泛微e-cology OA系统/mobile/DBconfigReader.jsp存在未授权访问，通过解密，可直接获取数据库配置信息。  
b修复建议  
禁止访问 /mobile/DBconfigReader.jsp  
c来源  
[https://github.com/r0eXpeR/redteam_vul
](https://github.com/r0eXpeR/redteam_vul)

**泛微OA云桥未授权任意文件读取**  
a漏洞分析  
泛微云桥（e-Bridge）是上海泛微公司在”互联网+”的背景下研发的一款用于桥接互联网开放资源与企业信息化系统的系统集成中间件。泛微云桥存在任意文件读取漏洞，攻击者成功利用该漏洞，可实现任意文件读取，获取敏感信息。  
b影响版本  
2018-2019 多个版本  
c修复建议  
关闭程序路由 /file/fileNoLogin  
d来源  
[https://www.cnblogs.com/yuzly/p/13677238.html
](https://www.cnblogs.com/yuzly/p/13677238.html)

**泛微ecology OA前台SQL注入漏洞**  
a漏洞分析  
该漏洞是由于OA系统的WorkflowCenterTreeData接口在收到用户输入的时候未进行安全过滤，oracle数据库传入恶意SQL语句，导致SQL漏洞。  
b影响范围  
使用oracle数据库的泛微 e-cology OA 系统  
c修复建议  
官网已更新补丁，请尽快更新  
d来源  
[https://www.cnblogs.com/ffx1/p/12653555.html
](https://www.cnblogs.com/ffx1/p/12653555.html)

**泛微OA系统
/ServiceAction/com.eweaver.base.security.servlet.LoginAction参数keywordid
SQL注入漏洞**  
a漏洞分析  
泛微OA系统在  
/ServiceAction/com.eweaver.base.security.servlet.LoginAction处对参数keywordid过滤不严格，导致出现SQL注入漏洞。远程攻击者可以利用该漏洞读取敏感信息。  
b影响范围  
使用oracle数据库的泛微电子OA系统  
c修复建议  
官网已更新补丁，请尽快更新  
d来源  
https://www.seebug.org/vuldb/ssvid-91089

### 致远(Seeyon)

 **致远 OA A8 htmlofficeservlet getshell漏洞**

a漏洞分析  
致远 OA 在国内的用户也比较多, 2019年攻防演练暴出来 htmlofficeservlet getshell 漏洞。  
b影响范围  
致远A8-V5协同管理软件 V6.1sp1  
致远A8+协同管理软件 V7.0、V7.0sp1、V7.0sp2、V7.0sp3  
致远A8+协同管理软件 V7.1  
c修复建议  
1.及时更新补丁  
2.使用waf拦截  
d来源  
[https://www.cnblogs.com/nul1/p/12803555.html
](https://www.cnblogs.com/nul1/p/12803555.html)

**致远OA A8未授权访问**  
a漏洞分析  
致远A8-V5协同管理软件存在未授权访问，可以利用普通用户权限访问system权限页面，获取大量缓存信息，如用户信息。利用之前提交的漏洞“致远A8-V5协同管理软件日志信息泄露(通杀V5)”获取到的某弱口令用户对http://a8v51.seeyon.com进行测试，发现致远A8-V5协同管理软件还存在未授权访问，可以利用普通用户权限访问system权限页面，获取大量缓存信息。  
b影响范围  
致远OA A8  
c修复建议  
官方下载最新版本  
d来源  
[https://www.cnblogs.com/AtesetEnginner/p/12106741.html
](https://www.cnblogs.com/AtesetEnginner/p/12106741.html)

**致远A8-V5存在任意用户密码修改漏洞**  
a漏洞分析  
致远A8-V5存在两个漏洞：  
一是无视验证码撞库，致远A8-V5在设计时存在逻辑错误，用户修改密码时对原密码进行了验证，但是验证使用的服务存在未授权访问漏洞，系统对非合法请求的原密码验证功能进行回应，导致了无视验证码，无需login页面进行密码尝试。

二是任意用户密码修改，致远A8-V5在设计时存在逻辑错误，在上一步对原始密码进行验证后，下一步不再检测原始密码，从而直接修改用户密码，导致平行权限的越权漏洞。  
b影响范围  
致远OA A8-V5  
c修复建议  
漏洞位置为：/seeyon/htmlofficeservlet，可以对该地址配置ACL规则。  
或者联系官方获取补丁程序，官网地址：  
http://www.seeyon.com/Info/constant.html  
d来源  
[http://wy.zone.ci/bug_detail.php?wybug_id=wooyun-2015-0104942
](http://wy.zone.ci/bug_detail.php?wybug_id=wooyun-2015-0104942)

### 通达OA(TongDa OA)

 **通达OA任意文件删除 &文件上传RCE**  
a漏洞分析  
通过任意文件漏洞删除上传点包含的身份验证文件，从而造成未授权访问实现任意文件上传。  
b影响范围  
通达OA V11.6  
c修复建议  
升级版本  
d来源  
[https://xz.aliyun.com/t/8430 ](https://xz.aliyun.com/t/8430)

**通达OA任意文件上传/文件包含GetShell**  
a漏洞分析  
通过绕过身份认证, 攻击者可上传任意文件，配合文件包含即可出发远程恶意代码执行。  
b影响范围  
V11  
2017  
2106  
2105  
2013  
c修复建议  
更新官方发布的补丁  
d来源  
[https://xz.aliyun.com/t/7437 ](https://xz.aliyun.com/t/7437)

**通达OA任意用户登录漏洞**  
a漏洞分析  
未授权的攻击者可以通过构造恶意请求进行任意用户登录，从而进一步攻击接管服务器权限。攻击者利用此漏洞 可以接管服务器权限。  
b影响版本  
通达OA2017、V11.X<V11.5  
c修复建议  
官方已发布最新修正版本，请及时更新补丁  
d来源  
[http://www.adminxe.com/1095.html ](http://www.adminxe.com/1095.html)

**通达OA 11.2后台getshell**  
a漏洞分析  
通达OA 11.2 "组织"-》"管理员"-》附件上传处存在任意文件上传漏洞，结合
"系统管理"-》"附件管理"-》"添加存储目录"，修改附件上传后保存的路径，最终导致getshell。  
b影响版本  
通达OA 11.2  
c修复建议  
升级版本  
d来源  
[https://www.cnblogs.com/yuzly/p/13606314.html
](https://www.cnblogs.com/yuzly/p/13606314.html)

**通达OA 11.7后台sql注入漏洞**  
a漏洞分析  
通达OA 11.7存在sql注入。  
b影响版本  
通达oa 11.7  
c修复建议  
升级版本  
d来源  
[https://www.cnblogs.com/yuzly/p/13690737.html
](https://www.cnblogs.com/yuzly/p/13690737.html)

**通达OA 11.7未授权RCE**  
a漏洞分析  
通达OA（Office
Anywhere网络智能办公系统）是由北京通达信科科技有限公司自主研发的协同办公自动化软件，是与中国企业管理实践相结合形成的综合管理办公平台。漏洞主要分为两个点，一个是文件上传，一个是文件包含。  
b影响版本  
通达OA V11版 <= 11.3 20200103  
通达OA 2017版 <= 10.19 20190522  
通达OA 2016版 <= 9.13 20170710  
通达OA 2015版 <= 8.15 20160722  
通达OA 2013增强版 <= 7.25 20141211  
通达OA 2013版 <= 6.20 20141017  
c修复建议  
及时安装官方补丁

由于通达oa默认过滤了大部分执行命令的函数，所以想要执行命令请参考使用com组件绕过disable_function。  
d来源  
[https://www.adminxe.com/1003.html ](https://www.adminxe.com/1003.html)

## 二、E-mail

### Exchange

**Microsoft Exchange Server 远程代码执行漏洞(CVE-2020-17083)**  
a漏洞分析  
漏洞使远程攻击者可以在受影响的Exchange Server安装上执行任意代码。若要利用此漏洞，需要使用“ Exchange
Server证书”角色进行身份验证。

在处理Export-ExchangeCertificate
cmdlet期间，WriteCertiricate函数中存在特定缺陷。造成此问题的原因是，在编写文件时缺少对用户提供的数据的正确验证。攻击者可以利用此漏洞在SYSTEM上下文中执行代码。  
b影响范围  
Microsoft Exchange服务器  
c修复建议  
Microsoft已发布更新来纠正此漏洞。可以在以下位置找到更多详细信息：  
https://msrc.microsoft.com/update-guide/zh-CN/vulnerability/CVE-2020-17083  
d来源  
https://srcincite.io/advisories/src-2020-0025/

 **Microsoft Exchange远程代码执行突破（CVE-2020-16875）**  
a漏洞分析  
由于对cmdlet参数的验证不正确，Microsoft
Exchange服务器中存在一个远程执行代码漏洞。成功利用此漏洞的攻击者可以在系统用户的上下文中运行任意代码。利用此漏洞需要拥有以某个Exchange角色进行身份验证的用户权限。  
b影响范围  
microsoft:exchange_server_2016: cu16/cu17  
microsoft:exchange_server_2019: cu5/cu6  
c修复建议  
通过如下链接自行寻找符合操作系统版本的漏洞补丁，并进行补丁下载安装。  
CVE-2020-16875 | Microsoft Exchange远程代码执行漏洞：  
https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2020-16875  
d建议  
[https://blog.csdn.net/weixin_45728976/article/details/108537236
](https://blog.csdn.net/weixin_45728976/article/details/108537236)

**微软EXCHANGE服务的远程代码执行漏洞(CVE-2020-0688)**  
a漏洞分析  
攻击者向存在缺陷的Exchange服务器发送经过特殊处理的电子邮件即可触发中断。这个突破是由于Exchange服务器在安装时没有正确地创建唯一的加密密钥所造成的。

具体来说，与每次软件安装都会产生随机密钥不同，所有Exchange服务器在安装后的web.config文件文件中都拥有相同的的validationKey和decryptionKey。这些密钥用于保证ViewState中的安全性。而ViewState是ASP.NET
Web应用以序列化格式存储在上面的服务端数据。客户端通过__VIEWSTATE请求参数将这些数据返回给服务器。攻击者可以在Exchange控制面板中web应用上执行任意.net代码。  
b影响版本  
exchange 2010、2013、2016、2019全版本通杀。  
c修复建议  
获取Exchange Server版本号，获取方式可参考如下：  
https://docs.microsoft.com/zh-cn/exchange/new-features/build-numbers-and-release-dates?view=exchserver-2019  
获取到版本好之后，查看是否受影响：  
https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2020-16875  
受影响的话，则直接下载对应的安全更新包进行更新即可。  
d来源  
[https://xz.aliyun.com/t/7321 ](https://xz.aliyun.com/t/7321)

**Microsoft Exchange任意用户伪造漏洞**  
a漏洞分析  
这种假冒是由于SSRF漏洞与其他漏洞结合在一起而发生的。Exchange允许任何用户为“推送订阅”指定所需的URL，服务器将尝试向该URL发送通知。  
b修复建议  
微软给这个漏洞分配了CVE-2018-8581并且在11月发布分版本中修补了这个问题。实际上没有修补程序可以纠正此问题。而是，Microsoft指出应该删除注册表项。删除此密钥将启用回送检查。  
c来源  
[https://xz.aliyun.com/t/3670 ](https://xz.aliyun.com/t/3670)

### Coremail

 **coremail 配置信息泄露及接口未授权漏洞**  
a漏洞分析  
Coremail邮件系统是论客科技（广州）有限公司（以下简称论客公司）自主研发的大型企业邮件系统，为客户提供电子邮件整体技术解决方案及企业邮局运营服务。  
Coremail邮件系统作为我国第一套中文邮件系统，客户范围涵盖党政机关、高校、知名企业以及能源、电力、金融等重要行业单位，在我国境内应用较为广泛。由于Coremail邮件系统的mailsms模块的参数大小写敏感存在缺陷，使得攻击者利用该漏洞，在未授权的情况下，通过远程访问URL地址获知Coremail服务器的系统配置文件，造成数据库连接参数等系统敏感配置信息泄露。  
b影响版本  
Coremail XT 3.0.1至XT 5.0.9版本  
c修复建议  
目前，论客公司已发布补丁进行修复，针对Coremail XT5和Coremail
XT3/CM5版本，补丁编号为CMXT5-2019-0002，程序版本1.1.0-alphabuild20190524（3813d273）。  
如已安装的程序包的版本号日期早于20190524，建议用户及时更新补丁：用户可以在Coremail云服务中心的补丁管理模块，根据补丁编号下载并按照操作指引进行手动更新。  
如有疑问，也可通过400-888-2488 或 support@coremail.cn 联系厂商售后人员提供协助。  
d来源  
<https://blog.csdn.net/u012206617/article/details/109579890>

## 三、Web中间件

### Apache

 **Apache Solr RCE—（CVE-2019-0192）**  
a漏洞分析  
Apache Solr是一个开源的搜索服务器。具有高度可靠、可伸缩和容错的，提供分布式索引、复制和负载平衡查询、自动故障转移和恢复、集中配置等功能。  
Solr为世界上许多最大的互联网站点提供搜索和导航功能。Solr 使用 Java 语言开发，主要基于 HTTP 和 Apache Lucene
实现ConfigAPI允许设置一个jmx.serviceUrl，它将创建一个新的 JMXConnectorServerFactory 并触发对目标RMI /
LDAP服务器进行“绑定”操作的调用。恶意的RMI服务器可能会响应任意对象，然后使用Java的ObjectInputStream在Solr端反序列化该对象，这被认为是不安全的。可以使用ysererial工具利用这种类型的漏洞。根据目标类路径，攻击者可以使用“小配件链”之一在Solr端触发远程代码执行。  
b修复建议  
升级到Apache Solr 7.0或更高版本。  
通过使用系统属性disable.configEdit = true运行Solr，禁用ConfigAPI（如果未使用）。  
如果升级或禁用Config API不可行，请应用SOLR-13301.patch并重新编译Solr。  
确保配置了网络设置，以便只允许受信任的流量进入/退出运行Solr的主机。  
c来源  
https://blog.csdn.net/yalecaltech/article/details/88829590

 **Apache Tika 命令注入(CVE-2018-1335)**  
a漏洞分析  
Apache Tika™ 工具集可以检测和提取上千种不同文件类型（比如PPT,XLS,PDF等）中的元数据和文本。用户可以发送精心构造的标头至tika-server，这些标头能够用来注入一些命令到运行tika-server的服务器的命令行中。此漏洞只影响向不受信用户开放并且运行tika-server的服务器。  
b影响版本  
1.18版本  
1.17版本  
c修复建议  
Apache官方不建议使用者在不安全环境下运行Tika-server，并且暴露给不受信的用户。现在最新的版本为1.20，如果你仍在使用该服务请立即更新！  
d来源  
<https://xz.aliyun.com/t/4452>

 **Apache Axis1 RCE**  
a漏洞分析  
ache Axis™是一个简单对象访问协议（SOAP）引擎。在最近的一次红队行动中，我们发现目标装有老版本的Apache
Axis（1.4）。现在较新的有Apache Axis2, Apache CXF,和Metro等。尽管Apache
Axis已经过时，但它仍然在许多情况下被使用，例如使用Axis构造的项目难以重写或者项目中含有使用SOAP编码的服务。Axis以管理员权限处理localhost的请求，攻击者可以通过SSRF漏洞修改HTTP
GET请求部分来伪装成localhost用户。  
b影响版本  
<=1.4版本  
c修复建议  
Apache团队已经推出Axis的补丁程序，该修补程序可以防止滥用XMLUtils.newDocument重定向。  
d来源  
<https://xz.aliyun.com/t/4768>

 **Tomcat信息泄漏和远程代码执行漏洞（CVE-2017-12615/CVE-2017-12616）**  
a漏洞分析  
CVE-2017-12616：信息泄露漏洞：当Tomcat中启用了
VirtualDirContext时，攻击者将能通过发送精心构造的恶意请求，绕过设置的相关安全限制，或是获取到由VirtualDirContext提供支持资源服务的JSP源代码，从而造成代码信息泄露。

CVE-2017-12615：远程代码执行漏洞：当 Tomcat运行在Windows操作系统时，且启用了HTTP PUT请求方法（例如，将 readonly
初始化参数由默认值设置为 false），攻击者将有可能可通过精心构造的攻击请求数据包向服务器上传包含任意代码的 JSP
文件，JSP文件中的恶意代码将能被服务器执行。导致服务器上的数据泄露或获取服务器权限。  
在一定的条件下，通过以上两个漏洞可在用户服务器上执行任意代码，从而导致数据泄露或获取服务器权限，存在高安全风险。  
b影响版本  
CVE-2017-12615影响范围：  
Apache Tomcat 7.0.0 - 7.0.79 (windows环境)  
CVE-2017-12616影响范围：  
Apache Tomcat 7.0.0 - 7.0.80  
c修复建议  
目前官方已经发布了7.0.81版本修复了两个漏洞，建议用户尽快升级到最新版本；  
对于最新版本绕过的问题，建议用户持续关注官方信息，及时更新到最新版本；  
d来源  
<https://xz.aliyun.com/t/54>

 **Tomcat本地提权漏洞（CVE-2016-1240）**  
a 漏洞分析  
Debian系统的Linux上管理员通常利用apt-get进行包管理，CVE-2016-1240这一漏洞其问题出在Tomcat的deb包中,使
deb包安装的Tomcat程序会自动为管理员安装一个启动脚本：/etc/init.d/tomcat<版本号>.sh。利用该脚本，可导致攻击者通过低权限的Tomcat用户获得系统root权限。  
b 修复建议  
目前，Debian、Ubuntu等相关操作系统厂商已修复并更新受影响的Tomcat安装包。受影响用户可采取以下解决方案：

更新Tomcat服务器版本：  
（1）针对Ubuntu公告链接  
http://www.ubuntu.com/usn/usn-3081-1/  
（2）针对Debian公告链接  
https://lists.debian.org/debian-security-announce/2016/msg00249.html  
https://www.debian.org/security/2016/dsa-3669  
https://www.debian.org/security/2016/dsa-3670  
c 来源  
https://blog.csdn.net/jlvsjp/article/details/52776377

### Weblogic

 **Weblogic未经授权的旁路RCE（CVE-2020–14882）**  
a 漏洞分析  
远程攻击者可以构造特殊的HTTP请求，在未经身份验证的情况下接管 WebLogic Server Console ，并在 WebLogic Server
Console 执行任意代码。远程攻击者可以构造特殊的HTTP请求，在未经身份验证的情况下接管 WebLogic Server Console ，并在
WebLogic Server Console 执行任意代码。  
b影响版本  
Oracle:Weblogic:  
10.3.6.0.0  
12.1.3.0.0  
12.2.1.3.0  
12.2.1.4.0  
14.1.1.0.0  
c修复建议  
及时更新补丁，参考oracle官网发布的补丁:  
Oracle Critical Patch Update Advisory - October 2020  
https://www.oracle.com/security-alerts/cpuoct2020traditional.html  
d来源  
https://blog.csdn.net/weixin_45728976/article/details/109359771

Weblogic 远程命令执行漏洞分析（CVE-2019-2725）  
a漏洞分析  
由于在反序列化处理输入信息的过程中存在缺陷，授权的攻击者可以发送精心构造的恶意HTTP请求，利用该漏洞获取服务器权限，实现远程代码执行。  
b影响版本  
Oracle WebLogic Server 10. *  
Oracle WebLogic Server 12.1.3版  
c修复建议  
官方目前已发布针对此突破的紧急修复补丁，可以采取以下4种方式进行防护。  
1.及时打上官方CVE-2019-2725补丁包官方已于4月26日发布紧急补丁包，下载地址如下：  
https://www.oracle.com/technetwork/security-advisory/alert-cve-2019-2725-5466295.html?from=timeline  
2.升级本地JDK版本  
因为Weblogic所采用的是其版本文件JDK文件的版本，属于存在的反序列化漏洞的JDK版本，因此升级到JDK7u21以上版本可以避免由于Java本机类反序列化破坏造成的远程代码执行。  
3.配置URL访问控制策略  
部署于公网的WebLogic服务器，可通过ACL禁止对/ _async / *及/ wls-wsat / *路径的访问。  
4.删除不安全文件  
删除wls9_async_response.war与wls-wsat.war文件及相关文件夹，并重新启动Weblogic服务。  
d来源  
<https://www.anquanke.com/post/id/177381>

 **WebLogic XMLDecoder反序列化漏洞（CVE-2017-10271）**  
a漏洞分析  
WebLogic
WLS组件中存在CVE-2017-10271远程代码执行漏洞，可以构造请求对运行WebLogic中间件的主机进行攻击，发现此漏洞的利用方式为传播挖矿程序。  
b影响版本  
10.3.6.0.0  
12.1.3.0.0  
12.2.1.1.0  
12.2.1.2.0  
c修复建议  
前往Oracle官网下载10月份所提供的安全补丁  
http://www.oracle.com/technetwork/security-advisory/cpuoct2017-3236626.html  
升级过程可参考：  
http://blog.csdn.net/qqlifu/article/details/49423839  
d来源  
<https://www.cnblogs.com/xiaozi/p/8205107.html>

 **Weblogic任意文件读取漏洞（CVE-2019-2615)）and 文件上传漏洞（CVE-2019-2618）漏洞**  
a漏洞描述  
该漏洞是任意文件读取漏洞，攻击者可以在已知用户名密码的情况下读取WebLogic服务器中的任意文件。  
b影响版本  
Weblogic 10.3.6.0  
Weblogic 12.1.3.0  
Weblogic 12.2.1.2  
Weblogic 12.2.1.3  
c修复建议  
升级补丁  
Oracle官方更新链接地址：  
https://www.oracle.com/technetwork/security-advisory/cpuapr2019-5072813.html。  
d来源  
<https://www.venustech.com.cn/new_type/aqldfx/20190417/18464.html>

 **Weblogic coherence组件iiop反序列化漏洞 (CVE-2020-14644)**  
a漏洞分析  
WebLogic的核心coherence组件存在严重的安全漏洞，可以在无需账户登录的情况下，通过发送精心恶意的IIOP协议数据包，进行反序列化攻击完成远程任意命令执行。  
b影响版本  
WebLogic 12.2.1.3.0  
WebLogic 12.2.1.4.0  
WebLogic 14.1.1.0.0  
c修复建议  
官方下载补丁  
地址：  
https://www.oracle.com/security-alerts/cpujul2020.html  
d来源  
<https://xz.aliyun.com/t/8155>

 **Weblogic远程代码执行漏洞（CVE-2021-2109）**  
a漏洞分析  
WebLogic是美国Oracle公司的主要产品之一，是商业市场上主要的 J2EE 应用服务器软件，也是世界上第一个成功商业化的J2EE应用服务器，在
Java
应用服务器中有非常广泛的部署和应用。该漏洞允许未经身份验证的攻击者通过IIOP,T3进行网络访问，未经身份验证的攻击者成功利用此漏洞可能接管Oracle
WebLogic Server。  
b影响版本  
Weblogic Server 10.3.6.0.0、12.1.3.0.0、12.2.1.3.0、12.2.1.4.0、14.1.1.0.0  
c修复建议  
建议受影响的用户参考Oracle官方网站的公告尽快修复  
d来源  
<https://www.oracle.com/security-alerts/cpujan2021.html>

 **WebLogic CVE-2020-14756 T3/IIOP反序列化RCE**  
a漏洞分析  
Oracle融合中间件的Oracle Coherence产品（组件：核心组件）中的漏洞。 易于利用的漏洞允许未经身份验证的攻击者通过IIOP
T3进行网络访问，从而危害Oracle Coherence。成功攻击此漏洞可能导致Oracle Coherence被接管。  
b影响版本  
3.7.1.0、12.1.3.0.0、12.2.1.3.0、12.2.1.4.0和14.1.1.0.0  
c修复建议  
官方下载补丁  
地址：  
https://www.oracle.com/security-alerts/cpujan2021.html  
d来源  
https://nvd.nist.gov/vuln/detail/CVE-2020-14756

### JBoss

 **CVE-2017-7504-JBoss JMXInvokerServlet 反序列化**  
a漏洞分析  
这是经典的JBoss反序列化漏洞，JBoss在/invoker/JMXInvokerServlet请求中读取了用户传入的对象，然后利用Apache
Commons Collections中的Gadget执行任意代码。  
b影响版本  
JBoss Enterprise Application Platform 6.4.4,5.2.0,4.3.0_CP10  
JBoss AS (Wildly) 6 and earlier  
JBoss A-MQ 6.2.0  
JBoss Fuse 6.2.0  
JBoss SOA Platform (SOA-P) 5.3.1  
JBoss Data Grid (JDG) 6.5.0  
JBoss BRMS (BRMS) 6.1.0  
JBoss BPMS (BPMS) 6.1.0  
JBoss Data Virtualization (JDV) 6.1.0  
JBoss Fuse Service Works (FSW) 6.0.0  
JBoss Enterprise Web Server (EWS) 2.1,3.0  
c修复建议  
更新Apache Commons Collections库 lib地址:  
https://github.com/ikkisoft/SerialKiller  
下载这个jar后放置于classpath，将应用代码中的java.io.ObjectInputStream替换为SerialKiller

之后配置让其能够允许或禁用一些存在问题的类，SerialKiller有Hot-Reload、Whitelisting、Blacklisting几个特性，控制了外部输入反序列化后的可信类型。  
d来源  
<https://paper.seebug.org/312/>

 **JBoss 5.x和6.x 反序列化漏洞（CVE-2017-12149）**  
a漏洞分析  
JBOSS Application
Server是一个基于J2EE的开放源代码的应用服务器。JBoss代码遵循LGPL许可，可以在任何商业应用中免费使用。该漏洞为
Java反序列化错误类型，存在于 Jboss 的 HttpInvoker 组件中的
ReadOnlyAccessFilter过滤器中。该过滤器在没有进行任何安全检查的情况下尝试将来自客户端的数据流进行反序列化，从而导致了攻击者可以在服务器上执行任意代码。  
b影响版本  
漏洞影响5.x和6.x版本的JBOSSAS  
c修复建议  
建议用户升级到JBOSS AS7。另，不能及时升级的用户，可采取如下临时解决方案：  
1.不需要 http-invoker.sar 组件的用户可直接删除此组件。  
2.添加如下代码至 http-invoker.sar 下 web.xml 的 security-constraint 标签中：<url-pattern>/*</url-pattern>用于对 http invoker 组件进行访问控制。  
d来源  
http://www.cnblogs.com/Oran9e/p/7897102.html

 **JBoss 4.x JBossMQ JMS 反序列化漏洞（CVE-2017-7504）**  
a漏洞分析  
JbossMQ实现的HTTP调用层上的JMS中的HTTPServerILServlet.java，默认情况下在Red Hat Jboss
Application Server <= Jboss 4.X中启用，它不限制其执行反序列化的类，这允许远程攻击者执行任意代码通过精心制作的序列化数据。  
b影响版本  
<=4.x  
c修复建议  
1.将JBoss版本升级到最新  
2.尽量不要将JBoss映射到公网  
d来源  
<https://nvd.nist.gov/vuln/detail/CVE-2017-7504>

 **JBOSS远程代码执行漏洞**  
a漏洞分析  
JBOSS默认配置会有一个后台漏洞，漏洞发生在jboss.deployment命名空间中的addURL()函数,该函数可以远程下载一个war压缩包并解压  
访问http://www.safe3.com.cn:8080/jmx-console/ 后台。  
b修复建议  
给jmx-console加上访问密码  
1.在 ${jboss.server.home.dir}/deploy下面找到jmx-console.war目录编辑WEB-INF/web.xml文件 去掉
security-constraint 块的注释，使其起作用

2.编辑WEB-INF/classes/jmx-console-users.properties或server/default/conf/props/jmx-console-users.properties
(version >=4.0.2)和 WEB-INF/classes/jmx-console-roles.properties  
或server/default/conf/props/jmx-console-roles.properties(version >=4.0.2)
添加用户名密码

3.编辑WEB-INF/jboss-web.xml去掉 security-domain 块的注释 ，security-domain值的映射文件为
login-config.xml （该文件定义了登录授权方式）  
c来源  
<https://www.cnblogs.com/Safe3/archive/2010/01/08/1642371.html>

 **Jboss未授权访问漏洞**  
a漏洞分析  
JBoss是一个基于J2EE的开放源代码应用服务器，代码遵循LGPL许可，可以在任何商业应用中免费使用；JBoss也是一个管理EJB的容器和服务器，支持EJB
1.1、EJB 2.0和EJB3规范。在低版本中，默认可以访问Jboss web控制台，无需用户名和密码。  
b影响版本  
JBOSS 全版本  
c修复建议  
关闭jmx-console和web-console，提高安全性。  
d来源  
<http://www.manongjc.com/detail/14-tjkcvyvhmnupndv.html>

## 四、源代码管理

### GitLab

 **GitLab 12.9.0任意文件读取（CVE-2020-10977）**  
a漏洞分析  
当项目之间发生移动问题时，可以读取任意本地文件。  
b影响版本  
影响GitLab EE / CE 8.5及更高版本  
c修复建议  
强烈建议尽快将所有运行上述受影响版本的安装升级到最新版本  
d来源  
<https://about.gitlab.com/releases/2020/03/26/security-release-12-dot-9-dot-1-released/>

 **GitLab远程代码执行突破-（CVE-2018-14364）**  
a漏洞分析  
可以绕过文件名正则表达式，并使攻击者可以通过导入特制的Gitlab导出在Gitlab上传目录中创建符号链接。此外，Gitlab设计为当前不删除项目上载目录。因此，攻击者可以删除导入的项目，然后将另一个特制的Gitlab导出上传到具有相同名称的项目，这会导致路径遍历/任意文件上传，并最终使攻击者能够在以下用户的许可下获取shell：系统gitlab用户。  
b影响版本  
> = 8.9.0  
c修复建议  
建议官方下载补丁  
地址：  
https://dev.gitlab.org/gitlab/gitlabhq/merge_requests/2440  
d来源  
<https://gitlab.com/gitlab-org/gitlab-ce/issues/49133>

 **GitLab 任意文件读取漏洞 (CVE-2016-9086) 和任意用户 token 泄露漏洞**  
a漏洞分析  
itLab 是一个利用Ruby on
Rails开发的开源应用程序，实现一个自托管的Git项目仓库，可通过Web界面进行访问公开的或者私人项目。研究发现在其多个版本中存在文件读取漏洞(CVE-2016-9086)
和 任意用户authentication_token泄漏漏洞，攻击者可以通过这两个漏洞来获取管理员的权限，进而控制所有gitlab项目。  
b影响版本  
任意文件读取漏洞(CVE-2016-9086):  
GitLab CE/EEversions 8.9, 8.10, 8.11, 8.12, and 8.13  
任意用户authentication_token泄露漏洞：  
Gitlab CE/EE versions 8.10.3-8.10.5  
c修复建议  
官方下载补丁  
地址：  
https://github.  
d来源  
<https://hackerone.com/reports/178152>

## 五、项目管理系统

### 禅道

 **禅道CMS文件上传漏洞（CNVD-C-2020-121325）**  
a漏洞分析  
禅道CMS<=12.4.2版本存在文件上传漏洞，该漏洞由于开发者对link参数过滤不严，导致攻击者对下载链接可控，导致可远程下载服务器恶意脚本文件，造成任意代码执行，获取webshell。  
b影响版本  
禅道CMS<=12.4.2版本  
c修复建议  
建议升级到禅道12.4.3以上版本  
d来源  
<https://blog.csdn.net/qq_36197704/article/details/109385695>

 **禅道12.4.2后台管理员权限Getshell**  
a漏洞分析  
禅道12.4.2版本存在任意文件下载漏洞，该漏洞是因为client类中download方法中过滤不严谨可以使用ftp达成下载文件的目的。且下载文件存储目录可解析php文件，造成getshell。  
b影响版本  
禅道≤ 12.4.2  
c修复建议  
升级到禅道12.4.3及之后的版本  
d来源  
<https://www.cnblogs.com/ly584521/p/13962816.html>

 **禅道9.12权限控制逻辑漏洞**  
a漏洞分析  
ZenTaoPMS（ZenTao Project Management
System），中文名为禅道项目管理软件。ZenTaoPMS是易软天创公司为了解决众多企业在管理过程中出现的混乱，无序的现象，开发出来的一套项目管理软件。  
b影响版本  
这个漏洞目前影响至禅道最新版9.1.2  
c修复建议  
建议官方下载最新版本  
d来源  
<https://xz.aliyun.com/t/186>

 **禅道远程代码执行漏洞**  
a漏洞分析  
此次发现的漏洞正是ZenTaoPHP框架中的通用代码所造成的的，因此禅道几乎所有的项目都受此漏洞影响。普通权限（用户组为1-10）的攻击者可通过module/api/control.php中getModel方法，越权调用module目录下所有的model模块和方法，从而实现SQL注入、任意文件读取、远程代码执行等攻击。  
b影响范围  
禅道几乎所有的项目  
c修复建议  
如果想要修复这个漏洞，最简单的办法就是删除这个getModel接口。  
d来源  
<http://foreversong.cn/archives/1410>

 **禅道 11.6 任意文件读取**  
a漏洞分析  
禅道项目管理软件是一款国产的，基于LGPL协议，开源免费的项目管理软件，它集产品管理、项目管理、测试管理于一体，同时还包含了事务管理、组织管理等诸多功能，是中小型企业项目管理的首选，基于自主的PHP开发框架──ZenTaoPHP而成，第三方开发者或企业可非常方便的开发插件或者进行定制。

禅道 11.6 版本中对用户接口调用权限过滤不完善，导致调用接口执行SQL语句导致SQL注入。  
b影响版本  
禅道 11.6  
c修复建议  
官网下载最新版本  
下载地址：  
https://www.zentao.net/download.html  
d来源  
<https://www.zhihuifly.com/t/topic/3363>

### Jira

 **Jira SSRF跳转漏洞（CVE-2017-9506）**  
a漏洞分析  
Atlassian
OAuth插件是大多数Atlassian产品（例如Jira和Confluence）的一部分。它存在一个漏洞，该漏洞允许未经验证的来自服务器的HTTP
GET请求执行。您可以使用它执行各种有趣的操作，例如访问内部网络上的资源或使用有效的TLS连接欺骗页面。  
b影响版本  
Jira < 7.3.5  
c修复建议  
如果您发现Atlassian产品容易受到攻击，请通知管理员，并要求他阻止URL或升级到产品的更高版本。  
d来源  
<http://dontpanic.42.nl/2017/12/there-is-proxy-in-your-atlassian.html>

 **Jira服务工作台路径遍历导致的敏感信息泄露漏洞**  
a漏洞分析  
JIRA Servcie
Desk是Atlassian旗下JIRA类应用的核心产品，它是一款服务台管理软件，专门用于接受和处理来自于团队或用户的问题或请求它还有其他类似于服务中心的附属功能包括处理服务协议、报告、队列，通过网站入口或者邮件等形式接收来自外部的问题及反馈。JIRA
Servcie Desk是专门为终端用户提交工单到客户支持团队而设计的，它也可适用于开发团队，可与JIRA
Software等同类产品配合使用。如果攻击者是可以访问用户门户（Customer
portal）的普通用户，那么，他就能遍历管理员门户（Administrative portal）中JIRA项目提交的所有实例问题清单，这些项目包括Jira
Service Desk自身、Jira Core projects以及Jira Software等。  
b影响版本  
All versions before 3.9.16  
3.10.x  
3.11.x  
3.12.x  
3.13.x  
3.14.x  
3.15.x  
3.16.x before 3.16.8 (the fixed version for 3.16.x)  
4.0.x  
4.1.x before 4.1.3 (the fixed version for 4.1.x)  
4.2.x before 4.2.5 (the fixed version for 4.2.x)  
4.3.x before 4.3.4 (the fixed version for 4.3.x)  
4.4.0 before 4.4.1 (the fixed version for 4.4.x)  
c修复建议  
升级至 Atlassian JIRA 服务桌面服务器 3.9.16 / 3.16.8 / 4.1.3 / 4.2.5 / 4.3.4 / 4.4.1
或更高版本  
d来源  
<https://cloud.tencent.com/developer/article/1529135>

 **Jira未授权SSRF漏洞复现（CVE-2019-8451）**  
a漏洞分析  
Jira的/plugins/servlet/gadgets/makeRequest资源存在SSRF漏洞，原因在于JiraWhitelist这个类的逻辑缺陷，成功利用此漏洞的远程攻击者可以以Jira服务端的身份访问内网资源。经分析，此漏洞无需任何凭据即可触发。  
b影响版本  
< 8.4.  
c修复建议  
升级到8.4.0及以上版本  
d来源  
奇安信CERT

 **Atlassian JIRA服务器模板注入漏洞复现（CVE-2019-11581）**  
a漏洞分析  
Atlassian Jira是澳大利亚Atlassian公司的一套缺陷跟踪管理系统。该系统主要用于对工作中各类问题、缺陷进行跟踪管理。

Atlassian Jira Server和Jira Data Center存在服务端模板注入漏洞，成功利用此漏洞的攻击者可对运行受影响版本的Jira
Server或Jira Data Center的服务器执行任意命令，从而获取服务器权限，严重危害网络资产。  
b影响版本  
AtlassianJira 4.4.x  
AtlassianJira 5.x.x  
AtlassianJira 6.x.x  
AtlassianJira 7.0.x  
AtlassianJira 7.1.x  
AtlassianJira 7.2.x  
AtlassianJira 7.3.x  
AtlassianJira 7.4.x  
AtlassianJira 7.5.x  
AtlassianJira 7.6.x < 7.6.14  
AtlassianJira 7.7.x  
AtlassianJira 7.8.x  
AtlassianJira 7.9.x  
AtlassianJira 7.10.x  
AtlassianJira 7.11.x  
AtlassianJira 7.12.x  
AtlassianJira 7.13.x < 7.13.5  
AtlassianJira 8.0.x < 8.0.3  
AtlassianJira 8.1.x < 8.1.2  
AtlassianJira 8.2.x < 8.2.3  
c修复建议  
1.升级到不受漏洞影响的版本。  
2.对http://ip:port/secure/admin/SendBulkMail!default.jspa限制访问的源ip  
d来源  
https://www.cnblogs.com/backlion/p/11608439.html

 **JIRA信息泄漏漏洞（CVE-2019-8449）**  
a漏洞分析  
Atlassian Jira
8.4.0之前版本/rest/api/latest/groupuserpicker接口允许未授权查询员工信息，攻击者可以通过爆破用户名名单等方法获取用户信息。  
b影响版本  
7.12< 受影响版本<8.4.0  
c修复建议  
1.JIRA升级至官方最新版本  
2.配置安全组，限制只允许可信源IP访问  
d来源  
https://xz.aliyun.com/t/7219

## 六、开源运维监控

### Jenkins

 **Jenkins路径遍历任意文件写入漏洞（CVE-2019-10352）**  
a漏洞分析  
具有“作业/配置”权限的用户可以在文件参数定义的文件名部分中指定一个相对路径，以相对于基本目录进行转义。此路径将用于在Jenkins控制器上存储上载的文件，从而导致任意文件写入漏洞。  
b影响版本  
Jenkins最高2.185  
Jenkins LTS最高至2.176.1（含）  
c修复建议  
詹金斯每周应该更新到版本2.186  
Jenkins LTS应该更新到版本2.176.2  
d来源  
<https://www.jenkins.io/security/advisory/2019-07-17/#SECURITY-1424>

 **Jenkins Git client插件RCE（CVE-2019-10392）**  
a漏洞分析  
Jenkins是一个开源软件项目，是基于Java开发的一种持续集成工具，用于监控持续重复的工作，旨在提供一个开放易用的软件平台，使软件的持续集成变成可能。Git客户端插件中的系统命令执行漏洞，这是以允许具有Job/Configure权限的攻击者在Jenkins主服务器上执行任意系统命令作为Jenkins进程正在运行的OS用户的方式实现命令执行。  
b影响版本  
Git client Plugin <= 2.8.4  
c修复建议  
升级Git client插件至2.8.4以上版本  
d来源  
安识科技安服团队

### Zabbix

 **Zabbix远程代码执行漏洞（CVE-2020-11800）**  
a漏洞分析  
Zabbix SIA Zabbix是拉脱维亚Zabbix SIA公司的一套开源的监控系统。该系统支持网络监控、服务器监控、云监控和应用监控等。Zabbix
Server的trapper命令处理，存在命令注入漏洞，可导致远程代码执行。  
b影响版本  
Zabbix 3.0.x~3.0.30  
c修复建议  
更新至版本3.0.31  
d来源  
<https://xz.aliyun.com/t/8991>

### Nagios

 **Nagios XI 5.6.9远程代码执行漏洞（CVE-2019-20197）**  
a漏洞分析  
Nagios是一款开源的电脑系统和网络监视工具，能有效监控Windows、Linux和Unix的主机状态，交换机路由器等网络设置，打印机等。在系统或服务状态异常时发出邮件或短信报警第一时间通知网站运维人员，在状态恢复后发出正常的邮件或短信通知。在Nagios
XI
5.6.9中，经过身份验证的用户可以在Web服务器用户帐户的上下文中，通过shell参数将外壳元字符执行到schedulereport.php的id参数中执行任意OS命令。  
b影响版本  
<= v5.6.9  
c修复建议  
1.建议服务器管理员配置复杂密码登录，避免被爆破攻击后再利用Nagios XI远程命令执行漏洞。  
2.配置受信任的源才能访问该服务。  
d来源  
<https://nvd.nist.gov/vuln/detail/CVE-2019-20197>

 **Nagios代码注入扩展（CVE-2021-3273）**  
a漏洞分析  
低于5.7的Nagios XI受/nagiosxi/admin/graphtemplates.php组件中的代码注入的影响。在nagios xi
5.7中，管理员可以编辑/删除/添加模板，模板将存储在其中。可以通过访问并作为PHP文件执行/并导致以Apache的方式执行PHP代码和执行OS命令。  
b影响版本  
低于5.7  
c修复建议  
官方下载补丁  
地址：  
https://www.nagios.com/downloads/nagios-xi/change-log/  
d来源  
<https://nvd.nist.gov/vuln/detail/CVE-2021-3273>

## 七、堡垒机

### JumpServer

 **JumpServer远程执行漏洞**  
a 漏洞分析  
JumpServer 是全球首款完全开源的堡垒机, 使用GNU GPL v2.0 开源协议, 是符合4A 的专业运维审计系统。JumpServer
使用Python / Django 进行开发。

2021年1月15日，JumpServer发布更新，修复了一处远程命令执行漏洞。由于 JumpServer
某些接口未做授权限制，攻击者可构造恶意请求获取到日志文件获取敏感信息，或者执行相关API操作控制其中所有机器，执行任意命令。  
b 影响版本  
JumpServer < v2.6.2  
JumpServer < v2.5.4  
JumpServer < v2.4.5  
JumpServer = v1.5.9  
c修复建议  
1.升级 JumpServer 至最新版本。  
2.设置当前产品的控制台登录IP地址白名单限制。  
d来源  
<https://nosec.org/home/detail/4653.html>

 **齐治堡垒机**  
齐治堡垒机前台远程代码执行漏洞  
a漏洞分析  
浙江齐治科技股份有限公司是一家主要经营计算机软硬件、网络产品的技术开发等项目的公司。齐治运维堡垒机服务端存在命令执行漏洞，攻击者可利用该漏洞获取服务器权限。  
b修复建议  
该漏洞的修复补丁已发布，如果客户尚未修复该补丁，可联系齐治科技的技术支持人员获得具体帮助。  
c来源  
https://www.cnvd.org.cn/flaw/show/1632201

