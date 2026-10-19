## 背景

近期，360威胁情报中心协助用户处理了多起非常有针对性的邮件钓鱼攻击事件，被攻击目标包括中国境内的巴基斯坦重要商务人士，该轮攻击活动最早发生在2018年5月，攻击者对目标机器进行了长时间的控制。360威胁情报中心在本文中对本次的钓鱼攻击活动的过程与技术细节进行揭露，希望相关组织和个人能够引起足够重视并采取必要的应对措施。

2017年，360公司发现并披露了主要针对巴基斯坦等南亚地区国家进行网络间谍活动的组织[1]，内部跟踪代号为APT-C-35，其后网络安全厂商Arbor公开了该组织的活动并命名为Donot[2]。此APT组织主要针对政府机构等领域进行攻击，以窃取敏感信息为主要目的。从2017年至今，该组织针对巴基斯坦至少发动了4波攻击行动，攻击过程主要是以携带Office漏洞或者恶意宏的鱼叉邮件进行恶意代码的传播，并先后使用了两套独有的恶意代码框架：EHDevel和yty。而在这一波攻击中，Donot团伙瞄准了在我国境内的巴基斯坦商务人士。

## 钓鱼攻击过程

攻击者针对目标的整个攻击过程如下：

  

![image.png](https://image.3001.net/images/20181213/1544674388_5c11dc54a0f9f.png!small)

## 恶意代码分析

360威胁情报中心对整个攻击过程进行了详细分析，过程如下。

### Dropper - Excel Macros

攻击者通过向目标邮箱发送带有恶意宏的Excel诱饵文档诱骗目标执行，宏代码成功执行后会在C:\micro释放office_update.exe，并执行该EXE文件。诱饵文档内容为宝马汽车促销的相关信息，这和受害者所从事的商务活动密切相关，极易取得受害者的信任：

  

![image.png](https://image.3001.net/images/20181213/1544674395_5c11dc5b8d585.png!small)

### Downloader - office_update.exe

文件名| office_update.exe  
---|---  
MD5| 2320ca79f627232979314c974e602d3a  
  
office_updata.exe则是一个下载者，其会通过<http://bigdata.akamaihub.stream/pushBatch>下载一个BAT文件并执行：

  

![image.png](https://image.3001.net/images/20181213/1544674403_5c11dc631c0da.png!small)

该BAT文件主要功能为设置自启动项实现持久化、创建隐藏的文件目录等，office_updata.exe还会从<http://bigdata.akamaihub.stream/pushAgent>下载文件保存到%USERPROFILE%\BackConfig\BackUp目录下，并命名为wlidsvcc.exe：

  

![image.png](https://image.3001.net/images/20181213/1544674408_5c11dc68add55.png!small)

office_updata.exe最后会实现自删除：

  

![image.png](https://image.3001.net/images/20181213/1544674413_5c11dc6daf99f.png!small)

### Plugin-Downloader - wlidsvcc.exe

文件名| wlidsvcc.exe  
---|---  
MD5| 68e8c2314c2b1c43709269acd7c8726c  
  
wlidsvcc.exe也是一个下载者，wlidsvcc.exe会与C2通信下载后续需要执行的插件：wuaupdt.exe、kylgr.exe、svchots.exe等等，并启动wuaupdt.exe。样本运行后通过创建互斥量“wlidsvcc”以保证只有一个实例运行：

  

![image.png](https://image.3001.net/images/20181213/1544674422_5c11dc764eab2.png!small)

随后判断当前进程路径是否为%USERPROFILE%BackConfig\BackUp\wlidsvcc.exe：

  

![image.png](https://image.3001.net/images/20181213/1544674427_5c11dc7b8bd7d.png!small)

若路径满足条件后，以POST方式与C2：bigdata.akamaihub.stream进行通信，并获取后续的控制指令：

  

![image.png](https://image.3001.net/images/20181213/1544674432_5c11dc8090d3f.png!small)

通过判断C2返回数据，根据不同指令执行不同操作，当指令为“no”时，则Sleep 90秒后再与C2继续通信：

  

![image.png](https://image.3001.net/images/20181213/1544674440_5c11dc88ba5ca.png!small)

当命令为“cmdline”时，则启动插件执行器：%USERPROFILE%\BackConfig\BackUp\wuaupdt.exe，并继续与C2通信：

  

![image.png](https://image.3001.net/images/20181213/1544674445_5c11dc8d66cac.png!small)

当指令不是上述两条指令，则从<http://bigdata.akamaihub.stream/orderMe>下载文件保存到路径C:\Users\%s\BackConfig\BigData，之后继续与C2通信获取需要执行的指令：

  

![image.png](https://image.3001.net/images/20181213/1544674450_5c11dc922d0ac.png!small)

### Plugin executor - wuaupdt.exe

文件名| Wuaupdt.exe  
---|---  
MD5| 35ec92dbd07f1ca38ec2ed4c4893f7ed  
  
wuaupdt.exe本身的功能是一个CMD后门，其会与C2通信执行一些CMD命令。并且还会通过攻击者下发的指令执行其他的插件，所有后门插件的分析见下节。

通过C2获取指令执行：

  

![image.png](https://image.3001.net/images/20181213/1544674455_5c11dc971491d.png!small)

### Backdoor – Plugins

wuaupdt.exe会根据攻击者下发的指令执行对应的插件，相关插件分析如下。

#### Keylogger - Kylgr.exe

文件名| Kylgr.exe  
---|---  
MD5| 88f244356fdaddd5087475968d9ac9bf  
PDB路径|
c:\users\user\documents\visualstudio2010\Projects\newkeylogger\Release\new
keylogger.pdb  
  
该插件的主要功能为键盘记录，其首先会在当前目录创建文件inc3++.txt，并检索%USERPROFILE%\Printers\Neighbourhood目录下是否已有历史键盘记录文件存在，若有则将文件名与最后修改时间保存到inc3++.txt：

  

![image.png](https://image.3001.net/images/20181213/1544674461_5c11dc9dd2e2c.png!small)

  

![image.png](https://image.3001.net/images/20181213/1544674468_5c11dca40f56e.png!small)

如果%USERPROFILE%\Printers\Neighbourhood路径下有历史键盘记录文件，则将历史键盘记录文件移动到%USERPROFILE%\Printers\Neighbourhood\Spools目录下：

  

![image.png](https://image.3001.net/images/20181213/1544674471_5c11dca7060e0.png!small)

之后在%USERPROFILE%\Printers\Neighbourhood下创建格式为“用户名_年_月_日(时_分_秒)”的文本文件，用于记录当前的键盘记录，最后循环获取是否有键盘鼠标操作：

  

![image.png](https://image.3001.net/images/20181213/1544674474_5c11dcaa6e0ac.png!small)

如果获取到窗口名，将窗口名和按键信息保存到创建的文本文件中：

  

![image.png](https://image.3001.net/images/20181213/1544674479_5c11dcafd3f29.png!small)

#### file-listing - svchots.exe

文件名| svchots.exe  
---|---  
MD5| 14eda0837105510da8beba4430615bce  
  
文件搜集插件首先会遍历C、D、E、F、G、H盘：

  

![image.png](https://image.3001.net/images/20181213/1544674484_5c11dcb4a1bf3.png!small)

并排除以下目录：

  

![image.png](https://image.3001.net/images/20181213/1544674489_5c11dcb94119f.png!small)

然后获取以下扩展名的文件：

  

![image.png](https://image.3001.net/images/20181213/1544674499_5c11dcc30e5cb.png!small)

当找到有以上扩展名的文件后，将文件名与最后的修改日期写入当前目录下的test.txt文件中，并将搜集到的文件加上txt后缀后复制到%USERPROFILE%\Printers\Neighbourhood\Spools目录下：

  

![image.png](https://image.3001.net/images/20181213/1544674503_5c11dcc7a5b83.png!small)

#### Systeminfo - spsvc.exe

文件名| spsvc.exe  
---|---  
MD5| 2565215d2bd8b76b4bff00cd52ca81be  
  
系统信息搜集插件使用UPX加壳，脱壳后根据字符串相关信息可以知道是go语言编写的程序。该插件会创建多个CMD进程执行命令，获取系统相关信息，并将获取的信息保存到目录%USERPROFILE%\Printers\Neighbourhood\Spools：

  

![image.png](https://image.3001.net/images/20181213/1544674509_5c11dccd82ed9.png!small)

#### Uploader - lssm.exe

文件名| lssm.exe  
---|---  
Md5| 23386af8fd04c25dcc4fdbbeed68f8d4  
  
文件上传插件主要用于将%USERPROFILE%Printers\Neighbourhood\Spools目录下，由木马收集的敏感信息和文件上传到C2：bigdata.akamaihub.stream

  

![image.png](https://image.3001.net/images/20181213/1544674514_5c11dcd2ccf77.png!small)

#### Uploader - lssmp.exe

文件名| lssmp.exe  
---|---  
MD5| b47386657563c4be9cec0c2f2c5f2f55  
数字签名| COMODO CA Limited  
  
和lssm.exe功能类似的另外一个文件上传插件为lssmp.exe，该样本包含数字签名：

  

![image.png](https://image.3001.net/images/20181213/1544674520_5c11dcd8a3bcc.png!small)

插件执行后会从当前进程列表中找到explorer.exe进程：

  

![image.png](https://image.3001.net/images/20181213/1544674526_5c11dcde30d1b.png!small)

然后获取插件的资源节，并解密出一个PE文件：

  

![image.png](https://image.3001.net/images/20181213/1544674530_5c11dce2d0e71.png!small)

将解密的PE文件注入到explorer.exe执行：

  

![image.png](https://image.3001.net/images/20181213/1544674535_5c11dce764de4.png!small)

注入的PE文件在功能与lssm.exe插件一致，上传其他插件收集的键盘信息到C2：

  

![image.png](https://image.3001.net/images/20181213/1544674541_5c11dced9d8aa.png!small)

## 关联样本分析

360威胁情报中心通过内部大数据关联到此次的攻击团伙使用的其它一些诱饵文档和插件，相关分析如下。

### CSD_Promotion_Scheme_2018.xls

文件名| CSD_Promotion_Scheme_2018.xls  
---|---  
MD5| 82a5b24fddc40006396f5e1e453dc256  
  
该诱饵文档同样是利用恶意宏的Excel样本，打开文档后会提示启用宏：

  

![image.png](https://image.3001.net/images/20181213/1544674547_5c11dcf3a6e78.png!small)

恶意宏代码的主要功能为在%APPDATA%目录下释放Skype.exe，在C:\Skype目录下释放Skype.bat，并执行Skype.bat文件：

  

![image.png](https://image.3001.net/images/20181213/1544674555_5c11dcfb39fed.png!small)

宏代码执行后同样会显示一个宝马汽车促销的相关图片：

  

![image.png](https://image.3001.net/images/20181213/1544674561_5c11dd01ddc6f.png!small)

### Skyep.bat

Skyep.bat会重新创建%USERPROFILE%Printers\Neighbourhood\Spools、%USERPROFILE%\BackConfig\BackUp和%USERPROFILE%\BackConfig\BigData文件夹，并将这些文件夹属性设置为隐藏：

  

![image.png](https://image.3001.net/images/20181213/1544674566_5c11dd06b7cf4.png!small)

该BAT文件还会获取计算机名，将获取到的计算机名和5位随机数字组成字符串保存到%USERPROFILE%\BackConfig\Backup\pcap.txt中：

  

![image.png](https://image.3001.net/images/20181213/1544674570_5c11dd0ac3462.png!small)

并创建多个自启动项，为后续下载执行的插件设置持久化。最后启动Skyep.exe，并删除自身：

  

![image.png](https://ti.360.net/uploads/2018/12/11/c47141f592908f8493916141778dd6cb.png)

### Skyep.exe

文件名| Skyep.exe  
---|---  
MD5| f67595d5176de241538c03be83d8d9a1  
PDB| C:\Users\spartan\Documents\Visual Studio 2010\Projects\downloader new 22
jun use\downloader\Release\downloader.pdb  
  
Skyep.exe的主要功能为下载执行，文件名则伪装成语音软件Skype，其会从<http://databig.akamaihub.stream/pushBatch>（还存活）下载文件保存到\BackConfig\BackUp\csrsses.exe并执行，且Skyep.bat文件中已经把该文件写入到自启动项：

  

![image.png](https://image.3001.net/images/20181213/1544674594_5c11dd22c9255.png!small)

### Csrsses.exe

文件名| Csrsses.exe  
---|---  
MD5| e0c0148ca11f988f292f527733e54fca  
  
该样本与前面分析的wlidsvcc.exe功能类似，都是与C2通信获取后续插件执行。

样本主要功能是与C2通信获取后续插件执行，首先从\\\BackConfig\\\BackUp\\\pcap.txt读取出计算机名：

  

![image.png](https://image.3001.net/images/20181213/1544674599_5c11dd27aa7ab.png!small)

然后将计算机名封装成字符串：“orderme/计算机名-随机数”，以POST方式与C2：databig.akamaihub.stream进行通信，获取后续命令执行：

  

![image.png](https://image.3001.net/images/20181213/1544674605_5c11dd2d255a2.png!small)

之后通过判断返回网络数据中的Content-Type进行后续操作：如果是“application”，则从C2获取文件保存到\\\BackConfig\\\BigData\\\目录下：

  

![image.png](https://image.3001.net/images/20181213/1544674609_5c11dd31d33cc.png!small)

如果是“cmdline”，则执行\\\BackConfig\\\BigData\\\wuaupdt.exe，并继续与C2通信：

  

![image.png](https://image.3001.net/images/20181213/1544674615_5c11dd37c2f20.png!small)

当等于“batcmd”时，则启动\\\BackConfig\\\BigData\\\test.bat，并且继续与C2通信：

  

![image.png](https://image.3001.net/images/20181213/1544674621_5c11dd3d3fff2.png!small)

## 溯源 – Donot（APT-C-35）

360威胁情报中心通过对此次攻击中使用的宏代码、插件、域名/IP关联分析，以及使用360威胁情报中心分析平台对相关样本和网络基础设施进行拓展，我们确认此次攻击的幕后团伙为Donot
APT组织（APT-C-35）。

### 宏代码相似

2018年3月ASERT曝光的DONOT APT组织[2]的宏利用样本和本次攻击活动中使用的宏利用样本相似度极高，并且都是执行完宏后弹出一个诱饵图片。

  

![image.png](https://image.3001.net/images/20181213/1544674626_5c11dd42afc99.png!small)

### 插件相似度

和之前的Donot样本一致，这次的样本也是通过重C&C获取插件执行的插件式木马。其中都有UPX加壳的go语言木马，且代码逻辑高度一致：

  

![image.png](https://image.3001.net/images/20181213/1544674633_5c11dd49a5495.png!small)

本次攻击活动中的wuaupdt.exe在之前的Donot攻击活动中[1]也曾出现，且C2地址一致。

## 总结

从本次捕获到的Donot
APT攻击活动来看，该APT团伙依然以巴基斯坦相关人士作为首要攻击目标，甚至将攻击范围扩大到包括在华的巴基斯坦人员和机构。种种迹象表明，Donot
APT组织（APT-C-35）从未停止自己的攻击活动，或许近期会再次发动新的网络间谍攻击。

360威胁情报中心再次提醒各企业用户，加强员工的安全意识培训是企业信息安全建设中最重要的一环，如有需要，企业用户可以建设态势感知，完善资产管理及持续监控能力，并积极引入威胁情报，以尽可能防御此类攻击。

目前，基于360威胁情报中心的威胁情报数据的全线产品，包括360威胁情报平台（TIP）、天眼高级威胁检测系统、360
NGSOC等，都已经支持对此APT攻击团伙攻击活动的检测。

## IOC

 **MD5**  
---  
82a5b24fddc40006396f5e1e453dc256  
f67595d5176de241538c03be83d8d9a1  
e0c0148ca11f988f292f527733e54fca  
2320ca79f627232979314c974e602d3a  
68e8c2314c2b1c43709269acd7c8726c  
35ec92dbd07f1ca38ec2ed4c4893f7ed  
88f244356fdaddd5087475968d9ac9bf  
14eda0837105510da8beba4430615bce  
2565215d2bd8b76b4bff00cd52ca81be  
23386af8fd04c25dcc4fdbbeed68f8d4  
b47386657563c4be9cec0c2f2c5f2f55  
 **C &C**  
databig.akamaihub.stream  
bigdata.akamaihub.stream  
185.236.203.236  
unique.fontsupdate.com  
 **PDB路径**  
C:\Users\spartan\Documents\Visual Studio 2010\Projects\downloader new 22 jun
use\downloader\Release\downloader.pdb  
C:\users\user\documents\visualstudio2010\Projects\newkeylogger\Release\new
keylogger.pdb  
  
## 参考

  1. <https://ti.360.net/blog/articles/latest-activity-of-apt-c-35/>

  2. <https://asert.arbornetworks.com/donot-team-leverages-new-modular-malware-framework-south-asia/>

  

