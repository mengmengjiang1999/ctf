# CVE-2020-14882：Weblogic Console 权限绕过深入解析

阅读量 **289834**

|评论 **5**

发布时间 : 2020-11-06 10:00:55

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t0114a24c6a1c796452.jpg)

作者：Hu3sky@360CERT

## 0x01 漏洞简述

2020年10月29日，360CERT监测发现 `Weblogic ConSole HTTP 协议代码执行漏洞` 相关 `POC`已经公开，相关漏洞编号为
`CVE-2020-14882,CVE-2020-14883` ，漏洞等级：`严重`，漏洞评分：`9.8`。

远程攻击者可以构造特殊的`HTTP`请求，在未经身份验证的情况下接管 `WebLogic Server Console` ，并执行任意代码。

对此，360CERT建议广大用户及时将 `Weblogic` 升级到最新版本。与此同时，请做好资产自查以及预防工作，以免遭受黑客攻击。

## 0x02 风险等级

360CERT对该漏洞的评定结果如下

评定方式 | 等级  
---|---  
威胁等级 | 严重  
影响面 | 广泛  
360CERT评分 | 9.8  
  
## 0x03 影响版本

`Oracle:Weblogic`:

  * 10.3.6.0.0
  * 12.1.3.0.0
  * 12.2.1.3.0
  * 12.2.1.4.0
  * 14.1.1.0.0

## 0x04 漏洞详情

目前网上的分析都没有说清楚权限绕过具体是怎么访问到`console.portal`路径并且触发`handle`执行的，在与`@Lucifaer`的共同深入研究下，大概掌握了原理，于是有了此文。

`CVE-2020-14883` 是一个 `Console` 的未授权访问，而 `CVE-2020-14883` 是在利用未授权访问的前提下，在
`Console` 进行代码执行，于是远程攻击者可以构造特殊的 `HTTP` 请求，在未经身份验证的情况下接管 `WebLogic Server
Console` ，并在 `WebLogic Server Console` 执行任意代码。

通过`diff`补丁，`console.jar` 里主要修改有两个类，能够定位到漏洞触发点。

CVE-2020-14883: `com.bea.console.utils.MBeanUtilsInitSingleFileServlet`

CVE-2020-14882: `com.bea.console.handles.HandleFactory`

下面对漏洞进行逐个分析。

### CVE-2020-14882

首先要明白，漏洞的触发是在 `console`
组件，而`console`对应着`webapp`服务，路径：`wlserver/server/lib/consoleapp/webapp`。并且存在`web.xml`，于是查看与`MBeanUtilsInitSingleFileServlet`相关的`web.xml`信息：

    
    
      <servlet>
        <servlet-name>AppManagerServlet</servlet-name>
        <servlet-class>weblogic.servlet.AsyncInitServlet</servlet-class>
    
        <init-param>
          <param-name>weblogic.servlet.AsyncInitServlet.servlet-class-name</param-name>
          <param-value>com.bea.console.utils.MBeanUtilsInitSingleFileServlet</param-value>
        </init-param>
        ...
    
      <servlet-mapping>
        <servlet-name>AppManagerServlet</servlet-name>
        <url-pattern>*.portal</url-pattern>
    </servlet-mapping>
    

#### Request处理

从上面的 `web.xml` 内容中可以得出：

  1. `MBeanUtilsInitSingleFileServlet`是`AppManagerServlet`的`servlet-class-name`初始化的值。
  2. 访问`*.portal`会经过`AppManagerServlet`的分派处理（通过认证后访问`console`的路径是`/console/console.portal`）。 `weblogic`所有的请求都会经过`weblogic.servlet.internal.ServletRequestImpl`的预处理。跟到`doSecuredExecute`方法。

这里会调用`WebAppSecurity#checkAccess`进行权限的校验。

第一次请求的时候`checkAllResources`为`false`，于是调用`getConstraint`方法。
传入参数为请求的`/console`下的资源的路径和请求的方法。这里以请求`/console.portal`为例。

#### 静态资源列表获取

看下前面的逻辑：

  1. 获取一个`mapping`如下

  2. 以当前请求方法作为`key`值匹配`value`，而第一行获取到的`map`的`key`是`""`，所以匹配结果为`null`。

  3. 判断当前请求的`url`是否匹配`mapping`里的路径，如果匹配不到，那么返回默认的`rcForAllMethods`（ **注意`unrestricted`为`false`，`unrestricted`是权限验证的一个关键点**），也就是：

现在的结果就是`rcForAllMethods`为默认值，而`rcForOneMethod`为`null`。所以返回`rcForAllMethods`。

执行到这里可以得出的是，如果请求的路径在`matchMap`列表里，那么`unrestricted`值就为`true`，这些是属于静态资源，没有做资源的限制和身份校验。

接着做`if`判断，`resourceConstraint`不为`null`。

接着进入`else`，调用`SecurityModule#isAuthorized`。

继续调用`ChainedSecurityModule#checkAccess`。

#### 权限校验

然后调用`hasPermission`开始判断是否有权限。

在`hasPermission`方法首先判断`unrestricted`，这里我们通过修改请求`/console/css/console.protal`访问静态资源使值为`true`。

然后 `checkAcess`方法返回 `true`。

#### 重定向登陆界面

如果`checkAcess`方法返回`false`。那么不会进入后续的分派，会结束`doSecuredExecute`方法的执行。一路`return`到执行`ServletRequestImpl#runInternal`的`finally`分支。

这里会调用`send`方法，在该方法会将没有分派的请求重定向到`login`界面。

#### 请求分派

如果`checkAcess`方法返回`true`。进入后续请求的分派，经过几个`filterchain`的分派，最终调用`ServletStubImpl`的`excute`方法。这里会根据`web.xml`的配置来获取对应的具体的`Servlet`。

注意，根据`web.xml`，请求如下路径所对应的`servlet`不一样，因为几个路径都是之前所提到的静态路径，没有身份验证，但是我们需要利用到`AsyncInitServlet`来处理，因为我们diff到的修补点在`MBeanUtilsInitSingleFileServlet`，这个类是通过`AsyncInitServlet`来设置的。

`servlet`对应关系部分如下：

    
    
    /framework/skeletons/wlsconsole/js/* -> FileDefault
    /css/* -> AsyncInitServlet
    /images/* -> AsyncInitServlet
    /common/* -> JSPCServlet
    ...
    

于是，请求`/css/*`会调用`AsyncInitServlet`的`service`方法，

这里的`delegate`就是在`web.xml`被初始化的`MBeanUtilsInitSingleFileServlet`。
接下来以漏洞`URL`为例。

    
    
    /css/%252E%252E%252Fconsole.portal
    

**这里要二次编码的原因是，发过去的时候http会解一次码，也就是说如果我们传的是`/css/%2E%2E%2Fconsole.portal`，那么解码后就是`/css/../console.portal`，这样发到服务端就没办法匹配到静态资源了，直接处理成了`/console.portal`。**

如果`http`解码后的`url`里没有`;`，那么就会继续调用`super.service`，而官方的补丁修复也是在这，通过一个黑名单列表检测路径里的非法字符，不过官方给出的黑名单字符不够完善，能够被绕过。

一路到达`UIServlet#service`，根据请求`method`调用不同的方法，`doGet`最终也会调用到`doPost`。

#### url解码

在`doPost`里调用`createUIContext`。

UIContext会根据请求中的参数作对应属性值的设置，比如后面会说到的`_nfpb`。

创建完之后，会返回一个`UIContext`对象。 这里的`tree`也就是`createUIContext`传入的第三个参数，初始值为`null`。

跟入`UIServletInternal#getTree`，这里会对`requestPattern`解码。

解码后。

#### 请求portal文件，构建控件树

将解码后的`url`传入`processStream`方法。

然后`SingleFileProcessor#getMergedControlFromFile`。

**关于`.portal`的加载方式`singleFile`：简单来说，在访问`.portal`时，是从文件系统加载的而不是数据库中，解析`.portal`文件的`XML`，并将呈现的`.portal`返回到浏览器。**

将请求路径同时当作`file`路径传入，接着创建了`SAXParser`，准备将文件解析。

接着调用下方`getControlFactoryFromFile`，一直跟进，会从本地获取请求的文件.

**在这里目录穿越起了效果** ，获取到的文件也就是`webapp`下的`console.portal`。

并且以`WarSource`对象存入缓存

之后调用`sax`解析`xml`文件`console.portal`，并从中生成控制树，也就是`getTree`返回的`ControlTreeRoot`对象，然后存入`UIContext`。

#### 树的生命周期

控件树被构建后，就会进入生命周期的运行，回到`UIServlet#doPost`，调用`runLifecycle`，运行生命周期。

这里会根据`UIContext`里的两个值来判断执行`runInbound`还是`runOutbound`，后面细说

生命周期可以看作是控件上的一组方法，这些方法按定义的顺序调用。生命周期方法如下

    
    
    init()
    loadState()
    handlePostbackData()
    raiseChangeEvents()
    preRender() 
    saveState()
    render()  
    dispose() 
    

控件的具体解析流程如下

对应了调用栈里的调用，从ROOT开始，第一个子节点是`Desktop`，而接下来:

然后，深度优先遍历子节点。

当然，这个顺序也就是`console.portal`文件里的`xml`嵌套顺序。

因为是深度优先，在`console.portal`里的所有引用的`portal`文件也会按顺序解析，比如

直到所有标签解析完。

### CVE-2020-14883

接下来也就是造成代码执行的点，`com.bea.console.handles.HandleFactory` 要触发`getHandle`方法有两个触发点

#### 触发点一

回到之前创建`UIContext`的时候，有一个`setServletRequest`方法。

如果请求中存在`_nfpb=true`的时候，会把`postback`选项设置为`true`。

那么，之后在运行树的生命周期时，由于`outbound`选项默认`false`，而`postback`为`true`进入判断。

会调用`runInbound`方法，因为`runInbound`会把`types`设置为`_inboundLifecycle`。

`_inboundLifecycle`如下，注意不同的type对应了不同的静态类

当然，如果没有`_nfpb=true`，会调用`runOutbound`，`type`设置为`_outboundNewLifecycle`。

这决定了在深度遍历的时候先调用的方法，上面说过生命周期方法，于是这里就会先调用所有节点的`init`方法。因为在运行生命周期的时候，这里会调用`ControlTreeWalker#walk`方法，第一个参数，也就是`type[0]`，是`init`。

继续跟入`walkRecursive`方法

注意两处：

  1. 如果当前是`Root`节点，那么调用`visitRoot`，这个方法只会调用一次，如果不是，则调用当前`visit`的`visit`方法，当前`visit`也就是`type`里提到的静态类。`init`是`ControlLifecycle$1`，也就是第一个静态类，而这里的control就是当前节点。也就是说，如果当前`type`是`init`，深度解析所有节点的时候，都会把`init`方法调用一次。也就有了漏洞触发点`Portlet#init`。

  2. 调用完之后，如果深度遍历发现还有子节点，那么继续调用`walkRecursive`，重复`1`的步骤，直到所有节点解析完。

当调用到`Portlet`节点的`init`方法时，会一直调用`super.init`。

调用栈：

直到`AdministeredBackableControl#init`，会调用`initializeBackingFile`

最终会调用到`BreadcrumbBacking#init`，而这里会获取请求中的`handle`参数，调用`getHandle`方法。

#### 触发点二

在调用完`init`之后，会根据`type`里的顺序，继续调用生命周期方法（都对应着`ControlLifecycle`里的`visitor`）。
如果是`_nfpb=true`，调用完`runInbound`->`runOutbound`

由于`postback`为`true`。

之后流程类似，不过调用的`visitor`最开始是`ControlLifecycle#preRenderVisitor`
在调用到`StrutsContet`节点的时候，这个是在解析到引用`PortalConfig/contentheader/ContentHeader_messages.portlet`的时候。

这时候会调用`preRenderVisitor#preRender`，`preRenderVisitor`没有该方法，去父类`NetuiContent#preRender`。

并且在文件里会设置`action/refreshAction`为`MessagesAction`。

后续调用栈：

当然，不止`StrutsContet`节点会调用到这里，还有`Book`,`Portlet`节点，而在深度遍历的时候，会有很多`Book`,`Portlet`,`StrutsContet`的子节点，于是就会执行`getHandle`很多次，这也是为什么在使用计算器进行poc测试的时候，会多次弹出的原因。

最终的利用结果如下：

### 总结

  1. 通过静态资源来绕过权限验证，防止被重定向到登陆界面。
  2. 通过请求`.portal`，控制处理的`Servlet`是渲染`UI`的`MBeanUtilsInitSingleFileServlet`。
  3. 通过编码后的`../`，让最终渲染的模版是`console.portal`。

综合起来，才造成了最终的未授权访问。

## 0x05 时间线

**2020-10-21** 360CERT发布Oracle补丁日通告

**2020-10-28** 360CERT监测到POC公开

**2020-10-29** 360CERT发布通告

**2020-11-05** 360CERT发布分析

## 0x06 参考链接

  1. [White Paper: WebLogic Portal Framework](https://docs.oracle.com/cd/E13218_01/wlp/docs81/whitepapers/netix/body.html)
  2. [CVE-2020-14882/14883: Weblogic ConSole HTTP 协议代码执行漏洞POC公开通告](https://cert.360.cn/warning/detail?id=1809357283e3a9bb3af3d8b9cbea70d2)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360CERT安全通告** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/221752](/post/id/221752)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [Weblogic](/tag/Weblogic)

 **+1** __4赞

 __收藏

![](https://p3.ssl.qhmsg.com/dm/200_200_100/t013be54b59d8ac5fe6.jpg)
360CERT安全通告

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

