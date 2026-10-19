思科和其他安全公司最近发现了一系列针对航空业的攻击活动，分析都主要集中在隐藏远控木马的加密工具上。

通过 RAT
入手分析攻击者是很好的起点，分析发现这些攻击行动与大约六年前的攻击者有关。思科认为攻击者来自尼日利亚，但并没有自己开发恶意软件的能力，加密工具也是从在线论坛上购买的。

攻击者至少活跃了五年之久，过去的两年里一直针对航空业发起攻击。这些小规模的攻击让攻击者在很长时间里都保持低调，但他们的攻击行动仍然可能会产生重大影响。

## 航空业

微软发现了使用 AsyncRAT
的新攻击行动，研究发现他们使用的攻击基础设施以某种方式互相关联：![image.png-383.5kB](https://image.3001.net/images/20210922/1632316166_614b2b06643879b005c3d.png!small)

在这次攻击活动中，攻击者使用类似于以下电子邮件作为初始攻击向量：![image.png-174.1kB](https://image.3001.net/images/20210922/1632316168_614b2b0833db5b9498d8b.png!small)

这些电子邮件包含一个指向托管在 Google Drive 中的
`.vbs`文件的链接。![image.png-85.1kB](https://image.3001.net/images/20210922/1632316169_614b2b09424c5a8309923.png!small)

研究表明，该攻击者至少从 2018 年开始就针对航空业发起攻击。使用 `akconsult.linkpc.net`的文件提到了 `Trip
Itinerary Details`和 `Bombardier`。

## AKCONSULT.LINKPC.NET

通过检索字符串 `Charter details.vbs`发现该域名，这是与 `kimjoy.ddns.net`域名有关的样本之一。

该域名在 2015 年 7 月 2 日首次出现，攻击者使用了多种远控木马。并且自从 2018 年 8
月开始，样本与该域名的通信表明攻击者正在针对航空业发起攻击。

可以发现，攻击者已经活跃了很长时间。与该域名有关的样本的时间线如下所示：![image.png-382.5kB](https://image.3001.net/images/20210922/1632316170_614b2b0a3b92101cbb852.png!small)

2013 年 2 月 7 日首次出现的样本是一个包含 .NET 打包程序，该程序执行 RunPE 的三重反射，挖空自身并注入 CyberGate
恶意软件。![image.png-154.4kB](https://image.3001.net/images/20210922/1632316171_614b2b0b4032031251958.png!small)

Cybergate RAT 的配置参数之一是 NewIdentification。如上所示，使用 Akconsult
作为识别密钥的样本。该参数由恶意软件构建工具定义，以便可以区分多个运算符。攻击者经常使用 `Akconsult`，用它作为用户名等。

该样本使用的 C&C 域名是 `opybiddo.zapto.org`，调查发现 AKconsult 与蠕虫创建者之间没有任何关系。

在 2012 年 9 月到 2014 年 5 月期间，所有的样本都使用相同的恶意软件，但具有不同的标识符。在最近的攻击行动中，该域名被用作 AsyncRAT
的 C&C 服务器，攻击者通过托管在 Google Drive 上的 VBS 文件进行分发。该服务器使用 TLS 来加密 C&C
通信，可以使用相同的证书指纹检索服务器。

AsyncRAT
与用于这些活动的同一服务器进行通信，样本可以扩大到超过五十个，对这些样本的分析揭露了另外八个域名。![image.png-346kB](https://image.3001.net/images/20210922/1632316172_614b2b0cb27dda8018372.png!small)

大多数域名在 2021 年 5 月或 6 月出现，最早的域名似乎只活跃了几天，关联的样本也较少。但是
`e29rava.ddns.net`始终处于活动状态，有一些样本将其用作 C&C 服务器。

## e29rava.ddns.net

6 月初到 7 月下旬对域名的分析显示，该域名至少与 14 个 VBS
文件有关，其名称与航空业明显相关。![image.png-388.4kB](https://image.3001.net/images/20210922/1632316174_614b2b0e128f52d39537a.png!small)

该域名几乎专门用于此类活动，其中一些文件名在同一段时间指向上一个列表中的其他域名，这些 VBS 文件是 AsyncRAT 的加密工具。

## bodmas.linkpc.net

`bodmas`也是攻击者用于 Aspire 加密的用户名之一，对相关的样本检索可以发现，在 2018 年 12 月 Nassief
已经购买了加密工具。![image.png-414.1kB](https://image.3001.net/images/20210922/1632316175_614b2b0fc576f10118036.png!small)

其中一个样本与 `kimjoy.ddns.net`有关，这是与航空业相关的域名之一，其中一个样本包含如下的 PDB
路径：![image.png-111.9kB](https://image.3001.net/images/20210922/1632316177_614b2b11752247e494da8.png!small)

此路径显示它正在使用 Aspire 加密工具，也与 `bodmas.linkpc.net`有关。

## groups.us.to

有时候分析会发现弱关联的关联关系，有一个域名看起来没有关系，但 IP
地址之间存在重叠。![image.png-102.6kB](https://image.3001.net/images/20210922/1632316178_614b2b1294e994ef9f02e.png!small)

最早在 2016 年 9 月 24 日出现的与该域名相关的恶意样本是一个简单的批处理文件，该恶意软件使用 Delphi
进行混淆并下载执行另一个恶意软件。![image.png-302.4kB](https://image.3001.net/images/20210922/1632316179_614b2b13a6fb002238e0b.png!small)

## njRAT

接着开始对 Microsoft Publisher
文件进行分析：![image.png-158.8kB](https://image.3001.net/images/20210922/1632316181_614b2b1545db74e1cb4e0.png!small)

这些 Publisher
文件都有相同的来源，最初用于测试的宏代码和后续版本的宏代码。![image.png-167kB](https://image.3001.net/images/20210922/1632316183_614b2b17ab7109c7da158.png!small)

不论如何，宏代码都会从嵌入恶意文档中的 Microsoft Form
对象中提取数据。![image.png-154.7kB](https://image.3001.net/images/20210922/1632316184_614b2b189d19a0be86930.png!small)

宏代码从 C&C 服务器下载 HTML 文件并使用 mshta，第二阶段是包含 mshta 执行的 VBScript 的 HTML 页面。代码中嵌入了
PowerShell
脚本，经过反混淆处理后如下所示：![image.png-119.6kB](https://image.3001.net/images/20210922/1632316185_614b2b197ef52fa3a8e62.png!small)

测试互联网连通性后，通过 GitHub 下载后续 PowerShell 脚本。包含三个不同的 .NET 压缩代码，第一段代码是修复 AMSI
阻止恶意软件检测：![image.png-183.4kB](https://image.3001.net/images/20210922/1632316186_614b2b1a56aa25b86ddf6.png!small)

第二段代码将执行第一个参数的可执行文件，并注入第二个参数的代码。![image.png-61.9kB](https://image.3001.net/images/20210922/1632316187_614b2b1b44d1d4b9e5bde.png!small)

注入的恶意软件是 njRAT 的变种。

## H-WORM

2019 年 12 月 13 日首次出现的恶意文档下载并执行部署在同一域名上的
Payload。![image.png-116.5kB](https://image.3001.net/images/20210922/1632316188_614b2b1c07763b3f96a60.png!small)

样本包含简单的 `chr`操作，与域名
`groups.us.to`通信。![image.png-155.8kB](https://image.3001.net/images/20210922/1632316189_614b2b1d0a93a8c136fa0.png!small)

##

通过对 njRAT 样本的深入研究，发现其中使用 `https://satlahlk.github.io/msc/cl.png`下载后续样本，这个
GitHub 账户表明攻击者在巴西，njRAT 的函数名称是西班牙语。

攻击者似乎对葡萄牙足球运动员 Cristiano Ronaldo 格外感兴趣，ChRiS
是巴西人和西班牙人对他的缩写。![image.png-47.8kB](https://image.3001.net/images/20210922/1632316189_614b2b1ddbac02ab0a6e3.png!small)

在 C&C 通信中，使用
`@!#&^%$`作为字段分隔符。![image.png-334.9kB](https://image.3001.net/images/20210922/1632316190_614b2b1ea3f5c3ca0e2fd.png!small)

通过对十六进制数据（0A800600000420391B0000800800000420011400008D）的检索，发现了另外三个样本，它们都与同一个域名有关。

这些样本创建名为 `UbboSatlahlk`的互斥锁，基于此可以发现七个样本，这些都与相同的域名有关。

进一步搜索可以发现这是西班牙语网络安全论坛上的用户名，这些域名使用的大部分 IP
地址位于多米尼加共和国，该国的官方语言是西班牙语。![image.png-136kB](https://image.3001.net/images/20210922/1632316191_614b2b1fcee105e97d2ea.png!small)

这些消息是 2016 年的，与域名首次出现时间相吻合。此外，一个名为 `UbboSatlahlk`的 Skype
帐户的位置在多米尼加共和国的圣多明各，这进一步揭示了其关系。

## 攻击者

攻击者最初使用 CyberGate 恶意软件，后使用商业恶意软件。`akconsult`的早期活动与另一个黑客论坛上的
`Nassief2018`有关，统一账户还提到在 RAT 中使用 `bodmas`和
`kimjoy`作为用户名。![image.png-49.7kB](https://image.3001.net/images/20210922/1632316192_614b2b20840b2a4859188.png!small)

在与用户互动的过程中，用户还透露了他的电子邮件是 `kimjoy44@yahoo.com`，Telegram 账户为
`pablohop`，这都与后来的航空业攻击有关。![image.png-18kB](https://image.3001.net/images/20210922/1632316193_614b2b21284feba8f9d0f.png!small)

而在 Skype 中，该电子邮件地址与 `abudulakeem123`有关。

## 地理位置

通过 DNS 遥测查看 `akconsult.linkpc.net`，大约 73% 的 IP
位于尼日利亚。![image.png-118.9kB](https://image.3001.net/images/20210922/1632316195_614b2b239920dfea0d3a5.png!small)

## 其他来源

在 Twitter
上也有其他人研究过，如下所示：![image.png-409.7kB](https://image.3001.net/images/20210922/1632316196_614b2b249d0aa66ebfc7f.png!small)

## 结论

攻击者的技术水平有限，但是从持续攻击多年来看，仍然会产生很大的风险。攻击行动往往更加隐蔽，而经济利益驱使着犯罪分子不会收手。

## IOC

> akconsult.linkpc.net  
> nextboss.ddns.net  
> exchangexe2021.ddns.net  
> shugardaddy.ddns.net  
> frankent2021.ddns.net  
> hoc2021.ddns.net  
> jorigt95.ddns.net  
> 8970.ddns.net  
> reserverem.duckdns.org  
> monthending.duckdns.org  
> e29rava.ddns.net  
> 03590bca5c249fff42c5bacef39bd308c91f8630a1a19386bed3d469f99864ac  
> 04ea078080a913511d938455a2ea0bfce88597499bf791a99d8561f8870da627  
> 083217a2f03d5c9b0a8e3371afda4c6dd2402ac98d0199aee9729a4e604db603  
> 096cf7af0363489cba18a567f535f3c79cb918226563402ebfa4288d7f4f88e9  
> 0a53710820d1c060c6d46946c81417b4294898accc31c847a027c5622b7afbcb  
> 0b119b80a5676021afd368da94527fc9fe717e2abf5d94574d29bec307251483  
> 0b3f6114a06812ec6676c730de23fd0a60b15b73210ac1151417353bcf7785aa  
> 0bbdae8713cdbb85ed8508140cc98c15c13fa8a82403d5ce848737d18491673a  
> 0c8b4a611d635d0c3fd224562f334b9b0798697af52961ed0e7537413b608830  
> 0caea3fdb7fbd02733441a5e54c1b03694e2203119dd1ff2affd85ca65d76d23  
> 0d04d8a74c4bdb7401e91bff73955738788901724d73b6c42272aa188e1cd72c  
> 0ea350d81b1fde31efdace2a3a96d3bacd6da7dc972723542e1de2dfd64e79a9  
> 0f05e24cc77952658e111c0bb2bf8236fd38d2e1ed90ea9e57e53c13e89275ff  
> 108deaea533c59386bc4c8c7fbade8f1e42e629908bd516ac2a6aa45cb854ff0  
> 1103019f32dd745bffa5319de5a18c5ebc50425f5ec102a436a7de665e6b1553  
> 13ad9c1755d39149c1b643f0e5d2935aad54e9e9754052572bd055056523d905  
> 1a4e182914a3be535bdde75f9a41eef106da3113dc4c683a6bcfc45c986d101a  
> 1a8a77b55f521ca9770e3ad465e1414d74651df2dc9281988a05ad5d0cbe8769  
> 1c6978501bc6f92d9c351315640d1ebbb109bfab7bde9df2db11fa47d9fc574f  
> 1e9033edd37c1115a798e5e8a90f880025f2f7304769d86ff42e88ec90c2f5b1  
> 2192ed71606de24f8def847e758ab2415525edf8a2236cec71fc8f5393c1f80c  
> 281e900c100ad29ef512c1c188800cbdf9c85166bc24a419583f2677b1c6fd23  
> 288c2b8a892fccff6fb94aeb90ae791322892d5ac1949f19f71b1664edc19c28  
> 2a5fc364ad77f25a6655467a3b07a6cb99ece0b266a582df0de7724de2473da6  
> 2da3c027d41c6b3f913a9a21920ba6a5e5c562a3301c8a1410927a6ee039bdd2  
> 2f878e7c5238448f04422067ca97bcebd5e105886a9542ac1a2ea21e42355f9f  
> 3123f70fb616717c44599477734e0dd0aaa7efc1060d755bd6bd8f7ec89f6fb5  
> 33a5ff49f019f2dcf8a400b3f98c5eb239078b7fb64302e22dd48ce50b0b344a  
> 3566eeab1656ef8cc3f7ab32b1d13c256747a57a0d47cd8cfc37b7d4dc38061b  
> 36c0408a369712bdf6b905849d5b8e3628dcaa903e9829378466a838f2265746  
> 39b89bdc998fc9cb3c936b03156c1f185eaeec659ebabeac7b4fcb74bd75847d  
> 3dc81cbb98731bdfe2b4caba9875129475c3fa101f6d458ed79185ada5eac4fd  
> 4077f8d706a2d7cbd453f522d55e88cc7f90e84783510fa56000d800719f1852  
> 4155f4a9d33c08e9ab0d38648930591de5c5376b3b1d551b0e16047d3648e021  
> 42056770d4c7fec72a529126c4c727c715171295ea68e8f39a3b25e835c9c4a0  
> 423b5645f797efdb72ce0e973e0c0d1b166a6b74b497b0a2e791405fb09683d8  
> 4309e6dc5f9633106714d1a16f9300641d45d5062f5456cfb836d4e6d24ace95  
> 43ccf1bf3334c7238b2fbc8ab9192859eccf7535a43332f2fc16e710a2123863  
> 45a271892d1547013ff384d9f1c31195973d6513cd856175cef1cbdbee283a72  
> 4870db29a47060a2a76a3d27ab4d60ae837b221f85f218a8c0fb7eb2d2525696  
> 494e877644452516700834e3599b21a0916d80eef7eaefdbecdb1409e4b5f90d  
> 4ad69083be6c8550af2cb9e9ac749d7c3439d71b542891238a6c749f393a00d5  
> 4bce32e4f456767257a25646a70a370f5c40668c79f7a9f0aecabeddbe6dd795  
> 4da2395efa22de5392cb6e4477f5c78d45f63feafa567960dd34cf7c0470b4ed  
> 4defaa009bec775363b8d8878e592f3928333674d2cbe667e0a279367d6b62a1  
> 4e3358f2c55a09345d65387f5f85ff330ddc18ec9223b773c32990433ae3cd57  
> 4ea27173db2122ae4196e498c3149017aed3598494290b6f3de9aa81e3bfbef1  
> 4f507144c8cd77b7e2f47c9c858ea90f9374b0303fa32eabaeb5221cf954f9dd  
> 50c40dfeb02b23c2dc70cad821b22a7471a5cc87497b4a6abd8efc284a76e7e8  
> 51c548b34c112b336d9e951942ae64ac46747147c2c618e86e6880726931e3a3  
> 554daca78ae1578a4cf518079111961d36eb9e77aad70f659eec521d0d6ef4c7  
> 5571b920ae6916b848cd5d543aad4799093583160ea44248b1a7e03c9222fe9d  
> 55a1585d2deaee3dea3bcf83fee889ab9f312575d9974d09f001927ca3bfe869  
> 5ad602845c426878cdea8c4fec4b2a09e3d2a9f19cf89f2c26b0543a64c67b2d  
> 5b2dc2be60ce4e2b45f56c7e948d4cbf992bf03b491f88e9b38ba59451e94e91  
> 5c4584bbe2f314fd016b3887b57a2ad2b1d7cf963adaf74323967fb75d777fc3  
> 5ceaef4f19760db61a8537fe32f0edc51035c08f96f5bc744b32673956436139  
> 5dcc73e97d260e969d28796b8627de32b248fe15e8688e6d62fe7bbdc2dd921c  
> 5f037d9a6d3232b001d501328a679dd7966b61e70de6a89ca03ede1818fc120e  
> 623534bf150f2538edb27e51ed56b92f464adb5da8e2db378ec3a666fcb64772  
> 6385e64dce8e5cc723fba17edfddc8df6ba18ba2a05b5dd60ac474efb445789b  
> 64ad814038c37cd199b1612c22329244a66d8fca4a0f9953cdd3d1b1ee7b2f95  
> 65ca4e932133e8758c5f177ad6043b6a2d672b19eec3218019c53b3b46bf3fab  
> 68f7e8b9a1a4b69ebe4fb7a5b57b890bd006e5eebaca1337eeca99f8f2d4b745  
> 69642f95f35b3d14f1123de60819e66e59c8f125defb5-8d23b8766f498597de3  
> 6b1db53cbd5dade029bac0a6c54f2d30b6c1579f39a345e7d72383ea7bc4f38c  
> 6b642a070211563273f3ed151103c6e8c52df29e094a28624ff57af05fb8eb22  
> 6b6d52d0f98ac22702ec61144ebd27552f939dadf10a835f995328c0789668ca  
> 6d8d882611849b0e7ebbe464497c052fe027479f6814618457c9f0fa7724dac2  
> 6edf51f455af63a82726d573a00b2b55c1086ee803991a063e5832c65fb3c790  
> 6f52ecef23b4bd9b600ceecd4017a896499bee94cb28320d0828ecf84deedd45  
> 71a7e0e7e1a13de9cd9ea55220196f7d4a9e928ed433c1dc6e257c49bb5c7f56  
> 72db243b5-873aced1d539c01fd36e162cc84e72767508ce080af4ce89e3bf68c  
> 739bc1cf80e017d48165fac50f95663c602587fbe3b6102db7724bfff39f825b  
> 77f2a568d727a29761d4f9aa23b092ffb614f7a7533399fbc8bf45b2cbb84d13  
> 7b52362ef06d1a8ec159d5fb0b2f81d3ed760102eaea86480b34292b480012d2  
> 7cfa61d907f8ee9dd1d943559e59227f58d862a2705b7f673ac302f22fad4803  
> 7e3cd407085c39e851eadc767a0d78443dd7fea16a919babe9dfd78e26d13c90  
> 7eedc9a8b30e105c9d37f05ee94769778e7b02eb568847b0fe347d98d5caf026  
> 7fc3b7342be53bb3933bbc9e69b3b841bf3618896a41fdf187d7b478f96e9e0b  
> 81a058522752f8f11c5045ab81b70e673f79cc0504a9f1a565f324336064a3b7  
> 83fcedc7c7581294bfe9f19fc6c400d8cd29eda746904e18c5b687d3560e2cca  
> 8437510b14bef4d0c535dba910e1c20df0ae3a11284a44f5e1fa432accb0363e  
> 8487084cac1881bc38d783df932733f4607704f30a0b7a9f6fbcec58902510ff  
> 853ff0fa8a56c24ddd6db57f781921d2b205fa099acbfb6a23ce418e1c227307  
> 858f83bf5fbc4eaf6900d3a481f23caf0c71519a5bd949506db04853a5847f44  
> 87c7c23ff999c80b081423d40721ee44b8bf037d26d3452030b8a0f19837f27f  
> 881b95b9064783c072f033052faca44fa4d53193a1f6ce9f754e77a68c2a7b71  
> 88db2afc4b8b21fc9be21f9960e573fe8794562f4e9d952a73ed808aa8961c4d  
> 8986a01fa210c49c7b51d206a83e2cf1f6bc69bc4dc4a346b0681408e58791e3  
> 8b5-88bf5db57e8a9e4d50d62bffd0cfd154158c882533388f9e74fb26ea8d69e  
> 8cbfaa1999cc16fc5f710a6427d2bab89ac62d678a50af17664c8907aad9cf23  
> 8e655b359f96de6f88fdb2076ca78110c3b0eb77f918e8e99a4d7751ed112a7a  
> 9024b2348e6bdba41cf7979fd09150b6311f3abd4e3eb3acbf86b259dbbf2a4f  
> 907ab14013ca5b760d2a16082b315bdfc54b4e9d44985d8cfb23fa43bc719cc8  
> 91377c7c09980e48c2c7aba5a3a66d71c9c6c471ca2dc02a186c7c9e72841438  
> 940629870cba0bceef555d6b05238c3684a6954399b5a05fd2d2678a889eb8b5  
> 948b3e9997588c5fa92cf17ea3606d621ab0fdb3a41f568c42b0d03f3112a676  
> 94a3b5-867d9804f89ea9c1fc8581ba56c83a80f0e77491a380a919377c79af57  
> 9881308b05c089b44390def980246fc830b67203b963d537358db157e9dfb4fe  
> 9cd0186792e78c9f625255402fd784325b213ecbb16d53a62e3baf7c2faefdd5  
> 9dbe3ad48a5c30ec5061da57a52a845129e2042e67ebb950f34b0465fa0b5387  
> 9e94d03c8af6ca9d5ea7cfbf481970c615d0831452fe0edb2a8abcae8c190693  
> 9ed430d3d6468cd2858d36cc9aa100b0c216a2778975ade55ac7f5dc6792d584  
> 9fdd7fa506d1cecb650611897e8172e63e50486c002356eae490a2066141fd2c  
> a03fd6e9683d8f48234081d994c8b2dc8ecd132004210894c0c7b4ed97f03208  
> a1e95c6769d83724dc68855540805d53ba1a1791c19c68aa176463ba376165e2  
> a3f943c77562107b681f066faa9c06001220c37ca48f1212a6e04ad27bc645de  
> a41f3fe5481ea0c32d5a0eaf0706415cceed74075c9c752b1ccb402b04a96730  
> a4d093b5b4825d7d30d64f6a4ba80a2b1079e688ac1a576bdb3d082ff44eaec8  
> a85919e8611fd1368c4e125a0663e30cd457ca98328b8e4d1940fbb330ea5738  
> ab3b4397c9e95f9b894c89a8ddda3401ee04526336d497a8c0ee12f89f3710a3  
> ace6e1274963d34ec4f01b6a74dfb23cb0733daed1abd0611e7ac4ac7e5c8ceb  
> b39eb6aca148f2e3fb491ef8bbfae6f3ea054a7894b36b431d4fb9a86a6be9d1  
> b3d3a285e35cba08647173ca33aa0744834f91b2af6ba95a374b8c8b89f83b35  
> b536b2e629251420a9cd824acd7e955540258c78ae7a14b10a787caee251dd40  
> b6b83a3aa0dd0a9bad132e432c6e8233d796ca6b1b1b831f1a94b7f3fc46ca1e  
> b8412bb181f81254ea35558460f35867ed2e0d6bc59b0c7086124187b8ed01b4  
> b9e112ad02d419897d298b651a7d1eff532ffbcff0a49514754621422159f02a  
> 3566eeab1656ef8cc3f7ab32b1d13c256747a57a0d47cd8cfc37b7d4dc38061b  
> bbee4612529f7d934954d18b7571522a7045a05457179f83e669f8b4fce10231  
> bd84d6decb2f5405d0459a1aefe08f9d7634a4262365ceb2cd3b1a033e9c9313  
> bef717e1da549e205bf88459c537cc22bbd381d24769f399eaa49521df1b9908  
> c278e70ee10d071ee23868d91628071bb87654c299804b90e4b07b2780c2e070  
> c2efcc8fa76a41d46b7503cdfbbac52f59280fbbfa10ffe974af0b4edcf57c0f  
> c320c2809e8b986fb4ac9db15bacd6a0f04e298b6be5d77d43099f94e8c51ca9  
> c3f78dea78b0ce6bed19c3c6d160758a8fd8b3f41e0d60211396eb88d856ab9d  
> c6c6fa1e4521fc4815023611e041377d1722bbb363f6af3c0d91ed216fe5c594  
> c9e2452b4d231ce272ea3b0b887de1a6b0ddf8c68149953cf3e69866d5a9875c  
> cae455e2cfdcefa11ee64beba30ebbec180490a0f452afcc0e00733d5ff1d944  
> cb981f01466ade4d1523068432875454e8fecb303ea56ef241ac5df51ba349c9  
> cd67795d0f8c61ab6269abd53f2bacb2d9d0ae7bcf00ffaba9b8794b9ac2440c  
> cf433da0d2dbbbb026ab3feb9b6b7d44fd681ae33e56da6d41df7e3f6f2c4c46  
> cfdf291f05acac3bc6a60ab7e20574bfa745a56ea2a0e7c74e3ffee8b38427ca  
> d515a54643d4e324938d2f9ae5d66491f3ed76c2045b681237b844bda801e2f3  
> d576d9e98452ac972fce6f787353f59587732aac6be8bd948fe38b4c23bbe682  
> d75818826396ad035834ffc9bbf5f59ad811c21ab6a0bba17911bf59b131b0ad  
> d8c1ccb824ce06a0374f673803bb6247e364145984d25feeb61ae4cbbaa87861  
> d9bb02f1636ce3e2ad9a4113c3fa9510e5292bf0f63977c5c9e64952930bba54  
> da2e63cd0e4e23fa018d771a158189ce8d40756633c073695e5c1cffc50d7601  
> da4b4d0a00b1ea3d81d5fe360dcac86a120ed96617ffc067151c09ff72ff3e45  
> da79ff6d4487b461ed320011d552ef3ed4d1b1633ec4c51e91702401d0cf221e  
> db6356982c1b324e7e89336abb544b93e9fa3b09b0d1a8fcdfaa22527a5cf66d  
> e403fa45fff2bac7c2c5dfe6dd76eef07c4a707a75ce78ecd17721c931b49f66  
> e45b917d7b153fa59545b2cbb3c6437d5820aa80b5718946df1bd10401ea39b6  
> ed007a0a9c9f151652cdb12d82ad500023f001c77cb56acf9c2de44b272e8718  
> ed2645b0898b4ee7f05d140f1a06ac846fd3029116d020093575b92803468add  
> eee171c3351b6772dc32ac7cf99b95753533ba42dc941034b22be674444a39ff  
> f0565b2e110812686c2eb4ac4cfb0fef390b9bb4ce989b5-8321dcf5797ae7656  
> f72f70885f5d9d3ce506127606712aa6784cc9ae9a8f7c4375ca430d268027b7  
> f81a37d816c639fd977d7781f7fe54cc51e2e34aa3bb8bc877c74ae140025003  
> fa04dec727fa5606216775030ca542478acdbb2ebaceae945167d152bbd19a55  
> fa1c7b13454ab1857da9a6d6e69fdf328b3f13be7c700e8fa1435bce29abdd25  
> fa1c7b13454ab1857da9a6d6e69fdf328b3f13be7c700e8fa1435bce29abdd25  
> 7eedc9a8b30e105c9d37f05ee94769778e7b02eb568847b0fe347d98d5caf026  
> fb11743c878695af326b0082709abac83a45a520545d455a1fc7c2bdb7877894  
> ff8c018ecabac99723b1851b1a50cab79629fce9151ed8ee5a1a2316f5d2ec88

## 参考来源

> [TalosIntelligence](https://blog.talosintelligence.com/2021/09/operation-> layover-how-we-tracked-attack.html)

