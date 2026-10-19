一组来自俄亥俄州立大学的研究人员发现一个Spectre攻击的新变种，该新变种命名为SgxPectre。

 **Intel Software GuardExtensions** （SGX）是一种针对应用程序开发人员技术，该技术能够保护选定的代码不被修改。SGX
enclave是执行内存中的保护区，英特尔的SGX允许应用程序在英特尔SGX enclave内执行。

我们长期以来一直在讨论英特尔处理器中的Spectre和Meltdown漏洞以及利用它们的方法。

Meltdown攻击能够允许攻击者阅读目标机器的物理记忆窃取凭证，个人信息和其他信息。

Spectre攻击允许用户模式应用程序从同一系统上的其他进程中提取数据。它也可以从自有进程代码中提取信息，举个例子，一个恶意JavaScript能够用于从浏览器内存中提取其它网站的登录COOKIE。

Spectre攻击打破了不同应用之间的隔离，它可以把内核中的信息泄露到用户应用，也能把虚拟化管理程序中的信息泄露到客户系统。

虽然Meltdown或者Spectre不允许攻击者从SGX硬件隔离环境中提取数据，SgxPectre攻击暴露了英特尔CPU中的BUG暴露了SGXEnclave。

这些研究员在发表的论文中表述：“SGXPECTRE攻击利用最近发现的CPU bug颠覆了SGX
enclave的机密性。特别是，我们表明硬件隔离代码的分支预测可以被硬件隔离环境外部的程序影响，硬件隔离程序控制流可以临时更改以执行可以观测到明显的魂村状态改变的指令。”

“对方通过观察这些变化，能够学习enclave内存中的秘密或者它的内存寄存器，从而彻底击败SGX提供的机密性保障。”

根据专家的看法，几乎所有的enclave程序在SGXPECTRE攻击面前都是脆弱的。

![Intel-SGX-enclave.jpg](https://image.3001.net/images/20180306/15203349023010.jpg!small)  

SgxPectre攻击利用软件库中特定的代码模型，允许开发者在他们的应用中添加SGX支持。所需的代码模式在SGX运行的大多数时间是可用的，包括英特尔SGX
SDK，Rust—SGX，Graphene-SGX。

基本上，SgxPectre是一个针对enclave程序的高速缓存侧信道攻击。

研究人员解释说他们的攻击是基于观测重复的代码执行模式，软件发展装备介绍SGX硬件隔离以及相关缓存大小设置。

论文中的后续内容表明：“尤其是，因为脆弱代码模式存在于大部分SGX运行库中，而且很难排除，对手能够采取针对enclave程序的SGXPECTRE攻击。”

“我们通过演示端到端攻击，证明对方能够获取enclave内存中的内容，以及在这种攻击中的寄存器值。”

随着英特尔在3月16日发布了SGX SDK安全更新，英特尔计划专注于SgxPectre。

开发人员需要用新的SDK版本更新他们的应用程序。

专家们发布了一个针对这个攻击的PoC视频，而Poc代码发布在GitHub上。

  

*参考来源：[security affairs](http://securityaffairs.co/wordpress/69853/hacking/sgxpectre-sgx-enclave.html)，丁牛网安实验室小编eva编辑，如需转载请标明出处

