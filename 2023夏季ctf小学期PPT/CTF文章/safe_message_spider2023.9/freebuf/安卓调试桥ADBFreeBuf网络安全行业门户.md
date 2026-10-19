## ADB简介

adb的全称为Android Debug Bridge,起到调试桥的作用，是连接Android手机与PC端的桥梁，方便我们在电脑上对手机进行操作。

adb采用socket TCP
5554等端口的方式让IDE和Qemu通讯，借助adb工具我们可以管理设备或手机模拟器的状态，还可以进行很多手机的操作如安装软件、系统升级、运行shell命令等。

adb的使用需要安装Android sdk环境，并把“platform-tools”目录添加到系统环境变量中直接打开cmd即可使用adb命令。

## ADB主要的功能

ADB常用功能如下：

  * 查看当前迷你裙或者Android设备实例的状态
  * 给特定的模拟器或设备实例发送命令
  * 安装和协助apk应用程序
  * 从本机省复制文件到模拟器或者Android设备
  * 查看logcat日志
  * 使用shell命令

# 几款常用模拟器的自带ADB环境

我们上面说到adb的使用需要安装android sdk环境，然而现在常用的模拟器都自带了打包的ADB调试环境程序，下面以两款模拟器为例演示。

逍遥模拟器：

逍遥模拟器自带的adb在软件安装根目录MEmu下,在根目录下直接通过cmd可运行。

![1652949057_628600412d8e522b16aaf.png!small](https://image.3001.net/images/20220519/1652949057_628600412d8e522b16aaf.png!small)

![1652949063_628600476ed182e748af1.png!small](https://image.3001.net/images/20220519/1652949063_628600476ed182e748af1.png!small)

MuMu模拟器：

MuMu模拟器系统自带adb在软件安装路径\MuMu\emulator\nemu\vmonitor\bin\下，通过cmd执行adb_server运行

![1652949069_6286004dd5a67b263d5b6.png!small](https://image.3001.net/images/20220519/1652949069_6286004dd5a67b263d5b6.png!small)

![1652949074_62860052a925e101b99a1.png!small](https://image.3001.net/images/20220519/1652949074_62860052a925e101b99a1.png!small)

## ADB常用命令

### 01基本命令

    
    
    ## 1.查看adb版本信息 
    adb version

![1652949079_62860057f204e1642b9b2.png!small](https://image.3001.net/images/20220519/1652949079_62860057f204e1642b9b2.png!small)

    
    
    ## 2.开启adb服务 
    adb start-server adb -P <port> start-server #指定服务运行端口 
    
    ## 3.关闭adb服务 
    adb kill-server

![1652949084_6286005cf0ce6741cec43.png!small](https://image.3001.net/images/20220519/1652949084_6286005cf0ce6741cec43.png!small)

    
    
    ## 4.以root权限运行
    adb adb root

![1652949089_62860061ca8235f7eb796.png!small](https://image.3001.net/images/20220519/1652949089_62860061ca8235f7eb796.png!small)

    
    
    ## 5.查询已连接设备 
    adb devices

![1652949094_628600660a8f50bb78347.png!small](https://image.3001.net/images/20220519/1652949094_628600660a8f50bb78347.png!small)

### 02应用管理

    
    
    ## 1.查看应用列表 
    adb shell pm list packages [-f] [-d] [-e][-s][-3][-i] [-u] [--user USER_ID][FILTER] 
    参数		显示列表 
    无	 	 所有应用 
    -f		显示应用关联的apk 文件 
    -d		只显示 disabled的应用 
    -e		只显示enabled的应用 
    -s		只显示系统应用 
    -3		只显示第三方应用 
    -i		显示应用的installer 
    -u		包含已卸载应用包名包含 
    ## 列举 
    adb shell pm list packages #查看所有应用 
    adb shell pm list packages -s #查看系统应用 
    adb shell pm list packages -3 #查看第三方应用 
    adb shell pm list packages xiaomi #查看包名包含'xiaomi'字符的应用

![1652949099_6286006b4754bf57e16b0.png!small](https://image.3001.net/images/20220519/1652949099_6286006b4754bf57e16b0.png!small)

    
    
    ## 2.安装应用 
    adb install [-1] [-r] [-t] [-s] [-d] [-g] <apk-file> 
    参数		含义 
    -I		将应用安装到保护目录/mnt/asec
    -r		允许覆盖安装
    -t		允许安装AndroidManifest.xml 里application指定android:testOnly="true"的应用
    -s		将应用安装到sdcard
    -d		允许降级覆盖安装
    -g		授予所有运行时权限 
    ## 列举 
    adb install apk路径
    ## 3.应用卸载 
    adb uninstall [-k] <package-name> 
    参数		含义 
    -k		卸载应用保留数据和缓存

![1652949104_628600704696ae1dd3f1c.png!small](https://image.3001.net/images/20220519/1652949104_628600704696ae1dd3f1c.png!small)

    
    
    ## 4.清除应用数据与缓存 
    adb shell pm clear <packega-name>

![1652949109_628600753c5cf17da7ae6.png!small](https://image.3001.net/images/20220519/1652949109_628600753c5cf17da7ae6.png!small)

    
    
    ## 5.查看应用详细信息 
    adb dumpsys package <package-name>

![1652949114_6286007a6d7d8956666b0.png!small](https://image.3001.net/images/20220519/1652949114_6286007a6d7d8956666b0.png!small)

    
    
    ## 6.查看软件安装路径 
    adb shell pm path <package-name>

![1652949119_6286007f7760bc1b1d9b9.png!small](https://image.3001.net/images/20220519/1652949119_6286007f7760bc1b1d9b9.png!small)

### 03文件管理

    
    
    ## 1.从设备传输文件到电脑 
    adb pull file file2    #file文件路径、file2传输到计算机中的位置 
    ## 2.从电脑传文件到设备 
    adb push file file2 #file计算机中的文件、file2传输到设备路径

将设备中/sdcard/Download/burp.cer复制到电脑桌面

![1652949369_628601793db45d6349315.png!small](https://image.3001.net/images/20220519/1652949369_628601793db45d6349315.png!small)

![1652949377_62860181e5567f8a7bcfb.png!small](https://image.3001.net/images/20220519/1652949377_62860181e5567f8a7bcfb.png!small)

将电脑桌面test.txt复制到设备中。

![1652949384_62860188c19b474402ea6.png!small](https://image.3001.net/images/20220519/1652949384_62860188c19b474402ea6.png!small)

![1652949390_6286018e6304321d16363.png!small](https://image.3001.net/images/20220519/1652949390_6286018e6304321d16363.png!small)

    
    
    ## 3.列出文件目录 
    adb shell ls [-a][-i][-s][-n][-R] 
    参数		显示列表
    无		列出目录下的所有文件和目录
    -a		歹出目录下的所有文件(包括隐藏的)
    -i		列出目录下的所有文件和索引编号 
    -s		列出目录下的所有文件和文件大小	
    -n		列出目录下的所有文件及其UID和GID 
    -R		列出目录下的所有子目录中的文件

![1652949397_628601959e0707d77f8d3.png!small](https://image.3001.net/images/20220519/1652949397_628601959e0707d77f8d3.png!small)

    
    
    ## 4.切换目录 
    adb shell 
      cd <dir> 
    ## 5.删除目录或文件 
    adb shell rm [-f][-r][-d][-i] <dir or file> 
    参数	含义 
    无		删除文件 
    -f		强制删除文件，系统不提示 
    -r		强制删除指定目录中的所有文件和子目录 
    -d		删除指定目录，即使它是一个非空目录 
    -i		交互式删除，删除前提示 
    ## cd rm命令分两步执行，先adb shell再执行
    下图演示切换目录后删除test.txt文件

![1652949267_62860113e9bd1b33bf005.png!small](https://image.3001.net/images/20220519/1652949267_62860113e9bd1b33bf005.png!small)

    
    
    ## 6.创建目录 
    adb shell mkdir [-m][-p] 
    参数 含义 
    无 创建指定目录 
    -m 创建指定目录并赋予读写权限 
    -p 创建指定目录及其父目录 
    ## 7.创建文件 
    adb shell touch 
    ## 8.查看当前路径 
    adb shell pwd 
    ## 9.复制文件或目录 
    adb shell cp <source> <dest> ##source 原路径，dest目的路径 
    ## 10.移动或重命名文件 
    adb shell mv <source> <dest>

### 04设备操作命令

    
    
    ## 1.查看手机CPU状态 
    adb shell dumpsys cpuinfo

![1652949262_6286010e2016b412fe659.png!small](https://image.3001.net/images/20220519/1652949262_6286010e2016b412fe659.png!small)

    
    
    ## 2.查看内存使用情况 
    adb shell dumpsys meminfo <packeag-name>

![1652949241_628600f95726402776323.png!small](https://image.3001.net/images/20220519/1652949241_628600f95726402776323.png!small)

    
    
    ## 3.显示磁盘使用信息： 
    adb shell dumpsys diskstats

![1652949235_628600f309e86a1303329.png!small](https://image.3001.net/images/20220519/1652949235_628600f309e86a1303329.png!small)

    
    
    ## 4.查看电池状态 
    adb shell dumpsys battery adb shell dumpsys batteryproperties

![1652949229_628600ed81c4f7454e441.png!small](https://image.3001.net/images/20220519/1652949229_628600ed81c4f7454e441.png!small)

![1652949223_628600e792b126ed6775b.png!small](https://image.3001.net/images/20220519/1652949223_628600e792b126ed6775b.png!small)

