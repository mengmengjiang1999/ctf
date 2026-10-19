**Web 应用防火墙已经成为众多企业的安全解决方案，然而还是有许多公司**
**经常忽略了一些比较实际的漏洞，仅仅依靠防火墙来进行保护。不幸的是，大多数（不是所有）的防火墙都可以被绕过，在这片文章中，我将会演示如何使用 SQLMap
的一些功能来绕过 WAF / IDS。**  

原作者为 SQLMap 编写了一些脚本，可以在 subversion 存储库的最新开发版本中找到：[svn
checkout](https://svn.sqlmap.org/sqlmap/trunk/sqlmap%20sqlmap-dev)。

篡改脚本的重点在于是使用特殊方法修改请求来避免 WAF 的检测，在某些情况下，可能需要将若干个脚本组合起来一起绕过
WAF。有关篡改脚本的完整列表，请参照<https://svn.sqlmap.org/sqlmap/trunk/sqlmap/tamper/>。

我将要演示的第一个脚本是
**[space2hash.py](https://svn.sqlmap.org/sqlmap/trunk/sqlmap/tamper/space2hash.py)**
和
**[space2morehash.py](https://svn.sqlmap.org/sqlmap/trunk/sqlmap/tamper/space2morehash.py)**
，它们可以与 MySQL 一起使用（依然没有在MSSQL上进行尝试）。这些脚本将所有空格替换为使用随机文本来截断注释，脚本的扩展版本（
**space2morehash.py** ）还将在某些函数名称和括号之间添加注释。

要开始使用篡改脚本，需先使用 --tamper 参数，后面再加上脚本的名称。在本文的示例中，我将使用以下命令：

    
    
    sqlmap -u http://192.168.0.107/test.php?id=1 -v 3 --dbms "MySQL" --technique U -p id --batch --tamper "space2morehash.py"
    

![图1：运行脚本
space2morehash.py](https://image.3001.net/images/20190401/1554094213_5ca198850a308.png!small)

如图1所示，在脚本中使用了 **％23randomText％0A** 来替换注入中的空格，当然这是经过 **URL** 编码的。部分函数如：
**CHAR(), USER(), CONCAT()** 都变为 **FUNCTION%23randomText%0A()** ，因为它们并没有出现在
**[IGNORE_SPACE_AFFECTED_KEYWORDS](https://svn.sqlmap.org/sqlmap/trunk/sqlmap/lib/core/settings.py)**
的黑名单中。这是因为 **MySQL** 的
**[函数名称的解析](https://dev.mysql.com/doc/refman/5.1/en/function-resolution.html)** 以及它是如何处理函数的调用和标识符的。

另外两个替换空格的脚本是
**[space2mssqlblank.py](https://svn.sqlmap.org/sqlmap/trunk/sqlmap/tamper/space2mssqlblank.py)**
和
**[space2mysqlblank.py](https://svn.sqlmap.org/sqlmap/trunk/sqlmap/tamper/space2mysqlblank.py)**
。 **MySQL** 允许字符 **09, 0A-0D, A0** 被用作空格，而 **MSSQL** 允许的字符范围要更加的宽，包括从
**01-1F** 。

![图2：space2mssqlblank.py
使用不同的字符作为空格](https://image.3001.net/images/20190401/1554094254_5ca198ae1c629.png!small)

接下来我们有一些乱码的脚本：
**[charencode.py](https://svn.sqlmap.org/sqlmap/trunk/sqlmap/tamper/charencode.py)**
和
**[chardoubleencode.py](https://svn.sqlmap.org/sqlmap/trunk/sqlmap/tamper/chardoubleencode.py)**
。这些脚本对于绕过不同的关键字过滤非常有用，例如，当检测到 **table_name** 且无法绕过它时。

![图3：charencode.py
可用于绕过关键字检测](https://image.3001.net/images/20190401/1554094265_5ca198b9709ae.png!small)

如果 Web 应用的 **URL** 由于某些原因解码了请求，则 **chardoubleencode.py** 脚本就可以派上用场。

![图4：当应用程序解码请求时，可以使用
chardoubleencode.py](https://image.3001.net/images/20190401/1554094278_5ca198c60f879.png!small)

此外，如果有的应用是用 **ASP / ASP.NET** 编写的话，则
**[charunicodeencode.py](https://svn.sqlmap.org/sqlmap/trunk/sqlmap/tamper/charunicodeencode.py)**
和
**[percentage.py](https://svn.sqlmap.org/sqlmap/trunk/sqlmap/tamper/percentage.py)**
脚本就可以用于隐藏真正有效的 payload。

![图5：charunicodeencode.py 使用 Unicode
编码模糊注入](https://image.3001.net/images/20190401/1554094287_5ca198cf5ac7c.png!small)

 **ASP** 的一个有趣特性就是可以在字符之间添加任意数量的百分号。例如， **`AND 1=%%%%%%%%1`** 就十分有效！

![图6：每个字符之间的任意数量百分号在 ASP
中有效](https://image.3001.net/images/20190401/1554094298_5ca198daa8d5f.png!small)

“总之，我只是展示了一部分的脚本，我强烈建议你们在使用前要对其进行测试，因为每个脚本可以在不同的情况下使用。”

***本文源自：[websec](https://www.websec.ca/publication/Blog/Bypassing_WAFs_with_SQLMap)
，由大学新生Bai 翻译整理，转载请注明来自 Freebuf**

