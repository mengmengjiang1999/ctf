**Check
Point发现了针对蒙古公共部门的网络攻击活动，该组织利用了冠状病毒恐慌情绪向目标发送恶意软件。研究发现其与可与在2016年进行的其他网络活动联系起来。多年来，这些行动的目标是多个国家/地区的不同部门，例如乌克兰，俄罗斯，
和白俄罗斯。**

在本报告中将对整个活动中使用的TTP，基础设施以及发现的新工具进行全面分析。  

## 诱饵文件

确定了发送给蒙古公共部门的两份可疑文件， 这些文件用蒙古文写成，其中之一来自蒙古外交部：

![1.png](https://image.3001.net/images/20200315/1584286867_5e6e4c9330ccc.png!small)![2.png](https://image.3001.net/images/20200315/1584286873_5e6e4c990363e.png!small)  

这些文件是使用名为RoyalRoad（aka 8.t）的工具进行处理。该工具使攻击者可以创建带有嵌入式对象的自定义文档，从而利用Word的Equation
Editor漏洞。

## 感染链

受害者打开特制的文档并触发Word漏洞后，将名为intel.wll的文件放入Word启动文件夹：％APPDATA％\Microsoft\Word\STARTUP。
每次启动Word时，Word Startup文件夹中所有带有WLL扩展名的DLL文件也将启动，从而触发感染链：

![1.png](https://image.3001.net/images/20200315/1584287097_5e6e4d79b7fcc.png!small)

该技术手段可以进行持久控制，还可以防止其在沙箱中运行时被分析，因为要完全执行该恶意软件，必须重新启动Word。恶意intel.wll
DLL加载后，会继续从服务器：95.179.242 [.]
6下载并解密下一阶段。下一阶段也是DLL文件，它是恶意软件框架的主要加载程序。它使用Rundll32执行，并另一台C＆C服务器（95.179.242 [.]
27）通信接收其他功能。

攻击者每天仅在线几个小时操作C＆C服务器，使得分析和访问感染链的高级部分变得更加困难。  

在感染链的最后阶段，接收到命令后恶意加载程序会以DLL的形式下载并解密RAT模块，将其加载到内存中。被入侵目标除了收到的有效载荷外还可能存在其他模块。RAT模块是自定义恶意软件，它还包含一些通用的核心功能，如下所示：

> 截屏
>
> 列出文件和目录
>
> 创建和删除目录
>
> 移动和删除文件
>
> 下载
>
> 执行新进程
>
> 获取所有服务的列表

## 技术分析

在研究之初，攻击者的一台服务器（用于下一阶段的恶意软件）在限定时间内启用了目录列表。
这样一来就可以下载所有托管文件，并深入了解操作时间表和攻击者的工作时间。

![1.png](https://image.3001.net/images/20200315/1584287661_5e6e4fad1edf7.png!small)

服务器上的所有文件都已加密，通过使用感染链中相同的加密方案，能够解密服务器上存储的大多数文件。

![1.png](https://image.3001.net/images/20200315/1584287715_5e6e4fe395687.png!small)能够解密的十二个文件可以分为四个主要的恶意软件家族。
它们的嵌入式内部名称和核心功能如下所述：  

> 1、http_dll.dll（Intel.wll）：第一阶段加载程序， 解密C＆C地址，下载并解密下一阶段的DLL，然后通过Rundll32执行它。  
>
>
> 2、ppdown.dll：下载解密服务器上存储的.rar文件。
> 从服务器读取access.txt文件，对其进行解密，然后将结果分为3部分：下一个要下载的阶段的名称；调用下一个导出功能；下一阶段的解密密钥。
>
> 3、Rundll32Templete.dll：用作下一阶段有效负载的加载和解密。有效负载在.sect节中加密。  
>
>
> 4、Minisdllpub.dll：第二阶段的加载程序，下面会进行详细描述。 加载其他DLL插件。  
>

获得其他解密文件的访问权限后可以寻找类似的样本。  

通过内部名称（http_dll，Rundll32Templete和minisdllpub），导出函数（Engdic，WSSet和MSCheck）和代码相似性（解密方法，通信模式等）搜索相似文件，能够找到与攻击者有关的更多示例：  

![1.png](https://image.3001.net/images/20200316/1584288063_5e6e513f10181.png!small)

样本（92de0a807cfb1a332aa0d886a6981e7dee16d621）找到了一篇类似初始感染链的[文章](https://bbs.pediy.com/thread-256810.htm)，其目标为乌克兰。另一个样本（9ef97f90dcdfe123ccb7d9b45e6fa9eceb2446f0）针对俄罗斯联邦，发生在2018年末。

## 基础设施

分析新发现的样本后，发现了攻击者使用的大部分基础设施以及一个常见的TTP：所有C＆C服务器都托管在Vultr服务器上，域则通过GoDaddy服务商注册。

![1.png](https://image.3001.net/images/20200316/1584288259_5e6e520304a82.png!small)  

在分析时发现，在某个时候C＆C服务器95.179.242[.]6停止提供服务。几天后，dw.adyboh[.]com开始提供目录服务：

表明攻击者在其中一台有效负载交付服务器处于活动状态时正在启用目录列表。![1.png](https://image.3001.net/images/20200316/1584288362_5e6e526a3aebb.png!small)

## 溯源分析

从恶意文档的角度来看，intel.wll的命名方案（RoyalRoad的7.x版本已将其删除）不足以对其做出明确的归属，因为许多攻击者使用相同的名称。另一方面，从有效载荷的角度来看，发现了其他相关样本可将其归属到已知的组织。在上面提到的NWCWorkstation.dll中，发现字符串：“
V09SS010”，这与Palo Alto
Networks在2017年发表的“[威胁行动者是白俄罗斯的目标政府](https://unit42.paloaltonetworks.com/unit42-threat-actors-target-government-belarus-using-cmstar-trojan/)”相似，其中描述了利用名为BYEBY的RAT攻击。还与一篇2016年的
[文章](https://unit42.paloaltonetworks.com/digital-quartermaster-scenario-demonstrated-in-attacks-against-the-mongolian-government/)相关，该文章指出在针对蒙古政府的攻击中使用了相同的工具。  

通过将其与2017年攻击中的IOC进行比较，发现了一些相似之处：  

### 基础架构相似

2017年的服务器与调查中发现的样本示例部署在相同的基础架构上，并利用Vultr和GoDaddy服务。  

### 代码相似

分析（bf9ef96b9dc8bdbc6996491d8167a8e1e63283fe）文件时，它解密并加载了一个名为wincore.dll的DLL。将其与2017年的BYEBY样本进行关联分析：

字符串相似性：

![image.png](https://image.3001.net/images/20200316/1584322535_5e6ed7e7d5ea0.png!small)功能相似性：

![image.png](https://image.3001.net/images/20200316/1584322570_5e6ed80a4398a.png!small)全局调用图和X-Ref图相似：即使两个示例中都存在混淆，仍然能够验证它们具有相似调用图和X-Ref图，这意味着可执行文件的核心功能是相同的。  

## 有效负载分析

攻击链中第二阶段有效载荷是minisdllpub.dll的加密DLL文件。从95.179.242 [.]
6下载的DLL是其他负载的下载器。Minisdllpub.dll首先创建名称为Afx：DV3ControlHost的互斥锁。然后定义大小为0x5f8的结构来存储系统和环境信息，例如正在运行的计算机的名称，IP地址，用户名和OS版本。接下来，创建一个大小为0x3FC的结构，存储指向加载的DLL和API函数以及C&C
IP地址（95.179.242 [.] 27）和端口（443）的指针。

设置好这些结构后创建一个新线程，获取API函数列表，动态加载它们。每个列表都由一个库的名称组成，然后从库中加载的一系列API函数。然后将这些函数的指针添加到先前的结构中，在需要时动态调用它们。  

![image.png](https://image.3001.net/images/20200316/1584325963_5e6ee54b0f704.png!small)

第二阶段有效负载建立HTTP或HTTPS通信，在新线程中与其远程控制进行通信。 服务器回复后，会使用密钥0x51将XOR编码的DLL发送给恶意软件。
然后，Minisdllpub.dll解码并将新的PE动态加载到内存中。加载后，它将搜索名称为e的导出函数。
恶意软件会继续监听来自服务器的命令，在收到命令后将其传递给新加载的有效负载的“e”功能。第二阶段充当了C＆C和最终有效载荷的中间人。

![image.png](https://image.3001.net/images/20200316/1584326095_5e6ee5cf037e8.png!small)至此已在受害者计算机上加载了模块，Minisdllpub.dll是最初由http_dll.dll（intel.wll）使用Rundll32加载的，RAT不直接从C＆C接收命令而是通过中介Minisdllpub.dll接收控制命令。  

![image.png](https://image.3001.net/images/20200316/1584326212_5e6ee644cc9a6.png!small)

除了要执行的命令外，Minisdllpub.dll还将结构体传递给最终的有效负载，RAT使用这些存储结构调用API函数并将数据传递到C＆C服务器，重复使用先前模块中加载的功能指针的方法使得在没有上一阶段的情况下很难进行RAT分析。最终有效负载支持功能及其接收和发送的相应命令如下：

![image.png](https://image.3001.net/images/20200316/1584326339_5e6ee6c3be453.png!small)

## 总结

这项特定的网络活动利用了COVID-19大流行来诱使受害者触发感染链。攻击者利用带有宏和较旧的RTF漏洞文档，并更新了其工具集，在野外观察到“
RoyalRoad” RTF漏洞生成器的最新版本。这个组织的真正意图仍然不清楚，但是显然他们会一直活跃下去，更新工具，并尽一切努力攻击新的受害者。

## 附录

### Files on the server  

###
![image.png](https://image.3001.net/images/20200316/1584326552_5e6ee798334d2.png!small)IOCs  

Servers：

> 95.179.242[.]6  
>
>
> 95.179.242[.]27
>
> 199.247.25[.]102
>
> 95.179.210[.]61
>
> 95.179.156[.]97
>
> dw.adyboh[.]com
>
> wy.adyboh[.]com
>
> feb.kkooppt[.]com
>
> compdate.my03[.]com
>
> jocoly.esvnpe[.]com
>
> bmy.hqoohoa[.]com
>
> bur.vueleslie[.]com
>
> wind.windmilldrops[.]com

RTFs:

> 234a10e432e0939820b2f40bf612eda9229db720
>
> 751155c42e01837f0b17e3b8615be2a9189c997a
>
> ae042ec91ac661fdc0230bdddaafdc386fb442a3
>
> d7f69f7bd7fc96d842fcac054e8768fd1ecaa88a
>
> dba2fa756263549948fac6935911c3e0d4d1fa1f

DLLs:

> 0e0b006e85e905555c90dfc0c00b306bca062e7b
>
> dde7dd81eb9527b7ef99ebeefa821b11581b98e0
>
> fc9c38718e4d2c75a8ba894352fa2b3c9348c3d7
>
> 601a08e77ccb83ffcd4a3914286bb00e9b192cd6
>
> 27a029c864bb39910304d7ff2ca1396f22aa32a2
>
> 8b121bc5bd9382dfdf1431987a5131576321aefb
>
> bf9ef96b9dc8bdbc6996491d8167a8e1e63283fe
>
> fcf75e7cad45099bf977fe719a8a5fc245bd66b8
>
> 0bedd80bf62417760d25ce87dea0ce9a084c163c
>
> 5eee7a65ae5b5171bf29c329683aacc7eb99ee0c
>
> 3900054580bd4155b4b72ccf7144c6188987cd31
>
> e7826f5d9a9b08e758224ef34e2212d7a8f1b728
>
> a93ae61ce57db88be52593fc3f1565a442c34679
>
> 5ff9ecc1184c9952a16b9941b311d1a038fcab56
>
> 36e302e6751cc1a141d3a243ca19ec74bec9226a
>
> 080baf77c96ee71131b8ce4b057c126686c0c696
>
> c945c9f4a56fd1057cac66fbc8b3e021974b1ec6
>
> 5560644578a6bcf1ba79f380ca8bdb2f9a4b40b7
>
> 207477076d069999533e0150be06a20ba74d5378
>
> b942e1d1a0b5f0e66da3aa9bbd0fb46b8e16d71d
>
> 9ef97f90dcdfe123ccb7d9b45e6fa9eceb2446f0
>
> cf5fb4017483cdf1d5eb659ebc9cd7d19588d935
>
> 92de0a807cfb1a332aa0d886a6981e7dee16d621
>
> cde40c325fcf179242831a145fd918ca7288d9dc
>
> 2426f9db2d962a444391aa3ddf75882faad0b67c
>
> 9eda00aae384b2f9509fa48945ae820903912a90
>
> 2e50c075343ab20228a8c0c094722bbff71c4a2a
>
> 2f80f51188dc9aea697868864d88925d64c26abc

RAT:

> 238a1d2be44b684f5fe848081ba4c3e6ff821917

 ***参考来源：[checkpoint](https://research.checkpoint.com/2020/vicious-panda-the-covid-campaign/)，由Kriston编译，转载请注明来自FreeBuf.COM**

