**作者: evilpan  
博客: [PansLabyrinth](https://evilpan.com/2020/03/29/wifi-security/) **

**本文为作者投稿，Seebug Paper 期待你的分享，凡经采用即有礼品相送！ 投稿邮箱：paper@seebug.org**

本文主要分享WiFi相关的一些安全研究，以及分析几个实际的攻击案例，如PMKID、KARMA、Krack、Kr00k等。

# WiFi起源

WiFi是一种无线局域网协议(WLAN)，经过多年的发展，WLAN基本上也等同于WiFi。史前时代的LAN可以追溯到1971年ALOHAnet提出的多址接入思想。

![
](https://images.seebug.org/content/images/2020/03/d372ca63-a29d-4e14-a729-3ff80bceb9e8.png-w331s)

但我们不看那么远，直接跳到1985年，当时FCC(US Federal Communications Commission,
美国联邦通信委员会)首次开放2.4GHz等频段，允许节点在这些频段以扩频技术通信，为后续无线局域网的发展立下基础。

> 扩频(Spread Spectrum)通信的方法有很多，常见的是蓝牙用的跳频(Frequency Hopping)和WiFi用的直序扩频(Direct
> Sequence)

随后在1989年，第一个无线局域网产品WaveLAN出现；次年，`IEEE
802.11`委员会被正式成立，开始构建一个无线局域网的专用协议。期间WaveLAN经过了许多部署尝试，在产业界沉淀了实践基础。

WiFi，正确写法应该是`Wi-Fi`(Wireless-Fidelity)，即无线-高保真。无线都能理解，高保真则是要求在无线网络中可靠地传输数据。WiFi最初是一个独立的完整协议，其主要内容在 **后来** 被IEEE
802.11委员会接受并成了`802.11a`的标准。

1999年，Wi-Fi联盟成立，这多个厂商发起的非盈利联盟，致力于解决工业界的兼容性和统一问题，填补学术界和工业界之间的实现差异。

![
](https://images.seebug.org/content/images/2020/03/8efccc44-ae9b-4c8c-8838-76ef1d77e224.png-w331s)

还是1999年，IEEE颁布了`802.11b`协议，这是WiFi协议的里程碑，早期笔记本电脑和PS游戏机中的无线功能都是基于802.11b的。同年，苹果也推出了基于WiFi原理的Airport技术。

一年后的2000年，`802.11a`才正式通过。但是因为当时5GHz开放的信道有限，802.11a并没有推广开来。

2003年，颁布`802.11g`协议标准，修改802.11a的不足，在2.4GHz频段上使用OFDM技术。

2004年，`802.11i`颁布，关键词是WiFi安全性。

2009年，`802.11n`，关键词是MIMO(多输入多输出)。

2014年，`802.11ac`，关键词是下行MU-MIMO。

...

2019年，`802.11ax`，WiFi6，关键词是双向MU-MIMO。

当然，这只是其中几个关键的标准。我们可以在[802.11_Timelines](http://grouper.ieee.org/groups/802/11/Reports/802.11_Timelines.htm)中看到所有802.11颁布的协议和时间线。按照演进的方向，也可以概要为下图：

![
](https://images.seebug.org/content/images/2020/03/63569978-3457-4d66-9bdb-0ac7a5849efc.png-w331s)

# WPA/WPA2/WPA3

WiFi虽然广为人知，但是其物理层和链路层的实现也是相当复杂，念完研究生的无线网络课程也不敢说自己精通WiFi。因此，我们主要聚焦在协议安全性以及实现的安全性上。

WPA([Wi-Fi Protected Access](https://en.wikipedia.org/wiki/Wi-Fi_Protected_Access))，即无线保护访问，是WiFi联盟为应对WEP([Wired Equivalent
Privacy](https://en.wikipedia.org/wiki/Wired_Equivalent_Privacy))中存在的各种安全问题而推出的解决方案。其中WPA最初只是作为草稿发布，并为后续更完善的WPA2铺路，二者都定义在`802.11i(IEEE
802.11i-2004)`的标准中。

我们目前广泛使用的WiFi安全保护访问就是WPA2的标准。在2018年1月，WiFi联盟又推出WPA3，在WPA2的基础上做了一些[安全增强](https://www.wi-fi.org/news-events/newsroom/wi-fi-alliance-introduces-security-enhancements)。

WPA是标准，而我们常见的WPA-PSK TKIP/AES-CCMP则是具体的加密模式和加密方法。

> 拓展阅读： [what-is-the-difference-between-tkip-and-> ccmp](http://www.comtechpass.com/what-is-the-difference-between-tkip-and-> ccmp/)

# 4-Way Handshake

说到WiFi安全，就不能不说校验过程中涉及到的四路握手。四路握手的目的是为了安全地验证和交换秘钥，验证对端合法性，防止中间人攻击。

四路握手中涉及到的一些名词如下：

  * authenticator：即AP(Access Point)，可以理解成路由器
  * supplicant：即想要接入AP的Client，简写为STA(Station)
  * MSK (Master Session Key)
  * PMK (Pairwise Master Key)
  * GMK (Group Master Key)
  * PTK (Pairwise Transit Key)
  * GTK (Group Temporal Key)
  * ANonce：Authenticator Nonce
  * SNonce：Supplicant Nonce
  * MIC：Message Integrity Check

是否有很多问号？不要紧，待会回头再看就很清晰了。先放一张四路握手的大图，记得时不时拉回来看看：）

![
](https://images.seebug.org/content/images/2020/03/04613f68-4667-4b40-b303-4323fc962695.png-w331s)

接下来就围绕着上图的握手流程进行分析。

## 802.11帧

既然我们不关注物理层，那么就可以从接受并解码后的数字信号说起。首先打开我们的WireShark抓一会儿包(monitor
mode)，挑选其中任意一个无线数据包查看，可以看到最顶层的包头是`IEEE 802.11 XXX frame`，所以我们就从这个包说起。

>
> 实际上面还有一层radiotap，是抓包工具加的，提供额外信息，比如时间，信道等，这些内容不是标准中的一部分，详情可见：<http://wifinigel.blogspot.com/2013/11/what-> are-radiotap-headers.html>

![
](https://images.seebug.org/content/images/2020/03/f287af00-e4ce-4faa-9f4b-d76510602da6.png-w331s)

一个802.11帧就是这么朴实无华，且枯燥。但是后面的介绍会用到里面的一些字段，所以就先放出来。注意前两字节是帧控制(Frame
Control)头，每个bit有不同的意思，具体可以看虚线下的展开。

接下来我们通过实际抓包来看WiFi连接认证的完整过程。测试使用我们自己搭建的WiFi，AP的SSID为`evilpan`，BSSID为`66x6`，WPA2密码为12345678，所连接的客户端为苹果手机。

## Auth & Associate

一般情况下，AP会一直向周围广播宣告自己的存在，这样STA才知道周围有哪些热点，并选其中的一个进行连接。广播的数据称为`Beacon
Frame`其中包括了热点的BSSID(即MAC地址)和ESSID(即热点名)。

![
](https://images.seebug.org/content/images/2020/03/73331792-04fa-4162-886c-1c17f3fa406a.png-w331s)

> **Beacon Frame** 并不是必须的，路由器可以配置不广播，STA依然可以通过指定SSID和密码进行连接，即所谓的隐藏热点。

在WiFi握手前还可以看到两大类型的帧，Authentication和Association，分别是认证和连接。注意这里的认证和安全性无关，只是认证双方是和符合标准的802.11设备。而连接后则在链路层接入网络，如果是Open
WiFi，此时已经接入LAN，如果需要WPA认证，即我们所讨论的情况，则正式开始四路握手。

回顾上面的四路握手大图。注意在握手开始之前，双方手上都有一个`PMK`，即配对主秘钥。这个秘钥是从哪来的呢？在`IEEE
802.11i-2004`标准中有定义，如果使用PSK(Pre-Shared
Key)认证，那么PMK实际上就是PSK。而PSK则是通过WiFi密码计算出来的：

    
    
    PMK = PSK = key_derivation_func(wifi_passwd)

key_derivation_func是一个秘钥推导函数(PBKDF1/2)，内部以SHA-1为哈希函数。

还注意到，AP端不止有PMK，还有一个`GMK`。这是AP自己`生成`的，GMK用来为每个连接的STA生成GTK，并分享给STA。为了避免GMK被STA猜解，有的AP可以设置定时更换GMK，如思科的设备中`broadcast
key rotation`选项。

> 拓展阅读：[Real 802.11 Security: Wi-Fi Protected Access and
> 802.11i](https://books.google.com/books?id=nnbD-> FPpszMC&pg=PA210&lpg=PA210&dq=how+is+GMK+generate&source=bl&ots=LP4NjRTyaH&sig=ACfU3U2NRkgzwu1mC07WnS2HxKW3rRdLJA&hl=en&sa=X&ved=2ahUKEwjD3cK6nb3oAhWRdn0KHX2wBSMQ6AEwBXoECAoQAQ#v=onepage&q=how%20is%20GMK%20generate&f=false)

WPA中四路握手的协议也称为`EAPOL(Extensible authentication protocol over
LAN)`，可以直接在wireshark等工具中使用eapol过滤出来。

## 握手1/4

握手第一阶段，AP向客户端发送随机数`ANonce`。

![
](https://images.seebug.org/content/images/2020/03/ec038553-0085-4bf5-8c5f-90ff0e747975.png-w331s)

此时，客户端中有PMK、ANonce、SNonce(客户端自行生成的随机数)，以及双方的MAC地址信息。通过这些信息，计算PTK：

    
    
    PTK = func(PMK + Anonce + SNonce + Mac (AA)+ Mac (SA))

> `func`是个伪函数，表示经过某种运算。函数的实现细节不展开，下面都使用func作为伪函数名。

PTK是 _Pairwise Transit Key_
，根据参与运算的参数可见，该秘钥在每个客户端每次握手中都是不同的。PTK也可以理解为一个临时秘钥，用来加密客户端和AP之间的流量。

## 握手2/4

客户端生成PTK后，带着自己生成的SNonce发送给AP，目的是为了让AP使用同样的方法计算出PTK，从而确保双方在后续加密中使用正确的秘钥。

![ ](https://images.seebug.org/content/images/2020/03/36066b36-c454-4aec-ac5c-3345949392d1.png-w331s)

在这次发送的数据中，还包含MIC(Message Integrity Check)字段，AP用以校验该条信息的完整性，确保没有被篡改。

## 握手3/4

客户端收到第二阶段发送的SNonce之后，就可以算出PTK，并用PTK加密GTK后，发送给客户端，同样带有MIC校验。

![
](https://images.seebug.org/content/images/2020/03/12fe0d95-5318-43f1-bf35-e9432ed785eb.png-w331s)

发送的GTK是最初从GMK生成而来的，主要用来加密组播和广播数据(实现上切分为GEK/GIK，在CCMP和TKIP作为不同字段使用)。

## 握手4/4

此时双方都有了后续加密通信所需要的PTK和GTK，第四次握手仅仅是STA告诉AP秘钥已经收到，并无额外数据：

![
](https://images.seebug.org/content/images/2020/03/bd6ea926-1e79-4d58-aa26-c8a020a06641.png-w331s)

## 小结

根据秘钥的唯一性，可以分为两种：

  * Parwise Key：一机一密，每个客户端保存一个，AP端保存多个，用来加密单播数据
  * Group Key：一组一密，所有客户端和AP都保存一个，用来加密组播或广播数据

根据秘钥的类型，也可以分为两类：

  * Master Key：主秘钥，预先安装或者很久才更新一次
  * Temporal Key：临时秘钥，每次通过主秘钥去生成

这样，理解前面的各种Key也就更加直观了。注意由于Group Key是所有客户端共享的，所以当某个客户端离开AP之后，AP会重新生成Group
Key，并通知其他终端进行更新；此外，前面也说了，某些AP也可以配置定期更新Group Key。

握手也可以简化描述为以下四步：

  1. AP发送ANonce给STA
  2. STA使用ANonce计算获得单播秘钥，发送SNonce给AP
  3. AP使用SNonce计算获得单播秘钥，并将加密的组播秘钥发送给STA
  4. 完成握手，双方都有PTK和GTK，加密后续对应报文

# 攻击案例

对四路握手有个基本了解之后，再来看看一些经常听说的WiFi安全问题是如何造成的。对于一些年代久远的案例，比如WEP、WPS攻击就不再介绍，因为它们已经退出历史舞台了。

## 暴力破解

既然WiFi密码是PSK，使用预置共享的秘钥，那么就不可避免面临暴力破解的问题。当然这里说的暴力破解不是输密码连WiFi，提示密码错误了再不断尝试，那样效率太低了。

实际中的暴力破解要高效得多。暴力破解的本质是获取PSK即PMK的明文，根据上面介绍握手的流程，作为一个未验证终端，我们实际能获取到的是ANonce、SNonce、Mac地址以及加密的内容和MIC，通过不断变换PSK/PMK计算PTK并验证MIC从而寻找真实密码。

比如我曾经最喜欢玩的`aircrack-ng`，其内部实现就是：

    
    
    EXPORT int ac_crypto_engine_wpa_crack(
        ac_crypto_engine_t * engine,
        const wpapsk_password key[MAX_KEYS_PER_CRYPT_SUPPORTED],
        const uint8_t eapol[256],
        const uint32_t eapol_size,
        uint8_t mic[MAX_KEYS_PER_CRYPT_SUPPORTED][20],
        const uint8_t keyver,
        const uint8_t cmpmic[20],
        const int nparallel,
        const int threadid)
    {
        ac_crypto_engine_calc_pmk(engine, key, nparallel, threadid);
    
        for (int j = 0; j < nparallel; ++j)
        {
            /* compute the pairwise transient key and the frame MIC */
    
            ac_crypto_engine_calc_ptk(engine, keyver, j, threadid);
    
            ac_crypto_engine_calc_mic(
                engine, eapol, eapol_size, mic, keyver, j, threadid);
    
            /* did we successfully crack it? */
            if (memcmp(mic[j], cmpmic, 16) == 0) //-V512
            {
                return j;
            }
        }
    
        return -1;
    }

在CPU/GPU足够给力的情况下，上百GB的字典可以在十几分钟跑完。当然跑字典也有一些循序渐进的策略，比如：

  1. 当地的手机号
  2. 所有8-10位数字组合
  3. Top xxx 密码字典
  4. 上述字典+变异
  5. 字典组合+变异
  6. ……

当然说这个不是教大家去暴力破解，而是根据上述策略去选取一个强度合适的WPA密码，保护自己的隐私安全。

## RSN PMKID

上面最常见的暴力破解需要获取4路握手包，也就是说有个前提是需要有客户端去连接。通过一些手段，比如伪造Deauth可以让目标强制掉线重连从而获取握手包，但不管怎样都需要有客户端在线才行。

PMKID攻击是`hashcat`的作者在2018年提出的，他发现在一些AP的第一次握手数据包中，包含了额外的EAPOL字段RSN(Robust
Security Network)，其中包含PMKID：

![
](https://images.seebug.org/content/images/2020/03/8f004a23-964c-4bbd-b93a-8f86926d8098.png-w331s)

这个PMKID的计算方法是：

    
    
    PMKID = HMAC-SHA1-128(PMK, "PMK Name" | MAC_AP | MAC_STA)

因此，如果返回包含RSN PMKID，那么就可以在无需客户端在线的情况下发起本地的暴力破解。事实上， **非常多**
路由器在第一次握手的EAPOL包中都会包含这个字段。

## KARMA & MANA

还记得前面介绍的Beacon
Frame吗？有的AP会定期像周围广播自己的存在，从而让客户端知道周围有哪些热点。但这只是其中一个方法，称为`被动扫描`；客户端还可以主动发送Probe
Request探测周围的WiFi，如果有WiFi响应则返回Probe
Response，返回对应的AP属性，从而让客户端发起连接，这称为`主动扫描`，主动探测又分为直接探测(Direct
Probe)和广播探测(Broadcast Probe)。

KARMA攻击的本质就是，监听客户端发送的`Directed Probe
Request`，然后伪造对应的热点信息，让客户端认为这是个之前连接过的热点，从而进行接入。

802.11协议中规定AP只能响应发给自己的Probe
Request，但KARMA并不准守这个规定，如果STA准守802.11，那么就会认为这是个合法的响应从而进行连接。

最初版本的KARMA攻击在2004年提出([KARMA Attacks Radioed Machines Automatically
](http://theta44.org/karma/))，但是在2014年时很多场景已经不再可用了，因此出现了更新的版本[MANA](https://github.com/sensepost/hostapd-mana/wiki/KARMA---MANA-Attack-Theory)。在更新的版本中，除了响应直接探测，还响应广播探测。

这一类伪AP的根本问题是802.11协议中没有清楚地定义客户端如何选择ESS以及如何在不同的ESS之间漫游，所以实现上就存在各种偏差。

一个使用MANA伪造AP和响应探测请求的例子如下：

![
](https://images.seebug.org/content/images/2020/03/a9c668a9-626e-4713-8ac3-e5face539ddd.png-w331s)

下面的窗口是通过aireplay发送deauth包令客户端掉线，从而连接上我们的恶意热点。

## Krack

Krack攻击可能大家都在新闻上看到过，前两年搞得沸沸扬扬，还做了官方网站和Logo，……Anyway，Krack就是`Key Reinstallation
Attacks`，即秘钥重装攻击。

在我们前面介绍WiFi握手的时候见过了双方更新秘钥的过程，秘钥的更新也称为安装(Key
Installation)。Krack攻击的原理就是通过重放握手信息，令客户端重新安装相同的秘钥。

当重装秘钥的时候，相关联的参数比如递增的发送包个数(即nonce)以及接收包数(即replay
counter)会恢复到初始值。WPA协议中没有明确规定这种情况下如何处理，因此很多实现就是正常安装，即重置这两个值。

重置之后就可以归类到nonce重用的密码学问题，感兴趣的可以参考[krack-paper](https://papers.mathyvanhoef.com/ccs2018.pdf)中的2.4节如何通过重置nonce和counter实现解密。

总之，重置秘钥之后就可以让攻击者解密本该加密的WPA数据，从而读取受害者的网络流量。这个漏洞还根据重置的是PTK、GTK以及其他内容申请了多个CVE，大部分是影响STA的握手应用，在Linux中是`wpa_supplicant`，但对于GTK其实也影响了内核，这个是对应内核upstream的patch信息：

    
    
    commit fdf7cb4185b60c68e1a75e61691c4afdc15dea0e
    Author: Johannes Berg <johannes.berg@intel.com>
    Date:   Tue Sep 5 14:54:54 2017 +0200
    
        mac80211: accept key reinstall without changing anything
    
        When a key is reinstalled we can reset the replay counters
        etc. which can lead to nonce reuse and/or replay detection
        being impossible, breaking security properties, as described
        in the "KRACK attacks".
    
        In particular, CVE-2017-13080 applies to GTK rekeying that
        happened in firmware while the host is in D3, with the second
        part of the attack being done after the host wakes up. In
        this case, the wpa_supplicant mitigation isn't sufficient
        since wpa_supplicant doesn't know the GTK material.
    
        In case this happens, simply silently accept the new key
        coming from userspace but don't take any action on it since
        it's the same key; this keeps the PN replay counters intact.
    
        Signed-off-by: Johannes Berg <johannes.berg@intel.com>

要说危害性，我感觉危害还是挺大的，好在目前的STA应用和内核大多已经修复了该问题。如果说存在密码学后门，这就是一个典型：利用理论和实现中的未定义行为造成偏差。

深入了解可参考下面的资料：

  * [krackattacks](https://www.krackattacks.com/)
  * [krack-paper](https://papers.mathyvanhoef.com/ccs2018.pdf)
  * [krack-scripts](https://github.com/vanhoefm/krackattacks-scripts)

## Kr00k

这是2020年2月份RSA大会上披露的一个漏洞([KR00K - CVE-2019-15126 SERIOUS VULNERABILITY DEEP
INSIDE YOUR WI-FI ENCRYPTION ](https://www.welivesecurity.com/wp-content/uploads/2020/02/ESET_Kr00k.pdf))，新鲜出炉。这是个芯片驱动实现的问题，主要影响Broadcom和Cypress网卡。

其核心漏洞点是在解除客户端关联后，其PTK会被置零，但是WiFi芯片会继续用置零的PTK发送缓冲中剩余的无线数据，攻击者收到这些数据后使用全零的PTK即可解密。

实际攻击中，攻击者需要不断令客户端关联/解除关联，即可不断地获得客户端发送的数据进行解密；同时由于部分路由器也受影响，因此可以获得下行的数据。

我个人的解读是这个漏洞可以泄露一些关键信息，但是不像Krack那样可以做到稳定的泄露，因此利用场景相对受限。比起后门般的Krack，Kr00t更像是一个漏洞。

漏洞详情以及PoC可以参考以下文章：

  * [KR00K - CVE-2019-15126 SERIOUS VULNERABILITY DEEP INSIDE YOUR WI-FI ENCRYPTION ](https://www.welivesecurity.com/wp-content/uploads/2020/02/ESET_Kr00k.pdf)
  * [R00KIE-KR00KIE. EXPLORING THE KR00K ATTACK](https://hexway.io/research/r00kie-kr00kie/)
  * [启明星辰ADLab的分析](https://mp.weixin.qq.com/s?__biz=MzAwNTI1NDI3MQ==&mid=2649614751&idx=1&sn=4d99cfb83923c62c6b8ab94012df39e7)

# 后记

本来这篇文章是想写如何偷WiFi密码的，但是写着写着就 ~~裂开~~ 展开了，因此顺便把之前放在Todo-List中的那些漏洞也一并拿出来进行研究分析。当然WiFi的安全问题不止这些，但是影响最大的还是协议设计中留下的坑。比如漫游的定义不清楚导致了KARMA，秘钥重装的不明确导致了Krack。这些坑还有多少谁也说不准，协议的更新到工业界的产品推出也需要时间，但我相信未来的无线安全性会越来越好——在众多学者、开发者以及安全研究人员的共同努力下。

# 参考资料

  * [Wireless lan security - Key Management](http://etutorials.org/Networking/Wireless+lan+security/Chapter+8.+WLAN+Encryption+and+Data+Integrity+Protocols/Key+Management/)
  * [Real 802.11 Security: Wi-Fi Protected Access and 802.11i](https://books.google.com/books?id=nnbD-FPpszMC&pg=PA210&lpg=PA210&dq=how+is+GMK+generate&source=bl&ots=LP4NjRTyaH&sig=ACfU3U2NRkgzwu1mC07WnS2HxKW3rRdLJA&hl=en&sa=X&ved=2ahUKEwjD3cK6nb3oAhWRdn0KHX2wBSMQ6AEwBXoECAoQAQ#v=onepage&q=how%20is%20GMK%20generate&f=false)
  * [4-WAY HANDSHAKE - wifi professional](https://www.wifi-professionals.com/2019/01/4-way-handshake)
  * [Evil Twin and Karma Attacks](https://posts.specterops.io/modern-wireless-attacks-pt-i-basic-rogue-ap-theory-evil-twin-and-karma-attacks-35a8571550ee)
  * [krackattacks](https://www.krackattacks.com/)
  * [KR00K - CVE-2019-15126 SERIOUS VULNERABILITY DEEP INSIDE YOUR WI-FI ENCRYPTION ](https://www.welivesecurity.com/wp-content/uploads/2020/02/ESET_Kr00k.pdf)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1159/>

