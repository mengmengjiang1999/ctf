# 前置知识

## JavaAgent

在之前的文章中有了解过：<https://blog.csdn.net/weixin_54902210/article/details/129614431>

## Javassist

Javassist (JAVA programming ASSISTant) 是在 Java 中编辑字节码的类库;它使 Java
程序能够在运行时定义一个新类, 并在 JVM 加载时修改类文件。原理与反射类似，但开销相对较低。

## 常用API

### ClassPool

  * getDefault : 返回默认的 ClassPool 是单例模式的，一般通过该方法创建我们的 ClassPool；

  * appendClassPath, insertClassPath : 将一个 ClassPath 加到类搜索路径的末尾位置 或 插 入到起始位置。通常通过该方法写入额外的类搜索路径，以解决多个类加载器环境中 找不到类的尴尬；

  * get , getCtClass : 根据类路径名获取该类的 CtClass 对象，用于后续的编辑。

  * makeClass：创建一个新的类。

### CtClass

  * freeze : 冻结一个类，使其不可修改；

  * isFrozen : 判断一个类是否已被冻结；

  * defrost : 解冻一个类，使其可以被修改。如果事先知道一个类会被 defrost， 则禁止 调用 prune 方法；

  * prune : 删除类不必要的属性，以减少内存占用。调用该方法后，许多方法无法将无 法正常使用，慎用；

  * detach : 将该 class 从 ClassPool 中删除；

  * writeFile : 根据 CtClass 生成 .class 文件；

  * toClass : 通过类加载器加载该 CtClass。

### CtMethod

  * insertBefore : 在方法的起始位置插入代码；

  * insterAfter : 在方法的所有 return 语句前插入代码以确保语句能够被执行，除非遇到 exception；

  * insertAt : 在指定的位置插入代码；

  * setBody : 将方法的内容设置为要写入的代码，当方法被 abstract 修饰时，该修饰符被 移除；

  * make : 创建一个新的方法。

# Javaassist 操作字节码示例

### 1、创建Hello类

    
    
    public class Demo1 {
        public static void main(String[] args) throws NotFoundException, IOException, CannotCompileException {
            ClassPool cp = ClassPool.getDefault();
            CtClass ctClass = cp.makeClass("Javassist.Hello");
            ctClass.writeFile();
        }
    }
    

![](./img/3678352700226590418.png)

### 2、添加属性

    
    
    public static void main(String[] args) throws NotFoundException, IOException, CannotCompileException {
        //1、创建Hello类
        ClassPool cp = ClassPool.getDefault();
        CtClass ctClass = cp.makeClass("Javassist.Hello");
    
        //2、添加属性
        CtField name = new CtField(cp.get("java.lang.String"), "name", ctClass);
        name.setModifiers(Modifier.PUBLIC);
        ctClass.addField(name,CtField.Initializer.constant("Sentiment"));
        ctClass.writeFile();
    }
    

![](./img/3853630282884175498.png)  
属性赋值时也可用：

    
    
    ctClass.addField(name,"name=\"Sentiment\"");
    

但这种赋值偏向于用构造器等进行初始化

### 3、添加方法

可以设置的返回类型：

    
    
    public static CtClass booleanType;
    public static CtClass charType;
    public static CtClass byteType;
    public static CtClass shortType;
    public static CtClass intType;
    public static CtClass longType;
    public static CtClass floatType;
    public static CtClass doubleType;
    public static CtClass voidType;
    

这里可以发现不支持String类型，在Java字节码中，String类型在方法的参数列表和返回值类型中，通常不是直接使用字符串，而是使用字符串在常量池中的索引值。如果想设置String类型的话可以用：`cp.getCtClass("java.lang.String")`

    
    
    CtMethod ctMethod = new CtMethod(CtClass.voidType, "Hello1", new CtClass[]{CtClass.intType, CtClass.charType}, ctClass);
    ctMethod.setModifiers(Modifier.PUBLIC);
    ctClass.addMethod(ctMethod);
    ctClass.writeFile();
    

![](./img/2910618612845552224.png)

#### 设置方法体

    
    
    ctMethod.setBody("System.out.println(\"This is test !\");");
    

#### 在方法体的前后分别插入代码

这里有参构造的形参是var1，如果要输出var1，就要用到特殊变量$1、$2(具体使用后边再说)

    
    
    CtMethod ctMethod = new CtMethod(CtClass.voidType, "Hello1", new CtClass[]{CtClass.intType, CtClass.charType}, ctClass);
    ctMethod.setModifiers(Modifier.PUBLIC);
    ctMethod.setBody("System.out.println(\"This is test !\");");
    ctClass.addMethod(ctMethod);
    ctMethod.insertBefore("System.out.println(\"我在前面插入:\"+$1);");
    ctMethod.insertAfter("System.out.println(\"我在后面插入了:\"+$2);");
    ctClass.writeFile();
    

![](./img/8721882309273445193.png)

### 4、添加构造器

直接添加的有参构造，无参构造去掉中间的参数即可

    
    
    CtConstructor cons = new CtConstructor(new CtClass[]{cp.getCtClass("java.lang.String")}, ctClass);
    cons.setBody("{name=\"Sentiment\";}");
    ctClass.addConstructor(cons);
    

设置`name=var1`

    
    
    {$0.name = $1;}
    

![](./img/2951693663452439308.png)

### 5、修改已有类

可以通过ClassPool的get方法获取已有类，并进行修改

    
    
    package Javassist;
    
    import javassist.*;
    
    import java.io.IOException;
    
    public class Demo02 {
        public static void main(String[] args) throws NotFoundException, CannotCompileException, IOException {
            ClassPool cp = ClassPool.getDefault();
            CtClass ctClass = cp.get("Javassist.Test");
            CtConstructor test = ctClass.getConstructors()[0];
            test.setBody("{System.out.println(\"Changing......\");}");
            ctClass.writeFile();
        }
    
    }
    class Test {
        public static String name = "Sentiment";
    
        public Test() {
            System.out.println("This is test !");
        }
    }
    

![](./img/4973213792644621135.png)

### 6、加载字节码

通过自带的toBytecode()转换下即可

    
    
    ctClass.toBytecode();
    ctClass.toClass().newInstance();
    

## Javassist 特殊变量

标识符 | 作用  
---|---  
$0、$1、$2、 3 、 3、 3、… | this和方法参数（1-N是方法参数的顺序）  
$args | 方法参数数组，类型为Object[]  
$$ | 所有方法参数，例如：m($$)相当于m($1,$2,…)  
$cflow(…) | control flow 变量  
$r | 返回结果的类型，在强制转换表达式中使用。  
$w | 包装器类型，在强制转换表达式中使用。  
$_ | 方法的返回值  
$sig | 类型为java.lang.Class的参数类型对象数组  
$type | 类型为java.lang.Class的返回值类型  
$class | 类型为java.lang.Class的正在修改的类  
  
### 1、$0,$1,$2,…

$0代表this，$1、$2代表方法的形参，通过上边例子也不难看出。这里需要注意：静态方法是没有$0的

### 2、$args

$args变量表示所有参数的数组，它是一个Object类型的数组（new Object[]{…}），如果参数中有原始类型的参数，会被转换成对应的包装类型。

![](./img/1762005008613496748.png)

### 3、$$

$$是方法所有参数的简写

    
    
    public static void main(String[] args) throws NotFoundException, CannotCompileException, IOException {
        ClassPool cp = ClassPool.getDefault();
        CtClass ctClass = cp.makeClass("Javassist.SpecialVariables");
        CtMethod ctMethod = new CtMethod(CtClass.voidType, "Test1",
                new CtClass[]{CtClass.intType, CtClass.doubleType}, ctClass);
        ctMethod.setModifiers(Modifier.PUBLIC);
        ctMethod.setBody("System.out.println($args);");
        ctClass.addMethod(ctMethod);
    
        //Test2方法调用Test1
        CtMethod ctMethod1 = new CtMethod(CtClass.voidType, "Test2",
                new CtClass[]{CtClass.intType, CtClass.doubleType}, ctClass);
        ctMethod1.setModifiers(Modifier.PUBLIC);
        ctMethod1.setBody("Test1($$);");
        ctClass.addMethod(ctMethod1);
        ctClass.writeFile();
    }
    

这里在定义一个Test2方法调用Test1，传参时写成`Test1($$)`就相当于`Test1($1,$2)`

![](./img/2816453673948488846.png)  
剩下的遇到了再看吧。

## Javassist 修改代码

Javassist 仅允许修改一个方法体中的表达式。javassist.expr.ExprEditor 是一个用来替换 方法体内表达式的类。用户可以定义
ExprEditor 的子类来制定表达式的修改

### javassist.expr.MethodCall

当修改某个方法中的代码时，可以用MethodCall进行回环调用找到我们要改的函数，并通过replace()进行修改。

这里定义了一个print方法，并用到了print和println两个方法，之后通过MethodCall的getMethodName获取到该方法中调用的方法

![](./img/5374002338026307155.png)  
所以这里可以做一个判断，当getMethodName等于print时既可以使用replace方法进行替换，由于只改方法不该参数，所以用$$直接代替原来的参数即可

    
    
    package Javassist;
    
    import javassist.*;
    import javassist.expr.ExprEditor;
    import javassist.expr.MethodCall;
    
    import java.io.IOException;
    
    public class Demo04 {
        public static void main(String[] args) throws NotFoundException, CannotCompileException, IOException {
            ClassPool cp = ClassPool.getDefault();
            CtClass ctClass = cp.get("Javassist.Change");
            CtMethod ctMethod = ctClass.getDeclaredMethod("print");
            ctMethod.instrument(
                    new ExprEditor(){
                        public void edit(MethodCall m)
                            throws CannotCompileException{
                                if (m.getClassName().equals("java.io.PrintStream")
                                        &&m.getMethodName().equals("print")){
                                    m.replace("System.out.println($$);");
                                }
                        }
                    }
            );
            ctClass.writeFile();
        }
    }
    class Change {
        public static String name = "Sentiment";
    
        public void print() {
            System.out.println("This is one !");
            System.out.print("This is two !");
        }
    }
    

![](./img/8902798767620507602.png)

### javassist.expr.ConstructorCall

修改控制器的与上同理

# RASP

​ RASP(Runtime application self-protection，应用程序运行时防护)，其与WAF等传统安全防护措施的主要区别于其防护层级更加底层——在功能调用前或调用时能获取访问到当前方法的参数等信息，根据这些信息来判定是否安全。

## Rasp 与 Waf 区别

### 优点

  * **误报率低** ：WAF 放置在 Web 应用程序外层，依赖于分析网络流量，拦截所有它认为可疑的输入而并不分析这些输入是如何被应用程序处理的。RASP 通过对应用程序上下文，会精确分析用户输入在应用程序里的行为，根据分析结果区分合法行为还是攻击行为，然后对攻击行为进行响应和处理。 RASP 不依赖于网络流量分析，大大减少了误报。
  * **保护全面性** ：WAF 在分析与过滤用户输入并检测有害行为方面比较有效，但是对应用程序的输出检查则毫无办法。RASP 不但能监控用户输入，也能监控应用程序组件的输出，这就使 RASP 具备了全面防护的能力。RASP 解决方案能够定位 WAF 通常无法检测到的严重问题——未处理的异常、会话劫持、权限提升和敏感数据披露等等。

### 缺点

  * **性能损耗** ：RASP 实时拦截、深入检测用户数据流，这是对精确度和误判率都有很大的帮助，但是对用户性能有一些影响，这些性能消耗也必然影响到用户的体验，这也是影响企业客户部署 RASP 的很大一方面原因。现在 RASP 的提供商在优化方面做了很大努力，大部分 RASP 对性能影响在 5% 左右。
  * **部署成本** ：RASP 是针对应用程序的，每个应用程序都必须有独立的探针，不能像防火墙一样只在入口放置一个设备就可以了，并且需要根据应用开发的技术不同使用不同的 RASP。比如 PHP 应用与 Java 应用需要不同的 RASP 产品，增加了部署成本。

## 双亲委派

简单解释下就是，如下三个类，在JVM加载某个类时，会先从BootstrapClassLoader进行加载，如果它没有则会从ExtClassLoader，还没有则到AppClassLoader，最终到自定义的类加载器

  * 启动类加载器(BootstrapClassLoader)，由C++实现，没有父类。
  * 拓展类加载器(ExtClassLoader)，由Java语言实现，父类加载器为null
  * 系统类加载器(AppClassLoader)，由Java语言实现，父类加载器为ExtClassLoader

而默认情况下premain，agentmain都是由AppClassLoader加载的，用一个实例看一下

**Main.java**

内容随便，这个只是后边会用到

    
    
    public class Main {
        public static void main(String[] args) throws IOException {
            ProcessBuilder command = new ProcessBuilder().command("cmd", "/c", "chdir");
            Process process = command.start();
            InputStream inputStream = process.getInputStream();
            BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(inputStream));
            System.out.println(bufferedReader.readLine());
        }
    }
    

**ClassLoaderDemo**

    
    
    public class ClassLoaderDemo {
        public static void premain(String agentArgs, Instrumentation inst) throws IOException, UnmodifiableClassException {
            System.out.println(ClassLoader.getSystemClassLoader().toString());
        }
    }
    

分别打成jar包后执行：

    
    
    java -javaagent:agent.jar=Sentiment -jar Main.jar
    

可以看到当前使用的类加载器是AppClassLoader

![](./img/6805259925817817689.png)  
而这就会引起一个问题

### 问题

**这里直接引用的参考文章里师傅写的内容，但是好像有些不准确的地方，因此简单了解下就好**

>
> agentmain和main都是同一个appClassLoader加载的，并且我们写好的各种类都是AppClassLoader加载的，那BootstrapClassLoader和extClassLoader加载的类调用我们写好的代理方法，这些类加载器向上委派寻找类时，扩展类加载器和引导类加载器都没有加过，直接违背双亲委派原则！举个例子，因为我们可以在transform函数里面获取到类字节码，并加以修改，如果我们在系统类方法前面插了代理方法，由于这些系统类是被Bootstrap
> ClassLoader加载的，当BootstrapClassLoader检查这些代理方法是否被加载时，直接就报错了，因为代理类是appClassLoader加载的

要解决这个问题，我们就应该想办法把代理类通过BootstrapClassLoader进行加载，从百度的OpenRASP可以学到解决方案：

    
    
    // localJarPath为代理jar包的绝对路径
    inst.appendToBootstrapClassLoaderSearch(new JarFile(localJarPath))
    

通过`appendToBootstrapClassLoaderSearch`方法，可以把一个jar包放到Bootstrap
ClassLoader的搜索路径，也就是说，当Bootstrap
ClassLoader检查自身加载过的类，发现没有找到目标类时，会在指定的jar文件中搜索，从而避免前面提到的违背双亲委派问题。

## RaspDemo

这里编写一个Hook ProcessBuilder执行cmd的简单例子，同时也遇到了上述提到的双亲委派问题，之后会提到。

**Main.java**

主程序不变

    
    
    public class Main {
        public static void main(String[] args) throws IOException {
            ProcessBuilder command = new ProcessBuilder().command("cmd", "/c", "chdir");
            Process process = command.start();
            InputStream inputStream = process.getInputStream();
            BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(inputStream));
            System.out.println(bufferedReader.readLine());
        }
    }
    

**PreMainDemo**

    
    
    public class PreMainDemo {
        public static void premain(String agentArgs, Instrumentation inst) throws IOException, UnmodifiableClassException {
            Class[] classes = inst.getAllLoadedClasses();
            for (Class aClass : classes) {
                if (aClass.getName().equals("java.lang.ProcessBuilder") && inst.isModifiableClass(aClass)){
                    inst.addTransformer(new TransformerDemo(),true);
                    inst.retransformClasses(aClass);
                }
            }
        }
    }
    

**TransformerDemo**

    
    
    public class TransformerDemo implements ClassFileTransformer {
    
        public byte[] transform(ClassLoader loader, String className, Class<?> classBeingRedefined, ProtectionDomain protectionDomain, byte[] classfileBuffer) {
            byte[] bytes = null;
            if (className.equals("java/lang/ProcessBuilder")) {
                ClassPool cp = ClassPool.getDefault();
                CtClass ctClass = null;
                try {
                    ctClass = cp.get("java.lang.ProcessBuilder");
                    CtMethod[] methods = ctClass.getMethods();
                    String source = "if ($0.command.get(0).equals(\"cmd\")){\n" +
                            "    System.out.println(\"Dangerous....\");\n" +
                            "    System.out.println($0);\n" +
                            "    return null;\n" +
                            "}";
                    for (CtMethod method : methods) {
                        if (method.getName().equals("start")) {
                            method.insertBefore(source);
                            break;
                        }
                    }
                    bytes = ctClass.toBytecode();
                } catch (NotFoundException | CannotCompileException | IOException e) {
                    e.printStackTrace();
                } finally {
                    if (ctClass != null) {
                        ctClass.detach();
                    }
                }
            }
            return bytes;
        }
    }
    

### 双亲委派问题

上述PreMainDemo中，通过if判断，来找到JVM加载的ProcessBuilder类，进而触发transform对该类进行修改

    
    
    if (aClass.getName().equals("java.lang.ProcessBuilder") && inst.isModifiableClass(aClass)){
    

但是当执行之后发现，JVM并没有加载ProcessBuilder类，那就无法通过if判断，触发transform

#### 猜想

上述问题我上网找了一些资料，但各抒己见，所以说说我的看法。( **仅个人观点，望师傅们指正！！！** )

上边提到premain函数默认使用AppClassLoader进行加载的，并且我们在代码中也没有加载ProcessBuilder类，因此默认不会加载ProcessBuilder类。因为该类在rt.jar包中，而该包是由`BootstrapClassLoader`进行加载的

#### 解决

既然没有加载ProcessBuilder类，那就可以在遍历JVM加载类之前，用`ProcessBuilder processBuilder = new
ProcessBuilder();`对其进行加载即可。

    
    
    public class PreMainDemo {
        public static void premain(String agentArgs, Instrumentation inst) throws IOException, UnmodifiableClassException, ClassNotFoundException, InstantiationException, IllegalAccessException {
    
            ProcessBuilder processBuilder = new ProcessBuilder();
    
            Class[] classes = inst.getAllLoadedClasses();
            for (Class aClass : classes) {
                if (aClass.getName().equals("java.lang.ProcessBuilder") && inst.isModifiableClass(aClass)){
                    inst.addTransformer(new TransformerDemo(),true);
                    inst.retransformClasses(aClass);
                }
            }
        }
    }
    

这里其实就可以在复制一遍Main中的代码，因为这样的话即可看出在触发Transofrom前后执行`cmd`的结果

最终代码

    
    
    public class PreMainDemo {
        public static void premain(String agentArgs, Instrumentation inst) throws IOException, UnmodifiableClassException, ClassNotFoundException, InstantiationException, IllegalAccessException {
            ProcessBuilder command = new ProcessBuilder().command("cmd", "/c", "chdir");
            Process process = command.start();
            InputStream inputStream = process.getInputStream();
            BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(inputStream));
            System.out.println(bufferedReader.readLine());
    
            Class[] classes = inst.getAllLoadedClasses();
            for (Class aClass : classes) {
                if (aClass.getName().equals("java.lang.ProcessBuilder") && inst.isModifiableClass(aClass)){
                    inst.addTransformer(new TransformerDemo(),true);
                    inst.retransformClasses(aClass);
                }
            }
        }
    }
    

接着将Main.java和 打包

**Main.jar**

    
    
    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-jar-plugin</artifactId>
                <configuration>
                    <archive>
                        <manifestEntries>
                            <Main-Class>RASP.Main</Main-Class>
                        </manifestEntries>
                    </archive>
                </configuration>
            </plugin>
        </plugins>
    </build>
    

**agent.jar**

    
    
    <build>
            <plugins>
                <plugin>
                    <groupId>org.apache.maven.plugins</groupId>
                    <artifactId>maven-jar-plugin</artifactId>
                </plugin>
    
                <plugin>
                    <artifactId>maven-assembly-plugin</artifactId>
                    <configuration>
                        <archive>
                            <manifestEntries>
                                <Premain-Class>RASP.PreMainDemo</Premain-Class>
                                <Can-Redefine-Classes>true</Can-Redefine-Classes>
                                <Can-Retransform-Classes>true</Can-Retransform-Classes>
                            </manifestEntries>
                        </archive>
                        <descriptorRefs>
                            <descriptorRef>jar-with-dependencies</descriptorRef>
                        </descriptorRefs>
                    </configuration>
                    <executions>
                        <execution>
                            <id>make-assembly</id>
                            <phase>package</phase>
                            <goals>
                                <goal>single</goal>
                            </goals>
                        </execution>
                    </executions>
                </plugin>
            </plugins>
        </build>
    

执行agent

    
    
    java -javaagent:AgentMemory-1.0-SNAPSHOT-jar-with-dependencies.jar=Sentiment -jar AgentMemory-1.0-SNAPSHOT.jar
    

可以看到一开始执行了chdir输出了`D:\java\AgentMemory\target`，因为此时还没触发transform，但之后触发后，输出了Dangerous，并返回了null，所以这里在`InputStream
inputStream = process.getInputStream();`爆了空指针异常，成功hook

![](./img/1735183419938147398.png)

