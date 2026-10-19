# Fastjson <=1.2.68 反序列化远程命令执行漏洞分析

阅读量 **495912**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-06-10 10:02:08

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

## 一、漏洞概述

近期Fastjson连续发布了两个版本。其中1.2.69版本修复了两个安全漏洞：前者能够绕过反序列化autotype开关限制，造成的危害严重；而后者则是常规的黑名单列表更新，在开启autotype且当前Classpath中存在Gadget类前提下会触发反序列化漏洞。对于1.2.70版本，从commit得知针对安全问题只是在黑名单列表中新增了12个Gadget漏洞利用类。相比较而言，没有出现绕过autotype的限制，造成影响并没有上版中第一个漏洞危害大。

经分析发现，绕过autotype开关反序列化漏洞在1.2.68及以下版本中均受影响，黑客可利用该漏洞直接获取服务器系统权限并远程执行任意命令。当前官方采用黑白名单的方式防御上述漏洞，但存在漏洞版本中没有统一控制的方式彻底关闭反序列化功能，导致威胁始终存在。本文主要分析了绕过autotype的漏洞成因、POC构造方式及修复建议。

## 二、漏洞分析

### 漏洞成因

Fastjson组件在反序列化不可信数据时会导致远程代码执行。究其原因：1.
Fastjson提供了反序列化功能，允许用户在输入JSON串时通过“@type”键对应的value指定任意反序列化类名；2.
Fastjson自定义的反序列化机制会使用反射生成上述指定类的实例化对象，并自动调用该对象的setter方法及部分getter方法。攻击者可以构造恶意请求，使目标应用的代码执行流程进入这部分特定setter或getter方法，若上述方法中有可被恶意利用的逻辑（也就是通常所指的“Gadget”），则会造成一些严重的安全问题。官方采用了黑名单方式对反序列化类名校验，但随着时间的推移及自动化漏洞挖掘能力的提升。新Gadget会不断涌现，黑名单这种治标不治本的方式只会导致不断被绕过，从而对使用该组件的用户带来不断升级版本的困扰。

### 补丁diff分析

通过68和69版本补丁diff分析发现（https://github.com/alibaba/fastjson/compare/1.2.68…1.2.69），总计有928处文件修改，其中1094处新增、233处删除。

![](https://p4.ssl.qhimg.com/t01ca777fa10f7bc2d3.png)

经对比分析，发现在src/main/java/com/alibaba/fastjson/parser/ParserConfig.java中将原明文存储的期望类经自定义消息摘要函数转换为hash值，并且新增了三个Class对象，较其它修改部分而言，推测这三个期望类是绕过autotype机制关键之所在。补丁详情如下图所示：

![](https://p3.ssl.qhimg.com/t0166137fc709ee208b.png)

使用彩虹表碰撞的方式，还原出了全部经消息摘要函数散列运算的明文Class对象，其中增量部分如下表所示：

版本 | 十进制hash值 | 十六进制hash值 | 类名  
---|---|---|---  
1.2.69 | 5183404141909004468L | 0x47ef269aadc650b4L | java.lang.Runnable  
1.2.69 | 2980334044947851925L | 0x295c4605fd1eaa95L | java.lang.Readable  
1.2.69 | -1368967840069965882L | 0xed007300a7b227c6L | java.lang.AutoCloseable  
  
从上述源码分析得知，将输入的期望类和源码中定义的Class对象做了 ”==” 运算符比较，
并依据判断结果为布尔类型标志位expectClassFlag赋值。为了解该标志位作用，跟入com.alibaba.fastjson.parser.
ParserConfig源码中查看该变量的引用，发现总计有两处if条件判断表达式中将该部分作为的输入值之一，如下图所示：

![](https://p1.ssl.qhimg.com/t01801a4d656fe75d55.png)

继续跟入上述条件表达式，发现都在ParserConfig#checkAutoType方法中定义，其中之一在方法体内部调用了TypeUtils.loadClass方法加载类，如下如所示：

![](https://p3.ssl.qhimg.com/t01ea4d4aa763788ec0.png)

因为该部分是反序列化类的关键部分之一，所以进一步印证了上述猜想。

使用68版本搭建调试环境，因为反序列化功能需要指定“@type”键，先尝试将其对应的value值指定为java.lang.AutoCloseable，开始调试分析。程序执行过程中首先在TypeUtils#addBaseClassMappings方法中调用ConcurrentMap对象的put方法添加java.lang.AutoCloseable
Class对象。如下图所示：

![](https://p1.ssl.qhimg.com/t012db896f79ed6afe0.png)

无论是否开启autotype开关，在反序列化前都会经过ParserConfig#checkAutoType函数校验所加载的反序列化类名：

![](https://p5.ssl.qhimg.com/t011da98f454e218040.png)

因该类不在官方内置白名单中，进行如下解析流程：1.采用二分查找法，检索一遍由内置白名单加上用户自定义白名单（可选）所组成的全量白名单列表。若检索结果大于等于0，则调用TypeUtils.loadClass加载类，在返回值不为空的前提下返回该class对象；2.若上述检索结果为空，继续使用二分法检索黑名单列表。在检索结果大于等于0并且调用TypeUtils.getClassFromMapping返回值为Null的前提下，再次使用二分法检索白名单列表，若检索结果为空则抛出JSONException异常。详细代码，如下图所示：

![](https://p5.ssl.qhimg.com/t01ffb95a438d8c2bc7.png)

经过上述黑白名单校验后，继续调用TypeUtils.getClassFromMapping方法从上文mapping对象中获取当前Class对象:

![](https://p5.ssl.qhimg.com/t01b1ea71f7aa845b7c.png)

继续单步调试过程，返回了该class对象：

![](https://p1.ssl.qhimg.com/t01e54e37ac45634a2a.png)

上述过程只是想调试针对java.lang.AutoCloseable接口的解析流程，由于解析到后续传入的是空Json对象，直接结束了反序列化过程：

![](https://p2.ssl.qhimg.com/t01a42aa377d7d01713.png)

### POC构造

基于上一小节补丁diff分析，下面开始构造POC。受1.2.47版本绕过autotype开关限制的启发，采用嵌套定义Json对象的方式在原基础上复用历史恶意payload，并开始后续调试过程。

前面解析过程和上一小节一致，此处继续Json串扫描解析过程：

![](https://p0.ssl.qhimg.com/t01a50b4c0d09b0dff6.png)

再次步入ParserConfig#checkAutoType方法，注意此时第二个参数 expectClass 为 AutoCloseable.class
，通常情况下这个参数都为 Null，此处采用了指定期望类的方式加载反序列化链中目标类：

![](https://p1.ssl.qhimg.com/t01a4da8a8a32cd6c56.png)

继续单步调试，因上述类名未出现在默认列表中，此时期望类标志位被设置为true：

![](https://p2.ssl.qhimg.com/t018d07b78c4a6b632c.png)

当前期望标志类为true时满足分支判断条件，进入如下解析流程，从源码得知会将目标类经过黑白名单校验，因为此时提供的Gadget
com.sun.rowset.JdbcRowSetImpl出现在黑名单列表中，直接抛出异常：

![](https://p3.ssl.qhimg.com/t015c62a29550d2f2c8.png)

这是本次漏洞和历史上47版本绕过autotype最大的不同之处，后者主要利用代码逻辑缺陷变相绕过了黑名单以及autotype开关检查，详情请参考文献2
，构造EXP的过程中可以直接复用历史Gadget。而本次漏洞利用过程中还需经黑名单校验，所以历史Gadget
构造的EXP在本次漏洞利用中已然失效。这就需要寻找不存在于黑名单列表中的新Gadget，

跟入上文中另一个引用了标志位的条件分支中，源码如下：

![](https://p0.ssl.qhimg.com/t01d52723f1e2620bbc.png)

进入该判断逻辑中调用TypeUtils.loadClass方法加载目标类。

继续查看后续执行过程，发现如下判断逻辑：

![](https://p3.ssl.qhimg.com/t014eb49c87aad20e6d.png)

当期望类不为空，调用isAssignableFrom()方法。跟入该方法从描述信息中发现，主要作用是判断一个类是否为某一个接口的实现类或者某个类的子类。

此时终于水落石出，真相大白。原来构造POC过程所输入目标类名，不仅需要不在当前黑名单列表，还需同时满足是所提供期望类的实现类。从实验角度出发，这里写了一个AutoCloseable接口的实现类并在getter方法中调用危险敏感函数。继续下面的漏洞调试，因为当前未开启autotype开关，进入常规黑白名单校验过程：

![](https://p4.ssl.qhimg.com/t01a18b9bf9675e8877.png)

调用TypeUtils.loadClass方法加载需要反序列化的目标类：

![](https://p0.ssl.qhimg.com/t01b6f836f28f405962.png)

这里判断了如果期望类不为空且反序列化目标类实现了期望接口就会添加到缓存 mapping 中并返回该class对象：

![](https://p3.ssl.qhimg.com/t01234b59f34b301344.png)

Fastjson调用ASM生成目标类的反序列化器：

![](https://p5.ssl.qhimg.com/t01a8c6676fd153a4f6.png)

和47版本绕过方法相类似，已加入到缓存表中的类在反序列化解析时会绕过autotype开关限制，并使用上述反序列化器反序列化目标类。最终造成任意命令执行，漏洞触发结果如下图所示：

![](https://p0.ssl.qhimg.com/t01053440596c8d373c.png)

完整漏洞原理分析过程到此也就全部结束了，在实战场景下，只需去寻找满足上述条件的合适
Gadget来利用此漏洞。这部分工作就交给亲爱的读者朋友们了，作者在此不过多赘述。探究漏洞原理的过程是繁琐而又有趣的，真可谓“山穷水尽疑无路，柳暗花明又一村”。同时在此祝愿Fastjson这款优秀的产品，能够越来越安全。

## 三、修复建议

  1. 对于使用了fastjson反序列化功能的应用，请将组件版本升级至1.2.70或对应版本的sec10安全版本（注意：不能开启safemode模式，否则会影响反序列化功能）。
  2. 其他未使用反序列化功能的应用，可将组件版本升级至1.2.70或对应版本的sec10安全版本并推荐开启safemode模式。
  3. Safemode模式

Fastjson
1.2.68及之后的版本（包括安全修复版本sec10）中，新增了safeMode模式，开启方式参考：<https://github.com/alibaba/fastjson/wiki/fastjson_safemode>。

跟进源码分析了safemode模式底层实现原理，当Fastjson解析到Json串中出现了“@type”键后会统一进入反序列化解析流程，从value中获取需反序列化的类名，经过ParserConfig#checkAutoType检查函数校验。并根据是否开启autotype使用不同先后顺序的黑白名单做类名检查。引入safemode模式后在执行后续反序列化过程前做了一次判断，当开启safemode时，由于布尔类型变量为true，对于传入的任意类名直接抛出异常，从而不进行后续的反序列化流程。Safemode可以说是等价于一个是否开启反序列化功能的总开关，开启后则禁用了反序列化功能。其中核心实现代码如下所示：

![](https://p4.ssl.qhimg.com/t0159c89c35947ea087.png)

开启safeMode模式后，依靠移除反序列化功能，从而保障不会遭受反序列化漏洞危害所造成的影响。理论上不用因为日后所爆发的反序列化漏洞原因而不断升级至新版本。

## 四、Reference

  1. <https://github.com/alibaba/fastjson/commit/1e1239eb5f4c2052dbc097d2c4e619ebc6e5cc28>
  2. <https://www.anquanke.com/post/id/181874>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **365安全卫视** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/208104](/post/id/208104)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [fastjson](/tag/fastjson)

 **+1** __10赞

 __收藏

![](https://p2.ssl.qhimg.com/t01479c2565a350d198.jpg) 365安全卫视

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

