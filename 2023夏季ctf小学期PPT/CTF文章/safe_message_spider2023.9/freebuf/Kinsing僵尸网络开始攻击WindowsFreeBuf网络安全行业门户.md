Akamai 在 2021 年 2 月 16 日发现一个大型的加密挖矿僵尸网络正在大规模感染整个互联网，该僵尸网络同时针对 Windows 和 Linux
系统。在美洲、欧洲和亚洲在内的各个区域都高度活跃，而且使用相同的地址（194.38.20.199）进行分发，已经使用了超过半年。

## 感染 Windows

僵尸网络利用 CVE-2020-14883（WebLogic RCE 漏洞）感染 Windows 机器。攻击者让失陷主机下载并执行名为 `wbw.xml`的
XML 文件，在 Windows 上通常通过
`ClassPathXmlApplicationContext`执行。![1632191707_614944db73069fe39631c.png!small?1632191706464](https://image.3001.net/images/20210921/1632191707_614944db73069fe39631c.png!small?1632191706464)

`wbw.xml`嵌入了 PowerShell
命令：![1632191741_614944fd715d6a6efcf78.png!small?1632191740387](https://image.3001.net/images/20210921/1632191741_614944fd715d6a6efcf78.png!small?1632191740387)

使用 `System.Net.WebClient.DownloadString`下载名为 `1.ps1`的 PowerShell 脚本，利用 `Set-ExecutionPolicy
Bypass`确保执行不会产生告警。![1632191874_61494582a370d12024df0.png!small?1632191873749](https://image.3001.net/images/20210921/1632191874_61494582a370d12024df0.png!small?1632191873749)

`1.ps1`脚本下载配置文件和矿工，矿工将会被重命名为
`sysupdate`并执行。![1632192031_6149461f4daa580e99694.png!small?1632192030226](https://image.3001.net/images/20210921/1632192031_6149461f4daa580e99694.png!small?1632192030226)

配置文件如下所示：![1632192050_614946325e637c24efa60.png!small?1632192049379](https://image.3001.net/images/20210921/1632192050_614946325e637c24efa60.png!small?1632192049379)

通过名为 `Update service for Windows Service`的计划任务实现持久化，也利用 `-ExecutionPolicy
bypass`和 `-windowstyle
hidden`实现隐藏。![1632192065_61494641574f55cb7426c.png!small?1632192064284](https://image.3001.net/images/20210921/1632192065_61494641574f55cb7426c.png!small?1632192064284)

## 感染 Linux

僵尸网络利用多个 CVE 来感染 Linux 系统，针对的服务包括 Oracle WebLogic Server、Redis、Apache
Solr、PHPUnit 和 Supervisor XML-RPC 等。

与 Windows 版本不同，Linux 中的 CVE-2020-14883 利用
`FileSystemXmlApplicationContext`来执行。恶意文件名为 `wb.xml`，进一步下载 bash
脚本。![1632192078_6149464e54e963e7650cf.png!small?1632192077388](https://image.3001.net/images/20210921/1632192078_6149464e54e963e7650cf.png!small?1632192077388)

![1632192092_6149465cc3b7bcd57e637.png!small?1632192092355](https://image.3001.net/images/20210921/1632192092_6149465cc3b7bcd57e637.png!small?1632192092355)

针对 Linux 系统，使用的 CVE 漏洞和 Payload
如下所示：![1632192121_61494679388024d362ef9.png!small?1632192121251](https://image.3001.net/images/20210921/1632192121_61494679388024d362ef9.png!small?1632192121251)

![1632192137_614946899778f638a948f.png!small?1632192136672](https://image.3001.net/images/20210921/1632192137_614946899778f638a948f.png!small?1632192136672)

![1632192152_6149469873e67cb4d0ca6.png!small?1632192152649](https://image.3001.net/images/20210921/1632192152_6149469873e67cb4d0ca6.png!small?1632192152649)

尽管文件名称不同，但所有的脚本几乎都差不多。它们都会杀死所有已经在系统中的矿工、禁用安全和日志记录。

最后下载 Golang 编写的 Kinsing
恶意软件，通过定时任务进行持久化。![1632192169_614946a91180d0c66e8e3.png!small?1632192168006](https://image.3001.net/images/20210921/1632192169_614946a91180d0c66e8e3.png!small?1632192168006)

一旦成功执行，会在 `/tmp`目录下创建名为 `kdevtmpfsi`的矿工文件并执行，且会持续监控该进程正在运行。

## 命令与控制

恶意软件使用 `getActiveC2CUrl`函数解码 C&C 地址，该函数使用 RC4 加密与异或加密。

静态字符串形成一个很大的字符块，明文密钥和十六进制数据很容易隐藏在大量字符串中。逆向该函数后可以发现密钥和十六进制数据的所在位置和长度。![1632192188_614946bc7b050139434bd.png!small?1632192188723](https://image.3001.net/images/20210921/1632192188_614946bc7b050139434bd.png!small?1632192188723)

![1632192202_614946cae771983a0b439.png!small?1632192203281](https://image.3001.net/images/20210921/1632192202_614946cae771983a0b439.png!small?1632192203281)

得到 C&C 的十六进制数据和密钥，可以逆向并在 Golang 中重写 `getActiveC2CUrl`函数计算 C&C
地址。![1632192218_614946da147144e647da4.png!small?1632192217870](https://image.3001.net/images/20210921/1632192218_614946da147144e647da4.png!small?1632192217870)

![1632192228_614946e485dd39ea6a4ae.png!small?1632192227657](https://image.3001.net/images/20210921/1632192228_614946e485dd39ea6a4ae.png!small?1632192227657)

## RAT

Kinsing 具有远控木马的功能，在名为 `doTask()`的函数中。该函数包含几个有趣的函数：

> runTaskWithScan()
>
> updateTask()
>
> startCmd()
>
> execTaskOut()
>
> masscan()
>
> socks()
>
> backconnect()
>
> runTaskWithHttp()
>
> downloadAndExecute()

其中一个有趣的函数是
`startCmd()`，可以在实现主机上执行任意命令。![1632192245_614946f59395c608723d9.png!small?1632192248075](https://image.3001.net/images/20210921/1632192245_614946f59395c608723d9.png!small?1632192248075)

## C&C 通信

恶意软件通过 HTTP 与 C&C 服务器通信，失陷主机随着每个 HTTP 请求发送系统状态和系统资源信息，例如内核数量、内存信息、操作系统信息、是否获得
root 权限等。所有这些参数都使用自定义 HTTP 头发送给 C&C
服务器。![1632192269_6149470d14acb5cfac3dd.png!small?1632192268419](https://image.3001.net/images/20210921/1632192269_6149470d14acb5cfac3dd.png!small?1632192268419)

失陷主机不断请求 `/get`，传递恶意 Shell
脚本。![1632192286_6149471e415ae5fc1b961.png!small?1632192285874](https://image.3001.net/images/20210921/1632192286_6149471e415ae5fc1b961.png!small?1632192285874)

`ph.sh`会从 `194.38.20.199/libsystem.so`处下载名为 `libsystem.so`的 Rootkit
以及其他恶意软件。然后 `ph.sh`将此 Rootkit 预加载到
`/etc/ld.so.preload`。![1632192297_6149472974fe017ac90dd.png!small?1632192296627](https://image.3001.net/images/20210921/1632192297_6149472974fe017ac90dd.png!small?1632192296627)

该脚本还注册一个定期重新感染主机的系统服务来持久化。![1632192308_6149473453677b1a0f4b9.png!small?1632192307474](https://image.3001.net/images/20210921/1632192308_6149473453677b1a0f4b9.png!small?1632192307474)

另一个脚本 `spre.sh`会检查 `~/.ssh/config`、`~/.bash_history`和
`.ssh/known_hosts`尝试进行横向平移。![1632192330_6149474a8d2c8a54e5cba.png!small?1632192332382](https://image.3001.net/images/20210921/1632192330_6149474a8d2c8a54e5cba.png!small?1632192332382)

失陷主机会请求 `/mg`，C&C 服务器将会响应几个字符，随后与其他主机进行通信，该主机似乎负责以 JSON-RPC 的形式通过 HTTP
发送失陷主机信息。![1632192346_6149475a09d4ae79566cc.png!small?1632192349001](https://image.3001.net/images/20210921/1632192346_6149475a09d4ae79566cc.png!small?1632192349001)

## IOC

> 185.154.53.140  
> 194.38.20.199  
> 95.181.179.88  
> 195.3.146.118  
> 8ca0229fb64e3f1819375cf1daf32104c37c0d0923bdc35cb6bea655ecd1a6a4  
> ede8fdb68d777efcc0538b465d640cbb2c061bd49461f76d65f68c135ff8bbb6  
> 0e79ec7b00c14a4c576803a1fd2e8dd3ea077e4e98dafa77d26c0f9d6f27f0c9  
> 6e35b5670953b6ab15e3eb062b8a594d58936dd93ca382bbb3ebdbf076a1f83b  
> 818179ac928027a5c26c9b13d3d830b7331c3e4c46ba1e305867e3d4accaf3ef  
> 56ac2321e481708ea72e2bf7710e66c3455afa729b24f6a6ba9065ae0cca8fb3  
> 05e5ad89443b5-8805ae2eb2628d3eef1d6cbcc338bced23f422abe5ce60ff82d  
> 274b11542fcb30065c4cc0976ce33252ba2812756f7e22f6d80fae1acadf5c4c  
> 6e25ad03103a1a972b78c642bac09060fa79c460011dc5748cbb433cc459938b  
> 7d31843ce5231c95ce07a609cb4473fe53b95a8d0685df9d666de348d17c69ff  
> c38c21120d8c17688f9aeb2af5bdafb6b75e1d2673b025b720e50232f888808a  
> 5e5b5171a95955ecb0fa8f9f1ba66f313165044cc1978a447673c0ac17859170  
> 49ff0329b9ad42c7fb17e6a2d80b316ed6b759ab5dfd04a5aba42b97225494cf  
> 25b545dc3423d5c3c0181f559486643a7097b5fd87b32f0347ed667cbf3fb38e  
> 6b9e23cb675be370a18a0c4482dc566be28920d4f1cd8ba6b4527f80acf978d3  
> fecd30cd7802f8ac4137a2d0659b3052411a99d809a5aefb48f8b821905100f3  
> cb2ca16246a687b34fa1ba76015cb4aa3b5-0b4ecca4550478eb5-80c4725ab48f  
> d7cda9e427d0848352a1158c68a2577c1600965fb9dbb32bc1e10af1a442d284  
> f4c319e43296ab323615ac4bd4b7601991218ecb6d6043b1c040a96f1a33f14f  
> dd603db3e2c0800d5eaa262b6b8553c68deaa486b545d4965df5dc43217cc839

## 参考来源

> [Akamai](https://www.akamai.com/blog/security/Kinsing-evolves-adds-windows-> to-attack-list)

