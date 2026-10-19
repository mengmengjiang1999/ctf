![](https://image.3001.net/images/20210904/1630762485_613375f57cb805ed286cb.png!small)

## 关于PowerShellArmoury

PowerShellArmoury是一款专为渗透测试人员、红蓝队成员或其他信息安全技术人员设计的PowerShell武器库。这个武器库提供了多种PowerShell工具，并且还允许我们下载各种PowerShell脚本，然后将其存储至一个加密文件之中。

在使用PowerShellArmoury的过程中，你无需担心更新Rubeus、PowerView之类的问题，我们只需要创建一个配置文件，或者使用该工具附带的默认配置文件即可。除此之外，整个PowerShellArmoury武器库都是加密的，并且自带了AMSI绕过功能，因此无需担心反病毒产品的检测。

注意：你必须提供提供有效的GitHub帐户以及个人访问令牌，以便脚本能够正确使用GitHub API。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/cfalta/PowerShellArmoury.git

## 配置参考

配置文件必须为有效的JSON格式文件，该文件由一个包含多个对象的单一数组组成，其中每一个对象都可以被解析为一个单一的脚本源，每一个对象都包含下列属性：

> Name：脚本名称；
>
> URL：脚本内容的位置来源，支持本地（C：）或网络源（https://）；
>
> Type：武器库创建者的脚本位置，可以为GitHub、WebDownloadSimple或LocalFile；

## 参数选项

> -Path：武器库文件路径，默认为“.\MyArmoury.ps1”。
>
> -FromFile：直接从本地目录或文件加载PowerShell脚本。
>
> -Config：JSON配置文件路径。
>
> -Password：用于加密武器库脚本的密码，如果不提供密码，脚本将会生成一个随机密码。
>
> -Sale：用于生成AES加密密钥的Salt值，如果不提供Salt值，脚本将会生成一个随机Salt。
>
> -OmitPassword：这个选项将会移除最终武器库脚本中的明文密码。
>
> -ValidateOnly：该选项配合“-Config”使用可以直接验证JSON配置文件中的语句有效性。
>
> -Use3DES：使用3DES加密算法。
>
> -EnhancedArmour：设置脚本运行需要受保护的PowerShell进程。

具体可查看完整的帮助手册。（man -full New-PSArmoury）。

## 工具使用样例

下列命令可以使用默认配置创建一个武器库脚本，并使用默认的样本配置文件：

    
    
    . .\New-PSArmoury.ps1
    
    New-PSArmoury -Config .\PSArmoury.json

上述命令将会在当前工作目录下创建一个名为“MyArmoury.ps1”的加密.ps1文件。用于加密的密码和Salt值将会随机生成，并写入一个明文文件中。

你可以直接使用下列命令在当前会话中加载武器库脚本：

    
    
    cat -raw .\MyArmoury.ps1 | iex

整个过程中PowerShellArmoury将会做以下几件事情：

> 加载所有的加密PowerShell函数至当前会话中；
>
> 禁用AMSI；
>
> 禁用控制台历史记录；
>
> 揭秘所有内容，并pipe至iex；

此时，所有的PowerShell代码可以使用，我们可以像往常一样直接调用：

    
    
    Invoke-Rubeus -Command "kerberoast /stats"
    
    Invoke-Bloodhound
    
    Get-DomainGroupMember -Identity "Domain Admins" -Recurse

如果你不记得具体的代码，可以直接使用下列命令进行简介调用：

    
    
    Get-PSArmoury

## 项目地址

PowerShellArmoury：【[
_GitHub传送门_](https://github.com/cfalta/PowerShellArmoury)】

## 参考资料

> [ _https://gist.github.com/rasta-> mouse/af009f49229c856dc26e3a243db185ec_](https://gist.github.com/rasta-> mouse/af009f49229c856dc26e3a243db185ec)
>
> [ _https://cyberstoph.org/posts/2019/12/evading-anti-virus-with-powershell-> armoury/_](https://cyberstoph.org/posts/2019/12/evading-anti-virus-with-> powershell-armoury/)
>
> [ _https://cyberstoph.org/posts/2020/02/psarmoury-1.4-now-with-even-more-> armour/_](https://cyberstoph.org/posts/2020/02/psarmoury-1.4-now-with-even-> more-armour/)
>
> [ _http://mywebserver.com/file.ps1_](http://mywebserver.com/file.ps1)
>
> [
> _https://github.com/cfalta/PoshRandom_](https://github.com/cfalta/PoshRandom)
>
> [ _https://docs.github.com/en/github/authenticating-to-github/creating-a-> personal-access-token_](https://docs.github.com/en/github/authenticating-to-> github/creating-a-personal-access-token)

