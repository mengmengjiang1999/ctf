## 一、前言

**近日，中兴通讯高级邮件防御系统捕获一例病毒样本。通过分析发现，该样本会通过进程替换等方式释放，并在傀儡进程中运行AgentTesla木马以达到信息窃取的目的。以下是对该样本的分析。**

## 二、样本简介

该样本为Autoit3编写的exe文件：

![](https://image.3001.net/images/20190820/1566262574_5d5b452e404eb.png!small)

反编译出部分脚本，脚本做了较强的混淆：

![](https://image.3001.net/images/20190820/1566262590_5d5b453e2bbbd.png!small)

脚本使用了多种混淆手法，如常数被转换成数学运算、无用的随机变量赋值、调用Chr函数加密、无用的条件分支等。脚本中对字符串的解密函数为：

![](https://image.3001.net/images/20190820/1566262604_5d5b454c1ee1e.png!small)

## 三、样本分析

通过对脚本进行解混淆并结合调试分析，样本的主要功能如下：

### 1.UAC Bypass

对反编译后的脚本分析后，发现该样本针对不同的windows系统分别采用了不同的UAC绕过方式。

(1)通过eventvwr绕过UAC

Windows下的事件查看器eventvwr.exe运行时会检查注册表项HKCU\Software\Classes\mscfile\shell\open\command，若存在就读取并运行其Default键值下保存的命令行。

对相关脚本解混淆后内容如下：

![](https://image.3001.net/images/20190820/1566262620_5d5b455cf418e.png!small)

![](https://image.3001.net/images/20190820/1566262632_5d5b4568be757.png!small)

上述脚本首先判断当前账号在win7、win8下是否为管理员账号，若不是就通过设置HKCU\Software\Classes\mscfile\shell\open\command中default默认值为要运行的代码路径（@ScriptFullPath），之后运行eventvwr.exe可以绕过UAC悄悄运行自己的代码。

eventvwr.exe为系统软件，查看微软签名的manifest清单可见其autoElevate属性为true，说明eventvwr有自动提权功能：

![](https://image.3001.net/images/20190820/1566262647_5d5b457726f20.png!small)

所以恶意程序使用eventvwr绕过UAC后，其作为eventvwr.exe创建的子进程也具备高完整性，允许访问多个特权和受保护的系统资源。

(2)fodhelper绕过UAC

这个原理和eventvwr绕过UAC类似。Win10下fodhelper.exe在运行时会打开注册表项HKCU\Software\Classes\ms-settings\shell\open\command，检查该注册表路径下是否有DelegateExecute键，若有，就执行Default键值下保存的命令行。

对相关脚本解混淆后内容如下：

![](https://image.3001.net/images/20190820/1566262662_5d5b45861b586.png!small)

样本设置注册表项HKCU\Software\Classes\ms-settings\shell\open\command下的DelegateExecute，并在Default下设置要运行的代码路径@ScriptFullPath，之后通过运行fodhelper来启动@ScriptFullPath中的命令。

样本通过上述两种方式，可以绕过UAC并使得创建的进程具备高完整性（high-integrity）。

### 2.提权

若样本发现自己没有拿到高权限，也会通过AdjustTokenPrivileges操作进行提权：

![](https://image.3001.net/images/20190820/1566262683_5d5b459bb680b.png!small)

以及使用DuplicateTokenEx复制高权限进程的Token后，根据需要修改安全属性并通过调用CreateProcessAsUserW使得创建的进程具备想要的权限：

![](https://image.3001.net/images/20190820/1566262695_5d5b45a7649c0.png!small)

![](https://image.3001.net/images/20190820/1566262711_5d5b45b78a8fb.png!small)

### 3.检测Vbox和Vmware虚拟机环境

![](https://image.3001.net/images/20190820/1566262724_5d5b45c40a284.png!small)

### 4.下载文件到temp目录下执行

![](https://image.3001.net/images/20190820/1566262736_5d5b45d03b4b3.png!small)

### 5.清理痕迹

![](https://image.3001.net/images/20190820/1566262748_5d5b45dc068b8.png!small)

### 6.利用傀儡进程隐藏踪迹

调试过程中发现样本通过IsDebuggerPresent、QueryPerformanceCounter等多种方式进行反调试，同时使用进程替换技术在傀儡进程中运行了自己的恶意代码。这部分代码存于样本的资源节中，首先加载资源并解密，通过创建子进程的方式运行C:\Windows\Microsoft.NET\Framework\v2.0.50727\RegAsm.exe，创建的子进程RegAsm即为傀儡进程，通过进程替换将RegAsm进程替换成自己的代码运行，以此达到隐藏恶意代码的目的。

为了使这部分行为更为隐蔽，样本在实施进程注入时既没有直接调用相关API，也没有通过调用GetProcAddress等函数来获取相关API地址，而是采用遍历kernel32.dll导出函数的方式来获取API函数入口地址：

![](https://image.3001.net/images/20190820/1566262765_5d5b45ed2bcd6.png!small)

查询到的API函数地址存于栈中，后续通过栈中地址调用相关API函数：

![](https://image.3001.net/images/20190820/1566262775_5d5b45f7a9aac.png!small)

这种方式使得无法直接从汇编代码看出调用的API，避免引起逆向人员的注意。

创建傀儡进程并进行进程替换的过程如下：

首先创建挂起的进程（create_suspended），此时windows加载器会将PEB结构体地址写入寄存器：

![](https://image.3001.net/images/20190820/1566262787_5d5b4603dc604.png!small)

通过Wow64GetThreadContext获取目标进程RegAsm.exe的主线程上下文：

![](https://image.3001.net/images/20190820/1566262804_5d5b4614018cd.png!small)

通过ReadProcessMemory在目标进程的PEB结构地址偏移8h处读取4字节，此处保存的是目标进程的加载基址：

![](https://image.3001.net/images/20190820/1566262816_5d5b462075ac8.png!small)

通过读取PEB结构获取目标进程加载基址的方式可避免ASLR（地址空间随机化）的影响。

随后判断目标进程基址是否为00400000，若基址相同，则执行ZwUnmapViewOfSection卸载模块，防止后续将恶意代码映射到00400000基址时引起冲突：

![](https://image.3001.net/images/20190820/1566262830_5d5b462ec30a5.png!small)

在本地进程空间中分配4C000大小的内存，用于分节区拷入PE文件，拷贝的内容具备明显的PE特征：

![](https://image.3001.net/images/20190820/1566262842_5d5b463a2e44b.png!small)

在目标进程（RegAsm.exe）中指定00400000处分配对应大小的内存：

![](https://image.3001.net/images/20190820/1566262854_5d5b46467833a.png!small)

通过WriteProcessMemory将恶意代码注入到目标进程00400000处：

![](https://image.3001.net/images/20190820/1566262866_5d5b46524027b.png!small)

并将目标进程中注入的PE头和资源部分置为ReadOnly，防止引起怀疑。

通过WriteProcessMemory将保存的目标进程PEB中的ImageBase修改为00400000（已注入PE的EP地址）：

![](https://image.3001.net/images/20190820/1566262884_5d5b46642c30f.png!small)

![](https://image.3001.net/images/20190820/1566262894_5d5b466e9409b.png!small)

设置RegAsm进程的主线程Context的EP为已注入PE的EP，完成进程替换。之后ResumeThread恢复主线程，开始运行被注入的代码：

![](https://image.3001.net/images/20190820/1566262935_5d5b46974b070.png!small)

基本就是常规的进程替换操作。之所以选择注入RegAsm.exe，可能因为是白名单。

### 7.注入代码分析

在进程注入前，于内存中找到待注入的PE文件，修改其入口代码为EBFE（自循环），用修改后的PE做后续的进程替换，调试器中Attach目标进程断下后将入口代码改回为原代码。然而随后发现attach的进程无法继续调试，推测可能做了反调试。接下来直接dump内存分析。将注入的这部分内存数据dump下来，修复PE头后，查看PE结构显示为.NET文件，且文件名、函数名以及函数中的关键字符串做了混淆：

![](https://image.3001.net/images/20190820/1566262949_5d5b46a590bbd.png!small)

查看反编译后的代码，确认采用了.NET反调试，自定义的函数里设置了DebuggerHidden属性，相当于对调试器隐藏代码，调试器会越过这些函数，不会停在断点处：

![](https://image.3001.net/images/20190820/1566262960_5d5b46b059899.png!small)

经分析，该.NET文件或为AgentTesla木马变种。AgentTesla是一个商业化的间谍软件，可生成定制功能的木马程序。查看反编译后的代码，其功能主要是窃取电脑的键盘输入和剪贴板信息、屏幕截图以及浏览器信息，并通过FTP、HTTP或SMTP方式发送出去。

主要功能分析如下：

(1)KeyLogger

![](https://image.3001.net/images/20190820/1566262976_5d5b46c0e9966.png!small)

(2)窃取剪贴板信息

![](https://image.3001.net/images/20190820/1566262988_5d5b46cc949cd.png!small)

![](https://image.3001.net/images/20190820/1566262997_5d5b46d57b17c.png!small)

(3)窃取屏幕截图

![](https://image.3001.net/images/20190820/1566263011_5d5b46e31ec09.png!small)

(4)木马支持FTP、HTTP、SMTP三种方式往外发送窃取的数据

a）通过FTP上传：一般是预先设置ftp地址、用户名和密码，并选择加密或者非加密方式上传

非加密方式：

![](https://image.3001.net/images/20190820/1566263026_5d5b46f28cbfd.png!small)

加密方式：

![](https://image.3001.net/images/20190820/1566263039_5d5b46ff8ecca.png!small)

b）通过HTTP上传：通常会预先设置C&C服务器，木马运行后会尝试连接该服务器并接收指令

![](https://image.3001.net/images/20190820/1566263054_5d5b470e988b4.png!small)

在分析过程中跟踪到该木马和外部网址周期性进行HTTP通讯过程：

![](https://image.3001.net/images/20190820/1566263073_5d5b47213e714.png!small)

c）通过SMTP上传：工具使用者可以指定邮箱服务器地址、用户名和密码

![](https://image.3001.net/images/20190820/1566263085_5d5b472dcdd5b.png!small)

(5)收集浏览器信息

在木马的资源节嵌入了一个名为IELibrary的DLL，该dll功能主要是搜集浏览器的url、cookie以及账号密码等信息

a)查询、添加及删除历史记录：

![](https://image.3001.net/images/20190820/1566263099_5d5b473be6943.png!small)

b)窃取并破解IE保存的密码和cookie：

![](https://image.3001.net/images/20190820/1566263109_5d5b4745e1952.png!small)

c) 查询、添加、删除URL历史：

![](https://image.3001.net/images/20190820/1566263119_5d5b474f6a4e4.png!small)

d)恢复浏览器账号：

![](https://image.3001.net/images/20190820/1566263130_5d5b475a2fac7.png!small)

e)获取URL信息：

![](https://image.3001.net/images/20190820/1566263140_5d5b47642afad.png!small)

此外，该木马还会自我复制，在%AppData\Roaming\MyApp目录下生成Myapp.exe文件，且文件属性置为隐藏：

![](https://image.3001.net/images/20190820/1566263154_5d5b47727e023.png!small)

随后将该文件添加到注册表实现自启动：

![](https://image.3001.net/images/20190820/1566263164_5d5b477c5bdac.png!small)

以及通过注册表禁用任务管理器，以防止用户通过任务管理器kill进程：

![](https://image.3001.net/images/20190820/1566263175_5d5b4787aea5c.png!small)

## 四、总结

该样本用了多种混淆和反调试方法干扰逆向，同时使用多种手法进行UAC绕过、提权，并使用进程替换等方式释放运行AgentTesla木马，意图窃取电脑中的键盘输入、剪贴板、屏幕截图以及浏览器账号密码和url等信息。

附样本MD5：

2e045198949970207aa8170522633010

 ***本文作者：ZInsight团队，转载请注明来自FreeBuf.COM**

