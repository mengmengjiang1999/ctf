## **前言**

经过一番调研，本文筛选了近三年来一直在持续更新的 13 款针对 PHP
的白盒审计工具进行分析。本文主要介绍这些白盒审计框架的原理并简单分析下它们的规则列表，未对具体的挖洞效果进行评估。这主要考虑以下两个原因：一方面，不同白盒审计框架的侧重点是不一致的，有的是为了挖洞设计的，有的实际产出必须经过人工复核；再者，即使都是以挖洞为目标设计的，有的是针对特定的框架，有的又是可以通用的。所以，大家如果感兴趣的话，可以自行选择相应的框架进行测试。

目前，主流的 PHP 开源白盒审计工具在设计思路上大都是依据敏感函数的参数部分/全部来自未经安全函数处理的外部输入
这一经验。最终落实到具体的实现上又可以划分成以下两大类：

 **基于文本特征**
：也就是我们常说的正则方式，基于人工代码审计时发现漏洞点的源代码规律，从而归纳出相应的正则表达式，然后基于此正则表达式来查找此类漏洞。基于文本特征的白盒审计工具优点在于审计速度相对较快，且规则维护起来成本较低，但是缺点又在于准确率相对较低，误报率也比较高。

 **基于静态分析**
：即借助传统静态分析技术来进行白盒审计。常见的技术主要有数据流分析、污点传播和控制流分析等。静态分析的方式能够更加准确的判断外部输入是否经过安全函数的处理，这点是基于文本特征的方式很难实现的。此外，基于静态分析的方式在判断一个变量是否部分/全部来自外部输入的时候也更有优势，尤其在针对框架进行审计的时候。

但是，有好的一面就有坏的一面，基于静态分析的问题在于：

> 1）时间开销大，做一次完整的分析所需的时间远大于基于文本特征的方式；
>
> 2）适配成本高，针对不同的目标，需要适配相应的解析器来生成所需的 AST 树和 CFG 等信息，此外，检测规则的适配也是一个相对较重的成本。

如下图所示，在本文中所介绍的 13 款白盒审计工具安全中，基于文本特征的审计工具有 7 款，基于静态分析的审计工具有 6 款。

![image](https://image.3001.net/images/20210427/1619496545_60878e61df3e5ba4e0aa9.jpg!small)

##  **基于文本特征**

###  **graudit**

    
    
    Github: https://github.com/wireghoul/graudit
    Language: Shell
    Last commit on 2019.11.12
    

graudit 从 09年在 Github 开源到现在为止已经有 10 年左右的历史，并且仍在不断的更新中。graudit 全称是 **g** rep
**r** ough **a** udit，顾名思义其主要是借助 Linux 内建的 grep 命令来实现白盒审计，其核心代码只有一个 200 行不到的
bash 脚本。graudit 支持的语言为 ASP, C, .NET, Java, JavaScript, Perl, PHP, Python,
Ruby等。

graudit 根据漏洞挖掘对象的开发语言选择相应的规则库，然后借助 grep
在源代码中快速定位，来满足指定规则的可疑位置，接下来由安全人员对这些可疑位置进行人工复核，看是否真实存在漏洞。

同时，graudit
经过多年的使用，不断更新，已经提供了十分全面的漏洞规则库（https://github.com/wireghoul/graudit/tree/master/signatures），其提供了
24 个涵盖不同的语言/漏洞类型的数据库，总计 1256 条规则。规则主要为针对危险函数及其参数的检查。值得一提的是，graudit 在 misc
目录里面提供了很多很有用的小脚本。

    
    
    $ ls signatures/*.db|xargs -I {} sh -c 'echo "{}`cat {}|grep -vE \"^$|^#\"|wc -l`"'
    signatures/actionscript.db     10
    signatures/android.db     49
    signatures/asp.db     53
    signatures/c.db     280
    signatures/cobol.db       8
    signatures/default.db     12
    signatures/dotnet.db     134
    signatures/exec.db     17
    signatures/ios.db     39
    signatures/java.db     102
    signatures/js.db       8
    signatures/perl.db     33
    signatures/php.db     160
    signatures/python.db     67
    signatures/rough.db     43
    signatures/ruby.db     16
    signatures/seafruit.db     11
    signatures/secrets-b64.db       1
    signatures/secrets.db       8
    signatures/spsqli.db       4
    signatures/sql.db     74
    signatures/strings.db     64
    signatures/xss.db     13
    

### **VisualCodeGrepper**

    
    
    Github: https://github.com/nccgroup/VCG
    
    Language: Visual Basic .NET
    
    Last commit on 2019.11.06
    

**V** isual **C** ode **G** repper 简称 VCG ，它是基于 VB 开发的一款 window
下的白盒审计工具。相对于其他白盒审计工具，VCG 还会检查代码注释中是否存在诸如 "ToDo", "FixMe", "Kludge"
此类的语句，从而提醒安全人员此处有未完成代码，可能存在安全问题。VCG 支持的语言为 C/C++, Java, C#, VB, PL/SQL, COBOL。

VCG 通过正则表达式检查每一行代码是否满足预先设定的漏洞规则，如若满足则提醒审计人员。不同的是，其规则是动态生成的，即 VCG
提取代码中的变量名等信息来动态生成针对该段代码的漏洞规则。

VCG 的漏洞规则位于 VisualCodeGrepper/modCheck.vb 文件中，每种语言有一个单独的文件，不同语言之间还有一些通用的检测函数。以
PHP 为例，VCG 会检测 10 种不同的漏洞类型。

> CheckSQLInjection：检测 SQL 注入漏洞；
>
> CheckXSS：检测 XSS 漏洞；
>
> CheckLogDisplay：检测写入日志前是否对日志内容进行转义；
>
> CheckRandomisation：检测随机数的生成是否足够安全；
>
> CheckFileValidation：检测是否直接使用 $_FILE 数组的值来进行条件判断；
>
> CheckFileInclusion: 检测文件包含的路径中是否存在用户可控的参数；
>
> CheckExecutable: 检测命令执行函数的参数是否经过转义；
>
> CheckBackTick: 检测反引号的参数是否存在用户可控部分；
>
> CheckRegisterGlobals: 检测全局变量的修改是否用户可控；
>
> CheckParseStr: 检测 parse_str 的参数是否用户可控。

![image](https://image.3001.net/images/20210427/1619504975_6087af4f642caf34bb47b.jpg!small)

###  **kiwi**

    
    
    Github: https://github.com/alpha1e0/kiwi
    
    Language: Python2
    
    Last commit on 2019.08.12
    

kiwi 是一款基于 Python
开发的白盒审计框架。作者在设计之初更多将其定义为一个代码搜索工具，而不是代码审计工具。其主要是为了帮助安全人员更快的定位可能的漏洞点，从而进行下一步的人工审计。Kiwi
的框架本身跟检测规则是完全分离的，安全人员可以根据自己需求编写具体的检测规则。kiwi 理论上可以支持大部分语言，官方提供了 PHP、Python
两种语言的检测规则。

Kiwi 会遍历源码的所有文件，根据文件的后缀选择相应的检测规则，然后通过正则匹配的方式定位可能的漏洞点。在找到漏洞点之后，kiwi
不会直接返回，而是会调用预设的 evaluate 函数进行进一步检测，检测通过后才会报告给安全人员。  
kiwi 官方只提供了 PHP 和 Python 两种语言的检测规则，位于 kiwi_data/features 目录。其中 Python 涵盖 5
种不同的漏洞类型，PHP 涵盖 10 种不同的漏洞类型。

###  **wpBullet**

    
    
    Github: https://github.com/webarx-security/wpbullet
    
    Language: Python3
    
    Last commit on 2019.06.04
    

wpBullet 是一款专为 WordPress 插件/主题设计的白盒审计工具。除了支持对本地源代码的审计之外，wpBullet 还支持根据传入的插件/主题
URL 自动下载源码来审计。

wpBullet 遍历整个源码的所有文件，针对 .php 后缀的文件进行分析。针对每个 PHP 文件，wpBullet 主要进行两个分析：

> 1）wpBullet 通过正则提取 PHP 文件中有关通过 add_action 函数注册的 admin_action
> (admin_action_xxx)、ajax hooks (wp_ajax_xxx) 和 admin 初始化 (admin_init)
> 的信息，并分别存入相应的全局变量以便后续展示给安全人员；
>
> 2）wpBullet 根据预定的检测规则分析该 PHP 文件是否存在漏洞。wpBullet
> 首先通过正则提取该文件中所有用户可控的变量，然后基于这些变量动态生成正则表达式，继而检测这些变量是否未经过检测规则中的安全函数处理而直接传入检测规则中的危险函数。如若是，则生成漏洞报告。

wpBullet 的检测规则位于 Modules 目录中。针对每种漏洞类型，检测规则含有造成此类漏洞的危险函数和针对此类漏洞的安全函数列表。wpBullet
默认提供一个通用的漏洞检测正则规则动态生成函数，但安全人员可以根据自己的实际需求修改该函数。wpBullet 官方提供针对 WordPress 框架的 10
种不同漏洞类型的检测规则。

###  **SourceCodeSniffer**

    
    
    Github: https://github.com/frizb/SourceCodeSniffer
    
    Language: Python2
    
    Last commit on 2018.06.14
    

正如作者所说的，SourceCodeSniffer 是一款乞丐版白盒审计工具，整体实现上相对比较简陋，也差不多2年多没有更新了。

SourceCodeSniffer 通过正则的方式检测源代码中是否存在危险函数，以此来判断是否存在漏洞。并未考虑该危险函数的参数是否为用户可控输入。

SourceCodeSniffer 的检测规则相对较少，但是对于每类安全漏洞都提供了简略的介绍和对应的 CWE 信息。其支持 7 种不同的语言，总计 52
条规则。

    
    
    $ ls *.ini|xargs -I {} sh -c 'echo "{}`cat {}|grep -E \"^Regex\"|wc -l`"' 
    
    ASP.ini    6
    
    C.ini   13
    
    CSharp.ini   17
    
    Custom.ini    1
    
    Default.ini    1
    
    Java.ini    6
    
    NodeJs.ini    3
    
    PHP.ini    5
    
    VBScript.ini    1
    

### **drek**

    
    
    Github: https://github.com/chrisallenlane/drek
    
    Language: JavaScript
    
    Last commit on 2017.06.29
    

drek 是一款基于 JavaScript 开发的白盒审计工具，它的目标是实现类似 grep 的功能，但是其输出格式为 HTML。

drek 会遍历源码的所有文件，然后通过正则检测其中是否存在危险函数，以此来判断该文件是否存在漏洞，并未考虑具体的参数是否可控等此类问题。

与其他工具不同的是，drek 的检测规则额外存放在另外一个 drek-signaturs仓库https://github.com/chrisallenlane/drek-signatures。在针对主流语言（PHP、C、JAVA、JavaScript、.NET）的检测规则之外，drek-signatures
还提供针对不同框架（WordPress、Eloquent ORM）的检测规则。但是检测规则基本只提供了危险函数名，而未进行更多的限定条件，且最近的更新在 3
年前。

###  **GrepBugs**

    
    
    Github: https://github.com/foospidy/GrepBugs
    
    Language: Python2
    
    Last commit on 2017.04.08
    
    

GrepBugs 也是一款基于 Python 开发的比较老的白盒审计框架。类似 graudit，GrepBugs 是对 grep 的 Python
版封装。GrepBugs 除了支持对本地源代码的安全扫描之外，还支持通过 Github API 对 Github 上的仓库源代码进行扫描。

GrepBugs 会遍历源代码，借助 cloc 命令判断文件开发语言，然后根据语言选择相应检测漏洞的正则表达式，最后调用 grep
命令检测文件中是否存在满足正则的语言，从而以此判断该文件是否存在漏洞。

GrepBugs 提供的检测规则（https://grepbugs.com/rules）涵盖 16 种不同的语言，总计 179 条不同的规则。

    
    
    {'ASP': 6,
     'ASP.Net': 10,
     'C': 24,
     'C#': 5,
     'C++': 18,
     'ColdFusion': 12,
     'ERB': 1,
     'HTML': 2,
     'JSP': 12,
     'Java': 15,
     'Javascript': 12,
     'Objective C': 7,
     'PHP': 37,
     'Python': 7,
     'Ruby': 10,
     'Visual Basic': 2}
    

由于篇幅的原因

今天只为大家介绍了基于文本特征的代码审计工具

我们将在下期给大家带来

基于静态分析的代码审计工具介绍

PHP 开源白盒审计工具调研报告（下）

我们不见不散哦~

