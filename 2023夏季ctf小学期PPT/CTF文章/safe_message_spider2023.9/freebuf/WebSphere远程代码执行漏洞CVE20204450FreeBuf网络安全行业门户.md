## **********一、** ** **漏洞分析****

###  ** **1.1 WebSphere 组件**** ** **介绍****

WebSphere 是 IBM 的软件平台。它包含了编写、运行和监视全天候的工业强度的随需应变 Web
应用程序和跨平台、跨产品解决方案所需要的整个中间件基础设施，如服务器、服务和工具。WebSphere Application Server
是该设施的基础，其他所有产品都在它之上运行。WebSphere Process Server 基于 WebSphere Application Server
和 WebSphere Enterprise Service Bus，它为面向服务的体系结构 (SOA)
的模块化应用程序提供了基础，并支持应用业务规则，以驱动支持业务流程的应用程序。

###  ** **1.2 漏洞描述****

2020年6月15日，IBM官方发布了针对CVE-2020-4450漏洞的防御补丁。漏洞产生的原因是IBM WebSphere Application
Server可以允许远程攻击者通过iiop协议传输精心构造的序列化数据，在系统上执行任意代码。

###  ** **1.3 详细分析****

首先梳理一下漏洞利用流程，漏洞触发入口位于com.ibm.ws.Transaction.JTS.TxServerInterceptor#receive_request方法。

![](https://image.3001.net/images/20200818/1597714666.png!small)

控制 serviceContext和serviceContext.context_data参数值不为null，保证

    
    
    boolean validOtsContext = serviceContext != null && serviceContext.context_data != null;

中的 validOtsContext 为true，从而进入下图所示的if代码块

![](https://image.3001.net/images/20200818/1597715215.png!small)

在代码块中，执行TxInterceptorHelper.demarshalContext(serviceContext.context_data,
(ORB)((LocalObject)sri)._orb())方法。

![](https://image.3001.net/images/20200818/1597715231.png!small)

首先调用createCDRInputStream创建EncoderInputStream（CDRInputStream的子类）。创建PropagationContext对象，将数据流中的属性读取到上下文中。这里重点关注

    
    
    propContext.implementation_specific_data = inputStream.read_any();

此段代码会调用EncoderInputStream#read_any方法，进而调用CDRReader#read_any方法进行反序列化操作。

![](https://image.3001.net/images/20200818/1597715282.png!small)

参考Zero Day
Initiative和iswin文章，CVE-2020-4450漏洞使用WSIFPort_EJB类进行gadget构造，同时通过反射，获取com.ibm.rmi.iiop.Connection#setConnectionContexts方法，添加构造的ServiceContext，满足上述流程的前提条件，为serviceContext和serviceContext.context_data赋值。

通过构造context_data数据，在demarshalContext方法解析时触发构造中的恶意数据，构造方式参考marshalContext方法

![](https://image.3001.net/images/20200818/1597715368.png!small)

模拟序列化流程，将构造的恶意数据传入result。

进入gadget使用的WSIFPort_EJB类，首先跟进readObject方法

![](https://image.3001.net/images/20200818/1597715391.png!small)

在WSIFPort_EJB反序列化过程中会调用readObject方法，进而执行

    
    
    this.fieldEjbObject = handle.getEJBObject();

这里可以构造一个恶意的fieldEjbObject 对象，为后续的jndi注入做准备。

继续跟进代码，在com.ibm.ejs.container.EntityHandle类中实现了Handler接口中的getEJBObject()方法。跟进com.ibm.ejs.container.EntityHandle#getEJBObject()，发现lookup()
jndi寻址方法。

![](https://image.3001.net/images/20200818/1597715434.png!small)

以下是Jndi lookup方法调用的流程

    
    
    com.sun.jndi.rmi.registry.RegistryContext#lookup
    com.sun.jndi.rmi.registry.RegistryContext#decodeObject
    javax.naming.spi.NamingManager#getObjectInstance
    org.apache.aries.jndi.OSGiObjectFactoryBuilder#getObjectInstance
    org.apache.aries.jndi.ObjectFactoryHelper#getObjectInstance
    org.apache.aries.jndi.ObjectFactoryHelper#getObjectInstanceViaContextDotObjectFactories

主要跟进getObjectInstanceViaContextDotObjectFactories方法，在此方法中可以调用任何ObjectFactory类的getObjectInstance，这里根据Zero
Day Initiative给出的WSIFServiceObjectFactory进行分析。

![](https://image.3001.net/images/20200818/1597715479.png!small)

通过获取远程恶意rmi服务中构造的xml文件并解析，读取其中的字段数据，为上图中属性进行赋值。

在获取homeClass之后，调用findFindByPrimaryKey()方法

![](https://image.3001.net/images/20200818/1597715508.png!small)![](https://image.3001.net/images/20200818/1597715522.png!small)

从此方法可以发现传入的homeclass的限制条件，首先需要实现findFindByPrimaryKey方法。而在调用lookup方法时，限制homeclass类需要继承EJBHome接口。

这里找到iswin提到的com.ibm.ws.batch.CounterHome接口。

![](https://image.3001.net/images/20200818/1597715562.png!small)

在执行this.object = (EJBObject)fbpk.invoke(home, this.key);
调用WSIFClientProxy#invoke方法，进行远程方法调用。实现漏洞利用。

###  ** **1.4 漏洞复现****

搭建WebSphere Application Server
9.0.0.2环境，构造恶意的反序列化数据，通过iiop发送到目标服务器，当目标服务器解析反序列化数据，会触发恶意代码执行，效果如图：

![](https://image.3001.net/images/20200818/1597715579.png!small)

#  **二、** ** **影响范围****

# 目前受影响的WebSphere版本：

WebSphere Application Server 9.0.0.0 - 9.0.5.4

WebSphere Application Server 8.5.0.0 - 8.5.5.17

#  **三、** ** **修复建议****

官方已经针对此漏洞发布补丁，请受影响的用户按照以下方式进行修复：

WebSphere Application Server 9.0：更新安全补丁PH25074，或者升级到9.0.5.5及更高版本。

WebSphere Application Server 8.5：更新安全补丁PH25074，或者升级到8.5.5.18及更高的版本。

#  **四、** ** **时间轴****

2020/6/15：IBM 官方分配漏洞编号CVE-2020-4450，发布补丁PH25074

2020/7/21：Zero Day Initiative 发布漏洞细节详情

2020/8/17 深信服千里目安全实验室分析并复现漏洞，发布产品解决方案。

#  **五、** ** **参考链接****

<https://i.blackhat.com/eu-19/Wednesday/eu-19-An-Far-Sides-Of-Java-Remote-Protocols.pdf>

https://www.thezdi.com/blog/2020/7/20/abusing-java-remote-protocols-in-ibm-websphere

https://www.iswin.org/2020/08/04/WebSphere-CVE-2020-4450-Vul-Analysis/

