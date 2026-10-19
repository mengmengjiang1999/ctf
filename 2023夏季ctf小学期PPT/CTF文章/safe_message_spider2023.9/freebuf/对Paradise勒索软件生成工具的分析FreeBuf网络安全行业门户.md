当今的恶意软件生成工具越来越多，新的恶意软件变种也越来越多。

2017 年，Paradise 勒索软件首次通过钓鱼邮件开始攻击，包含下载安装勒索软件的恶意 IQY
附件。勒索软件的第一个版本包含一些缺陷，安全研究人员利用该缺陷构建了[免费解密工具](https://www.bleepingcomputer.com/news/security/paradise-ransomware-decryptor-gets-your-files-back-for-free/)，旧版勒索软件可以恢复文件解密。随后，攻击者更新恶意软件，通过 RSA 进行加密，这样在没有私钥的情况下就无法解密。

正如 BleepingComputer 在 2021
年夏天[报道](https://www.bleepingcomputer.com/news/security/paradise-ransomware-source-code-released-on-a-hacking-forum/)的，Paradise 勒索软件源码在 XSS.IS 黑客论坛上被泄露。

![](https://image.3001.net/images/20210915/1631697351_6141b9c7a2fc0fc9403d6.jpg!small)

恶意软件生成工具是 .NET 写的，可以在本地和虚拟化环境中运行。

![](https://image.3001.net/images/20210915/1631697356_6141b9cc4b02102adbd32.png!small)

从泄露的源码来看，与 Microsoft VS 的默认结构类似，简单而精巧：

![](https://image.3001.net/images/20210915/1631697360_6141b9d0d4182f422a8d4.png!small)

快速对代码进行分析后有一些发现。尽管生成的勒索软件会公开暴露，但为了阻碍分析人员和分析工具，攻击者仍然插入了大量的检查代码。

## 语言

源代码中可以找到开发人员写的注释，Google 认为是俄语。

![](https://image.3001.net/images/20210915/1631697364_6141b9d4e77bd346f9115.png!small)

## 用户名

Microsoft Visual Studio 提供了将源码编译为二进制文件的用户信息。信息被留存到 `.csproj`文件中，记录了编译和链接的环境设置。

![](https://image.3001.net/images/20210915/1631697369_6141b9d90785cbe9fbe4e.png!small)

## 配置

构建工具的某些配置是直接在源代码中配置的字符串，而非从外部的配置文件读取。可能是生成工具仅用于高级用户或者是攻击者内部使用而非合作方。

![](https://image.3001.net/images/20210915/1631697372_6141b9dc9bd8ec127b523.png!small)

## 名称

从字符串和配置信息的角度上看，分析人员相信该恶意软件生成工具确实是属于 Paradise 勒索软件。

![](https://image.3001.net/images/20210915/1631697380_6141b9e4cd0bf974dec7f.png!small)

![](https://image.3001.net/images/20210915/1631697385_6141b9e981a9f8afbc715.png!small)

## 内存

即使使用不同的配置名称运行 Paradise 勒索软件，恶意软件也会在系统运行环境的内存中增加一个
`dp_main`。样本会查看字符串的计数项，以了解有多少进程在并行执行。

![](https://image.3001.net/images/20210915/1631697389_6141b9edd43e9fd4f1d7b.png!small)

## 持久化

虽然修改注册表自启动很常见，但 Paradise 勒索软件似乎会将自身复制到一个名为 DP（在 appdata
服务目录下）的特定目录中，并且看起来它总是以相同的方式命名恶意软件名称，与配置无关。

![](https://image.3001.net/images/20210915/1631697393_6141b9f14692538378c8e.png!small)

## 删除卷影副本

勒索软件一般都会删除卷影副本，执行 `ProcessStartInfo psiOpt = new ProcessStartInfo(@"cmd.exe",
@"/C sc delete VSS");`即可。

## C&C

攻击者向默认的 `/api/Encrypted.php`发送勒索相关信息。

![](https://image.3001.net/images/20210915/1631697395_6141b9f3d6fd7751908cb.png!small)

## 加密密钥

从 718 行开始，如下所示：

![](https://image.3001.net/images/20210915/1631697398_6141b9f67a0d4ed464161.png!small)

如果失陷主机中没有密钥，Paradise 勒索软件会生成密钥并保存在本地。不幸的是，加密保存的过程做的无懈可击。

![](https://image.3001.net/images/20210915/1631697408_6141ba007448a6a37c528.png!small)

`SavePrivateKey`实际上保存的是加密的私钥和 RSA 的公钥。调用一个名为 `SavekeysToFiles`的新函数，将它们保存到一个名为
`DecryptionInfo.auth`的文件中。

![](https://image.3001.net/images/20210915/1631697413_6141ba05a6a7ae4d50431.png!small)

Paradise 勒索软件作者仅加密大文件的前 10MB，而小文件的话会将文件切分成 117 个字节遍历处理。

## IOC

> 753f1e353ad0eb75555f81e090a3e89339d96266f5e33e2ada34c9ea655dcee9  
> e375edc127182453ad7ed84ae3abac3759dded7265284af48015a165e439f26c  
> 0dfb6a940a583432f21ce03634c0e8d6a9030443e391cf44f9581212716d4308  
> 363a99b2480c11b9431c046d44b323807e9b11bf237cc291dde11151d8b75581  
> 5eb2c22d092f3bf2077d7e9128c38c1bc29fd0b06479646c05afb0bf741891dc  
> f282d765bb83d76be318a2a982605d06619da2376165ba12cc6ca4e50aa0754d  
> a1428e2c84c3420a0481e524e103db7fde84d2107bd02738349c48ee4d6a5353  
> e9ae7a5837b34b65608964e7315450a3459e0e01366769b68b904504a55db102  
> 07958ee0ed74c8e4637d0903d686e66e7bd9e6b89bca0d3df4531d590c848a05

## 结论

每个恶意软件的作者都会在编写源代码时保留一定的设计风格和设计模式。本次介绍了部分 Paradise 勒索软件的特征，希望对安全分析人员有所帮助。

## 参考来源

> [Marcoramilli](https://marcoramilli.com/2021/08/23/paradise-ransomware-the-> builder/)

