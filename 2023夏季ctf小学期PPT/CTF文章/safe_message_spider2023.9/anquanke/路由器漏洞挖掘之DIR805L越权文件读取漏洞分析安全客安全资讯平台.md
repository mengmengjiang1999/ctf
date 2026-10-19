# 路由器漏洞挖掘之 DIR-805L 越权文件读取漏洞分析

阅读量 **339099**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-04-01 14:30:06

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/dm/1024_501_/t01017cb10a6f512436.jpg)

接下来的文章都会实战复现一些关于路由器的 web /二进制漏洞，可能会写的比较细，希望能给大家带来启发。

## 前言

本文在复现 DIR-805L 任意文件读取漏洞时，将会比较详细的分析一下用于 cgi 处理的 `phpcgi_main` 函数其中的一些功能。在逆向
`cgibin` 二进制文件时，常常会遇到一些用于解析 http
请求的函数，在分析时经常对这些函数的用法不太清楚。总是云里雾里的，所以这里对这些函数做一个比较细致的总结，希望对同样在学这块的朋友们一点启发吧，也算是达到抛砖引玉的目的吧。

  * 笔者能力有限，写不出高水平的文章，只能把基础的要点写详细一些，目的为了供一些和我一样的新手入门学习，文中若有解释错误恳请师傅们指出。

## 前提准备

去 dlink 的官网下载固件：

    
    
    ftp://ftp2.dlink.com/PRODUCTS/DIR-850L/REVA/DIR-850L_REVA_FIRMWARE_1.14.B07_WW.ZIP
    

使用 firmadyne 来模拟固件：

    
    
    ./sources/extractor/extractor.py -b DIR-850L -sql 127.0.0.1 -np -nk "DIR-850L_REVA_FIRMWARE_1.14.B07_WW.ZIP" images
    
    ./scripts/getArch.sh ./images/8.tar.gz
    
    ./scripts/tar2db.py -i 8 -f ./images/8.tar.gz
    
    sudo ./scripts/makeImage.sh 8
    
    ./scripts/inferNetwork.sh 8
    
    ./scratch/8/run.sh
    

  * 这里我使用远程的 vps 来搭建 firmadyne 的环境，路由器的 IP 是 `192.168.0.1`

![](https://p1.ssl.qhimg.com/t011cb2fdfcb0d3c438.png)

运行固件之后在本地连上远程的 ssh 隧道，代理到本地的 9000 端口：

    
    
    ssh ubuntu@xx.xx.xx.xx -D 9000
    

sockets 代理 `127.0.0.1:9000` ，这里我们就能在本地访问到 vps 上模拟的固件

访问 `192.168.0.1` 即可访问到路由器的登录界面。

![](https://p2.ssl.qhimg.com/t016e3d8adce1304332.png)

  * 如果用 Burp 访问的话，在 User options 中开启 socks proxy 选项就行了。

![](https://p3.ssl.qhimg.com/t01e3bb31ce01877a42.png)

## 越权文件读取

先给相应的 `payload`：

    
    
    post_uri: http://192.168.0.1/getcfg.php
    data: SERVICES=DEVICE.ACCOUNT&attack=ture%0aAUTHORIZED_GROUP=1
    

###  漏洞分析

####  getcfg.php 源代码分析

在 `/htdocs/web/getcfg.php` 文件中，有一处文件读取的操作，通过读取 POST 传入的参数 `SERVICES` 的值，最后拼接到
`$file` 变量中，调用 `dophp("load", $file)` 函数进行文件读取。

![](https://p1.ssl.qhimg.com/t01b30dcb9146aa1a2d.png)

显然这里的 `SERVICES` 变量的值可控，为了达到读取文件的目的， **这里还需要绕过前面的一个 if 判断**

    
    
        if(is_power_user() == 1)
    
        ......
    
        function is_power_user(){
            if($_GLOBALS["AUTHORIZED_GROUP"] == "")
            {
                    return 0;
            }
            if($_GLOBALS["AUTHORIZED_GROUP"] < 0)
            {
                    return 0;
            }
            return 1;
    }
    

这个函数在前面就定义了，通过全局变量 `AUTHORIZED_GROUP` 来判断返回值。这里需要满足 `AUTHORIZED_GROUP` 的值大于 0
才表示认证成功。那么这里全局变量 `AUTHORIZED_GROUP` 值是从哪里获取的呢？这里我们就需要在 `cgibin` 这个二进制文件中找到答案。

####  cgibin 的静态分析

首先要明确 `cgibin` 这个文件是起到解析处理脚本语言的作用，当前 webserver 运行的是 php 脚本，那么 **这个二进制文件中重点就是处理
php 语言的部分** ，也就是 `phpcgi`。

> CGI的英文是（COMMON GATEWAY INTERFACE）公共网关接口，它的作用就是帮助服务器与语言通信。

所以在 IDA 中我们需要找到处理 `phpcgi` 的相关函数。在 0x00406528 处找到这个函数

![](https://p5.ssl.qhimg.com/t01c58b0f15786e062d.png)

下面开始详细分析这个函数其中的一些细节。

首先，第一步函数调用了 `sobj_new、sobj_add_string、sobj_add_char` 函数来初始化字符串，为后面对解析 POST
变量的处理做一个准备。

  * sobj_new 函数开辟一个堆内存，并维护一个数组

![](https://p3.ssl.qhimg.com/t013ca58679f33626ec.png)

    
    
    int *malloc_addr = malloc(0x18)
    
    heap + 0 = malloc_addr
    heap + 4 = malloc_addr
    heap + 8 = 0
    heap + C = 0
    heap + 10 = 0
    heap + 14 = 0
    

接下来通过 `getenv` 函数来获取请求的方法和请求的 uri。

![](https://p1.ssl.qhimg.com/t01db252a3fde687bec.png)

这里是 POST 请求，所以会走到 `0x40668C` 这个分支

![](https://p2.ssl.qhimg.com/t01398a7701dd7f08fa.png)

  * 在 cgi 的处理中， `getenv` 是个很重要的函数，这个函数用来获取客户端通过 http 请求的一些请求参数，例如 uri、content-length、请求方法等。 
    
        char *getenv(const char *name)
    

当前函数返回值为指向查找的 `name` 的值的指针。

> getenv 函数的返回值存储在一个全局二维数组里，当你再次使用 getenv 函数时不用担心会覆盖上次的调用结果。

![](https://p2.ssl.qhimg.com/t01dea050342c15b0ef.png)

接着调用 `cgibin_parse_request` 这个函数，函数主要功能是进一步处理 http 请求。

    
    
    cgibin_parse_request(sub_406220,malloc_addr,8)
    

这个函数的第一个参数 sub_406220 函数意思是拼接 POST 请求的参数名和参数值。

![](https://p5.ssl.qhimg.com/t01e6bdfc97e55acb14.png)

接着 `cgibin_parse_request` 函数里调用 `parse_uri` 完后，将返回值存储到 &(heap + 8) 处

往下就跳转到了 `loc_406760` 这个分支，`sobj_get_string` 函数从堆空间中获取前一步拼接的参数名和参数值，主要是判断 POST
请求中是否存在 `AUTHORIZED_GROUP` 这个参数

![](https://p3.ssl.qhimg.com/t0179eff5863730aa1f.png)

继续往下，这里的开头先判断访问的绝对路径中是否包含 `htdocs/mydlink` 路径，再经过 `strcasecmp` 函数的比较之后，跳转到
`sess_validate` 函数来执行

![](https://p5.ssl.qhimg.com/t014f7ba94dfaa98d63.png)

在这里，`sess_validate` 函数作用是验证解析 `AUTHORIZED_GROUP` 这个参数的值，并通过 `sprintf` 函数后
**作为全局变量的形式格式化到栈上** 。即：

    
    
    sprintf($sp+0xB0-0x90,"AUTHORIZED_GROUP=%d",sess_validate())
    

![](https://p3.ssl.qhimg.com/t01607ff900ad8b560a.png)

之后再调用 `sobj_add_string` 和 `sobj_add_char` 函数来进行字符串的拼接。

![](https://p5.ssl.qhimg.com/t010d58c15f62df9cd0.png)

`sobj_add_string` 函数将 `sprintf` 格式化到栈上的数据作为指针，存储到 `sobj_new` 开辟的堆空间里。

    
    
    sobj_add_string(&heap,$sp+0xB0-0x90)
    

这里需要在 POST 数据包中加上 `%0a` 的原因是在调用 `sobj_add_char` 函数时，会用 n 来分隔参数

    
    
    sobj_add_char(heap,0x10)
    

因此这里的 `payload` 为：

    
    
    SERVICES=DEVICE.ACCOUNT&attack=%0aAUTHORIZED_GROUP=1
    

所以只要将 `%0aAUTHORIZED_GROUP=1` 伪造作为任意一个参数名的参数值就行了。

因此在 `cgibin` 处理完 `AUTHORIZED_GROUP` 参数后，就将他作为全局变量存储在 php 当中。这样就绕过了
`is_power_user` 函数的判断，执行下面的任意文件读取操作。

####  动态分析

这里直接使用 POST 方法提交上面的 payload 来进行调试，观察一下参数的变化。

###  另一处任意文件读取

这里其实还有一处的任意文件读取，漏洞位于 `htdocs/webinc/fatlady.php` 中，代码如下：

![](https://p4.ssl.qhimg.com/t01f6492dc625f44eb1.png)

`$service` 参数未经过滤就直接拼接到 `$target` 变量中，导致这里可以通过 **目录穿越** 读取到其他目录下的 .php
后缀的文件，例如存放 admin 用户信息的 DEVICE.ACCOUNT.xml.php 文件。

    
    
    <?xml version "1.0" encoding "utf-8"><postxml><module><service>../../../htdocs/webinc/getcfg/DEVICE.ACCOUNT.xml</service></module></postxml>
    

![](https://p2.ssl.qhimg.com/t01912d8a2ccb4fb8b2.png)

这里只要满足 POST 数据包中 xml 形式的 `postxml` 即可，`$service` 变量即可控，同样可以达到任意文件读取的效果。

  * 注意这里请求头的 `Content-Type` 的值要为 `text/xml`

###  任意文件读取漏洞的复现

这里复现一下第一种任意文件读取的效果，我们的目的是读取在 `/htdocs/webinc/getcfg` 目录下的
`DEVICE.ACCOUNT.xml.php` 文件。

![](https://p5.ssl.qhimg.com/t01c0b4f57ea58c976f.png)

`SERVICES` 的值可控，那么这里就可以传入 `SERVICES` 的值为 `/htdocs/webinc/getcfg` 文件夹下后缀为
`.xml.php` 的文件名，达到未授权读取配置文件的目的。

使用 Burp 构造数据包发送即可看到漏洞效果。

![](https://p4.ssl.qhimg.com/t01ff9a344561747b45.png)

  * 这里的 `Content-Type` 需要为 `application/x-www-form-urlencoded`，发送的 POST 数据才能正常被服务器解析。

## 总结

DIR-850L 任意文件读取复漏洞现重点还是要仔细分析 `phpcgi_main` 这个函数的在处理 http 请求时的相关逻辑。

这里在读取到 `DEVICE.ACCOUNT` 配置文件，得到 admin 的密码之后，可以进一步利用一处命令执行来
getshell，具体的后面的文章中会有具体的分析。

## 参考文章

<https://xz.aliyun.com/t/90>  
<https://xz.aliyun.com/t/2941>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **H4lo** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/175625](/post/id/175625)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [物联网](/tag/物联网)
  * [IoT](/tag/IoT)
  * [路由器](/tag/路由器)

 **+1** __4赞

 __收藏

![](https://p2.ssl.qhimg.com/t0129eee7c67478558f.jpg) H4lo

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

