原创： CoColer 合天智汇

原创投稿活动：[重金悬赏 |
合天原创投稿等你来](http://link.zhihu.com/?target=https%3A//mp.weixin.qq.com/s/Nw2VDyvCpPt_GG5YKTQuUQ)

## 0x00 前言  

最近刷题碰到好几个关于php代码审计中session相关的问题，之前没有做过系统的总结，在此补一下锅。

## 0x01 Session基础知识  

这里主要讲讲传统的PHP中的“服务端Session”。至于什么是服务端Session，什么是客户端Session，可以看看P神的**客户端 session
导致的安全问题https://www.leavesongs.com/PENETRATION/client-session-security.html

Session概念：在计算机中，尤其是在网络应用中，称为“会话控制”。Session 对象存储特定用户会话所需的属性及配置信息。这样，当用户在应用程序的
Web 页之间跳转时，存储在 Session 对象中的变量将不会丢失，而是在整个用户会话中一直存在下去。当用户请求来自应用程序的 Web
页时，如果该用户还没有会话，则 Web 服务器将自动创建一个 Session 对象。当会话过期或被放弃后，服务器将终止该会话。

Session机制：session内容一般以文件的形式存储于服务器中，而本地浏览器会存储一个与服务器中session文件对应的Cookie值，Cookie存储的是键值为“PHPSESSID”的Seeion_id值，用户在访问web应用时，每次跳转发生http请求时，会自动把这个存储session_id的Cookie值发送过去，因此web应用的所有页面都可以获取到这个SESSION_ID值，也就可以通过session_id获取服务器中存储的session值，当用户关闭浏览器后，cookie存储的session_id自动清除，一般服务器存储的session文件也会在30分钟后自动清除。

比如在wamp环境下，index.php如下：

<?php session_start(); phpinfo();?>

![v2-fc0937cd33331d2740370143c41a2b98_hd.j](https://pic2.zhimg.com/80/v2-fc0937cd33331d2740370143c41a2b98_hd.jpg)

首先理解一下session_start()

当会话自动开始或者通过 session_start() 手动开始的时候， PHP
内部会依据客户端传来的PHPSESSID来获取现有的对应的会话数据（即session文件）， PHP 会自动反序列化session文件的内容，并将之填充到
$_SESSION 超级全局变量中。如果不存在对应的会话数据，则创建名为sess_PHPSES
SID(客户端传来的)的文件。如果客户端未发送PHPSESSID，则创建一个由32个字母组成的PHPSESSID，并返回set-cookie。

可以看到请求中对应的PHPSESSID：ifrvi9r7ui81r0fjq569b06862

在服务器端，即/wamp/tmp下我们就可以发现一个生成的记录Session的文件，因为也没有记录什么会话信息，因此该文件是一个空文件。

![v2-a56113ef425fa9670ca4d7eb9e84a28f_hd.j](https://pic4.zhimg.com/80/v2-a56113ef425fa9670ca4d7eb9e84a28f_hd.jpg)

补充一下关于php-Session相关配置的说明

在php.ini中对Session存在许多配置，这里我们通过phpinfo来说明几个重要的点。

![v2-613d77e691706fedeb7c0a8524db8b5d_hd.j](https://pic1.zhimg.com/80/v2-613d77e691706fedeb7c0a8524db8b5d_hd.jpg)

说明如下：

session.save_path="" --设置session的存储路径session.save_handler=""
--设定用户自定义存储函数，如果想使用PHP内置会话存储机制之外的可以使用本函数(数据库等方式)，默认files以文件存储session.auto_start
boolen --指定会话模块是否在请求开始时启动一个会话,默认为0不启动session.serialize_handler string
--定义用来序列化/

常见的php-session存放位置

  1. /var/lib/php5/sess_PHPSESSID  

  2. /var/lib/php7/sess_PHPSESSID  

  3. /var/lib/php/sess_PHPSESSID  

  4. /tmp/sess_PHPSESSID  

  5. /tmp/sessions/sess_PHPSESSED  

0x02 Session可能导致的攻击面

  * Session序列化攻击  

  * Session文件包含  

  * Session伪造用户登录  

  * Session逻辑漏洞  

## 0x03 Session序列化攻击  

Serialize_handler

要了解Session序列化攻击，先来了解一下Session机制中对序列化是如何处理的。

在php中存在三种序列化处理引擎

session.serialize_handler对应存储格式php键名 + 竖线 +
经过serialize()函数序列化处理的值php_binary键名的长度对应的ASCII字符 + 键名 +
经过serialize()函数序列化处理的值php_serialize（ php >= 5.5.4 ）经过serialize()函数序列化处理的数组

本地测试如下：

![v2-4c9ce609d47d867a053caa74cbb3154d_hd.j](https://pic1.zhimg.com/80/v2-4c9ce609d47d867a053caa74cbb3154d_hd.jpg)

Session文件内容分别对应结果为

test|s:7:"CoCo1er";<0x04>tests:7:"CoCo1er";a:1:{s:4:"test";s:7:"CoCo1er";}

攻击利用原理

payload千万条，原理第一条。

（这里补充说一点，PHP中的Session的实现是没有的问题，危害主要是由于程序员的Session使用不当而引起的。如下）

使用不同引擎来处理session文件

如果在PHP在反序列化存储的$_SESSION数据时使用的引擎和序列化使用的引擎不一样，会导致数据无法正确第反序列化。通过精心构造的数据包，就可以绕过程序的验证或者是执行一些系统的方法。例如:

在这么一种情况下：

假如我们使用php_serialize引擎时进行数据存储时的序列化，可以得到内容

$_SESSION[‘key’] = ‘Boby’;a:1:{s:3:”key”;s:4:”Boby”;}

这时我们的解析采用了另一种引擎：php

思考一下这时会发生什么情况？（php引擎中以竖线来分隔键和值）

如果像上面我们的payload换一下，传入内容以及得到的存储内容如下：

$_SESSION['key'] = '|O:4:"User":0:{}';a:1:{s:3:"key";s:16:"|O:4:"User":0:{}";}

这时候a:1:{s:3:"key";s:16:"被当作了key，

而后续的O:4:"User":0:{}";}被当作了value从而被反序列化。这里可能有人会问了，为什么会被反序列化？

看看官方文档

![v2-35e07af0bcb04a22e5a14f7a70e3cb4e_hd.j](https://pic2.zhimg.com/80/v2-35e07af0bcb04a22e5a14f7a70e3cb4e_hd.jpg)

这里可能还会有人问？那串value不符合"正常"的被反序列化的字符串规则。这个也不用担心，这里提到一个unserialize的特性，之前也做题也遇到过。在执行unserialize的时候，如果字符串前面满足了可被反序列化的规则即后续的不规则字符会被忽略。

如果不太好理解不如直接来看一个在线测试用例：

![v2-4526e134dd1b02f59866181a029a1733_hd.j](https://pic1.zhimg.com/80/v2-4526e134dd1b02f59866181a029a1733_hd.jpg)

总结一下，在php以php_serialize引擎生成session，然而又以php引擎来解析时，我们通过传入类似$_SESSION[‘name’] =
|序列化内容
这种形式的payload即有可能触发反序列化漏洞。当然这里只是提到了能够找到反序列化利用的点，至于能不能真正触发反序列化漏洞还需要结合当前环境以及一些魔术函数中是否存在可利用点。这就涉及到php反序列化漏洞的利用知识点了，这里也就不详细讲了。关于Session反序列化攻击的复杂利用方式，可以参考2018LCTF中的bestphp’s
revenge一题。

没有$_SESSION变量赋值

从上面的情况中我们可以发现我们对session的赋值可控。那如果代码中不存在对$_SESSION变量赋值的情况下如何利用呢？来看下面一个点。

php还存在一个upload_process机制，即自动在$_SESSION中创建一个键值对，值中刚好存在用户可控的部分。

写入的方式主要是利用PHP中Session Upload
Progress来进行设置，具体为，在上传文件时，如果POST一个名为PHP_SESSION_UPLOAD_PROGRESS的变量，就可以将filename的值赋值到session中。

//上传表单<form action="http://xx.xxx.xx.xx/index.php" method="POST"
enctype="multipart/form-data"> <input type="hidden"
name="PHP_SESSION_UPLOAD_PROGRESS" value="123" /> <input type="file"
name="file" /> <input type="submit" /></form>
既然filename字段能够写入session中那么就满足了session可控条件，后续的利用条件同上面所述的情景一致，两种不同引擎先后作用导致了恶意的序列化字符串被解析。

## 0x04 Session文件包含  

这个也是一个比较旧的知识点了，其实不仅是Session文件包含，仔细想想，理论上只要能够在文件中写入php代码，再被include包含进来不都可以实现getshell嘛？只不过在这里我们的可控点是Session文件，如果能向其中写入php代码，也是可以实现文件包含漏洞利用的。

作为文件包含的利用这里就不展示了，网上关于这个的基础资料早就烂大街了。

值得一提的是，往往现在的CTF出题不会仅限于文件包含这一个点来出题，而是利用诸如session+lfi的形式来入题获取源码等。而且可能加入open_basedir来限制路径，此时就需要熟悉了解session的机制，通过函数来改变save路径来利用。这个思路是在XCTF
Final中出现的bestphp一题中的考点。感兴趣的同学可以去找到环境复现一波。

## 0x05 Session伪造用户登录  

前几天正好3CTF出了一个这个考点，这里以那个题目来说明一下利用方式。（由于没有提供复现环境，此处也只能限于“纸上谈兵”，希望大家能够理解一下利用原理即可。）

**利用前提：**session可控；知道session存储格式。

这里的考题是多个攻击面的组合。题面index.php下提示要以admin登录。

  * sql盲注可以跑sqlmap拿到执行shell  

  * sql root用户存在file权限，但是往站点直接写shell无法成功（猜测应该是站点根目录有限制，但是可以猜测/tmp可写  

  * 扫后台发现test.php，访问发现回显了session的数据结构Array([username]=>test)，知道了session的格式。key为username，至于采用了哪种序列化引擎？三种都测一下就完事。  

  * 这里满足了两个利用前提。通过sqlmap-shell往/tmp写入文件伪造admin  

  * payload：select 'username|s:5:"admin";' into outfile '/tmp/sess_PHPSESSID'  

  * 最后修改成对应设计的PHPSESSID即可伪造admin登录拿到flag。  

## 0x06 Session逻辑漏洞  

很遗憾这个点也没有可以复现的环境。（官方买断...）这个是上两周unctf中出现的一道web题考点。这个逻辑漏洞处在重置密码处。过程大致如下。

密码重置分为三个步骤。

  * 填写需要重置的用户名  

  * 用户名绑定的邮箱中收到验证码  

  * 填写验证码，进入重置密码页面，填写完新密码完成重置。  

这里存在的逻辑漏洞在于第一个页面的填写用户名处，猜测后台有设置session。类似：

$_SESSION[‘name’] = $_POST['name'];

利用方式：重置admin密码。

  * 打开一个正常页面完整流程走到最后一步，填写完验证码通过后，填写新密码，此时并不提交。  

  * 新开另外一个页面完成第一步，重置用户填写admin，此时Session不再是我们之前自己的用户，而变成了admin。  

  * 这时完成之前页面的提交。成功重置admin密码。  

这里逻辑漏洞产生的原因在于对填写验证码后没有对相关用户绑定做记录，在最后一步重置密码时没有对Session的可靠性进行检查就直接执行了功能。而我们都知道Session存储在服务器端，因此我们再开一个页面即可完成对单一session文件内容的修改（保证在同一个PHPSEEID下）。

## 0x07 总结  

这里仅仅是记录了自己关于PHP的session机制相关的学习，举的都是自己最近在CTF题中接触到的点，但关于session的利用点怎么可能只有这几个？遇到了再补充学习吧。限于篇幅没有展开讲拓展利用，但是说白了，拓展利用就是多个复杂知识点的综合。我认为只有把原理性的问题搞清楚了才有可能去理解复杂的组合攻击。另外如果文中有什么理解表达错误的地方还望师傅们指正。

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

  

