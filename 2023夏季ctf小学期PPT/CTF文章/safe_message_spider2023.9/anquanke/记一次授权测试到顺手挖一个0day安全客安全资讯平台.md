# 记一次授权测试到顺手挖一个0day

阅读量 **257123**

|评论 **1**

发布时间 : 2020-11-18 16:30:34

 **x**

##### 译文声明

本文是翻译文章，文章原作者 酒仙桥6号部队，文章来源：酒仙桥6号部队

原文地址：[https://mp.weixin.qq.com/s?src=11&timestamp=1605686610&ver=2713&signature=KOCiwYS-y3PpUcPBeXDeqxG2C0*mTLSdVU9*7p22c6kt4FNevligUt7LywggXCPVCPRnefJGKaaRIIBDU7CyAN4wa8AI62xTuQUhsnZJCaNcthuEMiVGYzjQhlXt0KxC&new=1](https://mp.weixin.qq.com/s?src=11&timestamp=1605686610&ver=2713&signature=KOCiwYS-y3PpUcPBeXDeqxG2C0*mTLSdVU9*7p22c6kt4FNevligUt7LywggXCPVCPRnefJGKaaRIIBDU7CyAN4wa8AI62xTuQUhsnZJCaNcthuEMiVGYzjQhlXt0KxC&new=1)

译文仅供参考，具体内容表达以及含义原文为准。

记在一次授权的渗透测试过程中遇到了这样一个项目，开始对前台一顿fuzz，端口一顿扫描也并没有发现什么可利用的漏洞，哪怕挖一个xss也行啊，但是xss也并没有挖掘到，实在不行挖一个信息泄露也好啊，果然让我挖掘到了一个信息泄露，get到了程序的指纹。

![](https://p0.ssl.qhimg.com/t0107b87c28e1a45bf2.png)

Pbootcms是一套开源网站系统，然后百度了下该程序所爆出来的漏洞进行了测试，发现都失败了，猜测应该是程序升级到了较新版本，造成了网上爆出来的漏洞都被修复了。既然没有捷径可走，那还是只有老老实实去官网下载一份源码回来审计测试。

## 源码审计

### 1.数据获取

通过对程序源代码的审查发现该程序封装了自己的数据获取助手函数：get(),post(),request()等，获取流程如下:
用post()函数举例说明：post(‘name’,’vars’)。

![](https://p3.ssl.qhimg.com/t011b939cca7b8e9345.png)

可以看到将我们的传入的数据再次传入到了filter函数中：

![](https://p2.ssl.qhimg.com/t015dbef0fdc6fdc39f.png)

在filter函数中，会对获取到的数据进行一系列的强过滤，例如我们这里的 vars，就只能传递中文，字母，数字，点，逗号，空格这些字符。（PS:
因为不能传递括号“(,)”，所以sql注入中的函数都没办法使用，也就导致了什么报错注入，盲注啥的都不能使用，只有联合查询这种可以使用）接着函数在最后还经过了处理。

![](https://p1.ssl.qhimg.com/t012f3992f55b72e2ae.png)

跟进escape_string函数：

![](https://p0.ssl.qhimg.com/t014cd53f03e37df4e4.png)

对数据还进行了htmlspecialchars，addslashes 双处理。

数据获取流程图所示：

![](https://p0.ssl.qhimg.com/t0147f5f63336e5c2e0.png)

现在我们对该程序的数据获取已经有了初步的了解，主要的数据获取都是通过post(),get(),request()三大助手函数来实现的。

### 2.注入挖掘

在审计的过程中发现程序存在较多的如下所示的代码：

![](https://p1.ssl.qhimg.com/t017add59d169a04626.png)

这里我将目光放在了DB类库中封装的where方法上，代码如下：

![](https://p3.ssl.qhimg.com/t01e862548ea825c1ba.png)

如果此处传入的$where变量是一个索引数组，那么就会进入红框代码这里，并对值进行拼接。

明确目标之后，我们就可以开始搜索目标了：

![](https://p3.ssl.qhimg.com/t01175203f61d54f215.png)

![](https://p5.ssl.qhimg.com/t01a342eee088d1782e.png)

一番搜索下来发现，要不数据不可控，要不数据会通过escape_string函数，并有单引号保护，达到过滤效果。

![](https://p4.ssl.qhimg.com/t016729130da837829d.png)

### 3.峰回路转

通过多次对where，select，update等关键字的搜索，但是并没有获取到什么突破性的进展，然后又尝试了对$GET,$POST等原生态数据的搜索：

![](https://p0.ssl.qhimg.com/t01e236805bfba390d0.png)

在appshomecontrollerParserController.php文件中的parserSearchLabel方法中发现了问题：由于该方法代码较长，所以仅截图了关键部分。

![](https://p0.ssl.qhimg.com/t011fd4b3651304a5ea.png)

可以看到首先遍历了$_POST数组，然后将键当做了$where数组的键。（这是关键），不过这里我们需要验证一下，键值为1，这个1是整型，还是字符串型，因为我们要控制输入的是索引数组。

![](https://p3.ssl.qhimg.com/t016bc4a8afc5eea37b.png)

是int类型，完全符合我们上面的需求。

到这里也就是说这个$where3数组的键，值我们都可以控制了，不过$key：只能是/^[w-.]+$/这些内容。$value:
只能是/^[x{4e00}-x{9fa5}w-.,s]+$/u 这些内容。

接着继续往下看代码：

![](https://p4.ssl.qhimg.com/t01c22e59bf7056b280.png)

这里的$page为true，因为默认值是true，并且在中途的重新赋值过程中，我们没办法控制它，所以这里必定会执行getLists方法。

Getlists方法代码如下：代码较长，只截图了关键部分。

![](https://p1.ssl.qhimg.com/t016a48c221f3e8c68e.png)

成功的将我们传递的$where3数组传递到了where方法里面。

接着执行了一个page方法：

![](https://p2.ssl.qhimg.com/t01d028cdd24146062f.png)

这里设置了一个sql属性，后面会用到。

然后执行了最终的select方法。

![](https://p4.ssl.qhimg.com/t0178a1561a62eef8e0.png)

其中的buildsql方法就是结合我们之前设置的属性值来进行拼接成完整的sql语句。

![](https://p3.ssl.qhimg.com/t01b6c7f9b7eca30f4d.png)

这里直接将我们前面通过链式操作where,order,page等方法设置的属性进行了替换拼接，又因为我们前面分析的在where方法中，如果传递进去的是一个索引数组的话，是没有单引号保护的，所以看到这里就差不多明白了我们成功逃逸了单引号的保护。

总体流程图如下所示：

![](https://p0.ssl.qhimg.com/t01adca0473f777ac63.png)

整个流程几乎已经走完了，测试效果如下：

![](https://p4.ssl.qhimg.com/t0134b37c774acd4660.png)

可以看到我们输入的aaaaaa已经成功带入到了sql语句中去执行，需要注意的是 我们输入内容是在小括号()里面的。

结合上面的request助手函数的过滤，我们知道输入的数据只能是指定字符：

![](https://p4.ssl.qhimg.com/t015947861890f3c39e.png)

常规的报错注入是不能成功的，如：

![](https://p4.ssl.qhimg.com/t010348a9585636baa5.png)

页面并没有像上面一样报错，而是返回了正常的页面，因为检测到了小括号，直接将我们的数据置为空值了。

### 4.绕过注入

因为我们可控的点在where后面，where后面是可以接子查询的，如图：

![](https://p0.ssl.qhimg.com/t0194331ad4a955f4ba.png)

![](https://p5.ssl.qhimg.com/t013b1049a54c18e36c.png)

所以我们的绕过思路就是通过子查询的方式来进行操作，因为子查询是可以不使用括号的，如：

![](https://p3.ssl.qhimg.com/t0123771f8c3204c026.png)

我们的注入payload并没有被过滤，成功带入到了sql语句中去，但是因为不能使用括号，所以类似substring,
mid等截断函数都不能使用，而且还不能使用=,<,>等一些比较符，怎么获取到准确数据又成了一个问题？

这里的突破目标就放在了对sql语句的变形上，首先就需要了解下sql的执行顺序。

![](https://p2.ssl.qhimg.com/t012e6498610ee3daed.png)

可以看到where的执行是在select之前的，那这怎么利用呢？如下：

![](https://p4.ssl.qhimg.com/t01fdeab10c2794f499.png)

可以看到即使是select一个常量，如果后面的where条件不成立，也是不会查询到数据的，我们就可以利用where比select来对比出数据。

因为不能使用=,<,>等比较符，所以我们就需要找一个东西来代替它，并且因为不能使用substr等截取函数，所以就没办法一个一个的对比数据，就必须要找到一个可以让我们一个一个来对比的方式。

找到利用regexp来完美代替，因为regexp后面能接正则表达式，并且.能代表任意字符，*代表任意个数，那不就刚好符合我们的要求么，利用方式如下：

![](https://p3.ssl.qhimg.com/t01c867d2833651ca88.png)

将我们需要查询的字段放在where处，通过where返回的内容来控制select出来的数据。

（注意请使用^限定开头。如：^ad.*）

因为数据不能使用引号，所以我们需要将引号内的数据进行16进制编码，效果是一样的。

控制了select返回的内容，达成的效果如下：

![](https://p5.ssl.qhimg.com/t0193debbaff0a4f54f.png)

Sql语句中，子查询先执行，并且在整个父类SELECT语句中我们子查询的结果处于where语句中，并且使用了AND连接，也就是说我们子查询的结果，同时也控制着整个sql语句的结果，那么就可以用来准确的判断数据了。

### 5.本地测试payload

正确的页面显示：

![](https://p3.ssl.qhimg.com/t01fb4b361df0bb625f.png)

错误的页面显示：

![](https://p1.ssl.qhimg.com/t018d46828c5648e2c8.png)

我们的真实数据：

![](https://p1.ssl.qhimg.com/t01b658d7764eaeb94c.png)

将我们的正则payload经过16进制编码然后带入执行，通过页面返回内容就可以判断我们的数据是多少了，最终达到了绕过过滤进行出数据的目的。

最终总体流程图可分三步，如图所示：

![](https://p0.ssl.qhimg.com/t0198dff8488d91b2b7.png)

![](https://p4.ssl.qhimg.com/t01efe6ff246eeb32d3.png)

![](https://p4.ssl.qhimg.com/t01a5d2e2f8923af1d9.png)

测试结果证明我们的注入漏洞成功利用，接下来就是将payload映射到项目网站上去，经过大量的fuzz后成功得到管理员账号密码：

![](https://p4.ssl.qhimg.com/t010886c4938ec7d4aa.png)

## 后台Getshell

漏洞文件：corefunctionfile.php

![](https://p4.ssl.qhimg.com/t018bb3c5c30d18746f.png)

后缀白名单来自于handle_upload函数的第三个参数，寻找调用handle_upload函数的地方。

![](https://p5.ssl.qhimg.com/t01800e22c9ad030896.png)

后缀白名单来自于upload函数的第二个参数，搜索upload函数的调用处。

触发文件：appshomecontrollerMemberController.php

![](https://p3.ssl.qhimg.com/t012e4837f95327aed4.png)

继续跟进config方法。

![](https://p2.ssl.qhimg.com/t01d9c1c59f5ebb7eba.png)

Config方法就是返回对应的配置项，配置项内容通过self::loadconfig()加载。

![](https://p3.ssl.qhimg.com/t0130c941044353c733.png)

配置项的一部分来至于md5(config).php文件，只要我们控制了这个文件中的home_upload_ext选项，也就控制了允许上传的后缀白名单了。

修改配置文件的地方。

文件：appsadmincontrollersystemConfigController.php

![](https://p2.ssl.qhimg.com/t0106fa823aaede88e9.png)

将$_POST遍历出来的键传递进了$this->moddbconfig方法。

![](https://p4.ssl.qhimg.com/t018d1968d588d877b8.png)

![](https://p0.ssl.qhimg.com/t015a1d82b3d3e9529c.png)

程序会首先将我们修改的配置内容更新到ay_config数据表中去，然后再将数据表中的内容写入到md5(config).php文件中，造成我们可以添加任何类型的后缀文件。

### Getshell利用

登录后台->全局配置->配置参数->立刻提交，使用burp抓包。

在POST数据中添加一个：home_upload_ext=php 字段即可。

![](https://p4.ssl.qhimg.com/t01a22fd0c7642e5142.png)

成功将其写入到文件。

![](https://p0.ssl.qhimg.com/t0129664ffae401ca2e.png)

设置好了允许的上传白名单后，我们就可以通过上传php达到getshell了。

上传文件exp：upload.html

    
    
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">    
        <title>pbootcms文件上传</title>
    </head>
    <body>
    <form action="http://xxxxx/?member/upload" method="post" enctype="multipart/form-data">
        <input type="file" name="upload">    
        <input type="submit" name="mufile">
    </form>
    </body>
    </html>

将exp保存到html文件，修改对应的域名直接上传即可，文件上传证明。

![](https://p3.ssl.qhimg.com/t010c616758599638b7.png)

在本地将流程成功走了一遍后，利用到项目网站上也很顺利，直接就getshell了，成功交差，又可以愉快的喝冰阔乐了。

## 总结

整个流程从网站获取到指纹，然后找到源码审计，在审计过程中还是花费了较多时间，主要在前台审计的入口点寻找，和绕过过滤注入出数据，当时一度认为没办法利用，还好当时没放弃，然后慢慢一步一步的啃，终于还是啃下来了。

本文翻译自酒仙桥6号部队
[原文链接](https://mp.weixin.qq.com/s?src=11&timestamp=1605686610&ver=2713&signature=KOCiwYS-y3PpUcPBeXDeqxG2C0*mTLSdVU9*7p22c6kt4FNevligUt7LywggXCPVCPRnefJGKaaRIIBDU7CyAN4wa8AI62xTuQUhsnZJCaNcthuEMiVGYzjQhlXt0KxC&new=1)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **酒仙桥六号部队** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/222849](/post/id/222849)

安全客 - 有思想的安全新媒体

本文转载自:
[酒仙桥6号部队](https://mp.weixin.qq.com/s?src=11&timestamp=1605686610&ver=2713&signature=KOCiwYS-y3PpUcPBeXDeqxG2C0*mTLSdVU9*7p22c6kt4FNevligUt7LywggXCPVCPRnefJGKaaRIIBDU7CyAN4wa8AI62xTuQUhsnZJCaNcthuEMiVGYzjQhlXt0KxC&new=1)

如若转载,请注明出处：
[https://mp.weixin.qq.com/s?src=11&timestamp=1605686610&ver=2713&signature=KOCiwYS-y3PpUcPBeXDeqxG2C0*mTLSdVU9*7p22c6kt4FNevligUt7LywggXCPVCPRnefJGKaaRIIBDU7CyAN4wa8AI62xTuQUhsnZJCaNcthuEMiVGYzjQhlXt0KxC&new=1](https://mp.weixin.qq.com/s?src=11&timestamp=1605686610&ver=2713&signature=KOCiwYS-y3PpUcPBeXDeqxG2C0*mTLSdVU9*7p22c6kt4FNevligUt7LywggXCPVCPRnefJGKaaRIIBDU7CyAN4wa8AI62xTuQUhsnZJCaNcthuEMiVGYzjQhlXt0KxC&new=1)

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [渗透测试](/tag/渗透测试)

 **+1** __18赞

 __收藏

![](https://p3.ssl.qhimg.com/t0110bc5d794d277012.png) 酒仙桥六号部队

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

