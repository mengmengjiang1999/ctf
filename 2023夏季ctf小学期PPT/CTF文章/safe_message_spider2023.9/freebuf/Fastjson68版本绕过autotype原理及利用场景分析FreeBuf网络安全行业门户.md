## 引言

 **fastjson
68版本前一阵子有些闹得沸沸扬扬的，我这边也一直忙着写字节码扫描器没太用心关注，今天看到fastjson代码已经跟进到71版本了，所以对68和69版本的代码做了一下比对，看了一下修复代码，这里对68版本fastjson的RCE漏洞做一下原理以及利用场景的分析。**

注：其实最初在5月10号的时候我这边就已经看到了68版本的一种利用方式，基于Throwable子类的利用方式，不过这种方式只是68版本利用方式中的一种。

##  原理

fastjson的漏洞跟进的比较多的情况下，可以明白一个基本的套路就是，不管绕过怎么样的风骚，修复代码大部分都在ParserConfig类的checkAutoType里面，所以就话不多说，把68版本和69版本的ParserConfig类做个比较，看到改动还是很少的。

![](https://image.3001.net/images/20200616/1592295012_5ee87e64a20e1.jpg!small)

基本上一看可以看出是和expectClass有关，所以在函数的上上下下看了一下这个变量，可以归并一下发现的信息：

1、expectClass不为代码中的那些类的时候可以将expectClassFlag设置为true

![](https://image.3001.net/images/20200616/1592295020_5ee87e6c49ed8.jpg!small)

2、当expectClassFlag为true的时候，即使fastjson的autoype为false我们也能生成期望类的实例。![](https://image.3001.net/images/20200616/1592295029_5ee87e756e607.jpg!small)

OK但从上诉两点，我们就可以看到借由expectClass我们是可以绕过fastjson的autotype安全限制的，这个安全通告相符合，代表我们走在正确的方向上。

但是在阅读checkAutoType函数中expectClass的代码的时候，也发现了其中一些会限制Gadget的点，

1、黑名单检测逻辑是放在loadClass之前的，也就是说我们的Gadget将依旧受到黑名单的限制。（代码太长，我就不贴了）

2、Gadget必须实现了expectClass接口（或是expectClass的子类），才能成功生成Gadget的实例。![](https://image.3001.net/images/20200616/1592295034_5ee87e7a11a61.jpg!small)

上面便是阅读代码得到的关键性信息了，接下来就要思考一下expectClass的问题了，第一个问题，expectClass是从哪里来的，看一下checkAutoType函数，

    
    
    public Class<?> checkAutoType(String typeName, Class<?> expectClass, int features)

很清晰，expectClass就是直接传给checkAutoType函数的，那么接下来我们需要去寻找，究竟哪些地方会给checkAutoType函数传expectClass，全局搜索一下，可以看到场景非常少，

> 1、JavaBeanDeserializer类的deserialze函数
>
> 2、ThrowableDeserializer类的deserialze函数

关于第二种场景，我这边5月10号就到了别的大佬的分析，有兴趣大家可以[去看一下](https://mp.weixin.qq.com/s/EXnXCy5NoGIgpFjRGfL3wQ)，我就不再赘述，这里着重讲第一种。（当然其实就原理而言完全是一回事。）

DefaultJSONParser调用parseObject，用@type生成的clazz实例会紧接着传入JavaBeanDeserializer类的deserialze方法的type参数中，并继续解析json数据，如果json数据中还有@type，则把@type的值作为typeName，type参数作为expectClass传入checkAutoType函数中，

![](https://image.3001.net/images/20200616/1592295292_5ee87f7c0d4a2.jpg!small)

![](https://image.3001.net/images/20200616/1592295040_5ee87e805503d.jpg!small)

那根据我们刚刚分析代码得出的结论，如果typeName刚好为expectClass的子类，那么接下来就能生成typename的对象，从而达成绕过autotype的目的。

但是，这里一定要注意一个特别重要的问题，由于默认autotype是关着的，那么我们又怎么样去用@type来生成传给deserialze的clazz呢，下面我就先给出目前fastjson在autotype关闭的情况下能生成的clazz的范围：

**1、cache mapping**
:48版本以前fastjson允许用户通过{"@type":"java.lang.Class","val":"com.evilClass"}的形式向mapping里面添加恶意类，这样不需要依赖autotype可以直接从cahce的mapping里获取clazz，但是48版本已经修复该问题。当然cache
mapping在刚fastjson启动的时候就已经放了不少clazz，加载的时候不受autotype限制。![](https://image.3001.net/images/20200616/1592295046_5ee87e86afae8.jpg!small)

**2、白名单** ：不赘述，白名单的目的就是不受autotype的限制嘛。不过新版本白名单已经被加密，需要爆破一下。

**3、默认deserializers的buckets（在PaserConfig类的initDeserializers函数中初始化）**
：可以把fastjson理解为一个编译器，它在进行初始化的时候也需要加载一些基础类型的对象，这些对象为了组件的正常工作是必须的。![](https://image.3001.net/images/20200616/1592295052_5ee87e8cacdf5.jpg!small)

所以我们需要的clazz就是要从上诉列举的三种情况里面寻找到，与此同时保证它不在黑名单里面。

OK，全部的分析已经到位，我们来汇总一下，看看poc究竟要怎么写：

1、首先要用@type来生成一个clazz（不受autotype影响的）。从而把这个clazz传入deserialze函数的exceptClass中，要保证clazz不能为以下类。（这个是68版本的，69版本又添加了三个。）![](https://image.3001.net/images/20200616/1592295058_5ee87e921add9.jpg!small)

2、紧跟在生成在第一个@type后面，再跟一个@type，它的value不能是黑名单里面的类，而且必须是第一个clazz的子类。

之后便能生成一个不受autotype影响的clazz，以达到利用效果。

关于漏洞的复现，为了方便起见，我就直接去拿了69版本被拉黑而68版本没被拉黑的AutoCloseable接口来构造poc了。

因为想要利用成功必须保证第二个clazz实现AutoCloseable的接口，恶意类难找，我们只聊原理，我就随便写了一个利用类。

    
    
    package defaultpack;
    import com.alibaba.fastjson.JSON;
    import com.sun.rowset.JdbcRowSetImpl;
    import org.h2.tools.SimpleResultSet;
    import java.lang.reflect.Field;
    public class Person implements AutoCloseable{
        private String name;
        private int age;
        private String gender;
        public Person() {
            System.out.println("no-arg construct invoked!!!");
        }
        public Person(String name, int age, String gender) {
            this.name = name;
            this.age = age;
            this.gender = gender;
        }
        public String getName() {
            return name;
        }
        public void setName(String name) {
            this.name = name;
        }
        public int getAge() {
            System.out.println("getAge invoked!!!");
            return age;
        }
        public void setAge(int age) {
            this.age = age;
            System.out.println("setAge invoked!!!");
        }
        public String getGender() {
            return gender;
        }
        public void setGender(String gender) {
            this.gender = gender;
        }
        @Override
        public void close() throws Exception {
        }
    }

利用的poc如下，

    
    
    String payload = "{\"@type\":\"java.lang.AutoCloseable\",\"@type\":\"defaultpack.Person\",\"age\":\"13\"}";
    JSON.parseObject(payload);

成功利用的截图如下，可以看到在68版本autype默认为关的情况下，依旧成功调用了Person类的setAGe方法。：![](https://image.3001.net/images/20200616/1592295066_5ee87e9ab35d2.jpg!small)

##  利用场景分析

可以从上面的分析看出，虽然在原理层面上，的确存在着代码执行的风险，且绕过了autotype机制，但是这个利用受到了多方面限制：

> 1、黑名单限制
>
> 2、漏洞利用类必须拥有一个在autotype关着的情况下可以生成实例的父类（目前在68版本我已知的是Throwable和AutoCloseable）。

所以因为以上两点的限制，就可以发现利用是非常局限的，当然也不排除黑客大佬们思路广阔而笔者才疏学浅的可能性，因此我也仅在这里给出自己的看法。

 ***本文作者：平安银行应用安全团队@Glassy，转载请注明来自FreeBuf.COM**

