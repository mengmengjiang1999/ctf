![20210713211509.jpg](https://image.3001.net/images/20210714/1626198931_60edd3935ada11066f265.jpg!small)

系列文章：

> [《内网渗透测试：初探远程桌面的安全问题》](https://www.freebuf.com/articles/network/276242.html)
>
> [《内网渗透测试：登录远程桌面的别样姿势》](https://www.freebuf.com/articles/network/280817.html)
>
> [《内网渗透测试：基于文件传输的 RDP
> 反向攻击》](https://www.freebuf.com/articles/network/280818.html)

## 前言

Windows 远程桌面是用于管理 Windows
服务器的最广泛使用的工具之一。管理员喜欢使用远程桌面，攻击者也喜欢使用（狗头）。在之前的文章中我们已经介绍了很多攻击远程桌面的方法，本篇文章我们继续来探究。

在渗透测试中，RDP
远程桌面连接的历史记录不可忽视，根据历史连接记录我们往往能够定位出关键的服务器。并且，当我们发现了某台主机上存在远程桌面的连接记录，我们还可以想办法获取其远程桌面登录历史的连接凭据。用于登录
RDP 远程桌面会话的凭据通常具有特权，这使它们成为红队操作期间的完美目标。

## 获取 RDP 远程桌面连接记录

获取 RDP 远程桌面的连接记录我们可以通过枚举注册表完成，但是如果想要获得所有用户的历史记录，需要逐个获得用户的 NTUSER.DAT
文件，通过注册表加载配置单元，导入用户配置信息，再进行枚举才能够实现。

### 导出当前用户的历史记录

可以通过枚举下面的注册表键值查看当前用户的历史记录：

    
    
    HKEY_CURRENT_USER\Software\Microsoft\Terminal Server Client\Servers

如下图所示，每个注册表项保存连接的服务器地址，其中的键值`UsernameHint`对应登录用户名：

![image-20210524084553447](https://image.3001.net/images/20210714/1626198931_60edd393c8955905cd1b9.png!small)

看也可以通过 PowerShell 命令行来实现，首先通过以下命令枚举指定注册表项下所有的的子项，即当前用户所连接过的所有的主机名：

    
    
    dir "Registry::HKEY_CURRENT_USER\Software\Microsoft\Terminal Server Client\Servers" -Name

![image-20210524093321775](https://image.3001.net/images/20210714/1626198932_60edd3942d9a567e38b78.png!small)

然后使用以下命令查询指定注册表项的注册表键值，即查看连接所使用的用户名：

    
    
    (Get-ItemProperty -Path "Registry::HKEY_CURRENT_USER\Software\Microsoft\Terminal Server Client\Servers\192.168.93.30").UsernameHint

![image-20210524093431912](https://image.3001.net/images/20210714/1626198932_60edd39469269f4b834ee.png!small)

下面给出一个三好学生写的枚举脚本：

    
    
    $RegPath = "Registry::HKEY_CURRENT_USER\Software\Microsoft\Terminal Server Client\Servers\"  
    $QueryPath = dir $RegPath -Name  
    foreach($Name in $QueryPath)  
    {     
    Try    
    {    
    $User = (Get-ItemProperty -Path $RegPath$Name -ErrorAction Stop | Out-Null).UsernameHint  
    Write-Host "Server:"$Name  
    Write-Host "User:"$User"`n"  
    }  
    Catch    
    {  
    Write-Host "No RDP Connections History"  
    }  
    }

### 导出已登录用户的历史记录

已登录用户的注册表信息会同步保存在`HKEY_USERS\<SID>`目录下，`<SID>`要对应每个用户的 SID：

![image-20210524085841555](https://image.3001.net/images/20210714/1626198932_60edd394aa504f187716c.png!small)

可以看到，当前系统登录三个用户，分别有三个子项。我们可以通过枚举注册表键值`HKEY_USERS\SID\Software\Microsoft\Terminal
Server Client\Servers`就能够获得已登录用户的远程桌面连接历史记录：

![image-20210524085946713](https://image.3001.net/images/20210714/1626198933_60edd3950a355ee673e67.png!small)

>
> 也就是说，如果当前主机登录了两个用户，那么这两个用户的注册表信息都会保存在`HKEY_USERS\<SID>`下。但如果第三个用户未登录，此时是无法直接获得该用户的注册表信息的，会报如下错误：
>
>
> ![image-20210524090421662](https://image.3001.net/images/20210714/1626198933_60edd3956390ae927ebf7.png!small)
>
> 也就无法直接导出该用户的远程桌面连接历史记录。

最后给出一个三好学生写的枚举脚本：

    
    
    $RegPath = "Registry::HKEY_CURRENT_USER\Software\Microsoft\Terminal Server Client\Servers\"
    $QueryPath = dir $RegPath -Name
    foreach($Name in $QueryPath)
    {   
    	Try  
    	{  
    		$User = (Get-ItemProperty -Path $RegPath$Name -ErrorAction Stop | Out-Null).UsernameHint
        		Write-Host "Server:"$Name
        		Write-Host "User:"$User"`n"
        	}
        	Catch  
        	{
    		Write-Host "No RDP Connections History"
        	}
    }

### 导出所有用户的历史记录

前面刚说了，对于未登录用户，无法直接获得注册表配置信息，那有什么解决办法？其实这里可以通过加载配置单元的方式来解决，即打开用户的 NTUSER.DAT
文件，加载配置单元导入用户配置信息，然后进行枚举。

选中 HKEY_USERS 项，“文件” —> “加载配置单元”，如下图：

![image-20210524091026247](https://image.3001.net/images/20210714/1626198933_60edd395b5016a750ebc4.png!small)

选择打开用户的 NTUSER.DAT 文件，路径为`C:\Documents and Settings\用户名\NTUSER.DAT`，这里以当前未登录的
moretz 用户为例：

![image-20210524092246927](https://image.3001.net/images/20210714/1626198933_60edd395f2e3cff260744.png!small)

接着指定一个项名称，即可在 HKEY_USERS 下读取该用户的注册表配置信息，如下图所示：

![image-20210524092404538](https://image.3001.net/images/20210714/1626198934_60edd39666b099246b8ae.png!small)

然后按照之前的路径进行枚举即可。

此外，也可以通过命令行实现加载配置单元的实例：

    
    
    Reg load HKEY_USERS\testmoretz C:\Documents and Settings\moretz\NTUSER.DAT

最后给出一个三好学生写的枚举脚本：<https://github.com/3gstudent/List-RDP-Connections-History>

## 获取 RDP 远程桌面连接凭据

一般的，就抓取凭据方面而言，很多人专注于从 lsass.exe 进程里面窃取凭据，但是 lsass.exe 通常来说已经是被 EDR
产品重点监控的进程了，因此我们自然而然的研究方向便是找到可能不太严格审查的替代方案。这就引出了我们下文中对 RDP 凭据的收集。与 lsass.exe
一样，RDP 协议相关的进程例如 svchost.exe、mstsc.exe 等也在收集凭证的范围内，并且从这些进程中收集凭据不需要管理员特权。

当我们发现目标主机中存在远程桌面连接的历史记录时，我们可以根据历史记录找到其连接过的远程桌面，并确定出关键的服务器。但光找到关键的服务器那能够啊！我们最好能够导出连接远程桌面的连接凭据，获取服务器密码。下面我们便来简单介绍几个可以导出远程桌面连接凭据的方法。

### 在凭据管理器中查看 Windows 凭据

对于那些经常使用 RDP
远程桌面连接远程服务器的用户来说，如果他不想对远程主机进行多次身份验证的话，他们可能会保存连接的详细信息，以便进行快速的身份验证。而这些凭据使用数据保护
API 以加密的形式存储在 Windows 的凭据管理器中。

![image-20210713142937250](https://image.3001.net/images/20210714/1626198934_60edd396bde65336350f4.png!small)

这些 Windows 凭据保存在磁盘上的以下位置中：

    
    
    C:\Users\<用户名>\AppData\Local\Microsoft\Credentials

我们可以用如下命令查看当前主机上保存的连接凭据：

    
    
    cmdkey /list    # 查看当前保存的凭据  
    ​  
    dir /a %userprofile%\AppData\Local\Microsoft\Credentials\*    # 遍历 Credentials 目录下保存的凭据

![image-20210713143759764](https://image.3001.net/images/20210714/1626198935_60edd397184db12b07bc4.png!small)

如上图可以看到，Credentials 目录下保存有两个历史连接凭据，但里面的凭据是加密的，要想查看还需要使用 M

