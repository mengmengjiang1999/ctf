![](https://image.3001.net/images/20220708/1657289519_62c83b2f7bb8f59f5713c.png!small)  

## 关于Sealighter

Sealighter是一款针对ETW（Event Tracing for Windows）和WPP（Windows PreProcessor
Tracing）的安全研究工具，在该工具的帮助下，广大研究人员可以轻松追踪和研究ETW和WPP。

Sealighter利用了功能丰富的Krabs ETW库来启用事件过滤功能，并对ETW和WPP事件进行分类。

除此之外，Sealighter可以将事件解析为JSON格式输出，并输入到Python、PowerShell、Splunk或ELK中进行进一步分析。

## 功能介绍

> 1、支持订阅多个ETW和WPP服务实体；
>
> 2、自动将事件解析为JSON格式；
>
> 3、内置事件过滤器；
>
> 4、支持将数据输出到stdout、文件或Windows事件日志工具；
>
> 5、获取事件堆栈记录；
>
> 6、可配置将一个时间段内的多个事件缓冲到一个具有计数的事件中，以减少生成的事件数；

## 工具安装

广大研究人员可以访问该项目的【[
_Releases页面_](https://github.com/pathtofile/Sealighter/releases)】下载最新版本的Sealighter代码，然后安装最新版本的Visual
C运行时环境：【[ _传送门_](https://support.microsoft.com/en-us/help/2977003/the-latest-supported-visual-c-downloads)】。

## 工具配置

Sealighter的配置文件将允许我们指定需要捕捉和记录的事件以及ETW会话，配置文件的数据结构使用的是JSON，下面给出的是配置样例：

    
    
    {
    
        "session_properties": {
    
            "session_name": "My-Process-Trace",
    
            "output_format": "stdout",
    
            "buffering_timout_seconds":  10
    
        },
    
        "user_traces": [
    
            {
    
                "trace_name": "proc_trace",
    
                "provider_name": "Microsoft-Windows-Kernel-Process",
    
                "keywords_any": 16
    
            },
    
            {
    
                "trace_name": "guid_trace",
    
                "provider_name": "{382b5e24-181e-417f-a8d6-2155f749e724}",
    
                "filters": {
    
                    "any_of": {
    
                        "opcode_is": [1, 2]
    
                    }
    
                },
    
                "buffers": [
    
                    {
    
                        "event_id": 1,
    
                        "max_before_buffering": 1,
    
                        "fields": [
    
                            "ImageName"
    
                        ]
    
                    }
    
                ]
    
            },
    
        ],
    
        "kernel_traces": [
    
            {
    
                "trace_name": "kernel_proc_trace",
    
                "provider_name": "process",
    
            }
    
        ]
    
    }

## 工具使用

### 输出至STDOUT或文件

以管理员权限运行“sealighter.exe”，并将JSON配置文件路径以参数形式传递给Sealighter：

    
    
    sealighter.exe path\to\config.json

下面给出的是记录下的所有活动信息样例：

    
    
    {
    
        "session_properties": {
    
            "session_name": "My-Process-Trace",
    
            "output_format": "stdout"
    
        },
    
        "user_traces": [
    
            {
    
                "trace_name": "proc_trace",
    
                "provider_name": "Microsoft-Windows-Kernel-Process",
    
                "keywords_any": 16
    
            }
    
        ]
    
    }

### 输出至Windows事件日志工具

针对大量的数据，可能我们需要将数据输出到Windows事件日志工具以提升我们的操作效率，并确保事件不会丢失。在将数据输出到Windows事件日志工具中之前，我们需要将一些数据解析到事件日志服务中。

此时需要从该项目的【[
_Releases页面_](https://github.com/pathtofile/Sealighter/releases)】下载最新版本的sealighter_provider.man文件。

接下来，在文本编辑器中打开刚刚下载的manifest文件，然后使用完整的“sealighter.exe”路径替换其中的“!!SEALIGHTER_LOCATION!!”参数，然后在以管理员权限运行的PowerShell或命令行窗口中运行下列命令：

    
    
    wevtutil im path/to/sealighter_provider.man

此时，在事件查看器UI界面的“Applications and Service Logs”选项中，我们将看到一个“Sealighter”文件夹以及日志记录。

我们还可以使用下列命令对报告进行验证：

    
    
    (Get-WinEvent -LogName "Sealighter/Operational").Length

下列命令可以删除日志：

    
    
    wevtutil um path/to/sealighter_provider.man

## 工具运行截图

![](https://image.3001.net/images/20220708/1657289621_62c83b954ff57743dea3f.png!small)

## 项目地址

 **Sealighter** ：【[ _GitHub传送门_](https://github.com/pathtofile/Sealighter)】

## 参考资料

> [
> _https://github.com/microsoft/krabsetw_](https://github.com/microsoft/krabsetw)
>
> [
> _https://github.com/jdu2600/Windows10EtwEvents_](https://github.com/jdu2600/Windows10EtwEvents)
>
> [
> _https://github.com/zodiacon/EtwExplorer_](https://github.com/zodiacon/EtwExplorer)
>
> [ _https://github.com/fireeye/SilkETW_](https://github.com/fireeye/SilkETW)
>
> [
> _https://github.com/pathtofile/Sealighter/blob/main/docs/COMPARISION.md_](https://github.com/pathtofile/Sealighter/blob/main/docs/COMPARISION.md)
>
> [ _https://posts.specterops.io/data-source-analysis-and-dynamic-windows-re-> using-wpp-and-tracelogging-e465f8b653f7_](https://posts.specterops.io/data-> source-analysis-and-dynamic-windows-re-using-wpp-and-> tracelogging-e465f8b653f7)

