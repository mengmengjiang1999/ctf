很久之前，为了诊断线上的问题，就想要是能有工具可以在线上出问题的时候，放个诊断包进去马上生效，就能看到线上问题的所在，那该是多么舒服的事情。后来慢慢的切换到
java 领域后，这种理想也变成了现实，小如 IDEA 中更改页面就能马上生效，大如利用 Althas
工具进行线上数据诊断，可谓是信手拈来，极大的方便了开发和诊断。后来深入研究之后，就慢慢的不满足框架本身带来的便利了，造轮子的想法慢慢在脑中挥之不去，这也是本文产生的原因了。接下来，你无需准备任何前置知识，因为我已经为你准备好了
ClassLoader 甜点，Javassist 配菜，JavaAgent 高汤，手写插件加载器框架主食，外加 SPI
知识做调料，且让我们整理餐具，开始这一道颇有点特色的吃播旅程吧。

## 双亲委派模型

开始前，让我们先聊聊双亲委派这个话题，因为无论是做热部署，还是做字节码增强，甚至于日常的编码，这都是绕不开的一个话题。先看如下图示：

![](https://image.3001.net/images/20220905/1662375325_6315d59dcb1ad9e6f0616.png!small)

从如上图示，我们可以看到双亲委派模型整体的工作方式，整体讲解如下：

类加载器的 findClass (loadClass) 被调用

  1. 进入 App ClassLoader 中，先检查缓存中是否存在，如果存在，则直接返回
  2. 步骤 2 中的缓存中不存在，则被代理到父加载器，即 Extension ClassLoader
  3. 检查 Extension ClassLoader 缓存中是否存在
  4. 步骤 4 中的缓存中不存在，则被代理到父加载器，即 Bootstrap ClassLoader
  5. 检查 Bootstrap ClassLoader 缓存中是否存在
  6. 步骤 6 中的缓存中不存在，则从 Bootstrap ClassLoader 的类搜索路径下的文件中寻找，一般为 rt.jar 等，如果找不到，则抛出 ClassNotFound Exception
  7. Extension ClassLoader 会捕捉 ClassNotFound 错误，然后从 Extension ClassLoader 的类搜索路径下的文件中寻找，一般为环境变量 $JRE_HOME/lib/ext 路径下，如果也找不到，则抛出 ClassNotFound Exception
  8. App ClassLoader 会捕捉 ClassNotFound 错误，然后从 App ClassLoader 的类搜索路径下的文件中寻找，一般为环境变量 $CLASSPATH 路径下，如果找到，则将其读入字节数组，如果也找不到，则抛出 ClassNotFound Exception。如果找到，则 App ClassLoader 调用 defineClass () 方法。

通过上面的整体流程描述，是不是感觉双亲委派机制也不是那么难理解。本质就是先查缓存，缓存中没有就委托给父加载器查询缓存，直至查到 Bootstrap
加载器，如果 Bootstrap 加载器在缓存中也找不到，就抛错，然后这个错误再被一层层的捕捉，捕捉到错误后就查自己的类搜索路径，然后层层处理。

## 自定义 ClassLoader

了解了双亲委派机制后，那么如果要实现类的热更换或者是 jar 的热部署，就不得不涉及到自定义 ClassLoader 了，实际上其本质依旧是利用
ClassLoader 的这种双亲委派机制来进行操作的。遵循上面的流程，我们很容易的来实现利用自定义的 ClassLoader 来实现类的热交换功能：

    
    
    public class CustomClassLoader extends ClassLoader {
    
        //需要该类加载器直接加载的类文件的基目录
        private String baseDir;
        public CustomClassLoader(String baseDir, String[] classes) throws IOException {
            super();
            this.baseDir = baseDir;
            loadClassByMe(classes);
        }
        private void loadClassByMe(String[] classes) throws IOException {
            for (int i = 0; i < classes.length; i++) {
                findClass(classes[i]);
            }
        }
        /**
         * 重写findclass方法
         *
         * 在ClassLoader中，loadClass方法先从缓存中找，缓存中没有，会代理给父类查找，如果父类中也找不到，就会调用此用户实现的findClass方法
         *
         * @param name
         * @return
         */
        @Override
        protected Class findClass(String name) {
            Class clazz = null;
            StringBuffer stringBuffer = new StringBuffer(baseDir);
            String className = name.replace('.', File.separatorChar) + ".class";
            stringBuffer.append(File.separator + className);
            File classF = new File(stringBuffer.toString());
            try {
                clazz = instantiateClass(name, new FileInputStream(classF), classF.length());
            } catch (IOException e) {
                e.printStackTrace();
            }
            return clazz;
        }
        private Class instantiateClass(String name, InputStream fin, long len) throws IOException {
            byte[] raw = new byte[(int) len];
            fin.read(raw);
            fin.close();
            return defineClass(name, raw, 0, raw.length);
        }
    }

这里需要注意的是，在自定义的类加载器中，我们可以覆写 findClass，然后利用 defineClass 加载类并返回。

上面这段代码，我们就实现了一个最简单的自定义类加载器，但是能映射出双亲委派模型呢？

首先点开 ClassLoader 类，在里面翻到这个方法：

    
    
    protected Class<?> loadClass(String name, boolean resolve) throws ClassNotFoundException
    {
        synchronized (getClassLoadingLock(name)) {
            // First, check if the class has already been loaded
            Class<?> c = findLoadedClass(name);
            if (c == null) {
                long t0 = System.nanoTime();
                try {
                    if (parent != null) {
                        c = parent.loadClass(name, false);
                    } else {
                        c = findBootstrapClassOrNull(name);
                    }
                } catch (ClassNotFoundException e) {
                    // ClassNotFoundException thrown if class not found
                    // from the non-null parent class loader
                }
                if (c == null) {
                    // If still not found, then invoke findClass in order
                    // to find the class.
                    long t1 = System.nanoTime();
                    c = findClass(name);
                    // this is the defining class loader; record the stats
                    sun.misc.PerfCounter.getParentDelegationTime().addTime(t1 - t0);
                    sun.misc.PerfCounter.getFindClassTime().addElapsedTimeFrom(t1);
                    sun.misc.PerfCounter.getFindClasses().increment();
                }
            }
            if (resolve) {
                resolveClass(c);
            }
            return c;
        }
    }

如果对比着双亲委派模型来看，则 loadClass 方法对应之前提到的步骤 1-8，点进去 findLoadedClass 方法，可以看到底层实现是
native 的 native final Class<?> findLoadedClass0 方法，这个方法会从 JVM
缓存中进行数据查找。后面的分析方法类似。

而自定义类加载器中的 findClass 方法，则对应步骤 9：

    
    
    clazz = instantiateClass(name, new FileInputStream(classF), classF.length());
    //省略部分逻辑
    return defineClass(name, raw, 0, raw.length);

看看，整体是不是很清晰？

## 自定义类加载器实现类的热交换

写完自定义类加载器，来看看具体的用法吧，我们创建一个类，拥有如下内容：

    
    
    package com.tw.client;
    public class Foo {
        public Foo() {
        }
        public void sayHello() {
            System.out.println("hello world22222! (version 11)");
        }
    }

顾名思义，此类只要调用 sayHello 方法，便会打印出 hello world22222! (version 11) 出来。

热交换处理过程如下：

    
    
    public static void main(String[] args) throws Exception {
            while (true) {
                run();
                Thread.sleep(1000);
            }
        }
        /**
         * ClassLoader用来加载class类文件的,实现类的热替换
         * 注意，需要在swap目录下，一层层建立目录com/tw/client/，然后将Foo.class放进去
         * @throws Exception
         */
        public static void run() throws Exception {
            CustomClassLoader customClassLoader = new CustomClassLoader("swap", new String[]{"com.tw.client.Foo"});
            Class clazz = customClassLoader.loadClass("com.tw.client.Foo");
            Object foo = clazz.newInstance();
            Method method = foo.getClass().getMethod("sayHello", new Class[]{});
            method.invoke(foo, new Object[]{});
        }

当我们运行起来后，我们会将提前准备好的另一个 Foo.class 来替换当前这个，来看看结果吧（直接将新的 Foo.class 类拷贝过去覆盖即可）：

    
    
    hello world22222! (version 11)
    hello world22222! (version 11)
    hello world22222! (version 11)
    hello world22222! (version 11)
    hello world22222! (version 11)
    hello world2222! (version 2)
    hello world2222! (version 2)
    hello world2222! (version 2)
    hello world2222! (version 2)

  

可以看到，当我们替换掉原来运行的类的时候，输出也就变了，变成了新类的输出结果。整体类的热交换成功。

不知道我们注意到一个细节没有，在上述代码中，我们先创建出 Object 的类对象，然后利用 Method.invoke 方法来调用类：

有人在这里会疑惑，为啥不直接转换为 Foo 类，然后调用类的 Foo.sayHello 方法呢？像下面这种方式：

    
    
    Foo foo2 = (Foo) clazz.newInstance();
    foo2.sayHello();

这种方式是不行的，但是大家知道为啥不行吗？

我们知道，我们写的类，一般都是被 AppClassloader 加载的，也就是说，你写在 main 启动类中的所有类，只要你写出来，那么就会被
AppClassloader 加载，所以，如果这里我们强转为 Foo 类型，那铁定是会被 AppClassloader 加载的，但是由于我们的 clazz
对象是由 CustomerClassloader 加载的，所以这里就会出现这样的错误：

    
    
    java.lang.ClassCastException: com.tw.client.Foo cannot be cast to com.tw.client.Foo

那有什么方法可以解决这个问题吗？其实是有的，就是对 Foo 对象抽象出一个 Interface，比如说
IFoo，然后转换的时候，转换成接口，就不会有这种问题了：

    
    
    IFoo foo2 = (IFoo) clazz.newInstance();
    foo2.sayHello();

通过接口这种方式，我们就很容易对运行中的组件进行类的热交换了，属实方便。

需要注意的是，主线程的类加载器，一般都是
AppClassLoader，但是当我们创建出子线程后，其类加载器都会继承自其创建者的类加载器，但是在某些业务中，我想在子线程中使用自己的类加载器，有什么办法吗？其实这里也就是打断双亲委派机制。

由于 Thread 对象中已经附带了 ContextClassLoader 属性，所以这里我们可以很方便的进行设置和获取：

    
    
    //设置操作
    Thread t = Thread.currentThread();
    t.setContextClassLoader(loader);
    //获取操作
    Thread t = Thread.currentThread();
    ClassLoader loader = t.getContextClassLoader();
    Class<?> cl = loader.loadClass(className);

## SPI 实现类的热交换

说完基于自定义 ClassLoader 来进行类的热交换后，我们再来说说 Java 中的 SPI。说到 SPI 相信大家都听过，因为在 java
中天生集成，其内部机制也是利用了自定义的类加载器，然后进行了良好的封装暴露给用户，具体的源码大家可以自定翻阅 ServiceLoader 类。

这里我们写个简单的例子：

    
    
    public interface HelloService {
        void sayHello(String name);
    }
    public class HelloServiceProvider implements HelloService {
        @Override
        public void sayHello(String name) {
            System.out.println("Hello " + name);
        }
    }
    public class NameServiceProvider implements HelloService{
        @Override
        public void sayHello(String name) {
            System.out.println("Hi, your name is " + name);
        }
    }

然后我们基于接口的包名 + 类名作为路径，创建出 com.tinywhale.deploy.spi.HelloService 文件到 resources
中的 META-INF.services 文件夹，里面放入如下内容：

    
    
    com.tinywhale.deploy.spi.HelloServiceProvider
    com.tinywhale.deploy.spi.NameServiceProvider

然后在启动类中运行：

    
    
    public static void main(String...args) throws Exception {
            while(true) {
                run();
                Thread.sleep(1000);
            }
        }
        private static void run(){
            ServiceLoader<HelloService> serviceLoader = ServiceLoader.load(HelloService.class);
            for (HelloService helloWorldService : serviceLoader) {
                helloWorldService.sayHello("myname");
            }
        }

可以看到，在启动类中，我们利用 ServiceLoader 类来遍历 META-INF.services 文件夹下面的
provider，然后执行，则输出结果为两个类的输出结果。之后在执行过程中，我们去 target 文件夹中，将
com.tinywhale.deploy.spi.HelloService 文件中的 NameServiceProvider
注释掉，然后保存，就可以看到只有一个类的输出结果了。

    
    
    Hello myname
    Hi, your name is myname
    Hello myname
    Hi, your name is myname
    Hello myname
    Hi, your name is myname
    Hello myname
    Hello myname
    Hello myname
    Hello myname

这种基于 SPI 类的热交换，比自己自定义加载器更加简便，推荐使用。

## 自定义类加载器实现 Jar 部署

上面讲解的内容，一般是类的热交换，但是如果我们需要对整个 jar 包进行热部署，该怎么做呢？虽然现在有很成熟的技术，比如 OSGI
等，但是这里我将从原理层面来讲解如何对 Jar 包进行热部署操作。

由于内置的 URLClassLoader 本身可以对 jar 进行操作，所以我们只需要自定义一个基于 URLClassLoader 的类加载器即可：

    
    
    public class BizClassLoader extends URLClassLoader {
        public BizClassLoader(URL[] urls) {
            super(urls);
        }
    }

注意，我们打的 jar 包，最好打成 fat jar，这样处理起来方便，不至于少打东西：

    
    
    <plugin>
             <groupId>org.apache.maven.plugins</groupId>
             <artifactId>maven-shade-plugin</artifactId>
             <version>2.4.3</version>
             <configuration>
                 <!-- 自动将所有不使用的类排除-->
                 <minimizeJar>true</minimizeJar>
             </configuration>
             <executions>
                 <execution>
                     <phase>package</phase>
                     <goals>
                         <goal>shade</goal>
                     </goals>
                     <configuration>
                         <shadedArtifactAttached>true</shadedArtifactAttached>
                         <shadedClassifierName>biz</shadedClassifierName>
                     </configuration>
                 </execution>
             </executions>
         </plugin>

之后，我们就可以使用了：

    
    
    public static void main(String... args) throws Exception {
           while (true) {
               loadJarFile();
               Thread.sleep(1000);
           }
       }
       /**
        * URLClassLoader 用来加载Jar文件, 直接放在swap目录下即可
        *
        * 动态改变jar中类，可以实现热加载
        *
        * @throws Exception
        */
       public static void loadJarFile() throws Exception {
           File moduleFile = new File("swap\\tinywhale-client-0.0.1-SNAPSHOT-biz.jar");
           URL moduleURL = moduleFile.toURI().toURL();
           URL[] urls = new URL[] { moduleURL };
           BizClassLoader bizClassLoader = new BizClassLoader(urls);
           Class clazz = bizClassLoader.loadClass("com.tw.client.Bar");
           Object foo = clazz.newInstance();
           Method method = foo.getClass().getMethod("sayBar", new Class[]{});
           method.invoke(foo, new Object[]{});
           bizClassLoader.close();
       }

启动起来，看下输出，之后用一个新的 jar 覆盖掉，来看看结果吧：

    
    
    I am bar, Foo's sister, can you catch me ?????????????
    I am bar, Foo's sister, can you catch me ?????????????
    I am bar, Foo's sister, can you catch me ！！！！
    I am bar, Foo's sister, can you catch me ！！！！
    I am bar, Foo's sister, can you catch me ！！！！
    I am bar, Foo's sister, can you catch me ！！！！

可以看到，jar 包被自动替换了。当然，如果想卸载此包，我们可以调用如下语句进行卸载：

    
    
    bizClassLoader.close();

需要注意的是，jar 包中不应有长时间运行的任务或者子线程等，因为调用类加载器的 close
方法后，会释放一些资源，但是长时间运行的任务并不会终止。所以这种情况下，如果你卸载了旧包，然后马上加载新包，且包中有长时间的任务，请确认做好业务防重，否则会引发不可知的业务问题。

由于 Spring 中已经有对 jar 包进行操作的类，我们可以配合上自己的 annotation
实现特定的功能，比如扩展点实现，插件实现，服务检测等等等等，用途非常广泛，大家可以自行发掘。

上面讲解的基本是原理部分，由于目前市面上有很多成熟的组件，比如 OSGI 等，已经实现了热部署热交换等的功能，所以很推荐大家去用一用。

说到这里，相信大家对类的热交换，jar
的热部署应该有初步的概念了，但是这仅仅算是开胃小菜。由于热部署一般都是和字节码增强结合着来用的，所以这里我们先来大致熟悉一下 Java Agent 技术。

## 代码增强 技术拾忆

话说在 JDK 中，一直有一个比较重要的 jar 包，名称为 rt.jar，他是 java 运行时环境中，最核心和最底层的类库的来源。比如
java.lang.String, java.lang.Thread, java.util.ArrayList 等均来源于这个类库。今天我们所要讲解的角色是
rt.jar 中的 java.lang.instrument 包，此包提供的功能，可以让我们在运行时环境中动态的修改系统中的类，而 Java Agent
作为其中一个重要的组件，极具特色。

现在我们有个场景，比如说，每次请求过来，我都想把 jvm
数据信息或者调用量上报上来，由于应用已经上线，无法更改代码了，那么有什么办法来实现吗？当然有，这也是 Java Agent
最擅长的场合，当然也不仅仅只有这种场合，诸如大名鼎鼎的热部署 JRebel，阿里的 arthas，线上诊断工具 btrace，UT 覆盖工具 JaCoCo
等，不一而足。

在使用 Java Agent 前，我们需要了解其两个重要的方法：

    
    
    /**
     * main方法执行之前执行，manifest需要配置属性Premain-Class，参数配置方式载入
     */
    public static void premain(String agentArgs, Instrumentation inst);
    /**
     * 程序启动后执行，manifest需要配置属性Agent-Class，Attach附加方式载入
     */
    public static void agentmain(String agentArgs, Instrumentation inst);

还有个必不可少的东西是 MANIFEST.MF 文件，此文件需要放置到 resources/META-INF 文件夹下，此文件一般包含如下内容：

    
    
    Premain-class                : main方法执行前执行的agent类.
    Agent-class                  : 程序启动后执行的agent类.
    Can-Redefine-Classes         : agent是否具有redifine类能力的开关，true表示可以，false表示不可以.
    Can-Retransform-Classes      : agent是否具有retransform类能力的开关，true表示可以，false表示不可以.
    Can-Set-Native-Method-Prefix : agent是否具有生成本地方法前缀能力的开关，trie表示可以，false表示不可以.
    Boot-Class-Path              : 此路径会被加入到BootstrapClassLoader的搜索路径.

在对 jar 进行打包的时候，最好打成 fat jar，可以减少很多不必要的麻烦，maven 加入如下打包内容：

    
    
    <plugin>
           <groupId>org.apache.maven.plugins</groupId>
           <artifactId>maven-shade-plugin</artifactId>
           <executions>
               <execution>
                   <phase>package</phase>
                   <goals>
                       <goal>shade</goal>
                   </goals>
               </execution>
           </executions>
       </plugin>

而 MF 配置文件，可以利用如下的 maven 内容进行自动生成：

    
    
    <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-jar-plugin</artifactId>
            <version>3.2.0</version>
            <configuration>
                <archive>
                    <manifestFile>src/main/resources/META-INF/MANIFEST.MF</manifestFile>
                </archive>
            </configuration>
        </plugin>

工欲善其事必先利其器，准备好了之后，先来手写个 Java Agent 尝鲜吧，模拟 premain 调用，main 调用和 agentmain 调用。

首先是 premain 调用类 ，agentmain 调用类，main 调用类：

    
    
    //main执行前调用
    public class AgentPre {
        public static void premain(String agentArgs, Instrumentation inst) {
            System.out.println("execute premain method");
        }
    }
    //main主方法入口
    public class App {
        public static void main(String... args) throws Exception {
            System.out.println("execute main method ");
        }
    }
    //main执行后调用
    public class AgentMain {
        public static void agentmain(String agentArgs, Instrumentation inst) {
            System.out.println("execute agentmain method");
        }
    }

可以看到，逻辑很简单，输出了方法执行体中打印的内容。之后编译 jar 包，则会生成 fat jar。需要注意的是，MANIFEST.MF
文件需要手动创建下，里面加入如下内容：

    
    
    Manifest-Version: 1.0
    Premain-Class: com.tinywhale.deploy.javaAgent.AgentPre
    Agent-Class: com.tinywhale.deploy.javaAgent.AgentMain

由于代码是在 IDEA 中启动，所以想要执行 premain，需要在 App4a 启动类上右击：Run App.main ()，之后 IDEA 顶部会出现
App 的执行配置，我们需要点击 Edit Configurations 选项，然后在 VM options 中填入如下命令：

    
    
    -javaagent:D:\app\tinywhale\tinywhale-deploy\target\tinywhale-deploy-1.0-SNAPSHOT-biz.jar

之后启动 App，就可以看到输出结果了。注意这里最好用 fat jar, 减少出错的机率。

    
    
    execute premain method
    execute main method

但是这里的话，我们看不到 agentmain 输出，是因为 agentmain 的运行，是需要进行 attach 的，这里我们对 agentmain 进行
attach：

    
    
    public class App {
        public static void main(String... args) throws Exception {
            System.out.println("execute main method ");
            attach();
        }
        private static void attach() {
            File agentFile = Paths.get("D:\\app\\tinywhale\\tinywhale-deploy\\target\\tinywhale-deploy-1.0-SNAPSHOT.jar").toFile();
            try {
                String name = ManagementFactory.getRuntimeMXBean().getName();
                String pid = name.split("@")[0];
                VirtualMachine jvm = VirtualMachine.attach(pid);
                jvm.loadAgent(agentFile.getAbsolutePath());
            } catch (Exception e) {
                System.out.println(e);
            }
        }
    }

启动 app 后，得到的结果为：

    
    
    execute premain method
    execute main method
    execute agentmain method

可以看到，整个执行都被串起来了。

讲到这里，相信大家基本上理解 java agent 的执行顺序和配置了吧， premain 执行需要配置 - javaagent 启动参数，而
agentmain 执行需要 attach vm pid。

看到这里，相信对 java agent 已经有个初步的认识了吧。接下来，我们就基于 Java SPI + Java Agent + Javassist
来实现一个插件系统，这个插件系统比较特殊的地方，就是可以增强 spring 框架，使其路径自动注册到 component-scan
路径中，颇有点霸道（鸡贼）的意思。Javassist 框架的使用方式。

## 插件框架 玉汝于成

首先来说下这个框架的主体思路，使用 Java SPI 来做插件系统；使用 Java Agent 来使得插件可以在 main
主入口方法前或者是方法后执行；使用 Javassist 框架来进行字节码增强，即实现对 spring 框架的增强。

针对插件部分，我们可以定义公共的接口契约：

    
    
    public interface IPluginExecuteStrategy {
        /**
         * 执行方法
         * @param agentArgs
         * @param inst
         */
        void execute(String agentArgs, Instrumentation inst);
    }

然后针对 premain 和 agentmain，利用策略模式进行组装如下：

###  **premain 处理策略类**

    
    
    public class PluginPreMainExecutor implements IPluginExecuteStrategy{
    
    
    
    
        /**
         * 扫描加载的plugin，识别出@PreMainCondition并加载执行
         */
        @Override
        public void execute(String agentArgs, Instrumentation inst) {
            //获取前置执行集合
            List<String> pluginNames = AgentPluginAnnotationHelper.annoProcess(PreMainCondition.class);
            ServiceLoader<IPluginService> pluginServiceLoader = ServiceLoader.load(IPluginService.class);
            //只执行带有PreMainCondition的插件
            for (IPluginService pluginService : pluginServiceLoader) {
                if (pluginNames.contains(pluginService.getPluginName())) {
                    pluginService.pluginLoad(agentArgs, inst);
                }
            }
        }
    }

###  **agentmain 处理策略类**

    
    
    public class PluginAgentMainExecutor implements IPluginExecuteStrategy {
    
    
    
    
        /**
         * 扫描加载的plugin，识别出@AgentMainCondition并加载执行
         */
        @Override
        public void execute(String agentArgs, Instrumentation inst) {
            //获取后置执行集合
            List<String> pluginNames = AgentPluginAnnotationHelper.annoProcess(AgentMainCondition.class);
            ServiceLoader<IPluginService> pluginServiceLoader = ServiceLoader.load(IPluginService.class);
            for (IPluginService pluginService : pluginServiceLoader) {
                //只执行带有AgentMainCondition的插件
                if (pluginNames.contains(pluginService.getPluginName())) {
                    pluginService.pluginLoad(agentArgs, inst);
                }
            }
        }
    }

针对 premain 和 agentmain，执行器工厂如下：

    
    
    public class AgentPluginContextFactory {
        /**
         * 创建agent pre执行上下文
         * @return
         */
        public static PluginExecutorContext makeAgentPreExecuteContext() {
            IPluginExecuteStrategy strategy = new PluginPreMainExecutor();
            PluginExecutorContext context = new PluginExecutorContext(strategy);
            return context;
        }
    
    
    
    
        /**
         * 创建agent main执行上下文
         * @return
         */
        public static PluginExecutorContext makeAgentMainExecuteContext() {
            IPluginExecuteStrategy strategy = new PluginAgentMainExecutor();
            PluginExecutorContext context = new PluginExecutorContext(strategy);
            return context;
        }
    
    
    }

编写 Premain-Class 和 Agent-Class 指定的类：

    
    
    public class AgentPluginPreWrapper {
        public static void premain(String agentArgs, Instrumentation inst) {
            AgentPluginContextFactory.makeAgentPreExecuteContext().execute(agentArgs, inst);
        }
    
    
    }
    
    
    
    
    public class AgentPluginMainWrapper {
        public static void agentmain(String agentArgs, Instrumentation inst) {
            AgentPluginContextFactory.makeAgentMainExecuteContext().execute(agentArgs, inst);
        }
    }

配置文件中指定相应的类：

    
    
    Manifest-Version: 1.0
    Premain-Class: org.tiny.upgrade.core.AgentPluginPreWrapper
    Agent-Class: org.tiny.upgrade.core.AgentPluginMainWrapper
    Permissions: all-permissions
    Can-Retransform-Classes: true
    Can-Redefine-Classes: true

框架搭好后，来编写插件部分，插件的话，需要继承自 org.tiny.upgrade.sdk.IPluginService 并实现：

    
    
    @AgentMainCondition
    @Slf4j
    public class CodePadPluginServiceProvider implements IPluginService {
    
    
        @Override
        public String getPluginName() {
            return "增强插件";
        }
    
    
        @Override
        public void pluginLoad(String agentArgs, Instrumentation inst) {
            //获取已加载的所有类
            Class<?>[] classes = inst.getAllLoadedClasses();
            if (classes == null || classes.length == 0) {
                return;
            }
            //需要将业务类进行retransform一下，这样可以避免在transform执行的时候，找不到此类的情况
            for (Class<?> clazz : classes) {
                if (clazz.getName().contains(entity.getClassName())) {
                    try {
                        inst.retransformClasses(clazz);
                    } catch (UnmodifiableClassException e) {
                        log.error("retransform class fail:" + clazz.getName(), e);
                    }
                }
            }
            //进行增强操作
            inst.addTransformer(new ByteCodeBizInvoker(), true);
        }
    
    
        @Override
        public void pluginUnload() {
    
    
        }
    }

这里需要注意的是，在插件 load 的时候，我们做了 class retransform
操作，这样操作的原因是因为，在程序启动的时候，有时候比如一些类，会在 JavaAgent
之前启动，这样会造成有些类在进行增强的时候，无法处理，所以这里需要遍历并操作下，避免意外情况。

下面是具体的增强操作：

    
    
    @Slf4j
    public class ByteCodeBizInvoker implements ClassFileTransformer {
        /**
         * 在此处加载tprd-ut并利用类加载器加载
         *
         * @param loader
         * @param className
         * @param classBeingRedefined
         * @param protectionDomain
         * @param classfileBuffer
         * @return
         * @throws IllegalClassFormatException
         */
        @Override
        public byte[] transform(ClassLoader loader
                                , String className
                                , Class<?> classBeingRedefined
                                , ProtectionDomain protectionDomain
                                , byte[] classfileBuffer) throws IllegalClassFormatException {
            //java自带的方法不进行处理
            if (loader == null) {
                return null;
            }
            //增强spring5的componetscan，将org.tiny路径塞入
            if (className.contains("ComponentScanBeanDefinitionParser")) {
                try {
                    System.out.println("增强spring");
                    ClassPool classPool = new ClassPool(true);
                    classPool.appendClassPath(ByteCodeBizInvoker.class.getName());
    
    
                    CtClass ctClass = classPool.get(className.replace("/", "."));
                    ClassFile classFile = ctClass.getClassFile();
                    MethodInfo methodInfo = classFile.getMethod("parse");
                    CtMethod ctMethod = ctClass.getDeclaredMethod("parse");
                    addComponentScanPackage(methodInfo, ctMethod);
                    return ctClass.toBytecode();
                } catch (Exception e) {
                    log.error("handle spring 5 ComponentScanBeanDefinitionParser error", e);
                }
            }
        }
        /**
         * 遍历method，直至找到ReportTracer标记类
         *
         * @param ctMethod
         */
        private void addComponentScanPackage(MethodInfo methodInfo, CtMethod ctMethod) throws CannotCompileException {
            final boolean[] success = {false};
            CodeAttribute ca = methodInfo.getCodeAttribute();
            CodeIterator codeIterator = ca.iterator();
            //行遍历方法体
            while (codeIterator.hasNext()) {
                ExprEditor exprEditor = new ExprEditor() {
                    public void edit(MethodCall m) throws CannotCompileException {
                        String methodCallName = m.getMethodName();
                        if (methodCallName.equals("getAttribute")) {
                            //将org.tiny追加进去
                            m.replace("{ $_ = $proceed($$); $_ = $_ +  \",org.tiny.upgrade\";  }");
                            success[0] = true;
                        }
                    }
                };
                ctMethod.instrument(exprEditor);
                if (success[0]) {
                    break;
                }
            }
        }
    }

从上面可以看出，我们是修改了 spring 中的 ComponentScanBeanDefinitionParser 类，并将里面的 parser 方法中将
org.tiny.upgrade 包扫描路径自动注册进去，这样当别人集成我们的框架的时候，就无须扫描到框架也能执行了。

写到这里，相信大家对整体框架有个大概的认识了。但是这个框架有个缺陷，就是我的插件 jar 写完后，一定要放到项目的 maven dependency
中，然后打包部署才行。实际上有时候，我项目上线后，根本就没有机会重新打包部署，那么接下来，我们就通过自定义 Classloader
来让我们的插件不仅仅可以本地集成，而且可以从网络中集成。

首先，我们需要定义自定义类加载器：

    
    
    public class TinyPluginClassLoader extends URLClassLoader {
        /**
         * 带参构造
         * @param urls
         */
        public TinyPluginClassLoader(URL[] urls, ClassLoader parent) {
            super(urls, parent);
        }
        /**
         * 添加URL路径
         * @param url
         */
        public void addURL(URL url) {
            super.addURL(url);
        }
    }

这个类加载器，是不是很眼熟，和前面讲的类似，但是带了个 parent classloader 的标记，这是为什么呢？这个标记的意思是，当前自定义的
TinyPluginClassLoader 的父 classloader
是谁，这样的话，这个自定义类加载器就可以继承父类加载器中的信息了，避免出现问题，这个细节大家注意。

这里需要说明的是，从本地 jar 文件加载还是从网络 jar 文件加载，本质上是一样的，因为 TinyPluginClassLoader 是按照 URL
来的。

针对于本地 jar 文件，我们构造如下 URL 即可：

    
    
    URL url = new URL("jar:file:/D:/project/tiny-plugin-hello/target/tiny-plugin-hello-1.0-SNAPSHOT.jar!/")

针对于网络 jar 文件，我们构造如下 URL 即可：

    
    
    URL url = new URL("jar:http://111.111.111.111/tiny-plugin-hello-1.0-SNAPSHOT.jar!/")

这样，我们只需要定义好自定义类加载器加载逻辑即可：

    
    
    /**
         * 从jar文件中提取出对应的插件类
         *
         * @param pluginClass
         * @param jarFile
         * @return
         */
        public static Set<Class> loadPluginFromJarFile(Class pluginClass, JarFile jarFile, TinyPluginClassLoader tinyPluginClassLoader) {
            Set<Class> pluginClasses = new HashSet<Class>();
            Enumeration<JarEntry> jars = jarFile.entries();
            while (jars.hasMoreElements()) {
                JarEntry jarEntry = jars.nextElement();
                String jarEntryName = jarEntry.getName();
                if (jarEntryName.charAt(0) == '/') {
                    jarEntryName = jarEntryName.substring(1);
                }
                if (jarEntry.isDirectory() || !jarEntryName.endsWith(".class")) {
                    continue;
                }
                String className = jarEntryName.substring(0, jarEntryName.length() - 6);
                try {
                    Class clazz = tinyPluginClassLoader.loadClass(className.replace("/", "."));
                    if (clazz != null && !clazz.isInterface() && pluginClass.isAssignableFrom(clazz)) {
                        pluginClasses.add(clazz);
                    }
                } catch (ClassNotFoundException e) {
                    log.error("PluginUtil.loadPluginFromJarFile fail",e);
                }
            }
            return pluginClasses;
        }

之后，我们就可以用如下代码对一个具体的 jar 路径进行加载就行了：

    
    
    /**
         * 加载插件
         *
         * @return
         */
        @Override
        public Set<Class> loadPlugins(URL jarURL) {
            try {
                JarFile jarFile = ((JarURLConnection) jarURL.openConnection()).getJarFile();
                getTinyPluginClassLoader().addURL(jarURL);
                return PluginUtil.loadPluginFromJarFile(IPluginService.class, jarFile, getTinyPluginClassLoader());
            } catch (IOException e) {
                log.error("LoadPluginViaJarStrategy.loadPlugins fail", e);
                return null;
            }
        }

最终，我们只需要利用 SPI 进行动态加载：

    
    
    /**
         * 执行插件
         */
        public void processPlugins(URL... urls) {
            if (urls == null || urls.length == 0) {
                log.error("jar url path empty");
                return;
            }
            for (URL url : urls) {
                pluginLoadFactory.loadJarPlugins(url);
            }
            ServiceLoader<IPluginService> serviceLoader = ServiceLoader.load(IPluginService.class, pluginLoadFactory.getPluginLoader());
            for (IPluginService pluginService : serviceLoader) {
                pluginService.Process();
            }
        }

这样，我们不仅实现了插件化，而且我们的插件还支持从本地 jar 文件或者网络 jar 文件加载。由于我们利用了 agentmain
对代码进行增强，所以当系统检测到我这个 jar 的时候，下一次执行会重新对代码进行增强并生效。

## 总结

其实本文的技术，从双亲委派模型到自定义类加载器，再到基于自定义类加载器实现的类交换，基于 Java SPI 实现的类交换，最后到基于 Java SPI+
Java Agent + Javassist
实现的插件框架及框架支持远程插件化，来一步一步的向读者展示所涉及的知识点。当然，由于笔者知识有限，疏漏之处，还望海涵，真诚期待我的抛砖，能够引出您的玉石之言。

