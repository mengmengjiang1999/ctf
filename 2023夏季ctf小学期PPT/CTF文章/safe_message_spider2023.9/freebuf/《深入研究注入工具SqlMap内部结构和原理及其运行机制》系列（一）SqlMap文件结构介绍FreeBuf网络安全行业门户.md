### 《深入研究注入工具SqlMap内部结构和原理及其运行机制》系列（一）：SqlMap文件结构介绍

`2021年的时候因为我在开发自动化渗透工具，所以去研究了一下sqlmap的整体架构和设计模式，也看了一些基于sqlmap的工具设计实现的论文，但是就目前国内来说，很少网络安全研究人员会对sqlmap内部去进行一个比较深入的探讨，甚至一些圈内人看到是sqlmap出来的sql注入漏洞就嗤之以鼻。
很多的研究者都基于sqlmap或sqlmapapi来开发自动化（主动/被动）扫描工具，因为sqlmap在处理各个模块之间的关系都处理得特别优秀，这得益于它内部藕连性强，但是对于学习sqlmap内部源码的同学的学习过程就很不舒服了。
很多初识sqlmap的同学在认识sqlmap的时候就认识不全面，甚至连基础的level或tamper参数都非常陌生，这种情况不可能说是真正意义上的“会”。
所以，我打算把我对sqlmap整个的理解以这种系列的形式公开，以便于真正想探究sqlmap的研究人员可以清楚从底层运行机制到整个环境的合理性的来龙去脉。我觉得作为web安全研究人员，更包括开发工具的一些大佬，都值得去拜读sqlmap的源码和理解他的内部结构及其思想等。
可能周期性有点久，毕竟sqlmap的架构还是相对完整的，这也是导致其代码藕连性强的因素之一。 `

* * *

## **研究环境：**

 **Python 3.7.6**  
 **SQLMap 1.5.2#dev and sqlmapapi**  
![image](https://image.3001.net/images/20220210/1644477472_6204bc202cb36bce79dc4.png!small)

* * *

## Sqlmap官方特征描述 ：

    
    
    全面支持 MySQL、Oracle、PostgreSQL、Microsoft SQL Server、Microsoft Access、IBM DB2、SQLite、Firebird、Sybase、SAP MaxDB、Informix、MariaDB、MemSQL、TiDB、CockroachDB、HSQLDB、H2、MonetDB、Apache Derby、Amazon Redshift、 Vertica、Mckoi、Presto、Altibase、MimerSQL、CrateDB、Greenplum、Drizzle、Apache Ignite、Cubrid、InterSystems Cache、IRIS、eXtremeDB、FrontBase、Raima 数据库管理器、YugabyteDB 和 Virtuoso 数据库管理系统。完全支持六种 SQL 注入技术： 基于布尔的盲注、基于时间的盲注、基于错误的、基于 UNION 查询、堆叠查询和带外 。支持 直接连接到数据库 而无需通过 SQL 注入。支持枚举 用户、密码哈希、权限、角色、数据库、表和列 。自动识别密码哈希格式并支持 使用基于字典的攻击来破解它们 。支持 转储数据库表 、一系列条目或特定列。 用户还可以选择仅转储每列条目中的一系列字符。支持 搜索特定数据库名称、跨所有数据库的特定表或跨所有数据库表的特定列 。 例如，这对于识别包含自定义应用程序凭据的表很有用，其中相关列的名称包含字符串，如 name 和 pass。支持 下载和上传任何文件 从数据库服务器底层文件系统支持 执行任意命令并检索其标准输出 在数据库服务器底层操作系统上支持 之间建立带外有状态 TCP 连接 底层操作系统 根据用户的选择，该通道可以是交互式命令提示符、Meterpreter 会话或图形用户界面 (VNC) 会话。支持 数据库进程的用户权限提升 通过 Metasploit 的 Meterpreter getsystem命令。
    

* * *

## **sqlmap根目录结构：**

![image](https://image.3001.net/images/20220210/1644477506_6204bc422dcebe44be19c.png!small)

### sqlmap/.github :

![image](https://image.3001.net/images/20220210/1644477523_6204bc535a12b7d5655fd.png!small)  
git的代码管理仓库，基本上每个github仓库都会有这个文件夹，记录了文件上传更改等版本信息

### sqlmap/data :

![image](https://image.3001.net/images/20220210/1644477540_6204bc6424569a2313cc9.png!small)  
 **html文件夹** 内存放这index.html里面是个demo，好像是参数介绍，但是进去之后好像功能都不能用。  
 **procs文件夹** 内包含了mssqlserver,mysql,oracle，postgresql的触发程序，存放了一些SQL语句。  
 **shell文件夹** 存放了四种加密过的webshell用于注入成功后上传。  
 **txt文件夹** 内存放着一堆字典，比如字段名，文件名，表名。  
 **udf文件夹** 内有mysql和postgresql 用于udf提权的dll或者so文件，也包含了用户自定义的payload。  
 **xml文件夹** 内包含了多种数据库的六类注入payload和各类数据库的banner以及其他信息

### sqlmap/doc :

![image](https://image.3001.net/images/20220210/1644477551_6204bc6f969b48911cfab.png!small)  
 **translations文件夹** 内包含17种语言版本README.md（官方介绍markdown文档)  
 **AUTHORS文件** 程序编写者及其邮箱，发现sqlmap的相关问题可以直接发送邮件给作者。  
 **CHANGELOG.md文件** 更新日志，介绍了sqlmap更新了哪些功能，Bug修复及相关特性。  
 **THANKS.md 感谢文档** ，介绍对sqlmap有贡献的作者。  
 **THIRD-PARTY.md** 第三方插件，介绍集成在sqlmap的第三方插件的概要说明

### sqlmap/extra：

![image](https://image.3001.net/images/20220210/1644477575_6204bc87f0d1ac885e8ec.png!small)  
 **beep** 警报声音处理文件夹  
 **beep.py** 执行后会发出警报声音，参数为–beep，当发现SQL注入的时候，发出警报声  
 **beep.wav** 警报声音的文件。loak 利用cloak.py可以生成和解密后门等操作。  
 **cloak** 利用cloak.py可以生成和解密后门等操作  
 **dbgtool** 执行转换的文件夹  
dbgtool.py 可以将ASCII文本转化为便携式的exe文件，生成的nc.exe 可以安装到Windows上，进行后门监听，python
./dbgtool.py -i ./nc.exe -o nc.scr  
 **icmpsh** 一个win32的反向icmpshell，在注入成功之后反弹回来的一种shell  
 **runcmd** 注入成功后，反弹回来cmd命令的辅助工具  
 **shellcodeexec**
被安装在受害者机器上的shellcode，这些不是在自己的机器上运行，是要在目标机器上运行，含有Windows和Linux的32和64位的文件  
 **shutils** 文件操作工具，python文件操作，实现查找第三方插件等相关功能  
 **vulnserver** 简易的漏洞服务，用于fuzz测试

### sqlmap/lib ：

![image](https://image.3001.net/images/20220210/1644477588_6204bc94dfb7ccdaca5ec.png!small)  
 **controller 文件夹**  
 **action.py** 利用URL受到影响的参数进行SQL注入，并且在条件许可下抽取系统或者数据库中的数据。  
 **checks.py** 利用载荷对发现的sql注入点进行注入检测。  
 **controller.py** 对用户传递的参数进行控制。  
 **handler.py** 对用户传递的数据库名称进行处理  
 **core** 这是 **核心文件夹** 有各种参数的调用文件，例如设置目标 会调用
target.py。还有agent.py，dump.py，threads.py等等  
 **parse** 该参数文件夹有banner.py cmdline.py sitemap.py configfile.py payloads.py
handler.py html.py headers.py 等一系列配置处理参数调用文件  
 **request** 该请求文件夹有basic.py templates.py basicauthhandler.py
redirecthandler.py comparison.py rangehandler.py connect.py pkihandler.py
direct.py methodrequest.py dns.py inject.py httpshandler.py 等一系列网络请求连接文件  
 **takeover** 这个是接管文件夹，文件夹里面有abstraction.py xp_cmdshell.py icmpsh.py web.py
metasploit.py udf.py registry.py 注入成功后接管受害者机器的shell.  
 **techniques** 这个是注入分类文件夹有blind，dns，error，union，brute
等物类注入类型，其中每个文件夹有相应的注入类型执行文件。  
 **utils** 这是小功能文件夹。该文件中含有 api.py xrange.pycrawler.py versioncheck.py deps.py
timeout.py getch.py hash.py sqlalchemy.py hashdb.py search.py htmlentities.py
purge.py pivotdumptable.py progress.py 等多种功能的调用文件。

### sqlmap/plugins ：

![image](https://image.3001.net/images/20220210/1644477613_6204bcad7e3ca1e80d2dd.png!small)  
 **dbms**
包含各种数据库枚举，连接和接管等相关说明，sqlmap支持Access，DB2，FireBird，HSQLDB，MaxDB，MSSQLServer，MySQL，Oracle，PostgreSQL，SQLite和Sybase数据库等等，每个数据库文件都有固定的文件，例如，MySQL文件夹中含有connector.py,
enumeration.py, filesystem.py, fingerprint.py, syntax.py, takeover.py  
 **generic** 这是个通用文件夹，里面包含 connector.py, custom.py, databases.py, entries.py,
enumeratioin.py, filesystem.py, fingerprint.py, misc.py, search.py, syntax.py,
takeover.py, users.py

### sqlmap/tamper ：

![image](https://image.3001.net/images/20220210/1644477627_6204bcbb08a1d36d3749e.png!small)  
用于存放绕过waf的脚本（tamper)

> apostrophemask.py apostrophenullencode.py appendnullbyte.py  
> base64encode.py  
> between.py  
> bluecoat.py  
> chardoubleencode.py  
> charencode.py  
> charunicodeencode.py commalesslimit.py  
> commalessmid.py  
> concat2concatws.py  
> equaltolike.py  
> escapequotes.py  
> greatest.py halfversionedmorekeywordsifnull2ifisnull.py
> informationschemacomment.lowercase.py modsecurityversioned.py
> modsecurityzeroversioned.multiplespaces.py
> nonrecursivereplacement.poverlongutf8.py  
> percentage.py  
> randomcase.py  
> randomcomments.py  
> securesphere.py  
> sp_password.py  
> space2comment.py  
> space2dash.py  
> space2hash.py  
> space2morehash.py space2mssqlblank.py space2mssqlhash.py space2mysqlblank.py
> space2mysqldash.py  
> space2plus.py  
> space2randomblank.py symboliclogical.py unionalltounion.py unmagicquotes.py  
> uppercase.py  
> varnish.py  
> versionedkeywords.py versionedmorekeywords.py xforwardedfor.py

### sqlmap/thirdparty :

![image](https://image.3001.net/images/20220210/1644477637_6204bcc5daa1b8a938f15.png!small)  
这个是sqlmap的第三方插件，实现各种优化格式的小功能。  
 **ansistrm** 该文件夹中主要文件是ansistrm.py，它定义了结果输出终端的颜色显示。  
 **beautifulsoup**
该文件夹中主要文件是beautifulsoup.py，它把XML等转化为树状表示法，用于爬取目标站点，参数为–crawl。  
 **bottle**
是Python的一个快速，简单和轻巧的WSGI微Web框架。它作为单个文件模块，不依赖其他Python标准库。主要文件是bottle.py，它是构建静态和动态HTTP请求的关键所在，虽然支持Python3，但是由于sqlmap整体是采用python2开发的，所以这里会进行一个兼容性检查。  
 **chardet** 该文件夹中有众多字符探针和字符定义文件，主要作用是探测web页面的页面编码。  
 **clientform** 该文件夹主要文件是clientform.py，它对Web客户端进行HTML表格处理。  
 **colorama** 该文件夹里面的文件其主要功能是为了将ansi转化为win32编码。  
 **fcrypt**
该文件夹主要为标准的Linux加密提供端口，或者说是修复缺失加密功能的Python版本,用于破解通用密码哈希值，参数为–passwords  
 **gprof2dot** #该文件夹里面的文件主要提供了从几个解析器的输出中产生一个dot 图形，  
 **keepalive**
#该文件夹里面的文件是keepalive.py，它的urllib2对HTTP处理程序支持HTTP1.1和存活，keepalive用于持久的HTTP(s)请求，参数为–keep-alive和-o  
 **magic** #该文件夹主要里面的文件是magic.py，magic
是一个libmagic文件识别库的包装器，用于识别和显示日志消息中的文件类型，参数为–file-write  
 **multipart** 该文件夹里面的文件是multipartpost.py，进行多线程发送数据包。  
 **odict** 该文件夹里面的文件是odict.py，为有序字典对象，保存插入顺序的密钥。  
 **oset** Python
ABC类的部分补丁，pyoset.py为主要程序，_abc.py为辅助类的ABC类说明,oset用于对所提供的排序目标进行排序，参数-l，-m和-g  
 **prettyprint** 该文件夹里面主要的文件是prettyprint.py，该脚本优化终端结果输出显示，用于生成xml输出，参数为 –xml  
 **pydes** Python中3DES加密解密算法，其中里面有加密解密算法说明，用于破解Oracle旧密码格式，参数为 –passwords  
 **socks** Python中的sock模块  
 **termcolor** 该文件夹里面文件是termcolor.py，它实现了终端输出的颜色格式化。  
 **wininetpton** 网络地址  
 **xdot** dot格式的可视化图形，用于内部测试  
 **six** 差不多算个空文件夹，里面就一个— **init**.py

 **.gitattributes** git的属性文件，例如：是什么编程语言，具体的文件类型等等  
 **.gitignore** git需要忽略的文件，一般按照理解，把一些没有必要传上去的文件排除在外，不用上传至git仓库中  
 **.pylintrc** Python代码分析工具，用于分析Python代码中的错误和不符合代码风格标准的问题代码  
 **.travis.yml** 标记Python版本和设置sqlmap的脚本  
 **COMMITMENT** 相关承诺 GPL Cooperation Commitment  
 **LICENSE** 授权许可文件  
 **README.md** 相关的说明文件，简单的指导怎么使用安装sqlmap，还针对各种语言版本进行介绍  
 **sqlmap.conf** sqlmap调用的配置文件，比如一些默认的参数，或者是想要提前配置一些默认的参数进行批量自动化扫描探测  
 **sqlmap.py**
sqlmap的主程序，是执行启动sqlmap的程序，执行期间可以调用各种参数进行测试，可以理解为一个可执行文件，到目前位置sqlmap是可以直接支持python2和python3
所以一般的执行操作是python sqlmap.py -u url 就可以开启对目标进行SQL注入测试  
 **sqlmapapi.py**
sqlmap的API文件，可以将sqlmap集成到其他各种平台，比如常用的是在Burpsuite的插件调用sqlmapapi.py接口，进行自动化扫描测试

>  **重点文件夹及文件**
>
> sqlmap/lib/  
> sqlmap/tamper/  
> sqlmap/sqlmap.conf  
> sqlmap/sqlmap.py  
> sqlmap/sqlmapapi.py

下一期： **《深入研究注入工具SqlMap内部结构和原理及其运行机制》系列（二）：循序渐进——从sqlmapapi.py开始研究**

