##  **一、背景介绍**

**MMCore是一款有趣的恶意文件，为下载器下载后在内存中解密执行的一个恶意文件。该恶意文件也被称为BaneChant，最早由fireeye在2013年曝光。此外Forcepoint也在2017年初曝光过而恶意文件的一些攻击活动。**

该恶意文件的活动，主要活跃在亚洲地区，包括中国、巴基斯坦、阿富汗、尼泊尔等。不过Forcepoint也提到该攻击活动也包含非洲和美国。攻击的目标主要为军事目标、媒体、大学等。

该攻击活动可以追溯到2013年，直到2020年，依然存在。虽然技术上并未发生太大的改变，但也存在一些有趣的变化。此外在归属上，我们认为该恶意文件跟印度的一些APT攻击组织有关联，包括白象、蔓灵花、孔夫子等，此外我们还意外的发现了一个未被曝光过的攻击武器，一个.net的RAT。

##  **二、攻击技术分析**

分析的缘起为一个twitter某个安全研究员的帖子：

![](https://image.3001.net/images/20200421/1587452011_5e9e986b04213.png!small)

虽然我们曾经无数次抓获过该种类样本，也曾经多次在攻击活动中发现过该恶意文件的存在，但是一直并未系统的分析和追溯过该恶意文件。因此这次我们决定深入的来跟踪一下这款有趣的恶意文件。

###  **1.MMCore loader分析**

我们以下面文件为例进行分析：

![](https://image.3001.net/images/20200421/1587452045_5e9e988d2485a.png!small)

整体功能：

![](https://image.3001.net/images/20200421/1587452052_5e9e9894d54d6.png!small)

对抗沙箱：首先获取最前端窗口，随后每隔1秒钟检测最前端端口是否发生变化，如果不变则无限循环检测：

![](https://image.3001.net/images/20200421/1587452065_5e9e98a170e84.png!small)

杀软检测：检测snxhk.dll模块（安全厂商Avast的相关文件），如果有则延时2分钟：

![](https://image.3001.net/images/20200421/1587452088_5e9e98b8b0c11.png!small)

解密下载URL，然后下载并内存执行：

存储方式：

![](https://image.3001.net/images/20200421/1587452096_5e9e98c0e2d6e.png!small)

![](https://image.3001.net/images/20200421/1587452106_5e9e98ca4e511.png!small)

解密后：

![](https://image.3001.net/images/20200421/1587452115_5e9e98d3e6f9a.png!small)

![](https://image.3001.net/images/20200421/1587452135_5e9e98e7b8073.png!small)

下载执行：

![](https://image.3001.net/images/20200421/1587452146_5e9e98f256648.png!small)

![](https://image.3001.net/images/20200421/1587452163_5e9e9903d0ef7.png!small)

shellcode位于偏移+0x14位置：

![](https://image.3001.net/images/20200421/1587452179_5e9e991356899.png!small)

###  **2.MMCore分析**

首先检测"avp"、"bdagent"两个杀软进程，如果找到则退出：

![](https://image.3001.net/images/20200421/1587452186_5e9e991acca47.png!small)

![](https://image.3001.net/images/20200421/1587452195_5e9e992320f1f.png!small)

然后使用两轮xor，解密得到一个dll：

![](https://image.3001.net/images/20200421/1587452201_5e9e992957936.png!small)

![](https://image.3001.net/images/20200421/1587452207_5e9e992fd7b30.png!small)

解密得到的dll具有自加载能力：

![](https://image.3001.net/images/20200421/1587452219_5e9e993b232af.png!small)

dllmain中首先判断加载的进程是否为rundll32.exe，不是则执行木马安装操作：

![](https://image.3001.net/images/20200421/1587452225_5e9e99410ad3b.png!small)

然后进行install，首先定位自身._code区段，该区段存放了一个PE文件：

![](https://image.3001.net/images/20200421/1587452231_5e9e99472bf5e.png!small)

![](https://image.3001.net/images/20200421/1587452241_5e9e99516278e.png!small)

将PE文件释放到C:\ProgramData\DailyUpdate\opendrive64.dll：

![](https://image.3001.net/images/20200421/1587452253_5e9e995d8053e.png!small)

在启动目录下释放OneDrive(2).lnk文件实现持久化，该lnk快捷方式指向rundll32.exe加载C:\ProgramData\DailyUpdate\opendrive64.dll并调用其IntRun函数：

![](https://image.3001.net/images/20200421/1587452261_5e9e996515da4.png!small)

启动rundll32.exe加载C:\ProgramData\DailyUpdate\opendrive64.dll并调用其IntRun函数：

![](https://image.3001.net/images/20200421/1587452266_5e9e996ab9c96.png!small)

该文件功能与loader相似，主要功能为从dailysync.zapto.org/fancycumti/combidation/scale.jpg上拉取payload并加载，确保payload本身无文件落地，每次木马加载均需从网络上拉取paylaod。其功能与loader相同，代码相似，因此不再详细分析。

![](https://image.3001.net/images/20200421/1587452273_5e9e9971dab14.png!small)

下面开始执行真正的恶意payload。

首先创建Mutex 44cbdd8d470e88800e6c32bd9d63d341 防止重复运行：

![](https://image.3001.net/images/20200421/1587452280_5e9e997807fb7.png!small)

执行命令收集获取信息，并将获取的信息上传到C&C服务器：

> cmd.exe /q /c tasklist
>
> cmd.exe /q /c ipconfig /all
>
> cmd.exe /q /c dir C:\\\
>
> cmd.exe /q /c dir D:\\\
>
> cmd.exe /q /c dir E:\\\
>
> cmd.exe /q /c dir F:\\\
>
> cmd.exe /q /c dir G:\\\
>
> cmd.exe /q /c dir H:\\\

![](https://image.3001.net/images/20200421/1587452288_5e9e9980c63f5.png!small)

收集的信息会保存在临时木马下，nnp[4位随机].tmp：

![](https://image.3001.net/images/20200421/1587452296_5e9e99886f9d9.png!small)

随后会读取到内存中，再删除该文件，再获取一些其他的信息后进行拼接，拼接后的信息如下：

![](https://image.3001.net/images/20200421/1587452304_5e9e999027b08.png!small)

![](https://image.3001.net/images/20200421/1587452310_5e9e9996a48b1.png!small)

![](https://image.3001.net/images/20200421/1587452317_5e9e999d36e63.png!small)

之后开始跟C&C服务器通信：

![](https://image.3001.net/images/20200421/1587452324_5e9e99a45546c.png!small)

![](https://image.3001.net/images/20200421/1587452331_5e9e99ab0d026.png!small)

获取指令，根据不同指令执行以下操作：

![](https://image.3001.net/images/20200421/1587452338_5e9e99b278877.png!small)

![](https://image.3001.net/images/20200421/1587452344_5e9e99b87bf25.png!small)

命令和功能对应关系如下表：

![](https://image.3001.net/images/20200421/1587452354_5e9e99c23ef0f.png!small)

##  **三、变化历程和总结**

从我们的样本库里检索出大量MMcore的样本，针对这些样本我们进行了归纳分析，发现了一些有趣的规律，总结如下：

###  **1.得名的由来**

该恶意文件第一次被称为MMcore为国外安全公司Forcepoint的一篇分析报告，但是该文章并未解释得名的由来。经过我们的跟踪发现，最初版本的MMcore中，其互斥量的取名为"
MM-Core-Running "，因此我们猜测，Forcepoint因此而给该恶意文件取名为MMCore：

![](https://image.3001.net/images/20200421/1587452365_5e9e99cd000d1.png!small)

此后，作者对该互斥名进行了一些混淆和变化，如M1M-C1o1r1e-R1u1n1n1i1n1g1：

![](https://image.3001.net/images/20200421/1587452370_5e9e99d2e74ce.png!small)

直至现在，已经完全没有MMCore的影子了：

![](https://image.3001.net/images/20200421/1587452375_5e9e99d7d2cac.png!small)

###  **2.标记的变更**

此外，从上面的MMCore的详细分析中，可以发现该恶意文件存在明显的版本和版本标签：

![](https://image.3001.net/images/20200421/1587452383_5e9e99dfd4bfc.png!small)

我们罗列一下发现的样本标签和版本信息，具体信息如下：

![](https://image.3001.net/images/20200421/1587452390_5e9e99e6ad16e.png!small)

可以发现，标签随着时间的变化而变化，目前最新的版本号为2.5，标签名为FreshPass。

###  **3.解密算法的和编码**

MMCore的一大特色就是把shellcode存放在下载回来的jpg文件中，虽然有些jpg已经完全没有了jpg的标识：

![](https://image.3001.net/images/20200421/1587452401_5e9e99f12f515.png!small)

Shellcode的编码主要有两种，Shikata ga nai和普通的编码。Shikata ga
nai编码为常用的一种躲避杀软检测的编码，海莲花中的shellcode也多采用该编码。

![](https://image.3001.net/images/20200421/1587452419_5e9e9a03eb425.png!small)

单次xor解密：

![](https://image.3001.net/images/20200421/1587452432_5e9e9a107c2b9.png!small)

两次xor解密：

![](https://image.3001.net/images/20200421/1587452435_5e9e9a13934f4.png!small)

多次xor解密：

![](https://image.3001.net/images/20200421/1587452446_5e9e9a1e42318.png!small)

1、C&C服务器的偏爱

MMCore的攻击团伙比较偏爱动态域名，使用的动态域名包括有ddns.net、zapto.org、no-ip.org、redirectme.net等，部分信息总结如下表：

![](https://image.3001.net/images/20200421/1587452452_5e9e9a24df26f.png!small)

##  **四、攻击归属**

腾讯安全御见威胁情报中心曾经在2019年发布过一篇文章《疑似白象组织针对巴基斯坦、孟加拉国等南亚国家的最新攻击活动报告》，文中就提到了MMCore部分的分析：

![](https://image.3001.net/images/20200421/1587452465_5e9e9a31611bb.png!small)

该活动的ip跟该文重点分析的白象存在重叠。

此外，也于奇安信的发布的文章《蔓灵花（BITTER）APT组织使用InPage软件漏洞针对巴基斯坦的攻击及团伙关联分析》中的RAT的分析一致：

![](https://image.3001.net/images/20200421/1587452506_5e9e9a5a36e15.png!small)

因此我们把该恶意软件归属到印度的相关组织中。虽然暂时还未清楚MMCore为一个独立小组还是归属于白象、蔓灵花、donot、孔夫子等组织中。但是可以确定的是，该些组织在某些重要的活动中，会采用MMcore恶意软件来进行攻击，至少说明MMCore跟这些组织共享技术。

此外还有个发现，依然是基于腾讯安全御见威胁情报中心去年的文章《疑似白象组织针对巴基斯坦、孟加拉国等南亚国家的最新攻击活动报告》，文章中提到的白象的攻击活动，该文件诱饵使用带有宏的doc进行攻击。我们同样在库里发现了类似的宏文件：

PakCERT-Snapchat hacked by Pakistani Hacker
Group.doc（92ee6729747e1f37dcae7b36d584760d）

![](https://image.3001.net/images/20200421/1587452517_5e9e9a6525e19.png!small)

![](https://image.3001.net/images/20200421/1587452528_5e9e9a70b186a.png!small)

![](https://image.3001.net/images/20200421/1587452536_5e9e9a78211f5.png!small)

而文档释放的恶意文件为一个.net编写的RAT：

![](https://image.3001.net/images/20200421/1587452542_5e9e9a7ee823e.png!small)

该.net RAT为之前未公开过的RAT，也为该组织的常规攻击武器之一。

其中文件的pdb为：d:\KL\rav\rav\obj\Release\rav.pdb

类似的，也有其他的pdb信息为：d:\startnew\JackSparow\WinStore\WinStore\obj\Release\WinStore.pdb

该RAT的主要功能包括：

![](https://image.3001.net/images/20200421/1587452549_5e9e9a85d3846.png!small)

解密C2：

![](https://image.3001.net/images/20200421/1587452564_5e9e9a946a794.png!small)

解密结果为"<http://188.241.68.127/pmpk/>"，拼接参数得到完整URL，执行systeminfo命令获取系统信息拼接到url尾部，url如下

> [http://188.241.68.127/pmpk/blue.php?MNVal=JNENIEYOU-> PC&FNVal=ConnInfo&DVal=17_](http://188.241.68.127/pmpk/blue.php?MNVal=JNENIEYOU-> PC&FNVal=ConnInfo&DVal=17_)

![](https://image.3001.net/images/20200421/1587452571_5e9e9a9bb90e2.png!small)

##  **五、结论**

APT组织的攻击武器库始终在进行不断进化，包括从攻击手段、开发工具和语言等等，也不断会有新的攻击武器库被补充进来。目前曝光的一些攻击武器库可能仅仅只是实际攻击中的冰山一角，但随着跟踪的深入以及被发现的攻击活动越来越多，会有更多的细节被曝光出来。

此外，攻击活动的归属，向来是一个比较头疼的问题。在MMCore的归属上，我们尚无十足的证据来证明必然归属于某个组织，但是至少可以说明，它跟印度的一些组织至少存在基础设施的重叠和攻击武器库的复用。这也跟印度的众多APT组织的关系错综复杂相关。

我们曾不止一次分析过，蔓灵花、白象、孔夫子、donot等等组织存在一定关联，也不排除为同属一个大组织。我们会继续跟踪该恶意文件的攻击活动，力图使得归属上更加清晰。

##  **六、安全建议**

腾讯安全威胁情报中心建议我国重要企业、政府机关对APT攻击保持高度警惕，可参考以下建议提升信息系统的安全性：

> 1、建议重要机构网管培训工作人员不要随意打开不明来源的邮件附件，在邮件目的及发件人均未知的情况下，建议不要访问附件。
>
> 2、建议企业用户使用安全管理系统修补漏洞，及时安装系统补丁，可减少被漏洞攻击的风险。同时注意打开Office文档时，避免启用宏代码。
>
> 3、推荐企业用户部署检测系统对黑客攻击行为进行检测。

 **七、附录**  

1、 **IOCs**

MMCore：

> fa5ca2cba0dab28fa0fb93a9bd7b1d83
>
> eecbfa73955218181b0bc27c9491bd03
>
> 0647bac99b6a8407795134f5d67d4590
>
> 0932b703849364ca1537305761bc3429
>
> 9e73734ac2ab5293c0f326245658***e
>
> b5c1b0137181cf818a46126ca613365e
>
> 263b6c350cbf7354b99139be17c272d3
>
> 9d7953cd0e67e6ebad049faba242a74b
>
> 30e519573d04a2e1505d8daafb712406
>
> 320e29f867ae579a9db0d04e998e5459
>
> 6303059930cfb785c5cf0af1512b2cbe
>
> 5024e86b00012a202d6aa55d5502b9e0
>
> 86e3e98c1e69f887e23d119d0d30d51c
>
> 5a489fb81335a13dff52678bbce69771
>
> 9782e1f021fff363b4a6ee196e1aa9cb
>
> a469f3f7eda824bafb8e569deb05b07d
>
> af501dfd35e7d04afd42d9178601a143
>
> 851ea11fa3cf5ca859dacf47d066d6df
>
> bac7c5528767d86863532bd31bdd12e2
>
> c0baa532636ecca97de85439d7ae8cb3
>
> eecbfa73955218181b0bc27c9491bd03
>
> d692a057330361f8f58163f9aa7fc3a8
>
> f946ea7d9640023d06c2751dde195eb8
>
> 03fa06ac91685e0df4c635339e297e04
>
> 0490e54e4cce81d2ab24a6e7787fa595
>
> 060d13afdb2212a717666b251feda1d3
>
> 5a477d4574983c2603c6f05ff5bae01e
>
> 7d19f3547dc900eba548ee5ceb84edae
>
> baa12a311b9029f33c4fc6de6fde06b0
>
> bddb10729acb2dfe28a7017b261d63db
>
> f3a7d55ee47f2b6bdf7ed6259a6f9496
>
> 423dbab9d632a1fc318f66dfc370ac28
>
> b692a0f56d2462ba0ec50374c653b6e8
>
> b3286791b22f515ab8d7f8866a154e9c
>
> 2826c9c6c25368f773c0e448572585d0
>
> 1e8915ccb433ce0406a98faa94db2237
>
> 8b2b4bed6db31739686531d11c9e98aa
>
> c4cee8d6f30127938681c93dd19f2af4
>
> 0922a6d3d9d9a774eea90853a075056e
>
> b4db105c90d2f2659fd4e930e0b7ad5b
>
> 65067f8c60cbc4ee459641c3b704e180
>
> dailysync.zapto.org
>
> abtprinting.com
>
> adworks.webhop.me
>
> ichoose.zapto.org
>
> theglobalnews24x7.com
>
> timpisstoo.hol.es
>
> burningforests.com
>
> account-support.site
>
> noitfication-office-client.890m.com
>
> mockingbird.no-ip.org
>
> useraccount.co
>
> nayanew1.no-ip.org
>
> nakamini.ddns.net
>
> adrev22.ddns.net
>
> hawahawai123.no-ip.biz
>
> waterlily.ddns.net
>
> pressnorth.net
>
> officeopenxml.co
>
> jospubs.com
>
> davidjone.net
>
> themoondelight.com
>
> g-img.no-ip.biz
>
> adnetwork33.redirectme.net
>
> plansecure.org
>
> kibber.no-ip.org
>
> .net RAT:
>
> 0464acc5f3ea3d907ab9592cf5af2ff4
>
> e223ff5a6a961a6c3ff30811e8a2ceb5
>
> 517c2c6e5e0f27f6f9c759a04a2bf612
>
> b3a2e376a9a1f9e4d597eb8509aed57a
>
> c69cd5894bdf4c92fcfb324e7db83ce3
>
> f8da3eab85def2cdedd4227eec3114bb
>
> 73eb441bcf27a1ee4b1f5c1f78139b3b
>
> 5b1d7c4cea8fcb96696a6e9318d36a45
>
> 2cc9cd56b2e4c17b6b63bad4dfc5bc10
>
> 188.241.68.127
>
> 91.211.88.71

2、 **参考资料**

> <https://s.tencent.com/research/report/711.html>
>
> <https://ti.qianxin.com/blog/articles/analysis-of-targeted-attack-against-> pakistan-by-exploiting-inpage-vulnerability-and-related-apt-groups-english/>
>
> <https://www.fireeye.com/blog/threat-research/2013/04/trojan-apt-banechant-> in-memory-trojan-that-observes-for-multiple-mouse-clicks.html>
>
> <https://www.forcepoint.com/blog/x-labs/mm-core-memory-backdoor-returns-> bigboss-and-sillygoose>
>
> <https://twitter.com/KorbenD_Intel/status/1237121311450652672>

***本文作者： 腾讯安全联合实验室，转载请注明来自FreeBuf.COM**  
  

