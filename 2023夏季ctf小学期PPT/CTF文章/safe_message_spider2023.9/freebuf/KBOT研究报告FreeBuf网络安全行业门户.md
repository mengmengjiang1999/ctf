## KBOT简介

**KBOT通过Internet或本地网络或受感染的外部媒介攻击用户计算机。受感染的文件启动后在系统中写入启动程序和任务调度程序，然后进行web注入窃取受害者的银行和个人数据。KBOT可以下载额外的窃取模块，把所有的用户信息发送给C
&C服务器，包括密码/登录、钱包数据、文件列表和已安装的应用程序等。恶意软件将其所有文件和收集的数据存储在RC6加密的虚拟文件系统中，因此很难被检测到。**

![](https://image.3001.net/images/20200211/1581398677_5e423a9550ef6.png!small)

## 感染方法

KBOT在文件中添加多种恶意代码，感染连接的驱动器（HDD分区、外部媒体、网络驱动器）和共享网络文件夹中的所有EXE文件。恶意软件使用IID
IwbemObjectSink接口和SELECT*FROM
InstanceCreationEvent查询侦听本地和网络逻辑驱动器的连接，并重写IwbemObjectSink接口的指示功能，对于每个驱动器执行目录递归扫描并感染EXE文件。

在扫描目录和感染可执行EXE之前，恶意软件使用API函数netserver enum和NetShareEnum检索共享网络资源的路径：

![](https://image.3001.net/images/20200211/1581400103_5e424027c0201.png!small)

与许多其他病毒一样，KBOT patch了入口点代码，可对代码段开头的代码的进行切换，受感染文件的原始功能不会被保留。

![](https://image.3001.net/images/20200211/1581400347_5e42411bdb493.png!small)

jmp命令将切换到多态代码：

![](https://image.3001.net/images/20200211/1581400475_5e42419b6e575.png!small)

病毒将加密数据添加到以下部分之一的结尾：.rsrc、.data、.rdata。同时对重定位表目录、资源目录、导入目录、节参数等PE文件参数进行相应修改。加密的数据包含恶意软件模块（DLL库）主体，以及用于解密、加载内存和运行的代码。数据用XOR方法加密，库用R**加密，用Aplib压缩。

![](https://image.3001.net/images/20200211/1581409548_5e42650c70608.png!small)

多态代码的末尾是获取kernel32.dll的代码：

![](https://image.3001.net/images/20200211/1581409665_5e426581aded9.png!small)

然后检索VirtualProtect函数的API地址，并使用该地址设置写入和执行位于.rsrc、.data和.rdata末尾的加密数据。解密数据并切换到相关代码：

![](https://image.3001.net/images/20200211/1581409798_5e426606c1739.png!small)

## KBOT功能

### 注入

为了隐藏系统恶意行为，KBOT尝试将代码注入正在运行的系统进程中。

使用API​​函数OpenProcess /
OpenProcessToken和GetTokenInformation，它检索已加载到其地址空间进程的SID。如果该进程的SID与WinLocalSystemSid匹配，则KBOT使用带有CREATE_SUSPENDED标志的CreateProcess
API来创建新进程svchost.exe，然后执行注入操作。
svchost.exe进程复制主模块的标题和部分主体，然后从导入目录中导入，并使用重定位表目录中的信息进行手动重定位。接下来，KBOT使用入口点的地址调用CreateRemoteThread
/ RtlCreateUserThread
API。如果该进程的SID与WinLocalSystemSid不匹配，则该恶意软件将设置SeDebugPrivilege调试特权，并尝试在SID与WinLocalSystemSid匹配的正在运行的services.exe、svchost.exe、explorer.exe进程中执行类似的注入。

KBOT还将injects.ini文件中指定的DLL注入到同一INI文件中列出的进程中。配置文件（包括injects.ini）读取解密并移动到虚拟文件存储中。该示例首先在其存储中搜索所需文件的当前版本；如果出现故障，它将从原始版本读取文件数据，原始版本以加密形式位于主体中。在每个加密数据的开头都有包含JF签名。

![](https://image.3001.net/images/20200212/1581506082_5e43de2297024.png!small)

![](https://image.3001.net/images/20200212/1581506716_5e43e09c62e05.png!small)

JUPITER.32和JUPITER.64执行web注入的dll，通过向HTTP流量中注入恶意代码来窃取用户在浏览器中输入的个人数据。在系统和浏览器进程中执行注入后会修补浏览器（Chrome、Firefox、Opera、Yandex.browser）中的功能代码和传输代码：

![](https://image.3001.net/images/20200212/1581507366_5e43e32649c8e.png!small)

配置文件中的注入列表和恶意软件本身存储在全局数组中的列表相同。

![](https://image.3001.net/images/20200212/1581507658_5e43e44ad9aed.png!small)

如下kbot.ini的所示，其中Hosts是C&C列表，ServerPub是用于数据加密的公钥：

![](https://image.3001.net/images/20200212/1581507730_5e43e492ba34e.png!small)

### DLL劫持

为了在系统启动时在合法操作，恶意软件通过感染在指定的系统库来执行DLL劫持攻击，然后将其写入启动。在系统文件夹C:\Windows\System32中，恶意软件搜索适合攻击的可执行EXE文件，但不考虑以下文件：

> 1、包含字符串level=“requireAdministrator”和>true，需要管理员权限才能运行的可执行文件。
>
> 2、在导入表库中包含以API-MS-WIN-和EXT-MS-WIN-开头的名称，对于这样的文件DLL劫持是不可能实现的。
>
> 3、其名称在以下列表中：“logoff.exe” "shutdown.exe" "slui.exe" "dxdiag.exe"

在找到满足所有条件的可执行文件后，KBOT将在系统目录中创建具有任意名称的文件夹，并将检测到的EXE文件以及位于导入目录中的系统dll复制到该文件夹中。恶意软件以管理员权限执行这些操作，使用EIFOMoniker
Elevation:administrator生成外壳代码，功能如下{3ad05575-8857-4850-9277-11b85bdb8e09}。

![](https://image.3001.net/images/20200212/1581512216_5e43f618c6b77.png!small)

外壳代码使用CreateRemoteThread
API函数注入explorer.exe进程。复制后在同一个文件夹中创建一个任意命名的文件作为加密的文件存储，存放主bot模块、从C&C接收的配置文件、系统信息和其他服务数据。

包含系统应用程序、导入目录中的dll和KBOT服务数据存储的目录如下所示（加密虚拟存储文件名为红色）：

![](https://image.3001.net/images/20200212/1581512663_5e43f7d79263b.png!small)

KBOT会感染复制的系统库，Dllentypoint入口点的代码将被以下代码覆盖：

![](https://image.3001.net/images/20200212/1581512704_5e43f8005b154.png!small)

感染可执行文件时会向代码部分添加多态代码，并在.rsrc、.data或.rdata的末尾添加加密代码。与添加到EXE文件的代码不同，此代码不包含bot的加密主模块，而是从文件存储中读取和解密。

恶意代码会进一步从加密存储中读取主bot模块，受感染的dll的原始数据不会被保存。DLL最后一部分结尾处的加密代码：

![](https://image.3001.net/images/20200212/1581513028_5e43f94434ea3.png!small)

在系统EXE文件启动后，dll将加载到进程的地址空间中。调用导入的函数后，将执行恶意代码。

### 启动

恶意软件在系统启动时运行，方法如下：

> 1、它将自己写入到Software\\\ Microsoft\\\ Windows\\\ CurrentVersion\\\ Run。
>
> 2、使用WMI工具创建一个任务，在任务计划程序中运行系统EXE文件。

KBOT审查Task Schedule中的当前任务，通过EXE文件读取DLL并搜索感染的签名：

![](https://image.3001.net/images/20200212/1581520249_5e441579bf472.png!small)

如果没有包含受感染文件的任务，它以系统帐户创建一个没有用户名的新任务：

![](https://image.3001.net/images/20200212/1581520374_5e4415f635602.png!small)

任务参数：

![](https://image.3001.net/images/20200212/1581520410_5e44161a23884.png!small)

任务创建实例xml文件：

![](https://image.3001.net/images/20200212/1581520453_5e44164545637.png!small)

### 远程管理

KBOT与BC.ini文件中列出的服务器建立反向连接，使用RDP协议同时创建多个会话，恶意软件将配置远程桌面服务器设置：

1、查找内存中termserv.dll库的进程

![](https://image.3001.net/images/20200212/1581520611_5e4416e3e83e0.png!small)

2、patch加载termserv.dll的内存部分

![](https://image.3001.net/images/20200212/1581520672_5e441720adbec.png!small)

3、path过程中在内存中搜索特定的字节，并将其替换为指定的字节

![](https://image.3001.net/images/20200212/1581520748_5e44176cd5e3b.png!small)

KBOT将编辑TermService的注册表项的值：

>
> HKLM\SYSTEM\ControlSet\Control\TerminalServer\LicensingCore\EnableConcurrentSessions
>
>
> HKLM\SOFTWARE\Microsoft\WindowsNT\CurrentVersion\Winlogon\EnableConcurrentSessions
>
>
> HKLM\SOFTWARE\Microsoft\WindowsNT\CurrentVersion\Winlogon\AllowMultipleTSSessions
>
> HKLM\SOFTWARE\Policies\Microsoft\WindowsNT\TerminalServices\MaxInstanceCount

重新启动TermService并在系统中创建一个用户，以便攻击者使用WinBuiltinRemoteDesktopUsersSid进行远程连接。

### C&C通信

恶意软件单独启动一个进程用于接收和处理来自服务器的命令。使用网络连接wininet.dll
API接收命令。接收命令的域位于hosts.ini文件中，恶意软件会定期更新该文件。所有带有C&C数据和连接参数的配置文件都以加密形式存储在主bot的最后一部分中。从C&C接收到的文件放在加密的存储器中，hosti.ini配置文件示例：

![](https://image.3001.net/images/20200212/1581521066_5e4418aaea843.png!small)

恶意软件可以接收以下命令：

> delete file、update file、update injects、update
> host、UpdateCore、卸载恶意软件、UpdateWormConfig

## 总结

KBOT已经造成了严重的危害，它能够通过感染可执行文件在系统和本地网络上迅速传播，且不可能恢复。它通过注入系统进程减慢系统运行速度，通过远程桌面控制系统，窃取个人数据，通过web注入窃取用户的银行数据。

## IoCs

Executable files:

Infected EXEs:

> x86 — 2e3a7d4cf86025f5873ebddf3dcacf72
>
> x64 — 46b3c12b44f587ae25d6f38d2a8c4e0f

Infected DLLs:

> x86 – 5f00df73bb6e84c49b9bf33ff1d552c3
>
> x64 – 1c15c98bc57c48140558d0e8d71b4ecd

Stealer:

> c37058752b2c055ff3a3b3eac50f1350

C&C

> 213.252.245.229
>
> my-backup-club-911[.]xyz
>
> 213.252.245.146/au.exe
>
> sync-time[.]info/au.exe
>
> sync-time[.]icu/au.exe
>
> sync-time[.]club/au.exe

 ***参考来源：[securelist](https://securelist.com/kbot-sometimes-they-come-back/96157/)，由Kriston编译，转载请注明来自FreeBuf.COM**

