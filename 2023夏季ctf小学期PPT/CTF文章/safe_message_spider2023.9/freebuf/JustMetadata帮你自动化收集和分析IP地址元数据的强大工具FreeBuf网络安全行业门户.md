**今天给大家介绍的是一款名叫Just-Metadata的工具，该工具可以帮助研究人员收集和分析IP地址元数据，并通过大量数据集寻找目标网络系统之间的层级关系。**

![cccccccc.jpg](https://image.3001.net/images/20190414/1555177396_5cb21fb4d8be1.jpg!small)

## Just-Metadata

Just-Metadata这款工具可以被动收集大量IP地址以及相关情报信息，并尝试推断出目标网络系统中各个设备系统之间的隐性关系。Just-Metadata的“gather”（收集）模块可以用来收集加载进框架中的IP元数据信息，而“analysis”（分析）模块可以用来分析加载进框架中的数据，并执行一系列识别系统间关系的分析操作。

Just-Metadata可以帮助研究人员快速定位目标IP地址所在的城市和时区等信息，而且还可以按照国家来搜索IP地址。值得注意的是，该工具还可以利用VirusTotal的回调信息来搜索目标IP地址。如果你想知道哪个IP地址是否参与了某些攻击活动的话，Just-Metadata是你最好的选择。

除此之外，该工具易于扩展，研究人员可以根据自己的需要轻松开发新的功能模块。

## 工具下载与安装

下载命令如下：

    
    
    git clone git://github.com/FortyNorthSecurity/Just-Metadata.git

下载完成后，大家可以运行安装脚本来完成工具的安装。如果需要使用Shodan信息收集模块的话，你需要申请一个Shodan API密钥，价格大概在9美元。

## 工具使用

Just-Metadata可以直接读取包含了IP地址的单一文本文件，其中每一行为一个IP地址。大家可以利用各种数据源来创建这种形式的文件，然后通过下列方式调用这个文件：

    
    
    ./Just-Metadata.py

## 操作命令

“help”：帮助命令可查看该框架所有支持的操作指令。

“load <filename>“：加载命令负责加载特定文件，用户需要输入包含了待分析IP地址的文件，Just-Metadata可以打开并加载文件中的IP。

    
    
    Ex：load ipaddresses.txt

“save”：保存命令可以用来保存Just-Metadata的工作状态，比如说当前的IP分析进程以及部分分析结果，

“import <statefile>“：导入命令可以用来加载之前保存的Just-Metadata状态，其中包括扫描的IP地址以及收集到的IP地址信息。

    
    
    Ex：import goodfile.state

“list <module type>“：该命令可以列出Just-Metadata框架中已下载的模块。

    
    
    Ex：list analysis
    
    Ex：list gather

“gather <gather module name>“：收集命令可以控制Just-Metadata从特定的源收集信息，其中包括地理位置信息、Virustotal信息以及Whois信息等等。

    
    
    Ex：gather geoinfo
    
    Ex：gather virustotal

“export”：导出命令可以将Just-Metadata收集到的信息以CSV文件的形式导出。

## 项目地址

Just-Metadata：【[GitHub传送门](https://github.com/FortyNorthSecurity/Just-Metadata)】

 ***参考来源：[FortyNorthSecurity](https://github.com/FortyNorthSecurity/Just-Metadata)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

