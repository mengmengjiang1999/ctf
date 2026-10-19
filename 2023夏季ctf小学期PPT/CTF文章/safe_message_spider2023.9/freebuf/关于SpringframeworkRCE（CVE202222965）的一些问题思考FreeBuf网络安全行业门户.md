## **引言**

千呼万唤始出来，在Spring
RCE漏洞在野曝光了一段时间后，Spring官方终于在3月31日发布了漏洞信息，在新版本v5.3.18和v5.2.20中修复了该漏洞，漏洞编号CVE-2022-22965。该漏洞的细节本篇文章就不详细分析了，这里想分享和解答一些有关这个漏洞的疑问。

##  **关于“只能成功复现一次”**

在初步进行漏洞研究和复现时，很多小伙伴遇到一个问题是文件写入只能进行一次，想要重复写入时发现无法成功，要重启服务器才能写入第二次。实际上这种现象是因为该漏洞本质上是一个由SpringBeans变量覆盖导致的文件写入漏洞，文件写入是通过tomcat的日志记录功能来实现的，tomcat的日志记录功能通过resources中的配置项来控制，修改之后的配置文件如下图所示，可以修改日志保存的文件名、后缀、路径等信息。

![](https://image.3001.net/images/20220406/1649208505_624cecb9b53bafa5fdaea.png!small)想要多次上传最简单的办法就是修改fileDateFormat属性，这是一个日期格式的字符串，最终会拼接到文件后缀里。图中最终保存的文件为/tmp/test/xxx111.jsp。

##  **关于“必须知道绝对路径”**

从本质上来说这条利用链是属于任意文件上传的利用链，最好的上传方式是把webshell传到网站的web目录（其他传SSH私钥，自启动目录暂不在考虑范围）。

要知道目标站点web的根目录并不容易办到，最好是通过相对路径来传webshell。所有tomcat的相对路径起点都是tomcat安装目录（注意，不是启动目录tomcat/bin），web目录的相对路径都是webapps/项目名。这里比较麻烦的是要知道项目名，我们以目标站点路由/Spring_demo/hello来推测可能存在的上传路径。

1）整个路径/Spring_demo/hello都是路由，上传文件路径则是webapps/ROOT/。tomcat默认web目录。

2）Sping_demo是项目名，hello是访问路由，上传路径则是webapps/Spring_demo/。上传到当前项目名下。

3）前面两种都失败了，可以通过创建目录的方式来生成一个新的tomcat项目，上传路径是webapps/xxxx/（如果上传目录不存在，会新建目录）。默认情况下新建的目录可以直接访问/xxxx/你的shell.jsp。

##  **关于“写入文件会不断刷新内容”**

部分小伙伴提出利用成功之后生成的文件会不断写入新内容，存在影响系统业务的可能。写入新内容是因为我们的shell是日志文件，只要有http请求就会有记录。

要不想一直记录日志，可以通过修改tomcat配置文件，关闭日志记录功能，payload如下：

>
> class.module.classLoader.resources.context.parent.pipeline.first.enabled=false

![](https://image.3001.net/images/20220406/1649208594_624ced12234dfa1e3a1c4.png!small)

##  **关于“为什么会保留class引用”**

相信不少人是通过某篇“不可描述”的pdf文档逐渐了解了漏洞细节的，作者上来就是一个原神海乱鬼的logo让我印象非常深刻。

![](https://image.3001.net/images/20220406/1649208615_624ced279396ca684440d.png!small)这篇文章的作者一直有个疑问是为啥参数绑定过程中会保留一个POJO的class引用。

![](https://image.3001.net/images/20220406/1649208639_624ced3f134d7cbdfb2f9.png!small)

![](https://image.3001.net/images/20220406/1649208989_624cee9d66cba1db66ff4.png!small)

本想给作者的github上留个言，但发现作者github已经关掉了，本人大概率也已“加入肯德基豪华午餐”。有一说一《网络产品安全漏洞管理规定》大家一定要牢记，在网络产品提供者提供网络产品安全漏洞修补措施之前不应该发布漏洞相关信息。

这里只能帮作者云解答一下了。在java中任何一个类均继承自Object类，Object类中就存在getClass方法，如下图所示。这其实也就是反射获取类的class对象的方式，所以所有的类中都有class字段。

![](https://image.3001.net/images/20220406/1649208657_624ced5192e777bdecd55.png!small)也可以通过getPropertyDescriptors方法来查看bean类的全部字段。name是类自带的，class是大家都有的。

![](https://image.3001.net/images/20220406/1649208685_624ced6d58bafbf07f51b.png!small)

##  **关于“随便编码就能绕过waf”**

在漏洞排查和修复期间，一般给的WAF防护规则建议是拦截诸如“class.*”
、“Class.*”、“*.Class.*”、“*.Class.*”的字符串。从笔者自测的情况来看，这个规则还是很难被绕过的，当然不排除有大佬有比较牛逼的bypass姿势。

但是网传的“随便编码就能绕过waf”肯定是有问题的，最开始自测的时候也发现似乎空格换行啥的随便加一加就能绕过。例如我们访问一个这样的请求，在“class”和“.”之间添加一个空格，看上去的确是文件写入成功了：

![](https://image.3001.net/images/20220406/1649208717_624ced8da63347e9b6915.png!small)当时也是很意外java调用类属性的方式居然这么不严格，但后面发现实际上是随便加什么样的字符串都能写入成功：

![](https://image.3001.net/images/20220406/1649208735_624ced9fde764f0fd8b1b.png!small)造成这个现象的原因也是因为这个洞本质上是个日志配置文件篡改的洞，在首次篡改成功后这条配置项就已经有了，下次请求即使失败了也会保留原有的记录。即使传入参数已经报错了，但是不影响后面的执行。例如这里我把写入改了一下，发现实际上还是之前的数据：

![](https://image.3001.net/images/20220406/1649208761_624cedb9e023ce07b8717.png!small)

因此这种现象很容易会被误以为绕过了waf，Unicode的编码也是同理，实测是无法利用的。事实上即使unicode编码能解析，绝大多数waf也是能够拦截的。一个正常的waf在normalize阶段一定会对unicode这种常见编码进行预处理，这个在上次分析log4j漏洞绕过的时候就提过，详情可以参考：

[Log4j2远程代码执行漏洞检测和防护策略研究](https://mp.weixin.qq.com/s?__biz=MzkzNjMxNDM0Mg==&mid=2247483712&idx=1&sn=900376b16fc2c928d111063184223daa&chksm=c2a1d5c9f5d65cdf6a7a98cf0e6a6301032cc839acee355a4653a91551ad92d45c5b4adee683&token=1953861836&lang=zh_CN&scene=21#wechat_redirect)

除了unicode的外，waf不太好预处理的是ibm等不太常见的编码方式，因为种类太多了无法去一一解析，一般都选择无脑把charset给拦截了，详情可以参考：

[编码导致的WAF安全性研究﻿](https://mp.weixin.qq.com/s?__biz=MzkzNjMxNDM0Mg==&mid=2247484127&idx=1&sn=f06161d87e1842909e93c8148186b2d3&chksm=c2a1d656f5d65f4000c9e8e1335705f8464d642efb200668c0160ad5edf101c4803ff9ab43e1&token=1953861836&lang=zh_CN&scene=21#wechat_redirect)

虽然目前没有比较好的直接绕过class.*的方式，但是如果规则写的比较长还是会有一定问题。很多waf厂商考虑到直接拦截class.*太暴力了，会造成茫茫多误报，于是把拦截的关键字给加长了。例如我看有的厂商给的waf规则建议为检测“class.module.classLoader.resources.context.parent.pipeline.first”字符串。事实上检测规则加长之后我们就有更多的利用链可以找了，像上述规则就可以直接通过class.module.classLoader.resources.context.resources.context.parent.pipeline.first.pattern这种方式绕过，如图所示。效果和原来的是一样的，只是路径不一样。

![](https://image.3001.net/images/20220406/1649208787_624cedd3e76b325f0282f.png!small)

##  **关于“其他利用链”**

目前已知的是tomcat写日志文件的利用链，至于是否有其他更直接的利用链大家可以自行研究。但是从spring的修复方式来看（spring把class下除name以外的所有属性都加入“全家桶”了），修复之后Class下面的利用链应该都凉凉了。

![](https://image.3001.net/images/20220406/1649209032_624ceec85a9d590884d3c.png!small)

##  **关于“漏洞影响范围”**

首先漏洞是个非常棒的漏洞，蚂蚁安全团队也算是国内java安全的顶流了，个人也是非常崇拜。但就漏洞影响面而言，感觉还是被大家过于夸大了。从目前已知的利用链来看，需要java9以上才会触发，这就一杆子去掉太多集成化部署的系统了，毕竟大家普遍还是以java8为主流版本。其次SpringMVC加jdk9这个搭配就挺不伦不类的，并且还需要使用spring的参数绑定的路径才能触发漏洞，因此并没有想象中的那么“核弹级”。  
 **漏洞自检工具**

文末附一个自研的漏洞自检工具，不知道在用系统是否存在漏洞的可以在本地自查

[https://github.com/webraybtl/springcore_detect﻿](https://github.com/webraybtl/springcore_detect)

