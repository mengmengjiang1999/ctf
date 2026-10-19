## 0x0 背景

**近日，深信服安全团队接到某大型进出口企业反馈，根据安全感知平台提示，内网部分邮箱遭受到恶意邮件的攻击。通过安全研究人员分析发现，该恶意邮件包含一个疑似lokibot恶意软件的附件，主要是用于窃取用户各类账号密码等机密信息。通过过程中的一些数据分析确定这是一起针对特定行业的定向攻击事件。**

## 0x1 过程

通过对安全感知平台里面的安全日志分析可以发现，客户的部分邮箱收到了很多恶意邮件，发件人地址主要是​srwuIan@maybank.co.id
(maybank:马来西亚银行)，maybank迷惑用户取得信任。主题为Remittance
advice(汇款通知单)，而且针对的收件人对象也很明确，主要包括此类公共邮箱：planning(计划)、dataprocess(数据处理)、barge(船舶)、bargecontrol
、dpsloading(dps:船舶动力定位系统)等，截图如下：

![图片0.png](https://image.3001.net/images/20190731/1564565268_5d415f14e0680.png!small)

源地址是一个来自美国的IP地址：142.4.5.244

![图片1.png](https://image.3001.net/images/20190731/1564565280_5d415f206ac33.png!small)

通过Virustotal对该IP进行关联，未发现相关的恶意行为。

![图片2.png](https://image.3001.net/images/20190731/1564565308_5d415f3c949c5.png!small)

## 0x2 恶意附件

源附件为一个575Kb的可执行程序，主要伪装成了一个音频文件的图标，查看木马母体信息是一个用Delphi封装的文件，编译的时间戳被修改为1991-12-20。

![图片3.png](https://image.3001.net/images/20190731/1564565320_5d415f48ec513.png!small)

病毒母体在执行的过程中会首先解密payload到进程内存中执行，先进行反虚拟机、反沙箱、反杀软、反调试分析等操作，相关字符信息如下：

**功能模块** | **特征字符举例**  
---|---  
反虚拟机 | VMwareVMware、XenVMMXenVMM、prl hyperv、Microsoft Hv、KVMKVMKVM  
反沙箱 | sandbox、malware、sample、virus、selfrun  
反杀软 |
avp.exe、avastsvc.exe、avastui.exe、avgsvc.exe、avgui.exe、bdagent.exe、bdwtxag.exe、dwengine.exe  
反调试分析 |
procexp64.exe、procmon64.exe、procmon.exe、ollydbg.exe、procexp.exe、windbg.exe  
  
payload中使用大量的跳转来干扰调试，随后从资源中解密出PE文件后注入新的同名进程，该文件就是LokiBot的核心功能体。

![图片4.png](https://image.3001.net/images/20190731/1564565339_5d415f5bbc527.png!small)

LokiBot是在地下网站上销售的商业恶意软件，其功能是从受感染机器中窃取私人数据，然后通过HTTP
POST将该信息提交给CC主机，敏感数据主要包括：存储的密码，Web浏览器、FTP、SFTP的密码和凭证等信息。

**窃取信息模块** | **特征字符举例**  
---|---  
浏览器 | IE系列 、Mozilla Firefox (x32+x64)、Google Chrome、Opera  
连接工具 | FileZilla、Xftp、FlashFXP、Vandyk SecureFX、WinSCP、RealVNC  
Email端 | Foxmail、Outlook  
  
![图片5.png](https://image.3001.net/images/20190731/1564565354_5d415f6a78a7a.png!small)

下图主要为实现读取Mozilla 用户登录凭证的部分功能：

![图片6.png](https://image.3001.net/images/20190731/1564565366_5d415f7671617.png!small)

恶意程序会将窃取到的主机信息与敏感信息发送到C&C服务器，由于分析时C&C端没有开启，这里本地使用SimpleHTTP来模拟接收发送的数据内容，目的地址为：slomiter45u.us
。

可以清晰的发现木马向C2进行POST上传数据会带一个特殊字符“ckav.ru”，根据已知的情报，该域名可能与某地下黑客交易站点有关。

![图片7.png](https://image.3001.net/images/20190731/1564565380_5d415f84d9ede.png!small)

## 0x3解决方案

1、不要点击来源不明的邮件附件，特别是附件为可执行文件、带有宏的文档时，应提高警惕。

2、深信服为广大用户免费提供查杀工具，可下载如下工具，进行检测查杀：  

> 64位系统下载链接：<http://edr.sangfor.com.cn/tool/SfabAntiBot_X64.7z>
>
> 32位系统下载链接：<http://edr.sangfor.com.cn/tool/SfabAntiBot_X86.7z>

 ***本文作者：深信服千里目安全实验室，转载请注明来自FreeBuf.COM**

