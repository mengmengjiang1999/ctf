### **1.OGNL** **是什么，它有什么用**

OGNL是Object-garph Navigation Language的缩写，它是一种功能强大的 **表达式语言** ，比EL更加强大。

Struts2将ognl表达式语言，集成到struts2框架中，作为他的默认表达式语言。

 **OGNL提供的五大类功能:**

1.支持对象方法的调用，如xxx.doSomeSpecial();

2.支持类静态的方法调用和值访问

3.支持OGNL上下文(OGNL context)和 **actionContext** (重点:操作ValueStack值栈)

4.支持复制操作和表达式串联

5.操作集合对象

###  **问题:**

 **1.valueStack** **是什么，有什么用** **?**

valueStack是值栈

它是什么，我们从两个方面来说

1.从技术角度上来说，ValueStack就是一个接口

 ******* **我所理解的就是将** **action** **对象呈现于** **web** **界面的一个接口** **,** **存储**
**action** **对象并将其呈现**

2.从使用角度来说，是一个容器

 ******* **我所理解的就是将** **action** **乱七八糟的一堆数据放入值栈中** **,** **感觉和上下文对象很像**

###  **2.ognl** **语句与** **valueStack** **有什么关系** **?**

在呈现界面通过ognl表达式将valueStack中的数据呈现出来

###  **3.** **什么是** **OgnlValueStack**

1.OgnlValueStack为ValueStack的一个 **实现类**

2.每一个Action实例都有一个ValueStack对象，一个请求对应一个ValueStack对象(包括一个请求，一个ruquest，一个action，一个valueStack)

3.而一个action的生命周期同request一样,在请求开始时开始，在响应结束时消散

4.值栈存储了在其中保存当前action和其他相关对象(request,session,application,parameters)

 ******* **即我之前所补充的乱七八糟**

###  **4.valueStack** **的内部结构**

一个是root其实就是一个Arrlylist(队列链表)就是action的相关信息

还有一个就是context其实就是一个MAP各种映射，常见web对象，等价于ognlContext上下文对象，ognlContext里面装有Root

但是Struts2的root在list集合中，list中的root但是在map中也有引用，所以Map集合是struts2中如假包换的OGNLCONTEXT上下文。。。。。

 ******* **概念有点混** **,** **主要自己理解** **,** **我的理解也不一定对**

###

###  **5.** **什么是上下文表达式** **(ContextMap)**

<contextmap是struts2封装好的一次请求可能出现的最大的数据容器>

且是一个Map结构 **(** **映射结构** **:** **即保存两组值** **,** **一组为** **key,** **一组为**
**value)**

例{String:Object}

里面的数据为:

  * application：ServletContext应用对象
  * session：HttpSession
  * valueStack：值栈 List类型
  * action：当前执行的动作类相关数据 【不是Map类型】
  * request：HttpServletRequest
  * parameters：请求参数
  * attr：四大域的属性数据

除了ValueStack和action不是Map类型的，其他的都是Map类型{String : Object}

ActionContext就是action对象的上下文!!!!!!!!!!!!

###  **6.ActionContext** **与** **ValueStrack** **的区别**

ActionContext为Struts提供数据环境，维护着一个Map结构,ActionContext中封装了servlet对象,从而将Action与Servlet解耦
(即Action无需依赖任何Servlet API). ActionContext是一个只在当前线程中可用的对象，即它存储在
ThreadLocal中，它用来存放一些同当前的action密切相关的信息。使用它可以在所有服务于当前请求的对象之间共享信息。在interceptor，action，及result中均可访问该对象。

 **ActionContext** **就是应用上下文**
，可以通过他来访问session对象等，可以保存的数据，在这个应用中都可以访问该数据。通常用于还回一个session对象。

ValueStack中的每一个元素都是 **根对象** ,Action位于ValueStack的最顶层.ValueStack
是OGNL表达式语言中的值栈，用来封装继承了action接口的类的属性值，在同一个请求范围类有效，在页面中直接通过表达式${属性名}就可以取出。

 ******* **我所理解的就是** **,ActionContext** **放着** **Action** **相关信息**

 **** **但是** **Valuestack** **存放的就是很多根对象** **,action** **是其中之一**

##  **如果理解有差，欢迎大神来指点，嘿嘿嘿。**

###  **7.** **表达式语言** **(EL** **同** **OGNL** **理解** **)**

 **表达式语言**

JSP表达式语言（EL）使得访问存储在JavaBean中的数据变得非常简单。JSP EL既可以用来创建算术表达式也可以用来创建逻辑表达式。在JSP
EL表达式内可以使用整型数，浮点数，字符串，常量true、false，还有null。

 **一个简单的语法**

典型的，当您需要在JSP标签中指定一个属性值时，只需要简单地使用字符串即可：

 **< jsp:setProperty name="box" property="perimeter" value="100"/>**

JSP EL允许您指定一个表达式来表示属性值。一个简单的表达式语法如下：

 **${expr}**

其中，expr指的是表达式。在JSP EL中通用的操作符是 .和 {}。这两个操作符允许您通过内嵌的JSP对象访问各种各样的JavaBean属性。

举例来说，上面的 **< jsp:setProperty>**标签可以使用表达式语言改写成如下形式：

 **< jsp:setProperty name="box" property="perimeter"  
value="** **${2*box.width+2*box.height}** **"/ >**

当JSP编译器在属性中见到" **${}"格式后，它会产生代码来计算这个表达式，并且产生一个替代品来代替表达式的值。**

您也可以在标签的模板文本中使用表达式语言。比如<jsp:text>标签简单地将其主体中的文本插入到JSP输出中：

 **< jsp:text>  
<h1>Hello JSP!</h1>  
</jsp:text>**

现在，在<jsp:text>标签主体中使用表达式，就像这样：

 **< jsp:text>  
Box Perimeter is: ${2*box.width + 2*box.height}  
</jsp:text>**

在EL表达式中可以使用圆括号来组织子表达式。比如${(1 + 2) * 3}等于9，但是${1 + (2 * 3)} 等于7。

想要 **停用** 对EL表达式的评估的话，需要使用page指令将isELIgnored属性值设为 **true** ：

<%@ page isELIgnored ="true|false" %>

这样，EL表达式就会被忽略。若设为false，则容器将会计算EL表达式。

 **EL中的基础操作符**

EL表达式支持大部分Java所提供的算术和逻辑操作符：

 **操作符**

|

 **描述**  
  
---|---  
  
.

|

访问一个Bean属性或者一个映射条目  
  
[]

|

访问一个数组或者链表的元素  
  
( )

|

组织一个子表达式以改变 **优先级**  
  
+

|

加  
  
-
|

减或负  
  
*

|

乘  
  
/ or div

|

除  
  
% or mod

|

取模  
  
== or eq

|

测试是否相等  
  
!= or ne

|

测试是否不等  
  
< or lt

|

测试是否小于  
  
> or gt

|

测试是否大于  
  
<= or le

|

测试是否小于等于  
  
>= or ge

|

测试是否大于等于  
  
&& or and

|

测试逻辑与  
  
|| or or

|

测试逻辑或  
  
! or not

|

测试取反  
  
empty

|

测试是否空值

