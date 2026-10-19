***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

![1.png](https://image.3001.net/images/20180305/15202403806367.png!small)  

## 概述

**在近期的一次内部渗透测试中，我们需要利用一个Java两级反序列化漏洞。在这篇文章中，我们将告诉大家如何改造Nessus插件，因为该插件原本只能利用一个现有的RCE漏洞，但我们将教会大家如何通过该插件来利用这个漏洞，并在我们的攻击服务器上获取到反向shell。**

可能很多同学都知道Java反序列化漏洞，但是两级反序列化漏洞却是近期才提出来的，而且跟Java反序列化漏洞有一些细微的差别。网上有很多关于Java反序列化漏洞的资源，所以我们就不再重复造轮子了，我们待会只介绍这两种漏洞之间的区别。

本文的主要目的是要告诉大家如何武器化Nessus插件，不过别担心，这里不需要涉及到逆向工程方面的知识。

我们所要利用的漏洞存在于一个Adobe ColdFusion Flex BlazeDS实例中，Flex使用了AMF（(Action Message
Format)，它是Flash与服务端通信的一种常见的二进制编码模式，而这个实例使用了AMF3，这种格式不仅提供了很多新的功能，而且还包含了很多安全漏洞。

## Nessus

在Nessus的一份报告中，我们找到了如下所示的漏洞：

  
![2.png](https://image.3001.net/images/20180305/15202403977855.png!small)  

在渗透测试的初始阶段，我们可以利用自动化工具/扫描器来寻找到简单的漏洞或过期的软件。从图中我们可以看到，Nessus可以通过发送自定义的Java对象来利用一个Java反序列化漏洞。也就是说，Nessus理应能够利用我们的目标漏洞。

### 可用的工具

请大家记住，我们要进行的是二级反序列化攻击，所以我们首先得满足下列要求：

1\. 需要设置一个监听器，并携带我们的二级Payload。这个Payload可以是某种Empire one-liner，或其他你想要执行的远程命令。

2\.
需要启动主Payload，其中包含的Payload可以让一个让目标服务器调用我们的监听器并获取二级Payload。在实际的漏洞利用过程中，我们并不是要通过命令来让目标用户下载Payload，如果要这样的话我们不就已经得到了一个RCE漏洞了吗？

虽然Ysoserial中包含了很多适用于该场景的工具，比如说JRMPListener和Marshalsec之类的，但是既然Nessus已经可以利用这种漏洞了，那我们为什么不用“现成”的呢？

## Nessus Payload

这一次渗透测试让我重新认识了Nessus，其实它不仅仅只是一款简单的漏洞扫描工具。Nessus使用了Nessus攻击脚本语言（NASL）来编码渗透测试插件，而这些插件代码是可以直接在系统中查看到的。

接下来，我们一起看看一看ColdFusion
AMF反序列化插件，该插件所在目录为“/opt/nessus/lib/nessus/plugins/”。下面给出的是该脚本中最有意思的部分，注意其中的“amf_payload”：

  
![3.png](https://image.3001.net/images/20180305/15202404182657.png!small)  

现在你的第一反应可能是：“我们只需要修改这个脚本，并修改cb_address（回调地址）就可以了”。其实并没有那么简单，因为在每一个插件的头部，Nessus都会进行签名，如果代码发生了改变，Nessus就无法使用该脚本了。下面给出的是签名样本：

  
![4.png](https://image.3001.net/images/20180305/15202404259537.png!small)  

其实，我们可以直接用Python直接重写一次，这里我们可以使用一款名叫Marshalsec的AMF3
Payload生成工具。但是出于某种原因，生成的Payload并不能直接使用。后来我才发现，这个工具只能起到一定的辅助作用，下面给出的是该工具的输出结果：

  
![5.png](https://image.3001.net/images/20180305/15202404329253.png!small)  

有可能是我打开的方式不对，但是我拿这个Payload跟Nessus
Payload进行对比之后，我发现Marshalsec的输出数据缺少了一些东西。下面给出的是两者之间的区别：

  
![6.png](https://image.3001.net/images/20180305/15202404468934.png!small)  

首先，Nessus Payload代码要长一些，而且更加完整。Marshalsec Payload开头为“0a0733”，这个数据可以在Nessus
Payload代码的三分之一处找到。其次，这两者的结尾部分是完全不同的。我们可以看到，Marshalsec
Payload中“000004d2”相当于Nessus
Payload中的“mkdword(listening_port，端口1234)”。随后，Marshalsec写入的是“ffffffff”，而Nessus写入的是“f96a767b”。

Marshalsec可以帮助我们生成Payload的中间部分，而我们可以直接从Nessus
Payload中直接抓取Payload代码中的“头”和“尾”，并将这两个部分和中间部分组合起来生成最终的Payload。

## 漏洞利用

首先，我们需要在攻击系统中设置两个监听器，这里可以使用JRMPListener+Empire Payload+
yososerial。然后，我们还需要一个Empire监听器来处理Empire代理的回调信息。

  
![7.png](https://image.3001.net/images/20180305/1520240466164.png!small)  

接下来，我们通过整合Nessus/Marshalsec payload来创建一个新的Python脚本：

  
![8.png](https://image.3001.net/images/20180305/15202404759908.png!small)  

在运行了漏洞利用代码之后，JRMPListener会收到通信连接，并用二级漏洞利用Payload予以响应：

  
![9.png](https://image.3001.net/images/20180305/15202404888839.png!small)  

接下来，Empire监听器将会收到“代理任务完成”等提示信息。

  
![10.png](https://image.3001.net/images/20180305/1520240498842.png!small)  

### 总结

我们在这篇文章中介绍了如何利用Nessus插件来帮助我们开发漏洞利用代码，Nessus提供的插件可以帮助我们轻松实现远程代码执行（RCE），但是它也有一定的功能限制。希望这篇文章可以帮助大家站在巨人的肩膀上看世界。

AdobeColdfusion BlazeDS Java Object Deserialization
RCE：【[下载地址一](https://github.com/depthsecurity/coldfusion_blazeds_des)】【[下载地址二](https://www.exploit-db.com/exploits/43993/)】

 *** 参考来源：[depthsecurity](https://depthsecurity.com/blog/weaponization-of-nessus-plugins)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

