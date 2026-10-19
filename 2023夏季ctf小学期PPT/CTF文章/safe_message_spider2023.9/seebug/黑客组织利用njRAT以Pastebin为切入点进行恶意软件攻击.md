**译者：知道创宇404实验室翻译组  
原文链接：<https://unit42.paloaltonetworks.com/njrat-pastebin-command-and-control/>**

### 概要

今年10月以来，研究人员发现，恶意软件攻击者在利用一种远程访问木马njRAT（也被称为Bladabindi）从Pastebin下载并传送第二阶段的有效负载。Pastebin是一个流行网站，可匿名存储数据。攻击者利用这一服务发布恶意数据，恶意软件可以通过一个简短的URL访问这些数据，避免使用他们自己的命令和控制（C2）基础设施，以免引起注意。

在这篇文章中，我们将介绍在野外发现的不同情形以及数据转换，并描述downloader组件与其第二阶段恶意软件之间的关系。

### Pastebin C2隧道

攻击者将Pastebin的C2隧道作为恶意负载的托管服务，这些负载可被键盘记录程序、后门程序或木马程序下载。

托管的数据在形式上有所不同，具有不同的数据编码和转换，包括传统的base64编码、十六进制和JSON数据、压缩blob和嵌入恶意url的明文数据。据分析，攻击者这么做是为了逃避安全产品的检测。

### base64编码响应丢弃的第二阶段恶意软件

  * **Downloader** : 91f4b53cc4fc22c636406f527e3dca3f10aea7cc0d7a9ee955c9631c80d9777f
  * **Second-stage** : 492ea8436c9a4d69e0a95a13bac51f821e8454113d4e1ccd9c8d903a070e37b2
  * **Source URL** : hxxps://pastebin[.]com/raw/VbSn9AnN

Downloader（91f4b53cc4fc22c636406f527e3dca3f10aea7cc0d7a9ee955c9631c80d9777f）请求Pastebin
C2数据并使用所规避的存储数据版本，该版本与传统的base64编码相对应。

![](https://images.seebug.org/content/images/2020/12/e7d24281-53d6-4b69-a79b-4d4d5949bf8e.png-w331s)
图1.base64编码数据与可执行文件的转换。

一旦解码，最终的有效负载将显示为一个32位的.NET可执行文件，它使用了几个Windows
API函数，包括GetKeyboardState()、GetAsynckeyState()、MapVirtualKey()等。这些函数通常由键盘记录程序和木马程序使用，也可以用来过滤用户数据。值得注意的是，下载器和第二阶段可执行文件在功能和代码方面是相似的。

下图显示了第二阶段示例的反编译代码的截图。

![](https://images.seebug.org/content/images/2020/12/dfa1548b-84e8-4154-9b17-94eab1530c62.png-w331s)
图2.与键盘记录程序功能相关的Windows API。

### base64编码反向规避丢弃的第二阶段恶意软件

  * **Downloader** : 67cbb963597abb591b8dc527e851fc8823ff22d367f4b580eb95dfad7e399e66
  * **Second-stage** : ffb01512e7357ab899c8eabe01a261fe9462b29bc80158a67e75fdc9c2b348f9
  * **Source URL** : hxxps://pastebin[.]com/raw/JMkdgr4h

在这个版本中，base64数据被反向，大概是为了躲避检测。

![](https://images.seebug.org/content/images/2020/12/d9266fe6-2b0a-40fa-9c7c-1e7ab917a19f.png-w331s)
图3.base64编码的反向字符串及其向base64格式的转换。

对数据进行适当的转换和解码后，最终的第二阶段32位.NET可执行文件与上个示例类似，它具有键盘记录和木马的功能。为了得到最终的有效负载，需要三个数据转换层。

### ASCII和base64响应丢弃的第二阶段恶意软件

  * **Downloader** : 9ba0126bd6d0c4b41f5740d3099e1b99fed45b003b78c500430574d57ad1ad39
  * **Second-stage** : dfc8bffef19b68cfa2807b2faaf42de3d4903363657f7c0d27435a767652d5b4
  * **Source URL** : hxxps://pastebin[.]com/raw/LKRwaias

在这个版本中，base64数据以十六进制字符表示。

![](https://images.seebug.org/content/images/2020/12/98fc99c7-83c4-4e32-b3c4-631b6f351161.png-w331s)
图4.十六进制编码字符串及其向base64格式的转换。

正确解码Hex和base64数据后，转储程序也是32位.NET可执行文件，与上一个示例具有相同的恶意特征。

### base64编码和压缩数据响应丢弃的第二阶段恶意软件

  * **Downloader** : 54cf2d7b27faecfe7f44fb67cb608ce5e33a7c00339d13bb35fdb071063d7654
  * **Second-stage** : 96c7c2a166761b647d7588428fbdd6030bb38e5ef3d407de71da657f76b74cac
  * **Source URL** : hxxp://pastebin[.]com/raw/zHLUaPvW

与其他示例不同，此32位.NET启动程序可以使用从Pastebin获取的压缩数据。

![](https://images.seebug.org/content/images/2020/12/b1b47563-387a-448d-b213-8dc423802fa8.png-w331s)
图5.解压并执行base64压缩数据。

下载程序执行以下操作：

  * 通过执行DownloadString()函数，将作为字符串的base64编码和压缩数据下载，该字符串是由形成目标URL的变量str，str2，str3和str4串联而成的。
  * base64和压缩数据现在由FromBase64String()函数解码，并由DecompressGZip()函数解压缩。最终将一个可执行文件存储在rawAssembly变量的字节数组中。
  * 最后，调用Load()。EntryPoint.Invoke()是通过将rawsassembly变量传递到内存中的可执行文件来实现的，以便在系统中定位并释放恶意负载。

下图显示了执行前驻留在内存中的经过解压缩的32位.NET可执行数据。

![](https://images.seebug.org/content/images/2020/12/f1df6855-9c57-4c73-9059-165025aede86.png-w331s)
图6.解压内存中的第二阶段恶意软件。

### URL链接响应丢弃的第二阶段恶意软件

  * **Downloader** : bd2387161cc077bfca0e0aae5d63820d1791f528feef65de575999454762d617
  * **Second-stage** : 7754d2a87a7c3941197c97e99bcc4f7d2960f6de04d280071eb190eac46dc7d8
  * **Source URL** : hxxp://pastebin[.]com/raw/ZFchNrpH

这个.NET下载程序使用传统的方法从远程URL获取可执行文件。目标地址指向hxxp://textfiles[.]us/driverupdate0.exe。

根据VirusTotal的说法，几家供应商将这个恶意软件样本识别为恶意软件。

![](https://images.seebug.org/content/images/2020/12/e35f51c8-6660-46d3-b65d-aaead3850c2f.png-w331s)
图7.driverupdate0.exe可执行文件的VirusTotal及其检测率。

### JSON响应中的配置文件

  * **Downloader** : 94e648c0166ee2a63270772840f721ba52a73296159e6b72a1428377f6f329ad
  * **Source URL** : hxxps://pastebin[.]com/raw/8DEsZn2y

在这个版本中，使用了JSON格式的数据。其中一个关键字名为“downlodLink”（恶意软件攻击者故意拼错），这表示该值将是一个URL，在该URL中可以下载其他组件。虽然没有提供关于这个特定文件目标的更多信息，但它可能被用作配置文件。

![](https://images.seebug.org/content/images/2020/12/02c8d0d1-6ccb-486c-9dbe-a9956ce776de.png-w331s)
图8.基于JSON的恶意软件配置文件。

### 代理Scraper被HTML响应丢弃

  * **Downloader** : 97227c346830b4df87c92fce616bdec2d6dcbc3e6de3f1c88734fe82e2459b88
  * **Proxy Scraper.exe** : e3ea8a206b03d0a49a2601fe210c949a3c008c97e5dbf77968c0d08d2b6c1255
  * **MaterialSkin.dll** : b9879df15e82c52e9166c71f7b177c57bd4c8289821a65a9d3f5228b3f606b4e
  * **Source URL** : hxxps://pastebin[.]com/rw/770qPDMt

此恶意软件会解析HTML页面，以获取链接从而进一步攻击。对于这个特定的示例，Pastebin数据用于提供软件下载的链接。

![](https://images.seebug.org/content/images/2020/12/3a530a50-377d-40ff-9c71-7ed2309377e0.png-w331s)
图9.指向代理Scraper软件的链接。

下载链接指向一个名为Simple + Scraper.zip的压缩文件，其中包含两个文件：MaterialSkin.dll和Proxy
Scraper.exe。通过使用.NET反编译软件对代码进行静态检查，我们发现下载程序恶意软件使用Pastebin作为存储库来托管与Proxy
Scraper软件相关的更新链接。

![](https://images.seebug.org/content/images/2020/12/3ab9e554-8f9a-4ebf-a3ab-2725affa3ae9.png-w331s)
图10.用于检查与Proxy Scraper软件相关更新的.NET代码。

### 结论

Pastebin
C2隧道仍然存在，并且被njRAT以下载Pastebin中托管的数据的方式来传递恶意有效负载，从而使恶意软件组织充分利用基于paste的公共服务。研究发现，攻击者将其第二阶段有效负载托管在Pastebin中，并对此类数据进行加密或混淆处理，以躲避检测。此外，攻击者可能会长期使用Pastebin这类的服务。

### IOCs

**Samples**

03c7015046ef4e39a209384f2632812fa561bfacffc8b195542930e91fa6dceb

205341c9ad85f4fc99b1e2d0a6a5ba5c513ad33e7009cdf5d2864a422d063aba

2270b21b756bf5b5b1b5002e844d0abe10179c7178f70cd3f7de02473401443a

54cf2d7b27faecfe7f44fb67cb608ce5e33a7c00339d13bb35fdb071063d7654

54d7ee587332bfb04b5bc00ca1e8b6c245bb70a52f34835f9151b9978920b6d7

678a25710addeefd8d42903ceddd1c82c70b75c37a80cf2661dab7ced6732cd3

67cbb963597abb591b8dc527e851fc8823ff22d367f4b580eb95dfad7e399e66

6817906a5eff7b02846e4e6a492ee57c2596d3f19708d8483bef7126faa7267f

69366be315acc001c4b9b10ffc67dad148e73ca46e5ec23509f9bb3eedcd4c08

94c2196749457b23f82395277a47d4380217dd821d0a6592fc27e1e375a3af70

94e648c0166ee2a63270772840f721ba52a73296159e6b72a1428377f6f329ad

96640d0c05dd83bb10bd7224004056e5527f6fad4429beaf4afa7bad9001efb7

97227c346830b4df87c92fce616bdec2d6dcbc3e6de3f1c88734fe82e2459b88

97b943a45b4716fcea4c73dce4cefe6492a6a51e83503347adcd6c6e02261b84

9ba0126bd6d0c4b41f5740d3099e1b99fed45b003b78c500430574d57ad1ad39

bd2387161cc077bfca0e0aae5d63820d1791f528feef65de575999454762d617

**Second Stage**

9982c4d431425569a69a022a7a7185e8c47783a792256f4c5420f9e023dee12a

d347080fbc66e680e2187944efbca11ff10dc5bfcc76c815275c4598bb410ef6

30c071a9e0207f0ca98105c40ac60ec50104894f3e4ed0fb1e7b901f56d14ad4

231d52100365c14be32e2e81306b2bb16c169145a8dbcdc8f921c23d7733cef0

fd5c731bb53c4e94622e016d83e4c0d605baf8e34c7960f72ff2953c65f0084c

b3730931aaa526d0189aa267aa0d134eb89e538d79737f332223d3fc697c4f5a

75b833695a12e16894a1e1650ad7ed51e6f8599ceaf35bbd8e9461d3454ab711

6d0b09fe963499999af2c16e90b6f8c5ac51138509cc7f3edb4b35ff8bef1f12

2af1bb05a5fde5500ea737c08f1b675a306150a26610d2ae3279f8157a3cb4df

db8ca46451a6c32e3b7901b50837500768bb913cafb5e12e2111f8b264672219

5ebb875556caefb78d5050e243f0efb9c2c8e759c9b32a426358de0c391e8185

bdc33dbdfd92207ad88b6feb3066bb662a6ca5cf02710870cae38320bb3a35bf

08f378fe42aec892e6eb163edc3374b0e2eb677bd01e398addd1b1fca4cd23c4

### URLs

**Active:**

hxxp://pastebin[.]com/raw/JKqwsAs6

hxxp://pastebin[.]com/raw/pc9QbQCK

hxxp://pastebin[.]com/raw/Rpx7tm9N

hxxp://pastebin[.]com/raw/hsGSLP89

hxxp://pastebin[.]com/raw/HNkipzLK

hxxp://pastebin[.]com/raw/Z3mcNqjz

hxxp://pastebin[.]com/raw/h5yBCwpY

hxxp://pastebin[.]com/raw/zHLUaPvW

hxxp://pastebin[.]com/raw/V6UWZm2n

hxxp://pastebin[.]com/raw/rTjmne99

hxxp://pastebin[.]com/raw/JMkdgr4h

hxxp://pastebin[.]com/raw/yPTNdYRN

hxxp://pastebin[.]com/raw/q56JPtdY

hxxp://pastebin[.]com/raw/a3U5MMj2

hxxp://pastebin[.]com/raw/E4MB4MFj

hxxp://pastebin[.]com/raw/770qPDMt

hxxp://pastebin[.]com/raw/YtuXz7YX

hxxp://pastebin[.]com/raw/LKRwaias

hxxp://pastebin[.]com/raw/ZFchNrpH

hxxp://pastebin[.]com/raw/8DEsZn2y

**Inactive**

hxxp://pastebin[.]com/raw/TWQYHv9Y

hxxp://pastebin[.]com/raw/0HpgqDt2

hxxp://pastebin[.]com/raw/1t8LPE7R

hxxp://pastebin[.]com/raw/3vsJLpWu

hxxp://pastebin[.]com/raw/6MFWAdWS

hxxp://pastebin[.]com/raw/AqndxJKK

hxxp://pastebin[.]com/raw/SdcQ9yPM

hxxp://pastebin[.]com/raw/XMKKNkb0

hxxp://pastebin[.]com/raw/ZM6QyknC

hxxp://pastebin[.]com/raw/pMDgUv62

hxxp://pastebin[.]com/raw/yEw5XbvF

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1425/>

