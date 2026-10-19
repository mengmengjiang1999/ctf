**今天给大家介绍的是一款名叫PeekABoo的工具，该工具适用于内部渗透测试或网络攻击的后渗透阶段。在PeekABoo的帮助下，研究人员可以直接在目标设备上启用远程桌面访问。该工具使用PowerShell来远程执行访问任务。**

![1.jpg](https://image.3001.net/images/20190517/1558028358_5cdda04685326.jpg!small)

## PeekABoo

该工具只有在启用了WinRM的环境下才可以正常使用，所有Windows服务器版的操作系统中，Windows Server 2012
WinRM都是默认启用了的，客户端操作系统就正好相反了，默认是没有启用该功能的。

注意：所有的Windows操作系统都默认禁用了远程桌面功能。

## 工具运行截图

在下面给出的样例中，目标设备位于uoge内部网络中，并禁用了RDP：

![2.png](https://image.3001.net/images/20190517/1558028370_5cdda05214263.png!small)

可以通过“选项2”开启目标设备的远程桌面服务：

![3.png](https://image.3001.net/images/20190517/1558028375_5cdda057032c6.png!small)

成功在目标设备上启用了远程桌面服务：

![4.png](https://image.3001.net/images/20190517/1558028379_5cdda05b9c904.png!small)

## 工具安装

    
    
    git clone <https://github.com/Viralmaniar/PeekABoo.git>
    
    cd PeekABoo
    
    python peekaboo.py

## 如何使用？

输入1：将PowerShell修改为非受限模式；

输入2：启用目标设备的远程桌面服务，并显示RDP端口（3389）状态；

输入3：禁用目标设备的远程桌面服务；

输入4：退出PeekABoo；

## 依赖组件

1、
从项目的[release页面](https://github.com/Viralmaniar/PeekABoo/releases)下载可执行文件以及[PowerShell文件](https://github.com/Viralmaniar/PeekABoo/releases)，或者直接从GitHub库将源代码克隆至本地，并使用PyInstaller安装。

2、 使用Pyinstaller将peekaboo.py编译为可执行文件；

3、 可以使用pip安装PyInstaller：

    
    
    pip install pyinstaller

## 项目地址

PeekABoo：【[Viralmaniar](https://github.com/Viralmaniar/PeekABoo)】

 ***
参考来源：[Viralmaniar](https://github.com/Viralmaniar/PeekABoo)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

