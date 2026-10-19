![](https://image.3001.net/images/20220929/1664454492_63358f5c2e3f94b42b535.png!small)

## 关于PyFlipper

PyFlipper是一款功能强大的Flipper Zero命令行接口封装器，该工具基于纯Python开发，因此具备良好的跨平台特性。

## Flipper Zero介绍

Flipper Zero是一种类似于Tamagotchi的小工具，Flipper
Zero是开源的并可自定义的，您可以插入其他硬件以获取更多帮助。您可以通过蓝牙将其连接到手机或其他设备，也可以插入MicroSD卡以扩展存储并添加自己的插件。Flipper
Zero还具有GPIO和USB端口，可将其连接到其他硬件。

![](https://image.3001.net/images/20220929/1664454508_63358f6c427aa4016cd7b.png!small)

尽管体积小巧，外观简洁，但Flipper
Zero实际上配备了多种用于黑客的工具。您有用于模拟遥控器的无线电，RFID阅读器，红外收发器，甚至是GPIO引脚。所有这些尺寸都适合您的口袋，而且设计不会引起太多关注。

## 功能介绍

> 1、提供Flipper串口命令行接口封装器；
>
> 2、提供Websocket客户端界面；

## 工具下载

该工具基于Python 3开发，因此广大研究人员首先需要在本地设备上安装并配置好Python
3环境。接下来，使用下列命令将该项目源码克隆至本地，并完成工具的虚拟环境配置：

    
    
    $ git clone https://github.com/wh00hw/pyFlipper.git
    
    $ cd pyFlipper
    
    $ python3 -m venv venv
    
    $ source venv/bin/activate

然后使用项目提供的requirements.txt文件安装该工具所需的依赖组件：

    
    
    $ pip install -r requirements.txt

## 测试平台

当前版本的PyFlipper已在下列平台和Python版本环境中进行过测试：

> 1、Python v3.8.10 + Linux 5.1.0 x86_64
>
> 2、Python 3.9.10 + Windows 10
>
> 3、Python 3.10.5 + Android 12 (Termux +
> [_OTGSerial2WebSocket_](https://play.google.com/store/apps/details?id=com.wh00hw.serial2websocket)，无需ROOT)

## 工具使用

### 连接

    
    
    from pyflipper import PyFlipper
    
    #本地串口号
    
    flipper = PyFlipper(com="/dev/ttyACM0")
    
    #或者
    
    #远程serial2websocket服务器
    
    flipper = PyFlipper(ws="ws://192.168.1.5:1337")

### 电源

    
    
    #电源信息
    
    info = flipper.power.info()
    
    #关机
    
    flipper.power.off()
     
    #重启
    
    flipper.power.reboot()
    
    #重启进入DFU模式
    
    flipper.power.reboot2dfu()

### 更新/备份

    
    
    #从.fuf文件安装更新
    
    flipper.update.install(fuf_file="/ext/update.fuf")
    
    #将Flipper备份至.tar文件
    
    flipper.update.backup(dest_tar_file="/ext/backup.tar")
    
    #从.tar备份文件恢复Flipper
    
    flipper.update.restore(bak_tar_file="/ext/backup.tar")

### 加载器

    
    
    #查看已安装程序列表
    
    apps = flipper.loader.list()
    
    #打开App
    
    flipper.loader.open(app_name="Clock")

### Flipper信息

    
    
    #获取Flipper日期
    
    date = flipper.date.date()
    
    #获取Flipper时间戳
    
    timestamp = flipper.date.timestamp()
    
    #获取进程列表
    
    ps = flipper.ps.list()
    
    #获取设备信息
    
    device_info = flipper.device_info.info()
    
    #获取堆信息
    
    heap = flipper.free.info()
    
    #获取free_blocks字符串
    
    free_blocks = flipper.free.blocks()
    
    #获取蓝牙信息
    
    bt_info = flipper.bt.info()

### 存储

 **文件系统信息**

    
    
    #获取文件系统存储信息
    
    ext_info = flipper.storage.info(fs="/ext")

 **资源管理器**

    
    
    #获取存储/ext目录
    
    ext_list = flipper.storage.list(path="/ext")
    
    #获取存储/ext树目录
    
    ext_tree = flipper.storage.tree(path="/ext")
    
    #获取文件信息
    
    file_info = flipper.storage.stat(file="/ext/foo/bar.txt")
    
    #创建目录
    
    flipper.storage.mkdir(new_dir="/ext/foo")

 **文件**

    
    
    #读取文件
    
    plain_text = flipper.storage.read(file="/ext/foo/bar.txt")
    
    #删除文件 
    
    flipper.storage.remove(file="/ext/foo/bar.txt")
    
    #复制文件
    
    flipper.storage.copy(src="/ext/foo/source.txt", dest="/ext/bar/destination.txt")
    
    #重命名文件 
    
    flipper.storage.rename(file="/ext/foo/bar.txt", new_file="/ext/foo/rab.txt")
    
    #MD5哈希文件 
    
    md5_hash = flipper.storage.md5(file="/ext/foo/bar.txt")
    
    #写入文件
    
    file = "/ext/bar.txt"
    
    text = """There are many variations of passages of Lorem Ipsum available,
    
    but the majority have suffered alteration in some form, by injected humour,
    
    or randomised words which don't look even slightly believable.
    
    If you are going to use a passage of Lorem Ipsum,
    
    you need to be sure there isn't anything embarrassing hidden in the middle of text.
    
    """
    
    flipper.storage.write.file(file, text)
    
    #使用监听器写入文件
    
    file = "/ext/foo.txt"
     
    text_one = """There are many variations of passages of Lorem Ipsum available,
    
    but the majority have suffered alteration in some form, by injected humour,
    
    or randomised words which don't look even slightly believable.
    
    If you are going to use a passage of Lorem Ipsum,
    
    you need to be sure there isn't anything embarrassing hidden in the middle of text.
    
    """
    
    flipper.storage.write.start(file)
    
    time.sleep(2)
    
    flipper.storage.write.send(text_one)
    
    text_two = """All the Lorem Ipsum generators on the Internet tend to repeat predefined chunks as
    
    necessary, making this the first true generator on the Internet.
    
     It uses a dictionary of over 200 Latin words, combined with a handful of
    
     model sentence structures, to generate Lorem Ipsum which looks reasonable.
    
    The generated Lorem Ipsum is therefore always free from repetition, injected humour, or non-characteristic words etc.
    
    """
    
    flipper.storage.write.send(text_two)
    
    time.sleep(3)
    
    #停止写入
    
    flipper.storage.write.stop()

### LED/背光

    
    
    #打开通用LED (r,b,g,bl)
    
    flipper.led.set(led='r', value=255)
    
    #关闭LED蓝光
    
    flipper.led.blue(value=0)
    
    #设置LED绿光值
    
    flipper.led.green(value=175)
    
    #打开背光
    
    flipper.led.backlight_on()
    
    #关闭背光
    
    flipper.led.backlight_off()
    
    #关闭LED
    
    flipper.led.off()

### 震动

    
    
    #开启或关闭震动功能
    
    flipper.vibro.set(True)
    
    #打开震动
    
    flipper.vibro.on()
    
    #关闭震动
    
    flipper.vibro.off()

### 音乐播放器

    
    
    #播放RTTTL格式音乐
    
    rttl_song = "Littleroot Town - Pokemon:d=4,o=5,b=100:8c5,8f5,8g5,4a5,8p,8g5,8a5,8g5,8a5,8a#5,8p,4c6,8d6,8a5,8g5,8a5,8c#6,4d6,4e6,4d6,8a5,8g5,8f5,8e5,8f5,8a5,4d6,8d5,8e5,2f5,8c6,8a#5,8a#5,8a5,2f5,8d6,8a5,8a5,8g5,2f5,8p,8f5,8d5,8f5,8e5,4e5,8f5,8g5"
    
    #循环播放
    
    flipper.music_player.play(rtttl_code=rttl_song)
    
    #停止循环播放
    
    flipper.music_player.stop()
    
    #播放20秒
    
    flipper.music_player.play(rtttl_code=rttl_song, duration=20)
    
    #蜂鸣器
    
    flipper.music_player.beep()
    
    #蜂鸣器开启5秒
    
    flipper.music_player.beep(duration=5)

### NFC

    
    
    #检测NFC
    
    nfc_detected = flipper.nfc.detect()
     
    #模拟NFC
    
    flipper.nfc.emulate()

### RFID

    
    
    #读取RFID
    
    rfid = flipper.rfid.read()

## 许可证协议

本项目的开发与发布遵循MIT开源许可证协议。

## 项目地址

 **PyFlipper** ：【[ _GitHub传送门_](https://github.com/wh00hw/pyFlipper)】

## 参考资料

> [ _https://medium.com/@nic_whr/how-to-hack-a-> restaurant-5d394be105a9_](https://medium.com/@nic_whr/how-to-hack-a-> restaurant-5d394be105a9)
>
> [
> _https://play.google.com/store/apps/details?id=com.wh00hw.serial2websocket_](https://play.google.com/store/apps/details?id=com.wh00hw.serial2websocket)

