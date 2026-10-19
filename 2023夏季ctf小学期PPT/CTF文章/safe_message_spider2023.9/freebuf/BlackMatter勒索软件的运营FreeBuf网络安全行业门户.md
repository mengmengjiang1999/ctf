BlackMatter 于 2021 年 7 月被首次发现，是勒索软件即服务（RaaS）领域的新玩家。业界认为其为最近退休的俄罗斯勒索软件团伙
DarkSide 的接班人，但 BlackMatter 的发言人坚称他们不是同一伙人。

BlackMatter 最近成为瞩目的焦点是因为攻击了一家大型医疗技术公司和美国农业合作社。

## 影响的操作系统

![](https://image.3001.net/images/20210925/1632549091_614eb8e3567d4f3d5b158.png!small)

## BlackMatter

BlackMatter 已在俄罗斯黑客论坛上发布了招募合作伙伴的公告，它声称汲取了 DarkSide、REvil 和 LockBit 的百家之长。

尽管黑客论坛在 2021 年 5 月 Colonial Pipeline 攻击事件后禁止发布勒索软件广告，但 BlackMatter
通过招募“初始访问中间商”来规避这一限制。这些中间商拥有访问公司网络的立足点，与 BlackMatter 进行合作。

BlackMatter 在公告中表示，他们的攻击目标是英语国家、拥有 500 到 1500 台主机、超过 1 亿美元收入的公司。

BlackMatter 旨在填补 DarkSide 和 REvil
暂停攻击行动而留下的市场空白。![](https://image.3001.net/images/20210925/1632549094_614eb8e6edd5ab27fec5a.png!small)

BlackMatter 有一个不攻击的范围，如果受害提供免费解密，包括医院和关键基础设施等。可能是为了规避 REvil、Conti 和 DarkSide
在此前攻击这些行业引起的巨大反弹。

与 DarkSide 和 REvil 不同，BlackMatter 不根据地理位置来区分受害者，俄语主机也会被加密。

## 技术分析

7 月以来，BlackMatter 已经更新了多个版本，包括 1.2、1.6、1.9 和 2.0，甚至包括 Linux 变种。

最近分析的文件是 2021 年 8 月 16 日编译的 Windows 可执行文件。该样本包含
`.rsrc`段，但不包含任何资源。该段用于存储编码配置信息，该样本是 BlackMatter 的 2.0 版本。

该二进制文件仅引用三个库文件：![](https://image.3001.net/images/20210925/1632549096_614eb8e8742ac8363fcec.png!small)

BlackMatter 将大多数 API 和重要字符串都混淆了，且 BlackMatter 实现的方式与 DarkSide 十分类似。

解析所需 API
地址如下所示：![](https://image.3001.net/images/20210925/1632549098_614eb8ea5a1f2a775def7.png!small)

DWORD 值指向每个 API 的加密哈希，后跟
`0xCCCCCCCC`，每个哈希都通过异或进行解密。![](https://image.3001.net/images/20210925/1632549100_614eb8ec64bd83e433602.png!small)

在执行函数
`sub_407DB0`之前加载的库如下所示：![](https://image.3001.net/images/20210925/1632549102_614eb8ee978ed63bb2920.png!small)

解析 API
完成后：![](https://image.3001.net/images/20210925/1632549104_614eb8f0a9f1345f49d5f.png!small)

BlackMatter 还会使用反调试技术隐藏调试器中的线程，调试分析会导致程序崩溃。

样本会创建一个互斥锁，确保不重复感染。根据与 `MachineGuid`相关的注册表生成的，例如
`Global\21661c2e54b253e217f64acc8644f973`。

恶意样本删除三个与卷影副本相关的服务：

> vmicvss
>
> vmvss
>
> vss

BlackMatter
会终止与生产力相关的常见进程，确保重要文件不会被锁定，扩大影响范围。勒索软件采用多线程方法枚举文件系统并执行加密，确保文件可以被快速锁定。

BlackMatter 的加密程序与 DarkSide 的加密程序也有相似之处，使用 Salsa20 和 RSA-1024 算法。BlackMatter
只对每个文件的前部一些字节进行加密，并将加密的密钥添加到文件末尾。部分加密使加密过程飞快，缩短攻击时间，让受害者没有反应时间。

加密文件扩展名由字母和数字的字符串组成，不同的攻击中不相同。![](https://image.3001.net/images/20210925/1632549107_614eb8f3d1e077c47896c.png!small)

通过注册表修改用户桌面：![](https://image.3001.net/images/20210925/1632549110_614eb8f613ba2f850c032.png!small)

桌面显示用户已经被 BlackMatter 加密，使用的图片与 DarkSide
也非常相似。![](https://image.3001.net/images/20210925/1632549111_614eb8f7addbfd749e0ae.png!small)

勒索信息放入每个目录下，使用与加密文件相同的扩展名再加上
`README.txt`。![](https://image.3001.net/images/20210925/1632549113_614eb8f9846a2898c015e.png!small)

提供的暗网地址支持受害者付款：![](https://image.3001.net/images/20210925/1632549115_614eb8fb7d285ff3dc631.png!small)

收集失陷主机的信息会通过 POST 请求发送到 C&C
服务器上。![](https://image.3001.net/images/20210925/1632549118_614eb8fe26f50a031335f.png!small)

BlackMatter
也使用双重勒索，如果受害者不支付赎金就会公开其数据。![](https://image.3001.net/images/20210925/1632549119_614eb8ffbcf79db611c67.png!small)

## Yara

> import "pe"  
> import "hash"
>
> rule Mal_Win_Ransom_BlackMatter {
>
> meta:  
> description = "BlackMatter Ransomware September 2021"  
> author = "BlackBerry Threat Research Team"  
> date = "2021-09"
>
> condition:  
> pe.is_32bit() and  
> filesize < 90KB and  
> filesize > 60KB and  
> pe.number_of_imports == 3 and  
> pe.imphash() == "2e4ae81fc349a1616df79a6f5499743f" and  
> hash.md5(pe.sections[0].raw_data_offset, pe.sections[0].raw_data_size) ==
> "100da8cf342d6d8f3bd24b367e0ea999" and  
> pe.sections[3].name == ".rsrc" and  
> pe.number_of_signatures == 0 and  
> pe.number_of_sections == 5  
> }

## IOC

> https://mojobiden.com  
> https://nowautomation.com  
>
> http://supp24yy6a66hwszu2piygicgwzdtbwftb76htfj7vnip3getgqnzxid.onion/O3KTUJZRE6CB4Q1OBR

## 参考来源

> [BlackBerry](https://blogs.blackberry.com/en/2021/09/threat-thursday-> blackmatter-ransomware-as-a-service)

