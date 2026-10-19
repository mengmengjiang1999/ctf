## 写在前面的话

 **Microsoft
Office文档为攻击者提供了各种欺骗受害者运行任意代码的方法。当然，攻击者可能会尝试直接利用Office漏洞，但更常见的情况是向受害者发送包含恶意代码的文档。
与此同时，微软也一直在制定安全措施。一般措施当文档从internet上下载时，并不会直接打开，而是在受保护视图中打开它们。**

Office 2016和Office
365使用其他安全措施（如GPO），以便在从Internet下载文档时完全禁用宏。而且Packer文件扩展名黑名单，阻止黑名单文件类型的运行。
当然，这些保护并不完美，但它们有助于减少这类攻击。最近，Matt Nelson演示了`SettingContent-ms`文件可用于运行任意命令。这些文件最初不在黑名单中，因此可用于欺骗受害者从Office文档运行`SettingContent-ms`文件。但此文件类型现已添加到黑名单中，以保护Office
2016/365用户。在2018年8月补丁周二期间，微软还发布了一个修复程序，如果这些文件没有从`%WinDir%\ImmersiveControlPanel`打开，就阻止它们被打开。在这篇博客中，我将展示另外两种诱导受害者运行恶意代码的方法。两种方法都需要一定量的用户交互。

## Shell.Explorer.1

所述`Shell.Explorer.1`OLE对象（`CLSID
{EAB22AC3-30C1-11CF-A7EB-0000C05BAE0B}`）充当嵌入Windows资源管理器或嵌入式的Internet
Explorer。此OLE对象可以嵌入Office文档中，并作为持久对象保存在文档中。专有格式用于持久化`Shell.Explorer.1`对象，可以在偏移量`76（0x4C）`处找到。位于此偏移处的结构是`ShellLink（LNK）`结构的[
MS-SHLLINK ](a%20href=)。
初始化（加载）`Shell.Exporer.1`对象时，`ShellLink`结构将被解析为常规LNK文件。然后，该对象从`ShellLink`
获取ID列表，并使用它来导航（浏览）到提供的文件，文件夹或网站。![1.png](https://image.3001.net/images/20180901/1535784861_5b8a379da9bb9.png!small)

### Embedded Explorer

提供文件夹路径时，该对象的行为类似于Windows资源管理器。可以浏览文件或文件夹，甚至可以通过双击来执行文件。攻击者可能会滥用此功能来嵌入Windows资源管理器。如果攻击者可以说服其受害者双击攻击者控制的文件，则可以远程运行可执行代码。
但是这种攻击似乎很难实现。首先，OLE对象需要单击才能激活，其次，用户需要双击OLE对象才能实际获得可用的Windows资源管理器视图。最后，用户还需要双击Windows资源管理器视图中的文件。
在管理员限制浏览某些文件夹或驱动器的可能性的情况下，嵌入Windows资源管理器对象会很方便。例如，如果限制对`C：`驱动器的访问，则本地用户可以使用包含嵌入式Windows资源管理器的Office文档来规避此限制。此外，该对象可用于窃取NetNTLM哈希值，但由于这对Office文档并不难，因此使用单击的OLE对象进行激活是没有意义的。

![2.png](https://image.3001.net/images/20180901/1535784869_5b8a37a511ca0.png!small)

### IE浏览器

当`Shell.Explorer.1`充当嵌入式Internet
Explorer时，事情会变得更有意思。除了可以在文档中嵌入Web浏览器之外，它还允许浏览本地计算机上的文件，以及浏览到远程位置（共享和网站）上的文件。没有一些用户交互，这是不可能完成的。单击激活也适用于此模式，单击该对象将触发Internet
Explorer的文件下载功能，这意味着将向用户显示“文件下载”对话框。如果用户单击“ 运行”或“ 打开”（取决于文件格式），则将执行该文件。
![3.png](https://image.3001.net/images/20180901/1535784877_5b8a37ad1a0cd.png!small)

某些文件类型（如EXE文件）将触发另一个警告对话框。但是通过使用其他可执行文件类型可以轻松避免此对话框。

![4.png](https://image.3001.net/images/20180901/1535784884_5b8a37b49081b.png!small)

保护模式IE被禁用用于控件，这确实会阻止显示其他对话框——如UAC对话框。因此，只需要两次单击就可以运行恶意代码，即单击以激活，然后运行/打开。

### Poc

下面的PowerShell脚本将尝试创建包含嵌入式Internet
Explorer对象的Word文档。该脚本使用Packager对象创建一个嵌入文件的对象，单击该对象将触发文件下载功能。

![5.gif](https://image.3001.net/images/20180901/1535784897_5b8a37c106ed0.gif!small)

## Microsoft Forms 2.0 HTML控件

Microsoft Forms
2.0对象库包含许多可以在Office文档中使用的`“HTML”ActiveX`控件。这些控件标记为可安全初始化，并且不要求用户为嵌入它们的文档启用ActiveX。存储格式比`Shell.Explorer.1`对象简单得多。本质上，它由对象的CLSID和HTML片段（UTF-16编码）组成。HTML片段不一定必须格式正确，对象只会搜索它支持的属性。两个对象支持action属性，该属性采用URL。这些对象是：

    
    
    - Forms.HTML:Image.1 (CLSID {5512D112-5CC6-11CF-8D67-00AA00BDCE1D})

`Forms.HTML:Submitbutton.1 (CLSID {5512D110-5CC6-11CF-8D67-00AA00BDCE1D})`

单击设置action属性的嵌入对象，将导致打开定义的URL。常规URL将在默认浏览器中打开，但文件URL（包括共享文件）将直接打开。将显示一个警告对话框，但此对话框与其他警告对话框略有不同，如图6所示。此警告对话框对于所有文件类型都是相同的。

![6.png](https://image.3001.net/images/20180901/1535784932_5b8a37e4230a3.png!small)

`Forms.HTML：Image.1`接受一个src，可用于配置文档中显示的图像。使用图像可以伪装对象，例如将其伪装成嵌入文档以诱使受害者点击它。
应该注意的是，当Office文档包含Web标记时，会显示另一个警告对话框，表明它是从Internet下载的。此对话框更明确，从远程攻击者的角度来看，这种技术没什么用。

![7.png](https://image.3001.net/images/20180901/1535784944_5b8a37f095826.png!small)

### Poc

以下PowerShell脚本可用于创建具有嵌入的`Forms.HTML：Image.1`对象的Word文档，单击该对象将导致计算器打开。

## 受保护的视图

如上所述，文档可能包含Web标记以将文件标记为从因特网下载。如果存在，文档将在受保护的视图中打开。在此模式下，将禁用文档中存在的任何嵌入对象。除非攻击者使用绕过受保护视图的漏洞，否则需要额外的社交工程来欺骗用户单击“
启用编辑”。

![9.png](https://image.3001.net/images/20180901/1535785000_5b8a3828ee986.png!small)

## 如何防御

用户应该注意包含以下任何对象的文档：

    
    
    - Shell.Explorer.1 / {EAB22AC3-30C1-11CF-A7EB-0000C05BAE0B} 
    Forms.HTML：Image.1 / {5512D112-5CC6-11CF- 8D67-00AA00BDCE1D} 
    

`Forms.HTML：Submitbutton.1 / {5512D110-5CC6-11CF-8D67-00AA00BDCE1D}`

对于`Shell.Explorer.1`对象从对象中提取LNK文件并检索ID列表以找出打开时的内容单击对象。我们的GitHub页面上的[ShellLink](a%20href=)
.NET类库可用于从LNK文件中读取ID列表。通常，LNK文件在`Shell.Explorer.1`对象的偏移量76处开始。 HTML
Forms对象更容易解析，因为它们是带有16字节GUID的UTF-16编码的HTML片段。防御者应该知道有多种方法可以在Office文档中存储对象。例如，ActiveX控件也可以嵌入为`PersistPropertyBag`对象，其中对象的属性设置在XML文件中（例如`activeX1.xml`）。

## 最后的话

Red
Teamers（和攻击者）一直在寻找新方法，他们并不关心什么符合安全修复的标准。作为一名防守者，知道什么样的攻击有助于阻止他们（工具者）。他不应止步于此，通过部署应用程序白名单和攻击面减少规则（或类似替代方案）之类的东西来提高攻击者的门槛。但更重要的是，确保能够了解网络上发生的事情，并寻找入侵者。

 ***参考来源：[securify](a%20href=)，由周大涛编译，转载请注明来自FreeBuf.COM**

