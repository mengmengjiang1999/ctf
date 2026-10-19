***本文作者：Yale1024，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

## 0x01 前言

**还有半年就毕业了，这段时间看自己的小本本，整理出之前练习过的一些经典的CTF题目，希望现在的萌新能通过练习这些题目事半功倍，更好地提升技术水平。本文包括一共4个题目，是流量取证方向，针对的是CTF中比较少见的一些协议，比如键盘、鼠标、无线、蓝牙、自定义的私有协议等等。**

## 0x02

2016年谷歌CTF一道200分的题目，针对的是USB鼠标的流量分析。这类题目在这几年不时被国内的出题人借鉴，不过本质还是掌握了几条关键的命令，之后都能秒flag，慢慢地就没有什么新意了。但是初学wireshark或者流量分析的萌新而言还是比较有意思的。

题目只给了数据包没有其他提示：

![](https://image.3001.net/images/20190221/1550758238_5c6eb15eb0469.png!small)

使用wireshark打开可以看到都是usb协议。

![](https://image.3001.net/images/20190221/1550758245_5c6eb16593863.png!small)

在第86条可以看到devicedescriptor。

![](https://image.3001.net/images/20190221/1550758252_5c6eb16c32e5f.png!small)

展开查看细节会发现这是罗技的一款鼠标。

![](https://image.3001.net/images/20190221/1550758259_5c6eb173314b3.png!small)

从第98条开始往下可以看到“USBInterrupt”并且这些数据包具有一些数据。

![](https://image.3001.net/images/20190221/1550758266_5c6eb17a1c841.png!small)

我们推测这是鼠标移动过程中，通过中断获取位置信息，怎么判断出是位置信息呢？

看下面几张连续的图就明白了：

![](https://image.3001.net/images/20190221/1550758272_5c6eb1806f10b.png!small)

![](https://image.3001.net/images/20190221/1550758279_5c6eb1879dc0d.png!small)

![](https://image.3001.net/images/20190221/1550758283_5c6eb18bd9c2e.png!small)

![](https://image.3001.net/images/20190221/1550758289_5c6eb1915c40e.png!small)

我们知道采集二维的数据，只需x,y坐标就可以了，上面的几张截图都是x,y交替着采集，至于数据，则在leftover capture data中变化着。

使用tshark从pcap-ng文件中提取了鼠标的数据。

数据量比较大，看最后10行稍微验证一下：

![](https://image.3001.net/images/20190221/1550758296_5c6eb1984dcee.png!small)

观察数据的变化，推测第二个、第三个字节即坐标变化，所以使用awk命令将其转换为坐标：

![](https://image.3001.net/images/20190221/1550758304_5c6eb1a00b345.png!small)

查看后10行转换出的数据：

![](https://image.3001.net/images/20190221/1550758309_5c6eb1a529356.png!small)

有了数据之后就可以使用GnuPlot来绘图了。

导入坐标所在的文件即可。

![](https://image.3001.net/images/20190221/1550758315_5c6eb1ab29e64.png!small)

生成的图像可以看到CTF字样，不过不太正常：

![](https://image.3001.net/images/20190221/1550758322_5c6eb1b294c5e.png!small)

镜像变化下即可，变化后得到flag。

## 0x03

HackIT
2017的一道题目，也是考USB的一道题目，不过这次是针对键盘的，而且结题需要参考USB键盘编码解码的规范，算是在流量取证的基础上加上了对新知识的获取、分析、利用的能力，以及考察快速编写脚本的能力。

使用wireshark打开数据包，发现还是一道USB的题：

![](https://image.3001.net/images/20190221/1550758331_5c6eb1bb46a33.png!small)

在第287条可以推测出这是采集键盘输入的数据：

![](https://image.3001.net/images/20190221/1550758336_5c6eb1c081f55.png!small)

该文件非常小，大多数是对按键进行编码的USB_INTERRUPT事件。

![](https://image.3001.net/images/20190221/1550758342_5c6eb1c64dc02.png!small)

和上一题类似的思路，可以先把Leftover Capture Data提取出来。

![](https://image.3001.net/images/20190221/1550758347_5c6eb1cbce52d.png!small)

使用下图的命令：

![](https://image.3001.net/images/20190221/1550758353_5c6eb1d194532.png!small)

得到的数据类似下图：

![](https://image.3001.net/images/20190221/1550758362_5c6eb1dac1596.png!small)

这些数据该如何解析呢？

查阅USB规范，下图的表格向我们展示了如何解码各个键：

![](https://image.3001.net/images/20190221/1550758369_5c6eb1e1ec695.png!small)

从图中可以知道A被编码为0x04，以此类推。

知道了编码规律之后就可以写脚本了：

![](https://image.3001.net/images/20190221/1550758377_5c6eb1e926172.png!small)

![](https://image.3001.net/images/20190221/1550758386_5c6eb1f27e9de.png!small)

输出的结果可能会有多种排列，在其中找到flag就可以了。

![](https://image.3001.net/images/20190221/1550758394_5c6eb1fa75225.png!small)

## 0x04

su-ctf
2016的一道题目，题目本身并不难，但是做习惯了TCP的protocol的题目后碰到802.11可能会有些懵，其实本质都是一样的，拿到flag要求能够意识到802.11无线协议的关键-路由器，进一步进行文件导出、解密等，这道题目还有种解法是使用aircrack进行破解，有兴趣的童鞋可以自行尝试。典型处理方法如下：

同样，先使用wireshark打开数据包，看到很多TP-LINk的流量，推测这是无线流量。

![](https://image.3001.net/images/20190221/1550758402_5c6eb20275e4c.png!small)

802.11不是很熟悉，不如先过滤出tcp协议来分析。

![](https://image.3001.net/images/20190221/1550758409_5c6eb2094448d.png!small)

选中一条tcp的，然后跟踪tcp流，可以看到通过GET命令请求名为rom-0的文件,左上角导出http对象保存即得到rom-0。

在上面的图中注意到特殊字符串Hdbgarea。

搜索引擎查一下：

![](https://image.3001.net/images/20190221/1550758415_5c6eb20f9e5d0.png!small)

第一条和路由器相关：

![](https://image.3001.net/images/20190221/1550758421_5c6eb215eb070.png!small)

点击下载链接下载后即可使用：

![](https://image.3001.net/images/20190221/1550758426_5c6eb21a58ed6.png!small)

解密后得到密码为Rome4040。

在wireshark中，依次Edit->Preferences->Protocols->IEEE802.11 -> Decryption Keys ->
New -> WPA-PWD，输入密码：

![](https://image.3001.net/images/20190221/1550758437_5c6eb2254e428.png!small)

点击ok后，有很多数据流就被解密。

![](https://image.3001.net/images/20190221/1550758443_5c6eb22bbb330.png!small)

有很多GET，但是只有一个POST，去看看这个POST。

![](https://image.3001.net/images/20190221/1550758457_5c6eb239e356d.png!small)

在报文里就找到了flag。

## 0x05

HITCON
2018的一道题目，这道题目比较新颖，而且有趣，容易把赛棍往弯路上个带，会花大量时间尝试隐写这一块的技术，dd、stego,binwalk,foremost等往上怼，后来才意识到题目考察的自定义的私有协议，非常有特点，算是考察到了流量分析的本质，而且考察选手的读写代码能力，对选手综合素质要求比较高。

题目给的是一个压缩文件。

解压：

![](https://image.3001.net/images/20190221/1550758467_5c6eb2432fcbd.png!small)

解压后得到两个文件。

图片长这样：

![](https://image.3001.net/images/20190221/1550758472_5c6eb2488c37a.png!small)

还有个pklg文件，可以使用wireshark打开。

![](https://image.3001.net/images/20190221/1550758478_5c6eb24e927c1.png!small)

pcap显示蓝牙流量，wireshark识别出了HCI_EVT、RFCOMM等协议。

等没听说过，咋整啊。

最开始解压拿到图片的时候，按照隐写术的办法分析，什么都没找到，现在再次回过头来，看到了”lego”，emmm，乐高积木，不像提示，EV3？去搜索引擎查一下：

![](https://image.3001.net/images/20190221/1550758485_5c6eb25551f97.png!small)

第一条就很符合题意~

再加上关键词wireshark试试：

![](https://image.3001.net/images/20190221/1550758489_5c6eb259e8390.png!small)

第一条是github上的一个工具~

赛棍的多年经验告诉我们，这可能是用于帮助wireshark解析某些私有协议用的一个工具。

看人家的描述果然如此：

![](https://image.3001.net/images/20190221/1550758496_5c6eb2601f3a5.png!small)

按照说明，通过命令行相应加载解析器，然后使用wireshark打开之前的数据包。

![](https://image.3001.net/images/20190221/1550758502_5c6eb2666203f.png!small)

此时再用ev3进行过滤：

![](https://image.3001.net/images/20190221/1550758508_5c6eb26cc2f8d.png!small)

EV3的报文如下：

![](https://image.3001.net/images/20190221/1550758516_5c6eb274170aa.png!small)

有好几个参数，这些参数代表什么意思呢？由于这是一个私有协议，我们需要去实现它的源码里去找定义。

还记得第一次搜索引擎找到的mindstorm吗，在源码里我们找到：

![](https://image.3001.net/images/20190221/1550758522_5c6eb27a08ace.png!small)

现在我们知道了第二个参数是x坐标，第三个是y坐标，第四个是我们的字符。 那么我们就可以一条条地根据这个跟着解析信息了，刀耕火种太慢，直接上脚本吧。

在此之前需要把数据导出为json格式：

![](https://image.3001.net/images/20190221/1550758529_5c6eb281cd1eb.png!small)

关键片段，按照参数定义进行解析：

![](https://image.3001.net/images/20190221/1550758535_5c6eb287e8012.png!small)

运行即得到flag了。

![](https://image.3001.net/images/20190221/1550758543_5c6eb28fa6cce.png!small)

## 0x06 后记

在CTF比赛中划水划了两年，也就在萌新前打肿脸充胖子，本文主要面向萌新以及对流量取证感兴趣的师傅们，望各位大佬轻喷。

 ***本文作者：Yale1024，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

