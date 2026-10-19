Java Native Interface(JNI)
是一种使用java语言和原生C/C++语言相互调用、混合编程的方法，它允许在Java虚拟机（VM）内运行的Java代码与应用其他编程语言（如C、C++和汇编）编写的应用程序和库进行互操作，它支持从动态链接库中加载代码,
并能使用C/C++的高效的特性。

如果要基本了解JNI的功能与使用，可以阅读Java Native
Interface文档<https://docs.oracle.com/javase/7/docs/technotes/guides/jni/spec/jniTOC.html>

同时，本文将介绍一些在可能在刚开始会注意不到的使用细节。

# FindClass找不到类的问题

JNI类名由包名开始, 由'/'分隔，例如

”java **/** lang **/** String”

如果要查找的是一个数组类, 类名应为签名形式，所以一个一维String数组的类定义为

“ **[** Ljava **/** lang **/** String **;** ”

可以参照<https://docs.oracle.com/javase/7/docs/technotes/guides/jni/spec/functions.html#wp9502>

但是目前即使全都传入签名形式的类名，FindClass依然会找到对应的类。原因是历史遗留问题，参考<https://bugs.openjdk.java.net/browse/JDK-6411605>

为了保证正确性，可以在运行class文件时，加参数-Xcheck:jni可以校验类名构造是否规范。

# javah生成的函数名不正确的问题

在函数重载和内部类类型作为某个重载函数的参数时，会触发javah生成的函数名不正确的问题，javah会按照JNI的名称解析规则生成JNI函数名，但是JVM在运行时却不会按照这个名字查找函数，因此会出现运行时找不到函数的情况。

参考<https://bugs.openjdk.java.net/browse/JDK-8145897>

package p **;**

class A **{**

static class B **{}**

static class C **{**

native static long Foo **(** B bar **);**

**}**

**}**

运行javah **-** jni -o jni_libA.h **-** classpath **./** p.A

预期的输出是：

//Method: Foo

//Signature: (Lp/A$B;)J

JNIEXPORT jlong JNICALLJava_p_A_00024C_Foo__Lp_A_00024B_2

但实际会输出：

//Method: Foo

//Signature: (Lp/A/B;)J

JNIEXPORT jlong JNICALLJava_p_A_00024C_Foo__Lp_A_B_2

内部类B的’$’被忽略。

可选的解决方法有两种：

1\. 不把有内部类作为参数的重载函数写入本地方法

2\. 在生成方法后手动添加’$’(‘00024’)

# JNI中的异常机制

在有异常等待处理时不能调用大多数的JNI方法。要通过函数ExceptionCheck或ExceptionOccurred的返回值预期到有异常并返回，或处理并清除异常。

如果要获得异常的描述，需要找到Throwable类，然后调用它的getMessage
"()Ljava/lang/String;"方法，用GetStringUTFChars来获取内容。

很多JNI方法会抛出异常，但有些异常不会被抛出，需要在应当抛出异常的地方添加条件判断，用ThrowNew构造异常，最常见的是java **.** lang
**.** ArithmeticException与 Java **.** lang **.** NullPointerException

# JNI中原生数组的取值与赋值

如果想对数组进行写入或读出，Get<Type>ArrayElements和GetStringChars是非常有用的方式。

Get<PrimitiveType>ArrayElements系列函数允许返回一个指向实际元素的指针，或者分配一些内存来拷贝数据。
返回的原始数据的指针在调用释放方法前是保证一直有效的，而且必须手动释放每个获取的数组。同时可以通过传一个非空指针作为isCopy的参数来决定是否拷贝数据。

jbyte ***** data **=** env **- >**GetByteArrayElements **(** array **,**
**NULL** **);**

**if** **(** data **!=** **NULL** **)** **{**

memcpy **(** buffer **,** data **,** len **);**

env **- >**ReleaseByteArrayElements **(** array **,** data **,** JNI_ABORT
**);**

**}**

上面的代码是一个简单的举例，获取了数组，然后拷贝了len长度的byte，最后释放掉数组。

还有一个更简单实现同样功能的方式是

env **- >**GetByteArrayRegion **(** array **,** 0 **,** len **,** buffer
**);**

这种方式有几个好处：

1\. 只需要一个JNI调用，减少开销.

2\. 不需要对原始数据进行限制或者额外的拷贝数据

3\. 减少在某些出错后忘记释放的风险

4\. 会在越界时抛出异常

类似的，Set<Type>ArrayRegion系列方法是将数组中的元素赋值，
GetStringRegion或者GetStringUTFRegion是获得String中的字符。

通付盾SDK保护系统应用输入为aar包，通过分析aar结构，将待保护的class文件转换为AST（抽象语法树），对AST进行同态翻译，将其转换为对应的本地代码。本地化的转换规则与AST节点数目一一对应。由于字节码是托管代码，运行于VM中（java代码运行于JVM，安卓字节码运行在Dalvik），对于操作VM内存模型，以及涉及VM特性的行为，如创建对象，抛出异常等操作，本地代码无法表达对应的语义。对于带有这样语义的AST节点，本地代码的翻译遵循JNI调用规范，在确保本地化翻译的正确性的同时兼顾了兼容性。  

