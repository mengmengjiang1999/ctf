**一段时间以来，ESET的研究人员一直在跟踪Winnti的活动，该组织从2012年起就开始活跃，并针对视频游戏和软件行业供应链进行攻击。最近，发现了一个以前未经记录的后门，其目标是Microsoft
SQL（MSSQL）。这个后门与PortReuse后门有多处相似之处，PortReuse是Winnti
Group使用的另一个工具，于2019年10月首次记录。**

今年检测到了一个新后门的样本，skip-2.0，作者是winnti组织成员。这个后门程序以MSSQL服务器11和12为目标，攻击者可以使用magic密码连接到任何MSSQL帐户，同时自动将这些连接隐藏在日志中。后门允许攻击者复制、修改或删除数据库内容，可以用来操纵游戏中的货币以获取经济利益。据了解，skip-2.0是第一个公开记录的mssql服务器后门。

本文将重点介绍mssql服务器后门的技术细节和功能，以及skip.2-0与winnti已知武器库（特别是portreuse后门和shadowpad）的技术相似性。

## vmprotected启动程序

我们在查找vmprotected启动程序时找到了skip-2.0，其有效负载通常是portreuse或shadowpad。

### 嵌入式有效载荷

与加密的portreuse和shadowpad有效负载一样，skip-2.0嵌入到vmprotected启动程序中，如图1所示：

![](https://image.3001.net/images/20191031/1572492566_5dba55169046a.png!small)

### 加密

有效负载加密与其他vmprotected启动程序中使用的相同。它是RC5加密的，密钥来自volumeID和字符串f@ukd！RCTO R$。

### 持久性

与portreuse和shadowpad的一样，启动程序可能会通过利用dll劫持而持续存在，方法是将其安装在c:\windows\system32\tsvipsrv.dll。这将导致标准Windows
SessionEnv服务在系统启动时加载DLL。

## 打包器

一旦解密，嵌入的有效负载实际上是winnti
group的自定义打包程序。这个打包器与我们在[白皮书](https://www.welivesecurity.com/wp-content/uploads/2019/10/ESET_Winnti.pdf)中记录的代码是相同的。它被用来打包portreuse后门以及嵌入在受损视频游戏中的负载。

### 配置

打包程序配置包含打包二进制文件的解密密钥及其原始文件名、大小和执行类型（exe或dll）。有效载荷配置如表1所示。

![](https://image.3001.net/images/20191031/1572492832_5dba5620853a8.png!small)

打包器配置可以看出，有效负载称为内部装载器。内部加载程序是一个注入器的名称，它是winnti集团的武库的一部分，用于将portreuse后门注入监听特定端口的进程。

### 内部加载器

这是一种内部加载程序的变体，不是像注入portreuse后门时那样寻找监听特定端口的进程，而是寻找名为sqlserv.exe的进程，这是mssql
server的常规进程名。如果找到，则内部加载程序会将有效负载注入此进程。此有效负载还与自定义打包程序打包在一起，该有效负载的打包程序配置如表2所示。

![](https://image.3001.net/images/20191031/1572493298_5dba57f2e2e26.png!small)

此注入负载的原始文件名为skip-2.0.dll。

## skip-2.0

在被内部加载程序注入并启动之后，skip-2.0首先检查它是否在sqlserv.exe进程中执行，如果是，则检索sqllang.dll的句柄，该句柄由sqlserv.exe加载。然后继续从该dll中查找并挂接多个函数。图2描述了skip-2.0的运行过程。

![](https://image.3001.net/images/20191031/1572493388_5dba584c49c9b.png!small)

### Hooking sqllang.dll

skip-2.0使用的hook过程与netagent非常相似，netagent是负责安装网络hook的portreuse模块。这个hook库基于distorm开源反汇编程序，该反汇编程序由多个开源挂接框架使用。需要一个反汇编库来正确计算要hook的指令的大小。在下图中可以看到，NetAgent和Skip-2.0使用的hook过程几乎相同。

![](https://image.3001.net/images/20191031/1572493470_5dba589ec8746.jpg!small)

图3Hex-Rays output comparison between the NetAgent (left) and skip-2.0 (right)
hooking procedures

有一个显著的区别就是skip-2.0中的hooking函数将要安装的钩子的地址作为参数，而对于netagent，要安装的钩子的地址是硬编码的。这是因为skip-2.0必须hooksqllang.dll中的多个函数才能正常运行，而netagent只针对一个函数。

要定位hook的每个sqllang.dll函数，skip-2.0首先通过解析pe头来检索加载到内存中的dll的大小（即其虚拟大小）。然后初始化sqllang.dll中要匹配的字节数组，如图4所示。一旦找到与字节数组匹配的第一个匹配项的地址，就会使用图3所示的过程安装钩子。

![](https://image.3001.net/images/20191031/1572493590_5dba5916379bd.png!small)

然后，钩子安装成功后会在cleartext中记录，该文件位于硬编码路径c:\ windows\temp\ts\u 2ce1.tmp中，如图5所示。

![](https://image.3001.net/images/20191031/1572493690_5dba597aa2f41.png!small)

如果找不到目标函数，钩子安装程序将搜索具有不同字节模式集的回退函数。

通过匹配字节序列来定位目标函数的地址，而不是使用静态偏移量，再加上使用字节的回退序列，skip-2.0可以更灵活地适应mssql更新，并可针对多个sqllang.dll更新。

### 密码控制

skip-2.0的目标函数与身份验证和事件日志记录相关。目标功能包括：

    
    
    CPwdPolicyManager::ValidatePwdForLogin
    CSECAuthenticate::AuthenticateLoginIdentity
    ReportLoginSuccess
    IssueLoginSuccessReport
    FExecuteLogonTriggers
    XeSqlPkg::sql_statement_completed::Publish
    XeSqlPkg::sql_batch_completed::Publish
    SecAuditPkg::audit_event::Publish
    XeSqlPkg::login::Publish
    XeSqlPkg::ual_instrument_called::Publish

其中最有趣的函数是第一个函数（cpwdpolicymanager：：validatepwdforlogin），它负责验证为给定用户提供的密码。

此函数的钩子检查用户提供的密码是否与magic密码匹配；如果是，则不会调用原始函数，钩子将返回0，从而允许连接。然后设置一个全局标志，该标志将由负责事件日志记录的其他hook函数进行检查。相应的反编译过程如图6所示。在设置此全局标志的情况下，hook的日志记录函数将静默返回，而不调用其对应的原始函数，因此不会记录操作。

![](https://image.3001.net/images/20191031/1572493924_5dba5a64daa60.png!small)

如果使用magic密码登录，reportloginsaccess和issueloginsuccessreport挂钩将不会调用原始函数。同样的行为也适用于feexecutelogontriggers。其他日志记录功能，如xesqlpkg：：sql_completed：：publish或xesqlpkg：：sql_batch_completed：：publish，在用户使用魔法密码登录的情况下也将被禁用。还禁用了多个审核事件，包括secauditpkg：：audit_event：：publish、xesqlpkg：：login：：publish和xesqlpkg：：uau
instrument_called：：publish。

这一系列hook不仅允许攻击者通过特殊密码在受害者的mssql服务器中获得持久控制，而且使用该密码时禁用了多个日志，因此无法检测到攻击者。

研究人员对多个MSSQL Server版本测试了Skip-2.0，发现能够使用MSSQL Server
11和12的密码成功登录。为了检查skip-2.0是否针对特定的sqllang.dll版本，创建了一个yara规则，该规则可以在[github](https://github.com/eset/malware-ioc/tree/master/winnti_group)库中找到。

## 与Winnti的联系

skip-2.0和来自winnti的其他工具有很多相似之处。vmprotected启动程序、自定义打包程序、内部加载程序和hook框架是winnti工具集的一部分。

## 总结

skip-2.0后门是winnti的工具集之一，它与该组织已知的工具集有很多相似之处，并允许攻击者在mssql服务器上实现持久控制。安装钩子需要管理权限，所以必须在已经被攻陷的mssql服务器上使用skip-2.0来实现持久控制和隐蔽。

 ***参考来源：[welivesecurity](https://www.welivesecurity.com/2019/10/21/winnti-group-skip2-0-microsoft-sql-server-backdoor/)，由Kriston编译，转载请注明来自FreeBuf.COM**  

