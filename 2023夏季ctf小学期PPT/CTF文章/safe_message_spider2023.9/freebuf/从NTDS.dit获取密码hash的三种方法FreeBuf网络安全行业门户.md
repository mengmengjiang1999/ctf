****

**本文我将为大家介绍一些取证工具，这些工具在渗透测试中将会对我们起到很大的帮助。例如当你提取到了大量的主机内部文件时，你可会发现其中包含如NTDS.dit和系统hive，那么你将可能需要用到下面的这些工具，来帮助你提取其中的用户信息。**

##  **Impacket-secretsdump**

Impacket是一个Python类库，用于对SMB1-3或IPv4 / IPv6
上的TCP、UDP、ICMP、IGMP，ARP，IPv4，IPv6，SMB，MSRPC，NTLM，Kerberos，WMI，LDAP等协议进行低级编程访问。
该库提供了一组工具，作为在此库的上下文中可以执行的操作示例。

 **secretsdump.py：** 实现了多种不需要在远程主机上执行任何代理的情况下转储机密数据的技术。对于SAM和LSA
Secrets（包括缓存的凭据），我们尽可能的尝试从注册表中读取，然后将hives保存在目标系统（％SYSTEMROOT％\Temp目录）中，并从那里读取其余的数据。对于DIT文件，我们使用DL_DRSGetNCChanges()方法转储NTLM哈希值，明文凭证（如果可用）和Kerberos密钥。此外，还可以通过使用smbexec/wmiexec方法执行vssadmin来转储NTDS.dit。

 **参考：**<https://www.coresecurity.com/corelabs-research/open-source-tools/impacket>

根据官方文档的说明，想要提取用户的密码哈希，我们必须获取到ntds.dit和System-hive这两个文件。如果条件满足，你可以执行以下命令：

 **impacket-secretsdump -system /root/Desktop/NTDS/SYSTEM -ntds
/root/Desktop/NTDS/ntds.dit LOCAL**

 **-system** ：表示系统hive文件的路径（SYSTEM）

 **-ntds** ：表示dit文件的路径（ntds.dit）

可以看到，它已从ntd.dit文件中转储了NTLM密码。

![1.PNG](https://image.3001.net/images/20180707/1530920072285.png!small)

利用在线密码破解工具来尝试破解密码哈希，如图所示，最终的爆破结果是“123@password”。

![2.PNG](https://image.3001.net/images/20180707/15309200884971.png!small)

##  **DSInternals PowerShell**

DSInternals
PowerShell模块提供了构建在框架之上的易于使用的cmdlet。主要功能包括离线ntds.dit文件操作以及通过目录复制服务（DRS）远程协议查询域控制器。

 **参考：**<https://github.com/MichaelGrafnetter/DSInternals>

此方法仅适用于Windows，你可以使用以下命令来提取NTLM哈希值：

    
    
    Save-Module DSInternals -Path C:\Windows\System32\WindowsPowershell\v1.0\Modules
    Install-Module DSInternals
    Import-Module DSInternals

![3.PNG](https://image.3001.net/images/20180707/15309201934765.png!small)

    
    
    Get-Bootkey -SystemHivePath 'C:\Users\sanje\Desktop\NTDS\SYSTEM'

![4.PNG](https://image.3001.net/images/20180707/1530920212681.png!small)

    
    
    Get-ADDBAccount -All -DBPath 'C:\Users\sanje\Desktop\NTDS\ntds.dit' -Bootkey $key

可以看到NTML哈希值成功被提取。同样，我们再次利用在线密码破解工具来尝试破解该密码哈希。

![6.PNG](https://image.3001.net/images/20180707/15309202362976.png!small)

##  **Ntdsxtract**

首先我们需要从NTDS.dit文件中提取表格，这里我们可以通过libesedb-tools中的esedbexport来帮我们完成。Libesedb是一个用于访问可扩展存储引擎（ESE）数据库文件（EDB）格式的库。当前，ESE数据库格式被应用于许多不同的应用程序上，如Windows
Search，Windows Mail，Exchange，Active Directory（NTDS.dit）等。

 **参考：**<https://github.com/libyal/libesedb/>

 **最新下载链接** ：<https://github.com/libyal/libesedb/releases>

键入以下命令来下载libesedb库以安装esedbexport，然后解压tar文件。

    
    
    wget https://github.com/libyal/libesedb/releases/download/20170121/libesedb-experimental-20170121.tar.gz
    tar xf libesedb-experimental-20170121.tar.gz

![7.PNG](https://image.3001.net/images/20180707/15309202587311.png!small)

接着，通过以下命令完成安装：

    
    
    cd libesedb-20170121
    apt-get install autoconf automake autopoint libtool pkg-config
    ./configure
    make
    make install
    ldconfig

![8.PNG](https://image.3001.net/images/20180707/15309202753036.png!small)

安装完成后，我们就可以利用该工具从ntds.dit文件中转储表格了。命令如下：

    
    
    esedbexport -m tables /root/Desktop/NTDS/ntds.dit

这将创建一个名为“ntds.dit.export”的新目录，其中包含提取的表。这里你将会提取到两个主表，即 **datatable** 和
**link_table** 。

![9.PNG](https://image.3001.net/images/20180707/15309202969478.png!small)

现在我们来下载ntdsxtract，这是一个取证工具，能够为我们从NTDS.dit文件中，提取与用户对象，组对象，计算机对象的相关信息以及删除对象。

![10.PNG](https://image.3001.net/images/20180707/1530920321389.png!small)

    
    
    git clone https://github.com/csababarta/ntdsxtract.git

执行以下命令，安装所有配置文件。

    
    
    cd ntdsxtract
    python setup.py build && python setup.py install

![11.PNG](https://image.3001.net/images/20180707/15309203403290.png!small)

## 提取用户信息和密码哈希值

现在借助这三个文件（即Datatable，link_table和system
hive），我们将能够转储用户信息和NT/LM密码哈希值。你也可以通过以下命令以John the ripper的格式来获取NTLM密码。

    
    
    dsusers.py ntds.dit.export/datatable.4 ntds.dit.export/link_table.6 data --syshive /root/Desktop/NTDS/SYSTEM --passwordhashes --pwdformat john --ntoutfile nthash.txt --lmoutfile lmhash.txt

![12.PNG](https://image.3001.net/images/20180707/15309203607490.png!small)

如你所见，用户信息和密码哈希值已成功被提取。

![13.PNG](https://image.3001.net/images/20180707/15309203763820.png!small)

 **cat data/nthash.txt**

现在，我们使用John the ripper来破解这个密码哈希值。如下：

![14.PNG](https://image.3001.net/images/20180707/15309203944330.png!small)

 ***参考来源：[hackingarticles](http://www.hackingarticles.in/3-ways-extract-password-hashes-from-ntds-dit/)，FB小编 secist 编译，转载请注明来自FreeBuf.COM**

