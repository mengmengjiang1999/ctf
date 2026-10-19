**作者：天融信阿尔法实验室  
公众号：<https://mp.weixin.qq.com/s/9ki_-IjFKybFUx-6FZ-A5g>**

### 一、前言

2020年8月13日,Apache官方发布了一则公告,该公告称Apache
Struts2使用某些标签时,会对标签属性值进行二次表达式解析,当标签属性值使用了`%{skillName}`并且`skillName`的值用户可以控制,就会造成`OGNL`表达式执行。

### 二、漏洞复现

我这里选用的测试环境 `Tomcat 7.0.72`、`Java 1.8.0_181`、`Struts 2.2.1`,受影响的标签直接使用官网公告给出的例子

    
    
    <s:url var="url" namespace="/employee" action="list"/><s:a id="%{payload}" href="%{url}">List available Employees</s:a>

测试漏洞URL

`http://localhost:8088/S2-059.action?payload=%25{3*3}`

在`s2-029`中由于调用了`completeExpressionIfAltSyntax`方法会自动加上`"%{" + expr +
"}"`,所以`payload`不用带`%{}`,在`s2-029`的`payload`里加上`%{}`就是`s2-059`的`payload`,具体原因看下面的分析。

### 三、漏洞分析

根据官网公告的漏洞描述及上面的测试过程可以知道,这次漏洞是由于标签属性值进行二次表达式解析产生的。`struts2 jsp`
标签解析是`org.apache.struts2.views.jsp.ComponentTagSupport`类的`doStartTag`和`doEndTag`方法。`debug`跟下
`doStartTag`方法。

![image-20200818174847155](https://images.seebug.org/content/images/2020/08/21/1597975843000-image-20200818174847155.png-w331s)

跟下`populateParams`方法

`org/apache/struts2/views/jsp/ui/AnchorTag.class`

![image-20200818174944494](https://images.seebug.org/content/images/2020/08/21/1597975843000-image-20200818174944494.png-w331s)

这里又去调用了父类的`populateParams`方法,接着调用`org/apache/struts2/views/jsp/ui/AbstractUITag.class`类的`populateParams`方法

![image-20200818175116276](https://images.seebug.org/content/images/2020/08/21/1597975844000-image-20200818175116276.png-w331s)

可以看到这里有给setId赋值,跟下setId方法,`org/apache/struts2/components/UIBean.class`

![image-20200818175306449](https://images.seebug.org/content/images/2020/08/21/1597975844000-image-20200818175306449.png-w331s)

由于id不为null,会执行`this.findString`方法,接着跟下.`org/apache/struts2/components/Component.class`

![image-20200818175715249](https://images.seebug.org/content/images/2020/08/21/1597975844000-image-20200818175715249.png-w331s)

![image-20200818175756449](https://images.seebug.org/content/images/2020/08/21/1597975844000-image-20200818175756449.png-w331s)

`altSyntax`默认开启,
所以`this.altSyntax()`会返回`true`,`toType`的值传过来是`String.class`,`if`条件成立会执行到`TextParseUtil.translateVariables('%',
expr, this.stack)`

![image-20200818182330520](https://images.seebug.org/content/images/2020/08/21/1597975844000-image-20200818182330520.png-w331s)

可以看到这里是首先截取去掉`%{}`字符,然后从`stack`中寻找`payload`参数,传输的`payload`参数是`%{3*2}`,这里会得到这个值。

执行完`populateParams`方法可以得知这个方法是对属性进行初始化赋值操作。接着跟下`start`方法

![image-20200818182850654](https://images.seebug.org/content/images/2020/08/21/1597975844000-image-20200818182850654.png-w331s)

`org/apache/struts2/components/Anchor.class`的`start`方法调用了父类`org/apache/struts2/components/ClosingUIBean.class`的`start`方法

![image-20200818190923090](https://images.seebug.org/content/images/2020/08/21/1597975844000-image-20200818190923090.png-w331s)

在接着跟下`org/apache/struts2/components/UIBean.class$evaluateParams`方法

![image-20200818191144959](https://images.seebug.org/content/images/2020/08/21/1597975844000-image-20200818191144959.png-w331s)

接着调用了`populateComponentHtmlId`方法

![image-20200818191311239](https://images.seebug.org/content/images/2020/08/21/1597975844000-image-20200818191311239.png-w331s)

在看下`findStringIfAltSyntax`方法的实现

`org/apache/struts2/components/Component.class$findStringIfAltSyntax`

![image-20200818191825377](https://images.seebug.org/content/images/2020/08/21/1597975845000-image-20200818191825377.png-w331s)

可以看到这里又执行了一次`TextParseUtil.translateVariables`方法.

![image-20200818192259407](https://images.seebug.org/content/images/2020/08/21/1597975845000-image-20200818192259407.png-w331s)

整个过程跟`S2-029`和`S2-036`漏洞产生的原因一样,都是由标签属性二次表达式解析造成漏洞。分析完漏洞产生原因后,我查看了`UIBean
class`相关代码,并没有发现除`id`外其它标签属性值可以这样利用。

### 四、总结

此次漏洞需要开启`altSyntax`功能,只能是在标签`id`属性中存在表达式,并且参数还可以控制,这种场景在实际开发中非常少见,危害较小。

### 五、参考链接

<https://cwiki.apache.org/confluence/display/WW/S2-059>

<http://blog.topsec.com.cn/struts2%e6%bc%8f%e6%b4%9es2-029%e5%88%86%e6%9e%90/>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1302/>

