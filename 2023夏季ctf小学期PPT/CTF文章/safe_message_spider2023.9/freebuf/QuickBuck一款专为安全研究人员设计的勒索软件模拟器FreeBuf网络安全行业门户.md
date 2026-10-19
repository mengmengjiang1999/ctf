## 关于QuickBuck

QuickBuck是一款基于Golang开发的勒索软件模拟工具，在该工具的帮助下，广大研究人员可以通过更简单的方法来判断反病毒保护方案是否能够有效地预防勒索软件的攻击。

## 功能介绍

该工具能够模拟下列勒索软件典型行为，其中包括：

> Word文档恶意宏文件（Staging）
>
> 删除卷影拷贝
>
> 加密文档
>
> 向用户桌面发送勒索信息

QuickBuck勒索软件模拟器并不会对目标设备上之前已经存在的任何文件进行实际的加密，或者删除卷影拷贝文件。当然了，这种类型的操作行为是可以触发反病毒产品的防御机制的。

除此之外，我们还可以通过命令行参数的形式严格控制上述的每一步操作。与此同时，我们还可以清楚地查看到每一步操作的响应信息。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/NextronSystems/ransomware-simulator.git

## 工具使用

    
    
    Ransomware Simulator
    
     
    
    Usage:
    
    ransomware-simulator [command]
    
     
    
    Examples:
    
    ransomware-simulator run
    
     
    
    Available Commands:
    
    help        显示工具帮助信息
    
    run         运行勒索软件模拟器
    
     
    
    Flags:
    
    -h, --help   显示QuickBuck帮助信息
    
     
    
    Use "ransomware-simulator [command] --help" for more information about a command.

## 工具使用

    
    
    Run Ransomware Simulator
    
     
    
    Usage:
    
    ransomware-simulator run [flags]
    
     
    
    Flags:
    
        --dir string                     Directory where files that will be encrypted should be staged (default "./encrypted-files")
    
        --disable-file-encryption        Don't simulate document encryption
    
        --disable-macro-simulation       Don't simulate start from a macro by building the following process chain: winword.exe -> cmd.exe -> ransomware-simulator.exe
    
        --disable-note-drop              Don't drop pseudo ransomware note
    
        --disable-shadow-copy-deletion   Don't simulate volume shadow copy deletion
    
    -h, --help                           help for run
    
        --note-location string           Ransomware note location (default "C:\\Users\\neo\\Desktop\\ransomware-simulator-note.txt")

## 工具参数

    
    
    --dir：需要加密的文件所在目录路径，默认为"./encrypted-files"；
    
    --disable-file-encryption：禁用文档加密功能；
    
    --disable-macro-simulation：禁用恶意宏模拟，恶意宏构建过程如下：winword.exe -> cmd.exe -> ransomware-simulator.exe；
    
    --disable-note-drop：禁用勒索信息发送功能；
    
    --disable-shadow-copy-deletion：禁用卷影拷贝删除功能；
    
    -h, --help：显示工具帮助信息
    
    --note-location：勒索信息发送位置，默认为"C:\\Users\\neo\\Desktop\\ransomware-simulator-note.txt"；

## 工具运行截图

![](https://image.3001.net/images/20220613/1655050933_62a612b5cb4badcc8da67.png!small)

## 许可证协议

本项目的开发与发布遵循[ _MIT_](https://github.com/NextronSystems/ransomware-simulator/blob/master/LICENSE)开源许可证协议。

 **QuickBuck：** 【[ _GitHub传送门_](https://github.com/NextronSystems/ransomware-simulator)】

