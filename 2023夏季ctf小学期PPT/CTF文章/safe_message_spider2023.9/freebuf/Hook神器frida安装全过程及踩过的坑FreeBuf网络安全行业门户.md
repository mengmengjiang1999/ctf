# Hook神器: frida安装全过程及踩过的坑

## 1.概述：

    
    
    Frida 是一款基于 Python + JavaScript 的 Hook 与调试框架。
    
    Frida的核心是用C编写的，并将Google的V8引擎注入到目标进程中，在这些进程中，JS可以完全访问内存，挂钩函数甚至调用进程内的本机函数来执行。
    
    使用Python和JS可以使用无风险的API进行快速开发。Frida可以帮助您轻松捕获JS中的错误并为您提供异常而不是崩溃。
    

`#准备环境： windows安装frida环境 手机中安装frida服务端`

## 2.windows安装frida环境:

    
    
    需要python环境，建议使用3.7版本，自行安装
    安装frida和frida-tools
    

命令为：

    
    
    pip install frida-tools
    

## 3.手机中安装frida服务端

安卓Frida 15.1.1下载地址：

    
    
    https://github.com/frida/frida/releases
    

注意：这里一定要下载与手机版本相对应的Frida。  
![image](https://image.3001.net/images/20210909/1631181405_6139da5dc70beba7f9aea.png!small)  
（1）使用adb push命令将下载好的Frida移动到手机下/data/local/tmp目录：

    
    
    adb push C:\Users\Administrator\Desktop\frida-server-15.1.1-android-arm64 /data/local/tmp
    

![image](https://image.3001.net/images/20210909/1631181436_6139da7c03ce7e15ab854.png!small)  
（2）frida-server-15.1.1-android-arm64加权限

    
    
    chmod 777 frida-server-15.1.1-android-arm64
    

![image](https://image.3001.net/images/20210909/1631181458_6139da92542ed55858d6b.png!small)  
（3）进行执行

    
    
    ./frida-server-15.1.1-android-arm64
    

`踩过的坑：刚开始每次执行frida时手机都会关机，最后刷机到7.0.0版本才可成功执行！！`

（4）打开cmd，查看frida是否安装成功，命令为

    
    
    frida-ps -U
    

![image](https://image.3001.net/images/20210909/1631181496_6139dab8443463d48c22b.jpg!small)

* * *

`最后附上安卓6怎么刷机为7.0.1`

## 安卓刷机：

1.下载镜像

    
    
    https://developers.google.cn/android/images#bullhead（这里下载7.0.1版本）拖到本地。
    

![image](https://image.3001.net/images/20210909/1631181524_6139dad46f4d979365f44.png!small)  
2.连接电脑的状态下将手机关机，然后按住电源键和音量下键重启，进入bootloader模式，本机在镜像目录下点击dlash-all.bat，一键刷机。  
![image](https://image.3001.net/images/20210909/1631181541_6139dae59ecf76bbd4b3f.jpg!small)  
`问题：.bat文件运行之后 一直在google界面不动，如果刷机不成功可将fastboot.zip这个解压到官方包里面进行批处理线刷`  
![image](https://image.3001.net/images/20210909/1631181566_6139dafe86776ce1e6d18.jpg!small)  
![image](https://image.3001.net/images/20210909/1631181588_6139db14005094073e50e.png!small)  
3.最后在运行.bat就会成功刷机！！！  
![image](https://image.3001.net/images/20210909/1631181603_6139db23d312d4ce6f004.png!small)

