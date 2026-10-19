# 七个致命缺陷界:软件安全错误的分类

本文翻译自fortify官方文档。

  

* * *

## 摘要

编码错误是软件安全中的一个重要问题。本研究报告将常见的编码错误类型组织成一个简单的分类法，以帮助开发人员和安全从业人员识别导致漏洞的问题类别，并帮助他们在构建软件时识别现有的错误。

我们的分类法中包含的信息能通过工具得到最有效地执行。事实上，我们分类法中包含的所有错误都可以使用静态源代码分析技术进行自动识别。

在本文中，我们演示了为什么我们的分类法会比其他现代分类法建议和漏洞列表更简单、更全面。我们在配套网站[www.fortifysoftware.com/vulncat](www.fortifysoftware.com/vulncat)上提供了对每个错误的深入解释和一个或多个代码级示例。

## 介绍

软件开发人员在构建安全的计算机系统中起着至关重要的作用。在定义编码错误的分类时，我们的主要目标是组织一组安全规则，这些规则可用于帮助软件开发人员理解对安全性有影响的错误类型。我们相信，向开发人员传递这些信息的最有效的方法之一是使用工具。我们的希望是，通过更好地理解系统是如何失败的，开发人员将更好地分析他们创建的系统，更容易地识别和处理安全问题，并且在将来通常避免重复相同的错误。

当在工具中工作时，根据这种分类法组织的一组安全规则是一种强大的教学机制。由于今天的开发人员基本上没有意识到他们可能在工作中引入安全问题的无数种方式，因此像这样的分类法的发布应该为软件安全社区提供切实的好处。

定义一个更好的分类方案也可以带来更好的工具:更好地理解问题将有助于研究人员和从业者创造更好的方法来寻找问题。

我们提出了一个简单的、直观的分类法，我们认为这是我们组织软件安全规则集的最佳方法，这些规则集将教会软件开发人员有关安全性的知识。我们的方法是CVE
(Common vulnerabilities and
Exposures)[7]提供的高度特定的攻击类型和漏洞列表的替代方案，CVE缺乏分类的方式，本质上是可操作的。我们的分类方案适用于自动识别，并且可以与静态分析工具一起用于检测软件中的真实安全漏洞。我们的方法也是许多专门针对操作系统相关漏洞的广泛分类方案的替代方案[1,2,3,12,19]。我们将在第2节中讨论这些分类法。

第3节激励了我们的工作，并讨论了编码错误与相应攻击之间的关系。它还定义了本文其余部分使用的术语。第4节描述了我们提出的方案。我们把一种编码错误称为门，把一组相关的门称为界。每个门的完整描述可在本文的配套网站上找到[8]。第5节对比了其他两个漏洞列表[11,17]。第6节总结。

## 相关工作

  

* * *

所有科学学科都受益于组织其研究主题的方法，软件安全也不例外。分类方案的价值是无可争辩的:为了创建通用词汇表和理解计算机安全失败的方式，分类法是必要的。自20世纪70年代中期以来，定义分类法的问题一直引起人们极大的兴趣。从那时起，已经提出了几种分类方案[4]。

计算机安全和隐私的最早研究之一是RISOS(安全操作系统研究)项目[1]。RISOS提出并描述了7类操作系统安全缺陷。该项目的目的是了解现有操作系统(包括MULTICS、TENEX、TOPS-10、GECOS、OS/MVT、SDS-940和EXEC-8)中的安全问题，并确定增强这些系统安全性的方法。RISOS项目建议的类别包括:

  * 参数验证不完整

  * 参数验证不一致

  * 隐式共享特权/机密数据

  * 异步验证/序列化不足

  * 识别/认证/授权不足

  * 违反禁令/限制

  * 可利用的逻辑错误

  * 研究表明，有少数基本缺陷在不同的环境中反复出现。

Protection Analysis
(PA)项目[3]的目标是通过使用模式导向的方法，使任何人(具有或不具有计算机安全知识)都能发现系统中的安全错误。其思想是使用形式化的模式来搜索相应的错误。PA项目是第一个探索安全缺陷检测自动化的项目。然而，将缺陷减少到抽象模式的过程并不全面，并且该技术不能适当地自动化。研究中收集的漏洞数据库从未发表过。

Landwehr、Bull、McDermott和Choi[12]从三个角度对每个漏洞进行分类:起源(问题如何进入系统)、时间(问题在生产周期中的哪一点进入系统)和位置(问题在系统中的哪个位置出现)。缺陷在起源上被分解为有意和无意，其中有意类进一步被分解为恶意和非恶意。在引入时，缺陷被分解为开发、维护和操作，其中开发类被进一步分解为设计、源代码和目标代码。缺陷按位置划分为软件和硬件，其中软件类进一步划分为操作系统、支持和应用程序。Weber、Karger和Paradkar[21]也提出了一个非常相似的方案。然而，他们的方案仅根据起源对漏洞进行分类。

这种类型的分层分类的优点是可以方便地识别解决安全问题的策略。例如，如果大多数安全性问题是无意中引入的，那么增加用于代码审查的资源将成为增加系统安全性的有效方法。该方案最大的缺点是无法对现有的一些漏洞进行分类。例如，如果不知道漏洞是如何进入系统的，则根本无法按起源对其进行分类。

另一个与我们的讨论相关的方案是ODC(正交缺陷分类)[19]，它被IBM提出并广泛使用。ODC根据错误类型(低级编程错误)和触发事件(导致缺陷的环境特征)对缺陷进行分类。此外，每个缺陷都有严重程度和症状特征。然而，ODC关注的是操作系统质量问题，而不是安全问题。

范畴的宽度使分类模糊不清。在某些情况下，一个问题可以分为多个类别。类别名称虽然对某些研究小组很有用，但对于开发人员来说，在日常工作的背景下，它们太过通用，无法快速直观。此外，这些方案主要关注操作系统安全问题，而没有对与用户级软件安全相关的问题进行分类。此外，这些分类法混合了实现级和设计级缺陷，并且在定义与问题的原因或结果相关的类别时不一致。

Landwehr, Bull,
McDermott和Choi所做的工作后来由Viega扩展[20]。除了根据起源、时间和位置对漏洞进行分类外，他还根据后果(错误造成的危害的影响)和其他杂项信息(包括平台、所需资源、严重性、利用的可能性、避免和缓解技术以及相关问题)对漏洞进行分类。对每个类别都进行了详细的讨论，并提供了具体的示例，在某些情况下还包括代码摘录。Viega称之为“根本原因”数据库，它努力为构成许多已知安全缺陷基础的潜在问题提供一个词典。因此，并非此分类法中的所有问题都是安全问题。此外，“rootcause”数据库允许根据分类人员的兴趣对同一个问题进行不同的分类。

Cheswick、Bellovin和Rubin[5]提供了一个很好的攻击类列表。清单包括:

  * 窃取密码

  * 社会工程

  * 漏洞和后门

  * 认证失败

  * 协议故障

  * 信息泄露

  * 指数攻击——病毒和蠕虫

  * 拒绝服务攻击

  * 僵尸网络

  * 主动攻击

每个类都提供了详细的描述和示例。这些攻击类将该列表与其他分类方案区分开来。这些类简单而直观。但是，此列表定义了攻击类，而不是导致这些攻击的常见编码错误的类别。Hoglund和McGraw[10]给出了一个类似的，但更全面的攻击模式列表。基于攻击的方法是基于了解你的敌人并评估类似攻击的可能性。它们代表了软件安全等式中的黑帽一方。编码错误的分类本质上是积极的。这类东西对软件安全领域的白帽一方最有用。最后，这两种方法都是有效和必要的。

Aslam[2]提出的分类方案是本文讨论的唯一精确方案。在这个方案中，每个漏洞只属于一个类别。对错误进行分类的决策过程由针对每个漏洞类别的一组问题组成。Aslam的系统是定义良好的，并且提供了一种通过相似性来识别缺陷的简单方法。Aslam分类法的另一个贡献是，它利用软件故障研究来开发它的分类。然而，它只关注UNIX操作系统中的实现问题，并且提供的类别对于我们的目的来说仍然过于宽泛。

我们所知道的最新分类方案是PLOVER(研究人员漏洞示例初步列表)[6]，它是创建WIFF(弱点，特性，错误，缺陷)的正式枚举的起点，称为CWE(常见WIFF枚举)[13]。包含近300个wiff的28个主要类别将christy和Martin的分类方案置于模糊范围的另一端——漏洞类别比上面讨论的任何分类法都要具体得多。他们自下而上的方法对我们的努力是有益的。PLOVER和CWE是christy早期将CVE
(Common Vulnerabilities and
Exposures)[7]命名为公开已知漏洞的工作的扩展。将理论攻击与实践中已知的漏洞进行类比的尝试是一项重要贡献，也是较大多数早期方案向前迈出的一大步。

## 理由

很明显，大多数现有的分类方案都是从对安全缺陷进行分类的理论和综合方法开始的。迄今为止，大多数研究都集中在使方案具有确定性和准确性，力求在漏洞和漏洞所属类别之间实现一对一的映射。同一目标的另一个方面是使不同抽象级别的分类保持一致：无论从设计还是实现的角度考虑，都应该将相同的漏洞分类到相同的类别中。

大多数提出的方案侧重于对操作系统的相关安全缺陷进行分类，而不是对软件安全中的错误进行分类。此外，许多现有分类法的类别应该是广泛和严格定义的，而不是直观和特定的。总的来说，大多数方案的安全规则都是不容易应用于组织中，且不利于想要学习如何构建安全软件的软件开发人员使用。

为了进一步培训软件开发人员关于常见错误的目标，我们放弃了理论完整性所必需的广度和复杂性，转而支持以开发人员可接近且有意义的编程概念为中心的实用语言。

在我们继续之前，我们需要定义一下从生物学中借用的术语，我们将在接下来的文章中使用这些术语来讨论我们的分类方案。

定义1：门是指一种特定类型的编码错误。例如，“非法指针值”是一个门。

定义2：界是指拥有共同主题的门的集合。例如，”输入验证和表示“是一个界。

在定义我们的分类法时，我们重视具体和具体的问题，这些问题是软件安全的真正关注点，而不是抽象和理论的问题，这些问题要么在实践中没有看到，要么是高层不安全规范决策的结果。我们并没有把创建一个理论上完整的分类方案作为目标。相反，我们提供了一个开放式的方案，可以适应未来的扩展。我们预计重要门的名单会随着时间的推移而改变。我们预计重要的王国也会发生变化，尽管速度会慢一些。任何进化都将受到语言、框架和库趋势的影响;发现新的攻击类型;软件正在应用的新问题和垂直领域;监管环境和社会规范。

我们重视简单性而不是并行性，以便创建对于非安全专家的软件开发人员来说直观的王国。与第2节中讨论的大多数分类方案相反，我们的分类法侧重于在一系列软件应用程序中出现的代码级安全问题，而不是最适用于特定类型的软件(如操作系统)的错误。例如，缓冲区溢出和命令注入[8]是我们分类法的一部分，而对SSH的击键和定时攻击的分析[18]以及其他类型的隐蔽通道类型的攻击则不包括在内。没有理由相信我们所选择的领域不适用于操作系统或其他类型的专用软件，然而，从事商业应用程序和桌面程序的开发人员比从事操作系统的开发人员多得多。

为了更好地理解我们的分类法提供的分类之间的关系，请考虑最近在Adobe Reader 5.0中发现的一个漏洞。x for
Unix[9]。该漏洞存在于函数UnixAppOpenFilePerform()中，该函数通过调用sprintf()将用户提供的数据复制到固定大小的堆栈缓冲区中。如果用户提供的数据的大小大于将其复制到的缓冲区的大小，则包括堆栈指针在内的重要信息将被覆盖。通过提供恶意PDF文档，攻击者可以在目标系统上执行任意命令。这种攻击是可能的，因为一个简单的编码错误——没有检查确保用户提供的数据的大小不大于目标缓冲区的大小。根据我们的经验，开发人员会将此检查与围绕sprintf()调用的防御性代码的失败联系起来。我们根据它所引发的攻击对这种编码错误进行分类——缓冲区溢出。我们选择输入验证和表示作为缓冲区溢出门所属领域的名称，因为缺乏适当的输入验证是攻击可能发生的原因。

我们门所代表的编码错误都可以通过静态源代码分析工具检测出来。源代码分析为开发人员提供了一个获得关于他们所编写的代码的快速反馈的机会。我们看到了通过让开发人员使用源代码分析工具来教育他们了解编码错误的巨大潜力。

  

## 分类法

  

* * *

我们现在提供一个分类法的摘要，它也将出现在McGraw的新书[14]中。我们将这一门划分为“7 +
1”的高级界，这对大多数开发者来说都是有意义的。其中7个界致力于解决源代码中的错误，一个界与配置和环境问题有关。我们将它们按对软件安全的重要性排序:

  1. 输入验证和表示

  2. API滥用

  3. 安全特性

  4. 时间和状态

  5. 错误

  6. 代码质量

  7. 封装

  8. *.环境

下面提供了界和门的简要描述。完整的描述和源代码示例可在互联网上获得<http://vulncat.fortifysoftware.com>。

我们的分类法包括在各种编程语言中出现的编码错误。其中最重要的是C和c++， Java以及
.net家族，包括c#和ASP。我们的一些分类是特定于语言的，因为它们所代表的错误类型只适用于特定的语言。一个例子是双自由门。它识别低级内存例程的不正确使用。这个分类是特定于C和c++的，因为Java和.net语言的托管部分都没有公开低级内存api。

除了特定于语言之外，我们的一些门还是特定于框架的。例如，Struts类只适用于Struts框架，J2EE类只适用于J2EE应用程序的上下文中。另一方面，原木锻造是一个更普遍的门。

我们的门列表当然是不完整的，但它可以适应随着时间的推移而发生的趋势变化和新缺陷的发现。我们关注于发现和分类与安全相关的缺陷，而不是更一般的质量或可靠性问题。代码质量界可能包含更多的领域，但是我们认为我们目前包含的是最有可能影响软件安全性的领域。最后，我们将重点放在对现实世界的企业开发人员最重要的错误分类上——我们从文献、我们的同事和我们的客户那里获得这些信息。

  1.  **输入验证和表示（Input Validation and Representation）**

输入验证和表示问题是由元字符、替代编码和数字表示引起的。信任输入会导致安全问题。这些问题包括:缓冲区溢出、跨站脚本攻击、SQL注入等。

  * 缓冲溢出（Buffer Overflow）：在已分配内存的边界之外写入可能会损坏数据、使程序崩溃或导致有效攻击载荷的执行。

  * 命令注入（Command Injection）：从不受信任的源或在不受信任的环境中执行命令可能导致应用程序代表攻击者执行恶意命令。

  * 跨站脚本（Cross-Site Scripting）：向Web浏览器发送未经验证的数据可能导致浏览器执行恶意代码(通常是脚本)。

  * 格式字符串（Format String）：允许攻击者控制函数的格式字符串可能会导致缓冲区溢出。

  * HTTP响应分割（HTTP Response Splitting）：将未经验证的数据写入HTTP报头，允许攻击者指定浏览器呈现的整个HTTP响应。

  * 非法指针值（Illegal Pointer Value）：这个函数可以返回一个指针，指向要搜索的缓冲区之外的内存。对指针的后续操作可能会产生意想不到的后果。

  * 整数溢出（Integer Overflow）：不考虑整数溢出可能导致逻辑错误或缓冲区溢出。

  * 日志伪造（Log Forging）：将未经验证的用户输入写入日志文件可以会导致攻击者伪造的日志条目向日志中注入恶意内容。

  * 路径操作（Path Manipulation）：允许用户输入控制应用程序使用的路径可能使攻击者能够访问其他受保护的文件。

  * 程序控制（Process Control）：从不受信任的源或在不受信任的环境中执行命令或加载库可能导致应用程序代表攻击者执行恶意命令(和有效负载)。

  * 资源注入（ Resource Injection）：允许用户输入控制资源标识符可能使攻击者能够访问或修改其他受保护的系统资源。

  * 设置操作（Setting Manipulation）：允许外部控制系统设置可能会中断服务或导致应用程序以意想不到的方式运行。

  * SQL注入（SQL Injection）：使用用户输入构造动态SQL语句可能允许攻击者修改语句的含义或执行任意SQL命令。

  * 字符串终止错误（String Termination Error）：依赖正确的字符串终止可能导致缓冲区溢出。

  * Struts重复验证表单（Struts: Duplicate Validation Forms）：多个具有相同名称的验证表单表明验证逻辑不是最新的。

  * Struts错误的validate()方法（Struts: Erroneous validate() Method）：验证器表单定义了validate()方法，但无法调用super.validate()。

  * Struts表单Bean不扩展验证类（Struts: Form Bean Does Not Extend Validation Class）：所有的Struts表单都应该扩展一个Validator类。

  * Struts没有验证器的表单字段（Struts: Form Field Without Validator）：表单中的每个字段都应该在相应的验证表单中进行验证。

  * Struts未使用的插件框架（Struts: Plug-in Framework Not In Use）：使用Struts验证器来防止未经检查的输入导致的漏洞。

  * Struts未使用的验证表单（Struts: Unused Validation Form）：未使用的验证表单表明验证逻辑不是最新的。

  * Struts未验证的动作表单（Struts: Unvalidated Action Form）：每个Action Form都必须有一个相应的验证表单。

  * Struts验证器已关闭（Struts: Validator Turned Off）：这个Action Form映射禁用表单的validate()方法。

  * Struts（Struts: Validator Without Form Field）：没有表单字段的验证器。如果验证字段没有出现在与其关联的表单中，则表明验证逻辑已经过时。

  * 不安全的JNI（Unsafe JNI）：Java本机接口(Java Native Interface, JNI)的不当使用会使Java应用程序容易受到其他语言中的安全漏洞的攻击。

  * 不安全反射（Unsafe Reflection）：攻击者可以通过应用程序创建意想不到的控制流路径，从而潜在地绕过安全检查。

  * XML验证（XML Validation）：如果在解析XML时没有启用验证，攻击者就有机会提供恶意输入。

  2.  **API滥用（API Abuse）**

API是调用者和被调用者之间的契约。最常见的API滥用形式是由于调用方未能履行该契约的终止。例如，如果程序在调用chroot()后未能调用chdir()，则违反了指定如何以安全方式更改活动根目录的契约。库滥用的另一个好例子是期望被调用方向调用方返回可信的DNS信息。在这种情况下，调用方通过对被调用方API的行为做出某些假设(即返回值可用于身份验证目的)来滥用被调用方API。一方也可以从另一方违反调用方-被调用方契约。例如，如果编码器继承了SecureRandom并返回了一个非随机值，则违反了契约。

  * 危险功能（Dangerous Function）：不能安全使用的函数永远不要使用。

  * 目录限制（Directory Restriction）：不正确地使用chroot()系统调用可能会让攻击者逃脱chroot约束。

  * 堆检查（Heap Inspection）：不要使用realloc()来调整存储敏感信息的缓冲区大小。

  * J2EE不良实践:getConnection()（J2EE Bad Practices: getConnection()）：J2EE标准禁止直接管理连接。

  * J2EE不良实践:套接字（J2EE Bad Practices: Sockets）：在web应用程序中基于套接字的通信很容易出错。

  * 常被误用:Authentication（Often Misused: Authentication）：不要依赖getlogin()函数族返回的名称，因为它很容易被欺骗。

  * 常被误用:异常处理（Often Misused: Exception Handling）：危险的函数可能抛出异常，可能导致程序崩溃。

  * 常被误用:文件系统（Often Misused: File System）：将大小不足的输出缓冲区传递给路径操作函数可能导致缓冲区溢出。

  * 经常被误用:特权管理（Often Misused: Privilege Management）：不遵守最小特权原则会放大其他漏洞带来的风险。

  * 经常被误用:字符串（Often Misused）：操作字符串的函数会导致缓冲区溢出。

  * 未检查返回值（Unchecked Return Value）：忽略方法的返回值可能会导致程序忽略意外的状态和条件。

  3.  **安全特征（Security Features）**

软件安全不是安全软件。这里我们关注的主题包括身份验证、访问控制、机密性、密码学和特权管理。

  * 不安全随机性（Insecure Randomness）：标准伪随机数生成器无法抵御加密攻击。

  * 最少特权违反（Least Privilege Violation）：执行chroot()等操作所需的特权级别应该在操作完成后立即删除执行。

  * 缺少访问控制（Missing Access Control）：程序没有在所有可能的执行路径上以一致的方式执行访问控制检查。

  * 密码管理（Password Management）：以明文形式存储密码可能会导致系统泄露。

  * 密码管理:配置文件中的空密码（Password Management: Empty Password in Config File）：使用空字符串作为密码是不安全的。

  * 密码管理:硬编码密码（Password Management: Hard-Coded Password）：硬编码密码可能以一种不容易补救的方式危及系统安全。

  * 密码管理:配置文件中的密码（Password Management: Password in Config File）：将密码保存在配置文件中可能会导致系统安全。

  * 密码管理:弱密码（Password Management: Weak Cryptography）：用简单的编码模糊密码并不能保护密码。

  * 侵犯隐私（Privacy Violation）：错误地处理私人信息，如客户密码或社会安全号码，可能会损害用户隐私，并且通常是非法的。

  4.  **时间和状态（Time and State）**

分布式计算是关于时间和状态的。也就是说，为了让多个组件进行通信，必须共享状态，而这一切都需要时间。大多数程序员把他们的工作拟人化。他们认为一个控制线程执行整个程序的方式与他们必须自己完成这项工作的方式相同。然而，现代计算机在任务之间切换得非常快，在多核、多cpu或分布式系统中，两个事件可能会在完全相同的时间发生。缺陷急于填补程序员关于程序如何执行的模型与实际发生的情况之间的空白。这些缺陷与线程、进程、时间和信息之间的意外交互有关。这些交互通过共享状态发生:信号量、变量、文件系统，以及基本上可以存储信息的任何东西。

  * 死锁（Deadlock）：不一致的锁定规则可能导致死锁。

  * 认证后启动新会话失败（Failure to Begin a New Session upon Authentication）：跨身份验证边界使用相同的会话标识符允许攻击者劫持经过身份验证的会话。

  * 文件访问竞争条件:TOCTOU（File Access Race Condition: TOCTOU）：从检查文件属性到使用文件之间的时间窗口可以被利用来发起特权升级攻击。

  * 临时文件不安全（Insecure Temporary File）：创建和使用不安全的临时文件会使应用程序和系统数据容易受到攻击。

  * J2EE不良实践:System.exit()（J2EE Bad Practices: System.exit()）：Web应用程序不应该试图关闭其容器。

  * J2EE不良实践:线程（J2EE Bad Practices: Threads）：在某些情况下，Web应用程序中的线程管理是被禁止的，并且总是非常容易出错。

  * 信号处理竞争条件（Signal Handling Race Conditions）：信号处理程序可能会更改其他信号处理程序或应用程序代码所依赖的共享状态，从而导致意外行为。

  5.  **错误（Errors）**

错误和错误处理代表了一类API。与错误处理相关的错误非常常见，因此它们应该有自己的特殊领域。与API滥用一样，引入与错误相关的安全漏洞有两种方式:最常见的一种是错误处理不当(或根本不处理)。第二种是产生错误，这些错误要么提供了太多信息(给可能的攻击者)，要么难以处理。

  * 捕获NullPointerException（Catch NullPointerException）：捕获NullPointerException不应该被用作防止解引用空指针的编程检查的替代方法。

  * 空Catch块（Empty Catch Block）：忽略异常和其他错误条件可能允许攻击者引起不被注意的意外行为。

  * 宽泛catch块（Overly-Broad Catch Block）：捕获过于宽泛的异常会导致更有可能包含安全漏洞的复杂错误处理代码。

  * 宽泛抛出声明（Overly-Broad Throws Declaration）：抛出过于宽泛的异常会导致更有可能包含安全漏洞的复杂错误处理代码。

  6.  **代码质量（Code Quality）**

糟糕的代码质量会导致不可预测的行为。从用户的角度来看，这通常表现为糟糕的可用性。对于攻击者来说，它提供了以意想不到的方式对系统施加压力的机会。

  * 重复释放（Double Free）：在同一内存地址上两次调用free()可能导致缓冲区溢出。

  * 不一致的实现（Inconsistent Implementations）：跨操作系统和操作系统版本实现不一致的函数会导致可移植性问题。

  * 内存泄漏（Memory Leak）：内存被分配，但从未释放，导致资源耗尽。

  * Null引用（Null Dereference）：程序可能解引用空指针，从而引发NullPointerException。

  * 过时函数（Obsolete）。使用弃用或过时的函数可能表示被忽略的代码。

  * 未定义行为（Undefined Behavior）：此函数的行为是未定义的，除非将其控制参数设置为特定值。

  * 未初始化的变量（Uninitialized Variable）：程序可能会在变量初始化之前使用它

  * 未释放的资源（Unreleased Resource）：程序可能无法释放系统资源。

  * 释放后使用（Use After Free）：在内存被释放后引用它可能导致程序崩溃。

  7.  **封装（Encapsulation）**

封装是关于绘制强大的边界。在web浏览器中，这可能意味着确保您的移动代码不会被其他移动代码滥用。在服务器上，这可能意味着区分已验证的数据和未验证的数据，区分一个用户的数据和另一个用户的数据，或者区分允许用户查看的数据和不允许用户查看的数据。

  * 按名称比较类（Comparing Classes by Name）：按名称比较类可能导致程序将两个实际上不同的类视为相同的类。

  * 用户之间的数据泄漏（Data Leaking Between Users）：数据可以通过单例对象(如servlet)的成员变量和共享池中的对象从一个会话“流出”到另一个会话。

  * 残留的调试代码（Leftover Debug Code）：调试代码可能会在应用程序中创建意想不到的入口点。

  *  **移动代码:** 对象劫持（ **Mobile Code:** Object Hijack）：攻击者可以使用可克隆对象来创建对象的新实例，而无需调用其构造函数。

  *  **移动代码:** 使用内部类（ **Mobile Code:** Use of Inner Class）：内部类被转换成在包范围内可访问的类，并且可能会向攻击者公开程序员想要保持私有的代码。

  *  **移动代码:** 非最终公共字段（ **Mobile Code** : Non-Final Public Field）：非final公共变量可以被攻击者操纵以注入恶意值。

  * 公共方法返回的私有数组类型字段（ Private Array-Typed Field Returned From a Public Method）：私有数组的内容可能会通过从公共方法返回的引用意外地改变。

  * 公共数据分配给私有数组类型字段（Public Data Assigned to Private Array-Typed Field）：将公共数据赋值给私有数组相当于赋予对该数组的公共访问权。

  * 系统信息泄露（System Information Leak）：泄露系统数据或调试信息有助于攻击者了解系统并制定攻击计划。

  * 信任边界违背（Trust Boundary Violation）：在同一数据结构中混合可信数据和不可信数据会导致程序员错误地信任未经验证的数据。

  8.  **环境（*. Environment）**

本节包括源代码之外的所有内容，但对于正在创建的产品的安全性仍然至关重要。因为这个界所涉及的问题与源代码没有直接关系，所以我们将其与其他界分开。

  * ASP.NET错误配置:创建调试二进制文件（ASP .NET Misconfiguration: Creating Debug Binary）：调试消息有助于攻击者了解系统并计划攻击形式。

  * ASP.NET错误配置:缺少自定义错误处理（ASP .NET Misconfiguration: Missing Custom Error Handling）：asp.net应用程序必须启用自定义错误页面，以防止攻击者从框架的内置响应中挖掘信息。

  * ASP.NET配置错误:配置文件中的密码（ASP .NET Misconfiguration: Password in Configuration File）：不要将密码硬连接到你的软件中。

  * 不安全的编译器优化（Insecure Compiler Optimization）：不正确地从内存中清除敏感数据可能会危及安全性。

  * J2EE错误配置:不安全的传输（J2EE Misconfiguration: Insecure Transport）：应用程序配置应确保SSL用于所有访问控制页面。

  * J2EE配置错误:会话id长度不足（J2EE Misconfiguration: Insufficient Session-ID Length）：会话标识符应该至少有128位长，以防止暴力破解会话。

  * J2EE错误配置:缺少错误处理（J2EE Misconfiguration: Missing Error Handling）：Web应用程序必须为404错误和500错误定义默认错误页面，并捕获java.lang.Throwable异常，以防止攻击者从应用程序容器内置错误响应中挖掘信息。

  * J2EE错误配置:不安全Bean声明（ J2EE Misconfiguration: Unsafe Bean Declaration）：实体bean不应该被声明为远程的。

  * J2EE错误配置:弱访问权限（J2EE Misconfiguration: Weak Access Permissions）：调用EJB方法的权限不应该授予ANYONE角色。

  

## SEVEN PLUS OR MINUS TWO

  

* * *

最近开发并提供了其他几个软件安全问题列表。第一种是《软件安全的19宗罪》[11]。第二个是Web上可用的OWASP十大最关键Web应用程序安全漏洞[17]。两者都有一个不幸的共同点——过于复杂。人们擅长记录7件事(正负2件)[16]。我们将此作为硬性约束，并试图将分类法中的王国数量减少到7个(加1个)。

通过讨论这些列表与我们提出的方案，我们说明并强调了我们分类法的优越性。这两个列表的主要限制是它们混合了特定类型的错误和漏洞类，并在同一抽象级别上讨论它们。十九个致命错误包括缓冲区溢出和未能保护网络流量类别，处于同一级别，尽管第一个是非常具体的编码错误，而第二个可能是由各种错误组成的一类。OWASP的十大漏洞还包括跨站脚本(XSS)漏洞和不安全的配置管理。

我们的分类方案包括两个层次:界和门。王国代表了错误的类别，而组成王国的门代表了特定的错误。我们想指出的是，尽管我们的分类方案的结构与上面描述的列表的结构不同，但组成这些列表的类别可以很容易地映射到我们的王国。以下是十九宗罪的映射:

  1. Input Validation and Representation Buffer Overflows Command Injection Cross-Site Scripting Format String Problems Integer Range Errors SQL Injection

  2. API Abuse Trusting Network Address Information

  3. Security Features Failing to Protect Network Traffic Failing to Store and Protect Data Failing to Use Cryptographically Strong Random Numbers Improper File Access Improper Use of SSL Use of Weak Password-Based Systems Unauthenticated Key Exchange

  4. Time and State Signal Race Conditions Use of “Magic” URLs and Hidden Forms

  5. Errors Failure to Handle Errors

  6. Code Quality Poor Usability

  7. Encapsulation Information Leakage

  8. *. Environment

  

Here is the mapping for the OWASP Top Ten:

  1. Input Validation and Representation Buffer Overflows Cross-Site Scripting (XSS) Flaws Injection Flaws Unvalidated Input

  2. API Abuse

  3. Security Features Broken Access Control Insecure Storage

  4. Time and State Broken Authentication and Session Management

  5. Errors Improper Error Handling

  6. Code Quality Denial of Service

  7. Encapsulation *. Environment

Insecure Configuration Management

## 结论

我们对影响安全性的常见编码错误进行了简单、直观的分类。我们讨论了我们定义的漏洞门与相应攻击之间的关系，并提供了所提出的分类中每个王国的描述

我们指出了我们提出的方案与相关工作中讨论的方案之间的重要区别。我们提出的分类方案旨在组织安全规则，因此对关心编写安全代码和能够自动检测安全缺陷的软件开发人员有帮助。这些目标使我们的方案简单，对开发人员来说是直观的，是实用的而不是理论的和全面的，可以用静态分析工具自动识别错误，并且可以适应随着时间的推移可能发生的趋势变化。

## 关于Fortify软件

强化软件产品保护公司免受当今最大的安全风险:运行其业务的软件应用程序。

Fortify software将深厚的应用程序安全专业知识与丰富的软件开发经验相结合，以跨越软件开发周期的获奖产品定义了市场。今天，Fortify
Software为最苛刻的客户部署(包括世界上最大、最多样化的代码库)加强了软件。

Fortify
Software是政府机构和财富500强公司在各种行业(如能源、金融服务、医疗保健、电子商务、媒体、电信、出版、保险、系统集成和信息管理)中选择的软件安全供应商。

了解更多信息 有关Fortify软件产品的信息，以及免费的安全评估以提供帮助 如果您确定您面临的安全风险，请访问我们的网站或立即与我们联系

web站点：[www.fortifysoftware.com](www.fortifysoftware.com)

## 引用

[1] R.P. Abbott, J. S. Chin, J.E. Donnelley, W.L. Konigsford, S. Tokubo, and
D.A. Webb. Security Analysis and Enhancements of Computer Operating Systems.
NBSIR 76-1041, National Bureau of Standards, ICST, Washington, D.C., 1976.

[2] T. Aslam. A Taxonomy of Security Faults in the Unix Operating System.
Master’s Thesis, Purdue University, 1995.

[3] R. Bisbey and D. Hollingworth. Protection Analysis Project Final Report.
ISI/RR-78-13, DTIC AD A056816, USC/Information Sciences Institute, 1978.

[4] M. Bishop. Computer Security: Art and Science. Addison-Wesley, December
2002.

[5] W. Cheswick, S. Bellovin, and A. Rubin. Firewalls and Internet Security:
Repelling the Wily Hacker, Second Edition. Addison-Wesley, 2003.

[6] S. Christey. PLOVER—Preliminary List of Vulnerability Examples for
Researchers. Draft, August 2005. <http://cve.mitre.org/docs/plover/>.

[7] CVE – Common Vulnerabilities and Exposures. <http://www.cve.mitre.org/>.

[8] Fortify Descriptions. <http://vulncat.fortifysoftware.com>.

[9] Fortify Extra. Adobe Reader for Unix Remote Buffer Overflow.
<http://extra.fortifysoftware.com/archives/2005/07/adobe_reader_fo_1.html>.

[10] G. Hoglund and G. McGraw. Exploiting Software: How to Break Code.
AddisonWesley, February 2004.

[11] M. Howard, D. LeBlanc, and J. Viega. 19 Deadly Sins of Software Security.
McGrawHill Osborne Media, July 2005.

[12] C. E. Landwehr, A. R. Bull, J. P. McDermott, W. S. Choi. A Taxonomy of
Computer Program Security Flaws, with Examples. ACM Computing Surveys, Vol.
26, No. 3, September 1994, pp. 211-254.

