![](https://image.3001.net/images/20211126/1637913986_61a0958256d3377fef800.png!small)

## 关于Qu1cksc0pe

Qu1cksc0pe是一款功能强大的多合一恶意软件分析工具，该工具可以帮助广大研究人员分析Windows、Linux和macOS平台下的可执行文件以及APK文件等。Qu1cksc0pe可以给分析人员提供下列信息：

> 可执行文件或应用程序使用了哪些DLL文件；
>
> 包含的功能函数和API接口；
>
> 数据字段；
>
> URL、IP地址和电子邮件信息；
>
> Android应用权限；
>
> 文件扩展名和文件名称；
>
> 其他

Qu1cksc0pe的主要功能就是给广大安全分析人员提供尽可能多地关于可疑文件的信息，并帮助用户了解目标文件的具体功能特性。

## 工具下载&安装

由于Qu1cksc0pe基于Python 3开发，因此我们首先要在本地主机上安装并配置好Python 3环境。接下来，使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/CYB3RMX/Qu1cksc0pe.git

## 工具配置

Qu1cksc0pe所需的Python模块如下：

> puremagic
>
> androguard
>
> apkid
>
> prettytable
>
> tqdm
>
> colorama
>
> oletools
>
> pefile
>
> quark-engine
>
> pyaxmlparser
>
> yara-python
>
> prompt_toolkit
>
> frida

我们可以使用下列命令安装该工具所需的Python模块：

    
    
    pip3 install -r requirements.txt

 **获取其他的依赖参数：**

VirusTotal API密钥：

    
    
    https://virustotal.com

Binutils：

    
    
    sudo apt-get install binutils

ExifTool：

    
    
    sudo apt-get install exiftool

Strings：

    
    
    sudo apt-get install strings

## 工具使用

    
    
    python3 qu1cksc0pe.py --file suspicious_file --analyze

## 扫描参数

### 普通分析

![](https://image.3001.net/images/20211126/1637914688_61a098404774723f686b5.gif)

### 多文件分析

    
    
    python3 qu1cksc0pe.py --multiple FILE1 FILE2 ...

![](https://image.3001.net/images/20211126/1637914658_61a09822148d24e23eef5.gif!small)

### Frida脚本动态指令（Android应用程序）

    
    
    python3 qu1cksc0pe.py --runtime

![](https://image.3001.net/images/20211126/1637914621_61a097fd436d7aadc1ee6.gif)

### 哈希扫描

    
    
    python3 qu1cksc0pe.py --file suspicious_file --hashscan

![](https://image.3001.net/images/20211126/1637914596_61a097e466f01db5802c8.gif!small)

### 文件夹扫描

 **支持的参数：**

\--hashscan

\--packer

    
    
    python3 qu1cksc0pe.py --folder FOLDER --hashscan

![](https://image.3001.net/images/20211126/1637914580_61a097d46c77354860bc2.gif!small)

### VirusTotal

 **报告内容：**

威胁类型

检测结果

CrowdSourced IDS报告

    
    
    python3 qu1cksc0pe.py --file suspicious_file --vtFile

![](https://image.3001.net/images/20211126/1637914551_61a097b7a9738430e23d5.gif!small)

### 文档扫描

    
    
    python3 qu1cksc0pe.py --file suspicious_document --docs

![](https://image.3001.net/images/20211126/1637914534_61a097a6099a6e330c3eb.gif!small)

### 编程语言检测

    
    
    python3 qu1cksc0pe.py --file suspicious_executable --lang

![](https://image.3001.net/images/20211126/1637914489_61a0977972ca8606773cd.gif!small)

### 交互式Shell

    
    
    python3 qu1cksc0pe.py --console

![](https://image.3001.net/images/20211126/1637914420_61a097343ae8ba057074d.gif)

### 域名检测

    
    
    python3 qu1cksc0pe.py --file suspicious_file --domain

## 工具运行截图

![](https://image.3001.net/images/20211126/1637914074_61a095da43c0b19d8dc80.jpg!small)

## 项目地址

 **Qu1cksc0pe：** 【[ _GitHub传送门_](https://github.com/CYB3RMX/Qu1cksc0pe)】

## 参考资料

> [ _https://github.com/Ch0pin/_](https://github.com/Ch0pin/)
>
> [ _https://codeshare.frida.re/browse﻿_](https://codeshare.frida.re/browse)

