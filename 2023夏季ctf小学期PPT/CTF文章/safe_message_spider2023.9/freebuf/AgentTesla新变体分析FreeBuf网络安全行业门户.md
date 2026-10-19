**AgentTesla是基于.Net的恶意软件，可从受害机器窃取不同应用程序的数据（例如浏览器，FTP客户端和文件下载器）。攻击者通过添加新模块不断对其进行更新维护，该恶意软件最新添加了WiFi配置文件窃取模块。**

AgentTesla于2014年首次出现，此后一直出现在各种恶意活动中。2020年3月和4月发现攻击者通过垃圾邮件，用各种文件格式传播恶意软件，例如ZIP，CAB，MSI，IMG文件和Office文档。  

## 技术分析

恶意软件变体是用.net开发的，可嵌入图像之中，在运行后释放执行：

![image.png](https://image.3001.net/images/20200420/1587365001_5e9d4489c2a58.png!small)该可执行文件（ReZer0V2）含有加密资源。
在反调试，反沙箱和反虚拟操作后，可执行文件解密并注入：

![image.png](https://image.3001.net/images/20200420/1587366708_5e9d4b345f20f.png!small)第二个有效负载（owEKjMRYkIfjPazjphIDdRoPePVNoulgd）是AgentTesla的主要组件，它从浏览器，FTP客户端，无线配置等文件中窃取凭据：  

![image.png](https://image.3001.net/images/20200420/1587366760_5e9d4b686f860.png!small)传递“
wlan show profile”参数创建“netsh”。 然后用正则表达式“All User Profile * :
(?<profile>.*)”提取可用的WiFi名称：  

![image.png](https://image.3001.net/images/20200420/1587366842_5e9d4bbaa8b8c.png!small)执行以下命令以提取凭据：“netsh
wlan show profile PRPFILENAME key=clear”：  

##
![image.png](https://image.3001.net/images/20200420/1587366896_5e9d4bf0a7552.png!small)字符串加密

恶意软件使用的所有字符串通过Rijndae均已加密，加密解密过程如下：  

![image.png](https://image.3001.net/images/20200420/1587366984_5e9d4c48c80f7.png!small)  

在上图中，“ 119216”被解密为“ wlan show profile name =”，“ 119196”被解密为“ key = clear”。

除了WiFi配置文件外，恶意软件还收集其他系统信息，包括FTP客户端，浏览器，PC信息（用户名，计算机名，操作系统名称，CPU体系结构，RAM）。  

  

![image.png](https://image.3001.net/images/20200420/1587367083_5e9d4cab2bca7.png!small)收集的信息以html格式写在SMTP邮件正文：  

![image.png](https://image.3001.net/images/20200420/1587367146_5e9d4ceaa42ac.png!small)如果最终列表中的元素少于三个，则不会生成SMTP邮件。
如果符合检查条件，消息会通过smtp.yandex.com发送：  

![image.png](https://image.3001.net/images/20200420/1587367214_5e9d4d2e8af62.png!small)下图显示了恶意软件工作的整个过程：  

##
![image.png](https://image.3001.net/images/20200420/1587367256_5e9d4d58f0910.png!small)总结

AgentTesla变体添加了WiFi窃取功能，攻击者可能正在考虑将WiFi作为新的传播机制，或是使用WiFi配置文件为下一步攻击做准备。  

## IOCs

### AgentTesla samples

> 91b711812867b39537a2cd81bb1ab10315ac321a1c68e316bf4fa84badbc09b  
>
>
> dd4a43b0b8a68db65b00fad99519539e2a05a3892f03b869d58ee15fdf5aa044
>
> 27939b70928b285655c863fa26efded96bface9db46f35ba39d2a1295424c07b

### First payload

> 249a503263717051d62a6d65a5040cf408517dd22f9021e5f8978a819b18063b  
>

### Second payload  

> 63393b114ebe2e18d888d982c5ee11563a193d9da3083d84a611384bc748b1b0  
>

 ***参考来源：[malwarebytes](https://blog.malwarebytes.com/threat-analysis/2020/04/new-agenttesla-variant-steals-wifi-credentials/)，由Kriston编译，转载请注明来自FreeBuf.COM**  

