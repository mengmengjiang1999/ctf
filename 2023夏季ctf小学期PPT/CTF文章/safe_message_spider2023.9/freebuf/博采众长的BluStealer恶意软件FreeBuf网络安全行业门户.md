## 概述

BluStealer 是一个用 Visual Basic 编写的恶意软件，具备窃取信息、键盘记录和文件上传等功能。该恶意软件家族在 5 月首次被
[@James_inthe_box](https://twitter.com/James_inthe_box/status/1395824249605025792)发现，并将其称为
`a310logger`。事实上，`a310logger`只是出现在 .NET 组件中的命名空间中的字符串。在 7 月左右，Fortinet
将同一恶意软件家族称为“新恶意软件”。最近 GoSecure 再次将其命名为 BluStealer。Avast 决定使用 BluStealer
为其命名，同时提供该恶意软件家族更全面视角及其内部运作的详细信息。![](https://image.3001.net/images/20210925/1632547983_614eb48f010a9794f3e8c.png!small)

BluStealer 主要通过垃圾邮件传播。所发现的样本大量来自一个特定的攻击活动，通过使用特有的 .NET 加载程序可以识别这些活动。

下面是两个 BluStealer 的垃圾邮件。第一个是伪造英文 DHL 发-票。第二个是伪造 General de
Perfiles（西班牙语，意为墨西哥航运公司）的发-票。

两个邮件都包含 `.iso`附件和可下载的
URL。邮件声称收件人需要打开并填写表单以解决运输问题。![](https://image.3001.net/images/20210925/1632548018_614eb4b20e5320d18ca3c.png!small)

![](https://image.3001.net/images/20210925/1632548085_614eb4f5ed9cff81bf01c.png!small)

根据遥测分析，在 2021 年 9 月 10 日至 11 日左右，BluStealer
的攻击活动显著增加。![](https://image.3001.net/images/20210925/1632548095_614eb4ffe3f2f6d85ff11.png!small)

## 技术分析

BluStealer 由一个用 Visual Basic 编写的核心和 C# .NET 内部 Payload
组成。两个组件间的差异很大，这表明恶意软件构建工具能够分别定义每个组件。VB 组件重用了 2004 年
[SpyEx](http://www.a1vbcode.com/app-2530.asp)的大量代码，在早期样本中也包含
`SpyEx`字符串。恶意软件开发者也添加了窃取加密钱包数据、查找和上传文档、窃取剪贴板中的加密钱包地址、通过 SMTP 和 Telegram Bot
API 窃取数据等。

而 .NET 组件是一个凭据窃取程序，重用开源 C# 工具（如
[ThunderFox](https://github.com/V1V1/SharpScribbles)、[ChromeRecovery](https://github.com/Elysian01/Chrome-Recovery)、[StormKitty](https://github.com/swagkarna/StormKitty)和
[firepwd](https://github.com/lclevy/firepwd)）。

## 混淆

![](https://image.3001.net/images/20210925/1632548102_614eb5068515c0b7e0918.png!small)

每个字符串都使用唯一的密钥进行加密。加密算法使用异或加密、RC4 加密或者 WinZip AES 加密。自定义的 AES 加密算法的 Python
版本如下所示：![](https://image.3001.net/images/20210925/1632548107_614eb50bc90c64e048878.png!small)

解密所有字符串的 IDAPython 程序在
[GitHub](https://github.com/avast/ioc/blob/master/BluStealer/extras/ida-decrypt.py)中。

## 反虚拟机

BluStealer 会进行虚拟机的检查。检查 `Win32_ComputerSystem`是否包含 `VIRTUA`、`VMware Virtual
Platform`、`VirtualBox`、`microsoft corporation`、`vmware`、`VMware`、`vmw`。

检查 `Win32_BaseBoard`的 `SerialNumber`包含 `0`或者 `None`。

检查下列文件是否存在：

> C:\Windows\System32\drivers\vmhgfs.sys
>
> C:\Windows\System32\drivers\vmmemctl.sys
>
> C:\Windows\System32\drivers\vmmouse.sys
>
> C:\Windows\System32\drivers\vmrawdsk.sys
>
> C:\Windows\System32\drivers\VBoxGuest.sys
>
> C:\Windows\System32\drivers\VBoxMouse.sys
>
> C:\Windows\System32\drivers\VBoxSF.sys
>
> C:\Windows\System32\drivers\VBoxVideo.sys

## .NET 组件

BluStealer 通过资源段发现 .NET 的 Payload，并使用硬编码密钥使用 WinZip AES 算法进行解密。然后执行以下来启动 .NET
可执行程序：

> C:\Windows\Microsoft.NET\Microsoft.NET\Framework\v4.0.30319\AppLaunch.exe
>
> C:\Windows\Microsoft.NET\Framework\v2.0.50727\InstallUtil.exe

![](https://image.3001.net/images/20210925/1632548120_614eb5180412d28792843.png!small)

.NET 组件不与 VB 组件通信，只窃取浏览器和应用程序的凭据，写入指定位置。VB 组件后续会将凭据文件缓慢渗出。

## 信息窃密

窃取的信息会写入 `%appdata%\Microsoft\Templates`文件夹，不同类型的数据写入不同的文件。VB
组件会定时跟踪不同文件的文件大小，等文件增大时将会被发送给攻击者。

![image.png-84kB](https://image.3001.net/images/20210925/1632548124_614eb51c5a203f5767cc3.png!small)

BluStealer 的 VB 组件还会替换剪贴板中的比特币、以太坊、门罗币、莱特币地址为攻击者自己的地址。

## 数据泄露

BluStealer 通过 SMTP 和 Telegram Bot 传输被盗数据。Telegram 的 Token 和 chat_id
通过两个命令（sendDocument 和 sendMessage）硬编码。

>
> [https://api.telegram.org/bot[BOT](https://api.telegram.org/bot%5BBOT)TOKEN]/sendMessage?chat_id=[MY_CHANNEL_ID]&text=[MY_MESSAGE_TEXT]
>
>
> [https://api.telegram.org/bot[BOT](https://api.telegram.org/bot%5BBOT)TOKEN]/sendDocument?chat_id=[MY_CHANNEL_ID]&caption=[MY_CAPTION]

SMTP 流量使用 Microsoft MimeOLE
规范构建：![](https://image.3001.net/images/20210925/1632548126_614eb51ec2b982886e956.jpg!small)

## .NET 加载程序

此 .NET Loader 已被 Formbook、Agent Tesla、Snake Keylogger、Oski Stealer、RedLine 以及
BluStealer 等恶意软件家庭使用。

### 第一阶段

和任何已知的 .NET
混淆器都不匹配，可识别的特征是资源中包含单个加密模块。![](https://image.3001.net/images/20210925/1632548133_614eb5254171fafa4d895.png!small)

查看引用可以查看哪里被解密并加载到内存中，如下所示：![](https://image.3001.net/images/20210925/1632548137_614eb5295392337275733.png!small)

程序会检查网络连接并设置持久化：

> C:\Users*\AppData\Roaming\Microsoft\Windows\Start
> Menu\Programs\chrome\chrom.exe
>
> HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run\chrom
>
> C:\Users*\AppData\Roaming\Microsoft\Windows\Start
> Menu\Programs\paint\paint.exe
>
> HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run\paint
>
> HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\User
> Shell Folders\Startup
>
> HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell
> Folders\Startup
>
> C:\Users*\AppData\Roaming\Microsoft\Windows\Start
> Menu\Programs\note\notepad.exe

模块使用 RC4
和硬编码密钥解密，以下是来自不同样本的示例：![](https://image.3001.net/images/20210925/1632548141_614eb52d002494039c251.png!small)

###
第二阶段![](https://image.3001.net/images/20210925/1632548154_614eb53a9205d956cd8d9.png!small)

接着混淆了函数调用和字符串，函数被 gzip 解压后是一个 PE
文件。![](https://image.3001.net/images/20210925/1632548169_614eb549a6a6ae325f480.png!small)

另一方面，所有的函数调用都是通过一个字段传递给
`CompareComparator`函数来进行的。![](https://image.3001.net/images/20210925/1632548173_614eb54d68bc5c86bfcad.png!small)

当调用相应的字段时，将在运行时调用
`DynamicResolver.GetCodeInfo()`以构建目标函数，通过这样在动态分析时混淆函数调用。![](https://image.3001.net/images/20210925/1632548177_614eb551938c065eaa15a.png!small)

通过 `Dic.Attr`即可处理映射的函数，查看所有函数调用后就明白程序的功能。程序会加载一个新的程序集，即解压后的
`Ehiuuvbfrnprkuyuxqv`。随后，创建一个名为
`SmartAssembly.Queues.MapFactoryQueue`的对象。最后，一个名为
`RegisterSerializer`的方法以另一个资源文件的数据作为参数被调用。

新加载的模块也被混淆：![](https://image.3001.net/images/20210925/1632548196_614eb5646bd876e0aedf0.png!small)

与前类似，额外还有代码虚拟化的开销。一旦 SmartAssembly.Queues 类被实例化，RegisterSerializer
方法将会被正确加载。![](https://image.3001.net/images/20210925/1632548209_614eb5719ccf6f887da62.png!small)

![](https://image.3001.net/images/20210925/1632548216_614eb578e1d77d3f43119.png!small)

保存加密数据的变量 `res`被传递给
`RulesListener.IncludeState`表示的函数。![](https://image.3001.net/images/20210925/1632548224_614eb580373e30627a17b.png!small)

RulesListener.IncludeState 标记 0x04000220 映射到函数
0x60000A3。![](https://image.3001.net/images/20210925/1632548228_614eb5844c36d43cfdfeb.png!small)

![](https://image.3001.net/images/20210925/1632548231_614eb58760b3b27b71212.png!small)

实际上，只要解压第二阶段嵌入的资源文件，就可以解压所有样本。

## 结论

BluStealer 重用了多个开源项目的代码，尽管其 C&C 的能力很弱，但仍然不失为一个有能力的攻击者。

## IOC

>
> https:[//cdn.discordapp.com/attachments/829530662406193185/881703391888281630/TME_delivery_status.iso  
>
> https:[//cdn.discordapp.com/attachments/829530662406193185/882099214866333706/Shipment_Receipt.pdf.iso  
> 678e9028caccb74ee81779c5dd6627fb6f336b2833e9a99c4099898527b0d481  
> 3151ddec325ffc6269e6704d04ef206d62bba338f50a4ea833740c4b6fe770ea  
> 7603f8e827ab78d5ff15be1b04b9a02821edf3bf90475295e0c7c792bc328f63  
> 7abe87a6b675d3601a4014ac6da84392442159a68992ce0b24e709d4a1d20690  
> 49da8145f85c63063230762826aa8d85d80399454339e47f788127dafc62ac22  
> 5ff29232adcc335d007ee55421d2d6bb4ac171becf2b9b9a7595d6e4b9fc13e1  
> edab175c91e078e92b57446111cb07c61e357d9a12274cab33872e14d4511ea9  
> 8ba38dfdaed05011a8f9d19eec1670efa63cce30f23609a3c00afb265aa22ad8  
> c52a0ce16c6db82bf194988a0094a4b18aec550f1953b5e9ab127c0b84f4ecca  
> 1885c2faae1cf90783c7fc9ea93506e8241232e90bdaeae4ca04a5cb305e13f3  
> e6ed1d0f3827d5a2e6fd38ec812456b62ee702bdaa460f7f6ef5298db5136df5  
> 61560f470822a249950e3d35574aae0ee9c93da31c1fd6f001c0cec97069a4fb  
> 1e41442f28a2328a8cec90459483ae5da9b21484b2bdd2b2e206e34a8f5672bc  
> 6384e3d112dfb4f7d3f2761764e491383f20cffbb7a180a087b22ef903bcc9a6  
> 037815f51ba857c16a5c98aa37a2acba3430b0d27de3abf558cda2bff50fa35e  
> b9dcf75696ba71f292246a31877cc8c833676c5c8c241e65c741711388d99bcb  
> d1c69a54577f5c6491b2979279b04c5db668e20968363d7476848d152bb94362  
> e6ed1d0f3827d5a2e6fd38ec812456b62ee702bdaa460f7f6ef5298db5136df5  
> fbab6f778d521589e9371227f25112fed34c19efa9f3cc068bdcffe304d67111  
> 620ce6c90baeaba37fb4e4ad1edcb0a862e12e1b058eaa8c41bed7439c3bd983  
> 0872abe29cc9231cdded3a44e02a7ea17f09cf2ac2bdbd7077065858829c3723  
> b340e287c5c5cd48a5d27c71808dc75c3fd3a69a6cad029db2332e19d998bb82  
> aef52ead2a03729f95962c511947226d78fe856d29ccfaacf25e1c002c0c9f92  
> 35d443578b1eb0708d334d3e1250f68550a5db4d630f1813fed8e2fc58a2c6d0  
> c783bdf31d6ee3782d05fde9e87f70e9f3a9b39bf1684504770ce02f29d5b7e1  
> 42fe72df91aa852b257cc3227329eb5bf4fce5dabff34cd0093f1298e3b5454e  
> 1c29ee414b011a411db774015a98a8970bf90c3475f91f7547a16a8946cd5a81  
> 81bbcc887017cc47015421c38703c9c261e986c3fdcd7fef5ca4c01bcf997007  
> 6322ebb240ba18119193412e0ed7b325af171ec9ad48f61ce532cc120418c8d5  
> 4932ea0c29c86544f03f9425b8088886d68a5965be8541a8d9c36a9b95eeacf9  
> 7b1fc82d47470ee3c7f8de53a959eb55febe3c4c6ba408190a877396907f8293  
> 5d5e9bc60284b01bc75bec81489654b56a739d81acce580cdff735070d9e831f  
> 43c2649b8f43a3a39f3d5f93347ac0460b9ccf910bda544e84a07769e1af34bd  
> bc52d9795f801ca6872502c6e8af05cf3730384062f3b90113abc30ff9395879  
> 304c188b1452beea8b8a1f8bd4ac64b02781665792b46df692762b18685b1ccb  
> 75839121c06dd5f7ea7a32ced2755c8913ae81f7225ef6e790c131a5554034fa  
> b2a74a9349ed9ebe01b89786e5472ac4cb437cec7bfb7107e135baa69d41e11a  
> 21f75377b964d884a9c32849b766d52f43dc05a5e53a3bf5665473abc15d7740  
> efd63437050cbce03fb4e13c4be8858d0793ceaf678ffed8e6369578037fb6e1  
> 274bcc8a907b7f1bbfceb5b0e9f0f8f6d0dbdc65d774ce135467b704f755db81  
> 7881a0b4a3b923ae091c09e3498e1513ff8872a56fbf7977777ad6776a781b0b  
> b9933e298be75df66ed2eee62207815a20ec36cbfae9b098c24739f0d712aacf  
> add711e10bfde4da3e2048a27d8c8eab084e2df5bde714437ff2dd5dc0baa505  
> andres.galarraga@sismode.com (smtp.1and1.com)  
> saleseuropower@yandex.com  
> info@starkgulf.com (mail.starkgulf.com )  
> etopical@bojtai.club (mail.bojtai.club)  
> fernando@digitaldirecto.es (smtp.ionos.es)  
> baerbelscheibll1809@gmail.com  
> dashboard@grandamishabot.ru (shepherd.myhostcpl.com)  
> logs@grandamishabot.ru  
> shan@farm-finn.com (mail.farm-finn.com)  
> info@starkgulf.com (mail.starkgulf.com)  
> netline@netjul.shop (mail.restd.club)

## 参考来源

> [Avast](https://decoded.avast.io/anhho/blustealer/)

