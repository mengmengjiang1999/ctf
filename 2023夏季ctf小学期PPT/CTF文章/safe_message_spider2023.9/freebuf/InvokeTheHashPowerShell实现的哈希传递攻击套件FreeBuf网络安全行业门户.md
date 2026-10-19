**Invoke-TheHash项目是一个基于.Net TCPClient，通过把NTLM
hash传递给NTLMv2身份验证协议来进行身份验证的攻击套件，且执行时客户端不需要本地管理员权限。**

## 安装环境

PowerShell 2.0及以上。

## 导入

    
    
    Import-Module ./Invoke-TheHash.psd1

 **或**

    
    
    . ./Invoke-WMIExec.ps1      
    . ./Invoke-SMBExec.ps1      
    . ./Invoke-SMBEnum.ps1      
    . ./Invoke-SMBClient.ps1      
    . ./Invoke-TheHash.ps1

## Invoke-WMIExec

作用：WMI命令执行。

###  **参数：**

 **Target** \- 目标主机名或IP地址。

 **Username** \- 用于身份验证的用户名。

 **Domain** \- 用于身份验证的域。本地帐户或在用户名后使用@domain时不需要此参数。

 **Hash** \- 用于身份验证的NTLM密码哈希（格式： LM:NTLM 或 NTLM）。

**Command** -在目标上执行的命令。如果命令未指定，则将检查用户名和哈希是否可以访问目标上的WMI。

 **Sleep** \- 默认 = 10毫秒：设置开始 - 睡眠值（以毫秒为单位）。

###  **示例：**

    
    
    Invoke-WMIExec -Target 192.168.100.20 -Domain TESTDOMAIN -Username TEST -Hash F6F38B793DB6A94BA04A52F1D3EE92F0 -Command "command or launcher to execute" -verbose

###  **截图：**

**![1.png](https://image.3001.net/images/20180908/1536369931_5b93250bb6223.png!small)**

## Invoke-SMBExec

作用：SMB（PsExec）命令执行，支持SMB1，SMB2.1，无论SMB有无签名。

###  **参数：**

 **Target** \- 目标主机名或IP地址。

 **Username** \- 用于身份验证的用户名。

 **Domain** \- 用于身份验证的域。本地帐户或在用户名后使用@domain时不需要此参数。

 **Hash** \- 用于身份验证的NTLM密码哈希（格式： LM:NTLM 或 NTLM）。

 **Command** \- 在目标上执行的命令。如果命令未指定，则将检查用户名和哈希是否可以访问目标上的SCM。

 **CommandCOMSPEC** \- 默认=Enabled：将%COMSPEC% /C预先添加到命令。

 **Service** \- 默认 = 20字符（随机）：要在目标上创建和删除的服务名称。

 **Sleep** \- 默认 = 150毫秒：设置开始 - 睡眠值（以毫秒为单位）。

 **Version** \- 默认 = Auto: (Auto,1,2.1) 强制SMB版本。默认执行SMB版本协商，如果目标支持，则使用SMB2.1。

###  **示例1：**

    
    
    Invoke-SMBExec -Target 192.168.100.20 -Domain TESTDOMAIN -Username TEST -Hash F6F38B793DB6A94BA04A52F1D3EE92F0 -Command "command or launcher to execute" -verbose

###  **示例2：**

检查目标上的SMB签名要求。Invoke-SMBExec -Target 192.168.100.20

###  **截图：**

**![2.png](https://image.3001.net/images/20180908/1536369945_5b932519dfa5f.png!small)**

## Invoke-SMBEnum

作用：通过签名或未签名的SMB2.1执行用户，组，NetSession和共享枚举任务。

###  **参数：**

###  **Target** \- 目标主机名或IP地址。

###  **Username** \- 用于身份验证的用户名。

###  **Domain** \- 用于身份验证的域。本地帐户或在用户名后使用@domain时不需要此参数。

###  **Hash** \- 用于身份验证的NTLM密码哈希（格式： LM:NTLM 或 NTLM）。

###  **Action** \- （全部，组，NetSession，共享，用户）默认 = share：枚举共享。

###  **Group** \- 默认 = Administrators：枚举组。

###  **Sleep** \- 默认 = 150毫秒：设置开始 - 睡眠值（以毫秒为单位）。

###  **Version** \- 默认 = Auto: (Auto,1,2.1)
强制SMB版本。默认执行SMB版本协商，如果目标支持，则使用SMB2.1。

###  **示例：**

    
    
    Invoke-SMBEnum -Target 192.168.100.20 -Domain TESTDOMAIN -Username TEST -Hash F6F38B793DB6A94BA04A52F1D3EE92F0 -verbose

###  **截图：**

**![3.PNG](https://image.3001.net/images/20180908/1536369960_5b932528ec05d.png!small)**

## Invoke-SMBClient

SMB client同时支持SMB2.1和SMB签名。主要提供SMB文件共享功能，以使用没有远程命令执行权限的哈希。此外，它还可用于staging
payload并与Invoke-WMIExec和Invoke-SMBExec一起使用。请注意，Invoke-SMBClient是基于.NET
TCPClient的，因此不使用Windows SMB client.。Invoke-SMBClient比Windows SMB client要慢很多。

###  **参数：**

 **Username** \- 用于身份验证的用户名。

 **Domain** \- 用于身份验证的域。本地帐户或在用户名后使用@domain时不需要此参数。

 **Hash** \- 用于身份验证的NTLM密码哈希（格式： LM:NTLM 或 NTLM）。

 **Action** \- 默认 = List: 执行(List/Recurse/Delete/Get/Put) 操作。

List：列出目录内容。

Recurse：列出目录和所有子目录内容。

Delete：删除文件。

Get：下载文件。

Put：上传文件并设置创建，访问和上次写入时间以匹配源文件。

 **Source（源）**

List 和 Recurse：目录的UNC路径。

Delete：文件的UNC路径。

Get：文件的UNC路径。

Put：要上传的文件。如果未指定完整路径，则该文件必须位于当前目录下。使用"Modify"开关时，“Source”必须是字节数组。

 **Destination（目标）**

List 和 Recurse：未使用。

Delete：未使用。

Get：如果使用，value将是下载文件的新文件名。如果未指定完整路径，则将在当前目录下创建该文件。

Put：上传文件的UNC路径。必须指定文件名。

 **Modify**

List and Recurse：输出一个由目录内容组成的对象。

Delete：未使用。

Get：输出下载文件的字节数组，而不是将文件写入磁盘。建议仅将其用于较小的文件，并将输出发送到一个变量。

Put：将字节数组上传到新的目标文件。

 **NoProgress** \- 不显示上传和下载进度条。

 **Sleep** \- 默认 = 100毫秒：设置开始 - 睡眠值（以毫秒为单位）。

 **Version** \- 默认 = Auto: (Auto,1,2.1) 强制SMB版本。默认执行SMB版本协商，如果目标支持，则使用SMB2.1。

###  **示例1：**

列出root共享目录内容。

    
    
    Invoke-SMBClient -Domain TESTDOMAIN -Username TEST -Hash F6F38B793DB6A94BA04A52F1D3EE92F0 -Source \\server\share -verbose

###  **示例2：**

从root开始递归列出共享内容。

    
    
    Invoke-SMBClient -Domain TESTDOMAIN -Username TEST -Hash F6F38B793DB6A94BA04A52F1D3EE92F0 -Action Recurse -Source \\server\share

###  **示例3：**

递归列出share subdirectory目录下的内容，并且只将内容输出返回到一个变量。

    
    
    $directory_contents = Invoke-SMBClient -Domain TESTDOMAIN -Username TEST -Hash F6F38B793DB6A94BA04A52F1D3EE92F0 -Action Recurse -Source \\server\share\subdirectory -Modify

###  **示例4：**

删除share目录中的一个文件。

    
    
    Invoke-SMBClient -Domain TESTDOMAIN -Username TEST -Hash F6F38B793DB6A94BA04A52F1D3EE92F0 -Action Delete -Source \\server\share\file.txt

###  **示例5：**

删除share subdirectory目录中的文件。

    
    
    Invoke-SMBClient -Domain TESTDOMAIN -Username TEST -Hash F6F38B793DB6A94BA04A52F1D3EE92F0 -Action Delete -Source \\server\share\subdirectory\subdirectory\file.txt

###  **示例6：**

从share目录中下载一个文件。

    
    
    Invoke-SMBClient -Domain TESTDOMAIN -Username TEST -Hash F6F38B793DB6A94BA04A52F1D3EE92F0 -Action Get -Source \\server\share\file.txt

###  **示例7：**

从share subdirectory目录中下载文件并设置新的文件名。

    
    
    Invoke-SMBClient -Domain TESTDOMAIN -Username TEST -Hash F6F38B793DB6A94BA04A52F1D3EE92F0 -Action Get -Source \\server\share\subdirectory\file.txt -Destination file.txt

###  **示例8：**

将文件从share目录下载到字节数组变量而不是磁盘。

    
    
    $password_file = Invoke-SMBClient -Domain TESTDOMAIN -Username TEST -Hash F6F38B793DB6A94BA04A52F1D3EE92F0 -Action Get -Source \\server\share\file.txt -Modify

###  **示例9：**

上传一个文件到share subdirectory目录。

    
    
    Invoke-SMBClient -Domain TESTDOMAIN -Username TEST -Hash F6F38B793DB6A94BA04A52F1D3EE92F0 -Action Put -Source file.exe -Destination \\server\share\subdirectory\file.exe

###  **示例10：**

从字节数组变量上传一个文件到share目录。

    
    
    Invoke-SMBClient -Domain TESTDOMAIN -Username TEST -Hash F6F38B793DB6A94BA04A52F1D3EE92F0 -Action Put -Source $file_byte_array -Destination \\server\share\file.txt -Modify

###  **截图：**

**![4.PNG](https://image.3001.net/images/20180908/1536369983_5b93253f2fa16.png!small)**

## Invoke-TheHash

作用：针对多个目标运行Invoke-TheHash。

 **参数：**

 **Type** \- 设置所需的Invoke-TheHash功能（支持SMBClient，SMBEnum，SMBExec或WMIExec）。

 **Target** \- 目标的主机名，IP地址，CIDR表示法或IP范围列表。

 **TargetExclude** \- 要从列表或目标中排除的主机名，IP地址，CIDR表示法或IP范围的列表。

 **PortCheckDisable** \-（Switch）禁用WMI或SMB端口检查。由于该功能尚未线程化，因此端口检查主要通过在尝试完全同步TCPClient连接之前，检查打开的WMI或SMB端口来提升速度。

 **PortCheckTimeout** \- 默认值 = 100：设置WMI或SMB端口检查的无响应超时时间（以毫秒为单位）。

 **Username** \- 用于身份验证的用户名。

 **Domain** \- 用于身份验证的域。本地帐户或在用户名后使用@domain时无需此参数。

 **Hash** \- 用于身份验证的NTLM密码哈希（格式： LM:NTLM 或 NTLM）。

 **Command** \- 在目标上执行的命令。如果命令未指定，则该函数将仅检查用户名和哈希是否可以访问目标上的WMI或SCM。

 **CommandCOMSPEC** \- 默认 = Enabled：仅支持SMBExec。将%COMSPEC% /C预先添加到命令。

 **Service** \- 默认 = 20字符（随机）：仅支持SMBExec。要在目标上创建和删除的服务名称。

 **SMB1** \- (Switch) 强制SMB1。仅支持SMBExec。默认执行SMB版本协商，如果目标支持，则使用SMB2。

 **Sleep** \- 默认 = WMI 10 毫秒，SMB 150 毫秒：设置启动 - 睡眠值（以毫秒为单位）。

###  **示例11：**

    
    
    Invoke-TheHash -Type WMIExec -Targets 192.168.100.0/24 -TargetsExclude 192.168.100.50 -Username Administrator -Hash F6F38B793DB6A94BA04A52F1D3EE92F0

###  **截图：**

![5.png](https://image.3001.net/images/20180908/1536369998_5b93254e1ce52.png!small)

 ***参考来源：[github](https://github.com/Kevin-Robertson/Invoke-TheHash)，FB小编
secist 编译，转载请注明来自FreeBuf.COM**

