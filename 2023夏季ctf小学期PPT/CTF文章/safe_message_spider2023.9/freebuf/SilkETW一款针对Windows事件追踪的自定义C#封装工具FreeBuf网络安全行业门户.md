![1.jpg](https://image.3001.net/images/20190514/1557837656_5cdab758e08b0.jpg!small)

## SilkETW

 **SilkETW是一款针对ETW（Event Tracing for
Windows）的自定义C#封装工具，该工具可以通过抽象化的方式简化ETW的复杂性，并帮助分析人员对目标应用进行内部架构以及运行机制方面的研究。虽然SilkETW是一款防御端应用程序，但是它目前所处的阶段仍只是研究工具。**

为了方便大家使用，输出数据被序列化成了JSON格式。JSON数据可以直接在本地使用PowerShell进行加载和分析，也可以转移到类似[Elasticsearch](https://www.elastic.co/)这样的第三方平台进行分析。

## 工具实现细节

### 代码库

SilkETW基于.NET
v4.5开发，并使用了大量[第三方库](https://github.com/fireeye/SilkETW/blob/master/LICENSE-3RD-PARTY.txt)：

    
    
    ModuleId                                 VersionLicenseUrl                                                  
    
    --------                                 -----------------                                                  
    
    McMaster.Extensions.CommandLineUtils     2.3.2  <https://licenses.nuget.org/Apache-2.0>                        
    
    Microsoft.Diagnostics.Tracing.TraceEvent2.0.36 <https://github.com/Microsoft/perfview/blob/master/LICENSE.TXT>
    
    Newtonsoft.Json                          12.0.1  <https://licenses.nuget.org/MIT>                               
    
    System.ValueTuple                        4.4.0   <https://github.com/dotnet/corefx/blob/master/LICENSE.TXT>     
    
    YaraSharp                                1.3.1  <https://github.com/stellarbear/YaraSharp/blob/master/LICENSE>

[](https://github.com/stellarbear/YaraSharp/blob/master/LICENSE)

### 命令行参数&选项

命令行的使用方式比较简单，用户在输入数据后即可获取验证结果：

![2.png](https://image.3001.net/images/20190514/1557837684_5cdab774d866b.png!small)

### JSON输出结构

JSON输出在进行序列化处理之前，会按照下列C#结构进行格式化：

    
    
    public struct EventRecordStruct
    
        public Guid ProviderGuid;
    
        public List<String> YaraMatch;
    
        public string ProviderName;
    
        public string EventName;
    
        public TraceEventOpcode Opcode;
    
        public string OpcodeName;
    
        public DateTime TimeStamp;
    
        public int ThreadID;
    
        public int ProcessID;
    
        public string ProcessName;
    
        public int PointerSize;
    
        public int EventDataLength;
    
        public Hashtable XmlEventData;
    
    }

请注意，根据不同的服务提供方以及事件类型，程序会在XmlEventData哈希表中存储不同的变量数据，下面给出的是针对"Microsoft-Windows-Kernel-Process"-> "ThreadStop/Stop"的JSON输出样本：

    
    
     "ProviderGuid":"22fb2cd6-0e7b-422b-a0c7-2fad1fd0e716",
    
       "YaraMatch":[
    
     
    
       ],
    
      "ProviderName":"Microsoft-Windows-Kernel-Process",
    
      "EventName":"ThreadStop/Stop",
    
       "Opcode":2,
    
       "OpcodeName":"Stop",
    
      "TimeStamp":"2019-03-03T17:58:14.2862348+00:00",
    
       "ThreadID":11996,
    
       "ProcessID":8416,
    
       "ProcessName":"",
    
       "PointerSize":8,
    
       "EventDataLength":76,
    
       "XmlEventData":{
    
          "FormattedMessage":"Thread11,996 (in Process 8,416) stopped. ",
    
         "StartAddr":"0x7fffe299a110",
    
          "ThreadID":"11,996",
    
         "UserStackLimit":"0x3d632000",
    
         "StackLimit":"0xfffff38632d39000",
    
          "MSec":"560.5709",
    
          "TebBase":"0x91c000",
    
         "CycleTime":"4,266,270",
    
          "ProcessID":"8,416",
    
          "PID":"8416",
    
         "StackBase":"0xfffff38632d40000",
    
          "SubProcessTag":"0",
    
          "TID":"11996",
    
         "ProviderName":"Microsoft-Windows-Kernel-Process",
    
          "PName":"",
    
         "UserStackBase":"0x3d640000",
    
         "EventName":"ThreadStop/Stop",
    
         "Win32StartAddr":"0x7fffe299a110"
    
       }
    
    }

## 工具使用

### 在PowerShell中过滤数据

在PowerShell的帮助下，你可以直接从SilkETW中导入JSON输出：

    
    
    function Get-SilkData {
    
           param($Path)
    
           $JSONObject = @()
    
           Get-Content $Path | ForEach-Object {
    
                  $JSONObject += $_ |ConvertFrom-Json
    
           }
    
           $JSONObject
    
    }

在下面的样例中，我们将从内核收集进程的事件数据，并通过加载图片来验证Mimikatz的执行。我们可以使用下列命令收集到我们想要的数据：

    
    
    SilkETW.exe -t kernel -kk ImageLoad -ot file -p C:\Users\b33f\Desktop\mimikatz.json

获取到数据之后，我们就可以根据属性来对数据进行排序、搜索和过滤了：

![3.png](https://image.3001.net/images/20190514/1557837732_5cdab7a487018.png!small)

## Yara

SilkETW提供了Yara功能来过滤数据或标记事件数据。虽然Yara规则普遍适用于防御端，但我们也可以在这里可以将其用于ETW研究。

在下面这个样例中，我们使用了Yara规则来检测内存中的Seatbelt执行：

    
    
    rule Seatbelt_GetTokenInformation
    
           strings:
    
                  $s1 ="ManagedInteropMethodName=GetTokenInformation" ascii wide nocase
    
                  $s2 ="TOKEN_INFORMATION_CLASS" ascii wide nocase
    
                  $s3 = /bool\(native int,valuetype\w+\.\w+\/\w+,native int,int32,int32&/
    
                  $s4 = "locals(int32,int64,int64,int64,int64,int32& pinned,bool,int32)" ascii widenocase
    
           
    
           condition:
    
                  all of ($s*)
    
    }

我们可以使用下列命令收集.NET ETW数据，“-yo”参数表明我们只能将Yara匹配写入磁盘：

    
    
    SilkETW.exe -t user -pn Microsoft-Windows-DotNETRuntime -uk 0x2038 -l verbose -yC:\Users\b33f\Desktop\yara -yo matches -ot file -pC:\Users\b33f\Desktop\yara.json

我们可以看到Yara规则的运行时匹配情况：

![4.png](https://image.3001.net/images/20190514/1557837752_5cdab7b8e07bb.png!small)

## SilkETW获取&构建

我们可以直接下载SilkETW源码并在Visual Studio中进行编译。

下载地址：【[点我下载预构建版本](https://github.com/fireeye/SilkETW/releases)】

## 项目地址

SilkETW：【[GitHub传送门](https://github.com/fireeye/SilkETW)】

 ***
参考来源：[fireeye](https://github.com/fireeye/SilkETW)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

