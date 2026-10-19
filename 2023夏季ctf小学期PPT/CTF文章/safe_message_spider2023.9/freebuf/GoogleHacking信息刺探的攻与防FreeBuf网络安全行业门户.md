*** 本文作者：K0rz3n，本文属FreeBuf原创奖励计划，未经许可禁止转载**

**我们都知道渗透测试中信息收集的重要性，是第一步也是最重要的一步。有的人渗透测试使出浑身解数破门而不入，可对有的人来说却如同囊中取物，也许功力就是差在信息收集，那么现在就让我带领各位读者重新认识一下Google———你军火库中的“大咖”
。（前面基础部分希望大家不要错过，说不定有你不知道的秘密，各位服务器管理员也不要错过最后的彩蛋哦！）**

##  **0X01 你不得不知道的谷歌基础**

###  **一、谷歌周边**

 **1.谷歌图片**

谷歌图片是一个图片识别的非常强大的工具，一张你不知道来源的图片上传之后不仅能知道来源，还能自动寻找相似图片。

![Image](https://image.3001.net/2018/04/5d8f11164726d92b84fba2785f18665c.png)  

![Image](https://image.3001.net/2018/04/9b4a65ae21ffbae72f4f41548d071bb0.png)  

**2.谷歌地球**

坐看世界各地，笑看云卷云舒，渗透之前看看渗透的地方长啥样对吧...

![Image](https://image.3001.net/2018/04/b07a559c568d5181b5d47b6b7e2921d0.png)  

![Image](https://image.3001.net/2018/04/fbe622d16cf436daaeab5dc8e565d4ac.png)  

**3.谷歌论坛**

信息收集的重要地点，谷歌背后的繁荣之地（多得是你不知道的事）

![Image](https://image.3001.net/2018/04/2f1393c567819b20c99dcc23c11aab80.png)  

**4.谷歌日历**

记录你生活的点点滴滴，有时却给hacker留下了巨大的财富

![Image](https://image.3001.net/2018/04/452c96e233e517c3c970426d6baed84e.png)  

![Image](https://image.3001.net/2018/04/2ecfbe9357141347d23f92f46e010701.png)  

**5.谷歌地图**

找到你回家的路，跑路的重要工具.....

![Image](https://image.3001.net/2018/04/283b7c60186c315bb322412bf2c83697.png)
**  
**

 **6.谷歌高级搜索**

这个功能异常强大，更加能满足你的需要  

![Image](https://image.3001.net/2018/04/3df6c1edff7b174300e1a38a6322cd6d.png)  

**7.谷歌自定义搜索引擎**

![Image](https://image.3001.net/2018/04/17097a8d408537abf1a4b504e7e3d196.png)
**  
**

 **8.GHDB 谷歌黑客数据库**

<https://www.exploit-db.com/google-hacking-database/>

 **这一部分我会放在github中会仔细的讲一下,链接地址在本文下方，希望大家关注**

###
![Image](https://image.3001.net/2018/04/fa9187314a98d439e3a3736db64cb90a.png)

### 二、搜索基础

1.查询是 **不区分** 大小写（OR在表示布尔含义时一定要大写）

2.*在谷歌搜索的时候只能当做 **一个单词** 使用

3.谷歌有32词的搜索限制（当然可以通过*代替某些单词突破这种限制）

4.短语搜索要带上 **单引号**

5.AND对谷歌来说是多余的，谷歌会自动查询你输入的一切

6.谷歌会忽略特别常见的字符，但是前面加上"+"强制搜索（+后面 **不能** 有空格）

7.NOT可以使用"-"(减号代替)

8.布尔查询OR/"|"

## 0X02 不得不说的高级运算符

###  **一、总览**

> intitle，allintitle
>
> inurl,allinurl
>
> filetype
>
> allintext
>
> site
>
> link
>
> inanchor
>
> datarange
>
> cache
>
> info
>
> related
>
> phonebook
>
> rphonebook
>
> bphonebook
>
> uthor
>
> group
>
> msgid
>
> insubject
>
> stocks
>
> define

 **使用方法：**

operator:search

 **注意点：**

1.在操作符、冒号、搜索项之间 **没有** 空格

2.all运算符（以all开头的运算符)都是有些奇怪的,通常一个查询只能使用 **一次** ，而且不能和其他运算符一起使用

①allintitle 会告诉谷歌，它后面的每一个单词或者短语都要在标题中出现

②allintext 在除了标题、URL、链接以外的任何地方找到某个内容（它后面的每一个单词或者短语都要在内容中出现）

3.intitle:"index of"等价于 intitle:index.of

因为‘.’休止符能够代替任何字符(这个技术也提供了一个无需键入空格和两边引号的短语)

4.intitle:"index of" private 能返回标题中有index of 以及在任何地方有
private的页面（intitle只对其后面第一个搜索项有效）

###  二、常见运算符解释

 **site 把搜索精确到特定的网站**

site 允许你搜索仅仅位于一个特定服务器上的或者在一个特定域名里的页面

 **filetype 搜索特定后缀的文件**

搜索以一个特别的文件扩展名结尾的页面，谷歌会以网页快照的形式来将这种格式转换成html页面，但是你直接点击标题就会下载

 **link 包含指定网页的链接的网页**

搜索包含指定网页的链接的网页，link后面跟的是完整的URL可以包含目录名、文件名、参数等，信息量越大查询结果越精确。

 **注意**

1\. 不要认为
Link能搜索链接中的文本，inanchor才执行的是这个操作，如果输入错误，那么并不会执行link查询而是把[link:短语]当做一个整体直接默认查询

2\. link运算符不能和其他运算符一起使用

 **inanchor 寻找链接的锚点**

inanchor 用于寻找链接的锚点，或者在链接中显示的文本（就是显示在页面上的提供点击的文字）

 **cache 显示页面的缓存版本**

直接跳转到页面的缓存版本

 **numberange 搜索一个数字**

numberange 需要两个参数，一个低位数字，一个高位数字，中间用连字符分割

例如：

为了找到12345 numberange:12344-12346

 **注意：**

1.这个运算符还有简化版， 12344..12346

2.可以和其他运算符一起使用

 **daterange 搜索在特定日期范围内发布的页**

谷歌每次重新抓取一个网页网页的日期就会刷新

两个参数日期都必须是自公元前4713年1月1日起经过的天数，中间用连字符分割但（不如使用谷歌的高级搜索引擎实现）

 **info 显示谷歌的总结信息**

显示一个网站的总结信息还提供了可能关于该网站的其他搜索链接

 **注意：**

info不能和其他运算符一起使用

 **related 显示相关站点**

参数是一个URL

**注意：**

1.点击类似网页链接和使用高级搜索引擎能实现相同的功能

2.不能和其他运算符一起使用

 **define 显示一个术语的定义**

此处语言苍白......

## 0X03 Google Hacking 基础

## 文件类

### 一、目录列表的查找

目录列表能列出存在于一个web服务器上的文件和目录

查找目录列表

 **实例：**

intitle:index.of 这里的休止符代表的是单个字母的通配符

![Image](https://image.3001.net/2018/04/2850b402574ee273820b44e599ed1991.png)  

更优化的查找

 **实例：**

intitle:index.of "parent directory"

intitle:index.of name size

###  二、（特定版本的）服务器

能被攻击者用来决定攻击web服务器最佳方法的一小段信息，就是确切的服务器版本

实例：

intitle:index.of "server at"

intitle:index.of "Apache/1.3.27 Server at"

![Image](https://image.3001.net/2018/04/1c8b1c39037ae4c6cc7e0bb1b61d0ce5.png)  

我们还可以确定服务器的操作系统、模块和其他信息

我们会把操作系统写在括号里

> Apache/1/3/26(Unix)
>
> CentOS
>
> Debian
>
> Debian GNU/Linux
>
> Fedora
>
> FreeBSD
>
> Linux/SUSE
>
> Linux/SuSE
>
> NETWRE
>
> Red Hat
>
> Ubuntu
>
> UNIX
>
> Win32

攻击者能结合这个操作系统标签里的信息以及web服务器的版本制定有针对性的攻击

### 三、扩展遍历技术

经常会出现web页面的备份文件，他们有泄露源码的倾向。常常在配置错误的时候出现这种问题，把php代码备份到不是以php结尾的文件中，比如bak

 **实例：**

intitle:index.of index.php.bak

inurl:index.php.bak

![Image](https://image.3001.net/2018/04/dc31747eb63a88ba949e992166c1ce31.png)  

### 四、配置文件的查找

配置文件的存在说明服务就在附近

 **实例：**

filetype:conf inurl:firewall

![Image](https://image.3001.net/2018/04/232b386fbefc7d2de6b7e1c0fcdd8410.png)  

如果你能知道配置文件的名字也是一个非常好的搜索方式，当然你可以从配置文件中抽取特定的字符串来查询，如果能再配上软件名字的话就效果更好了

 **注意：**

1.除了配置文件名conf的使用，也可以组合其他的通用的命名规则来查找其他等价的命名规则

inurl:conf OR inurl:config OR inurl:cfg

### 五、日志文件的查找

日志文件中也记录着日志很多的敏感信息

日志文件也有一个默认的名字可以被我们用作基础的搜索，最常见的扩展名就是log了

 **实例：**

filetype:log inurl:log

ext log log

filetype:log username putty

![Image](https://image.3001.net/2018/04/5b99bf6419c4cc3c58b0b3569b12b23f.png)  

### 六、office文档

 **实例：**

filetype:xls inurl:password.xls

filetype:xls username password email

![Image](https://image.3001.net/2018/04/563dff1d7a14f54d296acf4afebc1886.png)  

## 数据库、后台类

### 一、登录入口

登录入口是第一道防线，很容易泄露软硬件的信息

查找入口一般使用关键字login

大的厂商一般会把版权的注意事项放在页面的底部

 **实例：**

intitle:login intext:版权信息

![Image](https://image.3001.net/2018/04/50d9ee88a5bc05e08b03f855529c79cb.png)  

###  二、错误消息

数据库的错误消息能够用来分析操作系统和web服务器的版本，还可能更多

SQL command not properly ended

这个表示没有在sql语句的最后找到正确的终止符，所以可能会被用于注入攻击

### 三、数据库的转储

数据库基于文本的转换在网络上是很常见的，使用数据库的转储数据库管理员能完整地重建数据库，也就意味着一个完整的转储的细节并不只是数据表格的结构还有每张表的每一条记录。

攻击者可以搜索转储的标题 # Dumping data for table并且通过执行必要的关键词 username password等能够缩小范围

 **实例：**

# Dumping data for table(user|username|password|pass)

还可以关注一些由别的工具添加到数据库转储中最后的文件名

 **实例：**

filetype:sql sql

![Image](https://image.3001.net/2018/04/b0dd00e6e11f811fd8e66baebe6590b4.png)  

###  四、真实的数据库文件

攻击者还能直接搜索到数据库本身，并不适合所有的数据库系统，只适合哪些有着特定名字或者扩展名的数据库,因为是二进制文件，所以没法在里面搜索字符

 **实例：**

filetype:mdb inurl:com

![Image](https://image.3001.net/2018/04/6122efd20f28bb4fa4556e4f0e33b4b8.png)  

## 0X4 如何防御Google Hacking

###  web 服务器的安全防护

 **一、目录列表和丢失的索引文件**

.htaccess 可以来防止目录的内容未授权的访问，但是不当的配置还会让这个文件可见甚至可读

在 apache 的服务器上可以通过 httpd.conf文件中的单词indexs前加一个连字符或者减号来禁止目录列表

 **二、robots.txt**

#`开头的行会被认为是注释，每一个不以#开头的行都会以User-agent 或者是一个disallow
声明开头，表示禁止爬虫爬行的位置，但是也可以允许特定的爬虫访问

 **三、NOARCHIVE缓存杀手**

有时候你希望google住抓取某个页面但是又不希望对页面的副本进行缓存，或者搜索结果中显示缓存链接，这个要求可以通过META实现

    
    
    <META NAME= "ROBOTS" CONTENT= "NOARCHIVE">

如果你只想阻止谷歌对文件的缓存，可以在HEAD节里使用

    
    
    <META NAME="GOOGLEBOT" CONTENT="NOINDEX,NOFOLLOW">

 **四、NOSNIPET 去除摘要**

 ****

    
    
    <META NAME="GOOGLEBOT" CONTENT="NOSNIPPET">

另外这个功能还有个副作用，就是谷歌也不能缓存，一举两得。

 **五、十五条防止信息泄露和服务器入侵的措施**

> 1.检查所有的文档能否被Google搜索到，避免敏感文件能出现在公众的视野中
>
> 2.选择一个强大的自动化工具来扫描你网站上是否有信息的泄露
>
> 3.不要使用默认的登录入口，以防止登录入口被hacker猜解
>
> 4.关闭数据库的远程管理工具
>
> 5.删除明显的显示软件版本的信息
>
> 6.配置服务器只能下载特定的文件类型（白名单比黑名单要简单有效得多）
>
> 7.正确的配置你的服务器，不要抱有侥幸心理，任何的松懈带来的灾难是巨大的
>
> 8.不要把源码的备份放在未经授权就能访问的地方，并且及时删除网站上的无用的备份文件
>
> 9.不要使用弱密码，防止攻击者轻易攻破后台
>
> 10.登录请加上强度相对较高的验证手段，防止攻击者采用爆破的手段
>
> 11.关闭服务器不必要的端口
>
> 12.请不要使用网站上的任何信息作为密码，否则都属于容易爆破的类型
>
> 13.备份的源代码请经过专业的混淆，防止被下载之后轻易读取到内容
>
> 14.及时更新服务器的系统，修复潜在的漏洞
>
> 15.安装正规的安全防护软件

## 0X04 总结

亲爱的读者，读到这里真的是辛苦了，我上面讲的这些只是冰山一角，Google能做到的绝对超乎你的想象，如果大家对渗透测试、Google
Hacking或者服务器防范感兴趣可以访问我的github我会把我了解的更多的信息告诉你，而且还会介绍一些谷歌黑客数据库的知识(如果喜欢的话也欢迎你们fork或者star)

 **下面是我的github地址：**

<https://github.com/K0rz3n/GoogleHacking-Page>

 *** 本文作者：K0rz3n，本文属FreeBuf原创奖励计划，未经许可禁止转载**

