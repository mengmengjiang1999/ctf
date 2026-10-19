##  概述

**近日，Unit42安全团队在Github上公开了自己研发的powershell自动反混淆工具，Star数几日之间就突破了300，接下来，就来了解下这款神器的用法及原理。**

> 项目地址：<https://github.com/pan-> unit42/public_tools/tree/master/powershellprofiler>

![](https://image.3001.net/images/20191105/1572920274_5dc0dbd208b1e.png!small)

##  **使用方法**

工具用法很简洁，python PowerShellProfiler.py -f <file_name>，若要查看反混淆过程的话可以加上-d参数进行调试，下面使用官方给出的恶意脚本initial_obfusctaed_sample.ps1进行演示，该样本使用了IEX替换、字符串编码、运算符冗余、变量重命名等方式进行混淆。

![](https://image.3001.net/images/20191105/1572920311_5dc0dbf7da50f.png!small)运行PowerShellProfiler.py后，PowerShellProfiler打印出了每一步反混淆的步骤，反混淆后的脚本，以及最后的结论：该样本的恶意分数18.5，高威胁，是个Downloader脚本，病毒家族为Veil
Stream。

![](https://image.3001.net/images/20191105/1572920338_5dc0dc1217bd4.png!small)

##  **工具原理**

演示完了PowerShellProfiler.py的使用方法，来看一下工具的原理，主要为4个核心步骤： **反混淆目标脚本 - > 病毒家族检测 ->
可疑字符串扫描 -> 目标脚本恶意分数统计**

除了第一个函数，后三个函数的原理都是通过正则表达式特征码匹配，下面重点分析下第一个反混淆的函数unravelContent。

![](https://image.3001.net/images/20191105/1572920392_5dc0dc48a485d.png!small)进入该函数后，核心的反混淆函数为normalize()，在反混淆之前，工具会先对字符串进行相应的倒序、反编码、解压、解密等操作。这次的脚本initial_obfusctaed_sample.ps1存在frombase64string、decompress等字符串，首先会进入decompressContent这个反编码函数。

![](https://image.3001.net/images/20191105/1572920412_5dc0dc5c41804.png!small)该函数首先对脚本进行base64解密，然后尝试用各种压缩方式进行解压，直到解压成功为止。

![](https://image.3001.net/images/20191105/1572920429_5dc0dc6d704f5.png!small)

完成以上操作后，工具就调用normalize()函数进行反混淆，原理就是即时翻译powershell常用的混淆运算符、字符串，如：

> 1.删除一些无用的运算符：”空格”、”^”、”`”。
>
> 2.转化Char字节为ASCII码。
>
> 3.去掉”+”，连接字符串。
>
> 4.replace字符串。

![](https://image.3001.net/images/20191105/1572920687_5dc0dd6f279e6.png!small)反混淆前的脚本如下，存在大量的无用的运算符、char字符，以及一些明显的-replace替换函数。

![](https://image.3001.net/images/20191105/1572920720_5dc0dd908bd49.png!small)进行了normalize()函数反混淆后，得到的脚本如下，结构已经很清晰了，接下来工具就可以对该脚本进行特征码匹配了，如：downloadstring、Start-Process等可疑字符串的提取。

![](https://image.3001.net/images/20191105/1572920736_5dc0dda0c323d.png!small)

##  **结尾**

powershell作为APT攻击的常用攻击方式，免杀、混淆的方式千变万化，光使用该工具无法保证能对所有ps脚本进行反混淆检测，我们更应该深入理解ps脚本的混淆常用方法及原理，才能实时地与这类恶意攻击样本进行对抗。

 ***本文作者： 深信服千里目安全实验室，转载请注明来自FreeBuf.COM**  
  

