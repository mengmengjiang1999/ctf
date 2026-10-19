# 【技术分享】如何攻击Java反序列化过程

阅读量 **271969**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-08-17 13:58:01

 **x**

##### 译文声明

本文是翻译文章，文章来源：nickbloor.co.uk

原文地址：<https://nickbloor.co.uk/2017/08/13/attacking-java-deserialization/>

译文仅供参考，具体内容表达以及含义原文为准。

****

****

译者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**一、前言**

****

现在反序列化（deserialization）漏洞早已不是新鲜事物（如这几处参考资料[[1]](https://heine.familiedeelstra.com/security/unserialize)[[2]](http://www.pwntester.com/blog/2013/12/16/cve-2011-2894-deserialization-spring-rce/)[[3]](https://foxglovesecurity.com/2015/11/06/what-do-weblogic-websphere-jboss-jenkins-opennms-and-your-application-have-in-common-this-vulnerability/)[[4]](https://www.insomniasec.com/downloads/publications/Practical%20PHP%20Object%20Injection.pdf)），但与其他类别漏洞相比，反序列化漏洞的利用过程涉及更多方面的因素。在应邀对客户进行渗透测试时，我成功利用Java反序列化漏洞获得了某台服务器的权限，利用这台服务器，我获得了数十台服务器的root访问权限，这些服务器横跨多个数据中心，部署了各种预生产以及生产环境。在之前多次渗透测试中，安全人员都没有发现过这个漏洞，如果我之前没接触过Java序列化及反序列化方面的知识，我肯定也会错过这个漏洞。

在本文中，我会尝试理清大家对反序列化漏洞的一些误解及困扰，希望能通过工具的使用来降低反序列化漏洞利用的技术门槛。我主要针对的是Java语言，但所涉及的原理同样也适用于其他语言。此外，我会重点分析命令执行的利用方法，以保持主题的简洁性。

今年早些时候，我在[SteelCon](https://www.steelcon.info/)上讨论过这个话题，后面我还会在[BSides
Manchester](https://www.bsidesmcr.org.uk/)以及BSides
Belfast上讨论同一话题，此外，在今年的[44con](https://44con.com/)上，我会讨论另一个Java后门。

  

**二、序列化及反序列化**

****

简而言之，序列化就是将运行时的变量和程序对象转换为可被存储或传输形式的一种过程。反序列化是一个相反的过程，可以将序列化形式的数据转换回内存中的变量及程序对象。
**经过序列化的数据可以存储为文本格式的数据，如JSON或者XML，也可以存储为二进制格式的数据** 。包括 **C#** 、 **Java** 以及
**PHP**
在内的许多高级语言本身就支持数据序列化，操作起来非常便捷，使开发者不必自己去实现这一过程，大大减轻开发者的工作量。在本文中，我重点分析的是Java内置的序列化格式，但其他数据格式也可能面临类似的风险（大家可以参考Alvaro
Muñoz和Oleksandr Mirosh在Black Hat USA 2017以及Def Con
25上关于JSON攻击的[演讲](https://www.blackhat.com/us-17/briefings.html#friday-the-13th-json-attacks)来了解更多技术细节）。

**2.1 问题所在**

序列化和反序列化的应用本身并不存在问题。 **但当用户（或者攻击者）可以控制正在反序列化的数据时，问题则随之出现** 。比如，
**如果数据使用网络渠道投递给反序列化处理过程，那么当攻击者可以控制被反序列化的数据时，此时内存中的变量及程序对象就会受到一定程度的影响。随后，如果攻击者可以影响内存中的变量以及程序对象，与这些变量及程序对象有关的代码执行流程就会受到影响**
。我们来看一下Java反序列化的例子：

    
    
    public class Session { 
        public String username; 
        public boolean loggedIn;
        public void loadSession(byte[] sessionData) throws Exception { 
            ObjectInputStream ois = new ObjectInputStream(new ByteArrayInputStream(sessionData)); 
            this.username = ois.readUTF(); 
            this.loggedIn = ois.readBoolean(); 
            } 
        }

上述代码中，“loadSession”方法接受一个字节数组作为参数，反序列化一个字符串，将处理结果赋值给对象的“username”以及“loggedIn”属性。
**如果攻击者可以控制“sessionData”字节数组的内容，那么当该数组被传递给此方法时，攻击者就能控制对象的这些属性**
。这个Session对象的某个使用场景如下所示：

    
    
    public class UserSettingsController { 
        public void updatePassword(Session session, String newPassword) throws Exception { 
            if(session.loggedIn) { 
                UserModel.updatePassword(session.username, newPassword); 
            } else { 
                throw new Exception("Error: User not logged in."); 
                } 
            } 
        }

如果登录会话建立成功，那么会话所对应的那个用户的密码就会同步更新为输入的那个密码。这是“POP（Property-Oriented
Programming，面向属性编程）利用点”的一个简单示例，根据这段代码，我们可以利用对象的属性值来控制某些用户数据。

**2.2 面向属性编程**

当我们可以控制对象的属性值，并利用这些属性值影响代码的执行过程时，这一过程就称之为“面向属性编程（ **property-oriented
programming，POP** ）”。 **POP利用点指的是一个代码片段，我们可以修改某些对象的属性来影响这个代码片段，使其满足我们的特定需求**
。许多情况下，我们需要串联多个利用点才能形成完整的利用程序。我们可以将其看成高级ROP（return-oriented
programming，面向返回编程）技术，只不过ROP需要将某个值推送到栈上，而我们通过POP利用点可以将某些数据写入到文件中。

这里非常重要的一点是，反序列化漏洞利用过程不需要将类或者代码发送给服务器来执行。我们只是简单发送了类中的某些属性，服务器对这些属性比较敏感，通过这些属性，我们就能控制负责处理这些属性的已有代码。因此，
**漏洞利用成功与否取决于我们对代码的熟悉程度** ， **我们需要充分了解通过反序列化操作能被操控的那部分代码**
。这也是反序列化漏洞利用过程中的难点所在。

**2.3 有趣的利用点**

程序中任何地方都可能存在POP利用点，唯一的要求是，我们可以利用反序列化对象的属性来操控程序代码，且攻击者可以控制正在被反序列化的数据。还有一些利用点更值得我们注意，因为它们的执行过程预测起来更为方便。在Java中，可序列化的类可以定义名为“readObject”的一种方法，在反序列化过程中，这个方法可以用来执行某些特定的操作（比如支持向后兼容特性）。当该类所属的某个对象正在被反序列化时，可以用这种方法来响应这类事件。比如，当某个数据库管理器对象被反序列化到内存中时，利用这种方法可以自动化建立与数据库的连接。大多数Java序列化漏洞利用技术使用的正是readObject方法中的代码，因为反序列化过程中肯定会执行这些代码。

  

**三、利用反序列化漏洞**

****

为了利用反序列化漏洞，我们需要满足两个关键的要素：

我们需要一个入口点，通过这个入口点，我们可以将自定义的序列化对象发往目标来做反序列化处理。

我们可以通过反序列化过程操控的一个或多个代码片段。

**3.1 入口点**

为了识别入口点，我们可以查看应用的源代码，看哪里使用了“ **java.io.ObjectInputStream**
”这个类（特别是“readObject”这个方法），或者查看实现了“readObject”方法的那些可序列化的类。如果攻击者可以控制传递给ObjectInputStream的那些数据，那么这种数据也可以作为反序列化攻击的入口点。此外，如果我们无法获得Java源代码，我们可以查找存储在硬盘中的序列化数据，或者使用网络进行传输的序列化数据，只要我们知道具体要查找的内容即可。

Java序列化数据开头包含两字节的魔术数字，这两个字节始终为十六进制的0xAC ED。接下来是两字节的版本号。我只见到过版本号为5（0x00
05）的数据，但更早的版本可能也存在，并且未来可能会出现更高的版本号。这四个字节之后是一个或多个内容元素，每个内容元素的第一个字节应该在0x70到0x7E之间，用来标明内容元素的类型，以标识后续数据流所对应的具体结构。大家可以参考Oracle官方文档中关于对象序列化流协议的介绍来了解更多细节。

在识别Java序列化特征时，人们经常说要寻找4字节的特征序列： **0xAC ED 00 05**
，事实上某些IDS规则也是根据这个特征来识别此类攻击。在应邀对客户进行渗透测试时，我没有第一时间发现这四个特征字节，因为目标客户端应用在运行期间始终保持与服务端的连接，这四个特征字节只在序列化流刚创建时出现过一次。因此，IDS无法识别我的攻击行为，因为我的攻击payload没有在序列化流的头部出现，而是稍后才发送。

我们可以以ASCII形式导出数据，识别Java序列化数据，而无需依赖头部中的 **0xAC ED 00 05** 这四个特征字节。

Java序列化数据中最为明显的特征是导出数据中存在Java类名，比如“ **java.rmi.dgc.Lease**
”。在某些情况下，Java类名可能以另外一种形式出现，比如开头为“L”，结尾为“;”，并会使用斜杠来分隔命名空间以及类名（如“
**Ljava/rmi/dgc/VMID;**
”）。除了Java类名，根据序列化格式规范，还有其他一些常见的字符串可以作为特征字符串，比如“sr”可能代表某个对象（TCOBJECT），其后跟着对象的类描述（TCCLASSDESC），或者“xp”可能代表某个类的类注释的尾部（TCENDBLOCKDATA），这个类不存在对应的超类（TCNULL）。

识别出序列化数据后，我们需要识别数据中哪处偏移量能够注入我们的payload。目标需要调用“ObjectInputStream.readObject”才能反序列化及实例化某个对象（payload），也才能支持面向属性的编程，然而它可以先调用另一个ObjectInputStream方法，比如“readInt”，通过该方法从流中读取一个4字节长度的整数。readObject方法会从序列化流中读取以下内容类型：

    
    
    0x70 – TC_NULL
    0x71 – TC_REFERENCE
    0x72 – TC_CLASSDESC
    0x73 – TC_OBJECT
    0x74 – TC_STRING
    0x75 – TC_ARRAY
    0x76 – TC_CLASS
    0x7B – TC_EXCEPTION
    0x7C – TC_LONGSTRING
    0x7D – TC_PROXYCLASSDESC
    0x7E – TC_ENUM

在最简单的一种情况下，从序列化流中首先读取到的是一个对象，此时我们可以将payload直接插入4字节的序列化头部后面。我们可以检查序列化流的前5个字节，以识别这类场景。如果这5个字节的前4个字节为序列化头部（0xAC
ED 00 05），后面1个字节为上面列出的某个值，那么此时我们就可以在4字节序列化头部后发送我们的payload对象来攻击目标。

在其他情况下，4字节序列化头部后面最有可能跟着一个TCBLOCKDATA元素（0x77）或一个TCBLOCKDATALONG元素（0x7A）。前者由1个字节长的字段以及多个字节长的数据块构成，后者由4字节长的字段以及多个字节长的数据块构成。如果数据块后面跟着readObject支持的某个元素类型，那么我们就可以在数据块后面插入我们的攻击payload。

根据我在这一领域的研究成果，我编写了一个名为SerializationDumper的工具，利用这个工具，我们可以识别反序列化漏洞利用的入口点。这个工具可以解析Java序列化流，将序列化流以可视化的形式导出。如果数据流中包含readObject支持的某个元素类型，那么我们就可以使用某个payload对象来替换这一元素。工具的使用如下所示：

    
    
    $ java -jar SerializationDumper-v1.0.jar ACED00057708af743f8c1d120cb974000441424344 STREAM_MAGIC 
    - 0xac ed STREAM_VERSION 
    - 0x00 05 Contents TC_BLOCKDATA 
    - 0x77 Length - 8 
    - 0x08 Contents 
    - 0xaf743f8c1d120cb9 TC_STRING 
    - 0x74 newHandle 0x00 7e 00 00 Length - 4 
    - 0x00 04 Value - ABCD - 0x41424344

根据上面的输出结果，我们发现数据流中包含一个TCBLOCKDATA，后面跟着一个TCSTRING，我们可以将TC_STRING替换为我们的攻击payload。

序列化流中的对象在加载时会被实例化，而不是当整个流完成解析时才会被实例化。根据这个事实，我们可以将攻击payload注入到某个序列化流中，而不用考虑去矫正序列化流剩余的那些数据。当任何验证操作执行时，或者当程序尝试从序列化流中读取更多数据时，攻击payload的反序列化以及执行操作早已完成。

**3.2 POP利用点**

识别出入口点后，我们就可以提供自己构造的序列化对象，以供目标进行反序列化处理，接下来我们需要找到POP利用点。如果我们可以访问源代码，那么我们可以查找“readObject”方法，以及在调用“ObjectInputStream.readObject”之后的那些代码，以判断是否存在可利用的点。

通常情况下，我们无法访问应用程序的源代码，但这并不能阻止我们利用反序列化漏洞，因为有许多第三方库可以作为我们的攻击目标。比如Chris
Frohoff以及Gabriel
Lawrence等研究人员已经在许多库中发现了POP利用链，并且发布了一个名为“ysoserial”的工具，这个工具可以生成攻击payload。这个工具大大简化了Java反序列化漏洞的攻击过程。

ysoserial中还包括许多利用链，因此下一步我们需要探索哪些利用链可以用来攻击目标。首先我们应该探索目标应用使用了哪些第三方库，或者是否存在信息泄露问题。如果我们知道目标应用使用了哪些第三方库，那么我们就可以选择合适的ysoserial
payload来尝试攻击。不幸的是，这些信息没那么容易获取，这种情况下，我们可以小心地遍历ysoserial中各种利用链，直到我们找到可以利用的那个点。这一过程需要异常小心，因为我们可能会触发无法处理的异常点，导致目标应用崩溃。这种情况下，目标应用会变得极其不稳定，如果目标应用无法处理不在预期范围内的数据或者格式错误的数据，那么即使使用nmap来扫描目标应用的版本也可能导致目标崩溃。

如果使用某个ysoserial
payload时，目标应用的响应为“ClassNotFoundException”，这种情况下，很有可能我们选择的利用点不能用于目标应用。如果目标应用出现“java.io.IOException”，同时返回“Cannot
run program”信息，那么很有可能我们选择的利用链适用于目标应用，但尝试执行的命令无法在目标服务器上执行。

ysoserial命令执行payload属于盲payload（blind
payloads）类型，不会返回命令的输出结果。由于使用了“java.lang.Runtime.exec(String)”语句，因此还存在其他一些限制。首先是不支持shell操作符，如输出重定向以及管道。其次是传递给payload命令的参数中不能包含空格，比如，我们可以使用

    
    
    nc -lp 31313 -e /bin/sh

，但我们不能使用

    
    
    perl -e ‘use Socket;…'

，因为传递给perl的参数中包含空格。幸运的是，网上有一个非常好用的payload编码器/生成器，可以绕过这些限制，大家可以访问<http://jackson.thuraisamy.me/runtime-exec-payloads.html> 来了解更多信息。

  

**四、亲自动手：DeserLab以及SerialBrute**

****

为了有效利用反序列化漏洞，理解序列化的原理以及反序列化漏洞利用的工作原理（如面向属性的编程原理）是非常重要的一件事情。与其他类型的漏洞相比，想做到这一点需要涉及许多方面的因素，因此找到一个可供练习的实验对象可以达到事半功倍的效果。除了发表这篇文章以外，我还发布了一个名为“DeserLab”的演示应用，该应用在Java序列化格式的基础上实现了一个自定义的网络协议。这个应用存在反序列化漏洞，大家可以根据本文介绍的技术来利用这个漏洞。

我编写了一个名为“SerialBrute”的工具，该工具由一对Python脚本构成，可以自动化使用ysoserial
payload来测试任何目标。第一个脚本为“SerialBrute.py”，可以重放TCP会话或者HTTP请求，并且能将payload注入到指定的位置；第二个脚本为“SrlBrt.py”，这是一个框架型脚本，在特殊情况下我们可以修改这一脚本来发送payload。这些脚本并没有考虑全部情况，因此需要谨慎使用，以免导致应用程序崩溃，但对我个人而言，我经常通过重放TCP会话，成功将ysoserial利用链注入目标应用中。

  

**五、总结**

****

感谢阅读本文。如果你对DeserLab感兴趣，欢迎多加使用。如果发现本文或我开发的工具中存在任何不足，需要进一步解释，欢迎通过推特向我反馈意见或者建议。

本文翻译自nickbloor.co.uk [原文链接](https://nickbloor.co.uk/2017/08/13/attacking-java-deserialization/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **興趣使然的小胃** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86641](/post/id/86641)

安全客 - 有思想的安全新媒体

本文转载自: [nickbloor.co.uk](https://nickbloor.co.uk/2017/08/13/attacking-java-deserialization/)

如若转载,请注明出处： <https://nickbloor.co.uk/2017/08/13/attacking-java-deserialization/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __1赞

 __收藏

![](https://p5.ssl.qhmsg.com/dm/200_200_100/t0104d1b8b4ca36e961.jpg) 興趣使然的小胃

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

