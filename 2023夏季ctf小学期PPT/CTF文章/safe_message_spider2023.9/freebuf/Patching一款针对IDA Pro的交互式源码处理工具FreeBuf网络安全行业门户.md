![](https://image.3001.net/images/20220324/1648134077_623c87bd6995eaa18b8d5.png!small)

## 关于Patching

通过对编译代码进行处理来改变现有应用程序的行为，在恶意软件分析、软件逆向工程以及更广泛的安全研究领域中，其实并不少见。而Patching是一款针对[
_IDA_ __ _Pro_](https://www.hex-rays.com/products/ida/)的交互式源码处理工具，该工具能够扩展IDA
Pro反汇编工具的功能，以创建一个功能更加强大的交互式源码处理工作流。

当前版本的Patching基于[ _Keystone引擎_](https://github.com/keystone-engine/keystone)实现其功能，支持x86/x64和Arm/Arm64。

## 工具要求

该插件需要IDA 7.6和Python 3环境支持，并能够在Windows、Linux和macOS操作系统上运行。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/gaasedelen/patching.git

## 工具安装

我们可以直接在IDA工具的控制台中通过下列方法直接以自动化的形式安装该工具。

### Windows / Linux

    
    
    import urllib.request as r; exec(r.urlopen('https://github.com/gaasedelen/patching/raw/main/install.py').read())

### macOS

    
    
    import urllib.request as r; exec(r.urlopen('https://github.com/gaasedelen/patching/raw/main/install.py', cafile='/etc/ssl/cert.pem').read())

### 手动安装

除了上述方法之外，我们还可以手动安装该工具。首先，我们要访问该项目的【[
_Releases页面_](https://github.com/gaasedelen/patching/releases)】下载对应操作系统平台的插件包发布版本，并解压到插件目录下。

我们强烈建议广大研究人员将该工具直接安装到IDA的用户插件目录下：

    
    
    import ida_diskio, os; print(os.path.join(ida_diskio.get_user_idadir(), "plugins"))

## 工具使用

该插件将会自动加载支持的架构（x86/x64/Arm/Arm64），并注入相关的代码处理功能，我们可以直接在IDA反汇编视图中右键点击上下文菜单来查看和使用：

![](https://image.3001.net/images/20220324/1648134115_623c87e3c5825830aeb95.gif!small)

接下来，我们会对上下文菜单中提供的功能进行详细介绍。

### Assemble汇编

可以通过右键单击上下文菜单中的“Assemble”来启动代码操作的主界面。该功能将模拟基础的IDA反汇编视图，可用于快速连续编辑一条或多条指令：

![](https://image.3001.net/images/20220324/1648134173_623c881d13f4efecc665c.gif)

汇编行是一个可编辑的字段，可用于实时修改指令。按下回车键将能够把输入的指令提交到数据库中。

当前位置（即光标）将始终以绿色突出显示。在提交代码修复操作之前，由于编辑而被删除的指令将以红色突出显示：

![](https://image.3001.net/images/20220324/1648134193_623c883195f08343d2d2c.png!small)

最后，可以使用向上和向下箭头键，同时仍将焦点放在可编辑的部件文本字段上，以便在不使用鼠标的情况下快速在反汇编视图中上下移动光标。

### NOP空操作指令

最常见的代码操作就是删除一条或多条指令。因此，NOP操作将始终在右键单击菜单中可见，以便快速访问：

![](https://image.3001.net/images/20220324/1648134204_623c883cb4a524f400a84.gif!small)

当然了，我们也可以直接选择一系列操作指令。

### 强制条件跳转

该插件仅在右键单击条件跳转指令时显示此操作：

![](https://image.3001.net/images/20220324/1648134214_623c884634a9579b3b986.gif!small)

### 保存 & 快速应用

可以随时通过子菜单将处理后的程序保存（应用）到选定的可执行文件，“快速应用”操作可以更快地使用相同的设置保存后续经过处理的程序：

![](https://image.3001.net/images/20220324/1648134223_623c884fb94a1100ce2ac.gif!small)

该插件还会保留原始可执行文件的备份（.bak）。

### 恢复

最后，如果你对代码修改操作不满意的话，只需要右键单击黄色的指令块，将其恢复为原始值：

![](https://image.3001.net/images/20220324/1648134236_623c885c0cd3554705aed.gif!small)

不过有的时候可能恢复操作还需要进行部分人工处理。

## 项目地址

 **Patching：** 【[ _GitHub传送门_](https://github.com/gaasedelen/patching)】

## 参考资料

> [ _https://www.hex-rays.com/products/ida/_](https://www.hex-> rays.com/products/ida/)
>
> [
> _https://github.com/gaasedelen/keystone_](https://github.com/gaasedelen/keystone)
>
> [ _https://github.com/keystone-> engine/keystone_](https://github.com/keystone-engine/keystone)
>
> [ _https://hex-rays.com/_](https://hex-rays.com/)

