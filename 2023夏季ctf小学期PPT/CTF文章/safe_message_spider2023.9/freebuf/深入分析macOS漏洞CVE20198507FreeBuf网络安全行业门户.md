***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

![0.png](https://image.3001.net/images/20190712/1562861638_5d2760466ace8.png!small)

## 0x00 写在前面的话

 **2019年3月25日，苹果发布了macOS Mojave 10.14.4和iOS
12.2。这两个版本修复了大量的安全漏洞，其中包括QuartzCore（即CoreAnimation）中的[CVE-2019-8507](https://fortiguard.com/zeroday/FG-VD-19-001)。关于苹果更新的详细信息，可以参考这篇【[公告](https://support.apple.com/en-us/HT209600)】。**

在这篇文章中，我们将对macOS中的漏洞CVE-2019-8507进行详细分析。

## 0x01 漏洞概述

QuartzCore，也就是CoreAnimation，它是macOS和iOS用来创建动画场景的图形框架。CoreAnimation使用了一种独特的渲染模型，这种模型会以单独得进程来进行图形化操作。在macOS中，这个进程为WindowServer。在iOS中，这个进程为backboard。

QuartzCore中名为com.apple.CARenderServer的服务通常被称为CARenderServer。这个服务macOS和iOS中都有，可以直接从Safari沙盒环境中访问。但是，在macOS上，当QuartzCore在处理一个CA::Render::Decoder::decode_shape()函数中的图形对象时，就会发生内存崩溃（漏洞），这将导致应用程序意外终止运行。

下面给出的是Windows Server进程在遇到问题时的程序崩溃日志：

![1.png](https://image.3001.net/images/20190712/1562861649_5d27605112f2c.png!small)

![2.png](https://image.3001.net/images/20190712/1562861658_5d27605ac8bf1.png!small)

![3.png](https://image.3001.net/images/20190712/1562861664_5d2760601cac9.png!small)

![4.png](https://image.3001.net/images/20190712/1562861669_5d2760653194c.png!small)

## 0x02 PoC概念验证

接下来，我将演示如何使用我们的PoC来触发该漏洞。PoC代码如下所示：

![5.png](https://image.3001.net/images/20190712/1562861677_5d27606d7825b.png!small)

![6.png](https://image.3001.net/images/20190712/1562861683_5d27607342963.png!small)

![7.png](https://image.3001.net/images/20190712/1562861688_5d276078ed486.png!small)

原始Mach信息跟修改后的Mach信息对比如下图所示：

![8.png](https://image.3001.net/images/20190712/1562861697_5d27608167d1b.png!small)

通过对二进制源码进行分析后，我们发现只需要将偏移量0xB6的在一个字节由0x06修改为0x86，即可触发该漏洞。

如PoC代码所示，为了发送专门制作的Mach消息来触发该漏洞，我们首先需要发送一个msgh_id为40202的Mach消息，服务器中对应的处理器为_XRegisterClient，然后获取每一个新连接客户端的链接ID。

当我们获取到了连接ID之后，我们就可以在特质的Mach消息中偏移量0x2C的位置设置这个值了。最后，我们只需要发送这个Mach消息就可以触发该漏洞了。

## 0x03 漏洞分析

接下来，我们将使用LLDB来对漏洞进行动态调试，并分析导致漏洞产生的根本原因。注意：我们需要通过SSH模式来调试WindowServer进程。

通过对崩溃日志进行分析，我们可以获取到崩溃线程的堆栈回溯信息，并使用下列命令在CA::Render::Server::ReceivedMessage::run_command_stream函数处设置断点：

![9.png](https://image.3001.net/images/20190712/1562861705_5d276089a69b6.png!small)

conn_id的值可以通过在PoC代码的第86行设置断点来获取。

断点命中后，我们可以直接读取特制Mach消息的缓冲区数据，寄存器r13指向的就是特制的Mach消息。

![10.png](https://image.3001.net/images/20190712/1562861711_5d27608fcc958.png!small)

函数CA::Render::Decoder::decode_object(CA::Render::Decoder
*this,CA::Render::Decoder
*a2)可以用来解码这种类型的对象数据。开始于偏移量0x70000907dd52处的缓冲区数据为一个图片对象（绿色高亮标记）：

![11.png](https://image.3001.net/images/20190712/1562861717_5d276095bd3e1.png!small)

下面的代码段可以用来解析CA::Render::Decoder::decode_object函数中的图片对象数据：

![12.png](https://image.3001.net/images/20190712/1562861725_5d27609d1574f.png!small)

下图显示的是函数CA::Render::Image::decode()，我添加了部分注释方便大家查看：

![13.png](https://image.3001.net/images/20190712/1562861729_5d2760a19ca4c.png!small)

我们可以看到偏移量0x70000907dd52处的一个字节从0x06变为了0x86，所以变量v4现在等于0x86。接下来，程序会跳转到LABEL_31来执行其他分支代码，因为变量v4已经大于0x20了。在LABEL_31结尾处，程序会调用CA::Render::Texture::decode(CA::Render::Texture
*this,CA::Render::Decoder *a2)函数来继续处理后续数据。

![14.png](https://image.3001.net/images/20190712/1562861735_5d2760a73edda.png!small)

我们可以看到，它会调用函数CA::Render::Decoder::decode_shape来处理Shape对象数据。

接下来，我们看看其他的数据集是如何处理的。

![15.png](https://image.3001.net/images/20190712/1562861741_5d2760ad22451.png!small)

我们可以看到变量v2等于0x02它可以给缓冲区分配一个8字节大小的区域。最后，它会调用函数CA::Render::Decoder::decode_bytes来解码多个字节的数据。

![16.png](https://image.3001.net/images/20190712/1562861745_5d2760b1ed499.png!small)

导致该问题存在的根本原因在于CA::Render::Decoder::decode_shape函数缺乏限制验证机制。下面我们看看苹果方面是如何修复这个漏洞的：

![17.png](https://image.3001.net/images/20190712/1562861750_5d2760b6868e5.png!small)

## 0x04 总结

根据苹果的安全公告，这个漏洞只会影响macOS。该问题存在于QuartzCore中，由于缺少输入验证限制，因此当QuartzCore在处理一个CA::Render::Decoder::decode_shape()函数中的图形对象时，就会触发该漏洞。通过对比补丁代码，我们可以看到苹果通过增强输入验证机制修复了该问题。

## 0x05 受影响版本

    
    
    macOS Mojave 10.14.2
    
    macOS Mojave 10.14.3

## 0x06 漏洞分析环境

    
    
    macOS 10.14.2 (18C54) -MacBook Pro

## 0x07 时间轴

> 披露日期：2019年1月1日
>
> 通知日期：2019年1月3日
>
> 确认日期：2019年3月20日
>
> 发布日期：2019年3月25日

## 0x08 参考资料

> 1、 <https://support.apple.com/en-us/HT209600>
>
> 2、 <https://www.fortinet.com/blog/threat-research/detailed-analysis-of-> macos-ios-vulnerability-cve-2019-6231.html>

*** 参考来源：[fortinet](http://www.fortinet.com/blog/threat-research/detailed-analysis-mac-os-vulnerability-cve-2019-8507.html)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

