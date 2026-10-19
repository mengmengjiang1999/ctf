![](https://image.3001.net/images/20220707/1657191105_62c6bac152d6c44136813.jpeg!small)

## 关于EmoCheck

EmoCheck是一款针对Emotet木马病毒的安全检测工具，可以帮助广大研究人员检测目标Windows操作系统是否感染了Emotet木马病毒。

## 工具测试环境

> Windows 11 21H2 64位
>
> Windows 10 21H2 64位
>
> Windows 8.1 64位

注意：Windows 7不支持在命令行终端中输出UTF-8报告。

## 构建平台

> Windows 10 1809 64位
>
> Microsoft Visual Studio Community 2017

## 工具特性

> 1、Emotet会根据特定的单词词典和C驱动器序列号生成其进程名称，而EmoCheck可以扫描主机上正在运行的进程，并从进程名中找到Emotet进程。
>
> 2、Emotet会将其编码的进程名保存在特定的注册表项中，而EmoCheck可以查找并解码注册表值，并从进程列表中找到它。
>
> 3、支持检测2020年4月更新的Emotet版本。
>
> 4、支持检测2020年12月更新的Emotet版本。

## 工具下载

广大研究人员可以访问该项目的【[
_Releases页面_](https://github.com/JPCERTCC/EmoCheck/releases)】下载该工具的最新版本：

![](https://image.3001.net/images/20220707/1657191142_62c6bae628f971b5f5e2d.png!small)

## 命令选项

指定报告输出目录（默认：当前目录：）

    
    
    /output [your output directory]
    
    -output [your output directory]

禁用控制台输出：

    
    
    /quiet
    
    -quiet

将报告以JSON数据格式输出：

    
    
    /json
    
    -json

开启调试模式（无报告）：

    
    
    /debug
    
    -debug

显示工具帮助信息：

    
    
    /help
    
    -help

## 报告样例

### 文字格式

    
    
    [Emocheck v0.0.2]
    
    Scan time: 2020-02-10 13:06:20
    
    ____________________________________________________
    
     
    
    [Result]
    
    Detected Emotet process.
    
     
    
    [Emotet Process]
    
         Process Name  : mstask.exe
    
         Process ID    : 716
    
         Image Path    : C:\Users\[username]\AppData\Local\mstask.exe
    
    ____________________________________________________
    
     
    
    Please remove or isolate the suspicious execution file.

### JSON格式

    
    
    {
    
      "scan_time":"2020-02-10 13:06:20",
    
      "hostname":"[your hostname]",
    
      "emocheck_version":"0.0.2",
    
      "is_infected":"yes",
    
      "emotet_processes":[
    
        {
    
           "process_name":"mstask.exe",
    
           "process_id":"716",
    
           "image_path":"C:\\Users\\[username]\\AppData\\Local\\mstask.exe"
    
        }
    
      ]
    
    }

### 报告生成路径

    
    
    [current directory]\yyyymmddhhmmss_emocheck.txt
    
    [output path]\[computer name]_yyyymmddhhmmss_emocheck.txt
    
    [output path]\[computer name]_yyyymmddhhmmss_emocheck.json

## 工具运行截图

![](https://image.3001.net/images/20220707/1657191228_62c6bb3ca71a40d6cd298.png!small)

## 项目地址

 **EmoCheck** ：【[ _GitHub传送门_](https://github.com/JPCERTCC/EmoCheck)】

