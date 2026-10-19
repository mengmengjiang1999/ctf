**本文介绍一款名叫IoT-Home-Guard的安全检测工具，广大研究人员可使用该工具来检测物联网设备中的恶意行为。**

![IoT-Home-Guard](https://image.3001.net/images/20190314/1552532040_5c89c248556b8.png!small)

## IoT-Home-Guard

IoT-Home-Guard这款软件不仅可以帮助用户发现智能家居设备／物联网设备中的恶意软件，而且还可以帮助检测已被入侵的智能家居设备。对于安全研究人员来说，它还可以进行网络分析和恶意行为检测。

2018年7月份，我们发布了该工具的第一个版本，并在2018年10月份完成了第二个版本的开发，新版本大幅提升了用户体验度，并增加了可识别设备的数量及种类。

第一代IoT-Home-Guard是一款基于树莓派（带有无线网络接口控制器）开发的硬件设备，我们在第二代IoT-Home-Guard上使用了全新的自定义固件，并支持在笔记本上进行环境配置，相关软件可在项目目录的software_tools/文件夹中找到。

## 工作机制

该工具主要通过检测恶意网络流量来进行恶意行为的扫描与发现。植入了恶意软件的设备会尝试与远程服务器进行通信，并触发远程Shell或向服务器发送音频/视频。

下图显示的是一款植入了数据嗅探型恶意软件的网络流量情况：

> 红线：设备与恶意远程服务器之间的通信流量；
>
> 绿线：设备的正常通信流量；
>
> 黑线：TCP流量总和

![IoT-Home-Guard](https://image.3001.net/images/20190314/1552532050_5c89c25289a1a.png!small)

## 功能模块

> 1、 AP模块和数据流捕捉模块：捕捉网络通信流量；
>
> 2、 流量分析引擎：从网络流量中提取特征，并与设备指纹数据库进行比对；
>
> 3、 设备指纹数据库：存储了每一种设备正常的网络行为，该模块基于白名单实现，可调用360威胁情报数据库（<https://ti.360.net/>）；
>
> 4、 Web服务器：第二代中引入了Web服务器

## 工作流程图

![IoT-Home-Guard](https://image.3001.net/images/20190314/1552532063_5c89c25f92b74.png!small)

## 工具演示

在我们的研究过程中，我们利用IoT-Implant-Toolkit（可查看Freebuf针对该工具的介绍文档）成功在八台设备上植入了木马，其中包括智能扬声器、摄像头、行车记录仪和移动翻译器等等。

![IoT-Home-Guard](https://image.3001.net/images/20190314/1552532336_5c89c3701e66c.gif!small)

我们收集到了这些设备的特征信息，然后运行IoT-Home-Guard，最终成功检测到了所有设备上植入的木马。我们认为，以这样的方式来检测目标设备中的恶意行为，再配合上恶意特征数据库的话，检测准确率会非常高。

## 软件安装与使用

搭建环境：

    
    
    git clone https://github.com/arthastang/IoT-Home-Guard
    cd IoT-Home-Guard/software_tools/
    python setup.py install

你可以使用下列命令来检测目标设备是否已被植入了木马：

    
    
    ./IoT-Home-Guard.py

运行下列命令搭建Web服务器（使用8080端口）：

    
    
    ./homeguard

### 运行截图

![IoT-Home-Guard](https://image.3001.net/images/20190314/1552532117_5c89c295a45fb.png!small)![IoT-Home-Guard](https://image.3001.net/images/20190314/1552532126_5c89c29ea288d.png!small)

## 项目地址

IoT-Home-Guard：【[GitHub传送门](https://github.com/arthastang/IoT-Home-Guard)】

### 参考资料

IoT-Home-Guard软件操作指南：【[传送门](https://github.com/arthastang/IoT-Home-Guard/blob/master/software_tools/README.md)】

IoT-Home-Guard硬件操作指南：【[传送门](https://github.com/arthastang/IoT-Home-Guard/blob/master/hardware_tool/README.md)】

 *** 参考来源：[arthastang](https://github.com/arthastang/IoT-Home-Guard)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

