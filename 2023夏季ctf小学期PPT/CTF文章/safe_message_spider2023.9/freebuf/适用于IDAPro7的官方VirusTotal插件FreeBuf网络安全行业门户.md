![](https://image.3001.net/images/20200222/1582351973_5e50c665db3cd.png!small)

##  插件介绍

 **VirusTotal近期发布了一个针对IDA Pro v7的新型插件，该插件能够直接将[VT
Intelligence的内容搜索功能](https://support.virustotal.com/hc/en-us/articles/360001386897-Content-search-VTGrep-)直接整合进IDA之中。今天给大家介绍的插件是这个Official VirusTotal Plugin for IDA Pro
7，该插件在IDA
Pro反汇编和字符串窗口的右键菜单中添加了一个新的“VirusTotal”选项，以帮助研究人员直接在VirusTotal上搜索相关数据。该插件可以将用户选择的数据项转换为VTgrep可以解析和查询的数据类型。**

注意：如需使用内容搜索功能，你还需要访问[VT
Intelligence](https://www.virustotal.com/gui/intelligence-overview)。

###  该插件当前的Beta版本提供了以下搜索功能选项：

> 1、字节搜索：搜索所选区域中包含的字节数据。
>
> 2、字符串搜索：搜索字符串窗口中选择的字符串相同的字符串。
>
> 3、相似代码搜索：标记当前所选区域中的内存偏移量或地址，并在搜索过程中忽略这些数据。
>
> 4、相似代码搜索（严格模式）：除该选项常规模式的作用之外，它还会忽略当前所选区域中的所有常量。
>
>
> 5、相似函数搜索：与“相似代码搜索”选项类似，但是该选项无需用户选择所有属于该函数的指令，用户只需要右键点击一条指令，该模块将自动检测函数边界，并选择当前函数的所有指令。

![](https://image.3001.net/images/20200222/1582351989_5e50c6759a4ed.gif!small)

##  使用VTGrep内容搜索跟踪DTrack样本

为了演示该插件的分析过程，我们针对2019年10月份出现的[DTrack样本](https://www.virustotal.com/gui/file/bfb39f486372a509f307cde3361795a2f9f759cbeb4cac07562dcbaebc070364/detection)进行了分析。插一句题外话，DTrack这款恶意软件曾在2019年9月4日被网络犯罪分子用于攻击Kudankulam核电站（KKNPP-印度）。

实际上，这已经不是DTrack样本第一次复用之前攻击中曾使用过的代码了。如果我们搜索字符串“dkwero38oerA ^ t @＃”（VT
Intelligence查询语句为：[content:"dkwero38oerA^t@#](https://www.virustotal.com/gui/search/content%253A%2522dkwero38oerA%255Et%2540%2523%2522/files)"），我们可以直接在VirusTotal中找到79个包含该字符串的样本，而其中有一部分就是DTrack样本。

![](https://image.3001.net/images/20200222/1582352008_5e50c688d5932.gif!small)

这个字符串是压缩“C.TMP”文件的密钥，而“C.TMP”文件则包含了"C:\"中的文件和目录，其中一个zip文件对应一个连接到的设备。这里还有另一个有意思的字符串：“abcd
@
123”，这个字符串可以用来对包含了所有收集证据的zip文件进行加密。在VirusTotal数据库中，第二个字符串总共出现了[9次](https://www.virustotal.com/gui/search/content%3A%7B4343535f6162636440313233%7D/files)。

这个搜索结果可以作为我们的分析切入点，除此之外，我们还可以查看和分析Virus
Total数据库中的类似代码来辅助我们分析。如果我们选择了WinMain函数的代码，我们就可以查看到Virus Total返回的其中一个样本：

![](https://image.3001.net/images/20200222/1582352038_5e50c6a615d8c.gif!small)

当然了，我们还可以是用另一种方法来查找相关的样本。比如说，我么可以搜索相同的字符串序列，虽然生成的代码在经过编译处理之后会有变化，但字符串在代码文件中的排列顺序是相同的。通过查看当前IP地址、运行进程和开放端口等字符串相关信息，我们可以直接跳转到类似的另一个样本：

![1582352124_5e50c6fcd0e25.gif](https://image.3001.net/images/20200224/15825120727089.gif!small)

##  插件下载地址

> Official VirusTotal Plugin for IDA Pro
> 7：【[官方地址](https://github.com/VirusTotal/vt-ida-> plugin)】、【[GitHub传送门](https://github.com/VirusTotal/vt-ida-plugin)】

 *** 参考来源：[virustotal](https://blog.virustotal.com/2020/02/official-virustotal-plugin-for-ida-pro-7.html)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

