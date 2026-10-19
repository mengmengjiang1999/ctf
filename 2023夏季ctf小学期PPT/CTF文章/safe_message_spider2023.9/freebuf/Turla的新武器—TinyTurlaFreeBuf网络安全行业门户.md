Turla 也被称为 Snake、Venomous Bear、Uroburos 和 WhiteBear，是一个臭名昭著的 APT
组织。据信该组织来自俄罗斯，2004 年以来就一直活跃。

多年来，Turla 开发并维护了一套庞大的攻击工具来攻击世界各地的受害者，包括欧洲、美国、乌克兰和阿拉伯等多家。

Turla 通常不与 C&C 服务器直接通信，而是使用其他失陷主机作为代理，将流量转发到真正的 C&C 服务器上。

不仅诸如 Crutch 或 Kazuar 之类的知名恶意软件与 Turla 有关，近期发生的 Sunburst 也与 Turla 存在关联。

思科发现了一个 Turla 使用的新后门，该后门功能有限且编码风格简单，检测系统很容易放过它。根据遥测，该后门至少在 2020
年就开始使用了。分析发现，在西方撤军导致塔-利-班接管阿富汗政府前，该后门针对前阿富汗政府攻击。

## 技术细节

思科通过遥测发现了后门，但是并不知道确切的安装方式。后门以名为 `w64time.dll`的 DLL
形式出现，描述和文件名看起来像是正常的微软程序。![image.png-149.1kB](https://image.3001.net/images/20210922/1632315365_614b27e5f26650cfd1d9b.png!small)

在 `%SYSTEMROOT%\system32`目录下有真正的正统文件 `w32time.dll`，但并没有 `w64time.dll`。Windows
系统有很多 32 位和 64
位的应用程序，通过名称来识别恶意软件并不容易。![image.png-209.6kB](https://image.3001.net/images/20210922/1632315367_614b27e7006e9598f03f5.png!small)

攻击者使用类似以下的 `.bat`文件将后门安装成看起来很正常的 Windows
时间服务。![image.png-200kB](https://image.3001.net/images/20210922/1632315368_614b27e841820e3812d7d.png!small)

恶意软件会作为服务运行，隐藏在 `svchost.exe`进程中。DLL 的 `ServiceMain`函数主要是为了执行
`main_malware`，其中包含后门的代码。![image.png-192.5kB](https://image.3001.net/images/20210922/1632315369_614b27e95c0c768584d18.png!small)

首先，后门从注册表中读取配置并保存在 `result`结构体中，后续传递给
`sConfig`。![image.png-317.5kB](https://image.3001.net/images/20210922/1632315370_614b27ea49f1d7959c73a.png!small)

整个 DLL
文件非常简单，主要有几个函数和循环组成。![image.png-191.6kB](https://image.3001.net/images/20210922/1632315371_614b27eb6f914178846be.png!small)

首先在 C&C 服务器上注册，解析响应接收命令。C&C 服务器地址以 `<IP 地址1> <TcpPort> <IP 地址2> <TcpPort>
<IP地址3>
<TcpPort>`的格式存储在注册表中，空格为分隔符。![image.png-146.5kB](https://image.3001.net/images/20210922/1632315372_614b27ec4dda7d9f2bed0.png!small)

如果所有的 C&C 服务器都没有得到预期的响应，`host_index`等于零。后门等待存储在
`<TimeLong>`注册表中的毫秒数，捕获的样本时长为一分钟，再进行请求。

成功建立连接后，后门将每隔 `<TimeShort>`毫秒就检查命令下发。

`C2_GetCommand_ComHandler`处理与 C&C 服务器的通信，利用类似于 Windows WinHttp API 接收 C&C
命令及其参数。![image.png-42.7kB](https://image.3001.net/images/20210922/1632315374_614b27ee6c82e09c81bf6.png!small)

即使攻击者使用 TLS
加密流量，后门程序也不检查证书。![image.png-26.7kB](https://image.3001.net/images/20210922/1632315375_614b27ef04a4b5d61e9cb.png!small)

程序只验证存储在 `Security`注册表中的密码，在
`C2_ProcessCommand`函数的起始处就进行检查。![image.png-75kB](https://image.3001.net/images/20210922/1632315375_614b27ef8f220c9baf63f.png!small)

`C2_ProcessCommand`在接收到命令后使用 switch
处理相关命令。![image.png-193kB](https://image.3001.net/images/20210922/1632315376_614b27f048cb60c0f7187.png!small)

其功能如下所示：

> 0x00:身份验证
>
> 0x01:执行进程
>
> 0x02:执行收集输出
>
> 0x03:下载文件
>
> 0x04:上传文件
>
> 0x05:创建子进程
>
> 0x06:关闭子进程
>
> 0x07:子进程管道输入/输出
>
> 0x08:设置 TimeLong
>
> 0x09:设置 TimeShort
>
> 0x0A:设置新的'Security'密码
>
> 0x0B:设置 Host

在 HTTP 的头中设置 `Title`与 GUID 配对，例如 `Title:
01234567-1234-1234-1234-123456789abc`。![image.png-62kB](https://image.3001.net/images/20210922/1632315377_614b27f102712ea5552fe.png!small)

## 结论

Turla 作为 APT 组织已经活跃多年，他们经常使用复杂的恶意软件。本次思科将该后门归因为 Turla 是因为攻击基础设施的重用。

尽管 Turla 被密切监控，该后门程序仍然被使用了两年，这表明检测能力仍有改进的空间。

## Yara

> import "pe"  
> rule TinyTurla {  
> meta:  
> author = "Cisco Talos"  
> description = "Detects Tiny Turla backdoor DLL"  
> strings:  
> b = "Hosts" fullword wide  
> d = "TimeLong" fullword wide  
> f = "MachineGuid" fullword wide  
> h = "WinHttpSetOption" fullword ascii  
> $i = "WinHttpQueryDataAvailable" fullword ascii
>
> condition:  
> pe.is_pe and  
> pe.characteristics & pe.DLL and  
> pe.exports("ServiceMain") and  
> all of them  
> }

## IOC

> 030cbd1a51f8583ccfc3fa38a28a5550dc1c84c05d6c0f5eb887d13dedf1da01

## 参考来源

>
> [TalosIntelligence](https://blog.talosintelligence.com/2021/09/tinyturla.html)

