![](https://image.3001.net/images/20210420/1618906264_607e8c98485696529e94c.jpg!small)

## 关于MoveKit

MoveKit是一款功能强大的Cobalt Strike横向渗透套件，本质上来说MoveKit是一个Cobalt
Strike扩展，它利用的是SharpMove和SharpRDP
.NET程序集的execute_assembly函数实现其功能，攻击脚本能够通过读取指定类型的模板文件来处理Payload创建任务。

## Cobalt Strike

 **Cobalt Strike是一款美国Red Team开发的渗透测试神器，常被业界人称为CS。**

最近这个工具大火，成为了渗透测试中不可缺少的利器。其拥有多种协议主机上线方式，集成了提权，凭据导出，端口转发，socket代理，office攻击，文件捆绑，钓鱼等功能。同时，Cobalt
Strike还可以调用Mimikatz等其他知名工具，因此广受黑客喜爱。

## 脚本运行机制

在使用该脚本的过程中，用户仅需要加载MoveKit.cna脚本即可，它将加载所有其他的所需脚本。除此之外，用户可能还需要对代码进行编译，并存放至Assemblies目录中，具体取决于SharpMove和SharpRDP程序集所要采取的行为。最后，某些文件移动操作可能需要动态编译，这里将需要用到Mono。

在加载脚本时，会有一个名为Move的选择器被加载进menubar中，这里将给用户提供多个可用选项。首先，用户需要选择一个在远程系统上执行的命令，命令将通过WMI、DCOM、计划任务、RDP或SCM执行。接下来，脚本将会通过Command命令执行机制来获取执行文件。然后，使用File方法将文件存储至目标系统并执行它。这里所使用到的“Write
File Only”只会对数据进行移动。最后，工具会使用默认配置和信标命令进行操作。

 **在使用信标命令时，它将读取默认配置，并使用几个命令行参数。信标命令样本如下：**

    
    
    <exec-type> <target> <listener> <filename>
    
    
    move-msbuild 192.168.1.1 http move.csproj

 **自定义预构建信标命令则有些许不同，命令样本为：**

    
    
    move-pre-custom-file <target> <local-file> <remote-filename>
    
    
    move-pre-custom-file computer001.local /root/payload.exe legit.exe

对于上面的位置字段，当选择WMI方法时会用到，如果选择的是SMB，则无需使用该字段。Location字段接受三个不同的值，第一个是Cobalt Strile
Web服务器的URL地址，第二个则是待上传文件的远程目标系统的Windows目录路径，第三则是一个存储事件写入的Linux路径或“local”单词。

脚本将会针对所有的文件方法创建Payload，但是，如果Payload已经在之前创建好了的话，脚本只会移动或执行它。

## 支持的横向渗透技术

MoveKit包含了各种不同的横向渗透技术、执行触发器和Payload类型。

 **文件移动指的是获取文件或将文件移动到远程主机所使用的方法：**

    
    
    SMB to flat file
    
    WMI to flat file
    
    WMI to Registry Key Value
    
    WMI to Custom WMI Class property

 **命令触发器指的是触发在远程主机上执行命令的方法：**

    
    
    WMI
    
    SCM
    
    RDP
    
    DCOM
    
    计划任务
    
    修改计划任务
    
    修改服务路径

 **Shellcode执行：**

    
    
    Excel 4.0 DCOM
    
    WMI事件描述

 **劫持攻击：**

    
    
    服务DLL劫持
    
    DCOM服务器劫持

## 工具下载

广大研究人员可以使用下列命令将该工具源码克隆至本地：

    
    
    git clone https://github.com/0xthirteen/MoveKit.git

## 依赖组件

需要使用Mono（MCS）编译.NET程序集。

## 项目地址

MoveKit：https://github.com/0xthirteen/MoveKit

## 参考资料

> https://github.com/GhostPack/SharpWMI
>
> https://github.com/rvrsh3ll/SharpCOM
>
>
> https://github.com/cobbr/SharpSploit/blob/master/SharpSploit/LateralMovement/DCOM.cs
>
> https://github.com/malcomvetter/CSExec
>
> https://github.com/djhohnstein/SharpSC
>
> https://github.com/Mr-Un1k0d3r/SCShell
>
> https://github.com/Arno0x/CSharpScripts/blob/master/shellcodeLauncher.cs
>
> https://github.com/vysecurity/CACTUSTORCH

