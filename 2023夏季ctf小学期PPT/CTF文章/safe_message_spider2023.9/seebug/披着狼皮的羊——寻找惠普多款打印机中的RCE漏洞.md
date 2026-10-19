原文：[《A Sheep in Wolf’s Clothing – Finding RCE in HP’s Printer
Fleet》](https://foxglovesecurity.com/2017/11/20/a-sheep-in-wolfs-clothing-finding-rce-in-hps-printer-fleet/ "《A Sheep in Wolf’s Clothing – Finding RCE
in HP’s Printer Fleet》")  
作者：breenmachine@foxglovesecurity  
译者：Serene@知道创宇404实验室

非技术人员热衷于销售产品或服务的技术特性，但有时候市场营销做得有些过头了，需要有所控制。如果这条规律被打乱了，那么就会导致市场的FUD（Fear
Uncertainty and Doubt）：

![](https://images.seebug.org/content/images/2018/03/85eb59b5-07ec-4f21-b6c5-075902f4b5b6.png-w331s)

上面这段宣传视频《The
Wolf》中处处表明惠普打印机是安全的，而购买非惠普的打印机则是接近于疏忽犯罪。比如，在开场黑底白字上写着“世界上有数以亿计的商业打印机，只有不到2％是安全的”，从这里开始，视频中的“狼”执行了一系列不太可能的攻击，利用不安全的打印机以获取公司网络和敏感数据，显而易见是指惠普打印机不会受到这些攻击。

尽管有[“Printer Hacking Wiki”](http://hacking-printers.net/wiki/index.php/Main_Page)和相关的[PRET](https://github.com/RUB-NDS/PRET)工具包这样非常好的资源，但似乎没有人深入研究过现代惠普商业打印机的安全性以验证惠普的安全声明。

于是我们购买了几台打印机，[MFP-586](http://store.hp.com/us/en/pdp/hp-pagewide-enterprise-color-mfp-586dn) 和 [M553](http://store.hp.com/us/en/pdp/hp-color-laserjet-enterprise-m553n)，正如惠普视频中“狼”说的，“要开始捕猎了”。

本文中讲到的RCE漏洞在2017年8月21日报告给了惠普，惠普已经修复并发布了安全公告：<https://support.hp.com/nz-en/document/c05839270>，本文涉及的所有代码我们都放在Github上：<https://github.com/foxglovesec/HPwn>

#### 一、打印机攻击向量

在上面的视频及其续集中，“狼”执行了一系列不太可能的攻击。这些攻击是毫无道理且极其不切实际的，让我们暂且忽略这些事实，来看看下面相关的打印机安全问题：

  * 打印作业安全：打印作业安全主要通过两种方式暴露出来，一个是打印机托盘中已完成的文件，会被路过的人取走；或者是在一些打印机上，攻击者可以通过网络提取或拦截打印作业。

  * 未签名的代码执行：打印机通常会免除多种类型的监测，如果攻击者能在打印机上运行恶意软件，那么它不仅能不受限制地访问打印作业，并且还不太可能被发现，成为攻击者安全的避风港。

接下来，以上面2点攻击向量为主，我们将重点介绍一系列在现代惠普打印机上测试过的安全问题。

#### 二、测试常见的打印机漏洞

我们首先回顾了打印机中现有的安全空间，过程中我们发现了“打印机开发工具包”——PRET。这个工具包包含了许多预定义的攻击方法，可以针对不同制造商的打印机。它更多的是为常见攻击提供了模板，而不是针对某个特定打印机的特定漏洞。因此我们需要做些调查，看惠普打印机可能会受到哪些漏洞的影响。

以下问题是在PRET工具包中发现的：

##### 目录穿越 - 远程存储的打印作业泄漏

PRET工具包有三种模式，每种模式都指定工具包将尝试与打印机通信的“语言”。模式分别是Printer Job Language
(PJL)、PostScript
(PS)和PCL。每种模式都有一组不同的常见漏洞，和一些常见的问题。PJL是计算机允许打印作业时与打印机通信的语言，这种语言也被扩展为具有执行一些管理任务的能力。PJL的一项功能是对打印机上文件进行非常有限的管理，例如可以存储和删除文件，但只能在特定的位置，这是使用PJL语言在文件系统上不能逃离的一个小“监狱”。

![](https://images.seebug.org/content/images/2018/03/9f612e59-b54f-41f0-b1d1-bb76358f83ee.png-w331s)

从上面截图看到我们列举在目录“/”中的文件时，根目录中，我们只能看到“PostScript”目录。

在这里一个常见的漏洞是“目录穿越”，它涉及请求特别操作的文件和目录名称试图逃离这个“监狱”。我们在两台惠普打印机上找到了一条目录穿越序列，如下所示：

![](https://images.seebug.org/content/images/2018/03/d85dcc1c-4d6f-44ab-9797-e2480596bb24.png-w331s)

不幸的是，无法从这一点检索文件内容或编写任何文件，任何尝试都会导致打印机崩溃并重新启动。

经过进一步调查，我们发现只能在一个特定路径下检索文件内容，并且目录穿越序列略有修改：

![](https://images.seebug.org/content/images/2018/03/d1fbe330-f747-42e1-a694-543c37c00240.png-w331s)

这里的“Jobs”目录是存储打印作业的地方，通过PRET有可能检索存储在打印机上任何作业的内容，如下所示：

![](https://images.seebug.org/content/images/2018/03/47b235a5-018d-4156-8813-0192ae5bffb5.png-w331s)

针对“受PIN保护的”作业和不安全的作业进行测试，结果相同，这让打印作业受保护这项安全功能变得没有那么诱人了。

##### PostScript作业操作

某些类型的打印作业可以在打印之前自动处理。例如，网络上任何人都可以将任意图像和字体放置在所有打印作业的页面上，如下所示，水印“FOO”并不属于要打印的原始文档：

![](https://images.seebug.org/content/images/2018/03/bcf4b9cf-950c-4abd-acbe-f1ea9d4897c4.png-w331s)
![](https://images.seebug.org/content/images/2018/03/ec6b67c7-77e2-4a6e-b312-7a5e47e0dd6c.jpg-w331s)

##### 不安全的出厂重置功能

PRET工具包似乎包含了两个没有记录或者至少说不明显的方法，可将惠普打印机重置为出厂默认设置，从而将“Administrator”密码重设为默认无密码。通过PJL接口和SNMP可以实现这一点，即使设备上已经设置了管理密码，在默认情况下它们都是不安全的。

![](https://images.seebug.org/content/images/2018/03/3ae9791e-3af0-4285-bb2d-d8536e36f076.png-w331s)

除此之外，即使在PJL和SNMP接口已被管理员保护的情况下，也有可能将SNMP社区字符串重置为“public”的默认值！这可以利用一个鲜为人知但惠普默认启用的功能下实现，这个功能允许打印机在启动时通过DHCP或BOOTP服务器重新配置。

每次打印机启动，当从DHCP服务器获得IP地址时，它也会在DHCP响应中查找一些特殊的配置选项。其中一个选项指定了一个TFTP服务器，打印机可以检索应用各种配置设置的配置文件。在这些设备的详细说明手册中，惠普正确指出了，任何手动配置设置优先于DHCP配置的设置。然而，在DHCP配置中有些选项允许清除手动配置的设置，包括以下内容：

  * 安全复位：将打印服务器上的安全设置重置为出厂默认值。
  * 冷复位：冷复位后重置为TCP/IP出厂默认设置。

启用这些选项的DHCP服务器配置文件将与[项目代码](https://github.com/foxglovesec/HPwn)一起发布在GitHub上。

#### 三、不安全的默认设置

受到前面测试结果的启发，我们想看是否能找到可以应用到打印机上的安全设置组合，以阻止上述攻击。具体来说，是找到管理员应该做些什么才能让任何用户都无法重置“Administrator”密码。

我们发现这是有可能实现的，但是现实环境中的管理员不太可能成功锁定这些打印机的管理界面，至少他们需要从默认值中更改以下设置，并且注意，这里没有向用户表明，这些设置与安全性有关联。我们将展示管理菜单中的完整路径，以演示打印机中这些设置藏得有多深：

  * 必须在设备的管理Web界面上设置密码，这是IT中的常见做法，也是唯一可能应用于现实世界的设置。
  * 在`Networking > Security > Mgmt. Protocols > SNMP`的`Set Community Name`需要由默认改为`public`。
  * 在`Security > PJL Security > Password`下，必须设置新密码
  * 以下设置必须禁用`Networking > Other Settings > Misc Settings > Enabled Features > TFTP Configuration File`

如果上述任何一项被忽略了，网络上的攻击者就有可能重置设备并因此获得管理访问权限。

#### 四、深入挖掘：提取操作系统和固件

我们花费了几千美元购买打印机，在找到RCE漏洞前都不会停止研究。第一步是掌握在打印机上实际运行的代码，看起来惠普采取了一些措施来防止用户从打印机中提取操作系统和固件，不过我们可以绕过这些限制。

首先，惠普送来的设备同时包含了符合FIPS标准的加密硬盘驱动器，当插入这其中一个特殊的驱动器时，驱动器上的所有数据都将被加密，如果移除该驱动器，那么没有加密密钥的话任何人都将无法读取数据。另外，即使我们能够设置或恢复这个密钥，正在使用的加密细节也不清楚，并且需要在从驱动器读取数据之前发现。

相反，我们只是删除了HP提供的支持FIPS的驱动器，并插入了不支持加密的常规东芝笔记本电脑硬盘驱动器：

![](https://images.seebug.org/content/images/2018/03/c7a7c08b-59b7-4106-8d7b-27825f72e95d.jpg-w331s)

重新启动设备后，我们可以让打印机将操作系统和固件从USB密钥安装到新的未加密的驱动器上：

![](https://images.seebug.org/content/images/2018/03/b049e942-7552-4af1-9763-68202429f3be.png-w331s)

关闭打印机，取出驱动器，就可以将驱动器上的许多文件读取到一个标准PC上。不过，一些更有趣的文件仍然难以捕捉，特别是在“/Windows/”和“/Core/bin”目录下的HP
DLL文件，我们知道这些文件存在，因为可以利用我们的目录穿越漏洞在PRET中看到它们：

![](https://images.seebug.org/content/images/2018/03/3309270e-8b1f-4741-b56a-d931138f4058.png-w331s)
![](https://images.seebug.org/content/images/2018/03/1dfb5c2b-a899-447d-892e-885ad85bbfd7.png-w331s)

不幸的是，驱动器插入PC后，我们没有找到这些目录。经过大量调查后，我们应用了两种不同的方法从这两个来源检索文件。

##### 检索/Windows/

首先是Windows目录，Linux实用程序“grep”用于对Windows目录中存在的各种文件的引用进行搜索：

![](https://images.seebug.org/content/images/2018/03/b35d38a9-f023-457f-8598-d7f2085d8498.png-w331s)

文件“NK.bin”似乎每次都会返回，经过一番调查后，发现打印机上运行的操作系统是Windows CE的一个版本，Windows
CE内核存储在/CEKERNEL/NK.bin。我们可以用公开的工具Nkbintools来提取这个Windows
CE内核的内容，并检索Windows目录的确切内容：

![](https://images.seebug.org/content/images/2018/03/7e9569f2-e2d1-4924-ba68-0bb56e71dbac.png-w331s)

##### 检索/Core/bin

目录/Core/bin的内容更难以检索，当硬盘连接到PC时，/Core/bin目录实际上是可见的，然而与/Windows/目录不同，它是空的：

![](https://images.seebug.org/content/images/2018/03/40b57611-7e9b-42ac-a3cf-e6d110eb6859.png-w331s)

没能弄清为什么这个目录表现为空后，我们做了另一个尝试。

首先，我们检查了与硬盘上的/Core/关联的分区：

![](https://images.seebug.org/content/images/2018/03/44295810-0759-40f1-a8c8-6a02dbc58010.png-w331s)
![](https://images.seebug.org/content/images/2018/03/77e819c9-e703-45f3-974d-1b683d6ae003.png-w331s)

下一步是使用Linux“dd”实用程序拍摄这个分区的图像，这个实用程序会完全忽略文件系统，并获取分区的原始映像，将其保存到本地文件中。

![](https://images.seebug.org/content/images/2018/03/bca6c75f-d394-4f14-9624-1482f9e128bc.png-w331s)

最后，应用一种称为“file
carving”的技术，这种技术通常用于硬盘部分发生故障或文件系统已损坏时的数据恢复。我们使用的工具称为“scalpel”，指定一个配置文件，它可以“分解”在原始磁盘图像“image.bin”中找到的任何可疑的DLL文件。结果看来有数百个DLL文件，其中许多是无效的，并且所有文件都有一个数字而不是文件名：

![](https://images.seebug.org/content/images/2018/03/625bfeab-069e-45a3-b442-97ca97af7384.png-w331s)

由于我们最感兴趣的是.NET
DLL的文件，因此可以使用“monodis”工具来尝试反汇编每个DLL，只打印有效的DLL文件及其名称列表。虽然脚本的输出很混乱，但足以证实我们已经提取了正在寻找的DLL文件：

![](https://images.seebug.org/content/images/2018/03/9cd7e4d1-efd6-4b28-b73b-013b02a78bbf.png-w331s)

#### 五、固件和惠普软件“解决方案”逆向

通过访问设备上运行的代码，我们可以开始深入了解打印机中的一些功能，找到是否可能导致远程代码执行，特别是与惠普软件“解决方案”安装和固件更新相关的功能。

惠普软件解决方案利用惠普的OXP平台和SDK来扩展打印机的功能，第三方公司可以开发这些解决方案，但访问SDK由惠普严格控制，任何由SDK开发的软件最终版本必须由惠普签署才能安装在打印机上，如果能找到解决这些控制的方法，就可以创建适用于所有现代惠普打印机的恶意解决方案。

过去，恶意固件更新是在各种打印机上获得代码执行的一种方法。惠普已经转向了新的固件更新平台和文件格式，似乎没有安全研究人员详细地审查过。

##### BDL格式逆向工程

惠普解决方案和固件更新都包含一个带“.BDL”（捆绑）扩展名的单个文件。这是一种专有的二进制格式，没有公开的文档，我们决定对这种文件格式进行逆向工程，它可以让我们深入了解固件更新和软件解决方案的组成。

由于固件文件庞大而复杂，为了简单起见，我们从获取第三方软件解决方案“ThinPrint”的副本开始着手，与81MB的固件更新文件相比，这个解决方案的“BDL”文件有2.1MB。首先，我们在BDL文件上使用了一个叫binwalk的工具，它用于检查二进制文件并尝试提取其中包含的任何已知文件格式。binwalk被专门开发用于对这些类型的包进行逆向工程，工具输出单个ZIP文件包含以下内容：

![](https://images.seebug.org/content/images/2018/03/541b1695-9d22-4023-bb38-24f88cd50462.png-w331s)

我们在十六进制编辑器中手动检查了压缩文件和BDL文件，以确定ZIP文件在BDL文件中的位置：

![](https://images.seebug.org/content/images/2018/03/49416346-8351-43ad-84d4-6b34ea5904f7.png-w331s)
（ZIP文件由binwalk在十六进制编辑器中提取，并显示CRC-32校验和）

![](https://images.seebug.org/content/images/2018/03/e52b4865-d582-4557-90a8-8e4eb3bbaee6.png-w331s)
（BDL文件高亮显示ZIP部分并计算CRC-32）

请注意，在上面两个截图中，我们已经计算了十六进制编辑器中选定部分的“CRC-32”校验和。在第一种情况下，对于ZIP文件，CRC-32校验和是在整个文件中计算的。在第二种情况下，对于BDL文件，CRC-32是根据我们怀疑包含压缩文件的部分进行计算的（基于前几个字节匹配）。当两个CRC-32校验和达到相同的“6D
AC 9A 2F”值时，我们猜想得到了证实。

还要考虑上面十六进制编辑器中用红色圈起来的部分，注意“2F 9A AC
6D”就出现在ZIP文件开始之前，只是ZIP文件的CRC-32校验和，其字节顺序相反。

看到这个，我们对zip文件做了一个小修改（只是修改了其中一个文件的内容），计算了修改过的ZIP的CRC-32校验和，并用修改的ZIP文件替换了BDL中的ZIP文件。BDL文件中的CRC-32校验和进行更新以匹配新修改的ZIP文件，并将BDL文件上传到打印机。

不幸的是没有成功，出现了以下错误：

![](https://images.seebug.org/content/images/2018/03/d5be8258-763c-4a43-8fe9-ed5935db6648.png-w331s)

进一步调查在打印机调试日志文件中发现了以下内容：

![](https://images.seebug.org/content/images/2018/03/ba52e60f-97c5-410b-8ffd-b0f8bd193eb5.png-w331s)

很明显，当ZIP文件被替换时，还有额外的CRC校验和被损坏。经过调查，包括编写自定义python脚本以识别文件中的CRC-32校验和后，ThinPrint
BDL文件中推导出了以下字段：

  * 0x14-0x17 = CRC32 of 0x929 to 0x938 (IPKG header)
  * 0x931-0x934 = Length of IPKG structure
  * 0x94d-0x950 = CRC32 of 0xd76 to 0xe89 (ZIP header)
  * 0x929-0x92a = Distance of IPKG structure from the start of the BDL file
  * 0xe76-0xe77 = Distance of ZIP from IPKG header
  * 0xe7e-0xe81 = Length of ZIP file
  * 0xe86-0xe89 = CRC32 of 0xe8b-EOF (ZIP file binary)

有以上知识还是不够的，当BDL文件上传到打印机时，更新上面列出的所有校验和、长度，仍然导致某种校验和失败。

在这里我们决定采取替代路径，理论上可以创建一个和原始ZIP文件同样长度和CRC-32校验和的ZIP文件，如果创建完成，就不需要更新BDL文件中的任何字段！

我们用Python编写了一个自定义工具来完成这项工作，放在我们Github的[知识库](https://github.com/foxglovesec/HPwn)中。这个工具允许修改原始BDL文件，通过替换一个相同长度和CRC-32校验和但任意不同内容的ZIP文件。这个工具有点破解，可能只适用于ThinPrint
BDL。

以这种方式修改的BDL文件上传到了打印机并确认可用，但是还没对代码进行恶意更改。当我们试图替换任何ZIP中的DLL文件时，我们得到了DLL签名验证错误。

#### 六、逆向工程固件签名验证

一旦对BDL文件的工作原理有了总体的了解，我们就开始检查固件更新过程和周围的安全控制。首先，我们只是在一个十六进制编辑器中检查惠普的固件更新文件，相关的文件类型是“.BDL”，有人指出，在文件末尾存在一个签名块：

![](https://images.seebug.org/content/images/2018/03/dc4631cd-7525-4197-a8a6-1b036953158d.png-w331s)

这个签名块不在“ThinPrint”解决方案BDL中，这说明软件解决方案包和固件可能会以不同方式处理。

根据签名块中的信息判断，似乎正在使用该文件的行业标准签名验证，特别是使用SHA256的RSA。但是，正在使用安全加密算法并不意味着该文件有安全验证。一些常见的执行错误都可能导致签名验证不安全。

为了找出代码中签名验证执行的地方，我们上传一个仔细操作的固件文件到设备，注意不要以与ThinPrint解决方案相似的方式，使校验和或长度无效。进行到这里，从打印机的调试日志中产生了以下错误：

![](https://images.seebug.org/content/images/2018/03/380479fb-128b-4a03-ae2e-f739b8b9ce90.png-w331s)

查看从打印机中提取的反编译代码，确定这个消息是在类文件`HP.Mfp.Services.Installation.Fim.Fim`中生成的：

![](https://images.seebug.org/content/images/2018/03/4b7e0458-1698-40d2-af11-865d46de41ac.png-w331s)

进一步的逆向带我们到了正在执行签名验证的位置，快速审查代码后，我们没有发现严重的错误能容许绕过或操纵固件签名验证。

##### 惠普解决方案包的DLL签名验证逆向工程

我们已经对BDL格式进行了部分逆向，在打印机上执行恶意代码的第一步，显然是用修改过的DLL文件替换在BDL中打包的DLL文件之一，然而并没有成功，在打印机调式日志中，出现了如下的错误：

![](https://images.seebug.org/content/images/2018/03/34ed36dc-b703-4393-9d54-de3cac5d79c3.png-w331s)

这个详细的错误信息，直接为我们指向了正在执行签名验证的代码位置，“HP.ExtLib.Package.Process”：

![](https://images.seebug.org/content/images/2018/03/b6dc8796-27b8-46c3-9998-36424fb192bd.png-w331s)

深入探索一下，我们检查了“signedObject.ValidatePeSignature”下的代码：

![](https://images.seebug.org/content/images/2018/03/d64333ea-6f1a-48c1-bbc4-ea3853bc81f7.png-w331s)

快速审查这段代码，我们怀疑这里可能会出现一些问题。在第11行，从DLL文件的第60个字节读取了一个数，在第14行和第15行，从DLL文件读取了另外两个数字读入变量int32_2和int32_3。在第19-22行，这两个新变量用于指定一部分加载到名为numArray2的数组中的DLL文件。从第22行开始，其余代码在numArray2上运行。

仔细检查上述过程，我们怀疑可能可以这种方式操作读入int32_2和int32_3的数字，因为验证签名的DLL文件部分可以与打印机上运行的实际可执行代码分离。

#### 七、构建恶意解决方案

##### 打破惠普对DLL文件的数字签名验证

为了验证上述怀疑，我们用C＃重新实现了打印机上执行签名验证的算法的一个接近完全副本。然后，该程序在Visual
Studio调试器中运行，并使用由惠普签名的有效DLL文件作为输入。在上面“ValidatePeSignature”的代码示例（下面新程序中的第65行）中，执行在第22行中断了，这是从DLL文件中读取numArray2的位置：

![](https://images.seebug.org/content/images/2018/03/ca173e2e-ce48-4a3a-864b-5349eebc63e5.png-w331s)

请注意，这时我们可以在上面的调试窗口中看到int32_1，int32_2，int32_3和numArray2的值，numArray2的内容被转储到磁盘上的文件“Foo.txt”中：

![](https://images.seebug.org/content/images/2018/03/c28db64f-1b14-46c8-a0d7-135d4345f3c7.png-w331s)

我们的计划不需要了解这些内容的实际含义，因此没有分析。

接下来，在HxD十六进制编辑器中复制粘贴，将文件“Foo.txt”追加到名为“HPwn.dll”的自定义未签名的.NET
DLL的末尾，红色字体的字节是新加的：

![](https://images.seebug.org/content/images/2018/03/6186b47b-96fe-4d80-af85-563de9333b5f.png-w331s)

接下来必须小心操作DLL文件，以便惠普签名验证算法将文件末尾定义的新字节加载到numArray2中。仔细分析上面的ValidatePeSignature代码，并结合十六进制编辑器中相应的字节值，显示以下内容：

  * int32_2 is loaded from the DLL at offset = int32_1 + 152 = 128 + 152 = 280 = 118 hex
  * int32_3 is loaded from the DLL at offset = int32_1 + 156 = 128 + 156 = 284 = 11C hex

在这些偏移量处检查我们新加的未签名DLL文件，我们看到它们当前设置为0：

![](https://images.seebug.org/content/images/2018/03/e3ae192b-c7a0-4719-9c00-9434ddc0cfce.png-w331s)

显而易见的问题是，我们应该如何设置int32_2和int32_3的值，以将Foo.txt中粘贴在DLL文件末尾的字节读入numArray2中？

再次检查ValidatePeSignature的代码，第20-22行有所相关：

    
    
    if (file.Position != (long) (int32_2 + 8))
    file.Seek((long) (int32_2 + 8), SeekOrigin.Begin);
    file.Read(numArray2, 0, int32_3 - 8);

因此，读入numArray2的字节将是DLL文件中位于int32_2+8和int32_3-8之间的DLL文件中的字节。

我们想强制该算法读取已插入到DLL文件末尾的“Foo.txt”的内容，这个文件从0x1200开始，长度为11360字节（如果你要验证这些数字，请参阅上面Foo.txt粘贴到DLL中的截图，调试器的截图显示了numArray2的长度）。考虑到这一点，算出int32_2和int32_3值很简单：

  * int32_2 = 0x1200-0x8 = 0x11F8
  * int32_3 = 11360 = 0x2C68

如下图所示：

![](https://images.seebug.org/content/images/2018/03/64949ead-eecd-40ad-ac78-08680b42bc4b.png-w331s)

现在，针对这个新的DLL文件HPwn.dll运行签名验证算法，我们得到以下结果：

![](https://images.seebug.org/content/images/2018/03/63abbed0-8dc1-445f-a148-fdcecbd61230.png-w331s)

#### 八、获得任意代码执行

构建了我们自己的惠普“解决方案”软件包的方法，以及另一种方法来绕过他们的数字签名验证机制，剩下唯一的障碍就是构建与惠普平台兼容的恶意软件。

##### 创建恶意软件

为了创建恶意软件，我们以HP ThinPrint客户端主类中的反编译代码为例：

![](https://images.seebug.org/content/images/2018/03/43e75a2a-3348-4673-a45e-d0dff647a695.png-w331s)

幸运的是，这段代码非常简单。只要有从打印机中提取的HP.ExtLib.dll副本，完成一个山寨的应该是比较直接的。下图展示了大多数我们修改后的成果，这只是相同的方法和接口，但执行不同的操作：

![](https://images.seebug.org/content/images/2018/03/22e43c53-f48e-424b-bdf4-08d3a06ed394.png-w331s)

这个项目的副本将在[GitHub](https://github.com/foxglovesec/HPwn)上发布。“DoBadStuff”功能只需执行以下操作：

![](https://images.seebug.org/content/images/2018/03/7e417166-fb22-4332-b0b2-abb6f1c42e94.png-w331s)

  1. 从 <http://nationalinsuranceprograms.com/blar> 上下载文件
  2. 执行打印机上文件中指定的命令
  3. 等待5秒
  4. 重复操作

必须克服的一个技术障碍是，项目需要编译的.NET Compact Framework版本仅包含在Visual Studio 2008
Professional中。具体来说，这个项目需要针对“Windows CE设备”：

![](https://images.seebug.org/content/images/2018/03/7da8cf91-0046-48ae-845c-5528704449fe.png-w331s)

最终我们取得了Visual Studio 2008 Pro的副本，并成功构建了该项目。

##### 测试恶意软件

在执行新加的DLL文件中的签名验证过程之后，使用[我们的GitHub中的python代码](https://github.com/foxglovesec/HPwn/blob/master/BDL_Patcher/hp_solution_patcher.py)将该DLL加载到BDL中，修改后的BDL文件成功上传到打印机：

![](https://images.seebug.org/content/images/2018/03/ec11819c-dced-4fed-9a7b-9659a176d3a5.png-w331s)

回想一下，我们的恶意软件从<http://nationalinsuranceprograms.com/blar>中下载文件，在这个情况下，文件“blar”包含一个简单的命令，只是让打印机“ping”我们的另一台服务器。我们可以通过监视第二台服务器，来确认该命令成功执行：

![](https://images.seebug.org/content/images/2018/03/22d66c55-a065-4e5d-a25d-dafcc98842b5.png-w331s)

托管HTTP服务器上的文件之后，我们立即看到打印机为文件发出请求：

![](https://images.seebug.org/content/images/2018/03/daf9c6e9-129f-4b73-ab92-dba64603caf5.png-w331s)

在打印机上实际运行文件中的命令立即传送到了第二台服务器，在这种情况下，服务器被配置为打印出对其请求的任何域名。它开始打印“twoping.dns.evildomain.net”：

![](https://images.seebug.org/content/images/2018/03/d2014863-4240-4d99-8dfd-6d875bb7ed1e.png-w331s)

#### 九、未来的工作

过去对惠普打印机的研究似乎因为缺乏可用的固件文件和OXP SDK而受到阻碍。例如下面PrinterHacking Wiki所说的：

> 对于较新的设备，惠普使用基于“开放式扩展平台”（OXP）的Web服务，而不是使用没有公开可用的SDK。

这是OXP SDK的可用信息，并且没有关于BDL文件格式的信息，本报告为进一步工作奠定了基础，特别是在进一步深入代码审查后，对以下领域的工作可能更有成效。

##### 打印机开发模式

在审查源代码时，我们注意到惠普打印机可以进入“开发”模式。一旦启用这个模式，就可以自由安装未签名的固件更新。我们在HP.Mfp.Services.Installation.Fim.SignedConfigBundleRepository中找到了唯一可以启用开发模式的代码路径：

    
    
    protected override void InstallMfgConfigPackage(FileInfo[] files)
    {
    if (files != null &amp;amp;&amp;amp; files.Length &amp;gt; 0)
    {
    foreach (FileInfo file in files)
    {
    if (!(file.Name == "pak.hdr") &amp;amp;&amp;amp; new SecureNvramBundle().DecryptAndValidateManufacturingPackage(this.GetFileContents(file)) != null)
    {
    this.TransitionToDevMode();
    LogManager.InfoLog.Log("HP.Mfp.Services.Installation.Fim", 10030852U, new KeyValuePair&amp;lt;string, string&amp;gt;("MESSAGE", "Signed Mfg Config Bundle install succeeded. Development Mode Activated."));
    return;
    }
    }
    }
    LogManager.WarningLog.Log("HP.Mfp.Services.Installation.Fim", 10030853U, new KeyValuePair&amp;lt;string, string&amp;gt;("MESSAGE", "Signed Mfg Config Bundle digital signature validation failed"));
    }

如果有人能够获得有效的“制造配置包”并将其安装到打印机上，就将启用打印机上的“开发”模式，一直到下一次打印机重新启动。因为“制造配置包”不容易找到，所以这个假设没有经过测试，同时我们也不确定别人会如何安装它。

##### 选择固件更新机制

有许多方法可以更新惠普打印机的固件，大多数管理员都会意识到可以通过打印机的Web界面和“Web Jet
Admin”客户端安装固件更新。固件也可以在启动时通过BOOTP /
TFTP选项安装，但是经过测试后，我们没有找到正确的选项安装成功。另外，惠普打印机上的安全设置页面表明可以通过端口9100利用打印作业安装固件：

![](https://images.seebug.org/content/images/2018/03/fb834107-7801-4786-866b-33a98851140f.png-w331s)

没有关于这个功能的文档，不过这个有可能是能成功的。

特别有趣的是，这些可选择的固件更新机制中，有些可能是忽略执行签名验证的替代代码路径。例如，HP.Mfp.Services.Installation.Fim.Fim.RemoteInstall中的方法似乎是一种要求某种固件更新或安装的功能，我们对这种方法进行快速代码审查，发现其中不包含任何表示数字签名正在验证的代码。还需要更多的研究来验证这一发现。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/549/>

