![](https://image.3001.net/images/20230823/1692773583_64e5accf294ae1a3b150b.jpg!small)

## 关于Hidden

Hidden是一款针对Windows系统安全的研究任务解决方案，该工具专为系统安全与逆向工程专家而设计，目前已经被开发成为了一种针对Windows操作系统安全的强大工具。

本质上来说，Hidden是一个带有用户模式接口的Windows驱动程序，可以用于隐藏目标Windows设备上的特定环境，例如RCE程序（procmon或wireshark等）和VM基础设施（vmware
tools等）之类的工具环境。除此之外，该工具还能够实现进程、文件系统和注册表对象等系统元素，以实现进程保护或系统保护等目标。

## 功能介绍

> 1、隐藏注册表键和值；
>
> 2、隐藏文件和目录；
>
> 3、隐藏进程（试验性功能）；
>
> 4、保护指定进程；
>
> 5、从隐藏或受保护的功能排除指定的进程；
>
> 6、用户模式接口（lib或cli）的驱动程序；
>
> 7、更多功能持续开发中...

## 系统要求

> Windows Vista以上版本；
>
> x86或x64架构；

## 建议构建环境

> Visual Studio 2019
>
> Windows Driver Kit

## 项目克隆

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/JKornev/hidden.git

## 代码构建

我们可以按照下列步骤构建一个Hidden工具的win32发布版本：

> 1、使用Visual Studio打开Hidden.sln；
>
> 2、使用发布+Win32配置构建Hidden项目包；
>
> 3、打开构建后生成的<ProjectDir>\Release目录即可查看生成后的程序；

## 工具安装

> 1、在测试计算机上禁用强制数字签名功能（bcdedit /set TESTSIGNING ON），并重启设备；
>
> 2、将 <ProjectDir>\Release\Hidden Package中的文件拷贝到测试设备上；
>
> 3、鼠标右键点击Hidden.inf并选择Install；
>
> 4、开启一个驱动程序（sc start hidden）；
>
> 5、确保服务处于正在运行的状态（sc query hidden）；

## 工具使用

项目提供了一个hiddencli工具来帮助广大研究人员管理一个驱动程序，我们可以使用它来实现目标对象的隐藏和显示，或者修改一个驱动程序的状态等。

隐藏一个文件：

    
    
    hiddencli /hide file c:\Windows\System32\calc.exe

隐藏一个目录：

    
    
    hiddencli /hide dir "c:\Program Files\VMWare"

隐藏一个注册表键：

    
    
    hiddencli /hide regkey "HKCU\Software\VMware, Inc."

隐藏一个进程：

    
    
    hiddencli /hide pid 2340

通过进程镜像名称隐藏进程：

    
    
    hiddencli /hide image apply:forall c:\Windows\Explorer.EXE

获取工具命令行接口帮助信息：

    
    
    hiddencli /help

## 项目地址

Hidden：【[ _GitHub传送门_](https://github.com/JKornev/hidden)】

