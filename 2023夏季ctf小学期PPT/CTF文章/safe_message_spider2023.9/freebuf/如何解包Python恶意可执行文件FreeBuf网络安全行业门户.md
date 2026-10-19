使用 Python 编写的程序通常以源码的形式发布，也可以将所有依赖都打包到一个可执行文件中。那么如何解包 Python 恶意可执行文件呢？

## 打包

打包与加壳不同，打包 Python 程序的目的是创建一个可以在操作系统上独立运行的可执行文件。使用例如 PyInstaller
这类打包工具时，会执行以下操作：

> 将所有.py 源文件编译为 python 字节码文件（.pyc文件）
>
> 整合所有 python 编译的源代码和 python 依赖，包括依赖于操作系统的 python 解释器（Linux 上的
> libpython3.9.so.1.0 或 Windows 上的 python37.dll）
>
> 将所有资源都打包在一起，执行时将这些资源都解压到内存中，然后使用解释器解释执行原始 python 代码

以 Windows 平台为例，将示例代码使用 PyInstaller 进行打包：

![image.png-21kB](https://image.3001.net/images/20220509/1652080933_6278c12501e61ae84da8e.png!small)示例代码

直接运行脚本文件是很容易的：

![image.png-34.8kB](https://image.3001.net/images/20220509/1652080933_6278c1254f28d5b3a3e4c.png!small)运行情况

打包如下所示：

![image.png-176.8kB](https://image.3001.net/images/20220509/1652080933_6278c125af4de77add726.png!small)打包情况

打包得到的 `evil_program.exe`可以直接运行，可得到与脚本相同的运行结果。此时，程序可以移动到另一个完全没有 Python
环境的机器上一样可以执行。

![image.png-23.7kB](https://image.3001.net/images/20220509/1652080934_6278c1264433e9f5d09fb.png!small)运行情况

## 在 Windows 上解包 Python<3.9

如果样本中可以看到很多以 py 开头的字符串，基本可以断定是一个打包的 Python 程序。

![image.png-76.9kB](https://image.3001.net/images/20220509/1652080934_6278c1268cfab636c7115.png!small)字符串

对于 PyInstaller 来说，还有独特字符串 MEIPASS。

监控运行程序时在临时文件夹中创建了哪些文件，就能够知道使用的 Python 版本。例如 python38.dll 意味着使用的是 Python 3.8
版本。

![image.png-230.5kB](https://image.3001.net/images/20220509/1652080934_6278c126f3f9e00b97f98.png!small)监控文件系统

想要恢复源代码，必须要保证：

> 解压得到所有文件，特别是编译后的字节码文件（.pyc）
>
> 反编译感兴趣的 .pyc 文件

解压可以使用 [pyinstxtractor](https://github.com/extremecoders-re/pyinstxtractor)，使用相同版本的 Python 即可解压得到文件：

![image.png-68.2kB](https://image.3001.net/images/20220509/1652080935_6278c127a5f5dd9ca10ee.png!small)解压文件

pyinstxtractor 还额外提供了哪些是 Python 程序文件的信息，尽管存在误报但是也有很大的帮助。可以看到主文件是
evil_program.pyc：

![image.png-80.2kB](https://image.3001.net/images/20220509/1652080936_6278c1281a72789d8bc7d.png!small)提取文件

接着使用 [uncompyle6](https://github.com/rocky/python-uncompyle6)进行反编译，值得注意的是
uncompyle6 只支持到 Python 3.8。

![image.png-39kB](https://image.3001.net/images/20220509/1652080936_6278c1288327036fe351c.png!small)反编译

## 在 Linux 上解包 Python>=3.9

再次使用 pyinstxtractor 解压样本文件。由于样本是 64 位 ELF 文件，不能直接使用 pyinstxtractor 需要将文件的
pydata 转存到一个单独的文件再执行 pyinstxtractor。

![image.png-50.7kB](https://image.3001.net/images/20220509/1652080936_6278c128c92b6a407c8a3.png!small)转存文件

解包成功如下所示，也需要配合相应的 Python 版本：

![image.png-69.5kB](https://image.3001.net/images/20220509/1652080937_6278c1294b298fd8def52.png!small)解压文件

解压后的数据中有一个 RansomWare.pyc，就是需要关注的内容。由于使用 Python 3.9，需要
[Decompyle++](https://github.com/zrax/pycdc)进行反编译。该工具美中不足的就是没有文档讲解如何进行构建，如下所示：

![image.png-154.8kB](https://image.3001.net/images/20220509/1652080937_6278c129bbb8ad94606e7.png!small)构建反编译工具

如果想要从任何地方调用 pycdc 命令，也可以运行 sudo make install。

pycdc 是反编译命令，使用它来恢复 RansomWare.pyc 的源代码：

![image.png-52.2kB](https://image.3001.net/images/20220509/1652080938_6278c12a409a8601b09a7.png!small)反编译

当然，某些情况下也会遇到反编译失败的问题。但大部分代码还是可以正常进行反编译的：

![image.png-29.9kB](https://image.3001.net/images/20220509/1652080938_6278c12aa68e6f4d540d3.png!small)反编译失败

反编译失败时，可以使用 pycdas 命令来恢复“反汇编”的字节码。

![image.png-135.3kB](https://image.3001.net/images/20220509/1652080939_6278c12b074ec5b9290ab.png!small)write_key()
函数的字节码反汇编

## 结论

本文介绍了如何解压和反编译使用 PyInstaller 打包的 Python 程序，在应对使用 Python
编写的恶意软件时可以在源码级进行分析，可以大大提高效率。

## IOC

>
> hxxps://images[.]idgesg[.]net/images/article/2018/02/ransomware_hacking_thinkstock_903183876-100749983-large[.]jpg  
> lynrx_at_protonmail[.]com

## 参考来源

> [Fortinet](https://www.fortinet.com/blog/threat-research/unpacking-python-> executables-windows-linux)

