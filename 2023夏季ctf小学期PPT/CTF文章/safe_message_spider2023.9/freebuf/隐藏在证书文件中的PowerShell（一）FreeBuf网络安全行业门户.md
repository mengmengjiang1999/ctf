![shutterstock_248596792.jpg](https://image.3001.net/images/20180813/1534153044_5b71515447c7d.jpg!small)**最近，NVISO实验室分析人员开发了某种YARA规则，利用它发现了多种恶意证书文件（.crt），这些证书文件中包含的并不是真正的认证证书，而是一个恶意的PowerShell脚本。作为《隐藏在证书文件中的PowerShell》系列的第1部份，本文中我们一起来探讨如何制作这种YARA规则，去揭开攻击者的这种“潜伏“行为。**

## 认证证书（Certificates）

Windows系统中的证书文件有多种后缀格式，如.cer 和 .crt，通常，.cer 文件包含的是二进制数据，而 .crt
文件包含的则是一些ASCII数据。但随着多种微软应用程序的出现，这两种扩展名可以互换，应用程序仍然也能正确处理这两种互换过后缀扩展名的证书文件（他们会查看证书内容并进行相应的解析）。

本文中我们还是遵守惯例，即用.cer 文件来包含二进制数据，而 .crt 文件来包含ASCII数据。.cer
文件中包含的认证数据是按照DER可辨别编码规则（Distinguished Encoding
Rules）来编码的，这是x.690标准指定的编码格式。以Microsoft office程序为例，以下是其安装目录中的 .cer 文件示例：

![01.png](https://image.3001.net/images/20180813/1534152336_5b714e90adee1.png!small).crt
文件中包含的是ASCII数据，说白了，它也就是对 .cer文件的base64编码。根据[RFC
7468标准](https://tools.ietf.org/html/rfc7468)来看，.crt 文件格式以“—BEGIN
CERTIFICATE”为开头，以“—END
CERTIFICATE”为结尾，中间则是一些经base64编码过的数据。使用[Certutil工具](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/certutil)，可将 .cer文件转换生成
.crt文件，以下就是 .crt的一个示例：

##
![02.png](https://image.3001.net/images/20180813/1534152720_5b7150100f808.png!small)对工具
Certutil 的利用

Certutil是一个[Windows下的多功能程序](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/certutil)，可用来执行各种证书和服务操作。自从Casey
Smith在Twitter上[发推演示了Certutil 的
base64解码编码](https://twitter.com/subTee/status/595739989721403393)之后，一些红队人员和网络犯罪份子就开始利用这种编码技术来生成各种可绕过入侵检测和杀毒软件的恶意文件。

Certutil不会验证要编码的二进制数据，也就是说，它能对任意文件进行编码。一些Windows
下的可执行程序（PE文件）都能用Certutil工具来轻松完成编码，编码之后的格式，很多入侵检测和杀毒软件都无法识别。以下是Windows可执行程序编码成
.crt文件的示例：

![03.png](https://image.3001.net/images/20180813/1534152798_5b71505e04934.png!small)从上图可以看到，这种base64编码数据的第一个字母是T。因为使用Certutil工具进行编码的PE文件通常都是这种类型的：也就是，PE文件的第一个字节是大写字母M，这里的M来自“MZ”，即MS-DOS的主要开发者 Mark Zbikowski 的缩写，用二进制来标记，也就是01001101。而base64编码是以6个比特块来编码的，所以
010011 就是第一个被编码的块，010011
用十进制表示就是19，而在base64编码中，0编码成A，1编码成B，以此类推...，19则被编码成T，如下所示：

![04.png](https://image.3001.net/images/20180813/1534152816_5b715070b6beb.png!small)

这也就是为什么base64编码的PE文件总是以T开头的原因。有很多种检测规则：就比如，如果文件以“—BEGIN
CERTIFICATE–”开头，之后是一个大写字母T，那么这种检测规则也能触发。

这就是一种“known-bad”式的检测规则，因为PE文件经Certutil工具编码后存在固定格式，所以，按照这种格式来针对性的查找就行。这种检测规则直接有效，我们利用它已经检测到很多编码过的PE文件。

## 检测规则制作

然而，在NVISO实验环境中，我们尝试做出比上述“已知恶意文件”（known-bad）更好的检测规则来，所以，这就是我们着力构建检测证书文件不包含真正证书的检测环境原因了，最终，我们的检测规则，不仅能检测出包含PE文件的证书文件，还能检测出其它不包含特定证书数据的恶意证书文件。

X.509格式证书是被广泛使用的数字证书标准，是用于标志通讯各方身份信息的一系列数据。常见的X.509格式证书包含 .cer 和
.crt类证书，它们都以二进制形式存放，不含私钥。

X.509标准证书数据都是以RFC 5280 定义的ASN.1语法来编码的，也就是以ASN.1序列开始的，这个序列标记号为
0x30，所以，这个开头的0x30数据也是经DER编码的二进制数据。

![05.png](https://image.3001.net/images/20180813/1534152876_5b7150ac0c0c2.png!small)如我们前述的PE文件编码说明，可以确定其在ASCII字节环境下，它是以0x30开头的，而在base64编码过程中，它首先则是以大写字母M开头的。

所以，基于此种原因，根据 [RFC
7468标准](https://tools.ietf.org/html/rfc7468)，任何X.509标准的有效证书文件编码后都是以“—BEGIN
CERTIFICATE–”开头，之后紧跟大写字母M。  

也就是说，那些包含“—BEGIN CERTIFICATE–”，但之后紧跟的字母不是M的证书文件，它们都不是有效的X.509标准证书文件。

最后，我们以此为方法创建了一条YARA规则，放到了 VirusTotal Intelligence跑了几个月：

    
    
    rule certificate_payload
    
    {
    
        strings:
    
            $re1 = /-----BEGIN CERTIFICATE-----\r\n[^M]/
    
        condition:
    
            $re1 at 0
    
    }

## 发现目标

应用这条YARA规则，我们检测到很多伪装成证书文件的PE文件和一些有意思的其它文件，而且也没对有效证书发出误报。

其中我们检测到比较有意思的一个证书文件是，它的MD5
哈希值为[0082aed588f76b517946a824fba43994](https://www.virustotal.com/#/file/eed598fa60ad25cd43f33e4d64cede06b45a5140df3d8e8e92d64c4a83fd4898/detection)，大概样子如下：

![06.png](https://image.3001.net/images/20180813/1534152962_5b7151026948f.png!small)一开始，在VirusTotal的60个杀毒软件检测引擎中，它的被检测率为0，也就是全部通过，但当我们用base64dump.py对它进行base64解码之后，看到了一些有意思的发现：

![07.png](https://image.3001.net/images/20180813/1534152978_5b715112b834b.png!small)

![08.png](https://image.3001.net/images/20180813/1534153003_5b71512b3cd64.png!small)这个证书文件竟然包含了经过编码的PowerShell脚本程序，吓得我们....。这个脚本的检测需要几个步骤，在《隐藏在证书文件中的PowerShell》系列的第2部份，我们会继续讨论。

## 总结

这种使用“非良性文件”（not known-good）而非使用“已知恶意文件”（known-bad）的检测方法，我们不仅能够检测到已知的恶意文件，还能检测出一些未知的恶意文件。除了YARA规则，我们还在Suricata和ClamAV杀毒引擎中创建内置规则，这些规则将在该系列的第3部份公布，未完待续，敬请期待。

 ***** **参考来源：**[nviso](https://blog.nviso.be/2018/07/31/powershell-inside-a-certificate-part-1/) **，clouds编译，转载请注明来自FreeBuf.COM**  

