Windows
注册表中包含有二进制块（Blob），有些二进制块用于存储证书，如下所示：![](https://image.3001.net/images/20210928/1632806812_6152a79c5bde38e94a10a.png!small)

以下的注册表位置都存储证书：

> HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\SystemCertificates
>
> HKEY_CURRENT_USER\SOFTWARE\Microsoft\SystemCertificates

证书通过 [DER](https://en.wikipedia.org/wiki/X.690#DER_encoding)格式进行编码，总是以 0x30
为开始。但可以发现，在注册表中找到的二进制块并非以 0x30 开头，这是因为证书前缀存储了一些元数据。搜索 0x30
即可找到证书的位置：![](https://image.3001.net/images/20210928/1632806818_6152a7a2f34c6e68ecc5d.png!small)

并非所有以 0x30 开头的字节序列都是有效的证书。从 0x30 8
开始搜索，提取该字节序列直到二进制块的结尾找到了该证书。![](https://image.3001.net/images/20210928/1632806820_6152a7a4aea2ff4ce0d6b.png!small)

![](https://image.3001.net/images/20210928/1632806822_6152a7a65baefad082f4f.png!small)

该方法并不精确，通过查看几个二进制块可以发现：每个证书都以 4 字节为前缀，这些字节对证书的长度进行编码（小端序），然后此长度字段以不变的 8
字节为前缀：20 00 00 00 01 00 00
00。![](https://image.3001.net/images/20210928/1632806825_6152a7a997a7dc2af28cf.png!small)

看起来像是 [TLV](https://en.wikipedia.org/wiki/Type-length-value)的格式，每个证书的类型都是 20
00 00 00 01 00 00 00。工具 [format-bytes.py](https://blog.didierstevens.com/2019/07/16/update-format-bytes-py-version-0-0-9/)是解析二进制数据的工具，可用于解析 TLV
记录，如下所示：![](https://image.3001.net/images/20210928/1632806827_6152a7ab38ac788fb7d13.png!small)

`<QI`中 `<`表示小端序，`Q`表示 unsigned long long（8 字节），`I`表示 unsigned
int（4字节）。`t:0`意味着类型字段是第一个字段。`l:1`意味着长度字段是第二个字段。

可以看出，该二进制块包含 11 个 TLV 记录，最后一个长度为 1239，并且包含证书类型 0x100000020L。

进一步的研究[表明](https://itsme.home.xs4all.nl/projects/xda/smartphone-certificates.html)，类型字段实际上由两个字段组成：属性标识符字段与保留字段，均为四个字节。属性标识符的可能值可以在 [Windows
开发中心](https://docs.microsoft.com/en-us/windows/win32/api/wincrypt/nf-wincrypt-certgetcertificatecontextproperty)和 wincrypt.h 头文件中找到。

这意味着二进制块内的 TLV 记录可以使用 `format-bytes.py -f “tlv=f:<III,t:0,l:2”
blob.bin`进行解析：![](https://image.3001.net/images/20210928/1632806829_6152a7ad83d97abd63d9a.png!small)

例如，记录 5 的类型为 0x0b 代表是
`CERT_FRIENDLY_NAME_PROP_ID`：![](https://image.3001.net/images/20210928/1632806834_6152a7b24220ea7585313.png!small)

如上图所示，包含 UTF16 编码的发行者名称。如下所示，证书本身位于记录 11 内（类型为
0x20）：![](https://image.3001.net/images/20210928/1632806836_6152a7b43979ac920f814.png!small)

![](https://image.3001.net/images/20210928/1632806837_6152a7b5aeeb544e75ca7.png!small)

要提取证书请使用 `-d`执行二进制 dump
并写入本地文件：![](https://image.3001.net/images/20210928/1632806839_6152a7b7afb134b3cf801.png!small)

## 结论

二进制数据块中经常出现 TLV 记录，如果想要识别二进制块中的数据，请多比较几个示例可能就会发现定义的模式。证书与元数据一起存储在注册表中，元数据结构为
TrLV 记录。证书本身存储在记录内部，类型为 0x20。

## 参考来源

> [NVISO](https://blog.nviso.eu/2019/08/28/extracting-certificates-from-the-> windows-registry/)

