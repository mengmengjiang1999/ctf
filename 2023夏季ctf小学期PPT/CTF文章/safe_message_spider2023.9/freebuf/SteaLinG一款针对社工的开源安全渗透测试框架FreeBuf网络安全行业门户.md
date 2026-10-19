![](https://image.3001.net/images/20221017/1665939124_634c36b4af6dd42adbd30.jpg!small)

## 关于SteaLinG

SteaLinG是一款功能强大的开源渗透测试框架，该框架专为社会工程学研究人员设计，可以帮助广大研究人员或组织内的安全专家测试目标设备的安全性。该工具基于Python开发，因此具备良好的跨平台特性。在使用时，我们只需要将其上传至目标用户设备并运行SteaLinG即可。

该工具仅用于教育或测试目的，请在授权范围内使用。

## 功能介绍

该工具包含下列功能模块：

> 1、密码转储：支持获取设备中保存的所有密码，并会将保存密码的文件上传至Mega或Pastebin；
>
> 2、历史记录转储：支持导出目标设备浏览器历史记录；
>
> 3、文件导出：支持从目标设备硬盘驱动器导出文件，可自定义目标文件后缀；
>
> 4、Telegram会话劫持：支持进行Telegram会话劫持；
>
> 5、支持Linux；
>
> 6、Dropper；

## 工具运行流程

![](https://image.3001.net/images/20221017/1665939144_634c36c8b1b51b3cbc704.png!small)

## 工具要求

> Python：版本需>= 3.8++；
>
> 操作系统：Windows或Linux；

## 工具安装

首先，该工具基于Python开发，因此广大研究人员首先需要在本地设备上安装并配置好Python环境。

接下来，可以按照下列方法在不同操作系统平台上安装SteaLinG。

### Windows安装

    
    
    git clone https://github.com/De3vil/SteaLinG.git
    
    cd SteaLinG
    
    pip install -r requirements.txt
    
    python SteaLinG.py

### Linux安装

    
    
    git clone https://github.com/De3vil/SteaLinG.git
    
    cd SteaLinG
    
    chmod +x linux_setup.sh
    
    bash linux_setup.sh
    
    python SteaLinG.py

## 注意事项

请不要将相关内容上传至VirusTotal.com，因为Virustotal会将代码签名与反病毒产品共享。

## 工具使用

### 启动界面&工具选项

![](https://image.3001.net/images/20221017/1665939189_634c36f566f7a96f100c1.png!small)

### 反病毒产品检测

![](https://image.3001.net/images/20221017/1665939196_634c36fcae81991ca82c3.png!small)

## 项目地址

 **SteaLinG** ：【[ _GitHub传送门_](https://github.com/De3vil/SteaLinG)】

## 参考资料

> [
> _https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe﻿_](https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe)

