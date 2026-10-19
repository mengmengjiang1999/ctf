![恶意软件分析资源集合](https://image.3001.net/images/20190320/1553049496_5c91a798411f0.jpg!small)

## 前言

**大家都知道，成为一名优秀的恶意软件分析人员，需要具备各种技术以及丰富的知识，仅仅研究恶意软件分析这一个方向肯定是远远不够的。因此，大家可能会在各种恶意软件分析论坛上看到很多貌似跟这个主题或者领域毫不相关的帖子，但我想告诉大家的是，软件领域里的任何一个概念可能都与恶意软件分析有着某种关联。因为恶意软件，也是软件，恶意软件分析，最终都会归结到软件分析之上。**

在这篇文章中，我们将给大家提供有关PE文件格式、ELF格式、通用操作系统工程（大型）、WScript、JavaScript、SQL、PowerShell和Batch等学习资源和参考建议。

为什么呢？很简单！因为一款恶意软件的身上可以包含上面所提到的每一钟组件。这也就意味着，如果想要正确地分析恶意软件，分析人员需要对上述知识有着足够的了解，再配合上大量其他语言和软件框架的相关知识，我们才能在恶意软件分析这条路上越走越远。

### 工具列表

> 1、 [rshipp的GitHub库](https://github.com/rshipp/awesome-malware-> analysis)-作者自己比较喜欢的工具都在这里啦！
>
> 2、 [IDA
> Pro脚本](https://github.com/nihilus?utf8=%E2%9C%93&tab=repositories&q=ida&type=&language=)-可以在代码分析过程中完成一些自动化的工作；
>
> 3、 [IDA Pro插件](https://github.com/onethawt/idaplugins-list)-辅助研究人员进行代码分析；
>
> 4、 [恶意软件分析资源列表](https://www.peerlyst.com/posts/resource-learning-how-to-> reverse-malware-a-guide)-提供更多的恶意软件分析资源；
>
> 5、 [常用工具及使用指南](https://toddcullumresearch.com/2017/07/01/todds-giant-intro-> of-windows-malware-analysis-tools/)-白皮书啦！

### YouTube频道

> 1、[Colin
> Hardy](https://www.youtube.com/channel/UCND1KVdVt8A580SjdaS4cZg)-专业的逆向分析频道
>
> 2、[OALabs](https://www.youtube.com/channel/UC--DwaiMV-> jtO-6EvmKOnqg)-OALabs恶意软件分析实验室，提供了多种恶意软件分析视频
>
>
> 3、[MalwareAnalysisForHedgehogs](https://www.youtube.com/channel/UCVFXrUwuWxNlm6UNZtBLJ-A)-提供了多种恶意软件分析视频
>
> 4、[L!NK](https://www.youtube.com/channel/UCv6i6WVf-> KeUeXFmp9oy29w)-L!NK的Youtube门户频道
>
>
> 5、[Hasherezade](https://www.youtube.com/channel/UCNWVswPNgn5kutPNa5sprkg)-提供了大量逆向分析视频教程
>
> 6、[Fabian
> Wosar](https://www.youtube.com/watch?v=vFV2GxBZ7D0&t=963s)-可学习恶意软件分析的基本步骤
>
>
> 7、[BinaryAdventure](https://www.youtube.com/channel/UCSLlgiYtOXZnYPba_W4bHqQ)-各种代码分析实践样例；
>
> 8、[Bill Buchanan](https://www.youtube.com/user/billatnapier)-恶意软件分析实践频道
>
>
> 9、[Sysinternals的一个视频](https://www.youtube.com/watch?v=Wuy_Pm3KaV8)-相信我，你不看绝对亏大了！

### 博客网站

注：如果你想以最快的速度了解更多的东西，技术博客绝对是你的首选。

> 1、[Malwarebytes](https://blog.malwarebytes.com/)-大厂家，各种技术信息一网打尽；
>
>
> 2、[Cylance](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=1&cad=rja&uact=8&ved=0ahUKEwiCnrCLy4DVAhUC8WMKHf-> pBEAQFggoMAA&url=https%3A%2F%2Fblog.cylance.com%2F&usg=AFQjCNENX5VZUqyrUD9mlK31e4QLGYl9_g)-基于人工智能的威胁分析平台；
>
> 3、[FireEye](https://www.fireeye.com/blog.html)-火眼，不用过多介绍了吧？
>
> 4、[Securelist](https://securelist.com/all/?category=24)-卡巴斯基旗下的威胁情报分析与报告平台；
>
> 5、[Endgame](https://www.endgame.com/blog/technical-blog)-针对企业的终端保护平台；
>
> 6、[Virus Bulletin](https://www.virusbulletin.com/blog/)-杀毒测评机构；
>
> 7、[PCP TechTalk](https://techtalk.pcpitstop.com/malware-research-> team/)-提供了多种信息安全技术议题；
>
> 8、[Malware Unicorn](http://amanda.secured.org/)-提供了大量恶意软件逆向资源；
>
> 9、[Hasherezade](https://hshrzd.wordpress.com/)-提供了大量恶意软件分析教程；
>
> 10、[MalwareTech](https://www.malwaretech.com/tag/malware)-恶意软件分析博客集中地；
>
>
> 11、[Forcepoint](https://blogs.forcepoint.com/tags/malware)-基于人与数据交互方式来提供安全保护的平台；
>
> 12、[G
> DATA](https://www.gdatasoftware.com/blog)-30年德国老品牌歌德塔杀毒软件为您的家庭或企业提供了病毒防护、垃圾邮件、防火墙、防木马等其他威胁的全面保护。
>
> 13、[RedNaga](https://rednaga.io/)-针对Android的恶意软件分析资源库；
>
> 14、[Lasha Khasaia](https://secrary.com/ReversingMalware)-提供了大量逆向分析资源；
>
> 15、[ExecuteMalware](http://executemalware.com/)-著名的恶意软件分析网站

### 参考书籍/出版物

> 1、Practical MalwareAnalysis-《恶意软件分析实践》
>
> 2、Practical ReverseEngineering-《逆向工程实践》
>
> 3、AVIEN Malware DefenseGuide for the Enterprise-《AVIEN企业环境下的恶意软件防御指南》
>
> 4、The Art of ComputerVirus Research and Defense-《计算机病毒研究与防御的艺术》
>
> 5、The IDA Pro Book
>
> 6、Malware Analyst’s Cookbook-《恶意软件分析手册》
>
> 7、Hacking: The Art ofExploitation-《黑客：漏洞利用的艺术》
>
> 8、Windows Research Kernel-《研究Windows内核》
>
> 9、Windows Internals Parts1 and 2-《Windows内部分析》
>
> 10、Microsoft PECOFF FormatSpecification -《微软PECOFF格式标准》
>
> 11、Gray Hat Hacking: TheEthical Hacker’s Handbook Third
> Edition-《灰帽黑客：道德黑客手册》第三版

### 分析样本获取

如果你需要一些样本文件来进行分析实践的话，你可以访问以下网站获取：

> 1、<http://malshare.com/>
>
> 2、<http://www.malware-traffic-analysis.net/>
>
> 3、<https://virusshare.com/>
>
> 4、<http://virusign.com/>
>
> 5、<https://github.com/ytisf/theZoo>（可帮助组织搜索和分析特定的恶意软件）
>
> 6、<https://malpedia.caad.fkie.fraunhofer.de/login>

 ***
参考来源：[malwareanalysisforums](https://malwareanalysisforums.com/topic/7/malware-analysis-resources-noobs-read-first)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

