## 前言

Thinkphp最近报出了一个rce漏洞。当ThinkPHP开启了多语言功能时，攻击者可通过lang参数和目录穿越实现文件包含，当存在其他扩展模块如pear扩展时，可进一步利用文件包含实现远程代码执行

## 影响版本

ThinkPHP 5.0 - 5.1.41、6.0 - 6.0.13

## 利用条件

thinkphp开启多语言模块

漏洞本质是一个文件包含漏洞，如果要rce需要结合其它的扩展

## 漏洞分析

thinkphp框架运行时会首先加载thinkphp/library/think/App.php文件进行一系列的初始化操作。在run函数中可以看到当开启了多语言机制，会运行Lang::detect()函数。

![](https://image.3001.net/images/20221226/1672020781_63a9032d78fcfd6870a76.png!small)

跟进Lang::detect()函数，可以看到会依次从url，cookie，自动侦测浏览器中获取设置的语言，然后返回结果

![](https://image.3001.net/images/20221226/1672020812_63a9034c7500321086604.png!small)

在App.php中获取语言结果以后加载系统语言包，即执行Lang::load函数

![](https://image.3001.net/images/20221226/1672020843_63a9036b4a523947b8437.png!small)

跟进Lang:load()函数，可以看到将传进来的路径赋值给了$file，并且未在过滤的情况下直接使用include函数进行包含。最终导致了该漏洞。

![](https://image.3001.net/images/20221226/1672020878_63a9038ed76826e4e3cb1.png!small)

## 漏洞复现

1.使用thinkphp版本V5.0.5搭建php环境

![](https://image.3001.net/images/20221226/1672020914_63a903b2bb2b6d39d8fe2.png!small)

2.开启多语言模块

在application/config.php中将lang_switch_on设置为true

![](https://image.3001.net/images/20221226/1672021070_63a9044ecb033ba62dfef.png!small)

3.漏洞利用

直接包含文件

如果知道一些文件的路径，可以直接进行文件包含，如下，phpinfo1.php是我创建的一个测试文件，内容就是phpinfo。如下图可以看到直接显示了phpinfo的页面。

![](https://image.3001.net/images/20221226/1672021003_63a9040bd2ae351aecf10.png!small)

上面只是实现了任意文件包含，若想实现RCE还需结合其他扩展模块，如pear扩展。网上关于利用pear扩展实现RCE的文件很多，大家有兴趣可以去看看，如下面的链接。由于环境问题，本人没有搭建成功，在此不在复现。

[https://blog.csdn.net/weixin_53090346/article/details/127241278﻿](https://xz.aliyun.com/t/11940)

## 总结

该漏洞属于任意文件包含漏洞，仅仅一个文件包含漏洞也许并不能造成严重的危害，关键是要找到其它的点来利用文件包含。

