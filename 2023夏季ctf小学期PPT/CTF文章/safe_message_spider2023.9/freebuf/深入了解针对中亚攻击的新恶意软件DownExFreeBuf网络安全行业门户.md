2022 年底，Bitdefender 的研究人员发现了针对哈萨克斯坦外事机构的针对性攻击。研究人员立刻对同类攻击展开监测，随后又发现了针对阿富汗的攻击。

## 攻击分析

相关域名与 IP 地址没有公开披露的记录，且样本与已知的恶意软件也不存在相似之处。分析人员认为这是一个新的恶意软件家族，并将其命名为 DownEx。

通过攻击的目标、冒充外交官的诱饵文档以及以数据窃取为主要意图，应该是国家支持的攻击组织在背后兴风作浪，但研究人员并未能对其进行归因。攻击者使用了在俄语国家非常流行的破解版
Office 2016（被称为 SPecialisST RePack 或者 Russian RePack by
SPecialiST）。另外很不寻常的是，攻击者使用两种语言编写了同一个后门，此前在 APT28 编写 Zebrocy 时发现过。

### 初始访问

研究人员预计攻击者使用社会工程学技术发送带有恶意 Payload 的鱼叉邮件，附件名为 `! to <redacted> embassy kazakh
2022.exe`。攻击者并没有使用双重扩展名，但使用 Word 文档的图标进行了伪装。

该可执行文件是一个 Loader，执行后释放两个文件到本地并执行：

  * C:\Users\\\Appdata\Local\Temp! to Embassy kazakh 2022.doc
  * C:\ProgramData\Utility\log

释放的 Word 文档只是提供伪装，使后台执行的恶意脚本不被怀疑。而 log 文件则是内嵌 VBScript 代码的无扩展名 HTA 文件。

![image.png-151.2kB](https://image.3001.net/images/20230518/1684387002_6465b4baa1b21fb68a036.png!small)释放的
Word 文档

其整体的执行流程如下所示：

![image.png-227.2kB](https://image.3001.net/images/20230518/1684387003_6465b4bb6f153bc723846.png!small)感染链

后续的 Payload 下载失败，研究人员未能获取后续恶意软件。失陷主机上的多个样本都是用来与 C&C 服务器建立连接的，后续将一一进行介绍。

### 探测发现

攻击者使用 C/C++ 编写的工具来枚举网络上的各种资源。使用放置在 C:\ProgramData\Programs 的 wnet.exe 与
utility.exe，利用 Win32 API 中网络相关的函数进行侦察。

### 命令与控制

攻击者使用 PyArmor 对 Python 开发的后门进行混淆，阻止代码被研究人员进行逆向分析。Python 脚本使用的 DLL 文件也受到
Themida 的保护，使用了包括操作码混淆在内的多种混淆技术。

通过坚持不懈的逆向分析，还是对其有所了解：

![image.png-159.9kB](https://image.3001.net/images/20230518/1684387004_6465b4bc22f8621afb33e.png!small)后门的基本流程

  1. 首先后门生成一个 2048 位的 RSA 公私钥对。
  2. 后门通过 https[:]//net-certificate[.]services:443 将公钥回传给 C&C 服务器  
a. USR_KAF：其中包含 EmailID，可以标识特定电子邮件攻击行动的硬编码值  
b. USR_PUB：为上一步中生成的公钥  
c. USR_CR：脚本文件 Chelp.py 的 SHA256 哈希值

  3. C&C 服务器回复客户端 ID，留供后续使用  
a. TSK_KEY：解密 TSK_BODY 的 AES 密钥  
b. TSK_IV：解密 TSK_BODY 的 AES 初始化向量  
c. TSK_BODY：CBC 模式下 AES 加密的 Python 代码。响应中总是会返回变量 USR_KAR，似乎是客户身份 ID

  4. 无限循环向 C&C 服务器 https[:]//net-certificate.services:443/ 发起上述请求

C&C 服务器会返回要执行的任务在失陷主机上执行，主要包含：

  * TSK_BODY 与 TSK_IV：解密 TSK_BODY 所需的 AES 密钥与初始化向量
  * TSK_LINK：代表任务的唯一 ID，似乎是全球所有受害者共用的。在野发现的最大任务 ID 是 115880，研究人员认为攻击者向受害者发送了超过十万个任务
  * TSK_BODY：加密的 Python 代码

Python 代码的形式为 `class A<number>`，监控中发现了四个类型，当然应该还有更多的类型。

  * A3，上传特定扩展名的文件  

    * 扩展名的列表是硬编码的，有 doc、docx、dot、dotx、xls、xlsx、ppt、pptx、odt、pdf、rtf、rar、jpg、jpeg、bmp、heic、tiff、tif
    * 可以只检索最近 N 天内修改过的文件
    * 会通过 16MB 的压缩文件进行数据泄露
  * A4，不仅上传文件还会将文件删除  

    * 上传并删除 C:\ProgramData\Python\Lib\LOC\F 中 .py 扩展名的文件
    * 上传并删除 C:\Users\\\AppData\Local\Diagnostics\\\1cbe6654-466b-4d53-8303-2e86ab6db8a7 中 ~tmp 扩展名的文件
  * A6，只回传匹配的文件名但不回传文件本身
  * A7，上传失陷主机的屏幕截图

受害者完成任务后，会使用以下 JSON 结构与 C&C 服务器进行通信：

  * SK_LINK：任务 ID，由 C&C 服务器指定
  * RESULT：使用 AES 加密与 base64 编码处理的任务执行结果
  * NAME_FILE：包含时间戳、任务 ID 与其他信息的数据，并且使用 AES 加密与 base64 编码处理

### 数据收集与泄露

调查过程中，可以发现多个用 C++ 编写的恶意样本。用于数据泄露的可执行文件 diagsvc.exe 存储在
C:\ProgramData\Programs。

![image.png-201.6kB](https://image.3001.net/images/20230518/1684387004_6465b4bcdd7989427b42c.png!small)建立
C&C 连接的方式

其中一个样本中包含 PDB 路径（C:\Projects\DOWN\Release\DOWN.pdb），因此将该恶意软件家族命名为 DownEx。

样本间存在细微的差异，一些样本有许多调试字符串，有些样本则经过简单的异或加密。也有样本文件并不直接回传数据给 C&C 服务器，而是利用另一个
VBScript 脚本（C:\ProgramData\Temp\driver.vbs）将数据回传到相同的 C&C 服务器（84.32.188.123）。

执行后，DownEx 就会开始递归解析本地驱动器与网络驱动器，收集以下扩展名的文件：

  * .doc、.docx、.rtf、.xlsx、.xls、.pdf、.ppt、.pptx、.~tm、.bmp、.rar、.jpg、.odt、.p12、.heic、.enc、.jpeg、.tiff、.tif、.zip、.crf、.enc、.cr、.lhz、.pem、.pgp、.sbx、.tlg

相关的文件会通过加密的 ZIP 压缩文件进行回传，每个 ZIP 压缩文件的大小为 30MB。恶意软件通过
http[:]//84.32.188[.]123/hftqlbgtg.php 回传到 C&C 服务器。

![image.png-903kB](https://image.3001.net/images/20230518/1684387005_6465b4bdbf416b2ed05d5.png!small)VBS
脚本下载另一个脚本

调查过程中，研究人员发现了基于 VBScript 脚本开发的 DownEx 样本文件。其功能与 C++ 版本的 DownEx
相同，且是一种无文件攻击。DownEx 会在内存中执行，而不会存在落地的文件。VBScript 版本的 DownEx 通过 slmgr.vbe 使用自定义的
User Agent 发送给 http[:]//206.166.251[.]216/www.php 进行回传。

## 总结

DownEx 恶意软件家族显示了现代网络攻击的复杂性，攻击者会不断寻找新的方法巩固攻击。为了阻止攻击，各种技术构建的纵深防御可以确实地帮助检测与预防攻击。

## IOC

> 139.99.126[.]38  
> 84.32.188[.]123  
> 206.166.251[.]216  
> net-certificate[.]services  
> 1e46ef362b39663ce8d1e14c49899f0e  
> bb7cf346c7db1c518b1a63c83e30c602  
> a45106470f946ea6798f7d42878cff51  
> 3ac42f25df0b600d6fc9eac73f011261  
> 14a8aad94b915831fc1d3a8e7e00a5df  
> 457eca2f6d11dd04ccce7308c1c327b7  
> d310a9f28893857a0dc1f7c9b624d353  
> d20e4fffbac3f46340b61ab8f7d578b1  
> 5602da1f5b034c9d2d6105cdc471852b  
> 89f15568bc19cc38caa8fd7efca977af  
> ae5d4b9c1038f6840b563c868692f2aa  
> c273cdfcfd808efa49ec0ed4f1c976e0  
> d11fcd39a30a23176337847e54d7268c  
> 70e4305af8b00d04d95fba1f9ade222d  
> 1492b0079b04eb850279114b4361f10c

## 参考来源

> [BitDefender](https://www.bitdefender.com.au/blog/businessinsights/deep-> dive-into-downex-espionage-operation-in-central-asia/)

