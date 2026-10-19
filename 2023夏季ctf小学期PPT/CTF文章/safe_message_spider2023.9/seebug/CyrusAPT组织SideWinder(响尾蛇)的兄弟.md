**作者：深信服千里目安全实验室  
原文链接：<https://mp.weixin.qq.com/s/VNvnBgUknMZ8kw8ug-q5ZA>**

## 1.摘要

2019年7月，有人在VirusTotal上传了一个疑似针对阿富汗攻击的样本。这个样本最初被判定为"SideWinder(响尾蛇)"组织所为，有安全者深入分析后发现C2是一个印度的网站。但是网站是伪装的还是真实的无法验证。样本使用的木马和以往披露的"SideWinder(响尾蛇)"APT组织所用的木马也有差异。

2020年9月，印度的安全厂商Quick
Heal的威胁情报团队声称发现了一个针对印度国防部门的攻击组织，并且声称该攻击组织至少从2019年已经开始针对印度发起攻击。Quick
Heal的威胁情报团队将2019年到他们发报告时的一系列的攻击行动称为”Operation SideCopy“。“Operation
SideCopy”的攻击手法和"SideWinder(响尾蛇)"APT组织是高度相似的，因为"SideWinder(响尾蛇)"APT组织据称是来自印度，因此Quick
Heal的威胁情报团队认为不是"SideWinder(响尾蛇)"APT组织。他们认为这些攻击行动和一个叫做”透明部落( Transparent Tribe
)"的APT组织有“关联”。但是报告发出去后，很多新闻媒体就声称是来自巴基斯坦的名叫”透明部落( Transparent Tribe
)"的APT组织在攻击印度政府都，甚至声称是“有中国帮助的”。

2021年4月底，我们注意到了一系列的针对印度政府，军队等的攻击。通过对这些攻击手法的分析，我们发现这些攻击的手法和以前被称为"SideWinder(响尾蛇)"APT组织所用的手法很相似。这些攻击在最后阶段使用的木马名字叫Cyrus,为了方便区分我们称该组织为Cyrus
APT组织。

我们发现的针对印度的攻击大多通过入侵印度的网站或者伪装成印度的网站，将其作为C2服务器。接着向目标发送钓鱼邮件，邮件中嵌入一个包含lnk文件或者漏洞利用的文档。当点击了lnk文件或者包含有漏洞的文档后，恶意代码会从C2服务器上下载HTA文件，HTA文件会在某个目录下释放出一个名字为DUser.dll的文件，同时拷贝credwiz.exe到该目录。利用
DLL Side-loading
方法来执行恶意代码即通过credwiz.exe来加载DUser.dll，实现恶意代码的执行。DUser.dll文件通常不会包含恶意代码，它只是负责执行另一个包含恶意代码的文件。这些行为和"SideWinder(响尾蛇)"APT组织的攻击手法是很相似的，只是最终的payload大多是经过修改的开源的backdoor。这个backdoor使用delphi语言开发，攻击者在内部可能称其为"Cyrus"。

## 2\. Cyrus APT组织的历史

### 2.1 2019年下半年：上传到VirusTotal的样本

我们在VirusTotal上发现了两个HTA文件，它们分别被上传于2019年7月和2019年12月。这些HTA样本和"SideWinder(响尾蛇)"APT组织所用的样本流程完全一样，但是它们包含的经过序列化的.NET模块复杂程度更高一些,从代码上看它们增加了不少的功能。

2019年7月上传到VirusTotal的文件名字是:Sponsorship-Benefits.docx.lnk(dbdd56932730210f6556cc636aeb8a66)。这个lnk执行后会下载一个HTA文件:

![](https://images.seebug.org/content/images/2021/09/c44ee47d-c41e-463d-8395-fbbc4f717767.png-w331s)

这个文件中包含的经过序列化的.NET的模块如下:

![](https://images.seebug.org/content/images/2021/09/51f8796b-c0e3-43ee-82f1-c6a735f4f24d.png-w331s)

和"SideWinder(响尾蛇)"APT组织使用的hta.dll相比代码发生了变化, RealStPrickBack的定义如下:

![](https://images.seebug.org/content/images/2021/09/132f4970-fc5f-4a3a-a6cb-f03ed2159c42.png-w331s)

RealStPrickBack和"SideWinder(响尾蛇)"组织所用的hta.dll的pink函数很像，它会解码和解压缩数据，然后写入到文件中并打开它。接着调用getThridStrike下载另外一个HTA并执行。和"SideWinder(响尾蛇)"APT组织所用的hta.dll不同的是:压缩的数据头部有四个字节用来描述整个文件的大小，没有判断当前系统中的是否安装杀软。getThridStrike下载下来的HTA文件包含一个prebothta.dll文件，HTA文件调用的是preBotHta.Pink函数。preBotHta类的定义如下:

![](https://images.seebug.org/content/images/2021/09/03af908c-fb93-4489-8ca4-a0d91a794d15.png-w331s)

preBotHta类的函数Pink会判断当前系统中安装的杀毒软件，然后根据杀毒软件的类型来决定释放文件的方式:

![](https://images.seebug.org/content/images/2021/09/c759a950-3cae-4bcd-b46d-bf25c967935e.png-w331s)

其中的preBotHta.activeDefender的代码如下:

![](https://images.seebug.org/content/images/2021/09/6ec6cfc0-0038-49b4-9de7-74df5239d397.png-w331s)

这个函数执行的大致流程如下:

将Credwiz.exe拷贝到C:\ProgramData\dsk\目录下

preBotHta.work函数创建一个%ProgramData%Win Setting
Loader.lnk文件,LNK文件包含运行C:\ProgramData\dsk\Credwiz.exe的命令

preBotHta.CopyExeAsTxt函数释放一个%temp%\Windows Cleaner\ibtsiva.txt文件。

preBotHta.CopyDLLDefender函数 释放文件C:\ProgramData\dsk\abc.txt

preBotHta.renNameFile函数 将%temp%\Windows Cleaner\ibtsiva.txt重命名为%temp%\Windows
Cleaner\itstr.exe,然后调用powershell执行这个文件。

preBotHta.ExecuteCommand 函数执行cmd命令打开Win Setting Loader.lnk文件。

这里释放出来的abc.txt就是Duser.dll,但是没有将其重命名为Duser.dll。当系统中安装的是其他类型的杀软时执行流程是:Credwiz.exe加载Duser.dll,接着DUser.dll运行itstr.exe。我们推测是当在系统中安装了windows
defender时，无法使用这种 DLL Side-loading方法，于是攻击者选择直接运行itstr.exe。DUser.dll运行后会执行itstr.exe，而itstr.exe是一个使用Delphi开发的开源backdoor。该木马源代码的可以在github上找到，相关的链接如下:

<https://github.com/Grampinha/AllaKore_Remote>

值得一提的是这个样本第一阶段的C2是vidyasagaracademybrg[.]in。如果搜索这个域名可以在google地图上找到一个真实存在的地址:

![](https://images.seebug.org/content/images/2021/09/a4477c85-9fd5-45c2-9865-aaf28a28255d.png-w331s)

这是一个印度的学校，现在这个网站仍然可以打开。但现在是一个中国的矿机公司的网站。我们推测这可能是一个虚假的网站。如果说"SideWinder(响尾蛇)"APT组织是来自印度，那么伪装成印度学校的网站就显得不太正常。有一个安全研究者在分析完这个样本后也对此持有怀疑的态度，他判断可能是攻击者模仿了"SideWinder(响尾蛇)”APT组织。他的文章链接地址是:<https://sebdraven.medium.com/copy-cat-of-apt-sidewinder-1893059ca68d>

2019年12月有人提交到VirustTotal上一个名字为1.hta的文件，文件MD5:74d9e996d978a3c53c9c974a144a6b37。这个文件和7月份相比文件有少许的变动。HTA.DLL对比如下:

![](https://images.seebug.org/content/images/2021/09/0b8c6061-38c6-4530-998e-0c971b4e62d6.png-w331s)

可以看到12月份的hta.dll保存了download函数，但是这个函数是空的。7月份的样本下载第二阶段的hta文件是保存在临时目录，12月份的则是保存在C:\ProgramData\Adobe\目录下。

prebothta.dll对比如下:

![](https://images.seebug.org/content/images/2021/09/778d25ea-7a93-4e4e-adbb-e4f3d597b9e1.png-w331s)

两者对比可以发现PreBotHta类的命名被改成了DraftingPad,同时pink函数被改成了pinkAgin。增加了一个activeQuick函数，这里应该是针对Quick
Heal的。Quick
Heal是一家印度网络安全软件公司。除此之外释放文件的路径变成了C:\ProgramData\Adobe\,原来的%temp%\Windows
Cleaner\itstr.exe被改成了%temp%\Windows
Cleaner\MicroSoft\winms.exe。winms.exe仍然是一个使用Delphi开发的开源backdoor，和7月份的一样。

2019年12月份上传到VirustTotal的样本第二阶段的C2是fincruitconsulting[.]in，这个网站现在开可以打开，是一个印度的公司的网站。

### 2.2 2020年："SideWinder(响尾蛇)"与Operation SideCopy“

一个名字叫Quick Heal的印度安全公司发布了一篇名字为"Operation SideCopy An insight into Transparent
Tribe’s sub-divisionwhich has been incorrectly attributed for
years"的报告。这个公司的名字在2019年12上被上传到VirusTotal的样本中包含过。Quick
Heal声称他们在自己的设备上捕获到一些样本，这些样本被误解为"SideWinder(响尾蛇)"APT组织。他们认为该组织最早从2019年开始，这个组织和透明部落(Transparent
Trib)APT 组织相关。这些样本主要是攻击印度的国防工业和军人。我们没有找到Quick Heal报告中提到的样本，但是Quick
Heal报告提到的样本显然和2019年的7月以及12月提交到VirusTotal上的样本的行为高度相似。

更有意思的是Quick Heal报告中提到一个PDB文件E:\OpenRATs\ NigthFury\Night Fury HTA upload\
preBotHta\obj\ Debug\ preBotHta.pdb。当然这并不能说明什么，也可能是攻击者随便起的名字。

Quick Heal的报告在报告中提到有一张对比图：

![](https://images.seebug.org/content/images/2021/09/4ee561e1-f623-42bd-82e5-1f255dfe7c55.png-w331s)

我们在前面的章节中提到2019年12份上传到VirusTotal样本和Quick
Heal所声称的2020年发现的新的hta.dll样本在代码上完全一致。这也说明了，相关的攻击在2019年就发生了。另外Quick
Heal的报告中提到"SideWinder(响尾蛇)"APT组织使用Duser.dll都是C#开发的，这个结论不准确,"SideWinder(响尾蛇)"APT组织使用Duser.dll有部分是使用C++开发的,尤其是在2019年上半年出现的样本。

Quick Heal的报告仅仅是为这类攻击提供了一个新的视角，但是情况却发生了变化:CNN-News18是一个印度的印度英语新闻电视频道，这家公司的网站发表了一篇文章:"Cyber Warfare: China Is Helping
Pakistani Hackers Launch Cyber Attacks on India"：

![](https://images.seebug.org/content/images/2021/09/2403550c-6e74-49f9-aeb9-392f1d5c20af.png-w331s)

于是乎这些攻击变成了可疑的巴基斯坦黑客组织所为，并且是"中国帮助了巴基斯坦的"透明部落(Transparent
Trib)"APT组织发起了Operation SideCopy。

### 2.3 2021年:伤痕累累的大象

#### 2.3.1 钓鱼网站和njRAT

2021年，我们发现了一个伪装成印度政府官方网站。这个网站的地址是http[:]//149[.]248[.]52[.]61/webmail.gov.in/verification/KAVACH。在这个网站一个目录下的文件如下:

![](https://images.seebug.org/content/images/2021/09/bc699f86-7bdc-4400-be7f-811b2ec826d7.png-w331s)

受害者的密码被保存在一个名字为doublegoli2.txt的文件中，不过在我们查看了这个文件后，我们发现几乎没有人在这个页面上输入账户和密码。在继续进行时分析时，我们发现了多个与这个IP通讯的样本。部分样本的原始文件名与印度的军队和疫情相关:

  * Indian Army Restructring And Re-Organization.pdf.exe

  * Phase-3 of Nationwide Covid-19 Vaccination Registration.pdf.exe

  * director_general_level_border_coordination_conference.pdf.exe

  * covid-vaccination-approved-for-kin-of-armed-forces-personnel-veterans-in-service-hospitals.exe

这些文件都是winrar的自解压程序，它们运行后会释放出诱饵文档和恶意代码。其中的一个文件解压后如下:

![](https://images.seebug.org/content/images/2021/09/ad3c2a25-a120-4488-93f9-458b4902b1b7.png-w331s)

解压出来的PDF是来自于印度的一个政府网站:

![](https://images.seebug.org/content/images/2021/09/c2df0602-4e69-4eaf-b6e2-76b390250ec4.png-w331s)

Phase-3-of-Nationwide-Vaccination-Registration_pdf.exe释放出来的名字为winhosti.exe的文件是njRat的一个变种,文件中包含一个PDB路径:

D:\RATS\njRAT-0.7d-Stub-CSharp-master\njRATC#Stub\njRATC# Stub-backup\obj\x86\Debug\winhosti.pdb

通过搜索我们在github上找到了相关的源代码:

https[:]//github.com/NYAN-x-CAT/njRAT-0.7d-Stub-CSharp/tree/master/njRAT%20C%23%20Stub

不过项目的名字发生了变化，github上的项目名是"Lime",winhosti.exe中则变为"Ralinet":

![](https://images.seebug.org/content/images/2021/09/cab45608-930b-4dd6-8ce5-7c1ac0e33ebb.png-w331s)

除了上面的样本外，我们发现一些伪装成私有VPN APP的样本。名字为Kavach-Release-win.exe的文件解压后如下:

![](https://images.seebug.org/content/images/2021/09/51bd26d7-993b-425d-abe3-fbf6b31b840b.png-w331s)

go.vbs会打开链接:https[:]//kavach.mail.gov.in。通过网上公开的操作手册，我们了解到:登录kavach.mail.gov.in网站后可以下载认证工具，通过认证工具可以直接访问mail.gov.in所在的系统。释放出来的winhost.exe是一个旧版本的njRAT,它的C&C同样是149[.]248.52.61，不过这个文件并不包含PDB信息。

我们还发现了一个名字为10298-VPN-Win-10.exe的文件这个文件伪装成VPN的客户端程序，部分代码如下:

![](https://images.seebug.org/content/images/2021/09/865e8f3d-3c8f-42a8-b2bf-f860d653b040.png-w331s)

它会打开https[:]//vpn.nic.in/链接，造成访问正确网站的假象。然后在后台解密并释放%APPDATA%\inithost.exe，同时将其加入到开机自启动项。释放出来的inithost.exe是一个截屏程序，并且这个程序可以自动更新：

![](https://images.seebug.org/content/images/2021/09/f35acee3-234f-41e5-864c-1e2c8a054272.png-w331s)

10298-VPN-Win-10.exe中包含的PDB路径如下:

G:\VP-S-Fin\memory\encrypt-decrypt-byte-encrypted\encrypt-decrypt\obj\Debug\solaris.pdb

inithost.exe 中包含的PDB路径如下:

G:\VP-S-Fin\Margulas\Client\obj\Debug\solaris1.pdb

在我们分析完以上样本后，我们意外发现一个lnk文件和149[.]248[.]52[.]61有关联。最早发现的lnk文件的名字为:Cir-Bfg-Int-May21-Summary.docx.lnK。这个文件的执行流程如下:

![](https://images.seebug.org/content/images/2021/09/701bcf5c-2de0-4df7-a4cc-9ff77ce87b15.png-w331s)

下载下来的updtsys.exe中包含的PDB路径如下:

D:\RATS\njRAT-0.7d-Stub-CSharp-master\njRAT C# Stub\njRAT C# Stub-backup\obj\x86\Debug\wintask.pdb

#### 2.3.2 再次相遇

名字为Cir-Bfg-Int-May21-Summary.docx.lnK的文件中包含一个链接:https[:]//www[.]imenucard.com/fcm/files/ALMT-OF-TT&IEG-2021/css/word.ico,这个链接指向的是一个winword的图标。我们发现了[www.imenucard.com](www.imenucard.com)上存在另外一个hta文件:http[:]//imenucard.com/fcm/files/xmlk/css.hta。我们点开后发现了熟悉的代码:

![](https://images.seebug.org/content/images/2021/09/3de1f246-b45f-4e72-9263-8a808a40aef0.png-w331s)

这个LNK中包含一个MachineID字段，该字段的值是"desktop-g1i8n3f"。通过关联我们找到了另外几个与之相关的文件:

文件名 | MD5  
---|---  
DATE-OF-NEXT-INCREMENT-ON-UP-GRADATION-OF-PAY-ON-01-JAN-AND-01-JUL.pdf.lnk |
2d486754b4e2060db77f212da0c6f  
Call-for-Proposal-DGSP-COAS-Chair-Excellance.pdf.lnk |
261fa3263efc672ed853c7b327b64d70  
Covid Vaccination.pdf.lnk | 0330753edb0026e847052f6faffe3243  
Covid Vaccination On Emergency Basis for All Employees and their
Familes.pdf.lnk | ced4a3d54c12ff49b5b9bd562d935b3c  
Image__7563.jpg.lnk | 265598226b93803f67cee5fc2dc8199f  
  
这些文件lnk的执行流程和Cir-Bfg-Int-May21-Summary.docx.lnk有所差异，比如DATE-OF-NEXT-INCREMENT-ON-UP-GRADATION-OF-PAY-ON-01-JAN-AND-01-JUL.pdf.lnk文件的执行流程如下:

![](https://images.seebug.org/content/images/2021/09/b747f7b4-bee7-43b4-b040-faba31bb46d0.png-w331s)

LNK文件首先会下载一个HTA文件，这个文件中包含两个经过base64编码的字符串。其中一个是反序列化的.NET模块，解码后会调用其导出的函数。这个模块中类的定义如下:

![](https://images.seebug.org/content/images/2021/09/60772444-e63a-4441-9783-f13fa09a9109.png-w331s)

与2019年的hta.dll相比，新的模块在函数上又发生了变化。这次调用的是RealityShow,这个函数的定义如下:

![](https://images.seebug.org/content/images/2021/09/6605cd14-cd91-41c5-a7c9-f9cb2ba6e6e6.png-w331s)

data字符串经过base64编码并且GZIP压缩，RealityShow会先解码和解压缩这个字符串并写入一个PDF文件中，然后打开这个文件。

接着RealityShow会调用getThridStrike函数:

![](https://images.seebug.org/content/images/2021/09/f5b63739-6afd-45f7-aa06-d33fdbcb9f0b.png-w331s)

getThridStrike
会从https[:]//londonkids.in/echoolz/assets/css/front/hwo/css/下载一个HTA文件，这个文件中包含一个反序列化的.NET模块，这个模块的名字为prebothta.dll。HTA文件首先会遍历系统中的杀毒软件，然后将杀毒软件的名字传入到prebothta.dll的PinkAgain函数。prebothta.dll中的类的定义如下:

![](https://images.seebug.org/content/images/2021/09/8b860a67-8692-4338-bd8d-67c41cfc8fbe.png-w331s)

和2019年的样本相比，针对杀软而采取不同释放文件策略都不见了。每个前缀为active的函数执行逻辑是一样的，pinkAgain函数变成了4个参数，最后一个参数是是要释放的可执行文件的名字，这个名字根据杀软的类型来决定。我们目前发现这个值好像是固定的。PinkAgain函数会根据当前系统中的杀软名字来决定释放文件的方法。不论当前系统中安装了什么类型的杀软，代码的执行逻辑都是一样的。最终用都是调用CopyExeAsTxt函数，CopyExeAsTxt会解码和解压传递进来的字符串然后在Statrtup目录释放一个名字为winstr.jpg的文件，然后将winstr.jpg重命名为winstr.exe。相关代码如下:

![](https://images.seebug.org/content/images/2021/09/feed55d7-94dc-4c5e-a3b9-b6fac6df3a27.png-w331s)

释放出来的文件的原始文件名是officetool.exe,这个文件的功能是定期的更新恶意代码。如下图:

![](https://images.seebug.org/content/images/2021/09/9c06e31c-1fe3-4636-b591-a6173b916a1b.png-w331s)

main函数的如下代码如下:

![](https://images.seebug.org/content/images/2021/09/f7fd7ef0-1986-4ada-a8d2-3f3159b5d236.png-w331s)

GetThridStrike
还会从https[:]//londonkids.in/echoolz/assets/css/front/hwo/html/下载一个HTA文件，将其命名为duoApp1.hta,然后执行这个文件。

duoApp1.hta会释放出来 DUser.dll,streg.bat,
winidr.exe。同时duoApp1.hta还会将系统文件credwiz.exe拷贝到C:\ProgramData\AnyDeks\credwiz.exe。winidr.exe仍然是一个使用Delphi开发的开源backdoor,这一点没有变化。

![](https://images.seebug.org/content/images/2021/09/c64c8450-1a6a-4235-95be-42571d8b7c3b.png-w331s)

#### 2.3.3 我们发现了一个”巢穴“

就在我们即将写完报告时，我们发现了mmfaa[.]ddns[.]net网站。这个网站的主页伪装成阿富汗的新闻网站。仔细观察源代码后，我们发现页面中的内容是固定的,很多链接是不会变化。

我们探测到这个网站有三个特殊的目录：

  * https[:]//mmfaa[.]ddns[.]net/test

  * https[:]//mmfaa[.]ddns[.]net/classifieds

  * https[:]//mmfaa[.]ddns[.]net/classification

在这三个目录下都存在相同的C&C server 框架。从登陆界面显示判断这套C&C server
框架似乎叫"Crusade"。这三个目录下都存在tmp、downloads目录。tmp主要是存放一些木马文件，downloads则存放的是受害者的电脑上的文件。这些文件包括一些图片，文档，键盘记录日志等。

我们还发现了其他类似的目录：

  * http[:]//mfahost.ddns.net/classical/

  * http[:]//164.68.108.22/cruisers/

  * http[:]//164.68.108.22/crus/

  * http[:]//mffatool.ddns.net/knightrider/

  * http[:]//173.212.224.110/krowd/

在这个网站的classifieds\temp目录下，我们发现了大量的样本。这个目录中包含的winidr.exe文件正是我们前面分析的文件。

在这些文件中我们发现了6个HTA文件，从这些HTA文件中我们发现了至少3个prebothta.dll的变种:

![](https://images.seebug.org/content/images/2021/09/84c42e9e-3a42-4271-a4c3-fb4fa04ecfa3.png-w331s)

这些变种的发现也改变了我们一些认知，在此之前我们一度怀疑是不是有多个不同的组织在使用这套TTPs。C#开发的程序很容易反编译，有一定技术能力的攻击组织可以重新利用这些代码。在同一个服务器上发现了这么多的变种改变了我们的判断。

这些目录中包含了很多的恶意代码，这些恶意代码也一定程度上反映了这个组织在变换自己的攻击手法。从部分PDB路径就可以快速的识别恶意代码的功能:

D:\Projects\C#\Chromer\Chromer\obj\Debug\charmi.pdb
C:\Users\Monkey\source\repos\hijacker\Release\MeterPreter.pdb
C:\Users\nomi\Desktop\ReverseShell\Release\ReverseShell.pdb
c:\Users\Zombie\Desktop\ReverseRat
client\ReverseRat\ReverseRat\obj\Release\svchostt.pdb D:\Projects\C#\HTTP-Simple\WindowsMediaPlayer - HTTP - 02-23-2021
Current\WindowsMediaPlayer10\obj\x86\Release\winow4.pdb

值得一提的是winow4.exe是一个C#开发的远控，它伪装成播放器。部分代码代码如下:

![](https://images.seebug.org/content/images/2021/09/661cc396-f3e0-4eea-aa4e-1c36a2cf0ec2.png-w331s)

关键代码如下：

![](https://images.seebug.org/content/images/2021/09/3bfe5163-6088-4a3a-8947-5d3c22521210.png-w331s)
![](https://images.seebug.org/content/images/2021/09/ca57319c-5457-4902-829f-9a8d23bbf135.png-w331s)

我们发现一个名字为winow.exe的文件，这个文件使用delphi语言开发。它的功能和C#开发的winow4.exe的功能是一样的，部分代码如下：

![](https://images.seebug.org/content/images/2021/09/6752298a-0368-4b32-ba4c-83d304a0b3b4.png-w331s)

这个网站的目录下存在多个我们前面提到了名称为“AllaKore_Remote“后门的变种，这些变种大多数的文件名字大多是以"win"开头，但有一个变种的文件名是"Cyrus_Client.exe",我们推测攻击组织对这个后门的命名应该是"Cyrus"。我们观察到卡巴斯基对这个后门的变种所报的病毒名为"HEUR:Backdoor.Win32.Cyrus.gen"。

我们还在这个网站上发现了一个受害者的列表：

![](https://images.seebug.org/content/images/2021/09/d9d45e18-19aa-47f4-b11c-b18af9994c06.png-w331s)

这些数据都是2019年到2020年间收集的，受害者有100多个。对这些IP统计后发现受害者大部分位于阿富汗，有少量的印度、巴基斯坦、中国等国家。

## 3\. 结论

从目前观察的情况判断，Cyrus
APT组织主要针对的对象是印度和阿富汗。我们没有找到针对巴基斯坦及其他南亚国家的直接证据。域名是mmfaa[.]ddns.net的网站伪装成一个阿富汗的新闻网站，这个网站的IP是144[.]91.65.100。这个IP曾经和域名newsindia.ddns.net、www[.]afghannewsnetwork[.]com、afghannewsnetwork.com相关联。这个网站在2020年就存在，两家印度的安全公司都曾经在报告中提及144[.]91.65.100这个IP。推特上有个安全研究者对newsindia[.]ddns[.]net、www[.]afghannewsnetwork[.]com表示很困惑，因为这一些列的攻击和"SideWinder(响尾蛇)"APT组织太像了。但是"SideWinder(响尾蛇)"APT组织却被认为是来自于印度，甚至被认为是有"印度政府背景"。

Cyrus APT组织和"SideWinder(响尾蛇)"APT组织的主要区别如下：

  * Cyrus APT组织使用的C&C服务器的域名主要是印度的域名。部分网站看起来是真实的的网站，部份看起来是伪装的网站。

  * Cyrus APT组织使用的攻击技术是"SideWinder(响尾蛇)组织所用的攻击技术的前两种，第三种则从来没有出现过（细节请参考我们关于"SideWinder(响尾蛇)组织的报告）。

  * Cyrus APT组织的样本释放出来的DUser.dll通常是一个delphi开发的程序，偶尔有C#开发的。"SideWinder(响尾蛇)"APT组织使用的DUser.dll有C++开发的，后期大多是C#开发。

  * Cyrus APT组织最后的payload是使用delphi开发的开源木马，这个木马可能在内部叫"Cyrus"。

  * prebothta.dll和hta.dll中使用gzip解压后的数据的前四个字节表示解压后数据的大小。"SideWinder(响尾蛇)"APT组织的样本中gzip解压后的数据不存在这个字段。

  * Cyrus APT组织拥有更多的攻击武器，同时更新武器的速度比"SideWinder(响尾蛇)"APT组织要更加快。

在6月份，Cyrus
APT组织更换了服务器，起用一个afghannewsnetwork[.]com的域名。同时我们发现该组织开始使用golang开发后门了。

值得注意的是一些目录和文件的名字如：classical，classifieds，classification，crus，cruisers，cyrus,crusade，
knightrider,
krowd。另外mmfaa[.]ddns[.]net网站上的数据库中有两个账户名疑似是两个知名足球明星的名字。这些信息没有在"SideWinder(响尾蛇)"APT组织的攻击中发现，它们可能对描绘攻击者的形象有帮助。

如果在google中搜索”DraftingPad”会弹出相关的搜索，其中有一条是” drafting pad price in
pakistan”。我们当然不是在暗示这个组织来自于巴基斯坦。

部分安全厂商和安全研究者将这类攻击归于”透明部落(Transparent Tribe
)”APT组织，但是我们研究之后没有发现出它们之间有较强的联系。目前我们倾向于这是一个活跃于南亚国家的一个新的APT组织。

## 4\. IOC

**MD5:**

7fc510a92848ec9ffc92cdaff897de0c Indian Army Restructring And Re-Organization.pdf.exe

d33dec279966da2024c05d5fde688253 Phase-3 of Nationwide Covid-19 Vaccination
Registration.pdf.exe

fcae8c3823eecebb9b8e0f9f2b9eeb89
director_general_level_border_coordination_conference.pdf.exe

a3e614d1a2956cde029cb3ce1b499d12 Kavach-Release-win.exe

4f1c460608a80b82094bf9c87f31e032 covid-vaccination-approved-for-kin-of-armed-forces-personnel-veterans-in-service-hospitals

8ff555dea1402789ef19afa7efd06c76 sigma.exe

6743e3521bb2e738ae850e6d270057b9 solaris.exe or 10298-VPN-Win-10.exe

4b792b700f7c833d22f6a819175eb3bb Cir-Bfg-Int-May21-Summary.docx.lnk

261fa3263efc672ed853c7b327b64d70 Call-for-Proposal-DGSP-COAS-Chair-Excellance.pdf.lnk

2d486754b4e2060db77f212da0c6f9ff DATE-OF-NEXT-INCREMENT-ON-UP-GRADATION-OF-PAY-ON-01-JAN-AND-01-JUL.pdf.lnk

0330753edb0026e847052f6faffe3243 Covid Vaccination.pdf.lnk

265598226b93803f67cee5fc2dc8199f Image__7563.jpg.lnk

ced4a3d54c12ff49b5b9bd562d935b3c Covid Vaccination On Emergency Basis for All
Employees and their Familes.pdf.lnk

e55688a62991e86707864e97006af162 Posting (AllTypes), Promotions, and Other
Record Wing Matters.pdf.lnk

e49c1608e52aa1d49067c12b21032176 Tele Directory RSBs ZSBs

e05468aaa0c436e953116989ccf9703b United_States_Project_for_Promise.pdf .lnk

c22e74462f1c79ef0bc2de0e09d7f28d [My-CV.docx
.lnk](https://www.virustotal.com/gui/search/name%3A%22My-CV.docx%20.lnk%22)

**IP:**

149[.]248[.]52[.]61

144[.]91[.]65[.]100

194[.[163[.[139[.]250

**URL:**

https[:]//ikiranastore.com/images/files/ist/doc/abc.hta

https[:]//ikiranastore.com/images/files/ist/doc/i.php

https[:[//ikiranastore.com/images/files/ist/doc/

https[:]//ikiranastore.com/images/files/ist/doc/Cir-Bfg-Int.docx

https[:]//ikiranastore.com/images/files/ist/doc/tingo7.rar

https[:]//iiieyehealth.com/fonts/times/files/Call-for-Proposal-DGSP-COAS-Chair-Excellance/css/

https[:]//iiieyehealth.com/fonts/times/files/Call-for-Proposal-DGSP-COAS-Chair-Excellance/css/pdf.ico

https[:]//iiieyehealth.com/fonts/times/files/Call-for-Proposal-DGSP-COAS-Chair-Excellance/css/css.hta

https[:]//iiieyehealth.com/fonts/times/files/Call-for-Proposal-DGSP-COAS-Chair-Excellance/css

https[:]//cfl.dropboxstatic.com/static/css/error.css

https[:[//londonkids.in/preschool/video/Emergency_Vaccination/css/

https[:[//cfl.dropboxstatic.com/static/images/illustration_catalog/409_unsupported-browser-illo.png

https[:[//minervacollege.co.in/fonts/plugins/mrt/Image-7563/css2

https[:[//minervacollege.co.in/fonts/plugins/mrt/Image-7563/css2/pic.ico

https[:[//londonkids.in/admin/plugins/ckeditor/skins/moono/images/hidpi/EngrCoprsMatters/css/

https[:[//selforder.in/wp-content/uploads/wp-commerce/04/05/hzk/xml/

https[:[//selforder.in/wp-content/uploads/wp-commerce/04/05/hzk/html/

https[:[//selforder.in/wp-content/uploads/wp-commerce/04/05/hzk/Tele-Directory(RSBs-ZSBs)/css/

https[:[//selforder.in/wp-content/uploads/wp-commerce/04/05/hzk/html/jquery.txt

https[:[//selforder.in/wp-content/uploads/wp-commerce/04/05/hzk/Tele-Directory(RSBs-ZSBs)/css/css.hta

https[:[//selforder.in/wp-content/uploads/wp-commerce/04/05/hzk/html

https[:]//selforder.in/wp-content/uploads/wp-commerce/04/05/hzk/xml/css.hta

http[:]//167.86.75.119/h_tt_p

https[:]//dadsasoa.in/font/js/images/files/United-States_Project_for_Promise/css/

https[:]//dadsasoa.in/font/js/images/files/My-CV/css

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1721/>

