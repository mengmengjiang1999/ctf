Raccoon 是一个恶意软件家族，2019 年来一直在地下犯罪论坛中以恶意软件即服务的身份进行售卖。2022 年 7 月，该恶意软件家族发布了 C
语言编写的新版本 Raccoon Stealer v2，打破了以往使用 C++ 开发的传统。

Raccoon 是一个信息窃密恶意软件，能够从浏览器窃取例如密码、Cookie 和自动填充数据等隐私信息。特别的，攻击者对加密货币钱包也很感兴趣。

## 主要区别

Raccoon v2 也是一种窃密类恶意软件，2022 年 7 月 3 日被在野首次发现，使用 C 语言与汇编语言编写而成。

新版本 Raccoon 有一些新功能，但数据窃密机制与老版本仍然相同：

> 所有字符串都使用 base64+RC4 加密
>
> WinAPI 函数的动态加载
>
> 放弃了对 Telegram API 的依赖

其中，恶意软件获取 C&C 服务器列表的方式发生了重大变化。Raccoon Malware v1 滥用 Telegram 来获取 C&C
服务器列表，而新版本已经放弃该方式。转而使用通过受攻击者控制的服务器的硬编码 IP 地址来获取 C&C 服务器列表，再下载后续恶意软件。

## 调试信息

分析的样本（0cfa58846e43dd67b6d9f29e97f6c53e）带有完整的调试信息，可以查看其编译日期为 2022 年 5 月 26 日
13:58:25，如下所示：

![image.png-62.3kB](https://image.3001.net/images/20220802/1659409347_62e893c3927bc6426eecd.png!small)调试头文件

Raccoon Stealer v2 还通过动态解析 API 名称来隐藏攻击意图，窃密程序使用 LoadLibraryW 与 GetProcAddress
来解析每个必要的函数，如下所示。

![image.png-162.7kB](https://image.3001.net/images/20220802/1659409348_62e893c4625ff524c200a.png!small)动态解析
API

DLL 文件命和 WinAPI 函数的名称，都以明文形式存储在二进制文件中。加载的 DLL 文件包括：

> kernel32.dll
>
> Shlwapi.dll
>
> Ole32.dll
>
> WinInet.dll
>
> Advapi32.dll
>
> User-32.dll
>
> Crypt32.dll
>
> Shell32.dll

Raccoon v1 未使用动态解析，所以使用加壳技术来逃避检测，而 Raccoon v2 就直接以未加壳的方式进行投递。下图显示了 Raccoon v1
使用的 DLL 文件：

![image.png-37.3kB](https://image.3001.net/images/20220802/1659409349_62e893c50f3f6c5b50f40.png!small)导入表

一旦函数完成解析，恶意软件就开始对字符串进行解密。首先对 base64 编码进行解码，然后使用密钥 `edinayarossiya`进行 RC4
解密。所有字符串都使用解密函数 string_decryption() 进行解密，如下所示：

![image.png-206.2kB](https://image.3001.net/images/20220802/1659409349_62e893c5c181085cda991.png!small)字符串解密

旧版本的 Raccoon Stealer 只加密硬编码的 IP 地址，不加密其他字符串。而 Raccoon v2
将所有纯文本字符串都进行加密。Raccoon v1 的几个明文字符串如下所示：

![image.png-163kB](https://image.3001.net/images/20220802/1659409350_62e893c6d0bb50fd00d84.png!small)Raccoon
v1 明文字符串

在对 Raccoon v2 样本字符串进行手动解密后，可以得到以下明文字符串：

![image.png-234.1kB](https://image.3001.net/images/20220802/1659409351_62e893c79480de4b69f15.png!small)Raccoon
v2 明文字符串

![image.png-18.6kB](https://image.3001.net/images/20220802/1659409352_62e893c84f2af317e42cf.png!small)Raccoon
v2 明文字符串

C&C 服务器的 IP 地址保存在恶意软件中，使用相同的方式进行解密，但密钥为
`59c9737264c0b3209d9193b8ded6c127`。恶意软件通信的 IP 地址为
`hxxp://51.195.166.184/`，解密如下所示：

![image.png-98.9kB](https://image.3001.net/images/20220802/1659409352_62e893c8f0eaf25d49978.png!small)解密

## C&C 服务器地址

加密的字符串可以使用 CyberChef 等工具进行解密，如下所示：

![image.png-38.4kB](https://image.3001.net/images/20220802/1659409353_62e893c99e583643eb9cd.png!small)Raccoon
v2 C&C 服务器 IP 地址

这种技术在两个版本的恶意软件中都十分常见，在 Raccoon v1 中如下所示：

![image.png-48.8kB](https://image.3001.net/images/20220802/1659409354_62e893ca3b56f07fdefd7.png!small)Raccoon
v1 C&C 服务器 IP 地址

完成所有字符串的解密后，恶意软件会联系 C&C 服务器进行检查并下载恶意 DLL 文件。

## 泄露数据之前的检查

执行恶意软件核心功能前，会对环境进行检查。例如，通过获取互斥量的句柄（8724643052）查看是否在计算机上已经存在运行实例等。

这样确保同时只能运行一个恶意软件实例，下图显示了 Raccoon v2 互斥量的检查与创建。

![image.png-35.8kB](https://image.3001.net/images/20220802/1659409354_62e893cae0740d3c71c16.png!small)Raccoon
v2 互斥

下图为 Raccoon v1 中互斥量的检查与创建：

![image.png-50.2kB](https://image.3001.net/images/20220802/1659409355_62e893cb8ac9b5d8f7a2e.png!small)Raccoon
v1 互斥

检索匹配进程 Token 是否为 `S-1-5-18`，确定以 SYSTEM 身份运行，如下所示：

![image.png-127.1kB](https://image.3001.net/images/20220802/1659409356_62e893cc3b46078e1cdb4.png!small)Raccoon
v2 枚举进程 Token

如果以 SYSTEM 用户身份运行，使用 fun_CreateToolhelp32Snapshot 进行进程的枚举。下图显示了调用
enumerate_processes() 函数进行进程枚举的过程：

![image.png-20.2kB](https://image.3001.net/images/20220802/1659409356_62e893ccda482882d7c80.png!small)进程枚举

![image.png-64.6kB](https://image.3001.net/images/20220802/1659409357_62e893cd5a9e18f16724f.png!small)进程枚举

## 主机指纹

恶意软件会对主机环境进行指纹识别，利用：

> RegQueryValueExW 获取机器 ID
>
> GetUserNameW 获取用户名

下图显示了恶意软件通过 RegQueryKeyExW 和 RegQueryValueExW 函数从注册表项
SOFTWAREMicrosoftCryptography 中获取机器 ID。

![image.png-98kB](https://image.3001.net/images/20220802/1659409358_62e893ce19bc2b0189fc2.png!small)获取机器
ID

下图使用 GetUserNameW 函数获取用户名：

![image.png-36.8kB](https://image.3001.net/images/20220802/1659409358_62e893ced00ac7367230c.png!small)获取用户名

![image.png-55.3kB](https://image.3001.net/images/20220802/1659409359_62e893cf6adb1c87b09a9.png!small)用户名缓冲区

完成后，将机器 ID 与用户名等信息回传给 C&C 服务器。为此，恶意软件会创建一个字符串保存这些数据。缓冲区中构建的数据结构如下所示：

![image.png-108.6kB](https://image.3001.net/images/20220802/1659409360_62e893d013eea2e35566d.png!small)指纹信息

紧接着在后面附加 RC4 加密密钥，整体结构为 `machineId=<MachineGuid>|<UserName>&configId=<RC4
key>`。

## 命令与控制

C&C 通信完全通过 HTTP 协议进行，恶意软件首先解密获取 C&C 服务器的 IP 地址列表（存储在 local_3c 中）。分析的样本文件只包含一个
IP 地址，就只联系一个 IP 地址，如下所示：

![image.png-126.9kB](https://image.3001.net/images/20220802/1659409360_62e893d0bd01d41cbdf7a.png!small)C&C
通信

![image.png-49.1kB](https://image.3001.net/images/20220802/1659409361_62e893d1d4de8c95b1f03.png!small)缓冲区中的
URL

![image.png-114.6kB](https://image.3001.net/images/20220802/1659409362_62e893d26e1dbf23504b5.png!small)请求头

恶意软件检查是否存在响应，如果没有响应，恶意软件就会立刻退出，因为恶意软件的数据泄露需要 C&C 服务器的响应进行触发。下图中可以看到，这部分功能与
ExitProcess() 函数一同出现：

![image.png-137.9kB](https://image.3001.net/images/20220802/1659409363_62e893d34c2d460293a7e.png!small)验证响应

Raccoon v1 依靠 Telegram Bot API 获取 C&C 服务器列表，但 Raccoon Malware v2 使用 5 个硬编码 IP
地址，放弃了对 Telegram 的依赖。

## 数据泄露

撰写文章时，C&C 服务器的 IP 地址已经失效，无法分析相关流量数据。

![image.png-55.3kB](https://image.3001.net/images/20220802/1659409364_62e893d444277c81261e7.png!small)服务器失效

只能根据之前的监测数据进行分析，恶意软件下载了其他恶意 DLL 文件。

![image.png-66.8kB](https://image.3001.net/images/20220802/1659409364_62e893d4ccde566f946c9.png!small)下载的
DLL 文件

恶意软件使用 SHGetFolderPathW 函数获取 C:\Users\\\AppData 路径并追加
Local，将此目录作为存储被窃信息的位置，再回传到 C&C 服务器。

![image.png-52.4kB](https://image.3001.net/images/20220802/1659409365_62e893d588eee61e198b0.png!small)存储路径

## 结论

过去几年中，恶意软件即服务十分流行。Raccoon Stealer 作为其中的佼佼者，也被经常发现在野攻击。攻击者不断为其更新追加新功能，这是在 2019
年发布后的第二个主要版本，这意味着攻击者以后可能仍然会持续更新，对全球造成威胁。

## IOC

> 55.195.166.184  
> 0123b26df3c79bac0a3fda79072e36c159cfd1824ae3fd4b7f9dea9bda9c7909  
> 022432f770bf0e7c5260100fcde2ec7c49f68716751fd7d8b9e113bf06167e03  
> 048c0113233ddc1250c269c74c9c9b8e9ad3e4dae3533ff0412d02b06bdf4059  
> 0c722728ca1a996bbb83455332fa27018158cef21ad35dc057191a0353960256  
> 2106b6f94cebb55b1d55eb4b91fa83aef051c8866c54bb75ea4fd304711c4dfc  
> 263c18c86071d085c69f2096460c6b418ae414d3ea92c0c2e75ef7cb47bbe693  
> 27e02b973771d43531c97eb5d3fb662f9247e85c4135fe4c030587a8dea72577  
> 2911be45ad496dd1945f95c47b7f7738ad03849329fcec9c464dfaeb-5081f67e  
> 47f3c8bf3329c2ef862cf12567849555b17b930c8d7c0d571f4e112dae1453b1  
> 516c81438ac269de2b632fb1c59f4e36c3d714e0929a969ec971430d2d63ac4e  
> 5d66919291b68ab8563deedf8d5575fd91460d1adfbd12dba292262a764a5c99  
> 62049575053b432e93b176da7afcbe49387111b3a3d927b06c5b251ea82e5975  
> 7299026b22e61b0f9765eb63e42253f7e5d6ec4657008ea60aad220bbc7e2269  
> 7322fbc16e20a7ef2a3188638014a053c6948d9e34ecd42cb9771bdcd0f82db0  
> 960ce3cc26c8313b0fe41197e2aff5533f5f3efb1ba2970190779bc9a07bea63  
> 99f510990f240215e24ef4dd1d22d485bf8c79f8ef3e963c4787a8eb6bf0b9ac  
> 9ee50e94a731872a74f47780317850ae2b9fae9d6c53a957ed7187173feb4f42  
> bd8c1068561d366831e5712c2d58aecb21e2dbc2ae7c76102da6b00ea15e259e  
> c6e669806594be6ab9b46434f196a61418484ba1eda3496789840bec0dff119a  
> e309a7a942d390801e8fedc129c6e3c34e44aae3d1aced1d723bc531730b08f5  
> f7b1aaae018d5287444990606fc43a0f2deb4ac0c7b2712cc28331781d43ae27

## 参考来源

> [Zscaler](https://www.zscaler.com/blogs/security-research/raccoon-> stealer-v2-latest-generation-raccoon-family)

