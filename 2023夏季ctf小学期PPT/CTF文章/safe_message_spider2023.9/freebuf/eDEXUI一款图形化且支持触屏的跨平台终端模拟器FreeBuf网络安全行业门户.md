![](https://image.3001.net/images/20201116/1605480929_5fb1b1e1a550e1588bec3.png!small)

## eDEX-UI

eDEX-UI是一款图形化且支持触屏的跨平台终端模拟器，该工具支持全屏运行，使用起来就像科幻电影里的计算机界面，除了终端模拟之外，它还可以帮助广大研究人员实现系统监控。

eDEX-UI的设计灵感主要来自于黑客电影里的计算机界面效果，在保持未来感的同时，它还能够同时保持程序的功能可用性，并且支持在现实的生活场景中使用，也就是说，eDEX-UI将未来带到了现在。

## 功能介绍

  * 全功能终端模拟器，提供了标签、颜色高亮显示、鼠标事件和应用程序支持；
  * 实时系统（CPU、RAM和进程）和网络监控（IP地理位置、活动链接和传输速率）；
  * 完全支持触摸显示，包括屏幕键盘；
  * 遵循终端的CWD（当前工作目录）的目录查看器；
  * 高级定制使用主题，屏幕键盘布局，CSS注入；
  * 由一个天才的声音设计师为最大限度的好莱坞黑客氛围制作的可选音效；

## 工具安装

广大研究人员可以直接点击【[ _这里_](https://github.com/GitSquared/edex-ui/releases)】访问该项目的[
_Releases页面_](https://github.com/GitSquared/edex-ui/releases)，直接下载对应系统版本的预编译程序。

或者说，大家可以使用自己的包管理器（例如HomeBrew或AUR等）来进行工具的安装和配置。

![](https://image.3001.net/images/20201116/1605480961_5fb1b201916d10a6a8f9a.png!small)

## 为什么浏览器弹出“Tracking Failed”报错？（仅Windows）

因为在Linux和macOS系统下，eDEX可以跟踪终端选项卡中的当前位置，以便在屏幕上显示当前文件夹的内容。遗憾的是，这在技术上是不可能在Windows上实现的，所以文件浏览器会恢复到“分离”模式。但我们仍然可以使用它来浏览文件和目录，并单击文件来在终端中输入它们的路径。

## 是否支持在树莓派或ARM设备上使用？

当前版本的eDEX还不支持在ARM设备上使用，但是大家可以自己动手尝试针对ARM平台来重新编译工具代码，具体可以参考【 _这里_】。

## 其他命令

注意：下列操作指令适用于运行开发版本（最新非稳定版）的eDEX。

### 从源码获取

在类Unix系统上，我们可以运行下列命令（如果使用的是macOS，则需要设备上安装好Xcode）：

    
    
    git clone https://github.com/GitSquared/edex-ui.git
    
    npm run install-linux
    
    npm start

在Windows下，首先我们需要以管理员权限打开一个终端或PowerShell窗口，然后运行下列命令：

    
    
    git clone https://github.com/GitSquared/edex-ui.git
    
    npm run install-windows
    
    npm start

### 代码构建

注意：由于工具的原生模块，我们只能针对特定的主机操作系统构建目标：

    
    
    npm install（并非install-linux或install-windows）
    
    npm run build-linux或build-windows或build-darwin

脚本将多源代码进行优化，重新编译本地依赖项，然后在dist目录中创建可分发的程序组件。

## 工具运行截图

![](https://image.3001.net/images/20201116/1605481007_5fb1b22fc0c55fd1105e6.png!small)

![](https://image.3001.net/images/20201116/1605481015_5fb1b237c02b5e18e20c0.png!small)

![](https://image.3001.net/images/20201116/1605481024_5fb1b24047803f421387e.png!small)

## 项目地址

eDEX-UI：【[ _GitHub传送门_](https://github.com/GitSquared/edex-ui)】

