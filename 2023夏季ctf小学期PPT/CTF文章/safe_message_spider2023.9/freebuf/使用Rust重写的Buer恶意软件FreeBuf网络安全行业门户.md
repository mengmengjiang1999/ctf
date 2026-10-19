近日研究人员发现Buer恶意软件的一个变种伪装成DHL邮寄通知的形式进行分发传播，该恶意软件使用Rust语言进行了重写。

Profpoint的研究人员表示，高效且易用的Rust语言帮助恶意软件顺利逃避检测。一共发现了两种恶意软件，一种是使用C语言编写的，另一种是使用Rust语言编写的，这可以帮助恶意软件在被发现前感染更多的受害者。

Buer是一种Downloader，作为其他恶意软件的“引路人”。根据Proofpoint的研究，
**最近两年的Downloader变得越来越强大，拥有的功能和配置方式也越来越先进** 。

![](https://image.3001.net/images/20210504/1620129179_6091359bc1fe8f65ce8a6.png!small)

Proofpoint在2019年首次发现Buer，最近又发现了以DHL邮寄通知为主题的新变种。

受害者点击了恶意附件（Word/Excel）后就会触发由Rust编写的Buer变种。研究人员将其命名为RustyBuer，根据Proofpoint的研究表明，
**该恶意软件已经在50多个行业中感染了超过200个组织** 。

作为Downloader，研究人员发现后续可能会投放Cobalt
Strike。而有些时候，后续阶段的载荷并不存在。可能是因为恶意软件的开发者正在测试新的变种，以将其租赁给其他的攻击者。

## 多语言恶意软件

使用Rust重写的恶意软件与传统上用C语言来编写恶意软件的习惯并不相同， **尚不清楚为什么攻击者花费如此多的精力来重写**
。研究人员猜测可能是因为Rust的效率更高，而且支持的功能也越来越多了。

Proofpoint的威胁研究与检测高级主管Sherrod
DeGrippo认为，恶意软件的功能修改很常见，但是选择完全用另一种语言重写的非常少见。通常来说，恶意软件都会通过版本迭代增加新的功能或者提升检测逃避的能力，像这种完全切换到新语言是一个新方式。

![](https://image.3001.net/images/20210504/1620129186_609135a294d4085bb070e.png!small)

 **重写还会带来另一个好处就是对逆向工程带来了巨大的挑战，没有Rust开发经验的工程师难以进行分析**
。Proofpoint的研究人员认为将会看到不断更新的Rust版本的Buer。与过去一样，攻击者将会利用能利用的一切资源发展恶意软件。

## Rust的应用

Rust在业界越来越流行，微软在2月份加入了Rust基金会，在微软内部也越来越多地使用Rust语言。2019年，Python软件基金会和Django软件基金会的前董事Alex
Gaynor表示： **C与C++这样的内存不安全语言引入了非常多的安全漏洞，整个行业需要迁移到诸如Rust和Swift等内存安全的语言上来** 。

Buer的运营者一定是在以多种方式发展攻击技术，提高检测逃避能力，提高攻击成功率。Proofpoint表示，使用Rust重写的恶意软件可以让恶意软件逃避那些基于C编写的恶意软件检测特征。

![](https://image.3001.net/images/20210504/1620129194_609135aa19c391f5b1ac5.png!small)

为了与C版本的恶意软件兼容，Rust重写的恶意软件与C&C服务器的通信方式仍然未变。

## 不要点击

攻击者在文档中使用了一些安全公司的图标，以显示该文档是安全的，引诱用户打开。

![](https://image.3001.net/images/20210504/1620129205_609135b5afc9dc90b6b32.png!small)

恶意文档通过LOLBAS的Windows Shell DLL执行，逃避端点安全的检测。

## 参考来源

> [Proofpoint](https://www.proofpoint.com/us/blog/threat-insight/new-variant-> buer-loader-written-rust)
>
> [ThreatPOST](https://threatpost.com/buer-malware-loader-rewritten-> rust/165782/)

