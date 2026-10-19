****

[](https://youtu.be/ug5ZuezbD3c)

**![ODAT.jpg](https://image.3001.net/images/20180228/15197817046382.jpg!small)  
**

**ODAT（Oracle Database Attacking Tool）是一款开源的渗透测试工具，主要用于测试远端oracle数据库的安全性。**

## ODAT使用场景示例：

> 你希望找到远端Oracle数据库的SID和有效凭证以连接数据库
>
> 你已获取到一个有效的Oracle帐户，并想将你的权限提升为DBA或SYSDBA
>
> 你有一个Oracle帐户，并希望执行系统命令（例如，反向shell），以在托管数据库的操作系统上进一步的渗透

已在10g 11g和12c(12.1.0.2.0)版本上做过测试。

## 特点

ODAT可以为你做以下事情：

通过以下方式在远端Oracle数据库侦听器上搜索有效SID：

> 字典攻击
>
> 爆力攻击
>
> 侦听器的ALIAS

Oracle账户获取可通过：

> 字典攻击
>
> 密码同账户名 (需要先得到一个可用账户)

在数据库服务器执行系统命令，可使用：

> DBMS_SCHEDULER
>
> JAVA
>
> external tables
>
> oradbg

在数据库服务器存储下载文件，可使用：

> UTL_FILE
>
> external tables
>
> CTXSYS
>
> DBMS_LOB

在数据库服务器上传文件，可使用：

> UTL_FILE
>
> DBMS_XSLPROCESSOR
>
> DBMS_ADVISOR

删除文件可使用：

> UTL_FILE

使用以下系统权限组合获得访问权限，请参阅privesc模块命令的帮助信息）：（2016/02/21）

> CREATE ANY PROCEDURE
>
> CREATE PROCEDURE and EXECUTE ANY PROCEDURE
>
> CREATE ANY TRIGER (and CREATE PROCEDURE)
>
> ANALYZE ANY (and CREATE PROCEDURE)
>
> CREATE ANY INDEX (and CREATE PROCEDURE)

从数据库服务器发送/接收HTTP请求，可使用：

> UTL_HTTP
>
> HttpUriType

扫描本地或远程服务器端口，可使用：

> UTL_HTTP
>
> HttpUriType
>
> UTL_TCP

捕获SMB验证，可通过：

> 一个索引来触发一个SMB连接

利用一些CVE：

[ **CVE-2012-3137**](http://cvedetails.com/cve/2012-3137)

> 拾取任意用户的会话密钥和盐
>
> 对会话进行字典攻击

[**CVE-2012-????**](https://twitter.com/gokhanatil/status/595853921479991297)：通过身份验证的用户可以修改所有可选择的表，即使他无法正常修改它们（无ALTER权限）。

[ **CVE-2012-1675**](http://seclists.org/fulldisclosure/2012/Apr/204) 'TNS
Listener'远程数据投毒漏洞（25/03/2016）。

在搜索模块中搜索列名：

> 在列名中搜索一个匹配模式（例如：password）
>
> unwrap PL/SQL源码（10g/11g和12c）
>
> 获取系统权限和角色分配。

![ODAT_main_features_v2.0.jpg](https://image.3001.net/images/20180228/1519781735873.jpg!small)  

## 支持平台和依赖关系

ODAT当前仅支持Linux平台安装使用。

独立版不需要安装依赖和slqplus（请参阅<https://github.com/quentinhardy/odat/releases/>）。由于安装了pyinstaller，ODAT
standalone已经生成。

如果你想要在你的计算机上安装开发版本，则需要以下工具和依赖项：

语言环境：Python 2.7

Oracle依赖：

> Instant Oracle basic
>
> Instant Oracle sdk

Python库：

> cx_Oracle
>
> passlib
>
> pycrypto
>
> python-scapy
>
> colorlog (推荐)
>
> termcolor(推荐)
>
> argcomplete(推荐)
>
> pyinstaller(推荐)

 ***参考来源：[n0where](https://n0where.net/oracle-database-attacking-tool-odat)，FB小编 secist 编译，转载请注明来自FreeBuf.COM**

