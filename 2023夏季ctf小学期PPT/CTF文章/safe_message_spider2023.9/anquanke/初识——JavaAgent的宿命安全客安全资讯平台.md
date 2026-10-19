# 初识——JavaAgent的宿命

阅读量 **384222**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-05-06 16:30:46

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t01f7b8818a9034c5d8.jpg)

## 前言

在各大HW轮番对国内Web安全生态进行考核之后,安全设备大量普及.而基于Web的一句话木马显得力不从心,于是在Shiro反序列化的RCE大潮之际,无落地文件的内存马登上历史舞台,内存马实现之一的技术便是JavaAgent,于是下文便对JavaAgent进行学习，为后面文章埋下伏笔。

## JavaAgent简介

Java Agent 直译过来叫做 Java 代理，还有另一种称呼叫做 Java 探针。首先说 Java Agent 是一个 jar 包，只不过这个 jar
包不能独立运行，它需要依附到我们的目标 JVM 进程中。

Agent 是在 Java 虚拟机启动之时加载的，这个加载处于虚拟机初始化的早期，在这个时间点上：  
1.所有的 Java 类都未被初始化；  
2.所有的对象实例都未被创建；  
3.因而，没有任何 Java 代码被执行；

Javaagent是java命令的一个参数。参数 javaagent 可以用于指定一个 jar 包，并且对该 java 包有2个要求：  
1.agent的这个 jar 包的 MANIFEST.MF 文件必须指定 Premain-Class 项。  
2.Premain-Class 指定的那个类必须实现 premain() 方法。

## JavaAgent的应用场景

各个 Java IDE 的调试功能，例如 eclipse、IntelliJ ；  
热部署功能，例如 JRebel、XRebel、 spring-loaded；  
各种线上诊断工具，例如 Btrace、Greys，还有阿里的 Arthas；  
各种性能分析工具，例如 Visual VM、JConsole 等；

## 代码实现Agent类

###  1.创建JavaMaven项目

![](https://p4.ssl.qhimg.com/t01b3c6cfdb449ec213.png)

###  2.在Maven依赖中添加

    
    
        <dependencies>
            <dependency>
                <groupId>org.javassist</groupId>
                <artifactId>javassist</artifactId>
                <version>3.25.0-GA</version>
            </dependency>
        </dependencies>
    

###  3.创建一个agent类，声明agent入口函数

    
    
    public class MyCustomAgent {
        /**
         * jvm 参数形式启动，运行此方法
         * @param agentArgs
         * @param inst
         */
        public static void premain(String agentArgs, Instrumentation inst){
            System.out.println("premain");
            customLogic(inst);
        }
    
        /**
         * 动态 attach 方式启动，运行此方法
         * @param agentArgs
         * @param inst
         */
        public static void agentmain(String agentArgs, Instrumentation inst){
            System.out.println("agentmain");
            customLogic(inst);
        }
    
        /**
         * 打印所有已加载的类名称
         * 修改字节码
         * @param inst
         */
        private static void customLogic(Instrumentation inst){
            inst.addTransformer(new MyTransformer(), true);
            Class[] classes = inst.getAllLoadedClasses();
            for(Class cls :classes){
                System.out.println(cls.getName());
            }
        }
    }
    

###  4.创建一个自定义的方法，对被代理的Java类进行处理

    
    
    public class MyTransformer implements ClassFileTransformer {
        @Override
        public byte[] transform(ClassLoader loader, String className, Class<?> classBeingRedefined, ProtectionDomain protectionDomain, byte[] classfileBuffer) throws IllegalClassFormatException {
            System.out.println("Loading Class :"+ className);
            if (!"Test".equals(className)){
                return classfileBuffer;
            }
            CtClass cl = null;
            try {
                ClassPool classPool = ClassPool.getDefault();
                cl = classPool.makeClass(new ByteArrayInputStream(classfileBuffer));
                CtMethod ctMethod = cl.getDeclaredMethod("test");
                System.out.println("Get Method Name :"+ ctMethod.getName());
    
                ctMethod.insertBefore("System.out.println(\"before the method \");");
                ctMethod.insertAfter("System.out.println(\"after the method \");");
    
                byte[] transformed = cl.toBytecode();
                return transformed;
            }catch (Exception e){
                e.printStackTrace();
            }
            return classfileBuffer;
        }
    }
    
    
    
     ClassPool classPool = ClassPool.getDefault();
                cl = classPool.makeClass(new ByteArrayInputStream(classfileBuffer));
                CtMethod ctMethod = cl.getDeclaredMethod("test");
                System.out.println("Get Method Name :"+ ctMethod.getName());
    
                ctMethod.insertBefore("System.out.println(\"before the method \");");
                ctMethod.insertAfter("System.out.println(\"after the method \");");
    

此代码的含义是获取被加强类,使用反射的方式获取方法名称为test()的函数,然后使用ctMethod.insertBefore方法在调用前执行内容,ctMethod.insertAfter方法在调用后执行内容

###  5.在resources下创建META-INF/MANIFEST.MF文件

    
    
    Manifest-Version: 1.0
    Created-By: 雁不过衡阳
    Agent-Class: MyCustomAgent
    Can-Redefine-Classes: true
    Can-Retransform-Classes: true
    Premain-Class: MyCustomAgent
    

###  6.最后 Java Agent 是以 jar 包的形式存在，所以最后一步就是将上面的内容打到一个 jar 包里。

在 pom 文件中加入以下配置

    
    
    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-assembly-plugin</artifactId>
                <configuration>
                    <archive>
                        <manifestFile>src/main/resources/META-INF/MANIFEST.MF</manifestFile>
                    </archive>
                    <descriptorRefs>
                        <descriptorRef>jar-with-dependencies</descriptorRef>
                    </descriptorRefs>
                </configuration>
            </plugin>
        </plugins>
    </build>
    
    
    
    <manifestFile>src/main/resources/META-INF/MANIFEST.MF</manifestFile>
    

此配置是将上文创建的配置文件位置指定于此

###  7.使用Maven打包项目

![](https://p0.ssl.qhimg.com/t01712ffc6bc36e0b16.png)

    
    
    mvn assembly:assembly
    

###  8.生成结束后会在target目录下生成一个xx-1.0-SNAPSHOT-jar-with-dependencies

## 代码实现被代理类

###  1.创建新项目

###  2.创建测试类和测试方法，也就是被加强的类

    
    
    public class Test {
        public void test(){
            System.out.println("执行测试方法");
        }
    }
    

###  3.创建被加强的入口类

    
    
    public class App {
        public static void main(String[] args) {
            System.out.println("********main*******");
            new Test().test();
        }
    }
    
    
    
    new Test().test();
    

创建Test类并调用test方法

###  4.配置加强类的启动JVM参数

![](https://p3.ssl.qhimg.com/t01b09b3da5dac95962.png)

![](https://p1.ssl.qhimg.com/t0177107b9cac158bff.png)

![](https://p2.ssl.qhimg.com/t01e48d3e3d99571646.png)

    
    
    -javaagent:E:\IdeaProject\Java-agent\agent\target\agent-1.0-SNAPSHOT-jar-with-dependencies.jar
    -javaagent:上文打包的agent.jar路径
    

###  5.运行 加强类

![](https://p1.ssl.qhimg.com/t01596f4b9a61ae5cf1.png)

因为在agent类中定义了使用反射对被加强类的test方法进行的前后置增强,所有在调用test方法之前调用增强打印，在调用test方法之后调用增强打印。做到了对被加强类的控制。

## 总结

此文实现了JavaAgent的使用方法，以Demo的形式深入理解Agent的AOP模式,在接下来的文章中将会分析内存马的实现等内容，助君安全之路一往无前.

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **雁不过衡阳.** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/239200](/post/id/239200)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)
  * [木马](/tag/木马)

 **+1** __7赞

 __收藏

![](https://thirdwx.qlogo.cn/mmopen/vi_32/ibXI2KQI8cmOnnDuXOR7DmKK70JMwknA852GtXicJVVHgE6xQicliaxJmX35mmyPoxKwZUfQzzNy3IS3nOAAwTZ3vw/132)
雁不过衡阳.

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

