![](https://image.3001.net/images/20220925/1664115699_633063f3860f689f64666.png!small)

## 关于XLL关和XLL_Phishing

XLL是专门为Microsoft Excel设计的DLL，对于普通人来说，它们看起来就跟普通的Excel文档一样。

![](https://image.3001.net/images/20220925/1664115710_633063fe24ae4a38c88d5.png!small)

XLL为UDA提供了一个非常有吸引力的选项，因为它们由Microsoft
Excel执行，这是客户端网络中非常常见的软件。另一个好处是，由于它们是由Excel执行的，我们的Payload大概率会绕过应用程序白名单规则，因为受信任的应用程序（Excel）正在执行它。XLL可以用C、C++或C#编写，与VBA宏相比，它提供了更多的灵活性和功能（以及健全性），这进一步使它们成为了攻击者的一个理想选择。

当然，其缺点是XLL的合法用途很少，因此检查组织是否通过电子邮件和web下载以阻止该文件扩展名的下载应该是一个非常简单的实现方式。但不幸的是，许多组织已经落后多年，因此XLL在一段时间内将一直是一种可行的网络钓鱼方法。

有一系列不同的事件可用于在XLL中执行代码，其中最著名的是xlAutoOpen。完整列表如下：

![](https://image.3001.net/images/20220925/1664115717_633064052c2f13068cb54.png!small)

双击XLL后，用户会看到以下屏幕：

![](https://image.3001.net/images/20220925/1664115724_6330640c6dcce8bcd2c06.png!small)

这个对话框就是用户和代码执行中间的桥梁了，而且这种场景下代码被执行的可能性非常大。

必须记住的是，作为可执行文件的XLL是特定于体系结构的，这意味着你必须了解你的目标，即根据目标组织所使用的Microsoft
Office/Excel版本来决定构建何种体系架构的Payload：

> Office 2016或更早版本：x86
>
> Office 2019或更新版本：x64

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/Octoberfest7/XLL_Phishing.git

## 代码编译

我们可以使用下列命令编译项目源码（[
_ingestfile.c_](https://github.com/Octoberfest7/XLL_Phishing/blob/main/ingestfile.c)）：

    
    
    gcc -o ingestfile ingestfile.c

x64编译：

    
    
    x86_64-w64-mingw32-gcc snippet.c 2013_Office_System_Developer_Resources/Excel2013XLL*SDK/LIB/x64/XLCALL32.LIB -o importantdoc.xll -s -Os -DUNICODE -shared -I 2013_Office_System_Developer_Resources/Excel2013XLL*SDK/INCLUDE/

x86编译：

    
    
    i686-w64-mingw32-gcc snippet.c 2013_Office_System_Developer_Resources/Excel2013XLL*SDK/LIB/XLCALL32.LIB -o HelloWorldXll.xll -s -DUNICODE -Os -shared -I 2013_Office_System_Developer_Resources/Excel2013XLL*SDK/INCLUDE/

编译完成后，你需要新建一个文件夹，然后把XLL拷贝到这个文件夹中，然后使用下列命令进行压缩：

    
    
    zip -r <myzipname>.zip <foldername>/

请注意，你还需要将代码片段中的一些变量与你命名的XLL和zip文件相匹配。

## 工具使用演示

![](https://image.3001.net/images/20220925/1664115778_63306442db092a6d0a925.gif)

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/Octoberfest7/XLL_Phishing/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **XLL_Phishing** ：【[
_GitHub传送门_](https://github.com/Octoberfest7/XLL_Phishing)】

## 参考资料

> [ _https://docs.microsoft.com/en-us/deployoffice/security/internet-macros-> blocked_](https://docs.microsoft.com/en-us/deployoffice/security/internet-> macros-blocked)
>
> [ _https://docs.microsoft.com/en-us/office/client-developer/excel/add-in-> manager-and-xll-interface-functions_](https://docs.microsoft.com/en-> us/office/client-developer/excel/add-in-manager-and-xll-interface-functions)
>
> [
> _https://github.com/edparcell/HelloWorldXll_](https://github.com/edparcell/HelloWorldXll)
>
> [ _https://docs.microsoft.com/en-us/office/client-developer/excel/welcome-> to-the-excel-software-development-kit_](https://docs.microsoft.com/en-> us/office/client-developer/excel/welcome-to-the-excel-software-development-> kit)

