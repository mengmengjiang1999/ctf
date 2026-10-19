## 影响版本

![](https://image.3001.net/images/20210118/1610976302_60058c2e548dd977e4b62.png!small)

## 漏洞分析

简便的方法是，根据影响版本可以得到的信息是，v2.6.2是安全的，所以只需要在github上对比v2.6.2和v2.6.1的版本更迭记录即可。

### Compare v2.6.1 and v2.6.2

Analizied 6 changed files with **11 additions** and **12 deletions**.

![](https://image.3001.net/images/20210118/1610978188_6005938cd818de5f8c4aa.png!small)

uth.py&&ws.py这两个文件，前者删了一个方法，后者加了一些权限校验。接下来逐一分析。

### auth.py的代码分析

根据jumpserver官方给的应急解决方案中，定位到了要封禁的接口:

![](https://image.3001.net/images/20210118/1610978206_6005939e79e03544f2ec0.png!small)在api_urls.py文件中的url路由规则如下:

![](https://image.3001.net/images/20210118/1610978221_600593add72fa4faa95ac.png!small)

UserConnectionTokenApi类对应的是auth.py，所以通过这种方式也可以找到漏洞发生的地方

该类有三个方法:一个POST方法，和一个GET方法，和一个get_permissions方法，各自对应的源码如下：

POST:

![](https://image.3001.net/images/20210118/1610978241_600593c18741191e8a19b.png!small)GET:

![1610978278_600593e6e1585e6a9152d.png!small?1610978279175](https://image.3001.net/images/20210118/1610978278_600593e6e1585e6a9152d.png!small?1610978279175)get_permissions:

![1610978290_600593f2adfe6d294981e.png!small?1610978291042](https://image.3001.net/images/20210118/1610978290_600593f2adfe6d294981e.png!small?1610978291042)

首先对接口进行功能分析，POST方法实现的是:

post提交user、assest、system_user，该方法会设置生成一个token，并将该数组的对应关系缓存，然后返回token。

get方法实现的是，请求提交token，该方法用token去查user，如果存在就把token对应的user返回。

功能上看起来实现的是，用户通过jumpserver使用不同机器时，服务器按照用户提交参数签发一个20s的token，用户使用该token去访问对应的机器。

但我们使用jumpserver会发现，客户端使用机器时，向服务端提交的参数都是id，且ID随机复杂无规律，通过爆破的方式显然是不合理的，而本次未授权漏洞正是因为log中记录了这些敏感信息，并且可以被攻击者未授权访问到，所以产生了一个漏洞利用链。

### ws.py文件分析

 **Compare connect()**

如图为v1.5.9的connect函数。

![1610979693_6005996d9ce95697de035.png!small?1610979693841](https://image.3001.net/images/20210118/1610979693_6005996d9ce95697de035.png!small?1610979693841)如图为v2.6.2的connect函数![1610979704_600599780b643652a7821.png!small?1610979704237](https://image.3001.net/images/20210118/1610979704_600599780b643652a7821.png!small?1610979704237)

ws文件里对connect函数加了校验，判断只有认证过的org_admin才能访问该函数，证明这里是个未授权的入口。

继续分析函数，我们通过该未授权接口传入的task参数会传入到read_log_file中。

![1610979728_600599900e5e15de327fa.png!small?1610979728446](https://image.3001.net/images/20210118/1610979728_600599900e5e15de327fa.png!small?1610979728446)

 **wait_util_log_path_exist**

作用:
读取传入的logpath。并返回![1610979738_6005999a66e636a1edd79.png!small?1610979738878](https://image.3001.net/images/20210118/1610979738_6005999a66e636a1edd79.png!small?1610979738878)
**read_log_file![1610979749_600599a5f356f9ea3cc97.png!small?1610979750405](https://image.3001.net/images/20210118/1610979749_600599a5f356f9ea3cc97.png!small?1610979750405)**

通过以上流程分析的很清楚了，我们只需向服务器发起websocket请求，并提交json格式的taskid:logpath即可获取到日志中的敏感信息。

找到该websocket的访问路径

![1610979763_600599b3293ea25530f94.png!small?1610979763458](https://image.3001.net/images/20210118/1610979763_600599b3293ea25530f94.png!small?1610979763458)

###  **漏洞利用过程**

使用chrome插件 Websocket Client发包如下:

![1610980144_60059b305d906add07b2d.png!small?1610980144562](https://image.3001.net/images/20210118/1610980144_60059b305d906add07b2d.png!small?1610980144562)

![1610980161_60059b41cc7dc557bb72d.png!small?1610980162202](https://image.3001.net/images/20210118/1610980161_60059b41cc7dc557bb72d.png!small?1610980162202)

找到包含重要字段的日志:

> [18/Jan/2021:12:58:23 +0800] \"GET /api/v1/perms/asset-> permissions/user/validate/?action_name=connect&asset_id=12037419-570f-4732-b135-a8287f19f463&cache_policy=1&system_user_id=d90fe502-3263-4ed9-9540-9d5a60a39d42&user_id=adfcaf61-85bd-4102-b5a4-6f339d7f1db4

首先根据ID构造post包获取token令牌:

![1610979914_60059a4a69a92ec88d65e.png!small?1610979914824](https://image.3001.net/images/20210118/1610979914_60059a4a69a92ec88d65e.png!small?1610979914824)编写python模拟正常请求即可,用github上大佬ska的脚本[参考链接在后面]:

![1610979925_60059a55a5b1e249165a3.png!small?1610979926127](https://image.3001.net/images/20210118/1610979925_60059a55a5b1e249165a3.png!small?1610979926127)

大佬用协程写了个交互式shell(膜).

### modsecurity判定规则

在这种场景下，基本上看到这个uri请求我们就可以断言这是一个报警，因此编写规则如下:

> SecRule REQUEST_URI "/ws/ops/tasks/log"
> "id:11111111,phase:1,id:52,t:none,t:urlDecode,t:lowercase,t:normalizePath,msg:'jump-> rce'"

![1610979989_60059a95576e0083d5412.png!small?1610979989679](https://image.3001.net/images/20210118/1610979989_60059a95576e0083d5412.png!small?1610979989679)

可以通过部署的规则起到一定的报警作用，也可以捕获一些告警流量。

## 参考链接

> <https://s.tencent.com/research/bsafe/1228.html>
>
> <https://github.com/Skactor/jumpserver_rce>

