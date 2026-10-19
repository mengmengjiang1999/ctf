# 【技术分享】针对Outernet卫星信号的逆向工程

阅读量 **210380**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2016-11-14 09:59:37

 **x**

##### 译文声明

本文是翻译文章，文章来源：gnuradio

原文地址：<http://gnuradio.org/blog/reverse-engineering-outernet/>

译文仅供参考，具体内容表达以及含义原文为准。

****

******翻译：**[
**twittered**](http://bobao.360.cn/member/contribute?uid=245645961)

**稿费：200RMB（不服你也来投稿啊！）**

**投稿方式：发送邮件至linwei#360.cn，或登陆**[
**网页版**](http://bobao.360.cn/contribute/index) **在线投稿**

**前言**

Outernet[1]是一家旨在让访问国际互联网更加方便自由的公司，他们使用卫星来广播维基百科或者其他网站。目前，他们的广播主要使用三颗国际海事卫星[3]的L波段[2]，使其广播覆盖全球，大多数接收机是开源的，可是，他们的关键部分是闭源的，比如二进制的数据分发模式和信号的详细信息。实际上，Outernet可能违反了GPL
，因为他们的sdr100[4]是基于librtl SDR和libmirisdr[5]开发的，而这两个使用了GPL开源协议。

  

**详情**

最近。我逆向了 Outernet 的信号，并完成了一个完全开源的的解码器，他由一个GNU Radio流图 gr-outernet[6]和python脚本free-outernet[7]组成，前者负责获取信号，后者负责提取出传输的文件。

在这篇文章中，我将描述GNU
Radio是如何工作的还会介绍一些我用来逆向信号的工具和技术。这些技术可以同样应用于其他的类型的信号，特别是用于卫星通讯的信号（逆向结束之后，我才知道它使用了现成的卫星广播通讯方式，Datum
Systems M7[8]），你可以在我的博客[9]中找到更多有关于Outernet的信息和其他项目。

处理射频信号的第一步始终都是调整设备的频率和带宽。即使你不知道怎么解调信号，他在瀑布图上，频率和带宽是很明显的。在这里，我使用Scott
Chapman（K4KDR）[10]从 I-4 F3卫星上获取的I/Q数据信号，它在美国上空的广播频率是1539.8725
MHz，我们可以清楚的看见带宽大概是4.8kHz。如果你运行下面的流图，将会看到输出。

我们如果只看这些，基本对信号一无所知，他看起来像一个4.8khz的宽峰噪音，正如 Phil Karn
（KA9Q）[11]所说：“任何一个先进的通讯方案都无法区别噪音。”因为它是一个窄带卫星信号，我们猜测它使用的是PSK方式调制的，但是采用的BPSK还是QPSK？这两种都是有可能的。有一种简单的方式可以猜测PSK的类型而不用把它恢复到星图。这个方法是：首先，我们把信号功率提升到2倍（源信号乘以本身），如果我们发现了直流成分，那么这个是BPSK信号，如果没有，我们提升到4倍，如果这时产生直流成分，那么是QPSK信号。这也适用于高阶PSK信号（不适用于QAM），对于一个M-PSK信号来说，提升一个整数倍m时，会产生直流成分。

你可以看下面的流程，当提升2倍时，出现来直流脉冲，这表明，Outernet是BPSK信号。

下面的任务是获取信号的波特率，有一种叫循环平稳分析的方法可以用来获取信号的波特率。使用延时之后的信号复共轭相乘。最好的解释方式就是看下面的流图。

循环平稳分析的输出显示来一个特定频率下的波特率频率分量，在下面的图中，我们可以看到在4200hz处有分量，这表明，波特率是4.2kbaud。频率图中的高平均是很重要的，否则4200hz的频率分量是很难看到的。

现在，我们知道了波特率，我们可以把它恢复成星图，发现它确实是BPSk信号，有关于PSK的解调[12]，GNU
Radio入门介绍网页[13]有一篇很好的说明。下面，你可以看到我们的BPSK解调器流图和星图，正如预期，这是一个BPSK信号。

Outernet对外所说比特率约为2
kbps，或为20MB每天，而我们分析得到的比特率是4.2kbaud，所以，很有可能它使用了r=1/2正向纠错编码，参数r被称为速率， R = 1 /
2意味着数据流使用了1/2bits用来在接收器中纠正错误位，实际速率只有我们测得速率的一半，也就是2.1kbps。

对于参数是r=1/2的数据，最流行的是使用国际空间数据系统咨询委员会提出的，r=1/2,卷积码K = 7的协议式。针对这种编码的Viterbi解码器在GNU
radio中有相应的模块，叫做“Decode CCSDS 27”。然而，这种编码允许在几个变量上有所更改。我们可以使用Balint
Seeber[14]的Auto FEC[15]监视Viterbi译码器的误码率并尝试不同的组合参数，直到发现一个可以正常使用的组合。 Auto
FEC也可以删余一些数据（超过1/2的部分）。实际上，你很可能不知道它使用了何种删余率，因为变化太多了。

如果想使用Auto FEC，你需要在GNU Radio上打一个补丁，因为 Viterbi 解码器和 “Decode CCSDS
27”模块需要修改以便输出误码率。在这里[16]，你可以找到一个用于GNU Radio当前版本的补丁（3.7.10.1测试版），同样，Auto
FEC需要输入的是QPSK信号，这有一个补丁[17]可以让他与BPSK 信号工作。

从下面的流图，你可以看到Auto FEC的运行和他的输出，Auto FEC在控制台上打印各种组合，以尝试得到正确的参数。在这个输出中，需要注意的是把
“Viterbi swap”设置为true。他的含义是在CCSDS编码这个特定的环境中，多项式的数值是交换的。通常，A决定第一位，B
决定第二位。而在这里，第一位来自B，而第二位来自A。为了抵消这一点，我们需要交换每对数据，再把他们送入CCSDS协议解码器。

现在，我们实现了一个 Viterbi
译码器并检查了它的工作。“Swap”模块是一个自定义的模块，它交换每一对浮点数。对于BPSK信号，我们要把两个Viterbi译码器放在输入流上，

其中一个比另一个延后一个样本，因为我们不知道刚开始捕获数据的时候，是一对数据的第一个还是第二个。

你可能会看到如下的输出，其中metric变量表示Viterbi解码器的误码率，当误码率很低的时候metric变量很高，而且几乎有一个恒定的数值，相反，如果解码器没有工作，metric值会很低，并具有类似随机的值。当然，两个译码器只有一个正常工作。当BPSK解调错过一个值或者插入来一个值，（样本流多了或者少了一个bit），这两个Viterbi解码器的工作状态（是否工作正常）就会交换，如果信号质量好，不应该发生这种情况，在这个过程中，是由于树木在风中的移动干扰来信号。另外一个有趣的尝试是关闭“Swap”模块，这样的话两个Viterbi解码器都不会正常工作了。

现在，我们对Viterbi译码器是否工作很有信心，我们接下来把数据流放入raster图，观察是否使用了扰频器，如果使用了，数据流会看起来随机化，如果没有，我们会看到一些比特流的特有结构，实际上，我们基本已经确定它使用了扰频器，因为我们之前看到的BPSK信号很像噪声，而不是展现BPSK的特有频谱结构。

正如你下面看到的，比特流的出现是随机的，所以我们还需要一个解扰器。

选择正确的解扰器是很困难的，因为我们没有办法去猜测它的算法，如果您知道它使用来那种卫星调制解调器，请尝试它支持的所有算法，如果您不知道，那就尝试所有流行的算法。这一步通常需要大量的试验和错误。然而，如果选用正确来，效果也是很明显的，你可你看到他的输出比特流结构，如果不对，输出还是随机的。

最常用的一种是G3RUH的复数乘法器（它用于9.6kbaud业余无线电组和几个业余卫星），数据可以使用GNU radio中的 “Descrambler”
模块加扰，它使用0x21作为掩码，长度为16 ，这个模块的参数选择很麻烦，详见我的博客。[18]

在这种情况中，G3RUH加扰器是无法工作的。有这样的事实，我们的二进制代码要传递给寄存器进行处理，
sdr100在Outernet的软件中作为sdr接收器，那么，他只可能是基于ARM或者86-64架构上运行的Linux操作系统，而最新的软件版本只对arm进行支持，所以，Outernet上用于接收的部分应该是像树莓派3一样的arm板。

我对x86-64架构下的客户端程序中的sdr100二进制文件进行了逆向，来获取Outernet解扰算法，原来，这是
IESS-30解码器，很显然，这个算法的详细细节在卫星地球站的文档中没有公开。但是，我还是找到了一个文档[19]（见28页），里面的描述有助于我的逆向。

我设计了一个模块用于 IESS-308
解码，您可以在这里[20]看到这个模块的代码。如果你熟悉乘法加扰器，你会发现这个加扰器很普通，但是，它用了一个计数器。

下面的流图可以测试我们的 IESS-308 解码器

输入流显示出了很明显的结构，所以我们有信心，这个解码器是正常的。你可以看到一些白色和青色的水平线，这符合长时间连续二进制0,1传输的特征。这张图中的每行每列的水平线的数量和分布代表着二进制的数据，如果把它们垂直摆放在一条线上，看起来可能更明显，我们会很容易发现什么数据是不改变的（例如报文头）或者改变的（例如数据段）。在这条推文中[21]，你可以看到进行如上工作的一个例子。

下一步工作是解帧，通常，我们可以通过仔细观察比特流来识别帧标记，但是，在这里我们可以通过逆向sdr100二进制代码的方式减轻工作量。sdr100中，有一些函数的名称中含有HDLC，所以我们猜测可能是使用来HDLC帧，我们尝试从数据流中恢复HDLC帧。

GNU Radio中，提供了用于解HDLC帧的模块，但是，我准备用我自己的gr-kiss[22]模块。这个模块的好处是可以去保留CRC码校验错误的数据帧。有的时候，可能一个数据帧只有几个bit是错误的，他就被完全丢弃了。然而，保留CRC校验错误的帧对于逆向协议和分析测试是很有用的。有时候，HDLC帧会有几个bit的错误，那可能是因为干扰或者解码器参数没有优化，也有可能碰巧只有16位的CRC码出现了错误。在这种情况下，保留错误帧也是很有用的。

到现在为止，我们还没有考虑信号的极性，在接受
BPSK信号的时候，你不知到他是一个原始信号还是一个翻转信号（即0,1的互换），是否进行了180度的相位翻转是模糊的，很多时候，采用差分编码来消除这种模糊性。HDLC
可能采用的是NRZ-I，也可能没有采用差分编码，而采用其他方式消除模糊，这又是一个实验和试错的过程。

实际上，Outernet不使用任何一种差分编码，因此我们需要一个正置的数据流和一个反置的数据流，只有一个可以正常工作，但是我们实现不知道是哪一个。（当我们失去信号之后，下一次连接，它可能改变。）

下面是HDLC解帧的流图，“Invert
bit”是一个自定义的模块，他的功能就是进行位翻转。也可以使用程序提供的模块实现这一功能。下面，我把两个HDLC解帧模块连接在数据流上，在其中一个前面进行位翻转。

当我们运行这个流图之后，在控制台上会看到数据帧的出现。因为我们开启了CRC检查，

所以我们确信我们的接收机可以正常工作。毕竟，如果我们在处理的时候有错误，是不可能出现这么多通过CRC校验的数据帧。

我们GNU Radio阶段的任务就完成了，一旦提取了HDLC数据帧，就需要使用free-outernet[23]这个Python脚本进行UDP发送，或者把它们存在一个文件里。free-outernet会回复被传输的文件，它还会打印一些有趣的调试和技术信息。

下面你可以看到脚本可以恢复的两个文件，e89f-messages-0.html.tbz2包含了用于业余无线电的APRS[25]信息，和ed57-amazon.com.html.tbz2，其中包含亚马逊的维基百科网页[26]。大部分的文件是以tbz2压缩格式发送的。另一个有趣的事情是，每分钟，会有一个时间数据包。这用来更新接收器的时钟信号，因为使用的是小型ARM，所以没有真实的时钟或者网络连接。

提取文件后，我们可以在Web浏览器中打开亚马逊的维基百科页面。这页是一个HTML文件，其中包含CSS样式表和图片。它为独立的查看而进行了小尺寸优化，所以所有的超链接已被删除。

对广播文件协议的介绍超出了本文的范围，你可以在我的博客[27]中找到完整的描述。我唯一不能逆向的是使用了应用级FEC的LDPC编码。它可以使接受程序在一些数据帧错误的情况下恢复文件，由于LDPC码的译码没有实现，所以你需要获取一个文件所有的数据帧才能使用我们的脚本恢复，你可以看到github上有关于LDPC的进展[28]。

  

**参考链接**

[1]<https://outernet.is/>

[2][https://en.wikipedia.org/wiki/L_band](https://en.wikipedia.org/wiki/L_band)

[3][https://en.wikipedia.org/wiki/Inmarsat](https://en.wikipedia.org/wiki/Inmarsat)

[4][https://github.com/Outernet-Project/outernet-linux-lband/blob/master/bin/sdr100-1.0.4](https://github.com/Outernet-Project/outernet-linux-lband/blob/master/bin/sdr100-1.0.4)

[5][http://sdr.osmocom.org/trac/wiki/rtl-sdr](http://sdr.osmocom.org/trac/wiki/rtl-sdr)

[5][http://cgit.osmocom.org/libmirisdr/](http://cgit.osmocom.org/libmirisdr/)

[6][https://github.com/daniestevez/gr-outernet](https://github.com/daniestevez/gr-outernet)

[7][https://github.com/daniestevez/free-outernet](https://github.com/daniestevez/free-outernet)

[8][http://datumsystems.com/m7](http://datumsystems.com/m7)

[9][http://destevez.net/tag/outernet/](http://destevez.net/tag/outernet/)

[10][https://twitter.com/scott23192](https://twitter.com/scott23192)

[11][http://www.ka9q.net/oldquotes.html](http://www.ka9q.net/oldquotes.html)

[12][http://gnuradio.org/redmine/projects/gnuradio/wiki/Guided_Tutorial_PSK_Demodulation](http://gnuradio.org/redmine/projects/gnuradio/wiki/Guided_Tutorial_PSK_Demodulation)

[13][http://gnuradio.org/redmine/projects/gnuradio/wiki/Guided_Tutorials](http://gnuradio.org/redmine/projects/gnuradio/wiki/Guided_Tutorials)

[14][http://spench.net/](http://spench.net/)

[15][http://wiki.spench.net/wiki/Gr-baz#auto_fec](http://wiki.spench.net/wiki/Gr-baz#auto_fec)

[16][https://gist.github.com/daniestevez/79f6f9971e1c6f883cb67a2989ba33e6](https://gist.github.com/daniestevez/79f6f9971e1c6f883cb67a2989ba33e6)

[17][https://gist.github.com/daniestevez/70d570292493daac33efb1767fc478ed](https://gist.github.com/daniestevez/70d570292493daac33efb1767fc478ed)

[18][http://destevez.net/2016/05/scramblers-and-their-implementation-in-gnuradio/](http://destevez.net/2016/05/scramblers-and-their-implementation-in-gnuradio/)

[19][http://www.etsi.org/deliver/etsi_etr/100_199/192/01_60/etr_192e01p.pdf](http://www.etsi.org/deliver/etsi_etr/100_199/192/01_60/etr_192e01p.pdf)

[20][https://github.com/daniestevez/gr-outernet/blob/master/lib/descrambler308_impl.cc#L72](https://github.com/daniestevez/gr-outernet/blob/master/lib/descrambler308_impl.cc#L72)

[21][https://twitter.com/ea4gpz/status/786518040141717505](https://twitter.com/ea4gpz/status/786518040141717505)

[22][https://github.com/daniestevez/](https://github.com/daniestevez/gr-kiss)[g](https://github.com/daniestevez/gr-kiss)[r-k](https://github.com/daniestevez/gr-kiss)[iss](https://github.com/daniestevez/gr-kiss)

[23]<https://github.com/daniestevez/free-outernet>

[24]<http://www.ax25.net/kiss.aspx>

[25] [http://aprs.org/outnet.html](http://aprs.org/outnet.html)

[26]<https://en.wikipedia.org/wiki/Amazon.com>

[27]<http://destevez.net/2016/10/reverse-engineering-outernet-time-and-file-services/>

[28]<https://github.com/daniestevez/free-outernet/issues/1>

本文翻译自gnuradio [原文链接](http://gnuradio.org/blog/reverse-engineering-outernet/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **backahasten** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/84902](/post/id/84902)

安全客 - 有思想的安全新媒体

本文转载自: [gnuradio](http://gnuradio.org/blog/reverse-engineering-outernet/)

如若转载,请注明出处： <http://gnuradio.org/blog/reverse-engineering-outernet/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhmsg.com/dm/200_200_100/t018fc2200a809a7add.jpg)
backahasten

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

