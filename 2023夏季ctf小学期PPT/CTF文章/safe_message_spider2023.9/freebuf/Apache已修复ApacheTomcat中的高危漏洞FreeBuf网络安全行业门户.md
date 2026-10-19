***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **近日，Apache软件基金会为Tomcat应用程序服务器推送了最新的安全更新，并修复了多个安全漏洞，其中包括一个DoS漏洞和一个信息泄露漏洞。**

![Apache 已修复 Apache Tomcat
中的高危漏洞](https://image.3001.net/images/20180726/15325752326375.jpg!small)

ApacheTomcat是一款开源的Java Servlet容器，其中实现了多种Java EE规范，包括Java Servlet、JavaServer
Pages(JSP)、Java EL和WebSocket，并且提供了一个“纯Java”实现的HTTP Web服务器环境，可供Java代码运行。

据统计，Apache Tomcat目前占有的市场份额大约为60%。

Apache软件基金会修复的第一个漏洞为[CVE-2018-8037](https://mail-archives.us.apache.org/mod_mbox/www-announce/201807.mbox/raw/%3C20180722090623.GA92700@minotaur.apache.org%3E/)，这是一个非常严重的安全漏洞，存在于服务器的连接会话关闭功能之中。一旦成功利用，该漏洞将允许攻击者在新的会话连接中再次使用之前用户的会话凭证。Tomcat
v9.0.0.M9到v9.0.9以及v8.5.5到v.5.31都将受到该漏洞的影响，不过最新发布的Tomcat
v9.0.10和v8.5.32已经成功修复了该漏洞。

Apache软件基金会修复的第二个漏洞为[CVE-2018-1336](https://mail-archives.us.apache.org/mod_mbox/www-announce/201807.mbox/%3C20180722090435.GA60759%40minotaur.apache.org%3E)，这个漏洞是存在于UTF-8解码器中的溢出漏洞，如果攻击者向解码器传入特殊参数的话，将有可能导致解码器陷入死循环，并出现拒绝服务的情况。受该漏洞影响的Tomcat版本有v7.0.x、v8.0.x、v8.5.x和v9.0.x，而v9.0.7、v8.5.32、v8.0.52和v7.0.90版本已经成功修复了该漏洞。

![Apache 已修复 Apache Tomcat
中的高危漏洞](https://image.3001.net/images/20180726/15325752372222.png!small)

除了之前两个漏洞之外，Apache软件基金会还修复了一个低危的安全限制绕过漏洞，漏洞编号为[CVE-2018-8034](https://mail-archives.us.apache.org/mod_mbox/www-announce/201807.mbox/%3C20180722091057.GA70283@minotaur.apache.org%3E)。根据安全公告中的内容，该漏洞之所以存在，是因为服务器在使用TLS和WebSocket客户端时缺少对主机名的有效性验证。该漏洞目前已经在最新的Tomcat
v7.0.x、v8.0.x、v8.5.x和v9.0.x版本中成功修复。

US-CERT目前也已经给用户推送了漏洞安全警告，并敦促相关用户尽快修复该漏洞。

不过安全研究人员表示，目前还没有发现有攻击者利用这些漏洞来实施攻击。但是需要注意的是，这两个漏洞最终都将导致攻击者在目标服务器上实现任意代码执行。

 ***
参考来源：[securityaffairs](https://securityaffairs.co/wordpress/74727/hacking/apache-tomcat-flaws.html)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

