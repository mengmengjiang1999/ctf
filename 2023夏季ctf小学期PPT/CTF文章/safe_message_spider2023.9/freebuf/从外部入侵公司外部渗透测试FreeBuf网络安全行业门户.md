## **渗透测试" >从外部入侵公司：外部渗透测试**  

这个文章系列共有两篇，这是其一。你可能会有兴趣看另外一篇：[从内部入侵公司：内部渗透测试](https://bbs.ichunqiu.com/thread-40576-1-1.html?from=beef)。

## 介绍

有时候会有客户问我是如何处理那么多渗透测试的技术。你知道我在屏幕上打开的带有绿色文字的黑色小盒子是什么东西吗？偶尔，当我在和新的或有兴趣成为渗透测试的人交谈时，发现他们知道工具怎么使用，也知道他们经常了解漏洞的具体情况，但他们不一定知道漏洞是怎么结合在一起使用的。

另外，[GracefulSecurity.com](https://bbs.ichunqiu.com/thread-40577-1-1.html?from=beef)有非常多Web应用安全的相关内容，但没有任何关于它们如何结合使用的说明。所以我计划在这里写一个例子，来逐步地说明我是如何将一个web地址转换成实际的业务影响。

没有两个应用是完全一样的，但我作为"攻击者"，意图通常是相似的，所以这不会成为一个拿到系统权限的完整指南，如果你考虑让测试人员评估你的安全性，而他却在你工具包中徘徊，或者如果你刚在你第一本web书籍中领悟出了点东西，想更多地了解整个过程。那么，希望这篇文章能够填补一些你的空白。

## 攻击

提到攻击，入侵和攻击网络的实际行为，都会遵循一种方法。当询问你的渗透测试人员时，他们会告诉你操作方法。但要记住，每个网络环境都不同，每次攻击也都不一样。测试人员操作的标准方式是找到一个阻力最小的路径并使用它来获得尽可能高的权限，然后利用此权限来查找其他攻击入口。

渗透测试不是脆弱性分析。通常，在脆弱性分析的时候你要给评估者提供很多比较重要的信息和权限。他们会在授权的情况下进行网络扫描，来确定所有问题或尽可能多的问题。脆弱性评估通常对问题进行独立评级，不考虑在现实中的可利用性，也不考虑多个问题结合在一起使用所产生的影响。所以，脆弱性评估会给人广泛但不深刻的[网络安全](https://bbs.ichunqiu.com/thread-40577-1-1.html?from=beef)印象，但会突出一些系统问题，如补丁管理。

而渗透测试旨在尽可能地深入，尽管这可能会牺牲广度。但是这会让攻击者很直观地了解到这个漏洞的利用价值。这些评估很可能会涉及到实际利用的能故意损坏系统的漏洞，并且强调了攻击者为了获得最高权限不择手段，可能会带来的最严重的后果。

渗透测试人员通常会有以下步骤：

  * 枚举和映射
  * 漏洞发现
  * 漏洞利用
  * 内网漫游
  * 提权
  * 清除痕迹

渗透测试人员有可能运气很好，很快就直接通过了这些阶段。甚至有可能利用一些捷径来跳过某些阶段来达成目标。有可能也很蛋疼，必须要一次又一次地重复测试，来绕过一些保护机制。

## 枚举和映射

通常，在渗透测试开始前，会获得一些ip地址和网站的URL地址，类似于"*.example.org"。很明显，客户就是要你评估该域的所有子域。问题是通常一个配置良好的系统不应该输出一个所有可用子域列表，所以你应该自己去破解。

如果系统配置不当，你可以从权威域名服务器中读取域列表。你可以使用以下命令来找到这台服务器：

    
    
    > nslookup 
    > set querytype=soa
    > example.org

然后用下面的命令来和服务器交互：

    
    
    dig axfr @dns-server example.org

其中，dns-server是nslookup命令中的权威域名服务器，执行之后将导致DNS区域传送并且输出一个有效的子域列表。（DNS域传送漏洞）

另一个可替代的方式是通过Google Hacking，使用Google "dorks"。使用一些具体的关键字来限制搜索引擎的结果。例如：

    
    
    site:example.org

搜索的链接为：

    
    
    https://www.google.co.uk/?gws_rd=ssl#q=site:example.org&filter=0

这会导致谷歌将搜索范围限制在目标域名，它可能会返回如
ftp.example.org,www.example.org之类的结果。为了节省搜寻信息的时间，我们可以记下发现的子域，然后使用否定搜索（negative
searching） 来排除一些搜索结果：

    
    
    site:example.org -site:ftp.example.org -site:www.example.org

直到你找到所有能搜索到的域名为止！

爆破子域的最后一种方式是使用常见的子域名称列表。这里不需要花里胡哨的操作，只需要创建一个名为subdomains.txt的潜在子域列表，然后运行一个bash命令：

    
    
    cat subdomains.txt | while read line; do nslookup $line".example.org";done | grep "Name:"

如果有命中，会显示出像这样的结果：

    
    
    Name: www.example.org

现在你已经掌握了范围内的应用列表，是时候开始映射应用本身了。几乎所有Web应用评估我都会使用[Burp
Suite](https://bbs.ichunqiu.com/thread-40577-1-1.html?from=beef)，也可以使用另一个可替代的免费版本[OWASP
ZAP](https://bbs.ichunqiu.com/thread-40577-1-1.html?from=beef)。如果你刚开始使用Burp，我写了一篇
Burp Suite专业版的[使用教程](https://bbs.ichunqiu.com/thread-40577-1-1.html?from=beef)

  
Burp有两个选项可以映射应用，"spider"和"discover content"。Spider使用相当简单，选择Target->Site
map。然后右键选择Spider this host。如下图：

![image.png](https://image.3001.net/images/20180521/15268883494630.png!small)  

Spider（爬虫）只需要一个域名然后点击所有链接就可以有效地映射所有链接的内容。显然，这样就不会找到任何没有链接到的内容。如隐藏的管理界面、日志文件和备份内容。这时候"Forced
Browser"（爆破路径）就派上用场了。  

![image.png](https://image.3001.net/images/20180521/15268883739540.png!small)该选项尝试访问可能的文件和目录列表，然后会告诉你结果。你可以使用会话按钮启动浏览器：  

![image.png](https://image.3001.net/images/20180521/15268883885454.png!small)结束之后你会得到关于该应用所有内容的映射（map），这个过程很有可能会花费很长的时间。这意味着，在Burp面板中会有一个列表，这个列表包含该应用提供的所有功能？并不是，这只是测试每个功能是否存在漏洞的一个例子。可以在Burp界面中看到唯一请求列表:  

![image.png](https://image.3001.net/images/20180521/15268883992408.png!small)

跑完整个应用之后，"Contents"会列出所有功能，然后我们就逐个地测试

## 漏洞发现

在这一步，我们将依次测试每个功能，可能会用到Burp suite的Intruder或者Repeater（[这里有Burp
suite的介绍](https://bbs.ichunqiu.com/thread-40577-1-1.html?from=beef)）。有两个主要的评估方式，第一个是模糊测试-打破功能正常逻辑，看看是否有什么有趣的事情发生。"有趣"可能是详细的错误信息、信息泄露、绕过等。或者你可以从漏洞的角度去尝试一些特殊的payloads。比如[HTTP头注入](https://bbs.ichunqiu.com/thread-40577-1-1.html?from=beef)、[SQL注入](https://bbs.ichunqiu.com/thread-40577-1-1.html?from=beef)、[命令注入](https://bbs.ichunqiu.com/thread-40577-1-1.html?from=beef)、[跨站脚本（XSS）](https://bbs.ichunqiu.com/thread-40577-1-1.html?from=beef)、[跨站请求伪造（XSRF）]()、[XML外部实体注入](https://bbs.ichunqiu.com/thread-40577-1-1.html?from=beef)、[不安全的直接对象引用（Insecure
Direct Object
References）](https://bbs.ichunqiu.com/thread-40577-1-1.html?from=beef)等。

从通用模糊测试角度看，将各种payloads放在每个能输入的地方看看它们是什么反应，比如以下payloads：

    
    
    1
    10
    100
    1000000000000000000000000
    -1
    0.1
    lizard
    '
    "
    ;
    )
    ))))))))))))))))))))
    ]
    ]]]]]]]]]]]]]]]]]]]]
    TRUE
    FALSE
    \0
    %00
    |

应用程序会以输出的方式响应，在上下文环境中就可能导致一个漏洞：详细的错误信息输出。或者，可以发送一些特殊构造的payloads来利用漏洞，如[OWASP
Top
10](https://www.owasp.org/index.php/Top_10_2013-Top_10)中收录的问题。[这里](https://www.gracefulsecurity.com/cheat-sheets/)收录了一些不错的payloads，也可以作为[fuzzdb](https://github.com/fuzzdb-project/fuzzdb/)的一部分。

## 渗透攻击，内网漫游和提权

少数的渗透行为，能导致内网漫游或者提权。首先，如果存在允许命令执行的漏洞-如SQL注入或命令注入。在这种情况下，评估人员很可能会瞄准DMZ（隔离区）或内部企业网络中的其他系统。事实上，在能够执行命令的时候，安全评估就不再局限于Web应用程序评估，而是更多地倾向于内部网络评估。

另外还有一些潜在的漏洞，如XML外部实体注入、路径遍历、任意文件下载等漏洞可能会导致证书被盗用。然后通过证书重用对其他系统进行扫描。-----好像有问题。

最后，如果攻击者能够使存储型XSS发生，那这个payload很有可能可以在完全不同的应用程序上执行。举个例子，如果一个用户在www.example.org注册页面中注册一个账户，在地址等参数中填入XSS脚本，该内容可能会存储在admin.example.org中，可能通过窃取session
tokens或者站内请求伪造，来攻击该应用。

## 清理/清除痕迹

如果是恶意攻击，那还有很多事要做。你会想要删除日志记录和所有活动的痕迹。而作为一个渗透测试人员也一样，在渗透使用到的路径中可能会残留一些文件和用户账户，这些也都要清理干净。例如由于不安全的文件处理而可能上传web
shell，在渗透测试结束之后要将此文件删除，尽可能地和测试开始之前一样。

然后就开始写评估报告了。

作者：Holly-Grace  
翻译：i春秋翻译小组-北风乱  
责任编辑：jishuzhain  
翻译来源：[https://www.gracefulsecurity.com/hacking-from-inside/](https://bbs.ichunqiu.com/thread-40577-1-1.html?from=beef)

有问题大家可以留言哦，也欢迎大家到春秋论坛中来耍一耍
[>>>点击跳转](https://bbs.ichunqiu.com/portal.php?from=beef)  

