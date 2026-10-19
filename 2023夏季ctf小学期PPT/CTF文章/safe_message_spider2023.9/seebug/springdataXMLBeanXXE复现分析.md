作者：spoock  
作者博客：<https://blog.spoock.com/2018/05/16/cve-2018-1259/>

#### 漏洞信息

看pivotal发布的漏洞信息如下:
![](https://images.seebug.org/content/images/2018/05/e0cd496f-36e9-413f-92ac-e7151d604806.jpg-w331s)

通过发布的漏洞信息可以知道，漏洞组件是在`XMLBeam`1.4.14或者是更早的版本，主要原因是没有限制XML文件外部实体引用。而`Spring Data
Commons`的某些版本中使用了存在漏洞的`XMLBeam`组件。

#### 环境搭建

下载demo环境

    
    
    git clone https://github.com/spring-projects/spring-data-examples.git
    cd spring-data-examples
    git checkout ad2b77e

使用IDEA打开其中的`web/projection`项目，修改其中的`pom.xml`文件: 修改spring-data-commons的版本

    
    
    <dependency>
        <groupId>org.springframework.data</groupId>
        <artifactId>spring-data-commons</artifactId>
        <version>2.0.5.RELEASE</version>
    </dependency>

添加spring-boot的依赖

    
    
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>2.0.0.RELEASE</version>
    </parent>

漏洞组件版本如下:

![](https://images.seebug.org/content/images/2018/05/7ebdad7f-c266-4e14-8760-feebcae3e612.jpg-w331s)

注释`example.users`中`UserControllerClientTests.java`、`UserControllerIntegrationTests.java`中的代码（主要是测试代码，对漏洞环境无影响）。

#### 漏洞复现

使用IDEA启动程序。采用POST方法发送XML的数据：
![](https://images.seebug.org/content/images/2018/05/11dfccab-8c53-4c62-86b2-a80c9d530166.jpg-w331s)

成功地读取了文件。

#### 漏洞分析

通过[漏洞修复commit](https://github.com/SvenEwald/xmlbeam/commit/f8e943f44961c14cf1316deb56280f7878702ee1)发现，对`DefaultXMLFactoriesConfig.java`进行了修改，如下：

  1. 配置了默认的feature ![](https://images.seebug.org/content/images/2018/05/d3cd32b0-3d17-49d4-a7fa-fe52be4456c6.jpg-w331s)

  2. 禁止实体引用、禁止合并多个XML文档。关于XInclude的用法可以参考[XML包含机制](https://www.ibm.com/developerworks/cn/xml/standards/x-xincludespec.html)

![](https://images.seebug.org/content/images/2018/05/f3015af2-df6f-4b85-ab46-73649e3d6025.jpg-w331s)

通过补丁分析，漏洞原因是在于`XMLBeam`漏洞版本中没有限制外部实体。

当我们发送Payload时，是由`example.users.UserController`中的`@PostMapping(value =
"/")`来处理请求：

![](https://images.seebug.org/content/images/2018/05/28362417-f868-414c-90a3-0ec447d2d6d7.jpg-w331s)

其中`user.getFirstname()`已经完成了参数解析并读取`c:/windows/win.ini`中的内容，所以我们发送的Payload在发送到Web应用之前已经由`Spring
Data Commons`对发送的参数进行了解析并绑定到`user`对象上。而`Spring Data
Commons`是利用`XMLBeam`解析XML文件，这样就导致了在Web应用响应请求时已经完成了XML的解析从而造成了XXE漏洞。

通过层层追踪，XML的解析最终是由`org.xmlbeam.ProjectionInvocationHandler:invokeReadProjection()`处理,

![](https://images.seebug.org/content/images/2018/05/da2f9f17-6736-4660-9d5f-1b94f19b25c2.jpg-w331s)

XML的解析是由`Node dataNode = (Node)expression.evaluate(node,
XPathConstants.NODE);`完成，其中`expression`就有xpath表达式，`node`表示当前的document。最终解析完毕之后，`data`返回的就是`win.ini`的内容。

![](https://images.seebug.org/content/images/2018/05/e5cc23ea-1e99-44e7-b5de-24ab5ce88070.jpg-w331s)

当我们更新`XMLBeam`的版本至1.4.15时，即设置了`instance.setXIncludeAware(this.isXIncludeAware);instance.setExpandEntityReferences(this.isExpandEntityReferences);`。分析`invokeReadProjection()`函数

![](https://images.seebug.org/content/images/2018/05/05c80dde-26bc-4499-a7ec-6fce00558018.jpg-w331s)

可以看到`expression`中的xpath表达式保持不变，但是`data`此时的结果已经为空，说明通过设置禁止实体引用就导致了XXE漏洞失效。

其实整个XML的解析与参数整个请求参数的传递并没有关系只和`DefaultXMLFactoriesConfig`的配置有关，所以漏洞分析并不需要跟踪XML文件的解析过程，也不需要通过`Spring
Data Commons`去追踪数据流，只需要了解这个漏洞的本质原因即可。

#### 总结

这个XXE漏洞本质是因`DefaultXMLFactoriesConfig.java`配置不当而导致的，`Spring Data
Commons`的某些版本中恰好使用了含有漏洞的`XMLBeam`组件。这也就引出了一个问题，在Java这种大量使用第三方包的情况下，如何避免因第三方包的漏洞导致自己的应用也受到危害呢？

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/600/>

