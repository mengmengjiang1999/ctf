![](https://image.3001.net/images/20210505/1620200703_60924cff95fbbf7d34e23.png!small)

## 关于Evasor

 **Evasor是一款专为蓝队和红队研究人员设计的安全工具** ，
**该工具可以用于渗透测试任务中的后渗透接断，并能够帮助研究人员绕过APPLICATIONCONTROL策略。**

本质上来说，Evasor是一款自动化的安全审计工具，该工具能够绕过任意应用程序控制规则，支持在Windows操作系统上运行。该工具易于使用，运行速度也非常快，可以自动化生成分析报告，其中包含任务描述、截图和缓解方案建议。

## 工具要求

Windows操作系统；

Visual Studio 2017；

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/cyberark/Evasor.git

## 工具使用样例

下载并编译完成Evasor项目源码之后，我们需要在引用数种找到App.config文件，以验证项目的执行：

![](https://image.3001.net/images/20210505/1620200719_60924d0fd6ad800170504.png!small)

在项目的bin目录下运行Evasor.exe，根据你的需要选择对应任务的数字选项：

![](https://image.3001.net/images/20210505/1620200728_60924d1890f7d997e2f7f.png!small)

首先，找到能够用于绕过应用程序控制的可执行文件。这里我们可以通过下列两种方式实现：

检索所有正在运行进程的相关路径；

检查每一个进程，判断是否存在DLL注入漏洞：运行“MavInject”微软组件，路径为“C:\Windows\System32\mavinject.exe”。或者，检查MavInject执行的退出代码，如果进程存在，则说明该进程存在DLL注入漏洞，可以用于实现应用程序控制绕过；

接下来，定位存在DLL劫持漏洞的进程：

检索所有正在运行的进程；

针对每一个正在运行的进程：获取已加载的进程模块；通过创建空文件判断是否拥有正在运行进程所在目录的写入权限，文件命名为已加载模块（DLL）；如果写入操作成功，则说明存在DLL劫持漏洞；

最后，定位潜在的可劫持资源文件：

搜索目标设备上的指定文件；

尝试替换该文件，以验证文件是否可替换，判断是否存在资源劫持漏洞；

支持的扩展名:xml、config、json、bat、cmd、ps1、vbs、ini、js、exe、dll、msi、yaml、lib、inf、reg、log、htm、hta、sys、rsp；

生成自动化审计Word文档报告，包含测试描述和运行截图；

## 项目地址

Evasor：【[ _GitHub传送门_](https://github.com/cyberark/Evasor)】

## 许可证协议

本项目的开发与发布遵循[ _Apache License
2.0开源许可证协议_](https://github.com/cyberark/Evasor/blob/master/LICENSE)。

## 参考资料

> [ _https://github.com/cyberark/conjur-api-> go/blob/master/CONTRIBUTING.md_](https://github.com/cyberark/conjur-api-> go/blob/master/CONTRIBUTING.md)
>
> [ _https://github.com/cyberark/_](https://github.com/cyberark/)

