Java NativeInterface (JNI)
是一种使用java语言和原生C/C++语言相互调用、混合编程的方法，它允许在Java虚拟机（VM）内运行的Java代码与应用其他编程语言（如C、C++和汇编）编写的应用程序和库进行互操作，它支持从动态链接库中加载代码,
并能使用C/C++的高效的特性。

如果要基本了解JNI的功能与使用，可以阅读Java Native
Interface文档[https://docs.oracle.com/javase/7/docs/technotes/guides/jni/spec/jniTOC.html](https://docs.oracle.com/javase/7/docs/technotes/guides/jni/spec/jniTOC.html)

同时，本文将继续介绍一些在可能在刚开始会注意不到的使用细节。

# JNI中的局部引用与全局引用

局部引用(localreference)与全局引用(globalreference)是JNI中的重要概念，用来实现对JNI对象类型的引用。
JNI函数返回的所有Java对象都是局部引用，且JNI允许从局部引用创建全局引用。局部引用在本地方法的调用期间有效，在方法返回后自动释放；全局引用在其被显式释放前持续有效。

因此，在实际使用JNI的过程中要注意以下事项：

1\. 全局引用的创建NewGlobalRef(JNIEnv*
,jobject)必须伴随对它的删除DeleteGlobalRef(JNIEnv*,jobject)，否则会造成内存泄漏，并可能导致OutOfMemoryException

2\.
虽然局部引用会在方法返回时被全部自动释放，但是它会阻止gc对垃圾对象的回收，方法对java对象的访问会创建大量局部引用，即使对象不会再被使用，VM仍然需要占用空间进行对引用的跟踪，可能会造成系统内存不足。

在每一次的本地方法调用过程中VM创建局部引用表实现将本地引用映射到java对象，且JNI局部引用表没有检测与折叠重复引用的功能。在DalivkVM中，JNI局部引用表最大数量是512个，循环或频繁的字符串操作很容易就会导致局部引用表溢出。这些情况下，就需要使用DeleteLocalRef(JNIEnv*,jobject)手动删除局部引用。

对局部引用的操作还有以下接口：

EnsureLocalCapacity(JNIEnv* , jint)

确定在当前线程中是否至少可以创建给定数量的局部引用。调试过程中的命令行参数-verbose：jni也可以显示创建过多局部引用的警告信息。

PushLocalFrame(JNIEnv* ,jint)

创建新的局部引用框架，确认是否可以创建至少给定数量的局部引用。

PopLocalFrame(JNIEnv*,jobject )

释放当前所有局部引用，返回指定的局部引用。

NewLocalRef(JNIEnv *,jobject ref)

创建新的局部引用，引用指定对象。

3\. 由于局部引用会在调用结束后释放，因此不能用全局变量保存局部引用，否则会由于访问野指针造成崩溃。

除局部变引用与全局引用外，JNI还有弱全局引用(Weak Global
References)。它是可以被gc清理的全局引用，在gc运行时可能会将其引用的底层对象释放，此时该引用被置空。且IsSameObject虽然可用于确定弱全局引用是否引用已释放的对象，但它不会阻止此对象被释放。因此对于弱全局引用的调用是不安全的。当我们的本地代码不再需要一个弱全局引用时，也应该调用DeleteWeakGlobalRef来释放它，如果不手动调用这个函数来释放所指向的对象，JVM仍会回收弱引用所指向的对象，但弱引用本身在引用表中所占的内存永远也不会被回收。

# JNI中的异常处理

在进行本地方法调用实现中，应当对每一个JNI函数调用的返回进行检查、处理、清除异常后再做其它 JNI 函数调用，否则会产生不可预知的结果。
一旦发生异常，立即返回，让调用者处理这个异常。或调用ExceptionClear()
清除异常，然后执行自己的异常处理代码。JNI接口ExceptionCheck(JNIEnv*)可以判断是否发生异常，而且不会产生新的局部引用。接口ExceptionOccurred(JNIEnv*)可以创建局部引用返回异常对象。

值得注意的是，在有异常发生时，本地代码必须先处理异常才能执行其他的JNI调用。仅有指定接口可以在有异常挂起的情况下被调用，用于处理异常与释放资源：

    
    
    ExceptionOccurred()
    
    
    ExceptionDescribe()
    
    
    ExceptionClear()
    
    
    ExceptionCheck()
    
    
    ReleaseStringChars()
    
    
    ReleaseStringUTFChars()
    
    
    ReleaseStringCritical()
    
    
    Release<Type>ArrayElements()
    
    
    ReleasePrimitiveArrayCritical()
    
    
    DeleteLocalRef()
    
    
    DeleteGlobalRef()
    
    
    DeleteWeakGlobalRef()
    
    
    MonitorExit()
    
    
    PushLocalFrame()
    
    
    PopLocalFrame()

JNI在VM运行字节码与本地平台特定代码之间建立了桥梁，在复用C/C++代码，增加Java访问操作系统中一些底层的特性，提高代码运行效率上有较大的作用，但是这种本地代码与java代码间的通信与数据交换也会造成虚拟机崩溃或内存泄露等严重后果，因此深刻学习理解JNI的特性在开发过程中是非常重要的。

