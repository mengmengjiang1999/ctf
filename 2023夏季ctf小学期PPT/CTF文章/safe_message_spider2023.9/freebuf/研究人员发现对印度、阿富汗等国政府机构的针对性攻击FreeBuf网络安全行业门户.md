Trellix 电子邮件安全研究团队发现了自 2021 年以来针对阿富汗、印度、意大利、波兰和美国政府机构的针对性攻击行动。攻击者通过“印度-阿富汗”关系的地缘政治主题鱼叉邮件进行攻击，诱使受害者点击恶意链接或者执行恶意附件。

鱼叉邮件通常包含一个恶意附件或者提供恶意文件的下载 URL，打开 Excel 文件后就会执行嵌入的恶意宏代码并安装远控木马 AysncRAT 和
LimeRAT。攻击者能够通过木马对失陷主机进行屏幕截图、击键记录、凭据窃取、数据窃密等恶意行为。

攻击行动中使用的电子邮件来自南亚地区，应该是位于南亚的攻击者在行动，全球检测分布如下所示：

![image.png-304.9kB](https://image.3001.net/images/20220718/1658121487_62d4ed0fc93eff3e0bedd.png!small)目标分布

## 威胁演进

通常来说，攻击链都是：电子邮件 -> URL -> ZIP -> XLS -> 宏代码。Trellix 发现的恶意 Excel 文件名为
`FE_APT_Dropper_Macro_DoubleHide_1`。

![image.png-266.3kB](https://image.3001.net/images/20220718/1658121488_62d4ed10bc0af63a7d2c8.png!small)攻击链

## 攻击时间线

![image.png-202kB](https://image.3001.net/images/20220718/1658121489_62d4ed118a9a44a7b8c79.png!small)攻击时间线

攻击已经持续了一年多，攻击者在最开始攻击一段时间后立刻进入隐身状态。随后一直是这样的间歇攻击，2021 年 3 月至 4 月是第一波攻击，2021 年 7
月是第二波攻击，2021 年 12 月是第三波攻击，2022 年 3 月是第四波攻击。

## 电子邮件

攻击者通过 Gmail 发送鱼叉邮件，根据电子邮件头分析应该是从南亚地区发送的，并且时区也符合南亚攻击者的活动规律。

![image.png-353.5kB](https://image.3001.net/images/20220718/1658121490_62d4ed12531e0fcf0616f.png!small)电子邮件头

邮件的主题是与印度有关的地缘政治新闻，例如 Indian Nationals ( who were hidden in Kabul ) Killing in
Kabul Tonight（意为藏在喀布尔的印度人将在今晚杀人）和 Indian workers missing from the dam
project（意为在大坝建筑工程中失踪的印度工人）。最近使用的主题是与疫情有关，名为 31 Covid Deaths In 24 Hours:
Information campaign by NDTV（意为一日内31例新冠疫情死亡），在邮件中包含一个 Google Drive 的链接，用于下载恶意
ZIP 文件。在某些邮件中，恶意 ZIP 文件以文件附件的形式发送，其中包含一个 Office 文档，执行会释放远控木马。

![image.png-232.4kB](https://image.3001.net/images/20220718/1658121491_62d4ed135313621fc7c96.png!small)电子邮件

## 技术细节

恶意文档文件被当作 Dropper，执行名为 msword.exe 的文件。Excel 文件中包含 VBA 宏代码，在打开文档时会被执行。恶意可执行代码以
base64 编码的形式存在文档文件中，VBA 宏代码读取并解码，再利用硬编码的异或密钥进行解密，最终执行恶意代码。

![image.png-547.7kB](https://image.3001.net/images/20220718/1658121492_62d4ed142b861287bc400.png!small)恶意
Excel 文件

![image.png-266.2kB](https://image.3001.net/images/20220718/1658121493_62d4ed15185f6d8ebbda2.png!small)恶意宏代码

![image.png-299.4kB](https://image.3001.net/images/20220718/1658121494_62d4ed16078c35faee305.png!small)恶意宏代码

异或加密的硬编码密钥为：`MxjnbvbX%$#@c%%!@#$C%^&*(K(*&K0^%$W$@!&@#$C%EGGGxcel^MicrosoLKHGFD^%$W@2017!&
^%$#lx^&%$0`。

![image.png-314.1kB](https://image.3001.net/images/20220718/1658121494_62d4ed16d4c3df6324c9a.png!small)异或函数

msword.exe 是一个 SFX 格式文件，其中包含多个可执行文件：

![image.png-379.4kB](https://image.3001.net/images/20220718/1658121495_62d4ed17da3b3d2f5eb76.png!small)msword.exe
内容

文件信息如下所示：

![image.png-72.9kB](https://image.3001.net/images/20220718/1658121496_62d4ed18a8fcc9bafbc19.png!small)文件信息

执行后，msword.exe 会释放经过 Crypto Obfuscator For .Net 模糊处理过的远控木马。msword.exe 然后会启动进程
igfx.exe 执行以下操作：

> 检查 .NET 版本，重命名远控木马文件名为 excel.exe
>
> 检查 .NET 版本，使用相对应版本的远控木马，如果未能确定版本默认使用 3_5
>
> 设置 excel.exe 文件属性为隐藏与只读
>
> 修改注册表实现持久化
>
> 删除其他远控木马文件
>
> 启动 excel.exe 进程

![image.png-137.1kB](https://image.3001.net/images/20220718/1658121497_62d4ed19639bb857e3c5e.png!small)进程链

![image.png-199.9kB](https://image.3001.net/images/20220718/1658121498_62d4ed1a42a4934afcc00.png!small)注册表项

检查的各个 .NET 版本为：

> HKLM\SOFTWARE\Microsoft\NET Framework Setup\NDP\v4
>
> HKLM\SOFTWARE\Microsoft\NET Framework Setup\NDP\v4.5
>
> HKLM\SOFTWARE\Microsoft\NET Framework Setup\NDP\v4.5.1
>
> HKLM\SOFTWARE\Microsoft\NET Framework Setup\NDP\v4.5.2
>
> HKLM\SOFTWARE\Microsoft\NET Framework Setup\NDP\v4.6
>
> HKLM\SOFTWARE\Microsoft\NET Framework Setup\NDP\v4.6.1
>
> HKLM\SOFTWARE\Microsoft\NET Framework Setup\NDP\v4.7
>
> HKLM\SOFTWARE\Microsoft\NET Framework Setup\NDP\v4.7.2

## AsyncRAT

AsyncRAT 的配置如下所示：

> Ports = "6606”  
> Hosts = "107.173.143.111"  
> Version = "2.5.7b"  
> Install = "false"  
> InstallFolder = "AppData"  
> InstallFile = "msexcl.exe"  
> Key = "MZ-RX  
> MTX = "%MTX%";  
> Certificate = "%Certificate%"  
> Serversignature = "%Serversignature%"  
> X509Certificate2 ServerCertificate;  
> Anti = "false";  
> Aes256 aes256 = new Aes256(Key);  
> Pastebin = "null";  
> BDOS = "false";  
> Delay = "24";  
> Group = "Debug";

AsyncRAT 支持的命令是：

> pong：从客户端获取数据
>
> plugin：运行插件
>
> saveplugin：保存插件
>
> clientinfo：回传系统信息
>
> ping：测试服务器连通性
>
> sendplugin：下拉获取插件

## LimeRAT

LimeRAT 的配置如下所示：

> Pastebin = "<https://pastebin.com/raw/DDTVwwbu>"  
> HOST = "107.173.143.111"  
> PORT = "8989"  
> EncryptionKey = "MZRX"  
> ENDOF = "|'N'|"  
> SPL = "|'L'|"  
> EXE = "CLIENT.exe"  
> USB = "false"  
> PIN = "false"  
> ANTI = "false"  
> DROP = "false"  
> PATH1 = "Temp"  
> PATH2 = "\Lime\"  
> fullpath = Environ(PATH1) & PATH2 & EXE  
> BTC_ADDR = "THIS IS YOUR BTC 1234567890" 'Bitcoin address  
> DWN_CHK = "true"  
> DWN_LINK = ""  
> Delay = "3"

LimeRAT 支持的命令是：

> IPSend：运行计时器
>
> IP：停止计时器
>
> ICAP：获取屏幕截图
>
> CPL：检查插件是否安装
>
> IPL：保存插件并加载
>
> IPLM：加载插件但不保存
>
> INFO：回传系统信息
>
> IP：测试服务器连通性
>
> IPStart：计时器启动
>
> #CAP：发送屏幕截图
>
> GPL：下拉获取插件
>
> MSG：发送消息

## IOC

> 7a6b87a7ba79160232579157b8ebcaea7660392d98cb6b8b3d562a383a0894bc  
> 5e44f769aa9a745ade82589bbbd17c3687f2fb7c08b1043d8c5c44d28eaa20a9  
> fe1c8b01f5abc62551b0a3f59fe1675c66dd506d158f5de495a5d22d7445e6e9  
> fa9cb5608841f023052379818a9186496526039bc47cac05a6866f5fb0e70fc5  
> 080fcc70c11248eaf34bd30c0dc9800b0b1742fe92c96c9995a1c73c0adf2336  
> 465a59b7a97364bc933703a8fda715090c6a927f814bc22a0057e6a7134cb69f  
> 5e082d1c85e591aebb380d7d7af56000ac0ef5fc32e216cb5fe7027bb9861743  
> f59dc209ee236e5ed78f83117865164e57a223f742c75f57c20d3da4cbe179e0  
> f32b0d71274ea93f27527079371e5e926e8d6a6f29d84ac602e48da0332c9f4c  
> 8248432bcba6e8bb8731c0b8f2fbe4aae2e2d0fee2157477c83343743c39c1a8  
> 06064b3b0158efbfa9d849c853a9783c7e9d07c5924275d0d33c6ac74c78eec7  
> 886c5883113d279d97caaca2714860dfceb421c7297dbb3ee04a00b7d50b821b  
> b9584cf67e73a759d6c412962d4a9d7471c703f72e056cd24742a4b78c68ff2d  
>
> hxxps://drive.Google.com/u/0/uc?id=1nU6-jGVnOKeZofflu8hfx2t83lAB9TPI&export=download  
> 107.173.143.111  
> kabul.contact@gmail.com  
> mashrefhaideri@gmail.com  
> latifmahmood66666@gmail.com  
> fscon.kab@gmail.com  
> admn.kabul@gmail.com  
> ravish49.ndtv@gmail.com

## 参考来源

> [Trellix﻿](https://www.trellix.com/en-us/about/newsroom/stories/threat-> labs/targeted-attack-on-government-agencies.html)

