# AirHopper：使用无线电突破独立网络和手机物理隔离（下）

阅读量 **181372**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-01-23 11:30:47

 **x**

##### 译文声明

本文是翻译文章，文章原作者 arxiv.org

原文地址：[Mordechai Guri](Mordechai Guri)

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t01c5dd5c75318dbff4.jpg)

## 传送门

[AirHopper：使用无线电突破独立网络和手机物理隔离（上）](https://www.anquanke.com/post/id/95429)

## 5.隐身

为了在传输过程中保持隐身，AirHopper使用多种技术来实现视觉和被传送信号的隐身。

###  5.1 视觉隐身

本节将解释如何在电脑屏幕上实现所传输数据的视觉化隐身。推荐的三种技术利用的是配有附加显示器的标准化通信方式。HDMI、DVI和VGA
显示器以及VDU（视频显示单元）采用的是显示数据通道（DDC）协议族 。

显示数据通道命令接口（DDC/CI）本身是计算机显示器和VDU之间的一种双向通信协议。显示器控制命令集（MCCS）是一种由视频电子标准协会（VESA）制定的标准，特指通过DDC/CI通信协议控制显示器的命令集。

####  5.1.1 在显示器关闭状态下发射信号

通过使用DDC/CI，发射器能够在确定显示器处于关闭后才开始发射信号。当计算机在预定期间内处于空闲状态时，显示器会因为电源的节能设置而进入关闭状态。一旦发射器检测到显示器重新开启，它就会停止发射信号。需要注意的一点是，由于VDU会不断产生信号，而显示器电缆仅作为天线加以使用，因此信号传输只会在显示器关闭的状态下有效进行。从技术上讲，通过检查DDC/CI的电源控制状态（地址
0xe1）可以确定显示器的状态。发射器对这一状态进行持续采样，并同时在一个专用线程中对ioctl（I/O控制）进行顺序询问。0 表示屏幕处于关闭状态。

####  5.1.2 关闭显示器

通过使用
DDC/CI，传输代码也可以发送有意关闭显示器的命令。这种方法可以同样应用于屏幕保护程序；代码能够监视用户的计算机活动，并等待一段空闲时间。如果计算机处于闲置状态，它将关闭监视器并启动数据传输，直至检测到出现相关活动（如移动鼠标或敲击键盘）。然后它将停止数据传输并重新打开显示器，所有的表现都和正常的屏幕保护程序或电脑节电功能相同。与前面的方法类似，通过使用
ioctl 编写1或0至0xe1，完成打开或关闭显示器的操作。

####  5.1.3 将显示器切换到另一台计算机

在用户电脑屏幕上实现所显示图像隐身的另一个方法是利用通用的键盘视频鼠标（KVM）切换器。KVM开关是一种可以允许桌面基本外围设备、键盘鼠标和显示器在多台计算机之间共享的设备。通过单击KVM切换器上的一个按钮或使用键盘组合键，用户就可以在不同电脑之间切换。由于KVM切换器允许用户在一张办公桌上舒适地使用多台计算机，通常用于拥有物理隔离网络的企业。通过使用DDC/CI，发射器可以检测出KVM在不同计算机之间切换的时间，并据此相应地开始或停止传输数据。

####  5.1.4 使用辅助显示输出

本文测试的另一种方法是：迫使VDU在某个特定的视频输出上进行数据传输，即使它没有检测到可连接的显示器。当一台计算机（笔记本电脑或台式机）有多个显示输出时，这一功能将会非常有用。传送的代码可以检测到当前正在使用的是哪一个视频输出，并将传输重定向至某个闲置输出。由于大多数情况下只有一根显示电缆处于连接状态，而在没有显示电缆作为天线的情况下进行数据传输要求与接收器保持极近的距离，因此该方法仅适用于使用者将其手机放置在紧靠笔记本或台式机的情况下。另一种情况是，当笔记本电脑或台式机在会议室中使用时，其与投影仪之间拥有辅助的持久性连接。由于投影仪输出在大部分时间内处于关闭或连接断开状态，因此为进行长时间的数据传输提供了不易为人所觉察的良好机会。我们的测试也表明，通常用于连接投影仪的非屏蔽式长电缆也十分适用于高质量传输，且可以通过相邻房间里的手机予以接收。

###  5.2 信号隐身

另一种检测风险是被传输信号的意外接收情形。由于调制传输数据的系统使用的是可听的音调频率，因此如果将一台常规的FM接收器调到用于传输的载波频率，则会生成可能引起嫌疑人警惕的音调。为了减少这种被意外检测到的风险，我们将手机的FM接收频段扩展至
76MHz-108MHz，将传输载波频率调整至80MHz。

只有极少数国家（如日本）在76MHz～87.5MHz之间进行FM传输。世界其他地方的大多数FM接收器不允许在这个范围内进行收听或搜索无线电信号。然而，我们发现，虽然手机的FM芯片实际上支持非标准范围，但上层的软件层却对此加以禁用。通过在扩展范围中进行数据传输，可以在大多数国家中避免被偶然发现。在接收手机上，我们通过使用smali反汇编程序修改Samsung框架，从而扩大接收的频率范围[17]。从技术上讲，该框架文件位于
/system/framework目录下。通过将BAND_76000_108000_kHz的值设置为
1，我们对com.android.server数据包中的FMRadioService类进行了更改。这种在操作系统级代码上的更改无法被手机用户所察觉。与此同时，使用一个非标准的频段既有助于避免与当地的无线电广播产生冲突，也可以允许使用更广泛的可用传输频率。另一种防止被意外检测到的方法是改变手机的频率搜索间隔，将从默认的200KHz改为50KHz。这允许发送器和接收器代码微调到许多FM接收器不允许对普通用户开放的载波频率，从而避免遭遇意外检测的风险。

## 6\. 评估

在本节中，我们将评估假定的数据攫取方法的可行性和有效性。用于提高效率的主要措施包括发射的信号强度、有效的广播距离、传输速率、传输质量、电池消耗和扫描时间。影响因素包括电缆类型、接收机天线存在与否、调制方法（A-FSK或DTMF）、载波频率、信号延时、所发送的数据大小以及发送频率的范围。在给出相关实验设置的简短描述之后，下文进一步解释了用于提高效率的多种措施及其影响因素，阐述了它们之间的相关性。

###  6.1 实验设置

所使用的显示器是三星SyncMaster SA450。操作系统是64 位Ubuntu
13.04（代号raring）系统，内核为3.8.0-29-generic。

手机是三星 GT I9300 Galaxy S3。Android版本是三星 stock 4.1.2。基带版本是 I9300XXEMC2。内核版本是
3.0.31-1042335。无线电芯片是芯科实验室Si4705 FM无线电接收器IC。我们使用的是手机标配的 1.22 米（4
英尺）立体声耳机。需要注意的是，在这款手机中，耳机被用作 FM 接收器的天线。

我们使用四种类型的电缆来连接计算机的显示器：（I） 标准VGA电缆，1.52 米（5 英尺）、30V、接口类型15pin、正极对正极； （II）
标准VGA电缆，0.91 米（3 英尺）、HD15、正极对负极，通常用来作为投影仪延长线；（III） HDMI电缆，0.91 米（3
英尺）、30V。（IV） DVI 电缆，1.82 米（6 英尺）、30V。下文将这些缆线分别简述为标准VGA、扩展 VGA、HDMI和DVI。表 1
提供了电缆类型的相关分类（即屏蔽/非屏蔽、 模拟/数字）。

**表1 电缆分类**

###  6.2 信号强度

随着与发射器之间的距离逐渐增加，接收到的信号强度预计将会逐渐下降。我们测量了不同距离处的接收信号强度指示 （RSSI）（见 图 3）以及
dBm（毫瓦分贝，见图 4）。RSSI通常是由芯片API显示的信号质量指标。RSSI 的测量可以通过调用IFMPlayer的getCurrentRSSI
函数完成，其隶属于 FM 收音机播放器内置的一项三星公司服务。可以使用外置的频谱分析仪测定 dBm 的值。RSSI
的测量显示值与有效距离相关；若RSSI刻度上的测量值为10，则大致表示每根被测电缆的有效距离限值。

图3 使用A-FSK时，不同距离处的信号强度（RSSI）。  
（由移动电话的FM接收器测得）

图4 使用A-FSK时，不同距离处的信号强度（dBm）。  
（由外置的频谱分析仪测得）

###  6.3 有效距离

有效距离是发射器和接收器之间的最大距离，此时的传输质量仍处于可接受的程度。从图 5 中可以看出，使用接收天线时，非屏蔽电缆（扩展
VGA）的有效距离会显著大于屏蔽电缆（HDMI 和标准 VGA）。总而言之，当接收天线存在时，这两种类型电缆的有效距离大约为8~20
米，符合我们的实验要求。  
一些新型号的手机都配备了内置的FM天线，则不再需要使用耳机。

图5 使用A-FSK时，不同距离处的信号强度（RSSI）。

###  6.4 数据调制方法

信号发送方法（即 A-FSK或DTMF）也会对有效距离产生一定的影响。从图 6中可以看出，A-FSK能够产生的有效距离稍长一些。

图6 使用A-FSK和DTMF时，不同类型电缆在有接收天线的情况下的有效距离

###  6.5 传输质量

传输质量（也指“成功率”）表示的是每原始发送字节中正确接收到的字节比率。这一比率采用不同的信号延迟加以衡量，即为传输一个字节所分配的数据时间间隔
（以毫秒为单位）。

如图7
所示，传输质量和信号延迟之间的相关性呈对数关系，逐渐接近100%。若信号延迟超过70ms，额外的传输质量似乎可以忽略不计。之所以将延时时间设置为70ms较为合理，其原因是延迟时间越长会导致传输速度变慢，以致无法明显地改善传输的质量。

图7：使用DTMF时，不同信号延迟情形下的传输质量

正如表格2所示，我们测量了每种类型电缆在不同距离处的传输质量（或成功率）。信号延迟为最优值70
毫秒。该表中显示的测量值为0.3m、6.2m以及传输质量处于可接受程度下的最大距离（或有效距离）处的传输质量。可以看出，不同类型电缆的最大距离值不同。

表 2 中的数值反映的是传输质量；在达到最大距离之前（因电缆类型的不同而有所差异），这一数值随着距离的增大几乎保持在固定不变的高数值上。

**表 2：使用DTMF时不同距离处的传输质量**

![](https://p5.ssl.qhimg.com/t01228040fd993f1f80.png)

###  6.6 数据大小

有效的数据攫取行为将实际限制放置在传输时间上。在被入侵的计算机上运行的传输程序应隐藏自身的活动，限制所收集数据被广播的安全时间间隔。此外，接收手机不会无限期地处于发射器的有效范围内。

在表格3中显示了各种类型文件（典型大小）使用原始数据或结构化数据包传输方式时所需的传输时间（如“实施”一节中所描述的）。实验发现，70ms延迟是最佳的选择。传输极少量数据（100
字节以下，如IP&MAC或密码）所需的时间少于10秒，这看来还可以接受。传输少量数据（10 KB以下，如系统信息或单日键盘记录）
将需要几分钟的时间，这似乎也可以接受。然而，传输约0.5 MB 大小的文件将花费数小时时间，这似乎是不能接受的。

**表格 3：不同数据大小的传输时间（70毫秒延迟）**

![](https://p0.ssl.qhimg.com/t0123270c9cc1004fbf.png)

## 7\. 应对策略

之所以将延时时间设置为70ms较为合理，其原因是延迟时间越长则会导致传输速度变慢，以致无法明显地改善传输的质量。技术型对策包括 （a） 物理隔离、（b）
基于软件减少所载信息的发射量和 （c） 信号的早期加密。

程序型对策包括官方的规范和标准，以及法律或组织的支持。与Tempest相关的美国和北约标准在整个冷战期间都属于高度机密信息。虽然最终有部分标准得以泄露或公开发布，但亦遭到严重删减，而更多的信息文件，特别是涉及防御对策的文件仍属于机密一类[18]。现行标准的目的在于限制户外给定距离下、或使用绝缘材料时对等情况下可检测的调制RF信号的水平。实际上，合格的设备将按照“地区”进行分类，即指需要加以控制以防止接收信号的边界[19]。作为应对类似本研究中攻击的一种对策，
“地区”划分方法应该用于指定机构内部的物理区域，在此区域内禁止携带手机或其他无线电接收器。另一个对策是确保使用唯一的正确屏蔽电缆。正如我们的实验所示，屏蔽可以对有效范围产生影响。

## 8\. 相关工作

谈及信号的发射安全 （Emsec），Anderson在其文[19]中给出了极为详实的叙述：应预防使用传导或辐射的电磁信号构成的泄密发射攻击。1985
年，van Eck[11] 演示了如何使用相当普通的设备和技能来生成Tempest漏洞。

通过使用一台改进的电视机，他设法重现了一幅由远距离处的视频显示单元（VDU）所生成的电磁信号构成的图像。20世纪90年代后五年内，一些与Tempest有关的研究和出版物[12][13]极大地增加了公众的兴趣。这一趋势继而被网络加以扩大，网络或是提供了一个窥探Tempest[18]保密性官方标准的机会，或是提供了有关Tempest的详细说明和指南[14]。Kuhn和Anderson[12][13]表示，无论采用防守还是进攻的方式，目前都可以经由合适的软件操作在一台PC上实现众多泄密发射。Thiele[14][20]提出了一份名为“Tempest
for
Eliza”的开源项目，尝试使用电脑显示器发射AM无线电信号。随后，所生成的音乐可以经由某个电台予以接听。Kania[15]通过软件程序集生成FM无线电信号，然后使用一个VGA显卡加以发送。在我们的实践中，为了提高信号的质量，我们通过使用不同的技术来生成FM信号。

## 9\. 结论

从物理隔离网络中攫取数据并不是一项简单的任务。但我们在本文中所阐述的AirHopper分支型攻击模式却能够成功完成这一富有挑战性的任务。该方法的核心由两个基本要素组成：（a）
基于计算机显示器电缆中发出的电磁信号进行有意地数据调制；（b）
手机中的FM接收器可以收集传输的信号，并提取调制的数据。整个过程的攻击链虽然相当复杂，但并没有超过现代高级持续性威胁（APT）所采用的技能和操作水平。所提出的评估方法包括诸如有效传输距离、电缆型号、
接收器天线存在与否等多种方法的实验性测量情况。

AirHopper增加了对电磁发射威胁以及APT技术的了解。近期的学术文献尚未对这一研究领域进行充分的讨论与探究。本文认为，针对这种威胁所进行的专业和学术的讨论，最终将满足社会在网络防御方面的利益需求。

## 参考文献

[1]Nokia, “Nokia Corporation Interim Report for Q2 2013 and January-June
2013,” 2013.

[2]Gartner, “Gartner Says Smartphone Sales Grew 46.5 Percent in Second Quarter
of 2013 and Exceeded Feature Phone Sales for First Time,” 14 August 2013.
[Online]. Available: <http://www.gartner.com/newsroom/id/2573415>. [Accessed
15 September 2013].

[3]phoneArena.com, “phone finder,” 2013. [Online]. Available:
<http://www.phonearena.com/phones>. [Accessed 8 October 2013].

[4]M. Stroh, “Windows Phone Blog,” Microsoft, 14 May 2013. [Online].
Available:
<http://blogs.windows.com/windows_phone/b/windowsphone/archive/2013/05/14/nokia-s-first-metal-windows-phone-arrives-meet-the-sexy-lumia-925.aspx>. [Accessed 8
October 2013].

[5]National broadcaster association, “Equipping Mobile Phones with Broadcast
Radio Capability for Emergency Preparedness,” September 2013. [Online].
Available:
<http://www.nab.org/documents/advocacy/FMEnabledPhones/RadioEnabledPhonesIssueSheet.pdf>.
[Accessed 8 October 2013].

[6]Q. Z. P. R. B. T. Clark A., “An impact-aware defense against Stuxnet,” in
American Control, 2013.

[7]J. Larimer, “An inside look at Stuxnet,” IBM X-Force, 2010.

[8]W. J. L. III, Defending a New Domain, 2010.

[9]C. A. E. I. K. A. Hamandi K., “Android SMS Malware: Vulnerability and
Mitigation,” in Advanced Information Networking and Applications Workshops,
2013.

[10]R.-P. Weinmann, “Baseband Attacks: Remote Exploitation of Memory
Corruptions in Cellular,” in Usenix, 2012.This is a slightly revised version
of the paper accepted by the 9th IEEE International  
Conference on Malicious and Unwanted Software (MALCON 2014).20

[11]W. van Eck, “Electromagnetic Radiation from Video Display Units: An
Eavesdropping Risk?,” Computers and Security 4, pp. 269-286, 1985.

[12]M. G. Kuhn and R. J. Anderson, “Soft Tempest: Hidden data transmission
using electromagnetic emanations,” in Information hiding, Springer-Verlag,
1998, pp. 124-142.

[13]M. G. Kuhn, “Compromising emanations: Eavesdropping risks of computer
displays,” University of Cambridge, Computer Laboratory, 2003.

[14]E. Thiele, “Tempest for Eliza,” 2001. [Online]. Available:
<http://www.erikyyy.de/tempest/>. [Accessed 4 10 2013].

[15]B. Kania, “VGASIG: FM radio transmitter using VGA graphics card,” 19 4
2009. [Online]. Available: <http://bk.gnarf.org/creativity/vgasig/vgasig.pdf>.
[Accessed 4 10 2013].

[16]Google, “Android API: AudioRecord,” 02 11 2013. [Online]. Available:
<http://developer.android.com/reference/android/media/AudioRecord.htm>.
[Accessed 03 11 2013].

[17]”smali. An assembler/disassembler for Android’s dex format,” [Online].
Available: <https://code.google.com/p/smali/>.

[18]J. McNamara, “The Complete, Unofficial TEMPEST Information Page,” 1999.
[Online]. Available: <http://www.jammed.com/~jwa/tempest.html>. [Accessed 4 10
2013].

[19]R. J. Anderson, “Emission security,” in Security Engineering, 2nd Edition,
Wiley Publishing, Inc., 2008, pp. 523-546.

[20]E. Thiele, “Tempest for Eliza (updated Readme file),” 2004. [Online].
Available:
<http://www.olifantasia.com/projects/gnuradio/mdvh/videocard_rf_output/readme.fm.txt>.
[Accessed 4 10 2013].

[21]USAF, “AFSSI 7700: Communications and information emission security,”
Secretary of the Air Force, 2007.

本文翻译自 [原文链接](Mordechai Guri)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **张璐** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/95447](/post/id/95447)

安全客 - 有思想的安全新媒体

本文转载自: [](Mordechai Guri)

如若转载,请注明出处： [Mordechai Guri](Mordechai Guri)

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)
  * [AirHopper](/tag/AirHopper)
  * [无线电](/tag/无线电)

 **+1** __1赞

 __收藏

![](https://p4.ssl.qhmsg.com/dm/48_48_100/t01923d359dad425928.jpg?f=e7d531597a0bce2c56ec8531e36b9f1d)
张璐

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

