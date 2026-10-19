![](https://image.3001.net/images/20220211/1644520258_62056342106d8f6529d0d.jpeg!small)  

## wireshark-forensics-plugin介绍

毫无疑问，Wireshark是目前应用最为广泛的网络流量分析工具，无论是实时网络流量分析，还是信息安全取证分析，或是恶意软件分析，Wireshark都是必不可缺的利器。尽管Wireshark为协议解析和过滤提供了极其强大的功能，但它暂时还无法提供任何有关目标网络节点的上下文信息。对于一名安全分析人员来说，TA必须梳理大量的PCAP文件来识别恶意活动，这就有点像大海捞针了。

wireshark-forensics-plugin是一个跨平台Wireshark插件，它能够将网络流量数据与威胁情报、资产分类和漏洞数据关联起来，以加速网络取证分析活动。该工具通过扩展Wireshark本地搜索过滤器来实现自身的功能，允许我们基于这些附加的上下文属性进行数据过滤。除此之外，该工具还可以处理PCAP文件并进行实时的流量捕捉。

## 工具功能

> 1、加载从MISP等威胁情报平台导出的恶意标识CSV，并将其与网络流量中的每个源/目标IP相关联。
>
> 根据IP范围到资产类型的映射加载资产分类信息，该映射能够过滤特定类型资产的传入/传出流量（例如，过滤“数据库服务器”、“员工笔记本电脑”等）。
>
> 2、将从Qualys/Nessus导出的漏洞扫描信息加载到CVE。
>
> 3、扩展本机Wireshark过滤器的功能，允许基于网络日志中每个源或目标IP地址的严重性、源、资产类型和CVE信息进行过滤。

## 工具使用

首先，我们需要使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/rjbhide/wireshark-forensics-plugin.git

项目中的data/formatted_reports目录包含三个文件：

> asset_tags.csv：有关资产IP/域/CIDR和相关标签的信息，并提供了针对内网IP和DNS服务器的参考示例；
>
> asset_vulnerabilities.csv：关于每项资产的CVE ID和最高CVSS评分的详细信息；
>
> indicators.csv：入侵威胁指标IoC数据，包含属性类型、值、严重性和威胁类型；

上述的三个文件都可以手动编辑，或者可以使用导出的MISP和Tenable
Nessus扫描报告生成漏洞和指标文件。此时，需要将导出的文件放在以下指定了确切名称的文件夹下：

> data/raw_reports/misp.csv：该文件可以通过以下路径从MISP导出：“Export->CSV_Sig->Generate then
> Download”；

![](https://image.3001.net/images/20220211/1644520302_6205636e1825df1dc33fc.png!small)

> data/raw_reports/nessus.csv：该文件可以通过Tenable Nessus接口导出；

![](https://image.3001.net/images/20220211/1644520309_62056375714ef3516de99.png!small)

接下来，选择“Options->Export as CSV->Select
All->Submit”，将下载下来的文件重命名为nessus.csv，然后拷贝至“raw_reports/nessus.csv”。

如果你打算从ThreatStream获取数据而不是MISP的话，则需要在config.json文件中提供用户名、API密钥和过滤器信息。每次你运行Python脚本时，工具都会尝试从ThreatStream获取最新的IoC并将其存储至data/formatted_reports/indicators.csv文件中。

如果你使用的是Windows系统，可以直接运行wft.exe，如果是macOS或Ubuntu的话，则需要运行“python
wtf.py”来安装和更新报告文件。脚本将会自动寻找Wireshark的安装路径。

安装完成之后，打开Wireshark，点击“Edit->Configuration
Profiles”，选择“wireshark_forensics_toolkit”：

![](https://image.3001.net/images/20220211/1644520329_620563897713369b271a3.png!small)

现在，启动Wireshark，打开一个PCAP文件或开启实时数据捕捉：

![](https://image.3001.net/images/20220211/1644520337_620563910033b860d2b04.png!small)

## 可用的过滤器列表

> wft.src.domain (使用以前的DNS流量进行源/域解析)
>
> wft.src.detection (使用IOC数据进行源IP/域检测)
>
> wft.src.severity (使用IOC数据的源IP/域检测漏洞严重性)
>
> wft.src.threat_type (使用IOC数据的源IP/域检测威胁类型的严重性)
>
> wft.src.tags (源IP/域资产标签)
>
> wft.src.os (漏洞报告中指定的源IP/域操作系统)
>
> wft.src.cve_ids (源IP/域的CVE ID列表，以逗号分隔)
>
> wft.src.top_cvss_score (给定主机的所有CVE ID中的CVSS评分)

## 项目地址

 **wireshark-forensics-plugin：** 【[
_GitHub传送门_](https://github.com/rjbhide/wireshark-forensics-plugin)】

