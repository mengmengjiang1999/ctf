笔者查阅网上相关资料，尝试在windows环境下编译谷歌浏览器，发现相关资料部分太老，部分未考虑国内的上网环境。本文以windows10操作系统和vs2019为例，编译最新版谷歌浏览器（2021.05）。

## 一、系统要求

官网要求：

1.64位Intel 机器，最低8GB内存，推荐16GB以上内存。

2.硬盘格式NTFS，至少剩余100GB空间。因为git文件包大于4G，所以FAT32格式硬盘不支持。

3.Visual Studio最低版本为2017 (>=15.7.2)，推荐使用VS2019 (>=16.0.0)。

4.windows10操作系统或者更新（还有什么更新的操作系统）。

## 二、环境搭建：

### 1.Visual Studio

最新版Chromium要求Visual Studio最低版本为2017 (>=15.7.2)，推荐使用VS2019 (>=16.0.0)
，这里使用vs2019进行编译。官网上提示，如果只编译64位谷歌浏览器vs安装的时候需要安装如下组件：

$ PATH_TO_INSTALLER.EXE

\--add Microsoft.VisualStudio.Workload.NativeDesktop

\--add Microsoft.VisualStudio.Component.VC.ATLMFC

\--includeRecommended

如果同时编译32位和64位浏览器则需要安装如下组件：

$ PATH_TO_INSTALLER.EXE

\--add Microsoft.VisualStudio.Workload.NativeDesktop

\--add Microsoft.VisualStudio.Component.VC.ATLMFC

\--add Microsoft.VisualStudio.Component.VC.Tools.ARM64

\--add Microsoft.VisualStudio.Component.VC.MFC.ARM64

\--includeRecommended

实际安装过程中，安装下图中3个工作载荷即可满足需求。

![](https://image.3001.net/images/20210524/1621863506_60abac52a6a455f11a84c.png!small)

安装完成后，添加Visual Studio安装路径的环境变量，set vs2019_install=C:\Program Files
(x86)\Microsoft Visual
Studio\2019\Professional，具体方法为：打开控制面板→系统和安全→系统→高级系统设置→环境变量→新建

![](https://image.3001.net/images/20210524/1621863557_60abac851f8cea60e47af.png!small)

### 2.安装depot_tools

工具下载地址：[ _https://storage.googleapis.com/chrome-infra/depot_tools.zip_](https://storage.googleapis.com/chrome-infra/depot_tools.zip)，下载后将压缩包解压到
pathto/depot_tools，同时将pathto/depot_tools添加到环境变量Path中。

![](https://image.3001.net/images/20210524/1621863951_60abae0f4426e104e3b50.png!small)

此外，以同样的方式添加DEPOT_TOOLS_WIN_TOOLCHAIN系统变量，并将其设置为 0。这样depot_tools会使用本地安装的Visual
Studio。

![](https://image.3001.net/images/20210524/1621863991_60abae37bd09abb21e034.png!small)

## 3.Windows 10 SDK安装

按照上述方法安装Visual Studio会安装好Windows 10 SDK (10.0.19041.0)，在编译过程中还会用到"Debugging
Tools for Windows”。从[ _Windows 10 SDK - Windows 应用开发
(microsoft.com)_](https://developer.microsoft.com/zh-cn/windows/downloads/windows-10-sdk/)下载相关安装包，安装SDK Debugger-x86_en-us.msi即可。

![](https://image.3001.net/images/20210524/1621863489_60abac4174556d3170ff5.png!small)

![](https://image.3001.net/images/20210524/1621864049_60abae7148b6f76e5d124.png!small)

如果不安装配置生成VS解决方案时会报错

![](https://image.3001.net/images/20210524/1621864147_60abaed38f4808403cf84.png!small)

## 三、源码及依赖下载：

### 1.配置Gi:

$ git config --global user.name "My Name"

$ git config --global user.email "my-name@chromium.org"

$ git config --global core.autocrlf false

$ git config --global core.filemode false

$ git config --global branch.autosetuprebase always

### 2.创建文件夹

$ mkdir chromium && cd chromium

### 3.利用depot_tools工具包中的fetch拉取源码及其依赖。

$ fetch chromium

如果不想下整个仓库，只下最新代码，可以使用fetch --no-history
chromium，减少下载量。这个过程会比较麻烦，因为即使使用虚拟专用网上网，某些域名依然访问不到，导致下载失败，解决相关问题后通过$ gclient
sync恢复下载。

下面介绍使用虚拟专用网上网，某些域名依然访问不到的解决办法。通过[
_http://mping.chinaz.com/_](http://mping.chinaz.com/)网站，获取该域名的海外解析IP。

![](https://image.3001.net/images/20210524/1621864075_60abae8b9f8126637d755.png!small)

随后编辑C:\Windows\System32\drivers\etc\hosts文件，如果没有新建一个，将访问不到的域名及海外解析IP添加到该文件中。

172.217.160.112 commondatastorage.googleapis.com

172.217.160.84 chrome-infra-packages.appspot.com。

下载完成后的目录如下：

![](https://image.3001.net/images/20210524/1621864111_60abaeaf8cb4ec6db1e60.png!small)

## 四、编译代码：

默认的编译命令如下：

$cd src && gn gen out/Default

可以通过设置一些参数来改变编译选项，具体的编译参数可以参考官网文件。

is_component_build = true-这使用更多、更小的DLL和增量链接。

enable_nacl = false-这禁用本地客户端，这通常是不需要为本地生成。

target_cpu = "x86"-x86构建速度略快于x64,生成和支持增量链接以适应更多目标。

![](https://image.3001.net/images/20210524/1621864207_60abaf0f1666243b9ebc6.png!small)

### 2.生成chrome

autoninja -C out\VSDebug

![](https://image.3001.net/images/20210524/1621864281_60abaf59b02d8b90fbc3b.png!small)

  

