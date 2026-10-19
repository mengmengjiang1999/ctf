**近日，多个企业反馈大量主机和服务存在卡顿和蓝屏现象，深信服安全团队研究发现，该企业用户中的是最新型的WannaMine变种，之前有WannaMine1.0、WannaMine2.0、WannaMine3.0版本。**

此病毒变种是基于WannaMine3.0改造，又加入了一些新的免杀技术，传播机制与WannaCry勒索病毒一致（可在局域网内，通过SMB快速横向扩散），故深信服安全团队将其命名WannaMine4.0。该变种是国内外发现的首例新型WannaMine4.0变种，国内安全厂商还没有相关报道。

深信服安全团队对捕获的样本进行分析，发现其接入站点已变更为totonm.com。经查验，这是一个 **2019年3月17日刚申请注册的域名** 。

![WannaMine升级到V4.0版本，警惕中招](https://image.3001.net/images/20190321/1553151427_5c9335c377514.png!small)

病毒编译时间为 **2019** **年3** **月18** **日，也就是说17** **号注册域名，18**
**号编译完成，就开始进行传播了，深信服在20** **号，国内首家发现此新型变种** 。

![WannaMine升级到V4.0版本，警惕中招](https://image.3001.net/images/20190321/1553151439_5c9335cfaa5f4.png!small)

近日，有多家医院已先后感染该木马变种，传播速度惊人，预计未来感染面也会跟原始变种WannaMine1.0、WannaMine2.0、WannaMine3.0一样大。

##  **一、攻击场景**

此次攻击，沿用了WannaMine3.0的精心设计，涉及的病毒模块多，感染面广，关系复杂。

![WannaMine升级到V4.0版本，警惕中招](https://image.3001.net/images/20190321/1553151550_5c93363eeb54a.png!small)

有所不同的是，原始“压缩包”已经变为 **rdpkax.xsl**
，其含有所需要的所有攻击组件。此变种与之前3.0版本一样，同样做了免杀，rdpkax.xsl是一个特殊的数据包，需要病毒自己解密分离出各个组件，其组件包含“永恒之蓝”漏洞攻击工具集（svchost.exe、spoolsv.exe、x86.dll/x64.dll等）。

本文所述病毒文件，释放在下列文件目录中

> C:\Windows\System32\rdpkax.xsl
>
> C:\Windows\System32\dllhostex.exe
>
> C:\Windows\System32\ApplicationNetBIOSClient.dll
>
> C:\Windows\SysWOW64\ApplicationNetBIOSClient.dll
>
> C:\Windows\SysWOW64\dllhostex.exe
>
> C:\Windows\NetworkDistribution

![WannaMine升级到V4.0版本，警惕中招](https://image.3001.net/images/20190321/1553151584_5c933660bc6eb.png!small)

攻击顺序：

1.有一个主服务 **ApplicationNetBIOSClient** ,对应动态库为 **ApplicationNetBIOSClient.dll**
（由系统进程svchost.exe加载），每次都能开机启动，启动后加载 **spoolsv.exe** 。

2. **spoolsv.exe** 对局域网进行445端口扫描，确定可攻击的内网主机。同时启动漏洞攻击程序 **svchost.exe** 和 **spoolsv.exe** **（另外一个病毒文件）** 。

3. **svchost.exe** 执行“永恒之蓝”漏洞溢出攻击（目的IP由第2步确认），成功后 **spoolsv.exe** (NSA黑客工具包DoublePulsar后门）安装后门，加载payload（ **x86.dll/x64.dll** ）。

4.payload（ **x86.dll/x64.dll** ）执行后，负责将 **rdpkax.xsl** 从本地复制到目的IP主机，注册
**ApplicationNetBIOSClient** 主服务，再解压该文件，启动 **spoolsv**
执行攻击（每感染一台，都重复步骤1、2、3、4）。

##  **二、** **组合变形与免杀**

WannaMine4.0与早期版本相比，最强特征是加了组合变形与免杀。

生成不同的主服务模块DLL和数据包，如下所示：

![WannaMine升级到V4.0版本，警惕中招](https://image.3001.net/images/20190321/1553151639_5c9336974a57d.png!small)

生成的主服务模块DLL，随机组合下列字符串，如下所示：

![WannaMine升级到V4.0版本，警惕中招](https://image.3001.net/images/20190321/1553151650_5c9336a2e2d57.png!small)

生成的主服务模块，由上面三个字符串列表，组成随机生成、如下所示：

字符串列表1，如下所示：

> Windows、Microsoft、Network、Remote、Function、Secure、Application

字符串列表2，如下所示：

> Update、Time、NetBIOS、RPC、Protocol、SSDP、UPnP

字符串列表3，如下所示：

> Service、Host、Client、Event、Manager、Helper、System

 **即字符串 1+** **字符串 2+** **字符串 3** **，例如 ApplicationNetBIOSClient**
**，就是以上三段拼凑而成。由于关系复杂，上午讲到的主服务 ApplicationNetBIOSClient** **和对应的动态库
ApplicationNetBIOSClient.dll** **本身都是会变化的，即每次运行都按照上面规律进行动态组合。**

生成的加密数据包名后缀列表，如下所示：

> xml、log、dat、xsl、ini、tlb、msc

同时，由于病毒母体在生成主服务模块DLL时，会将随机组合的字符串硬编码到文件中，导致每次释放的文件哈希值都可能不一样。

![WannaMine升级到V4.0版本，警惕中招](https://image.3001.net/images/20190321/1553151683_5c9336c387342.jpg!small)

##  **三、挖矿**

WannaMine4.0沿用早期WannaMine家族的套路，同样是瞄准了大规模的集体挖矿（利用了“永恒之蓝”漏洞的便利，迅速使之在局域网内迅猛传播），挖矿主体病毒文件为dllhostex.exe。
**由于利用了“永恒之蓝”漏洞攻击，所以除了中招主机业务卡顿之外，还有可能造成蓝屏，极大威胁客户业务安全。**

挖矿程序行为，如下所示：

![WannaMine升级到V4.0版本，警惕中招](https://image.3001.net/images/20190321/1553151701_5c9336d577953.png!small)

获取到相应的数据包，如下所示：

![WannaMine升级到V4.0版本，警惕中招](https://image.3001.net/images/20190321/1553151707_5c9336db85124.png!small)

##  **四、** **解决方案**

 **病毒检测查杀**

1、深信服为广大用户免费提供查杀工具，可下载如下工具，进行检测查杀。

64位系统下载链接：

<http://edr.sangfor.com.cn/tool/SfabAntiBot_X64.7z>

32位系统下载链接：

<http://edr.sangfor.com.cn/tool/SfabAntiBot_X86.7z>

![WannaMine升级到V4.0版本，警惕中招](https://image.3001.net/images/20190321/1553151717_5c9336e5a3d67.png!small)

2、深信服EDR产品及防火墙等安全产品均具备病毒检测能力，部署相关产品用户可进行病毒检测：

![WannaMine升级到V4.0版本，警惕中招](https://image.3001.net/images/20190321/1553151726_5c9336ee3573b.png!small)

##  **病毒防御**

> 1、及时给电脑打补丁，修复漏洞，打上“永恒之蓝”漏洞补丁，请到微软官网，下载对应的漏洞补丁
>
> （<https://technet.microsoft.com/zh-cn/library/security/ms17-010.aspx>）。
>
> 2、对重要的数据文件定期进行非本地备份。
>
> 3、不要点击来源不明的邮件附件，不从不明网站下载软件。
>
> 4、尽量关闭不必要的文件共享权限，譬如445等网络共享端口。

最后，建议企业对全网进行一次安全检查和杀毒扫描，加强防护工作。

 ***本文作者：千里目安全实验室，转载请注明来自FreeBuf.COM。**

