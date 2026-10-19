**在之前的两篇文章中，我已经教大家如何使用证书加解密文件，但总的来说操作过程还是有些繁杂。今天我将为你们提供一个文件加密工具，来自动化的帮我们完成这些过程。关于证书问题，大家也不必担心。该工具会询问你是否有证书，如果没有它将会被自动创建。**

## EncryptFiles.ps1（无证书操作）

当你第一次下载该工具并运行它时，它会询问你是否已有证书。这里我没有任何的证书。

![EncryptFiles.ps1](https://image.3001.net/images/20180614/15289299698260.png!small)

按N并输入证书名称。随后，证书将被创建...

![EncryptFiles.ps1](https://image.3001.net/images/20180614/15289299816230.png!small)

你必须为pfx文件输入一个密码。为了保证你的安全性，这款工具会强制你备份新创建的证书。

![EncryptFiles.ps1](https://image.3001.net/images/20180614/15289299958736.png!small)

现在输入你想要加密文件的路径。之后，用记事本打开该文件，可以看到你的文件内容已被加密。

![EncryptFiles.ps1](https://image.3001.net/images/20180614/15289300088245.png!small)

## EncryptFiles.ps1（有证书操作）

如果你已经拥有了证书，那么创建新自签名证书这步将会被跳过。

按Y后，会打开一个窗口，选择你的证书。一定要注意不要选错。证书必须有私钥，并且必须设计用于文件加密，否则会出错。

![EncryptFiles.ps1](https://image.3001.net/images/20180614/15289300268708.png!small)

## 证书

前面忘说了，相信我你会是这个星球上唯一能够解密你文件的人，因为只有你的手中拥有证书私钥。 打开certmgr.msc并查看你的证书。

![EncryptFiles.ps1](https://image.3001.net/images/20180614/1528930041661.png!small)

那么证书备份存放在哪？不用着急，你可以在你的家目录中找到它。

    
    
    Get-ChildItem $home

![EncryptFiles.ps1](https://image.3001.net/images/20180614/15289300588685.png!small)

建议大家将它尽快保存到U盘或其它外部存储设备上，这样会更安全！

## 解密

如果你想解密文件，操作也非常的简单。使用Unprotect-CmsMessage命令即可解密。

    
    
    Unprotect-CmsMessage -Path C:\Temp\passwords.txt

##
![EncryptFiles.ps1](https://image.3001.net/images/20180614/15289300746543.png!small)

## 下载

[EncryptFiles.ps1](https://patrick6649.files.wordpress.com/2018/06/encryptfiles.zip)

## 相关文章

> [PowerShell：使用证书（公钥/私钥）加解密数据](https://sid-500.com/2017/10/29/powershell-> encrypt-and-decrypt-data/)
>
> [PowerShell：加密并存储你的密码将其用于远程验证（Protect-> CmsMessage）](https://sid-500.com/2018/02/24/powershell-encrypt-and-store-> your-passwords-and-use-them-for-remote-authentication-protect-cmsmessage/)

 ** *参考来源：[sid-500](https://sid-500.com/2018/06/11/encryptfiles-ps1-tool-for-encrypting-files-with-powershell/)，FB小编 secist 编译，转载请注明来自FreeBuf.COM**

