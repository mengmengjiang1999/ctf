斗哥这期将给大家带来Android逆向的动态分析，主要简述了Android动态分析环境配置与IDA调试so文件。学习Android逆向动态分析前，一定要有基础环境支持，比如sdk、jdk等，所以在动态分析前先要进行一波基础配置。

## 0X01 基础环境配置

#### 1、配置adb命令：

adb是android
sdk里的一个工具，用这个工具可以直接操作管理android模拟器或者真实的andriod设备。主要功能有:1、运行设备的shell2、管理模拟器或设备的端口映射3、主机和设备之间上传/下载文件4、将本地apk软件安装至模拟器或android设备[下载SDK
Platform-Tools](https://pan.baidu.com/s/1sj4ZfTb?utm_source=androiddevtools&utm_medium=website)（如果你的主机已经有sdk就不需要下载，直接添加）将文件解压后将adb.exe所在的Platform-Tools目录绝对路径添加到path环境变量启动终端就能使用adb命令，输入adb就能查看版本与参数介绍![2](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-2018092000241855.png)

#### 2、配置设备：

准备一个android设备或者模拟器，用来调试apk，下面介绍是夜神模拟器的配置。打开开发者模式(默认不开)，设置->关于手机![6](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-20180823214712340.png)点击版本号五下，手机将进入开发者模式，手机设置多出开发者选项一栏![7](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-20180823214840528.png)进入开发者选项，打开USB调试![8](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-20180823214941297.png)真实的android设备到这步就能结束，模拟器的话还要打开IP端口先启动夜神模拟器，然后运行cmd命令，cd到夜神安装目录，执行命令：nox_adb.exe
connect 127.0.0.1:62001 打开端口![9](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-20180815112453698.png)adb connect 127.0.0.1:62001
主机就能连接到模拟器![9](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-20180824161151447.png)查看连接的设备![9](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-20180824161851542.png)adb shell
进入连接上的设备![10](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-20180824114719830.png)接下来就可以愉快的调试程序了![3](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-20180815114027163.png)

##0X02 动态分析这里的动态分析主要使用IDA和adb命令配合Android模拟器来分析so

####1.动态环境配置将IDA安装目录E:\IDA 7.0\dbgsrv下符合Android安装系统位数的android_server
push到Android目录下(本系统是X86)![7](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-20180827140916452.png)修改文件权限为777或者755，运行服务chmod 777 android_x86_server
修改文件权![9](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-20180827141204962.png)服务器(pc)转发端口adb forward tcp:23946
tcp:23946![10](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-20180827142346903.png)

启动IDA，进行程序调试启动IDA的32bit程序，点击：Debugger-Run-RemoteArmLinux/Android
debugger，打开调试程序的设置对话框：Application：对应调试程序所在的路径Directory：对应调试程序所在的目录路径HostName：输入localhost，Port：PC端口

#### 2.加载程序调试

![11](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-20180827234925897.png)加载成功![12](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-20180828092609776.png)加载不成功情况：1.配置主机和路径错误2.主机无法连接3.程序与IDA位数不对(如x86)![12](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-20180828092930431.png)

#### 3.IDA远程调试

在分析加壳程序的壳时，应以调试方式来启动调试程序(adb shell am start-D -n
packagename/activityname)ida--->Debugger--->Attacth---->Remote GDB
Debugger![13](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-20180827233811174.png)查看到Android的进程![14](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-20180827233836252.png)双击要调试的进程，IDA将加载到so,IDA进行动态分析![15](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-20180920101954804.png)双击可以为相应的代码打上断点，F9重新开始调试，程序将停在断点处就能开始调试so文件![16](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-20180920102728834.png)IDA动态调试的小技巧①调试快捷键：F2设置断点，F4运行到鼠标位置，F7单步步入，F8单步步过，F9运行程序F5/Tab
将相应的简单汇编代表粗略转换为C/C++代码

## 0X03 小小总结

斗哥这期`Android逆向之动态分析so篇`主要讲述了Android逆向的环境配置以及利用`IDA`配合模拟器动态分析so文件。有疑问的小伙伴们欢迎留言探讨。

![qrcode_for_gh_223e082fe8a7_344.jpg](https://image.3001.net/images/20181022/1540196865_5bcd8a010f8a9.jpg!small)

