## 启动阶段

OpenRASP的启动类Jar包是`rasp.jar`在他的`MANIFEST.MF`中有如下配置

![](./img/8246176686360674927.png)

确定了`Premain-Class / Agent-Class / Main-Class / Can-Redefine-Classes / Can-Retransform-Classes`这些关键属性值

具体表示什么功能这里就不过于描述了

首先在启动是将会加载的是`Agent#premain`方法

![](./img/8350636517080926428.png)

![](./img/5344669593461961691.png)

这里存在一个步骤是将我们的`rasp.jar`包加入到了`BootStrapClassLoader`下，这是因为Java的一个双亲委派机制，如果不将其加入根下，当我们hook的点是通过`BootStrapClassLoader`加载的类的时候，将不能正确的检测

后面就是一些模块的加载

![](./img/6246218054065949220.png)

![](./img/7285380833703529529.png)

首先是如果是`JBoss`的服务器，将会进行一些相关配置

![](./img/5531220591155449899.png)

这里的`ENGINE_JAR`是`rasp-engine.jar`，之后就是对rasp-engine这个模块的加载

![](./img/8032570843819218991.png)

简单的描述一下流程就是

  1. 获取`rasp-engine.jar`这个包的绝对路径
  2. 获取在`rasp-engine.jar`包中的`MANIFEST.MF`文件中的`Rasp-Module-Class`这个模块的主要类名
  3. 将`rasp-engine.jar`添加进入classpath下，使得能够加载包中的类文件
  4. 加载`Rasp-Module-Class`属性对应的类，并实例化

![](./img/900099150419649116.png)

紧接着就是调用我们前面获取到的`engine`类的start方法进行启动

![](./img/4818962330670666162.png)

首当其充的就是V8引擎的加载，这里是为了方便OpenRASP跨平台以及热部署使用V8引擎进行部分规则的编写

有关V8的详细源码可以在[github](https://github.com/baidu-security/openrasp-v8/blob/4e1398d9e3de81a581c8f465b117abb8399a014d/java/CMakeLists.txt)中找到

后面就是一些插件的初始化

![](./img/2498746880598099152.png)

这里设置了是通过JSON的格式来保存栈信息

之后就是设置了一些保存信息用的key值

![](./img/8471955219457430052.png)

紧接着就是对插件的更新

![](./img/6761245972404100296.png)

![](./img/1670416730082885649.png)

  1. 首先获取对应的插件的绝对路径
  2. 之后获取对应目录下的js文件，官方内置的为`official.js`进行插件的配置
  3. 读取文件内容并将其和文件名保存在`scripts`中，之后使用V8引擎进行信息的提取

![](./img/7759530359871956010.png)

之后就是调用`InitFileWatcher`方法来实现对js配置文件的监听事件，使得能够实时的更新OpenRasp的配置

![](./img/9154858709730986559.png)

之后就是调用`CheckerManager.init`方法进行检测类型的加载

![](./img/4942371079804893392.png)

![](./img/2222582545401572506.png)

![](./img/2494062208109162968.png)

有 js插件检测，java本地检测和安全基线检测

紧接着就是使用`initTransformer(inst)`方法进行字节码转换器的初始化，进行插桩的配置

![](./img/4919509075102108280.png)

![](./img/1497089509042782826.png)

通过调用`addAnnotationHook`进行插桩

![](./img/8821851051678372264.png)

  1. 通过获取在`com.baidu.openrasp.hook`包下的所有类，提取这里面中使用了`@HookAnnotation`注解的类

  2. 实例化类之后调用`addHook`进行插桩

接着调用`retransform`方法进行转换

![](./img/8605578230042553117.png)

这里存在有一个判断，通过`isClassMatched`的调用判断是否是Hook的类

![](./img/3322278907216995100.png)

实现分为两种

而如果存在这样的将会对这些类进行Hook点的加载

最后结束了初始化的过程

![](./img/5863399905680692231.png)

## 检测阶段

有了前面的一些基础，我们简单的认识了OpenRASP的再启动阶段的一些初始化的配置

我们这里具体看看其中的原理，这里使用XXE的检测作为例子

前面也提及了，在OpenRASP初始化的阶段就会对应一些危险类的危险函数进行Hook，并使用了javassist这个ASM框架在危险方法中动态加入了一些特定的检测逻辑来判断是否是异常行为，如果是，将会进行拦截，不是，就会放行

正如XXE的Hook流程

`XXEHook#isClassMatched`方法是用来进行筛选，可能出现的XXE漏洞的sink点

![](./img/4442000171248728954.png)

这三个类都是可能出现XXE的漏洞点，当然，这里过滤得不是很完全，对于XXE得sink点还有这其他的类，这里就不扩充了

在`CustomClassTransformer#transform`方法就是重写字节码的具体实现

![](./img/7691059909601203518.png)

  1. 将原类文件写入classpath中
  2. 调用`AbstractClassHook#transformClass`进行检测代码的添加并返回修改后的字节码

![](./img/4299042657576421712.png)

这里主要是通过不同的实现类的`hookMethod`方法来进行检测代码的添加

这里针对XXE就是在`XXEHook#hookMethod`方法中

![](./img/48861293012216124.png)

主要是使用`getInvokeStaticSrc`获取了`checkXXE`方法的字节码并将其写入了sink点的运行前，这里也就是在XML进行解析的必经之路上`expandSystemId
/ setDescription`等两个方法

![](./img/8517797023185402115.png)

在我们的漏洞靶场中，这里选用的是openRASP的[官方靶场](https://github.com/baidu-security/openrasp-testcases/releases)

在配置成功RASP之后，进行XXE攻击

![](./img/8587077378363464799.png)

根据jsp中的代码，这种XXE是通过`DocumentBuilder`类进行xml的解析的

![](./img/270510911020817173.png)

在解析过程中，将会调用我们已经hook了的`org/apache/xerces/impl/XMLEntityManager`类的关键方法`expandSystemId`

而经过前面的分析，我们知道在初始化的过程中已经在调用`expandSystemId`方法之前添加了`checkXXE`方法的调用，这些流程的调用栈如下

    
    
    checkXXE:102, XXEHook (com.baidu.openrasp.hook.xxe)
    invoke:-1, GeneratedMethodAccessor9 (sun.reflect)
    invoke:43, DelegatingMethodAccessorImpl (sun.reflect)
    invoke:498, Method (java.lang.reflect)
    expandSystemId:-1, XMLEntityManager (org.apache.xerces.impl)
    addExternalEntity:-1, XMLEntityManager (org.apache.xerces.impl)
    scanEntityDecl:-1, XMLDTDScannerImpl (org.apache.xerces.impl)
    scanDecls:-1, XMLDTDScannerImpl (org.apache.xerces.impl)
    scanDTDInternalSubset:-1, XMLDTDScannerImpl (org.apache.xerces.impl)
    dispatch:-1, XMLDocumentScannerImpl$DTDDispatcher (org.apache.xerces.impl)
    scanDocument:-1, XMLDocumentFragmentScannerImpl (org.apache.xerces.impl)
    parse:-1, XML11Configuration (org.apache.xerces.parsers)
    parse:-1, XML11Configuration (org.apache.xerces.parsers)
    parse:-1, XMLParser (org.apache.xerces.parsers)
    parse:-1, DOMParser (org.apache.xerces.parsers)
    parse:-1, DocumentBuilderImpl (org.apache.xerces.jaxp)
    

之后就是检查是否是危险操作

![](./img/9200661871177972654.png)

![](./img/8604273054088820783.png)

在检测过程中，将会有安全对业务让步的操作

之后真正的检查逻辑在`doRealCheckWithoutRequest`方法中

![](./img/4996280875861234333.png)

![](./img/6350309562712776217.png)

使用不同类型的检查方式，这里XXE是`V8AttackChecker`类

![](./img/494077310744545883.png)

使用`checkParam`来对payload进行检测

![](./img/7782158815493317055.png)

也即是通过插件来进行检测

更多的检查方式可以在`official.js`中了解，这里跟一下XXE的检测方法

![](./img/4559477675335924592.png)

这分别是针对XXE检测的一些内置的手段，比如说禁用外部实体 / 禁用特殊协议 / 直接禁用file协议等等

其中的`action`字段就是判断是否启用

至于如何进行检测，如下图

![](./img/2777105887318001787.png)

这两种是对特殊协议的禁用的检测，一旦使用前面配置的协议，将会被视为恶意请求，message字段也就是将会在告警中打印的提示符

![](./img/476645124044592208.png)

至于针对file协议的使用检测如下

![](./img/6656472731456898007.png)

  1. 如果启用了这个算法，首先将会file:///xxx中后面的内容进行提取

  2. 检查是否进行了跨目录访问

  3. 检查是否使用了url的锚点

  4. 检查是否使用file协议读取了内部文件

  5. 如果都不满足，将会返回一个常量`clean`

![](./img/6107812617023305013.png)

## 总结

上面针对OpenRASP这一个开源RASP产品进行了详细的流程分析，通过跟踪代码，分析流程，对RASP产品有了更深的体验

从V8引擎进行检测，到使用js进行热部署，已经hook点的定位的手法和思路也有了更深的体会

总的来说，RASP产品的优势和缺点同样的突出

  1. 优势
    * 有着很好的精准性，误报率不高
    * 能够进行0Day的一定程度的防御，（甚至可以拿来做蜜罐
    * 相比于WAF，能够对加密的流量进行防御
  2. 劣势
    * 有可能造成资源的浪费
    * 需要维护多个sink点
    * 容易造成sink点检测不全的风险，比如OpenRASP在对webshell的检测的时候，针对市面上常见的大型攻击框架(`ysoserial`和`behinder`)等等进行了包名的检查，但是针对随机类名将会被绕过，又比如前面分析到的XXE的sink点，针对常见的XXE漏洞点进行了检测，但是前段时间公布了一个sink点因项目未更新，可能也会存在绕过的风险
    * 通用性的解决方法也是一个难题

## 参考

<https://forum.butian.net/share/1959>

<https://github.com/baidu-security/openrasp-v8>

<https://rasp.baidu.com/doc/>

