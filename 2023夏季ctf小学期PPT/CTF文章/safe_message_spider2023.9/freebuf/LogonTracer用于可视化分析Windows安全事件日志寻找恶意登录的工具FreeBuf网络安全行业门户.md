##
![LogonTracer：用于可视化分析Windows安全事件日志寻找恶意登录的工具](https://image.3001.net/images/20180523/15270257916478.png!small)

## 简介

**LogonTracer是一款用于可视化分析Windows安全事件日志寻找恶意登录的工具。它会将登录相关事件中找到的主机名（或IP地址）和帐户名称关联起来，并将其以图形化的方式展现出来。通过这种方式，可以看到哪个帐户中发生过登录尝试以及哪个主机被使用。[基于此研究](https://www.first.org/resources/papers/conf2016/FIRST-2016-105.pdf)，该工具可以可视化与Windows登录相关的下列事件ID。**

> 4624：登录成功
>
> 4625：登录失败
>
> 4768：Kerberos身份验证（TGT请求）
>
> 4769：Kerberos服务票据（ST请求）
>
> 4776：NTLM身份验证
>
> 4672：分配特殊权限

更多细节可在以下文档中查看：

> [可视化事件日志识别非法账户 - LogonTracer -](http://blog.jpcert.or.jp/2017/11/visualise-> event-logs-to-identify-compromised-accounts---logontracer-.html)
>
> [可视化事件日志识别非法账户（日文）](http://blog.jpcert.or.jp/2017/11/visualise-event-logs-> to-identify-compromised-accounts---logontracer-.html)

 **额外分析**

LogonTracer使用
[PageRank和](https://en.wikipedia.org/wiki/PageRank)[ChangeFinder](https://pdfs.semanticscholar.org/c5bc/7ca31914d3cdfe1b2932cbc779875e645bbb.pdf)从事件日志中检测恶意主机和帐户。

![LogonTracer：用于可视化分析Windows安全事件日志寻找恶意登录的工具](https://image.3001.net/images/20180523/15270258389081.png!small)

使用LogonTracer，也可以按时间顺序显示事件日志。

![LogonTracer：用于可视化分析Windows安全事件日志寻找恶意登录的工具](https://image.3001.net/images/20180523/1527025862378.png!small)

## LogonTracer使用

> ## [安装](https://github.com/JPCERTCC/LogonTracer/wiki/how-to-install)
>
> ## [使用docker](https://github.com/JPCERTCC/LogonTracer/wiki/jump-start-with-> docker)

## 文档

如果你想更进一步的了解这款工具，请查看[LogonTracer
wiki](https://github.com/JPCERTCC/LogonTracer/wiki).。

## 架构

LogonTracer是基于Python编写的，并使用Neo4j作为其数据库。以下工具会使用到。

Python 3

> [Neo4j](https://neo4j.com/)用于图形数据库。
>
> [Neo4j JavaScript driver](https://github.com/neo4j/neo4j-javascript-> driver)，用于使用二进制协议连接到Neo4j。
>
> [Cytoscape](http://www.cytoscape.org/)一款图形化显示网络并进行分析和编辑的软件。
>
> [Flask](http://flask.pocoo.org/)一个使用 Python 编写的轻量级 Web 应用框架。

 ***参考来源：[GitHub](https://github.com/JPCERTCC/LogonTracer)，FB小编 secist
编译，转载请注明来自FreeBuf.COM**  

