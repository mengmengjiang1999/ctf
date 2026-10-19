**在对船舶控制系统进行测试时，我们注意到控制系统对西门子Scalance工业以太网交换机的严重依赖，因此为对其进行了深入研究。经过逆向发现可使用静态密钥对管理密码进行可逆加密，并使用不同的密钥对用户密码进行可逆加密。**

以下是我们找到静态密钥的方法。

![](https://image.3001.net/images/20190909/1568011554_5d75f52283f4f.png!small)

研究开始于配置文件，密码看起来很不寻常，似乎不是单向哈希。 已有漏洞可用于恢复配置文件和固件，这意味着攻击者可以访问此信息：

![](https://image.3001.net/images/20190909/1568011619_5d75f5636e711.png!small)

密码很短小，长度取决于密码大小，并会被填充至8个字符。 这意味着使用的是分组密码进行加密。

其中用于测试的64位大小的密码表明利用DES或Blowfish作为加密算法。 另外值得注意的是，管理员帐户有两个密码。

## 固件逆向

固件文件为ARM ELF文件，在ELF文件上运行“binwalk”命令，找到“VxWorks”实时操作系统和LZMA压缩数据的版本字符串。

![](https://image.3001.net/images/20190909/1568011966_5d75f6be9efcb.png!small)

lzma压缩文件是设备的主要固件，对它进行解压缩表明它是一个二进制文件，没有可识别的文件签名。hexdump解压后的二进制文件表明它是arm固件。

![](https://image.3001.net/images/20190909/1568012049_5d75f7110c818.png!small)

由于固件已被识别并且格式可读，因此可以将其作为ARM Little-endian二进制文件加载到IDA中。

![](https://image.3001.net/images/20190909/1568012090_5d75f73aea0ae.png!small)

对固件有效负载执行静态分析，并且没有关于设备内部的已知信息。 因此，固件的入口点尚不清楚。

发生这种情况时，可以使用默认地址0x00000000作为入口点。 但是，对函数和数据的引用将不准确。

![](https://image.3001.net/images/20190909/1568012152_5d75f77872933.png!small)

查找入口点非常重要，因为它可以更容易地识别正在使用的代码引用和跟踪函数。有许多技术可以使用，由于固件使用VxWorks实时操作系统，因此存在快捷方式。

![](https://image.3001.net/images/20190909/1568012233_5d75f7c92815a.png!small)

VxWorks符号表提供与字符串引用匹配的函数引用，允许固件中的每个函数都有一个定义其函数的名称。通过标识固件启动时使用“sysInit”函数找到该函数的入口点。

ram可以通过在代码中设置的值来识别，还可以借助ida分析固件的其余部分。

![](https://image.3001.net/images/20190910/1568104426_5d775feaa8b98.png!small)

## 密码加密分析

我们可以找到单词“password”的函数引用或找到任何类似加密的函数调用，重点放在blowfish或des加密上。在调用参数之前跟踪加载到参数中的值，对于arm，这些值将在寄存器r0、r1、r2等中设置。

![](https://image.3001.net/images/20190910/1568104565_5d776075d02c6.png!small)

在“clieditpasswordset”函数中标识了blowfish函数调用，证明使用了可逆加密。blowfish测试函数是使用特定的常数来识别的，这些常数可以在网上搜索到，这样就可以识别所使用的确切blowfish库，该库可以从github下载。

![](https://image.3001.net/images/20190910/1568104638_5d7760be3540f.png!small)

可以通过标识传递给寄存器r1的值来跟踪用于blowfish的加密密钥。寄存器r0将包含“ctx”变量，r1将包含密钥，r2将包含密钥的长度。

分析表明，用于管理员密码的加密密钥是“els_key”，但是尝试使用此字符串解密用户密码失败。进一步分析表明，加密使用了第二个密钥，但无法静态识别。

当处理相对简单的软件时，或者有很多时间跟踪每个函数调用时，静态分析非常有用。在这种情况下，我们无法通过静态分析来识别用户密码的加密方法。

我们购买了scalance交换机，在主板上识别出jtag，将头部焊接上，并将其连接到segger j-link jtag调试器。

![](https://image.3001.net/images/20190910/1568104805_5d776165ad23b.png!small)

使用segger gdb可以添加断点并逐步遍历固件的每个元素。由此，可以通过在调用函数时检查寄存器设置来标识加密所使用的确切变量。

确定了以下密码加密方法：

> 1、管理员密码使用静态密钥“els_key”加密
>
> 2、第二个管理员密码是一个静态字符串“elsdebug”，它使用明文管理员密码进行加密，用于确保管理员密码与用户密码使用的加密相对应
>
> 3、所有其他用户密码也用明文管理员密码加密

## 解决方案

西门子对披露的信息反应迅速。西门子调查并确定，该问题影响了整个scalance交换机产品线，

> 已披露：<https://www.us-cert.gov/ics/advisories/icsa-19-162-04>
>
> 新固件发布：<https://support.industry.siemens.com/en/document/109767965/firmware-> update-version-5-2-4-for-scalance-x-200>
>
> 西门子发布了一份安全建议：<https://cert-> portal.siemens.com/productcert/pdf/ssa-646841.pdf>

 ***参考来源：[pentestpartners](https://www.pentestpartners.com/security-blog/pwning-a-siemens-scalance-ics-switch-through-arm-reversing/)，由Kriston编译，转载请注明来自FreeBuf.COM**

