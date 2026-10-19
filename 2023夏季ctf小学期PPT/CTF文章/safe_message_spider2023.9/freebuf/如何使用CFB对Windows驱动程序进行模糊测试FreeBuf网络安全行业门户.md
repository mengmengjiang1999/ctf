![](https://image.3001.net/images/20220104/1641267098_61d3bf9a74fd7f573f07b.png!small)

## 关于CFB

CFB，全名为Canadian Furious
Beaver，是一款功能强大的Windows驱动程序模糊测试工具，该工具可以帮助广大研究人员监控Windows驱动程序中的IRP处理器，并对Windows驱动程序漏洞进行分析、复现和模糊测试。

CFB本质上是一款分布式工具，可以捕捉发送给任何Windows驱动程序的IRP。它主要由两部分组成：

>
> 1、该工具的“Broker”（代理）结合了用户端代理和一个能将自己安装到目标系统上的自提取驱动程序（IrpDumper.sys）。运行之后，它将暴露（取决于编译选项）远程命名管道（可从\\\target.ip.address\pipe\cfb访问）或侦听TCP/1337的TCP端口。该工具所实现的通信协议设计简单，允许任何[
> _第三方工具_](https://github.com/hugsy/cfb-cli)轻松地（通过简单的JSON消息）从同一个代理转储驱动程序IRP。
>
>  
>
>
> 2、CFB的GUI是一个采用ProcMon风格的Windows 10
> UWP应用程序：它将连接到代理所在的任何位置，并提供一个方便的GUI来操作代理（驱动程序枚举、钩子和IRP捕获）。它还提供了伪造/重放IRP、自动模糊测试（即对捕获的每个IRP采用特定的模糊策略）或以各种格式提取IRP，方便研究人员进行深入分析。捕获的数据可以以易于解析的格式（*.cfb=SQLite）保存在磁盘上，以便进一步分析，或随后在GUI中重新加载。

尽管GUI显然需要Windows 10环境（UWP应用程序）中使用，但代理本身可以部署在任何Windows
7+主机（x86或x64）上。目标主机必须启用testsigning BCD策略，因为自解压驱动程序不支持WHQL。

## 机制分析

IrpDumper.sys是CFB
Broker代理的驱动程序部分，它将在启动时自动提取和安装。驱动程序将负责通过代理传递的IOCTL挂接请求挂接到驱动程序的IRP主功能表。成功后，驱动程序的IRP表将指向IrpDumper.sys拦截程序，我们也可以轻松通过调试器或WinObjEx64之类的工具查看到相关信息。

![](https://image.3001.net/images/20220104/1641267121_61d3bfb152a9a57eb666a.png!small)

IrpDumper.sys本身可以充当一个rootkit，并代理所有对目标驱动程序的调用。当DeviceIoControl被发送给挂钩的驱动程序时，IrpDumper只需捕获数据（如果有），并将消息推送到用户端代理，然后将执行返回给合法的驱动程序，从而允许预期的代码按预期继续执行。代理会将所有这些数据存储在用户区域中，等待事件去请求它们。

## 工具构建

### GUI

首先，我们需要使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/hugsy/CFB.git

接下来，使用Visual Studio构建项目根目录中的CFB.sln代理解决方案。除此之外，我们还可以通过构建GUI(Unicersal
Windows)项目来构建App GUI。

### 命令行

首先，我们需要使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/hugsy/CFB.git

然后通过VS命令行终端运行下列命令：

    
    
    C:\cfb\> msbuild CFB.sln /p:Configuration=$Conf

其中的$Conf可以设置为Releases或Debug。

## 工具安装&配置

在Windows 7+设备上（推荐使用Windows 10 SDK VM），启用BCD测试签名选项（以管理员权限启动cmd.exe）：

    
    
    C:\> bcdedit.exe /set {whatever-profile} testsigning on

如果使用了调试模式，IrpDumper.sys将提供更多的详细信息。我们可以通过DebugView.exe之类的工具或WinDbg之类的内核调试器来查看全部的相关信息。此时，我们必须启用内核调试BCD选项（以管理员权限启动cmd.exe）：

    
    
    C:\> bcdedit.exe /set {whatever-profile} debug on

## 工具运行截图

### IRP拦截界面

![](https://image.3001.net/images/20220104/1641267172_61d3bfe44b857eba71fde.png!small)

### IRP详情

![](https://image.3001.net/images/20220104/1641267178_61d3bfea86aa60449c2b8.png!small)

![](https://image.3001.net/images/20220104/1641267184_61d3bff01d6f59301304a.png!small)

### IRP重放

![](https://image.3001.net/images/20220104/1641267193_61d3bff9aecc5d9e2de1e.png!small)

## 项目地址

 **CFB：** 【[ _GitHub传送门_](https://github.com/hugsy/CFB)】

## 参考资料

> [ _https://github.com/hugsy/cfb-cli_](https://github.com/hugsy/cfb-cli)
>
> [
> _https://github.com/hfiref0x/WinObjEx64_](https://github.com/hfiref0x/WinObjEx64)
>
> [ _https://github.com/hugsy/stuff/tree/master/random-> word_](https://github.com/hugsy/stuff/tree/master/random-word)

