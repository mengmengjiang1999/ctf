**作者：深信服千里目实验室  
原文链接：<https://mp.weixin.qq.com/s/WtT0o2ygGGQek3wvIulfiQ>**

## 1\. 组件介绍

XStream是Java类库，用来将对象序列化成XML(JSON)或反序列化为对象。XStream在运行时使用Java反射机制对要进行序列化的对象树的结构进行探索，并不需要对对象作出修改。XStream可以序列化内部字段，包括私private和final字段，并且支持非公开类以及内部类。在缺省情况下，XStream不需要配置映射关系，对象和字段将映射为同名XML元素。但是当对象和字段名与XML中的元素名不同时，XStream支持指定别名。XStream支持以方法调用的方式，或是Java标注的方式指定别名。XStream在进行数据类型转换时，使用系统缺省的类型转换器。同时，也支持用户自定义的类型转换器。  

XStream类图：  
![](https://images.seebug.org/content/images/2020/12/02/1606888968000-background1.png-w331s)  

## 2\. 高危漏洞介绍

漏洞名称 | 漏洞ID | 影响版本 | CVSS  
---|---|---|---  
XStream 远程代码执行漏洞 | CVE-2013-7285 | XStream <= 1.4.6 | 9.8  
XStream 远程代码执行漏洞 | CVE-2019-10173 | XStream < 1.4.10 | 9.8  
XStream 远程代码执行漏洞 | CVE-2020-26217 | XStream <= 1.4.13 | 8.0  
XStream 外部实体注入漏洞 | CVE-2016-3674 | XStream <= 1.4.8 | 7.5  
XStream 拒绝服务攻击 | CVE-2017-7957 | XStream <= 1.4.9 | 7.5  
  
XStream组件漏洞主要是java反序列化造成的远程代码执行漏洞，目前官方通过黑名单的方式对java反序列化攻击进行防御，由于黑名单防御机制存在被绕过的风险，因此以后可能会再次出现类似上述java反序列化漏洞。

## 3\. 漏洞利用链

### 3.1 组件风险梳理

根据XStream组件的漏洞，结合XStream常用的使用场景，得到如下风险梳理的场景图。  
![](https://images.seebug.org/content/images/2020/12/02/1606888969000-Vulnerability-panel.png-w331s)  

### 3.2 利用链总结

基于风险梳理思维导图，总结出一种漏洞的利用场景。

#### 3.2.1 无权限 -> GetShell

![](https://images.seebug.org/content/images/2020/12/02/1606888969000-attack-chain1.png-w331s)  

XStream远程代码执行漏洞单独使用，即可完成GetShell。一般情况，如果一个Web应用中使用了受漏洞影响版本的XStream，都会受XStream本身的漏洞影响。除此之外，由于XStream是将XML格式数据反序列化成对象。因此如果Web应用还引入了其他的在反序列化过程中容易出现安全问题的依赖，也会出现反序列化漏洞。

## 4\. 高可利用漏洞分析

从高危漏洞列表中，针对部分近年高可利用漏洞进行漏洞深入分析。  

**技术背景**

**java动态代理**

Java标准库提供了一种 **动态代理（Dynamic Proxy）** 的机制：可以在运行期动态创建某个interface的实例。

**例子：**
我们先定义了接口Hello，但是我们并不去编写实现类，而是直接通过JDK提供的一个Proxy.newProxyInstance()创建了一个Hello接口对象。这种没有实现类但是在运行期动态创建了一个接口对象的方式，我们称为动态代码。JDK提供的动态创建接口对象的方式，就叫动态代理。

    
    
    package test3_proxyclass;
    
    import java.lang.reflect.InvocationHandler;
    import java.lang.reflect.Method;
    import java.lang.reflect.Proxy;
    
    public class Main {
        public static void main(String[] args) {
            InvocationHandler handler = new InvocationHandler() {
                @Override
                public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
                    System.out.println(method);
                    if (method.getName().equals("morning")) {
                        System.out.println("Good morning, " + args[0]);
                    }
                    return null;
                }
            };
            Hello hello = (Hello) Proxy.newProxyInstance(
                    Hello.class.getClassLoader(), // 传入ClassLoader
                    new Class[] { Hello.class }, // 传入要实现的接口
                    handler); // 传入处理调用方法的InvocationHandler
            hello.morning("Bob");
        }
    }
    
    interface Hello {
        void morning(String name);
    }

java动态代理机制中有两个重要的类和接口InvocationHandler（接口）和Proxy（类），这一个类Proxy和接口InvocationHandler是我们实现动态代理的核心；

**InvocationHandler接口:**
proxy代理实例的调用处理程序实现的一个接口，每一个proxy代理实例都有一个关联的调用处理程序；在代理实例调用方法时，方法调用被编码分派到调用处理程序的invoke方法。

**newProxyInstance:** 创建一个代理类对象，它接收三个参数，我们来看下几个参数的含义：

    
    
    loader：一个classloader对象，定义了由哪个classloader对象对生成的代理类进行加载
    interfaces：一个interface对象数组，表示我们将要给我们的代理对象提供一组什么样的接口，如果我们提供了这样一个接口对象数组，那么也就是声明了代理类实现了这些接口，代理类就可以调用接口中声明的所有方法。
    h：一个InvocationHandler对象，表示的是当动态代理对象调用方法的时候会关联到哪一个InvocationHandler对象上，并最终由其调用。

**getInvocationHandler：** 返回指定代理实例的调用处理程序

**getProxyClass：** 给定类加载器和接口数组的代理类的java.lang.Class对象。

**isProxyClass：**
当且仅当使用getProxyClass方法或newProxyInstance方法将指定的类动态生成为代理类时，才返回true。

**newProxyInstance：** 返回指定接口的代理类的实例，该接口将方法调用分派给指定的调用处理程序。

#### 4.1 XStream 远程代码执行漏洞

**1 漏洞信息**

**1.1 漏洞简介**

  * 漏洞名称：XStream Remote Code Execution Vulnerability
  * 漏洞编号：CVE-2013-7285
  * 漏洞类型：Remote Code Execution
  * CVSS评分：CVSS v2.0：7.5 ， CVSS v3.0：9.8
  * 漏洞危害等级：高危

**1.2 漏洞概述**

包含类型信息的流在`unmarshalling`时，会再次创建之前写入的对象。因此XStream会基于这些类型信息创建新的实例。攻击者可以操控XML数据，将恶意命令注入在在可以执行任意shell命令的对象中，实现漏洞的利用。

**1.3 漏洞利用条件**

  * 无

**1.4 漏洞影响**

影响版本：  
XStream <= 1.4.6  

**1.5 漏洞修复**

获取XStream最新版本，下载链接：<https://x-stream.github.io/download.html>

**2.漏洞复现**

**2.1 环境拓扑**

![](https://images.seebug.org/content/images/2020/12/02/1606888969000-env3.png-w331s)  

**2.2 应用协议**

8080/HTTP

**2.3 环境搭建**

基于Windows平台，使用`环境`目录下的`xstreamdemo`环境，拷贝后使用Idea打开`xstreamdemo`文件夹，下载maven资源，运行DemoApplication类，即可启动环境。效果如图。  
  
![](https://images.seebug.org/content/images/2020/12/02/1606888970000-env1.png-w331s)

**2.4 漏洞复现**

运行`sniper`工具箱，填写表单信息，点击Attack，效果如图。  
![](https://images.seebug.org/content/images/2020/12/02/1606888970000-attack1.png-w331s)

**3.漏洞分析**

**3.1 详细分析**

**3.1.1 代码分析**

传入的payload首先会在`com.thoughtworks.xstream.XStream`的`fromXML()`方法中处理，在进入`unmarshal()`方法中进行解集。  
![](https://images.seebug.org/content/images/2020/12/02/1606888970000-ana1.png-w331s)

在`com.thoughtworks.xstream.core.AbstractTreeMarshallingStrategy`类中的`unmarshal()`方法中调用`start()`方法进行Java对象转换。  
![](https://images.seebug.org/content/images/2020/12/02/1606888970000-ana2.png-w331s)

在`com.thoughtworks.xstream.core.TreeUnmarshaller`类中的`start()`方法通过调用`readClassType()`获取`type`类型。  
![](https://images.seebug.org/content/images/2020/12/02/1606888971000-ana3.png-w331s)

在`readClassType()`方法中调用`readClassAttribute`方法。  
![](https://images.seebug.org/content/images/2020/12/02/1606888971000-ana4.png-w331s)

进入`readClassAttribute`方法调用`aliasForSystemAttribute`方法获取别名。调用`getAttribute`方法，获取reader对象中记录的外部传入XML数据中是否存在对应的标签，如果不存在则返回null。  
![](https://images.seebug.org/content/images/2020/12/02/1606888971000-ana14.png-w331s)

回到`HierarchicalStreams#readClassType`方法中调用`realClass`方法，通过别名在wrapped对象中的Mapper中循环查找，获取与别名对应的类。  
![](https://images.seebug.org/content/images/2020/12/02/1606888971000-ana15.png-w331s)

找到`sorted-set`别名对应的`java.util.SortedSet`类，并将类存入realClassCache对象中。  
![](https://images.seebug.org/content/images/2020/12/02/1606888971000-ana16.png-w331s)

回到`TreeUnmarshaller#start`方法，调用`convertAnother`方法。进入`convertAnother`方法后，调用`defaultImplementationOf`方法，在mapper对象中寻找java.util.SortedSet接口类的实现类`java.util.TreeSet`。  
![](https://images.seebug.org/content/images/2020/12/02/1606888971000-ana17.png-w331s)

获取`java.util.TreeSet`类型，调用`lookupConverterForType`方法，寻找对应类型的转换器。进入`lookupConverterForType`方法，循环获取转换器列表中的转换器，调用转换器类中的`canConvert`方法判断选出的转换器是否可以对传入的type类型进行转换。  
![](https://images.seebug.org/content/images/2020/12/02/1606888971000-ana18.png-w331s)

转换器`TreeSetConverter`父类`CollectionConverter`中`canConvert`方法判断，传入的type与`java.util.TreeMap`相同，返回true，表示可以使用`TreeSetConverter`转换器进行转换。  
![](https://images.seebug.org/content/images/2020/12/02/1606888971000-ana19.png-w331s)

回到`DefaultConverterLookup#lookupConverterForType`方法，将选取的converter与对应的type存入typeToConverterMap。

回到`TreeUnmarshaller#convertAnother`方法中，调用`this.convert`方法。  
![](https://images.seebug.org/content/images/2020/12/02/1606888972000-ana20.png-w331s)

首先判断传入的xml数据中是否存在reference标签，如果不存在，则将当前标签压入parentStack栈中，并调用父类的`convert`方法。  
![](https://images.seebug.org/content/images/2020/12/02/1606888972000-ana21.png-w331s)

进入`convert`方法中，调用转换器中的`unmarshal`方法，对传入的xml数据继续解组。  
![](https://images.seebug.org/content/images/2020/12/02/1606888972000-ana22.png-w331s)

首先调用`unmarshalComparator`方法判断是否存在comparator，如果不存在，则返回NullComparator对象。  
![](https://images.seebug.org/content/images/2020/12/02/1606888972000-ana23.png-w331s)

根据unmarshalledComparator对象状态，为possibleResult对象赋予TreeSet类型对象。  
![](https://images.seebug.org/content/images/2020/12/02/1606888972000-ana24.png-w331s)

由于possibleResult是一个空的TreeMap，因此最终treeMap也是一个空对象，从而调用`treeMapConverter.populateTreeMap`方法。  
![](https://images.seebug.org/content/images/2020/12/02/1606888972000-ana25.png-w331s)

进入`populateTreeMap`方法中，首先调用调用`putCurrentEntryIntoMap`方法解析第一个标签，再调用`populateMap`方法处理之后的标签（此流程中二级标签只存在一个，因此在处理二级标签时暂不进入populateMap方法）。  
![](https://images.seebug.org/content/images/2020/12/02/1606888972000-ana29.png-w331s)

具体调用流程如下，`com.thoughtworks.xstream.converters.collections.TreeSetConverter`类中调用`putCurrentEntryIntoMap`方法
->
`com.thoughtworks.xstream.converters.collections.AbstractCollectionConverter.readItem()`
中的 `readClassType()`方法获取传入xml数据中标签名（别名）对应的类（与本节中获取sorted-set对应类的流程相同）。本次获取的是dynamic-proxy对应的`java.lang.reflect.Proxy.DynamicProxyMapper`类型，并将别名与类型作为键值对，存入realClassCache中。  
![](https://images.seebug.org/content/images/2020/12/02/1606888972000-ana5.png-w331s)  
![](https://images.seebug.org/content/images/2020/12/02/1606888972000-ana6.png-w331s)

回到`AbstractCollectionConverter.readItem()`方法中，调用`convertAnother`方法，寻找`DynamicProxyMapper`对应的convert，获取到`DynamicProxyConverter`转换器。  
![](https://images.seebug.org/content/images/2020/12/02/1606888972000-ana26.png-w331s)

得到`com.thoughtworks.xstream.mapper.DynamicProxyMapper$DynamicProxy`，按照之前获取转换器之后的流程，调用转换器中的`unmarshal()`方法获取`interface`元素，得到`java.lang.Comparable`，并添加到mapper中。  
![](https://images.seebug.org/content/images/2020/12/02/1606888973000-ana7.png-w331s)

在通过循环查询，继续查找下面的节点元素，进而获得了`handler java.beans.EventHandler`。  
![](https://images.seebug.org/content/images/2020/12/02/1606888973000-ana8.png-w331s)

调用`Proxy.newProxyInstance`方法创建动态代理，实现java.lang.Comparable接口。  
![](https://images.seebug.org/content/images/2020/12/02/1606888973000-ana27.png-w331s)

调用`convertAnother`方法获取传入type的转换器，`java.beans.EventHandler`对应的convert是`ReflectionConverter`。并将父类及其对象写进HashMap中  
![](https://images.seebug.org/content/images/2020/12/02/1606888973000-ana9.png-w331s)  
![](https://images.seebug.org/content/images/2020/12/02/1606888973000-ana28.png-w331s)

在`com.thoughtworks.xstream.converters.reflection.AbstractReflectionConverter.duUnmarshal()`方法获取下面的节点元素`target
java.lang.ProcessBuilder`。  
具体流程如下：调用`getFieldOrNull`方法，判断xml格式中传入的标签名在目标类中是否存在对应属性。  
![](https://images.seebug.org/content/images/2020/12/02/1606888973000-ana10.png-w331s)  
![](https://images.seebug.org/content/images/2020/12/02/1606888973000-ana30.png-w331s)

在调用`reader.getNodeName()`方法获取标签名，并赋值给originalNodeName。  
![](https://images.seebug.org/content/images/2020/12/02/1606888973000-ana31.png-w331s)

调用`realMember`方法获取反序列化属性的名称。  
![](https://images.seebug.org/content/images/2020/12/02/1606888973000-ana32.png-w331s)

调用`readClassAttribute`方法获取target标签中传入的类名  
![](https://images.seebug.org/content/images/2020/12/02/1606888974000-ana33.png-w331s)

调用`realClass`获取上述过程中类名对应的类，并调用`unmarshallField`方法进行解析。  
![](https://images.seebug.org/content/images/2020/12/02/1606888974000-ana11.png-w331s)

进入方法中，寻找对应type的转换器，由于是java.beans.EventHandler作为动态代理的实现类，所以选择的转化器都是`ReflectionConverter`
。使用选中的转换器进行解组。  
![](https://images.seebug.org/content/images/2020/12/02/1606888974000-ana34.png-w331s)

使用`ReflectionConverter` convert处理`java.lang.ProcessBuilder`
，在`duUnmarshal()`方法获取`command`标签和comand标签下的String标签及其参数。（其中String标签下的参数是在下一层convert调用中获取的。）  
![](https://images.seebug.org/content/images/2020/12/02/1606888974000-ana12.png-w331s)

调用`this.reflectionProvider.writeField`方法，将参数值传入对象中。  
![](https://images.seebug.org/content/images/2020/12/02/1606888974000-ana35.png-w331s)  
![](https://images.seebug.org/content/images/2020/12/02/1606888974000-ana36.png-w331s)  
![](https://images.seebug.org/content/images/2020/12/02/1606888974000-ana37.png-w331s)

在按照获取target标签相同的流程获取action标签，最终将start方法存入对象中。  
![](https://images.seebug.org/content/images/2020/12/02/1606888974000-ana38.png-w331s)

回到`TreeMapConverter#populateTreeMap`方法中，上述过程中构造的object保存在sortedMap中。且其中的动态代理实现的接口是`java.lang.Comparable`，因此只要调用`java.lang.Comparable`接口中的`compareTo`方法，即可触发动态代理，进入`java.beans.EventHandler`实现类中的`invoke`方法。在`populateTreeMap`方法中调用`putAll`方法，将sortedMap中的对象写入result变量的过程中会调用到`compareTo`，调用链如下。  
![](https://images.seebug.org/content/images/2020/12/02/1606888974000-ana39.png-w331s)

进入`java.beans.EventHandler#invoke`方法中，通过反射执行对象中的方法。  
![](https://images.seebug.org/content/images/2020/12/02/1606888975000-ana40.png-w331s)

**3.1.2补丁分析**

XStream1.4.7版本中，在`com.thoughtworks.xstream.converters.reflection.ReflectionConverter`添加`type
!=
eventHandlerType`阻止`ReflectionConverter`解析`java.beans.EventHandler`类。从而防御了此漏洞。  
![](https://images.seebug.org/content/images/2020/12/02/1606888975000-patch1.png-w331s)

#### 4.2 XStream 远程代码执行漏洞

**1.漏洞信息**

**1.1 漏洞简介**

  * 漏洞名称：XStream Remote Code Execution Vulnerability
  * 漏洞编号：CVE-2019-10173
  * 漏洞类型：Remote Code Execution
  * CVSS评分：CVSS v2.0：7.3 ， CVSS v3.0：9.8
  * 漏洞危害等级：高危

**1.2 漏洞概述**

包含类型信息的流在`unmarshalling`时，会再次创建之前写入的对象。因此XStream会基于这些类型信息创建新的实例。攻击者可以操控XML数据，将恶意命令注入在在可以执行任意shell命令的对象中，实现漏洞的利用。

**1.3 漏洞利用条件**

无

**1.4 漏洞影响**

影响版本：  
XStream = 1.4.10  

**1.5 漏洞修复**

获取XStream最新版本，下载链接：<https://x-stream.github.io/download.html>

**2.漏洞复现**

**2.1 环境拓扑**

![](https://images.seebug.org/content/images/2020/12/02/1606888975000-env3.png-w331s)  

**2.2 应用协议**

8080/HTTP

**2.3 环境搭建**

基于Windows平台，使用`环境`目录下的`xstreamdemo`环境，拷贝后使用Idea打开`xstreamdemo`文件夹，下载maven资源，运行DemoApplication类，即可启动环境。效果如图。  
  
![](https://images.seebug.org/content/images/2020/12/02/1606888975000-env1.png-w331s)

**2.4 漏洞复现**

运行`sniper`工具箱，填写表单信息，点击Attack，效果如图。  
![](https://images.seebug.org/content/images/2020/12/02/1606888977000-attack1.png-w331s)

**3.漏洞分析**

**3.1 详细分析**

**3.1.1 代码分析**

CVE-2019-10173漏洞与CVE-2013-7285漏洞原理相同，由于在XStream的安全模式默认不启动，导致防御失效。

**Xstream 1.4.7对于漏洞的防御措施：**
通过在`com.thoughtworks.xstream.converters.reflection.ReflectionConverter`添加`type
!= eventHandlerType`阻止`ReflectionConverter`解析`java.beans.EventHandler`类  
![](https://images.seebug.org/content/images/2020/12/02/1606888978000-ana42.png-w331s)

**Xstream 1.4.10漏洞产生原因：**
在`com.thoughtworks.xstream.converters.reflection.ReflectionConverter`类中，canConvert方法中的`type
!= eventHandlerType`被删除了，使得原来的漏洞利用方式可以再次被利用。
由于在Xstream1.4.10中的`com.thoughtworks.xstream.XStream`类增加了`setupDefaultSecurity()`方法和`InternalBlackList`转换器，通过黑名单的形式对漏洞进行防御。但是安全模式默认不开启，必须在初始化后才可以使用，eg：`XStream.setupDefaultSecurity(xStream)`。导致防御失效，造成漏洞的第二次出现。  
![](https://images.seebug.org/content/images/2020/12/02/1606888978000-ana43.png-w331s)  
![](https://images.seebug.org/content/images/2020/12/02/1606888978000-ana44.png-w331s)

**3.1.2补丁分析**

XStream1.4.11版本中，在`com.thoughtworks.xstream.XStream`更改安全模式初始化方法中的`securityInitialized`标志位。在调用`InternalBlackList`转换器中的`canConvert`方法时,可以进行黑名单匹配，从而防御了此漏洞。  
![](https://images.seebug.org/content/images/2020/12/02/1606888979000-patch1.png-w331s)  
![](https://images.seebug.org/content/images/2020/12/02/1606888979000-patch2.png-w331s)

**漏洞防御**
在Xstream1.4.11中的`com.thoughtworks.xstream.XStream`类中`InternalBlackList`类会对`java.beans.EventHandler`进行过滤，`java.beans.EventHandler`执行`marshal`或者`unmarshal`方法时，会抛出异常终止程序。  
![](https://images.seebug.org/content/images/2020/12/02/1606888979000-patch3.png-w331s)

#### 4.3 XStream 远程代码执行漏洞

**1.漏洞信息**

**1.1 漏洞简介**

  * 漏洞名称：XStream Remote Code Execution Vulnerability
  * 漏洞编号：CVE-2020-26217
  * 漏洞类型：Remote Code Execution
  * CVSS评分：CVSS v2.0：无， CVSS v3.0：8.0
  * 漏洞危害等级：高危

**1.2 漏洞概述**

包含类型信息的流在`unmarshalling`时，会再次创建之前写入的对象。因此XStream会基于这些类型信息创建新的实例。攻击者可以操控XML数据，将恶意命令注入在在可以执行任意shell命令的对象中，实现漏洞的利用。

**1.3 漏洞利用条件**

  * 无

**1.4 漏洞影响**

影响版本：  
XStream = 1.4.13  

**1.5 漏洞修复**

获取XStream最新版本，下载链接：<https://x-stream.github.io/download.html>

**2.漏洞复现**

**2.1 环境拓扑**

![](https://images.seebug.org/content/images/2020/12/02/1606888980000-env3.png-w331s)  

**2.2 应用协议**

8080/HTTP

**2.3 环境搭建**

基于Windows平台，使用`环境`目录下的`xstreamdemo`环境，拷贝后使用Idea打开`xstreamdemo`文件夹，下载maven资源，运行DemoApplication类，即可启动环境。效果如图。  
  
![](https://images.seebug.org/content/images/2020/12/02/1606888980000-env1.png-w331s)

**2.4 漏洞复现**

运行`sniper`工具箱，填写表单信息，点击Attack，效果如图。  
![](https://images.seebug.org/content/images/2020/12/02/1606888981000-attack1.png-w331s)

**3.漏洞分析**

**3.1 详细分析**

**3.1.1 代码分析**

代码分析：传入的payload首先会在`com.thoughtworks.xstream.XStream`的`fromXML()`方法中处理，在进入`unmarshal()`方法中进行解集。  
![](https://images.seebug.org/content/images/2020/12/02/1606888981000-ana1.png-w331s)

在`com.thoughtworks.xstream.core.AbstractTreeMarshallingStrategy`类中的`unmarshal()`方法中调用`start()`方法进行Java对象转换。  
![](https://images.seebug.org/content/images/2020/12/02/1606888982000-ana2.png-w331s)

在`com.thoughtworks.xstream.core.TreeUnmarshaller`类中的`start()`方法通过调用`readClassType()`获取`type`类型。  
![](https://images.seebug.org/content/images/2020/12/02/1606888982000-ana3.png-w331s)

在`readClassType()`方法中调用`readClassAttribute`方法。  
![](https://images.seebug.org/content/images/2020/12/02/1606888983000-ana4.png-w331s)

进入`readClassAttribute`方法调用`aliasForSystemAttribute`方法获取别名。调用`getAttribute`方法，获取reader对象中记录的外部传入XML数据中是否存在对应的标签，如果不存在则返回null。  
![](https://images.seebug.org/content/images/2020/12/02/1606888983000-ana14.png-w331s)

回到`HierarchicalStreams#readClassType`方法中调用`realClass`方法，通过别名在wrapped对象中的Mapper中循环查找，获取与别名对应的类。  
![](https://images.seebug.org/content/images/2020/12/02/1606888983000-ana15.png-w331s)

在`DefaultMapper`中，通过反射，获取到string标签传入的class，并将类存入realClassCache对象中。  
![](https://images.seebug.org/content/images/2020/12/02/1606888984000-ana41.png-w331s)  
![](https://images.seebug.org/content/images/2020/12/02/1606888985000-ana16.png-w331s)

回到`TreeUnmarshaller#start`方法，调用`convertAnother`方法。进入`convertAnother`方法后，调用`lookupConverterForType`方法，寻找对应类型的转换器。进入`lookupConverterForType`方法，循环获取转换器列表中的转换器，调用转换器类中的`canConvert`方法判断选出的转换器是否可以对传入的type类型进行转换。  
![](https://images.seebug.org/content/images/2020/12/02/1606888986000-ana18.png-w331s)

转换器`ReflectionConverter`中`canConvert`方法判断，传入的type非null，返回true，表示可以使用`ReflectionConverter`转换器进行转换。  
![](https://images.seebug.org/content/images/2020/12/02/1606888986000-ana19.png-w331s)

回到`DefaultConverterLookup#lookupConverterForType`方法，将选取的converter与对应的type存入typeToConverterMap。

回到`TreeUnmarshaller#convertAnother`方法中，调用`this.convert`方法。  
![](https://images.seebug.org/content/images/2020/12/02/1606888986000-ana20.png-w331s)

首先判断传入的xml数据中是否存在reference标签，如果不存在，则将当前标签压入parentStack栈中，并调用父类的`convert`方法。  
![](https://images.seebug.org/content/images/2020/12/02/1606888987000-ana21.png-w331s)

在`com.thoughtworks.xstream.converters.reflection.AbstractReflectionConverter.duUnmarshal()`方法获取下面的节点元素`iter
java.util.ArrayList$Itr`。  
具体流程如下：调用`getFieldOrNull`方法，判断xml格式中传入的标签名在目标类中是否存在对应属性。  
![](https://images.seebug.org/content/images/2020/12/02/1606888988000-ana10.png-w331s)  
![](https://images.seebug.org/content/images/2020/12/02/1606888988000-ana30.png-w331s)

在调用`reader.getNodeName()`方法获取标签名，并赋值给originalNodeName。  
![](https://images.seebug.org/content/images/2020/12/02/1606888989000-ana31.png-w331s)

调用`realMember`方法获取反序列化属性的名称。  
![](https://images.seebug.org/content/images/2020/12/02/1606888990000-ana32.png-w331s)

调用`readClassAttribute`方法获取iter标签中传入的类名  
![](https://images.seebug.org/content/images/2020/12/02/1606888991000-ana33.png-w331s)

调用`realClass`获取上述过程中类名对应的类，并调用`unmarshallField`方法进行解析。  
![](https://images.seebug.org/content/images/2020/12/02/1606888991000-ana11.png-w331s)

进入方法中，寻找对应type的转换器，使用选中的ReflectionConverter转换器进行解组。  
![](https://images.seebug.org/content/images/2020/12/02/1606888992000-ana34.png-w331s)

使用`ReflectionConverter` convert处理`java.util.ArrayList$Itr`
，在`duUnmarshal()`方法获取`cursor`标签和`cursor`标签下的参数。（调用`unmarshallField`方法，与上述流程相似）  
![](https://images.seebug.org/content/images/2020/12/02/1606888992000-ana12.png-w331s)

调用`this.reflectionProvider.writeField`方法，将参数值传入对象中。  
![](https://images.seebug.org/content/images/2020/12/02/1606888993000-ana35.png-w331s)  
![](https://images.seebug.org/content/images/2020/12/02/1606888993000-ana36.png-w331s)  

回到`AbstractReflectionConverter#doUnmarshal`方法中获取后续的标签及其参数（分别为lastRet，expectedModCount，outer-class）。  
![](https://images.seebug.org/content/images/2020/12/02/1606888994000-ana5.png-w331s)

按照同样的反序列化流程获取属性值，并写入对象。  
![](https://images.seebug.org/content/images/2020/12/02/1606888994000-ana6.png-w331s)

解析outer-class标签，由于type是`java.util.ArrayList`，选择转换器是`CollectionConverter`。  
![](https://images.seebug.org/content/images/2020/12/02/1606888995000-ana7.png-w331s)

调用`CollectionConverter#unmarshal`方法进行反序列化。  
![](https://images.seebug.org/content/images/2020/12/02/1606888995000-ana8.png-w331s)

调用`CollectionConverter#populateCollection` ->
`CollectionConverter#addCurrentElementToCollection`->`AbstractCollectionConverter#readItem`方法。最终调用realClass方法获取type类，获取过程中将outer-class标签下的子标签存入realClassCache中。  
![](https://images.seebug.org/content/images/2020/12/02/1606888995000-ana9.png-w331s)

回到`AbstractCollectionConverter#readBareItem`方法调用`convertAnother`方法，按照之前的流程进行反序列化，为属性赋值，并写入对象。  
![](https://images.seebug.org/content/images/2020/12/02/1606888996000-ana37.png-w331s)

最终返回`ProcessBuilder`对象，写入`FilterIterator`对象中。  
![](https://images.seebug.org/content/images/2020/12/02/1606888996000-ana38.png-w331s)

在按照获取`java.util.ArrayList$Itr`对象相同的流程获取`javax.imageio.ImageIO$ContainsFilter`对象，通过反序列化为其内部的method属性和name属性进行赋值。

在选择转换器的过程中，由于method属性的类型是`java.lang.reflect.Method`，因此选择对应的转换器为JavaMethodConverter。  
![](https://images.seebug.org/content/images/2020/12/02/1606888996000-ana17.png-w331s)

调用`JavaMethodConverter#unmarshal`方法进行xml数据解析，获取java.lang.processBuilder类中的start方法对象，写入到`javax.imageio.ImageIO$ContainsFilter`对象中。  
![](https://images.seebug.org/content/images/2020/12/02/1606888996000-ana23.png-w331s)

再按照相同的流程，将start方法名写入name属性中。  
![](https://images.seebug.org/content/images/2020/12/02/1606888996000-ana24.png-w331s)

最终在调用`ReflectionProvider#writeField`方法将`javax.imageio.ImageIO$ContainsFilter`对象写进`FilterIterator`对象的filter属性中。  
![](https://images.seebug.org/content/images/2020/12/02/1606888997000-ana25.png-w331s)

将`FilterIterator`对象返回给最初的`iterator`对象中。  
![](https://images.seebug.org/content/images/2020/12/02/1606888997000-ana26.png-w331s)

调用`iterator.next()`方法时，会调用其实现类`FilterIterator`中的next方法。  
![](https://images.seebug.org/content/images/2020/12/02/1606888997000-ana27.png-w331s)

进入调用advance方法，调用filter方法时，会通过反射执行ProcessBuilder对象中的start方法，从而造成代码执行。  
![](https://images.seebug.org/content/images/2020/12/02/1606888997000-ana28.png-w331s)  
![](https://images.seebug.org/content/images/2020/12/02/1606888997000-ana29.png-w331s)

**3.1.2补丁分析**

XStream1.4.11版本中，在`com.thoughtworks.xstream.XStream`更改安全模式初始化方法中的`securityInitialized`标志位。在调用`InternalBlackList`转换器中的`canConvert`方法时,可以进行黑名单匹配，从而防御了此漏洞。  
![](https://images.seebug.org/content/images/2020/12/02/1606888979000-patch1.png-w331s)  
![](https://images.seebug.org/content/images/2020/12/02/1606888979000-patch2.png-w331s)

**漏洞防御**
XStream1.4.14版本中，在`com.thoughtworks.xstream.XStream`的黑名单添加`java.lang.ProcessBuilder`和`javax.imageio.ImageIO$ContainsFilter`。从而防御了此漏洞。  
![](https://images.seebug.org/content/images/2020/12/02/1606888998000-patch1.png-w331s)

## 5.漏洞利用

### XStream 远程代码执行漏洞

漏洞利用视频，请转到原文观看，链接：<https://mp.weixin.qq.com/s/WtT0o2ygGGQek3wvIulfiQ>

## 6.参考链接

1.<https://blog.csdn.net/yaomingyang/article/details/80981004>  
2.<https://github.com/x-stream/xstream/compare/XSTREAM_1_4_6...XSTREAM_1_4_7>  
3.<https://github.com/x-stream/xstream/compare/XSTREAM_1_4_10...XSTREAM_1_4_11>  
4.<https://github.com/x-stream/xstream/compare/XSTREAM_1_4_13...XSTREAM_1_4_14>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1417/>

