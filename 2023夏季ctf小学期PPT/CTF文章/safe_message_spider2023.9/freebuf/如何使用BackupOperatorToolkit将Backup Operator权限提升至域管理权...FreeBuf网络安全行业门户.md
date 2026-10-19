![](https://image.3001.net/images/20230727/1690459924_64c25f146a0b574f5f4a4.png!small)  

## 关于BackupOperatorToolkit

BackupOperatorToolkit是一款针对域安全的强大工具，该工具引入了多种不同的技术，可以帮助广大研究人员从Backup
Operator用户权限提权至域管理员权限。

## 工具下载

广大研究人员可以直接使用下列命令将该项目源码克隆至本地，并自行完成项目构建：

    
    
    git clone https://github.com/improsec/BackupOperatorToolkit.git

除此之外，我们也可以直接访问该项目的【[
_Releases页面_](https://github.com/improsec/BackupOperatorToolkit/releases/tag/release)】下载该工具的与编译版本。

## 工具使用

该工具简称BOT，并且拥有四种不同的操作模式。

在运行该工具之前，请先运行下列命令：

    
    
    runas.exe /netonly /user:domain.dk\backupoperator powershell.exe

### 服务模式

服务模式会在远程主机上创建一个服务，该服务将在主机重新启动时执行。

该服务是通过修改远程注册表创建的，这个操作通过将“REG_OPTION_BACKUP_RESTORE”值传递给RegOpenKeyExA和RegSetValueExA来实现。

需要注意的是，我们无法立即执行服务，因为服务控制管理器数据库“SERVICES_ACTIVE_database”会在启动时加载到内存中，并且只能使用本地管理员权限进行修改：

    
    
    .\BackupOperatorToolkit.exe SERVICE \\PATH\To\Service.exe \\TARGET.DOMAIN.DK SERVICENAME DISPLAYNAME DESCRIPTION

![](https://image.3001.net/images/20230727/1690459984_64c25f503bc0753b068ce.png!small)

### DSRM模式

DSRM模式会将在“HKLM\SYSTEM\CURRENTCONTROLET\CONTROL\LSA”中找到的DsrmAdminLogonBehavior注册表项设置为0、1或2。

> 将该值设置为0将只允许在恢复模式下使用DSRM帐户。
>
> 将该值设置为1将允许在目录服务服务停止且NTDS解锁时使用DSRM帐户。
>
> 将该值设置为2将允许DSRM帐户与网络身份验证（如WinRM）一起使用。

如果使用了DUMP模式，并且DSRM帐户已离线破解，请将该值设置为2，并使用将成为本地管理员的DSRM帐户登录到域控制器：

    
    
    .\BackupOperatorToolkit.exe DSRM \\TARGET.DOMAIN.DK 0||1||2

![](https://image.3001.net/images/20230727/1690460009_64c25f6951c997b10d9a3.png!small)

### DUMP模式

DUMP模式会式将SAM、SYSTEM和SECURITY配置单元转储到远程主机上的本地路径，或将文件上传到网络共享。

一旦配置单元被转储，我们就可以使用域控制器哈希进行PtH，破解DSRM并启用网络身份验证，或者可能使用转储中的另一个帐户进行身份验证：

    
    
    .\BackupOperatorToolkit.exe DUMP \\PATH\To\Dump \\TARGET.DOMAIN.DK

![](https://image.3001.net/images/20230727/1690460024_64c25f78ee8fd4b095571.png!small)

### IFEO模式

IFEO模式（图像文件执行选项）将使我们能够在特定进程终止时运行应用程序。这可能会在SERVICE模式之前授权拿到Shell，以防目标主机被大量使用且很少重新启动：

    
    
    .\BackupOperatorToolkit.exe IFEO notepad.exe \\Path\To\pwn.exe \\TARGET.DOMAIN.DK

![](https://image.3001.net/images/20230727/1690460040_64c25f88f12db0d760be4.png!small)

![](https://image.3001.net/images/20230727/1690460049_64c25f91336fa66eb594f.png!small)

![](https://image.3001.net/images/20230727/1690460056_64c25f98b2f80b836b647.png!small)

![](https://image.3001.net/images/20230727/1690460064_64c25fa029d39f65cfbd4.png!small)

## 项目地址

 **BackupOperatorToolkit** ：【[
_GitHub传送门_](https://github.com/improsec/BackupOperatorToolkit)】

## 参考资料

> [
> _https://github.com/mpgn/BackupOperatorToDA_](https://github.com/mpgn/BackupOperatorToDA)

