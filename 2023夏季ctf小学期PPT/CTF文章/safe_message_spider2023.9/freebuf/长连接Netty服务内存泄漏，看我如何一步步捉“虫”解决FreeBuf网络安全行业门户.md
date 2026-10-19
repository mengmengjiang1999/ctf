​作者：京东科技 王长春

# 背景

事情要回顾到双11.11备战前夕，在那个风雨交加的夜晚，一个急促的咚咚报警，惊破了电闪雷鸣的黑夜，将沉浸在梦香，熟睡的我惊醒。

一看手机咚咚报警，不好！有大事发生了！电话马上打给老板：

> 老板说： 长连接吗?  
> 我说：是的！  
> 老板说：该来的还是要来的，最终还是来了，快，赶紧先把服务重启下！  
> 我说：已经重启了！  
> 老板说： 这问题必须给我解决了！  
> 我说：必须的！

 **线上应用长连接Netty服务出现内存泄漏了！真让人头大**

在这风雨交加的夜晚，此时，面对毫无头绪的问题，以及迫切想攻克问题的心，已经让我兴奋不已，手一把揉揉刚还迷糊的眼，今晚又注定是一个不眠之夜！

# 应用介绍

 **说起支付业务的长连接服务，真是说来话长，我们这就长话短说** ：

随着业务及系统架构的复杂化，一些场景，用户操作无法同步得到结果。一般采用的短连接轮训的策略，客户端需要不停的发起请求，时效性较差还浪费服务器资源。

 **短轮训痛点:**

  * 时效性差
  * 耗费服务器性能
  * 建立、关闭链接频繁

相比于短连接轮训策略，长连接服务可做到实时推送数据，并且在一个链接保持期间可进行多次数据推送。服务应用常见场景：PC端扫码支付，用户打开扫码支付页面，手机扫码完成支付，页面实时展示支付成功信息，提供良好的用户体验。

 **长连服务优势:**

  * 时效性高提升用户体验
  * 减少链接建立次数
  * 一次链接多次推送数据
  * 提高系统吞吐量

![长连接服务系统架构](https://image.3001.net/images/20230423/1682217233_6444991170ffb56fd6c5a.png!small)

这个长连接服务使用`Netty`框架，`Netty`的高性能为这个应用带来了无上的荣光，承接了众多长连接使用场景的业务：

  * PC收银台微信支付
  * 声波红包
  * POS线下扫码支付

# 问题现象

回到线上问题，出现内存泄漏的是长连接前置服务，观察线上服务，这个应用的内存泄漏的现象总伴随着内存的增长，
**这个增长真是非常的缓慢，缓慢，缓慢，2、3个月内从30%慢慢增长到70%，极难发现** ：

![应用实例的内存总是在缓慢的增长](https://image.3001.net/images/20230423/1682217234_644499120ae9ac6ad09dd.png!small)

每次发生内存泄漏，内存快耗尽时，总得重启下，
**虽说重启是最快解决的方法，但是程序员是天生懒惰的，要数着日子来重启，那绝对不是一个优秀程序员的行为！问题必须彻底解决！**

# 问题排查与复现

### 排查

遇到问题，毫无头绪，首先还是需要去案发第一现场，排查“死者(应用实例)”死亡现场，通过在发生FullGC的时间点，通过Digger查询`ERROR`日志，没想到还真找到破案的第一线索:

![线上出现问题日志](https://image.3001.net/images/20230423/1682217234_644499129a7c71a8f2a86.png!small)

    
    
    io.netty.util.ResourceLeakDetector [176] - LEAK: ByteBuf.release() was not called before it's garbage-collected. Enable advanced leak reporting to find out where the leak occurred. To enable advanced leak reporting, specify the JVM option '-Dio.netty.leakDetection.level=advanced' or call ResourceLeakDetector.setLevel() See http://netty.io/wiki/reference-counted-objects.html for more information.
    
    
    

线上日志竟然有一个明显的`"LEAK"`泄漏字样，作为技术人的敏锐的技术嗅觉，和找Bug的直觉，可以确认，这就是事故案发第一现场。

我们凭借下大学四六级英文水平的，继续翻译下线索，原来是这呐！

> ByteBuf.release（） 在垃圾回收之前没有被调用。启用高级泄漏报告以找出泄漏发生的位置。要启用高级泄漏报告，请指定 JVM
> 选项“-Dio.netty.leakDetectionLevel=advanced”或调用
> ResourceLeakDetector.setLevel（）

啊哈！这信息不就是说了嘛！`ByteBuf.release（）`在垃圾回收前没有调用，有`ByteBuf`对象没有被释放，`ByteBuf`可是分配在直接内存的，没有被释放，那就意味着堆外内存泄漏，所以内存一直是非常缓慢的增长，GC都不能够进行释放。

提供了这个线索，那到底是我们应用中哪段代码出现了`ByteBuf`对象的内存泄漏呢？  
项目这么大，Netty通信处理那么多，怎么找呢？自己从中搜索，那肯定是不靠谱，找到了又怎么释放呢？

### 复现

面对这一连三问？别着急，Netty的日志提示还是非常完善： **启用高级泄漏报告找出泄漏发生位置**
嘛，生产上不可能启用，并且生产发生时间极长，时间上来不及，而且未经验证，不能直接生产发布，那就本地代码复现一下！找到具体代码位置。

为了本地复现`Netty`泄漏，定位详细的内存泄漏代码，我们需要做这几步：

1、配置足够小的本地JVM内存，以便快速模拟堆外内存泄漏。  
如图，我们设置设置PermSize=30M, MaxPermSize=43M  
![IDEA配置本地JVM内存](https://image.3001.net/images/20230423/1682217235_6444991368ec12146e50e.png!small)

2、模拟足够多的长连接请求，我们使用Postman定时批量发请求，以达到服务的堆外内存泄漏。

启动项目，通过`JProfiler`JVM监控工具，我们观察到内存缓慢的增长，最终触发了本地`Netty`的堆外内存泄漏，本地复现成功：

![JProfilerJVM监控](https://image.3001.net/images/20230423/1682217235_64449913f136cd71bcc48.png!small)

![复现线上生产问题](https://image.3001.net/images/20230423/1682217236_64449914d19d25b4e1aa0.png!small)

_ **那问题具体出现在代码中哪块呢？** _我们最重要的是定位具体代码，在开启了`Netty`的高级内存泄漏级别为高级，来定位下：

3、开启`Netty`的高级内存泄漏检测级别，JVM参数如下：  
`-Dio.netty.leakDetectionLevel=advanced`

![IDEA配置本地JVM内存-增加DIO](https://image.3001.net/images/20230423/1682217237_64449915a9845b8ae7160.png!small)

再启动项目，模拟请求，达到本地应用JVM内存泄漏，Netty输出如下具体日志信息，可以看到，具体的日志信息比之前的信息更加完善：

    
    
    2020-09-24 20:11:59.078 [nioEventLoopGroup-3-1] INFO  io.netty.handler.logging.LoggingHandler [101] - [id: 0x2a5e5026, L:/0:0:0:0:0:0:0:0:8883] READ: [id: 0x926e140c, L:/127.0.0.1:8883 - R:/127.0.0.1:58920]
    2020-09-24 20:11:59.078 [nioEventLoopGroup-3-1] INFO  io.netty.handler.logging.LoggingHandler [101] - [id: 0x2a5e5026, L:/0:0:0:0:0:0:0:0:8883] READ COMPLETE
    2020-09-24 20:11:59.079 [nioEventLoopGroup-2-8] ERROR io.netty.util.ResourceLeakDetector [171] - LEAK: ByteBuf.release() was not called before it's garbage-collected. See http://netty.io/wiki/reference-counted-objects.html for more information.
    WARNING: 1 leak records were discarded because the leak record count is limited to 4. Use system property io.netty.leakDetection.maxRecords to increase the limit.
    Recent access records: 5
    #5:
    	io.netty.buffer.AdvancedLeakAwareCompositeByteBuf.readBytes(AdvancedLeakAwareCompositeByteBuf.java:476)
    	io.netty.buffer.AdvancedLeakAwareCompositeByteBuf.readBytes(AdvancedLeakAwareCompositeByteBuf.java:36)
    	com.jd.jr.keeplive.front.service.nettyServer.handler.LongRotationServerHandler.getClientMassageInfo(LongRotationServerHandler.java:169)
    	com.jd.jr.keeplive.front.service.nettyServer.handler.LongRotationServerHandler.handleHttpFrame(LongRotationServerHandler.java:121)
    	com.jd.jr.keeplive.front.service.nettyServer.handler.LongRotationServerHandler.channelRead(LongRotationServerHandler.java:80)
    	io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:362)
    	io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:348)
    	io.netty.channel.AbstractChannelHandlerContext.fireChannelRead(AbstractChannelHandlerContext.java:340)
    	io.netty.channel.ChannelInboundHandlerAdapter.channelRead(ChannelInboundHandlerAdapter.java:86)
    	......
    #4:
    	Hint: 'LongRotationServerHandler#0' will handle the message from this point.
    	io.netty.buffer.AdvancedLeakAwareCompositeByteBuf.touch(AdvancedLeakAwareCompositeByteBuf.java:1028)
    	io.netty.buffer.AdvancedLeakAwareCompositeByteBuf.touch(AdvancedLeakAwareCompositeByteBuf.java:36)
    	io.netty.handler.codec.http.HttpObjectAggregator$AggregatedFullHttpMessage.touch(HttpObjectAggregator.java:359)
    	......
    #3:
    	Hint: 'HttpServerExpectContinueHandler#0' will handle the message from this point.
    	io.netty.buffer.AdvancedLeakAwareCompositeByteBuf.touch(AdvancedLeakAwareCompositeByteBuf.java:1028)
    	io.netty.buffer.AdvancedLeakAwareCompositeByteBuf.touch(AdvancedLeakAwareCompositeByteBuf.java:36)
    	io.netty.handler.codec.http.HttpObjectAggregator$AggregatedFullHttpMessage.touch(HttpObjectAggregator.java:359)
      ......
    #2:
    	Hint: 'HttpHeartbeatHandler#0' will handle the message from this point.
    	io.netty.buffer.AdvancedLeakAwareCompositeByteBuf.touch(AdvancedLeakAwareCompositeByteBuf.java:1028)
    	io.netty.buffer.AdvancedLeakAwareCompositeByteBuf.touch(AdvancedLeakAwareCompositeByteBuf.java:36)
    	io.netty.handler.codec.http.HttpObjectAggregator$AggregatedFullHttpMessage.touch(HttpObjectAggregator.java:359)
      ......
    #1:
    	Hint: 'IdleStateHandler#0' will handle the message from this point.
    	io.netty.buffer.AdvancedLeakAwareCompositeByteBuf.touch(AdvancedLeakAwareCompositeByteBuf.java:1028)
    	io.netty.buffer.AdvancedLeakAwareCompositeByteBuf.touch(AdvancedLeakAwareCompositeByteBuf.java:36)
    	io.netty.handler.codec.http.HttpObjectAggregator$AggregatedFullHttpMessage.touch(HttpObjectAggregator.java:359)
      ......
    Created at:
    	io.netty.util.ResourceLeakDetector.track(ResourceLeakDetector.java:237)
    	io.netty.buffer.AbstractByteBufAllocator.compositeDirectBuffer(AbstractByteBufAllocator.java:217)
    	io.netty.buffer.AbstractByteBufAllocator.compositeBuffer(AbstractByteBufAllocator.java:195)
    	io.netty.handler.codec.MessageAggregator.decode(MessageAggregator.java:255)
      ......
    
    
    

开启高级的泄漏检测级别后，通过上面异常日志，我们可以看到内存泄漏的具体地方：`com.jd.jr.keeplive.front.service.nettyServer.handler.LongRotationServerHandler.getClientMassageInfo(LongRotationServerHandler.java:169)`

![内存泄漏代码快](https://image.3001.net/images/20230423/1682217238_6444991672ec6cdabe288.png!small)

不得不说`Netty`内存泄漏排查这点是真香！真香好评！

# 问题解决

找到问题了，那我么就需要解决，如何释放`ByteBuf`内存呢？

## 如何回收泄漏的ByteBuf

其实`Netty`官方也针对这个问题做了专门的讨论，一般的经验法则是，最后访问引用计数对象的一方负责销毁该引用计数对象，具体来说：

  * 如果一个[发送]组件将一个引用计数的对象传递给另一个[接收]组件，则发送组件通常不需要销毁它，而是由接收组件进行销毁。

  * 如果一个组件使用了一个引用计数的对象，并且知道没有其他对象将再访问它（即，不会将引用传递给另一个组件），则该组件应该销毁它。

详情请看翻译的Netty官方文档对引用计数的功能使用：

[【翻译】Netty的对象引用计数](http://sd.jd.com/article/13509?shareId=5032&isHideShareButton=1)  
[【原文】Reference counted objects](https://netty.io/wiki/reference-counted-objects.html)

 **总结起来主要三个方式** ：  
 **方式一** ：手动释放，哪里使用了，使用完就手动释放。  
 **方式二** ：升级`ChannelHandler`为`SimpleChannelHandler`，
在`SimpleChannelHandler`中，`Netty`对收到的所有消息都调用了`ReferenceCountUtil.release（msg）`。  
 **方式三**
：如果处理过程中不确定`ByteBuf`是否应该被释放，那交给Netty的`ReferenceCountUtil.release（msg）`来释放，这个方法会判断上下文是否可以释放。

考虑到长连接前置应用使用的是`ChannelHandler`，如果升级`SimpleChannelHandler`对现有API接口变动比较大，同时如果手动释放，不确定是否应该释放风险也大，因此使用方式三，如下：

![修复代码](https://image.3001.net/images/20230423/1682217239_644499176122a627c3638.png!small)

## 线上实例内存正常

问题修复后，线上服务正常，内存使用率也没有再出现因泄漏而增长，从线上我们增加的日志中看出，`FullHttpRequest`中`ByteBuf`内存释放成功。
**从此长连接前置内存泄漏的问题彻底解决** 。

![线上服务内存释放成功](https://image.3001.net/images/20230423/1682217240_64449918343e581c50ba6.png!small)

# 总结

 **一、Netty的内存泄漏排查其实并不难，Netty提供了比较完整的排查内存泄漏工具**

JVM 选项`-Dio.netty.leakDetection.level`

目前有 4 个泄漏检测级别的：

  * DISABLED - 完全禁用泄漏检测。 **不推荐** 。

  * SIMPLE - 抽样 1% 的缓冲区是否有泄漏。 **默认** 。

  * ADVANCED - 抽样 1% 的缓冲区是否泄漏， **以及能定位到缓冲区泄漏的代码位置** 。

  * PARANOID - 与 ADVANCED 相同，只是它适用于每个缓冲区， **适用于自动化测试阶段** 。如果生成输出包含“LEAK：”，则可能会使生成失败。

本次内存泄漏问题，我们通过本地设置泄漏检测级别为高级，即：`-Dio.netty.leakDetectionLevel=advanced`定位到了具体内存泄漏的代码。

同时Netty也给出了 **避免泄漏的最佳实践** ：

  * 在 PARANOID 泄漏检测级别以及 SIMPLE 级别运行单元测试和集成测试。

  * 在 SIMPLE 级别向整个集群推出应用程序之前，请先在相当长的时间内查看是否存在泄漏。

  * 如果有泄漏，灰度发布中使用 ADVANCED 级别，以获得有关泄漏来源的一些提示。

  * 不要将泄漏的应用程序部署到整个群集。

 **二、解决Netty内存泄漏，Netty也提供了指导方案，主要有三种方式**

 **方式一** ：手动释放，哪里使用了，使用完就手动释放， **这个对使用方要求比较高了** 。  
 **方式二**
：如果处理过程中不确定`ByteBuf`是否应该被释放，那交给`Netty`的`ReferenceCountUtil.release（msg）`来释放，这个方法会判断上下文中是否可以释放，
**简单方便** 。  
 **方式三** ：升级`ChannelHandler`为`SimpleChannelHandler`，
在SimpleChannelHandler中，Netty对收到的所有消息都调用了`ReferenceCountUtil.release（msg）`，
**升级接口，可能对现有API改动会比较大** 。

​

