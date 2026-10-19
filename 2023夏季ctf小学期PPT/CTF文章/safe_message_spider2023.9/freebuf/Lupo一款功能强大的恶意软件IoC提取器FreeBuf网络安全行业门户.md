![](https://image.3001.net/images/20220506/1651848212_627534142a31424f5d5a0.png!small)  

## 关于Lupo

Lupo是一款功能强大的恶意软件IoC提取工具，可以帮助广大研究人员在恶意软件分析自动化的任务场景下实现恶意代码分析和调试。

在处理涉及恶意软件的安全事件时，我们经常会遇到这样的情况：由于许多因素（时间、技能、规模等），不可能对每一个案例都进行完整的手动分析，因此我们觉得需要自动化分析其中的一部分内容。

而Lupo的主要目标是
尽可能地自动化和加速这个过程。Lupo是一个动态分析工具，可以作为调试器的模块使用。这个工具的工作方式非常简单。将Lupo加载到调试器中，然后执行它。Lupo会分析恶意软件，并收集预定义的IOC，并将其写入磁盘上的文本文件。然后，您可以使用这些信息来遏制和消除恶意软件活动，或者简单地响应我们正在处理的安全事件。

该工具基于C++开发， 支持使用Windows调试框架来执行代码，该工具也可以作为插件与WinDbg结合使用，以帮助广大研究人员自动化实现恶意软件分析。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/malienist/lupo.git

然后在Visual Studio中选择加载所有的C++组件。

## 工具使用

该工具的使用非常简单，大致步骤如下：

点击【[ _这里_](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/debugger-download-tools)】下载WinDbg，然后将Lupo扩展拷贝到扩展目录下，文件默认路径为“sdk\samples\exts”子目录，扩展路径为“C:\Program
Files (x86)\Windows Kits\10\Debuggers\x86\winext”我们还可以通过下列命令来设置扩展路径 ：

    
    
    .extpath[+] [Directory[;…]]

运行调试工具，并开启调试会话。将进程绑定调试模式（即恶意软件），此时需要确保所有的虚拟机断开网络。然后执行恶意软件，当进程处于活动状态时，我们可以点击第一个断点来暂停进程：

![](https://image.3001.net/images/20220506/1651848232_627534283c01808fb69f6.png!small)

使用下列命令加载Lupo：

    
    
    .load lupo

![](https://image.3001.net/images/20220506/1651848243_627534337d690b403a302.png!small)

此时，可以使用下列命令来测试Lupo是否已经成功加载到调试器中：

    
    
    .chain

![](https://image.3001.net/images/20220506/1651848252_6275343cd24953e3f8505.png!small)

现在，我们就可以使用下列命令执行Lupo：

    
    
    lupo.go

![](https://image.3001.net/images/20220506/1651848261_6275344568fc861e31e6f.png!small)

Lupo此时将返回所有已加载的模块列表：

![](https://image.3001.net/images/20220506/1651848267_6275344b10ad7793f1f14.png!small)

所有的分析结果都将显示在控制台中，同时也会存储到磁盘中的一个文本文件内。文本文件的路径和文件名同样也会显示在终端窗口中：

![](https://image.3001.net/images/20220506/1651848272_627534504929c041ddbb1.png!small)

![](https://image.3001.net/images/20220506/1651848278_62753456569d5bd591a9d.png!small)

![](https://image.3001.net/images/20220506/1651848284_6275345c7ccfdefa75999.png!small)

除此之外，我们还可以在Lupo中选择其他的配合工具一起使用。

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/malienist/lupo/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **Lupo：** 【[ _GitHub传送门_](https://github.com/malienist/lupo)】

## 参考资料

> [ _https://medium.com/@vishal_thakur/lupo-malware-ioc-extractor-> cc86ae76b85d_](https://medium.com/@vishal_thakur/lupo-malware-ioc-extractor-> cc86ae76b85d)
>
> [ _https://medium.com/@vishal_thakur/introducing-ragno-ioc-> multiplier-9b75834353bb_](https://medium.com/@vishal_thakur/introducing-> ragno-ioc-multiplier-9b75834353bb)
>
> [ _https://github.com/vithakur/ragno_](https://github.com/vithakur/ragno)

