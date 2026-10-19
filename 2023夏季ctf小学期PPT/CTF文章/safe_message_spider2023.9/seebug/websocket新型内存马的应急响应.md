**作者：flamingo  
原文链接：<https://mp.weixin.qq.com/s/T3UfA1plrlG-e9lgfB4whg>**

前几天看到一个推送，websocket新型内存马。因其自身注册在Ws下面所以常规的内存检测脚本memshell scanner无法快速检出来。

项目地址：<https://github.com/veo/wsMemShell>

![图片](https://images.seebug.org/content/images/2022/07/18/1658127276000-1pjqxy.png-w331s)

为了防止应急响应的时候翻车，我复现了一下ws内存马，并在本地环境上做了一套检测方案，能够有效的查找这款内存马。

## 内存马复现

这套内存马作者提供了wscmd.jsp的样例文件。通过查看这个jsp代码跟作者给出的方法，大概就是上传这个jsp，然后通过参数传入路径，便能在其传入的路径下注册一个内存马。

![图片](https://images.seebug.org/content/images/2022/07/18/1658127276000-2rcpdw.png-w331s)

![图片](https://images.seebug.org/content/images/2022/07/18/1658127276000-3scjpp.png-w331s)

根据这个方法，在本地搭建了tomcat后放上恶意文件，然后传入地址参数，实现了内存马的操作

![图片](https://images.seebug.org/content/images/2022/07/18/1658127276000-4rxutg.png-w331s)

从流量上看没有任何的特征

![图片](https://images.seebug.org/content/images/2022/07/18/1658127277000-5jxjip.png-w331s)

不信邪的我又跑去喊同事搭建了远程环境上去测了一下，还真的是没法看，但是传输的协议的WS，又不是wss，我不是很理解这是为什么，希望有知道的师傅指教一下。

不能说毫无特征吧，只能说没啥可看。

![图片](https://images.seebug.org/content/images/2022/07/18/1658127277000-6mttna.png-w331s)

![图片](https://images.seebug.org/content/images/2022/07/18/1658127277000-7srtgb.png-w331s)

看起来这个方法再跟上反序列化漏洞的方法，将会是今年hw一大杀器。

## WS内存马检测手法

由于我本身目前工作都是蓝队应急方向的，所以这种大杀器在我这里就算不能流量设备检测出来，上机也得排出来。

既然是写在java内存里的，那么就能从内存里找到它。

java目录下打开java自带的jvm内存查看工具HSDB

java -cp sa-jdi.jar sun.jvm.hotspot.HSDB

![图片](https://images.seebug.org/content/images/2022/07/18/1658127277000-8ctafm.png-w331s)

根据注入的方法，可以看出来应该是在Endpoint注册的，根据作者提供的思路也应该是这样

![图片](https://images.seebug.org/content/images/2022/07/18/1658127277000-9rvjjk.png-w331s)

![图片](https://images.seebug.org/content/images/2022/07/18/1658127278000-10trsho.png-w331s)

从tomcat目录下jps找到tomcat的pid

![图片](https://images.seebug.org/content/images/2022/07/18/1658127278000-11ydyzz.png-w331s)

根据pid打开

![图片](https://images.seebug.org/content/images/2022/07/18/1658127278000-12takaw.png-w331s)

![图片](https://images.seebug.org/content/images/2022/07/18/1658127278000-13rvpcd.png-w331s)

从HSDB的class browser里面找这个class

![图片](https://images.seebug.org/content/images/2022/07/18/1658127278000-14xfzzn.png-w331s)

![图片](https://images.seebug.org/content/images/2022/07/18/1658127279000-15rwjbc.png-w331s)

打开它，并找到它的类层次结构，可以很轻易的看到这个jsp生成的内存马

![图片](https://images.seebug.org/content/images/2022/07/18/1658127279000-16kdhbv.png-w331s)

马上把它导出来丢到ida里面看看，确实可以锁定这个是内存马，干掉就行

![图片](https://images.seebug.org/content/images/2022/07/18/1658127279000-17wnciw.png-w331s)

## 反序列化实现

那么反序列化出来的内存马是不是这样的呢？找了@清水川崎 水子哥来帮忙写了一段shiro反序列化的ws内存马注入，做了环境复现

反序列化复现方法这里不说了，减少今年干活儿的次数

![图片](https://images.seebug.org/content/images/2022/07/18/1658127279000-18hddqw.png-w331s)

同样的手法去检测，可以看到也能很明显的快速定位到ws内存马的位置

![图片](https://images.seebug.org/content/images/2022/07/18/1658127279000-19jdrej.png-w331s)

![图片](https://images.seebug.org/content/images/2022/07/18/1658127279000-20zwqdr.png-w331s)

![图片](https://images.seebug.org/content/images/2022/07/18/1658127280000-21emisr.png-w331s)

那么此次检测应急方法到此结束，后续遇到ws内存马可以按照此类方法检测。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1935/>

