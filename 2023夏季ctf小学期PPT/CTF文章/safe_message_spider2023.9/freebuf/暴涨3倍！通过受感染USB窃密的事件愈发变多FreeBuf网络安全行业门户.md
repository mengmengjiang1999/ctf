2023 年上半年，Mandiant 观察到使用受感染 USB 驱动器窃取机密数据的事件至少增加了3倍。此前，Mandiant
披露了在菲律宾的一次攻击行动。本文将会介绍研究人员发现的两外两次基于 USB 驱动器的网络间谍行动。

 **通过 USB 闪存驱动器感染 SOGU 恶意软件**

这是使用 USB 闪存驱动器的间谍攻击，也是针对全球各行业垂直领域的公共与私营部门的攻击行动。攻击者使用 USB 闪存驱动器加载 SOGU
恶意软件，来窃取主机的敏感信息。

Mandiant 将攻击行动归因于 TEMP.Hex
攻击团伙，针对欧洲、亚洲与美国的多个行业进行攻击，对建筑、工程、商业服务、政府、卫生、运输与零售行业构成威胁。

 **通过 USB 闪存驱动器传播 SNOWYDRIVE 恶意软件**

攻击者使用 USB 闪存驱动器传播 SNOWYDRIVE
恶意软件。一旦加载成功，就会在失陷主机上创建后门，攻击者可以远程发送命令，使恶意软件传播到其他闪存驱动器上以在整个网络中扩散。

Mandiant 将攻击行动归因于 UNC4698，这是一个针对亚洲石油与天然气公司进行攻击的团伙。一旦获取了访问权限，就可以执行任意命令、修改注册表等。

## SOGU 恶意软件

研究人员首先发现该攻击行动，在攻击者用于存放恶意软件、攻击工具或实用程序的开放目录中寻找可疑文件写入。

![image.png-344.5kB](https://image.3001.net/images/20230713/1689228161_64af938147a5799a4852e.png!small)受害者国家分布

![image.png-212.8kB](https://image.3001.net/images/20230713/1689228162_64af938202eb99e5417a0.png!small)受害者行业分布

### 最初的感染

受感染的 USB 闪存驱动器是最初始的感染媒介，其中包含多个恶意软件，旨在通过 DLL 劫持将恶意 Payload 加载到内存中。

![image.png-136.6kB](https://image.3001.net/images/20230713/1689228162_64af9382cdfbfe55dacdc.png!small)攻击链

### 立足点

完整的感染链通常由三个文件组成：合法的可执行文件、恶意 DLL 加载文件与加密的 Payload 文件。如下显示了整个攻击周期发现的恶意软件文件与路径：

![image.png-43.6kB](https://image.3001.net/images/20230713/1689228163_64af938373354d20cd883.png!small)常利用的合法可执行文件为安全软件

在合法的可执行文件执行时，会加载一个恶意 DLL 文件（KORPLUG）。随后 KORPLUG 将会加载加密的 dat 文件中的 Shellcode
数据，并在内存中执行。Shellcode 是一个用 C 语言编写的后门，被命名为 SOGU。

### 侦察

通过将批处理文件放入 RECYCLE.BIN 路径下继续进行侦察。该批处理文件会探测主机并将结果输出到名为 c3lzLmluZm8 的文件中。通过
base64 解码后，c3lzLmluZm8 为 sys.info。脚本执行以下命令收集系统特定元数据：

  * tasklist /v
  * arp -a
  * netstat -ano
  * ipconfig /all
  * systeminfo

随后，恶意软件会在 C 盘检索以下扩展名的文件：

  * .doc
  * .docx
  * .ppt
  * .pptx
  * .xls
  * .xlsx
  * .pdf

恶意软件会加密每个文件的副本，并且使用 base64 对原始文件名进行编码，再将加密的文件放入以下目录：

  * C:\Users\\\AppData\Roaming\Intel\\\
  * :\RECYCLER.BIN\\\

### 持久化

为了保持持久化，恶意软件需要创建一个伪装成合法程序的目录，并将该目录的属性设置为隐藏。然后，将主要组件都复制到该目录下。常用的文件路径如下所示：

  * C:\ProgramData\AvastSvcpCP
  * C:\ProgramData\AAM UpdatesHtA
  * C:\ProgramData\AcroRd32cWP
  * C:\ProgramData\Smadav\SmadavNSK

随后创建一个与之前创建的目录同名的 Run 注册表项，该表项用于在用户登录时自动运行程序：

  * Value: AvastSvcpCP
  * Text: C:\ProgramData\AvastSvcpCP\AvastSvc.exe
  * Value: AAM UpdatesHtA
  * Text: C:\ProgramData\AAM UpdatesHtA\AAM Updates.exe
  * Value: AcroRd32cWP
  * Text: C:\ProgramData\AcroRd32cWP\AcroRd32.exe
  * Value: SmadavNSK
  * Text: C:\ProgramData\Smadav\SmadavNSK\Smadav.exe

某些 SOGU 变种，可能会创建一个额外的计划任务（SCHTASKS.exe /create /sc minute /mo 10 /tn "Autodesk
plugin" /tr """"C:\ProgramData\Smadav\SmadavNSK\Smadav.exe""" 644"
/f）。每十分钟运行一次恶意软件，以进行持久化。

### 完成任务

攻击的最后阶段，恶意软件将会回传所有数据。通信使用 HTTP、HTTPS、TCP 或者 UDP 的自定义协议以及
ICMP。该恶意软件还支持多种命令，包括文件传输、文件执行、远程桌面、屏幕截图、反向 Shell 与键盘记录。

该恶意软件还可以复制到失陷主机新的可移动设备上，使恶意软件能够传播到其他设备，这样也能够穿越气隙网络回传数据。

## SNOWYDRIVE 攻击亚洲石油与天然气公司

用户被引诱在 USB 驱动器上执行恶意软件时，通常会发现命令行检索可疑文件夹路径。虽然这种类型的威胁并不罕见，但研究人员坚持发现了特殊的间谍行动。

### 最初的感染

受感染的 USB 闪存驱动器是初始感染媒介，受害者被引诱点击为转成合法可执行文件的恶意软件。执行后，就会触发一系列恶意行为。

![image.png-587.2kB](https://image.3001.net/images/20230713/1689228164_64af93841c45262f2e180.png!small)攻击链

### 立足点

感染链通常从可执行文件开始，将恶意文件写入磁盘并启动。例如，名为 USB Drive.exe 的恶意程序将以下加密文件写入
C:\Users\Public\SymantecsThorvices\Data：

  * aweu23jj46jm7dc
  * bjca3a0e2sfbs
  * asdigasur3ase
  * sf33kasliaeae
  * sf24acvywsake

加密文件包含在目录 C:\Users\Public\SymantecsThorvices\Bin 中提取与写入的可执行文件和 DLL 文件。

![image.png-176.6kB](https://image.3001.net/images/20230713/1689228164_64af9384e397f166d5874.png!small)组件情况

这些文件一共分为四个部分，每部分都是由合法的可执行文件通过 DLL 顺序劫持加载的恶意 DLL 文件组成。如下所示，每个组件负责攻击中的一部分任务。

![image.png-137.6kB](https://image.3001.net/images/20230713/1689228165_64af9385932a0a3e583a0.png!small)组件列表

### 命令与控制

名为 SNOWYDRIVE 的基于 Shellcode 的后门会根据系统名称、用户名与卷序列号生成唯一标识。该标识符会在 C&C 通信时被当成唯一
ID，而且 C&C 域名通常被硬编码在 Shellcode 中。

![image.png-480.5kB](https://image.3001.net/images/20230713/1689228166_64af93864b86f7d4bf6a9.png!small)硬编码域名

后门支持以下命令：

![image.png-64.4kB](https://image.3001.net/images/20230713/1689228170_64af938aed372ae1445ee.png!small)支持命令

### 持久化

恶意软件使用 HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run\ushsguaei1hgba
注册表项进行持久化，存储 Silverlight.Configuration.exe 的路径。

### 横向平移

该恶意软件会将自身复制并插入失陷主机的可移动驱动器中。首先创建文件夹 `<drive_root>\Kaspersky\Usb
Drive\3.0`，再复制包含恶意组件的加密文件。从文件 `aweu23jj46jm7dc`中提取可执行文件并写入
`<drive_root>\<volume_name> .exe`，该文件负责提取并执行加密文件的内容。

## 影响

Mandiant 确定打印店、印刷店与酒店都是攻击的重点，这些攻击可能都是长期收集信息的一部分，也可能是针对国家级攻击者后续行动的一部分。

组织应该优先考虑对 USB 驱动器等外部设备的访问进行限制，如果不能限制则至少应该先扫描是否存在恶意代码。

## Yara

### SOGU

    
    
    rule M_Code_SOGU{meta:author = "Mandiant"description = "Hunting rule for SOGU"sha256 = "8088b1b1fabd07798934ed3349edc468062b166d5413e59e78216e69e7ba58ab"strings:$sb1 = { 8B [2] C7 ?? 01 03 19 20 8B [2] C7 ?? 04 01 10 00 00 8B [2] C7 ?? 08 00 00 00 00 8B [2] C7 ?? 0C 00 00 00 00 0F B7 }$sb2 = { 8B ?? 0C C7 ?? 01 03 19 20 8B ?? 0C C7 ?? 04 00 10 00 00 6A 40 E8 [4] 83 C4 04 8B ?? 0C 89 ?? 08 8B ?? 0C C7 ?? 0C 00 00 00 00 C7 [2] 00 00 00 00 EB 09 8B [2] 83 ?? 01 89 [2] 8B ?? 0C 8B [2] 3? ?? 08 7? ?? 68 FF 00 00 00 E8 [4] 83 C4 04 8B [2] 03 [2] 88 ?? 10 EB D4 }condition:(uint16(0) == 0x5A4D) and (uint32(uint32(0x3C)) == 0x00004550) and (uint16(uint32(0x3C)+0x18) == 0x010B) and all of them}

### FROZENHILL

    
    
    rule M_Code_FROZENHILL {meta:author = "Mandiant"description = "Hunting rule for FROZENHILL"sha256 = "89558b4190abcdc1a2353eda591901df3bb8856758f366291df85c5345837448"strings:$str1 = "path_symantec" ascii$str2 = "symantec_dir" ascii$str3 = "name_svchost" ascii$str4 = "run_cmd" ascii$str5 = "usb_dll_name" ascii$str6 = "name_mutex" ascii$str7 = "cmd /c \"%s\" %d" wide$str8 = { 8B 85 [4] 83 ?? 01 89 85 [4] 8B 85 [4] 3B 45 0C 74 ?? 8B 45 ?? 03 85 [4] 0F B6 08 33 8D [4] 81 E1 [4] 8B 95 [4] C1 EA ?? 33 94 8D [4] 89 95 [4] EB } condition:uint16(0) == 0x5A4D and uint32(uint32(0x3C)) == 0x00004550 and all of them}

### ZIPZAG

    
    
    rule M_Code_ZIPZAG{meta:author = "Mandiant"description = "Hunting rule for ZIPZAG"sha256 = "8a968a91c78916a0bb32955cbedc71a79b06a21789cab8b05a037c8f2105e0aa"strings:$str1 = { C6 45 ?? 55 C6 45 ?? 8B C6 45 ?? EC C6 45 ?? 81 C6 45 ?? EC C6 45 ?? 08 C6 45 ?? 01 C6 45 ?? 00 C6 45 ?? 00 C6 45 ?? C7 C6 45 ?? 45 C6 45 ?? FC C6 45 ?? 78 C6 45 ?? 56 C6 45 ?? 34 C6 45 ?? 12 C6 45 ?? 68 C6 45 ?? 04 C6 45 ?? 01 C6 45 ?? 00 C6 45 ?? 00 C6 45 ?? 8D C6 45 ?? 85 C6 45 ?? F8 C6 45 ?? FE C6 45 ?? FF C6 45 ?? FF C6 45 ?? 50 C6 45 ?? FF C6 45 ?? 75 C6 45 ?? FC C6 45 ?? B8 C6 45 ?? 79 C6 45 ?? 56 C6 45 ?? 34 C6 45 ?? 12 C6 45 ?? FF C6 45 ?? D0 C6 45 ?? FF C6 45 ?? 75 C6 45 ?? FC C6 45 ?? B8 C6 45 ?? 7A C6 45 ?? 56 C6 45 ?? 34 C6 45 ?? 12 C6 45 ?? FF C6 45 ?? D0 C6 45 ?? 8D C6 45 ?? 85 C6 45 ?? F8 C6 45 ?? FE C6 45 ?? FF C6 45 ?? FF C6 45 ?? 50 C6 45 ?? B8 C6 45 ?? 7B C6 45 ?? 56 C6 45 ?? 34 C6 45 ?? 12 C6 45 ?? FF C6 45 ?? D0 C6 45 ?? C9 C6 45 ?? C3 } $str2 = "shellcode_size" asciicondition:uint16(0) == 0x5A4D and uint32(uint32(0x3C)) == 0x00004550 and all of them}

### SNOWYDRIVE

    
    
    rule M_Code_SNOWYDRIVE{meta:author = "Mandiant"description = "Hunting rule for SNOWYDRIVE"sha256 = "964c380bc6ffe313e548336c9dfaabbd01a5519e8635adde42eedb7e1187c0b3"strings:$str1 = { C6 45 ?? 6B C6 45 ?? 65 C6 45 ?? 72 C6 45 ?? 6E C6 45 ?? 65 C6 45 ?? 6C C6 45 ?? 33 C6 45 ?? 32 C6 45 ?? 2E C6 45 ?? 64 C6 45 ?? 6C C6 45 ?? 6C } $str2 = { C6 45 ?? 47 C6 45 ?? 65 C6 45 ?? 74 C6 45 ?? 50 C6 45 ?? 72 C6 45 ?? 6F C6 45 ?? 63 C6 45 ?? 41 C6 45 ?? 64 C6 45 ?? 64 C6 45 ?? 72 C6 45 ?? 65 C6 45 ?? 73 C6 45 ?? 73 } $str3 = { C6 85 ?? FD FF FF 4C C6 85 ?? FD FF FF 6F C6 85 ?? FD FF FF 61 C6 85 ?? FD FF FF 64 C6 85 ?? FD FF FF 4C C6 85 ?? FD FF FF 69 C6 85 ?? FD FF FF 62 C6 85 ?? FD FF FF 72 C6 85 ?? FD FF FF 61 C6 85 ?? FD FF FF 72 C6 85 ?? FD FF FF 79 C6 85 ?? FD FF FF 41 } $str4 = { C6 85 ?? FC FF FF 57 C6 85 ?? FC FF FF 61 C6 85 ?? FC FF FF 69 C6 85 ?? FC FF FF 74 C6 85 ?? FC FF FF 46 C6 85 ?? FC FF FF 6F C6 85 ?? FC FF FF 72 C6 85 ?? FC FF FF 53 C6 85 ?? FD FF FF 69 C6 85 ?? FD FF FF 6E C6 85 ?? FD FF FF 67 C6 85 ?? FD FF FF 6C C6 85 ?? FD FF FF 65 C6 85 ?? FD FF FF 4F C6 85 ?? FD FF FF 62 C6 85 ?? FD FF FF 6A C6 85 ?? FD FF FF 65 C6 85 ?? FD FF FF 63 } condition:uint16(0) != 0x5A4D and uint32(0) != 0x464c457f and uint32(0) != 0xBEBAFECA and uint32(0) != 0xFEEDFACE and uint32(0) != 0xFEEDFACF and uint32(0) != 0xCEFAEDFE and all of them}

### 狩猎规则

    
    
    rule hunting_T1091_User Execution: Malicious File{meta:rule_name = "Replication Through Removable Media"description = "This rule detects a file write event from a RECYCLER/S named path to another directory"author = "Mandiant Managed Defense"mitre_technique_name = "User Execution: Malicious File"mitre_technique = "T1204"mitre_tactic_name = "Execution"platform = "Windows"events:   $e.target.process.path = ":\RECYCLER.BIN\" nocase or$e.target.process.path = ":\RECYCLERS.BIN\" nocase}condition:$e}rule hunting_T1091_Replication_Through_Removable_Media{meta:rule_name = "Replication Through Removable Media"description = "This rule detects windows explorer process execution with a suspicious folder path specified on the command line"author = "Mandiant Managed Defense"mitre_technique_name = "Replication Through Removable Media"mitre_technique = "T1091"mitre_tactic_name = "Lateral Movement,Initial Access"platform = "Windows"events:$e.target.process = "explorer.exe" and{re.regex($e.principal.process.command_line, = `/explorer.exe?(\")?\s+(\")?[A-BD-Za-bd-z]:\\/`) nocase andre.regex($e.principal.process.full_path, `:\\[^\\]+\.exe$`) nocase}condition:$e}

## IOC

> ebb7749069a9b5bcda98d89f04d889db  
> b061d981d224454ffd8d692cf7ee92b7  
> 38baabddffb1d732a05ffa2c70331e21  
> FC55344597d540453326d94eb673e750  
> 028201d92b2b41cb6164430232192062  
> 722b15bbc15845e4e265a1519c800c34  
> ab5d85079e299ac49fcc9f12516243de  
> 848feec343111bc11cceb828b5004aad  
> e1cea747a64c0d74e24419ab1afe1970  
> www.beautyporntube[.]com  
> 45.142.166[.]112  
> 103.56.53[.]46  
> 45.251.240[.]55  
> 43.254.217[.]165

## 参考来源

> [Mandiant](https://www.mandiant.com/resources/blog/infected-usb-steal-> secrets)

