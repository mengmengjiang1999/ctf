## **简介**

在2022年的Defcon大会上,安全研究人员Wietze
Beukema通过对进程级环境变量的研究，提出了一种Dll劫持新思路，下面就其中涉及的技术点展开介绍。

##  **01** 环境变量

每一个进程都有一个环境块，其中包含一组环境变量及其值。有两种类型的环境变量，用户环境变量和系统环境变量。

 **用户环境变量** :仅对当前用户有效，位于:HKEY_CURRENT_USER\Environment

![1662625790_6319a7fec0bf7a2ef0d51.png!small?1662625791600](https://image.3001.net/images/20220908/1662625790_6319a7fec0bf7a2ef0d51.png!small?1662625791600)

 **系统环境变量**
:对所有用户均有效，位于:HKEY_LOCAL_MACHINE\SYSTEM\ControlSet001\Control\Session
Manager\Environment

![1662625797_6319a80587c059c04f8c9.png!small?1662625798165](https://image.3001.net/images/20220908/1662625797_6319a80587c059c04f8c9.png!small?1662625798165)

默认情况下，子进程继承其父进程的环境变量。命令处理器启动的程序继承命令处理器的环境变量。

##  **02** 劫持原因

程序可能会依赖Windows定义好的环境变量来确定某些文件的位置，尤其对于Windows内置程序来说大量依赖环境变量来寻找系统盘文件。如下展示的是Windows系统盘ws2_32.dll中的代码片段：

![1662625834_6319a82a574b57e0b0741.png!small?1662625834920](https://image.3001.net/images/20220908/1662625834_6319a82a574b57e0b0741.png!small?1662625834920)

正常来说"%SystemRoot%/System32/mswsock.dll"会被解析为"C:/Windows/System32/mswsock.dll"，但是这里面有一个不确定的因素就是"%SystemRoot%"，假设我们修改了环境变量"%SystemRoot%"的值为其他文件夹路径且在该路径下存放恶意Dll，那么程序就会加载我们设定的Dll，继而完成Dll劫持。

如果直接更改"%SystemRoot%"的值，会对整个操作系统上运行的程序产生影响，但是我们可以只修改指定进程的环境变量，如创建以下vbs脚本，利用子进程默认继承其父进程环境变量的特性，修改Windows内置进程hostname.exe的环境变量"SystemRoot"为"C:\Evil"。

    
    
    Set shell = WScript.CreateObject("WScript.Shell")  
    shell.Environment("Process")("SystemRoot") = "C:\Evil"  
    shell.Exec("C:\windows\system32\hostname.exe")

操作流程如下：

![1662625847_6319a8378e4d9fb532a36.png!small?1662625847911](https://image.3001.net/images/20220908/1662625847_6319a8378e4d9fb532a36.png!small?1662625847911)

然后用Procmon监控hostname.exe，可以看到确实会加载"C:\Evil"路径下的Dll。

![1662625857_6319a841632caa56059f7.png!small?1662625857868](https://image.3001.net/images/20220908/1662625857_6319a841632caa56059f7.png!small?1662625857868)

##  **03** 持久化

从上面流程可以看到，能够完成Dll劫持的关键在于修改环境变量的值，那么完成持久化的关键就在于维持目标进程环境变量值的修改。下面提供2种持久化方案：

 **利用注册表修改Windows自启服务的环境变量**

这里先引用下Wietze Beukema文章中提到的修改Windows打印机服务的环境变量，看是否会成功加载指定目录下的Dll文件。

1\. 首先将恶意Dll"mswsock.dll"放到指定目录"C:\Evil\System32"

2\. 在注册表spoolsv服务下创建"Environment"键值修改环境变量

![1662625877_6319a855e9278c3bb2691.png!small?1662625878526](https://image.3001.net/images/20220908/1662625877_6319a855e9278c3bb2691.png!small?1662625878526)

3\. 重启spoolsv服务，用Procmon进行监控

![1662625897_6319a86930dfd5581a228.png!small?1662625897634](https://image.3001.net/images/20220908/1662625897_6319a86930dfd5581a228.png!small?1662625897634)

可以看到使用上述方式修改Windows服务的环境变量确实能够加载我们指定目录下的Dll文件。但是需要注意的是，有时候为了保证被修改的服务能够正常运行，我们需要将受环境变量影响的Dll全部移动到我们指定的路径下。

实际上能够被利用的Windows服务远不止上面一个，通常来说服务对应一个PE文件，这里我们去看看Windows自带服务的PE文件路径是如何写的就明白了。

![1662625926_6319a886761e07e86d49d.png!small?1662625926952](https://image.3001.net/images/20220908/1662625926_6319a886761e07e86d49d.png!small?1662625926952)![1662625931_6319a88b961c8b35426ac.png!small?1662625932124](https://image.3001.net/images/20220908/1662625931_6319a88b961c8b35426ac.png!small?1662625932124)

可以看到很多服务都依赖环境变量来寻找所对应的PE文件，这里我推荐修改的Windows自启服务是Windows推送通知系统服务(WpnService)，修改环境变量后只需移动一个受影响的Dll文件即可,不用管该服务是否能够正常运行。

 **常规持久化配合创建子进程**

我们也可以使用常规持久化方案如创建计划任务或者写注册表来实现自启，然后程序自启后自修改自身环境变量值,最后创建受环境变量影响的Windows可信进程，利用Dll劫持来完成一次隐匿攻击行为。

接下来使用Win32 API来展示下如何修改子进程的环境变量。

1\. 子进程Child.exe代码如下:

    
    
    #include <windows.h>  
    int main(int argc, char* argv[], char* envp[]) {  
    char szBuf[MAX_PATH] = {};  
    GetEnvironmentVariable("SystemRoot", szBuf, sizeof(szBuf));  
    MessageBox(NULL, szBuf, "Child", MB_OK);  
    return 0;  
    }

2\. 父进程Parent.exe代码如下:

    
    
    #include <stdio.h>  
    #include <windows.h>  
    int main(int argc, char* argv[], char* envp[]) {  
    SetEnvironmentVariable("SystemRoot", "C:\\Evil");  
    UINT nRet = WinExec("C:/Users/Super/Desktop/Child.exe", SW_HIDE);  
    if (nRet > 31)  
    {  
    printf("创建子进程成功\n");  
    }  
    else  
    {  
    printf("创建子进程失败\n");  
    }  
    return 0;  
    }

3\. 运行Parent.exe进程，查看结果

![1662625959_6319a8a71aadde817a704.png!small?1662625959622](https://image.3001.net/images/20220908/1662625959_6319a8a71aadde817a704.png!small?1662625959622)

以上需要注意一点的就是，当Child.exe进程需要的权限比Parent.exe进程高时，Parent.exe创建Child.exe进程时会失败，当然也就无法谈起修改其环境变量值了，如下：

![1662625972_6319a8b46540c874720cf.png!small?1662625973041](https://image.3001.net/images/20220908/1662625972_6319a8b46540c874720cf.png!small?1662625973041)

##  **04** 预防和影响范围

环境变量是Windows的一个历史包袱，随着Windows注册表出现，可以在一定程度上代替环境变量。但是为了考虑兼容性，它依然存在且在Windows内部大量使用。关于这点，我们可以对程序进行简单的调试，对ExpandEnvironmentStringsW
API函数下断回溯，就会发现很多Windows内置Dll在使用环境变量来确定某些文件，如下：

![1662626005_6319a8d5ee22a2f82e892.png!small?1662626006776](https://image.3001.net/images/20220908/1662626005_6319a8d5ee22a2f82e892.png!small?1662626006776)

我们自己写的程序或者模块可能会引用Windows系统Dll文件，但是Windows内部Dll文件大量引用环境变量，这会让我们的程序可能会受到此类Dll劫持手法的攻击。为了尽可能的减少风险，在编码时我们可以遵循以下规则：

1\.
程序代码使用GetWindowsDirectory代替环境变量"%SystemRoot%"，或者使用GetSystemDirectory直接拿系统盘System32路径

2\. 对系统Dll进行路径检测

3\. 对程序加载的Dll进行签名校验

##  **05** 总结

1\.
相对于传统Dll劫持利用Windows加载Dll时的搜索顺序，将恶意Dll存放在目标程序所在文件夹之下来完成Dll劫持。该方式可以保持目标程序所在文件夹的纯净度，可有效规避检测。

2\. "海量"的Windows服务和内置进程均受环境变量的影响，这值得引起我们安全研究人员对环境变量的重视，以应对后面可能出现的此类攻击手法。

## 参考

https://www.wietzebeukema.nl/blog/save-the-environment-variables

https://docs.microsoft.com/zh-cn/windows/win32/procthread/environment-variables

  

