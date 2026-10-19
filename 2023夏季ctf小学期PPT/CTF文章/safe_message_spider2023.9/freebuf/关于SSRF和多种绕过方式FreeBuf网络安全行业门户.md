## **SSRF是什么？**

 **SSRF** （Server-Side Request
Forgery，服务器端请求伪造），漏洞形成的原因主要是服务器端所提供的接口中包含了所要请求内容的URL参数，并且未对客户端所传输过来的URL参数进行过滤，导致攻击者可以传入任意的地址来让后端服务器对其发起请求，并返回对该目标地址请求的数据。因此存在SSRF漏洞的服务器通常被作为跳板机来取得外网或内网其它应用服务器的信息。

![image.png](https://image.3001.net/images/20220209/1644395624_62037c68ec89b76508e4c.png!small)

图1 SSRF的利用流程

##  **SSRF的危害**

 **主要攻击类型：**

  * 钓鱼。

  * 对外网、服务器所在内网、本地进行端口、资产发现。

  * 读取本地文件。

  * 配合其它漏洞攻击内网其它机器。

举个例子

 **【场景一】**

如下图以骗取用户在线转账作为一个比较经典的利用SSRF攻击流程，可以主要分为以下四个步骤：

> (1）攻击者伪造了一个资金转帐网站的请求。
>
> (2）将其嵌入到用户经常访问，存在SSRF漏洞的站点中。
>
> (3）当访问者登录该网站并单击犯罪者创建的钓鱼链接时，它最终将重定向到犯罪者的网站。
>
> (4）受害者在并将金额转移到攻击者指定的帐户中。

由于利用SSRF后的钓鱼链接伪造程度较高，以URL前部分与正常域名一致，所以对安全知识了解不多的用户是极其容易受此类漏洞制作的钓鱼网站的攻击。

![image.png](https://image.3001.net/images/20220209/1644395625_62037c69a1567cb3e830c.png!small)

图2 利用SSRF的攻击

 **【场景二】**

这里我们以‘PIKACHU’渗透测试环境来举例，演示一下攻击者是如何利用SSRF漏洞来获取到服务器内网其它主机资源的。

假设网站维护人员使用PHP函数不当（使用了危险函数：file_get_contents()、fsockopen()、curl_exec()），导致在站点目录pikachu/pikachu/vul/ssrf/ssrf_curl.php存在SSRF漏洞利用。

![image.png](https://image.3001.net/images/20220209/1644395633_62037c71cbdba3438378a.png!small)

图3 “PIKACHU”SSRF实验

发现参数以URL的格式调用了本地的其它资源，可以尝试调用同一网段下其它服务器的资源。

如图，利用SSRF成功查询了同网段172主机下7070端口的资源，导致了内部的数据暴露。

![image.png](https://image.3001.net/images/20220209/1644395634_62037c729492c370665a4.png!small)

图4 访问内部数据

在通常情况下，对SSRF的防御措施是对URL特征参数进行检测和过滤、设置可访问URL白名单或使用户无法控制URL的参数，一但过滤的措施不够严密，就会存在多种Bypass方式。

##  **绕过姿势大全**

####  **1.“@”符号绕过**

[http://www.baidu.com@10.10.10.10与http://10.10.10.10请求是相同的。](http://10.10.10.xn
--10http-4p7i//10.10.10.10%E8%AF%B7%E6%B1%82%E6%98%AF%E7%9B%B8%E5%90%8C%E7%9A%84%E3%80%82)

该请求得到的内容都是10.10.10.10的内容，此绕过同样在URL跳转绕过中适用。

利用的原理： **解析URL时的规则问题。**

一般情况下利用URL解析导致SSRF过滤被绕过基本上都是因为后端通过不正确的正则表达式对URL进行了解析。这个原理在2017年的Blackhat大会上被提出过，是Orange
Thai（蔡政达,现任台湾信息安全公司戴夫寇尔(Devcore)高级研究员)在Blackhat（国际黑帽大会）中发表的演讲，《A New Era of
SSRF - Exploiting URL Parser in Trending Programming Languages!
》该文中介绍了SSRF攻击的一个新的角度——利用不同编程语言对URL的处理标准来绕过SSRF过滤，来实施攻击。

![image.png](https://image.3001.net/images/20220209/1644395635_62037c73818f0a829e41e.png!small)

图5 A New Era of SSRF - Exploiting URL Parser in Trending Programming Languages

下图展示了CURL请求函数与其他语言解析函数结合使用时，由于差异性造成的漏洞。

![image.png](https://image.3001.net/images/20220209/1644395638_62037c76a17fd5be1881b.png!small)

图6 CURL请求函数与其他解析函数的差异性

从他的文章得知，NodeJS url、Perl URI、Go net/url、PHP parser_url以及Ruby
addressable解析函数与cURL libcurl请求函数差异性都可能造成漏洞的产生。

如果上面的解释并不能很好理解的话，可以看下图的实例，我们看到上述所述编程语言的解析函数得到的IP是google.com，而CURL请求得到的却是evil.com:80

![image.png](https://image.3001.net/images/20220209/1644395639_62037c77e7c4b33ca82fa.png!small)

 **2.点分割符号替换（钓鱼邮件常用于绕过检测）**

在浏览器中可以使用不同的分割符号来代替域名中的.分割，可以使用。、｡、．来代替：

[http://www。qq。com](http://www.qq.com)

[http://www｡qq｡com](http://www.qq.com)

[http://www．qq．com](http://www.qq.com)

 **3.本地回环地址的其他表现形式**

 **127.0.0.1** ，通常被称为本地回环地址(Loopback
Address)，指本机的虚拟接口，一些表示方法如下(ipv6的地址使用http访问需要加[])：

http://127.0.0.1  
http://localhost  
http://127.255.255.254  
127.0.0.1 - 127.255.255.254  
http://[::1]  
http://[::ffff:7f00:1]  
http://[::ffff:127.0.0.1]  
http://127.1  
http://127.0.1  
http://0:80

####  **4.IP的进制转换（钓鱼邮件常用于绕过检测）**

IP地址是一个32位的二进制数，通常被分割为4个8位二进制数。通常用“点分十进制”表示成（a.b.c.d）的形式，所以IP地址的每一段可以用其他进制来转换。使用如win系统自带的计算机（程序员模式）就可简单实现IP地址的进制转换。

由于一些系统会直接提取邮件中内嵌的链接进行检测，而一种此类URL混淆技术采用了URL主机名部分中使用的编码十六进制IP地址格式来逃避检测。

由于IP地址可以用多种格式表示，因此可以在URL中如下所示使用：

  * 点分十进制IP地址：http://216.58.199.78

  * 八进制IP地址：http://0330.0072.0307.0116（将每个十进制数字转换为八进制）

  * 十六进制IP地址：http://0xD83AC74E或者http://0xD8.0x3A.0xC7.0x4E（将每个十进制数字转换为十六进制）

  * 整数或DWORD IP地址：http://3627730766（将十六进制IP转换为整数）

 **5.利用短网址**

网上有很多将网址转换为短网址（短链接）的工具网站，黑客会利用短网址来绕过情报检测。

##  **SSRF的加固**

  * 禁止302跳转，或者每跳转一次都进行校验目的地址是否为内网地址或合法地址。

  * 过滤返回信息，验证远程服务器对请求的返回结果，是否合法。

  * 禁用高危协议，例如：gopher、dict、ftp、file等，只允许http/https。

  * 设置URL白名单或者限制内网IP。

  * 限制请求的端口为http的常用端口，或者根据业务需要开放远程调用服务的端口。

  * catch错误信息，做统一错误信息，避免黑客通过错误信息判断端口对应的服务。

参考文章：

<https://blog.csdn.net/qq_34974749/article/details/112424693>

<https://blog.csdn.net/blackorbird/article/details/108701342>

