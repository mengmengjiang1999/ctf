## 一、背景概述

**近期，深信服安全团队接到客户反馈，内网中出现了大量伪造成文件夹的可疑exe文件，删掉以后仍会反复。经深信服安全团队分析发现，这是一个蠕虫病毒FakeFolder，该病毒会通过U盘及共享文件夹进行传播，一旦主机感染了该病毒，文件系统中的文件夹都会被隐藏，取而代之的是一个伪装的病毒文件，当用户运行病毒文件时，也会弹出对应文件夹的窗口，因此不易被察觉；只要系统中还残留着一个FakeFolder病毒文件，就会对主机进行反复感染。**

深信服安全团队提取了该蠕虫病毒文件，并对其进行了详细的技术。

## 二、病毒原理

[1] 病毒首先会创建一个子进程并注入恶意代码进行核心操作，从而避开杀软的查杀。

[2] 子进程会释放要给ghi.bat脚本进行主机、网络信息的收集。

[3] 进行完以上操作后，病毒开始感染文件夹，并配和autorun.inf实现重复感染。

[4] 最后，病毒还有创建两个定时器，定时监控注册表实现持久化攻击，以及定时访问windows服务器实现伪装。

![](https://image.3001.net/images/20190422/1555936424_5cbdb4a8b1234.png!small)

## 三、病毒现象

被感染主机，系统中的文件夹全部变成了328KB的可执行文件：

![](https://image.3001.net/images/20190422/1555936433_5cbdb4b1c26be.png!small)

病毒为一个文件夹图标的wmimgmt.exe进程：

![](https://image.3001.net/images/20190422/1555936437_5cbdb4b551244.png!small)

## 四、病毒母体分析

病毒使用MFC编写，首先会进行一些初始化操作，包括：获取system32路径、动态获取系统函数地址、获取系统安装的杀软信息，如果没有安装卡巴斯基则执行后续恶意行为：

![](https://image.3001.net/images/20190422/1555936441_5cbdb4b945351.png!small)

若未检测到杀软进程，则病毒代码将进入到0x402DD0开始进程注入的操作。

### 4.1 注入环节（0x402F70 -> 0x402DD0）

该环节，病毒会读取资源节中的恶意代码（一个PE文件），然后以挂起状态创建子进程，调用WriteProcessMemory将恶意PE注入子进程并恢复进程：

![](https://image.3001.net/images/20190422/1555936453_5cbdb4c570ebc.png!small)

## 五、注入恶意代码分析（0x40B070）

我们将注入的恶意代码dump下来,分析发现,该段恶意代码首先会判断程序当前路径是否为C:\ProgramData\ApplicationData或C:\Documents
andSettings\All
Users，如果不是，则将其拷贝到相应目录下命名为wmimgmt.exe并运行。重复上述操作后，跳到0x40BE00执行核心恶意操作：

![](https://image.3001.net/images/20190422/1555936459_5cbdb4cbc7269.png!small)

### 5.1 收集信息环节（0x40B070 -> 0x40BE00）

恶意代码会创建3个线程，分别执行创建互斥量、遍历磁盘、释放病毒脚本的操作：

![](https://image.3001.net/images/20190422/1555936463_5cbdb4cfca63d.png!small)

脚本名为ghi.bat，主要操作为获取系统、网络以及进程信息：

![](https://image.3001.net/images/20190422/1555936608_5cbdb560cb84d.png!small)

做完以上操作后，会使用DialogBoxParamA创建一个模态对话框，用于监控执行恶意功能。

### 5.2 定时操作环节（0x40B070 -> 0x40BE00 -> 0x40BF70）

调用SetTimer设置2个定时器，分别为10秒和30秒，定时触发后面3个行为：

[1]HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced\Folder\SuperHidden\UncheckedValue置为0，不显示隐藏文件及文件夹。

![](https://image.3001.net/images/20190422/1555936653_5cbdb58deee31.png!small)

[2] 添加开机自启动项HKLM\Software\Microsoft\Windows\CurrentVersion\Run\wmi32：

![](https://image.3001.net/images/20190422/1555936657_5cbdb5917c286.png!small)

[3]查询域名“windowsupdate.microsoft.com”地址：

![](https://image.3001.net/images/20190422/1555936660_5cbdb59498805.png!small)

### 5.3 感染磁盘环节（0x40B070-> 0x40BE00 -> 0x40BF70 -> 0x40C460）

当初始化或者硬件设备发生改变时，回调的方式执行DialogFunc执行感染流程，感染对象为USB磁盘和网络磁盘：

![](https://image.3001.net/images/20190422/1555936665_5cbdb599b2f46.png!small)

经过一系列的判断，终于来到了感染的核心环节，病毒会创建
C:\RECUCLER\wmimgmt.exe和AuToRUn.iNf实现重复感染。wmimgmt.com为病毒的克隆体。AuToRUn.iNf的代码如下，功能为当用户打开文件夹时，自动执行C:\RECYCLER\wmimgmt.exe重复感染：

![](https://image.3001.net/images/20190422/1555936670_5cbdb59e430f5.png!small)

wmimgmt.exe病毒文件有特殊属性，在正常情况下不会显示出来：

![](https://image.3001.net/images/20190422/1555936674_5cbdb5a298c3b.png!small)

最后，便是执行我们开头见到的篡改文件夹操作，病毒先将原文件夹隐藏，然后将病毒自身克隆成文件夹的样子，命名为“文件夹名+.exe”：

![](https://image.3001.net/images/20190422/1555936678_5cbdb5a672855.png!small)

运行感染的病毒程序，会打开病毒所伪装的文件夹，从而避免被受害者发现异常：

![](https://image.3001.net/images/20190422/1555936684_5cbdb5aca5c95.png!small)

感染后的文件夹如下图所示：

![](https://image.3001.net/images/20190422/1555936688_5cbdb5b0267e4.png!small)

## 解决方案

深信服为广大用户免费提供查杀工具，可下载如下工具，进行检测查杀。

> 64位系统下载链接：<http://edr.sangfor.com.cn/tool/SfabAntiBot_X64.7z>
>
> 32位系统下载链接：<http://edr.sangfor.com.cn/tool/SfabAntiBot_X86.7z>

 ***本文作者：深信服千里目安全实验室，转载请注明来自FreeBuf.COM**

