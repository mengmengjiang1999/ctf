![](https://image.3001.net/images/20220911/1662869126_631d5e865eeecc279e135.jpg!small)  

## 关于LiveTargetsFinder

LiveTargetsFinder是一款功能强大的实时活动主机生成工具，该工具可以为广大研究人员以自动化的形式生成可供分析和测试的实时活动主机URL列表，并通过[
_MassDNS_](https://github.com/blechschmidt/massdns)、[
_Masscan_](https://github.com/robertdavidgraham/masscan)和[ _N_
_map_](https://nmap.org/)自动过滤出无法访问的主机。

我们只需要提供一个域名作为输入文件，工具脚本将会自动使用MassDNS筛选出无法解析的主机，然后将结果传递给Masscan，以确认主机是否可访问以及开启了哪些端口。接下来，该脚本将会生成一个完整的URL列表，其中将包含可访问的域名信息和可以抵达的IP地址，随后可以将其发送到gobuster或dirsearch等工具，或发送HTTP请求。值得一提的是，该工具还支持将生成的主机信息发送到Nmap上进行扫描，以在早起验证目标主机是否可访问或是否已启动，并根据打开的端口收集服务信息。

该脚本特别适用于大规模网络，比如说从数千个子域或apex域收集大量信息。如果直接将这些信息发送给Nmap进行扫描的话，速度会比较慢，因此我们首先使用不太准确但速度快得多的MassDNS，通过删除无法解析的域来快速减少输入列表的大小。然后，Masscan将能够从MassDNS获取输出，并进一步确认主机是否可访问，以及开启了哪些端口。最后，工具将解析这些结果并生成实时主机列表。

## 工具安装

注意：如果你要使用Nmap扫描选项，则需要先安装好Nmap。除此之外，MassDNS和Masscan是必须安装的工具组件。因此在使用该工具之前，还需要配置好相应的可执行文件路径。

由于该工具基于Python开发，因此我们首先需要在本地设备上安装并配置好Python环境。接下来，使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/allyomalley/LiveTargetsFinder.git

接下来，切换到项目目录，并通过pip3命令和项目提供的requirements.txt文件安装该工具所需的依赖组件：

    
    
    cd LiveTargetsFinder
    
    sudo pip3 install -r requirements.txt

可选项：

    
    
    chmod +x install_deps.sh
    
    ./install_deps.sh

## 工具使用

    
    
    python3 liveTargetsFinder.py [domainList] [options]

 ** **参数选项****

|

 ** **描述****

|

 ** **默认值****

|

 ** **是否必须****  
  
---|---|---|---  
  
\--target-list

|

包含目标域名列表的输入文件，例如google.com

| |

是  
  
\--massdns-path

|

MassDNS可执行文件路径

|

./massdns/bin/massdns

|

否  
  
\--masscan-path

|

Masscan可执行文件路径

|

./masscan/bin/masscan

|

否  
  
\--nmap

|

针对生成的活动主机执行Nmap版本检测扫描

|

Disabled

|

否  
  
\--db-path

|

如果使用了--nmap选项，则需要提供需要添加的数据库路径

|

output/liveTargetsFinder.sqlite3

|

否  
  
## 工具使用样例

如果你运行了工具安装脚本，则可以使用下列命令运行LiveTargetsFinder：

    
    
    python3 liveTargetsFinder.py --target-list victim_domains.txt

如果你没有运行工具安装脚本，则需要使用下列命令运行LiveTargetsFinder：

    
    
    python3 liveTargetsFinder.py --target-list victim_domains.txt --massdns-path ../massdns/bin/massdns --masscan-path ../masscan/bin/masscan

执行Nmap扫描和写入/追加默认数据库路径（liveTargetsFinder.sqlite3）：

    
    
    python3 liveTargetsFinder.py --target-list victim_domains.txt --nmap

执行Nmap扫描和写入/追加指定的数据库路径：

    
    
    python3 liveTargetsFinder.py --target-list victim_domains.txt --nmap --db-path serviceinfo_victim.sqlite3

## 工具输出

> 输入文件：victimDomains.txt

文件

|

描述

|

样例  
  
---|---|---  
  
output/victimDomains_targetUrls.txt

|

可抵达的活动主机URL列表

|

https://github.com, http://github.com  
  
output/victimDomains_domains_alive.txt

|

活动域名列表

|

github.com, google.com  
  
output/victimDomains_ips_alive.txt

|

活动IP列表

|

10.1.0.200, 52.3.1.166  
  
指定的或默认数据库路径

|

存储了活动主机及其运行服务的SQLite数据库

|  
  
output/victimDomains_massdns.txt

|

MassDNS的原始输出，格式为ndjson

|  
  
output/victimDomains_masscan.txt

|

Masscan的原始输出，格式为ndjson

|  
  
output/victimDomains_nmap.txt

|

Nmap的原始输出，格式为XML

|  
  
## 工具运行截图

![](https://image.3001.net/images/20220911/1662869207_631d5ed733c2f76299ecf.png!small)

## 项目地址

 **LiveTargetsFinder** ：【[
_GitHub传送门_](https://github.com/allyomalley/LiveTargetsFinder)】

## 参考资料

> [
> _https://github.com/blechschmidt/massdns_](https://github.com/blechschmidt/massdns)
>
> [
> _https://github.com/robertdavidgraham/masscan_](https://github.com/robertdavidgraham/masscan)
>
> [ _https://nmap.org/_](https://nmap.org/)

