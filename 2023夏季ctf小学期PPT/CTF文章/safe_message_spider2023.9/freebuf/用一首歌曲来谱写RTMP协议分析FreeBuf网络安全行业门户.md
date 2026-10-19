***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 ** ***本文原创作者：星空111，本文属FreeBuf原创奖励计划，未经许可禁止转载**  
**

为了让我这篇技术稿更加有情趣，打算用一首歌曲的结构来命名我整篇文章的脉络。

##  **一、前序 <C插句>**

 **最近在重温由W.Richard Stevens 的传世之作《TCP/IP详解》，看到第12章TCP ，基于传输层有TCP 、 UDP 、 TLS
、DCCP 、SCTP 、RSVP 、PPTP等，那我好奇那基于TCP有哪些协议呢？在Google里面查找了一下，有一个协议映入眼帘 RTMP
，RTMP(实时消息传输协议)是Adobe
公司开发的一个基于TCP的应用层协议，主要用来在Flash/AIR平台和支持RTMP协议的流媒体/交互服务器之间进行音视频和数据通信。RTMP协议没听过啊，一下子激起了我想要揭开它的面纱的冲动，大概研究了RTMP协议整整3天时间，试图想要找出一些漏洞出来，幸运的是我找到了！很鸡冻，下面就是我对此协议的分析。**

##  **二、RTMP协议分析 <A主歌>**

### 1) 播放一个RTMP协议的流媒体需要经过：

1>握手 2> 建立链接 3>建立流 4>播放 5>发送 --------------
1>握手(Handshark)

**********![33.PNG](https://image.3001.net/images/20180808/1533698733_5b6a62ad99741.png!small)****
** ****

**Handshake done Handshake done**

Note：交互示意图就不讲解了,很简单!为了让本技术稿有很好的易读性，我尽力注释！  

2>建立链接（ConnectResponse）

 ** ** ** **
**![33.PNG](https://image.3001.net/images/20180808/1533698815_5b6a62ff55afb.png!small)****
** ****

3>建立流<CreateStream>

**********![33.PNG](https://image.3001.net/images/20180808/1533698887_5b6a63476ec5e.png!small)****
** ****

4>播放<Play><\-----抓包播放的关键字符串 "play"  

**********![33.PNG](https://image.3001.net/images/20180808/1533698978_5b6a63a2ae474.png!small)******
** **

5>发送（Send）----Metadata  

###
![33.PNG](https://image.3001.net/images/20180808/1533698353_5b6a6131d6a89.png!small)**2）用我的宝贝wireshark抓包来分析一下过程**

1>抓包：

![Clipboard
Image.png](https://image.3001.net/images/20180808/1533701608_5b6a6de8f0f37.png!small)

2>RTMP消息结构：

![33.PNG](https://image.3001.net/images/20180808/1533701745_5b6a6e715f224.png!small)还是用XMind做个示意图吧！

要想在相应的网络环境上传输就需要将消息拆分成较小的数据块 **< Chunk>**![Clipboard
Image.png](https://image.3001.net/images/20180808/1533702501_5b6a71654600d.png!small)3>消息块的报文结构：

![33.PNG](https://image.3001.net/images/20180808/1533703177_5b6a7409ac4e0.png!small)

![33.PNG](https://image.3001.net/images/20180808/1533705103_5b6a7b8fdec39.png!small)Note:时间戳<Timestamp>:由于时间戳在电子取证中的重要作用及其法律地位，时间戳系统必须拥有极高的安全级别，
安全保护应包括物理环境安全和软件安全。

4>RTMP消息分块

Message被分割为几个消息块的过程中， Message Body大小固定的消息块(Chunk Size，默认128个字节)并在其首部加上Chunk
Header 就组成了相应的消息块。

Eg:309字节的消息块进行分块示意图如下所示：

![33.PNG](https://image.3001.net/images/20180808/1533705859_5b6a7e8341206.png!small)

###  ** ** ** ** **3) HnadsShark阶段的源码分析**********

 ** ** ** **
**![33.PNG](https://image.3001.net/images/20180808/1533741647_5b6b0a4f8d0b7.png!small)******
****

## **三、渗透测试 <B副歌>&<流行句D>**

分析到RTMP居然是未加密协调，很开心！然后就查了一下此协议的都应用在哪些方面，结果是：流媒体/交互服务器之间进行音视频和数据通信
，我第一就想到的应用场景是当今炙手可热的直播平台，随便百度了一下，点进去一个直播平台如下图：

![33.PNG](https://image.3001.net/images/20180808/1533706981_5b6a82e513eeb.png!small)

哇塞，可爱的妹子，心里想再瞅瞅，不一会有有一个恶心的弹窗蹦出来，如下图：

![33.PNG](https://image.3001.net/images/20180808/1533707189_5b6a83b50a544.png!small)

我毫不犹豫的关闭这个弹窗，心里想：还敢不敢让我安安静静的看这个直播，没过30s又出现这个弹窗！我明白了这个直播平台想要 _ **收集我的个人信息
<不怀好意，大家都懂的！>**_不认证不给看!心里憋屈，想着能不能绕过注册认证看直播呢？反正已经知道RTMP协议是未加密的，是明文传输的！先抓包看一下再说。

Note:1>想要抓到完整的三次握手包，必须是在免费观看的那段时间进行抓包，弹窗后后抓的包是不完整的！

2>由于这种通信模式是最常见的C/S模式，突然让我想到刚刚分享了Rtmp的消息结构， **Play/Pause** 它是C/S交互的字符串标志！

![1.PNG](https://image.3001.net/images/20180808/1533708178_5b6a87924e142.png!small)

 **Note:ID(15-20)是负责发送AMF编码的命令，负责User与Server之间的交互 eg：Play/Pause。**

也就是Rtmp协议里面肯定有"play"这个字符串！然后用wireshark的过滤器进行字符串关键字的查询；由于是未加密的协议，只要我找到这个播放的URL地址，再找个可以播放这种流式协议的播放器不就大功告成了吗？突然脑袋中灵光乍现，记得在2017-7-27的BUF早餐铺<本人像追剧一样，每次发布，必拜读>就有报道一个内容是：
关于因频繁杀后台，VLC播放器将华为机型列入黑名单。

![33.PNG](https://image.3001.net/images/20180808/1533729878_5b6adc5696424.png!small)

Note: VLC是开源播放器应用，可播放大多数多媒体文件，以及 DVD、音频 CD、VCD 及各类流媒体协议！正好得来全不费工夫！

 **Just Do It !**

1>首先筛选出字符串为"rtmp"----（B1）

![33.PNG](https://image.3001.net/images/20180808/1533707961_5b6a86b910caa.png!small)

Note: 右下角的ASCII区明文显示：rtmp://pull.kktv8.com:1935/livekktv。

当时有点鸡冻，直接将这部分url地址粘贴在VLC的没有打开！

![33.PNG](https://image.3001.net/images/20180808/1533730672_5b6adf709540d.png!small)

2>我居然忘记一个最重要的字符串"Play",赶紧再筛选一次----(B2)

**![33.PNG](https://image.3001.net/images/20180808/1533730819_5b6ae0035325b.png!small)Note：出现了！是:128128278。**

3>URL组合：rtmp://pull.kktv8.com:1935/livekktv/128128278 ----(B3)

4>Play it！(B4)

**![33.PNG](https://image.3001.net/images/20180808/1533731157_5b6ae1557c85e.png!small)**5
>Bingo--->妹子终于现身(B5)

**![33.PNG](https://image.3001.net/images/20180808/1533731540_5b6ae2d406118.png!small)**Note:RTMP
RTSP 协议都可以用来做视频直播，只要我们拿到它们的URL，都可以通过VLC Media Player进行播放查看。

6>发散思维（留个大家的思考问题）(B6)

这个渗透实验的成功,让我想到一些比如爱奇艺，腾讯视频，优酷等要看那些美国大片必须要买VIP才能观看，并且最重要的是可以试看几分钟，但是这些视频传输是基于Http协议的，或者说是一个[客户端](https://baike.baidu.com/item/%E5%AE%A2%E6%88%B7%E7%AB%AF)和[服务器](https://baike.baidu.com/item/%E6%9C%8D%E5%8A%A1%E5%99%A8)端请求和应答的标准（TCP）！这个方面我之前研究过，在此就不赘述了！大家可以再脑袋大开一点研究研究！

##  **四、修复方案 <E结尾>**

1>协议不变的基础上,总体思路：首先明确漏洞点，然后明确代码块，再加权限函数。  

**需要加的权限函数如下：//类似于大家通常在数据库里边添加校验位一个作用**

    
    
     if (ReadN(r,(char*)serversig,RTMP_SIG_SIZE)!=RTMP_SIG_SIZE)
    
    return FALSE;
    
    if (!WriteN(r,(char*)reply,RTMP_SIG_SIZE))
    
    return FALSE;

2>使用加密协议RTMPS协议；

3>让用户不要试看，一点击进去就需要认证，防止捕获到完整的数据包；

整首歌的结构是：C+A+B+D+B1+B2+B3+B4+B5+B6+E；

熬夜写歌，是否动听！

 ***本文原创作者：星空111，本文属FreeBuf原创奖励计划，未经许可禁止转载**

