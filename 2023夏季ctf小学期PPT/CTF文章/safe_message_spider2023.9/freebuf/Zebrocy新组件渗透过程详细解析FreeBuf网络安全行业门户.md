**在2018年8月，Sednit的运营者部署了两个新的Zebrocy组件，从那时起我们看到Zebrocy部署的增长，它的目标是中亚以及中欧和东欧国家，特别是这些国家的大使馆、外交部和外交官员。**

Sednit组织自2004年以来一直在运营，并且在过去几年中经常成为头条新闻：它被认为是主要的，高调的攻击背后的组织。例如，美国司法部为在2016年美国大选之前对民主党全国委员会（DNC）进行的黑客攻击而将该组织命名。该组织还被认为是全球电视网TV5Monde、世界反兴奋剂机构（WADA）电子邮件泄密以及许多其他攻击的背后组织。该组织在其武器库中拥有各种各样的的恶意软件，我们已在2016年的Sednit白皮书中记录了几个例子。

与此同时，ESET研究人员发布了一份关于[LoJax](https://www.welivesecurity.com/2018/09/27/lojax-first-uefi-rootkit-found-wild-courtesy-sednit-group/)的白皮书，用于入侵巴尔干半岛、中欧和东欧的组织的UEFI rootkit，我们认为是由Sednit开发的。

在2018年8月，Sednit的运营者部署了两个新的Zebrocy组件，从那时起我们看到了Zebrocy部署的增长。Zebrocy包含一套下载器，注入器和后门;
当下载器和注入器正在进行侦察时，后门会对目标进行持久化和间谍活动。这些新组件使用不寻常的与SMTP和POP3等邮件服务相关的协议来窃取信息。

这些新组件所针对的受害者与我们和卡巴斯基之前关于[Zebrocy](https://www.welivesecurity.com/2018/04/24/sednit-update-analysis-zebrocy/)的博客中提到的受害者类似。攻击的目标是中亚、中欧和东欧国家，特别是大使馆，外交部和外交官员。

## 全景图

![Afigure1-1024x895.jpg](https://image.3001.net/images/20181130/15435579371527.jpg!small)

两年来，Sednit组织主要使用网络钓鱼电子邮件作为Zebrocy感染媒介（案例1和案例2）。一旦目标被感染，他们就会使用不同的第一阶段下载器收集有关受害者的信息并判断受害者是否值得关注，经过几个小时或几天的延迟，他们会部署一个二级后门。

Zebrocy的经典“作案手段”是让受害者收到有附件的电子邮件。该附件包含两个文件，一个是良性文档，另一个是可执行文件。运营者试图通过“双扩展名”技巧把可执行文件命名为表面上是文档或图像的文件来欺骗受害者。

图1中案例3所示的新模式，使用了更为复杂的过程。下面我们将剖析这个过程。

Delphi注入器第一个二进制文件是Delphi注入器，这对Zebrocy来说很不寻常。大多数情况下，第一阶段安装在受害者系统上是一个下载器而不是注入器。

这个注入器包含了一些使逆向工程更加困难的技巧。在我们描述的样本中使用关键字“liver” 来标记关键元素的开始和结束，如下所示：

    
    
    $ yara -s tag_yara.yar  SCANPASS_QXWEGRFGCVT_323803488900X_jpeg.exe
    find_tag SCANPASS_QXWEGRFGCVT_323803488900X_jpeg.exe
    0x4c260:$tag: l\x00i\x00v\x00e\x00r\x00
    0x6f000:$tag: liver
    0x6f020:$tag: liver
    0x13ab0c:$tag: liver
    

上面的YARA规则寻找liver字符。第一个liver是在代码中使用的，它不分隔任何东西，而其他liver分隔密钥描述符、图片（下面的hexdump）和注入器中被加密的payload。

    
    
    $ hexdump -Cn 48 -s 0x6f000  SCANPASS_QXWEGRFGCVT_323803488900X_jpeg.exe
    0006f000  6c 69 76 65 72 4f 70 65  6e 41 69 72 33 39 30 34  |liverOpenAir3904|
    0006f010  35 5f 42 61 79 72 65 6e  5f 4d 75 6e 63 68 65 6e  |5_Bayren_Munchen|
    0006f020  6c 69 76 65 72 ff d8 ff  e0 00 10 4a 46 49 46 00  |liver……JFIF.|
    

从图片开始，如果C:\Users\public\Pictures\scanPassport.jpg文件不存在，则将其注入。有趣的是，注入的文件名SCANPASS_QXWEGRFGCVT_323803488900X_jpeg.exe也暗示了围绕旅行或护照信息的网络钓鱼方案。这可能表示运营者明确网络钓鱼邮件的目标。注入器打开图片：如果文件存在，它将停止执行;
否则，它会注入图片，打开它，并检索密钥描述符OpenAir39045_Bayren_Munchen。当文件格式有效时，图片不显示任何内容; 见图2。

![figure2-1024x788.jpg](https://image.3001.net/images/20181130/15435574597191.jpg!small)

密钥描述符的字符串包含Bayren_Munchen，这似乎可能是指德国足球队拜仁慕尼黑队。然而，真正起作用的不是密钥描述符的内容，而是它的长度，它的长度用于检索加密payload的XOR密钥。

要获取XOR密钥，注入器会查找最后一个liver关键字并增加密钥描述符的偏移量。XOR密钥的长度是27（0x1b）字节，与密钥描述符的长度相同。

使用XOR密钥和简单的XOR循环，注入器解密最后一个部分:加密的payload（从最后一个标记到文件的结束)。请请注意，payload的MZ头从关键字liver后开始，XOR密钥从通常为0x00序列PE头的某部分检索，一旦payload被解密它们就恢复，如图3所示。

![figure3-1024x144.jpg](https://image.3001.net/images/20181130/15435569325298.jpg!small)

以文件C:\Users\Public\Documents\
AcrobatReader.txt注入payload，并将文件移动到C:\Users\Public\Documents\AcrobatReader.exe。

也许这是为了避免终端保护系统触发删除.exe扩展名的二进制文件的警报。

运营者再次尝试在受害者查看目录时欺骗他们，在这种情况下，他们将看到如图4所示的文件：

![Payload.jpg](https://image.3001.net/images/20181130/1543559351526.jpg!small)

默认情况下，Windows会隐藏扩展名，入侵者可以利用此注入可执行文件到Documents目录中，使其看起来像PDF文件。

最后，注入器执行其新注入的payload，然后退出。

##MSIL邮件下载器前一个注入器的payload是一个UPX压缩的MSIL下载器。为了使过程更容易理解，下面介绍主要逻辑，接着是源代码，然后是控制流的概述。

Main方法调用Run来启动应用程序，然后创建Form1表单。

    
    
    {
        Application.EnableVisualStyles();
        Application.SetCompatibleTextRenderingDefault(false);
        Application.Run((Form) new Form1());
    }
    

Form1启动了很多变量，包括七个新的 Timer。

    
    
        this.start = new Timer(this.components);
        this.inf = new Timer(this.components);
        this.txt = new Timer(this.components);
        this.subject = new Timer(this.components);
        this.run = new Timer(this.components);
        this.load = new Timer(this.components);
        this.screen = new Timer(this.components);
    

Timer对象有三个重要字段：

> Enabled:表示计时器是否处于活动状态；
>
> Interval:事件之间的时间（以毫秒为单位）；
>
> Tick:当计时器间隔结束并启用计时器时执行的回调。

这些字段初始化为：

    
    
        this.start.Enabled = true;
        this.start.Interval = 120000;
        this.start.Tick += new EventHandler(this.start_Tick);
        this.inf.Interval = 10000;
        this.inf.Tick += new EventHandler(this.inf_Tick);
        this.txt.Interval = 120000;
        this.txt.Tick += new EventHandler(this.txt_Tick);
        this.subject.Interval = 120000;
        this.subject.Tick += new EventHandler(this.subject_Tick);
        this.run.Interval = 60000;
        this.run.Tick += new EventHandler(this.run_Tick);
        this.load.Interval = 120000;
        this.load.Tick += new EventHandler(this.load_Tick);
        this.screen.Interval = 8000;
        this.screen.Tick += new EventHandler(this.screen_Tick);
    

对于每个对象，它设置一个从8秒到2分钟的间隔。回调被添加到事件句柄。请注意，start是唯一一个将Enabled设置为true的地方，这意味着在2分钟（12000毫秒=
120秒）之后，事件句柄将调用start_Tick。

    
    
        private void start_Tick(object sender, EventArgs e)
        {
            try
            {
                this.start.Enabled = false;
                Lenor lenor = new Lenor();
                this.dir = !Directory.Exists(this.label15.Text.ToString()) ? this.label16.Text.ToString() + "\" : this.label15.Text.ToString() + "\";
                this.att = this.dir + "audev.txt";
                this._id = lenor.id(this.dir);
                this.inf.Enabled = true;
            }
    

此后，每个方法都具有相同的行为：在方法的开头将Enabled变量设置为false。该方法执行，然后将下一个对象的Enabled变量设置为true，这将激活下一个计时器。入侵者把Enabled变量作为一种状态机：如果函数调用失败，该机制就重复执行函数，直到他们成功调用。在两个函数的执行时间之间添加延迟可能是在尝试规避终端保护系统。

至此每种方法的结构都被定义了; 以下部分将重点介绍恶意软件的控制流程。

交换发生在不同的电子邮件收件箱之间，以下是不同步骤的概述。

![figure5-1024x929.jpg](https://image.3001.net/images/20181130/1543559389792.jpg!small)

恶意软件进行的早期检查之一是判断其执行期间用于注入所有文件的特定路径是否存在。如果可能，它使用C:\Users\Public
\Videos\，否则它将回退到C:\Documents and Settings\All
Users\Documents\作为其默认目录。请注意，后者路径适用于Windows XP，而前者适用于Vista及更高版本。

通过拼接C盘序列号和UserName 生成一个16字节的id，并存储在audev.txt文件中。

下载器收集以下信息：

> 应用程序的当前路径
>
> 操作系统版本
>
> 系统目录
>
> 用户域
>
> 机器名称
>
> 用户名
>
> 当前时区
>
> 当前的日期
>
> 逻辑驱动器列表和每个驱动器列表的信息（型号，序列号等）
>
> C:\Program Files\和C:\Program Files（x86）的目录列表
>
> 进程列表

所有这些信息都保存在C:\Users\Public\Videos\
si.ini文件中，并作为电子邮件的附件通过SMTPS默认端口465发出。电子邮件正文包含字符串SI（可能是代表系统信息），收件人是sym777.g@post.cz。所有电子邮件的主题设置为id。

运营者使用多个收件地址，并将相同的电子邮件发送给另外两个收件人，以防止主要收件人无法收邮件。发送电子邮件后，下载器将删除si.ini文件。

恶意软件第一次执行时会创建包含{System_Parametrs = 10}的文件:set.txt，并创建Windows注册表项：

![figure6-1024x259.jpg](https://image.3001.net/images/20181130/15435594366421.jpg!small)

受害者计算机的屏幕截图被命名为scx.bin，并作为电子邮件附件发送，电子邮件正文中是SC（可能是Screenshot缩写）。

发送后，恶意软件通过SSL的POP3（端口995）连接到kae.mezhnosh@post.cz邮箱，并查找主题对应于自己的id邮件。如果有这样的邮件并且正文不为空，则恶意软件用十六进制编码方式对其进行解码，然后将正文为okey的邮件发送到sym777.g@post.cz。之前找到的邮件内容将按以下方式进行处理和解析：

    
    
            string[] strArray = this._adr.Replace("B&", "").Replace("Db", "").Split('%');
            string str1 = strArray[0];
            string str2 = strArray[1];
    

获得两个字符串：第一个是密码，第二个是电子邮件地址的用户名。

这些新凭证用于连接新收集的特定收件箱，并在那里查找包含主题与恶意软件ID相匹配的邮件，以及在其文件名中包含字符串audev的附件。如果满足这两个条件，则恶意软件会保存附件并从服务器中删除该邮件。

所有日志消息都发送到sym777.g@post.cz，而通过POP3得到的消息是最近获得的凭据。

运营者的这些决策使得取证更加困难。首先，如果您的下载程序包含电子邮件，则无法连接到包含下一阶段的邮箱。

其次，如果你获得了电子邮件凭据，仍然无法获取下一个payload，因为它在检索后已被删除。

下载器成功将附件写入磁盘后，它会在正文中发送一封带有okey2的电子邮件，并发送一个内容包含090名为l.txt的附件。该附件被000覆写，同时恶意软件尝试获取另一条消息。再次，如果它有用，则发送正文为okey3和附件为l.txt的邮件。附件的内容是目录和文件名。恶意软件将audev文件移动到此文件路径。最后，恶意软件会发送一封电子邮件，其中包含正文okey4和附件l.txt。它启动可执行文件：audev.exe并检查进程列表以查看其中一个是否包含字符串audev。

    
    
        Process.Start(this.rn);
        foreach (Process process in Process.GetProcesses())
        {
            if (process.ProcessName.Contains("audev"))
        }
    

如果找到具有此类名称的进程，则会发送最后一封电子邮件，其中okey5作为正文消息，l.txt作为附件。最后，它删除l.txt和set.txt，删除它创建的Windows注册表项，然后退出。

Delphi邮件下载器这个下载器的主要作用是评估入侵系统的重要性，如果认为足够重要，则下载并执行Zebrocy的最后下载器。

二进制文件是用Delphi编写的，并用UPX打包。TForm1对象的完整定义可以在其资源部分中找到，并包含恶意软件使用的一些配置参数。以下部分重点介绍下载器的初始化，功能和网络协议。

###初始化最开始，它解密了一堆字符串，这些字符串是电子邮件地址和密码。运营者使用AES
ECB加密算法。每个字符串都是十六进制编码的，前四个字节是解密字符串的最终大小（解密后的字符串可能在末尾包含一些填充）。TForm1对象中有两个AES密钥;
第一个用于加密数据，第二个用于解密。

电子邮件和密码用于向恶意软件发送命令，并收集从受害者计算机收集的信息。通信协议是SMTP和POP3 -两者都使用SSL。恶意软件使用的两个OpenSSL动态链接库为（DLL）：libeay32.dll（98c348cab0f835d6cf17c3a31cd5811f86c0388b）和ssleay32.dll（6d981d71895581dfb103170486b8614f7f203bdc）。

![Open-SSL-1024x703.jpg](https://image.3001.net/images/20181130/15435594604375.jpg!small)

请注意，所有文件都放在恶意软件的工作目录C:\Users\Public\中。

恶意软件第一次执行期间使用众所周知的“登录脚本”技术
完成持久化。它创建一个脚本文件registration.bat并从TForm1对象写入几个字符串。最后的脚本是：

    
    
    reg add HKCU\Environment /v "UserInitMprLogonScript" /t REG_EXPAND_SZ /d "C:\Users\Public\Videos\audev.exe" /f
    del C:\Users\Public\Videos\registr.bat
    exit
    

最后，恶意软件创建了一个id，就像之前Zebrocy二进制文件中看到的一样。该Id由Windows API
GetUserNameW方法获得的UserName，和在其前面添加C盘序列号组成。

###功能虽然在上述执行过程中存在一些收集受害者的信息的判断条件和流程，但以下部分描述了不同的收集功能。扫描配置存储在TForm1对象中，分为七类，用于从受害者的计算机中收集信息。

从简单扫描开始，恶意软件收集的第一类信息是具有以下扩展名的文件：.docx，.xlsx，.pdf，.pptx，.rar，.zip，.jpg，.bmp，.tiff。对于磁盘上找到的每个文件，它将检索文件的完整路径和上次修改日期。这些信息使用前面提到的AES密钥加密并存储在文件0.txt中。另一个扫描针对扩展名.dat，.json，.db，与上述扫描类似，它会检索文件的完整路径和上次修改日期。然后密它们并存储在文件57.txt下。

列出正在运行的进程也是此恶意软件的功能之一，它将该信息存储在08.txt文件中，如下所示：

    
    
    ======Listing_of_processes=======
    [System Process]
    System
    smss.exe
    csrss.exe
    wininit.exe
    csrss.exe
    winlogon.exe
    services.exe
    lsass.exe
    […]
    

在i.txt文件中，恶意软件收集有关受害者计算机的一般信息以及有关恶意软件的一些信息，例如版本号和执行它的路径，如下所示：

    
    
    v7.00
    C:\Users\Public\Videos\audev.txt 
    ============================================
    Log_Drivers:
     C: fixed; size= 102297 Mb, free=83927 Mb S/N: [redacted]
     ==================================================
     OSV: Windows 7
    WinType: 32
    WinDir: C:\Windows
    Lang: English (United States)
    TZ: UTC1:0 Romance Standard Time
    HostN: [redacted]-PC
    User: [redacted]
    ===============S_LIST=====================
    C:\Program Files\Common Files
    C:\Program Files\desktop.ini
    C:\Program Files\DVD Maker
    C:\Program Files\Internet Explorer
    C:\Program Files\Microsoft.NET
    C:\Program Files\MSBuild
    C:\Program Files\Reference Assemblies
    C:\Program Files\Uninstall Information
    C:\Program Files\Windows Defender
    […]
    

该恶意软件能够屏幕截图，图片存储为2[YYYY-mm-dd HH-MM-SS]
-Image_001.jpg，并生成另一个文件2\sa.bin，其中保存所有截屏的路径列表。它的最后一个功能是网络枚举，结果输出到4.txt。

###网络协议Delphi
Mail下载器是Zebrocy工具集的新增功能，它提供了一种新的方法来从运营者那里获取数据和命令。渗透方式很简单但在网络上非常嘈杂，因为之前收集的所有加密文件都是通过SMTPS发送的，并且每个版本的文件都会发送三次。

寄件人 | 接受者  
---|---  
kevin30@ambcomission.com | rishit333@ambcomission.com  
salah444@ambcomission.com | rishit333@ambcomission.com  
karakos3232@seznam.cz | antony.miloshevich128@seznam.cz  
  
邮件的主题是受害者的id，文件作为附件发送，其中包含与文件内容对应的关键字。请注意，对于每个文件，都有一个加密版的发送文件。

文件 | 对应的加密文件 | 关键词  
---|---|---  
- | 0.txt | SCAN  
57.txt | 58.txt | ACC  
08.txt | 082.txt | PrL  
i.txt | i2.txt | SYS_INFO  
4.txt | 42.txt | GET_NETWORK  
  
屏幕截图以及与上述两个扫描匹配的文件也会发送，使用有不同的关键词。

内容 | 关键词  
---|---  
screenshots | SC  
.docx, .xlsx, .pdf, .pptx, .rar, .zip, .jpg, .bmp, .tiff | FILEs  
.dat, .json, .db | D_ACC  
  
![figure8-1024x647.jpg](https://image.3001.net/images/20181130/15435594818979.jpg!small)

虽然渗透使用SMTP，但二进制文件通过POP3
连接到电子邮件地址tomasso25@ambcomission.com并解析电子邮件。电子邮件的正文包含不同的关键字，这些关键字被恶意软件解释为命令。

关键词 | 目的 | 日志  
---|---|---  
Co55 | copy file | is_cp  
cd25 | create directory | isc  
dele6 | delete directory | isd  
dele5 | delete file | isd  
autodel | delete itself |  
net40 | enumerating network resources |  
Start23 | execute | isr  
edit34 | execute and delete |  
Mo00 | move file | is_m  
prlist | process listing |  
pKL90 | register | isreg  
ldfile | scan |  
scan | scan | -  
  
一旦执行，调试日志和命令的执行结果（如果有的话）将被发送回运营者。例如，对于扫描命令，运营者接收包含与扫描扩展名匹配的文件列表以及每个匹配文件的文件。

虽然这个下载器具有一些后门功能，但它删除了已经与该组相关联的Delphi下载器，这在我们之前的Zebrocy[文章](https://www.welivesecurity.com/2018/04/24/sednit-update-analysis-zebrocy/)中已进行了描述。

总结在过去，我们发现了Zebrocy与其他传统Sednit恶意软件之间的重叠。我们抓住Zebrocy放弃了Sednit旗舰后门XAgent。因此，我们很自信地将Zebrocy归于Sednit组织。

但是，对这些二进制文件的分析显示了一些语言级别的错误以及在工具集开发中出现的不同成熟度的开发决策。两个下载程序都使用邮件协议来窃取信息并共享通用机制来收集相同的信息。两者在网络和系统上都非常“嘈杂”，因为它们会创建大量文件并通过网络发送大量文件。在分析Delphi邮件下载器时，一些功能似乎已经消失，但有些字符串仍然保留在二进制文件。因此，虽然这个工具集由Sednit集团运营，但与开发传统的Sednit组件相比，我们非常有信心认为它是由另一个经验不足的团队开发的。

Zebrocy是Sednit工具集的新增组件，最近的事件可能解释了Zebrocy被越来越多的使用，而不是Sednit之前的恶意软件。

Indicators of Compromise (IoCs)| 文件名| SHA-1 | ESET 检测 || ------ | ------ |
------
    
    
    ||SCANPASS_QXWEGRFGCVT_323803488900X_jpeg.exe|7768fd2812ceff05db8f969a7bed1de5615bfc5a|Win32/Sednit.ORQ||C:\Users\public\Pictures\scanPassport.jpg|da70c54a8b9fd236793bb2ab3f8a50e6cd37e2df|-||C:\Users\Public\Documents\AcrobatReader.{exe,txt}|a225d457c3396e647ffc710cd1edd4c74dc57152|MSIL/Sednit.D||C:\Users\Public\Videos\audev.txt|a659a765536d2099ecbde988d6763028ff92752e|Win32/Sednit.CH||%TMP%\Indy0037C632.tmp    |20954fe36388ae8b1174424c8e4996ea2689f747| Win32/TrojanDownloader.Sednit.CMR||%TMP%\Indy01863A21.tmp| e0d8829d2e76e9bb02e3b375981181ae02462c43| Win32/TrojanDownloader.Sednit.CMQ|

## 邮件列表

邮件  
---  
carl.dolzhek17@post.cz  
shinina.lezh@post.cz  
P0tr4h4s7a@post.cz  
carl.dolzhek17@post.cz  
sym777.g@post.cz  
kae.mezhnosh@post.cz  
tomasso25@ambcomission.com  
kevin30@ambcomission.com  
salah444@ambcomission.com  
karakos3232@seznam.cz  
rishit333@ambcomission.com  
antony.miloshevich128@seznam.cz  
  
***参考来源：[welivesecurity](https://www.welivesecurity.com/2018/11/20/sednit-whats-going-zebrocy/)，本文作者fengbin8606，转载请注明来自FreeBuf.COM**

