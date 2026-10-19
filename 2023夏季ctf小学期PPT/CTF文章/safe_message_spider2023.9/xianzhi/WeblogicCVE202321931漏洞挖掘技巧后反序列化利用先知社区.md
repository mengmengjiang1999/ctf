# 概述

近些年，Weblogic反序列化漏洞一直围绕着反序列化的触发点进行漏洞挖掘，事实上还有很多存在反序列化但无法实时利用的点，在大家平时的漏洞挖掘中容易忽略。在行业内也有一些关于”后反序列化“的进一步讨论，这些看似无法利用的漏洞，其实可以通过一些后续的技巧完成稳定的利用效果。例如，进行`bind()`或`rebind()`操作后，并没有触发漏洞，此时可以尝试其他方法如`lookup()`、`lookupLink()`等触发漏洞。

通过这种思路我们发现了两个Weblogic的后反序列化漏洞（CVE-2023-21931、CVE-2023-21839），获得了Oracle的官方确认。本文以这两个Weblogic漏洞为例，分享"后反序列化漏洞"的利用思路。我们相信还有很多这类的漏洞在未来会逐渐被挖掘出来，希望本篇文章能够给大家一些启发。

# 后序列化漏洞

![](./img/834672041849679588.png)

Weblogic反序列化漏洞挖掘思路是利用
`readObject()`、`readResolve()`、`readExternal()`等反序列化方法对恶意序列化数据进行操作，以达到攻击目的。常规的漏洞思路重点关注Weblogic在反序列化过程中进行恶意攻击，而忽略了反序列化完成后的操作。后反序列化漏洞挖掘的思路重点关注Weblogic完成反序列化过程后，在达到某个时机或执行操作后触发的漏洞攻击。

在Weblogic中，如果进行`bind()`或`rebind()`操作后，并没有触发漏洞，此时可以尝试其他方法如`lookup()`、`lookupLink()`等触发漏洞。

本文将以 `lookup()` 方法作为漏洞触发点，对 Weblogic 后反序列化漏洞的攻击过程进行分析和漏洞实例展示。

# lookup

通过跟踪调用堆栈，我们发现`lookup()`的流程如下：

  * Weblogic在接收到请求后，通过`BasicServerRef`类中的`invoke()`方法解析传入数据。

  * 通过`_invoke()`方法，Weblogic根据传入的方法名`resolve_any` 执行的`resolve_any()`方法。

  * 在`resolve_any()`方法中，通过`resolveObject()`方法对传入的绑定命名进行解析。

  * 在`resolveObject()`方法中，根据上下文信息调用其中的`lookup()`方法。

  * 根据上下文中的信息，经过在`WLContextImpl`、`WLEventContextImpl`、 `WLEventContextImpl` 、`RootNamingNode`、`ServerNamingNode` 、`BasicNamingNode`类中一系列的`lookup()`方法调用，实现`BasicNamingNode`类中的`resolveObject()`方法调用。

  * 由于传入`resolveObject()`方法中的obj不是`NamingNode`类的实例，且`mode`的值默认为1，所以会调用`WLNamingManager`类中的`getObjectInstance()`方法。

![](./img/538318580367736231.png)

最终，可以看到`WLNamingManager`类的`getObjectInstance()`方法根据传入的对象接口类型，调用对象中的`getReferent()`方法，完成漏洞触发点的`lookup()`方法调用。实际上这两个CVE漏洞都是通过`getObjectInstance()`的两个分支触发的。

# CVE-2023-21931

CVE-2023-21931的漏洞触发点在`WLNamingManager`类的 `getObjectInstance()`方法中，当传入的
`boundObject` 对象是 `LinkRef` 的实现类时，则调用传入对象 `boundObject` 的 `getLinkName()`
方法，并通过`lookup()` 方法对 `getLinkName()` 方法返回的 `linkAddrType` 地址进行远程JNDI加载。在实例化
`LinkRef` 类时，可以通过类中的构造方法给 `linkAddrType` 传入一个JNDI地址。这样，我们就可以调用 `lookup()`
方法对自定义的JNDI地址进行远程加载，达到攻击的目的。

    
    
    package weblogic.jndi.internal;
    public final class WLNamingManager {
        public static Object getObjectInstance(Object boundObject, Name name, Context ctx, Hashtable env) throws NamingException {
            if (boundObject instanceof ClassTypeOpaqueReference) {
                            ......
            } else if (boundObject instanceof LinkRef) {
                String linkName = ((LinkRef)boundObject).getLinkName();
                InitialContext ic = null;
                try {
                    ic = new InitialContext(env);
                    boundObject = ic.lookup(linkName);  // 漏洞触发点
                } catch (NamingException var15) {
                  ......
                } finally {......}
            }
        }
    }
    

漏洞JNDI地址构造在`LinkRef`这个类中，`LinkRef`是Java的一个原生类。通过`LinkRef`类中的构造方法，我们可以控制变量`linkAddrType`的值，
再通过`getLinkName()`方法将`linkAddrType`作为字符串返回。

    
    
    package javax.naming;
    public class LinkRef extends Reference {
        static final String linkClassName = LinkRef.class.getName();
        static final String linkAddrType = "LinkAddress";
    
        public LinkRef(Name linkName) {
            super(linkClassName, new StringRefAddr(linkAddrType, linkName.toString()));
        }
    
        public LinkRef(String linkName) {
            super(linkClassName, new StringRefAddr(linkAddrType, linkName));
        }
    
        public String getLinkName() throws NamingException {
            if (className != null && className.equals(linkClassName)) {
                RefAddr addr = get(linkAddrType);
                if (addr != null && addr instanceof StringRefAddr) {
                    return (String)((StringRefAddr)addr).getContent();
                }
            }
            throw new MalformedLinkException();
        }
    }
    

![](./img/2367349595511763797.png)

在上述过程中，`rebind()`和`lookup()`方法的反序列化过程并未执行恶意操作，而是在完成反序列化之后，通过调用类`WLNamingManager`中`getObjectInstance()`方法的`lookup()`才触发漏洞，进行远程恶意加载JNDI地址操作的。

我们在GOBY中已经集成了CVE-2023-21931漏洞，并加入了回显和反弹shell的功能。演示效果如下：

![](./img/8077863524936952822.png)

# CVE-2023-21839

`ForeignOpaqueReference`是`OpaqueReference`接口的实现类。在`ForeignOpaqueReference`类中声明了两个私有变量：`jndiEnvironment`和`remoteJNDIName`，同时声明了两个构造方法，在有参构造方法中接收`env`和`remoteJNDIName`，并分别赋值给了上面的两个私有类变量。

`ForeignOpaqueReference`类的`getReferent()`方法是`OpaqueReference`接口的实现方法，在`getReferent()`方法中，`retVal
= context.lookup(this.remoteJNDIName);`
对本类`remoteJNDIName`变量中的JNDI地址进行远程加载，导致了反序列化漏洞。

    
    
    package weblogic.jndi.internal;
    public class ForeignOpaqueReference implements OpaqueReference, Serializable {
        private Hashtable jndiEnvironment;
        private String remoteJNDIName;
            ......
        public ForeignOpaqueReference(String remoteJNDIName, Hashtable env) {
            this.remoteJNDIName = remoteJNDIName;
            this.jndiEnvironment = env;
        }
        public Object getReferent(Name name, Context ctx) throws NamingException {
            InitialContext context;
            if (this.jndiEnvironment == null) {
                context = new InitialContext();
            } else {
                Hashtable properties = this.decrypt();
                context = new InitialContext(properties);
            }
            Object retVal;
            try {
                retVal = context.lookup(this.remoteJNDIName);   // 漏洞点
            } finally {
                context.close();
            }
            return retVal;
        }
        ......
    }
    

**getReferent()调用分析**

    
    
    package weblogic.jndi;
    public interface OpaqueReference {
        Object getReferent(Name var1, Context var2) throws NamingException;
        String toString();
    }
    

`OpaqueReference` 接口有两个抽象方法：`getReferent()` 和 `toString()`;

`ForeignOpaqueReference` 类的 `getReferent()` 方法调用在`WLNamingManager`类中。

在 `WLNamingManager` 类的 `getObjectInstance()` 方法中，当传入的 `boundObject` 对象实现了
`OpaqueReference` 接口时，则会调用该对象的 `getReferent()` 方法，即 `boundObject =
((OpaqueReference)boundObject).getReferent(name, ctx);`。

正如上方提到的 `ForeignOpaqueReference` 类实现了 `OpaqueReference` 接口，因此会调用该类中的
`getReferent()` 方法，导致反序列化代码执行漏洞。

    
    
    package weblogic.jndi.internal;
    public final class WLNamingManager {
        public static Object getObjectInstance(Object boundObject, Name name, Context ctx, Hashtable env) throws NamingException {
            if (boundObject instanceof ClassTypeOpaqueReference) {
                            ......
            } else if (boundObject instanceof OpaqueReference) {
                boundObject = ((OpaqueReference)boundObject).getReferent(name, ctx);
            } else if (boundObject instanceof LinkRef) {
          ...
            }
        }
    }
    

![](./img/8678711248504693099.png)

与CVE-2023-21931漏洞原理相同，CVE-2023-21839也是在反序列化过程中没有进行恶意操作，而是完成反序列化过程后执行了漏洞类`ForeignOpaqueReference`中`getReferent()`方法中的`lookup()`才触发的漏洞。

在GOBY中，我们已经集成了CVE-2023-21839漏洞，并添加了回显以及反弹Shell的功能。以下是演示效果：

![](./img/3402504244862482145.png)

# 时间线

CVE-2023-21931

  * 2022年8月12日 漏洞提交官方

  * 2022年8月19日 漏洞官方确认

  * 2023年4月18日 漏洞官方修复

CVE-2023-21839

  * 2022年7月31日 漏洞提交官方
  * 2022年8月5日 漏洞官方确认
  * 2023年1月16日 漏洞官方修复

# 研究环境

Vulfocus weblogic 环境

    
    
    docker pull vulfocus/vcpe-1.0-a-oracle-weblogic:12.2.1.2.0-jdk-release
    docker pull vulfocus/vcpe-1.0-a-oracle-weblogic:12.2.1.1.0-jdk-release
    docker pull vulfocus/vcpe-1.0-a-oracle-weblogic:12.2.1.3.0-jdk-release
    docker pull vulfocus/vcpe-1.0-a-oracle-weblogic:12.2.1.4.0-jdk-release
    docker pull vulfocus/vcpe-1.0-a-oracle-weblogic:12.2.1.0.0-jdk-release
    docker pull vulfocus/vcpe-1.0-a-oracle-weblogic:14.1.1.0.0-jdk-release
    docker pull vulfocus/vcpe-1.0-a-oracle-weblogic:12.1.2.0.0-jdk-release
    docker pull vulfocus/vcpe-1.0-a-oracle-weblogic:12.1.3.0.0-jdk-release
    docker pull vulfocus/vcpe-1.0-a-oracle-weblogic:10.3.6.0-jdk-release
    

# 参考

[Java“后反序列化漏洞”利用思路 - Ruilin (rui0.cn)](http://rui0.cn/archives/1338)

[Ruil1n/after-deserialization-attack: Java After-Deserialization Attack
(github.com)](https://github.com/Ruil1n/after-deserialization-attack)

