## **一、概述**

**近日，腾讯御见威胁情报中心发现了WannaMiner的新变种，该挖矿木马在挖取XMR同时还会下载远控木马，和以往的版本类似，这个WannaMiner挖矿木马的最新变种会查杀其他挖矿木马，保证自己独享系统资源。同时，该变种在自身入侵成功后会关闭高危端口，避免其他挖矿木马入侵，其目的同样是保证独享挖矿资源。**

此外，经过分析发现，该变种除了跟友商发布的MsraMiner家族在漏洞利用和恶意基础设施上高度一致，跟友商今年六月爆出的另一个家族HSMiner如出一辙。因此我们判断，WannaMiner、MsraMiner、HSMiner实际为同一家族的不同命名，背后为同一黑产团伙。

 **WannaMiner新变种具有如下特点：**

1.冒充微软系统文件，关闭Windows防火墙，添加任务自启动。

2.释放NSA攻击工具套件（永恒之蓝），扫描内网445端口横向扩散。

3.释放远程控制木马java.exe(文件名伪装)，该远控木马具体系统最高权限，可实现窃取隐私及一切远程管理任务。

4.释放挖矿模块we32.exe，有意思的是，这个挖矿模块除了会结束其他挖矿木马进程，还会在安装好自身之后，会关闭系统的135、137、138、139、445端口，避免这台机器被其他入侵者控制。

5.通过同源性分析，发现该木马与HSMiner挖矿木马高度相似，该木马下载了和HSMiner挖矿木马一样的远程控制模块。

6.通过比对以往的威胁情报，发现该木马使用的C2服务器与HSMiner挖矿木马有相关性。

7.同样，通过溯源分析，发现WannaMiner挖矿木马与MsraMiner挖矿木马同样相似度级高，C2服务器也存在复用。

通过5，6，7的分析，御见威胁情报中心判断不同安全团队报告的WannaMiner、MsraMiner与HSMiner背后的控制者为同一团伙。

##  **二、样本分析**

WannaMiner木马依然分为三个部分：传播模块、挖矿模块、远控模块。

###  **1、传播模块分析（32ja.exe）**

32ja.exe为自解压SFX文件，执行脚本会解压释放到“%windir%\IME\Microsofts”文件夹下，关闭防火墙，并隐藏文件，设置任务启动。

![1.png](https://image.3001.net/images/20180906/1536218459_5b90d55b0f439.png!small)

以服务执行的spoolsv.exe会释放NSA利用组件，并且扫描内网445端口开放的主机写入配置文件中，并利用永恒之蓝进行攻击。并且spoolsv.exe执行步骤会发送回C2服务器d.drawal.dk。

释放的NSA漏洞利用组件：

![2.png](https://image.3001.net/images/20180906/1536218474_5b90d56ae7854.png!small)

发送执行信息到目标C2：

![3.png](https://image.3001.net/images/20180906/1536218485_5b90d5759583b.png!small)

payload继续下载32ja.exe和we32.exe：

![4.png](https://image.3001.net/images/20180906/1536218495_5b90d57faac35.png!small)

32ja.exe除了会释放漏洞利用部分spoolsv.exe外，同时还会释放一个远控java.exe。

###  **2、远控模块分析（java.exe）**

该远控和之前友商的HSMiner报告中的远控一致，不再继续展开。

如远控中遍历的安全软件：

![5.png](https://image.3001.net/images/20180906/1536218505_5b90d58953de5.png!small)

###  **3、挖矿模块分析（we32.exe）**

We32.exe也是SFX自解压文件，解压后脚本执行cls.bat。

![6.png](https://image.3001.net/images/20180906/1536218514_5b90d592b81a6.png!small)

Cls.bat会将释放在同一文件夹下的的spoolsv.exe和windows.exe(矿机)启动，spoolsv.exe实际上为NSSM，NSSM是一个服务封装程序，它可以将普通exe程序封装成服务，使之像windows服务一样运行。脚本会利用spoolsv.exe（NSSM）安装windows.exe，让windows.exe以服务启动。启动后，脚本会继续关闭135，137，138，139，445等端口，避免被其他挖矿木马入侵占用。

![7.png](https://image.3001.net/images/20180906/1536218530_5b90d5a252db7.png!small)

矿机windows.exe为github上源码修改重新编译。由于使用代理矿池<https://udns.duckdns.org>，无法获取钱包地址。

![8.png](https://image.3001.net/images/20180906/1536218542_5b90d5ae90280.png!small)

代理矿池访问：

![9.png](https://image.3001.net/images/20180906/1536218554_5b90d5bac3190.png!small)

##  **三、关联分析**

### 1、代码

从代码来看，该木马跟HSMiner的代码高度相似，而样本的pdb信息也一致。

该木马payload下载代码：

![10.png](https://image.3001.net/images/20180906/1536218565_5b90d5c52104c.png!small)

友商报告中的payload下载代码：

![11.png](https://image.3001.net/images/20180906/1536218575_5b90d5cf57cd5.png!small)

pdb信息：

![12.png](https://image.3001.net/images/20180906/1536218589_5b90d5dd31aba.png!small)

其次，该木马都下载了和HSMiner一样的远控，且都是利用NSSM来安装服务。

最后，使用御见威胁情报中心查询，该C2下的样本均被打上了HSMiner的标签：

![13.png](https://image.3001.net/images/20180906/1536218600_5b90d5e8a413f.png!small)

### 2、和MsraMiner的关系

值得关注的是此次捕获样本WannaMiner变种的漏洞利用模块，该模块在漏洞攻击代码与MsraMiner对NSA组件利用代码高度相似，并且c2服务器复用了MsraMiner的恶意基础设施。

左边为MsraMiner传播模块利用代码，右边为spoolsv.exe传播利用代码：

![14.png](https://image.3001.net/images/20180906/1536218610_5b90d5f2dea43.png!small)

C2：d.drawal.tk，该域名同样出现在友商的MsraMiner的分析报告中。

![15.png](https://image.3001.net/images/20180906/1536218620_5b90d5fc5b307.png!small)

MsraMiner今年三月份同样被友商发现公布，MsraMiner之前曾运行在大型僵尸网络Mining Botnet上，通过NSA武器库和自带Web
Server进行传播，传播范围达到30000台主机。此次发现的变种在利用代码和基础设施上与MsraMiner高度一致。

### 3、结论

通过分析发现，MsraMiner和WannaMiner实际为统一家族的不同命名，而该家族和另一家族HSMiner背后的黑产团伙极有可能是统一团伙。

##  **四、安全建议**

1、手动安装“永恒之蓝”漏洞补丁。请访问以下页面：

<https://technet.microsoft.com/zh-cn/library/security/ms17-010.aspx>

其中WinXP，Windows Server 2003用户请访问：

<https://www.catalog.update.microsoft.com/Search.aspx?q=KB4012598>

2、企业用户建议全网安装御点终端安全管理系统

<https://s.tencent.com/product/yd/index.html>

御点终端安全管理系统具备终端杀毒统一管控、修复漏洞统一管控，以及策略管控等全方位的安全管理功能，可帮助企业管理者全面了解、管理企业内网安全状况、保护企业安全。

![16.jpg](https://image.3001.net/images/20180906/1536218632_5b90d608b027a.jpg!small)

3、个人用户推荐使用腾讯电脑管家，拦截此类病毒攻击。

##  **IOCs**

###  **url:**

d.drawal.tk

hxxp://dwn.rundll32.ml:88/32ja.exe

hxxp://dwn.rundll32.ml/we64.exe

hxxp://dwn.rundll32.ml:88/1433.exe

hxxp://dwn.rundll32.ml:88/w.exe

hxxp://dwn.rundll32.ml:88/xe64.exe

hxxp://dwn.rundll32.ml/w.exe

hxxp://dwn.rundll32.ml/dll.exe

hxxp://dwn.rundll32.ml:88/java.exe

hxxp://dwn.rundll32.ml:88/0812.exe

hxxps://udns.duckdns.org

###  **PDB:**

E:\有用的\Projects\Dllhijack\Dllhijack\Release\Dllhijack.pdb

###  **MD5:**

403ac5415063143617f8e594747518d5

03672abddf9e28c1af41ffbe67c875ae

b765383df88bbb0a08416344f332a159

c6384e0bd8be4083d2709ac5d7b712b9

ea4b4b671439697a57f46293fa66d8e2

70a4c47870a8988927342d31f32472e1

8cdbddc66dd270f01029f21716e547a6

67e7b9d9b39bca0e27087fcf9fe95535

##  **参考链接：**

<https://mp.weixin.qq.com/s/FEyaQ_AHn2TZPy-5FeMP7A>

 ***本文作者腾讯电脑管家，转载请注明来自FreeBuf.COM**

