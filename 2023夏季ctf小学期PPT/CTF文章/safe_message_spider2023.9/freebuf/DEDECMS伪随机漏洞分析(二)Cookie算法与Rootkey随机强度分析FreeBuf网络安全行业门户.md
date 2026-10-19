**本篇为[《DEDECMS伪随机漏洞分析 (一)
：PHP下随机函数的研究》](https://www.freebuf.com/vuls/234563.html)**
**的续篇，研究DEDECMS的cookie生成的算法, 以及rootkey生成的算法, 确认rootkey使用的随机算法的强度, 计算攻击耗时。**  

## **一、Cookie算法** ****

###  ** **1.COOKIE的作用和常见的构造形式****

作用: 权限鉴别、无会话状态。

构成:

常常是以下形式 cookie = F(x,y), F为不可逆函数, x为盐 , y为和权限/用户相关的数据

我们可以知道的部分, F-> 一般常常为hash函数md5,sha256等

y-> 比如用户名称/id编号/权限简称

我们无法知道的部分, x

###  ** **2.定位算法-动态调试****

根据常识, 在登陆后, server端会返回cookie!

2.1在web站点上进行登陆,并抓包, 看到路径/member/index_do.php

2.2分析index_do.php (dedecms路由很简单, 路径直接对应到了文件),在登陆接口处下断点

![图片2.png](https://image.3001.net/images/20200511/1589187648_5eb914409bcc6.png!small)2.3大致浏览整个函数,
并没有发现设置cookie的操作(php原型函数-setcookie),但是发现了检查账号的函数, 跟入进去:

![图片3.png](https://image.3001.net/images/20200511/1589187731_5eb91493e1782.png!small)![图片4.png](https://image.3001.net/images/20200511/1589187732_5eb9149406595.png!small)
![图片5.png](https://image.3001.net/images/20200511/1589187732_5eb914940b2ff.png!small)![图片6.png](https://image.3001.net/images/20200511/1589187732_5eb914943657f.png!small)2.4关键字段

有的时候, 查看服务端响应或是通过js生成的cookie字段很多, 但调用接口时, 可能校验的是cookie里面的几个字段,
因此我们找到关键的被用来鉴权的字段, 可以减少我们测试时的干扰.

针对2.1图片的cookie通过递减字段测试, 其实可以发现dedecms校验cookie的关键字段为:

    
    
    DedeUserID=7; DedeUserID_ckMd5=4d0db47b3ba3fef5;
    
    DedeUserID=用户ID; DedeUserIDckMd5 = substr(md5($cfgcookie_encode.用户ID),0,16)

其中DedeUserID是很容易知道的, 或者有规律的, 1,2,3,4这样子,
那么其实要伪造cookie的关键是需要知道$cfgcookieencode(本文称之为rootkey)

##  **二、 Root Key生成算法** ****

###  **1\. 代码定位** ****

$cfgcookieencode是固定的? 还是在内存内动态生成的?

1.1
全文查找以下cfgcookieencode,发现在config.cache.inc.php存储有:![图片7.png](https://image.3001.net/images/20200511/1589187816_5eb914e86422a.png!small)这个值和我们在上面断点看到的值一样,大概率可以判断,应该属于一个固定值.

1.2 全局找一下有哪些地方操作了config.cache.inc.php,看是哪个函数写入了这个值

这儿定位偏了, 这儿是更新服务器的时候会刷新一次root key~

![图片8.png](https://image.3001.net/images/20200511/1589187849_5eb91509347dd.png!small)1.3
继续定位到install.php

$cfgcookieencode除了在config.cache.inc.php,也记录在config.cache.bak.php,
那么看下哪里操作了config.cache.bak.php:

![图片9.png](https://image.3001.net/images/20200511/1589187873_5eb91521247f5.png!small)在上下文找到了同样的root
key生成算法:

这儿是真正第一次生成root key的地方

![图片10.png](https://image.3001.net/images/20200511/1589187899_5eb9153b70576.png!small)在安装界面的时候其实会显示出来给我们:

![图片11.png](https://image.3001.net/images/20200511/1589187920_5eb915506302c.png!small)1.4
根据1.2, 1.3可知Root Key算法如下:

    
    
    $chars='abcdefghigklmnopqrstuvwxwyABCDEFGHIGKLMNOPQRSTUVWXWY0123456789';      
    $max = strlen($chars) - 1;      
          
    $length = rand(28,32);      
    $root_key='';      
    for($i = 0; $i < $length; $i++) {      
        $root_key .= $chars[mt_rand(0, $max)];      
    }

###  **2\. 强度分析** ****

2.1 套用结论

基于第一篇的下面三个结论:

> 4.1 影响随机数生成的因素为两个: 1. 种子 2. 次数
>
> 4.4 种子区间为0到0xffffffff
>
> 4.6 同一进程下,先后被调用的rand和mt_rand, 在未播种的前提下, 会使用同一个随机种子

可知, root_key的可能性为 (0xffffffff-0)+1 = 2^32种可能.

揣测一下作者认为的强度为:

62^28 + 62^29 + 62^30 + 62^31 + 62^32

2.2 遍历全部rootkey耗时

这儿md5和substr计算是静态的字符串, 实际的字符串是变化的, 消耗的时间应该在计算出来的时间的周围浮动

    
    
    <?php      
    $start = microtime(true);      
    for ($i = 0; $i < 10000000; ++$i) {      
        ;      
    }      
    $total_1 = microtime(true) - $start;      
          
    $start = microtime(true);      
    for ($i = 0; $i < 10000000; ++$i) {      
        md5("111111111111111111111111111111");      
    }      
    $total_2 = microtime(true) - $start;      
          
    $start = microtime(true);      
    for ($i = 0; $i < 10000000; ++$i) {      
        substr(md5("111111111111111111111111111111"),0,16);      
    }      
    $total_3 = microtime(true) - $start;      
          
    $start = microtime(true);      
    $chars='abcdefghigklmnopqrstuvwxwyABCDEFGHIGKLMNOPQRSTUVWXWY0123456789';      
    $max = strlen($chars) - 1;      
    for ($i = 0; $i < 1000000; ++$i) {      
        $hash='';      
        $length = rand(28,32);      
        for($y = 0; $y < $length; $y++) {      
         $hash .= $chars[mt_rand(0, $max)];      
        }      
    }      
    $total_4 = microtime(true) - $start;      
          
    echo ($total_2 - $total_1);      
    echo "\n";      
    echo ($total_3 - $total_1);      
    echo "\n";      
    echo ($total_4 - $total_1);      
    echo "\n";      
    ?>

结果:

3.9920189380646 //10^7次md5() 用时

7.0076858997345 //10^7次substr(md5()) 用时

8.376072883606 // 10^6次生成key 用时

那么单进程遍历root key的时间需要:

((8.376072883606/10^6) * (2^32)) / 3600 ≈ 10 hour

 ** ***本文作者：** 光通天下无患实验室 Djerryz，转载请注明来自FreeBuf.COM**  

