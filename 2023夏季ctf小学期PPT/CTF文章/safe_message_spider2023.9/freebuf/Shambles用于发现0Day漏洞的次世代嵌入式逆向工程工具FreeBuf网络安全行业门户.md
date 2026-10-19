> 这是一篇来自于国外测试用户的文章，介绍了 LianSecurity 的 SHAMBLES 在嵌入式设备逆向领域的功能和特点，也见证了 SHAMBLES
> 在海外的每一个脚印

原文引用：Shambles: The Next-Generation IoT Reverse Engineering Tool to Discover
0-Day Vulnerabilities (boschko.ca)

逆向工程一直笼罩着神秘的氛围，令人望而却步。揭示嵌入式系统中隐藏的漏洞，特别是 0-Day
漏洞，往往被视为一种特权。根据我的经验，研究物联网/集成电路逆向也是一个充满难以克服障碍的领域。 **Shambles**
旨在通过简化嵌入式系统逆向工程过程，改变这一过去的局面。

Shambles 的使命是让 **任何人** 都能 **快速、轻松地** 发现漏洞。它旨在简化和加强在物联网和工业控制系统中搜索 0-Day
漏洞的过程，而无需用户成为专家或逆向工程专业人士。

从根本上说，Shambles 是用于分析嵌入式系统二进制代码的高级集成工具包。因此，Shambles
提供了一套全面的内部应用程序，从解包、反编译、反汇编到生成静态伪代码漏洞，再到成熟的固件仿真内核、调试器等多种功能。所有这些不同的功能都无缝地融合在一个工具中，为逆向和发现嵌入式系统漏洞提供了全方位综合解决方案。

截至 2023 年 8 月，我在不到 **200** 个小时的时间里发现了 **107** 个 0-day 漏洞，并为其中的 **49** 个编写了可用的
RCE POC。预计随着时间推移，这个数字可能会进一步增长。已有约 **30%**
的漏洞已向供应商报告，但仍有大量待发现或报告的漏洞！这些漏洞主要存在于物联网设备中，涵盖了一些我们熟知且信赖的大品牌的路由器、摄像头和防火墙。这些漏洞大多涉及命令注入、缓冲区溢出/拒绝服务（BOF/DOS）以及绕过已知
CVE 的补丁等问题，而这恰恰是 Shambles 擅长识别的漏洞类型。

![1692953487_64e86b8f529226044c451.png!small](https://image.3001.net/images/20230825/1692953487_64e86b8f529226044c451.png!small)

在本文撰写时，获得 Shambles 早期访问权限的最简便方式是加入我们的 Discord 并详细阅读 “ **faq-readme** ”
部分。如需了解最新版本和动态，请在 Twitter 上关注 H4k 和 Boschk 。

作为免责声明，有必要提及的是，我与 Shambles 背后的公司 LianSecurity
保持着非正式的联系和关系。这种关系可以说是友谊与商业伙伴关系的健康结合。我们共同的目标是为未来铺平道路，让更多人了解
Shambles。我们致力于简化发现漏洞的过程，从而重新定义逆向工程。

我对 Shambles 的成功充满热情，我衷心希望物联网/逆向工程社区能认识到它的价值，拥抱它的潜力，并利用它来发现并负责地披露 0-day
漏洞，从而为提高互联网的安全性做出贡献。看到 Shambles
在这个社区中茁壮成长，我感到无比欣慰。因为它具有巨大潜力，可以增强新老研究人员和爱好者深入探索嵌入式系统领域，加强网络安全，并对网络安全领域产生积极影响。

![1692953909_64e86d3564e777fd25af2.png!small](https://image.3001.net/images/20230825/1692953909_64e86d3564e777fd25af2.png!small)

让我们深入了解一下 Shambles 公司。它是由 [Lian
Security](https%3A%2F%2Fliansecurity.com%2F%23%2Fmain%2Fhome)的 12
名工程师组成的技术团队创立，至今已经有两年多的历史。他们负责
[SHAMBLES](https%3A%2F%2Fliansecurity.com%2F%23%2Fmain%2Fproduct%2Finfo%3FproductId%3D2)、[INCINERATOR](https%3A%2F%2Fliansecurity.com%2F%23%2Fmain%2Fproduct%2Finfo%3FproductId%3D1)和
[FLEGIAS](https%3A%2F%2Fliansecurity.com%2F%23%2Fmain%2Fproduct%2Finfo%3FproductId%3D4)等软件，涵盖从软件到硬件、基本操作和维护、产品
UI 设计等各个方面。

![1692953968_64e86d7021783f0fa78eb.png!small](https://image.3001.net/images/20230825/1692953968_64e86d7021783f0fa78eb.png!small)

需要注意的是，Lian Security
是一家总部位于中国的公司，这意味着他们的根基在中国。他们团队背后的员工和我们一样，都是备受推崇的安全专家。团队中的大多数成员曾在全球百强且备受尊敬的信息安全公司工作过。我认为，如果因为地域偏见而否定他们的才能、研究成果、辛勤工作以及对技术框架的奉献，这将是一种耻辱。

该团队计划公开并开源一些非常出色的研究成果。例如，他们将分享关于
"[通过文本分类实现混淆检测](https://www.liansecurity.com/#/main/news/FjJTjIkBUQjGUXE2LPuq/detail)"
和 “[NAND
存储器转储分析](https://www.liansecurity.com/#/main/news/J_r_j4kBQKl-d7iAKGsT/detail)”
的研究。

接下来，我将向您展示 Shambles
的主要功能之一，以及我个人如何使用它来发现顺序式漏洞。当然，还有许多其他功能，我无法一一介绍。如果您希望了解更多信息，Lian Security
有一篇精彩的博客文章，详细介绍了 "[如何在 Shambles 中重现
CVE-2019-10999"](https://www.liansecurity.com/#/main/news/_reYGIMBcR9248to5h5p/detail)的过程。

Shambles 支持 **Windows、MacOS** 和 **Linux** 系统，涵盖了多种固件架构，包括 **MIPS、ARM、PPC 和
RISC-V** ，而且还计划在未来版本中集成 **intel x86** 架构 。企业可以通过特定途径在内部获取 Shambles，Lain
Security 也在考虑这种可能性，同时他们对向公司和供应商出售批量 API 调用的想法持开放态度。

![1692953990_64e86d86c309b39a2e003.jpg!small](https://image.3001.net/images/20230825/1692953990_64e86d86c309b39a2e003.jpg!small)

Shambles 的核心逆向工程引擎是
**[Reactor](https%3A%2F%2Fwww.liansecurity.com%2F%23%2Fmain%2Ffeature%2Freverse%2Fengine)**
，它用于反编译 **MIPS、ARM、PPC 和 RISC-V** 处理器的指令集、以及 **Android** APK。前端使用了
**Electron** 技术，内核部分采用 **Java** ，后端和 API 服务器使用了 **GO** 语言。

提供了有两种方法进行固件分析。第一种是通过 Shambles 桌面客户端，第二种是通过其 web
端传送门：[https://shambles.cloud/](https%3A%2F%2Fshambles.cloud%2F)。 在 web 端，您只需通过
web 界面上传固件，即可获得完整的分析报告。

![1692954077_64e86dddc4b974601767f.png!small](https://image.3001.net/images/20230825/1692954077_64e86dddc4b974601767f.png!small)

就我个人而言，我主要是使用这个云平台进行固件上传。上传和分析固件后，您将获得一份总结了一般信息和静态分析结果的报告。

![1692954097_64e86df14d63b0275a557.png!small](https://image.3001.net/images/20230825/1692954097_64e86df14d63b0275a557.png!small)

在我们进一步探讨之前，您可能会看到报告中潜在漏洞数目而感到疑惑。

![1692954129_64e86e110d28d635ca954.png!small](https://image.3001.net/images/20230825/1692954129_64e86e110d28d635ca954.png!small)

老实说，一开始我也有这样的疑虑。但在使用 Shambles 之后，您会发现它的 **准确性非常高** 。大多数 BOF
必须与其他基元连锁，而且很多时候您无法控制寄存器。尽管如此，请不要忽视分析中提供的数字，它实际上相当准确和精确。需要记住的是，Shambles 与 IDA
PRO 等工具的主要区别在于它提高了挖掘漏洞和减少不必要的人工审查的效率。

还有一个我迫不及待要介绍的功能是 **云报告生成器** 。我认为，能够下载这样的报告对供应商来说具有巨大的价值。

![1692954161_64e86e31a331ec6740cba.png!small](https://image.3001.net/images/20230825/1692954161_64e86e31a331ec6740cba.png!small)

通过该报告，您可以全面了解可能需要清理和重构的二进制文件。报告还包括有关您使用的二进制文件可能存在的任何已知
CVE。总之，如果您是供应商，拥有并了解这些信息将会非常有益。

![1692954194_64e86e52536a44cc4deea.jpg!small](https://image.3001.net/images/20230825/1692954194_64e86e52536a44cc4deea.jpg!small)

我发现自己主要使用 Windows 的桌面客户端进行操作。

![1692954230_64e86e76d8f351f425618.png!small](https://image.3001.net/images/20230825/1692954230_64e86e76d8f351f425618.png!small)

上传固件到云端后，您可以在桌面应用程序的 " **Browser All** " 视图中检索，如下所示。当然，您只能看到您的 **用户 ID**
上传的固件。

![1692954288_64e86eb078388e287a971.png!small](https://image.3001.net/images/20230825/1692954288_64e86eb078388e287a971.png!small)

未来，为了增强安全性，Lian Security
将为公共云用户实施双向证书验证功能。这将确保用户上传和生成的文件只能由用户自己访问，并且他们可以使用自己的证书对账户目录进行加密。目前，他们的实施已经相当安全。

在桌面应用程序中，" **Clone to Local** " 的功能就如您所想。一旦克隆了固件，您就可以在 Shambles
中打开它。这是桌面客户端第二种上传固件以进行分析的方法，固件会被上传到 Shambles Cloud 进行解包、分析、模糊处理等。

![1692954311_64e86ec7f3159578cccd1.png!small](https://image.3001.net/images/20230825/1692954311_64e86ec7f3159578cccd1.png!small)

固件克隆到本地后，双击 " **Local Firmware List** " 中的固件，您将会进入以下界面。

![1692954330_64e86edadbebd1aaba042.png!small](https://image.3001.net/images/20230825/1692954330_64e86edadbebd1aaba042.png!small)

" **Firware Info** " 选项卡中包含了很多信息。虽然我不会详细介绍每个功能，但我认为 " **File Password** "
功能非常有用。Shambles 可以识别应用程序固件中的硬编码凭证。

![1692954351_64e86eefeb8c3be7405fa.png!small](https://image.3001.net/images/20230825/1692954351_64e86eefeb8c3be7405fa.png!small)

虽然您确实可以使用 **Shambles Cloud** 来破解密码，但最好还是在本地进行操作。另外，" **Key Information** "
也是值得关注的。私钥和证书可以让您更深入了解正在破解的内容。如果您拥有物理机，还可以打开一些 MITM 途径。

![1692954376_64e86f08acaa4937dd08c.png!small](https://image.3001.net/images/20230825/1692954376_64e86f08acaa4937dd08c.png!small)

在主用户界面的右侧是 " **Vulnerability** " 和 " **Virtual Machine** " 的选项卡。

![1692954410_64e86f2a20a6d94509d03.png!small](https://image.3001.net/images/20230825/1692954410_64e86f2a20a6d94509d03.png!small)

以下是静态检测捕获的疑似漏洞。

![1692954447_64e86f4fe19602caba551.png!small](https://image.3001.net/images/20230825/1692954447_64e86f4fe19602caba551.png!small)

高、中、低仅是根据一些准确性指标得出的静态指标。我个人发现，大部分的命令注入都在 " **Low Vulnerability** "
部分。正如我之前展示过的，您经常会在我的直播中看到我查看这个部分，所以请不要忽视低和中等级的严重性。这并不会限制影响。

展开任何一个高、中或低选项卡，都会显示您感兴趣的二进制文件及其引发的检测/警报数量。在这里，我要强调一下，当我提到“警报”时，指的是
"可能存在潜在漏洞的怀疑"。

![1692954474_64e86f6a7c3ddc7abaa4e.png!small](https://image.3001.net/images/20230825/1692954474_64e86f6a7c3ddc7abaa4e.png!small)

如果我们点击`/sbin/ncc2`，它会显示大约 237 个潜在漏洞警报，通过展开下拉菜单，我们可以快速查看它认为存在问题的地方。这对于快速分析`%s
`、`strcpy`、`memset `等非常有帮助，我个人也用它来优先处理我感兴趣的函数。

![1692954509_64e86f8db207829c614e2.png!small](https://image.3001.net/images/20230825/1692954509_64e86f8db207829c614e2.png!small)

Shambles 的有趣之处在于，它为您提供了静态分析或触发静态分析的函数指针。如下所示，Shambles 认为`sub_49f280 `函数中存在潜在的
BOF，因为代码中有一个类似于`strcpy(&var118,get_entry_value_by_name(p1,p2,
"nextPage"))`的操作，如果`var118`的缓冲区很小，而且我们可以通过`nextPage`参数传递输入，那么这个操作就可能引发问题。对我个人而言，这有助于迅速确定哪些函数可能会易受到攻击，哪些不会。

![1692954551_64e86fb7a4271b04fa898.png!small](https://image.3001.net/images/20230825/1692954551_64e86fb7a4271b04fa898.png!small)

双击即可进入其反汇编视图。

![1692954607_64e86fef75424bb8bdf77.png!small](https://image.3001.net/images/20230825/1692954607_64e86fef75424bb8bdf77.png!small)

所使用的颜色编码如下所示。

![1692954639_64e8700f281b468fec823.jpg!small](https://image.3001.net/images/20230825/1692954639_64e8700f281b468fec823.jpg!small)

通过转到函数的 ASM 视图并单击`TAB`键，我们可以获得伪代码，感觉上和 IDA/Ghidra 很相似，但看起来更加美观。

![1692954659_64e870233afe780de94d8.png!small](https://image.3001.net/images/20230825/1692954659_64e870233afe780de94d8.png!small)

如前所述，我无法展示 Shambles
的每一个令人惊叹的功能。但我确实想要为内置的搜索工具（`Alt+T`调用）投上一些光辉，因为它确实是我用过的最好的搜索工具之一。

![1692954701_64e8704d0dd55203e7be6.png!small](https://image.3001.net/images/20230825/1692954701_64e8704d0dd55203e7be6.png!small)

通过搜索，您可以看到 ASM
视图。此外，还有字符串视图、导入视图（分析二进制文件导入的函数）、导出视图（程序执行的入口点）、段视图（二进制文件中存在的段）和十六进制视图。

让我们看看 Shambles 是否发现了有效漏洞。

事实上，`nextPage`参数似乎容易受到缓冲区溢出的影响。当`get_entry_value_by_name(p1,p2,
"nextPage")`返回的字符串长度超过 **260 字节** 时，`strcpy`可能会在`var118`缓冲区的末尾之外写入，导致缓冲区溢出。

![1692954725_64e8706524741e5402c18.png!small](https://image.3001.net/images/20230825/1692954725_64e8706524741e5402c18.png!small)

为了证明这一点，我们还要看看在 " **Low Vulnerability** " 部分发现的命令注入。实际上，该函数中还存在缓冲区溢出。通常，当出现
BOF 时，也会出现命令注入。

![1692954807_64e870b7a097a05a13c78.png!small](https://image.3001.net/images/20230825/1692954807_64e870b7a097a05a13c78.png!small)

这个函数比较长，您只需知道函数需要 3 个参数。

![1692954838_64e870d69f0db7e186998.png!small](https://image.3001.net/images/20230825/1692954838_64e870d69f0db7e186998.png!small)

然后，函数三次调用`get_entry_value_by_name`，将`p0`、`p1`、`p2`分别作为`ddnsHostName`、`ddnsUsername
`和`ddnsPassword`传入。这将是我们控制的输入，并通过`doCheck`参数传递给`ddns_check.c `端点。

![1692954858_64e870eadfccd2730fec2.png!small](https://image.3001.net/images/20230825/1692954858_64e870eadfccd2730fec2.png!small)

在给一些变量赋值并进行一些检查后，代码会调用`__system`函数，并给出一个格式化的命令字符串。这个函数会在下面看到的`noip2`二进制文件上执行`/bin/sh`系统命令。

![1692954878_64e870fece66448a98319.png!small](https://image.3001.net/images/20230825/1692954878_64e870fece66448a98319.png!small)

在这里，我们提供的输入将被 "注入 "到`%s`格式字符串中，而`%s`格式字符串是用于表示要执行命令的字符串参数的。这看起来非常有希望。

在 Shambles 中，这两个漏洞的定位和识别各耗时约 5-7 分钟。如何让这个过程变得更快？答案就是人工智能！

![1692954921_64e8712974d8f6b34d933.png!small](https://image.3001.net/images/20230825/1692954921_64e8712974d8f6b34d933.png!small)

从 **1.2.2 版** 开始，Lain Security 已将 AI 助手添加到 Shambles
中！在此之前，如果伪代码让您感到困惑，您可能会将所有内容复制到 ChatGPT 中，要求其为您解释。或者您可能会花费 15
分钟逐步分析函数。Shambles 的 AI 助手可以帮助您轻松解决这个问题。

![1693192108_64ec0facd8d973c84253a.png!small](https://image.3001.net/images/20230828/1693192108_64ec0facd8d973c84253a.png!small)

AI 助手位于虚拟机侧边栏的右下方，让我们看看 AI 助手是如何处理`sub_49f280`函数中的缓冲区溢出的。

![1693192131_64ec0fc37fdd7ccfe04bf.png!small](https://image.3001.net/images/20230828/1693192131_64ec0fc37fdd7ccfe04bf.png!small)

它的分析相当准确。我相信我们都能看到这种功能的价值。在很多方面，它比我之前给大家关于`sub_49f280`的描述和分析更好。有更多的想法和可验证的利用路径。对于我们这些在深夜喝了几瓶青岛啤酒后还在做这项工作的人来说，详细解释器提供了如下所示的易于理解的伪代码注释，让我们的生活变得更加美好。

![1693192163_64ec0fe38bd858b793005.png!small](https://image.3001.net/images/20230828/1693192163_64ec0fe38bd858b793005.png!small)

既然有了两个潜在漏洞，我们就需要验证它们的合法性。通常在这个时候，您会使用未经维护的 Ubuntu 18.04 和不稳定的 FirmAE 或 QEMU
环境，希望不会出什么问题。有了 Shambles，您就不必紧张或担心了。我们可以通过它的动态仿真器来仿真我们的固件并验证我们的漏洞！

在官方文档中，它通常被称为 " **动态模拟模式**
"，但我们称之为虚拟机（VM），它包含所有应用程序函数的静态分析。它是一个内置的运行环境，提供并支持固件动态运行。您可以执行调试、挂钩、监控和编辑固件等操作。

要访问和创建虚拟机，必须单击下图所示的下拉箭头， **从蓝色切换到绿色** ，绿色是虚拟机模式，是同步接口后的状态。

![1693192189_64ec0ffda68530e158f8a.png!small](https://image.3001.net/images/20230828/1693192189_64ec0ffda68530e158f8a.png!small)

要进入同步界面，请单击下图中的 " **Sync Emulator** " 。

![1693192214_64ec10161ca0a47c51625.png!small](https://image.3001.net/images/20230828/1693192214_64ec10161ca0a47c51625.png!small)

固件同步完成后，可以看到模式开关中固件名称的颜色发生变化（变为绿色）。

![1693192236_64ec102c8de553ea75282.png!small](https://image.3001.net/images/20230828/1693192236_64ec102c8de553ea75282.png!small)

该固件进入动态模拟（即 VM 模式）后，就能为其创建一个虚拟机。如下步骤所示。

![1693192256_64ec1040bc3f020c6f6e0.png!small](https://image.3001.net/images/20230828/1693192256_64ec1040bc3f020c6f6e0.png!small)

如果您曾经模拟过固件，就会知道通常需要对`rCS`、`init.d`或`httpd.conf`进行修改。在 Shambles
中，为了使模拟正常运行，您通常需要将硬编码的启动 IP 更改为** 0.0.0.0 **。有时，您还需要终止 Web 服务器（`httpd
`、`jhttpd`、`bao`等）的 pid，并在 SSH 控制台中手动重新启动它，我们很快将看到如何操作。这里有一篇不错的 [关于 Shambles
常见模拟调试](https%3A%2F%2Fliansecurity.feishu.cn%2Fdocs%2FdoccnoReH3epH8X3fdXJlFlxMLe%3Ffrom%3Dfrom_copylink)的文章（为方便翻译，请在页面的
TLD (.com)后添加 **.translate.goog** ）。

如果我们需要更改虚拟机的文件，我们必须通过如下所示的静态终端来进行。只能在 VM 模式下访问。

![1693190798_64ec0a8ea3f3f6bbd5238.png!small](https://image.3001.net/images/20230828/1693190798_64ec0a8ea3f3f6bbd5238.png!small)

![1693190810_64ec0a9aab8c03151a602.png!small](https://image.3001.net/images/20230828/1693190810_64ec0a9aab8c03151a602.png!small)

完成所有更改后，刷新文件系统并启动虚拟机。该固件无需任何修改即可进行模拟。我们可以单击播放按钮启动机器。

![1693190834_64ec0ab2f1a9b9888d7ae.png!small](https://image.3001.net/images/20230828/1693190834_64ec0ab2f1a9b9888d7ae.png!small)

启动虚拟机后，会打开一个新的面板，其中包含详细的错误信息、启动进程、一般任务、日志以及设备使用的输出。运行几秒钟后，我们将查看路由器是否正常启动。单击下方所示按钮启动
SSH shell，就能看到这一切了。

![1693190864_64ec0ad0320a416b504b5.png!small](https://image.3001.net/images/20230828/1693190864_64ec0ad0320a416b504b5.png!small)

这将是一个从模拟固件作为机器进程生成的实时交互式 shell。

![1693190880_64ec0ae02a2853d1b06f4.png!small](https://image.3001.net/images/20230828/1693190880_64ec0ae02a2853d1b06f4.png!small)

现在，我们已经在正在运行的固件上模拟了 SSH shell，可以检查守护进程是否已经启动，并确保所需进程正常运行。如下所示，路由器已启动并正常运行。

![1693190900_64ec0af44b6519bcda748.png!small](https://image.3001.net/images/20230828/1693190900_64ec0af44b6519bcda748.png!small)

我们现在的目标是使用 Caido 或 Burp Suite
等工具验证我们的漏洞。为此，我们需要通过浏览器访问路由器。为此，我们必须设置端口转发。以下是路由需要如何流动的示意图。

![1693191031_64ec0b775ae2f2b81154c.png!small](https://image.3001.net/images/20230828/1693191031_64ec0b775ae2f2b81154c.png!small)

如上所示，端口转发的逻辑并不复杂。虚拟机运行在云主机上，因此有必要先转发虚拟机的网络，然后再与用户的本地计算机建立连接。我们只想为路由器转发** 80
**端口。因此，我们将添加一条转发规则，如下所示。

![1693190916_64ec0b04c1cf67c06a205.png!small](https://image.3001.net/images/20230828/1693190916_64ec0b04c1cf67c06a205.png!small)

在 " **Setting** " 面板中，我们将虚拟机内部的 **80** 端口映射到 **10040** 端口。然后，我们需要前往 " **Local
Forward** " 面板。

![1693190935_64ec0b175b3fb212d5337.png!small](https://image.3001.net/images/20230828/1693190935_64ec0b175b3fb212d5337.png!small)

然后我们只需要启动端口转发即可。

![1693190952_64ec0b28b46897a5e8abf.png!small](https://image.3001.net/images/20230828/1693190952_64ec0b28b46897a5e8abf.png!small)

瞧！我们已经成功模拟了固件，可以开始通过用户界面进行交互了。

![1693190966_64ec0b36891aa37eb97c1.png!small](https://image.3001.net/images/20230828/1693190966_64ec0b36891aa37eb97c1.png!small)

现在一切运行顺利，我们将集中精力验证两个可疑漏洞。我们从基于堆栈的缓冲区溢出开始。我们再次向`ping.ccp `发送一个`nextPing`值大于
**260** 个字符的`canclePing`操作。

![1693191113_64ec0bc963f5ffd857a69.png!small](https://image.3001.net/images/20230828/1693191113_64ec0bc963f5ffd857a69.png!small)

发送这样的请求会导致应用程序崩溃。如果您尝试再次发送请求，您将无法发送，因为最初的 BOF 会导致服务器崩溃，而这基本上是一个未经验证的 DOS BOF。

![1693191145_64ec0be9d227e43d14fe4.png!small](https://image.3001.net/images/20230828/1693191145_64ec0be9d227e43d14fe4.png!small)

我们可以从虚拟机主面板上看到，由于我们的 POST 请求`canclePing`带有恶意`nextPage`输入，系统杀死了`ping`进程，导致路由器出现
DOS 故障。从下图我们可以看到，堆栈被覆盖为`0x41`，即十六进制的`A`。

![1693191168_64ec0c0060f086dc2c5c2.png!small](https://image.3001.net/images/20230828/1693191168_64ec0c0060f086dc2c5c2.png!small)

这个 BOF 会完全关闭应用程序，因此我们只需重启 VM 就能让它重新运行。

![1693191196_64ec0c1c10e8d51f5de5f.png!small](https://image.3001.net/images/20230828/1693191196_64ec0c1c10e8d51f5de5f.png!small)

我不会使用 Shambles 调试器来处理这个错误。不过，我可以说我对它毫无怨言。它做了一个调试器需要做的一切，甚至更多。

现在，让我们继续测试命令注入漏洞。我们通过`doCheck`函数调用所有内容，其中易受攻击的输入参数是`ddnsHostName
`和`ddnsUsername`，恶意输入将分别是`;/bin/ps>/www/BlogDemoCommandInjection_Hostname.txt;
`和`;/bin/ps>/www/BlogDemoCommandInjection_Username.txt; `使用 ;
作为命令分隔符来转义`/bin/sh`正在运行的二进制文件`noip2`。

![1693191210_64ec0c2a5d1a828f2d0ac.png!small](https://image.3001.net/images/20230828/1693191210_64ec0c2a5d1a828f2d0ac.png!small)

一旦向应用程序发送了 POST 请求，我们就可以使用 shambles SSH shell
来验证这些文件是否已创建，并通过运行`ps`命令来确认这些文件包含 **4316** 字节的内容。

![1693191229_64ec0c3d9b9373696893d.png!small](https://image.3001.net/images/20230828/1693191229_64ec0c3d9b9373696893d.png!small)

此外，我们还可以从虚拟机控制台日志中看到，它在抱怨未找到某些参数。这在调试或试图获得正确语法或命令注入转义时非常有用。

![1693191257_64ec0c59107944aa30d7a.png!small](https://image.3001.net/images/20230828/1693191257_64ec0c59107944aa30d7a.png!small)

![1693191279_64ec0c6f60db2c8af3cae.png!small](https://image.3001.net/images/20230828/1693191279_64ec0c6f60db2c8af3cae.png!small)

由于我们将文件写入了网络根目录，因此也可以在浏览器中查看我们的文件。

![1693191302_64ec0c869cf2025fb1e8e.png!small](https://image.3001.net/images/20230828/1693191302_64ec0c869cf2025fb1e8e.png!small)

我喜欢用 Shambles 发现的另一类漏洞是我称之为 "补丁绕过 "的漏洞。我认为它更广为人知的名称是
"补丁差异"，即交叉比较产品的易受攻击版本和修复版本的过程。

利用旧的 0-day 安全补丁是学习和了解供应商如何修复漏洞的绝佳机会。我逐渐意识到，他们的实施/修复工作通常都很仓促，而且漏洞百出。通常情况下，你会使用
BinDiff 等超棒的工具来完成这项工作，不过 Shambles 提供了一个类似的内置解决方案，我更偏向于使用它。

![1693191355_64ec0cbb34d7d3778364c.jpg!small](https://image.3001.net/images/20230828/1693191355_64ec0cbb34d7d3778364c.jpg!small)

要使用该功能，必须同时上传两个固件版本，即已打补丁版本和易受攻击版本。

![1693191377_64ec0cd13a2182dab2df1.png!small](https://image.3001.net/images/20230828/1693191377_64ec0cd13a2182dab2df1.png!small)

一旦这两个固件版本加载到 Shambles 后，您将看到扩展的固件信息，其中包含类似图表部分，如下所示。

![1693191393_64ec0ce1e41794a6a2fa3.png!small](https://image.3001.net/images/20230828/1693191393_64ec0ce1e41794a6a2fa3.png!small)

修改后的固件克隆了多少个节点，就有多少个节点。单击 " **Compare** "后，您将看到以下视图。

![1693191409_64ec0cf1cf04486193ef1.png!small](https://image.3001.net/images/20230828/1693191409_64ec0cf1cf04486193ef1.png!small)

您可以扩展任何软件包或二进制文件，以获取更多信息。这包括但不限于功能已更改，如下所示。

![1693191457_64ec0d21f1c3020805150.png!small](https://image.3001.net/images/20230828/1693191457_64ec0d21f1c3020805150.png!small)

您可以进入任何一个函数并查看其汇编代码的变化。

![1693191473_64ec0d311b25aaa3b0b46.png!small](https://image.3001.net/images/20230828/1693191473_64ec0d311b25aaa3b0b46.png!small)

因此，不言而喻，您可以点击`TAB`键获取伪代码，去理解这些补丁。

![1693191538_64ec0d72bf02a6daec5b5.png!small](https://image.3001.net/images/20230828/1693191538_64ec0d72bf02a6daec5b5.png!small)

这看起来并不强大，但是一旦你开始寻找此类漏洞并开始参考旧的 0-day 案例，你就会充分了解并使用这一功能。

有关此功能的动态演示，请查看 [H4kb4n](https%3A%2F%2Ftwitter.com%2Fh4kb4n)的推文。

<https://twitter.com/i/status/1688232137294827520>

增强 Shambles 的一个好方法是自定义检测。Shambles 拥有一个名为 BinQL 的引擎，允许您创建检测规则，进一步帮助您发现漏洞。

![1693191577_64ec0d992d6dd157dd9a2.png!small](https://image.3001.net/images/20230828/1693191577_64ec0d992d6dd157dd9a2.png!small)

BinQL 附加到 “ **ELF Vulnerability Info** " 中，最初是通过 Shambles
基本漏洞检测功能识别出的潜在漏洞。虽然名称可能让人联想它是围绕二进制文件检索的 CodeQL 的改编，但实际上并非如此。BinQL
是一种真正专有的创新。BinQL 是完全基于云的。因此，一旦您上传的固件完成解包，BinQL 可以自动执行其检测过程。您可以通过下面所示的 “
**Plugin** ” 菜单来制定自定义检测。

![1693191592_64ec0da80775f607f8d4f.png!small](https://image.3001.net/images/20230828/1693191592_64ec0da80775f607f8d4f.png!small)

使用 BinQL 的原因在于，不同的供应商和固件使用不同的函数，这些函数可能很脆弱，不能完全被 Shambles
本地摄取。例如`do_system`、`__system`、`exec_cste`等函数，如前所述，有许多输入和输出函数，其中一些是特定固件所特有的，Shambles
要原生识别和收集所有这些函数是不切实际的，因为不同的设备可能使用不同的函数。

换句话说，BinQL 允许用户为输入和输出函数定义模板，这有助于 Shambles 执行更多定制检查和验证。

在更高的层面上；BinQL
通过对中间表示（IR）层的数据流进行逆向工程来工作。通过模拟执行，引擎会评估用户的输入是否可以修改堆栈内容、执行系统命令或执行文件读/写操作。获取用户输入通常是通过检测常见的用户输入函数（如`fgets
`、`get_value`等）来实现的，此外，为了确定是否可能修改堆栈，Shambles 还会查找`strcpy`、`memcpy `等函数，这些函数在
binql 中被定义为输出函数。

打开感兴趣的二进制文件后，选择`Plugin -> Vulnerability -> Analysis`，将会出现以下网页。

![1693191617_64ec0dc1020de8cc81495.png!small](https://image.3001.net/images/20230828/1693191617_64ec0dc1020de8cc81495.png!small)

您可以在这里输入 BinQL 检测规则。这些规则是您为当前二进制文件定制的。生成规则后，单击” **Submit**
“，您的规则就会提交到云检测服务器，状态将显示云检测状态，并且在运行时不能重新提交。

以下是检测规则的工作原理。

NAME| TYPE| DESCRIPTION  
---|---|---  
name| String| Name of the function protocol  
retValue| int| Type of the return value  
Possible values:  
-1: IGNORE, current value type can be ignored  
0: OP_PRINTF_FORMAT, current value type is output format  
1: OP_IN, current value type is tainted input  
2: OP_OUT, current value is tainted output  
3: OP_SCANF_FORMAT, current value type is input format  
4: BUFFER_LENGTH, current value type is buffer-related length  
paramList| List| Types of all parameters. Possible values are the same as
above  
matchString| String| String used for matching  
matchType| int| Matching method  
Possible values:  
0: equals  
1: contains  
2: startsWith  
3: endsWith  
4: regex  
functionType| int| Type of the current function  
Possible values:  
0: The current function serves as an input source  
1: The current function can execute commands  
2: The current function may cause buffer overflow  
3: The current function is related to file access  
  
我们发现函数`get_entry_value_by_name`经常会导致
BOF，因为它传递的是用户提供的输入，而这些输入经常会被存储到堆栈中。我们正在寻找这样的情况。

    
    
    v1 = get_entry_value_by_name(p1, p2, "fromLan");
    v41 = get_entry_value_by_name(p1, p2, "ddnsPassword");
    v61 = get_entry_value_by_name(v1, v3, "WlanValue");
    

为了实现这一点，我们首先必须了解`get_entry_value_by_name(p1, p2, p3);`是什么意思。这样我们才能分配正确的 BinQL
retValues，这非常重要。因此，`get_entry_value_by_name在libleopard.so`中被定义，并命名为`get_entry_by_name`。

![1693191683_64ec0e03b488a5cb5cede.png!small](https://image.3001.net/images/20230828/1693191683_64ec0e03b488a5cb5cede.png!small)

`get_entry_by_name
`找到`p3`在`p1`中的位置，这本身并不会造成堆栈溢出，但当使用返回值时，有可能会将其推送到堆栈基数可溢出的变量中。因此，来自第一个参数的返回值被称为
**污点输出** 。这个函数的第一个参数将被称为 **污点输入**
。`get_entry_value_by_name`函数是一个生成可能导致栈溢出的输入的函数。因此它是一个 **输入函数** 。另外，BinQL
的配置将如下所示。

    
    
    [{
        "name":"get_entry_value_by_name",
        "retValue":2,
        "paramList":[1, 4, -1],
        "matchString":"get_entry_value_by_name",
        "matchType":0,
        "functionType":0
    }]
    

因此，我们将使用下面的查询来进一步识别`ncc2`二进制文件中有趣的`get_entry_value_by_name`。

![1693191706_64ec0e1ad357021e313c5.png!small](https://image.3001.net/images/20230828/1693191706_64ec0e1ad357021e313c5.png!small)

一旦服务器状态结束，“ **ELF Vulnerability Info** ” 面板上就会出现更新的 BinQL 查询内容。

![1693191722_64ec0e2aeba988db7e1f1.png!small](https://image.3001.net/images/20230828/1693191722_64ec0e2aeba988db7e1f1.png!small)

为了更好地帮助您理解 BinQL，我们提供了一些示例，因为对于初次使用 BinQL 的用户来说，可能会有些困惑。首先，我们来看一个标记 **污点输出**
的示例。

`int * web_get(int *a1, int *key, int a3, int a4, int a5)；`

函数`web_get`用于从 HTTP 协议中读取参数。第一个参数是指向所有数据的指针，第二个参数是要读取数据的键值。返回值是所需的 **污点输出值**
。匹配方法是`web_get`。 因此，我们的 BinQL 配置将是以下 JSON 格式。

    
    
    [{
        "name":"web_get",
        "retValue":2,
        "paramList":[-1,-1,-1,-1,-1],
        "matchString":"web_get",
        "matchType":3,
        "functionType":2
    }]
    

现在让我们来看一个标记 **污点输入** 的示例。

`FILE * popen(const char *command, const char *type)；`

函数`popen`可以执行命令。第一个参数是 **污点输入** 参数，其他参数可以忽略。匹配方法是`popen`。

    
    
    [{
        "name":"popen",
        "retValue":-1,
        "paramList":[1,-1],
        "matchString":"popen",
        "matchType":3,
        "functionType":2
    }]
    

最后，让我们来看一个标记 **污点输出** 、 **污点输** 入和 **长度** 的示例。

`char *strncpy(char *dest, char *src, int n)；`

如果使用不当，函数`strncpy`可能会导致缓冲区溢出。第一个参数是 **污点输出** ，第二个参数是 **污点输入** ，第三个参数是要
**复制的长度** 。匹配方法是`strncpy`。

    
    
    [{
        "name":"strncpy",
        "retValue":-1,
        "paramList":[2,1,4],
        "matchString":"strncpy",
        "matchType":3,
        "functionType":2
    }]
    

使用 BinQL 后，根据您为其生成的检测规则的功能协议，您可以预期识别出的漏洞会大幅增加。

![1693191764_64ec0e5459e52a0362d97.png!small](https://image.3001.net/images/20230828/1693191764_64ec0e5459e52a0362d97.png!small)

就到这里吧，您已经完成了阅读！还有许多功能和令人惊叹的黑客技巧没有在本文中涵盖到。务必加入 Lian Security Discord 以获得
Shambles 的早期访问权限！如果您想观看 Shambles 的实际操作，请在 Twitch 上观看我的演示！

