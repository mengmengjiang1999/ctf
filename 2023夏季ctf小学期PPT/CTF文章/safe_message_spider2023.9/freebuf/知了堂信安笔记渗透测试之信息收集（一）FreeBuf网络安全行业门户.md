文章来源：知了堂冯老师

![v2-c4c958a3e1dfbc0814708d05a49ef731_hd.j](https://pic2.zhimg.com/80/v2-c4c958a3e1dfbc0814708d05a49ef731_hd.jpg)

0 信息收集

进行渗透测试之前，最重要的一步就是信息收集。在这个阶段，我们要尽可能地收集目标的信息。所谓“知己知彼，百战不殆”，我们越了解测试目标，测试的工作就越容易。

信息收集的方式可以分为两种：主动和被动。

·主动信息收集：通过直接访问、扫描网站，这种流量将流经网站。

·被动信息收集：利用第三方的服务对目标进行访问了解，比例：Google搜索、Shodan搜索等。

没有一种方式是最完美的，每个方式都有自己的优势，主动方式，你能获取更多的信息，但是目标主机可能会记录你的操作记录。被动方式，你收集的信息会相对较少，但是你的行动并不会被目标主机发现。一般在一个渗透项目下，你需要有多次的信息收集，同时也要运用不同的收集方式，才能保证信息收集的完整性。
而信息收集到底要收集哪些信息呢？接下来，我就给大家整理了一下，渗透测试中常见的一些需要收集的信息。

1 Whois查询

Whois是一个标准的互联网协议，可以用收集网络注册信息，注册的域名，IP地址等信息。简单的说，Whois就是一个用于查询域名是否已被注册以及域名的详细信息的数据库(如域名所有人、域名注册商)。在Whois查询中，得到注册人的姓名和邮箱通常对测试个人站点非常有用，因为我们可以通过搜素引擎和社交网络挖掘出域名所有人的很多信息。对中小站点而言，域名所有人往往就是管理员。

·查询方法

1\.
站长之家：[http://tool.chinaz.com](https://link.zhihu.com/?target=http%3A//tool.chinaz.com)

2\. Virus Total:
[https://www.virustotal.com](https://link.zhihu.com/?target=https%3A//www.virustotal.com)
,是一个提供免费的可疑文件分析服务的网站

3\. kali下使用whois进行查找

2 备案信息查询

网站备案是根据国家法律法规规定，需要网站的所有者向国家有关部门申请的备案，这是国家信息产业部对网站的一种管理，为了防止在网上从事非法的网站经营活动的发生。主要针对国内网站，如果网站搭建在其他国家，则不需要进行备案。

·在线查询站点：

1.[Icp备案查询网][[http://www.beianbeian.com](https://link.zhihu.com/?target=http%3A//www.beianbeian.com)]

2.[天眼查][[http://www.tianyancha.com](https://link.zhihu.com/?target=http%3A//www.tianyancha.com)]

3 收集敏感信息

·Google hacking

Google是世界上最强大的搜素引擎之一，对一位渗透测试者来说，它可能是一款绝佳的黑客工具。我们可以通过构造特殊的关键字语法来搜索互联网上的相关敏感信息。

Google Hack常用语法：

site：可限制你搜索范围的域名

inurl：用于搜索网页上包含的URL，这个语法对寻找网页上的搜索，帮助之类的很有用

intext: 只搜索网页部分中包含的文字(也就是忽略了标题、URL等的文字)

filetype：搜索文件的后缀或者扩展名

intitle：限制你搜索的网页标题

link: 可以得到一个所有包含了某个指定URL的页面列表

info：查找指定站点的一些基本信息

cache：搜索Google里关于某些内容的缓存

查找后台地址：site:域名
inurl:login|admin|manage|member|admin_login|login_admin|system|login|user|main|cms

查找文本内容：site:域名
intext:管理|后台|登陆|用户名|密码|验证码|系统|帐号|admin|login|sys|managetem|password|username

查找可注入点：site:域名 inurl:aspx|jsp|php|asp

查找上传漏洞：site:域名 inurl:file|load|editor|Files找eweb

编辑器：site:域名 inurl:ewebeditor|editor|uploadfile|eweb|edit

存在的数据库：site:域名 filetype:mdb|asp|#

查看脚本类型：site:域名 filetype:asp/aspx/php/jsp

迂回策略入侵：inurl:cms/data/templates/images/index/

列：尝试搜索一些学校网站的后台，语法为:”site:[http://edu.cn](https://link.zhihu.com/?target=http%3A//edu.cn)
intext: 后台管理”

意思为搜索网页正文中包含有“后台管理”
并且域名后缀是[http://edu.cn](https://link.zhihu.com/?target=http%3A//edu.cn)的网站，

利用Goole搜索，我们可以很轻松地得到想要的信息，还可以用它来收集数据库文件、SQL注入、配置信息、源代码泄露、未授权访问和robots.txt等敏感信息。

注：Google搜索的思路同样可以用在百度、雅虎、Bing、Shodan等搜索引擎上，语法大同小异。

·Shodan的使用

相关文章：[https://www.freebuf.com/sectool/121339.html](https://link.zhihu.com/?target=https%3A//www.freebuf.com/sectool/121339.html)

·Burp suite

通过Burp Suite的Repeater功能同样可以获取一些服务器的信息，如运行的Server类型及版本，PHP的版本信息等，针对不同的server
利用不同的漏洞进行测试。

·GitHub

尝试在Github上寻找相关的敏感信息，如数据库连接信息，邮箱密码，uc-key ，阿里的osskey，有时还能找到泄露的源代码等。

·SRC漏洞平台

补天：[https://www.butian.net/](https://link.zhihu.com/?target=https%3A//www.butian.net/)

乌云：[http://www.anquan.us/](https://link.zhihu.com/?target=http%3A//www.anquan.us/)

国家信息安全漏洞共享平台：[https://www.cnvd.org.cn](https://link.zhihu.com/?target=https%3A//www.cnvd.org.cn/)

漏洞盒子：[https://www.vulbox.com/](https://link.zhihu.com/?target=https%3A//www.vulbox.com/)

知道创宇：[https://www.seebug.org/](https://link.zhihu.com/?target=https%3A//www.seebug.org/)

![v2-c1a2aaa1f89d1a594aa4d2abc6298db7_hd.j](https://pic4.zhimg.com/80/v2-c1a2aaa1f89d1a594aa4d2abc6298db7_hd.jpg)

鉴于内容太多，将分次更新，今天就先更到这儿了，本文来自知了堂冯老师，原创整理，转载请注明出处，喜欢请分享给更多人。

![v2-7327d17669bd87ceda005f931d078d95_hd.j](https://pic2.zhimg.com/80/v2-7327d17669bd87ceda005f931d078d95_hd.jpg)

###  

