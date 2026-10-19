## 写在前面的话

 **我在一次偶然的机会中了解了Koadic这款工具，于是我决定制作一个`“javascript rundll32
exploit”`的关键字组合，看看会出现什么。所以我开始了Koadic后期开发rootkit之路，学习Koadic可以参考Sean Dillon和Zach
Harding在Defcon上的[演示](a%20href=)。Koadic类似于[`PowerShell
Empire`](a%20href=)，拥有基于脚本的stager和植入设备功能。然而，关键的区别在于，Koadic依赖于受害者计算机上的JavaScript和VBScript。但如今安全团队更加关注在Windows事件日志中寻找不寻常的PS活动。我想这可以称为`JavaScript
Empire`。**

## 开始

在这篇文章中，我们将对Koadic的能力和架构做一个简单的介绍。Koadic有一个特点就是允许攻击者能够随时更改代码，来迅速适应新的环境。稍后我将在本系列文章中讨论这个问题，但是很明显，您需要将注意力从Windows事件日志转移到底层文件系统上。首先，我们在AWS环境中的一个Ubuntu实例上安装了[Github](a%20href=)上的软件。我们遇到了一些困难，但这很快就被解决了——重新安装了Koadic的Python模块。是的，Koadic的服务器端都是基于python的。为了完成工作，Koadic利用了Windows二进制代码，这些二进制代码会偷偷地引入远程JavaScript或VBScript。让我们假设`mshta
stager`(测试中使用的stager)是通过钓鱼邮件发送给受害者的。一旦激活，Koadic就会创造出`“zombie”`。这是他们对受害者机器的控制方式。

![1.jpg](https://image.3001.net/images/20180901/1535774726_5b8a100628336.jpg!small)

在一个实际的笔试场景中，第一个任务就是要解决who和where问题。输入`“info”`命令来查看基本参数是什么，然后相应地设置它们。

![2.jpeg](https://image.3001.net/images/20180901/1535774733_5b8a100da9134.jpeg!small)

## 第二步

一旦掌握了基础知识，就可以帮助您发现您所使用的Windows环境的完整限定域名(FQDN)。正如我们将看到的，您将需要域名离开最初被黑客入侵的计算机。为此，我需要通过将`cmd`参数设置为`GetHostByName（$
env：computerName）`来使用PowerShell。它是一个良性的`PS cmdlet`。

![3.jpg](https://image.3001.net/images/20180901/1535774740_5b8a101444216.jpg!small)

简而言之：Koadic内置支持获取重要的环境信息，当然还有运行shell命令填补空白的能力。顺便说一下，可以在Github
[主页](a%20href=)上找到所有命令的描述。

## 第三步

除非黑客运气爆炸，登陆的服务器上有数百万个未加密的信用卡号码，否则她需要跳到另一台计算机上。这样做的方法是获取域级凭据，最终找到具有提升权限的凭据，然后执行横向渗透。曾几何时，我写过如何使用`mimikatz`和`psexec`这样做。Koadic已经提供了一个基于`mimikatz`来从SAM存储器中检索凭证，另一个用于支持`psexec`。小提示：您必须将`psexec`可执行文件显式上传到受害者的计算机并设置路径名称。例如，要检索凭证，我运行了`implant/inject/mimikatz_dynwrapx`：

![4.jpeg](https://image.3001.net/images/20180901/1535774747_5b8a101b420ed.jpeg!small)

您可以看到NTLM哈希，如果需要，您可以离线破解。但是您还可以利用wdigest安全[漏洞](a%20href=)，获得纯文本密码。我不会在这篇文章中展示如何进行实际的横向移动，但您可以在下面看到`implant/pivot/psexec
below`的设置：![5.jpg](https://image.3001.net/images/20180901/1535774755_5b8a1023d0fb0.jpg!small)

## 最后的话

下次我将介绍如何创建一群僵尸网络。敬请期待!

 ***参考来源：[varonis](a%20href=)，由周大涛编译，转载请注明来自FreeBuf.COM**

