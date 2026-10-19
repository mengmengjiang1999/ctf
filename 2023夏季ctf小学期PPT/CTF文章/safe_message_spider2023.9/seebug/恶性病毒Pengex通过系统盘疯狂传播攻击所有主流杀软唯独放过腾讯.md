作者：[火绒安全实验室](http://bbs.huorong.cn/forum.php?mod=viewthread&tid=23107#lastpost)

#### 一、综述

近日，火绒安全实验室截获到一种内核级后门病毒，并将其命名为 "Pengex" 病毒。经分析，"Pengex"
以劫持用户首页流量牟利为目的，但是不同于其他"流量劫持"类病毒的是，它技术高明、手段凶狠，会主动攻击国内主流的安全软件，使他们失去内核对抗能力，这会让电脑完全失去安全防护。诡异的是，Pengex
唯独不攻击并且刻意"放过"腾讯电脑管家。

"Pengex" 通过盗版系统盘和"注册机"软件进行传播，并在用户电脑中留下后门，日后可随时植入任意病毒，因此威胁隐患极大。"Pengex"
会攻击各种主流的杀毒软件，包括火绒、360、金山等，导致这些软件的驱动无法加载，因此失去在内核层对抗病毒的能力。

但有意思的是，该病毒却唯独刻意放过了腾讯电脑管家，它将腾讯电脑管家加入白名单中，在进行"删除驱动回调"的操作时放过腾讯电脑管家。病毒的这种行为表明，该病毒团伙很可能是腾讯安全管家的系统盘渠道推广服务商，火绒建议"腾讯安全管家"彻查系统盘推广渠道。

"Pengex"
通过修改浏览器配置和进程启动参数两种方式，来劫持首页牟利。在此过程中，病毒会按照制作者的计划，将不同的浏览器指向不同的导航站。该病毒不仅攻击安全软件，还会攻击其他同类病毒，以便独占用户电脑首页资源牟利。据分析，该病毒劫持首页后设置的渠道号是"oemxiazaiba2"（"下载吧"的全拼），请各大导航站关注并查证这个渠道账号。

"火绒安全软件"已经在第一时间更新病毒库，可彻底查杀该病毒。火绒工程师提醒广大用户，如需重装系统，务必通过正规渠道，购买正版系统，目前看来，盗版系统盘已经成为电脑病毒的重要传播渠道。

#### 二、详细分析

该病毒是一个内核级后门病毒，初步怀疑该样本主要通过第三方系统盘方式进行传播。该样本在系统中运行后，会造成国内主流安全软件驱动程序无法正常加载，从而使安全软件失去防御能力。该病毒主要对抗的安全厂商包括：火绒、360、金山等，其恶意代码执行之后，可以执行远端
C&C 服务器存放的任意病毒代码。

该病毒分为两个部分，即病毒加载器和后门病毒，下文中分为两部分进行详细分析。病毒结构如下图所示：

![](https://images.seebug.org/content/images/2017/07/1-1.png-w331s)

病毒整体结构图

###### 病毒加载器

该部分代码主要用于对抗安全软件查杀和进行内核对抗。加载器功能代码分为两个部分，先会在内存中通过虚拟映射加载一个新的 ntoskrnl
镜像，再通过相同的方式将真正的病毒驱动加载到内存中，并且将导入的 ntoskrnl 中的函数地址指向其虚拟加载的 ntoskrnl
镜像中的函数地址上，通过此方法可以绕过其他驱动在 ntoskrnl 中设置的内核钩子。全局变量 `is_virus_load`
是一个标记，通过传入驱动主函数中的 RegistryPath 参数是否为 NULL 判断是否为病毒通过虚拟映射方式加载。如下图所示：

![](https://images.seebug.org/content/images/2017/07/2-1.png-w331s) 加载器驱动主函数代码

**(一) 虚拟加载ntoskrnl**

`load_fake_ntoskrnl_safe` 函数会通过虚拟加载新的 ntoskrnl 镜像，在其执行完虚拟加载逻辑之后，会与当前内存中系统加载的
ntoskrnl 模块前 0x200 个字节数据进行比较，从而判断自己创建的 ntoskrnl 镜像内容是否正常。如下图所示：

![](https://images.seebug.org/content/images/2017/07/3-1.png-w331s) 检测虚拟加载是否成功

![](https://images.seebug.org/content/images/2017/07/4-1.png-w331s)
虚拟加载ntoskrnl

**(二) 虚拟加载后门病毒**

`load_rootkit` 函数会通过与虚拟映射 ntoskrnl 相同的方法加载真正的病毒驱动。病毒驱动的镜像数据是被异或 0xC0
加密过的，该函数首先会将病毒数据进行解密，之后对该驱动进行映射并修复导入表和重定位数据，最后通过调用 `ExQueueWorkItem`
函数执行病毒驱动入口。如下图所示：

![](https://images.seebug.org/content/images/2017/07/5-1.png-w331s) 加载病毒驱动

上图所示调用 `ExQueueWorkItem` 函数所传入的 `WORK_QUEUE_ITEM`
结构尾部带有附加数据，在上述调用中，附加数据存放有被加载驱动的入口点地址。如下图所示：

![](https://images.seebug.org/content/images/2017/07/6-1.png-w331s) 执行驱动入口

###### 内核级后门

该病毒执行后，会不断地与 C&C 服务器（域名：caoduba.com 或 139.129.234.76，通讯端口：7897）进行通讯。病毒使用的域名和
IP 地址解密代码，如下图所示：

![](https://images.seebug.org/content/images/2017/07/7-1.png-w331s) 解密域名和IP地址

**(一) 病毒与C &C服务器通讯**

病毒与C&C服务器的通讯内容分为两大类：

1) 数据请求通知

服务器在获取到病毒请求数据的通知后，可以根据控制码返回被请求的数据。通过网络通讯，病毒可以进行远程驱动模块加载、获取远程动态库注入系统进程、获取配置数据进行流量劫持。控制码含义，如下图所示：

![](https://images.seebug.org/content/images/2017/07/8-1.png-w331s) 数据请求相关控制码

2) 运行状态通知

服务器可以根据通知中的控制码获取当前病毒的运行状态，例如映像加载回调是否设置成功，是否已经成功劫持用户主页等，病毒作者可以根据这些通知得知病毒运行中可能存在的问题。控制码含义，如下图所示：

![](https://images.seebug.org/content/images/2017/07/9.png-w331s) 运行状态通知

通过上述控制命令，我们可以直观的看到，该病毒不但可以根据远程获取的配置数据劫持用户首页，还可以根据病毒作者需求在用户计算机中执行任意恶意代码。又由于该病毒会阻止安全软件驱动加载，使得安全软件完全失去了与其进行内核对抗的能力，从而导致很难对其进行查杀。

病毒与服务器通讯函数，如下图所示：

![](https://images.seebug.org/content/images/2017/07/10.png-w331s) 发送数据代码

通讯使用TDI网络函数，连接服务器代码，如下图所示：

![](https://images.seebug.org/content/images/2017/07/11.png-w331s)
调用TDI网络函数链接服务器

发送数据、接收数据代码类似，仅以发送数据为例。如下图所示：
![](https://images.seebug.org/content/images/2017/07/13.png-w331s)

调用TDI网络函数发送数据

**(二) 控制码功能分析**

下面我们根据病毒所使用的主要的控制码对病毒功能进行详细分析：

1) 控制码0x2，获取病毒执行配置数据进行流量劫持

与服务器通讯后，病毒可以获取到劫持配置数据，数据中包括是否劫持某种浏览器、各个种类浏览器需要劫持的网址、控制病毒执行流程的执行标记。如下图所示：

![](https://images.seebug.org/content/images/2017/07/13-1.png-w331s) 下载配置

配置数据并不是通过明文存放，下载之后需要逐字节异或 0xC0 进行解密，数据长度共 0x1CA0 个字节。如下图所示：

![](https://images.seebug.org/content/images/2017/07/14.png-w331s) 解密配置

下载的浏览器配置内容中，包括需要劫持的浏览器种类、各个浏览器所劫持的网址、需要执行哪些对抗操作、是否劫持腾讯电脑管家的首页保护注册表项及所劫持注册表项内容。如下图所示：

![](https://images.seebug.org/content/images/2017/07/15.png-w331s) 下载的配置内容

上图中所示红框所标注出的变量 `virus_proc_ctrl_code`
可以控制病毒的执行执行的对抗操作流程，其所能控制的对抗操作例如：删除其他驱动的映像加载回调和进程回调、截断 attach
在系统网络驱动上的设备链等。因为绝大部分浏览器首页保护和首页劫持都会在这些位置上做文章，所以在病毒在劫持流量的同时进行上述对抗可以一定程度上提高其劫持成功率。该变量以位段的形式规定执行流程，各个位段含义如下图所示：

![](https://images.seebug.org/content/images/2017/07/16.png-w331s) 位段含义

使用 `virus_proc_ctrl_code` 变量控制执行流程，如下图所示：

![](https://images.seebug.org/content/images/2017/07/17.png-w331s)
virus_proc_ctrl_code相关代码

下面我们根据上图中所示顺序依次对其所使用的对抗方法进行说明：

A. 删除其他驱动的进程回调和映像加载回调

这种方法主要针对利用进程回调和映像加载回调相互配合劫持或保护浏览器启动参数的情况，病毒先通过搜索代码的方式在设置回调的系统函数中找到回调函数表，之后判断回调函数所属驱动模块是否在白名单中，如果不在白名单中则执行删除操作，删除成功后想服务器发送运行状态通知
0x10。如下图所示：

![](https://images.seebug.org/content/images/2017/07/18.png-w331s) 删除映像加载回调

![](https://images.seebug.org/content/images/2017/07/19.png-w331s)
搜索影响加载回调函数列表代码

![](https://images.seebug.org/content/images/2017/07/20.png-w331s)
判断回调地址所属驱动模块是否在白名单列表中

白名单中所存放字符串可以是文件名也可以是部分文件名，其中除了一些系统驱动模块外还包括腾讯电脑管家相关驱动，因为腾讯电脑管家驱动全部包含 QQPCMgr、Ts
和 TS 字符串，所以腾讯电脑管家的全部驱动都会被放过。白名单列表如下图所示：

![](https://images.seebug.org/content/images/2017/07/21.png-w331s) 白名单列表

![](https://images.seebug.org/content/images/2017/07/22.png-w331s) 检测回调所属模块文件名

删除进程回调的方法与删除映像加载回调方法类似。如果执行中无法得到进程回调函数表则向C&C服务器发送控制码 0xE，如果成功注册进程回调函数则向 C&C
服务器发送 0x11。如下图所示：

![](https://images.seebug.org/content/images/2017/07/23.png-w331s) 删除进程回调

![](https://images.seebug.org/content/images/2017/07/24.png-w331s) 搜索进程回调函数列表

B. 截断 attach 在系统网络驱动对象上的设备链

除了删除驱动回调外，该病毒还会通过截断 attach 到 tcpip、AFD、tdx
驱动上设备链的方式，排除网络过滤驱动对其流量劫持效果的影响。如下图所示：

![](https://images.seebug.org/content/images/2017/07/25.png-w331s)
截断attach的设备链

C. 清空 hosts 文件

![](https://images.seebug.org/content/images/2017/07/26.png-w331s) 清除hosts

D. 清除 BHO（BrowserHelperObjects）

通过删除`\Registry\Machine\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\BrowserHelperObjects`
注册表项下的所有子项来删除所有
BHO。但当病毒发现系统中存在`\REGISTRY\MACHINE\Software\Wow6432Node\Tencent\QQPCMgr`
注册表项时，则不对 BHO 文件进行清除。如下图所示：

![](https://images.seebug.org/content/images/2017/07/27.png-w331s) 删除BHO相关代码

![](https://images.seebug.org/content/images/2017/07/28.png-w331s) 删除BHO注册表项

E. 重置IE代理设置

病毒通过将`\Registry\User\`当前用户`\Software\Microsoft\Windows\CurrentVersion\InternetSettings的ProxyEnable`
键值置为0的方法禁用网络代理。

F. 劫持浏览器配置

在进行对抗操作之后，病毒使用所收到的劫持网址和相关数据尝试对一些常用浏览器（IE、QQ浏览器、360安全浏览器、火狐、世界之窗）和腾讯电脑管家首页保护的配置进行修改，从而进行流量劫持。在进行劫持操作之后，会向C&C服务器发送控制码0x4。如下图所示：

![](https://images.seebug.org/content/images/2017/07/29.png-w331s)
劫持浏览器和腾讯管家首页保护配置

劫持浏览器代码以劫持360安全浏览器为例，如下图所示：

![](https://images.seebug.org/content/images/2017/07/30.png-w331s)
构造360安全浏览器相关环境字符串

最引起我们注意的是，在劫持360安全浏览器首页的同时，病毒还将渠道号设置成了
"oemxiazaiba2"，字母组成的后半部分为"下载吧"全拼，但由于可以获取到的信息十分有限，我们暂时无法求证其与"下载吧"是否存在直接关系。如下图所示：

![](https://images.seebug.org/content/images/2017/07/31.png-w331s)
劫持360安全浏览器首页代码

G. 劫持腾讯电脑管家首页保护网址

病毒除了会篡改浏览器配置外，还会通过添加自定义保护网址（自定义网址相关注册表项均为 3rd 开头）的方式，劫持腾讯电脑管家首页保护网址。如下图所示：

![](https://images.seebug.org/content/images/2017/07/32.png-w331s)
修改腾讯电脑管家首页保护注册表项

2) 控制码 0x3，获取远程驱动模块

与上文（一）病毒加载器中病毒所使用的方法相似，只不过病毒这次用来加载的驱动模块数据是通过C&C服务器获取的，大致执行过程相同，其具体的驱动执行过程不再赘述。如下图所示：

![](https://images.seebug.org/content/images/2017/07/33.png-w331s) 加载远程驱动模块

![](https://images.seebug.org/content/images/2017/07/34.png-w331s)
虚拟加载驱动并执行入口点

3) 控制码0xA，获取远程驱动模块

执行远程驱动模块代码部分，是通过注入 winlogon.exe 进程实现的，注入部分使用了开源的 BlackBone 项目代码。如下图所示：

![](https://images.seebug.org/content/images/2017/07/35.png-w331s) 请求远程动态库

病毒会先将获取到的动态库数据是放到 system32 目录下，之后再调用 BlackBone 代码将动态库注入到 winlogon 进程中执行。如下图所示：

![](https://images.seebug.org/content/images/2017/07/36.png-w331s) 注入 winlogon

![](https://images.seebug.org/content/images/2017/07/37.png-w331s) 注入 winlogon

![](https://images.seebug.org/content/images/2017/07/38.png-w331s) 病毒中的
BlackBone 项目相关代码

**(三) 其他劫持和对抗手段**

1) 通过进程回调和映像加载回调劫持浏览器启动参数

除了上述介绍的病毒所使用的劫持方法外，病毒还通过注册进程回调和映像加载回调劫持浏览器启动参数进行流量劫持。如下图所示：

![](https://images.seebug.org/content/images/2017/07/39.png-w331s) 病毒注册回调

病毒在进程回调中会判断浏览器种类，针对不同的浏览器劫持的网址链接可以有所不同，在检测到需要进行劫持的进程后，将相关的劫持信息添加到劫持列表中。如下图所示：

![](https://images.seebug.org/content/images/2017/07/40.png-w331s) 劫持浏览器进程检测

在进程回调中记录劫持进程信息后，在映像加载回调中将 PEB 中的进程参数篡改为欲劫持网址。如下图所示：

![](https://images.seebug.org/content/images/2017/07/41.png-w331s) 劫持进程参数

2) 通过映像加载回调拦截驱动加载

除了用于进行流量劫持的映像加载回调外，病毒还注册了一个用来进行内核对抗的映像加载回调，该回调函数不但会阻止带有安全软件签名信息的驱动执行，还会拦截一些内核级流量劫持类病毒的执行。当所加载的驱动信息在黑名单中，病毒会将映像的入口点代码替换为直接返回，从而禁止执行该映像中的逻辑代码。如下图所示：

![](https://images.seebug.org/content/images/2017/07/42.png-w331s)
禁止执行安全软件驱动逻辑

在判断正在加载的映像是否属于黑名单时，病毒先常见的内核级流量劫持病毒的文件名进行匹配，如果文件名中包含 Mslmedia.sys 或者
mssafel.sys
则会禁止其执行。之后，病毒会获取当前映像的签名信息与黑名单中的签名信息进行匹配，如果包含则也会禁止其执行。黑名单中的签名信息包括：火绒、360、金山、2345、瑞星、百度，甚至还包括
ADSafe
的签名和病毒常用"上海域联"签名信息，但是其中依然没有腾讯电脑管家相关签名信息，由此我们可以推断病毒对腾讯电脑管家是有意进行放过的，并非无意之举。签名信息黑名单信息，如下图所示：

![](https://images.seebug.org/content/images/2017/07/43.png-w331s) 签名黑名单

如上图，除了主流安全软件的签名外，还包括有"上海域联"的签名信息。该签名虽然已经过期，但是不会影响驱动正常加载，所以经常被病毒程序盗用，去年大面积爆发的"小马激活病毒"也是盗用了"上海域联"的签名。相关代码如下图所示：

![](https://images.seebug.org/content/images/2017/07/44.png-w331s) 判断是否属于黑名单

![](https://images.seebug.org/content/images/2017/07/45.png-w331s)
检测签名信息是否在黑名单中

由于很多内核级流量劫持类病毒都使用 VMProtect 壳进行保护，所以病毒作者还加入了一个更加暴力的判断方法，如果节名为 `UPX0` 或者
`.vmp0` 则禁止驱动逻辑执行。如下图所示：

![](https://images.seebug.org/content/images/2017/07/46.png-w331s) 检测节名

#### 三、附录

文中涉及样本SHA256：

![](https://images.seebug.org/content/images/2017/07/47.png-w331s)

[附PDF版报告下载地址](http://down4.huorong.cn/doc/pengex.pdf)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/347/>

