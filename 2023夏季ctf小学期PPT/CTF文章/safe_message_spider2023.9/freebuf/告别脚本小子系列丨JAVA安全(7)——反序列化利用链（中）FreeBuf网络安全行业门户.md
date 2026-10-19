![](https://image.3001.net/images/20230504/1683178922_645345aa5c49c4295b4ee.jpg!small)

## **0x01 前言**

距离上一次更新JAVA安全的系列文章已经过去一段时间了，在上一篇文章中介绍了反序列化利用链基本知识，并阐述了Transform链的基本知识。Transform链并不是一条完整的利用链，只是CommonsCollections利用链中的一部分。当然并不是所有的CC链都需要用Transform链。

为了更方便的理解CC链，我们并不会按照顺序来阐述所有的链，而是按照链的难易程度，由易到难。

 **往期推荐**

1
[告别脚本小子系列丨JAVA安全(1)——JAVA本地调试和远程调试技巧](https://mp.weixin.qq.com/s?__biz=MzkzNjMxNDM0Mg==&mid=2247483768&idx=1&sn=36ff6d279fa7dbd7d5ae00b06a3c3ddc&chksm=c2a1d5f1f5d65ce701e1f73ce0f584412bfc38a507622758f2acabce370cdcc4bb4af2270045&token=1637952127&lang=zh_CN&scene=21#wechat_redirect)

2
[告别脚本小子系列丨JAVA安全(2)——JAVA反编译技巧](https://mp.weixin.qq.com/s?__biz=MzkzNjMxNDM0Mg==&mid=2247483803&idx=1&sn=1af141cd5623b2682cfbdc2c12a53309&chksm=c2a1d512f5d65c04bc046ee83de4ba98881d086837f05cef581b39323026195b504bb5635c4c&token=1637952127&lang=zh_CN&scene=21#wechat_redirect)

3
[告别脚本小子系列丨JAVA安全(3)——JAVA反射机制](https://mp.weixin.qq.com/s?__biz=MzkzNjMxNDM0Mg==&mid=2247483830&idx=1&sn=39c08c61cbab36ace4ac691e0756948b&chksm=c2a1d53ff5d65c29f9b8310c324c67568fe27e61720baffff8af19ef9cb94f5096d73df0c69f&token=1637952127&lang=zh_CN&scene=21#wechat_redirect)

4
[告别脚本小子系列丨JAVA安全(4)——ClassLoader机制与冰蝎Webshell分析](https://mp.weixin.qq.com/s?__biz=MzkzNjMxNDM0Mg==&mid=2247483971&idx=1&sn=13bc478b9bad8c40279f4a2b22c7e29e&chksm=c2a1d6caf5d65fdc4c76043ba0650ca947722c69bfd4bca69a4ef35d3fb318b5cf26fa557c6d&token=1295938837&lang=zh_CN&scene=21#wechat_redirect)

5
[告别脚本小子系列丨JAVA安全(5)——序列化与反序列化](https://mp.weixin.qq.com/s?__biz=MzkzNjMxNDM0Mg==&mid=2247484384&idx=1&sn=675a280b04097ab115a98b623ffc9957&chksm=c2a1d769f5d65e7ff06adba1117ee14d1d772baedcd822302c5827b77fd6177a55f1c6add46b&token=1295938837&lang=zh_CN&scene=21#wechat_redirect)

6
[告别脚本小子系列丨JAVA安全(6)——反序列化利用链（上）](https://mp.weixin.qq.com/s?__biz=MzkzNjMxNDM0Mg==&mid=2247485071&idx=1&sn=830634ad6a570e08a1b5d6780175f028&chksm=c2a1d206f5d65b10f9a731195f726d2885aec965d9ba37551113b81c9afa045a4079480360d3&token=1452276723&lang=zh_CN&scene=21#wechat_redirect)

##  **0x02** **CommonsCollections5链**

CommonsCollections5链是整个CC链中最简单的一条链，通过BadAttributeValueExpException类的readObject方法触发反序列化的过程，最终调用Transform链来达到命令执行的效果。

在ysoserial的环境中调试CommonsCollections5链的方式很简单，如图2.1所示。

![](https://image.3001.net/images/20230504/1683179001_645345f9310397d7ec3bb.png!small)

图2.1 使用ysoserial生成反序列化利用链

直接调用就会执行弹出计算器的命令，跟踪run方法可以查看代码执行逻辑，如图2.2所示。

![](https://image.3001.net/images/20230504/1683179011_64534603c196fe185ec22.png!small)

图2.2 在ysoserial中的序列化和反序列化过程

在ysoserial的run方法中既有序列化的过程，也有反序列化的过程。所以调用run方法因为反序列化的过程导致会执行对应的恶意代码，弹出计算器。

在很多情况下需要保存反序列化对象到文件，可以通过在run方法中添加文件保存方法即可，如图2.3所示。![](https://image.3001.net/images/20230504/1683179045_6453462508fb8eeaab39c.png!small)

图2.3 保存序列化字节码对象到文件

通过上面的方式可以直接把生成的序列化字节码对象保存到文件cc.ser，查看文件内容，如图2.4所示。文件中开头的字符是aced0005，符合序列化文件的标准特征。![](https://image.3001.net/images/20230504/1683179056_64534630005887c7440e2.png!small)

图2.4 通过xxd查看序列化文件保存的内容

通过上面的方式可以利用ysoserial生成标准的CommonsCollections5利用链对应的payload，下一步会继续对CommonsCollections5利用链的调用过程进行分析。

通过debug的方式可以查看整个CommonsCollections5利用链的栈调用过程，如图2.5所示。

![](https://image.3001.net/images/20230504/1683179078_64534646a469dc01f42d3.png!small)

图2.5 CommonsCollections5利用链的栈调用过程

在图2.5中，红框2对应的过程阶段是属于Transform链的调用过程，在上一篇文章中已经进行详述。红框1对应的过程阶段是属于CommonsCollections5特有的调用过程，也是属于本文的重点部分内容。

反序列化的起始点是javax.management.BadAttributeValueExpException类的readObject方法，如图2.6所示。![](https://image.3001.net/images/20230504/1683179095_6453465793d28d7d46aff.png!small)

图2.6 调用BadAttributeValueExpException类的readObject方法

从图2.6可以看出readObject方法首先获取字节流类（也就是本类）对应的val字段，然后基于多个判断，最终下一步操作是val字段对应的toString方法。这里有一点需要注意的是判断逻辑中要求System.getSecurityManager()为null，也就是不能开启SecurityManager模式。

在下一步的调用栈中是调用了org.apache.commons.collections.keyvalue.TiedMapEntry的toString方法，也就是需要把上一步的val字段类型赋值为TiedMapEntry类。在TiedMapEntry类的toString方法中调用了getValue方法，如图2.7所示。

![](https://image.3001.net/images/20230504/1683179115_6453466b78722e4bd7476.png!small)

图2.7 TiedMapEntry类的toString方法

继续跟踪getValue方法，如图2.8所示。![](https://image.3001.net/images/20230504/1683179135_6453467f039d02b836a1a.png!small)

图2.8 调用map接口的get方法

从图2.8可以看出，这里调用了java.util.Map接口的get方法。所有只要找到一个继承自java.util.Map接口的类的get方法中存在恶意调用即可。在CommonsCollections5链中找到的恶意类是org.apache.commons.collections.map.LazyMap类，如图2.9所示。

![](https://image.3001.net/images/20230504/1683179152_64534690a7c683ed9af33.png!small)

图2.9 LazyMap类的get方法调用

从图2.9可以看出LazyMap类的get方法会调用org.apache.commons.collections.Transformer类的transform方法。在上一篇文章的内容中已经讲到在反序列化过程中如果可以调用transform方法，那么就可以通过transform方法来执行系统命令，也就可以达到RCE的效果。

实际上要编写真正可利用的EXP远比基于栈调用来分析更加复杂，因为在编写EXP的过程中，需要考虑每一步栈调用的过程中的逻辑判断条件，这并不是一件简单的事情。

一般来说反序列化利用链代码的编写是倒着来写的，首先是transform链的构造，如果某个类可以调用transformChain的transform方法，则可以执行命令，如图2.10所示![](https://image.3001.net/images/20230504/1683179172_645346a4718e1ce6c5c41.png!small)

图2.10 通过调用Transformer类的transform方法调用执行命令

注释transform方法调用，继续倒序编写EXP。如果某个类可以调用LazyMap类的get方法，则可以执行系统命令，如图2.11所示。![](https://image.3001.net/images/20230504/1683179196_645346bcd1da8308ebb04.png!small)

图2.11 通过调用LazyMap类的get方法执行命令

注释LazyMap的get方法调用，继续倒序编写EXP。如果某个类可以调用TiedMapEntry类的toString方法，则可以执行系统命令，如图2.12所示。

![](https://image.3001.net/images/20230504/1683179216_645346d09229cdb3ba5a4.png!small)

图2.12 通过调用TiedMapEntry类的toString方法执行系统命令

注释TiedMapEntry的toString方法调用，继续倒序编写EXP。找到javax.management.
BadAttributeValueExpException类的readObject方法中存在toString的方法调用，模拟反序列化过程，执行命令，如图2.13所示。

![](https://image.3001.net/images/20230504/1683179234_645346e2ac52b62c72ecf.png!small)

图2.13 模拟BadAttributeValueExpException类的反序列化过程执行命令

这样就完整的复现和分析了CommonsCollections5利用链，从图2.13的payload中可以看出CommonsCollections5利用链中没有复杂的逻辑处理，适合新手入门java反序列化漏洞学习。

##  **0x03** **CommonsCollections7链**

CommonsCollections7链是一条和CommonsCollections5链很像的利用链，最终的结果都是通过LazyMap的get方法调用Transform链来执行命令，调用栈如图3.1所示。

![](https://image.3001.net/images/20230504/1683179282_64534712228657858e5d8.png!small)

图3.1 CommonsCollections7利用链

如图3.1所示，其中红框部分和CommonsCollections5链是完全一样的，区别在于CommonsCollections7链是通过Hashtable类readObject方法一步步调用AbstractMap类的equals方法来调用的。

由于分析调用链的方式基本相同，所以不再对这条链进行分析。

##  **0x04 结论**

CommonsCollections利用链中有多条利用链都涉及到Transform链，包括CC1、CC5、CC6、CC7，其中的调用过程都非常相似。但是并不是所有的CC链都是基于Transform实现的命令执行，在下一篇文章中会讲到其他的利用链，会有更加复杂的应用方式。

[原文链接](https://mp.weixin.qq.com/s?__biz=MzkzNjMxNDM0Mg==&mid=2247485935&idx=1&sn=1ea3b73a420f788dfda878f367a3b4b0&chksm=c2a1dd66f5d654707dd6a554a80f99710faf10229df5059ed8a754b90a424e016b8cffaf94c6&token=2010433839&lang=zh_CN#rd)

