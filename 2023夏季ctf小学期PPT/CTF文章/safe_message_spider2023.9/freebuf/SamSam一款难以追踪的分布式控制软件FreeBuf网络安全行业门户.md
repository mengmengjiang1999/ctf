![1.png](https://image.3001.net/images/20180622/15296049533437.png!small)

**近期，SamSam勒索软件频繁出现在了很多[高调的网络攻击活动](https://www.wired.com/story/atlanta-ransomware-samsam-will-strike-again/)中。自其出现以来，SamSam经历了大量的改进，并增加了很多额外功能，虽然这些功能并没有让SamSam变得更加危险，但它们增加了SamSam的检测难度，而且这个难度一直随着时间的推移而增加。**

在对近期样本的分析过程中，研究人员发现这款勒索软件的Payload一直都是在运行时解密的，这也是这款勒索软件最显著的特点，这种加密Payload机制也表明了为何我们难以去定位实际的Payload。

新版本SamSam和旧版本之间的对比如下：

> 1\. 所使用的模块；
>
> 2\. 交互方式；

接下来，我们将跳过旧版本的SamSam，直接对新版本SamSam代码进行分析，并通过一些简单的对比来了解SamSam的进化过程。

## 近期的SamSam样本分析

SamSam的攻击活动由五个部分组成，其中的四个部分是实际的文件，而第五个部分涉及到用户的直接参与。

![2.png](https://image.3001.net/images/20180622/15296049657030.png!small)

第一个部分是一个batch文件，其中包含了勒索软件的设置信息，它也是攻击者唯一一个需要手动执行的部分。它会运行一个.NET可执行文件，并对已加密的stub文件进行解密。攻击者在受感染主机中执行bat文件时，需要在命令行中输入密码作为执行参数，这个密码会在攻击链中向下传递，直到.NET文件用其实现解密为止。在旧版本中，这个bat文件似乎并不在攻击链中，攻击者需要直接执行.NET组件。

这部分的详细信息如下所示：

![3.png](https://image.3001.net/images/20180622/15296049792276.png!small)

在这里，mswinupdate就是这部分的“runner”（暂时这样命名），这个runner就是文件的加载器，这是一个
.NET可执行文件，它主要负责对勒索软件的Payload进行解密。

接下来，你会看到“SET password”那一行，它负责从命令行参数中提取密码信息。

这也解释了为什么对主Payload的分析会如此之难，这个密码的输入是不需要文件参与的，而且想要完整手动复现攻击场景也是非常难得，因为攻击者会在攻击完成之后将其中的某些文件和日志记录删除。

![4.png](https://image.3001.net/images/20180622/15296049876565.png!small)

上面是攻击链的第二个部分，runner，也就是Payload的解密器和启动器，这个文件没有经过混淆处理，而且功能也非常简单。它会搜索目录中包含.stubbin后缀的文件，而这个文件是攻击者存放在目标设备中的。stubbin文件就是加密后的勒索软件，它会从文件中读取出字节数据并立刻删除原始文件。文件内容使用了AES加密，所以即使拿到了stubbin文件我们也没办法对其进行分析，因为它还是需要攻击者手动输入密码。

Stubbin文件会调用assembly.Load函数，并动态加载一个.NET文件。函数需要接收一个参数来作为解密器的输出方法，这也意味着它能够动态实现stub文件解密、转换为对应的PE并加载文件。密码在bat文件的args[0]中输入，其中Arg_4E_0为加密字节流。

在新版本SamSam的第三个部分中，解密代码包含了一个单独的DLL文件，但在旧版本中，所有内容都包含在runner之中，因此旧版本总共也只有三个组件，而不像新版本那样拥有四个组件。

下面是解密代码：

![5.png](https://image.3001.net/images/20180622/15296050086547.png!small)

查看程序代码后你将会发现下列内容：

![6.png](https://image.3001.net/images/20180622/15296050212860.png!small)

第四个部分如下所示，即加密后的恶意软件Payload-*.stubbin：

![7.png](https://image.3001.net/images/20180622/15296050308854.png!small)

## SamSam的目标：实施有针对性的攻击

在本文的分析过程中，我们讨论了很多关于密码方面的东西（由攻击者手动输入），这也是SamSam勒索软件活动中非常关键的一点。在分析时，由于我们不知道密码，所以我们无法分析勒索软件的源码。而且需要注意的是，我们甚至都无法在测试设备上运行SamSam，因此这也意味着只有攻击者本人才能实施SamSam攻击。

这跟之前的很多勒索软件或恶意软件都不同，而且SamSam的感染范围不仅没有Wildfire大，而且它甚至都不能够实现自动传播。

实际上，如果你不小心下载并执行了这款勒索软件的话，你也不用担心，因为没有密码它的Payload也运行不起来。可能大家已经发现了，这款勒索软件只有一个目的：进行有针对性的网络攻击。开发人员明显是要选择特定攻击目标的，对于勒索软件来说这就非常有意思了。

## 入侵威胁指标IoC

BAT文件

    
    
    9C8AD4147F5CBDDA51317A857D75720C84BDDB16338DABE374A3E60C64C2F0DE

加密DLL

    
    
    DA9C2ECC88E092E3B8C13C6D1A71B968AA6F705EB5966370F21E306C26CD4FB5

Runner

    
    
    738C95F5BFE63A530B200A0D73F363D46C5671C1FCBB69C217E15A3516501A86

Stubbin

    
    
    594B9B42A2D7AE71EF08795FCA19D027135D86E82BC0D354D18BFD766EC2424C

### 参考资料

SophosLabs的SamSam样本分析白皮书：【[点我获取](https://www.sophos.com/en-us/medialibrary/pdfs/technical-papers/samsam-ransomware-chooses-its-targets-carefully-wpna.aspx)】

 *** 参考来源：[malwarebytes](https://blog.malwarebytes.com/threat-analysis/2018/06/samsam-ransomware-controlled-distribution/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

