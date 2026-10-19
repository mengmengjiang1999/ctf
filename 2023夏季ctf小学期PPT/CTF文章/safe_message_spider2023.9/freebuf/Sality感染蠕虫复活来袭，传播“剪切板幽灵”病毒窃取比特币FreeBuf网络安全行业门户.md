## 一、事件背景

**近期，金山毒霸安全实验室“捕风”系统捕获到一批异常活跃的样本，该样本会监控剪切板，将比特币和以太坊的钱包地址，替换成自己的钱包地址。这样，用户复制粘贴钱包地址进行转账时，虚拟货币最终会转帐到攻击者的钱包中。通过对该病毒进行溯源分析，最终发现是由Sality感染型病毒进行传播感染。此类“剪切板幽灵”病毒在2018年初就曾被监控到大量传播行为，时隔一年再次卷土重来。**

Sality病毒家族最早于2003年被发现，该病毒融入多态加密引擎，运行后会尝试感染用户系统中大部分可执行程序，并通过感染U盘、网络共享进一步扩展传播，受感染系统将被进一步用于传播垃圾邮件、代理跳板、隐私窃取、分布式攻击等。随着十几年的发展，该病毒家族不断加入Rootkit对抗、P2P网络控制等新特性，成为当下最流行、最复杂、最顽固的感染型蠕虫之一，预计全球范围内累计感染用户超过千万级别。

## 二、流程分析

##
![](https://image.3001.net/images/20190319/1552982685_5c90a29d910da.png!small)

对于Sality病毒的感染过程本文不再赘述，以下主要分析感染以后，病毒通过P2P网络获取恶意插件URL数据，下载安装比特币剪切板劫持木马。以下为抓包发现的剪切板劫持木马下载行为：

![](https://image.3001.net/images/20190319/1552982701_5c90a2ad7ca34.png!small)

![](https://image.3001.net/images/20190319/1552982701_5c90a2adb81cb.png!small)

通过分析被Sality病毒感染进程中注入的恶意模块dump , 也可以发现挂马地址和抓包地址一致。

![](https://image.3001.net/images/20190319/1552982716_5c90a2bc7aa4a.png!small)

以上数据解密落地后的PE文件（MD5:68b6a3a936b256510a1af099082355a5），就是钱包地址劫持木马，采用UPX压缩，病毒行为非常简单，执行以后循环读取系统剪贴板的内存数据，进行比特币地址格式校验，替换为自身硬编的比特币地址，用户转账过程中一旦疏于检查就会被盗取比特币和以太坊等虚拟货币：

![](https://image.3001.net/images/20190319/1552982724_5c90a2c4f2278.png!small)

捕获的在野样本中，我们发现攻击者有多个BTC钱包地址和ETH钱包地址，部分钱包地址收益情况如下：

**钱包地址** | **共收入** | **折合人民币**  
---|---|---  
15Wm3Xy2wLWboyCgH4G9cNhgr5xD7z11QA | 0.00206297 BTC | 53.86  
13wG8KRQx1tpCkCBWRyYrdqfuaCUcagvmq | 0.16267025 BTC | 4248.13  
19QmbQGK8srwjJ8bLm2iZj9qfMP5EZqHcx | 0.29304165 BTC | 7652.78  
0x3D15c7341BBD7cCc193769de903ea711a2e4b43e | 0.00090811 ETH | 0.82  
  
## 三、IOC

**挂马域名** | **状态**  
---|---  
elcisigur.ro | 404  
funwebstrankaaqworlds.wz.cz | 404  
gdergi.com | 404  
bamas.planet-it.co.id | 404  
batata.webzdarma.cz | 404  
ilmesters.edu.pk | 404  
acbilgisayar.com.tr | alive  
sgw.co.th | alive  
[www.figg.co.za](http://www.figg.co.za) | alive  
server2.hainhan.com | alive  
moulitech.com | alive  
  
### MD5:

    
    
    55bfee3915ae84f38fda750587868ae7
    
    68b6a3a936b256510a1af099082355a5
    
    47b6cf018dabd9002b1024422061c137

 ***本文作者：安全豹，转载请注明来自FreeBuf.COM**

