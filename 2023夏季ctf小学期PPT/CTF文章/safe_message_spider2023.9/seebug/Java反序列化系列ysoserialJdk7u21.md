**作者：天融信阿尔法实验室**  
**原文链接：<https://mp.weixin.qq.com/s/qlg3IzyIc79GABSSUyt-OQ>**

## 1\. Jdk7U21漏洞简介

谈到java的反序列化，就绕不开一个经典的漏洞，在ysoserial 的payloads目录下
有一个jdk7u21，以往的反序列化Gadget都是需要借助第三方库才可以成功执行，但是jdk7u21的Gadget执行过程中所用到的所有类都存在在JDK中，JRE版本<=7u21都会存在此漏洞

## 2\. Jdk7u21漏洞原理深入讲解

### 2.1 漏洞执行流程

整体的恶意对象的封装整理成了脑图，如下图所示

![](https://images.seebug.org/content/images/2020/05/abfd01ca-62cc-4ad9-80e0-c7ce8fee9d51.png-w331s)

这里用到了TemplatesImpl对象来封装我们的恶意代码，其封装和代码执行的流程在[《Java 反序列化系列 ysoserial
Hibernate1》](https://mp.weixin.qq.com/s/O1ay4BHiyPBkotNIgDQ6Kg)中针对这种利用已经进行了详细的讲解，基本原理是通过动态字节码生成一个类，该类的静态代码块中存储有我们所要执行的恶意代码，最终通过TemplatesImpl.newTransformer()实例化该恶意类从而触发其静态代码块中的恶意代码，关于TemplatesImpl的详细分析可以去查看java
反序列化系列 Hibernate1中去学习了解。

首先最外层的是LinkedHashSet
类，看过该类源码的同学应该都清楚，该类其实是基于HashMap实现的。我们首先来看LinkedHashSet的readObject方法。

    
    
        private void readObject(java.io.ObjectInputStream s)
            throws java.io.IOException, ClassNotFoundException {
            // Read in any hidden serialization magic
            s.defaultReadObject();
    
            // Read in HashMap capacity and load factor and create backing HashMap
            int capacity = s.readInt();
            float loadFactor = s.readFloat();
            map = (((HashSet)this) instanceof LinkedHashSet ?
                   new LinkedHashMap<E,Object>(capacity, loadFactor) :
                   new HashMap<E,Object>(capacity, loadFactor));
    
            // Read in size
            int size = s.readInt();
    
            // Read in all elements in the proper order.
            for (int i=0; i<size; i++) {
                E e = (E) s.readObject();
                map.put(e, PRESENT);
            }
        }
    }

该方法最后可以看到有一个for循环，将LinkedHashSet对象在序列化时一个一个被序列化的元素在反序列化回来。该循环体中有一行代码
`map.put(e,PRESENT)`
这里的map变量指向的是一个LinkedHashMap对象，PRESENT常量的值是一个空的Object对象由下图可知

![](https://images.seebug.org/content/images/2020/05/1f865d80-35f3-4fbe-813b-5b4b3331fc5c.png-w331s)

此时的变量e指向的是我们实现封装进LinkedHashSet里的TemplatesImpl对象，里面存有我们的恶意代码

![](https://images.seebug.org/content/images/2020/05/27b7038f-0dd6-4077-8eed-3c51eb4435a7.png-w331s)

接下来我们来看LinkedHashMap.put方法的实现

    
    
    public V put(K key, V value) {
        if (key == null)
            return putForNullKey(value);
        int hash = hash(key);
        int i = indexFor(hash, table.length);
        for (Entry<K,V> e = table[i]; e != null; e = e.next) {
            Object k;
            if (e.hash == hash && ((k = e.key) == key || key.equals(k))) {
                V oldValue = e.value;
                e.value = value;
                e.recordAccess(this);
                return oldValue;
            }
        }
    
        modCount++;
        addEntry(hash, key, value, i);
        return null;
    }

大概流程就是判断其key值的hash是否一致
如果不一致则证明是一个新的元素从而加入到当前的HashMap对象中，如果hash一致则进行判断该元素是否存在于当前的HashMap中如果存在则返回oldValue,如果不存在则加入当前HashMap对象中。

这里核心关键点就是如何让程序执行到key.equals，此时的key指向的是我们通过动态代理生成的Proxy对象，我们知道调用Proxy对象的任何方法，本质上都是在调用，InvokcationHandler
对象中被重写的invoke方法。因为生成Proxy对象时传入的参数是InvokcationHandler的子类AnnotationInvocationHandler，所以自然要调用AnnotationInvocationHandler.invoke()方法。

我们来看该方法的具体实现

![](https://images.seebug.org/content/images/2020/05/5264ee3e-6e71-4f98-9552-cc683d41dca8.png-w331s)

通过观察代码我们可以看到接下来会调用equalsImpl()方法，传入的var3参数是封装了我们恶意代码的TemplatesImpl对象

    
    
    private Boolean equalsImpl(Object var1) {
        if (var1 == this) {
            .....
        } else {
            Method[] var2 = this.getMemberMethods();
            int var3 = var2.length;
    
            for(int var4 = 0; var4 < var3; ++var4) {
                Method var5 = var2[var4];
                String var6 = var5.getName();
                Object var7 = this.memberValues.get(var6);
                Object var8 = null;
                AnnotationInvocationHandler var9 = this.asOneOfUs(var1);
                if (var9 != null) {
                    var8 = var9.memberValues.get(var6);
                } else {
                    try {
                        var8 = var5.invoke(var1);
           ......

在这里我们可以看到有这么一行代码`var8 =
var5.invoke(var1);`这里就会调用TemplatesImpl.newTransformer()从而实例化恶意类，这里的var1我们清楚是我们传递进来的TemplatesImpl对象，但是var5的结果是怎么来的还需要分析一下。

从代码中可以看到`Method var5 = var2[var4];` var4=0 而`var2= this.getMemberMethods()；`

跟入getMemberMethods()方法

    
    
    private Method[] getMemberMethods() {
        if (this.memberMethods == null) {
            this.memberMethods = (Method[])AccessController.doPrivileged(new PrivilegedAction<Method[]>() {
                public Method[] run() {
                    Method[] var1 = AnnotationInvocationHandler.this.type.getDeclaredMethods();
                    AccessibleObject.setAccessible(var1, true);
                    return var1;
                }
            });
        }

该方法会循环获取AnnotationInvocationHandler.type中的方法，我们可以看到type对象指向了一个Templates.class对象

![](https://images.seebug.org/content/images/2020/05/776327b8-cbe3-4c3d-8c62-78b4150bbcee.png-w331s)

Templates是一个接口，该接口中只有两个抽象方法

![](https://images.seebug.org/content/images/2020/05/97da54eb-cc78-424b-a6ec-69a010e7a689.png-w331s)

所以getMemberMethods()方法返回的结果就是两个Method对象，一个是newTransformer的Method对象，一个是getOutputProperties的Method对象,这样我们是如何通过反射调用的TemplatesImpl.newTransformer()方法的逻辑就清晰了

![](https://images.seebug.org/content/images/2020/05/b41fb3ee-f170-4063-bc01-df3a791b13eb.png-w331s)

### 2.2 如何构造满足条件的hash值

但是有一个问题还没有解决，那就是刚才所讲的所有代码逻辑，都要在`key.equals(k)`可以执行的前提下才可以，那么究竟怎样才能执行`key.equals(k)`呢，我们来重新看一遍LinkedHashMap.put方法的部分实现

    
    
    public V put(K key, V value) {
        if (key == null)
            return putForNullKey(value);
        int hash = hash(key);
        int i = indexFor(hash, table.length);
        for (Entry<K,V> e = table[i]; e != null; e = e.next) {
            Object k;
            if (e.hash == hash && ((k = e.key) == key || key.equals(k))) {
            ......
            }

可以看到 需要满足一些条件
才可以执行到`key.equals(k)`接下来就详细讲一讲如何才能满足以上这些条件，这是笔者个人觉得整个漏洞利用中最难也是最让人拍案叫绝的思路。

首先第一次调用`map.put()`时传入的参数e是我们封装了恶意代码的TemplatesImpl对象，另一个参数就是一个空的Object对象

![](https://images.seebug.org/content/images/2020/05/d77b8c3a-ebed-42a5-85c5-b53586c335ac.png-w331s)

由下图代码可知，我们需要计算出key 也就是恶意TemplatesImpl对象的hash值

![](https://images.seebug.org/content/images/2020/05/216bc1b6-493c-4abe-9d40-bc2c2a8f84ee.png-w331s)

深入看hash方法的实现

    
    
    final int hash(Object k) {
        int h = 0;
        if (useAltHashing) {
            if (k instanceof String) {
                return sun.misc.Hashing.stringHash32((String) k);
            }
            h = hashSeed;
        }
    
        h ^= k.hashCode();
    
        // This function ensures that hashCodes that differ only by
        // constant multiples at each bit position have a bounded
        // number of collisions (approximately 8 at default load factor).
        h ^= (h >>> 20) ^ (h >>> 12);
        return h ^ (h >>> 7) ^ (h >>> 4);
    }

这里调用TemplatesImpl.hashCode()方法来得出hash值然后进行固定的异或操作，得出的最终结果进行返回，下面的截图中就是此次运算得出的hash值

![](https://images.seebug.org/content/images/2020/05/a72cb7d3-5231-41a4-a489-9f0ccde0f1e2.png-w331s)

接下来通过indexFor()函数 得到其hash索引 这里返回的索引值是12，并将值符給变量i
这里传入的table.legth，table是一个Entry数组，用来存放我们通过map.put()传入的键值对，并作为后续判断新传入的键值对和旧键值对是否重复的依据

    
    
    /**
     * Returns index for hash code h.
     */
    static int indexFor(int h, int length) {
        return h & (length-1);
    }

![](https://images.seebug.org/content/images/2020/05/36ae6a35-b055-4c61-83ef-bac2eea07de8.png-w331s)

接着就开始了第一次判断，首先当前table变量指向的Entry对象是空的，所以自然e 为null 在这里就不符合了，所以循环体内的代码不会执行

    
    
    for (Entry<K,V> e = table[i]; e != null; e = e.next）

跳过for循环体，然后计数器自增，并将此TemplatesImpl对象本身，还有其Hash值和索引放入到之前说到的table变量中。

![](https://images.seebug.org/content/images/2020/05/323cfcdd-5ac8-45c2-ba7f-486890b6929a.png-w331s)

接下来就开始第二次循环了，第二次传入的key就是触发TemplatesImpl.newTransformer()的媒介
Proxy对象了这个对象里有我们特意封装进去的AnnotationInvocationHandler对象。

![](https://images.seebug.org/content/images/2020/05/3c5706d6-4ebc-4fae-ac32-530fcdfb0826.png-w331s)

接下来问题就来了首先for循环中要满足e不为空，这就要求这次循环并计算Proxy对象从而得出的Hash值和Hash索引必须和上一次循环中的TemplatesImpl对象相同，这样才能在`Entry<K,V>
e = table[i]`这一步中，从table中取到对应索引的对象赋值給e，从而满足`e != null` 。

    
    
    for (Entry<K,V> e = table[i]; e != null; e = e.next)

那怎么才能让两个连类型都不相同的对象通过运算却能得出一样的hash值呢？接下载关键点就来了，也就是我们为什么生成Proxy对像时要传入AnnotationInvocationHandler对象。

在计算Proxy对象的hash值的时候 我们看到最终是通过调用Proxy.hashCode()来计算hash值

![](https://images.seebug.org/content/images/2020/05/e62a983c-0f22-43a8-a026-9e6d5d32c06a.png-w331s)

Proxy是一个动态代理对象，所以经过对调用方法名称的判断，最终调用AnnotationInvocationHandler.hashCodeImpl()方法

![](https://images.seebug.org/content/images/2020/05/38c01bfd-0ee2-4bbb-ada0-20e59b06a5d5.png-w331s)

以下是hashCodeImpl方法的实现,此时的var2是一个Iterator对象，用来遍历memberValues对象中存储的键值对

    
    
    private int hashCodeImpl() {
        int var1 = 0;
    
        Entry var3;
        for(Iterator var2 = this.memberValues.entrySet().iterator(); 
            var2.hasNext(); 
            var1 += 127 * ((String)var3.getKey()).hashCode() ^ memberValueHashCode(var3.getValue())) {
            var3 = (Entry)var2.next();
        }
    
        return var1;
    }

可以看到memberValues中只有一个键值对就是，就是我们在初期通过反射生成AnnotationInvocationHandler对象时传入的HashMap对象中的那个键值对
key是一个字符串"f5a5a608" Value值适合第一次循环时用来计算hash值的同一个TemplatesImpl对象

![](https://images.seebug.org/content/images/2020/05/a6711624-4c50-47c1-b525-b4a39917635e.png-w331s)

![](https://images.seebug.org/content/images/2020/05/caaa635d-74e2-42b7-a56b-fd5361bdd1d6.png-w331s)

![](https://images.seebug.org/content/images/2020/05/810a145b-abf1-4d6a-a554-1cf323521768.png-w331s)

我们在看一看var3此时的值。

![](https://images.seebug.org/content/images/2020/05/e157001d-3648-4e23-8156-5fe4fb1b4c37.png-w331s)

AnnotationInvocationHandler计算hash最关键的是这一段代码。简单来说就是127乘var3
key的hash值，然后和var3的value值的hash值进行异或操作

    
    
    var1 += 127 * ((String)var3.getKey()).hashCode() ^ memberValueHashCode(var3.getValue())

下面贴出memberValueHashCode方法的关键代码，返回var3的value值也就是TemplatesImpl对象的Hash值。

    
    
    private static int memberValueHashCode(Object var0) {
        Class var1 = var0.getClass();
        if (!var1.isArray()) {
            return var0.hashCode();

至此所得到的结果都是和第一次循环时得到的Hash值相同，但接下来就要解决如果在经过与`127 *
((String)var3.getKey()).hashCode()`进行异或操作后，保持结果不变。

我们知道0和任何数字进行异或，得到的结果都是被异或数本身。所以我们要让`127 *
((String)var3.getKey()).hashCode()`的结果等于0
也就是(String)var3.getKey()).hashCode()的值要为零

还记得我们var3的 key是什么么？是一个字符串 值为"f5a5a608" 这个字符串非常有意思我们看一下这个字符串的hash值是多少

![](https://images.seebug.org/content/images/2020/05/4be6b7e9-0087-409b-9d1f-32cc37c0352e.png-w331s)

![](https://images.seebug.org/content/images/2020/05/b471becc-296d-4cfe-8870-d42aa38d886f.png-w331s)

结果是0，完全符合我们的要求，这样127乘以0自然结果是0，0在同TemplatesImpl对象的hash值进行异或，得到的结果自然也是TemplatesImpl对象的hash值本身。这样就符合我们的要求。通过了LinkedHashMap.put方法中的for循环的判断，由于hash值相同，所以计算出的索引相同，e的值就为之前的TemplatesImpl对象，所以e不为null
结果为true

    
    
    for (Entry<K,V> e = table[i]; e != null; e = e.next) 

接下来好要通过if 判断中的前两个条件，因为&& 和|| 有短路效果，所以这三个条件我们要符合e.hash == hash为true (k = e.key)
== key为flase

    
    
    if (e.hash == hash && ((k = e.key) == key || key.equals(k)))

首先e.hash ==
hash是将第一次循环时的TemplatesImpl对象的hash取出同第二次循环时TemplatesImpl对象的hash进行对比，本来就都是同一个对象，所以自然时相同的，所以结果为true

(k = e.key) == key
将第一次循环时的key取出和第二次循环时的key做比对看是否相同，第一次循环的key是TemplatesImpl对象，而第二次循环时key时Proxy对象，所以结果为flase

如此这般，我们就通过了前两个判断条件，接下来自然就会执行key.equals(k)从而调用TemplatesImpl.newTransformer()方法并最终触发我们的恶意代码

至此jdk7u21漏洞原理分析完毕

## 3\. 总结

此次Jdk7u21
payload中作用到的所有类，均存在于JDK自身的代码中，无需再调用任何第三方jar包，所以当时爆出漏洞时影响极大。只要目标系统中使用的jdk版本并存在反序列化数据交互点就会存在远程代码执行漏洞。漏洞的触发点在LinkedHashSet，其实我们看代码的时候可以看到LinkedHashSet里面的方法都是调用了其父类HashSet中的方法，但是之所以不直接用HashSet的原因是LinkedHashSet里数据的下标和我们插入时的顺序一样，而HashSet顺序就不一样了。通过Hash值的匹配，然后执行到key.equals(k)最终执行到TemplatesImpl.newTransformer()方法

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1224/>

