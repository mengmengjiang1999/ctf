**Spring Data** 是一个用于简化数据库访问，并支持云服务的开源框架，其主要目标是使数据库的访问变得方便快捷。 **Spring Data
Commons** 是Spring Data下所有子项目共享的基础框架。Spring的核心是控制反转（IoC）和面向切面（AOP），相比Struts
2框架绝大部分的安全漏洞都都是由于OGNL产生，而自从Spring引入SpEL，也引起很多安全漏洞，今天利用 **Spring Data Commons
（CVE-2018-1273）** 作为案例和大家聊一聊。

## **01 漏洞描述**

Spring Data
Commons（1.13至1.13.10之前的版本，2.0至2.0.5的版本以及较旧的不受支持的版本）包含由于特殊元素的不正确中和而导致的属性绑定器漏洞。未经身份验证的远程恶意用户（或攻击者）可以针对Spring
Data REST支持的HTTP资源提供特制的请求参数，或者使用Spring Data的基于投影的请求有效负载绑定帽可能导致远程执行代码攻击。

## **02 源码分析**

Spring MVC框架会处理来自前端的页面的请求，并根据请求进行数据的封装，处理前端页面的请求暂不赘述，我们现在主要探讨对数据的封装处理，因为Spring
Data
Commons框架在做数据封装处理的时候产生了漏洞，进入org.springframework.web.method.support.InvocableHandlerMethod类，进入getMethodArgumentValues方法，如下图所示：

![v2-8e6e1379990429e4926ddaa739bfa00e_1440w.jpg](https://image.3001.net/images/20200813/1597311941.jpg!small)

如上图所示红框所示位置，resolveArgument对请求参数进行了进一步处理，进入org.springframework.web.method.support.HandlerMethodArgumentResolverComposite类的resolveArgument方法，如下图所示：

![v2-01bd7129326e8c3e8025830a3e977cee_1440w.jpg](https://image.3001.net/images/20200813/1597311942.jpg!small)

由于resolveArgument方法，并没有明显的逻辑，定位到resolve.resolveArgument行进入到org.springframework.web.method.annotation.ModelAttributeMethodProcessor类的resolveArgument方法，如下图所示：

![preview](https://image.3001.net/images/20200814/1597394891.jpg!small)

进入到resolveArgument方法的第132行代码，如下图所示，该行代码创建attribute的实例对象，并实现具体的数据绑定功能。

![v2-302144c49ba45a88dd62e3b82acd6213_1440w.jpg](https://image.3001.net/images/20200813/1597311943.jpg!small)

进入org.springframework.data.web.ProxyingHandlerMethodArgumentResolver类的createAttribute方法，createAttribute方法中调用MapDataBinder类进行传入数据的数据绑定。

![preview](https://image.3001.net/images/20200814/1597394892.jpg!small)

定位到binder.bind语句进入bind方法，看实现的具体逻辑，进入到org.springframework.web.bind.WebDataBinder类的bind方法，如下图所示：

![v2-09362a5323a5879fe79f4686a79b2c1d_1440w.jpg](https://image.3001.net/images/20200813/1597311944.jpg!small)

因为WebDataBinder类继承了DataBinder类，所以super.doBind语句是将参数传递给WebDataBinder类的doBinder方法，进入DataBinder类的doBinder方法，如下图所示，在该方法中前两句是校验语句，applyPropertyValues方法是具体的处理逻辑。

![v2-697e1f292e03c41cd76a0188f6760000_1440w.png](https://image.3001.net/images/20200813/1597311944.png!small)

进入org.springframework.validation.DataBinder类的applyPropertyValues方法，如下图所示：

![v2-cc822828fe201f8cd197fe41af5e2b8f_1440w.jpg](https://image.3001.net/images/20200813/1597311944.jpg!small)

如上图所示箭头位置，继续进入org.springframework.beans.AbstractPropertyAccessor类的setPropertyValues方法，如下图所示：

![v2-4152b8d9adab0ff4f3ff68e61acd66b1_1440w.jpg](https://image.3001.net/images/20200813/1597311946.jpg!small)

定位到该方法的第97行，如下图所示：

![preview](https://image.3001.net/images/20200814/1597394893.jpg!small)

进入setPropertyValue方法，如下图所示：

![v2-d2ffd721effa802ca72920f3282784de_1440w.png](https://image.3001.net/images/20200813/1597311946.png!small)

继续跟踪进入org.springframework.data.web.MapDataBinder类的setPropertyValue方法，如下图所示：

![v2-a2b4ccb8790375ca09fa3ead62a8c663_1440w.jpg](https://image.3001.net/images/20200813/1597311947.jpg!small)

在serPropertyValue方法中对前端出入的参数进行处理，定位到setPropertyValue方法中的第182行代码，如下图所示：

![preview](https://image.3001.net/images/20200814/1597394893.jpg!small)

第182行代码中使用Spring 的SpEL表达式对外部的参数进行处理，但是并没有对参数进行进行有效的校验，所示第182行代码是漏洞注入点。

## **03 漏洞复现**

抓取前端传入后台的数据包，如下图所示：

![v2-2161c828a8303cfaa9403f4e38c3e47a_1440w.jpg](https://image.3001.net/images/20200813/1597311948.jpg!small)

构造payload,如下图所示：

![preview](https://image.3001.net/images/20200814/1597394895.jpg!small)

响应结果，如下图所示：

![v2-424273dab6751d28515ef80c81196328_1440w.jpg](https://image.3001.net/images/20200813/1597311949.jpg!small)

## **04 总结与修复**

本次漏洞问题出现在 Spring Data
Commons中。该漏洞是由前端参数传入后台，后台框架使用SpEL表达式处理未校验的恶意字符串所引起的，因此建议采取IP白名单对IP进行限制，或者升级框架到最新版本。将Spring
Data Commons框架的版本由2.0.x升级到2.0.6，1.13.x的用户升级到1.13.11。

