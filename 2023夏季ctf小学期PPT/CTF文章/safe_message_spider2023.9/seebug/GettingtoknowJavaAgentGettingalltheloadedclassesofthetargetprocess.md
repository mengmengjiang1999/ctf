**Author：Longofo@Knownsec 404 Team**  
**Time: December 10, 2019**  
**Chinese version:<https://paper.seebug.org/1099/>**

An error occurred during the deserialization test with a class in an
application. The error was not `class notfound`, but other`0xxx` errors. After
some researches, I found that it was probably because the class was not
loaded. I just studied the JavaAgent recently and learned that it can
intercept. It mainly uses the Instrument Agent to enhance bytecode. It can
perform operations such as **byte code instrumentation** , **bTrace** ,
**Arthas**. Combined with ASM, javassist, the cglib framework can achieve more
powerful functions. **Java RASP** is also implemented based on JavaAgent. The
following records the basic concepts of JavaAgent, and I'll introduce how I
used JavaAgent to implement a test to get the classes loaded by the target
process.

#### JVMTI & Java Instrument

The **Java Platform Debugger Architecture**
([JPDA](https://en.wikipedia.org/wiki/Java_Platform_Debugger_Architecture)) is
a collection of APIs to debug Java code:

  * Java Debugger Interface (JDI) - defines a high-level Java language interface that developers can easily use to write remote debugger application tools.
  * [Java Virtual Machine Tools Interface](https://en.wikipedia.org/wiki/Java_Virtual_Machine_Tools_Interface) (JVMTI), a native interface that helps to inspect the state and to control the execution of applications running in the [Java Virtual Machine](https://en.wikipedia.org/wiki/Java_Virtual_Machine) ([JVM](https://en.wikipedia.org/wiki/JVM)).
  * Java Virtual Machine Debug Interface (JVMDI)- JVMDI was deprecated in J2SE 5.0 in favor of JVM TI, and was removed in Java SE 6.
  * Java Debug Wire Protocol (JDWP) - defines communication between debuggee (a Java application) and debugger processes.

JVMTI provides a set of "agent" program mechanisms, supporting third-party
tools to connect and access the JVM in a proxy manner, and use the rich
programming interface provided by JVMTI to complete many JVM-related
functions. JVMTI is event-driven. Every time the JVM executes certain logic,
it will call some event callback interfaces (if any). These interfaces can be
used by developers to extend their own logic.

JVMTIAgent is a dynamic library that provides the functions of agent on load,
agent on attach, and agent on unload by using the interface exposed by JVMTI.
Instrument Agent can be understood as a type of JVMTIAgent dynamic library. It
is also called JPLISAgent (Java Programming Language Instrumentation Services
Agent), which is the agent that provides support for instrumentation services
written in the Java language.

#### Instrumentation Interface

The following interfaces are provided by Java SE 8 [in the API
documentation](https://docs.oracle.com/javase/8/docs/api/java/lang/instrument/Instrumentation.html)
[1] (different versions may have different interfaces):

    
    
    void    addTransformer(ClassFileTransformer transformer)
    Registers the supplied transformer.
    void    addTransformer(ClassFileTransformer transformer, boolean canRetransform)
    Registers the supplied transformer.
    void    appendToBootstrapClassLoaderSearch(JarFile jarfile)
    Specifies a JAR file with instrumentation classes to be defined by the bootstrap class loader.
    void    appendToSystemClassLoaderSearch(JarFile jarfile)
    Specifies a JAR file with instrumentation classes to be defined by the system class loader.
    Class[] getAllLoadedClasses()
    Returns an array of all classes currently loaded by the JVM.
    Class[] getInitiatedClasses(ClassLoader loader)
    Returns an array of all classes for which loader is an initiating loader.
    long    getObjectSize(Object objectToSize)
    Returns an implementation-specific approximation of the amount of storage consumed by the specified object.
    boolean isModifiableClass(Class<?> theClass)
    Determines whether a class is modifiable by retransformation or redefinition.
    boolean isNativeMethodPrefixSupported()
    Returns whether the current JVM configuration supports setting a native method prefix.
    boolean isRedefineClassesSupported()
    Returns whether or not the current JVM configuration supports redefinition of classes.
    boolean isRetransformClassesSupported()
    Returns whether or not the current JVM configuration supports retransformation of classes.
    void    redefineClasses(ClassDefinition... definitions)
    Redefine the supplied set of classes using the supplied class files.
    boolean removeTransformer(ClassFileTransformer transformer)
    Unregisters the supplied transformer.
    void    retransformClasses(Class<?>... classes)
    Retransform the supplied set of classes.
    void    setNativeMethodPrefix(ClassFileTransformer transformer, String prefix)
    This method modifies the failure handling of native method resolution by allowing retry with a prefix applied to the name.

**[redefineClasses&
retransformClasses](https://stackoverflow.com/questions/19009583/difference-between-redefine-and-retransform-in-javaagent)**：

redefineClasses was introduced in Java SE 5, and retransformClasses in Java SE
6. We may use retransformClasses as a more general feature, but
redefineClasses must be retained for backward compatibility, and
retransformClasses can be more convenient.

#### Two Loading Methods of Instrument Agent

As mentioned in the official [API
documentation](https://docs.oracle.com/javase/8/docs/api/java/lang/instrument/Instrumentation.html)[1],
there are two ways to get Instrumentation interface instance:

  1. When a JVM is launched in a way that indicates an agent class. In that case an `Instrumentation` instance is passed to the `premain` method of the agent class.
  2. When a JVM provides a mechanism to start agents sometime after the JVM is launched. In that case an `Instrumentation` instance is passed to the `agentmain` method of the agent code.

`Premain` refers to the Instrument Agent load when the VM starts, that is
`agent on load`, and the `agentmain` refers to the Instrument Agent load when
the VM runs, that is `agent on attach`. The Instrument Agent loaded by the two
loading forms both monitor the same `JVMTI` event - the`ClassFileLoadHook`
event. This event is used in the callback when we finish reading bytecode,
that is, in the premain and agentmain modes. The callback timing is after the
class file bytecode is read (or after the class is loaded), and then the
bytecode is redefined or retransformed. However, the modified bytecode also
needs to meet some requirements.

#### Difference between premain and agentmain

The final purpose of `premain` and`agentmain` is to call back the
`Instrumentation` instance and activate
`sun.instrument.InstrumentationImpl#transform ()`(InstrumentationImpl is the
implementation class of Instrumentation) so that the callback is registered to
`ClassFileTransformer` in`Instrumentation` to implement bytecode modification,
and there is not much difference in essence. The non-essential functions of
the two are as follows:

  * The premain method is introduced by JDK1.5, and the agentmain method is introduced by JDK1.6. After JDK1.6, you can choose to use `premain` or `agentmain`.

  * `premain` needs to use the external agent jar package from the command line, that is, `-javaagent: agent jar package path`; `agentmain` can be directly attached to the target VM via the`attach` mechanism to load the agent, that is, use `agentmain` In this mode, the program that operates `attach` and the proxy program can be two completely different programs.

  * The classes in the `premain` callback to the`ClassFileTransformer` are all the classes loaded by the virtual machine. This is because the order of loading by the proxy is determined earlier. From the perspective of developer logic, all classes are loaded for the first time and enter the program. Before the main () method, the premain method will be activated, and then all loaded classes will execute the callback in the ClassFileTransformer list.
  * Because the `agentmain` method uses the `attach` mechanism, the target target VM of the agent may have been started long ago. Of course, all its classes have been loaded. At this time, you need to use the `Instrumentation#retransformClasses(Class <?>. .. classes)` to allow the corresponding class to be retransformed, thereby activating the retransformed class to execute the callback in the `ClassFileTransformer` list. 
  * If the agent Jar package through the premain method is updated, the server needs to be restarted, and if the agent package Jar is updated, it needs to be reattached, but the agentmain reattach will also cause duplicate bytecode insertion problems, but there are also problems `Hotswap` and`DCE VM` way to avoid.

We can also see some differences between them through the following tests.

##### premain loading method

The steps to write in premain are as follows:

1.Write the premain function, which contains one of the following two methods:

    
    
        public static void premain (String agentArgs, Instrumentation inst);
        public static void premain (String agentArgs);
    
    
    If both methods are implemented, then the priority with the Instrumentation parameter is higher, and it will be called first. `agentArgs` is the program parameter obtained by the` premain` function. It is passed in via the command line parameter.

2.Define a MANIFEST.MF file, which must include the Premain-Class option, and
usually include the Can-Redefine-Classes and Can-Retransform-Classes options

3.Premain class and MANIFEST.MF file into a jar package

4.Start the agent with the parameter `-javaagent: jar package path`

The premain loading process is as follows:

1.Create and initialize JPLISAgent  
2.Parse the parameters of the MANIFEST.MF file, and set some content in
JPLISAgent according to these parameters.  
3.Listen for the `VMInit` event and do the following after the JVM is
initialized:  
(1) create an InstrumentationImpl object;  
(2) listen for the ClassFileLoadHook event;  
(3) call the`LoadClassAndCallPremain` method of InstrumentationImpl, which
will be called in this method Premain method of Premain-Class class specified
in MANIFEST.MF in javaagent

Here is a simple example (tested under JDK1.8.0_181):

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

MANIFEST.MF

    
    
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

Package PreMainAgent as a Jar package (you can directly package it with idea,
or you can use maven plugin to package). In idea, you can start it as follows:

![](https://images.seebug.org/content/images/2019/12/12/1576136913000-1.png-w331s)

You can start with the path `java -javaagent: PreMainAgent.jar -jar
TestMain.jar`

The results are as follows:

    
    
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

You can see that some necessary classes have been loaded before PreMainAgent -the PreMainAgent get loaded class: xxx part, these classes have not been
transformed. Then some classes have been transformed before main, and classes
have undergone transform after main is started, and classes have undergone
transform after main has ended, which can be compared with the results of
agentmain.

##### agentmain loading method

The steps to write in agentmain are as follows:

  1. Write the agentmain function, which contains one of the following two methods:

    
    
       public static void agentmain (String agentArgs, Instrumentation inst);
       public static void agentmain (String agentArgs);

If both methods are implemented, then the priority with the Instrumentation
parameter is higher, and it will be called first. `agentArgs` is the program
parameter obtained by the`premain` function. It is passed in via the command
line parameter.

  1. Define a MANIFEST.MF file, which must include the Agent-Class option. Can-Redefine-Classes and Can-Retransform-Classes options are also usually added.

  2. Make the agentmain class and MANIFEST.MF file into a jar package

  3. Through the attach tool to directly load the Agent, the program that executes the attach and the program that needs to be agent can be two completely different programs:

    
    
       // List all VM instances
       List <VirtualMachineDescriptor> list = VirtualMachine.list ();
       // attach the target VM
       VirtualMachine.attach (descriptor.id ());
       // Target VM loads Agent
       VirtualMachine # loadAgent ("Agent Jar Path", "Command Parameters");

The agentmain loading process is similar:

  1. Create and initialize JPLISAgent

  2. Parse the parameters in MANIFEST.MF and set some content in JPLISAgent according to these parameters

  3. Listen for the `VMInit` event and do the following after the JVM initialization is complete: 

(1) Create an InstrumentationImpl object;

(2) Monitor the ClassFileLoadHook event;

(3) Call `loadClassAndCallAgentmain` method in InstrumentationImpl, and it
will call `agentmain` the `agentmain` method of the Agent-Class class
specified in MANIFEST.MF.in javaagent.

Here is a simple example (tested under JDK 1.8.0_181):

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
            //Get all running virtual machines in the current system
            System.out.println("TestSufMainAgent start...");
            String option = args[0];
            List<VirtualMachineDescriptor> list = VirtualMachine.list();
            if (option.equals("list")) {
                for (VirtualMachineDescriptor vmd : list) {
                    System.out.println(vmd.displayName());
                }
            } else if (option.equals("attach")) {
                String jProcessName = args[1];
                String agentPath = args[2];
                for (VirtualMachineDescriptor vmd : list) {
                    if (vmd.displayName().equals(jProcessName)) {
                        VirtualMachine virtualMachine = VirtualMachine.attach(vmd.id());
                        //Then load agent.jar and send it to the virtual machine
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

Package SufMainAgent and TestSufMainAgent as Jar packages (can be packaged
directly with idea, or packaged with maven plugin), first start Testmain, and
then list the current Java programs:

![](https://images.seebug.org/content/images/2019/12/12/1576136913000-2.png-w331s)

attach SufMainAgent to Testmain：

![](https://images.seebug.org/content/images/2019/12/12/1576136913000-3.png-w331s)

The output in Testmain is as follows:

    
    
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

Compared with the previous `premain`, it can be seen that the number of
classes from getloadedclasses in `agentmain` is greater than the number from
getloadedclasses in `premain`, and the classes of `premain` getloadedclasses
and `premain` transform basically match `agentmain` getloadedclasses (only for
this test. if there are other communications, things may be different). That
is to say, if a certain class has not been loaded before, then it will pass
the transform set by both, which can be seen from the last java/lang/Shutdown.

##### Test if one class is loaded in Weblogic

Here we use weblogic for testing, and the agent method uses agentmain method
(tested under jdk1.6.0_29):

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

WeblogicTestSufMainAgent

    
    
    import com.sun.tools.attach.*;
    
    import java.io.IOException;
    import java.util.List;
    
    public class WeblogicTestSufMainAgent {
        public static void main(String[] args) throws IOException, AgentLoadException, AgentInitializationException, AttachNotSupportedException {
            //Get all current VMs that're on this device
            System.out.println("TestSufMainAgent start...");
            String option = args[0];
            List<VirtualMachineDescriptor> list = VirtualMachine.list();
            if (option.equals("list")) {
                for (VirtualMachineDescriptor vmd : list) {
                    //If the VM is xxx, it is the target. Get its pid
                    //Then load agent.jar and send it to this VM
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

List running Java applications:

![](https://images.seebug.org/content/images/2019/12/12/1576136913000-4.png-w331s)

attach：

![](https://images.seebug.org/content/images/2019/12/12/1576136913000-5.png-w331s)

Weblogic output:

![](https://images.seebug.org/content/images/2019/12/12/1576136914000-6.png-w331s)

If we are using Weblogic t3 for deserialization and a class has not been
loaded before but can be found by Weblogic, then the corresponding class will
be transformed by the Agent. But some classes are in some Jar in the Weblogic
directory, while Weblogic won't load it unless there are some special
configurations.

#### Instrumentation limitations

In most cases, we use Instrumentation to use its bytecode instrumentation,
which is generally a **class retransformation** function, but has the
following limitations:

  1. `premain` and `agentmain` are to modify the bytecode are after the class file is loaded. That is to say, you must take a parameter of type Class, which cannot be redefined through the bytecode file and **custom class name** that one class **does not exist**. What needs to be noted here is the redefinition mentioned above. **Cannot be redefined** just now means that a class name cannot be changed again. The bytecode content can still be redefined and modified. However, the byte code content must also meet the requirements of the second point after modification.
  2. In fact, class conversions will eventually return to `Instrumentation#retransformClasses ()` method. This method has the following restrictions:
  3. The parent of the new and old classes must be the same;
  4. The number of interfaces implemented by the new and old classes must be the same, and they must be the same;
  5. The accessors number of new class and old class must match. The number and field names of the new and old classes must be the same;
  6. The adding and deleting methods of new class and old class must be private static/final.
  7. You can delete or modify method body.

The limitations encountered in practice may not be limited to these. If we
want to redefine a brand new class (the class name does not exist in the
loaded class), we can consider the method based on class loader isolation:
create a new custom class loader to define a brand new through the new
bytecode , But the limitations of this new class can only be called through
reflection.

#### Summary

  * This article only describes some basic concepts related to JavaAgent. I got to know that there was such a thing, and verified a problem that I encountered before. I also read several articles written by other security researchers [4]&[5].
  * I used stain tracking, hook, syntax tree analysis and other technologies after reading some articles such as [PHP-RASP implementation of vulnerability detection](https://c0d3p1ut0s.github.io/%E4%B8%80%E7%B1%BBPHP-RASP % E7% 9A% 84% E5% AE% 9E% E7% 8E% B0 /)[6]. And I have also read a few about Java RASP [2]&[3]. If you want to write RASP-based vulnerability detection/ exploitation tools,you can also learn from them.

The code is now on [github](https://github.com/longofo/learn-javaagent). You
can test it if you are interested in this. Be careful of the JDK version in
the pom.xml file. If an error occurs when you switch JDK tests, remember to
modify the JDK version in pom.xml.

#### Reference

  1. <https://docs.oracle.com/javase/8/docs/api/java/lang/instrument/Instrumentation.html>
  2. <https://paper.seebug.org/513/#0x01-rasp>
  3. <https://paper.seebug.org/1041/#31-java-agent>
  4. <http://www.throwable.club/2019/06/29/java-understand-instrument-first/#Instrumentation%E6%8E%A5%E5%8F%A3%E8%AF%A6%E8%A7%A3>
  5. <https://www.cnblogs.com/rickiyang/p/11368932.html>
  6. <https://c0d3p1ut0s.github.io/%E4%B8%80%E7%B1%BBPHP-RASP%E7%9A%84%E5%AE%9E%E7%8E%B0/>

# About Knownsec & 404 Team

Beijing Knownsec Information Technology Co., Ltd. was established by a group
of high-profile international security experts. It has over a hundred frontier
security talents nationwide as the core security research team to provide
long-term internationally advanced network security solutions for the
government and enterprises.

Knownsec's specialties include network attack and defense integrated
technologies and product R&D under new situations. It provides visualization
solutions that meet the world-class security technology standards and enhances
the security monitoring, alarm and defense abilities of customer networks with
its industry-leading capabilities in cloud computing and big data processing.
The company's technical strength is strongly recognized by the State Ministry
of Public Security, the Central Government Procurement Center, the Ministry of
Industry and Information Technology (MIIT), China National Vulnerability
Database of Information Security (CNNVD), the Central Bank, the Hong Kong
Jockey Club, Microsoft, Zhejiang Satellite TV and other well-known clients.

404 Team, the core security team of Knownsec, is dedicated to the research of
security vulnerability and offensive and defensive technology in the fields of
Web, IoT, industrial control, blockchain, etc. 404 team has submitted
vulnerability research to many well-known vendors such as Microsoft, Apple,
Adobe, Tencent, Alibaba, Baidu, etc. And has received a high reputation in the
industry.

The most well-known sharing of Knownsec 404 Team includes: [KCon Hacking
Conference](http://kcon.knownsec.com/#/ "KCon Hacking Conference"), [Seebug
Vulnerability Database](https://www.seebug.org/ "Seebug Vulnerability
Database") and [ZoomEye Cyberspace Search Engine](https://www.zoomeye.org/
"ZoomEye Cyberspace Search Engine").

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1100/>

