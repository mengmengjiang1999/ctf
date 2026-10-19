## 前言

 **近期，McAfee
Lab的研究人员发现了一款新型的俄罗斯恶意软件，这款恶意软件名叫“WebCobra”，它可以利用目标设备的计算能力来挖加密货币。**

实际上，恶意挖矿软件是很难被检测到的。当设备被感染后，恶意软件会在系统后台悄悄运行，唯一可能暴露痕迹的就是设备性能的下降。由于恶意软件会增加设备计算能力的消耗，设备的运行速度会显著降低，随之而来的除了用户使用过程中的反感，还有电费账单上的“天文数字”，毕竟挖一个比特币需要消耗的成本大约在531美元到26170美元之间…

毫无疑问，加密货币价值的增长正在吸引越来越多的网络犯罪分子投身于恶意挖矿的行列中。

下图显示的是门罗币价格走势与恶意挖矿软件发展趋势之间的关系对应图：

![关系对应图](https://image.3001.net/images/20181122/1542884290_5bf68bc2c8247.png!small)  

在此之前，McAfee
Lab曾对加密货币文件注入工具CoinMiner进行了分析，感兴趣的同学可以浏览【[分析报告](https://www.cyberthreatalliance.org/wp-content/uploads/2018/09/CTA-Illicit-CryptoMining-Whitepaper.pdf)】。

WebCobra这款恶意软件在感染了目标设备之后，会在后台悄悄植入Cryptonight Miner或Claymore的Zcash
Miner，具体需要根据WebCobra扫描到的目标设备架构来确定。我们认为，这款恶意软件主要通过PUP流氓安装器来实现传播，目前全球范围都受到了影响，受感染用户最多的地区分别是巴西、南非和美国。

  
![受感染用户](https://image.3001.net/images/20181122/1542884295_5bf68bc7d62cc.png!small)

与其他恶意挖矿软件不同的是，WebCobra会根据受感染设备的配置和架构来选择植入不同的挖矿工具。

## 恶意行为分析

恶意软件的Dropper是一个Windows安装程序，它会检测系统运行环境。在x86系统上，它会向正在运行的进程中注入Cryptonight
Miner代码，然后启用进程监控。在x64系统上，它会检测GPU配置，然后从远程服务器下载并执行Claymore的Zcash Minner。

![恶意行为分析](https://image.3001.net/images/20181122/1542884306_5bf68bd244424.png!small)

启动之后，恶意软件会使用下列命令下载并解压一个受密码保护的Cabinet压缩文件：

![受密码保护的Cabinet压缩文件](https://image.3001.net/images/20181122/1542884312_5bf68bd8af0d3.png!small)

这个CAB文件包含以下两个文件：

> 1、 LOC：用于解密data.bin的DLL文件；
>
> 2、 bin：包含了经过加密处理的恶意Payload；

CAB文件使用了下列脚本来执行ERDNT.LOC：

![执行ERDNT.LOC](https://image.3001.net/images/20181122/1542884319_5bf68bdf9bf1c.png!small)

ERDNT.LOC会解密data.bin，然后利用下列路径将执行流传递给它：

    
    
    [PlainText_Byte]= (([EncryptedData_Byte] + 0x2E) ^ 0x2E) + 0x2E

![恶意行为分析](https://image.3001.net/images/20181122/1542884326_5bf68be6689b1.png!small)

程序会在检测了当前运行环境之后启动对应的Miner，整个过程如下图所示：

  
![恶意行为分析](https://image.3001.net/images/20181122/1542884344_5bf68bf83eb42.png!small)  

当data.bin被解密并执行之后，它会尝试执行一些反调试、反模拟和反沙箱技术，并检测当前系统上运行的其他安全产品，而这些都是这款恶意软件保护自己不被检测到的一些基本手段。

大多数安全产品都会通过挂钩API函数来监控恶意软件的行为，为了避免被检测到，WebCobra会在内存中以数据文件的形式加载ntdll.dll和user32.dll，然后重写这些函数的前八个字节（解除API
hook）。

### 未设置hook的ntdll.dll API

    
    
    LdrLoadDll
    
    ZwWriteVirtualMemory
    
    ZwResumeThread
    
    ZwQueryInformationProcess
    
    ZwOpenSemaphore
    
    ZwOpenMutant
    
    ZwOpenEvent
    
    ZwMapViewOfSection
    
    ZwCreateUserProcess
    
    ZwCreateSemaphore
    
    ZwCreateMutant
    
    ZwCreateEvent
    
    RtlQueryEnvironmentVariable
    
    RtlDecompressBuffer

### 未设置hook的user32.dll API

    
    
    SetWindowsHookExW
    
    SetWindowsHookExA

## 感染x86系统

恶意软件会向svchost.exe注入恶意代码，并利用无限循环来检测所有打开的窗口，然后使用下面列表中的字符串来匹配窗口的标题栏。这也是WebCobra采用的另一种检测机制，它会根据这个检测结果来判断当前环境是否是专门用来分析恶意软件的隔离环境。

    
    
    adw
    
    emsi
    
    avz
    
    farbar
    
    glax
    
    delfix
    
    rogue
    
    exe
    
    asw_av_popup_wndclass
    
    snxhk_border_mywnd
    
    AvastCefWindow
    
    AlertWindow
    
    UnHackMe
    
    eset
    
    hacker
    
    AnVir
    
    Rogue
    
    uVS
    
    malware

恶意软件会根据打开窗口的标题栏来判断运行环境：

![判断运行环境](https://image.3001.net/images/20181122/1542884401_5bf68c31ba76d.png!small)

进程监控执行之后，它会使用Miner的配置文件创建一个svchost.exe的实例，并注入Cryptonignt Miner代码：

![注入Cryptonignt
Miner代码](https://image.3001.net/images/20181122/1542884410_5bf68c3ab6548.png!small)

最后，恶意软件会让Cryptonight Miner在后台静默运行，并利用目标主机的全部CPU资源来挖矿：

![利用目标主机的全部CPU资源来挖矿](https://image.3001.net/images/20181122/1542884421_5bf68c45247a9.png!small)

## 感染x64系统

恶意软件首先会检测是否运行了Wireshark：

![感染x64系统](https://image.3001.net/images/20181122/1542884438_5bf68c56b732b.png!small)

然后检测GPU品牌和型号，只有在检测到下列GPU的时候它才会运行：

    
    
    Radeon
    
    Nvidia
    
    Asus

![检测GPU品牌和型号](https://image.3001.net/images/20181122/1542884457_5bf68c69877d1.png!small)

如果检测成功，恶意软件会创建下面隐藏文件夹，然后从远程服务器下载并执行Zcash Miner：

    
    
    C:\Users\AppData\Local\WIXToolset 11.2

![执行Zcash
Miner](https://image.3001.net/images/20181122/1542884478_5bf68c7e19143.png!small)![执行Zcash
Miner](https://image.3001.net/images/20181122/1542884478_5bf68c7e38fcf.png!small)![执行Zcash
Miner](https://image.3001.net/images/20181122/1542884478_5bf68c7e3f916.png!small)

最后，恶意软件会在%temp%\–xxxxx.cMD中植入一个batch文件来删除Dropper（[WindowsFolder]\\{DE03ECBA-2A77-438C-8243-0AF592BDBB20}\\*.*）：

![植入一个batch文件来删除Dropper](https://image.3001.net/images/20181122/1542884491_5bf68c8b51b13.png!small)

Miner的配置文件如下：

![Miner的配置文件](https://image.3001.net/images/20181122/1542884500_5bf68c94db79a.png!small)

配置文件中包含：

    
    
    矿池地址：5.149.254.170
    
    用户名：49YfyE1xWHG1vywX2xTV8XZzbzB1E2QHEF9GtzPhSPRdK5TEkxXGRxVdAq8LwbA2Pz7jNQ9gYBxeFPHcqiiqaGJM2QyW64C
    
    密码：soft-net

![配置文件](https://image.3001.net/images/20181122/1542884518_5bf68ca6063a4.png!small)

这份配置文件包含：

    
    
    矿池地址：eu.zec.slushpool.com
    
    用户名：pavelcom.nln
    
    密码：zzz

## 总结

毫无疑问，恶意挖矿软件还会不断进化，因为网络犯罪分子肯定不会放过这种相对来说比较轻松的赚钱方式。而且跟勒索软件相比，恶意挖矿软件的风险会更低，并且不需要目标用户直接性地“支付费用”。只要隐蔽性够高，只要不被发现，网络犯罪分子就可以躺着把钱赚了。

## 入侵威胁指标

### IP地址

    
    
    5.149.249[.]13:2224
    
    5.149.254[.]170:2223
    
    104.31.92[.]212

### 域名

    
    
    emergency.fee.xmrig[.]com
    
    miner.fee.xmrig[.]com
    
     saarnio[.]ru
    
    eu.zec.slushpool[.]com

### 哈希（SHA-256）

    
    
    5E14478931E31CF804E08A09E8DFFD091DB9ABD684926792DBEBEA9B827C9F37
    
    2ED8448A833D5BBE72E667A4CB311A88F94143AA77C55FBDBD36EE235E2D9423
    
    F4ED5C03766905F8206AA3130C0CDEDEC24B36AF47C2CE212036D6F904569350
    
    1BDFF1F068EB619803ECD65C4ACB2C742718B0EE2F462DF795208EA913F3353B
    
    D4003E6978BCFEF44FDA3CB13D618EC89BF93DEBB75C0440C3AC4C1ED2472742
    
    06AD9DDC92869E989C1DF8E991B1BD18FB47BCEB8ECC9806756493BA3A1A17D6
    
    615BFE5A8AE7E0862A03D183E661C40A1D3D447EDDABF164FC5E6D4D183796E0
    
    F31285AE705FF60007BF48AEFBC7AC75A3EA507C2E76B01BA5F478076FA5D1B3
    
    AA0DBF77D5AA985EEA52DDDA522544CA0169DCA4AB8FB5141ED2BDD2A5EC16CE

 ***参考来源：[securingtomorrow](https://securingtomorrow.mcafee.com/other-blogs/mcafee-labs/webcobra-malware-uses-victims-computers-to-mine-cryptocurrency/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

