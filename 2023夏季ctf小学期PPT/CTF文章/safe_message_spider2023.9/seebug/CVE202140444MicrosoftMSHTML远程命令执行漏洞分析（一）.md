**作者：且听安全  
原文链接：<https://mp.weixin.qq.com/s/6q9fbggpkhd4PtwnghvZgg>**

## 漏洞概述

2021年9月8日，微软发布安全通告，披露了Microsoft MSHTML远程代码执行漏洞，攻击者可通过制作恶意的ActiveX控件供托管浏览器呈现引擎的
Microsoft Office文档使用，成功诱导用户打开恶意文档后，可在目标系统上以该用户权限执行任意代码。

> CVE-2021-40444
>
> <https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-40444>

完整的攻击流程借用了微软分析文章里面的图：

> Microsoft Security Blog
>
> <https://www.microsoft.com/security/blog/2021/09/15/analyzing-attacks-that-> exploit-the-mshtml-cve-2021-40444-vulnerability/>

![](https://images.seebug.org/content/images/2022/06/3611326e-5f45-4482-8b7c-2133188d8f9c.png-w331s)

## 快速样本分析

在恶意样本在线查询网站下载到样本：938545f7bbe40738908a95da8cdeabb2a11ce2ca36b0f6a74deda9378d380a52.zip，样本的MD5值为：1d2094ce85d66878ee079185e2761beb。可以看到该样本早在9月2号就被该网站收录了。

![](https://images.seebug.org/content/images/2022/06/0fc3db7e-3991-44a4-9562-3adb1cd3eba2.png-w331s)

注意该网站的样本解压密码为：infected，解压后可以得到一个docx文件。

![](https://images.seebug.org/content/images/2022/06/6c862f9a-dfd0-4453-b08e-b080aa738ecc.png-w331s)

熟悉的小伙伴都知道，docx文件其实就是一个zip压缩包，使用7zip等解压软件能够轻松将其解压出来：

![](https://images.seebug.org/content/images/2022/06/7746a541-8c9f-4222-9bcd-a9191b26db5c.png-w331s)

通过简单浏览，很快就能发现一个可疑的文件：word_rels\document.xml.rels，其中有个可疑的下载链接：

![](https://images.seebug.org/content/images/2022/06/b30a080b-ee66-4e9c-86ab-e785ed644203.png-w331s)

尝试去下载该side.html文件，发现服务器无法访问了，经验证h****.com这个域名已经失效：

![](https://images.seebug.org/content/images/2022/06/25a7d8e6-be88-41b1-ac85-f08fa7cc9487.png-w331s)

尝试通过网络搜索该域名信息，可以找到域名对应的真实IP： 23.106. ** _._**

![](https://images.seebug.org/content/images/2022/06/cae24013-7978-4eea-bac7-880cfca56de1.png-w331s)

抱着试试看的心情，用该IP来尝试下载，居然成功下载到可疑的html页面:

![](https://images.seebug.org/content/images/2022/06/c420ac94-b356-4473-8058-78992cace37d.png-w331s)

那就接着看一个这个神秘的html文件，发现文件中有一段更神秘的javascript代码：

![](https://images.seebug.org/content/images/2022/06/db8425fe-10da-407d-a725-8bf9171bf424.png-w331s)

![](https://images.seebug.org/content/images/2022/06/eec5fa1b-1a8b-4b21-a743-2f8c57df255f.png-w331s)

简单浏览side.html里面的javascript代码，又发现了一个可疑的下载链接http://hi***.com/e8c76295a5f9acb7/ministry.cab：

![](https://images.seebug.org/content/images/2022/06/ddf23d59-4093-48f0-a744-2e93aabc02d2.png-w331s)

javascript代码明显是经过某种混淆后的结果，幸好代码不算复杂，我们通过vscode的js插件先将代码整理一下，最终通过手动分析和去混淆后可以得到如下的代码：

![](https://images.seebug.org/content/images/2022/06/db8a41d8-71f0-4f2b-9d0d-7b99b448b4ce.png-w331s)

这段代码功能大概就是先利用XMLHttpRequest对象下载ministry.cab文件（这个地方可能是多余的，后面ActiveX也能实现下载），然后利用ActiveX控件自动从网络下载安装ministry.cab，最后利用Control
Panel objects
（.cpl）来执行championship.inf文件（该文件暂时不知道从哪里来的），直接通过IP地址将ministry.cab下载回来：

![](https://images.seebug.org/content/images/2022/06/94522338-020c-482a-a8b8-10d1d29ab10e.png-w331s)

接着分析这个ministry.cab文件，可以看到确实是微软的cab文件，尝试用cabextract解压发生错误（起初以为文件被破坏了，后来才知道这个异常却是漏洞利用的关键）：

![](https://images.seebug.org/content/images/2022/06/722ae701-f90a-4c8a-90ed-693837450c1d.png-w331s)

不过该cab文件中确实有championship.inf这个文件，这就与javascript代码对上了。这样整个样本的快速分析基本就到这里了，这里再理一下样本的利用思路：

  1. 发送恶意docx文件给用户点开
  2. docx文件利用OleObject对象实现下载并解析side.html
  3. side.html利用ActiveX控件实现下载ministry.cab，并释放championship.inf文件
  4. 最后利用Control Panel objects （.cpl）来执行championship.inf文件

好了，样本分析就到这里了，下一篇我们将进行漏洞复现和漏洞分析。关注我，不迷路！

## 参考

<https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-40444>

<https://www.microsoft.com/security/blog/2021/09/15/analyzing-attacks-that-exploit-the-mshtml-cve-2021-40444-vulnerability/>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1792/>

