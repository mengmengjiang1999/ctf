![](https://image.3001.net/images/20220113/1642064371_61dfe9f332692709ef32f.jpg!small)

## **前言**

反序列化漏洞作为java中最常见和最好用的漏洞之一，是检验一个安全研究员能力的核心技术。我们接下来的分享会围绕java反序列化漏洞展开，包括相关知识的准备、反序列化的原理、反序列化利用链等。

今天我们先讲关于java反射的知识，反射是java中一个非常重要的概念，学习java安全的人必须把反射的概念理解清楚。

>  **目录**
>
> 1\. Java本地调试和远程调试技巧
>
> 2\. Java反编译技巧
>
>  **3\. Java安全基础概念之反射与ClassLoader**
>
> 4\. 从冰蝎来看目前webshell的实现原理
>
> 5\. Java反序列化基础
>
> 6\. CommonCollections利用链分析介绍上
>
> 7\. CommonCollections利用链分析介绍下
>
> 8\. JNDI注入原理与fastjson漏洞实践
>
> 9\. Weblogic反序列化漏洞分析
>
> 10\. Java命令回显技术研究
>
> 11\. Java内存马技术研究
>
> 12\. RASP技术研究
>
> 13\. 基于CodeQL的自动化代码审计技术研究上
>
> 14\. 基于CodeQL的自动化代码审计技术研究下
>
> ……

##  **class对象**

java反射机制是指在java代码执行过程中，对于任意一个类，可以获取这个类的属性与方法；对于任意一个对象，可以获取、修改这个对象的属性值，调用对象的方法。这种动态获取信息和调用方法的技术就是java中的反射机制。

在了解具体反射机制之前，首先需要了解Class类（全限定名称是java.lang.Class）和class对象。class对象就是由Class类创建的对象，只是这个创建过程不是由用户主动创建的，而是由JVM自动实现的。JVM会为项目中每一个类（不论是JDK自带的类、第三方jar包的类、还是自己编写的类）创建一个class对象，用来保存与这个类相关的信息。class对象只与类有关，与对象无关。我们从一张图来看它们之间的关系。

![](https://image.3001.net/images/20220113/1642064448_61dfea403e892ffa81c9a.png!small)

图1. Student类、类对象、class对象之间的关系

从上面的图可以看出，每个类都有且仅有一个class对象。通过类和对象都能获取到类的class对象，获取到class对象有下面三种方式。

> 1.Student.class //通过类名.class的方式获取class对象
>
> 2.stu1.getClass() //通过类对象.getClass()的方式获取class对象
>
> 3.Class.forName("com.test.Student") //通过全限定名的方式获取class对象

这三种获取class对象的方式都要掌握，遇到不同的应用场景能熟练的使用某一种方式获取到类的class对象。java反射的所有操作都是基于class对象来完成的。

Java反射的主要作用是通过class对象来对类的属性和方法进行获取和调用，那么相比于传统的调用有什么区别呢？

![](https://image.3001.net/images/20220113/1642064494_61dfea6ee232dde9f63ce.png!small)

图2.传统方式和反射方式对比图

传统生成一个类对象和通过反射来生成类对象，从本质上来看最终创建的对象是一样的，但是创建的方法是完全不同的。通过new关键字来生成对象，调用对象方法是传统的方法；通过class对象来生成对象，调用方法是属于反射机制。看起来似乎反射的调用比传统的方式更加复杂，但是反射的主要作用之一就是在动态上面，我们调用的类名称和方法名称都是通过变量传入的，在某些复杂逻辑下，动态的类名和函数名是极为重要的。

另外，反射机制还有一个极为重要的特征就是可以调用类的私有方法（包括protected和private）。如下图所示，这种看似违背继承机制的特性却是反射里面极为重要的概念，也是后续很多java反序列化利用链依赖反射机制的重要原因。

![](https://image.3001.net/images/20220113/1642064519_61dfea8741063f48f1123.png!small)

图3.通过反射来操作私有的方法

到此，我们就先简单总结一下反射的优势:

1、反射是对动态类和方法的调用

2、反射可以调用和修改类的私有属性和方法

##  **Java反射**

Java反射机制一般有下面三种用途：字段获取和修改、方法获取和访问、构造函数获取和使用。

 **字段获取和修改**

我们可以通过下面的方法来进行字段获取：

getField(String name)| 根据字段名获取对应的字段，只能获取public类型的字段，可以获取父类的字段。  
---|---  
getFields()| 获取类所有的字段，只能获取public类型的字段，可以获取父类的字段。  
getDeclaredField(String name)|
根据字段名获取对应的字段，可以获取public、protected和private类型的字段，不能获取父类的字段。  
getDeclaredFields()| 获取类所有的字段，包括public、protected和private。不能获取父类的字段。  
  
Java的反射机制提供了获取属性的方式，同时支持对私有的属性进行获取。一种最典型的获取属性的方式如下图所示：

![](https://image.3001.net/images/20220113/1642064651_61dfeb0be29a29340c3f4.jpg!small)

图4. 通过反射获取字段值

上面是一个通过反射来获取字段值的典型过程，对于public类型的字段，可以使用getField进行获取，但是对于private类型的字段却要使用下面的方式获取：

![](https://image.3001.net/images/20220113/1642064686_61dfeb2e2e5c10371743a.jpg!small)

图5. 通过反射获取和修改私有的属性

如果字段是static修饰的，那么在获取字段和修改字段时，可以使用null代替具体的对象stu：

![](https://image.3001.net/images/20220113/1642064710_61dfeb46dfab07d6a8839.jpg!small)

图6. 获取和修改static修饰的字段

在进行私有属性获取时，有两个注意事项。第一，必须使用getDeclaredField(s)函数来获取。第二，在对字段进行操作之前，必须field.setAccessible(true);这个表示设置允许对字段进行操作。

对字段的操作一般分成获取和设置，基本操作如下:

field.get(Obj)| 获取Obj对象的field字段  
---|---  
field.set(Obj,field_value)| 设置Obj对象的field字段值为field_value  
field.get(null)| 获取static修饰的静态字段field的值  
field.set(null,field_value)| 设置static修饰的静态字段field的值为field_value  
  
从上面的过程中，我们可以通过反射来获取和修改对象的属性字段。但是如果仔细看上表的小伙伴就会发现，Java反射机制似乎没有提供获取父类私有字段的方法，那如何才能获取父类的私有属性呢？要获取父类的私有属性字段，需要首先获取父类的class对象，最简单的就是通过clazz.getSuperclass()来获取父类的class对象，如下图所示：

![](https://image.3001.net/images/20220113/1642064835_61dfebc3c9ef41e6a5337.jpg!small)

图7. 获取父类的私有属性字段

在获取类的属性字段时，有一个需要特殊注意的类型就是final修饰符。我们把name字段增加final修饰，然后通过反射的方式对name字段进行修改，相关代码如下图所示：

![](https://image.3001.net/images/20220113/1642064860_61dfebdc55e075527a279.jpg!small)

图8. 对final修饰符的字段进行反射修改

最后的两行代码，一个是通过反射获取到对象stu中保存的name字段的值，一个是通过sayHello方法调用来查看对象中保存的name值。我们会发现一个很奇怪的现象，这两个位置得到的name是不一样的，如下图所示：

![](https://image.3001.net/images/20220113/1642064893_61dfebfd0e224552432d3.jpg!small)

图9. 反射对final修饰符的字段进行了伪修改

当final修饰一个数据域时，意义是声明该数据域是最终的，不可修改的。使用传统的方式对final修饰符的字段进行修改，代码运行不会报错，但是实际上却是进行的伪修改，真正的字段值并没有被修改。那有什么办法可以修改final属性的值吗？

首先有很多文章说通过修改field.getClass().getDeclaredField("modifiers")来修改final标志位的值，然后再进行反射就可以修改final字段的方法是错误的。比如https://blog.csdn.net/weixin_39674190/article/details/114175329。大家可以自己去写代码验证。

final字段能否修改，有且取决于字段是直接赋值还是间接赋值（编译时赋值和运行时赋值的区别）。直接赋值是指在创建字段时就对字段进行赋值，并且值为JAVA的8种基础数据类型或者String类型，而且值不能是经过逻辑判断产生的，其他情况均为间接赋值。具体如下所示：

1）下面的直接赋值方式不可修改

![](https://image.3001.net/images/20220113/1642064983_61dfec57ad3f7c5675215.png!small)

2) 经过逻辑判断产生的变量赋值可以修改  
![](https://image.3001.net/images/20220113/1642065000_61dfec68782d88faf5795.png!small)3）new生成的对象赋值可以修改，如图10所示![](https://image.3001.net/images/20220113/1642065251_61dfed638b19d1b5142ce.png!small)4）通过构造函数进行赋值的final字段可以修改，如图11所示![](https://image.3001.net/images/20220113/1642065298_61dfed92812c612a147a7.png!small)

![](https://image.3001.net/images/20220113/1642065331_61dfedb3b770dad04cb5e.jpg!small)图10.
new生成的对象赋值给final字段可以修改

![](https://image.3001.net/images/20220113/1642065352_61dfedc82f0c36f641f64.jpg!small)

图11. 构造函数赋值的final字段可以修改

对于既有final又有static修饰的字段，不能直接通过反射的方式来修改变量执行，否则会报错，如图12所示：

![](https://image.3001.net/images/20220113/1642065376_61dfede03a7e5009d7d80.jpg!small)

图12. 反射修改final static修饰的字段报错

这时候可以通过反射修改final修饰符的值，然后就可以进行正常的修改了，主要增加的代码如下

![](https://image.3001.net/images/20220113/1642065412_61dfee04a4a3a8808dab8.png!small)

  
![](https://image.3001.net/images/20220113/1642065429_61dfee1545dbe54f1b623.jpg!small)

图13. 通过反射修改final static修饰的字段

 **方法获取和访问**

方法获取和访问的方式如下：

getMethod(String name, Class... parameterTypes)|
根据方法名和参数类型获取对应的方法，只能获取public类型的方法，可以获取父类的方法。  
---|---  
getMethods()| 获取类所有的方法，只能获取public类型的字段，可以获取父类的方法。  
getDeclaredMethod(String name, Class... parameterTypes)|
根据方法名获取对应的方法，可以获取public、protected和private类型的方法，不能获取父类的方法。  
getDeclaredMethods()| 获取类所有的方法，包括public、protected和private。不能获取父类的方法。  
  
获取方法的函数和获取字段的函数很相似，在使用上也基本一致。这里需要强调的是getMethod方法的第二个参数，代表的是想要获取方法的参数类型。第二个参数需要传入的是参数对应的class对象，多个参数以数组的形式传入。

要使用通过反射获取的方法，需要使用invoke函数。关于invoke方法的使用如下：

invoke(Object obj, Object[] args)| 执行通过反射获取的方法，obj代表要执行方法的对象，args代表方法的参数。  
---|---  
  
最简单的方法使用案例如下：

![](https://image.3001.net/images/20220113/1642065554_61dfee920480688bf0eb9.jpg!small)

图14. 通过反射来调用对象的方法

上面的是最简单的方法调用，如果调用的方法是私有的，并且有多个参数，就应该用下面的使用方式：

![](https://image.3001.net/images/20220113/1642065578_61dfeeaa3e9c29729e68a.jpg!small)

图15. 通过反射来调用私有的多参数方法

在调用私有多参数方法时，需要注意下面几个问题：

1） 私有方法执行需要使用method.setAccessible(true)来设置允许访问。

2） 使用getDeclaredMethod获取多个参数的方法，第二个参数为new
Class[]{}类型的数组，数组中每一个值对应参数的class对象。这是一种标准的传参方式，建议即使方法没有参数或者只有一个参数也按照这种方式传参。

3） 使用method.invoke方法对方法进行调用，传递的第二个参数表示实际调用时传递的参数值，类型是Object数组。

对于static类型的方法，与字段的使用方法相似，在执行方法时，同样可以把obj对象换成null，如下图所示：

![](https://image.3001.net/images/20220113/1642065610_61dfeeca31b4a68f501d4.jpg!small)

图16. 通过反射调用多参数的静态方法

获取父类的私有方法就不再赘述了，与获取父类的私有字段的方式一样。

 **构造函数获取和使用**

构造函数理论上也是一种方法，只是这是一种特殊的方法。我们很多情况下都需要通过反射获取构造函数，然后调用构造函数生成类的实例。可能某些小伙伴会问，生成类的实例不是直接new就可以了吗，为啥还要用反射这么复杂的调用方式来生成实例？答案是很多情况下，我们遇到的构造函数是private的或者是protected的，又或是我们本身想生成实例的类就是private的，这样我们就不能直接用new来生成实例了，只能通过反射来生成。

我们主要通过下面的方法来获取构造函数：

getConstructor(Class... parameterTypes)|
根据参数类型获取对应的构造函数，只能获取public类型的构造函数，不能获取父类的构造函数。  
---|---  
getConstructors()| 获取类所有的构造函数，只能获取public类型的字段，不能获取父类的构造函数。  
getDeclaredConstructor (Class... parameterTypes)|
根据参数类型获取对应的构造函数，可以获取public、protected和private类型的构造函数，不能获取父类的构造函数。  
getDeclaredConstructors()| 获取类所有的构造函数，包括public、protected和private。不能获取父类的构造函数。  
  
在获取到构造函数之后，需要通过newInstance函数来生成类对象。关于newInstance的使用如下所示：

newInstance(Object ... initargs)​

newInstance(Object ... initargs)|
newInstance函数接受可变的参数个数，构造函数实际有几个传输，这里就传递几个参数值。newInstance返回的数据类型是Object。  
---|---  
  
一个最简单的通过反射来获取构造函数并通过构造函数生成对象的代码如下：

![](https://image.3001.net/images/20220113/1642065911_61dfeff76ec22df5e6879.jpg!small)

图17. 通过反射获取构造函数生成对象

需要注意的是，通过newInstance生成的对象永远都是Object类型，要实际调用对象的某个方法，需要进行向下强制类型转换。

对于私有的多参数构造函数，我们应该采用下面的方法来生成类对象，如下图所示：

![](https://image.3001.net/images/20220113/1642065938_61dff012c063e440d565b.jpg!small)

图18. 通过反射获取私有的多参数构造函数生成对象

由于getDeclaredConstructor函数和newInstance函数接受的是可变长度的参数，每一个参数对应的就是构造函数中的参数。这里需要和获取普通方法时传递数组参数进行区别。

##  **Java反射应用**

Java反射作为Java安全学习过程中最重要的概念，后面很多关于Java漏洞编写poc或者exp都要用到Java反射。但是因为我们现在还没有说到反序列化，就暂时不说反射在反序列化利用链中的作用。这里只说反射的一个简单应用，通过反射来隐藏webshell关键字，绕过WAF检测。

最简单的一个java执行命令的方式如下

> Runtime.getRuntime().exec("open /System/Applications/Calculator.app");

很多WAF在检测webshell的时候会基于关键字Runtime、getRuntime、exec这三个关键字来进行规则匹配。下面我们就通过反射来隐藏着三个关键字，如下图所示。我们把着三个关键字都写成了字符串变量，稍微做一下字符串拼接也就没有这三个关键字了。（这里为了方便大家阅读就不替换了）

![](https://image.3001.net/images/20220113/1642066005_61dff055946ae1fdb601f.jpg!small)

图19. 通过反射的方式实现java命令执行函数，隐藏关键字

可以分成几步来看整个实现过程：

1）
由于Runtime类的getRuntime方法属于静态方法，所以我们这里不需要生成一个Runtime对象，直接传递null就可以调用getRuntime方法。

2） getRuntime()方法会返回一个Runtime类的对象，但是由于我们是通过反射的方式实现的，所以要进行一次强制类型转换。

3）
继续通过反射获取Runtime类的exec方法，传递一个String类型的参数，这个方法不是静态方法了，所以必须传入一个Runtime对象，也就是上一步返回的对象。

4） 隐藏关键字，执行命令。

通过相同的办法，可以隐藏其他冰蝎、哥斯拉等webshell的关键字，如果WAF不拦截反射相关的函数，那就可以通过反射来进行任意操作。

![](https://image.3001.net/images/20220113/1642066023_61dff06742916a0fceeaf.jpg!small)

[原文链接](https://mp.weixin.qq.com/s?__biz=MzkzNjMxNDM0Mg==&mid=2247483830&idx=1&sn=39c08c61cbab36ace4ac691e0756948b&chksm=c2a1d53ff5d65c29f9b8310c324c67568fe27e61720baffff8af19ef9cb94f5096d73df0c69f&token=1134049837&lang=zh_CN#rd)

