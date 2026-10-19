**今天给大家介绍一款名叫Flightsim的实用工具，该工具可以帮大家生成恶意网络流量，并以此来评估自身的网络安全控制策略。**

![Flightsim：看我如何生成并分析恶意网络流量](https://image.3001.net/images/20190514/1557838439_5cdaba67880e0.jpg!small)

## Network Flight Simulator

**Flightsim是一款轻量级的开源网络安全工具，安全研究人员可以利用这款工具来生成恶意网络流量，并帮助他们评估自身网络系统的安全控制策略以及网络可见性。工具可以通过执行测试任务来模拟DNS隧道、DGA流量、向已知活动C2服务器发送请求以及其他的可疑网络行为。**

## 工具安装

大家可以直接从该项目的[GitHub
Releases页面](https://github.com/alphasoc/flightsim/releases)下载最新版本的Flightsim。或者，大家也可以使用[Golang](https://golang.org/doc/install)来构建项目代码（支持Linux、macOS和Windows等）：

    
    
    go get -u github.com/alphasoc/flightsim/...

工具运行

工具安装完成之后，可以按照如下方式测试flightsim：

    
    
    $flightsim --help
    
    AlphaSOCNetwork Flight Simulator™ (<https://github.com/alphasoc/flightsim>)
    
    flightsimis an application which generates malicious network traffic for security
    
    teamsto evaluate security controls (e.g. firewalls) and ensure that monitoring tools
    
    areable to detect malicious traffic.
    
    Usage:
    
      flightsim [command]
    
    AvailableCommands:
    
      help       Help about any command
    
      run        Run all simulators (default) or a particular test
    
      version    Print version and exit
    
    Flags:
    
      -h, --help  help for flightsim
    
    Use"flightsim [command] --help" for more information about a command

该工具会运行单独模块来生成恶意流量，如果你需要执行完整测试，可以直接使用下列命令：

    
    
    flightsim run

该命令会使用第一个可用的网络接口来生成恶意流量。在运行C2模块时，flightsim会从CybercrimeTracker和AlphaSOC
API来收集当前的C2地址。

大家可以使用下列命令查看所有可用模块：

    
    
    flightsim run --help

使用下列命令可执行特定测试：

    
    
    flightsim run <module>

## 运行结果：

    
    
    $flightsim run --help
    
    Runall simulators (default) or a particular test
    
    Usage:
    
      flightsim run[c2-dns|c2-ip|dga|hijack|scan|sink|spambot|tunnel] [flags]
    
    Flags:
    
      -n,                      number of hosts generatedfor each simulator (default 10)
    
          --fast               run simulator fast without sleepintervals
    
      -h, --help               help for run
    
      -i, --interface string   network interface to use
    
    $flightsim run dga
    
    AlphaSOCNetwork Flight Simulator™ (<https://github.com/alphasoc/flightsim>)
    
    TheIP address of the network interface is 172.31.84.103
    
    Thecurrent time is 10-Jan-18 09:30:28
    
    Time      Module  Description
    
    --------------------------------------------------------------------------------    
    09:30:28  dga     Starting
    
    09:30:28  dga     Generating list of DGA domains
    
    09:30:30  dga     Resolving rdumomx.xyz
    
    09:30:31  dga     Resolving rdumomx.biz
    
    09:30:31  dga      Resolving rdumomx.top
    
    09:30:32  dga     Resolving qtovmrn.xyz
    
    09:30:32  dga     Resolving qtovmrn.biz
    
    09:30:33  dga     Resolving qtovmrn.top
    
    09:30:33  dga     Resolving pbuzkkk.xyz
    
    09:30:34  dga     Resolving pbuzkkk.biz
    
    09:30:34  dga     Resolving pbuzkkk.top
    
    09:30:35  dga     Resolving wfoheoz.xyz
    
    09:30:35  dga     Resolving wfoheoz.biz
    
    09:30:36  dga     Resolving wfoheoz.top
    
    09:30:36  dga     Resolving lhecftf.xyz
    
    09:30:37  dga     Resolving lhecftf.biz
    
    09:30:37  dga     Resolving lhecftf.top
    
    09:30:38  dga     Finished
    
    Alldone! Check your SIEM for alerts using the timestamps and details above.

## 工具模块介绍

下面给出的是该工具自带的模块包：

**模块名** **** |  **模块描述** ****  
---|---  
c2-dns |  生成当前的C2目的地址列表，分别执行DNS请求  
c2-ip |  随机连接10个当前列表中的C2 IP地址:端口，模拟攻击会话  
dga |  使用随机标签和顶级域名模拟DGA流量  
hijack |  通过ns1.sandbox.alphasoc.xyz测试DNS劫持  
scan |  使用常见端口对10个随机RFC 1918地址进行端口扫描  
sink |  对10个安全提供商的随机地址进行安全测试  
spambot |  随机解析并连接互联网SMTP服务器，测试欺诈端口  
tunnel |  生成DNS隧道请求并发送至*.sandbox.alphasoc.xyz  
  
## 项目地址

Flightsim：【[GitHub传送门](https://github.com/alphasoc/flightsim)】

 ***
参考来源：[alphasoc](https://github.com/alphasoc/flightsim)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

