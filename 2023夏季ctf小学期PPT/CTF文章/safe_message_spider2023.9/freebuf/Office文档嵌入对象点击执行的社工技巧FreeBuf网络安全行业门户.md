## 简介  

 **Microsoft
Office相信大家都用过。Office在文档中嵌入对象极大的方便了我们的日常使用，但同时也为我们带来了众多安全问题。可以说，Office文档为攻击者提供了各种方法来诱骗受害者运行任意代码。当然，攻击者也可能会尝试利用Office漏洞，但更常见的情况是，攻击者会向受害者发送包含恶意宏或嵌入式（Packager）可执行文件的Office文档。**

## ![ie-download-file.png](https://image.3001.net/images/20180902/1535856198_5b8b4e465833b.png!small)

为此，微软在Office的安全问题上也下了不少的功夫。Office中有个名为[受保护的视图（Protected
View）](https://support.office.com/en-us/article/what-is-protected-view-d6f09ac7-e6b9-4495-8e43-2bbcdbcb6653)的安全功能，如果Office文档来自于互联网，那么该功能会以受限方式打开该文档。这个功能的目的是限制可运行的Office组件，以防止攻击者自动利用诸如OLE、Flash以及ActiveX等对象中存在的漏洞。在Office
2016和Office
365还添加了其它的安全措施（如GPO等），这样当用户从Internet下载文档时宏将完全被禁用，以及阻止在[Packer文件扩展名黑名单列表](https://support.office.com/en-us/article/packager-activation-in-office-365-desktop-applications-52808039-4a7c-4550-be3a-869dd338d834?ui=en-US&rs=en-US&ad=US)中的文件类型运行。

当然，即便如此安全问题依旧存在，但这些措施也在一定程度上减少了此类攻击的发生。最近，[Matt
Nelson](https://twitter.com/enigma0x3)向我们演示了使用[SettingContent-ms](https://posts.specterops.io/the-tale-of-settingcontent-ms-files-f1ea253e4d39)文件运行任意命令的方法。由于这些文件并不包含在文件类型的黑名单列表中，因此攻击者可以诱骗受害者从Office文档运行嵌入的SettingContent-ms文件。目前，此类文件类型已被添加到了黑名单中。在2018年8月的补丁更新中，微软还发布了一个修复程序，即如果不是从%WinDir%\ImmersiveControlPanel.打开这些文件的，则会进行阻止。

在本文中，我将向大家介绍另外两种诱骗受害者运行恶意代码的方法。这两种方法都需要有一定量的用户交互。MSRC指出“这种技术需要结合大量的社会工程学技巧：受害者必须要对安全警告说'Yes'
，且在非保护模式下运行”攻击者才有可能得手，因此并不会针对该问题发布任何的修复程序。

##  **Shell.Explorer.1**

Shell.Explorer.1 OLE对象（CLSID
{EAB22AC3-30C1-11CF-A7EB-0000C05BAE0B}）充当嵌入式Windows资源管理器或IE浏览器。此OLE对象可以嵌入到Office文档中，并可作为持久对象保存在文档中。专有格式用于持久化Shell.Explorer.1对象，在偏移量76
(0x4C)处可以找到熟悉的结构。可以看到位于此偏移处的结构是ShellLink (LNK) [[MS-SHLLINK](https://msdn.microsoft.com/en-us/library/dd871305.aspx)]。

当初始化（加载）Shell.Exporer.1对象时，ShellLink结构将被解析为常规LNK文件。然后，该对象从ShellLink获取ID列表，并以此来导航到提供的文件，
(shell) 文件夹或网站。

![CWebBrowserOC_BrowseObject.png](https://image.3001.net/images/20180902/1535856233_5b8b4e6936e3f.png!small)

###  **嵌入Windows资源管理器对象**

当提供了文件夹路径后，该对象的行为类似于Windows资源管理器。可以浏览文件或文件夹，甚至可以通过双击来执行文件。攻击者可能会滥用此功能来嵌入Windows资源管理器，从而打开包含可执行文件的远程共享。如果攻击者可以说服受害者双击文件，就可以从该远程共享运行可执行代码。

但这种攻击者的实现条件较为苛刻。首先，OLE对象需要单击才能激活。其次，用户需要双击OLE对象才能实际获得可用的Windows资源管理器视图。最后，用户还需要双击Windows资源管理器视图中的文件。这其中的任何一步出现问题，都将导致失败。

在某些情况下，管理员可能会限制一些用户对某些文件夹或硬盘的浏览权限。这种情况下，嵌入Windows资源管理器对象就会很方便。例如，如果限制对C:盘的访问，则本地用户可以使用包含嵌入式Windows资源管理器的Office文档来绕过该限制。此外，该对象也可用于窃取NetNTLM哈希值，但这对于Office文档来说并不难，因此使用单击激活OLE对象是没有意义的。

![embedded-windows-explorer.png](https://image.3001.net/images/20180902/1535856567_5b8b4fb7bbd7f.png!small)

### Internet Explorer

当Shell.Explorer.1充当嵌入式Internet
Explorer时，除了可以在文档中嵌入Web浏览器之外，它还允许我们浏览本地计算机上的文件，以及远程（共享和网站）上的文件。但这依然需要与用户产生交互，可以说这是无法避免的。单击激活也适用于此模式，单击该对象将触发Internet
Explorer的文件下载功能，这将向用户弹出一个“文件下载”对话框。如果用户单击“运行”或“打开”（主要取决于文件格式），则将执行该文件。

![File-Download-dialog.png](https://image.3001.net/images/20180902/1535856594_5b8b4fd2c980a.png!small)

某些文件类型（如EXE文件）还将会触发一个额外的警告对话框。但我们可以通过使用其他可执行文件类型，来避免该警告弹框（例如SettingContent-ms文件格式等）。

![run-security-warning.png](https://image.3001.net/images/20180902/1535856637_5b8b4ffda976c.png!small)

对于控件禁用IE保护模式，这将阻止其他对话弹框 - 如UAC对话框。因此，只需要单击两次就可以运行恶意代码，即单击激活，然后
运行/打开。Shell.Explorer.1对象，也是解决Office
2016/365中文件扩展名黑名单的一个很好的方法。因为，Shell.Explorer.1并未使用黑名单列表。

###  **POC**

以下PowerShell脚本将尝试创建包含嵌入式Internet
Explorer对象的Word文档。该脚本使用Packager对象创建了一个看起来像是嵌入文件的对象，单击该对象将触发文件下载功能。

![20180902105255.png](https://image.3001.net/images/20180902/1535856818_5b8b50b270c20.png!small)

![20180902105231.png](https://image.3001.net/images/20180902/1535856842_5b8b50ca86b4e.png!small)

## Microsoft Forms 2.0 HTML 控件

Microsoft Forms
2.0对象库包含许多可以在Office文档中使用的“HTML”ActiveX控件。这些控件在初始化时被标记为安全，并且不需要用户为嵌入它们的文档启用ActiveX。存储格式比Shell.Explorer.1对象简单得多。本质上，它是由对象的CLSID和HTML片段（UTF-16编码）组成的。HTML片段（HTML
fragment）的格式正确与否并不重要，对象只会搜索它支持的属性。以下是支持action属性的两个对象：

> \- Forms.HTML:Image.1 (CLSID {5512D112-5CC6-11CF-8D67-00AA00BDCE1D})
>
> \- Forms.HTML:Submitbutton.1 (CLSID {5512D110-5CC6-11CF-8D67-00AA00BDCE1D})

单击设置了action属性的嵌入对象，将打开定义的URL。常规URL将在默认浏览器中打开，但文件URL（包括共享文件）将会被直接打开。这将弹出一个警告对话框，但此对话框与其他警告对话框略有不同，如下图所示。

![1.png](https://image.3001.net/images/20180902/1535856874_5b8b50ea1b2fe.png!small)

Forms.HTML:Image.1支持src属性，可用于配置文档中显示的图像。使用图像可以伪装对象，例如将其伪装成嵌入文档诱使受害者点击它。

需要提醒的是，当Office文档包含[Web标记](https://docs.microsoft.com/en-us/previous-versions/windows/internet-explorer/ie-developer/compatibility/ms537628\(v=vs.85\))时，将会弹出另外一个警告对话框，向用户表明它是从Internet下载的。此对话框的提示将更为明确，从一个远程攻击者的角度来看，这种技术并不实用。

![motw-exe-warning.png](https://image.3001.net/images/20180902/1535856924_5b8b511c1efe9.png!small)

###  **POC**

以下PowerShell脚本可用于创建具有嵌入Forms.HTML:Image.1对象的Word文档，单击该对象将打开计算器。

![20180902105550.png](https://image.3001.net/images/20180902/1535856988_5b8b515c8a8e4.png!small)

![20180902105651.png](https://image.3001.net/images/20180902/1535857043_5b8b51937c111.png!small)

## 受保护视图

如上所述，当Office文档包含[Web标记](https://docs.microsoft.com/en-us/previous-versions/windows/internet-explorer/ie-developer/compatibility/ms537628\(v=vs.85\))时，则会向用户表明它是从Internet下载的。这种情况下，文档将在受保护的视图中打开。在此模式下，将禁用文档中存在的任何嵌入对象。除非攻击者利用漏洞绕过受保护视图，否则攻击者就需要结合社工的技巧来欺骗受害者单击“启用编辑（Enable
Editing）”。

![office-protected-view.png](https://image.3001.net/images/20180902/1535857073_5b8b51b1e2bd3.png!small)

## 防御

特别关注包含以下对象的文档：

> \- Shell.Explorer.1 / {EAB22AC3-30C1-11CF-A7EB-0000C05BAE0B}
>
> \- Forms.HTML:Image.1 / {5512D112-5CC6-11CF-8D67-00AA00BDCE1D}
>
> \- Forms.HTML:Submitbutton.1 / {5512D110-5CC6-11CF-8D67-00AA00BDCE1D}

Shell.Explorer.1对象从对象中提取LNK文件，并检索ID列表查找单击对象时打开的内容。我们的GitHub上的[ShellLink](https://github.com/securifybv/ShellLink)
.NET类库可用于从LNK文件中读取ID列表。

HTML
Forms对象更容易解析。作为防御者应该知道有多种方法可以在Office文档中存储对象。例如，ActiveX控件也可以嵌入作为PersistPropertyBag对象，其中对象的属性设置在XML文件中（例如，activeX1.xml）。

## 总结

当前，通过诱骗受害者点击运行恶意可执行文件仍是一种较为流行的方法。由于近些年来微软对Office和Windows安全的不断优化，攻击者需要探索出更多的攻击方法。在本文中我为大家提供了两种备选方案，相比之下Shell.Explorer.1技术似乎在实际场景中更加实用。虽然，在实际的攻击过程当中会向用户弹框告警，但多数用户的安全意识都较为薄弱，攻击者往往只要耍一点小聪明就能控制用户行为成功实施攻击计划。

作为红队队员或是一个攻击者，他们并不会去关心有什么安全修复，只要有机会他们就会马上付诸于行动。而作为一名防御者，我们必须第一时间了解或掌握此类攻击方法，以作出合理的响应和防御计划方案。不仅于此，我们还要通过通过部署诸如应用程序白名单和攻击面减少规则（或类似的替代方案）来提高攻击者的门槛。但更重要的是，做好在安全事件发生之前的安全防护工作，以及追捕入侵者让他们为此付出沉重代价。

***参考来源：[securify](https://securify.nl/en/blog/SFY20180801/click-me-if-you-can_-office-social-engineering-with-embedded-objects.html)，FB小编 secist
编译，转载请注明来自FreeBuf.COM**

