**作者：Lucifaer  
博客：<https://www.lucifaer.com/>**

### 0x01 漏洞概述

> Confluence Server and Data Center had a path traversal vulnerability in the
> downloadallattachments resource. A remote attacker who has permission to add
> attachments to pages and / or blogs, or to create a new space or personal
> space, or who has 'Admin' permissions for a space, can exploit this path
> traversal vulnerability to write files to arbitrary locations which can lead
> to remote code execution on systems that run a vulnerable version of
> Confluence Server or Data Center.

根据官方文档的描述，我们大致能知道这是个需要权限的路径穿越的漏洞，并且可以将文件上传到任意路径。造成这个漏洞的关键点在于`DownloadAllAttachments`这个资源。在经过diff后，可以确定漏洞触发的关键点在于文件名的构造：

修复前

![](https://images.seebug.org/content/images/2019/04/19/1555669183000-15556630124609.jpg-w331s)

修复后

![](https://images.seebug.org/content/images/2019/04/19/1555669183000-15556629685846.jpg-w331s)

![](https://images.seebug.org/content/images/2019/04/19/1555669183000-15556630389868.jpg-w331s)

可以看到这里是对这里的`attachment.getFileName`所获取的文件名进行二次文件名获取。

### 0x02 漏洞分析

分析这个漏洞要从两个点入手：

  * `DownloadAllAttachments`自身的处理流程
  * 如何让文件名中包含`../`

在分析前我们应清楚哪里能调用`DownloadAllAttachments`，这样才方便调试。根据官方给出的临时修补措施，我们大致可以从附件管理的`Download
all attachments`这个地方入手：

![-w635](https://images.seebug.org/content/images/2019/04/19/1555669183000-15556636645966.jpg-w331s)

![-w1133](https://images.seebug.org/content/images/2019/04/19/1555669184000-15556640416058.jpg-w331s)

#### 2.1 DownloadAllAttachments处理流程

`DownloadAllAttachments`位于`com.atlassian.confluence.pages.actions.DownloadAllAttachmentsOnPageAction`，为了便于快速的解释这个漏洞，我用动态调试+静态分析的方法来进行说明。

我这里选取的是默认生成的`Lay out your page (step 6 of 9)`这个页面的下载全部附件进行测试的：

![-w1132](https://images.seebug.org/content/images/2019/04/19/1555669184000-15556643371813.jpg-w331s)

代码非常简单，分两部分来看：

![](https://images.seebug.org/content/images/2019/04/19/1555669184000-15556648729610.jpg-w331s)

可以看到在这里首先会将附件中的所有文件的基础信息置于一个数组中，然后对数组进行遍历，然后执行以下操作：

  1. 根据文件名创建一个新的`File`对象(tmpFile)
  2. 将文件内容写入输入流
  3. 将`FileOutputStream`输出流指向`File`对象
  4. 将输入流中的内容拷贝到`FileOutputStream`输出流中

这样就完成了将文件拷贝到另外一个位置的操作。

这里的`attachment.getFileName()`：

![](https://images.seebug.org/content/images/2019/04/19/1555669184000-15556657114892.jpg-w331s)

而title名就是文件名：

![](https://images.seebug.org/content/images/2019/04/19/1555669184000-15556657884254.jpg-w331s)

`getTempDirectoryForZipping()`：

![](https://images.seebug.org/content/images/2019/04/19/1555669185000-15556658919734.jpg-w331s)

![](https://images.seebug.org/content/images/2019/04/19/1555669185000-15556659124664.jpg-w331s)

是根据时间和随机数生成的一个目录，格式类似于`download2q1gP165938`，这里我们通过方法的名字就能看出这里是建立了一个创建一个zip的目录，这个目录在`confluence_home/temp/`

ok，知道了这些，继续向下看`DownloadAllAttachments`：

![](https://images.seebug.org/content/images/2019/04/19/1555669185000-15556661700493.jpg-w331s)

这里是完成将zip目录打包成zip文件的过程。

在进行文件复制的时候，我们注意到文件的路径是zip目录与文件名直接进行进行拼接生成的：

![](https://images.seebug.org/content/images/2019/04/19/1555669185000-15556665323662.jpg-w331s)

而这里就是整个目录穿越的关键，也就是说在生成zip文件前，如果附件列表中有文件的文件名是`../../xxx`的格式的话，就能进行目录穿越，在任意位置创建文件。

#### 2.2 寻找利用链

默认情况下，我们是没有办法创建以`.`开头的文件的，如果想要上传一个文件名类似`../../xxx`的文件的话，最简单的思路是用burp中间改包，但是在这个例子中是不行的：

![-w1241](https://images.seebug.org/content/images/2019/04/19/1555669185000-15556668251787.jpg-w331s)

应该是进行了自动的过滤，这个方法行不通。我又注意到了在属性中好像能修改文件名：

![-w1132](https://images.seebug.org/content/images/2019/04/19/1555669186000-15556668967289.jpg-w331s)

但是也是不成功的：

![-w700](https://images.seebug.org/content/images/2019/04/19/1555669186000-15556669182290.jpg-w331s)

就在我想要放弃的时候我尝试了一下编辑页面中的上传附件功能，竟然成功了：

![-w1036](https://images.seebug.org/content/images/2019/04/19/1555669186000-15556670429318.jpg-w331s)

![-w1245](https://images.seebug.org/content/images/2019/04/19/1555669186000-15556672925783.jpg-w331s)

![-w1122](https://images.seebug.org/content/images/2019/04/19/1555669187000-15556673194395.jpg-w331s)

在这里我点击`下载全部`，即可完成目录穿越：

![-w559](https://images.seebug.org/content/images/2019/04/19/1555669187000-15556673630695.jpg-w331s)

我们来对比一下两种上传方式有什么不同。

##### 直接上传(FileStorer)

直接上传这里是调用的`com.atlassian.confluence.pages.actions.beans.FileStorer`，关键点在：

![](https://images.seebug.org/content/images/2019/04/19/1555669187000-15556678949378.jpg-w331s)

在获取文件名时会对请求中的文件名进行处理：

![](https://images.seebug.org/content/images/2019/04/19/1555669187000-15556679723274.jpg-w331s)

![](https://images.seebug.org/content/images/2019/04/19/1555669187000-15556680604026.jpg-w331s)

会将文件名提取出来。

##### 利用插件上传

在利用插件上传时用的是`drag-and-drop`这个插件在`com.atlasian.confluence.plugins.dragdrop.UploadAction`。

在处理请求时并未对请求中的文件名进行处理：

![](https://images.seebug.org/content/images/2019/04/19/1555669187000-15556682894757.jpg-w331s)

所以会保存我们恶意修改的文件名

至此该漏洞分析完毕。

### 0x03 构造POC

首先登陆后编辑附件数大于2个的页面，在页面中加入附件：

![-w1036](https://images.seebug.org/content/images/2019/04/19/1555669186000-15556670429318.jpg-w331s)

burp抓包修改上传文件的文件名：

![-w1245](https://images.seebug.org/content/images/2019/04/19/1555669186000-15556672925783.jpg-w331s)

在附件管理页面下载全部附件：

![-w1122](https://images.seebug.org/content/images/2019/04/19/1555669187000-15556673194395.jpg-w331s)

文件会生成到`/confluence_home/temp/zip文件名../../`目录中：

![-w646](https://images.seebug.org/content/images/2019/04/19/1555669188000-15556686614397.jpg-w331s)

### 0x04 Reference

  * <https://confluence.atlassian.com/doc/confluence-security-advisory-2019-04-17-968660855.html>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/896/>

