## 前言

兜兜转转来到了Java agent技术，下一篇将会针对这种技术来进行内存马的注入，这里主要是一些对Java agent技术的基础的讲解。

这是内存马系列的第十二篇，针对Java agent进行学习。

## 正文

### 什么是Java agent技术？

java agent本质上可以理解为一个插件，该插件就是一个精心提供的jar包，这个jar包通过JVMTI（JVM Tool
Interface）完成加载，最终借助JPLISAgent（Java Programming Language Instrumentation
Services Agent）完成对目标代码的修改。

Java agent的功能

  * 可以在加载java文件之前做拦截把字节码做修改

  * 可以在运行期将已经加载的类的字节码做变更

  * ...........

### 简单使用

对于Java agent，主要是存在有`java.lang.instrument`中实现的API进行操作

![image-20221015202027547.png](https://image.3001.net/images/20221017/1666013756_634d5a3c75b2bba8b385e.png!small)

Java Agent支持目标JVM启动时加载，也支持在目标JVM运行时加载，这两种不同的加载模式会使用不同的入口函数

主要的使用方式有两种

  * 实现`premain`方法在JVM启动前进行加载，进行类增加等操作

  * 实现`agentmain`方法，能够在JVM启动之后进行加载

这两个方法的函数声明为

    
    
    public static void agentmain(String agentArgs, Instrumentation inst) {
        ...
    }
    
    public static void agentmain(String agentArgs) {
        ...
    }
    
    public static void premain(String agentArgs, Instrumentation inst) {
        ...
    }
    
    public static void premain(String agentArgs) {
        ...
    }
    

对于每种方法的重载，具有`Instrumentation`传参的方法优先级更高

#### premain方法的体验

我们首先创建一个我们的主`jar`包，运行我们的逻辑，步骤如下

我这里就不创建一个完整的项目了，直接手动创建一个类命令行生成jar包进行简单测试

创建一个测试类

    
    
    public class Test {
    	public static void main(String[] args) {
    		System.out.println("This is Test....");
    	}
    }
    

之后将其编译

    
    
    javac Test.java
    

创建一个`MANIFEST.MF`文件，包含有

    
    
    Manifest-Version: 1.0
    Main-Class: Test
    

生成一个jar包

    
    
    jar cvfm hello.jar MANIFEST.MF Test.class
    

最后的最后，直接`java -jar hello.jar`运行查看是否构建成功

颓废的是，我失败了，我采用直接暴力解压生成的`hello.jar`，修改其中的`MANIFEST.MF`中的内容，添加主类，也就是前面的

    
    
    Main-Class: Test
    

最后也能够成功

![image-20221015215601629.png](https://image.3001.net/images/20221017/1666013767_634d5a47b6ff433a7a117.png!small)

接下来就是创建一个存在有`premain`方法的agent.jar包

和上面的相似

其中的主类为

    
    
    import java.lang.instrument.Instrumentation;
    
    public class PremainTest {
    	public static void premain(String agentArgs, Instrumentation inst) throws Exception {
    		System.out.println(agentArgs);
    		System.out.println("This is premain....");
    	}
    }
    

其中不同的是，在`MANIFEST.MF`中指定类的key不是`Main-Class`，这里是`Premain-Class`这个key值

之后就是在运行jar包的时候加载agent包，这里使用

    
    
    java -javaagent:Agent.jar=Args -jar ..\hello\hello.jar
    

进行加载

![image-20221015221238725.png](https://image.3001.net/images/20221017/1666013775_634d5a4f82606dac3eecb.png!small)

其中，等号后面的`Args`就是在`premain`中的第一个参数的传入

从上面的输出我们可以知道，首先是运行我们agent包中的`premain`方法中的逻辑才会执行我们的主jar包中的主类逻辑

这种方法的调用只能在JVM启动时通过`-javaagent`指定jar进行调用

#### agentmain方法的体验

对于该方法，不同于前面一种方法，这种方法能够在在启动后进行添加

那么是如何进行加载的呢？

官方提供了`Attach`API进行动态的加载agent，在`tools.jar`包中,
值得注意的是，在JVM默认启动过程中不会加载这个jar包，我们需要额外指定才能添加进入JVM中

其中存在有两个关键的类，在`com.sun.tools.attach`包下

![image-20221015222843385.png](https://image.3001.net/images/20221017/1666013783_634d5a578635a99ee33b4.png!small)

首先看看`VirtualMachine`这个抽象类

查看一下类结构

![image-20221015223009721.png](https://image.3001.net/images/20221017/1666013791_634d5a5f952f6f63e8b1b.png!small)

这个类可以用来获取JVM中的相关信息

  * `attach`: 能够通过该方法传入JVM的pid号，远程连接该JVM

  * `detach`: 关闭与JVM的远程连接

  * `loadAgent`: 能够通过该方法向远程JVM注册一个Agent

而`VirtualMachineDescriptor`就是对`VirtualMachine`的一种增加

现在简单使用一下`agentmain`方法，首先，我修改了hello.jar中的逻辑，输出了该JVM的pid方便加载agent，并通过while死循环的方式保持程序的活性

    
    
    import java.lang.management.ManagementFactory;
    
    public class Test {
        public static void main(String[] args) throws Exception{
            String pid = ManagementFactory.getRuntimeMXBean().getName();
            int indexOf = pid.indexOf('@');
            if (indexOf > 0) {
                pid = pid.substring(0, indexOf);
            }
            System.out.println("JVM pid is -> " + pid);
           while(true) {
                System.out.println("This is Test....");
                Thread.sleep(20 * 60 * 60);
           }
        }
    }
    

之后就是`agent.jar`的编写

这里和之前差不多的过程，将前面的key值从`Premain-Class`变为了`Agent-Class`这个key值

    
    
    Manifest-Version: 1.0
    Premain-Class: PremainTest
    Agent-Class: AgentmainTest
    

我们在`AgentmainTest`类中实现了`agentmain`方法

    
    
    import java.lang.instrument.Instrumentation;
    
    public class AgentmainTest {
    	public static void agentmain(String agentArgs, Instrumentation inst) {
    		System.out.println("This is agentmain....");
    	}
    }
    

最后按照上面的方式，得到了`Agent.jar`包

运行hello.jar包

![image-20221015230623666.png](https://image.3001.net/images/20221017/1666013802_634d5a6a1be4e7507a65c.png!small)

输出了PID号

我们利用前面提到的`VirtualMachine`进行agent的加载

    
    
    package pers.test_03;
    
    import com.sun.tools.attach.VirtualMachine;
    
    public class Test {
        public static void main(String[] args) throws Exception {
            String path = "path for agent.jar";
            VirtualMachine vm = VirtualMachine.attach("11508");
            vm.loadAgent(path);
            vm.detach();
        }
    }
    

![image-20221015230743725.png](https://image.3001.net/images/20221017/1666013811_634d5a731e785a77aeaf9.png!small)

可以成功运行我们的`agentmain`方法中的逻辑，之后会正常运行hello.jar中的内容

#### Instrumentation的几点使用

此类提供检测 Java 编程语言代码所需的服务。 Instrumentation
是在方法中添加字节码，以收集工具使用的数据。由于更改纯粹是附加的，因此这些工具不会修改应用程序状态或行为。这种良性工具的示例包括监控代理、分析器、覆盖分析器和事件记录器。

其中在这个接口中定义了多个方法

![image-20221015231253698.png](https://image.3001.net/images/20221017/1666013818_634d5a7a84baf0fd851d2.png!small)

  * `addTransformer`: 添加一个类转换器

  * `removeTransformer`: 删除一个类转换器

  * `isRetransformClassesSupported`: 判断是否支持类的重新转换

  * `retransformClasses`: 在类加载后，重新定义该类

  * `isRedefineClassesSupported`: 判断是否支持重新定义类

  * `redefineClasses`: 重新进行类的定义

  * `isModifiableClass`: 确定一个类是否可以通过重新转换或重新定义来修改

  * `getAllLoadedClasses`: 返回 JVM 当前加载的所有类的数组

  * `getInitiatedClasses`: 返回 loader 为其初始加载器的所有类的数组。如果提供的加载器为空，则返回由引导类加载器启动的类

  * .............

接下来，我们通过修改agent中的代码结合`getAllLoadedClasses / isModifiableClass`来寻找已经加载且能够修改的类

    
    
    import java.lang.instrument.Instrumentation;
    import java.io.File;
    import java.io.FileOutputStream;
    
    public class AgentmainTest {
    	public static void agentmain(String agentArgs, Instrumentation inst) throws Exception{
    		System.out.println("This is agentmain....");
    		Class[] classes = inst.getAllLoadedClasses();
    		FileOutputStream out = new FileOutputStream(new File("E:/dst.txt"));
    		for (Class aClass : classes) {
    			String message = "class ==> " + aClass.getName() + "\r\n" + "isModify ==> " + inst.isModifiableClass(aClass) + "\n";
    			out.write(message.getBytes());
    		}
    		out.close();
    	}
    }
    

我们会将我们的结果存放在`dst.txt`文件中去

![image-20221015233138424.png](https://image.3001.net/images/20221017/1666013826_634d5a8259bbc8cb3393b.png!small)

我们想要达到修改类字节码的目的，我们需要添加一个类转换器，即需要调用`addTransformer`方法

我们详细看看这个方法的注释

![image-20221016095138335.png](https://image.3001.net/images/20221017/1666013839_634d5a8fca729673e57ad.png!small)

注册提供的变压器。所有未来的类定义都将被转换器看到，除了任何注册的转换器所依赖的类的定义。转换器在加载类时调用，当它们被重新定义时。如果
canRetransform 为真，则在重新转换它们，所以我们同时也要使得第二个参数为`true`，重新转换

同时，可以关注到传入的转换器是一个`ClassFileTransformer`实例

![image-20221016095540373.png](https://image.3001.net/images/20221017/1666013849_634d5a991bd16d7680253.png!small)

该接口主要是代理提供此接口的实现以转换类文件

定义了一个`transform`方法

![image-20221016095651938.png](https://image.3001.net/images/20221017/1666013854_634d5a9e6d46c337605a0.png!small)

此方法的实现可能会转换提供的类文件并返回一个新的替换类文件

那么仅仅只是添加了一个转换器，还是需要利用这个转换器进行字节码的转换

可以关注到`retransformClasses`方法

![image-20221016100026535.png](https://image.3001.net/images/20221017/1666013862_634d5aa654f0d25d08515.png!small)

这个方法，主要是用来重新进行类的加载

执行流程如下

  * 从初始类文件字节开始

  * 对于添加了 canRetransform false 的每个转换器，transform 在最后一次加载或重新定义期间返回的字节被重用作为转换的输出；

  * 对于每个添加了 canRetransform true 的转换器，在这些转换器中调用 transform 方法

  * 转换后的类文件字节被安装为类的新定义

所以通过调用这个方法将会触发我们在`addTransformer`方法中传入的转换器

流程就很清晰了，首先通过`addTransformer`方法添加转换器，之后通过调用`retransformClasses`方法触发转换器的`transform`方法

对于如果操控字节码我们可以使用`javassist`库进行操作，这个就不一步一步解释怎么操作了

所以，现在，我们可以尝试编写一个`Agent.jar`来尝试修改字节码进行操作

对于hello.jar，添加了一个

`Hello`类

    
    
    public class Hello {
        public void hello() {
            System.out.println("hello.....");
        }
    }
    

agent.jar中的`agentmain`方法

    
    
    import java.lang.instrument.Instrumentation;
    import java.io.File;
    import java.io.FileOutputStream;
    
    public class AgentmainTest {
    	public static void agentmain(String agentArgs, Instrumentation inst) throws Exception{
            Class[] classes = inst.getAllLoadedClasses();
            for (Class aClass : classes) {
                if (aClass.getName().contains(TransformerTest.editMethodName)) {
                    inst.addTransformer(new TransformerTest(), true);
                    inst.retransformClasses(aClass);
                }
            }
    	}
    }
    

转换器的逻辑

    
    
    import javassist.ClassClassPath;
    import javassist.ClassPool;
    import javassist.CtClass;
    import javassist.CtMethod;
    
    import java.lang.instrument.ClassFileTransformer;
    import java.lang.instrument.IllegalClassFormatException;
    import java.lang.instrument.Instrumentation;
    import java.security.ProtectionDomain;
    
    //实现了ClassFileTransformer接口的类
    public class TransformerTest implements ClassFileTransformer {
        public static String editClassName = "Hello";
        public static String editMethodName = "hello";
    
        @Override
        public byte[] transform(ClassLoader loader, String className, Class<?> classBeingRedefined, ProtectionDomain protectionDomain, byte[] classfileBuffer) throws IllegalClassFormatException {
            try {
                ClassPool cp = ClassPool.getDefault();
                if (classBeingRedefined != null) {
                    ClassClassPath ccp = new ClassClassPath(classBeingRedefined);
                    cp.insertClassPath(ccp);
                }
                CtClass ctc = cp.get(editClassName);
                CtMethod method = ctc.getDeclaredMethod(editMethodName);
                String source = "{System.out.println(\"hello transformer\");}";
                method.setBody(source);
                byte[] bytes = ctc.toBytecode();
                ctc.detach();
                return bytes;
            } catch (Exception e) {
                e.printStackTrace();
            }
            return null;
        }
    }
    

使用同样的手法添加agent，将会得到`hello transformer`的输出

## 总结

学习了有关agent技术的各种基本使用，为后面的agent内存马实现打一下基础

## Ref

https://www.yuque.com/tianxiadamutou/zcfd4v/tdvszq

https://xz.aliyun.com/t/9450

