# 一、 **XStream框架组成分析**

XStream是java实现对javaBean(实用类)简单快速进行序列化反序列化的框架。目前支持XML或JSON格式数据的序列化或反序列化过程。

![1631696991_6141b85f7d724eec3ded9.png!small](https://image.3001.net/images/20210915/1631696991_6141b85f7d724eec3ded9.png!small)

XStream总体主要由上图所示的五个接口和抽象类组成。其中，

 ** **AbsractDriver****
是为XStream提供解析器和编辑器的创建的抽象类。XStream默认使用的解析器是XppDriver(这也就解释为了什么XStream使用默认的构造方法创建XStream对象的时候，需要依赖Xpp类库
--如果没有导入对应版本的Xpp类库是会报错的)

 ** **MarshallingStrategy****
是编组和解组策略的核心接口。(其中，编组过程可以简单的理解为将JavaBean对象对应的属性参数逐个读取并按照指定的数据格式进行组合，最后整合成我们需要的XML或JSON数据格式；依此类推，解组过程就可以理解成是将xml或JSON数据按照节点的方式进行JavaBean类对象属性的读取解析过程)

 ** **Mapper****
映射器，XStream通过XML数据的elementName通过mapper获取对应类、成员、属性的class对象(这个步骤其实是和MarshallingStrategy的解组过程是相辅相成的)。它是支持解组和编组，所以方法是成对存在real
和serialized，他的子类MapperWrapper作为装饰者，包装了不同类型映射的映射器，如AnnotationMapper，ImplicitCollectionMapper，ClassAliasingMapper。(这个步骤可以理解为让mapper具有了解组和编组各种类的class对象的能力
---类似做的数学题类型的多少，通过不断累积题目类型才可以解出更多的题目，获取更高的分数)

 ** **ConverterLookup****
通过Mapper获取的class对象后，接着调用lookupConverterForType获取对应Class的转换器，将其转化成对应实例对象。DefaultConverterLookup是该接口的实现类，同时实现了ConverterRegistry的接口，所有DefaultConverterLookup具备查找converter功能和注册converter功能。所有注册的转换器按一定优先级组成由TreeSet保存的有序集合(PS:XStream
默认使用了DefaultConverterLookup)。

# 二、 **序列化及反序列化调用链分析**

写一个简单的测试案例，并在创建XStream对象的位置下一个断点，然后开始debug，看看创建对象过程中XStream框架的调用链究竟是什么样的呢？

1、XStream对象初始化过程利用链及源码分析

![1631697193_6141b929a9802bcdaf936.png!small](https://image.3001.net/images/20210915/1631697193_6141b929a9802bcdaf936.png!small)

StepInto，很明显我们我们进入了XStream的无参构造方法中，在这个方法中，传递了默认的接口反射提供者(与其他框架的反序列化方式不同，XStream利用的是java的反射机制
--也是为什么XStream不用限制javaBean类中setters、getters方法不用必须实现的原因；也是JavaBean类不用实现Serializeable接口，重写readObject()方法的确依然可以进行反序列化的原因)、Mapper映射器、以及解析器对象的创建(在默认的构造方法中，不难发现依赖的是自包含的XppDriver分层流驱动程序，也就是单纯的使用XMLPullParser()方法进行解析，并未依赖Xpp3类库的解析方法)

![1631697206_6141b93675ce542e8adb5.png!small](https://image.3001.net/images/20210915/1631697206_6141b93675ce542e8adb5.png!small)

执行完上面的无参构造方法后，执行参数带有接口反射提供者、Mapper、解析器对象的构造方法中，这次创建了一个扩展类加载器对象(编组或解组过程中，用来尝试加载特性的类)

![1631697215_6141b93f5832956c73942.png!small](https://image.3001.net/images/20210915/1631697215_6141b93f5832956c73942.png!small)

1 ：公共类加载器引用，对上一步构造方法中创建的类加载器对象的引用

2 ：创建转换器对象，用于将Mapper获取的class转换成对应的实例对象

![1631697225_6141b949870951ba9e320.png!small](https://image.3001.net/images/20210915/1631697225_6141b949870951ba9e320.png!small)

lookupConverterForType获取对应Class的转换器，将其转化成对应实例对象

![1631697236_6141b954be7f3b0c7efff.png!small](https://image.3001.net/images/20210915/1631697236_6141b954be7f3b0c7efff.png!small)

实现了ConverterRegistry的接口，所有DefaultConverterLookup具备查找converter功能和注册converter功能

![1631697246_6141b95ed04d88aa8181d.png!small](https://image.3001.net/images/20210915/1631697246_6141b95ed04d88aa8181d.png!small)

调用buildMapper()方法开始构建Mapper：XStream构建映射器，是通过MapperWrapper装饰者，将各个不同功能的映射器包装成Mapper

![1631697266_6141b9723e330878cce11.png!small](https://image.3001.net/images/20210915/1631697266_6141b9723e330878cce11.png!small)

MapperWrapper装饰者底层代码的逻辑就是将Mapper中的方法按不同功能划分成不同实现类，并通过装饰者进行装载(简单的理解是将各种类型的class都映射到mapper上去，使之具有获取和转换各种class实例的能力)

设置好映射器Mapper后就完成了XStream对象的初始化过程。。。

2、XML数据反序列化利用链

Xstream 调用fromXML

①把String转化成StringReader，HierarchicalStreamDriver通过StringReader创建HierarchicalStreamReader，最后调用MarshallingStrategy的unmarshal方法开始解组

![1631697870_6141bbceb01ec9f3892c1.png!small](https://image.3001.net/images/20210915/1631697870_6141bbceb01ec9f3892c1.png!small)

![1631697910_6141bbf6a36a2012bf38f.png!small](https://image.3001.net/images/20210915/1631697910_6141bbf6a36a2012bf38f.png!small)

![1631698017_6141bc6164a93514d8ecb.png!small](https://image.3001.net/images/20210915/1631698017_6141bc6164a93514d8ecb.png!small)

②marshallingStrategy创建出TreeUnmarshaller来并启动解析

③开始组码—————>TreeUnmarshaller的start方法

![1631698120_6141bcc8d42e7c52b7df7.png!small](https://image.3001.net/images/20210915/1631698120_6141bcc8d42e7c52b7df7.png!small)

④通过节点名获取Mapper中对应的Class

![1631704197_6141d485c04557ebe33b1.png!small?1631704197704](https://image.3001.net/images/20210915/1631704197_6141d485c04557ebe33b1.png!small?1631704197704)

⑤根据Class把它转化成对应的java对象—————>TreeUnmarshaller的convertAnother方法

![1631704238_6141d4aedb75acf308004.png!small?1631704238793](https://image.3001.net/images/20210915/1631704238_6141d4aedb75acf308004.png!small?1631704238793)

⑥如何查找对应的Converter———>ConverterLookup中的lookupConverterForType方法

⑦根据找到的Converter把Type转化成java对象————>TreeUnmarshaller的convert()

组码的过程，当Class对应的Converter为AbstractReflectionConverter时，根据获取的对象，继续读取子节点，并转化成对象对应的变量;获取class变量值的过程是一个循环过程，直到读取到最后一个节点推出循环，最终整个反序列化的过程也就结束了，对XML数据的解析过程也结束了。。。

#  **三、漏洞成因**

通过对XStream框架整体的分析不难发现，是程序在调用XStream中的fromXML()方法对XML数据进行反序列化的时候，通过绕过XStream的黑名单限制而已输入带有任意命令的xml格式数据，让反序列化产生了非预期对象，造成了任意命令执行的安全漏洞出现。

#  **四、漏洞POC链挖掘思考**

XStream反序列化漏洞屡见不鲜的原因：其实很大程度上来源于XStream的“特性”就是不是JavaBean类实现Serializable接口并重写readObject()方法。在JavaBean类没有实现的时候，XStream会调用默认的readOject()方法；而实现的时候，会调用重写的readObject方法。在未实现的时候最终结果会返回一个ReflectionConverter，并且只是处理我们自定义的未实现Serializable接口的JavaBean类时使用ReflectionConverter，这时候该Converter的原理是通过反射获取类对象并通过反射为其每个属性进行赋值

那么，也就是说归根结底，XStream反序列化漏洞的原因就是对重写readObject()方法调用的时候，黑名单控制不严格问题主要引起漏洞形成的。

那么，我们在分析源码的时候，就可以沿着这种方式再重新找到一条实现重写ReadObject()方法的XML返序列化调用链，再在XML数据中写入任意命令即可执行了。。。

## 五、CVE-2020-26259漏洞复现

使用IntelliJIDEA，创建一个maven项目，在pom.xml文件中，给新建的XStream项目中引入了XStream依赖

然后，将CVE-2020-26259漏洞任意文件删除的POC写入到XML字符串中，调用XStream反序列化函数进行反序列化后，观察现象：

![1631704963_6141d783ec551cc32e018.png!small?1631704964094](https://image.3001.net/images/20210915/1631704963_6141d783ec551cc32e018.png!small?1631704964094)

![1631705104_6141d81094f9fdb5a8a6b.png!small?1631705104928](https://image.3001.net/images/20210915/1631705104_6141d81094f9fdb5a8a6b.png!small?1631705104928)

执行代码后，对应的文件成功被删除！！（可以删除任意文件）

![1631705153_6141d84114be241829509.png!small?1631705153091](https://image.3001.net/images/20210915/1631705153_6141d84114be241829509.png!small?1631705153091)

CVE-2020-26259_SSRF现象：

###
poc：![1631705615_6141da0f6b149c5457446.png!small?1631705615476](https://image.3001.net/images/20210915/1631705615_6141da0f6b149c5457446.png!small?1631705615476)

本地利用nc监听8989端口，观察现象：

![1631705772_6141daac96ab3c47fff34.png!small?1631705772493](https://image.3001.net/images/20210915/1631705772_6141daac96ab3c47fff34.png!small?1631705772493)

![1631706361_6141dcf9659272e9fd8af.png!small?1631706361747](https://image.3001.net/images/20210915/1631706361_6141dcf9659272e9fd8af.png!small?1631706361747)

## 总结

终于，把XStream整个框架的分析完了。虽然过程很痛苦，及其乏味，但是俺胡汉三还是坚持过来了！！哈哈哈哈，各位大佬们如果发现文章中有什么表达错误的地方欢迎指教。互相交流，互相学习。

![](https://image.3001.net/images/20210916/1631800422_61434c66b93c001fa4798.jpg!small)

