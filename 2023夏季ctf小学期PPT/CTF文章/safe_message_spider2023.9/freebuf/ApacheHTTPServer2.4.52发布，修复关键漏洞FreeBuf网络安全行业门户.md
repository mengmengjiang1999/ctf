![](https://image.3001.net/images/20211228/1640675991_61caba9773e87dd1fe7d4.jpg!small)2021年12月20日，Apache
软件基金会和 Apache HTTP 服务器项目宣布发布 Apache HTTP Server 2.4.52版本，以解决几个可能导致远程代码执行的安全漏洞。

这些漏洞被追踪为 CVE-2021-44790 和 CVE-2021-44224，可以导致远程代码执行攻击。其 CVSS 分数分别为 9.8 和
8.2，排名均低于Log4Shell（CVSS 分数为10分）。

其中，CVE-2021-44790是Apache HTTP Server
2.4.51及以前的mod_lua在解析多部分内容时可能出现的缓冲区溢出。Apache httpd团队没有发现在野外有利用这个漏洞的攻击。

"精心设计的请求正文可能会导致 mod_lua 多部分解析器（从 Lua 脚本调用的 r:parsebody()）中的缓冲区溢出。" Apache
发布的公告写道。

第二个关键漏洞被追踪为CVE-2021-44224，是 Apache HTTP Server 2.4.51 及更早版本中，转发代理配置中可能的 NULL
取消引用或 SSRF。

“发送到配置为转发代理（ProxyRequests on）的 httpd 的精心制作的 URI
可能导致崩溃（空指针取消引用），或者对于混合前向和反向代理声明的配置，可以允许将请求定向到声明的 Unix 域套接字端点（服务器端请求伪造）。”公告显示。

尽管此严重漏洞已被用于任何野外攻击，但Apache httpd团队认为它还存在被攻击者“武器化”的可能。

因此，修补 Apache 网络服务器中的这两个漏洞成为其首要任务。

美国网络安全和基础设施安全局（ CISA）发出警告， 建议用户和管理员查看 Apache 公告，并尽快更新他们的版本，以免遭受不必要的潜在攻击。

11 月，德国联邦信息安全办公室 (BSI) 和思科也曾发出警告，攻击者正利用 HTTP 服务器中的另一个服务器端请求伪造 (SSRF) 漏洞，其编号为
CVE-2021-40438。

> 参考来源：https://securityaffairs.co/wordpress/126077/security/apache-http-> server-flaws.html

