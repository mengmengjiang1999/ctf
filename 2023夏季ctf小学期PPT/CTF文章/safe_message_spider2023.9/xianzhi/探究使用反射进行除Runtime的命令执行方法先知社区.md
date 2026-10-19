## 概述

在RASP等安全产品防护严密的现在，普通的寻找`Runtime.getRuntime().exec(cmds)`的调用已经成为了一件不现实的事情

同样的，在Java中盛行的反序列化漏洞中，如果将RCE的功能简单的通过`Runtime.getRuntime().exec(cmds)`这种结构来进行实现可能大概率也不能达到我们的目的，所以探索一下Runtime的底层实现，使用更加底层且复杂的调用来进行RCE功能的实现相对来说更加的可行

这里主要是对Java中多种命令执行的方式跟踪源码进行原理分析、构造利用代码、集成自研工具

## 前置

首先需要对Java中的反射机制有着基本的掌握

通过反射的方式，我们可以获取到任何类的构造方法，类方法，成员变量，且能够获取对应类对象进行对应方法的调用等等目的

  1. 获取Class类对象

对于类对象的获取，主要可以通过`Class.forName /
loadClass`的方式来获取，值得注意的是，在调用`Class.forName`进行类的加载的时候，将会调用static方法

    
        Class.forName("java.lang.Runtime")
    

![](./img/347131235034170399.png)

  1. 获取对应类的构造方法

对于获取类的构造方法，主要可以通过`getConstructor`或者`getDeclaredConstructor`这两种方法来进行实现

![](./img/4354429854748539670.png)

![](./img/2128451275820541014.png)

两者的区别主要是前者不能够反射获取`private`修饰的构造方法，而后者能够获取

所以通常使用后者进行构造函数的获取，传入的参数就是对应构造方法的参数类

    
    
    clazz.getDeclaredConstructor(type.class)
       clazz.getConstructor(type.class)
    

  1. 反射获取成员变量

和构造方法类似的，存在有`getField`和`getDeclaredField`两个不同的获取方法，区别和构造函数类似

    
        clazz.getField(name)
    clazz.getDeclaredField(name)
    

  2. 反射获取类方法

同样具有`getMethod`和`getDeclaredMethod`两种

  3. ...............

一个普通的命令执行是

    
    
    Runtime.getRuntime().exec("calc");
    

如果使用反射机制

可以是

    
    
    Class.forName("java.lang.Runtime").getMethod("exec", String.class).invoke(runtime, "calc");
    

或者是其他的一些使用反射机制的变形

## command

### 跟踪Runtime

首先我们跟踪Runtime执行命令的过程

![](./img/6762370093377223731.png)

在这里接收一个`String`类型的参数，调用exec的另一个重在方法对参数进行处理，将其通过分隔符，将其封装成了数组对象(这里就是一个字符串)

![](./img/6204272497721132141.png)

之后通过参数是`String[]`类型的另一个重载方法，通过调用`ProcessBuilder`类的方法进行执行

![](./img/5477159049470916731.png)

在`ProcessBuilder#start`方法中，将命令传递给了`ProcessImpl#start`方法进行处理

![](./img/2627000756350895387.png)

#### windows

在windows中主要是在`ProcessImpl`的构造方法中调用了`create`方法

![](./img/2101863035755714163.png)

这个`create`方法是通过`win32`的方式创建了一个进程

![](./img/2268790946606554443.png)

#### linux

在linux下，在`ProcessImpl#start`的调用中将会创建一个`UNIXProcess`对象并返回

![](./img/2931704757012202347.png)

![](./img/6899359784645964486.png)

在`UNIXProcess`类的构造方法中，调用了`forkAndExec`这个native方法

![](./img/5849966484161994246.png)

创建了一个一个进程，并返回了对应进程的pid

### 构造命令执行

#### ProcessBuilder#start

在上面的流程分析中，知道了在Runtime.getRuntime().exec()方法调用的下一层就是使用`ProcessBuilder#start`方法

如果hook掉了我们可以通过使用`ProcessBuilder`类来进行命令执行的构造

    
    
    new ProcessBuilder("calc").start();
    

或者使用反射的思路构造

    
    
    //method_1
            Class pro = Class.forName("java.lang.ProcessBuilder");
            ((ProcessBuilder) pro.getConstructor(List.class).newInstance(Arrays.asList("calc.exe"))).start();
    
            //method_2
            Class pro = Class.forName("java.lang.ProcessBuilder");
            pro.getMethod("start").invoke(pro.getConstructor(List.class).newInstance(Arrays.asList("calc.exe")));
    
            //method_3
            Class pro = Class.forName("java.lang.ProcessBuilder");
            ((ProcessBuilder) pro.getConstructor(String[].class).newInstance(new String[][]{{"calc.exe"}})).start();
    
            //method_4
            Class pro = Class.forName("java.lang.ProcessBuilder");
            pro.getMethod("start").invoke(pro.getConstructor(String[].class).newInstance(new String[][]{{"calc.exe"}}));
    

#### ProcessImpl

从上面的分析可以知道，在windows环境下的JDK

`ProcessImpl`类的构造方法将会调用`create`方法执行native方法进行命令执行

![](./img/8122176062205839498.png)

所以我们只需要反射获取`ProcessImpl`类的构造方法并实例化就会执行我们的恶意逻辑

#### UNIXProcess

上面是针对windows的方式

针对linux，在前面的分析中知道主要是在其`start`方法中调用了`UNIXProcess`类的构造方法

![](./img/3751965327243881322.png)

执行`forkAndExec`这个native方法进行命令执行

#### other

甚至于，我们知道最后主要是在`create`方法(windows)、`forkAndExec`方法(linux)中执行命令，我们同样可以通过反射这两个方法进行命令执行

