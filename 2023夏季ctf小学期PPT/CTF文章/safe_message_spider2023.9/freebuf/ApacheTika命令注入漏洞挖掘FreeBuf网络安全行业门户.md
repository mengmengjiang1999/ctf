***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 介绍

 **这篇文章将从一个Apache
tika服务器的命令注入漏洞到完全利用的步骤。CVE是<https://nvd.nist.gov/vuln/detail/CVE-2018-1335>。由于Apache
Tika是开源的，我能够通过分析Apache
Tika代码来确定问题。虽然命令注入漏洞通常很简单，但要实现完整的远程代码或命令执行需要克服一些障碍。这是由于Java处理执行操作系统命令的方式以及Apache
Tika代码本身的一些特性。但在最后，我们仍然可以使用Cscript.exe来执行操作。**

## 什么是Apache Tika

> Apache
> Tika™工具包可从超过一千种不同的文件类型（如PPT，XLS和PDF）中检测和提取元数据和文本。所有这些文件类型都可以通过一个接口进行解析，使得Tika对搜索引擎索引，内容分析，翻译等非常有用。（<https://tika.apache.org/>）

Apache Tika有几个不同的组件：Java库，命令行工具和自带REST API的独立服务器（tika-server）。此攻击特别针对独立服务器，它通过REST
API公开<https://wiki.apache.org/tika/TikaJAXRS>。样本可在<https://archive.apache.org/dist/tika/tika-server-1.17.jar>找到。

## Breaking Down The CVE

我们首先需要阅读issue，看看可以从中获取哪些信息。

原始描述：

> 在Tika 1.18之前，客户端可以将精心设计的标头发送到tika-server，该标头可用于将命令注入运行tika-> server的服务器的命令行。此漏洞仅影响在对不受信任的客户端开放的服务器上运行tika-server的漏洞。

我们可以从这个描述中看到的事情：

> 1.版本1.18已修补；
>
> 2.版本1.17未修补；
>
> 3.该漏洞是命令注入；
>
> 4.漏洞的入口点是“headers”；
>
> 5.这会影响代码的tika-server部分。

有了这些信息，我们现在有了一个识别漏洞的起点。下一步将看看Tika补丁和未补丁版本的差异，特别是tika-server部分。为Java中已知的执行操作系统命令的函数编写Grepping代码是另一个不错的选择。最后，搜索tika-server代码的各个部分，我们可以假设这些报头是某种HTTP请求。

## 0x01

对tika-server 1.17与1.18源目录进行并行递归比较。只返回一个已修改的文件，如下部分。

![1.png](https://image.3001.net/images/20190517/1558071432_5cde488809ec9.png!small)

由于目标是在头字段中找到命令注入，所以第一个结果是一个代码块，这个代码块已经添加到补丁版本“ALLOWABLE_HEADER_CHARS”中。这是一个非常好的开始,假设这是补丁试图过滤可用于将命令注入头字段的字符。

继续向下是一个名为“processHeaderConfig”的函数内部的代码，它已在1.18中删除。它使用一些变量来动态创建一个方法，该方法似乎设置了某个对象的属性，并使用HTTP头来执行此操作。

![2.png](https://image.3001.net/images/20190517/1558071442_5cde489299670.png!small)

以下是此功能的说明：

![3.png](https://image.3001.net/images/20190517/1558071452_5cde489ce7207.png!small)

截图显示了不同属性的前缀，并在此代码的开头定义为静态字符串。

![4.png](https://image.3001.net/images/20190517/1558071460_5cde48a414f30.png!small)

因此，我们有一些静态字符串可以作为HTTP头文件包含在请求中，并用于设置对象的某些属性。最终header的示例看起来像“X-Tika-OCRsomeproperty：somevalue”，然后将“someproperty”转换为类似于“setSomeproperty()”的函数，并将somevalue作为要设置的值传递给该函数。

![5.png](https://image.3001.net/images/20190517/1558071467_5cde48ab1a805.png!small)

可以看到这里正在使用这个函数，并且在请求中检查了前缀头以确定如何调用该函数。然后，所有需要的参数都从HTTP请求传递到“processHeaderConfig”函数。

查看使用“processHeaderConfig”函数的方式，可以看到正在“TesseractOCRConfig”对象上设置属性。搜索可能使用我们发现的“TesseractOCRConfig”对象的地方：[tika-parsers/src/main/java/org/apache/tika/parser/ocr/TesseractOCRParser.java](https://github.com/apache/tika/blob/86e997510b44f12dc9f90a68aaf583d5d3912892/tika-parsers/src/main/java/org/apache/tika/parser/ocr/TesseractOCRParser.java)。

这是来自“TesseractOCRParser.java”的“doOCR”函数，它将配置属性从我们刚刚发现的“TesseractOCRConfig”对象直接传递到一个字符串数组中，这些字符串用于构造“ProcessBuilder”的命令，然后该过程已开始。

![6.png](https://image.3001.net/images/20190517/1558071476_5cde48b48327e.png!small)

这看起来很有希望,如果我们将所有信息放在一起，我们应该能够向服务器发出某种HTTP请求，设置一个看起来像“X-Tika-OCRTesseractPath：<some
command>”的标题。并将此命令插入cmd字符串并执行。唯一的问题是“config.getTesseractPath()”前缀为另一个我们无法控制的字符“getTesseractProg()”，最终是一个静态字符串“tesseract.exe”。为了解决这个问题，我们可以用双引号包装我们想要执行的命令，Windows将忽略引号后附加的任何内容，只执行我们的注入的命令。

为了进行测试，我们可以使用tika-server文档中的示例来检索有关文件的一些元数据。

![7.png](https://image.3001.net/images/20190517/1558071485_5cde48bd03512.png!small)

由于OCR用于从图像中提取文本和内容，我们将上传图像而不是docx，以期有望达到“doOCR”功能。

我们最终得到：

    
    
    curl -T test.tiff http://localhost:9998/meta --header "X-Tika-OCRTesseractPath: \"calc.exe\""

![8.png](https://image.3001.net/images/20190517/1558071491_5cde48c3bcca9.png!small)

在上传图像时，通过在PUT请求中将一个命令用双引号括起来作为“X-Tika-OCRTesseractPath”HTTP头的值来标识命令注入。

## 0x02 不仅仅是弹个计算器

我们直接更改正在执行的应用程序名称。由于该命令作为数组传递给Java
ProcessBuilder，因此我们实际上不能运行多个命令，也不能将参数作为单个字符串添加到命令中，否则执行将失败。这是因为将一组字符串传递给Java中的进程构建器或runtime.exec的工作方式如下：

![9.png](https://image.3001.net/images/20190517/1558071501_5cde48cd4d6d3.png!small)

通常像cmd.exe或/bin/sh这样的shell解释的字符（例如＆，<，>，|，`等）不会被ProcessBuilder解释并且将被忽略，因此您不能中断命令或添加任何将它作为单个字符串的参数。不像“X-Tika-OCRTesseractPath: \“cmd.exe /c some args\”这样简单。

回到“cmd”数组的构造，您可以看到我们也控制了命令中的多个参数，这是每个看起来像“config.get*()”的项，但是它被一些我们不控制的其他项分割开了。

![10.png](https://image.3001.net/images/20190517/1558071510_5cde48d650a45.png!small)

我的第一个想法是运行“cmd.exe”，然后将参数“/c”作为“config.getLanguage()”传入，然后将“|| somecommand
||”作为“config.getPageSegMode()”插入，这虽然可以执行“somecommand”。但是在调用｀“doOCR”｀之前，还有另一个函数在｀“config.getTesseractPath()”｀字符串上调用，该字符串只执行该命令（目的是检查是否被调用的应用程序是有效的应用程序）。这里的问题是只运行没有参数的“cmd.exe”并一直挂起，因为“cmd.exe”永远不会退出并让执行继续执行“doOCR”功能。

## 0x03 解决方案

除了运行单个命令外，我们可以更深入地了解“doOCR”函数使用[Process
Monitor](https://docs.microsoft.com/en-us/sysinternals/downloads/procmon)启动进程时会发生什么。 查看进程的属性，当tika-server启动它时，会生成以下命令行，该命令行是使用inject命令构造的。

    
    
    "calc.exe"tesseract.exe C:\Users\Test\AppData\Local\Temp\apache-tika-3299124493942985299.tmp C:\Users\Test\AppData\Local\Temp\apache-tika-7317860646082338953.tmp -l eng -psm 1 txt -c preserve_interword_spaces=0

我们控制的命令部分以红色突出显示。我们可以在命令中注入3个地方，1个命令和2个参数。另一个有趣的发现是Tika实际上创建了2个临时文件，其中一个作为第一个参数被传递。

经过一些进一步的调查后，我能够确认传递给命令的第一个临时文件是我上传的文件中的内容。这意味着我可以用一些代码或命令填充该文件并执行它。

现在我必须找到一个原生的Windows应用程序，它将忽略tika-server创建的所有随机杂散参数，并仍然执行第一个文件内容作为某种命令或代码，即使它具有“.tmp”扩展名。找到一些可以做到这一切的事情起初对我来说听起来不太可能。最后我发现了Cscript.exe，它看起来有点希望。我们来看看Cscript可以做些什么。

![11.png](https://image.3001.net/images/20190517/1558071519_5cde48dfaf2f0.png!small)

Cscript正是我们所需要的。它将第一个参数作为脚本，并允许您使用"//E:engine"标志来指定要使用的脚本引擎（可能是Jscript或VBS），因此文件扩展名无关紧要。将它放入新命令现在看起来如下所示。

    
    
    "cscript.exe"tesseract.exe C:\Users\Test\AppData\Local\Temp\apache-tika-3299124493942985299.tmp C:\Users\Test\AppData\Local\Temp\apache-tika-7317860646082338953.tmp -l //E:Jscript -psm 1 txt -c preserve_interword_spaces=0

这可以通过设置以下HTTP标头来完成：

    
    
    X-Tika-OCRTesseractPath: "cscript.exe"X-Tika-OCRLanguage: //E:Jscript

将上传的“image”文件将包含一些Jscript或VBS：

    
    
    var oShell = WScript.CreateObject("WScript.Shell");var oExec = oShell.Exec('cmd /c calc.exe');

首先，上传失败，因为它不是有效图片，无法验证图像的魔术字节。然后我发现将内容类型设置为“image/jp2”迫使Tika不检查图像中的魔术字节，但仍然通过OCR处理图像。这允许上载包含Jscript的图像。

最后，将所有这些放在一起，我们有完整的command/jscript/vbs脚本。

![12.gif](https://image.3001.net/images/20190517/1558071528_5cde48e8d21cb.gif!small)

## 结论

虽然这是一个简单的命令注入，但为了利用，还是需要尝试各种方法的。Apache不建议在不受信任的环境中运行Tika服务器或将其暴露给不受信任的用户。此错误也已修补，当前版本为1.20，因此如果您使用此服务，请确保更新。

PoC：<https://github.com/RhinoSecurityLabs/CVEs/tree/master/CVE-2018-1335>

 ***参考来源：[rhinosecuritylabs](https://rhinosecuritylabs.com/application-security/exploiting-cve-2018-1335-apache-tika/)，FB小编周大涛编译，转载请注明来自FreeBuf.COM**  

