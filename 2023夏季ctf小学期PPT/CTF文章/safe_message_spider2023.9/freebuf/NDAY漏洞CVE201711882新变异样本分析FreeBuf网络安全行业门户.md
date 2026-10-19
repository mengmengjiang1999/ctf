## 0x0 基本情况  

最近截获一个QUOTATION.doc文档，重新命名为virus.doc，其实际为RTF文档。winword.exe进程打开后，执行EQNEDT32.EXE进程，其中exe远程下载和运行的动作由EQNEDT32.EXE进程来完成。我们知道，EQNEDT32.EXE为公式编辑器，在Office的安装过程中被默认安装。前期与之相关的漏洞主要为CVE-2017-11882和CVE-2018-08082。

与上一篇文章《一个CVE-2017-11882漏洞新变异样本的调试与分析》[
_https://www.freebuf.com/vuls/190397.html_](https://www.freebuf.com/vuls/190397.html)中的样本相比，本次样本RTF格式更加怪异，下面来看看具体的分析情况。

## 0x1 文件格式

### 1、静态文件

利用winhex查看该文件，发现其是一个rft1开始的RTF格式文件，不过该文件与之前分析的CVE-2017-11882样本相比，显得较为怪异，没有包含OLE结构。

该RTF文件格式非常简单，如下图是文档头部，中间数据则全都是16进制字符串，结尾以字符串“}\objupdate688639934}}”结尾。

![](https://image.3001.net/images/20191012/1570863677_5da17a3d9a905.png!small)

### 2、查杀情况

利用文件HASH值，在totolvirus查询，发现该样本10月9日上传，57款杀软有11款已经查杀，其中McAfee-GW-Edition、Ikarus、McAfee、AhnLab-V3、ESET-NOD32识别为CVE-2017-11882漏洞，如下图所示：

![](https://image.3001.net/images/20191012/1570863688_5da17a483ab10.png!small)

### 3、RTFOBJ工具分析

利用RTFOBJ工具分析，结果如下：

![](https://image.3001.net/images/20191012/1570863701_5da17a55ac322.png!small)

其中导出的virus.doc_object_0000006C.bin不是正常的OLE结构。

![](https://image.3001.net/images/20191012/1570863712_5da17a60b17c5.png!small)

### 0x2 文档动作

利用Procmon监控，发现winword.exe执行后，启动EQNEDT32.EXE。EQNEDT32.EXE进程远程下载PE文件并保存为本地%appdata%目录下：bobyen23534.exe。如下图所示：

![](https://image.3001.net/images/20191012/1570863737_5da17a799e7c9.png!small)

抓包发现PE下载地址为：[
_http://modexcourier.eu/bobbye/bobbye.exe_](http://modexcourier.eu/bobbye/bobbye.exe)，如下图所示：

![](https://image.3001.net/images/20191012/1570863754_5da17a8af3ce2.png!small)

bobyen23534.exe进程运行后即退出。

下载后的bobyen23534.exe根据HASH在totolvirus搜索，大部分指向的是Trojan木马文件，如下图所示：

![](https://image.3001.net/images/20191012/1570863802_5da17aba44c0c.png!small)

### 0x3 样本调试

我们知道，漏洞利用EQNEDT32.EXE进程的栈溢出漏洞，调试其溢出点，如下图所示：

![](https://image.3001.net/images/20191012/1570863837_5da17add8dcc1.png!small)

经过拷贝动作后，栈被覆盖。

![](https://image.3001.net/images/20191012/1570863851_5da17aeb3395d.png!small)

![](https://image.3001.net/images/20191012/1570863856_5da17af08b571.png!small)

我们来看这段数据在RTF中的位置，该段数据在开头0x128处，如下图所示：

![](https://image.3001.net/images/20191012/1570863869_5da17afd1994d.png!small)

这段代码是第一段shellcode，用于栈溢出后跳转。

这是典型的栈溢出利用。其中0x00433d49用于覆盖0x41160F函数返回地址，当函数0x41160F返回的时候，跳转到0x00433d49处执行，而EQNEDT32.EXE进程中，0x00433d49处所在的值是0xC3,也就是汇编代码retn。

因此，0x00433d49执行后，会返回到当前栈地址执行，也就是0018f354处的代码（第一段shellcode）。

![](https://image.3001.net/images/20191012/1570864031_5da17b9f5c42d.png!small)

第一段shellcode执行后，跳转到第二段shellcode处执行，我们来看第二段shellcode的内容。

其所在的文件中的位置是：0xA8FDE处，两者对应如下图所示：

![](https://image.3001.net/images/20191012/1570863893_5da17b15eab90.png!small)

第二段shellcode执行后，开始对其自身的内容做解密操作，如下图所示的汇编代码。

![](https://image.3001.net/images/20191012/1570863930_5da17b3a04df8.png!small)

解密的算法是：

解密前的内容如下图所示：

![](https://image.3001.net/images/20191012/1570864178_5da17c3201d57.png!small)

解密后的内容如下图所示：

![](https://image.3001.net/images/20191012/1570864185_5da17c39391c0.png!small)

该段shellcode正是下载运行的功能代码。

对比上一篇文章[
_https://www.freebuf.com/vuls/190397.html_](https://www.freebuf.com/vuls/190397.html)分析的样本，解密后的shellcode基本上是一致的，主要变化只是加解密算法中的常量值进行了更换。

上篇文章中的加解密算法为：

至此，样本基本调试分析完毕。

### 0x4 小结

> 1、CVE-2017-11882漏洞由于稳定、效果好等特点，经久不衰。
>
> 2、CVE-2017-11882漏洞变异样本层出不穷。
>
> 3、及时更新补丁，打开不明文档要谨慎小心。

 ***本文原创作者：cgf99，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

