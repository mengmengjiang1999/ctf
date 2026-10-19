****

[](https://youtu.be/ug5ZuezbD3c)

****

**相对于Windows系统来说，Mac系统以其安全性而著称。因此，也有许多的Mac用户认为他们并不需要安全什么杀毒软件。但事实真的是如此吗？其实不然，这些年来随着Mac用户的增多，专门针对Mac系统的病毒软件、流氓软件也逐渐的多了起来。不要忘了世界上的第一个计算机病毒Elk
Cloner，就是在一台苹果计算机上被制造的。**

 **
**![infectedapple-900x506.jpg](https://image.3001.net/images/20180311/15207305059186.jpg!small)**  
**

2018年，[Mac恶意软件的现状](https://press.malwarebytes.com/2018/03/08/widespread-customer-acclaim-leads-malwarebytes-extend-endpoint-protection-macs-enterprise/)发生了改变，越来越多的威胁针对这些所谓的高安全性机器。我们已经发现了四个针对Mac的新威胁出现。其中的第一个，OSX.MaMi，是在我们的[论坛上发现](https://forums.malwarebytes.com/topic/218198-dns-hijacked/)的，它会更改受害者机器的DNS设置，并且即使用户发现了也无法将其更改回来。另外，它还会在keychain中安装一个新的受信任的根证书。

这两个举动，对于计算机用户来说是非常危险的。黑客可以通过该操作，将计算机的DNS查找重定向到恶意服务器上，将流量导向合法网站（例如银行网站，亚马逊和Apple的iCloud/Apple
ID服务），并将其引导至恶意钓鱼站点。新增证书可用于执行“中间人”攻击，这些钓鱼网站看起来似乎是合法的。

![MaMi-cert.png](https://image.3001.net/images/20180311/15207305381926.png!small)  

因此我们可以判断该恶意软件的目的是盗取用户的凭据，但具体哪些网站是它的针对目标我们不得而知。

第二个恶意软件是通过Lookout发表的，一份针对国家级恶意软件[Dark
Caracal](https://info.lookout.com/rs/051-ESQ-475/images/Lookout_Dark-Caracal_srr_20180118_us_v.1.0.pdf)的研究报告中发现的。该报告提到了一种新的跨平台RAT（远程访问工具，或后门）CrossRAT，它能够感染Mac以及其他系统。这种以Java编写的恶意软件，为受感染的Mac系统提供了一些基本的远程后门访问。虽然不是很完善，但目前该恶意软件的版本显示为0.1，这很可能表明它仍处于开发的初期阶段。

虽然Mac不再使用预装的Java，但对于这类高度定制化目标明确的恶意软件，我们往往防不胜防。

下一个恶意软件被命名为[OSX.CreativeUpdate](https://blog.malwarebytes.com/threat-analysis/2018/02/new-mac-cryptominer-distributed-via-a-macupdate-hack/)，最初是通过MacUpdate网站的供应链攻击被发现的。黑客通过对MacUpdate网站上的下载链接恶意修改，使其指向由黑客控制的恶意软件URL。一些流行的Mac应用程序（包括Firefox）的下载链接也都被恶意链接所取代。

![OSX.CreativeUpdate-MacUpdate-statement-582x600.png](https://image.3001.net/images/20180311/15207305778915.png!small)  

正如Panic公司在“[源代码盗取案例](https://panic.com/blog/stolen-source-code/)”中记录的那样，这类供应链攻击是非常危险的，即便是一些经验丰富的专业人员也难于幸免。

从MacUpdate下载受影响应用程序的用户，最终会看到类似的恶意应用程序。这些应用程序会与合法应用程序捆绑，并偷偷的在受害者机器上安装恶意软件。

恶意软件一旦被成功安装，受害者计算机的CPU就会被黑客所操作，成为黑客手中挖掘Monero（与比特币类似的货币）加密货币的傀儡机。这会导致我们的电脑运行速度变慢，风扇也会转的很厉害。时间久了，电脑的性能将受到极大的影响，如电池寿命缩短，电用量增加，甚至可能导致计算机过热并损坏硬件（特别是风扇不能在峰值容量下工作，或通风口被灰尘堵塞的情况下）。

最新的恶意软件[OSX.Coldroot](https://objective-see.com/blog/blog_0x2A.html)是一个通用后门，它提供了典型的后门程序对系统的所有常见访问。然而，在新版系统（macOS
10.11，又名El
Capitan或更高版本）中，该恶意软件在某些放面的安装将会失败，并且由于设计的缺陷，在某些系统上完全无法安装。这个恶意软件似乎不是很大的威胁，但这也只是相对的，在可被正确安装的系统上它的危害也不可小觑。

这些只是最近的一些例子。让我们来通过数据感受下Mac恶意软件的发展趋势。在2016年到2017年间，Mac恶意软件增长了270％以上。就在去年，就出现了许多新的后门，例如臭名昭着的[Fruitfly](https://blog.malwarebytes.com/threat-analysis/2017/01/new-mac-backdoor-using-antiquated-code/)，用于捕获个人数据，甚至还被用来生成儿童色情内容。

这并没有阻止日益增长的广告软件和PUP威胁（可能有害的程序，通常是伪装成合法软件的软件）。这些类型的威胁在过去几年中已经普遍存在，甚至已经侵入到了Mac
App Store，App Store中的某些类别的软件（如防病毒软件或广告拦截软件）几乎完全是PUP并且不可信。

但许多Mac用户并没有意识到问题的存在及严重性。有人仍然认为“Mac电脑不会感染病毒”，即没有完全符合严格定义的“Mac病毒”。还有一些人甚至认为Mac是无懈可击的。比如说，“Mac被沙盒包装，所以它们不会被感染。”

![no-Mac-viruses-600x92.png](https://image.3001.net/images/20180311/1520730602298.png!small)  

这种错误的观点，导致许多Mac用户并没有有效的防护措施来阻止恶意软件，更不用说广告软件和PUP所带来的更为常见的威胁。更糟糕的是，由于安全意识的缺失，在对待Windows系统时他们也忽视了威胁的存在。

苹果公司的macOS包含了一些实用的安全功能，但它们很容易被新的恶意软件所绕过，而且它们也根本无法解决广告软件和PUP的问题。

我们知道不是每个人都想在自己的Mac上运行杀毒软件，但如果你正在为此烦恼，那么[Malwarebytes for
Mac](https://malwarebytes.com/mac)可以提供帮助。商业用户也可以从[Malwarebytes Endpoint
Protection](https://www.malwarebytes.com/business/endpointprotection/)获得类似级别的保护。

 ***参考来源：[malwarebytes](https://blog.malwarebytes.com/101/2018/03/the-state-of-mac-malware/)，FB小编 secist 编译，转载请注明来自FreeBuf.COM**

