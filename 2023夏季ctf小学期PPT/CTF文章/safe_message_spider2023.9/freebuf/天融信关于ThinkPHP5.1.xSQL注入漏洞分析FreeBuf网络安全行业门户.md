## 一、背景介绍

ThinkPHP 是一个快速、简单的基于 MVC 和面向对象的轻量级 PHP 开发框架，遵循 Apache2
开源协议发布。ThinkPHP从诞生以来一直秉承简洁实用的设计原则，在保持出色的性能和至简的代码的同时，也注重开发体验和易用性，为 WEB 应用和 API
开发提供了强有力的支持。

在近期，ThinkPHP 框架被曝出存在SQL注入漏洞。由于SQL注入漏洞的危害性以及该框架应用十分广泛。
对此，天融信阿尔法实验室以静态和动态两种方式对该漏洞进行了深入分析。

### 1.1 漏洞描述

在ThinkPHP5.1.23之前的版本中存在SQL注入漏洞，该漏洞是由于程序在处理order by
后的参数时，未正确过滤处理数组的key值所造成。如果该参数用户可控，且当传递的数据为数组时，会导致漏洞的产生。

### 1.2 受影响的系统版本

ThinkPHP < 5.1.23

### 1.3 漏洞编号

CVE-2018-16385

## 二、环境搭建

1.下载安装thinkphp5.1.x

对于thinkphp5.1.x完整版，目前官方没有直接下载的链接。Github上只是放出核心版。该版本需要以Composer或Git方式进行安装。

这里以Composer安装方式说明：

在 Linux 和 Mac OS X 中可以运行如下命令：

curl -sS https://getcomposer.org/installer | php

mv composer.phar/usr/local/bin/composer

在 Windows 中，你需要下载并运行 Composer-Setup.exe 。

安装好之后，切换路径到WEB目录下运行：

composercreate-project topthink/think=5.1.1 tp5.1 --prefer-dist

然后会生成一个名为tp5.1的文件夹。到此think5.1.1下载成功。

2.然后在浏览器中访问  

  
![image.png](https://image.3001.net/images/20180925/1537862328_5ba9eab8a2416.png!small)

  

如果出现该页面，则证明安装成功。

3.Demo示例

  
  

编写Demo文件，并将文件命名为Test.php，然后放在/tp5.1/application/index/controller/目录下。

4.数据库

与Demo文件匹配，需要创建一个user表，然后设一个字段(id)。

  
![image.png](https://image.3001.net/images/20180925/1537862343_5ba9eac76f089.png!small)  

## 三、漏洞细节

在/thinkphp/library/think/db/Builder.php parseOrder()的函数中：

  
![image.png](https://image.3001.net/images/20180925/1537862354_5ba9ead205eb3.png!small)  

通过Demo传入order参数内容，当传入的$order是一个数组时，foreach函数将$order数组分为key和value形式。

根据漏洞修复补丁，知道漏洞发生在parseOrderField()函数中。

当$val为数组时，会进入parseOrderField()函数。

跟踪parseOrderField()函数

  
![image.png](https://image.3001.net/images/20180925/1537862361_5ba9ead953570.png!small)  

getOptions()函数是获取了当前要查询的参数，getFieldsBind()函数是获取数据表绑定信息，foreach循环是对$val值进行了处理，这里其实不是重点，就提一下。$val值是什么不用管，因为注入点在$key上，而$val
拼接在$key后面，可以在构造$key加#注释掉$val。

  
![image.png](https://image.3001.net/images/20180925/1537862371_5ba9eae382e1c.png!small)  

重点是parseKey()函数，跟踪parseKey()函数

  
![image.png](https://image.3001.net/images/20180925/1537862379_5ba9eaeb70b2e.png!small)  

这里对传入的$key进行多重判断以及处理。

1\. is_numeric判断，如果是数字，则返回，不是的话继续向下执行。

2\. 判断$key是否属于Expression类。

3\. strpos($key, '->') && false ===strpos($key, '(') 。

4\. ('*' != $key && ($strict ||!preg_match('/[,\'\"\\*\\(\\)`.\s]/', $key)))。

因为$key是我们的sql注入语句，所以1.2.3肯定不满足，而4满足。

所以此时的$key会在左右两侧加个 ` 号。

$table不存在，不会对$key修改，所以加 `
号后会返回$key，然后和$val以及field字符串进行拼接，再然后return赋值给array变量，紧接着，array与order by
字符串进行拼接形成order by查询语句，最终系统调用query()函数进行数据库查询，触发漏洞。

  
![image.png](https://image.3001.net/images/20180925/1537862394_5ba9eafa5c8d3.png!small)  

着重说明一下，这里由于field函数，漏洞利用有两个关键点：

首先解释下field()函数：MySQL中的field()函数作用是对SQL中查询结果集进行指定顺序排序。一般与order by 一起使用。

关键点1

field()函数必须指定大于等于两个字段才可以正常运行，否则就会报错。

  
![image.png](https://image.3001.net/images/20180925/1537862400_5ba9eb00e0de8.png!small)

当表中只有一个字段时，我们可以随意指定一个数字或字符串的参数。

![image.png](https://image.3001.net/images/20180925/1537872807_5baa13a79d010.png!small)  
  

关键点2

当field中的参数不是字符串或数字时，指定的参数必须是正确的表字段，否则程序就会报错。这里由于程序会在第一个字段中加 `` 限制
,所以必须指定正确的字段名称。第二个字段没有限制，可以指定字符串或数字。  

![image.png](https://image.3001.net/images/20180925/1537872981_5baa14558f32c.png!small)

  

所以，我们要利用该漏洞，第一我们至少需要知道表中的一个字段名称，第二向field()函数中中传入两个字段。第二个字段不需要知道字段名，用数字或字符串绕过即可。

Payload构造

根据以上分析，构造payload需要满足以下条件：

1.传入的$order需要是一个数组。

2.$val 必须也是数组。

3.至少知道数据库表中的一个字段名称，并且传入两个参数。

4.闭合 ` 。

最终Payload构造如下：

http://127.0.0.1/tp5.1/public/index/test/index?order[id`,111)|updatexml(1,concat(0x3a,user()),1)%23][]=1

或

http://127.0.0.1/tp5.1/public/index/test/index?order[id`,'aaa')|
updatexml(1,concat(0x3a,user()),1)%23][]=1

  

![image.png](https://image.3001.net/images/20180925/1537873363_5baa15d3023e7.png!small)  

## 四、动态调试分析

有时候单单静态分析，很难知道某些函数做了些什么，而对于程序运行过程，也很难理解透彻。而利用动态分析，一步一步debug，就很容易理解清楚。

这里我们利用上面构造的payload进行debug。

首先下断点

  
![image.png](https://image.3001.net/images/20180925/1537873373_5baa15dd2cf06.png!small)  

$val是个数组，进入parseOrderField()函数。F7下一步（我这里用的是phpstorm，F7是单步调试的意思）。

  
![image.png](https://image.3001.net/images/20180925/1537873379_5baa15e3a604b.png!small)  

foreach循环后，可以看到只是处理了$val，并没有涉及$key（我们的关注点在$key）。$val
的值是在$key的基础上加了个:data__前缀，后面加了个0。

继续F7，进入了parseKey()函数。

  
![image.png](https://image.3001.net/images/20180925/1537873386_5baa15ea6bb28.png!small)  

到这里，看到$key满足if条件，然后两边加了个 ` 号。

  
![image.png](https://image.3001.net/images/20180925/1537873402_5baa15fa3157d.png!small)

  

最后返回的$key。其实就是两边加了个 ` 号 。

  
![image.png](https://image.3001.net/images/20180925/1537873426_5baa161270e56.png!small)  

最后，返回给array变量的值为file字符串和$key以及$val的拼接。

继续F7，看看接下来程序怎么走。

  
![image.png](https://image.3001.net/images/20180925/1537873435_5baa161bebd34.png!small)

  
![image.png](https://image.3001.net/images/20180925/1537873441_5baa16214f720.png!small)  

进行了limit分析，union分析等多个分析处理，最终来到了removeoption()函数。

  
![image.png](https://image.3001.net/images/20180925/1537873453_5baa162d9337e.png!small)  

可以看到这里的$sql，已经可以触发注入漏洞。

  
![image.png](https://image.3001.net/images/20180925/1537873458_5baa1632c8530.png!small)  

然后经过了中间的几个过程，对比上图，并没有改变sql语句内容。最后sql语句，进入query()函数执行了SQL语句，成功触发注入漏洞。

## 五、修复建议

官方补丁

目前官方已经更新补丁，请受影响的用户尽快升级到ThinkPHP5.1.24版本。

手工修复

根据官方给出的方案进行代码修改。

https://github.com/top-think/framework/commit/f0f9fc71b8b3716bd2abdf9518bcdf1897bb776

