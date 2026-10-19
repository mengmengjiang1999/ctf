![](https://image.3001.net/images/20230830/1693368257_64eebfc17c1b688f1cc1c.jpeg!small)

## 关于GitBackdorizer

GitBackdorizer是一款针对Git的安全研究工具，在该工具的帮助下，广大研究人员可以轻松对Git库进行安全扫描，并尝试识别开发人员意外遗漏在代码库中的Git访问凭证。

## 工作机制

GitBackdorizer主要由三个组件组成，即Handler、Dropper和Payload。

### Handler

Handler将设置一台HTTP服务器，并尝试捕捉凭证以及向Dropper的Payload提供一个配置菜单，而Dropper则由研究人员负责传递和发送。

### Dropper

Dropper在设计时就具备了较高的兼容性，以避免任何非sh的特定功能所导致的问题，该组件的工作机制如下：

> 1、识别GitBackdorizer的Git钩子是否已设置成功；
>
> 2、将后门Payload投放至指定的钩子；
>
> 3、提供可执行权限；

### Payload

Payload仍然是按照最高级别兼容性设计的，以避免任何非sh的特定功能所导致的问题。当前该模块提供了两种类型的Payload，即常规Payload和预推送Payload。

常规Payload会尝试通过下列方式识别远程类型（HTTPS/SSH）：

> 1、检测当前分支：git branch --contains HEAD；
>
> 2、收集分支的远程名称（通过Git配置实现）；
>
> 3、收集分支远程名称的远程URL（通过Git配置实现），并检测URL使用的是HTTPS或SSH；

预推送Payload则负责直接对URL执行检测，并提供URL的相关Git信息。

## 工具下载

由于该工具基于纯Python开发，因此我们首先需要在本地设备上安装并配置好Python环境。接下来，广大研究人员可以直接使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/UnkL4b/GitBackdorizer.git

然后切换到项目目录中，使用pip工具和项目提供的requirements.txt文件安装该工具所需的其他依赖组件：

    
    
    cd GitBackdorizer/
    
    pip install requirements.txt

## 工具使用演示

在下面的例子中，我们将演示如何使用GitBackdorizer检测和提取Git库中遗留的Git访问凭证：

 **演示视频** ：【[ _点我观看_](https://www.youtube.com/watch?v=ka8uJqaDYOs)】

## 许可证协议

本项目的开发与发布遵循[ _GPL_
_-3.0_](https://github.com/UnkL4b/GitBackdorizer/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **GitBackdorizer** ：【[
_GitHub传送门_](https://github.com/UnkL4b/GitBackdorizer)】

## 参考资料

> [ _https://github.com/ulissescastro_](https://github.com/ulissescastro)
>
> [ _https://www.slideshare.net/ulissescastro/50-ton-of-> backdoors_](https://www.slideshare.net/ulissescastro/50-ton-of-backdoors)
>
> [ _https://github.com/giovanifss/_](https://github.com/giovanifss/)

