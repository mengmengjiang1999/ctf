**作者：Lucifaer  
博客：<https://www.lucifaer.com>**

这篇分析其实在上周五也就是2月15号左右就已经分析完了，但是当时没有及时发出来，当周一看到iswin
dalao发出的详尽分析后才把这篇分析发布做了预警算是慢了n步2333…

总体来说这个漏洞流程是比较好分析的，真正的难度是找漏洞触发点，当时分析的时候找了半天没找到触发点，最后还是硬着头皮在OrientDb的处理流程中绕了半天才意识到…还是太菜了

### 0x00 漏洞概述

> Insufficient access controls have been discovered in Nexus Repository
> Manager 3 which allow remote code execution.
>
> An unauthenticated user can craft requests in such a manner that can execute
> java code on the server. We have mitigated the issue by adding the necessary
> access controls as well as disabling the ability to execute arbitrary java
> code via this path. This advisory provides the pertinent information needed
> to properly address this vulnerability, along with the details on how to
> reach us if you have any further questions or concerns.

从官方的漏洞简述来看简单的来说就是由于未授权访问的用户可以构造请求而造成任意代码执行。而且因为3.15.0+以上的版本增加了用户认证，所以3.15.0+的版本不受此漏洞的影响。所以根据diff的结果，可以大致的确定漏洞在`org.sonatype.nexus.coreui.ComponentComponent#previewAssets`：

![-w1338](https://images.seebug.org/content/images/2019/02/26/1551149261000-15505627413764.jpg-w331s)

### 0x01 整体触发流程

    
    
    ExtDirectModule$configure:60 # 路由绑定与请求解析
      ExtDirectServlet$doPost:155 # 处理post请求
        DirectJNgineServlet$doPost:595 # 根据不同的Content-Type来解析请求
          DirectJNgineServlet$processRequest:632 # 解析json请求
            JsonRequestProcesor$process:119 # 解析json语法树
              JsonRequestProcessor$getIndividualJsonRequests:216 # 提取json数据
            JsonRequestProcesor$process:133 # 构造返回结构
    ComponentComponent$previewAssets:188 # 解析post包中的data数据并构造查询语句查询包
      ComponentComponent$previewAssets:208 # 获得查询结果
        BrowseServiceImpl$previewAssets:252 # 构建OrientDb查询语句
        BrowseServiceImpl$previewAssets:258 # 拼接查询语句
        BrowseServiceImpl$previewAssets:262 # 执行查询
          MetadataNodeEntityAdapter$countByQuery:221 # 执行OrientDb查询语句
    ContextExpressionFunction$execute:125 # 提取jexl表达式
      ContextExpressionFunction$checkJexlExpression:154 # 执行jexl表达式

### 0x02 漏洞分析

漏洞的触发主要分两部分：post包解析及jexl表达式执行。

#### 2.1 post包解析

首先先看一下web.xml中如何做的路由解析：

![img](https://images.seebug.org/content/images/2019/02/26/1551149261000-15504603584828.jpg-w331s)

`org.sonatype.nexus.bootstrap.osgi.DelegatingFilter`拦截了所有的请求，大概率为动态路由加载，动态路由加载需要配置相应的`Module`模块用代码将配置与路由进行绑定并显式加载servlet，而该漏洞的入口就在`org.sonatype.nexus.extdirect.internal.ExtDirectModule#configure`中:

![img](https://images.seebug.org/content/images/2019/02/26/1551149261000-15504698938286.jpg-w331s)

直接跟进`org.sonatype.nexus.extdirect.internal.ExtDirectServlet$doPost`:

![img](https://images.seebug.org/content/images/2019/02/26/1551149262000-15504699262539.jpg-w331s)

继续向下更进看到处理post请求的部分：

![img](https://images.seebug.org/content/images/2019/02/26/1551149262000-15504702237568.jpg-w331s)

在这里我们跟进看一下如何对json格式的请求进行处理：

![img](https://images.seebug.org/content/images/2019/02/26/1551149262000-15504702513086.jpg-w331s)

![img](https://images.seebug.org/content/images/2019/02/26/1551149262000-15504706911673.jpg-w331s)

首先对json的语法树进行解析，将数据提取出来：

![img](https://images.seebug.org/content/images/2019/02/26/1551149262000-15504708404906.jpg-w331s)

可以看到需要5个变量分别为`action`、`method`、`tid`、`type`、`data`。

注意到`isBatched`是由参数长度决定的，而返回的一个数组，其长度为1，所以`isBatched`为`false`。之后就是传入`processIndividualRequestsInThisThread`方法中：

![img](https://images.seebug.org/content/images/2019/02/26/1551149263000-15504715738470.jpg-w331s)

在这里构造返回的结果，可以看到这里在有一个json反序列化的过程，这里主要是将返回结果以json格式返回。

#### 2.2 jexl表达式执行

从post包的解析中可以得知我们需要构造5个参数，同时当我们构造好`action`和`method`后，可以直接动态调用相应的类与方法。

这个漏洞出现在`org.sonatype.nexus.coreui.ComponentComponent#previewAssets`:

![img](https://images.seebug.org/content/images/2019/02/26/1551149263000-15504724137293.jpg-w331s)

首先将post包中`repositoryName`、`expression`、`type`的值取出来，这三个参数分别代表已经存在的`repository`的名字、expression的类型，以及表达式。

着重看一下jexl的处理过程：

![img](https://images.seebug.org/content/images/2019/02/26/1551149263000-15504726133105.jpg-w331s)

![img](https://images.seebug.org/content/images/2019/02/26/1551149263000-15504726645374.jpg-w331s)

注意到这里只是实例化了一个`JexlSelector`对象，而并没有调用`evaluate`来执行表达式，所以漏洞的触发点在其他的位置。而真正的表达式执行点在`browseService.previewAssets`的处理过程中，这一点也是这个漏洞最为难找的一个点。

跟进`previewAssets`的实现，在`org.sonatype.nexus.repository.browse.internal.BrowseServiceImpl#previewAssets`：

![img](https://images.seebug.org/content/images/2019/02/26/1551149263000-15504739454711.jpg-w331s)

在这里可以看到表达式最后会被当做参数形成SQL查询，最后由OrientDb执行：

![img](https://images.seebug.org/content/images/2019/02/26/1551149263000-15504742411091.jpg-w331s)

但是OrientDb本身是没有`contentExpression`这个方法的，也就是说明这个方法是用Java来实现的，找了一下，在`org.sonatype.nexus.repository.selector.internal.ContentExpressionFunction`：

![img](https://images.seebug.org/content/images/2019/02/26/1551149263000-15504753654778.jpg-w331s)

在`checkJexlExpression`中：

![img](https://images.seebug.org/content/images/2019/02/26/1551149264000-15504754823135.jpg-w331s)

调用了`selectorManage.evaluate`来执行jexl表达式：

![img](https://images.seebug.org/content/images/2019/02/26/1551149264000-15504755769130.jpg-w331s)

### 0x03 构造POC

通过上面的分析，我们只需要按照post包解析中的参数进行相应的构造即可，下面为一个例子：

![img](https://images.seebug.org/content/images/2019/02/26/1551149264000-15505678890758.jpg-w331s)

注意，这个漏洞需要当Nexus中存在已有的jar包，在本地验证的时候先传一个jar报上去。至于原理分析可能后面会单独再拿出来分析。

### 0x04 Reference

  * <https://support.sonatype.com/hc/en-us/articles/360017310793-CVE-2019-7238-Nexus-Repository-Manager-3-Missing-Access-Controls-and-Remote-Code-Execution-February-5th-2019>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/827/>

