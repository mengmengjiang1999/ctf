![](https://image.3001.net/images/20220303/1646314962_6220c5d2cb9d1d54ffc52.jpeg!small)

## 关于Boko

Boko是一款针对macOS的应用程序劫持扫描工具，该工具可以帮助广大研究人员搜索和识别目标应用程序可执行文件中潜在的Dylib劫持和弱Dylib漏洞，并发现应用程序所使用的脚本中是否有可能被植入后门。

该工具基于[
_DylibHijack项目_](https://github.com/synack/DylibHijack)的scan.py脚本进行了重新开发，可以扫描出研究人员所感兴趣的文件，并将它们枚举出来，这样就不需要研究人员手动浏览文件系统并进行分析了。在主动探测功能的帮助下，如果一个可执行文件容易受到Dylib劫持的话，工具就能够直接发现它。

该工具的主要目的，是发现、识别和管控那些Dylib劫持扫描工具所发现的数据。大多数公开可用的扫描工具会在发现第一个易受攻击的Dylib时便停止运行，而不会扩展其余的rpath。有的时候第一个扫描结果会在SIP保护区内的一个不存在的文件中展开，而我们有时候需要获取这些展开路径的其余部分。在这种情况下，便会出现误报。Boko便应运而生，因为它可以为每个项目指定一个确定性区域。

## 确定性描述

 ** **确定性****

|

 ** **描述****  
  
---|---  
  
绝对

|

漏洞100%可利用  
  
高

|

如果该漏洞与主可执行文件相关，且rpath在加载顺序中排名第二，则该漏洞很有可能被利用  
  
潜在

|

值得研究，但可能无法利用  
  
低

|

由于加载顺序较晚，这个入口点很难被利用  
  
## 工具要求

该工具需要本地设备上安装并配置好Python 3环境，然后运行下列命令安装该工具所需的依赖组件：

    
    
    python -m pip install psutil

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/bashexplode/boko.git

## 工具使用

    
    
    boko.py [-h] (-r | -i | -p /path/to/app) (-A | -P | -b) [-oS outputfile | -oC outputfile | -oA outputfile] [-s] [-v]

## 参数描述

 ** **参数****

|

 ** **描述****  
  
---|---  
  
-h, --help

|

显示帮助信息和退出  
  
-r, --running

|

检查当前正在运行的进程  
  
-i, --installed

|

检查所有已安装的应用程序  
  
-p /file.app

|

检查指定的应用程序，例如/Application/Safari.app  
  
-A, --active

|

执行发现的可执行二进制文件，以主动识别可劫持的dylib  
  
-P, --passive

|

仅通过查看文件Header来执行检查（默认）  
  
-b, --both

|

执行两种漏洞测试方法  
  
-oS outputfile

|

将标准输出结果保存至.log文件中  
  
-oC outputfile

|

将输出结果保存至.csv文件中  
  
-oA outputfile

|

将输出结果保存至.csv文件和标准日志中  
  
-s, --sipdisabled

|

如果系统上禁用了SIP，则使用此选项搜索通常为只读的路径  
  
-v, --verbose

|

脚本运行时，以Verbose模式输出所有结果  
  
## 许可证协议

本项目的开发与发布遵循BSD-3开源许可证协议。

## 项目地址

 **Boko：** 【[ _GitHub传送门_](https://github.com/bashexplode/boko)】

## 参考资料

> [
> _https://github.com/synack/DylibHijack_](https://github.com/synack/DylibHijack)
>
> [
> _https://github.com/bashexplode/boko/wiki_](https://github.com/bashexplode/boko/wiki)

