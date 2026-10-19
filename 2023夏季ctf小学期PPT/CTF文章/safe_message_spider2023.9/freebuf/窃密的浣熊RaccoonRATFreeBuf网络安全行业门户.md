Raccoon 是一个信息窃密恶意软件，通过恶意软件即服务（MaaS）提供给订阅者，所窃取的信息可能会通过暗网论坛找到潜在的买家。

## 操作系统

![](https://image.3001.net/images/20210922/1632315769_614b29798b72273d40920.png!small)

## 背景

Raccoon 一直被认为是 Azorult 的替代品，在 2019 年年初开始对外披露，2019 年 4 月被首次在野发现。

Raccoon
一直都在宣传他们拥有负责开发的专家团队，而且十分注重解决用户使用中存在的问题。这种水平的客户服务使攻击者在犯罪社区中积累了良好的信誉，成为了社区里可靠的服务提供商。

Raccoon 每月订阅费用不到 100 美元，长期订阅还可以享受更多折扣。每个订阅者都要求保护 Raccoon 的新版本，防止被端点防护软件检测到。

Raccoon 通常以“游击战”方式部署，窃取了凭据、Cookie 和加密钱包等信息后，所有的主要恶意软件都会从失陷主机上删除。

## 样本保护

以 Raccoon 投递的 32 位 Windows
程序（d7b4e7a29b5a4c2779df187c35b8137f5f27a9f0a06527d0966b8537c0a2c5ec）为例，订阅者也可以订阅
DLL 版本的恶意程序。

样本在 VirusTotal 上的首次提交时间是 2021 年 8 月上旬，而样本的创建时间戳为 2020 年 9 月、调试时间戳为 2021 年 6
月。而通过 Raccoon 的运行时日志可以确认构建在 2021 年 2
月下旬完成。![](https://image.3001.net/images/20210922/1632315772_614b297ce33b5d8b586b1.png!small)

恶意样本包含大量带有丢弃返回值的循环函数调用，被调用达到数万次，这会使得沙盒的报告非常嘈杂，分析也更为复杂。![](https://image.3001.net/images/20210922/1632315774_614b297e95c5c35722546.png!small)

Raccoon 的实际入口点与对 OLE32.DLL 的 `CoInitialize`函数调用一致。

为了阻止多重感染，Raccoon 利用用户名和硬编码字符串前缀
`uiabfqwfu`生成互斥量。![](https://image.3001.net/images/20210922/1632315777_614b29814365fa891f2fe.png!small)

检查失陷主机的国家设置，与独联体国家列表进行比较，如果命中则停止执行。

## 攻击基础设施

C&C 信息硬编码在样本中，经过 RC4 加密和 base64 编码，且 RC4 密钥也存储在可执行文件中。

C&C 使用的是似乎 2018 年注册的虚假 Telegram 域名，该域名在 2021 年 6 月开始解析，登录页面仿冒合法的 Telegram
服务。![](https://image.3001.net/images/20210922/1632315778_614b29822cdafeaeb80c5.png!small)

Raccoon 会提取页面上的 base64 编码的字符串，解密后发现二阶段的 C&C 服务器。

C&C 的 URL 和 config_id 都存储在 Raccoon 中 260 字节的占位符中，用于解密二阶段 C&C URL 的明文 RC4 密钥存储在
100 字节的占位符中。

    
    
    b=D6744488-8D2E-4BD1-7812-C37123498E72_Zaphod&c=76965ce08094e45ba176fa000c8299935ebdd965&f=json

Raccoon 获取 Windows GUID 和用户名，与配置 ID 一起发送给 C&C 服务器。在发送前，需要经过 RC4 加密和 base64
编码。![image.png-15.3kB](https://image.3001.net/images/20210922/1632315780_614b29842ca64183d58f8.png!small)

C&C 服务器的响应也经过 RC4 加密和 base64 编码。在响应 JSON 中，有包含 DLL 文件的 ZIP 文件的下载地址，再由 Raccoon
加载。![](https://image.3001.net/images/20210922/1632315781_614b29857cd4a1d733b33.png!small)

下载的 DLL
文件对应的合法应用程序列表如下所示：![image.png-89.2kB](https://image.3001.net/images/20210922/1632315782_614b29867fb79cd9643a5.png!small)

配置文件中还包括启动屏幕截图和自我销毁、文件合并的配置信息。![](https://image.3001.net/images/20210922/1632315784_614b29880a83bf50ad2cc.png!small)

Raccoon 针对常见的 Windows 应用程序发起攻击，主要是 Web
浏览器和电子邮件客户端。![](https://image.3001.net/images/20210922/1632315785_614b2989de3486ec90500.png!small)

大多数是注册表路径的片段，用于确认是否安装应用程序，或者是收集存在特定注册表路径的凭据。![](https://image.3001.net/images/20210922/1632315787_614b298bd19648ef34dc5.png!small)

除此之外，Raccoon
还会探测流行的加密货币钱包，将完整文件复制上传。![](https://image.3001.net/images/20210922/1632315789_614b298db7b916c1a79f1.png!small)

## 游击战

窃取的所有信息都被复制到一个随机命名的临时文件夹中。压缩文件夹为 ZIP 文件并上传到 C&C 服务器后，Raccoon
会被要求自我销毁。![](https://image.3001.net/images/20210922/1632315791_614b298f7333789bceb2b.png!small)

但是，Raccoon
的自我销毁并不完整，下载的库文件会被残留下来。![](https://image.3001.net/images/20210922/1632315792_614b29909174e83e72ecf.png!small)

## 结论

尽管 Raccoon
并不复杂，但是却为初出茅庐的网络犯罪分子和经验丰富的攻击者都提供了“平价”的攻击工具。它机会扫平了所有进入的技术门槛，让订阅者可以专注于窃取信息进行销售。

## Yara

> rule RaccoonInfoStealer
>
> {  
> strings:  
> $b64_conf_id = /[A-Za-z0-9+\/=\ ]+/  
> $hx_str_xor = { F6 D1 30 8C 15 ?? FD FF FF 42 83 FA ?? 73 08 8A 8D ?? FD FF
> FF EB }
>
> condition:  
> !b64_conf_id[1] == 260 or  
> all of ($hx*)  
> }

## IOC

> telete.in  
> tttttt.me  
> 5.181.156.252  
> 66.115.165.153  
> 34.135.32.61  
> 95.216.186.40

## 参考来源

> [BlackBerry](https://blogs.blackberry.com/en/2021/09/threat-thursday-> raccoon-infostealer)

