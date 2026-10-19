## 简介

https://openjdk.org/jeps/290

`Filter Incoming Serialization Data`过滤传入的序列化数据

JEP290是Java官方提供的一套来防御反序列化的机制，其核心在于提供了一个ObjectInputFilter接口，通过设置filter对象，然后在反序列化（ObjectInputStream#readObject）的时候触发filter的检测

JEP 290 在 JDK 9 中加入，但在 JDK 6,7,8 一些高版本中也添加了：

    
    
    Java? SE Development Kit 8, Update 121 (JDK 8u121)
    
    Java? SE Development Kit 7, Update 131 (JDK 7u131)
    
    Java? SE Development Kit 6, Update 141 (JDK 6u141)
    

## 处理

我这里的JDK是 8u202版本

### ObjectInputStream

对于`ObjectInputStream`类来说，主要的过滤方法为`filterCheck`

![image-20221009185828921.png](https://image.3001.net/images/20221012/1665582237_6346c49d148faf4c463ab.png!small)

根据注释，我们知道这个方法主要是当序列化过滤器不为空的时候触发该过滤器

其中反序列化过滤器就为`serialFilter`属性值，跟进一下

![image-20221009190023383.png](https://image.3001.net/images/20221012/1665582243_6346c4a3d181789907bcd.png!small)

这是一个`ObjectInputFilter`接口，根据注释我们知道从流中读取类的类描述符和类的过滤器，可以不进行配置

我们看看该类的构造方法

![image-20221009190254010.png](https://image.3001.net/images/20221012/1665582249_6346c4a946102d365db29.png!small)

默认会对`serialFilter`属性进行赋值操作，跟进`ObjectInputFilter.Config.getSerialFilter()`方法的调用

![image-20221009190420085.png](https://image.3001.net/images/20221012/1665582255_6346c4af3099aca00f92b.png!small)

获取的是`ObjectInputFilter`中的内部静态类`Config`的`serialFilter`属性

跟下来回到`filterCheck`方法的分析

![image-20221009190703164.png](https://image.3001.net/images/20221012/1665582262_6346c4b623ea8faf55f5f.png!small)

首先就会判断是否具有`serialFilter`这个过滤器，如果不为空，将会调用过滤器的`checkInput`方法进行过滤处理，传入了`clazz /
arrayLength / depth`等信息

![image-20221009191015234.png](https://image.3001.net/images/20221012/1665582268_6346c4bc001c36662a5d0.png!small)

这个方法返回的是一个`ObjectInputFilter.Status`，这是一个枚举类型

![image-20221009191057036.png](https://image.3001.net/images/20221012/1665582275_6346c4c37af8c3bf7242c.png!small)

接下来回到`filterCheck`方法

如果返回的状态为`null/REJECTED`两个之一，将会抛出异常

所以，对于过滤器的设置，我们可以通过创建一个`ObjectInputFilter`实例，并重写他的`checkInput`方法，在其中实现我们的过滤逻辑，之后通过调用`ObjectInputStream#setInternalObjectInputFilter`进行为stream添加过滤器

![image-20221009191546558.png](https://image.3001.net/images/20221012/1665582284_6346c4ccb54afcbccdc20.png!small)

### ObjectInputFilter$Config

在这个类中，存在有一个静态代码块

![image-20221009194839656.png](https://image.3001.net/images/20221012/1665582291_6346c4d334c385fa7a58a.png!small)

在调用该类的时候就会为`serialFilter`属性赋值，跟进到`configuredFilter`属性的来源

![image-20221009194957544.png](https://image.3001.net/images/20221012/1665582298_6346c4da96900a010a628.png!small)

主要是获取`jdk.serialFilter`属性值，之后通过调用`createFilter`方法进行过滤器的创建

跟进一下`createFilter`方法的调用

![image-20221009195401018.png](https://image.3001.net/images/20221012/1665582317_6346c4ed96679ab11ab26.png!small)

这个方法将会调用`ObjectInputFilter.Config.Global.createFilter`方法进行创建

### ObjectInputFilter$Config$Global

接着上面的分析，我们跟进该类的`createFilter`方法

![image-20221009195813279.png](https://image.3001.net/images/20221012/1665582330_6346c4fa51389488a94a0.png!small)

将传入的JEP规则字符串var0传入`Global`内部静态类的构造方法中，创建了一个Golbal对象，进行返回，所以前面在`ObjectInputStream`类的构造方法中主要是为`serialFilter`赋值的是一个Global类

查看官方文档，我们知道JEP 290的编写规则为

  1. 如果模式以“！”开头，如果模式的其余部分匹配，则该类被拒绝，否则被接受

  2. 如果模式包含“/”，则“/”之前的非空前缀是模块名称。如果模块名称与类的模块名称匹配，则剩余模式与类名称匹配。如果没有“/”，则不比较模块名称。

  3. 如果模式以“.**”结尾，则它匹配包和所有子包中的任何类

  4. 如果模式以“.*”结尾，它匹配包中的任何类

  5. 如果模式以“*”结尾，它匹配任何以该模式为前缀的类。

  6. 如果模式等于类名，则匹配。

  7. 否则，状态未定

>   * If the pattern starts with "`!`", the class is rejected if the rest of
> the pattern matches, otherwise it is accepted
>
>   * If the pattern contains "/", the non-empty prefix up to the "/" is the
> module name. If the module name matches the module name of the class then
> the remaining pattern is matched with the class name. If there is no "/",
> the module name is not compared.
>
>   * If the pattern ends with "`.**`" it matches any class in the package and
> all subpackages
>
>   * If the pattern ends with "`.*`" it matches any class in the package
>
>   * If the pattern ends with "`*`", it matches any class with the pattern as
> a prefix.
>
>   * If the pattern is equal to the class name, it matches.
>
>   * Otherwise, the status is undecided.
>
>

接下来看看Global构造方法中是如何进行解析的

![image-20221009201153578.png](https://image.3001.net/images/20221012/1665582339_6346c5030f87af5b0edae.png!small)

首先是通过传入的规则var1，将其根据`;`进行分割，并初始化`filters`属性为`ArrayList`数组

![image-20221009201516961.png](https://image.3001.net/images/20221012/1665582344_6346c50827dada13227e7.png!small)

首先判断是否以`*`结尾，进而判断是否是`.*`结尾，如果是以`!`开头的话成功匹配的话，将会通过lambada的格式调用`this.filters.add`将`Status`放置于`filters`属性中，这里举个例子就行了，后面就也就是同样的格式，进行`filters`属性的添加

我们看看`filters`属性是个什么东西？

![image-20221009202802332.png](https://image.3001.net/images/20221012/1665582349_6346c50df163b90904b33.png!small)

这是一个函数列表

这样成功设置了过滤器，当我们调用的时候将会调用

    
    
    ObjectInputStream#filterCheck
        ObjectInputFilter$Config$Global#checkInput
    

![image-20221009203807974.png](https://image.3001.net/images/20221012/1665582355_6346c513f06deb07c33cd.png!small)

主要是根据遍历`filters`属性通过反序列化的类进行获取对应的`Status`状态

## 过滤器

### 全局过滤器

通过前面的分析，我们可以知道在`ObjectInputFilter$Config`类中属性`configuredFilter`中获取了`jdk.serialFilter`属性值，这里就是全局过滤器

对于该属性值的设置有两种方式

  1. 配置JVM的`jdk.serialFilter`

  2. 配置`%JAVA_HOME%\conf\security\java.security`中的`jdk.serialFilter`字段

### 局部过滤器

同样有着两种方法进行设置

  1. 在创建`ObjectInputStream`对象之后通过调用其`setInternalObjectInputFilter`方法进行设置

  2. 又或者是调用`Config#setObjectInputFilter`方法进行设置

