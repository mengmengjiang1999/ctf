![](https://image.3001.net/images/20220623/1655978497_62b43a015253ac3a78867.jpg!small)

## **0x01 前言**

我们通常把反序列化漏洞和反序列化利用链分开来看，有反序列化漏洞不一定有反序列化利用链（经常用shiro反序列化工具的人一定遇到过一种场景就是找到了key，但是找不到gadget，这也就是在这种场景下没有可利用的反序列化利用链）。如果我们向某个漏洞提交平台提交一个反序列化漏洞，但是不给反序列化利用链，那么平台大概率是不会接受这种漏洞的。

反序列化利用链是整个反序列化利用过程中最关键的一环，通常反序列化利用链需要借助常用的第三方jar包，其中最有名的就是CommonCollections利用链（简称CC链）。

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

  

##  **0x02** **反序列化环境准备**

为了更方便初学者来学习反序列化利用链，我们首先要准备当前需要的实验环境。学习反序列化利用链最好的办法是参考ysoserial(https://github.com/frohoff/ysoserial)，ysoserial是一个开源的集成化反序列化利用链工具，可以快速生成反序列化利用链payload。

如果是不追求细节的小伙伴，可以直接按照参照ysoserial使用文档来生成payload，如下图所示。![](https://image.3001.net/images/20220623/1655978573_62b43a4dc6838a9bba56b.png!small)本文的主要目的是教会小伙伴们告别脚本小子，所以就不直接使用编译好的jar包，但是我们后面很多利用代码会参考ysoserial中的代码，ysoserial中关于反序列化利用链的代码都在ysoserial.payloads包中。我们的目的是不通过ysoserial框架，自己实现相应的反序列化利用链。我们搭建反序列化测试的基础环境，新建maven项目，添加项目依赖的jar包。![](https://image.3001.net/images/20220623/1655978596_62b43a64b1faf8ab5b999.png!small)为了模拟序列化和反序列化的过程，编写两个公用的静态方法，这两个方法将在后面的反序列化利用链中被多次使用。其中searialize方法的作用是把对象obj序列化之后保存到文件filename中，unserialize方法的作用是把文件filename中的数据读出来反序列化为对象。![](https://image.3001.net/images/20220623/1655978628_62b43a849cf47ddfab3ba.png!small)通过读写文件来模拟序列化和反序列化的过程是最直观的实现方式，但是在实际环境中，我们遇到的都是基于POST输入的字符输入流来进行反序列化，如下图所示。本地读写文件的反序列化和基于POST输入字符的反序列化是完全没有区别的，所以我们后面在研究反序列化利用链的时候都是通过本地文件读写的方式来实现，而不会准备专门的WEB漏洞环境。![](https://image.3001.net/images/20220623/1655978648_62b43a98ee8967b6b9736.png!small)

某系统反序列化漏洞实例

##  **0x03 反序列化利用链**

###  **0x3.1 URLDNS利用链**

URLDNS链是JAVA众多利用链中最简单的一条利用链，非常适合初学者研究学习，具有下面的特点：

1）利用链只依赖jdk本身提供的类，不依赖其他第三方类，所以具有很高的通用性，可以用于判断目标是否存在反序列化漏洞。

2）利用链本身只能执行域名解析的操作，不能执行系统命令或者其他恶意操作。如果向漏洞提交平台提交反序列化漏洞，但是利用链是URLDNS的利用链，那么漏洞提交平台可能会拒绝这个漏洞。

Ysoserial中关于URLDNS链的主要代码如下图3.1.1，图3.1.2所示。这里面有一个很关键的点是使用了自定义的SilentURLStreamHandler类，为什么要使用这个自定义的类，我将在后面说明原因。

![](https://image.3001.net/images/20220623/1655978724_62b43ae4adaef1de12a31.png!small)图3.1.1
生成URLDNS利用链对象

![](https://image.3001.net/images/20220623/1655978749_62b43afd9060906aef2b9.png!small)

图3.1.2 自定义SilentURLStreamHandler类

  

我们先把ysoserial的代码搬运到本地，做一名合格的搬运工。直接搬运过来之后运行payload可以查看到DNSLOG的日志，证明搬运工没有问题了。搬运过来之后需要去掉ysoserial中的反射调用，我们这里没有Reflections类，所以自己写关于反射调用的代码，如图3.1.3所示，运行结果如图3.1.4所示

![](https://image.3001.net/images/20220623/1655978774_62b43b16e7608b0ee2514.png!small)图3.1.3
本地引用URLDNS利用链

![](https://image.3001.net/images/20220623/1655978798_62b43b2e520ab2cf521a1.png!small)

图3.1.4 运行之后可以在DNSLOG查看DNS请求日志

为了理清楚利用链的整个流程，我们在java.net.
URLStreamHandler类的getHostAddress方法中下断点调试一下，如图3.1.5所示。![](https://image.3001.net/images/20220623/1655978824_62b43b486ae94845eb449.png!small)

图3.1.5 下断点调试URLDNS利用链

运行整个payload，根据debug查看栈调用情况，如图3.1.6所示。其中最关键的红色的框中的部分，可以看出整个利用链非常简单。

![](https://image.3001.net/images/20220623/1655978852_62b43b64d8f3d7d0a167d.png!small)

图3.1.6 URLDNS利用链的栈调用情况

首先反序列化入口是在HashMap的readObject，在这个方法中会调用本类的hash方法，如图3.1.7所示。

![](https://image.3001.net/images/20220623/1655978877_62b43b7de6a1fc830cdb8.png!small)

图3.1.7 在HashMap的readObject方法中调用HashMap的hash方法

继续跟进hash方法，在这个方法中会调用key的hashCode方法。Key对应的值是java.net.URL类的对象，如图3.1.8所示。

![](https://image.3001.net/images/20220623/1655978905_62b43b9932c3028b64042.png!small)

图3.1.8 通过hash方法调用URL类的hashCode方法

继续跟进会调用java.net.URL类的hashCode方法,会调用handler字段的hashCode方法。而handler定义来自于URLStreamHandler类，所以会调用URLStreamHandler类的handler方法，如图3.1.9所示。

![](https://image.3001.net/images/20220623/1655978935_62b43bb7c6adf602a8944.png!small)

图3.1.9 URL类的hashCode方法调用URLStreamHandler类的hashCode方法

继续跟进java.net.URLStreamHandler类的hashCode方法，如图3.1.10所示。这里可以看出里面就直接调用了getHostAddress方法，该方法执行之后会进行域名到IP地址的解析请求。

![](https://image.3001.net/images/20220623/1655978958_62b43bce3f3c0d9a9fc40.png!small)

图3.1.10 最终调用了域名解析相关的方法getHostAddress方法

到这里已经看完了整个调用栈的流程，但是还是没有找到任何理由必须要用自定义的SilentURLStreamHandler类。为了理清楚原因，我们对原来的payload进行修改，去除自定义的SilentURLStreamHandler类，如图3.1.11所示。![](https://image.3001.net/images/20220623/1655978985_62b43be91df85413be5d3.png!small)

图3.1.11 修改后的URLDNS利用链

还是在java.net.
URLStreamHandler类的getHostAddress方法中下断点。可以看到整个栈调用情况如图3.1.12所示。可以看出触发getHostAddress方法的入口点是从generalURLDNS2这个方法，而不是unserialize方法，也就是在生成序列化对象的时候就已经触发了域名解析的请求。由于JAVA内部对DNS请求存在缓存机制，那么在反序列化的时候会优先从DNS缓存中查找域名解析记录，那么反序列化的时候就收不到正确的DNS请求数据。![](https://image.3001.net/images/20220623/1655979009_62b43c018addc3bba4006.png!small)

图3.1.12 修改后的URLDNS利用链

我们跟一下在生成payload时候触发getHostAddress的流程，其中最关键的是执行HashMap中的put方法，如图3.1.13所示。

![](https://image.3001.net/images/20220623/1655979035_62b43c1bd28c7e9507748.png!small)

图3.1.13 URLDNS利用链生成对象时调用HashMap的put方法

跟踪put方法的定义，如图3.1.14所示。里面会调用hash方法![](https://image.3001.net/images/20220623/1655979730_62b43ed2e6562e0f3a744.png!small)

图3.1.14 HashMap的put方法会调用本类的hash方法

剩下的流程和上面分析调用栈一样，最终会导致触发执行getHostAddress方法。为了避免在生成payload的时候触发DNS请求，影响反序列化时DNS请求的执行。有两种解决办法。

1）第一种就是像ysoserial代码中的方式一样，定义一个类继承自URLStreamHandler，并且在类中重写getHostAddress等方法，使得在序列化的时候不会执行getHostAddress方法。

2）第二种办法是通过通过java.net.URL类中的hashCode方法中的逻辑来避免执行后续的getHostAddress方法。

第一种方法在ysoserial的代码中已经写很清楚了，这里主要再说一下第二种方式。在整个利用链中一个很重要的步骤是会调用java.net.URL类中的hashCode方法。如图3.1.14所示。![](https://image.3001.net/images/20220623/1655979082_62b43c4aba6fcd27f93f2.png!small)

图3.1.15 java.net.URL类中的hashCode方法代码逻辑

这里有一个很重要的判断语句是，如果hashCode不等于-1，则直接返回对应hashCode的值，否则调用hashCode方法计算对应的值。这里需要特别注意的一点是这里的hashCode既是java.net.URL类的方法，也是java.net.URL类的字段。所以我们需要

1）第一次put的时候把hashCode字段设置为不是-1的值，避免运行下面的handler.hashCode(this)。

2）生成序列化对象的时候又需要把hashCode字段设置为-1，因为反序列化的时候需要运行下面的handler.hashCode(this)。

所以我们也可以通过反射修改hashCode字段的方式来避免在序列化的时候触发DNS请求，再次修改后的代码如图3.1.15所示。这里最主要的是增加了通过反射修改hashCode字段的操作。![](https://image.3001.net/images/20220623/1655979127_62b43c770fd3fedfc5434.png!small)

图3.1.16 通过控制hashCode字段避免序列化时候触发DNS请求

这样之后也能达到和ysoserial代码一样的效果。也能正常触发URLDNS的请求，如图3.1.16所示。

![](https://image.3001.net/images/20220623/1655979154_62b43c92a1dc91a924d17.png!small)图3.1.17
通过修改的payload触发URLDNS链的DNS请求

###  **0x3.2** **CC链**

CC链是最早出现的影响较大的java反序列化利用链，原作者一共给出7条利用链，但是后来有很多大牛在此基础上给出了一些改进的利用链，对初学者而言，学习CC链是属于学习JAVA反序列化利用链的重要基础。关于CC链的内容很多，限于篇幅有限，这次的文章先开头对部分CC链进行讲解，关于CC链的更多内容将在下一篇文章中详述。本次我们主要先讲关于CC链中的Transform链。在学习Transform链之前，首先需要说明JAVA中命令执行的方式。JAVA中最典型的运行操作系统命令的办法是通过Runtime类来执行，如图3.2.1所示。

  
![](https://image.3001.net/images/20220623/1655979187_62b43cb34b561b3dd8de3.png!small)

图3.2.1 JAVA中执行系统命令的方式

但是在反序列化的过程中不能直接通过Runtime来执行，因为Runtime类没有继承Serializable接口，如图3.2.2所示。![](https://image.3001.net/images/20220623/1655979216_62b43cd06f8d8ac2d50d8.png!small)

图3.2.2 Runtime类没有继承Serializable接口

但是我们可以通过反射的方式来调用Runtime类执行，并且里面涉及到的全部类都继承了Serializable接口，如图3.2.3所示。这里有一个坑是，通过反射来执行方法的返回值类型一定是Object类型，需要做强制类型转换，把Objectl类型转化为Runtime类型。后续的Transform利用链基本上都是通过执行这段代码来执行系统命令的。![](https://image.3001.net/images/20220623/1655979246_62b43cee0d6a602729fd4.png!small)

图3.2.3 通过反射的方式来执行Runtime类的exec方法

严格来说Transform链属于整个CC链中的Sink点，CC链基本上都是通过Transform来最终执行系统命令的。学习Tranform链是掌握CC链的基础前提，最典型的Transform链如图3.2.4所示。![](https://image.3001.net/images/20220623/1655979276_62b43d0c3dfd84978898b.png!small)

图3.2.4 典型Transform链运行情况

直接运行上面的代码是可以弹出计算器的，多数CC链最终也是通过调用类似的代码来执行系统命令。为了理解Transforml链的内容，需要分开来看里面涉及到的几个类：InvokerTransformer类、ConstantTransformer类和ChainedTransformer类。在InvokerTransformer类中，最主要的是transform方法。该方法中通过反射的方式执行任意一个类的方式，如图3.2.5所示。Transform执行的方法必须是public修饰符的。![](https://image.3001.net/images/20220623/1655979305_62b43d292063ff910dbc9.png!small)

图3.2.5 通过InvokerTransformer类的transform方法执行任意public方法

InvokerTransformer类的transform方法提供了一种执行任意其他方法的路径，我们写一个简单的例子来帮助大家理解transform方法，如图3.2.6所示。定义一个类TEST，类中定义一个方法Hello，那么我们就可以通过tranform方法来执行TEST类的Hello方法。![](https://image.3001.net/images/20220623/1655979341_62b43d4dcce68e1d183bb.png!small)

图3.2.6 典型的transform方法调用

可能有的小伙伴会疑惑，我要执行Hello，为什么不直接调用，非要通过transform来调用呢？试想一下，如果我们要执行的是“Runtime.getRuntime()”这样的方法，但是整个系统中都没有任何地方直接调用了这个，那么我们是不是就可以通过transform来间接的执行这个方法呢。但是现在通过transform来执行方法还有一个很明显的不足，就是只能执行单个对象的单个方法，不能链式调用。形象一点来说明这个问题，我们可以执行”Runtime.getRuntim()”，但是我们不能执行“Runtime.getRuntime().exec(xxxx)”。我们需要找到链式调用的方式，幸运的是CommonsCollections中提供了另一个类ChainedTransformer。ChainedTransformer类中提供了链式调用transform方法的办法，如图3.2.7所示。ChainedTransformer类的构造方法是传入Transformer类型的数组，通过transform方法依次遍历数组中的每一个元素，上一步的方法调用的输出作为下一步的方法调用的输入，完美的链式调用解决办法。![](https://image.3001.net/images/20220623/1655979399_62b43d87bc5943337c6e4.png!small)

图3.2.7 通过ChainedTransformer类链式调用transform方法

  
现在已经可以链式调用来执行命令了，但是还有一个问题没有解决，从图3.2.3中可以看出要执行命令，第一步是获取Runtime.class对象，如何通过某个类的transform对象来获取Runtime.class对象呢？这个时候就要用到CommonCollections包里面另一个类ChainedTransformer。ChainedTransformer类的transform方法很简单，就是直接返回构造函数中的iConstant字段，如图3.2.8所示。这完美地解决了我们想要Runtime.class对象的愿望。![](https://image.3001.net/images/20220623/1655979441_62b43db1ee25729c26baa.png!small)

图3.2.8 通过ChainedTransformer类获取Runtime.class对象

通过上面的分析可以知道通过Transform链已经可以达到执行操作系统命令的效果，如图3.2.4所示。目前的情况是如果反序列化的时候，可以调用ChainedTransformer类的transform方法，则可以导致命令执行，但是反序列化的时候会自动调用的是readObject方法，如何通过readObject方法来调用transform方法呢？这是下一次分享的内容，未完待续。

##  **0x04 总结**

这次主要分享的是关于反序列化利用链的知识，主要介绍了URLDNS利用链和CC链中的Transform链。这些都是属于JAVA反序列化的基础知识，后续的知识都会在此基础上进行延展。从文中可以看出反序列化利用链通常包含比较复杂的逻辑知识，就算是最简单的URLDNS链也能让初学者难受，分析反序列化利用链不能太快，理解很重要。后续还有更多关于反序列化利用链的分享，欢迎交流沟通。

 **参考链接**

<https://xz.aliyun.com/t/9873>

<https://github.com/frohoff/ysoserial>

[原文链接﻿](https://mp.weixin.qq.com/s?__biz=MzkzNjMxNDM0Mg==&mid=2247485071&idx=1&sn=830634ad6a570e08a1b5d6780175f028&chksm=c2a1d206f5d65b10f9a731195f726d2885aec965d9ba37551113b81c9afa045a4079480360d3&token=911612436&lang=zh_CN#rd)

