**本文将向各位读者展示如何开发杀毒软件。**

在很多人思维中，特别是IT从业者、程序员看来，杀毒软件及其开发技术历来是一个颇为神秘不可及的领域。在市面上和网络中的各种文章、书集中，也鲜有涉及此方面的开发资料。正因如此，使的杀毒软件业成了一个稀缺、高门槛的行业，相关技术也似乎是高度机密的资料、只掌握在极少数人手中。

本文将从杀毒软件开发方案、功能结构设计、界面设置、代码编写、实际应用等各方面，逐步展示如何开发一款具功能完善的大众化杀毒软件。以此揭密杀毒软件开发各方面技术，引领对此领域有兴趣或有志于此行的读者朋友们入门杀毒软件开发！

##  **一、关于杀毒软件，你需要知道的**

###  **1、** **杀毒软件的重要性**

电脑的使用已普及到社会生活的方方面面，无论是工作、娱乐、学习、购物等等都会接触到电脑。使用电脑实际上是使用电脑中的各种软件。

什么软件重要呢？对于不同的人、不同的目标，答案也不尽相同，但是无论做什么，安全自然是不容忽视的：网上购物需要确保交易安全、资金安全；聊天娱乐需要保护隐私；工作学习需要防止资料、机密泄漏，即便没有这些诸多考虑只是随意上网也要需要一个安全稳定的操作系统环境，这一切需要被人们担心、防范的又是什么呢？是木马、病毒、恶意软件。而杀毒软件正是用来对付这些威胁、保护电脑正常使用的必不可少的软件。

###  2、 **了解杀毒软件开发的重要性**

对于大多数普通的电脑使用者来说并不重要。

绝大多数的电脑使用者并不需要学会开发杀毒软件，也不需要懂杀毒原理，会用就足够了。但对于某些人也许很重要，有的需要了解、有的需要熟悉，甚至有的需要掌握。

电脑行业相关从业者，譬如网管、空间服务商、系统管理员或其它从事系统安全维护人员等，有必要多了解杀毒软件相关知识，熟愁杀毒软件功能重点，以及防杀毒原理，以便在进行选用杀毒软件或部署防杀毒安全方案等操作时有更多好的选择。

因为杀毒软件的重要性所至，绝大多数的电脑都会安装杀毒软件，因此杀毒软件的目标用户群非常之大、市场非常广阔。也就意味着从业者的前景较为光明。有条件以此方向进行创业是个不错的选择，当然并不是指跟国内外几大杀毒巨头抗衡，现存的一些小众反病毒安全产品也有不错的生存空间。

在安全公司或开展安全相关技术项目的公司供职者，如果自己掌握着此方面技术，想必在工作中更会如鱼得水。

最后，从兴趣或是研究、学习角度讲，如果以广义的技术含量而论，杀毒技术无疑居于金字塔的顶端，是一个门槛级高的领域，掌握了其技术，就等于掌握一门稀缺的技艺，何乐而不为呢？

###  3、 **杀毒软件技术难吗？**

不难。

杀毒软件开发技术之所以在人们眼中高深莫测，是因为通常无法窥得其门禁所至。就好像要做一件从未做过的不一般事情一样，会觉的无从下手。

造成这种境况的原因源自相关资料的匮乏，就像在武侠小说中，常会有某门派高等功夫很厉害，却传男不传女、传内不传外，更没有印刷量为5000册的秘籍。结果造成江湖人士们天天听说，却见不得、习不到。感觉就是很好很强大，自己学不会。

杀毒软件开发技术便像是如此，掌握在全地球为数不多的几家或几十家企业手中，用户能听到的往往是某某杀毒引擎、启发式技术甲、主动式技术乙、八重防御系统、九层监测技术等等这些貌似很厉害的字眼，用户无法判断其倒底有多么强大，只能中这些晦涩神奇的词句中下意识的自我判断，书店中各种类的也更加使人们觉的杀毒是一个神密不可及的领域。

而事实上，杀毒技术真的有那么难吗？

不可否认，任何领域的任何事情做到极致都是很难的，杀毒技术确实有很难的部分，但如果想入门、想掌握，并不会是想像中的那么困难。很多内容其实是已知的，但只是之前没有把它跟杀毒开发联想起来，只是以前没有想到杀毒软件是用如此的方法开发的，只是以前不知道如此技术有如此用法。

相信很多人读完本文后会有这样的感觉：原来如此，不难，我也可以掌握的。

##  **二、功能设计**

进行杀毒软件开发之前，首先需要明确功能。

杀毒软件需要具备的基本功能分为：杀毒、防毒、升级、自我保护、设置以及其它辅助功能。

###  **1、杀毒**

查毒杀毒，是杀毒软件的基本功能。

在实际的软件应用中，用户通常有不同的操作需求，比如有要要对内存和敏感系统区域进行快速扫描、有时需要进行全硬盘扫描、有时临时使用U盘，插入U盘后，需要对U盘进行单独扫描。

为了满足这些需求，通常在杀毒软件中提供三种扫描方式：快速扫描、全盘扫描、自定义扫描，也就是经典的三按钮式杀毒功能。国内外很多杀毒软件都采用了这种方式，并不是跟风，而是这样的设计确实实用、确实能满足用户的需求。

既然进行病毒扫描，理所当然可能会扫描到病毒。在扫描到病毒后，需要提供给用户相应的操作措施，如清除、自动清除、忽略、隔离。

###  **2、防毒**

在一定意义上而言，防毒功能的重要性甚至大于杀毒功能。如果用户有忧患意识，在安装系统后及时安装好杀毒软件，做好病毒防护工作，时刻阻止病毒侵入系统，远比中毒后再杀毒效果要好的多，亡羊补牢在电脑使用过程中是常常会晚的。因此，防毒功能是杀毒软件另一个非常重要且不可缺的部分。

在这里要对云安全进行一些简单的介绍，因为本文中对杀毒软件的设计中，将要在防毒功能中引入云安全概念，这是一个与常见的主流杀毒软件不同的防毒理念。

云安全，曾是个新兴的技术，高度依赖互联网、依赖带宽、依赖用户量，是互联网高度发展衍生出的一种技术。在杀毒软件领域中，具有极高的实用性。目前主要的杀毒软件中，大都有云安全应用的身影，甚至有完全的云查杀软件。使用云技术，利用云病毒库进行病毒的检测和查杀。

但本人认为，云安全技术在这一领域更适用来做防护，而不适用做杀毒。原因在于：云查杀，是在建立云服务器的基础上，将病毒库特征码置于服务器数据库中。用户在本地进行扫描时获取到本地文件特征码，然后需要连接到服务器，进行特征码匹配验证，以确定被扫描的文件否是病毒。网络验证，不管当前的网速达到了多快，但其速度是永远无法与本地相比的，进行文件扫描查杀，用户需要速度，而此举降低了扫描速度。况且，存储于服务器中的病毒库，是完全可以可以以升级病毒库的方式下载到客户机器中，进行高速扫描，这是传统杀毒软件惯用的方式，没有必要，也没有理由非存放在服务器。再则，云的思想，原本是将工作量分散到大量的互联网终端执行，而现行的这种云查杀，反而是将大量的客户端工作量集中到服务器执行，根本有驳云的思路。因此，云查杀不是一种优势的做法。

而如果将它应用到防护方面，在大数量用户的基础上，可以做到自动、快速的病毒特征码提取，将大量互联网客户端的数据上交到服务器，并且可以将特征码即时放置在云服务器病毒库，在有用户查询时，又能做到即时的反馈，直接提高了对新出病毒的反映速度。而这种防护式的云检测，对速度要求远低于云查杀的强度。

介于以上原因，本文中设计的杀毒软件，将使用此种云安全防护技术。

###  **3、** **升级**

杀毒软件，需要带有病毒库，病毒库是病毒特征码的**，杀毒软件性能的强弱在很大程度上依赖于病毒库。病毒库是很庞大的，通常有几十MB，甚至上百MB，因为它要存放几十万上百万的病毒特征码。最新最全的病毒库放置在网络中的服务器端，为了实时的将病毒库更新到客户机器，便需要用到下载升级功能。这是杀毒软件的辅助的功能，却也是必不可少的。

另一方面，升级功能也用于更新杀毒软件的功能模块，以方便户在不必重新下载安装软件即可使用到最新最稳定的功能。

###  **4、** **自我保护**

杀毒软件需要一定的自我保护能力甚至是绝对的自我保护能力，以防止被病毒或其它恶意软件强行将自身进程结束，换句话说，即是要防止没杀掉病毒反被病毒杀掉。

很多病毒木马为了提高生存率，会与杀毒软件对抗，反杀杀毒软件。比如某些病毒木马在运行时，会检测系统中是否已经安装了杀毒软件，如果检测到，会想尽办法终止杀毒软件，以方便进一步入侵系统。此时，杀毒软件必须有足够的能力自保，以确认能够击败病毒。

当然，杀毒软件的主要功能是保护系统的正常运行，而不是与病毒木马进行技术对抗，在使用自我保护功能时，需多方面考虑，即不过份影响系统性能和稳定性又能确保系统安全为最佳。

###  **5、** **黑白名单**

黑白名单是一个简化的特征码库，辅助病毒库工作。

有了病毒库，为什么还要使用黑白名单？

病毒库中存放的是病毒木马的特征码，有某些情况下，除了病毒木马还有一些边缘软件，不属于病毒木马范畴，不会对系统造成危害，但它会对系统产生一些不好的影响，比如某些P2P在线影音软件的后台程序，会将机器做为一台种子机器，不停的上传下载电影，占用大量宝贵的带宽和流量、比如某些聊天软件登录时弹出的广告等等。这些软件是正常电脑使用不需要的，但它却是某些正常软件附加软件，出于多种原因的考虑，不能将其列入到病毒库，那么只能使用黑名单功能阻止其运行。

甚至是系统中存在的某些正常软件，因为一些个人原因想阻止它的启动，等等这些都可以使用黑名单功能。

至于白名单，与此恰恰相反。比如一些调试工具，往往被归为恶意工具的一种而被列入病毒库，如果出于工作或其它需要需要使用这些工具，则需要使用白名单功能使期能够运行而不被杀毒软件阻止。

归结起来，黑白名单的存在，是为了扩充病毒库的使用范围，和减少杀毒软件的误报率。

###  **6、** **设置**

杀毒软件需要提供合理自由的设置选项，对软件功能进行配置，以符合用户的使用习惯。

比如是否使用右键菜单。文件及文件夹的右键菜单可以使扫描病毒等工具简单化，但有的用户却不喜欢在右键菜单中增加过多的内容而宁可使用自定义扫描。

比如是否要让软件在系统启动后自动运行、是否开启自动保护、是否启用云安全等等。

细节决定成败，用户使用软件的舒适度，决定着用户对软件的忠诚度。

###  **7、界面**

除了功能性方面，软件界面也是不可忽视的一部分，对用户而言，基本功能相近的情况下，选择一款软件时，往往会根据对软件界面的第一感觉进行选择。

界面不单单是美工、设计的事，在编程中巧妙的利用技巧对界面进行美化、优化也会起到非常好的效果。比如可以做换肤、动态按钮、显示特效等等。

###  **8、** **其它**

除上面介绍到的具体功能外，软件中还需要对版本号、病毒库日期等用户较为关心的相关信息在界面中合理的位置进行显示。在以上的设计理念中，多次提到了对用户的感受，之所以要多次提及，是因为不管设计任何软件，都是以用户使用、为用户解决问题为目的，设计杀毒软件当然也不例外，一方面设计功能，一方面也要考虑用户体验。

以上，对于功能的设计已经写完了，到此也许有疑惑：杀毒引擎呢？主动防御呢？为什么都没有说到。

诚然，在各种杀毒软件的推广宣传词中，常会到见各自引擎的名称，甚至是双引擎、四引擎，好似引擎越多功能越强大，当然在大多数用户认知当中也确实会是这样。那么杀毒引擎倒底是什么呢？它是检测和查杀病毒的方式，比如在扫描一个文件时，首先获取它的特征码，然后与病毒库中的病毒特征码进行比对，如果确认是病毒，对它进行查杀，如果是感染型病毒，需要对文件重写，还原文件入口点，等等这一系列操作组合整合起来就是杀毒软件的引擎。对源程序而言它就是一部分代码。同理，主动防御也只是防毒功能而已。

是否有这种一种感觉：宣传中那样神秘莫测的杀毒引擎原来不过如此。

##  **三、** **功能实现**

在上面的部分中，对软件的功能进行了初步设定，接下来将要以编程的思路，将这些功能进行梳理、整合，确定模块化的编程实现方案，并编码实现。

###  **1、杀毒实现方案及编码实现**

如上文所讲，本软件中将杀毒分为三种模式：快速扫描、全盘扫描、自定义扫描。

这三种扫描方式，展现在用户面前时是3种不同的操作，而在程序中的编码是非常相近的，不同在于扫描的目标文件对像不同。

> 快速扫描对加载在内存中的文件进行扫描；
>
> 全盘扫描对整个硬盘中的文件扫描；
>
> 自定义扫描对选中的目标文件进行扫描。

如下图所示：

![](https://image.3001.net/images/20191114/1573714051_5dccf883dcb34.png!small)

在此，以快速扫描为例，进行编码说明 。

快速扫描要扫描内存中的文件，如何确定哪些文件在内存中被使用呢？这里我们通过遍历系统活动进程及进程模块文件的方式来实现。

编码如下：

    
    
    Dim lProcess As Long
    
        lProcess = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    
        Dim uProcess As PROCESSENTRY32
    
        uProcess.dwSize = Len(uProcess)
    
        If Process32First(lProcess, uProcess) Then
    
        Dim lModule As Long
    
        lModule=CreateToolhelp32Snapshot(TH32CS_SNAPMODULE, uProcess.th32ProcessID)      
    
        Dim ModEntry As MODULEENTRY32
    
        ModEntry.dwSize = LenB(ModEntry)
    
        ModEntry.szExePath = ""
    
        If Module32First(lModule, ModEntry) Then
    
        Dim sFile As String
    
        sFile = TrimNull(ModEntry.szExePath)
    
        Dim sScanResult As String
    
        sScanResult = ScanFile(sFile)
    
        Loop While Module32Next(lModule, ModEntry)
    
        CloseHandle lModule
    
        Loop While Process32Next(lProcess, uProcess)
    
        CloseHandle lProcess

以上是遍历系统进程及相关模块的代码，也就是检测系统内存中加载着哪些文件。其中，使用APi函数CreateToolhelp32Snapshot获取系统进程快照，然后使用Process32First和Process32Next函数获取进程列表，使用Module32First和Module32Next获取进程调用的各文件。

这里没有读取配置文件区分是否扫描执行文件或是全部文件。此功能半放在后面部分单独讲述。

上面的代码中sFile变量中存放的是加载在内存中的各文件完整路径，获取到文件路径后，使用ScanFile函数对文件进行扫描，ScanFile函数是实现文件病毒扫描的功能。编码如下：

    
    
    Public Function **ScanFile** (sFile As String) As String
    
        ScanFile = ""
    
        Dim lFileHwnd As Long
    
        lFileHwnd = **CreateFile** (sFile, ByVal &H80000000, 0, ByVal 0&, 3, 0, ByVal 0)
    
        Dim bBuffer(12) As Byte
    
        Dim lBytesRead As Long
    
        Dim uDosHeader As IMAGE_DOS_HEADER  
    
        **ReadFile** lFileHwnd, uDosHeader, ByVal Len(uDosHeader), lBytesRead, ByVal 0&
    
        **CopyMemory** bBuffer(0), uDosHeader.Magic, 2

检查PE文件标志

    
    
    If (Chr(bBuffer(0)) & Chr(bBuffer(1)) = "MZ") Then

设置偏移量，指向PE头结构

****

    
    
    **SetFilePointer** lFileHwnd, uDosHeader.lfanew, 0, 0
    
        **ReadFile** lFileHwnd, bBuffer(0), 4, lBytesRead, ByVal 0&

再次检查是否是PE文件

    
    
    If (Chr(bBuffer(0)) = "P") And (Chr(bBuffer(1)) = "E") And (bBuffer(2) = 0) And (bBuffer(3) = 0) Then

以进一步调用下级函数扫描文件是否是病毒,如果是病毒则返回病毒名，否则返回空值

    
    
    Dim sScanSectionResult As String
    
        sScanSectionResult = **ScanSections** (lFileHwnd)

如果返回不为空，表示检测到是病毒，则关闭文件，返回

    
    
    If sScanSectionResult <> "" Then
    
        ScanFile = sScanSectionResult
    
        **CloseHandle** lFileHwnd
    
        Exit Function
    
        End If
    
        End If
    
        End If
    
        CloseHandle lFileHwnd
    
        End Function

上面已对部分关键代码做了注释，这里再对代码功能做具体介绍。此函数中，sFile是传入的待扫描文件名，先使用CreateFile函数打开文件，然后检测两处文件标识对文件类型进行检测，确定是PE文件(也就是可执行文件）后，再调用下级函数对文件进行扫描，因为病毒木马都是可执行文件，而不可能是文本文件，所以只有扫描可执行文件才有意义。

也许有人注意到，到之前介绍扫描方式时，方案中设计了两种扫描方式，一种为扫描可执行文件，一种为扫描所有文件，那这里为何又要对文件格式进行判断只扫描可执行文件呢？这是因为：在windows系统中，文件的后缀名是可以自由更改的，前面所提到的是从表面上根据后缀名进行分类，这种分类较为直观，但不够严谨，这里再次进行判断是为了弥补根据后缀名判断的不足。

这部分代码中，要扫描PE文件，涉及了PE文件结构的知识，那就么需要对PE文件结构有一定的了解。

PE文件是Windows系统上的可执行文件，全称是Portable
Execute，即：可移植的执行体。常见的EXE、DLL、OCX、SYS、COM都是PE文件。PE文件较为复杂，但在此只需了解部分相关知识，没有必要详尽说明，我们在程序中需用到的知识点是：判断一个文件是否是PE文件、获取PE文件的节内容，如大小、哈希值。

首先来看一下PE文件结构简图：

![](https://image.3001.net/images/20191114/1573714511_5dccfa4f91da4.png!small)

要操作PE文件，就要在程序中定义与之相同的文件格式，首先在程序中需要定义的是DOS头，需如下编码：

    
    
    Private Type IMAGE_DOS_HEADER
    
        Magic As Integer
    
        cblp As Integer
    
        cp As Integer
    
        crlc As Integer
    
        cparhdr As Integer
    
        minalloc As Integer
    
        maxalloc As Integer
    
        ss As Integer
    
        sp As Integer
    
        csum As Integer
    
        ip As Integer
    
        cs As Integer
    
        lfarlc As Integer
    
        ovno As Integer
    
        res(3) As Integer
    
        oemid As Integer
    
        oeminfo As Integer
    
        res2(9) As Integer
    
        **lfanew** As Long
    
        End Type

DOS头中除了最后的lfanew和e_magic，其它内容对我们都不重要。这个部分，我们关心的仅为lfanew,该值指向了PE头结构在文件中的偏移。如我们的这个文件该值为0x40,那么0x40开始就是PE头的开始,标志为"PE"两个字符。判断文件是否是PE文件，就是依靠这个。

PE结构第二部分：文件头:

    
    
    Private Type IMAGE_FILE_HEADER
    
        Machine As Integer
    
        NumberOfSections As Integer
    
        TimeDateStamp As Long
    
        PointerToSymbolTable As Long
    
        NumberOfSymbols As Long
    
        SizeOfOtionalHeader As Integer
    
        Characteristics As Integer
    
        End Type

这部分没有实际操作意义，但要定义到PE的相应位置，它在程序中编码时必须存在。

PE结构第三部分：可选文件头：

    
    
    Private Type IMAGE_DATA_DIRECTORY
    
        DataRVA As Long
    
        DataSize As Long
    
        End Type

RVA表示指向的地址是虚拟地址,就是程序加载后该地址在内存中相对于ImageBase的偏移,带Virtual的地址是这样。在文件中的偏移为：Addr -对应Section的VirtualAddress + 对应Section的文件内起始偏移。

PE结构第四部分:节头：

    
    
    Private Type IMAGE_SECTION_HEADER
    
        SectionName(7) As Byte
    
        VirtualSize As Long
    
        VirtualAddress As Long
    
        SizeOfRawData As Long
    
        PointerToRawData As Long
    
        PointerToRelocations As Long
    
        PLineNums As Long
    
        RelocCount As Integer
    
        LineCount As Integer
    
        Characteristics As Long
    
        End Type

SectionName中存储的是节的名称，比如.Text、.Res，占8个字节。VirtualAddress是节的RVA，即虚拟地址。SizeOfRawData是节的大小，PointerToRawData是节的文件偏移量。这几个变量很重要，我们要依靠它们来获节的内容，进而取得特征码。

这里提到了特征码，在接下来进一步扫描文件时，我们使用特征码匹配技术对文件进行检测，判断是否是病毒木马。为了便于理解之后的代码，我们先对本文中设计的杀毒软件的特征码、病毒库规范进行一些讲解。

 **病毒库简介**

>
> 病毒库是杀毒软件很重要的组成部分，影响杀毒软件的查杀、防护性能，病毒库由病毒特征码组成，是特征码的**。病毒库可以是一个单独的文件，也可是由多个文件组成。

**特征码**

> 病毒特征码是一组字符串，由特定的规则组成，用于标识某一病毒文件的特征。通过一定规则的特征码匹配校验，可以确定某文件是否是病毒。
>
> 特征码定义方式很有多种，比如根据文件特定位置的字节信息、根据PE文件格式使用的API组合、根据文件节信息等，甚至于文件的MD5码也属于文件独有的特征码。
>
> 在本文中将使用“PE文件节大小”+“对应节的Hash值”做为特征码。

**如何定义病毒名称**

在国际上，有一套病毒名称定义标准。对某病毒根据不同的性偏向冠以不同的前缀加以详细区分。比如这些种类有：Virus（病毒）、Trojan（木马） **、**
Worm（蠕虫）、AdWare（广告）、HackTool（黑客工具）、Exploit（溢出程序）、W32（Win32恶意文件）等。

比如我们获取到一个以远程控制为主要功能的病毒，我会可能会将它命名为:Trojan.a.b。

**病毒库设计**

有了特征码、病毒名称，将大量的特征码和病毒名称依照一定的规则存储在一起，即形成了病毒库。

在本杀毒软件设计中，为了起到保密作用，防止特征码被他人非法使用，将前文的特征码字符串进行加密，加密后存储在本地病毒库中。

例如：某文件Test.exe中，.Text节的大小为1024，节内容的Hash值为1234567890abcdef，则其特征码为：“1024:1234567890abcdef”，再将此特征码字符串加密，得到加密的特征码：abcdef1234567890，再附加上病毒名称，就得到了最终特征码组合：abcdef1234567890Trojan.a.b，这时便可以进行存储了。

**优化病毒库**

实现了特征码的存储，这还不够。还要考虑它的使用性能，如果特征码数据量达到一定级别，比如100万。那么逐一加载和匹配校验耗时就成了制约杀毒软件性能的一个瓶颈。诚然，数据量越大加载和匹配校验需要的时间就越长，这是一个根本的事实。但我们要尽可能的优化，加快这一过程。

**病毒库加载速度优化**

加载速度的优化，我们采用这种的方案来实现：给每个组合过的特征码字符串增加足够的长度，使所有字符串长度统一。

比如：

特征码1：“abcdef1234567890Trojan.a.b”

特征码2：“abcdef1234567890Virus.a.b”

为了让这两个特征码长度一至，我们给它的末尾增加空格，使其成为：

特征码1：“abcdef1234567890Trojan.a.b ”

特征码1：“abcdef1234567890Virus.a.b ”

然后，在加载时，不对每条数据进行逐一读取，而是一次性将整个病毒库文件读入内存，这个操作在速度上会比逐一读取特征码快很多。

因为每个特征码的长度是统一的，我们就能以固定长度分隔特征码，分隔后也就把整块的内存数据赋值给了程序中代表特征码的字符串数组。

**特征码匹配检测速度优化**

如果有100万条数据，每扫描一个文件时，都对这100万条数据进行一次匹配，显然是会非常耗时的。因此，特征码匹配检测速度优化是非常有必要。我们采用如下的办法：

在加密初始特定码时，使用Md5加密方法，不管加密前的特征码是哪种形式，加密后，将都是一个32位固定长度的字符串，且首字母将会是16个字符：0123456789abcdef中的任意一个。那么我们有机会将原有扫描匹配速度提高16倍。

把特征码按字母的不同，分别存储在16个不同的文件中。软件加载时同样按首字母的不同赋值给16个不同的特征码字符串数组。

接下来，在进行文件扫描时，为了能进行匹配，我们也必须把被扫描的文件特征码转化为与病毒库中存储的数据相符的格式。转化之后进行匹配校验之前，先取特征码首字符进行比较。

比如：

如果被扫描文件的特征码首字符是“a”,在程序中，只在“a”打头的特征码字符串数组中进行匹配，其它15种情况完全忽略，这样就极大的提高了扫描速度。

定义了16个病毒库文件，我们还是假设数据量为100万条，那么每个病毒库文件的体积都是较大的，可能有数MB大小。这对病毒库升级带来了一定的影响：下载的文件太大，每天可能需要下载数十MB的病毒库。对于病毒库服务器和用户来讲，都是一个不小的负担。为了解决这个问题，我们在16个病毒库文件之外，再增加一个X文件，它里面存储近期升级的少量的特征码。日常病毒库升级时，新的特征码都放置在其中。当积累到一数量时，再将特征码归类置入相应的文件，进行全面升级。

到此，我们了解了病毒库以及内部特征码的存储方式。但在进行特征码检测前，还有一项工程必须进行：特征码的加载。

**特征码** **加载**

假设我们已经建产了病毒库文件，文件共17个，文件名分别为：0.sig、1.sig、2.sig、3.sig、4.sig、5.sig、6.sig、7.sig、8.sig、9.sig、a.sig、b.sig、c.sig、d.sig、e.sig、f.sig、g.sig。

文件后缀名sig，含意为signature，即特征码的意思。

文件内容格式为：

“072B68E60B25FED5336235962D9C86E0Virus.OnlineGame-1376 ”

“0F5473AA8A8402561**0F050A784F47EVirus.Spy-62220”

“0DC38A0DA3B57DBE5E14512DE7A67C72Virus.Spy-62252”

特征码每个占一行，以回车换车结束。特征码在病毒库文件中不使用双引号“”。

程序中，读取之前，首先要定义一个自定义格式。用于存储单个特征码信息:

    
    
    Private Type Signature
    
        sHash As String * 32
    
        sName As String * 32
    
        sVbCrlf As String * 2
    
        End Type

sHash是文件特征码，占32个字节；sName是病毒名称，占32个字节；sVbCrlf是回车换行的意思，占两个字节。

然后定义一组公共变量数组，用于存储所有病毒库特征码：

    
    
    Public uSignature0() As Signature
    
        Public uSignature1() As Signature
    
        Public uSignature9() As Signature

中间省略

    
    
    Public uSignatureA() As Signature
    
        Public uSignatureF() As Signature
    
        Public uSignatureG() As Signature

这些变量存放在模块中，用Public标识，使它们可以在工程中的所有窗体和模块中被访问到，以方便在其它函数中调用进行特征码匹配校验。

然后编程读取病毒库，将特征码内容填充进这些数组中。

    
    
    Dim sSignatureFile As String
    
        Dim lFile As Long
    
        Dim lFileLen As Long

加载0~9.sig病毒库文件：

    
    
    Dim i As Long
    
        For i = 0 To 9
    
        sSignatureFile = sAppPath & i & ".sig"     

从病毒库文件加载特征码：

    
    
    Select Case i
    
        Case "0"
    
        lFile = FreeFile
    
        **Open** sSignatureFile For Binary As #lFile
    
        lFileLen = **LOF** (lFile)

重新定义特征码数组大小，这里数字66的含意是：
前面定义的特征码自定义格式中，sHash和sName各占32字节，sVbCrlf占2字节，即一个自定义特征码占66字节，因此，使用文件大小除以66，得到的是该病毒库文件中特征码的数量。

    
    
    ReDim uSignature0(1 To lFileLen / 66) As Signature

使用get方法获取文件内容，获取后uSignature0数组保已经得到了所有以字符0开头的病毒特征码，使用uSignature0(?)即可访问到具体的数据。

****

    
    
    **Get** lFile, , uSignature0
    
        **Close** lFile

接下来使用与上面类似的方法加载A~F.sig病毒库文件，数字65~70使用Chr()函数转化后可以得到字母A~F。

    
    
    Dim j As Long
    
        For j = 65 To 70
    
        sSignatureFile = sAppPath & Chr(j) & ".sig"
    
        Select Case **UCase** (Chr(j))
    
        Case "A"
    
        lFile = FreeFile
    
        **Open** sSignatureFile For Binary As #lFile
    
        lFileLen = **LOF** (lFile)
    
        If lFileLen <> 0 Then
    
        ReDim uSignatureA(1 To lFileLen / 66) As Signature
    
        **Get** lFile, , uSignatureA
    
        End If
    
        **Close** lFile
    
        End Select
    
        Next

有了这些前期准备，现在可以正式介绍扫描病毒的部分了，这些部分即相当于概念上的杀毒引擎，比较重要，请者朋友请仔细理解。

    
    
    Private Function **ScanSections** (hFile As Long) As String
    
        ScanSections = ""
    
        Dim uDos          As IMAGE_DOS_HEADER
    
        Dim uFile         As IMAGE_FILE_HEADER
    
        Dim uOptional     As IMAGE_OPTIONAL_HEADER
    
        Dim uSections()   As IMAGE_SECTION_HEADER
    
        Dim lBytesRead As Long
    
        Dim i As Long
    
        Dim bTempMemory() As Byte

把指针移动到文件头，读取PE信息

****

    
    
    **SetFilePointer** hFile, 0, 0, 0
    
        **ReadFile** hFile, uDos, Len(uDos), lBytesRead, ByVal 0&

根据DOS头的lfanew，指向PE头+4的地方(即文件头开始地址)

****

    
    
    **SetFilePointer** hFile, ByVal uDos.lfanew + 4, 0, 0

读取文件头

****

    
    
    **ReadFile** hFile, uFile, Len(uFile), lBytesRead, ByVal 0&

读取可选头

****

    
    
    **ReadFile** hFile, uOptional, Len(uOptional), lBytesRead, ByVal 0&
    
        ReDim uSections(uFile.NumberOfSections - 1) As IMAGE_SECTION_HEADER

读取节头

****

    
    
    **ReadFile** hFile, uSections(0), Len(uSections(0)) * uFile.NumberOfSections, lBytesRead, ByVal 0&

扫描每个节

    
    
    For i = 0 To UBound(uSections)
    
        ReDim bTempMemory(1 To uSections(i).SizeOfRawData) As Byte
    
        **SetFilePointer** hFile, ByVal uSections(i).PointerToRawData, 0, 0                    
    
        **ReadFile** hFile, bTempMemory(1), uSections(i).SizeOfRawData, lBytesRead, ByVal 0&
    
        Dim sTargetStr As String

构造特征码，特征码为：节大小+节的哈希值

    
    
    sTargetStr=uSections(i).SizeOfRawData&":"&LCase(HashFileStream(bTempMemory))
    
        Dim bTempStrByte() As Byte
    
        bTempStrByte = sTargetStr

用哈希算法加密特征码

    
    
    sTargetStr = **HashFileStream** (bTempStrByte)

特征码匹配检测

    
    
    Dim sMatchResult As String
    
        sMatchResult = **MatchSignature** (sTargetStr)

如果函数返回不为空表示检测到是病毒

    
    
    If sMatchResult <> "" Then
    
        ScanSections = Trim(sMatchResult)
    
        Exit Function
    
        End If
    
        Next i
    
        End Function

这个函数的主要能两有两处，一、分析PE文件，获取文件每个节的特征码；二、再次调用下级函数对节特征码进行检测，判断是否是病毒。并且使用的又是下级函数进行具体操作。

也许有的朋友会问：这已经多次使用下级函数进行特征码判断了，为什么不把代码顺序写下去，那样代码会更为工整，逻辑会更清晰。这是因为以上调用的每个下级函数都是一个相较独立的功能，且会在代码的其它地方被调次使用，写为独立函数从全局角度看会使函数调用关系更为合理，这了是一个良好的编程习惯。

接下来且看HashFileStream和MatchSignature两个关键函数：

    
    
    Public Function HashFileStream(ByteStream() As Byte) As String
    
        HashFileStream = ""
    
        Dim lCtx As Long
    
        Dim lHash As Long
    
        Dim lFile As Long
    
        Dim lRes As Long
    
        Dim lLen As Long
    
        Dim lIdx As Long
    
        Dim bHash() As Byte
    
        Dim bBlock() As Byte
    
        Dim bStream() As Byte
    
        ReDim bStream(1 To UBound(ByteStream)) As Byte
    
        CopyMemory bStream(1), ByteStream(1), UBound(ByteStream)

CryptAcquireContext功能：得到CS，即密码容器

参数说明：

> 参数1 lCtx : 返回CSP句柄
>
> 参数2 : 密码容器名,为空连接缺省的CSP
>
> 参数3 : 为空时使用默认CSP名(微软RSA Base Provider)
>
> 参数4 PROV_RSA_FULLCSP : 类型
    
    
    lRes = CryptAcquireContext(lCtx, vbNullString, vbNullString, PROV_RSA_FULL, 0)
    
        If lRes <> 0 Then

CryptCreateHash功能：创哈希对象

参数说明：

> 参数1: CSP句柄
>
> 参数2: 选择哈希算法，比如CALG_MD5等
>
> 参数3: HMAC 和MAC算法时有用
>
> 参数4: 保留，传入0即可
>
> 参数5:返回hash句柄
    
    
    lRes = CryptCreateHash(lCtx, ALGORITHM, 0, 0, lHash)
    
        If lRes <> 0 Then
    
        Const BLOCK_SIZE As Long = 32 * 1024&
    
        ReDim bBlock(1 To BLOCK_SIZE) As Byte
    
        Dim lCount As Long
    
        Dim lBlocks As Long
    
        Dim lLastBlock As Long

块个数

    
    
    lBlocks = UBound(ByteStream) \ BLOCK_SIZE

最后一个块

    
    
    lLastBlock = UBound(ByteStream) - lBlocks * BLOCK_SIZE
    
        For lCount = 0 To lBlocks - 1
    
        CopyMemory bBlock(1), bStream(1 + lCount * BLOCK_SIZE), BLOCK_SIZE

CryptHashData功能：哈希数据

参数说明：

> 参数1: 哈希对象
>
> 参数2: 被哈希的数据
>
> 参数3: 数据的长度
>
> 参数4: 微软的CSP这个值会被忽略
    
    
    lRes = CryptHashData(lHash, bBlock(1), BLOCK_SIZE, 0)
    
        Next
    
        If lLastBlock > 0 And lRes <> 0 Then
    
        ReDim bBlock(1 To lLastBlock) As Byte
    
        CopyMemory bBlock(1), bStream(1 + lCount * BLOCK_SIZE), lLastBlock
    
        lRes = CryptHashData(lHash, bBlock(1), lLastBlock, 0)
    
        End If
    
        If lRes <> 0 Then

CryptGetHashParam功能：取哈希数据大小

参数说明：

> 参数1：哈希对像
>
> 参数2：取哈希数据大小(HP_HASHSIZE)
>
> 参数3：返回hash数据长度
    
    
    lRes = CryptGetHashParam(lHash, HP_HASHSIZE, lLen, 4, 0)
    
        If lRes <> 0 Then
    
        ReDim bHash(0 To lLen - 1)

CryptGetHashParam功能：取得哈希数据

参数说明：

> 参数1：哈希对像
>
> 参数2：取哈希数据(值)(HP_HASHVAL)
>
> 参数3：哈希数组
    
    
    lRes = CryptGetHashParam(lHash, HP_HASHVAL, bHash(0), lLen, 0)
    
        If lRes <> 0 Then
    
        For lIdx = 0 To UBound(bHash)

构造hash值，2位一组，不足补0

    
    
    HashFileStream = HashFileStream & Right("0" & Hex(bHash(lIdx)), 2)
    
        Next
    
        End If
    
        End If
    
        End If
    
        CryptDestroyHash lHash
    
        End If
    
        End If
    
        CryptReleaseContext lCtx, 0
    
        End Function

以上使用的是微软提供的一组用于哈希计算的API函数，在我们的程序中用于算运算出可执行文件各节的哈希值，用途是得到文件节的哈希码，以进行特征码匹配
，检测扫描文件是否是病毒。而用于匹配算法的MatchSignature代码编码如下:

    
    
    Public Function MatchSignature(ByVal sHash As String) As String
    
        MatchSignature = ""
    
        If sHash = "" Then
    
        Exit Function
    
        End If

取哈希码值的第一位为标志，确定使用特征码类型

    
    
    Dim sFlagWord As String
    
        sFlagWord = UCase(Left(sHash, 1))
    
        Dim i As Long
    
        Select Case sFlagWord
    
        Case "0"
    
        For i = 1 To UBound(uSignature0)
    
        If uSignature0(i).sHash = sHash Then

匹配成功，返回病毒名称

    
    
    MatchSignature = uSignature0(i).sName
    
        Exit Function
    
        End If
    
        Next i
    
        Case "1"
    
        For i = 1 To UBound(uSignature1)
    
        If uSignature1(i).sHash = sHash Then

匹配成功，返回病毒名称

    
    
    MatchSignature = uSignature1(i).sName
    
        Exit Function
    
        End If
    
        Next i
    
        End Function

此处代码的功能是用于检测实现从PE文件中运算出的节特征码与病毒库中的特征码是否匹配，如果匹配则返回病毒名称。

到此，扫描病毒的功能的编码都已实现。

这里实现的仅仅是非感染型病毒木马的检测。在查杀时，仅需要简单的结束病毒进程、删除病毒文件即可完成。在近年来，绝大多数的病毒木马都是这种非感染型的，本世纪初及上世纪未DOS时代流行的感染型病毒已并不多见，当然并不是说完全不存在。对于感染型病毒的检测方式，与此大至相同，各位读者可以触类旁通使用类似的方法进行检测，只是在查杀方法上与此有所不同。并不能只是简单的进行文件删除操作，还需要对已感染的文件进行重写。

启发式病毒扫描技术是与此种特征码匹配检测完全不同的病毒木马检测技术。启发式也可以理解为行为分析，即根据病毒木马对系统入侵的行为进行检测，比如木马进入系统后，为了能够长期获得对系统的控制权，最基本的一点是要实现开机自启动，实现的方式可以通过写注册表自启动键值、关联文件类型、向系统添加服务、使用计划任务等等。木马的这些行为，会使系统配置、设置发生变化，在对系统相关信息熟悉的情况下，通过检查相关配置位置的内容，便可以发现木马入侵的蛛丝马迹，进而揪出木马本身。这一套操作，通过编程的方法进行实现便形成了启发式杀毒。当然，这只是实现启发式的一种方式，除此之外，还有其它多种实现方法，比如通过检测PE文件的函数导入列表中是否含有某种组织的函数、通过内置反汇编引擎判断PE文件的反汇编代码等等。

###  **2、防毒实现方案实编码实现**

防毒功能实现需要拦截进程启动行为，在一个进程启动前，先对其进行扫描，判断是否是病毒，如果是病毒立刻进行阻止。这也就是许多杀毒软件宣传的主动防御功能。

为了实现拦截功能，我们这里要使用API
Hook技术。拦截到进程时，获取到它的文件特征码，并在本地病毒库、黑名单、云病毒库中进行匹配校验，如果检测到是病毒，直接阻止。其程序流程如下图所示：

![](https://image.3001.net/images/20191114/1573715020_5dccfc4c9ba60.png!small)

实现拦截进程启动，可以由多种技术手段实现。可以修改SSDT表通过驱动实现，这是较底层的方式；也可以通过在用户层进行全局DLL注入实现。两者各有优劣。驱动方式更加接近系统底层，控制权限更高，但容易对系统稳定性造成影响，并且杀毒软件大多采用驱动方式，这样容易引发同类软件冲突、与同类软件不兼容等情况。DLL方式工作在用户层，对系统稳定性及性能影响小，并不易有同类软件兼容性问题。本杀毒软件设计中采用DLL注入方式。

大多数杀毒软件的防护功能，不仅仅会拦截进程启动，还会对注册表读写、文件读写等众多操作进行监管。而本设计中，只拦截启动行为，这样做的原因在于：防护的最核心最关键的就在于进程执行这一步，如果这一步被病毒通过，那么病毒可能会读写文件，可能会读写注册表，也可能会格式化磁盘，甚至会强行删除文件，一切都是不可预料的，做为杀毒软件，不可能接管系统所有的操作，也就是说，如果被病毒运行，等于防线已经崩溃了，系统已经被破坏了。而且，接管系统的各种操作，在系统中没有病毒的情况下，也会给系统本身带来很大的性能负担和运行风险。可能会使系统性能降低一半甚至更多，可能会使系统经常性的死机、蓝屏。用一个为了防止未知的风险，而付出如此多的代价是划不来的，用户也不愿意接受的。因此，在本软件中，仅最大化的加强执行防护这一个防毒门槛。带给用户安全的同时，又不影响用户使用电脑。

**云安全实现方案的引入**

从理论上来讲，云安全的实现，最少是需要一台服务器的，用于架设服务器、存储数据。架设服务器，需要云后台程序，存储数据，需要用安装数据库。

本设计中使用云安全，云安全后台使用ASP编写。数据库可以用MS-SQL或Access。

后台程序实现两个功能。其一，接收用户端杀毒软件传送的数据，数据为用户执行程序时获取的文件特征码，这个行为将用户端视为云的客户端，实现了采集数据的功能；其二，根据客户端请求进行查询并反馈结果。请求中附带的依然是特征码。根据云数据库中的数据，后台程序接收特征码进行校验查询，并反馈查询结果给客户端，这个操作用于防毒功能。即上文所讲的防毒方案中的查询云安全病毒库过程。接收到的数据存储在数据库中，可由维护人员操作，或由云后台根据数据情况按一定规则返回查询结果给客户端软件。

![](https://image.3001.net/images/20191114/1573715052_5dccfc6cb86b5.png!small)

数据量和用户量都较小的时候，可以使用Access，服务器可以使用虚拟主机代替。

且看拦截进程启动的编程实现：

系统在启动一个进程时，在用户层是通过调用API函数:CreateProcess实现的。拦截进程启动行为，我们要做的就是Hook这个API。要实现API
Hook,并在拦截后执行相应的操作，单纯VB是做不到的。这时需要用VC开发一个DLL文件供VB调用。软件运行时，DLL将被注入到所有系统进程中，接管各进程中的CreateProcess函数。这样，无论是哪个程序调用CreateProcess启动程序，DLL都会将暂停这个启动行为，并将被启动的文件信息发给杀毒软件，由杀毒软件判断安全性，根据判断结果决定是否允许程序启动。如果这时检测到是病毒在启动，杀毒软件会告诉DLL：这是病毒，不能让它启动。病毒的启动行为就被阻止了。

来看代码：

DLL部分：

Dll入口函数：

    
    
    BOOL APIENTRY DllMain( HANDLE hModule, DWORD  ul_reason_for_call, LPVOID lpReserved)
    
        {
    
        hMod = (HINSTANCE)hModule;
    
        if (ul_reason_for_call==DLL_PROCESS_ATTACH)
    
        {
    
        hProcess=OpenProcess(PROCESS_ALL_ACCESS,0, CurrentProcessId());

获取我们设计的杀毒软件的标题，以便发送消息进行通迅

hExe = FindWindow(NULL, "Ty2y杀毒软件");

DLl被加载时对createprocess函数进行Hook

****

    
    
    **HookCreateProcess** ();
    
        }
    
        if (ul_reason_for_call==DLL_PROCESS_DETACH) 
    
        {
    
        HookStatus(FALSE);
    
        }
    
        return TRUE;
    
        }

Hook createprocess函数:

    
    
    BOOL **HookCreateProcess** ()
    
        {
    
        ULONG JmpAddr=0;

获取该GetProcAddress函数原始地址

    
    
    FunAddr=(ULONG)GetProcAddress(LoadLibrary("Kernel32.dll"), "CreateProcessW");

保存原始地址，以备恢复挂钩时使用

    
    
    memcpy(OldCode, (void *)FunAddr, 5);

构造汇编跳转指令

    
    
    NewCode[0] = 0xe9;
    
        JmpAddr = (ULONG)CreateProcessWCallBack - FunAddr - 5;
    
        CreateProcessWCallBack的地址
    
        memcpy(&NewCode[1], &JmpAddr, 4);

启用API
Hook，此处将CreateProcessW函数替代为我们自定义的CreateProcessWCallBack函数地址，当有启动进程操作时，由CreateProcessWCallBack进行管理

    
    
    HookStatus(TRUE);
    
        return TRUE;
    
        }

CreateProcessW的替代函数，拥有与CreateProcessW相同的参数：

    
    
    BOOL WINAPI CreateProcessWCallBack
    
        (
    
        LPCWSTR lpApplicationName, 
    
        LPWSTR lpCommandLine,
    
        LPSECURITY_ATTRIBUTESlpProcessAttributes,
    
        LPSECURITY_ATTRIBUTESlpThreadAttributes,
    
        BOOL bInheritHandles,
    
        DWORD dwCreationFlags,
    
        LPVOID lpEnvironment,  
    
        LPCWSTR lpCurrentDirectory,
    
        LPSTARTUPINFOW lpStartupInfo,
    
        LPPROCESS_INFORMATION lpProcessInformation
    
        )
    
        {
    
        BOOL b=FALSE;

获取要启动的进程

    
    
    char AppName[256]={0};
    
        WideCharToMultiByte(CP_ACP, 0,(const unsigned short *)lpApplicationName, -1, AppName, 256,NULL, NULL); 
    
        char* CopyData="";

连接字符串：进程和命令行，用于发送给杀毒软件

    
    
    strcpy(CopyData,AppName);
    
        strcat(CopyData,"$");
    
        COPYDATASTRUCT cds={0};
    
        cds.lpData = CopyData;
    
        cds.cbData = 1024;

取得dll所在进程pid

    
    
    DWORD dwProcessId;
    
        dwProcessId=GetCurrentProcessId();
    
        DWORD ret;

向杀毒软件发送消息，并等待返回结果

    
    
    ret=SendMessage(hExe, WM_COPYDATA, dwProcessId, (LPARAM)&cds);

如果返回值是915，这个值是自定义的，这个值表明杀毒软件已经检验过被启动文件，并且是安全的，可以启动。

    
    
    if(ret==915)
    
        {

设置拦截状态，暂不否启用API Hook。如果此处不做修改，CreateProcessWCallBack会一直有效，形成错误的递规调用，任何程序都启动不了。

    
    
    HookStatus(FALSE);

启动进程

    
    
    b = CreateProcessW
    
        (
    
        lpApplicationName, 
    
        lpCommandLine,
    
        lpProcessAttributes,
    
        lpThreadAttributes,
    
        bInheritHandles,
    
        dwCreationFlags,
    
        lpEnvironment,
    
        lpCurrentDirectory,
    
        lpStartupInfo,
    
        lpProcessInformation
    
        );

启动后立刻启用API Hook，继续监控进程启动行为

    
    
    HookStatus(TRUE);
    
        return b;
    
        }
    
        else
    
        {

如果返回值不是915，表达在杀毒软件中检测到被启动文件是病毒或是其它恶意文件。直接返回，阻止程序启动。这时软件中也有相应的提示及操作。

    
    
    return FALSE;
    
        }
    
        return FALSE;
    
        }

设置API Hook启用状态状态

    
    
    BOOL HookStatus(BOOL Status)
    
        {
    
        BOOL ret=FALSE;
    
        if (Status) 
    
        {

将CreateProcessW入口地址写为我们自己定义的函数，API Hook启用

    
    
    ret = WriteProcessMemory(hProcess, (void *)FunAddr, NewCode, 5, 0);
    
        if (ret) return TRUE;
    
        }
    
        else 
    
        {

将CreateProcessW入口地址写为原始函数CreateProcessW的地址，API Hook停止

    
    
    ret = WriteProcessMemory(hProcess, (void *)FunAddr, OldCode, 5, 0);
    
        if (ret) return TRUE;
    
        }
    
        return FALSE;
    
        }
    
        LRESULT CALLBACK HookProc(int nCode,WPARAM wParam,LPARAM lParam){
    
        return(CallNextHookEx(hHook,nCode,wParam,lParam));
    
        }

这是输出函数，用于在应用程序中调用，关闭API HOOK

    
    
    BOOL WINAPI **ActiveDefenseOFF** ()
    
        {
    
        return(UnhookWindowsHookEx(hHook));
    
        }
    
        这是输出函数，用于在应用程序中调用，启用API HOOK
    
        BOOL WINAPI ActiveDefenseON(DWORD uPID)
    
        {

取得上层应用程序传来的参数:PID值0

    
    
    dwLordPid=uPID;

设置系统钩子，向各活动进程注入此DLL

    
    
    hHook = SetWindowsHookEx(WH_GETMESSAGE,(HOOKPROC)HookProc, hMod, 0);
    
        if (hHook) 
    
        {
    
        return TRUE;
    
        }
    
        else
    
        {
    
        return FALSE;
    
        }
    
        }

在此DLL中，使用SetWindowsHookEx函数向所有进程注入此DLL，DLL初注入后，接管各进程中的CreateProcessW系统函数，此函数可以控制进程启动操作，当检测到进程启动后，暂停启动行为，获取进程的完整路径，并传递给上层执行文件，也就是我们的杀毒软件主程序。传递到主程序后，主程序中对文件进行扫描，此时DLL中还在等待上层主程序的处理结果，当在主程序中扫描完成后，反馈信息给DLL：如果是病毒，会中止此进程的启动行为，否则让程序完成启动。这就就完成了对病毒的主动防御。

在主程序要，为了与DLL呼应，完成相应的功能，需要两方面的操作，一方面接管窗口消息，以实现DLL发送消息的响应；另一方面，完成文件扫描并向DLL回应消息。

编码如下：

    
    
    用SetWindowLong函数，将把程序的消息权交给SubClassMessage函数。
    
        SetWindowLong hWnd, -4, AddressOf SubClassMessage
    
        这样我们就可以在SubClassMessage函数中获取DLL发来的数据。如下：
    
        Public Function SubClassMessage(ByVal lHwnd As Long, ByVal lMessage As Long, ByVal lParentPID As Long, ByVal lParam As Long) As Long
    
         ...
    
        Dim sTemp As String
    
        Dim uCDS As COPYDATASTRUCT
    
        判是否是DLL传来的消息，上文中DLL发送消息的参数WM_COPYDATA值等于&H4A
    
        If lMessage = &H4A Then
    
        CopyMemory uCDS, ByVal lParam, Len(uCDS)
    
        sTemp = Space(uCDS.cbData)
    
        CopyMemory ByVal sTemp, ByVal uCDS.lpData, uCDS.cbData
    
        获取拦截到的正要启动的程序
    
        Dim sFile As String
    
        sFile = Left(sTemp, InStr(1, sTemp, "$") - 1)
    
        sTemp = Right(sTemp, Len(sTemp) - InStr(1, sTemp, "$"))
    
        end if
    
        End function
    
        获取到要启动的程序后，便可使上前面介绍过的扫描病毒代码对文件进行检测。并根据扫描结果向DLL返回消息。编码如下：
    
        Dim sScanResult As String
    
        sScanResult = **ScanFile** (sFile)
    
        If sScanResult ="" then
    
        SubClassMessage =915
    
        else
    
        SubClassMessage = 0
    
        End if

同样是调用前面讲过的ScanFile函数对文件进行扫描，如果返回为空说明没有检测到病毒，文件是安全的，则给SubClassMessage赋值915。这句代码代码的意思是：SubClassMessage函数是主程序负责消息处理的函数，DLL中将消息发送到主程序后，将由此函数负责处理，此函数获取赋值后，相当于是函数的返回值，也就是DLL中使用SendMessage函数发送消息后要等待的消息返回结果。这里的赋值，会直接传递给DLL。而915这个数字我们在前面已经提过，是自定义的一个数值，如果DLL中接收到此值，表明文件没有扫描到病毒是安全的。反之返回0的含意与此类似。

这是防毒功能中使用传统特征码扫描识别的实现，我们前面过要在防毒中使用云安全技术。接下来进行相关介绍。

当本地病毒库特征码校验没有扫描到病毒后，时此可以使用云安全扫描，进行二次检测。编码如下：

    
    
    sCloudAskRet=CloudMatch("http://ty2y.com/ask.asp?Hash="&HashFile(sFile))  
    
    
        我们约定：如果返回值不为空说明是病毒
    
        If sCloudAskRet <> "" Then
    
        Dim sCloudName As String
    
        此处是获取病毒文件描述，返回的数据中用“$”符号做为判断分隔符
    
        sCloudName = Right(sCloudAskRet, Len(sCloudAskRet) - InStr(1, sCloudAskRet, "$"))
    
        用与上面同样的方法向DLL回应消息                            
    
        SubClassMessage = 0
    
        End If

这里需要说明的是，使用云安全检测，同样是需要提取文件的特征码，并将特征码发送给云安全服务器。在这里我们使用不同于病毒库中的特征码格式，云安全中将文件整体的哈希码做为特征码。这样做是为了存储和查询的方便。上面代码中HashFile函数，用于获取文件的云安全特征码。编码如下：

    
    
    Function HashFile(ByVal sFilename As String) As String
    
        HashFile = ""
    
        Dim lCtx As Long
    
        Dim lHash As Long
    
        Dim lFile As Long
    
        Dim lRes As Long
    
        Dim lLen As Long
    
        Dim lIdx As Long
    
        Dim bHash() As Byte
    
        If Len(Dir(sFilename)) = 0 Then
    
        Exit Function
    
        End If
    
        lRes = CryptAcquireContext(lCtx, vbNullString, vbNullString, PROV_RSA_FULL, 0)
    
        If lRes <> 0 Then
    
        lRes = CryptCreateHash(lCtx, ALGORITHM, 0, 0, lHash)
    
        If lRes <> 0 Then
    
        lFile = FreeFile
    
        Open sFilename For Binary As #lFile
    
        Const BLOCK_SIZE As Long = 32 * 1024&
    
        ReDim bBlock(1 To BLOCK_SIZE) As Byte
    
        Dim lCount As Long
    
        Dim lBlocks As Long
    
        Dim lLastBlock As Long
    
        lBlocks = LOF(lFile) \ BLOCK_SIZE
    
        lLastBlock = LOF(lFile) - lBlocks * BLOCK_SIZE
    
        For lCount = 1 To lBlocks
    
        Get lFile, , bBlock
    
        lRes = CryptHashData(lHash, bBlock(1), BLOCK_SIZE, 0)
    
        Next
    
        f lLastBlock > 0 And lRes <> 0 Then
    
        ReDim bBlock(1 To lLastBlock) As Byte
    
        Get lFile, , bBlock
    
        lRes = CryptHashData(lHash, bBlock(1), lLastBlock, 0)
    
        End If
    
        Close lFile
    
        If lRes <> 0 Then
    
        lRes = CryptGetHashParam(lHash, HP_HASHSIZE, lLen, 4, 0)
    
        If lRes <> 0 Then
    
        ReDim bHash(0 To lLen - 1)
    
        Res = CryptGetHashParam(lHash, HP_HASHVAL, bHash(0), lLen, 0)
    
        If lRes <> 0 Then
    
        For lIdx = 0 To UBound(bHash)
    
        HashFile = HashFile & Right("0" & Hex(bHash(lIdx)), 2)
    
        Next
    
        End If
    
        End If
    
        End If
    
        CryptDestroyHash lHash
    
        End If
    
        End If
    
        CryptReleaseContext lCtx, 0
    
        End Function

此函数跟前面讲过的HashFileStream函数代码非常接近，上文中已对HashFileStream函数做过详细讲解，在此不再缀述。

上面的代码中获取了文件的云安全特征码后，使用CloudMatch函数进行云安全校验。CloudMatch函数中将连接云安全服务器，向云后台传递云安全特征码，通过调用云安全后台程序判断文件是否是病毒，编码代码如下：

    
    
    Public Function CloudMatch(sUrl As String) As String
    
        Dim lInternetOpenUrl As Long
    
        Dim lInternetOpen As Long
    
        Dim sTemp As String * 1024
    
        Dim lInternetReadFile As Long
    
        Dim lSize As Long
    
        Dim sContent As String
    
        sContent = vbNullString
    
        lInternetOpen = InternetOpen("Cloud", 1, vbNullString, vbNullString, 0)
    
        If lInternetOpen Then
    
        连接云后台，sUrl是云后台程序的网络地址
    
        lInternetOpenUrl = **InternetOpenUrl** (lInternetOpen, sUrl, vbNullString, 0, INTERNET_FLAG_NO_CACHE_WRITE, 0)
    
        If lInternetOpenUrl Then
    
        Do
    
        读取云后台反馈的内容
    
        lInternetReadFile = **InternetReadFile** (lInternetOpenUrl, sTemp, 1024, lSize)
    
        sContent = sContent & Mid(sTemp, 1, lSize)
    
        Loop While (lSize <> 0)
    
        End If
    
        如果云安全后台检测到病毒，返回的内容格式为：Cloud$(云安全标识)+病毒名称/病毒描述
    
        If UCase(Left(sContent, 6)) = UCase("Cloud$") Then
    
        CloudMatch = Right(sContent, Len(sContent) - 6)
    
        Else
    
        CloudMatch = ""
    
        End If
    
        End Function

**云安全服务端编程**

上面的代码中查行云安全查询时，是这样调用的：“sCloudAskRet =
CloudMatch("<http://ty2y.com/ask.asp?Hash=>" & HashFile(sFile))”

不难看出，“<http://ty2y.com/ask.asp>”此地址便是云安全的后台程序，在本例中，后台程序由asp写成，负责处理杀毒软件发起的查询，并返回云安全扫描结果。编码如下：

    
    
    <%
    
        取得杀毒软件中传递的文件特征码
    
        dim sHash
    
        sHash=trim(request("Hash"))
    
        dim conn
    
        dim connstr
    
        dim rs
    
        dim sql
    
        连接数据库,云安全的特征码存储在数据库，数据库可以使用MsSql、MySql等各种数据库，甚至是Access，为了演示编码方便，这里我们采用最简单的Access数据库	
    
        set conn=server.createobject("ADODB.CONNECTION")
    
        onnstr="DBQ="+server.mappath("cloud.mdb")+";DefaultDir=;DRIVER={Microsoft Access Driver (*.mdb)};"
    
        conn.open connstr
    
        set rs=createobject("adodb.recordset")
    
        进行SQL查询，病毒库中是否有传特来的特征码
    
        sql="select * from Cloud where Hash='" & sHash & "'"
    
        rs.open sql,conn,1,3
    
        if rs.recordcount=1 then
    
        response.write "Cloud$云安全检测到病毒"
    
        end if
    
        rs.close
    
        set rs=nothing 
    
        set conn=nothing 
    
        %>

到此，杀毒和防毒两个最核心功能的基本讲解已完成。也许有读者会疑惑、会意犹未尽:为什么这么简单？是的，确实很简单，到此，本文使用较少量的代码已经完成了这两个功能的介绍和编码实现演示，之所以使用能由如此少量的代码完成，原因在于省略掉了其它部分代码量非常大的会影响功能实现直观性的编码，只保留了相关的核心代码。这是一种模块化的功能演示编码，也只有这样，才能明了的完成这两个功能的讲解。其它相关部分，如黑白名单的使用、设置选项的关联、与界面的互交代码等等会单独进行讲解。本文后面部分中讲述其它功能时，也会采用类似的方法。

###  **3、** **升级实现方案及编码实现**

杀毒软件需要及时升级病毒库，更新特征码，以保护能够识别最新爆发的病毒。为了完成这个操作，需要用到升级服务器（或者虚拟主机也可以满足基本需要）。将要升级的文件，连同新的版本号文件放置在服务器固定位置上。软件中以IP地址或域名的方式访问这个版本号文件，获取最新的版本号，然后跟保存在用户端本地的版本号进行对比。如果检测到服务器上的版本号更高，表明有新的文件需要升级。

升级其实是一个很简单的功能，主要实现的是文件下载功能，为了能够在程序中进行版本号判断以及替换正在执行的文件等操作，我们将此功能分为两个部分，一部分写在应用程序中，一部分写做一个单独的模块控件。编码如下：

主动事件：用于向用户显示下载进度

    
    
    Public Event DownloadProcess(lProgress As Long)

主动事件，下载完文件后触发

    
    
    Public Event DownLoadFinish()

主动事件，错误信息输出

    
    
    Public Event ErrorMassage(sDescription As String)

控件初始化函数

    
    
    Public Function Init() As Boolean
    
        bConnect = True

该函数是第一个由应用程序调用的 WinINet 函数。它告诉 Internet DLL
初始化内部数据结构并准备接收应用程序之后的其他调用。当应用程序结束使用 Internet 函数时，应调用 InternetCloseHandle
函数来释放与之相关的资源

    
    
    lOpen = InternetOpen(scUserAgent, INTERNET_OPEN_TYPE_PRECONFIG, vbNullString, vbNullString, 0)

通过一个完整的FTP，Gopher或HTTP网址打开一个资源。

    
    
    lFile = InternetOpenUrl(lOpen, sUrl, vbNullString, 0, INTERNET_FLAG_RELOAD, 0)
    
        sBuffer = Space(1024)
    
        lBuffer = 1024

从服务器获取 HTTP 请求头信息

    
    
    bRetQueryInfo = HttpQueryInfo(lFile, 21, sBuffer, lBuffer, 0)
    
        sBuffer = Mid(sBuffer, 1, lBuffer)
    
        End Function

开始下载文件

    
    
    Public Function StartUpdate() As Boolean
    
        Dim bBuffer(1 To 1024) As Byte
    
        Dim lRet As Long
    
        Dim lDownloadSize As Long
    
        Dim i As Long
    
        Dim lFileNumber As Long
    
        lFileNumber = FreeFile()

下载保存文件方式:下载保存为file.exe.bak 下载完后 删除file.exe 重命名 file.exe.bak 为file.exe

    
    
    Dim sTempDownloadFile As String
    
        sTempDownloadFile = Trim(sSaveFile) & ".bak"
    
        If Dir(sTempDownloadFile) <> "" Then
    
        Call DeleteFile(sTempDownloadFile)
    
        End If

打开文件，保存下载数据

    
    
    Open sTempDownloadFile For Binary Access Write As #lFileNumber
    
        Do

读取被下载文件内容

    
    
    InternetReadFile lFile, bBuffer(1), 1024, lRet
    
        If lRet = 1024 Then

将读取到的数据写入文件

    
    
    Put #1, , bBuffer
    
        Else
    
        For i = 1 To lRet
    
        Put #1, , bBuffer(i)
    
        doEvents
    
        Next i
    
        end If
    
        lDownloadSize = lDownloadSize + lRet

引发下载进度事件

    
    
    RaiseEvent DownloadProcess(lDownloadSize)
    
        Loop Until lRet < 1024
    
        Close #lFileNumber

检查已下载字节数与要下载文件大小是否一至，一至说明下载完成了。

    
    
    If lDownloadSize = CLng(GetHeader("Content-Length")) Then

下载完成，删除原文件，重命名下载文件为原文件名

    
    
    If Dir(Trim(sSaveFile)) <> "" Then
    
        Call DeleteFile(sSaveFile)
    
        End If
    
        Sleep 50
    
        If Dir(sSaveFile) = "" Then

重命名下载的文件

    
    
    Name sTempDownloadFile As sSaveFile
    
        End If
    
        DoEvents  
    
        End If
    
        End Function

获取要下载文件的信息

    
    
    Public Function GetHeader(Optional hdrName As String) As String
    
        Dim sTemp As Long
    
        Dim sTemp2 As String
    
        Select Case UCase(hdrName)

获取要下载的文件大小

    
    
    Case "CONTENT-LENGTH"
    
        sTemp = InStr(sBuffer, "Content-Length")
    
        sTemp2 = Mid(sBuffer, sTemp + 16, Len(sBuffer))
    
        sTemp = InStr(sTemp2, Chr(0))
    
        GetHeader = CStr(Mid(sTemp2, 1, sTemp - 1))
    
        End Select
    
        End Function

控件设置属性，URL地址

    
    
    Public Property Let URL(ByVal sInUrl As String)
    
        sUrl = sInUrl
    
        End Property

以上是控件中的编码，之所以使用控件，是为了能够使用主动事件，方向的与界面互交，即时的显示下载进度，下载完成后也能有相应的消息提示。

在程序更新病毒库或其它程序文件时，首先会进行如下的方式进行调用获取文件版本号：

    
    
    Dim sUpdateFiles As String
    
        sUpdateFiles= **DetectUpdateFile** ("<http://ty2y.com/update/update.txt>")

DetectUpdateFile函数的代码如下：

    
    
    Public Function DetectUpdateFile(sUrl As String) As String
    
        Dim lInternetOpenUrl As Long
    
        Dim lInternetOpen As Long
    
        Dim sTemp As String * 1024
    
        Dim lInternetReadFile As Long
    
        Dim lSize As Long
    
        Dim sContent As String
    
        sContent = vbNullString
    
        lInternetOpen = InternetOpen("update", 1, vbNullString, vbNullString, 0)
    
        lInternetOpenUrl = InternetOpenUrl(lInternetOpen, sUrl, vbNullString, 0, INTERNET_FLAG_NO_CACHE_WRITE, 0)
    
        Do
    
        lInternetReadFile = InternetReadFile(lInternetOpenUrl, sTemp, 1024, lSize)
    
        sContent = sContent & Mid(sTemp, 1, lSize)
    
        Loop While (lSize <> 0)
    
        lInternetReadFile = InternetCloseHandle(lInternetOpenUrl)

升级查询返回以“Update”开始为标识

    
    
    If UCase(Left(sContent, 6)) = UCase("Update") Then
    
        DetectUpdateFile = Right(sContent, Len(sContent) - 6)
    
        Else
    
        DetectUpdateFile = ""
    
        End If
    
        End Function

这部分代码与上面文件下载控件中的代码非常类似，都是用来下载文件的，不同在于此处下载文件后会读取文件内容。

文件内容是我们预设好的，本地设置文件中版本号，升级时，从服务器下载版本号文件并从中读取内容获取最新整体版本号，与当前软件中的整体版本号进行比对，如果网络中的版本号更高，则进行更新，调用升级控件下载升级文件。每次升级把设置文件同时也下载，以同步版本号。

我们设定版本号文件格式为："Update"(6位，用于标识是升级校验文件)+版本号(6位)+待升级文件+"$"（结束符）

然后对比版本号，如果服务器中的版本号更高，则表示有文件需要下载更新，那么我们就需要下载文件。编码如下：

取得服务器文件中的版本号

    
    
    Dim lNewWholeVersion As Long
    
        lNewWholeVersion = Left(sUpdateFiles, 6)
    
        sUpdateFiles = Right(sUpdateFiles, Len(sUpdateFiles) - 6)

取得本地版本号，在这里Version.ini文件中存放着本地版本号

    
    
    Dim sVersionFile As String
    
        sVersionFile = App.Path & "\Version.ini"
    
        Dim lOldWholeVersion As Long
    
        lOldWholeVersion = ReadIni(sVersionFile, "Version", "WholeVersion")

判断是否需要升级

    
    
    If lNewWholeVersion <= lOldWholeVersion Then  
    
    
        MsgBox "已是最新版本，无需升级。"
    
        End If

如果有持更新内容,从返回内容中获取要升级的文件并下载

    
    
    Do While Not sUpdateFiles = ""
    
        sNewFile = Left(sUpdateFiles, InStr(1, sUpdateFiles, "$") - 1)
    
        sUpdateFiles = Right(sUpdateFiles, Len(sUpdateFiles) - InStr(1, sUpdateFiles, "$"))

如果是要下载exe文件，先用MoveFileEx函数去掉它的执行保护，这样就不会出现替换正在执行的文件时失败的情况

    
    
    If InStr(1, LCase(sNewFile), LCase(".exe")) Then
    
        Call MoveFileEx(sNewFile, RndChr(6), 1)
    
        End If

使用上面写好的升级控件，假设控件名为UserControlUpdate1

    
    
    With UserControlUpdate1

构造文件下载地址

    
    
    .URL = "<http://ty2y.com/update/>" & sNewFile 
    
        .SaveFile = App.Path & "\" & sNewFile 
    
        If .Init = True Then
    
        lCurrentFileSize = .GetHeader("Content-Length")

开始下载文件

    
    
    .StartUpdate
    
        End If
    
        End With
    
        Loop

以上是升级功能的思现思路及编码方法，在实际软件的编码中，除了实现文件下载的功能，还需要考虑其它辅助因素，比如在下地时，要将文件显示在界面中，告诉用户正在下载哪个文件，以及显示下载进度，以给用户一个更为直观和亲切的使用感受。

###  **4、** **自我保护设计方案及编码实现**

实现此功能，同样使用API
Hook技术，与上面介绍过的通过防护功能类似。只是这里不再是拦截CreateProcess,而是要接管OpenProcess函数。

也许有的程序员朋友会有疑惑，做我我保护，也就是要防止自己的进程被非法结束进程，在编程中，结束进程所使用API函数是TerminateProcess，而不是OpenProcess，这里为什么会说通过拦截OpenProcess实现保护进程呢？这是由于TerminateProcess函数结束进程时，需要使用进程句柄做为输入参数，结束传入的指定句柄的进程。在不同进程间句柄是无法传递的，好在进程ID是可以传递的，而在使用TerminateProcess函数结束进程前，会先调用OpenProcess打开进程并把句柄传递给TerminateProcess，而OpenProcess函数的输入参数恰好为进程ID。这也就是我们选择拦截OpenProcess的原因了。

防止被结束进程的原理其实很简单，将DLL注入其它进程后，接管进程的OpenProcess函数，在我们自己定义的新OpenProcess函数被调用，判断是否要打开我们杀毒软件的进程，并且其操作是否是要将要进程结束进程操作，如果是，就终止这个行为。这样便实现了保护，做到了进程防杀。

且看编码实现，首先是DLL中拦截OpenProcess的部分。鉴于上文中又详细介绍过拦截CreateProcess函数的方法，这里就不再重复对代码做说明了，参考上文代码中的注释说明即可。

    
    
    #include <windows.h>
    
        #include "stdio.h"
    
        #include "stdlib.h"
    
        #pragma data_seg(".Shared2") 
    
        static DWORD g_PID2Protect=0;
    
        #pragma data_seg() 
    
        #pragma comment(linker, "/section:.Shared2,rws") 
    
        HANDLE hProcess=0;
    
        UCHAR OldCode2[5]={0}, NewCode2[5]={0};
    
        ULONG FunAddr2=0;
    
        HINSTANCE hMod=0;
    
        HHOOK hHook=0;
    
        BOOL HookStatus2(BOOL Status){
    
        BOOL ret2=FALSE;
    
        if (Status) {
    
        ret2 = WriteProcessMemory(hProcess, (void *)FunAddr2, NewCode2, 5, 0);
    
        if (ret2) return TRUE;}
    
        else {
    
        ret2 = WriteProcessMemory(hProcess, (void *)FunAddr2, OldCode2, 5, 0);
    
        if (ret2) return TRUE;}
    
        return FALSE;
    
        }
    
        HANDLE WINAPI OpenProcessCallBack(DWORD dwDesiredAccess,BOOL bInheritHandle,DWORD dwProcessId)
    
        {
    
        HANDLE hProc=NULL;
    
        if(dwProcessId==g_PID2Protect && (dwDesiredAccess & PROCESS_TERMINATE!=0))
    
        {
    
        hProc=NULL;
    
        }else{
    
        HookStatus2(FALSE);
    
        hProc= OpenProcess(dwDesiredAccess,bInheritHandle,dwProcessId);
    
        HookStatus2(TRUE);
    
        }
    
        return hProc;
    
        }
    
        BOOL HookOpenProcess(){
    
        ULONG JmpAddr2=0;
    
        FunAddr2 = (ULONG)GetProcAddress(LoadLibrary("Kernel32.dll"), "OpenProcess");
    
        memcpy(OldCode2, (void *)FunAddr2, 5);
    
        NewCode2[0] = 0xe9;
    
        JmpAddr2 = (ULONG)OpenProcessCallBack - FunAddr2 - 5;
    
        memcpy(&NewCode2[1], &JmpAddr2, 4);
    
        HookStatus2(TRUE);
    
        return TRUE;
    
        }
    
        BOOL APIENTRY DllMain( HANDLE hModule,DWORD  ul_reason_for_call, LPVOID lpReserved)
    
        {
    
        hMod = (HINSTANCE)hModule;
    
        if (ul_reason_for_call==DLL_PROCESS_ATTACH)
    
        {
    
        hProcess = OpenProcess(PROCESS_ALL_ACCESS, 0, GetCurrentProcessId());
    
        HookOpenProcess();
    
        }
    
        if (ul_reason_for_call==DLL_PROCESS_DETACH) 
    
        {
    
        HookStatus2(FALSE);
    
        }
    
        return TRUE;
    
        }
    
        LRESULT CALLBACK HookProc(int nCode,WPARAM wParam,LPARAM lParam){
    
        return(CallNextHookEx(hHook,nCode,wParam,lParam));
    
        }
    
        BOOL WINAPI SafeGuardOFF(){
    
        return(UnhookWindowsHookEx(hHook));
    
        }
    
        BOOL WINAPI SafeGuardON(DWORD uPID){
    
        g_PID2Protect=uPID;
    
        hHook = SetWindowsHookEx(WH_GETMESSAGE,(HOOKPROC)HookProc, hMod, 0);
    
        if (hHook) 
    
        {
    
        return TRUE;
    
        }else{
    
        return FALSE;
    
        }
    
        }

由代码中可知，此DLL的导出函数有两个：SafeGuardON和SafeGuardOFF，SafeGuardON用于开启防护，参数是被保护进程的ID；SafeGuardOFF用于关闭防护。

在上层应用程序中，调用方法如下：

函数声明：

    
    
    Private Declare Function ActiveDefenseON Lib "ActiveDefense.dll" (ByVal TargetHwnd As Long) As Boolean
    
        Private Declare Function ActiveDefenseOFF Lib "ActiveDefense.dll" () As Boolean

调用调码再封装为函数：

    
    
    Public Function ActiveDefense(ByVal bOperation As Boolean) As Boolean
    
        Dim lPid As Long

获取当前进程PID，也就是我们杀毒软件的进程ID

    
    
    lPid = GetCurrentProcessId
    
        Dim bRet As Boolean
    
        If bOperation = True Then

开启主动防御

    
    
    bRet = ActiveDefenseON(lPid)
    
        If bRet Then
    
        ActiveDefense = True
    
        Else
    
        ActiveDefense = False
    
        End If
    
        Else

关闭主动防御

    
    
    ActiveDefenseOFF
    
        End If
    
        End Function

有此简单封装过的函数，当杀毒软件启动时调用，传入参数true便可开启防护，关闭程序时调用传入false便可停止防护。使用非常简单。

###  **5、** **黑白名单设计方案及编码实现**

黑白名单功能做为病毒库的辅助，主要用于病毒防护、减少误报、阻止非病毒类的边缘灰色文件。

在查杀病毒时，并不使用黑白名单，而在防毒的主动防御中我们使用它。前面我们已经讲过：当进程要启动时，会先使用病毒病毒库以特征码匹配的方法对其进行扫描，如果没有检测到病毒，会次使用云安全进行识别。黑白名单的引入，可以更进一步提升防毒效果，增强整体软件的防护功能。

我们进行如此设计：黑名白名数据文件，在本地存储时使用ini文件格式。ini文件内容由节和参数组成，可以方便进行少量数据的存储、修改、添加、删除。

黑白名单文件格式使用如下例：

    
    
    [Count]
    
        MaxID=0
    
        [File]
    
        00001=C:\WINDOWS\system32\cmd.exe
    
        [Signature]
    
        00001=83BA7E22BF529858A345F483D7E94C16
    
        [Description]
    
        00001=安全的文件
    
        [DefenseFlag]
    
        00001=1

Count节中，MaxID参数指明共有多少条数据。

File节中，序号对应的是文件。

Signature节中，序号对应的的是文件的特征码。

Description节中，序号对应的是对文件的描述。

DefenseFlag节中，序号对应的是处理规则。数字1代表安全的文件，执行放行操作；数字0代表是恶意文件，执行阻止操作。

程序编码时，相关操作代码置于上文中介绍过的SubClassMessage函数中，当获取到DLL专来的启动程序信息后，在黑白名单文件中进行匹配校验，如果检测到是安全的文件，则直接放行；如果检测到是恶意文件，直接阻止。且看代码：

获取黑白名单文件名,假设黑白名单文件名为ActiveDefense.ini

    
    
    Dim sDefenseIniFile As String
    
        sDefenseIniFile = App.Path & "\ActiveDefense.ini"
    
        End If

读取黑白名单文件中的记录数据量

    
    
    Dim lMaxID As Long
    
        lMaxID = ReadIni(sDefenseIniFile, "Count", "MaxID")

规则对应文件

    
    
    Dim sDefenseRuleFile As String

规则对应文件特征码

    
    
    Dim sDefenseRuleFileSignature As String

规则标志，1为放行，0为禁止

    
    
    Dim sDefenseRuleFileFlag As String

循环匹配黑白名单中的所有数据

    
    
    Dim i As Long
    
        For i = 1 To lMaxID

规则文件

    
    
    sDefenseRuleFile = ReadIni(sDefenseIniFile, "File", Format(i, "00000"))

文件特征码

    
    
    sDefenseRuleFileSignature = ReadIni(sDefenseIniFile, "Signature", Format(i, "00000"))

处理标志

    
    
    sDefenseRuleFileFlag = ReadIni(sDefenseIniFile, "DefenseFlag", Format(i, "00000"))  

这里假调sFile变量中保存的是DLL中传来的要启动的文件，获取文件的特征码，然后跟名单中所有记录进行匹配

    
    
    If (sDefenseRuleFileSignature = HashFile(sFile)) And (Len(sDefenseRuleFileSignature) = 32) And (Len(HashFile(sFile)) = 32) Then
    
        If CLng(sDefenseRuleFileFlag) = 1 Then

标志为1，执行放行操作。SubClassMessage函数在上面介绍过，是用来接收DLL消息的函数。给它赋值915，也就是令SubClassMessage函数的返回值为915。在讲前面讲的DLL编程中，DLL中使用“ret=SendMessage(hExe,
WM_COPYDATA, dwProcessId,
(LPARAM)&cds)”向程序发来了启动文件信息，同时在等待消息的返回。如果返回915，DLL中就会放行这个试图启动的文件。

    
    
    SubClassMessage = 915                                            
    
        Exit Function
    
        ElseIf CLng(sDefenseRuleFileFlag) = 0 Then
    
        标志为0，执行阻止操作。与返回915的行为刚好相反。
    
        SubClassMessage = 0
    
        Exit Function
    
        End If
    
        End If
    
        Next

代码中用到的HashFile函数即是上文中进行云安全扫描前用于获取文件特征码的函数。在黑白名单中使用的特征码，与云安全使用相同的特征码。

###  **6、** **设置实现方案**

软件设置选项以配置文件的形式保存在软件目录中，配置文件以文本方式保存，当用户在软件中改变设置时，将相应的标识记录在文件中，软件启动时自动加载配置信息并反应在软件中。

###  7、 **界面**

###  8、 **其它功能** ，如软件版本、病毒库版本等信息，从配置文件中读取，显示在软件界面相应位置。

 **框架设计**

![](https://image.3001.net/images/20191114/1573715943_5dccffe7a7447.png!small)

**设置选项功能编程**

软件的设置选项，即软件配置。同样使用ini文件的方式对软件的各种设置进行保存。保存时时使用代码如下：

    
    
        Dim sSettingsFile As String

软件设置记录文件

    
    
    If Right(App.Path, 1) = "\" Then
    
        sSettingsFile = App.Path & "Settings.ini"
    
        Else
    
        sSettingsFile = App.Path & "\Settings.ini"
    
        End If

自我保护设置

    
    
    Call WriteIni(sSettingsFile, "Normal", "SafeGuard", CheckSafeGuard.value)

自启动设置

    
    
    Call WriteIni(sSettingsFile, "Normal", "AutoRun", CheckAutoRun.value)

自动放入托盘图标

    
    
    Call WriteIni(sSettingsFile, "Normal", "AutoTray", CheckAutoTray.value)

WriteIni函数是经简单封装便用使用的ini操作函数，如下所示：

    
    
    Public Function WriteIni(ByVal sFile As String, ByVal sSection As String, ByVal sKeyName As String, ByVal sKeyValue As String) As Boolean
    
        Dim lRet As Long

调用API函数WritePrivateProfileString进行写操作

    
    
    lRet = WritePrivateProfileString(sSection, sKeyName, sKeyValue, sFile)
    
        If lRet = 0 Then

写文件失败，返回

    
    
    WriteIni = False
    
        Exit Function
    
        else

成功，返回

    
    
    WriteIni = True
    
        Exit Function
    
        end If
    
        End Function

进行读取操作时：

读取自我保护设置

    
    
    heckSafeGuard.value = ReadIni(sSettingsFile, "Normal", "SafeGuard")

读取自启动设置

    
    
    CheckAutoRun.value = ReadIni(sSettingsFile, "Normal", "AutoRun")

读取自动放入托盘图标设置

    
    
    CheckAutoTray.value = ReadIni(sSettingsFile, "Normal", "AutoTray")

读取扫描时减少CPU占用设置

    
    
    CheckLowCPU.value = ReadIni(sSettingsFile, "Scan", "CheckLowCPU")

使用ReadIni函数获取配置信息，直接赋值给界面中的控件。

ReadIni函数与WriteIni类似，如下：

    
    
    Public Function ReadIni(ByVal sFile As String, ByVal sSection As String, ByVal sKeyName As String) As String
    
        Dim lRet As Long
    
        Dim sTemp As String * 255

读操作

    
    
    lRet = GetPrivateProfileString(sSection, sKeyName, "", sTemp, 255, sFile)
    
        If lRet = 0 Then

返回空

    
    
    ReadIni = ""
    
        Exit Function
    
        else

去掉不可见字符，返回字据

    
    
    ReadIni = TrimNull(sTemp)
    
        End If
    
        End Function

设置选项相关的操作都是对ini文件进行读写，这里就不一一例举了。

到此，杀毒软件各核心功能的实现方法及编程思路已经基本介绍完毕，重点在于展示如何实现各自的功能。在完整的杀毒软件编程中的编写的代码，与前面的代码是有很大不同的，因为杀毒软件要整体以上所有功能，实现一个不可分隔的整体，各功能模块在很多方面是互有关联、相互影响的，代码也将会有条理的交织在一起。

欲了解更多、知晓细节，请直接阅读源码吧：<https://github.com/w2sft/Ty2yAntiVirus>

本文所讲种种，即是源自该杀毒软件。

##  **四、写在技术之外**

本文所设计和讲述的杀毒软件开发，实现了传统杀毒软件的基础、主要功能，实现了杀毒防毒功能。但从功能及性能强度方面而言，还仅属于中小型轻量级杀毒软件，与大型杀毒软件相比,如卡巴、Nod等，有差距。也有用户对如此设计软件的性能有怀疑，认为没有使用驱动，软件不够强大；在用户层做保护，安全防护性没达到最高，等等。这里我想说的是：我们开发杀毒软件，不是进行技术对抗、不是为了验证倒底是魔高一丈还是道高一尺、也不是为了研究和模拟同类产品的功能，而是为了方便用户，带给用户实实在在的使用效果，保护用户系统安全。

**尽请期待杀毒软件开发第二弹：《不传之密：杀毒软件开发之二，感染型病毒查杀、启发式杀毒》，将向您展示感染性病毒原理与编程、感染型病毒查杀方式，以及启发式杀毒技术原理和编程实战。**

 ***本文原创作者： w2sfoot，本文书友FreeBuf原创奖励计划，未经许可禁止转载**  
  

