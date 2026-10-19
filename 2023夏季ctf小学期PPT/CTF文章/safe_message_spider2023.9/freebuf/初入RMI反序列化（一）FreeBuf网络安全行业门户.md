**程序员写在文章前：**

《初入RMI反序列化》将由“RMI基础”及“RMI反序列化漏洞解析”两大部分共同组成，本期我们将着重分析“RMI基础”部分，通过分享“分布式处理中RPC框架、RMI基本通讯代码、RMI源码浅析、代码逻辑总结”等九大部分的内容，与各位读者共同探讨RMI反序列化的方法、逻辑。

## 环境

 **IDEA**

 **攻击端JDK8u92:**

https://www.oracle.com/java/technologies/downloads/

 **服务端 jdk7：**

https://www.oracle.com/java/technologies/downloads/

 **Apache-Commons-Collections 3.1：**

https://commons.apache.org/proper/commons-collections/

 **ysoserial.jar:**

[https://codeload.github.com/frohoﬀ/ysoserial/zip/master](https://codeload.github.com/froho%EF%AC%80/ysoserial/zip/master)

## RMI基础

 **（一）分布式处理中的** **RPC** **框架**

既然要谈RMI了，那我们就得谈谈RPC框架了，例如：RMI(
Java中最早的RPC框架)、grpc(谷歌的框架)、dubbo(阿里巴巴开发的开源RPC框架依托于spring)。虽然RMI已经不适合企业级生产，但是思想仍然值得我们学习。

 **（二）RMI是什么**

RMI是Java的远程方法调用，允许运行在一台Java虚拟机(
JVM)的对象调用运行在另一台虚拟机的对象，这个对象可以在相同计算机的不同进程中，也可以是运行在网络上的不同计算机中，它分为三个部分：端午节吃粽子和赛龙舟的习俗，是为了纪念我国历史上伟大的诗人屈原，也正是因为如此解放后曾把端午节定名为“诗人节”。

![](https://image.3001.net/images/20220817/1660717205_62fc8895d39cd99f65a2c.png!small)这里用先知社区一张图：

![](https://image.3001.net/images/20220817/1660717240_62fc88b8d042f47cfaf97.png!small)

Server与Client通过JRMP协议交互，客户端使用代理调用服务端方法，客户端的代理叫stub、服务端的
代理叫skeleton，漏洞就产生于远程通信的时候。

 **（三）RMI基本通信代码**

我们知道了RMI是个啥，现在我们开始写个测试用代码。

 **1\. 定义一个远程接口**

远程接口定义public修饰的接口类,继承Remote并且要调用java.rmi.Remote和java.rmi.RemoteException。

![](https://image.3001.net/images/20220817/1660717277_62fc88dded61d9b075351.png!small)

 **2\. 实现远程接口**

继承远程接口时，所有方法都需要抛出RemoteException,并且该方法要间接或者直接继承UnicastRemoteObject类(最终会继承到Remote这个接口),该类提供了支持RMI的方法,可以通过JRMP协
议导出一个远程对象的引用，生成动态代理构建的Stub对象。

![](https://image.3001.net/images/20220817/1660717314_62fc8902a7216e0c9e02c.png!small)

![](https://image.3001.net/images/20220817/1660717331_62fc89136c83861095a44.png!small)

 **3\. 服务器端实体**

我们构造一个server端实体，为了远程传输，我们要让他继承序列化接口。

![](https://image.3001.net/images/20220817/1660717366_62fc8936885d63aa5aa5d.png!small)
**4\. 调用远程对象的客户端**

![](https://image.3001.net/images/20220817/1660717617_62fc8a31b5a5cfbca5427.png!small)![](https://image.3001.net/images/20220817/1660717644_62fc8a4c98808dfcaba7b.png!small)

 **5\. 总结**

简单来说就是，服务器A现在有一个sayhello的方法想让另一台服务器B调用，但服务器B显然没办法直接调用服务器A的方法，但是现在RMI来了！服务器A可以把sayhello这个类对象序列化后放到一个"共享池"当中，这样大家都可以通过这个"共享池"调用到这个sayhello方法所在的类中，其实有点像初中计算机课老师把文件放在共享里。

 **（四）RMI源码浅析**

为了避免查找的都是class文件可以参考这个配置：![](https://image.3001.net/images/20220817/1660717686_62fc8a76cf2b36ed9cf86.png!small)

 **（五）服务端发布调试**

1\.
服务端的工作是发布对象到注册中心,这里因为方法实现类继承了UnicastRemoteObject(发布远程对象)；![](https://image.3001.net/images/20220817/1660717723_62fc8a9bbe26f5bd09fe2.png!small)

2\.
跟进这个方法找无参构造打点调试,这里传参是一个0,继续跟进；![](https://image.3001.net/images/20220817/1660717767_62fc8ac75d48a0b2d077e.png!small)3\.
因为this调用的是当前类,因为Remotehello继承了UnicastRemoteObject,所以当前的类是Remotehello继续跟进；![](https://image.3001.net/images/20220817/1660717818_62fc8afa799fb0418ba2f.png!small)4\.
从名字可以看出这里new了一个发布服务的引用UnicastServerRef,并且传入了port(端口)；![](https://image.3001.net/images/20220817/1660717846_62fc8b167a5530a7b4fa6.png!small)5.这里继续套娃,调用了父类有参构造,并且传入了一个LiveRef(实时引用)的对象,从名字可以看出这个对象是
发布远程对象的关键；![](https://image.3001.net/images/20220817/1660717868_62fc8b2c0d36a2b930804.png!small)6.调用的本类的有参构造,并且new了一个objID,这个顾名思义就是ID号,没必要继续debug,我们回到上一层,继续看UnicastServerRef的父类有参构造；![](https://image.3001.net/images/20220817/1660717888_62fc8b407876310de373b.png!small)![](https://image.3001.net/images/20220817/1660717905_62fc8b517699b62c74cee.png!small)7.这里可以看到,LiveRef(实时引用)对象带了一个与TCP有关的对象,这个就与网络传输有关了,目前端口号还是0,没变化,然后就把这个对象封装给了UnicastRef(远程引用)的ref中；![](https://image.3001.net/images/20220817/1660717933_62fc8b6d9413ceb1022e8.png!small)

8\. 显然上面的var1中的UnicastRef对象封装了进来,并且这个对象中封装了LiveRef和TCP,这里if判断了obj的类型；

instanceof判断的范围是:接口、子类、当前类,所以这一条是一定可以过的；

后续将封装起来的UnicastRef对象赋值,并且返回值中调用了UnicastRef的exportObject(导出对象)方法,导出的正是RemoteHelloWorld对象；

![](https://image.3001.net/images/20220817/1660717960_62fc8b887fba664aa974d.png!small)

  

9\. 这里是标准的代理写法,创建了RemoteHelloWorld类的代理,这里的跟进很多,略过一部分；

![](https://image.3001.net/images/20220817/1660717986_62fc8ba2a1456a5154cf1.png!small)

10\.
这里使用了一个Class.forName的方法初始化了对象。但这里有一个疑问:Stub应该是client端用的,但为什么在server出来了？stub由server制定创建,client拿出stub使用；

![](https://image.3001.net/images/20220817/1660718031_62fc8bcf3b4360d6bcc50.png!small)

11.到这里stub创建就算完成了,后续还会调用loadClass来进行类加载,这里不一一截图了；

![](https://image.3001.net/images/20220817/1660718097_62fc8c116e958f6d60b8a.png!small)

![](https://image.3001.net/images/20220817/1660718123_62fc8c2b05c47de6e725e.png!small)

12\.
后续跟进可以发现端口进行了随机数的赋值,这里的端口赋值可以从TCPEndpoint类中找到对应方法(之前TCPEndpoint类就被封装了进来),这里就算发布完成了。

 **（六）注册中心和注册表的创建**

![](https://image.3001.net/images/20220817/1660718156_62fc8c4c247eab14dad8e.png!small)![](https://image.3001.net/images/20220817/1660718170_62fc8c5a48889ee5c8757.png!small)
1\.
方法名就能看出,是用来创建注册表的,这里new了RegistryImpl,跟进一下；![](https://image.3001.net/images/20220817/1660718206_62fc8c7eed65c877e1058.png!small)2\.
这里跟刚刚的发布对象的感觉差不多,也是创建一个代理类,不过这个代理类是给服务端自己用的；

![](https://image.3001.net/images/20220817/1660718238_62fc8c9e735dceb88133e.png!small)

![](https://image.3001.net/images/20220817/1660720086_62fc93d68e0242fe86d91.png!small)![](https://image.3001.net/images/20220817/1660720119_62fc93f78389a656d2974.png!small)

3.从后面代码逻辑看,很明显这个也是一个创建代理类,不过跟刚刚的不同的是,registryimpl是jdk自己的类，不用我们自己写；

这个过程有俩代理,一个stub给客户端用,另一个Skeleton给服务器用,我们去Skeleton对应的几个类下断点看看：

DGCImpl_Skel.class 创建远程对象的时候调用；

RegistryImpl_Skel.class 创建注册表的时候调用。

![](https://image.3001.net/images/20220817/1660720149_62fc94159fd54d126d750.png!small)![](https://image.3001.net/images/20220817/1660720166_62fc942679404706373f4.png!small)

ps: 这里可以看到几个readObject的调用在dispatch(派发)方法中但是这里打点我没有跟踪到....

 **（七）客户端请求注册中心**

![](https://image.3001.net/images/20220817/1660720202_62fc944a1de0927f7f3c8.png!small)![](https://image.3001.net/images/20220817/1660720213_62fc9455b527daa98bc3c.png!small)
1\.
第一步就是请求/获取注册中心,跟进getRegistry后发现返回值又调用了一层getRegistry方法,继续debug一下；![](https://image.3001.net/images/20220817/1660720241_62fc94718b94c44ae9b1d.png!small)2\.
这段代码我们又看到了老朋友--liveRef跟UnicastRef,后续又是一个创建代理类,后续代码用的也是这个
代理类带有了lookup方法,继续跟进；![](https://image.3001.net/images/20220817/1660720261_62fc9485ae4909933059c.png!small)![](https://image.3001.net/images/20220817/1660720273_62fc94910cc26fd9e51e1.png!small)

3\. 这里有个对于安全人员来说比较敏感的方法：writeObject(存储对象)和invoke(反射)， **这里其实也开始到重点,java
rmi反序列化！**

第一个点writeObject:我们lookup传参一个参数是hello,这里write直接把我们的传参序列化后写了进
去,这样对面注册中心就一定会进行反序列化,这里就是一个攻击点；

第二个点invoke:后续的invoke是一个激活网络请求的方法。

![](https://image.3001.net/images/20220817/1660720301_62fc94ad6aee3b9a4c2dd.png!small)4\.
executeCall方法就是用来处理客户请求的,
**这里有一个有意思的点！**![](https://image.3001.net/images/20220817/1660720371_62fc94f357e8ed0b63c12.png!small)

5\.
在处理请求的时候会抛一个异常类,这里进行了一次readObject,这里就会出现一个问题,如果连接的时候有一个恶意流,那客户端反序列化的时候就会反序列化这个恶意对象,会导致客户端被攻击,这就会导致攻击面更广泛。因为几乎每个涉及连接注册中心的方法都会用这个invoke,估计rmi设计的时候压根没考虑关于这个的安全问题。我们继续往下看...

![](https://image.3001.net/images/20220817/1660720394_62fc950a0c6b23c85cec9.png!small)6\.
显示获取了一个输入流,然后这里有一个readObject方法,写和读都全了还没过滤, **那漏洞就来了！**

![](https://image.3001.net/images/20220817/1660720413_62fc951d9197e5639c11e.png!small)

7\. 这里可以看到,var22是一个动态代理类,代理的是rmidemo方法,继续跟进远程方法调用的部分；

![](https://image.3001.net/images/20220817/1660720434_62fc95329aff569ed7e4f.png!small)

8\.
这里是一个动态代理,所以会走到一个RemoteObjectInvocationHandler类,这里的hello也可以看到,最终嵌套的是一个LiveREF里面有刚刚服务端开放的端口。

![](https://image.3001.net/images/20220817/1660720451_62fc954397fa4f54297cd.png!small)

 **（八）客户端调用远程方法**

1\.
我们在两个可能成为攻击点的位置打点debug,在调用方法的时候可以发现,只要涉及到连接注册中心,那就得进一次executeCall；![](https://image.3001.net/images/20220817/1660720477_62fc955d82fb79433651c.png!small)2\.
继续调试,当函数有返回值的时候会进入一个unmarshalValue()方法,这里也有一个反序列化的点；  
![](https://image.3001.net/images/20220817/1660720496_62fc9570481230cd0d1d0.png!small)3\.
继续调试就会看到一个我们返回的字符串,这里就可能成为一个攻击点来攻击客户端；  
![](https://image.3001.net/images/20220817/1660720519_62fc95877c2474b396016.png!small)

 **（九）代码逻辑总结**

1\. 序列化跟反序列化的关系是对称的,客户端传字符串hello的时候如果给一个恶意参数服务端反序列化读取的时候就可以攻击服务端；

2\. 反之,如果有返回值,那客户端就会进行一次反序列化读取,所以客户端跟服务端可以互锤，可以尝试一下！

下一期，我们将会和大家分享"RMI反序列化漏洞解析”的相关内容，记得继续关注哦！

