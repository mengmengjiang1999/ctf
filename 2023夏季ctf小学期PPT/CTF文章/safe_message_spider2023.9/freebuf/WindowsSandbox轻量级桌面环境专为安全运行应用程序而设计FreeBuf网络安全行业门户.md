![微软官方沙盒Windows
Sandbox](https://image.3001.net/images/20181228/1545929888_5c2504a0a0d5d.png!small)

## 写在前面的话

> 有多少次，当你下载了一个可执行文件之后，你却不敢直接运行它？你是否需要一个干净的Windows安装环境，但是又懒得搭建一台虚拟机呢？

 **为了应对这种场景，微软开发了Windows
Sandbox：一款隔离的、临时性的桌面环境，用户可以在这个环境下运行不受信任的软件，而无需担心主机系统受到影响，因为任何安装在Windows
Sandbox中的软件就只会在沙盒环境中运行。Windows Sandbox关闭之后，所有的软件和文件都会被永久删除。**

 **Windows Sandbox的特点：Windows系统的默认组件、纯净版、一次性使用、安全和高效。**

### 依赖条件

> 1、 Windows 10专业版或企业版（[InsiderBuild
> 18305](https://blogs.windows.com/windowsexperience/2018/12/19/announcing-> windows-10-insider-preview-build-18305/)及以上版本）
>
> 2、 AMD 64位架构
>
> 3、 BIOS启用虚拟化功能
>
> 4、 至少4GB RAM（推荐8GB）
>
> 5、 至少1GB磁盘空间（推荐SSD）
>
> 6、 至少双核CPU（推荐四核超线程CPU）

## 快速开始

1、 安装Windows 10专业版或企业版，[InsiderBuild
18305](https://blogs.windows.com/windowsexperience/2018/12/19/announcing-windows-10-insider-preview-build-18305/)及以上版本。

2、 启用虚拟化：

a) 如果你使用的是物理设备，确保BIOS中开启了虚拟化功能；

b) 如果你使用的是虚拟设备，运行下列PowerShell命令启用嵌套虚拟化功能：

    
    
    Set-VMProcessor -VMName <VMName>-ExposeVirtualizationExtensions $true

3、 在控制面板中进入“启用或关闭Windows功能”，选择Windows Sandbox，点击“确定”，重启电脑后即可完成Windows
Sandbox的安装：

![微软官方沙盒Windows
Sandbox](https://image.3001.net/images/20181228/1545929929_5c2504c9abe59.png!small)

4、 点击“开始”菜单，找到Windows Sandbox，双击运行。

5、 从本地主机中复制一个可执行文件。

6、 将可执行文件粘贴到Windows Sandbox的运行窗口中。

7、 在Windows Sandbox中运行这个可执行文件，或完成程序安装。

8、 正常使用该程序。

9、 实验或分析完成后，关闭Windows Sandbox应用程序即可。沙盒环境下的所有内容都将被永久删除。

![微软官方沙盒Windows
Sandbox](https://image.3001.net/images/20181228/1545929938_5c2504d279788.png!small)

注：Windows Sandbox遵循主机的诊断数据设置，所有其他的隐私设置均为默认值。

## Windows Sandbox内部机制

Windows
Sandbox基于WindowsContainers（Windows容器）技术实现，WindowsContainers主要适用于云环境，微软基于该技术实现了Windows
Sandbox，并将其整合进了Windows 10中。

### 动态生成镜像

Windows Sandbox实际上是一款轻量级虚拟机，因此它需要操作系统镜像才可启动。Windows
Sandbox其中一个关键性升级，就是它可以使用本地主机的Windows10系统副本，因此用户无需再下载一个新的VHD镜像了。

在每次进行安全分析之前，我们都需要一个干净的分析环境，这里我们提出了“动态镜像”的概念：即保存一份纯净版的操作系统镜像，基于这个操作系统镜像做多个镜像拷贝，镜像拷贝文件可修改，但源镜像不可修改。其中的大部分文件均为链接，因此整个操作系统的大小非常小，约为100MB。

如果主机没有安装Windows
Sandbox，那么系统会将动态镜像以压缩包的形式存储，大小仅为25MB。但是安装之后，动态镜像数据包将会解压并占100MB磁盘空间。

![微软官方沙盒Windows
Sandbox](https://image.3001.net/images/20181228/1545929963_5c2504ebf3ade.png!small)

### 智能内存管理

内存管理是另一个整合进Windows内核的部分，Windows的管理程序允许单一物理设备分隔成多个共享相同物理硬件的虚拟机。这种方式虽然对传统的服务器负载效果比较好，但它不太适用于那些资源有限的设备，而Windows
Sandbox的优势就在于主机可以根据需要来从沙盒系统中回收内存。

除此之外，由于Windows Sandbox的运行基本上跟主机操作系统相同，因此Windows
Sandbox还可以通过“直接映射”技术来使用跟主机相同的物理内存页面。

![微软官方沙盒Windows
Sandbox](https://image.3001.net/images/20181228/1545929979_5c2504fb3a5b4.png!small)

### 集成内核调度器

对于普通虚拟机，Windows的管理程序主要控制的是运行在虚拟机中的虚拟进程。但Windows
Sandbox使用的是一种名叫“集成调度器”的新技术，这种技术允许主机来决定沙箱何时运行。

Windows Sandbox采用了独特的调度策略，允许以跟进程调度线程相同的方式来调度沙箱的虚拟处理器。

值得一提的是，大家可以把Windows Sandbox当做一个应用程序，但是它却能提供跟虚拟机一样的安全保护。

### 快照和克隆

Windows Sandbox的每一次启动其实并不需要花费完整的系统启动资源，因为这里使用了另外两种技术：即“快照”和“克隆”。

快照允许我们挂起沙箱环境，并将内存、CPU和设备状态存储在磁盘中。当我们需要一个新的Windows
Sandbox实例时，可以直接从磁盘恢复沙箱环境并将其放入内存中，这样显著降低了Windows Sandbox的启动时间。

## 结束语

希望大家能够充分利用这个Windows 10自带的沙盒环境，如果使用过程中遇到了任何问题，均可直接向微软提供报告或建议。

 *** 参考来源：[microsoft](https://techcommunity.microsoft.com/t5/Windows-Kernel-Internals/Windows-Sandbox/ba-p/301849)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

