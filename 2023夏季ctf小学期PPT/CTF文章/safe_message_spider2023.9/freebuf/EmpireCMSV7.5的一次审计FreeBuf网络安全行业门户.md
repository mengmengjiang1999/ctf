**i春秋作家：Qclover**

**原文来自：[EmpireCMS_V7.5的一次审计](https://bbs.ichunqiu.com/thread-46685-1-1.html?from=beef)**

## EmpireCMS_V7.5的一次审计

### 1概述

    
    
       最近在做审计和WAF规则的编写，在CNVD和CNNVD等漏洞平台寻找各类CMS漏洞研究编写规则时顺便抽空对国内一些小的CMS进行了审计，另外也由于代码审计接触时间不是太常，最近一段时间也跟着公司审计项目再次重新的学习代码审计知识，对于入行已久的各位审计大佬来说，自己算是新手了。对于审计也正在不断的学习和积累中。于是抽空在CNVD上选取了一个国内小型CMS进行审计，此次审计的CMS为EmpireCMS_V7.5版本。从官方下载EmpireCMS_V7.5后进行审计，审计过程中主要发现有三处漏洞（应该还有其他漏洞暂未审计）：配置文件写入、后台代码执行及后台getshell，造成这几处漏洞的原因几乎是由于对输入输出参数未作过滤和验证所导致。

### 2前言

    
    
       帝国网站管理英文译为”EmpireCMS”，它是基于B/S结构，安全、稳定、强大、灵活的网站管理系统.帝国CMS 7.5采用了系统模型功能：用户通过此功能可直接在后台扩展与实现各种系统，如产品、房产、供求…等等系统，因此特性，帝国CMS系统又被誉为“万能建站工具”;大容量数据结构设计;高安全严谨设计;采用了模板分离功能：把内容与界面完全分离，灵活的标签+用户自定义标签，使之能实现各式各样的网站页面与风格;栏目无限级分类;前台全部静态：可承受强大的访问量;强大的信息采集功能;超强广告管理功能……

### 3代码审计部分

    
    
      拿到该CMS后先把握大局按照往常一样先熟悉该CMS网站基本结构、入口文件、配置文件及过滤，常见的审计方法一般是：通读全文发（针对一些小型CMS）、敏感函数回溯法以及定向功能分析法，自己平常做审计过程中这几个方法用的也比较多。在把握其大局熟悉结构后，再通过本地安装去了解该CMS的一些逻辑业务功能并结合黑盒进行审计，有时候黑盒测试会做到事半功倍。

常见的漏洞个人总结有：

1）程序初始化安装

2）站点信息泄漏

3）文件上传

4）文件管理

5）登陆认证

6）数据库备份

7）找回密码

8）验证码

若各位大佬在审计过程中还有发现其他漏洞可补充交流。

于是首先从程序初始化安装开始进行审计….,如下：

#### 3.1配置文件写入

    
    
      开始进行审计安装程序，根据经验安装问题一般出现在配置数据输入配置时导致，常见引发问题漏洞的参数用户输入数据库名参数、可控的表前缀等可控参数，于是乎定位到代码位置install/index.php 645行附近，可以看到表名前缀phome_,并将获取表名前缀交给了mydbtbpre参数。继续往下看并跟踪参数传递。

![image.png](https://image.3001.net/images/20181011/1539249906_5bbf16f28082d.png!small)  

    
    
       在代码位置/e/install/data/fun.php 347~379行发现，将用户前端输入的表前缀（默认phome_）替换掉默认的phome_后带入了sql语句中进行表的创建，并且可以发现过程中未作过滤。

  
![image.png](https://image.3001.net/images/20181011/1539249912_5bbf16f8e3056.png!small)  

创建表的同时将配置数据包含可控的表前缀一起写入到config.php配置文件，代码位置/e/install/data/fun.php 587~645行

![image.png](https://image.3001.net/images/20181011/1539249918_5bbf16fe15493.png!small)![image.png](https://image.3001.net/images/20181011/1539249921_5bbf1701af502.png!small)

  

整个install过程中并未对用户数据进行过滤，导致配置文件代码写入。

配置文件代码写入复现：

![image.png](https://image.3001.net/images/20181011/1539249931_5bbf170bbb764.png!small)![image.png](https://image.3001.net/images/20181011/1539249934_5bbf170e01992.png!small)![image.png](https://image.3001.net/images/20181011/1539249937_5bbf1711ba0d2.png!small)

#### 3.2后台任意代码执行

    
    
       漏洞代码发生在后台数据备份处代码/e/admin/ebak/ChangeTable.php 44行附近，通过审计发现执行备份时，对表名的处理程序是value=”” 通过php短标签形式直接赋值给tablename[]。

  
![image.png](https://image.3001.net/images/20181011/1539249952_5bbf17209e660.png!small)  

进行备份时未对数据库表名做验证，导致任意代码执行。

任意代码执行复现：

![image.png](https://image.3001.net/images/20181011/1539249957_5bbf17254bbdd.png!small)![image.png](https://image.3001.net/images/20181011/1539249961_5bbf17296605d.png!small)![image.png](https://image.3001.net/images/20181011/1539249964_5bbf172c35bdc.png!small)

#### 3.3后台getshell

代码位置：e\admin\ecmscom.php

![image.png](https://image.3001.net/images/20181011/1539249973_5bbf173510546.png!small)  

跟踪AddUserpage跳转至代码e\class\comdofun.php页面AddUserpage函数定义94行至114行处，继续跟踪代码在116行可以看到将path变量参数传入ReUserpage函数

  
![image.png](https://image.3001.net/images/20181011/1539249977_5bbf17395ec6e.png!small)  

跟踪并跳转至该函数的定义如下图所示：

  
![image.png](https://image.3001.net/images/20181011/1539249982_5bbf173eb3880.png!small)  

进入该函数继续跟踪DoFileMkDir至e/class/connect.php
2151行该DoFileMkDir函数，可以看到先执行了dirnamej进行了罗列当前可供选择的目录，如下图

  
![image.png](https://image.3001.net/images/20181011/1539249990_5bbf174675eac.png!small)  

然后执行了DoMkdir函数进行了创建文件操作

  
![image.png](https://image.3001.net/images/20181011/1539249997_5bbf174d36d74.png!small)  

代码位置为/adm1n/ebak/class/function.php

在path传递和创建过程中并未对path进行验证和限制。

同时在进行pagetext页面内容进行写入时，也未进行过滤引发代码执行的危险函数

代码位置为：e/class/functions.php 4280行

![image.png](https://image.3001.net/images/20181011/1539250003_5bbf17536f5ef.png!small)![image.png](https://image.3001.net/images/20181011/1539250006_5bbf175671f78.png!small)

  

导致用户可通过更改文件名并写入php执行代码创建自定义含[恶意代码](http://bbs.ichunqiu.com/portal.php)的文件名页面从而导致getshell。

复现：

![image.png](https://image.3001.net/images/20181011/1539250013_5bbf175dc7334.png!small)![image.png](https://image.3001.net/images/20181011/1539250016_5bbf1760bad18.png!small)![image.png](https://image.3001.net/images/20181011/1539250023_5bbf1767d77d3.png!small)![image.png](https://image.3001.net/images/20181011/1539250027_5bbf176b1d4ae.png!small)

总结：

# 大家有任何问题可以提问，更多文章可到[i春秋论坛](https://bbs.ichunqiu.com/portal.php?from=beef)阅读哟~

