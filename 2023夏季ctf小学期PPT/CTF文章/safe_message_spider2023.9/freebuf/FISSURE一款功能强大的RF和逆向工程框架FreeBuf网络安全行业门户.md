![](https://image.3001.net/images/20220923/1663938243_632daec32d65129e1fba9.jpeg!small)  

## 关于FISSURE

FISSURE是一款功能强大的RF和逆向工程框架，该工具适用于不同技能水平的安全研究人员，并提供了信号检测、信号分类、协议发现、渗透测试、IQ操作、漏洞分析、自动化和AI/机器学习等功能。该框架旨在促进软件模块、无线电、协议、信号数据、脚本、流程图、参考资料和第三方工具的快速集成。

FISSURE中包含的框架和工具旨在检测射频能量的存在，了解信号的特征，收集和分析样本，开发传输和/或注入技术，以及定制Payload。FISSURE包含一个不断增长的协议和信号信息库，以帮助进行数据识别、制作数据包和模糊测试。在线文档功能可用于下载信号文件，以模拟流量和测试系统。

友好的Python代码库和用户界面允许初学者快速学习涉及RF和逆向工程的流行工具和技术。网络安全和工程方面的教育工作者可以利用内置材料或利用框架来演示他们自己的实际应用。开发人员和研究人员可以使用FISSURE完成日常任务，或者向更广泛的受众展示他们的尖端解决方案。随着社区对FISSURE的认识和使用的增加，其能力的范围和所包含的技术的广度也会随之增加。

## 支持的硬件

> USRP: X3xx, B2xx, B20xmini, USRP2, N2xx
>
> HackRF
>
> RTL2832U
>
> 802.11 Adapters
>
> LimeSDR
>
> bladeRF, bladeRF 2.0 micro
>
> Open Sniffer
>
> PlutoSDR

## 工具组件

![](https://image.3001.net/images/20220923/1663938262_632daed6a3b90c528b85d.png!small)

## 工具版本及系统支持

FISSURE中有三个分支，可以简化文件导航并减少代码冗余。Python2_maint-3.7分支包含一个围绕Python2、PyQt4和GNU Radio
3.7构建的代码库；Python3_maint-3.8分支是围绕Python3、PyQt5和GNU Radio
3.8构建的；Python3_maint-3.10分支是围绕Python3、PyQt5和GNU Radio 3.10构建的。

 ** **操作系统****

|

 ** **FISSURE**** ** **分支****  
  
---|---  
  
Ubuntu 18.04 (x64)

|

Python2_maint-3.7  
  
Ubuntu 18.04.5 (x64)

|

Python2_maint-3.7  
  
Ubuntu 18.04.6 (x64)

|

Python2_maint-3.7  
  
Ubuntu 20.04.1 (x64)

|

Python3_maint-3.8  
  
Ubuntu 20.04.4 (x64)

|

Python3_maint-3.8  
  
KDE neon 5.25 (x64)

|

Python3_maint-3.8  
  
## 工具安装

广大研究人员可以使用下列命令将该项目克隆至本地，并完成工具的安装和配置：

    
    
    git clone https://github.com/ainfosec/FISSURE.git
    
    cd FISSURE
    
    git checkout <Python2_maint-3.7> or <Python3_maint-3.8> or <Python3_maint-3.10>
    
    git submodule update --init
    
    ./install

上述命令还将下载PyQt软件依赖以启动图形化界面。接下来，工具将根据你的操作系统来选择最佳的匹配版本：

 **Python2_maint-3.7**

![](https://image.3001.net/images/20220923/1663938284_632daeecde2531ac73c58.png!small)

 **Python3_maint-3.8**

![](https://image.3001.net/images/20220923/1663938291_632daef3bbbdb2dee7a1a.png!small)

 **Python3_maint-3.10**

![](https://image.3001.net/images/20220923/1663938298_632daefa76ebfab051af9.png!small)

我们建议在新装的操作系统上安装和配置FISSURE以避免存在冲突。选择所有建议的复选框（默认按钮），以避免在FISSURE中操作各种工具时出错。在整个安装过程中会出现多个提示，主要是要求提升权限和用户名。如果项目末尾包含“验证”部分，安装程序将运行后面的命令，并突出显示复选框项目绿色或红色，具体取决于该命令是否产生任何错误。没有“验证”部分的选中项目在安装后将保持黑色。

![](https://image.3001.net/images/20220923/1663938304_632daf00bd9ea44315821.png!small)

## 工具使用

打开命令行终端并运行下列命令即可执行FISSURE：

    
    
    fissure

## 工具运行截图

![](https://image.3001.net/images/20220923/1663938325_632daf15c06fc91b23660.png!small)

![](https://image.3001.net/images/20220923/1663938342_632daf2646d730a1dd7e0.png!small)

![](https://image.3001.net/images/20220923/1663938349_632daf2ddee629eb6ec87.png!small)

![](https://image.3001.net/images/20220923/1663938356_632daf3492645012533aa.png!small)

![](https://image.3001.net/images/20220923/1663938363_632daf3b019ce26344038.png!small)

![](https://image.3001.net/images/20220923/1663938373_632daf454930b18c7ca47.png!small)

![](https://image.3001.net/images/20220923/1663938381_632daf4d318f373942c3f.png!small)

![](https://image.3001.net/images/20220923/1663938388_632daf54e314696e82450.png!small)

![](https://image.3001.net/images/20220923/1663938396_632daf5cbb790eab11942.png!small)

![](https://image.3001.net/images/20220923/1663938404_632daf646fca8650020b0.png!small)

![](https://image.3001.net/images/20220923/1663938411_632daf6b3d171925684c7.png!small)

![](https://image.3001.net/images/20220923/1663938419_632daf731fb92d8232653.png!small)

## 许可证协议

本项目的开发与发布遵循[ _GPL_
_-3.0_](https://github.com/ainfosec/FISSURE/blob/Python3_maint-3.8/LICENSE)开源许可证协议。

## 项目地址

 **FISSURE** ：【[ _GitHub传送门_](https://github.com/ainfosec/FISSURE)】

