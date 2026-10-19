# pcfcms安装页面的一处意料之外的变量注入可导致网站瘫痪

阅读量 **234764**

|评论 **3**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-10-22 15:30:09

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t01d01534c3c31ff646.jpg)

## 前言：

在代码审计环节当中，本人偏向于先审计网站安装文件，因为在这里涉及了很多对数据库的操作，如果在网站安装完后没有删除安装文件，或者对网站安装页面访问的限制不够严谨，就会导致产生恶意访问的情况，轻则数据被篡改，重则被重装，注入

近期在php代码审计过程当中发现了pcfcms在install文件中有一处判断过滤不严谨的地方，可导致恶意入侵者篡改本不应该运行的安装过程中的数据，最后造成网站瘫痪

* * *

**实验环境：**  
wampserver3.1.7 64bit  
phpversion:7.2.14  
MySQL:5.7.24  
Apache:2.4.37  
url::<http://127.0.0.4/pcfcms/>  
pcfcms:V2.1.1  
pcfcms纯净版下载地址：  
<http://www.pcfcms.com/>  
这里需要注意，php版本需要高于7.1且php的上传限制要大于8M,否则安装页面会报错

## pcfcms介绍：

PCFCMS是基于TP6.0框架为核心开发的免费+开源的企业内容管理系统，专注企业建站用户需求提供海量各行业模板，降低中小企业网站建设、网络营销成本，致力于打造用户舒适的建站体验。

## 代码分析：

首先进入程序安装页面<http://127.0.0.4/pcfcms/install/index.php>

![](https://p1.ssl.qhimg.com/t01691a98cb7ee7ad10.png)

然后按照步骤配置好后安装成功

![](https://p5.ssl.qhimg.com/t015c8dd067853d561c.png)

当出现这个提示说明安装成功

安装成功后再次访问该文件会提示

![](https://p5.ssl.qhimg.com/t019e5882e603b27726.png)

总结这个安装过程中需要手动输入的有数据库信息，管理员账号密码，看一下/install目录下的情况

![](https://p4.ssl.qhimg.com/t01911a12c62ec13e87.png)

(请忽略exp.txt文件)可以看出增加了install.lock文件，但是安装页面并没有被删除，进入index.php文件内开始审计

![](https://p5.ssl.qhimg.com/t010aeeca6598d67ceb.png)

![](https://p5.ssl.qhimg.com/t010cd0ac95925471fc.png)

这里注意代码的37行-43行  
`if($get!='step5-1'){....程序已安装...  
};`  
在之前对$get变量有个定义  
`$get=@$_GET['type']?$_GET['type']:$config['indexpage'];`  
也就是说，$get就是我们用户以get方式向服务器提交的参数，如果我们get的不是type=step5-1，那么程序会对install.lock文件做个判定，这里的step1到step5就是程序进行配置$config和$db_config的步骤  
尝试get方式提交type=step5-1

![](https://p3.ssl.qhimg.com/t01999404f44cf2befa.png)

(这里要注意当安装完成后要清除cookie,否则访问无效)  
可以看到，当type=step5-1时，成功绕过了install.lock的文件检测，追踪两项关于账户密码的报错：

![](https://p4.ssl.qhimg.com/t01f39c3366114357df.png)

/step5-1.html文件第十五行，调用了php代码分别输出$_SESSION[‘adminaccount’]和$_SESSION[‘admin_password’];回头来看index.php中哪里定义了这两个数据：

![](https://p4.ssl.qhimg.com/t019f135f25b297f127.png)

可以看到，在148与149行，当满足if语句$_POST[‘type’]==’3’时，程序会接收来自post方式上传的账号密码，再来追踪$_POST[‘admin_account’]和$_POST[‘admin_password’]

![](https://p0.ssl.qhimg.com/t010af4cc3ed5eaa227.png)

在157和160行内，程序会直接接收用户post的账户密码，并在161行生成插入数据库的语句，并在接下来的语句中进行插入，但是，我们只上传了账户密码，数据库配置需要满足  
if ($get == $config[‘importPage’])，

![](https://p1.ssl.qhimg.com/t018f369dbdb68080bc.png)

所以此时的数据库内容为空，但是进行强行插入的话就会导致数据库内容无法连接，如果访问者post了admin_account=”任意值”,并且符合条件type=step5-1，程序则会向错误的数据库插入数据，最后导致网站无法连接致正确的数据库，攻击产生

## 漏洞利用过程：

访问页面  
<http://127.0.0.4/pcfcms/public/install/index.php?type=step5-1>  
post数据：type=3&admin_account=123&admin_password=123

![](https://p3.ssl.qhimg.com/t01b7a71af93e715bca.png)

刷新页面：

![](https://p1.ssl.qhimg.com/t0163087622c7d33b5f.png)

访问主页：

![](https://p2.ssl.qhimg.com/t01a4e48d8a9091455f.png)

修补建议：

安装完成后不建议保留安装文件

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **schiz0wcingu** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/219034](/post/id/219034)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)

 **+1** __3赞

 __收藏

![](https://p3.ssl.qhimg.com/t01540ba788035bcd2e.png) schiz0wcingu

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

