## 前言

 **2020年1月15日，Oracle官方发布2020年1月关键补丁更新公告CPU（CriticalPatch
Update），其中CVE-2020-2551的漏洞，漏洞等级为高危，CVVS评分为9.8分，漏洞利用难度低。影响范围为10.3.6.0.0,
12.1.3.0.0, 12.2.1.3.0, 12.2.1.4.0。**

## 漏洞浅析

从Oracle
官方的公告中看出该漏洞存在于Weblogic核心组件，影响的协议为IIOP协议。该漏洞依然是由于调用远程对象的实现存在缺陷，导致序列化对象可以任意构造，在使用之前未经安全检查，导致恶意代码被执行。通过分析，该漏洞的PoC构造与历史漏洞CVE-2017-3241、CVE-2018-3191都有一些相似的地方，而后在构造PoC的时候也可以发现。

## 简单了解下一些名词概念：

 **IIOP：** IIOP 是 CORBA 的通信协议。它定义通过 CORBA 客户端与服务器之间的连线发送位的方式。

 **CORBA：** 公用对象请求代理（调度）程序体系结构（Common Object Request Broker Architecture），缩写为
CORBA，CORBA 是由对象管理组(OMG) 开发的标准分布式对象体系结构。远程对象的接口在平台无关接口定义语言 (IDL) 中进行说明。实现从 IDL
到特定编程语言的映射，将该语言绑定到 CORBA/IIOP。Java Standard Edition CORBA/IIOP 实现被称为 JavaIDL。
与 IDL 到 Java (idlj) 编译器一起，Java IDL 可用于定义、实现和访问 Java 编程语言中的 CORBA 对象。

 **RMI-IIOP：** Java 程序员在编程时需要在分布式编程解决方案RMI 和 CORBA/IIOP (Java IDL)
之间进行选择。现在，可以通过遵循一些限制，可以使得RMI 服务器对象可以使用 IIOP 协议，并与任何语言编写的 CORBA
客户端对象进行通信。该解决方案被称为 RMI-IIOP。 RMI-IIOP 结合了 RMI 的易用性与 CORBA 的跨语言互操作性。

具体更多的相关概念以及weblogic的IIOP的相关知识，可以查阅官方文档，这里不做过多解释。

通过网上放出的漏洞PoC利用截图，我们可以根据异常的抛出行，大概推断出漏洞的出发点，这里不难发现最后的异常点抛在了这里weblogic.utils.io.ObjectStreamClass

![](https://image.3001.net/images/20200221/1582267489_5e4f7c6133b35.png!small)

那么我们根据流出的图，一步步逆向分析回去，向上跟踪哪个方法调用了他它，可以发现这里weblogic.corba.utils.
ValueHandlerImpl最后调用了readObject方法：

![](https://image.3001.net/images/20200221/1582267530_5e4f7c8a3df63.png!small)

再继续往上走，发现同方法的readValue函数这里调用了上面的方法：

![](https://image.3001.net/images/20200221/1582267546_5e4f7c9ac8440.png!small)

继续追踪分析，可以发现主要的函数weblogic.iiop. IIOPInputStream方法中存在问题，到这里就基本很清晰了：

![](https://image.3001.net/images/20200221/1582267619_5e4f7ce3b4363.png!small)

![](https://image.3001.net/images/20200221/1582267619_5e4f7ce3c682d.png!small)

根据官方的描述，攻击者可以通过 IIOP 协议远程访问 Weblogic Server
服务器上的远程接口，传入恶意数据，从而获取服务器权限并在未授权情况下远程执行任意代码。Weblogic默认的IIOP协议端口为7001，默认开启。根据漏洞披露的信息这个漏洞是JNDI注入。需要寻找到weblogic中的工厂类，进行封装发送，通过查阅官方的一些手册，可以使用weblogic.jndi.WLInitialContextFactory该工厂方法。

 ***本文作者：WebRAY，转载请注明来自FreeBuf.COM**

