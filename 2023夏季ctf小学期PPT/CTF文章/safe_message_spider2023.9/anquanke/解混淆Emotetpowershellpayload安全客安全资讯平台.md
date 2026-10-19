# 解混淆Emotet powershell payload

阅读量 **270700**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-08-02 15:00:19

 **x**

##### 译文声明

本文是翻译文章，文章来源：malfind.com

原文地址：<https://malfind.com/index.php/2018/07/23/deobfuscating-emotets-powershell-payload/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t01f7bd0b8170db7647.jpg)

Emotet是2014年发现的一种银行木马，之后研究人员发现了大量的Emotet垃圾邮件活动，使用多种钓鱼方法诱使用户下载和加载恶意payload，主要使用恶意Word文档传播。

![](https://p3.ssl.qhimg.com/t013d1d051141872b0c.png)

图1 Emotet感染链

用户在收到钓鱼邮件时，点击邮件中的链接后，就会下载恶意Word文档。然后恶意文档会诱使用户启用内容和宏来加载嵌入的VBA代码。但是VBA代码是混淆过的，最后会加载一个powershell命令。下面讲述使用沙盒和powershell审计技术在不解混淆的情况下获取VBA代码加载的powershell命令。

![](https://p1.ssl.qhimg.com/t0162885a98725e5719.png)

## 混淆方法

Powershell代码本身也是经过混淆的，在虚拟环境下加载的问题就是我们可能看不到任何网络IoC。最好的办法就是将代码解混淆，这样才能更好地理解它。

混淆是一种使恶意代码不便于阅读的方法，有两个作用：一是欺骗杀毒软件，二是使对恶意代码的分析更耗时间也更困难。

下面介绍2017年12月起Emotet恶意软件使用的三种混淆方法：

###  1\. 字符串替换方法

字符串替换方法使用多个powershell的replace函数来交换无用的字符串和一些关键字，最终产生有效的powershell代码。

![](https://p1.ssl.qhimg.com/t01fe1cd46653c2a5fb.png)

图3. 用代码替换方法混淆的代码

可以通过替换字符串的方式在文本编辑器中解混淆代码，用正则表达式可以加速这一过程。最后可以通过python脚本中的正则表达式自动完成解混淆。

在python中实施解混淆时应注意：

  * 字符串连接。代码中的+会使正则表达式出错，因为需要提前处理。
  * 字符类型映射。有时候为了增强混淆的效果，字符串可能不是直接用powershell中的代码类型替换，而是用int转化为char。因此也需要提取处理。
  * 替换代码的一部分会生成新的替换。这是因为无用字符串可能是在替换器的中间，因此，最好把正则表达式加入循环中，如果还可以替换就一直替换。

![](https://p0.ssl.qhimg.com/t01d66a8a4c64815157.png)

图4 解混淆图3中代码的结果

###  2\. 字符串压缩

字符串压缩方法也很简单，使用powershell内置的DeflateStream类来解压缩和执行压缩流。

![](https://p0.ssl.qhimg.com/t011f28abcb864a5549.png)

图5 解压缩字符串混淆方法

最简单的解混淆方法是用powershell简单的解压缩字符串。

需要注意的是要手动移除前两个括号中的命令，因为这是混淆的Invoke-Expression
cmdlet（接受任何字符串输入并将它视为PowerShell代码）。在处理恶意代码时，最好使用安全的虚拟环境。

![](https://p1.ssl.qhimg.com/t01d32dbc74b1c3f680.png)

图6 powershell中使用的解压缩解混淆方法

查看MSDN文档，可以看到RFC 1951
Deflate数据格式说明中的DeflateStream类，所以可以用zlib库完成解压缩。Zlib的解压缩方法默认需要准确的zlib文件头，而DeflateStream是不需要的，因为这就变成了一个流而不是文件。为了让zlib解压缩流，可以在文件中加一个header或者简单的传递一个-zlib.MAX_WBITS参数给解压缩函数。zlib.MAX_WBITS参数如果是负值就表示解压缩函数应该跳过header位。

###  3\. ASCII代码数组

计算机用0101数字串来表示字符串，但对人类而言，字符串更易读，所以数字串要通过程序转变成字符串。恶意代码可以利用这个技巧来隐藏真正目的，这是第三种混淆方法，ASCII码数组混淆方法。

![](https://p5.ssl.qhimg.com/t01aab4f7c3132529d2.png)

图7 ASCII码数组混淆方法

在图5的例子中，我们可以看到一些含有数字的长字符串。如果熟悉ASCII码，可能就可以马上认出来。如果不熟悉的话，可以通过映射表将数字转化为int然后在转化为char。例子中的方法使用了切割函数，通过给定的分割器将字符串分割开来进行下一步的混淆。

为了在python中解混淆代码，可以使用一个简单的split方法，然后用chr()函数将字符与数字进行映射。

![](https://p2.ssl.qhimg.com/t01e0c535d8f4a8ada9.png)

图8 用split方法在python中解混淆出的ASCII码数组

## 真实代码

在解混淆出源代码后，可以看出是一个简单的释放器，用WebClient类来连接硬编码的域名，在%TEMP%目录下载二进制文件，然后加载。代码中使用break，try-catch语句来确保脚本在下载完成前能够连接到域名。

## Invoke-Expression

许多混淆powershell脚本都用Invoke-Expression cmdlet来把混淆后的字符串当作代码运行。在Windows
console中运行powershell恶意代码是有必要的，因为如果没有invoke-expression cmdlet，混淆后的恶意代码就不能运行。

因此，找出伪装的Invoke-Expression cmdlet就非常重要。首先，powershell允许为长命令使用缩写。所以Invoke-Expression的内置缩写就是iex，但powershell还允许将字符串连接并用作cmdlets，而且字符串可以保存为变量。

那么问题来了，我们可以用DeflateString压缩的例子来说明。脚本开始的一行代码是：

`$vERBOsepreFErEncE.tOStRIng()[1,3]+'X'-JoIn''`

这行代码将powershell内置变量$verbosepreference的值转化为字符串，然后在第2和第4个字符后面连接了X，之后再用join将所有的字符连接成一个字符串。

那么变量$verbosepreference的默认值是什么呢？`SilentlyContinue`第2个第4个字符分别是i和e。当连接一个x后就变成了iex，也就是Invoke-Expression cmdlet的缩写。事实上，这类技巧在powershell中应用还是很普遍的，尤其是在恶意软件开发中。

![](https://p1.ssl.qhimg.com/t0146e6f9663f47d7ec.png)

图9 Invoke-Expression混淆示例

Emotet解混淆代码脚本下载地址：<https://github.com/lasq88/deobfuscate/>

本文翻译自malfind.com
[原文链接](https://malfind.com/index.php/2018/07/23/deobfuscating-emotets-powershell-payload/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **ang010ela** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/153537](/post/id/153537)

安全客 - 有思想的安全新媒体

本文转载自: [malfind.com](https://malfind.com/index.php/2018/07/23/deobfuscating-emotets-powershell-payload/)

如若转载,请注明出处： <https://malfind.com/index.php/2018/07/23/deobfuscating-emotets-powershell-payload/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)
  * [powershell](/tag/powershell)
  * [Emotet](/tag/Emotet)
  * [代码混淆](/tag/代码混淆)

 **+1** __0赞

 __收藏

![](https://p3.ssl.qhmsg.com/dm/200_200_100/t00df551a583a87f4e9.jpg) ang010ela

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

