## 前言

**今天，给大家介绍的是一款名叫WepAttack的开源工具。这是一款基于Linux平台的开源WEP密钥破解工具，它主要针对的是WLAN无线安全领域，可利用基于字典攻击的方式破解802.11
WEP密钥。**

![1.png](https://image.3001.net/images/20181211/1544525828_5c0f9804e49fe.png!small)

这款工具基于主动字典攻击，这种攻击方式可以测试数百万条关键词并最终寻找到正确的密钥。在执行这种攻击时，只需要一个数据包即可。

## WEP密钥是什么？

WEP是Wired
EquivalentPrivacy的简称，有线等效保密（WEP）协议是对在两台设备间无线传输的数据进行加密的方式，用以防止非法用户窃听或侵入无线网络。不过密码分析学家已经找出
WEP 好几个弱点，因此在2003年被Wi-Fi Protected Access (WPA) 淘汰，又在2004年由完整的 IEEE 802.11i
标准（又称为 WPA2）所取代。WEP 虽然有些弱点，但也足以吓阻非专业人士的攻击渗透了。

## 如何使用WepAttack WEP密钥破解工具

WepAttack在执行攻击之前，需要一份dumpfile。如果目标网络数据是采用[Kismet](https://www.darknet.org.uk/2008/02/kismet-wireless-network-hacking-sniffing-monitoring/)捕捉到的话，会自动生成一个dumpfile。这种文件的基础格式为“Kismet-[date]-[no].dump”，WepAttack可以直接对此类文件进行解析。

### 工具使用：

    
    
    wepattack-f dumpfile [-m mode] [-w wordlist] [-n network]
    
    -fdumpfile        network dumpfile to readfrom
    
    -mmode                run WepAttack indifferent modes. If this option is empty, all modes are executed sequentially(default)
    
     
    
                   64              WEP 64, ASCII mapping
    
     
    
                   128            WEP128, ASCII mapping
    
     
    
                   n64            WEP64, KEYGEN function
    
     
    
                   n128          WEP128, KEYGEN function
    
     
    
    -wwordlist        wordlist to use, withoutany wordlist stdin is used
    
    -nnetwork          network number, can bepassed to attack only one network. Default is attacking all available networks(recommended)

### 使用样例

    
    
    wepattack –f Kismet-Oct-21-2002-3.dump –w wordlist.txt

## WepAttack工具资源：

>
> WepAttack：【[下载地址](https://sourceforge.net/projects/wepattack/files/latest/download)】
>
> 官方网站：【[传送门](http://wepattack.sourceforge.net/)】

 ***参考来源：[darknet](https://www.darknet.org.uk/2018/11/wepattack-wlan-802-11-wep-key-hacking-tool/?utm_source=feedly&utm_medium=webfeeds)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

