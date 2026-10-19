## **情报背景**

近日Malwarebytes发现了一起针对俄罗斯的鱼叉式钓鱼攻击，使用了Konni RAT的新变种。该新变种使用巧妙的手法隐藏JS代码，并利用Google
Project Zero曾披露的一种较新的UAC Bypass手法和父进程欺骗相结合进行权限提升。

本文将对这两个技术点进行攻击技术研判和剖析。

 **组织名称**

|

未知  
  
---|---  
  
 **战术标签**

|

载荷隐匿 权限提升  
  
 **技术标签**

|

RPC, UAC Bypass  
  
 **情报来源**

|

https://blog.malwarebytes.com/threat-intelligence/2021/08/new-variant-of-konni-malware-used-in-campaign-targetting-russia/  
  
## 攻击技术分析

 **亮点1:执行命令检索嵌入的js代码并执行。**

Kooni使用恶意宏文档作为获取初始访问的手段，在宏文档中使用了一些简单但有效的手段隐匿其载荷。攻击者将执行主要攻击行为的恶意js脚本嵌入文档末尾。

![1636965900_61921e0c2da669e336702.png!small?1636965905256](https://image.3001.net/images/20211115/1636965900_61921e0c2da669e336702.png!small?1636965905256)

  

在宏执行时提取嵌入的恶意js代码，写入磁盘后执行。

![1636966041_61921e996755fd4f84dcb.png!small?1636966046419](https://image.3001.net/images/20211115/1636966041_61921e996755fd4f84dcb.png!small?1636966046419)

如上图所示：在宏代码中使用findstr查找文档内容中的"^var"字符串，然后将从"
var"开始的行内容写入y.js，之后用wscript运行该JS文件。

这种做法避免了攻击特征在文档宏中直接出现，可能躲避一些安全产品对文档安全性的检测。

 **亮点2:基于RPC的权限提升手法在野利用。**

在Windows 10的系统环境下，该样本使用了一种利用RPC服务中暴露的脆弱接口进行UAC绕过的方法。这种方法由Google Project
Zero团队的James Forshaw提出，并公开了利用细节与代码。

被利用的RPC函数RAiLaunchAdminProcess 位于APPINFO服务中，函数定义如下：

    
    
    // APPID  
    // 201ef99a-7fa0-444c-9399-19ba84f12a1a  
      
    long RAiLaunchAdminProcess(  
    handle_t hBinding,  
    [in][unique][string] wchar_t* ExecutablePath,  
    [in][unique][string] wchar_t* CommandLine,  
    [in] long StartFlags,  
    [in] long CreateFlags,  
    [in][string] wchar_t* CurrentDirectory,  
    [in][string] wchar_t* WindowStation,  
    [in] struct APP_STARTUP_INFO* StartupInfo,  
    [in] unsigned __int3264 hWnd,  
    [in] long Timeout,  
    [out] struct APP_PROCESS_INFORMATION* ProcessInformation,  
    [out] long *ElevationType  
    );

通过RAiLaunchAdminProcess函数接口，我们可以指定权限创建新的进程。权限的控制由StartFlags决定，为0时以普通权限执行，为1时则创建具有管理员权限的进程。虽然仍会有UAC弹窗，但具有微软签名的一些可信程序能够绕开UAC弹窗，直接以高权限执行，这给后面的利用提供了条件。

RAiLaunchAdminProcess函数中存在一个CreateFlags参数，该参数与CreateProcessAsUser函数的dwCreateFlags参数一致。而在dwCreateFlags中有两个比较特殊的标志位：DEBUG_PROCESS和DEBUG_ONLY_THIS_PROCESS，这两个标志位能够自动启动对新进程的调试。

如果能在已经提升的UAC进程上启动调试并获取调试对象句柄，我们便可以请求调试事件，且该函数能够返回完全访问的句柄。拥有高权限进程完整的句柄之后，通过代码注入等手段便可以成功绕过UAC限制，成功获取管理员权限。

![1636966331_61921fbb1e9f954f9db95.png!small?1636966336079](https://image.3001.net/images/20211115/1636966331_61921fbb1e9f954f9db95.png!small?1636966336079)

但利用该接口进行权限提升所需解决的问题则是：在访问进程的调试对象句柄中权限不够，访问Debug
Object时需要的是PROCESS_QUERY_INFORMATION权限；但在安全限制下，获取到的访问权限是PROCESS_QUERY_LIMITED_INFORMATION。这种限制使得我们不能简单地获取高权限进程的调试对象句柄。

幸而同一线程上创建的具有调试标志的所有进程共享一个调试对象，无论是普通权限进程还是高权限进程。因此通过先后创建两个进程的方式，我们可以绕过这种限制，获取高权限新进程的调试对象，进而获取完整权限的句柄。

完整利用过程如下：

1\.
StartFlags设为0，使用RAiLaunchAdminProcess创建非提升进程，并在CreateFlags中开启DEBUG_PROCESS选项。

2\. 使用NtQueryInformationProcess打开调试对象的句柄。

3\. 使用NtRemoveProcessDebug将调试器从进程中分离出来，并用TerminateProcess终止创建的进程。

4\. StartFlags设为1，使用RAiLaunchAdminProcess再创建一个新的高权限进程，并将2步骤的对象分配给新进程。

5\. 检索并使用NtDuplicateObject返回完整访问进程句柄的初始化调试事件。

6\. 使用新的进程句柄代码可以注入提升的进程完成UAC绕过。

而在Konni新变种在获取程序的完全访问进程句柄后，通过父进程欺骗技术将高权限的Taskmgr.exe设置为新进程的父进程，通过子进程继承其管理员权限，实现UAC绕过。比起Project
Zero原本的利用路径，避免了进程注入等敏感操作，减少了暴露面。

![1636966486_61922056b796ed5fd1b08.png!small?1636966491764](https://image.3001.net/images/20211115/1636966486_61922056b796ed5fd1b08.png!small?1636966491764)

##  **总结**

Konni将恶意代码写入文档内容末尾的方式，在躲避安全产品检测上具有一定的效果；而本地windows RPC服务滥用和父进程欺骗的结合，是对Google
Project Zero披露的权限提升技术的改进，使得该过程更加的隐蔽。

随着攻防环境的发展，此类在野攻击中涌现的新攻击手法与改进措施，值得蓝军攻击研究人员的进一步思考。

## 绿盟科技 M01N Team 战队

绿盟科技M01N战队专注于Red
Team、APT等高级攻击技术、战术及威胁研究，涉及Web安全、终端安全、AD安全、云安全等相关领域。通过研判现网攻击技术发展方向，以攻促防，为风险识别及威胁对抗提供决策支撑，全面提升安全防护能力。

