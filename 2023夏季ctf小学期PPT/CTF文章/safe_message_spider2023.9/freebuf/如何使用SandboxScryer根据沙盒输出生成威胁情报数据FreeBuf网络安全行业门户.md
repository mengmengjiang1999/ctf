![](https://image.3001.net/images/20221129/1669724613_6385f9c5304dfe7b7adb9.jpeg!small)

## 关于Sandbox Scryer

Sandbox
Scryer是一款功能强大的开源安全威胁情报工具，该工具可以根据公开的沙盒输出生成威胁搜索和情报数据，并允许广大研究人员将大量样本发送给沙盒，以构建可以跟MITRE
ATT&CK Framework一起使用的技术文档。Sandbox
Scryer提供了前所未有的大规模用例解决方案，该工具适用于对利用沙盒输出数据进行威胁搜索和攻击分析感兴趣的网络安全专业人员。

值得一提的是，当前版本的Sandbox Scryer使用了免费和公共混合分析恶意软件分析服务的输出，以帮助分析人员加快和扩大威胁搜索的能力。

## 项目内容

> [root] version.txt - 当前版本的工具许可证协议
>
> [root\bin] \Linux ｜ MacOS ｜ Windows -> 适用于Linux、MacOS和Windows平台的预构建工具代码，当前支持Ubuntu x64、OSX 10.15 x64、Win10 x64；
>
> [root\presentation_video] Sandbox_Scryer__BlackHat_Presentation_and_demo.mp4
> - 工具介绍和使用演示视频；
>
> [root\screenshots_and_videos] 各种工具运行截图；
>
> [root\scripts] Parse_report_set.* - Windows
> PowerShell和DOS命令行脚本文件，可以调用工具来解析Collate_Results.*测试结果集中的每一个HA沙盒报告概述，以及从解析报告中收集数据并生成MITRE
> Navigator Layer 文件；
>
> [root\slides] BlackHat_Arsenal_2022__Sandbox_Scryer__BH_template.pdf -> 2022世界黑帽大会上本工具的演示文稿；
>
> [root\src] Sandbox_Scryer - Sandbox Scryer 的C#源代码和Visual Studio 2019 解决方案文件；
>
> [root\test_data] (SHA256 filenames).json - 企业级分析报告信息，可以用于在MITRE
> Navigator中对生成热图的技术进行排序；
>
> [root\test_output] (SHA256)_report__summary_Error_Log.txt -> 包含了大量人类可读的报告错误日志信息；
>
> \collated_data collated_080122_MITRE_Attck_Heatmap.json - 用于导入至MITRE
> Navigator的Layer文件；

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地，并根据对应的操作系统平台进行选择和使用：

    
    
    git clone https://github.com/PayloadSecurity/Sandbox_Scryer.git

## 工具使用

Sandbox Scryer需要使用命令行工具来调用，并使用指定的脚本来完成特定的功能。

Sandbox Scryer的使用和操作分为两个主要步骤：

> 1、解析：需要解析一个给定的报告摘要，并提取输出数据；
>
> 2、整理：获取第一步解析步骤获取到的数据，并对其进行整理以生成Navigator Layer文件；

## 工具命令

    
    
    Options:
    
               -h  显示工具帮助信息
    
               -i   输入文件路径
    
               -ita  输入文件路径（MITRE报告）
    
               -o  输出目录路径
    
               -ft  提交文件的类型
    
               -name 输出文件名称
    
               -sb_name 需要使用的沙盒识别符，默认为ha
    
               -api_key 提交用例至沙盒时所使用的API密钥
    
               -env_id 提交用例至沙盒时所使用的环境ID
    
               -inc_sub 图形化输出要包含的子技术，默认不包含
    
               -mitre_data 包含待解析MITRE CTI数据的文件路径
    
               -cmd  Command
    
                     Options:
    
                        parse  从之前的沙盒提交解析报告文件
    
                               支持-i, -ita, -o, -name, -inc_sub, -sig_data参数
    
                        col    整理以前沙盒提交的报告数据
    
                               支持-i (treated as folder path), -ita, -o, -name, -inc_sub, -mitre_data   parameters

如果想要使用“-h”参数，则可以运行下列命令：

    
    
    Sandbox_Scryer.exe -h

一旦Navigator Layer文件生成之后，我们就可以将其加载到[ _Navigator_](https://mitre-attack.github.io/attack-navigator/)【[ _传送门_](https://mitre-attack.github.io/attack-navigator/)】中以便进行后续分析了。

在Navigator中，沙盒报告摘要中指出的技术将突出显示，并根据沙盒报告总结中的技术排名和技术点击次数的组合评分，按热度排列显示。

## 工具使用演示

### Collated_data__Navigator_layer_file

![](https://image.3001.net/images/20221129/1669724670_6385f9fee5ef0d9a11ff5.png!small)

### Hybrid_Analysis

![](https://image.3001.net/images/20221129/1669724677_6385fa05694c1266239bf.png!small)

### MITRE_Navigator

![](https://image.3001.net/images/20221129/1669724683_6385fa0b8d8b6d2eb9823.png!small)

### Parsed_Report_Summary_csv_data

![](https://image.3001.net/images/20221129/1669724690_6385fa12bc3bec14cf1e4.png!small)

### Sandbox_report_Summary

![](https://image.3001.net/images/20221129/1669724698_6385fa1a0e8488c3b1fb7.png!small)

## 许可证协议

本项目的开发与发布遵循[ _GPL_ __ _v_
_3_](https://github.com/PayloadSecurity/Sandbox_Scryer/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **Sandbox Scryer** ：【[
_GitHub传送门_](https://github.com/PayloadSecurity/Sandbox_Scryer)】

## 参考资料

> [ _https://mitre-attack.github.io/attack-navigator/﻿_](https://mitre-> attack.github.io/attack-navigator/)

