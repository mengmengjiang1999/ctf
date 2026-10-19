![](https://image.3001.net/images/20230810/1691645653_64d476d5e7cb5d8aa19d2.jpg!small)  

## 关于Wanderer

Wanderer是一款功能强大的进程注入枚举工具，该工具基于C#开发，代码完全开源，可以帮助广大研究人员收集与正在运行的目标进程相关的信息。支持收集的信息包括完整性级别、AMSI是否作为加载模块存在、目标进程是以64位或32位运行的、以及当前进程的去特权级别。这些数据信息在研究人员尝试构建Payload并实现进程注入时，将会提供非常大的帮助。

## 工具下载

由于该工具基于C#开发，因此我们需要在本地设备上安装并配置好最新版本的Visual
Studio。接下来，广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/gh0x0st/wanderer.git

然后打开Visual Studio，导入项目源码并完成编译即可运行Wanderer。

## 工具使用

    
    
    PS C:\> .\wanderer.exe
    
     
    
         >> Process Injection Enumeration
    
         >> https://github.com/gh0x0st
    
         
    
    Usage: wanderer [target options] <value> [filter options] <value> [output options] <value>
    
     
    
    Target Options:
    
     
    
    -i, --id, 通过ID设置单个目标或进程组
    
    -n, --name, 通过进程名称设置单个目标或进程组
    
    -c, --current, 针对目标进程查看特权级别
    
    -a, --all, 设置所有正在运行的进程为目标进程
    
     
    
    Filter Options:
    
     
    
    --include-denied, 包含无法反问的进程实例
    
    --exclude-32, 排除进程体系结构为32位的实例
    
    --exclude-64, 排除进程体系结构为64位的实例
    
    --exclude-amsiloaded, 排除已加载amsi.dll的进程模块实例
    
    --exclude-amsiunloaded, 排除未加载amsi.dll的进程模块实例
    
    --exclude-integrity, 排除进程完整性级别为特定值的实例
    
     
    
    Output Options:
    
     
    
    --output-nested, 在嵌套样式视图中输出结果
    
    -q, --quiet, 不输出banner

## 工具使用样例

枚举进程ID为12345的进程：

    
    
    C:\> wanderer --id 12345

枚举所有名为process1和process2的进程：

    
    
    C:\> wanderer --name process1,process2

枚举当前进程特权级别：

    
    
    C:\> wanderer --current

枚举所有32位进程：

    
    
    C:\wanderer --all --exclude-64

枚举加载了AMSI的所有进程：

    
    
    C:\> wanderer --all --exclude-amsiunloaded

枚举进程名为pwsh、powershell、spotify的进程，且完整性级别不受信（包括32位进程）：

    
    
    C:\> wanderer --name pwsh,powershell,spotify --exclude-integrity untrusted,low --exclude-32

## 工具运行截图

![](https://image.3001.net/images/20230810/1691645705_64d47709e137bbe003ac1.png!small)

![](https://image.3001.net/images/20230810/1691645712_64d477104673e1bfadda2.png!small)

![](https://image.3001.net/images/20230810/1691645718_64d47716569e80b00656c.png!small)

![](https://image.3001.net/images/20230810/1691645723_64d4771b9a9740eefdf2f.png!small)

![](https://image.3001.net/images/20230810/1691645729_64d477213946fc52de250.png!small)

## 许可证协议

本项目的开发与发布遵循[ _GPL_
_-3.0_](https://github.com/gh0x0st/wanderer/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **Wanderer** ：【[ _GitHub传送门_](https://github.com/gh0x0st/wanderer)】

