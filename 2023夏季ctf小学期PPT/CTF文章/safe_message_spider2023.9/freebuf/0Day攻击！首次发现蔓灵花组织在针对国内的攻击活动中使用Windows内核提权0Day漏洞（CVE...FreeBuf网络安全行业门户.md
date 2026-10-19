**01 背景**

2020年12月中旬，安恒威胁情报中心猎影实验室发布了 **《蔓灵花（BITTER）组织近期针对我国政府部门、科研机构发起攻击》**
，文中已经给出并分析了该组织攻击的一些组件。

在后续的跟进分析中我们又发现了一个全新的组件，经过分析，我们发现该组件利用了一个未知的Windows内核提权漏洞，且利用代码适配了Windows10
1909操作系统。我们随即将相关信息报送给微软，经过微软的确认，我们确信这是一个win32kfull模块的0Day漏洞，在最新版本的Windows10
20H2全补丁环境下也能触发！

 **02 事件时间轴**

●2020年12月10日，安恒威胁情报中心捕获到相关样本

●2020年12月15日，安恒威胁情报中心在分析过程中发现一个可疑的Windows内核提权漏洞，并启动根因调查

●2020年12月29日，安恒威胁情报中心将漏洞信息报告给MSRC

●2020年12月29日，MSRC确认收到漏洞报告

●2020年12月31日，MSRC确认该漏洞是一个0Day，并开始调查，同时要求提供更多细节

●2020年12月31日，安恒威胁情报中心向MSRC提供该0Day漏洞的更多细节

●2021年1月6日，MSRC就安恒威胁情报中心提供的更多细节表示感谢，并表示漏洞已在修复中

●2021年2月9日，MSRC修复该漏洞，漏洞编号为CVE-2021-1732

 **03 漏洞特点**

根据我们的调查分析，本次捕获的0Day漏洞具有以下特点：

 **（1）** **攻击目标为最新版Windows 10操作系统**

(a)在野样本攻击的是当时最新版Windows10 1909 64位操作系统（在野样本的编译时间为2020年5月）；

(b)在野样本适配了从Windows10 1709到Windows10 1909多个版本，且只会在Windows10 1709及以上版本中运行利用代码；

(c)原始利用代码经过少量修改后可在最新版Windows10 20H2 64位全补丁环境进行提权。

 ** **（2）** 漏洞质量高，利用手法精湛，稳定性好，动态检测难度大**

(a)在野样本借助漏洞绕过了最新版Windows 10系统的内核地址空间布局随机化（KASLR）；

(b)本次漏洞不同于以往的Win32k漏洞，漏洞类型不是UAF，整个利用过程不涉及堆喷射和内存重用，Type
Isolation缓解机制对其无效。在野样本在打开Driver
Verifier验证器的情况下依然可以正常提权，无法通过开启内核池追踪检测到，动态检测难度大；

(c)在野样本的任意地址写入采用了漏洞特性结合SetWindowLong系列函数的手法，令人眼前一亮；

(d)在野样本借助GetMenuBarInfo实现任意地址读取，这种手法此前未被公开过，这体现出开发者精湛的利用编写水平；

(e)在野样本在构造出任意地址读写原语后，采用Data Only Attack的方式替换了当前进程的Token，目前的内核缓解机制无法防御此类攻击；

(f)在野样本的漏洞利用成功率几乎为100%；

(g)在野样本在完成利用后，将相关内核结构全部还原，整个过程不会对系统造成蓝屏影响，工作稳定。

 ** **（3）** 使用谨慎，隐蔽性好**

(a)在野样本在进行漏洞利用前对特定杀毒软件进行了检测；

(b)在野样本对当前操作系统版本进行了判断，低于Windows 10 1709版本的系统不会调用漏洞利用函数；

(c)在野样本从2020年5月完成编译，到2020年12月被我们发现，中间至少存活了7个月，这说明使用者在使用该漏洞时相当谨慎，间接体现出捕获此类隐蔽性样本的难度。

 **04 漏洞触发效果**

在最新版Windows10 1909 x64环境中对在野0Day样本进行测试，可以看到该进程在初始启动时为Medium权限，

![](https://image.3001.net/images/20210206/1612592875_601e36eb19a6257d9d209.png!small)

当漏洞利用代码执行后，当前进程变为System权限，这表明当前进程的Token已经被替换为System进程的Token，这是内核提权漏洞利用的常见手法。

![](https://image.3001.net/images/20210206/1612592947_601e3733bc1d2534a8149.png!small)

在最新的Windows10 20H2全补丁环境下启动该样本，则会导致系统蓝屏。这是因为该利用代码被编译时，Windows10 2004和Windows10
20H2还未发布，攻击者只将利用代码适配到当时最新的Windows10 1909版本。

![](https://image.3001.net/images/20210206/1612593183_601e381feec5d5c3bbc56.png!small)

 **05 技术分析**

 **0x01漏洞成因**

该漏洞是win32kfull!xxxCreateWindowEx函数内，一处由用户态回调导致的flag位设置与对应offset设置不同步导致的漏洞。

win32kfull.sys模块的xxxCreateWindowEx函数在创建带窗口扩展内存的窗口时，会调用xxxClientAllocWindowClassExtraBytes用户态回调函数，返回用户态创建窗口扩展内存。攻击者可在回调函数内调用NtUserConsoleControl并传入当前窗口的句柄，将当前窗口内核结构中的一个成员(用于指明窗口扩展内存的区域)修改为offset，并修改相应的flag，指明该成员是一个offset。随后，攻击者可在回调函数中调用NtCallbackReturn返回任意值，回调结束后，该返回值会覆写之前的offset，但对应的flag并未被清除，随后未经校验的offset直接被内核代码用于堆内存寻址，引发越界访问。

 **0x02漏洞触发逻辑**

我们完全逆向了在野样本的漏洞利用代码，在此基础上构造了该漏洞的poc，下图是poc的主要执行逻辑，我们将结合此图对漏洞触发逻辑进行解释：

![](https://image.3001.net/images/20210206/1612593212_601e383c70689fc36e67d.png!small)

在win32kfull!xxxCreateWindowEx 函数中，

窗口扩展内存默认会使用xxxClientAllocWindowClassExtraBytes
函数回调用户态函数，该回调函数的返回值是一个指针，返回的是从用户态创建的内存，这个值会被保存到内核结构中。

![](https://image.3001.net/images/20210206/1612593222_601e3846379adea7d664d.png!small)

当我们在自定义的xxxClientAllocWindowClassExtraBytes回调函数中调用
win32kfull!xxxConsoleControl
函数后,窗口扩展内存的flag会被置位(|=0x800)，并将保存在内核地址的用户态地址修改成一个offset，以便使用内核的堆管理器管理。

![](https://image.3001.net/images/20210206/1612593233_601e38517fb4788b9303f.png!small)

在poc中，我们选择在销毁窗口时触发漏洞， win32kfull!xxxFreeWindow
函数会判断上述flag是否被设置，若被设置，则代表对应的内核结构中存储的是offset，调用RtlFreeHeap函数释放相应的内存；若未被设置，则代表对应的内核结构中存储的是内存地址，调用xxxClientFreeWindowClassExtraBytes借助用户态回调函数进行释放。

![](https://image.3001.net/images/20210206/1612593256_601e3868472b5de325888.png!small)

在xxxClientAllocWindowClassExtraBytes回调函数内，可以借助NtCallbackReturn控制返回值，回调结束后，会用返回值覆写之前的offset，但并未清除相应的flag。在poc中，我们返回了一个用户态堆地址，从而将原来的offset覆写为一个用户态堆地址(fake_offset)。这最终导致win32kfull!xxxFreeWindow在用RtlFreeHeap释放内核堆时出现了越界访问。

 **RtlFreeHeap所期望的释放地址是RtlHeapBase+offset**

 **RtlFreeHeap实际释放的地址是RtlHeapBase+fake_offset**

![](https://image.3001.net/images/20210206/1612593277_601e387d8d947c7399a0c.png!small)

只要调用此处的RtlFreeHeap，就会导致越界释放，从而导致BSOD。

![](https://image.3001.net/images/20210206/1612593299_601e3893eb43c17aceef0.png!small)

 **0x03在野利用**

在野样本是一个64位的程序，它首先调用CreateToolhelp32Snapshot等函数遍历所有进程，查找“avp.exe”进程（“avp.exe”是卡巴斯反病毒软件进程）。

![](https://image.3001.net/images/20210206/1612593314_601e38a25543dba1115e5.png!small)

在野样本在检测“avp.exe”进程后，只会对一些自定义结构进行赋值，并不会退出进程，后续的提权函数仍会被调用。我们在装有卡巴斯基反病毒软件的环境中进行了实验，在野样本可以正常提权，如下图所示。

![](https://image.3001.net/images/20210206/1612593325_601e38ad06cb7a59cfd6d.png!small)

随后，在野样本调用IsWow64Process以判断当前所运行的环境，并依据结果对一些偏移进行修正。这里代码编写者似乎在逻辑判断时存在一些问题，按照下面的源码示意，下图中的g_x64应理解为g_x86，但后续的调用表明此变量代表x64环境。

代码编写者在初始化时强制给g_x64赋值为TRUE，所以此处对IsWow64Process的调用可以忽略，不过这似乎暗示开发者还写了另一个32位版本的提权组件。

![](https://image.3001.net/images/20210206/1612593337_601e38b907763a4e0be38.png!small)

在修正偏移后，在野样本动态获取了RtlGetNtVersionNumbers，NtUserConsoleControl和NtCallbackReturn三个函数。随后调用RtlGetNtVersionNumbers函数获取当前系统版本号，检查当前系统版本号是否大于等于16353（Windows10
1709），只有大于该版本号时，漏洞利用代码才会被调用，接着又判断当前系统版本号是否大于等于18204（Windows10
1903），如果大于，则修正一些内核结构的偏移，便于后面的利用。

![](https://image.3001.net/images/20210206/1612593348_601e38c44b023e7038390.png!small)

校验通过后，在野样本开始调用利用代码，它首先动态搜索得到HmValidateHandle函数的地址，并hook
USER32!_xxxClientAllocWindowClassExtraBytes回调函数。

![](https://image.3001.net/images/20210206/1612593357_601e38cdeb109bf889f84.png!small)

利用代码随后注册了两种窗口类，其中一种用于创建漏洞窗口，类名为“magicClass”，另一种窗口类名为“normalClass”，用于创建一般窗口，用以辅助后续的任意地址写入。

![](https://image.3001.net/images/20210206/1612593366_601e38d6a64ab2d02f496.png!small)

接着，利用代码借助normalClass创建10个窗口，调用HmValidateHandle函数泄露这些窗口的用户态tagWND结构体地址，并泄露结构体内的offset偏移，随后销毁第3-10个窗口，只保留窗口0和窗口1。

如果当前环境为64位，则调用NtUserConsoleControl将窗口0对应的flag从pointer改为offset，这样，窗口0的内核tagWND结构寻址方式变为offset，而窗口1的寻址方式仍为pointer。

![](https://image.3001.net/images/20210206/1612593377_601e38e1d391bccae01db.png!small)

随后，利用代码借助magicClass创建一个带特定长度窗口扩展内存的窗口2，在窗口2创建过程中触发xxxClientAllocWindowClassExtraBytes回调,进入自定义回调函数，在自定义函数中，首先判断当前窗口扩展内存长度是否为特定长度，随后判断当前环境是否为x64，校验通过后，调用NtUserConsoleControl将窗口2的的内核tagWND结构寻址方式变为offset；随后调用NtCallbackReturn将窗口2的窗口扩展内存对应的offset改为窗口0的tagWND对应的offset，这导致后续对窗口2的窗口扩展内存的读写都变为了对窗口0的tagWND结构的读写，到这里已经成功使用漏洞。

![](https://image.3001.net/images/20210206/1612593386_601e38ea4f65252f5bdf6.png!small)

回调结束后，利用代码已经可以借助SetWindowLongW对窗口0的内核tagWND成员进行修改。

利用代码首先调用SetWindowLongW将窗口0的cbWndExtra设置为0xFFFFFFF，从而使窗口0具备越界写入能力。随后借助窗口0令窗口1的dwStyle|=WS_CHILD，随后用fake_spmenu替换窗口1原有的spmenu，在fake_spmenu的基础上实现任意地址读写原语。

![](https://image.3001.net/images/20210206/1612593396_601e38f488cdaeadc1098.png!small)

利用代码的任意地址读原语借助fake_spmenu，

配合GetMenuBarInfo读取tagMenuBarInfo.rcBar.left和tagMenuBarInfo.rcBar.top两个成员进行实现，这种方式此前未被公开使用过，但和2016年ZeroNight的《LPE
vulnerabilities exploitation on Windows 10 Anniversary Update》中提到的思路类似。

![](https://image.3001.net/images/20210206/1612593406_601e38feed4c83e246e47.png!small)

利用代码的任意地址写原语借助窗口0和窗口1，配合SetWindowLongPtrA进行封装，具体实现如下。

![](https://image.3001.net/images/20210206/1612593414_601e3906d4d76c05d220d.png!small)

构造出任意地址读写原语后，利用代码从窗口1的原始spmenu结构中泄露出一个内核地址，借助该地址逐步定位到当前进程的EPROCESS，随后遍历进程链，找到System进程的Token指针和当前进程EPROCESS结构内存储Token的地址，并将当前进程的Token改写System进程的Token，实现权限提升。

![](https://image.3001.net/images/20210206/1612593423_601e390f55f5e00cb6722.png!small)

完成提权后，利用代码借助任意地址写入原语将之前被修改的窗口0，窗口1，窗口2成员进行还原，例如原始的spmenu和导致漏洞的flag，以确保利用完成后不会产生蓝屏异常。整个漏洞利用过程非常稳定。

 **0x04 结论**

该漏洞是win32k子系统内一个通过CallBack回调机制引发的漏洞，该漏洞可以被用作IE、Adobe
Reader等沙箱环境的逃逸。该漏洞质量较高，在野样本利用手法高超，威胁组织可能招募了具有一定实力的成员，也不排除从专业的漏洞中间商处购买，该在野样本的使用体现出背后APT组织较强的0day漏洞储备能力。

 **06 总结思考**

0Day在网络空间隐蔽战场上具有举足轻重的作用，0Day通常作为攻击组织的战略储备，具有特殊使命和战略意义。为了充分合理发挥其价值，一般只会在针对极特殊的目标条件下才会使用。

随着软硬件不断的成熟和防御体系的提升，一些重点软硬件、系统的0Day挖掘成本和利用成本已经变得非常高，使用条件变得更为苛刻，再譬如多年来各厂商对APT攻击检测的投入和能力加强，使得APT组织对0Day的使用变得更加谨慎，稍有不慎就会使得0Day的的价值生命周期缩水。

0Day仍是“核武器”，发现并不一定等于检出，而是有可能在其它蛛丝马迹中窥见的端倪。最直接的例子就是永恒之蓝所利用的远程代码漏洞，在被曝光前已经潜伏了许久。

对0Day或其它隐蔽攻击的检测能力提升仍是APT对抗过程中需要持续精进、不断提高、必不可少的重要环节。

0Day的产生不会停止，使用漏洞进行的攻击不会停止。在去年（2020年）就曝光了多起涉及在野0Day/1Day漏洞的攻击行动，仅安恒威胁情报中心追踪到的就有3起，除此之外，全球至少还披露了十余起在野漏洞利用事件。并从披露漏洞的趋势来看，浏览器、沙箱逃逸、提权漏洞将会进一步增加。

除了端上的攻击利用之外，边界系统、临界设备、集控系统也是需要关注的点。去年就有多起此类安全事件的发生。其中更需要注意的是起到安全防护的边界系统，更需要关注、加强和保障自身质量。

未被发现并不表示不存在，可能更多的是处于潜伏状态。在高级威胁、隐蔽攻击、0Day攻击的发现、检测与防御上，需要在博弈过程中不断迭代强化。需要积极思考在各环节、各区块、各点位上对防御体系、防御能力、防御方位上的把握。网络安全任重而道远，共勉之。

 **07 自查方案**

这次Bitter APT组织攻击的样本默认会存在如下目录：

c:\intel\logs

如自查的时候，发现存在相关目录或文件，用户可以提交样本到安恒威胁情报中心平台进行检测，平台地址：

 **https://ti.dbappsecurity.com.cn/**

![](https://image.3001.net/images/20210206/1612593447_601e39273e83258b00134.png!small)

也可联系我们处理

联系方式： **400 6059 110**

如果客户有购买安恒APT攻击预警平台，可以直接上传进行检测。

![](https://image.3001.net/images/20210206/1612593456_601e393094edf31c0360e.png!small)

**攻击者使用0day进行攻击是为了提权，一般是为了获取更多、更高的权限，比如为了内网横向渗透做准备。如果发现同时还存在某国外VPN程序，不排除该单位的内网存在被横向渗透的风险。**

 **08 防御建议**

升级安恒APT攻击预警平台以及明御主机安全及管理系统EDR到最新版本可进行检测。

 **请确认是最新版本:**

1、APT攻击预警平台版本大于等于V2.0.66.23509.210119

2、EDR版本大于等于v2.0.15.34

安恒APT攻击预警平台能够发现已知或未知威胁，平台能实时监控、捕获和分析恶意文件或程序的威胁性，并能够对邮件投递、漏洞利用、安装植入、回连控制等各个阶段关联的木马等恶意样本进行强有力的监测。同时，平台根据双向流量分析、智能的机器学习、高效的沙箱动态分析、丰富的特征库、全面的检测策略、海量的威胁情报等，对网络流量进行深度分析。检测能力完整覆盖整个APT攻击链，有效发现APT攻击、未知威胁及用户关心的网络安全事件。

安恒明御主机安全及管理系统是一款集成了丰富的系统加固与防护、网络加固与防护等功能的主机安全产品。业界独有的高级威胁模块，专门应对攻防对抗场景；
明御主机安全及管理系统通过自主研发的专利级文件诱饵引擎，有着业界领先的勒索专防专杀能力；通过内核级东西向流量隔离技术，实现网络隔离与防护；拥有补丁修复、外设管控、文件审计、违规外联检测与阻断等主机安全能力。目前产品广泛应用在服务器、桌面PC、虚拟机、工控系统、容器安全、攻防对抗等各个场景。

 **09 检测策略**

 **YARA**

rule apt_bitter_win32k_0day {

meta:

author = "dbappsecurity_lieying_lab"

data = "2021-01-01"

strings:

$s1 ="NtUserConsoleControl" ascii wide

$s2 = "NtCallbackReturn" ascii wide

$s3 ="CreateWindowEx"ascii wide

$s4 ="SetWindowLong"ascii wide

$a1 ={48 C1 E8 02 48 C1 E9 02 C7 04 8A }

$a2 ={66 0F 1F 44 00 00 80 3C 01 E8 74 22 FF C2 48 FF C1}

$a3 = {48 63 05 CC 69 05 00 8B 0D C2 69 05 00 48 C1 E0 20 48 03 C1}

condition:

uint16(0) == 0x5a4d and all of ($s*) and 1 of ($a*)

}

 **10 英文版报告**

复制链接到浏览器，即可查看最全英文版报告

https://ti.dbappsecurity.com.cn/blog/index.php/2021/02/10/windows-kernel-zero-day-exploit-is-used-by-bitter-apt-in-targeted-attack/

本文为安恒威胁情报中心原创，转载请注明出处，谢谢

![](https://image.3001.net/images/20210206/1612593518_601e396e2082ff11a1ab7.png!small)

安恒信息威胁情报中心：专注于提供威胁情报数据和分析服务

平台地址：https://ti.dbappsecurity.com.cn/

