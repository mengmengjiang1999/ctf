**作者：Longofo@知道创宇404实验室**  
**时间：2019年12月10日**  
**英文版本：<https://paper.seebug.org/1100/>**

之前在一个应用中搜索到一个类，但是在反序列化测试的时出错，错误不是`class
notfound`，是其他`0xxx`这样的错误，通过搜索这个错误大概是类没有被加载。最近刚好看到了JavaAgent，初步学习了下，能进行拦截，主要通过Instrument
Agent来进行字节码增强，可以进行 **字节码插桩，bTrace，Arthas**
等操作，结合ASM，javassist，cglib框架能实现更强大的功能。 **Java RASP**
也是基于JavaAgent实现的。趁热记录下JavaAgent基础概念，以及简单使用JavaAgent实现一个获取目标进程已加载的类的测试。

#### JVMTI与Java Instrument

**Java平台调试器架构** （Java Platform Debugger
Architecture，[JPDA](https://zh.wikipedia.org/wiki/JPDA)）是一组用于调试Java代码的API（摘自维基百科）：

  * Java调试器接口（Java Debugger Interface，JDI）——定义了一个高层次Java接口，开发人员可以利用JDI轻松编写远程调试工具
  * Java虚拟机工具接口（Java Virtual Machine Tools Interface，JVMTI）——定义了一个原生（native）接口，可以对运行在Java虚拟机的应用程序检查状态、控制运行
  * Java虚拟机调试接口（JVMDI）——JVMDI在J2SE 5中被JVMTI取代，并在Java SE 6中被移除
  * Java调试线协议（JDWP）——定义了调试对象（一个 Java 应用程序）和调试器进程之间的通信协议

JVMTI 提供了一套"代理"程序机制，可以支持第三方工具程序以代理的方式连接和访问 JVM，并利用 JVMTI 提供的丰富的编程接口，完成很多跟 JVM
相关的功能。JVMTI是基于事件驱动的，JVM每执行到一定的逻辑就会调用一些事件的回调接口（如果有的话），这些接口可以供开发者去扩展自己的逻辑。

JVMTIAgent是一个利用JVMTI暴露出来的接口提供了代理启动时加载(agent on load)、代理通过attach形式加载(agent on
attach)和代理卸载(agent on unload)功能的动态库。Instrument
Agent可以理解为一类JVMTIAgent动态库，别名是JPLISAgent(Java Programming Language
Instrumentation Services Agent)，是 **专门为java语言编写的插桩服务提供支持的代理** 。

#### Instrumentation接口

以下接口是Java SE 8
[API文档中](https://docs.oracle.com/javase/8/docs/api/java/lang/instrument/Instrumentation.html)[1]提供的（不同版本可能接口有变化）：

    
    
    void addTransformer(ClassFileTransformer transformer, boolean canRetransform)//注册ClassFileTransformer实例，注册多个会按照注册顺序进行调用。所有的类被加载完毕之后会调用ClassFileTransformer实例，相当于它们通过了redefineClasses方法进行重定义。布尔值参数canRetransform决定这里被重定义的类是否能够通过retransformClasses方法进行回滚。
    
    void addTransformer(ClassFileTransformer transformer)//相当于addTransformer(transformer, false)，也就是通过ClassFileTransformer实例重定义的类不能进行回滚。
    
    boolean removeTransformer(ClassFileTransformer transformer)//移除(反注册)ClassFileTransformer实例。
    
    void retransformClasses(Class<?>... classes)//已加载类进行重新转换的方法，重新转换的类会被回调到ClassFileTransformer的列表中进行处理。
    
    void appendToBootstrapClassLoaderSearch(JarFile jarfile)//将某个jar加入到Bootstrap Classpath里优先其他jar被加载。
    
    void appendToSystemClassLoaderSearch(JarFile jarfile)//将某个jar加入到Classpath里供AppClassloard去加载。
    
    Class[] getAllLoadedClasses()//获取所有已经被加载的类。
    
    Class[] getInitiatedClasses(ClassLoader loader)//获取所有已经被初始化过了的类。
    
    long getObjectSize(Object objectToSize)//获取某个对象的(字节)大小，注意嵌套对象或者对象中的属性引用需要另外单独计算。
    
    boolean isModifiableClass(Class<?> theClass)//判断对应类是否被修改过。
    
    boolean isNativeMethodPrefixSupported()//是否支持设置native方法的前缀。
    
    boolean isRedefineClassesSupported()//返回当前JVM配置是否支持重定义类（修改类的字节码）的特性。
    
    boolean isRetransformClassesSupported()//返回当前JVM配置是否支持类重新转换的特性。
    
    void redefineClasses(ClassDefinition... definitions)//重定义类，也就是对已经加载的类进行重定义，ClassDefinition类型的入参包括了对应的类型Class<?>对象和字节码文件对应的字节数组。
    
    void setNativeMethodPrefix(ClassFileTransformer transformer, String prefix)//设置某些native方法的前缀，主要在找native方法的时候做规则匹配。

**[redefineClasses与redefineClasses](https://stackoverflow.com/questions/19009583/difference-between-redefine-and-retransform-in-javaagent)** ：

**重新定义** 功能在Java SE 5中进行了介绍， **重新转换** 功能在Java SE 6中进行了介绍，一种猜测是将 **重新转换** 作为
**更通用的功能** 引入，但是必须保留 **重新定义** 以实现向后兼容，并且 **重新转换** 操作也更加方便。

#### Instrument Agent两种加载方式

在官方[API文档](https://docs.oracle.com/javase/8/docs/api/java/lang/instrument/Instrumentation.html)[1]中提到，有两种获取Instrumentation接口实例的方法
：

  1. JVM在指定代理的方式下启动，此时Instrumentation实例会传递到代理类的premain方法。
  2. JVM提供一种在启动之后的某个时刻启动代理的机制，此时Instrumentation实例会传递到代理类代码的agentmain方法。

premain对应的就是VM启动时的Instrument Agent加载，即`agent on
load`，agentmain对应的是VM运行时的Instrument Agent加载，即`agent on
attach`。两种加载形式所加载的`Instrument Agent`都关注同一个`JVMTI`事件 –
`ClassFileLoadHook`事件，这个事件是在读取字节码文件之后回调时用，也就是说
**premain和agentmain方式的回调时机都是类文件字节码读取之后（或者说是类加载之后），之后对字节码进行重定义或重转换，不过修改的字节码也需要满足一些要求，在最后的局限性有说明**
。

**premain与agentmain的区别** ：

`premain`和`agentmain`两种方式最终的目的都是为了回调`Instrumentation`实例并激活`sun.instrument.InstrumentationImpl#transform()`（InstrumentationImpl是Instrumentation的实现类）从而回调注册到`Instrumentation`中的`ClassFileTransformer`实现字节码修改，本质功能上没有很大区别。两者的非本质功能的区别如下：

  * premain方式是JDK1.5引入的，agentmain方式是JDK1.6引入的，JDK1.6之后可以自行选择使用`premain`或者`agentmain`。

  * `premain`需要通过命令行使用外部代理jar包，即`-javaagent:代理jar包路径`；`agentmain`则可以通过`attach`机制直接附着到目标VM中加载代理，也就是使用`agentmain`方式下，操作`attach`的程序和被代理的程序可以是完全不同的两个程序。

  * `premain`方式回调到`ClassFileTransformer`中的类是虚拟机加载的所有类，这个是由于代理加载的顺序比较靠前决定的，在开发者逻辑看来就是：所有类首次加载并且进入程序`main()`方法之前，`premain`方法会被激活，然后所有被加载的类都会执行`ClassFileTransformer`列表中的回调。
  * `agentmain`方式由于是采用`attach`机制，被代理的目标程序VM有可能很早之前已经启动，当然其所有类已经被加载完成，这个时候需要借助`Instrumentation#retransformClasses(Class<?>... classes)`让对应的类可以重新转换，从而激活重新转换的类执行`ClassFileTransformer`列表中的回调。
  * 通过premain方式的代理Jar包进行了更新的话，需要重启服务器，而agentmain方式的Jar包如果进行了更新的话，需要重新attach，但是agentmain重新attach还会导致重复的字节码插入问题，不过也有`Hotswap`和`DCE VM`方式来避免。

通过下面的测试也能看到它们之间的一些区别。

##### premain加载方式

premain方式编写步骤简单如下：

1.编写premain函数，包含下面两个方法的其中之一：

`java public static void premain(String agentArgs, Instrumentation inst);
public static void premain(String agentArgs);`

如果两个方法都被实现了，那么带Instrumentation参数的优先级高一些，会被优先调用。`agentArgs`是`premain`函数得到的程序参数，通过命令行参数传入

2.定义一个 MANIFEST.MF 文件，必须包含 Premain-Class 选项，通常也会加入Can-Redefine-Classes 和 Can-Retransform-Classes 选项

3.将 premain 的类和 MANIFEST.MF 文件打成 jar 包

4.使用参数 -javaagent: jar包路径启动代理

premain加载过程如下：

1.创建并初始化 JPLISAgent  
2.MANIFEST.MF 文件的参数，并根据这些参数来设置 JPLISAgent 里的一些内容  
3.监听 `VMInit` 事件，在 JVM 初始化完成之后做下面的事情：  
（1）创建 InstrumentationImpl 对象 ；  
（2）监听 ClassFileLoadHook 事件 ；  
（3）调用 InstrumentationImpl 的`loadClassAndCallPremain`方法，在这个方法里会去调用 javaagent 中
MANIFEST.MF 里指定的Premain-Class 类的 premain 方法

下面是一个简单的例子（在JDK1.8.0_181进行了测试）：

PreMainAgent

    
    
    package com.longofo;
    
    import java.lang.instrument.ClassFileTransformer;
    import java.lang.instrument.IllegalClassFormatException;
    import java.lang.instrument.Instrumentation;
    import java.security.ProtectionDomain;
    
    public class PreMainAgent {
        static {
            System.out.println("PreMainAgent class static block run...");
        }
    
        public static void premain(String agentArgs, Instrumentation inst) {
            System.out.println("PreMainAgent agentArgs : " + agentArgs);
            Class<?>[] cLasses = inst.getAllLoadedClasses();
    
            for (Class<?> cls : cLasses) {
                System.out.println("PreMainAgent get loaded class:" + cls.getName());
            }
    
            inst.addTransformer(new DefineTransformer(), true);
        }
    
        static class DefineTransformer implements ClassFileTransformer {
    
            @Override
            public byte[] transform(ClassLoader loader, String className, Class<?> classBeingRedefined, ProtectionDomain protectionDomain, byte[] classfileBuffer) throws IllegalClassFormatException {
                System.out.println("PreMainAgent transform Class:" + className);
                return classfileBuffer;
            }
        }
    }

MANIFEST.MF：

    
    
    Manifest-Version: 1.0
    Can-Redefine-Classes: true
    Can-Retransform-Classes: true
    Premain-Class: com.longofo.PreMainAgent

Testmain

    
    
    package com.longofo;
    
    public class TestMain {
    
        static {
            System.out.println("TestMain static block run...");
        }
    
        public static void main(String[] args) {
            System.out.println("TestMain main start...");
            try {
                for (int i = 0; i < 100; i++) {
                    Thread.sleep(3000);
                    System.out.println("TestMain main running...");
                }
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            System.out.println("TestMain main end...");
        }
    }

将PreMainAgent打包为Jar包（可以直接用idea打包，也可以使用maven插件打包），在idea可以像下面这样启动：

![](https://images.seebug.org/content/images/2019/12/11/1576048102000-1.png-w331s)

命令行的话可以用形如`java -javaagent:PreMainAgent.jar路径 -jar TestMain/TestMain.jar`启动

结果如下：

    
    
    PreMainAgent class static block run...
    PreMainAgent agentArgs : null
    PreMainAgent get loaded class:com.longofo.PreMainAgent
    PreMainAgent get loaded class:sun.reflect.DelegatingMethodAccessorImpl
    PreMainAgent get loaded class:sun.reflect.NativeMethodAccessorImpl
    PreMainAgent get loaded class:sun.instrument.InstrumentationImpl$1
    PreMainAgent get loaded class:[Ljava.lang.reflect.Method;
    ...
    ...
    PreMainAgent transform Class:sun/nio/cs/ThreadLocalCoders
    PreMainAgent transform Class:sun/nio/cs/ThreadLocalCoders$1
    PreMainAgent transform Class:sun/nio/cs/ThreadLocalCoders$Cache
    PreMainAgent transform Class:sun/nio/cs/ThreadLocalCoders$2
    ...
    ...
    PreMainAgent transform Class:java/lang/Class$MethodArray
    PreMainAgent transform Class:java/net/DualStackPlainSocketImpl
    PreMainAgent transform Class:java/lang/Void
    TestMain static block run...
    TestMain main start...
    PreMainAgent transform Class:java/net/Inet6Address
    PreMainAgent transform Class:java/net/Inet6Address$Inet6AddressHolder
    PreMainAgent transform Class:java/net/SocksSocketImpl$3
    ...
    ...
    PreMainAgent transform Class:java/util/LinkedHashMap$LinkedKeySet
    PreMainAgent transform Class:sun/util/locale/provider/LocaleResources$ResourceReference
    TestMain main running...
    TestMain main running...
    ...
    ...
    TestMain main running...
    TestMain main end...
    PreMainAgent transform Class:java/lang/Shutdown
    PreMainAgent transform Class:java/lang/Shutdown$Lock

可以看到在PreMainAgent之前已经加载了一些必要的类，即PreMainAgent get loaded
class：xxx部分，这些类没有经过transform。然后在main之前有一些类经过了transform，在main启动之后还有类经过transform，main结束之后也还有类经过transform，可以和agentmain的结果对比下。

##### agentmain加载方式

agentmain方式编写步骤简单如下：

1.编写agentmain函数，包含下面两个方法的其中之一：

    
    
       public static void agentmain(String agentArgs, Instrumentation inst);
       public static void agentmain(String agentArgs);

如果两个方法都被实现了，那么带Instrumentation参数的优先级高一些，会被优先调用。`agentArgs`是`premain`函数得到的程序参数，通过命令行参数传入

2.定义一个 MANIFEST.MF 文件，必须包含 Agent-Class 选项，通常也会加入Can-Redefine-Classes 和 Can-Retransform-Classes 选项

3.将 agentmain 的类和 MANIFEST.MF 文件打成 jar 包

4.通过attach工具直接加载Agent，执行attach的程序和需要被代理的程序可以是两个完全不同的程序：

    
    
       // 列出所有VM实例
       List<VirtualMachineDescriptor> list = VirtualMachine.list();
       // attach目标VM
       VirtualMachine.attach(descriptor.id());
       // 目标VM加载Agent
       VirtualMachine#loadAgent("代理Jar路径","命令参数");

agentmain方式加载过程类似：

1.创建并初始化JPLISAgent  
2.解析MANIFEST.MF 里的参数，并根据这些参数来设置 JPLISAgent 里的一些内容  
3.监听 `VMInit` 事件，在 JVM 初始化完成之后做下面的事情：  
（1）创建 InstrumentationImpl 对象 ；  
（2）监听 ClassFileLoadHook 事件 ；  
（3）调用 InstrumentationImpl 的`loadClassAndCallAgentmain`方法，在这个方法里会去调用javaagent里
MANIFEST.MF 里指定的`Agent-Class`类的`agentmain`方法。

下面是一个简单的例子（在JDK 1.8.0_181上进行了测试）：

SufMainAgent

    
    
    package com.longofo;
    
    import java.lang.instrument.ClassFileTransformer;
    import java.lang.instrument.IllegalClassFormatException;
    import java.lang.instrument.Instrumentation;
    import java.security.ProtectionDomain;
    
    public class SufMainAgent {
        static {
            System.out.println("SufMainAgent static block run...");
        }
    
        public static void agentmain(String agentArgs, Instrumentation instrumentation) {
            System.out.println("SufMainAgent agentArgs: " + agentArgs);
    
            Class<?>[] classes = instrumentation.getAllLoadedClasses();
            for (Class<?> cls : classes) {
                System.out.println("SufMainAgent get loaded class: " + cls.getName());
            }
    
            instrumentation.addTransformer(new DefineTransformer(), true);
        }
    
        static class DefineTransformer implements ClassFileTransformer {
    
            @Override
            public byte[] transform(ClassLoader loader, String className, Class<?> classBeingRedefined, ProtectionDomain protectionDomain, byte[] classfileBuffer) throws IllegalClassFormatException {
                System.out.println("SufMainAgent transform Class:" + className);
                return classfileBuffer;
            }
        }
    }

MANIFEST.MF

    
    
    Manifest-Version: 1.0
    Can-Redefine-Classes: true
    Can-Retransform-Classes: true
    Agent-Class: com.longofo.SufMainAgent

TestSufMainAgent

    
    
    package com.longofo;
    
    import com.sun.tools.attach.*;
    
    import java.io.IOException;
    import java.util.List;
    
    public class TestSufMainAgent {
        public static void main(String[] args) throws IOException, AgentLoadException, AgentInitializationException, AttachNotSupportedException {
            //获取当前系统中所有 运行中的 虚拟机
            System.out.println("TestSufMainAgent start...");
            String option = args[0];
            List<VirtualMachineDescriptor> list = VirtualMachine.list();
            if (option.equals("list")) {
                for (VirtualMachineDescriptor vmd : list) {
                    //如果虚拟机的名称为 xxx 则 该虚拟机为目标虚拟机，获取该虚拟机的 pid
                    //然后加载 agent.jar 发送给该虚拟机
                    System.out.println(vmd.displayName());
                }
            } else if (option.equals("attach")) {
                String jProcessName = args[1];
                String agentPath = args[2];
                for (VirtualMachineDescriptor vmd : list) {
                    if (vmd.displayName().equals(jProcessName)) {
                        VirtualMachine virtualMachine = VirtualMachine.attach(vmd.id());
                        virtualMachine.loadAgent(agentPath);
                    }
                }
            }
        }
    }

Testmain

    
    
    package com.longofo;
    
    public class TestMain {
    
        static {
            System.out.println("TestMain static block run...");
        }
    
        public static void main(String[] args) {
            System.out.println("TestMain main start...");
            try {
                for (int i = 0; i < 100; i++) {
                    Thread.sleep(3000);
                    System.out.println("TestMain main running...");
                }
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            System.out.println("TestMain main end...");
        }
    }

将SufMainAgent和TestSufMainAgent打包为Jar包（可以直接用idea打包，也可以使用maven插件打包），首先启动Testmain，然后先列下当前有哪些Java程序：

![](https://images.seebug.org/content/images/2019/12/11/1576048102000-2.png-w331s)

attach SufMainAgent到Testmain：

![](https://images.seebug.org/content/images/2019/12/11/1576048102000-3.png-w331s)

在Testmain中的结果如下：

    
    
    TestMain static block run...
    TestMain main start...
    TestMain main running...
    TestMain main running...
    TestMain main running...
    ...
    ...
    SufMainAgent static block run...
    SufMainAgent agentArgs: null
    SufMainAgent get loaded class: com.longofo.SufMainAgent
    SufMainAgent get loaded class: com.longofo.TestMain
    SufMainAgent get loaded class: com.intellij.rt.execution.application.AppMainV2$1
    SufMainAgent get loaded class: com.intellij.rt.execution.application.AppMainV2
    ...
    ...
    SufMainAgent get loaded class: java.lang.Throwable
    SufMainAgent get loaded class: java.lang.System
    ...
    ...
    TestMain main running...
    TestMain main running...
    ...
    ...
    TestMain main running...
    TestMain main running...
    TestMain main end...
    SufMainAgent transform Class:java/lang/Shutdown
    SufMainAgent transform Class:java/lang/Shutdown$Lock

和前面premain对比下就能看出，在agentmain中直接getloadedclasses的类数目比在premain直接getloadedclasses的数量多，而且premain
getloadedclasses的类+premain transform的类和agentmain
getloadedclasses基本吻合（只针对这个测试，如果程序中间还有其他通信，可能会不一样）。也就是说某个类之前没有加载过，那么都会通过两者设置的transform，这可以从最后的java/lang/Shutdown看出来。

#### 测试Weblogic的某个类是否被加载

这里使用weblogic进行测试，代理方式使用agentmain方式（在jdk1.6.0_29上进行了测试）：

WeblogicSufMainAgent

    
    
    import java.lang.instrument.ClassFileTransformer;
    import java.lang.instrument.IllegalClassFormatException;
    import java.lang.instrument.Instrumentation;
    import java.security.ProtectionDomain;
    
    public class WeblogicSufMainAgent {
        static {
            System.out.println("SufMainAgent static block run...");
        }
    
        public static void agentmain(String agentArgs, Instrumentation instrumentation) {
            System.out.println("SufMainAgent agentArgs: " + agentArgs);
    
            Class<?>[] classes = instrumentation.getAllLoadedClasses();
            for (Class<?> cls : classes) {
                System.out.println("SufMainAgent get loaded class: " + cls.getName());
            }
    
            instrumentation.addTransformer(new DefineTransformer(), true);
        }
    
        static class DefineTransformer implements ClassFileTransformer {
    
            @Override
            public byte[] transform(ClassLoader loader, String className, Class<?> classBeingRedefined, ProtectionDomain protectionDomain, byte[] classfileBuffer) throws IllegalClassFormatException {
                System.out.println("SufMainAgent transform Class:" + className);
                return classfileBuffer;
            }
        }
    }

WeblogicTestSufMainAgent：

    
    
    import com.sun.tools.attach.*;
    
    import java.io.IOException;
    import java.util.List;
    
    public class WeblogicTestSufMainAgent {
        public static void main(String[] args) throws IOException, AgentLoadException, AgentInitializationException, AttachNotSupportedException {
            //获取当前系统中所有 运行中的 虚拟机
            System.out.println("TestSufMainAgent start...");
            String option = args[0];
            List<VirtualMachineDescriptor> list = VirtualMachine.list();
            if (option.equals("list")) {
                for (VirtualMachineDescriptor vmd : list) {
                    //如果虚拟机的名称为 xxx 则 该虚拟机为目标虚拟机，获取该虚拟机的 pid
                    //然后加载 agent.jar 发送给该虚拟机
                    System.out.println(vmd.displayName());
                }
            } else if (option.equals("attach")) {
                String jProcessName = args[1];
                String agentPath = args[2];
                for (VirtualMachineDescriptor vmd : list) {
                    if (vmd.displayName().equals(jProcessName)) {
                        VirtualMachine virtualMachine = VirtualMachine.attach(vmd.id());
                        virtualMachine.loadAgent(agentPath);
                    }
                }
            }
        }
    }

列出正在运行的Java应用程序：

![](https://images.seebug.org/content/images/2019/12/11/1576048103000-4.png-w331s)

进行attach：

![](https://images.seebug.org/content/images/2019/12/11/1576048103000-5.png-w331s)

Weblogic输出：

![](https://images.seebug.org/content/images/2019/12/11/1576048103000-6.png-w331s)

假如在进行Weblogic
t3反序列化利用时，如果某个类之前没有被加载，但是能够被Weblogic找到，那么利用时对应的类会通过Agent的transform，但是有些类虽然在Weblogic目录下的某些Jar包中，但是weblogic不会去加载，需要一些特殊的配置Weblogic才会去寻找并加载。

#### Instrumentation局限性

大多数情况下，使用Instrumentation都是使用其字节码插桩的功能，笼统说是 **类重转换** 的功能，但是有以下的局限性：

  1. premain和agentmain两种方式修改字节码的时机都是类文件加载之后，就是说必须要带有Class类型的参数，不能通过字节码文件和 **自定义的类名** 重新定义一个本来 **不存在** 的类。这里需要注意的就是上面提到过的重新定义，刚才这里说的 **不能重新定义** 是指不能重新换一个类名，字节码内容依然能重新定义和修改，不过字节码内容修改后也要满足第二点的要求。 
  2. 类转换其实最终都回归到类重定义Instrumentation#retransformClasses()方法，此方法有以下限制：   
1.新类和老类的父类必须相同；  
2.新类和老类实现的接口数也要相同，并且是相同的接口；  
3.新类和老类访问符必须一致。 新类和老类字段数和字段名要一致；  
4.新类和老类新增或删除的方法必须是private static/final修饰的；  
5.可以删除修改方法体。

实际中遇到的限制可能不止这些，遇到了再去解决吧。如果想要重新定义一全新类（类名在已加载类中不存在），可以考虑基于类加载器隔离的方式：创建一个新的自定义类加载器去通过新的字节码去定义一个全新的类，不过只能通过反射调用该全新类的局限性。

#### 小结

  * 文中只是描述了JavaAgent相关的一些基础的概念，目的只是知道有这个东西，然后验证下之前遇到的一个问题。写的时候也借鉴了其他大佬写的几篇文章[4]&[5]
  * 在写文章的过程中看了一些如[一类PHP-RASP实现的漏洞检测的思路](https://c0d3p1ut0s.github.io/%E4%B8%80%E7%B1%BBPHP-RASP%E7%9A%84%E5%AE%9E%E7%8E%B0/)[6]，利用了污点跟踪、hook、语法树分析等技术，也看了几篇大佬们整理的Java RASP相关文章[2]&[3]，如果自己要写基于RASP的漏洞检测/利用工具的话也可以借鉴到这些思路

代码放到了[github](https://github.com/longofo/learn-javaagent)上，有兴趣的可以去测试下，注意pom.xml文件中的jdk版本，在切换JDK测试如果出现错误，记得修改pom.xml里面的JDK版本。

#### 参考

1.<https://docs.oracle.com/javase/8/docs/api/java/lang/instrument/Instrumentation.html>  
2.<https://paper.seebug.org/513/#0x01-rasp>  
3.<https://paper.seebug.org/1041/#31-java-agent>  
4.<http://www.throwable.club/2019/06/29/java-understand-instrument-first/#Instrumentation%E6%8E%A5%E5%8F%A3%E8%AF%A6%E8%A7%A3>  
5.<https://www.cnblogs.com/rickiyang/p/11368932.html>  
6.<https://c0d3p1ut0s.github.io/%E4%B8%80%E7%B1%BBPHP-RASP%E7%9A%84%E5%AE%9E%E7%8E%B0/>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1099/>

