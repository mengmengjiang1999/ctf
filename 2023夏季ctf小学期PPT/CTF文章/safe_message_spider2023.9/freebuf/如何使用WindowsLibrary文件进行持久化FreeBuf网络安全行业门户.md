## 前言

**想象一下，假设在你不知道的情况下，攻击者在你的计算机上放置了一个恶意文件。每当你访问桌面上某个文件夹时（例如Documents文件夹），都会执行一次该文件。这样的场景，通过利用一种鲜为人知的持久化技术就可以实现，这一过程需要用到Windows库（Library）文件。**

在Windows系统中，引入了库文件，允许用户在单个视图中查看多个目录的内容。库可以包含存储在本地计算机或远程位置的文件或文件夹。

对这些文件进行滥用以实现持久化的技术，首先由WikiLeaks Vault 7公开，这种技术与Junction
Folder滥用有许多相似之处。由于这两种技术都难以检测，所以它们为攻击者提供了一个不错的选择，同时也为安全研究人员制造了一大挑战。

本文将主要分析如何使用库文件来实现持久化，以及在搜索过程中需要查找的内容。

## 关于库文件

默认情况下，Windows库文件位于%APPDATA%\Microsoft\Windows\Libraries目录下，文件扩展名为library-ms。这些文件是基于XML的，并遵循了公开可用的模式。

作为示例，我们查看了用于Documents文件夹的文档库文件（Documents.library-ms）。在该文件中，最值得关注的部分是SimpleLocation元素的URL。这一元素指定了基于文件系统或基于协议处理程序的搜索连接器（Search
Connectors）的位置。

在我们的示例中，库使用全局唯一标识符（GUID）指向了URL元素中两个不同的已知文件夹。通过搜索GUID，我们发现了两个文档目录：

    
    
    {FDD39AD0-238F-46AF-ADB4-6C85480369C7} %USERPROFILE%\Documents
    
    {ED4824AF-DCE4-45A8-81E2-FC7965083634} %PUBLIC%\Documents

![文档目录](https://www.countercept.com/assets/Uploads/_resampled/ResizedImageWzYwMCw1NDFd/Library-Files-Screenshot-of-documents-library-pointing-to-two-directories.jpg)

在使用这两个位置时，打开这个库将会允许用户在单个视图中查看两个不同目录的内容。下面的屏幕截图中展示了每个文件夹中的内容：

![文件夹内容](https://www.countercept.com/assets/Uploads/Library-Files-Screenshot-of-document-folder-directory.jpg)

然而，在查看库时，所有项目都会显示在同一个文件夹中：

![显示在同一个文件夹中](https://www.countercept.com/assets/Uploads/_resampled/ResizedImageWzYwMCwxNTdd/Library-Files-Screenshot-of-documents-library2.jpg)

## 创建恶意库文件

那么，我们如何滥用此功能来获得持久性呢？

最简单的方法是添加另一个URL元素，来加载恶意COM对象。当访问或显示文件夹时，它将导致我们的COM对象执行。

在下面的示例中，我们创建了一个引用Payload beacon.dll的COM对象。

![引用Payload
beacon.dll的COM对象](https://www.countercept.com/assets/Uploads/_resampled/ResizedImageWzYwMCwxMjdd/Library-Files-COM-object-that-referenced-payload-beacon-dll.jpg)

然后，另一个searchConnector被添加到库中，其中一个URL元素引用了我们创建的CLSID。

![引用了我们创建的CLSID](https://www.countercept.com/assets/Uploads/Library-Files-search-connector-added-to-library.jpg)

最后，该库已经被保存到桌面，因此它看起来像一个合法的文件夹“Documents”。如果用户打开该文件夹，将会显示Documents文件夹中的内容。但是在后台，COM对象也会被执行，从PID为5392的rundll32.exe启动我们的信标Payload（Beacon）。

![启动我们的信标Payload](https://www.countercept.com/assets/Uploads/Library-Files-library-saved-to-desktop.jpg)

![启动我们的信标Payload](https://www.countercept.com/assets/Uploads/_resampled/ResizedImageWzYwMCwzNzld/Library-Files-rundll32-exe-properties.jpg)

有趣的是，rundll32没有显示父进程。这是由于，在运行COM对象后，退出了父进程dllhost.exe（COM
Surrogate进程）。在Sysmon中，我们将看到类似于以下示例的事件，其父进程为dllhost.exe，子进程为rundll32.exe。

![子进程为rundll32.exe](https://www.countercept.com/assets/Uploads/Library-Files-sysmon-event-properties-window.jpg)

查看Process
Monitor，我们可以看到dllhost.exe在查询我们创建的CLSID，然后加载beacon.dll，再然后执行rundll32.exe。

![](https://www.countercept.com/assets/Uploads/Library-Files-process-monitor-1.jpg)

![](https://www.countercept.com/assets/Uploads/Library-Files-process-monitor-2.jpg)

![查看Process Monitor](https://www.countercept.com/assets/Uploads/Library-Files-process-monitor-3.jpg)

虽然这些数据点可用于检测，但很可能会出现合法活动的误报情况。我们可以通过关联数据点，来得到具有更高准确度的结果。

## 实现持久化

显然，为了实现持久性，我们需要在系统启动时执行library-ms文件。那么，应该如何实现这一目标呢？

除了通常的持久化技术之外，有一种更隐蔽的方法，是使用Windows资源管理器。它将在查看包含该文件的目录时，自动执行该文件。因此，用户无需实际单击这个文件，只需要查看目录就足够了。举例来说，我们可以将库文件放在桌面上，在启动时，资源管理器将会对它进行渲染，导致COM对象执行。

从检测角度来看，启动执行和用户单击执行之间的区别就在于，启动执行时父进程是explorer.exe，因为它是导致库文件呈现出来的资源管理器。

![](https://www.countercept.com/assets/Uploads/_resampled/ResizedImageWzYwMCwzM10/Library-Files-explorer-exe.jpg)

![](https://www.countercept.com/assets/Uploads/_resampled/ResizedImageWzYwMCwyMl0/Library-Files-IP-screenshot.jpg)

![从检测角度来看](https://www.countercept.com/assets/Uploads/Library-Files-rundll-exe-properties-2.jpg)

### 寻找library-ms文件

我们可以通过查找具有library-ms扩展名的任意文件，来使用PowerShell搜索恶意库文件，然后过滤URL标记以获取CLSID，同时检索相关的注册表项以进行分析。

![寻找library-ms文件](https://www.countercept.com/assets/Uploads/_resampled/ResizedImageWzYwMCwyNzNd/Library-hunting-for-library-ms-files-using-PowerShell.jpg)

此方案仅仅是基于对URL元素的滥用，如果想要进一步发现异常，可能需要寻找其他元素。

我们提供了一个脚本，用于对%USERPROFILE%文件夹中创建的任何library-ms文件执行上述条件检查，我们可以使用该文件检查注册表中是否存在与此技术相关的异常项。

![寻找library-ms文件](https://www.countercept.com/assets/Uploads/_resampled/ResizedImageWzYwMCw5NV0/Library-Files-hunting-for-library-ms-files-3.jpg)

脚本的下载地址为：
<https://gist.github.com/countercept/6890be67e09ba3daed38fa7aa6298fdf>。

寻找library-ms文件创建也很有用，这可能会是一个高准确度的指标，因为这些扩展很少会被创建。类似于Sysmon这样的工具可以让我们轻松监视这些事件，只需要将以下内容添加到带有FileCreate标记的Sysmon配置文件中即可。

![寻找library-ms文件](https://www.countercept.com/assets/Uploads/_resampled/ResizedImageWzYwMCw1N10/Library-Files-file-create-tag-in-sysmon.jpg)

创建library-ms文件时，我们将看到如下所示的文件创建事件：

![文件创建事件](https://www.countercept.com/assets/Uploads/_resampled/ResizedImageWzYwMCwzODZd/Library-Files-file-creation-event.jpg)

## 结论

在Windows中，有很多“传统”的持久化技术，例如注册表、服务、计划任务等，许多安全研究者都会关注这些技术。正如本文所描述的， library-ms文件对防守方提出了一个独特的挑战，由于它们可以隐蔽地通过COM引用执行代码，所以检测和分析过程就更加具有挑战性。

系统防守方应该专注于创建和修改.library-ms文件以及COM条目。除了来自explorer.exe或dllhost.exe的这些可疑进程执行之外，它们还可以提供恶意活动的进一步证据。

参考链接：<https://www.countercept.com/blog/abusing-windows-library-files-for-persistence/>

 ***本文作者：eridanus96，转载请注明来自FreeBuf.COM**

