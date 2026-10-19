## 前言

最近挖洞过程中，发现了一些反序列化的问题，然后然后呢。。。发现貌似智慧挖掘反序列化的漏洞，并不太清楚底层代码的原理是什么样子的，这样在和甲方大大battle的时候很被动呢！！！磕磕绊绊、一知半解的回答，甲方大大并不认可技术水平，那么为了刚入门的老铁们不要遇到和我一样的尴尬情况，就整理一篇可供基础入门或者深挖原理的小伙伴们观看吧。。。

实话实说，抓包分析原理这篇文真的快把我搞木得了。。。还是太菜了。。。

还是那句话，如果哪位大佬看到这篇文章，欢迎批评指正。非常欢迎大佬来指导！！！

##  **WebLogic XMLDecoder反序列化漏洞(** ** **CVE-2017-10271**** **)**

###  **漏洞利用说明：**

攻击者可利用weblogic WLS
LS组件的远程代码执行漏洞CVE-2017-10271,对企业服务器发起大范围远程攻击，对大量其要求的服务器造成了严重威胁。近期发现此漏洞的利用方式未传播挖矿程序。。。

受影响版本：

10.3.6.0.0, 12.1.3.0.0, 12.2.1.1.0, 12.2.1.2.0

CVE-2017-10271就是CVE-2017-3506的黑名单绕过操作，CVE-2017-3506本来可以执行对<Object>标签也进行反序列化命令执行，后来Oracle发布了关于CVE-2017-3506的补丁就是将<Object>加入黑名单。。。这种补丁防御对于java的相关防御是非常不安全的。所以就没有彻底修复这个XMLDecoder反序列化漏洞。。。

###  **原理分析：**

CVE-2017-10271漏洞主要是由Weblogic Server WLS组件远程命令执行漏洞，主要由wls-wsat.war触发该漏洞，Weblogic组件使用了自带的webservices处理程序来处理SOAP请求。通过WLLServletAdapter类进行处理，在WorkContentServerTube类中处理POST数据包中传递的XML数据.

即漏洞引发的原因是Weblogic“wls-wsat”组件在反序列化操作时使用了Oracle官方的JDK组件中“ ** **XMLDecoder****
”类进行XML反序列化操作引发了代码执行。也就说XMLDecoder类在解析XML文件的时候出现了反序列化问题。。。

其中，XMLDecoder类是用于读取使用XMLEncoder创建的XML文档。

## XMLDecoder全过程分析

1.调用readObject()函数将xml文件进行反序列化

![1629374861_611e498dbe1fd6360734b.png!small?1629374862917](https://image.3001.net/images/20210819/1629374861_611e498dbe1fd6360734b.png!small?1629374862917)

![1629374869_611e4995bcbe725e332b6.png!small?1629374870654](https://image.3001.net/images/20210819/1629374869_611e4995bcbe725e332b6.png!small?1629374870654)

readObject()方法根据parsingComplete()方法来决定返回值是array数组中的元素还是null

![1629374888_611e49a8c9310eb35d4c5.png!small?1629374889799](https://image.3001.net/images/20210819/1629374888_611e49a8c9310eb35d4c5.png!small?1629374889799)

ParsingComplete()方法读取的xml文件内容的字节流是否为空，如果为空返回false；

判断存储object属性的数组是否为空，如果为空，判断AccessControlContext对象是否为空且是否系统安全管理也为空，如果均为空则抛出异常，提示”AccessControlContext对象没有建立”。。。

如果if语句均不满足，则返回True

![1629374904_611e49b8db3aeaee27d97.png!small?1629374906238](https://image.3001.net/images/20210819/1629374904_611e49b8db3aeaee27d97.png!small?1629374906238)

![1629374912_611e49c016219098ba7e4.png!small?1629374913043](https://image.3001.net/images/20210819/1629374912_611e49c016219098ba7e4.png!small?1629374913043)

![1629374919_611e49c72aa3826b5a9fd.png!small?1629374920151](https://image.3001.net/images/20210819/1629374919_611e49c72aa3826b5a9fd.png!small?1629374920151)

![1629374927_611e49cf9a80ba30d8bed.png!small?1629374928836](https://image.3001.net/images/20210819/1629374927_611e49cf9a80ba30d8bed.png!small?1629374928836)

![1629374936_611e49d8946904cbc890d.png!small?1629374937534](https://image.3001.net/images/20210819/1629374936_611e49d8946904cbc890d.png!small?1629374937534)

![1629374945_611e49e14eadab723a736.png!small?1629374946306](https://image.3001.net/images/20210819/1629374945_611e49e14eadab723a736.png!small?1629374946306)

![1629374990_611e4a0eda5095448e7b9.png!small?1629374992062](https://image.3001.net/images/20210819/1629374990_611e4a0eda5095448e7b9.png!small?1629374992062)

。。。代码调用层比较深入。。。。

这前面的复杂的步骤，我们可以看成是XMLDecoder反序列化xml文件的准备步骤，其中有一点值得注意的是这准备步骤中是没有权限限制的。。。

  2. 调用startElement()方法

![1629374991_611e4a0f1fb562632e2d3.png!small?1629374992063](https://image.3001.net/images/20210819/1629374991_611e4a0f1fb562632e2d3.png!small?1629374992063)

如上图代码所示，就已经读取到了xml文件的第一个标签<java>

![1629375021_611e4a2d60c4f109713c5.png!small?1629375022661](https://image.3001.net/images/20210819/1629375021_611e4a2d60c4f109713c5.png!small?1629375022661)

接下来就是利用addAttribute()方法为将读取到的标签的所有属性赋予读取到的值喽。。。

![1629375021_611e4a2daaf33b8f72942.png!small?1629375022662](https://image.3001.net/images/20210819/1629375021_611e4a2daaf33b8f72942.png!small?1629375022662)

![1629375028_611e4a34e7cf165e18efc.png!small?1629375029838](https://image.3001.net/images/20210819/1629375028_611e4a34e7cf165e18efc.png!small?1629375029838)

![1629375036_611e4a3c978d68c217be6.png!small?1629375037519](https://image.3001.net/images/20210819/1629375036_611e4a3c978d68c217be6.png!small?1629375037519)

经过上面的代码调用就读取到了第一个开始标签<java>的属性及属性值

读取完第一个开始标签<java>后，接下来仍然是调用startElement()方法来读取第二个标签<Object>（SAX模式读取xml文件就是将先利用startElement()读取所有开始标签，然后再调用endElement()读取所有结束标签）

![1629375057_611e4a51d67dd6f1a2bb8.png!small?1629375058926](https://image.3001.net/images/20210819/1629375057_611e4a51d67dd6f1a2bb8.png!small?1629375058926)

![1629375065_611e4a59353f39117b63b.png!small?1629375066148](https://image.3001.net/images/20210819/1629375065_611e4a59353f39117b63b.png!small?1629375066148)

读取结束标签是用endElement()方法

![1629375074_611e4a623f9a2c87db59e.png!small?1629375075130](https://image.3001.net/images/20210819/1629375074_611e4a623f9a2c87db59e.png!small?1629375075130)

endElement方法中将调用getValueObject方法获取每一个标签所产生的对象对应的ValueObject实例

![1629375090_611e4a72ae092230fae89.png!small?1629375091617](https://image.3001.net/images/20210819/1629375090_611e4a72ae092230fae89.png!small?1629375091617)

![1629375099_611e4a7b722f776c07702.png!small?1629375100425](https://image.3001.net/images/20210819/1629375099_611e4a7b722f776c07702.png!small?1629375100425)

以上代码就是XMLDecoder()调用readObject()方法反序列化获取student对象的较详细的过程了。。。

那么，根据对上面代码的分析，我们可以发现在准备阶段java给这类反序列化过程赋予了无限制权限，并且在利用endElement()方法读取闭合结束标签的时候，利用getValueObject()方法获取了每对标签中定义的valueObject实例即读取了student对象的属性值，就完成了反序列化的过程。。。

那么DocumentHandler都可以读取哪些类型的标签呢？在其构造方法中已经写的明明白白：

![1629375136_611e4aa0a35f5cfb02c6b.png!small?1629375137750](https://image.3001.net/images/20210819/1629375136_611e4aa0a35f5cfb02c6b.png!small?1629375137750)

##  **漏洞复现过程**

![1629375221_611e4af5bc19775295b9c.png!small?1629375222719](https://image.3001.net/images/20210819/1629375221_611e4af5bc19775295b9c.png!small?1629375222719)

环境搭建成功！！！

  1. ### 初步判断

访问http://ip:7001/wls-wsat/CoordinatorPortType，存在下图则说明存在漏洞：

![1629375250_611e4b1216d930f5ad2e0.png!small?1629375251090](https://image.3001.net/images/20210819/1629375250_611e4b1216d930f5ad2e0.png!small?1629375251090)

  2. ### 尝试抓取数据包，并向其中插入XML文档(test.txt)--构造POST数据包

将Content-Type修改为：text/xml, 并添加Cache-Control为no-cache

再写入text.txt文件的xml内容

![1629375274_611e4b2a8f705a1a4639a.png!small?1629375275513](https://image.3001.net/images/20210819/1629375274_611e4b2a8f705a1a4639a.png!small?1629375275513)

### 3.构造POST包进行测试，写入txt

![1629375486_611e4bfed247ea889b381.png!small?1629375487813](https://image.3001.net/images/20210819/1629375486_611e4bfed247ea889b381.png!small?1629375487813)

  4. ### 访问txt，页面显示如下，说明确实存在该weblogic XMLDecoder漏洞

![1629375508_611e4c14b3890da36a287.png!small?1629375509600](https://image.3001.net/images/20210819/1629375508_611e4c14b3890da36a287.png!small?1629375509600)

## 总结

感谢飞速发展的互联网。。。让我在参考了各路大佬的文章后，总结出这么一篇自己觉得还能看的文章出来。。。参考的文章比较丰富，就不一一感谢了！！哈哈哈哈哈哈

好了，这篇关于weblogic反序列化漏洞原理分析和挖掘方式就分享到这里。。。大家下去记得做实验哦，如果实验搭建过程中遇到什么问题也可以交流哦。。。总之，还是一定要亲自动手去看实验现象，这样才能真正的理解原理。。加油，大佬们！！！

![1629376071_611e4e473e1529060876b.png!small?1629376072358](https://image.3001.net/images/20210819/1629376071_611e4e473e1529060876b.png!small?1629376072358)

