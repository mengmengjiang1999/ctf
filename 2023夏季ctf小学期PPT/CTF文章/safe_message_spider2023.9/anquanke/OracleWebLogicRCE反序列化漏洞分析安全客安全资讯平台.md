# Oracle WebLogic RCE反序列化漏洞分析

阅读量 **430485**

发布时间 : 2018-10-20 03:30:58

 **x**

##### 译文声明

本文是翻译文章，文章原作者 Zhang Zhiyi，文章来源：projectmoon.pw

原文地址：<https://blogs.projectmoon.pw/2018/10/19/Oracle-WebLogic-Two-RCE-Deserialization-Vulnerabilities/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t01dad5e3157726eeb6.jpg)

Author: Zhiyi Zhang of 360 ESG Codesafe Team

## 前言

Oracle 官方在7月份发布[关键补丁更新](https://www.oracle.com/technetwork/security-advisory/cpujul2018-4258247.html)之后，我在当月随后陆续提交了一些weblogic的不同类型漏洞，由于官方并
没有全部修复完成，本次的补丁修复了我报送的6个漏洞，其中有3个漏洞由于某些原因合并成1个CVE，本文针对10
月份这次补丁修复的其他两个漏洞进行简单分析。其中CVE-2018-3245是补来补去一直没有修好的Weblogic JRMP反
序列化漏洞，另一个漏洞CVE-2018-3252是DeploymentService组件的反序列化漏洞。

## CVE-2018-3252 (DeploymentService Deserialization via HTTP)

当我在阅读DeploymentService这个servlet的时候，在doPost函数中看到用于对通过HTTP方式提交的POST数据处理的核心函数internalDoPost。

![](https://blogs.projectmoon.pw/2018/10/19/Oracle-WebLogic-Two-RCE-Deserialization-Vulnerabilities/1.png)

可以看到，var4是通过HTTPHeader中的wl_request_type获取。然后进入不同的处理逻辑中。这里先跟进handleDataTransferRequest函数。

![](https://blogs.projectmoon.pw/2018/10/19/Oracle-WebLogic-Two-RCE-Deserialization-Vulnerabilities/2.png)

在上图箭头所指向的地方，程序对var9进行了反序列化，而var9是通过DeploymentObjectInputStream的构造函数生成，其中函数中的参数都是我们可控制的。

再来看handleDeploymentServiceMessage函数，基本逻辑大致相同，也是对DeploymentObjectInputStream对象的反序列化。

![](https://blogs.projectmoon.pw/2018/10/19/Oracle-WebLogic-Two-RCE-Deserialization-Vulnerabilities/3.png)

看到这里，心里隐隐觉得这个洞应该很好用，还是通过HTTP的方式。细心的同学可能发现，这里我们分析的每个函数都有一个参数是AuthenticatedSubject对象。这就是这个漏洞鸡肋的地方，需要用户认证。有兴趣的同学可以深入分析一下weblogic的用户认证机制，试试bypass🤪。具体函数请参考authenticateRequest，下图关于该函数有做删减，方便大家看到weblogic提供的两种认证方式。

![](https://blogs.projectmoon.pw/2018/10/19/Oracle-WebLogic-Two-RCE-Deserialization-Vulnerabilities/4.png)

这里我们使用username/password的用户认证方式验证PoC。

![](https://blogs.projectmoon.pw/2018/10/19/Oracle-WebLogic-Two-RCE-Deserialization-Vulnerabilities/5.png)

## CVE-2018-3245(JRMP Deserialization via T3)

在拿到7月份补丁后迅速去diff了一下，果然不出所料，针对JRMP反序列化修复的方式依旧是增加黑名单。黑名单package(DEFAULT_BLACKLIST_PACKAGES)新增java.rmi.activation
sun.rmi.server;黑名单class(DEFAULT_BLACKLIST_CLASSES)新增java.rmi.server.UnicastRemoteObject
java.rmi.server.RemoteObjectInvocationHandler。

    
    
    1
    2
    3
    4
    5
    6
    7
    8
    9

|

    
    
     private static final String[] DEFAULT_BLACKLIST_PACKAGES = {
    "org.apache.commons.collections.functors", "com.sun.org.apache.xalan.internal.xsltc.trax",
    "javassist", "java.rmi.activation", "sun.rmi.server" };
    
      private static final String[] DEFAULT_BLACKLIST_CLASSES = {
    "org.codehaus.groovy.runtime.ConvertedClosure",
    "org.codehaus.groovy.runtime.ConversionHandler", "org.codehaus.groovy.runtime.MethodClosure",
    "org.springframework.transaction.support.AbstractPlatformTransactionManager",
    "java.rmi.server.UnicastRemoteObject", "java.rmi.server.RemoteObjectInvocationHandler" };  
  
---|---  
  
其实如果认真分析过之前相关漏洞和补丁的同学，都能够很容易找到绕过的方式。  
正如之前和lpwd讨论的所谈到，只要满足继承java.rmi.server.RemoteObject,且不在黑名单之中的类对象。
这里我通过ReferenceWrapper_Stub这个类对象绕过。

![](https://blogs.projectmoon.pw/2018/10/19/Oracle-WebLogic-Two-RCE-Deserialization-Vulnerabilities/6.png)

验证:

![](https://blogs.projectmoon.pw/2018/10/19/Oracle-WebLogic-Two-RCE-Deserialization-Vulnerabilities/7.png)

WebLogic Console Log:

    
    
    1
    2
    3
    4
    5
    6
    7
    8
    9
    10
    11
    12

|

    
    
     java.lang.ClassCastException: com.sun.jndi.rmi.registry.ReferenceWrapper_Stub cannot be cast to
    weblogic.rjvm.ClassTableEntry.
    java.lang.ClassCastException: com.sun.jndi.rmi.registry.ReferenceWrapper_Stub cannot be cast to
    weblogic.rjvm.ClassTableEntry
        at weblogic.rjvm.MsgAbbrevInputStream.readClassDescriptor(MsgAbbrevInputStream.java:410)
        at
    weblogic.utils.io.ChunkedObjectInputStream$NestedObjectInputStream.readClassDescriptor(ChunkedO
    bjectInputStream.java:284)
        at java.io.ObjectInputStream.readNonProxyDesc(ObjectInputStream.java:1564)
        at java.io.ObjectInputStream.readClassDesc(ObjectInputStream.java:1495)
        at java.io.ObjectInputStream.readNonProxyDesc(ObjectInputStream.java:1582)
        Truncated. see log file for complete stacktrace  
  
---|---  
  
## 总结

可能目前谈到weblogic漏洞的挖掘，马上想到的是反序列化漏洞。依照之前多次补丁更新的迹象，虽然可能还是会
有新的绕过，但是能够使用的gadget越来越少，会让漏洞的利用难度提高很多。其实，我在阅读weblogic代码的过
程中发现，很多在java中常见的漏洞:文件下载、上传、SSRF、XXE、DoS…这些漏洞也都存在，并且利用简单方便。
或许，试着找些其他类型的漏洞配合使用，也是可以达到远程代码执行的效果。

## 参考

[Critical Patch Update – October
2018](https://www.oracle.com/technetwork/security-advisory/cpuoct2018-4428296.html)  
[Ysoserial](https://github.com/frohoff/ysoserial)

感谢你的阅读，文中如有问题，可以通过[projectmoon.pw@gmail.com](mailto:projectmoon.pw@gmail.com)与我联系。

本文翻译自projectmoon.pw [原文链接](https://blogs.projectmoon.pw/2018/10/19/Oracle-WebLogic-Two-RCE-Deserialization-Vulnerabilities/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **安全客** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/162390](/post/id/162390)

安全客 - 有思想的安全新媒体

本文转载自: [projectmoon.pw](https://blogs.projectmoon.pw/2018/10/19/Oracle-WebLogic-Two-RCE-Deserialization-Vulnerabilities/)

如若转载,请注明出处： <https://blogs.projectmoon.pw/2018/10/19/Oracle-WebLogic-Two-RCE-Deserialization-Vulnerabilities/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [Weblogic](/tag/Weblogic)
  * [RCE](/tag/RCE)

 **+1** __17赞

 __收藏

![](https://p0.ssl.qhimg.com/t01546a096e83e700fe.jpg) 安全客

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

