## 背景

 **在2018年1月8日美国拉斯维加斯的国际消费电子展(CES)上，Wi-Fi联盟发布了最新的WPA3加密协议，作为WPA2技术的的后续版本，并在2018年6月26日，WiFi联盟宣布WPA3协议已最终完成。与WPA3相关的最核心的文档为RFC7664，其中描述的是WPA3中最大的改进，就是将原来的四次握手协议换成了新的“蜻蜓秘钥交换协议”(Dragonfly
Key Exchange)，该协议将认证和秘钥交换两个功能合成于一个协议。号称可以解决WPA2中未解决的几个安全问题：**

> 1.离线密码破解——获得WPA2的四次握手包即可进行离线字典攻击，破解无线密码。
>
> 2.前向安全(Forward Secracy)——已知4次握手和无线密码的情况下，可以解密目标的所有通信流量。
>
> 3.KRACK等其他已知攻击方法。

由于WPA3还尚未普及，想来目前无论公众还是相关研究人员对WPA3的协议的实施细节所知应该并不多，所以笔者在仔细阅读RFC7664文档后，在此文中将做详细的分析讨论，以及指出可能的攻击方法，供其他相关研究人员参考。

## WPA3简介

本节中我们简单介绍一下WPA3相关的基本知识，在WPA2的基础上讨论在WPA3协议中做了哪些关键改进以及改进后在安全方面会有哪些提升。

![dreamstime_m_102039327.jpg](https://image.3001.net/images/20181022/15401385272718.jpg!small)

根据Wi-Fi联盟官方发布的文档，WPA3仍然分为WPA3个人级和WPA3企业级两种标准，其中，WPA3企业级认证与WPA2相比差别不大，仅仅将密钥长度增加到了192位（WPA2使用的是128位的加密密钥）仍然采用EAP-SSL，EAP-SIM/EAP-AKA之类的基于认证服务器的认证方法。

那么此次协议改进最大的地方在哪里呢？没错，改动最大的地方就是WPA3个人级相对于WPA2个人级的改进，根据官方的说法，WPA3个人级有如下几个提升：

> 1.更强的基于密码的认证安全（官方声称即使用户使用弱密码，仍然可以得到良好的保护。）
>
> 2.使用等量同步认证——一种更安全的设备间密钥交换协议，即蜻蜓协议，可以防止通通信流量被窃听，即使被攻击者获取了握手过程，也无法解密流量。
>
> 3.密钥长度扩展到192位。

其中官方宣称的第1点建立的基础就是因为引入了蜻蜓秘钥交换协议，该协议作者在该协议的说明中声称可以避免离线字典攻击，这一点应该就是以上第1所述的可保护弱密码的原理。至于3，其实128位的对称密钥已经足够，此处提升仅仅有理论上的安全提升。看来WPA3上最明显的改进就是替换了密钥交换算法，在接下来的章节中我们就着重分析一下这个蜻蜓算法。

## WPA2-PSK回顾

在开始分析蜻蜓算法之前，为了更有效的对比WPA2和WPA3密钥交换算法的差异，这里先简单介绍一下WPA2协议中设备入网认证的过程，见下图。

![图片 1.png](https://image.3001.net/images/20181022/15401382128763.png!small)

事实上一次完整的WPA2入网过程中，在上图所述的密钥交换过程之前还需要3次交互，分别是客户端发送Probe Request，服务器回应Probe
Response，客户端发送Authentication Request服务器回应Authentication
Response，接着客户端发送Association Request，服务器回应Association
Response，接着开始上图所示密钥交换过程。密钥交换过程分为如下几步：

> 1.AP发送一个随机数AP
> Nonce给STA，STA通过AP的ESSID，以及自己的MAC地址，AP的MAC地址，PSK，AP发送的随机数以及自己生成的STA
> Nonce，这6个参数生成PMK和PTK。
>
> 2.STA发送第1步生成的随机数STA
> Nonce给AP，并使用上一步生成的PTK生成该数据包的消息校验值MIC附在数据包后面发送给AP，AP通过包括STA
> Nonce在内的同样6个参数生成自己的PMK和PTK，并用PTK校验STA发送的数据包的MIC值是否匹配，如果匹配则说明PSK正确认证通过。
>
> 3.AP将组密钥（即GTK用于加密广播以及组播包的密钥）用PMK加密并附上MIC发送给STA。
>
> 4.STA校验MIC后装入GTK并回复ACK，密钥交换结束开始加密通信。

如果你觉得以上写的太纠结，为了照顾大家特此附上代码：

    
    
    #!/usr/bin/env python
    
    import hmac
    from hashlib import pbkdf2_hmac,sha1,md5
    
    def PRF(key,A,B):
        nByte = 48
        i = 0
        R = ''
    
        while ( i <= ((nByte*8 + 159)/160)):
            hmacsha1 = hmac.new(key,A+"\x00" + B + chr(i),sha1)
            R += hmacsha1.digest()
            i += 1
        return R[0:nByte]
    
    def MakeAB(aNonce,sNonce,apMac,cliMac):
        A = "Pairwise key expansion"
        B = min(apMac,cliMac) + max(apMac,cliMac) + min(aNonce, sNonce) + max(aNonce, sNonce)
        return (A,B)
    
    def MakeMIC(pwd,ssid,A,B,data,wpa = False):
        pmk = pbkdf2_hmac('sha1',pwd,ssid,4096,32)
    
        ptk = PRF(pmk,A,B)
    
        hmacFunc = md5 if wpa else sha1
    
        mics = [hmac.new(ptk[0:16],i,hmacFunc).digest() for i in data]
    
        return (mics,ptk,pmk)
    
    def calcKey(essid,psk,apMac,cliMac,data0,data1,data2,data3):
    
        ssid = essid
        #print ssid
    
        aNonce = data0[17:17+32]
        #print aNonce.encode('hex')
    
        sNonce = data1[17:17+32]
        #print sNonce.encode('hex')
    
        apMac = apMac.replace(':','').decode("hex")
    
        cliMac = cliMac.replace(':','').decode("hex")
    
        mic1 = data1[81:81+16]
    
        data1 = data1.replace(mic1,'\x00'*16)
    
        mic2 = data2[81:81+16]
    
        data2 = data2.replace(mic2,'\x00'*16)
    
        mic3 = data3[81:81+16]
    
        data3 = data3.replace(mic3,'\x00'*16)
    
        A,B = MakeAB(aNonce,sNonce,apMac,cliMac)
    
        mics,ptk,pmk = MakeMIC(psk,ssid,A,B,[data1,data2,data3])
    
        print "pmk:",pmk.encode('hex')
    
        print "ptk:",ptk.encode('hex'),"len:",len(ptk)*8
    
        print "desired mic1:",mic1.encode('hex')
    
        print "acture mic1:",mics[0].encode('hex')[:-8]
    
        if (mic1==mics[0][:-4]):
            print "MIC1 MATCHED"
    
        print "desired mic2:",mic2.encode('hex')
    
        print "acture mic2:",mics[1].encode('hex')[:-8]
    
        if (mic2==mics[1][:-4]):
            print "MIC2 MATCHED"
    
        print "desired mic3:",mic3.encode('hex')
    
        print "acture mic3:",mics[2].encode('hex')[:-8]
    
        if (mic3==mics[2][:-4]):
            print "MIC3 MATCHED"
    
        return ptk
    

从上面的过程可以看出，其中最重要的参数就是PTK，每个STA和AP之间通信的PTK是不同的，这也意味着一旦PTK被获知，就可以解密该STA和AP之间通信的所有流量。那么纵观整个交换过程，最重要的参数就是PSK，PSK参与了密钥的计算，且AP和STA对于PTK密钥的计算算法是对称的，这或许就是WPA2不提供前向安全的最重要原因，那就是，只要握手过程被获取，任何知道PSK的人都可以计算出PTK，从而解密所有通信流量。并且，由于算法是对称的，只要抓取握手包，就可以通过离线校验MIC的方式来验证PSK的正确性，这就是aircrack-ng抓取握手包跑包破解WIFI密码的原理。

好了，至此我们可以看出，对称的密钥生成算法或许是WPA2安全性的最大缺陷！因为这一点，导致WPA2可以被离线字典攻击，同时，在PSK公开的网络中，例如星巴克，酒店之类的场景，PSK被很多人都知道，且一旦密钥被攻击者获取，就无法保证用户的数据安全！

## WPA3 Dragonfly(蜻蜓)密钥交换算法

在大致了解了WPA3的改进以及WPA2优劣后，我们可以进入正题，分析WPA3中最核心的算法——蜻蜓秘钥交换算法，分析的过程中会牵扯到一些非对称加密的知识，后面我会一一说明。

蜻蜓算法从本质上说也是一个基于离散对数这个难解问题的算法，也就是说蜻蜓算法可以使用普通的整数有限域或者椭圆曲线来实现，由此可见，蜻蜓算法和Diffie-Hellman算法十分相似。我们可以很容易的先对比D-H算法中的离散对数，为了简单起见，下面的讨论我们以有限域上的情况来做例子，椭圆曲线的实现同理可以类比。首先我们取一个大质数p，通常1024位以上，我们通常记Z_p^表示模p的剩余类乘法群，Q是一个Z_p^上的q阶（q也是素数）子群。那么蜻蜓算法的密钥交换和认证过程如下：

>
> 前3次交互，即Probe+Authentication+Association过程同WPA2。密钥交换第一步，对于一次正常的认证过程，AP和STA共享了同样的一个PSK，我们首先要将这个PSK映射为Q上的一个元素P，映射算法有很多种，可以保证PSK到P的唯一映射，具体方法这里不做详细讨论，即我们只要知道映射完成之后，我们可以通过PSK得到一个唯一的整数P即可。
>
> 第二步，AP生成随机的两个参数r_A和m_A，(1<r_A,m_A<q)，然后计算出参数secret记作s_A,其中s_A=(r_A+m_A ) mod
> p和参数E_A=P^(-m_A ) mod p，然后将s_A和 E_A发送给STA。
>
> 第三步，STA同样生成r_B和m_B，(1<r_B,m_B<q)，secret参数s_B=(r_B+m_B ) mod p
> q，以及E_B=P^(-m_B ) mod p，然后将s_B和 E_B发送给AP。
>
> 第四步，AP计算ss=〖(P^(s_B ) E_B)〗^(r_A )=P^(r_A r_B ) mod
> p。kck|mk=KDF-n(ss,"Dragonfly Key Derivation")， KDF-n是一个密钥导出算法。
>
> 第五步，STA计算ss=〖(P^(s_A ) E_A)〗^(r_B )=P^(r_A r_B ) mod
> p，kck|mk=KDF-n(ss,"Dragonfly Key Derivation") 。
>
>
> 第六步，AP计算参数A=H(kck|sA|sB|EA|EB|idA)发送给STA，其中H是一个hash算法。其中idA是AP的发送方标识，可以通过密码以及双方参数通过固定算法计算所得。
>
> 第七步，STA计算参数B=H(kck|sB|sA|EB|EA|idB)发送给AP，idB同理
>
> 第八步，AP和STA分别使用自己的参数计算对方的hash的值，并与对方发送过来的值想比较，如果相等，则通过认证，否则断开连接。
>
> 第九步，若第八步的验证通过，则双方交换的相同密钥为第5,6步中mk。

更直观的过程大家看下图：

![图片 2.png](https://image.3001.net/images/20181022/15401382291621.png!small)

上面就是WPA3中蜻蜓密钥交换算法的主要内容了，由于WPA3尚未大规模商用，因此有很多实现细节还尚不清楚，要真正的实际使用还有很多工程方面的工作需要考虑，这些不是本文所关心的。因此后面我们仅做一个理论性的讨论，上面的过程是对RFC7664里面所述协议的简化模型，源文档写的非常冗长，但核心就在上面的过程里，如果对协议细节有兴趣可以参考原文档。

## 蜻蜓算法安全性分析

从上面的密钥交换过程可见，这个算法确实如之前介绍所说，将认证和密钥交换两个功能合二为一，首先进行PSK认证，认证通过了密钥才会生成，而对于WPA2，前两次握手已经计算出密钥了，后第3第4次握手是在对密钥是否一致进行校验，由此可见WPA3的新协议确实对于提高安全性有一定帮助。

### 关于前向安全的分析

而对于前向安全的保证在于，即使知道PSK，攻击者可以推知P，但由于攻击者并不知道r_A或者r_B，因此攻击者无法通过E_A或者E_B计算ss，因为要知道r_A或r_B必须先知道m_A或m_B，而通过E_A求m_A是一个离散对数问题，这是个难解问题，知道m_A求E_A很容易，但是反过来很难，用这个非对称性质来保证即使攻击者知道PSK也无法根据握手过程计算出K，从而保证前向安全。

### 关于中间人攻击

从以上密钥交换算法的细节可以看出，对于同样知道PSK的攻击者来说，这种算法也存在D-H密钥交换算法的毛病，就是无法防止中间人攻击！不过考虑到无线信道想要完成中间人劫持并不容易，所以这样考虑也尚且合情合理，不过话说回来，WiFi网络里中间人攻击并不是完全不可能的，只是实施有一定条件而已，因此在这一点上，我认为仍然重蹈了WPA2中“只能保证PSK不泄露情况下安全”的覆辙。

### 关于离线字典攻击

接下来我们来看看字典攻击的情况，事实上蜻蜓算法的作者并没有给出蜻蜓算法可以杜绝离线字典攻击的严格证明，仅仅给出了一个主观性的分析：

首先，作为攻击者只能被动监听流量的情况，则如上面所说的，攻击者无法得知r_A和r_B，要得到r_A和r_B需要计算离散对数，这是一个难解的问题，缺少这两个参数使得攻击者无法做仅仅代入密码验证的方式，因此，仅仅抓取握手包，字典攻击无法进行。

然后，讨论主动的攻击者，攻击者此时能够主动和AP或者STA进行虚假的交互，此时作者假设攻击者会选择一个随机的m_B值，计算P=G^(m_B
)发送给AP，其中G是Q的一个群生成元，这时候密码可以表示成G的某个幂次，这时候AP计算的ss值则是密码P的某个幂次，这时候假设攻击者期望代入P进行校验，即使成功求出正确的ss，要计算密码也需要计算离散对数，这是个难解问题，因此作者认为此时离线字典攻击也没有意义。

最后，我们再看看在D-H算法中的小子群攻击对蜻蜓算法是否有效，小子群攻击也需要攻击者主动发起一次交互，类比D-H算法中的小子群攻击的思想，我们知道，如果用S表示Q的一个小子群Q'中的元素，那么S的任意次方也是Q'中的元素，因为Q是质数阶群，所以子群一定存在，只要我们能找到一个元素个数足够小的子群，取元素S，并且随机选择s_B，将E_B=S发送给AP，这时候AP会计算ss=〖(P^(s_B
) E_B)〗^(r_A )=P^(s_B r_A ) S^(R_A )=〖(P^(r_A ))〗^(s_B )
R的哈希值，并发送给STA，上式中，由于S是子群元素，所以S的r_A次方我们记作R，仍然是小子群中元素，而r_A虽然不知道，但是P^(r_A
)=P^(s_A-m_A )=P^(s_A )
E_A，即可以使用s_A和E_A来计算，这时候我们未知的参数只有P和R，我们可以通过PSK生成离线字典P，然后计算ss的值，并且作hash比较，直至找出P，只要S的规模足够小，这种离线攻击方式还是有实施的可能性的，只不过要完成这种攻击，攻击者需要主动和STA或者AP完成至少一次交互，提高了攻击成本。但实际上对于弱密码来说，仍然是不安全的！

## 结论

本文详细分析了WPA3中的蜻蜓密钥交换算法，虽然对于工程化的实施细节尚不明确，本文从理论角度对于其安全性得出的结论总结如下：

> 1.WPA3使用蜻蜓算法，可以防止被动的攻击者窃取数据，即可以提供前向安全。
>
> 2.因为WPA3个人级并不建立在公钥信任的基础上，因此对于同样知道PSK的攻击者来说，无法防止中间人攻击。
>
>
> 3.无法完全防止离线字典攻击，一定条件下字典攻击是可以实施的，不过相比WPA2，提高了攻击成本，但如果期待WPA3协议能很好的保护12345678这种弱密码，那还是想多了。
>
>
> 4.至于对KRACK之类的密钥重装攻击的防御，由于对握手过程的丢包处理机制细节还不明确，因此不确定能否防止此类攻击，但从中间人攻击的角度，此类攻击在WPA3中仍然存在可能性。

 ***本文作者：阿里安全技术，转载请注明来自FreeBuf.COM**

