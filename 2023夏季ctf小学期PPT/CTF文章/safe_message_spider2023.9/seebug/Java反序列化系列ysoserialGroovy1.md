**作者：天融信阿尔法实验室**  
**原文链接：<https://mp.weixin.qq.com/s/FdZ9nVjyLGV7eEbYtcm4sg>**

## ysoserial简介

ysoserial是一款在Github开源的知名java 反序列化利用工具，里面集合了各种java反序列化payload；
由于其中部分payload使用到的低版本JDK中的类，所以建议自己私下分析学习时使用低版本JDK JDK版本建议在1.7u21以下。

此篇文章为java反序列化系列文章的第一篇Groovy1
原理分析，后续会以ysoserial这款工具为中心，挨个的去分析其中的反序列化payload和gadget，讲完该工具后会继续对工具中没有的java
反序列化漏洞进行讲解，例如 FastJson
JackSon，WebLogic等等，并将这些漏洞的exp加入到ysoserial中然后共享和大家一起学习交流。

源码下载地址 <https://codeload.github.com/frohoff/ysoserial/zip/master>  
jar包下载地址
<https://jitpack.io/com/github/frohoff/ysoserial/master-30099844c6-1/ysoserial-master-30099844c6-1.jar>

## 源码深度解析

我们首先看一下该payload的整个源码

![](https://images.seebug.org/content/images/2020/04/180898e1-29e5-4c43-9d92-7aea52f376b1.png-w331s)

代码量其实很少，但是调用了一些别的类中的方法，看起来可能不是太直观，我将调用方法中所做的操作都写到一个类的main方法中这样看起来应该会更好理解一些。

先写一个简化版的可以执行代码的Demo

![](https://images.seebug.org/content/images/2020/04/a87f886b-4e59-4edf-8b9d-c40c930ad5b6.png-w331s)

直接运行的话会执行我们预先设定好的命令，调用计算器

![](https://images.seebug.org/content/images/2020/04/1a814d88-d9f3-4535-819a-8a1ba768d51a.png-w331s)

但是这短短几行代码里我们并没有调用Runtime对象的exec方法亦或着ProcessBuilder对象的star方法来执行命令，我们仅仅调用了一个Map对象的entrySet()方法，怎么就可以执行命令了呢？

对java有些许了解的同学应该熟悉Map.Entry是Map里面的一个接口，主要用途是来表示Map对象中的一个映射项也就是一个
并提供了一下五个方法,通常我们会使用`map.entrySet().iterator()`，方法得到一个Iterator对象从而对Map中的Entry对象进行遍历，那为何一个获取遍历对象的操作会导致代码执行呢？这里就涉及到这个Map对象究竟是哪一个实现了Map接口的类来实例化的。

![](https://images.seebug.org/content/images/2020/04/30f7aee9-f538-4d43-a9a7-9be962ba061d.png-w331s)

首先我们先来看看这个map变量里面保存的是什么

![](https://images.seebug.org/content/images/2020/04/3cddb30e-bcb5-4a2b-8a3d-31cce9c5fab3.png-w331s)

居然是一个代理对象，这里就要涉及到java的一个知识点，就是所谓的动态代理。动态代理其实不难理解，可以写个简单的例子,以下是这个例子的代码。

![](https://images.seebug.org/content/images/2020/04/45a1bc3f-d01e-4e9b-98f6-62157a54c72b.png-w331s)

我们可以看到我们写了一个Son类继承了Father接口，然后在Test3类中的main方法中被实例化，接下来我们通过Proxy的`newProxyInstance`方法生成了一个Son对象的代理，我们传递了三个参数进去，Son类的类加载器和实现的接口，这里注意被代理的对像是一定要实现至少一个接口的，因为实例化的代理类本身是继承了Proxy类，所以只能通过实现被代理类接口的形式来实例化。最后我们通过匿名内部类的形式传入了一个`InvocationHandler`对象，`InvocationHandler`是一个接口，该接口中只有一个方法就是invoke方法，所以我们一定要重写该方法。

然后我们看执行结果

![](https://images.seebug.org/content/images/2020/04/b8d9d62e-616c-4f76-9656-0d3232464c4e.png-w331s)

可以看到，我们调用Son对象本身和Son的代理对象所执行的结果是不同的，因为代理对象在执行被代理对象的任意方法时，会首先执行我们之前重写的`InvocationHandler`的invoke方法。同时会传入三个参数，第一个参数是代理对象本身，第二个参数是你要执行的方法的方法名，第三个参数是你要执行的该方法时要传递的参数。关键点在于什么？在于无论你调用代理对象的那一个方法，都一定要先执行这个Invoke方法。

然后返回到我们之前的payload中我们可以看到我们使用`Proxy.newProxyInstance`方法生成了一个代理对象，然后将其强转成了一个Map对象然后调用了entrySet方法。

![](https://images.seebug.org/content/images/2020/04/36953a8c-8b8a-4077-a4ea-a4584649899c.png-w331s)

接下来我们先记住我们payload所用到的两个类也就是所谓的gadget

![](https://images.seebug.org/content/images/2020/04/1ec44122-8526-4ad0-b5b3-4de8b8e69bda.png-w331s)

是位于`org.codehaus.groovy.runtim`e包下的`ConvertedClosure`和`MethodClosure`。

接下来我们就来一步一步的调试分析

![](https://images.seebug.org/content/images/2020/04/d3e2af1a-c323-445a-bf58-5d9412de4371.png-w331s)

首先我们生成一个MethodClosure对象并将我们要执行的命令和和一个值为“execute”的字符串传递进去我们跟进

![](https://images.seebug.org/content/images/2020/04/58a9d8aa-2dd5-49dd-84d8-56b4f4d287c9.png-w331s)

可以看到我们将要执行的命令传给了MethodClosure的父类来处理，将“execute”赋值给了MethodClosure.method属性。然后紧接着跟到Closure的构造方法中看到命令被赋值给了`Closure.owner`和`Closure.delegate`属性，之所以讲这些赋值过程是因为后面都会用得到。

![](https://images.seebug.org/content/images/2020/04/aaeeb0a4-e0ed-4fe9-812b-6a34834ed652.png-w331s)

接下来payload中又实例化了另一个对象并将刚才实例化的`MethodClosure`对象和一个字符串常量“entrySet”传入，我们童颜继续跟进。

![](https://images.seebug.org/content/images/2020/04/b56ae539-9b67-4516-8082-bc6f0b88b6c5.png-w331s)

字符串常量被赋值给`ConvertedClosure.methodName`属性

![](https://images.seebug.org/content/images/2020/04/dc256449-bb33-499b-a106-9fcc8d9e981a.png-w331s)

`MethodClosure`对象赋值给父类的的`ConversionHandler.delegate`属性。

![](https://images.seebug.org/content/images/2020/04/f09fbed3-00e6-43f3-8552-60d504ac53d7.png-w331s)

接下这两步就是生成一个Class类型的Arry数组因为`Proxy.newProxyInstance`方法第二个参数是动态代理类要实现的接口要以数组的形式传入。所以我们生成了一个Class数组并在其中存入我要实现的接口也就是Map.calss

![](https://images.seebug.org/content/images/2020/04/f70acc09-c442-4c68-bb30-891a90dac830.png-w331s)

接下来就是生成动态代理对象的过程了，这个在前面已经介绍过了，`Proxy.newProxyInstance`方法传递的第二个参数是代理类所要实现的接口，里面只有一个Map.class所以生成的代理对象是实现了Map接口里所有方法的，所以才可以将其强转成Map类型并调用entrySet方法。

![](https://images.seebug.org/content/images/2020/04/8e64aaec-39bd-4466-8ff2-6ec99c3b9813.png-w331s)

之前我们也说了动态代理的一大特点就是不论你调用代理对象的那一个方法其实执行的都是我们创建代理对象时所传入的`InvocationHandler`对象中我们所重写的Invoke方法。这里传入的`InvocationHandler`对象就是我们之前实例化的`ConvertedClosure`我们看一下该类的继承关系

![](https://images.seebug.org/content/images/2020/04/b81219a7-5e9b-40c6-b6c4-8a07da676f22.png-w331s)

可以看到`ConvertedClosure`类的继承关系中其父类`ConversionHandler`实现了`InvocationHandler`并重写了Invoke方法，所以我们由此可知当我么调用代理对象`map.entrySet`方法时实际上执行的`是ConversionHandler.Invoke`方法。我们跟进方法继续分析。

![](https://images.seebug.org/content/images/2020/04/49f9e844-8bc4-4db6-ab2a-ba1afe34e37b.png-w331s)

紧接着由调用了invokeCustom方法，该方法在ConversionHandler中是一个抽象方法，所以调用的是其子类重写的`ConvertedClosure.invokeCustom方`法。

![](https://images.seebug.org/content/images/2020/04/f30b7241-b1d4-4057-bc48-b4c8fa7a1558.png-w331s)

之前我们创建ConvertedClosure对象时为methodName属性赋了值“entrySet”此时我们调用的是代理对象的entrySet方法，自然传递进来method的值也是“entrySet”符合判断。

接下来的getDelegate()是其父类的方法也就是`ConversionHandler.getDelegate()`

![](https://images.seebug.org/content/images/2020/04/cd1f7d8a-74e9-42fc-a639-2aa7d4c86a68.png-w331s)

返回一个MethodClosure对象也就是并将其强转成Closure，然后调用`Closure.call()`方法

![](https://images.seebug.org/content/images/2020/04/4f263498-f4a2-425e-a2a5-426a0d00f9a2.png-w331s)

紧接着调用Closure的父类`GroovyObjectSupport.getMetaClass()`方法返回一个`MetaClassImpl`对象并调用`MetaClassImpl.invokeMethod()`方法

步入跟进该方法

    
    
    MetaMethod method = null;
    ......
       if (method==null) {
                method = getMethodWithCaching(sender, methodName, arguments, isCallToSuper);
            }
    ......
        final boolean isClosure = object instanceof Closure;
            if (isClosure) {
                final Closure closure = (Closure) object;
    
                final Object owner = closure.getOwner();
    
                if (CLOSURE_CALL_METHOD.equals(methodName) || CLOSURE_DO_CALL_METHOD.equals(methodName)) {
                    final Class objectClass = object.getClass();
                    if (objectClass == MethodClosure.class) {
                        final MethodClosure mc = (MethodClosure) object;
                        methodName = mc.getMethod();
                        final Class ownerClass = owner instanceof Class ? (Class) owner : owner.getClass();
                        final MetaClass ownerMetaClass = registry.getMetaClass(ownerClass);
                        return ownerMetaClass.invokeMethod(ownerClass, owner, methodName, arguments, false, false);

该方法代码过多先截取关键代码，首先创建一个Method类型的变量并为其赋值，然后我们通过判断传入的Object是否是Closure的子类，由截图可以看出Object里存储的是一个MethodClosure对象，所以判断的结果是true
接下来就走第一条判断成功执行的代码。

![](https://images.seebug.org/content/images/2020/04/a620b3c9-5034-4b2f-a457-c5b8c98a65d2.png-w331s)

接下来执行的就是将Object强转为Closure类型，接下来取出我们一开始我们在创建MethodClosure对象时存入的要执行的命令。

![](https://images.seebug.org/content/images/2020/04/f9532922-2408-4775-9b03-c3d732e29864.png-w331s)

接下来就一路执行到`return ownerMetaClass.invokeMethod()`

![](https://images.seebug.org/content/images/2020/04/48238615-9db5-4667-88f0-e92c8584809e.png-w331s)

我们看到这个ownerMetaClass其实还是一个MetaClassImpl对象也就是说这里其实是一个递归调用。

![](https://images.seebug.org/content/images/2020/04/05910332-4333-467c-bfb1-ddaf2a63643e.png-w331s)

以下是递归调用的执行路径可以看到在`if
(isClosure)`这里判断失败了，所以不再执行刚才的代码改为执行`method.doMethodInvoke()`

    
    
    MetaMethod method = null;
    ......
    if (method == null)
         method = tryListParamMetaMethod(sender, methodName, isCallToSuper, arguments);
    ......
    final boolean isClosure = object instanceof Closure;
    if (isClosure) {
      ......
    }
    if (method != null) {
          return method.doMethodInvoke(object, arguments);
       } 
    ......

我们看到method变量里存储的是一个叫dgm的对象

![](https://images.seebug.org/content/images/2020/04/5ac6701f-dfe0-4b44-a088-9f1477806fed.png-w331s)

以下是传入`method.doMethodInvoke()` 的两个参数里面所存储的值

![](https://images.seebug.org/content/images/2020/04/17a11d53-7f8a-44f8-8315-297d3ffd423a.png-w331s)

![](https://images.seebug.org/content/images/2020/04/6bb0f40c-f2c0-4329-be9d-47bf5565c9d6.png-w331s)

我们要执行的命令被传进了`ProcessGroovyMethods.execute((String)var1)`方法中，继续跟进。

![](https://images.seebug.org/content/images/2020/04/face1282-5aea-416d-81fc-d9c8351d8313.png-w331s)

至此通过调用`Map.entrySet()`方法就能导致代码执行的原理水落石出。

![](https://images.seebug.org/content/images/2020/04/6af68db8-0433-48c0-a289-2b6d350085d8.png-w331s)

以上就是ysoserial的payload中的Groovy的gadget介绍。接下来要讲的就是反序列化漏洞中的反序列化如何配和Groovy1的gadget来远程代码执行的。

我们来看ysoserial Groovy1所执行的全部代码。我们可以看到在第34行代码以前，执行的代码和我们之前看到的简化版的代码执行Demo是一样的。

![](https://images.seebug.org/content/images/2020/04/6b3da9c6-960d-4432-ba28-cbec0eb5ccfb.png-w331s)

我们看到我们通过反射先是拿到了`AnnotationInvocationHandler`此类的Class对象，然后在通过该Class对象以反射的形式拿到了它的构造方法，并最终通过该构造方法反射并传入两个参数一个是`Override.class`一个常见的注解类对象。而另一个就是我们之前所分析的可以通过调用`Map.entrySet()`方法可以造成代码执行的Map对象。

![](https://images.seebug.org/content/images/2020/04/a8f9da5c-b6a1-483f-b307-e5ac879d07ea.png-w331s)

为什么我们要如此的费力通过反射形式来生成一个AnnotationInvocationHandler对象呢？由以下截图可知。因为该类的构造方法和该类本身都不是public修饰的，所以我们没法通过new一个对象的形式来创建AnnotationInvocationHandler对象

![](https://images.seebug.org/content/images/2020/04/6b33b224-67aa-4fad-8b6d-d52f60885c95.png-w331s)

之前已经简单介绍过了什么是反序列化，JDK序列化/反序列化。如果反序列化的类里有readObject方法，那么就一定会调用该方法。这就给了我们一个可趁之机，我们观察一下`AnnotationInvocationHandler`对象中都执行了些什么。

    
    
    private void readObject(java.io.ObjectInputStream s)
    throws java.io.IOException, ClassNotFoundException {
    s.defaultReadObject();
    // Check to make sure that types have not evolved incompatibly
    AnnotationType annotationType = null;
    try {
        annotationType = AnnotationType.getInstance(type);
    } catch (IllegalArgumentException e) {
        // Class is no longer an annotation type; time to punch out
        throw new java.io.InvalidObjectException("Non-annotation type in annotation serial stream");
    }
    Map<String, Class<?>> memberTypes = annotationType.memberTypes();
    // If there are annotation members without values, that
    // situation is handled by the invoke method.
    for (Map.Entry<String, Object> memberValue : memberValues.entrySet()) {
        String name = memberValue.getKey();
        Class<?> memberType = memberTypes.get(name);
        if (memberType != null) {  // i.e. member still exists
            Object value = memberValue.getValue();
            if (!(memberType.isInstance(value) ||
                    value instanceof ExceptionProxy)) {
                memberValue.setValue(
                        new AnnotationTypeMismatchExceptionProxy(
                                value.getClass() + "[" + value + "]").setMember(
                                annotationType.members().get(name)));
            }
        }
    }
    }

我们在这段代码里看到了一个熟悉的影子，在readObject方法里有一个foreach循环,里面有一个名字叫memberValues的变量调用的entrySet()，也就是说，如果这个memberValues里面存储的是我们之前构造好的那个实现了Map接口的代理对象的话，那就意味着这里就像一个炸弹的引爆点一样，会瞬间执行我们刚才所分析的代码执行路径，并最终执行我们提前包装好的代码。

好那问题是这个变量我们可以控制么？如果该变量不接受外部传入的参数那么这个点就变的毫无价值。但是我们通过分析惊喜的发现，`memberValues`是一个全局变量，接受的恰好就是我们精心构造的那个可以执行代码的代理对象。

![](https://images.seebug.org/content/images/2020/04/be047ded-1623-4ed1-872a-2858bbde4a49.png-w331s)

`AnnotationInvocationHandler`对我们来说就是一个反序列化的入口点，就像是一个引爆器一样。而我们封装好的那个代理对象就是炸弹，在`AnnotationInvocationHandler`进行序列化时被封装了进去作为`AnnotationInvocationHandler`对象一个被序列化的属性存在着，等到`AnnotationInvocationHandler`对象被反序列化时，就瞬间爆炸，一系列的嵌套调用瞬间到达执行`Runtime.getRuntime().exec()`的位置

至此ysoserial Java 反序列化系列第一集 Groovy1原理分析结束

## 总结

其实网上反序列化的文章有很多，但是不知为何大家讲解反序列化漏洞时都是用CC链也就是`Apache.CommonsCollections`来进行举例，平心而论我觉得这个利用连一开始没接触过反序列化的同学直接理解还有一定的难度的，难在整个CC链的调用看上去略微复杂，并不是难在反序列化的部分。所以我挑了一个我觉得调用链比较清晰明了的Groovy来进行java
反序列化分析的第一篇文章，来帮助大家能更快速的了解java
反序列化漏洞。虽然Groovy1这个gadget在实际生产环境中碰的的概率可能少之又少，但是作为一个反序列化入们学习的例子我觉得还是比较适合的。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1171/>

