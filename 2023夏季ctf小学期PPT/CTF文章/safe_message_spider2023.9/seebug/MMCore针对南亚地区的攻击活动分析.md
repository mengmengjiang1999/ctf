**作者：腾讯御见威胁情报中心**  
**原文链接：<https://mp.weixin.qq.com/s/QrmXuXt3jKjNYzRQn3SIWQ>**

## 背景介绍

MMCore是一款有趣的恶意文件，为下载器下载后在内存中解密执行的一个恶意文件。该恶意文件也被称为BaneChant，最早由fireeye在2013年曝光。此外Forcepoint也在2017年初曝光过而恶意文件的一些攻击活动。

该恶意文件的活动，主要活跃在亚洲地区，包括中国、巴基斯坦、阿富汗、尼泊尔等。不过Forcepoint也提到该攻击活动也包含非洲和美国。攻击的目标主要为军事目标、媒体、大学等。

该攻击活动可以追溯到2013年，直到2020年，依然存在。虽然技术上并未发生太大的改变，但也存在一些有趣的变化。此外在归属上，我们认为该恶意文件跟印度的一些APT攻击组织有关联，包括白象、蔓灵花、孔夫子等，此外我们还意外的发现了一个未被曝光过的攻击武器，一个.net的RAT。

## 攻击技术分析

分析的缘起为一个twitter某个安全研究员的帖子：

![](https://images.seebug.org/content/images/2020/04/2853148e-0924-4cd0-8462-bb0877badf35.png-w331s)

虽然我们曾经无数次抓获过该种类样本，也曾经多次在攻击活动中发现过该恶意文件的存在，但是一直并未系统的分析和追溯过该恶意文件。因此这次我们决定深入的来跟踪一下这款有趣的恶意文件。

### 1.MMCore loader分析

我们以下面文件为例进行分析：

![](https://images.seebug.org/content/images/2020/04/4e37320f-b057-4250-89b5-bde5b0213f18.jpg-w331s)

整体功能：

![](https://images.seebug.org/content/images/2020/04/1c51bac7-a126-4d46-9cb2-368fe37f9895.png-w331s)

对抗沙箱：首先获取最前端窗口，随后每隔1秒钟检测最前端端口是否发生变化，如果不变则无限循环检测：

![](https://images.seebug.org/content/images/2020/04/272f6fd9-4d99-4e00-9e89-7da9538b02d5.png-w331s)

杀软检测：检测snxhk.dll模块（安全厂商Avast的相关文件），如果有则延时2分钟：

![](https://images.seebug.org/content/images/2020/04/5271f47e-103d-4c16-90ee-64bf5ace8283.png-w331s)

解密下载URL，然后下载并内存执行：

存储方式：

![](https://images.seebug.org/content/images/2020/04/76d656a8-d35c-4abd-9e92-22e35521558d.png-w331s)

![](https://images.seebug.org/content/images/2020/04/6b158aee-399e-4837-92cb-679de00b8ee4.png-w331s)

解密后：

![](https://images.seebug.org/content/images/2020/04/13816b68-f5d2-4f2b-af43-22946582aec3.png-w331s)

![](https://images.seebug.org/content/images/2020/04/8db6f66f-7e71-427e-bb80-dd35e3563f60.png-w331s)

下载执行：

![](https://images.seebug.org/content/images/2020/04/7bfe081d-cc18-43a1-922c-c65ed6c1c862.png-w331s)

![](https://images.seebug.org/content/images/2020/04/432da1d8-1a23-4043-94ce-980dadfcbb6e.png-w331s)

shellcode位于偏移+0x14位置：

![](https://images.seebug.org/content/images/2020/04/7f0ee006-c5fc-4bcc-82b6-4736fcc4bd62.png-w331s)

### 2.MMCore分析 2.MMCore分析

首先检测"avp"、"bdagent"两个杀软进程，如果找到则退出：

![](https://images.seebug.org/content/images/2020/04/953bbfd2-bb22-476c-92a9-bb5bea79f073.png-w331s)

![](https://images.seebug.org/content/images/2020/04/fdb14add-c937-4d79-b68e-361c814a68dc.png-w331s)

然后使用两轮xor，解密得到一个dll：

![](https://images.seebug.org/content/images/2020/04/279c3f4c-6050-4659-8a9a-82320808a217.png-w331s)

![](https://images.seebug.org/content/images/2020/04/bc7edb8e-e487-48e8-88f2-8f050c3ea3a9.png-w331s)

解密得到的dll具有自加载能力：

![](https://images.seebug.org/content/images/2020/04/f085b114-5bb0-474a-b195-36a2b853807d.png-w331s)

dllmain中首先判断加载的进程是否为rundll32.exe，不是则执行木马安装操作：

![](https://images.seebug.org/content/images/2020/04/850e598d-d512-4033-8319-28a97d987547.png-w331s)

然后进行install，首先定位自身`._code`区段，该区段存放了一个PE文件：

![](https://images.seebug.org/content/images/2020/04/e7aa774f-511f-479b-9d2d-a4988868f5a9.png-w331s)

![](https://images.seebug.org/content/images/2020/04/bc663701-b1b9-4d34-9390-ed029f6541ea.png-w331s)

将PE文件释放到`C:\ProgramData\DailyUpdate\opendrive64.dll`：

![](https://images.seebug.org/content/images/2020/04/493f452d-140c-480b-9d7d-5a26f5979063.png-w331s)

在启动目录下释放`OneDrive(2).lnk`文件实现持久化，该lnk快捷方式指向`rundll32.exe`加载`C:\ProgramData\DailyUpdate\opendrive64.dll`并调用其IntRun函数：

![](https://images.seebug.org/content/images/2020/04/58d61f57-8a97-42b6-afbc-13833dc21068.png-w331s)

启动`rundll32.exe`加载`C:\ProgramData\DailyUpdate\opendrive64.dll`并调用其IntRun函数：

![](https://images.seebug.org/content/images/2020/04/4a460a52-611f-4c8c-bd07-dc6caa17c99a.png-w331s)

该文件功能与loader相似，主要功能为从`dailysync.zapto.org/fancycumti/combidation/scale.jpg`上拉取payload并加载，确保payload本身无文件落地，每次木马加载均需从网络上拉取paylaod。其功能与loader相同，代码相似，因此不再详细分析。

![](https://images.seebug.org/content/images/2020/04/95ff8d7d-a094-47fd-9b8f-b00a63b97de5.png-w331s)

下面开始执行真正的恶意payload。

首先创建`Mutex 44cbdd8d470e88800e6c32bd9d63d341` 防止重复运行：

![](https://images.seebug.org/content/images/2020/04/d68af81c-7a90-4ea1-a6f8-4b36107b1ae5.png-w331s)

执行命令收集获取信息，并将获取的信息上传到C&C服务器：

cmd.exe /q /c tasklist

cmd.exe /q /c ipconfig /all

cmd.exe /q /c dir C:\

cmd.exe /q /c dir D:\

cmd.exe /q /c dir E:\

cmd.exe /q /c dir F:\

cmd.exe /q /c dir G:\

cmd.exe /q /c dir H:\

![](https://images.seebug.org/content/images/2020/04/70c52e46-6117-40aa-a7b9-9cf46e045045.png-w331s)

收集的信息会保存在临时木马下，nnp[4位随机].tmp：

![](https://images.seebug.org/content/images/2020/04/5b157cb2-58a8-4678-9973-12444f8d2edc.png-w331s)

随后会读取到内存中，再删除该文件，再获取一些其他的信息后进行拼接，拼接后的信息如下：

![](https://images.seebug.org/content/images/2020/04/34224794-4f38-45f2-9d14-b9f92091fb6e.png-w331s)

![](https://images.seebug.org/content/images/2020/04/4f6e3845-99d4-4793-aae6-50d764653178.png-w331s)

![](https://images.seebug.org/content/images/2020/04/68d29302-6af9-4951-b1cf-07a2bd7879e3.png-w331s)

之后开始跟C&C服务器通信：

![](https://images.seebug.org/content/images/2020/04/86ca0854-c46c-4f49-93a3-c85da304846a.png-w331s)

![](https://images.seebug.org/content/images/2020/04/24102988-a65e-47d0-86b7-8f48eb5e221d.png-w331s)

获取指令，根据不同指令执行以下操作：

![](https://images.seebug.org/content/images/2020/04/fdbb6f38-2677-470b-a6f3-1c2b42507e5c.png-w331s)

![](https://images.seebug.org/content/images/2020/04/ad43b5c5-96da-4086-909b-d869b8021013.png-w331s)

命令和功能对应关系如下表：

![](https://images.seebug.org/content/images/2020/04/bace9419-20cb-4263-bc02-5b96a67a3dae.jpg-w331s)

## 变化历程和总结

从我们的样本库里检索出大量MMcore的样本，针对这些样本我们进行了归纳分析，发现了一些有趣的规律，总结如下：

### 1.得名的由来

该恶意文件第一次被称为MMcore为国外安全公司Forcepoint的一篇分析报告，但是该文章并未解释得名的由来。经过我们的跟踪发现，最初版本的MMcore中，其互斥量的取名为"
MM-Core-Running "，因此我们猜测，Forcepoint因此而给该恶意文件取名为MMCore：

![](https://images.seebug.org/content/images/2020/04/7bb08bab-c6f5-49f5-a519-3ebb9565ca0e.png-w331s)

此后，作者对该互斥名进行了一些混淆和变化，如M1M-C1o1r1e-R1u1n1n1i1n1g1：

![](https://images.seebug.org/content/images/2020/04/34ce6593-c6c5-4418-9414-c71192d08060.png-w331s)

直至现在，已经完全没有MMCore的影子了：

![](https://images.seebug.org/content/images/2020/04/3892228c-b45f-4398-9118-b4ec6f340201.png-w331s)

### 2.标记的变更

此外，从上面的MMCore的详细分析中，可以发现该恶意文件存在明显的版本和版本标签：

![](https://images.seebug.org/content/images/2020/04/948b6ae4-5cec-4ce3-9622-6987fb70b6e8.png-w331s)

我们罗列一下发现的样本标签和版本信息，具体信息如下：

![](https://images.seebug.org/content/images/2020/04/b1f7dcf7-84f9-441c-8665-1b524aec94c1.jpg-w331s)

可以发现，标签随着时间的变化而变化，目前最新的版本号为2.5，标签名为FreshPass。

### 3.解密算法的和编码

MMCore的一大特色就是把shellcode存放在下载回来的jpg文件中，虽然有些jpg已经完全没有了jpg的标识：

![](https://images.seebug.org/content/images/2020/04/89b7d72b-f4fb-4624-9661-bf0eeb162c21.png-w331s)

Shellcode的编码主要有两种，Shikata ga nai和普通的编码。Shikata ga
nai编码为常用的一种躲避杀软检测的编码，海莲花中的shellcode也多采用该编码。

![](https://images.seebug.org/content/images/2020/04/015f99b3-8f0c-4ec1-b649-e35a7b5762d7.png-w331s)

单次xor解密：

![](https://images.seebug.org/content/images/2020/04/128b9c58-8c5a-4148-9c11-617e1d47ca54.png-w331s)

两次xor解密：

![](https://images.seebug.org/content/images/2020/04/d57275c2-c701-490f-9307-1365219526a4.png-w331s)

多次xor解密：

![](https://images.seebug.org/content/images/2020/04/16a8b1da-9780-4f8c-8979-87caa3b4d3e0.png-w331s)

C&C服务器的偏爱

MMCore的攻击团伙比较偏爱动态域名，使用的动态域名包括有ddns.net、zapto.org、no-ip.org、redirectme.net等，部分信息总结如下表：

![](https://images.seebug.org/content/images/2020/04/4ba81191-e821-472a-837f-e794bc66d2f1.jpg-w331s)

## 攻击归属

腾讯安全御见威胁情报中心曾经在2019年发布过一篇文章《疑似白象组织针对巴基斯坦、孟加拉国等南亚国家的最新攻击活动报告》，文中就提到了MMCore部分的分析：

![](https://images.seebug.org/content/images/2020/04/6f482054-983f-455f-9da9-763bad09a391.png-w331s)

该活动的ip跟该文重点分析的白象存在重叠。

此外，也于奇安信的发布的文章《蔓灵花（BITTER）APT组织使用InPage软件漏洞针对巴基斯坦的攻击及团伙关联分析》中的RAT的分析一致：

![](https://images.seebug.org/content/images/2020/04/35752375-75d9-4f9d-a604-83e4e83adb88.png-w331s)

因此我们把该恶意软件归属到印度的相关组织中。虽然暂时还未清楚MMCore为一个独立小组还是归属于白象、蔓灵花、donot、孔夫子等组织中。但是可以确定的是，该些组织在某些重要的活动中，会采用MMcore恶意软件来进行攻击，至少说明MMCore跟这些组织共享技术。

此外还有个发现，依然是基于腾讯安全御见威胁情报中心去年的文章《疑似白象组织针对巴基斯坦、孟加拉国等南亚国家的最新攻击活动报告》，文章中提到的白象的攻击活动，该文件诱饵使用带有宏的doc进行攻击。我们同样在库里发现了类似的宏文件：

`PakCERT-Snapchat hacked by Pakistani Hacker
Group.doc（92ee6729747e1f37dcae7b36d584760d）`

![](https://images.seebug.org/content/images/2020/04/3629af40-cf4a-47f6-9f9d-64984be5ad73.png-w331s)

![](https://images.seebug.org/content/images/2020/04/20e56fbe-4383-470a-90b3-dfef36210b7d.png-w331s)

![](https://images.seebug.org/content/images/2020/04/0dadeade-0304-4fda-90de-49a464382585.png-w331s)

而文档释放的恶意文件为一个.net编写的RAT：

![](https://images.seebug.org/content/images/2020/04/d4d8fc53-2b01-45a5-b1f8-6d5b77053461.png-w331s)

该.net RAT为之前未公开过的RAT，也为该组织的常规攻击武器之一。

其中文件的pdb为：`d:\KL\rav\rav\obj\Release\rav.pdb`

类似的，也有其他的pdb信息为：`d:\startnew\JackSparow\WinStore\WinStore\obj\Release\WinStore.pdb`

该RAT的主要功能包括：

![](https://images.seebug.org/content/images/2020/04/d7dd0427-405e-4354-913e-6b20538c60b2.jpg-w331s)

解密C2：

![](https://images.seebug.org/content/images/2020/04/9ce00411-1af3-4824-9112-59954791326e.png-w331s)

解密结果为<http://188.241.68.127/pmpk/>，拼接参数得到完整URL，执行systeminfo命令获取系统信息拼接到url尾部，url如下：

[http://188.241.68.127/pmpk/blue.php?MNVal=JNENIEYOU-PC&FNVal=ConnInfo&DVal=17_](http://188.241.68.127/pmpk/blue.php?MNVal=JNENIEYOU-PC&FNVal=ConnInfo&DVal=17_)

![](https://images.seebug.org/content/images/2020/04/64f6eda3-1d39-43f4-a056-75b42d1a9b27.png-w331s)

## 结论

APT组织的攻击武器库始终在进行不断进化，包括从攻击手段、开发工具和语言等等，也不断会有新的攻击武器库被补充进来。目前曝光的一些攻击武器库可能仅仅只是实际攻击中的冰山一角，但随着跟踪的深入以及被发现的攻击活动越来越多，会有更多的细节被曝光出来。

此外，攻击活动的归属，向来是一个比较头疼的问题。在MMCore的归属上，我们尚无十足的证据来证明必然归属于某个组织，但是至少可以说明，它跟印度的一些组织至少存在基础设施的重叠和攻击武器库的复用。这也跟印度的众多APT组织的关系错综复杂相关。

我们曾不止一次分析过，蔓灵花、白象、孔夫子、donot等等组织存在一定关联，也不排除为同属一个大组织。我们会继续跟踪该恶意文件的攻击活动，力图使得归属上更加清晰。

## 安全建议

  1. 腾讯安全威胁情报中心建议我国重要企业、政府机关对APT攻击保持高度警惕，可参考以下建议提升信息系统的安全性：

  2. 建议重要机构网管培训工作人员不要随意打开不明来源的邮件附件，在邮件目的及发件人均未知的情况下，建议不要访问附件。

  3. 建议企业用户使用腾讯安全T-Sec终端安全管理系统修补漏洞，及时安装系统补丁，可减少被漏洞攻击的风险。同时注意打开Office文档时，避免启用宏代码。

  4. 推荐企业用户部署腾讯T-Sec高级威胁检测系统（腾讯御界）对黑客攻击行为进行检测。

## **附录**

### 1.IOCs

MMCore：

fa5ca2cba0dab28fa0fb93a9bd7b1d83

eecbfa73955218181b0bc27c9491bd03

0647bac99b6a8407795134f5d67d4590

0932b703849364ca1537305761bc3429

9e73734ac2ab5293c0f326245658b50e

b5c1b0137181cf818a46126ca613365e

263b6c350cbf7354b99139be17c272d3

9d7953cd0e67e6ebad049faba242a74b

30e519573d04a2e1505d8daafb712406

320e29f867ae579a9db0d04e998e5459

6303059930cfb785c5cf0af1512b2cbe

5024e86b00012a202d6aa55d5502b9e0

86e3e98c1e69f887e23d119d0d30d51c

5a489fb81335a13dff52678bbce69771

9782e1f021fff363b4a6ee196e1aa9cb

a469f3f7eda824bafb8e569deb05b07d

af501dfd35e7d04afd42d9178601a143

851ea11fa3cf5ca859dacf47d066d6df

bac7c5528767d86863532bd31bdd12e2

c0baa532636ecca97de85439d7ae8cb3

eecbfa73955218181b0bc27c9491bd03

d692a057330361f8f58163f9aa7fc3a8

f946ea7d9640023d06c2751dde195eb8

03fa06ac91685e0df4c635339e297e04

0490e54e4cce81d2ab24a6e7787fa595

060d13afdb2212a717666b251feda1d3

5a477d4574983c2603c6f05ff5bae01e

7d19f3547dc900eba548ee5ceb84edae

baa12a311b9029f33c4fc6de6fde06b0

bddb10729acb2dfe28a7017b261d63db

f3a7d55ee47f2b6bdf7ed6259a6f9496

423dbab9d632a1fc318f66dfc370ac28

b692a0f56d2462ba0ec50374c653b6e8

b3286791b22f515ab8d7f8866a154e9c

2826c9c6c25368f773c0e448572585d0

1e8915ccb433ce0406a98faa94db2237

8b2b4bed6db31739686531d11c9e98aa

c4cee8d6f30127938681c93dd19f2af4

0922a6d3d9d9a774eea90853a075056e

b4db105c90d2f2659fd4e930e0b7ad5b

65067f8c60cbc4ee459641c3b704e180

域名：

dailysync.zapto.org

abtprinting.com

adworks.webhop.me

ichoose.zapto.org

theglobalnews24x7.com

timpisstoo.hol.es

burningforests.com

account-support.site

noitfication-office-client.890m.com

mockingbird.no-ip.org

useraccount.co

nayanew1.no-ip.org

nakamini.ddns.net

adrev22.ddns.net

hawahawai123.no-ip.biz

waterlily.ddns.net

pressnorth.net

officeopenxml.co

jospubs.com

davidjone.net

themoondelight.com

g-img.no-ip.biz

adnetwork33.redirectme.net

plansecure.org

kibber.no-ip.org

.net RAT:

0464acc5f3ea3d907ab9592cf5af2ff4

e223ff5a6a961a6c3ff30811e8a2ceb5

517c2c6e5e0f27f6f9c759a04a2bf612

b3a2e376a9a1f9e4d597eb8509aed57a

c69cd5894bdf4c92fcfb324e7db83ce3

f8da3eab85def2cdedd4227eec3114bb

73eb441bcf27a1ee4b1f5c1f78139b3b

5b1d7c4cea8fcb96696a6e9318d36a45

2cc9cd56b2e4c17b6b63bad4dfc5bc10

IP：

188.241.68.127

91.211.88.71

### 2、参考资料

  1. <https://s.tencent.com/research/report/711.html>

  2. <https://ti.qianxin.com/blog/articles/analysis-of-targeted-attack-against-pakistan-by-exploiting-inpage-vulnerability-and-related-apt-groups-english/>

  3. <https://www.fireeye.com/blog/threat-research/2013/04/trojan-apt-banechant-in-memory-trojan-that-observes-for-multiple-mouse-clicks.html>

  4. <https://www.forcepoint.com/blog/x-labs/mm-core-memory-backdoor-returns-bigboss-and-sillygoose>

  5. <https://twitter.com/KorbenD_Intel/status/1237121311450652672>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1184/>

