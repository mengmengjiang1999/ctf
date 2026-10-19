**最近，[TechHelpList](https://twitter.com/Techhelplistcom)将一个用于传播Hancitor恶意软件的Word文档上传到了[VirusBay](https://beta.virusbay.io/)，并概述了与之相关的站点、C2服务器以及由该文档所释放的payload。由于Hancitor通常被用于下载Pony和ZeusPanda恶意软件，因此我决定对这个文档进行分析，以了解程序流程和功能。**

## 恶意文档  

在打开恶意文档之后，我们首先会看到一张图片，告诉我们有一份新的传真电文，并且只有在单击“Enable Editing”和“Enable
Content”之后才能查看具体的内容。可恨的是，在点击了所述的按钮之后，我仍然没有能够看到传真电文的实质内容。好吧！反正我也不想看。

在我们激活了宏的几秒钟之后，Word突然退出，给人的印象是“Word似乎崩溃了”。正如你可能已经猜到的那样，Word并没有崩溃，实际上这是Hancitor恶意软件所使用的一种策略。它提取了一个经打包的可执行文件，并用一个干净版本（即不包含恶意宏）替换了恶意文档，以防止出现几个Hancitor实例同时运行的情况。

![分析一个用于传播Hancitor恶意软件的Word文档](https://image.3001.net/images/20180815/1534301936_5b7396f05f71c.png!small)

## 恶意宏

接下来，让我们来看看恶意宏，你会注意到Document_Open()子程序首先会被执行，但是还有一个Document_Close()子程序会在程序关闭时执行，它调用了子程序closee()。让我们暂时先忘掉这个最后被执行Document_Close()子程序，来看看这个首先被执行的Document_Open()子程序。

![分析一个用于传播Hancitor恶意软件的Word文档](https://image.3001.net/images/20180815/1534301976_5b739718c7545.png!small)

通过查看它，你会发现Document_Open()负责调用另外3个子程序：kfs()、sdfsdf()和Module1.killo()。接着，让我们看看每个函数的作用。

![分析一个用于传播Hancitor恶意软件的Word文档](https://image.3001.net/images/20180815/1534302001_5b7397313b7b7.png!small)

## kfs()

kfs()看上去像是垃圾代码，因为它的作用只是简单地将页面向下移动14，向右移动24，使用backspace一次，然后复制一些东西，而这并不会造成太大的影响。

![分析一个用于传播Hancitor恶意软件的Word文档](https://image.3001.net/images/20180815/1534302022_5b73974600e49.png!small)

这让我感到很困惑，因为Hancitor的开发者应该不会做一些无用功。于是，我决定对文档和宏进行了更细致的观察。我注意到，在恶意文档中有一个很小的但很显眼的小黄点。

![分析一个用于传播Hancitor恶意软件的Word文档](https://image.3001.net/images/20180815/1534302042_5b73975a72ec4.png!small)

我们可以点击它并将其放大，从而看到这样一张图片：

![分析一个用于传播Hancitor恶意软件的Word文档](https://image.3001.net/images/20180815/1534302052_5b7397640ef69.png!small)

在查看了下一个子程序sdfsdf()之后，我明白了这张图片的作用。我们在下图中可以看到，恶意宏将目录更改为了“TEMP”，并创建了一个
Scripting.FileSystemObject。Scripting.FileSystemObject会将5C.pif的内容复制到UserForm2.TextBox1.Text和6.pif，然后返回。

## sdfsdf()

sdfsdf()似乎负责提取恶意代码，因为在与文档中的.pif图标交互时，它会在%TEMP%文件夹中创建一个快捷方式文件，即使你没有单击启用宏。在关闭文档时，快捷方式文件会消失。因此，它似乎是由恶意文档所创建的临时文件。这样，sdfsdf()就能够将内容复制到另一个文件，而不是执行5C.pif。此外，将5C.pif的数据复制到UserForm2.TextBox1.Text，还会导致一个名为“6.exe”的文件在%TEMP%文件夹中被创建。实际上，6.exe
和 6.pif 是两个完全相同的文件，只是文件扩展名不同而已。

![分析一个用于传播Hancitor恶意软件的Word文档](https://image.3001.net/images/20180815/1534302080_5b739780d3ca1.png!small)

让我想想，如果.pif文件被嵌入在文档中，那么我们该如何提取它呢？又怎样才能找到这个文件的位置呢？这让我想到了名为hexedit和 CFF
Explorer的小工具。我在主机上执行了 hexedit
，看看是否可以通过检查十六进制代码找到嵌入的文件。由于.pif文件的执行方式与可执行文件相同，因此我搜索了“MZ”。果然，我能够在一个有意思的文件路径下找到嵌入的文件，可能来自攻击者的主机：

C:\Users\win7home\Desktop\5C.pif

现在，我们已经找到了这个文件，它可以被确认为一个可执行文件，我们可以使用CFF Explorer或其他十六进制查看器/转储工具来提取它。

![分析一个用于传播Hancitor恶意软件的Word文档](https://image.3001.net/images/20180815/1534302144_5b7397c013342.png!small)

只需要搜索“ MZ ”，并单击鼠标右键选择Begin Of Block，然后滚动到可执行文件的末尾（在文件信息之后），并单击鼠标右键选择End Of
Block。然后，再次单击鼠标右键并选择Copy -> Into New
File。使用这种方法，你最终得到的哈希值可能会与原始文件的哈希值有所不同，因为你比预期多复制了一个 “00”，但这似乎不会影响程序的整体执行。

![分析一个用于传播Hancitor恶意软件的Word文档.gif](https://image.3001.net/images/20180815/1534302169_5b7397d9dc2a5.gif!small)

## Module1.killo()

现在，我们已经提取到了可执行文件，以供进一步分析使用。让我们回到宏，并查看最后一个子程序Module1.killo()。简单来说，killo()负责保存Word文档的干净版本（即不包含恶意宏）。为此，它将其保存为XML格式，从而删除文件中的所有宏。最后，killo()会终止程序，让它看起来像是意外崩溃。到这里，恶意宏看起来似乎就已经执行完了，但实际上什么也没有发生。在这种情况下，你忘记了前面提到的会在程序关闭时执行的Document_Close()和closee()。

![分析一个用于传播Hancitor恶意软件的Word文档](https://image.3001.net/images/20180815/1534302195_5b7397f37bbf7.png!small)
就如前面所提到的那样，有一个Document_Close()子程序会在程序关闭时执行，它调用了子程序closee()。因此，需要重点关注的函数似乎是closee()。首先，恶意宏会使用WMI查询来查看当前正在运行的进程列表：

    
    
    SELECT * FROM Win32_Process

然后，一个for
循环被执行，遍历列表中的每个进程，记为x。对于每个进程，将进程名称与bdagent.exe和PSUAMain.exe进行比较。从名称上看，它们像是由恶意软件下载的恶意文件，以防止出现几个Hancitor实例同时运行的情况。但在我通过Google搜索之后发现，bdagent.exe与BitDefender相关联，而PSUAMain.exe与Panda
Security相关联。因此，恶意软件似乎是在检查这两个防病毒程序，并为每个程序运行不同的执行方法。如果bdagent.exe正在运行，恶意宏则将创建%TEMP%\1.hta并将句柄存储在#1中。当你看到Print＃1时，宏实际上正在将字符串写入1.hta，而不是将其显示出来。具体来讲，宏会对经编码的字符串进行Base64解码（使用DecodeBase64()），将其转换为unicode字符串，然后写入1.hta。在进行了两次之后，文件会被关闭。最后，使用
一个 WScript.Shell对象将1.hta移动到％TEMP％文件夹并以静默方式执行 ，然后宏退出。

![分析一个用于传播Hancitor恶意软件的Word文档](https://image.3001.net/images/20180815/1534302244_5b7398240fd6c.png!small)

在解码这些字符串之后，我们可以很清楚地看到Hancitor同时使用了Visual
Basic脚本和JavaScript来执行6.exe。有意思的地方在于，这个恶意软件并非直接通过执行可执行文件来执行最终的payload，而是创建了一个.hta文件，但前提是bdagent.exe正在运行。这也许是因为bdagent不会对.hta文件进行扫描？

![分析一个用于传播Hancitor恶意软件的Word文档](https://image.3001.net/images/20180815/1534302285_5b73984dc73bd.png!small)

无论原因如何，让我们先回到宏。如果进程名称与PSUAMain.exe匹配
，则另外2个字符串会被解码并用于形成shell命令，由Shell在行的开头执行。在解码之后，我得到了如下命令：

    
    
    cmd.exe /c ping localhost -n 100 &&%TEMP%\6.exe

这个ping命令似乎用于推迟6.exe的执行，使得它会在ping退出后执行。在执行cmd.exe之后，宏也会退出。

![分析一个用于传播Hancitor恶意软件的Word文档](https://image.3001.net/images/20180815/1534302309_5b739865379ab.png!small)

最后，如果没有进程名称与bdagent.exe或 PSUAMain.exe匹配，则 for
循环结束，然后执行一个Shell命令（由3个base64编码的字符串组成）。在解码之后，我得到了如下命令：

cmd.exe /c ping localhost -n 100 &&%TEMP%\6.pif

我们可以看出，如果没有找到匹配项，恶意软件则会执行6.pif，而不是 6.exe 或
1.hta。我不确定为什么会这样，但我相信它背后必然有一大堆理论，只是我还没有找到。一旦执行了最终的payload，宏的运行也就结束了，只留下6.exe 或
6.pif运行。

## 概要

l 嵌入在恶意文档中的宏被启用；

l 6.exe和6.pif在%TEMP%文件夹中被创建；

l 一个干净的文档被创建，并替换恶意文档；

l 恶意文档退出，但宏将一直运行到返回为止；

l 恶意软件会检查bdagent.exe和PSUAMain.exe是否在运行：

> 如果bdagent.exe正在运行，恶意软件将在％TEMP％文件夹中创建1.hta，然后执行该文件夹，从而导致6.exe运行；
>
> 如果PSUAMain.exe正在运行，恶意软件会执行一个shell命令，该命令首先运行ping.exe，然后运行6.exe；
>
> 如果两个进程都没有运行，恶意软件会执行一个shell命令，首先运行6.exe ，然后运行6.pif。

l 恶意word文档完全退出，只留下6.exe 或 6.pif运行。

## IoC

> 恶意Word文档（MD5）：00955c1db30ddc172086a061ab158f00
>
> 6.exe/pif（MD5）： 992f079a832820c61388f753dab1114d

**参考来源：[0ffset](https://0ffset.wordpress.com/2018/08/12/post-0x16-hancitor-stage-1/)，Hydralab 编译，转载请注明来自 FreeBuf.COM**  

