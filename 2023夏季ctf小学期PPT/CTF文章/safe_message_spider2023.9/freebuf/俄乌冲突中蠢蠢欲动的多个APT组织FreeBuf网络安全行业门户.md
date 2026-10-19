地缘政治紧张不仅成为了全球的头条新闻，也为攻击者提供了攻击的话题。一个月前，俄乌冲突搅动全球，世界各地的 APT
组织也以相关话题作为诱饵展开攻击。许多诱饵文档利用恶意宏代码或模板注入获取初始立足点，发起后续的恶意攻击。战争题材的诱饵文档不局限在相关地区，而是在各地都有，从拉丁美洲、中东到亚洲。

组织名称| 归因| 目标部门| 目标国家  
---|---|---|---  
El Machete| 西班牙语国家| 金融、政府| 尼加拉瓜、委内瑞拉  
Lyceum| 伊朗| 能源| 以色列、沙特阿拉-伯  
SideWinder| 印度| 未知| 巴基斯坦  
  
## El Machete

2014 年，[卡巴斯基](https://securelist.com/el-machete/66108/)首次披露针对拉丁美洲发起攻击的 El
Machete。该组织的攻击行动最早可以追溯到 2010 年，经常使用当前政治局势相关主题的诱饵文件。

在 3 月中旬，研究人员发现 El Machete 向尼加拉瓜的金融机构发送鱼叉邮件，附件名为 `乌克兰新纳粹政权的暗黑计划`。该 Word
文档包含俄罗斯驻尼加拉瓜大使 `Alexander
Khokholikov`发表的、探讨俄乌冲突的[文章](https://www.el19digital.com/articulos/ver/titulo:126145-planes-oscuros-del-regimen-neonazi-de-ucrania)。

![image.png-225.4kB](https://image.3001.net/images/20220406/1649224131_624d29c3039b3c115b0c1.png!small)诱饵文档

### 感染链

恶意宏代码会释放名为 `~djXsfwEFYETE.txt`的 base64 编码文件，再利用 `certutil.exe`将其解码成名为
`~djXsfwEFYETE.vbe`的 VBScript 文件。利用 `wscript.exe`执行 `.vbe`文件，并通过
`msiexec.exe`执行伪装成 Adobe 软件的 `Adobe.msi`。

![image.png-126kB](https://image.3001.net/images/20220406/1649224131_624d29c3baac58fbb03cf.png!small)感染链

`Adobe.msi`会将恶意软件安装在 TEMP 目录下，再将自身复制到隐藏目录 `C:\ProgramData\PD`，这样用户通过文件资源管理器打开
ProgramData 文件夹时就不能发现。恶意软件使用 Python 编写，带有两个 Python 解释器，都伪装成 Adobe
相关的可执行文件（`AdobeReaderUpdate.exe`与`ReaderSetting.exe`）。该样本每五分钟运行一次计划任务（UpdateAdobeReader）实现持久化，该定时任务会执行
`AdobeReaderUpdate`（Loki.Rat 的修改版，自从 2020 年以来一直被 El Machete 使用）。

### C&C 通信

恶意软件的 C&C 地址并不是硬编码的，而是依赖于另一个包含指向 BlogSpot 网页、经过 base64 编码 URL 的
`license.dll`。网页内容在讨论非对称加密，但是其中嵌入了一个 base64 编码的字符串，就是真正的 C&C 地址。恶意样本将会在两个 6-7
字符长的硬编码字符串之间进行检索，例如 `/AAAA/`与 `*AAAA/`（注：A 代表字符）。

![image.png-331.3kB](https://image.3001.net/images/20220406/1649224132_624d29c4591ba20e1ed8a.png!small)BlogSpot
网页

这样可以让样本最初的连接为 `blogspot.com`的子域名，显得并非恶意。而且，攻击者可以很容易地切换 C&C 地址，而不需要重新部署样本。

上传给 C&C 服务器的数据为：

    
    
    {"nu8": "<hostname-username>","d4": "<tag>","r88": "<module name/data type>","m77": "<file path>.pgp","ns32": "<payload>","submit": "submit"}﻿

其中，`d4`字段的标签为 `Utopiya_Nyusha_Maksim`，这也是 El Machete 一直使用的标签。

### Loki.Rat

Python 使用了 base64 编码进行混淆，解码后其实代码较少，部分变量名也进行了混淆。

![image.png-206.2kB](https://image.3001.net/images/20220406/1649224133_624d29c541f037aba3d9f.png!small)去混淆脚本

样本包含的主要功能：

> 键盘记录
>
> Chrome、Firefox 浏览器凭据收集
>
> 上传和下载文件
>
>
> 收集文件信息（.doc、.docx、.pdf、.xlsx、.xls、.ppt、.pptx、.jpg、.jpeg、.rar、.zip、.odt、.ott、.odm、.ods、.ots、.odp）
>
> 屏幕截图
>
> 收集剪贴板数据
>
> 执行命令

### Payload

攻击者首先要通过屏幕截图、键盘记录和相关文件来确定失陷主机是否值得后续处理，后续攻击者会通过 `msiexec.exe`下载安装
`JavaOracle.msi`。

与 `Adobe.msi`类似，`JavaOracle.msi`也部署 Python 恶意软件并使用计划任务进行持久化。该恶意软件会并行启动多个
Python 解释器，每个解释器运行不同的模块。Python 解释器被伪装成 `JavaHosts.exe`、`JavaExt.exe`与
`JavaAdd.exe`，攻击者还会根据进程名检查某个脚本/模块是否正在运行：

> GAME 模块：通过 C&C 服务器下载 Payload，从代码看应该是 EXE 或者 MSI 文件。文件写入隐藏目录
> `C:\ProgramData\ControlD\`

> TIME 模块：进行键盘记录并回传给 C&C 服务器

> BOX 模块：检查系统中小于 5MB 的文件，经过 base64 编码再上传。首先通过 google.es 测试网络连通性，不可用则退出脚本

> LIST 模块：保存屏幕截图（`-shopt.png`）到伪装成 Microsoft
> 的目录（`%APPDATA%\Microsoft\ControlDesktop\`）中再上传到 C&C 服务器。与 BOX 模块类似，通过
> google.ru 测试网络连通性，不可用则退出脚本

> SCAN 模块：将剪贴板数据回传到 C&C 服务器。也会通过 google.ru 测试网络连通性

`JavaOracle.msi`似乎使用了新的硬编码标签 `Foo_Fighters_Everlong`，可能与 Foo Fighters 鼓手
Taylor Hawkins 去世有关。

![image.png-198.5kB](https://image.3001.net/images/20220406/1649224134_624d29c6087c2645d9ad1.png!small)部分代码

### 攻击目标

鱼叉邮件发往尼加拉瓜的一家金融机构，但诸多证据表明攻击目标不止这一个组织，还有委内瑞拉的政府。

## Lyceum

Lyceum 在 2017 年后一直十分活跃，经常攻击中东与非洲的相关部门进行窃密活动。3 月中旬，一家以色列能源公司收到来自
`reporter@protonmail.com`的鱼叉邮件，标题为 `俄罗斯在乌克兰的战争罪行`。邮件中使用了媒体中公开发布的一些图片，并且包含指向
`news-spot.live`上一篇文章的 URL。

![image.png-439.1kB](https://image.3001.net/images/20220406/1649224134_624d29c6c3b6e970adf0b.png!small)鱼叉邮件

URL 指向一份文档，引用了《卫报》发表的文章：

![image.png-436.8kB](https://image.3001.net/images/20220406/1649224136_624d29c840c92042d1350.png!small)诱饵文档

该域名下还有一些其他与俄罗斯或者俄乌冲突的恶意文档，如大西洋理事会在 2020 年分析俄罗斯核武器的报告、乌克兰特工岗位等。

![image.png-338.9kB](https://image.3001.net/images/20220406/1649224137_624d29c99c6d025742cb9.png!small)诱饵文件

### 感染链

Office 文档携带恶意宏代码，代码将嵌在文档中的可执行文件进行去混淆并释放到 `%APPDATA%\Microsoft\Windows\Start
Menu\Programs\Startup\`中。这样恶意样本的执行不会与 Office 有什么关系，而是在下次启动计算机时运行。有些 Dropper
不是文档而是 PDF 图标的可执行文件：

![image.png-126.7kB](https://image.3001.net/images/20220406/1649224138_624d29cade5388ec90ab3.png!small)感染链

Dropper 提取诱饵 PDF 文档并打开，后台下载并执行 Payload。一共发现三类 Dropper：

#### .NET DNS dropper

![image.png-180.5kB](https://image.3001.net/images/20220406/1649224139_624d29cbb786909eeaecf.png!small)Dropper

#### .NET TCP Dropper

该后门是 .NET HTTP 的变种，并添加计划任务运行。

#### Golang Dropper

将 Golang 后门释放到 Startup 文件夹和 Public\Downloads 文件夹中，并且打开 PDF 诱饵文档。

![image.png-283.6kB](https://image.3001.net/images/20220406/1649224140_624d29cc51c13daa017d0.png!small)Dropper

### Payload

每个 Dropper 都有对应的 Payload：

#### .NET DNS Backdoor

.NET DNS 后门是 DnsDig 的自定义版本：

![image.png-72.7kB](https://image.3001.net/images/20220406/1649224141_624d29cd0ba1802dfcdc4.png!small)后门

使用 DNS 隧道与 C&C 服务器通信，能够上传/下载文件并执行命令。

#### .NET TCP Backdoor

后门使用原生 TCP 套接字利用自定义协议与 C&C 服务器通信：

![image.png-179.1kB](https://image.3001.net/images/20220406/1649224141_624d29cd7f60e797f083f.png!small)后门

样本使用硬编码的配置进行 C&C 通信，代码仍然积极开发中。典型的功能包括：

> 执行命令
>
> 屏幕截图
>
> 遍历目录文件
>
> 查看安装程序列表
>
> 上传/下载/执行文件

#### Golang HTTP Backdoor

该后门主要有三个阶段：

> 检查连接：根据用户名称计算 MD5 生成 UUID，向 C&C 服务器的 `/GO/1.php`发送空的 HTTP POST 请求，服务器响应 OK
> 则继续向下

> 受害者注册：恶意样本通过 POST 请求向 C&C 服务器的 `/GO/2.php`发送失陷主机的基本信息

> 命令检索执行：向 C&C 服务器的 `/GO/3.php`发送 POST 请求获取执行命令。与其他后门一样，也可以上传/下载文件并且执行命令

![image.png-267kB](https://image.3001.net/images/20220406/1649224142_624d29ce2cb731871d330.png!small)后门

### 归因

除了以色列的能源部门，还在 VirusTotal 上发现了攻击者攻击沙特阿拉-伯的类似样本。中东地区应该是该组织攻击的重点，与 Lyceum 的相似点包括：

> 都使用 Heijden.DNS 开源库
>
> 都使用 DNS 隧道进行 C&C 通信
>
> C&C 服务器与此前 Lyceum 的 C&C 服务器在相同的 ASN 上，并且域名的注册商都是 Namecheap
>
> 都是用 Protonmail 发送鱼叉邮件

从样本时间戳和域名注册时间来看，攻击行动已经持续了几个月了。尽管多次发现，但 Lyceum 组织仍然在中东展开持续进攻。

## SideWinder

SideWinder 可能是来自印度的 APT 组织，主要针对巴基斯坦和中国进行攻击。SideWinder 利用俄乌冲突话题的样本在三月中旬被上传到了
VirusTotal 上。根据内容分析，攻击目标是巴基斯坦。诱饵文档包含伊斯-兰堡巴赫里亚大学国家海洋事务研究所的文件，标题为`聚焦俄乌冲突对巴基斯坦的影响`。

![image.png-350.2kB](https://image.3001.net/images/20220406/1649224143_624d29cf0f95e123ba0a5.png!small)诱饵文档

该文档利用远程模板注入技术，下载的外部模板是利用 CVE-2017-11882 漏洞进行攻击的 RTF 文件。利用成功后，释放并执行包含混淆
JavaScript 代码的 `1.a`。

SideWinder 的 TTP 在过去几年基本没有改变，技术细节已经被相关方披露了很多次。值得一提的是，典型的 SideWinder 的 Payload
是基于 aaaaa.NET 开发的窃密程序，最初被称为 `SystemApp.dll`。该恶意样本能够收集系统信息、从失陷主机窃取文件并执行命令等。2019
年后，该窃密程序不断在进行微调。

## 结论

俄乌冲突已经占据头版头条很长时间了，史无前例的影响了全球并且不知道何时才能结束。已经发现了几个 APT
组织利用俄乌冲突的话题进行攻击，不出意外后续也会有其他 APT 组织利用该话题发起攻击。

## IOC

    
    
    13814a190f61b36aff24d6aa1de56fe2 f9fd9e32cb04c4fc93e65f48562ecad3 53542ec51daf61fba2d26fe91b7d701f d962dd55fde800d972a156f5c63a6243 1a5489147a888c4f5f32e97ffcb01733 9fcad8f97eeae10f7a222eca94cb9a5f f8c29040122cf892190bcf3665975d2f a5dbfd729b6fd64a6c4fd77a3e356989 8b01dec07856a67db0e0d849bc84fd9e 23d174e6a0905fd59b2613d5ac106261 a437f997d45bc14e76d0f2482f572a34 ce186cda677f0120cfdb308803b8e8d8 214011a0d57b1d8238532be4f6414f58 8d51fbb90ad5942cd1a5a6534bd9d1d7 6aeca48c9090b301b3fdf9da4382c882 c41ffcbd933039bb6981d05b4c4c673e e03c7e3e8957ede592de07d3dca247b7 f72768f352994ecce3b9e5109fe93eec 8199f14502e80581000bd5b3bda250ee d79687676d2d152aec4143c852bdbc4a 2bc2abefc1a721908bc805894b62227d 37a1514a7a5f9b2c6786096129a30721 1c444ebeba24dcba8628b7dfe5fec7c6 85ca334f87667bd7fa0c47ae6149353e 73bddd5f1a0847ae5f5d55e7d9c177f6 9fb86915db1b7c00f1a4587de4e052de 37fe608983d4b06a5549247f0e16bc11 5916e5189ef0050dfcc3cc19382d08d5 f3b395661cc663c1baad41b439622071 8044dc6078b003698d6e1cbbd22a9ea6 bcb465cc2257e5777bab431690ca5039news-spot[.]livenews-spot[.]xyzcyberclub[.]onescience-news[.]livenews-reporter[.]xyz104.249.26[.]6085.206.175[.]201185.243.112[.]1368e1360cc27e95fc47924d9ba3ef84cb8fa9e142cfd16e1503c5277d0c16ae241e2c67e495166be1b97134e67b2326e1b800d3d4d8dba4bc61fd3f8eb3a92d612e3718adaca6eafeba6ff171669210cb55a3b8babf3b78072cc513273b99a7639ed09da9d48afe918f9c7f72fe4466167e2f127a28a7641ba80d6165e82f48431b9bf3e9725696331916e32e5936111e1166867b1d2d3ab05e46b9fff8679cf8fc6c794348d17d40c544487154ca72e8e6199b670f804ee25d7bcd9ff884d67b17115580f8235a0bbce61e8af79c3ed5cbe46900912eb0765ccaee82213a9275e907ccb541d0066d36701310e86e1d2b61448178d1d36f6748af0b3163ca273ac7ea7cae7dd6353831359179f4834ac4c2e9022659e205ca8506f372aad63f629bb4b04eff1b5154d23b2636fc55222e4f27c654777f348edee47c920e457835eebbcc2075fcb0ba18d43475b8454c51b35bb65e1ed323b657ea7d9651e98074dda81697353fe3238920a8c2c4cbbf25a298b3e3414f988ece0cf7afb73e3e0a54c22116b68732f8fe9e2fb5e56e9ff798f30805f9008e4f7a4be1e1c830162b865e48c986d185d156999adc762d7bff84ddbf44851419d66c2985a2ccc2e072dcaac5087528dde6839481133737de12af973080184b2aa0b2eb35af88875adbba5f0af1124f7abf06e712a2bfb4f1104ee0df179343020577959339617db69b3ca4182fbaf3f02d9b428f7e851d5a679d6dcfceafabb245cff155b48d9c0930796b33df5720901b4f2fc6fb810b6eca994fb8b2ff0edc0aa456195a7c9115615e27f75c4e4e74bff20270ec0f2bd41a4b54c121bcb811451a67c831dba1e4c03a26751cde843d44506ccece87d6347ede5071703bfd63fb12f8982eae7aaf3dde60ea877d008e61cb625b4f8b2d712ce9289892f7e799dbb1030301e2db4b0achxxps://correomindefensagobvemyspace[.]com/kolomenskoye/Adobe.msihxxps://solutionconect[.]online/uu2/x3/JavaOracle.msihxxps://great-jepsen.51-79-62-98[.]plesk[.]page/MKS/w3/Adobe.msihxxps://asymmetricfile.blogspot[.]comhxxps://postinfomatico.blogspot[.]comhxxp://31.207.44[.]72:8080hxxps://Intelligent-archimedes.51-79-62-98[.]plesk[.]page/x3/Uu-3.phpf765b0b6e4a34eb95c6f0ddf058bc88d5ef9ec2b11a5f3504d1673f4f69acecamaritimepakistan.kpt-pk[.]netkpt-pk[.]net

## Yara

    
    
    rule lyceum_dotnet_dns_backdoor{meta:author = "CPR"hash1 = "8199f14502e80581000bd5b3bda250ee"hash2 = "d79687676d2d152aec4143c852bdbc4a"hash3 = "bcb465cc2257e5777bab431690ca5039"hash4 = "2bc2abefc1a721908bc805894b62227d"hash5 = "37a1514a7a5f9b2c6786096129a30721"strings:$log1 = "MSG SIZE rcvd" wide$log2 = "Empty output" wide$log3 = "Big Output. lines: " wide$com1 = "Enddd" wide$com2 = "uploaddd" wide$com3 = "downloaddd" wide$dga = "trailers.apple.com" wide$replace1 = "BackSlashh" wide$replace2 = "QuotationMarkk" wide$re_pattern = "60\\s+IN\\s+TXT" wide$func1 = "comRun"$func2 = "PlaceDot"$func3 = "sendAns"$heijden1 = "Heijden.DNS"$heijden2 = "DnsHeijden"condition:uint16(0)==0x5a4d and (all of ($log*) or all of ($com*) or all of ($replace*) or all of ($func*) or (any of ($heijden*) and $re_pattern and $dga))}rule lyceum_dotnet_http_backdoor{meta:author = "CPR"hash1 = "1c444ebeba24dcba8628b7dfe5fec7c6"hash2 = "85ca334f87667bd7fa0c47ae6149353e"hash3 = "73bddd5f1a0847ae5f5d55e7d9c177f6"hash4 = "9fb86915db1b7c00f1a4587de4e052de"hash5 = "37fe608983d4b06a5549247f0e16bc11"hash6 = "5916e5189ef0050dfcc3cc19382d08d5"strings:$class1 = "Funcss"$class2 = "Constantss"$class3 = "Reqss"$class4 = "Screenss"$class5 = "Shll"$class6 = "test_A1"$class7 = "Uploadss"$class8 = "WebDL"$cnc_uri1 = "/upload" wide$cnc_uri2 = "/screenshot" wide$cnc_pattern_hex1 = {43 6f 6e 74 65 6e 74 2d 44 69 73 70 6f 73 69 74 69 6f 6e 3a 20 66 6f 72 6d 2d 64 61 74 61 3b 20 6e 61 6d 65 3d 22 7b 30 7d 22 0d 0a 0d 0a}$cnc_pattern_hex2 = {6d 75 6c 74 69 70 61 72 74 2f 66 6f 72 6d 2d 64 61 74 61 3b 20 62 6f 75 6e 64 61 72 79 3d 7b 30 7d}$cnc_pattern_hex3 = {43 6f 6e 74 65 6e 74 2d 44 69 73 70 6f 73 69 74 69 6f 6e 3a 20 66 6f 72 6d 2d 64 61 74 61 3b 20 6e 61 6d 65 3d 22 7b 30 7d 22 3b 20 66 69 6c 65 6e 61 6d 65 3d 22 7b 31 7d 22 0d 0a 43 6f 6e 74 65 6e 74 2d 54 79 70 65 3a 20 7b 32 7d 0d 0a 0d 0a}$constant1 = "FILE_DIR_SEPARATOR"$constant2 = "APPS_PARAMS_SEPARATOR"$constant3 = "TYPE_SENDTOKEN"$constant4 = "TYPE_DATA1"$constant5 = "TYPE_SEND_RESPONSE_IN_SOCKET"$constant6 = "TYPE_FILES_LIST"$constant7 = "TYPE_FILES_DELETE"$constant8 = "TYPE_FILES_RUN"$constant9 = "TYPE_FILES_UPLOAD_TO_SERVER"$constant10 = "TYPE_FILES_DELETE_FOLDER"$constant11 = "TYPE_FILES_CREATE_FOLDER"$constant12 = "TYPE_FILES_DOWNLOAD_URL"$constant13 = "TYPE_OPEN_CMD"$constant14 = "TYPE_CMD_RES"$constant15 = "TYPE_CLOSE_CMD"$constant16 = "TYPE_CMD_REQ"$constant17 = "TYPE_INSTALLED_APPS"$constant18 = "TYPE_SCREENSHOT"$constant19 = "_RG_APP_NAME_"$constant20 = "_RG_APP_VERSION_"$constant21 = "_RG_APP_DATE_"$constant22 = "_RG_APP_PUB_"$constant23 = "_RG_APP_SEP_"$constant24 = "_SC_EXT_"condition:uint16(0)==0x5a4d and (4 of ($class*) or 4 of ($cnc_*) or 4 of ($constant*))}rule lyceum_golang_backdoor{meta:author = "CPR"hash1 = "a437f997d45bc14e76d0f2482f572a34"hash2 = "23d174e6a0905fd59b2613d5ac106261"hash3 = "bcb465cc2257e5777bab431690ca5039"strings:$func1 = "main.Ase256"$func2 = "main.DecryptAse256"$func3 = "main.IsServerUp"$func4 = "main.register"$func5 = "main.commandforrun"$func6 = "main.UPLOAD"$func7 = "main.commandforanswer"$func8 = "main.GetMD5Hash"$func9 = "main.get_uid"$func10 = "main.commandrun"$func11 = "main.download"$func12 = "main.postFile"$func13 = "main.sendAns"$func14 = "main.comRun"$cnc_uri1 = "/GO/1.php"$cnc_uri2 = "/GO/2.php"$cnc_uri3 = "/GO/3.php"$auth_token = "auth_token=\"XXXXXXX\""$log1 = "client registred"$log2 = "no command"$log3 = "can not create file"$log4 = "errorGettingUserName"$log5 = "New record created successfully"$log6 = "SERVER_IS_DOWN"$dga = "trailers.apple.com."condition:uint16(0)==0x5a4d and ((10 of ($func*) or any of ($cnc_uri*) or $auth_token or 3 of ($log*)) or ($dga and 4 of them))}rule ElMachete_doc{meta:author = "CPR"hash1 = "8E1360CC27E95FC47924D9BA3EF84CB8FA9E142CFD16E1503C5277D0C16AE241"strings:$s1 = "You want to continue with the Document" ascii$s2 = "certutil -decode" ascii$s3 = /C:\\ProgramData\\.{1,20}\.txt/$s4 = /C:\\ProgramData\\.{1,20}\.vbe/condition:uint16be(0) == 0xD0CF and 2 of ($s*)}rule ElMachete_msi{meta:author = "CPR"hash1 = "ED09DA9D48AFE918F9C7F72FE4466167E2F127A28A7641BA80D6165E82F48431"strings:$s1 = "MSI Wrapper (8.0.26.0)"$s2 = "Windows Installer XML Toolset (3.11.0.1701)"$s3 = "\\Lib\\site-packages\\PIL\\"$s4 = "\\Lib\\site-packages\\pyHook\\"$s5 = "\\Lib\\site-packages\\requests\\"$s6 = "\\Lib\\site-packages\\win32com\\"$s7 = "\\Lib\\site-packages\\Crypto\\"condition:4 of them}

## 参考来源

> [CheckPoint](https://research.checkpoint.com/2022/state-sponsored-attack-> groups-capitalise-on-russia-ukraine-war-for-cyber-espionage/)

