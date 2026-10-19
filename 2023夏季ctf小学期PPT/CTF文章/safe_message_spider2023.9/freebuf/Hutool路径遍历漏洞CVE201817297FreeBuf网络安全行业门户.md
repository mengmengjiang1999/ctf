![](https://image.3001.net/images/20230728/1690528147_64c36993aa7fa2076ba97.gif!small)

**0x01 概述**

Hutool 是一个 **Java工具库** ，提供了丰富的工具和方法，方便开发者在Java应用程序中进行各种常见任务的处理。它具有
**简单易用、功能丰富、性能优越** 等特点，被广泛用于Java开发中。

笔者通过对数百个真实项目引入组件的分析选出了Hutool组件的常见漏洞进行分析。本次分析的是 **CVE-2018-17297** ，Hutool-core执行unzip操作时的路径遍历漏洞。

 **0x02 组件使用场景**

Hutool-core组件包括Bean操作、日期、各种Util等，其中的ZipUtil类在压缩文件，解压文件等操作会被使用。

 **0x03 漏洞信息**

 **3.1 漏洞简介**

 **漏洞名称：** 路径遍历漏洞

 **漏洞编号：** CVE-2018-17297

 **漏洞类型：** CWE-22 路径遍历

 **CVSS评分：** CVSS v3.1：7.5

 **漏洞危害等级：** 高危

 **3.2 漏洞概述**

该库的ZipUtil类的unzip函数默认不检测压缩文件内的文件名，因此解压压缩文件的时候 **可能造成目录穿越** 。

 **3.3 漏洞利用条件**

使用Hutool默认的unzip函数，并且未对压缩文件内的文件数据进行校验会导致该漏洞。

 **3.4 影响版本**

Hutool < 4.1.12

 **3.5 漏洞分析**

该漏洞是一个标准的Zip Slip漏洞。这类漏洞在多个语言生态中存在，包括JavaScript，Ruby，.NET，Go等。

![](https://image.3001.net/images/20230728/1690528181_64c369b527a1ee64def10.png!small)

该漏洞在权限设置不当的情况下可以实现任意文件覆盖的效果，覆盖一些敏感文件如/etc/passwd或ssh连接私钥，这样可能导致服务器被远程控制，并且在特定的情况下也可能造成远程命令执行。具体如下：

  1. 攻击者上传恶意的压缩文件；

  2. 解压文件的代码存在Zip Slip漏洞；

  3. 压缩文件内的可执行文件覆盖了上级目录的可执行文件；

  4. 攻击者可远程调用文件或等待系统调用它们；

  5. 恶意文件被执行。

该漏洞产生的原因在于其unzip函数在ZipUtil.class:203行时，outItemFile = new File(outFile,
zipEntry.getName());创建的对象是直接从zipEntry获取压缩文件的FileName并创建File对象，未对得到的FileName进行过滤。

![](https://image.3001.net/images/20230728/1690528190_64c369bede1d95bbe0de5.png!small)

 **3.6 漏洞复现**

 **1.构造恶意的Zip文件**

Windows下对文件进行重命名../会提示不可包含/字符，所以使用Python脚本来制作恶意的压缩文件。

![](https://image.3001.net/images/20230728/1690528203_64c369cb93f02e04914eb.png!small)

该代码会在压缩文件内压入两个文件其文件名分别为../../../../etc/passwd，../index.html。

![](https://image.3001.net/images/20230728/1690528211_64c369d3339ed5173ffe7.png!small)

 **2.使用hutool组件的unzip函数对压缩文件进行解压。**

![](https://image.3001.net/images/20230728/1690528218_64c369da720c9ff5aa633.png!small)

 **3.查看结果**

发现之前/etc/passwd，与/var/www/html/index.html，已被覆盖。

![](https://image.3001.net/images/20230728/1690528226_64c369e2f0c5d05f2c4ef.png!small)

![](https://image.3001.net/images/20230728/1690528235_64c369ebb98fbbc3fcb68.png!small)

 **3.7 漏洞修复**

漏洞修复的办法有如下几种：

 **1.升级Hutool至4.1.12版本**

其修复原理是使用新增的FileUtil替代原先的File对象。

![](https://image.3001.net/images/20230728/1690528243_64c369f315a1aa462ebbf.png!small)

创建File对象的时候会调用checkSlip函数，该函数会通过获取传入文件的规范路径来消除路径的冗余和符号链接，然后检查file的规范路径是否以parentFile的规范路径开头，如果不是，则说明file不在parentFile目录下，将抛出异常；如果在，则返回file本身。这是一种安全性检查，以确保文件在指定的父目录下，防止越界访问。

![](https://image.3001.net/images/20230728/1690528251_64c369fbe2098d97d125a.png!small)

该修复方案可通过修改包管理文件（pom.xml，build.gradle），随后重新构建项目完成。

 **2.手动修改源码**

第一种修复方案的本质是代码的Patch，对解压文件内的文件名进行了校验，所以也可以通过自己实现相关校验代码避免漏洞的产生。

Example Vulnerable Code:

![](https://image.3001.net/images/20230728/1690528258_64c36a02ea97d1e623e81.png!small)

Example Valid Code:

![](https://image.3001.net/images/20230728/1690528265_64c36a0912c8786219aa2.png!small)

该修复方案可通过下载组件源码，手动Patch实现修复，不整体升级组件可保证项目的其余部分不受影响。

 **3.权限控制**

该修复方案可以以一个较低权限的用户进行解压操作，限制其对敏感目录和敏感文件的访问权限，从而放置Zip Slid攻击的利用。

