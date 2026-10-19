**Golang (Go)是一种相对较新的编程语言，发现其编写的恶意软件并不常见。 然而，用Go编写的新变种正在慢慢出现，这给恶意软件分析人员带来了挑战。
使用这种语言编写的应用程序体积较大，在调试器下看起来与使用其他语言（如C / C ++）编译的应用程序有很大不同。**

最近，我们观察到一种新的Zebocry恶意软件变种，用Go编写（详细分析可在[此处](a%20href=)获得）。我们在实验室中捕获了另一个用Go编写的恶意软件。这一次，我们将Trojan.CryptoStealer.Go视为一个非常简单的窃取程序。本文将详细介绍其功能，同时展示可用于分析Go编写的其他恶意软件的方法和工具。

## 分析样本

Malwarebytes将此窃取程序检测为Trojan.CryptoStealer.Go：

> **·** 992ed9c632eb43399a32e13b9f19b769c73d07002d16821dde07daa231109432 **  
> **
>
> **·** 513224149cd6f619ddeec7e0c00f81b55210140707d78d0e8482b38b9297fc8f
>
> **·** 941330c6be0af1eb94741804ffa3522a68265f9ff6c8fd6bcf1efb063cb61196 –
> HyperCheats.rar (原始安装包) **  
> **
>
> **·** 3fcd17aa60f1a70ba53fa89860da3371a1f8de862855b4d1e5d0eb8411e19adf –
> HyperCheats.exe (UPX 加壳) **  
> **
>
> **·** 0bf24e0bc69f310c0119fc199c8938773cdede9d1ca6ba7ac7fea5c863e0f099 –
> 脱壳之后

### 行为分析

在底层，Golang调用WindowsAPI，我们可以使用典型工具跟踪其调用，例如PIN跟踪器。 我们发现恶意软件会在以下路径中搜索文件：

    
    
    "C:\Users\tester\AppData\Local\Uran\User Data\"
    "C:\Users\tester\AppData\Local\Amigo\User\User Data\"
    "C:\Users\tester\AppData\Local\Torch\User Data\"
    "C:\Users\tester\AppData\Local\Chromium\User Data\"
    "C:\Users\tester\AppData\Local\Nichrome\User Data\"
    "C:\Users\tester\AppData\Local\Google\Chrome\User Data\"
    "C:\Users\tester\AppData\Local\360Browser\Browser\User Data\"
    "C:\Users\tester\AppData\Local\Maxthon3\User Data\"
    "C:\Users\tester\AppData\Local\Comodo\User Data\"
    "C:\Users\tester\AppData\Local\CocCoc\Browser\User Data\"
    "C:\Users\tester\AppData\Local\Vivaldi\User Data\"
    "C:\Users\tester\AppData\Roaming\Opera Software\"
    "C:\Users\tester\AppData\Local\Kometa\User Data\"
    "C:\Users\tester\AppData\Local\Comodo\Dragon\User Data\"
    "C:\Users\tester\AppData\Local\Sputnik\Sputnik\User Data\"
    "C:\Users\tester\AppData\Local\Google (x86)\Chrome\User Data\"
    "C:\Users\tester\AppData\Local\Orbitum\User Data\"
    "C:\Users\tester\AppData\Local\Yandex\YandexBrowser\User Data\"
    "C:\Users\tester\AppData\Local\K-Melon\User Data\"
    

这些路径指向从浏览器存储的数据。一个有趣的事实是其中一条路径指向Yandex浏览器，该浏览器主要在俄罗斯流行。下一个搜索的路径`"C:\Users\tester\Desktop\*"`找到的所有文件都复制到在％APPDATA％中创建的一个文件夹中：![1.png](https://image.3001.net/images/20190222/1550840033_5c6ff0e181a2a.png!small)“Desktop”文件夹包含从桌面及其子文件夹复制的所有TXT文件。
我们的测试机器示例：![2.png](https://image.3001.net/images/20190222/1550840042_5c6ff0eabd808.png!small)搜索完成后，文件被压缩：![3.png](https://image.3001.net/images/20190222/1550840056_5c6ff0f83328a.png!small)我们可以看到这个数据包被发送到C＆C服务器（cu23880.tmweb.ru/landing.php）：![4.png](https://image.3001.net/images/20190222/1550840063_5c6ff0ff39567.png!small)
**内在** Golang编译的二进制文件通常比较大，所以样本采用UPX打包来压缩并不奇怪。
我们将其脱壳。就得到了简单的Go二进制文件。导出表显示了编译路径和一些其他有趣的函数：![5.png](https://image.3001.net/images/20190222/1550840071_5c6ff10790281.png!small)看看这些导出的数据，我们可以了解其内部使用的静态库。其中许多函数（与trampoline有关）可以在模块sqlite-3中找到：<
<https://github.com/mattn/go-sqlite3/blob/master/callback.go>>。函数crosscall2来自Go运行时，它与从C/C++应用程序调用Go相关(
<https://golang.org/src/cmd/cgo/out.go>)。

## 工具

为了分析，我使用了IDA Pro以及George
Zaytsev编写的脚本[IDAGolangHelper](a%20href=)。首先，Go可执行文件必须加载到IDA中。然后，我们可以从菜单（文件 ->脚本文件）运行脚本。然后，我们会看到以下菜单，可以访问特定功能：![6.png](https://image.3001.net/images/20190222/1550840081_5c6ff11125814.png!small)首先，我们需要确定Golang版本（该脚本提供了一些有用的启发式）。在这种情况下，它将是Go
1.2。然后，我们可以重命名函数并添加标准的Go类型。完成这些操作后，代码看起来更具可读性。下面，您可以看到使用脚本之前和之后的函数视图。之前（仅导出的函数被命名）：![7.png](https://image.3001.net/images/20190222/1550840087_5c6ff117c96d3.png!small)之后（大多数函数都自动解析并添加了它们的名称）：![8.png](https://image.3001.net/images/20190222/1550840095_5c6ff11f0861a.png!small)其中许多功能来自静态链接库。因此，我们需要主要关注注释为`main_*`\-特定于特定可执行文件的函数。![9.png](https://image.3001.net/images/20190222/1550840102_5c6ff1260bb36.png!small)

## 代码概述

在函数“main_init”中，我们可以看到将在应用程序中使用的模块：

![10.png](https://image.3001.net/images/20190222/1550840109_5c6ff12dcde4b.png!small)它与以下模块静态链接：

GRequests（<https://github.com/levigross/grequests>）

go-sqlite3（<https://github.com/mattn/go-sqlite3>）

尝试（<https://github.com/manucorporat/try>）分析此功能可以帮助我们预测功能;
即查看上面的库，我们可以看到它们将通过网络进行通信，读取SQLite3数据库并抛出异常。其他初始化器建议使用正则表达式，zip格式和读取环境变量。此函数还负责初始化和映射字符串。我们可以看到其中一些是第一个base64解码的：

![11.png](https://image.3001.net/images/20190222/1550840119_5c6ff137b1dc8.png!small)

在字符串初始化中，我们看到对加密货币钱包的引用。Ethereum：

![12.png](https://image.3001.net/images/20190222/1550840125_5c6ff13da893f.png!small)

Monero：

![13.png](https://image.3001.net/images/20190222/1550840131_5c6ff1437bdb2.png!small)

Golang二进制文件的主要功能是注释“main_main”。

![14.png](https://image.3001.net/images/20190222/1550840138_5c6ff14a93ce9.png!small)

在这里，我们可以看到应用程序正在创建一个新目录（使用函数os.Mkdir）。这是将要复制（找到的）文件的目录。之后，有几个Goroutine已经开始使用runtime.newproc。（Goroutines可以像线程一样使用，但它们的管理方式不同。更多细节可以在[here](a%20href=)找到）。
这些例程负责搜索文件。 同时，Sqlite模块用于解析数据库以窃取数据。之后，恶意软件将其全部压缩到一个包中，最后，压缩包被上传到C＆C。

![15.png](https://image.3001.net/images/20190222/1550840144_5c6ff15088938.png!small)

### 盗取了什么？

要查看攻击者究竟对哪些数据感兴趣，我们可以更详细地了解执行SQL查询的函数，并查看相关字符串。Golang中的字符串以连续形式存储在批量中：

![16.png](https://image.3001.net/images/20190222/1550840153_5c6ff15938268.png!small)

之后，根据需要检索来自此批量的单个块。因此，看看每个字符串被引用的代码中的哪个位置并不容易。下面是代码中打开“sqlite3”数据库的片段（检索长度为7的字符串）：

![17.png](https://image.3001.net/images/20190222/1550840162_5c6ff162cd09f.png!small)

另一个例子：通过给定的偏移量和长度，从完整的字符串块中检索此查询：

![18.png](https://image.3001.net/images/20190222/1550840168_5c6ff168a1129.png!small)

我们来看看这些查询试图获取的数据。获取调用引用的字符串，我们可以检索并列出所有字符串：

    
    
    select name_on_card, expiration_month, expiration_year, card_number_encrypted, billing_address_id FROM credit_cards
    select * FROM autofill_profiles
    select email FROM autofill_profile_emails
    select number FROM autofill_profile_phone
    select first_name, middle_name, last_name, full_name FROM autofill_profile_names
    

我们可以看到浏览器的cookie数据库被查询与在线交易相关的数据：信用卡号，到期日以及姓名和电子邮件地址等个人数据。所有搜索的文件的路径都存储为base64字符串。其中许多与加密货币钱包有关，但我们也可以找到对Telegram的引用。

    
    
    Software\\Classes\\tdesktop.tg\\shell\\open\\command
    \\AppData\\Local\\Yandex\\YandexBrowser\\User Data\\
    \\AppData\\Roaming\\Electrum\\wallets\\default_wallet
    \\AppData\\Local\\Torch\\User Data\\
    \\AppData\\Local\\Uran\\User Data\\
    \\AppData\\Roaming\\Opera Software\\
    \\AppData\\Local\\Comodo\\User Data\\
    \\AppData\\Local\\Chromium\\User Data\\
    \\AppData\\Local\\Chromodo\\User Data\\
    \\AppData\\Local\\Kometa\\User Data\\
    \\AppData\\Local\\K-Melon\\User Data\\
    \\AppData\\Local\\Orbitum\\User Data\\
    \\AppData\\Local\\Maxthon3\\User Data\\
    \\AppData\\Local\\Nichrome\\User Data\\
    \\AppData\\Local\\Vivaldi\\User Data\\
    \\AppData\\Roaming\\BBQCoin\\wallet.dat
    \\AppData\\Roaming\\Bitcoin\\wallet.dat
    \\AppData\\Roaming\\Ethereum\\keystore
    \\AppData\\Roaming\\Exodus\\seed.seco
    \\AppData\\Roaming\\Franko\\wallet.dat
    \\AppData\\Roaming\\IOCoin\\wallet.dat
    \\AppData\\Roaming\\Ixcoin\\wallet.dat
    \\AppData\\Roaming\\Mincoin\\wallet.dat
    \\AppData\\Roaming\\YACoin\\wallet.dat
    \\AppData\\Roaming\\Zcash\\wallet.dat
    \\AppData\\Roaming\\devcoin\\wallet.dat
    

## 总结

此恶意软件中使用的一些概念提醒我们，例如Evrial，PredatorTheThief和Vidar。它有类似的目标，并将被盗数据作为ZIP文件发送给C＆C。但是，没有证据证明这个窃取者的作者与这些案件有某种联系。当我们看一下这个恶意软件的实现和功能时，它相当简单。它的大尺寸来自许多静态编译的模块。可能这个恶意软件还处于开发的早期阶段
- 作者可能刚刚开始学习Go并正在进行实验。我们将密切关注其发展。

起初，分析Golang编译的应用程序可能会感到压倒性，因为它具有庞大的代码库和不熟悉的结构。但是在适当的工具的帮助下，安全研究人员可以轻松地在这个迷宫中导航，因为所有的功能都被贴上标签。由于Golang是一种相对较新的编程语言，我们可以预期分析它的工具会随着时间的推移而成熟。用恶意软件写出威胁发展的新兴趋势吗？这有点太早了。但我们知道，用新语言编写的恶意软件的意识对我们的freehuf的读者来说非常重要。

 ***参考来源：[malwarebytes](https://blog.malwarebytes.com/threat-analysis/2019/01/analyzing-new-stealer-written-golang/)，由周大涛编译，转载请注明来自FreeBuf.COM**

