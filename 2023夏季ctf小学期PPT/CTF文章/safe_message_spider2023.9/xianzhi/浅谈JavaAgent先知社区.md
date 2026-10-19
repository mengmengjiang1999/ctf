# Java Agent

Javaagent是java命令的一个参数。参数 Javaagent 可以用于指定一个 jar 包，并且对该 java 包有2个要求：

  1. 这个 jar 包的 MANIFEST.MF 文件必须指定 Premain-Class 项。
  2. Premain-Class 指定的那个类必须实现 premain() 方法。

premain 方法，从字面上理解，就是运行在 main 函数之前的的类。当Java 虚拟机启动时，在执行 main 函数之前，JVM
会先运行`-javaagent`所指定 jar 包内 Premain-Class 这个类的 premain 方法 。

## 启动时加载Agent

前边提到`premain()`函数，它实在main函数之前运行的，也就是启动时加载的Agent，函数声明如下，`Instrumentation
inst`参数的方法 **优先级更高** ：

    
    
    public static void agentmain(String agentArgs, Instrumentation inst) {
        ...
    }
    
    public static void agentmain(String agentArgs) {
        ...
    }
    

  * `String agentArgs` 就是Java agent后跟的参数。

  * `Instrumentaion inst` 用于和目标JVM进行交互，从而达到修改数据的效果。

先看下premain()函数的具体使用：

### **PreMainDemo**

    
    
    import java.lang.instrument.Instrumentation;
    
    public class PreMainDemo {
        public static void premain(String agentArgs, Instrumentation inst){
            System.out.println(agentArgs);
            for(int i=0 ; i<5 ;i++){
                System.out.println("premain is loading.....");
            }
        }
    }
    

接着打包，先创建 mainfest(注：在前边说到过文件中一定要有Premain-Class属性，其次最后要有空行)

**agent.mf**

    
    
    Manifest-Version: 1.0
    Premain-Class: Agent.PreMainDemo
    

**agent.jar**

将msf文件和PreMainDemo打成一个jar包

    
    
    jar cvfm agent.jar agent.mf Agent\PreMainDemo.class
    

前边说到premain是在main函数之前调用的，所以这里再写个带有main的测试类

### **Hello.java**

    
    
    public class Hello {
        public static void main(String[] args) {
            System.out.println("Hello,Sentiment!");
        }
    }
    

**Hello.mf**

    
    
    Manifest-Version: 1.0
    Main-Class: Agent.Hello
    

**hello.jar**

    
    
    jar cvfm hello.jar Hello.mf Agent\Hello.class
    

之后就是利用`-javaagent`进行加载

    
    
    java -javaagent:agent.jar=Sentiment -jar hello.jar
    

可以看到我们 agent 中 premain 的代码被优先执行了，同时还获取 到了 agentArgs 参数

![](./img/274767360305452583.png)  
这种有个比较明显的弊端：若目标服务器已启动，则无法预先加载premain。

## 启动后加载 Agent

在前边说到agent中用到的两种加载方式，第二种就是`agentmain`，这种方式就有效的解决了上述premain中提到的弊端，因为他是启动后加载的。

函数声明如下：

    
    
    public static void agentmain (String agentArgs, Instrumentation inst)
    public static void agentmain (String agentArgs)
    

官方为了实现启动后加载，提供了`Attach API`。Attach API 很简单，只有 2 个主要的类，都在
`com.sun.tools.attach` 包里面。这里有两个比较重要的类，分别是 VirtualMachine 和
VirtualMachineDescriptor。

由于Attach API 在 tool.jar 中，jvm 启动时是默认不加载该依赖的，所以需要手动加载进去

![](./img/8862998836011872539.png)

### VirtualMachine

VirtualMachine
可以来实现获取系统信息，内存dump、线程dump、类信息统计（例如JVM加载的类）。里面配备有几个方法LoadAgent，Attach 和 Detach
。下面来看看这几个方法的作用

    
    
    public abstract class VirtualMachine {
        // 获得当前所有的JVM列表
        public static List<VirtualMachineDescriptor> list() { ... }
    
        // 根据pid连接到JVM
        public static VirtualMachine attach(String id) { ... }
    
        // 断开连接
        public abstract void detach() {}
    
        // 加载agent，agentmain方法靠的就是这个方法
        public void loadAgent(String agent) { ... }
    
    }
    

  * **list** ：获取所有JVM列表
  * **Attach** ：允许我们通过给attach方法传入一个jvm的pid(进程id)，远程连接到jvm上
  * **loadAgent** ：向jvm注册一个代理程序agent，在该agent的代理程序中会得到一个Instrumentation实例，该实例可以 在class加载前改变class的字节码，也可以在class加载后重新加载。在调用Instrumentation实例的方法时，这些方法会使用ClassFileTransformer接口中提供的方法进行处理。
  * **Detach** ：断开连接即解除代理

VirtualMachineDescriptor 就不做探究了，其实就是个描述虚拟机的容器类，配合 VirtualMachine 使用的。

#### AgentMainDemo

    
    
    public class AgentMainDemo {
        public static void agentmain(String agentArgs, Instrumentation inst) {
            System.out.println("agentmain start.........");
        }
    }
    

**agent.mf**

    
    
    Manifest-Version: 1.0
    Agent-Class: Agent.AgentMainDemo
    

打包

    
    
    jar cvfm agent.jar agent.mf Agent\AgentMainDemo.class
    

#### **Hello.java**

    
    
    public class Hello {
        public static void main(String[] args) throws InterruptedException {
            System.out.println("Hello.main() in test project start!!");
            Thread.sleep(300000000);
            System.out.println("Hello.main() in test project  end!!");
        }
    }
    

运行Hello.java后，会sleep等待状态来模拟正常服务，此时查看java服务进程发现，Hello的进程是14460

![](./img/6591892920760111081.png)  
接着就用attach绑定pid进程，并通过 **loadAgent** 绑定对应的agent.jar来调用

#### **AttchDemo**

    
    
    public class AttchDemo {
        public static void main(String[] args) throws AgentLoadException, IOException, AgentInitializationException, AttachNotSupportedException {
            VirtualMachine attach = VirtualMachine.attach("14460");  // 命令行找到这个jvm的进程号
            attach.loadAgent("D:\\java\\AgentMemory\\target\\classes\\agent.jar");
            attach.detach();
        }
    }
    

运行后可以发现在输出`Hello.main() in test project end!!`前输出了我们agent中的语句`agentmain
start.........`，达到了启动服务后仍能加载Agent的效果

![](./img/1808937409314858158.png)

# 动态修改字节码

agentmain中有一个形参Instrumentation，通过它能和目标 JVM 进行交互，结合Javassist修改数据，达到真正Agent的效果。

    
    
    public static void agentmain (String agentArgs, Instrumentation inst)
    

## Instrumentation

    
    
    public interface Instrumentation {
    
        // 增加一个 Class 文件的转换器，转换器用于改变 Class 二进制流的数据，参数 canRetransform 设置是否允许重新转换。在类加载之前，重新定义 Class 文件，ClassDefinition 表示对一个类新的定义，如果在类加载之后，需要使用 retransformClasses 方法重新定义。addTransformer方法配置之后，后续的类加载都会被Transformer拦截。对于已经加载过的类，可以执行retransformClasses来重新触发这个Transformer的拦截。类加载的字节码被修改后，除非再次被retransform，否则不会恢复。
        void addTransformer(ClassFileTransformer transformer);
    
        // 删除一个类转换器
        boolean removeTransformer(ClassFileTransformer transformer);
    
        // 在类加载之后，重新定义 Class。这个很重要，该方法是1.6 之后加入的，事实上，该方法是 update 了一个类。
        void retransformClasses(Class<?>... classes) throws UnmodifiableClassException;
    
        // 判断目标类是否能够修改。
        boolean isModifiableClass(Class<?> theClass);
    
        // 获取目标已经加载的类。
        @SuppressWarnings("rawtypes")
        Class[] getAllLoadedClasses();
    
        ......
    }
    

先看下getAllLoadedClasses`和`isModifiableClasses`。

### getAllLoadedClasses

获取所有已经加载的类。

还是用刚才的例子，只是换下`AgentMainDemo`类的代码

    
    
    public class AgentMainDemo {
        public static void agentmain(String agentArgs, Instrumentation inst) {
            Class[] classes = inst.getAllLoadedClasses();
            for (Class aClass : classes) {
                String result = "class ==> " + aClass.getName();
                System.out.println(result);
            }
        }
    }
    

可以看到打印出了所有已经加载的类

### isModifiableClasses

判断该类是否可以修改

    
    
    public class AgentMainDemo {
        public static void agentmain(String agentArgs, Instrumentation inst) {
            Class[] classes = inst.getAllLoadedClasses();
            for (Class aClass : classes) {
                String result = "class ==> " + aClass.getName()+ aClass.getName() + "\n\t" + "Modifiable ==> " + (inst.isModifiableClass(aClass) ? "true" : "false") + "\n";
                if (result.contains("true")){
                    System.out.println(result);
                }
            }
        }
    }
    

## ClassFileTransformer

Instrumentation中还有两个比较重要的类，但是这两个类的都有一个共同类型的形参`ClassFileTransformer`，所以先来了解一下这个transform

    
    
    // 添加 Transformer
    void addTransformer(ClassFileTransformer transformer);
    // 触发 Transformer
    boolean removeTransformer(ClassFileTransformer transformer);
    

`ClassFileTransformer`中只有一个方法

    
    
    public interface ClassFileTransformer {
        default byte[]
        transform(  ClassLoader         loader,
                    String              className,
                    Class<?>            classBeingRedefined,
                    ProtectionDomain    protectionDomain,
                    byte[]              classfileBuffer) {
            ....
        }
    }
    

其中`classBeingRedefined`为我们要修改的类，他的值受retransformClasses函数传入的值影响，即：

    
    
    inst.retransformClasses(Hello);
    

当`retransformClasses`中的值是Hello类时，那此时的`classBeingRedefined`对应的类也就是Hello，根据调用栈也不难看出(
**这个后续会用到** )

### Javassist

知道了`retransformClasses`的用处之后，我们就可以通过构造`retransformClasses`方法中的值，来自定义要重新修改的字节码文件

这里就介绍一点：

> 如果程序运行在 JBoss 或者 Tomcat 等 Web 服务器上，ClassPool 可能无法找到用户的类，因为 Web
> 服务器使用多个类加载器作为系统类加载器。在这种情况下， **ClassPool 必须添加额外的类搜索路径**
> ，使用insertClassPath()函数
    
    
    cp.insertClassPath(new ClassClassPath(<Class>));
    

insertClassPath中要填写的是我们要修改文件的路径，而前文提到`classBeingRedefined`存储的就是我们要修改的类，所以这里只需要改成：

    
    
    ClassClassPath ccp = new ClassClassPath(classBeingRedefined);
    

这样就可以避免无法加载类的情况

## 测试

**Hello**

这个是我们要修改的类

    
    
    public class Hello {
        public void Hello() {
            System.out.println("This is Sentiment !");
        }
    }
    

**HelloWorld**

这个类通过sleep()进行隔断，前后调用两次Hello()方法，来验证我们修改完字节码后的结果

    
    
    public class HelloWorld  {
        public static void main(String[] args) throws InterruptedException {
            Hello h1 = new Hello();
            h1.Hello();
    
            Thread.sleep(15000);
    
            Hello h2 = new Hello();
            h2.Hello();
        }
    }
    

**AgentMainDemo**

agentmain类，它会触发TransformerDemo()类中的transform()

    
    
    public class AgentMainDemo {
        public static void agentmain(String agentArgs, Instrumentation inst) throws UnmodifiableClassException {
            Class[] classes = inst.getAllLoadedClasses();
            for (Class aClass : classes) {
                if (aClass.getName().equals(TransformerDemo.editClassName)) {
    
                    // 添加 Transformer
                    inst.addTransformer(new TransformerDemo(), true);
                    // 触发 Transformer
                    inst.retransformClasses(aClass);
                }
            }
        }
    }
    

**TransformerDemo**

这个类就是要通过`agentmain()`的`retransformClasses()`方法触发的ClassFileTransformer

    
    
    public class TransformerDemo implements ClassFileTransformer {
    
        public static final String editClassName = "Agent.Hello";
        public static final String editMethod = "Hello";
    
        @Override
        public byte[] transform(ClassLoader loader, String className, Class<?> classBeingRedefined, ProtectionDomain protectionDomain, byte[] classfileBuffer) throws IllegalClassFormatException {
            try {
                ClassPool cp = ClassPool.getDefault();
                if (classBeingRedefined != null) {
                    ClassClassPath ccp = new ClassClassPath(classBeingRedefined);
                    cp.insertClassPath(ccp);
                }
                CtClass ctc = cp.get(editClassName);
                CtMethod method = ctc.getDeclaredMethod(editMethod);
    
                //将Hello中的函数体改成System.out.println("Has been modified");
                String source = "{System.out.println(\"Has been modified\");}";
                method.setBody(source);
                byte[] bytes = ctc.toBytecode();
                ctc.detach();
                return bytes;
            } catch (Exception e){
                e.printStackTrace();
            }
            return null;
        }
    }
    

**agent.mf**

**注意** ：如果需要修改已经被JVM加载过的类的字节码，那么还需要设置在 MANIFEST.MF 中添加 Can-Retransform-Classes: true 或 Can-Redefine-Classes: true，其次别忘了空格

    
    
    Manifest-Version: 1.0
    Can-Redefine-Classes: true
    Can-Retransform-Classes: true
    Agent-Class: Agent.AgentMainDemo
    

打成jar包

    
    
    jar cvfm agent.jar Hello.mf Agent\AgentMainDemo.class
    

运行HelloWorld，获取其进程号，然后通过自定义的Attch类加载agent包

    
    
    public class AttchDemo {
        public static void main(String[] args) throws AgentLoadException, IOException, AgentInitializationException, AttachNotSupportedException {
            VirtualMachine attach = VirtualMachine.attach("15484");  // 命令行找到这个jvm的进程号
            attach.loadAgent("D:\\java\\AgentMemory\\target\\classes\\agent.jar");
            attach.detach();
        }
    }
    

可看到结果原本应该是输出：

    
    
    This is Sentiment !
    This is Sentiment !
    

但在输出第二条语句时通过agentMain的Transform进行了拦截修改成了`Has been modified`，因此结果为：

    
    
    This is Sentiment !
    Has been modified
    

