# 初探Java安全之JavaAgent

## About Java Agent

### Java Agent的出现

在JDK1.5版本开始，Java增加了Instrumentation(Java Agent API)和JVMTI(JVM Tool
Interface)功能，该功能可以实现JVM再加载某个class文件对其字节码进行修改，也可以对已经加载的字节码进行一个重新的加载。而在1.6版本新增了attach(附加方式)方式，可以对运行中的Java进程插入Agent。Java
Agent可以去实现字节码插桩、动态跟踪分析等，比如RASP产品和Java Agent内存马。

### Java Agent运行模式

有两种模式:  
1、启动Java程序时添加-javaagent(Instrumentation
API实现方式)或-agentpath/-agentlib(JVMTI的实现方式)参数，如java -javaagent:/data/XXX.jar
LingXeTest。  
2、JDK1.6新增了attach(附加方式)方式，可以对运行中的Java进程附加Agent。

这两种运行方式的最大区别在于第一种方式只能在程序启动时指定Agent文件，而attach方式可以在Java程序运行后根据进程ID动态注入Agent到JVM。

所以类似于想要注入Agent型内存马,一般会用attach的方式。

### Java Agent

Javaagent是java命令的一个参数。参数 javaagent 可以用于指定一个jar包

Java Agent和普通的Java类并没有任何区别，普通的Java程序中规定了main方法为程序入口，而Java
Agent则将premain（Agent模式）和agentmain（Attach模式）作为了Agent程序的入口，两者所接受的参数是完全一致的，如下：

    
    
    public static void premain(String args, Instrumentation inst) {}
    public static void agentmain(String args, Instrumentation inst) {}
    

而在Attach模式下的`premain()`方法有两种写法,如下：

    
    
    public static void premain(String agentArgs, Instrumentation inst)
      
    public static void premain(String agentArgs)
    

JVM会去优先加载带 Instrumentation 签名的方法，加载成功忽略第二种，如果第一种没有，则加载第二种方法。  
![](https://image.3001.net/images/20220507/1651908960_62762160a1683a52709b8.png!small)

Java Agent还限制了我们必须以jar包的形式运行或加载，我们必须将编写好的Agent程序打包成一个jar文件。除此之外，Java
Agent还强制要求了所有的jar文件中必须包含/META-INF/MANIFEST.MF文件，且该文件中必须定义好Premain-Class（Agent模式）或Agent-Class:（Agent模式）配置，如：

    
    
    Premain-Class: com.anbai.sec.agent.CrackLicenseAgent
    Agent-Class: com.anbai.sec.agent.CrackLicenseAgent
    

如果我们需要修改已经被JVM加载过的类的字节码，那么还需要设置在MANIFEST.MF中添加

    
    
    Can-Retransform-Classes: true或Can-Redefine-Classes: true。
    

javaagent参数相关:

    
    
    -agentlib:<libname>[=<选项>] 加载本机代理库 <libname>, 例如 -agentlib:hprof
    另请参阅 -agentlib:jdwp=help 和 -agentlib:hprof=help
    -agentpath:<pathname>[=<选项>]
    按完整路径名加载本机代理库
    -javaagent:<jarpath>[=<选项>]
    加载 Java 编程语言代理, 请参阅 java.lang.instrument
    
    jarpath 是指向代理程序 JAR 文件的路径。options 是代理选项。此开关可以在同一命令行上多次使用，从而创建多个代理程序。多个代理程序可以使用同一 jarpath。代理 JAR 文件必须符合 JAR 文件规范。下面的清单属性是针对代理 JAR 文件定义的：
    Premain-Class
    代理类。即包含 premain 方法的类。此属性是必需的，如果它不存在，JVM 将中止。注：这是类名，而不是文件名或路径。
    Boot-Class-Path
    由引导类加载器搜索的路径列表。路径表示目录或库（在许多平台上通常作为 jar 或 zip 库被引用）。查找类的特定于平台的机制出现故障之后，引导类加载器会搜索这些路径。按列出的顺序搜索路径。列表中的路径由一个或多个空格分开。路径使用分层 URI 的路径组件的语法。如果该路径以斜杠字符（“/”）开头，则为绝对路径，否则为相对路径。相对路径根据代理 JAR 文件的绝对路径解析。忽略格式不正确的路径和不存在的路径。此属性是可选的。
    Can-Redefine-Classes
    布尔值（true 或 false，与大小写无关）。能够重定义此代理所需的类。值如果不是 true，则被认为是 false。此属性是可选的，默认值为 false。
    代理 JAR 文件附加到类路径之后。
    

而关于`java.lang.instrument`包位于rt.jar，一共有5个文件  
![](https://image.3001.net/images/20220507/1651908960_62762160eb5ccf86c20ba.png!small)

## 源码简介

其实这一部分把注释翻译过来，有些类和某些方法依旧不理解是什么意思，也有些看懂了但不知道怎么用，先鸽着。

### ClassDefinition

    
    
    public final class ClassDefinition {
        /**
         *  要重定义的类
         */
        private final Class<?> mClass;
    
        /**
         *  用于替换的本地 class ，为 byte 数组
         */
        private final byte[]   mClassFile;
    
        /**
         *  构造方法，使用提供的类和类文件字节创建一个新的 ClassDefinition 绑定
         */
        public ClassDefinition( Class<?> theClass, byte[]  theClassFile) {
            if (theClass == null || theClassFile == null) {
                throw new NullPointerException();
            }
            mClass      = theClass;
            mClassFile  = theClassFile;
        }
    
        /**
         * 以下为 getter 方法
         */
        public Class<?>  getDefinitionClass() {
            return mClass;
        }
    
        public byte[] getDefinitionClassFile() {
            return mClassFile;
        }
    }
    

### ClassFileTransformer

ClassFileTransformer是一个转换类文件的代理接口，我们可以在获取到Instrumentation对象后通过addTransformer方法添加自定义类文件转换器。

使用`addTransformer`方法可以注册一个我们自定义的Transformer到Java
Agent，当有新的类被JVM加载时JVM会自动回调用我们自定义的Transformer类的transform方法，传入该类的transform信息(类名、类加载器、类字节码等)，我们可以根据传入的类信息决定是否需要修改类字节码，修改完字节码后我们将新的类字节码返回给JVM，JVM会验证类和相应的修改是否合法，如果符合类加载要求JVM会加载我们修改后的类字节码。

    
    
    package java.lang.instrument;
    
    public interface ClassFileTransformer {
    
      /**
       * 类文件转换方法，重写transform方法可获取到待加载的类相关信息
       *
       * @param loader              定义要转换的类加载器；如果是引导加载器，则为 null
       * @param className           类名,如:java/lang/Runtime
       * @param classBeingRedefined 如果是被重定义或重转换触发，则为重定义或重转换的类；如果是类加载，则为 null
       * @param protectionDomain    要定义或重定义的类的保护域
       * @param classfileBuffer     类文件格式的输入字节缓冲区（不得修改）
       * @return 字节码byte数组。
       */
      byte[] transform(ClassLoader loader, String className, Class<?> classBeingRedefined,
                              ProtectionDomain protectionDomain, byte[] classfileBuffer);
    
    }
    

重写transform方法需要注意以下事项：

  1. ClassLoader如果是被Bootstrap ClassLoader(引导类加载器)所加载那么loader参数的值是空。
  2. 修改类字节码时需要特别注意插入的代码在对应的ClassLoader中可以正确的获取到，否则会报ClassNotFoundException，比如修改java.io.FileInputStream(该类由Bootstrap ClassLoader加载)时插入了我们检测代码，那么我们将必须保证FileInputStream能够获取到我们的检测代码类。
  3. JVM类名的书写方式路径方式：java/lang/String而不是我们常用的类名方式：java.lang.String。
  4. 类字节必须符合JVM校验要求，如果无法验证类字节码会导致JVM崩溃或者VerifyError(类验证错误)。
  5. 如果修改的是retransform类(修改已被JVM加载的类)，修改后的类字节码不得新增方法、修改方法参数、类成员变量。
  6. addTransformer时如果没有传入retransform参数(默认是false)就算MANIFEST.MF中配置了Can-Redefine-Classes: true而且手动调用了retransformClasses方法也一样无法retransform。
  7. 卸载transform时需要使用创建时的Instrumentation实例。

### Instrumentation

java.lang.instrument.Instrumentation是监测运行在JVM程序的Java
API，利用Instrumentation我们可以实现如下功能：

  1. 动态添加或移除自定义的ClassFileTransformer（addTransformer/removeTransformer），JVM会在类加载时调用Agent中注册的ClassFileTransformer；
  2. 动态修改classpath（appendToBootstrapClassLoaderSearch、appendToSystemClassLoaderSearch），将Agent程序添加到BootstrapClassLoader和SystemClassLoaderSearch（对应的是ClassLoader类的getSystemClassLoader方法，默认是sun.misc.Launcher$AppClassLoader）中搜索；
  3. 动态获取所有JVM已加载的类(getAllLoadedClasses)；
  4. 动态获取某个类加载器已实例化的所有类(getInitiatedClasses)。
  5. 重定义某个已加载的类的字节码(redefineClasses)。
  6. 动态设置JNI前缀(setNativeMethodPrefix)，可以实现Hook native方法。
  7. 重新加载某个已经被JVM加载过的类字节码retransformClasses)。  
![](https://image.3001.net/images/20220507/1651908961_6276216131c540f81dc91.png!small)

源码如下：

    
    
    public interface Instrumentation {
      
        //增加一个Class 文件的转换器，转换器用于改变 Class 二进制流的数据，参数 canRetransform 设置是否允许重新转换。
        void addTransformer(ClassFileTransformer transformer, boolean canRetransform);
    
        //在类加载之前，重新定义 Class 文件，ClassDefinition 表示对一个类新的定义，如果在类加载之后，需要使用 retransformClasses 方法重新定义。addTransformer方法配置之后，后续的类加载都会被Transformer拦截。对于已经加载过的类，可以执行retransformClasses来重新触发这个Transformer的拦截。类加载的字节码被修改后，除非再次被retransform，否则不会恢复。
        void addTransformer(ClassFileTransformer transformer);
    
        //删除一个类转换器
        boolean removeTransformer(ClassFileTransformer transformer);
    
        boolean isRetransformClassesSupported();
    
        //在类加载之后，重新定义 Class。这个很重要，该方法是1.6 之后加入的，事实上，该方法是 update 了一个类。
        void retransformClasses(Class<?>... classes) throws UnmodifiableClassException;
    
        boolean isRedefineClassesSupported();
    
      
        void redefineClasses(ClassDefinition... definitions)
            throws  ClassNotFoundException, UnmodifiableClassException;
    
        boolean isModifiableClass(Class<?> theClass);
    
        @SuppressWarnings("rawtypes")
        Class[] getAllLoadedClasses();
    
      
        @SuppressWarnings("rawtypes")
        Class[] getInitiatedClasses(ClassLoader loader);
    
        //获取一个对象的大小
        long getObjectSize(Object objectToSize);
    
    
       
        void appendToBootstrapClassLoaderSearch(JarFile jarfile);
    
      
        void appendToSystemClassLoaderSearch(JarFile jarfile);
    
      
        boolean isNativeMethodPrefixSupported();
    
      
        void setNativeMethodPrefix(ClassFileTransformer transformer, String prefix);
    }
    

## Java Agent使用

前面都是理论，我们来简单写一个小Demo感受一下如何使用Java Agent技术。

### Agent模式

大致分为以下流程（以-javaagent模式为例）：

  1. 编写一个Agent类，其中定义`premain`方法并调用`Instrumentation#addTransformer`方法添加一个自定义的`Transformer`
  2. 自定义一个`Transformer`类，实现`Instrumentation`接口，在`transform`方法中写入自己想要的AOP逻辑
  3. 创建MANIFEST.MF文件，可以手动写也可以通过Maven的插件（pom.xml）
  4. 打包Agent的jar包
  5. 在需要使用JavaAgent的项目添加JVM启动参数`-javaagent`并指定我们打包好的jar

这里需要2个项目，1个为javaagent的jar包，另1个为被javaagent代理的类。最终在被代理类的main方法执行前先执行我们Agent中的premain方法

0x01 编写javaagent相关代码  
先创建一个Maven项目,其中创建一个Agent类，里面需要包含`premain`方法

    
    
    package com.zh1z3ven;
    
    import java.lang.instrument.Instrumentation;
    
    public class Agent {
        public static void premain(String agentArgs, Instrumentation inst){
            System.out.println("agentArgs"+agentArgs);
            inst.addTransformer(new DefineTransformer(),true);//调用addTransformer添加一个Transformer
        }
    
    }
    

创建`DefineTransformer`类，实现`ClassFileTransformer`接口

    
    
    package com.zh1z3ven;
    
    import java.lang.instrument.ClassFileTransformer;
    import java.lang.instrument.IllegalClassFormatException;
    import java.security.ProtectionDomain;
    
    public class DefineTransformer implements ClassFileTransformer {
        @Override
        public byte[] transform(ClassLoader loader, String className, Class<?> classBeingRedefined, ProtectionDomain protectionDomain, byte[] classfileBuffer) throws IllegalClassFormatException {
            System.out.println("premain load class"+className); //打印加载的类
            return new byte[0];
        }
    }
    

0x02 创建MANIFEST.MF文件  
手动创建的话需要在resources/META-INF目录下创建MANIFEST.MF文件，内容如下:注意多留一行空行

    
    
    Manifest-Version: 1.0
    Can-Redefine-Classes: true
    Can-Retransform-Classes: true
    Premain-Class: com.zh1z3ven.Agent
    
    

通过`pom.xml`中调用Maven的插件去创建该文件

    
    
    <build>
            <plugins>
                <plugin>
                    <groupId>org.apache.maven.plugins</groupId>
                    <artifactId>maven-jar-plugin</artifactId>
                    <version>3.1.0</version>
                    <configuration>
                        <archive>
                            <!--自动添加META-INF/MANIFEST.MF -->
                            <manifest>
                                <addClasspath>true</addClasspath>
                            </manifest>
                            <manifestEntries>
                                <Premain-Class>com.zh1z3ven.Agent</Premain-Class>
                                <Agent-Class>com.zh1z3ven.Agent</Agent-Class>
                                <Can-Redefine-Classes>true</Can-Redefine-Classes>
                                <Can-Retransform-Classes>true</Can-Retransform-Classes>
                            </manifestEntries>
                        </archive>
                    </configuration>
                </plugin>
                <plugin>
                    <groupId>org.apache.maven.plugins</groupId>
                    <artifactId>maven-compiler-plugin</artifactId>
                    <configuration>
                        <source>6</source>
                        <target>6</target>
                    </configuration>
                </plugin>
            </plugins>
        </build>
    

打包好jar后，文件会在jar包中  
![](https://image.3001.net/images/20220507/1651908961_62762161c36a25e73717b.png!small)

一些可能会用到的参数说明：

> Premain-Class ：包含 premain 方法的类（类的全路径名）  
> Agent-Class ：包含 agentmain 方法的类（类的全路径名）  
> Boot-Class-Path
> ：设置引导类加载器搜索的路径列表。查找类的特定于平台的机制失败后，引导类加载器会搜索这些路径。按列出的顺序搜索路径。列表中的路径由一个或多个空格分开。路径使用分层
> URI 的路径组件语法。如果该路径以斜杠字符（“/”）开头，则为绝对路径，否则为相对路径。相对路径根据代理 JAR
> 文件的绝对路径解析。忽略格式不正确的路径和不存在的路径。如果代理是在 VM 启动之后某一时刻启动的，则忽略不表示 JAR 文件的路径。（可选）  
> Can-Redefine-Classes ：true表示能重定义此代理所需的类，默认值为 false（可选）  
> Can-Retransform-Classes ：true 表示能重转换此代理所需的类，默认值为 false （可选）  
> Can-Set-Native-Method-Prefix： true表示能设置此代理所需的本机方法前缀，默认值为 false（可选）

0x03 编写测试类  
随意写一个

    
    
    public class a {
        public static void main(String[] args) {
            System.out.println("main Method");
        }
    }
    
    

0x04 -javaagent模式启动  
JVM启动参数添加

    
    
    -javaagent:target/JavaAgent-1.0-SNAPSHOT.jar
    

![](https://image.3001.net/images/20220507/1651908962_627621621f887bfb57a0d.png!small)

![](https://image.3001.net/images/20220507/1651908962_62762162608f5d226fdf5.png!small)

执行main方法之前会加载所有的类，包括系统类和自定义类。而在`ClassFileTransformer`中会去拦截系统类和自己实现的类对象，逻辑则是在`ClassFileTransformer`实现类的`transform`方法中定义。  
而在这里`transform`给我的感觉是类似于一个`filter`会去拦截/遍历一些要在JVM中加载的类，而在`transform`方法中我们可以定义一些逻辑，比如`if
className==
xxx`时走入一个逻辑去实现AOP。而其中就可以利用如javassist技术修改字节码并作为`transform`方法的返回值，这样就在该类在JVM中加载前（-javaagent模式）修改了字节码

### 使用javassist修改字节码

这里在之前a类中新添加一个方法，并在`Agent`里我们自定义的`Transformert`中`transform`添加一个逻辑，使用`javassist`去修改我们a类中新添加的方法。

a类中新加一个call方法

    
    
    package MemoryShell.JavaAgent;
    
    public class a {
        public static void main(String[] args) {
            System.out.println("main Method");
            call();
        }
    
        public static void call(){
            System.out.println("say hello ...");
        }
    }
    

DefineTransformer

    
    
    package com.zh1z3ven;
    
    import javassist.*;
    
    import java.io.IOException;
    import java.lang.instrument.ClassFileTransformer;
    import java.lang.instrument.IllegalClassFormatException;
    import java.security.ProtectionDomain;
    
    public class DefineTransformer implements ClassFileTransformer {
        @Override
        public byte[] transform(ClassLoader loader, String className, Class<?> classBeingRedefined, ProtectionDomain protectionDomain, byte[] classfileBuffer) throws IllegalClassFormatException {
            // System.out.println("premain load class"+className); //打印加载的类
            if ("MemoryShell/JavaAgent/a".equals(className)){
    
                try {
                    ClassPool classPool = ClassPool.getDefault();
                    CtClass ctClass = classPool.get("MemoryShell.JavaAgent.a");
                    CtMethod call = ctClass.getDeclaredMethod("call");
                    // 打印后加了一个弹计算器的操作
                    String MethodBody = "{System.out.println(\"say hello ...\");" +
                            "java.lang.Runtime.getRuntime().exec(\"open -a Calculator\");}";
                    call.setBody(MethodBody);
                    byte[] bytes = ctClass.toBytecode();
        
                    //detach的意思是将内存中曾经被javassist加载过的a对象移除，如果下次有需要在内存中找不到会重新走javassist加载
                    ctClass.detach();
                    return bytes;
    
                } catch (NotFoundException e) {
                    e.printStackTrace();
                } catch (CannotCompileException e) {
                    e.printStackTrace();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
            return new byte[0];
        }
    
    }
    

打成jar包，指定JVM参数后运行a类

    
    
    -javaagent:target/JavaAgent-1.1-SNAPSHOT.jar
    

![](https://image.3001.net/images/20220507/1651908962_62762162c1b21df083765.png!small)

### Attach api

在Java SE 6 以后在`Instrumentation`接口中提供了新的方法`agentmain`可以在 main 函数开始运行之后再运行。

    
    
    //采用attach机制，被代理的目标程序VM有可能很早之前已经启动，当然其所有类已经被加载完成，这个时候需要借助Instrumentation#retransformClasses(Class<?>... classes)让对应的类可以重新转换，从而激活重新转换的类执行ClassFileTransformer列表中的回调
    public static void agentmain (String agentArgs, Instrumentation inst)
    
    public static void agentmain (String agentArgs)
    

同样，agentmain 方法中带Instrumentation参数的方法也比不带优先级更高。开发者必须在MANIFEST.MF文件里面设置“Agent-Class”来指定包含 agentmain 函数的类。

在Java6 以后实现启动后加载的新实现是Attach api。Attach API 很简单，只有 2 个主要的类，都在
com.sun.tools.attach 包里面：  
![](https://image.3001.net/images/20220507/1651908963_627621632ac47357d573c.png!small)

  1. VirtualMachine 字面意义表示一个Java 虚拟机，也就是程序需要监控的目标虚拟机，提供了获取系统信息(比如获取内存dump、线程dump，类信息统计(比如已加载的类以及实例个数等)， loadAgent，Attach 和 Detach （Attach 动作的相反行为，从 JVM 上面解除一个代理）等方法，可以实现的功能可以说非常之强大 。该类允许我们通过给attach方法传入一个jvm的pid(进程id)，远程连接到jvm上 。代理类注入操作只是它众多功能中的一个，通过loadAgent方法向jvm注册一个代理程序agent，在该agent的代理程序中会得到一个Instrumentation实例，该实例可以 在class加载前改变class的字节码，也可以在class加载后重新加载。在调用Instrumentation实例的方法时，这些方法会使用ClassFileTransformer接口中提供的方法进行处理。
  2. VirtualMachineDescriptor 则是一个描述虚拟机的容器类，配合 VirtualMachine 类完成各种功能。

attach实现动态注入的原理如下：

通过VirtualMachine类的attach(pid)方法，便可以attach到一个运行中的java进程上，之后便可以通过loadAgent(agentJarPath)来将agent的jar包注入到对应的进程，然后对应的进程会调用agentmain方法。  
![](https://image.3001.net/images/20220507/1651908963_6276216367ad4393851d5.png!small)

### Attach模式使用

0x01 在JavaAgent项目中新编写一个AgentMain类

    
    
    package com.zh1z3ven;
    
    import java.lang.instrument.Instrumentation;
    
    public class AgentMain {
        public static void agentmain(String agentArgs, Instrumentation instrumentation) {
            instrumentation.addTransformer(new AgentMainTransformer(), true);
        }
    }
    

0x02 新建一个自定义的Transformer  
transform方法中逻辑依旧是修改a类的call方法字节码去弹calc

    
    
    package com.zh1z3ven;
    
    import javassist.*;
    
    import java.lang.instrument.ClassFileTransformer;
    import java.lang.instrument.IllegalClassFormatException;
    import java.security.ProtectionDomain;
    
    public class AgentMainTransformer implements ClassFileTransformer {
        @Override
        public byte[] transform(ClassLoader loader, String className, Class<?> classBeingRedefined, ProtectionDomain protectionDomain, byte[] classfileBuffer) throws IllegalClassFormatException {
    
            if ("MemoryShell.JavaAgent.a".equals(className)) {
                try {
                    ClassPool classPool = ClassPool.getDefault();
                    CtClass ctClass = classPool.get("MemoryShell.JavaAgent.a");
                    CtMethod call = ctClass.getDeclaredMethod("call");
                    // 打印后加了一个弹计算器的操作
                    String MethodBody = "{java.lang.Runtime.getRuntime().exec(\"open -a Calculator\");" +
                            "System.out.println(\"say hello ...\");}";
                    call.setBody(MethodBody);
                    byte[] bytes = ctClass.toBytecode();
                    return bytes;
                    //detach的意思是将内存中曾经被javassist加载过的a对象移除，如果下次有需要在内存中找不到会重新走javassist加载
                    //  ctClass.detach();
    
    
                } catch (Exception e) {
                    e.printStackTrace();
                    return classfileBuffer;
                }
            }else {
                return classfileBuffer;
            }
    
    
        }
    
    
    }
    
    

0x03 测试AgentMainTest类  
将jar通过jvm pid注入进来，使其修改a类中call方法的字节码

    
    
    package MemoryShell.JavaAgent;
    
    import com.sun.tools.attach.*;
    
    import java.io.IOException;
    import java.util.List;
    
    public class AgentMainTest {
        public static void main(String[] args) {
            System.out.println("running JVM start ");
            List<VirtualMachineDescriptor> list = VirtualMachine.list(); // 寻找当前系统中所有运行着的JVM进程
            for (VirtualMachineDescriptor vmd : list) {
                //如果虚拟机的名称为 xxx 则 该虚拟机为目标虚拟机，获取该虚拟机的 pid
                //然后加载 agent.jar 发送给该虚拟机
                System.out.println(vmd.displayName()); //vmd.displayName()看到当前系统都有哪些JVM进程在运行
                if (vmd.displayName().endsWith("MemoryShell.JavaAgent.AgentMainTest")) {
                    VirtualMachine virtualMachine = null;
                    try {
                        virtualMachine = VirtualMachine.attach(vmd.id());
                        virtualMachine.loadAgent("/Users/xxxx/JavaSourceCode/JavaCode/JavaAgent/target/JavaAgent-1.0-SNAPSHOT.jar");
    
                        virtualMachine.detach();
    
                    } catch (AttachNotSupportedException e) {
                        e.printStackTrace();
                    } catch (IOException e) {
                        e.printStackTrace();
                    } catch (AgentLoadException e) {
                        e.printStackTrace();
                    } catch (AgentInitializationException e) {
                        e.printStackTrace();
                    }
    
                }
            }
        }
    
    }
    

0x04 记得修改MANIFEST.MF或直接改pom.xml

    
    
    <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-jar-plugin</artifactId>
        <version>3.1.0</version>
        <configuration>
            <archive>
                <!--自动添加META-INF/MANIFEST.MF -->
                <manifest>
                    <addClasspath>true</addClasspath>
                </manifest>
                <manifestEntries>
                    <Agent-Class>com.zh1z3ven.AgentMain</Agent-Class>
                    <Can-Redefine-Classes>true</Can-Redefine-Classes>
                    <Can-Retransform-Classes>true</Can-Retransform-Classes>
                </manifestEntries>
            </archive>
        </configuration>
    </plugin>
    

0x05
打包，先运行测试AgentMainTest类将jar注入进来使其修改a类的字节码，之后运行a的main方法，调用到call方法时是我们修改过后的字节码了，所以会弹calc

![](https://image.3001.net/images/20220507/1651908963_6276216399eca4abd2e24.png!small)

Agent模式与Attach模式小结：

  1. 上面Attach这种情况是修改的还没被JVM加载的类，已加载的Java类是不会再被Agent处理的，这时候我们需要在Attach到目标进程后调用instrumentation.redefineClasses，让JVM重新该Java类，这样我们就可以使用Agent机制修改该类的字节码了。
    
        public static void agentmain(String agentArgs, Instrumentation inst) throws UnmodifiableClassException,
     ClassNotFoundException {
     inst.addTransformer(new Transformer(), true);
     inst.retransformClasses(Class.forName("com.example.xxxclass"));
     }
    

  2. premain和agentmain两种方式修改字节码的时机都是类文件加载之后，也就是说必须要带有Class类型的参数，不能通过字节码文件和自定义的类名重新定义一个本来不存在的类。
  3. 类的字节码修改称为类转换(Class Transform)，类转换其实最终都回归到类重定义Instrumentation#redefineClasses()方法，此方法有以下限制：
    * 新类和老类的父类必须相同；
    * 新类和老类实现的接口数也要相同，并且是相同的接口；
    * 新类和老类访问符必须一致。 新类和老类字段数和字段名要一致；
    * 新类和老类新增或删除的方法必须是private static/final修饰的；
    * 可以修改方法体。
  4. java agent 中的所有依赖，在原进程中的 classpath 中都要能找到，否则在注入时原进程会报错NoClassDefFoundError。
  5. agent 进程的 classpath 中必须有 tools.jar（提供 VirtualMachine attach api ），jdk 默认有 tools.jar，jre 默认没有。并且Linux和Windows之间是存在一个tools.jar适配问题。

## Reference

[https://www.cnblogs.com/nice0e3/p/14086165.html](https://www.sec-in.com/outLinkPage/?target=https://www.cnblogs.com/nice0e3/p/14086165.html)  
[https://www.cnblogs.com/rickiyang/p/11368932.html](https://www.sec-in.com/outLinkPage/?target=https://www.cnblogs.com/rickiyang/p/11368932.html)  
[https://su18.org/post/irP0RsYK1/](https://www.sec-in.com/outLinkPage/?target=https://su18.org/post/irP0RsYK1/)  
javasec.org

