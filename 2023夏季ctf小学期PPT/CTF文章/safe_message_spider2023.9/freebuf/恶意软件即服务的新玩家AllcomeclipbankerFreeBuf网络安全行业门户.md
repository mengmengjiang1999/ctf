Allcome clipbanker 最初是由研究人员
[@3xp0rtblog](https://twitter.com/3xp0rtblog)发现的，披露了它的广告、定价以及购买的联系方式（Telegram）。Allcome
clipbanker 提供的恶意软件即服务定价分为每月 25 美元和终身许可 220 美元两种。

![](https://image.3001.net/images/20220221/1645443678_62137a5e73c1cd4dc09a7.png!small)广告

Allcome clipbanker
在广告中特别强调它能够窃取许多不同付款方式的加密货币钱包，并且每周都会进行更新。客户也可以通过购买工具来自行增加窃密功能。

![image.png-128.1kB](https://image.3001.net/images/20220221/1645443117_6213782d0f872d3142779.png!small)对应翻译

## 功能

Allcome 是一个相对较小（120KB）的 C/C++ 程序。发现的所有样本都具有相同的持久化机制：样本将自己复制到
`%LOCALAPPDATA%\CrashDumps\subst.exe`，设置每分钟运行一次的计划任务
`NvTmRep_CrashReport3_{B2FE1952-0186}`。

![image.png-247.5kB](https://image.3001.net/images/20220221/1645443117_6213782dea6a1c37dea5f.png!small)持久化

样本创建一个名为 `08841d-18c7-4e2d-f7e29d`的互斥量，并检查文件是否以 `subst`开头。如果没有，启用上述持久化机制。

从资源段中检索加密的 C&C 服务器 URL，解密后使用。C&C 服务器响应 `+`或者 `-`，取决于客户是否拥有有效的许可证。服务器响应
`-`的话，样本不会窃取任何机密信息。如果响应其他内容，样本会检查或替换剪贴板内容。

![image.png-246.2kB](https://image.3001.net/images/20220221/1645443119_6213782f133e41d902240.png!small)部分代码

窃取的核心代码和其他 clipbanker 类似，Allcome 会将加密货币钱包地址替换为攻击者的地址，将交易劫持到攻击者的钱包。PayPal
地址、Steam 交易等都与之类似。

![image.png-79.3kB](https://image.3001.net/images/20220221/1645443120_621378308fc951c3bbc54.png!small)部分代码

它的功能相对原始，主要检查字符串长度和字符串的开头。并不关心来源，也不做过多的校验。

例如在替换 PayPal 交易地址时，样本将任何包含 `@`和
`.`的字符串替换为攻击者的电子邮件地址。这意味着，受害者复制任何的电子邮件地址都会被替换。这样的感染会非常嘈杂，而且也容易引起受害者的注意。

## 配置提取

C&C 地址、攻击者的钱包地址等配置信息都加密保存在资源段中。字符串表的每个 ID 都对应一个用于替换剪贴板内容的地址。

![image.png-420.5kB](https://image.3001.net/images/20220221/1645443121_6213783128c1f4345d331.png!small)资源信息

研究人员编写了提取配置信息的[脚本](https://github.com/struppigel/hedgehog-tools)，并且提供了一些已经提取的[配置信息](https://github.com/struppigel/hedgehog-tools/blob/main/extracted_allcome_configs.txt)。有些攻击者的钱包已经出现交易记录，可能来自失陷主机。

![image.png-456.4kB](https://image.3001.net/images/20220221/1645443122_6213783285486e782837c.png!small)提取并解密配置

可以通过 VirusTotal 查询
`behaviour_network:dba692117be7b6d3480fe5220fdd58b38bf.xyz`进一步收集样本。

## 结论

尽管广告经过了精心设计，但 Allcome clipbanker 的技术水平还是有限的。尽管如此，它们还是获得了想当的关注度，通过 VirusTotal
就可以检索到 51 个样本。营销就是一切！

## IOC

> 02b06acb113c31f5a2ac9c99f9614e0fab0f78afc5ae872e46bae139c2c9b1f6  
> hxxp://dba692117be7b6d3480fe5220fdd58b38bf.xyz/exp.php

## 参考来源

> [GData](https://www.gdatasoftware.com/blog/2022/02/37239-allcome-clipbanker-> is-a-newcomer-in-malware-underground-forums)

