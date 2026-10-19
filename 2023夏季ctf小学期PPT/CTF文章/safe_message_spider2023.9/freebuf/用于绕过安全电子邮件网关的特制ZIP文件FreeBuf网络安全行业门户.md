**攻击者一直在寻找新的技巧来分发恶意软件，而不会被防病毒扫描程序和电子邮件网关检测到。这在一个新的网络钓鱼活动中得到了实现，该活动利用了特制的ZIP文件，该文件旨在绕过安全的电子邮件网关来分发NanoCore
RAT。**

每个ZIP归档文件都包含一个特殊的结构，其中包含压缩的数据和有关压缩文件的信息。每个ZIP归档文件还包含一个“中央目录结尾”（EOCD）记录，该记录用于指示归档文件结构的结尾。

![](https://image.3001.net/images/20191108/1573206948_5dc53ba410427.png!small)

在Trustwave研究员发现的一项新的垃圾邮件活动中发现了一封垃圾邮件，该邮件冒充来自USCO Logistics进出口操作专家的订单运输信息。

![](https://image.3001.net/images/20191108/1573206953_5dc53ba90dac7.png!small)

Trustwave安全电子邮件网关（SEG）中的电子邮件,来源:

> <https://www.bleepingcomputer.com/news/security/specially-crafted-zip-files-> used-to-bypass-secure-email-gateways/>

在检查文件时，Trustwave的研究人员发现ZIP存档包含两个不同的存档结构，每个结构都由自己的EOCD记录标记。

![](https://image.3001.net/images/20191108/1573206961_5dc53bb19c0e3.png!small)

如前所述，ZIP存档应该只包含一个EOCD记录，因此这表明ZIP文件是经过特殊设计的，包含两个存档结构。

第一个ZIP结构用于一个诱饵的order.jpg文件，它只是一个无害的图像文件。但是，第二个ZIP结构包含一个名为SHIPPING_MX00034900_PL_INV_pdf.exe的文件，它是远程访问木马NanoCore
RAT。

攻击者创建此特制的ZIP存档，以绕过安全的电子邮件网关，其网关使用的解压缩程序可能无法正确提取恶意软件，并且只会看到无害的诱饵图像文件。

### 不同的文件提取器的行为不同

使用各种文件提取程序打开存档时，Trustwave研究员发现每个文件提取器对存档的处理方式有所不同。

例如，Windows内置的ZIP提取程序指出该ZIP文件无效，因此不会提取该文件。

![](https://image.3001.net/images/20191108/1573206968_5dc53bb8ea8e1.png!small)

### Windows尝试提取ZIP附件

当BleepingComputer用7-Zip 9.20进行测试时，警告显示ZIP文件存在问题，但能够提取文件。

![](https://image.3001.net/images/20191108/1573206973_5dc53bbd6cb77.png!small)

提取时发出7-Zip发出警告

但是，提取的文件不是恶意负载，而是无害的order.jpg图像文件。

![](https://image.3001.net/images/20191108/1573206983_5dc53bc765d92.png!small)

### 7zip提取order.jpg文件

但是，WinRAR在提取ZIP存档时未发出警告，并且提取了SHIPPING_MX00034900_PL_INV_pdf.exe NanoCore文件。

![](https://image.3001.net/images/20191108/1573206997_5dc53bd52377a.png!small)

### WinRAR提取NanoCore文件

由于各种取消存档引擎显示的行为不同，Trustwave认为其中一些引擎可能检测到无害文件，而不是恶意有效负载。

“此示例对网关扫描器提出了挑战。根据所使用的解压缩引擎的类型，很可能仅对诱饵文件进行审查和审查，然而恶意软件未被注意-就像某些最流行的解压工具未能解压出第二个ZIP结构。”

在测试了众多文件提取程序之后，Trustwave确定只有某些版本的PowerArchiver，WinRar和较旧的7-Zip实用程序才能正确提取NanoCore可执行文件。

这表明，尽管该技术可能有助于绕过电子邮件扫描程序，但其副作用还在于难以提取恶意负载。这将导致受感染的受害者比攻击者预期的要少得多。

### 来源:

> Trustwave:<https://www.trustwave.com/en-us/resources/blogs/spiderlabs-> blog/double-loaded-zip-file-delivers-nanocore/>
>
> BleepinpComputer:<https://www.bleepingcomputer.com/news/security/specially-> crafted-zip-files-used-to-bypass-secure-email-gateways/>

 ***本文作者：Alluka，转载请注明来自FreeBuf.COM**

