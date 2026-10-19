# Struts2 漏洞分析系列 - S2-007/类型转换到RCE

阅读量 **160093**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-12-07 10:30:15

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t015d522b9523c46f5d.png)

## 0x00 漏洞概述

S2-007的漏洞原理是在处理类型转换的错误时会存入错误到内存中，在后续调用流程中触发OGNL表达式注入。

**影响版本：2.0.0 – 2.2.3**

**复现版本：2.2.3**

官方issue地址：<https://cwiki.apache.org/confluence/display/WW/S2-007>

## 0x01 环境搭建

由于本漏洞发生在Bean中某个Property类型转换时，因此需要我们编写一个Action类：

    
    
    import com.opensymphony.xwork2.ActionSupport;
    
    public class LoginAction extends ActionSupport {
        private String username;
        private String password;
        private int age;
    
        public String getUsername() {
            return username;
        }
    
        public String getPassword() {
            return password;
        }
    
        public int getAge() {
            return age;
        }
    
        public void setUsername(String username) {
            this.username = username;
        }
    
        public void setPassword(String password) {
            this.password = password;
        }
    
        public void setAge(int age) {
            this.age = age;
        }
    
        public String execute() throws Exception{
            if (this.username == null || this.password == null) {
                return "failed";
            }
    
            if (this.username.equals("admin") && this.password.equals("admin")) {
                return "success";
            }
    
            return "failed";
        }
    }
    

接着分别编写两个JSP文件，index.jsp用于模拟用户登陆后的界面，login.jsp用户模拟登陆界面。

index.jsp：

    
    
    <%@ page contentType="text/html;charset=UTF-8" language="java" %>
    <html>
      <head>
        <title>Admin Console</title>
      </head>
      <body>
      Hello admin
      </body>
    </html>
    

login.jsp：

    
    
    <%@ page language="java" contentType="text/html; charset=UTF-8"
             pageEncoding="UTF-8"%>
    <%@ taglib prefix="s" uri="/struts-tags" %>
    <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
    <html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <title>S2-007</title>
    </head>
    <body>
    <h2>S2-007 Demo</h2>
    <p>link: <a href="https://struts.apache.org/docs/s2-007.html">https://struts.apache.org/docs/s2-007.html</a></p>
    
    <s:form action="login">
        <s:textfield name="username" label="username" />
        <s:textfield name="password" label="password" />
        <s:textfield name="age" label="age" />
        <s:submit></s:submit>
    </s:form>
    </body>
    </html>
    

接着编写struts.xml用于定义路由以及成功、失败、错误时的渲染页面：

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    
    <!DOCTYPE struts PUBLIC
            "-//Apache Software Foundation//DTD Struts Configuration 2.0//EN"
            "http://struts.apache.org/dtds/struts-2.0.dtd">
    
    <struts>
        <package name="st2-demo" extends="struts-default">
            <action name="login" class="LoginAction">
                <result name="success">index.jsp</result>
                <result name="failed">login.jsp</result>
                <result name="input">login.jsp</result>
            </action>
        </package>
    </struts>
    

随后配置一下WEB服务器，部署后通过`'+(#application)+'`这个Payload测试是否回显相关信息：

![](https://p2.ssl.qhimg.com/t019c90cc66c2f193fb.jpg)

## 0x02 漏洞分析

###  2.0 上报错误

之前介绍过Struts2存在着许多拦截器用于在请求真正执行到execute方法前的封装，其中就有一个ParametersInterceptor，在这里会将请求中的参数赋到当前请求对应的Bean上，请求中的参数一定是String类型的，但是Bean中的数据类型并不一定是String类型的，这个时候会自动进行一个类型转换，当转换发生错误时，会将错误进行记录。

比如`aaa`必然不可能被转为int类型，但如果是`123（String）`还是可以被转为int类型的，具体转换的逻辑我就不在这展开记录了，本文的重点是错误记录部分。

相关代码：

    
    
    com.opensymphony.xwork2.conversion.impl.XWorkConverter#handleConversionException
    protected void handleConversionException(Map<String, Object> context, String property, Object value, Object object) {
            if (context != null && Boolean.TRUE.equals(context.get("report.conversion.errors"))) {
                String realProperty = property;
                String fullName = (String)context.get("conversion.property.fullName");
                if (fullName != null) {
                    realProperty = fullName;
                }
    
                Map<String, Object> conversionErrors = (Map)context.get("com.opensymphony.xwork2.ActionContext.conversionErrors");
                if (conversionErrors == null) {
                    conversionErrors = new HashMap();
                    context.put("com.opensymphony.xwork2.ActionContext.conversionErrors", conversionErrors);
                }
    
                ((Map)conversionErrors).put(realProperty, value);
            }
    
        }
    

在类型转换过程中触发的异常会通过handleConversionException方法进行搜集，但前提是report.conversion.errors这个键必须为true，默认情况下这个键是为true的。

随后会获取转换出错的property名称以及`com.opensymphony.xwork2.ActionContext.conversionErrors`这个Map并对其进行初始化，最终将property名称以及其对应的值放入这个Map中。

相关调用栈：

    
    
    handleConversionException:438, XWorkConverter (com.opensymphony.xwork2.conversion.impl)
    convertValue:338, XWorkConverter (com.opensymphony.xwork2.conversion.impl)
    convertValue:39, OgnlTypeConverterWrapper (com.opensymphony.xwork2.ognl)
    getConvertedType:1060, OgnlRuntime (ognl)
    getConvertedTypes:1077, OgnlRuntime (ognl)
    getConvertedMethodAndArgs:1103, OgnlRuntime (ognl)
    getAppropriateMethod:1189, OgnlRuntime (ognl)
    callAppropriateMethod:1203, OgnlRuntime (ognl)
    setMethodValue:1474, OgnlRuntime (ognl)
    setPossibleProperty:85, ObjectPropertyAccessor (ognl)
    setProperty:162, ObjectPropertyAccessor (ognl)
    setProperty:27, ObjectAccessor (com.opensymphony.xwork2.ognl.accessor)
    setProperty:2245, OgnlRuntime (ognl)
    setProperty:77, CompoundRootAccessor (com.opensymphony.xwork2.ognl.accessor)
    setProperty:2245, OgnlRuntime (ognl)
    setValueBody:127, ASTProperty (ognl)
    evaluateSetValueBody:220, SimpleNode (ognl)
    setValue:301, SimpleNode (ognl)
    setValue:737, Ognl (ognl)
    setValue:209, OgnlUtil (com.opensymphony.xwork2.ognl)
    trySetValue:173, OgnlValueStack (com.opensymphony.xwork2.ognl)
    setValue:160, OgnlValueStack (com.opensymphony.xwork2.ognl)
    setValue:151, OgnlValueStack (com.opensymphony.xwork2.ognl)
    setParameters:288, ParametersInterceptor (com.opensymphony.xwork2.interceptor)
    doIntercept:199, ParametersInterceptor (com.opensymphony.xwork2.interceptor)
    intercept:98, MethodFilterInterceptor (com.opensymphony.xwork2.interceptor)
    invoke:248, DefaultActionInvocation (com.opensymphony.xwork2)
    doIntercept:207, ParametersInterceptor (com.opensymphony.xwork2.interceptor)
    intercept:98, MethodFilterInterceptor (com.opensymphony.xwork2.interceptor)
    invoke:248, DefaultActionInvocation (com.opensymphony.xwork2)
    intercept:190, StaticParametersInterceptor (com.opensymphony.xwork2.interceptor)
    invoke:248, DefaultActionInvocation (com.opensymphony.xwork2)
    intercept:75, MultiselectInterceptor (org.apache.struts2.interceptor)
    invoke:248, DefaultActionInvocation (com.opensymphony.xwork2)
    intercept:94, CheckboxInterceptor (org.apache.struts2.interceptor)
    invoke:248, DefaultActionInvocation (com.opensymphony.xwork2)
    intercept:243, FileUploadInterceptor (org.apache.struts2.interceptor)
    invoke:248, DefaultActionInvocation (com.opensymphony.xwork2)
    intercept:100, ModelDrivenInterceptor (com.opensymphony.xwork2.interceptor)
    invoke:248, DefaultActionInvocation (com.opensymphony.xwork2)
    intercept:141, ScopedModelDrivenInterceptor (com.opensymphony.xwork2.interceptor)
    invoke:248, DefaultActionInvocation (com.opensymphony.xwork2)
    intercept:270, DebuggingInterceptor (org.apache.struts2.interceptor.debugging)
    invoke:248, DefaultActionInvocation (com.opensymphony.xwork2)
    intercept:145, ChainingInterceptor (com.opensymphony.xwork2.interceptor)
    invoke:248, DefaultActionInvocation (com.opensymphony.xwork2)
    doIntercept:171, PrepareInterceptor (com.opensymphony.xwork2.interceptor)
    intercept:98, MethodFilterInterceptor (com.opensymphony.xwork2.interceptor)
    invoke:248, DefaultActionInvocation (com.opensymphony.xwork2)
    intercept:176, I18nInterceptor (com.opensymphony.xwork2.interceptor)
    invoke:248, DefaultActionInvocation (com.opensymphony.xwork2)
    intercept:164, ServletConfigInterceptor (org.apache.struts2.interceptor)
    invoke:248, DefaultActionInvocation (com.opensymphony.xwork2)
    intercept:190, AliasInterceptor (com.opensymphony.xwork2.interceptor)
    invoke:248, DefaultActionInvocation (com.opensymphony.xwork2)
    intercept:187, ExceptionMappingInterceptor (com.opensymphony.xwork2.interceptor)
    invoke:248, DefaultActionInvocation (com.opensymphony.xwork2)
    execute:52, StrutsActionProxy (org.apache.struts2.impl)
    serviceAction:498, Dispatcher (org.apache.struts2.dispatcher)
    doFilter:434, FilterDispatcher (org.apache.struts2.dispatcher)
    internalDoFilter:239, ApplicationFilterChain (org.apache.catalina.core)
    doFilter:206, ApplicationFilterChain (org.apache.catalina.core)
    invoke:219, StandardWrapperValve (org.apache.catalina.core)
    invoke:106, StandardContextValve (org.apache.catalina.core)
    invoke:501, AuthenticatorBase (org.apache.catalina.authenticator)
    invoke:142, StandardHostValve (org.apache.catalina.core)
    invoke:79, ErrorReportValve (org.apache.catalina.valves)
    invoke:610, AbstractAccessLogValve (org.apache.catalina.valves)
    invoke:88, StandardEngineValve (org.apache.catalina.core)
    service:516, CoyoteAdapter (org.apache.catalina.connector)
    process:1086, AbstractHttp11Processor (org.apache.coyote.http11)
    process:659, AbstractProtocol$AbstractConnectionHandler (org.apache.coyote)
    process:223, Http11NioProtocol$Http11ConnectionHandler (org.apache.coyote.http11)
    doRun:1558, NioEndpoint$SocketProcessor (org.apache.tomcat.util.net)
    run:1515, NioEndpoint$SocketProcessor (org.apache.tomcat.util.net)
    runWorker:1149, ThreadPoolExecutor (java.util.concurrent)
    run:624, ThreadPoolExecutor$Worker (java.util.concurrent)
    run:61, TaskThread$WrappingRunnable (org.apache.tomcat.util.threads)
    run:748, Thread (java.lang)
    

###  2.1 错误处理

前面说到，在ParametersInterceptor进行类型转换时产生的错误会被存入`com.opensymphony.xwork2.ActionContext.conversionErrors`中。

在后续流程中，会使用ConversionErrorInterceptor对前面产生的错误进行处理：

    
    
    com.opensymphony.xwork2.interceptor.ConversionErrorInterceptor#intercept
    public String intercept(ActionInvocation invocation) throws Exception {
            ActionContext invocationContext = invocation.getInvocationContext();
            Map<String, Object> conversionErrors = invocationContext.getConversionErrors();
            ValueStack stack = invocationContext.getValueStack();
            HashMap<Object, Object> fakie = null;
            Iterator i$ = conversionErrors.entrySet().iterator();
    
            while(i$.hasNext()) {
                Entry<String, Object> entry = (Entry)i$.next();
                String propertyName = (String)entry.getKey();
                Object value = entry.getValue();
                if (this.shouldAddError(propertyName, value)) {
                    String message = XWorkConverter.getConversionErrorMessage(propertyName, stack);
                    Object action = invocation.getAction();
                    if (action instanceof ValidationAware) {
                        ValidationAware va = (ValidationAware)action;
                        va.addFieldError(propertyName, message);
                    }
    
                    if (fakie == null) {
                        fakie = new HashMap();
                    }
    
                    fakie.put(propertyName, this.getOverrideExpr(invocation, value));
                }
            }
    
            if (fakie != null) {
                stack.getContext().put("original.property.override", fakie);
                invocation.addPreResultListener(new PreResultListener() {
                    public void beforeResult(ActionInvocation invocation, String resultCode) {
                        Map<Object, Object> fakie = (Map)invocation.getInvocationContext().get("original.property.override");
                        if (fakie != null) {
                            invocation.getStack().setExprOverrides(fakie);
                        }
    
                    }
                });
            }
    
            return invocation.invoke();
        }
    

这里首先通过getConversionErrors获取到所有的错误，随后通过while循环对错误进行处理，首先获取其key&value，接着通过shouldAddError判断value或propertyName是否为空，如果不为空则继续进入if的代码块中。

在if的代码块中会获取到这个错误对应的message以及当前请求对应的Action，并在Action实现了ValidationAware类的情况下调用其addFielderror方法，但是这都不是重点，重点在下面的fakie.put。

注意看，这里调用了`getOverrideExpr`方法对value进行处理：

    
    
    protected Object getOverrideExpr(ActionInvocation invocation, Object value) {
            ValueStack stack = invocation.getStack();
    
            String var4;
            try {
                stack.push(value);
                var4 = "'" + stack.findValue("top", String.class) + "'";
            } finally {
                stack.pop();
            }
    
            return var4;
        }
    

这里首先将value压入栈中，随后通过top语法取出value并在左右两侧进行一个`'`的拼接，最后通过pop方法取出前面压入栈中的value，并且将上面拼接完毕的value返回，此时我们的Payload由`'+(#application)+'`转为了`''+(#application)+''`，可以发现左右两侧的单引号被我们人为闭合了，这里为后面的漏洞利用埋下了一个伏笔。

在value被拼接完后会被放入fakie中，最后在invocation中添加了一个`PreResultListener`，这里取出了前面的fakie，并且会调用setExprOverrides对其进行处理：

    
    
    public void setExprOverrides(Map<Object, Object> overrides) {
            if (this.overrides == null) {
                this.overrides = overrides;
            } else {
                this.overrides.putAll(overrides);
            }
    
        }
    

setExprOverrides会将传入的overrides赋到this.overrides这个属性上，最后会在模板渲染时，通过`lookupForOverrides`方法从this.overrides中取出某个键对应的值。

    
    
    private String lookupForOverrides(String expr) {
            if (this.overrides != null && this.overrides.containsKey(expr)) {
                expr = (String)this.overrides.get(expr);
            }
    
            return expr;
        }
    

![](https://p4.ssl.qhimg.com/t01a202d31c7d61c93a.jpg)

最终会调用getValue方法处理取出来的值，getValue的过程中会触发OGNL表达式解析，这个在S2-001中有过相关介绍，这里就不重复记录了。

完整调用栈：

    
    
    tryFindValue:331, OgnlValueStack (com.opensymphony.xwork2.ognl)
    tryFindValueWhenExpressionIsNotNull:307, OgnlValueStack (com.opensymphony.xwork2.ognl)
    findValue:293, OgnlValueStack (com.opensymphony.xwork2.ognl)
    findValue:350, OgnlValueStack (com.opensymphony.xwork2.ognl)
    translateVariables:196, TextParseUtil (com.opensymphony.xwork2.util)
    translateVariables:115, TextParseUtil (com.opensymphony.xwork2.util)
    translateVariables:88, TextParseUtil (com.opensymphony.xwork2.util)
    findValue:378, Component (org.apache.struts2.components)
    evaluateParams:769, UIBean (org.apache.struts2.components)
    end:510, UIBean (org.apache.struts2.components)
    doEndTag:42, ComponentTagSupport (org.apache.struts2.views.jsp)
    _jspx_meth_s_005ftextfield_005f2:18, login_jsp (org.apache.jsp)
    _jspx_meth_s_005fform_005f0:18, login_jsp (org.apache.jsp)
    _jspService:14, login_jsp (org.apache.jsp)
    service:70, HttpJspBase (org.apache.jasper.runtime)
    service:725, HttpServlet (javax.servlet.http)
    service:431, JspServletWrapper (org.apache.jasper.servlet)
    serviceJspFile:396, JspServlet (org.apache.jasper.servlet)
    service:340, JspServlet (org.apache.jasper.servlet)
    service:725, HttpServlet (javax.servlet.http)
    internalDoFilter:291, ApplicationFilterChain (org.apache.catalina.core)
    doFilter:206, ApplicationFilterChain (org.apache.catalina.core)
    doFilter:52, WsFilter (org.apache.tomcat.websocket.server)
    internalDoFilter:239, ApplicationFilterChain (org.apache.catalina.core)
    doFilter:206, ApplicationFilterChain (org.apache.catalina.core)
    invoke:721, ApplicationDispatcher (org.apache.catalina.core)
    processRequest:466, ApplicationDispatcher (org.apache.catalina.core)
    doForward:391, ApplicationDispatcher (org.apache.catalina.core)
    forward:318, ApplicationDispatcher (org.apache.catalina.core)
    doExecute:157, ServletDispatcherResult (org.apache.struts2.dispatcher)
    execute:186, StrutsResultSupport (org.apache.struts2.dispatcher)
    executeResult:373, DefaultActionInvocation (com.opensymphony.xwork2)
    invoke:277, DefaultActionInvocation (com.opensymphony.xwork2)
    doIntercept:263, ValidationInterceptor (com.opensymphony.xwork2.validator)
    doIntercept:68, AnnotationValidationInterceptor (org.apache.struts2.interceptor.validation)
    intercept:98, MethodFilterInterceptor (com.opensymphony.xwork2.interceptor)
    invoke:248, DefaultActionInvocation (com.opensymphony.xwork2)
    intercept:133, ConversionErrorInterceptor (com.opensymphony.xwork2.interceptor)
    invoke:248, DefaultActionInvocation (com.opensymphony.xwork2)
    doIntercept:207, ParametersInterceptor (com.opensymphony.xwork2.interceptor)
    intercept:98, MethodFilterInterceptor (com.opensymphony.xwork2.interceptor)
    invoke:248, DefaultActionInvocation (com.opensymphony.xwork2)
    doIntercept:207, ParametersInterceptor (com.opensymphony.xwork2.interceptor)
    intercept:98, MethodFilterInterceptor (com.opensymphony.xwork2.interceptor)
    invoke:248, DefaultActionInvocation (com.opensymphony.xwork2)
    intercept:190, StaticParametersInterceptor (com.opensymphony.xwork2.interceptor)
    invoke:248, DefaultActionInvocation (com.opensymphony.xwork2)
    intercept:75, MultiselectInterceptor (org.apache.struts2.interceptor)
    invoke:248, DefaultActionInvocation (com.opensymphony.xwork2)
    intercept:94, CheckboxInterceptor (org.apache.struts2.interceptor)
    invoke:248, DefaultActionInvocation (com.opensymphony.xwork2)
    intercept:243, FileUploadInterceptor (org.apache.struts2.interceptor)
    invoke:248, DefaultActionInvocation (com.opensymphony.xwork2)
    intercept:100, ModelDrivenInterceptor (com.opensymphony.xwork2.interceptor)
    invoke:248, DefaultActionInvocation (com.opensymphony.xwork2)
    intercept:141, ScopedModelDrivenInterceptor (com.opensymphony.xwork2.interceptor)
    invoke:248, DefaultActionInvocation (com.opensymphony.xwork2)
    intercept:270, DebuggingInterceptor (org.apache.struts2.interceptor.debugging)
    invoke:248, DefaultActionInvocation (com.opensymphony.xwork2)
    intercept:145, ChainingInterceptor (com.opensymphony.xwork2.interceptor)
    invoke:248, DefaultActionInvocation (com.opensymphony.xwork2)
    doIntercept:171, PrepareInterceptor (com.opensymphony.xwork2.interceptor)
    intercept:98, MethodFilterInterceptor (com.opensymphony.xwork2.interceptor)
    invoke:248, DefaultActionInvocation (com.opensymphony.xwork2)
    intercept:176, I18nInterceptor (com.opensymphony.xwork2.interceptor)
    invoke:248, DefaultActionInvocation (com.opensymphony.xwork2)
    intercept:164, ServletConfigInterceptor (org.apache.struts2.interceptor)
    invoke:248, DefaultActionInvocation (com.opensymphony.xwork2)
    intercept:190, AliasInterceptor (com.opensymphony.xwork2.interceptor)
    invoke:248, DefaultActionInvocation (com.opensymphony.xwork2)
    intercept:187, ExceptionMappingInterceptor (com.opensymphony.xwork2.interceptor)
    invoke:248, DefaultActionInvocation (com.opensymphony.xwork2)
    execute:52, StrutsActionProxy (org.apache.struts2.impl)
    serviceAction:498, Dispatcher (org.apache.struts2.dispatcher)
    doFilter:434, FilterDispatcher (org.apache.struts2.dispatcher)
    internalDoFilter:239, ApplicationFilterChain (org.apache.catalina.core)
    doFilter:206, ApplicationFilterChain (org.apache.catalina.core)
    invoke:219, StandardWrapperValve (org.apache.catalina.core)
    invoke:106, StandardContextValve (org.apache.catalina.core)
    invoke:501, AuthenticatorBase (org.apache.catalina.authenticator)
    invoke:142, StandardHostValve (org.apache.catalina.core)
    invoke:79, ErrorReportValve (org.apache.catalina.valves)
    invoke:610, AbstractAccessLogValve (org.apache.catalina.valves)
    invoke:88, StandardEngineValve (org.apache.catalina.core)
    service:516, CoyoteAdapter (org.apache.catalina.connector)
    process:1086, AbstractHttp11Processor (org.apache.coyote.http11)
    process:659, AbstractProtocol$AbstractConnectionHandler (org.apache.coyote)
    process:223, Http11NioProtocol$Http11ConnectionHandler (org.apache.coyote.http11)
    doRun:1558, NioEndpoint$SocketProcessor (org.apache.tomcat.util.net)
    run:1515, NioEndpoint$SocketProcessor (org.apache.tomcat.util.net)
    runWorker:1149, ThreadPoolExecutor (java.util.concurrent)
    run:624, ThreadPoolExecutor$Worker (java.util.concurrent)
    run:61, TaskThread$WrappingRunnable (org.apache.tomcat.util.threads)
    run:748, Thread (java.lang)
    

分析到这里，其实可以发现一个问题，首先网上流传的Payload，也就是’+(#application)+’，这里可以换种容易理解的写法，即`' +
#{application} + '`，这样也许大家会更容易分清楚其中OGNL表达式的部分。

## 0x03 修复方案

S2-007的修复方式也是十分的简单粗暴，废话不多说，直接看DIFF：

![](https://p5.ssl.qhimg.com/t01022f2b542028026f.jpg)

可以发现，修复方式十分粗暴，就是通过StringEscapeUtils.escapeJava对其进行了一个转义，并且将原先左右两侧的单引号换为了双引号，此时我们则没有办法逃逸这左右两侧的引号了，因为`"`会被转义为`\"`。

## 0x04 一个小问题

在最开始的时候写了，我测试的时候发现某些低版本用不了，这是因为在某些低版本中把`XWorkConverter`这个类给去掉了，因此没有上报错误的这么一个流程了，自然也就无法产生后续错误处理时的漏洞。所以如果想稳定复现，最好还是使用
**2.2.3** 版本进行复现。

## 0x05 吐槽

在分析这个漏洞时自然是参考了网上的一些文章，比如：

  * <https://github.com/xhycccc/Struts2-Vuln-Demo/tree/master/s2-007>
  * <https://xz.aliyun.com/t/2684>

其中Github中的参考链接是第二个链接，然而实际上第二篇文章的漏洞分析部分有着些许问题，比如这个漏洞压根就不需要编写什么validate.xml，并且实际上触发OGNL表达式的也不是invoke这里，而是后续的调用中。

但这样错误的文章，也还是被抄来抄去的，这里只作吐槽，希望大家复现漏洞时能够在真正了解漏洞之后再去COPY，否则很容易被没复现过这个漏洞的人误解。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **tlmn** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/261741](/post/id/261741)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Java](/tag/Java)
  * [Struts2](/tag/Struts2)

 **+1** __3赞

 __收藏

![](https://p3.ssl.qhimg.com/t01b9a70454dd1d265f.png) tlmn

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

