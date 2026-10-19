使用 LokiBot
的一个在野[样本](https://app.any.run/tasks/db864efd-35b3-4e91-9e84-c6149dbfd4d7)进行分析。

## OLEDUMP

使用 oledump 工具可以看到 `EncryptedPackage`内有很多数据：

![](https://image.3001.net/images/20210929/1632896911_6154078f86d287bdc2116.png!small)

在这种情况下，一般意味着工作簿中一个或多个 Sheet 被加密锁定保护。

![](https://image.3001.net/images/20210929/1632896914_615407927284b97c7ebd2.png!small)

可以使用 [msoffcrypto-crack.py](https://blog.didierstevens.com/2018/12/31/new-tool-msoffcrypto-crack-py/)处理该文档：

![](https://image.3001.net/images/20210929/1632896919_6154079755aac438709ff.png!small)

我们可以使用 msoffcrypto-crack.py 破解密码并新建一个没有密码保护的同名文件：

![](https://image.3001.net/images/20210929/1632896920_61540798c88f9336b2f32.png!small)

也可以直接提取内容通过管道传递给 oledump.py。但在其中并未发现宏代码，而是发现了 `eQUaTiON naTIvE`:

![](https://image.3001.net/images/20210929/1632896922_6154079a65f1149d26f05.png!small)

将对象的 `eQUaTiON naTIvE`部分转存到另一个文件中，以便可以对其进行处理：

![](https://image.3001.net/images/20210929/1632896925_6154079d349e03ceeebe5.png!small)

可以使用
[XORSearch.exe](https://blog.didierstevens.com/programs/xorsearch/)在二进制文件中搜索
32 位 Shellcode 各种签名。可以看到在两处匹配到了 GetIP：

![](https://image.3001.net/images/20210929/1632896927_6154079fa08076ccd6b02.png!small)

## scDbg.exe

接着使用 Shellcode 模拟器 scDbg.exe 加载转存的二进制文件，并填入偏移位置以查看是否出现某种解码的 Shellcode：

![](https://image.3001.net/images/20210929/1632896930_615407a26974cf8bc10c9.png!small)

深入查看转存的 oledump.unpack 文件的 402438 处，如下所示。使用工具 [cut-bytes.py](https://blog.didierstevens.com/2015/10/14/cut-bytes-py/)查看
oledump.unpack 可以发现字符串如
`LoadLibraryW`、`ExpandEnvironmentStringsW`、`APPDATA\vbc.exe`、`http://frndgreen`等：

![](https://image.3001.net/images/20210929/1632896932_615407a4f19d824e5350f.png!small)

再次使用 scDbg.exe 剪切必要的部分：

![](https://image.3001.net/images/20210929/1632896935_615407a71c6faec55f5dd.png!small)

使用 scDbg.exe 直接处理 oledump-cut.unpack 会遇到问题，除了 ExpandEnvironmentStringsW
什么都发现不了：

![](https://image.3001.net/images/20210929/1632896936_615407a86e8b3b4c81dd7.png!small)

[文章](https://isc.sans.edu/forums/diary/VelvetSweatshop+Maldocs+Shellcode+Analysis/24776/)阐述了如何处理该问题。事实证明，scDbg.exe
不会 Hook 函数 `ExpandEnvironmentStringsW`，但是会 Hook 函数
`ExpandEnvironmentStringsA`。可以尝试使用 `ExpandEnvironmentStringsA`代替
`ExpandEnvironmentStringsW`，在保存更改后再使用 scDbg.exe 运行：

![](https://image.3001.net/images/20210929/1632896939_615407ab20527944ba1ee.png!small)

另一个选择是直接通过命令行覆写该字符。通过查看上面的十六进制，可以发现需要修改的位置在 0x77 处，可以用如下方式将其添加到 scDbg.exe 的起始点

![](https://image.3001.net/images/20210929/1632896940_615407acdac251382c81e.png!small)

这样我们就得到了很清晰的 ShellCode 内容。

## 参考来源

>
> [ClickAllTheThings](https://clickallthethings.wordpress.com/2020/03/31/lokibot-> getting-equation-editor-shellcode/)

