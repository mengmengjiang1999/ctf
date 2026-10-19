# 引子

表妹是个会写代码的奇女子，  
前几天半夜神神秘秘的发了个视频给我。  
躲着女盆友，  
在厕所满怀激动的点开，  
结果是个WORD打开执行CALC的小视频（不是我想的）  
唉，既然看都看到了，  
那就跟一下，让表妹崇拜崇拜吧  
满世界找，终于弄到了一个样本的MD5...  
![这是广西表妹，不是俺表妹](https://image.3001.net/images/20210922/1632274329_614a8799b01cd26889c1e.jpg!small)

# 漏洞概述

2021年9月8日，微软发布安全通告 CVE-2021-40444 披露了Microsoft MSHTML远程代码执行漏洞：

[CVE-2021-40444](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-40444)

攻击者可通过制作恶意的ActiveX控件供托管浏览器呈现引擎的 Microsoft
Office文档使用，成功诱导用户打开恶意文档后，可在目标系统上以该用户权限执行任意代码。完整的攻击流程如图（借用了微软分析文章）：

[Microsoft Security
Blog](https://www.microsoft.com/security/blog/2021/09/15/analyzing-attacks-that-exploit-the-mshtml-cve-2021-40444-vulnerability/)

![image.png](https://image.3001.net/images/20210921/1632153797_6148b0c5d17714f26b64a.png!small)

# 快速样本分析

在恶意样本在线查询网站下载到样本：938545f7bbe40738908a95da8cdeabb2a11ce2ca36b0f6a74deda9378d380a52.zip，样本的MD5值为：1d2094ce85d66878ee079185e2761beb。可以看到该样本早在9月2号就被该网站收录了。

![image.png](https://image.3001.net/images/20210921/1632153843_6148b0f34a25384ae883f.png!small)

注意该网站的样本解压密码为：infected，解压后可以得到一个docx文件。

![image.png](https://image.3001.net/images/20210921/1632153890_6148b12294a019ea7be77.png!small)

熟悉的小伙伴都知道，docx文件其实就是一个zip压缩包，使用7zip等解压软件能够轻松将其解压出来：

![image.png](https://image.3001.net/images/20210921/1632153910_6148b136cc1dc7c5ba124.png!small)

通过简单浏览，很快就能发现一个可疑的文件：word_rels\document.xml.rels，其中有个可疑的下载链接：

![image.png](https://image.3001.net/images/20210921/1632153958_6148b16604a737b516ea7.png!small)

尝试去下载该side.html文件，发现服务器无法访问了，经验证h***.com这个域名已经失效：

![image.png](https://image.3001.net/images/20210921/1632153991_6148b1871dfd1c5aaa209.png!small)

尝试通过网络搜索该域名信息，可以找到域名对应的真实IP： 23.106.?.?

![image.png](https://image.3001.net/images/20210921/1632154047_6148b1bfb5fbb360ba09d.png!small)

抱着试试看的心情，用该IP来尝试下载，居然成功下载到可疑的html页面:

![image.png](https://image.3001.net/images/20210921/1632154080_6148b1e0795c01ff7ecf5.png!small)

那就接着看一个这个神秘的html文件，发现文件中有一段更神秘的javascript代码：

![image.png](https://image.3001.net/images/20210921/1632154101_6148b1f573c540100529d.png!small)

![image.png](https://image.3001.net/images/20210921/1632154113_6148b20134395ac3f1538.png!small)

简单浏览side.html里面的javascript代码，又发现了一个可疑的下载链接http://h***.com/e8c76295a5f9acb7/ministry.cab：

![image.png](https://image.3001.net/images/20210921/1632154147_6148b2238da1865361d6a.png!small)

javascript代码明显是经过某种混淆后的结果，幸好代码不算复杂，我们通过vscode的js插件先将代码整理一下，最终通过手动分析和去混淆后可以得到如下的代码：

![image.png](https://image.3001.net/images/20210921/1632154180_6148b24413c8a42644a88.png!small)

这段代码功能大概就是先利用XMLHttpRequest对象下载ministry.cab文件（这个地方可能是多余的，后面ActiveX也能实现下载），然后利用ActiveX控件自动从网络下载安装ministry.cab，最后利用Control
Panel objects
（.cpl）来执行championship.inf文件（该文件暂时不知道从哪里来的），直接通过IP地址将ministry.cab下载回来：

![image.png](https://image.3001.net/images/20210921/1632154212_6148b264c5a51ff340c73.png!small)

接着分析这个ministry.cab文件，可以看到确实是微软的cab文件，尝试用cabextract解压发生错误（起初以为文件被破坏了，后来才知道这个异常却是漏洞利用的关键）：

![image.png](https://image.3001.net/images/20210921/1632154235_6148b27b7fcbfffae37b7.png!small)

不过该cab文件中确实有championship.inf这个文件，这就与javascript代码对上了。

这样整个样本的快速分析基本就到这里了，这里再理一下样本的利用思路：

  1. 发送恶意docx文件给用户点开
  2. docx文件利用OleObject对象实现下载并解析side.html
  3. side.html利用ActiveX控件实现下载ministry.cab，并释放championship.inf文件
  4. 最后利用Control Panel objects （.cpl）来执行championship.inf文件

好了，样本分析就到这里了，下一篇我们将继续进行漏洞复现和漏洞分析。

# 参考

https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-40444  
https://www.microsoft.com/security/blog/2021/09/15/analyzing-attacks-that-exploit-the-mshtml-cve-2021-40444-vulnerability/

