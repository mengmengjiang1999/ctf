***本文作者：aWe18s，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

## 前言

 **最近在分析样本时，遇到了不少使用PowerShell脚本的病毒程序，这些脚本基本都是经过混淆处理过的，给分析过程带来了一些麻烦。**

**我们知道PowerShell是微软推出的一款强大的命令行脚本环境，连微（ju）软（ying）这样低调的公司都将其以“Power”冠名，足见其强大之处。但凡事都有两面性，PowerShell能够为用户管理Windows系统带来便捷，也同样可以为黑客大开方便之门，沦为黑客违法行为的工具。而PowerShell灵活的语言特性又使其能够轻易的被混淆处理，混淆过的PowerShell脚本不仅使得基于特征码的杀软很难查杀，也给病毒分析工作增加了难度。**

本文基于笔者在分析PowerShell病毒过程中的经验，总结了解密被混淆过的PowerShell脚本的一些方法。

## 0x01 PowerShell代码混淆方法

想要去混淆，首先要了解有哪些混淆的方法。在17年的黑帽大会上，有人专门对此做过[演讲](https://www.blackhat.com/docs/us-17/thursday/us-17-Bohannon-Revoke-Obfuscation-PowerShell-Obfuscation-Detection-And%20Evasion-Using-Science.pdf)。

主要包括：转义符（反引号）、简写与通配符*、脚本块、字符串处理、编码、自构造关键字替换等，这里不做详细介绍。

## 0x02 如何实现去混淆？

先看一个被混淆过的PowerShell脚本：

![被混淆过的PowerShell脚本1](https://image.3001.net/images/20180821/1534850682_5b7bf67aafc68.jpg!small)

![被混淆过的PowerShell脚本2](https://image.3001.net/images/20180821/1534850682_5b7bf67ad9872.jpg!small)

中间都是被混淆的代码，已经面目全非，所以只看头尾。可以发现混淆后其实只有一行代码，是一条`IEX`命令。查看微软对`IEX`的解释：

![微软对IEX的解释](https://image.3001.net/images/20180821/1534850795_5b7bf6eb13c04.jpg!small)

`IEX`用于将字符串作为命令执行，当去掉`IEX`后，执行后就会显示原本的字符串。

观察整段程序，其格式可以提取为：`IEX( -jOiN(‘aaa’).SplIT( 'LzX>hGp!' ) |%{ ([chaR]
([CONVErT]::TOiNT16( ([StrIng]$_),16) ))}
))`，括号中的代码其实就是对字符串`‘aaa’`进行处理，将其还原成原本要执行的代码，处理完后调用`IEX`执行。

因此我们可以类比脱壳的思想，即 **无论程序怎样加壳，最终执行后都会把原本的代码吐出来** ，PowerShell也是如此，
**无论怎样混淆，最终都会执行它原本的代码** 。

将脚本开头的`IEX`去掉，并将执行结果输出到文件1.ps1中：

![执行结果输出到文件](https://image.3001.net/images/20180821/1534851288_5b7bf8d8e40ea.jpg!small)

打开1.ps1，可以看到去混淆后的PowerShell代码：

![混淆后的PowerShell代码](https://image.3001.net/images/20180821/1534851332_5b7bf904ae507.jpg!small)

有时`IEX`不一定在开头，也可能在结尾，如下：

![不一定在开头，也可能在结尾1](https://image.3001.net/images/20180821/1534851332_5b7bf904e9395.jpg!small)

![不一定在开头，也可能在结尾2](https://image.3001.net/images/20180821/1534851333_5b7bf90504186.jpg!small)

这其实也是一行代码，其格式可以提取为：`“aaa” | Invoke-Expression`。也是将字符串当作命令执行，去混淆时只需删除结尾的`|
Invoke-Expression`即可。

有时也会有找不到`IEX`的情况，如下：

![9.jpg](https://image.3001.net/images/20180821/1534851333_5b7bf905433a1.jpg!small)

![10.jpg](https://image.3001.net/images/20180821/1534851333_5b7bf905857c6.jpg!small)

可以看到这也是一行代码，但首尾都找不到`IEX`，这种情况如何处理呢？观察这行代码，可以将其提取为：`&(“aaa”)(“bbb”)`。`&`是PowerShell的操作符，调用`&`可以将字符串或变量当作命令执行。所以这里的`&(
$psHOme[4]+$pshOme[34]+'x')`其实是一个命令。

这是什么命令呢？首先看下`$psHOme`表示什么：

![$psHOme](https://image.3001.net/images/20180821/1534851333_5b7bf9056c3e1.jpg!small)

可以看到它其实就是系统中PowerShell的路径。那么`$psHOme[4]`和`$pshOme[34]`就应该分别是这个路径字符串中的一个字符：

![PowerShell的路径](https://image.3001.net/images/20180821/1534851333_5b7bf905a75f5.jpg!small)

连起来正好是`“iex”`：

![“iex”](https://image.3001.net/images/20180821/1534851333_5b7bf905c05d1.jpg!small)

所以`&( $psHOme[4]+$pshOme[34]+'x')`其实等同于`IEX`命令，我们把它从脚本前面去掉，然后执行，可以看到去混淆后的代码：

![去混淆后的代码](https://image.3001.net/images/20180821/1534851333_5b7bf905ed832.jpg!small)

前面都能够通过去掉头尾的`IEX`实现去混淆，但有时去掉后不一定就是可读的代码，如下：

![不可读的代码1](https://image.3001.net/images/20180821/1534852367_5b7bfd0f427dd.jpg!small)

![不可读的代码2](https://image.3001.net/images/20180821/1534852367_5b7bfd0f48544.jpg!small)

去掉末尾的`| Invoke-Expression`后，解密出的代码如下，并不可读：

![解密出的代码1](https://image.3001.net/images/20180821/1534852367_5b7bfd0f6128e.jpg!small)

![解密出的代码2](https://image.3001.net/images/20180821/1534852367_5b7bfd0fd4b79.jpg!small)

观察这段代码，发现依然只有一行代码，且开头是一个`IEX`。我们继续前面的方法进行解密，经过6次解密后，在代码的头尾都找不到`IEX`了。

![进行解密1](https://image.3001.net/images/20180821/1534852367_5b7bfd0fe1e0d.jpg!small)

![进行解密2](https://image.3001.net/images/20180821/1534852367_5b7bfd0ff0dbb.jpg!small)

这时的脚本已经是可读的了。

## 0x03总结

PowerShell去混淆与程序脱壳其实是一个道理，即 **无论怎样混淆，最终都会执行它原本的代码** ，遵循这个原则就一定能将被混淆的代码解密出来。

此外，PowerShell语法多样且非常灵活，本文也仅仅是基于笔者自身经验做了一些总结，难免有偏差遗漏之处，欢迎指正补充。

 ***本文作者：aWe18s，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

