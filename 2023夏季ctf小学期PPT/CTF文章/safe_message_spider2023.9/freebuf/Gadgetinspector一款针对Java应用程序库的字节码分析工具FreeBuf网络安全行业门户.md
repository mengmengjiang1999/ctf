![](https://image.3001.net/images/20200223/1582460075_5e526cab6c036.jpg!small)

##  Gadgetinspector

**Gadgetinspector是一款针对Java应用程序/库的字节码分析工具，它可以帮助研究人员寻找和分析Java应用程序中的反序列化小工具链（Gadget
Chain）。**

该项目可以检查Java代码库和类路径中的Gadget链，而Gadget链可以被用来构造针对反序列化漏洞的漏洞利用技术。通过自动化识别和发现目标Java应用程序类路径中可能的Gadget链，渗透测试研究人员可以快速构造攻击代码或漏洞利用代码，而对于应用程序安全工程师将能够对反序列化漏洞的影响进行评估，并确定其修复的优先级。

##  工具下载

广大研究人员可以使用下列命令将Gadgetinspector项目源码克隆至本地：

    
    
    git clone https://github.com/JackOfMostTrades/gadgetinspector.git

##  项目构建

假设你的系统上已经安装好了JDK，那你就可以直接运行下列命令了：

    
    
    ./gradlew shadowJar

接下来，你就可以使用下列命令来对一个目标Java应用程序来进行分析了：

    
    
    java -jar build/libs/gadget-inspector-all.jar <args>

##  工具使用

在使用该工具时，我们需要通过参数的形式来给Gadgetinspector提供一个war文件或任意数量jar文件的路径。如果你提供的是一个war文件，那么工具将会对war文件进行分解，并且其中所有的类和库都将会被当作类路径来处理。

需要注意的是，分析过程将会是内存密集型的，也就是说会占用掉大量的系统内存，因为Gadgetinspector还没有进行内存方面的优化。对于较小的代码库，你可能需要至少2GB的堆内存空间，如果分析的应用程序体积较大，你可能还需要使用到更多的内存。

该工具包可以通过几个阶段的类路径检测来构建后续将要使用到的数据集，这些数据**被写入到以.dat为后缀的数据文件中，在被执行后将会被丢弃，因为它们的主要功能是为了在开发过程中跳过早期阶段。

分析任务完成之后，工具将会把数据写入至gadget-chains.txt文件中。

##  使用样例

在下面给出的样例中，我们将对commons-collections-3.2.1.jar【[下载地址](http://central.maven.org/maven2/commons-collections/commons-collections/3.2.1/commons-collections-3.2.1.jar)】进行分析，相关命令如下：

    
    
    wget <http://central.maven.org/maven2/commons-collections/commons-collections/3.2.1/commons-collections-3.2.1.jar>
    
        java -Xmx2G -jar build/libs/gadget-inspector-all.jar commons-collections-3.2.1.jar

在gadget-chains.txt中，我们找到了下列Gadget链：

    
    
    com/sun/corba/se/spi/orbutil/proxy/CompositeInvocationHandlerImpl.invoke(Ljava/lang/Object;Ljava/lang/reflect/Method;[Ljava/lang/Object;)Ljava/lang/Object; (-1)
    
          com/sun/corba/se/spi/orbutil/proxy/CompositeInvocationHandlerImpl.invoke(Ljava/lang/Object;Ljava/lang/reflect/Method;[Ljava/lang/Object;)Ljava/lang/Object; (0)
    
          org/apache/commons/collections/map/DefaultedMap.get(Ljava/lang/Object;)Ljava/lang/Object; (0)
    
          org/apache/commons/collections/functors/InvokerTransformer.transform(Ljava/lang/Object;)Ljava/lang/Object; (0)
    
          java/lang/reflect/Method.invoke(Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object; (0)

这个Gadget链的入口点是JDK中InvocationHandler类的实现，将同样的技术应用到原始的commons-collections
Gadget链中，这个类中任何可序列化实现都可以在Gadget链中访问到，因此我们选择这里作为分析的入口点。这个方法会调用classToInvocationHandler.get()，我们所发现的Gadget链表明，classToInvocationHandler能够序列化为DefaultedMap，因此该调用将会跳转到DefaultedMap.get()。Gadget链的下一步将会调用该方法中的value.transform()，这个类中的参数值可以被序列化为InvokerTransformer。在这个类的transform()方法中，我们可以看到“
cls.getMethodName(iMethodName,
...).invoke(...)”这样的调用，而Gadgetinspector将会确定iMethodName就是攻击者可控的，并且是一个可序列化的兑现，因此攻击者将能够执行该类中的任意方法。

###  其他样例

如果你想了解更多这款工具能够查找到的Gadget链，你可以参考下列代码库：

>
> 1、<http://central.maven.org/maven2/org/clojure/clojure/1.8.0/clojure-1.8.0.jar>
>
> 2、<https://mvnrepository.com/artifact/org.scala-lang/scala-library/2.12.5>
>
> 3、<http://central.maven.org/maven2/org/python/jython-> standalone/2.5.3/jython-standalone-2.5.3.jar>

除此之外，你还可以利用Gadgetinspector对一个完整的应用程序进行分析，比如说对Zksample2应用程序的war文件来进行分析，我们可以获取到下列Gadget链：

    
    
    net/sf/jasperreports/charts/design/JRDesignPieDataset.readObject(Ljava/io/ObjectInputStream;)V (1)
    
          org/apache/commons/collections/FastArrayList.add(Ljava/lang/Object;)Z (0)
    
          java/util/ArrayList.clone()Ljava/lang/Object; (0)
    
          org/jfree/data/KeyToGroupMap.clone()Ljava/lang/Object; (0)
    
          org/jfree/data/KeyToGroupMap.clone(Ljava/lang/Object;)Ljava/lang/Object; (0)
    
          java/lang/reflect/Method.invoke(Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object; (0)

你可以看到，这款应用程序使用了多种不同的代码库来构建Gadget链。

##  项目地址

>
> Gadgetinspector：【[GitHub传送门](https://github.com/JackOfMostTrades/gadgetinspector)】

 ***
参考来源：[JackOfMostTrades](https://github.com/JackOfMostTrades/gadgetinspector)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

