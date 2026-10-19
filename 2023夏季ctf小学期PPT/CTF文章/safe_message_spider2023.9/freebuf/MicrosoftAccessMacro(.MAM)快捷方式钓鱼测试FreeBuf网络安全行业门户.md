**去年，我曾发表过一篇关于[创建恶意.ACCDE（Microsoft
Access数据库）文件，并将其作为攻击向量进行网络钓鱼的文章](https://medium.com/rvrsh3ll/phishing-for-access-554105b0901e)。作为扩展，本文将为大家引入一种新的钓鱼方案Microsoft Access
Macro“MAM”快捷方式钓鱼。MAM文件是一个直接链接到Microsoft Access Macro的快捷方式（从Office 97开始）。**

## 创建一个MAM文件

我们先来创建一个可以弹出本地计算机的，简单Microsoft Access数据库来练练手。首先，我们打开MS Access并创建一个空数据库。如下：

![1_HSUkf9qr2SpQlt1x.png](https://image.3001.net/images/20180705/15307758802182.png!small)

接着，找到Create ribbon并选择Module。这将为我们打开Microsoft Visual Basic for Applications
design editor。

在Microsoft Access中，我们的module将包含我们的代码库，而macro将会使Access执行VB代码。

以下是我编写的一个简单的计算机弹出代码：

![2_MEsimvkiNDrFA2Ue.png](https://image.3001.net/images/20180705/15307759024245.png!small)

请注意这里我是如何将Function调用添加到此代码中的。当我们创建宏时，它将寻找function调用而不是sub。

现在，我们保存模块并退出代码编辑器。

![3_fWXZeHWNjNwa1coU.png](https://image.3001.net/images/20180705/15307759211226.png!small)

模块保存后，我们可以创建宏来调用模块。打开Create ribbon并选择“macro”。 使用下拉框选择“Run Code”并指向你的宏函数。

![4_eBvNz7Uxavtnc6zd.png](https://image.3001.net/images/20180705/15307759416211.png!small)

接下来，我们点击“Run”菜单选项来测试宏，Access将提示你保存宏。如果你希望在打开文档时自动运行宏，请务必将宏保存为Autoexec。

![5_dJxP4gLR_h-d27HP.png](https://image.3001.net/images/20180705/15307759552503.png!small)

保存项目，我们以.accdb格式保存，以便后续对该项目的修改操作。

![6_KcH9O92Z7qmRPoty.png](https://image.3001.net/images/20180705/15307759791238.png!small)

然后，我们将再次保存我们的项目。这一次，我们选择Make ACCDE选项。这将为我们创建数据库的“execute only”版本。

![7_sOafDTyz4suHS6Lk.png](https://image.3001.net/images/20180705/15307760029941.png!small)

![888.png](https://image.3001.net/images/20180705/15307760604691.png!small)

我们可以将ACCDE作为钓鱼时的payload添加至邮件或链接当中。我们可以创建MAM快捷方式，它将远程链接到我们的ACCDE文件并通过网络运行其中的内容。

确保ACCDE文件已打开，单击鼠标左键并将宏拖到桌面上。这将为我们创建一个可以修改的初始.MAM文件。用你喜欢的编辑器或记事本打开它，看看我们有什么需要修改的地方。

![9_HD2ZKqc7GD_9xQKZ.png](https://image.3001.net/images/20180705/15307760861052.png!small)![10_XQFDrsuDAbDfYOc2.png](https://image.3001.net/images/20180705/15307760879679.png!small)

正如你所看到的，快捷方式的属性并不多。唯一需要我们更改的就是DatabasePath变量，指定我们远程托管地址路径。我们可以通过SMB或Web托管ACCDE文件。通过SMB托管可以实现双重目的，捕获凭据以及允许端口445离开目标网络。在本文中，我将通过http演示如何做到这一点。

## 钓鱼

在远程主机上，使用首选的Web托管方法提供ACCDE文件。

![11_tPxgST_pislvMTqJ.png](https://image.3001.net/images/20180705/15307761075319.png!small)

编辑.MAM文件以指向Web服务器上托管的ACCDE文件。

![12_pT9uoc9AWLWtamPL.png](https://image.3001.net/images/20180705/15307761231870.png!small)

现在我们的任务是将MAM
payload传送给我们的目标。一些提供商默认阻止MAM文件和Outlook，因此在这种情况下，我们会向目标发送钓鱼链接，并且只会在我们的web服务器上托管我们的MAM文件，或者你也可以使用Apache
mod_rewrite进行一些重定向操作，详细说明请[点击这里](https://twitter.com/bluscreenofjeff)。

一旦目标用户点击了我们的钓鱼链接（在使用Edge浏览器的情况下），系统将会提示他们打开或保存文件。

![13_ZCQN8Ve8_8JH2rJR.png](https://image.3001.net/images/20180705/15307761461112.png!small)

接着，系统会再次向用户弹出安全警告提示框。

![14_mkbHr67nPF32n7dK.png](https://image.3001.net/images/20180705/1530776165494.png!small)

最后，系统还会警告一次，并将向用户显示远程托管主机的IP或域名（希望会有说服力）。而在此之后将不会出现任何的[安全警告](https://support.office.com/en-us/article/what-is-protected-view-d6f09ac7-e6b9-4495-8e43-2bbcdbcb6653)，以及阻止此macro payload运行的情况。

![15_GdC88BxbdiMra-v5.png](https://image.3001.net/images/20180705/15307761905043.png!small)

用户单击“ Open”后，我们的代码就会被执行。

![16.png](https://image.3001.net/images/20180705/15307762422597.png!small)

虽然这当中出现了好几次的安全提示，但对于毫无戒心的不知情用户而言，也很容易成功。此外，我们还可以结合一些社会工程学的技巧，以达到我们的最终目的。

## OPSEC

在渗透测试的收尾阶段，我们不能忘的一件事就是擦干净可能遗留在目标系统上的痕迹。那么针对我们的这个payload在系统执行后，又会留下些什么蛛丝马迹呢？让我们通过procmon一探究竟。

![17_6bG2W1VN_UKX2Rif.png](https://image.3001.net/images/20180705/15307762621292.png!small)

第一个值得我们注意的条目是“CreateFile”调用，它执行上图所示命令。查找用于命令行审计的“ShellOpenMacro”字符串。

接下来，我们来观察下从本地计算机保存并被执行的远程ACCDE文件。虽然看起来好像我们的payload是远程调用的，但它却被下载到了“%APPDATA%\Local\Microsoft\Windows\INetCache\Content.MSO\95E62AFE.accde\PopCalc.accde”中。因此，一定要格外注意对该文件的清理。

![18_umOwr04AEThzixcT.png](https://image.3001.net/images/20180705/15307762998020.png!small)

![19_ZLW0cCmsk9WWokCh.png](https://image.3001.net/images/20180705/15307763189554.png!small)

## 缓解措施

在Microsoft Office 2016中，你可以启用GPO以阻止来自网络中的宏执行或为每个办公产品设置以下注册表项。

**Computer\HKEY_CURRENT_USER\Software\Microsoft\Office\16.0\Access\Security\blockcontentexecutionfrominternet
= 1**

**![20_VIFHAFijZuzM3Q9x.png](https://image.3001.net/images/20180705/15307763424289.png!small)**

如果用户进行了此项设置后，钓鱼程序将会被拒绝执行。需要注意的是，即使宏被阻止了，MAM文件仍会向外pull down
Access文件。所以，目标用户仍将会知道你是通过smb接收执行或窃取凭据的。

##
![21_jNCk4oCV17GnWTvx.png](https://image.3001.net/images/20180705/15307763659771.png!small)

## 总结

本文我向大家展示了，如何使用Microsoft Access
Macro快捷方式进行钓鱼的方法和步骤，以及后续痕迹的查找和清除还有缓解措施。希望通过这篇文章，能为你提供一个好的钓鱼思路，以及提高你们的安全防范意识。

 *******参考来源：[specterops](https://posts.specterops.io/phishing-tales-microsoft-access-macro-mam-shortcuts-c0bc3f90ed62)， FB小编 secist
编译，转载请注明来自FreeBuf.COM**

