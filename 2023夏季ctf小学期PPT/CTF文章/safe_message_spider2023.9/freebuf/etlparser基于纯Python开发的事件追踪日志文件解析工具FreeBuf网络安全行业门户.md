![](https://image.3001.net/images/20220101/1641016047_61cfeaefe94f9639ad2c4.png!small)

## 关于etl-parser

etl-parser是一款基于纯Python开发的事件追踪日志文件读取和解析工具。该工具基于纯Python 3 ETL
Windows日志文件解析库实现其功能，而ETL则是[ _ETW_](https://docs.microsoft.com/en-us/windows/win32/etw/event-tracing-portal)以及内核日志工具的默认格式。

ETL是Windows系统程序员大量使用的一种日志工具/格式，比如说：

> C:\Windows\System32\WDI\LogFiles\BootPerfDiagLogger.etl
>
> C:\Windows\System32\WDI\LogFiles\ShutdownPerfDiagLogger.etl
>
> NetTrace.etl（netsh）
>
> C:\Windows\System32\WDI\<GUID>\<GUID>\snapshot.etl
>
> 其他...

很多新型的API都基于ETW实现，比如说Tracelogging或WPP等，而这些API都是微软开发者会经常使用的。

etl-parser不需要任何系统依赖，支持在Windows和Linux系统上运行。

etl-parser可以通过引入下列日志格式解析器来帮助广大研究人员解决各种问题：

> ETW manifest base provider
>
> TraceLogging
>
> MOF for kernel log

## 工具下载&安装

广大研究人员可以直接使用下列命令将该项目源码克隆至本地

    
    
    git clone https://github.com/airbus-cert/etl-parser.git

然后切换至项目目录中，并运行setup.py脚本进行工具安装：

    
    
    git clone https://github.com/airbus-cert/etl-parser.git
    
    cd etl-parser
    
    pip install -e .

除此之外，我们也可以直接通过pip命令来安装etl-parser：

    
    
    pip install etl-parser

## 工具使用

etl-parser提供了两个功能脚本，第一个脚本为etl2xml，该脚本可以将所有已知的ETL事件转换为XML格式的数据：

    
    
    etl2xml -i example.etl -o example.xml

第二个脚本为etl2pcap，该脚本负责将那些通过netsh创建的网络数据包转换为pcap文件格式：

    
    
    netsh start trace capture=yes
    
    netsh stop trace
    
     
    
    etl2pcap -i NetTrace.etl -o NetTrace.pcap

### 以代码库的形式使用

当然了，你也可以将etl-parser以代码库的形式使用：

    
    
    from etl.etl import IEtlFileObserver, build_from_stream
    
    from etl.system import SystemTraceRecord
    
    from etl.perf import PerfInfo
    
    from etl.event import Event
    
    from etl.trace import Trace
    
    from etl.wintrace import WinTrace
    
     
    
    class EtlFileLogger(IEtlFileObserver):
    
        def on_system_trace(self, event: SystemTraceRecord):
    
            """Mof kernel message with Process Id and Thread Id"""
    
            mof = event.get_mof() # Invoke MOF parser
    
     
    
        def on_perfinfo_trace(self, event: PerfInfo):
    
            """Mof kernel message with timestamp"""
    
            mof = event.get_mof() # Invoke MOF parser
    
     
    
        def on_trace_record(self, event: Trace):
    
            """unknown"""
    
     
    
        def on_event_record(self, event: Event):
    
            """ETW event this is what you search"""
    
            # Choose the "parse_" function which corresponds to your event
    
            message = event.parse_tracelogging() # Invoke TraceLogging parser
    
            message = event.parse_etw() # Invoke Manifest based parser
    
     
    
        def on_win_trace(self, event: WinTrace):
    
            """unknown"""
    
            etw = event.parse_etw()
    
     
    
    with open("example.etl", "rb") as etl_file:
    
        etl_reader = build_from_stream(etl_file.read())
    
        etl_reader.parse(EtlFileLogger())

## 许可证协议

本项目的开发与发布遵循[ _Apache
v2.0_](https://www.apache.org/licenses/LICENSE-2.0)开源许可证协议。

## 项目地址

 **etl-parser：** 【[ _GitHub传送门_](https://github.com/airbus-cert/etl-parser)】

## 参考资料

> [ _https://docs.microsoft.com/en-us/windows/win32/etw/event-tracing-> portal_](https://docs.microsoft.com/en-us/windows/win32/etw/event-tracing-> portal)
>
> [ _https://www.geoffchappell.com/_](https://www.geoffchappell.com/)
>
> [ _https://www.trusted-introducer.org/directory/teams/ai-> cert.html_](https://www.trusted-introducer.org/directory/teams/ai-cert.html)

  

  

  

