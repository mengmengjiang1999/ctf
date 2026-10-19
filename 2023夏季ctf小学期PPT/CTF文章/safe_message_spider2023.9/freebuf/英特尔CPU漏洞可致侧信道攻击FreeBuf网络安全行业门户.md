![image.png](https://image.3001.net/images/20200615/1592185430_5ee6d256d5be3.png!small)

**安全研究人员发现了两种攻击英特尔处理器的方式，可从CPU受信任执行环境（TEE）中获取敏感信息。**

第一种方式是今年初发现的CacheOut攻击（CVE-2020-0549）的变体，攻击者可以从CPU的L1缓存中检索内容。

第二种攻击方式是CrossTalk，攻击者通过在一个CPU内核上执行代码，从而针对运行在不同内核的SGX安全区，获取安全区的私钥。  

TEE与英特尔的Software Guard
Extensions（SGX）一样，指的是安全区域，它是处理器内确保代码和数据机密性和完整性的区域，防止攻击者入侵目标计算机，对敏感软件和数据进行修改。  

## SGAxe攻击：从SGX Enclaves中提取敏感数据

SGAxe攻击是基于CacheOut攻击来窃取SGX数据，尽管英特尔使用若干微代码和新架构来应对针对SGX的侧信道攻击，但这些措施都没有效果。该攻击可以从更新的英特尔计算机上恢复SGX加密密钥。认证是SGX的一种机制，可以向第三方证明它们已经在真实的Intel处理器上正确的进行初始化，其目的是确保CPU内部运行的软件未被篡改，增强软件在安全区域内部运行的可靠性。

攻击者可使用CacheOut从英特尔生产quoting enclave地址空间中恢复sealing密钥，解密quoting
enclave存储，获得机器的EPID认证密钥。  

![image.png](https://image.3001.net/images/20200615/1592186281_5ee6d5a95fdd7.png!small)

由于机器的生产认证密钥遭到破坏，服务器提供的任何数据都可以由客户不受信任的应用程序读取，客户运行的enclave产生的所有数据均无法得到信任，基于SGX的DRM应用程序全部失效，任何预置的数据都可以被恢复。  

英特尔在一月份向OEM供应商进行更新并向最终用户进行BIOS更新，发布CacheOut修复程序，芯片制造商还将执行Trusted Compute
Base（TCB）恢复，使所有先前签名的证明密钥无效。  

## CrossTalk攻击：跨CPU内核信息泄漏  

第二项攻击是CrossTalk（CVE-2020-0543），MDS（微体系结构数据采样）攻击，利用在所有CPU内核上均可读取的“staging”缓冲区，在内核之间进行瞬时执行攻击，提取在单独CPU内核上运行的安全区域的完整ECDSA私钥。

staging缓冲区保留了先前在所有CPU内核上执行的offcore-instructions指令结果，例如硬件DRNG返回的随机数，bootguard状态哈希和其他敏感数据。  

![image.png](https://image.3001.net/images/20200615/1592187022_5ee6d88e9b53b.png!small)

CrossTalk的工作方式是瞬时攻击期间读取staging缓冲区，泄漏先前执行指令访问的敏感数据，攻击还原视频[地址](https://www.*******.com/watch?v=7tba2ayE3cI&feature=emb_logo)。

随着2015年至2019年发布的英特尔CPU数量不断增加，受影响的Xeon E3和E
CPU数量不断增加。研究人员称：“现有针对瞬时执行攻击的缓解措施在基本上是无效的。”
“目前大多数缓解措施都依赖于边界空间隔离，这些边界由于跨核攻击不再适用，新微代码更新可以缓解这些攻击。”

 ***参考来源：[thehackernews](https://thehackernews.com/2020/06/intel-sgaxe-crosstalk-attacks.html)，由Kriston编译，转载请注明来自FreeBuf.COM**  

