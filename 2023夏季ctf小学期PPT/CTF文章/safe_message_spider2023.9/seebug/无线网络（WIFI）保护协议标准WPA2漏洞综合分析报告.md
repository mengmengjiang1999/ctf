作者：[安天安全研究与应急处理中心](http://www.antiy.com/response/krack.html "安天安全研究与应急处理中心")

#### 1 概述

欧洲鲁汶大学的博士后安全研究员 Mathy Vanhoef 在10月15日披露无线网络（Wi-Fi）保护协议标准 WPA2 的高危漏洞[1,2]。漏洞允许在
Wi-Fi 范围内的攻击者监听计算机和接入点之间的 Wi-Fi 流量。该漏洞影响协议本身，且对 WPA 和 WPA2 均有效，因此支持 WPA/WPA2
协议的软件或硬件均受到影响。

漏洞披露后，安天与炼石的工程师迅速响应，对该漏洞展开联合分析，形成此报告。

#### 2 漏洞分析

WPA全名为 Wi-Fi Protected Access，有 WPA 和 WPA2 两个标准，是一种保护无线网络（Wi-Fi）安全的协议[3]。WPA
实现了IEEE 802.11i标准的大部分，是在802.11i完备之前替代WEP的过渡方案，后被 WPA2 取代。由于 WPA 和 WPA2
均基于802.11i，因此在技术层面上几乎是相同的，主要区别在于WPA2要求支持更安全的CCMP。WPA 和 WPA2
均使用802.11i中定义的四次握手，客户端（Station, STA）和接入点（Access Point,
AP）通过四次握手相互验证和协商名为成对临时密钥（Pairwise Transient Key, PTK）的会话密钥。PTK
通过成对主密钥（Pairwise Master Key, PMK）、AP 随机数 ANonce、STA 随机数 SNonce 和双方 MAC
地址等计算生成，其中 PMK 由登录密码等双方均已知的信息计算生成。而后续正常数据加密所使用的临时密钥（Temporal KEY, TK）即派生自
PTK。各密钥、参数的关系如下图所示。

![](https://images.seebug.org/content/images/2017/10/fd12db4e-0b63-49aa-a7c7-6951a60b8f9f.png-w331s)
图 2 ‑ 1 四次握手中各密钥、参数关系

四次握手的过程可概括如下：

  1. AP 发送自己的随机数 ANonce 给 STA；
  2. STA 生成随机数 SNonce，计算出 PTK，并将 SNonce 和信息完整性校验码 MIC 发送给 AP；
  3. AP 收到 SNonce，计算出 PTK（此时双方都已有 PTK），将组密钥GTK加密后连同 MIC 发给 STA；
  4. STA 收到 GTK，安装 PTK 和 GTK，发送 ACK 确认。AP 收到确认后安装 PTK。

![](https://images.seebug.org/content/images/2017/10/9183cc81-fe87-404b-9f0f-38cc0dfa8a74.png-w331s)
图 2 ‑ 2 四次握手过程

Vanhoef 将披露的漏洞攻击命名为 KRACK（Key Reinstallation Attack），攻击者通过在 Wi-Fi 范围内利用中间人的手段对
WPA/WPA2
协议的四次握手交互验证的第三阶段进行攻击。此时受害者已经安装了密钥，通过中间人手段进行增量式重放攻击后，迫使受害者使用攻击之前的密钥流加密数据。鉴于
WPA/WPA2 为对称加密，因此可以通过简单的明文密文得到可重复利用的密钥流。攻击者一旦获得密钥流就可以对 Wi-Fi 流量数据解密。

##### 2.1 利用原理

此漏洞利用的核心在于密钥重装，该模式基于WPA/WPA2协议中建立连接时的四次握手流程。在四次握手过程中，AP和客户端将会协商一个用于加密接下来通信数据的加密密钥，客户端在收到AP发来的第三次握手的信息（消息3）后会核实MIC，若正确将会安装加密密钥key，用于加密正常的数据帧，并向AP发送响应作为确认。根据协议规则，若AP无法正确接收到确认，将引发数据重传，重新发送消息3。客户端每次接收到消息3时都会重装相同的会话密钥。攻击者可利用此次握手过程，暴力增量式发送消息3，从而强制重置数据保密协议使用的增量传输数据包数（nonce）和接收重放计数器，导致密钥重用。攻击者可以通过这种方法重放、解密和/或伪造数据包。

KRACK攻击可分为4种场景：

  1. 客户端（受害者）接受消息3的明文重传时的密钥重装攻击；
  2. 受害者仅接受消息3的加密重传时的密钥重装攻击；
  3. 对组密钥握手攻击即时密钥安装；
  4. 对组密钥握手攻击延迟密钥安装。

![](https://images.seebug.org/content/images/2017/10/1db267e9-8d53-4ae0-9dc9-218028a79020.png-w331s)
图 2 ‑ 3 接受消息3明文重传时执行密钥重装攻击示意图

图2-3中展示了攻击者解密一个密文数据包的攻击流程。如果攻击者已知第一个发送的密文数据包的明文，则可以恢复出用于加密该明文数据的密钥流。由于四次握手协议的设计允许通过重传消息3来重装密钥PTK和GTK，并重置待发送数据包的nonce值，导致客户端使用相同的密钥流加密下一个数据包，进而导致攻击者可以解密客户端发送的下一个密文数据包。

上述解密过程是基于攻击者知道第一个数据包明文这一前提，然而攻击者有时无法预知数据包中的全部字段值（比如可能存在的随机字段），
所以攻击者可能需要多次重传消息3以收集更多数据来进行解密。图2-3中仅展示了恢复一个密文数据包的攻击过程，但是攻击者可以通过多次重传并合理选择重传时机（等待客户端在重传之前发送足够多的数据），甚至通过解除对客户端的认证来迫使客户端重新执行四次握手协议，实现解密多个数据包的目的。

![](https://images.seebug.org/content/images/2017/10/2fbf69c4-c955-4f65-98e9-928d3c3a8eeb.png-w331s)
图 2 ‑ 4 接受消息3明文重传时使用全0替换真实密钥攻击示意图

由于2.4和2.5版本的 wpa_supplicant（Android
6及以上的版本）在收到重传的消息3后对密钥重装过程的错误实现，使得在客户端接收到攻击者重传的消息3后，数据加密密钥 TK
被置为全0。这一错误实现极大的简化了密文恢复攻击，利用数据加密密钥为全0这个信息，攻击者不再需要已知明文条件就可以解密客户端发送的后续数据包。基于上述背景，攻击者通过中间人攻击迫使客户端改用全0的密钥之后，就可实现对客户端流量劫持，监控并篡改客户端发出的全部数据。

##### 2.2 KRACK攻击中nonce重用的密码分析

Nonce
重用引发的后果与所采用的数据保密协议密切相关。三种数据保密协议TKIP、CCMP和GCMP所采用的数据加密算法分别为流密码RC4、认证加密算法AES-CCM和认证加密算法AES-GCM，其中AES-CCM和AES-GCM的加密部分都是基于CTR模式的流式加密。即可认为TKIP、CCMP和GCMP三种协议均采用流式加密，即明文数据与算法生成的密钥流按比特逐位异或后得到密文数据。流式加密的问题是在密钥固定的条件下重用nonce时总会生成相同的密钥流。这一特性可以被利用来解密数据包。

![](https://images.seebug.org/content/images/2017/10/dd2aac7d-078d-40d0-a8c7-42014de27452.png-w331s)
图 2 ‑ 5 CTR模式下加密过程示意图

上图展示了CTR模式下用密钥k和计数器ctr加密明文消息![](https://images.seebug.org/content/images/2017/10/e9bb48c9-242c-4ac2-a0f8-ecceaa2fb82b.png-w331s)的过程，其中![](https://images.seebug.org/content/images/2017/10/08e4ed1a-4c80-4c4d-8a4c-05c55971887b.png-w331s)分别表示一个分组长度（采用AES算法时为128比特，明文消息长度并不一定是分组长度的整数倍）。注意图中没有展示CCM和GCM模式中应用CTR模式进行加密时所涉及到的一些细节。正确使用的情况下，计数器ctr的值不断累加（值不重复！！）并在算法和密钥的作用下生成具有强伪随机特性的密钥流，![](https://images.seebug.org/content/images/2017/10/6cd2ca53-8a36-4f5c-a887-21134bd105ad.png-w331s)
则对应的密文为![](https://images.seebug.org/content/images/2017/10/8dcc4aa0-39cf-410a-bcf3-4738d493f01d.png-w331s)
TKIP中基于RC4流密码的加密过程与此类似不再赘述。

在KRACK的攻击中，通过重放消息3能够达到迫使受害者重用nonce，导致上述加密过程中相同计数器ctr值的重复出现。相同密钥相同计数器ctr条件下，生成的密钥流![](https://images.seebug.org/content/images/2017/10/6380356a-bcc4-4038-b957-73b765d35c35.png-w331s)值相同，攻击者可据此解密数据包。用KeyStream表示该密钥流，P1和P2表示两组明文数据，假设KeyStream，P1，P2具有相同的比特长度，则两组明文对应的密文分别为：

    
    
    C1 = P1 ^ KeyStream
    C2 = P2 ^ KeyStream

其中 ^ 表示逐比特异或操作。攻击者可以通过网络收集到密文C1和C2，如果攻击者知道密文C1对应的明文P1，则可以据此恢复明文P2的信息：

    
    
    P2 = C2 ^ keystream = C2 ^ (P1 ^ C1)

在实际情况中，通常能找到已知内容的数据包，所以可以认为在密钥固定的条件下重用nonce时获得密文数据包可根据上述过程解密。即使已知内容的数据包确实无法获得，当对消息类型有足够的知识（比如消息为英文字符）的条件下，也可能解密还原出明文。值得注意的是，虽然nonce重用会导致密文数据包被解密，但并不导致密钥TK、PTK、PMK以及WiFi登陆密码的泄露，因此WPA2的密码体系只是被绕过，并没有被攻破。分组密码算法（AES）本身的安全性保证了即使在输入![](https://images.seebug.org/content/images/2017/10/8163ad0c-2629-4d2c-bd56-00b6071df2aa.png-w331s)
和输出![](https://images.seebug.org/content/images/2017/10/980ae948-ecb5-44e0-9643-c0637ba20915.png-w331s)
已知的条件下，加密密钥k也不会泄露。

TKIP、CCMP和GCMP三种数据加密协议，在数据机密性之外，还提供数据完整性保护。而重用nonce在不同的数据加密条件下在数据完整性保护方面会带来不同等级的安全隐患。

使用TKIP协议时，当解密完整的TKIP数据包之后（包括MIC字段），攻击者可进一步攻击Michael算法获得相应的MIC密钥。这是由于Michael算法本身的脆弱性导致的，在给定明文数据以及MIC值的条件下，攻击者可恢复出MIC密钥。借助恢复出的MIC密钥，攻击者可伪造该数据传输方向上的数据帧（TKIP在不同的数据传输方向上使用不同的MIC密钥）。

使用CCMP协议时，虽然有研究展示了在重用nonce条件下数据伪造攻击的可能性，但都是停留在理论层面的攻击，难以在实际中生成真正的伪造数据包，仅能执行重放攻击以及数据包解密。

使用GCMP协议时nonce重用导致的安全问题最为严重。nonce重用使得攻击者能够恢复出GCM模式中的认证密钥（H），由于GCMP协议在数据传输的两个方向上使用相同的密钥进行数据保护，这赋予了攻击者在数据传输的两个方向上均可伪造数据包的能力。作为认证加密的一种工作模式，GCM模式由CTR加密算法以及GHASH验证算法组合而成，其中CTR算法部分直接采用传递给GCM模式的密钥k进行加密，而GHASH运算所需的验证子密钥H是AES算法利用密钥k加密全128比特的全0明文得到的128比特密文值。法国密码学家Joux指出当nonce重用时，攻击者可恢复出验证子密钥H的值（注意从H的值无法推算出GCM的输入密钥，这是由AES算法本身的安全性保证的）。攻击者获得H的值之后，GCMP所提供的数据完整性保护形同虚设，也因此攻击者可以伪造数据包。

总体来说，对于TKIP和GCMP，KRACK攻击影响极其严重，攻击者可以对数据包重放、解密和伪造。对于CCMP，虽然攻击者不能伪造，但是基于TCP/IP协议的特点，只要攻击者能够获得序列号，攻击者就可以劫持TCP流并将恶意数据注入到其中，后果同样十分严重。

#### 3 漏洞影响及响应情况

通过此漏洞可实现解密Wi-Fi流量数据、数据包重组、TCP连接劫持、HTTP内容注入等。KRACK攻击是通用的，适用于连接或使用WPA/WPA2的WiFi网络的所有类型设备。针对个人和企业网络以及所使用的任何加密套件（WPA-TKIP，AES-CCMP和GCMP）都有效，包括Android，iOS，Windows，Linux， MacOS，
OpenBSD以及嵌入式和物联网（IoT）设备。尤其是Android 6及以上的版本，研究人员表示可针对Android 6系统客户端
wpa_supplicant “完美攻击”，并且该攻击技术易于实现。根据安天移动安全统计数据，Android设备中Android 6系统占比约为41.9%。

由于此次漏洞影响较大，范围较广，供应商纷纷发起响应或发布补丁，部分供应商响应情况见下表：

表 3 ‑ 1 部分供应商响应情况[4]
![](https://images.seebug.org/content/images/2017/10/bdb4cf9e-b6c5-4370-9bfd-5060af8c5edf.png-w331s)
![](https://images.seebug.org/content/images/2017/10/e82c8e10-92cb-44fa-9cdd-cfaff1369b43.png-w331s)

注：如表中链接无法打开，可以从参考资料4中获取。

我们对表中Linux对应的八个补丁进行了分析，下面展示了各个补丁的作用原理。

1.`ebased-v2.6-0001-hostapd-Avoid-key-reinstallation-in-FT-handshake.patch`

在握手阶段Reassociation-Response时避免将TK重新安装到驱动程序部分，防止密钥重装攻击。

![](https://images.seebug.org/content/images/2017/10/b5998957-4c86-4964-bd45-062fb6576df0.png-w331s)

另外，只有在TK确认已经被卸载时，才允许安装配置，且不允许重复安装(当且仅允许成功配置一次)
![](https://images.seebug.org/content/images/2017/10/5422f3a4-ff0c-4f97-af22-ddc1fdf9acd9.png-w331s)

2.`rebased-v2.6-0002-Prevent-reinstallation-of-an-already-in-use-group-ke.patch`

跟踪当前正在使用的GTK和IGTK，当接收到(可能重传)的第一次握手阶段的消息或WNM-睡眠模式响应时，如果密钥已经在使用中，则不安装新的密钥。这阻止了攻击者欺骗客户端去重置或更改与组密钥关联的序列计数器的行为。

安装igtk时：
![](https://images.seebug.org/content/images/2017/10/fd9073b4-f69d-4c18-97e0-788762a5d8b0.png-w331s)

WNM-睡眠模式响应时：
![](https://images.seebug.org/content/images/2017/10/b98b8cdd-950b-42c5-af44-a3238901d8de.png-w331s)

3.`rebased-v2.6-0003-Extend-protection-of-GTK-IGTK-reinstallation-of-WNM-.patch`

这个补丁追踪最后配置的GTK / IGTK值，分别与EAPOL-Key帧和WNM-睡眠模式帧配合，因为当这两种不同的机制的GTK /
IGTK发生变化时候，跟踪单个值不足以及时发现检测可能的密钥重新配置行为。

记录两种模式下的GTK：

![](https://images.seebug.org/content/images/2017/10/61022f11-1429-4ba1-87f8-09c5742c31f6.png-w331s)

记录两种模式下的Igtk：

![](https://images.seebug.org/content/images/2017/10/c21fdd28-acb1-41e3-88c2-bc15cb821983.png-w331s)

4.`rebased-v2.6-0004-Prevent-installation-of-an-all-zero-TK.patch`

跟踪PTK是否已经安装到驱动程序，并且TK部分已经从内存中清除。 这样可以防止攻击者欺骗客户端来安装全零TK。

![](https://images.seebug.org/content/images/2017/10/6c7654b6-cbbf-4d3a-a3cf-35d07dbe5aa5.png-w331s)

5.`rebased-v2.6-0005-Fix-PTK-rekeying-to-generate-a-new-ANonce.patch`

用于PTK rekeying的授权状态机，会在随机数生成的时候绕过authenication2状态，而直接进入之PKT-START状态，因为此时无需再次确认PMK，可能导致随机数不“随机”，或遭致其他问题。

针对此问题，当切换至PTKSTART状态时，便生成一个新的ANonce。

![](https://images.seebug.org/content/images/2017/10/8bdde74b-c0d5-4448-9679-f5ab092d5099.png-w331s)

6.`rebased-v2.6-0006-TDLS-Reject-TPK-TK-reconfiguration.patch`

当成功配置TPK-TK后，禁止重新配置相同的参数至驱动。

![](https://images.seebug.org/content/images/2017/10/111bb677-3bc9-40b2-9b42-bf0f3bdb491a.png-w331s)
![](https://images.seebug.org/content/images/2017/10/d03ee282-6f08-43d9-a5c6-f050f47f0517.png-w331s)

7.`rebased-v2.6-0007-WNM-Ignore-WNM-Sleep-Mode-Response-without-pending-r.patch`

如果WNM-睡眠模式尚未使用，则忽略对应的WNM-睡眠模式请求。这可以避免处理意外的重传数据帧。

![](https://images.seebug.org/content/images/2017/10/6dcdb406-ebec-4e83-8a3a-ef9343a3de3e.png-w331s)

8.`rebased-v2.6-0008-FT-Do-not-allow-multiple-Reassociation-Response-fram.patch`

驱动部分除非在客户端明确请求一个新的连接时才会开启一个连接事件。不过，重新配置相同的成对密钥或组密钥会导致nonce被重用的问题，因此要进行额外的检查以避免恶意攻击的发生，包括因为某种环境因素导致意外收到重传数据包的情况。

![](https://images.seebug.org/content/images/2017/10/0a648957-fa6b-44be-9409-79b414dac963.png-w331s)

#### 4 结论

KRACK漏洞利用主要针对WPA/WPA2的四次握手过程，没有利用AP接入点，而是针对客户端的攻击。因此，用户的路由器可能不需要更新。对于普通家庭用户，应多关注各终端设备厂商的安全公告，及时更新配置或打补丁，优先更新笔记本电脑和智能手机等客户端。

对该漏洞的利用并没有破坏密码体系本身，而是对实现过程进行了攻击，因此基本可以绕过所有的安全监控设备。利用该漏洞能够在一个良好实现的网络环境中，通过良好实现的WiFi打开攻击面，为后续攻击打开通路。

目前使用WPA2的大多数家庭和商业无线应用客户端升级相对容易，但对于数百万难以及时更新的IoT无线设备，可能造成巨大影响。请大家保持警惕，我们会持续关注相关事件并积极应对。

#### 附录：参考资料

  1. [Mathy Vanhoef, Frank Piessens. Key Reinstallation Attacks](https://www.krackattacks.com/ "Mathy Vanhoef, Frank Piessens. Key Reinstallation Attacks")
  2. [Mathy Vanhoef, Frank Piessens. Key Reinstallation Attacks: Forcing Nonce Reuse in WPA2](https://papers.mathyvanhoef.com/ccs2017.pdf "Mathy Vanhoef, Frank Piessens. Key Reinstallation Attacks: Forcing Nonce Reuse in WPA2")
  3. [Wikipedia. WPA](https://zh.wikipedia.org/wiki/WPA "Wikipedia. WPA")
  4. [Kristate, Github. Vendor Response](https://github.com/kristate/krackinfo#vendor-response-complete "Kristate, Github. Vendor Response")

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/420/>

