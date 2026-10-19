***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

##  **0x0 简介**

 **jexboss是一个使用Python编写的Jboss漏洞检测利用工具，通过它可以检测并利用web-console、jmx-console、JMXInvokerServlet、struc2、Jenkins等漏洞并且可以直接获得一个shell，杀人越货勒索挖矿必备神器。**

起初，攻击者会通过JexBoss工具对JBoss服务器执行侦查，随后利用漏洞并安装SamSam。与其他勒索软件不同，SamSam包含一个通道，让攻击者可实时通过.onion网站与受害者通信。

![图片1.png](https://image.3001.net/images/20180820/1534735675_5b7a353b7366d.png!small)

主要针对以下命令执行漏洞为主：  

**/admin-console**

tested and working in JBoss versions 5 and 6

 **/jmx-console**

tested and working in JBoss versions 4, 5 and 6

 **/web-console/Invoker**

tested and working in JBoss versions 4, 5 and 6

 **/invoker/JMXInvokerServlet**

tested and working in JBoss versions 4, 5 and 6

 **Application Deserialization**

tested and working against multiple java applications, platforms, etc, via
HTTP POST Parameters

 **Servlet Deserialization**

tested and working against multiple java applications, platforms, etc, via
servlets that process serialized objets (e.g. when you see an "Invoker" in a
link)

 **Apache Struts2 CVE-2017-5638**

tested in Apache Struts 2 applications

Github路径如下：

 **<https://github.com/joaomatosf/jexboss>**

##  **0x1 源码分析**

a.检测目标站点的漏洞设置检查的路径：

![图片2.png](https://image.3001.net/images/20180820/1534735708_5b7a355c7b879.png!small)

依次检查漏洞：

> 1.Jenkins
>
> 2.Java Unserializable in Application Parameters
>
> 3.Java Unserializable in viewState
>
> 4.Struts2
>
> 5.JMX Tomcat
>
> 6.JMXInvokerServlet

b.举例/web-console/Invoker通过特定的数据包请求记录下请求的HTTP状态码保存在 r.status变量当中.

![3.png](https://image.3001.net/images/20180820/1534735727_5b7a356fc0cbe.png!small)

c.通过对漏洞检查的payload与返回的状态对结果进行输出，确定漏洞的存在性。

![4.png](https://image.3001.net/images/20180820/1534735746_5b7a3582bc777.png!small)

d.自动化反弹shell。

以下是关于JMXInvokerServlet漏洞的反弹shell的分析，直接调用了一个方法shell_http。

![5.png](https://image.3001.net/images/20180820/1534735762_5b7a3592a9e36.png!small)

Payload的如下：

![6.png](https://image.3001.net/images/20180820/1534735798_5b7a35b6c09c5.png!small)

e.通过上传了一个/jexws4/jexws4.jsp的webshell。

![7.png](https://image.3001.net/images/20180820/1534735920_5b7a36302bc88.png!small)

Jexws4.jsp如下：  

![8.png](https://image.3001.net/images/20180820/1534735933_5b7a363d6feb4.png!small)

f. 解码后为一个带参数的webshel，可以实现命令执行的功能，传递的参数名为ppp。

![9.png](https://image.3001.net/images/20180820/1534735948_5b7a364cb8f74.png!small)

##  **0x2 工具使用**

可以使用 python jexboss.py -h 查看各个参数文档：

![10.png](https://image.3001.net/images/20180820/1534735961_5b7a36592746a.png!small)

使用python jexboss.py -u dsturl可以实现一键拿shell：  

![11.png](https://image.3001.net/images/20180820/1534735975_5b7a366700d7e.png!small)

成功返回一个shell：

![12.png](https://image.3001.net/images/20180820/1534735989_5b7a3675df2c4.png!small)

##  **0x3 结论**

1.夫祸患常积于忽微,而智勇多困于所溺。

2.及时修复漏洞，及时打补丁，及时升级版本。

