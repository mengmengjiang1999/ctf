## 1.前言

Proofpoint的安全研究员发现并分析了这个新型恶意软件并命名为NerbianRAT，此恶意软件使用了反分析和反逆向功能，该恶意软件是使用Golang编写的64位程序，主要传播方式为冒充世界卫生组织发送的COVID-19相关的安全措施邮件，通过邮件附件中有VBA宏的Word文档传播。

## 2.样本运行流程

![image](https://image.3001.net/images/20220708/1657256153_62c7b8d96507a4949a94d.jpg!small)

## 3.样本IOCs

名称: ee1bbd856bf72a79221baa0f7e97aafb6051129905d62d74a37ae7754fccc3db.doc  
大小: 280469 字节 (273 KiB)  
MD5: d7888fea6047b662a30bf00edac4c3ee  
SHA1: 8137670512be55796f612e41602f505955b0bb0c  
SHA256: ee1bbd856bf72a79221baa0f7e97aafb6051129905d62d74a37ae7754fccc3db

名称: MoUsoCore.exe  
大小: 5867008 字节 (5729 KiB)  
MD5: 5d5bc970f975341558b8d2c225ca0115  
SHA1: 4f74826ed56cda233cfc12b86fd1b7da4a9f2e56  
SHA256: 902c65435b6b44cfda1156b0e7c6a30b2785fa4f2cbb9b1944a66f5146ec7aa5

名称: UpdateUAV.exe  
大小: 3642880 字节 (3557 KiB)  
MD5: 9cca59eec5af63e42cd845b67cf6df89  
SHA1: 178aad6c7918cc495a908944e79143a913630890  
SHA256: 1b8c9e7c150bacd466fbe7f12b39883821f23b67cae0a427a57dc37e5ea4390f

## 4.恶意代码分析

### 4.1 doc宏代码分析

双击打开doc文件发现是一个带宏的文档，文档中诱导用户点击启用宏脚本  
![image](https://image.3001.net/images/20220708/1657256644_62c7bac4e1ed192e18c1e.jpg!small)

这里我使用olevba脚本来分析此word文档的vba代码  
![image](https://image.3001.net/images/20220708/1657256806_62c7bb665c3a7a12360bc.jpg!small)

olevba脚本已经帮我们分析出了此vba代码的主要功能，从解码的Base64字符串我们大致可以判断此vba脚本使用powershell从C2下载了payload并写入本地文件夹执行  
![image](https://image.3001.net/images/20220708/1657256832_62c7bb80ec0b37f8147e0.jpg!small)

此vba代码有三个函数，GetByte和DecodeBase64这两个函数功能为解码Base64  
![image](https://image.3001.net/images/20220708/1657256849_62c7bb918eac3639cbc49.jpg!small)

主要的Document_Open入口函数我们可以看到定义了很多字符串但都是经过Base64编码，这些字符串在使用之前都调用DecodeBase64函数进行解码

![image](https://image.3001.net/images/20220708/1657256867_62c7bba327c550ab66a18.jpg!small)

我们将Base64字符串解码后优化代码再查看逻辑更清晰，主要逻辑就是红框中的命令行，使用cmd.exe将powershell命令行写入%temp%\util.bat，然后执行bat脚本，从hxxps://www[.]fernandestechnical[.]com/pub/media/gitlog下载文件到%appdata%\UpdateUAV.exe并且执行，执行完UpdateUAV.exe后将%temp%\util.bat和%appdata%\UpdateUAV.exe删除  
![image](https://image.3001.net/images/20220708/1657256903_62c7bbc75500b33978600.jpg!small)

### 4.2 UpdateUAV.exe分析

我们查看从C2下载的dropper文件，通过详细信息可以看到，文件详细信息伪装成Windows系统程序，这里还可以发现此dropper的原始文件是nsoobe.exe  
![image](https://image.3001.net/images/20220708/1657256934_62c7bbe63d75ef1f840af.jpg!small)

使用DIE工具查看UpdateUAV.exe发现此程序是64位程序并且使用了UPX3.9.6压缩壳进行加壳  
![image](https://image.3001.net/images/20220708/1657256950_62c7bbf6c9204703a169a.jpg!small)

我这里使用了UPX -d命令直接进行自动脱壳，如果遇到了修改版的UPX就需要手动脱壳，脱完壳文件体积膨胀到了将近一倍  
![image](https://image.3001.net/images/20220708/1657256972_62c7bc0c94482f1fa94b5.jpg!small)

脱完壳我们在使用DIE工具查看此UpdateUAV.exe是使用Golang编写的，Go编译器版本号为1.15.0或以上的版本  
![image](https://image.3001.net/images/20220708/1657256996_62c7bc2485cc9af0db3b9.jpg!small)

要想确定精确的Go编译器版本可以通过搜索字符串`go1.`关键词，可以看到UpdateUAV.exe使用的是go1.17.3版本编译器，注意此方法在遇到去除符号信息和严重混淆的样本可能无效  
![image](https://image.3001.net/images/20220708/1657257037_62c7bc4d793832da085f3.jpg!small)

这里直接使用IDA打开文件进行分析，查看main函数发现此Golang程序的符号信息都在，代码并没有被加密或者混淆，我们甚至可以通过函数符号名分析出函数的大致功能，比如函数main_hideWindows可以推断是隐藏进程窗口  
![image](https://image.3001.net/images/20220708/1657257183_62c7bcdf151f1c7fc7d9a.jpg!small)

我们使用x64dbg进行动态调试，这里为了方便调试我们手动关闭掉随机基址，使用010Editor打开PE文件将Nt头中的扩展头中的DllCharacteristics前1个字节改为00就关闭了PE文件的随机基址，这里原始是字节60
81  
![image](https://image.3001.net/images/20220708/1657257215_62c7bcff58ca0b5e5a37f.jpg!small)

我们改为00 81并保存至此已经成功将随机基址关闭  
![image](https://image.3001.net/images/20220708/1657257236_62c7bd14eb6d52bbbe2a1.jpg!small)

我们此时再把IDA中的符号信息导出成MAP文件并导入x64dbg，打开IDA选择File->Produce file->Create MAP
file然后选择保存位置，把全部选框都勾上确认  
![image](https://image.3001.net/images/20220708/1657257253_62c7bd2532893d2e1bdfc.jpg!small)

然后使用x64dbg的SwissArmyKnife插件导入刚刚生成的MAP文件  
![image](https://image.3001.net/images/20220708/1657257276_62c7bd3c63387c21080c2.jpg!small)

当x64dbg导入MAP文件后通过查看IDA中的main函数地址并下断点，MAP文件导入x64dbg后让我们可以和IDA分析更好的同步  
![image](https://image.3001.net/images/20220708/1657257295_62c7bd4fd558528f25716.jpg!small)

首先分析hideWindows函数，通过函数名可猜测此函数是隐藏控制台窗口，首先使用GetConsoleWindow获取控制台窗口句柄  
![image](https://image.3001.net/images/20220708/1657257382_62c7bda69001f849496fb.jpg!small)

最后调用ShowWindowAsync函数使用SW_HIDE参数将控制台窗口隐藏  
![image](https://image.3001.net/images/20220708/1657257406_62c7bdbe59722a3ec0735.jpg!small)

接下来分析checkEnvironment函数，可以看到此函数中调用了github上的第三方包chacal  
![image](https://image.3001.net/images/20220708/1657257430_62c7bdd65019c1c5f095c.jpg!small)

我们搜索发现chacal这个包是Golang的反虚拟机框架  
![image](https://image.3001.net/images/20220708/1657257449_62c7bde959ba5727eebdd.jpg!small)

checkEnvironment函数主要通过5个函数实现，其中两个函数都是安全工具进程检测，另外三个函数主要是反虚拟机检测  
![image](https://image.3001.net/images/20220708/1657257478_62c7be06db162c1aa9ca2.jpg!small)

antidebug_processList函数调中又调用了第三方的包go_ps实现遍历windows进程  
![image](https://image.3001.net/images/20220708/1657257502_62c7be1e648f7f7751b6c.jpg!small)

使用了CreateToolhelp32Snapshot函数创建进程快照，然后使用Process32First和Process32Next函数组合遍历进程  
![image](https://image.3001.net/images/20220708/1657257531_62c7be3b3e8a852bb9806.jpg!small)

Process32Next遍历下一个进程  
![image](https://image.3001.net/images/20220708/1657257570_62c7be62bcabfd9f183e9.jpg!small)

遍历完进程后将调用github_com_p3tr0v_chacal_utils_PList函数进行对比  
![image](https://image.3001.net/images/20220708/1657257619_62c7be93afd5f244a0e36.jpg!small)

先对比进程黑名单列表字符串长度，如果长度相同则调用runtime_memequal函数进行字符串对比  
![image](https://image.3001.net/images/20220708/1657257680_62c7bed09e59c4c5f18bc.jpg!small)

进程黑名单列表一共有42个如下，antimem_processList函数和antidebug_processList函数逻辑都相同不过antimem_processList只检测了DumpIt.exe、RAMMap.exe、RAMMap64.exe、vmmap.exe这四个用于DUMP进程内存的工具进程所以就不贴图了  
![image](https://image.3001.net/images/20220708/1657257706_62c7beea4345161e98042.jpg!small)

IsVirtualDisk函数首先调用了queryWMI函数，此函数封装了两个函数先调用了CreateQuery函数创建了WMI WQL查询语句  
![image](https://image.3001.net/images/20220708/1657257761_62c7bf2148a3309cc0e22.jpg!small)

然后调用wmi_Query函数使用WMI WQL语句进行查询了网卡信息  
![image](https://image.3001.net/images/20220708/1657257785_62c7bf398b11b97813594.jpg!small)

最后调用了ContainsInList函数对比网卡是否为列表中名单中的虚拟网卡，虚拟网卡黑名单列表中有三个virtual,vmware, vbox  
![image](https://image.3001.net/images/20220708/1657257814_62c7bf56d8ad069ebb4e8.jpg!small)

接下来分析ByMacAddress函数该函数首先调用了getMacAddr函数查询本机的MAC地址  
![image](https://image.3001.net/images/20220708/1657257834_62c7bf6a545622db74a74.jpg!small)

然后调用ContainsPrefix函数对比本机和黑名单列表的的MAC地址  
![image](https://image.3001.net/images/20220708/1657257854_62c7bf7e6e026ead49ab8.jpg!small)

接下来分析diskTotalSize函数，从函数符号可猜测此函数用来检测硬盘大小，通过函数的传参0x64十进制为100可以猜测此检测大小为100GB  
![image](https://image.3001.net/images/20220708/1657257877_62c7bf95a7466f4a7b390.jpg!small)

通过分析diskTotalSize函数内部，也是调用了queryWMI函数进行查询硬盘信息，然后对比本机硬盘是否小于100GB，我的虚拟机硬盘大小为99GB十六进制0x63  
![image](https://image.3001.net/images/20220708/1657257938_62c7bfd278abbebd80434.jpg!small)

如果以上反调试检测都通过，接着使用IsDebuggerPresent检测本进程是否被调试，还调用了time_Since函数和函数开头的time_Now函数组合检测函数运行时间判断进程是否被调试  
![image](https://image.3001.net/images/20220708/1657257962_62c7bfea5718bb25a80c5.jpg!small)

checkLocation函数使用GET请求`hxxps://json[.]geoiplookup[.]io`网站获取json格式的公网IP归属地，但是此网站屏蔽了ASN为4134的IP地址所以这里返回值为错误代码  
![image](https://image.3001.net/images/20220708/1657258118_62c7c086dcb233674d33b.jpg!small)

正常如果获取到了本机IP归属地会和列表中的地区进行比较，我们可以看到此列表中，只有两个具体的地区伦敦和俄罗斯在这两个中间的单词都为一些少儿不宜的话  
![image](https://image.3001.net/images/20220708/1657258146_62c7c0a268d8f7efc6450.jpg!small)

一共对比了列表中7个单词，从2到6个单词可以猜测此恶意软件的作者可能是个种族歧视主义者  
![image](https://image.3001.net/images/20220708/1657258216_62c7c0e8d87bc316e7ea6.jpg!small)

调用strings_Index函数进行逐一对比  
![image](https://image.3001.net/images/20220708/1657258233_62c7c0f9d94df76604cde.jpg!small)

checkLocation函数检测如果IP归属地不在列表中则会调用downloadNerbian函数从C2服务器下载NerbianRAT主体程序  
![image](https://image.3001.net/images/20220708/1657258328_62c7c1580799f6582f8e0.jpg!small)

分析downloadNerbian函数，此函数首先会使用RedFile函数打开`C:\\ProgramData\\USOShared\\MoUsoCore.exe`路径中的文件  
![image](https://image.3001.net/images/20220708/1657258347_62c7c16bd417e37c77768.jpg!small)

如果文件不存在则会从C2下载，如果存在此文件还会判断此文件前两个字节是否为4D5A（MZSignature）用于判断此文件是否为PE文件  
![image](https://image.3001.net/images/20220708/1657258411_62c7c1ab37b731f7d0bc8.jpg!small)

调用downloadFile函数从C2下载NerbianRAT  
![image](https://image.3001.net/images/20220708/1657258501_62c7c205f3651029fe8db.jpg!small)

如果首次从C2下载失败，还会调用cmd使用curl从C2下载  
![image](https://image.3001.net/images/20220708/1657258551_62c7c2371fa4d0b6026ea.jpg!small)

从C2下载完成后都会读取文件并检测文件头两个字节是否为4D5A（MZSignature）判断是否为PE文件  
![image](https://image.3001.net/images/20220708/1657258593_62c7c261a8b0c0e3bdc13.jpg!small)

最后一个函数是创建计划任务实现持久化运行，首先通过CMD调用格式化好的命令创建计划任务  
![image](https://image.3001.net/images/20220708/1657258611_62c7c27315292770c92c3.jpg!small)

我们可以打开计划任务查看，可以看到触发条件是每隔1小时运行一次  
![image](https://image.3001.net/images/20220708/1657258626_62c7c2828471888bd3555.jpg!small)

触发操作就是启动从C2下载的NerbianRAT  
![image](https://image.3001.net/images/20220708/1657258641_62c7c291588bf3d3decbe.jpg!small)

如果创建计划任务成功则直接触发执行运行NerbianRAT，至此UpdateUAV.exe这个dropper程序就分析完成  
![image](https://image.3001.net/images/20220708/1657258700_62c7c2ccc157db6b96b7b.jpg!small)

### 4.3 MoUsoCore.exe分析

接下来我们分析NerbianRAT主体程序，NerbianRAT一样使用了UPX压缩壳还是一样的流程脱壳，此样本去除大部分的符号信息，不过我们还是可以通过搜索`github`关键词查找MoUsoCore.exe的函数可以查看使用的go开源包，通过如下这些包可以大致判断出NerbianRAT的大致功能

    
    
    smbios包提供对系统管理BIOS(SMBIOS)和桌面管理接口(DMI)数据和结构的检测和访问：github[.]com/digitalocean/go-smbios
    Windows WMI提供了WQL接口：github[.]com/StackExchange/wmi
    桌面截图：github[.]com/kbinani/screenshot
    go的WindowsAPI封装：github[.]com/AllenDang/w32
    golang的win32 ole实现：github[.]com/go-ole/go-ole
    go的WindowsAPI封装：github[.]com/lxn/win
    

golang有一种特殊的函数初始化函数，定义格式`fcun
init()`，此函数会在main函数之前执行，并且同一个包可以定义多个init函数，编译时编译器会自动更名，这里可以看到main包中一共有两个init初始化函数  
![image](https://image.3001.net/images/20220708/1657258874_62c7c37a14c976b6944af.jpg!small)

其中的main_init_0使用了硬编码的AesGCM加密模式的密钥解密了很多需要使用到的字符串  
![image](https://image.3001.net/images/20220708/1657258895_62c7c38f8f7eb20b204b9.jpg!small)

调用gcmAsm_open解密  
![image](https://image.3001.net/images/20220708/1657258916_62c7c3a45c524533586af.jpg!small)

可以看到解密出来的是一个ip地址此地址应该是和C2相关的，接下来还进行了多次解密出剩下的加密字符串  
![image](https://image.3001.net/images/20220708/1657258935_62c7c3b794074e92e5725.jpg!small)

下面开始分析main函数，第一个函数调用main_I4JkbFMH还是个进程检测名单  
![image](https://image.3001.net/images/20220708/1657258961_62c7c3d14dfcc67c2f337.jpg!small)

使用了github开源的StackExchange包通过WQL语句`SELECT * FROM Win32_Process`查询了本机进程  
![image](https://image.3001.net/images/20220708/1657258989_62c7c3edf31dbb2e23ba8.jpg!small)

对比进程黑名单列表  
![image](https://image.3001.net/images/20220708/1657259011_62c7c403028ff6361283d.jpg!small)

接下来分析main_H5NzwUxN函数，首先获取了本机BIOS信息，然后对获取到的BIOS信息使用MD5算法进行了哈希  
![image](https://image.3001.net/images/20220708/1657259038_62c7c41e14676a56c0205.jpg!small)

然后将MD5值类型转换成16进制  
![image](https://image.3001.net/images/20220708/1657259062_62c7c4364a90da89ad4ff.jpg!small)

接着使用getCurrentProcessId函数获取了本进程的PID并同样对PID使用MD5进行哈希  
![image](https://image.3001.net/images/20220708/1657259080_62c7c448c5073728dd2cb.jpg!small)

同样的将MD5值类型转换为16进制  
![image](https://image.3001.net/images/20220708/1657259099_62c7c45beea1d7cba6620.jpg!small)

接着生成了一个唯一ID  
![image](https://image.3001.net/images/20220708/1657259121_62c7c47109afd393d4e78.jpg!small)

接着将生成的唯一ID转为大写字母  
![image](https://image.3001.net/images/20220708/1657259137_62c7c4810e9d79a3fdc4d.jpg!small)

函数main_H5NzwUxN获取收集了主机名称等信息  
![image](https://image.3001.net/images/20220708/1657259164_62c7c49c2eb49f9f77ae3.jpg!small)

函数main_JgJWgOp中调用ReadFile函数读取了`args_c.txt`文件如果不存在此文件则跳转，暂不清楚此文件的作用可能是后期存储收集到的信息  
![image](https://image.3001.net/images/20220708/1657259546_62c7c61a0afb152370da4.jpg!small)

函数main_ZPBgbOEQ读取了`C:\ProgramData\Microsoft
OneDrive\setup\rev.sav`文件，此文件可能也是用来存储一些收集到的数据  
![image](https://image.3001.net/images/20220708/1657259573_62c7c635baa97cd263b27.jpg!small)

接下来main_DNKvpcvy函数实现了加解密和收发网络请求，首先格式化了一个IP地址，此地址可能是C2服务器IP地址  
![image](https://image.3001.net/images/20220708/1657259600_62c7c6503164831accff0.jpg!small)

向C2`hxxps://www[.]fernandestechnical[.]com/pub/health_check[.]php`发送Get请求判断C2是否存活  
![image](https://image.3001.net/images/20220708/1657259624_62c7c668ba061757c01e0.jpg!small)

向C2发送Get请求  
![image](https://image.3001.net/images/20220708/1657260341_62c7c935a3a4a7e78e81a.jpg!small)

C2返回状态码200则C2存活  
![image](https://image.3001.net/images/20220708/1657259642_62c7c67aea5235db84d8d.jpg!small)

C2和本机的keep-alive心跳包  
![image](https://image.3001.net/images/20220708/1657260431_62c7c98f0591f2145b7be.jpg!small)

获取了本地IP地址  
![image](https://image.3001.net/images/20220708/1657259657_62c7c689b45e6748af649.jpg!small)

接下来使用RSA-2048加密了0x98大小的内容  
![image](https://image.3001.net/images/20220708/1657259676_62c7c69c1e1b394686623.jpg!small)

RSA公钥为硬编码  
![image](https://image.3001.net/images/20220708/1657259798_62c7c71646984ac9881ad.jpg!small)

RSA加密后的Buff为0x100  
![image](https://image.3001.net/images/20220708/1657259815_62c7c727c9b7bcde5c904.jpg!small)

然后拼接了0x14C大小的缓冲区  
![image](https://image.3001.net/images/20220708/1657259834_62c7c73a42d12beddcef3.jpg!small)

接下来使用了AesCBC模式加密，使用补全码0x4填充了4字节到0x150大小  
![image](https://image.3001.net/images/20220708/1657259853_62c7c74d8b2f55c5b5586.jpg!small)

使用了硬编码的32字节Aes密钥进行加密  
![image](https://image.3001.net/images/20220708/1657259880_62c7c7689ab0e88463a97.jpg!small)

使用硬编码的AesCBC密钥加密后数据  
![image](https://image.3001.net/images/20220708/1657259903_62c7c77fdf3a46bce8996.jpg!small)

将随机生成的0x10大小的数据写入AesCBC加密后的缓冲区头部  
![image](https://image.3001.net/images/20220708/1657259919_62c7c78fb75888e538e94.jpg!small)

再次拼接将8563写入缓冲区头部  
![image](https://image.3001.net/images/20220708/1657259938_62c7c7a2bd5db5113e961.jpg!small)

函数main_P6EwC8SB是对auth_post、data_post、addr_post、port_post字段数据进行加密的函数，此AesCBC模式加密密钥是随机生成的32字节  
![image](https://image.3001.net/images/20220708/1657259961_62c7c7b9f3ebc99a283ef.jpg!small)

使用AesCBC模式加密后  
![image](https://image.3001.net/images/20220708/1657259979_62c7c7cb545f699d18afb.jpg!small)

接着生成了70个字节的随机数  
![image](https://image.3001.net/images/20220708/1657259997_62c7c7dd53754aaa1242d.jpg!small)

使用Base64对AesCBC模式加密后的数据进行编码  
![image](https://image.3001.net/images/20220708/1657260014_62c7c7ee0bf987d68009a.jpg!small)

将随机生成的70个字节数据填充到头部，将AesCBC模式加密使用的32字节大小随机生成密钥存放在70个字节数据之后，后面的数据为Base64编码后的加密数据  
![image](https://image.3001.net/images/20220708/1657260040_62c7c80808356b9d4aa49.jpg!small)

函数main_GNd3j2oz就是生成session_key字段的数据，首先调用了go-smbios包获取bios硬件信息，并使用MD5哈希  
![image](https://image.3001.net/images/20220708/1657260059_62c7c81baf55be02230c3.jpg!small)

将MD5转为十六进制  
![image](https://image.3001.net/images/20220708/1657260075_62c7c82b0abaf3b5b01a2.jpg!small)

之后将0x40字节大小的全局变量和bios信息MD5值和字符串windows进行格式化，随后直接使用Base64对这些数据进行了编码  
![image](https://image.3001.net/images/20220708/1657260116_62c7c85444d193ba4289a.jpg!small)

拼接好要发送的POST请求数据  
![image](https://image.3001.net/images/20220708/1657260136_62c7c868adfcf5182075e.jpg!small)

发送POST请求到C2  
![image](https://image.3001.net/images/20220708/1657260151_62c7c8771d7b75feeb08a.jpg!small)

屏幕截图功能使用了screenshot开源库实现  
![image](https://image.3001.net/images/20220708/1657260167_62c7c887a9532b514f244.jpg!small)

屏幕截图功能  
![image](https://image.3001.net/images/20220708/1657260183_62c7c8973238dc38a2d7a.jpg!small)

这里我使用了golang编写了解密脚本，除了session_key这个数据单单使用了Base64编码，其他的4个字段的数据都可以使用这个脚本解密，auth_post和data_post使用了3层加密，第一层的数据使用了RSA-2048进行加密，第二层req使用了硬编码的AesCBC密钥加密，第三层8563使用了随机生成的AesCBC加密，所以我们最多可以解密两层

    
    
    package main
    
    import (
    	"crypto/aes"
    	"crypto/cipher"
    	"encoding/base64"
    	"fmt"
    )
    
    func main() {
        // addr_post字段加密数据
    	allcryptDataBase64 := "EcgOPkkOHFylaFoLaqoXmbKPGOzvddbJMlnTtEtlScAdeewEFwzdITJsRYdYEushByrcQJCtuqdlGSeQyCjNieJBeQSnVwNcDhtQrh06LdGa3uyRHexahEL05goQ=="
    	// 加密数据前70个字节为垃圾数据，垃圾数据后的32个字节为AesCBC加密密钥
    	aesCBCKey := allcryptDataBase64[70 : 70+32]
    	// 需要解密的数据为70垃圾字节+32字节的AesCBC密钥后面的Base64编码数据
    	cryptDataBase64 := allcryptDataBase64[70+32:]
    	// 将加密数据进行Base64解码
    	cryptData, _ := base64.StdEncoding.DecodeString(string(cryptDataBase64))
    	// 使用AesCBC解密数据
    	decryptData := AesDecryptCBC(cryptData, []byte(aesCBCKey))
    	// 打印解密数据
    	fmt.Printf("%x\n", decryptData)
    	// 解密第二层数据：解密auth_post和data_post数据时再调用
    	DecryptoSecData(decryptData)
    }
    
    func DecryptoSecData(decryptData []byte) {
    	// 解密第二层加密
    	// 硬编码AesCBCKey
    	gaesCBCKeyBase64 := "F+h/WB8d+NYSnWX9UM6z3WxOHCIwd819TFldpsPfkrI="
    	// 解码第二层硬编码的AesCBC密钥
    	gaesCBCKey, _ := base64.StdEncoding.DecodeString(string(gaesCBCKeyBase64))
    	// 第二层要解密的数据
    	secCryptData := decryptData[8:]
    	// 使用AesCBC解密数据
    	secDecryptData := AesDecryptCBC(secCryptData, []byte(gaesCBCKey))
    	fmt.Println("第二层数据解密--------------------------------------")
    	// 打印解密数据
    	fmt.Printf("%x", secDecryptData)
    }
    
    // AesCBC模式解密函数
    func AesDecryptCBC(encrypted []byte, key []byte) (decrypted []byte) {
    	// 分组密钥
    	block, _ := aes.NewCipher(key)
    	// 获取密钥块的长度
    	blockSize := block.BlockSize()
    	// 加密模式
    	blockMode := cipher.NewCBCDecrypter(block, key[:blockSize])
    	// 创建数组
    	decrypted = make([]byte, len(encrypted))
    	// 解密
    	blockMode.CryptBlocks(decrypted, encrypted)
    	// 去除补全码
    	decrypted = PKCS5UnPadding(decrypted)
    	return decrypted
    }
    
    // 去除补全码
    func PKCS5UnPadding(origData []byte) []byte {
    	length := len(origData)
    	unpadding := int(origData[length-1])
    	return origData[:(length - unpadding)]
    }
    

## 5.总结

NerbianRAT使用了现在主要的恶意软件传播方式之一为通过邮件附件的带VBA宏脚本的word文档进行传播，甚至不乏很多境外APT组织也使用此方式针对性攻击，go这种跨平台的编译型编程语言正被越来越多的恶意软件开发者采用，go众多的开源包可以实现快速开发，NerbianRAT使用了众多的反逆向和反虚拟机功能加大了分析的时间和难度，并且使用了RSA和AES组合的加密手段用来传输数据，对于此类传播方式的恶意软件能做的只有加强邮件地址过滤和附件检测和加大信息安全教育普及。

