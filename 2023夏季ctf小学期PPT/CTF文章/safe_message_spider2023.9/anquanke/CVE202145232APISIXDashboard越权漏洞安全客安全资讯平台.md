# CVE-2021-45232 APISIX Dashboard 越权漏洞

阅读量 **132409**

发布时间 : 2022-03-23 10:30:20

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p403.ssl.qhimgs4.com/t0115d65f4fcf5b43d5.png)

## 漏洞描述

在2.10.1之前的Apache APISIX Dashboard中，Manager
API使用了两个框架，并在框架‘gin’的基础上引入了框架‘droplet’，所有的API和认证中间件都是基于框架‘droplet’开发的，但有些API直接使用框架‘gin’的接口，从而绕过了认证。

## 利用条件

Apache APISIX Dashboard < 2.10.1版本

## 漏洞原理

###  漏洞分析

对一个漏洞的分析、先提出几个问题：  
1.是什么漏洞  
CVE官方给出的描述是 api 未授权漏洞

![](https://p3.ssl.qhimg.com/t0138ae9fd743b945a2.jpg)

2.什么原因导致出现了这种漏洞  
分析思路(在gtihub上对提交的源码做分析、涉及到认证相关的代码)  
在commits中找到提交的修复记录、发现中间件鉴权相关

![](https://p1.ssl.qhimg.com/t0161f1e2c855351a76.jpg)

点进去看修改的代码  
移除了 filter包、中间件鉴权方式

![](https://p1.ssl.qhimg.com/t012b01673def7dcf81.jpg)

修改了authentication文件，对login、version及未经认证的接口处理做了修改。

![](https://p4.ssl.qhimg.com/t01a5386a8276a5d79d.jpg)

修改了authentication_test.go 做了修改，对各种状态的请求做了修改

![](https://p1.ssl.qhimg.com/t0199704367e801517a.jpg)

关键修复migrate_test.go中、添加了两个接口的描述、增加了api token验证。

![](https://p1.ssl.qhimg.com/t01311ac122c511d814.jpg)

在带有漏洞的版本中、结合migrate_test.go中的修复、判断应该是这两个api存在未授权漏洞。  
/apisix/admin/migrate/import  
/apisix/admin/migrate/export

![](https://p4.ssl.qhimg.com/t018466ae69786bcc34.jpg)

![](https://p5.ssl.qhimg.com/t01088851bd53fcffc6.jpg)

###  漏洞验证

通过访问 <http://127.0.0.1:9000/apisix/admin/migrate/export>  
下载到配置文件 apisix-config.bak

![](https://p2.ssl.qhimg.com/t01868131808f53ea8c.jpg)

![](https://p2.ssl.qhimg.com/t01f2cec5b524a9ff41.jpg)

###  漏洞利用

手动测试：  
主要利用过程就是在接口路由中执行一个扩展脚本 , 通过执行系统命令。  
通过在路由列表、查看数据时、添加script字段、后跟系统命令。

![](https://p5.ssl.qhimg.com/t0103642116b5ed30d7.jpg)

最终脚本执行是在管理apache/apisix 的 9080端口的容器里

![](https://p5.ssl.qhimg.com/t0115eea5b77d4afe52.jpg)

访问创建的路由 <http://11.22.33.101:9080/dream> 执行扩展脚本  
运行docker命令  
docker exec -it 0f643a6a69b8 /bin/sh  
cd /tmp  
ls

## 修复建议

升级到最新版本([https://github.com/apache/apisix-dashboard)；](https://github.com/apache/apisix-dashboard\)%EF%BC%9B)  
接口添加token验证；  
建立白名单、做ip验证。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **星阑科技** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/270518](/post/id/270518)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhimg.com/t01ae1a72a720da3a7b.png) 星阑科技

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

