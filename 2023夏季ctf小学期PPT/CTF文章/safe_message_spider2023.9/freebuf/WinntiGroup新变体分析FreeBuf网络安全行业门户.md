**2020年2月发现Winnti
Group新的模块化后门PipeMon。其主要目标是韩国和台湾多人在线游戏和视频公司，恶意软件可发起对供应链的攻击。攻击者可在发行的游戏中植入木马，或攻击游戏服务器，利用游戏货币获取经济利益。Winnti
Group从2012年以来一直保持活跃，该组织针对软件行业供应链攻击。最近ESET研究人员还发现了其针对香港几所大学的攻击。**

## 技术分析

在目标公司中发现了PipeMon的两个变体，PipeMon的第一阶段包括启动嵌入在.rsrc中受密码保护的可执行文件。
启动程序将RARSFX会在自动生成目录下写入setup0.exe，通过参数提供密码，利用CreateProcess执行RARSFX，如下所示：

    
    
    setup0.exe -p*|T/PMR{|T2^LWJ*          

每个样本的密码都不相同，然后将RARSFX的内容提取到%TMP%\RarSFX0中：

> CrLnc.dat – 加密负载
>
> Duser.dll – UAC bypass
>
> osksupport.dll – UAC bypass
>
> PrintDialog.dll – 恶意软件初始化
>
> PrintDialog.exe – 加载PrintDialog.dll的合法Windows文件
>
> setup.dll – 安装dll
>
> setup.exe – 主程序

如果文件夹名发生冲突，RarSFX0字符串末尾的数字将递增，直到没有冲突为止。提取文件后，setup.exe将不带参数地执行，使用LoadLibraryA加载setup.dll。
加载后，setup.dll将检查形如‘–x:n’的参数，n不同操作模式也不同。表1中显示了支持的参数及其相应的行为。

![](https://image.3001.net/images/20200527/1590582907_5ece5e7bb70ad.png!small)

RARSFX在不带参数的情况下执行setup.exe，检查它是否以特权运行。 如果不是，进一步判断Windows版本是否低于Windows 7 build
7601，如果符合条件则会利用[token impersonation]()获取权限。 否则它将尝试使用不同的UAC
bypass技术，可将有效载荷加载安装到以下其中一项中：

> C:\Windows\System32\spool\prtprocs\x64\DEment.dll
>
> C:\Windows\System32\spool\prtprocs\x64\EntAppsvc.dll
>
> C:\Windows\System32\spool\prtprocs\x64\Interactive.dll

攻击者并不是随机选择恶意DLL的位置，setup.dll通过设置以下注册表值将DLL加载程序注册为备用打印器：  

> HKLM\SYSTEM\ControlSet001\Control\Print\Environments\Windows x64\Print
> Processors\PrintFiiterPipelineSvc\Driver = “DEment.dll”  
>
>
> HKLM\SYSTEM\CurrentControlSet\Control\Print\Environments\Windows x64\Print
> Processors\lltdsvc1\Driver = “EntAppsvc.dll”  
>

请注意PrintFiiterPipelineSvc中的拼写错误（由于可以使用任何名称，因此对打印处理器的安装没有影响）。

注册打印处理器后，PipeMon重新启动打印后台处理服务（spoolsv.exe），将加载恶意打印进程。 Print
Spooler服务会在每次PC启动时启动，从而确保了恶意程序的持久性。根据安装程序的不同，会将CrLnc.dat写入注册表中的以下位置：

>
> HKLM\SOFTWARE\Microsoft\Print\Components\DC20FD7E-4B1B-4B88-8172-61F0BED7D9E8
>
> HKLM\SOFTWARE\Microsoft\Print\Components\A66F35-4164-45FF-9CB4-69ACAA10E52D

整个PipeMon执行过程如下图所示：  

##
![](https://image.3001.net/images/20200527/1590583525_5ece60e504ac0.png!small)PipeMon  

PipeMon是一个模块化后门，每个模块都是一个DLL，可导出IntelLoader函数，使用反射加载技术进行加载。每个模块具有不同的功能，如表2所示。

![](https://image.3001.net/images/20200527/1590583606_5ece6136ba3a9.png!small)

  

负责加载主要模块（ManagerMain和GuardClient）的加载程序是Win32CmdDll.dll，位于打印处理器目录中。这些模块以加密的方式存储在相同位置，其命名如下：

> banner.bmp
>
> certificate.cert
>
> License.hwp
>
> JSONDIU7c9djE
>
> D8JNCKS0DJE
>
> B0SDFUWEkNCj.logN

.hwp是韩文文字处理程序使用的扩展名，在韩国非常流行。模块经过R**加密，解密密钥‘Com！123Qasdz’会硬编码在每个模块之中。
Win32CmDll.dll解密并注入ManagerMain和GuardClient模块。
ManagerMain模块负责解密和注入Communication模块，而GuardClient模块将确保Communication模块正在运行，并在必要时重新加载。下图概述了PipeMon的工作方式。

![](https://image.3001.net/images/20200527/1590583814_5ece620600b93.png!small)

Win32CmDll.dll首先尝试将ManagerMain和GuardClient模块注入以下名称之一的进程中：lsass.exe，wininit.exe或lsm.exe。如果失败，它将尝试注入已注册的Windows服务进程之一，但不包括名为spoolsv.exe，ekrn.exe（ESET），avp.exe（Kaspersky）或dllhost.exe的进程。如果所有操作均失败，它将尝试进程taskhost.exe，taskhostw.exe或explorer.exe。

可以使用专用命令按需加载其他模块，但是还没有发现其中的任何模块。模块间通过命名管道通信，每个模块之间通信通道使用两个命名管道，一个用于发送，一个用于接收。

![](https://image.3001.net/images/20200527/1590584213_5ece63953f0a3.png!small)从C＆C服务器收到％CNC_DEFINED％字符串，变量％B64_TIMESTAMP％是base64编码的时间戳：  

![](https://image.3001.net/images/20200527/1590584264_5ece63c8c49a9.png!small)

通讯模块负责通过管道管理C＆C服务器与其他模块之间的通讯，其C＆C地址硬编码在ManagerMain模块中。通信协议是基于TCP的TLS，通过HP-Socket库处理。 所有消息均使用硬编码密钥进行R**加密。如果传输内容大于或等于4KB，则先使用zlib对其进行压缩。

![](https://image.3001.net/images/20200527/1590584556_5ece64ec4e792.png!small)启动与C＆C服务器的通信，首先发送信标消息，其中包含以下信息：

> OS version
>
> physical addresses of connected network adapters concatenated with
> %B64_TIMESTAMP%
>
> victim’s local IP address
>
> backdoor version/campaign ID; we’ve observed the following values
>
> “1.1.1.4beat”
>
> “1.1.1.4Bata”
>
> “1.1.1.5”
>
> Victim computer name

支持的命令如下表：  

![](https://image.3001.net/images/20200527/1590584874_5ece662a6b9f2.png!small)

攻击者还使用了PipeMon的更新版本，R**替换为简单的XOR，以0x75E8EEAF作为密钥，删除了所有硬编码的字符串，使用随机值命名模块间通信管道。只有主加载程序作为文件存储在磁盘上，更新的模块如下表描述：

![](https://image.3001.net/images/20200527/1590585067_5ece66ebd5073.png!small)C&C
通信格式发生变化：  

![](https://image.3001.net/images/20200527/1590585099_5ece670b106c9.png!small)后门配置被加密并嵌入到加载程序DLL中。  

![](https://image.3001.net/images/20200527/1590585165_5ece674d99e29.png!small)PipeMon模块和安装程序都使用相同的签名，该证书可能是Winnti组织在上一次攻击中盗取的。  

##
![](https://image.3001.net/images/20200527/1590585227_5ece678b420c5.png!small)IOCs

### ESET detection names

Win64/PipeMon.A

Win64/PipeMon.B

Win64/PipeMon.C

Win64/PipeMon.D

Win64/PipeMon.E

### Filenames

100.exe

103.exe

Slack.exe

setup.exe

%SYSTEM32%\spool\prtprocs\x64\DEment.dll

%SYSTEM32%\spool\prtprocs\x64\EntAppsvc.dll

%SYSTEM32%\spool\prtprocs\x64\Interactive.dll

%SYSTEM32%\spool\prtprocs\x64\banner.bmp

%SYSTEM32%\spool\prtprocs\x64\certificate.cert

%SYSTEM32%\spool\prtprocs\x64\banner.bmp

%SYSTEM32%\spool\prtprocs\x64\License.hwp

%SYSTEM32%\spool\prtprocs\x64\D8JNCKS0DJE

%SYSTEM32%\spool\prtprocs\x64\B0SDFUWEkNCj.log

%SYSTEM32%\spool\prtprocs\x64\K9ds0fhNCisdjf

%SYSTEM32%\spool\prtprocs\x64\JSONDIU7c9djE

%SYSTEM32%\spool\prtprocs\x64\NTFSSSE.log

AceHash64.exe

mz64x.exe

### Named pipes

\\\\.\pipe\ScreenPipeRead%CNC_DEFINED%

\\\\.\pipe\ScreenPipeWrite%CNC_DEFINED%

\\\\.\pipe\RoutePipeWriite%B64_TIMESTAMP%

\\\\.\pipe\MainPipeWrite%B64_TIMESTAMP%

\\\\.\pipe\MainPipeRead%B64_TIMESTAMP%

\\\\.\pipe\MainHeatPipeRead%B64_TIMESTAMP%

\\\\.\pipe\InCmdPipeWrite%B64_TIMESTAMP%

\\\\.\pipe\InCmdPipeRead%B64_TIMESTAMP%

\\\\.\pipe\FilePipeRead%B64_TIMESTAMP%

\\\\.\pipe\FilePipeWrite%B64_TIMESTAMP%

\\\\.\pipe\ComHeatPipeRead%B64_TIMESTAMP%

\\\\.\pipe\CMDPipeRead

\\\\.\pipe\CMDPipeWrite

### Registry

HKLM\SYSTEM\ControlSet001\Control\Print\Environments\Windows x64\Print
Processors\PrintFiiterPipelineSvc\Driver = “DEment.dll”

HKLM\SYSTEM\CurrentControlSet\Control\Print\Environments\Windows x64\Print
Processors\lltdsvc1\Driver = “EntAppsvc.dll”

HKLM\SOFTWARE\Microsoft\Print\Components\DC20FD7E-4B1B-4B88-8172-61F0BED7D9E8

HKLM\SOFTWARE\Microsoft\Print\Components\A66F35-4164-45FF-9CB4-69ACAA10E52D

### Samples

 **First stage**

4B90E2E2D1DEA7889DC15059E11E11353FA621A6

C7A9DCD4F9B2F26F50E8DD7F96352AEC7**123FE

3508EB2857E279E0165DE5AD7BBF811422959158

729D526E75462AA8D33A1493B5A77CB28DD654BC

5663AF9295F171FDD41A6D819094A5196920AA4B

 **PipeMon**

23789B2C9F831E385B22942DBC22F085D62B48C7

53C5AE2655808365F1030E1E06982A7A6141E47F

E422CC1D7B2958A59F44EE6D1B4E10B524893E9D

5BB96743FEB1C3375A6E2660B8397C68BEF4AAC2

78F4ACD69DC8F9477CAB9C732C91A92374ADCACD

B56D8F826FA8E073E6AD1B99B433EAF7501F129E

534CD47EB38FEE7093D24BAC66C2CF8DF24C7D03

 **PipeMon encrypted binaries**

168101B9B3B512583B3CE6531CFCE6E5FB581409

C887B35EA883F8622F7**8EC9D0427AFE833BF46

44D0A2A43ECC8619DE8DB99C1465DB4E3C8FF995

E17972F1A3C667EEBB155A228278AA3B5F89F560

C03BE8BB8D03BE24A6C5CF2ED14EDFCEFA8E8429

2B0481C61F367A99987B7EC0ADE4B6995425151C

### Additional tools

 **WinEggDrop**

AF9C220D177B0B54A790C6CC135824E7C829B681

 **Mimikatz**

4A240EDEF042AE3CE47E8E42C2395DB43190909D

 **Netcat**

751A9CBFFEC28B22105CDCAF073A371DE255F176

 **HTran**

48230228B69D764F71A7BF8C08C85436B503109E

 **AceHash**

D24BBB898A4A301870CAB85F836090B0FC968163

### Code-signing certificate SHA-1 thumbprints

745EAC99E03232763F98FB6099F575DFC7BDFAA3

2830DE648BF0A521320036B96CE0D82BEF05994C

### C&C domains

n8.ahnlabinc[.]com

owa.ahnlabinc[.]com

ssl2.ahnlabinc[.]com

www2.dyn.tracker[.]com

ssl2.dyn-tracker[.]com

client.gnisoft[.]com

nmn.nhndesk[.]com

ssl.lcrest[.]com

### C&C IP addresses

154.223.215[.]116

203.86.239[.]113

 ***参考来源：[welivesecurity](https://www.welivesecurity.com/2020/05/21/no-game-over-winnti-group/)，由Kriston编译，转载请注明来自FreeBuf.COM **  

