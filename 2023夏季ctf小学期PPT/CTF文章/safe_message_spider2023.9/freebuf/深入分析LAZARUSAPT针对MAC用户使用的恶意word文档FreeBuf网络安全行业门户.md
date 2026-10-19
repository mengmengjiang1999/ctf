**就在上个月，卡巴斯基实验室的研究人员发现了一个针对macOS和Windows用户的恶意攻击活动，并将该活动命名为了“Lazarus
APT”。据了解，此次攻击活动主要针对的是金融领域的用户，受影响最为严重的当属加密货币交易平台的用户了。Lazarus网络犯罪组织，又名Hidden
Cobra，从2009年开始一直活跃至今，还有同学记得 日本索尼公司曾在2014年经历过一次严重的网络攻击吗？没错，那也是Lazarus干的。**

在这篇文章中，我们将主要对Lazarus在攻击macOS和Windows系统时所使用的攻击逻辑以及恶意Word文档进行分析。

![](https://image.3001.net/images/20190530/1559225800_5cefe5c8792bc.png!small)

实际上，利用VBA宏来创建恶意Microsoft Office文档已经不算什么新鲜事了，尤其是针对银行机构的木马病毒。但我们很少能够见到
针对macOS的恶意Word文档，正因如此，我们才需要更加深入地了解Lazarus的攻击技术细节，而这些内容是卡巴斯基的安全报告中没有提及到的。

## 启用了宏功能的恶意Word文档

下面给出的是Lazarus针对韩国地区用户的一份恶意文档样本：

![](https://image.3001.net/images/20190530/1559225809_5cefe5d13921c.png!small)

奇怪的是，卡巴斯基的研究人员发现，上述攻击活动大约是从2018年底才开始的，但是文档中标注的创建日期却是四年以前，也就是2014年11月3日。就文档内容来看，该文件声称是由一家名为““Han
Seung”的公司及其公司代表“Jin Seok Kim”提供的。

![](https://image.3001.net/images/20190530/1559225814_5cefe5d6d0cee.png!small)

我们在搜索引擎中找出了几家名叫“Han Seung”的公司，但这些公司都没有“Jin Seok
Kim”这个员工。因此，我们认为要么恶意文档中公司名称是假的，或者代表名称是假的，要么就是全都是假的。

我们使用oletools来对恶意文档中的VBA代码进行了反汇编，从中我们可以看到，文档首先会测试恶意代码是否能够在macOS上运行，如果可以运行，它将会根据VBA的版本来声明系统函数和popen函数。

![](https://image.3001.net/images/20190530/1559225820_5cefe5dc58c33.png!small)

如果目标系统不是macOS，那么文档会定义144个不同的数据数组，其中包含了ASCII码，而这些ASCII码可以组成一份完整的PowerShell脚本。

![](https://image.3001.net/images/20190530/1559225827_5cefe5e333c99.png!small)

重构之后的脚本代码段如下：

![](https://image.3001.net/images/20190530/1559225832_5cefe5e85e4cf.png!small)

一切就绪之后，代码会定义AutoOpen()的子路径，并再次测试目标平台是否为macOS或Windows。

![](https://image.3001.net/images/20190530/1559225839_5cefe5ef2267c.png!small)

我们可以看到目标设备的macOS版本架构，代码会通过system函数来调用Payload下载功能（使用curl命令实现，下载目录为/tmp），URL地址如下：

    
    
    https//nzssdm.com/assets/mt.dat

代码使用了chmod命令给Payload文件赋予了可执行权限，并运行了Payload。由于该文件是通过curl下载的，因此Gatekeeper和XProtect都无法检测到它。

Windows版本架构由一个包含了下列PowerShell命令的字符串组成：

    
    
    powershell-ExecutionPolicy Bypass -file spath

其中的spath是随机命名的，文件名为13个随机字符，但此时会添加.ps1作为文件后缀，，并保存在目标用户的temp目录中。

## macOS后门

mt.dat这个Payload文件是一个Mach-O
64位可执行文件，符号表中的数据表明，这是一个自定义后门。其中的部分变量从名字就可以猜测到对应的功能，比如说CheckUSB和ReplyOtherShellCmd等等。但是，那些包含了字符串“Troy”的函数其功能就没那么显而易见了。但有些同学可能知道，“Troy”是一个著名的恶意软件活动，主要针对的是韩国用户。

![](https://image.3001.net/images/20190530/1559225853_5cefe5fd3df32.png!small)

从这里大家可以看出，这些命令显然是从C2服务器发送过来的，静态分析结果也表明，ReplyTroyInfo方法首先会检测目标设备的主机名，然后进行网络信息收集，最后将收集到的数据进行加密后提取至远程服务器。

除此之外，攻击者还试图使用字符串规则匹配等方式来绕过某些遗留的反病毒机制。

![](https://image.3001.net/images/20190530/1559225858_5cefe602987e3.png!small)

执行恶意文件后，我们发现恶意软件会尝试与三个不同的C2服务器地址进行通信。每隔60秒，恶意软件就会执行curl_easy_perform方法来尝试与其中一个硬编码服务器地址建立连接。如果连接建立失败，进程会休眠60秒，并再次与下一台服务器尝试建立连接。

![](https://image.3001.net/images/20190530/1559225864_5cefe6083889e.png!small)

样本中的服务器地址列表如下：

> <https://baseballcharlemagnelegardeur.com>
>
> <https://www.tangowithcolette.com>
>
> <https://towingoperations.com>

使用netcat测试IP地址后，我们发现所有的服务器都处于活动状态：

![](https://image.3001.net/images/20190530/1559225873_5cefe611cad84.png!small)

但是，我们无法直接运行恶意软件，每一个尝试跟服务器建立连接的请求都遇到了406错误，说明请求格式有问题：

![](https://image.3001.net/images/20190530/1559225880_5cefe6183745f.png!small)

除此之外，我们还从C2服务器获取到了一份加密文件，下面给出的是其中一个恶意软件通信地址：

    
    
    https://www.tangowithcolette.com/pages/common.php

在下载该文件时，我们还发现了另一个引用地址：

![](https://image.3001.net/images/20190530/1559225895_5cefe627a3a41.png!small)

“_Incapsula_Resource…”脚本包含了大量十六进制值：

![](https://image.3001.net/images/20190530/1559225900_5cefe62c6cb4d.png!small)

将其转换为ASCII之后，我们得到了一份经过混淆处理的JavaScript：

![](https://image.3001.net/images/20190530/1559225904_5cefe630d9475.png!small)

脚本代码大概1400多行，包含了URI组件解码、资源获取、cookie移除和浏览器会话修改等功能。

## 总结

在这篇文章中，我们深入研究了Lazarus
APT组织的攻击活动，目前该活动主要针对的是macOS和Windows用户。因此，各大组织应尽可能地保护其macOS和Windows设备，但也不要忽略了Linux设备，因为攻击者肯定会不断更新自己的攻击技术来扩大攻击面。

 *** 参考来源：[sentinelone](https://www.sentinelone.com/blog/lazarus-apt-targets-mac-users-poisoned-word-document/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

