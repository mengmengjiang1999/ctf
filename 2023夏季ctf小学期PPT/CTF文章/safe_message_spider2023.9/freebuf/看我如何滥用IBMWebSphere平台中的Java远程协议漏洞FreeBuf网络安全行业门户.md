![](https://image.3001.net/images/20200812/1597247863.png!small)

在今年的四月份，一位名叫[ _tint0_](https://www.twitter.com/_tint0)的安全研究人员向ZDI提交了两个存在于IBM
WebSphere平台中的安全漏洞。其中一个漏洞是一个信息披露漏洞（[
_ZDI-20-690_](https://www.zerodayinitiative.com/advisories/ZDI-20-690/)/CVE-2020-4449），另一个则是一个远程代码执行（RCE）漏洞（[
_ZDI-20-689_](https://www.zerodayinitiative.com/advisories/ZDI-20-689/)/CVE-2020-4450）。在这篇文章中，我们将对这两个漏洞进行分析。

CORBA，即公共对象请求代理体系结构，它是一个由对象管理组织（OMG）定义的标准化规范。它是一个独立与平台的RPC框架，并且早于SOAP和gRPC等标准出现。在分布式环境中，CORBA使用了[
_互联网InterORB协议_](https://en.wikipedia.org/wiki/General_Inter-ORB_Protocol)（IIOP）来实现端点之间的通信。在IBM
WebSphere的默认安装配置下，CORBA服务可以运行在TCP端口2809、9100、9402和9403。在调用服务方法之前，Interceptor类将会拦截调用请求，这里我们需要注意的是TxServerInterceptor类。

### CVE-2020-4450-snippet-1.java：

    
    
    public void receive_request(ServerRequestInfo sri) {
    
      // ...snip...
    
        if (TxProperties.SINGLE_PROCESS) {
    
          propagationContext = TxInterceptorHelper.demarshalContext(serviceContext.context_data, (ORB)((LocalObject)sri)._orb()); // <------------    
          contextType = TxInterceptorHelper.determineContextType(propagationContext);
    
        }  
    
      // ...snip...
    
    }
    
     
    
    public static final PropagationContext demarshalContext(byte[] bytes, ORB orb) {
    
      // ...snip...
    
      propContext.implementation_specific_data = inputStream.read_any(); // <-------    
      // ...snip...
    
    }
    
     
    
    public Any read_any() {
    
      // ...snip...
    
      any.read_value(this.encoderStream, typeCodeImpl); // <------------------------    
      return any;
    
    }
    
     
    
    private Object simpleReadObjectInternal(Class paramClass, String paramString) throws ClassNotFoundException, IOException {
    
      // ...snip...
    
          return readSerializable(paramClass, objectStreamClass, paramString); // <------    
      // ...snip...
    
    }
    
     
    
    private Object readSerializable(Class paramClass, ObjectStreamClass paramObjectStreamClass, String paramString) throws IOException, ClassNotFoundException {
    
      // ...snip...
    
      return inputObjectClassDesc(serializable, paramObjectStreamClass); // <-------    
    }
    
     
    
    private Object inputObjectClassDesc(Object paramObject, ObjectStreamClass paramObjectStreamClass) throws IOException, ClassNotFoundException {
    
      ObjectStreamClass objectStreamClass = processClassHierarchy(paramObject, paramObjectStreamClass);
    
      return inputObjectUsingClassDesc(paramObject, objectStreamClass); // <--------    
    }
    
     
    
      Object inputObjectUsingClassDesc(Object paramObject, ObjectStreamClass paramObjectStreamClass) throws IOException, ClassNotFoundException {
    
        // ...snip...
    
          ObjectStreamClass objectStreamClass = this.readObjectOSC;
    
          this.readObjectOSC = paramObjectStreamClass;
    
          paramObjectStreamClass.readObjectMethod.invoke(paramObject, this.readObjectArglist); // <--- calls readObject()
    
          this.readObjectOSC = objectStreamClass;
    
          return true;
    
    }

当TxServerInterceptor类成功拦截调用请求时，便会调用receive_request()方法，同时还会试用demarshalContext()方法来从字节流中接收一个ServiceContext对象，而这个对象是攻击者可控的。任何嵌入在这个字节流中的对象都可以通过调用read_any()方法来提取，最终通过调用readObject()方法来获取嵌入的对象类。

## 远程代码执行漏洞（CVE-2020-4450）

尽管我们可以实现对任何对象进行反序列化操作，但实现远程代码执行并非易事。这是因为IBM Java SDK实现了针对反序列化攻击的安全缓解措施，其中包括：

  * 拥有更严格的ClassLoader类，在运行时仅提供必要的类；
  * TemplatesImpl类已无法再被序列化；
  * IBM SDK不会使用Oracle JDK的Java名命方法以及目录接口（JNDI）。因此，我们无法通过RMI/LDAP来加载远程类并实现漏洞利用；

根据tint0的描述，tint0提供了一个Gadget链来绕过这种缓解方案。这个Gadget使用了WSIFPort_EJB类作为入口点。

### CVE-2020-4450-snippet-2.java：

    
    
    public class WSIFPort_EJB
    
      extends WSIFDefaultPort
    
      implements Serializable
    
     
    
    {
    
      // ...snip...
    
     
    
      private void readObject(ObjectInputStream ois) throws ClassNotFoundException, IOException {
    
        ois.defaultReadObject();
    
        if (this.separatedEJBRefs) {
    
          Object objHome = ois.readObject();
    
          if (objHome != null && objHome instanceof HomeHandle) {
    
            HomeHandle homeHandle = (HomeHandle)objHome;
    
            this.fieldEjbHome = homeHandle.getEJBHome();
    
          }  
    
     
    
          Object obj = ois.readObject();
    
          if (obj != null && obj instanceof Handle) {
    
            Handle handle = (Handle)obj;
    
            this.fieldEjbObject = handle.getEJBObject();  // <----------------------    
          }  
    
        }
    
      }
    
    }
    
     
    
    public EJBObject getEJBObject() throws RemoteException {
    
      // ...snip...
    
      home = (EJBHome)PortableRemoteObject.narrow(ctx.lookup(this.homeJNDIName), homeClass); // <----    
      // ...snip...
    
      Method fbpk = findFindByPrimaryKey(homeClass); // <---- returns findFindByPrimaryKey() method
    
      this.object = (EJBObject)fbpk.invoke(home, new Object[] { this.key });   <--  $proxy.findFindByPrimaryKey(Serializable $arg)
    
    }

这个类最有趣的地方在于getEJBObject()方法，我们一起来看一看这里面的JNDI查询调用。

### CVE-2020-4450-snippet-3.java：

    
    
    com.sun.jndi.rmi.registry.RegistryContext#lookup
    
    com.sun.jndi.rmi.registry.RegistryContext#decodeObject
    
    javax.naming.spi.NamingManager#getObjectInstance
    
    org.apache.aries.jndi.OSGiObjectFactoryBuilder#getObjectInstance
    
    org.apache.aries.jndi.ObjectFactoryHelper#getObjectInstance
    
    org.apache.aries.jndi.ObjectFactoryHelper#getObjectInstanceViaContextDotObjectFactories
    
     
    
    protected Object getObjectInstanceViaContextDotObjectFactories(Object obj, Name name, Context nameCtx, Hashtable<?, ?> environment, Attributes attrs) throws Exception {
    
      Object result = null;
    
      String factories = (String)environment.get("java.naming.factory.object");
    
     
    
      if (factories != null && factories.length() > 0) {
    
        String[] candidates = factories.split(":");
    
        ClassLoader cl = (ClassLoader)AccessController.doPrivileged(new PrivilegedAction<ClassLoader>() {
    
              public ClassLoader run() {
    
                return Thread.currentThread().getContextClassLoader();
    
              }
    
        });
    
     
    
        for (String cand : candidates) {
    
          ObjectFactory factory = null;
    
          try {
    
            Class<ObjectFactory> clz = cl.loadClass(cand);
    
            factory = (ObjectFactory)clz.newInstance();
    
          } catch (Exception e) {
    
            if (logger.isLoggable(Level.FINE)) logger.log(Level.FINE, "Exception instantiating factory: " + e);
    
          }
    
     
    
          if (logger.isLoggable(Level.FINE)) logger.log(Level.FINE, "cand=" + cand + " factory=" + factory);
    
     
    
          if (factory != null) {
    
            if (factory instanceof DirObjectFactory) {
    
              if (logger.isLoggable(Level.FINE)) logger.log(Level.FINE, "its a DirObjectFactory");  
    
              DirObjectFactory dirFactory = (DirObjectFactory)factory;
    
              result = dirFactory.getObjectInstance(obj, name, nameCtx, environment, attrs);
    
            }
    
            else {
    
              if (logger.isLoggable(Level.FINE)) logger.log(Level.FINE, "its an ObjectFactory");  
    
              result = factory.getObjectInstance(obj, name, nameCtx, environment);
    
            }  
    
          }
    
     
    
          if (result != null && result != obj)
    
            break;
    
        }
    
      }  if (logger.isLoggable(Level.FINE)) logger.log(Level.FINE, "result = " + result);
    
      return (result == null) ? obj : result;
    
    }

我们可以看到，getObjectInstanceViaContextDotObjectFactories()将会调用getObjectInstance的任意ObjectFactory类，其中一个跟我们Gadget链相关的类就是WSIFServiceObjectFactory。

### CVE-2020-4450-snippet-4.java：

    
    
    public Object getObjectInstance(Object obj, Name name, Context context, Hashtable env) throws Exception {
    
      Trc.entry(this, obj, name, context, env);
    
      if (obj instanceof Reference && obj != null) {
    
        Reference ref = (Reference)obj;
    
        if (ref.getClassName().equals(WSIFServiceRef.class.getName())) {
    
          String wsdlLoc = resolveString(ref.get("wsdlLoc"));
    
          String serviceNS = resolveString(ref.get("serviceNS"));
    
          String serviceName = resolveString(ref.get("serviceName"));
    
          String portTypeNS = resolveString(ref.get("portTypeNS"));
    
          String portTypeName = resolveString(ref.get("portTypeName"));
    
          if (wsdlLoc != null) {
    
            WSIFServiceFactory factory = WSIFServiceFactory.newInstance();
    
            WSIFService service = factory.getService(wsdlLoc, serviceNS, serviceName, portTypeNS, portTypeName);
    
            Trc.exit(service);
    
            return service;
    
          }  
    
        } else if (ref.getClassName().equals(WSIFServiceStubRef.class.getName())) {
    
          String wsdlLoc = resolveString(ref.get("wsdlLoc"));
    
          String serviceNS = resolveString(ref.get("serviceNS"));
    
          String serviceName = resolveString(ref.get("serviceName"));
    
          String portTypeNS = resolveString(ref.get("portTypeNS"));
    
          String portTypeName = resolveString(ref.get("portTypeName"));
    
          String preferredPort = resolveString(ref.get("preferredPort"));
    
          String className = resolveString(ref.get("className"));
    
          if (wsdlLoc != null) {
    
            WSIFServiceFactory factory = WSIFServiceFactory.newInstance();
    
            WSIFService service = factory.getService(wsdlLoc, serviceNS, serviceName, portTypeNS, portTypeName); // <----    
            Class iface = Class.forName(className, true, Thread.currentThread().getContextClassLoader());
    
            Object stub = service.getStub(preferredPort, iface);
    
            Trc.exit(stub);
    
            return stub;
    
          }  
    
        }  
    
      }
    
    }

针对getObjectInstance()的调用将会根据一个指向远程XML定义的URL来初始化一个Web服务调用框架（[
_WSIF_](https://ws.apache.org/wsif/providers/wsdl_extensions/java_extension.html)）服务，而这个XML也是攻击者可控的。在这种场景下，服务的className会被设置为javax.el.ELProcessor，并且会定义一个java:operation元素，然后将findByPrimaryKey()映射为eval()方法。

getObjectInstance()调用将会返回一个WSIFClientProxy
Java代理对象，当findByPrimaryKey()方法被调用时，这个代理对象将会调用ELProcessor实例的eval()方法。别忘了我们已经可以通过反序列化来控制this.key参数了，那么这样一来，我们就可以通过表达式语言注入技术来实现远程代码执行了。

## 信息披露漏洞（CVE-2020-4449）

这个漏洞利用Gadget利用的是一个XXE漏洞，漏洞代码如下所示。

### CVE-2020-4450-snippet-5.java：

    
    
    public static Definition readWSDL(String contextURL, String wsdlLoc) throws WSDLException {
    
      Trc.entry(null, contextURL, wsdlLoc);
    
       
    
      initializeProviders();
    
       
    
      WSDLFactory factory = WSDLFactory.newInstance("org.apache.wsif.wsdl.WSIFWSDLFactoryImpl");
    
       
    
      WSDLReader wsdlReader = factory.newWSDLReader(); // <---------------------    
      wsdlReader.setFeature("javax.wsdl.verbose", false);
    
      try {
    
        Definition def = wsdlReader.readWSDL(contextURL, wsdlLoc); // <---------    
        Trc.exitExpandWsdl(def);
    
        return def;
    
      } catch (WSDLException e) {
    
        Trc.exception(e);
    
        MessageLogger.log("WSIF.0002E", wsdlLoc);
    
        throw e;
    
      }  
    
    }

这个Gadget还演示了如何在现代JRE中如何绕过类似的缓解方案，尤其是通过FTP来实现越界提取等等。在这种场景下，数据是通过错误信息来提取的，因此当代码在解析XML文档时，如果没有封装在一个try/catch语句中的话，那么该漏洞将产生严重影响。

## 漏洞修复

为了修复这些漏洞，IBM采取了很多措施来确保TxServerInterceptor类不再会被反序列化为任意对象：

![](https://image.3001.net/images/20200812/1597247946.png!small)

## 参考资料

  * [_https://i.blackhat.com/eu-19/Wednesday/eu-19-An-Far-Sides-Of-Java-Remote-Protocols.pdf_](https://i.blackhat.com/eu-19/Wednesday/eu-19-An-Far-Sides-Of-Java-Remote-Protocols.pdf)

