**简介**  
这是“A Deep Dive into Penetration Testing of macOS
Application”的博客系列的第二部分。在第一部分中，我们了解了macOS应用程序及其结构，并演示了如何构建虚拟应用程序。我们还谈到了系统完整性保护（SIP）以及如何配置常见的网络拦截工具。第二部分将深入研究文件和二进制分析。

**TL;DR**  
本博客探讨了如何分析macOS应用程序，包括代码签名、强化运行时和授权的概述。此外，我们还介绍了各种文件和内存分析技术和工具。

**静态文件和二进制分析**  
在分析macOS应用程序时，通常的做法是从查看代码签名开始。签名包含元数据，例如证书链、授权和签名信息，可以提供关于应用程序功能、安全性和潜在漏洞的见解。

**什么是代码签名？**  
根据Apple的文档：“代码签名是一种macOS安全技术，你可以使用它来证明你创建了一个应用程序。一旦签名，系统可以检测到应用程序的任何更改——无论是意外引入还是恶意代码引入。”

代码签名使用私钥创建的数字签名，并使用公钥进行验证。签名附加到应用程序上，操作系统可以使用存储在其受信任根证书仓库中的公钥来验证它。

与Windows不同，其中代码签名是可选的，可以使用第三方证书，macOS要求使用由Apple颁发的开发者ID证书进行代码签名。从macOS
10.15开始，所有通过App Store内外分发的应用程序必须由Apple签名和公证才能在默认Gatekeeper设置下运行。

Gatekeeper是一种安全技术，旨在确保只有受信任的软件在用户的Mac上运行。

默认情况下，Gatekeeper仅允许从Mac App
Store下载或获得已注册苹果的开发者的ID证书的应用程序运行。如果应用程序没有使用有效证书进行签名或未经过Apple公证，Gatekeeper将显示警告消息并阻止应用程序运行。

或者，用户可以无视Gatekeeper策略以打开任何软件，除非受到移动设备管理（MDM）解决方案的限制。

使用codesign实用工具，可以获取有关应用程序的全面信息，包括其哈希类型、哈希校验和签名机构。通过运行以下命令，我们可以显示应用程序的代码签名（图1）：

    
    
    codesign -dvv "<path to application>"

![](./img/7203439666237139113.png)

**图1：虚拟应用程序的代码签名**

有时，应用程序可能没有有效的数字签名。例如，如果应用程序使用不受信任的证书（已过期或缺少颁发机构），或者如果应用程序包中的某些资源没有有效的签名，则可能会出现这种情况。

绕过代码签名机制的其中一种有趣方法与“TeamIdentifier”字段相关。

TeamIdentifier是分配给开发团队的唯一标识符代码，用于在苹果开发者计划中注册时签署应用程序并在macOS设备上安装配置文件。

长话短说，发现了一种绕过第三方开发人员解释代码签名API的方法，这使得具有adhoc签名的二进制文件（通常用于测试目的）看起来像是由Apple签署的。这种绕过方法可能可行，因为一些Apple应用程序的TeamIdentifier值设置为“not
set”。Ref中可以获取更多信息。

**强化运行时**

我们通过分析代码签名可以了解到是否将强化运行时应用于应用程序。根据苹果的文档：

“强化运行时（[Hardened
Runtime](https://developer.apple.com/documentation/security/hardened_runtime?language=objc
"Hardened
Runtime")）和系统完整性保护（SIP）通过防止某些类别的攻击（如代码注入、动态链接库（DLL）劫持和进程内存空间篡改）来保护你的软件的运行时完整性。”

我们可以在代码签名中通过[SecCodeSignatureFlags](https://developer.apple.com/documentation/security/seccodesignatureflags?language=objc
"SecCodeSignatureFlags")来查看Hardened
Runtime提供的保护级别。这些标志在codesign命令输出中的CodeDirectory行中显示。

SecCodeSignatureFlags是一组位掩码标志，描述各种已签名代码特征。值为0x0表示二进制文件具有标准代码签名，没有其他安全功能或限制（图2）。这是macOS中代码签名的默认状态，适用于大多数没有特殊安全要求的应用程序。

![](./img/8506724683398663028.png)

**图2：无限制的虚拟应用程序**

标志0x10000表示应用程序已应用运行时强化策略，例如ASLR、库验证、沙箱、系统调用过滤器和代码签名验证。这些策略共同工作，以防止基于内存的漏洞、限制系统访问并防止恶意代码注入。此外，标志的值可以合并，例如在下面的示例中（图3），虚拟应用程序具有标志0x10002，因为它既具有adhoc签名（0x0002），又具有运行时强化策略（0x10000）。

![](./img/4712921918779409135.png)

**图3：具有运行时强化策略的虚拟应用程序**

所有可能标志的列表如下：

    
    
    kSecCodeSignatureHost = 0x0001，/可能托管客户代码/
    kSecCodeSignatureAdhoc = 0x0002，/必须在没有签署者的情况下使用/
    kSecCodeSignatureForceHard = 0x0100，/始终在启动时设置HARD模式/
    kSecCodeSignatureForceKill = 0x0200，/始终在启动时设置KILL模式/
    kSecCodeSignatureForceExpiration = 0x0400，/强制证书过期检查/
    kSecCodeSignatureRestrict = 0x0800，/限制dyld加载/
    kSecCodeSignatureEnforcement = 0x1000，/强制执行代码签名/
    kSecCodeSignatureLibraryValidation = 0x2000，/需要库验证/
    kSecCodeSignatureRuntime = 0x10000，/应用运行时强化策略/
    kSecCodeSignatureLinkerSigned = 0x20000，/标识签名是由链接器自动生成的/

某些应用程序可能依赖于Hardened
Runtime限制的功能。在这种情况下，开发人员可以使用[运行时异常](https://developer.apple.com/documentation/security/hardened_runtime#3111188
"运行时异常")来禁用单个保护（图4）。

![](./img/5061297561222274276.png)

**图4：Xcode中的运行时异常**

启用运行时异常可能会使应用程序面临潜在攻击。我们可以通过查看[授权](https://developer.apple.com/documentation/bundleresources/entitlements
"授权")来检查应用程序是否有异常。

**授权**

**授权** 是授予可执行文件使用服务或技术权限的键值对。

检查授权是文件分析的关键步骤，因为它们指示应用程序在系统上可以执行哪些操作，就像一组权限一样。

我们有几种选项可以查看应用程序的授权。一种方法是使用codesign工具运行以下命令：

    
    
    codesign -d --entitlements :-  <path to binary file>
    

或者我们也可以使用jtool（由Jonathan Levin创建的otool扩展版本）运行以下命令：

    
    
    jtool2 –ent ~/dummy.app/Contents/MacOS/dummy
    

通过分析应用程序的授权，我们可以确定潜在的安全问题。例如，如果一个应用程序具有allow-dyld-environment-variables授权，并带有“true”值（图5），则可以将其用于Dylib注入。关于这方面的问题将在博客系列第三部分中进行更多介绍。

![](./img/6972795456265523928.png)

**图5：虚拟应用程序具有“allow-dyld-environment-variables”授权**

以下是一些示例授权：

com.apple.security.cs.disable-library-validation：该应用程序可以加载任意插件或框架而无需进行代码签名。  
com.apple.security.cs.allow-dyld-environment-variables：该应用程序可能受到动态链接器环境变量影响，你可以使用它们向你的应用程序进程注入代码。  
com.apple.security.get-task-allow：二进制文件允许其他非沙盒进程附加。  
com.apple.security.cs.allow-unsigned-executable-memory：将该应用程序暴露于常见的漏洞中,漏洞由内存不安全的代码语言编写。  
com.apple.security.files.downloads.read-write：该应用程序可能对Downloads文件夹具有读写访问权限。  
com.apple.security.device.camera：该应用程序可以与内置和外部摄像头交互，并捕捉电影和静态图像。  
如果应用程序具有不必要或过于宽松的授权，则可能会获得访问敏感信息或系统资源的权限。

例如，com.apple.security.device.camera授权授予了应用程序访问用户Mac上摄像头的权限。然而，从macOS 11（Big
Sur）开始，此权限将触发 **TCC** （Transparency, Consent and Control）提示。

**TCC**
是一种管理应用程序访问敏感用户数据（例如相机、麦克风和位置服务）的macOS技术。在允许应用程序访问之前，TCC将提示用户进行同意操作。用户可以授予或拒绝访问，并且决策将由TCC存储，所以提示不会重新出现。

**Hacks和技巧**  
我们可以使用各种文件分析技术来识别在macOS应用程序渗透测试时可能存在的漏洞。

其中一种技术是检查应用程序使用的第三方库是否存在已知的安全漏洞。我们可以使用包含在Xcode命令行工具包或[jtool](http://www.newosxbook.com/tools/jtool.html
"jtool")中的[otool](https://www.unix.com/man-page/osx/1/otool "otool")来执行此操作。

要获取应用程序使用的库列表，我们可以执行otool -L <path binary="" file=""
to="">命令（图6），并搜索易受攻击或过时的库。</path>

![](./img/4526602288553524203.png)

**图6：虚拟应用程序的库**

使用nm命令，我们可以检索函数符号和应用程序变量名称。例如，要在二进制文件中显示符号列表，我们可以运行nm <path binary="" file=""
to="">命令（图7）。在输出中，查找已知的易受攻击函数或未安全使用的函数。</path>

此命令还可用于确定应用程序是使用哪种编程语言编写的。包含_objc的函数可能表示应用程序是使用Objective-C开发的，_swift可能表示Swift语言，等等。

![](./img/44117335867877542.png)

**图7：虚拟应用程序的函数**

另一个关键要素是搜索敏感信息，例如密码、API密钥和日志文件，这些信息可能存储不安全。

要检查的一些关键文件：

配置文件，例如.plist、XML或JSON文件，通常位于应用程序包中。  
日志文件，通常位于~/Library/Log目录中。  
缓存文件，存储为SQLite数据库文件，通常位于~/Library/Caches目录中，但可能位于系统上的其他位置。可以使用SQLite
Browser或SQLitestudio等工具分析这些数据库文件（图8）。

![](./img/644787261614861453.png)

**图8：虚拟应用程序的缓存文件**

查看“Activity Monitor”时，我们可以看到应用程序打开的所有文件列表。

为此，请打开“Activity Monitor”，选择应用程序并单击“Open Files and Ports”选项卡（图9）。

![](./img/3265395716016391913.png)

**图9：虚拟应用程序打开的所有文件都显示在Activity Monitor中**

另一种查找敏感信息的方法是从二进制文件中提取文本字符串。为此，我们可以使用strings <path binary="" file=""
to="">命令。</path>

我们不会在此帖子中深入探讨逆向工程过程，但我们认为值得注意的是，你可以使用反汇编器软件，例如：

  * [Ghidra](https://github.com/NationalSecurityAgency/ghidra "Ghidra")
  * [Hopper Disassembler](https://www.hopperapp.com/ "Hopper Disassembler")
  * [IDA Pro](https://hex-rays.com/ "IDA Pro")  
这些工具具有反汇编和反编译（生成更易于阅读的C代码）的功能（请参见图10）。这有助于你在编译代码中找到逻辑、内存损坏和其他潜在安全问题。

![](./img/1559308697487403951.png)

**图10：Ghidra中虚拟应用程序的反编译代码**

**动态分析**  
以下是动态分析常用工具的常见列表：

[Apple
Instruments](https://developer.apple.com/library/archive/documentation/Performance/Conceptual/CellularBestPractices/Appendix/Appendix.html
"Apple Instruments")。Xcode的开发人员工具之一——用于监视应用程序性能、识别内存泄漏和跟踪文件系统活动（图11）。

![](./img/1647236988322416748.png)

**图11：Apple Instrument**

[TaskExplorer](https://objective-see.org/products/taskexplorer.html
"TaskExplorer")。提供有关运行任务的信息，包括签名状态、已加载的动态库和打开的文件。  
[FileMonitor](https://objective-see.com/products/utilities.html#FileMonitor
"FileMonitor")。监视文件事件，如创建、修改和删除。  
[ProcessMonitor](https://objective-see.org/products/utilities.html#ProcessMonitor "ProcessMonitor")。监视进程创建和终止。  
[Frida](https://frida.re/ "Frida")。面向开发人员、逆向工程师和安全研究人员的动态检测工具。

**Frida**  
让我们更详细地谈谈 **Frida** 。它是一种动态分析工具，可以hook正在运行的应用程序的内部API。Frida使用V8
javascript引擎创建一个方便的环境来执行hook和内存拦截。这使我们能够实时监视和修改应用程序的行为。

我们可以使用命令pip3 install frida-tools安装Frida。

安装后，在JavaScript中创建一个Frida脚本，该脚本将注入到应用程序中。

例如，以下脚本拦截macOS应用程序中的open函数调用，并将文件路径和模式记录到控制台：

    
    
    Interceptor.attach(Module.findExportByName(null, "open"), { onEnter: function(args) {console.log("File path: " + Memory.readUtf8String(args[0])); console.log("Mode: " + args[1].toInt32()); } });
    

使用frida -l命令将Frida脚本注入到正在运行的macOS应用程序中（图12）。

![](./img/8117554225500719135.png)

**图12：Frida的使用方法**

**内存分析**  
通过读取内存，我们可以找到可能暴露给攻击者的敏感信息，包括密码、加密密钥和在执行应用程序期间临时存储在内存中的其他机密信息。

分析应用程序内存的一种方法是使用[lldb](https://lldb.llvm.org/
"lldb")工具，默认情况下是Xcode调试器，通常用于macOS应用程序的动态分析。它可以附加到运行进程、设置断点、检查内存并逐步执行代码。

要搜索敏感数据，我们可以使用以下步骤创建进程内存转储。  
首先，让我们通过下面一条命令找到正在运行进程的PID：  
ps aux | grep -i “testing app”…  
接下来，我们需要使用lldb附加到相关进程并转储其进程内存。  
lldb --attach-pid 44434 —> 44444 PID of process

