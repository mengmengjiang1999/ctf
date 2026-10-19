***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 ****

![Spectre-variations.png](https://image.3001.net/images/20180712/15313846961272.png!small)

 **Meltdown熔断、Spectre幽灵两大安全漏洞被发现之后，Intel处理器身上的漏洞开始源源不断地出现，尤其以“幽灵”漏洞变种居多。**

近日，两位安全研究人员又披露了两个新的“幽灵级”（Specter-class）安全漏洞，并将这些漏洞命名为“Spectre 1.1”和“Spectre
1.2”。

像之前发现的所有“熔断”（Meltdown）和“幽灵”（Specter）CPU漏洞变种一样，最新发现的两个漏洞也利用了CPU中的推测执行（speculative
execution）进程——这是在所有现代CPU中发现的一种功能，它通过提前计算操作，并稍后丢弃不需要的数据来提高性能。

## Spectre 1.1和Spectre 1.2简要介绍

根据研究人员的说法，Spectre 1.1攻击利用了预测缓冲区溢出，使得本地攻击者可以在脆弱的系统上执行任意不受信任的代码。通过边际信道分析（side-channel analysis）和投机缓冲区溢出（speculative buffer
overflow），它可利用微处理器的投机性执行和分支预测来暴露敏感信息。

据悉，Spectre 1.1与Spectre V1.和V4.非常相似，但发现该漏洞的两名研究人员表示：

> “目前，还没有有效的静态分析或编译器工具可用于检测或缓解Spectre 1.1漏洞影响。”

更可怕的是，除了Spectre 1.1之外，研究人员还指出了所谓的“Spectre 1.2”漏洞。作为幽灵漏洞的另一个新型变体，Spectre
1.2漏洞主要影响那些CPU不执行读/写保护和依赖于懒惰的PTE强制执行的处理器。在一场 Spectre 1.2
攻击中，被允许的投机存储可覆写只读的数据、代码指针、以及代码元数据：其包括 vtables、GOT /
IAT、以及控制流缓解元数据，结果就是依赖于只读存储器的硬件执行沙箱都被无效化了。

与大多数之前发现的Meltdown和Spectre漏洞类似，这两个漏洞都需要在用户的PC上存在恶意代码，这些代码负责运行攻击。这在某种程度上限制了漏洞的严重性，但这一点不能作为系统管理员在补丁可用时不及时应用补丁的借口。

## 漏洞影响Intel和ARM，甚至AMD

英特尔和ARM已经公开承认，其部分CPU容易受到Spectre
1.1漏洞的攻击。而AMD方面暂时没有发布任何声明，不过可以理解，AMD在审查安全问题方面一直动作很慢。由于所有Spectre攻击都会影响AMD
CPU，因此可以大胆地假设，这些新攻击也会影响AMD的产品组合。

目前，研究人员还没有发布有关受Spectre
1.2影响的CPU的信息，而且也没有任何补丁可用于修复这两种漏洞。但英特尔发言人表示，其用于处理Meltdown和Spectre漏洞的指南中包含有关“开发人员应该如何检查和修改其源代码，以减轻应用程序/软件级别漏洞”的信息。

此外，Microsoft、Oracle以及Red Hat也已经表示，他们仍在调查Spectre
1.1是否会影响其产品所处理的数据，并正在研究如何降低软件级别的风险。

在一篇题为《投机缓冲区溢出：攻击和防御》（Speculative Buffer Overflows: Attacks and
Defenses）的研究论文中，发现这些漏洞的两位学者提出了3种基于硬件的缓解措施，来防止Spectre 1.1和Spectre 1.2攻击。

值得一提的是，英特尔方面还向发现该漏洞的研究团队支付了10万美元的漏洞赏金，用于兑现该公司在最初的Meltdown和Spectre漏洞披露后设立的“漏洞悬赏项目”。据悉，这是迄今为止已知的赏金最高的漏洞悬赏项目之一。

如果您已经忘记了所有最近的Meltdown和Spectre相关的CPU漏洞，我们还将所有信息总结在了下表之中，以帮助您跟踪所有变化：

![微信截图_20180712153623.png](https://image.3001.net/images/20180712/15313847183697.png!small)

***参考来源：[bleepingcomputer](https://www.bleepingcomputer.com/news/security/new-spectre-11-and-spectre-12-cpu-flaws-disclosed/)，米雪儿编译整理，转载请注明来自 FreeBuf.COM **  

