## **漏洞概述**

福建福昕软件开发股份有限公司是一家国际化运营的PDF电子文档解决方案提供厂商，提供文档的生成、转换、显示、编辑、搜索、打印、存储、签章、表单、保护、安全分发管理等涵盖文档生命周期的产品技术与解决方案。其下产品Foxit
PDF Reader和Foxit PDF
Editor的javascript函数exportXFAData，只验证了cPath参数中文件夹路径是否存在，未校验文件后缀的合法性，导致可以将交互式表单(XML
Forms
Architecture，简称XFA)数据导出为任意后缀的文件。XFA数据中可以包含javascript代码，将其导出为后缀为hta的文件，写入Windows
Startup 文件夹，该文件可以在计算机重启后自动运行，实现任意代码执行。

##  **影响范围**

  * Foxit PDF Reader <= 12.1.1.15289

  * Foxit PDF Editor 12.x <= 12.1.1.15289

  * Foxit PDF Editor 11.x <= 11.2.5.53785

  * Foxit PDF Editor <= 10.1.11.37866

##  **复现环境**

  * 操作系统：Win7 sp1 32位操作系统

  * 分析工具：IDA、OD、Procexp、PdfStreamDumper

##  **PDF文件格式**

便携式文档格式（英语：Portable Document
Format，缩写：PDF）是一种用独立于应用程序、硬件、操作系统的方式呈现文档的文件格式，最早由Adobe公司开发。每个PDF文件包含固定布局的平面文档的完整描述，包括文本、字形、图形及其他需要显示的信息。PDF文件除平面的文本和图形外，还可能包括逻辑结构元素，注释、表单、图层、富媒体（包括视频内容）之类的交互元素，使用U3D或PRC的三维对象，以及多种其他数据内容。PDF规范还提供了启用这些功能时所需的加密功能、数字签名、文档附件和元数据等。

PDF文件整体上可分为文件头（Header）、对象集合（Body）、交叉引用表（Xref table）、文件尾（Trailer）四个部分，如下图所示：

![](https://image.3001.net/images/20230614/1686711414_64892c7671e2ab32aa2f5.png!small)

其中Body是PDF文件的核心部分，文件中用到的所有对象，包括文本、图象、音乐、视频、字体、超连接、加密信息、文档结构信息等等，都在这里定义。一个对象的基本格式，如下图所示：

![](https://image.3001.net/images/20230614/1686711423_64892c7f374350b5895c2.png!small)

一个对象的定义包含4个部分：

  * 对象序号

  * 对象生成号

  * 对象定义范围

  * 对象内容

最前面的数字1是对象序号，用来唯一标记一个对象；0是生成号，按照PDF规范，如果一个PDF文件被修改，那这个数字是累加的，它和对象序号一起标记是原始对象还是修改后的对象；obj和end
obj是对象的定义范围，相当于定义了对象的开始和结束的位置；obj和end
obj中间的部分是PDF规定的任意合法对象，主要包括booleam，numeric，string，name，array，dictionary，stream等，感兴趣的读者可自行了解其详细内容。

为了增强PDF文档的交互性和动态性，PDF还支持JavaScript。PDF中的JavaScript与Web中的JavaScript有所不同，功能受到各种安全限制和约束。通过JavaScript，可以在PDF文件中处理事件，例如单击、双击、鼠标进入或离开、文本输入等，还可以用于处理PDF表单中的数据校验、格式化、提交和重置等功能，也可以实现PDF中的动态效果，例如隐藏、显示和移动元素，更改文本内容等。比如在文档即将关闭的时候，弹出提示对话的javascript的代码为：app.alert("javascript示例：文档即将关闭，是否已保存所有修改？")，如下图所示：

![](https://image.3001.net/images/20230614/1686711513_64892cd90e20f6bb51bc5.png!small)![](https://image.3001.net/images/20230614/1686711519_64892cdfe92a27b05387d.png!small)

##  **漏洞复现**

复现使用的版本为Foxit PDF Editor Pro 12.1.1.15289。默认安装后主程序路径为C:\Program Files\Foxit
Software\Foxit PDF Editor\FoxitPDFEditor.exe。

在https://github.com/webraybtl/CVE-2023-27363上下载已公开的POC文件CVE-2023-27363.pdf，漏洞利用成功后，弹出JavaScript控制台对话框，同时在Startup目录释放了evil.hta文件，如下图所示：

![](https://image.3001.net/images/20230614/1686711553_64892d0145b0804cd6204.png!small)![](https://image.3001.net/images/20230614/1686711560_64892d080a78cb690f24f.png!small)evil.hta将在计算机重启后自动执行，HTA是HTML
Application的缩写，将由本地的应用程序mshta.exe加载执行。evil.hta中包含了一段javascript脚本，如下图所示：

![](https://image.3001.net/images/20230614/1686711581_64892d1d6b39639af204d.png!small)

evil.hta运行后，启动了notepad.exe和calc.exe程序，如下图所示：

![](https://image.3001.net/images/20230614/1686711596_64892d2cd9fc5897e5505.png!small)  
![](https://image.3001.net/images/20230614/1686711603_64892d334407efc6aa0f6.png!small)

##  **漏洞分析**

使用文本编辑器winhex打开CVE-2023-27363.pdf，搜索关键字“[+] CVE-2023-27363
PoC”，但是并未搜索到。仔细分析后发现，该pdf中有很多被压缩的流（stream）对象，无法看到明文数据，如下图所示：

![](https://image.3001.net/images/20230614/1686711626_64892d4a86414ca092db5.png!small)

为方便分析，使用PdfStreamDumper工具打开CVE-2023-27363.pdf，该工具可以自动解压数据流，提取对象，javascript代码等，方便分析。该工具识别到了38个对象，再次搜索关键字“[+]
CVE-2023-27363 PoC”，结果显示在编号为3的对象中找到了该字符串，如下图所示：

![](https://image.3001.net/images/20230614/1686711652_64892d64d9e367ee0bd32.png!small)

可以清楚的看到，3号对象中包含了javascript代码，其功能是显示javascript控制台，然后向控制台输出“[+] CVE-2023-27363
PoC”字符串，再调用setTimeOut函数，该函数是延时500毫秒，执行另一段代码，最后再向控制台输出“[+] HTA payload written
in the startup.”字符串。

在延时执行的另一段代码中，调用exportXFAData函数，其中传递的cPath参数，正是恶意文件释放路径，该函数是漏洞触发和利用的关键函数。根据Adobe
Acrobat JavaScript Scripting Reference帮助文档，exportXFAData主要的功能是导出交互式表单(XML
Forms Architecture，简称XFA)数据为XDP文件，其中cPath参数为导出文件的绝对路径，如下图所示：

![](https://image.3001.net/images/20230614/1686711661_64892d6d635160e0b0a2e.png!small)

Adobe Acrobat在实现该函数时只允许导出后缀为“.xdp”和“.xml”的文件，但Foxit
PDF在实现exportXFAData函数功能时，只验证了文件夹路径是否存在，未校验cPath参数中文件后缀的合法性，导致可以将XFA数据导出为任意后缀的文件，XFA数据中又包含了可执行的javascript代码，将其导出为后缀为hta的文件，从而实现任意代码执行。验证文件夹路径是否存在的代码，如下图所示：

![](https://image.3001.net/images/20230614/1686711668_64892d74b23bf7b830d6a.png!small)

##  **参考链接**

  * <https://github.com/webraybtl/CVE-2023-2736>

  * <https://github.com/j00sean/SecBugs/tree/main/CVEs/CVE-2023-27363>

  * <https://www.foxit.com/support/security-bulletins.html>

  * <https://github.com/zxyle/PDF-Explained/blob/master/resources/pdf_reference_1.7.pdf>

[原文链接](https://mp.weixin.qq.com/s?__biz=MzkzNjMxNDM0Mg==&mid=2247485995&idx=1&sn=c54f89fd0bce983a2bb1cf98954dccfc&chksm=c2a1dea2f5d657b483da80f5840b1a144a96fc712cb4f9f41976c503e511a25493610d9fcfc2&token=21105299&lang=zh_CN#rd)

