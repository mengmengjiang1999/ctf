MetaStealer 是一个新出现的窃密恶意软件，该恶意软件旨在填补 2022 年 3 月份 Racoon stealer 停止运营带来的市场空白。

以色列暗网情报公司 Kela 的分析人员首先在地下市场确认了 MetaStealer 的出现，紧接着 SANS 确认该恶意软件参与了垃圾邮件攻击。

![image.png-84kB](https://image.3001.net/images/20220526/1653563619_628f60e3e90f8c6a5286c.png!small)攻击链

## 技术分析

### 检测绕过

最开始 Metastealer 使用 PowerShell 执行命令 `powershell -inputformat none -outputformat
none –NonInteractive -Command Add-MpPreference -ExclusionExtension "exe"`。

该命令为 Microsoft Defender 添加了例外规则，将 `.exe`扩展名排除在扫描外。这样降低了恶意软件与攻击者投递的其他 Payload
被检测的概率。

![image.png-30.9kB](https://image.3001.net/images/20220526/1653563620_628f60e473fa04e26af2f.png!small)Microsoft
Defender

在处理 Microsoft Defender 后，Metastealer 使用另一个 PowerShell
命令将文件重命名为固定名称：`powershell rename-item -path .xyz -newname hyper-v.exe`。

### 持久化

Metastealer 使用组件对象模型（COM）在 `\Microsoft\Windows’`下创建名为
`sys`的计划任务。该计划任务会在用户登录时触发，确保恶意软件在计算机重启后仍能持久化存在。

![image.png-77.2kB](https://image.3001.net/images/20220526/1653563620_628f60e4bb67e6024742d.png!small)计划任务

### 字符串混淆

Metastealer 的大部分字符串都是加密的，在运行时根据需要进行解密。加密字符串都被放置在栈上，使用按位异或进行解密。

![image.png-51kB](https://image.3001.net/images/20220526/1653563621_628f60e527837bfbfdd63.png!small)字符串混淆逻辑

Python 等效代码如下所示：

    
    
    def swap32(x):return int.from_bytes(x.to_bytes(8, byteorder='little'), byteorder='big', signed=False)def split_hex(input):text = hex(input)text = text[2:]text = text.zfill(len(text) + len(text) % 2)output = " ".join(text[i: i+2] for i in range(0, len(text), 2))return(output.split(' '))hexIntXOR = []hexIntKey = []hexIntXOR.append(0x4BFB9390)hexIntXOR.append(0x25C2F251)hexIntXOR.append(0x11C52ED4)hexIntXOR.append(0x5CEDBB0D)hexIntKey.append(0x2489FBF3)hexIntKey.append(0x25C2973C)hexIntKey.append(0x11C52ED4)hexIntKey.append(0x5CEDBB0D)hexbytesxor = []hexbyteskey = []for HexInt in hexIntXOR:hexBytes = split_hex(HexInt)hexBytes.reverse()hexbytesxor = hexbytesxor + hexBytesfor HexInt in hexIntKey:hexBytes = split_hex(HexInt)hexBytes.reverse()hexbyteskey = hexbyteskey + hexBytescount = 0for hexByte in hexbytesxor:print(chr(int(hexByte, base=16) ^ int(hexbyteskey[count], base=16)), end='')count+=1

## C&C

分析时 C&C 上线虽然能够成功，但后续的请求会返回 HTTP 400 错误。这可能表示该攻击是短期的，对新感染者不再下发指令。也有可能是为了限制分析人员对
C&C 通信的分析。

样本总硬编码的 C&C 服务器为 `193.106.191.162:1775`，该地址也是被加密存储的。

使用 `cpp-httplib`通过 User Agent 为 `cpp-httplib/0.10.1`的 HTTP 请求连接 C&C 服务器。

初始请求路径为 `/api/client/new`，仅用于注册上线：

![image.png-171kB](https://image.3001.net/images/20220526/1653563621_628f60e57fb84356e6049.png!small)注册上线

响应中返回的 UUID 作为 `BotId`，每个上线请求都会返回一个新的 UUID。

使用 Nlohmann JSON 解析 JSON 字符串提取 `BotId`，并以明文形式写入文件
`%localappdata%\hyper-v.ver`。

随后的 C&C 通信以 UUID 为请求内容：

![image.png-57.2kB](https://image.3001.net/images/20220526/1653563621_628f60e5f2db9974785a7.png!small)UUID

POST 请求发送给 `/tasks/get_worker`，分析时 C&C 服务器只响应 HTTP 400 错误代码。

![image.png-120.4kB](https://image.3001.net/images/20220526/1653563622_628f60e66b06a628d4348.png!small)C&C
通信

执行命令后，执行结果会发送到 `/tasks/collect`，其中包含窃密数据或者命令执行输出。

### C&C 命令

命令ID| 功能| 描述  
---|---|---  
1001| 收集系统信息| 通过 cmd.exe 获取系统信息  
1002| 窃取 Cookie| 窃取 Chrome、Firefox 与 Edge 浏览器的 Cookie  
1003| 窃取密码| 窃取 Chrome、Firefox 与 Edge 浏览器的密码  
1004| 启动键盘记录| 针对 Chrome、Firefox 与 Notepad 启动键盘记录  
1005| 停止键盘记录|  
  
1006| 启动 HVNC| 利用 Kissnet 创建 HVNC 连接  
1007| 停止 HVNC|  
  
1008| 执行命令| 通过 cmd.exe 执行命令  
  
## IOC

> 193.106.191[.]162:1775  
> cpp-httplib/0.10.1  
> hyper-v.exe

## Yara

    
    
    rule metaStealer_memory {meta:description = "MetaStealer Memory"author = "Peter Gurney"date = "2022-04-29"strings:$str_c2_parse = {B8 56 55 55 55 F7 6D C4 8B C2 C1 E8 1F 03 C2 8B 55 C0 8D 04 40 2B 45 C4}$str_filename = ".xyz -newname hyper-v.exe" fullword wide$str_stackstring = {FF FF FF C7 85 ?? ?? ?? ?? ?? ?? ?? ?? C7 85 ?? ?? ?? ?? ?? ?? ?? ?? C7 85 ?? ?? ?? ?? ?? ?? ?? ?? C7 85 ?? ?? ?? ?? ?? ?? ?? ?? 66 0F EF}condition:uint16(0) == 0x5a4d and2 of ($str_*)}

## 参考来源

> [NCCGroup](https://research.nccgroup.com/2022/05/20/metastealer-filling-the-> racoon-void/)

