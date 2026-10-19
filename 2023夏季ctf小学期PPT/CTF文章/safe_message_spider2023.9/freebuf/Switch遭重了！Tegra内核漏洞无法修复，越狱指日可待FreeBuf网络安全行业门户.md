***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

![nintendo-TA.jpg](https://image.3001.net/images/20180425/15246373824552.jpg!small)  

**研究人员发布了一个Fusée Gelée漏洞的PoC代码，漏洞影响的是任天堂Switch主机里嵌入式处理器中涉及Nvidia Tegra的代码。**

这个漏洞被取名为“FuséeGelée”，是一种冷启动破解，可以让用户绕过设备锁，在Switch上运行自定义代码。

漏洞的意义在于给那些用户提供了运行自定义游戏或者导出设备数据的可能，这些都是目前Switch禁止的。

## Fusée Gelée无法修复

![Fusee-Gelee.jpg](https://image.3001.net/images/20180425/15246375741453.jpg!small)  

技​​术层面上，Fusée Gelée只不过是个微不足道的缓冲区溢出漏洞。问题在于漏洞处于Switch的bootROM组件中，该组件位于Nvidia
Tegra芯片组内，用于控制设备的启动程序。

这个组件在离开Nintendo工厂后就会在硬件级别上被锁定，也就无法通过固件补丁更新。也就是说这个Fusée
Gelée不可能修复，除非任天堂为了防范越狱决定召回所有的游戏机，但这显然也不太可能。

## 越狱过程极其简单  

要使用这个Fusée Gelée漏洞难度也并不高，用户需要强制重启Switch，然后进入USB恢复模式，然后用USB线连接，通过控制台运行Python脚本。

可能整个过程中最难的环节就是强制Switch进入USB恢复模式，需要短接右手柄插槽的两个触点。

不过没关系，发现漏洞的大神Katherine
Temkin为大家提供了全套指导，包括[常见问题解答页面](http://www.ktemkin.com/)、[短接引脚的教程](https://github.com/reswitched/fusee-launcher/blob/master/report/fusee_gelee.md)以及[PoC代码](https://github.com/reswitched/fusee-launcher)。

由于当前的PoC代码只能在Switch上显示设备数据，Temkin保证会在6月15日发布更多有关利用Fusée Gelée的脚本和信息。

## 争先恐后曝漏洞  

有趣的是，破解Switch引发了团队们的相互竞争。

Temkin说她提前披露了漏洞内容，因为另一个硬件黑客团队之前表示他们会在几周内发布一个Switch芯片exp。

硬件黑客团队之间存在激烈的竞争，而Temkin想要在网上率先发布漏洞，Temkin是ReSwitched团队的成员。

事实上，研究Switch越狱的不止这两个团队，就在Temkin发布Fusée Gelée漏洞细节之后，团队Fail0verflow也发布了自己的Nvidia
Tegra漏洞（ShofEL2）。

团队们还在不断改进利用攻击，试图让越狱变得更简单，Temkin目前正在研究改进FuséeGelée漏洞，并将其整合到一个名为Atmosphère的越狱工具包中，该工具包计划于6月发布。

而Fail0verflow则宣布他们将推出一款定制工具switchx
pro，使得短接引脚变得更容易。不过他们也开玩笑说其实任何电子商店购买的电线就可以做到。

![TIM截图20180425142354.png](https://image.3001.net/images/20180425/15246375405876.png!small)  

## Fusée Gelée漏洞会影响其他设备

无论如何，Fusée Gelée漏洞应该是广大Switch玩家的福音，但是漏洞也可能带来严重的后果。

本次破解利用了Nvidia Tegra
X1芯片（版本210）的USB恢复模式漏洞，该漏洞能够绕过保护芯片关键部分bootROM，通过发送超长的控制请求导致内存溢出，从而获得直接内存访问。这个漏洞影响的是大量Tegra设备，不仅仅是Switch，甚至不止是Tegra
X1芯片。因此急于过早地公布漏洞细节可能也太过草率。

 *** 参考来源：[BleepingComputer](https://www.hackread.com/science-fiction-becomes-science-fact-our-brains-can-be-hacked/) &
[CnBeta](https://hot.cnbeta.com/articles/game/720049)，本文作者Sphinx，转载注明来自FreeBuf.com**  

