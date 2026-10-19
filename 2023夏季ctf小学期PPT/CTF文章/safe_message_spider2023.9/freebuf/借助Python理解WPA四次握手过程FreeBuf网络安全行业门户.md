环境准备  

在正式开始分析之前，先要准备一下软件和分析对象。

## 系统环境

本次使用的操作系统是Windows10 1909，部分需要Linux的使用虚拟机安装的Kali进行。

代码部分，解释器版本为Python 2.7。

数据包分析工具使用经典的Wireshark。

## 数据准备

由于不同的加密方法和参数对握手包的影响较大，因此分析对象使用了Wireshark官方给出的WPA数据包。

该数据包可以在<https://wiki.wireshark.org/HowToDecrypt802.11>页面上进行下载：

![image-20200629105537200.png](https://image.3001.net/images/20200630/1593489330_5efab7b21c140.png!small)

  

## 手动捕获握手包

额外说明一下，如果想自己捕获设备的WPA握手包，则需要额外的软件，并将网卡置为`Monitor Mode`。下面简单介绍一下。

 **Windows平台** ：在Windows平台下想要捕获802.11管理帧，需要使用微软官方的软件[Microsoft Network
Monitor](https://www.microsoft.com/en-us/download/details.aspx?id=4865)。它的安装和使用也相对比较方便，网上也有相当多的教程，如《[windows下抓取802.11管理包](https://cstriker1407.info/blog/windows-80211-frame/)》。有一点需要注意，该软件在“扫描设置（Scanning
Options）”中开启`Monitor Mode`后，该窗口不能关闭，否则会退出：

![20150905181951_10373.png](https://image.3001.net/images/20200630/1593489350_5efab7c61a25d.png!small)

 **Linux平台** ：在Linux平台下，可以借助我们熟悉的`aircrack-ng`套件来设置网卡的`Monitor
Mode`，并使用`Wireshrak`来获取和查看数据。此处以Kali为例，其他Linux系统可以自行安装相关套件。

设置监听模式的命令为：

    
    
    root@kali:~# airmon-ng start wlan0

其中`wlan0`是网卡的名称。若出现以下情况：

    
    
    root@kali:~# airmon-ng start wlan0  
    ​  
    Found 2 processes that could cause trouble.  
    If airodump-ng, aireplay-ng or airtun-ng stops working after  
    a short period of time, you may want to run 'airmon-ng check kill'  
    ​  
        PID Name  
       1959 NetworkManager  
       1989 wpa_supplicant  
    ​  
    PHY Interface   Driver      Chipset  
    ​  
    phy0    wlan0       rt2800usb   Ralink Technology, Corp. RT2870/RT3070  
    ​  
            (mac80211 monitor mode vif enabled for [phy0]wlan0 on [phy0]wlan0mon)  
            (mac80211 station mode vif disabled for [phy0]wlan0)  
    ​

说明网卡被占用，需要使用`airmon-ng check kill`命令来结束占用进程：

    
    
    root@kali:~# airmon-ng check kill  
    ​  
    Killing these processes:  
    ​  
        PID Name  
       1989 wpa_supplicant  
    ​  
    root@kali:~# airmon-ng start wlan0  
    ​  
    ​  
    PHY Interface   Driver      Chipset  
    ​  
    phy0    wlan0mon    rt2800usb   Ralink Technology, Corp. RT2870/RT3070  
    ​

这里网卡名称会变成`wlan0mon`，需要注意。

但是，直接设置后抓包有时只能抓到部分，比如仅有AP侧的数据，设备端的数据包都丢失了，原因是 **未指定信道** 。此时需要使用`airodump-ng`工具查看目标AP的信道：

    
    
    root@kali:~# airodump-ng wlan0mon

![image-20200629141915808.png](https://image.3001.net/images/20200630/1593489362_5efab7d263524.png!small)

上图中第一行所示的信息中，CH表示信道，我们想对该AP进行四次握手的捕获，则需要将网卡监听的信道固定为11：

    
    
    root@kali:~# airmon-ng start wlan0mon 11  
    ​  
    ​  
    PHY Interface   Driver      Chipset  
    ​  
    phy0    wlan0mon    rt2800usb   Ralink Technology, Corp. RT2870/RT3070  
    ​  
            (mac80211 monitor mode already enabled for [phy0]wlan0mon on [phy0]11)

看到命令行中最后一行括号里的提示，表示已经设置为固定监听信道11。

此时打开wireshark，选中网卡wlan0mon即可捕获。

# WPA四次握手

在上一篇文章《[Wi-Fi攻击方式简述](https://www.freebuf.com/column/240988.html)》中，已经对WPA的握手过程进行过简单讲解，总结起来WPA的四次握手完成了：

1）Wi-Fi密码的验证

2）后续通信加密的密码的计算（注意这里是“计算”不是“传输”）

而在其握手过程中，会生成一些过程产物，如加密握手数据的密钥、完整性校验数据等。密钥计算的总览视图如下：

![image-20200629154441387.png](https://image.3001.net/images/20200630/1593489370_5efab7da9e063.png!small)

四次握手的简单示意图：

![686769-20161117152254170-216963418.png](https://image.3001.net/images/20200630/1593489383_5efab7e77bc42.png!small)

接下来会逐步介绍每一步的计算过程。

## 握手前的准备：计算PMK

 **PMK(Pairwise Master Key)** 是整个WPA认证过程中非常核心的一个密钥，是由Wi-Fi的`SSID`和`Pre-Shared-Key`（即Wi-Fi密码）计算而来，其算法被称为Password-Based Key Derivation Function 2 (PBKDF2)
，是一种使用HMAC-SHA1，使用SSID作为盐值来进行哈希的一种算法。

![image-20200629170801055.png](https://image.3001.net/images/20200630/1593489393_5efab7f13ca12.png!small)

在默认的Python环境中，需要安装`pbkdf2`库来支持这种算法，可以使用`pip install pbkdf2`命令来安装 。

    
    
    from pbkdf2 import PBKDF2  
    ​  
    psk = "Induction"  
    ssid = "Coherer"  
    pmk = PBKDF2(psk, ssid, 4096).read(32)

![image-20200629165810353.png](https://image.3001.net/images/20200630/1593489404_5efab7fcb956a.png!small)

此外，可以利用Linux系统中的`wpa_passphrase`工具来计算PMK，其命令为：

    
    
    pentest@DESKTOP-2AE07FJ:~$ wpa_passphrase Coherer Induction

![image-20200629165935651.png](https://image.3001.net/images/20200630/1593489409_5efab801dad5d.png!small)

这里可以看出来，计算出来的值是一致的。

## 第一次握手：传递ANonce，STA计算PTK

在WPA的第一次握手时，由AP向STA发送`ANonce`：

![image-20200629170336475.png](https://image.3001.net/images/20200630/1593489416_5efab808e6f88.png!small)

在这个数据包中，除了 `ANonce` 以外，在头部包含了双方的MAC地址。此时
**STA本地生成SNonce，满足了PTK计算的全部条件，因此进行PTK的计算** 。

![image-20200629171145032.png](https://image.3001.net/images/20200630/1593489431_5efab817699d4.png!small)

 **由于SNonce在第二次握手的数据包中，因此这部分计算的演示在下一节进行。**

## 第二次握手：传递SNonce，AP计算PTK

第二次握手时，STA向AP发送SNonce：

![image-20200629171638896.png](https://image.3001.net/images/20200630/1593489440_5efab8207cfa4.png!small)

PTK（Pairwise Transient Key）的计算需要使用 **PRF512** 算法，其实现是参照《[Understanding
WPA/WPA2 Hash (MIC) Cracking Process In
Python](https://www.shellvoide.com/wifi/understanding-wpa-wpa2-hash-mic-cracking-process-python/)》文章中给出的算法进行：

    
    
    def customPRF512(key, A, B):  
        blen = 64  
        i = 0  
        R = ''  
        while i <= ((blen * 8 + 159) / 160):  
            hmacsha1 = hmac.new(key, A + chr(0x00) + B + chr(i), hashlib.sha1)  
            i += 1  
            R = R + hmacsha1.digest()  
        return R[:blen]

从前两次握手包中提取的`ANonce`、`SNonce` 以及双方的MAC地址，拼接起来作为计算PTK的部分：

    
    
    mac_ap = binascii.unhexlify("000c4182b255")  
    mac_cl = binascii.unhexlify("000d9382363a")  
    anonce = binascii.unhexlify("3e8e967dacd960324cac5b6aa721235bf57b949771c867989f49d04ed47c6933")  
    snonce = binascii.unhexlify("cdf405ceb9d889ef3dec42609828fae546b7add7baecbb1a394eac5214b1d386")  
    key_data = min(mac_ap, mac_cl) + max(mac_ap, mac_cl) + min(anonce,snonce) + max(anonce,snonce)

`PRF512`需要3个参数，`PMK`，`PKE` 和上面计算出来的 `key_data`。其中`PKE`是一个固定字符串，`PMK`在前文中有过计算：

    
    
    pke = "Pairwise key expansion"  
    pmk = PBKDF2("Induction", "Coherer", 4096).read(32)  
    ptk = customPRF512(pmk, pke, key_data)  
    # 此处ptk的值(Hex String)为：b1cd792716762903f723424cd7d1651182a644133bfa4e0b75d96d230835843315798d511beae0028313c8ab32f12c7ecb71c893482669daaf0e9223fe1c0aed

到这里，AP和STA各自都计算出了PTK（正常情况下双方算出的PTK内容是一致的）。

## PTK的构成

上一步骤中，计算出来的PTK是一个512bit的字符串（64字节），这是由于我们下载的Wireshark官方提供的样例包中的WPA采用的是TKIP加密，如果是CCMP加密，这里的算法会有所区别，因为计算出的PTK应当为384bit。

此处以TKIP加密为例，512bit的字符串可以分割为3个部分：KCK、KEK 和 TK。

![image-20200629191743423.png](https://image.3001.net/images/20200630/1593495618_5efad0420873e.png!small)

 **KCK (Key Confirmation Key)：** 用于计算WPA EAPOL密钥消息的MIC（完整性验证）

 **KEK (Key Encryption Key)：** 用于加密发送到客户端的附加数据（在“密钥数据”字段中）

 **TK (Temporal Key)：** 用于后续通信数据加密

TKIP加密模式下，PTK共512bit，其中按顺序为：KCK（128bit），KEK（128bit），TK（256bit）

CCMP加密模式下，PTK共384bit，其中按顺序为：KCK（128bit），KEK（128bit），TK（128bit）

![image-20200630095341818.png](https://image.3001.net/images/20200630/1593495626_5efad04ac9bb1.png!small)

如上节中计算的PTK，按照长度划分，应为：

KCK = b1cd792716762903f723424cd7d16511

KEK = 82a644133bfa4e0b75d96d2308358433

TK = 15798d511beae0028313c8ab32f12c7ecb71c893482669daaf0e9223fe1c0aed

## 验证MIC

比较第一次和第二次握手，在数据包中会发现在`WPA Key MIC`字段中由原来的全0变成了一串字符：

![image-20200629202936492.png](https://image.3001.net/images/20200630/1593495637_5efad05557b46.png!small)

 **MIC (Message Integrity Code)：** 消息完整性代码
是校验数据是否被篡改，以及PSK是否正确（因为MIC是由PTK参与计算，PTK由是由PSK生成）。

![image-20200630100306995.png](https://image.3001.net/images/20200630/1593495651_5efad06363d4a.png!small)

MIC的计算是以KCK为密钥（Key），整个802.1X报文为消息体（Message）进行HMAC运算得出的结果，共128bit。

顺便一提，WPA的密码离线破解也是利用PSK生成PMK，并根据握手包计算KCK，再生成MIC并对比原数据包中的MIC来确定密码是否正确。

在我们手工验证的时候，需要先将整个报文（这里以第二次握手为例）提取出来，并找到`WPA Key MIC`字段，将这部分内容替换成0，再计算。

![image-20200630101214680.png](https://image.3001.net/images/20200630/1593495661_5efad06de4e72.png!small)

这部分代码如下：

    
    
    payload = binascii.unhexlify("0203007502010a00100000000000000000cdf405ceb9d889ef3dec42609828fae546b7add7baecbb1a394eac5214b1d386000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001630140100000fac020100000fac040100000fac020000")  
    mic = hmac.new(ptk[0:16], payload, hashlib.sha1).hexdigest()[:32]

至此，大部分的计算和校验任务已经结束。

## 第三次握手：传递加密的GTK，STA安装TK

第三次握手，由AP向STA发送数据，其中MIC部分与上面的计算方式一致。STA接收到数据后，验证MIC通过则说明AP是有效的，双方PMK是一致的。

同时，在这个数据包中，包含了加密后的GTK。 **GTK (Group Temporal Key)**
用于加密广播和多播数据。GTK加密的密钥为KEK，其解密和使用不在此详述。

当STA接收到第三次握手包并验证MIC通过后，会将计算出来的TK（PTK的最后一段）安装到系统中，作为后续的通信加密密钥。

## 第四次握手：AP安装TK

最后一次握手仅为STA向AP发送的确认信息，表示密钥已经安装完毕，此时AP端也会进行密钥安装，至此，双方的密钥安装全部结束，后续通信中按照前面步骤中的密钥进行通信。

# 密钥重装攻击 KRACK Attack

上文中简单梳理了一下WPA四次握手的过程，其中省略了一些部分。由于主要是想帮助对KRACK漏洞的理解，因此重点放在第三次握手的密钥安装部分，安装的密钥来源上。

## 原理

关于这一漏洞，感兴趣的可以参考《[WPA2 密钥重装攻击 KRACK Attacks
分析报告](https://www.freebuf.com/articles/wireless/150953.html)》，个人感觉这篇文章解释的比较详细，总结起来这个漏洞就是：

​

> 其中，wpa_supplicant
> 2.4及2.5版本实现了协议注释内容“一旦安装后，就可从内存中清除加密密钥”，将导致客户端会安装值全为零的秘钥。因此使用了这些wpa_supplicant版本的Linux及Android设备将遭受严重威胁。

​

这个漏洞是利用wpa_supplicant在第三次握手时对TK的处理来达到攻击的目的的。由于TK是根据第一次和第二次握手包中的数据生成，因此STA会将该密钥保存在本地的内存中。当收到第三次握手的数据包时，STA会将该密钥安装，并从内存中清除（“一旦安装后，就可从内存中清除加密密钥”），因此再次收到该握手包时，程序会再次加载这部分已被清零的内存，导致重新安装的密钥为全0。

## 利用

由于目前未找到直接的利用EXP/POC，在Github上有一个检测工具：<https://github.com/vanhoefm/krackattacks-scripts>，其官网 <https://www.krackattacks.com> 上有对这个漏洞的演示。

从原理和演示来看，KRACK漏洞需要搭建Rogue AP做中间人，转发握手数据帧。当发送第三次握手包时，进行重放。

由于多次接收到第三次握手包，STA会尝试安装全0的密钥，并使用密钥加密后续通信包。Rogue AP的通信密钥预先就被置为0，这样就可以正常的和STA通信。

目前没有时间来实践这个漏洞，仅从原理上对漏洞的利用方式进行分析，该漏洞更像是传统的Evil Twin的攻击方法，但Evil
Twin需要知道目标AP的密码，才能让用户的设备顺利连入；而借助KRACK Attack，攻击者无需知道目标AP的密码即可实现中间人攻击，监听受害者流量。

# 总结

WPA的四次握手中，前两次是在互相交换计算PTK的信息（ANonce、SNonce），AP验证STA身份（利用MIC）并各自计算出PTK；第三次握手STA验证了AP的身份，传输加密GTK，并将计算出的TK安装；第四次握手确认密钥安装完成。

附：完整的计算MIC的 Python 代码

    
    
    from pbkdf2 import PBKDF2  
    import hmac, binascii, hmac, hashlib, sha  
    ​  
    def customPRF512(key, A, B):  
        blen = 64  
        i = 0  
        R = ''  
        while i <= ((blen * 8 + 159) / 160):  
            hmacsha1 = hmac.new(key, A + chr(0x00) + B + chr(i), sha)  
            i += 1  
            R = R + hmacsha1.digest()  
        return R[:blen]  
    ​  
    psk = "Induction"  
    ssid = "Coherer"  
    pmk = PBKDF2(psk, ssid, 4096).read(32)  
    ​  
    mac_ap = binascii.unhexlify("000c4182b255")  
    mac_cl = binascii.unhexlify("000d9382363a")  
    anonce = binascii.unhexlify("3e8e967dacd960324cac5b6aa721235bf57b949771c867989f49d04ed47c6933")  
    snonce = binascii.unhexlify("cdf405ceb9d889ef3dec42609828fae546b7add7baecbb1a394eac5214b1d386")  
    ​  
    key_data = min(mac_ap, mac_cl) + max(mac_ap, mac_cl) + min(anonce,snonce) + max(anonce,snonce)  
    pke = "Pairwise key expansion"  
    ptk = customPRF512(pmk, pke, key_data)  
    ​  
    print "PTK Original:                ",ptk.encode('hex')  
    print "EAPOL-Key Confirm Key:       ",ptk[:16].encode('hex')  
    print "EAPOL-Key Encrypt Key:       ",ptk[16:32].encode('hex')  
    print "(TKIP|CCMP) Temporal Key:    ",ptk[32:].encode('hex')  
    ​  
    payload = binascii.unhexlify("0203007502010a00100000000000000000cdf405ceb9d889ef3dec42609828fae546b7add7baecbb1a394eac5214b1d386000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001630140100000fac020100000fac040100000fac020000")  
    ​  
    mic = hmac.new(ptk[0:16], payload, hashlib.sha1).hexdigest()[:32]  
    print "MIC (Message Integrity Code):",mic

 **参考链接**

[1] [WPA/RSN四次握手和PTK](WPA/RSN%E5%9B%9B%E6%AC%A1%E6%8F%A1%E6%89%8B%E5%92%8CPTK)

[2] [KEYS, KEYS, AND EVEN MORE
KEYS!](https://dalewifisec.wordpress.com/2013/06/03/keys-keys-and-even-more-keys/)

[3] [WPA/WPA2-PSK认证过程](WPA/WPA2-PSK%E8%AE%A4%E8%AF%81%E8%BF%87%E7%A8%8B)

[4] [四次握手](https://www.jianshu.com/p/392362718d68)

[5] [安全协议系列（二）----CCM与CCMP](https://www.cnblogs.com/efzju/p/3199330.html)

[6] <https://www.krackattacks.com/>

[7] <https://github.com/vanhoefm/krackattacks-scripts>

[8] [国内研究人员首次Wifi重大漏洞利用实现 |
Krack攻击测试套件打包](https://www.freebuf.com/articles/wireless/153255.html)

[9] [WPA2 密钥重装攻击 KRACK Attacks
分析报告](https://www.freebuf.com/articles/wireless/150953.html)

[10] [Understanding WPA/WPA2 Hash (MIC) Cracking Process In
Python](https://www.shellvoide.com/wifi/understanding-wpa-wpa2-hash-mic-cracking-process-python/)

[11] [HowToDecrypt802.11](https://wiki.wireshark.org/HowToDecrypt802.11)

