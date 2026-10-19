# ctf中关于文件压缩的2个web题

阅读量 **322651**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-07-16 10:00:21

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

## [CSCCTF 2019 Final]ZlipperyStillAlive

题目下载链接

<https://github.com/sturmisch/cscctf-problem/tree/master/2019/final/web/zlippery-still-alive>

这个题网上没有找到具体细节的wp，而且关于go的web题比较少，这里记录一下，看看题目

![](https://p1.ssl.qhimg.com/t016ed321b1828fa566.jpg)

看看源码，发现有2个路由，get请求的根目录，和post请求的upload

![](https://p3.ssl.qhimg.com/t01e59971170e3658fc.jpg)

先来看看get请求/的代码吧，发现调用了getServerTime这个函数，看看这个函数，发现执行了一个叫time.sh的脚本，所以如果我们可以覆写这个文件，那就可以达到命令执行，所以可以确定目标

![](https://p0.ssl.qhimg.com/t017b55a89463d9cea6.jpg)

看看upload这个路由，发现允许上传rar和png和jpg文件，重点放在rar，如果后缀名为rar就会调用extract这个函数把rar文件解压

![](https://p0.ssl.qhimg.com/t01ec2479d73369bd86.jpg)

![](https://p3.ssl.qhimg.com/t01716a4fb914839e53.jpg)

google查询了一下相关代码，发现有个zip的slip漏洞

![](https://p1.ssl.qhimg.com/t01e53a6c41b1661ddc.jpg)

具体搜索这个漏洞，发现go也受影响，并且rar等多种压缩文件受影响，网上有现成的zip压缩的构造脚本，但是没有rar的，下一个目标就是要搞清楚rar的一些格式，但是rar的文件压缩是不开源的，但是我们可以从go代码的一些验证里面进行突破

![](https://p5.ssl.qhimg.com/t01509f57994123daab.jpg)

linux和window都不可以以/为文件名，所以先在文件里面写上读取flag的代码，然后压缩为rar文件

![](https://p1.ssl.qhimg.com/t01f1b3fe85a798d448.jpg)

用winhex打开把2改成/

![](https://p5.ssl.qhimg.com/t01fd386cd622ca4208.jpg)

上传文件后发现了报错bad header crc

![](https://p0.ssl.qhimg.com/t01aae215ad5a098e74.jpg)

参考源码发现调用了这个rardecode这个库

![](https://p3.ssl.qhimg.com/t014845ff1baec32d82.jpg)

所以继续跟踪这个库，然后搜索这个报错的字符串发现了位置

![](https://p5.ssl.qhimg.com/t014614d88d22dd6043.jpg)

在看看哪里调用了这个错误

![](https://p3.ssl.qhimg.com/t01905f8d6ae365ff85.jpg)

这里判断了crc的值，如果不等于，就报错，所以我们的目标就是绕过这个，但是具体不知道他是计算的哪里的crc值，所以我们一会写脚本爆破

![](https://p3.ssl.qhimg.com/t01ac94f9579177d031.jpg)

我们在创建一个..1..1time.sh的文件，并且压缩为rar文件，对2个文件进行对比

![](https://p5.ssl.qhimg.com/t01772d3b7f80dc355c.jpg)

发现就只有这个4个字节不同，但是我们不知道他是计算的哪些字符串的crc32的值，所以写脚本爆破

![](https://p2.ssl.qhimg.com/t01eecef0c29a93467c.jpg)

这里的16进制直接重winhex里面复制就行

![](https://p1.ssl.qhimg.com/t0186f87968b707deba.jpg)

    
    
    import binascii
    from zlib import crc32
    s='526172211A0701003392B5E50A01050600050101808000C1CCD15B2902030B900004900020E57A05988000000D2E2E312E2E3174696D652E73680A0302A5263B1FFA2BD601746163202F6574632F7370617274616E1D77565103050400'
    for x in range(len(binascii.a2b_hex(s))):
        for y in range(x+1,len(binascii.a2b_hex(s))):
            if '5b' in hex(crc32(binascii.a2b_hex(s)[x:y])) and 'c1' in hex(crc32(binascii.a2b_hex(s)[x:y])):
                print(x,y,hex(crc32(binascii.a2b_hex(s)[x:y])))
    

爆破出来发现是第27位到第69位

![](https://p5.ssl.qhimg.com/t015f2d24dfa5e4f92f.jpg)

所以取出第27到第69，然后修改内容计算crc32的值，修改成计算出来的值

![](https://p3.ssl.qhimg.com/t0126569b30ab831a84.jpg)

然后上传

![](https://p2.ssl.qhimg.com/t01ba8a5abf366f222d.jpg)

回地开始界面刷新就会执行那个覆写的time.sh的脚本

![](https://p5.ssl.qhimg.com/t01e89bcd4219d8c6bc.jpg)

## tctf2021的1linephp

题目的代码很简单，可惜这个phpinfo是个静态的phpinfo.html，不然可以尝试一下临时缓存文件的利用，所以只有通过session的文件上传包含了。题目是有zip拓展的(通过phpinfo.html可以发现)，结合之前的文件包含的学习总结，可以知道后缀名限制时可以用`zip://t.zip#t.php`和`phar://a.phar/a.php`，但是phar的文件包含的条件比较苛刻，第一个就是文件必须有后缀名，但是我们通过session构造上传的文件是没有后缀名的，所以就得想办法利用zip了

    
    
    <?php
    ($_=@$_GET['yxxx'].'.php') && @substr(file($_)[0],0,6) === '@<?php' ? include($_) : highlight_file(__FILE__) && include('phpinfo.html');
    

借用维基百科上面zip文件为单文件时的结构图，可以明显的看到前26字节基本上是一些基础信息，一般是用于校验用的

![](https://p1.ssl.qhimg.com/t01f857e12ff3924e39.png)

先看看php的文档上面正常打开zip文件的操作，先是选择了`ZipArchive::CHECKCONS`的模式进行了检查，检查通过后就用`stream_get_contents`读取了文件内容，最后进行了crc的校验

![](https://p0.ssl.qhimg.com/t01297fe7064feed5c6.png)

来看看底层ZipArchive的open方法，接受2个参数，第二个flags就是打开时启用的模式

![](https://p5.ssl.qhimg.com/t019e598deefb09a746.png)

那么`ZipArchive::CHECKCONS`其实就是`ZIP_CHECKCONS`，`ZIP_CHECKCONS`是什么就可以看看libzip里面的声明了

![](https://p5.ssl.qhimg.com/t017593fbb33ca781e9.png)

![](https://p0.ssl.qhimg.com/t01e1ee5fb8d57439d6.png)

然后看看官网的libzip的说明，也就是说如果是`ZIP_CHECKCONS`的模式打开才会进行魔数这些东西的检查，结合之前维基百科的zip单文件压缩结构图，真正对读取文件起作用的就是第26个字节后关于文件的描述

![](https://p1.ssl.qhimg.com/t0105c10120546c3e99.png)

然后我们看看php底层通过数据流打开时的代码，可以发现php通过zip的数据流打开时是没有进行验证的，就直接调用了`zip_open`函数，但是打开的方式是`ZIP_CREATE`，这个模式是不会检测文件的，然后通过`zip_fopen`打开要读取的zip文件

`php_stream_zip_opener`

![](https://p2.ssl.qhimg.com/t01ecc52b9c7291a588.png)

然后看看libzip的源码的`zip_open`怎么写的吧，`zip_open_from_source`函数就是针对我们传入的模式进行创建数据流

![](https://p4.ssl.qhimg.com/t013ee67c214eea5e73.png)

直接看看函数调用链到关键地方吧

![](https://p4.ssl.qhimg.com/t0117eeb0333ffa3207.png)

![](https://p5.ssl.qhimg.com/t0134dd3bbf29dac96c.png)

<a name=”这里是对魔数进行了检测匹配的，但是匹配的是`504b0506`，而没有匹配的文件头” class=”reference-link”>这里是对魔数进行了检测匹配的，但是匹配的是`504b0506`，而没有匹配的文件头

![](https://p2.ssl.qhimg.com/t01570d1fe63a888746.png)

但是如果是`ZIP_CHECKCONS`模式就会进入`_zip_checkcons`，这个函数就是zip的格式检查函数，所以可以通过`ZIP_CREATE`的模式打开的就不会进入`_zip_checkcons`

![](https://p4.ssl.qhimg.com/t01416ac17e9d2bacec.png)

可以看看他检查的主要内容

![](https://p0.ssl.qhimg.com/t017f0844bdcf648f59.png)

![](https://p2.ssl.qhimg.com/t01a80a851ee9e67349.png)

所以我们目标就很明确了，只要读取文件的关键位置偏移不变，那么就可以成功读取文件，所以只需要删除构造的zip的单文件的前16字节，在配合zip协议进行包含就行

![](https://p3.ssl.qhimg.com/t01c4fcbf534d693ef0.png)

![](https://p3.ssl.qhimg.com/t01f5e0b3d120d34756.png)

然后通过bp进行条件竞争，包含session的临时文件后写入一句话，得到flag

![](https://p2.ssl.qhimg.com/t01e10cfebd94698b3d.png)

![](https://p4.ssl.qhimg.com/t017a77d9a277a40086.png)

![](https://p3.ssl.qhimg.com/t01ab7e344508331b80.png)

![](https://p5.ssl.qhimg.com/t013fdcab3bf14ce53e.png)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **123qwer** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/246722](/post/id/246722)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __2赞

 __收藏

![](https://thirdqq.qlogo.cn/g?b=oidb&k=PCGUeYx0xXvaXeCPiceiauNA&s=40&t=1557114336)
123qwer

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

