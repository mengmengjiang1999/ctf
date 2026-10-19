**Responder下载[链接](a%20href=)，Responder工具可以毒化LLMNR和NBT-NS请求。**

 **假设我们已连接到Windows Active Directory环境，当网络上的设备尝试用LLMNR和NBT-NS请求来解析目标机器时，Responder就会伪装成目标机器。当受害者机器尝试登陆攻击者机器，responder就可以获取受害者机器用户的NTLMv2哈希值。**

本文我们将讨论2种攻击。

> 1.获取NTLMv2哈希值，并使用Hashcat密码破解工具破解。
>
>
> 2.使用Responder和Multirelay.py脚本，脚本负责执行NTMLMv2哈希值中继到“已禁用SMB签名”的机器上。如果中继成功，就可以访问目标机器。

## 捕获NTLMv2哈希值

通过使用参数`-I`指定机器的以太网接口来运行Responder，这个例子中使用的接口是`eth0`。命令:`python Responder.py -I
<Interface_card_name>`例如`python Responder.py -I eth0`  
![Windows环境中使用Responder获取NTLMv2哈希并利用](https://image.3001.net/images/20190118/1547798319_5c41872f84de1.png!small)Responder监听模式：  
![Windows环境中使用Responder获取NTLMv2哈希并利用](https://image.3001.net/images/20190118/1547798326_5c418736b681e.png!small)如果网络中的任何用户试图访问共享哪个机器没有IP或用户类型共享名称不正确，该机器将触发LLMNR请求到网络，Responder将通过说我是那台机器来回答该请求，请提供给我NTLMv2哈希并访问资源。  
![Windows环境中使用Responder获取NTLMv2哈希并利用](https://image.3001.net/images/20190118/1547798333_5c41873ddff74.png!small)这里，用户`“box1”`（机器`IP
192.168.56.101`）正在尝试访问名称为`“pwned68”`的共享分区。当机器触发LLMNR请求时，Responder响应该请求并从域`“DC2”`捕获用户`“box1”`的NTLMv2哈希值。然后，我们需要破解此哈希以获取纯文本密码。`“Hashcat”`是执行最快的hashcracking的绝佳工具。它支持CPU/GPU散列破解，并支持多种哈希格式。Hahcat官方下载[网站](a%20href=),密码字典[下载地址](a%20href=)  
![Windows环境中使用Responder获取NTLMv2哈希并利用](https://image.3001.net/images/20190118/1547798356_5c418754d78f9.png!small)在获得明文密码后，我们可以登录到Windows域上的其他计算机，来确定我们是否可以在其他计算机上访问任何敏感信息。

## 获取shell访问权限

Responder是少有的可以通过中继NTLMv2哈希来获取网络中机器的shell。如果捕获哈希的用户在目标机器上具有`“administrator”`访问权限，则捕获的哈希可以帮助我们获得shell访问。普通域用户哈希不会帮助我们在机器上获得shell访问权限。在我给出的案例中，其中一个管理员用户试图访问一个不存在的共享，Responder投毒成功，然后`Multirelay.py`脚本使用捕获的NTLMv2哈希登录到Windows域网络的一部分机器。为了设置这些，需要修改`Responder.conf`文件。打开`Responder.conf`文件，将SMB和HTTP的值改为off。这样responder就不会获取哈希值，而是`Multirelay.py`来完成这一任务。  
![Windows环境中使用Responder获取NTLMv2哈希并利用](https://image.3001.net/images/20190118/1547798364_5c41875ca5727.png!small)现在运行`RunFinger.py`脚本来识别网络中已将`“SMB
signing”`设置为`“False”`的HOST计算机，因为我们只能对那些没有将`“SMB
signing”`设置为`“True”`的计算机执行攻击。该脚本位于Responder的`”tools“`目录中，首先进入该目录。`RunFinger.py`脚本需要IP范围，它将检查活动主机是否启用了SMB签名。运行`RunFinger.py`脚本的命令是：`python
RunFinger.py -i IP_Range`比如:`python RunFinger.py -i 192.168.56.100-200`  
![Windows环境中使用Responder获取NTLMv2哈希并利用](https://image.3001.net/images/20190118/1547798371_5c4187633e612.png!small)脚本的输出将是这样的  
![Windows环境中使用Responder获取NTLMv2哈希并利用](https://image.3001.net/images/20190118/1547798376_5c418768c03e8.png!small)这里只有3个机器。其中一个是域名控制器机器，另一个是Windows域中的Windows
7主机。IP为192.168.56.101的机器SMB
Signing未启用。因此可以对该机器进行NTMLv2哈希中继攻击。在发现了这些机器后，可以设置responder和`multirelay.py`脚本来访问SMB
Signing未启用的机器。运行下面的命令可以开启Responder和`Multirelay.py`。在第一个终端上，开启responder：`python
Responder.py -I <interface_card>`在第二个终端中，运行Multirelay.py`python MultiRelay.py
-t <target_machine_IP> -u ALL`  
![Windows环境中使用Responder获取NTLMv2哈希并利用](https://image.3001.net/images/20190118/1547798383_5c41876f810fd.png!small)这两个脚本都是这样的  
![Windows环境中使用Responder获取NTLMv2哈希并利用](https://image.3001.net/images/20190118/1547798390_5c418776d899d.png!small)域中的admin用户会尝试访问不存在的share，responder会污染响应消息。`Multirelay.py`会通过获取NTLMv2哈希值来完成其他动作，并与目标机器相关联。成功中继后就可以获取目标机器上的shell访问权限。  
![Windows环境中使用Responder获取NTLMv2哈希并利用](https://image.3001.net/images/20190118/1547798397_5c41877dcaab9.png!small)一旦我们获得shell访问权限，我们也可以执行其他工作，其中一个正在加载“Mimikatz”，它可以执行诸如转储当前登录用户的纯文本密码/哈希或从SAM文件中获取本地用户哈希等任务。  
![Windows环境中使用Responder获取NTLMv2哈希并利用](https://image.3001.net/images/20190118/1547798404_5c4187844d6a1.png!small)
***参考来源[github](https://github.com/incredibleindishell/Windows-AD-environment-related/tree/master/Responder)，由周大涛编译，转载请注明来自FreeBuf.COM**

