# Camille介绍

基于Frida的Android
App隐私合规检测辅助工具，现如今APP隐私合规十分重要，各监管部门不断开展APP专项治理工作及核查通报，不合规的APP通知整改或直接下架。camille可以hook住Android敏感接口，检测是否第三方SDK调用。根据隐私合规的场景，辅助检查是否符合隐私合规标准。

# 环境搭建

  * python3

  * frida

  * 已root的手机

## frida环境搭建

手机需要root，打开开发者模式，需要开启Android调试

![图片.png](https://image.3001.net/images/20221212/1670836507_6396f11b61597cdf85313.png!small)

连接上电脑查看`adb devices`  
![图片.png](https://image.3001.net/images/20221212/1670836613_6396f185f3d4cfad648e6.png!small)

输入 adb shell ，查看CPU`getprop | grep abi`

![图片.png](https://image.3001.net/images/20221212/1670836770_6396f222ad825aafd4539.png!small)

以Windows为例，需要在windows安装frida。

    
    
    pip install frida
    pip install frida-tools
    

安装好后查看版本，`frida --version`  
![图片.png](https://image.3001.net/images/20221212/1670836901_6396f2a5caf8eb6e6799f.png!small)

然后根据上面的版本和CPU型号去官网下载frida-server：https://github.com/frida/frida/releases

![图片.png](https://image.3001.net/images/20221212/1670837129_6396f38911ba06547fd36.png!small)

解压放然后推到手机里

    
    
    adb push frida-server-12.11.17-android-x86 /data/local/frida-12
    

进入shell， 到 /data/local目录下，使用`chmod`命令修改权限为可执行

    
    
    chmod 777 frida-server-12.11.17-android-x86
    

执行`setenforce 0`

关闭`SELinux`,然后执行该二进制文件。  
![图片.png](https://image.3001.net/images/20221212/1670837382_6396f486cf854f5dba969.png!small)

到本机上运行`frida-ps -U`，看是否成功  
![图片.png](https://image.3001.net/images/20221212/1670837451_6396f4cb8b868d32eabac.png!small)

## 安装camille

    
    
    git clone https://github.com/zhengjim/camille.git
    cd camille
    pip install -r requirements.txt
    python camille.py -h
    

![图片.png](https://image.3001.net/images/20221212/1670837820_6396f63c1a7a7fa182850.png!small)

# 使用

使用文档：  
https://github.com/zhengjim/camille/blob/master/docs/use.md  
![图片.png](https://image.3001.net/images/20221212/1670838096_6396f75065ab34bbbd110.png!small)

## 基本使用

    
    
    python camille.py tv.danmaku.bili -t 2 -f demo.xlsx
    

![图片.png](https://image.3001.net/images/20221212/1670839038_6396fafe6d23382b196fa.png!small)

  * -t 延迟hook，有些包直接hook会失败，需要增加延迟。

  * -f 保存堆栈信息到xlsx里

同时桌面会弹出屏幕页面，来同意隐私政策，用于区分权限是同意前获取的还是同意后获取。根据提示点击即可。  
如果不需要的话可以使用 `-npp`关闭。

可以看到获取敏感信息的主体是来自什么SDK。好评！  
![图片.png](https://image.3001.net/images/20221212/1670839258_6396fbda206edf15e7a77.png!small)

还可以通过`-u`、`-nu`来选择用什么模块和不用什么模块。  
 **模块列表：**

模块名| 备注  
---|---  
permission| 申请权限  
phone| 电话、基站  
system| 系统信息(AndroidId/标识/content敏感信息)  
app| 其他app信息  
location| 位置信息  
network| getNetwork  
camera| 照相机  
bluetooth| 蓝牙  
file| 文件  
media| 麦克风  
custom| 用户自定义接口  
  
如果需要自定义接口，可以直接写在custom里。  
![图片.png](https://image.3001.net/images/20221212/1670839459_6396fca3a19cec9660207.png!small)

查看报告。  
![图片.png](https://image.3001.net/images/20221212/1670839528_6396fce825fb0b83cac04.png!small)

# 参考链接

  * https://github.com/zhengjim/camille

  * https://www.bilibili.com/read/cv17626303

  * https://blog.csdn.net/qq_38312411/article/details/126521411

  * https://blog.csdn.net/YSR1282855229/article/details/126927194

