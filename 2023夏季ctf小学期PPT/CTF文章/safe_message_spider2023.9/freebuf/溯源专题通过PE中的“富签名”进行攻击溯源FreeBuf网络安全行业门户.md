欢迎关注同名微信公众号！[狼蛛安全实验室](https://mp.weixin.qq.com/s/ccMQEhCoSwOaUV1RMFpFvg)！

众所周知，Windows PE文件结构长这样。

![1668495575_637338d71086ca4da8667.jpg!small](https://image.3001.net/images/20221115/1668495575_637338d71086ca4da8667.jpg!small)

落到文件就像是这样，其中“■”颜色选中的地方是“IMAGE_DOS_HEADER”。

![1668495589_637338e51a18961c389dc.jpg!small](https://image.3001.net/images/20221115/1668495589_637338e51a18961c389dc.jpg!small)

按照微软的文档说明，结构应该是这样：

![1668495599_637338ef229a3c2a973ad.jpg!small](https://image.3001.net/images/20221115/1668495599_637338ef229a3c2a973ad.jpg!small)

是不是感觉怪怪的，好像与文档对不上？

我们可以尝试着人工先分析一下，首先，把这段明文的内容提取出来，根据内容“This program cannot be run in DOS
mode.(该程序不能以DOS模式运行。)”可以猜出，这段明文可能是用来在dos环境下，提示该程序无法直接运行的。

![1668495612_637338fc0ac673ca12e91.jpg!small](https://image.3001.net/images/20221115/1668495612_637338fc0ac673ca12e91.jpg!small)

那么我们跳过这段数据继续往下看，下面这段看起来似乎比较有结构话，很多地方都存在重复字节。

![1668495622_637339064079b83ee11b6.jpg!small](https://image.3001.net/images/20221115/1668495622_637339064079b83ee11b6.jpg!small)

作者在对比了多个样本后发现，在PE头之前，去掉看似被填充的0x00以后，在他倒数的0x08~0x04位置，每个样本均出现了明文字符串”Rich”。

![1668495628_6373390cec63bf9b0de8d.jpg!small](https://image.3001.net/images/20221115/1668495628_6373390cec63bf9b0de8d.jpg!small)

作者查阅了大量资料，发现一段数据，是使用微软的编译器时微软故意留下的编译器信息。

称为“Rich Signature”（富签名），该签名似乎只有在使用微软Visual Studio编译器时留下。

下面，作者带大家一起分析一下Rich签名，老规矩，作者会尽量讲的细一点，希望大家可以有所收获。

首先，我们可以看到，在这个”Rich
Signature”中存在大量的重复字节，例如图中的红框和绿框部分，而最后一个红框部分内容很巧合的出现在明文Rich（蓝框）的后面，形成了一个结尾。但是不清楚有何用途。

![1668495642_6373391a72aa5a0713d73.jpg!small](https://image.3001.net/images/20221115/1668495642_6373391a72aa5a0713d73.jpg!small)

作者在经过对Visual Studio的link.exe逆向分析后，在函数中找到了答案，异或！

![1668495652_6373392404782b8f75ad9.jpg!small](https://image.3001.net/images/20221115/1668495652_6373392404782b8f75ad9.jpg!small)

根据他的算法我们可以看出来，他使用”Rich
Signature”最后的4字节进行了一次异或，所以作者按照上图所示，使用CyberChef工具对整个”Rich
Signature”异或一下，来还原原始数据。

![1668495661_6373392d86c36acf3679f.jpg!small](https://image.3001.net/images/20221115/1668495661_6373392d86c36acf3679f.jpg!small)

我们根据逆向link.exe时看到的生成Rich签名的处理逻辑继续分析。首先我们忽略最前面的“DanS”部分的结构头，从0x10继续分析。

![1668495669_63733935372a5521fe1de.jpg!small](https://image.3001.net/images/20221115/1668495669_63733935372a5521fe1de.jpg!small)

虽然从图中我们可以很明显的看出使用异或解密后的数据十分的有结构化，但是还是无法明确每个字节的含义是什么，作者又在查阅了一大堆资料后，从微软泄露的“Windows
2000“的源代码中发现了更多的答案。

![1668495681_63733941119015e988fac.jpg!small](https://image.3001.net/images/20221115/1668495681_63733941119015e988fac.jpg!small)

正如我们所看到，”Rich
Signature”以每”PRODITEM(8字节)”为一个结构数组，每个”PRODITEM(8字节)”由三个部分组成，分别是”dwProdid(ProdID(2字节)、dwProdid(2字节))”、”dwCount(4字节)“。我们按照此结构继续解析。

 **注意大小端！注意大小端！注意大小端！**

首先读取2字节把16进制转换为10进制，”0x78 0x09″->”30729″。//ProdID

再读取2字节把16进制转换为10进制，”0x00 0x93″->”147″。//dwProdid

再读取4字节把16进制转换为10进制，”0x00 0x00 0x00 0x0A”->”10″。//dwCount

到此为止，我们便成功提取了富签名的信息，但是这些信息还不足以对我们产生太多的价值，但是如果价值不大，那么微软为什么会把这个信息加密隐藏在PE中呢？我们接着往下看。

作者继续分析了泄露的“Windows
2000“源代码，发现”dwProdid“代表的是编译工具内部的版本号，例如在本次的样本中，”147″则代表着”Implib900″（完整版本号见文末附录二）。

而”ProdID“（产品标识符）存在于”Visual Studio“开发工具中，包括微软的链接器、C/C++ 编译器、MASM、资源、导入、implibs
等。

当开发者在使用这些开发工具编译文件时，便会将这些开发工具的”ProdID“写入”Rich
Signature”中，在本次的样本中，”30729″就是代表着”Visual Studio 2008 SP1 [9.0]、Visual C++ 2008
SP1 [9.0]”（完整版本号见文末附录三）。

最后的”dwCount”则是开发工具被调用到的次数，”10″代表着被调用了10次，表示参与编译的文件有10个，注意：此处的数量不一定是开发者编写了10个文件，而是开发者编写的文件加参与编译的系统库一共有10个文件调用了开发工具。

以上我们便完成了对一个”PRODITEM”结构数组的分析，我们继续往下看，…，直到看到这里。

![1668495690_6373394a2ffc7b6e5c206.jpg!small](https://image.3001.net/images/20221115/1668495690_6373394a2ffc7b6e5c206.jpg!small)

我们按照上面的方法继续解析一下。

首先读取2字节把16进制转换为10进制，”0x7B 0x8E”->”31630″。//ProdID

再读取2字节把16进制转换为10进制，”0x01 0x02″->”258″。//dwProdid

再读取4字节把16进制转换为10进制，”0x00 0x00 0x00 0x01″->”1″。//dwCount

根据附录二，”258(dwProdid)”表示”Linker1400″，值得注意的是“dwProdid”中的“Linker”、”Cvtres”字段极有可能表示的是开发者使用的VS版本，根据附录三，”31630(ProdID)”表示”Visual
Studio 2022 version 17.3.4″。

所以，这个样本就是使用”Visual Studio 2022 version 17.3.4″开发编译的！

总结一下，综上所述，当使用微软编译器编译时，他会将编译器的信息一起加密记录在编译完的二进制文件中，可以通过这个信息精准的识别编译器的版本、内部版本、调用次数等等，还可以通过编译器信息知道被编译的文件是c语言还是c++，是汇编还是cvtres，又或者是什么Visual
Studio版本。

那么我们在溯源的时候可以怎么使用呢？

我们可以通过上述信息知道攻击者是使用什么环境编译的样本，并可以接着YARA在VT上进行Hunter，狩猎更多的样本。

附录一(yara规则模板)：

    
    
    rule MSVC5{condition:pe.rich_signature.version(1668) and pe.rich_signature.toolid(6)}

附录二(dwProdid)：

![](https://image.3001.net/images/20221115/1668496184_63733b389ac65df51689c.jpg!small)

附录三(Visual Studio MSC版本)：

![](https://image.3001.net/images/20221115/1668495812_637339c469bed4433f5cd.jpg!small)

