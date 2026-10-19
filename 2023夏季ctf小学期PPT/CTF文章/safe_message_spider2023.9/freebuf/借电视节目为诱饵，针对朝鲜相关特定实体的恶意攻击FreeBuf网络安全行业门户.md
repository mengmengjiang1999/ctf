研究人员发现名为 CNA[Q].doc 的恶意 Word 文档一直在通过 FTP 泄露用户凭据。该恶意文档伪装成新加坡亚洲新闻台 CNA
的电视节目采访稿，文档的密码随着电子邮件一同分发。

![image.png-65.7kB](https://image.3001.net/images/20221128/1669566721_63839101c215d8c4530bc.png!small)受密码保护的
Word 文档

文档与此前发现的恶意文件类似，也包含与朝鲜相关特定实体的信息，并且包含恶意 VBA 宏代码。

![image.png-181.5kB](https://image.3001.net/images/20221128/1669566722_63839102771ebc569d29b.png!small)Word
文件内容

![image.png-88.2kB](https://image.3001.net/images/20221128/1669566723_638391032190383db4685.png!small)文件属性

打开文档时并不会触发宏代码执行，但文档会弹出一个消息框提醒用户在打开时要启用宏。用户点击“启用内容”后，就会执行文件中嵌入的 VBA 宏代码。

![image.png-80.1kB](https://image.3001.net/images/20221128/1669566723_63839103f2123b7eeee08.png!small)部分宏代码

![image.png-128.6kB](https://image.3001.net/images/20221128/1669566724_63839104b59bcb4d48cbd.png!small)打开时的消息框

VBA 宏代码中包含 Document_Open 函数，使恶意宏代码能够自动执行。执行的宏代码与此前分析的类似，也是经过混淆处理的，在 %appdata%
文件夹中创建并执行一个 VBScript 文件 tmp.pip。

![image.png-306.6kB](https://image.3001.net/images/20221128/1669566725_63839105b46802c671a94.png!small)自动执行的恶意
VBA 宏代码

执行 tmp.pip 时，它会创建 Defender.log、DefenderUpdate.lba 和 Ahnlab.lnk。然后将
DefenderUpdate.lba 的文件扩展名改为 bat 并执行该文件。

文件名| 描述  
---|---  
DefenderUpdate.lba| 用于执行 Ahnlab.lnk  
Ahnlab.lnk| 调用 PowerShell 执行 Defender.log  
Defender.log| 下载并执行 hxxp://okihs.mypressonline[.]com/bb/bb.txt  
  
bb.txt 类似于之前发现的 ng.txt，如下所示：

![image.png-161.9kB](https://image.3001.net/images/20221128/1669566726_63839106c10b5c39ce436.png!small)

脚本代码

该脚本主要：

> 收集并回传失陷主机信息
>
> 通过 hxxp://okihs.mypressonline[.]com/bb/bb.down 下载恶意文件

收集的信息与此前一致：

执行命令| 收集信息  
---|---  
GetFolderPath(“Recent”)| 最近的文件夹路径  
dir $env:ProgramFiles| ProgramFiles 文件夹信息  
dir “C:\Program Files (x86)| C:\Program Files (x86) 文件夹信息  
systeminfo| 系统信息  
  
与此前版本的 ng.down 相比，bb.down 新增了使用 FTP 来泄露用户信息，创建 LNK 文件（Ahnlab.lnk）、更改 Office
安全设置、键盘记录等功能仍然是一致的。

![image.png-297.9kB](https://image.3001.net/images/20221128/1669566727_63839107aed3ba2548e0e.png!small)新添加的功能代码

bb.down 在执行时会执行 main 函数，在 %LOCALAPPDATA%\Google\Chrome\User Data 与
%LOCALAPPDATA%\Microsoft\Edge\User Data 文件夹中读取特定文件并将 encrypted_key 保存在
%APPDATA%\masterkey.txt 中。随后，通过 FTP 将 masterkey.txt 上传到
jojoa.mypressonline[.]com 中，用于解密后续收集的与浏览器有关的文件。

上传 encrypted_key 成功后，寻找以下文件并复制到 %APPDATA% 文件夹中，收集与浏览器相关的信息。

路径| 转存路径  
---|---  
Files containing ‘Login Data’ within %LOCALAPPDATA%\Google\Chrome\User Data|
%APPDATA%\LoginData_Chrome[n]  
Files containing ‘Login Data For Account’ within
%LOCALAPPDATA%\Google\Chrome\User Data| %APPDATA%\LoginForAccount_Chrome[n]  
Files containing ‘Cookies’ within %LOCALAPPDATA%\Google\Chrome\User Data|
%APPDATA%\Cookies_Chrome[n]  
Files containing ‘Login Data’ within %LOCALAPPDATA%\Microsoft\Edge\User Data|
%APPDATA%\LoginData_msedge[n]  
Files containing ‘Login Data For Account’ within
%LOCALAPPDATA%\Microsoft\Edge\User Data| %APPDATA%\LoginForAccount_msedge[n]  
Files containing ‘Cookies’ within %LOCALAPPDATA%\Microsoft\Edge\User Data|
%APPDATA%\Cookies_msedge[n]  
  
这些文件以 KLoginData 和 KCookie 等文件名上传到 FTP 服务器：

> 登录数据：jojoa.mypressonline[.]com/KLoginData_[Chrome/msedge][n]
>
> 账户数据：jojoa.mypressonline[.]com/KLoginForAccount_[Chrome/msedge][n]
>
> Cookie：jojoa.mypressonline[.]com/KCookie_[Chrome/msedge][n]

为了规避检测与分析，攻击者还删除了
%APPDATA%\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt，该文件是保存
PowerShell 命令执行的日志。

## IOC

> 59be2b9a3e33057b3d80574764ab0952  
> 89d972f89b336ee07733c72f6f89edc5  
> 8785b8e882eef125dc527736bb1c5704  
> okihs.mypressonline[.]com  
> jojoa.mypressonline[.]com

## 参考来源

> [ASEC](https://asec.ahnlab.com/en/42529/)

