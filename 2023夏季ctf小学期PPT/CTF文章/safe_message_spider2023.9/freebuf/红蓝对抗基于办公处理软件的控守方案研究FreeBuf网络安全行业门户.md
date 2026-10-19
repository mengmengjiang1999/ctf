![](https://image.3001.net/images/20210609/1623227969_60c07e41d81134bbd53bf.jpg!small)

# 01 概述

红蓝对抗中，如何能够对渗透测试的目标进行长期控制，绕过操作系统的安全检测和防护软件的查杀检测，长久进行后门植入，进行长期的攻防对抗，这是一个非常值得深入研究的技术话题，笔者对国内某款办公处理软件，进行技术研究，就基于此办公处理处理软件进行后门植入和控守作为示例，进行技术演示。

# 02 控守思路

诸如办公处理软件，Adobe
Reader和某PDF阅读器都是每个人常用的办公处理类的软件，标准配置。在红蓝对抗的渗透测试中，基于办公处理软件来做到长期控守，后门工具能够依托于办公处理软件启动而运行，工具隐藏程度深，可作为办公处理软件的正常功能来使用，做到操作系统环境中不闪、不弹、不卡，隐蔽执行。

确认了研究思路框架，接下来就是如何达到控守的目标，分几步走，以及是否有比较完美的解决方案？

带着这些问题，我进行了以下研究。

# 03 安装分析

### **3.1 首选安装包**

控守目标选择的是办公处理软件，首先从安装包开始进行分析，安装包大致上可以分为网络安装包和离线安装包，两者都可以进行分析，找出安装包执行过程中，存在的弱点，校验是否有可利用的点，如下：

某办公处理软件的安装包拷贝到桌面，使用ProcessMonitor监控执行过程中的行为，安装过程中可以观察到很有意义的输出。

    
    
    NoFinishPage_foucs_app.exe CreateFile  C:\Users\Admin\Desktop\MSIMG32.dll  
    NoFinishPage_foucs_app.exe CreateFile  C:\Users\Admin\Desktop\WINSPOOL.DRV  
    NoFinishPage_foucs_app.exe CreateFile  C:\Users\Admin\Desktop\oledlg.dll  
    NoFinishPage_foucs_app.exe CreateFile  C:\Users\Admin\Desktop\urlmon.dll  
    NoFinishPage_foucs_app.exe CreateFile  C:\Users\Admin\Desktop\VERSION.dll  
    NoFinishPage_foucs_app.exe CreateFile  C:\Users\Admin\Desktop\IPHLPAPI.DLL  
    NoFinishPage_foucs_app.exe CreateFile  C:\Users\Admin\Desktop\WININET.dll  
    NoFinishPage_foucs_app.exe CreateFile  C:\Users\Admin\Desktop\USERENV.dll  
    NoFinishPage_foucs_app.exe CreateFile  C:\Users\Admin\Desktop\OLEACC.dll  
    NoFinishPage_foucs_app.exe CreateFile  C:\Users\Admin\Desktop\WINMM.dll  
    NoFinishPage_foucs_app.exe CreateFile  C:\Users\Admin\Desktop\iertutil.dll  
    NoFinishPage_foucs_app.exe CreateFile  C:\Users\Admin\Desktop\OLEACCRC.DLL  
    NoFinishPage_foucs_app.exe CreateFile  C:\Users\Admin\Desktop\4_GA_NoFinishPage_foucs_appCHS.dll    

安装包会在桌面路径C:\Users\Admin\Desktop来搜索和加载DLL文件，很不合理，应该从C:\windows\和C:\windows\system32\文件夹路径搜索和加载DLL。

再来看另一个办公处理软件的安装包执行记录，也存在同样的问题：

    
    
    test_office_inst.exe CreateFile  C:\Users\Admin\Desktop\Iphlpapi.dll  NAME NOT FOUND   
    test_office_inst.exe CreateFile  C:\Users\Admin\Desktop\Wldp.dll  NAME NOT FOUND   
    test_office_inst.exe CreateFile  C:\Users\Admin\Desktop\test_office_inst.exe.Local  NAME NOT FOUND   
    test_office_inst.exe CreateFile  C:\Users\Admin\Desktop\test_office_inst.exe.Local  NAME NOT FOUND   
    test_office_inst.exe CreateFile  C:\Users\Admin\Desktop\msimg32.dll  NAME NOT FOUND   
    test_office_inst.exe CreateFile  C:\Users\Admin\Desktop\WINHTTP.dll  NAME NOT FOUND   
    test_office_inst.exe CreateFile  C:\Users\Admin\Desktop\webio.dll  NAME NOT FOUND   
    test_office_inst.exe CreateFile  C:\Users\Admin\Desktop\winnlsres.dll  NAME NOT FOUND   
    test_office_inst.exe CreateFile  C:\Users\Admin\Desktop\SspiCli.dll  NAME NOT FOUND   
    test_office_inst.exe CreateFile  C:\Users\Admin\Desktop\white_list.data  NAME NOT FOUND   
    test_office_inst.exe CreateFile  C:\Users\Admin\Desktop\TextShaping.dll  NAME NOT FOUND   
    test_office_inst.exe CreateFile  C:\Users\Admin\Desktop\DWrite.dll  NAME NOT FOUND   
    test_office_inst.exe CreateFile  C:\Users\Admin\Desktop\WindowsCodecs.dll  NAME NOT FOUND   
    test_office_inst.exe CreateFile  C:\Users\Admin\Desktop\ncrypt.dll  NAME NOT FOUND   
    test_office_inst.exe CreateFile  C:\Users\Admin\Desktop\MSASN1.dll  NAME NOT FOUND   
    test_office_inst.exe CreateFile  C:\Users\Admin\Desktop\DPAPI.DLL  NAME NOT FOUND  

再来校验一下DLL模块调用堆栈：

    
    
    ntdll.dll  RtlUpcaseUnicodeChar + 0x1b1  0x7701f341  C:\Windows\SysWOW64\ntdll.dll
    ntdll.dll  RtlMultiAppendUnicodeStringBuffer + 0x1e8  0x7701f7f8  C:\Windows\SysWOW64\ntdll.dll
    ntdll.dll  LdrLoadDll + 0xf6  0x7701fdc6  C:\Windows\SysWOW64\ntdll.dll
    KernelBase.dll  LoadLibraryExW + 0x156  0x7630ec56  C:\Windows\SysWOW64\KernelBase.dll
    KernelBase.dll  LoadLibraryA + 0x42  0x7630f772  C:\Windows\SysWOW64\KernelBase.dll // 调用LoadLibraryA() 函数
    test_office_inst.exe  test_office_inst.exe + 0xf3253  0x643253  C:\Users\Admin\Desktop\test_office_inst.exe
    test_office_inst.exe  test_office_inst.exe + 0xf408d  0x64408d  C:\Users\Admin\Desktop\test_office_inst.exe

  

部分DLL文件是通过LoadLibraryA()函数进行调用执行加载动作。

办公处理软件的安装包在安装过程中就存在DLL路径加载的问题，这给我们达到控守的目标创造了条件，其次软件安装包在执行过程中windows操作系统的权限校验，特别是UAC已经是用户同意了的，后门工具执行不会遇到执行权限上的障碍。

软件安装视频演示：https://www.bilibili.com/video/BV1G44y167yi

###  **3.2 运行时后门植入分析**

办公处理软件的安装包正常运行结束，办公处理软件也能够正常运行工作，使用工具来分析办公处理软件运行中的行为。

其中一个办公处理软件，安装目录是：

C:\Users\Admin\AppData\Local\Software\Office\11.23.548.10152\office6\

首先来看，目录是当前用户，这意味着当前用户拥有对软件安装目录的所有权限，包括读写、删除和执行，其次配合其他的安全问题，比如任意文件移动、任意文件写，或者文件释放的安全方面问题，最后达到的效果就是在办公处理软件目录下可进行任意操作。

一个相较于特殊的情况是办公处理软件在操作系统层面是默认在系统白名单中，普通用户也不会留意软件的某些恶意行为，相对较为隐蔽。

再来看另外一个办公处理软件，虽然其安装目录是C:\Program Files (x86)\PDF Software\PDF
Reader\，但是更新程序的加载目录却是当前用户目录，如下：

    
    
    PdfReaderUpdater.exe CreateFile  C:\Users\Admin\AppData\Roaming\PDF Software\Addon\PDF Reader\VERSION.dll  NAME NOT FOUND
    PdfReaderUpdater.exe CreateFile  C:\Users\Admin\AppData\Roaming\PDF Software\Addon\PDF Reader\MSIMG32.dll  NAME NOT FOUND
    PdfReaderUpdater.exe CreateFile  C:\Users\Admin\AppData\Roaming\PDF Software\Addon\PDF Reader\USERENV.dll  NAME NOT FOUND
    PdfReaderUpdater.exe CreateFile  C:\Users\Admin\AppData\Roaming\PDF Software\Addon\PDF Reader\OLEACC.dll  NAME NOT FOUND
    PdfReaderUpdater.exe CreateFile  C:\Users\Admin\AppData\Roaming\PDF Software\Addon\PDF Reader\SspiCli.dll  NAME NOT FOUND
    PdfReaderUpdater.exe CreateFile  C:\Users\Admin\AppData\Roaming\PDF Software\Addon\PDF Reader\DPAPI.DLL  NAME NOT FOUND
    PdfReaderUpdater.exe CreateFile  C:\Users\Admin\AppData\Roaming\PDF Software\Addon\PDF Reader\MSASN1.dll  NAME NOT FOUND
    PdfReaderUpdater.exe CreateFile  C:\Users\Admin\AppData\Roaming\PDF Software\Addon\PDF Reader\urlmon.dll  NAME NOT FOUND
    PdfReaderUpdater.exe CreateFile  C:\Users\Admin\AppData\Roaming\PDF Software\Addon\PDF Reader\CoreMessaging.dll  NAME NOT FOUND

以当前用户权限，即可完成针对办公处理软件的后门植入。

软件更新视频演示：https://www.bilibili.com/video/BV1V54y1G7LV

# 04 高权限维持分析

红蓝对抗中，对抗的基础就是权限的维持，特别是高权限的维持，那么现在就来分析一下就办公处理软件而言，如何来进行高权限的注入和维持。

就windows系统而言，最高权限是NT AUTHORITY\SYSTEM，笔者以此权限为目标继续分析。

操作系统的服务管理器中可以观察到两款办公处理软件都安装有系统服务。

![](https://image.3001.net/images/20210609/1623228006_60c07e66e303def0e33b1.png!small)

服务的停止和启动操作可以观察到服务的进程行为：

    
    
    pdfProtect.exe CreateFile  C:\Program Files (x86)\pdf Software\pdf Reader\OLEACCRC.DLL  NAME NOT FOUND
    pdfProtect.exe CreateFile  C:\Program Files (x86)\pdf Software\pdf Reader\UxTheme.dll  NAME NOT FOUND
    pdfProtect.exe CreateFile  C:\Program Files (x86)\pdf Software\pdf Reader\HttpENU.dll  NAME NOT FOUND
    pdfProtect.exe CreateFile  C:\Program Files (x86)\pdf Software\pdf Reader\HttpCHS.dll  NAME NOT FOUND
    pdfProtect.exe CreateFile  C:\Program Files (x86)\pdf Software\pdf Reader\HttpLOC.dll  NAME NOT FOUND
    pdfProtect.exe CreateFile  C:\Program Files (x86)\pdf Software\pdf Reader\Wldp.dll  NAME NOT FOUND
    pdfProtect.exe CreateFile  C:\Program Files (x86)\pdf Software\pdf Reader\profapi.dll  NAME NOT FOUND

服务会在办公处理软件安装目录下进行模块搜索和加载，并且权限都是以NT权限加载和启动。

# 05 权限维持思路

经过前面的分析，进行梳理和总结。从安装包开始，就有方法进行恶意模块的注入和加载，UAC已绕过，即C:\Program Files
(x86)\目录具备读写权限，以上述一款办公处理软件为例，可以写入恶意模块到软件安装目录，服务启动时即可加载恶意DLL模块，且权限是NT最高权限。

![](https://image.3001.net/images/20210609/1623228028_60c07e7ccf4f2c0b14d0b.png!small)

# 06 总结

办公处理软件由于在办公处理上的高频使用特性，成为红蓝对抗中的首要关注对象，笔者以办公处理软件为例，总结红蓝对抗中权限维持的控守思路和方法，重点在于查找和分析办公处理软件安装包和正常使用过程中正常功能操作、高权限服务和日常软件维护中的控守技巧分享。

 **作者：极光无限-莫夜**

