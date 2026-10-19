## 背景  

CiscoTalos研究团队在近期披露了一例针对印度iOS用户的定向攻击活动[1]，但原文并没有明确攻击组织相关背景。360威胁情报中心结合内部威胁情报数据和该公开报告中披露的IOC信息，关联到多份公开情报，并发现该事件的攻击组织极有可能就是“摩诃草”组织(又常称为Hangover，Patchwork，DroppingElephant)，并且分析了该事件与Bellingcat披露的Bahamut[2]和趋势科技披露的Confucius[3]间的联系。本报告是对相关线索和背景推测的分析说明。

截至我们分析和文档完成时，Cisco Talos研究团队披露了后续分析进展，并同样提及了和Bahamut的关联性[6]。

## 关联样本分析

360威胁情报中心结合内部的威胁情报数据关联到相关的针对Windows平台和Android平台的恶意代码样本。

### Windows平台

#### Delphi Dropper

我们发现一批Delphi编写的Dropper程序，其中一个样本回连URL地址为<http://techwach.com/expendedrange98gh/>，该Dropper程序主要收集目标主机信息，并可以下载更多载荷文件并执行。以下为对该类Dropper的分析。

其首先在%userprofile%下创建Docoument目录，然后通过GetSystemInfo或查询注册表信息获取系统版本信息。

  

![image.png](https://image.3001.net/images/20180727/1532677106_5b5acbf2933ee.png!small)

其生成一个随机ID字符串，并写入% userprofile%\Docoument下的eventdriven.dat文件，该字符串用于标识受害主机。

其通过WMI查询获取更多主机信息，包括主机名称，操作系统信息以及安装的安全软件。

  

![image.png](https://image.3001.net/images/20180727/1532677111_5b5acbf7e6ef2.png!small)

  

![image.png](https://image.3001.net/images/20180727/1532677115_5b5acbfb7896a.png!small)

该Dropper程序在窗体上实现了三个Timer。

  

![image.png](https://image.3001.net/images/20180727/1532677123_5b5acc0398c6c.png!small)

其中一个Timer会向控制服务器发送HTTP请求，其URL为<http://digitizet.com/express54354view/>。

  

![image.png](https://image.3001.net/images/20180727/1532677129_5b5acc0949310.png!small)

并且下载下一阶段载荷命令执行。

  

![image.png](https://image.3001.net/images/20180727/1532677133_5b5acc0d19fa6.png!small)

另外一个Timer会获取本机信息，包括用户名，主机名，系统版本，安全软件信息，并存储到%
userprofile%\Docoument的Detail.log文件。

![image.png](https://image.3001.net/images/20180727/1532677149_5b5acc1d4dd10.png!small)  

其随后上传文件内容到远程URL，docc7686gg154po.php?b=

  

![image.png](https://image.3001.net/images/20180727/1532677159_5b5acc2775a5e.png!small)

加密

Delphi Dropper程序对关键的字符串信息进行加密，其解密算法主要有两种不同形态。

其中一种解密算法使用了硬编码的密钥，如dc67f@#$%hlhsdfg。下图为解密算法的结构视图。

  

![image.png](https://image.3001.net/images/20180727/1532677168_5b5acc300b2df.png!small)

  

![image.png](https://image.3001.net/images/20180727/1532677171_5b5acc33c704c.png!small)

### Android平台

通过voguextra.com域名可以关联到一个Android样本，其默认界面加载图片URL从voguextra.com域名下加载。

  

![image.png](https://image.3001.net/images/20180727/1532677178_5b5acc3a875f8.png!small)

其会收集包括短信，通讯录等信息，以及外存储路径下的.txt,
.db.crypt，.db.crypt8，.db.crypt5，.db.crypt7，.doc，.docx，.xls，.xlsx，.csv，.pdf，.jpeg，.jpg扩展名的文件列表和内容。

解密的上传URL地址如下：

  

![image.png](https://image.3001.net/images/20180727/1532677185_5b5acc41c5899.png!small)

### iOS平台

结合Cisco Talos团队发现的MDM后台地址和开源的mdm-server[5]实现，攻击组织并未修改默认的服务端监听地址，并且扩展了默认的请求连接。

  

![image.png](https://image.3001.net/images/20180727/1532677198_5b5acc4e5ddd1.png!small)

  

![image.png](https://image.3001.net/images/20180727/1532677202_5b5acc52800eb.png!small)

访问该MDM后台可以下载描述文件，我们发现其增加了向受害设备推送Telegram等应用的指令。

我们访问的时候，MDM设备注册的请求已经失效，但依然留存了3台iOS设备的日志信息，推测可能为安全研究人员的测试设备。

  

![image.png](https://image.3001.net/images/20180727/1532677216_5b5acc60c018c.png!small)

## 攻击来源分析

### 与"Confucius"的联系

在对线索和攻击来源的深入挖掘过程中，发现其中一个Delphi
Dropper程序回连了logstrick.com域名，该域名曾被趋势披露为Confucius使用[3]。

### 与"摩诃草"的联系

并且同类Delphi
Dropper程序还回连了<http://ebeijingcn.live/templates>地址，该控制域名曾被360威胁情报中心披露的《摩诃草APT组织针对我国敏感机构最新的网络攻击活动分析》分析过[4]。

  

![image.png](https://image.3001.net/images/20180727/1532677222_5b5acc66e9795.png!small)

### 与"Bahamut"的联系

通过分析关联到的Android样本，我们发现其与"Bahamut"组织有关，该组织是Bellingcat披露的一个针对中东和南亚地区的APT攻击组织。[3]

![image.png](https://image.3001.net/images/20180727/1532677236_5b5acc74f255b.png!small)

![image.png](https://image.3001.net/images/20180727/1532677247_5b5acc7f7a143.png!small)  
  

我们对三个组织的TTP进行简单对比：

|  **Confucius** |  **摩诃草(又称Hangover，Patchwork，Dropping Elephant)** |
**Bahamut**  
---|---|---|---  
**攻击目标** |  南亚 |  中国，巴基斯坦为主 |  南亚(主要为巴基斯坦)，中东  
**攻击平台** |  PC，Android |  PC，Android |  Android  
**恶意代码实现** |  Delphi |  Delphi，C# |  
**攻击入口** |  社交网络 |  鱼叉攻击，社交网络 |  鱼叉攻击，社交网络  
  
结合攻击恶意代码的功能结构的高度相似性，恶意载荷使用的控制域名的重叠，以及TTP的重叠，我们认为三个组织极有可能归属同一攻击组织。

## 总结

360威胁情报中心结合公开情报和内部威胁情报数据，确定了摩诃草组织(又称Hangover，Patchwork，DroppingElephant)与"
Confucius"，" Bahamut"间存在的关联性，并推测Cisco Talos披露的针对印度iOS用户的攻击事件极有可能与摩诃草有关。

## IOC

voguextra.com (OSINT)

techwach.com (OSINT)

[www.scorpviz.com](http://www.scorpviz.com)

digitizet.com

disc4l.com

logstrick.com

qutonium.com

classmunch.com

appswonder.info

conioz.com

pcupdate.ddns.net

windefendr.com

object2d.com

eec26ee59a6fc0f4b7a2a82b13fe6b05(Android)

899720af1cf9413a00f1b1a13f699eda

43e79de28318e2e5f4936ada7d09a4dc

## 参考链接

1.<https://blog.talosintelligence.com/2018/07/Mobile-Malware-Campaign-uses-Malicious-MDM.html>

2.<https://www.bellingcat.com/resources/case-studies/2017/10/27/bahamut-revisited-cyber-espionage-middle-east-south-asia/>

3.<https://blog.trendmicro.com/trendlabs-security-intelligence/confucius-update-new-tools-and-techniques-further-connections-with-patchwork/>

4.<https://ti.360.net/blog/articles/analysis-of-apt-c-09-target-china/>

5.<https://github.com/project-imas/mdm-server>

6.<https://blog.talosintelligence.com/2018/07/Mobile-Malware-Campaign-uses-Malicious-MDM-Part2.html>

## 原文链接

<https://ti.360.net/blog/articles/analysis-of-targeted-attacks-suspected-of-patchover/>  

