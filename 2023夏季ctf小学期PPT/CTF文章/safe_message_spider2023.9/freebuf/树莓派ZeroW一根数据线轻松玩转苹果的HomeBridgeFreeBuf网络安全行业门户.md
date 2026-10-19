## 前言

 **最近入手了Zero
W，非常小巧，打算整个homebridge玩，不过找了网上很多文章发现树莓派ZeroW的文章很少，而且都是早期的安装方法了，安装过程中出现各种问题，于是结合其他的文章写了这篇只需要一根数据线一个SD卡就可以轻松完成homebridge安装的文章。（由于本人买不起配件，所以这里我用homebridge控制远程php服务器上的软件的开关做了个案例，原理其实差不多）**

 **废话不多说，我们直接开始干！**

首先下载好raspbian镜像和balenaEtcher工具。

当然，你也可以选择win32diskimager，不过我用过balenaEtcher之后还是觉得balenaEtcher真的是非常简单好用。

 **Raspbian下载链接：<https://www.raspberrypi.org/downloads/raspbian/>**

 **balenaEtcher官方下载链接：<https://www.balena.io/etcher/>**

Raspbian系统，由于后面不需要用到桌面，我这里用的是“Raspbian Stretch Lite”，下好了之后 **不要解压** 。

BalenaEtcher下载很慢，所以我还是选择到百度随便下载了一个。

![下载完就是这俩玩意儿啦](https://image.3001.net/images/20190611/1560245581_5cff754dd8be6.png!small)

 **[↑↑↑] 下载完就是这两个东西哦 **[↑↑↑]**** **** ****  

**一、把SD卡插入读取器并插入电脑，然后打开balenaEtcher（打开的时候比较慢），点击Selectimage，选择刚刚下载的raspbian的镜像，点击Flash，等待刷入并验证完成，显示“FlashComplete！”就是刷入完成了。**

![Clipboard
Image.png](https://image.3001.net/images/20190611/1560246072_5cff7738c3bbc.png!small)

 **二、拔出读卡器再次插入电脑，会出现一个分区boot。**

> 修改boot分区里的config.txt文件，在最后一行下面，另起一行添加：dtoverlay=dwc2
>
> 修改boot分区里的cmdline.txt文件，找到单词rootwait，在其之后添加：modules-load=dwc2,g_ether

注意每个参数之间空格分开，且都是在同一行。

注意：关于dtoverlay的更多内容可以查看boot/overlay文件夹里的README。

> 在boot分区根目录创建一个文本文件，然后重命名为ssh，注意去掉.txt后缀，此时即可以
> 开启ssh登录（新版Raspbian的改动）。SSH默认关闭，因此需要在boot分区创建一个名为ssh的文件来开启SSH服务。

注意：这个ssh文件容易丢失，如果ssh不能登录了，先检查ssh是否丢失。

 **三、插好TF卡，将Micro USB数据线一头接在Zero W USB接口，如果正常此时电脑会安装相关驱动并显示一个新网卡。**

**![20180715112227865.png](https://image.3001.net/images/20190630/15619088887904.png!small)**

等待驱动安装完成之后 打开“设备管理器- >网络适配器”，检查其中是否有类似“USB Ethernet/RNDIS Gadget”的设备，

如果有，则跳过以下步骤，如果没有则需要手动安装RNDIS/Ethernet Gadget 驱动。

由于我这里是WIN10，WIN10
x64的用户可以在[这里下载驱动](http://www.drv5.cn/sfinfo/15631.html)，其他系统的用户请自行百度安装"RNDIS/Ethernet
Gadget驱动"。

![Clipboard
Image.png](https://image.3001.net/images/20190611/1560247998_5cff7ebe93263.png!small)具体如何安装，下载完解压之后里面会有驱动安装方法。

安装成功后，在“设备管理器->网络适配器”中就会出现“RNDIS/Ethernet Gadget”咯！！！

 **四、接下来，使用putty链接树莓派，在Host Name中输入raspberrypi.local然后点击Open：**

![Clipboard
Image.png](https://image.3001.net/images/20190611/1560248426_5cff806abcc14.png!small)

![Clipboard
Image.png](https://image.3001.net/images/20190611/1560248635_5cff813bea80f.png!small)

在弹出的窗口中输入树莓派的默认用户名 **pi，** 然后回车，输入默认密码 **raspberry：**

![Clipboard
Image.png](https://image.3001.net/images/20190611/1560248803_5cff81e35f936.png!small)
出现这样的界面，代表登陆成功。

 **五、配置WIFI链接，让树莓派连上WIFI，扩容SD卡空间。**  

输入：

    
    
    sudo nano /etc/wpa_supplicant/wpa_supplicant.conf    

在最下面插入（注意：下面改成你自己的 WIFI名 和 WIFI密码）

    
    
    network={
              ssid="你的WIFI名"
              psk="WIFI密码"
            }  
    

好了之后，按Ctrl+x，然后输入y，然后回车。

接着使用raspi-config扩容SD卡空间。

输入：

    
    
    sudo raspi-config

选择Advanced Options->Expand Filesystem->Finsh->OK，
然后树莓派会重启，等待一会儿（2分钟左右），然后再次链接树莓派，具体步骤和上面一样：

![Clipboard
Image.png](https://image.3001.net/images/20190611/1560249073_5cff82f10086a.png!small)![Clipboard
Image.png](https://image.3001.net/images/20190611/1560249134_5cff832e9740b.png!small)
**六、修改树莓派默认源，安装并配置HomeBridge。**

输入：

    
    
    sudo nano /etc/apt/sources.list

把里面原本的源注释掉，前面加个#，然后在最底下插入：

    
    
    deb http://mirrors.aliyun.com/raspbian/raspbian/ stretch main non-free contrib
    deb-src http://mirrors.aliyun.com/raspbian/raspbian/ stretch main non-free contrib  
    

好了之后，按Ctrl+x，然后输入y，然后回车：  

![Clipboard
Image.png](https://image.3001.net/images/20190611/1560250734_5cff896e3e23a.png!small)

然后依次输入（具体为啥要执行两次update，我也不清楚，照做就行了）

    
    
    sudo apt-get update
    
    sudo apt-get upgrade
    
    sudo apt-get update
    
    sudo apt-get install npm
    
    sudo apt-get install git-core
    
    sudo apt-get install libnss-mdns
    
    sudo apt-get install libavahi-compat-libdnssd-dev

注意：建议分开一个一个的安装，这样如果出错了方便检查问题。  

然后安装Node，建议不要使用apt-get安装，请到node官方选择ARMv6（很多人出错都是因为选的ARMv7）。

 **Node下载地址：<https://nodejs.org/zh-cn/download/>**  

进去右键复制ARMv6的下载链接，然后到树莓派中运行 wget空格你复制的链接，类似下面这样：

    
    
    wget https://nodejs.org/dist/v10.16.0/node-v10.16.0-linux-armv6l.tar.xz

然后解压，安装HomeBridge，配置HomeBridge：

    
    
    xz -d node-v10.16.0-linux-armv6l.tar.xz
    
    tar -xvf node-v10.16.0-linux-armv6l.tar
    
    cd node-v10.16.0-linux-armv6l  
    
    
    sudo cp -R * /usr/local/  
    
    
    sudo npm install -g --unsafe-perm homebridge

安装一个Homebridge插件（homebridge-http-switch）

    
    
    sudo npm install -g homebridge-http-switch

这个homebridge-http-switch是一个开关的功能，这里为了方便演示。

注意：更多的插件可以在[npm官网](https://www.npmjs.com/)搜索“homebridge-plugin”，里面有很多各种功能的插件以及使用方法，非常详细。

### 配置HomeBridge

    
    
    sudo nano /root/.homebridge/config.json    

然后输入：

    
    
    {
        "bridge": {
            "name": "HomeBridge",
            "username": "B9:36:DA:93:30:20",
            "port": 51826,
            "pin": "031-45-166"
        },
        "description": "Bla Bla Bla",
        "accessories": [{
              "accessory": "HTTP-SWITCH",
              "name": "Switch",
              "switchType": "stateful",
              "onUrl": "http://xxx.com/On.php",
              "offUrl": "http://xxx.com/Off.php",
              "statusUrl": "http://xxx.com/Status.php"
        }],
        "platforms": []
    }  
    

好了之后，按Ctrl+x，然后输入y，然后回车。

注意：这里的onUrl，offUrl，statusUrl需要自己配置，下面我做了一个开关PHP服务器上的软件的例子 （对不起，我太穷了，买不起配件）。

因为之前我试了很多方法，都无法在服务器前台启动软件，只能以www用户运行，最后我发现可以用计划任务实现，首先在你的服务器上创建一个计划任务（注意：以下代码在您的服务器的cmd上以管理员权限运行）：

    
    
    schtasks /create /tn "homerun" /tr "c:\windows\system\calc.exe" /sc daily /st 00:01    

**On.php**

    
    
    <?php
    exec('schtasks /run /TN "homerun"');
    echo '{"statusPattern":"true"}';
    ?>

 **Off.php**

    
    
    <?php
    exec('taskkill /f /im "calc.exe"');
    echo '{"statusPattern":"true"}'
    ?>

 **Status.php**  

    
    
    <?php
    $res=exec('tasklist | find /i "calc.exe"');
    $res=(string)stripos($res,"calc.exe");
    if($res!==""){
      $res="1";
    }else{
      $res="0";
    }
    echo $res;
    ?>  
    

注释（bridge）：这里的username可以设置成你的树莓派的mac地址（我试了下改成别的也没事），port不需要改，pin就是之后链接的时候用的pin码也可以不用修改  

注释（accessories）：这里的onUrl是点击打开时树莓派就会访问这个链接，offUrl就是点击关闭的时候会访问这个链接，statusUrl就是状态链接（statusUrl
返回0就是关闭 返回1就是打开）具体可以参照这里：<https://www.npmjs.com/package/homebridge-http-switch>

 **七、连接HomeBridge，设置HomeBridge开机自启。**

输入：

    
    
    sudo homebridge

![Clipboard
Image.png](https://image.3001.net/images/20190611/1560253871_5cff95af15835.png!small)然后打开手机上的“家庭”（如果被你之前删掉了，就去Appstore里装回来），点击右上角的+号
->添加配件->扫码连接：

![Clipboard
Image.png](https://image.3001.net/images/20190611/1560254121_5cff96a95c032.png!small)

![Clipboard
Image.png](https://image.3001.net/images/20190611/1560254269_5cff973d29da1.png!small)

 **八、配置HomeBridge开机自动启动。**

输入：

    
    
    sudo nano /etc/rc.local

在 exit 0 前添加一行代码：

    
    
    sudo nohup homebridge > /home/pi/homebridge.log 2>&1 &

好了之后，按Ctrl+x，然后输入y，然后回车。

之后每次关闭树莓派重新打开都会自动启动Homebridge咯！！！

注意：树莓派和手机必须在同一个WIFI下，否则在“家庭”中 会无法找到设备。

 **基本的Homebridge安装就是这样，下一篇 我打算把他打造成一个智能可变色的Homekit台灯。**
**本人学美术出身，纯属个人兴趣，如果有写得不对的地方，希望大佬指出，我会及时改正。**

下面整理一些你们可能需要用到的链接：

> Raspbian下载链接：<https://www.raspberrypi.org/downloads/raspbian/>
>
> balenaEtcher官方下载链接：<https://www.balena.io/etcher/>
>
> Node下载地址：<https://nodejs.org/zh-cn/download/>  
>
>
> NPM官方的 homebridge插件列表：<https://www.npmjs.com/search?q=homebridge-plugin>  
>
>
>
> HomeBridge的README：<https://github.com/nfarina/homebridge/blob/master/README.md>
>
> 参考链接：<https://blog.csdn.net/SongtaIot/article/details/81389120>
>
> 参考链接：<https://blog.csdn.net/chentuo2000/article/details/81051308>

 ***本文作者：mrzcpo，转载请注明来自FreeBuf.COM**

