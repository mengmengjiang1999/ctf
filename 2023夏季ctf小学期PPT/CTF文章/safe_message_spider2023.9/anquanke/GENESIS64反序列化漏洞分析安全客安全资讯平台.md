# GENESIS64反序列化漏洞分析

阅读量 **167690**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2022-01-07 10:30:20

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t0121cf6463b1fc897f.png)

ICONICS是一家专门从事可视化和自动化软件开发的公司，ICONICS解决方案提高效率，缩短集成时间和节省运营成本，优化资产利用率。GENESIS64为ICONICS公司的软件产品，套件所包含的一系列解决方案实现了从工厂车间和楼宇设备一级到企业业务系统的互联互通。GENESIS64是革命性的全新设计，充分利用了64位系统的优点、OPC/OPC-UA 的先进架构、微软 .NET 托管代码、 Silverlight 和 SharePoint 的技术优势。该系统允许企业的管理者和 IT 专家利用
GENESIS64 实现生产实时和商业信息为一体化、安全、通用、基于 Web 方式的可视化管理平台。

## 0x00 概述

GENESIS64软件的多个版本存在反序列化漏洞，影响多个组件，例如：

![](https://p3.ssl.qhimg.com/t0162b3208eda76a2de.png)

![](https://p0.ssl.qhimg.com/t01ad4e1e2aa7ee7ab8.png)

根据CVE漏洞相关描述，下载对应GENESIS软件版本搭建环境，进行漏洞分析与复现工作。软件安装可参考如下链接：https://jingyan.baidu.com/article/5d368d1ebb5a163f61c05773.html

## 0x01 服务分析

安装完成后对整个系统进行熟悉，发现Web程序接口使用Silverlight进行数据交互，因此需要找到相关功能文件进行分析。经过一些时间查找，找到系统服务开启的配置文件，在配置文件中定义了访问接口信息以及调用的相关配置文件信息：

![](https://p1.ssl.qhimg.com/t016f55fc2c79383ea0.png)

经过多方分析找到FwxServer类，类中定义了重要服务的启动与注册配置，跟进一下StartAsyncServer()进行查看：

![](https://p3.ssl.qhimg.com/t014aa772efaa067d9f.png)

StartAsyncServer()函数里对配置项进行处理，加载配置项里的配置，在后面有一个FwxServerBase()函数处理了很多的参数，继续跟进：

![](https://p1.ssl.qhimg.com/t013d51fe1f1bdcc40d.png)

FwxServerBase()函数里只是对配置文件里的配置做了一些设置，但此处发现继承了AsyncServer,再次跟进AsyncServer：

![](https://p1.ssl.qhimg.com/t01bea192c200e4c158.png)

AsyncServer()函数最后完成配置相关参数并进行启动。到这里就完成整个服务的创建与启动，当然这里只看了一个启动项目，其他的服务注册与启动都差不多：

![](https://p5.ssl.qhimg.com/t01b747bf3eb418876e.png)

## 0x02 漏洞分析

基于前期的服务启动流程以及配置项的分析，最后定位到Asyncserver里处理提交请求的接口中，此接口中定义了几个接口，均为提交请求的处理，于是就用这个作为分析的突破口。

下图中定义了一个服务契约，在服务契约里面有多个处理提交请求的操作契约：

![](https://p1.ssl.qhimg.com/t018102e92d8de6d3d5.png)

我们来对相关参数做一个简单的分析，因为这里只有PutRequests是处理提交请求的，所以先来看看它。这里是判断提交过来的数据里的Session是否失效，失效返回false，如果Session未失效则进入第二层处理Request：

在下图可以看到Request()函数对我们提交过来的数据进行了处理：

![](https://p0.ssl.qhimg.com/t01756f61df6bf97a69.png)

主要的SOAP数据包标签头：

![](https://p3.ssl.qhimg.com/t01daaf6713b4e2bc0a.png)

标签里的cat标签对应了下面的几种提交类型,几种类型对应了相关的处理方式：

![](https://p1.ssl.qhimg.com/t01a8eba7254d68b683.png)

![](https://p3.ssl.qhimg.com/t01fb8ab37e3f8cdcba.png)

其他的标签处理大同小异。来到PutRequest()函数，此函数里有一个a函数处理session，跟进分析一下：

![](https://p0.ssl.qhimg.com/t01802e153c970f5047.png)

a()函数里，判断了标签Actor和用户提交的数据A_1，跟进a(A_1)重载函数：

![](https://p4.ssl.qhimg.com/t019c4422685eae59d6.png)

可以看到a(A_1)重载函数里只是一个值选项判断，再次回到之前，跟进a(A_0)重载函数：

![](https://p2.ssl.qhimg.com/t01f0becb4d020076a3.png)

a(A_0)重载函数处理了Session相关数据，也没什么可分析的，接着往下看：

![](https://p3.ssl.qhimg.com/t015200cfec30906c2e.png)

接下来看到存在一个if判断，对标签PointName和PointHandle做了值判断，因为一般情况下都会有值，因此这个地方流程一般不会进入，进入else分支分析：

![](https://p5.ssl.qhimg.com/t01bece6c42c06ec904.png)

在else分支里面进行了一系列的标签值判断，下面代码对提交的数据进行了处理

PointManager.ValidationResult validationResult = this.a(session, request, out
pointManagerWrapper, out pointHint);

只要validationResult的值不为Invalid和Unknown，则不会进行处理request数据，否则处理完成后进行返回：

![](https://p3.ssl.qhimg.com/t01af62b310a6c2c168.png)

继续往下看，这里调用了IsRequestAllowed()函数，这个函数是属于ISecurityManager接口的，跟进看一下处理：

在IsRequestAllowed()函数中，也对相关标签值进行了判断，这里判断了cat标签值是否为4以及InParams的值是否为SubscribeProcedureInParams；接着判断了Session信息是否失效，后面判断了PointName的值是否为“cfg:”开头的，如果是则进入tj.a()函数里，跟进tj.a()函数：

![](https://p5.ssl.qhimg.com/t01513c4a8f406d3060.png)

函数根据cat标签的值进行处理，如果我们提交了cat的值为4且InParams的值为SubscribeProcedureInParams的话，就会进入case
4分支处理，再次跟进tj.a()重载处理函数看看：

这里首先进行了一次判断，使用的是RepositoryIdentifier类，跟进RepositoryIdentifier.TryParse()函数:

这里把用户提交过来的PointName数据用”|”进行分割，加到list变量里面：

![](https://p2.ssl.qhimg.com/t01f712ef09c8829ac6.png)

在处理完数据后，判断了数据的格式是否正常，这里主要判断了数据的长度，Guid.值，“rpt:“， “ctx:”
，“tag:”，随后处理了”tag:”标签，可以看到这里将”tag:”标签Base64解密后进行了反序列化的操作，跟进Deserialize()函数：

反序列化调用了DataContractSerializer进行序列化操作：

![](https://p4.ssl.qhimg.com/t010e5230d79bf025ac.png)

分析上图代码，可知代码里面存在一个坑：代码对用户提交过来序列化的数据进行自定义处理，固不能直接生成POC，须预先做一个处理才能被利用。进入Deserialize()函数后，函数首先获取序列化数据的前4个字节，然后以前4个字节作为长度读取序列化数据，所以我们须在前面加上长度，否则无法反序列化成功，因为在前面的GetType获取中就读取错了数据。

我们可以看到在DataContractSerializer()函数中，GetType的参数是可以控制的,分析一下对type的处理过程：首先使用工具生成一个测试poc，然后带入函数进行处理：

![](https://p1.ssl.qhimg.com/t013c93cf87faa0513b.png)

看到函数已经对数据进行了处理，处理完数据之后我们发现，取出的变量值并不完整

![](https://p5.ssl.qhimg.com/t01974cb7ded66aaf1d.png)

接下来带入系统进行查找类型：

![](https://p2.ssl.qhimg.com/t01f732cdcf5f38ff83.png)

最后返回的type结果为null，也就是没有找到所属的类型，自然就会反序列化失败：

![](https://p4.ssl.qhimg.com/t01ed41496ddbd7b582.png)

这里的序列化类型的清单均置于list清单里，System.Security.Principal.WindowsPrincipal是在list里面的，但却没有找到，就是因为数据存在格式问题：

根据按照序列化处理代码对POC进行删减构造，即可成功获取type：

![](https://p0.ssl.qhimg.com/t019ba35406ad084504.png)

## 0x03 POC构造

根据上节的漏洞分析，我们可以构造出漏洞利用POC，并使用DataContractSerializer()作为反序列化的载体进行利用测试：

通过抓包可以看到请求的数据，在数据包中可以看到，标签cat为4，type为0，但是Inparams还不是SubscribeProcedureInParams，借用抓到的数据包构造POC，删除数据包中一些不必要的数据并添加一些能够让漏洞触发的数据：

数据包构造完成后，使用工具生成POC，此处使用ysoserial.NET，把漏洞利用POC修改后添加到数据包里面即可成功利用：

![](https://p5.ssl.qhimg.com/t01b79f5ed1e9e8fc7e.png)

## 0x04 总结

这个GENESIS64
.NET的反序列化漏洞的分析过程比较曲折，一方面没有太多的资料可供参考，加之软件程序十分庞大，系统开启服务太多，漏洞分析过程中发现的坑点也很多，导致漏洞定位难度增大，但总的来说，整个漏洞的利用过程还是很有意思，个人收获很大。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **博智安全** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/264690](/post/id/264690)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [工控安全](/tag/工控安全)

 **+1** __2赞

 __收藏

![](https://p5.ssl.qhimg.com/t01dc77631201c3445b.png) 博智安全

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

