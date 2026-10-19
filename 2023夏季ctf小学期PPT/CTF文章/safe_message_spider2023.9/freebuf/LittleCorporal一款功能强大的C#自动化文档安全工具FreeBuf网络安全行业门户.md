![](https://image.3001.net/images/20211108/1636368618_618900eaa8f4430949c2a.png!small)

## 关于LittleCorporal

LittleCorporal是一款功能强大的C#自动化文档安全工具，该工具可以帮助广大研究人员生成并分析恶意Word文档。

## 运行机制

LittleCorporal能够接受用户提供的参数，并在需要执行Maldoc（恶意Word文档）的目标远程主机上执行进程注入。除此之外，LittleCorporal还可以接受以.bin格式存储的本地Shellcode文件路径作为输入参数。因此，如果要使用此项目生成的Maldoc，则需要在要运行Maldoc的计算机上指定一个已在运行的进程（无论是本地计算机还是其他计算机，explorer.exe始终都会有一个实例，因此我们可以直接选择使用此实例）。

LittleCorporal可以将Shellcode和目标进程嵌入至Loader.cs中，并实时将Loader.cs编译为一个.NET
.exe工具，并利用线程劫持技术来执行远程进程注入。生成的.NET
.exe工具就是一个线程劫持加载器，可以通过Donut来生成位置独立的Shellcode，而这个Shellcode将负责执行.exe文件。Donut生成的Shellcode使用了Base64编码，并最终生成一个Word文档。

除此之外，LittleCorporal还使用了VBA模板功能，其中将包含本项目提供的一个文本文件，并将该宏文件注入至新生成的Word文档中。宏文件名为“autoopen”，因此文档打开时，这个宏便会立刻被调用执行。

## 红队建议

如果你计划使用LittleCorporal来进行红队安全任务的话，可以考虑给Shellcode代码设置一个“退出”功能，而无需完全终止掉Shellcode所注入的目标进程。这一步可以通过在msfvenom中设置EXITFUNC=thread来实现，或者在Cobalt
Strike中通过Aggressor来设置。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/connormcgarr/LittleCorporal.git

## 工具使用

1、我们必须获取完整的项目代码，因为LittleCorporal使用了相对路径来引入额外的资源，比如说Donut。

2、获取到整个项目代码之后，我们需要将工作目录修改为“bin\Release”目录。如果你选择自行重新编译该项目的话，我们建议大家使用已发布的构建版本，而不要使用调试版本。命令如下：

    
    
    cd C:\Path\to\LittleCorporal\bin\Release

3、在需要执行LittleCorporal.exe的设备上指定Shellcode文件的路径以及正在运行的进程（负责执行生成的Maldoc）。命令如下：

    
    
    LittleCorporal.exe C:\Path\To\Shellcode.bin explorer.exe

4、接下来，LittleCorporal将会输出最终生成的Word文档的路径地址。

5、如需清理工具目录，可以直接使用下列命令：

    
    
    LittleCorporal.exe clean

## 工具运行示例

    
    
    C:\LittleCorporal\bin\Release>LittleCorporal.exe C:\beacon.bin explorer.exe
    
    .____    .__  __    __  .__         _________                                         .__
    
    |    |   |__|/  |__/  |_|  |   ____ \_   ___ \  _________________   ________________  |  |
    
    |    |   |  \   __\   __\  | _/ __ \/    \  \/ /  _ \_  __ \____ \ /  _ \_  __ \__  \ |  |
    
    |    |___|  ||  |  |  | |  |_\  ___/\     \___(  <_> )  | \/  |_> >  <_> )  | \// __ \|  |__
    
    | _______ \__||__|  |__| |____/\___  >\______  /\____/|__|  |   __/ \____/|__|  (____  /____/
    
            \/                        \/        \/             |__|                     \/
    
     
    
     
    
                 ________
    
                /        \
    
             __ /       (o)\__
    
            /     ______\   \                   I am the strongest debater in the whole Conseil.
    
            | ____/__  __\____|                 I let myself be attacked, because I know how to defend myself.
    
               [  --~~--  ]                                                              - Napoleon Bonaparte
    
                | (  L   )|
    
          ___----\  __  /----___
    
         /   |  < \____/ >   |   \
    
        /    |   < \--/ >    |    \
    
        ||||||    \ \/ /     ||||||
    
        |          \  /   o       |
    
        |     |     \/   === |    |
    
        |     |      |o  ||| |    |
    
        |     \______|   +#* |    |
    
        |            |o      |    |
    
         \           |      /     /
    
         |\__________|o    /     /
    
         |           |    /     /
    
     
    
    [+] Parsed Arguments:
    
       [>] Shellcode Path: C:\beacon.bin
    
       [>] Target Process: explorer.exe
    
     
    
    [+] Embedded shellcode in Loader.cs!
    
    [+] Generated C# Loader artifact!
    
    [+] Ran the .NET assembly through Donut!
    
    [+] Donut artifact is located at: C:\LittleCorporal\Artifacts\payload.bin
    
    [+] Path to Word document: C:\LittleCorporal\Artifacts\Form.doc

## 项目地址

 **LittleCorporal：** 【[
_GitHub传送门_](https://github.com/connormcgarr/LittleCorporal)】

## 参考资料

> [ _https://connormcgarr.github.io/thread-> hijacking/_](https://connormcgarr.github.io/thread-hijacking/)
>
> [ _https://github.com/TheWover/donut_](https://github.com/TheWover/donut)
>
> [ _https://docs.microsoft.com/en-> us/office/vba/api/word.inlineshape.alternativetext_](https://docs.microsoft.com/en-> us/office/vba/api/word.inlineshape.alternativetext)
>
> [
> _https://github.com/connormcgarr/LittleCorporal/blob/main/LittleCorporal/LittleCorporal.Loader/Loader.cs#L266﻿_](https://github.com/connormcgarr/LittleCorporal/blob/main/LittleCorporal/LittleCorporal.Loader/Loader.cs#L266)

