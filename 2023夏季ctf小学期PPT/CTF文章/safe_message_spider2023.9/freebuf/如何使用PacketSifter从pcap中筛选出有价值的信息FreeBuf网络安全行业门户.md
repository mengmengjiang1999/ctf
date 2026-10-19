![](https://image.3001.net/images/20210914/1631631419_6140b83b8f27e18240829.png!small)

## 关于PacketSifter

PacketSifter这款工具旨在帮助广大研究/分析人员 **从捕捉到的数据包文件（pcap）中筛选出其中有价值或值得分析的流量数据**
。PacketSifter可以接受一个pcap文件作为输入参数，并输出多个分析结果文件。

当前版本的PacketSifter在经过优化改进之后，允许用户与其进行更加精简的交互，我们可以运行./packetsifter
-h以了解新版本PacketSifter的具体使用方式。

## 工作机制

我们只需要向PacketSifter提供一个待分析的pcap文件，然后使用适当的参数运行筛选分析工作，PacketSifter将会给我们直接提供分析结果文件。

在运行PacketSifter主程序之前，为了保证分析正常执行，请先运行AbuseIPDBInitial.sh和VTInitial.sh。

## 工具要求

tshark -[_https://tshark.dev/setup/install/﻿_](https://tshark.dev/setup/install/)

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/packetsifter/packetsifterTool.git

## 命令行选项

-a：针对DNS A记录中的IP地址启用AbuseIPDB查询；

-h：打印帮助信息；

-i：输入文件【必须】；

-r：解析pcap中的主机名；

-v：针对SMB/HTTP对象启用VirusTotal查询；

## VirusTotal整合

PacketSifter可以通过VirusTotal API对通过SMB/HTTP发现的导出对象执行哈希查询。

首先，我们需要在本地设备上安装并配置好[ _jq_](https://stedolan.github.io/jq/download/)：

    
    
    root@ubuntu:~# apt-get install jq

接下来，确保已经安装好了curl：

    
    
    root@ubuntu:~# apt-get install curl

现在，切换到项目根目录下，并运行VTInitial.sh，然后提供你的VirusTotal API密钥（64位）。关于如何获取免费的VirusTotal
API密钥，可以参考这篇【[ _文档_](https://developers.virustotal.com/reference)】。

 **VTInitial.sh的正常输出如下图所示：**

![](https://image.3001.net/images/20210914/1631631452_6140b85ce8f00a5838b39.png!small)

使用-v参数运行PacketSifter以针对导出的HTTP和SMB对象启用VirusTotal查询。

 **成功执行后的VTInitial.sh输出结果如下图所示：**

![](https://image.3001.net/images/20210914/1631631459_6140b863396406749ea4c.png!small)

## AbuseIPDB整合

PacketSifter可以针对DNS A记录中的IP地址执行IP地理位置查询或IP名声查询。

首先，我们需要在本地设备上安装并配置好[ _jq_](https://stedolan.github.io/jq/download/)：

    
    
    root@ubuntu:~# apt-get install jq

接下来，确保已经安装好了curl：

    
    
    root@ubuntu:~# apt-get install curl

现在，切换到项目根目录下，并运行AbuseIPDBInitial.sh，然后提供你的AbuseIPDB API密钥（80位）。

关于如何获取免费的AbuseIPDB API密钥，可以参考这篇【[ _文档_](https://www.abuseipdb.com/register)】。

注意：免费的AbuseIPDB API密钥每天只能执行1000次查询。

 **AbuseIPDBInitial.sh的正常输出如下图所示：**

![](https://image.3001.net/images/20210914/1631631478_6140b8762d5452e5b440b.png!small)

使用-a参数运行PacketSifter以通过AbuseIPDB针对DNS A记录执行查询。

 **成功执行后的AbuseIPDBInitial.sh输出结果如下图所示：**

![](https://image.3001.net/images/20210914/1631631485_6140b87d11966d9efd845.png!small)

## 工具使用样例

    
    
    root@ubuntu:~# ./packetsifter -i /tmp/testing.pcap -a -r -v

## 项目地址

 **PacketSifter：** 【[
_GitHub传送门_](https://github.com/packetsifter/packetsifterTool)】

## 参考资料

> [ _https://tshark.dev/setup/install/_](https://tshark.dev/setup/install/)
>
> [
> _https://stedolan.github.io/jq/download/_](https://stedolan.github.io/jq/download/)
>
> [
> _https://developers.virustotal.com/reference_](https://developers.virustotal.com/reference)
>
> [ _https://www.abuseipdb.com/register﻿_](https://www.abuseipdb.com/register)

