**作者：且听安全  
原文链接：<https://mp.weixin.qq.com/s/q0lbegDjLViLI48N6RjGVw>**

接上文：

> 第一部分：样本分析
>
> [CVE-2021-40444-Microsoft
> MSHTML远程命令执行漏洞分析（一）](https://paper.seebug.org/1792/)

分析完网上流传的样本后，我准备尝试替换cab文件中的文件后复现漏洞。安装的office软件版本：Microsoft Word 2016
（16.0.4266.1003）:

![](https://images.seebug.org/content/images/2022/06/9e6e96d5-5aa0-4e3b-ab3c-4558fb7616eb.png-w331s)

Windows的版本：Windows10 1909 （build
18363.1734）。我们首先在虚拟机上用原始的docx进行复现测试，先修改hosts文件，将域名解析为127.0.0.1：

![](https://images.seebug.org/content/images/2022/06/f54c13f0-ec67-4f96-ab96-c3c0394aca04.png-w331s)

将ministry.cab和side.html预先存放在一个目录下（目录名根据前期的样本分析，设置为e8c76295a5f9acb7），并在上层目录用python开一个http服务，服务端口为80：

![](https://images.seebug.org/content/images/2022/06/3a2a9936-d8b0-45cd-9012-0b615110a056.png-w331s)

然后尝试打开恶意docx文件，可以看到http服务器上有对应像下载请求：

![](https://images.seebug.org/content/images/2022/06/70c7e9f9-232e-4c01-80a5-a6a2abdeee37.png-w331s)

可以使用Process Monitor来看一下word在打开恶意样本的时候到底做了什么，启动前先设个过滤器：

![](https://images.seebug.org/content/images/2022/06/a35f0003-aab1-4acc-98f8-6aa36472096e.png-w331s)

重新打开docx，Process
Monitor会记录word（即winword.exe）的所有操作，可以看到word将side.html存放在临时目录下，并改名为side[1].htm

![](https://images.seebug.org/content/images/2022/06/db03161a-06f6-49ad-be56-e8809d131b93.png-w331s)

继续往下翻，还可以看到word将ministry.cab存在了另一个临时目录下，并改名为ministry[1].cab，但是用资源管理器查看时发现文件已经被删除了。

![](https://images.seebug.org/content/images/2022/06/58f08c95-d8f1-415c-b601-a4d121496ff2.png-w331s)

继续往下翻，还可以看到word又在Temp目录下创建了文件championship.inf
![](https://images.seebug.org/content/images/2022/06/ea8e72d6-c69e-4807-b4ca-ae83eed95756.png-w331s)

而后面则是使用control.exe 执行
.cpl:../../../AppData/Local/Temp/championship.inf，可以合理推测恶意软件已被成功执行（恶意软件的进一步分析已超出本文的范围）：

![](https://images.seebug.org/content/images/2022/06/f0ea838e-8b2d-4bfa-9bdc-69296e2b48ac.png-w331s)

下一步我们准备替换ministry.cab文件中的文件，看能否实际执行成功，所以我们要做的就是重新创建一个cab包，就像这样：

![](https://images.seebug.org/content/images/2022/06/44451673-a0ed-450d-80df-6bf92ed9fcef.png-w331s)

将新的cab替换原来的文件后，再次打开docx，结果并没有预期那样释放我们提供的messagebox.dll（通过浏览Process
Monitor监控，没有看到创建文件操作），这一点比较奇怪（后面在漏洞成因分析中，通过逆向urlmon.dll就能发现原因了）。

于是我将自定义的dll重命名为championship.inf（跟原始样本一样），再试一次：

![](https://images.seebug.org/content/images/2022/06/576ec0ce-5b39-4b4b-b872-49f4875466b0.png-w331s)
这次应该是成功释放了，不过释放的目录不一样，没有直接存放在Temp目录下，而是在一个随机文件名的临时目录下（这样的话control.exe就没办法找到championship.inf）：
![](https://images.seebug.org/content/images/2022/06/a2f3bb24-2ba3-4cec-9f5d-f9e2b2617e6d.png-w331s)

看来只能对比新旧两个ministry.cab有什么区别了：

![](https://images.seebug.org/content/images/2022/06/c290b221-d1e9-4df1-861f-025e0bae79aa.png-w331s)

通过对比发现原始的ministry.cab中文件的名称前有../，这也就解释了为什么原始的文件会释放在Temp目录下，而我们自己做的却没有。所以我们得重新创建一个cab，而其中的文件名也是../championship.inf。

为了方便，我们可以先用makecab打包一个xxxchampionship.inf，然后再用二进制编辑软件将文件名的前3个字节其修改为../，再次尝试果然也成功释放到了Temp目录下，但是似乎一直没有被执行，通过仔细查看Process
Monitor中的结果，我们发现了下面的一项：

![](https://images.seebug.org/content/images/2022/06/1cde41ee-2a12-4283-b69a-d5396dff583c.png-w331s)

这个championship.inf居然直接被删除了，而对比原始样本，在CloseFile前没有这一项：

![](https://images.seebug.org/content/images/2022/06/f5b0a862-3f7e-4260-9504-5cf36b5dc79d.png-w331s)

这个问题困扰了我一段时间，但是目前我还不想逆向整个漏洞的成因和触发流程。现在整个漏洞利用链条，我们修改过的仅仅是这个cab文件，所以问题肯定就在这个文件上面，而cab文件的头又非常简单，通过几次尝试，终于找到了问题所在：就是CFFILE结构中的cbFile字段：
![](https://images.seebug.org/content/images/2022/06/8a8b83bc-7692-425e-a118-4667299f777e.png-w331s)

当我们将该长度改一个比正常值更大的值，则释放的championship.inf文件将不再被删除，恶意代码将被执行：

![](https://images.seebug.org/content/images/2022/06/75ab4a53-0cef-4556-a0cf-c507a6534980.png-w331s)

事实上，当cbFile的大小超出cab包的实际大小时，将发生访问异常，导致championship.inf没有被正常清除，使恶意代码得以执行，详细分析见下一章的漏洞成因分析。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1795/>

