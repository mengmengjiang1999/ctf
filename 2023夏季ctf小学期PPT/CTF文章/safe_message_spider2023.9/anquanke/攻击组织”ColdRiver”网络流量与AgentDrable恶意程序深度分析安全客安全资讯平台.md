# 攻击组织”Cold River”：网络流量与Agent_Drable恶意程序深度分析

阅读量 **294400**

|评论 **4**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-01-21 15:30:56

 **x**

##### 译文声明

本文是翻译文章，文章原作者 lastline，文章来源：lastline.com

原文地址：<https://www.lastline.com/labsblog/threat-actor-cold-river-network-traffic-analysis-and-a-deep-dive-on-agent-drable/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t01279e47b5032d25db.jpg)

我们近期在回顾一些网络异常时，发现了使用DNS隧道与C2进行通讯的攻击组织并将其命名为”Cold
River”，我们已经能解密受害者与C2的通信流量，并发现了攻击者使用的复杂诱饵文档，从而关联到了其他未知样本，并发现了攻击者使用的大量基础设施

该活动主要针对中东组织，其中大多数来自黎巴嫩和阿拉伯联合酋长国，除此之外，与这些中东国家关系密切的印度与加拿大公司也成为了目标。这次攻击中使用了新的TTP
– 例如Agent_Drable恶意程序利用Django 框架来搭建C2服务器，其技术细节将在后面的博客中披露。

我们不确定这次攻击行动背后是否有其他攻击组织提供支持，这次攻击使用了之前从未发现的新工具，我们推测这次攻击中使用的种植程序中发现的硬编码字符串”Agent_Drable”使用的是一种从右到左的语言，它引用了2007年黎巴嫩军队在“Nahr
Elbard”巴勒斯坦难民营发生的冲突，”Nahr Elbard”是”Nahr el bared”的音译，”Nahr Elbard”的英文翻译是”Cold
River”。

简而言之，”Cold River”是一种复杂的威胁，他使用了DNS子域劫持，证书欺骗，隐蔽的C2通信方式，复杂又极具迷惑性的诱饵文档以及定制化的恶意程序。

## 恶意doc文档dropper

我们发现了两个只是诱饵内容不同的恶意文档，他们拥有相同的VBA宏，相同的payload，第一个是带有恶意payload的空白文档

![](https://p1.ssl.qhimg.com/t01ce7463c14e4c82d2.png)

图1 ： 空文档截图 SHA1: 1f007ab17b62cca88a5681f02089ab33adc10eec

第二个是来自SUNCOR公司的合法人力资源文档，他们在其中添加了恶意payload和VBA宏（图2）。

![](https://p3.ssl.qhimg.com/t01320895ba2dd6f72d.png)

图2：来自Suncor的文档的截图 SHA1：9ea865e000e3e15cec15efc466801bb181ba40a1

在收集关于回连域名0ffice36o[.]com
的开源威胁情报时，我们在推特发现了可能的关联文档，尽管这个文档并不包含相同的payload，但是推特账号的用户可能附加了错误的文档。

![](https://p2.ssl.qhimg.com/t01ca84f9dcc578f764.png)

图3：引用第三个文档的推文：
**[https](https://twitter.com/KorbenD_Intel/status/1053037793012781061)** ：
**[//twitter.com/KorbenD_Intel/status/1053037793012781061](https://twitter.com/KorbenD_Intel/status/1053037793012781061)**

表一列出的时间戳倾向于证实Suncor文档是带有payload的合法文档的假设:文档创建时间足够久远，最后的保存时间与攻击事件相符，空文档很可能被用于测试宏或者在Suncor之外的环境投递payload。

SHA1 | 描述 | 创作时间 | 最后保存的时间  
---|---|---|---  
1f007ab17b62cca88a5681f02089ab33adc10eec | 空文件 | 2018-10-05 07:10:00 |
2018-10-15 02:59:00  
9ea865e000e3e15cec15efc466801bb181ba40a1 | Suncor 诱饵 | 2012-06-07 18:25:00 |
2018-10-15 22:22:00  
  
## 行为分析

VBA宏保持简洁但是有效，宏被分为两部分，一个在文档打开时执行，另一个在文档关闭时执行。实际payload不直接存储在VBA代码中，而是隐藏在文档中的表单中。

打开Suncor文档时，用户必须启用宏执行才能查看其真实内容。这使得允许宏执行对于普通用户是合理的。唯一的混淆是使用了字符串拼接，例如“ t”＆“
mp”，“ Microsoft.XML” & “ DOM”，“ userp” & “ rofile”等。

恶意宏包含一些基本的反沙箱代码，使用Application.MouseAvailable检查计算机上是否有鼠标可用。宏的整体流程如下:

当文档打开时:

  1. 检查Environ(“userprofile”)\\.oracleServices\svshost_serv.exe是否存在。

如果存在则退出，不存在则继续执行

  2. 如果Environ(“userprofile”)\\.oracleServices目录不存在，则创建该目录。
  3. 读取UserForm1.Label1.Caption中存储的base64编码payload
  4. 解码并写入Environ(“userprofile”)\\.oracleServices\svshost_serv.doc。
  5. 显示文档内容。

在文件关闭时：

  1. 将释放的”svshost_serv.doc”文件重命名为”svshost_serv.exe”
  2. 创建一个名为”chrome updater”的每分钟执行EXE文件的计划任务

最后一个有趣的事情是，设置计划任务的一部分代码为从网上复制而来

## Payload与C&C通信

我们发现了两个相关的Payload，如表2所示，两个payload的主要区别是其中一个有事件记录功能，这让我们更容易的确定恶意程序的功能，也可能是早期开发的调试版本，Suncor文档中的payload并没有记录功能。

SHA1 | 描述 | 编译时间戳  
---|---|---  
1c1fbda6ffc4d19be63a630bd2483f3d2f7aa1f5 | 带有日志信息的payload | 2018-09-03
16:57:26 UTC  
1022620da25db2497dc237adedb53755e6b859e3 | 没有日志信息的payload | 2018-09-15
02:31:15 UTC  
  
表2: Agent_Deable payload

二进制文件中发现了一个有趣的字符串”AgentDrable.exe”，这个字符串就是PE头中的导出表中的Dll
Name字段的值，这个字符串在攻击行动的其他部分也有出现，比如基础架构配置，我们几乎可以确认这是攻击者为恶意程序起的代号，除了近期出现在少数在线分析平台的提交之外，很少有证据指向”Agent
Drable”，一个假设是他被称为”Elbard”。

两个样本的编译时间戳也很有趣。我们必须充分意识到时间戳很容易被伪造，但是，这些时间戳可以在二进制文件的多个位置找到（调试目录，文件头），并且与攻击事件中的其他部分相符合。我们将所有dropper和payloadde
的有效时间戳放在图4中。

![](https://p4.ssl.qhimg.com/t01002d04e54a6c761b.png)

图4：请注意，WORD_1的创建时间戳被省略，正在进一步溯源（2012）。

一个有趣的事实是没有日志记录功能的样本的编译时间戳与被嵌入文件的两个word文档的最后保存时间相匹配，这意味着他们可能在编译了最终版本的恶意程序之后直接嵌入了文档以便投递。

两个恶意文档都是在几天后从黎巴嫩被上传到VirusTotal，总之这个时间表显示了一个连贯的故事，这表示攻击者没有修改任何时间戳，这完成了对整个攻击事件的全局视野，当我们在对比攻击者使用的C2结构时将会提供其他的信息。

## 被释放的可执行的文件 – 行为分析

被释放的可执行文件主要被用作侦察工具，在二进制文件中没有发现高级功能(比如没有屏幕监控或者键盘记录)，该文件的主要功能如下:

  1. 运行C&C下发的命令并返回执行结果
  2. 下载并执行指定文件
  3. 文件窃取

在文件中发现了硬编码的一个IP和一个域名以及一个User-Agent

0ffice36o[.]com (明显在模仿合法的 office360[.]com)

185.161.211[.]72

Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko

被植入的程序有两种与C&C通信的方式

  1. DNS请求
  2. HTTP(s) GET/POST

第一次执行默认为DNS通信，之后根据收到的命令，它可能会切换到HTTP

因为恶意文档创建了计划任务，这个程序每分钟都会执行一次，每次开始运行时都会检查如下子目录是否存在，如果不存在则会创建

.\Apps

.\Uploads

.\Downloads

“Uploads”和”Downloads”目录的功能和他们的名字一样，任何位于”Apps”目录中的可执行文件在被投递的程序执行时也会执行。

所有的配置信息都使用JSON和cJSON库处理，键值名是通用的，使用一个或两个字母(‘a’，’m’，’ul’)，但是我们设法得到了如表3所示的完整的列表，配置信息存储在”Configure.txt”中，在每次开始执行时都会被检索。

参数名称 | 解释  
---|---  
a | 运行模式 (DNS/HTTP)  
m | 最大查询长度，用于将过长的DNS请求分割为多个较短的请求  
f | 阶段  
c | DNS计数器  
h | 根目录，子目录与配置文件被创建的位置  
u | HTTP C&C 资源路径  
s | HTTP C&C IP地址  
d | DNS C&C 域名  
p | HTTP C&C 端口号  
l | 连接种类，HTTP 或者 HTTPS  
i | 受害者ID (两个字符)  
k | 自定义的base64字符表  
  
表3 : JSON配置参数

为了与DNS C&C通信，样本会对特定子域名进行DNS查询，例如以下就是来自不同受害者的一些DNS查询:

crzugfdhsmrqgq4hy000.0ffice36o[.]com

gyc3gfmhomrqgq4hy.0ffice36o[.]com

svg4gf2ugmrqgq4hy.0ffice36o[.]com

Hnahgfmg4mrqgq4hy.0ffice36o[.]com

6ghzGF2UGMD4JI2VOR2TGVKEUTKF.0ffice36o[.]com

子域名遵循特定的模式:它们由4个随机alphadecimal字符与base32编码的payload组成，当应用于上面列出的子域名时，我们得到:

子域名 | 明文  
---|---  
crzugfdhsmrqgq4hy000 | 1Fy2048|  
gyc3gfmhomrqgq4hy | 1Xw2048|  
svg4gf2ugmrqgq4hy | 1uC2048|  
6ghzGF2UGMD4JI2VOR2TGVKEUTKF | 1uC0|J5WGS5TJME  
  
前三个明文只通过两个不同的字母区分: Fy /Xw
/uC，这是样本生成的受害者ID，这使得C&C可以分辨请求来源，它是通过用户名与主机名生成，因此会在样本执行期间保持不变，同样的ID也会应用于HTTP通讯。

在DNS模式下，样本仅通过这些特定子域名与C&C通信并通过解析返回的IP地址来获取指令，HTTP通信模式更加高级，请求与应答分别使用GET与POST，默认情况下，样本拼接的URL格式为[http://[CNC_IP]/[RESOURCE_PATH]?id=[ID](http://%5BCNC_IP%5D/%5bRESOURCE_PATH%5d?id=%5bID)]，参数解释如下:

参数 | 默认值 | 注意事项  
---|---|---  
CNC_IP | 185.161.211[.]72 | 此IP可以更新  
RESOURCE_PATH | /index.html | 此路径可以更新  
ID | Fy | 这个ID与受害者绑定  
  
存储在二进制文件中的硬编码C&C IP在分析时处于离线状态，我们找到了另一个活跃C&C 185.20.184.138 图5为浏览器访问C&C的截图

图5: 假冒的Wikipedia页面

C&C命令隐藏在HTML注释或特定标记内并且使用自定义base64字母表进行编码，下面就是页面源代码的一段摘录，其中展示了编码后的数据

解码后会得到下面的JSON对象并从中提取指令

这些命令显示了攻击者在继续入侵之前执行主机侦察的典型步骤，完整的包含指令或命令的tag的列表如表4。

标签

|

描述  
  
---|---  
<!–[DATA]–> |

Base64编码后的json内容  
  
<link href=”[DATA]”> |

需要下载的资源路径  
  
<form action=”[DATA]” |

需要POST回复的资源路径  
  
<style>/*[DATA]*/</style> |  
  
<script>/*[DATA]*/</script> |  
  
表4:从页面提取的tags列表

HTTP C&C由打开了调试模式的Django框架驱动，由于配置错误，可以收集一些用于显示整个基础架构的额外信息，表5显示了所有可以访问的页面

路径 | 描述  
---|---  
/index.html (GET) | 获取指令与配置参数  
/Client/Login (GET) | 获取自定义base64字母表  
/Client/Upload (POST) | 上传窃取的数据或者命令执行结果  
/Client/Download/<str:url> |  
/DnsClient/Register |  
/DnsClient/GetCommand |  
/DnsClient/SendResult |  
/DnsClient/SendNotification |  
/static/ |  
^\\.well\\-known\/acme\\-challenge\/(?P<path>.*)$ | 用于生成let的加密证书  
  
表5:可以访问的页面列表

除了所有的资源路径，调试模式还泄露了所有环境变量和一些Django内部设置。最有趣的值列于表6和表7中（完整列表可根据要求提供）：

键值名称 | 值 | 解释  
---|---|---  
PWD | /root/relayHttps | 有趣的目录名  
PATH_INFO | /static/backup.zip | 带有密码的数据库备份  
SERVER_NAME | debian |  
SERVER_SOFTWARE | WSGIServer/0.2 |  
SHELL | /usr/bin/zsh |  
SSH_CLIENT | 194.9.177[.]22 53190 22 | 泄露了他们的VPN服务器的IP  
  
表6：由于Django实例配置错误而泄露的环境变量。

键值名称 |  值 | 解释  
---|---|---  
LOGIN_URL |  /accounts/login/ |  
MAGIC_WORD | microsoft | 未知  
PANEL_PATH | /Th!sIsP@NeL |  
PANEL_PORT | :7070 |  
PANEL_USER_NAME | admin |  
DATABASES | /root/relayHttps/D b.sqlite3 |  
SERVER_PORT | :8083 |  
SERVER_URL | https://185.20.184[.]157 | 泄露的未知用途IP  
  
表7：由于Django实例配置错误而泄露的设置。

我们可以再一次发现对”drable”的使用，这次是用于从底层数据库获取数据的查询语句的一部分。

SELECT COUNT(*) AS “__count” FROM “Client_drable”

WHERE “Client_drable”.”relay_id” = %s  
  
---  
  
## 基础设施

根绝C&C泄露的信息以及额外的被动DNS数据，我们能够高度确定几台属于攻击行动基础设施的主机，一个有趣的事实是他们都属于同一个自治系统，Serverius
N(AS 50673)，并由Deltahost托管，除此之外，所有的域名都通过NameSilo注册

IP | 描述  
---|---  
185.161.211[.]72 | 硬编码HTTP C&C，在分析时未使用。  
185.20.187[.]8 | 主要用于生成Let的加密证书。端口443仍然以memail.mea.com [。]
lb应答。端口444具有memail.mea.com [.] lb的“GlobalSign”证书。  
185.20.184[.]138 | 存活的HTTP C&C。端口80和443返回Django调试信息。  
185.20.184[.]157 | 未知用途。端口7070存在受基本身份验证保护的https页面，证书CN是“ kerteros
”，端口8083为Web服务器 ，但仅返回空白页。  
185.161.211[.]79 | 存放人力资源相关钓鱼域名hr-suncor [.] com和hr-wipro [.] com，现在重定向到合法网站。  
194.9.177[.]22 | Openconnect VPN用于访问HTTP CnC。  
  
通过将这些IP地址与DNS解析相关联（参见附录A中的时间表），我们确定了三个最有可能用于投递第一阶段攻击文档的三个域名；

hr-suncor[.]com

hr-wipro[.]com

files-sender[.]com

这些看起来相似的域名与攻击中使用的Suncor文档模板很匹配。我们还没有找到任何关联到Wipro的文件。我们还发现来自政府的AE和LB域名到185.20.187
[.]8的短时间可疑DNS解析。

通过将此数据与来自<https://crt.sh>的证书生成记录进行关联分析，我们可以得出结论，攻击者设法接管了这些域名的DNS入口并生成多个”Let’s
encrypt”证书，这允许他们透明拦截任何TLS交换。

域名 | **证书** | **重定向日期**  
---|---|---  
`memail.mea.com[.]lb` | <https://crt.sh/?id=923463758> | `2018-11-06`  
`webmail.finance.gov[.]lb` | <https://crt.sh/?id=922787406> | `2018-11-06`  
`mail.apc.gov[.]ae` |
[`https://crt.sh/?id=782678542`](https://crt.sh/?id=782678542) | `2018-09-23`  
`mail.mgov[.]ae` | <https://crt.sh/?id=750443611> | `2018-09-15`  
`adpvpn.adpolice.gov[.]ae` | <https://crt.sh/?id=741047630> | `2018-09-12`  
  
## 结论

总之，Cold
River是一个复杂的攻击组织，恶意使用DNS隧道作为C&C通信方式，极具欺骗性的诱饵文档，以及之前未知的投递木马，攻击行动主要针对来自中东组织，主要来自黎巴嫩和阿拉伯联合酋长国，但是和这些中国国家关系密切的印度和加拿大公司也可能成为目标。

Cold River提醒了我们威胁情报多样化和情景化的重要性，如果不与行为情报和流量分析相结合，对Cold
River的完全揭露将无法实现，从而使受害者面临更多危险

## IOC

### 恶意文档

9ea865e000e3e15cec15efc466801bb181ba40a1 (Suncor 文档)

678ea06ebf058f33fffa1237d40b89b47f0e45e1

### Payloads

1022620da25db2497dc237adedb53755e6b859e3 (文档 Payload)

1c1fbda6ffc4d19be63a630bd2483f3d2f7aa1f5 (带有日志功能)

### IP地址

185.161.211[.]72

185.20.184[.]138

185.20.187[.]8

185.20.184[.]15

185.161.211[.]79

194.9.177[.]22

104.148.109[.]193

### 网站域名

0ffice36o[.]com

hr-suncor[.]com

hr-wipro[.]com

files-sender[.]com

microsoftonedrive[.]org

### 证书域名

memail.mea.com[.]lb

webmail.finance.gov[.]lb

mail.mgov[.]ae

adpvpn.adpolice.gov[.]ae

Mail.apc.gov[.]ae

### 生成的证书

https://crt.sh/?id=923463758

https://crt.sh/?id=922787406

https://crt.sh/?id=782678542

https://crt.sh/?id=750443611

<https://crt.sh/?id=741047630>

### User-Agent

Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko

### 文件路径

%userprofile%\\.oracleServices\Apps\

%userprofile%\\.oracleServices\Configure.txt

%userprofile%\\.oracleServices\Downloads\

%userprofile%\\.oracleServices\log.txt

%userprofile%\\.oracleServices\svshost_serv.doc

%userprofile%\\.oracleServices\svshost_serv.exe

%userprofile%\\.oracleServices\Uploads\

### 计划任务

Name: “chrome updater”

Description: “chromium updater v 37.5.0”

Interval: 1 minute

Execution: “%userprofile%\\.oracleServices\svshost_serv.exe”

### 附录A: DNS解析时间表

![](https://p4.ssl.qhimg.com/t01192b14269196ad91.png)

本文翻译自lastline.com [原文链接](https://www.lastline.com/labsblog/threat-actor-cold-river-network-traffic-analysis-and-a-deep-dive-on-agent-drable/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Flygend** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/169939](/post/id/169939)

安全客 - 有思想的安全新媒体

本文转载自: [lastline.com](https://www.lastline.com/labsblog/threat-actor-cold-river-network-traffic-analysis-and-a-deep-dive-on-agent-drable/)

如若转载,请注明出处： <https://www.lastline.com/labsblog/threat-actor-cold-river-network-traffic-analysis-and-a-deep-dive-on-agent-drable/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)
  * [钓鱼攻击](/tag/钓鱼攻击)
  * [恶意活动](/tag/恶意活动)

 **+1** __1赞

 __收藏

![](https://p5.ssl.qhimg.com/t018141f2cf1ffbc0d0.png) Flygend

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

