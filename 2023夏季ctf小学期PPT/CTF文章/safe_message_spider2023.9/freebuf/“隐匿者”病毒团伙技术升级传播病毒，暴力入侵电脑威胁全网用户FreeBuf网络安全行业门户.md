***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

##  **一、概述**

**近期，火绒安全团队发现病毒团伙"隐匿者"进行了新的技术升级，正在传播病毒"Voluminer"。该病毒通过暴力破解的方式入侵电脑后，会利用用户电脑挖取门罗币，并且在电脑中留下后门，病毒团伙可通过远程控制随时修改恶意代码，下载其他更具威胁性的病毒模块。该病毒还会通过内核级对抗手段躲避安全软件查杀。**

病毒暴力破解用户数据库入侵电脑后，会篡改电脑系统中的主引导记录（MBR），一旦重启电脑，即可执行病毒，并在系统内核空间运行恶意代码，之后将恶意代码注入到系统进程中（winlogon或explorer进程），最终恶意代码会下载后门病毒到本地执行。

目前，后门病毒会下载执行挖矿相关病毒模块，挖取门罗币，但不排除病毒团伙将来会推送其他病毒模块，发动更具威胁性病毒攻击的可能性。

火绒安全团队曾曝光过该病毒制作组织"隐匿者"，通过对该其长期追踪，发现一直在活跃中，该团伙可能由中国人组成或参与，并完全以牟利为目的。是近年来互联网上最活跃、发起攻击次数最多、攻击范围最广的黑客团伙之一。

与此前相比，"隐匿者"本次传播的病毒样本所使用的技术更深入底层，隐蔽性更强，也更不易被用户察觉。使用内核级手段对自身病毒代码在磁盘中进行自我保护，与安全软件对抗，难以清除。并且加入远程控制功能，可以随时下载其他病毒模块。

### **相关文章：**

《彻底曝光黑客"隐匿者" 目前作恶最多的网络攻击团伙》

<https://www.huorong.cn/info/150097083373.html>

## **二、病毒来源**

通过对
"隐匿者"黑客组织的长期追踪，我们发现近期大范围传播的病毒家族Bootkit/Voluminer与该黑客组织可能存在直接关系。病毒运行后会篡改磁盘MBR代码，在电脑重启执行病毒MBR代码后，会在系统内核空间运行恶意代码，之后将恶意代码注入winlogon或explorer进程（依据操作系统版本），最终恶意代码会下载后门病毒到本地执行。后门病毒现阶段会下载执行挖矿相关病毒模块挖取门罗币，但我们不排除将来会推送其他病毒模块的可能性。

"隐匿者"通常会通过暴力破解连接用户计算机中的RPC服务、数据库服务器等，通过这些方式入侵用户电脑进而执行其他恶意代码，具体攻击方式与火绒在2017年7月发布的《彻底曝光黑客"隐匿者"
目前作恶最多的网络攻击团伙》报告中所介绍的攻击方式完全相同。火绒所截获到与本次样本相关的攻击行为，如下图所示：

![161223fqxuuuq8wbueuqso.jpg](https://image.3001.net/2018/09/15bfa2d057557d1e7ef5cfaab9ebcb242.jpg)

攻击行为

火绒在前期报告中，在列举病毒攻击行为时所使用的病毒行为日志原图，如下图所示：

![161240n18t3zlqpfdplb1t.jpg](https://image.3001.net/2018/09/f7b224a590e3e465826eda1dbd7c541b2.jpg)

前期报告原图

在火绒前期报告中所提到的黑客所常用的FTP服务器用户名及密码分别为test和1433，与本次所截获攻击事件中黑客所使用的FTP服务器（ftp.ftp0118.info）相关信息相同。在"隐匿者"使用的FTP服务器地址中，我们发现down.mysking.info域名所指向的FTP服务器依然可以正常访问，服务器中存放的病毒文件虽然与本次黑客使用的FTP服务器中不同，但是文件名却极其相似。FTP服务器存放文件情况对比，如下图所示：

![161253mic33cqw0s30maqi.jpg](https://image.3001.net/2018/09/02cb0e8884758f22371736e172b3c1842.jpg)

FTP文件情况对比图

除此之外，在本次截获的部分病毒样本语言信息为简体中文，与"隐匿者"报告中相同。进而我们可以初步判断，本次攻击事件可能与"隐匿者"黑客组织存在直接关系。本次截获样本（SHA256：46527e651ae934d84355adb0a868c5edda4fd1178c5201b078dbf21612e6bc78）的语言信息，如下图所示：

![161309k3njnnjp3jis2adl.jpg](https://image.3001.net/2018/09/52d5bac71ab222b831c3b895ec54796d2.jpg)

病毒样本语言信息

##  **三、样本分析**

与隐匿者早期样本相比，近期在野进行传播的隐匿者样本病毒行为已经越来越复杂，所使用的攻击技术也更为底层。例如本文所提到的病毒样本就会感染MBR，并对被篡改后的MBR代码进行保护，从而提高了对该病毒进行查杀的复杂度。

### Bootkit/Voluminer

Bootkit/Voluminer病毒运行后会直接写入病毒MBR代码，原始的MBR数据被病毒备份在磁盘的第二个扇区中。其余病毒代码起始位置为第三个扇区，其余病毒代码（除MBR代码外）共占用54个扇区，由于内核平台版本不同（x86/x64），报告中分析内容以病毒在Windows
7（x64）系统中的感染情况为例。被感染后的MBR代码数据，如下图所示：  

![161327j8xf88qv25o2qom2.jpg](https://image.3001.net/2018/09/10f7e58e0e0b955969fafa2edf03547e2.jpg)

被感染后的MBR代码数据

病毒MBR代码，如下图所示：  

![161340cy850npiqzovz04m.jpg](https://image.3001.net/2018/09/3c5131a71f83eb9c5c06485e48f3414c2.jpg)

病毒MBR代码

病毒MBR代码运行后，会将第三个扇区后的恶意代码拷贝到0x8f000地址进行执行，恶意代码会在hook INT
15中断后，重新调用原始MBR执行正常的引导启动逻辑。当INT 15
中断被调用时，病毒代码会通过匹配硬编码的方式搜索BootMgr（startup.com）代码进行hook，被hook后执行的恶意代码代码会最终hook
Bootmgr.exe
中的Archx86TransferTo32BitApplicationAsm和Archx86TransferTo64BitApplicationAsm。Hook
INT15后执行的病毒逻辑，如下图所示：  

![161356mlvlhi92bmzdmv21.jpg](https://image.3001.net/2018/09/1b50b8c61b8dc37fa3a59b2be9d224fd2.jpg)

Hook INT 15执行的病毒逻辑

BootMgr（startup.com部分）被hook后，在BootMgr.exe 加载时会继续执行下一步hook操作。Hook
BootMgr.exe相关代码，如下图所示：  

![161410vuitdiq7ua1ekiqm.jpg](https://image.3001.net/2018/09/696cd8b70086b8dd247935d3d345cc1e2.jpg)

Hook BootMgr.exe相关代码

BootMgr.exe被hook后，Archx86TransferTo32BitApplicationAsm和Archx86TransferTo64BitApplicationAsm函数内代码情况，如下图所示：  

![161442gpcdzq3el6r1973r.jpg](https://image.3001.net/2018/09/755b8df37e155d3c2baf1a65ee9025852.jpg)

被hook后的函数入口

Archx86TransferTo32BitApplicationAsm和Archx86TransferTo64BitApplicationAsm函数被hook后，被调用的病毒代码会在BootMgr.exe加载Winload.exe时hook
OslArchTransferToKernel，为hook ntoskrnl.exe做准备。相关代码，如下图所示：  

![161459uosj1df7lv7q7fqy.jpg](https://image.3001.net/2018/09/c80d802f6f1af60fb01154ba874342d12.jpg)

Hook OslArchTransferToKernel相关代码

被hook后的OslArchTransferToKernel函数内代码，如下图所示：  

![161633q7y25ay1muyxx525.jpg](https://image.3001.net/2018/09/1675b23d2230e86af80fcd64eb09a68c2.jpg)

被hook后的OslArchTransferToKernel函数代码

OslArchTransferToKernel被hook后执行的恶意代码会hook
ZwCreateSection，并破坏ntoskrnl.exe中PatchGuard相关逻辑。相关代码，如下图所示：  

![161644epxdskfv0vd9gkgp.jpg](https://image.3001.net/2018/09/99441fbf54acc85cac8648b49a17822a2.jpg)

Hook OslArchTransferToKernel函数后执行的恶意代码入口

首先，恶意代码会先通过函数名哈希值获取ZwCreateSection函数地址，再获取最终需要在内核态执行的恶意代码入口（malware_krnl_main_entry），然后获取hook
ZwCreateSection后被调用的处理函数入口和相关信息（包括ntoskrnl基址、malware_krnl_main_entry函数入口、ZwCreateSection函数入口地址、被patch掉的原始ZwCreateSection代码内容），最后修改ZwCreateSection函数入口代码，并将ntoskrnl中PatchGuard相关代码通过修改硬编码禁用掉。相关代码，如下图所示：  

![161659cz1t6bvbk4mk8m0i.jpg](https://image.3001.net/2018/09/63dda28c89d521550f9c042db9db20222.jpg)

Hook ZwCreateSection和破坏PatchGuard的恶意代码

被hook后的ZwCreateSection函数入口代码，如下图所示：  

![161711a77ijgra6qmn8x7c.jpg](https://image.3001.net/2018/09/f953c92f00540cf21816fa10c931c1f72.jpg)

被hook后的ZwCreateSection函数入口代码

ZwCreateSection被hook后调用的恶意代码，首先会修复ZwCreateSection被patch掉的代码内容，之后再将后续需要执行恶意代码（代码地址：0x946E6）通过MmMapIoSpace映射到内核态地址空间进行执行。相关代码，如下图所示：  

![161725olxh6u8x9g5har9c.jpg](https://image.3001.net/2018/09/03d1c59f36eacd99d02fbf76db5fa72f2.jpg)

ZwCreateSection被hook后调用的恶意代码

上述代码被调用后，会执行内核态恶意代码malware_krnl_main_entry，该函数内代码首先会根据函数名哈希获取所需的API地址。相关代码，如下图所示：  

![161739wtzt867keuzt2x8i.jpg](https://image.3001.net/2018/09/cd52047660906b09aa3dcb1a980b70892.jpg)

malware_krnl_main_entry代码

内核态主要恶意代码逻辑执行后，首先会创建线程通知回调，在回调中检测csrss.exe进程是否启动，在该进程启动后再继续执行后续恶意代码逻辑。相关代码，如下图所示：  

![161754x4ca9xdzswhyfiyh.jpg](https://image.3001.net/2018/09/dcd72cd272eefd84bef518fe8d23c5172.jpg)

线程通知回调中恶意代码逻辑

如上图所示，在检测到csrss.exe后，首先会尝试感染MBR并将存放恶意代码的扇区保护起来。通过过滤IRP的方式，在用户访问病毒引导代码所在扇区时，返回正常引导代码数据，提高病毒的隐蔽性。感染MBR相关代码，如下图所示：  

![161809j9fq5zrfxf3re5xu.jpg](https://image.3001.net/2018/09/d9f9cf5f140dd59a8c8172fe0cfabdbe2.jpg)

感染MBR并将原始MBR数据拷贝到第二扇区

恶意MBR及相关数据保护逻辑会保护磁盘前0x3E个扇区。相关代码，如下图所示：  

![161821xt9zjkd9841v8xsx.jpg](https://image.3001.net/2018/09/cbae69de760a722e25885a9be1cfb39f2.jpg)

恶意MBR及相关数据保护相关代码

之后在内核线程（malware_behav_entry）中会根据不同的操作系统版本对winlogon.exe或explorer.exe进行APC注入。WinXP注入explorer.exe，其他操作系统注入winlogon.exe，如果是Win10系统会再次尝试hook
Storport驱动对象的IRP回调。相关代码，如下图所示：  

![161836b3oipyvnp2pnyp43.jpg](https://image.3001.net/2018/09/ca774539e34dfcb5032de1588791aeee2.jpg)

APC注入相关代码

被注入的病毒代码执行恶意逻辑主要参照从C&C服务器请求到的配置文件，该文件释放到本地后路径为：%SystemRoot%\Temp\ntuser.dat。该文件被异或0x95加密过，在使用该文件时会对文件进行解密。解密后的ntuser.dat配置内容，如下图所示：  

![161848qikq5bf44qiqs46y.jpg](https://image.3001.net/2018/09/896b6beabb73946e71c39dda4cd789232.jpg)

ntuser.dat配置内容

如上图，配置文件总体分为两个部分：main和update。main部分中的所有ip和网址用来下载后门病毒相关配置，update部分中的ip和网址用来更新ntuser.dat配置数据，请求到的相关配置信息至今依然在持续更新。下载后门病毒配置信息cloud.txt的代码逻辑，如下图所示：  

![161901a8jshgxjgjjan5jw.jpg](https://image.3001.net/2018/09/65a1c317a73a1a9d1028a8af2227902d2.jpg)

下载后门病毒配置信息

请求到的配置信息中，除后门病毒下载地址（exe键名对应数据）外，还有名为url的配置项，该功能开启后会hook
CreateProcessW劫持浏览器启动参数，但现阶段该功能尚未被开启。配置信息，如下图所示：  

![161915mjj6qsajjcj5tacv.jpg](https://image.3001.net/2018/09/ef88328e06fa3fe9b0ae6fcf6c383e9d2.jpg)

配置信息

恶意代码会通过上图中的下载地址，将后门病毒下载到%SystemRoot%\Temp\conhost.exe目录进行执行。下载执行远程后门病毒相关逻辑，如下图所示：  

![161929wm6lpz1gb88g86eb.jpg](https://image.3001.net/2018/09/1874867367e4c841dbd1f66498cfea222.jpg)

下载执行后门病毒Backdoor/Voluminer

该病毒运行后，首先会释放存放有C&C服务器列表的文件（xp.dat）至C:\Program Files\Common
Files目录中，之后向C&C服务器列表中的服务器地址请求xpxmr.dat文件，用于更新C&C服务器列表。请求到的xpxmr.dat文件数据使用RSA算法进行过加密，进行解密后会重新写入到xpxmr.dat文件中，该文件为明文存放。相关代码及数据，如下图所示：

![161944tjy505mv9k6v05v8.jpg](https://image.3001.net/2018/09/25b01ff2d2d9dc4dc0baf9539a20edee2.jpg)

更新C&C服务器列表

病毒在运行中会向C&C服务器请求获取最新病毒版本号，当检测到存在新版本时，则会通过C&C服务器下载执行最新版本的病毒程序。当后门病毒发现当前系统为64位系统时，还会向C&C服务器请求64位版本的后门病毒到本地进行执行。相关代码，如下图所示：  

![161956wh66qfqw66e6jw02.jpg](https://image.3001.net/2018/09/a2f0987f0b8296defdb34be8d208a2b52.jpg)

请求64位版本病毒

随后，病毒会使用地址列表中的C&C服务器地址下载挖矿所需的病毒组件，暂时我们发现会被病毒下载至本地病毒仅具有挖矿功能，但我们不排除其将来会下载其他病毒模块的可能性。病毒在下载文件后，会对病毒组件进行md5校验，病毒组件的md5值会参考C&C服务器中的md5.txt文件内容。相关代码，如下图所示：  

![162007h393zo3rirsx3f3x.jpg](https://image.3001.net/2018/09/1d24bafb27b87e7d2470d8fb69d87db52.jpg)

获取远程恶意代码模块

在病毒组件下载完成后，病毒会将挖矿相关的模块和配置文件释放到%windir%\debug目录中，随后开始挖矿逻辑。病毒释放挖矿配置相关代码，如下图所示：  

![162021v8jwso23jowwvjo6.jpg](https://image.3001.net/2018/09/1dbc96506e206472e760db2ad154d13d2.jpg)

释放挖矿配置相关代码

与前段时间友商报告中所描述的该后门病毒相比，病毒的恶意行为已经有了明显变化。在早期版本中，被配发到用户本地的后门病毒会被注册为系统服务（服务名为：Windows
Audio
Control），并在运行后会显示控制台窗口并且在病毒运行时会在窗口中显示运行日志，最终会下载执行挖矿病毒，中毒现象十分明显。而在现阶段版本中，被下发到用户本地的后门病毒隐蔽性已经有所提高，在病毒执行过程中用户很难有所察觉。病毒挖取门罗币时使用的配置信息片段，如下图所示：  

![162034ytwlslf5lf77s7xx.jpg](https://image.3001.net/2018/09/9979f7ff6a7f1a7b2184f417375590b52.jpg)

配置信息片段

通过上图中的门罗币钱包地址查询，我们发现该账户自2017年6月12日起开始有门罗币进账信息，至今已经共获取门罗币约2867个，合人民币约200余万元。病毒使用的门罗币钱包信息，如下图所示：  

![162051kmzgw11xm81d5451.jpg](https://image.3001.net/2018/09/ff33dbcf11f1c12f2e41fd74f412eb3c2.jpg)

门罗币钱包信息

##  **四、同源性分析**

除行为特征外，我们通过对比样本关键数据，还发现了更多的同源性特征。比如在获取挖矿钱包信息时，文中样本与2017年隐匿者相关样本（SHA256：f37a0d5f11078ef296a7c032b787f8fa485d73b0115cbd24d62cdf2c1a810625）均会向C&C服务器请求名为xmrok.txt的加密数据文件，且该文件均为AES算法加密。相关数据，如下图所示：  

![162103zvzr4uiubgnxvvqb.jpg](https://image.3001.net/2018/09/b572c4b9b72b6aa65c87fe7debc947912.jpg)

样本关键逻辑对比

除此之外，文中所提到的样本与2017年样本相同，挖矿功能均是使用xmr-stak开源代码。相关数据，如下图所示：  

![162120qqtzbkb40k02cplc.jpg](https://image.3001.net/2018/09/eff64d4e1fdeaa7389cfa9c4fedb47312.jpg)

挖矿相关数据对比

通过对比分析，我们发现与2017年样本相比，虽然最终恶意行为完全相同，但新样本在恶意逻辑中加入了云控功能，从而可以使样本可以根据黑客在C&C服务器中提供的恶意代码和相关配置信息对病毒进行调整。除此之外，文中样本较2017年隐匿者样本还加强了对样本自身代码的保护，在后门病毒及其派发模块中大量使用了VMProtect保护壳，加大了安全分析人员的分析成本。壳信息，如下图所示：  

![162130xh5zh5d1kkdkpavc.jpg](https://image.3001.net/2018/09/92891eff514500d27bbae32fa66bb27b2.jpg)

###  壳信息

隐匿者黑客组织最早可以追溯至2014年（时间依据请见前期报告），其攻击手法多样，且至今依然在不断进行改进和增强，已经成为对互联网环境威胁最大黑客组织之一。火绒会继续对该黑客组织进行追踪，不断收集和防御与该组织相关的所有安全威胁。

## **五、附录**

文中涉及样本 **SHA256：**  

![162150cnngdzgk893k8def.jpg](https://image.3001.net/2018/09/cde367e2b1507481ef58f38f24b3ccc22.jpg)

**IOC:  
**

![162202s0ssoqv0ybr706sz.jpg](https://image.3001.net/2018/09/10dedb8ca7e0a45c96cc80244bfa81972.jpg)

***本文作者火绒安全，转载请注明来自FreeBuf.COM**

