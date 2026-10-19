2022 年 1 月，研究人员发现了一个名为 ChromeLoader（也被称为 Choziosi Loader 和
ChromeBack）的浏览器劫持恶意软件。

攻击者没有选择使用 EXE、DLL
等传统的恶意软件，而是使用浏览器扩展进行攻击。攻击者通过浏览器展示广告并且窃取用户搜索数据。攻击者在持续进行升级与技术迭代，本文介绍相关的细节与演变。

## ChromeLoader 恶意软件

ChromeLoader 是一个多阶段恶意软件家族，在攻击链的不同阶段都有不同的变种。各种各样的浏览器扩展程序也就是恶意软件各种各样的变种：

> 变种0：在野发现恶意活动前就活跃的样本，使用 AutoHotKey 编译的 Chrome 扩展 1.0 版本，第一次已知攻击发生在去年十二月。
>
> 变种1：Chrome 扩展的 2.0-4.4 版本，还有一个 .NET 可执行文件。该文件通过混淆的 PowerShell 进行传播，主要在一月份活跃。
>
> 变种2：Chrome 扩展的 6.0 版本，自从三月以来一直活跃。
>
> MacOS变种：针对 MacOS 计算机，使用 Chrome 扩展的 6.0 版本，自从三月以来一直活跃。

![image.png-118.6kB](https://image.3001.net/images/20220718/1658122300_62d4f03c704ec76f3976f.png!small)感染链

## 变种1

变种 1 于 2022 年 1 月首次出现。

当用户通过广告网站和社交媒体平台上的恶意广告下载种子文件或破解游戏时，就会被感染。用户扫描网页上的二维码，被重定向到 ISO 文件的下载站，下载后点击执行。

![image.png-362.7kB](https://image.3001.net/images/20220718/1658122301_62d4f03d454e9efa4d034.png!small)二维码示例

![image.png-105.3kB](https://image.3001.net/images/20220718/1658122302_62d4f03e4efe4afc1783c.png!small)下载站示例

## 部署

ISO 文件中包含：

> Microsoft.Win32.TaskScheduler.dll：由微软将签名的合法 .NET DLL 文件
>
> Language 文件夹：DLL 使用的资源文件
>
> CS_installer.exe 及其配置文件：恶意可执行文件，某些文件中不小心包含了 PDB 路径
>
> _meta.txt：文本文件

大部分文件都是隐藏的，普通用户在用资源管理器打开时不会注意到这些隐藏文件。唯一的非隐藏文件是
CS_installer.exe，诱使受害者双击来完成软件安装下载。

![image.png-198.8kB](https://image.3001.net/images/20220718/1658122303_62d4f03f064387cbceff8.png!small)ISO
文件示例

受害者执行后，会显示如下消息，攻击者在误导受害者。

![image.png-41.8kB](https://image.3001.net/images/20220718/1658122303_62d4f03fd5290e879ecce.png!small)弹出提示

可执行文件是用 .NET 编写的无混淆程序，程序创建计划任务每十分钟执行一次 base64 编码的 PowerShell 命令。

![image.png-244.2kB](https://image.3001.net/images/20220718/1658122304_62d4f0407e2877ca85df3.png!small)部分代码

脚本文件来自 _meta.txt 文件，通过预定义函数进行字符替换来解密：

![image.png-56.8kB](https://image.3001.net/images/20220718/1658122305_62d4f041451a6b7c5a1e8.png!small)部分代码

该恶意软件变种的早期版本中缺少部分功能，如下所示。只是简单将编码后的 PowerShell 脚本硬编码到 .NET
可执行文件中，计划任务也提供了硬编码的名称 ChromeLoader。

![image.png-428.3kB](https://image.3001.net/images/20220718/1658122305_62d4f041de10729796b5e.png!small)部分代码

攻击者使用编码的 PowerShell 脚本下载恶意浏览器扩展并将其加载到用户使用的 Chrome 浏览器中。

![image.png-127.4kB](https://image.3001.net/images/20220718/1658122306_62d4f042e15d8616e6431.png!small)PowerShell
部分代码

![image.png-215.5kB](https://image.3001.net/images/20220718/1658122307_62d4f043981e7328bdcab.png!small)下载
Payload

![image.png-38.8kB](https://image.3001.net/images/20220718/1658122308_62d4f0444d2fa12b28727.png!small)尝试加载

下图显示了该变种早期版本执行的 PowerShell 脚本，早期的代码明显更短且不复杂：

![image.png-133.9kB](https://image.3001.net/images/20220718/1658122308_62d4f044e32839c6da2b3.png!small)PowerShell
部分代码

## Dropper 统计

Chrome 扩展程序的 URL 被硬编码在混淆的 PowerShell 命令中，并且在不同版本之间发生变化：

![image.png-151.1kB](https://image.3001.net/images/20220718/1658122309_62d4f0459f11ff982a55c.png!small)域名列表

![image.png-126kB](https://image.3001.net/images/20220718/1658122310_62d4f0464c8129b2f11b1.png!small)分布统计

![image.png-14kB](https://image.3001.net/images/20220718/1658122310_62d4f046e81cbf4c77e0b.png!small)被阻拦位置的统计

![image.png-78.9kB](https://image.3001.net/images/20220718/1658122311_62d4f0477553f3438c3ab.png!small)时间演进

## Payload

Payload 是一个 Chrome 扩展程序：

![image.png-76.5kB](https://image.3001.net/images/20220718/1658122312_62d4f0482f29625a492d7.png!small)扩展文件示例

扩展程序声称自己是无害的，但是会要求提升权限，访问浏览器数据、操纵 Web 请求和访问每个可能的 URL 地址，而合法的浏览器扩展程序不会这样做。

![image.png-120.9kB](https://image.3001.net/images/20220718/1658122312_62d4f048d1364bdbbcd52.png!small)清单文件示例

Javascript 文件 conf.js 中声明了常量变量，C&C 域名存储在 `_ExtDomNoSchema`中。

![image.png-83kB](https://image.3001.net/images/20220718/1658122313_62d4f04982581b03ddabe.png!small)JavaScript
文件示例

background.js 文件是经过高度混淆的，公开的去混淆工具都无法正常反混淆。

![image.png-22.7kB](https://image.3001.net/images/20220718/1658122314_62d4f04a196ae4acdcda6.png!small)JavaScript
文件示例

该脚本使用各种混淆技术来隐藏其目的和恶意代码。执行的第一个函数负责将标准 JavaScript
函数和对象复制到命名混淆的新对象中，稍后将使用该脚本来解码位于该脚本最后一条指令中的最终 Payload。

![image.png-218.8kB](https://image.3001.net/images/20220718/1658122314_62d4f04ad0c9969c07f66.png!small)重命名示例

攻击者使用了面向 switch-case 的结构来使恶意软件分析人员更难分析：

![image.png-290.6kB](https://image.3001.net/images/20220718/1658122315_62d4f04ba35d4497a4658.png!small)部分代码

攻击者利用常见去混淆工具会删除未引用的函数与对象的特性，但攻击者通过执行逻辑保证了如果这些函数被删除将会陷入无限循环。

![image.png-31.2kB](https://image.3001.net/images/20220718/1658122316_62d4f04c68d1f40a5a6f8.png!small)未引用的函数

这个函数返回一个长的加扰字符串，通过一个硬编码的键进行异或，然后拆分成一个字符串数组。

![image.png-26.8kB](https://image.3001.net/images/20220718/1658122316_62d4f04ce48805e8358a6.png!small)数组示例

恶意软件最终使用这些字符串来解码，引用此数组中相关索引处的字符串，而不是在代码中硬编码字符串。

![image.png-37kB](https://image.3001.net/images/20220718/1658122317_62d4f04d75281aedd846d.png!small)数组示例

![image.png-172.6kB](https://image.3001.net/images/20220718/1658122318_62d4f04e010ec6b4bca64.png!small)去混淆脚本

## 窃密与广告

恶意软件使用了各种扩展功能，实现自己的恶意目的。

![image.png-237.5kB](https://image.3001.net/images/20220718/1658122318_62d4f04ec62bb43d5918d.png!small)安装计划任务示例

安装扩展程序时，它会添加两个 Chrome 计划任务。计划任务触发时，调用两个函数:

> ad：扩展程序向 C&C 服务器请求广告并显示在选项卡中
>
> hb：扩展程序向 C&C 服务器告知执行状态

![image.png-125kB](https://image.3001.net/images/20220718/1658122319_62d4f04fae36dad3b5644.png!small)计划任务

恶意软件还拦截向搜索引擎发出的请求，包括 Google、Yahoo 以及 Bing，攻击者更好地了解受害者的兴趣爱好。

![image.png-149.8kB](https://image.3001.net/images/20220718/1658122320_62d4f0506efb793a28952.png!small)浏览器劫持功能

扩展使用不同的机制来验证它是否正确执行。例如每个传出到 C&C 服务器的数据包都有一个名为 `dd`的硬编码头，攻击者可以使用它来识别不同的分销渠道。

![image.png-60.3kB](https://image.3001.net/images/20220718/1658122321_62d4f05123ad51568b4b1.png!small)硬编码头

## 版本控制

大多数恶意扩展包含一个名为 conf.js 的文件，该文件存储相关配置信息，如 C&C 主机名、dd 字段值、扩展名与版本等。

> 2.0 版本，2022 年 1 月 4 日发布
>
> 3.0 版本，2022 年 1 月 6 日发布
>
> 4.* 版本，2022 年 1 月 7 日发布

## MacOS 变种

2022 年 3 月，攻击者部署了针对 MacOS 用户的新变种，该变种到现在仍然活跃。

Dropper 通常为一个 DMG 文件，其中包含多个文件。利用 bash 脚本：

> 下载浏览器扩展
>
> 将浏览器扩展加载到目标浏览器中

![image.png-46.1kB](https://image.3001.net/images/20220718/1658122321_62d4f051b9786148bab61.png!small)安装脚本

后续更新中，攻击者不在 base 脚本中执行而是将命令编码在独立文件再通过 OpenSSL 解码并执行。

![image.png-152.8kB](https://image.3001.net/images/20220718/1658122322_62d4f052686e8a829abcd.png!small)安装脚本

MacOS 变种晚于 Windows 平台，根据扩展程序应该为该恶意软件的 6.0 版本。

## 变种2

变种 2 的 ISO 文件中包含新的可执行文件，受害者只能看到一个 Windows 快捷方式。

![image.png-40.3kB](https://image.3001.net/images/20220718/1658122323_62d4f05368f167d3227e4.png!small)恶意
ISO 文件

ISO 文件通过 LNK 文件运行名为 resources.bat 的批处理脚本，将 app.zip 的内容提取到 %APPDATA% 中。其中包含一个名为
Tone.exe 的可执行文件。

![image.png-251.6kB](https://image.3001.net/images/20220718/1658122324_62d4f0541714206debcb6.png!small)LNK
文件配置

![image.png-47.5kB](https://image.3001.net/images/20220718/1658122325_62d4f05523f64d45ece31.png!small)示例脚本

与变种 1 一样，变种 2 也安装 Chrome 扩展程序。通过 PowerShell 执行 WMI 查询，安装名为 chrome 的计划任务。

![image.png-74.9kB](https://image.3001.net/images/20220718/1658122325_62d4f055b5abe75ee6379.png!small)安装计划任务

分析混淆 PowerShell 脚本时，发现了与变种 1 类似的 Dropper：

![image.png-164.5kB](https://image.3001.net/images/20220718/1658122326_62d4f0567ad818057aa5d.png!small)计划任务示例

PowerShell 脚本会创建并加载恶意 Chrome 扩展程序。

![image.png-170.8kB](https://image.3001.net/images/20220718/1658122327_62d4f057486e9c5aa824d.png!small)下载文件示例

## 变种0

分析显示，变种 0 最早在 2021 年 12 月就开始在野使用。恶意软件是使用 AutoHotKey 编写的可执行文件，功能与 PowerShell 的
Dropper 非常相似：

![image.png-55.3kB](https://image.3001.net/images/20220718/1658122328_62d4f058453d2bb9618c3.png!small)AutoHotKey
脚本内容

按图索骥，发现了被攻击者命名为 1.0 版本的 ChromeLoader 恶意软件。该版本并未经过混淆，并且包含开发者注释：

![image.png-194.7kB](https://image.3001.net/images/20220718/1658122328_62d4f058e8e6c0f6760b9.png!small)部分代码

## 结论

本文介绍了 ChromeLoader
恶意软件的诸多版本与演化过程，在非常短的时间内就发布了多个版本的恶意软件。攻击者尽管没有造成重大的恶劣影响，但也正是因此才获得了广泛的传播。攻击者对恶意软件不同版本进行了详细标注，应该有成体系的开发框架。当然，目前用户对
ISO 文件与浏览器扩展的安全性也应该重视起来。

## IOC

> fa52844b5b7fcc0192d0822d0099ea52ed1497134a45a2f06670751ef5b33cd3  
> e1f9968481083fc826401f775a3fe2b5aa40644b797211f235f2adbeb0a0782f  
> 860c1f6f3393014fd84bd29359b4200027274eb6d97ee1a49b61e038d3336372  
> 0ecbe333ec31a169e3bce6e9f68b310e505dedfed50fe681cfd6a6a26d1f7f41  
> 614e2c3540cc6b410445c316d2e35f20759dd091f2f878ddf09eda6ab449f7aa  
> 2e006a8e9f697d8075ba68ab5c793670145ea56028c488f1a00b29738593edfb  
> bcc6cfc82a1dc277be84f28a3b3bb037aa9ef8be4d5695fcbfb24a1033174947  
> 6d89c1cd593c2df03cdbd7cf3f58e2106ff210eeb6f60d5a4bf3b970989dee2e  
> edeec82c65adf5c44b52fbdc4b7ff754c6bd391653bba1e0844f0cab906a5baf  
> 6c54e1ea9c54e4d8ada1d15fcdbf53e4ee7e4a677d33c0ea91f6203e02140788  
> a9670d746610c3be342728ff3ba8d8e0680b5ac40f4ae6e292a9a616a1b643c8  
> fb9cce7a3fed63c0722f8171e8167a5e7220d6f8d89456854c239976ce7bb5d6  
> 1717de403bb77e49be41edfc398864cfa3e351d9843afc3d41a47e5d0172ca79  
> 1b4786ecc9b34f30359b28f0f89c0af029c7efc04e52832ae8c1334ddd2b631e  
> 486c966b6e2d24dd8373181faf565d85abfd39559d334765f5135e20af55542c  
> 03b2f267de27dae24de14e2c258a18e6c6d11581e6caee3a6df2b7f42947d898  
> dd2da35d1b94513f124e8b27caff10a98e6318c553da7f50206b0bfded3b52c9
> 3927e4832dcbfae7ea9e2622af2a37284ceaf93b86434f35878e0077aeb29e7e  
> e449eeade197cab542b6a11a3bcb972675a1066a88cfb07f09e7f7cbd1d32f6d  
> 8840f385340fad9dd452e243ad1a57fb44acfd6764d4bce98a936e14a7d0bfa6  
> 26977d22d9675deddfde231e89a77c013062b8820aa117c8c39fd0a0b6ab0a23  
> ded20df574b843aaa3c8e977c2040e1498ae17c12924a19868df5b12dee6dfdd  
> 1dbe5c2feca1706fafc6f767cc16427a2237ab05d95f94b84c287421ec97c224  
> 9eca0cd45c00182736467ae18da21162d0715bd3d53b8df8d92a74a76a89c4a0  
> c56139ea4ccc766687b743ca7e2baa27b9c4c14940f63c7568fc064959214307  
> 3b5a18d45ab6fcf85df51703ef6fac8226fc274ecd0a21c0a1f15f15f7d39e01  
> 44464fb09d7b4242249bb159446b4cf4c884d3dd7a433a72184cdbdc2a83f5e5  
> 2d4454d610ae48bf9ffbb7bafcf80140a286898a7ffda39113da1820575a892f  
> 53347d3121764469e186d2fb243f5c33b1d768bf612cc923174cd54979314dd3  
> afc8a5f5f8016a5ce30e1d447c156bc9af5f438b7126203cd59d6b1621756d90  
> 564e913a22cf90ede114c94db8a62457a86bc408bc834fa0e12e85146110c89b  
> e72a42ad27c06ba0a9951705423a3650a0c4a1f8c18c5782ab98e2e72021bbb8  
> 26bce62ea1456b3de70d7ac328f4ccc57fe213babce9e604d8919adf09342876  
> 44f9680710ba7635bb3bfe025b087e85d51857d9618c5ffa5c247ccdc8bca3c3  
> 5ee2b7ea46cc3f34b796ab4992e778938c057490695e9109f016fc7a1b308395  
> a0ff3b427c77594fa48d79ed52d372bd2a8baae54ee85b243d86d9dd493ffbc6  
> f3176bcd28b89e4ae7a4426c82c8b73ca22c62ecbc363296193c8f5becef973c  
> 424347b6f5caca8174d1b0ac2e32867a4201a41176fed1af7b3e1a0716fc7e46  
> c67b87cb7420500e4b0bb6500f1875bc77a7d96997ed2850d8142dfd9636da29  
> 8f2da6c721251edd251addb795552ed54d89fb53d2a470d8a7f807e77aac402c  
> e0d57152524e79a07e5b7d7b37831cb7596cd3afe651b4eecaf4123b1af1ffa6  
> 606d49ae054e13461bad3e405cc5996462c14bd48e94fe8a63f923fbb7c14b71  
> 7ef7bdf8ea2f8751f45482453bf7441d2b2f92d743324afdf1afc11ea248c56d  
> 84c93f1f7bdc44e8e92be10bf5e566f3116c9962c35262643fe2084c3b8d1bb5  
> 4673c1f8d307b70c4be837e842cfdf5cce60c6bf793ae85a1bce07c9c15fe14d  
> 0257dccfdeb1bc9683334d0d964c72ea0eeedbfda33cba1f60a395cca8e516da  
> 0d510dbcf8ed5c7b81206598886a7fbd86f11d36871612ba066d6ec85723fada  
> e920dbc4741114f747a631928e398ef671fe9133b6aab33991d18150b4fcd745  
> 3d65f5a060f8ecc92de9f5e0754b8f6c129cb9a243bf1504a92143ac3bc5a197  
> 11174dbaca376288fd59c66d1c00255ad6c034beff96a075e833897ef3a113cc  
> 44e77ac27a8b7d9227d95feb87bad1cc2a4ed2172c85f5e16d335a4d62d385f4  
> 00c07e354014c3fb21d932627c2d7f77bf9b4aeb9be6efb026afdbd0368c4b29  
> 3c7acdce8a37e40672eb4fba092804f9e783f284e7d52cbcf8a9f9f3cf306af7  
> 5fbf4d8d44b2e26450c1dd927c92b93f77550cebfbc267c80ff9d224c5318b88  
> 1bb6f2a9498a220ade34b64f3208287fca6699847a5fd61e0e5ed4ee56b19316  
> 4e5001c698f9f1758874067c5fb6fb2911e1f948db2cc0f289d42c61f2e2fec1  
> 747ba8be14e4d465f79a8211a26204230719ce19293725ca139f4386e57a7dff  
> fcc92f1736b5b4bd9fe503e7d6debeb7e69858fc582783c3f35e7cdece9d4feb  
> 0b00a215a42739809a55f05b6028399843e305fb285028de6efc5544b949a1ef  
> 66ababb8bd9f8b19193f56678568197350be6306f448ee9a01eeee21a487f765  
> ce129e2e14fb0de7bd0af27a8303686bde1c330c05449c1ff95591f364189e33  
> 1a01be5f08943ce03811f398f7b77aba26313dc0d0681cfad89f37db59819bc2  
> c93fbf63d82b816cd32dfc7bb0eaf7053fb27cfb78433638248010e83636ae20  
> 7f9d31d382cef81bf858b8e848897b41397c033ad5aa5c416277cf843d7218f5  
> 6c87e496ba0595ac161be8abb4e6da359d5d44c7e5afbe7de8fd689e4bb88249  
> d3212f79f33c8ccf6ba27984ed18acc86ec2297fe9c3df8fad5a00878986f2e2  
> 329e7494d516652e64c1181979fdf53b-507b4a3ab23b4821823f0aef96abc6a4  
> b73becdb7ad8b130072622ac7b2f03d450d7d0f9aae28e67dcb6724e5727f96c  
> 10bd1b5144d9a2582aaecd28eb0b80366a2675d0fd8a2f62407f8c108d367ec7  
> 11ad9d3e25bee2275f4930818bd737df1e1d79b334f990970c61763078c532d0  
> 061408f4e1f37feb0b89db3cafc496194941fade412c96ee03fc46e492df3d29  
> 8bdaf2a1e5400df06ce4d47b5b302b20cfb62e662e778a657485c6599865e393  
> 0bc3516e327fea0b5f65299366182d1e7577c9998d0cbd07891709f51fb0ac47  
> 0e1c5477ea71fdc1271e63989107b2d855c685c6c2303f297a610eb875520ec0  
> 140162b2c314e603234f2b107a4c69eb24aece3a3b6bd305101df7c26aee5f8e  
> 1dbc8aa73b64a1a607bcbe448347314d9a456d4d31a6cf846e25277b575bbb5b  
> 32aa2f66b96a95a00b032758232fc09e18439395466660b995a7d82905ef0637  
> 3ff8e17ee3c130e327a614400f594fec404c42188c0e7df0ce3b2bb3a3c1aff6  
> 57c0f3d24452b68d756577af78e809e2da12694691e62448bb132c12311360ec  
> 8ef4026b254dd0918bf3ace7741b26ff52a52ef024c721d8129c5ccfa4ccde24  
> d2b1b9642884a6839f09204135944c02c7437f7e692d07bb0d0269c4ff8316bb  
> d8d18baa934a4f1ad6777f2ca862be8d3b3a59a1fedb8d2a8e50f0a419793a15  
> e4ab0e5ecbd6c87432f08398b7f7424a248f98ff780e0adb710edd0698bf5434  
> 45510bf70bc9063392ac0514f4e26431b9c38631ed0e61b6847fe9385f5eb17c  
> e4ab0e5ecbd6c87432f08398b7f7424a248f98ff780e0adb710edd0698bf5434  
> f3727e372949d12ce9f214b0615c9d896dcf2ac0e09fcd40f4a85ff601ef01f0  
> 965a6729b89f432f61b65a7addbe376317e8fd4a188c05c6aae7f9e4a1a88fbb  
> 6f105daec2336658629042afa4f334f4949fc189404f66c09400fd2ca260eb0c  
> 267ab450a5965a525bda34deccd64bf22b5fb6cc04d811a3eec1d9289e28bc73  
> a6c8cbbe502df8407861590b97e634f51b85e4fe176bf68f86f6088ce81baaac  
> 6845a4b37e51fbf01a9573330c81483d5a438dbb1c87cbe069f72896927b4dab  
> fad5e680c181fd7415e8c03ee20735411d1259f4ae19ead0100f0929d48f3f53  
> 40232e0ffdb8fe925f9d4a1f10d5aeda208bb-58d82390ac7d1952f9219770103  
> fd9a89dc83d26994708a1d9661322df12d107693d4b483a89bf9b03c974f418c  
> b65dc44a3288b1718657d2197b1e0b22aa97d0e33b05e2877320e838da0ccb26  
> 2b24417ea8cb3271636e1747be0cc205af4bdc0d31686f024693259afdca259e  
> dffdad0ced320b9934019a75658b16cf8f6abb2e4af48cb73f66a761dfe72392  
> 0c1700551ca47143590722ae60204f1a597040d5fa6afa966d4fc3c42d82d517  
> 060c0b17a2d6fc7fb3a7a866c2013891527f1cf4602c420bc186d55b1802e382  
> 1286ff043574dffb0c0a677b102272d7ea858030dc48d6c50534dba19d95adb6  
> 1adc521a448a3588c892c98e00c9e58ba30a453b0795286b79ff2f0eaf821d25  
> 90acb46c7964404cf22b7faad5910dfa97ae8d49b45808bd9f98bb61b7bc878f  
> f0da9bf1fc8da212ae1bcb10339539f5127e62aae0ad5809c2ae855921d2ab96  
> c0e50646addd20136befa520380e4d0f8915c0e0808fd8d393a386f5af87e623  
> 2612ee5c099d6115dcbed7247cc56838fdeeb2654ba365b1b00d6294e6981f22  
> 8ea53e242e05e5da560ac9a4c286f707e888784d9c64c43ae307d78b296d258a  
> a660f95f4649f7c1c4a48e1da45a622f3751ee826511167f3de726e2a03df05c  
> 6c1f93e3e7d0af854a5da797273cb77c0121223485543c609c908052455f045d  
> 92dc59664ab3427fb4b0d2d4108f1729abb-506a2567770f7c4406e64db9aafae  
> 79114e6392bb8ffee76738e71f47131b0a2c843efe3e14f1b5e6a6d2a94c1046  
> 667f5bb-50318fe13ea11227f5e099ab4e21889d53478a8ee1677b0f105bdc70a  
> 34d21f3a543a69f34973c25bbaaedb5c8bc797d63da493cbac97bfbbedbe7206  
> a950e93ab9b2c4d1771a52fbeb62a9f2f47dc20e9921b9d23d829b949ba187b5  
> 48efaa1fdb9810705945c15e80939b0f8fe3e5646b4d4ebcace0c049d1a67789  
> 6c1af2e5cf6d6ea68c7e017d279b432d5259358b81ea1c444dc20625805b95b9  
> 0f5fb924eb5eb646ba6789db665545a08c0438e99e5a24f27c37bc0279b1a8a6  
> a1005c22c2305781fbbce5552dcc095f9ef0237023d7041eace005542fcd3d81  
> 7f2cd9ad91ddab408619d3c80eef614b91a727c35285ebd813bcd1636b2cb030  
> 7e3d97c3802cc8bc9524480170d78aa68a9de28e3a7f4ce35d103f77843a3d0c  
> f940e948586d3148e28df3e35e5671e87bc7c49525606068ac6f00783409d7aa  
> 63c97409bb2a8b-5026b459ff6c6dcc93dd12fdd8c0a4915e9298bd96dfdedb5c  
> 3b4c3c598b87a3c3b9590940b4e67861c6541316bac1e1c07a139b1892307c04  
> a113128466145973de141c4e5c5199e5474050edd4d9225463d0527d68935ef0  
> ef633a38fb49a81a30fe8977dff378bb9e89f849ceceb709cbcf76272f92c402  
> cc01324cbefb6d79e3a7ea1031edb6256fb3d40832ea621913aadda70e08a3b9  
> 3271eac4d9d20044a5fc27be6d0feece31791f3889dce2788f7ef4e201ffff4e  
> 8e74b6d667d7ddb7859687fd5c599f67b62b491087d1d926037effc7f7890b43  
> 4556d3c5e6a3322fcb39da3ef5b36d541bab70fa2f68a12e52c3de41bef092a6  
> 181a15d583d1ba4ad42b09ab62f3ef401c8cc2103e7ea2717d0571864f5440fd  
> a950e93ab9b2c4d1771a52fbeb62a9f2f47dc20e9921b9d23d829b949ba187b5  
> 308071d4e8298b4eba9f82ca7269ac58f8e39f64da515c0761406aacd110b731  
> ddb1793220d75c7126eb8af9f0d35f22e7be6998bf8ede8199c2019119b26592  
> 5b7dedcf0802547c8e18d46fbfe1a5daa91e77a6cf464c4b5f0cfc48fa235c1d  
> b8b8f57edbd70345e2134abd8917371a29e04aa37210b553879710f717b69ddd  
> 6b1db4f891aa9033b615978a3fcfef02f1904f4eba984ba756ff5cd755d6f0b4  
> 099c2d8c3c34a24f6ed3cbf5c4ff6b22312546f2c3881281b7cc66ebff899136  
> 70f1d1b35ee085768aa75f171c4d24b65d16099b2b147f667c891f31d594311b  
> 3da0189884e07adfe946ef8f214fa9ec1c01bf093d69418563368f39fdc98e12  
> 216f9f9c3e69c6723203afb79ee91917eff7707312058d7e9858d70bfb6acf92  
> f85e706123bedf3b98eb23e2fb4781e2845b2b438aa0f6789c2b496bfb36d580  
> 18b8ab327177cbde47867694d3d7acb93c83237d2418271f1020fe943760c026  
> 23f30fa4e9fe3580898be54f8762f85d5098fd526a51183c457b44822446c25a  
> 276f4008ce6dcf867f3325c6b002950cbd0fdb5bf12dc3d3afb1374622820a4e  
> 309c87b34966daecd05c48b787c3094eeed85b5f23ec93b20fc9cdbf8ff9b-586  
> 47c65ef4d6b0ffe7109c588e04575dcf05fdf3afe5796078b4f335cb94c438b7  
> 502a8d1e95c21b5dc283ef4877ca2fe2ba41570bd813c47527fca2fb224d5380  
> 5e6b5a9c0849db8ca0696a16c882d6945a62e419bd646f23d4d00533bbe9bca5  
> 6e0cb7518874437bac717ba1888991cee48dfaca4c80a4cbbbe013a5fe7b01a6  
> 83cf9d2244fa1fa2a35aee07093419ecc4c484bb398482eec061bcbfbf1f7fea  
> 87f0416410ac5da6fd865c3398c3d9012e5488583b39edacd37f89bc9469d6a9  
> c6a68fac895c0b15d5cbbba63f208e5b0a6f3c1d2382b9465375d1794f447ac5  
> c7aedc8895e0b306c3a287995e071d7ff2aa09b6dac42b1f8e23a8f93eee8c7a  
> d374ef30aa17f8bad0fb88d0da47f4038669c340d4c7fc2ff6505b07c17fdf65  
> dfc90f64139b050cf3c72d833e1a7915af1bd689ece7222b9ac2c8426a0bfd0a  
> 9a5be852afef127b5cbe3af23ef49055677b07bcaca1735cf4ad0ff1e8295ccb  
> 7ba5e623ad2e09896f0e1d1167758bcf22a9092e4a65856f825a2b8740e748f6  
> edb21b3f6f52ab0d0e17aca7e658a6e3f9ce98002433810612562b8e6ab41920  
> 0cf40fbce8a48bfc5068ac24ec1dd1f828af31fe3cff0342003d12b0ea561dcf  
> 4a0ababa34024691dc1a9e6b050fe1e5629220af09875998917b1a79af4e2244  
> 52c7bb3efafdd8f16af3f75ca7e6308b96e19ef462d5d4083297da1717db8b07  
> bcac3fee6182a64764e88b4ed4f78cc071f297c501746df6473b0e9e679b3b43  
> aa9b742267bba71507a644ea4ee52a0f118ee6d595bd7eac816a8e8ee0246427  
> 55f240467cf2c0891484d97ded9e0c53b259a88814b6f1c78a8961bda58c9377  
> 49006f7529453966d6796040bb1c0ab2d53a1337c039afe32aaa14a8cce4bf0e  
> 08de8a1103ccd7980a9900e2ceccdef0fe4db6bd06184eb628bfbcf76a7ff997  
> 2eb1056cc176747c1be4b115be90cc7ee26da11a597cff6631da54c517d1a15c  
> 436dde0fb44f95371832a55e56ed9ee9cb22f5323ce0d2a4cdcd61cbab713503  
> c05dbec1aaa11703195c743433a4319d49180c7fbd9a962e162cacd6b605ddd9  
> b919fbd354654a7bf99db7206adf6a5fba9ce73ee3fedb6d08ed932ee527f301  
> bfead4ccc3c16dee5f205b78e12aaaa2b33bdedbc57e22a4dbc48724f13f6277  
> eddd3ce6d39909be6fd5a093c2798a0c9113769b8f0f24a038449b409232472a  
> 22f4a87053769ae21efa8945a83e46df2f56e8f01a66f156cacf5ef6b6a8262a  
> a3631d6012b72a63b0f1b4a013d0971ea8505ee3db32d4a0b7b31cb9ba8dd309  
> 1ad535854fe536fd17aa56ae82f74872d6fad18545e19950afa3863bcbcf34eb  
> 9d46a0509291bf3365771f6ad53e213ffb-58e4926f11365687f4a11fd0f03855  
> brokenna.work  
> etterismype.co  
> idwhitdoe.work  
> ithconsukultin.com  
> learnataloukt.xyz  
> rsonalrecom.co  
> yflexibilituky.co  
> yeconnected.com  
> ableawid.com  
> airplanegoobly.com  
> baganmalan.com  
> balljoobly.com  
> balokyalokd.com  
> boogilooki.com  
> bookimooki.com  
> carfunusme.com  
> carmoobly.com  
> chairtookli.com  
> chookiebooki.com  
> choopinookie.com  
> ckgrounda.com  
> computermookili.com  
> dubifunme.com  
> dudesurfbeachfun.com  
> exkcellent.com  
> funbeachdude.com  
> ketobepar.com  
> kooblniplay.com  
> letfunhapeme.com  
> lookiroobi.com  
> lookitoogi.com  
> madorjabl.com  
> malanbagam.com  
> mokkilooki.com  
> myeducatio.com  
> nakasulba.com  
> ndinterper.com  
> ndworldwi.com  
> nookiespooti.com  
> oempafnyfi.com  
> saveifmad.com  
> siwoulukdli.com  
> slootni.com  
> sonalskills.com  
> tabletoobly.com  
> toogimoogi.com  
> toukfarep.com  
> uiremukent.com  
> ukrawinrusyes.com  
> utfeablea.com  
> voobmijump.com  
> xoomitsleep.com  
> yalfnbagan.com  
> yalokmalos2.com  
> yescoolservmate.com  
> yourretyeq.com  
> tcaukthw.com  
> tooblycars.com  
> koooblycar.com  
> rooblimyooki.com  
> yooblygoobnku.com  
> playkooblni.com  
> rockslootni.com  
> muendakere.xyz  
> mployeesihigh.xyz  
> adiingsinsp.xyz  
> ajorinryeso.xyz  
> ktyouexpec.xyz  
> learnataloukt.xyz  
> ngwitheaam.xyz  
> ptonnervent.xyz  
> ukmlasttyye.xyz  
> ukseseem.xyz  
> withyourret.xyz  
> betasymbolic.com  
> krestinaful.com  
> tobepartou.com  
> tobedirectuke.com  
> eandworldw.com  
> etobepartou.com  
> kfareputfeabl.com  
> blesasmetot.com  
> siwoulukdlik.com  
> sforourcompa.com

## 参考来源

> [Unit42](https://unit42.paloaltonetworks.com/chromeloader-malware/)

