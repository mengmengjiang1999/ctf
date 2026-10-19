**最近，卡巴斯基研究团队发现了谷歌Chrome浏览器的一个新的未知漏洞，并立即向谷歌Chrome安全团队报告了这一情况。谷歌确认存在零日漏洞，并分配编号CVE-2019-13720。谷歌发布了Chrome版本78.0.3904.87，建议所有Chrome用户尽快更新到最新版本！详见谷歌[公告](https://chromereleases.googleblog.com/2019/10/stable-channel-update-for-desktop_31.html)，具体漏洞细节如下。**

##  技术细节

该攻击利用韩语新闻门户网站进行水坑式注入。在主页面中插入了恶意的JavaScript代码，该代码从远程站点加载脚本。

![](https://image.3001.net/images/20191104/1572830839_5dbf7e776edf2.png!small)主页存在一个javascript脚本，并从从hxxp://code.jquery.cdn.behindcona[.]com/加载了一个远程脚本。

然后，脚本加载另一个名为.charlie.xxxxxxx.js的脚本，通过与浏览器的用户代理进行比较来检查受害者的系统是否可能受到感染，该用户代理在64位版本的windows上运行；它还尝试获取浏览器的名称和版本。该漏洞试图利用Google
Chrome浏览器中的漏洞，脚本还会检查浏览器版本是否大于或等于65（当前Chrome版本为78）：![](https://image.3001.net/images/20191104/1572831007_5dbf7f1fbca88.png!small)如果浏览器版本确认符合要求，脚本将开始向攻击者控制的服务器（behindcona[.]com）执行多个ajax请求，并向服务器中php脚本传递参数。

第一个请求是获取重要信息以供进一步分析。此信息包括几个十六进制编码的字符串，这些字符串告诉脚本应该从服务器下载多少个漏洞利用代码块，以及一个指向图像文件的URL，该图像文件嵌入了最终有效负载的密钥和rc4密钥，以解密这些漏洞利用代码块。

![](https://image.3001.net/images/20191104/1572831193_5dbf7fd9a0c8e.png!small)在下载所有块之后，rc4脚本解密并将所有代码块连接在一起，形成一个新的javascript代码，其中包含完整的浏览器攻击手段。

![](https://image.3001.net/images/20191104/1572831295_5dbf803f5a346.png!small)

浏览器利用脚本被混淆，在消除混淆之后，观察到一些特殊的情况：

1、脚本中另一个检查是针对用户代理的字符串，它检查浏览器版本是76还是77，漏洞的作者可能只对这些版本进行了调试（以前的利用漏洞阶段检查过版本号为65或更高版本），或者其他曾用于较旧Chrome版本的漏洞利用方法。

![](https://image.3001.net/images/20191104/1572831486_5dbf80fe5bd4b.png!small)2、有几个函数在浏览器的内置bigint类上进行操作，这对于在64位系统中执行javascript代码非常有用。通常，漏洞利用开发人员通过32位系统来实现自己的功能。

![](https://image.3001.net/images/20191104/1572831714_5dbf81e23e42d.png!small)

3、有许多函数和变量没有在实际代码中使用，它们用于代码调试，在代码编译生成时被留下。

4、大多数代码使用与浏览器中某个易受攻击组件相关的类。由于此bug仍未修复，在此不包括有关特定易受攻击组件的详细信息。

5、有一些带有数字的大数组，这些数字代表一个shellcode和一个PE镜像。

由于存在漏洞披露原则，在此提供的分析比较简短。该漏洞利用了两个线程之间的竞争条件错误，原因是它们之间缺少适当的同步。它使攻击者可利用Use-After-Free 进行远程代码执行。

该漏洞利用程序首先尝试触发UaF对重要的64位地址信息泄漏。结果是：

> 1）如果地址成功泄漏，则表明漏洞利用正常。
>
> 2）泄漏的地址可用于查询堆/堆栈的位置，使地址随机化（ASLR）无效；
>
> 3）在该地址附近进行搜索，可以找到其他一些有用的指针，以供进一步利用。

之后尝试使用递归函数创建了很多对象，为了生成一些确定的堆布局，对于成功利用该漏洞非常重要。同时，它利用堆喷技术，该技术可重用先前在UaF部分释放的指针。但该技巧可能会引起混乱，使攻击者对两个不同的对象进行操作。

该漏洞尝试执行许多操作来分配/释放内存，最终为攻击者提供任意的读/写，用于制作可以与WebAssembly和FileReader一起使用的特殊对象，以执行Shellcode。

![](https://image.3001.net/images/20191104/1572832481_5dbf84e1c4975.png!small)

##  Payload

最终的有效负载为加密的二进制文件（worst.jpg），下载后由shellcode解密。

![](https://image.3001.net/images/20191104/1572832587_5dbf854b7b896.png!small)

解密后，恶意软件模块将作为updata.exe存储在磁盘上并执行。 为了持久控制，该恶意软件会在Windows Task Scheduler中新建任务。

有效负载“安装程序”是RAR SFX文件，其中包含以下信息：

    
    
    File size: 293,403
    MD5: 8f3cd9299b2f241daf1f5057ba0b9054
    SHA256: 35373d07c2e408838812ff210aa28d90e97e38f2d0132a86085b0d54256cc1cd

文件包含两个部分：

![](https://image.3001.net/images/20191104/1572833182_5dbf879e44b8f.png!small)

    
    
    File name: iohelper.exe
    MD5: 27e941683d09a7405a9e806cc7d156c9
    SHA256: 8fb2558765cf648305493e1dfea7a2b26f4fc8f44ff72c95e9165a904a9a6a48
    File name: msdisp64.exe
    MD5: f614909fbd57ece81d00b01958338ec2
    SHA256: cafe8f704095b1f5e0a885f75b1b41a7395a1c62fd893ef44348f9702b3a0deb

这两个文件是同时编译的，时间戳记是“ Tue Oct 8 01:49:31 2019”。

主模块（msdisp64.exe）从硬编码C2服务器集中下载下一阶段模块，下一阶段模块位于C2服务器上受害计算机名称的文件夹中。攻击者可以了解有哪些计算机被感染，并将下一阶段模块放置在C2服务器上的特定文件夹中。

##  IoCs

> behindcorona[.]com
>
> code.jquery.cdn.behindcorona[.]com
>
> 8f3cd9299b2f241daf1f5057ba0b9054
>
> 35373d07c2e408838812ff210aa28d90e97e38f2d0132a86085b0d54256cc1cd
>
> 27e941683d09a7405a9e806cc7d156c9
>
> 8fb2558765cf648305493e1dfea7a2b26f4fc8f44ff72c95e9165a904a9a6a48
>
> f614909fbd57ece81d00b01958338ec2
>
> cafe8f704095b1f5e0a885f75b1b41a7395a1c62fd893ef44348f9702b3a0deb
>
> kennethosborne@protonmail.com

 ***参考来源：[securelist](https://securelist.com/chrome-0-day-exploit-cve-2019-13720-used-in-operation-wizardopium/94866/)，由Kriston编译，转载请注明来自FreeBuf.COM**

  

